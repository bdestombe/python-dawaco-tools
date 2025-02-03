"""Code to download data from the Ellitrack website."""

import getpass
import logging
from io import StringIO

import pandas as pd
from requests import session

try:
    usrname = input("Enter Username: ")
    passwd = getpass.getpass("Enter your password: ")
except ValueError as e:
    msg = f"Error occurred while getting input: {e}"
    logging.exception(msg)

payload = {"action": "login", "username": usrname, "password": passwd}

with session() as c:
    c.post("https://www.ellitrack.nl/auth/login", data=payload)
    response = c.get(
        "https://www.ellitrack.nl/multitracker/downloadexport/trackerid/20480/type/period/n/0/periodfrom/19-7-2020%2017%3A00/periodto/25-7-2030%2012%3A00/periodtype/date"
    )

response_s = StringIO(response.text)
df = pd.read_csv(response_s, sep="\t", index_col=0)

df.plot()
