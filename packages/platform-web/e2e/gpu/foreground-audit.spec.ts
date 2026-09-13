/**
 * The GPU tier's own foreground, measured rather than assumed (Decision Log
 * #32(b)).
 *
 * K5 found that a foreground rule expressed against the *backdrop* stops
 * describing what a reader sees once the material's opacity crosses a line: at
 * `tintAlpha` 0.62 the glyphs sit on the tint, not on the backdrop, so a
 * `tone: "dark"` hint mapped straight to the light ink produced near-white ink on
 * a near-white surface (measured WCAG 1.24). The CSS tier was corrected. The
 * parent handed the GPU tier's half of the same question here with the order of
 * operations fixed: **measure first, fix only if the defect reproduces.**
 *
 * The scene is the one an app actually hits — the demo's own shape: a dom-backdrop
 * group over dark page content, with `hint: { tone: "dark" }`, on the WebGPU tier,
 * and a host that reads `--vitrea-foreground` with its own ink as the fallback
 * (which is what the fixture page's `.glass-host` does, and what both READMEs
 * document). The measurement is a page screenshot, because the composite is the
 * page plus the optics canvas plus the label, and only the compositor has all
 * three.
 */

import { expect, test } from "@playwright/test";

import { gotoHarness, requireHardwareAdapter, sample, type Rgb } from "../support";

const PANEL = { x: 300, y: 200, width: 220, height: 120 };

/** WCAG AA for body text — the floor the CSS tier's own pixel test holds. */
const BODY_FLOOR = 4.5;

const linear = (channel: number): number => {
  const value = channel / 255;
  return value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
};

const luminanceOf = (rgb: Rgb): number =>
  0.2126 * linear(rgb.r) + 0.7152 * linear(rgb.g) + 0.0722 * linear(rgb.b);

interface Ink extends Rgb {
  readonly alpha: number;
}

const parseInk = (declaration: string): Ink => {
  const match = /(\d+),\s*(\d+),\s*(\d+)(?:,\s*([\d.]+))?/.exec(declaration);
  if (match === null) throw new Error(`not an rgb() declaration: ${declaration}`);
  return {
    r: Number(match[1]),
    g: Number(match[2]),
    b: Number(match[3]),
    alpha: match[4] === undefined ? 1 : Number(match[4]),
  };
};

/**
 * What a glyph of this ink actually leaves on this surface.
 *
 * The ink is TRANSLUCENT since W27e G2 — Apple's automatic label colour is black
 * at α 0.847059 over a bright surface, white at α 0.804706 over a dark one, not
 * an opaque hex — so its own three channels are not what a reader sees. The
 * composite is taken in encoded sRGB, which is the space the browser composites
 * text in; dropping the alpha would score pure black or pure white against the
 * material and report a contrast no glyph on it has. A contrast test can only
 * ever be wrong in the flattering direction here, which is the one direction it
 * must not be.
 */
const compositeOver = (ink: Ink, surface: Rgb): Rgb => ({
  r: ink.alpha * ink.r + (1 - ink.alpha) * surface.r,
  g: ink.alpha * ink.g + (1 - ink.alpha) * surface.g,
  b: ink.alpha * ink.b + (1 - ink.alpha) * surface.b,
});

const contrastOf = (a: number, b: number): number =>
  (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);

test("a dark-hinted GPU-tier surface's label holds the body-text floor", async ({ page }) => {
  await gotoHarness(page);
  requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));

  const built = await page.evaluate(async (panel) => {
    await window.h.createRoot({ renderer: "webgpu" });
    window.h.addGroup("g", { backdrop: { tone: "dark" } });
    window.h.addSurface({
      groupId: "g",
      nodeId: "panel",
      left: panel.x,
      top: panel.y,
      width: panel.width,
      height: panel.height,
      radius: 26,
      label: "Publish",
    });
    window.h.frame(3);
    return { state: window.h.capabilities("g"), style: window.h.hostStyle("panel") };
  }, PANEL);

  // The tier under test, not the fallback: without this the assertion below would
  // be the CSS tier's, which K5 already corrected.
  expect(built.state?.activeRenderer, `resolved ${JSON.stringify(built.state)}`).toBe("webgpu");

  const ink = parseInk(built.style?.color ?? "");

  // The surface, sampled at four interior points well clear of the centred glyphs
  // so the reading is material rather than type. The worst is the one that counts.
  // Each point gets its own composite rather than a representative one: the ink
  // is translucent, so what a glyph reads as differs wherever the material does.
  const panel = await sample(page, PANEL);
  const points = [
    [40, 30],
    [180, 30],
    [40, 90],
    [180, 90],
  ] as const;
  const ratios = points.map(([x, y]) => {
    const surface = panel.at(x, y);
    return contrastOf(luminanceOf(compositeOver(ink, surface)), luminanceOf(surface));
  });
  const worst = Math.min(...ratios);

  expect(
    worst,
    `ink ${built.style?.color ?? "?"} (published foreground: ${
      built.style?.foreground === "" ? "none" : (built.style?.foreground ?? "?")
    }) against the rendered surface; ratios ${ratios.map((r) => r.toFixed(2)).join(", ")}`,
  ).toBeGreaterThanOrEqual(BODY_FLOOR);
});

test("the GPU tier publishes the same foreground token the CSS tier does", async ({ page }) => {
  // Tier coherence on the one axis a reader cannot recover from: the same app,
  // the same hint, two tiers. K5 made the CSS tier answer this; a GPU tier that
  // publishes nothing leaves the app's own fallback to carry it, which is how the
  // ratio above goes wrong without any code being wrong on its own terms.
  await gotoHarness(page);
  requireHardwareAdapter(await page.evaluate(() => window.h.adapter()));

  const build = async (renderer: "webgpu" | "css"): Promise<string | undefined> =>
    page.evaluate(async ([mode, panel]) => {
      await window.h.createRoot({ renderer: mode as "webgpu" | "css" });
      window.h.addGroup("g", { backdrop: { tone: "dark" } });
      window.h.addSurface({
        groupId: "g",
        nodeId: "panel",
        left: (panel as typeof PANEL).x,
        top: (panel as typeof PANEL).y,
        width: (panel as typeof PANEL).width,
        height: (panel as typeof PANEL).height,
        radius: 26,
        label: "Publish",
      });
      window.h.frame(3);
      return window.h.hostStyle("panel")?.foreground;
    }, [renderer, PANEL] as const);

  const gpu = await build("webgpu");
  await page.reload();
  await page.waitForSelector("html[data-harness-ready='1']");
  const css = await build("css");

  // Apple's automatic label colour through the vibrancy operator: pure black at
  // Apple's own 0.847059 (W27e G2; W27 Decision Log 15 (a)). It was `#1c1c1e`
  // opaque, which is a different platform's ink at a different opacity.
  expect(css, "the CSS tier's answer").toBe("rgb(0 0 0 / 0.847059)");
  expect(gpu, "the GPU tier's answer").toBe(css);
});
