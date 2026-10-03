#!/usr/bin/env python3.12
"""W45 G1: part 2's search, run with ONE correction beside the pinned tool (claims §5.206).

The defect. `search.label_of` (pinned by part 2 at e6874e02) marks a receded-light leaf with an
upper-case `R` (`c-s2-t0.75-Rt0.1`), and W45's builder (pinned by part 1) accepts only labels in
[a-z0-9.-], so stage 2's receded component cannot build its first point: c05's stage 2 stopped
there with nothing rendered (`logs/search-c05-stage2.attempt1.txt`; the refused spec is kept under
`specs-refused/`). No test caught it: the search tests' runner builds nothing, and the label test
asserts the upper-case form.

The correction. Part 2's second amendment was its last, and the builder is a part-1 pin, so
neither file moves. This wrapper imports the pinned `search.py` unchanged and replaces one
function: a receded-light leaf is marked `rc` (`c-s2-t0.75-rct0.1`), which no SHORT name begins
with. A label is a candidate's NAME: it changes no override, no grid, no domain, no objective and
no decision, and every point keeps the overrides its spec states (the review of G0's closure, P1).

    python3.12 -B search_g1.py stage stage2 --start c05|joint --base LABEL
"""
from __future__ import annotations

import sys
from pathlib import Path

G0_FIT = Path(__file__).resolve().parents[2] / "2026-10-03-w45-g0-operator" / "fit"
sys.path.insert(0, str(G0_FIT))
import search  # noqa: E402  (the pinned file, unchanged)


def label_of(start: str, stage_id: str, overrides: dict, base: dict) -> str:
    """`search.label_of` with the receded mark `rc` in place of `R` (the builder's [a-z0-9.-])."""
    parts = []
    for slot, leaves in sorted(overrides.items()):
        for leaf, v in sorted(leaves.items()):
            if base.get(slot, {}).get(leaf) != v:
                parts.append(f"{'rc' if slot == 'receded.light' else ''}{search.SHORT[leaf]}{search.fmt(round(v, 6))}")
    return f"{start[0]}-{search.STAGE_SHORT.get(stage_id, stage_id)}" + ("-" + "-".join(parts) if parts else "-base")


search.label_of = label_of

if __name__ == "__main__":
    sys.exit(search.main(sys.argv))
