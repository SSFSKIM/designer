#!/usr/bin/env python3
"""The 26.5 freeze — W29 acceptance clause 1, contract X1.

`python3 freeze.py write` records SHA-256 over every byte of 26.5 evidence: the six
`apple-macos-26.5-*` fixture directories and `backgrounds/`, the fixtures manifest, the
26.5 material profile documents, and every 26.5-keyed row of the canonical matrix (each
row serialised canonically — sorted keys, no whitespace — and hashed on its own, so a
27 row appended beside them changes nothing here). `python3 freeze.py verify` re-derives
the same list and exits non-zero on any difference, naming it. Run at every W29 merge.
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


def entries():
    files = []
    for d in sorted(FIX.glob("apple-macos-26.5-*")):
        files += sorted(p for p in d.rglob("*") if p.is_file())
    files += sorted(p for p in (FIX / "backgrounds").rglob("*") if p.is_file())
    files.append(FIX / "manifest.json")
    files += sorted(PROFILES.glob("apple-macos-26.5*"))
    for f in files:
        yield f"{sha(f.read_bytes())}  {f.relative_to(ROOT)}"
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
