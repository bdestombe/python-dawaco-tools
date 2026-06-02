import numpy as np
import pandas as pd
import pytest

from dawacotools import io_plenty


@pytest.mark.parametrize(
    ("tag", "start", "end"),
    [
        ("CAWP02", "2016-01-01", "2019-01-01"),
        ("CAWP05", "2016-02-01", "2018-01-01"),
        ("CAWQ01", "2012-01-01", "2013-01-01"),
        ("HEW906", "2016-01-01", "2018-01-01"),
        ("HEWPAF", "2012-01-01", "2013-01-01"),
        ("BEWARU", "2004-01-01", "2005-01-01"),
        ("BEWBRU", "2016-01-01", "2018-01-01"),
    ],
)
def test_sec_pa_flow_date_masks_use_totalizer_only_inside_affected_interval(tag, start, end):
    start = pd.Timestamp(start)
    end = pd.Timestamp(end)
    index = pd.DatetimeIndex([start - pd.Timedelta(days=1), start, end])
    data = {
        f"{tag}_FQ10R": 1.0,
        f"{tag}_FT10": 100.0,
    }
    if tag in {"CAWP02", "CAWP05", "CAWQ01", "HEW906"}:
        data[f"{tag}_FQ11R"] = 10.0
        expected = np.array([-44.0, -140.0, -44.0])
    else:
        expected = np.array([-4.0, -100.0, -4.0])
    df_plenty = pd.DataFrame(data, index=index)

    actual = df_plenty.eval(io_plenty.secs_pa_flow[tag]).to_numpy()

    np.testing.assert_allclose(actual, expected)


@pytest.mark.parametrize("flow_func", [io_plenty.get_flow, io_plenty.get_flows])
def test_get_flow_returns_1d_array_for_all_pump_metadata(flow_func):
    metadata = pd.DataFrame(
        {
            "MpCode": ["19CNPCP 1", "19CNPCP 3"],
            "Filtnr": [0, 0],
        },
    )
    df_plenty = pd.DataFrame(
        {
            "CAWP01_FQ10R": [1.0],
            "CAWP01_FQ11R": [2.0],
            "CAWP03_FQ10R": [3.0],
            "CAWP03_FQ11R": [4.0],
        },
        index=pd.DatetimeIndex(["2020-01-01"]),
    )

    flow = flow_func(metadata, df_plenty)

    assert flow.shape == (2,)
    np.testing.assert_allclose(flow, [-12.0, -28.0])


@pytest.mark.parametrize("flow_func", [io_plenty.get_flow, io_plenty.get_flows])
def test_get_flow_returns_1d_array_for_mixed_pump_and_non_pump_metadata(flow_func):
    metadata = pd.DataFrame(
        {
            "MpCode": ["19CNPCP 1", "OBS001"],
            "Filtnr": [0, 1],
        },
    )
    df_plenty = pd.DataFrame(
        {
            "CAWP01_FQ10R": [1.0],
            "CAWP01_FQ11R": [2.0],
        },
        index=pd.DatetimeIndex(["2020-01-01"]),
    )

    flow = flow_func(metadata, df_plenty)

    assert flow.shape == (2,)
    np.testing.assert_allclose(flow, [-12.0, np.nan], equal_nan=True)
