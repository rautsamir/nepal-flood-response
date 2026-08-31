"""
UNFRC — Unified Nepal Flood Response Center
A bilingual (English / Nepali) chat-over-data app for flood response units.

Pattern: FMAPI text-to-SQL. A user asks a question in English or Nepali; the LLM
(Databricks Foundation Model API) turns it into a single safe SELECT against the
governed nepal_flood_response tables, we execute it on a SQL warehouse, then the
LLM writes a short natural-language answer in the user's language. Map-able rows
(with lat/lon) are returned so the front end can plot them.

All data stays in the customer's Databricks account. Prototype on open humanitarian
data; not an official assessment.
"""
import json
import os
import re
import time
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.serving import ChatMessage, ChatMessageRole

from backend.sql_cache import SqlCache

SERVING_ENDPOINT = os.environ.get("DATABRICKS_SERVING_ENDPOINT", "databricks-claude-sonnet-4-6")
WAREHOUSE_ID = os.environ.get("SQL_WAREHOUSE_ID", "")
CATALOG = os.environ.get("UNFRC_CATALOG", "main")
SCHEMA = os.environ.get("UNFRC_SCHEMA", "nepal_flood_response")
FQ = f"{CATALOG}.{SCHEMA}"

app = FastAPI(title="UNFRC")
_w: Optional[WorkspaceClient] = None
_sql_cache = SqlCache(FQ)
_poi_cache: Optional[tuple[float, list[dict]]] = None


def w() -> WorkspaceClient:
    global _w
    if _w is None:
        _w = WorkspaceClient()
    return _w


# ── Schema context handed to the model (built from the governed semantic layer) ──
SCHEMA_CONTEXT = f"""
You write DuckDB/Spark-SQL SELECT queries against these Unity Catalog tables in {FQ}.
The MAIN table for almost every question is acute_need_enriched.

{FQ}.acute_need_enriched — one row per ~1km grid cell in the flood-affected area
(Nuwakot, Rasuwa and nearby districts north of Kathmandu). Columns:
  place_name (nearest village/town, English), district, municipality,
  damaged_bld (damaged buildings), total_bld, damage_pct,
  population (estimated people in cell),
  acute_need_score (= damaged_bld * population),
  damaged_bridges_5km (washed-out/damaged bridges within 5km; isolation signal),
  nearest_damaged_bridge_km, nearest_helipad_km,
  likely_isolated (BOOLEAN: TRUE if a damaged bridge is within 5km),
  priority_score (main ranking: acute need boosted by isolation; higher = more urgent),
  lat_k, lon_k (cell center coordinates).

{FQ}.hot_bridge_damage — bridges with volunteer-reported condition.
  name, status (e.g. 'Washed out'), location, adm2_name (district), adm3_name, lat, lon.

{FQ}.hot_helipads — helipads. name, adm2_name, adm3_name, lat, lon.
{FQ}.hot_populated_places — settlements. name_en, place, adm2_name, adm3_name, lat, lon.
{FQ}.hot_roads — roads. name, highway (class), adm2_name, lat, lon.
{FQ}.buildings — individual footprints. damaged (1/0), lat, lon.

New HDX operational layers (all include _lat and _lon representative coordinates):
{FQ}.hdx_destroyed_features — OSM features reported damaged or destroyed.
  name, name_en, name_ne, status, feature_type, damage_type, damage_date,
  adm2_name, adm3_name, _lat, _lon.
{FQ}.hdx_health_facilities — hospitals, clinics, and pharmacies.
  name, name_en, name_ne, status, amenity, adm2_name, adm3_name, _lat, _lon.
{FQ}.hdx_education_facilities — schools and colleges.
  name, name_en, status, amenity, operator_type, adm2_name, adm3_name, _lat, _lon.
{FQ}.hdx_open_spaces — potential shelter or relief-staging open ground.
  name, status, leisure, landuse, natural, adm2_name, adm3_name, _lat, _lon.
{FQ}.hdx_exposed_hydropowers — exposed hydropower projects.
  name, capacity_mw, river, status, district, municipality, _lat, _lon.
{FQ}.hdx_flood_extent — observed flood extent polygon metadata.
  name, area_sq_km, _geometry_json, _lat, _lon.

Rules:
- Return exactly ONE SELECT statement. No DDL/DML/INSERT/UPDATE/DELETE/DROP/CREATE.
- Always fully-qualify tables as {FQ}.<table>.
- Prefer acute_need_enriched. Default to ORDER BY priority_score DESC when ranking need.
- Always include lat_k, lon_k (or lat, lon) so results can be mapped, plus place_name/district when available.
- For HDX tables, select _lat AS lat and _lon AS lon so results can be mapped.
- LIMIT to 50 rows unless the user asks for a count/aggregate.
""".strip()

FORBIDDEN = re.compile(r"\b(insert|update|delete|drop|create|alter|merge|truncate|grant|revoke)\b", re.I)


def _llm(system: str, user: str, max_tokens: int = 900) -> str:
    r = w().serving_endpoints.query(
        name=SERVING_ENDPOINT,
        messages=[
            ChatMessage(role=ChatMessageRole.SYSTEM, content=system),
            ChatMessage(role=ChatMessageRole.USER, content=user),
        ],
        max_tokens=max_tokens,
        temperature=0.0,
    )
    return r.choices[0].message.content


def _extract_sql(raw: str) -> str:
    s = raw.strip()
    if "```" in s:
        parts = s.split("```")
        for p in parts:
            if p.strip().lower().startswith("sql"):
                s = p.strip()[3:].strip()
                break
            if "select" in p.lower():
                s = p.strip()
                break
    m = re.search(r"(select\b.*)", s, re.I | re.S)
    if m:
        s = m.group(1)
    return s.rstrip(";").strip()


def _run_sql(sql: str):
    res = w().statement_execution.execute_statement(
        warehouse_id=WAREHOUSE_ID, statement=sql, wait_timeout="50s"
    )
    cols = [c.name for c in (res.manifest.schema.columns or [])] if res.manifest and res.manifest.schema else []
    rows = res.result.data_array if res.result and res.result.data_array else []
    dict_rows = [dict(zip(cols, r)) for r in rows]
    return cols, dict_rows


class AskReq(BaseModel):
    question: str
    lang: str = "en"  # "en" or "ne"


@app.post("/api/ask")
def ask(req: AskReq):
    lang_name = "Nepali (नेपाली)" if req.lang == "ne" else "English"

    # 1) SQL: suggested-question lookup, then runtime cache, then text-to-SQL
    cached = _sql_cache.get(req.question)
    sql_source = "generated"
    if cached:
        sql, sql_source = cached
    else:
        sql_system = (
            "You are a text-to-SQL engine for a Nepal flood response data app. "
            "Given a question (in English or Nepali), output ONLY a single SQL SELECT query, nothing else.\n\n"
            + SCHEMA_CONTEXT
        )
        raw_sql = _llm(sql_system, req.question, max_tokens=500)
        sql = _extract_sql(raw_sql)

    # 2) Safety gate
    if not sql.lower().lstrip().startswith("select") or FORBIDDEN.search(sql):
        return {
            "ok": False,
            "answer": ("माफ गर्नुहोस्, म त्यो अनुरोध सुरक्षित रूपमा प्रशोधन गर्न सकिनँ।"
                       if req.lang == "ne" else
                       "Sorry, I could not process that request safely."),
            "sql": sql, "sql_source": sql_source, "rows": [], "columns": [],
        }

    # 3) Execute
    try:
        cols, rows = _run_sql(sql)
    except Exception as e:
        return {"ok": False, "answer": f"Query error: {e}", "sql": sql,
                "sql_source": sql_source, "rows": [], "columns": []}

    if sql_source == "generated":
        _sql_cache.remember(req.question, sql)

    # 4) Rows -> natural language answer in the user's language
    preview = json.dumps(rows[:15], default=str)
    ans_system = (
        f"You are UNFRC, a flood-response assistant for Nepal. Answer in {lang_name}. "
        "Be concise and operational (2-4 sentences). Use place names and districts. "
        "Write plain prose only: no markdown headings, bullets, or tables. "
        "The interface displays the result rows separately in an evidence table. "
        "These are prioritization estimates from open data, not an official assessment; "
        "do not overstate certainty. If rows are empty, say no matching data was found."
    )
    ans_user = f"Question: {req.question}\nSQL: {sql}\nResult rows (JSON): {preview}\nWrite the answer."
    answer = _llm(ans_system, ans_user, max_tokens=500)

    # rows that can be mapped
    map_rows = []
    for r in rows:
        lat = r.get("lat_k") or r.get("lat")
        lon = r.get("lon_k") or r.get("lon")
        if lat is not None and lon is not None:
            try:
                map_rows.append({
                    "lat": float(lat), "lon": float(lon),
                    "label": r.get("place_name") or r.get("name") or r.get("district") or "",
                    "priority": r.get("priority_score"), "damaged": r.get("damaged_bld"),
                    "status": r.get("status"),
                })
            except (TypeError, ValueError):
                pass

    return {"ok": True, "answer": answer, "sql": sql, "sql_source": sql_source,
            "columns": cols, "rows": rows[:50], "map_rows": map_rows}


@app.get("/api/health")
def health():
    return {"status": "ok", "endpoint": SERVING_ENDPOINT, "schema": FQ}


@app.get("/api/pois")
def points_of_interest():
    global _poi_cache
    now = time.monotonic()
    if _poi_cache and now - _poi_cache[0] < 300:
        return {"rows": _poi_cache[1], "cached": True}

    sql = f"""
      SELECT 'health' category,
             coalesce(name_en, name, name_latin, 'Health facility') name,
             status, amenity subtype, adm2_name district, adm3_name municipality,
             _lat lat, _lon lon
      FROM {FQ}.hdx_health_facilities
      UNION ALL
      SELECT 'education' category,
             coalesce(name_en, name, name_latin, 'Education facility') name,
             status, amenity subtype, adm2_name district, adm3_name municipality,
             _lat lat, _lon lon
      FROM {FQ}.hdx_education_facilities
      UNION ALL
      SELECT 'open_space' category,
             coalesce(name, name_latin, 'Open space') name,
             status, coalesce(leisure, landuse, natural, 'open space') subtype,
             adm2_name district, adm3_name municipality, _lat lat, _lon lon
      FROM {FQ}.hdx_open_spaces
      UNION ALL
      SELECT 'hydropower' category, name, status, river subtype,
             coalesce(adm2_name, district) district,
             coalesce(adm3_name, municipality) municipality, _lat lat, _lon lon
      FROM {FQ}.hdx_exposed_hydropowers
    """
    _, rows = _run_sql(sql)
    valid = []
    for row in rows:
        try:
            valid.append({
                **row,
                "lat": float(row["lat"]),
                "lon": float(row["lon"]),
            })
        except (KeyError, TypeError, ValueError):
            continue
    _poi_cache = (now, valid)
    return {"rows": valid, "cached": False}


app.mount("/", StaticFiles(directory="static", html=True), name="static")


@app.get("/")
def index():
    return FileResponse("static/index.html")
