
from dawacotools.plot import plot_daw_mp
from dawacotools.io import get_daw_filters, get_daw_mps

f = get_daw_filters(mpcode="09BZW012")
mpcode = "15CZW1004"
fig = plot_daw_mp(mpcode=mpcode)

print("hoi")