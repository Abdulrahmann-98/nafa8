#!/usr/bin/env python3
"""
Quick checks that call loaders.py and report:
- WRF dims & proj
- Emissions dims & IOAPI proj
- Simple grid compatibility verdict
- Boundary files found
"""
from loaders import load_paths, open_wrf, open_emissions, read_boundaries, get_wrf_proj_attrs, get_ioapi_proj_attrs, grids_roughly_match

def main():
    paths = load_paths()
    print("Paths:", paths)

    ds_w = open_wrf()
    wrf_attrs = get_wrf_proj_attrs(ds_w)
    print("\nWRF attrs:", wrf_attrs)
    print("WRF dims:", dict(ds_w.dims))

    ds_e = open_emissions()
    emi_attrs = get_ioapi_proj_attrs(ds_e)
    print("\nEmissions attrs:", emi_attrs)
    print("Emissions dims:", dict(ds_e.dims))

    verdict = grids_roughly_match(wrf_attrs, emi_attrs)
    print("\nGrid-compat verdict:", verdict)

    polys = read_boundaries()
    print("\nBoundaries:", {k: v.shape for k, v in polys.items()})

if __name__ == "__main__":
    main()

