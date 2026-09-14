import { spawnSync } from "node:child_process";
import { chmodSync, mkdirSync, mkdtempSync, readFileSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, resolve } from "node:path";
import { describe, expect, it } from "vitest";
import { captureIntegrityRefusal } from "../src/capture-integrity";
import {
  MATERIAL_PATCH_KEYS,
  readMaterialProfileFile,
} from "../scripts/material-profile-file";

/**
 * The declared cell: the matrix's canvas and the scale the fixture was captured
 * at. Everything a capture may be measured against comes from here.
 */
const declared = { canvas: { width: 320, height: 200 }, scale: 1 };

/** A page that reported exactly what was declared. */
const clean = {
  canvas: { width: 320, height: 200 },
  requestedScale: 1,
  devicePixelRatio: 1,
  problems: [] as readonly string[],
};

describe("a capture's integrity before it may be measured", () => {
  it("passes a page that reported the declared framing and no problems", () => {
    expect(captureIntegrityRefusal(clean, declared)).toBeUndefined();
    expect(captureIntegrityRefusal(
      { ...clean, requestedScale: 2, devicePixelRatio: 2 },
      { ...declared, scale: 2 },
    )).toBeUndefined();
  });

  it("refuses the viewport mismatch the page reports as a problem", () => {
    // W27c G1's invalidation: an 800x200 window around the 320x200 scene. The
    // stage still screenshots at the declared size, so the PNG is the right
    // shape and every number off it is measured against a raster the renderer
    // cover-fitted to the wrong frame.
    const problem =
      "The viewport is 800×600 CSS px but the scene canvas is 320×200. The renderer " +
      "cover-fits the backdrop texture to the viewport, so the glass would sample a " +
      "differently-framed raster than the page shows.";
    const refusal = captureIntegrityRefusal({ ...clean, problems: [problem] }, declared);
    expect(refusal).toMatch(/may not be measured/);
    expect(refusal).toContain(problem);
  });

  it("refuses a canvas, a requested scale or a devicePixelRatio the cell did not declare", () => {
    expect(captureIntegrityRefusal({ ...clean, canvas: { width: 800, height: 600 } }, declared))
      .toMatch(/scene canvas is 800x600 where the matrix declares 320x200/);
    expect(captureIntegrityRefusal({ ...clean, requestedScale: 2 }, declared))
      .toMatch(/asked for scale 2 where the cell is 1/);
    // The one the page cannot always catch itself: a context whose
    // deviceScaleFactor disagrees with the fixture's scale produces a capture of
    // the wrong pixel size, which is diffed against the native fixture anyway.
    expect(captureIntegrityRefusal({ ...clean, devicePixelRatio: 2 }, declared))
      .toMatch(/devicePixelRatio is 2 where the cell is 1/);
    // A scale that failed to parse is not silently equal to anything.
    expect(captureIntegrityRefusal({ ...clean, requestedScale: Number.NaN }, declared))
      .toMatch(/asked for scale NaN/);
  });

  it("names every disagreement at once, so a run is corrected once", () => {
    const refusal = captureIntegrityRefusal(
      { canvas: { width: 800, height: 600 }, requestedScale: 2, devicePixelRatio: 3,
        problems: ["the committed raster is 640×400"] },
      declared,
    );
    expect(refusal).toMatch(/scene canvas/);
    expect(refusal).toMatch(/asked for scale/);
    expect(refusal).toMatch(/devicePixelRatio/);
    expect(refusal).toMatch(/committed raster/);
  });

  it("refuses a ready page that reported nothing, rather than reading it as clean", () => {
    expect(captureIntegrityRefusal(undefined, declared)).toMatch(/reported nothing/);
  });
});

describe("the material profile document's key admission", () => {
  const write = (document: unknown): string => {
    const path = join(mkdtempSync(join(tmpdir(), "vitrea-profile-")), "profile.json");
    writeFileSync(path, `${JSON.stringify(document, undefined, 2)}\n`);
    return path;
  };

  it("admits the inactive endpoint's two tint terms (W27c, claims §5.130)", () => {
    // The frozen receded endpoint sets both. While they were missing from the
    // set, the canonical capture path refused the very document it exists to
    // measure — so a fitting run had to go around it, which is how a driver with
    // no integrity check came to produce the evidence.
    for (const key of ["tintChromaScale", "tintShadeCollapseRetention"]) {
      expect(MATERIAL_PATCH_KEYS.has(key)).toBe(true);
    }
    const path = write({
      patch: { tintChromaScale: 0, tintShadeCollapseRetention: 1, tintShadeStrength: 1,
        rimCollapsed: 0, outerShadow: { liftAmplitude: 0 } },
    });
    expect(readMaterialProfileFile(path).patch).toMatchObject({
      tintChromaScale: 0,
      tintShadeCollapseRetention: 1,
    });
  });

  it("admits the per-policy occlusion lift (W27c G1d, Decision Log 19)", () => {
    // The same gap one wave later, and on the one key G1d's whole sweep varied:
    // the receded endpoint's lift is a level PER accessibility policy now, and
    // the shared scalar beside it no longer says what either policy does. A
    // document naming it was refused by the path that exists to measure it.
    expect(MATERIAL_PATCH_KEYS.has("increasedOcclusionLiftByPolicy")).toBe(true);
    const path = write({
      patch: {
        increasedOcclusionLift: 0.96,
        increasedOcclusionLiftByPolicy: { reduceTransparency: 0.92, increaseContrast: 0.96 },
      },
    });
    expect(readMaterialProfileFile(path).patch).toMatchObject({
      increasedOcclusionLiftByPolicy: { reduceTransparency: 0.92, increaseContrast: 0.96 },
    });
  });

  it("still refuses a key the renderer does not have, naming it", () => {
    const path = write({ patch: { tintChromaScale: 0, tintChroma: 0.4 } });
    expect(() => readMaterialProfileFile(path)).toThrow(/does not have: tintChroma\b/);
    // The trap the guard was built for: a document handed in one level too deep,
    // whose every key is unrecognised and whose application would be a silent
    // no-op measuring the renderer's defaults.
    const nested = write({ patch: { patch: { tintChromaScale: 0 } } });
    expect(() => readMaterialProfileFile(nested)).toThrow(/silently measured the defaults/);
    // The nested guard, and the CSS tier's half of the same document.
    const retired = write({ patch: { outerShadow: { occlusion: 0.3 } } });
    expect(() => readMaterialProfileFile(retired)).toThrow(/MaterialOuterShadow does not have/);
    const mapping = write({ cssTierMapping: { shadowAlpha: 0.2 } });
    expect(() => readMaterialProfileFile(mapping)).toThrow(/CssTierMapping does not have/);
  });

  it("refuses a policy the per-policy lift does not have, naming it", () => {
    // The nested half of the key just admitted. The block has exactly two leaves
    // and the renderer spreads it over the defaults, so a document naming a third
    // — or spelling one of the two the way the media query does — applies
    // cleanly, hashes itself into every cell as the configuration that ran, and
    // lifts by the shared scalar instead. That is the silently-measured-the-
    // defaults failure one level deeper, which is what `outerShadow`'s leaf guard
    // beside it exists for.
    const typo = write({
      patch: { increasedOcclusionLiftByPolicy: { reduceTransparency: 0.92, contrast: 1 } },
    });
    expect(() => readMaterialProfileFile(typo))
      .toThrow(/MaterialOcclusionLiftByPolicy does not have: contrast\b/);
    const media = write({
      patch: { increasedOcclusionLiftByPolicy: { "prefers-contrast": 1 } },
    });
    expect(() => readMaterialProfileFile(media)).toThrow(/does not have: prefers-contrast\b/);
    // Either leaf alone is a valid document: the renderer merges the block over
    // the base, so a sweep may name one policy and leave the other where it was.
    for (const policy of ["reduceTransparency", "increaseContrast"]) {
      expect(readMaterialProfileFile(write({
        patch: { increasedOcclusionLiftByPolicy: { [policy]: 0.92 } },
      })).patch).toMatchObject({ increasedOcclusionLiftByPolicy: { [policy]: 0.92 } });
    }
  });

  it("refuses a per-policy lift that is not a map of policies to numbers", () => {
    /*
     * The leaf guard above only looks at a value it could read keys off, so
     * everything that is not a record walked straight past it. The renderer
     * SPREADS this block over the defaults, so each of these applies cleanly and
     * measures something nobody asked for: an array spreads as the numeric keys
     * `0` and `1` — neither of which is a policy — and a scalar or a null spreads
     * to nothing at all, leaving both policies on the shared default while the
     * cell records the document as the configuration that ran. An empty map is
     * the same no-op one level up. And a leaf that is not a finite number reaches
     * the lift arithmetic, where a string multiplies to NaN and a NaN alpha is a
     * surface that does not draw.
     */
    const lift = (value: unknown): string =>
      write({ patch: { increasedOcclusionLiftByPolicy: value } });
    for (const notAMap of [[0.92, 0.96], 0.92, "0.92", null, true]) {
      expect(() => readMaterialProfileFile(lift(notAMap)), JSON.stringify(notAMap) ?? "undefined")
        .toThrow(/increasedOcclusionLiftByPolicy/);
    }
    expect(() => readMaterialProfileFile(lift({}))).toThrow(/names no policy/);
    for (const bad of ["0.92", null, true, {}, []]) {
      expect(() => readMaterialProfileFile(lift({ reduceTransparency: bad })),
        JSON.stringify(bad)).toThrow(/reduceTransparency/);
    }
    /*
     * A number that is not finite is the same defect wearing the right type, and
     * it reaches here as literal JSON rather than through `JSON.stringify` — the
     * encoder writes `NaN` and `Infinity` out as `null`, so the only way one can
     * arrive in a committed document is an overflowing literal, which
     * `JSON.parse` turns into `Infinity` with no error of its own.
     */
    const overflow = join(mkdtempSync(join(tmpdir(), "vitrea-profile-")), "profile.json");
    writeFileSync(overflow,
      `{ "patch": { "increasedOcclusionLiftByPolicy": { "increaseContrast": 1e999 } } }\n`);
    expect(JSON.parse(readFileSync(overflow, "utf8")).patch.increasedOcclusionLiftByPolicy
      .increaseContrast).toBe(Number.POSITIVE_INFINITY);
    expect(() => readMaterialProfileFile(overflow)).toThrow(/increaseContrast/);
    // And the shape the sweep actually writes still reads.
    expect(readMaterialProfileFile(lift({ reduceTransparency: 0.92, increaseContrast: 0.96 })).patch)
      .toMatchObject({ increasedOcclusionLiftByPolicy: { reduceTransparency: 0.92 } });
  });

  it("reads a bare patch, a CSS-only document, and refuses one that would change nothing", () => {
    expect(readMaterialProfileFile(write({ tintChromaScale: 0 })).cssTierMapping).toBeUndefined();
    expect(readMaterialProfileFile(write({ cssTierMapping: { saturation: 1.4 } })).patch).toEqual({});
    expect(() => readMaterialProfileFile(write({ patch: {} }))).toThrow(/is empty/);
  });
});

describe("the G1c capture driver's accessibility preflight", () => {
  it("treats a missing key as off but fails closed when defaults itself fails", () => {
    const temporary = mkdtempSync(join(tmpdir(), "vitrea-g1c-preflight-"));
    const bin = join(temporary, "bin");
    mkdirSync(bin);
    const defaults = join(bin, "defaults");
    writeFileSync(
      defaults,
      `#!/bin/sh
if [ "$3" = "reduceTransparency" ]; then
  echo "The domain/default pair of (com.apple.universalaccess, reduceTransparency) does not exist" >&2
  exit 1
fi
echo "defaults second-read failure sentinel" >&2
exit 2
`,
    );
    chmodSync(defaults, 0o755);

    const repo = resolve(import.meta.dirname, "../../..");
    const driver = resolve(
      import.meta.dirname,
      "../results/2026-09-13-w27c-g1c-fit/g1c-run.ts",
    );
    const patch = join(temporary, "patch.json");
    writeFileSync(patch, "patch-read-after-preflight");

    const result = spawnSync(
      "pnpm",
      [
        "--filter", "@vitrea/calibration", "--fail-if-no-match", "exec", "tsx", driver,
        "--out", join(temporary, "out"), "--patch", patch,
      ],
      {
        cwd: repo,
        encoding: "utf8",
        env: { ...process.env, PATH: `${bin}:${process.env.PATH ?? ""}` },
        timeout: 30_000,
      },
    );
    const output = `${result.stdout ?? ""}${result.stderr ?? ""}`;
    expect(result.status).not.toBe(0);
    expect(output).toContain("defaults second-read failure sentinel");
    expect(output).not.toContain("patch-read-after-preflight");
  }, 30_000);
});
