/**
 * Node-side support for the GPU suite: adapter gating, golden comparison, and the
 * f32 reference.
 *
 * ## The adapter gate
 *
 * Every spec here needs a real GPU, and this machine's answer depends on the
 * launch mode (see `playwright.config.ts`). So the gate does two things rather
 * than one: it **skips with a reason** where there is no adapter at all, and it
 * **fails** where the adapter is a software fallback while the suite was told to
 * expect hardware. Silently measuring SwiftShader and calling it a GPU benchmark
 * is the failure mode worth spending a branch on.
 *
 * `VITREA_ALLOW_FALLBACK_ADAPTER=1` opts into the software path deliberately, for
 * a machine that has no other.
 *
 * ## Goldens
 *
 * Committed PNGs, compared with a tolerance rather than byte-for-byte. X5's sRGB
 * lock removes the browser's colour management from the comparison, but it cannot
 * remove floating-point differences between GPU vendors, and the spec's own
 * calibration model expects results to be keyed by adapter class rather than to be
 * identical across them. The tolerance is tight enough that a changed transfer
 * function, a changed corner fit, or a changed lens profile all fail it.
 *
 * Regenerate with `VITREA_UPDATE_GOLDENS=1 pnpm --filter @vitrea/renderer-webgpu test:golden`.
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, type Page } from "@playwright/test";
import { PNG } from "pngjs";

export const GOLDEN_DIR = join(dirname(fileURLToPath(import.meta.url)), "goldens");

export const UPDATING_GOLDENS = process.env.VITREA_UPDATE_GOLDENS === "1";
const ALLOW_FALLBACK = process.env.VITREA_ALLOW_FALLBACK_ADAPTER === "1";

export interface AdapterReport {
  readonly ok: boolean;
  readonly why?: string;
  readonly vendor?: string;
  readonly architecture?: string;
  readonly isFallback?: boolean;
  readonly timestamps?: boolean;
}

/** Load the harness page and wait for its module to have run. */
export async function openHarness(page: Page): Promise<AdapterReport> {
  page.on("pageerror", (error) => {
    throw error;
  });
  await page.goto("/e2e/fixtures/index.html");
  await page.waitForSelector("html[data-vitrea-ready='1']");
  return page.evaluate(() => window.vitrea.probe());
}

/**
 * Skip with a reason where there is no adapter; fail where the adapter is a
 * software fallback and nobody asked for one.
 */
export function requireHardwareAdapter(report: AdapterReport): void {
  if (!report.ok) {
    // eslint-disable-next-line @typescript-eslint/no-unnecessary-condition
    expect(report.ok, `no WebGPU adapter on this machine: ${report.why ?? "unknown"}`).toBe(true);
  }
  if (report.isFallback === true && !ALLOW_FALLBACK) {
    throw new Error(
      `The adapter is a software fallback (${report.vendor ?? "?"}/${report.architecture ?? "?"}). ` +
        "Goldens and benchmark numbers from a CPU rasteriser are not what they claim to be. " +
        "Launch with Playwright's full Chromium binary (channel: \"chromium\"), or set " +
        "VITREA_ALLOW_FALLBACK_ADAPTER=1 to measure the software path deliberately.",
    );
  }
}

export interface Raster {
  readonly width: number;
  readonly height: number;
  readonly data: Uint8Array;
}

export function decodeCapture(capture: {
  width: number;
  height: number;
  pixels: string;
}): Raster {
  return {
    width: capture.width,
    height: capture.height,
    data: new Uint8Array(Buffer.from(capture.pixels, "base64")),
  };
}

export function goldenPath(name: string): string {
  return join(GOLDEN_DIR, `${name}.png`);
}

export function writeGolden(name: string, raster: Raster): void {
  mkdirSync(GOLDEN_DIR, { recursive: true });
  const png = new PNG({ width: raster.width, height: raster.height });
  png.data = Buffer.from(raster.data);
  writeFileSync(goldenPath(name), PNG.sync.write(png));
}

export function readGolden(name: string): Raster | undefined {
  const path = goldenPath(name);
  if (!existsSync(path)) return undefined;
  const png = PNG.sync.read(readFileSync(path));
  return { width: png.width, height: png.height, data: new Uint8Array(png.data) };
}

export interface Difference {
  readonly maxChannelDelta: number;
  readonly meanChannelDelta: number;
  /** Fraction of pixels where any channel differs by more than `perPixel`. */
  readonly outlierFraction: number;
}

export function compare(actual: Raster, expected: Raster, perPixel = 2): Difference {
  if (actual.width !== expected.width || actual.height !== expected.height) {
    throw new Error(
      `Golden size mismatch: got ${actual.width}×${actual.height}, expected ${expected.width}×${expected.height}.`,
    );
  }
  let max = 0;
  let sum = 0;
  let outliers = 0;
  const pixels = actual.width * actual.height;

  for (let i = 0; i < pixels; i += 1) {
    let pixelMax = 0;
    for (let channel = 0; channel < 4; channel += 1) {
      const delta = Math.abs((actual.data[i * 4 + channel] ?? 0) - (expected.data[i * 4 + channel] ?? 0));
      sum += delta;
      if (delta > pixelMax) pixelMax = delta;
    }
    if (pixelMax > max) max = pixelMax;
    if (pixelMax > perPixel) outliers += 1;
  }

  return {
    maxChannelDelta: max,
    meanChannelDelta: sum / (pixels * 4),
    outlierFraction: outliers / pixels,
  };
}

/**
 * A rendering is not blank.
 *
 * Worth its own check because every failure mode that produces an all-zero target
 * — a missing bind group, a scissor that excluded everything, a device that
 * quietly died — would otherwise pass a "matches the golden" test on the day the
 * golden was regenerated from the same broken render.
 */
export function assertNotBlank(raster: Raster, name: string): void {
  let nonZero = 0;
  for (let i = 3; i < raster.data.length; i += 4) {
    if ((raster.data[i] ?? 0) > 0) nonZero += 1;
  }
  const fraction = nonZero / (raster.width * raster.height);
  expect(fraction, `${name} rendered nothing at all`).toBeGreaterThan(0.02);
}

declare global {
  interface Window {
    /**
     * One source of truth for the harness's shape: the type comes from the
     * harness module itself, so a signature that changes on one side stops
     * compiling on the other rather than failing at run time inside
     * `page.evaluate`.
     */
    vitrea: import("./fixtures/harness").VitreaHarness;
  }
}
