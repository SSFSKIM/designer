/**
 * W23 G1 (g) — the goldens' attribution for the LANDED rim law (X2).
 *
 * The isolation proof answers "did anything move" by pinning bytes at a named profile. This answers
 * "where did it move, and by how much", which is what X2 actually asks: a rim law that lands
 * correctly moves the contour band and nothing else, and only a per-pixel comparison can say so.
 *
 * G0 measured the same thing against the SHIPPED defaults, because at G0 the constants were all 0
 * and the shipped render was the before. Here the shipped render IS the after, so the before is
 * built explicitly: the same `PRE_C9A_PROFILE` the isolation proof renders through, with the rim's
 * five constants set back to what they were on 2026-09-08 before this gate. The two renders differ
 * in the rim law and in nothing else, which is exactly the attribution the re-recorded hashes need.
 *
 * The band is computed from the before render's own alpha channel rather than from geometry: a
 * pixel is "in the band" when it is within 3 px of a pixel whose coverage differs from its own by
 * more than a code — the contour wherever a surface has one, and empty where none does.
 *
 * This file is EVIDENCE, not a suite member. `g1-goldens.sh` copies it into `e2e/golden/` for the
 * length of one run; committing it would pin this gate's before-constants into CI.
 */

import { expect, test } from "@playwright/test";

import { SCENES } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

/**
 * The profile the isolation proof renders every golden through, restated here so the attribution
 * is measured on the same material the pinned hashes are.
 */
const PRE_C9A_PROFILE = {
  optics: { regular: { tintAlpha: 0.28 } },
  adaptiveTintLight: [0.94, 0.94, 0.94] as const,
  outerShadow: {
    thinOcclusionDark: 0,
    thinOcclusionMid: 0,
    thinOcclusionBright: 0,
    thickOcclusionAt96: 0,
    thickOcclusionAt128: 0,
    thickOcclusionAt160: 0,
    liftAmplitude: 0,
    reducedTransparencyOcclusion: 0,
  },
};

/** The rim as it stood before this gate: an additive constant, one band, no collapsed rim. */
const BEFORE = {
  ...PRE_C9A_PROFILE,
  optics: {
    regular: { tintAlpha: 0.28, rimAlpha: 0.18, rimLevelGain: 0, rimWidth2x: 1.5 },
    clear: { rimWidth2x: 1.25 },
  },
  rimCollapsed: 0,
  rimCollapsedTinted: 0,
};

/** Pixels within `reach` px of a coverage discontinuity in the before render. */
function contourBand(raster: Raster, reach = 3): Uint8Array {
  const { width, height, data } = raster;
  const edge = new Uint8Array(width * height);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const i = (y * width + x) * 4 + 3;
      const a = data[i] ?? 0;
      const right = x + 1 < width ? (data[i + 4] ?? 0) : a;
      const down = y + 1 < height ? (data[i + width * 4] ?? 0) : a;
      if (Math.abs(a - right) > 1 || Math.abs(a - down) > 1) edge[y * width + x] = 1;
    }
  }
  const band = new Uint8Array(width * height);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if (edge[y * width + x] !== 1) continue;
      for (let dy = -reach; dy <= reach; dy += 1) {
        for (let dx = -reach; dx <= reach; dx += 1) {
          const ny = y + dy;
          const nx = x + dx;
          if (ny < 0 || nx < 0 || ny >= height || nx >= width) continue;
          band[ny * width + nx] = 1;
        }
      }
    }
  }
  return band;
}

function compare(
  base: Raster,
  other: Raster,
  band: Uint8Array,
): { inBand: number; outside: number; movedInBand: number; movedOutside: number } {
  let inBand = 0;
  let outside = 0;
  let movedInBand = 0;
  let movedOutside = 0;
  for (let p = 0; p < band.length; p += 1) {
    let worst = 0;
    for (let c = 0; c < 4; c += 1) {
      worst = Math.max(worst, Math.abs((base.data[p * 4 + c] ?? 0) - (other.data[p * 4 + c] ?? 0)));
    }
    if (band[p] === 1) {
      inBand = Math.max(inBand, worst);
      if (worst > 0) movedInBand += 1;
    } else {
      outside = Math.max(outside, worst);
      if (worst > 0) movedOutside += 1;
    }
  }
  return { inBand, outside, movedInBand, movedOutside };
}

test.describe("@golden W23 G1 the landed rim law's reach on every golden", () => {
  test("the rim law moves the contour band and nothing else", async ({ page }) => {
    test.setTimeout(300_000);
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const say = (text: string): void => {
      // eslint-disable-next-line no-console
      console.log(text);
    };
    say("W23 G1 — the landed rim law's reach on every golden, against the pre-W23 rim");
    say("");
    say("`inBand` / `outside` are the largest 8-bit channel delta between the pre-W23 rim and the");
    say("landed one, inside and outside the contour band (3 px of a coverage discontinuity).");
    say("`movedOut` is the count of pixels outside the band that moved at all: X2 wants it 0.");
    say("");
    say(
      `${"scene".padEnd(26)} ${"inBand".padStart(7)} ${"outside".padStart(8)} ` +
        `${"movedIn".padStart(8)} ${"movedOut".padStart(9)}`,
    );

    let worstOutside = 0;
    for (const scene of SCENES.filter((candidate) => candidate.measureOnly !== true)) {
      const before = decodeCapture(
        await page.evaluate(
          ([name, profile]) => window.vitrea.renderScene(name as string, undefined, profile),
          [scene.name, BEFORE] as const,
        ),
      );
      const after = decodeCapture(
        await page.evaluate(
          ([name, profile]) => window.vitrea.renderScene(name as string, undefined, profile),
          [scene.name, PRE_C9A_PROFILE] as const,
        ),
      );
      const band = contourBand(before);
      const d = compare(before, after, band);
      worstOutside = Math.max(worstOutside, d.outside);
      say(
        `${scene.name.padEnd(26)} ${String(d.inBand).padStart(7)} ${String(d.outside).padStart(8)} ` +
          `${String(d.movedInBand).padStart(8)} ${String(d.movedOutside).padStart(9)}`,
      );
    }
    say("");
    say(`the largest movement outside any contour band, over every scene: ${worstOutside}`);
    expect(worstOutside, "a golden moved a pixel the rim cannot reach — W23 G1 stop S4").toBeLessThanOrEqual(1);
  });
});
