#!/usr/bin/env python3
"""The A/B composite of two gate sheets, side by side under one banner each.

Written for W12 Decision Log 4 (the ω 0.8 round: `lensOvalization` 0.6 against 0.8), which
asks for both sheets put beside each other for the user's eye. Each half keeps the sheet's
own column banner — LEFT native, MIDDLE vitrea, RIGHT signed difference — and gains a
caption strip naming which value of the constant it renders.

    cd packages/calibration && python3 results/2026-09-03-w12-lens/sheets/make-ab.py \
        --left g2-2x.png --left-label "omega 0.6 (landed)" \
        --right g2b-2x.png --right-label "omega 0.8 (A/B)" --out g2-vs-g2b-2x.png

Paths are relative to this script's directory. Needs PIL only.
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
GAP = 12
BACKGROUND = (24, 24, 24)


def label_strip(width, text):
    """A caption strip the height of one large line, in the sheets' own yellow on near-black."""
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', max(22, width // 40))
    except Exception:
        font = None
    probe = ImageDraw.Draw(Image.new('RGB', (1, 1)))
    bbox = probe.textbbox((0, 0), text, font=font)
    strip = Image.new('RGB', (width, bbox[3] - bbox[1] + 28), (16, 16, 16))
    ImageDraw.Draw(strip).text((GAP, 14 - bbox[1]), text, fill=(255, 220, 120), font=font)
    return strip


def half(path, text):
    sheet = Image.open(path).convert('RGB')
    strip = label_strip(sheet.width, text)
    out = Image.new('RGB', (sheet.width, sheet.height + strip.height), BACKGROUND)
    out.paste(strip, (0, 0))
    out.paste(sheet, (0, strip.height))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--left', required=True)
    ap.add_argument('--left-label', required=True)
    ap.add_argument('--right', required=True)
    ap.add_argument('--right-label', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()

    left = half(os.path.join(HERE, args.left), args.left_label)
    right = half(os.path.join(HERE, args.right), args.right_label)
    width = left.width + GAP + right.width
    height = max(left.height, right.height)
    canvas = Image.new('RGB', (width, height), BACKGROUND)
    canvas.paste(left, (0, 0))
    canvas.paste(right, (left.width + GAP, 0))
    out = os.path.join(HERE, args.out)
    canvas.save(out, optimize=True)
    print(out, canvas.size, os.path.getsize(out))


if __name__ == '__main__':
    main()
