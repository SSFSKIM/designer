/**
 * What the page displays under a glass footprint, measured, and the hint that states it.
 *
 * A declared hint overrides the runtime's own tone reading on both tiers: on the CSS tier it is the
 * only reading there is, and on the WebGPU tier a texture group still refracts the still's own
 * pixels while its measured local tone stands down for the declaration (platform-web `root.ts`,
 * the declared luminance; renderer-webgpu `renderer.ts`, `backdropToneHint`). So every group's
 * hint here is measured off what the reader sees under that group's footprint, at the moment it is
 * declared, rather than typed once at one window size: the crop is a cover fit and moves with the
 * viewport, and the bar re-lays itself out below 1360 px (DESIGN.md, groups).
 *
 * The displayed image is composed by the page, so the page can compose it again: the still,
 * read back from the canvas it was painted into, with the scroll column's paper laid over it
 * wherever the column paints paper, at the alpha of the scroll edge's mask at that row. That is
 * the composite the browser draws, in the same encoded space it blends in. The column's type,
 * rules and printed figure are not modelled; the paper is. DESIGN.md records the size of that
 * approximation against a capture.
 *
 * The reduction is the runtime's own silhouette reading (platform-web `backdrop-tone.ts`,
 * `silhouetteBackdropTone`): encoded Rec. 709 luma averaged over the device-pixel centres inside
 * the rounded footprint, decoded to linear once. `complexity` is the spread of the same luma,
 * as a fraction of its largest possible value (0.5, a field half black and half white). The
 * runtime consumes no complexity (platform-web `optics.ts`, `materialAtBackdrop`); it is stated
 * for the record.
 */

import type { BackdropHint } from "@vitreajs/vitrea-react";
import type { GlassFrameRenderInput } from "@vitreajs/vitrea-web";

/** A glass surface's footprint in viewport CSS px, with its corner radius. */
export interface Footprint {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
  readonly radius: number;
}

/** A box of the scroll column that paints paper, and that paper's encoded luma. */
export interface Paper {
  readonly rect: DOMRectReadOnly;
  readonly luma: number;
}

/** Where the scroll edge's mask starts and where it reaches opaque, in viewport CSS px. */
export interface ScrollEdge {
  readonly start: number;
  readonly end: number;
}

/** Encoded luma under a footprint: its mean, its spread, and how much of it was paper. */
export interface Reading {
  readonly encoded: number;
  readonly spread: number;
  readonly paper: number;
}

const luma = (r: number, g: number, b: number): number =>
  (0.2126 * r + 0.7152 * g + 0.0722 * b) / 255;

const decode = (c: number): number => (c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4);

/**
 * Read the displayed composite under one footprint. `plane` is the still's canvas, painted at the
 * device-pixel size of the viewport and fixed over it, so a viewport point maps to a canvas pixel
 * by the ratio of the two.
 */
export function displayedUnder(
  plane: HTMLCanvasElement,
  footprint: Footprint,
  papers: readonly Paper[],
  edge: ScrollEdge,
): Reading | undefined {
  const context = plane.getContext("2d", { willReadFrequently: true });
  const box = plane.getBoundingClientRect();
  if (context === null || box.width === 0 || box.height === 0) return undefined;
  const sx = plane.width / box.width;
  const sy = plane.height / box.height;
  const { x, y, width, height } = footprint;
  const x0 = Math.max(0, Math.floor((x - box.left) * sx));
  const y0 = Math.max(0, Math.floor((y - box.top) * sy));
  const x1 = Math.min(plane.width, Math.ceil((x + width - box.left) * sx));
  const y1 = Math.min(plane.height, Math.ceil((y + height - box.top) * sy));
  if (x1 <= x0 || y1 <= y0) return undefined;
  const data = context.getImageData(x0, y0, x1 - x0, y1 - y0).data;

  const radius = Math.max(0, Math.min(footprint.radius, width / 2, height / 2));
  const cx = x + width / 2;
  const cy = y + height / 2;
  const ramp = Math.max(1e-6, edge.end - edge.start);
  let sum = 0;
  let squares = 0;
  let paperWeight = 0;
  let count = 0;
  for (let row = y0; row < y1; row += 1) {
    const py = box.top + (row + 0.5) / sy;
    // The mask is a vertical ramp, so a row shares one alpha wherever the column is painted.
    const mask = Math.min(1, Math.max(0, (py - edge.start) / ramp));
    for (let col = x0; col < x1; col += 1) {
      const px = box.left + (col + 0.5) / sx;
      const qx = Math.abs(px - cx) - width / 2 + radius;
      const qy = Math.abs(py - cy) - height / 2 + radius;
      const distance =
        Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) + Math.min(Math.max(qx, qy), 0) - radius;
      if (distance > 0) continue;
      const i = ((row - y0) * (x1 - x0) + (col - x0)) * 4;
      const still = luma(data[i] as number, data[i + 1] as number, data[i + 2] as number);
      let shown = still;
      if (mask > 0) {
        const paper = papers.find(
          (p) => px >= p.rect.left && px < p.rect.right && py >= p.rect.top && py < p.rect.bottom,
        );
        if (paper !== undefined) {
          shown = still * (1 - mask) + paper.luma * mask;
          paperWeight += mask;
        }
      }
      sum += shown;
      squares += shown * shown;
      count += 1;
    }
  }
  if (count === 0) return undefined;
  const encoded = sum / count;
  return {
    encoded,
    spread: Math.sqrt(Math.max(0, squares / count - encoded * encoded)),
    paper: paperWeight / count,
  };
}

/**
 * The hint a reading states. The luminance carries the level: the runtime reads it whenever the
 * tone is `light` or `dark` (platform-web `css-tier.ts`, `hintedBackdropLuminance`), so the tone
 * is only the coarse class, split at the middle of the encoded scale. Quantised, so a repaint that
 * moves nothing the runtime could act on does not patch the group.
 */
export function hintFrom(reading: Reading): BackdropHint {
  return {
    tone: reading.encoded >= 0.5 ? "light" : "dark",
    luminance: Math.round(decode(reading.encoded) * 100) / 100,
    complexity: Math.round(Math.min(1, reading.spread / 0.5) * 20) / 20,
  };
}

/**
 * A surface's body as the runtime states it for the frame it is drawing: its tint layer's encoded
 * luma and the alpha that layer is laid over the blurred backdrop with (`MaterialOptics`, "also the
 * occlusion knob"), after the accessibility and pose folds.
 */
export interface Body {
  readonly tint: number;
  readonly alpha: number;
}

export type Ink = "dark" | "light";

/** The relative luminance at which black and white ink read the same ratio, about 4.58:1. */
const CROSSOVER = Math.sqrt(1.05 * 0.05) - 0.05;

/** The body the runtime publishes for a group's surface in this frame, if it is drawing one. */
export function bodyOf(
  input: GlassFrameRenderInput | undefined,
  groupId: string,
): Body | undefined {
  for (const plane of input?.planes ?? []) {
    for (const node of plane.nodes) {
      if (node.groupId !== groupId) continue;
      const [r, g, b] = node.optics.tint;
      return { tint: luma(r, g, b), alpha: node.optics.tintAlpha };
    }
  }
  return undefined;
}

/**
 * One label's ink, from its own reading. The runtime picks one pole per surface, off the surface's
 * whole backdrop; a surface whose backdrop straddles two levels (the platter across the sheet's
 * edge) then has a body brighter over one part than over the other, on either side of the
 * crossover. So each label predicts its own ground as the runtime composes it (the tint over the
 * backdrop under the label at the tint's alpha, in encoded space, as the layer blends) and takes
 * the pole that reads the higher ratio against it.
 */
export function inkOver(reading: Reading, body: Body): Ink {
  const ground = body.alpha * body.tint + (1 - body.alpha) * reading.encoded;
  return decode(ground) >= CROSSOVER ? "dark" : "light";
}

export const sameHint = (a: BackdropHint | undefined, b: BackdropHint | undefined): boolean =>
  a?.tone === b?.tone && a?.luminance === b?.luminance && a?.complexity === b?.complexity;

let swatch: CanvasRenderingContext2D | null | undefined;

/** An element's painted background as encoded luma, resolved by the browser's own conversion. */
export function paperOf(element: Element): Paper | undefined {
  const colour = getComputedStyle(element).backgroundColor;
  if (swatch === undefined) {
    const canvas = document.createElement("canvas");
    canvas.width = 1;
    canvas.height = 1;
    swatch = canvas.getContext("2d", { willReadFrequently: true });
  }
  if (swatch === null) return undefined;
  swatch.clearRect(0, 0, 1, 1);
  swatch.fillStyle = colour;
  swatch.fillRect(0, 0, 1, 1);
  const [r, g, b, a] = swatch.getImageData(0, 0, 1, 1).data;
  if (a === undefined || a < 255) return undefined;
  const rect = element.getBoundingClientRect();
  return { rect, luma: luma(r as number, g as number, b as number) };
}
