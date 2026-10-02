#!/usr/bin/env python3.12
"""W43 G3 (i), step 1: the pre-fit render's record (clause 10; Decision Log 5 (b), RULED).

Reads the scratch pre-fit matrix and capture tree that ``render.py`` wrote and records what the
cuts take as their reference, so the reference is committed evidence and not a path on one
machine:

- the scratch matrix's SHA-256, a gzipped copy beside this file (``matrix.json.gz``, the rows'
  raw bytes; the PNGs stay on the machine), and its rows per (profile, tier, set);
- every row's admission as a pre-fit row (``cuts/bed.py``: the cross-position stamp and the two
  shipped 0.5 documents at their live hashes) and no holdout row;
- every capture's PNG SHA-256, with the capture metadata naming the row's exact capturePath;
- **the runtime-base identity**: the web side never reads a fixture, so drawing the 0.5 documents
  on a 0.25 cell must reproduce, byte for byte, the canonical 0.5 web capture of the same scene
  (``/Users/new/Developer/GitHub/designer/packages/calibration/web-captures``, the tree
  ``check-capture-tree`` read exit 0 at G2). Every pre-fit PNG is compared with its counterpart
  there, and where they are identical the pre-fit row's web readings are attributable to the
  shipped material alone (W42 clause 8's proof, re-read at this base);
- **the anti-null, measured**: G2 read the unmoved endpoint's interiorMean through the 0.25
  silhouette offline (``2026-10-02-w43-g2-reading/s1/anti-null-readings.json``, ``webUnder025``).
  The pre-fit row IS that endpoint rendered, so its interiorMeanWeb is compared with G2's reading.

    python3.12 -B record.py            # writes record.json and matrix.json.gz beside this file
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "cuts"))
import bed as B  # noqa: E402

SCRATCH = Path.home() / "vitrea-w43" / "g3-scratch" / "prefit"
CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
ANTI_NULL = B.RESULTS / "2026-10-02-w43-g2-reading" / "s1" / "anti-null-readings.json"


def main() -> int:
    matrix = SCRATCH / "matrix.json"
    raw = matrix.read_bytes()
    bed = B.load([str(matrix)], "prefit")
    counts = Counter((r["key"]["profileKey"], r["key"]["web"]["renderer"], r["fixtureSet"])
                     for r in bed.rows)
    anti = {(a["profileKey"], a["sceneId"], a["tier"]): a
            for a in json.loads(ANTI_NULL.read_text())["readings"]}
    captures, identical, differs, absent_canonical = [], 0, [], []
    anti_checked, anti_worst = 0, 0.0
    for r in bed.rows:
        profile, sid, renderer = r["key"]["profileKey"], r["key"]["sceneId"], r["key"]["web"]["renderer"]
        folder = SCRATCH / "web-captures" / profile / sid
        meta = json.loads((folder / f"cell__{renderer}.json").read_text())
        if meta["capturePath"] != r["key"]["web"]["capturePath"]:
            raise SystemExit(f"{profile}/{sid} {renderer}: capture metadata names another capturePath")
        digest = hashlib.sha256((folder / f"{sid}__{renderer}.png").read_bytes()).hexdigest()
        twin = CANONICAL / B.counterpart_05(profile) / sid / f"{sid}__{renderer}.png"
        twin_digest = hashlib.sha256(twin.read_bytes()).hexdigest() if twin.exists() else None
        if twin_digest is None:
            absent_canonical.append(f"{profile}/{sid} {renderer}")
        elif twin_digest == digest:
            identical += 1
        else:
            differs.append(f"{profile}/{sid} {renderer}")
        captures.append(dict(cell=f"{profile}/{sid}", renderer=renderer, set=r["fixtureSet"],
                             pngSha256=digest, canonical05PngSha256=twin_digest))
        a = anti.get((profile, sid, renderer))
        web = B.value(r, "material", "interiorMeanWeb")
        if a is not None and a.get("status") == "measured" and web is not None:
            anti_checked += 1
            anti_worst = max(anti_worst, abs(a["webUnder025"] - web))
    record = dict(
        what="W43 G3 (i): the pre-fit render, the shipped 0.5 documents on the 0.25 cells "
             "(crossPosition=shipped-glass0.5-against-glass0.25), scratch; L1's growth baseline "
             "and M2's and E2's reference (Decision Log 5 (b), RULED 2026-10-02)",
        matrix=dict(scratchPath=str(matrix), sha256=hashlib.sha256(raw).hexdigest(),
                    bytes=len(raw), committedCopy="matrix.json.gz"),
        documents=B.shipped_05(),
        rows=len(bed.rows),
        rowsBy={f"{p} {t} {s}": n for (p, t, s), n in sorted(counts.items())},
        missingNonHoldout={k: v for k, v in bed.described()["missingNonHoldout"].items()},
        runtimeBase=dict(
            canonicalTree=str(CANONICAL), identicalToCanonical05=identical, differs=differs,
            noCanonicalCapture=absent_canonical,
            rule="the web side reads no fixture, so a 0.5-document render of a scene must equal "
                 "the canonical 0.5 capture of that scene byte for byte"),
        antiNull=dict(source=str(ANTI_NULL.relative_to(B.ROOT)), checked=anti_checked,
                      worstAbsDifference=anti_worst,
                      rule="G2's offline webUnder025 (the 0.5 web capture under the 0.25 native "
                           "silhouette) against the rendered pre-fit row's interiorMeanWeb"),
        captures=captures,
    )
    (HERE / "record.json").write_text(json.dumps(record, indent=1) + "\n")
    (HERE / "matrix.json.gz").write_bytes(gzip.compress(raw, mtime=0))
    print(json.dumps({k: v for k, v in record.items() if k != "captures"}, indent=1)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
