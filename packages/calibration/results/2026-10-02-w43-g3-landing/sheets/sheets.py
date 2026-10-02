#!/usr/bin/env python3.12
"""W43 G3 (iii), charter clause 14: eye sheets over the WHOLE canonical glass 0.25 bed (§5.201).

G3 (i)'s sheets (``../../2026-10-02-w43-g3-refit/sheets/sheets.py``) were drawn in scratch over
the non-holdout cells of a candidate. These are drawn over what was published: every scene the
four ``-glass0.25`` standard profiles declare in ``scenes.json``, every role (calibration,
validation, holdout, recorded, probe), both poses and both tiers, read from the PUBLISHED
generation files the index names current and from the CANONICAL capture tree. Each row is

  Apple 0.25 (fixture) | vitrea 0.25 (shipped) | Apple 0.5 (fixture) | vitrea 0.5 (shipped) |
  |vitrea 0.25 - Apple 0.25| x4 | |vitrea 0.5 - Apple 0.5| x4

so Apple's two slider positions and vitrea's two renders sit side by side. The brief named the
0.5 render without its fixture; the 0.5 fixture is added beside it, because without it the only
view of what Apple's material does between the positions is a difference image. Where the
current 0.5 generation has no row for the cell (its recorded rows and part of its probe rows were
never read), the 0.5 render and its difference are an empty labelled tile; the 0.5 fixture is
still drawn. Each row is cropped to the component's declared box plus 24 CSS px, 1x cells shown
at 2x pixel size, and labelled with its role, its pose and the L1 level error of both renders
(|web - native| of the interior mean, linear luminance, as the rows record it).

Strata as G3 (i) declared them (``STRATA`` there; gradient is empty on the canonical bed). Pages
are per (stratum, tier, scheme, pose), split into balanced parts of at most ``--rows`` rows,
holdout rows first and marked with an orange bar; the holdout cells also have pages of their own.

Before any capture pixel is read, every capture's cell JSON (``cell__<tier>.json``) must name
the published row's ``capturePath``, ``sceneId`` and ``renderer``: the per-cell assertion that a
capture names the shipped document bytes, the receded document included (CLAUDE.md, W31). A
mismatch refuses the whole run. The 0.25 rows are admitted by ``cuts/bed.py``'s ``sealed`` mode
(both sealed documents at their live hash, holdout admitted); the 0.5 rows must name the two
shipped 0.5 documents of their scheme at their live hash. Reads only; writes PNGs, index.html,
README.txt and checks.json under --out.

    python3.12 -B sheets.py --out DIR [--captures TREE] [--tier webgpu,css] [--rows 30]
"""
from __future__ import annotations

import argparse
import hashlib
import html
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
G3I = HERE.parents[1] / "2026-10-02-w43-g3-refit" / "sheets" / "sheets.py"
_spec = importlib.util.spec_from_file_location("w43_g3i_sheets", G3I)
S1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S1)
B = S1.B                      # cuts/bed.py, as G3 (i) imported it
STRATA, FIXTURES, crop_box, rgb = S1.STRATA, S1.FIXTURES, S1.crop_box, S1.rgb

GENERATIONS = B.RESULTS / "generations"
ROLES = ("holdout", "calibration", "validation", "recorded", "probe")
POSES = {"active": ("rest", "pressed"), "inactive": ("inactive",)}
ROLE_COLOUR = {"holdout": (255, 150, 40), "calibration": (120, 200, 255),
               "validation": (150, 230, 150), "recorded": (200, 170, 255), "probe": (190, 190, 190)}
COLUMNS = ("Apple 0.25 fixture", "vitrea 0.25 shipped", "Apple 0.5 fixture", "vitrea 0.5 shipped",
           "|v0.25 - A0.25| x4", "|v0.5 - A0.5| x4")
LABEL_W = 360
CAPTION_H = 18
FONT = ImageFont.load_default(size=14)
SMALL = ImageFont.load_default(size=12)


def canonical_tree() -> Path:
    """The main checkout's capture tree: a worktree inherits none (CLAUDE.md)."""
    common = subprocess.run(["git", "-C", str(B.ROOT), "rev-parse", "--path-format=absolute",
                             "--git-common-dir"], check=True, capture_output=True, text=True)
    return Path(common.stdout.strip()).parent / "packages" / "calibration" / "web-captures"


def published(profiles) -> dict:
    """The current generation file of each profile, its bytes checked against the index."""
    index = json.loads((GENERATIONS / "index.json").read_bytes())
    out = {}
    for profile in profiles:
        name = index["currentByProfile"][profile]
        meta = index["files"][name]
        raw = (GENERATIONS / name).read_bytes()
        if hashlib.sha256(raw).hexdigest() != meta["sha256"] or len(raw) != meta["bytes"]:
            raise SystemExit(f"generations/{name}: bytes differ from index.json's record")
        if meta["status"] != "current":
            raise SystemExit(f"generations/{name}: status {meta['status']}")
        out[profile] = dict(file=name, sha256=meta["sha256"], bytes=meta["bytes"])
    return out


def admit_05(row: dict, shipped: dict) -> None:
    profile, sid = row["key"]["profileKey"], row["key"]["sceneId"]
    path = row["key"]["web"]["capturePath"]
    where = f"0.5 row {profile} {row['key']['web']['renderer']} {sid}"
    if "crossPosition=" in path or B.CANDIDATE_CLAUSE.search(path):
        raise SystemExit(f"{where}: not a strict shipped-mode row")
    named = {kind: (p, s) for kind, p, s in B.DOC_CLAUSE.findall(path)}
    scheme = B.scheme_of(profile)
    for kind, suffix in (("materialProfile", ""), ("recededProfile", "-receded")):
        rel = f"packages/calibration/profiles/apple-macos-27.0-1x-{scheme}-standard-glass0.5{suffix}.json"
        if named.get(kind) != (rel, shipped[rel]):
            raise SystemExit(f"{where}: {kind} is {named.get(kind)}, not {rel} at {shipped[rel]}")
    if (row.get("fixtureSet"), row.get("state")) != (B.SCENES.role[sid], B.SCENES.by_id[sid]["state"]):
        raise SystemExit(f"{where}: fixtureSet/state disagree with scenes.json")


def check_cell(tree: Path, row: dict) -> tuple[Path, bool]:
    """The per-cell assertion. Returns the PNG path and whether the whole web key matched too."""
    key = row["key"]
    profile, sid, renderer = key["profileKey"], key["sceneId"], key["web"]["renderer"]
    folder = tree / profile / sid
    cell_path = folder / f"cell__{renderer}.json"
    if not cell_path.exists():
        raise SystemExit(f"{cell_path}: no cell JSON for a published row")
    cell = json.loads(cell_path.read_bytes())
    for field in ("capturePath", "sceneId", "renderer"):
        if cell.get(field) != key["web"][field]:
            raise SystemExit(f"{cell_path}: {field} {cell.get(field)!r} is not the published "
                             f"row's {key['web'][field]!r}")
    png = folder / f"{sid}__{renderer}.png"
    if not png.exists():
        raise SystemExit(f"{png}: missing")
    return png, cell == key["web"]


def level(row: dict | None):
    if row is None:
        return None
    web = B.value(row, "material", "interiorMeanWeb")
    native = B.value(row, "material", "interiorMeanNative")
    return None if web is None or native is None else web - native


def fmt(err) -> str:
    return "unmeasured" if err is None else f"{abs(err):.4f} (web-native {err:+.4f})"


def diff(a: np.ndarray, n: np.ndarray) -> np.ndarray:
    return np.clip(np.abs(a.astype(int) - n.astype(int)) * 4, 0, 255).astype(np.uint8)


def empty_tile(shape, text: str) -> np.ndarray:
    tile = Image.new("RGB", (shape[1], shape[0]), (58, 58, 58))
    draw = ImageDraw.Draw(tile)
    for i, line in enumerate(text.split("\n")):
        draw.text((8, 8 + 16 * i), line, fill=(235, 235, 235), font=SMALL)
    return np.asarray(tile)


def strip_for(entry: dict) -> tuple[np.ndarray, list[int]]:
    profile, sid, scale = entry["profile"], entry["sid"], entry["scale"]
    n25 = rgb(FIXTURES / profile / f"{sid}.png")
    n05 = rgb(FIXTURES / B.counterpart_05(profile) / f"{sid}.png")
    w25 = rgb(entry["png25"])
    for name, a in (("0.5 fixture", n05), ("0.25 render", w25)):
        if a.shape != n25.shape:
            raise SystemExit(f"{profile} {sid}: {name} is {a.shape}, the 0.25 fixture {n25.shape}")
    x0, y0, x1, y1 = crop_box(sid, scale, n25.shape)
    crop = lambda a: a[y0:y1, x0:x1]  # noqa: E731
    if entry["png05"] is not None:
        w05 = rgb(entry["png05"])
        if w05.shape != n25.shape:
            raise SystemExit(f"{profile} {sid}: 0.5 render is {w05.shape}")
        tiles = [crop(n25), crop(w25), crop(n05), crop(w05), crop(diff(w25, n25)), crop(diff(w05, n05))]
    else:
        tiles = [crop(n25), crop(w25), crop(n05), None, crop(diff(w25, n25)), None]
    if scale == 1:
        tiles = [None if t is None else np.kron(t, np.ones((2, 2, 1), dtype=np.uint8)) for t in tiles]
    tiles = [empty_tile(tiles[0].shape, "no row in the current\n0.5 generation") if t is None else t
             for t in tiles]
    padded = [np.pad(t, ((2, 2), (2, 2), (0, 0)), constant_values=40) for t in tiles]
    xs, x = [], 0
    for t in padded:
        xs.append(x)
        x += t.shape[1]
    return np.concatenate(padded, 1), xs


def draw_page(title: str, entries: list[dict], path: Path) -> None:
    strips = [strip_for(e) for e in entries]
    width = LABEL_W + max(s.shape[1] for s, _ in strips)
    height = 44 + sum(s.shape[0] + CAPTION_H + 10 for s, _ in strips)
    page = Image.new("RGB", (width, height), (24, 24, 24))
    draw = ImageDraw.Draw(page)
    draw.text((8, 10), title, fill=(240, 240, 240), font=FONT)
    y = 44
    for (strip, xs), e in zip(strips, entries):
        colour = ROLE_COLOUR[e["role"]]
        if e["role"] == "holdout":
            draw.rectangle((0, y, 7, y + CAPTION_H + strip.shape[0]), fill=colour)
        for x, name in zip(xs, COLUMNS):
            draw.text((LABEL_W + x + 4, y + 2), name, fill=(170, 170, 170), font=SMALL)
        page.paste(Image.fromarray(strip), (LABEL_W, y + CAPTION_H))
        lines = [
            (f"{e['scale']}x {e['scheme']}  {e['tier']}", (230, 230, 230)),
            (e["sid"], (230, 230, 230)),
            (f"role: {e['role'].upper() if e['role'] == 'holdout' else e['role']}", colour),
            (f"pose: {e['pose']}", (230, 230, 230)),
            ("L1 level err |web - native|:", (200, 200, 200)),
            (f"  0.25 {fmt(e['err25'])}", (230, 230, 230)),
            (f"  0.5  {'no row' if e['png05'] is None else fmt(e['err05'])}", (230, 230, 230)),
        ]
        for i, (line, fill) in enumerate(lines):
            draw.text((14, y + CAPTION_H + 2 + 17 * i), line, fill=fill, font=FONT)
        y += strip.shape[0] + CAPTION_H + 10
    page.save(path)


README = """W43 G3 (iii), charter clause 14: eye sheets over the whole canonical glass 0.25 bed (§5.201).

Open index.html. Every scene the four -glass0.25 standard profiles declare (164 light, 117 dark,
at 1x and 2x), every role (calibration, validation, holdout, recorded, probe), both poses and both
tiers: {cells} cells on {pages} pages. Read from the published generation files and the canonical
capture tree; every capture's cell JSON was checked to name its published row's capturePath
before a pixel was read ({checked} cells checked, all matched).

Each row, left to right:
  Apple 0.25 fixture   the native capture at glass 0.25
  vitrea 0.25 shipped  the published 0.25 render (the sealed 0.25 documents)
  Apple 0.5 fixture    the native capture of the same scene at glass 0.5 (the default position)
  vitrea 0.5 shipped   the published 0.5 render of that scene (the current 0.5 generation)
  |v0.25 - A0.25| x4   absolute difference of the 0.25 render from the 0.25 fixture, times 4
  |v0.5 - A0.5| x4     the same at 0.5
Where the current 0.5 generation has no row for a cell (its recorded rows and part of its probe
rows), the 0.5 render and its difference are a grey labelled tile; the 0.5 fixture is still drawn.
Crops are the component's declared box plus 24 CSS px; 1x cells are shown at 2x pixel size.
The label gives scale, scheme, tier, scene, role, pose and the L1 level error of both renders:
|web - native| of the interior mean (linear luminance), signed value beside it.

Pages: one per stratum x tier x scheme x pose, split into balanced parts of at most {rows} rows.
Strata by backdrop, as W42 declared them and G3 (i) drew them:
  uniform   dark-solid, light-solid, mid-dark-solid, mid-chroma-solid, mid-light-solid
  binary    checkerboard, checkerboard-4/-8/-32/-64, checkerboard-lc16
  text      hc-text, hc-text-7, hc-text-28
  impulse   impulse
  photo     photo
  gradient  empty: the canonical bed declares no gradient backdrop
Pose: active is the focused window (rest, or pressed for the recorded cells); inactive is the
unfocused window, drawn with the receded document.
Holdout cells come first on each page, with an orange bar on the left and the role in capitals.
They also have pages of their own (holdout-<tier>-<scheme>-<pose>.png). The holdout was read once
per tier at G3 (ii); these sheets only look at the captures that reading measured.
"""


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--captures", type=Path, default=None,
                    help="the canonical capture tree (default: the main checkout's)")
    ap.add_argument("--tier", default="webgpu,css")
    ap.add_argument("--rows", type=int, default=30)
    args = ap.parse_args()
    tree = (args.captures or canonical_tree()).resolve()
    tiers = args.tier.split(",")

    files25 = published(B.PROFILES)
    files05 = published([B.counterpart_05(p) for p in B.PROFILES])
    bed = B.load(sorted({str(GENERATIONS / f["file"]) for f in files25.values()}), "sealed",
                 with_holdout=True)
    shipped = B.shipped_05()
    rows05 = {}
    for name in sorted({f["file"] for f in files05.values()}):
        for row in json.loads((GENERATIONS / name).read_bytes())["cells"]:
            if row["key"]["profileKey"] in files05:
                admit_05(row, shipped)
                rows05[(row["key"]["profileKey"], row["key"]["web"]["renderer"], row["key"]["sceneId"])] = row

    # Every declared cell has exactly one published 0.25 row; then every capture is checked,
    # 0.25 and 0.5 alike, before any pixel is read.
    entries, tally = [], Counter()
    stratum_of = {bg: s for s, bgs in STRATA.items() for bg in bgs}
    for renderer in tiers:
        rows25 = bed.by_key(renderer)
        for profile in B.PROFILES:
            for sid in B.SCENES.declared(profile):
                row = rows25.get((profile, sid))
                if row is None:
                    raise SystemExit(f"{profile} {renderer} {sid}: declared, no published row")
                png25, full25 = check_cell(tree, row)
                tally["checked025"] += 1
                tally["webKeyEqual025"] += full25
                row05 = rows05.get((B.counterpart_05(profile), renderer, sid))
                png05 = None
                if row05 is not None:
                    png05, full05 = check_cell(tree, row05)
                    tally["checked05"] += 1
                    tally["webKeyEqual05"] += full05
                else:
                    tally["no05row"] += 1
                state = B.SCENES.by_id[sid]["state"]
                entries.append(dict(
                    profile=profile, sid=sid, tier=renderer, scale=B.scale_of(profile),
                    scheme=B.scheme_of(profile), role=B.SCENES.role[sid],
                    stratum=stratum_of[B.SCENES.by_id[sid]["background"]],
                    pose="inactive (receded document)" if state == "inactive" else f"active ({state})",
                    posekey=next(k for k, v in POSES.items() if state in v),
                    png25=png25, png05=png05, err25=level(row), err05=level(row05)))
    held = sum(r["key"]["web"]["renderer"] in tiers for r in bed.rows)
    if len(entries) != held:
        raise SystemExit(f"{len(entries)} cells declared, the published files hold {held} rows")
    print(f"capturePath checked: {tally['checked025']} 0.25 + {tally['checked05']} 0.5 cells, all "
          f"matched; {tally['no05row']} cells have no 0.5 row", flush=True)

    args.out.mkdir(parents=True, exist_ok=True)
    order = lambda e: (ROLES.index(e["role"]), e["sid"], e["scale"])  # noqa: E731
    pages = []

    def emit(prefix: str, group: list[dict], title: str, meta: dict) -> None:
        group = sorted(group, key=order)
        size = -(-len(group) // -(-len(group) // args.rows))   # balanced parts, none over --rows
        parts = [group[i:i + size] for i in range(0, len(group), size)]
        for k, part in enumerate(parts, 1):
            suffix = f"-{k}" if len(parts) > 1 else ""
            name = f"{prefix}{suffix}.png"
            head = f"{title}{f'  (part {k}/{len(parts)})' if len(parts) > 1 else ''}"
            draw_page(f"W43 G3 (iii) canonical 0.25 bed | {head} | " + " | ".join(COLUMNS), part,
                      args.out / name)
            pages.append(dict(meta, name=name, cells=len(part),
                              roles=dict(Counter(e["role"] for e in part))))
            print(name, len(part), flush=True)

    for renderer in tiers:
        for stratum in STRATA:
            for scheme in ("light", "dark"):
                for posekey in POSES:
                    group = [e for e in entries if (e["tier"], e["stratum"], e["scheme"], e["posekey"])
                             == (renderer, stratum, scheme, posekey)]
                    meta = dict(kind="stratum", stratum=stratum, tier=renderer, scheme=scheme, pose=posekey)
                    if not group:
                        pages.append(dict(meta, name=None, cells=0, roles={}))
                        continue
                    emit(f"{stratum}-{renderer}-{scheme}-{posekey}", group,
                         f"{stratum} | {renderer} | {scheme} | {posekey}", meta)
    for renderer in tiers:
        for scheme in ("light", "dark"):
            for posekey in POSES:
                group = [e for e in entries if e["role"] == "holdout" and
                         (e["tier"], e["scheme"], e["posekey"]) == (renderer, scheme, posekey)]
                if group:
                    emit(f"holdout-{renderer}-{scheme}-{posekey}", group,
                         f"HOLDOUT, all strata | {renderer} | {scheme} | {posekey}",
                         dict(kind="holdout", stratum="all", tier=renderer, scheme=scheme, pose=posekey))

    drawn = [p for p in pages if p["name"]]
    tabled = lambda a, b: {f"{x} {y}": n for (x, y), n in  # noqa: E731
                           sorted(Counter((e[a], e[b]) for e in entries).items())}
    counts = dict(byTier=dict(Counter(e["tier"] for e in entries)),
                  byStratumTier=tabled("stratum", "tier"), byRoleTier=tabled("role", "tier"),
                  byStratumRole=tabled("stratum", "role"), byPoseTier=tabled("posekey", "tier"))
    checks = dict(
        captureTree=str(tree), cells=len(entries), pages=len(drawn),
        stratumPages=sum(p["kind"] == "stratum" for p in drawn),
        holdoutPages=sum(p["kind"] == "holdout" for p in drawn),
        capturePathChecked=dict(glass025=tally["checked025"], glass05=tally["checked05"],
                                total=tally["checked025"] + tally["checked05"], mismatches=0),
        wholeWebKeyEqual=dict(glass025=tally["webKeyEqual025"], glass05=tally["webKeyEqual05"]),
        cellsWithNo05Row=tally["no05row"],
        generations025={p: f for p, f in files25.items()},
        generations05={p: f for p, f in files05.items()},
        counts=counts, pagesList=pages)
    (args.out / "checks.json").write_text(json.dumps(checks, indent=1) + "\n")
    (args.out / "README.txt").write_text(README.format(
        cells=len(entries), pages=len(drawn), rows=args.rows,
        checked=tally["checked025"] + tally["checked05"]))
    with (args.out / "index.html").open("w") as f:
        f.write("<!doctype html><meta charset=utf-8><title>W43 G3 (iii) eye sheets</title>"
                "<body style='background:#111;color:#ddd;font:14px system-ui;max-width:72em'>"
                "<h1>W43 G3 (iii): the whole canonical glass 0.25 bed</h1>"
                f"<p>{len(entries)} cells, {len(drawn)} pages. Each row: "
                + " | ".join(html.escape(c) for c in COLUMNS) +
                ". Crops are the component plus 24 CSS px; 1x cells at 2&times; pixel size. "
                "Holdout rows come first on each page, orange bar on the left. "
                f"capturePath checked on {tally['checked025'] + tally['checked05']} captures "
                f"({tally['checked025']} at 0.25, {tally['checked05']} at 0.5), all matched; "
                f"{tally['no05row']} cells have no row in the current 0.5 generation. "
                "See README.txt.</p>")
        for kind, heading in (("holdout", "Holdout only"), ("stratum", "By stratum")):
            f.write(f"<h2>{heading}</h2><ul>")
            for p in pages:
                if p["kind"] != kind:
                    continue
                roles = ", ".join(f"{r} {p['roles'][r]}" for r in ROLES if r in p["roles"])
                label = (f"{p['stratum']} — {p['tier']} — {p['scheme']} — {p['pose']}: "
                         f"{p['cells']} cells")
                f.write(f"<li><a href='{p['name']}'>{html.escape(p['name'])}</a> {html.escape(label)}"
                        f" ({html.escape(roles)})</li>" if p["name"] else
                        f"<li>{html.escape(label)} (empty on the canonical bed)</li>")
            f.write("</ul>")
        f.write("</body>\n")
    print(json.dumps({k: v for k, v in checks.items() if k != "pagesList"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
