#!/usr/bin/env python3
import sys, platform, importlib, json, pathlib
pkgs = ["xarray","netCDF4","cftime","pandas","yaml","matplotlib"]
versions = {}
for p in pkgs:
    try:
        m = importlib.import_module(p if p!="yaml" else "yaml")
        v = getattr(m, "__version__", "unknown")
    except Exception:
        v = "not-installed"
    versions[p] = v
out = {
  "python": platform.python_version(),
  "executable": sys.executable,
  "platform": platform.platform(),
  "versions": versions
}
pathlib.Path("outputs").mkdir(exist_ok=True)
pathlib.Path("outputs/env_report.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))

