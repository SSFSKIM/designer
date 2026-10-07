#!/usr/bin/env python3.12
"""W49a G0 (d): the two hashed parts of W49a's declaration (charter `2026-10-07-w49-authorised-list-repair.md`,
Decision Logs 1-8). W48's `declare.py` (`results/2026-10-06-w48-g0-declaration/declare.py`) gave the form: a
part 1 that states what will be rendered and what is predicted, a part 2 that states the rule that reads it,
each hashed by SHA-256 over its exact bytes before the thing it governs exists. W49a declares one family of one
leaf pair and no ladder, so it carries neither W47's ladder reader, W48's verdicts nor their amendment
exceptions; it is written anew at the size of the question.

    python3.12 -B declare.py check                 assemble both parts from the tree and compare with what is hashed
    python3.12 -B declare.py hash --charter-commit C   write and hash both parts (refused once any probe render exists)
    python3.12 -B declare.py amend --part 1|2 --reason TEXT [--charter-commit C]
                                                   once per part, and only before the first probe render

**Part 1** (`declaration.json`): the charter (path and commit) and the rulings that bound the probes, verbatim
from that commit (DL1, DL3, DL6, DL8); family R (members, signed domain, the active unmoved, scale
separability); the probes P1 and P2 (specs, built candidates by hash, cells per scale, render protocol); the
first-order predictions (`probes/predict.json`) including every withheld cell's number (DL6); X74, X75, X76; the
tooling smoke; and every tool and evidence file the renders and readings depend on, by SHA-256.

**Part 2** (`fit-declaration.json`): part 1's hash; DL2, DL4, DL5 and DL7 verbatim; the landing rule and the
selection as `probes/rule.py` computes them (the file pinned, its arithmetic W44 G1's `t1.py`, pinned); the reads
(the gate, read 9, the owner test); and `amendmentAfterGate: "none"`.

**The order.** `hash` refuses once a probe render exists (`probes/runs.jsonl` or any matrix under the scratch
render root). `probes/probe.py render` refuses until `check` passes on both parts. Each part admits ONE
amendment, recorded in `amendments.json` with the hash it supersedes, and only before the first probe render;
after it, none (DL4: part 2 admits no post-gate amendment, and part 1 is what the renders were made under).
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
ROOT = CAL.parents[1]
RESULTS = CAL / "results"
CHARTER = "docs/doperpowers/specs/2026-10-07-w49-authorised-list-repair.md"
PROBES = HERE / "probes"
RUNS = PROBES / "runs.jsonl"
RENDERS = Path.home() / "vitrea-w49" / "w49a-g0-probes" / "renders"
PART1, PART2 = HERE / "declaration.json", HERE / "fit-declaration.json"
SHA1, SHA2 = HERE / "declaration.sha256", HERE / "fit-declaration.sha256"
AMENDMENTS = HERE / "amendments.json"

# Every file the probes' renders and readings depend on (part 1), and the rule's (part 2), by repository path.
PART1_PINS = [
    "packages/calibration/scripts/no-opaque-glass.ts",
    "packages/calibration/test/x75-no-opaque-glass.test.ts",
    "packages/calibration/scripts/candidate-document.ts",
    "packages/calibration/cli/compare.ts",
    *[f"packages/calibration/results/2026-10-07-w49a-g0-declaration/{p}" for p in (
        "documents/b2d074d2df24.json", "documents/29da6a888a23.json", "documents/d0219cd684bf.json",
        "documents/f0b36a71772a.json", "documents/ebc3d9105a4a.json", "documents/12712d534b78.json",
        "fit/build-candidate.ts", "fit/labels.json", "fit/test_build_candidate.py",
        "seal/seal.ts", "seal/test_seal.py",
        "probes/probe.py", "probes/predict.py", "probes/predict.json", "probes/smoke/smoke.json",
        "x76/audit.py", "x76/audit.json", "x75/x75-on-0.28.0-unmarked.txt", "declare.py", "test_declare.py")],
    "packages/calibration/results/2026-10-06-w48-g0-declaration/cuts/cuts.py",
    "packages/calibration/results/2026-10-06-w47-g0-operators/cuts/cuts.py",
    "packages/calibration/results/2026-10-02-w43-g3-refit/stage/census.py",
    "packages/calibration/results/2026-10-06-w48-g1-refit/cuts/cut-025-w48-dl9-exposure.json.gz",
    "packages/calibration/results/2026-10-05-w46-g1-refit/gate/"
    "d-s2-rta0.8-rs214-rfa0.5-rh10.25-re20.04-rk10.15-rk20.04-rn10.4-rn20.4-rg0/cut.json.gz",
]
PART2_PINS = [
    "packages/calibration/results/2026-10-07-w49a-g0-declaration/probes/rule.py",
    "packages/calibration/results/2026-10-07-w49a-g0-declaration/probes/test_rule.py",
    "packages/calibration/results/2026-10-03-w44-g1-refit/cuts/t1.py",
    "packages/calibration/results/2026-10-06-w48-g1-refit/cuts/cut-025-w48-dl9-exposure.json.gz",
]


class Refusal(SystemExit):
    pass


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pins(paths: list[str]) -> dict[str, str]:
    out = {}
    for rel in paths:
        path = ROOT / rel
        if not path.is_file():
            raise Refusal(f"pin {rel}: no such file")
        out[rel] = sha(path)
    return out


def charter_at(commit: str) -> str:
    got = subprocess.run(["git", "show", f"{commit}:{CHARTER}"], cwd=ROOT, capture_output=True, text=True)
    if got.returncode:
        raise Refusal(f"the charter at {commit}: {got.stderr.strip()}")
    return got.stdout


def ruling(text: str, n: int) -> str:
    """The body of `### DL<n>` in the charter's Decision Log, verbatim, up to the next heading."""
    m = re.search(rf"^### DL{n}\n\n(.*?)(?=^### |^## )", text, flags=re.S | re.M)
    if m is None:
        raise Refusal(f"the charter has no `### DL{n}` section")
    return m.group(1).rstrip("\n")


def renders_exist() -> list[str]:
    found = [str(RUNS)] if RUNS.exists() else []
    found += [str(p) for p in RENDERS.glob("*/*/matrix.json")] if RENDERS.exists() else []
    return found


def part1(commit: str) -> dict:
    text = charter_at(commit)
    sys.path.insert(0, str(PROBES))
    import probe  # noqa: E402  (scenes, specs)
    specs = probe.specs()
    cells = {label: {f"{s}x": probe.scenes(label, s) for s in (1, 2)} for label in specs}
    predict = json.loads((PROBES / "predict.json").read_text())
    smoke = json.loads((PROBES / "smoke" / "smoke.json").read_text())
    candidates = {label: sha(probe.CANDIDATES / label / "candidate.json") for label in specs}
    withheld = [dict(scale=r["scale"], scene=r["scene"], partition=r["partition"], role=r["role"],
                     predicted={v: round(p["t1"], 5) for v, p in r["predicted"].items()})
                for r in predict["rows"] if r["partition"] != "gate"]
    return {
        "schema": "w49a-part1",
        "wave": "W49a G0",
        "charter": {"path": CHARTER, "commit": commit},
        "rulings": {f"DL{n}": ruling(text, n) for n in (1, 3, 6, 8)},
        "family": {
            "name": "R",
            "members": {"receded.dark": ["tintAlphaFar1x", "tintAlphaFar2x"]},
            "domain": [-0.3, 0.2],
            "activeUnmoved": "b2d074d2df24 (791cde91d97acbc7); the builder refuses any other override on base b2d074",
            "scaleSeparable": "at dpr exactly 1 a cell reads only tintAlphaFar1x, at 2 only tintAlphaFar2x "
                              "(rampAtScale); a landing composes the two scales' selections",
            "reach": "receded surfaces of span > 96 CSS px: rrect-lg (farS 1), rrect-ml (0.5), the glass-over-glass "
                     "base (about 0.55); farS = 0 at or below 96",
        },
        "probes": {
            "P1": {"spec": "probes/specs/p1-d0219-top160.json", "base": "d0219",
                   "overrides": specs["p1-d0219-top160"]["overrides"], "cells": cells["p1-d0219-top160"],
                   "purpose": "F2 by render, recorded for W49b; selects nothing in W49a",
                   "prediction": {"1x": {"checkerboard-32__rrect-lg__rest": 0.0228,
                                         "checkerboard-64__rrect-lg__rest": 0.0297,
                                         "hc-text-28__rrect-lg__rest": 0.0270},
                                  "2x": {"checkerboard-32__rrect-lg__rest": 0.0283,
                                         "checkerboard-64__rrect-lg__rest": 0.0347,
                                         "hc-text-28__rrect-lg__rest": 0.0287}},
                   "bar": "each within its cell's B of the prediction"},
            "P2": {"specs": {label: f"probes/specs/{label}.json" for label in specs if label.startswith("p2-")},
                   "base": "b2d074", "far": [-0.1, 0, 0.05, 0.09, 0.1, 0.15],
                   "cells": cells["p2-far0.09"],
                   "rest": "read b2d074d2df24 by construction (the receded document is not drawn in the rest pose)",
                   "purpose": "the rendered points part 2's selection reads"},
            "candidates": candidates,
            "protocol": {"mode": "candidate (compare --candidate-document), scratch --out-matrix and capture tree",
                         "renderer": "webgpu", "sets": probe.SETS, "profiles": probe.R.PROFILES,
                         "scratch": str(probe.SCRATCH), "candidatesIn": "probes/candidates (repository)",
                         "census": "W43 G3 (ii) stage/census.py and the pin Playwright 1.62.1 / Chromium 1234 "
                                   "(151.0.7922.34); a refusal launches nothing", "lock": str(probe.LOCK),
                         "reading": "W48's cut launcher, --kind candidate, reference d0219cd684bf, reference captures "
                                    "web-captures-superseded/d0219cd684bf", "withheld": "no referee or holdout cell "
                                    "is rendered (DL6)"},
        },
        "predictions": {"method": "probes/predict.py: a line in alphaBase through b2d074d2df24 and W46's point A "
                                  "(gate cells), through b2d074 and d0219 (withheld rrect-lg), proportional to "
                                  "1 - alphaBase (withheld glass-over-glass); first order, stated before any render",
                        "file": "probes/predict.json", "expected": "no P2 point meets DL2 at either scale: every far "
                        "that repairs checkerboard-64__rrect-lg__inactive moves impulse__rrect-ml__inactive away "
                        "from b2d074d2df24 beyond B", "withheld": withheld},
        "invariants": {
            "X75": {"bound": 0.95, "floatAllowance": 1e-9, "spans": "0..1024 CSS px, integer", "dpr": [1, 2],
                    "tiers": ["webgpu", "css"], "variants": ["regular", "clear"], "policy": "nominal",
                    "statement": "packages/calibration/scripts/no-opaque-glass.ts",
                    "test": "packages/calibration/test/x75-no-opaque-glass.test.ts",
                    "on028": "fails exactly apple-macos-27.0-glass0.25 dark receded, from span 140, both tiers and "
                             "scales (x75/x75-on-0.28.0-unmarked.txt); an expected failure naming W49a, removed at G2",
                    "refusals": ["fit/build-candidate.ts", "seal/seal.ts"]},
            "X74": {"report": "probes/rule.py authority(): over a probe's points, a cell with one distinct reading is "
                              "outside reach and named, its reason predicted where farS = 0; the objective excludes it",
                    "control": "each outside-reach cell reads its b2d074d2df24 value within 0.1 bar, else VOID"},
            "X76": {"rule": "seal/seal.ts: a receded leaf stated at its active's resolved value, or an active-fitted "
                            "leaf the receded does not name, needs { held: [reading] } in the method record",
                    "audit": "x76/audit.txt"},
        },
        "smoke": {"file": "probes/smoke/smoke.json", "read": smoke["read"], "published": smoke["publishedD0219"],
                  "exactlyEqual": smoke["exactlyEqual"]},
        "order": "no probe render before both parts are hashed; each part amended at most once and only before the "
                 "first probe render",
        "pins": pins(PART1_PINS + [f"packages/calibration/results/2026-10-07-w49a-g0-declaration/probes/specs/{p.name}"
                                   for p in sorted((PROBES / "specs").glob("*.json"))]),
    }


def part2(commit: str, part_one_hash: str) -> dict:
    text = charter_at(commit)
    return {
        "schema": "w49a-part2",
        "wave": "W49a G0",
        "partOne": part_one_hash,
        "charter": {"path": CHARTER, "commit": commit},
        "rulings": {f"DL{n}": ruling(text, n) for n in (2, 4, 5, 7)},
        "landingRule": {
            "scope": "per dark 0.25 profile (1x, 2x), WebGPU tier, T1 by W44 G1's classify: B = max(code, 2 bar), "
                     "growth |k - n| - |c - n|; T cells read away on T1-low",
            "a": "checkerboard-64__rrect-lg__inactive against d0219cd684bf, growth <= B at the gate; "
                 "checkerboard-32__rrect-lg__inactive and photo__rrect-lg__inactive the same, at read 9",
            "b": "hc-text__, impulse__ and checkerboard-8__rrect-lg__inactive against d0219cd684bf, growth <= B",
            "c": "every other cell against b2d074d2df24: zero cells away with growth > B (none past 3 B)",
            "d": "C rest at both scales and F inactive at 1x against d0219cd684bf, every partition, A <= A_ref / 2; "
                 "at the gate a withheld cell R cannot move enters at its read-8 value",
            "X75": "the builder refuses any point that draws opaque glass",
            "implementation": "probes/rule.py evaluate_profile",
        },
        "selection": {
            "objective": "per scale, the median |log((k + code)/(n + code))| over X74's reachable gate cells",
            "tie": "points within tau of the minimum, tau the median log(1 + bar/(n + code)) over the same cells",
            "tieBreak": "the largest far delta (the smallest departure from the shipped bytes)",
            "landing": "(far1x, far2x) of the two scales' selections",
            "none": "a scale with no point meeting DL2: NEITHER; W49a closes at the finding and the parent asks "
                    "the user (DL4)",
            "void": "X74's control failing at a scale voids that scale's selection",
            "implementation": "probes/rule.py select",
        },
        "reads": {
            "gate": "P2's rendered gate cells, rest cells by construction; the report, then STOP for the parent",
            "read9": "once, on the selected point only, sealed, in a strict-mode stage: every DL2 clause over all "
                     "partitions, the two withheld repair cells binding; the other withheld cells against part 1's "
                     "predictions (DL6). A clause failing there: W49a closes at the finding and the parent asks "
                     "the user; no other point is read",
            "owner": "the owner test's other adopted rows (M2, L1, E2, T1 blocks) at G2; a failure stops for the "
                     "parent",
        },
        "amendmentAfterGate": "none",
        "pins": pins(PART2_PINS),
    }


def canonical(body: dict) -> str:
    return json.dumps(body, indent=1, sort_keys=True, ensure_ascii=False) + "\n"


def recorded(path: Path) -> str | None:
    return path.read_text().splitlines()[-1].split()[0] if path.exists() else None


def write(path: Path, body: dict, sha_path: Path, append: bool) -> str:
    text = canonical(body)
    path.write_text(text)
    digest = hashlib.sha256(text.encode()).hexdigest()
    line = f"{digest}  {path.name}\n"
    sha_path.write_text((sha_path.read_text() if append and sha_path.exists() else "") + line)
    return digest


def check() -> int:
    if not (PART1.exists() and SHA1.exists() and PART2.exists() and SHA2.exists()):
        print("not hashed: declaration.json / fit-declaration.json and their .sha256 are not all present")
        return 1
    one, two = json.loads(PART1.read_text()), json.loads(PART2.read_text())
    problems = []
    for path, sha_path in ((PART1, SHA1), (PART2, SHA2)):
        if sha(path) != recorded(sha_path):
            problems.append(f"{path.name} hashes to {sha(path)[:12]}, not its recorded {str(recorded(sha_path))[:12]}")
    fresh1 = part1(one["charter"]["commit"])
    if canonical(fresh1) != PART1.read_text():
        diff = [k for k in fresh1 if fresh1[k] != one.get(k)]
        moved = [p for p, h in fresh1["pins"].items() if one["pins"].get(p) != h]
        problems.append(f"part 1 does not reassemble from the tree: {diff}; pins moved {moved}")
    fresh2 = part2(two["charter"]["commit"], recorded(SHA1))
    if canonical(fresh2) != PART2.read_text():
        diff = [k for k in fresh2 if fresh2[k] != two.get(k)]
        moved = [p for p, h in fresh2["pins"].items() if two["pins"].get(p) != h]
        problems.append(f"part 2 does not reassemble from the tree: {diff}; pins moved {moved}")
    if problems:
        print("REFUSES:\n  " + "\n  ".join(problems))
        return 1
    print(f"both parts hashed and checked: part 1 {recorded(SHA1)}, part 2 {recorded(SHA2)}"
          + (f"; amendments {len(json.loads(AMENDMENTS.read_text()))}" if AMENDMENTS.exists() else ""))
    return 0


def hash_(commit: str) -> int:
    if renders_exist():
        raise Refusal(f"hash: a probe render exists ({renders_exist()[:2]}); the declaration comes first")
    if SHA1.exists() or SHA2.exists():
        raise Refusal("hash: already hashed; `amend` is the only route, and only before the first render")
    h1 = write(PART1, part1(commit), SHA1, append=False)
    h2 = write(PART2, part2(commit, h1), SHA2, append=False)
    print(f"part 1 {h1}\npart 2 {h2}")
    return 0


def amend(part: int, reason: str, commit: str | None) -> int:
    if renders_exist():
        raise Refusal("amend: a probe render exists; neither part admits an amendment after it (DL4)")
    record = json.loads(AMENDMENTS.read_text()) if AMENDMENTS.exists() else []
    if any(r["part"] == part for r in record):
        raise Refusal(f"amend: part {part} has been amended once; a further amendment refuses")
    if not reason.strip():
        raise Refusal("amend: a reason is required")
    old1, old2 = recorded(SHA1), recorded(SHA2)
    if part == 1:
        c = commit or json.loads(PART1.read_text())["charter"]["commit"]
        h1 = write(PART1, part1(c), SHA1, append=True)
        # Part 2 names part 1's hash, so it is re-stated over the new one (an amendment of part 1 forces it).
        h2 = write(PART2, part2(json.loads(PART2.read_text())["charter"]["commit"], h1), SHA2, append=True)
    else:
        c = commit or json.loads(PART2.read_text())["charter"]["commit"]
        h1, h2 = old1, write(PART2, part2(c, old1), SHA2, append=True)
    record.append(dict(part=part, reason=reason, at=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                       supersedes={"part1": old1, "part2": old2}, now={"part1": h1, "part2": h2}))
    AMENDMENTS.write_text(json.dumps(record, indent=1) + "\n")
    print(f"amended part {part}: part 1 {h1}, part 2 {h2}")
    return 0


def main(argv) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="verb", required=True)
    sub.add_parser("check")
    h = sub.add_parser("hash")
    h.add_argument("--charter-commit", required=True)
    a = sub.add_parser("amend")
    a.add_argument("--part", type=int, choices=(1, 2), required=True)
    a.add_argument("--reason", required=True)
    a.add_argument("--charter-commit")
    args = ap.parse_args(argv[1:])
    if args.verb == "check":
        return check()
    if args.verb == "hash":
        return hash_(args.charter_commit)
    return amend(args.part, args.reason, args.charter_commit)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
