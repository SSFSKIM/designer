/**
 * The golden suite — §Testing's "headless golden-image tests (sRGB-locked)".
 *
 * Each scene isolates one mechanism, so a failure says *which* thing changed:
 * the field and the corner algebra (`field-mask`), the displacement (`refraction-
 * checkerboard`), the size parameterisation (`lens-size-scaling`), the adaptation
 * path including its readback (`tint-adaptation-*`), the two corner references
 * (`rim-two-references`), X8 rider 2 (`concentric-nesting`), the bounded union
 * (`union-pair`), and the highlight canvas (`highlight-press-glow`).
 *
 * Regenerate with:
 *
 *     VITREA_UPDATE_GOLDENS=1 pnpm --filter @vitrea/renderer-webgpu test:golden
 *
 * The goldens in `e2e/goldens/` were produced on this machine's `apple / metal-3`
 * adapter through Playwright's full Chromium binary. §Calibration's own model keys
 * results by adapter class, so regenerating them on different hardware is expected
 * to move some pixels; the tolerance below is what says how much is a rounding
 * difference and how much is a change in the optics.
 */

import { createHash } from "node:crypto";
import { expect, test } from "@playwright/test";

import { SCENES } from "../fixtures/scenes";
import {
  assertNotBlank,
  compare,
  decodeCapture,
  openHarness,
  readGolden,
  requireHardwareAdapter,
  UPDATING_GOLDENS,
  writeGolden,
} from "../support";

/**
 * Tolerance. Tight enough that a changed transfer function (which moves midtones
 * by tens of code units), a changed corner fit (which moves the silhouette by a
 * whole pixel at the corners) or a changed lens profile all fail; loose enough to
 * absorb the last-bit differences between two runs on the same adapter.
 */
const MAX_CHANNEL_DELTA = 4;
const MAX_MEAN_DELTA = 0.35;
const MAX_OUTLIER_FRACTION = 0.02;

test.describe("@golden sRGB-locked scenes", () => {
  for (const scene of SCENES.filter((candidate) => candidate.measureOnly !== true)) {
    test(`${scene.name} matches its golden`, async ({ page }) => {
      const report = await openHarness(page);
      requireHardwareAdapter(report);

      const capture = await page.evaluate(
        (name) => window.vitrea.renderScene(name),
        scene.name,
      );
      const actual = decodeCapture(capture);

      expect(actual.width).toBe(Math.round(scene.widthCss * scene.devicePixelRatio));
      expect(actual.height).toBe(Math.round(scene.heightCss * scene.devicePixelRatio));
      assertNotBlank(actual, scene.name);

      if (UPDATING_GOLDENS) {
        writeGolden(scene.name, actual);
        test.info().annotations.push({ type: "golden", description: `wrote ${scene.name}.png` });
        return;
      }

      const expected = readGolden(scene.name);
      expect(
        expected,
        `No golden for "${scene.name}". Regenerate with VITREA_UPDATE_GOLDENS=1.`,
      ).toBeDefined();
      if (expected === undefined) return;

      const difference = compare(actual, expected);
      expect(difference.maxChannelDelta, `${scene.name}: max channel delta`).toBeLessThanOrEqual(
        MAX_CHANNEL_DELTA,
      );
      expect(difference.meanChannelDelta, `${scene.name}: mean channel delta`).toBeLessThanOrEqual(
        MAX_MEAN_DELTA,
      );
      expect(difference.outlierFraction, `${scene.name}: outlier pixels`).toBeLessThanOrEqual(
        MAX_OUTLIER_FRACTION,
      );
    });
  }
});

test.describe("@golden the goldens are distinguishable", () => {
  test("two scenes that should differ do differ", async ({ page }) => {
    // A golden suite where every scene renders the same thing would pass for the
    // wrong reason. The light and dark adaptation scenes share a geometry and
    // differ only in the backdrop's luminance, so they are the sharpest pair to
    // check the suite is measuring anything at all.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const light = decodeCapture(
      await page.evaluate(() => window.vitrea.renderScene("tint-adaptation-light")),
    );
    const dark = decodeCapture(
      await page.evaluate(() => window.vitrea.renderScene("tint-adaptation-dark")),
    );

    const difference = compare(light, dark, 8);
    expect(difference.maxChannelDelta).toBeGreaterThan(24);
  });
});

test.describe("@golden acceptance #2 — lensing scales with surface size", () => {
  test("a larger surface bends a deeper band of the same backdrop", async ({ page }) => {
    // The golden says the pixels are what they were; this says which way the
    // mechanism runs. Measured as the DEPTH of the band that moves when
    // refraction is switched off — moved pixels over perimeter — which is the
    // lens depth itself. A mean over each surface's area would report the
    // opposite, because the lens occupies a larger fraction of a small surface.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const lensing = await page.evaluate(() => window.vitrea.measureLensing("lens-size-depth"));
    const narrow = lensing.narrow;
    const wide = lensing.wide;

    expect(narrow, "narrow group was not measured").toBeDefined();
    expect(wide, "wide group was not measured").toBeDefined();
    if (narrow === undefined || wide === undefined) return;

    expect(narrow.maxDelta, "the narrow surface lenses at all").toBeGreaterThan(8);
    expect(wide.maxDelta, "the wide surface lenses at all").toBeGreaterThan(8);

    // material.ts resolves 11.25 CSS px of depth for the 36 px span and 25 for
    // the 400 px one (W12 G2: the reference's height law at thickness 10). The
    // assertion is the ratio, not the absolute number, so recalibrating the law
    // (C7's job) moves the numbers and not the property.
    expect(
      wide.depthCss,
      `wide group's lens depth (${wide.depthCss.toFixed(2)} CSS px) should exceed the narrow group's (${narrow.depthCss.toFixed(2)} CSS px)`,
    ).toBeGreaterThan(narrow.depthCss * 1.5);
  });
});

/**
 * SHA-256 of `placed-checkerboard` rendered with its placement WITHHELD — the
 * texture cover-fit to the viewport, which is what every texture backdrop got
 * before claims §5.47. Recorded on this machine's `apple / metal-3` adapter the
 * day the placed fit landed, and never regenerated: it is the fail-before
 * record, the render the golden replaced.
 */
const PLACED_CHECKERBOARD_COVER_HASH = "a0cd4e7b1b08ffeeb4ec341fcb060e27";

/**
 * The cover-fit hash above was `e1383ed6f133d99d19b7e44b73022749` when the
 * placed fit landed. W12 G2 (claims §5.51) changed the lens's shape, and the
 * cover-fit render carries the lens like the placed one does, so the record
 * moved with it and was re-recorded in the same run as the golden — the
 * attribution of that change is the isolation proof's `W12_G2_HASHES`, not
 * this constant, which only says the two fits still differ by the fit alone.
 *
 * It moved again for the same reason in the W12 ω 0.8 A/B round (Decision Log 4:
 * `lensOvalization` 0.6 → 0.8, `84d9a10e3b866580c15dfce961a888ac` → the value
 * below), whose attribution is `W12_G2B_HASHES` in the isolation proof.
 *
 * And again at W14 G2 (claims §5.66; `e9224420043e4362d343f39485490052` → the
 * value below): the outer shadow became the reference's two-term composite,
 * and the cover-fit render casts that shadow like the placed one does. The
 * attribution is the isolation proof's `W14_HASHES` and the goldens regenerated
 * behind it; this constant still says only that the two fits differ by the fit.
 *
 * And at W15 G2 (claims §5.70 §8; `7980eed23df12794a7608b12a4d66a48` → the value
 * below): the 2x body took its second scale — the widths in device pixels, the
 * deep value fully heavy, the ramp the whole body above it — and this scene
 * renders at ratio 2, so the cover-fit render's body moved like the placed
 * one's. The attribution is `W15_G2_HASHES` and `results/2026-09-04-w15-body-2x/
 * g2/attribution.txt` (30 502 of 96 000 pixels by up to 19 codes on the placed
 * render, inside the surface, alpha untouched). The same landing lowered the
 * "different pictures" bound below from 24 to 16 codes: a deeper 2x body blurs
 * the stretched squares and the 8 px squares more alike deep inside the surface,
 * and the two fits now differ by 22 codes at most (0.147 of the pixels beyond 8)
 * where they differed by more than 24 before. The bound's job is to say the two
 * renders are not the same picture, which 22 codes on a seventh of the pixels
 * does; the hash below is what says the cover render is exactly the record.
 */

test.describe("@golden claims §5.47 — a backdrop is sampled where it sits", () => {
  test("the placed render is the golden, and the cover-fit render is what it replaced", async ({
    page,
  }) => {
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const placed = decodeCapture(
      await page.evaluate(() => window.vitrea.renderScene("placed-checkerboard")),
    );
    const cover = decodeCapture(
      await page.evaluate(() =>
        window.vitrea.renderScene("placed-checkerboard", undefined, undefined, {
          ignorePlacement: true,
        }),
      ),
    );

    // Different pictures: the placed render shows 8 px squares under the surface
    // and clamps past the texture's edge; the cover render stretched the same
    // 96 texels over 200×120 CSS px.
    const difference = compare(placed, cover, 8);
    expect(difference.maxChannelDelta).toBeGreaterThan(16);
    expect(difference.outlierFraction).toBeGreaterThan(0.05);

    // And the cover render is exactly the render the golden replaced, so the
    // golden's whole delta is the fit and nothing else travelled with it.
    const hash = createHash("sha256").update(cover.data).digest("hex").slice(0, 32);
    expect(hash).toBe(PLACED_CHECKERBOARD_COVER_HASH);
  });
});
