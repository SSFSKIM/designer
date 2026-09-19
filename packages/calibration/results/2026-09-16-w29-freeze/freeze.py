#!/usr/bin/env python3
"""The 26.5 freeze — W29 acceptance clause 1, contract X1.

`python3 freeze.py write` records SHA-256 over every byte of 26.5 evidence: the six
`apple-macos-26.5-*` fixture directories and `backgrounds/`, the fixtures manifest, the
26.5 material profile documents, and every 26.5-keyed row of the canonical matrix (each
row serialised canonically — sorted keys, no whitespace — and hashed on its own, so a
27 row appended beside them changes nothing here). `python3 freeze.py verify` re-derives
the same list and exits non-zero on any difference, naming it. Run at every W29 merge.

**Amended 2026-09-19 (W29 G1 Part B, claims §5.150).** `fixtures/manifest.json` was hashed
as ONE FILE, and that was right while the bundle held one bed. It stopped being right the
moment clause 2's 27 profiles were published, because the manifest is the file their
entries have to go in: a whole-file hash cannot tell "the 26.5 bed moved" from "a second
bed was added beside it", and after publication it can only ever report the first. It is
now decomposed the way the matrix already was — one hash per unit: each 26.5 profile
entry, each top-level block, each `backgrounds` index pair and each `bedProvenance` block,
serialised canonically and hashed on its own. A 27 entry appended beside them changes
nothing here; a 26.5 entry that moves, or a provenance block that is dropped or rewritten,
still fires. That is strictly what X1 asks, and it is what a whole-file hash could no
longer say.

The superseded reading is recorded rather than discarded: the manifest's whole-file
SHA-256 immediately before the 27 bed was published was
`e17fd7dba402a91791c166137e716d535ff9b8d34c0e55afedb6ba4a8c0cf9ac`, and
`results/2026-09-18-w29-g1-bed/manifest-before.json` is the structural snapshot it came
from. `manifest-delta.py verify` beside that snapshot proves the same thing independently
of this file, by classifying every difference rather than by hashing.
"""
import hashlib, json, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parents[4]
HERE = pathlib.Path(__file__).resolve().parent
FIX = ROOT / "apps/reference-apple/fixtures"
PROFILES = ROOT / "packages/calibration/profiles"
MATRIX = ROOT / "packages/calibration/results/matrix.json"
OUT = HERE / "sha256.txt"


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def canon(obj) -> bytes:
    """One JSON value, serialised so that only its content decides its hash."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()


def manifest_entries():
    """The bundle manifest, per unit rather than whole-file — see the module docstring.

    Every unit that describes the 26.5 bed is hashed on its own, and nothing that
    describes another bed is hashed at all. The units are the ones the file actually
    has: its top-level blocks, its profile entries, its background index pairs and
    its publication records.
    """
    m = json.loads((FIX / "manifest.json").read_text())
    for key in sorted(k for k in m if k not in ("profiles", "bedProvenance", "backgrounds")):
        yield f"{sha(canon(m[key]))}  manifest:{key}"
    # The index pair, not the map: an id added for a bed captured later changes
    # nothing, and an id RE-POINTED at another raster still fires — which is the
    # thing that would misattribute the fixtures already filed under it.
    for bid in sorted(m.get("backgrounds") or {}):
        yield f"{sha(canon([bid, m['backgrounds'][bid]]))}  manifest:background:{bid}"
    for p in sorted(m["profiles"], key=lambda p: p["profileKey"]):
        if not p["profileKey"].startswith("apple-macos-26.5-"):
            continue
        yield f"{sha(canon(p))}  manifest:profile:{p['profileKey']}"
    # Publication records, and only the ones that published 26.5 cells. Hashed by
    # content and sorted rather than by position, so a block appended for another
    # bed changes nothing and a 26.5 block that is dropped or rewritten fires —
    # the supersede rule inside `materialize` can rewrite one, which is exactly
    # the event this has to be able to see. A block names its profiles, so which
    # bed it belongs to is read from the record rather than assumed.
    blocks = [b for b in (m.get("bedProvenance") or [])
              if all(str(p).startswith("apple-macos-26.5-") for p in (b.get("profiles") or []))
              and (b.get("profiles") or [])]
    for digest in sorted(sha(canon(b)) for b in blocks):
        yield f"{digest}  manifest:bedProvenance:26.5"


def entries():
    files = []
    for d in sorted(FIX.glob("apple-macos-26.5-*")):
        files += sorted(p for p in d.rglob("*") if p.is_file())
    files += sorted(p for p in (FIX / "backgrounds").rglob("*") if p.is_file())
    files += sorted(PROFILES.glob("apple-macos-26.5*"))
    for f in files:
        yield f"{sha(f.read_bytes())}  {f.relative_to(ROOT)}"
    yield from manifest_entries()
    rows = json.loads(MATRIX.read_text())
    cells = rows["cells"] if isinstance(rows, dict) and "cells" in rows else rows
    n = 0
    for c in cells:
        key = c.get("key", c)
        pk = key.get("profileKey") if isinstance(key, dict) else None
        if pk is None:
            pk = c.get("profileKey")
        if not (isinstance(pk, str) and pk.startswith("apple-macos-26.5-")):
            continue
        n += 1
        canon = json.dumps(c, sort_keys=True, separators=(",", ":")).encode()
        yield f"{sha(canon)}  matrix-row:{pk}:{key.get('sceneId') if isinstance(key, dict) else c.get('sceneId')}:{n}"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "verify"
    lines = list(entries())
    if mode == "write":
        OUT.write_text("\n".join(lines) + "\n")
        print(f"wrote {len(lines)} entries to {OUT.relative_to(ROOT)}")
        return 0
    want = OUT.read_text().splitlines()
    if want == lines:
        print(f"26.5 freeze intact: {len(lines)} entries")
        return 0
    ws, ls = set(want), set(lines)
    for m in sorted(ws - ls)[:20]:
        print("MISSING/CHANGED:", m)
    for a in sorted(ls - ws)[:20]:
        print("NEW/CHANGED:    ", a)
    print(f"FROZEN 26.5 EVIDENCE DIFFERS: recorded {len(want)}, now {len(lines)}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
