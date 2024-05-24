from dawacotools import get_daw_mps
from dawacotools.analysis import get_cluster_mps

mps = get_daw_mps()
col, icol = get_cluster_mps(mps, r_max=1.5, min_cluster_size=2)
