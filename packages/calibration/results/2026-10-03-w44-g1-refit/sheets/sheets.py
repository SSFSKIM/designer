#!/usr/bin/env python3.12
"""W44 G1 (charter clause 10): native | vitrea c05 | vitrea candidate | difference eye sheets.

At the gate (step 6) over every T1 cell the light stage holds (both scales, both poses, both tiers;
the referees and the holdout are not read before the exposure); at the publication (step 8) over
the whole light bed (`--whole`: every declared light scene, holdout and referees included, read
after the exposure). Each row is

  Apple 0.25 (fixture) | vitrea c05 (published) | vitrea W44 (stage) |
  |W44 - Apple| x4 | |c05 - Apple| x4 | |W44 - c05| x4

cropped to the component's declared box plus 24 CSS px (W43's crop), 1x cells shown at 2x pixel
size, labelled with the cell's role, pose, stratum and T1's numbers (native, c05, W44 web SD and
the fidelity / change states; a T cell's T1-fine and T1-low states from the gate cut when given).

Before any pixel is read, every capture's cell JSON must name its row's `capturePath`, `sceneId`
and `renderer` (the per-cell assertion that a capture names the documents it was drawn with, W31):
the stage's rows the frozen light documents, the c05 rows the published c05 documents. A mismatch
refuses the whole run. Reads only; writes PNGs and index.html under --out.

    python3.12 -B sheets.py --stage MATRIX --stage-captures TREE --out DIR [--cut CUTS.json] [--whole]
"""
from __future__ import annotations

import argparse
import html
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402
import t1  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "w43_sheets", B.RESULTS / "2026-10-02-w43-g3-refit" / "sheets" / "sheets.py")
W43 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(W43)
crop_box, rgb, FIXTURES = W43.crop_box, W43.rgb, W43.FIXTURES

CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
LIGHT = ("apple-macos-27.0-1x-light-standard-glass0.25", "apple-macos-27.0-2x-light-standard-glass0.25")
COLUMNS = ("Apple 0.25", "vitrea c05", "vitrea W44", "|W44 - Apple| x4", "|c05 - Apple| x4", "|W44 - c05| x4")
LABEL_W = 420
FONT = ImageFont.load_default(size=14)
SMALL = ImageFont.load_default(size=12)


def checked_png(tree: Path, row: dict) -> Path:
    key = row["key"]
    folder = tree / key["profileKey"] / key["sceneId"]
    cell = json.loads((folder / f"cell__{key['web']['renderer']}.json").read_bytes())
    for field in ("capturePath", "sceneId", "renderer"):
        if cell.get(field) != key["web"][field]:
            raise SystemExit(f"{folder}: {field} {cell.get(field)!r} is not the row's {key['web'][field]!r}")
    return folder / f"{key['sceneId']}__{key['web']['renderer']}.png"


def diff(a, b):
    return np.clip(np.abs(a.astype(int) - b.astype(int)) * 4, 0, 255).astype(np.uint8)


def tile(img: np.ndarray, scale: int) -> np.ndarray:
    if scale == 1:
        img = np.repeat(np.repeat(img, 2, axis=0), 2, axis=1)
    return img


def label_image(lines, height):
    im = Image.new("RGB", (LABEL_W, height), (30, 30, 30))
    d = ImageDraw.Draw(im)
    for i, (text, colour) in enumerate(lines):
        d.text((8, 6 + 17 * i), text, fill=colour, font=FONT if i == 0 else SMALL)
    return np.asarray(im)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, type=Path)
    ap.add_argument("--stage-captures", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--cut", type=Path, help="the gate's cuts.json, for T1's states per cell")
    ap.add_argument("--whole", action="store_true", help="every declared light scene (after the exposure)")
    ap.add_argument("--rows", type=int, default=24)
    args = ap.parse_args()
    stage = [r for r in json.loads(args.stage.read_bytes())["cells"] if r["key"]["profileKey"] in LIGHT]
    c05 = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r
           for r in B.load_published("6d18c059eb42").rows}
    held = B.referee_plan.referee_cells(B.referee_plan.load_manifest())
    states = {}
    if args.cut:
        cut = json.loads(args.cut.read_bytes())
        for c in cut["T1"]["cells"]:
            states[(c["profile"], c["tier"], c["scene"])] = c
    rows = []
    for r in stage:
        p, tier, sid = r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]
        is_t1 = B.SCENES.by_id[sid]["background"] in t1.T1_BACKDROPS
        part = t1.partition(p, sid, held) if is_t1 else ("holdout" if B.SCENES.role[sid] == "holdout" else "gate")
        if not args.whole and (not is_t1 or part != "gate"):
            continue
        rows.append((t1.stratum(sid) if is_t1 else "-", B.scale_of(p), tier, t1.pose(sid), sid, p, r, part))
    rows.sort(key=lambda x: (x[0], x[2], x[1], x[3], x[4]))
    # The per-cell assertion first, for every capture, before any pixel is read.
    paths = []
    for stratum, scale, tier, pose, sid, p, r, part in rows:
        twin = c05.get((p, tier, sid))
        if twin is None:
            raise SystemExit(f"{p} {tier} {sid}: no c05 row")
        paths.append((checked_png(args.stage_captures, r), checked_png(CANONICAL, twin)))
    args.out.mkdir(parents=True, exist_ok=True)
    pages, page, page_rows, index = [], [], 0, []
    groups = {}
    for item, (mine, theirs) in zip(rows, paths):
        groups.setdefault(item[:4], []).append((item, mine, theirs))
    for (stratum, scale, tier, pose), items in groups.items():
        for start in range(0, len(items), args.rows):
            chunk = items[start:start + args.rows]
            strips = []
            for (stratum, scale, tier, pose, sid, p, r, part), mine, theirs in chunk:
                n = rgb(FIXTURES / p / f"{sid}.png")
                k = rgb(mine)
                c = rgb(theirs)
                x0, y0, x1, y1 = crop_box(sid, scale, n.shape)
                crops = [x[y0:y1, x0:x1] for x in (n, c, k)]
                images = crops + [diff(crops[2], crops[0]), diff(crops[1], crops[0]), diff(crops[2], crops[1])]
                images = [tile(x, scale) for x in images]
                h = images[0].shape[0]
                s = states.get((p, tier, sid))
                lines = [(f"{scale}x {tier} {sid}", (240, 240, 240)),
                         (f"{part} / {B.SCENES.role[sid]} / {pose} / stratum {stratum}", (180, 200, 255))]
                if s is not None:
                    lines.append((f"T1 n {s['native']:.4f} c05 {s['reference']:.4f} W44 {s['candidate']:.4f}  "
                                  f"{s['fidelity']}/{s['change']}", (230, 230, 160)))
                    for band in ("fine", "low"):
                        if "bands" in s:
                            b = s["bands"][band]
                            lines.append((f"T1-{band} n {b['native']:.4f} c05 {b['reference']:.4f} W44 "
                                          f"{b['candidate']:.4f}  {b['fidelity']}/{b['change']}", (200, 230, 200)))
                strip = np.concatenate([label_image(lines, h)] + [np.pad(x, ((0, 0), (2, 2), (0, 0)))
                                                                  for x in images], axis=1)
                strips.append(strip)
            width = max(x.shape[1] for x in strips)
            strips = [np.pad(x, ((0, 4), (0, width - x.shape[1]), (0, 0))) for x in strips]
            header = Image.new("RGB", (width, 24), (10, 10, 10))
            d = ImageDraw.Draw(header)
            d.text((8, 4), f"W44 G1 sheets: stratum {stratum}, {scale}x, {tier}, {pose}   columns: "
                   + " | ".join(COLUMNS), fill=(255, 255, 255), font=FONT)
            name = f"{stratum}-{scale}x-{tier}-{pose}-{start // args.rows + 1}.png"
            Image.fromarray(np.concatenate([np.asarray(header)] + strips, axis=0)).save(args.out / name)
            index.append((name, len(chunk)))
    with (args.out / "index.html").open("w") as f:
        f.write("<html><body><h1>W44 G1 eye sheets</h1><p>Columns: " + html.escape(" | ".join(COLUMNS)) + "</p>")
        for name, n in index:
            f.write(f'<h2>{html.escape(name)} ({n} cells)</h2><img src="{html.escape(name)}"><br>')
        f.write("</body></html>\n")
    print(json.dumps(dict(pages=len(index), cells=len(rows), out=str(args.out))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
