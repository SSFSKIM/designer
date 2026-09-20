/**
 * W30 G3b — the surface draws everywhere it declared, at a thin σ (claims
 * §5.159b).
 *
 * The outer shadow's falloff is a `tanh` of a cubic in the distance measured in
 * σ, and the cubic reaches f32's `exp` overflow at about ten σ inside the
 * shadow's silhouette. A backend that lowers `tanh` through `exp` — Metal's
 * fast-math path does — returned NaN there, and the NaN travelled into the
 * composite's alpha, so a strip of the SURFACE went undrawn. Nothing caught it
 * for the whole life of the project because every σ vitrea had shipped was above
 * 10 CSS px and ten σ was further than any caster is deep. macOS 27's law draws
 * σ = 2.13 at a span-44 caster, where ten σ is 21.4 CSS px and a 44 px capsule's
 * own centre line is 25 CSS px inside its silhouette.
 *
 * So the 34 goldens cannot see this and never could: they render at the macOS
 * 26.5 σ of 15.55, where the argument peaks at about 2 and the curve is nowhere
 * near an overflow. **The case that sees it has to name a thin σ**, and this one
 * names the macOS 27 light document's own fitted law.
 *
 * What it asserts is W20's clause on one raster: the drawn silhouette — alpha
 * at or above half of what the material composites at — must CONTAIN the
 * declared region and agree with it to an IoU of 0.99. That is the bound the
 * calibration harness reads per cell (`declared-conformance.test.ts`, the alpha
 * extractor at threshold 0.5), read here on a scene the renderer package owns,
 * so the renderer's own suite fails on a defect that used to be visible only
 * from the calibration bed.
 *
 * Before the fix this case reads **652 of the capsule's 4,780 declared pixels
 * undrawn (IoU 0.8636) and 132 of the toolbar's 4,308 (IoU 0.9694)**, and the σ
 * sweep below reads 0 / 0 / 784 / 784 across σ 15.55, 8.96, 2.1272 and the law
 * — the numbers §5.159b records as the fail-before. The capsule's 652 is the
 * same 652 the calibration harness measures on
 * `checkerboard__capsule-button__rest` over a transparent page.
 */

import { expect, test, type Page } from "@playwright/test";

import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

/**
 * The macOS 27 light document's outer shadow, as W30 G3 sealed it — the σ law,
 * its reference and floor, and the geometry the law is read beside.
 *
 * Named here rather than imported from `packages/calibration/profiles`: this
 * package does not depend on that one, and a case that silently followed a
 * document as it is refitted would stop being a case about a thin σ the day the
 * fit moved. σ(44) = 8.96 + max(−6.8328, 0.1314 · (44 − 96)) = 2.1272.
 */
const THIN_SIGMA_SHADOW = {
  outerShadow: {
    sigmaPx: 8.96,
    sigmaSlopePerSpan: 0.1314,
    sigmaSpanRefPx: 96,
    sigmaThinOffsetPx: -6.8328,
    offsetPx: 7.95,
    spreadPx: 3.1,
    thinOcclusionMid: 0.068,
    thinOcclusionBright: 0.0683,
    thickOcclusionAt96: 0.1158,
    thickOcclusionAt128: 0.1827,
    thickOcclusionAt160: 0.26,
  },
} as const;

/** The scene's declared regions, in CSS px — `scenes.ts`'s own numbers. */
const CAPSULE = { cx: 160, cy: 70, w: 120, h: 44, r: 22 } as const;
const TOOLBAR = [104, 160, 216].map((cx) => ({ cx, cy: 200, w: 44, h: 44, r: 22 }));

interface Region {
  readonly cx: number;
  readonly cy: number;
  readonly w: number;
  readonly h: number;
  readonly r: number;
}

/** The signed distance to a rounded rectangle, CSS px, negative inside. */
const roundedRectDistance = (x: number, y: number, region: Region): number => {
  const dx = Math.abs(x - region.cx) - (region.w / 2 - region.r);
  const dy = Math.abs(y - region.cy) - (region.h / 2 - region.r);
  const ox = Math.max(dx, 0);
  const oy = Math.max(dy, 0);
  return Math.min(Math.max(dx, dy), 0) + Math.hypot(ox, oy) - region.r;
};

/**
 * The declared region as pixel indices.
 *
 * A pixel counts as declared when its CENTRE is at least half a pixel inside the
 * contour, which is the same rule that keeps the antialiased ring out of the
 * calibration harness's declared mask: a partially covered pixel is evidence
 * about the contour, not about coverage, and the clause this case exists for is
 * about the interior.
 */
const declaredPixels = (regions: readonly Region[], width: number): number[] => {
  const out: number[] = [];
  for (const region of regions) {
    const x0 = Math.floor(region.cx - region.w / 2) - 1;
    const x1 = Math.ceil(region.cx + region.w / 2) + 1;
    const y0 = Math.floor(region.cy - region.h / 2) - 1;
    const y1 = Math.ceil(region.cy + region.h / 2) + 1;
    for (let y = y0; y <= y1; y += 1) {
      for (let x = x0; x <= x1; x += 1) {
        if (roundedRectDistance(x + 0.5, y + 0.5, region) <= -0.5) out.push(y * width + x);
      }
    }
  }
  return out;
};

/**
 * The drawn silhouette: alpha at or above half the material's own composited
 * alpha, which is what an `{ kind: "alpha", threshold: 0.5 }` extractor reads
 * once the scale is taken off a layer that is not opaque. The scale is the
 * capture's own maximum rather than 255, because this scene has no backdrop and
 * the optics pass emits the material's tint at its own alpha (`field-mask`'s
 * note), which is well under one.
 */
const drawnPixels = (raster: Raster): { readonly set: Set<number>; readonly peak: number } => {
  let peak = 0;
  for (let i = 3; i < raster.data.length; i += 4) peak = Math.max(peak, raster.data[i] ?? 0);
  const cutoff = peak / 2;
  const set = new Set<number>();
  for (let i = 0; i < raster.width * raster.height; i += 1) {
    if ((raster.data[i * 4 + 3] ?? 0) >= cutoff) set.add(i);
  }
  return { set, peak };
};

const render = (
  page: Page,
  patch: Record<string, unknown> = THIN_SIGMA_SHADOW,
): Promise<{ width: number; height: number; pixels: string }> =>
  page.evaluate(
    ([name, material]) =>
      window.vitrea.renderScene(name as string, undefined, material as Record<string, unknown>),
    ["w30-thin-sigma-coverage", patch] as const,
  );

/**
 * The declaration's own clause, read the way the calibration harness reads it:
 * BOUNDED to the declared component region. Outside it nothing is recovered —
 * the exterior there is the shadow, which is a facet and not a silhouette — so
 * the union is the declaration and the IoU is the fraction of it that carries
 * material.
 */
const conformance = (
  raster: Raster,
  regions: readonly Region[],
): { readonly undrawn: number; readonly declared: number; readonly iou: number } => {
  const declared = declaredPixels(regions, raster.width);
  const { set } = drawnPixels(raster);
  let intersection = 0;
  for (const index of declared) if (set.has(index)) intersection += 1;
  return {
    undrawn: declared.length - intersection,
    declared: declared.length,
    iou: intersection / declared.length,
  };
};

test.describe("@gpu the surface draws everywhere it declared, at a thin σ", () => {
  test("a 44 px capsule and a 44 px toolbar are drawn whole under macOS 27's σ law", async ({
    page,
  }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const raster = decodeCapture(await render(page));

    // The material composited something: a blank canvas would pass every
    // containment clause below by having no drawn pixels to disagree with.
    const { peak } = drawnPixels(raster);
    expect(peak, "the optics pass wrote no alpha at all").toBeGreaterThan(16);

    const capsule = conformance(raster, [CAPSULE]);
    expect(
      capsule.undrawn,
      `capsule: ${capsule.undrawn} of ${capsule.declared} declared px undrawn, IoU ${capsule.iou.toFixed(4)}`,
    ).toBe(0);
    expect(capsule.iou, "capsule declaration conformance").toBeGreaterThanOrEqual(0.99);

    const toolbar = conformance(raster, TOOLBAR);
    expect(
      toolbar.undrawn,
      `toolbar: ${toolbar.undrawn} of ${toolbar.declared} declared px undrawn, IoU ${toolbar.iou.toFixed(4)}`,
    ).toBe(0);
    expect(toolbar.iou, "toolbar declaration conformance").toBeGreaterThanOrEqual(0.99);
  });

  /**
   * The invariant behind the clause, stated where a future σ cannot escape it:
   * **the shadow's blur does not decide what the surface covers.**
   *
   * The outer shadow sits UNDER the material and is clipped out of the border
   * box, exactly as a `box-shadow` is, so a group's drawn silhouette is the same
   * set of pixels at every σ. Sweeping σ over the macOS 26.5 value, the macOS 27
   * thick anchor and the macOS 27 thin regime is what makes this a case about
   * the law rather than about one fitted number — the first two pass on the
   * unfixed renderer and the third does not, and the defect is precisely that
   * the three disagreed.
   */
  test("the drawn silhouette is the same at every σ", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const flat = (sigmaPx: number): Record<string, unknown> => ({
      outerShadow: {
        ...THIN_SIGMA_SHADOW.outerShadow,
        sigmaPx,
        sigmaSlopePerSpan: 0,
        sigmaSpanRefPx: 0,
        sigmaThinOffsetPx: 0,
      },
    });

    const areas = new Map<string, number>();
    for (const [label, patch] of [
      ["macOS 26.5, σ 15.55", flat(15.55)],
      ["macOS 27 at span 96, σ 8.96", flat(8.96)],
      ["macOS 27 at span 44, σ 2.13", flat(2.1272)],
      ["macOS 27's law, σ(44) = 2.13", THIN_SIGMA_SHADOW as unknown as Record<string, unknown>],
    ] as const) {
      const raster = decodeCapture(await render(page, patch));
      areas.set(label, conformance(raster, [CAPSULE, ...TOOLBAR]).undrawn);
    }

    const report_ = [...areas].map(([label, undrawn]) => `${label}: ${undrawn}`).join(" | ");
    for (const [, undrawn] of areas) expect(undrawn, report_).toBe(0);
  });
});
