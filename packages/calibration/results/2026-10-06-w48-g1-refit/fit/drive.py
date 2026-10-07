#!/usr/bin/env python3.12
"""W48 G1: run a fit command (this directory's `fit.py`, W47's driver with X70) to completion across
census refusals. W46 G1's `drive.py`, re-bound to W48 (the bindings through `inherit`, G1's logs here).

The classifying census REFUSES a launch while another session's browser automation is up (§5.201 §21),
and the pinned fit driver stops the search there (`Runner.points`: "census refused before ...; nothing
after it rendered"), leaving that launch's compare log, which `render_scale` opens exclusively. This
driver changes no pinned tool. On a refusal it:
  1. renames each refused launch's log to `<log>.census-refused-<n>.txt` (kept as evidence; the launch
     itself is logged in runs.jsonl with exit code 3),
  2. waits until the census would pass (read without logging), backing off from 60 s to 10 min,
  3. reruns the command, which resumes: built points, renders and readings are memoized.
Any other failure stops it.

    python3.12 -B drive.py <log name> -- <command and arguments, run from this directory>
"""
from __future__ import annotations

import datetime
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parents[1] / "2026-10-06-w48-g0-declaration"
sys.path.insert(0, str(G0))
import inherit  # noqa: E402

W = inherit.W
LOGS = HERE / "logs"


def refused_logs() -> list[Path]:
    out = []
    for f in sorted(LOGS.glob("*.txt")) if LOGS.exists() else []:
        if ".census-refused-" in f.name:
            continue
        first = f.read_text().splitlines()[:1]
        if first and first[0].startswith("census ") and ": REFUSES" in first[0]:
            out.append(f)
    return out


def set_aside(f: Path) -> Path:
    n = 1
    while (dest := f.with_name(f"{f.stem}.census-refused-{n}.txt")).exists():
        n += 1
    f.rename(dest)
    return dest


def census_passes() -> bool:
    return bool(W.census().observe()["passes"])


def note(text: str) -> None:
    print(f"[{datetime.datetime.now().isoformat(timespec='seconds')}] {text}", flush=True)


def main(argv) -> int:
    name, cmd = argv[1], argv[argv.index("--") + 1:]
    (HERE / "search-logs").mkdir(exist_ok=True)
    attempt = 0
    while True:
        attempt += 1
        note(f"{name}: attempt {attempt}: {' '.join(cmd)}")
        with (HERE / "search-logs" / f"{name}.attempt-{attempt}.txt").open("w") as f:
            code = subprocess.run(cmd, cwd=HERE, stdout=f, stderr=subprocess.STDOUT).returncode
        if code == 0:
            note(f"{name}: done")
            return 0
        refused = refused_logs()
        if not refused:
            note(f"{name}: exit {code}, not a census refusal: stop")
            return code
        for f in refused:
            note(f"{name}: census refused; set aside {set_aside(f).name}")
        wait = 60
        while not census_passes():
            time.sleep(wait)
            wait = min(wait * 2, 600)
        note(f"{name}: the census passes again")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
