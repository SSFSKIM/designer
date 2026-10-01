"""W43 G2 (1): the null pairs the declared bar is rehearsed on before any 0.25 pair is read.

Every G1a bridge capture is a 0.5 capture through the W39 side bundle on the night of the 0.25 bed
(§5.199 §4). Read against its canonical 0.5 fixture (the original bundle, 2026-09-18/19), each is
a pair whose true slider change is zero: what the declared bar calls "moved" on it is what the bar
would misread as Apple's slider change, from the bundle, the night and (for the sentinels) the
capture protocol alone.

- the 72 canonical bridge captures (six cells per pass, three runs, the bed's own protocol);
- the W42 sentinels (long protocol) whose cell has a canonical twin: the checker-64 on rrect-lg in
  all eight endpoints and the impulse on rrect-md in the light ones (G0 (b)'s twin mapping;
  the canonical dark profiles carry no impulse scene).

    python3.12 -B null-pairs.py [--g1a ~/vitrea-w43/g1a-run]   # writes rehearsal/null-pairs.json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
FIXTURES = REPO / "apps" / "reference-apple" / "fixtures"
RUN = re.compile(r"^run-(\d+)$")
SENTINEL_TWIN = {
    "f-checker64-rrect-lg__rest": "checkerboard-64__rrect-lg__rest",
    "f-checker64-rrect-lg__inactive": "checkerboard-64__rrect-lg__inactive",
    "f-impulse-rrect-md__rest": "impulse__rrect-md__rest",
    "f-impulse-rrect-md__inactive": "impulse__rrect-md__inactive",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--g1a", default=str(Path.home() / "vitrea-w43" / "g1a-run"))
    args = parser.parse_args()
    root = Path(args.g1a)
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    published = {(p["profileKey"], f["sceneId"]) for p in manifest["profiles"] for f in p["fixtures"]}
    pairs, skipped = [], []
    for pass_dir in sorted(root.iterdir()):
        name = pass_dir.name
        if not (name.startswith("open-") or name.startswith("close-")) or not pass_dir.is_dir():
            continue
        kind = "canonical" if name.startswith("open-canonical") else "sentinel"
        for run in sorted(d for d in pass_dir.iterdir() if d.is_dir() and RUN.match(d.name)):
            for profile in sorted(run.glob("apple-macos-27.0-*-glass0.5")):
                for png in sorted(profile.glob("*.png")):
                    scene = SENTINEL_TWIN.get(png.stem, png.stem) if kind == "sentinel" else png.stem
                    if (profile.name, scene) not in published:
                        skipped.append(f"{name}/{run.name}/{profile.name}/{png.stem}: no canonical twin")
                        continue
                    pairs.append(
                        {
                            "label": f"{kind}:{name}/{run.name}/{png.stem}",
                            "subjectImage": str(png),
                            "profileKey": profile.name,
                            "sceneId": scene,
                        }
                    )
    out = HERE / "rehearsal"
    out.mkdir(exist_ok=True)
    (out / "null-pairs.json").write_text(json.dumps(pairs, indent=1) + "\n")
    (out / "null-pairs-skipped.txt").write_text("\n".join(skipped) + "\n")
    print(f"{len(pairs)} null pairs ({sum(p['label'].startswith('canonical') for p in pairs)} canonical), "
          f"{len(skipped)} captures with no canonical twin")


if __name__ == "__main__":
    main()
