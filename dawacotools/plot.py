import datetime
import locale

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection, LineCollection
import matplotlib.dates as dates
from matplotlib.patches import Polygon
import xarray as xr

from .colors import tno_colors, boorlegenda_dawaco
from .io import df2gdf
from .io import get_daw_boring
from .io import get_daw_mon_dates
from .io import get_daw_ts_stijghgt
from .io import get_daw_filters
from .io import get_daw_meteo_from_loc
from .io import get_daw_mps
from .io import get_nlmod_vertical_profile
from .io import get_regis_ds

locale.setlocale(locale.LC_ALL, 'nl_NL')

def plot_daw_triwaco(df, ax, zlim=-60):
    if len(df) == 0:
        return

    d = df.copy()

    d["okp_nap"].fillna(-999.0, inplace=True)

    ax.xaxis.set_visible(False)
    patches_lay = []

    for _, lay in d.iterrows():
        top = lay.bkp_nap
        bottom = lay.okp_nap

        if top < zlim:
            continue

        if lay.Type_pak == "S":
            c = (0, 146 / 255, 0)
        else:
            c = [i / 255 for i in (243, 225, 6)]

        patches_lay.append(
            Polygon(
                [
                    (0, float(bottom)),
                    (1, float(bottom)),
                    (1, float(top)),
                    (0, float(top)),
                ],
                facecolor=c,
            )
        )
        textstr = lay.Type_pak + " " + str(lay.Num_pak)
        ax.text(
            0.5,
            (top + max(bottom, zlim)) / 2,
            textstr,
            fontsize=6,
            verticalalignment="center",
            ha="center",
        )

    ax.add_collection(
        PatchCollection(patches_lay, match_original=True, edgecolors="none")
    )
    ax.set_ylim((zlim, lay.Maaiveld))
    ax.set_title("Triwaco")

    pass


def plot_daw_boring(dfi, ax):
    if len(dfi) == 0:
        return
    
    assert 'Maaiveld' in dfi, 'Obtain dfi with get_daw_boring using join_with_mps=True'

    legend_handles = []
    legend_names = []

    for ili, li in dfi.iterrows():
        top = li["Maaiveld"] - li["Van"]  # m+NAP
        bottom = li["Maaiveld"] - li["Tot"]  # m+NAP
        ncomp = len(li.Nencode)

        if li.Nencode == "NBE":
            # Niet benoemd
            ph = ax.add_patch(
                Polygon(
                    [(0, bottom), (1, bottom), (1, top), (0, top)], facecolor="purple"
                )
            )
            legend_handles.append(ph)
            legend_names.append("Niet bepaald")
            continue

        if ncomp % 2:
            # 'Boorcode ontbreekt grof/fijn indicatie'
            print("Unable to process " + li.Nencode + ". Missing grof/fijn indicatie.")
            ph = ax.add_patch(
                Polygon([(0, bottom), (1, bottom), (1, top), (0, top)], facecolor="red")
            )
            legend_handles.append(ph)
            legend_names.append("Niet verwerkt")
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
            print("Unable to process " + li.Nencode + ". Too many compounds.")
            ph = ax.add_patch(
                Polygon([(0, bottom), (1, bottom), (1, top), (0, top)], facecolor="red")
            )
            legend_handles.append(ph)
            legend_names.append("Niet verwerkt")
            continue

        for code, b1, b2 in zip(
            [li.Nencode[i : i + 2] for i in range(0, ncomp, 2)],
            breedten[:-1],
            breedten[1:],
        ):
            try:
                if code[1] == "-":
                    igroffijn = boorlegenda_dawaco[code[0]]["idefault"]
                else:
                    igroffijn = int(code[1])

                hatch = boorlegenda_dawaco[code[0]]["hatch"]
                lw = boorlegenda_dawaco[code[0]]["lw"][igroffijn]
                fc = [i / 255 for i in boorlegenda_dawaco[code[0]]["fc"][igroffijn]]

                with plt.rc_context({"hatch.linewidth": lw**3}):
                    ph = ax.add_patch(
                        Polygon(
                            [(b1, bottom), (b2, bottom), (b2, top), (b1, top)],
                            fill=True,
                            fc=fc,
                            hatch=hatch,
                            linewidth=0.0001,
                        )
                    )
                    legend_handles.append(ph)
                    legend_names.append(code)
            except:
                print(
                    "Unable to process "
                    + li.Nencode
                    + ". Most likely a weird compound abbrev."
                )
                ph = ax.add_patch(
                    Polygon(
                        [(0, bottom), (1, bottom), (1, top), (0, top)], facecolor="red"
                    )
                )
                legend_handles.append(ph)
                legend_names.append("Niet verwerkt")
                continue

    ax.xaxis.set_visible(False)
    ax.set_ylim([bottom, li["Maaiveld"]])
    legend_names_uniq, uniq_arg = np.unique(legend_names, return_index=True)
    ax.legend(
        [legend_handles[i] for i in uniq_arg], legend_names_uniq, loc="lower left"
    )
    ax.set_title("Boring")
    pass


def plot_nlmod_k(xcoord, ycoord, fp_model_ds, ax, zlim=None):
    model_ds = xr.open_dataset(fp_model_ds)
    
    iicell2d_nearest = np.argmin((model_ds.x.values - xcoord) ** 2 + (model_ds.y.values - ycoord) ** 2)
    idomain_nearest = model_ds.idomain.isel(icell2d=iicell2d_nearest).values
    
    kh_nearest = model_ds.kh.isel(icell2d=iicell2d_nearest).values
    kh_nearest[idomain_nearest == 0] = 0.
    kh_nearest[idomain_nearest < 0] = np.nan
    kv_nearest = model_ds.kv.isel(icell2d=iicell2d_nearest).values
    kv_nearest[idomain_nearest == 0] = 0.
    kv_nearest[idomain_nearest < 0] = np.nan
    
    top_nearest = model_ds.top.isel(icell2d=iicell2d_nearest).values
    botm_nearest = model_ds.botm.isel(icell2d=iicell2d_nearest).values
    tops = np.concatenate(([top_nearest], botm_nearest[:-1]))[~np.isnan(kh_nearest)]
    botms = botm_nearest[~np.isnan(kh_nearest)]

    y_k = np.array([item for sublist in zip(tops, botms) for item in sublist])
    x_kh = np.repeat(kh_nearest[~np.isnan(kh_nearest)], 2)
    x_kv = np.repeat(kv_nearest[~np.isnan(kv_nearest)], 2)

    labels = model_ds.layer[~np.isnan(kh_nearest)]
    x_label = (x_kh[::2] + x_kv[1::2]) / 2
    y_label = (y_k[::2] + y_k[1::2]) / 2

    for li, xi, yi in zip(labels, x_label, y_label):
        ax.annotate(
            li.item(),
            (xi, yi),
            ha="center",
            va="center",
            textcoords="offset points",
            xytext=(0, 0),
            size=8,
        )

    ax.plot(x_kh, y_k, c='C0', ls='-')
    ax.set_xlabel('Kv (m/dag; blauw)')
    ax.set_ylabel('mNAP')
    ax2 = ax.twiny()
    ax2.plot(x_kv, y_k, c='C1', ls='-.')
    ax2.set_xlabel('Kv (m/dag; oranje)')
    
    if zlim is not None:
        ax.set_ylim(zlim)
        
    pass


def plot_daw_filters(filters, ax, linewidth_buis=5, linewidth_filter=10):
    xlim = ax.get_xlim()

    dx = 1 / (len(filters) + 1) * (xlim[1] - xlim[0])

    for irow, (mpcode, row) in enumerate(filters.iterrows()):
        x = (irow + 1) * dx + xlim[0]

        ax.plot([x, x], [row.Maaiveld, row.Refpunt - row.Ok_filt], c='k', linewidth=linewidth_buis)
        ax.plot([x, x], [row.StygMeting_Nap, row.Refpunt - row.Ok_filt], c='lightblue', linewidth=linewidth_buis / 2)
        ax.plot([x, x], [row.Refpunt - row.Ok_filt, row.Refpunt - row.Bk_filt], c='C' + str(irow), linewidth=linewidth_filter)

        ax.annotate(
            f"F{row.Filtnr:.0f}",
            (x, row.Refpunt - (row.Bk_filt + row.Ok_filt) / 2),
            ha="center",
            va="center",
            textcoords="offset points",
            xytext=(0, 0),
            size=8,
        )
        
    pass


def plot_daw_mp_map(
        mps,
        ax=None,
        limit_mps_to_extent=False,
        soort=None,
        annotate_mpcode=True,
        marker=None,
        color="k",
        text_dict=None,
        **kwargs
):
    mps = (
        mps.reset_index().groupby("MpCode").agg(lambda x: x.iloc[0])
    )  # for multiple occurence of mpcode
    mps = df2gdf(mps)

    if soort is not None:
        mpssel = mps[mps.Soort == soort]
    else:
        mpssel = mps

    if ax is not None and limit_mps_to_extent:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        mpssel = mpssel.cx[xmin:xmax, ymin:ymax]

    if marker is None:
        marker = {
            'Waarnemingspunt': "o",
            'Pompput': "X",
            'Opp.water meetpunt': "^",
            'Monsterpunt': "s",
            '4': "d",
            'Infiltratieput': "+"
        }

    for soort_iter in mpssel.Soort.unique():
        m = marker[soort_iter]
        ax = mpssel.plot(marker=m, ax=ax, color=color, label=soort_iter, **kwargs)

    if annotate_mpcode:
        for mpcode, x, y in zip(mpssel.index, mpssel.geometry.x, mpssel.geometry.y):
            mp_label = mpcode[4:]

            if text_dict is not None and mpcode in text_dict:
                mp_label += text_dict[mpcode]

            ax.annotate(
                mp_label,
                (x, y),
                ha="center",
                va="bottom",
                textcoords="offset points",
                xytext=(0, 2),
                size=6,
            )
    return ax


def plot_daw_map_gws(filters, vkey='val', vmin=-1., vmax=1., ax=None, colormap='viridis'):
    gwss = [get_daw_ts_stijghgt(mpcode=mpcode, filternr=filter.Filtnr) for mpcode, filter in filters.iterrows()]
    gwss = [gws['2017-01-01':] for gws in gwss if gws['2017-01-01':].size > 10]
    gwsmeds = {gws.name: gws.median() for gws in gwss}
    filtmeds = filters.loc[gwsmeds.keys()]
    filtmeds['gwsmed'] = gwsmeds.values()
    h = filtmeds.plot.scatter(x='Xcoor', y='Ycoor', c='gwsmed', colormap=colormap, vmin=vmin, vmax=vmax)
    return filtmeds, h


def plot_nlmod_vertical_profile(
    model_ds, ax, x, y, label, mark_inactive=True, **line_plot_kwargs
):
    data = get_nlmod_vertical_profile(model_ds, x, y, label, active_only=True)
    yplot = data[:2].T.reshape(-1)
    xplot = data[2].repeat(2)
    ax.plot(xplot, yplot, label=label, **line_plot_kwargs)
    ax.set_xlim((-xplot.max() / 50, xplot.max() * 1.02))

    # mark inactive
    if mark_inactive:
        data = get_nlmod_vertical_profile(model_ds, x, y, label, active_only=False)
        icid = np.argmin((model_ds.x.values - x) ** 2 + (model_ds.y.values - y) ** 2)
        ilay_inactive = model_ds.idomain.isel(cid=icid).values < 1

        for top, bot in data[:2, ilay_inactive].T:
            ax.axhspan(bot, top, color=(1, 0.5, 0.5, 1), linewidth=0)


def plot_regis_lay(rds_x, rds_y, ax, zlim=-60):
    keys = ["layer", "bottom", "top"]
    dsi_r2 = get_regis_ds(rds_x, rds_y, keys=keys)

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
                [
                    (0, float(ri.bottom)),
                    (1, float(ri.bottom)),
                    (1, float(ri.top)),
                    (0, float(ri.top)),
                ],
                facecolor=c,
                label=name,
            )
        )

    ax.add_collection(
        PatchCollection(patches_lay, match_original=True, edgecolors="none")
    )
    ax.set_ylim((zlim, dsi_r2.top.max()))
    ax.legend(handles=patches_lay, loc="lower left")
    ax.set_title("REGIS v2.2")
    pass


def plot_daw_mp(mpcode, radius_plot_near_gws=None, fp_model_ds=None, extent_map=None, dy_map=50.):
    fig = plt.figure(figsize=(30, 20))
    grid = plt.GridSpec(3, 3, hspace=0.1, wspace=0.1, width_ratios=[10, 1, 1], height_ratios=[1, 1, 1], left=0.05,
                        right=0.95, top=0.95, bottom=0.05)
    ax_ts_gws = fig.add_subplot(grid[1, 0], xticklabels=[])
    ax_ts_meteo = fig.add_subplot(grid[2, 0])

    ax_bor = fig.add_subplot(grid[1:3, 1], xticklabels=[])
    ax_triw = fig.add_subplot(grid[1:3, 2])

    ax_map = fig.add_subplot(grid[0, 0:3])

    # gather data
    filters = get_daw_filters(mpcode)
    x, y, mv = filters.loc[filters.index == mpcode][['Xcoor', 'Ycoor', 'Maaiveld']].values[0]

    ax_map.scatter(x, y, s=12, c='red', marker='*', zorder=99, label=mpcode)

    # plot soils columns
    df_bor = get_daw_boring(mpcode=mpcode, join_with_mps=True)
    # df_bor = df_bors.loc[df_bors.index == mpcode]
    z_botm = min(mv - df_bor.Tot.max(), mv - filters.Ok_filt.max()) - 0.5
    z_top = mv + 0.5

    plot_daw_boring(df_bor, ax_bor)
    ax_bor.set_ylim((z_botm, z_top))

    if fp_model_ds is None:
        df_triw = df_triws.loc[df_triws.index == mpcode]
        plot_daw_triwaco(df_triw, ax_triw, zlim=(z_botm, z_top))
    else:
        plot_nlmod_k(x, y, fp_model_ds, ax_triw, zlim=(z_botm, z_top))

    # plot map
    if extent_map is None:
        # ax_map.axis('equal')
        aspect = ax_map.get_data_ratio()
        extent_map = [x - dy_map * aspect, x + dy_map * aspect, y - dy_map, y + dy_map]

    # ahn_file = nlmod.read.ahn.get_ahn_within_extent(extent_map)
    # with ahn_file.open() as dataset:
    #     show(dataset, ax=ax_map, cmap='gist_earth', label=None)

    mps_map = get_daw_mps().cx[extent_map[0]:extent_map[1], extent_map[2]:extent_map[3]]

    plot_daw_mp_map(
        mps_map,
        ax=ax_map,
        limit_mps_to_extent=False,
        soort=None,
        annotate_mpcode=True,
        marker=None,
        color="k",
        text_dict=None,
    )

    ax_map.legend(fontsize=6)
    ax_map.set_xlim(extent_map[:2])
    ax_map.set_ylim(extent_map[2:])

    # plot gws ts
    plot_daw_filters(filters, ax_bor)

    if radius_plot_near_gws is not None:
        mps_nears = get_daw_mps().cx[x - radius_plot_near_gws:x + radius_plot_near_gws, y - radius_plot_near_gws:y + radius_plot_near_gws]
        for mpcode_near, mp in mps_nears.iterrows():
            for filternr in range(1, int(mp.Aant_Fil) + 1):
                label = f'{mpcode_near}-F{str(filternr)}'
                gws = get_daw_ts_stijghgt(mpcode=mpcode_near, filternr=filternr)
                gws.plot(ax=ax_ts_gws, label=label, linewidth=0.7)

                mon_dates = get_daw_mon_dates(mpcode=mpcode_near, filternr=filternr)

                if len(mon_dates) > 0:
                    ax_ts_gws.plot([], [], linewidth=0.8, color='lightgrey', label='Monstername')

                    for mon_date in mon_dates:
                        ax_ts_gws.axvline(mon_date, linewidth=1.6, color='white', alpha=0.7)
                        ax_ts_gws.axvline(mon_date, linewidth=0.8, color='lightgrey')

    ax_ts_gws.legend(fontsize='x-small')

    # plot meteo
    tmin, tmax = ax_ts_gws.get_xlim()
    plot_knmi_meteo(ax_ts_meteo, x, y, tmin=tmin, tmax=tmax)

    return fig


def plot_knmi_meteo(ax_ts_meteo, x, y, tmin=None, tmax=None):
    tmin_range, tmax_range = dates.num2date(tmin), dates.num2date(tmax)
    tmin_range, tmax_range = datetime.datetime(tmin_range.year, tmin_range.month, tmin_range.day), datetime.datetime(tmax_range.year, tmax_range.month, tmax_range.day)
    N = get_meteo_from_loc(x=x, y=y, mettype='Neerslag', start_date=tmin_range, end_date=tmax_range)[0]
    V = get_meteo_from_loc(x=x, y=y, mettype='Verdamping', start_date=tmin_range, end_date=tmax_range)[0]
    N.plot(ax=ax_ts_meteo)
    V.plot(ax=ax_ts_meteo)
    ax_ts_meteo.legend(fontsize=6)
    ax_ts_meteo.set_xlim([tmin, tmax])


def plot_regis_kh(rds_x, rds_y, ax, zlim=-60):
    keys = ["kh", "sdh", "bottom", "top"]
    dsi_r2 = get_regis_ds(rds_x, rds_y, keys=keys)

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
                [
                    (float(ri.kh - ri.sdh), float(ri.bottom)),
                    (float(ri.kh + ri.sdh), float(ri.bottom)),
                    (float(ri.kh + ri.sdh), float(ri.top)),
                    (float(ri.kh - ri.sdh), float(ri.top)),
                ],
                facecolor=c,
                label=name,
            )
        )
        lines_kh.append(
            ([float(ri.kh), float(ri.top)], [float(ri.kh), float(ri.bottom)])
        )

    ax.add_collection(
        PatchCollection(patches_kh, match_original=True, edgecolors="none")
    )
    ax.add_collection(LineCollection(lines_kh, color="black", linewidth=0.8))
    ax.set_xlim((0.1, float(dsi_r2.kh.max()) + float(dsi_r2.sdh.max())))
    ax.set_title("REGIS Kh (m/d)")
    pass


def plot_regis_kv(rds_x, rds_y, ax, zlim=-60):
    keys = ["kv", "sdv", "bottom", "top"]
    dsi_r2 = get_regis_ds(rds_x, rds_y, keys=keys)

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
                [
                    (float(ri.kv - ri.sdv), float(ri.bottom)),
                    (float(ri.kv + ri.sdv), float(ri.bottom)),
                    (float(ri.kv + ri.sdv), float(ri.top)),
                    (float(ri.kv - ri.sdv), float(ri.top)),
                ],
                facecolor=c,
                label=name,
            )
        )
        lines_kv.append(
            ([float(ri.kv), float(ri.top)], [float(ri.kv), float(ri.bottom)])
        )

    ax.add_collection(
        PatchCollection(patches_kv, match_original=True, edgecolors="none")
    )
    ax.add_collection(LineCollection(lines_kv, color="black", linewidth=0.8))
    ax.set_xlim((0.001, float(dsi_r2.kv.max()) + float(dsi_r2.sdv.max())))
    ax.set_title("REGIS Kv (m/d)")
    pass
