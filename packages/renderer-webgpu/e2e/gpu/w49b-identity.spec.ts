/** Byte recorder run unchanged on the pre-operator tree and the assembled W49b tree. */
import { createHash } from "node:crypto";
import { readdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { expect, test } from "@playwright/test";
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, type MaterialProfilePatch } from "../../src/material";
import { SCENES, type Scene } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter } from "../support";

const profiles = resolve(import.meta.dirname, "../../../../packages/calibration/profiles");
const files = readdirSync(profiles).filter(p => /^apple-macos-.*-1x-(light|dark)-standard(?:-glass0\.(25|5)(?:-receded)?)?\.json$/.test(p));
const patch = (name: string): MaterialProfilePatch =>
  (JSON.parse(readFileSync(join(profiles, name), "utf8")) as { patch: MaterialProfilePatch }).patch;

test("@gpu W49b records ten shipped endpoints and every golden scene", async ({ page }) => {
  test.setTimeout(180_000);
  const out = process.env["W49B_IDENTITY_OUT"];
  test.skip(out === undefined, "Cross-tree identity recorder: provide W49B_IDENTITY_OUT");
  requireHardwareAdapter(await openHarness(page));
  const records: Record<string, string> = {};
  const record = async (name: string, scene: Scene | string, material: MaterialProfilePatch) => {
    const image = decodeCapture(await page.evaluate(([s, p]) => window.vitrea.renderScene(s, undefined, p),
      [scene, material] as const));
    records[name] = createHash("sha256").update(image.data).digest("hex");
  };
  expect(files).toHaveLength(10);
  for (const file of files) {
    const base = file.includes("-receded") ? withMaterialOverrides(DEFAULT_MATERIAL_PROFILE,
      patch(file.replace("-receded", ""))) : DEFAULT_MATERIAL_PROFILE;
    const material = withMaterialOverrides(base, patch(file));
    for (const dpr of [1, 1.5, 2]) {
      const scene: Scene = {
        name: "identity", widthCss: 320, heightCss: 200, devicePixelRatio: dpr,
        measureOnly: true, warmupFrames: 24,
        backdrop: { kind: "checkerboard", cell: 16 * dpr, size: 320 * dpr },
        backdropPlacement: { x: 0, y: 0, width: 320, height: 320 },
        groups: [{ groupId: "g", backdropSourceId: "bg", refraction: "true", analysisExact: true,
          surfaces: [{ nodeId: "s", family: "fixed-rounded-rect", reference: "figma-smoothing",
            shape: { center: [160, 100], size: [280, 160], radii: [24, 24, 24, 24],
              smoothing: 0, thickness: 10 } }] }],
      };
      await record(`${file}/${String(dpr)}x`, scene, material);
    }
  }
  for (const scene of SCENES.filter(s => s.measureOnly !== true)) {
    await record(`golden/${scene.name}`, scene.name, {});
  }
  writeFileSync(out!, JSON.stringify(records, null, 2) + "\n");
});
