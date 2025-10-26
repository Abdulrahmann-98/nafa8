#!/usr/bin/env python3
"""
Quick sanity checker for NAFA8 paths & data.

- Reads important_paths.yaml (preferred) or falls back to important_paths.txt
- Prints key directories
- Summarizes one WRF wrfout file (dims, calendar)
- Summarizes one emissions file (dims, IOAPI attrs)
- Reads first lines of boundaries polygons (lon/lat)
- Lists a few FLEXPART outputs (flxout_* or partposit_*)
"""

import os, re, sys, pathlib, textwrap

# Optional deps: xarray/netCDF4 for WRF/emissions; pandas for boundaries
try:
    import xarray as xr
except Exception:
    xr = None

try:
    import yaml
except Exception:
    yaml = None

def load_paths():
    root = pathlib.Path(".")
    yml = root / "important_paths.yaml"
    txt = root / "important_paths.txt"

    paths = {}
    if yml.exists() and yaml:
        with yml.open() as f:
            cfg = yaml.safe_load(f)
        # Flatten the bits we need
        paths["flex_runs_dir"] = cfg["flexpart"]["runs_dir"]
        paths["flex_main_run"] = cfg["flexpart"]["main_run"]
        paths["wrf_campaign_dir"] = cfg["wrf"]["campaign_dir"]
        paths["wrf_sample"] = cfg["wrf"].get("sample_file")
        paths["emissions_dir"] = cfg["emissions"]["base_dir"]
        paths["emissions_sample"] = cfg["emissions"].get("sample_file")
        paths["boundaries_dir"] = cfg["boundaries"]["dir"]
        return paths

    # Fallback: parse simple KEY=VALUE lines in important_paths.txt
    if txt.exists():
        with txt.open() as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"): 
                    continue
                if "=" in line:
                    k, v = line.split("=", 1)
                    paths[k.strip()] = v.strip()
        # Try to normalize to the keys we use below
        paths = {
            "flex_runs_dir": paths.get("FLEX_RUNS_DIR"),
            "wrf_campaign_dir": paths.get("WRF_CAMPAIGN_DIR"),
            "emissions_dir": paths.get("EMISSION_DIR"),
            "boundaries_dir": paths.get("BOUNDARIES_DIR"),
        }
        return paths

    print("No important_paths.yaml or important_paths.txt found.", file=sys.stderr)
    sys.exit(1)

def pick_one(patterns, base, limit=1):
    base = pathlib.Path(base)
    if not base.exists():
        return []
    found = []
    for pat in patterns:
        found += list(base.glob(pat))
    found = sorted(set(found))
    return found[:limit]

def summarize_wrf(wrf_dir, wrf_sample=None):
    print("\n[WRF]")
    print("dir:", wrf_dir)
    if wrf_sample:
        candidate = pathlib.Path(wrf_dir) / wrf_sample
        if candidate.exists():
            wrf_files = [candidate]
        else:
            # wrf_sample may be a symlink name with colons; search by prefix
            wrf_files = pick_one(["wrfout_d02_*"], wrf_dir, limit=1)
    else:
        wrf_files = pick_one(["wrfout_d02_*"], wrf_dir, limit=1)

    if not wrf_files:
        print("  (no wrfout files found)")
        return

    f = wrf_files[0]
    print("file:", f)
    if xr is None:
        print("  xarray not available; skipping metadata open.")
        return
    try:
        ds = xr.open_dataset(f, engine="netcdf4")
        dims = dict(ds.dims)
        vars_ = list(ds.data_vars)[:10]
        print("dims:", dims)
        print("vars (first 10):", vars_)
        if "Times" in ds.variables:
            t = ds["Times"].isel(Time=slice(0,3))
            print("Times sample (first 3):", t.values)
    except Exception as e:
        print("  ERROR opening WRF:", e)

def summarize_emissions(emi_dir, emi_sample=None):
    print("\n[Emissions]")
    print("dir:", emi_dir)
    base = pathlib.Path(emi_dir)
    if not base.exists():
        print("  (dir missing)")
        return
    if emi_sample and (base / emi_sample).exists():
        files = [base / emi_sample]
    else:
        # try to find a NetCDF in common subdirs
        files = []
        for sub in ["onroad", "nonroad", "airports", "residential_gas", "."]:
            files += pick_one(["*.nc"], base / sub, limit=1)
            if files:
                break
    if not files:
        print("  (no .nc found)")
        return
    f = files[0]
    print("file:", f)
    if xr is None:
        print("  xarray not available; skipping metadata open.")
        return
    try:
        ds = xr.open_dataset(f, engine="netcdf4")
        dims = dict(ds.dims)
        vars_ = list(ds.data_vars)[:10]
        print("dims:", dims)
        print("vars (first 10):", vars_)
        # IOAPI attrs if present
        for k in ["NCOLS","NROWS","NLAYS","GDTYP","P_ALP","P_BET","P_GAM","XCELL","YCELL","XORIG","YORIG","GDNAM"]:
            if k in ds.attrs:
                print(f"attr {k}:", ds.attrs[k])
    except Exception as e:
        print("  ERROR opening emissions:", e)

def summarize_boundaries(bdir):
    print("\n[Boundaries]")
    print("dir:", bdir)
    base = pathlib.Path(bdir)
    if not base.exists():
        print("  (dir missing)")
        return
    txts = pick_one(["*.txt"], base, limit=3)
    if not txts:
        print("  (no .txt polygons)")
        return
    for f in txts:
        print("file:", f.name)
        try:
            with open(f) as fh:
                lines = [next(fh) for _ in range(10)]
            print("  head:", "".join(lines).strip().splitlines()[:4], "...")
        except Exception as e:
            print("  ERROR reading:", e)

def summarize_flexpart_runs(runs_dir, main_rel="test_backward_CTC/first_trial"):
    print("\n[FLEXPART runs]")
    print("dir:", runs_dir)
    base = pathlib.Path(runs_dir)
    if not base.exists():
        print("  (dir missing)")
        return
    subdirs = [p for p in base.iterdir() if p.is_dir()]
    print("subdirs:", [p.name for p in subdirs])
    # list a few outputs from the main run if present
    main = base / main_rel
    if main.exists():
        outs = pick_one(["flxout_*.nc","partposit_*","*.txt"], main, limit=5)
        print("example outputs:", [p.name for p in outs])

def main():
    paths = load_paths()
    summarize_wrf(paths.get("wrf_campaign_dir"), paths.get("wrf_sample"))
    summarize_emissions(paths.get("emissions_dir"), paths.get("emissions_sample"))
    summarize_boundaries(paths.get("boundaries_dir"))
    summarize_flexpart_runs(paths.get("flex_runs_dir"))
    print("\nDone.")

if __name__ == "__main__":
    main()

