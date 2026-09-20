#!/usr/bin/env python3
"""The split's classifier, exercised on shapes the bed does not contain — W30 G1 review.

`split-generation.py` decides two things per row: whether the row is CURRENT (every
material profile document it names is on disk at the bytes it records) and, when it is
not, which superseded file its generation lands in. The bed exercises exactly one of
those shapes — a whole generation, active document and all, superseded together — so
every other branch of the rule was prose until this ran.

Six cases, over synthetic matrices with the same envelope the canonical file has:

  current retained         a row naming only current documents stays in the working file
  superseded named         a row whose ACTIVE document moved lands in `<active>.json`
  receded-only compound    a row whose active document still ships and whose RECEDED
                           document moved lands in `<active>-<receded>.json`, which is
                           the one generation shape the plain rule cannot name
  index lookup complete    every document the moved rows name — active and receded —
                           is reachable, which is what makes finding a row a lookup
  third clause refused     a `capturePath` carrying a document hash the clause pattern
                           does not parse is refused rather than judged on the clauses
                           that happen to match
  no active refused        a superseded row naming a receded document and no active one
                           is refused: the file name is the index, and it would have none
  X1 held by the tool      a frozen macOS 26.5 row selected to move is refused before a
                           byte is written, whatever `--current` said

    python3 classifier-selftest.py            # output committed at classifier-selftest.txt
"""
import importlib.util
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location("split_generation", HERE / "split-generation.py")
_split = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_split)

LIGHT = "packages/calibration/profiles/light.json"
RECEDED = "packages/calibration/profiles/light-receded.json"
CSS = "packages/calibration/profiles/css-crossing.json"

# What is on disk in this fixture: the light document at `aaaa…`, its receded at `dddd…`.
CURRENT = {LIGHT: "a" * 12, RECEDED: "d" * 12}


def row(profile_key: str, scene: str, clauses: str) -> dict:
    """One matrix row in the shape the classifier reads, and nothing it does not."""
    return {
        "key": {
            "profileKey": profile_key,
            "sceneId": scene,
            "web": {"capturePath": f"web-captures/{scene}.png {clauses}"},
        },
        "tier": "texture",
        "fixtureSet": "calibration",
        "capturedAt": "2026-09-20T00:00:00.000Z",
    }


def matrix(rows: list) -> bytes:
    """The same envelope the canonical file carries, so `elements` walks a real shape."""
    return json.dumps({"schemaVersion": 5, "cells": rows}, indent=2).encode()


def classified(rows: list):
    raw = matrix(rows)
    _, spans, _ = _split.elements(raw)
    return raw, [_split.classify(raw, s, CURRENT) for s in spans]


def refuses(rows: list, through: str) -> str:
    """The refusal a shape draws, as a message; the empty string if it drew none."""
    try:
        raw, seen = classified(rows)
        if through == "classify":
            return ""
        _split.destinations(seen, CURRENT)
        return ""
    except ValueError as refusal:
        return str(refusal)


def main() -> int:
    results = []
    detail = []

    def check(clause: str, ok: bool, note: str) -> None:
        results.append((clause, ok))
        detail.append(f"  {clause}: {note}")

    # --- the three-row matrix: current, superseded active, receded-only superseded ----
    active_clause = f"materialProfile={LIGHT} sha256:"
    receded_clause = f"recededProfile={RECEDED} sha256:"
    three = [
        row("apple-macos-27.0-1x-light-standard", "current-scene",
            f"{active_clause}{'a' * 12}"),
        row("apple-macos-27.0-1x-light-standard", "superseded-active-scene",
            f"{active_clause}{'b' * 12}"),
        row("apple-macos-27.0-1x-light-standard", "receded-only-scene",
            f"{active_clause}{'a' * 12} {receded_clause}{'c' * 12}"),
    ]
    raw, seen = classified(three)
    keep_idx, dest = _split.destinations(seen, CURRENT)
    stems = {stem: [seen[i]["sceneId"] for i in group] for stem, group in dest.items()}

    check("current retained", keep_idx == [0] and seen[0]["current"] is True,
          f"retained {[seen[i]['sceneId'] for i in keep_idx]}")
    check("superseded named", stems.get("b" * 12) == ["superseded-active-scene"],
          f"{'b' * 12}.json holds {stems.get('b' * 12)}")
    compound = f"{'a' * 12}-{'c' * 12}"
    check("receded-only compound", stems.get(compound) == ["receded-only-scene"],
          f"{compound}.json holds {stems.get(compound)}")

    # The lookup the index is built from: every document a moved row names, active and
    # receded alike, reaching the file that holds it.
    lookup = {}
    for stem, group in dest.items():
        for i in group:
            for document in seen[i]["documents"]:
                lookup[document["sha256"]] = f"{stem}.json"
    check("index lookup complete",
          lookup == {"b" * 12: f"{'b' * 12}.json",
                     "a" * 12: f"{compound}.json",
                     "c" * 12: f"{compound}.json"},
          json.dumps(lookup, sort_keys=True))

    # --- the shapes that are refused ---------------------------------------------------
    third = refuses(
        [row("apple-macos-27.0-1x-light-standard", "third-clause-scene",
             f"{active_clause}{'a' * 12} {receded_clause}{'d' * 12} "
             f"crossingProfile={CSS} sha256:{'e' * 12}")],
        "classify")
    check("third clause refused", third.startswith("capturePath carries 3 document hashes"),
          third or "no refusal")

    no_active = refuses(
        [row("apple-macos-27.0-1x-light-standard", "receded-without-active-scene",
             f"{receded_clause}{'c' * 12}")],
        "destinations")
    check("no active refused", "names no active document" in no_active,
          no_active or "no refusal")

    frozen = refuses(
        [row("apple-macos-26.5-1x-light-standard", "frozen-scene",
             f"{active_clause}{'b' * 12}")],
        "destinations")
    check("X1 held by the tool", frozen.startswith("X1:"), frozen or "no refusal")

    width = max(len(clause) for clause, _ in results)
    for clause, ok in results:
        print(f"{clause.ljust(width)}  {'PASS' if ok else 'FAIL'}")
    print()
    print("what each case read:")
    for line in detail:
        print(line)
    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
