#!/usr/bin/env python3.12
"""W48 G1 step 5: W47's cuts (`cuts/cuts.py`, inherited by path under W48's bindings, through G0's launcher)
on the sealed strict-mode stages: the dark stage (~/vitrea-w48/g1-stage-dark, both tiers, the non-withheld
cells) and X60's light stage (~/vitrea-w48/g1-stage-x60-light), as ONE sealed bed, against d0219cd684bf
(every regression row's reference and T1's) and ebc3d9105a4a (the light rows). The two capture trees (the
worktree's `web-captures`, where the dark stage lands, and the light stage's own) are hard-linked into one
scratch tree for the cut. `--with-holdout` is the exposure's cut (read 8), only after it.

    python3.12 -B cut.py NAME [--with-holdout]       writes NAME.json.gz and NAME.txt beside this file
"""
from __future__ import annotations

import gzip
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parents[1] / "2026-10-06-w48-g0-declaration"
sys.path.insert(0, str(G0))
import inherit  # noqa: E402

W = inherit.W
# The round (as `stage/run.py`): the first freeze's dark captures were taken into the worktree's tree and then
# moved, unchanged, beside their stage; the re-freeze's (W48 Decision Log 9) are in their own stage's tree.
ROUND = os.environ.get("W48_G1_ROUND", "first")
if ROUND == "dl9":
    W.STAGE = W.SCRATCH / "g1-stage-dark-dl9"
SUFFIX = "" if ROUND == "first" else "-dl9"
LIGHT_STAGE = W.SCRATCH / f"g1-stage-x60-light{SUFFIX}"
TREES = (W.STAGE / "web-captures", LIGHT_STAGE / "web-captures")
MERGED = W.SCRATCH / "g1-scratch" / "gate" / f"merged-captures{SUFFIX}"


def merge() -> Path:
    for tree in TREES:
        for prof in sorted(tree.iterdir()):
            if not prof.is_dir():
                continue
            for cell in prof.iterdir():
                (MERGED / prof.name / cell.name).mkdir(parents=True, exist_ok=True)
                for f in cell.iterdir():
                    link = MERGED / prof.name / cell.name / f.name
                    if link.exists() and os.stat(link).st_ino != os.stat(f).st_ino:
                        link.unlink()
                    if not link.exists():
                        os.link(f, link)
    return MERGED


def main(argv) -> int:
    name = argv[1]
    out = HERE / f"{name}.json"
    if (HERE / f"{name}.json.gz").exists():
        raise SystemExit(f"{name}.json.gz exists; outputs are never overwritten")
    args = [sys.executable, "-B", str(W.CUTS / "cuts.py"), "--bed", str(W.STAGE / "matrix.json"),
            "--bed", str(LIGHT_STAGE / "matrix.json"), "--kind", "sealed", "--captures", str(merge()),
            "--out", str(out), "--text", str(HERE / f"{name}.txt")]
    if "--with-holdout" in argv:
        # The exposure reads a T cell of every partition on its bands (W44 G1: "the exposure adds the referees
        # and the holdout"); without them the T cells withheld until now have no reading and the rule is
        # UNMEASURED.
        args += ["--with-holdout", "--band-partitions", "gate,referee,holdout"]
    got = subprocess.run(args, cwd=W.CUTS, capture_output=True, text=True)
    if got.returncode:
        raise SystemExit(f"cuts.py exit {got.returncode}: {got.stderr[-2500:]}")
    with gzip.open(HERE / f"{name}.json.gz", "wt") as f:
        f.write(out.read_text())
    out.unlink()
    print(got.stdout[-1500:])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
