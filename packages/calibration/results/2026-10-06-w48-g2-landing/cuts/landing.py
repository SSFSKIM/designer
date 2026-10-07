#!/usr/bin/env python3.12
"""W48 G2: the 0.25 cut regenerated at the dark landing, from the PUBLISHED generations (claims §5.214).

Charter clause 10 and the G2 child (W47's G2 verbatim): the owner test's dark 0.25 blocks are re-pinned
against a NEW immutable cut, `cut-025-dark-w48-landing.json`, regenerated at the gate that adopts it (claims
§5.162 §9), never copied from G1's stage reads. W45's landing cut, W46's gate cut and G1's cuts stay where
they are and are not rewritten.

What this script does, in order:
  1. **The bed** is the four `-glass0.25` standard profiles' rows of the current union, read through W40's
     store: `generations/b2d074d2df24.json` (dark, published at W48 G1 step 8) and `ebc3d9105a4a.json`
     (light, unchanged since W45), each checked against `index.json` (file SHA-256, `current`, and the
     union's selection for every profile). Every dark set is read, the holdout and W46's six referees per
     scale included: the exposure was read once at W48 G1 step 7 (the cross-gate ledger's read 8), so these
     are recorded rows and this renders nothing. The light rows are the bed W47's cuts admit for X60, every
     light row less the cells W44 and W43 withheld (`bed.LIGHT_WITHHELD`, which W47's bed refuses for
     good): the same light population G1's gate and exposure cuts read off X60's stage, here read off the
     published file. The owner test's light 0.25 blocks do not read this cut; they keep W45's landing cut.
  2. **The references are selected explicitly, by hash** (X52): M2's, L1's growth baseline, E2's and T1's
     change read `d0219cd684bf` (dark, retired at W48's publication and loadable by its hashes) and
     `ebc3d9105a4a` (light, its own reference), exactly as G1's gate and exposure cuts read them.
  3. **The reference captures.** `d0219cd684bf`'s dark captures moved to
     `web-captures-superseded/d0219cd684bf/` at this landing; the light ones are in the canonical tree. The
     cuts read one `--reference-captures` root and refuse a capture that resolves outside it, so both are
     copied byte for byte into one scratch root, and every copied capture's descriptor is held to its row
     by the cuts' own `capture()` as it is read.
  4. **The cuts are W47's** (`results/2026-10-06-w47-g0-operators/cuts/`), inherited by path under W48's
     bindings (`inherit`, pinned in `bindings.INHERITED`), as G1's gate and exposure cuts were. **One change,
     made here and named:** `cuts.declared` leaves the referee cells out of every population (X49). W46's
     six dark referees per scale were read at read 8 and are spent, so at the landing they are ordinary
     members of the adopted rows they belong to, as W45's landing counted its own. This script rebinds
     `declared` to the same rule without the DARK referee exclusion; the light withheld cells stay out,
     because this bed does not carry them. T1's partition labels still come from the manifests
     (`cuts.REFEREES` is untouched).
  5. **Against G1's exposure cut** (`2026-10-06-w48-g1-refit/cuts/cut-025-w48-dl9-exposure.json.gz`, the
     same rows read off G1's stages against the same references; `landing.json`): every section is EQUAL,
     or (C1, X1, E2) its exposure entries are equal and it adds exactly the dark referee cells. Anything
     else is a stop: the script exits 1 and the landing adopts nothing on it.

    python3.12 -B landing.py [--scratch DIR]
"""
from __future__ import annotations

import argparse
import gzip
import hashlib
import json
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
sys.path.insert(0, str(CAL / "results" / "2026-10-06-w48-g0-declaration"))
import inherit  # noqa: E402

C = inherit.tool("cuts/cuts.py")
B = C.B

GENERATIONS = {"dark": "b2d074d2df24.json", "light": "ebc3d9105a4a.json"}
REFERENCE = ("ebc3d9105a4a", "d0219cd684bf")
T1_REFERENCE = ("ebc3d9105a4a", "d0219cd684bf")
CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
REFERENCE_TREES = {"light": CANONICAL,
                   "dark": CANONICAL.parent / "web-captures-superseded" / "d0219cd684bf"}
EXPOSURE = CAL / "results" / "2026-10-06-w48-g1-refit" / "cuts" / "cut-025-w48-dl9-exposure.json.gz"
# What names the read rather than measures it: the matrices and capture roots it was loaded from and the
# owner test's bytes (its tables are compared through `tables`, which the cuts parse out of it).
PROVENANCE = ("what", "bed", "reference", "ownerTest", "cutsSource", "referenceCaptures")
WITH_REFEREES = ("X1", "E2")
OUT, TEXT = HERE / "cut-025-dark-w48-landing.json", HERE / "cut-025-dark-w48-landing.txt"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def published_rows() -> tuple[list, dict]:
    index = json.loads((CAL / "results" / "generations" / "index.json").read_text())
    record, rows = {}, []
    for scheme, name in GENERATIONS.items():
        entry = index["files"][name]
        raw = (CAL / "results" / "generations" / name).read_bytes()
        if sha256(raw) != entry["sha256"] or entry["status"] != "current":
            raise SystemExit(f"{name}: not the current published file the index records")
        record[name] = dict(sha256=entry["sha256"], rows=entry["rowCount"])
    for profile in B.PROFILES:
        if index["currentByProfile"].get(profile) != GENERATIONS[B.scheme_of(profile)]:
            raise SystemExit(f"{profile}: the union selects {index['currentByProfile'].get(profile)}")
        rows += [r for r in B.matrix_store.load_current_profile(profile)
                 if (profile, r["key"]["sceneId"]) not in B.LIGHT_WITHHELD]
    return rows, record


def declared_at_landing(rule) -> list[tuple[str, str]]:
    """`cuts.declared` less its DARK referee exclusion (item 4 of the docstring)."""
    return [(p, sid) for p in B.PROFILES for sid in B.SCENES.declared(p)
            if B.SCENES.role[sid] in B.NON_HOLDOUT and rule(sid)
            and not ((p, sid) in C.REFEREES and B.scheme_of(p) == "light")]


def reference_tree(scratch: Path) -> Path:
    root = scratch / "reference-captures"
    if root.exists():
        raise SystemExit(f"{root} exists; give a fresh --scratch")
    root.mkdir(parents=True)
    for profile in B.PROFILES:
        shutil.copytree(REFERENCE_TREES[B.scheme_of(profile)] / profile, root / profile)
    return root


def compare(landing: dict, exposure: dict) -> dict:
    referees = {f"{p}/{s}" for p, s in C.REFEREES if B.scheme_of(p) == "dark"}
    sections = sorted((set(landing) | set(exposure)) - set(PROVENANCE))
    equal, added, moved, differ = [], {}, {}, []
    for s in sections:
        if landing.get(s) == exposure.get(s):
            equal.append(s)
            continue
        if s == "T1" and {**landing[s], "referenceCaptures": None} == {**exposure[s], "referenceCaptures": None}:
            # T1 names the reference capture root it read d0219cd684bf off; the bytes it read are the same
            # (`readings[].referenceWebSha256` is compared with everything else).
            equal.append(s)
            continue
        if s == "C1":
            ok, extra = True, []
            for tier in B.TIERS:
                here, there = landing[s][tier], exposure[s][tier]
                more = sorted(set(here["cells"]) - set(there["cells"]))
                ok &= set(there["cells"]) <= set(here["cells"]) and set(more) <= referees
                ok &= all(here["cells"][c] == there["cells"][c] for c in there["cells"])
                ok &= here["verdict"] == there["verdict"] and here["noRow"] == there["noRow"]
                ok &= set(here["perBedSpan"]) == set(there["perBedSpan"])
                grown = 0
                for bs, entry in here["perBedSpan"].items():
                    if entry != there["perBedSpan"][bs]:
                        grown += entry["cells"] - there["perBedSpan"][bs]["cells"]
                        moved[f"{s} {tier} {bs}"] = dict(landing=entry, exposure=there["perBedSpan"][bs])
                ok &= grown == len(more)
                extra += [f"{tier} {c}" for c in more]
            if ok:
                added[s] = extra
                continue
        if s in WITH_REFEREES:
            ok, extra = True, []
            for tier in B.TIERS:
                here, there = landing[s][tier], exposure[s][tier]
                cells_here = {c["cell"]: c for c in here["perCell"]}
                cells_there = {c["cell"]: c for c in there["perCell"]}
                more = sorted(set(cells_here) - set(cells_there))
                ok &= set(cells_there) <= set(cells_here) and set(more) <= referees
                ok &= all(cells_here[c] == cells_there[c] for c in cells_there)
                failing_here = {c["cell"] for c in here["failing"]}
                failing_there = {c["cell"] for c in there["failing"]}
                ok &= failing_there <= failing_here and failing_here - failing_there <= set(more)
                ok &= here["cells"] == there["cells"] + len(more)
                ok &= here["verdict"] == there["verdict"] and here["noRow"] == there["noRow"]
                ok &= here.get("unmeasured") == there.get("unmeasured")
                extra += [f"{tier} {c}" for c in more]
                # The fields that aggregate over the cells move with the added cells and are
                # recorded both ways rather than compared.
                for k in sorted(set(here) - {"perCell", "failing", "cells", "verdict", "noRow", "unmeasured"}):
                    if here[k] != there.get(k):
                        brief = (lambda v: len(v) if isinstance(v, (list, dict)) and k.startswith("namedMiss") else v)
                        moved[f"{s} {tier} {k}"] = dict(landing=brief(here[k]), exposure=brief(there.get(k)))
            if ok:
                added[s] = extra
                continue
        differ.append(s)
    return dict(sectionsCompared=sections, equal=equal, addedRefereeCells=added,
                aggregatesMovedWithTheAddedCells=moved, differ=differ)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--scratch", type=Path, default=Path.home() / "vitrea-w48" / "g2-scratch" / "landing-cut")
    args = ap.parse_args()
    for stale in (OUT, TEXT):
        if stale.exists():
            raise SystemExit(f"{stale} exists: the landing cut is immutable once written")
    rows, record = published_rows()
    args.scratch.mkdir(parents=True, exist_ok=True)
    bed_path = args.scratch / "published-025.json"
    if bed_path.exists():
        raise SystemExit(f"{bed_path} exists; give a fresh --scratch")
    bed_path.write_text(json.dumps(dict(schemaVersion=5, cells=rows)))
    references = reference_tree(args.scratch)
    C.declared = declared_at_landing
    C.main(["--bed", str(bed_path), "--kind", "sealed", "--with-holdout",
            "--captures", str(CANONICAL),
            *[a for g in REFERENCE for a in ("--reference", g)],
            *[a for g in T1_REFERENCE for a in ("--t1-reference", g)],
            "--reference-captures", str(references),
            "--band-partitions", "gate,referee,holdout",
            "--out", str(OUT), "--text", str(TEXT)])
    landing = json.loads(OUT.read_text())
    with gzip.open(EXPOSURE, "rt") as f:
        exposure = json.load(f)
    against = compare(landing, exposure)
    bed_same = all(landing["bed"][k] == exposure["bed"][k]
                   for k in ("kind", "rows", "pairs", "missingNonHoldout", "refereeRowsDropped"))
    ref_same = all(landing["reference"][k] == exposure["reference"][k]
                   for k in ("label", "kind", "matrices", "rows", "pairs"))
    result = dict(
        what="W48 G2: the 0.25 cut regenerated at the dark landing from the published generations (claims §5.214)",
        published=record, rows=len(rows),
        bedMatrix=dict(path=str(bed_path), sha256=sha256(bed_path.read_bytes())),
        references=dict(generations=list(REFERENCE), t1=list(T1_REFERENCE), captures=str(references),
                        copiedFrom={k: str(v) for k, v in REFERENCE_TREES.items()}),
        captures=str(CANONICAL),
        declaredAtLanding="cuts.declared without the DARK referee exclusion (W46's referees, spent at read 8)",
        cut=dict(path=OUT.name, sha256=sha256(OUT.read_bytes())),
        againstExposure=dict(path=str(EXPOSURE.relative_to(CAL)), sha256=sha256(EXPOSURE.read_bytes()),
                             bedEqual=bed_same, referenceEqual=ref_same, **against),
        verdict="EQUAL" if not against["differ"] and bed_same and ref_same else "DIFFERS: STOP",
    )
    (HERE / "landing.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "againstExposure"}, indent=1))
    print(json.dumps({k: v for k, v in result["againstExposure"].items() if k != "sectionsCompared"}, indent=1))
    return 0 if result["verdict"] == "EQUAL" else 1


if __name__ == "__main__":
    raise SystemExit(main())
