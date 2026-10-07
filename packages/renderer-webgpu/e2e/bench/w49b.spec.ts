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
// All W/S/current/control rows share this scene: seven thin controls and a broad
// span-160 morph (64% of summed rectangle area on mobile, 86% on desktop). W's
// extra texture is sampled at the far endpoint, not merely built and never read.
const configs = [
  { label: "mobile", widthCss: 390, heightCss: 844, devicePixelRatio: 3 },
  { label: "desktop", widthCss: 1440, heightCss: 900, devicePixelRatio: 2 },
].map(view => ({ ...view, morphSpanCss: 160, morphPress: 0, backdropSize: 2048 }))
  .flatMap(view => [
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
  const rounds = 60;
  const warmup = 20;
  const measurement = await page.evaluate(input => window.vitrea.bench(input),
    { configs, rounds, warmup });
  const out = process.env["W49B_BENCH_OUT"];
  if (out !== undefined) writeFileSync(out, JSON.stringify({ adapter, measurement }, null, 2) + "\n");
  for (const row of measurement.results) {
    expect(row.wallMsPerFrame).toBeGreaterThan(0);
    expect(row.pyramidRebuilds, `${row.label} live source rebuilds`).toBe(rounds + warmup);
    expect(row.scene.backdrop).toEqual({ kind: "checkerboard", cell: 12, size: 2048, live: true });
    const spans = row.scene.groups.flatMap(g => g.surfaces.map(s => Math.min(...s.shape.size)));
    expect(spans).toEqual([44, 44, 44, 44, 40, 40, 40, 160]);
    const morph = row.scene.groups.find(g => g.groupId === "morph")!;
    expect(morph.surfaces[0]?.channels?.press, `${row.label} uncompressed thick span`).toBe(0);
    test.info().annotations.push({ type: "bench", description: JSON.stringify(row) });
  }
  for (const view of ["mobile", "desktop"]) {
    const current = measurement.results.find(r => r.label === `${view}/current`)!;
    for (const row of measurement.results.filter(r => r.label.startsWith(`${view}/`))) {
      expect(row.scene, `${row.label} comparison geometry`).toEqual(current.scene);
    }
    const baseline = current.gpuMsPerFrame;
    const control = measurement.results.find(r => r.label === `${view}/control`)?.gpuMsPerFrame;
    if (baseline !== undefined && control !== undefined) {
      expect(Math.abs(Math.log2(control / baseline)), `${view} ordering drift`).toBeLessThan(Math.log2(1.25));
    }
  }
});
