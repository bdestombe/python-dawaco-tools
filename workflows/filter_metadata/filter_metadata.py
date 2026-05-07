from dawacotools.io import get_daw_filters
from dawacotools.io import get_daw_ts_temp

get_daw_ts_temp(mpcode="19CNL5150")

filters = get_daw_filters(vervallen_filters_meenemen=True)
print(filters)
filters.to_excel("filters.xlsx")
filters.to_file("filters_incl_vervallen.gpkg", driver="GPKG")
filters.to_file("filters_incl_vervallen.geoJSON", driver="GeoJSON")
