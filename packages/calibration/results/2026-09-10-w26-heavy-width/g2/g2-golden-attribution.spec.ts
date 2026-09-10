/**
 * W26 G2 — the goldens' attribution at the landed heavy width (X2, and this wave's S13).
 *
 * Two constants land — `sizeHeavyTapSigma` and `sizeHeavyTapSigma2x`, both 0 → 9 — and S13 asks
 * that every golden that moves be attributable to them and to nothing else. W25 G3's spec is the
 * ancestor and the question has changed shape with the mechanism: that wave landed a RIM factor and
 * asked whether the delta stayed inside a contour band. This wave lands a BODY width, so the delta
 * belongs inside the drawn area of a glass surface and the band split is a second reading rather
 * than the assertion.
 *
 * For each golden scene it renders the landed defaults (an empty patch) and then both anchors
 * declined to 0, through the same `renderScene(name, undefined, profile)` seam the isolation proof
 * uses, and reports the largest 8-bit channel delta INSIDE the surfaces' own drawn area and the
 * largest OUTSIDE it, with the pixel counts on each side, the contour band's own reading beside
 * them, and the scene's thickest span.
 *
 * **The prediction, and it is structural rather than hoped for.** The optics canvas is transparent
 * where no surface draws, and the heavy width only ever changes what a surface's body samples, so
 * **the delta outside the drawn area must be exactly 0 on every scene**. That is the assertion.
 *
 * **What this wave does NOT assert, and the reason is a measurement.** W25's spec asserted that a
 * scene whose every surface is thinner than `sizeSpanMin` = 32 moves not one pixel, because that
 * wave's factor carried `sizeThickness` and is exactly 0 there. The heavy width carries no such
 * factor: `sizeScatterFloor` is 0.4, so a 32 px surface still draws four tenths of its body through
 * the heavy component and a thin scene is EXPECTED to move. The thin claim is carried by the bed
 * instead, where X5 bounds every cell at or below span 44 at 0.001 OKLab ΔE on both tiers — and the
 * thin scenes' readings are printed here so the two can be read against each other.
 *
 * The drawn area is the shipped render's own alpha rather than geometry: a pixel is "drawn" when
 * its alpha is non-zero in either render, which is exactly the set a surface can reach.
 *
 * This file is EVIDENCE, not a suite member. It lives under the gate's results directory and is
 * copied into `e2e/golden/` by `g2-goldens.sh` for the length of one run; committing it to the
 * suite would pin a scratch constant into CI.
 */

import { expect, test } from "@playwright/test";

import { SCENES } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

/**
 * The one point on the ladder: both anchors declined to 0, which is the 0.14.0 material exactly —
 * at σ 0 the pyramid allocates no heavy texture and encodes no heavy pass, and the optics pass
 * takes the single `textureSampleLevel` of the chain it has always taken. Declining ONE anchor
 * would not do it: `rampAtScale` would then carry the other one's value down or up to this scale
 * and the render would be neither material (W26 Decision Log 6 (c) — the mechanism has no small
 * values, and a lone anchor is the same trap wearing a different name).
 */
const DECLINED = { sizeHeavyTapSigma: 0, sizeHeavyTapSigma2x: 0 };

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

/** Pixels a surface draws on, in either render — the set the body can reach. */
function drawnArea(a: Raster, b: Raster): Uint8Array {
  const drawn = new Uint8Array(a.width * a.height);
  for (let p = 0; p < drawn.length; p += 1) {
    drawn[p] = (a.data[p * 4 + 3] ?? 0) > 0 || (b.data[p * 4 + 3] ?? 0) > 0 ? 1 : 0;
  }
  return drawn;
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

interface Split {
  readonly inside: number;
  readonly outside: number;
  readonly movedInside: number;
  readonly movedOutside: number;
}

function compare(base: Raster, other: Raster, mask: Uint8Array): Split {
  let inside = 0;
  let outside = 0;
  let movedInside = 0;
  let movedOutside = 0;
  for (let p = 0; p < mask.length; p += 1) {
    let worst = 0;
    for (let c = 0; c < 4; c += 1) {
      worst = Math.max(worst, Math.abs((base.data[p * 4 + c] ?? 0) - (other.data[p * 4 + c] ?? 0)));
    }
    if (mask[p] === 1) {
      inside = Math.max(inside, worst);
      if (worst > 0) movedInside += 1;
    } else {
      outside = Math.max(outside, worst);
      if (worst > 0) movedOutside += 1;
    }
  }
  return { inside, outside, movedInside, movedOutside };
}

test.describe("@golden W26 the heavy width's reach on every golden", () => {
  test("moves a surface's body and nothing off a surface", async ({ page }) => {
    test.setTimeout(180_000);
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const say = (text: string): void => {
      // eslint-disable-next-line no-console
      console.log(text);
    };
    say("W26 G2 — the heavy width's reach on every golden, at the landed 9 / 9");
    say("");
    say("`drawn` / `off` are the largest 8-bit channel delta against the LANDED render, inside and");
    say("outside the set of pixels a surface draws on; `band` is the same delta inside the contour");
    say("band (3 px of a coverage discontinuity), printed beside them because this wave's mechanism");
    say("is a BODY width and the band is a reading rather than the claim. `span` is the scene's");
    say("thickest surface's short side in CSS px; unlike W25's field the heavy component has a");
    say("floor of 0.4 and reaches every span, so a thin scene is expected to move.");
    say("");
    say(
      `${"scene".padEnd(26)} ${"span".padStart(5)} ${"drawn".padStart(6)} ${"off".padStart(4)} ` +
        `${"band".padStart(5)} ${"movedIn".padStart(8)} ${"movedOff".padStart(9)}`,
    );

    let worstOff = 0;
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
      const drawn = drawnArea(shipped, other);
      const d = compare(shipped, other, drawn);
      const band = compare(shipped, other, contourBand(shipped));
      const span = thickestSpan(scene);
      worstOff = Math.max(worstOff, d.outside);
      if (span <= SPAN_MIN) worstThin = Math.max(worstThin, d.inside);
      say(
        `${scene.name.padEnd(26)} ${String(span).padStart(5)} ${String(d.inside).padStart(6)} ` +
          `${String(d.outside).padStart(4)} ${String(band.inside).padStart(5)} ` +
          `${String(d.movedInside).padStart(8)} ${String(d.movedOutside).padStart(9)}`,
      );
    }
    say("");
    say(`the largest movement off any surface, on any scene: ${worstOff}`);
    say(`the largest movement on a scene whose thickest span is at or below 32: ${worstThin}`);
    expect(worstOff, "the heavy width moved a pixel no surface draws on").toBe(0);
  });
});
