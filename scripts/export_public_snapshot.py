#!/usr/bin/env python3
"""Export a safe, read-only UNFRC lakehouse snapshot for the public dashboard.

The public site never receives Databricks credentials. This script runs fixed
SELECT statements, converts spatial rows to GeoJSON, and writes static files
that can be deployed by Vercel or any other static host.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from databricks.sdk import WorkspaceClient


DEFAULT_SCHEMA = "nepal_flood_response"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--profile",
        default=os.environ.get("DATABRICKS_CONFIG_PROFILE"),
        help="Optional Databricks CLI profile. Falls back to DATABRICKS_* env vars.",
    )
    parser.add_argument(
        "--catalog",
        default=os.environ.get("UNFRC_CATALOG"),
        required=not os.environ.get("UNFRC_CATALOG"),
        help="Unity Catalog name that holds the flood-response schema.",
    )
    parser.add_argument("--schema", default=os.environ.get("UNFRC_SCHEMA", DEFAULT_SCHEMA))
    parser.add_argument(
        "--warehouse-id",
        default=os.environ.get("SQL_WAREHOUSE_ID"),
        required=not os.environ.get("SQL_WAREHOUSE_ID"),
        help="SQL warehouse used for the read-only snapshot queries.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "public-dashboard" / "data",
    )
    return parser.parse_args()


def clean_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, str):
        lowered = value.lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
        try:
            number = float(value)
            return int(number) if number.is_integer() else number
        except ValueError:
            return value
    return value


def query(client: WorkspaceClient, warehouse_id: str, statement: str) -> list[dict[str, Any]]:
    response = client.statement_execution.execute_statement(
        warehouse_id=warehouse_id,
        statement=statement,
        wait_timeout="50s",
    )
    if response.status and response.status.state and response.status.state.value != "SUCCEEDED":
        message = response.status.error.message if response.status.error else "Unknown SQL error"
        raise RuntimeError(message)
    columns = [column.name for column in response.manifest.schema.columns]
    rows = response.result.data_array or []
    return [
        {column: clean_value(value) for column, value in zip(columns, row)}
        for row in rows
    ]


def point_collection(
    rows: Iterable[dict[str, Any]],
    *,
    lat_column: str,
    lon_column: str,
) -> dict[str, Any]:
    features = []
    for row in rows:
        lat = row.get(lat_column)
        lon = row.get(lon_column)
        if lat is None or lon is None:
            continue
        lat_number = float(lat)
        lon_number = float(lon)
        if not math.isfinite(lat_number) or not math.isfinite(lon_number):
            continue
        properties = {
            key: value
            for key, value in row.items()
            if key not in {lat_column, lon_column}
        }
        features.append(
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [lon_number, lat_number]},
                "properties": properties,
            }
        )
    return {"type": "FeatureCollection", "features": features}


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    client = WorkspaceClient(profile=args.profile) if args.profile else WorkspaceClient()
    fq = f"`{args.catalog}`.`{args.schema}`"

    cells = query(
        client,
        args.warehouse_id,
        f"""
        SELECT lat_k, lon_k, place_name, district, municipality,
               damaged_bld, total_bld, damage_pct, population, acute_need_score,
               damaged_bridges_5km, nearest_damaged_bridge_km,
               nearest_helipad_km, likely_isolated, priority_score
        FROM {fq}.`acute_need_enriched`
        ORDER BY priority_score DESC
        """,
    )
    districts = query(
        client,
        args.warehouse_id,
        f"""
        SELECT district, count(*) affected_cells,
               sum(damaged_bld) damaged_buildings,
               round(sum(population * damaged_bld / total_bld)) estimated_people,
               sum(CASE WHEN likely_isolated THEN 1 ELSE 0 END) isolated_cells,
               round(sum(acute_need_score)) acute_need_score,
               round(sum(priority_score)) priority_score
        FROM {fq}.`acute_need_enriched`
        GROUP BY district
        ORDER BY priority_score DESC
        """,
    )
    summary_rows = query(
        client,
        args.warehouse_id,
        f"""
        SELECT count(*) affected_cells,
               sum(damaged_bld) damaged_buildings,
               round(sum(population * damaged_bld / total_bld)) estimated_people,
               sum(CASE WHEN likely_isolated THEN 1 ELSE 0 END) isolated_cells,
               count(DISTINCT district) districts
        FROM {fq}.`acute_need_enriched`
        """,
    )
    bridges = query(
        client,
        args.warehouse_id,
        f"""
        SELECT name, status, location, adm2_name district,
               adm3_name municipality, lat, lon
        FROM {fq}.`hot_bridge_damage`
        WHERE lat IS NOT NULL AND lon IS NOT NULL
        """,
    )
    helipads = query(
        client,
        args.warehouse_id,
        f"""
        SELECT coalesce(name, 'Helipad') name, adm2_name district,
               adm3_name municipality, lat, lon
        FROM {fq}.`hot_helipads`
        WHERE lat IS NOT NULL AND lon IS NOT NULL
        """,
    )
    pois = query(
        client,
        args.warehouse_id,
        f"""
        SELECT 'health' category,
               coalesce(name_en, name, name_latin, 'Health facility') name,
               status, amenity subtype, adm2_name district,
               adm3_name municipality, _lat lat, _lon lon
        FROM {fq}.`hdx_health_facilities`
        UNION ALL
        SELECT 'education', coalesce(name_en, name, name_latin, 'Education facility'),
               status, amenity, adm2_name, adm3_name, _lat, _lon
        FROM {fq}.`hdx_education_facilities`
        UNION ALL
        SELECT 'open_space', coalesce(name, name_latin, 'Open space'),
               status, coalesce(leisure, landuse, natural, 'open space'),
               adm2_name, adm3_name, _lat, _lon
        FROM {fq}.`hdx_open_spaces`
        UNION ALL
        SELECT 'hydropower', name, status, river,
               coalesce(adm2_name, district), coalesce(adm3_name, municipality),
               _lat, _lon
        FROM {fq}.`hdx_exposed_hydropowers`
        """,
    )
    source_rows = query(
        client,
        args.warehouse_id,
        f"""
        SELECT resource_name, source_modified_at,
               row_count, status, ingested_at
        FROM {fq}.`hdx_ingestion_state`
        QUALIFY row_number() OVER (
          PARTITION BY table_name ORDER BY ingested_at DESC
        ) = 1
        ORDER BY table_name
        """,
    )
    flood_rows = query(
        client,
        args.warehouse_id,
        f"""
        SELECT name, area_sq_km, _geometry_json geometry_json
        FROM {fq}.`hdx_flood_extent`
        LIMIT 1
        """,
    )

    flood_features = []
    for row in flood_rows:
        geometry_json = row.pop("geometry_json", None)
        if geometry_json:
            flood_features.append(
                {
                    "type": "Feature",
                    "geometry": json.loads(geometry_json),
                    "properties": row,
                }
            )

    generated_at = datetime.now(timezone.utc).isoformat()
    meta = {
        "generated_at": generated_at,
        "as_of_label": datetime.now(timezone.utc).strftime("%d %b %Y, %H:%M UTC"),
        "summary": summary_rows[0],
        "districts": districts,
        "sources": source_rows,
        "methodology": {
            "grid": "Approximately 1 km cells (0.01 degrees)",
            "acute_need_score": "damaged buildings × population",
            "likely_isolated": "one or more damaged bridges within 5 km",
            "priority_score": "acute need × (1 + 0.5 × damaged bridges within 5 km)",
        },
        "notice": "Prototype derived from open humanitarian data; not an official assessment.",
    }

    write_json(args.output / "meta.json", meta)
    write_json(
        args.output / "need-cells.geojson",
        point_collection(cells, lat_column="lat_k", lon_column="lon_k"),
    )
    write_json(
        args.output / "pois.geojson",
        point_collection(pois, lat_column="lat", lon_column="lon"),
    )
    write_json(
        args.output / "bridges.geojson",
        point_collection(bridges, lat_column="lat", lon_column="lon"),
    )
    write_json(
        args.output / "helipads.geojson",
        point_collection(helipads, lat_column="lat", lon_column="lon"),
    )
    write_json(
        args.output / "flood-extent.geojson",
        {"type": "FeatureCollection", "features": flood_features},
    )
    print(
        f"Exported {len(cells)} need cells, {len(pois)} POIs, "
        f"{len(bridges)} bridges, and {len(helipads)} helipads to {args.output}"
    )


if __name__ == "__main__":
    main()
