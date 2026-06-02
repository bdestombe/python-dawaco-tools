"""Analysis functions for processing groundwater data from DAWACO database."""

import numpy as np
import pandas as pd
from scipy import integrate, interpolate

from dawacotools.io import (
    get_daw_boring,
    get_daw_filters,
    get_daw_meteo_from_loc,
    get_daw_triwaco,
    get_daw_ts_stijghgt,
    get_daw_ts_temp,
    get_regis_ds,
    meteo_pars,
)


def remove_outliers(data: pd.Series, threshold: float = 3.0) -> pd.Series:
    """Remove outliers from a pandas.Series.

    Outliers are defined as values that are more than threshold standard deviations away from the mean.

    Parameters
    ----------
    data : pandas.Series
        The data to remove outliers from.
    threshold : float, optional
        The threshold in standard deviations. Default is 3.0.

    Returns
    -------
    pandas.Series
        The data with outliers as nan
    """
    outlier_mask = np.abs(data - data.mean()) < threshold * data.std()
    return data.where(outlier_mask, other=np.nan, inplace=False)


def compute_residence_time(
    flow: pd.Series,
    pore_volume_reservoir: float | None = None,
    average_residence_time: float | None = None,
    extraction_infiltration: str = "extraction",
    retardation_factor: float = 1.0,
) -> pd.Series:
    """Compute the residence time of the water extracted from a plug-flow reservoir.

    The residence time is computed from historic flow rates through a reservoir of a given volume. The
    cumulative transported volume is derived from elapsed days in ``flow.index``; therefore ``flow`` values
    must be volumetric rates per day (for example m³/day). Convert rates in other time units before calling
    this function, e.g. multiply m³/hour by 24.

    IKIEF 9100:
    >> pore_volume_reservoir = 2 * lengte_strang * afstand_pand_put / porositeit
    >> 128571 m3 = 2 * 500 * 45 / 0.35

    Parameters
    ----------
    flow : pandas.Series
        Volumetric flow rate through the reservoir in m³/day. The index must be a strictly increasing
        pandas.DatetimeIndex; flow is linearly interpolated between timestamps and integrated over elapsed days.
    pore_volume_reservoir : float, optional
        The pore volume of the reservoir in the same volume unit as ``flow``. Provide either this value or
        ``average_residence_time``.
    average_residence_time : float, optional
        The average residence time in days. If no ``pore_volume_reservoir`` is given, the pore volume is computed
        as the product of the average residence time and the time-weighted mean flow.
    extraction_infiltration : str, optional
        The type of flow. Either 'extraction' or 'infiltration'. Extraction refers to backward modeling: how many
        days ago did this extracted water infiltrate. Infiltration refers to forward modeling: how many days will it
        take for this infiltrated water to be extracted.
        Default is 'extraction'.
    retardation_factor : float, optional
        Multiplicative factor for solute retardation relative to water movement. Default is 1.

    Returns
    -------
    pandas.Series
        The residence time in days.
    """
    if pore_volume_reservoir is None and average_residence_time is None:
        msg = "Provide either pore_volume_reservoir or average_residence_time"
        raise ValueError(msg)

    if not isinstance(flow.index, pd.DatetimeIndex):
        msg = "flow must be indexed by a pandas.DatetimeIndex"
        raise TypeError(msg)

    minimum_timestamps = 2
    if len(flow.index) < minimum_timestamps:
        msg = "flow must contain at least two timestamps"
        raise ValueError(msg)

    elapsed_days = ((flow.index - flow.index[0]) / pd.to_timedelta(1, unit="D")).to_numpy(dtype=float)
    if not np.all(np.diff(elapsed_days) > 0.0):
        msg = "flow.index must be strictly increasing"
        raise ValueError(msg)

    flow_values = flow.to_numpy(dtype=float)
    cum_flow_val = integrate.cumulative_trapezoid(y=flow_values, x=elapsed_days, initial=0.0)

    if not np.all(np.diff(cum_flow_val) > 0.0):
        msg = "Cumulative flow must be strictly increasing; use positive flow rates through the reservoir"
        raise ValueError(msg)

    if pore_volume_reservoir is None:
        if average_residence_time is None:
            msg = "Provide either pore_volume_reservoir or average_residence_time"
            raise ValueError(msg)
        mean_flow = cum_flow_val[-1] / elapsed_days[-1]
        pore_volume = average_residence_time * mean_flow
    else:
        pore_volume = pore_volume_reservoir

    transport_volume = pore_volume * retardation_factor
    elapsed_at_cumulative_flow = interpolate.interp1d(
        cum_flow_val,
        elapsed_days,
        fill_value="extrapolate",
        assume_sorted=True,
    )

    if extraction_infiltration == "extraction":
        infiltration_time = elapsed_at_cumulative_flow(cum_flow_val - transport_volume)
        residence_time = elapsed_days - infiltration_time
    elif extraction_infiltration == "infiltration":
        extraction_time = elapsed_at_cumulative_flow(cum_flow_val + transport_volume)
        residence_time = extraction_time - elapsed_days
    else:
        msg = "extraction_infiltration should be 'extraction' or 'infiltration'"
        raise ValueError(msg)

    return pd.Series(residence_time, index=flow.index)


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
    """
    Calculate groundwater flow between two monitoring points.

    Parameters
    ----------
    mpcode1 : str, optional
        Monitoring point code for first location.
    mpcode2 : str, optional
        Monitoring point code for second location.
    filternr1 : int, optional
        Filter number for first location.
    filternr2 : int, optional
        Filter number for second location.
    dh1 : float, optional
        Water level relative to reference point for first location.
    dh2 : float, optional
        Water level relative to reference point for second location.
    hydraulic_conductivity : float, optional
        Hydraulic conductivity in m/day.
    porosity : float, default 0.35
        Porosity of the aquifer material.

    Returns
    -------
    dict
        Dictionary containing distance, gradient, and optionally specific_discharge,
        poreflow_velocity, and duration.
    """
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
    """
    Retrieve comprehensive information for a monitoring well.

    Parameters
    ----------
    mpcode : str, optional
        Monitoring point code.
    filternr : int, optional
        Filter number.

    Returns
    -------
    dict
        Dictionary containing filter metadata, groundwater levels, temperature,
        meteorological data, geological information from Triwaco and boring logs,
        and REGIS subsurface model data.
    """
    # mpcode='19CZL5302'
    # filternr=2

    out = {}

    """Filter and MP data"""
    out["filter_metadata"] = get_daw_filters(
        mpcode=mpcode,
        filternr=filternr,
        partial_match_mpcode=True,
    )
    if len(out["filter_metadata"]) != 1:
        msg = "Better specify mpcode and filter number"
        raise ValueError(msg)

    filter_metadata = out["filter_metadata"].iloc[0]
    mpcode = filter_metadata["MpCode"]
    filternr = filter_metadata["Filtnr"]
    x, y = filter_metadata["Xcoor"], filter_metadata["Ycoor"]

    """Groundwater levels"""
    out["gws"] = get_daw_ts_stijghgt(mpcode=mpcode, filternr=filternr)

    """Groundwater temperature"""
    out["gwt"] = get_daw_ts_temp(mpcode=mpcode, filternr=filternr)

    """Meteo"""
    for k in meteo_pars:
        out[k], _ = get_daw_meteo_from_loc(
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


def get_cluster_mps(mps, r_max=1.5, min_cluster_size=2):
    """
    Cluster all monitoring points within a certain distance of each other.

    Parameters
    ----------
    mps : pandas.DataFrame
        Monitoring points, retrieved from the DAWACO database.
    r_max : float
        Maximum distance between monitoring points.
    min_cluster_size : int
        Minimum number of monitoring points in a cluster.

    Returns
    -------
    list
        List of tuples containing the monitoring points within a certain distance of each other.
    """
    x = mps.geometry.x.values
    y = mps.geometry.y.values

    dx = x[:, None] - x
    dy = y[:, None] - y

    dist = np.sqrt(dx**2 + dy**2)

    # Find all points within r_max
    i, j = np.where(dist < r_max)
    collections = {i: [] for i in range(len(x))}
    for ii, jj in zip(i, j, strict=False):
        collections[ii].append(jj)

    # get unique collections larger than 1
    unique_collection_indices = {frozenset(c) for c in collections.values() if len(c) >= min_cluster_size}
    unique_collections = [tuple(mps.index[xx] for xx in x) for x in unique_collection_indices]
    return unique_collections, unique_collection_indices
