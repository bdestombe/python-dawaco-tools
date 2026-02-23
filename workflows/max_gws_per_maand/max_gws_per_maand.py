import numpy as np
import pandas as pd
from scipy.interpolate import UnivariateSpline
import matplotlib.pyplot as plt

from dawacotools.io import get_daw_ts_stijghgt

mps = {
    "12_1": ("09BZW012", 1),
    "12_2": ("09BZW012", 2),
    "14_1": ("09BZW014", 1),
}
h_level = 0.55  # mNAP
hh_level = 0.35  # mNAP

gwss = {}
for key, (mpcode, filternr) in mps.items():
    gwss[key] = get_daw_ts_stijghgt(mpcode=mpcode, filternr=filternr)

gw = gwss["12_2"].resample("D").median()

gw = gw.interpolate(method="time")["2011-02-01":]

fig, ax = plt.subplots(figsize=(12, 6))
ax.axhspan(ymin=h_level, ymax=hh_level, color="orange", alpha=0.4)
ax.axhspan(ymin=hh_level, ymax=gw.max(), color="red", alpha=0.4)
gw.plot(ax=ax)

# Forward-looking 14-day rolling max: max of the next 14 days stored at the index
gw_construction = gw[::-1].rolling(window=14, min_periods=1).max()[::-1]

# Percentage of days where gw_construction exceeds h_level, grouped by month
pct_above_h = (gw_construction > h_level).groupby(gw_construction.index.month).mean() * 100
pct_above_h = (pct_above_h / 5).round() * 5

# Dutch month names as index
dutch_months = [
    "januari", "februari", "maart", "april", "mei", "juni",
    "juli", "augustus", "september", "oktober", "november", "december",
]
pct_above_h.index = [dutch_months[m - 1] for m in pct_above_h.index]

# Print as tab-separated table for easy copy-paste into Outlook
print("Maand\tKans (%)")
for month, pct in pct_above_h.items():
    print(f"{month}\t{pct:.0f}%")

    