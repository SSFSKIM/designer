#!/usr/bin/env python3
"""W27c G2 read: the pair sheets, because metrics are not the whole verdict.

One PNG per profile: every checking cell as native | web | 8× amplified absolute
difference, captioned with the two metrics the bound scores on. The rule this
serves is the repository's own — put the capture next to the native fixture and
look, because SSIM and ΔE can score well on a blurred interior while the eye sees
the rim band or the lens curvature differ.

    python3 sheet.py /tmp/w27c-g2/checking.json [OUTDIR]
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = HERE.split("/packages/")[0]
FIXTURES = os.path.join(REPO, "apps/reference-apple/fixtures")
GAIN = 8


def strip(native_path, web_path):
    native = Image.open(native_path).convert("RGB")
    web = Image.open(web_path).convert("RGB")
    diff = ImageChops.difference(native, web).point(lambda v: min(255, v * GAIN))
    width, height = native.size
    out = Image.new("RGB", (width * 3 + 8, height), (24, 24, 24))
    out.paste(native, (0, 0))
    out.paste(web, (width + 4, 0))
    out.paste(diff, (width * 2 + 8, 0))
    return out


def main():
    read = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "/tmp/w27c-g2/checking.json"))
    outdir = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "sheets")
    os.makedirs(outdir, exist_ok=True)
    rows = [r for r in read["rows"] if r["scored"]]
    written = []
    for profile in sorted({r["profile"] for r in rows}):
        cells = sorted((r for r in rows if r["profile"] == profile),
                       key=lambda r: -r["body"]["deltaE"])
        strips = [(r, strip(r["nativePath"], r["capture"])) for r in cells]
        width = max(s.width for _, s in strips)
        pitch = strips[0][1].height + 22
        sheet = Image.new("RGB", (width + 16, pitch * len(strips) + 34), (16, 16, 16))
        draw = ImageDraw.Draw(sheet)
        draw.text((8, 8), f"{profile} — native | webgpu | diff x{GAIN}   "
                          f"(worst body ΔE first)", fill=(235, 235, 235))
        for i, (row, image) in enumerate(strips):
            y = 30 + i * pitch
            sheet.paste(image, (8, y))
            draw.text((8, y + image.height + 4),
                      f"{row['scene']}   body ΔE {row['body']['deltaE']:.5f}   "
                      f"full-canvas {row['deltaE']['mean']:.5f}   "
                      f"Y {row['body']['webY']:.4f}/{row['body']['nativeY']:.4f}   "
                      f"SD {row['body']['webSD']:.4f}/{row['body']['nativeSD']:.4f}",
                      fill=(190, 190, 190))
        path = os.path.join(outdir, f"{profile}.png")
        sheet.save(path)
        written.append(path)
        print(path)
    print(f"{len(written)} sheet(s)")


sys.exit(main())
