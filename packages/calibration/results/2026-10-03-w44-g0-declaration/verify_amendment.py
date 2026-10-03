#!/usr/bin/env python3.12
"""W44 G1 step 0, a correction beside `declare.py` (the review of G1 steps 0-2, P2): part 2's one
amendment is checked for its VALUES, not only its paths.

`declare.py`'s `validate_ops` refuses an operation outside its ruling's paths, an unknown ruling, a
removal, a path touched twice and a missing ruling, and `check-fit` proves the superseded part 2
rebuilds byte for byte. Neither constrains the value an authorized path receives: an operation
replacing `landingRule.fullClose` under ruling 3 with any text at all would pass both. The
deterministic transformation that defines the five rulings is `declare.amendment_one`, so the
complete check is that the recorded operations ARE `amendment_one` applied to the rebuilt
superseded body: same paths, kinds, rulings, `from` and `to`, in order.

`declare.py` cannot carry this check itself: the amendment records its bytes as part 1's one
accepted re-pin (`fit-amendments.json`, `partOnePins`), so any edit to it would fail part 1's
`check`. This file sits beside it, and `test_verify_amendment.py` holds its red case (an
unauthorized value at an authorized path).

    python3.12 -B verify_amendment.py      exit 0 when the recorded amendment is exactly the five
                                           rulings' transformation, 1 otherwise
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import declare as D  # noqa: E402


def differences(fit: dict, ops: list) -> list[str]:
    """Every way `ops` differs from `amendment_one` on the body `ops` reverts `fit` to."""
    try:
        before = D.revert_ops(fit, ops)
    except D.Refusal as err:
        return [f"the operations do not revert: {err}"]
    want = D.amendment_one(before)
    out = []
    if len(ops) != len(want):
        out.append(f"{len(ops)} operations recorded, the five rulings' transformation has {len(want)}")
    for i, (got, exp) in enumerate(zip(ops, want)):
        for key in ("ruling", "kind", "path", "from", "to"):
            if (key in got) != (key in exp) or got.get(key) != exp.get(key):
                out.append(f"operation {i + 1} ({'/'.join(map(str, exp['path']))}): its {key} is not the "
                           f"ruling's")
    return out


def main() -> int:
    record = D.amendments("fit")
    if len(record) != 1:
        print(f"verify_amendment: {len(record)} amendments recorded, not one")
        return 1
    fit = json.loads(D.PARTS["fit"]["declaration"].read_text())
    found = differences(fit, record[0]["ops"])
    for line in found:
        print("  MISMATCH", line)
    if found:
        print(f"verify_amendment: {len(found)} difference(s) from the five rulings' transformation")
        return 1
    print(f"verify_amendment: the recorded amendment is exactly the five rulings' transformation "
          f"({len(record[0]['ops'])} operations, values included)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
