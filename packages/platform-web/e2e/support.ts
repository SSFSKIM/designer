import { PNG } from "pngjs";
import { expect, type Page } from "@playwright/test";

/** Load the fixture page and wait for the harness module to have run. */
export async function gotoHarness(page: Page): Promise<void> {
  await page.goto("/e2e/fixtures/index.html");
  await page.waitForSelector("html[data-harness-ready='1']");
}

/** What the page reports about this machine's adapter. Mirrors the harness. */
export interface AdapterReport {
  readonly ok: boolean;
  readonly why?: string;
  readonly vendor?: string;
  readonly architecture?: string;
  readonly isFallback?: boolean;
}

const ALLOW_FALLBACK = process.env.VITREA_ALLOW_FALLBACK_ADAPTER === "1";

/**
 * The `e2e/gpu` gate: fail, never skip.
 *
 * C6 established both halves of this. An absent adapter means the suite was run
 * on a machine it cannot answer for, and a skipped test reads as a passing one
 * in every report. A *software* adapter is worse than absent: it answers every
 * question plausibly and none of them about the thing acceptance #2 asks, which
 * is whether real glass renders on real hardware.
 */
export function requireHardwareAdapter(report: AdapterReport): void {
  expect(report.ok, `no WebGPU adapter on this machine: ${report.why ?? "unknown"}`).toBe(true);

  if (report.isFallback === true && !ALLOW_FALLBACK) {
    throw new Error(
      `The adapter is a software fallback (${report.vendor ?? "?"}/${report.architecture ?? "?"}). ` +
        "A GPU tier verified on a CPU rasteriser is not the tier this suite is about. " +
        'Launch with Playwright\'s full Chromium binary (channel: "chromium"), or set ' +
        "VITREA_ALLOW_FALLBACK_ADAPTER=1 to measure the software path deliberately.",
    );
  }
}

export interface Rgb {
  readonly r: number;
  readonly g: number;
  readonly b: number;
}

/** One screenshot, decoded, with a point sampler in the clip's own coordinates. */
export interface Sampler {
  at(x: number, y: number): Rgb;
  readonly width: number;
  readonly height: number;
}

export interface ClipRect {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

/**
 * Screenshot a region and decode it.
 *
 * The pixels have to come from a screenshot rather than from page script: the
 * whole point of S1's Q5 is that no in-page readback path can see
 * `backdrop-filter` output. Chromium only, by the acceptance narrowing.
 */
export async function sample(page: Page, clip: ClipRect): Promise<Sampler> {
  const buffer = await page.screenshot({ clip, animations: "disabled" });
  const png = PNG.sync.read(buffer);
  const scale = png.width / clip.width;

  return {
    width: png.width,
    height: png.height,
    at(x, y) {
      const px = Math.round(x * scale);
      const py = Math.round(y * scale);
      const index = (png.width * py + px) << 2;
      return {
        r: png.data[index] ?? 0,
        g: png.data[index + 1] ?? 0,
        b: png.data[index + 2] ?? 0,
      };
    },
  };
}

/** Absolute per-channel difference, the metric S1's report is written in. */
export function channelDelta(a: Rgb, b: Rgb): number {
  return Math.max(Math.abs(a.r - b.r), Math.abs(a.g - b.g), Math.abs(a.b - b.b));
}

export function expectByteIdentical(a: Rgb, b: Rgb, what: string): void {
  expect(channelDelta(a, b), `${what} should be byte-identical, got ${JSON.stringify(a)} vs ${JSON.stringify(b)}`).toBe(0);
}
