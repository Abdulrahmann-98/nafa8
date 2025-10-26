#!/usr/bin/env python3
import hashlib, pathlib, csv, sys
rows = []
with open("samples/manifest.tsv") as f:
    for line in f:
        if not line.strip() or line.startswith("#"): continue
        ds, p, why = line.strip().split("\t", 2)
        path = pathlib.Path(p)
        if not path.exists():
            rows.append((ds, p, why, "MISSING"))
            continue
        h = hashlib.md5()
        with path.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1<<20), b""):
                h.update(chunk)
        rows.append((ds, p, why, h.hexdigest()))
pathlib.Path("outputs").mkdir(exist_ok=True)
with open("outputs/sample_checksums.tsv", "w", newline="") as out:
    w = csv.writer(out, delimiter="\t")
    w.writerow(["dataset","filepath","why","md5"])
    w.writerows(rows)
print("Wrote outputs/sample_checksums.tsv")

