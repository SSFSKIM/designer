import { describe, expect, it } from "vitest";

import {
  componentRegion,
  declaredShapeArea,
  placeComponent,
  type DeclaredComponent,
} from "../src/component-region";
import { CalibrationError } from "../src/errors";
import type { CalibrationImage } from "../src/image";
import { extractSilhouette, silhouetteArea, type Silhouette } from "../src/silhouette";
import { fromLinearLuminance, solidLuminance } from "./synthesise";

const CANVAS = { width: 320, height: 200 } as const;

/** The canonical control, as `scenes.json` declares it. */
const CAPSULE: DeclaredComponent = { kind: "capsule", size: [120, 44] };

/** The one placed shape of a single-shape component. */
function onlyShape(component: DeclaredComponent): ReturnType<typeof placeComponent>[number] {
  const placed = placeComponent(component, CANVAS)[0];
  if (placed === undefined) throw new Error("placeComponent returned nothing");
  return placed;
}

describe("declared component placement", () => {
  it("centres a lone shape and derives a capsule's radius from its short side", () => {
    // ZStack's default alignment, and the value the web side lays out at.
    expect(onlyShape(CAPSULE)).toEqual({
      kind: "capsule",
      left: 100,
      top: 78,
      width: 120,
      height: 44,
      radius: 22,
    });
  });

  it("lays a group out left to right at its declared spacing", () => {
    const group: DeclaredComponent = {
      kind: "group",
      spacing: 12,
      items: [
        { kind: "capsule", size: [44, 44] },
        { kind: "capsule", size: [44, 44] },
        { kind: "capsule", size: [44, 44] },
      ],
    };
    // Three 44 pt capsules and two 12 pt gaps span 156 pt, so the row starts at
    // (320 − 156) / 2 and each sibling follows 56 pt after the last.
    expect(placeComponent(group, CANVAS).map((shape) => shape.left)).toEqual([82, 138, 194]);
  });

  it("places a stack's base before its overlay, honouring the overlay's offset", () => {
    const stack: DeclaredComponent = {
      kind: "stack",
      base: { kind: "rrect", size: [220, 130], radius: 24 },
      over: { kind: "rrect", size: [120, 56], radius: 16, offset: [0, -8] },
    };
    const [base, over] = placeComponent(stack, CANVAS);
    expect(base?.top).toBe(35);
    expect(over?.top).toBe(64);
  });

  it("refuses a shape kind it has no geometry for, rather than approximating one", () => {
    let caught: unknown;
    try {
      placeComponent({ kind: "hexagon", size: [40, 40] } as DeclaredComponent, CANVAS);
    } catch (error) {
      caught = error;
    }
    expect(caught).toBeInstanceOf(CalibrationError);
  });
});

describe("the declared search region", () => {
  it("rasterises to the analytic area of the declaration, at both backing scales", () => {
    for (const scale of [1, 2]) {
      const region = componentRegion(CAPSULE, {
        canvas: CANVAS,
        scale,
        width: CANVAS.width * scale,
        height: CANVAS.height * scale,
      });
      const analytic = declaredShapeArea(onlyShape(CAPSULE), scale);
      // Within a boundary pixel per unit of perimeter: the raster is the floor.
      expect(Math.abs(region.areaPx - analytic) / analytic).toBeLessThan(0.005);
      expect(region.centreX).toBe(160 * scale);
      expect(region.centreY).toBe(100 * scale);
    }
  });

  it("refuses a capture that was not framed as the declared canvas", () => {
    let caught: unknown;
    try {
      componentRegion(CAPSULE, { canvas: CANVAS, scale: 1, width: 320, height: 240 });
    } catch (error) {
      caught = error;
    }
    expect((caught as CalibrationError).code).toBe("dimension-mismatch");
  });

  it("measures signed distance from the declared contour, negative inside", () => {
    const region = componentRegion(CAPSULE, {
      canvas: CANVAS,
      scale: 1,
      width: CANVAS.width,
      height: CANVAS.height,
    });
    const at = (x: number, y: number): number => region.signedDistancePx[y * CANVAS.width + x] ?? 0;
    // The capsule spans x 100..220, y 78..122; pixel centres are at +0.5.
    expect(at(160, 77)).toBeCloseTo(0.5, 6);
    expect(at(160, 74)).toBeCloseTo(3.5, 6);
    expect(at(160, 100)).toBeCloseTo(-21.5, 6);
  });
});

/**
 * The bounding pin.
 *
 * A halo outside the declared region is exactly the shape the active-pose
 * reference's outer shadow has, and the schema-4 rule — anything differing from
 * the background is the surface — swallowed it whole (claims §5.11). These two
 * cases differ only in *where* the departure sits, so what they pin is the
 * bound, not the threshold.
 */
describe("extraction bounded to the declared region", () => {
  const scale = 1;
  const region = componentRegion(CAPSULE, {
    canvas: CANVAS,
    scale,
    width: CANVAS.width,
    height: CANVAS.height,
  });
  const background = solidLuminance(CANVAS.width, CANVAS.height, 0.8);
  const inside = (x: number, y: number): boolean =>
    (region.silhouette.mask[y * CANVAS.width + x] ?? 0) !== 0;
  const distance = (x: number, y: number): number => region.signedDistancePx[y * CANVAS.width + x] ?? 0;

  const extract = (image: CalibrationImage, bound?: Silhouette): number =>
    silhouetteArea(
      extractSilhouette(image, {
        kind: "luminance-delta",
        background,
        threshold: 0.02,
        ...(bound === undefined ? {} : { region: bound }),
      }),
    );

  it("keeps a shadow-like halo outside the declaration out of the silhouette", () => {
    // A body inside the declaration, plus a multiplicative halo reaching 20 px
    // past its contour — the reference's shadow, in miniature.
    const withHalo = fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) => {
      if (inside(x, y)) return 0.5;
      const d = distance(x, y);
      return d <= 20 ? 0.8 * (1 - 0.25 * (1 - d / 20)) : 0.8;
    });

    const unbounded = extract(withHalo);
    const bounded = extract(withHalo, region.silhouette);

    // Unbounded, the halo roughly doubles the recovered area — the schema-4
    // failure. Bounded, the silhouette is the declaration and nothing else.
    expect(unbounded).toBeGreaterThan(1.8 * region.areaPx);
    expect(bounded).toBe(region.areaPx);
  });

  it("still reads the pixels inside the bound rather than returning the bound", () => {
    // The same halo, and no body: bounded extraction finds nothing, because
    // every departure is outside the declaration.
    const haloOnly = fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) => {
      if (inside(x, y)) return 0.8;
      const d = distance(x, y);
      return d <= 20 ? 0.8 * (1 - 0.25 * (1 - d / 20)) : 0.8;
    });
    expect(extract(haloOnly, region.silhouette)).toBe(0);

    // A departure of the same magnitude moved INSIDE the declaration is found,
    // and only where it is: the bound decides where to look, the pixels decide
    // what is there.
    const patchOnly = fromLinearLuminance(CANVAS.width, CANVAS.height, (x, y) =>
      inside(x, y) && distance(x, y) <= -10 ? 0.6 : 0.8,
    );
    const patch = extract(patchOnly, region.silhouette);
    expect(patch).toBeGreaterThan(0);
    expect(patch).toBeLessThan(region.areaPx);
  });
});
