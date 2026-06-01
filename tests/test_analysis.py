import numpy as np
import pandas as pd

import dawacotools as dt


def test_remove_outliers_replaces_values_outside_threshold():
    series = pd.Series([1.0, 1.1, 0.9, 10.0])

    result = dt.analysis.remove_outliers(series, threshold=1.0)

    assert np.isnan(result.iloc[-1])
    assert result.iloc[:3].notna().all()


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


def test_get_cluster_mps_finds_nearby_monitoring_points():
    mps = dt.get_daw_mps()

    clusters, cluster_indices = dt.get_cluster_mps(mps, r_max=6.0, min_cluster_size=2)

    assert frozenset({"MOCK001", "MOCK002"}) in {frozenset(cluster) for cluster in clusters}
    assert frozenset({0, 1}) in cluster_indices
