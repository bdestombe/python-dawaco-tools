"""Code to download data from the Ellitrack website."""

import getpass
import logging
from io import StringIO

import numpy as np
import pandas as pd
from requests import session

try:
    usrname = input("Enter Username: ")
    passwd = getpass.getpass("Enter your password: ")
except ValueError as e:
    msg = f"Error occurred while getting input: {e}"
    logging.exception(msg)

payload = {"action": "login", "username": usrname, "password": passwd}

# Hoorn
years = np.arange(2019, 2026)
keys = {
    "19FNL014-1 kelder 3": 26859,
    "19FNL015-1 kelder 3": 26857,
    "19FNL016-1 kelder 3": 26861,
    "19FNL017-1 kelder 3": 26858,
}
out = {}
for k, id in keys.items():
    out_years = []
    for year in years:
        with session() as c:
            c.post("https://www.ellitrack.nl/auth/login", data=payload)
            response = c.get(
                f"https://www.ellitrack.nl/multitracker/downloadexport/trackerid/{id}/type/period/n/0/periodfrom/1-1-{year}%2015%3A00/periodto/31-12-{year}%2015%3A00/periodtype/date"
            )

        response_s = StringIO(response.text)
        df = pd.read_csv(response_s, sep="\t", index_col=0)
        out_years.append(df)
    out[k] = pd.concat(out_years)["Waterstand"]


def merge_series_named(series_dict):
    all_indices = sorted(set().union(*[s.index for s in series_dict.values()]))
    result = pd.DataFrame(index=all_indices)

    for name, series in series_dict.items():
        result[name] = series.reindex(all_indices)

    return result


out2 = merge_series_named(out)
out2.set_index(pd.to_datetime(out2.index), inplace=True)
