"""Dawacotools package for working with the DAWACO database."""

# Analysis functions
from .analysis import (
    compute_residence_time,
    get_cluster_mps,
    get_well_info,
    potential_to_flow,
    remove_outliers,
)

# Color schemes and legends
from .colors import boorlegenda_dawaco, regis_colors, tno_colors

# Core I/O functions
from .io import (
    connection_string,
    connection_url,
    dbname,
    df2gdf,
    dw_df_to_hpd,
    engine,
    fuzzy_match_mpcode,
    get_daw_boring,
    get_daw_coords_from_mpcode,
    get_daw_filters,
    get_daw_meteo_arr_daterange,
    get_daw_meteo_from_loc,
    get_daw_mon_dates,
    get_daw_mps,
    get_daw_soort_mp,
    get_daw_triwaco,
    get_daw_ts_meteo,
    get_daw_ts_stijghgt,
    get_daw_ts_temp,
    get_hpd_gws_obs,
    get_knmi_station_meta,
    get_nlmod_index_nearest_cell,
    get_nlmod_vertical_profile,
    get_regis_ds,
    identify_data_gaps,
    meteo_arr,
    meteo_header,
    meteo_pars,
)

# Plenty system I/O functions
from .io_plenty import (
    get_flow,
    get_flows,
    get_nput,
    get_nput_dict,
    get_plenty_data,
    get_required_patags_for_flow,
    get_sec_pa,
    get_sec_pa_flows,
    get_tra_flows,
    ispomp_filter,
    mpcode_to_sec_pa_flow,
    mpcode_to_sec_pa_tag,
    secs_pa_flow,
    secs_pa_fun,
    tra_alias,
)

# Plotting functions
from .plot import (
    plot_daw_boring,
    plot_daw_filters,
    plot_daw_map_gws,
    plot_daw_mp,
    plot_daw_mp_map,
    plot_daw_triwaco,
    plot_knmi_meteo,
    plot_nlmod_k,
    plot_nlmod_vertical_profile,
    plot_regis_kh,
    plot_regis_kv,
    plot_regis_lay,
)