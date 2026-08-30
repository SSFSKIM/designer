/**
 * The declared component region: where the scene matrix says the surface is.
 *
 * ## Why the instrument needs this at all
 *
 * Through schema 4 the shape axis found the surface by differencing a capture
 * against the raster background it was composited over — *anything that differs
 * from the known background is inside*. The active-pose bed falsified that
 * premise (wave Decision Log 15, claims §5.11): Apple's active material casts an
 * outer shadow, the shadow differs from the background, and the extractor
 * therefore returned the component **and its shadow** as one body — native
 * silhouettes at roughly twice the declared area, with the material axis's
 * interior statistics sampled under that same confounded mask.
 *
 * The ruling was to bound the search. The scene matrix already declares every
 * component's geometry — that is what both harnesses lay out from — so the
 * region is *derived from the declaration*, never from the image. An
 * image-derived bound would be the same circularity in a longer form: the
 * shadow would still be in the pixels the bound was fitted to.
 *
 * ## What that costs, stated here because the cost is the design
 *
 * Inside the bound the two sides' silhouettes are still compared to each other
 * on every term — coverage, contour position, corner profile. Outside it,
 * nothing is recovered: a surface drawn *larger* than its declaration is clipped
 * to the declaration and reads as a match. **Area recovery is therefore partly
 * assumed rather than measured**, and the axis's honest claim shrinks to "each
 * side fills, and stays inside, the geometry the scene declares". Over-fill is
 * not measurable against a shadow-casting reference by luminance differencing at
 * all — see `DEFAULT_COMPONENT_REGION_MARGIN_PX`.
 *
 * ## Placement is owned here, once
 *
 * `web/scenes.ts` lays the same declaration out for the DOM and reads its
 * numbers from this module rather than restating them. Two hand-kept copies of a
 * rect would drift, and the drift would be indistinguishable from a fidelity
 * finding — which is the same reason `web/scenes.ts` refuses to restate a
 * geometry value from `scenes.json`.
 */

import { CalibrationError } from "./errors";
import type { Silhouette } from "./silhouette";

/** One rounded rectangle, exactly as the scene matrix declares it, in points. */
export interface DeclaredShape {
  readonly kind: string;
  readonly size: readonly [number, number];
  /** Absent on a capsule, whose radius is half its short side by definition. */
  readonly radius?: number;
  /** Displacement from the canvas centre, in points. */
  readonly offset?: readonly [number, number];
}

/** Siblings in one container, laid out in a row at a declared spacing. */
export interface DeclaredGroup {
  readonly kind: "group";
  readonly items: readonly DeclaredShape[];
  readonly spacing: number;
}

/** An overlay surface over a base one — S1's mandated stacked scene. */
export interface DeclaredStack {
  readonly kind: "stack";
  readonly base: DeclaredShape;
  readonly over: DeclaredShape;
}

export type DeclaredComponent = DeclaredShape | DeclaredGroup | DeclaredStack;

/** The canvas the scene matrix declares, in points. */
export interface CanvasSize {
  readonly width: number;
  readonly height: number;
}

/** One shape placed on the canvas, in points, ready to scale to device pixels. */
export interface PlacedShape {
  readonly kind: string;
  readonly left: number;
  readonly top: number;
  readonly width: number;
  readonly height: number;
  /** Uniform corner radius, per X8's v1 restriction. */
  readonly radius: number;
}

const isGroup = (spec: DeclaredComponent): spec is DeclaredGroup => spec.kind === "group";
const isStack = (spec: DeclaredComponent): spec is DeclaredStack => spec.kind === "stack";

/**
 * A capsule's corner radius is half its short side — the value that makes the
 * shape a stadium, which is what `Capsule()` draws. Derived rather than read,
 * because `scenes.json` gives capsules no radius and a second copy of the rule
 * could disagree with the native side's.
 */
function radiusOf(spec: DeclaredShape): number {
  if (spec.kind === "capsule") return Math.min(spec.size[0], spec.size[1]) / 2;
  if (spec.kind === "rrect") return spec.radius ?? 0;
  throw new CalibrationError(
    "malformed-report",
    `componentRegion: the scene matrix declares a "${spec.kind}" shape, which this instrument has no ` +
      `geometry for. Add it here — a bound guessed from a shape nobody modelled would silently mis-state ` +
      `every shape and shadow figure over that scene.`,
  );
}

/**
 * Centre a box in the canvas, then apply the scene's own offset — `ZStack`'s
 * default alignment, spelled out. `Math.round` matches SwiftUI laying out on the
 * point grid; every size in the current matrix centres to an integer anyway.
 */
function place(spec: DeclaredShape, canvas: CanvasSize, left?: number, top?: number): PlacedShape {
  const [width, height] = spec.size;
  const [offsetX, offsetY] = spec.offset ?? [0, 0];
  return {
    kind: spec.kind,
    left: left ?? Math.round((canvas.width - width) / 2) + offsetX,
    top: top ?? Math.round((canvas.height - height) / 2) + offsetY,
    width,
    height,
    radius: radiusOf(spec),
  };
}

/**
 * Lay a declared component out on the canvas, in points.
 *
 * The order is the declaration's own — group items left to right, a stack's base
 * before its overlay — so a caller that needs to attach per-surface identity
 * (`web/scenes.ts` does) can zip against the declaration rather than re-deriving
 * the layout.
 */
export function placeComponent(component: DeclaredComponent, canvas: CanvasSize): readonly PlacedShape[] {
  if (isGroup(component)) {
    const total =
      component.items.reduce((sum, item) => sum + item.size[0], 0) +
      component.spacing * (component.items.length - 1);
    const height = Math.max(...component.items.map((item) => item.size[1]));
    const top = Math.round((canvas.height - height) / 2);
    let left = Math.round((canvas.width - total) / 2);

    const placed: PlacedShape[] = [];
    for (const item of component.items) {
      placed.push(place(item, canvas, left, top + Math.round((height - item.size[1]) / 2)));
      left += item.size[0] + component.spacing;
    }
    return placed;
  }

  if (isStack(component)) {
    return [place(component.base, canvas), place(component.over, canvas)];
  }

  return [place(component, canvas)];
}

/**
 * Exact signed distance from a point to a rounded rectangle, in the same units.
 * Negative inside, zero on the contour, positive outside — the standard 2-D
 * rounded-box form, which is exact everywhere rather than only near the contour.
 */
function roundedRectSignedDistance(
  x: number,
  y: number,
  centreX: number,
  centreY: number,
  halfWidth: number,
  halfHeight: number,
  radius: number,
): number {
  const qx = Math.abs(x - centreX) - (halfWidth - radius);
  const qy = Math.abs(y - centreY) - (halfHeight - radius);
  return (
    Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - radius
  );
}

/**
 * The margin the declared region is dilated by, in **device pixels**, and it is
 * zero — which is a measured decision rather than an omission.
 *
 * A margin exists to admit real edge softness: the antialiased boundary band,
 * and any part of the material that legitimately sits a fraction of a pixel past
 * its declared contour. On this bed there is no such band to admit *on its own*.
 * The reference's occlusion field begins at the contour with no gap — measured
 * over `apple-macos-26.5-1x-light-standard`, the mean occlusion in the first
 * one-pixel ring outside the declared contour is 0.05…0.19 of the backdrop's own
 * level, i.e. fully-developed shadow — so every pixel of outward margin admits
 * shadow-darkened backdrop into the reference's silhouette and almost none into
 * a renderer that draws no shadow. The cost was measured directly: one device
 * pixel of margin moves IoU on `photo__capsule-button__rest` from 1.000 to
 * 0.970 and on `light-solid__capsule-button__rest` from 0.888 to 0.850, all of
 * it the shadow re-entering the shape axis that the bound exists to keep it out
 * of.
 *
 * So the bound is the declared region itself, rasterised by pixel-centre
 * containment, and the axis's noise floor stays what `silhouette.ts` already
 * declares it to be: the raster grid, ±0.5 px. The margin remains a parameter
 * because it is a judgement about a bed, not a law — a reference that ever casts
 * no shadow could afford one, and the cell records the value it was measured at.
 */
export const DEFAULT_COMPONENT_REGION_MARGIN_PX = 0;

export interface ComponentRegionOptions {
  /** The canvas the component is centred in, in points. */
  readonly canvas: CanvasSize;
  /** Device pixels per point — the profile's backing scale. */
  readonly scale: number;
  /** The capture's size in device pixels. */
  readonly width: number;
  readonly height: number;
  /** Outward dilation in device pixels; see `DEFAULT_COMPONENT_REGION_MARGIN_PX`. */
  readonly marginPx?: number;
}

/**
 * The declared region, as a mask plus the geometry every bounded metric reads
 * off it.
 *
 * `signedDistancePx` is kept because the shadow axis profiles by *distance from
 * the declared contour*, and that distance is exact here — analytic, from the
 * declaration — where a distance transform of the extracted mask would inherit
 * whatever the extractor got wrong.
 */
export interface ComponentRegion {
  /** Inside the declared geometry, dilated by `marginPx`. */
  readonly silhouette: Silhouette;
  /** Exact signed distance to the declared contour, device px, negative inside. */
  readonly signedDistancePx: Float64Array;
  readonly areaPx: number;
  readonly marginPx: number;
  /** Centre of the declared bounding box, device px. */
  readonly centreX: number;
  readonly centreY: number;
  /** Half-extents of the declared bounding box, device px. */
  readonly halfWidth: number;
  readonly halfHeight: number;
  readonly placed: readonly PlacedShape[];
}

/**
 * Build the declared region for one scene at one backing scale.
 *
 * The capture size is checked against the declaration rather than trusted: a
 * capture that is not `canvas × scale` was framed differently from the scene the
 * geometry describes, and every bounded number over it would be a measurement of
 * that mistake wearing the scene's name.
 */
export function componentRegion(
  component: DeclaredComponent,
  options: ComponentRegionOptions,
): ComponentRegion {
  const { canvas, scale, width, height } = options;
  const marginPx = options.marginPx ?? DEFAULT_COMPONENT_REGION_MARGIN_PX;

  if (width !== Math.round(canvas.width * scale) || height !== Math.round(canvas.height * scale)) {
    throw new CalibrationError(
      "dimension-mismatch",
      `componentRegion: the capture is ${width}x${height} but the scene matrix declares a ` +
        `${canvas.width}x${canvas.height} canvas at ${scale}x, which is ` +
        `${Math.round(canvas.width * scale)}x${Math.round(canvas.height * scale)}. The declared geometry ` +
        `cannot be placed on a capture that was framed differently.`,
    );
  }

  const placed = placeComponent(component, canvas);
  const boxes = placed.map((shape) => ({
    centreX: (shape.left + shape.width / 2) * scale,
    centreY: (shape.top + shape.height / 2) * scale,
    halfWidth: (shape.width / 2) * scale,
    halfHeight: (shape.height / 2) * scale,
    radius: shape.radius * scale,
  }));

  const signedDistancePx = new Float64Array(width * height);
  const mask = new Uint8Array(width * height);
  let areaPx = 0;
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      // Pixel centres, matching the convention the distance transform and the
      // contour trace already use.
      const px = x + 0.5;
      const py = y + 0.5;
      let nearest = Number.POSITIVE_INFINITY;
      for (const box of boxes) {
        const distance = roundedRectSignedDistance(
          px,
          py,
          box.centreX,
          box.centreY,
          box.halfWidth,
          box.halfHeight,
          box.radius,
        );
        if (distance < nearest) nearest = distance;
      }
      const index = y * width + x;
      signedDistancePx[index] = nearest;
      if (nearest <= marginPx) {
        mask[index] = 1;
        areaPx += 1;
      }
    }
  }

  if (areaPx === 0) {
    throw new CalibrationError(
      "empty-region",
      "componentRegion: the declared geometry covers no pixel of this capture.",
    );
  }

  const minX = Math.min(...boxes.map((box) => box.centreX - box.halfWidth));
  const maxX = Math.max(...boxes.map((box) => box.centreX + box.halfWidth));
  const minY = Math.min(...boxes.map((box) => box.centreY - box.halfHeight));
  const maxY = Math.max(...boxes.map((box) => box.centreY + box.halfHeight));

  return {
    silhouette: { width, height, mask },
    signedDistancePx,
    areaPx,
    marginPx,
    centreX: (minX + maxX) / 2,
    centreY: (minY + maxY) / 2,
    halfWidth: (maxX - minX) / 2,
    halfHeight: (maxY - minY) / 2,
    placed,
  };
}

/**
 * Analytic area of the declared geometry in device pixels — a rectangle less its
 * four corner offcuts, each of which removes `r² − πr²/4`.
 *
 * The right-hand side of the shape axis's conditioning predicate, and reported
 * next to `ComponentRegion.areaPx` so a reader can tell the *declaration* from
 * its rasterisation. Overlapping members are counted twice, which is why a
 * stacked component's declared area is not this sum; the callers that need one
 * number for such a component compute it from the geometry they know.
 */
export function declaredShapeArea(shape: PlacedShape, scale: number): number {
  const width = shape.width * scale;
  const height = shape.height * scale;
  const radius = shape.radius * scale;
  return width * height - (4 - Math.PI) * radius * radius;
}
