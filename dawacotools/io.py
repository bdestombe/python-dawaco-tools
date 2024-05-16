from collections.abc import Iterable

import geopandas as gpd
import hydropandas as hpd
import numpy as np
import pandas as pd
import xarray as xr
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Test server
connection_string = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=tcp:pwnka-p-we-prd-dawaco-sql.database.windows.net;"
    "PORT=1433;"
    "DATABASE=Dawacoprod;"
    "Authentication=ActiveDirectoryInteractive;"
)
dbname = "dbo"

"""
Get date latest change to database:
  SELECT * FROM [dawacoprod].[guest].[Stijghgt] WHERE Recnum=(SELECT max(Recnum) FROM [dawacoprod].[guest].[Stijghgt]);
"""

connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
engine = create_engine(connection_url, echo=False)

meteo_header = [
    "statcode",
    "name",
    "x",
    "y",
    "N_start",
    "N_end",
    "T_start",
    "T_end",
    "TMAX_start",
    "TMAX_end",
    "TMIN_start",
    "TMIN_end",
    "V_start",
    "V_end",
]
a = pd.Timestamp
b = pd.NaT
# fmt: off
meteo_arr = [
    ['17', 'Den-Burg', 115435, 563268, a('1894-11-21'), a('2022-05-10'), b, b, b, b, b, b, b, b],
    ['225', 'Overveen', 102203, 489790, a('1898-11-01'), a('2022-05-10'), b, b, b, b, b, b, b, b],
    ['226', 'Wijk-aan-Zee', 101115, 500986, a('1910-01-01'), a('2022-05-10'), b, b, b, b, b, b, b, b],
    ['229', 'Zandvoort', 96675, 487396, a('1912-03-27'), a('2022-05-10'), b, b, b, b, b, b, b, b],
    ['234', 'Bergen-NH', 107603, 521696, a('1927-06-18'), a('2022-05-10'), b, b, b, b, b, b, b, b],
    ['235', 'Castricum', 104994, 506638, a('1927-07-01'), a('2022-05-10'), b, b, b, b, b, b, b, b],
    ['235W', 'De Kooy', 115137, 547547, a('1957-01-01'), a('2022-06-07'), a('1906-01-01'), a('2022-09-04'),
     a('1906-01-01'), a('2022-06-07'), a('1906-01-01'), a('2022-06-07'), a('1964-11-01'), a('2022-06-07')],
    ['240W', 'Schiphol', 112375, 480192, a('1971-01-01'), a('2022-06-07'), a('1951-01-01'), a('2022-06-07'),
     a('1951-01-01'), a('2022-06-07'), a('1951-01-01'), a('2022-06-07'), a('1987-09-11'), a('2022-06-07')],
    ['257W', 'Mensink', 101623, 502234, a('2001-05-01'), a('2022-06-07'), a('2001-05-01'), a('2022-06-07'),
     a('2001-05-01'), a('2022-06-07'), a('2001-05-01'), a('2022-06-07'), a('2001-05-02'), a('2022-06-07')],
    ['435', 'Heemstede', 102848, 485268, a('1866-12-01'), a('2022-05-10'), b, b, b, b, b, b, b, b],
    ['438', 'Hoofddorp', 107631, 479958, a('1866-12-01'), a('2022-05-10'), b, b, b, b, b, b, b, b],
    ['454', 'Lisse', 97283, 474334, a('1915-10-02'), a('2022-05-10'), b, b, b, b, b, b, b, b],
    ['593', 'Laren', 143323, 472733, a('1951-01-01'), a('2022-05-10'), b, b, b, b, b, b, b, b],
    ['BER PLUV', 'Pluvio Bergen', 107390, 521669, a('2017-03-01'), a('2020-05-31'), b, b, b, b, b, b, b, b],
    ['CAS PLUV', 'Pluvio Castricum', 104090, 507687, a('2017-01-01'), a('2020-05-31'), b, b, b, b, b, b, b, b],
    ['CAS1', 'Cas ps & sterrenwach', 104091, 507687, a('1932-01-01'), a('2016-12-31'), b, b, b, b, b, b, b, b],
    ['CAS3', 'Rainman', 0, 0, a('2000-07-01'), a('2008-03-31'), b, b, b, b, b, b, b, b],
    ['HMK', 'Heemskerk', 103938, 502758, a('1999-09-01'), a('2015-06-30'), b, b, b, b, b, b, b, b],
    ['LEI', 'Leiduin GW', 101123, 484581, a('1983-07-16'), a('2001-09-30'), b, b, b, b, b, b, b, b],
    ['LIJNDEN', 'Lijnden', 112313, 485028, a('1980-01-01'), a('2003-11-30'), b, b, b, b, b, b, b, b],
    ['LYS', 'Lysimeters Castricum', 104074, 507771, a('1975-01-16'), a('1995-10-16'), b, b, b, b, b, b, b, b],
]
# fmt: on

meteo_pars = {
    "Neerslag": "N",
    "Temperatuur": "T",
    "Temp. maximum": "TMAX",
    "Temp. minimum": "TMIN",
    "Verdamping": "V",
}


def df2gdf(df):
    df = df.loc[:, ~df.columns.duplicated()].copy()
    if "Xcoor" in df.columns:
        geom = gpd.points_from_xy(df.Xcoor, df.Ycoor, crs="EPSG:28992")
    else:
        geom = gpd.points_from_xy(df.x, df.y, crs="EPSG:28992")

    return gpd.GeoDataFrame(df, geometry=geom, crs="EPSG:28992")


def get_daw_mps(mpcode=None, partial_match_mpcode=True):
    """Inclusief vervallen! Retreive metadata of all wells. Takes 5 seconds."""
    q = f"SELECT * FROM {dbname}.mp "

    q += fuzzy_match_mpcode(
        mpcode=mpcode,
        partial_match_mpcode=partial_match_mpcode,
        mpcode_sql_name="MpCode",
    )

    b = pd.read_sql_query(q, engine)
    b.set_index("MpCode", inplace=True)

    get_daw_soort_mp(b)
    return df2gdf(b)


def get_daw_mon_dates(mpcode=None, filternr=None):
    """Retreive unique water quality sampling dates of all mpcode and filternr provided."""
    q = (
        f"select datum from {dbname}.gwkmon "  # for debug use * instead of Datum
        f"inner join {dbname}.filters on {dbname}.gwkmon.filtrec = {dbname}.filters.recnum "
    )

    q += fuzzy_match_mpcode(
        mpcode=mpcode,
        filternr=filternr,
        partial_match_mpcode=False,
        mpcode_sql_name="MpCode",
        filternr_sql_name="filtnr",
    )

    q += "ORDER BY datum "

    b = pd.read_sql_query(q, engine)

    return pd.to_datetime(b.datum.unique(), format="%Y-%m-%d", errors="coerce")


def fuzzy_match_mpcode(
    mpcode=None,
    filternr=None,
    partial_match_mpcode=True,
    mpcode_sql_name="MpCode",
    filternr_sql_name="filternr",
):
    if mpcode is None:
        return ""

    if not partial_match_mpcode and isinstance(mpcode, str):
        q = f"WHERE {mpcode_sql_name}='{mpcode}' "

    elif not partial_match_mpcode and isinstance(mpcode, Iterable):
        mp_code_Str = "', '".join(mpcode)
        q = f"WHERE {mpcode_sql_name} in ('{mp_code_Str}') "

    elif partial_match_mpcode and isinstance(mpcode, str):
        mps = pd.read_sql_query(f"SELECT MpCode FROM {dbname}.mp", engine).values[:, 0]
        mpcode_match = mps[[mpcode in s for s in mps]]
        mp_code_Str = "', '".join(mpcode_match)
        q = f"WHERE {mpcode_sql_name} in ('{mp_code_Str}') "

    elif partial_match_mpcode and isinstance(mpcode, Iterable):
        mps = pd.read_sql_query(f"SELECT MpCode FROM {dbname}.mp", engine).values[:, 0]
        mpcode_match = mps[[any(ss in s for ss in mpcode) for s in mps]]
        mp_code_Str = "', '".join(mpcode_match)
        q = f"WHERE {mpcode_sql_name} in ('{mp_code_Str}') "

    else:
        assert mpcode is None, "Unsupported mpcode type"

    if filternr is None:
        return q

    if isinstance(filternr, str):
        filternr_str = filternr

    elif isinstance(filternr, (float, int)):
        assert filternr >= 0, "Pumping well is zero and observations wells start counting at 1"

        filternr_str = str(int(filternr))

    elif isinstance(filternr, list):
        for i in filternr:
            assert int(i) > 0, "filternr is one-based"

        filternr_str = "', '".join([str(int(i)) for i in filternr])

    else:
        assert filternr is None, "Unsupported filternr type"

    q += f"AND {filternr_sql_name} in ('{filternr_str}') "

    return q


def get_daw_filters(
    mpcode=None,
    filternr=None,
    partial_match_mpcode=True,
    vervallen_filters_meenemen=False,
    return_hpd=False,
):
    """Retreive metadata of all filters. Takes 25 seconds."""
    match_mp_str = fuzzy_match_mpcode(
        mpcode=mpcode,
        filternr=None,
        partial_match_mpcode=partial_match_mpcode,
        mpcode_sql_name="MpCode",
        filternr_sql_name="Filtnr",
    )
    mps = pd.read_sql_query(f"SELECT * from {dbname}.mp {match_mp_str}", engine).drop(columns=["RECNUM"])

    match_filt_str = fuzzy_match_mpcode(
        mpcode=mpcode,
        filternr=filternr,
        partial_match_mpcode=partial_match_mpcode,
        mpcode_sql_name="MpCode",
        filternr_sql_name="Filtnr",
    )
    filters = pd.read_sql_query(
        f"SELECT * from {dbname}.filters {match_filt_str}",
        engine,
        dtype={"Filtnr": int},
    ).drop(columns=["RECNUM"])
    filters = filters[filters.MpCode != " "]
    b = filters.merge(mps, left_on="MpCode", right_on="MpCode", how="left")
    b["Verval_datum"] = pd.to_datetime(b["Verval_datum"], format="%Y-%m-%d", errors="coerce")
    if not vervallen_filters_meenemen:
        b = b[b["Verval_datum"].isna()]

    # Sommige filters zijn opnieuw geplaatst en verschijnen dubbel in de lijst
    b.drop_duplicates(["MpCode", "Filtnr"], keep="last", inplace=True)
    b.sort_values(by=["MpCode", "Filtnr"], inplace=True)

    get_daw_soort_mp(b)

    return dw_df_to_hpd(b) if return_hpd else df2gdf(b)


def dw_df_to_hpd(dw_df):
    b = pd.DataFrame(
        index=dw_df.index,
        data={
            "x": dw_df.Xcoor,
            "y": dw_df.Ycoor,
            "onderkant_filter": dw_df.Refpunt - dw_df.Ok_filt,
            "bovenkant_filter": dw_df.Refpunt - dw_df.Bk_filt,
            "metadata_available": True,
            "locatie": dw_df["MpCode"],
            "maaiveld": dw_df.Maaiveld,
            "filternr": dw_df.Filtnr,
            "meetpunt": dw_df.Refpunt,
            "soort": dw_df.Soort,
            "vervallen": pd.notna(dw_df.Verval_datum),
            "verval_datum": dw_df.Verval_datum,
            "wvp": dw_df.Wvp,
        },
    )
    return df2gdf(b)


def get_daw_boring(mpcode=None, join_with_mps=False):
    query = (
        f"select * from {dbname}.NenLaag "
        f"inner join {dbname}.NenNorm on {dbname}.NenLaag.Nencode = {dbname}.NenNorm.Code "
        f"left join {dbname}.NenToev on {dbname}.NenLaag.Recnum = {dbname}.NenToev.Nenlaagrec "
    )

    query += fuzzy_match_mpcode(
        mpcode=mpcode,
        filternr=None,
        partial_match_mpcode=True,
        mpcode_sql_name="MpCode",
        filternr_sql_name="filtnr",
    )

    b = pd.read_sql_query(query, engine)

    b.set_index("MpCode", inplace=True)

    if join_with_mps:
        mps = get_daw_mps(mpcode=mpcode)
        b = b.join(mps, lsuffix="MP_")
        b = df2gdf(b)

    return b


def get_daw_triwaco(mpcode=None):
    query = (
        "select e.Mpcode as hydmpcode, e.Bk_pak, e.Type_pak, e.Num_pak, "
        f"d.Mpcode, d.Maaiveld from {dbname}.HydStrat e "
        f"inner join {dbname}.MpMv d on e.MpCode = d.Mpcode "
    )

    query += fuzzy_match_mpcode(
        mpcode=mpcode,
        filternr=None,
        partial_match_mpcode=True,
        mpcode_sql_name="e.Mpcode",
        filternr_sql_name="filtnr",
    )

    b = pd.read_sql_query(query, engine)
    del b["hydmpcode"]

    b["dikte"] = b.groupby("Mpcode")["Bk_pak"].transform(lambda x: x.diff().shift(-1))

    # remove layers that have 1 cm thickness minimal thickness dawaco
    b = b[np.logical_or(b["dikte"] > 0.01, pd.isna(b.dikte))]

    b["bkp_nap"] = -b["Bk_pak"] + b["Maaiveld"]
    b["okp_nap"] = b["bkp_nap"] - b["dikte"]

    return b


def get_daw_soort_mp(a, key="Soort"):
    foutje = {
        "19ANL5196": 5,
        "19ANL5197": 5,
        "19ANL5408": 5,
        "19ANL5414": 5,
        "19ANL5415": 5,
        "19ANL5416": 5,
    }

    for k, v in foutje.items():
        if k in a.index:
            a.loc[k, key] = v

    sd = {
        1: "Waarnemingspunt",
        2: "Pompput",
        3: "Infiltratieput",
        5: "Opp.water meetpunt",
        6: "Monsterpunt",
    }
    for k, v in sd.items():
        a.loc[a[key] == k, key] = v
        a.loc[a[key] == str(k), key] = v


def get_daw_coords_from_mpcode(mpcode=None, partial_match_mpcode=True):
    assert isinstance(mpcode, str), "Only strings are accepted"

    mp = get_daw_mps(mpcode=mpcode, partial_match_mpcode=partial_match_mpcode)
    assert len(mp) == 1, f"Ambigous mpcode: {', '.join(mp.index)}"

    x, y = mp[["Xcoor", "Ycoor"]].values[0]

    return x, y


def get_daw_meteo_from_loc(x=None, y=None, mpcode=None, mettype=None, start_date=None, end_date=None):
    """
    Returns the nearest meteo stations that are needed to fill a timeseries from
    start_date to end_date as `out`.
    A timeseries is composed using most data of the nearest station and using more
    remote stations to fill the gaps and is returned as df_out.
    """
    if mpcode is not None:
        assert x is None and y is None, "Use either the coodinates or mpcode to refer to a location"

        x, y = get_daw_coords_from_mpcode(mpcode=mpcode, partial_match_mpcode=True)

    assert start_date is not None
    assert end_date is not None
    assert mettype in meteo_pars

    start_date = pd.Timestamp(start_date).floor(freq="D")
    end_date = pd.Timestamp(end_date).ceil(freq="D")
    istart = meteo_header.index(meteo_pars[mettype] + "_start")
    iend = meteo_header.index(meteo_pars[mettype] + "_end")
    within_dates = np.array([row[istart] <= end_date and row[iend] >= start_date for row in meteo_arr])  # False for NaT
    distance = np.array([((row[2] - x) ** 2 + (row[3] - y) ** 2) ** 0.5 for row in meteo_arr])
    isorts = np.arange(len(meteo_arr))[within_dates][np.argsort(distance[within_dates])]

    isorts_nooverlap = [isorts[0]]
    nooverlap_start, nooverlap_end = (
        meteo_arr[isorts[0]][istart],
        meteo_arr[isorts[0]][iend],
    )

    for isort in isorts:
        if (meteo_arr[isort][istart] < nooverlap_start and nooverlap_start > start_date) or (
            meteo_arr[isort][iend] > nooverlap_end and nooverlap_end < end_date
        ):
            isorts_nooverlap.append(isort)
            nooverlap_start, nooverlap_end = (
                meteo_arr[isort][istart],
                meteo_arr[isort][iend],
            )

    out = [(meteo_arr[i][0], distance[i], get_daw_ts_meteo(meteo_arr[i][0], mettype)) for i in isorts_nooverlap]

    # construct merged_ts:
    if len(out) > 1:
        name = f"Samengestelde {mettype} van {', '.join([i[0] for i in out])}"
    else:
        name = "Station " + out[0][0] + " - " + mettype

    index = pd.date_range(start_date, end_date, freq="D")
    df_out = pd.Series(data=None, index=index, dtype=float, name=name)

    for _, _, ts in out[::-1]:
        df_out.loc[ts.index.min() : ts.index.max()] = ts

    return df_out, out


def get_daw_meteo_arr_daterange():
    """Constructs the array used by get_daw_meteo_from_loc."""
    import pprint

    l = []
    for sc in meteo_arr:
        ll = []
        for mt in [
            "Neerslag",
            "Temperatuur",
            "Temp. maximum",
            "Temp. minimum",
            "Verdamping",
        ]:
            df = get_daw_ts_meteo(sc[0], mt)
            ll.extend([df.index.min(), df.index.max()])

        l.append(ll)

    arr3 = [[a, b, int(c), int(d), *lli] for (a, b, c, d), lli in zip([a[:4] for a in meteo_arr], l)]
    for ai in arr3:
        s = pprint.pformat(ai, width=999, indent=4)
        # s = s.replace("Timestamp", "pd.Timestamp")
        s = s.replace("Timestamp", "a")
        s = s.replace(" 00:00:00')", "')")
        # s = s.replace("NaT", "pd.NaT")
        s = s.replace("NaT", "b")
        s += ","


def get_knmi_station_meta():
    """
    Op deze pagina treft U een overzicht aan van alle tijdreeksen van de 320 actuele neerslagstations en 350
    historische neerslagstations. Vermeld wordt de 24-uurs neerslagsom, gemeten van 0800 utc op de voorafgaande dag tot
    0800 utc op de vermelde datum. De hoeveelheid wordt weergegeven in tienden van millimeters. De neerslaggegevens
    worden per 10 dagen gevalideerd. Dit proces neemt maximaal drie weken in beslag. De gevalideerde gegevens worden
    toegevoegd aan de bestaande reeksen. Hierdoor is de einddatum van iedere reeks gelijk aan die van de laatst
    beschikbare gevalideerde dag (waarvoor de gevalideerde gegevens beschikbaar zijn).

    # https://www.knmi.nl/nederland-nu/klimatologie/monv/reeksen staan alle links naar zip. Gebruik regex
    mydateparser = lambda x: pd.to_datetime(x, format="%Y%m%d", errors='coerce')
    pd.read_csv("https://cdn.knmi.nl/knmi/map/page/klimatologie/gegevens/monv_reeksen/neerslaggeg_AARDENBURG_711.zip", skiprows=23, index_col='STN', parse_dates=[1], date_parser=mydateparser)


    Returns
    -------

    """

    def mydateparser(x):
        return pd.to_datetime(x, format="%Y%m%d", errors="coerce")

    return pd.read_csv(
        "https://cdn.knmi.nl/knmi/map/page/klimatologie/gegevens/Neerslagstations_apr2022_d1.txt",
        sep="\t",
        header=0,
        skiprows=[1],
        decimal=",",
        index_col="STN",
        parse_dates=[1, 2],
        date_parser=mydateparser,
    )


def get_daw_ts_meteo(statcode, mettype):
    """

    Parameters
    ----------
    statcode : str
        Any of:
            '017', '225', '226', '229', '234', '235', '235W', '240W',
            '257W', '435', '438', '454', '593', 'BER PLUV', 'CAS PLUV',
            'CAS1', 'CAS3', 'HMK', 'LEI', 'LIJNDEN', 'LYS'

    mettype : str
        Any of:
            'Neerslag', 'Temperatuur', 'Temp. maximum', 'Temp. minimum', 'Verdamping'

    > 234, 235, 257W, BER PLUV, CAS PLUV en CAS 1 coordinaten komen uit dawaco
    overige coordinaten gebaseerd op plaatsnaam.


    Metpar  Mettype         Eenheid
    N	    Neerslag	    mm
    T	    Temperatuur	    oC
    TMAX	Temp. maximum	oC
    TMIN	Temp. minimum	oC
    V	    Verdamping	    mm
    """
    assert statcode in [row[0] for row in meteo_arr], "not a valid statcode"
    assert mettype in meteo_pars, "not a valid mettype"

    q = f"SELECT * FROM {dbname}.metwaar " f"WHERE code = '{statcode}' and code_par = '{meteo_pars[mettype]}' "
    b = pd.read_sql_query(q, engine)
    waarnemingen = b[[s for s in b.columns if "W_d" in s]].values.reshape(-1)
    jaar = np.repeat(b.Jaar.values, 31).astype(int).astype(str)
    maand = np.repeat(b.Maand.values, 31).astype(int).astype(str)
    dag = np.tile(np.arange(1, 32), len(b)).astype(int).astype(str)
    dates_str = np.array([x1 + "-" + x2 + "-" + x3 for x1, x2, x3 in zip(jaar, maand, dag)])

    # sometimes missing value is -99 and sometimes 0.
    dates = pd.to_datetime(dates_str, format="%Y-%m-%d", errors="coerce")
    mask = np.logical_and(waarnemingen != -99.0, ~pd.isnull(dates))

    # Is an error made if there are multiple values?
    # print('Missing value: ', np.unique(waarnemingen[pd.isnull(dates)]))

    return pd.Series(
        data=waarnemingen[mask],
        index=dates[mask],
        name="Station " + statcode + " - " + mettype,
    )


def get_daw_ts_stijghgt(mpcode=None, filternr=None):
    """

    :param mpcode:
    :param filternr:
    :param start: string in de vorm van YYYY-MM-DD
    :param end: string in de vorm van YYYY-MM-DD
    :return:
    """
    assert mpcode is not None and filternr is not None, "Define mpcode and filternr"

    query = f"""
    SELECT datum, tijd, meting_nap
    FROM {dbname}.Stijghgt
    INNER JOIN {dbname}.Filters on {dbname}.Filters.recnum = {dbname}.Stijghgt.filtrec
    WHERE Filters.mpcode = '{mpcode!s}' and Filters.filtnr = '{filternr!s}'"""

    query += """\nORDER BY datum, tijd"""

    b = pd.read_sql_query(query, engine)
    values = b["meting_nap"].values
    values[values < -60.0] = np.nan

    f"{mpcode!s}_{filternr!s}"

    if len(b) == 0:
        mps = pd.read_sql_query(f"SELECT MpCode FROM {dbname}.mp", engine).values[:, 0]
        assert mpcode in mps, f"mpcode: {mpcode} not in Dawaco"

    out = pd.Series(
        data=values,
        index=pd.to_datetime(b.datum.astype(str) + b.tijd, format="%Y-%m-%d%H:%M", errors="coerce"),
        name="mNAP",
    )
    out = out.sort_index()
    return identify_data_gaps(out)


def get_daw_ts_temp(mpcode=None, filternr=None):
    assert mpcode is not None and filternr is not None, "Define mpcode and filternr"

    query = f"""
    SELECT datum, tijd, Temp
    FROM {dbname}.Stijghgt
    INNER JOIN {dbname}.Filters on {dbname}.Filters.recnum = {dbname}.Stijghgt.filtrec
    WHERE Filters.mpcode = '{mpcode!s}' and Filters.filtnr = '{filternr!s}'
    ORDER BY datum, tijd"""

    b = pd.read_sql_query(query, engine)
    values = b["Temp"].values
    values[values < -60.0] = np.nan
    values[values == 0.0] = np.nan

    name = f"{mpcode!s}_{filternr!s}"

    if len(b) == 0:
        pass

    out = pd.Series(
        data=values,
        index=pd.to_datetime(b.datum.astype(str) + b.tijd, format="%Y-%m-%d%H:%M", errors="coerce"),
        name=name,
    )
    out = out.sort_index()
    return identify_data_gaps(out)


def get_hpd_gws_obs(
    df_filter=None,
    mpcode=None,
    filternr=None,
    partial_match_mpcode=True,
):
    if df_filter is None:
        filter_metadata_df = get_daw_filters(
            mpcode=mpcode,
            partial_match_mpcode=partial_match_mpcode,
            filternr=filternr,
        )
    else:
        filter_metadata_df = df_filter

    assert len(filter_metadata_df) == 1, (
        f"Your mpcode is not specific enough. "
        f"Multiple are returned: \n{filter_metadata_df}. \n"
        f"Or set `partial_match_mpcode` to `False` and use the complete `mpcode`"
    )
    filter_metadata = filter_metadata_df.iloc[0]

    gws_measurements = get_daw_ts_stijghgt(
        mpcode=filter_metadata["MpCode"],
        filternr=int(filter_metadata["Filtnr"]),
    )

    # Extra PWN attributes
    meta_pwn = {
        "soort": filter_metadata.Soort,
        "vervallen": not pd.isna(filter_metadata.Verval_datum),
        "verval_datum": filter_metadata.Verval_datum,
        "wvp": filter_metadata.Wvp,
    }

    # Hydropandas GroundwaterObs attributes
    meta = {
        "name": f"{filter_metadata['MpCode']}-{filter_metadata['Filtnr']:03d}",
        "x": float(filter_metadata["Xcoor"]),
        "y": float(filter_metadata["Ycoor"]),
        "meta": meta_pwn,
        "filename": pd.Timestamp.now().strftime("Dawacotools SQL API - %Y%m%d"),
        "monitoring_well": filter_metadata["MpCode"],
        "tube_nr": int(filter_metadata["Filtnr"]),
        "screen_top": float(filter_metadata["Refpunt"] - filter_metadata["Ok_filt"]),
        "screen_bottom": float(filter_metadata["Refpunt"] - filter_metadata["Bk_filt"]),
        "ground_level": float(filter_metadata["Maaiveld"]),
        "tube_top": float(filter_metadata["Refpunt"]),
        "metadata_available": True,
        "source": "dawaco",
        "unit": "mNAP",
    }

    return hpd.GroundwaterObs(
        gws_measurements,
        **meta,
    )


def get_nlmod_index_nearest_cell(fils, model_ds, error_if_nearest_cell_inactive=False):
    assert isinstance(fils, gpd.GeoDataFrame)
    fils = fils.copy()

    qxc = xr.DataArray(
        fils.geometry.x.values,
        dims=("filters",),
    )
    qyc = xr.DataArray(
        fils.geometry.y.values,
        dims=("filters",),
    )
    qzc = xr.DataArray(
        fils.Refpunt - (fils.Bk_filt + fils.Ok_filt) / 2,
        dims=("filters",),
    )
    topbot = np.concatenate((model_ds.top.values[None], model_ds.bot))
    zc = xr.ones_like(model_ds.bot) * (topbot[:-1] + topbot[1:]) / 2
    distances = np.sqrt((qxc - model_ds.x) ** 2 + (qyc - model_ds.y) ** 2 + (qzc - zc) ** 2)

    nearest_coords = distances.argmin(dim=("icell2d", "layer"))

    if error_if_nearest_cell_inactive:
        assert (model_ds.idomain.isel(**nearest_coords) > 0).all(), "Filters are placed in inactive cells"

    elif (model_ds.idomain.isel(**nearest_coords) > 0).all():
        pass

    else:
        nearest_coords = distances.where(model_ds.idomain > 0).argmin(dim=("icell2d", "layer"))

    return pd.DataFrame(nearest_coords, index=fils.index)


def get_nlmod_vertical_profile(model_ds, x, y, label, active_only=True):
    """Get vertical profile of model_ds[label] given global coordinates
    The returned array contains the [top_cell, bot_cell, value] for all active cells.
    Returned array has size (3, nlay_active).
    """
    icid = np.argmin((model_ds.x.values - x) ** 2 + (model_ds.y.values - y) ** 2)
    topbot = np.concatenate((model_ds.top.isel(cid=icid).values[None], model_ds.bot.isel(cid=icid).values))
    out = np.stack((topbot[:-1], topbot[1:], model_ds[label].isel(cid=icid).values))

    if active_only:
        ilay_active = model_ds.idomain.isel(cid=icid).values > 0
        return out[:, ilay_active]
    return out


def get_regis_ds(rds_x, rds_y, keys=None):
    regis_ds = xr.open_dataset("http://www.dinodata.nl:80/opendap/REGIS/REGIS.nc")
    dsi_r = regis_ds.sel(x=rds_x, y=rds_y, method="nearest")

    if keys is None:
        dsi_r2 = dsi_r.compute().sel(layer=~np.isnan(dsi_r.bottom))

    else:
        dsi_r2 = dsi_r[keys].compute().sel(layer=~np.isnan(dsi_r.bottom))

    return dsi_r2


def identify_data_gaps(series):
    """
    Add NaN's at places where data is expected.

    instead of == maybe use isclose

    Parameters
    ----------
    series

    Returns
    -------

    """
    series = series[pd.notna(series.index)]
    index, values = series.index, series.values
    dt = (index[1:] - index[:-1]).values
    assert np.all(dt.astype(float) > 0), "Index is not sorted or has duplicates"

    iden = (np.roll(dt, -2) == np.roll(dt, -1)) & (np.roll(dt, 1) == np.roll(dt, 2)) & (dt >= 2 * np.roll(dt, -1))
    start, end, delta, delta_prev = (
        index[:-1][iden],
        index[1:][iden],
        dt[iden],
        np.roll(dt, -1)[iden],
    )

    out_index, out_values = index.copy(), values.copy()
    for si, ei, _di, dpi in zip(start, end, delta, delta_prev):
        t_insert = np.arange(si, ei, dpi)[1:]
        v_insert = np.full(t_insert.shape, np.nan, dtype=float)
        before_ind = np.argwhere(index == ei).item()
        out_index = np.insert(out_index, before_ind, t_insert)
        out_values = np.insert(out_values, before_ind, v_insert)

    return pd.Series(data=out_values, index=out_index, name=series.name)
