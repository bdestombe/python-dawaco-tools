import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.patches import Polygon

from .colors import tno_colors, boorlegenda_dawaco
from .io import df2gdf
from .io import get_nlmod_vertical_profile
from .io import get_regis_ds


def plot_daw_triwaco(df, ax, zlim=-60):
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


def plot_daw_boring(dfi, ax):
    if len(dfi) == 0:
        return

    legend_handles = []
    legend_names = []

    for ili, li in dfi.iterrows():
        top = li['Maaiveld'] - li['Van']  # m+NAP
        bottom = li['Maaiveld'] - li['Tot']  # m+NAP
        ncomp = len(li.Nencode)

        if li.Nencode == 'NBE':
            # Niet benoemd
            ph = ax.add_patch(
                Polygon(
                    [(0, bottom),
                     (1, bottom),
                     (1, top),
                     (0, top)],
                    facecolor='purple'))
            legend_handles.append(ph)
            legend_names.append('Niet bepaald')
            continue

        if ncomp % 2:
            # 'Boorcode ontbreekt grof/fijn indicatie'
            print('Unable to process ' + li.Nencode + '. Missing grof/fijn indicatie.')
            ph = ax.add_patch(
                Polygon(
                    [(0, bottom),
                     (1, bottom),
                     (1, top),
                     (0, top)],
                    facecolor='red'))
            legend_handles.append(ph)
            legend_names.append('Niet verwerkt')
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
            print('Unable to process ' + li.Nencode + '. Too many compounds.')
            ph = ax.add_patch(
                Polygon(
                    [(0, bottom),
                     (1, bottom),
                     (1, top),
                     (0, top)],
                    facecolor='red'))
            legend_handles.append(ph)
            legend_names.append('Niet verwerkt')
            continue

        for code, b1, b2 in zip([li.Nencode[i:i + 2] for i in range(0, ncomp, 2)],
                                breedten[:-1],
                                breedten[1:]):
            try:
                if code[1] == '-':
                    igroffijn = boorlegenda_dawaco[code[0]]['idefault']
                else:
                    igroffijn = int(code[1])

                hatch = boorlegenda_dawaco[code[0]]['hatch']
                lw = boorlegenda_dawaco[code[0]]['lw'][igroffijn]
                fc = [i / 255 for i in boorlegenda_dawaco[code[0]]['fc'][igroffijn]]

                with plt.rc_context({'hatch.linewidth': lw ** 3}):
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
            except:
                print('Unable to process ' + li.Nencode + '. Most likely a weird compound abbrev.')
                ph = ax.add_patch(
                    Polygon(
                        [(0, bottom),
                         (1, bottom),
                         (1, top),
                         (0, top)],
                        facecolor='red'))
                legend_handles.append(ph)
                legend_names.append('Niet verwerkt')
                continue

    ax.xaxis.set_visible(False)
    ax.set_ylim([bottom, li['Maaiveld']])
    legend_names_uniq, uniq_arg = np.unique(legend_names, return_index=True)
    ax.legend([legend_handles[i] for i in uniq_arg], legend_names_uniq, loc='lower left')
    ax.set_title('Boring')
    pass


def plot_daw_mp_map(mps, ax=None, limit_mps_to_extent=False, soort=None, annotate_mpcode=True, marker='x', color='k',
                    **kwargs):
    mps = mps.reset_index().groupby('MpCode').agg(lambda x: x.iloc[0])  # for multiple occurence of mpcode
    mps = df2gdf(mps)

    if soort is not None:
        mpssel = mps[mps.Soort == soort]
        soort_label = soort
    else:
        mpssel = mps
        soort_label = None

    if ax is not None and limit_mps_to_extent:
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        mpssel = mpssel.cx[xmin:xmax, ymin:ymax]

    ax = mpssel.plot(marker=marker, ax=ax, color=color, label=soort_label, **kwargs)

    if annotate_mpcode:
        for mpcode, x, y in zip(mpssel.index, mpssel.geometry.x, mpssel.geometry.y):
            mp_label = mpcode[4:]
            ax.annotate(
                mp_label,
                (x, y),
                ha='center',
                va='bottom',
                textcoords="offset points",
                xytext=(0, 2),
                size=6)


def plot_nlmod_vertical_profile(model_ds, ax, x, y, label, mark_inactive=True, **line_plot_kwargs):
    data = get_nlmod_vertical_profile(model_ds, x, y, label, active_only=True)
    yplot = data[:2].T.reshape(-1)
    xplot = data[2].repeat(2)
    ax.plot(xplot, yplot, label=label, **line_plot_kwargs)
    ax.set_xlim((-xplot.max() / 50, xplot.max() * 1.02))

    # mark inactive
    if mark_inactive:
        data = get_nlmod_vertical_profile(model_ds, x, y, label, active_only=False)
        icid = np.argmin((model_ds.x.values - x) ** 2 +
                         (model_ds.y.values - y) ** 2)
        ilay_inactive = model_ds.idomain.isel(cid=icid).values < 1

        for top, bot in data[:2, ilay_inactive].T:
            ax.axhspan(bot, top, color=(1, 0.5, 0.5, 1), linewidth=0)


def plot_regis_lay(rds_x, rds_y, ax, zlim=-60):
    keys = ['layer', 'bottom', 'top']
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


def plot_regis_kh(rds_x, rds_y, ax, zlim=-60):
    keys = ['kh', 'sdh', 'bottom', 'top']
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


def plot_regis_kv(rds_x, rds_y, ax, zlim=-60):
    keys = ['kv', 'sdv', 'bottom', 'top']
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
