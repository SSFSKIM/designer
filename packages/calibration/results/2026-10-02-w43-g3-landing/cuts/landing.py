#!/usr/bin/env python3.12
"""W43 G3 (iii): the 0.25 cuts regenerated at the landing gate, from the PUBLISHED generation.

Charter clause 13 and Decision Log 5 (a)-(e) as RULED 2026-10-02. G3 (ii) read the cuts on its two
publication stages (``2026-10-02-w43-g3-refit/stage/stage-cuts.json``) and the holdout once
(``stage/holdout-reading.json``). This gate adopts the rows in ``adopted-thresholds.test.ts``, and a
cut is regenerated at the gate that adopts it (claims §5.162 §9): never copied from the stage read.

So this script reads the four ``-glass0.25`` standard profiles' rows out of the current union
through the store (``generations/6d18c059eb42.json`` light, ``d0219cd684bf.json`` dark), writes
them to scratch matrices, and runs G3's own ``cuts.py`` over them unchanged, with the pre-fit
render as the reference (L1's growth baseline, M2's and E2's reference; Decision Log 5 (b)). The
pre-fit matrix is the committed ``2026-10-02-w43-g3-refit/prefit/matrix.json.gz``, checked against
the hash every G3 cut recorded; its captures (E2's reference) stay on the capture machine. X1 and E2
read the canonical capture tree, which ``check-capture-tree`` holds to the published rows.

It then compares the regenerated reading with the stage's, section by section, and the holdout
tables on the published rows with the stage's one holdout reading. Any difference is a stop: the
script exits 1 and the landing adopts nothing on it.

    python3.12 -B landing.py [--captures DIR] [--prefit-captures DIR]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
REFIT = CAL / "results" / "2026-10-02-w43-g3-refit"
sys.path.insert(0, str(REFIT / "cuts"))
sys.path.insert(0, str(REFIT / "stage"))
import bed as B  # noqa: E402
import cuts as C  # noqa: E402

GENERATIONS = {"light": "6d18c059eb42.json", "dark": "d0219cd684bf.json"}
PREFIT_GZ = REFIT / "prefit" / "matrix.json.gz"
PREFIT_SHA256 = "504c5348638265e6a141308d4f74d98dc6119dfbb9e12e15164fc6e028bdebbb"
CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
PREFIT_CAPTURES = Path.home() / "vitrea-w43" / "g3-scratch" / "prefit" / "web-captures"
# What names the bed rather than reads it: the matrices it was loaded from, and the owner test's
# bytes (its tables are compared through `tables`, which is what the cuts parse out of it).
PROVENANCE = ("what", "bed", "reference", "ownerTest", "cutsSource")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def published_rows() -> tuple[list, list, dict]:
    index = json.loads((CAL / "results" / "generations" / "index.json").read_text())
    record = {}
    rows = []
    for scheme, name in GENERATIONS.items():
        entry = index["files"][name]
        raw = (CAL / "results" / "generations" / name).read_bytes()
        if sha256(raw) != entry["sha256"] or entry["status"] != "current":
            raise SystemExit(f"{name}: not the current published file the index records")
        record[name] = dict(sha256=entry["sha256"], rows=entry["rowCount"])
    for profile in B.PROFILES:
        current = B.matrix_store.load_current_profile(profile)
        names = {n for n, e in index["files"].items() if profile in e["rowsByProfileKey"]
                 and e["status"] == "current"}
        if names != {GENERATIONS[B.scheme_of(profile)]}:
            raise SystemExit(f"{profile}: the union selects {names}, not the published file")
        rows += current
    holdout = [r for r in rows if r["fixtureSet"] == "holdout"]
    measured = [r for r in rows if r["fixtureSet"] != "holdout"]
    return measured, holdout, record


def write(path: Path, rows: list) -> None:
    path.write_text(json.dumps(dict(schemaVersion=5, cells=rows)))


def strip(value):
    """A cut section with the scratch paths it names taken out (captures are named by tree)."""
    return json.loads(json.dumps(value))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--captures", type=Path, default=CANONICAL)
    ap.add_argument("--prefit-captures", type=Path, default=PREFIT_CAPTURES)
    args = ap.parse_args()
    measured, holdout, record = published_rows()
    raw = gzip.decompress(PREFIT_GZ.read_bytes())
    if sha256(raw) != PREFIT_SHA256:
        raise SystemExit("the committed pre-fit matrix is not the one every G3 cut recorded")
    with tempfile.TemporaryDirectory(prefix="w43-landing-") as scratch:
        scratch = Path(scratch)
        bed_path, prefit_path, all_path = scratch / "published.json", scratch / "prefit.json", scratch / "all.json"
        write(bed_path, measured)
        write(all_path, measured + holdout)
        prefit_path.write_bytes(raw)
        out, text = HERE / "cut-025.json", HERE / "cut-025.txt"
        for stale in (out, text):
            stale.unlink(missing_ok=True)
        C.main(["--bed", str(bed_path), "--kind", "sealed", "--captures", str(args.captures),
                "--prefit", str(prefit_path), "--prefit-captures", str(args.prefit_captures),
                "--out", str(out), "--text", str(text)])
        landing = json.loads(out.read_text())
        stage = json.loads((REFIT / "stage" / "stage-cuts.json").read_text())
        sections = sorted(set(landing) | set(stage))
        differ = [s for s in sections if s not in PROVENANCE and landing.get(s) != stage.get(s)]
        # The bed: the same rows by count and pair, now from the published files.
        bed_same = all(landing["bed"][k] == stage["bed"][k] for k in ("kind", "rows", "pairs", "missingNonHoldout"))
        ref_same = all(landing["reference"][k] == stage["reference"][k]
                       for k in ("kind", "rows", "pairs", "documents", "stamp"))
        ref_sha = landing["reference"]["matrices"][0]["sha256"] == stage["reference"]["matrices"][0]["sha256"]

        # The holdout: the stage's reader over the published rows.
        import holdout as H  # noqa: E402
        published_holdout = B.load([str(all_path)], "sealed", with_holdout=True)
        H.STAGES = [all_path]
        H.HERE = scratch
        H.main()
        reading = json.loads((scratch / "holdout-reading.json").read_text())
        recorded = json.loads((REFIT / "stage" / "holdout-reading.json").read_text())
        holdout_same = reading["readings"] == recorded["readings"]

    result = dict(
        what="W43 G3 (iii): the 0.25 cuts regenerated at the landing from the published generation",
        published=record, holdoutRows=len(holdout), measuredRows=len(measured),
        prefit=dict(path=str(PREFIT_GZ.relative_to(CAL.parent.parent)), sha256=PREFIT_SHA256),
        captures=str(args.captures), prefitCaptures=str(args.prefit_captures),
        cut=dict(path="cut-025.json", sha256=sha256(out.read_bytes())),
        againstStage=dict(sectionsCompared=[s for s in sections if s not in PROVENANCE],
                          sectionsThatDiffer=differ, bedRowsAndPairsEqual=bed_same,
                          referenceEqual=ref_same and ref_sha),
        againstHoldoutReading=dict(readingsEqual=holdout_same,
                                   holdoutRowsRead=len(published_holdout.rows) - len(measured)),
        verdict="EQUAL" if not differ and bed_same and ref_same and ref_sha and holdout_same else "DIFFERS: STOP",
    )
    (HERE / "landing.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "againstStage"}, indent=1))
    print("differ:", differ)
    return 0 if result["verdict"] == "EQUAL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
