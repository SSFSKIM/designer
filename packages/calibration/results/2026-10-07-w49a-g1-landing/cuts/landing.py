#!/usr/bin/env python3.12
"""W49a: regenerate the dark owner cut from the completed strict-mode stage; no render or publication.

The stage must contain exactly the previous dark generation's 468 cell identities and name the
sealed pair b2d074d2df24 / 940384c06f73. The unchanged light rows come from W45's immutable file,
with its still-withheld members excluded as in W48. M2/L1/E2 and this cut's whole-bed T1 comparison
retain d0219; the companion T1 derivation witnesses BOTH references and DL2's explicit partition.

Dark referee rows are ordinary adopted-row members after read 9. The pinned W47 readers are
inherited under W48's bindings without editing their source; only `declared` includes spent dark
referees, exactly as at W48's landing. The candidate and reference capture trees are COPIES under
a fresh scratch root; the main checkout's canonical and superseded trees are read-only inputs.

Run only after the landing worker confirms the stage is complete:
  python3.12 -B landing.py --stage STAGE --canonical TREE --d0219 TREE --scratch NEW_DIR
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "t1"))
import w49_inputs as I

C = I.cuts()
B = C.B
OUT = HERE / "cut-025-dark-w49a-landing.json"


def declared_at_landing(rule):
    return [(p, sid) for p in B.PROFILES for sid in B.SCENES.declared(p)
            if B.SCENES.role[sid] in B.NON_HOLDOUT and rule(sid)
            and not ((p, sid) in C.REFEREES and B.scheme_of(p) == "light")]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    for flag in ("stage", "canonical", "d0219", "scratch"):
        ap.add_argument(f"--{flag}", type=Path, required=True)
    args = ap.parse_args()
    if OUT.exists() or args.scratch.exists():
        raise SystemExit("landing cut or scratch exists; never overwrite a recorded read")
    rows = I.stage_rows(args.stage)
    light = I.published("ebc3d9105a4a", ("ebc3d9105a4a", "12712d534b78"))
    rows += [r for r in light if (r["key"]["profileKey"], r["key"]["sceneId"]) not in B.LIGHT_WITHHELD]
    args.scratch.mkdir(parents=True)
    bed = args.scratch / "bed.json"
    bed.write_text(json.dumps(dict(schemaVersion=5, cells=rows)))
    captures, references = args.scratch / "captures", args.scratch / "reference-captures"
    for profile in B.PROFILES:
        dark = B.scheme_of(profile) == "dark"
        shutil.copytree((args.stage / "web-captures" if dark else args.canonical) / profile,
                        captures / profile)
        shutil.copytree((args.d0219 if dark else args.canonical) / profile, references / profile)
    C.declared = declared_at_landing
    C.main(["--bed", str(bed), "--kind", "sealed", "--with-holdout", "--captures", str(captures),
            "--reference", "ebc3d9105a4a", "--reference", "d0219cd684bf",
            "--t1-reference", "ebc3d9105a4a", "--t1-reference", "d0219cd684bf",
            "--reference-captures", str(references), "--band-partitions", "gate,referee,holdout",
            "--out", str(OUT), "--text", str(OUT.with_suffix(".txt"))])
    record = dict(generation=I.GENERATION, pair=I.PAIR, rows=len(rows), stage=str(args.stage),
                  stageSha256=hashlib.sha256((args.stage / "matrix.json").read_bytes()).hexdigest(),
                  cutSha256=hashlib.sha256(OUT.read_bytes()).hexdigest(),
                  captures=str(captures), referenceCaptures=str(references),
                  reference="d0219cd684bf / f0b36a71772a", t1Witness="../t1/derive.py")
    with (HERE / "landing.json").open("x") as f:
        json.dump(record, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
