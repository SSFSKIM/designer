#!/usr/bin/env python3
"""W31 G4 — proof that M1, M2 and the cut's own re-derivation can go red.

    python3 cut-discrimination.py            # writes cut-discrimination.txt

W31 G2's closure and W31 G3c's `append-check-discrimination.txt` both record the
same lesson from different directions: **a clause that cannot fail reads PASS
forever**, and the only way that class is ever found is by making it fail on
purpose. A newly adopted row is exactly where that matters, because it has never
been red and nothing yet knows whether it would be.

So this perturbs the committed `chroma-cut.json` one field at a time, runs
`adopted-thresholds.test.ts` against each perturbation, and records which cases
went red. The cut is regenerated from `chroma-cut.py` at the end, so the
committed artefact is byte-identical to what the gate adopted — asserted here
rather than assumed.

The four perturbations, one per clause the gate rests on:

  1. a passing cell pushed past the per-cell ceiling — M1's per-cell clause AND
     the `MISSED_27_ROWS` owner, which must see a miss nobody recorded;
  2. a whole bed's `R` scaled so its median leaves [0.80, 1.20] — M1's median
     clause (and the cut's own summary, which is asserted to agree);
  3. one cell's `interiorStdDevWeb` moved 3 % off its pre-fit baseline — M2;
  4. one cell's `R` moved away from the matrix it was read off — the
     re-derivation, which is what keeps this cut from becoming a snapshot the way
     B1's was (claims §5.162 §9).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent.parent
REPO = PACKAGE.parent.parent
CUT = HERE / "chroma-cut.json"

TEST = ["npx", "vitest", "run", "test/adopted-thresholds.test.ts", "--reporter=verbose"]


def run() -> tuple[int, str]:
    out = subprocess.run(TEST, cwd=PACKAGE, capture_output=True, text=True)
    return out.returncode, out.stdout + out.stderr


def failed_cases(output: str) -> list[str]:
    return sorted(
        {
            line.split(" > ")[-1].strip()
            for line in output.splitlines()
            if line.strip().startswith("×") or line.strip().startswith("✗")
        }
    )


def perturb(original: bytes, label: str, mutate) -> str:
    """One perturbation from the committed cut, and the committed cut back after it.

    Restored between perturbations and not only at the end: a run that let them
    accumulate would report every later clause as red for the first one's reason
    and prove nothing about any of them but the first.
    """
    cut = json.loads(original)
    mutate(cut)
    CUT.write_text(json.dumps(cut, indent=2) + "\n")
    status, output = run()
    cases = failed_cases(output)
    CUT.write_bytes(original)
    lines = [f"── {label}", f"   exit={status}"]
    lines += [f"   RED: {case}" for case in cases] or ["   RED: (none — THE CLAUSE CANNOT FAIL)"]
    return "\n".join(lines)


def cell(cut: dict, scene: str, profile_fragment: str) -> dict:
    for row in cut["cells"]:
        if row["scene"] == scene and profile_fragment in row["profile"]:
            return row
    raise SystemExit(f"cut-discrimination: no cell {scene} on {profile_fragment}")


def main() -> int:
    original = CUT.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    report = [
        "W31 G4 — cut discrimination (claims §5.165 §1).",
        "",
        "The committed cut, perturbed one field at a time, with the cases each",
        "perturbation turns red. A green baseline is recorded first, because",
        '"it went red" means nothing without "and it was green before".',
        "",
        f"chroma-cut.json sha256 before: {before}",
        "",
    ]

    status, output = run()
    report.append(f"── baseline (the committed cut)\n   exit={status}")
    report += [f"   RED: {case}" for case in failed_cases(output)] or ["   RED: (none)"]
    report.append("")

    def push_over_ceiling(cut: dict) -> None:
        # `photo__rrect-md__rest` on the 2x dark profile reads 1.0935 and is not a
        # recorded miss. 1.45 puts it past the ceiling.
        cell(cut, "photo__rrect-md__rest", "2x-dark")["R"] = 1.45

    def move_a_median(cut: dict) -> None:
        # Halve every dark active cell: the median leaves the band from below and
        # the cut's own recorded median stops agreeing with the computed one.
        for row in cut["cells"]:
            if row["scheme"] == "dark" and row["pose"] == "active":
                row["R"] = row["R"] / 2

    def flatten_the_body(cut: dict) -> None:
        row = cell(cut, "photo__toolbar-group__rest", "1x-light")
        row["interiorStdDevWeb"] = row["interiorStdDevWebPreFit"] * 0.97
        row["structureDeltaFraction"] = -0.03

    def desync_from_the_matrix(cut: dict) -> None:
        cell(cut, "photo__rrect-ml__rest", "1x-light")["R"] += 0.05

    for label, mutate in (
        ("1. a passing cell pushed to R 1.45", push_over_ceiling),
        ("2. the dark active bed's R halved", move_a_median),
        ("3. one cell's interiorStdDevWeb moved 3% off its pre-fit baseline", flatten_the_body),
        ("4. one cell's R moved away from the matrix it was read off", desync_from_the_matrix),
    ):
        report.append(perturb(original, label, mutate))
        report.append("")

    restored = hashlib.sha256(CUT.read_bytes()).hexdigest()
    report.append(f"chroma-cut.json sha256 after the last perturbation: {restored}")
    report.append(
        "RESTORED, byte for byte" if restored == before else "*** THE CUT DID NOT COME BACK ***"
    )

    # And the script still writes what is committed. `generatedAt` is the one
    # field that cannot reproduce — it is the run's own clock — so it is excluded
    # by name and the exclusion is stated rather than folded into a tolerance.
    regenerated = subprocess.run(
        [sys.executable, str(HERE / "chroma-cut.py"), "--out", "/tmp/w31-g4-cut-check.json"],
        cwd=HERE,
        capture_output=True,
        text=True,
    )
    fresh = json.loads(Path("/tmp/w31-g4-cut-check.json").read_text())
    committed = json.loads(original)
    moved = sorted(
        key
        for key in set(fresh) | set(committed)
        if key != "generatedAt" and fresh.get(key) != committed.get(key)
    )
    report.append(
        f"chroma-cut.py re-run at this head reproduces the committed cut "
        f"(every field but generatedAt): {'YES' if not moved and regenerated.returncode == 0 else moved}"
    )

    status, output = run()
    report.append(f"the suite at the restored cut: exit={status}")
    report += [f"   RED: {case}" for case in failed_cases(output)] or ["   RED: (none)"]

    text = "\n".join(report) + "\n"
    (HERE / "cut-discrimination.txt").write_text(text)
    print(text)
    return 0 if restored == before and status == 0 and not moved else 1


if __name__ == "__main__":
    raise SystemExit(main())
