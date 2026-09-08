/**
 * W24 G2 — the goldens' attribution at the LANDED constants (X2).
 *
 * The wave's X2 asks that every golden that moves be attributable to the two mechanisms and to
 * nothing else. This spec is the measurement behind that claim, and it is deliberately not
 * `isolation.spec.ts`: that proof pins BYTES at a named profile and answers "did anything move",
 * while the question here is "where did it move, and by how much" — a lit edge that lands correctly
 * must move the contour band and nothing else, and only a per-pixel comparison can say so.
 *
 * For each golden scene it renders the LANDED defaults (an empty patch) and then each mechanism
 * DECLINED, through the same `renderScene(name, undefined, profile)` seam the isolation proof uses,
 * and reports the largest 8-bit channel delta INSIDE the contour band (within 3 CSS px of a
 * coverage discontinuity) and the largest OUTSIDE it, with the count of pixels that moved on each
 * side. The lit edge's outside delta must be 0 on every scene; the transmission's must be 0
 * everywhere except inside the collapsed surfaces of `collapsed-tone-textured`, which is the whole
 * reason that scene was added.
 *
 * The band is computed from the shipped render's own alpha channel rather than from geometry: a
 * pixel is "in the band" when it is within 3 px of a pixel whose coverage differs from its own by
 * more than a code, which is the contour wherever a surface has one and is empty where none does.
 *
 * This file is EVIDENCE, not a suite member. It lives under the gate's results directory and is
 * copied into `e2e/golden/` by `golden-ladder.sh` for the length of one run; committing it to the
 * suite would pin a scratch constant into CI.
 */

import { expect, test } from "@playwright/test";

import { SCENES } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

/** The ladder's points, named exactly as the capture ladder names them. */
const POINTS: ReadonlyArray<readonly [string, object]> = [
  ["landed (empty patch)", {}],
  // The lit edge declined. Its delta against the landed render IS the lit edge, per scene.
  ["rimLitExponent 0", { optics: { regular: { rimLitExponent: 0 } } }],
  // The transmission declined, both anchors. Its delta is the transmission.
  ["collapseTransmission 0", { collapseTransmission: 0, collapseTransmission2x: 0 }],
  // Both declined together — the W23 material, which is what the re-recorded goldens are measured
  // against as a whole.
  [
    "both declined (the W23 material)",
    {
      optics: { regular: { rimLitExponent: 0 } },
      collapseTransmission: 0,
      collapseTransmission2x: 0,
    },
  ],
];

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

function compare(base: Raster, other: Raster, band: Uint8Array): {
  inBand: number;
  outside: number;
  movedInBand: number;
  movedOutside: number;
} {
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

test.describe("@golden W24 the two mechanisms' reach on every golden", () => {
  test("each mechanism moves what it can reach and nothing else", async ({ page }) => {
    test.setTimeout(180_000);
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const lines: string[] = [];
    const say = (text: string): void => {
      lines.push(text);
      // eslint-disable-next-line no-console
      console.log(text);
    };
    say("W24 G2 — the two mechanisms' reach on every golden, at the landed constants");
    say("");
    say("`inBand` / `outside` are the largest 8-bit channel delta against the LANDED render,");
    say("inside and outside the contour band (3 px of a coverage discontinuity). `movedOutside` is");
    say("the count of pixels outside the band that moved at all.");
    say("");
    say("The lit edge wants movedOutside 0 on every scene. The transmission is allowed to move the");
    say("INTERIOR of a collapsed surface over a textured backdrop, which is only");
    say("`collapsed-tone-textured`, and nothing at all anywhere else.");
    say("");
    say(
      `${"scene".padEnd(26)} ${"point".padEnd(22)} ${"inBand".padStart(7)} ` +
        `${"outside".padStart(8)} ${"movedIn".padStart(8)} ${"movedOut".padStart(9)}`,
    );

    let worstOutside = 0;
    let worstOutsideLitEdge = 0;
    for (const scene of SCENES.filter((candidate) => candidate.measureOnly !== true)) {
      const shipped = decodeCapture(
        await page.evaluate(
          ([name, profile]) => window.vitrea.renderScene(name as string, undefined, profile),
          [scene.name, {}] as const,
        ),
      );
      const band = contourBand(shipped);
      for (const [label, patch] of POINTS.slice(1)) {
        const other = decodeCapture(
          await page.evaluate(
            ([name, profile]) => window.vitrea.renderScene(name as string, undefined, profile),
            [scene.name, patch] as const,
          ),
        );
        const d = compare(shipped, other, band);
        worstOutside = Math.max(worstOutside, d.outside);
        if (label === "rimLitExponent 0") worstOutsideLitEdge = Math.max(worstOutsideLitEdge, d.outside);
        say(
          `${scene.name.padEnd(26)} ${label.padEnd(22)} ${String(d.inBand).padStart(7)} ` +
            `${String(d.outside).padStart(8)} ${String(d.movedInBand).padStart(8)} ` +
            `${String(d.movedOutside).padStart(9)}`,
        );
      }
    }
    say("");
    say(
      "the largest movement outside any contour band, over every scene and every point: " +
        `${worstOutside}`,
    );
    say(`the lit edge's own largest movement outside a contour band: ${worstOutsideLitEdge}`);
    expect(worstOutsideLitEdge, "the lit edge moved a pixel the rim cannot reach").toBe(0);
  });
});
