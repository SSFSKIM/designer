#!/usr/bin/env python3.12
"""W48 G0 (b): the shipped rung's identity re-proven from W47's committed record, with no render and no
pixel read (charter G0 (b): "the level check re-bound, the shipped rung's identity re-proven from W47's
committed records"; X61, X71).

W47 G0 rendered the shipped rung (the snapshots, no override) on every ladder (i) cell at both scales and
read it IDENTICAL to `d0219cd684bf` (`results/2026-10-06-w47-g0-operators/level/identity/identity.json`,
130 of 130, reading no change). That record names, per cell, the SHA-256 of the canonical capture and
alpha PNG its candidate's were compared with. W48 re-proves it against bytes it now holds by hash: every
canonical PNG hash in the record must equal the archive inventory's `reference/` entry for that cell
(`archive/inventory.json`, the `d0219cd684bf` subset copied from the canonical tree into
`w47-ladders-archive`), and the candidate's hash must equal it too. Nothing here reads a PNG.

    python3.12 -B identity_reproof.py      (writes identity-reproof.json and .txt beside it)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import inherit  # noqa: E402

W = inherit.W
RECORD = W.W47_G0 / "level" / "identity" / "identity.json"
INVENTORY = W.G0 / "archive" / "inventory.json"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reproof() -> dict:
    rec = json.loads(RECORD.read_text())
    inv = json.loads(INVENTORY.read_text())
    reference = {r["path"]: r["sha256"] for r in inv["reference"]}
    failures, checked = [], 0
    for cell in rec["perCell"]:
        profile, renderer, sid = cell["cell"].split(" ")
        if renderer != "webgpu":
            failures.append(f"{cell['cell']}: not a WebGPU cell")
            continue
        for key, suffix in (("png", ""), ("png__alpha", "__alpha")):
            path = f"reference/{profile}/{sid}/{sid}__webgpu{suffix}.png"
            want = reference.get(path)
            got = cell[key]
            if want is None:
                failures.append(f"{path}: not in the archive's reference subset")
            elif got["canonical"] != want or got["candidate"] != want:
                failures.append(f"{path}: record canonical {got['canonical'][:12]} / candidate "
                                f"{got['candidate'][:12]}, archive {want[:12]}")
            checked += 1
    ok = (rec["verdict"] == "IDENTICAL" and rec["cells"] == rec["pixelAndMeasurementIdentical"] == 130
          and rec["failures"] == [] and rec["readsNoChange"] is True and not failures and checked == 260)
    return dict(
        what="W48 G0 (b): the shipped rung's identity (W47 G0's level/identity record) re-proven against the "
             "archive's d0219cd684bf reference subset by hash; no render, no pixel read",
        record=dict(path=str(RECORD.relative_to(W.ROOT)), sha256=sha(RECORD), verdict=rec["verdict"],
                    cells=rec["cells"], identical=rec["pixelAndMeasurementIdentical"],
                    readsNoChange=rec["readsNoChange"], failures=len(rec["failures"])),
        inventory=dict(path=str(INVENTORY.relative_to(W.ROOT)), sha256=sha(INVENTORY), referenceEntries=len(reference)),
        pngsChecked=checked, failures=failures, verdict="REPRODUCED" if ok else "DIFFERS")


if __name__ == "__main__":
    out = reproof()
    (HERE / "identity-reproof.json").write_text(json.dumps(out, indent=1) + "\n")
    text = (f"{out['what']}\nrecord {out['record']['path']} ({out['record']['sha256'][:12]}): {out['record']['verdict']} "
            f"{out['record']['identical']}/{out['record']['cells']}, readsNoChange {out['record']['readsNoChange']}\n"
            f"archive inventory {out['inventory']['sha256'][:12]} ({out['inventory']['referenceEntries']} reference "
            f"entries): {out['pngsChecked']} PNG hashes checked, {len(out['failures'])} differ\n"
            f"VERDICT {out['verdict']}\n")
    (HERE / "identity-reproof.txt").write_text(text)
    print(text, end="")
    sys.exit(0 if out["verdict"] == "REPRODUCED" else 1)
