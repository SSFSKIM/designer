#!/usr/bin/env python3.12
"""W47 G0 (g): run `ladder.py render [LABEL...]` to completion across census refusals (charter clause 5; the
census of §5.201 §21, which refuses a launch while another session's browser automation is up).

W46 G1's `fit/drive.py` form, for the ladder driver. `ladder.py render` stops at the first non-zero launch
and resumes where it stopped (a launch recorded exit 0 in `runs.jsonl` is never repeated; a repeated launch
gets a `.relaunch-<n>` log, so a refused launch's log is kept as evidence). On a census refusal (the launch
log's first line `census <label>: REFUSES`, which `with-gpu.sh` writes before it exits 1 without launching)
this driver waits with backoff (60 s doubling to 600 s), notes it in `drive.jsonl`, and reruns. Any other
failure stops it with that exit code. The census is never bypassed.

    python3.12 -B drive.py [LABEL...]
"""
from __future__ import annotations

import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
LOGS = HERE / "logs"


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")


def note(row: dict) -> None:
    with (HERE / "drive.jsonl").open("a") as f:
        f.write(json.dumps(dict(row, at=now())) + "\n")
    print(json.dumps(row), flush=True)


def last_log() -> Path | None:
    logs = sorted(LOGS.glob("*.txt"), key=lambda p: p.stat().st_mtime) if LOGS.exists() else []
    return logs[-1] if logs else None


def refused(log: Path | None) -> bool:
    if log is None:
        return False
    first = log.read_text().splitlines()[:1]
    return bool(first) and first[0].startswith("census ") and ": REFUSES" in first[0]


def main(labels: list[str]) -> int:
    wait = 60
    note(dict(event="start", labels=labels))
    while True:
        rc = subprocess.run([sys.executable, "-B", str(HERE / "ladder.py"), "render", *labels], cwd=HERE).returncode
        if rc == 0:
            note(dict(event="done", exitCode=0))
            return 0
        log = last_log()
        if not refused(log):
            note(dict(event="stopped", exitCode=rc, log=None if log is None else log.name))
            return rc
        note(dict(event="census refused", log=log.name, census=log.read_text().splitlines()[0], waitSeconds=wait))
        time.sleep(wait)
        wait = min(wait * 2, 600)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
