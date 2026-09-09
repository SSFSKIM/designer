/**
 * W25 G3 — the goldens' attribution at the LANDED constant (X2, and the wave's S13).
 *
 * One mechanism lands this wave — `optics.regular.rimAlongSideSlope` 0.45, the rim's along-side
 * position field — and S13 asks that every golden that moves be attributable to it and to nothing
 * else: a golden moved outside a thick surface's body or rim stops the change. This spec is the
 * measurement behind that claim. It is deliberately not `isolation.spec.ts`, which pins BYTES at a
 * named profile and answers "did anything move"; the question here is "where did it move, by how
 * much, and on which surfaces".
 *
 * For each golden scene it renders the LANDED defaults (an empty patch) and then the field
 * declined, through the same `renderScene(name, undefined, profile)` seam the isolation proof uses,
 * and reports the largest 8-bit channel delta INSIDE the contour band (within 3 CSS px of a
 * coverage discontinuity) and the largest OUTSIDE it, with the count of pixels that moved on each
 * side and the scene's own thickest span.
 *
 * The two predictions this wave states before the run, and both are structural rather than hoped
 * for. **A scene whose every surface is thinner than `sizeSpanMin` = 32 moves not one pixel**,
 * because the factor is `1 + slope · sizeThickness(span) · field` and `sizeThickness` is exactly 0
 * there. **A scene that does move, moves in its rim**: the field multiplies the rim's amplitude and
 * nothing else, so its delta belongs inside a contour band, and the amount outside one is the
 * refraction path's own displacement reaching past the contour rather than a second mechanism.
 *
 * The band is computed from the shipped render's own alpha channel rather than from geometry: a
 * pixel is "in the band" when it is within 3 px of a pixel whose coverage differs from its own by
 * more than a code, which is the contour wherever a surface has one and is empty where none does.
 *
 * This file is EVIDENCE, not a suite member. It lives under the gate's results directory and is
 * copied into `e2e/golden/` by `g3-goldens.sh` for the length of one run; committing it to the
 * suite would pin a scratch constant into CI.
 */

import { expect, test } from "@playwright/test";

import { SCENES } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

/**
 * The one point on the ladder: the PAIR declined back to the 0.13.0 material — the along-side field
 * to 0 and the lit edge's exponent to W24's 1.15 — whose delta against the shipped render is the
 * joint re-fit and nothing else. W25 G3b declines both together because the two were fitted
 * together (Decision Log 6): a spec that declined only one would attribute the goldens' movement to
 * a constant that did not move alone.
 */
const DECLINED = { optics: { regular: { rimAlongSideSlope: 0, rimLitExponent: 1.15 } } };

/** The band the size law reads: 0 below `sizeSpanMin`, saturated at `sizeSpanMax`. */
const SPAN_MIN = 32;

/** The thickest span in a scene — the short side of its widest-reaching surface, in CSS px. */
function thickestSpan(scene: (typeof SCENES)[number]): number {
  let worst = 0;
  for (const group of scene.groups) {
    for (const surface of group.surfaces) {
      worst = Math.max(worst, Math.min(surface.shape.size[0], surface.shape.size[1]));
    }
  }
  return worst;
}

/** Pixels within `reach` px of a coverage discontinuity in the shipped render. */
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

test.describe("@golden W25 the along-side field's reach on every golden", () => {
  test("moves the rim of a thick surface and nothing on a thin scene", async ({ page }) => {
    test.setTimeout(180_000);
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const lines: string[] = [];
    const say = (text: string): void => {
      lines.push(text);
      // eslint-disable-next-line no-console
      console.log(text);
    };
    say("W25 G3 — the along-side field's reach on every golden, at the landed slope 0.45");
    say("");
    say("`inBand` / `outside` are the largest 8-bit channel delta against the LANDED render,");
    say("inside and outside the contour band (3 px of a coverage discontinuity). `span` is the");
    say("scene's thickest surface's short side in CSS px; below 32 the field is exactly 0 and the");
    say("scene must not move at all.");
    say("");
    say(
      `${"scene".padEnd(26)} ${"span".padStart(5)} ${"inBand".padStart(7)} ` +
        `${"outside".padStart(8)} ${"movedIn".padStart(8)} ${"movedOut".padStart(9)}`,
    );

    let worstThin = 0;
    for (const scene of SCENES.filter((candidate) => candidate.measureOnly !== true)) {
      const shipped = decodeCapture(
        await page.evaluate(
          ([name, profile]) => window.vitrea.renderScene(name as string, undefined, profile),
          [scene.name, {}] as const,
        ),
      );
      const other = decodeCapture(
        await page.evaluate(
          ([name, profile]) => window.vitrea.renderScene(name as string, undefined, profile),
          [scene.name, DECLINED] as const,
        ),
      );
      const band = contourBand(shipped);
      const d = compare(shipped, other, band);
      const span = thickestSpan(scene);
      if (span <= SPAN_MIN) worstThin = Math.max(worstThin, Math.max(d.inBand, d.outside));
      say(
        `${scene.name.padEnd(26)} ${String(span).padStart(5)} ${String(d.inBand).padStart(7)} ` +
          `${String(d.outside).padStart(8)} ${String(d.movedInBand).padStart(8)} ` +
          `${String(d.movedOutside).padStart(9)}`,
      );
    }
    say("");
    say(`the largest movement on any scene whose thickest span is at or below 32: ${worstThin}`);
    expect(worstThin, "the field moved a scene the size law cannot reach").toBe(0);
  });
});
