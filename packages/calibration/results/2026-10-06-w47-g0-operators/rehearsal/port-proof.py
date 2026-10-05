#!/usr/bin/env python3.12
"""W47 G0 (c): the cuts port, held to W46's cut of the same generation (W46's `port-proof.py` form, the
brief's "the cuts port proof on d0219cd684bf").

W46 G0 cut the published `d0219cd684bf` (with `ebc3d9105a4a`) against itself with W46's tools
(`results/2026-10-05-w46-g0-declaration/rehearsal/d0219-cuts.json.gz`, committed). W47's cut of the same
generations against themselves (`d0219-cuts.json.gz` here) must equal it on EVERY entry, both schemes,
both tiers: every adopted row's block (tables, M1, M2, C1, L1, X1, E2, S1), T1's cells, aggregates,
rule and stages. Both withhold the same referees (`w46-referees-1`), so no population differs. What
may differ is provenance only, and is listed: the label (`what`), the tools' source hashes
(`cutsSource`), the summary's rule key (`W46 rule …` → `W47 rule …`), and the owner test's file hash
(`ownerTest.sha256`: `adopted-thresholds.test.ts` gained W46 G2's dark T1 block after W46 G0's cut;
the tables the cut reads OUT of it are compared value by value under `tables` and must be equal). W46's own
proof against W45's landing cut (`port-proof.txt` there) is carried by transitivity.

    python3.12 -B port-proof.py
"""
import gzip
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bindings as W  # noqa: E402

W46_CUT = W.W46_G0 / "rehearsal" / "d0219-cuts.json.gz"
W47_CUT = HERE / "d0219-cuts.json.gz"
PROVENANCE = {"what", "cutsSource"}


def walk(a, b, path, out, counted):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(f"{path}.{k}: only in {'W46' if k in a else 'W47'}")
                continue
            walk(a[k], b[k], f"{path}.{k}", out, counted)
        return
    if isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append(f"{path}: {len(a)} entries in W46's, {len(b)} in W47's")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            walk(x, y, f"{path}[{i}]", out, counted)
        return
    counted[0] += 1
    if a != b:
        out.append(f"{path}: W46 {str(a)[:80]!r} W47 {str(b)[:80]!r}")


def main() -> int:
    a = json.loads(gzip.open(W46_CUT).read())
    b = json.loads(gzip.open(W47_CUT).read())
    differ, provenance, counted = [], [], [0]
    for key in sorted(set(a) | set(b)):
        if key in PROVENANCE:
            provenance.append(key)
            continue
        if key == "ownerTest":
            walk({k: v for k, v in a[key].items() if k != "sha256"},
                 {k: v for k, v in b[key].items() if k != "sha256"}, key, differ, counted)
            provenance.append(f"ownerTest.sha256 {a[key]['sha256'][:12]} → {b[key]['sha256'][:12]}")
            continue
        if key == "summary":
            sa = {k.replace("W46 rule", "W47 rule"): v for k, v in a[key].items()}
            walk(sa, b[key], key, differ, counted)
            provenance.append("summary's rule key renamed W46 → W47")
            continue
        walk(a.get(key), b.get(key), key, differ, counted)
    print(f"port proof: {counted[0]} leaf values of W47's d0219cd684bf cut compared with W46's ({W46_CUT.name}, "
          f"committed); {len(differ)} differ; provenance only: {', '.join(provenance)}"
          + ("" if not differ else "\n  " + "\n  ".join(differ[:40])))
    return 1 if differ else 0


if __name__ == "__main__":
    sys.exit(main())
