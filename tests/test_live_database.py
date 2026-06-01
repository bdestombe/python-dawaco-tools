import os

import pytest

import dawacotools as dt


@pytest.mark.live_db
def test_live_database_returns_configured_monitoring_point():
    mpcode = os.environ.get("DAWACOTOOLS_LIVE_MPCODE")
    if not mpcode:
        pytest.skip("set DAWACOTOOLS_LIVE_MPCODE to run this live smoke test")

    mps = dt.get_daw_mps(mpcode=mpcode, partial_match_mpcode=False)

    assert list(mps.index) == [mpcode]


@pytest.mark.live_db
def test_live_database_returns_configured_filter():
    mpcode = os.environ.get("DAWACOTOOLS_LIVE_MPCODE")
    filternr = os.environ.get("DAWACOTOOLS_LIVE_FILTER")
    if not mpcode or not filternr:
        pytest.skip("set DAWACOTOOLS_LIVE_MPCODE and DAWACOTOOLS_LIVE_FILTER to run this live smoke test")

    filters = dt.get_daw_filters(mpcode=mpcode, filternr=filternr, partial_match_mpcode=False)

    assert len(filters) == 1
    assert filters.iloc[0]["MpCode"] == mpcode
    assert str(filters.iloc[0]["Filtnr"]) == filternr
