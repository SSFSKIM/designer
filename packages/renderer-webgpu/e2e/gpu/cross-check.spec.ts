/**
 * The family-C f32 cross-check on real hardware — Decision Log #20's obligation.
 *
 * > family C as the governor's first within-tier step **conditional on C6's f32
 * > cross-check**
 *
 * S2 ran exactly this protocol for family D on a metal-3 adapter and measured
 * 4.08e-5 px, which is 0.024% of family D's declared 0.170 px bound. Family C was
 * priced at 0.0097 ns/eval/px but only inspection-verified, so it could not ship
 * as a governor tier until it went through the same check.
 *
 * What runs here is the **shipped kernel string**, compiled from
 * `WGSL_FIELD_KERNELS` — the same constants `fieldPassSource` assembles the field
 * pass from — over the same three shape regimes, the same contour-relative
 * offsets and the same grid the spike used. The f64 reference comes from
 * `@vitrea/geometry`'s own `rsupField` / `rsupnField`, which are the line-for-line
 * TypeScript mirrors those shaders were transcribed from, so the difference this
 * measures is purely f32 versus f64 rounding of one arithmetic sequence.
 *
 * `test/f32-cross-check.test.ts` runs the CPU-emulated half of the same check in
 * the unit suite, which is what makes the answer available on a machine with no
 * adapter. Neither half alone is the whole check: the emulation cannot see
 * hardware fused multiply-add (which makes the real shader *more* accurate) or a
 * low-precision `inverseSqrt` (which makes it *less*), and only the run here can.
 */

import { expect, test } from "@playwright/test";
import { rsupField, rsupnField } from "@vitrea/geometry";

import { buildCheckSet, summarise } from "../../test/harness/f32-mirror";
import { openHarness, requireHardwareAdapter } from "../support";

/** S2's declared bounds for the two families, in px. */
const BOUND = { rsupn: 0.17, rsup: 0.574 } as const;

/**
 * The pass criterion, the same share of the budget the unit half uses: f32
 * rounding may not consume more than a thousandth of the family's bound, which
 * leaves that bound intact to three significant figures whatever the rounding
 * does. S2's own framing — 4.08e-5 px being "0.024% of the declared bound" — is a
 * share, so the criterion is one too.
 */
const BUDGET_SHARE = 1e-3;

test.describe("@gpu the f32 cross-check (Decision Log #20)", () => {
  test("both families agree with f64 to a rounding error on this adapter", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const set = buildCheckSet();

    // Two shape tables, because the families share a corner offset but not a fit.
    // The kernels take `k` as an argument, so one dispatch can evaluate both only
    // if they are fed the same coefficients — they are not, so each family gets
    // its own pass over the same points.
    const runFor = async (family: "rsupn" | "rsup") => {
      const shapes: number[] = [];
      for (const shape of set.shapes) {
        const params = family === "rsupn" ? shape.rsupn : shape.rsup;
        shapes.push(
          0,
          0,
          params.halfW,
          params.halfH,
          params.reach,
          params.k[0],
          params.k[1],
          params.k[2],
          params.k[3],
          params.k[4],
          0,
          0,
        );
      }
      const points: number[] = [];
      for (const point of set.points) points.push(point.x, point.y, point.shape, 0);

      const result = await page.evaluate(
        (input) => window.vitrea.crossCheck(input),
        { shapes, points, count: set.points.length },
      );

      const shader = family === "rsupn" ? result.rsupn : result.rsup;
      const diffs: number[] = [];
      const reaches: number[] = [];
      for (let i = 0; i < set.points.length; i += 1) {
        const point = set.points[i];
        const shape = set.shapes[point?.shape ?? 0];
        if (point === undefined || shape === undefined) continue;
        const params = family === "rsupn" ? shape.rsupn : shape.rsup;
        const exact =
          family === "rsupn"
            ? rsupnField(params, point.x, point.y)
            : rsupField(params, point.x, point.y);
        diffs.push(Math.abs((shader[i] ?? 0) - exact));
        reaches.push(params.reach);
      }
      return summarise(diffs, reaches);
    };

    const rsupn = await runFor("rsupn");
    const rsup = await runFor("rsup");

    for (const [family, stats, bound] of [
      ["rsupn", rsupn, BOUND.rsupn],
      ["rsup", rsup, BOUND.rsup],
    ] as const) {
      test.info().annotations.push({
        type: "f32-cross-check",
        description:
          `${family} on ${report.vendor ?? "?"}/${report.architecture ?? "?"}: ` +
          `n=${stats.n} max=${stats.maxAbsDiff.toExponential(3)} px ` +
          `(${((stats.maxAbsDiff / bound) * 100).toFixed(4)}% of the ${bound} px bound) ` +
          `p99=${stats.p99AbsDiff.toExponential(3)} mean=${stats.meanAbsDiff.toExponential(3)} ` +
          `rel-to-reach=${stats.maxRelativeToReach.toExponential(3)}`,
      });
    }

    expect(rsupn.n).toBe(set.points.length);
    expect(rsup.n).toBe(set.points.length);

    // Family D is the control: it must reproduce S2's own verdict, or the two runs
    // are not measuring the same thing.
    expect(rsupn.maxAbsDiff, "family D versus f64").toBeLessThan(BOUND.rsupn * BUDGET_SHARE);
    expect(rsupn.maxAbsDiff, "family D near S2's 4.08e-5 px").toBeLessThan(1e-3);

    // Family C is the verdict Decision Log #20 asks for.
    expect(rsup.maxAbsDiff, "family C versus f64").toBeLessThan(BOUND.rsup * BUDGET_SHARE);
    expect(rsup.maxRelativeToReach, "family C relative to the corner reach").toBeLessThan(1e-5);
  });

  test("the shader computes the same function as the TypeScript, not merely a close one", async ({
    page,
  }) => {
    // A transcription slip shows up as a gross disagreement rather than as a
    // rounding difference, so the two are distinguishable — and worth
    // distinguishing, because only one of them is a precision result.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const set = buildCheckSet();
    // The fully smoothed shape, deliberately. At smoothing 0 every coefficient is
    // zero, so the corner correction vanishes, `dR/dtheta` is zero, and the
    // normalization factor is exactly 1 — the two families are then the *same*
    // function, correctly, and a difference assertion on that shape would be
    // asking the shader to be wrong.
    const shapeIndex = set.shapes.length - 1;
    const shape = set.shapes[shapeIndex];
    expect(shape).toBeDefined();
    if (shape === undefined) return;

    const points = set.points.filter((point) => point.shape === shapeIndex).slice(0, 512);
    const result = await page.evaluate(
      (input) => window.vitrea.crossCheck(input),
      {
        shapes: [
          0,
          0,
          shape.rsupn.halfW,
          shape.rsupn.halfH,
          shape.rsupn.reach,
          shape.rsupn.k[0],
          shape.rsupn.k[1],
          shape.rsupn.k[2],
          shape.rsupn.k[3],
          shape.rsupn.k[4],
          0,
          0,
        ],
        points: points.flatMap((point) => [point.x, point.y, 0, 0]),
        count: points.length,
      },
    );

    // Every sample within a rounding error, and the two families genuinely
    // different from each other — the normalization has to be doing something.
    let worst = 0;
    let familyGap = 0;
    for (let i = 0; i < points.length; i += 1) {
      const point = points[i];
      if (point === undefined) continue;
      worst = Math.max(worst, Math.abs((result.rsupn[i] ?? 0) - rsupnField(shape.rsupn, point.x, point.y)));
      familyGap = Math.max(familyGap, Math.abs((result.rsupn[i] ?? 0) - (result.rsup[i] ?? 0)));
    }
    expect(worst).toBeLessThan(1e-3);
    expect(familyGap, "family C and family D must not be the same shader").toBeGreaterThan(0.01);
  });
});
