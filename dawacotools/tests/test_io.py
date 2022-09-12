import dawacotools as dt


def test_get_daw_mps():
    mps = dt.get_daw_mps()
    assert len(mps) > 5000

    mps = dt.get_daw_mps(mpcode="09BZW012")
    assert len(mps) == 1

    mps = dt.get_daw_mps(mpcode="09BZW01", partial_match_mpcode=False)
    assert len(mps) == 0

    mps = dt.get_daw_mps(mpcode="09BZW01", partial_match_mpcode=True)
    assert len(mps) > 0

    mps = dt.get_daw_mps(mpcode=["09BZW012", "09BZW013"])
    assert len(mps) == 2

    mps = dt.get_daw_mps(mpcode=["09BZW01"], partial_match_mpcode=False)
    assert len(mps) == 0

    mps = dt.get_daw_mps(mpcode=["09BZW01"], partial_match_mpcode=True)
    assert len(mps) > 0
    pass


def test_get_daw_filters():
    mps = dt.get_daw_filters(mpcode="09BZW012")
    assert len(mps) == 2

    mps = dt.get_daw_filters(mpcode="09BZW012", filternr=1)
    assert len(mps) == 1

    mps = dt.get_daw_filters(mpcode="09BZW012", filternr="1")
    assert len(mps) == 1

    mps = dt.get_daw_filters(mpcode="09BZW012", filternr=[1.0, 2.0])
    assert len(mps) == 2

    mps = dt.get_daw_filters(mpcode="09BZW01", partial_match_mpcode=False)
    assert len(mps) == 0

    mps = dt.get_daw_filters(mpcode="09BZW01", partial_match_mpcode=True)
    assert len(mps) > 0

    mps = dt.get_daw_filters(mpcode=["09BZW012", "09BZW013"])
    assert len(mps) == 4

    mps = dt.get_daw_filters(mpcode=["09BZW01"], partial_match_mpcode=False)
    assert len(mps) == 0

    mps = dt.get_daw_filters(mpcode=["09BZW01"], partial_match_mpcode=True)
    assert len(mps) > 0
    pass
