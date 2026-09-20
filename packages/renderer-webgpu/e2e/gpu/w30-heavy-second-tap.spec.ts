/**
 * W30 G2 — the second heavy tap's ON path, proved to exist on a real adapter.
 *
 * `sizeHeavySecondShare` is the single gate on the whole mechanism: the second
 * heavy texture is allocated, blurred and sampled only where it is non-zero, and
 * it ships at 0. That is what makes the operator cost nothing until §5.159 fits
 * it, and the 34 renderer goldens are what prove the OFF path is the path the
 * material has always taken.
 *
 * A gate nothing ever opens is indistinguishable from a gate wired to nothing,
 * and the goldens cannot tell the two apart — every one of them renders at share
 * 0. So this spec opens it. On a test profile at a non-zero share the rendered
 * bytes must DIFFER from the same scene at the shipped material; at a share of 0
 * with both widths named they must be identical, which is the gate being the
 * share and not the width (W26 Decision Log 6 (c) is what happens when a width
 * is read as a switch); and a negative share must differ from a positive one of
 * the same magnitude, because the weight is signed and the sign is the whole
 * reason candidate (i) can cut a notch a positive mix of Gaussians cannot.
 *
 * The scene is `lens-size-depth`: a registered texture backdrop, so the source
 * carries a pyramid and the heavy path is reachable, over a **32 px** checker at
 * dpr 1 and under a 400 px surface. Both choices are forced. The pitch has to
 * survive the FIRST heavy width (9 device px) or the two widths read the same
 * flat mean and a real difference measures as nothing — `refraction-checkerboard`'s
 * 10 px cell is erased at both and moves one 8-bit code. And the span has to be
 * deep enough that `kScatter` has saturated, because the deep component is what
 * the second tap is mixed into.
 */

import { expect, test, type Page } from "@playwright/test";

import { decodeCapture, openHarness, requireHardwareAdapter } from "../support";

/** A test profile's second heavy tap: a width well clear of the first one's 9. */
const WIDTHS = { sizeHeavySecondSigma: 40, sizeHeavySecondSigma2x: 40 } as const;

const render = (
  page: Page,
  materialProfile: Record<string, number>,
): Promise<{ readonly width: number; readonly height: number; readonly pixels: string }> =>
  page.evaluate(
    (patch) => window.vitrea.renderScene("lens-size-depth", undefined, patch),
    materialProfile,
  );

/** Every byte the optics pass wrote. */
const bytes = (capture: {
  readonly width: number;
  readonly height: number;
  readonly pixels: string;
}): number[] => [...decodeCapture(capture).data];

/** Spread over a raster this size is a reduction, not a spread argument. */
const maxDelta = (a: readonly number[], b: readonly number[]): number => {
  let worst = 0;
  for (let index = 0; index < a.length; index += 1) {
    worst = Math.max(worst, Math.abs((a[index] ?? 0) - (b[index] ?? 0)));
  }
  return worst;
};

/** The brightest colour channel anywhere on the capture. */
const peak = (raster: readonly number[]): number => {
  let brightest = 0;
  for (let index = 0; index < raster.length; index += 1) {
    if (index % 4 !== 3) brightest = Math.max(brightest, raster[index] ?? 0);
  }
  return brightest;
};

test.describe("@gpu W30's second heavy tap (claims §5.156 §3, §5.158)", () => {
  test("draws nothing at the shipped share and something at a fitted one", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));

    const off = bytes(await render(page, {}));
    const widthsOnly = bytes(await render(page, { ...WIDTHS }));
    const negative = bytes(await render(page, { ...WIDTHS, sizeHeavySecondShare: -1 }));
    const positive = bytes(await render(page, { ...WIDTHS, sizeHeavySecondShare: 1 }));

    process.stdout.write(
      `second heavy tap: widths-only Δ ${String(maxDelta(off, widthsOnly))}; ` +
        `share −1 Δ ${String(maxDelta(off, negative))}; ` +
        `share +1 Δ ${String(maxDelta(off, positive))}; ` +
        `sign Δ ${String(maxDelta(negative, positive))}\n`,
    );

    // The scene draws something, so none of the comparisons below can pass by
    // comparing two blank canvases.
    expect(peak(off)).toBeGreaterThan(40);

    // The SHARE is the gate. Two widths named beside a zero share allocate
    // nothing, bind nothing and sample nothing, so the bytes are the shipped
    // material's — exactly, not nearly.
    expect(
      maxDelta(off, widthsOnly),
      "a second heavy WIDTH moved the render while its share was 0 — the gate is not the share",
    ).toBe(0);

    // And the ON path exists. A signed weight on a second, wider Gaussian moves
    // the deep component, so the interior has to move with it.
    expect(
      maxDelta(off, negative),
      "a non-zero second heavy share changed nothing — the ON path is wired to nothing",
    ).toBeGreaterThan(1);
    expect(maxDelta(off, positive)).toBeGreaterThan(1);

    // The weight is SIGNED, which is the whole of why candidate (i) can cut a
    // notch: a negative share subtracts the wider sample where a positive one
    // adds it, so the two land on opposite sides of the shipped material.
    expect(
      maxDelta(negative, positive),
      "the second heavy share's sign made no difference — the mix is not signed",
    ).toBeGreaterThan(1);
  });
});
