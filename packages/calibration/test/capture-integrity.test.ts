import { mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
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

  it("reads a bare patch, a CSS-only document, and refuses one that would change nothing", () => {
    expect(readMaterialProfileFile(write({ tintChromaScale: 0 })).cssTierMapping).toBeUndefined();
    expect(readMaterialProfileFile(write({ cssTierMapping: { saturation: 1.4 } })).patch).toEqual({});
    expect(() => readMaterialProfileFile(write({ patch: {} }))).toThrow(/is empty/);
  });
});
