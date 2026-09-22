"""Descarga una extracción reproducible de World Development Indicators."""

from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "south_america_indicators.csv"
API = "https://api.worldbank.org/v2/country/{countries}/indicator/{indicator}"

COUNTRIES = {
    "ARG": "Argentina",
    "BOL": "Bolivia",
    "BRA": "Brasil",
    "CHL": "Chile",
    "COL": "Colombia",
    "ECU": "Ecuador",
    "GUY": "Guyana",
    "PRY": "Paraguay",
    "PER": "Perú",
    "SUR": "Surinam",
    "URY": "Uruguay",
    "VEN": "Venezuela",
}

INDICATORS = {
    "NY.GDP.PCAP.CD": ("PIB per cápita", "US$ corrientes"),
    "SP.DYN.LE00.IN": ("Esperanza de vida", "años"),
    "IT.NET.USER.ZS": ("Uso de Internet", "% de la población"),
    "SP.POP.TOTL": ("Población", "personas"),
}


def fetch_indicator(indicator_code: str) -> list[dict[str, object]]:
    countries = ";".join(COUNTRIES)
    response = requests.get(
        API.format(countries=countries, indicator=indicator_code),
        params={"format": "json", "date": "2000:2025", "per_page": 20000},
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, list) or len(payload) < 2:
        raise RuntimeError(f"Respuesta inesperada para {indicator_code}")

    indicator, unit = INDICATORS[indicator_code]
    rows = []
    for item in payload[1]:
        value = item.get("value")
        code = item.get("countryiso3code")
        if value is None or code not in COUNTRIES:
            continue
        rows.append(
            {
                "country": COUNTRIES[code],
                "country_code": code,
                "year": int(item["date"]),
                "indicator": indicator,
                "indicator_code": indicator_code,
                "unit": unit,
                "value": float(value),
            }
        )
    return rows


def main() -> None:
    rows = []
    for indicator_code in INDICATORS:
        rows.extend(fetch_indicator(indicator_code))

    frame = pd.DataFrame(rows).sort_values(["indicator", "country", "year"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(OUTPUT, index=False, encoding="utf-8")
    print(f"Guardadas {len(frame):,} observaciones en {OUTPUT}")


if __name__ == "__main__":
    main()
