import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import dawacotools as dw
from dawacotools.io_plenty import get_plenty_data

all_tags = dw.io_plenty.get_required_patags_for_flow()

fp = './scratch/PA flow metingen2.xlsx'

# df_plenty = get_plenty_data(fp, center_average_values=None)
# df_plenty.reset_index().to_feather(fp+".feather")
df_plenty = pd.read_feather(fp+".feather").set_index("ophaal tijdstip")

fils = dw.io.get_daw_filters(return_hpd=True)
fils = fils[fils.filternr == 0]
fils["sec_flow_tag"] = fils.locatie.apply(dw.io_plenty.mpcode_to_sec_pa_tag)
# fils.loc[fils.filternr != 0, "sec_flow_tag"] = ""
# Soort filter not correct for most pumping wells

counts = fils["sec_flow_tag"][fils["sec_flow_tag"] != ""].value_counts().to_dict()
fils["sec_nput"] = fils["sec_flow_tag"].replace(counts)

sec_flows = dw.io_plenty.get_sec_pa_flows(df_plenty)

# save unaltered version to feather
sec_flows.reset_index().to_feather("sec_flows.feather")

# alter data
sec_flows_altered = sec_flows.iloc[-10:].copy()
sec_flows_altered = sec_flows_altered + (np.random.rand(*sec_flows_altered.shape) - 0.5) * sec_flows_altered
sec_flows_altered.reset_index().to_feather("sec_flows_altered.feather")

sec_flows = sec_flows.groupby(sec_flows.index.year).mean()
sec_flows.index = "flow_" + sec_flows.index.astype(str)
fils[sec_flows.index] = np.nan


for tag, nput in counts.items():
    fils.loc[fils["sec_flow_tag"] == tag, sec_flows.index] = sec_flows[tag].values / nput

fils.to_file("pumping_infiltration_wells.geojson", driver="GeoJSON")

# altered data
import geopandas as gpd

x = fils.x + (np.random.rand(len(fils)) - 0.5) * 250
y = fils.y + (np.random.rand(len(fils)) - 0.5) * 250
del fils["x"]
del fils["y"]
fils = gpd.GeoDataFrame(fils, geometry=gpd.points_from_xy(x, y), crs="EPSG:28992")

fils[sec_flows.index] = fils[sec_flows.index] + (np.random.rand(len(fils), len(sec_flows.index)) - 0.5) * fils[sec_flows.index]
fils.to_file("pumping_infiltration_wells_altered.geojson", driver="GeoJSON")