/**
 * W45 G0 — `sizeHeavySecondShareFar2x`, the second heavy tap's share graded on the scatter's far
 * curve, proved inert by bytes on a real adapter (charter clause 1, Decision Log 1, X57; claims
 * §5.205).
 *
 * The leaf lands at identity 0 and is evaluated per pixel in the optics pass as
 * `tapShare = sizeHeavySecondShare + farDeltaAtScale · farS`, UNCLAMPED, on the far-curve
 * smoothstep the pass already computes from each pixel's span. The goldens render the renderer
 * default, where the second texture does not exist, so they cannot see this expression at all:
 * the identity has to be shown where the second texture is LIVE, at a signed share, because the
 * existing share is signed by design (a negative share is an unsharp mask) and a clamp or a
 * rewritten mix would break a tuned configuration no shipped digest would catch.
 *
 * Two tests.
 *
 * - **The recorder** renders every case below and, where `W45_PROOF_OUT` names a directory,
 *   writes each raster's SHA-256 (and its PNG) there. It asserts nothing about the operator, so it
 *   runs unchanged on the commit BEFORE the shader learned the uniform: the signed-share cases
 *   recorded there and after must be byte-identical, which is the proof the mix did not move.
 *   (Before the leaf existed a patch naming it was ignored by `withMaterialOverrides`, so the
 *   same case list runs on both sides.)
 * - **The assertions** hold the identity and the grading on today's code: an explicit delta of 0
 *   is the absent leaf at both signed shares; at share 0 the delta is unread (no second texture);
 *   at dpr 1 the delta cannot reach a pixel (`rampAtScale(0, delta, 1)` is 0); and a non-zero
 *   delta at a live share moves the members above the knee and leaves the span-96 member's
 *   pixels exactly where they were, because `farS` is 0 there — the grading is per pixel and not
 *   per group.
 */

import { createHash } from "node:crypto";
import { mkdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

import { expect, test, type Page } from "@playwright/test";
import { PNG } from "pngjs";

import { SCENES } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

const SCENE_2X = "w45-span-triple";
const SCENE_1X = "w45-span-triple-1x";

/** A live second tap: 3 CSS px at both anchors, so the 1x twin carries one too. */
const LIVE = { sizeHeavySecondSigma: 3, sizeHeavySecondSigma2x: 3 } as const;
/** The charter's identity cases: the 2x width alone, the 1x width at its shipped 0. */
const CHARTER = { sizeHeavySecondSigma2x: 3 } as const;

interface Case {
  readonly label: string;
  readonly scene: string;
  readonly patch: Record<string, unknown>;
}

const FAR = "sizeHeavySecondShareFar2x";

/** Every case the recorder writes; the assertions read them back by label. */
const CASES: readonly Case[] = [
  { label: "2x/default", scene: SCENE_2X, patch: {} },
  // Clause 1's identity cases, on the charter's own patch: share −0.3 and +0.5 at σ2x 3.
  { label: "2x/share-0.3", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: -0.3 } },
  { label: "2x/share+0.5", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: 0.5 } },
  { label: "2x/share-0.3/far0", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: -0.3, [FAR]: 0 } },
  { label: "2x/share+0.5/far0", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: 0.5, [FAR]: 0 } },
  // The share-0 ladder: the delta unread where no second texture exists.
  { label: "2x/share0/far-1", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: 0, [FAR]: -1 } },
  { label: "2x/share0/far0", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: 0, [FAR]: 0 } },
  { label: "2x/share0/far+1", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: 0, [FAR]: 1 } },
  // The ON path at a live share: the delta reads on the members above the knee only.
  { label: "2x/share+0.5/far-0.5", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: 0.5, [FAR]: -0.5 } },
  { label: "2x/share+0.5/far-1", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: 0.5, [FAR]: -1 } },
  { label: "2x/share+0.5/far+1", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: 0.5, [FAR]: 1 } },
  { label: "2x/share-0.3/far-1", scene: SCENE_2X, patch: { ...CHARTER, sizeHeavySecondShare: -0.3, [FAR]: -1 } },
  // The 1x twin: the charter's patch (no 1x width, so no texture at 1x) and a LIVE 1x tap.
  { label: "1x/default", scene: SCENE_1X, patch: {} },
  { label: "1x/share+0.5", scene: SCENE_1X, patch: { ...CHARTER, sizeHeavySecondShare: 0.5 } },
  { label: "1x/share+0.5/far-1", scene: SCENE_1X, patch: { ...CHARTER, sizeHeavySecondShare: 0.5, [FAR]: -1 } },
  { label: "1x/share+0.5/far+1", scene: SCENE_1X, patch: { ...CHARTER, sizeHeavySecondShare: 0.5, [FAR]: 1 } },
  { label: "1x/live-0.3", scene: SCENE_1X, patch: { ...LIVE, sizeHeavySecondShare: -0.3 } },
  { label: "1x/live+0.5", scene: SCENE_1X, patch: { ...LIVE, sizeHeavySecondShare: 0.5 } },
  { label: "1x/live+0.5/far-1", scene: SCENE_1X, patch: { ...LIVE, sizeHeavySecondShare: 0.5, [FAR]: -1 } },
  { label: "1x/live+0.5/far0", scene: SCENE_1X, patch: { ...LIVE, sizeHeavySecondShare: 0.5, [FAR]: 0 } },
  { label: "1x/live+0.5/far+1", scene: SCENE_1X, patch: { ...LIVE, sizeHeavySecondShare: 0.5, [FAR]: 1 } },
  { label: "1x/live-0.3/far-1", scene: SCENE_1X, patch: { ...LIVE, sizeHeavySecondShare: -0.3, [FAR]: -1 } },
];

const render = async (page: Page, scene: string, patch: Record<string, unknown>): Promise<Raster> =>
  decodeCapture(
    await page.evaluate(
      ([name, materialProfile]) =>
        window.vitrea.renderScene(name as string, undefined, materialProfile as Record<string, unknown>),
      [scene, patch] as const,
    ),
  );

const sha256 = (raster: Raster): string => createHash("sha256").update(raster.data).digest("hex");

/** The three members' columns in CSS px, gaps excluded; the body pass writes nothing between. */
const COLUMNS = { span96: [20, 160], span128: [185, 335], span160: [360, 540] } as const;

/** The largest channel difference inside one member's column. */
const columnDelta = (a: Raster, b: Raster, dpr: number, [from, to]: readonly [number, number]): number => {
  let worst = 0;
  for (let index = 0; index < a.data.length; index += 4) {
    const x = (index / 4) % a.width;
    if (x < from * dpr || x >= to * dpr) continue;
    for (let channel = 0; channel < 4; channel += 1) {
      worst = Math.max(worst, Math.abs((a.data[index + channel] ?? 0) - (b.data[index + channel] ?? 0)));
    }
  }
  return worst;
};

test.describe("@gpu W45 sizeHeavySecondShareFar2x (charter clause 1; claims §5.205)", () => {
  test("records every case's bytes", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const out = process.env["W45_PROOF_OUT"];
    const record: Record<string, { readonly scene: string; readonly patch: Record<string, unknown>;
      readonly width: number; readonly height: number; readonly sha256: string }> = {};
    if (out !== undefined) mkdirSync(join(out, "png"), { recursive: true });
    for (const { label, scene, patch } of CASES) {
      const raster = await render(page, scene, patch);
      record[label] = { scene, patch, width: raster.width, height: raster.height, sha256: sha256(raster) };
      if (out !== undefined) {
        const png = new PNG({ width: raster.width, height: raster.height });
        png.data = Buffer.from(raster.data);
        writeFileSync(join(out, "png", `${label.replaceAll("/", "__")}.png`), PNG.sync.write(png));
      }
    }
    // The golden scenes at the renderer default, by their raw bytes: the golden suite compares
    // within a tolerance, and "byte-identical" is read here.
    for (const scene of SCENES.filter((candidate) => candidate.measureOnly !== true)) {
      const raster = await render(page, scene.name, {});
      record[`golden/${scene.name}`] = {
        scene: scene.name, patch: {}, width: raster.width, height: raster.height, sha256: sha256(raster),
      };
    }
    if (out !== undefined) writeFileSync(join(out, "cases.json"), `${JSON.stringify(record, null, 1)}\n`);
    expect(Object.keys(record).length).toBeGreaterThan(CASES.length);
  });

  test("is the identity at 0, unread at share 0 and at dpr 1, and per pixel above the knee", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const bytes = new Map<string, Raster>();
    for (const { label, scene, patch } of CASES) bytes.set(label, await render(page, scene, patch));
    const hash = (label: string): string => sha256(bytes.get(label)!);

    // The second tap is live at both signed shares, so none of what follows compares two
    // renders of the off path.
    expect(hash("2x/share-0.3")).not.toBe(hash("2x/default"));
    expect(hash("2x/share+0.5")).not.toBe(hash("2x/default"));
    expect(hash("1x/live+0.5")).not.toBe(hash("1x/default"));

    // An explicit 0 is the absent leaf, at both signed shares: `share + 0·farS` is `share`.
    expect(hash("2x/share-0.3/far0")).toBe(hash("2x/share-0.3"));
    expect(hash("2x/share+0.5/far0")).toBe(hash("2x/share+0.5"));

    // At share 0 no second texture exists and the delta is unread, at either sign.
    for (const label of ["2x/share0/far-1", "2x/share0/far0", "2x/share0/far+1"]) {
      expect(hash(label), label).toBe(hash("2x/default"));
    }

    // At dpr 1 the delta resolves to 0 whatever it holds, with the 1x tap live and with it off.
    for (const label of ["1x/live+0.5/far-1", "1x/live+0.5/far0", "1x/live+0.5/far+1"]) {
      expect(hash(label), label).toBe(hash("1x/live+0.5"));
    }
    expect(hash("1x/live-0.3/far-1")).toBe(hash("1x/live-0.3"));
    for (const label of ["1x/share+0.5", "1x/share+0.5/far-1", "1x/share+0.5/far+1"]) {
      expect(hash(label), label).toBe(hash("1x/default"));
    }

    // ON: the delta reads where `farS` is above 0 and nowhere else. The span-96 member sits at the
    // knee, where the curve is exactly 0, so its column is byte-identical at every delta; the 128
    // and 160 members move.
    const base = bytes.get("2x/share+0.5")!;
    for (const label of ["2x/share+0.5/far-0.5", "2x/share+0.5/far-1", "2x/share+0.5/far+1"]) {
      const moved = bytes.get(label)!;
      expect(columnDelta(base, moved, 2, COLUMNS.span96), `${label}: span 96`).toBe(0);
      expect(columnDelta(base, moved, 2, COLUMNS.span128), `${label}: span 128`).toBeGreaterThan(0);
      expect(columnDelta(base, moved, 2, COLUMNS.span160), `${label}: span 160`).toBeGreaterThan(0);
    }
    // And the sign of the share is carried through: a negative share graded by a negative delta
    // is a different render from the ungraded one.
    expect(hash("2x/share-0.3/far-1")).not.toBe(hash("2x/share-0.3"));
  });
});
