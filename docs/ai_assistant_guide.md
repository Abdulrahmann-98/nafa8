# How to use this repo (for AI assistants)
- Read paths from `important_paths.yaml`.
- Assume Python 3.8.10 and the package versions pinned in `env.yml` / `requirements.txt`.
- Double-check current runtime via `python src/env_report.py` (JSON written to outputs/).
- Prefer helpers in `src/loaders.py`. Keep code Python 3.8–compatible (use Optional/List, no `|` unions).
- Use the sample files listed in `samples/manifest.tsv` for runnable examples.
- Write outputs to `outputs/` (don’t commit large artifacts).

