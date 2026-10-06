/**
 * W47 G0 (a) — operator 1, `tintAlphaFar1x` / `tintAlphaFar2x`, the transmission graded on the
 * scatter's far curve, proved inert by bytes on a real adapter (charter clause 1, Decision Log 2,
 * X57, X65; claims §5.211).
 *
 * The leaves land at identity 0 and are evaluated per pixel in the optics pass, before the size
 * law's occlusion term and the W9 solve:
 *
 * ```
 * alphaBase  = clamp(tintAlpha + rampAtScale(far1x, far2x, dpr) · farS(span), 0, 1)
 * sizedAlpha = alphaBase + sizeOcclusionGain · sizeK · (1 − alphaBase)
 * ```
 *
 * with `farS` the far-curve smoothstep the pass already computes from each pixel's span. Unlike
 * W45's share this alpha is read on EVERY body pixel of every material, so the identity has to be
 * shown on every shipped endpoint, not only where a texture is live.
 *
 * Two tests.
 *
 * - **The recorder** renders every case below and, where `W47_PROOF_OUT` names a directory,
 *   writes each raster's SHA-256 (and its PNG) there. It asserts nothing about the operator, so it
 *   runs unchanged on the commit BEFORE the shader learned the uniform, when `withMaterialOverrides`
 *   ignores the two unknown keys: the identity cases recorded there and after must be
 *   byte-identical, which is the proof the inert leaves changed no raster.
 * - **The assertions** hold the identity and the grading on today's code: an explicit 0 on both
 *   leaves is the absent leaf on the dark 0.25 material at both scales; a 2x-only delta cannot
 *   reach a 1x pixel and a 1x-only delta cannot reach a 2x pixel (`rampAtScale` holds each anchor
 *   outside [1, 2]); and a non-zero delta moves the members above the knee and leaves the span-56
 *   and span-96 members' pixels exactly where they were, because `farS` is 0 at and below the knee —
 *   the grading is per pixel and not per group, in the toned scene (where the solve runs at each
 *   pixel's alpha against ONE group mean) as in the untoned one.
 */

import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

import { expect, test, type Page } from "@playwright/test";
import { PNG } from "pngjs";

import { SCENES } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

type Patch = Record<string, unknown>;

const PROFILES = fileURLToPath(new URL("../../../calibration/profiles/", import.meta.url));

/** A shipped document's `patch`, read from the committed document itself (the authority). */
const documentPatch = (key: string): Patch =>
  (JSON.parse(readFileSync(join(PROFILES, `${key}.json`), "utf8")) as { patch: Patch }).patch;

const isRecord = (value: unknown): value is Patch =>
  typeof value === "object" && value !== null && !Array.isArray(value);

/**
 * A receded difference OVER its active endpoint, merged leaf by leaf exactly as the runtime's
 * `mergeMaterialProfiles` (`platform-web/src/color-scheme.ts`) poses an inactive window: records
 * merge, arrays and numbers replace.
 */
const merge = (base: Patch, over: Patch): Patch => {
  const result: Patch = { ...base };
  for (const [key, value] of Object.entries(over)) {
    const held = result[key];
    result[key] = isRecord(held) && isRecord(value) ? merge(held, value) : value;
  }
  return result;
};

const ACTIVE = (key: string): Patch => documentPatch(key);
const RECEDED = (key: string): Patch => merge(documentPatch(key), documentPatch(`${key}-receded`));

const DARK025 = "apple-macos-27.0-1x-dark-standard-glass0.25";

/**
 * Every shipped endpoint the identity is shown on. The renderer default is the macOS 26.5 light
 * material; the 26.5 receded difference has no document (it lives in `receded-profile.ts`), so the
 * 26.5 material is shown at its two active endpoints.
 */
const ENDPOINTS: Readonly<Record<string, Patch>> = {
  "default": {},
  "macos26-dark": ACTIVE("apple-macos-26.5-1x-dark-standard"),
  "light05": ACTIVE("apple-macos-27.0-1x-light-standard-glass0.5"),
  "light05-receded": RECEDED("apple-macos-27.0-1x-light-standard-glass0.5"),
  "dark05": ACTIVE("apple-macos-27.0-1x-dark-standard-glass0.5"),
  "dark05-receded": RECEDED("apple-macos-27.0-1x-dark-standard-glass0.5"),
  "light025": ACTIVE("apple-macos-27.0-1x-light-standard-glass0.25"),
  "light025-receded": RECEDED("apple-macos-27.0-1x-light-standard-glass0.25"),
  "dark025": ACTIVE(DARK025),
  "dark025-receded": RECEDED(DARK025),
};

interface Case {
  readonly label: string;
  readonly scene: string;
  readonly patch: Patch;
}

const SCALES = [
  { tag: "2x", plain: "w47-span-quad", toned: "w47-span-quad-toned" },
  { tag: "1x", plain: "w47-span-quad-1x", toned: "w47-span-quad-toned-1x" },
] as const;

/** The dark 0.25 material's far deltas: off, explicit 0, 2x-only, 1x-only, and the clamp. */
const DARK_DELTAS: Readonly<Record<string, Patch>> = {
  "far0": { tintAlphaFar1x: 0, tintAlphaFar2x: 0 },
  "far2x+0.2": { tintAlphaFar2x: 0.2 },
  "far2x+0.45": { tintAlphaFar2x: 0.45 },
  "far2x+1": { tintAlphaFar2x: 1 },
  "far1x+0.3": { tintAlphaFar1x: 0.3 },
  "far1x+0.3/far2x+0.45": { tintAlphaFar1x: 0.3, tintAlphaFar2x: 0.45 },
};

const CASES: readonly Case[] = SCALES.flatMap(({ tag, plain, toned }) =>
  [["plain", plain], ["toned", toned]].flatMap(([form, scene]) => [
    ...Object.entries(ENDPOINTS).map(([name, patch]) => ({
      label: `${tag}/${form}/${name}`, scene: scene!, patch,
    })),
    ...Object.entries(DARK_DELTAS).map(([name, delta]) => ({
      label: `${tag}/${form}/dark025/${name}`, scene: scene!, patch: { ...ENDPOINTS["dark025"], ...delta },
    })),
    {
      label: `${tag}/${form}/dark025-receded/far2x+0.45`, scene: scene!,
      patch: { ...ENDPOINTS["dark025-receded"], tintAlphaFar2x: 0.45 },
    },
  ]),
);

const render = async (page: Page, scene: string, patch: Patch): Promise<Raster> =>
  decodeCapture(
    await page.evaluate(
      ([name, materialProfile]) =>
        window.vitrea.renderScene(name as string, undefined, materialProfile as Record<string, unknown>),
      [scene, patch] as const,
    ),
  );

const sha256 = (raster: Raster): string => createHash("sha256").update(raster.data).digest("hex");

/**
 * The four members' boxes in CSS px, x then y, each widened by 4 CSS px beyond the silhouette so
 * the anti-aliased edge (where the body is mixed with what is outside it by coverage) counts as the
 * member's. The gaps between the members are 17 CSS px or more after the widening.
 */
const MEMBERS = {
  span56: [[16, 114], [68, 132]],
  span96: [[131, 279], [48, 152]],
  span128: [[301, 459], [32, 168]],
  span160: [[486, 674], [16, 184]],
} as const;

type Box = readonly [readonly [number, number], readonly [number, number]];

/** The largest channel difference inside one member's box. */
const boxDelta = (a: Raster, b: Raster, dpr: number, [[x0, x1], [y0, y1]]: Box): number => {
  let worst = 0;
  for (let index = 0; index < a.data.length; index += 4) {
    const x = (index / 4) % a.width;
    const y = Math.floor(index / 4 / a.width);
    if (x < x0 * dpr || x >= x1 * dpr || y < y0 * dpr || y >= y1 * dpr) continue;
    for (let channel = 0; channel < 4; channel += 1) {
      worst = Math.max(worst, Math.abs((a.data[index + channel] ?? 0) - (b.data[index + channel] ?? 0)));
    }
  }
  return worst;
};

/** The largest channel difference anywhere outside the four members' boxes. */
const outsideDelta = (a: Raster, b: Raster, dpr: number): number => {
  let worst = 0;
  const boxes = Object.values(MEMBERS) as readonly Box[];
  for (let index = 0; index < a.data.length; index += 4) {
    const x = (index / 4) % a.width;
    const y = Math.floor(index / 4 / a.width);
    const inside = boxes.some(([[x0, x1], [y0, y1]]) =>
      x >= x0 * dpr && x < x1 * dpr && y >= y0 * dpr && y < y1 * dpr);
    if (inside) continue;
    for (let channel = 0; channel < 4; channel += 1) {
      worst = Math.max(worst, Math.abs((a.data[index + channel] ?? 0) - (b.data[index + channel] ?? 0)));
    }
  }
  return worst;
};

test.describe("@gpu W47 operator 1, tintAlphaFar1x/2x (charter clause 1; claims §5.211)", () => {
  test("records every case's bytes", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const out = process.env["W47_PROOF_OUT"];
    const record: Record<string, { readonly scene: string; readonly patch: Patch;
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

  test("is the identity at 0, held to its own scale, and per pixel above the knee", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));
    const bytes = new Map<string, Raster>();
    for (const { label, scene, patch } of CASES) bytes.set(label, await render(page, scene, patch));
    const hash = (label: string): string => sha256(bytes.get(label)!);

    for (const { tag } of SCALES) {
      const dpr = tag === "2x" ? 2 : 1;
      for (const form of ["plain", "toned"]) {
        const at = (name: string): string => `${tag}/${form}/dark025${name === "" ? "" : `/${name}`}`;
        // The dark material is not the default, so nothing below compares two default renders.
        expect(hash(at("")), at("")).not.toBe(hash(`${tag}/${form}/default`));

        // An explicit 0 on both leaves is the absent leaf: `tintAlpha + 0·farS` is `tintAlpha`.
        expect(hash(at("far0")), at("far0")).toBe(hash(at("")));

        // Each anchor is held outside [1, 2]: the other scale's delta reaches no pixel.
        const inert = dpr === 2 ? ["far1x+0.3"] : ["far2x+0.2", "far2x+0.45", "far2x+1"];
        for (const name of inert) expect(hash(at(name)), at(name)).toBe(hash(at("")));

        // ON: the delta reads where `farS` is above 0 and nowhere else. The span-56 and span-96
        // members sit at or below the knee, where the curve is exactly 0, so their boxes are
        // byte-identical at every delta; the 128 and 160 members move; and the gaps between the
        // members (the backdrop and the outer shadow, neither of which reads the alpha) do not.
        const live = dpr === 2
          ? ["far2x+0.2", "far2x+0.45", "far2x+1", "far1x+0.3/far2x+0.45"]
          : ["far1x+0.3", "far1x+0.3/far2x+0.45"];
        const base = bytes.get(at(""))!;
        for (const name of live) {
          const moved = bytes.get(at(name))!;
          expect(boxDelta(base, moved, dpr, MEMBERS.span56), `${at(name)}: span 56`).toBe(0);
          expect(boxDelta(base, moved, dpr, MEMBERS.span96), `${at(name)}: span 96`).toBe(0);
          expect(boxDelta(base, moved, dpr, MEMBERS.span128), `${at(name)}: span 128`).toBeGreaterThan(0);
          expect(boxDelta(base, moved, dpr, MEMBERS.span160), `${at(name)}: span 160`).toBeGreaterThan(0);
          expect(outsideDelta(base, moved, dpr), `${at(name)}: outside the members`).toBe(0);
        }

        // The receded endpoint inherits the active's leaves by merge and grades the same way.
        if (dpr === 2) {
          const receded = bytes.get(`${tag}/${form}/dark025-receded`)!;
          const graded = bytes.get(`${tag}/${form}/dark025-receded/far2x+0.45`)!;
          expect(boxDelta(receded, graded, dpr, MEMBERS.span96), `${tag}/${form} receded: span 96`).toBe(0);
          expect(boxDelta(receded, graded, dpr, MEMBERS.span160), `${tag}/${form} receded: span 160`)
            .toBeGreaterThan(0);
        } else {
          expect(hash(`${tag}/${form}/dark025-receded/far2x+0.45`))
            .toBe(hash(`${tag}/${form}/dark025-receded`));
        }
      }
    }
  });
});
