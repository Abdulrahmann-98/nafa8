# Goal
Write Python that uses `important_paths.yaml`, `samples/manifest.tsv`, and functions from `src/interfaces.py`
to:
1) open the WRF file, compute 10m wind speed,
2) open the emissions file, get hour-0 emiss 2D,
3) overlay Fairbanks boundary & save a PNG to outputs/.

# Constraints
- Never hardcode paths; read from important_paths.yaml or samples/manifest.tsv.
- Use xarray/netCDF4, pandas, matplotlib (no cartopy).
- Must run under Python 3.8.

# Steps skeleton
- Parse YAML & TSV
- Implement `interfaces.py` functions in a new module `src/impl.py`
- Add a script `src/make_quicklook.py` with CLI: `--hour 0`
- Save outputs/co_emiss_h00.png

