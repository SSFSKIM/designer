import { PNG } from "pngjs";
import { expect, type Page } from "@playwright/test";

/** Load the fixture page and wait for the harness module to have run. */
export async function gotoHarness(page: Page): Promise<void> {
  await page.goto("/e2e/fixtures/index.html");
  await page.waitForSelector("html[data-harness-ready='1']");
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
