import { expect, test, type Page } from "@playwright/test";
import { openHarness, requireHardwareAdapter } from "../support";
import type { silhouetteProbe } from "../fixtures/silhouette";

const probe = (page: Page, mode: "silhouette" | "source" | "absent", reference = 0.3, split = false, hint = false,
  alpha: "opaque" | "partial" | "empty" = "opaque") =>
  page.evaluate(async ({ mode, reference, split, hint, alpha }) => {
    const path = "/e2e/fixtures/silhouette.ts";
    const module = await import(path) as { silhouetteProbe: typeof silhouetteProbe };
    return module.silhouetteProbe(mode, reference, split, hint, alpha);
  }, { mode, reference, split, hint, alpha });

const body = (result: Awaited<ReturnType<typeof silhouetteProbe>>): number[] => {
  const pixels: number[] = [];
  for (const centre of [32, 96]) for (let y = 24; y < 40; y++) {
    for (let x = centre - 8; x < centre + 8; x++) {
      pixels.push(...result.output.slice((y * result.width + x) * 4,
        (y * result.width + x) * 4 + 4));
    }
  }
  return pixels;
};

const maxDelta = (a: readonly number[], b: readonly number[]) =>
  Math.max(...a.map((value, i) => Math.abs(value - b[i]!)));

test.describe("@gpu W28 silhouette abscissa", () => {
  test("encodes raw texels before averaging, separately for both hosts", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const result = await probe(page, "silhouette");
    expect(result.readings).toHaveLength(2);
    const [left, right] = result.readings;
    expect(left!.surfaceId).toBe("host-0");
    expect(left!.encodedLuminance).toBeCloseTo(0.5, 3);
    expect(left!.linearLuminance).toBeCloseTo(0.5, 3);
    expect(left!.luminance).toBeCloseTo(0.21404114, 3);
    expect(right!.encodedLuminance).toBeCloseTo(191 / 255, 3);
    expect(left!.level).toBe(0);
    expect(left!.sampledWidth).toBe(128);
    expect(left!.sampleCount).toBeGreaterThan(1400);
    result.readings.forEach((reading, i) => {
      expect(Math.abs(reading.encodedLuminance - result.css[i]!.encodedLuminance!))
        .toBeLessThanOrEqual(1 / 255);
      expect(reading.sampleCount).toBe(result.css[i]!.footprint!.sampleCount);
    });
  });

  test("all solve consumers use the local reference and the union keeps both hosts", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const base = await probe(page, "silhouette", 0.3);
    const wrongSource = await probe(page, "silhouette", 0.9);
    const separate = await probe(page, "silhouette", 0.3, true);
    expect(maxDelta(body(base), body(wrongSource))).toBeLessThanOrEqual(1);
    expect(maxDelta(body(base), body(separate))).toBeLessThanOrEqual(1);
    // The assertion above cannot pass by returning a blank target.
    expect(Math.max(...body(base).filter((_, i) => i % 4 !== 3))).toBeGreaterThan(100);
    expect(Math.abs(body(base)[0]! - body(base)[1024]!)).toBeGreaterThan(5);
  });

  test("transparent texels carry no colour and an empty mask publishes no abscissa", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const partial = await probe(page, "silhouette", 0.3, false, false, "partial");
    expect(partial.readings[0]!.encodedLuminance).toBeCloseTo(1, 5);
    expect(partial.readings[0]!.linearLuminance).toBeCloseTo(1, 5);
    expect(partial.readings[0]!.encodedLuminance)
      .toBeCloseTo(partial.css[0]!.encodedLuminance!, 5);
    expect(partial.readings[0]!.sampleCount).toBe(partial.css[0]!.footprint!.sampleCount);
    const empty = await probe(page, "silhouette", 0.3, false, false, "empty");
    expect(empty.readings.map((reading) => reading.surfaceId)).toEqual(["host-1"]);
    expect(empty.css[0]).toBeUndefined();
  });

  test("an author hint bypasses the reduction on every host", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const hint = await probe(page, "silhouette", 0.3, false, true);
    const source = await probe(page, "source", 0.3);
    expect(hint.output).toEqual(source.output);
    expect(hint.readings).toHaveLength(2);
    for (const reading of hint.readings) {
      expect(reading.kind).toBe("hint");
      expect(reading.encodedLuminance).toBeCloseTo(0.3, 12);
      expect(reading.sampleCount).toBe(0);
    }
  });

  test("absent and explicit source preserve the same drawing", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const absent = await probe(page, "absent");
    const source = await probe(page, "source");
    expect(source.output).toEqual(absent.output);
    expect(source.readings).toEqual([]);
  });
});
