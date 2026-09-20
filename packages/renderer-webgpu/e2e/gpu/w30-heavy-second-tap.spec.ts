/**
 * W30 G2 — the three new uniform vec4s, each proved to exist on a real adapter.
 *
 * Three cases, one per vec4, because a vec4 nothing ever reads at a non-zero
 * value is indistinguishable from a vec4 wired to the wrong lanes — which is not
 * hypothetical here: the three were first packed at float offsets 117, 121 and
 * 125, none of them a multiple of four, and the whole unit chain, the 34 goldens
 * and every inertness proof were green over it because every word involved is 0
 * on the landed material (claims §5.158 §6). Only opening a gate could see it,
 * and on the merge only ONE of the three gates had a case (§5.158 §8, finding
 * 2). `scatterHeavy2` is the first case below, `shadowSigma` (floats 120..123)
 * the second and `scatterScale` (124..127) the third.
 *
 * ## The second heavy tap's ON path
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
  materialProfile: Record<string, unknown>,
  scene = "lens-size-depth",
): Promise<{ readonly width: number; readonly height: number; readonly pixels: string }> =>
  page.evaluate(
    ([name, patch]) =>
      window.vitrea.renderScene(name as string, undefined, patch as Record<string, unknown>),
    [scene, materialProfile] as const,
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

/**
 * The same reduction over one vertical band of the raster.
 *
 * A band rather than a mask, because what a per-caster law has to be shown to do
 * is act differently on two casters in ONE capture — and the honest way to say
 * "differently" is to reduce over each caster's own half and compare the two
 * numbers, not to compare either against the whole.
 */
const maxDeltaInBand = (
  a: readonly number[],
  b: readonly number[],
  width: number,
  fromX: number,
  toX: number,
): number => {
  let worst = 0;
  for (let index = 0; index < a.length; index += 4) {
    const x = (index / 4) % width;
    if (x < fromX || x >= toX) continue;
    for (let channel = 0; channel < 4; channel += 1) {
      worst = Math.max(worst, Math.abs((a[index + channel] ?? 0) - (b[index + channel] ?? 0)));
    }
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

/**
 * The same, on the ALPHA channel.
 *
 * The shadow scene has no backdrop, so the pass writes premultiplied black
 * outside the contour and opacity is the whole of what lands on the canvas —
 * `e2e/gpu/shadow-extent.spec.ts`'s reasoning, which is why `peak` would read
 * that scene as blank.
 */
const alphaPeak = (raster: readonly number[]): number => {
  let brightest = 0;
  for (let index = 3; index < raster.length; index += 4) {
    brightest = Math.max(brightest, raster[index] ?? 0);
  }
  return brightest;
};

test.describe("@gpu W30's three operator vec4s (claims §5.156 §2 and §3, §5.158)", () => {
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

  test("grades the shadow's σ by the CASTER's own span, not the group's", async ({ page }) => {
    /*
     * `shadowSigma`, floats 120..123, opened.
     *
     * The law is `σ(span) = sigmaPx + max(sigmaThinOffsetPx, sigmaSlopePerSpan ·
     * (span − sigmaSpanRefPx))`, evaluated in the shader from the casting
     * surface's own span, which rides the field pass's aux target. At the fitted
     * shape — slope 0.133 per CSS px about a reference of 96 (Decision Log 3 (c))
     * — the two halves of `w30-shadow-span` land on opposite sides of that
     * reference: the 44 px caster's arm is `max(0, 0.133 · −52)`, which is the
     * floor's own zero, and the 160 px caster's is +8.5 CSS px of σ.
     *
     * So the assertion is that the two spans' shadows differ FROM EACH OTHER.
     * "The patched render differs from the shipped one" would pass against a law
     * read once per group and applied to every member, which is exactly the
     * mistake this file exists to catch one facet along.
     */
    requireHardwareAdapter(await openHarness(page));

    const SCENE = "w30-shadow-span";
    const shipped = await render(page, {}, SCENE);
    const width = shipped.width;
    const off = bytes(shipped);
    const graded = bytes(
      await render(page, { outerShadow: { sigmaSlopePerSpan: 0.133, sigmaSpanRefPx: 96 } }, SCENE),
    );
    // The control: one width for both casters, moved by the same amount the law
    // moves the thick one. A span-blind σ moves both halves.
    const widened = bytes(await render(page, { outerShadow: { sigmaPx: 24.06 } }, SCENE));

    // The raster is two casters side by side with 160 CSS px of clear air
    // between them; the bands stop well short of each other's reach.
    const THIN = [0, 280] as const;
    const THICK = [300, width] as const;
    const thinLaw = maxDeltaInBand(off, graded, width, THIN[0], THIN[1]);
    const thickLaw = maxDeltaInBand(off, graded, width, THICK[0], THICK[1]);
    const thinWidth = maxDeltaInBand(off, widened, width, THIN[0], THIN[1]);
    const thickWidth = maxDeltaInBand(off, widened, width, THICK[0], THICK[1]);
    process.stdout.write(
      `shadow σ law: span 44 Δ ${String(thinLaw)}, span 160 Δ ${String(thickLaw)}; ` +
        `one width for both: span 44 Δ ${String(thinWidth)}, span 160 Δ ${String(thickWidth)}\n`,
    );

    // The scene draws a shadow at all: the alpha the two groups write is what
    // every comparison here is over.
    expect(alphaPeak(off)).toBeGreaterThan(40);

    // The thick caster's shadow widened, and the thin caster's did not move at
    // all — the law's floor arm, read at the caster's own span.
    expect(
      thickLaw,
      "a fitted σ slope moved nothing at span 160 — the law is not reaching the shader",
    ).toBeGreaterThan(1);
    expect(
      thinLaw,
      "a fitted σ slope moved the span-44 caster, whose arm is max(0, negative) — the span the " +
        "shader reads is not the caster's",
    ).toBe(0);

    // And the thin half is not a dead region: one width for both casters moves
    // it, by more than the noise the case above calls zero.
    expect(thinWidth, "the span-44 half never moves, so its zero above says nothing").toBeGreaterThan(
      1,
    );
    expect(thickWidth).toBeGreaterThan(1);
  });

  test("keys the scatter on the SOURCE's measured scale, at a real statistic", async ({ page }) => {
    /*
     * `scatterScale`, floats 124..127, opened.
     *
     * The shader adds `sizeScatterScaleGain · (statistic − sizeScatterScaleRef)`
     * to `kScatter` and clamps. The statistic is the analysis pass's edge density
     * for the source this group samples, which arrives by readback — so the scene
     * has to run frames for it to exist at all, and `w30-scatter-scale` runs 40
     * over a 32 px checker for that reason. A gain at a zero statistic would be
     * an ON path that draws nothing, which is the same vacuity as the gate that
     * never opens.
     */
    requireHardwareAdapter(await openHarness(page));

    const SCENE = "w30-scatter-scale";
    const off = bytes(await render(page, {}, SCENE));
    const refOnly = bytes(await render(page, { sizeScatterScaleRef: 0.25 }, SCENE));
    const negative = bytes(await render(page, { sizeScatterScaleGain: -2.5 }, SCENE));
    const positive = bytes(await render(page, { sizeScatterScaleGain: 2.5 }, SCENE));

    process.stdout.write(
      `scatter scale: reference-only Δ ${String(maxDelta(off, refOnly))}; ` +
        `gain −2.5 Δ ${String(maxDelta(off, negative))}; ` +
        `gain +2.5 Δ ${String(maxDelta(off, positive))}; ` +
        `sign Δ ${String(maxDelta(negative, positive))}\n`,
    );

    expect(peak(off)).toBeGreaterThan(40);

    // The GAIN is the gate, exactly as the share is for the second heavy tap: a
    // reference named beside a zero gain multiplies into nothing.
    expect(
      maxDelta(off, refOnly),
      "a scatter scale REFERENCE moved the render while its gain was 0 — the gate is not the gain",
    ).toBe(0);

    // And the ON path exists, at a statistic the analysis pass actually measured.
    expect(
      maxDelta(off, negative),
      "a non-zero scatter scale gain changed nothing — either the ON path is wired to nothing or " +
        "the source's edge density never reached the shader",
    ).toBeGreaterThan(1);
    expect(maxDelta(off, positive)).toBeGreaterThan(1);
    // Signed, so the two gains land on opposite sides of the shipped material.
    expect(maxDelta(negative, positive)).toBeGreaterThan(1);
  });
});
