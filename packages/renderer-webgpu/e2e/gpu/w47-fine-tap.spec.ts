/**
 * W47 G0 (b), Decision Log 3 and X66: the BODY fine tap's identity and live path.
 *
 * Committed before the operator exists. The recorder makes no assertion that a new leaf draws:
 * old `withMaterialOverrides` ignores the three names, so precisely this case list runs before
 * and after the landing. Identity cases must match across those trees; live cases must differ
 * after it. The assertions below are for the implemented tree, separately from the recorder.
 *
 * The diagnostic chose body (minimum R 0.7393, pooled 0.8908); this proof is not another fit.
 * An eight-CSS-pixel checker under one span-96 surface carries the fine structure the tap removes,
 * with an explicit source placement so the source's density is the declared DPR, not a cover fit.
 * The dark receded 0.25 material is X62's snapshot pair. Every 0.5 endpoint and both light 0.25
 * endpoints are read too, at identity, without moving their documents. No native fixture is read.
 *
 * W47_FINE_PROOF_OUT records raw raster hashes and PNGs. Run the recorder on the merged tree
 * immediately before op2 and after it, under W47's with-gpu.sh. Recording is deliberately deferred
 * until review and assembly; this spec never regenerates a renderer golden.
 */
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { expect, test, type Page } from "@playwright/test";
import { PNG } from "pngjs";

import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides, type MaterialProfilePatch } from "../../src/material";
import { SCENES, type Scene } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

const ROOT = resolve(import.meta.dirname, "../../../..");
const CAL = join(ROOT, "packages/calibration");
const SNAPSHOTS = join(CAL, "results/2026-10-06-w47-g0-operators/documents");
const PAIRS = {
  "025/light": [join(SNAPSHOTS, "ebc3d9105a4a.json"), join(SNAPSHOTS, "12712d534b78.json")],
  "025/dark": [join(SNAPSHOTS, "d0219cd684bf.json"), join(SNAPSHOTS, "f0b36a71772a.json")],
  "05/light": ["", ""], "05/dark": ["", ""],
};
for (const scheme of ["light", "dark"] as const) {
  PAIRS[`05/${scheme}`] = ["", "-receded"].map(pose => join(CAL, "profiles",
    `apple-macos-27.0-1x-${scheme}-standard-glass0.5${pose}.json`));
}
const patchOf = (file: string): MaterialProfilePatch =>
  (JSON.parse(readFileSync(file, "utf8")) as { patch: MaterialProfilePatch }).patch;
const endpoints: Record<string, MaterialProfilePatch> = {};
for (const [name, [active, receded]] of Object.entries(PAIRS)) {
  const base = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(active!));
  endpoints[`${name}/active`] = base;
  endpoints[`${name}/receded`] = withMaterialOverrides(base, patchOf(receded!));
}

const sceneAt = (dpr: number): Scene => ({
  name: `w47-fine-${String(dpr)}x`, widthCss: 320, heightCss: 200, devicePixelRatio: dpr,
  measureOnly: true, warmupFrames: 24,
  backdrop: { kind: "checkerboard", cell: 8 * dpr, size: 320 * dpr },
  backdropPlacement: { x: 0, y: 0, width: 320, height: 320 },
  groups: [{ groupId: "g", backdropSourceId: "bg", refraction: "true", analysisExact: true,
    surfaces: [{ nodeId: "s", family: "fixed-rounded-rect", reference: "figma-smoothing",
      shape: { center: [160, 100], size: [160, 96], radii: [20, 20, 20, 20],
        smoothing: 0, thickness: 10 } }] }],
});
interface Case {
  readonly label: string;
  readonly scene: Scene;
  readonly patch: MaterialProfilePatch & Record<string, unknown>;
  readonly identity: boolean;
}
const CASES: Case[] = [];
for (const dpr of [1, 2]) {
  for (const [endpoint, base] of Object.entries(endpoints)) {
    const label = `${String(dpr)}x/${endpoint}`;
    CASES.push({ label, scene: sceneAt(dpr), patch: { ...base }, identity: true });
    for (const width of [1.5, 6]) {
      CASES.push({ label: `${label}/zero-${String(width)}`, scene: sceneAt(dpr), identity: true,
        patch: { ...base, sizeFineTapShare: 0, sizeFineTapSigma: width, sizeFineTapSigma2x: width } });
    }
  }
  for (const share of [0.5, 1]) {
    for (const width of [2, 6]) {
      CASES.push({ label: `${String(dpr)}x/live-${String(share)}-${String(width)}`,
        scene: sceneAt(dpr), identity: false,
        patch: { ...endpoints["025/dark/receded"], sizeFineTapShare: share,
          sizeFineTapSigma: width, sizeFineTapSigma2x: width } });
    }
  }
}
const sha = (r: Raster): string => createHash("sha256").update(r.data).digest("hex");
const render = async (page: Page, scene: string | Scene, patch: MaterialProfilePatch): Promise<Raster> =>
  decodeCapture(await page.evaluate(([name, material]) => window.vitrea.renderScene(name, undefined, material),
    [scene, patch] as const));

test.describe("@gpu W47 fine body tap (G0 (b), Decision Log 3, X66)", () => {
  test.setTimeout(180_000);
  test("records every case's bytes", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const out = process.env["W47_FINE_PROOF_OUT"];
    const records: Record<string, unknown> = {};
    if (out !== undefined) mkdirSync(join(out, "png"), { recursive: true });
    for (const item of CASES) {
      const raster = await render(page, item.scene, item.patch);
      records[item.label] = { ...item, width: raster.width, height: raster.height, sha256: sha(raster) };
      if (out !== undefined) {
        const png = new PNG({ width: raster.width, height: raster.height });
        png.data = Buffer.from(raster.data);
        writeFileSync(join(out, "png", `${item.label.replaceAll("/", "__")}.png`), PNG.sync.write(png));
      }
    }
    for (const scene of SCENES.filter(s => s.measureOnly !== true)) {
      const raster = await render(page, scene.name, {});
      records[`golden/${scene.name}`] = { identity: true, width: raster.width,
        height: raster.height, sha256: sha(raster) };
    }
    if (out !== undefined) writeFileSync(join(out, "cases.json"), `${JSON.stringify(records, null, 1)}\n`);
    expect(Object.keys(records).length).toBeGreaterThan(CASES.length);
  });

  test("keeps every endpoint at identity and draws each live width and share", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const hashes = new Map<string, string>();
    for (const item of CASES) hashes.set(item.label, sha(await render(page, item.scene, item.patch)));
    for (const dpr of [1, 2]) {
      for (const endpoint of Object.keys(endpoints)) {
        const label = `${String(dpr)}x/${endpoint}`;
        for (const width of [1.5, 6]) {
          expect(hashes.get(`${label}/zero-${String(width)}`)).toBe(hashes.get(label));
        }
      }
      for (const share of [0.5, 1]) {
        for (const width of [2, 6]) {
          expect(hashes.get(`${String(dpr)}x/live-${String(share)}-${String(width)}`))
            .not.toBe(hashes.get(`${String(dpr)}x/025/dark/receded`));
        }
        expect(hashes.get(`${String(dpr)}x/live-${String(share)}-2`))
          .not.toBe(hashes.get(`${String(dpr)}x/live-${String(share)}-6`));
      }
      for (const width of [2, 6]) {
        expect(hashes.get(`${String(dpr)}x/live-0.5-${String(width)}`))
          .not.toBe(hashes.get(`${String(dpr)}x/live-1-${String(width)}`));
      }
    }
  });
});
