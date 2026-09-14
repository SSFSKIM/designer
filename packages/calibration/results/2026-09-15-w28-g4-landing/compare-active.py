"""The active half of the seam proof: every re-captured active PNG against the canonical one.

`active-sample.sh` re-runs the ordinary `compare` pipeline over the six scenes every
profile's canonical capture directory holds, on both tiers, into a scratch root. This
walks that root and compares each PNG, byte for byte, with the file of the same name
under the canonical `web-captures/` on this machine — the tree the committed matrix's
rows were measured from.

An absent canonical counterpart is reported as absent and never as a pass.

    python3 compare-active.py <scratch-capture-root> <canonical-web-captures>
"""
import hashlib
import json
import pathlib
import sys

scratch = pathlib.Path(sys.argv[1]).resolve()
canonical = pathlib.Path(sys.argv[2]).resolve()

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

rows = []
for png in sorted(scratch.rglob("*.png")):
    relative = png.relative_to(scratch)
    twin = canonical / relative
    rows.append({
        "path": str(relative),
        "canonicalPresent": twin.exists(),
        "sha256": sha(png),
        "canonicalSha256": sha(twin) if twin.exists() else None,
        "identical": twin.exists() and sha(twin) == sha(png),
    })

identical = [r for r in rows if r["identical"]]
absent = [r for r in rows if not r["canonicalPresent"]]
differing = [r for r in rows if r["canonicalPresent"] and not r["identical"]]

report = {
    "gate": "W28 G4 — the calibration seam, active pose",
    "claims": "§5.148",
    "scratchRoot": str(scratch),
    "canonicalRoot": str(canonical),
    "captures": len(rows),
    "identical": len(identical),
    "absentFromCanonical": [r["path"] for r in absent],
    "differing": [
        {"path": r["path"], "observed": r["sha256"], "canonical": r["canonicalSha256"]}
        for r in differing
    ],
    "rows": rows,
}
out = pathlib.Path(__file__).with_name("active-sample.json")
if out.exists():
    raise SystemExit(f"{out} exists; refusing to overwrite evidence")
out.write_text(json.dumps(report, indent=2) + "\n")
print(f"{len(identical)} / {len(rows)} byte-identical; {len(absent)} absent from canonical")
if differing:
    for r in differing:
        print(f"  DIFFERS {r['path']}")
    raise SystemExit(1)
