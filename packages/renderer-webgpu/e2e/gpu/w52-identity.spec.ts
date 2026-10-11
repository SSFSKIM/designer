/** W52 G0: the golden suite's 34 tests include 13 scene rasters; pin those pixels exactly. */
import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { expect, test } from "@playwright/test";
import { SCENES } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter } from "../support";

const prior = JSON.parse(readFileSync(new URL(
  "../../../calibration/results/2026-10-08-w50-g0-declaration/evidence/raw-identity.json",
  import.meta.url,
), "utf8")) as Record<string, string>;

test("@gpu W52 all thirteen default golden rasters retain their exact pre-wave bytes", async ({ page }) => {
  requireHardwareAdapter(await openHarness(page));
  const scenes = SCENES.filter((scene) => scene.measureOnly !== true);
  expect(scenes).toHaveLength(13);
  for (const scene of scenes) {
    const capture = decodeCapture(await page.evaluate((name) => window.vitrea.renderScene(name), scene.name));
    const actual = createHash("sha256").update(capture.data).digest("hex");
    expect(actual, scene.name).toBe(prior[`golden/${scene.name}`]);
  }
});
