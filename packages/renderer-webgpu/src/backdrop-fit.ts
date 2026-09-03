/**
 * Where a backdrop texture sits on the plane, and what that makes of a CSS px.
 *
 * The optics pass samples the backdrop through one uv transform on
 * viewport-normalised coordinates — `uv = viewport01 · scale + offset` — and
 * the pyramid converts the material's CSS-px σ into source texels once, at build.
 * Both numbers are functions of the same thing: the rectangle of the viewport the
 * texture's pixels actually occupy. This module is the one place that rectangle
 * turns into either.
 *
 * ## Placed
 *
 * A texture handed over from a DOM element — an `<img>`, a `<canvas>`, a
 * `<video>` — has a box the host measures every read phase, in CSS px relative
 * to the viewport, and that box IS the placement: a 320 px raster in the corner
 * of a 1440 px page maps the 320 px, not the page. The source's own extent is
 * still what the pyramid is built from; the placement only says where on the
 * plane its texels land, so one texel is `placement.width / sourceWidth` CSS px.
 *
 * Outside the placement the sampler clamps to the edge. A surface hanging past
 * the texture's box reads the nearest edge texel rather than nothing; the
 * unsampled layer (W11a) is not applied to partial overlap in this cut.
 *
 * ## Cover
 *
 * A source with no placement — an `ImageBitmap`, an `OffscreenCanvas`, an
 * element not in the document, or a renderer driven without a host at all —
 * keeps the original rule: the backdrop fills the viewport and the overflow is
 * cropped symmetrically. Every golden and every calibration capture was taken
 * with the texture the size of the stage, where the two rules coincide exactly;
 * the demo's reference panel is where they came apart (claims §5.47).
 */

import type { Rect } from "./render-model";

/** `[scaleX, scaleY, offsetX, offsetY]` on viewport-normalised coordinates. */
export type BackdropFit = readonly [number, number, number, number];

/** A backdrop source's box on the plane, in CSS px relative to the viewport. */
export type BackdropPlacement = Rect;

export const IDENTITY_FIT: BackdropFit = [1, 1, 0, 0];

/** A placement with a zero or negative side places nothing and falls back to cover. */
export function isUsablePlacement(placement: BackdropPlacement | undefined): placement is Rect {
  return (
    placement !== undefined &&
    Number.isFinite(placement.x) &&
    Number.isFinite(placement.y) &&
    placement.width > 0 &&
    placement.height > 0
  );
}

/**
 * Cover fit: the backdrop fills the viewport and the overflow is cropped
 * symmetrically, aspect preserved.
 */
export function coverFit(
  sourceWidth: number,
  sourceHeight: number,
  viewportWidthCss: number,
  viewportHeightCss: number,
): BackdropFit {
  const viewportAspect = viewportHeightCss > 0 ? viewportWidthCss / viewportHeightCss : 1;
  const sourceAspect = sourceHeight > 0 ? sourceWidth / sourceHeight : 1;
  if (sourceAspect > viewportAspect) {
    const scaleX = viewportAspect / sourceAspect;
    return [scaleX, 1, (1 - scaleX) / 2, 0];
  }
  const scaleY = sourceAspect / viewportAspect;
  return [1, scaleY, 0, (1 - scaleY) / 2];
}

/**
 * Placed fit: `uv = (viewport01 · viewportCss − placement.xy) / placement.wh`,
 * so a viewport pixel inside the placement lands on the texel under it and one
 * outside lands beyond [0, 1], where the sampler clamps.
 */
export function placementFit(
  placement: BackdropPlacement,
  viewportWidthCss: number,
  viewportHeightCss: number,
): BackdropFit {
  return [
    viewportWidthCss / placement.width,
    viewportHeightCss / placement.height,
    -placement.x / placement.width,
    -placement.y / placement.height,
  ];
}

export function backdropFit(
  sourceWidth: number,
  sourceHeight: number,
  placement: BackdropPlacement | undefined,
  viewportWidthCss: number,
  viewportHeightCss: number,
): BackdropFit {
  return isUsablePlacement(placement)
    ? placementFit(placement, viewportWidthCss, viewportHeightCss)
    : coverFit(sourceWidth, sourceHeight, viewportWidthCss, viewportHeightCss);
}

/**
 * Source texels per CSS px — the factor a CSS-px σ or displacement is multiplied
 * by to land in the source's own pixels.
 *
 * Placed: the width alone decides. A source drawn into a box of a different
 * aspect than its own (an `<img>` under `object-fit`, a canvas stretched by CSS)
 * has two densities, and the body blur is one isotropic σ; the wider axis is the
 * one a reader sees the frost across, so it is the one honoured. Cover: the axis
 * the crop keeps — the larger ratio — as it always was.
 */
export function texelsPerCssPx(
  sourceWidth: number,
  sourceHeight: number,
  placement: BackdropPlacement | undefined,
  viewportWidthCss: number,
  viewportHeightCss: number,
): number {
  if (isUsablePlacement(placement)) {
    return sourceWidth > 0 ? sourceWidth / placement.width : 1;
  }
  return viewportWidthCss > 0 && viewportHeightCss > 0
    ? Math.max(sourceWidth / viewportWidthCss, sourceHeight / viewportHeightCss)
    : 1;
}

/** Two placements that would produce the same fit and density. */
export function samePlacement(
  a: BackdropPlacement | undefined,
  b: BackdropPlacement | undefined,
): boolean {
  if (a === undefined || b === undefined) return a === b;
  return a.x === b.x && a.y === b.y && a.width === b.width && a.height === b.height;
}
