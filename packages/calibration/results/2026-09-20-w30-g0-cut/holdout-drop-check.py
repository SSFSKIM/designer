#!/usr/bin/env python3
"""W30 G0 (f) — the proof that the fit loop cannot read a holdout row.

    python3 holdout-drop-check.py > holdout-drop-check.txt

The drop moved from `shadow-table.py`'s own filter into `fit.py`'s `cells()`,
the single function every reader built on that file takes its rows from
(claims §5.156 §4; the tracker's "the fit loop's holdout drop lives in one
reader, and the other reader has none"). A guarantee by construction is only a
guarantee if something exercises it, so this builds a scratch matrix that
CONTAINS a holdout row — the failure the drop exists for — and runs every
reader over it.

It writes into a temporary directory and points `VITREA_G3_SCRATCH` at it, so
nothing outside that directory is touched: no capture, no canonical matrix, no
profile, no fixture (X2, X5). The scratch cells are synthetic, three of them,
with the smallest shape each reader needs.

What is asserted, per reader:
  - without the flag, no holdout scene id appears on any TABLE line — the drop
    notice's own `#` lines name the dropped row on purpose, and naming what was
    refused is the opposite of reading it;
  - the notice is present and carries the count, so the drop is never silent;
  - a non-holdout row IS printed, so the check cannot pass because the reader
    printed nothing;
  - with `--with-holdout` the holdout scene reaches the table — so the check is
    discriminating rather than vacuously satisfied.

And, since the review closure (W30 Decision Log 3 (e), claims §5.156 §9), one
channel further: `fit.py render` writes `compare`'s own stdout to the label's
log, so a round invoked with `--set holdout` or a holdout `--scene` put a
holdout number one `cat` away while every table stayed clean. `render` now
refuses that selection unless `--with-holdout` is typed, and the check exercises
`capture_refusal()` DIRECTLY — the argument check in isolation, with no capture,
no browser and no `compare` process (X2, X5).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESULTS = HERE.parent
FIT = RESULTS / "2026-09-19-w29-g3-refit" / "fit.py"
SHADOW_TABLE = RESULTS / "2026-09-19-w29-g3b-shadow-recede" / "shadow-table.py"

HOLDOUT_SCENE = "checkerboard__rrect-lg__rest"
KEPT_SCENE = "checkerboard__rrect-md__rest"
PROFILE = "apple-macos-27.0-1x-light-standard-glass0.5"


def load(path: Path):
    """`fit.py` as a module, so its predicates can be exercised without its verbs."""
    spec = importlib.util.spec_from_file_location("fit_under_check", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cell(scene: str, fixture_set: str) -> dict:
    """One synthetic cell with the material and shadow blocks both readers need."""
    return {
        "key": {
            "profileKey": PROFILE,
            "sceneId": scene,
            "web": {"renderer": "webgpu", "capturePath": "synthetic"},
        },
        "fixtureSet": fixture_set,
        "state": "rest",
        "tier": "texture",
        "material": {
            "axis": "material",
            "interiorMeanNative": {"value": 0.5, "units": "luminance"},
            "interiorMeanWeb": {"value": 0.5, "units": "luminance"},
        },
        "shadow": {
            "axis": "shadow",
            "meanDepartureNative": {"value": 0.001, "units": "luminance"},
            "meanDepartureWeb": {"value": 0.001, "units": "luminance"},
        },
        "perceptual": {"axis": "perceptual"},
    }


def run(argv: list[str], scratch: Path) -> str:
    result = subprocess.run(
        [sys.executable, *argv],
        capture_output=True,
        text=True,
        env={**os.environ, "VITREA_G3_SCRATCH": str(scratch)},
    )
    if result.returncode != 0:
        raise SystemExit(f"{argv}: exit {result.returncode}\n{result.stdout}\n{result.stderr}")
    return result.stdout


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory(prefix="w30-holdout-") as temporary:
        scratch = Path(temporary)
        label = scratch / "fit-log" / "check"
        label.mkdir(parents=True)
        (label / f"{PROFILE}.webgpu.json").write_text(
            json.dumps(
                {
                    "schemaVersion": 5,
                    "cells": [
                        cell(KEPT_SCENE, "calibration"),
                        cell(HOLDOUT_SCENE, "holdout"),
                        cell("photo__rrect-md__rest", "validation"),
                    ],
                }
            )
        )
        print("W30 G0 (f) — the holdout drop, by construction")
        print("=" * 76)
        print()
        print(f"A scratch matrix of three cells, one of them `{HOLDOUT_SCENE}` at")
        print("fixtureSet `holdout` — the row the drop exists for. Every reader built on")
        print("`fit.py`'s `cells()` is run over it, with and without the flag.")
        print()

        def table_lines(output: str) -> list[str]:
            """The reader's TABLE — its `#` notice lines are not part of it."""
            return [line for line in output.splitlines() if not line.startswith("#")]

        for name, argv in (
            ("fit.py table", [str(FIT), "table", "check"]),
            ("shadow-table.py", [str(SHADOW_TABLE), "check"]),
        ):
            without = run(argv, scratch)
            with_flag = run([*argv, "--with-holdout"], scratch)
            table_without = "\n".join(table_lines(without))
            notice = "\n".join(line for line in without.splitlines() if line.startswith("#"))
            print(f"--- {name}")
            print("    on the table, default:  "
                  f"{'holdout scene ABSENT' if HOLDOUT_SCENE not in table_without else 'PRESENT'}")
            print("    drop notice:            "
                  f"{'present, count 1' if '1 holdout row(s)' in notice else 'MISSING'}")
            print("    notice names the row:   "
                  f"{'yes' if HOLDOUT_SCENE in notice else 'no'}")
            print("    a kept row IS printed:  "
                  f"{'yes' if KEPT_SCENE in table_without else 'NO'}")
            print("    with --with-holdout:    "
                  f"{'holdout scene reaches the table' if HOLDOUT_SCENE in '\n'.join(table_lines(with_flag)) else 'STILL ABSENT'}")
            print()
            if HOLDOUT_SCENE in table_without:
                failures.append(f"{name}: a holdout scene reached the table without the flag")
            if "1 holdout row(s)" not in notice:
                failures.append(f"{name}: the drop was silent")
            if HOLDOUT_SCENE not in notice:
                failures.append(f"{name}: the notice did not name what it dropped")
            if KEPT_SCENE not in table_without:
                failures.append(f"{name}: the reader printed nothing, so the check is vacuous")
            if HOLDOUT_SCENE not in "\n".join(table_lines(with_flag)):
                failures.append(f"{name}: --with-holdout did not admit the row")

        # `fit.py render`'s own argument check, exercised in isolation. The verb
        # itself would capture, so what is run is the predicate `render` consults
        # before it does anything — which is the whole of the guarantee, and the
        # only part of it that can be exercised without a browser.
        fit = load(FIT)
        holdout_ids = sorted(fit.holdout_scenes())
        a_holdout_scene = holdout_ids[0]
        a_kept_scene = KEPT_SCENE
        if a_kept_scene in fit.holdout_scenes():
            failures.append("render: the control scene is itself holdout, so the check is vacuous")
        cases = [
            ("--set holdout", ["--set", "holdout"], False, True),
            ("--set calibration,holdout", ["--set", "calibration,holdout"], False, True),
            (f"--scene {a_holdout_scene}", ["--scene", a_holdout_scene], False, True),
            ("--set calibration", ["--set", "calibration"], False, False),
            (f"--scene {a_kept_scene}", ["--scene", a_kept_scene], False, False),
            ("--set holdout --with-holdout", ["--set", "holdout"], True, False),
            (f"--scene {a_holdout_scene} --with-holdout", ["--scene", a_holdout_scene], True, False),
        ]
        print("--- fit.py render (the argument check, in isolation)")
        print(f"    {len(holdout_ids)} declared holdout ids, read from scenes.json's own split")
        for label, argv, with_holdout, expected in cases:
            refusal = fit.capture_refusal(argv, with_holdout)
            got = refusal is not None
            print(f"    {label:<66}{'REFUSED' if got else 'allowed'}"
                  f"{'' if got == expected else '   <-- WRONG'}")
            if got != expected:
                failures.append(
                    f"render: `{label}` was {'refused' if got else 'allowed'} and should not be"
                )
        print()

        # `merge` writes a file rather than a table, so it is checked on the file.
        merged = scratch / "merged.json"
        run([str(FIT), "merge", str(merged), "check"], scratch)
        scenes = {c["key"]["sceneId"] for c in json.loads(merged.read_text())["cells"]}
        run([str(FIT), "merge", str(merged), "check", "--with-holdout"], scratch)
        scenes_with = {c["key"]["sceneId"] for c in json.loads(merged.read_text())["cells"]}
        print("--- fit.py merge")
        print(f"    default:          {sorted(scenes)}")
        print(f"    --with-holdout:   {sorted(scenes_with)}")
        print()
        if HOLDOUT_SCENE in scenes:
            failures.append("merge: a holdout row survived into the merged file")
        if HOLDOUT_SCENE not in scenes_with:
            failures.append("merge: --with-holdout did not admit the row")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("OK — no reader yields a holdout number without the flag, every reader yields")
    print("     one with it, and `render` refuses to CAPTURE a holdout selection without it.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
