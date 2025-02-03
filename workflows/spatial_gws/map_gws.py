import os

import geopandas as gpd
import numpy as np
import pandas as pd
import pastastore as pst
from pastas import stats as pst_stats

# Load the data from the localdb
dbname = "20250127_dawaco_db"
dbtype = "arctic"

# open the store
if dbtype == "pystore":
    fd = os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..", "localdb", "data"))
    conn = pst.PystoreConnector("dawaco_db", path=fd)
elif dbtype == "arctic":
    uri = "lmdb://" + os.path.relpath(os.path.join(os.path.abspath(__file__), "..", "..", "localdb", "data", dbname))
    conn = pst.ArcticDBConnector("my_db", uri)
else:
    raise ValueError("dbtype should be 'pystore' or 'arctic'")

store = pst.PastaStore(name="dawaco_db", connector=conn)
print("store opened")

# get metadata from all observation series oseries groundwaterlevels
names = store.conn.oseries_names

# which statistics to calculate
# - for the periods: [aug '18 - jul '19, aug '19 - jul '20, aug '20 - jul '21, aug '21 - jul '22, aug '22 - jul '23, aug '23 - jul '24, aug '18 - jul '24]
# - mean
# - std
# - median
# - min
# - date min
# - max
# - date max
# - 5th percentile
# - 95th percentile
# - 97.5th percentile
# - 99th percentile
# https://github.com/pastas/pastas/blob/dev/pastas/stats/dutch.py#L367


def get_arnoud_inundation(series, date="2024-03-04", cutoff_days=7):
    s = series.copy()

    # get water level close to the date of the inundation map
    date = pd.Timestamp(date)
    dt = np.abs(s.index - date)

    # sort values
    s[dt > pd.Timedelta(cutoff_days, unit="D")] = pd.NA
    s = s.iloc[dt.argsort()]

    return s.iloc[0]


def get_statistics(series):
    stats = {
        "len": len(series),
        "mean": series.mean(),
        "std": series.std(),
        "median": series.median(),
        "min": series.min(),
        "max": series.max(),
        "p5": series.quantile(0.05),
        "p95": series.quantile(0.95),
        "p975": series.quantile(0.975),
        "p99": series.quantile(0.99),
        "q_ghg": pst_stats.q_ghg(series),
        "q_glg": pst_stats.q_glg(series),
        "q_gvg": pst_stats.q_gvg(series),
        "ghg": pst_stats.ghg(series),
        "glg": pst_stats.glg(series),
        "gvg": pst_stats.gvg(series),
        # "gg": pst_stats.gg(series),
    }
    if series.notna().any():
        stats["mindate"] = series.idxmin()
        stats["maxdate"] = series.idxmax()
    else:
        stats["mindate"] = pd.NaT
        stats["maxdate"] = pd.NaT

    return stats


# for each observation series, calculate the statistics
periods = [
    ("1993-01-01", "1993-12-31"),
    ("1994-01-01", "1994-12-31"),
    ("1995-01-01", "1995-12-31"),
    ("2023-01-01", "2023-12-31"),
    ("2024-01-01", "2024-12-31"),
    ("2018-08-01", "2019-07-31"),
    ("2019-08-01", "2020-07-31"),
    ("2020-08-01", "2021-07-31"),
    ("2021-08-01", "2022-07-31"),
    ("2022-08-01", "2023-07-31"),
    ("2023-08-01", "2024-07-31"),
    ("2024-08-01", "2025-07-31"),
    ("2018-08-01", "2025-07-31"),
    ("1900-01-01", "2025-07-31"),  # all data
]

out = store.oseries.copy()
out.drop(columns="name", inplace=True)

for name in names:
    print(name)
    obs = store.conn.get_oseries(name)
    for start, stop in periods:
        per_label = f"{start.replace('-', '')[:6]}{stop.replace('-', '')[:6]}"

        try:
            stats = get_statistics(obs.loc[start:stop])
        except:
            stats = {
                k: pd.NA
                for k in [
                    "len",
                    "mean",
                    "std",
                    "median",
                    "min",
                    "max",
                    "p5",
                    "p95",
                    "p975",
                    "p99",
                    "mindate",
                    "maxdate",
                    "q_ghg",
                    "q_glg",
                    "q_gvg",
                    "ghg",
                    "glg",
                    "gvg",
                ]
            }

        stats = {f"{per_label}_{k}": v for k, v in stats.items()}
        for k, v in stats.items():
            out.loc[name, k] = v

    out.loc[name, "202403_inundation"] = get_arnoud_inundation(obs, date="2024-03-04", cutoff_days=7)

geo_out = gpd.GeoDataFrame(out, geometry=gpd.points_from_xy(out.x, out.y), crs="EPSG:28992")
geo_out.to_file("output.geojson", driver="GeoJSON")
geo_out.to_file("output.gpkg", driver="GPKG")
