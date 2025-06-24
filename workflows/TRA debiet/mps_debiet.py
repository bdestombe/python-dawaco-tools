import os

import geopandas as gpd
import numpy as np
import pandas as pd

import dawacotools as dw

all_tags = dw.io_plenty.get_required_patags_for_flow()

fp = "workflows/TRA debiet/data/20240209 - Debieten.xlsx"
output_dir = os.path.join(__file__, "..", "output")

df_plenty = dw.io_plenty.get_plenty_data(fp, center_average_values=None)
# df_plenty.reset_index().to_feather(fp+".feather")
df_plenty = pd.read_feather(fp + ".feather").set_index("ophaal tijdstip")

fils = dw.io.get_daw_filters(return_hpd=True)
fils = fils[fils.filternr == 0]
fils["sec_flow_tag"] = fils.locatie.apply(dw.io_plenty.mpcode_to_sec_pa_tag)
# fils.loc[fils.filternr != 0, "sec_flow_tag"] = ""
# Soort filter not correct for most pumping wells

counts = fils["sec_flow_tag"][fils["sec_flow_tag"] != ""].value_counts().to_dict()
fils["sec_nput"] = fils["sec_flow_tag"].replace(counts)

sec_flows = dw.io_plenty.get_sec_pa_flows(df_plenty)

# save unaltered version to feather
fp = os.path.join(output_dir, "sec_flows.feather")
sec_flows.reset_index().to_feather(fp)

# alter data
sec_flows_altered = sec_flows.iloc[-10:].copy()
sec_flows_altered += (np.random.rand(*sec_flows_altered.shape) - 0.5) * sec_flows_altered
fp = os.path.join(output_dir, "sec_flows_altered.feather")
sec_flows_altered.reset_index().to_feather(fp)

sec_flows_year = sec_flows.groupby(sec_flows.index.year).mean()
sec_flows_year.index = "flow_" + sec_flows_year.index.astype(str)
fils[sec_flows_year.index] = np.nan


for tag, nput in counts.items():
    fils.loc[fils["sec_flow_tag"] == tag, sec_flows_year.index] = sec_flows_year[tag].values / nput
fp = os.path.join(output_dir, "pumping_infiltration_wells.geojson")
fils.to_file(fp, driver="GeoJSON")

# altered data
x = fils.x + (np.random.rand(len(fils)) - 0.5) * 250
y = fils.y + (np.random.rand(len(fils)) - 0.5) * 250
del fils["x"]
del fils["y"]
fils = gpd.GeoDataFrame(fils, geometry=gpd.points_from_xy(x, y), crs="EPSG:28992")

fils[sec_flows_year.index] += (np.random.rand(len(fils), len(sec_flows_year.index)) - 0.5) * fils[sec_flows_year.index]
fp = os.path.join(output_dir, "pumping_infiltration_wells_altered.geojson")
fils.to_file(fp, driver="GeoJSON")
