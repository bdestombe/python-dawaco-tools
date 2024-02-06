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


# FLOW: m3/h inclusief return flow. Extraction is negative.
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
    "HEI801": "4 * HEI801_FQ10R - HEI8AA_FQ10R.where(HEI801_LT30C < 0., other=0)",
    "HEI802": "4 * HEI802_FQ10R - HEI8AA_FQ10R.where(HEI802_LT30C < 0., other=0)",
    "HEI803": "4 * HEI803_FQ10R - HEI8AA_FQ10R.where(HEI803_LT30C < 0., other=0)",
    "HEI804": "4 * HEI804_FQ10R - HEI8AA_FQ10R.where(HEI804_LT30C < 0., other=0)",
    "HEI805": "4 * HEI805_FQ10R - HEI8AA_FQ10R.where(HEI805_LT30C < 0., other=0)",
    "HEI806": "4 * HEI806_FQ10R - HEI8AA_FQ10R.where(HEI806_LT30C < 0., other=0)",
    "HEI807": "4 * HEI807_FQ10R - HEI8AA_FQ10R.where(HEI807_LT30C < 0., other=0)",
    "HEI808": "4 * HEI808_FQ10R - HEI8AA_FQ10R.where(HEI808_LT30C < 0., other=0)",
    "HEI809": "4 * HEI809_FQ10R - HEI8AA_FQ10R.where(HEI809_LT30C < 0., other=0)",
    "HEI810": "4 * HEI810_FQ10R - HEI8AA_FQ10R.where(HEI810_LT30C < 0., other=0)",
    "HEI811": "4 * HEI811_FQ10R - HEI8AA_FQ10R.where(HEI811_LT30C < 0., other=0)",
    "HEI812": "4 * HEI812_FQ10R - HEI8AA_FQ10R.where(HEI812_LT30C < 0., other=0)",
    "HEI813": "4 * HEI813_FQ10R - HEI8AA_FQ10R.where(HEI813_LT30C < 0., other=0)",
    "HEI814": "4 * HEI814_FQ10R - HEI8AA_FQ10R.where(HEI814_LT30C < 0., other=0)",
    "HEI815": "4 * HEI815_FQ10R - HEI8AA_FQ10R.where(HEI815_LT30C < 0., other=0)",
    "HEI816": "4 * HEI816_FQ10R - HEI8AA_FQ10R.where(HEI816_LT30C < 0., other=0)",
    "HEI817": "4 * HEI817_FQ10R - HEI8AA_FQ10R.where(HEI817_LT30C < 0., other=0)",
    "HEI818": "4 * HEI818_FQ10R - HEI8AA_FQ10R.where(HEI818_LT30C < 0., other=0)",
    "HEI819": "4 * HEI819_FQ10R - HEI8AA_FQ10R.where(HEI819_LT30C < 0., other=0)",
    "HEI820": "4 * HEI820_FQ10R - HEI8AA_FQ10R.where(HEI820_LT30C < 0., other=0)",
    "CAA1DP": "-CAA1DP_FT10",  # ECAS Double check times 4? pos or neg?
    "HNWHAA": "-4 * HNWHAA_FQ10P",  # Huizen
    "LAWLAAZUID": "-4 * LAWLAA_FQ20R",
    "LAWLAANOORD": "-4 * LAWLAA_FQ10R",
    "IKIEFaanvoer": "4 * HVAOAF_FQ20R",
    "ICASDWATaanvoer": "4 * HVAOAF_FQ10R",  # Aanvoer ICAS+DWAT(HVAOAF_FQ10R)
    "IKIEFbedrijfswater": "HVAOAF_FQ20R + HEIDBA_FQ10R + HEZ3AF_FQ10R + HEZ5EF_FQ10R",
}

# Infiltratie['Infiltratie IKIEF (HVAOAF_FQ20R)']+Debieten_FQ['HEIDBA_FQ10R']+Debieten_FQ['HEZ3AF_FQ10R']+Debieten_FQ['HEZ5EF_FQ10R']
# FLOW: m3/h exclusief return flow. Extraction is negative. Infiltration is positive
tra_alias = {
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
    "ICAS-P-Ont": "-(CAWP01 + CAWP02 + CAWP03 + CAWP04 + CAWP05 + CAWP06)",
    "ICAS-Q-Ont": "-(CAWQ01 + CAWQ02 + CAWQ03 + CAWQ04 + CAWQ05 + CAWQ06)",
    "ICAS-PQ-Ont": "-(CAWP01 + CAWP02 + CAWP03 + CAWP04 + CAWP05 + CAWP06 + CAWQ01 + CAWQ02 + CAWQ03 + CAWQ04 + CAWQ05 + CAWQ06)",
    "NHDz-R-Ont": "-CAWRAF",
    "NHDz-S-Ont": "-CAWSAF",
    "NHDz-R+S-Ont": "-(CAWRAF + CAWSAF)",
    "ICAS-PQRS-Ont": "-(CAWP01 + CAWP02 + CAWP03 + CAWP04 + CAWP05 + CAWP06 + CAWQ01 + CAWQ02 + CAWQ03 + CAWQ04 + CAWQ05 + CAWQ06 + CAWRAF + CAWSAF)",
    "ICAS-spui": "4 * (CAWP01_FQ11R + CAWP02_FQ11R + CAWP03_FQ11R + CAWP04_FQ11R + CAWP05_FQ11R + CAWP06_FQ11R + CAWQ01_FQ11R + CAWQ02_FQ11R + CAWQ03_FQ11R + CAWQ04_FQ11R + CAWQ05_FQ11R + CAWQ06_FQ11R)",
    "IKIEF-spui": "4 * (HEW901_FQ11R + HEW902_FQ11R + HEW903_FQ11R + HEW904_FQ11R + HEW905_FQ11R + HEW906_FQ11R + HEW101_FQ11R + HEW102_FQ11R + HEW103_FQ11R + HEW104_FQ11R + HEW105_FQ11R + HEW106_FQ11R)",
    "ICAS-Inf": "-(CAA1DP + ICASDWATaanvoer - (HEI801 + HEI802 + HEI803 + HEI804 + HEI805 + HEI806 + HEI807 + HEI808 + HEI809 + HEI810 + HEI811 + HEI812 + HEI813 + HEI814 + HEI815 + HEI816 + HEI817 + HEI818 + HEI819 + HEI820 + HEW801 + HEW802 + HEW803 + HEW804 + HEW805 + HEW806 + HEW807 + HEW808 + HEW809 + HEW810 + HEW811 + HEW812))",
    "ICAS-PQRS-Netto": "-(CAWP01 + CAWP02 + CAWP03 + CAWP04 + CAWP05 + CAWP06 + CAWQ01 + CAWQ02 + CAWQ03 + CAWQ04 + CAWQ05 + CAWQ06 + CAWRAF + CAWSAF) + (CAA1DP + ICASDWATaanvoer - (HEI801 + HEI802 + HEI803 + HEI804 + HEI805 + HEI806 + HEI807 + HEI808 + HEI809 + HEI810 + HEI811 + HEI812 + HEI813 + HEI814 + HEI815 + HEI816 + HEI817 + HEI818 + HEI819 + HEI820 + HEW801 + HEW802 + HEW803 + HEW804 + HEW805 + HEW806 + HEW807 + HEW808 + HEW809 + HEW810 + HEW811 + HEW812))",
    "ICAS-PQ-Netto": "-(CAWP01 + CAWP02 + CAWP03 + CAWP04 + CAWP05 + CAWP06 + CAWQ01 + CAWQ02 + CAWQ03 + CAWQ04 + CAWQ05 + CAWQ06) + (CAA1DP + ICASDWATaanvoer - (HEI801 + HEI802 + HEI803 + HEI804 + HEI805 + HEI806 + HEI807 + HEI808 + HEI809 + HEI810 + HEI811 + HEI812 + HEI813 + HEI814 + HEI815 + HEI816 + HEI817 + HEI818 + HEI819 + HEI820 + HEW801 + HEW802 + HEW803 + HEW804 + HEW805 + HEW806 + HEW807 + HEW808 + HEW809 + HEW810 + HEW811 + HEW812))",
    "Bemaling": "CAA1DP",  # ECAS
    "IKIEF-9-1-Ont": "HEW901",
    "IKIEF-9-2-Ont": "HEW902",
    "IKIEF-9-3-Ont": "HEW903",
    "IKIEF-9-4-Ont": "HEW904",
    "IKIEF-9-5-Ont": "HEW905",
    "IKIEF-9-6-Ont": "HEW906",
    "IKIEF-9-Ont": "HEW901 + HEW902 + HEW903 + HEW904 + HEW905 + HEW906",
    "IKIEF-10-1-Ont": "HEW101",
    "IKIEF-10-2-Ont": "HEW102",
    "IKIEF-10-3-Ont": "HEW103",
    "IKIEF-10-4-Ont": "HEW104",
    "IKIEF-10-5-Ont": "HEW105",
    "IKIEF-10-6-Ont": "HEW106",
    "IKIEF-10-Ont": "HEW101 + HEW102 + HEW103 + HEW104 + HEW105 + HEW106",
    "IKIEF-9+10-Ont": "HEW901 + HEW902 + HEW903 + HEW904 + HEW905 + HEW906 + HEW101 + HEW102 + HEW103 + HEW104 + HEW105 + HEW106",
    "NHDz-A-Ont": "CAWAAF",
    "NHDz-H-Ont": "CAWHAA",
    "NHDz-4-Ont": "HEW4AA",
    "NHDz-HP-Ont": "HEWPAF",
    "NHDz-Tot-Excl-RS-Ont": "CAWAAF + CAWHAA + HEW4AA + HEWPAF",
    "NHDz-Tot-Incl-RS-Ont": "CAWAAF + CAWHAA + HEW4AA + HEWPAF + CAWRAF + CAWSAF",
    "BER-A-Ont": "BEWARU",
    "BER-B-Ont": "BEWBRU",
    "BER-C-Ont": "BEWCRU",
    "BER-HP-Ont": "BEWPRU",
    "BER-Tot-Ont": "BEWARU + BEWBRU + BEWCRU + BEWPRU",
    "Gooi-Laren-Z-Ont": "LAWLAAZUID",
    "Gooi-Laren-N-Ont": "LAWLAANOORD",
    "Gooi-Laren-Z+N-Ont": "LAWLAAZUID + LAWLAANOORD",
    "Gooi-Huizen-Ont": "HNWHAA",
    "Gooi-Tot-Ont": "LAWLAAZUID + LAWLAANOORD + HNWHAA",
    "DWAT-Ont": "HEW801 + HEW802 + HEW803 + HEW804 + HEW805 + HEW806 + HEW807 + HEW808 + HEW809 + HEW810 + HEW811 + HEW812",
    "DWAT-Inf": "HEI801 + HEI802 + HEI803 + HEI804 + HEI805 + HEI806 + HEI807 + HEI808 + HEI809 + HEI810 + HEI811 + HEI812 + HEI813 + HEI814 + HEI815 + HEI816 + HEI817 + HEI818 + HEI819 + HEI820",
    "DWAT-Netto": "-(HEI801 + HEI802 + HEI803 + HEI804 + HEI805 + HEI806 + HEI807 + HEI808 + HEI809 + HEI810 + HEI811 + HEI812 + HEI813 + HEI814 + HEI815 + HEI816 + HEI817 + HEI818 + HEI819 + HEI820 + HEW801 + HEW802 + HEW803 + HEW804 + HEW805 + HEW806 + HEW807 + HEW808 + HEW809 + HEW810 + HEW811 + HEW812)",
    # "ICAS-Inf": "ICASDWATaanvoer - (HEI801 + HEI802 + HEI803 + HEI804 + HEI805 + HEI806 + HEI807 + HEI808 + HEI809 + HEI810 + HEI811 + HEI812 + HEI813 + HEI814 + HEI815 + HEI816 + HEI817 + HEI818 + HEI819 + HEI820 + HEW801 + HEW802 + HEW803 + HEW804 + HEW805 + HEW806 + HEW807 + HEW808 + HEW809 + HEW810 + HEW811 + HEW812)"
}
"""
BER-A-Ont	BER-B-Ont	BER-C-Ont	BER-HP-Ont	BER-Tot-Ont	
Bemaling	
DWAT-Inf	DWAT-Netto	DWAT-Ont
ICAS-PQ-NettoICAS-PQRS-NettoNHDz-H-OntNHDz-4-OntICAS-PQRS-NettoICAS-PQ-NettoNHDz-R+S-OntICAS-PQ-NettoNHDz-H-OntNHDz-R-OntNHDz-S-OntICAS-PQ-NettoNHDz-R+S-OntNHDz-H-Ont
ICAS-PQRS-NettoDWAT-NettoNHDz-H-OntNHDz-A-OntICAS-PQRS-NettoICAS-PQ-NettoICAS-PQ-NettoNHDz-H-OntDWAT-NettoNHDz-R+S-OntICAS-PQRS-NettoNHDz-H-OntICAS-PQ-NettoDWAT-Netto
NHDz-H-OntNHDz-A-OntICAS-PQRS-NettoDWAT-NettoNHDz-H-OntNHDz-R+S-OntTATA_zout_tot_PWKBICAS-PQRS-NettoNHDz-A-OntNHDz-R+S-OntNHDz-A-OntNHDz-R+S-OntTATA_zout_tot_PWKB
NHDz-A-OntTATA_zout_tot_PWKBNHDz-R+S-OntNHDz-A-OntTATA_zout_tot_PWKBNHDz-A-OntNHDz-H-OntNHDz-R+S-OntICAS-PQRS-NettoDWAT-NettoNHDz-H-OntNHDz-4-OntNHDz-R+S-OntDWAT-Netto
NHDz-R+S-OntDWAT-NettoNHDz-R+S-OntTATA_zout_tot_PWKBNHDz-H-OntTATA_zout_tot_PWKBNHDz-R+S-OntTATA_zout_tot_PWKBDWAT-NettoNHDz-R+S-OntNHDz-A-OntICAS-PQ-NettoNHDz-H-OntNHDz-R+S-OntICAS-PQRS-NettoNHDz-H-OntNHDz-R+S-OntICAS-PQ-NettoNHDz-R+S-OntNHDz-H-OntNHDz-A-OntNHDz-R+S-OntNHDz-H-OntDWAT-NettoNHDz-R+S-OntDWAT-NettoNHDz-H-OntTATA_zout_tot_PWKBDWAT-NettoNHDz-H-OntNHDz-R+S-OntTATA_zout_tot_PWKBNHDz-R+S-OntDWAT-NettoNHDz-H-OntNHDz-R+S-OntDWAT-NettoNHDz-H-OntTATA_zout_tot_PWKBTATA_zout_tot_PWKBDWAT-NettoNHDz-R+S-OntTATA_zout_tot_PWKBTATA_zout_tot_PWKBNHDz-R+S-OntDWAT-NettoICAS-PQ-NettoTATA_zout_tot_PWKBDWAT-NettoNHDz-R+S-OntNHDz-H-OntTATA_zout_tot_PWKBDWAT-NettoICAS-PQRS-NettoNHDz-H-OntICAS-PQRS-NettoDWAT-NettoTATA_zout_tot_PWKBDWAT-NettoNHDz-A-OntNHDz-R+S-OntTATA_zout_tot_PWKBICAS-PQRS-NettoNHDz-A-OntNHDz-H-OntICAS-PQ-NettoNHDz-R+S-OntNHDz-H-OntNHDz-4-OntNHDz-4-OntICAS-PQ-NettoNHDz-4-OntNHDz-H-OntNHDz-R+S-OntICAS-PQ-NettoNHDz-4-OntNHDz-H-OntNHDz-H-OntNHDz-H-OntNHDz-4-OntICAS-PQ-NettoNHDz-4-OntICAS-PQ-NettoNHDz-H-OntICAS-PQ-NettoNHDz-R+S-OntNHDz-H-OntDWAT-NettoICAS-PQRS-NettoNHDz-4-OntICAS-PQ-NettoNHDz-4-OntNHDz-R+S-OntNHDz-H-OntICAS-PQ-NettoNHDz-R+S-OntNHDz-4-OntNHDz-H-OntNHDz-4-OntICAS-PQRS-NettoNHDz-H-OntICAS-PQRS-NettoICAS-PQ-NettoDWAT-NettoNHDz-H-OntNHDz-R+S-OntICAS-PQ-NettoDWAT-NettoNHDz-H-OntNHDz-4-OntNHDz-R+S-OntICAS-PQ-NettoNHDz-4-OntICAS-PQ-NettoNHDz-R+S-OntICAS-PQRS-NettoNHDz-H-OntNHDz-4-OntNHDz-R+S-OntICAS-PQ-NettoNHDz-H-OntNHDz-4-OntNHDz-R+S-OntICAS-PQ-NettoNHDz-R+S-OntDWAT-NettoNHDz-H-OntNHDz-4-OntNHDz-H-OntICAS-PQ-NettoNHDz-H-OntNHDz-4-OntIKIEF-9+10+Bas-NettoNHDz-4-OntNHDz-H-OntNHDz-R+S-OntICAS-PQRS-NettoNHDz-4-OntNHDz-H-OntICAS-PQ-NettoNHDz-4-OntICAS-PQ-NettoDWAT-NettoNHDz-H-OntNHDz-R-OntICAS-PQRS-NettoDWAT-NettoNHDz-4-OntICAS-PQRS-NettoIKIEF-9+10+Bas-NettoNHDz-H-OntICAS-PQ-NettoNHDz-R-OntNHDz-S-OntNHDz-H-OntNHDz-R+S-OntICAS-PQ-NettoNHDz-4-OntNHDz-H-OntICAS-PQ-NettoNHDz-4-OntNHDz-R+S-OntNHDz-4-OntICAS-PQRS-NettoNHDz-4-OntICAS-PQ-NettoNHDz-R-OntNHDz-S-OntNHDz-4-OntNHDz-H-OntICAS-PQRS-NettoDWAT-NettoNHDz-H-OntNHDz-4-OntNHDz-R+S-OntICAS-PQ-NettoNHDz-H-OntNHDz-4-OntNHDz-R+S-OntDWAT-NettoTATA_zout_tot_PWKBDWAT-NettoNHDz-H-OntNHDz-4-OntTATA_zout_tot_PWKBNHDz-H-OntNHDz-4-OntDWAT-NettoICAS-PQ-NettoNHDz-H-OntNHDz-R+S-OntNHDz-4-OntNHDz-R+S-OntNHDz-H-OntNHDz-H-OntNHDz-R+S-OntICAS-PQ-NettoDWAT-NettoNHDz-H-OntNHDz-R+S-OntICAS-PQ-NettoICAS-PQ-NettoNHDz-4-OntNHDz-H-OntIKIEF-9+10+Bas-NettoICAS-PQRS-NettoDWAT-NettoNHDz-4-OntIKIEF-9+10+Bas-NettoNHDz-4-OntNHDz-H-OntNHDz-R+S-OntIKIEF-9+10+Bas-NettoIKIEF-9+10+Bas-NettoNHDz-4-OntNHDz-H-OntICAS-PQ-NettoICAS-PQRS-NettoIKIEF-9+10+Bas-NettoDWAT-NettoNHDz-4-OntTATA_zout_tot_PWKBNHDz-H-OntNHDz-4-OntNHDz-R+S-OntNHDz-H-OntNHDz-4-OntNHDz-H-OntNHDz-4-OntNHDz-R+S-OntDWAT-NettoTATA_zout_tot_PWKBNHDz-H-OntNHDz-4-OntDWAT-NettoNHDz-H-OntNHDz-4-OntICAS-PQ-NettoNHDz-H-OntICAS-PQ-NettoNHDz-H-OntNHDz-4-OntICAS-PQRS-NettoNHDz-H-OntTATA_zout_tot_PWKBTATA_zout_tot_PWKBNHDz-H-OntDWAT-NettoTATA_zout_tot_PWKBICAS-PQRS-NettoIKIEF-9+10+Bas-NettoDWAT-NettoDWAT-NettoTATA_zout_tot_PWKBDWAT-NettoNHDz-R+S-OntNHDz-H-OntICAS-PQ-NettoNHDz-4-OntNHDz-H-OntNHDz-R-OntNHDz-R+S-OntDWAT-NettoTATA_zout_tot_PWKBNHDz-4-OntNHDz-R+S-OntDWAT-NettoNHDz-H-OntNHDz-4-OntDWAT-NettoTATA_zout_tot_PWKBNHDz-R+S-OntNHDz-4-OntNHDz-H-OntNHDz-4-OntICAS-PQ-NettoDWAT-NettoDWAT-NettoNHDz-H-OntNHDz-R+S-OntICAS-PQ-NettoDWAT-NettoNHDz-H-OntICAS-PQ-NettoTATA_zout_tot_PWKBDWAT-NettoNHDz-H-OntNHDz-H-OntICAS-PQ-NettoNHDz-4-OntNHDz-4-OntNHDz-H-OntNHDz-R+S-OntICAS-PQRS-NettoNHDz-R+S-OntNHDz-R+S-OntNHDz-H-OntNHDz-4-OntDWAT-NettoNHDz-H-OntNHDz-4-OntNHDz-R+S-OntICAS-PQ-NettoNHDz-H-OntNHDz-R+S-OntDWAT-NettoNHDz-R+S-OntNHDz-H-OntDWAT-NettoICAS-PQ-NettoDWAT-NettoTATA_zout_tot_PWKBNHDz-H-OntNHDz-R+S-OntNHDz-H-OntICAS-PQ-NettoNHDz-R+S-OntDWAT-NettoNHDz-H-OntICAS-PQ-NettoNHDz-R+S-OntTATA_zout_tot_PWKBDWAT-NettoNHDz-H-OntICAS-PQRS-NettoNHDz-H-OntICAS-PQRS-NettoDWAT-NettoNHDz-H-OntNHDz-R+S-OntICAS-PQ-NettoDWAT-NettoICAS-PQRS-NettoIKIEF-9+10+Bas-NettoDWAT-NettoNHDz-H-OntNHDz-R+S-OntNHDz-H-OntICAS-PQ-NettoNHDz-H-OntICAS-PQ-Netto

ICAS-PQ-Netto ICAS-PQRS-Netto NHDz-H-Ont NHDz-4-Ont ICAS-PQRS-Netto ICAS-PQ-Netto NHDz-R+S-Ont ICAS-PQ-Netto NHDz-H-Ont NHDz-R-Ont NHDz-S-Ont ICAS-PQ-Netto NHDz-R+S-Ont NHDz-H-Ont ICAS-PQRS-Netto DWAT-Netto NHDz-H-Ont NHDz-A-Ont ICAS-PQRS-Netto ICAS-PQ-Netto ICAS-PQ-Netto NHDz-H-Ont DWAT-Netto NHDz-R+S-Ont ICAS-PQRS-Netto NHDz-H-Ont ICAS-PQ-Netto DWAT-Netto NHDz-H-Ont NHDz-A-Ont ICAS-PQRS-Netto DWAT-Netto NHDz-H-Ont NHDz-R+S-Ont TATA_zout_tot_PWKB ICAS-PQRS-Netto NHDz-A-Ont NHDz-R+S-Ont NHDz-A-Ont NHDz-R+S-Ont TATA_zout_tot_PWKB NHDz-A-Ont TATA_zout_tot_PWKB NHDz-R+S-Ont NHDz-A-Ont TATA_zout_tot_PWKB NHDz-A-Ont NHDz-H-Ont NHDz-R+S-Ont ICAS-PQRS-Netto DWAT-Netto NHDz-H-Ont NHDz-4-Ont NHDz-R+S-Ont DWAT-Netto NHDz-R+S-Ont DWAT-Netto NHDz-R+S-Ont TATA_zout_tot_PWKB NHDz-H-Ont TATA_zout_tot_PWKB NHDz-R+S-Ont TATA_zout_tot_PWKB DWAT-Netto NHDz-R+S-Ont NHDz-A-Ont ICAS-PQ-Netto NHDz-H-Ont NHDz-R+S-Ont ICAS-PQRS-Netto NHDz-H-Ont NHDz-R+S-Ont ICAS-PQ-Netto NHDz-R+S-Ont NHDz-H-Ont NHDz-A-Ont NHDz-R+S-Ont NHDz-H-Ont DWAT-Netto NHDz-R+S-Ont DWAT-Netto NHDz-H-Ont TATA_zout_tot_PWKB DWAT-Netto NHDz-H-Ont NHDz-R+S-Ont TATA_zout_tot_PWKB NHDz-R+S-Ont DWAT-Netto NHDz-H-Ont NHDz-R+S-Ont DWAT-Netto NHDz-H-Ont TATA_zout_tot_PWKB TATA_zout_tot_PWKB DWAT-Netto NHDz-R+S-Ont TATA_zout_tot_PWKB TATA_zout_tot_PWKB NHDz-R+S-Ont DWAT-Netto ICAS-PQ-Netto TATA_zout_tot_PWKB DWAT-Netto NHDz-R+S-Ont NHDz-H-Ont TATA_zout_tot_PWKB DWAT-Netto ICAS-PQRS-Netto NHDz-H-Ont ICAS-PQRS-Netto DWAT-Netto TATA_zout_tot_PWKB DWAT-Netto NHDz-A-Ont NHDz-R+S-Ont TATA_zout_tot_PWKB ICAS-PQRS-Netto NHDz-A-Ont NHDz-H-Ont ICAS-PQ-Netto NHDz-R+S-Ont NHDz-H-Ont NHDz-4-Ont NHDz-4-Ont ICAS-PQ-Netto NHDz-4-Ont NHDz-H-Ont NHDz-R+S-Ont ICAS-PQ-Netto NHDz-4-Ont NHDz-H-Ont NHDz-H-Ont NHDz-H-Ont NHDz-4-Ont ICAS-PQ-Netto NHDz-4-Ont ICAS-PQ-Netto NHDz-H-Ont ICAS-PQ-Netto NHDz-R+S-Ont NHDz-H-Ont DWAT-Netto ICAS-PQRS-Netto NHDz-4-Ont ICAS-PQ-Netto NHDz-4-Ont NHDz-R+S-Ont NHDz-H-Ont ICAS-PQ-Netto NHDz-R+S-Ont NHDz-4-Ont NHDz-H-Ont NHDz-4-Ont ICAS-PQRS-Netto NHDz-H-Ont ICAS-PQRS-Netto ICAS-PQ-Netto DWAT-Netto NHDz-H-Ont NHDz-R+S-Ont ICAS-PQ-Netto DWAT-Netto NHDz-H-Ont NHDz-4-Ont NHDz-R+S-Ont ICAS-PQ-Netto NHDz-4-Ont ICAS-PQ-Netto NHDz-R+S-Ont ICAS-PQRS-Netto NHDz-H-Ont NHDz-4-Ont NHDz-R+S-Ont ICAS-PQ-Netto NHDz-H-Ont NHDz-4-Ont NHDz-R+S-Ont ICAS-PQ-Netto NHDz-R+S-Ont DWAT-Netto NHDz-H-Ont NHDz-4-Ont NHDz-H-Ont ICAS-PQ-Netto NHDz-H-Ont NHDz-4-Ont IKIEF-9+10+Bas-Netto NHDz-4-Ont NHDz-H-Ont NHDz-R+S-Ont ICAS-PQRS-Netto NHDz-4-Ont NHDz-H-Ont ICAS-PQ-Netto NHDz-4-Ont ICAS-PQ-Netto DWAT-Netto NHDz-H-Ont NHDz-R-Ont ICAS-PQRS-Netto DWAT-Netto NHDz-4-Ont ICAS-PQRS-Netto IKIEF-9+10+Bas-Netto NHDz-H-Ont ICAS-PQ-Netto NHDz-R-Ont NHDz-S-Ont NHDz-H-Ont NHDz-R+S-Ont ICAS-PQ-Netto NHDz-4-Ont NHDz-H-Ont ICAS-PQ-Netto NHDz-4-Ont NHDz-R+S-Ont NHDz-4-Ont ICAS-PQRS-Netto NHDz-4-Ont ICAS-PQ-Netto NHDz-R-Ont NHDz-S-Ont NHDz-4-Ont NHDz-H-Ont ICAS-PQRS-Netto DWAT-Netto NHDz-H-Ont NHDz-4-Ont NHDz-R+S-Ont ICAS-PQ-Netto NHDz-H-Ont NHDz-4-Ont NHDz-R+S-Ont DWAT-Netto TATA_zout_tot_PWKB DWAT-Netto NHDz-H-Ont NHDz-4-Ont TATA_zout_tot_PWKB NHDz-H-Ont NHDz-4-Ont DWAT-Netto ICAS-PQ-Netto NHDz-H-Ont NHDz-R+S-Ont NHDz-4-Ont NHDz-R+S-Ont NHDz-H-Ont NHDz-H-Ont NHDz-R+S-Ont ICAS-PQ-Netto DWAT-Netto NHDz-H-Ont NHDz-R+S-Ont ICAS-PQ-Netto ICAS-PQ-Netto NHDz-4-Ont NHDz-H-Ont IKIEF-9+10+Bas-Netto ICAS-PQRS-Netto DWAT-Netto NHDz-4-Ont IKIEF-9+10+Bas-Netto NHDz-4-Ont NHDz-H-Ont NHDz-R+S-Ont IKIEF-9+10+Bas-Netto IKIEF-9+10+Bas-Netto NHDz-4-Ont NHDz-H-Ont ICAS-PQ-Netto ICAS-PQRS-Netto IKIEF-9+10+Bas-Netto DWAT-Netto NHDz-4-Ont TATA_zout_tot_PWKB NHDz-H-Ont NHDz-4-Ont NHDz-R+S-Ont NHDz-H-Ont NHDz-4-Ont NHDz-H-Ont NHDz-4-Ont NHDz-R+S-Ont DWAT-Netto TATA_zout_tot_PWKB NHDz-H-Ont NHDz-4-Ont DWAT-Netto NHDz-H-Ont NHDz-4-Ont ICAS-PQ-Netto NHDz-H-Ont ICAS-PQ-Netto NHDz-H-Ont NHDz-4-Ont ICAS-PQRS-Netto NHDz-H-Ont TATA_zout_tot_PWKB TATA_zout_tot_PWKB NHDz-H-Ont DWAT-Netto TATA_zout_tot_PWKB ICAS-PQRS-Netto IKIEF-9+10+Bas-Netto DWAT-Netto DWAT-Netto TATA_zout_tot_PWKB DWAT-Netto NHDz-R+S-Ont NHDz-H-Ont ICAS-PQ-Netto NHDz-4-Ont NHDz-H-Ont NHDz-R-Ont NHDz-R+S-Ont DWAT-Netto TATA_zout_tot_PWKB NHDz-4-Ont NHDz-R+S-Ont DWAT-Netto NHDz-H-Ont NHDz-4-Ont DWAT-Netto TATA_zout_tot_PWKB NHDz-R+S-Ont NHDz-4-Ont NHDz-H-Ont NHDz-4-Ont ICAS-PQ-Netto DWAT-Netto DWAT-Netto NHDz-H-Ont NHDz-R+S-Ont ICAS-PQ-Netto DWAT-Netto NHDz-H-Ont ICAS-PQ-Netto TATA_zout_tot_PWKB DWAT-Netto NHDz-H-Ont NHDz-H-Ont ICAS-PQ-Netto NHDz-4-Ont NHDz-4-Ont NHDz-H-Ont NHDz-R+S-Ont ICAS-PQRS-Netto NHDz-R+S-Ont NHDz-R+S-Ont NHDz-H-Ont NHDz-4-Ont DWAT-Netto NHDz-H-Ont NHDz-4-Ont NHDz-R+S-Ont ICAS-PQ-Netto NHDz-H-Ont NHDz-R+S-Ont DWAT-Netto NHDz-R+S-Ont NHDz-H-Ont DWAT-Netto ICAS-PQ-Netto DWAT-Netto TATA_zout_tot_PWKB NHDz-H-Ont NHDz-R+S-Ont NHDz-H-Ont ICAS-PQ-Netto NHDz-R+S-Ont DWAT-Netto NHDz-H-Ont ICAS-PQ-Netto NHDz-R+S-Ont TATA_zout_tot_PWKB DWAT-Netto NHDz-H-Ont ICAS-PQRS-Netto NHDz-H-Ont ICAS-PQRS-Netto DWAT-Netto NHDz-H-Ont NHDz-R+S-Ont ICAS-PQ-Netto DWAT-Netto ICAS-PQRS-Netto IKIEF-9+10+Bas-Netto DWAT-Netto NHDz-H-Ont NHDz-R+S-Ont NHDz-H-Ont ICAS-PQ-Netto NHDz-H-Ont ICAS-PQ-Netto

ICAS-P-Ont	ICAS-P1-Ont	ICAS-P2-Ont	ICAS-P3-Ont	ICAS-P4-Ont	ICAS-P5-Ont	ICAS-P6-Ont	ICAS-PQ-Inf	ICAS-PQ-Netto	ICAS-PQ-Ont	ICAS-PQRS-Netto	ICAS-PQRS-Ont	ICAS-Q-Ont	ICAS-Q1-Ont	ICAS-Q2-Ont	ICAS-Q3-Ont	ICAS-Q4-Ont	ICAS-Q5-Ont	ICAS-Q6-Ont	ICAS_Noord_MPBS+O/2	ICAS_inf	ICAS_ontt_tot	ICAS_zuid_NQCR+O/2	IKIEF-10-1-Ont	IKIEF-10-2-Ont	IKIEF-10-3-Ont	IKIEF-10-4-Ont	IKIEF-10-5-Ont	IKIEF-10-6-Ont	IKIEF-10-Ont	IKIEF-9+10+Bas-Netto	IKIEF-9+10-Inf	IKIEF-9+10-Netto	IKIEF-9+10-Ont	IKIEF-9-1-Ont	IKIEF-9-2-Ont	IKIEF-9-3-Ont	IKIEF-9-4-Ont	IKIEF-9-5-Ont	IKIEF-9-6-Ont	IKIEF-9-Ont	IKIEF-Bassin-Netto	IKIEF_inf	IKIEF_noord_7+10	IKIEF_ontt_tot	IKIEF_zuid_6+9	Jaar	NHDz-1-Ont	NHDz-2-Ont	NHDz-3-Ont	NHDz-4-Ont	NHDz-5-Ont	NHDz-6-Ont	NHDz-7-Ont	NHDz-A-Ont	NHDz-B-Ont	NHDz-Cdui-Ont	NHDz-Cinf-Ont	NHDz-D-Ont	NHDz-E-Ont	NHDz-F-Ont	NHDz-G-Ont	NHDz-H-Ont	NHDz-HP-Ont	NHDz-HPcas-Ont	NHDz-J-Ont	NHDz-L-Ont	NHDz-M-Ont	NHDz-N-Ont	NHDz-O-Ont	NHDz-R+S-Ont	NHDz-R-Ont	NHDz-S-Ont	NHDz-Tot-Excl-RS-Ont	NHDz-Tot-Incl-RS-Ont	TATA_KF1	TATA_PB	TATA_PK	TATA_PW	TATA_Q004	TATA_Q107	TATA_Q110	TATA_Q142	TATA_Q142+Q143	TATA_Q143	TATA_Q154	TATA_S_ondiep_midden	TATA_Tijdelijk	TATA_Tot_Excl_zout_GW	TATA_Totaal	TATA_tot_SenPWKB	TATA_zout_tot_PWKB
Secundair_NHDzuid=['CAWRAF','CAWSAF','CAWAAF','CAWHAA','HEW4AA','HEWPAF']
Onttrekking_def['DWAT-Ont']=Debieten_FQ['HEW8AF_FQ10R']

Onttrekking_def['NHDz-R-Ont']=Debieten_FQ['CAWRAF_FQ10R']
Onttrekking_def['NHDz-S-Ont']=Debieten_FQ['CAWSAF_FQ10R']

Onttrekking_def['NHDz-A-Ont']=Debieten_FQ['CAWAAF_FQ10R']
Onttrekking_def['NHDz-H-Ont']=Debieten_FQ['CAWHAA_FQ10R']
Onttrekking_def['NHDz-4-Ont']=Debieten_FQ['HEW4AA_FQ10R']
Onttrekking_def['NHDz-HP-Ont']=np.where(Onttrekking_def['Jaar']==2012,Debieten_FT_dag['HEWPAF_FT10'],Debieten_FQ['HEWPAF_FQ10R'])

Onttrekking_def['BER-A-Ont']=np.where(Debieten_FQ['BEWARU_FQ10R']==2004,Debieten_FT_dag['BEWARU_FT10'],Debieten_FQ['BEWARU_FQ10R'])
Onttrekking_def['BER-B-Ont']=np.where((Debieten_FQ['BEWBRU_FQ10R']==2016)|(Debieten_FQ['BEWBRU_FQ10R']==2017),Debieten_FT_dag['BEWBRU_FT10'],Debieten_FQ['BEWBRU_FQ10R'])
Onttrekking_def['BER-C-Ont']=Debieten_FQ['BEWCRU_FQ10R']
Onttrekking_def['BER-HP-Ont']=Debieten_FQ['BEWPRU_FQ10R']


Secundair_duin_dag=['NHDz-A-Ont','NHDz-4-Ont','NHDz-H-Ont','BER-A-Ont','BER-B-Ont','BER-C-Ont']
Secundair_NHDzuid_dag=list(Onttrekking_def.columns[Onttrekking_def.columns.str.contains(pat = 'NHDzuid')]) 
Secundair_Bergen_dag=list(Onttrekking_def.columns[Onttrekking_def.columns.str.contains(pat = 'BER')]) 
Secundair_IKIEF_9_dag=list(Onttrekking_def.columns[Onttrekking_def.columns.str.contains(pat = 'IKIEF-9')])
Secundair_IKIEF_10_dag=list(Onttrekking_def.columns[Onttrekking_def.columns.str.contains(pat = 'IKIEF-10')])
Secundair_ICAS_P_dag=list(Onttrekking_def.columns[Onttrekking_def.columns.str.contains(pat = 'ICAS-P')])
Secundair_ICAS_Q_dag=list(Onttrekking_def.columns[Onttrekking_def.columns.str.contains(pat = 'ICAS-Q')])


Onttrekking_dag_infiltratiewater=pd.DataFrame(index=Onttrekking_def.index)
Onttrekking_dag_infiltratiewater['Jaar']=Onttrekking_def['Jaar']
Onttrekking_dag_infiltratiewater['ICAS']=(Onttrekking_def[Secundair_ICAS_P_dag].sum(axis=1))+(Onttrekking_def[Secundair_ICAS_Q_dag].sum(axis=1))
Onttrekking_dag_infiltratiewater['ICAS incl. RS']=(Onttrekking_def[Secundair_ICAS_P_dag].sum(axis=1))+(Onttrekking_def[Secundair_ICAS_Q_dag].sum(axis=1))+Onttrekking_def['NHDz-R-Ont']+Onttrekking_def['NHDz-S-Ont']
Onttrekking_dag_infiltratiewater['IKIEF']=(Onttrekking_def[Secundair_IKIEF_9_dag].sum(axis=1))+(Onttrekking_def[Secundair_IKIEF_10_dag].sum(axis=1))

Onttrekking_def['ICAS-P-Ont']=Onttrekking_def[Secundair_ICAS_P_dag].sum(axis=1)
Onttrekking_def['ICAS-Q-Ont']=Onttrekking_def[Secundair_ICAS_Q_dag].sum(axis=1)
Onttrekking_def['ICAS-PQ-Ont']=(Onttrekking_def[Secundair_ICAS_P_dag].sum(axis=1))+(Onttrekking_def[Secundair_ICAS_Q_dag].sum(axis=1))
Onttrekking_def['ICAS-PQRS-Ont']=(Onttrekking_def[Secundair_ICAS_P_dag].sum(axis=1))+(Onttrekking_def[Secundair_ICAS_Q_dag].sum(axis=1))+Onttrekking_def['NHDz-R-Ont']+Onttrekking_def['NHDz-S-Ont']
Onttrekking_def['NHDz-R+S-Ont'] = Onttrekking_def['NHDz-R-Ont'] + Onttrekking_def['NHDz-S-Ont']

Onttrekking_def['IKIEF-9-Ont']=Onttrekking_def[Secundair_IKIEF_9_dag].sum(axis=1)
Onttrekking_def['IKIEF-10-Ont']=Onttrekking_def[Secundair_IKIEF_10_dag].sum(axis=1)
Onttrekking_def['IKIEF-9+10-Ont']=(Onttrekking_def[Secundair_IKIEF_9_dag].sum(axis=1))+(Onttrekking_def[Secundair_IKIEF_10_dag].sum(axis=1))

Onttrekking_def['BER-Tot-Ont']= (Onttrekking_def[Secundair_Bergen_dag].sum(axis=1))
Onttrekking_def['NHDz-Tot-Excl-RS-Ont']= (Onttrekking_def[Secundair_NHDzuid_dag].sum(axis=1))-Onttrekking_def['NHDz-R-Ont']-Onttrekking_def['NHDz-S-Ont']
Onttrekking_def['NHDz-Tot-Incl-RS-Ont']= (Onttrekking_def[Secundair_NHDzuid_dag].sum(axis=1))

Onttrekking_def['Bemaling']= Debieten_FT ['CAA1DP_FT10']


Onttrekking_dag_infiltratiewater['DWAT']=Onttrekking_def['DWAT-Ont']
#Onttrekking_dag_infiltratiewater['Totaal']=Onttrekking_dag_infiltratiewater['ICAS']+Onttrekking_dag_infiltratiewater['IKIEF']+Onttrekking_dag_infiltratiewater['DWAT']
Onttrekking_dag_infiltratiewater['Totaal']=Onttrekking_dag_infiltratiewater['ICAS incl. RS']+Onttrekking_dag_infiltratiewater['IKIEF']+Onttrekking_dag_infiltratiewater['DWAT']

Onttrekking_dag_duinwater=pd.DataFrame(index=Onttrekking_def.index)
Onttrekking_dag_duinwater['Jaar']=Onttrekking_def['Jaar']
Onttrekking_dag_duinwater['Bergen']=(Onttrekking_def[Secundair_Bergen_dag].sum(axis=1))
Onttrekking_dag_duinwater['NHDzuid incl. RS']=(Onttrekking_def[Secundair_NHDzuid_dag].sum(axis=1))
Onttrekking_dag_duinwater['NHDzuid']=(Onttrekking_def[Secundair_NHDzuid_dag].sum(axis=1))-Onttrekking_def['NHDz-R-Ont']-Onttrekking_def['NHDz-S-Ont']
Onttrekking_dag_duinwater['Totaal']=Onttrekking_dag_duinwater['Bergen']+Onttrekking_dag_duinwater['NHDzuid']

# incl. Gooi:
Onttrekking_def ['Gooi-Laren-Z-Ont'] = Debieten_FQ ['LAWLAA_FQ20R']
Onttrekking_def ['Gooi-Laren-N-Ont'] = Debieten_FQ ['LAWLAA_FQ10R']
Onttrekking_def ['Gooi-Laren-Z+N-Ont'] = Debieten_FQ ['LAWLAA_FQ20R'] + Debieten_FQ ['LAWLAA_FQ10R']
Onttrekking_def ['Gooi-Huizen-Ont'] = Debieten_FQ ['HNWHAA_FQ10P']
Onttrekking_def ['Gooi-Tot-Ont'] = Debieten_FQ ['LAWLAA_FQ20R'] + Debieten_FQ ['LAWLAA_FQ10R'] + Debieten_FQ ['HNWHAA_FQ10P']

Onttrekking_def.to_excel(Filelocatie_input +'Onttrekking_def.xlsx', sheet_name='Onttrekking_def')


Secundair_infiltratiewater_dag=['ICAS','ICAS incl. RS','IKIEF','DWAT']

#Infiltratie def


Infiltratie_def=pd.DataFrame(index=Onttrekking_def.index)
Infiltratie_def['Jaar']=Onttrekking_def['Jaar']

Infiltratie_def['DWAT-Inf']=Infiltratie_totaal['Infiltratie DWAT']
Infiltratie_def['ICAS-PQ-Inf']=Infiltratie_totaal['Infiltratie ICAS+bedrijfswater+spui']
Infiltratie_def['IKIEF-9+10-Inf']=Infiltratie_totaal['Infiltratie IKIEF+bedrijfswater+spui']
Infiltratie_def['Totaal']=Infiltratie_def['DWAT-Inf']+Infiltratie_def['ICAS-PQ-Inf']+Infiltratie_def['IKIEF-9+10-Inf']


Infiltratie_def.to_excel(Filelocatie_input +'Infiltratie_def.xlsx', sheet_name='Infiltratie_def')

# Netto = ont-inf

Netto_def=pd.DataFrame(index=Onttrekking_def.index)
Netto_def['Jaar']=Onttrekking_def['Jaar']

Netto_def['DWAT-Netto']= Onttrekking_def['DWAT-Ont'] - Infiltratie_totaal['Infiltratie DWAT']
Netto_def['ICAS-PQ-Netto']= Onttrekking_def['ICAS-PQ-Ont'] - Infiltratie_totaal['Infiltratie ICAS+bedrijfswater+spui']
Netto_def['ICAS-PQRS-Netto']= Onttrekking_def['ICAS-PQRS-Ont'] - Infiltratie_totaal['Infiltratie ICAS+bedrijfswater+spui']
Netto_def['IKIEF-9+10-Netto']= Onttrekking_def['IKIEF-9+10-Ont'] - Infiltratie_totaal['Infiltratie IKIEF+bedrijfswater+spui']
Netto_def['IKIEF-Bassin-Netto']= Debieten_FQ ['HEIDBA_FQ10R'] - ( Debieten_FQ['HEZS01_FQ10R'] + Debieten_FQ ['HEZS02_FQ10R'] )
Netto_def['IKIEF-9+10+Bas-Netto'] = Netto_def['IKIEF-9+10-Netto'] + Netto_def['IKIEF-Bassin-Netto']

Netto_def.to_excel(Filelocatie_input +'Netto_def.xlsx', sheet_name='Netto_def')
"""


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

    tags = list(filter(lambda s: "_" in s, comb.split(" ")))
    print("\t".join(tags))
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


def get_plenty_data(fp):
    """Returns the Plenty data from the file `fp`

    Parameters
    ----------
    fp : str
        Path to Plenty data

    Returns
    -------
    data : pd.DataFrame
        Plenty data
    """
    data = pd.read_excel(fp, skiprows=9, index_col="ophaal tijdstip", na_values=["EOF"])
    return data
