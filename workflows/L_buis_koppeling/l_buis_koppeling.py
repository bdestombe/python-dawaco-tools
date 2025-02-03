from dawacotools import get_daw_filters, get_daw_mps
from dawacotools.analysis import get_cluster_mps

mps = get_daw_mps()
fts = get_daw_filters()
col, icol = get_cluster_mps(mps, r_max=10, min_cluster_size=2)


# Contains pompputten
def contains_pompput(arr):
    mps_sel = mps.loc[list(arr)]
    flag = "Pompput" in mps_sel.Soort.values

    return flag


faulties = [
    "19azw034",
    "19azw249",
    "19ANPBA 25",
    "19anl5000",
    "19anl5023",
    "19anl5024",
    "19anL5504",
    "19anL5507",
    "19czl5350",
    "19czw617",
    "19czw642",
    "19czw282",
    "19czL111",
    "19czw787",
    "25ANL006",
    "19CZL5221",
    "19czl5223",
    "19azl5036",
    "19CNW121",
    "19cnl122",
    "19azw193",
    "19cnl317",
    "19czw102",
    "19czw640",
]
faulties = [s.upper() for s in faulties]

for f in faulties:
    if f not in mps.index:
        print(f, "not in mps")
        continue
    if contains_pompput([f]):
        print(f, "is a faulty pompput")
        continue

    if f in [a for c in col for a in c]:
        print(f, "in cluster")
        col_matches = list(filter(lambda x: f in x, col))
        if contains_pompput(col_matches[0]):
            print(f, "in cluster with pompput", col_matches[0])
            for ff in col_matches[0]:
                if contains_pompput([ff]):
                    print(ff, "is a nearby pompput")
        else:
            print(f, "in cluster without pompput")
    else:
        print(f, "not in cluster")
