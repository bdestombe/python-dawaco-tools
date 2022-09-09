import geopandas as gpd
import numpy as np
import pandas as pd
import xarray as xr
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

# Test server
# connection_string = (
#     'DRIVER={ODBC Driver 17 for SQL Server};'
#     'SERVER=pwnka-a-we-acc-dawaco-sql.database.windows.net;'
#     'PORT=1433;'
#     'DATABASE=Dawacotest;'
#     'Trusted_Connection=yes;')
# dbname = 'dbo'

# Production server
connection_string = (
    r"Driver={SQL Server};"
    r"Server=IN_PW_P03;"  # Deze server zou het best moeten werken
    r"Database=dawacoprod;"
    r"Trusted_Connection=yes;"
)
dbname = "guest"

connection_url = URL.create("mssql+pyodbc", query={"odbc_connect": connection_string})
engine = create_engine(connection_url, echo=False)


def df2gdf(df):
    df = df.loc[:, ~df.columns.duplicated()].copy()
    geom = gpd.points_from_xy(df.Xcoor, df.Ycoor, crs="EPSG:28992")
    gdf = gpd.GeoDataFrame(df, geometry=geom)
    return gdf


def get_daw_mps(mpcode=None, partial_match_mpcode=True):
    """Retreive metadata of all wells. Takes 5 seconds."""

    q = f"SELECT * FROM {dbname}.mp "

    q += fuzzy_match_mpcode(
        mpcode=mpcode,
        partial_match_mpcode=partial_match_mpcode,
        mpcode_sql_name="MpCode",
    )

    b = pd.read_sql_query(q, engine)
    b.set_index("MpCode", inplace=True)

    get_daw_soort_mp(b)
    b = df2gdf(b)
    return b


def fuzzy_match_mpcode(
    mpcode=None, partial_match_mpcode=True, mpcode_sql_name="MpCode"
):
    if mpcode is None:
        return ""

    else:
        if not partial_match_mpcode and isinstance(mpcode, str):
            q = f"WHERE {mpcode_sql_name}='{mpcode}' "

        elif not partial_match_mpcode and isinstance(mpcode, list):
            mp_code_Str = "', '".join(mpcode)
            q = f"WHERE {mpcode_sql_name} in ('{mp_code_Str}') "

        elif partial_match_mpcode and isinstance(mpcode, str):
            mps = pd.read_sql_query(f"SELECT MpCode FROM {dbname}.mp", engine).values[:, 0]
            mpcode_match = mps[[mpcode in s for s in mps]]
            mp_code_Str = "', '".join(mpcode_match)
            q = f"WHERE {mpcode_sql_name} in ('{mp_code_Str}') "

        elif partial_match_mpcode and isinstance(mpcode, list):
            mps = pd.read_sql_query(f"SELECT MpCode FROM {dbname}.mp", engine).values[:, 0]
            mpcode_match = mps[[any(ss in s for ss in mpcode) for s in mps]]
            mp_code_Str = "', '".join(mpcode_match)
            q = f"WHERE {mpcode_sql_name} in ('{mp_code_Str}') "

        else:
            assert mpcode is None, "Unsupported mpcode type"
            pass

        return q


def get_daw_filters(
    mpcode=None,
    mv=True,
    betrouwbaarheid=False,
    filternr=None,
    partial_match_mpcode=True,
):
    """Retreive metadata of all filters. Takes 25 seconds."""

    q = (
        "SELECT * "
        "FROM "
        "   ("
        "   select "
        "       m0.MpCode AS FiltMpCode, "
        "       m0.Filtnr, "
        "       m0.Refpunt, "
        "       m0.Bk_filt, "
        "       m0.Ok_filt, "
        "       m0.Zandvang, "
        "       m0.Verval_datum, "
        "       m0.Wvp, "
        "       m0.Dia_filt, "
        "       m0.Sk_freq, "
        "       m0.Lab_code, "
        "       m0.TypeDm, "
        "       m0.Div_id, "
        "       m0.Div_boven_ref, "
        "       m0.Div_lucht, "
        "       m0.ImpDat, "
        "       m0.ValDat, "
        "       m0.ValMin, "
        "       m0.ValMax, "
        "       m0.ValOp, "
        "       m0.ValNeer, "
        "       m3.*, "
        "       m4.* "
        f"   from {dbname}.filters m0 "
        "   RIGHT JOIN "
        "       ("
        "       SELECT "
        "           m1.Filtrec, "
        "           m1.Datum as StygDatum, "
        "           m1.Tijd as StygTijd, "
        "           m1.Meting as StygMeting, "
        "           m1.Meting_Nap as StygMeting_Nap, "
        "           m1.Bron as StygBron, "
        "           m1.Druk_Water, "
        "           m1.Druk_Lucht, "
        "           m1.Druk_Cor, "
        "           m1.Temp "
        "       FROM "
        f"           {dbname}.stijghgt m1 "
        "       INNER JOIN "
        f"           (SELECT max(Recnum) as lastmsgId FROM {dbname}.stijghgt WHERE Meting > -80 GROUP BY Filtrec) m2 "
        "               ON m1.Recnum=m2.lastmsgId"
        "       ) m3 "
        "   on m3.Filtrec = m0.recnum "
        "   inner JOIN "
        f"       {dbname}.mp m4 "
        "       ON m4.mpcode = m0.MpCode "
        "   ) AS m6 "
    )

    if betrouwbaarheid:
        # removes filters that don't have betr value in last StygHgt value
        q += f"INNER JOIN {dbname}.StygBetr AS m5 ON m5.Recnum = m6.Recnum "

    if mv:
        # removes rows that don't have mv
        q += f"LEFT JOIN {dbname}.MpMv AS d on FiltMpCode = d.Mpcode "

    q += fuzzy_match_mpcode(
        mpcode=mpcode,
        partial_match_mpcode=partial_match_mpcode,
        mpcode_sql_name="FiltMpCode",
    )

    b = pd.read_sql_query(q, engine)
    b = b.loc[:, ~b.columns.duplicated()]
    b.sort_values(["MpCode", "Filtnr"], inplace=True)

    if filternr is not None:
        b = b.loc[b.Filtnr == float(filternr)]

    b.set_index("MpCode", inplace=True)
    get_daw_soort_mp(b)
    b = df2gdf(b)
    return b


def get_daw_boring(mpcode=None, join_with_mps=False):
    query = (
        f"select * from {dbname}.NenLaag "
        f"inner join {dbname}.NenNorm on {dbname}.NenLaag.Nencode = {dbname}.NenNorm.Code "
        f"left join {dbname}.NenToev on {dbname}.NenLaag.Recnum = {dbname}.NenToev.Nenlaagrec "
    )

    if mpcode is not None:
        query += f" WHERE MpCode='{mpcode}' "

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

    if mpcode is not None:
        query += f"WHERE e.MpCode='{mpcode}' "

    b = pd.read_sql_query(query, engine)
    del b["hydmpcode"]

    b["dikte"] = b.groupby("Mpcode")["Bk_pak"].transform(lambda x: x.diff().shift(-1))

    # remove layers that have 1 cm thickness minimal thickness dawaco
    b = b[np.logical_or(b["dikte"] > 0.01, pd.isna(b.dikte))]

    b["bkp_nap"] = -b["Bk_pak"] + b["Maaiveld"]
    b["okp_nap"] = b["bkp_nap"] - b["dikte"]

    # b.groupby('Mpcode')[['okp_nap', 'Maaiveld']].transform(lambda x: print(x))

    return b


def get_daw_soort_mp(a, key="Soort"):
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

    pass


def get_daw_meteo(statcode, mettype):
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


    Returns
    -------

    """
    valid_statcodes = [
        "017",
        "225",
        "226",
        "229",
        "234",
        "235",
        "235W",
        "240W",
        "257W",
        "435",
        "438",
        "454",
        "593",
        "BER PLUV",
        "CAS PLUV",
        "CAS1",
        "CAS3",
        "HMK",
        "LEI",
        "LIJNDEN",
        "LYS",
    ]
    valid_mettypes = [
        "Neerslag",
        "Temperatuur",
        "Temp. maximum",
        "Temp. minimum",
        "Verdamping",
    ]
    assert statcode in valid_statcodes, "not a valid statcode"
    assert mettype in valid_mettypes, "not a valid mettype"

    q = f"""
    SELECT metdet.datum, metdet.tijd, metdet.waarde , metpar.naam as mettype, metpar.eenheid, metpar.type_tot , metstat.code as statcode , metstat.naam as statnaam
    FROM {dbname}.metdet as metdet 
    INNER JOIN {dbname}.metpar as metpar on metdet.code_par = metpar.code_par
    INNER JOIN {dbname}.metstat as metstat on metdet.code = metstat.code 
    WHERE metdet.code = '{statcode}' and metpar.naam = '{mettype}'
    """
    b = pd.read_sql_query(q, engine)
    b.set_index(
        pd.to_datetime(b.datum.astype(str) + b.tijd, format="%Y-%m-%d%H:%M"),
        inplace=True,
    )
    b.drop(columns=["datum", "tijd"], inplace=True)

    return b


def get_daw_ts_stijghgt(mpcode=None, filternr=None):
    assert mpcode is not None and filternr is not None, "Define mpcode and filternr"

    query = f"""
    SELECT datum, tijd, meting_nap
    FROM {dbname}.Stijghgt
    INNER JOIN {dbname}.Filters on {dbname}.Filters.recnum = {dbname}.Stijghgt.filtrec
    WHERE Filters.mpcode = '{str(mpcode)}' and Filters.filtnr = '{str(filternr)}'
    ORDER BY datum, tijd"""

    b = pd.read_sql_query(query, engine)
    values = b["meting_nap"].values
    values[values < -60.0] = np.nan

    name = f"{str(mpcode)}_{str(filternr)}"

    if len(b) == 0:
        print(name + " does not have any validated water level measurements stored")

    out = pd.Series(
        data=values,
        index=pd.to_datetime(b.datum.astype(str) + b.tijd, format="%Y-%m-%d%H:%M"),
        name=name,
    )

    out = identify_data_gaps(out)

    return out


def get_daw_ts_temp(mpcode=None, filternr=None):
    assert mpcode is not None and filternr is not None, "Define mpcode and filternr"

    query = f"""
    SELECT datum, tijd, Temp
    FROM {dbname}.Stijghgt
    INNER JOIN {dbname}.Filters on {dbname}.Filters.recnum = {dbname}.Stijghgt.filtrec
    WHERE Filters.mpcode = '{str(mpcode)}' and Filters.filtnr = '{str(filternr)}'
    ORDER BY datum, tijd"""

    b = pd.read_sql_query(query, engine)
    values = b["Temp"].values
    values[values < -60.0] = np.nan
    values[values == 0.0] = np.nan

    name = f"{str(mpcode)}_{str(filternr)}"

    if len(b) == 0:
        print(name + " does not have any validated water level measurements stored")

    out = pd.Series(
        data=values,
        index=pd.to_datetime(b.datum.astype(str) + b.tijd, format="%Y-%m-%d%H:%M"),
        name=name,
    )

    out = identify_data_gaps(out)

    return out


def get_nlmod_ts_at_filter(fils, model_ds, heads_label="heads"):
    """Returns the heads at the filter height (shape: [ntime x nfilter])."""
    heads = model_ds[heads_label]
    x = fils.geometry.x.values
    y = fils.geometry.y.values
    icids = np.argmin(
        (model_ds.x.values[None] - x[:, None]) ** 2
        + (model_ds.y.values[None] - y[:, None]) ** 2,
        axis=1,
    )

    botm = model_ds.bot.assign_coords({"layer": np.arange(model_ds.layer.size)})
    mkfnap = fils.Refpunt - (fils.Bk_filt + fils.Ok_filt) / 2

    # Find nearest bottom of active cell that is below halfway filter.
    # Alternative approach would be to find the nearest cell center.
    ilays_active = [
        botm.isel(cid=icid)[model_ds.idomain.isel(cid=icid).values == 1][
            np.searchsorted(
                botm.isel(cid=icid)[model_ds.idomain.isel(cid=icid).values > 0] < zi,
                True,
            )
        ].layer.item()
        for icid, zi in zip(icids, mkfnap)
    ]
    return heads.values[:, ilays_active, icids]


def get_nlmod_vertical_profile(model_ds, x, y, label, active_only=True):
    """get vertical profile of model_ds[label] given global coordinates
    The returned array contains the [top_cell, bot_cell, value] for all active cells.
    Returned array has size (3, nlay_active)
    """
    icid = np.argmin((model_ds.x.values - x) ** 2 + (model_ds.y.values - y) ** 2)
    topbot = np.concatenate(
        (model_ds.top.isel(cid=icid).values[None], model_ds.bot.isel(cid=icid).values)
    )
    out = np.stack((topbot[:-1], topbot[1:], model_ds[label].isel(cid=icid).values))

    if active_only:
        ilay_active = model_ds.idomain.isel(cid=icid).values > 0
        return out[:, ilay_active]
    else:
        return out


def get_regis_ds(rds_x, rds_y, keys=None):
    regis_ds = xr.open_dataset("http://www.dinodata.nl:80/opendap/REGIS/REGIS.nc")
    dsi_r = regis_ds.isel(**x_to_ix(regis_ds, rds_x, rds_y))

    if keys is None:
        dsi_r2 = dsi_r.compute().sel(layer=~np.isnan(dsi_r.bottom))

    else:
        dsi_r2 = dsi_r[keys].compute().sel(layer=~np.isnan(dsi_r.bottom))

    return dsi_r2


def identify_data_gaps(series):
    """
    Add NaN's at places where data is expected

    instead of == maybe use isclose
    Parameters
    ----------
    series

    Returns
    -------

    """
    index, values = series.index, series.values
    dt = (index[1:] - index[:-1]).values

    iden = (
        (np.roll(dt, -2) == np.roll(dt, -1))
        & (np.roll(dt, 1) == np.roll(dt, 2))
        & (dt >= 2 * np.roll(dt, -1))
    )
    start, end, delta, delta_prev = (
        index[:-1][iden],
        index[1:][iden],
        dt[iden],
        np.roll(dt, -1)[iden],
    )

    out_index, out_values = index.copy(), values.copy()
    for si, ei, di, dpi in zip(start, end, delta, delta_prev):
        print(si, ei, di, dpi)
        t_insert = np.arange(si, ei, dpi)[1:]
        v_insert = np.full(t_insert.shape, np.nan, dtype=float)
        before_ind = np.argwhere(index == ei).item()
        out_index = np.insert(out_index, before_ind, t_insert)
        out_values = np.insert(out_values, before_ind, v_insert)

    return pd.Series(data=out_values, index=out_index, name=series.name)


def x_to_ix(ds, rds_x, rds_y):
    ix, iy = np.argmin((ds.x - rds_x).values ** 2), np.argmin(
        (ds.y - rds_y).values ** 2
    )
    return dict(x=ix, y=iy)
