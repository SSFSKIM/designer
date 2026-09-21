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
 * declared region and agree with it to 0.99. (That clause said "IoU" until
 * 2026-09-21; the number is CONTAINMENT, and the helper's note below says what
 * the difference is and which recorded figures are unaffected — review closure,
 * claims §5.163 §8, finding N2.) That is the bound the
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
 *
 * **The third case sweeps the other axis: depth** (review closure; claims
 * §5.159b §10, finding 11). σ and depth enter the overflow only as their ratio,
 * and the two cases above hold the depth at 44 CSS px, so nothing here said
 * that the defect reaches the material the package still ships as
 * `macos26MaterialProfileDocument`. It does — at σ 15.55 the overflow sits
 * 153.35 CSS px inside the silhouette — and the case reads **1,156 of 114,356
 * declared pixels undrawn (IoU 0.9899)** on the unfixed renderer at that σ,
 * measured by unclamping the shader on this branch and re-running.
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
/** `w30-deep-caster-coverage`'s single surface, likewise. */
const DEEP = { cx: 210, cy: 220, w: 340, h: 340, r: 36 } as const;

/**
 * The macOS 26.5 σ, span-invariant, with this document's thick anchors: the
 * material 0.20.0 still ships as `macos26MaterialProfileDocument`.
 */
const MACOS_26_5_SIGMA = 15.55;

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
  scene = "w30-thin-sigma-coverage",
): Promise<{ width: number; height: number; pixels: string }> =>
  page.evaluate(
    ([name, material]) =>
      window.vitrea.renderScene(name as string, undefined, material as Record<string, unknown>),
    [scene, patch] as const,
  );

/**
 * The σ law switched off at one width, which is what "a σ" means here: the two
 * law leaves zeroed and the floor with them, so `outerShadowSigmaPx` returns
 * `sigmaPx` at every span.
 */
const flatSigma = (sigmaPx: number): Record<string, unknown> => ({
  outerShadow: {
    ...THIN_SIGMA_SHADOW.outerShadow,
    sigmaPx,
    sigmaSlopePerSpan: 0,
    sigmaSpanRefPx: 0,
    sigmaThinOffsetPx: 0,
  },
});

/**
 * The declaration's own clause, read the way the calibration harness reads it:
 * BOUNDED to the declared component region. Outside it nothing is recovered —
 * the exterior there is the shadow, which is a facet and not a silhouette — so
 * what is measured is the fraction of the DECLARATION that carries material.
 *
 * **The field was called `iou` until 2026-09-21** (review closure; claims
 * §5.163 §8, finding N2). `intersection / declared.length` is containment —
 * recall over the declared mask, identically `1 − undrawn/declared` — and not an
 * intersection over union: the union would add the drawn pixels outside the
 * declaration, which are deliberately not counted. The numbers §5.159b recorded
 * off this case, and the module note above with them (0.8636 and 0.9694 for the
 * capsule and the toolbar, 0.9899 for the deep caster), are unchanged and stay
 * as recorded; only what the column is CALLED is corrected. Over-draw remains
 * invisible to this number, by construction and as it always was.
 */
const conformance = (
  raster: Raster,
  regions: readonly Region[],
): { readonly undrawn: number; readonly declared: number; readonly containment: number } => {
  const declared = declaredPixels(regions, raster.width);
  const { set } = drawnPixels(raster);
  let intersection = 0;
  for (const index of declared) if (set.has(index)) intersection += 1;
  return {
    undrawn: declared.length - intersection,
    declared: declared.length,
    containment: intersection / declared.length,
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
      `capsule: ${capsule.undrawn} of ${capsule.declared} declared px undrawn, ` +
        `containment ${capsule.containment.toFixed(4)}`,
    ).toBe(0);
    expect(capsule.containment, "capsule declaration conformance").toBeGreaterThanOrEqual(0.99);

    const toolbar = conformance(raster, TOOLBAR);
    expect(
      toolbar.undrawn,
      `toolbar: ${toolbar.undrawn} of ${toolbar.declared} declared px undrawn, ` +
        `containment ${toolbar.containment.toFixed(4)}`,
    ).toBe(0);
    expect(toolbar.containment, "toolbar declaration conformance").toBeGreaterThanOrEqual(0.99);
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

    const areas = new Map<string, number>();
    for (const [label, patch] of [
      ["macOS 26.5, σ 15.55", flatSigma(MACOS_26_5_SIGMA)],
      ["macOS 27 at span 96, σ 8.96", flatSigma(8.96)],
      ["macOS 27 at span 44, σ 2.13", flatSigma(2.1272)],
      ["macOS 27's law, σ(44) = 2.13", THIN_SIGMA_SHADOW as unknown as Record<string, unknown>],
    ] as const) {
      const raster = decodeCapture(await render(page, patch));
      areas.set(label, conformance(raster, [CAPSULE, ...TOOLBAR]).undrawn);
    }

    const report_ = [...areas].map(([label, undrawn]) => `${label}: ${undrawn}`).join(" | ");
    for (const [, undrawn] of areas) expect(undrawn, report_).toBe(0);
  });

  /**
   * The exposure's OTHER half: a caster deep enough to reach the overflow at a σ
   * nobody would call thin (review closure; claims §5.159b §10, finding 11).
   *
   * The two cases above sweep σ at a fixed 44 px depth. The quantity that
   * overflows is the ratio — `x` is the distance to the shadow's silhouette
   * MEASURED IN σ — so a wide caster reaches it by being deep, and the material
   * this package still ships as `macos26MaterialProfileDocument` reaches it at a
   * half-depth of 10.061 · 15.55 − 3.1 = 153.35 CSS px. A surface past about 307
   * CSS px on its shorter side therefore drew a strip of itself undrawn under
   * 0.19.0 at the macOS 26.5 material, which is a class of surface an
   * application has — a full-height sidebar, a tall sheet — and which the
   * calibration bed does not carry, its deepest component being 160 px.
   *
   * So this case is the one reading that says the fix is not about macOS 27's
   * thin regime: it is about the argument, at every material the package ships.
   * It fails on the unfixed renderer at the same σ the 34 goldens render at.
   */
  test("a 340 px caster is drawn whole at the macOS 26.5 σ", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const raster = decodeCapture(
      await render(page, flatSigma(MACOS_26_5_SIGMA), "w30-deep-caster-coverage"),
    );
    const { peak } = drawnPixels(raster);
    expect(peak, "the optics pass wrote no alpha at all").toBeGreaterThan(16);

    const deep = conformance(raster, [DEEP]);
    expect(
      deep.undrawn,
      `deep caster: ${deep.undrawn} of ${deep.declared} declared px undrawn, ` +
        `containment ${deep.containment.toFixed(4)} at σ ${MACOS_26_5_SIGMA}`,
    ).toBe(0);
    expect(deep.containment, "deep caster declaration conformance").toBeGreaterThanOrEqual(0.99);
  });
});
