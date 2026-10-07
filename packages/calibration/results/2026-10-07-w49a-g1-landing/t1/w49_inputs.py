"""W49a landing inputs. Identity is the active/receded pair, including on historical reads.

The active document is unchanged, so an unqualified active-hash lookup is ambiguous after
publication. Readers below check the immutable file and both document hashes, not its alias.
No function renders, publishes, or writes a capture tree.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
RESULTS = CAL / "results"
PAIR = ("b2d074d2df24", "940384c06f73")
GENERATION = "-".join(PAIR)
REFERENCES = {"b2d074d2df24": ("b2d074d2df24", "29da6a888a23"),
              "d0219cd684bf": ("d0219cd684bf", "f0b36a71772a")}
CLAUSE = re.compile(r"(materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})")


# DL2 (a)/(b) and DL9: the opacity repair/flattered cells retain the pre-opacity reference.
D0219_SCENES = {f"{bg}__rrect-lg__inactive" for bg in
                ("checkerboard-64", "checkerboard-32", "photo", "hc-text", "impulse", "checkerboard-8")}
# DL2/DL5: the eleven W48 authorisations keep their original reference and ruling.
CARRIED_COMMON = {"checkerboard-32__rrect-lg__rest", "checkerboard-lc16__rrect-md__rest",
                  "checkerboard-64__rrect-lg__rest", "hc-text-28__rrect-lg__rest"}
CARRIED_BY_SCALE = {1: {"impulse__capsule-button__rest"},
                    2: {"checkerboard__capsule-button__inactive",
                        "checkerboard__capsule-button__inactive-tint-orange"}}


def selected_reference(profile: str, scene: str) -> str:
    scale = 2 if "-2x-" in profile else 1
    return ("d0219cd684bf" if scene in D0219_SCENES | CARRIED_COMMON | CARRIED_BY_SCALE[scale]
            else "b2d074d2df24")


def capture_pair(path: str) -> tuple[str, str]:
    clauses = CLAUSE.findall(path)
    if len(clauses) != 2 or {c[0] for c in clauses} != {"materialProfile", "recededProfile"}:
        raise ValueError(f"capture must name exactly one active and one receded document: {path}")
    named = {kind: sha for kind, _, sha in clauses}
    return named["materialProfile"], named["recededProfile"]


def require_pair(path: str, pair: tuple[str, str]) -> None:
    if capture_pair(path) != pair:
        raise ValueError(f"capture names {capture_pair(path)}, expected {pair}")


def cuts():
    sys.path.insert(0, str(RESULTS / "2026-10-06-w48-g0-declaration"))
    import inherit
    return inherit.tool("cuts/cuts.py")


def published(generation: str, pair: tuple[str, str]) -> list:
    index = json.loads((RESULTS / "generations/index.json").read_text())
    name = f"{generation}.json"
    raw = (RESULTS / "generations" / name).read_bytes()
    if hashlib.sha256(raw).hexdigest() != index["files"][name]["sha256"]:
        raise ValueError(f"{name}: file differs from generation index")
    rows = json.loads(raw)["cells"]
    if len(rows) != index["files"][name]["rowCount"]:
        raise ValueError(f"{name}: row count differs from generation index")
    for row in rows:
        require_pair(row["key"]["web"]["capturePath"], pair)
    return rows


def row_key(row: dict) -> tuple[str, str, str]:
    key = row["key"]
    return key["profileKey"], key["web"]["renderer"], key["sceneId"]


def stage_rows(stage: Path) -> list:
    body = json.loads((stage / "matrix.json").read_text())
    if body.get("schemaVersion") != 5:
        raise ValueError("stage is not schema 5")
    rows = body["cells"]
    for row in rows:
        require_pair(row["key"]["web"]["capturePath"], PAIR)
    expected = {row_key(r) for r in published("b2d074d2df24", REFERENCES["b2d074d2df24"])}
    actual = [row_key(r) for r in rows]
    if len(actual) != len(set(actual)) or set(actual) != expected:
        raise ValueError(f"stage incomplete or duplicated: {len(actual)} rows, expected {len(expected)}; "
                         f"missing {sorted(expected - set(actual))}, extra {sorted(set(actual) - expected)}")
    return rows


def band_fixture(path: Path, pair: tuple[str, str]) -> dict:
    body = json.loads(path.read_text())
    out = {}
    for entry in body["entries"]:
        require_pair(entry["capturePath"], pair)
        key = (entry["profile"], entry["renderer"], entry["scene"], entry["capturePath"])
        if key in out:
            raise ValueError(f"duplicate band entry: {key}")
        out[key] = entry
    return out
