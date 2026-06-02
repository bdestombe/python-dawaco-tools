import numpy as np
import pandas as pd
import pytest

import dawacotools as dt
from dawacotools import io as dawaco_io


def test_create_connection_string_uses_default_interactive_authentication(monkeypatch):
    monkeypatch.delenv(dawaco_io.AUTHENTICATION_ENV_VAR, raising=False)

    connection_string = dt.create_connection_string()

    assert "Authentication=ActiveDirectoryInteractive;" in connection_string


def test_create_connection_string_accepts_user_specific_authentication(monkeypatch):
    monkeypatch.setenv(dawaco_io.AUTHENTICATION_ENV_VAR, "ActiveDirectoryIntegrated")

    connection_string = dt.create_connection_string()
    explicit_connection_string = dt.create_connection_string(authentication="ActiveDirectoryPassword")

    assert "Authentication=ActiveDirectoryIntegrated;" in connection_string
    assert "Authentication=ActiveDirectoryPassword;" in explicit_connection_string


def test_get_daw_mps_returns_synthetic_monitoring_points():
    mps = dt.get_daw_mps()

    assert list(mps.index) == ["MOCK001", "MOCK002", "MOCK010"]
    assert mps.crs.to_string() == "EPSG:28992"
    assert mps.loc["MOCK001", "Soort"] == "Waarnemingspunt"
    assert mps.loc["MOCK002", "Soort"] == "Pompput"


def test_get_daw_mps_supports_exact_and_partial_matching():
    exact = dt.get_daw_mps(mpcode="MOCK001", partial_match_mpcode=False)
    no_exact_match = dt.get_daw_mps(mpcode="MOCK00", partial_match_mpcode=False)
    partial = dt.get_daw_mps(mpcode="MOCK00")
    partial_list = dt.get_daw_mps(mpcode=["MOCK001", "MOCK010"])

    assert list(exact.index) == ["MOCK001"]
    assert no_exact_match.empty
    assert list(partial.index) == ["MOCK001", "MOCK002"]
    assert list(partial_list.index) == ["MOCK001", "MOCK010"]


def test_get_daw_mps_binds_mpcode_values_safely():
    injected = dt.get_daw_mps(mpcode="MOCK001' OR '1'='1", partial_match_mpcode=False)

    assert injected.empty


def test_get_daw_filters_excludes_expired_filters_by_default():
    filters = dt.get_daw_filters()

    assert list(filters[["MpCode", "Filtnr"]].itertuples(index=False, name=None)) == [
        ("MOCK001", 1),
        ("MOCK001", 2),
        ("MOCK002", 1),
    ]
    assert filters.crs.to_string() == "EPSG:28992"


def test_get_daw_filters_supports_filter_and_expired_selection():
    filter_one = dt.get_daw_filters(mpcode="MOCK001", filternr=1)
    filter_one_as_string = dt.get_daw_filters(mpcode="MOCK001", filternr="1")
    filter_list = dt.get_daw_filters(mpcode="MOCK001", filternr=[1.0, 2.0])
    no_exact_match = dt.get_daw_filters(mpcode="MOCK00", partial_match_mpcode=False)
    with_expired = dt.get_daw_filters(mpcode="MOCK010", vervallen_filters_meenemen=True)

    assert list(filter_one["Filtnr"]) == [1]
    assert list(filter_one_as_string["Filtnr"]) == [1]
    assert list(filter_list["Filtnr"]) == [1, 2]
    assert no_exact_match.empty
    assert len(with_expired) == 1
    assert with_expired.iloc[0]["Verval_datum"] == pd.Timestamp("2020-01-01")


def test_get_daw_filters_validates_scalar_and_list_filternr_consistently():
    assert dt.get_daw_filters(mpcode="MOCK001", filternr=0).empty
    assert dt.get_daw_filters(mpcode="MOCK001", filternr=[0]).empty

    with pytest.raises(ValueError, match="filternr must be a non-negative integer-like value"):
        dt.get_daw_filters(mpcode="MOCK001", filternr=-1)
    with pytest.raises(ValueError, match="filternr must be a non-negative integer-like value"):
        dt.get_daw_filters(mpcode="MOCK001", filternr=[1, -1])


def test_get_daw_filters_can_return_hydropandas_metadata_shape():
    filters = dt.get_daw_filters(mpcode="MOCK001", filternr=1, return_hpd=True)

    assert filters.crs.to_string() == "EPSG:28992"
    assert filters.iloc[0]["locatie"] == "MOCK001"
    assert filters.iloc[0]["filternr"] == 1
    assert filters.iloc[0]["bovenkant_filter"] == -2.0
    assert filters.iloc[0]["onderkant_filter"] == -4.0
    assert not filters.iloc[0]["vervallen"]


def test_get_daw_mon_dates_returns_unique_sorted_dates():
    dates = dt.get_daw_mon_dates(mpcode="MOCK001", filternr=1)

    assert list(dates) == [pd.Timestamp("2021-01-01"), pd.Timestamp("2021-01-15")]


def test_get_daw_ts_stijghgt_masks_sentinel_values_and_inserts_expected_gaps():
    series = dt.get_daw_ts_stijghgt(mpcode="MOCK001", filternr=1)

    assert list(series.index) == list(pd.date_range("2020-01-01", "2020-01-06", freq="D"))
    assert series.name == "mNAP"
    np.testing.assert_allclose(series.to_numpy(), [1.0, 1.1, np.nan, np.nan, np.nan, 1.4], equal_nan=True)


def test_get_daw_ts_temp_masks_zero_and_sentinel_values():
    series = dt.get_daw_ts_temp(mpcode="MOCK001", filternr=1)

    assert list(series.index) == list(pd.date_range("2020-01-01", "2020-01-06", freq="D"))
    assert series.name == "MOCK001_1"
    np.testing.assert_allclose(series.to_numpy(), [8.0, np.nan, np.nan, np.nan, np.nan, 9.0], equal_nan=True)


def test_get_daw_ts_stijghgt_binds_public_inputs_safely():
    with pytest.raises(ValueError, match="not in Dawaco"):
        dt.get_daw_ts_stijghgt(mpcode="MOCK001' OR '1'='1", filternr=1)
    with pytest.raises(ValueError, match="filternr must be a non-negative integer-like value"):
        dt.get_daw_ts_stijghgt(mpcode="MOCK001", filternr="1 OR 1=1")


def test_identify_data_gaps_preserves_order_when_filling_multiple_gaps():
    index = pd.to_datetime([
        "2020-01-01",
        "2020-01-02",
        "2020-01-05",
        "2020-01-06",
        "2020-01-07",
        "2020-01-10",
        "2020-01-11",
    ])
    series = pd.Series(np.arange(len(index), dtype=float), index=index, name="synthetic")

    filled = dawaco_io.identify_data_gaps(series)

    assert filled.index.is_monotonic_increasing
    assert list(filled.index) == list(pd.date_range("2020-01-01", "2020-01-11", freq="D"))
    assert np.isnan(filled.loc["2020-01-03"])
    assert np.isnan(filled.loc["2020-01-04"])
    assert np.isnan(filled.loc["2020-01-08"])
    assert np.isnan(filled.loc["2020-01-09"])
    assert filled.loc["2020-01-10"] == 5.0


def test_get_daw_ts_meteo_unpivots_month_columns_and_drops_missing_values():
    series = dt.get_daw_ts_meteo("235W", "Neerslag")

    assert series.name == "Station 235W - Neerslag"
    assert list(series.index) == [pd.Timestamp("2020-01-01"), pd.Timestamp("2020-01-03")]
    np.testing.assert_allclose(series.to_numpy(), [1.0, 3.0], equal_nan=True)


def test_get_daw_meteo_from_loc_raises_clear_error_without_covering_station():
    with pytest.raises(ValueError, match="No meteo station covers Neerslag"):
        dt.get_daw_meteo_from_loc(
            x=100000,
            y=500000,
            mettype="Neerslag",
            start_date="1800-01-01",
            end_date="1800-01-31",
        )


def test_get_daw_meteo_arr_daterange_returns_reconstructed_ranges():
    dateranges = dawaco_io.get_daw_meteo_arr_daterange()

    assert list(dateranges.columns) == dawaco_io.meteo_header
    station = dateranges.set_index("statcode").loc["235W"]
    assert station["N_start"] == pd.Timestamp("2020-01-01")
    assert station["N_end"] == pd.Timestamp("2020-01-03")


def test_get_daw_boring_and_triwaco_use_mock_database():
    boring = dt.get_daw_boring(mpcode="MOCK001")
    triwaco = dt.get_daw_triwaco(mpcode="MOCK001")

    assert list(boring.index.unique()) == ["MOCK001"]
    assert set(boring["Omschrijving"]) == {"Synthetic sand", "Synthetic clay"}
    np.testing.assert_allclose(triwaco["dikte"].values, [5.0, 10.0, np.nan])
    assert list(triwaco["bkp_nap"]) == [2.0, -3.0, -13.0]
