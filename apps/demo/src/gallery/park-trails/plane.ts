/**
 * The live plane and what the page knows about it.
 *
 * The plane is one photograph painted cover-fit into a viewport-fixed canvas. Because the page
 * paints it, the page can also say, honestly and from pixels, what any rectangle of it looks
 * like: `paint` keeps a downsampled field of encoded luma beside the canvas, and `measure`
 * answers "what is behind this rectangle right now" from that field, the printed sheet as
 * modelled from its DOM (paper.ts) and the scroll-edge mask that fades the sheet over it. Every
 * group's declared backdrop is that answer (DESIGN.md, groups), and a declaration overrides the
 * runtime's own tone reading on both tiers, so the material adapts to a measurement of what is
 * displayed rather than to a number typed once.
 */

import { CELL, sheetLumaAt, type SheetField } from "./paper";

export interface Crop {
  /** Extra zoom over a plain cover fit, so the crop can choose its band. */
  readonly zoom: number;
  /** Where the overflow goes, 0 = keep the image's left/top edge, 1 = its right/bottom. */
  readonly fx: number;
  readonly fy: number;
}

/**
 * The crop, chosen by looking (DESIGN.md, decisions): enough zoom to lift the cloud bank out of
 * the band the planner sits in, so the band is the forested ridge line and the valley's far wall.
 */
export const PARK_CROP: Crop = { zoom: 1.4, fx: 0.4, fy: 0.94 };

export interface Placement {
  readonly dx: number;
  readonly dy: number;
  readonly dw: number;
  readonly dh: number;
}

export function placeImage(
  imageWidth: number,
  imageHeight: number,
  width: number,
  height: number,
  crop: Crop,
): Placement {
  const scale = Math.max(width / imageWidth, height / imageHeight) * crop.zoom;
  const dw = imageWidth * scale;
  const dh = imageHeight * scale;
  return { dx: (width - dw) * crop.fx, dy: (height - dh) * crop.fy, dw, dh };
}

/** Encoded Rec. 709 luma of the painted plane, one cell per `CELL` CSS px, row-major. */
export interface LumaField {
  readonly columns: number;
  readonly rows: number;
  readonly luma: Float32Array;
}

export function buildField(
  image: CanvasImageSource,
  placement: Placement,
  width: number,
  height: number,
): LumaField {
  const columns = Math.max(1, Math.ceil(width / CELL));
  const rows = Math.max(1, Math.ceil(height / CELL));
  const scratch = document.createElement("canvas");
  scratch.width = columns;
  scratch.height = rows;
  const context = scratch.getContext("2d", { willReadFrequently: true });
  if (context === null) throw new Error("park-trails: no 2D context for the luma field.");
  context.imageSmoothingQuality = "high";
  context.drawImage(
    image,
    placement.dx / CELL,
    placement.dy / CELL,
    placement.dw / CELL,
    placement.dh / CELL,
  );
  const { data } = context.getImageData(0, 0, columns, rows);
  const luma = new Float32Array(columns * rows);
  for (let i = 0; i < luma.length; i += 1) {
    const at = i * 4;
    luma[i] =
      (0.2126 * (data[at] ?? 0) + 0.7152 * (data[at + 1] ?? 0) + 0.0722 * (data[at + 2] ?? 0)) / 255;
  }
  return { columns, rows, luma };
}

/** What the page currently holds about the plane, the sheet and the scroll edge. */
export interface PlaneState {
  field: LumaField | undefined;
  /** The sheet as displayed, in its own coordinates (paper.ts). */
  sheet: SheetField | undefined;
  /** Viewport y of the sheet's top edge. */
  sheetTop: number;
  /** Viewport y where the scroll-edge mask starts letting the sheet through, and where it is opaque. */
  fadeStart: number;
  fadeEnd: number;
}

export const planeState: PlaneState = {
  field: undefined,
  sheet: undefined,
  sheetTop: Number.POSITIVE_INFINITY,
  fadeStart: 0,
  fadeEnd: 0,
};

export interface Rect {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export interface Measured {
  readonly tone: "light" | "dark";
  /** Linear relative luminance, 0..1: the encoded mean decoded once. */
  readonly luminance: number;
  readonly complexity: number;
  /** The encoded mean, kept for the record. */
  readonly encoded: number;
}

const decode = (encoded: number): number =>
  encoded <= 0.04045 ? encoded / 12.92 : ((encoded + 0.055) / 1.055) ** 2.4;

/**
 * The backdrop under `rect`, as displayed, cell by cell: the photograph where the sheet is absent
 * or masked away, the printed sheet (paper, fills, rules and the ink of its text, paper.ts) where
 * it is present, blended by the mask's alpha at the cell's row. Averaged in encoded space and
 * decoded once, which is the model the runtime's own CSS-tier reading uses.
 */
export function measure(rect: Rect, state: PlaneState = planeState): Measured | undefined {
  const field = state.field;
  if (field === undefined || rect.width <= 0 || rect.height <= 0) return undefined;
  const x0 = Math.max(0, Math.floor(rect.x / CELL));
  const x1 = Math.min(field.columns, Math.ceil((rect.x + rect.width) / CELL));
  const y0 = Math.max(0, Math.floor(rect.y / CELL));
  const y1 = Math.min(field.rows, Math.ceil((rect.y + rect.height) / CELL));
  const fadeSpan = Math.max(1, state.fadeEnd - state.fadeStart);
  const sheet = state.sheet;

  let total = 0;
  let totalSquares = 0;
  let count = 0;
  for (let row = y0; row < y1; row += 1) {
    const top = row * CELL;
    const mask = Math.min(1, Math.max(0, (top + CELL / 2 - state.fadeStart) / fadeSpan));
    const alpha = sheet !== undefined && top + CELL / 2 >= state.sheetTop ? mask : 0;
    for (let column = x0; column < x1; column += 1) {
      const photo = field.luma[row * field.columns + column] ?? 0;
      const shown =
        sheet === undefined || alpha === 0
          ? photo
          : photo * (1 - alpha) +
            sheetLumaAt(sheet, column - Math.round(sheet.left / CELL), top - state.sheetTop) * alpha;
      total += shown;
      totalSquares += shown * shown;
      count += 1;
    }
  }
  if (count === 0) return undefined;
  const encoded = total / count;
  const variance = Math.max(0, totalSquares / count - encoded * encoded);
  const luminance = decode(encoded);
  return {
    tone: luminance >= 0.18 ? "light" : "dark",
    luminance,
    complexity: Math.min(1, Math.sqrt(variance) / 0.25),
    encoded,
  };
}
