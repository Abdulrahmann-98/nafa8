# nafa8

## How to work with this repo (for AI assistant)
- Read `important_paths.yaml` for directories and `samples/manifest.tsv` for real sample files.
- Use function contracts in `src/interfaces.py` and implement them in `src/impl.py`.
- Keep code Python 3.8 compatible.
- Use `make quickcheck` to verify environment; `make quicklook` for a first plot.
## Purpose
This repo is a **live contract** describing my HPC datasets (WRF, emissions, FLEXPART, boundaries) and the exact Python environment, so code assistants can write reliable code without reading large data.

## Ritual
- `make env` → print actual Python + package versions
- `make quickcheck` → sanity info (dims, attrs, alignment)
- `make validate` → enforce expected shapes/vars/attrs
- `make quicklook` → produce a small emiss quicklook PNG

## Data
See `docs/datasets.yaml` for schemas and `samples/manifest.tsv` for small real files.

