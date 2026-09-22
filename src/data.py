"""Carga, validación y metadatos de los indicadores."""

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "south_america_indicators.csv"

INDICATORS = {
    "PIB per cápita": {
        "code": "NY.GDP.PCAP.CD",
        "unit": "US$ corrientes",
        "description": "Producto interno bruto por habitante.",
    },
    "Esperanza de vida": {
        "code": "SP.DYN.LE00.IN",
        "unit": "años",
        "description": "Años de vida esperados al nacer.",
    },
    "Uso de Internet": {
        "code": "IT.NET.USER.ZS",
        "unit": "% de la población",
        "description": "Personas que utilizaron Internet.",
    },
    "Población": {
        "code": "SP.POP.TOTL",
        "unit": "personas",
        "description": "Población total estimada.",
    },
}

REQUIRED_COLUMNS = {
    "country",
    "country_code",
    "year",
    "indicator",
    "indicator_code",
    "unit",
    "value",
}


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    """Read the local World Bank extract and enforce its public data contract."""
    frame = pd.read_csv(path)
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {', '.join(sorted(missing))}")

    frame = frame.dropna(subset=["value"]).copy()
    frame["year"] = pd.to_numeric(frame["year"], errors="raise").astype(int)
    frame["value"] = pd.to_numeric(frame["value"], errors="raise")
    frame = frame.drop_duplicates(["country_code", "year", "indicator_code"])
    return frame.sort_values(["indicator", "country", "year"]).reset_index(drop=True)


def indicator_frame(frame: pd.DataFrame, indicator: str) -> pd.DataFrame:
    """Return one indicator using the human-readable label exposed by the UI."""
    if indicator not in INDICATORS:
        raise KeyError(f"Indicador desconocido: {indicator}")
    code = INDICATORS[indicator]["code"]
    return frame.loc[frame["indicator_code"].eq(code)].copy()
