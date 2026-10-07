#!/usr/bin/env python3.12
"""W45 G2 (claims §5.207): the capture tree a landing copies is the read the published rows were
measured off, cell by cell, and the copy is byte-for-byte that tree.

    python3.12 -B witness.py --generation FILE --tree DIR [--copy DIR] --out FILE

For every row of the generation file: the capture directory exists, its `cell__<renderer>.json`
equals the row's `key.web` field for field, and its `report.cell__<renderer>.json` (the row as the
compare launch wrote it beside the capture) equals the published row in full, `capturedAt` and
every metric included; the capture's own `report__<renderer>.json` precedes that `capturedAt`. A
capture from an earlier or later launch at the same document bytes is told apart that way, which
a document-hash compare cannot do. With --copy, every file under the generation's profile directories in TREE has a
byte-identical twin under COPY and COPY holds no other file there.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--generation", type=Path, required=True)
    ap.add_argument("--tree", type=Path, required=True)
    ap.add_argument("--copy", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()
    cells = json.loads(a.generation.read_text())["cells"]
    bad: list[str] = []
    profiles = set()
    for row in cells:
        key = row["key"]
        profile, scene, web = key["profileKey"], key["sceneId"], key["web"]
        renderer = web["renderer"]
        profiles.add(profile)
        d = a.tree / profile / scene
        desc, report = d / f"cell__{renderer}.json", d / f"report__{renderer}.json"
        written = d / f"report.cell__{renderer}.json"
        if not desc.exists() or not report.exists() or not written.exists():
            bad.append(f"{profile} {renderer} {scene}: no capture")
            continue
        if json.loads(desc.read_text()) != web:
            bad.append(f"{profile} {renderer} {scene}: descriptor differs from the row's key.web")
        if json.loads(written.read_text()) != row:
            bad.append(f"{profile} {renderer} {scene}: the row written beside the capture is not the published row")
        got = json.loads(report.read_text()).get("capturedAt")
        if not got or got > row["capturedAt"]:
            bad.append(f"{profile} {renderer} {scene}: capture {got} does not precede row {row['capturedAt']}")
    files = copied = 0
    if a.copy is not None:
        for profile in sorted(profiles):
            src = {p.relative_to(a.tree): p for p in (a.tree / profile).rglob("*") if p.is_file()}
            dst = {p.relative_to(a.copy): p for p in (a.copy / profile).rglob("*") if p.is_file()}
            files += len(src)
            if set(src) != set(dst):
                bad.append(f"{profile}: file sets differ ({len(set(src) ^ set(dst))} paths)")
            for rel in sorted(set(src) & set(dst)):
                if sha(src[rel]) != sha(dst[rel]):
                    bad.append(f"{rel}: bytes differ")
                else:
                    copied += 1
    record = dict(generation=str(a.generation), generationSha256=sha(a.generation), rows=len(cells),
                  tree=str(a.tree), copy=str(a.copy) if a.copy else None, profiles=sorted(profiles),
                  filesInTree=files, filesByteIdentical=copied, failures=bad)
    a.out.write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps({k: v for k, v in record.items() if k != "failures"}, indent=1))
    print(f"failures: {len(bad)}")
    for line in bad[:20]:
        print("  " + line)
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
