/**
 * Text contrast over live glass, measured on the rendered pixels.
 *
 * axe cannot answer this. Its contrast rule needs a computable background, and every
 * label on this page's glass sits on a translucent material over an animating
 * canvas, so axe reports "incomplete" and moves on. For the front page of a library
 * whose whole accessibility claim is that the material respects the reader, an
 * unchecked "incomplete" is not good enough.
 *
 * So: the ink is the element's *computed* `color` — whatever the runtime resolved
 * this frame, painted through a canvas and read back, because a colour authored in
 * OKLCH serialises as `oklch(...)` and no arithmetic over that string is a
 * luminance. The surface is the median luminance of the element's own rendered
 * pixels, which on a control is overwhelmingly material rather than type. A
 * percentile pair would not do: on an 80x44 button the glyphs are about six per cent
 * of the area, so both tails describe the surface and the ratio comes out flattering
 * and wrong.
 *
 * Sampled at several points in the backdrop's drift, and the worst is the one that
 * counts. The field moves, so a single sample measures one moment rather than the
 * page.
 */

import { expect, test, type Locator, type Page } from "@playwright/test";
import { PNG } from "pngjs";

/** WCAG AA: 4.5:1 for body text, 3:1 for large text. */
const BODY_FLOOR = 4.5;
const LARGE_FLOOR = 3;

/** Phases of the backdrop's drift, in ms. It has a nine-second period. */
const SAMPLE_DELAYS = [400, 2200, 4200, 6200];

const channel = (value: number): number => {
  const v = value / 255;
  return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
};

const luminance = (r: number, g: number, b: number): number =>
  0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b);

const contrast = (a: number, b: number): number =>
  (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);

type Channels = readonly [number, number, number];

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
async function inkOf(target: Locator): Promise<readonly { readonly rgb: Channels; readonly alpha: number }[]> {
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
async function surfaceOf(target: Locator): Promise<Channels> {
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
function inkOver(
  ink: { readonly rgb: Channels; readonly alpha: number },
  surface: Channels,
): number {
  const channel = (index: 0 | 1 | 2): number =>
    ink.alpha * (ink.rgb[index] ?? 0) + (1 - ink.alpha) * (surface[index] ?? 0);
  return luminance(channel(0), channel(1), channel(2));
}

/** The worst ratio any matching element reaches right now, as the page stands. */
async function worstNow(
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
async function worstRatio(page: Page, selector: string): Promise<{ ratio: number; where: string }> {
  let worst = { ratio: Number.POSITIVE_INFINITY, where: selector };
  for (const delay of SAMPLE_DELAYS) {
    await page.waitForTimeout(delay);
    const found = await worstNow(page, selector, `at +${delay}ms`);
    if (found.ratio < worst.ratio) worst = found;
  }
  return worst;
}

async function showSection(page: Page, id: string): Promise<void> {
  await page.goto("/?renderer=css");
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await page.evaluate((target) => {
    document.getElementById(target)?.scrollIntoView({ block: "center", behavior: "instant" });
  }, id);
  await expect(page.locator(`#${id}`)).toHaveAttribute("data-current", "");

  /*
   * Wait for the material to exist before measuring it, rather than for a clock.
   *
   * Every sample below is folded into a MINIMUM, so one reading taken before the
   * tier has materialized a surface is not a slow start, it is a permanent
   * result: the glass is unpainted, the screenshot is the stage's dark ground,
   * and the ratio it reports is about 1:1 whatever the page does afterwards. The
   * first sample used to be a 400ms timeout, which held on a warm dev server and
   * did not on a cold one — the suite failed on the first run in a fresh
   * worktree and passed on every run after it, which is the signature of a test
   * measuring the server rather than the page.
   *
   * `--vitrea-tint` is the CSS tier's own statement that it has written this
   * host's material, and this file always asks for that tier by query string, so
   * it is the honest ready signal rather than a proxy for one.
   */
  await expect
    .poll(() =>
      page.evaluate(() =>
        [...document.querySelectorAll<HTMLElement>("[data-vitrea-node]")].filter(
          (host) => host.style.getPropertyValue("--vitrea-tint") !== "",
        ).length,
      ),
    )
    .toBeGreaterThan(0);
}

test("control labels on glass hold the body-text floor", async ({ page }) => {
  await showSection(page, "behavior");
  const worst = await worstRatio(page, ".control");
  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(BODY_FLOOR);
});

test("segment labels on glass hold the body-text floor, selected and not", async ({ page }) => {
  await showSection(page, "behavior");
  const worst = await worstRatio(page, ".segment");
  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(BODY_FLOOR);
});

test("the plates' labels hold the large-text floor", async ({ page }) => {
  await showSection(page, "material");
  const worst = await worstRatio(page, ".plate strong");
  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(LARGE_FLOOR);
});

/*
 * The backdrop tone stage, at every position the reader can put it in (W7).
 *
 * This is the case the axis needs and the others cannot cover. Backdrop tone
 * adaptation moves a surface's body all the way from a light glass plate to the
 * backdrop's own level, and the runtime re-chooses the ink against it somewhere in
 * the middle — so the label's contrast is not a property of the page, it is a
 * function of a control, and the only honest way to hold it to a floor is to walk
 * the control. The crossing is per surface: the 40px plate flips near 0.05 and the
 * 68px one near 0.01, so the worst reading is never at either end.
 *
 * No phase sampling here, unlike the cases above. The tone stage's ground is flat
 * and still by construction — the drifting field is off, which is what makes the
 * convergence exact — so there is no drift to catch, and what varies instead is
 * the one thing this loop varies.
 */
test("the plates' labels hold the large-text floor at every ground level", async ({ page }) => {
  await showSection(page, "tone");

  const slider = page.getByTestId("ground-level");
  let worst = { ratio: Number.POSITIVE_INFINITY, where: "" };
  for (let value = 2; value <= 160; value += 8) {
    await slider.fill(String(value));
    await expect(page.getByTestId("ground-level-readout")).toContainText(
      `${(value / 1000).toFixed(3)} linear`,
    );
    // Past the material transition, so the reading is the settled surface rather
    // than a frame the reader never stops on.
    await page.waitForTimeout(320);
    const found = await worstNow(page, ".plate strong", `at ground ${(value / 1000).toFixed(3)}`);
    if (found.ratio < worst.ratio) worst = found;
  }

  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(LARGE_FLOOR);
});
