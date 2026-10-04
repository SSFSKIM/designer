#!/usr/bin/env python3.12
"""W45 G1: the stage's CSS rows re-read in place after the CSS tier's light 0.25 decline (the
parent's ruling of 2026-10-04; claims §5.206 §15).

    python3.12 -B css_hold_reread.py

The same argv `stage/stage.py measure` builds for the CSS tier, per light profile: `--set
calibration,validation,recorded`, then `--set probe --scene <the planner's pre-gate list>`, each with
`--alpha --write-partial` into the declared stage (`compare --stage`, which upserts each row by its
member key and validates every row against the declaration). The 2x profile is the re-read and the
1x profile the X48-style witness. No referee or holdout cell is in either pass. `stage.py` itself
skips passes it has completed, so this script launches them under new labels (`css-hold/...`),
through `with-gpu.sh` (the GPU lock and the classifying census), logged in this directory's
`runs.jsonl` and `logs/` beside the first measure's.
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
STAGE_TOOL = HERE.parents[1] / "2026-10-03-w45-g0-operator" / "stage"
sys.path.insert(0, str(STAGE_TOOL))
import stage as S  # noqa: E402  (W45's pinned stage tool: its launch, logging and passes)

W = S.W
# The first re-read (`css-hold/...`) drew rows byte-identical to the first measure: the decline's
# first cut let an app's value through, and the harness hands the shipped document's patch to the
# root as the app's too. The decline now treats the document's own value as no tune; the second
# re-read is labelled `css-hold-2/...`.
PREFIX = sys.argv[1] if len(sys.argv) > 1 else "css-hold"


def main() -> int:
    S.require_sealed()
    stage = W.refuse_w44_path(W.STAGE, "the stage")
    out = W.refuse_w44_path(W.G1_STAGE, "the stage's evidence")
    for profile in (W.PROFILE[2], W.PROFILE[1]):
        for suffix, sets, scenes in S.passes("measure", profile):
            label = f"{PREFIX}/css/{profile}/{suffix}"
            argv = ["pnpm", "run", "-s", "compare", "--", "--stage", str(stage), "--profile", profile,
                    "--renderer", "css", "--material-profile", S.ACTIVE, "--receded-profile", S.RECEDED,
                    "--set", sets, "--alpha", "--write-partial"]
            if scenes is not None:
                argv += ["--scene", ",".join(scenes)]
            code = S.launch(argv, label, out, "g1", scenes)
            if code not in (0, 1):
                raise W.Refusal(f"{label}: exit {code}; stop")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
