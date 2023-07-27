import dawacotools as dt

wps = dt.get_daw_filters(mpcode="19CNL5389")
out = dt.potential_to_flow(
    mpcode1="19CNL5389",
    mpcode2="19CNL5390",
    filternr1=None,
    filternr2=None,
    dh1=None,
    dh2=None,
    hydraulic_conductivity=None,
    porosity=0.35,
)