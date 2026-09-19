#!/usr/bin/env python3
"""W29 G3b — the field diff of a profile document against the one it supersedes.

    python3 document-diff.py > document-diff.txt

Decision Log 6 (a) says "no other constant moves in this part; say so and prove
it with a field diff of the documents". This is that proof, and it is a script
rather than a paragraph because a paragraph is a claim and a leaf-by-leaf diff is
a reading.

Two comparisons, both against something already committed:

  * each 27 ACTIVE document against the 26.5 document it supersedes, which is the
    whole of what vitrea's 27 material differs by — G3's refit plus this child's
    shadow;
  * each 27 active document against its own state at G3's seal, taken from git,
    which is this child's contribution alone and is the one the Decision Log
    asks about.

The receded documents are diffed against the shipped 26.5 endpoint they
supersede, which is their own equivalent of the first comparison.
"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROFILES = HERE.parent.parent / "profiles"
REPO = HERE.parents[3]

# The commit G3's documents were sealed at — the merge that closed it.
G3_SEAL = "b2a42bde"


def leaves(value, prefix=""):
    if isinstance(value, dict):
        for key in sorted(value):
            yield from leaves(value[key], f"{prefix}.{key}" if prefix else key)
    else:
        yield prefix, value


def diff(before: dict, after: dict) -> list[tuple[str, object, object]]:
    a = dict(leaves(before))
    b = dict(leaves(after))
    out = []
    for key in sorted(set(a) | set(b)):
        if a.get(key, "(absent)") != b.get(key, "(absent)"):
            out.append((key, a.get(key, "(absent)"), b.get(key, "(absent)")))
    return out


def load(name: str) -> dict:
    return json.loads((PROFILES / f"{name}.json").read_text())


def at_commit(name: str, commit: str) -> dict | None:
    rel = f"packages/calibration/profiles/{name}.json"
    got = subprocess.run(
        ["git", "-C", str(REPO), "show", f"{commit}:{rel}"], capture_output=True, text=True
    )
    return json.loads(got.stdout) if got.returncode == 0 else None


def report(title: str, before: dict | None, after: dict, section: str = "patch") -> None:
    print(f"\n── {title} ──")
    if before is None:
        print("   (no counterpart on record — this document is new in this child)")
        return
    rows = diff(before.get(section, {}), after.get(section, {}))
    if not rows:
        print("   no leaf differs")
    for key, was, now in rows:
        print(f"   {key:<44} {json.dumps(was):>16}  ->  {json.dumps(now)}")
    mapping = diff(before.get("cssTierMapping", {}), after.get("cssTierMapping", {}))
    for key, was, now in mapping:
        print(f"   cssTierMapping.{key:<30} {json.dumps(was):>16}  ->  {json.dumps(now)}")


for scheme in ("light", "dark"):
    active = f"apple-macos-27.0-1x-{scheme}-standard-glass0.5"
    supersedes = f"apple-macos-26.5-1x-{scheme}-standard"
    report(f"{active}  against  {supersedes}", load(supersedes), load(active))
    report(
        f"{active}  against  its own state at G3's seal ({G3_SEAL})",
        at_commit(active, G3_SEAL),
        load(active),
    )

for scheme in ("light", "dark"):
    receded = f"apple-macos-27.0-1x-{scheme}-standard-glass0.5-receded"
    print(f"\n── {receded}  against  the shipped 26.5 endpoint ──")
    if not (PROFILES / f"{receded}.json").exists():
        print("   (not written yet)")
        continue
    shipped = json.loads(
        (
            HERE.parent / "2026-09-14-w28-g1-silhouette" / "fitted-endpoint.json"
        ).read_text()
    )["patch"][scheme]
    rows = diff(shipped, load(receded)["patch"])
    if not rows:
        print("   no leaf differs")
    for key, was, now in rows:
        print(f"   {key:<44} {json.dumps(was):>16}  ->  {json.dumps(now)}")
