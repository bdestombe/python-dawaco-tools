import pandas as pd
import io
from collections import defaultdict
import zipfile
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import requests
from lxml import html

def get_neerslag_reeksen():
    # URL of the webpage
    url = "https://www.knmi.nl/nederland-nu/klimatologie/monv/reeksen"

    # Send a request to the webpage
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse the content of the webpage
    tree = html.fromstring(response.content)
    
    # Use XPath to find all links that end with '.zip'
    zip_links = tree.xpath('//a[contains(@href, ".zip")]/@href')
    zip_filenames = tree.xpath('//a[contains(@href, ".zip")]/text()')

    # Add scheme to relative URLs
    zip_links = [f"https:{link}" for link in zip_links]
    
    # return dictionary with filenames and links
    return dict(zip(zip_filenames, zip_links))

def get_uurgegevens_links():
    # URL of the webpage
    url = "https://www.knmi.nl/nederland-nu/klimatologie/uurgegevens"

    # Send a request to the webpage
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Parse the content of the webpage
    tree = html.fromstring(response.content)
    
    # Use XPath to find all links that end with '.zip'
    zip_links = tree.xpath('//a[contains(@href, ".zip")]/@href')[3:]
    zip_links = [l for l in zip_links if l != '//cdn.knmi.nl/knmi/map/page/klimatologie/gegevens/uurgegevens/uurgeg_251_-.zip']
    # Add scheme to relative URLs
    zip_links = [f"https:{link}" for link in zip_links]

    zip_filenames = [l.split("/")[-1] for l in zip_links]
    station_number = [int(l[7:10]) for l in zip_filenames]
    dates = [l[11:-4] for l in zip_filenames]

    grouped = defaultdict(list)
    for station, date, filename, link in zip(station_number, dates, zip_filenames, zip_links):
        grouped[station].append((date, filename, link))

    # return dictionary with filenames and links
    return grouped

def get_uurgegevens(station_number: int) -> pd.Series:
    # Get the links for the station
    links = get_uurgegevens_links()[station_number]

    # Download the ZIP file
    response = requests.get(links[0][2], params={'download': 'zip'})
    response.raise_for_status()  # Raise an error for bad responses

    # Use BytesIO to treat the content as a file-like object
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        with zip_ref.open(zip_ref.namelist()[0]) as my_file:
            _df = pd.read_csv(my_file, sep=",", skiprows=1, index_col=1, parse_dates=True, na_values=["     "])

    # Strip leading and trailing nan values
    _df = _df.loc[_df["RH"].first_valid_index():_df["RH"].last_valid_index()]

    return _df

# Function to download a ZIP file and read a specified file into a pandas DataFrame
def download_and_read_zip(zip_url):
    # Download the ZIP file
    response = requests.get(zip_url, params={'download': 'zip'})
    response.raise_for_status()  # Raise an error for bad responses

    # Use BytesIO to treat the content as a file-like object
    with zipfile.ZipFile(io.BytesIO(response.content)) as zip_ref:
        with zip_ref.open(zip_ref.namelist()[0]) as my_file:
            _df = pd.read_csv(my_file, sep=",", skiprows=23, index_col=1, parse_dates=True, na_values=["     "])

    # Strip leading and trailing nan values
    _df = _df.loc[_df["   RD"].first_valid_index():_df["   RD"].last_valid_index()]

    return pd.Series(_df["   RD"].values / 10., index=_df.index.values)


stations = ["Bergen Nh", "Castricum", "De Bilt"]
urls = {station: get_neerslag_reeksen()[station] for station in stations}
dfs = {station: download_and_read_zip(url) for station, url in urls.items()}
start_dates = {station: df.first_valid_index() for station, df in dfs.items()}
df = pd.DataFrame(dfs)[max(start_dates.values()):]
dfy = df.resample("YE").sum()[1:-1]

# Perform linear regression for each station using scipy
from scipy.stats import linregress
import numpy as np

# Create a DataFrame to store the results
results = pd.DataFrame(index=["slope", "intercept", "rvalue", "pvalue", "stderr"], columns=stations)

# Perform linear regression for each station
for station in stations:
    x = np.arange(len(dfy[station]))
    y = dfy[station].values
    slope, intercept, rvalue, pvalue, stderr = linregress(x, y)
    results[station] = [slope, intercept, rvalue, pvalue, stderr]

# Add regression lines to dataframe
dfs_regres = {station: results[station]["slope"] * np.arange(len(dfy[station])) + results[station]["intercept"] for station in stations}

# Plot the results
# plt.style.use('unhcrpyplotstyle')

fig, ax = plt.subplots(figsize=(10, 6))
for i, station in enumerate(stations):
    ax.plot(dfy[station].index, dfy[station], label=station, color=f"C{i}")
    ax.plot(dfy[station].index, dfs_regres[station], label=None, linestyle="--", color=f"C{i}")

# 100 jaar neerslag toename
increase = results.loc["slope"] * 100 / results.loc["intercept"]

# Add title and legend
ax.set_title("Toename in afgelopen 100 jaar: van 700 naar 1000 mm/jaar")
ax.legend()
ax.set_ylabel("Jaarlijkse neerslag (mm)")
ax.xaxis.set_minor_locator(AutoMinorLocator())
ax.set_yticks(range(100, 2000, 100))
ax.set_ylim(300, 1600)
# plot grey horizontal gridlines
ax.yaxis.grid(True, which="major", color="grey", linestyle="-", linewidth=0.5)
fig.tight_layout()
fig.savefig("neerslag.png", dpi=300)
print("Done.")