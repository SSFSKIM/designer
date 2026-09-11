"""Compose the 0.16.0 eye sheets from the captured panels.

One sheet per colour scheme. Every panel is pasted at its captured size: the
captures are device pixels at devicePixelRatio 2 and nothing here resamples
them, so what the sheet shows is what Chromium drew. The only derived images are
the amplified difference panels in the lens row, which are labelled as such.

Run after `apps/demo/eye-capture.mjs` has written `panels/`:

    /Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python compose.py
"""

from __future__ import annotations

import json
import textwrap
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
PANELS = HERE / "panels"
REPO = HERE.parents[4]
FIXTURES = REPO / "apps" / "reference-apple" / "fixtures"

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
F_SMALL = font(19, mono=True)

THEME = {
    "light": {"bg": (250, 251, 252), "ink": (16, 19, 22), "dim": (96, 104, 112), "rule": (206, 213, 219)},
    "dark": {"bg": (14, 16, 18), "ink": (236, 239, 242), "dim": (150, 158, 166), "rule": (54, 60, 66)},
}


class Sheet:
    """A vertical stack of blocks, drawn onto one tall canvas."""

    def __init__(self, scheme: str) -> None:
        self.scheme = scheme
        self.theme = THEME[scheme]
        self.blocks: list[tuple[str, object]] = []

    # — authoring ————————————————————————————————————————————————————————
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
        """One horizontal row of panels, each with a label under it."""
        self.blocks.append(("row", panels))

    # — measuring and drawing ————————————————————————————————————————————
    def _wrap(self, text: str, f: ImageFont.FreeTypeFont) -> list[str]:
        # A character budget from the font's average advance: exact enough for a
        # sheet, and it keeps every caption on the same left edge.
        per = f.getlength("n")
        return textwrap.wrap(text, width=max(40, int((WIDTH - 2 * MARGIN) / per)))

    def _label_lines(self, text: str, width: int) -> list[str]:
        """A panel's label, wrapped to the panel's own width so rows never collide."""
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
                draw.line(
                    [(MARGIN, y + 16), (WIDTH - MARGIN, y + 16)], fill=self.theme["rule"], width=2
                )
            elif kind == "ruler":
                self._ruler(draw, y)
            else:
                x = MARGIN
                for im, label in payload:
                    sheet.paste(im.convert("RGB"), (x, y))
                    draw.rectangle(
                        [x, y, x + im.width - 1, y + im.height - 1],
                        outline=self.theme["rule"],
                        width=1,
                    )
                    for i, line in enumerate(self._label_lines(label, im.width)):
                        draw.text(
                            (x, y + im.height + 12 + i * 26),
                            line,
                            font=F_LABEL,
                            fill=self.theme["dim"],
                        )
                    x += im.width + GAP
            y += h + 16
        return sheet

    def _ruler(self, draw: ImageDraw.ImageDraw, y: int) -> None:
        """200 device pixels = 100 CSS px at devicePixelRatio 2, ticked every 20."""
        x0 = MARGIN
        draw.line([(x0, y + 44), (x0 + 200, y + 44)], fill=self.theme["ink"], width=3)
        for t in range(0, 201, 20):
            tall = t % 100 == 0
            draw.line(
                [(x0 + t, y + 44), (x0 + t, y + 44 - (18 if tall else 10))],
                fill=self.theme["ink"],
                width=3 if tall else 2,
            )
        draw.text(
            (x0 + 220, y + 18),
            "200 device px = 100 CSS px  ·  devicePixelRatio 2  ·  every panel below is at "
            "native pixels, nothing is resampled",
            font=F_BODY,
            fill=self.theme["ink"],
        )


def load(scheme: str, name: str) -> Image.Image:
    return Image.open(PANELS / scheme / name)


def amplify(a: Image.Image, b: Image.Image, factor: int, bg: tuple[int, int, int]) -> Image.Image:
    """|a − b| × factor on a flat ground: where the lens actually moved."""
    diff = np.abs(np.asarray(a.convert("RGB"), float) - np.asarray(b.convert("RGB"), float))
    scaled = np.clip(diff * factor, 0, 255)
    ground = np.asarray(bg, float)
    out = np.clip(ground + scaled * (1 if sum(bg) < 380 else -1), 0, 255)
    return Image.fromarray(out.astype("uint8"))


def presence_label(frame: dict) -> str:
    return (
        f"t = {frame['t']:>3} ms   --vitrea-materialization {frame['materialization']:.4f}   "
        f"opacity {frame['opacity']}"
    )


def build(scheme: str, meta: dict) -> Image.Image:
    m = meta["schemes"][scheme]
    harness = m["harness"]
    adapter = harness["adapter"]
    theme = THEME[scheme]
    s = Sheet(scheme)

    s.title(f"vitrea 0.16.0 — eye sheet — {scheme.upper()} colour scheme")
    s.body(
        f"Chromium {meta['chromium']} (Playwright channel \"chromium\", headed) · WebGPU adapter "
        f"{adapter['vendor']} / {adapter['architecture']} "
        f"(isFallbackAdapter: {str(adapter['isFallbackAdapter']).lower()}) · "
        f"devicePixelRatio 2 · Reduce Transparency and Increase Contrast both off · "
        f"captured {meta['capturedAt'][:19]}Z."
    )
    s.body(
        "Every group photographed below reported activeRenderer: webgpu before its shot was "
        "taken; the capture script refuses the run otherwise. Group ids and their resolved "
        "sampling backends: "
        + ", ".join(f"{g['id']} -> {g['backend']}" for g in harness["states"])
        + ".",
        dim=True,
    )
    if m["playground"] is None:
        s.body(
            "No panel on this sheet comes from the shipped playground: its <GlassRoot> takes the "
            "binding's default colorScheme=\"light\", so there is no dark-material playground to "
            "photograph. The live instances named in eye/index.md are the light sheet's.",
            dim=True,
        )
    s.ruler()
    s.rule()

    # ── 1 — the toolbar split ──────────────────────────────────────────────
    s.head("1 · A toolbar splits its shared background")
    s.body(
        ".changeset/a-toolbar-splits-its-background.md — @vitreajs/vitrea-react and "
        "@vitreajs/vitrea-web, minor. Left bar: one GlassToolbar whose children are partitioned "
        "at a flexible GlassToolbarSpacer and at a sharedBackground=\"hidden\" tinted Publish — "
        "one role=\"toolbar\" and one tab stop, but two sampling groups, so the shared "
        "background breaks and the emphasised action gets a body, a proxy and a blur of its "
        "own. Right bar: the same four items with neither — one group, one continuous "
        "background, with the tint colouring a part of it. "
        "LOOK AT: where the background breaks, and how wide the break is. The spacer measured "
        "min-width: 24px on this run — samplingPaddingFor({members, material}) read from the "
        "resolved policy with Reduce Transparency off, never a constant; turn Reduce "
        "Transparency on and the frost thickens and that number rises."
    )
    panels = [(load(scheme, "toolbar-split.png"), "harness /eye/ · split (left) beside unsplit (right)")]
    if m["playground"] is not None:
        panels.append(
            (
                load(scheme, "live-toolbar-split.png"),
                "the shipped playground's own split toolbar (/playground/)",
            )
        )
    s.row(panels)
    s.rule()

    # ── 2 — tint and ink ───────────────────────────────────────────────────
    s.head("2 · Tinted buttons, a tinted group, and four named ink levels")
    s.body(
        ".changeset/buttons-can-be-tinted.md, a-group-carries-its-seed.md, "
        "four-named-ink-levels.md, the-material-decides-its-own-ink.md. Left to right: "
        "GlassButton tint=\"#ff9500\", tint=\"#0a84ff\", tint=\"rgb(255 149 0 / 50%)\" (the "
        "colour's own alpha is the strength), and an untinted control; then a GlassGroup "
        "tint=\"#30d158\" whose first member inherits the seed and whose second clears it with "
        "tint={null}; then one surface carrying all four ink tokens as text. "
        "LOOK AT: the half-strength button, which is a shade of the seed rather than a fill and "
        "still shows the material through it; the second plate in the green group carrying no "
        "colour at all; and the ink ramp — secondary is raised to whatever holds WCAG 4.5 "
        "against the colour this surface is actually drawing, while tertiary and quaternary "
        "carry no floor by design."
    )
    s.row([(load(scheme, "tint-ink.png"), "harness /eye/ · one row, six sampling groups")])
    s.rule()

    # ── 3 — the material over page content ─────────────────────────────────
    stage_crop = (30, 50, 730, 860)
    native_name = (
        "photo__glass-over-glass__rest.png"
        if scheme == "light"
        else "checkerboard__glass-over-glass__rest.png"
    )
    native_profile = f"apple-macos-26.5-2x-{scheme}-standard"
    s.head("3 · The WebGPU material over ordinary page content")
    s.body(
        ".changeset/page-content-gets-the-material.md — @vitreajs/vitrea-web, minor (W27f G1, "
        "claims §5.131). The same three plates at the same authored thickness, first over this "
        "page's own markup and then over a registered texture, and beside them Apple's own "
        "stacked capture at the matching 2x scale. The site's readout said, for the page stage: "
        + ", ".join(f"{k} {v}" for k, v in m["site"]["readouts"]["page"].items())
        + "; and for the texture stage: "
        + ", ".join(f"{k} {v}" for k, v in m["site"]["readouts"]["material"].items())
        + ". LOOK AT: the body and the rim of the unsampled path against the sampled one — the "
        "derivation is the same profile and the same backdrop-tone law now, but a DOM group "
        "still has no pixels to read, so response and collapse remain unavailable without a "
        "hint. The native capture is a different scene and is here for the overlay's character, "
        "not as a diff."
    )
    s.row(
        [
            (
                load(scheme, "page-stage.png").crop(stage_crop),
                "site /#page · ordinary DOM, nothing declared (cropped, not scaled)",
            ),
            (
                load(scheme, "texture-stage.png").crop(stage_crop),
                "site /#material · registered texture (cropped, not scaled)",
            ),
            (
                Image.open(FIXTURES / native_profile / native_name),
                f"NATIVE, read-only · {native_profile}/{native_name}",
            ),
        ]
    )
    s.rule()

    # ── 4 — presence and the two morph transitions ─────────────────────────
    s.head("4 · Authored presence, and materialize beside matched geometry")
    s.body(
        ".changeset/the-material-can-leave-in-place.md — all three packages, minor (W27d, claims "
        "§5.132). Six frames across present={true} -> {false}, stepped on a hand-driven frame "
        "loop (GlassRoot autoStart={false}, root.runFrame + ticker.advance), so the time under "
        "each frame is that frame's own time at the shipped 220 ms / easeOutCubic. "
        "LOOK AT: the material leaving while the element's opacity stays exactly 1 — presence "
        "scales the optical terms, it never touches opacity — and the label staying where the "
        "app wrote it at presence 0, which is Glass.identity. The ink under that label is still "
        "the material's (X9): that is the limit vibrancy will close, not a bug."
    )
    frames = harness["presence"]["frames"]
    s.row([(load(scheme, Path(f["file"]).name), presence_label(f)) for f in frames])
    s.row(
        [
            (
                load(scheme, "presence-rest.png"),
                "before the flip · materialization "
                f"{harness['presence']['rest']['materialization']:.4f}",
            ),
            (
                load(scheme, "presence-identity.png"),
                f"settled · materialization {harness['presence']['identity']['materialization']:.4f}"
                f" · opacity {harness['presence']['identity']['opacity']} · Glass.identity",
            ),
        ]
        + (
            [
                (load(scheme, "live-presence-on.png"), "playground (live) · present={true}"),
                (
                    load(scheme, "live-presence-identity.png"),
                    "playground (live) · present={false} · opacity "
                    f"{m['playground']['presence']['after']['opacity']} · the retained label",
                ),
            ]
            if m["playground"] is not None
            else []
        )
    )
    s.body(
        "GlassMorph transition=\"materialize\" (top) against the default matchedGeometry "
        "(bottom), both opening, both on the same hand-driven clock. LOOK AT: materialize is "
        "two bodies — the closed end leaves in its own geometry while the platter arrives in "
        "its own — and matchedGeometry is one body travelling between the two shapes.",
        dim=True,
    )
    for name, label in (("morph-materialize", "materialize"), ("morph-matched", "matchedGeometry")):
        s.row(
            [
                (load(scheme, f"{name}-{t:04d}.png"), f"{label} · t = {t:>3} ms")
                for t in (0, 60, 120, 180, 260, 420)
            ]
        )
    s.rule()

    # ── 5 — the lens answering the pointer ─────────────────────────────────
    s.head("5 · The lens answers the pointer")
    s.body(
        ".changeset/the-lens-answers-the-pointer.md — @vitreajs/vitrea-web, minor. One capsule, "
        "at rest, hovered and pressed, on each sampling backend: over ordinary DOM (refraction "
        "resolves approximate) and over a registered texture (refraction true). The renderer "
        "clamped lensStrength at 1 before this cut, so every state that deepens the lens "
        "arrived indistinguishable from rest; the published --vitrea-lens under each frame is "
        "what now reaches the shader. LOOK AT: the rim, where the lens displacement lives. The "
        "movement is small by design — 1.06 hovered, 1.14 pressed — so each state is followed "
        "by its difference from rest, amplified 8x; that panel is derived, every other panel on "
        "this sheet is not."
    )
    for key, what in (("dom", "DOM backdrop · css-backdrop · refraction approximate"),
                      ("texture", "registered texture · gpu-texture · refraction true")):
        rest = load(scheme, f"lens-{key}-rest.png")
        hover = load(scheme, f"lens-{key}-hover.png")
        press = load(scheme, f"lens-{key}-press.png")
        readings = harness["lens"][key]
        s.row(
            [
                (rest, f"{what} · rest · --vitrea-lens {readings['rest']['lens']}"),
                (hover, f"hover · --vitrea-lens {readings['hover']['lens']}"),
                (amplify(hover, rest, 8, theme["bg"]), "|hover − rest| x 8 (derived)"),
                (press, f"press · --vitrea-lens {readings['press']['lens']}"),
                (amplify(press, rest, 8, theme["bg"]), "|press − rest| x 8 (derived)"),
            ]
        )

    s.rule()
    s.body(
        "Not on this sheet: recede-keeps-strength.md (W27c G1 publishes the receded profile "
        "documents; the activation observer and the public windowActivation option are W27c G2 "
        "and were not dispatched, so there is nothing on any page to photograph). The dark "
        "sheet's native panel is the checkerboard stack because the 2x dark profile carries no "
        "photo__glass-over-glass capture. See eye/index.md.",
        dim=True,
    )
    return s.render()


def main() -> None:
    meta = json.loads((PANELS / "meta.json").read_text())
    for scheme in ("light", "dark"):
        sheet = build(scheme, meta)
        out = HERE / f"eye-sheet-{scheme}.png"
        sheet.save(out)
        print(out.name, sheet.size)


if __name__ == "__main__":
    main()
