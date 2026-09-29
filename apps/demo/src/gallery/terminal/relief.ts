/**
 * The Lake Tahoe basin as a relief map: the data the build script wrote (`data/relief.*`, see
 * `scripts/build-terminal-relief.mjs`), and the painter that draws it into a canvas for one
 * viewport and one colour scheme.
 *
 * The map is drawn in the hillshade's own pixel space (Web Mercator at zoom 12, about 30 m a
 * pixel), scaled so the viewport spans a fixed ground width and placed so Lake Tahoe lies under
 * a chosen point. Contours and shores are vectors, stroked at the device's resolution, so the
 * fine structure the lens bends at the window's rim stays sharp at any pixel ratio; only the
 * hillshade is a raster, and it is the broad structure.
 */

import binUrl from "./data/relief.bin?url";
import meta from "./data/relief.json";
import shadeUrl from "./data/relief.webp";
import type { Scheme } from "./shell/types";

export type ReliefMeta = typeof meta;

export interface ReliefLine {
  /** A contour's elevation in metres, or −1 − n for the shore of lake n. */
  readonly key: number;
  readonly closed: boolean;
  /** x, y pairs in the hillshade's pixel space. */
  readonly points: Float32Array;
}

export interface Relief {
  readonly meta: ReliefMeta;
  readonly contours: readonly ReliefLine[];
  /** Each lake's shore lines, by lake index; an island is a second closed line. */
  readonly shores: readonly (readonly ReliefLine[])[];
  readonly shade: ImageBitmap;
}

/** The ground width the viewport spans on a landscape screen, and the height on a portrait one. */
const SPAN_ACROSS_M = 38_000;
const SPAN_DOWN_M = 60_000;

export async function loadRelief(): Promise<Relief> {
  const [bin, shade] = await Promise.all([
    fetch(binUrl).then((r) => {
      if (!r.ok) throw new Error(`relief.bin answered ${String(r.status)}`);
      return r.arrayBuffer();
    }),
    fetch(shadeUrl)
      .then((r) => r.blob())
      .then((blob) => createImageBitmap(blob)),
  ]);
  const lines = parseVectors(bin);
  const shores: ReliefLine[][] = meta.lakes.map(() => []);
  const contours: ReliefLine[] = [];
  for (const line of lines) {
    if (line.key < 0) shores[-1 - line.key]?.push(line);
    else contours.push(line);
  }
  return { meta, contours, shores, shade };
}

/** `relief.bin`'s layout is documented at the build script's `writeVectors`. */
export function parseVectors(buffer: ArrayBuffer): ReliefLine[] {
  const view = new DataView(buffer);
  const bytes = new Uint8Array(buffer);
  const magic = String.fromCharCode(...bytes.subarray(0, 4));
  if (magic !== "RLF1") throw new Error(`relief.bin: unexpected magic ${magic}`);
  const count = view.getUint32(4, true);
  let o = 8;
  const varint = (): number => {
    let z = 0;
    let shift = 1;
    for (;;) {
      const b = bytes[o++] as number;
      z += (b & 0x7f) * shift;
      if (b < 0x80) break;
      shift *= 128;
    }
    return z % 2 === 0 ? z / 2 : -(z + 1) / 2;
  };
  const lines: ReliefLine[] = [];
  for (let n = 0; n < count; n++) {
    const key = view.getInt16(o, true);
    const closed = bytes[o + 2] === 1;
    const length = view.getUint32(o + 3, true);
    let x = view.getUint16(o + 7, true);
    let y = view.getUint16(o + 9, true);
    o += 11;
    const points = new Float32Array(length * 2);
    points[0] = x / 4;
    points[1] = y / 4;
    for (let k = 1; k < length; k++) {
      x += varint();
      y += varint();
      points[k * 2] = x / 4;
      points[k * 2 + 1] = y / 4;
    }
    lines.push({ key, closed, points });
  }
  return lines;
}

/** Where the map stands: CSS px per source pixel, and the source origin's position in CSS px. */
export interface ReliefView {
  readonly scale: number;
  readonly x: number;
  readonly y: number;
}

/**
 * The map's framing for a viewport, with Lake Tahoe's middle placed at `focus` (CSS px) as far as
 * the map's edges allow: the map always covers the viewport.
 */
export function reliefView(viewport: { readonly width: number; readonly height: number }, focus: { readonly x: number; readonly y: number }): ReliefView {
  const mpp = meta.metresPerPixel;
  const scale = Math.max(viewport.width / (SPAN_ACROSS_M / mpp), viewport.height / (SPAN_DOWN_M / mpp));
  const lake = meta.lakes[0] as { x: number; y: number };
  const clamp = (v: number, lo: number, hi: number): number => Math.min(hi, Math.max(lo, v));
  const x = clamp(focus.x - lake.x * scale, viewport.width - meta.width * scale, 0);
  const y = clamp(focus.y - lake.y * scale, viewport.height - meta.height * scale, 0);
  return { scale, x, y };
}

interface Palette {
  readonly land: string;
  readonly shade: { readonly mode: GlobalCompositeOperation; readonly alpha: number };
  readonly contour: string;
  readonly index: string;
  readonly water: string;
  readonly waterLine: string;
  readonly shore: string;
  readonly border: string;
  readonly label: string;
  readonly lakeLabel: string;
  readonly halo: string;
}

/**
 * Two maps, one per scheme, drawn from the same data. Light is a survey sheet: pale ground, the
 * relief shaded from the north-west, brown contours, blue water. Dark is the same sheet at night:
 * the relief on slate, the contours a cool grey, the lakes near black. Neither is a depicted
 * material; both are the content, and colour lives here rather than on the glass.
 */
const PALETTES: Record<Scheme, Palette> = {
  light: {
    land: "#eef0ea",
    shade: { mode: "multiply", alpha: 0.62 },
    contour: "rgba(142, 94, 52, 0.5)",
    index: "rgba(122, 76, 38, 0.82)",
    water: "#bcd5e7",
    waterLine: "rgba(76, 128, 172, 0.34)",
    shore: "rgba(54, 104, 150, 0.9)",
    border: "rgba(96, 72, 120, 0.7)",
    label: "#383d42",
    lakeLabel: "#3f6a90",
    halo: "rgba(238, 240, 234, 0.8)",
  },
  dark: {
    land: "#3b4651",
    shade: { mode: "multiply", alpha: 0.9 },
    contour: "rgba(160, 192, 206, 0.32)",
    index: "rgba(176, 208, 222, 0.58)",
    water: "#07121d",
    waterLine: "rgba(70, 132, 180, 0.42)",
    shore: "rgba(118, 170, 210, 0.85)",
    border: "rgba(180, 160, 210, 0.55)",
    label: "#b8c3cc",
    lakeLabel: "#7fa6c6",
    halo: "rgba(20, 26, 32, 0.7)",
  },
};

/** How far north of the lake's seed its name is set, in ground metres. */
const LAKE_LABEL_NORTH_M = 9_600;

/** Water lines inside each shore, in ground metres from it. */
const WATER_LINES_M = [140, 330, 600, 950, 1450];

/**
 * Paints the whole map into `ctx`, which covers the viewport at `dpr` device pixels per CSS px.
 * Deterministic for a given view, scheme and size: the page paints it once per change into a base
 * canvas and composes everything that moves over a copy.
 */
export function paintRelief(ctx: CanvasRenderingContext2D, relief: Relief, view: ReliefView, scheme: Scheme, dpr: number): void {
  const palette = PALETTES[scheme];
  const { width, height } = ctx.canvas;
  const s = view.scale * dpr;
  ctx.save();
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalCompositeOperation = "source-over";
  ctx.globalAlpha = 1;
  ctx.fillStyle = palette.land;
  ctx.fillRect(0, 0, width, height);

  ctx.setTransform(s, 0, 0, s, view.x * dpr, view.y * dpr);
  ctx.imageSmoothingEnabled = true;
  ctx.imageSmoothingQuality = "high";
  ctx.globalCompositeOperation = palette.shade.mode;
  ctx.globalAlpha = palette.shade.alpha;
  ctx.drawImage(relief.shade, 0, 0);
  ctx.globalCompositeOperation = "source-over";
  ctx.globalAlpha = 1;

  // Contours: every line thin, every fifth (the index lines) heavier.
  const px = 1 / s;
  const index = relief.meta.contourInterval * relief.meta.indexEvery;
  ctx.lineJoin = "round";
  ctx.lineCap = "round";
  for (const heavy of [false, true]) {
    ctx.beginPath();
    for (const line of relief.contours) {
      if ((line.key % index === 0) !== heavy) continue;
      trace(ctx, line);
    }
    ctx.strokeStyle = heavy ? palette.index : palette.contour;
    ctx.lineWidth = (heavy ? 1.15 : 0.6) * dpr * px;
    ctx.stroke();
  }

  // Lakes: flat water, water lines along the shore inside, then the shore itself.
  const metre = 1 / relief.meta.metresPerPixel;
  relief.shores.forEach((shores) => {
    if (shores.length === 0) return;
    const path = new Path2D();
    for (const line of shores) trace(path, line);
    ctx.save();
    ctx.fillStyle = palette.water;
    ctx.fill(path, "evenodd");
    ctx.clip(path, "evenodd");
    // A ring at distance d is a stroke of width 2d + w in the line's colour under one of 2d − w
    // in the water's, painted from the farthest ring in.
    for (let k = WATER_LINES_M.length - 1; k >= 0; k--) {
      const d = (WATER_LINES_M[k] as number) * metre;
      ctx.lineWidth = 2 * d + 0.9 * dpr * px;
      ctx.strokeStyle = palette.waterLine;
      ctx.stroke(path);
      ctx.lineWidth = Math.max(0, 2 * d - 0.9 * dpr * px);
      ctx.strokeStyle = palette.water;
      ctx.stroke(path);
    }
    ctx.restore();
    ctx.lineWidth = 1.1 * dpr * px;
    ctx.strokeStyle = palette.shore;
    ctx.stroke(path);
  });

  // The California–Nevada line.
  ctx.beginPath();
  relief.meta.border.forEach((p, k) => (k === 0 ? ctx.moveTo(p.x, p.y) : ctx.lineTo(p.x, p.y)));
  ctx.setLineDash([7 * px * dpr, 4 * px * dpr]);
  ctx.lineWidth = 1 * dpr * px;
  ctx.strokeStyle = palette.border;
  ctx.stroke();
  ctx.setLineDash([]);

  paintLabels(ctx, relief, view, palette, dpr);
  ctx.restore();
}

function trace(target: CanvasRenderingContext2D | Path2D, line: ReliefLine): void {
  const p = line.points;
  target.moveTo(p[0] as number, p[1] as number);
  for (let k = 2; k < p.length; k += 2) target.lineTo(p[k] as number, p[k + 1] as number);
  if (line.closed) target.closePath();
}

/** Labels are set in device pixels at the map's positions, so type stays crisp at any scale. */
function paintLabels(ctx: CanvasRenderingContext2D, relief: Relief, view: ReliefView, palette: Palette, dpr: number): void {
  const at = (p: { readonly x: number; readonly y: number }): [number, number] => [
    (view.x + p.x * view.scale) * dpr,
    (view.y + p.y * view.scale) * dpr,
  ];
  const face = `-apple-system, BlinkMacSystemFont, "SF Pro Text", system-ui, "Segoe UI", sans-serif`;
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.textBaseline = "middle";
  ctx.lineJoin = "round";
  const write = (text: string, x: number, y: number, font: string, colour: string, align: CanvasTextAlign, tracking = 0): void => {
    ctx.font = font;
    ctx.textAlign = align;
    ctx.letterSpacing = `${String(tracking * dpr)}px`;
    ctx.lineWidth = 3 * dpr;
    ctx.strokeStyle = palette.halo;
    ctx.strokeText(text, x, y);
    ctx.fillStyle = colour;
    ctx.fillText(text, x, y);
  };

  for (const summit of relief.meta.summits) {
    const [x, y] = at(summit);
    ctx.beginPath();
    const r = 4 * dpr;
    ctx.moveTo(x, y - r);
    ctx.lineTo(x + r * 0.9, y + r * 0.6);
    ctx.lineTo(x - r * 0.9, y + r * 0.6);
    ctx.closePath();
    ctx.fillStyle = palette.label;
    ctx.fill();
    write(summit.name, x + 8 * dpr, y - 6 * dpr, `600 ${String(11 * dpr)}px ${face}`, palette.label, "left");
    write(`${summit.elevation.toLocaleString("en-US")} m`, x + 8 * dpr, y + 7 * dpr, `500 ${String(10 * dpr)}px ${face}`, palette.label, "left");
  }
  for (const town of relief.meta.towns) {
    const [x, y] = at(town);
    ctx.beginPath();
    ctx.arc(x, y, 2.2 * dpr, 0, Math.PI * 2);
    ctx.fillStyle = palette.label;
    ctx.fill();
    write(town.name.toUpperCase(), x + 7 * dpr, y, `600 ${String(9.5 * dpr)}px ${face}`, palette.label, "left", 0.9);
  }
  // Lake Tahoe's name stands in its north basin, where the lake is widest and the window's first
  // place leaves it in the open; the small lakes are named at their seeds.
  const northBasin = LAKE_LABEL_NORTH_M / relief.meta.metresPerPixel;
  relief.meta.lakes.forEach((lake, n) => {
    const big = n === 0;
    const [x, y] = at(big ? { x: lake.x, y: lake.y - northBasin } : lake);
    write(big ? "LAKE  TAHOE" : lake.name, x, y, `italic 600 ${String((big ? 15 : 10) * dpr)}px ${face}`, palette.lakeLabel, "center", big ? 5 : 0.4);
    if (big) write(`${lake.level.toLocaleString("en-US")} m`, x, y + 20 * dpr, `italic 500 ${String(10 * dpr)}px ${face}`, palette.lakeLabel, "center", 0.6);
  });
  for (const feature of relief.meta.features) {
    const [x, y] = at(feature);
    write(feature.name, x, y, `italic 600 ${String(10 * dpr)}px ${face}`, palette.lakeLabel, "center", 0.4);
  }
  const [bx, by] = at(relief.meta.border[1] as { x: number; y: number });
  write("CALIFORNIA", bx - 14 * dpr, by + 40 * dpr, `600 ${String(9 * dpr)}px ${face}`, palette.label, "right", 2.4);
  write("NEVADA", bx + 14 * dpr, by + 40 * dpr, `600 ${String(9 * dpr)}px ${face}`, palette.label, "left", 2.4);
}
