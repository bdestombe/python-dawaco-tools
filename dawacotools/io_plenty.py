# TAGS
import numpy as np
import pandas as pd

"""
CAWPXX_LT10C  # ICAS pand niveau middenkom
HEW9XX_LT50C  # IKIEF pand niveau pand 9
"""

# relate mpcode to sec_pa tag
secs_pa_fun = {
    "CAWP01": lambda s: "19CNPCP 1" in s,
    "CAWP02": lambda s: "19CNPCP 2" in s,
    "CAWP03": lambda s: "19CNPCP 3" in s,
    "CAWP04": lambda s: "19CNPCP 4" in s,
    "CAWP05": lambda s: "19CNPCP 5" in s,
    "CAWP06": lambda s: "19CNPCP 6" in s,
    "CAWQ01": lambda s: "19CNPCQ 1" in s,
    "CAWQ02": lambda s: "19CNPCQ 2" in s,
    "CAWQ03": lambda s: "19CNPCQ 3" in s,
    "CAWQ04": lambda s: "19CNPCQ 4" in s,
    "CAWQ05": lambda s: "19CNPCQ 5" in s,
    "CAWQ06": lambda s: "19CNPCQ 6" in s,
    "HEW901": lambda s: "19CZPM91" in s,
    "HEW902": lambda s: "19CZPM92" in s,
    "HEW903": lambda s: "19CZPM93" in s,
    "HEW904": lambda s: "19CZPM94" in s,
    "HEW905": lambda s: "19CZPM95" in s,
    "HEW906": lambda s: "19CZPM96" in s,
    "HEW101": lambda s: "19CZPM101" in s,
    "HEW102": lambda s: "19CZPM102" in s,
    "HEW103": lambda s: "19CZPM103" in s,
    "HEW104": lambda s: "19CZPM104" in s,
    "HEW105": lambda s: "19CZPM105" in s,
    "HEW106": lambda s: "19CZPM106" in s,
    "CAWRAF": lambda s: "19CNPCR" in s,
    "CAWSAF": lambda s: "19CNPCS" in s,
    "CAWAAF": lambda s: "19CNPCA" in s,
    "CAWHAA": lambda s: "19CZPCH" in s,
    "HEW4AA": lambda s: "19CZPM4" in s,
    "HEWPAF": lambda s: "19CZPMHP" in s,
    "BEWARU": lambda s: "19ANPBA" in s,
    "BEWBRU": lambda s: "19ANPBB" in s,
    "BEWCRU": lambda s: "19ANPBC" in s,
    "BEWPRU": lambda s: "19ANPBHP" in s,
    "HEW801": lambda s: "19CZPM8 01" == s,
    "HEW802": lambda s: "19CZPM8 02" == s,
    "HEW803": lambda s: "19CZPM8 03" == s,
    "HEW804": lambda s: "19CZPM8 04" == s,
    "HEW805": lambda s: "19CZPM8 05" == s,
    "HEW806": lambda s: "19CZPM8 06" == s,
    "HEW807": lambda s: "19CZPM8 07" == s,
    "HEW808": lambda s: "19CZPM8 08" == s,
    "HEW809": lambda s: "19CZPM8 09" == s,
    "HEW810": lambda s: "19CZPM8 10" == s,
    "HEW811": lambda s: "19CZPM8 11" == s,
    "HEW812": lambda s: "19CZPM8 12" == s,
    "HEI801": lambda s: "19CZIM8 01" == s,
    "HEI802": lambda s: "19CZIM8 02" == s,
    "HEI803": lambda s: "19CZIM8 03" == s,
    "HEI804": lambda s: "19CZIM8 04" == s,
    "HEI805": lambda s: "19CZIM8 05" == s,
    "HEI806": lambda s: "19CZIM8 06" == s,
    "HEI807": lambda s: "19CZIM8 07" == s,
    "HEI808": lambda s: "19CZIM8 08" == s,
    "HEI809": lambda s: "19CZIM8 09" == s,
    "HEI810": lambda s: "19CZIM8 10" == s,
    "HEI811": lambda s: "19CZIM8 11" == s,
    "HEI812": lambda s: "19CZIM8 12" == s,
    "CAA1DP_FT10": lambda s: False,  # Bemaling?
    "HNWHAA_FQ10P": lambda s: False,  # Gooi
    "LAWLAA_FQ10P": lambda s: False,  # Gooi
    "LAWLAA_FQ20R": lambda s: False,  # Gooi
    "LAWLAA_FQ10R": lambda s: False,  # Gooi
}


# FLOW: m3/h inclusief return flow. Infiltration is positive. Extraction is negative. (MODFLOW convention)
secs_pa_flow = {
    "CAWP01": "-(4 * CAWP01_FQ10R + 4 * CAWP01_FQ11R)",
    "CAWP02": "-(CAWP02_FQ10R.mul(4).add(CAWP02_FQ11R.mul(4))).where((index < '2016-01-01').mul(index >= '2019-01-01'), other=CAWP02_FT10.add(CAWP02_FQ11R.mul(4)))",
    "CAWP03": "-(4 * CAWP03_FQ10R + 4 * CAWP03_FQ11R)",
    "CAWP04": "-(4 * CAWP04_FQ10R + 4 * CAWP04_FQ11R)",
    "CAWP05": "-(CAWP05_FQ10R.mul(4).add(CAWP05_FQ11R.mul(4))).where((index < '2016-02-01').mul(index >= '2018-01-01'), other=CAWP05_FT10.add(CAWP05_FQ11R.mul(4)))",
    "CAWP06": "-(4 * CAWP06_FQ10R + 4 * CAWP06_FQ11R)",
    "CAWQ01": "-(CAWQ01_FQ10R.mul(4).add(CAWQ01_FQ11R.mul(4))).where((index < '2012-01-01').mul(index >= '2013-01-01'), other=CAWQ01_FT10.add(CAWQ01_FQ11R.mul(4)))",
    "CAWQ02": "-(4 * CAWQ02_FQ10R + 4 * CAWQ02_FQ11R)",
    "CAWQ03": "-(4 * CAWQ03_FQ10R + 4 * CAWQ03_FQ11R)",
    "CAWQ04": "-(4 * CAWQ04_FQ10R + 4 * CAWQ04_FQ11R)",
    "CAWQ05": "-(4 * CAWQ05_FQ10R + 4 * CAWQ05_FQ11R)",
    "CAWQ06": "-(4 * CAWQ06_FQ10R + 4 * CAWQ06_FQ11R)",
    "HEW901": "-(4 * HEW901_FQ10R + 4 * HEW901_FQ11R)",
    "HEW902": "-(4 * HEW902_FQ10R + 4 * HEW902_FQ11R)",
    "HEW903": "-(4 * HEW903_FQ10R + 4 * HEW903_FQ11R)",
    "HEW904": "-(4 * HEW904_FQ10R + 4 * HEW904_FQ11R)",
    "HEW905": "-(4 * HEW905_FQ10R + 4 * HEW905_FQ11R)",
    "HEW906": "-(HEW906_FQ10R.mul(4).add(HEW906_FQ11R.mul(4))).where((index < '2016-01-01').mul(index >= '2018-01-01'), other=HEW906_FT10.add(HEW906_FQ11R.mul(4)))",
    "HEW101": "-(4 * HEW101_FQ10R + 4 * HEW101_FQ11R)",
    "HEW102": "-(4 * HEW102_FQ10R + 4 * HEW102_FQ11R)",
    "HEW103": "-(4 * HEW103_FQ10R + 4 * HEW103_FQ11R)",
    "HEW104": "-(4 * HEW104_FQ10R + 4 * HEW104_FQ11R)",
    "HEW105": "-(4 * HEW105_FQ10R + 4 * HEW105_FQ11R)",
    "HEW106": "-(4 * HEW106_FQ10R + 4 * HEW106_FQ11R)",
    "CAWRAF": "-4 * CAWRAF_FQ10R",
    "CAWSAF": "-4 * CAWSAF_FQ10R",
    "CAWAAF": "-4 * CAWAAF_FQ10R",
    "CAWHAA": "-4 * CAWHAA_FQ10R",
    "HEW4AA": "-4 * HEW4AA_FQ10R",
    "HEWPAF": "-(HEWPAF_FQ10R.mul(4)).where((index < '2012-01-01').mul(index >= '2013-01-01'), other=HEWPAF_FT10)",
    "BEWARU": "-(BEWARU_FQ10R.mul(4)).where((index < '2004-01-01').mul(index >= '2005-01-01'), other=BEWARU_FT10)",
    "BEWBRU": "-(BEWBRU_FQ10R.mul(4)).where((index < '2016-01-01').mul(index >= '2018-01-01'), other=BEWBRU_FT10)",
    "BEWCRU": "-4 * BEWCRU_FQ10R",
    "BEWPRU": "-4 * BEWPRU_FQ10R",
    "HEW8AF": "-4 * HEW8AF_FQ10R",  # Double check. correct according to overview Henk
    "HEW801": "-4 * HEW801_FQ10R",
    "HEW802": "-4 * HEW802_FQ10R",
    "HEW803": "-4 * HEW803_FQ10R",
    "HEW804": "-4 * HEW804_FQ10R",
    "HEW805": "-4 * HEW805_FQ10R",
    "HEW806": "-4 * HEW806_FQ10R",
    "HEW807": "-4 * HEW807_FQ10R",
    "HEW808": "-4 * HEW808_FQ10R",
    "HEW809": "-4 * HEW809_FQ10R",
    "HEW810": "-4 * HEW810_FQ10R",
    "HEW811": "-4 * HEW811_FQ10R",
    "HEW812": "-4 * HEW812_FQ10R",
    # Only use these if deltatime is 15 minutes or less
    "HEI801": "4 * HEI801_FQ10R - 4 * HEI8AA_FQ10R.where(HEI801_LT30C < 0., other=0)",
    "HEI802": "4 * HEI802_FQ10R - 4 * HEI8AA_FQ10R.where(HEI802_LT30C < 0., other=0)",
    "HEI803": "4 * HEI803_FQ10R - 4 * HEI8AA_FQ10R.where(HEI803_LT30C < 0., other=0)",
    "HEI804": "4 * HEI804_FQ10R - 4 * HEI8AA_FQ10R.where(HEI804_LT30C < 0., other=0)",
    "HEI805": "4 * HEI805_FQ10R - 4 * HEI8AA_FQ10R.where(HEI805_LT30C < 0., other=0)",
    "HEI806": "4 * HEI806_FQ10R - 4 * HEI8AA_FQ10R.where(HEI806_LT30C < 0., other=0)",
    "HEI807": "4 * HEI807_FQ10R - 4 * HEI8AA_FQ10R.where(HEI807_LT30C < 0., other=0)",
    "HEI808": "4 * HEI808_FQ10R - 4 * HEI8AA_FQ10R.where(HEI808_LT30C < 0., other=0)",
    "HEI809": "4 * HEI809_FQ10R - 4 * HEI8AA_FQ10R.where(HEI809_LT30C < 0., other=0)",
    "HEI810": "4 * HEI810_FQ10R - 4 * HEI8AA_FQ10R.where(HEI810_LT30C < 0., other=0)",
    "HEI811": "4 * HEI811_FQ10R - 4 * HEI8AA_FQ10R.where(HEI811_LT30C < 0., other=0)",
    "HEI812": "4 * HEI812_FQ10R - 4 * HEI8AA_FQ10R.where(HEI812_LT30C < 0., other=0)",
    "HEI813": "4 * HEI813_FQ10R - 4 * HEI8AA_FQ10R.where(HEI813_LT30C < 0., other=0)",
    "HEI814": "4 * HEI814_FQ10R - 4 * HEI8AA_FQ10R.where(HEI814_LT30C < 0., other=0)",
    "HEI815": "4 * HEI815_FQ10R - 4 * HEI8AA_FQ10R.where(HEI815_LT30C < 0., other=0)",
    "HEI816": "4 * HEI816_FQ10R - 4 * HEI8AA_FQ10R.where(HEI816_LT30C < 0., other=0)",
    "HEI817": "4 * HEI817_FQ10R - 4 * HEI8AA_FQ10R.where(HEI817_LT30C < 0., other=0)",
    "HEI818": "4 * HEI818_FQ10R - 4 * HEI8AA_FQ10R.where(HEI818_LT30C < 0., other=0)",
    "HEI819": "4 * HEI819_FQ10R - 4 * HEI8AA_FQ10R.where(HEI819_LT30C < 0., other=0)",
    "HEI820": "4 * HEI820_FQ10R - 4 * HEI8AA_FQ10R.where(HEI820_LT30C < 0., other=0)",
    "HEI": "4 * (- HEI8AA_FQ10R + HEI801_FQ10R + HEI802_FQ10R + HEI803_FQ10R + HEI804_FQ10R + HEI805_FQ10R + HEI806_FQ10R + HEI807_FQ10R + HEI808_FQ10R + HEI809_FQ10R + HEI810_FQ10R + HEI811_FQ10R + HEI812_FQ10R + HEI813_FQ10R + HEI814_FQ10R + HEI815_FQ10R + HEI816_FQ10R + HEI817_FQ10R + HEI818_FQ10R + HEI819_FQ10R + HEI820_FQ10R)",
    "CAA1DP": "-4 * CAA1DP_FQ10C",  # ECAS Double check times 4? pos or neg?
    "HNWHAA": "-4 * LAWHAA_FQ10R",  # Huizen. HNWHAA_FQ10P is een berekening van enkel LAWHAA_FQ10R
    "LAWHAA": "-4 * LAWHAA_FQ10R",  # Huizen
    "LAWLAAZUID": "-4 * LAWLAA_FQ20R",
    "LAWLAANOORD": "-4 * LAWLAA_FQ10R",
    "HVAOAF": "4 * HVAOAF_FQ10R",  # Aanvoer ICAS+DWAT
    "IKIEFbedrijfswater": "4 * HEIDBA_FQ10R + 4 * HEZ3AF_FQ10R + 4 * HEZ5EF_FQ10R",
    "IKIEFbassin": "-4 * HEIDBA_FQ10R + 4 * HEZS01_FQ10R + 4 * HEZS02_FQ10R",
}

# Opposite sign!
# FLOW: m3/h exclusief return flow. Infiltration is positive. Extraction is negative.
tra_alias = {
    "DWATOnt": "-(HEW801 + HEW802 + HEW803 + HEW804 + HEW805 + HEW806 + HEW807 + HEW808 + HEW809 + HEW810 + HEW811 + HEW812)",
    "DWATInf": "- HEI",
    "DWAT-Netto": "DWATOnt + DWATInf",
    "ICAS-P1-Ont": "-CAWP01",
    "ICAS-P2-Ont": "-CAWP02",
    "ICAS-P3-Ont": "-CAWP03",
    "ICAS-P4-Ont": "-CAWP04",
    "ICAS-P5-Ont": "-CAWP05",
    "ICAS-P6-Ont": "-CAWP06",
    "ICAS-Q1-Ont": "-CAWQ01",
    "ICAS-Q2-Ont": "-CAWQ02",
    "ICAS-Q4-Ont": "-CAWQ04",
    "ICAS-Q3-Ont": "-CAWQ03",
    "ICAS-Q5-Ont": "-CAWQ05",
    "ICAS-Q6-Ont": "-CAWQ06",
    "ICASPOnt": "-(CAWP01 + CAWP02 + CAWP03 + CAWP04 + CAWP05 + CAWP06)",
    "ICASQOnt": "-(CAWQ01 + CAWQ02 + CAWQ03 + CAWQ04 + CAWQ05 + CAWQ06)",
    "ICASPQOnt": "ICASPOnt + ICASQOnt",
    "NHDzROnt": "-CAWRAF",
    "NHDzSOnt": "-CAWSAF",
    "NHDzRSOnt": "NHDzROnt + NHDzSOnt",
    "NHDz-Tot-Excl-RS-Ont": "-(CAWAAF + CAWHAA + HEW4AA + HEWPAF)",
    "NHDz-Tot-Incl-RS-Ont": "-(CAWAAF + CAWHAA + HEW4AA + HEWPAF + CAWRAF + CAWSAF)",
    "ICASPQRSOnt": "ICASPQOnt + NHDzRSOnt",
    "ICASspui": "-4 * (CAWP01_FQ11R + CAWP02_FQ11R + CAWP03_FQ11R + CAWP04_FQ11R + CAWP05_FQ11R + CAWP06_FQ11R + CAWQ01_FQ11R + CAWQ02_FQ11R + CAWQ03_FQ11R + CAWQ04_FQ11R + CAWQ05_FQ11R + CAWQ06_FQ11R)",
    "ICASInf": "- HVAOAF - 4 * HEI8AA_FQ10R + CAA1DP + ICASspui",
    "ICASPQRSNetto": "ICASInf + ICASPQRSOnt",
    "ICASPQNetto": "ICASInf + ICASPQOnt",
    "Bemaling": "-CAA1DP",  # ECAS
    "IKIEF-9-1-Ont": "-HEW901",
    "IKIEF-9-2-Ont": "-HEW902",
    "IKIEF-9-3-Ont": "-HEW903",
    "IKIEF-9-4-Ont": "-HEW904",
    "IKIEF-9-5-Ont": "-HEW905",
    "IKIEF-9-6-Ont": "-HEW906",
    "IKIEF9Ont": "-(HEW901 + HEW902 + HEW903 + HEW904 + HEW905 + HEW906)",
    "IKIEF-10-1-Ont": "-HEW101",
    "IKIEF-10-2-Ont": "-HEW102",
    "IKIEF-10-3-Ont": "-HEW103",
    "IKIEF-10-4-Ont": "-HEW104",
    "IKIEF-10-5-Ont": "-HEW105",
    "IKIEF-10-6-Ont": "-HEW106",
    "IKIEF10Ont": "-(HEW101 + HEW102 + HEW103 + HEW104 + HEW105 + HEW106)",
    "IKIEF910Ont": "IKIEF9Ont + IKIEF10Ont",
    "IKIEFspui": "-4 * (HEW901_FQ11R + HEW902_FQ11R + HEW903_FQ11R + HEW904_FQ11R + HEW905_FQ11R + HEW906_FQ11R + HEW101_FQ11R + HEW102_FQ11R + HEW103_FQ11R + HEW104_FQ11R + HEW105_FQ11R + HEW106_FQ11R)",
    "IKIEFInf": "-4 * HVAOAF_FQ20R - IKIEFbedrijfswater + IKIEFspui",
    # Infiltratie['Infiltratie IKIEF (HVAOAF_FQ20R)']+Debieten_FQ['HEIDBA_FQ10R']+Debieten_FQ['HEZ3AF_FQ10R']+Debieten_FQ['HEZ5EF_FQ10R']
    "IKIEF910Netto": "IKIEFInf + IKIEF910Ont",
    "IKIEFBassinNetto": "-IKIEFbassin",
    "IKIEF910BasNetto": "IKIEF910Netto + IKIEFBassinNetto",
    "NHDz-A-Ont": "-CAWAAF",
    "NHDz-H-Ont": "-CAWHAA",
    "NHDz-4-Ont": "-HEW4AA",
    "NHDz-HP-Ont": "-HEWPAF",
    "BER-A-Ont": "-(BEWARU)",
    "BER-B-Ont": "-(BEWBRU)",
    "BER-C-Ont": "-(BEWCRU)",
    "BER-HP-Ont": "-(BEWPRU)",
    "BER-Tot-Ont": "-(BEWARU + BEWBRU + BEWCRU + BEWPRU)",
    "Gooi-Laren-Z-Ont": "-(LAWLAAZUID)",
    "Gooi-Laren-N-Ont": "-(LAWLAANOORD)",
    "Gooi-Laren-Z+N-Ont": "-(LAWLAAZUID + LAWLAANOORD)",
    "Gooi-Huizen-Ont": "-(HNWHAA)",
    "Gooi-Tot-Ont": "-(LAWLAAZUID + LAWLAANOORD + HNWHAA)",
}


def mpcode_to_sec_pa_tag(mpcode):
    """Returns the sec_pa tag for a single mpcode. If no sec_pa tag is found, an empty string is returned.

    Parameters
    ----------
    mpcode : str
        Mpcode

    Returns
    -------
    sec_pa_tag : str
        sec_pa tag
    """
    # df['a'] = df['a'].apply(lambda x: x + 1)
    for k, fun in secs_pa_fun.items():
        if fun(mpcode):
            return k
        else:
            pass

    return ""


def mpcode_to_sec_pa_flow(df_plenty, mpcode):
    """Returns the flow for a single mpcode

    Parameters
    ----------
    df_plenty : pd.DataFrame
        Plenty data
    mpcode : str
        Mpcode

    Returns
    -------
    flow : float
        Flow in m3/h for the specific well
    """
    assert isinstance(mpcode, str), "single mpcode allowed"
    patag = mpcode_to_sec_pa_tag(mpcode)
    flow_eq = secs_pa_flow[patag]
    flow = df_plenty.eval(flow_eq)
    return flow


def get_required_patags_for_flow(df=None):
    """Returns the required Plenty tags for the flow calculation

    If `df` is None, the tags are returned for all wells. Otherwise, the tags are returned for the wells in `df`.

    Parameters
    ----------
    df : pd.DataFrame, optional

    Returns
    -------
    tags : list
        List of required Plenty tags
    """
    if df is None:
        comb = " ".join(secs_pa_flow.values())
    else:
        unique_secs = list(set(get_sec_pa(df)))
        pa_flow_eqs = [secs_pa_flow.get(k, k) for k in unique_secs]
        comb = " ".join(pa_flow_eqs)

    for c in "().=":
        comb = comb.replace(c, " ")

    tags = set(filter(lambda s: "_" in s, comb.split(" ")))
    print("\t".join(sorted(tags)))  # to copy-paste to Excel
    return tags


def get_sec_pa(df):
    """Returns the sec_pa tag for each well in `df`

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with well data. Must contain the columns `MpCode` and `Soort`

    Returns
    -------
    sec : list
        List of sec_pa tags
    """
    ispomp = ispomp_filter(df)
    mpcodes = df.reset_index().MpCode
    sec = np.where(ispomp, list(map(mpcode_to_sec_pa_tag, mpcodes)), "")
    return sec


def ispomp_filter(df):
    """Returns a boolean array indicating whether a well is a pump well or not

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with well data. Must contain the columns `MpCode` and `Soort`

    Returns
    -------
    ispomp : np.ndarray
        Boolean array indicating whether a well is a pump well or not
    """
    ispomp = ((df.Soort == "Pompput") + (df.Soort == "Infiltratieput")).astype(bool)
    ifiltermin = df.groupby("MpCode")["Filtnr"].transform("min")
    isfiltermin = df.Filtnr == ifiltermin
    return np.logical_and(isfiltermin, ispomp)


def get_nput_dict(df):
    """Returns a dictionary with the nput for each well in `df`

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with well data. Must contain the columns `MpCode` and `Soort`

    Returns
    -------
    nput_dict : dict
        Dictionary with the nput for each well in `df`
    """
    ispomp = ispomp_filter(df)
    mpcodes = df[ispomp].reset_index().MpCode
    u, counts = np.unique(list(map(mpcode_to_sec_pa_tag, mpcodes)), return_counts=True)
    nput_dict = {ui: ci for ui, ci in zip(u, counts)}
    nput_dict[""] = np.nan
    return nput_dict


def get_nput(df):
    """Returns the nput for each well in `df`

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with well data. Must contain the columns `MpCode` and `Soort`

    Returns
    -------
    nput : np.ndarray
        Nput for each well in `df`
    """
    sec = get_sec_pa(df)
    nput_dict = get_nput_dict(df)
    return [nput_dict.get(k, k) for k in sec]


def get_flow(df, df_plenty, divide_by_nput=True):
    """Returns the flow for each well in `df`

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with well data. Must contain the columns `MpCode` and `Soort`
    df_plenty : pd.DataFrame
        Plenty data
    divide_by_nput : bool, optional
        If True, the flow is divided by the nput

    Returns
    -------
    flow : np.ndarray
        Flow for each well in `df` if divide_by_nput is True. Otherwise, the flow is returned for each well in `df` without division by the nput.
    """
    if isinstance(df_plenty, pd.Series):
        try:
            date = pd.Timestamp(df_plenty.name)
        except:
            date = pd.Timestamp.now()

        df_plenty = pd.DataFrame(
            columns=df_plenty.index.values,
            data=df_plenty.values.reshape(1, -1),
            index=[date],
        )

    elif isinstance(df_plenty, pd.DataFrame):
        assert len(df_plenty) == 1, "Only one value value/timestamp/average allowed"
    else:
        raise NotImplementedError

    required_pa_tags = get_required_patags_for_flow(df=df)
    assert all(
        i in df_plenty.columns for i in required_pa_tags
    ), f"`df_plenty` requires the following Plenty tags:\n{required_pa_tags}"
    assert np.issubdtype(df_plenty.index, np.datetime64), "Index needs to be a date"

    sec = get_sec_pa(df)
    u_sec = set(sec)
    u_pa_flow_eqs = [secs_pa_flow.get(k, k) for k in u_sec]
    u_pa_flow = [df_plenty.eval(eq) if eq else np.nan for eq in u_pa_flow_eqs]

    if divide_by_nput:
        nput_dict = get_nput_dict(df)
        pa_flow_dict = {k: v / nput_dict[k] for k, v in zip(u_sec, u_pa_flow)}
    else:
        pa_flow_dict = {k: v for k, v in zip(u_sec, u_pa_flow)}

    pa_flow = np.array([pa_flow_dict.get(k, k) for k in sec], dtype=float)
    return pa_flow


def get_flows(df, df_plenty, divide_by_nput=True):
    """Returns the flow for each well in `df`

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with well data. Must contain the columns `MpCode` and `Soort`
    df_plenty : pd.DataFrame
        Plenty data
    divide_by_nput : bool, optional
        If True, the flow is divided by the nput, otherwise the flow is returned without division by the nput

    Returns
    -------
    flow : np.ndarray
        Flow for each well in `df`
    """
    if isinstance(df_plenty, pd.Series):
        try:
            date = pd.Timestamp(df_plenty.name)
        except:
            date = pd.Timestamp.now()

        df_plenty = pd.DataFrame(
            columns=df_plenty.index.values,
            data=df_plenty.values.reshape(1, -1),
            index=[date],
        )

    elif isinstance(df_plenty, pd.DataFrame):
        assert len(df_plenty) == 1, "Only one value value/timestamp/average allowed"
    else:
        raise NotImplementedError

    required_pa_tags = get_required_patags_for_flow(df=df)
    assert all(
        i in df_plenty.columns for i in required_pa_tags
    ), f"`df_plenty` requires the following Plenty tags:\n{required_pa_tags}"
    assert np.issubdtype(df_plenty.index, np.datetime64), "Index needs to be a date"

    sec = get_sec_pa(df)
    u_sec = set(sec)
    u_pa_flow_eqs = [secs_pa_flow.get(k, k) for k in u_sec]
    u_pa_flow = [df_plenty.eval(eq) if eq else np.nan for eq in u_pa_flow_eqs]

    if divide_by_nput:
        nput_dict = get_nput_dict(df)
        pa_flow_dict = {k: v / nput_dict[k] for k, v in zip(u_sec, u_pa_flow)}
    else:
        pa_flow_dict = {k: v for k, v in zip(u_sec, u_pa_flow)}

    pa_flow = np.array([pa_flow_dict.get(k, k) for k in sec], dtype=float)
    return pa_flow


def get_sec_pa_flows(df_plenty):
    """Returns the sec_pa_flows as defined in `secs_pa_flow` for the Plenty data `df_plenty`

    Parameters
    ----------
    df_plenty : pd.DataFrame
        Plenty data

    Returns
    -------
    flows : pd.DataFrame
        sec_pa_flows as defined in `secs_pa_flow` for the Plenty data `df_plenty`
    """

    return pd.DataFrame({k: df_plenty.eval(v) for k, v in secs_pa_flow.items()})


def get_tra_flows(df_plenty):
    """Returns the tra_flows as defined in `tra_alias` for the Plenty data `df_plenty`

    Parameters
    ----------
    df_plenty : pd.DataFrame
        Plenty data

    Returns
    -------
    flows : pd.DataFrame
        tra_flows as defined in `tra_alias` for the Plenty data `df_plenty`
    """
    sec_flows = get_sec_pa_flows(df_plenty)
    df = pd.concat((df_plenty, sec_flows), axis=1)
    tra_alias_keys = list(tra_alias.keys())

    # while True:
    for i in range(5):
        for k in tra_alias:
            if k in df.columns:
                continue
            try:
                df[k] = df.eval(tra_alias[k])
                tra_alias_keys.remove(k)
            except:
                print(f"Failed {k}")
                pass

    if tra_alias_keys:
        print(f"Failed {tra_alias_keys}")

    return df[tra_alias.keys()]


def get_plenty_data(fp, center_average_values=None, sanity_checks=True):
    """Returns the Plenty data from the file `fp`

    Parameters
    ----------
    fp : str
        Path to Plenty data
    center_average_values : bool, optional
        If True, the indices are centered over the measurement period. If False, the values are not centered. If None, the configuration in the Excel is read to determine whether to center the indices
    sanity_checks : bool, optional
        If True, sanity checks are performed

    Returns
    -------
    data : pd.DataFrame
        Plenty data
    """
    data = pd.read_excel(fp, skiprows=9, index_col="ophaal tijdstip", na_values=["EOF"])
    config_df = pd.read_excel(fp, skiprows=0, nrows=5, header=None, usecols=[0, 1, 3])
    assert (
        config_df.iloc[4, 0] == "gemiddelde ?"
    ), "Unable to read configuration. Set `center_average_values` manually"
    is_dagsom = config_df.iloc[0, 2] == 5.0
    assert (
        not is_dagsom
    ), "Dagsom not supported. In other parts flow units are assumed instead of dagsom's 'm3'."

    if sanity_checks:
        # check config is in sync with the data
        timedelta_config = pd.Timedelta(f"{config_df.iloc[2, 1]}H")
        assert timedelta_config == (
            data.index[1] - data.index[0]
        ), "Configuration and data are not in sync"
        assert timedelta_config == (
            data.index[-1] - data.index[-2]
        ), "Configuration and data are not in sync"
        assert timedelta_config == pd.Timedelta(
            data.index.inferred_freq
        ), "Unable to infer frequency from data. Missing rows?"

        data[data.abs() > 10000.0] = np.nan

    if center_average_values is None:
        is_avg = config_df.iloc[4, 1] == "ja"
        is_actual_values = config_df.iloc[0, 2] == 1.0

        center_average_values = (is_avg and is_actual_values) or is_dagsom

    if center_average_values:
        timedelta = data.index[1] - data.index[0]
        data.index -= timedelta / 2

    return data
