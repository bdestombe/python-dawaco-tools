import numpy as np
import pandas as pd

import dawacotools as dt


def test_remove_outliers_replaces_values_outside_threshold():
    series = pd.Series([1.0, 1.1, 0.9, 10.0])

    result = dt.analysis.remove_outliers(series, threshold=1.0)

    assert np.isnan(result.iloc[-1])
    assert result.iloc[:3].notna().all()


def test_compute_residence_time_uses_datetime_elapsed_days_for_explicit_pore_volume():
    index = pd.date_range("2020-01-01", periods=5, freq="12h")
    flow = pd.Series(12.0, index=index)

    result = dt.analysis.compute_residence_time(flow, pore_volume_reservoir=6.0)

    expected = pd.Series(0.5, index=index)
    pd.testing.assert_series_equal(result, expected)


def test_compute_residence_time_can_derive_pore_volume_from_average_residence_time():
    index = pd.date_range("2020-01-01", periods=5, freq="D")
    flow = pd.Series(8.0, index=index)

    result = dt.analysis.compute_residence_time(flow, average_residence_time=1.25)

    expected = pd.Series(1.25, index=index)
    pd.testing.assert_series_equal(result, expected)


def test_compute_residence_time_supports_flow_direction_and_retardation():
    index = pd.date_range("2020-01-01", periods=5, freq="D")
    flow = pd.Series(10.0, index=index)

    extraction = dt.analysis.compute_residence_time(flow, pore_volume_reservoir=20.0)
    infiltration = dt.analysis.compute_residence_time(
        flow,
        pore_volume_reservoir=20.0,
        extraction_infiltration="infiltration",
    )
    retarded = dt.analysis.compute_residence_time(flow, pore_volume_reservoir=20.0, retardation_factor=1.5)

    pd.testing.assert_series_equal(extraction, pd.Series(2.0, index=index))
    pd.testing.assert_series_equal(infiltration, pd.Series(2.0, index=index))
    pd.testing.assert_series_equal(retarded, pd.Series(3.0, index=index))


def test_potential_to_flow_uses_filter_metadata_and_static_heads():
    result = dt.potential_to_flow(
        mpcode1="MOCK001",
        filternr1=1,
        mpcode2="MOCK002",
        filternr2=1,
        dh1=1.0,
        dh2=2.0,
        hydraulic_conductivity=10.0,
        porosity=0.25,
    )

    np.testing.assert_allclose(result["distance"], np.array([5.0]))
    pd.testing.assert_series_equal(result["gradient"], pd.Series([0.1]), check_names=False)
    pd.testing.assert_series_equal(result["specific_discharge"], pd.Series([1.0]), check_names=False)
    pd.testing.assert_series_equal(result["poreflow_velocity"], pd.Series([4.0]), check_names=False)
    pd.testing.assert_series_equal(result["duration"], pd.Series([1.25]), check_names=False)


def test_potential_to_flow_resamples_dynamic_head_series():
    result = dt.potential_to_flow(
        mpcode1="MOCK001",
        filternr1=1,
        mpcode2="MOCK002",
        filternr2=1,
        hydraulic_conductivity=10.0,
        porosity=0.25,
    )

    index = pd.date_range("2020-01-01", "2020-01-06", freq="D")
    expected_gradient = pd.Series([0.05, 0.05, np.nan, np.nan, np.nan, 0.01], index=index)
    expected_duration = pd.Series([2.5, 2.5, np.nan, np.nan, np.nan, 12.5], index=index)

    pd.testing.assert_series_equal(result["gradient"], expected_gradient, check_freq=False, check_names=False)
    pd.testing.assert_series_equal(result["duration"], expected_duration, check_freq=False, check_names=False)


def test_get_well_info_uses_mock_database_and_current_filter_columns(monkeypatch):
    meteo_calls = []
    regis_calls = []

    def fake_meteo_from_loc(*, x, y, mettype, start_date, end_date):
        meteo_calls.append({
            "x": x,
            "y": y,
            "mettype": mettype,
            "start_date": start_date,
            "end_date": end_date,
        })
        return pd.Series([1.0], index=pd.DatetimeIndex([start_date]), name=mettype), [("MOCK", 0.0, None)]

    regis = {"source": "synthetic-regis"}

    def fake_regis_ds(x, y, keys=None):
        regis_calls.append((x, y, keys))
        return regis

    monkeypatch.setattr(dt.analysis, "get_daw_meteo_from_loc", fake_meteo_from_loc)
    monkeypatch.setattr(dt.analysis, "get_regis_ds", fake_regis_ds)

    info = dt.get_well_info(mpcode="MOCK001", filternr=1)

    assert info["filter_metadata"].iloc[0]["MpCode"] == "MOCK001"
    assert info["filter_metadata"].iloc[0]["Filtnr"] == 1
    assert info["gws"].loc["2020-01-01"] == 1.0
    assert info["gwt"].loc["2020-01-01"] == 8.0
    assert list(info["boring"].index.unique()) == ["MOCK001"]
    assert list(info["triwaco"]["Mpcode"].unique()) == ["MOCK001"]
    assert info["regis"] is regis
    assert regis_calls == [(100000.0, 500000.0, None)]
    assert {call["mettype"] for call in meteo_calls} == set(dt.analysis.meteo_pars)
    assert all(call["x"] == 100000.0 and call["y"] == 500000.0 for call in meteo_calls)
    assert all(call["start_date"] == pd.Timestamp("2020-01-01") for call in meteo_calls)
    assert all(call["end_date"] == pd.Timestamp("2020-01-06") for call in meteo_calls)


def test_get_cluster_mps_finds_nearby_monitoring_points():
    mps = dt.get_daw_mps()

    clusters, cluster_indices = dt.get_cluster_mps(mps, r_max=6.0, min_cluster_size=2)

    assert frozenset({"MOCK001", "MOCK002"}) in {frozenset(cluster) for cluster in clusters}
    assert frozenset({0, 1}) in cluster_indices
