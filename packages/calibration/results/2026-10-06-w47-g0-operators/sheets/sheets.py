#!/usr/bin/env python3.12
"""W47 G0 (c): native | vitrea d0219cd684bf | vitrea W47 | difference eye sheets — W46 G0's
`sheets/sheets.py` (`results/2026-10-05-w46-g0-declaration/sheets/sheets.py`) ported by copy for W47
(charter clause 10, "By eye"; Design "The populations per phase", MARKED: W46's verbatim). W46's
committed copy is untouched.

What the port changes, and nothing else: W47's bindings (W44's, W45's and W46's stages, scratch and
evidence refused as an input or output); the withheld dark cells through W47's X69 loader
(`w46-referees-1` by hash, and the dark holdout); `--whole` waits on a committed ledger read
witnessing that manifest (read 8); the columns name W47. The populations per phase are W46's:
before the exposure only the non-withheld dark rows draw (a dark referee or holdout row refuses the
run), a light withheld row refuses always, the whole bed after the exposure. Gain ×16, printed.

W46 G0's text follows, unchanged; where it says W46 it is W47.

W46 G0 (a): native | vitrea d0219cd684bf | vitrea W46 | difference eye sheets — W45 G0's
`sheets/sheets.py` (`results/2026-10-03-w45-g0-operator/sheets/sheets.py`) ported for W46 (charter
clause 10; Design "The populations per phase", MARKED; Risks "The dark sheets are hard to read by
eye"). W45's committed copy is untouched.

What the port changes, and nothing else:
  - **The dark pair, against `d0219cd684bf`.** Each row is

      Apple 0.25 (fixture) | vitrea d0219cd684bf (published) | vitrea W46 (stage or candidate) |
      |W46 - Apple| xG | |d0219 - Apple| xG | |W46 - d0219| xG

    over the DARK 0.25 rows of the matrix given (a G1 stage, or a candidate's scratch matrix); light
    rows are X60's (`stage/x60.py`) and are not drawn. The native | candidate pair is shown at native
    gamma (the sRGB bytes as captured); the three difference panels are GAIN-LIFTED, G = 16 on the dark
    scheme (4 on the light, W45's), and the gain is printed in every page header and column name.
  - **The populations per phase are enforced, not assumed.** Before the exposure a row of a withheld
    cell refuses the whole run: a dark referee (W46's manifest) or dark holdout cell, or ANY light
    withheld cell (the light holdout and W44's referees, spent at read 7 and never re-rendered).
    Before the exposure every non-withheld dark row is drawn (`--t1-only` keeps the T1 cells).
    `--whole` (the whole dark bed, withheld cells included) refuses unless the cross-gate ledger's last
    COMMITTED read witnesses W46's referee manifest — the exposure, read 8. A light withheld row
    refuses even then.
  - **W46's bindings.** W44's and W45's stages, scratch and evidence refuse as an input or output.

W45 G0's text follows, unchanged; where it says c05 it is `d0219cd684bf`, where it says light, dark.

W45 G0 (b): native | vitrea c05 | vitrea W45 | difference eye sheets — W44 G1's prepared
`sheets/sheets.py` ported for W45 (charter clause 10; X58). W44's committed copy is untouched.

At the gate (G1 step 6) over every T1 cell the light stage holds (both scales, both poses, both
tiers; the referees and the holdout are not read before the exposure); at the publication (step 8)
over the whole light bed (`--whole`, after the exposure). Each row is

  Apple 0.25 (fixture) | vitrea c05 (published) | vitrea W45 (stage) |
  |W45 - Apple| x4 | |c05 - Apple| x4 | |W45 - c05| x4

cropped to the component's declared box plus 24 CSS px (W43's crop, by path and pinned), 1x cells
shown at 2x pixel size, labelled with the cell's role, pose, stratum and T1's numbers (and a T
cell's T1-fine and T1-low states from the gate cut when given).

Before any pixel is read, every capture's cell JSON must name its row's `capturePath`, `sceneId`
and `renderer` (W31's per-cell assertion that a capture names the documents it was drawn with):
the stage's rows W45's frozen light documents, the c05 rows the published c05 documents. A
mismatch refuses the whole run. A stage, capture tree or output inside W44's evidence, scratch or
stage refuses (X58). A row of a referee or holdout cell refuses unless `--whole` (the exposure has
been read). Reads only; writes PNGs and index.html under --out.

    python3.12 -B sheets.py --stage MATRIX --stage-captures TREE --out DIR [--cut CUTS.json] [--whole]
        [--t1-only]
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import bindings as W  # noqa: E402

GAIN = {"dark": 16, "light": 4}
LABEL_W = 420
FONT = ImageFont.load_default(size=14)
SMALL = ImageFont.load_default(size=12)


def columns(gain: int) -> tuple[str, ...]:
    return ("Apple 0.25 (native gamma)", "vitrea d0219cd684bf", "vitrea W47", f"|W47 - Apple| x{gain}",
            f"|d0219 - Apple| x{gain}", f"|W47 - d0219| x{gain}")


def checked_png(tree: Path, row: dict) -> Path:
    key = row["key"]
    folder = tree / key["profileKey"] / key["sceneId"]
    cell = json.loads((folder / f"cell__{key['web']['renderer']}.json").read_bytes())
    for field in ("capturePath", "sceneId", "renderer"):
        if cell.get(field) != key["web"][field]:
            raise W.Refusal(f"{folder}: {field} {cell.get(field)!r} is not the row's {key['web'][field]!r}")
    return folder / f"{key['sceneId']}__{key['web']['renderer']}.png"


def diff(a, b, gain: int):
    return np.clip(np.abs(a.astype(int) - b.astype(int)) * gain, 0, 255).astype(np.uint8)


def tile(img: np.ndarray, scale: int) -> np.ndarray:
    return np.repeat(np.repeat(img, 2, axis=0), 2, axis=1) if scale == 1 else img


def label_image(lines, height):
    im = Image.new("RGB", (LABEL_W, height), (30, 30, 30))
    d = ImageDraw.Draw(im)
    for i, (text, colour) in enumerate(lines):
        d.text((8, 6 + 17 * i), text, fill=colour, font=FONT if i == 0 else SMALL)
    return np.asarray(im)


def exposure_read() -> bool:
    """Whether the cross-gate ledger's last COMMITTED read witnesses `w46-referees-1` (read 8)."""
    stage = W.load_module("w47_stage", HERE.parent / "stage" / "stage.py")
    last = stage.committed_last_read() or {}
    return (last.get("refereeManifest") or {}).get("sha256") == W.referees().load_manifest()["sha256"]


def select(stage_rows, B, t1, held, light_held, whole: bool, t1_only: bool = False):
    """(stratum, scale, tier, pose, scene, profile, row, partition) for every dark row the sheets draw.
    A withheld row refuses before the exposure; a light withheld row refuses always."""
    rows = []
    for r in stage_rows:
        p, tier, sid = r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]
        if (p, sid) in light_held:
            raise W.Refusal(f"{p} {tier} {sid}: a light withheld cell (holdout or W44 referee), spent at read 7 and "
                            "never re-rendered (X60)")
        if p not in W.DARK_025:
            continue
        is_t1 = B.SCENES.by_id[sid]["background"] in t1.T1_BACKDROPS
        part = ("referee" if (p, sid) in held else "holdout" if B.SCENES.role[sid] == "holdout" else "gate")
        if not whole and part != "gate":
            raise W.Refusal(f"{p} {tier} {sid}: a {part} row before --whole (the exposure)")
        if t1_only and not is_t1:
            continue
        rows.append((t1.stratum(sid) if is_t1 else "-", B.scale_of(p), tier, t1.pose(sid), sid, p, r, part))
    rows.sort(key=lambda x: (x[0], x[2], x[1], x[3], x[4]))
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", required=True, type=Path, help="a stage's or a candidate's matrix.json")
    ap.add_argument("--stage-captures", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--cut", type=Path, help="the cut's cuts.json, for T1's states per cell")
    ap.add_argument("--whole", action="store_true", help="the whole dark bed (only after the exposure, read 8)")
    ap.add_argument("--t1-only", action="store_true", help="draw the T1 cells only")
    ap.add_argument("--rows", type=int, default=24)
    args = ap.parse_args(argv)
    stage_matrix = W.refuse_other_wave_path(args.stage, "the stage")
    captures = W.refuse_other_wave_path(args.stage_captures, "the stage's captures")
    out_dir = W.refuse_other_wave_path(args.out, "the sheets' output")
    if args.whole and not exposure_read():
        raise W.Refusal("--whole: the ledger's last committed read does not witness w46-referees-1; the "
                        "whole dark bed is drawn only after the exposure (read 8)")
    B, t1, _ = W.load_cuts()
    # W43's helpers by path; its module puts W43's cuts on the path and imports `bed`, which is
    # already W47's in sys.modules — the path entry is taken back off so nothing else resolves there.
    w43 = W.load_module("w43_sheets", W.W43_SHEETS)
    w43_cuts = str(W.W43_SHEETS.parent.parent / "cuts")
    while w43_cuts in sys.path:
        sys.path.remove(w43_cuts)
    crop_box, rgb, fixtures = w43.crop_box, w43.rgb, w43.FIXTURES
    plan = W.referees()
    held = plan.referee_cells(plan.load_manifest())
    rows = select(json.loads(stage_matrix.read_bytes())["cells"], B, t1, held, B.LIGHT_WITHHELD, args.whole,
                  args.t1_only)
    reference = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r
                 for r in B.load_published(W.REFERENCE["dark"]).rows}
    states = {}
    if args.cut:
        cut = json.loads(W.refuse_other_wave_path(args.cut, "the cut").read_bytes())
        for c in cut["T1"]["cells"]:
            states[(c["profile"], c["tier"], c["scene"])] = c
    # The per-cell assertion first, for every capture, before any pixel is read.
    paths = []
    for stratum, scale, tier, pose, sid, p, r, part in rows:
        twin = reference.get((p, tier, sid))
        if twin is None:
            raise W.Refusal(f"{p} {tier} {sid}: no {W.REFERENCE['dark']} row")
        paths.append((checked_png(captures, r), checked_png(W.CANONICAL_CAPTURES, twin)))
    out_dir.mkdir(parents=True, exist_ok=True)
    gain = GAIN["dark"]
    index, groups = [], {}
    for item, (mine, theirs) in zip(rows, paths):
        groups.setdefault(item[:4], []).append((item, mine, theirs))
    for (stratum, scale, tier, pose), items in groups.items():
        for start in range(0, len(items), args.rows):
            chunk = items[start:start + args.rows]
            strips = []
            for (stratum, scale, tier, pose, sid, p, r, part), mine, theirs in chunk:
                n, k, c = rgb(fixtures / p / f"{sid}.png"), rgb(mine), rgb(theirs)
                x0, y0, x1, y1 = crop_box(sid, scale, n.shape)
                crops = [x[y0:y1, x0:x1] for x in (n, c, k)]
                images = [tile(x, scale) for x in crops + [diff(crops[2], crops[0], gain),
                                                           diff(crops[1], crops[0], gain),
                                                           diff(crops[2], crops[1], gain)]]
                h = images[0].shape[0]
                s = states.get((p, tier, sid))
                lines = [(f"{scale}x {tier} {sid}", (240, 240, 240)),
                         (f"{part} / {B.SCENES.role[sid]} / {pose} / stratum {stratum}", (180, 200, 255))]
                if s is not None:
                    lines.append((f"T1 n {s['native']:.4f} ref {s['reference']:.4f} W47 {s['candidate']:.4f}  "
                                  f"{s['fidelity']}/{s['change']}", (230, 230, 160)))
                    for band in ("fine", "low"):
                        if "bands" in s:
                            b = s["bands"][band]
                            lines.append((f"T1-{band} n {b['native']:.4f} ref {b['reference']:.4f} W47 "
                                          f"{b['candidate']:.4f}  {b['fidelity']}/{b['change']}", (200, 230, 200)))
                strips.append(np.concatenate([label_image(lines, h)] + [np.pad(x, ((0, 0), (2, 2), (0, 0)))
                                                                         for x in images], axis=1))
            width = max(x.shape[1] for x in strips)
            strips = [np.pad(x, ((0, 4), (0, width - x.shape[1]), (0, 0))) for x in strips]
            header = Image.new("RGB", (width, 24), (10, 10, 10))
            ImageDraw.Draw(header).text((8, 4), f"W47 sheets: stratum {stratum}, {scale}x, {tier}, {pose}; difference "
                                        f"gain x{gain}   columns: " + " | ".join(columns(gain)),
                                        fill=(255, 255, 255), font=FONT)
            name = f"{stratum}-{scale}x-{tier}-{pose}-{start // args.rows + 1}.png"
            Image.fromarray(np.concatenate([np.asarray(header)] + strips, axis=0)).save(out_dir / name)
            index.append((name, len(chunk)))
    with (out_dir / "index.html").open("w") as f:
        f.write(f"<html><body><h1>W47 eye sheets (difference gain x{gain})</h1><p>Columns: "
                + html.escape(" | ".join(columns(gain))) + "</p>")
        for name, n in index:
            f.write(f'<h2>{html.escape(name)} ({n} cells)</h2><img src="{html.escape(name)}"><br>')
        f.write("</body></html>\n")
    print(json.dumps(dict(pages=len(index), cells=len(rows), gain=gain, out=str(out_dir))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
