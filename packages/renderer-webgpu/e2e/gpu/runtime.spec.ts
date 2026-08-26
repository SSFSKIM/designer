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

test.describe("@gpu the governor's resolution rungs", () => {
  test("rungs 2 and 3 render the same material through a coarser field", async ({ page }) => {
    // `refractionResolutionScale` was defined and never read: rungs 2 and 3 used
    // to deliver a cadence saving and nothing else. Now they rasterise the
    // group's field targets below device resolution, and the optics and highlight
    // passes filter what they read — a shader branch that exists only under the
    // knob and is therefore compiled and run nowhere else.
    //
    // Two things have to hold, and they pull in opposite directions. The rung
    // must actually change the output, or the knob is still inert; and it must
    // still render the same material, or the ladder's "within a tier" promise is
    // a fiction. So this measures coverage rather than bytes: the silhouette is
    // the material's identity, and the interior shading is what a coarser field
    // is allowed to move.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const capture = async (level: number) =>
      Buffer.from(
        (
          await page.evaluate(
            (rung) => window.vitrea.renderAtGovernorLevel("refraction-checkerboard", rung),
            level,
          )
        ).pixels,
        "base64",
      );

    const nominal = await capture(0);
    const rung2 = await capture(2);
    const rung3 = await capture(3);

    // Nothing the device could not do: a validation failure here draws nothing
    // and reports nothing unless asked.
    const errors = await page.evaluate(() => window.vitrea.errors());
    expect(errors, `WebGPU reported: ${errors.join(" | ")}`).toEqual([]);

    const covered = (bytes: Buffer): number => {
      let sum = 0;
      for (let i = 3; i < bytes.length; i += 4) sum += bytes[i] ?? 0;
      return sum / 255;
    };
    const changed = (a: Buffer, b: Buffer): number => {
      let moved = 0;
      for (let i = 0; i < a.length; i += 4) {
        for (let channel = 0; channel < 3; channel += 1) {
          if (Math.abs((a[i + channel] ?? 0) - (b[i + channel] ?? 0)) > 2) {
            moved += 1;
            break;
          }
        }
      }
      return moved;
    };

    const base = covered(nominal);
    expect(base, "the nominal rung covered nothing").toBeGreaterThan(1000);

    for (const [level, coarse] of [
      [2, rung2],
      [3, rung3],
    ] as const) {
      // Same silhouette: the group covers the pixels it always did.
      const ratio = covered(coarse) / base;
      expect(ratio, `rung ${level} coverage ratio`).toBeGreaterThan(0.98);
      expect(ratio, `rung ${level} coverage ratio`).toBeLessThan(1.02);
      // And the knob is not inert — a coarser field moves the refracted interior.
      expect(changed(nominal, coarse), `rung ${level} changed no pixels`).toBeGreaterThan(100);
    }
  });
});
