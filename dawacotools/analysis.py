import numpy as np
import pandas as pd

from .io import get_daw_filters
from .io import get_daw_ts_stijghgt
from .io import get_daw_ts_temp
from .io import get_daw_triwaco
from .io import get_daw_boring
from .io import get_regis_ds


def potential_to_flow(
    mpcode1=None,
    mpcode2=None,
    filternr1=None,
    filternr2=None,
    dh1=None,
    dh2=None,
    hydraulic_conductivity=None,
    porosity=0.35,
):
    meta1 = get_daw_filters(mpcode=mpcode1, filternr=filternr1)
    meta2 = get_daw_filters(mpcode=mpcode2, filternr=filternr2)

    if dh1 is None:
        h1 = get_daw_ts_stijghgt(mpcode=mpcode1, filternr=filternr1)
    else:
        h1 = pd.Series(data=meta1.Refpunt.item() - dh1)

    if dh2 is None:
        h2 = get_daw_ts_stijghgt(mpcode=mpcode2, filternr=filternr2)
    else:
        h2 = pd.Series(data=meta2.Refpunt.item() - dh2)

    # resample. nearest neighbor for extrapolation. Use longest ts to interp to.
    if len(h1) == 1 and len(h2) == 1:
        h1res, h2res = h1, h2

    elif len(h1) > len(h2):
        h1res = h1
        h2res_array = np.interp(h1.index, h2.index, h2.values)
        h2res_array[h1.index < h2.index[0]] = h2.values[0]
        h2res_array[h1.index > h2.index[-1]] = h2.values[-1]
        h2res = pd.Series(index=h1.index, data=h2res_array)

    else:
        h1res_array = np.interp(h2.index, h1.index, h1.values)
        h1res_array[h2.index < h1.index[0]] = h1.values[0]
        h1res_array[h2.index > h1.index[-1]] = h1.values[-1]
        h1res = pd.Series(index=h2.index, data=h1res_array)
        h2res = h2

    # compute
    out = {"distance": meta1.distance(meta2.iloc[0].geometry).values}
    out["gradient"] = (h1res - h2res) / out["distance"]  # m/m

    if hydraulic_conductivity is not None:
        out["specific_discharge"] = hydraulic_conductivity * out["gradient"]  # m/day

        if porosity is not None:
            out["poreflow_velocity"] = out["specific_discharge"] / porosity  # m/day
            out["duration"] = out["distance"] / out["poreflow_velocity"]  # day

    return out


def get_well_info(mpcode=None, filternr=None):
    from .io import meteo_pars

    # mpcode='19CZL5302'
    # filternr=2

    out = {}

    """Filter and MP data"""
    out["filter_metadata"] = get_daw_filters(
        mpcode=mpcode,
        mv=True,
        betrouwbaarheid=False,
        filternr=filternr,
        partial_match_mpcode=True,
    )
    assert len(out["filter_metadata"]) == 1, "Better specify mpcode and filter number"

    mpcode = out["filter_metadata"].iloc[0].FiltMpCode
    filternr = out["filter_metadata"].iloc[0].Filtnr
    x, y = out["filter_metadata"].iloc[0].Xcoor, out["filter_metadata"].iloc[0].Ycoor

    """Groundwater levels"""
    out["gws"] = get_daw_ts_stijghgt(mpcode=mpcode, filternr=filternr)

    """Groundwater temperature"""
    out["gwt"] = get_daw_ts_temp(mpcode=mpcode, filternr=filternr)

    """Meteo"""
    for k in meteo_pars:
        out[k], _ = get_meteo_from_loc(
            x=x,
            y=y,
            mettype=k,
            start_date=out["gws"].index[0],
            end_date=out["gws"].index[-1],
        )

    """Geology"""
    out["triwaco"] = get_daw_triwaco(mpcode=mpcode)
    out["boring"] = get_daw_boring(mpcode=mpcode)
    out["regis"] = get_regis_ds(x, y, keys=None)

    return out
