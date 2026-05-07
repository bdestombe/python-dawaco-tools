from pathlib import Path

import dawacotools as dw

mpcodes = ["15CZW1004", "15CZW1005", "15CZW1006", "15CZW1007"]
folder_out = Path(__file__).parent / "data"
for mpcode in mpcodes:
    for i in range(10):
        ds = dw.io.get_daw_ts_stijghgt(mpcode=mpcode, filternr=i)
        if len(ds) > 0:
            ds.to_csv(folder_out / f"{mpcode}_F{i}.csv")
            print(ds)
