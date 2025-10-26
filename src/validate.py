#!/usr/bin/env python3
import sys, yaml, xarray as xr, pandas as pd
from loaders import load_paths, open_wrf, open_emissions, read_boundaries, get_wrf_proj_attrs, get_ioapi_proj_attrs

def fail(msg): print("ERROR:", msg); sys.exit(1)

def main():
    reg = yaml.safe_load(open("docs/datasets.yaml"))
    paths = load_paths()

    # WRF
    ds_w = open_wrf()
    wrf_dims = dict(ds_w.dims)
    target = reg["wrf"]["dims"]
    for k,v in target.items():
        if k not in wrf_dims or wrf_dims[k] != v:
            fail(f"WRF dim mismatch {k}: got {wrf_dims.get(k)} expected {v}")
    for rv in reg["wrf"]["required_vars"]:
        if rv not in ds_w.variables:
            fail(f"Missing WRF var: {rv}")

    # Emissions
    ds_e = open_emissions()
    emi_dims = dict(ds_e.dims)
    for k,v in reg["emissions"]["dims"].items():
        if k not in emi_dims or emi_dims[k] != v:
            fail(f"Emiss dim mismatch {k}: got {emi_dims.get(k)} expected {v}")
    if reg["emissions"]["var"] not in ds_e.variables:
        fail("Missing emissions var 'emiss'")

    # Boundaries
    polys = read_boundaries()
    needed = [f.split(".")[0] for f in reg["boundaries"]["files"]]
    for name in needed:
        if name not in polys:
            fail(f"Boundary missing: {name}")

    print("validate.py: OK")
if __name__ == "__main__":
    main()

