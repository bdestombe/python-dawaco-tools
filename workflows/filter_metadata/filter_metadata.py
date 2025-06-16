from dawacotools.io import get_daw_filters

filters = get_daw_filters(vervallen_filters_meenemen=True)
print(filters)
filters.to_excel("filters.xlsx")
