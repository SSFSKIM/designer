#!/usr/bin/env python3
"""W31 G4 review closure — the fifth perturbation, for the per-bed count guard
(claims §5.165 §9, finding N8).

    python3 cut-discrimination-closure.py   # writes cut-discrimination-closure.txt

`cut-discrimination.py` proved four of the five cases this gate adopted can go
red. The fifth — *"carries every bed the two documents draw, at the cell counts
the read left"* — was not perturbed, so the one case whose whole job is to catch
a bed that quietly stopped contributing was itself the one clause nobody had seen
fail. That is the class both W31 G2's closure and G3c's `append-check-discrimination`
both name: a clause that cannot fail reads PASS forever.

The perturbation is the guard's own failure mode, taken from its comment: **a bed
loses a cell**. One `dark|active` row is dropped from the committed cut — the
smallest bed, four cells, where a silent loss would move the median most — and the
suite is run against it.

This script does not rewrite `cut-discrimination.txt`, which is committed
evidence. It writes its own file beside it and restores the cut byte for byte,
which is asserted rather than assumed.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
CUT = HERE / "chroma-cut.json"

_spec = importlib.util.spec_from_file_location("cut_discrimination", HERE / "cut-discrimination.py")
assert _spec is not None and _spec.loader is not None
_base = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_base)

run = _base.run
failed_cases = _base.failed_cases


def main() -> int:
    original = CUT.read_bytes()
    before = hashlib.sha256(original).hexdigest()
    report = [
        "W31 G4 review closure — the fifth perturbation (claims §5.165 §9, finding N8).",
        "",
        "`cut-discrimination.txt` perturbed four of the five cases this gate adopted.",
        "The fifth is the per-bed count guard, and this is it going red. The committed",
        "cut is restored byte for byte after it.",
        "",
        f"chroma-cut.json sha256 before: {before}",
        "",
    ]

    status, output = run()
    report.append(f"── baseline (the committed cut)\n   exit={status}")
    report += [f"   RED: {case}" for case in failed_cases(output)] or ["   RED: (none)"]
    report.append("")

    cut = json.loads(original)
    dropped = next(
        row for row in cut["cells"] if row["scheme"] == "dark" and row["pose"] == "active"
    )
    cut["cells"] = [row for row in cut["cells"] if row is not dropped]
    cut["beds"]["dark|active"]["n"] = len(
        [row for row in cut["cells"] if row["scheme"] == "dark" and row["pose"] == "active"]
    )
    CUT.write_text(json.dumps(cut, indent=2) + "\n")
    status, output = run()
    cases = failed_cases(output)
    CUT.write_bytes(original)

    label = (
        f"5. one dark|active cell dropped from the bed "
        f"({dropped['profile']} {dropped['scene']})"
    )
    report.append(f"── {label}\n   exit={status}")
    report += [f"   RED: {case}" for case in cases] or [
        "   RED: (none — THE CLAUSE CANNOT FAIL)"
    ]
    report.append("")

    guard = "carries every bed the two documents draw, at the cell counts the read left"
    caught = any(guard in case for case in cases)
    report.append(f"the per-bed count guard went red: {'YES' if caught else '*** NO ***'}")

    restored = hashlib.sha256(CUT.read_bytes()).hexdigest()
    report.append(f"chroma-cut.json sha256 after: {restored}")
    report.append(
        "RESTORED, byte for byte" if restored == before else "*** THE CUT DID NOT COME BACK ***"
    )

    status, output = run()
    report.append(f"the suite at the restored cut: exit={status}")
    report += [f"   RED: {case}" for case in failed_cases(output)] or ["   RED: (none)"]

    text = "\n".join(report) + "\n"
    (HERE / "cut-discrimination-closure.txt").write_text(text)
    print(text)
    return 0 if caught and restored == before and status == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
