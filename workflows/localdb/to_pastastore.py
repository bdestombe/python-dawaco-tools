import datetime
import os

import pastastore as pst
from hydropandas.io.pastas import _get_metadata_from_obs

import dawacotools as dw

dbname = datetime.datetime.now().strftime(r"%Y%m%d_dawaco_db")
dbtype = "Arctic"

if dbtype == "Arctic":
    # define ArcticDB connector
    uri = "lmdb://" + os.path.relpath(os.path.join(os.path.abspath(__file__), "..", "data", dbname))
    conn = pst.ArcticDBConnector("my_db", uri)
elif dbtype == "Pystore":
    fd = os.path.join(os.path.abspath(__file__), "..", "data", dbname)
    conn = pst.PystoreConnector("dawaco_db", path=fd)
else:
    msg = "dbtype should be Arctic or Pystore"
    raise ValueError(msg)

store = pst.PastaStore(name="dawaco_db", connector=conn)

filters = dw.get_daw_filters()
failed = []

for _i, (_, f) in enumerate(filters.iterrows()):
    try:
        print(f"{_i / len(filters) * 100:.0f}% Loading {f.MpCode} {f.Filtnr}")
        obs = dw.get_hpd_gws_obs(mpcode=f.MpCode, filternr=f.Filtnr, partial_match_mpcode=False)
        obs.sort_index(inplace=True)
        if len(obs) == 0:
            continue
        else:
            meta = _get_metadata_from_obs(obs)
            store.conn.add_oseries(obs.iloc[:, 0], obs.name, metadata=meta, overwrite=True)

    except Exception:
        obs = None
        print(f"Failed to load {f.MpCode} {f.Filtnr}")
        failed.append(f.MpCode)

# Retry failed filters
for _i, (_, f) in enumerate(filters[filters.MpCode.isin(failed)].iterrows()):
    try:
        obs = dw.get_hpd_gws_obs(mpcode=f.MpCode, filternr=f.Filtnr, partial_match_mpcode=False).sort_index()
        if len(obs) == 0:
            continue
        else:
            meta = _get_metadata_from_obs(obs)
            store.conn.add_oseries(obs.iloc[:, 0], obs.name, metadata=meta, overwrite=True)

    except Exception:
        print(f"Failed to load {f.MpCode} {f.Filtnr} twice")
        obs = None

print("Failed to load the following filters:")
print(failed)
store.conn.close()
