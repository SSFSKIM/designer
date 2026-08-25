/**
 * The isolation proof (Decision Log #31(a), user-directed).
 *
 * Eight goldens went stale when C9a tuned the material, and the parent refused to
 * re-baseline them on the strength of "the tint changed, so of course they moved."
 * The gate is this: **render every golden scene with the OLD profile values
 * injected through the `materialProfile` seam, and require the result to be
 * byte-identical to the goldens the new baseline replaces.** Identity attributes
 * the entire visual delta to exactly the two constants C9a moved. Any residual
 * means something unintended moved with them, and is investigated before anything
 * is re-baselined.
 *
 * ## Why this stays in the suite after the re-baseline
 *
 * The obvious shape — compare an old-profile render against the old golden PNGs —
 * can only run once, because the PNGs are about to be overwritten. So the
 * baseline is carried as **hashes of the pre-C9a pixel bytes** instead: nine short
 * strings rather than nine more images, recorded at the moment the proof was run
 * and never regenerated. That makes the attribution reproducible rather than a
 * paragraph in a commit message, and it keeps working as a regression guard: any
 * future change that moves a golden *other* than through the material profile
 * fails here too, because the old-profile render would stop matching a hash taken
 * before that change existed.
 *
 * Hashing the raw RGBA readback rather than the encoded PNG deliberately: the
 * bytes are what the renderer produced, and a PNG encoder's choices are not part
 * of the claim.
 */

import { createHash } from "node:crypto";

import { expect, test } from "@playwright/test";

import { SCENES } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

/**
 * The material as it stood before C9a, as a patch over today's defaults.
 *
 * Exactly the two constants C9a moved, from `git show 1d4545e^` — the tint alpha
 * (0.28 → 0.62) and the light-backdrop end of the adaptive crossover, whose old
 * value `SRGB_DARK_TINT` = [0.09, 0.09, 0.1] is what made the tint invert against
 * the backdrop. The dark end was white then and is white now, and the crossover
 * band (0.12 / 0.42) never moved, so neither is restated here: a patch that named
 * unchanged fields would weaken the claim rather than strengthen it, because
 * identity would no longer tell "these two constants" apart from "these five".
 */
const PRE_C9A_PROFILE = {
  optics: { regular: { tintAlpha: 0.28 } },
  // srgbToLinear([0.09, 0.09, 0.1]), computed here rather than imported so the
  // patch is a literal a reader can check against the old source.
  adaptiveTintLight: [0.008540382112116999, 0.008540382112116999, 0.010022825574869039],
} as const;

/**
 * SHA-256 of each scene's pre-C9a RGBA readback, recorded 2026-08-25 on this
 * machine's `apple / metal-3` adapter through Playwright's full Chromium binary.
 *
 * These ARE the goldens that C9d replaced: every one of them was verified equal to
 * the committed `e2e/goldens/*.png` of the moment, before regeneration, which is
 * the proof itself. §Calibration keys results by adapter class, so a different GPU
 * is expected to move them — this file is a same-machine attribution, not a
 * cross-hardware claim.
 */
const PRE_C9A_HASHES: Readonly<Record<string, string>> = {
  "field-mask": "532584d4daebd7a1c93f90191e64f19f",
  "refraction-checkerboard": "e18f05b87024069ca806bdcce24d85c6",
  "lens-size-scaling": "bd3f42d122eae08df677d36f0dbe93c1",
  "tint-adaptation-light": "adb3f1ada4ecbd31d4221bb414f83c42",
  "tint-adaptation-dark": "f10e9033dc5b3846ff90c352bcd6cc1c",
  "rim-two-references": "889c2dab911df9a3f68dfde8698ef855",
  "concentric-nesting": "59e00a6cae5b199c5f254934859221f1",
  "union-pair": "5ed83d006fa1c5cf95d0acd30bda8e66",
  "highlight-press-glow": "0b9dc460a6616c5a3d6fb69a6b97a783",
};

const hashOf = (raster: Raster): string =>
  createHash("sha256").update(raster.data).digest("hex").slice(0, 32);

test.describe("@golden the C9a delta is exactly the two tuned constants", () => {
  for (const scene of SCENES.filter((candidate) => candidate.measureOnly !== true)) {
    test(`${scene.name} reproduces its pre-C9a bytes from the old profile`, async ({ page }) => {
      const report = await openHarness(page);
      requireHardwareAdapter(report);

      const before = decodeCapture(
        await page.evaluate(
          ([name, profile]) => window.vitrea.renderScene(name as string, undefined, profile),
          [scene.name, PRE_C9A_PROFILE] as const,
        ),
      );

      expect(
        hashOf(before),
        `${scene.name}: rendering with the pre-C9a profile must reproduce the pre-C9a bytes`,
      ).toBe(PRE_C9A_HASHES[scene.name]);
    });
  }

  test("and the tuned profile is not the old one — the proof is not vacuous", async ({ page }) => {
    // Without this, every assertion above would pass just as happily if the
    // `materialProfile` argument were being dropped on the floor.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const before = decodeCapture(
      await page.evaluate(
        (profile) => window.vitrea.renderScene("tint-adaptation-light", undefined, profile),
        PRE_C9A_PROFILE,
      ),
    );
    const after = decodeCapture(
      await page.evaluate(() => window.vitrea.renderScene("tint-adaptation-light")),
    );

    expect(hashOf(before)).not.toBe(hashOf(after));
  });
});
