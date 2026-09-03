/**
 * The attribution capture (W15 G2; claims §5.70 §8) — an instrument, not a golden.
 *
 * A golden that moves at a landing is attributed by measurement, never re-recorded
 * blind: the scene is rendered on the tree before the merge and on the tree
 * after, and the two readbacks are diffed pixel for pixel, so the proof's new hash
 * carries a count, a magnitude and a bounding box beside it. This spec is that
 * capture. It renders every golden scene under the isolation proof's named
 * profile (the outer shadow declined) and under the default profile and writes
 * both as PNGs to `$VITREA_ATTRIB_OUT`; `results/2026-09-04-w15-body-2x/g2/
 * attribute-goldens.py` reads two such directories and prints the table. It runs
 * only when that variable is set, so the ordinary suites never write anywhere.
 */
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { PNG } from "pngjs";
import { test } from "@playwright/test";
import { SCENES } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter } from "../support";

const OUT = process.env.VITREA_ATTRIB_OUT;
const DECLINED = {
  optics: { regular: { tintAlpha: 0.28 } },
  adaptiveTintLight: [0.008540382112116999, 0.008540382112116999, 0.010022825574869039],
  outerShadow: {
    thinOcclusionDark: 0, thinOcclusionMid: 0, thinOcclusionBright: 0,
    thickOcclusionAt96: 0, thickOcclusionAt128: 0, thickOcclusionAt160: 0, liftAmplitude: 0,
  },
} as const;

test("@attrib write every golden scene's declined and default readbacks", async ({ page }) => {
  test.skip(OUT === undefined, "set VITREA_ATTRIB_OUT to a directory to capture");
  const out = OUT as string;
  test.setTimeout(120_000);
  const report = await openHarness(page);
  requireHardwareAdapter(report);
  mkdirSync(out, { recursive: true });
  for (const scene of SCENES.filter((s) => s.measureOnly !== true)) {
    for (const [tag, profile] of [["declined", DECLINED], ["default", undefined]] as const) {
      const raster = decodeCapture(
        await page.evaluate(
          ([name, p]) => window.vitrea.renderScene(name, undefined, p),
          [scene.name, profile] as const,
        ),
      );
      const png = new PNG({ width: raster.width, height: raster.height });
      png.data = Buffer.from(raster.data);
      writeFileSync(join(out, `${scene.name}__${tag}.png`), PNG.sync.write(png));
    }
  }
});
