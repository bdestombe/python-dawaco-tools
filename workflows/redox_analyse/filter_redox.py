from pathlib import Path

import pandas as pd

import dawacotools as dw

fp_parquet = Path(__file__).parent / "data" / "redox_filters.parquet"
interesting_columns = [
    "Waarde",
    "Betr",
    "Datum",
    "Parnr",
    "Naam",
    "Eenheid",
    "Afkorting",
    "MpCode",
    "Filtnr",
    "Refpunt",
    "Bk_filt",
    "Ok_filt",
    "Lab_code",
    "Xcoor",
    "Ycoor",
    "Maaiveld",
]
if fp_parquet.exists():
    df = pd.read_parquet(fp_parquet)
else:
    fd = Path(r"C:\Users\tombb\OneDrive - PWN\Vincent PWN inhuur\Data aangeleverd\Grondwaterkwaliteit\Dawaco")
    fn = "20251007 - Dawaco chemie2.xlsx"
    fp = fd / fn
    df = pd.read_excel(fp, sheet_name="sheet1", skiprows=0)
    df2 = df[interesting_columns].copy()
    df2["Datum"] = pd.to_datetime(df2["Datum"], errors="coerce")

    df2.to_parquet(fp_parquet)
    df3 = pd.read_parquet(fp_parquet)
    if not df2.equals(df3):
        msg = "DataFrames are not equal after saving and loading parquet"
        raise ValueError(msg)

redox_compounds = {"Nitraat", "Zuurstof, opgelost", "Sulfaat"}
# redoxcompounds = ["NO3", "O2", "SO4"]

out = []
for (mpcode, filtnr, datum), group in df.groupby(["MpCode", "Filtnr", "Datum"]):
    if redox_compounds.issubset(group.Naam):
        out.append((mpcode, filtnr, datum))

out2 = {}
for mpcode, filtnr, datum in out:
    if (mpcode, filtnr) not in out2:
        out2[(mpcode, filtnr)] = []
    out2[(mpcode, filtnr)].append(datum)
mps = dw.get_daw_mpcodes()
fils = dw.get_daw_filters()
fils["redoxyears"] = ""
out3 = {}
for mpcode, filtnr in out2:
    filt = fils[(fils.MpCode == mpcode) & (fils.Filtnr == filtnr)]
    if len(filt) == 1:
        f = filt.iloc[0]
        out3[(mpcode, filtnr)] = {
            "Naam": f.MpCode,
            "Xcoor": f.Xcoor,
            "Ycoor": f.Ycoor,
            "Maaiveld": f.Maaiveld,
            "Refpunt": f.Refpunt,
            "Bk_filt": f.Bk_filt,
            "Ok_filt": f.Ok_filt,
            "Bk_filt_mNAP": f.Refpunt - f.Bk_filt,
            "Ok_filt_mNAP": f.Refpunt - f.Ok_filt,
            "Datums": out2[(mpcode, filtnr)],
            "Datums_str": "-".join(str(d.year)[-2:] for d in out2[(mpcode, filtnr)]),
        }
        fils.loc[(fils.MpCode == mpcode) & (fils.Filtnr == filtnr), "redoxyears"] = out3[(mpcode, filtnr)]["Datums_str"]
    else:
        print(f"Filter not found or multiple found for {mpcode} {filtnr}")

# Aantal filters per put, exclusief de pompfilters
numfils_data = []
for mpcode, group in fils.groupby("MpCode"):
    mask1 = group.Filtnr > 0
    if group[mask1].Verval_datum.notna().any():
        mask2 = group.Verval_datum.isna() & mask1
        print(f"Verval datum found for {mpcode}. Vervallen: {group[~mask2].Filtnr.values}.")
    else:
        mask2 = mask1

    ifils_str = ",".join(group[mask2].Filtnr.astype(str))

    numfils_data.append({"MpCode": mpcode, "Filtnrs": ifils_str, "NumFils": mask2.sum()})

numfils = pd.DataFrame(numfils_data)
fils_redox = fils[fils.redoxyears != ""].copy()
fils_redox.to_file(Path(__file__).parent / "data" / "redox_filters.gpkg", driver="GPKG")
