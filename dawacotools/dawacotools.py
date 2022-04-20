import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyodbc
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.patches import Polygon


from .colors import tno_colors, boorlegenda_dawaco


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
    """Retreive metadata of all monitoring wells. Takes 5 seconds."""

    q = "SELECT * FROM guest.mp"
    b = pd.read_sql_query(q, con)
    b.set_index('MpCode', inplace=True)

    get_soort_mp(b)
    b = df2gdf(b)
    return b


def get_daw_filters(mpcode=None, mv=True, betrouwbaarheid=False):
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

    get_soort_mp(b)
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


def get_soort_mp(a, key='Soort'):
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


def plot_dawaco_triwaco(df, ax, zlim=-60):
    if len(df) == 0:
        return

    d = df.copy()


    d['okp_nap'].fillna(-999., inplace=True)

    ax.xaxis.set_visible(False)
    patches_lay = []

    for _, lay in d.iterrows():
        top = lay.bkp_nap
        bottom = lay.okp_nap

        if top < zlim:
            continue

        if lay.Type_pak == 'S':
            c = (0, 146 / 255, 0)
        else:
            c = [i / 255 for i in (243, 225, 6)]

        patches_lay.append(
            Polygon(
                [(0, float(bottom)),
                 (1, float(bottom)),
                 (1, float(top)),
                 (0, float(top))],
                facecolor=c))
        textstr = lay.Type_pak + ' ' + str(lay.Num_pak)
        ax.text(0.5, (top + max(bottom, zlim)) / 2, textstr, fontsize=6,
                verticalalignment='center', ha='center')

    ax.add_collection(PatchCollection(patches_lay, match_original=True, edgecolors='none'))
    ax.set_ylim((zlim, lay.Maaiveld))
    ax.set_title('Triwaco')
    pass


def plot_dawaco_boring(dfi, ax):
    if len(dfi) == 0:
        return

    legend_handles = []
    legend_names = []

    for ili, li in dfi.iterrows():
        top = li['Maaiveld (m NAP)'] - li['Van (m-Mv)']  # m+NAP
        bottom = li['Maaiveld (m NAP)'] - li['Tot (m-Mv)']  # m+NAP
        ncomp = len(li.Boorcode)

        if ncomp % 2:
            # 'Boorcode ontbreekt grof/fijn indicatie'
            ax.add_patch(
                Polygon(
                    [(0, bottom),
                     (1, bottom),
                     (1, top),
                     (0, top)],
                    facecolor='red'))
            continue

        if ncomp / 2 == 1:
            breedten = [0, 1]
        elif ncomp / 2 == 2:
            breedten = [0, 0.75, 1]
        elif ncomp / 2 == 3:
            breedten = [0, 0.5, 0.75, 1]
        elif ncomp / 2 == 4:
            breedten = [0, 0.4, 0.6, 0.8, 1]
        else:
            print('Error! with', li.Boorcode)

        for code, b1, b2 in zip([li.Boorcode[i:i + 2] for i in range(0, ncomp, 2)],
                                breedten[:-1],
                                breedten[1:]):
            if code[1] == '-':
                igroffijn = boorlegenda_dawaco[code[0]]['idefault']
            else:
                igroffijn = int(code[1])

            hatch = boorlegenda_dawaco[code[0]]['hatch']
            lw = boorlegenda_dawaco[code[0]]['lw'][igroffijn]
            fc = [i / 255 for i in boorlegenda_dawaco[code[0]]['fc'][igroffijn]]

            with plt.rc_context({'hatch.linewidth': lw**3}):
                ph = ax.add_patch(
                    Polygon(
                        [(b1, bottom),
                         (b2, bottom),
                         (b2, top),
                         (b1, top)],
                        fill=True,
                        fc=fc,
                        hatch=hatch,
                        linewidth=0.0001))
                legend_handles.append(ph)
                legend_names.append(code)

    ax.xaxis.set_visible(False)
    ax.set_ylim([bottom, li['Maaiveld (m NAP)']])
    legend_names_uniq, uniq_arg = np.unique(legend_names, return_index=True)
    ax.legend([legend_handles[i] for i in uniq_arg], legend_names_uniq, loc='lower left')
    ax.set_title(dfi['Meetpuntcode'].iloc[0])
    pass


def plot_regis_lay(dsi_r2, ax, zlim=-60):
    ax.xaxis.set_visible(False)
    patches_lay = []

    # iterate over the layers
    for ilayer, name_bytes in enumerate(dsi_r2.layer.data):
        ri = dsi_r2.isel(layer=ilayer)

        if ri.top < zlim:
            continue

        name = name_bytes.decode("utf-8")
        c = [i / 255 for i in tno_colors[name]]

        patches_lay.append(
            Polygon(
                [(0, float(ri.bottom)),
                 (1, float(ri.bottom)),
                 (1, float(ri.top)),
                 (0, float(ri.top))],
                facecolor=c,
                label=name))

    ax.add_collection(PatchCollection(patches_lay, match_original=True, edgecolors='none'))
    ax.set_ylim((zlim, dsi_r2.top.max()))
    ax.legend(handles=patches_lay, loc='lower left')
    ax.set_title('REGIS v2.2')
    pass


def plot_regis_kh(dsi_r2, ax, zlim=-60):
    patches_kh = []
    lines_kh = []

    # iterate over the layers
    for ilayer, name_bytes in enumerate(dsi_r2.layer.data):
        ri = dsi_r2.isel(layer=ilayer)

        if ri.top < zlim:
            continue

        name = name_bytes.decode("utf-8")
        c = [i / 255 for i in tno_colors[name]]

        # Kh
        patches_kh.append(
            Polygon(
                [(float(ri.kh - ri.sdh), float(ri.bottom)),
                 (float(ri.kh + ri.sdh), float(ri.bottom)),
                 (float(ri.kh + ri.sdh), float(ri.top)),
                 (float(ri.kh - ri.sdh), float(ri.top))],
                facecolor=c,
                label=name))
        lines_kh.append(([float(ri.kh), float(ri.top)],
                         [float(ri.kh), float(ri.bottom)]))

    ax.add_collection(PatchCollection(patches_kh, match_original=True, edgecolors='none'))
    ax.add_collection(LineCollection(lines_kh, color='black', linewidth=0.8))
    ax.set_xlim((0.1, float(dsi_r2.kh.max()) + float(dsi_r2.sdh.max())))
    ax.set_title('REGIS Kh (m/d)')
    pass


def plot_regis_kv(dsi_r2, ax, zlim=-60):
    patches_kv = []
    lines_kv = []

    # iterate over the layers
    for ilayer, name_bytes in enumerate(dsi_r2.layer.data):
        ri = dsi_r2.isel(layer=ilayer)

        if ri.top < zlim:
            continue

        name = name_bytes.decode("utf-8")
        c = [i / 255 for i in tno_colors[name]]

        # Kv
        patches_kv.append(
            Polygon(
                [(float(ri.kv - ri.sdv), float(ri.bottom)),
                 (float(ri.kv + ri.sdv), float(ri.bottom)),
                 (float(ri.kv + ri.sdv), float(ri.top)),
                 (float(ri.kv - ri.sdv), float(ri.top))],
                facecolor=c,
                label=name))
        lines_kv.append(([float(ri.kv), float(ri.top)],
                         [float(ri.kv), float(ri.bottom)]))

    ax.add_collection(PatchCollection(patches_kv, match_original=True, edgecolors='none'))
    ax.add_collection(LineCollection(lines_kv, color='black', linewidth=0.8))
    ax.set_xlim((0.001, float(dsi_r2.kv.max()) + float(dsi_r2.sdv.max())))
    ax.set_title('REGIS Kv (m/d)')
    pass
