import os

from dawacotools import get_daw_filters


fp_out = os.path.join(os.path.abspath(__file__), "..", "data", "filters.gpkg")

filters = get_daw_filters()
filters.to_file(fp_out, driver="GPKG")
