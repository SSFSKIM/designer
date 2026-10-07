#!/usr/bin/env python3.12
"""W48 G1 step 1: the references (charter G1 child; Design "The populations per phase"; X52).

`d0219cd684bf` (dark) and `ebc3d9105a4a` (light) by hash, cut with W47's `cuts/cuts.py` (inherited by
path under W48's bindings, through G0's launcher) on their published rows and the canonical capture tree
(read only). W43's pre-fit render is not read (W44 G1 replaced it with the published reference; X52). The
cut must equal G0's rehearsal cut (`rehearsal/d0219-cuts.json.gz`) on every value: the same tool, the
same rows and captures, so the reference the fit is read against is the one the rule was rehearsed on.

    python3.12 -B reference.py
"""
from __future__ import annotations

import gzip
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parents[1] / "2026-10-06-w48-g0-declaration"
sys.path.insert(0, str(G0))
import inherit  # noqa: E402

W = inherit.W


def main() -> int:
    gz = HERE / "d0219-cuts.json.gz"
    if gz.exists():
        raise SystemExit("reference: d0219-cuts.json.gz exists; outputs are never overwritten")
    out = HERE / "d0219-cuts.json"
    argv = [sys.executable, "-B", str(W.CUTS / "cuts.py"), "--published", W.REFERENCE["dark"],
            "--published", W.REFERENCE["light"], "--captures", str(W.CANONICAL_CAPTURES),
            "--out", str(out), "--text", str(HERE / "d0219-cuts.txt")]
    got = subprocess.run(argv, cwd=W.CUTS, capture_output=True, text=True)
    if got.returncode:
        raise SystemExit(f"reference: cuts.py exit {got.returncode}: {got.stderr[-1500:]}")
    mine = json.loads(out.read_text())
    with gzip.open(gz, "wt") as f:
        f.write(out.read_text())
    out.unlink()
    with gzip.open(G0 / "rehearsal" / "d0219-cuts.json.gz", "rt") as f:
        theirs = json.load(f)
    strip = lambda d: {k: v for k, v in d.items() if k not in ("generatedAt", "argv", "out")}  # noqa: E731
    same = strip(mine) == strip(theirs)
    diff = sorted(k for k in set(mine) | set(theirs) if mine.get(k) != theirs.get(k))
    record = dict(cut=gz.name, sha256=W.file_sha(gz), equalToG0Rehearsal=same, differingTopKeys=diff)
    (HERE / "reference.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record))
    return 0 if same else 1


if __name__ == "__main__":
    sys.exit(main())
