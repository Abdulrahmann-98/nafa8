#!/usr/bin/env python3
"""
Function contracts Codex should implement. Keep IO simple & deterministic.
"""

from pathlib import Path
import xarray as xr
import pandas as pd
from typing import Tuple, Dict, Any

def open_wrf_file(path: Path) -> xr.Dataset:
    """Open a single WRF wrfout file and return an xarray.Dataset."""
    raise NotImplementedError

def wrf_latlon(ds: xr.Dataset) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Return lat/lon as 2D arrays and basic attrs.
    Returns:
      (df, meta) where df has columns ['lat','lon','i','j'] for a thin sample,
      meta includes dims and projection fields.
    """
    raise NotImplementedError

def compute_wind10(ds: xr.Dataset) -> xr.DataArray:
    """Compute 10m wind speed (m/s) from U10 and V10, same 2D grid."""
    raise NotImplementedError

def open_emiss_file(path: Path) -> xr.Dataset:
    """Open an emissions NetCDF and return xarray.Dataset."""
    raise NotImplementedError

def emiss_2d_at_hour(ds: xr.Dataset, hour: int = 0) -> xr.DataArray:
    """Return 2D emissions slice (sum over LAY if present) for given hour."""
    raise NotImplementedError

def read_boundary_txt(path: Path) -> pd.DataFrame:
    """Read boundary text (lon,lat,0) into DataFrame with ['lon','lat']."""
    raise NotImplementedError

