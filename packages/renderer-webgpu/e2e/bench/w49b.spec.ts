/** W49b DL2: price uniform capture resolution and the extra bandwidth pair on live sources. */
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { expect, test } from "@playwright/test";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, type MaterialProfilePatch } from "../../src/material";
import { openHarness, requireHardwareAdapter } from "../support";

const cal = resolve(import.meta.dirname, "../../../..", "packages/calibration");
const patch = (pose: string): MaterialProfilePatch => (JSON.parse(readFileSync(resolve(cal, "profiles",
  `apple-macos-27.0-1x-dark-standard-glass0.25${pose}.json`), "utf8")) as
  { patch: MaterialProfilePatch }).patch;
const active = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch(""));
const receded = withMaterialOverrides(active, patch("-receded"));
const configs = [
  { label: "mobile", widthCss: 390, heightCss: 844, devicePixelRatio: 3 },
  { label: "desktop", widthCss: 1440, heightCss: 900, devicePixelRatio: 2 },
].flatMap(view => [
  { ...view, label: `${view.label}/current`, materialProfile: receded },
  { ...view, label: `${view.label}/S-0.5`, materialProfile: { ...receded, backdropCaptureScale: 0.5 } },
  { ...view, label: `${view.label}/S-0.25`, materialProfile: { ...receded, backdropCaptureScale: 0.25 } },
  { ...view, label: `${view.label}/W-delta4`, materialProfile: { ...receded,
    sizeHeavySecondSigmaFar1x: 4, sizeHeavySecondSigmaFar2x: 4 } },
  { ...view, label: `${view.label}/control`, materialProfile: receded },
]);

test("@bench W49b live backdrop capture and bandwidth", async ({ page }) => {
  test.setTimeout(300_000);
  const adapter = await openHarness(page);
  requireHardwareAdapter(adapter);
  const measurement = await page.evaluate(c => window.vitrea.bench({ configs: c, rounds: 60, warmup: 20 }),
    configs);
  const out = process.env["W49B_BENCH_OUT"];
  if (out !== undefined) writeFileSync(out, JSON.stringify({ adapter, measurement }, null, 2) + "\n");
  for (const row of measurement.results) {
    expect(row.wallMsPerFrame).toBeGreaterThan(0);
    test.info().annotations.push({ type: "bench", description: JSON.stringify(row) });
  }
  for (const view of ["mobile", "desktop"]) {
    const baseline = measurement.results.find(r => r.label === `${view}/current`)?.gpuMsPerFrame;
    const control = measurement.results.find(r => r.label === `${view}/control`)?.gpuMsPerFrame;
    if (baseline !== undefined && control !== undefined) {
      expect(Math.abs(Math.log2(control / baseline)), `${view} ordering drift`).toBeLessThan(Math.log2(1.25));
    }
  }
});
