#!/usr/bin/env python3
"""
Lightweight loaders for NAFA8 (Python 3.8 compatible).

Functions:
- load_paths(): read important_paths.yaml (or fallback to .txt)
- open_wrf(sample=None): returns xarray.Dataset for one wrfout file
- open_emissions(sample=None): returns xarray.Dataset for one emissions file
- read_boundaries(): returns dict[name] -> DataFrame(lon, lat)
- get_wrf_proj_attrs(ds): extract key Lambert params from WRF
- get_ioapi_proj_attrs(ds): extract Lambert params from IOAPI emissions
- grids_roughly_match(wrf_attrs, ioapi_attrs): coarse alignment check
"""

from pathlib import Path
from typing import Optional, List, Dict, Any

import xarray as xr
import pandas as pd
import yaml


def load_paths(repo_root: Optional[Path] = None) -> Dict[str, Any]:
    root = Path(".") if repo_root is None else Path(repo_root)
    yml = root / "important_paths.yaml"
    txt = root / "important_paths.txt"
    paths: Dict[str, Any] = {}

    if yml.exists():
        with yml.open() as f:
            cfg = yaml.safe_load(f)
        paths["wrf_dir"] = cfg["wrf"]["campaign_dir"]
        paths["wrf_sample"] = cfg["wrf"].get("sample_file")
        paths["emi_dir"] = cfg["emissions"]["base_dir"]
        paths["emi_sample"] = cfg["emissions"].get("sample_file")
        paths["runs_dir"] = cfg["flexpart"]["runs_dir"]
        paths["main_run_rel"] = cfg["flexpart"].get("main_run", "")
        paths["boundaries_dir"] = cfg["boundaries"]["dir"]
        return paths

    if txt.exists():
        raw: Dict[str, str] = {}
        with txt.open() as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                raw[k.strip()] = v.strip()
        return {
            "wrf_dir": raw.get("WRF_CAMPAIGN_DIR"),
            "emi_dir": raw.get("EMISSION_DIR"),
            "runs_dir": raw.get("FLEX_RUNS_DIR"),
            "boundaries_dir": raw.get("BOUNDARIES_DIR"),
        }

    raise FileNotFoundError("important_paths.yaml or important_paths.txt not found.")


def _pick_one(base: Path, patterns: List[str]) -> Optional[Path]:
    for pat in patterns:
        hits = sorted(base.glob(pat))
        if hits:
            return hits[0]
    return None


def open_wrf(sample: Optional[str] = None, engine: str = "netcdf4") -> xr.Dataset:
    p = load_paths()
    wrf_dir = Path(p["wrf_dir"])
    candidate = (wrf_dir / sample) if sample else None
    f = candidate if (candidate and candidate.exists()) else _pick_one(wrf_dir, ["wrfout_d02_*"])
    if f is None:
        raise FileNotFoundError("No wrfout_d02_* file found.")
    return xr.open_dataset(f, engine=engine)


def open_emissions(sample: Optional[str] = None, engine: str = "netcdf4") -> xr.Dataset:
    p = load_paths()
    base = Path(p["emi_dir"])
    if sample and (base / sample).exists():
        f = base / sample
    else:
        f = None
        for sub in ["onroad", "nonroad", "airports", "residential_gas", "residential_wood", "."]:
            f = _pick_one(base / sub, ["*.nc"])
            if f:
                break
    if f is None:
        raise FileNotFoundError("No emissions .nc found.")
    return xr.open_dataset(f, engine=engine)


def read_boundaries() -> Dict[str, pd.DataFrame]:
    p = load_paths()
    bdir = Path(p["boundaries_dir"])
    out: Dict[str, pd.DataFrame] = {}
    for f in sorted(bdir.glob("*.txt")):
        df = pd.read_csv(f, skiprows=2, header=None, names=["lon", "lat", "z"])
        out[f.stem] = df[["lon", "lat"]].copy()
    return out


def get_wrf_proj_attrs(ds: xr.Dataset) -> Dict[str, Any]:
    attrs: Dict[str, Any] = {}
    for k in ["TRUELAT1", "TRUELAT2", "STAND_LON", "CEN_LAT", "CEN_LON", "DX", "DY", "MAP_PROJ"]:
        if k in ds.attrs:
            attrs[k] = ds.attrs[k]
    for k in ["west_east", "south_north"]:
        if k in ds.dims:
            attrs[k] = int(ds.dims[k])
    return attrs


def get_ioapi_proj_attrs(ds: xr.Dataset) -> Dict[str, Any]:
    keys = ["P_ALP", "P_BET", "P_GAM", "XCELL", "YCELL", "XORIG", "YORIG", "NCOLS", "NROWS", "GDTYP", "GDNAM"]
    out: Dict[str, Any] = {}
    for k in keys:
        if k in ds.attrs:
            out[k] = ds.attrs[k]
    for k in ["x", "y", "time", "LAY"]:
        if k in ds.dims:
            out[k] = int(ds.dims[k])
    return out


def grids_roughly_match(wrf: Dict[str, Any], ioapi: Dict[str, Any],
                        angle_tol: float = 0.25, cell_tol: float = 100.0) -> Dict[str, bool]:
    """
    Very coarse check:
      TRUELAT1 ≈ P_ALP, TRUELAT2 ≈ P_BET, STAND_LON ≈ P_GAM
      DX ≈ XCELL, DY ≈ YCELL (within ~100 m)
      west_east ≈ NCOLS (±5), south_north ≈ NROWS (±5)
    """
    res: Dict[str, bool] = {}
    try:
        if all(k in wrf for k in ["TRUELAT1", "TRUELAT2", "STAND_LON"]):
            res["lat1_ok"] = abs(float(wrf["TRUELAT1"]) - float(ioapi.get("P_ALP", wrf["TRUELAT1"]))) <= angle_tol
            res["lat2_ok"] = abs(float(wrf["TRUELAT2"]) - float(ioapi.get("P_BET", wrf["TRUELAT2"]))) <= angle_tol
            res["lon_ok"]  = abs(float(wrf["STAND_LON"]) - float(ioapi.get("P_GAM", wrf["STAND_LON"]))) <= angle_tol
        if "DX" in wrf and "XCELL" in ioapi:
            res["dx_ok"] = abs(float(wrf["DX"]) - float(ioapi["XCELL"])) <= cell_tol
        if "DY" in wrf and "YCELL" in ioapi:
            res["dy_ok"] = abs(float(wrf["DY"]) - float(ioapi["YCELL"])) <= cell_tol
        if "west_east" in wrf and "NCOLS" in ioapi:
            res["nx_ok"] = abs(int(wrf["west_east"]) - int(ioapi["NCOLS"])) <= 5
        if "south_north" in wrf and "NROWS" in ioapi:
            res["ny_ok"] = abs(int(wrf["south_north"]) - int(ioapi["NROWS"])) <= 5
        res["all_ok"] = all(res.values()) if res else False
    except Exception:
        res["all_ok"] = False
    return res

