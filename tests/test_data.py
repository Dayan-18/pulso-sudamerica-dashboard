from src.data import INDICATORS, load_data


def test_dataset_has_expected_schema_and_indicators() -> None:
    frame = load_data()
    assert not frame.empty
    assert set(frame["indicator_code"].unique()) == {
        metadata["code"] for metadata in INDICATORS.values()
    }
    assert frame["country_code"].nunique() >= 10
    assert frame["year"].min() == 2000
    assert frame["value"].notna().all()


def test_dataset_primary_key_is_unique() -> None:
    frame = load_data()
    assert not frame.duplicated(["country_code", "year", "indicator_code"]).any()
