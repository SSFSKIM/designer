#!/usr/bin/env python3
"""W30 G3 — one fit round: six profiles, one tier, one pair of candidate documents.

    VITREA_G3_SCRATCH=/tmp/w30g3 python3 round.py <label> <doc-dir> \
        [--sets calibration,probe] [--renderer webgpu] [--profiles a,b]

Every capture goes through W29 G3's `fit.py render`, imported rather than
reimplemented, so this round inherits its three refusals (another capture
process, an accessibility toggle that is not 0, a slider that is not 0.5), its
scratch-only output, and — the one that matters for X4 — `capture_refusal()`,
which refuses a `--set` or a `--scene` naming the holdout before any side effect
exists. THE FIT NEVER READS A HOLDOUT ROW and never captures one.

The receded document is passed on every round, because the inactive rows are in
the population B3's stop is read over and posing them from the runtime's own
endpoint instead would make the round a different bed from the canonical read.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "2026-09-19-w29-g3-refit"))
from fit import render  # noqa: E402

PROFILES = [
    "apple-macos-27.0-1x-light-standard-glass0.5",
    "apple-macos-27.0-2x-light-standard-glass0.5",
    "apple-macos-27.0-1x-dark-standard-glass0.5",
    "apple-macos-27.0-2x-dark-standard-glass0.5",
    "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
    "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5",
]

ACTIVE = {
    "light": "apple-macos-27.0-1x-light-standard-glass0.5",
    "dark": "apple-macos-27.0-1x-dark-standard-glass0.5",
}


def option(argv: list[str], name: str, default: str) -> str:
    return argv[argv.index(f"--{name}") + 1] if f"--{name}" in argv else default


def main(argv: list[str]) -> int:
    label, doc_dir = argv[0], Path(argv[1])
    sets = option(argv, "sets", "calibration,probe")
    renderer = option(argv, "renderer", "webgpu")
    profiles = option(argv, "profiles", ",".join(PROFILES)).split(",")
    # A scene list, for the rounds that read the pitch ladder alone: the scatter
    # is identified on the ladder and a whole calibration set beside it is four
    # minutes of capture per profile that no scatter leaf is read on.
    scenes = option(argv, "scene", "")
    for profile in profiles:
        scheme = "dark" if "-dark-" in profile else "light"
        document = doc_dir / f"{ACTIVE[scheme]}.json"
        receded = doc_dir / f"{ACTIVE[scheme]}-receded.json"
        started = time.time()
        print(f"── {label} / {profile} / {renderer} / set {sets} ──", flush=True)
        matrix = render(
            label, profile, renderer, document,
            ["--set", sets, "--receded-profile", str(receded)]
            + ([] if scenes == "" else ["--scene", scenes]),
        )
        print(f"   {matrix}  {time.time() - started:.0f} s", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    raise SystemExit(main(sys.argv[1:]))
