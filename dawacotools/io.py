"""Core I/O functions for accessing and processing DAWACO database data."""

from __future__ import annotations

import datetime as dt
import os
from collections.abc import Iterable, Sequence

import geopandas
import hydropandas as hpd
import numpy as np
import pandas as pd
import xarray as xr
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

DEFAULT_DRIVER = "ODBC Driver 18 for SQL Server"
DEFAULT_SERVER = "tcp:pwnka-p-we-prd-dawaco-sql.database.windows.net"
DEFAULT_PORT = 1433
DEFAULT_DATABASE = "Dawacoprod"
DEFAULT_AUTHENTICATION = "ActiveDirectoryInteractive"
DEFAULT_SCHEMA = "dbo"
DATABASE_URL_ENV_VAR = "DAWACOTOOLS_DATABASE_URL"
CONNECTION_STRING_ENV_VAR = "DAWACOTOOLS_CONNECTION_STRING"
AUTHENTICATION_ENV_VAR = "DAWACOTOOLS_ODBC_AUTHENTICATION"
SCHEMA_ENV_VAR = "DAWACOTOOLS_DB_SCHEMA"


def create_connection_string(authentication: str | None = None) -> str:
    """Create the default SQL Server ODBC connection string."""
    if authentication is None:
        authentication = os.environ.get(AUTHENTICATION_ENV_VAR, DEFAULT_AUTHENTICATION)

    return (
        f"DRIVER={{{DEFAULT_DRIVER}}};"
        f"SERVER={DEFAULT_SERVER};"
        f"PORT={DEFAULT_PORT};"
        f"DATABASE={DEFAULT_DATABASE};"
        f"Authentication={authentication};"
    )


def get_connection_string() -> str:
    """Return the SQL Server ODBC connection string for the current environment."""
    connection = os.environ.get(CONNECTION_STRING_ENV_VAR)
    if connection is not None:
        return connection

    return create_connection_string()


connection_string = get_connection_string()
dbname = os.environ.get(SCHEMA_ENV_VAR, DEFAULT_SCHEMA)
engine = None

"""
Get date latest change to database:
  SELECT * FROM [dawacoprod].[guest].[Stijghgt] WHERE Recnum=(SELECT max(Recnum) FROM [dawacoprod].[guest].[Stijghgt]);
"""

connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})


def create_dawaco_engine(database_url: str | None = None, echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine for DAWACO or a configured test database."""
    if database_url is None:
        database_url = os.environ.get(DATABASE_URL_ENV_VAR)

    if database_url:
        return create_engine(database_url, echo=echo)

    connection = get_connection_string()
    return create_engine(URL.create("mssql+pyodbc", query={"odbc_connect": connection}), echo=echo)


def get_engine() -> Engine:
    """Return the configured SQLAlchemy engine, creating the DAWACO engine lazily."""
    global engine

    if engine is None:
        engine = create_dawaco_engine()

    return engine


def set_database_engine(database_engine: Engine | None, schema: str | None = None) -> None:
    """Set the SQLAlchemy engine used by DAWACO readers."""
    global dbname, engine

    engine = database_engine
    if schema is not None:
        dbname = schema


def reset_database_engine(schema: str | None = None) -> None:
    """Reset DAWACO readers to the default lazily-created production engine."""
    global dbname, engine

    engine = None
    dbname = schema if schema is not None else os.environ.get(SCHEMA_ENV_VAR, DEFAULT_SCHEMA)


def _table(name: str) -> str:
    return f"{dbname}.{name}" if dbname else name


def _read_sql_query(query: str, params: dict[str, object] | None = None, **kwargs) -> pd.DataFrame:
    return pd.read_sql_query(text(query), get_engine(), params=params, **kwargs)


def _sql_in_clause(column_name: str, values: Sequence[object], parameter_prefix: str) -> tuple[str, dict[str, object]]:
    if len(values) == 0:
        return "1 = 0", {}

    params = {f"{parameter_prefix}_{i}": value for i, value in enumerate(values)}
    placeholders = ", ".join(f":{name}" for name in params)
    return f"{column_name} IN ({placeholders})", params


def _normalise_mpcodes(mpcode) -> list[str]:
    if isinstance(mpcode, str):
        return [mpcode]

    if isinstance(mpcode, Iterable):
        return [str(code) for code in mpcode]

    msg = "Unsupported mpcode type"
    raise ValueError(msg)


def _matching_mpcodes(mpcode, partial_match_mpcode: bool) -> list[str]:
    mpcodes = _normalise_mpcodes(mpcode)
    if not partial_match_mpcode:
        return mpcodes

    available_mpcodes = _read_sql_query(f"SELECT MpCode FROM {_table('mp')}")["MpCode"].astype(str).to_numpy()
    return [
        available_mpcode
        for available_mpcode in available_mpcodes
        if any(mpcode in available_mpcode for mpcode in mpcodes)
    ]


def _normalise_filternr(filternr) -> int:
    try:
        filternr_float = float(filternr)
    except (TypeError, ValueError):
        msg = "filternr must be a non-negative integer-like value"
        raise ValueError(msg) from None

    if not np.isfinite(filternr_float) or not filternr_float.is_integer() or filternr_float < 0:
        msg = "filternr must be a non-negative integer-like value"
        raise ValueError(msg)

    return int(filternr_float)


def _normalise_filternrs(filternr) -> list[int]:
    if isinstance(filternr, str) or not isinstance(filternr, Iterable):
        return [_normalise_filternr(filternr)]

    return [_normalise_filternr(value) for value in filternr]


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


def _meteo_station_frame() -> pd.DataFrame:
    return pd.DataFrame(meteo_arr, columns=pd.Index(meteo_header))


def _required_timestamp(value: object, name: str) -> pd.Timestamp:
    if not isinstance(value, str | dt.date | dt.datetime | np.datetime64 | pd.Timestamp):
        msg = f"{name} must be a valid timestamp"
        raise TypeError(msg)

    timestamp = pd.Timestamp(value)
    if isinstance(timestamp, pd.Timestamp):
        return timestamp

    msg = f"{name} must be a valid timestamp"
    raise ValueError(msg)


def df2gdf(df):
    """
    Convert DataFrame with coordinate columns to GeoDataFrame.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing coordinate columns (Xcoor/Ycoor or x/y).

    Returns
    -------
    geopandas.GeoDataFrame
        GeoDataFrame with Point geometry in RD New (EPSG:28992) coordinates.
    """
    df = df.loc[:, ~df.columns.duplicated()].copy()
    if "Xcoor" in df.columns:
        geom = geopandas.points_from_xy(df.Xcoor, df.Ycoor, crs="EPSG:28992")
    else:
        geom = geopandas.points_from_xy(df.x, df.y, crs="EPSG:28992")

    return geopandas.GeoDataFrame(df, geometry=geom, crs="EPSG:28992")


def get_daw_mps(mpcode=None, partial_match_mpcode=True):
    """Inclusief vervallen! Retreive metadata of all wells. Takes 5 seconds."""
    q = f"SELECT * FROM {_table('mp')} "

    match_mp_str, params = fuzzy_match_mpcode(
        mpcode=mpcode,
        partial_match_mpcode=partial_match_mpcode,
        mpcode_sql_name="MpCode",
        return_params=True,
    )
    q += match_mp_str

    b = _read_sql_query(q, params=params, dtype={"Soort": int})
    b.set_index("MpCode", inplace=True)

    get_daw_soort_mp(b)
    return df2gdf(b)


def get_daw_mon_dates(mpcode=None, filternr=None):
    """Retreive unique water quality sampling dates of all mpcode and filternr provided."""
    gwkmon_table = _table("gwkmon")
    filters_table = _table("filters")
    q = (
        f"select datum from {gwkmon_table} as gwkmon "  # for debug use * instead of Datum
        f"inner join {filters_table} as filters on gwkmon.filtrec = filters.recnum "
    )

    match_mp_str, params = fuzzy_match_mpcode(
        mpcode=mpcode,
        filternr=filternr,
        partial_match_mpcode=False,
        mpcode_sql_name="MpCode",
        filternr_sql_name="filtnr",
        return_params=True,
    )
    q += match_mp_str

    q += "ORDER BY datum "

    b = _read_sql_query(q, params=params)

    return pd.to_datetime(b.datum.unique(), format="%Y-%m-%d", errors="coerce")


def fuzzy_match_mpcode(
    mpcode=None,
    filternr=None,
    partial_match_mpcode=True,
    mpcode_sql_name="MpCode",
    filternr_sql_name="filternr",
    return_params=False,
):
    conditions = []
    params = {}

    if mpcode is not None:
        mpcode_clause, mpcode_params = _sql_in_clause(
            mpcode_sql_name,
            _matching_mpcodes(mpcode, partial_match_mpcode),
            "mpcode",
        )
        conditions.append(mpcode_clause)
        params.update(mpcode_params)

    if filternr is not None:
        filternr_clause, filternr_params = _sql_in_clause(
            filternr_sql_name,
            _normalise_filternrs(filternr),
            "filternr",
        )
        conditions.append(filternr_clause)
        params.update(filternr_params)

    query = "" if len(conditions) == 0 else "WHERE " + " AND ".join(conditions) + " "

    if return_params:
        return query, params

    return query


def get_daw_filters(
    mpcode=None,
    filternr=None,
    partial_match_mpcode=True,
    vervallen_filters_meenemen=False,
    return_hpd=False,
):
    """Retreive metadata of all filters. Takes 25 seconds."""
    match_mp_str, match_mp_params = fuzzy_match_mpcode(
        mpcode=mpcode,
        filternr=None,
        partial_match_mpcode=partial_match_mpcode,
        mpcode_sql_name="MpCode",
        filternr_sql_name="Filtnr",
        return_params=True,
    )
    mps = _read_sql_query(f"SELECT * from {_table('mp')} {match_mp_str}", params=match_mp_params).drop(
        columns=["RECNUM"]
    )

    match_filt_str, match_filt_params = fuzzy_match_mpcode(
        mpcode=mpcode,
        filternr=filternr,
        partial_match_mpcode=partial_match_mpcode,
        mpcode_sql_name="MpCode",
        filternr_sql_name="Filtnr",
        return_params=True,
    )
    filters = _read_sql_query(
        f"SELECT * from {_table('filters')} {match_filt_str}",
        params=match_filt_params,
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
    nenlaag_table = _table("NenLaag")
    nennorm_table = _table("NenNorm")
    nentoev_table = _table("NenToev")
    query = (
        f"select * from {nenlaag_table} as NenLaag "
        f"inner join {nennorm_table} as NenNorm on NenLaag.Nencode = NenNorm.Code "
        f"left join {nentoev_table} as NenToev on NenLaag.Recnum = NenToev.Nenlaagrec "
    )

    match_mp_str, params = fuzzy_match_mpcode(
        mpcode=mpcode,
        filternr=None,
        partial_match_mpcode=True,
        mpcode_sql_name="MpCode",
        filternr_sql_name="filtnr",
        return_params=True,
    )
    query += match_mp_str

    b = _read_sql_query(query, params=params)

    b.set_index("MpCode", inplace=True)

    if join_with_mps:
        mps = get_daw_mps(mpcode=mpcode)
        b = b.join(mps, lsuffix="MP_")
        b = df2gdf(b)

    return b


def get_daw_triwaco(mpcode=None):
    hydstrat_table = _table("HydStrat")
    mpmv_table = _table("MpMv")
    query = (
        "select e.Mpcode as hydmpcode, e.Bk_pak, e.Type_pak, e.Num_pak, "
        f"d.Mpcode, d.Maaiveld from {hydstrat_table} e "
        f"inner join {mpmv_table} d on e.MpCode = d.Mpcode "
    )

    match_mp_str, params = fuzzy_match_mpcode(
        mpcode=mpcode,
        filternr=None,
        partial_match_mpcode=True,
        mpcode_sql_name="e.Mpcode",
        filternr_sql_name="filtnr",
        return_params=True,
    )
    query += match_mp_str

    b = _read_sql_query(query, params=params)
    del b["hydmpcode"]
    b = b.sort_values(["Mpcode", "Bk_pak", "Num_pak", "Type_pak"], kind="mergesort").reset_index(drop=True)

    b["dikte"] = b.groupby("Mpcode", sort=False)["Bk_pak"].transform(lambda x: x.diff().shift(-1))

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
        4: "Point of interest",
        5: "Opp.water meetpunt",
        6: "Monsterpunt",
    }
    a[key] = a[key].map(sd)


def get_daw_coords_from_mpcode(mpcode=None, partial_match_mpcode=True):
    assert isinstance(mpcode, str), "Only strings are accepted"

    mp = get_daw_mps(mpcode=mpcode, partial_match_mpcode=partial_match_mpcode)
    assert len(mp) == 1, f"Ambigous mpcode: {', '.join(mp.index)}"

    x, y = mp[["Xcoor", "Ycoor"]].values[0]

    return x, y


def get_daw_meteo_from_loc(x=None, y=None, mpcode=None, mettype=None, start_date=None, end_date=None):
    """Return nearest meteo stations needed to fill a timeseries.

    The returned series covers ``start_date`` to ``end_date``.
    A timeseries is composed using most data of the nearest station and using more
    remote stations to fill the gaps and is returned as df_out.
    """
    if mpcode is not None:
        assert x is None and y is None, "Use either the coodinates or mpcode to refer to a location"

        x, y = get_daw_coords_from_mpcode(mpcode=mpcode, partial_match_mpcode=True)

    if x is None or y is None:
        msg = "Provide x/y coordinates or mpcode"
        raise ValueError(msg)
    x_coord = float(x)
    y_coord = float(y)

    assert mettype in meteo_pars

    start_date = _required_timestamp(start_date, "start_date").floor("D")
    end_date = _required_timestamp(end_date, "end_date").ceil("D")
    meteo = _meteo_station_frame()
    start_key = meteo_pars[mettype] + "_start"
    end_key = meteo_pars[mettype] + "_end"
    station_start = pd.to_datetime(meteo[start_key])
    station_end = pd.to_datetime(meteo[end_key])
    within_dates = ((station_start <= end_date) & (station_end >= start_date)).to_numpy(dtype=bool)
    distance = np.sqrt(
        (meteo["x"].to_numpy(dtype=float) - x_coord) ** 2 + (meteo["y"].to_numpy(dtype=float) - y_coord) ** 2
    )
    isorts = np.arange(len(meteo_arr))[within_dates][np.argsort(distance[within_dates])]
    if len(isorts) == 0:
        msg = f"No meteo station covers {mettype} from {start_date.date()} to {end_date.date()}."
        raise ValueError(msg)

    isorts_nooverlap = [isorts[0]]
    nooverlap_start, nooverlap_end = (
        station_start.iloc[isorts[0]],
        station_end.iloc[isorts[0]],
    )

    for isort in isorts:
        candidate_start = station_start.iloc[isort]
        candidate_end = station_end.iloc[isort]
        if (candidate_start < nooverlap_start and nooverlap_start > start_date) or (
            candidate_end > nooverlap_end and nooverlap_end < end_date
        ):
            isorts_nooverlap.append(isort)
            nooverlap_start, nooverlap_end = candidate_start, candidate_end

    out = [
        (str(meteo.iloc[i]["statcode"]), distance[i], get_daw_ts_meteo(str(meteo.iloc[i]["statcode"]), mettype))
        for i in isorts_nooverlap
    ]

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
    """Return station date ranges reconstructed from meteo measurements."""
    rows = []
    meteo = _meteo_station_frame()
    for _, station in meteo.iterrows():
        row = [station["statcode"], station["name"], int(station["x"]), int(station["y"])]
        for mettype in meteo_pars:
            timeseries = get_daw_ts_meteo(str(station["statcode"]), mettype)
            row.extend([timeseries.index.min(), timeseries.index.max()])

        rows.append(row)

    return pd.DataFrame(rows, columns=pd.Index(meteo_header))


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

    q = f"SELECT * FROM {_table('metwaar')} WHERE code = :statcode and code_par = :metpar "
    b = _read_sql_query(q, params={"statcode": statcode, "metpar": meteo_pars[mettype]})
    waarnemingen = b[[s for s in b.columns if "W_d" in s]].values.reshape(-1)
    jaar = np.repeat(b.Jaar.values, 31).astype(int).astype(str)
    maand = np.repeat(b.Maand.values, 31).astype(int).astype(str)
    dag = np.tile(np.arange(1, 32), len(b)).astype(int).astype(str)
    dates_str = np.array([x1 + "-" + x2 + "-" + x3 for x1, x2, x3 in zip(jaar, maand, dag, strict=True)])

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
    assert mpcode is not None and filternr is not None, "Define mpcode and filternr"
    filternr_value = _normalise_filternr(filternr)

    stijghgt_table = _table("Stijghgt")
    filters_table = _table("Filters")
    query = f"""
    SELECT datum, tijd, meting_nap
    FROM {stijghgt_table} as Stijghgt
    INNER JOIN {filters_table} as Filters on Filters.recnum = Stijghgt.filtrec
    WHERE Filters.mpcode = :mpcode and Filters.filtnr = :filternr"""

    query += """\nORDER BY datum, tijd"""

    b = _read_sql_query(query, params={"mpcode": mpcode, "filternr": filternr_value})
    values = b["meting_nap"].values
    values[values < -60.0] = np.nan

    if len(b) == 0:
        mps = _read_sql_query(f"SELECT MpCode FROM {_table('mp')}").values[:, 0]
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
    filternr_value = _normalise_filternr(filternr)

    stijghgt_table = _table("Stijghgt")
    filters_table = _table("Filters")
    query = f"""
    SELECT datum, tijd, Temp
    FROM {stijghgt_table} as Stijghgt
    INNER JOIN {filters_table} as Filters on Filters.recnum = Stijghgt.filtrec
    WHERE Filters.mpcode = :mpcode and Filters.filtnr = :filternr
    ORDER BY datum, tijd"""

    b = _read_sql_query(query, params={"mpcode": mpcode, "filternr": filternr_value})
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
        "location": filter_metadata["MpCode"],
        "tube_nr": int(filter_metadata["Filtnr"]),
        "screen_top": float(filter_metadata["Refpunt"] - filter_metadata["Bk_filt"]),
        "screen_bottom": float(filter_metadata["Refpunt"] - filter_metadata["Ok_filt"]),
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
    assert isinstance(fils, geopandas.GeoDataFrame)
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
    regis_ds = xr.open_dataset("https://dinodata.nl/opendap/REGIS/REGIS.nc")
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
    if len(series) < 2:
        return series

    index = series.index
    dt = (index[1:] - index[:-1]).values
    assert np.all(dt.astype(float) > 0), "Index is not sorted or has duplicates"

    iden = (np.roll(dt, -2) == np.roll(dt, -1)) & (np.roll(dt, 1) == np.roll(dt, 2)) & (dt >= 2 * np.roll(dt, -1))
    start, end, delta, delta_prev = (
        index[:-1][iden],
        index[1:][iden],
        dt[iden],
        np.roll(dt, -1)[iden],
    )

    inserted = []
    for si, ei, _di, dpi in zip(start, end, delta, delta_prev, strict=True):
        t_insert = np.arange(si, ei, dpi)[1:]
        if len(t_insert) > 0:
            inserted.append(pd.Series(data=np.nan, index=pd.to_datetime(t_insert), name=series.name))

    out = pd.concat([series, *inserted]).sort_index(kind="mergesort") if inserted else series.copy()

    out_dt = (out.index[1:] - out.index[:-1]).values
    if not np.all(out_dt.astype(float) > 0):
        print(
            f"Unable to fill gaps of {series.name}. Index is not sorted or has duplicates: {out_dt}. Returning original series."
        )
        return series
    return out
