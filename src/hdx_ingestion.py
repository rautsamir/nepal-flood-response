# Databricks notebook source
"""Checksum-aware HDX ingestion for the UNFRC Nepal flood response schema.

The job polls HDX's public CKAN API, downloads only changed GeoJSON resources,
keeps immutable raw snapshots in a Unity Catalog volume, and replaces one
curated Delta table per resource.
"""

# COMMAND ----------

import json
import os
import re
import shutil
import tempfile
import urllib.request
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from pyspark.sql.types import (
    BooleanType,
    DoubleType,
    LongType,
    StringType,
    StructField,
    StructType,
    TimestampType,
)

dbutils.widgets.text("catalog", "rautsamir")
dbutils.widgets.text("schema", "nepal_flood_response")
dbutils.widgets.text("volume", "source_files")

CATALOG = dbutils.widgets.get("catalog")
SCHEMA = dbutils.widgets.get("schema")
VOLUME = dbutils.widgets.get("volume")
FQ = f"`{CATALOG}`.`{SCHEMA}`"
VOLUME_ROOT = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}/hdx"
STATE_TABLE = f"{FQ}.`hdx_ingestion_state`"
HDX_API = "https://data.humdata.org/api/3/action/resource_show?id={resource_id}"
USER_AGENT = "UNFRC-HDX-Ingestion/1.0 (samir.raut@databricks.com)"

RESOURCES = [
    {
        "table": "hdx_flood_extent",
        "resource_id": "46aadcbe-16cc-492e-a3d9-60509cedfbb6",
        "description": "Observed flood extent on 27 August 2026.",
    },
    {
        "table": "hdx_destroyed_features",
        "resource_id": "db0f6639-2fa7-4763-a06c-19475c3a9bcf",
        "description": "OSM features reported destroyed or damaged during the response.",
    },
    {
        "table": "hdx_health_facilities",
        "resource_id": "7eb1b3a0-9539-42dd-b62d-57642960c918",
        "description": "OSM hospitals, clinics, pharmacies, doctors, and dentists.",
    },
    {
        "table": "hdx_education_facilities",
        "resource_id": "5b0b2f0a-9099-495f-b795-3e3f6b0e9427",
        "description": "OSM schools, kindergartens, colleges, and universities.",
    },
    {
        "table": "hdx_open_spaces",
        "resource_id": "f23522c5-b87d-4568-9427-e44c0ebcf108",
        "description": "OSM open ground that may support shelter or relief staging.",
    },
    {
        "table": "hdx_exposed_hydropowers",
        "resource_id": "f6a9b580-087a-40b2-bed4-4aea9478db03",
        "description": "Hydropower projects exposed along the Bhote Koshi and Trishuli.",
    },
]

spark.sql(f"USE CATALOG `{CATALOG}`")
spark.sql(f"USE SCHEMA `{SCHEMA}`")
spark.sql(
    f"""
    CREATE TABLE IF NOT EXISTS {STATE_TABLE} (
      resource_id STRING,
      table_name STRING,
      resource_name STRING,
      source_hash STRING,
      source_modified_at STRING,
      download_url STRING,
      row_count BIGINT,
      status STRING,
      message STRING,
      ingested_at TIMESTAMP
    ) USING DELTA
    COMMENT 'Audit history for checksum-aware HDX ingestion'
    """
)

# COMMAND ----------


def request_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def download(url: str, destination: Path) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response, destination.open("wb") as output:
        shutil.copyfileobj(response, output)


def find_geojson(downloaded: Path, workdir: Path) -> Path:
    if zipfile.is_zipfile(downloaded):
        extract_dir = workdir / "extracted"
        extract_dir.mkdir()
        with zipfile.ZipFile(downloaded) as archive:
            archive.extractall(extract_dir)
        candidates = sorted(
            path for path in extract_dir.rglob("*")
            if path.suffix.lower() in {".geojson", ".json"} and path.name.lower() != "metadata.json"
        )
        if not candidates:
            raise ValueError("Downloaded archive contains no GeoJSON file")
        return candidates[0]
    return downloaded


def coordinate_pairs(value: Any) -> Iterable[tuple[float, float]]:
    if (
        isinstance(value, list)
        and len(value) >= 2
        and isinstance(value[0], (int, float))
        and isinstance(value[1], (int, float))
    ):
        yield float(value[0]), float(value[1])
        return
    if isinstance(value, list):
        for child in value:
            yield from coordinate_pairs(child)


def center(geometry: dict[str, Any]) -> tuple[float | None, float | None]:
    points = list(coordinate_pairs(geometry.get("coordinates")))
    if not points:
        return None, None
    lons, lats = zip(*points)
    return (min(lons) + max(lons)) / 2.0, (min(lats) + max(lats)) / 2.0


def safe_column(name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_]", "_", name.strip()).lower()
    value = re.sub(r"_+", "_", value).strip("_")
    if not value:
        value = "property"
    if value[0].isdigit():
        value = f"property_{value}"
    return value


def scalar(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def infer_type(values: list[Any]):
    populated = [value for value in values if value is not None]
    if populated and all(isinstance(value, bool) for value in populated):
        return BooleanType()
    if populated and all(isinstance(value, int) and not isinstance(value, bool) for value in populated):
        return LongType()
    if populated and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in populated):
        return DoubleType()
    return StringType()


def convert(value: Any, data_type):
    if value is None:
        return None
    if isinstance(data_type, StringType):
        return str(value)
    if isinstance(data_type, BooleanType):
        return bool(value)
    if isinstance(data_type, LongType):
        return int(value)
    if isinstance(data_type, DoubleType):
        return float(value)
    return value


def dataframe_from_geojson(
    geojson_path: Path,
    resource_id: str,
    source_hash: str,
    source_modified_at: str,
):
    with geojson_path.open(encoding="utf-8") as handle:
        document = json.load(handle)
    features = document.get("features") or []
    if not isinstance(features, list):
        raise ValueError("GeoJSON document does not contain a feature list")

    property_names = sorted(
        {str(key) for feature in features for key in (feature.get("properties") or {}).keys()}
    )
    column_map: dict[str, str] = {}
    used: set[str] = set()
    for original in property_names:
        candidate = safe_column(original)
        base = candidate
        suffix = 2
        while candidate in used or candidate.startswith("_"):
            candidate = f"{base}_{suffix}"
            suffix += 1
        used.add(candidate)
        column_map[original] = candidate

    rows: list[dict[str, Any]] = []
    for feature in features:
        properties = feature.get("properties") or {}
        geometry = feature.get("geometry") or {}
        lon, lat = center(geometry)
        row = {column_map[name]: scalar(properties.get(name)) for name in property_names}
        row.update(
            {
                "_geometry_type": geometry.get("type"),
                "_geometry_json": json.dumps(geometry, ensure_ascii=False, separators=(",", ":")),
                "_lon": lon,
                "_lat": lat,
                "_resource_id": resource_id,
                "_source_hash": source_hash,
                "_source_modified_at": source_modified_at,
                "_ingested_at": datetime.now(timezone.utc),
            }
        )
        rows.append(row)

    ordered_columns = [column_map[name] for name in property_names] + [
        "_geometry_type",
        "_geometry_json",
        "_lon",
        "_lat",
        "_resource_id",
        "_source_hash",
        "_source_modified_at",
        "_ingested_at",
    ]
    types = {}
    for column in ordered_columns:
        if column in {"_lon", "_lat"}:
            types[column] = DoubleType()
        elif column == "_ingested_at":
            types[column] = TimestampType()
        else:
            types[column] = infer_type([row.get(column) for row in rows])
    schema = StructType([StructField(column, types[column], True) for column in ordered_columns])
    normalized_rows = [
        tuple(convert(row.get(column), types[column]) for column in ordered_columns)
        for row in rows
    ]
    return spark.createDataFrame(normalized_rows, schema)


def current_hash(resource_id: str) -> str | None:
    escaped = resource_id.replace("'", "''")
    rows = spark.sql(
        f"""
        SELECT source_hash
        FROM {STATE_TABLE}
        WHERE resource_id = '{escaped}' AND status = 'SUCCESS'
        ORDER BY ingested_at DESC
        LIMIT 1
        """
    ).collect()
    return rows[0]["source_hash"] if rows else None


STATE_SCHEMA = StructType(
    [
        StructField("resource_id", StringType(), False),
        StructField("table_name", StringType(), False),
        StructField("resource_name", StringType(), True),
        StructField("source_hash", StringType(), True),
        StructField("source_modified_at", StringType(), True),
        StructField("download_url", StringType(), True),
        StructField("row_count", LongType(), True),
        StructField("status", StringType(), False),
        StructField("message", StringType(), True),
        StructField("ingested_at", TimestampType(), False),
    ]
)


def record_state(
    resource: dict[str, str],
    metadata: dict[str, Any],
    row_count: int | None,
    status: str,
    message: str,
) -> None:
    row = (
        resource["resource_id"],
        resource["table"],
        metadata.get("name"),
        str(metadata.get("hash") or "").strip('"') or None,
        metadata.get("last_modified"),
        metadata.get("download_url") or metadata.get("url"),
        row_count,
        status,
        message[:2000],
        datetime.now(timezone.utc),
    )
    spark.createDataFrame([row], STATE_SCHEMA).write.mode("append").saveAsTable(STATE_TABLE)


# COMMAND ----------

summary: list[dict[str, Any]] = []
failures: list[str] = []

for resource in RESOURCES:
    metadata: dict[str, Any] = {}
    table_name = resource["table"]
    resource_id = resource["resource_id"]
    try:
        response = request_json(HDX_API.format(resource_id=resource_id))
        if not response.get("success"):
            raise RuntimeError(f"HDX API returned failure: {response}")
        metadata = response["result"]
        source_hash = str(metadata.get("hash") or "").strip('"')
        if not source_hash:
            source_hash = re.sub(r"[^0-9A-Za-z]+", "_", metadata["last_modified"])

        if current_hash(resource_id) == source_hash and spark.catalog.tableExists(table_name):
            print(f"SKIP {table_name}: source hash {source_hash} is unchanged")
            summary.append({"table": table_name, "status": "UNCHANGED", "hash": source_hash})
            continue

        with tempfile.TemporaryDirectory(prefix=f"{table_name}_") as temporary:
            workdir = Path(temporary)
            downloaded = workdir / "resource"
            download(metadata.get("download_url") or metadata["url"], downloaded)
            geojson_path = find_geojson(downloaded, workdir)

            raw_dir = f"{VOLUME_ROOT}/{table_name}"
            raw_path = f"{raw_dir}/{source_hash}.geojson"
            os.makedirs(raw_dir, exist_ok=True)
            shutil.copyfile(geojson_path, raw_path)

            frame = dataframe_from_geojson(
                geojson_path,
                resource_id,
                source_hash,
                metadata.get("last_modified") or "",
            )
            row_count = frame.count()
            (
                frame.write.mode("overwrite")
                .option("overwriteSchema", "true")
                .saveAsTable(f"{CATALOG}.{SCHEMA}.{table_name}")
            )
            description = resource["description"].replace("'", "''")
            spark.sql(
                f"COMMENT ON TABLE {FQ}.`{table_name}` IS "
                f"'HDX resource {resource_id}. {description}'"
            )
            record_state(resource, metadata, row_count, "SUCCESS", raw_path)
            print(f"REFRESHED {table_name}: {row_count:,} rows from {source_hash}")
            summary.append(
                {"table": table_name, "status": "REFRESHED", "rows": row_count, "hash": source_hash}
            )
    except Exception as error:
        message = f"{type(error).__name__}: {error}"
        failures.append(f"{table_name}: {message}")
        record_state(resource, metadata, None, "FAILED", message)
        print(f"FAILED {table_name}: {message}")

print(json.dumps(summary, indent=2))
if failures:
    raise RuntimeError("One or more HDX resources failed:\n" + "\n".join(failures))

dbutils.notebook.exit(json.dumps(summary))
