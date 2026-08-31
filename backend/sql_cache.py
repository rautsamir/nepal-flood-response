"""Suggested-question SQL lives in this module (app source), not in a warehouse table.

Ad-hoc questions that miss this map still go through text-to-SQL; their generated
SQL is remembered in process memory for the life of the Databricks App replica.
"""
from __future__ import annotations

import re
from typing import Optional

_WS = re.compile(r"\s+")


def normalize_question(q: str) -> str:
    return _WS.sub(" ", (q or "").strip()).casefold()


def suggested_sql(fq: str) -> dict[str, str]:
    t = f"{fq}.acute_need_enriched"
    bridges = f"{fq}.hot_bridge_damage"
    cols = (
        "place_name, district, municipality, damaged_bld, total_bld, damage_pct, "
        "population, acute_need_score, damaged_bridges_5km, nearest_damaged_bridge_km, "
        "nearest_helipad_km, likely_isolated, priority_score, lat_k, lon_k"
    )
    return {
        "Which areas need help most urgently?":
            f"SELECT {cols} FROM {t} ORDER BY priority_score DESC LIMIT 50",
        "कुन क्षेत्रलाई सबैभन्दा तत्काल सहयोग चाहिन्छ?":
            f"SELECT {cols} FROM {t} ORDER BY priority_score DESC LIMIT 50",
        "Which villages may be cut off by damaged bridges?":
            f"SELECT {cols} FROM {t} WHERE likely_isolated = TRUE ORDER BY priority_score DESC LIMIT 50",
        "कुन गाउँ क्षतिग्रस्त पुलका कारण काटिएका हुन सक्छन्?":
            f"SELECT {cols} FROM {t} WHERE likely_isolated = TRUE ORDER BY priority_score DESC LIMIT 50",
        "Which isolated areas are farthest from a helipad?":
            f"SELECT {cols} FROM {t} WHERE likely_isolated = TRUE ORDER BY nearest_helipad_km DESC NULLS LAST LIMIT 50",
        "कुन एकान्त क्षेत्र हेलिप्याडबाट सबैभन्दा टाढा छन्?":
            f"SELECT {cols} FROM {t} WHERE likely_isolated = TRUE ORDER BY nearest_helipad_km DESC NULLS LAST LIMIT 50",
        "Where is building damage the most severe?":
            f"SELECT {cols} FROM {t} ORDER BY damaged_bld DESC, damage_pct DESC LIMIT 50",
        "भवन क्षति सबैभन्दा गम्भीर कहाँ छ?":
            f"SELECT {cols} FROM {t} ORDER BY damaged_bld DESC, damage_pct DESC LIMIT 50",
        "Which municipalities have the most people in damaged areas?":
            f"SELECT municipality, district, SUM(population) AS population, "
            f"SUM(damaged_bld) AS damaged_bld, SUM(acute_need_score) AS acute_need_score, "
            f"AVG(lat_k) AS lat_k, AVG(lon_k) AS lon_k "
            f"FROM {t} WHERE damaged_bld > 0 GROUP BY municipality, district "
            f"ORDER BY population DESC LIMIT 50",
        "कुन नगरपालिकामा क्षतिग्रस्त क्षेत्रमा सबैभन्दा बढी मानिस छन्?":
            f"SELECT municipality, district, SUM(population) AS population, "
            f"SUM(damaged_bld) AS damaged_bld, SUM(acute_need_score) AS acute_need_score, "
            f"AVG(lat_k) AS lat_k, AVG(lon_k) AS lon_k "
            f"FROM {t} WHERE damaged_bld > 0 GROUP BY municipality, district "
            f"ORDER BY population DESC LIMIT 50",
        "Which bridges are washed out, and in which districts?":
            f"SELECT name, status, location, adm2_name AS district, adm3_name, lat, lon "
            f"FROM {bridges} WHERE lower(coalesce(status, '')) LIKE '%wash%' "
            f"ORDER BY adm2_name LIMIT 50",
        "कुन पुलहरू बगेका छन्, र कुन जिल्लामा?":
            f"SELECT name, status, location, adm2_name AS district, adm3_name, lat, lon "
            f"FROM {bridges} WHERE lower(coalesce(status, '')) LIKE '%wash%' "
            f"ORDER BY adm2_name LIMIT 50",
        "Which high-need areas are farthest from any helipad?":
            f"SELECT {cols} FROM {t} WHERE damaged_bld > 0 "
            f"ORDER BY nearest_helipad_km DESC NULLS LAST, priority_score DESC LIMIT 50",
        "उच्च आवश्यकता भएका कुन क्षेत्र हेलिप्याडबाट सबैभन्दा टाढा छन्?":
            f"SELECT {cols} FROM {t} WHERE damaged_bld > 0 "
            f"ORDER BY nearest_helipad_km DESC NULLS LAST, priority_score DESC LIMIT 50",
        "How many buildings are damaged in Rasuwa district?":
            f"SELECT district, SUM(damaged_bld) AS damaged_bld, SUM(total_bld) AS total_bld, "
            f"SUM(population) AS population, AVG(lat_k) AS lat_k, AVG(lon_k) AS lon_k "
            f"FROM {t} WHERE lower(district) = 'rasuwa' GROUP BY district LIMIT 50",
        "रसुवा जिल्लामा कति भवन क्षतिग्रस्त छन्?":
            f"SELECT district, SUM(damaged_bld) AS damaged_bld, SUM(total_bld) AS total_bld, "
            f"SUM(population) AS population, AVG(lat_k) AS lat_k, AVG(lon_k) AS lon_k "
            f"FROM {t} WHERE lower(district) = 'rasuwa' GROUP BY district LIMIT 50",
    }


class SqlCache:
    def __init__(self, fq: str):
        self._suggested = {normalize_question(k): v for k, v in suggested_sql(fq).items()}
        self._runtime: dict[str, str] = {}

    def get(self, question: str) -> Optional[tuple[str, str]]:
        key = normalize_question(question)
        if key in self._suggested:
            return self._suggested[key], "suggested"
        if key in self._runtime:
            return self._runtime[key], "runtime"
        return None

    def remember(self, question: str, sql: str) -> None:
        self._runtime[normalize_question(question)] = sql
