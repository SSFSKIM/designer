/**
 * W42 G2 step 3, U7: the body law ON, rendered on a real adapter, against `forward.py` with a
 * known T, and uniform invariance on rendered cells
 * (`calibration/results/2026-09-30-w42-g2-identification/implementation-design/u7_rendered.py`).
 *
 * The cells, with their instrument backdrops and expected codes, are generated into a scratch
 * directory by that script and named by `W42_U7_DIR`. They are too large to commit, and the
 * script regenerates them exactly. Each renders into `rgba32float` where the adapter offers
 * `float32-blendable`, so the comparison is the realisation's own and not the output format's, and
 * is held to the 0.15-code budget (§11.1, ruled) against the composite over the exact per-pixel
 * Gaussians. Its distance from `forward.py`, whose own narrow levels miss the exact Gaussian by up
 * to about 0.18 code at an impulse, is recorded beside it. Without the feature it renders into
 * `rgba16float`, whose conversion was measured at up to one ulp (0.1245 code at the top of the
 * range), and the bound widens by that.
 * Every render also asserts that WebGPU reported no error. That is the adapter's answer to
 * whether `layout: "auto"` gives the law's rgba32float tiles and A an `unfilterable-float`
 * binding: any other sample type fails validation at bind-group creation.
 *
 *     W42_U7_DIR=/tmp/w42-u7 npx playwright test --grep @w42-u7
 */

import { readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { expect, test } from "@playwright/test";

import { openHarness, requireHardwareAdapter } from "../support";

const DIR = process.env["W42_U7_DIR"];
const BUDGET_CODES = 0.15;
/** One rgba16float ulp at the top of the range, in codes: 2^-11 · 255. */
const HALF_FLOAT_CODES = 0.1245;
/** f32 end to end: the uniform invariance's own arithmetic, the tile store and two transfers. */
const FLOAT_CODES = 0.001;

interface Cell {
  readonly id: string;
  readonly uniform: boolean;
  readonly scene: unknown;
  readonly patch: Record<string, unknown>;
  readonly x: readonly number[];
  readonly y: readonly number[];
  /** `forward.py`'s output, T(255 · M), with its own narrow levels. */
  readonly expected: readonly (readonly number[])[];
  /** The composite over the exact per-pixel Gaussians, through the same knee, fill and T. */
  readonly exact: readonly (readonly number[])[];
}

test("@w42-u7 the law ON agrees with forward.py, and a uniform backdrop is invariant", async ({ page }) => {
  test.skip(DIR === undefined, "needs W42_U7_DIR from u7_rendered.py prepare");
  test.setTimeout(1_800_000);
  const report = await openHarness(page);
  requireHardwareAdapter(report);
  const cells = (JSON.parse(readFileSync(join(DIR!, "cells.json"), "utf8")) as { cells: Cell[] }).cells;
  const rows: {
    id: string; uniform: boolean; maxCodes: number; p99Codes: number; forwardMaxCodes: number;
    rendered: number[][];
  }[] = [];
  let format = "";
  for (const cell of cells) {
    const capture = await page.evaluate(([scene, patch]) =>
      window.vitrea.renderSceneFloat(scene as never, patch as never), [cell.scene, cell.patch] as const);
    format = capture.format;
    const bytes = Buffer.from(capture.pixels, "base64");
    const values = new Float32Array(bytes.buffer, bytes.byteOffset, bytes.byteLength / 4);
    const errors: number[] = [];
    let forward = 0;
    const rendered: number[][] = [];
    cell.x.forEach((x, n) => {
      const i = (cell.y[n]! * capture.width + x) * 4;
      expect(values[i + 3], `${cell.id} (${x}, ${cell.y[n]}) is not a covered interior pixel`)
        .toBeCloseTo(1, 3);
      rendered.push([0, 1, 2].map((c) => values[i + c]! * 255));
      for (let c = 0; c < 3; c++) {
        errors.push(Math.abs(values[i + c]! * 255 - cell.exact[n]![c]!));
        forward = Math.max(forward, Math.abs(values[i + c]! * 255 - cell.expected[n]![c]!));
      }
    });
    errors.sort((a, b) => a - b);
    rows.push({ id: cell.id, uniform: cell.uniform, maxCodes: errors[errors.length - 1]!,
      p99Codes: errors[Math.floor(0.99 * (errors.length - 1))]!, forwardMaxCodes: forward, rendered });
  }
  writeFileSync(join(DIR!, "result.json"), JSON.stringify({
    adapter: `${report.vendor ?? "?"}/${report.architecture ?? "?"}`,
    gpuErrors: await page.evaluate(() => window.vitrea.errors()),
    format,
    formatRoundingCodes: format === "rgba32float" ? FLOAT_CODES : HALF_FLOAT_CODES,
    cells: rows,
  }, null, 1));
  const rounding = format === "rgba32float" ? FLOAT_CODES : HALF_FLOAT_CODES;
  for (const row of rows) {
    expect(row.maxCodes, row.id).toBeLessThanOrEqual(row.uniform ? rounding : BUDGET_CODES + rounding);
  }
});
