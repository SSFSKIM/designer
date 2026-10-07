/** W49b DL2: W is per pixel over a shared source; S changes the source before scatter. */
import { createHash } from "node:crypto";
import { expect, test, type Page } from "@playwright/test";
import type { MaterialProfilePatch } from "../../src/material";
import type { Scene } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

const sceneAt = (dpr: number): Scene => ({
  name: `w49b-shared-${String(dpr)}`, widthCss: 400, heightCss: 320,
  devicePixelRatio: dpr, measureOnly: true, warmupFrames: 24,
  backdrop: { kind: "checkerboard", cell: 8 * dpr, size: 400 * dpr },
  backdropPlacement: { x: 0, y: 0, width: 400, height: 400 },
  groups: [{ groupId: "g", backdropSourceId: "bg", refraction: "true", analysisExact: true,
    surfaces: [
      { nodeId: "thin", family: "fixed-rounded-rect", reference: "figma-smoothing",
        shape: { center: [100, 64], size: [160, 64], radii: [16, 16, 16, 16],
          smoothing: 0, thickness: 10 } },
      { nodeId: "thick", family: "fixed-rounded-rect", reference: "figma-smoothing",
        shape: { center: [240, 220], size: [200, 160], radii: [24, 24, 24, 24],
          smoothing: 0, thickness: 10 } },
    ] }],
});
const base: MaterialProfilePatch = {
  sizeHeavySecondShare: 0.25, sizeHeavySecondSigma: 5, sizeHeavySecondSigma2x: 5,
  sizeSpanMax: 96, sizeScatterSpanMax: 160, sizeScatterSpanMax2x: 160,
};
const digest = (r: Raster, y0 = 0, y1 = r.height): string =>
  createHash("sha256").update(r.data.subarray(y0 * r.width * 4, y1 * r.width * 4)).digest("hex");
const render = async (page: Page, scene: Scene, patch: MaterialProfilePatch): Promise<Raster> =>
  decodeCapture(await page.evaluate(([s, p]) => window.vitrea.renderScene(s, undefined, p),
    [scene, patch] as const));

test.describe("@gpu W49b bandwidth and capture", () => {
  test("keeps the old path at identity and separates spans sharing one source", async ({ page }) => {
    test.setTimeout(180_000);
    requireHardwareAdapter(await openHarness(page));
    for (const dpr of [1, 1.5, 2]) {
      const scene = sceneAt(dpr);
      const current = await render(page, scene, base);
      const identity = await render(page, scene, { ...base, sizeHeavySecondSigmaFar1x: 0,
        sizeHeavySecondSigmaFar2x: 0, backdropCaptureScale: 1 });
      expect(digest(identity)).toBe(digest(current));
      const wide = await render(page, scene, { ...base, sizeHeavySecondSigmaFar1x: 4,
        sizeHeavySecondSigmaFar2x: 4 });
      expect(digest(wide, 0, 110 * dpr)).toBe(digest(current, 0, 110 * dpr));
      expect(digest(wide, 140 * dpr)).not.toBe(digest(current, 140 * dpr));
      const alphaCurrent = await render(page, scene, { ...base,
        tintAlphaFar1x: 0.2, tintAlphaFar2x: 0.2 });
      const alphaIndependent = await render(page, scene, { ...base,
        tintAlphaFar1x: 0.2, tintAlphaFar2x: 0.2, tintAlphaSpanMax: 256, tintAlphaSpanMax2x: 256 });
      expect(digest(alphaIndependent, 0, 110 * dpr)).toBe(digest(alphaCurrent, 0, 110 * dpr));
      expect(digest(alphaIndependent, 140 * dpr)).not.toBe(digest(alphaCurrent, 140 * dpr));
      const off = await render(page, scene, { ...base, sizeHeavySecondShare: 0 });
      const unread = await render(page, scene, { ...base, sizeHeavySecondShare: 0,
        sizeHeavySecondSigmaFar1x: 4, sizeHeavySecondSigmaFar2x: 4 });
      expect(digest(unread)).toBe(digest(off));
      const reduced = await render(page, scene, { ...base, backdropCaptureScale: 0.5 });
      expect(digest(reduced)).not.toBe(digest(current));
    }
  });
});
