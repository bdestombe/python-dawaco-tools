import geopandas as gpd
import numpy as np
import pandas as pd
import pyodbc

con = pyodbc.connect(r"Driver={SQL Server};"
                     r"Server=IN_PW_P03;"  # Deze server zou het best moeten werken
                     r"Database=dawacoprod;"
                     r"Trusted_Connection=yes;")


def df2gdf(df):
    df = df.loc[:, ~df.columns.duplicated()].copy()
    geom = gpd.points_from_xy(df.Xcoor, df.Ycoor, crs="EPSG:28992")
    gdf = gpd.GeoDataFrame(df, geometry=geom)
    return gdf


def get_daw_mps():
    """Retreive metadata of all wells. Takes 5 seconds."""

    q = "SELECT * FROM guest.mp"
    b = pd.read_sql_query(q, con)
    b.set_index('MpCode', inplace=True)

    get_daw_soort_mp(b)
    b = df2gdf(b)
    return b


def get_daw_filters(mpcode=None, mv=True, betrouwbaarheid=False, filternr=None):
    """Retreive metadata of all filters. Takes 25 seconds."""

    q = "SELECT * " \
        "FROM " \
        "   (" \
        "   select " \
        "       m0.MpCode AS FiltMpCode, " \
        "       m0.Filtnr, " \
        "       m0.Refpunt, " \
        "       m0.Bk_filt, " \
        "       m0.Ok_filt, " \
        "       m0.Zandvang, " \
        "       m0.Verval_datum, " \
        "       m0.Wvp, " \
        "       m0.Dia_filt, " \
        "       m0.Sk_freq, " \
        "       m0.Lab_code, " \
        "       m0.TypeDm, " \
        "       m0.Div_id, " \
        "       m0.Div_boven_ref, " \
        "       m0.Div_lucht, " \
        "       m0.ImpDat, " \
        "       m0.ValDat, " \
        "       m0.ValMin, " \
        "       m0.ValMax, " \
        "       m0.ValOp, " \
        "       m0.ValNeer, " \
        "       m3.*, " \
        "       m4.* " \
        "   from guest.filters m0 " \
        "   RIGHT JOIN " \
        "       (" \
        "       SELECT " \
        "           m1.Filtrec, " \
        "           m1.Datum as StygDatum, " \
        "           m1.Tijd as StygTijd, " \
        "           m1.Meting as StygMeting, " \
        "           m1.Meting_Nap as StygMeting_Nap, " \
        "           m1.Bron as StygBron, " \
        "           m1.Druk_Water, " \
        "           m1.Druk_Lucht, " \
        "           m1.Druk_Cor, " \
        "           m1.Temp " \
        "       FROM " \
        "           guest.stijghgt m1 " \
        "       INNER JOIN " \
        "           (SELECT max(Recnum) as lastmsgId FROM guest.stijghgt WHERE Meting > -80 GROUP BY Filtrec) m2 " \
        "               ON m1.Recnum=m2.lastmsgId" \
        "       ) m3 " \
        "   on m3.Filtrec = m0.recnum " \
        "   inner JOIN " \
        "       guest.mp m4 " \
        "       ON m4.mpcode = m0.MpCode " \
        "   ) AS m6 "

    if betrouwbaarheid:
        # removes filters that don't have betr value in last StygHgt value
        q += "INNER JOIN " \
            "   guest.StygBetr AS m5 " \
            "   ON m5.Recnum = m6.Recnum "

    if mv:
        # removes rows that don't have mv
        q += "LEFT JOIN " \
            "   guest.MpMv AS d " \
            "   on FiltMpCode = d.Mpcode "

    if mpcode is not None:
        if isinstance(mpcode, list):
            mp_code_Str = "', '".join(mpcode)
            q += f"WHERE FiltMpCode=('{mp_code_Str}') "
        else:
            q += f"WHERE FiltMpCode='{mpcode}' "

    b = pd.read_sql_query(q, con)
    b = b.loc[:, ~b.columns.duplicated()]
    b.sort_values(['MpCode', 'Filtnr'], inplace=True)

    if filternr is not None:
        b = b.loc[b.Filtnr == float(filternr)]

    get_daw_soort_mp(b)
    b = df2gdf(b)
    return b


def get_daw_boring(mpcode):
    query = "select * from guest.NenLaag " \
            "inner join guest.NenNorm on guest.NenLaag.Nencode = guest.NenNorm.Code " \
            "left join guest.NenToev on guest.NenLaag.Recnum = guest.NenToev.Nenlaagrec "

    if mpcode != 'all':
        query += f"WHERE MpCode='{mpcode}' "

    b = pd.read_sql_query(query, con)
    return b


def get_daw_triwaco(mpcode=None):
    query = "select e.Mpcode as hydmpcode, e.Bk_pak, e.Type_pak, e.Num_pak, " \
            "d.Mpcode, d.Maaiveld from guest.HydStrat e " \
            "inner join guest.MpMv d on e.MpCode = d.Mpcode "

    if mpcode is not None:
        query += f"WHERE e.MpCode='{mpcode}' "

    b = pd.read_sql_query(query, con)
    del b['hydmpcode']

    b['dikte'] = b.groupby('Mpcode')['Bk_pak'].transform(lambda x: x.diff().shift(-1))

    # remove layers that have 1 cm thickness minimal thickness dawaco
    b = b[np.logical_or(b['dikte'] > 0.01, pd.isna(b.dikte))]

    b['bkp_nap'] = - b['Bk_pak'] + b['Maaiveld']
    b['okp_nap'] = b['bkp_nap'] - b['dikte']

    # b.groupby('Mpcode')[['okp_nap', 'Maaiveld']].transform(lambda x: print(x))

    return b


def get_daw_soort_mp(a, key='Soort'):
    sd = {
        1: 'Waarnemingspunt',
        2: 'Pompput',
        3: 'Infiltratieput',
        5: 'Opp.water meetpunt',
        6: 'Monsterpunt'
    }
    for k, v in sd.items():
        a.loc[a[key] == k, key] = v
        a.loc[a[key] == str(k), key] = v

    pass


def get_daw_ts_stijghgt(mpcode=None, filternr=None):
    query = f'''
    SELECT datum, tijd, meting_nap
    FROM guest.Stijghgt
    INNER JOIN guest.Filters on guest.Filters.recnum = guest.Stijghgt.filtrec
    WHERE Filters.mpcode = '{str(mpcode)}' and Filters.filtnr = '{str(filternr)}'
    ORDER BY datum, tijd'''

    b = pd.read_sql_query(query, con)
    values = b['meting_nap'].values
    values[values < -60.] = np.nan

    name = f'{str(mpcode)}_{str(filternr)}'

    assert len(b) > 0, name + ' does not have any validated water level measurements stored'

    out = pd.Series(
        data=values,
        index=pd.to_datetime(b.datum + b.tijd, format='%Y-%m-%d%H:%M'),
        name=name)

    return out


def get_nlmod_da(fils, model_ds, heads_label='heads'):
    """Returns the heads at the filter height (shape: [ntime x nfilter])."""
    heads = model_ds[heads_label]
    x = fils.geometry.x.values
    y = fils.geometry.y.values
    icids = np.argmin((model_ds.x.values[None] - x[:, None]) ** 2 +
                      (model_ds.y.values[None] - y[:, None]) ** 2, axis=1)

    botm = model_ds.bot.assign_coords({'layer': np.arange(model_ds.layer.size)})
    mkfnap = fils.Refpunt - (fils.Bk_filt + fils.Ok_filt) / 2

    # Find nearest bottom of active cell that is below halfway filter.
    # Alternative approach would be to find the nearest cell center.
    ilays_active = [
        botm.isel(cid=icid)[
            model_ds.idomain.isel(cid=icid).values == 1][
            np.searchsorted(botm.isel(cid=icid)[
                                model_ds.idomain.isel(cid=icid).values == 1] < zi, True)].layer.item()
        for icid, zi in zip(icids, mkfnap)]
    return heads.values[:, ilays_active, icids]
