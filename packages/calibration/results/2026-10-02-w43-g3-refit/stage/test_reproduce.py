#!/usr/bin/env python3.12
"""W43 G3 (ii) review closure, finding 3: ``reproduce.py`` stops on a stage that lacks a c05 row.

At 48d3b744 the verdict read only the rows the stage carried, so a stage missing a candidate row
whose surviving rows all matched read REPRODUCED. This builds a synthetic tree under /tmp (two
stages, c05's matrix and both capture trees, every PNG byte-identical between the two), points
the module's ``STAGES``, ``C05`` and ``STAGE_CAPTURES`` at it and its output directory ``HERE``
at a scratch directory, then reads it with the fixed ``reproduce.py`` and, for contrast, with the
48d3b744 revision read out of git:

  (a) complete stages and one holdout row, ``--with-holdout``: REPRODUCED, exit 0 (the control);
  (b) the light stage without one c05 row, ``--with-holdout``: DIFFERS: STOP, exit 1, the row
      named in ``c05RowsWithNoStageRow`` (48d3b744: REPRODUCED, exit 0);
  (c) the same without the holdout row or the flag: the same verdict, written to
      ``reproduce.json`` in the scratch directory rather than ``reproduce-with-holdout.json``.

Pure Python over synthetic rows: no browser, no capture, no real stage read. The committed
``reproduce.json`` beside this file and any ``reproduce-with-holdout.json`` there are hashed
before and after and must not move. ``python3.12 -B test_reproduce.py`` prints the record
``test_reproduce.txt`` keeps, and exits 1 on any failed check.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reproduce as P  # noqa: E402

PRE_FIX = "48d3b744"
TMP = Path("/tmp/w43-g3-test-reproduce")
failures: list[str] = []


def check(ok: bool, what: str) -> None:
    print(f"    {'ok  ' if ok else 'FAIL'} {what}")
    if not ok:
        failures.append(what)


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else None


def pre_fix_module():
    """The 48d3b744 ``reproduce.py``, read out of git and loaded from the scratch tree."""
    source = subprocess.run(["git", "-C", str(HERE), "show", f"{PRE_FIX}:./reproduce.py"],
                            check=True, capture_output=True, text=True).stdout
    path = TMP / "pre-fix" / "reproduce.py"
    path.parent.mkdir(parents=True)
    path.write_text(source)
    spec = importlib.util.spec_from_file_location("reproduce_pre_fix", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def row(profile: str, renderer: str, scene: str, fixture_set: str, how: str) -> dict:
    return dict(key=dict(profileKey=profile, sceneId=scene,
                         web=dict(renderer=renderer, sceneId=scene, capturePath=how)),
                fixtureSet=fixture_set, capturedAt=f"{how} time", perceptual=dict(ssim=0.99))


PROFILES = {"light": "apple-macos-27.0-1x-light-standard-glass0.25",
            "dark": "apple-macos-27.0-1x-dark-standard-glass0.25"}
SCENES = ["photo__rrect-md__rest", "checkerboard__capsule-button__rest"]
MEASURED = [(scheme, renderer, scene) for scheme in PROFILES for renderer in ("webgpu", "css")
            for scene in SCENES]
HOLDOUT = ("light", "webgpu", "impulse__rrect-md__rest")
MISSING = ("light", "css", "checkerboard__capsule-button__rest")


def build(case: str, drop: tuple | None, holdout: bool) -> dict:
    """A synthetic tree for one case; returns the constants the module is pointed at."""
    root = TMP / case
    stages = {s: root / f"g3-stage-{s}" for s in PROFILES}
    c05, captures, out = root / "c05", root / "web-captures", root / "out"
    for directory in (*stages.values(), c05, out):
        directory.mkdir(parents=True)
    candidate = [row(PROFILES[s], r, sid, "calibration", "candidate") for s, r, sid in MEASURED]
    (c05 / "matrix.json").write_text(json.dumps(dict(cells=candidate)))
    for scheme, stage in stages.items():
        cells = [row(PROFILES[s], r, sid, "calibration", "strict") for s, r, sid in MEASURED
                 if s == scheme and (s, r, sid) != drop]
        if holdout and scheme == HOLDOUT[0]:
            cells.append(row(PROFILES[scheme], HOLDOUT[1], HOLDOUT[2], "holdout", "strict"))
        (stage / "matrix.json").write_text(json.dumps(dict(cells=cells)))
    for s, r, sid in MEASURED:
        for tree in (captures, c05 / "web-captures"):
            png = tree / PROFILES[s] / sid / f"{sid}__{r}.png"
            png.parent.mkdir(parents=True, exist_ok=True)
            png.write_bytes(f"{s} {r} {sid}".encode())
    return dict(STAGES=stages, C05=c05, STAGE_CAPTURES=captures, HERE=out)


def read(module, constants: dict, flag: bool) -> tuple[int, dict, list[str]]:
    """Run ``module.main`` over the tree; (exit code, the reading, the files it wrote)."""
    for name, value in constants.items():
        setattr(module, name, value)
    argv = sys.argv
    sys.argv = ["reproduce.py", *(["--with-holdout"] if flag else [])]
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            code = module.main()
    finally:
        sys.argv = argv
    written = sorted(p.name for p in constants["HERE"].iterdir())
    reading = json.loads((constants["HERE"] / written[0]).read_text()) if written else {}
    for path in constants["HERE"].iterdir():
        path.unlink()
    return code, reading, written


def summary(code: int, reading: dict, written: list[str]) -> str:
    return (f"{reading.get('verdict')!s:<14} exit {code}; stage {reading.get('stageRows')}, "
            f"holdout {reading.get('holdoutRows')}, c05 {reading.get('c05Rows')}, identical rows "
            f"{reading.get('identicalRowsExceptHowDrawn')}, captures "
            f"{reading.get('identicalCaptures')}, c05 rows with no stage row "
            f"{reading.get('c05RowsWithNoStageRow')}; wrote {written}")


def main() -> int:
    guarded = {name: digest(HERE / name) for name in ("reproduce.json",
                                                       "reproduce-with-holdout.json")}
    if TMP.exists():
        shutil.rmtree(TMP)
    old = pre_fix_module()
    print(f"W43 G3 (ii) review, finding 3: reproduce.py on an incomplete stage; pre-fix "
          f"{PRE_FIX}; synthetic tree under {TMP}")
    missing_key = [PROFILES[MISSING[0]], MISSING[1], MISSING[2]]
    for case, drop, holdout, flag, expected_file in [
            ("a-complete", None, True, True, "reproduce-with-holdout.json"),
            ("b-missing-with-holdout", MISSING, True, True, "reproduce-with-holdout.json"),
            ("c-missing-no-holdout", MISSING, False, False, "reproduce.json")]:
        print(f"  ({case[0]}) {case[2:]}{' --with-holdout' if flag else ''}")
        constants = build(case, drop, holdout)
        code, reading, written = read(P, constants, flag)
        print(f"      fixed:    {summary(code, reading, written)}")
        if drop is None:
            check(code == 0 and reading["verdict"] == "REPRODUCED"
                  and reading["c05RowsWithNoStageRow"] == [],
                  "fixed: a complete stage reads REPRODUCED, exit 0")
        else:
            check(code == 1 and reading["verdict"] == "DIFFERS: STOP"
                  and reading["c05RowsWithNoStageRow"] == [missing_key],
                  "fixed: the stage lacking one c05 row reads DIFFERS: STOP, exit 1, and names it")
        check(written == [expected_file], f"fixed: wrote {expected_file} and nothing else")
        code, reading, written = read(old, constants, flag)
        print(f"      {PRE_FIX}: {summary(code, reading, written)}")
    after = {name: digest(HERE / name) for name in guarded}
    check(after == guarded, "the files beside this script are unmoved: " + ", ".join(
        f"{name} {(value or 'absent')[:12]}" for name, value in after.items()))
    print(f"{'FAILED' if failures else 'PASSED'}: {len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
