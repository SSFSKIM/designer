"""Compose W27f G2's eye sheet — one per colour scheme.

What the sheet is for: claims §5.131 §6 records three residuals that a scalar
does not settle — the light overlay's rim, the photo base's colour, and the dark
unhinted overlay's brightness — and W27f G2's charter puts the user's eye on the
demo's DOM stage. So every row here is a comparison the metrics cannot finish.

Per row, left to right: Apple's own fixture where one exists, then the same
scene drawn three ways — the sampled texture path, the page path at its measured
backdrop level, and the page path with no hint at all. The last of those is the
information limit, not a candidate: a DOM group with neither pixels nor a
declared tone cannot tell a dark page from a light one.

**Scale.** The calibration bed is 1x, so every fixture and capture here is
320 × 200 device pixels. They are magnified ×2 by **nearest neighbour**, which
turns each source pixel into a crisp 2 × 2 block and invents nothing — it is
reversible, and it is the only way a 320-px panel can be looked at beside the
demo's 792-px stage. Every such panel says `1x ×2 NN` in its label. The demo
panel alone is native device pixels at devicePixelRatio 2. The ruler is true for
the demo panel and for the magnified ones alike, because ×2 of a 1x capture and
native dpr-2 are the same number of device pixels per CSS pixel.

Run after the captures exist and `capture-demo.mjs` has written `panels/`:

    /Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python compose.py --scratch /tmp/w27f-g2
"""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PANELS = HERE / "panels"
# eye → 2026-09-11-w27f-g2 → results → calibration → packages → the repository.
REPO = HERE.parents[4]
FIXTURES = REPO / "apps" / "reference-apple" / "fixtures"
if not FIXTURES.is_dir():  # a wrong depth here silently turns every fixture into
    raise SystemExit(f"no fixtures at {FIXTURES}")  # a "no native fixture" panel.

WIDTH = 4720
MARGIN = 72
GAP = 28

FONT = "/System/Library/Fonts/HelveticaNeue.ttc"
MONO = "/System/Library/Fonts/Menlo.ttc"


def font(size: int, *, mono: bool = False, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(MONO if mono else FONT, size, index=index)


F_TITLE = font(58, index=8)
F_HEAD = font(38, index=8)
F_BODY = font(26)
F_CAPTION = font(25)
F_LABEL = font(21, mono=True)

THEME = {
    "light": {"bg": (250, 251, 252), "ink": (16, 19, 22), "dim": (96, 104, 112),
              "rule": (206, 213, 219)},
    "dark": {"bg": (14, 16, 18), "ink": (236, 239, 242), "dim": (150, 158, 166),
             "rule": (54, 60, 66)},
}

# The four arms a row shows, in the order they are drawn.
ARMS = [
    ("sampled", "the sampled texture path (S1 on a stack)"),
    ("unsampled-hint", "the page path at its measured level (Uh)"),
    ("unsampled-nohint", "the page path with no hint (U0) — the information limit"),
]

STACKS = ["checkerboard__glass-over-glass__rest", "photo__glass-over-glass__rest"]

# The ordinary cells §5.131 §3 and §5 single out, and why each is on the sheet.
PAGE_CELLS = [
    ("dark-solid__rrect-md__rest",
     "the thick body G1 repaired: native ΔE 0.07851 → 0.00667 in light"),
    ("checkerboard__rrect-md__rest",
     "structure: the page body keeps too little spread (0.0285 against native 0.0479)"),
    ("photo__rrect-md__rest",
     "colour: the photo base still differs, and the page keeps too much spread"),
    ("dark-solid__capsule-button__rest",
     "unknown tone: unhinted, the capsule never collapses (ΔE 0.544 in light)"),
]


class Sheet:
    """A vertical stack of blocks, drawn onto one tall canvas."""

    def __init__(self, scheme: str) -> None:
        self.scheme = scheme
        self.theme = THEME[scheme]
        self.blocks: list[tuple[str, object]] = []

    def title(self, text: str) -> None:
        self.blocks.append(("title", text))

    def head(self, text: str) -> None:
        self.blocks.append(("head", text))

    def body(self, text: str, *, dim: bool = False) -> None:
        self.blocks.append(("dim" if dim else "body", text))

    def rule(self) -> None:
        self.blocks.append(("rule", None))

    def ruler(self) -> None:
        self.blocks.append(("ruler", None))

    def row(self, panels: list[tuple[Image.Image, str]]) -> None:
        self.blocks.append(("row", panels))

    def _wrap(self, text: str, f: ImageFont.FreeTypeFont) -> list[str]:
        per = f.getlength("n")
        return textwrap.wrap(text, width=max(40, int((WIDTH - 2 * MARGIN) / per)))

    def _label_lines(self, text: str, width: int) -> list[str]:
        per = F_LABEL.getlength("n")
        return textwrap.wrap(text, width=max(12, int(width / per))) or [""]

    def render(self) -> Image.Image:
        rows: list[tuple[str, object, int]] = []
        total = MARGIN
        for kind, payload in self.blocks:
            if kind == "title":
                h = 78
            elif kind == "head":
                h = 56
            elif kind in ("body", "dim"):
                h = 34 * len(self._wrap(payload, F_BODY)) + 8
            elif kind == "rule":
                h = 34
            elif kind == "ruler":
                h = 96
            else:
                images = payload
                label_lines = max(len(self._label_lines(lb, im.width)) for im, lb in images)
                h = max(im.height for im, _ in images) + 16 + 26 * label_lines
            rows.append((kind, payload, h))
            total += h + 16
        total += MARGIN

        sheet = Image.new("RGB", (WIDTH, total), self.theme["bg"])
        draw = ImageDraw.Draw(sheet)
        y = MARGIN
        for kind, payload, h in rows:
            if kind == "title":
                draw.text((MARGIN, y), payload, font=F_TITLE, fill=self.theme["ink"])
            elif kind == "head":
                draw.text((MARGIN, y), payload, font=F_HEAD, fill=self.theme["ink"])
            elif kind in ("body", "dim"):
                colour = self.theme["dim"] if kind == "dim" else self.theme["ink"]
                for i, line in enumerate(self._wrap(payload, F_BODY)):
                    draw.text((MARGIN, y + i * 34), line, font=F_CAPTION, fill=colour)
            elif kind == "rule":
                draw.line([(MARGIN, y + 16), (WIDTH - MARGIN, y + 16)],
                          fill=self.theme["rule"], width=2)
            elif kind == "ruler":
                self._ruler(draw, y)
            else:
                x = MARGIN
                for im, label in payload:
                    sheet.paste(im.convert("RGB"), (x, y))
                    draw.rectangle([x, y, x + im.width - 1, y + im.height - 1],
                                   outline=self.theme["rule"], width=1)
                    for i, line in enumerate(self._label_lines(label, im.width)):
                        draw.text((x, y + im.height + 12 + i * 26), line,
                                  font=F_LABEL, fill=self.theme["dim"])
                    x += im.width + GAP
            y += h + 16
        return sheet

    def _ruler(self, draw: ImageDraw.ImageDraw, y: int) -> None:
        x0 = MARGIN
        draw.line([(x0, y + 44), (x0 + 200, y + 44)], fill=self.theme["ink"], width=3)
        for t in range(0, 201, 20):
            tall = t % 100 == 0
            draw.line([(x0 + t, y + 44), (x0 + t, y + 44 - (18 if tall else 10))],
                      fill=self.theme["ink"], width=3 if tall else 2)
        draw.text((x0 + 220, y + 18),
                  "200 device px = 100 CSS px  ·  the 320 × 200 panels are 1x captures magnified "
                  "×2 by nearest neighbour (no resampling)  ·  the demo panel is native dpr 2",
                  font=F_BODY, fill=self.theme["ink"])


def magnify(image: Image.Image) -> Image.Image:
    """×2, nearest neighbour: one source pixel becomes one 2 × 2 block, exactly."""
    return image.resize((image.width * 2, image.height * 2), Image.Resampling.NEAREST)


def missing(size: tuple[int, int], scheme: str, text: str) -> Image.Image:
    """A panel that says what is absent, in frame, instead of substituting something.

    The dark bed has no `photo__glass-over-glass`, and the honest panel for it is
    a labelled hole — never the light fixture, never the checkerboard stack.
    """
    theme = THEME[scheme]
    image = Image.new("RGB", size, theme["bg"])
    draw = ImageDraw.Draw(image)
    draw.rectangle([0, 0, size[0] - 1, size[1] - 1], outline=theme["rule"], width=3)
    for i, line in enumerate(textwrap.wrap(text, width=30)):
        draw.text((28, size[1] // 2 - 40 + i * 34), line, font=F_CAPTION, fill=theme["dim"])
    return image


def native_path(scheme: str, scene: str) -> Path:
    return FIXTURES / f"apple-macos-26.5-1x-{scheme}-standard" / f"{scene}.png"


def arm_path(scratch: Path, phase: str, scheme: str, arm: str, scene: str) -> Path:
    profile = f"apple-macos-26.5-1x-{scheme}-standard"
    return scratch / phase / scheme / arm / profile / scene / f"{scene}__webgpu.png"


def cell_row(scratch: Path, scheme: str, phase: str, scene: str) -> list[tuple[Image.Image, str]]:
    """Apple's fixture, then the three web arms, all at the same magnification."""
    panels: list[tuple[Image.Image, str]] = []
    native = native_path(scheme, scene)
    if native.exists():
        panels.append((magnify(Image.open(native)),
                       f"NATIVE  {native.parent.name}/{native.name}  ·  1x ×2 NN  ·  read-only"))
    else:
        panels.append((missing((640, 400), scheme,
                               f"no native fixture: apple-macos-26.5-1x-{scheme}-standard "
                               f"carries no {scene}"),
                       "NATIVE  absent — nothing is substituted for it"))
    for arm, description in ARMS:
        path = arm_path(scratch, phase, scheme, arm, scene)
        if path.exists():
            panels.append((magnify(Image.open(path)), f"{arm}  ·  {description}  ·  1x ×2 NN"))
        else:
            panels.append((missing((640, 400), scheme, f"not captured: {arm}"),
                           f"{arm}  ·  absent"))
    return panels


def build(scheme: str, scratch: Path, demo_meta: dict) -> Image.Image:
    sheet = Sheet(scheme)
    sheet.title(f"W27f G2 — the material over ordinary page content ({scheme})")
    sheet.body("The landing gate's eye sheet. Every web panel was drawn at this gate's head by the "
               "same runner that produced its reading; nothing here was made for the picture.")
    sheet.ruler()
    sheet.rule()

    adapter = demo_meta["schemes"][scheme]["adapter"]
    sheet.body(f"Chromium {demo_meta['chromium']}  ·  WebGPU adapter {adapter['vendor']}/"
               f"{adapter['architecture']}  ·  isFallbackAdapter measured "
               f"{adapter['isFallbackAdapter']}  ·  captured {demo_meta['capturedAt']}", dim=True)

    sheet.head("1 · The stacks — the only native evidence of a composed-glass overlay")
    sheet.body("A stack's overlay resolves css-backdrop in every configuration, so this is the one "
               "place Apple's own material can be put beside vitrea's page material directly. Look "
               "at the small inner plate, not the large one: the base is the sampled path on the "
               "left-hand web panel and the page path on the other two.")
    for scene in STACKS:
        sheet.row(cell_row(scratch, scheme, "holdout", scene))

    sheet.head("2 · Ordinary page cells")
    sheet.body("The same material over a single surface, where there is no overlay to confuse it.")
    for scene, why in PAGE_CELLS:
        sheet.body(f"{scene} — {why}", dim=True)
        sheet.row(cell_row(scratch, scheme, "candidate", scene))

    sheet.head("3 · The demo's own page stage, live")
    sheet.body("The shipped site at /#page, drawing over its own paragraph text and CSS gradient — "
               "different backdrop pixels from the harness, and not a controlled comparison. The "
               "readout beneath it is the site's, scraped at the moment of the shot.")
    rows = demo_meta["schemes"][scheme]["readout"]
    stage = Image.open(PANELS / scheme / "demo-page-stage.png")
    sheet.row([(stage, "  ·  ".join(f"{k}: {v}" for k, v in rows.items()) +
                "  ·  native device pixels at dpr 2, not magnified")])
    return sheet.render()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--scratch", type=Path, default=Path("/tmp/w27f-g2"))
    parser.add_argument("--out", type=Path, default=HERE)
    args = parser.parse_args()

    demo_meta = json.loads((PANELS / "demo-meta.json").read_text())
    for scheme in ("light", "dark"):
        sheet = build(scheme, args.scratch, demo_meta)
        path = args.out / f"eye-sheet-{scheme}.png"
        sheet.save(path)
        print(f"wrote {path}  {sheet.width} × {sheet.height}")


if __name__ == "__main__":
    main()
