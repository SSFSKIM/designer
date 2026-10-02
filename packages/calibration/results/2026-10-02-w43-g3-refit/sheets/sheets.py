#!/usr/bin/env python3.12
"""W43 G3 (i), step 3: eye sheets by stratum (charter clause 14; W42's six strata).

One page per (stratum, tier, scheme): every non-holdout canonical 0.25 cell of the stratum, each
row the 0.25 FIXTURE | the CANDIDATE | the PRE-FIT render (the 0.5 documents on the 0.25 cell) |
|candidate − fixture| ×4 | |pre-fit − fixture| ×4, cropped to the component's declared box plus
24 CSS px at the cell's own device resolution, with the row's L1 error (|web − native|
interiorMean, linear) for both renders beside it. Strata by backdrop, as W42 declared them:

  uniform   dark-solid, light-solid, mid-dark-solid, mid-chroma-solid, mid-light-solid
  binary    checkerboard, checkerboard-4/-8/-32/-64, checkerboard-lc16
  text      hc-text, hc-text-7, hc-text-28
  impulse   impulse
  photo     photo
  gradient  none: the canonical bed declares no gradient backdrop (W42 took its gradient
            stratum from the W39 archive, which is not this bed); recorded as an empty stratum

Holdout cells are never opened (``cuts/bed.py`` refuses their rows; the fixture reader refuses
the role). Reads only; writes PNGs and an index.html under --out.

    python3.12 -B sheets.py --candidate LABEL --out DIR [--tier webgpu,css]
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402

SCRATCH = Path.home() / "vitrea-w43" / "g3-scratch"
FIXTURES = B.ROOT / "apps" / "reference-apple" / "fixtures"
STRATA = {
    "uniform": {"dark-solid", "light-solid", "mid-dark-solid", "mid-chroma-solid", "mid-light-solid"},
    "binary": {"checkerboard", "checkerboard-4", "checkerboard-8", "checkerboard-32",
               "checkerboard-64", "checkerboard-lc16"},
    "text": {"hc-text", "hc-text-7", "hc-text-28"},
    "impulse": {"impulse"},
    "photo": {"photo"},
    "gradient": set(),
}
MARGIN_CSS = 24
LABEL_W = 300


def rgb(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("RGB"))


def crop_box(sid: str, scale: int, shape) -> tuple[int, int, int, int]:
    comp = B.SCENES.component(sid)
    if "size" in comp:
        w, h = comp["size"]
        dx, dy = comp.get("offset", [0, 0])
    else:
        w, h, dx, dy = 300, 180, 0, 0
    cx, cy = 160 + dx, 100 + dy
    x0 = max(0, int((cx - w / 2 - MARGIN_CSS) * scale))
    y0 = max(0, int((cy - h / 2 - MARGIN_CSS) * scale))
    x1 = min(shape[1], int((cx + w / 2 + MARGIN_CSS) * scale))
    y1 = min(shape[0], int((cy + h / 2 + MARGIN_CSS) * scale))
    return x0, y0, x1, y1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--candidate", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--tier", default="webgpu,css")
    args = ap.parse_args()
    cand_root = SCRATCH / "fit" / args.candidate
    candidate = B.load([str(cand_root / "matrix.json")], "candidate",
                       str((EVIDENCE / "fit" / "candidates" / args.candidate / "candidate.json").relative_to(B.ROOT)))
    prefit = B.load([str(SCRATCH / "prefit" / "matrix.json")], "prefit")
    args.out.mkdir(parents=True, exist_ok=True)
    pages = []
    for renderer in args.tier.split(","):
        cand = candidate.by_key(renderer)
        pre = prefit.by_key(renderer)
        for stratum, backdrops in STRATA.items():
            for scheme in ("light", "dark"):
                keys = sorted(k for k in cand if B.scheme_of(k[0]) == scheme
                              and B.SCENES.by_id[k[1]]["background"] in backdrops and k in pre)
                if not keys:
                    pages.append((stratum, renderer, scheme, None, 0))
                    continue
                rows = []
                for profile, sid in keys:
                    scale = B.scale_of(profile)
                    n = rgb(FIXTURES / profile / f"{sid}.png")
                    c = rgb(cand_root / "web-captures" / profile / sid / f"{sid}__{renderer}.png")
                    p = rgb(SCRATCH / "prefit" / "web-captures" / profile / sid / f"{sid}__{renderer}.png")
                    x0, y0, x1, y1 = crop_box(sid, scale, n.shape)
                    crop = lambda a: a[y0:y1, x0:x1]  # noqa: E731
                    diff = lambda a: np.clip(np.abs(a.astype(int) - n.astype(int)) * 4, 0, 255).astype(np.uint8)  # noqa: E731
                    tiles = [crop(n), crop(c), crop(p), crop(diff(c)), crop(diff(p))]
                    if scale == 1:
                        tiles = [np.kron(t, np.ones((2, 2, 1), dtype=np.uint8)) for t in tiles]
                    strip = np.concatenate([np.pad(t, ((2, 2), (2, 2), (0, 0)), constant_values=40) for t in tiles], 1)
                    err = lambda r: (None if B.value(r, "material", "interiorMeanWeb") is None or  # noqa: E731
                                     B.value(r, "material", "interiorMeanNative") is None else
                                     B.value(r, "material", "interiorMeanWeb") - B.value(r, "material", "interiorMeanNative"))
                    ec, ep = err(cand[(profile, sid)]), err(pre[(profile, sid)])
                    text = [f"{profile.replace('apple-macos-27.0-', '').replace('-standard-glass0.25', '')}",
                            sid, cand[(profile, sid)]["fixtureSet"],
                            f"level err cand {'—' if ec is None else f'{ec:+.4f}'}",
                            f"level err prefit {'—' if ep is None else f'{ep:+.4f}'}"]
                    rows.append((strip, text))
                width = LABEL_W + max(s.shape[1] for s, _ in rows)
                height = sum(s.shape[0] + 6 for s, _ in rows) + 40
                page = Image.new("RGB", (width, height), (24, 24, 24))
                draw = ImageDraw.Draw(page)
                draw.text((8, 8), f"W43 G3 (i) {args.candidate} | {stratum} | {renderer} | {scheme}: "
                          "fixture 0.25 | candidate | pre-fit (0.5 docs) | |cand-fixture|x4 | |prefit-fixture|x4",
                          fill=(230, 230, 230))
                y = 40
                for strip, text in rows:
                    page.paste(Image.fromarray(strip), (LABEL_W, y))
                    for i, line in enumerate(text):
                        draw.text((8, y + 4 + 14 * i), line, fill=(220, 220, 220))
                    y += strip.shape[0] + 6
                name = f"{stratum}-{renderer}-{scheme}.png"
                page.save(args.out / name, optimize=True)
                pages.append((stratum, renderer, scheme, name, len(rows)))
    with (args.out / "index.html").open("w") as f:
        f.write(f"<!doctype html><meta charset=utf-8><title>W43 G3 (i) {html.escape(args.candidate)}</title>"
                "<body style='background:#111;color:#ddd;font:14px system-ui'>"
                f"<h1>W43 G3 (i) eye sheets: {html.escape(args.candidate)}</h1>"
                "<p>Each row: the 0.25 fixture | the candidate | the pre-fit render (the shipped 0.5 "
                "documents on the 0.25 cell) | |candidate − fixture| ×4 | |pre-fit − fixture| ×4. "
                "1x cells are shown at 2× pixel size. Holdout never read.</p><ul>")
        for stratum, renderer, scheme, name, count in pages:
            label = f"{stratum} — {renderer} — {scheme}: {count} cells"
            f.write(f"<li><a href='{name}'>{html.escape(label)}</a></li>" if name else
                    f"<li>{html.escape(label)} (empty stratum on the canonical bed)</li>")
        f.write("</ul></body>\n")
    print(json.dumps(pages))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
