import contextily as ctx
import matplotlib as mpl

mpl.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr

import dawacotools as dt
from dawacotools import plot as dawaco_plot


def test_plot_daw_mp_uses_filter_mpcode_column_and_triwaco_tuple_zlim(monkeypatch):
    def fake_get_daw_boring(*_args, **_kwargs):
        return pd.DataFrame()

    def fake_plot_daw_mp_map(**kwargs):
        return kwargs["ax"]

    def fake_plot_knmi_meteo(*_args, **_kwargs):
        return None

    def fake_get_daw_mon_dates(*_args, **_kwargs):
        return []

    monkeypatch.setattr(dawaco_plot, "get_daw_boring", fake_get_daw_boring)
    monkeypatch.setattr(dawaco_plot, "plot_daw_mp_map", fake_plot_daw_mp_map)
    monkeypatch.setattr(dawaco_plot, "plot_knmi_meteo", fake_plot_knmi_meteo)
    monkeypatch.setattr(dawaco_plot, "get_daw_mon_dates", fake_get_daw_mon_dates)
    gws_index = pd.date_range("2020-01-01", periods=2, freq="D")

    def fake_get_daw_ts_stijghgt(mpcode, filternr):
        assert isinstance(mpcode, str)
        assert filternr in {1, 2}
        return pd.Series([1.0, 1.1], index=gws_index, name="mNAP")

    monkeypatch.setattr(dawaco_plot, "get_daw_ts_stijghgt", fake_get_daw_ts_stijghgt)

    fig = dawaco_plot.plot_daw_mp("MOCK001", map_type="satelite")

    assert fig.axes
    plt.close(fig)


def test_plot_daw_map_gws_keys_medians_by_filter_row(monkeypatch):
    filters = dt.get_daw_filters().reset_index(drop=True)
    median_by_filter = {
        ("MOCK001", 1): 1.0,
        ("MOCK001", 2): 2.0,
        ("MOCK002", 1): 3.0,
    }

    def fake_get_daw_ts_stijghgt(mpcode, filternr):
        value = median_by_filter[(mpcode, filternr)]
        index = pd.date_range("2017-01-01", periods=12, freq="D")
        return pd.Series(np.full(index.size, value), index=index, name="mNAP")

    monkeypatch.setattr(dawaco_plot, "get_daw_ts_stijghgt", fake_get_daw_ts_stijghgt)
    fig, ax = plt.subplots()

    filtmeds, plot_ax = dawaco_plot.plot_daw_map_gws(filters, ax=ax)

    assert plot_ax is ax
    assert list(filtmeds[["MpCode", "Filtnr"]].itertuples(index=False, name=None)) == list(median_by_filter.keys())
    np.testing.assert_allclose(filtmeds["gwsmed"], list(median_by_filter.values()))
    plt.close(fig)


def test_plot_daw_mp_map_supports_point_of_interest_marker(monkeypatch):
    def fake_add_basemap(*_args, **_kwargs):
        return None

    monkeypatch.setattr(ctx, "add_basemap", fake_add_basemap)
    mps = dt.get_daw_mps()
    mps.loc["MOCK001", "Soort"] = "Point of interest"
    fig, ax = plt.subplots()
    ax.set_xlim(99990.0, 100010.0)
    ax.set_ylim(499990.0, 500010.0)

    returned_ax = dawaco_plot.plot_daw_mp_map(mpcode="MOCK001", mps=mps, ax=ax, map_type="satelite")

    assert returned_ax is ax
    plt.close(fig)


def test_plot_nlmod_k_labels_horizontal_conductivity_as_kh(monkeypatch):
    model_ds = xr.Dataset(
        data_vars={
            "idomain": (("layer", "icell2d"), np.array([[1], [1]])),
            "kh": (("layer", "icell2d"), np.array([[10.0], [5.0]])),
            "kv": (("layer", "icell2d"), np.array([[1.0], [0.5]])),
            "top": ("icell2d", np.array([2.0])),
            "botm": (("layer", "icell2d"), np.array([[0.0], [-5.0]])),
        },
        coords={
            "layer": np.array([1, 2]),
            "icell2d": np.array([0]),
            "x": ("icell2d", np.array([100000.0])),
            "y": ("icell2d", np.array([500000.0])),
        },
    )
    monkeypatch.setattr(dawaco_plot.xr, "open_dataset", lambda _path: model_ds)
    fig, ax = plt.subplots()

    dawaco_plot.plot_nlmod_k(100000.0, 500000.0, "model.nc", ax)

    assert ax.get_xlabel() == "Kh (m/dag; blauw)"
    assert fig.axes[1].get_xlabel() == "Kv (m/dag; oranje)"
    plt.close(fig)
