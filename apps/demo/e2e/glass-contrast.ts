/**
 * Text contrast over live glass, measured on the rendered pixels.
 *
 * Shared by the site's contrast suite and by the GPU-only cases, which need the
 * same reading on a real adapter. It lives beside them rather than inside either,
 * because a measurement duplicated into two suites drifts and the two answers then
 * disagree about a floor neither of them owns.
 *
 * The method, and why each half of it is what it is:
 *
 * axe cannot answer this. Its contrast rule needs a computable background, and
 * every label on this page's glass sits on a translucent material over a canvas or
 * a page's own markup, so axe reports "incomplete" and moves on. For the front page
 * of a library whose whole accessibility claim is that the material respects the
 * reader, an unchecked "incomplete" is not good enough.
 *
 * So: the ink is the element's *computed* `color` — whatever the runtime resolved
 * this frame, painted through a canvas and read back, because a colour authored in
 * OKLCH serialises as `oklch(...)` and no arithmetic over that string is a
 * luminance. The surface is the median luminance of the element's own rendered
 * pixels, which on a control is overwhelmingly material rather than type. A
 * percentile pair would not do: on an 80x44 button the glyphs are about six per
 * cent of the area, so both tails describe the surface and the ratio comes out
 * flattering and wrong.
 */

import type { Locator, Page } from "@playwright/test";
import { PNG } from "pngjs";

/** WCAG AA: 4.5:1 for body text, 3:1 for large text. */
export const BODY_FLOOR = 4.5;
export const LARGE_FLOOR = 3;

/** Phases of the backdrop's drift, in ms. It has a nine-second period. */
export const SAMPLE_DELAYS = [400, 2200, 4200, 6200];

const channel = (value: number): number => {
  const v = value / 255;
  return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
};

export const luminance = (r: number, g: number, b: number): number =>
  0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);

export const contrast = (a: number, b: number): number =>
  (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);

export type Channels = readonly [number, number, number];

/**
 * The ink, **with its alpha**, painted through a canvas because a colour authored
 * in OKLCH or produced by `color-mix()` serialises as a function call and no
 * arithmetic over that string is a luminance.
 *
 * The alpha is not decoration. A semi-transparent ink is a real and useful way to
 * express a recessed state — it dims toward whatever is behind it in either colour
 * scheme — but its contrast is the contrast of the *composite*, and this harness
 * used to drop the alpha channel on the floor and report the ratio of the fully
 * opaque colour. That would have scored a translucent label as if it were solid,
 * which is a blind spot pointing the one direction a contrast test must never be
 * wrong in: it can only ever flatter. Found in C9d while re-deriving the disabled
 * control's ink, and closed before that ink was chosen.
 */
export async function inkOf(target: Locator): Promise<readonly { readonly rgb: Channels; readonly alpha: number }[]> {
  return target.evaluate((element) => {
    /*
     * Every element that actually paints glyphs, not just the one that was
     * selected. A control may hold its label in a child — this page's disabled
     * state does — and then the host's computed colour is not the colour a reader
     * sees. Measuring the selected element alone would score the ink the app
     * *stopped* using.
     */
    const painters: Element[] = [];
    const walk = (node: Element): void => {
      const ownText = [...node.childNodes].some(
        (child) => child.nodeType === Node.TEXT_NODE && (child.textContent ?? "").trim() !== "",
      );
      if (ownText) painters.push(node);
      for (const child of node.children) walk(child);
    };
    walk(element);
    if (painters.length === 0) painters.push(element);

    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    const context = canvas.getContext("2d");
    if (context === null) return [{ rgb: [0, 0, 0] as Channels, alpha: 1 }];

    // Painted over an opaque white and an opaque black: the pair recovers the
    // colour and its alpha exactly, without depending on how the 2D context
    // rounds a partially transparent single fill.
    const read = (colour: string, ground: string): Channels => {
      context.clearRect(0, 0, 1, 1);
      context.fillStyle = ground;
      context.fillRect(0, 0, 1, 1);
      context.fillStyle = colour;
      context.fillRect(0, 0, 1, 1);
      const data = context.getImageData(0, 0, 1, 1).data;
      return [data[0] ?? 0, data[1] ?? 0, data[2] ?? 0];
    };

    return painters.map((painter) => {
      const colour = getComputedStyle(painter).color;
      const onBlack = read(colour, "#000");
      const onWhite = read(colour, "#fff");
      // over(c, g) = a·c + (1−a)·g, so the white/black gap is (1−a)·255 per channel.
      const gap = (onWhite[1] ?? 0) - (onBlack[1] ?? 0);
      const alpha = Math.max(0, Math.min(1, 1 - gap / 255));
      const rgb: Channels =
        alpha === 0
          ? [0, 0, 0]
          : ([0, 1, 2].map((c) => (onBlack[c] ?? 0) / alpha) as unknown as Channels);
      return { rgb, alpha };
    });
  });
}

/**
 * The surface's median-luminance pixel, as a colour rather than as a number.
 *
 * A colour because the ink may be composited over it, and compositing is
 * per-channel in encoded sRGB. Median rather than a percentile pair: on an 80x44
 * button the glyphs are about six per cent of the area, so both tails describe the
 * surface and the ratio comes out flattering and wrong.
 */
export async function surfaceOf(target: Locator): Promise<Channels> {
  const png = PNG.sync.read(await target.screenshot());
  const pixels: { readonly rgb: Channels; readonly y: number }[] = [];
  for (let i = 0; i < png.data.length; i += 4) {
    if ((png.data[i + 3] ?? 0) < 200) continue;
    const rgb: Channels = [png.data[i] ?? 0, png.data[i + 1] ?? 0, png.data[i + 2] ?? 0];
    pixels.push({ rgb, y: luminance(rgb[0], rgb[1], rgb[2]) });
  }
  pixels.sort((a, b) => a.y - b.y);
  return pixels[Math.floor(pixels.length / 2)]?.rgb ?? [0, 0, 0];
}

/** The ink as it actually reaches the eye: composited over the surface it sits on. */
export function inkOver(
  ink: { readonly rgb: Channels; readonly alpha: number },
  surface: Channels,
): number {
  const channel = (index: 0 | 1 | 2): number =>
    ink.alpha * (ink.rgb[index] ?? 0) + (1 - ink.alpha) * (surface[index] ?? 0);
  return luminance(channel(0), channel(1), channel(2));
}

/** The worst ratio any matching element reaches right now, as the page stands. */
export async function worstNow(
  page: Page,
  selector: string,
  when: string,
): Promise<{ ratio: number; where: string }> {
  let worst = { ratio: Number.POSITIVE_INFINITY, where: selector };
  for (const target of await page.locator(selector).all()) {
    const surface = await surfaceOf(target);
    const surfaceLuminance = luminance(surface[0], surface[1], surface[2]);
    // The worst painter on the element: a control whose label is a child is
    // measured on the child's ink, and one with several is measured on the
    // weakest of them.
    const found = Math.min(
      ...(await inkOf(target)).map((ink) => contrast(inkOver(ink, surface), surfaceLuminance)),
    );
    if (found >= worst.ratio) continue;
    const label = (await target.innerText()).trim().replace(/\s+/g, " ") || selector;
    worst = { ratio: found, where: `${label} ${when}` };
  }
  return worst;
}

/** The worst ratio any matching element reaches across the sampled phases. */
export async function worstRatio(page: Page, selector: string): Promise<{ ratio: number; where: string }> {
  let worst = { ratio: Number.POSITIVE_INFINITY, where: selector };
  for (const delay of SAMPLE_DELAYS) {
    await page.waitForTimeout(delay);
    const found = await worstNow(page, selector, `at +${delay}ms`);
    if (found.ratio < worst.ratio) worst = found;
  }
  return worst;
}

