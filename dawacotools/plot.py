import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.patches import Polygon

from .colors import tno_colors, boorlegenda_dawaco


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


def plot_map_mp(mps, ax=None, soort=None, annotate_mpcode=True, marker='x', color='k', **kwargs):
    if soort is not None:
        mpssel = mps[mps.Soort == soort]
        soort_label = soort
    else:
        mpssel = mps
        soort_label = None

    if ax is not None:
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
