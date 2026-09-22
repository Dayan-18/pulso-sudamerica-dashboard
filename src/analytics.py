"""Cálculos reutilizables para el dashboard."""

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Summary:
    year: int
    first_year: int
    median: float
    change_pct: float | None
    leader: str
    leader_value: float
    countries: int


def latest_common_year(frame: pd.DataFrame, expected_countries: int) -> int:
    """Find the newest year with data for every selected country."""
    counts = frame.groupby("year")["country_code"].nunique()
    complete = counts[counts >= expected_countries]
    if not complete.empty:
        return int(complete.index.max())
    return int(frame["year"].max())


def build_summary(frame: pd.DataFrame, expected_countries: int) -> Summary:
    """Calculate comparable headline values from the selected slice."""
    if frame.empty:
        raise ValueError("No existen datos para la selección.")

    latest_year = latest_common_year(frame, expected_countries)
    first_year = int(frame["year"].min())
    latest = frame.loc[frame["year"].eq(latest_year)]
    first = frame.loc[frame["year"].eq(first_year)]

    latest_median = float(latest["value"].median())
    first_median = float(first["value"].median())
    change_pct = None if first_median == 0 else ((latest_median / first_median) - 1) * 100
    leader_row = latest.loc[latest["value"].idxmax()]

    return Summary(
        year=latest_year,
        first_year=first_year,
        median=latest_median,
        change_pct=change_pct,
        leader=str(leader_row["country"]),
        leader_value=float(leader_row["value"]),
        countries=int(latest["country_code"].nunique()),
    )


def development_snapshot(frame: pd.DataFrame, countries: list[str], max_year: int) -> pd.DataFrame:
    """Build the latest complete country-level snapshot for the bubble chart."""
    selected = frame.loc[frame["country"].isin(countries) & frame["year"].le(max_year)]
    pivot = selected.pivot_table(
        index=["country", "country_code", "year"],
        columns="indicator_code",
        values="value",
        aggfunc="first",
    ).reset_index()

    required = ["NY.GDP.PCAP.CD", "SP.DYN.LE00.IN", "IT.NET.USER.ZS", "SP.POP.TOTL"]
    complete = pivot.dropna(subset=required).copy()
    if complete.empty:
        return complete

    year_counts = complete.groupby("year")["country_code"].nunique()
    target_count = min(len(countries), int(year_counts.max()))
    valid_years = year_counts[year_counts >= target_count].index
    year = int(valid_years.max())
    return complete.loc[complete["year"].eq(year)].copy()
