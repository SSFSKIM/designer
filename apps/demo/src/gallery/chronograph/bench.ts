/**
 * The bench the watch lies on: a self-healing cutting mat with its printed grid and rulers, the
 * strap running off the top and bottom of the window, and at night one desk lamp's pool of light.
 *
 * The grid is the page's refraction target. Straight printed lines are what the eye reads a lens
 * against, so wherever glass sits on the bench the grid bends at its edge; nothing here is
 * decoration laid over the glass, all of it is under it. Drawn in CSS px on a context the caller
 * has scaled for the device.
 */

import type { Layout } from "./layout";
import type { Palette } from "./palette";

const SANS = "'Avenir Next', 'Avenir', 'Helvetica Neue', system-ui, sans-serif";
const SERIF = "Didot, 'Bodoni 72', 'Iowan Old Style', Georgia, serif";

/** Grid pitch in CSS px: a minor line every 12, a major one every fifth. */
export const GRID = 12;

let grainTile: HTMLCanvasElement | null = null;

/** A small tile of rubber grain, repeated: deterministic, and cheap to scale under the loupe. */
function grain(): HTMLCanvasElement {
  if (grainTile !== null) return grainTile;
  const tile = document.createElement("canvas");
  tile.width = 128;
  tile.height = 128;
  const c = tile.getContext("2d");
  if (c === null) return tile;
  let s = 7;
  const rand = (): number => {
    s = (s * 1664525 + 1013904223) >>> 0;
    return s / 4294967296;
  };
  for (let i = 0; i < 2600; i += 1) {
    const light = rand() > 0.5;
    c.fillStyle = light ? `rgb(255 255 255 / ${0.02 + rand() * 0.04})` : `rgb(0 0 0 / ${0.03 + rand() * 0.06})`;
    c.fillRect(rand() * 128, rand() * 128, 1 + rand(), 1 + rand());
  }
  grainTile = tile;
  return tile;
}

/**
 * A gradient radius the canvas will accept. `createRadialGradient` throws on a negative radius, and
 * one bad layout number would then take the whole page down with it; a zero radius only paints the
 * gradient flat. The layouts keep the watch's radius positive, and this keeps a painter from being
 * the thing that fails if one ever does not.
 */
export const radius = (r: number): number => Math.max(0, r);

export function paintBench(ctx: CanvasRenderingContext2D, layout: Layout, p: Palette): void {
  const { width: W, height: H } = layout;
  const { cx, cy, r } = layout.watch;
  // The mat: a slow fall-off from the watch's side, so the bench has a near and a far.
  const base = ctx.createRadialGradient(cx, cy, radius(r * 0.5), cx, cy, radius(Math.hypot(W, H) * 0.75));
  base.addColorStop(0, p.mat);
  base.addColorStop(1, p.matDeep);
  ctx.fillStyle = base;
  ctx.fillRect(0, 0, W, H);
  const pattern = ctx.createPattern(grain(), "repeat");
  if (pattern !== null) {
    // The same grain reads twice as strong on the pale mat.
    ctx.globalAlpha = p.scheme === "light" ? 0.45 : 1;
    ctx.fillStyle = pattern;
    ctx.fillRect(0, 0, W, H);
    ctx.globalAlpha = 1;
  }

  paintGrid(ctx, W, H, p);
  paintRulers(ctx, W, H, p);
  paintPrinting(ctx, layout, p);

  if (p.lamp !== null) {
    const lamp = ctx.createRadialGradient(cx - r * 0.35, cy - r * 0.45, radius(r * 0.2), cx, cy, radius(r * 2.3));
    lamp.addColorStop(0, p.lamp);
    lamp.addColorStop(1, "rgb(255 214 160 / 0)");
    ctx.fillStyle = lamp;
    ctx.fillRect(0, 0, W, H);
  }

  // The strap, in the watch's own units: from the lugs to beyond the window's edge. Without it,
  // the two spring bars the strap would hang from.
  ctx.save();
  ctx.translate(cx, cy);
  ctx.scale(r / 1000, r / 1000);
  if (layout.strap) {
    const reach = ((Math.max(cy, H - cy) + 40) / r) * 1000;
    paintStrap(ctx, p, -reach, -700);
    paintStrap(ctx, p, 700, reach);
  } else {
    for (const sy of [-1, 1]) {
      const bar = ctx.createLinearGradient(0, sy * 1062, 0, sy * 1098);
      bar.addColorStop(0, p.steelLight);
      bar.addColorStop(1, p.steelDark);
      ctx.fillStyle = bar;
      ctx.beginPath();
      ctx.roundRect(-470, sy * 1080 - 16, 940, 32, 16);
      ctx.fill();
    }
  }
  ctx.restore();
}

function paintGrid(ctx: CanvasRenderingContext2D, W: number, H: number, p: Palette): void {
  for (const major of [false, true]) {
    ctx.strokeStyle = major ? p.gridMajor : p.gridMinor;
    ctx.lineWidth = major ? 1.2 : 0.7;
    ctx.beginPath();
    for (let x = 0, i = 0; x <= W; x += GRID, i += 1) {
      if ((i % 5 === 0) !== major) continue;
      ctx.moveTo(x + 0.5, 0);
      ctx.lineTo(x + 0.5, H);
    }
    for (let y = 0, i = 0; y <= H; y += GRID, i += 1) {
      if ((i % 5 === 0) !== major) continue;
      ctx.moveTo(0, y + 0.5);
      ctx.lineTo(W, y + 0.5);
    }
    ctx.stroke();
  }
}

/** Millimetre rules along the left and bottom edges, numbered every major line. */
function paintRulers(ctx: CanvasRenderingContext2D, W: number, H: number, p: Palette): void {
  ctx.strokeStyle = p.print;
  ctx.fillStyle = p.print;
  ctx.font = `600 9px ${SANS}`;
  ctx.textBaseline = "middle";
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let y = GRID * 2, i = 2; y < H - GRID; y += GRID / 2, i += 1) {
    const length = i % 10 === 0 ? 14 : i % 2 === 0 ? 9 : 5;
    ctx.moveTo(0, Math.round(y) + 0.5);
    ctx.lineTo(length, Math.round(y) + 0.5);
  }
  for (let x = GRID * 2, i = 2; x < W - GRID; x += GRID / 2, i += 1) {
    const length = i % 10 === 0 ? 14 : i % 2 === 0 ? 9 : 5;
    ctx.moveTo(Math.round(x) + 0.5, H);
    ctx.lineTo(Math.round(x) + 0.5, H - length);
  }
  ctx.stroke();
  ctx.textAlign = "left";
  for (let y = GRID * 5, n = 1; y < H - GRID * 2; y += GRID * 5, n += 1) ctx.fillText(String(n), 17, y);
  ctx.textAlign = "center";
  for (let x = GRID * 5, n = 1; x < W - GRID * 2; x += GRID * 5, n += 1) ctx.fillText(String(n), x, H - 21);
}

/**
 * How far the watch's horns reach out from the case's centre, in case radii (640 of the case's
 * 1000 units, with the edge of their shadow). Printing beside the watch keeps left of this.
 */
const LUG_REACH = 0.64;

/** The smallest title the mat prints. Below it the subtitle is under 7 px, and none reads better. */
const MIN_TITLE = 16;

const SUBTITLE = "CHRONOGRAPHE À RATTRAPANTE";
const FOOT = "ATELIER BENCH No. 7 · 12 PX GRID";

/**
 * The maker's name on the mat, the loupe's place, and the mat's own printing along its foot.
 *
 * On the wide layout all three are printed on the mat left of the watch, and the room there
 * shrinks with the window faster than the title does, so each is printed only where it clears
 * the watch. The title shrinks to the room beside the upper horn, measured in the font that
 * draws it, and is left off below a legible size; the foot line is left off where it would run
 * under the lower horn; and the loupe's place is printed only where the loupe rests on the mat,
 * not where a short window starts it on the dial.
 */
function paintPrinting(ctx: CanvasRenderingContext2D, layout: Layout, p: Palette): void {
  const { x } = layout.title;
  const { cx, cy, r } = layout.watch;
  const clear = cx - r * LUG_REACH - 12;
  ctx.textAlign = "left";
  ctx.textBaseline = "alphabetic";

  let size = layout.title.size;
  if (size > 0 && layout.mode === "wide") {
    ctx.font = `600 ${size * 0.42}px ${SANS}`;
    ctx.letterSpacing = `${size * 0.12}px`;
    const fitted = size * Math.min(1, (clear - (x + 24)) / ctx.measureText(SUBTITLE).width);
    size = fitted >= MIN_TITLE ? fitted : 0;
  }
  if (size > 0) {
    // The layout's title origin is for its own size; a fitted title keeps the same top.
    const y = layout.title.y - (layout.title.size - size) * 0.8;
    ctx.fillStyle = p.print;
    ctx.font = `400 ${size * 1.5}px ${SERIF}`;
    ctx.letterSpacing = `${size * 0.32}px`;
    ctx.fillText("VITREA", x + 22, y + size * 0.6);
    ctx.letterSpacing = `${size * 0.12}px`;
    ctx.font = `600 ${size * 0.42}px ${SANS}`;
    ctx.fillStyle = p.printSoft;
    ctx.fillText(SUBTITLE, x + 24, y + size * 1.45);
  }
  ctx.letterSpacing = "0px";
  if (layout.mode !== "wide") return;

  ctx.font = `600 9px ${SANS}`;
  ctx.fillStyle = p.printSoft;
  // The loupe's place on the mat, printed the way a bench marks where a tool lives.
  const rest = layout.loupeRest;
  if (Math.hypot(rest.cx - cx, rest.cy - cy) > r + rest.r) {
    ctx.letterSpacing = "2.5px";
    ctx.textAlign = "center";
    ctx.fillText("LOUPE · 2×", rest.cx, rest.cy - rest.r - 14);
    ctx.textAlign = "left";
  }
  ctx.letterSpacing = "2px";
  if (x + 24 + ctx.measureText(FOOT).width <= clear) ctx.fillText(FOOT, x + 24, layout.height - 36);
  ctx.letterSpacing = "0px";
}

/** One half of the strap: calf, with its edge paint and a saddle stitch down both sides. */
function paintStrap(ctx: CanvasRenderingContext2D, p: Palette, y0: number, y1: number): void {
  const half = 430;
  ctx.save();
  const body = ctx.createLinearGradient(-half, 0, half, 0);
  body.addColorStop(0, p.strapEdge);
  body.addColorStop(0.08, p.strap);
  body.addColorStop(0.5, p.strap);
  body.addColorStop(0.92, p.strap);
  body.addColorStop(1, p.strapEdge);
  ctx.save();
  ctx.shadowColor = p.shadow;
  ctx.shadowBlur = 30;
  ctx.shadowOffsetY = 10;
  ctx.fillStyle = body;
  ctx.fillRect(-half, y0, half * 2, y1 - y0);
  ctx.restore();
  // A soft crown down the middle where the leather is padded.
  const pad = ctx.createLinearGradient(-half, 0, half, 0);
  pad.addColorStop(0.2, "rgb(255 255 255 / 0)");
  pad.addColorStop(0.5, "rgb(255 255 255 / 0.07)");
  pad.addColorStop(0.8, "rgb(255 255 255 / 0)");
  ctx.fillStyle = pad;
  ctx.fillRect(-half, y0, half * 2, y1 - y0);
  ctx.strokeStyle = p.stitch;
  ctx.lineWidth = 7;
  ctx.setLineDash([26, 16]);
  for (const x of [-half + 44, half - 44]) {
    ctx.beginPath();
    ctx.moveTo(x, y0);
    ctx.lineTo(x, y1);
    ctx.stroke();
  }
  ctx.setLineDash([]);
  ctx.restore();
}
