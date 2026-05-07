import geopandas as gpd
import pandas as pd

from dawacotools.io import get_daw_filters, get_daw_mps, get_daw_ts_stijghgt

fp = "output3.geojson"
gdf = gpd.read_file(fp)

icas_pref_tags = "19CNPCQ", "19CNPCP"
ikief_pref_tags = "19CZPM9", "19CZPM10"
pref_tags = icas_pref_tags + ikief_pref_tags

gws_ts = {}
gws_mean = {}
gws_mean_pref = {}

for pref in pref_tags:
    mps = get_daw_mps(mpcode=pref, partial_match_mpcode=True)

    gws_ts[pref] = {}
    gws_mean_pref[pref] = {}

    for mpcode, mpdata in mps.iterrows():
        # gws_ts[pref][mpcode] = get_daw_ts_stijghgt(mpcode=mpcode, filternr=mpdata["Aant_Fil"] - 1)
        # gws_mean_pref[pref][mpcode] = float(gws_ts[mpcode].mean())
        name = f"{mpcode}-{mpdata["Aant_Fil"]-1:03d}"
        gws_mean_pref[pref][mpcode] = gdf.loc[gdf.name == name, '190001202507_median']

    gws_mean[pref] = pd.concat(gws_mean_pref[pref]).median()