PY=python

env:
	$(PY) src/env_report.py

checksums:
	$(PY) src/hash_samples.py

quickcheck:
	$(PY) src/quick_checks.py

validate:
	$(PY) src/validate.py

quicklook:
	$(PY) src/example_plot.py

# placeholder targets Codex will implement
wind:
	$(PY) src/make_quicklook.py --hour 0 --kind wind

emiss:
	$(PY) src/make_quicklook.py --hour 0 --kind emiss

