/**
 * Two of C6's acceptance clauses, on a real device.
 *
 *  - **"instrumented dirty-epoch invariant (≤1 pyramid rebuild per dirty source
 *    per frame)"** — `test/dirty-epoch.test.ts` drives core's own scene and
 *    scheduler over the ledger with no GPU, which is where the composition is
 *    proved. What that cannot show is the ledger doing its job *inside a real
 *    frame*, where the rebuild also allocates textures and encodes four passes.
 *    So this spec hands the renderer two requests for one source in one frame —
 *    something core would never do — and reads the store's own counters.
 *  - **"device-loss recovery test for both ownership modes"** — a real
 *    `GPUDevice.destroy()`, a real `lost` promise, a real replacement, and a draw
 *    afterwards that has to succeed against resources rebuilt on the new device.
 */

import { expect, test } from "@playwright/test";

import { openHarness, requireHardwareAdapter } from "../support";

test.describe("@gpu the dirty-epoch invariant on a device", () => {
  test("rebuilds an always-dirty source once per frame, never twice", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const frames = 30;
    const stats = await page.evaluate((count) => window.vitrea.invariant(count), frames);

    expect(stats.framesDrawn).toBe(frames);
    // The invariant, stated exactly: no source rebuilt more than once in any frame.
    expect(stats.peak, "peak rebuilds per source per frame").toBe(1);
    // One rebuild per frame — not one per group, though two groups sample it.
    expect(stats.rebuilds, "one rebuild per frame, not one per group").toBe(frames);
    // And the duplicate request in each frame was declined rather than served.
    // Against a live source that decline comes from the ledger; against a static
    // one it would come from the clean-skip. Either way, nothing rebuilt twice.
    expect(stats.refused + stats.skippedClean, "duplicates declined").toBe(frames);
    expect(stats.refused, "declined by the ledger, since the source is live").toBe(frames);
  });
});

test.describe("@gpu device-loss recovery", () => {
  test("an app-owned device reports the loss and waits for a replacement", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const result = await page.evaluate(() => window.vitrea.deviceLoss("app"));

    expect(result.beforeHealth).toBe("ok");
    expect(result.afterHealth).toBe("lost");
    // `webgpu` stays "available" across the loss: core only raises `device-lost`
    // where there was a device to lose, and clearing this would collapse a
    // recoverable fault into `no-webgpu`, whose honest recovery is "none".
    expect(result.afterWebgpu).toBe("available");
    // The app owns the resources that would have to be re-registered, so the
    // renderer waits rather than inventing a device it was not given.
    expect(result.replacementPending).toBe(true);

    expect(result.recoveredHealth).toBe("ok");
    expect(result.generations).toBe(2);
    expect(result.drewAfterRecovery, "drew a frame on the replacement device").toBe(true);
  });

  test("a vitrea-owned device recovers and draws again", async ({ page }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const result = await page.evaluate(() => window.vitrea.deviceLoss("vitrea"));

    expect(result.beforeHealth).toBe("ok");
    expect(result.afterHealth).toBe("lost");
    expect(result.afterWebgpu).toBe("available");
    // Nothing for the app to hand in: a vitrea-owned device is the renderer's to
    // replace.
    expect(result.replacementPending).toBe(false);
    expect(result.recoveredHealth).toBe("ok");
    expect(result.generations).toBe(2);
    expect(result.drewAfterRecovery).toBe(true);
  });
});

test.describe("@gpu the shipped shaders compile", () => {
  test("every pass builds a pipeline without a validation error", async ({ page }) => {
    // The unit suite checks the WGSL structurally because Node has no compiler.
    // This is the other half: a frame that touches every pass, with the device's
    // own error channel read afterwards. A validation failure draws nothing and
    // says nothing unless somebody asks.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    await page.evaluate(() => window.vitrea.renderScene("refraction-checkerboard"));
    await page.evaluate(() => window.vitrea.renderScene("highlight-press-glow"));
    const errors = await page.evaluate(() => window.vitrea.errors());

    expect(errors, `WebGPU reported: ${errors.join(" | ")}`).toEqual([]);
  });
});

test.describe("@gpu the governor's field families agree", () => {
  test("family C renders the same silhouette as family D", async ({ page }) => {
    // The two families share a zero level set by construction — that is what makes
    // family C a *within-tier* degradation rather than a different shape. So their
    // coverage must agree closely, and only the shading inside the band may move.
    //
    // This also guards a much duller failure: a family-C field that rendered
    // almost no coverage would make every downstream pass early-out, and the
    // benchmark would report it as a large and entirely fictional speed-up.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const decodeAlpha = (capture: { width: number; height: number; pixels: string }): number[] => {
      const bytes = Buffer.from(capture.pixels, "base64");
      const alpha: number[] = [];
      for (let i = 3; i < bytes.length; i += 4) alpha.push(bytes[i] ?? 0);
      return alpha;
    };

    const d = decodeAlpha(
      await page.evaluate(() => window.vitrea.renderScene("field-mask", "rsupn")),
    );
    const c = decodeAlpha(
      await page.evaluate(() => window.vitrea.renderScene("field-mask", "rsup")),
    );

    expect(c).toHaveLength(d.length);

    const covered = (values: number[]): number =>
      values.reduce((sum, alpha) => sum + alpha, 0) / 255;
    const coveredD = covered(d);
    const coveredC = covered(c);
    expect(coveredD, "family D covered nothing").toBeGreaterThan(1000);

    // Within a fraction of a percent: the zero level set is shared, so only the
    // antialiased boundary pixels may differ at all.
    const ratio = coveredC / coveredD;
    expect(
      ratio,
      `family C covered ${coveredC.toFixed(0)} px against family D's ${coveredD.toFixed(0)}`,
    ).toBeGreaterThan(0.995);
    expect(ratio).toBeLessThan(1.005);
  });
});
