/**
 * W31 G2 — the range sweeps: both halves of every guarded ratio (claims §5.163
 * §2; the tracker's WGSL range class, fix shape 2).
 *
 * `test/w31-wgsl-range.test.ts` reads the shader text and says every
 * transcendental's argument is bounded. This says the same thing from the other
 * end, on a real adapter, where the backend's own lowering lives: render the
 * material at values a fit could reach and at surfaces an application has, and
 * assert an invariant that **does not depend on the value being swept**.
 *
 * ## The invariant, and why it is this one
 *
 * *No constant of the material decides what the surface covers.* The lens
 * displaces where the backdrop is sampled from, the scatter decides how wide a
 * blur it is sampled through, the tone response decides how light the body sits
 * and the rim's exponent decides how the lit edge falls around the contour —
 * and not one of them may move the set of pixels the surface draws on. So the
 * reading is W20's declaration conformance (`declared-coverage.ts`), which is
 * exactly what caught §5.159 §6's undrawn strip while every perceptual row
 * stayed green: SSIM over a whole cell moved 0.98217 → 0.97826 on a capsule
 * with a hole through it.
 *
 * Beside it, on the same rasters and for free, the readback guard: `renderScene`
 * refuses any raster with an enclosed region of zero alpha, so every sweep below
 * is also a test that no swept value produces a NaN that reaches the composite.
 * **An f32 NaN is not observable in an 8-bit readback** — written to
 * `rgba8unorm` it is a zero — so what is asserted is its signature and not the
 * NaN, and saying so is the honest form of "no NaN in the readback".
 *
 * ## Both halves of the ratio
 *
 * §5.159b's overflow was a ratio: a caster's depth over its own σ. The material
 * half of it was swept by W30 G3b and the scene half was added by its review
 * closure (§5.159b §10, finding 11), because "sweep the material and hold the
 * geometry" covers half an exposure. Every sweep here has both.
 *
 * **The material axis is bracketed by 550×**, and that number is a measurement
 * rather than a taste: it is the widest ratio the project has ever moved a leaf
 * across a material generation — `backdropToneHigh`, 0.055 → 0.0001, on both
 * macOS 27 standard documents (the documents' own `entries[].previous`, read by
 * `results/2026-09-21-w31-g2-range-class/leaf-moves.py`). A fit that moved a
 * leaf further than any fit ever has would be outside what this claims, and
 * that is a bound worth stating rather than a range worth guessing. The ladder
 * is ÷550, ÷23.45, ×1, ×23.45, ×550 — the geometric midpoints included so the
 * sweep is a curve and not two endpoints.
 *
 * **The scene axis** is span, radius and depth at the shipped material: a 32 px
 * caster where the σ law is at its thin floor, the bed's spans, and a 340 px one
 * past where §5.159b's own third case found the macOS 26.5 material reaching the
 * overflow at a half-depth of 153.35 CSS px.
 */

import { expect, test, type Page } from "@playwright/test";

import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";
import { conformance, type Region } from "./declared-coverage";

/**
 * The widest ratio any leaf has moved between two material generations.
 *
 * Measured, not chosen. See the module note.
 */
const WIDEST_LEAF_MOVE = 550;
const LADDER = [1 / WIDEST_LEAF_MOVE, 1 / Math.sqrt(WIDEST_LEAF_MOVE), 1, Math.sqrt(WIDEST_LEAF_MOVE), WIDEST_LEAF_MOVE] as const;

/**
 * The macOS 27 light document's own values for the leaves swept here, named
 * rather than imported: this package does not depend on `@vitrea/calibration`,
 * and a case that silently followed a document as it is refitted would stop
 * being a case about the range a fit can reach the day the fit moved.
 */
const SHIPPED = {
  lensHeightPerSpan: 0.25,
  lensHeightMax: 20,
  lensAmountPerSpan: 0.8,
  lensAmountMax: 60,
  lensExtentGain: 1.337,
  lensProfileExponent: 3.69,
  sizeHeavyTapSigma: 14,
  sizeHeavyTapSigma2x: 20,
  sizeHeavySecondSigma: 30,
  sizeHeavySecondSigma2x: 30,
  toneAnchorX: [0.004, 0.11, 0.425, 0.95],
  toneThin: [0.214, 0.2835, 0.5383, 0.937],
  toneThick: [0.242, 0.3074, 0.5554, 0.957],
  rimLitExponent: 0.85,
} as const;

/**
 * The scene axis's two ends, for the cross term below: the thin floor of macOS
 * 27's σ law, and the caster past where the macOS 26.5 material reached the
 * overflow.
 */
const CROSS_SPANS = [32, 340] as const;

const scaled = (row: readonly number[], factor: number): number[] =>
  row.map((value) => value * factor);

/**
 * One surface over a checkerboard, at a given span and radius.
 *
 * A structured backdrop rather than a flat one because the scatter and the lens
 * are the axes being swept and neither does anything over a constant: a sweep of
 * a blur width over a flat field is a sweep of nothing.
 */
const sweepScene = (span: number, radius: number, label: string): Record<string, unknown> => {
  const pad = 80;
  const widthCss = span + pad * 2;
  const heightCss = span + pad * 2;
  const cx = widthCss / 2;
  const cy = heightCss / 2;
  return {
    name: `w31-range-sweep-${label}`,
    widthCss,
    heightCss,
    devicePixelRatio: 1,
    measureOnly: true,
    backdrop: { kind: "checkerboard", cell: 16, size: 256 },
    groups: [
      {
        groupId: "g",
        refraction: "true",
        analysisExact: true,
        backdropSourceId: "bg",
        surfaces: [
          {
            nodeId: "s",
            family: "fixed-rounded-rect",
            reference: "figma-smoothing",
            shape: {
              center: [cx, cy],
              size: [span, span],
              radii: [radius, radius, radius, radius],
              smoothing: 0,
              thickness: 14,
            },
          },
        ],
      },
    ],
  };
};

const regionOf = (span: number, radius: number): Region => {
  const pad = 80;
  const centre = (span + pad * 2) / 2;
  return { cx: centre, cy: centre, w: span, h: span, r: radius };
};

/**
 * A green run still has to say what it measured: these readings are the gate's
 * evidence (`results/2026-09-21-w31-g2-range-class/`), and a sweep that reports
 * only "passed" records nothing about the range it swept. Written to stdout
 * rather than through `console`, which the lint rules reserve for warnings.
 */
const record = (label: string, lines: readonly string[]): void => {
  process.stdout.write(`[${label}]\n  ${lines.join("\n  ")}\n`);
};

const render = (
  page: Page,
  scene: Record<string, unknown>,
  patch: Record<string, unknown>,
): Promise<Raster> =>
  page
    .evaluate(
      (args) =>
        window.vitrea.renderScene(
          args.scene as never,
          undefined,
          args.patch as never,
        ),
      { scene, patch },
    )
    .then(decodeCapture);

/**
 * One reading: render, refuse a hole (the guard, inside `renderScene`), and
 * assert the declaration clause.
 *
 * Returns the line the spec records, so a green run still says what it measured.
 */
const readOne = async (
  page: Page,
  span: number,
  radius: number,
  label: string,
  patch: Record<string, unknown>,
): Promise<string> => {
  const scene = sweepScene(span, radius, label);
  const raster = await render(page, scene, patch);
  const read = conformance(raster, [regionOf(span, radius)]);
  expect(read.peak, `${label}: the optics pass wrote no alpha at all`).toBeGreaterThan(16);
  expect(
    read.undrawn,
    `${label}: ${read.undrawn} of ${read.declared} declared px undrawn, ` +
      `containment ${read.containment.toFixed(4)}`,
  ).toBe(0);
  expect(read.containment, `${label}: declaration conformance`).toBeGreaterThanOrEqual(0.99);
  return (
    `${label}: ${read.declared} declared, ${read.undrawn} undrawn, ` +
    `containment ${read.containment.toFixed(4)}, peak ${read.peak}`
  );
};

test.describe("@gpu the material's range: a swept leaf does not decide what the surface covers", () => {
  test("the lens depth, over the range a fit could reach", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const lines: string[] = [];
    for (const factor of LADDER) {
      lines.push(
        await readOne(page, 96, 24, `lens ×${factor.toPrecision(4)}`, {
          lensHeightPerSpan: SHIPPED.lensHeightPerSpan * factor,
          lensHeightMax: SHIPPED.lensHeightMax * factor,
          lensAmountPerSpan: SHIPPED.lensAmountPerSpan * factor,
          lensAmountMax: SHIPPED.lensAmountMax * factor,
          lensExtentGain: SHIPPED.lensExtentGain * factor,
        }),
      );
    }
    /*
     * The exponent separately, and on its own ladder, because it is not a
     * length: `pow(lensT, p)`'s base reaches exactly 0 at every pixel past the
     * lens's extent, so p is the one leaf of the lens whose RANGE PROOF is a
     * bound rather than an arithmetic fact (`test/wgsl-range/proofs.ts`). The
     * ladder runs to the proof's own ceiling of 64 and down to just above its
     * floor of 0, which is where `pow(0, 0)` would be NaN.
     */
    for (const exponent of [0.01, 0.5, SHIPPED.lensProfileExponent, 16, 64]) {
      lines.push(await readOne(page, 96, 24, `lensProfileExponent ${exponent}`, {
        lensProfileExponent: exponent,
      }));
    }
    record("w31 lens depth", lines);
  });

  test("the scatter widths, both taps, over the range a fit could reach", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const lines: string[] = [];
    for (const factor of LADDER) {
      lines.push(
        await readOne(page, 96, 24, `heavy tap ×${factor.toPrecision(4)}`, {
          sizeHeavyTapSigma: SHIPPED.sizeHeavyTapSigma * factor,
          sizeHeavyTapSigma2x: SHIPPED.sizeHeavyTapSigma2x * factor,
        }),
      );
      /*
       * The SECOND tap is inert on every shipped document — W30 declined it on
       * both, at a share of 0 — so a sweep of its width alone would sweep a
       * multiplied zero. The share is opened to 0.5 so the tap is live, which
       * is the only way this axis is swept at all.
       */
      lines.push(
        await readOne(page, 96, 24, `second tap ×${factor.toPrecision(4)}`, {
          sizeHeavySecondSigma: SHIPPED.sizeHeavySecondSigma * factor,
          sizeHeavySecondSigma2x: SHIPPED.sizeHeavySecondSigma2x * factor,
          sizeHeavySecondShare: 0.5,
        }),
      );
    }
    record("w31 scatter widths", lines);
  });

  test("the tone response's knots, abscissa and both ordinate rows", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const lines: string[] = [];
    for (const factor of LADDER) {
      lines.push(
        await readOne(page, 96, 24, `tone knots ×${factor.toPrecision(4)}`, {
          backdropToneAnchorX: scaled(SHIPPED.toneAnchorX, factor),
          backdropToneResponseThin: scaled(SHIPPED.toneThin, factor),
          backdropToneResponseThick: scaled(SHIPPED.toneThick, factor),
        }),
      );
      /*
       * The abscissa alone, so a collapsed spacing between knots is reached: the
       * monotone interpolation's own divisors are the gaps between them, and
       * scaling the ordinates with it leaves the curve's shape unchanged.
       *
       * The two ordinate rows are still sent at their shipped values because
       * `withMaterialOverrides` REFUSES a patch that leaves the three rows at
       * different knot counts — measured here: the macOS 27 document is a
       * four-knot curve and the runtime default is a three-knot one, so an
       * abscissa-only patch resolves to a mixed triplet and the material layer
       * rejects it before a pipeline is built. A guard of exactly this class,
       * one layer up, and it is why this case sends all three rows.
       */
      lines.push(
        await readOne(page, 96, 24, `tone abscissa ×${factor.toPrecision(4)}`, {
          backdropToneAnchorX: scaled(SHIPPED.toneAnchorX, factor),
          backdropToneResponseThin: [...SHIPPED.toneThin],
          backdropToneResponseThick: [...SHIPPED.toneThick],
        }),
      );
    }
    record("w31 tone knots", lines);
  });

  test("the rim's lit-edge exponent, across the window its range proof claims", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const lines: string[] = [];
    // 0 is the inert reading the `clear` variant ships; 64 is the proof's
    // ceiling. The base is floored at 1e-6, so 0 is safe here where it is not
    // for the lens — which is the asymmetry the two proofs record.
    for (const exponent of [0, 0.1, SHIPPED.rimLitExponent, 8, 64]) {
      lines.push(
        await readOne(page, 96, 24, `rimLitExponent ${exponent}`, {
          optics: { regular: { rimLitExponent: exponent }, clear: { rimLitExponent: exponent } },
        }),
      );
    }
    // And the axis it is symmetric about, at the range-proof's own ceiling of 2.
    for (const axis of [[-0.7071, -0.7071], [1, 0], [-1.4142, -1.4142]] as const) {
      lines.push(
        await readOne(page, 96, 24, `rimLitAxis [${axis[0]}, ${axis[1]}]`, {
          rimLitAxis: [...axis],
          optics: { regular: { rimLitExponent: 8 } },
        }),
      );
    }
    record("w31 rim exponent", lines);
  });

  test("the SCENE's axis at the shipped material: span, radius and depth", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    /*
     * The other half of every ratio above. §5.159b's overflow was a caster's
     * depth over its own σ, so a sweep that holds the geometry fixed covers half
     * the exposure — the review closure's finding 11, applied to every axis
     * rather than only to the shadow's.
     *
     * The spans are the bed's own (32 is where macOS 27's σ law sits at its thin
     * floor, 44 is the capsule, 96 is the σ reference, 160 the widest gated
     * component) plus 340, which is past the half-depth of 153.35 CSS px where
     * §5.159b found the macOS 26.5 material reaching the overflow. The radius
     * runs from square corners to a full capsule at each.
     */
    const lines: string[] = [];
    for (const span of [32, 44, 96, 160, 340]) {
      for (const radius of [0, Math.min(12, span / 2), span / 2]) {
        lines.push(
          await readOne(page, span, radius, `span ${span} r ${radius}`, {}),
        );
      }
    }
    record("w31 scene axis", lines);
  });

  /**
   * The CROSS term: a material at an extreme ON a scene at an extreme (review
   * closure 2026-09-21; claims §5.163 §8, finding N9).
   *
   * Every case above holds one axis at the shipped values while it sweeps the
   * other — the material ladders all run at span 96 / radius 24, and the scene
   * axis runs at the shipped material. §5.159b's own defect was neither: it was
   * a COMBINATION, a caster deep enough measured in a σ narrow enough, and each
   * half of it was unremarkable alone. A pair of one-dimensional sweeps cannot
   * see that class, which is the same reason the review closure of §5.159b
   * added the scene's axis in the first place.
   *
   * So each material ladder's two ENDPOINTS are re-read at the scene axis's own
   * two ends — span 32, where macOS 27's σ law sits at its thin floor, and span
   * 340, past where the macOS 26.5 material reached the overflow — asserting the
   * same invariant, because the invariant is the same one: no constant of the
   * material decides what the surface covers, at any surface. Two leaves whose
   * extreme obviously interacts with span are carried in beside them: the lens
   * profile's exponent, whose base is the pixel's depth over the lens's
   * span-scaled extent, and the rim's, which shapes the lit edge around a
   * contour whose curvature is the scene's.
   */
  test("the cross term: each material extreme at each end of the scene's axis", async ({
    page,
  }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const ends = [1 / WIDEST_LEAF_MOVE, WIDEST_LEAF_MOVE] as const;
    const ladders: readonly (readonly [string, (factor: number) => Record<string, unknown>])[] = [
      [
        "lens",
        (factor) => ({
          lensHeightPerSpan: SHIPPED.lensHeightPerSpan * factor,
          lensHeightMax: SHIPPED.lensHeightMax * factor,
          lensAmountPerSpan: SHIPPED.lensAmountPerSpan * factor,
          lensAmountMax: SHIPPED.lensAmountMax * factor,
          lensExtentGain: SHIPPED.lensExtentGain * factor,
        }),
      ],
      [
        "heavy tap",
        (factor) => ({
          sizeHeavyTapSigma: SHIPPED.sizeHeavyTapSigma * factor,
          sizeHeavyTapSigma2x: SHIPPED.sizeHeavyTapSigma2x * factor,
        }),
      ],
      [
        "second tap",
        (factor) => ({
          sizeHeavySecondSigma: SHIPPED.sizeHeavySecondSigma * factor,
          sizeHeavySecondSigma2x: SHIPPED.sizeHeavySecondSigma2x * factor,
          sizeHeavySecondShare: 0.5,
        }),
      ],
      [
        "tone knots",
        (factor) => ({
          backdropToneAnchorX: scaled(SHIPPED.toneAnchorX, factor),
          backdropToneResponseThin: scaled(SHIPPED.toneThin, factor),
          backdropToneResponseThick: scaled(SHIPPED.toneThick, factor),
        }),
      ],
      [
        "tone abscissa",
        (factor) => ({
          backdropToneAnchorX: scaled(SHIPPED.toneAnchorX, factor),
          backdropToneResponseThin: [...SHIPPED.toneThin],
          backdropToneResponseThick: [...SHIPPED.toneThick],
        }),
      ],
    ];

    const lines: string[] = [];
    for (const span of CROSS_SPANS) {
      const radius = Math.min(12, span / 2);
      for (const [name, patch] of ladders) {
        for (const factor of ends) {
          lines.push(
            await readOne(
              page,
              span,
              radius,
              `span ${span} × ${name} ×${factor.toPrecision(4)}`,
              patch(factor),
            ),
          );
        }
      }
      for (const exponent of [0.01, 64]) {
        lines.push(
          await readOne(page, span, radius, `span ${span} × lensProfileExponent ${exponent}`, {
            lensProfileExponent: exponent,
          }),
        );
      }
      for (const exponent of [0, 64]) {
        lines.push(
          await readOne(page, span, radius, `span ${span} × rimLitExponent ${exponent}`, {
            optics: { regular: { rimLitExponent: exponent }, clear: { rimLitExponent: exponent } },
          }),
        );
      }
    }
    record("w31 cross term", lines);
  });
});
