import os

import pastastore as pst
from hydropandas.io.pastas import _get_metadata_from_obs

import dawacotools as dw

# fd = os.path.join(os.path.abspath(__file__), "..", "data", "Dawaco_db_v1")
fd = os.path.join(os.path.abspath(__file__), "..", "data", "20240715_Dawaco_db")
conn = pst.PystoreConnector("dawaco_db", path=fd)
store = pst.PastaStore(name="dawaco_db", connector=conn)

filters = dw.get_daw_filters()
failed = []

for i, (_, f) in enumerate(filters.iterrows()):
    try:
        obs = dw.get_hpd_gws_obs(
            mpcode=f.MpCode, filternr=f.Filtnr, partial_match_mpcode=False
        )
        obs.sort_index(inplace=True)
        if len(obs) == 0:
            print(f"{i:05d} No data: \t{f.MpCode}_{f.Filtnr}")
            continue
        else:
            meta = _get_metadata_from_obs(obs)
            store.conn.add_oseries(
                obs.iloc[:, 0], obs.name, metadata=meta, overwrite=True
            )
            print(f"{i:05d} Added: \t{f.MpCode}_{f.Filtnr}")

    except Exception as e:
        print(e)
        obs = None
        print(f"{i:05d} Failed: \t{f.MpCode}_{f.Filtnr}")
        failed.append(f.MpCode)


for i, (_, f) in enumerate(filters[filters.MpCode.isin(failed)].iterrows()):
    try:
        obs = dw.get_hpd_gws_obs(
            mpcode=f.MpCode, filternr=f.Filtnr, partial_match_mpcode=False
        ).sort_index()
        if len(obs) == 0:
            print(f"{i:05d} No data: \t{f.MpCode}_{f.Filtnr}")
            continue
        else:
            meta = _get_metadata_from_obs(obs)
            store.conn.add_oseries(
                obs.iloc[:, 0], obs.name, metadata=meta, overwrite=True
            )
            print(f"{i:05d} Added: \t{f.MpCode}_{f.Filtnr}")

    except Exception as e:
        print(e)
        obs = None
        print(f"{i:05d} Failed: \t{f.MpCode}_{f.Filtnr}")
        pass

print("end")
