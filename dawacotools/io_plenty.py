# TAGS
import numpy as np

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


# FLOW: m3/h inclusief return flow. Minus is extraction
secs_pa_flow = {
    "CAWP01": "-4 * CAWP01_FQ10R + 4 * CAWP01_FQ11R",
    "CAWP02": "-(CAWP02_FQ10R.mul(4).add(CAWP02_FQ11R.mul(4))).where((index < '2016-01-01').mul(index >= '2019-01-01'), other=CAWP02_FT10.add(CAWP02_FQ11R.mul(4)))",
    "CAWP03": "-4 * CAWP03_FQ10R + 4 * CAWP03_FQ11R",
    "CAWP04": "-4 * CAWP04_FQ10R + 4 * CAWP04_FQ11R",
    "CAWP05": "-(CAWP05_FQ10R.mul(4).add(CAWP05_FQ11R.mul(4))).where((index < '2016-02-01').mul(index >= '2018-01-01'), other=CAWP05_FT10.add(CAWP05_FQ11R.mul(4)))",
    "CAWP06": "-4 * CAWP06_FQ10R + 4 * CAWP06_FQ11R",
    "CAWQ01": "-(CAWQ01_FQ10R.mul(4).add(CAWQ01_FQ11R.mul(4))).where((index < '2012-01-01').mul(index >= '2013-01-01'), other=CAWQ01_FT10.add(CAWQ01_FQ11R.mul(4)))",
    "CAWQ02": "-4 * CAWQ02_FQ10R + 4 * CAWQ02_FQ11R",
    "CAWQ03": "-4 * CAWQ03_FQ10R + 4 * CAWQ03_FQ11R",
    "CAWQ04": "-4 * CAWQ04_FQ10R + 4 * CAWQ04_FQ11R",
    "CAWQ05": "-4 * CAWQ05_FQ10R + 4 * CAWQ05_FQ11R",
    "CAWQ06": "-4 * CAWQ06_FQ10R + 4 * CAWQ06_FQ11R",
    "HEW901": "-4 * HEW901_FQ10R + 4 * HEW901_FQ11R",
    "HEW902": "-4 * HEW902_FQ10R + 4 * HEW902_FQ11R",
    "HEW903": "-4 * HEW903_FQ10R + 4 * HEW903_FQ11R",
    "HEW904": "-4 * HEW904_FQ10R + 4 * HEW904_FQ11R",
    "HEW905": "-4 * HEW905_FQ10R + 4 * HEW905_FQ11R",
    "HEW906": "-(HEW906_FQ10R.mul(4).add(HEW906_FQ11R.mul(4))).where((index < '2016-01-01').mul(index >= '2018-01-01'), other=HEW906_FT10.add(HEW906_FQ11R.mul(4)))",
    "HEW101": "-4 * HEW101_FQ10R + 4 * HEW101_FQ11R",
    "HEW102": "-4 * HEW102_FQ10R + 4 * HEW102_FQ11R",
    "HEW103": "-4 * HEW103_FQ10R + 4 * HEW103_FQ11R",
    "HEW104": "-4 * HEW104_FQ10R + 4 * HEW104_FQ11R",
    "HEW105": "-4 * HEW105_FQ10R + 4 * HEW105_FQ11R",
    "HEW106": "-4 * HEW106_FQ10R + 4 * HEW106_FQ11R",
    "CAWRAF": "-4 * CAWRAF_FQ10R",
    "CAWSAF": "-4 * CAWSAF_FQ10R",
    "CAWAAF": "-4 * CAWAAF_FQ10R",
    "CAWHAA": "-4 * CAWHAA_FQ10R",
    "HEW4AA": "-4 * HEW4AA_FQ10R",
    "HEWPAF": "-(4 * HEWPAF_FQ10R).where((index < '2012-01-01').mul(index >= '2013-01-01'), other=HEWPAF_FT10))",
    "BEWARU": "-(4 * BEWARU_FQ10R).where((index < '2004-01-01').mul(index >= '2005-01-01'), other=BEWARU_FT10))",
    "BEWBRU": "-(4 * BEWBRU_FQ10R).where((index < '2016-01-01').mul(index >= '2018-01-01'), other=BEWBRU_FT10))",
    "BEWCRU": "-4 * BEWCRU_FQ10R",
    "BEWPRU": "-4 * BEWPRU_FQ10R",
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
    "HEI801": "4 * HEI801_FQ10R",
    "HEI802": "4 * HEI802_FQ10R",
    "HEI803": "4 * HEI803_FQ10R",
    "HEI804": "4 * HEI804_FQ10R",
    "HEI805": "4 * HEI805_FQ10R",
    "HEI806": "4 * HEI806_FQ10R",
    "HEI807": "4 * HEI807_FQ10R",
    "HEI808": "4 * HEI808_FQ10R",
    "HEI809": "4 * HEI809_FQ10R",
    "HEI810": "4 * HEI810_FQ10R",
    "HEI811": "4 * HEI811_FQ10R",
    "HEI812": "4 * HEI812_FQ10R",
    "CAA1DP_FT10": "",
    "HNWHAA_FQ10P": "",
    "LAWLAA_FQ10P": "",
    "LAWLAA_FQ20R": "",
    "LAWLAA_FQ10R": "",
}


def mpcode_to_sec_pa_tag(mpcode):
    # df['a'] = df['a'].apply(lambda x: x + 1)
    for k, fun in secs_pa_fun.items():
        if fun(mpcode):
            return k
        else:
            pass

    return ""


def mpcode_to_sec_pa_flow(df, mpcode):
    # df['a'] = df['a'].apply(lambda x: x + 1)
    patag = mpcode_to_sec_pa_tag(mpcode)
    flow_eq = secs_pa_flow[patag]
    return df.eval(flow_eq)


def get_all_required_patags_for_flow():
    comb = " ".join(secs_pa_flow.values())
    for c in "().=":
        comb = comb.replace(c, " ")

    tags = list(filter(lambda s: "_" in s, comb.split(" ")))
    print("\t".join(tags))
    return tags


def get_sec_pa(df):
    mpcodes = df.reset_index().MpCode
    return list(map(mpcode_to_sec_pa_tag, mpcodes))


def get_nput_dict(df):
    ispomp = ((df.Soort == "Pompput") + (df.Soort == 'Infiltratieput')).astype(bool)
    mpcodes = np.unique(df[ispomp].reset_index().MpCode)  # multiple filters per put
    u, counts = np.unique(list(map(mpcode_to_sec_pa_tag, mpcodes)), return_counts=True)
    nput_dict = {ui: ci for ui, ci in zip(u, counts)}
    nput_dict[''] = np.nan
    return nput_dict


def get_nput(df):
    nput_dict = get_nput_dict(df)
    return df["sec"].replace(to_replace=nput_dict)
