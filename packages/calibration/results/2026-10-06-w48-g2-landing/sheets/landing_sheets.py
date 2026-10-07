#!/usr/bin/env python3.12
"""W48 G2 (claims §5.214): the eye sheets over the whole dark bed at the landing, from the trees the landing
left. G1's `sheets/run.py` form: W47's `sheets/sheets.py`, inherited by path under W48's bindings, its
"W47" label corrected at draw time. Each row is Apple 0.25 | vitrea d0219cd684bf | vitrea W48 | the three
gain-lifted differences (the gain printed on the page), both tiers, both poses, both scales, every set.

What moves from G1's form, and nothing else: the W48 rows are the PUBLISHED generation file
(`generations/b2d074d2df24.json`) read off the canonical tree the landing copied G1's stage to, and the
`d0219cd684bf` twins are read off `web-captures-superseded/d0219cd684bf/`, where the landing moved them
(the tool reads its reference twins from `bindings.CANONICAL_CAPTURES`, re-bound here for this run). The
tool's `checked_png` holds every capture to its row's capturePath before a pixel is read. T1's states per
cell are the landing cut's.

    python3.12 -B landing_sheets.py OUT_DIR
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
sys.path.insert(0, str(CAL / "results" / "2026-10-06-w48-g0-declaration"))
import inherit  # noqa: E402

W = inherit.W
sheets = inherit.tool("sheets/sheets.py", "sheets")
_Draw = sheets.ImageDraw.Draw


class _W48Draw:
    def __init__(self, image, *a, **k):
        self._d = _Draw(image, *a, **k)

    def text(self, xy, text, *a, **k):
        return self._d.text(xy, text.replace("W47", "W48"), *a, **k)

    def __getattr__(self, name):
        return getattr(self._d, name)


sheets.ImageDraw.Draw = _W48Draw
CANONICAL = W.CANONICAL_CAPTURES
W.CANONICAL_CAPTURES = CANONICAL.parent / "web-captures-superseded" / "d0219cd684bf"
args = ["--stage", str(CAL / "results" / "generations" / "b2d074d2df24.json"), "--stage-captures", str(CANONICAL),
        "--out", sys.argv[1], "--whole",
        "--cut", str(HERE.parent / "cuts" / "cut-025-dark-w48-landing.json")]
sys.exit(sheets.main(args))
