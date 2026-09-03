import { PNG } from "pngjs";
import { expect, test, type Page } from "@playwright/test";
import { resolveAccessibilityPolicy } from "@vitreajs/vitrea";

import {
  MATERIAL_OPTICS,
  MATERIAL_SOURCE_SIZE,
  opticsUnderPolicy,
  requiredSamplingPadding,
  CSS_TIER_RAMP_SCALE,
  scatterThickness,
  sizeScatterSigmaAt,
} from "../src/optics";
import { accessibilityRefractionCap } from "../src/refraction";

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
  /** `true` software, `false` measured hardware, `undefined` unmeasurable. */
  readonly isFallback?: boolean | undefined;
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
 *
 * `VITREA_ALLOW_FALLBACK_ADAPTER=1` is the deliberate exception — the one CI
 * takes, because `ubuntu-latest` has no GPU. Taking it is not free: the run has
 * to say so, on every test, naming the rasteriser it measured, so that a green
 * report cannot be mistaken for a hardware verdict.
 */
export function requireHardwareAdapter(report: AdapterReport): void {
  expect(report.ok, `no WebGPU adapter on this machine: ${report.why ?? "unknown"}`).toBe(true);

  // Only a measured `false` is hardware: `undefined` means the harness could not
  // tell, and an unmeasured adapter must not pass as a verified one.
  if (report.isFallback === false) return;

  const named = `${report.vendor ?? "?"}/${report.architecture ?? "?"}`;
  const what =
    report.isFallback === true
      ? `a software fallback (${named})`
      : `of unmeasurable class (${named} — this build exposes no isFallbackAdapter to read)`;

  if (!ALLOW_FALLBACK) {
    throw new Error(
      `The adapter is ${what}. ` +
        "A GPU tier verified on a CPU rasteriser is not the tier this suite is about. " +
        'Launch with Playwright\'s full Chromium binary (channel: "chromium"), or set ' +
        "VITREA_ALLOW_FALLBACK_ADAPTER=1 to measure the software path deliberately.",
    );
  }

  const note =
    `measuring the GPU tier on ${report.isFallback === true ? `a SOFTWARE adapter (${named})` : what}. ` +
    "Behaviour is under test here; how real glass looks on real hardware is not, " +
    "and that coverage lives on developer machines.";
  test.info().annotations.push({ type: "software-adapter", description: note });
  console.warn(`[chromium-gpu] ${note}`);
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

/**
 * The blur the CSS tier will write for a member of this span and box, and the
 * 3σ sampling padding `root.ts` takes over it — derived from the same optics
 * module the runtime uses rather than written down, so the specs assert the
 * mechanism and not a material.
 *
 * At the 1x law, whatever ratio the page composites at (W13 Decision Log 5):
 * the CSS tier has no device-scale input, so `Desktop Safari` at ratio 2 and
 * `Desktop Chrome` at 1 get the same σ, and a spec that divided its expectation
 * by the page's ratio would assert half the width the proxy writes and call it
 * an engine defect.
 */
export function expectedProxyBlur(options: {
  readonly spanPx: number;
  /**
   * The member's own width and height. The ramp's projection is its area
   * average over the member's box (W13 G1), so a 120×40 fixture projects a
   * different σ from a 40×40 square of the same span; a spec that omits this
   * asserts the square's number against a runtime that renders the box's.
   */
  readonly extentsCssPx?: readonly [number, number];
  readonly reducedTransparency?: boolean;
}): { readonly sigma: number; readonly padding: number } {
  const policy = resolveAccessibilityPolicy(
    {
      reducedTransparency: options.reducedTransparency ?? false,
      reducedMotion: false,
      increasedContrast: false,
      forcedColors: false,
      reducedTransparencySupported: true,
    },
    { reducedTransparency: options.reducedTransparency ?? false },
  ).material;
  const folded = opticsUnderPolicy(MATERIAL_OPTICS.regular, policy);
  const sigma = sizeScatterSigmaAt(
    folded.blurRadius,
    // The projection at the scale the CSS tier reads it at, which is what
    // `root.ts` takes the padding floor over — see `CSS_TIER_RAMP_SCALE`.
    scatterThickness(
      options.spanPx,
      MATERIAL_SOURCE_SIZE.refractionScale[accessibilityRefractionCap(policy)],
      MATERIAL_SOURCE_SIZE,
      CSS_TIER_RAMP_SCALE,
      options.extentsCssPx,
    ),
    MATERIAL_SOURCE_SIZE,
    CSS_TIER_RAMP_SCALE,
  );
  return { sigma, padding: requiredSamplingPadding(sigma) };
}

export interface Box {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

/** A member union inflated by a padding on every side — what a proxy's box is. */
export function paddedBox(union: Box, padding: number): Box {
  return {
    x: union.x - padding,
    y: union.y - padding,
    width: union.width + 2 * padding,
    height: union.height + 2 * padding,
  };
}

/** `toEqual` for a box whose padding is a real number rather than an integer. */
export function expectBox(actual: Box | undefined, wanted: Box): void {
  expect(actual).toBeDefined();
  for (const side of ["x", "y", "width", "height"] as const) {
    expect(actual?.[side], side).toBeCloseTo(wanted[side], 3);
  }
}
