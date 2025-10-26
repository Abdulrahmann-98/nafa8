# How to work with this repo (for AI assistants)
- Read `important_paths.yaml` and `docs/datasets.yaml` to understand paths, shapes, projections.
- Confine examples to files listed in `samples/manifest.tsv`.
- Respect Python 3.8 and library versions in `env.yml` (or report via `src/env_report.py`).
- Prefer utility functions in `src/loaders.py`.
- Before proposing analysis, run `python src/validate.py` and confirm "OK".
- Output files into `outputs/` and avoid committing large artifacts.

