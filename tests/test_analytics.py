import pandas as pd

from src.analytics import build_summary, latest_common_year


def sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "country": ["A", "B", "A", "B"],
            "country_code": ["AAA", "BBB", "AAA", "BBB"],
            "year": [2020, 2020, 2021, 2021],
            "value": [10.0, 20.0, 15.0, 30.0],
        }
    )


def test_latest_common_year() -> None:
    assert latest_common_year(sample_frame(), 2) == 2021


def test_build_summary() -> None:
    summary = build_summary(sample_frame(), 2)
    assert summary.year == 2021
    assert summary.median == 22.5
    assert summary.change_pct == 50.0
    assert summary.leader == "B"
    assert summary.countries == 2
