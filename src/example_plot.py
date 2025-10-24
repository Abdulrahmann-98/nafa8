#!/usr/bin/env python3
"""
Example: plot CO emissions (hour 0) on WRF lat/lon grid and overlay Fairbanks boundary.

Requires: xarray, netCDF4, pandas, PyYAML, matplotlib (no cartopy).
Output: outputs/co_emiss_h00.png
"""

from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.path import Path as MplPath

from loaders import (
    load_paths, open_wrf, open_emissions, read_boundaries
)

def mask_with_polygon(lon2d, lat2d, poly_lon, poly_lat):
    """Return boolean mask where True=inside polygon."""
    poly_xy = np.column_stack([poly_lon, poly_lat])
    poly = MplPath(poly_xy)
    pts = np.column_stack([lon2d.ravel(), lat2d.ravel()])
    inside = poly.contains_points(pts)
    return inside.reshape(lon2d.shape)

def main():
    paths = load_paths()
    outdir = Path("outputs")
    outdir.mkdir(exist_ok=True, parents=True)

    # open one wrf + emissions
    ds_w = open_wrf()                     # has XLAT/XLONG
    ds_e = open_emissions()               # has emiss(time,LAY,y,x)

    # get lat/lon from WRF (time 0 slice)
    XLAT  = ds_w["XLAT"].isel(Time=0).values
    XLONG = ds_w["XLONG"].isel(Time=0).values   # shape ~ (south_north, west_east)

    # emissions field at hour 0, summed over LAY (if exists)
    var = ds_e["emiss"]
    if "LAY" in var.dims:
        emiss2d = var.isel(time=0).sum("LAY").values
    else:
        emiss2d = var.isel(time=0).values
    # emissions is (y, x); WRF lat/lon is (south_north, west_east).
    # If sizes differ by ~2 cells (201 vs 199), center-crop WRF to match emissions,
    # or pad emissions to match WRF. We’ll crop WRF to inner 199x199 for plotting.
    ny_w, nx_w = XLAT.shape
    ny_e, nx_e = emiss2d.shape
    if (ny_w != ny_e) or (nx_w != nx_e):
        # crop from each side evenly
        dy = (ny_w - ny_e) // 2
        dx = (nx_w - nx_e) // 2
        XLATc  = XLAT[dy:dy+ny_e, dx:dx+nx_e]
        XLONGc = XLONG[dy:dy+ny_e, dx:dx+nx_e]
    else:
        XLATc, XLONGc = XLAT, XLONG

    # boundaries
    polys = read_boundaries()
    fb = polys.get("Fairbanks", None)

    # plot
    fig = plt.figure(figsize=(8, 7))
    ax = plt.gca()

    # pcolormesh in geodetic coordinates (no projection)—good enough for quicklook
    # set very small value floor to reduce dynamic range issues
    data = np.where(np.isfinite(emiss2d), emiss2d, np.nan)
    mesh = ax.pcolormesh(XLONGc, XLATc, data, shading="auto")
    cbar = plt.colorbar(mesh, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label("CO emissions (moles s$^{-1}$) — hour 0")

    # overlay Fairbanks polygon if present
    if fb is not None and len(fb) > 3:
        ax.plot(fb["lon"].values, fb["lat"].values, lw=1.0)

        # optional: mask outside polygon (comment out if you prefer full map)
        # mask = mask_with_polygon(XLONGc, XLATc, fb["lon"].values, fb["lat"].values)
        # masked = np.where(mask, data, np.nan)
        # mesh.set_array(masked.ravel())  # simple update (works with shading='auto')

    ax.set_xlabel("Longitude (°E)")
    ax.set_ylabel("Latitude (°N)")
    ax.set_title("Fairbanks CO emissions – first hour")

    # tighten extents to finite data
    xfin = XLONGc[np.isfinite(data)]
    yfin = XLATc[np.isfinite(data)]
    if xfin.size and yfin.size:
        ax.set_xlim(xfin.min(), xfin.max())
        ax.set_ylim(yfin.min(), yfin.max())

    out_png = outdir / "co_emiss_h00.png"
    fig.tight_layout()
    fig.savefig(out_png, dpi=150)
    print(f"Saved: {out_png}")

if __name__ == "__main__":
    main()

