/**
 * The watch, painted: case, bezel, flange, dial, registers and hands.
 *
 * Everything here is drawn in the watch's own units, where the case's radius is 1000 and the
 * centre is the origin; the caller has already translated and scaled the context. That keeps the
 * watch one drawing at every size, and it is what lets the loupe redraw the same watch at twice
 * the scale and stay sharp. `unitPx` is how many DEVICE pixels one unit covers, because a canvas
 * shadow's blur and offset ignore the transform and have to be converted by hand.
 *
 * The crystal is not painted. It is the one glass surface over the dial, and the runtime draws it.
 */

import type { Palette } from "./palette";

const TAU = Math.PI * 2;

/** The registers: small seconds at nine, the thirty-minute counter at three, hours at six. */
export const REGISTER_OFFSET = 372;
export const REGISTER_RADIUS = 196;
export const DIAL_RADIUS = 792;
export const FLANGE_RADIUS = 866;
export const BEZEL_OUTER = 984;

const SERIF = "Didot, 'Bodoni 72', 'Iowan Old Style', Georgia, serif";
const SANS = "'Avenir Next', 'Avenir', 'Helvetica Neue', system-ui, sans-serif";
const CONDENSED = "'Avenir Next Condensed', 'DIN Condensed', 'Helvetica Neue', system-ui, sans-serif";

/** Angle in radians, clockwise from twelve, to a point at radius `r`. */
const at = (angle: number, r: number): [number, number] => [Math.sin(angle) * r, -Math.cos(angle) * r];

function mix(a: string, b: string, t: number): string {
  const pa = parseHex(a);
  const pb = parseHex(b);
  const c = pa.map((v, i) => Math.round(v + ((pb[i] ?? 0) - v) * t));
  return `rgb(${c[0]} ${c[1]} ${c[2]})`;
}

function parseHex(hex: string): number[] {
  const h = hex.replace("#", "");
  return [0, 2, 4].map((i) => parseInt(h.slice(i, i + 2), 16));
}

function ring(ctx: CanvasRenderingContext2D, outer: number, inner: number): void {
  ctx.beginPath();
  ctx.arc(0, 0, outer, 0, TAU);
  ctx.arc(0, 0, inner, 0, TAU, true);
}

/**
 * A steel surface lit from the upper left: a conic gradient whose bright lobes face the light
 * and its reflection, the way a polished or brushed round part catches one window.
 */
function steelConic(
  ctx: CanvasRenderingContext2D,
  p: Palette,
  lobes: number,
  sharpness: number,
  offset = 0,
): CanvasGradient {
  const g = ctx.createConicGradient(-Math.PI / 2 + offset, 0, 0);
  const steps = 48;
  for (let i = 0; i <= steps; i += 1) {
    const a = (i / steps) * TAU;
    const k = Math.pow(Math.abs(Math.cos((a - 5.5) * (lobes / 2))), sharpness);
    const color = k > 0.5 ? mix(p.steelMid, p.steelLight, (k - 0.5) * 2) : mix(p.steelDark, p.steelMid, k * 2);
    g.addColorStop(i / steps, color);
  }
  return g;
}

/** Text set along an arc, centred on `angle`, upright when read from outside or inside. */
function arcText(
  ctx: CanvasRenderingContext2D,
  text: string,
  radius: number,
  angle: number,
  font: string,
  color: string,
  tracking: number,
  inward: boolean,
): void {
  ctx.save();
  ctx.font = font;
  ctx.fillStyle = color;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  const widths = [...text].map((ch) => ctx.measureText(ch).width + tracking);
  const total = widths.reduce((a, b) => a + b, 0) - tracking;
  let cursor = -total / 2;
  const dir = inward ? -1 : 1;
  for (const [i, ch] of [...text].entries()) {
    const w = widths[i] ?? 0;
    const a = angle + (dir * (cursor + (w - tracking) / 2)) / radius;
    ctx.save();
    ctx.rotate(a);
    ctx.translate(0, -radius);
    if (inward) ctx.rotate(Math.PI);
    ctx.fillText(ch, 0, 0);
    ctx.restore();
    cursor += w;
  }
  ctx.restore();
}

function uprightText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  font: string,
  color: string,
  tracking = 0,
): void {
  ctx.save();
  ctx.font = font;
  ctx.fillStyle = color;
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.letterSpacing = `${tracking}px`;
  // letterSpacing trails the last glyph; centre on the glyphs, not on the spacing.
  ctx.fillText(text, x + tracking / 2, y);
  ctx.restore();
}

export interface WatchPaintOptions {
  /** Device pixels per watch unit, for shadows (they ignore the transform). */
  readonly unitPx: number;
  /** Today's date, shown in the window at half past four. */
  readonly date: number;
}

/** The strap, the lugs, the crown and pushers, the case, the bezel, the flange and the dial. */
export function paintWatchBody(ctx: CanvasRenderingContext2D, p: Palette, o: WatchPaintOptions): void {
  paintLugs(ctx, p, o);
  paintCrownAndPushers(ctx, p, o);
  paintCase(ctx, p, o);
  paintBezel(ctx, p);
  paintFlange(ctx, p);
  paintDial(ctx, p, o);
}

/** Four lugs, each a tapered horn with a polished bevel along its inner edge. */
function paintLugs(ctx: CanvasRenderingContext2D, p: Palette, o: WatchPaintOptions): void {
  for (const sy of [-1, 1]) {
    for (const sx of [-1, 1]) {
      ctx.save();
      ctx.scale(sx, sy);
      const horn = (): void => {
        ctx.beginPath();
        ctx.moveTo(440, 560);
        ctx.lineTo(452, 1130);
        ctx.quadraticCurveTo(456, 1178, 504, 1178);
        ctx.quadraticCurveTo(560, 1178, 568, 1120);
        ctx.quadraticCurveTo(606, 820, 700, 560);
        ctx.closePath();
      };
      ctx.save();
      ctx.shadowColor = p.shadow;
      ctx.shadowBlur = 40 * o.unitPx;
      ctx.shadowOffsetY = 26 * o.unitPx * sy;
      const side = ctx.createLinearGradient(440, 0, 640, 0);
      side.addColorStop(0, p.steelMid);
      side.addColorStop(0.5, p.steelDark);
      side.addColorStop(1, p.steelMid);
      ctx.fillStyle = side;
      horn();
      ctx.fill();
      ctx.restore();
      // The polished bevel: a bright band down the inner edge of the horn.
      const bevel = ctx.createLinearGradient(440, 0, 520, 0);
      bevel.addColorStop(0, p.steelLight);
      bevel.addColorStop(1, "rgb(255 255 255 / 0)");
      ctx.fillStyle = bevel;
      ctx.beginPath();
      ctx.moveTo(440, 560);
      ctx.lineTo(452, 1130);
      ctx.quadraticCurveTo(456, 1178, 504, 1178);
      ctx.lineTo(500, 560);
      ctx.closePath();
      ctx.fill();
      ctx.restore();
    }
  }
}

function paintCrownAndPushers(ctx: CanvasRenderingContext2D, p: Palette, o: WatchPaintOptions): void {
  const part = (angle: number, length: number, width: number, knurl: boolean): void => {
    ctx.save();
    ctx.rotate(angle);
    ctx.shadowColor = p.shadow;
    ctx.shadowBlur = 24 * o.unitPx;
    ctx.shadowOffsetY = 18 * o.unitPx;
    const g = ctx.createLinearGradient(0, -width / 2, 0, width / 2);
    g.addColorStop(0, p.steelLight);
    g.addColorStop(0.45, p.steelMid);
    g.addColorStop(1, p.steelDark);
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.roundRect(930, -width / 2, length, width, width * 0.22);
    ctx.fill();
    ctx.shadowColor = "transparent";
    if (knurl) {
      ctx.strokeStyle = "rgb(0 0 0 / 0.35)";
      ctx.lineWidth = 5;
      for (let y = -width / 2 + 12; y < width / 2 - 6; y += 16) {
        ctx.beginPath();
        ctx.moveTo(1000, y);
        ctx.lineTo(930 + length - 8, y);
        ctx.stroke();
      }
    }
    ctx.restore();
  };
  part(-Math.PI / 6, 150, 96, false); // two o'clock
  part(Math.PI / 6, 150, 96, false); // four o'clock
  part(0, 190, 170, true); // the crown
}

function paintCase(ctx: CanvasRenderingContext2D, p: Palette, o: WatchPaintOptions): void {
  ctx.save();
  ctx.shadowColor = p.shadow;
  ctx.shadowBlur = 70 * o.unitPx;
  ctx.shadowOffsetY = 44 * o.unitPx;
  ctx.fillStyle = steelConic(ctx, p, 2, 1.6);
  ctx.beginPath();
  ctx.arc(0, 0, 1000, 0, TAU);
  ctx.fill();
  ctx.restore();
  // The polished chamfer where the case meets the bezel.
  ctx.fillStyle = steelConic(ctx, p, 2, 6, 0.3);
  ring(ctx, 996, BEZEL_OUTER + 2);
  ctx.fill("evenodd");
}

/** The tachymeter bezel: speed over a measured kilometre, from 500 km/h at 7.2 s to 60 at 60 s. */
function paintBezel(ctx: CanvasRenderingContext2D, p: Palette): void {
  ctx.fillStyle = p.bezel;
  ring(ctx, BEZEL_OUTER, FLANGE_RADIUS);
  ctx.fill("evenodd");
  // A faint sheen on the insert, so black reads as a material and not a hole.
  const sheen = ctx.createLinearGradient(-900, -900, 900, 900);
  sheen.addColorStop(0, "rgb(255 255 255 / 0.10)");
  sheen.addColorStop(0.5, "rgb(255 255 255 / 0)");
  sheen.addColorStop(1, "rgb(255 255 255 / 0.05)");
  ctx.fillStyle = sheen;
  ring(ctx, BEZEL_OUTER, FLANGE_RADIUS);
  ctx.fill("evenodd");

  const values = [500, 400, 300, 250, 200, 180, 160, 150, 140, 130, 120, 110, 100, 90, 85, 80, 75, 70, 65, 60];
  ctx.strokeStyle = p.bezelPrint;
  for (const v of values) {
    const a = ((3600 / v) / 60) * TAU;
    const [x0, y0] = at(a, BEZEL_OUTER - 10);
    const [x1, y1] = at(a, BEZEL_OUTER - 34);
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
    if (v === 500 || v === 180 || v === 140 || v === 85 || v === 75 || v === 65) continue;
    arcText(ctx, String(v), 916, a, `600 44px ${CONDENSED}`, p.bezelPrint, 1, false);
  }
  // Fine marks between 60 and 100, every 5 km/h.
  for (let v = 100; v >= 60; v -= 5) {
    const a = ((3600 / v) / 60) * TAU;
    const [x0, y0] = at(a, BEZEL_OUTER - 10);
    const [x1, y1] = at(a, BEZEL_OUTER - 22);
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
  }
  arcText(ctx, "TACHYMETRE", 918, 0.38, `600 30px ${SANS}`, p.bezelPrint, 10, false);
}

/** The flange (rehaut): a plain steel slope between the bezel and the dial. */
function paintFlange(ctx: CanvasRenderingContext2D, p: Palette): void {
  const g = ctx.createRadialGradient(0, 0, DIAL_RADIUS, 0, 0, FLANGE_RADIUS);
  g.addColorStop(0, mix(p.flange, "#000000", 0.25));
  g.addColorStop(1, p.flange);
  ctx.fillStyle = g;
  ring(ctx, FLANGE_RADIUS, DIAL_RADIUS);
  ctx.fill("evenodd");
  ctx.fillStyle = steelConic(ctx, p, 2, 3, 0.4);
  ctx.globalAlpha = 0.35;
  ring(ctx, FLANGE_RADIUS, DIAL_RADIUS);
  ctx.fill("evenodd");
  ctx.globalAlpha = 1;
}

function paintDial(ctx: CanvasRenderingContext2D, p: Palette, o: WatchPaintOptions): void {
  ctx.save();
  ctx.beginPath();
  ctx.arc(0, 0, DIAL_RADIUS, 0, TAU);
  ctx.clip();
  paintTapisserie(ctx, p);
  // One window's light across the whole dial, and the edge falling into the flange's shadow.
  const sheen = ctx.createLinearGradient(-DIAL_RADIUS, -DIAL_RADIUS, DIAL_RADIUS * 0.6, DIAL_RADIUS);
  sheen.addColorStop(0, "rgb(255 255 255 / 0.16)");
  sheen.addColorStop(0.45, "rgb(255 255 255 / 0)");
  sheen.addColorStop(1, "rgb(0 0 0 / 0.14)");
  ctx.fillStyle = sheen;
  ctx.fillRect(-DIAL_RADIUS, -DIAL_RADIUS, DIAL_RADIUS * 2, DIAL_RADIUS * 2);
  const edge = ctx.createRadialGradient(0, 0, DIAL_RADIUS - 90, 0, 0, DIAL_RADIUS);
  edge.addColorStop(0, "rgb(0 0 0 / 0)");
  edge.addColorStop(1, "rgb(0 0 0 / 0.3)");
  ctx.fillStyle = edge;
  ctx.fillRect(-DIAL_RADIUS, -DIAL_RADIUS, DIAL_RADIUS * 2, DIAL_RADIUS * 2);
  ctx.restore();

  paintTrack(ctx, p);
  paintRegister(ctx, p, o, [-REGISTER_OFFSET, 0], 60, [20, 40, 60], "SECONDES");
  paintRegister(ctx, p, o, [REGISTER_OFFSET, 0], 30, [10, 20, 30], "MINUTES");
  paintRegister(ctx, p, o, [0, REGISTER_OFFSET], 12, [3, 6, 9, 12], "HEURES");
  paintIndices(ctx, p, o);
  paintPrint(ctx, p);
  paintDate(ctx, p, o);
}

/** The tapisserie pitch in watch units: a square grid of small pyramids, cut into the dial. */
const TAPISSERIE = 34;

/**
 * A tapisserie dial: a square grid of raised pyramids, each face catching the light from the
 * upper left at its own strength. A square grid is also the one pattern a round crystal cannot
 * hide: its lines are not radial, so wherever the crystal's lens bends them, they curve.
 */
function paintTapisserie(ctx: CanvasRenderingContext2D, p: Palette): void {
  ctx.fillStyle = p.dialGroove;
  ctx.fillRect(-DIAL_RADIUS, -DIAL_RADIUS, DIAL_RADIUS * 2, DIAL_RADIUS * 2);
  const inset = 3;
  const n = Math.ceil(DIAL_RADIUS / TAPISSERIE) + 1;
  const faces: Array<[string, (x: number, y: number, s: number) => void]> = [
    [p.dialTop, (x, y, s) => { ctx.moveTo(x, y); ctx.lineTo(x + s, y); ctx.lineTo(x + s / 2, y + s / 2); }],
    [p.dialLeft, (x, y, s) => { ctx.moveTo(x, y); ctx.lineTo(x, y + s); ctx.lineTo(x + s / 2, y + s / 2); }],
    [p.dialRight, (x, y, s) => { ctx.moveTo(x + s, y); ctx.lineTo(x + s, y + s); ctx.lineTo(x + s / 2, y + s / 2); }],
    [p.dialBottom, (x, y, s) => { ctx.moveTo(x, y + s); ctx.lineTo(x + s, y + s); ctx.lineTo(x + s / 2, y + s / 2); }],
  ];
  const size = TAPISSERIE - inset * 2;
  for (const [color, face] of faces) {
    ctx.fillStyle = color;
    ctx.beginPath();
    for (let i = -n; i < n; i += 1) {
      for (let j = -n; j < n; j += 1) {
        const x = i * TAPISSERIE + inset;
        const y = j * TAPISSERIE + inset;
        if (Math.hypot(x + size / 2, y + size / 2) > DIAL_RADIUS + TAPISSERIE) continue;
        face(x, y, size);
        ctx.closePath();
      }
    }
    ctx.fill();
  }
}

/** A railway track just inside the flange: quarter-seconds, and the five-second marks in red. */
function paintTrack(ctx: CanvasRenderingContext2D, p: Palette): void {
  const outer = DIAL_RADIUS - 26;
  const inner = DIAL_RADIUS - 58;
  ctx.fillStyle = p.trackBand;
  ring(ctx, outer + 10, inner - 30);
  ctx.fill("evenodd");
  ctx.strokeStyle = p.dialPrint;
  ctx.lineWidth = 2.2;
  for (const r of [outer, inner]) {
    ctx.beginPath();
    ctx.arc(0, 0, r, 0, TAU);
    ctx.stroke();
  }
  for (let i = 0; i < 240; i += 1) {
    const a = (i / 240) * TAU;
    const five = i % 20 === 0;
    const [x0, y0] = at(a, outer);
    const [x1, y1] = at(a, five ? inner - 22 : inner);
    ctx.strokeStyle = five ? p.dialAccent : p.dialPrint;
    ctx.lineWidth = five ? 6 : i % 4 === 0 ? 3 : 1.6;
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
  }
}

function paintRegister(
  ctx: CanvasRenderingContext2D,
  p: Palette,
  o: WatchPaintOptions,
  [x, y]: [number, number],
  count: number,
  numerals: number[],
  label: string,
): void {
  ctx.save();
  ctx.translate(x, y);
  // Recessed: a lip of shadow on the upper edge and light on the lower.
  ctx.save();
  ctx.shadowColor = "rgb(0 0 0 / 0.45)";
  ctx.shadowBlur = 10 * o.unitPx;
  ctx.shadowOffsetY = -4 * o.unitPx;
  ctx.fillStyle = p.register;
  ctx.beginPath();
  ctx.arc(0, 0, REGISTER_RADIUS, 0, TAU);
  ctx.fill();
  ctx.restore();
  // Azurage: fine concentric grooves that catch the light as rings.
  for (let r = 14; r < REGISTER_RADIUS; r += 7) {
    ctx.strokeStyle = r % 14 === 0 ? p.registerRing : "rgb(128 128 128 / 0.05)";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.arc(0, 0, r, 0, TAU);
    ctx.stroke();
  }
  const bevel = ctx.createLinearGradient(0, -REGISTER_RADIUS, 0, REGISTER_RADIUS);
  bevel.addColorStop(0, "rgb(0 0 0 / 0.35)");
  bevel.addColorStop(0.5, "rgb(0 0 0 / 0)");
  bevel.addColorStop(1, "rgb(255 255 255 / 0.25)");
  ctx.strokeStyle = bevel;
  ctx.lineWidth = 8;
  ctx.beginPath();
  ctx.arc(0, 0, REGISTER_RADIUS - 4, 0, TAU);
  ctx.stroke();

  ctx.strokeStyle = p.registerPrint;
  const ticks = count === 60 ? 60 : count === 30 ? 150 : 24;
  for (let i = 0; i < ticks; i += 1) {
    const a = (i / ticks) * TAU;
    const major = count === 60 ? i % 5 === 0 : count === 30 ? i % 5 === 0 : i % 2 === 0;
    const [x0, y0] = at(a, REGISTER_RADIUS - 14);
    const [x1, y1] = at(a, REGISTER_RADIUS - (major ? 44 : 28));
    ctx.lineWidth = major ? 5 : 2;
    ctx.beginPath();
    ctx.moveTo(x0, y0);
    ctx.lineTo(x1, y1);
    ctx.stroke();
  }
  for (const n of numerals) {
    const a = ((n % count) / count) * TAU;
    const [nx, ny] = at(a, REGISTER_RADIUS - 82);
    uprightText(ctx, String(n), nx, ny, `600 40px ${SANS}`, p.registerPrint);
  }
  uprightText(ctx, label, 0, 64, `600 18px ${SANS}`, p.registerPrint, 5);
  ctx.restore();
}

/** Applied batons, polished steel with a lume insert; twelve is doubled. */
function paintIndices(ctx: CanvasRenderingContext2D, p: Palette, o: WatchPaintOptions): void {
  for (let h = 0; h < 12; h += 1) {
    if (h === 3 || h === 6 || h === 9) continue;
    const a = (h / 12) * TAU;
    const doubled = h === 0;
    for (const dx of doubled ? [-30, 30] : [0]) {
      ctx.save();
      ctx.rotate(a);
      ctx.translate(dx, 0);
      const top = -(DIAL_RADIUS - 70);
      const length = 150;
      const w = 34;
      ctx.save();
      ctx.shadowColor = p.shadow;
      ctx.shadowBlur = 8 * o.unitPx;
      ctx.shadowOffsetX = 4 * o.unitPx;
      ctx.shadowOffsetY = 8 * o.unitPx;
      const g = ctx.createLinearGradient(-w / 2, 0, w / 2, 0);
      g.addColorStop(0, p.steelLight);
      g.addColorStop(0.5, p.steelMid);
      g.addColorStop(0.52, p.steelDark);
      g.addColorStop(1, p.steelMid);
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.roundRect(-w / 2, top, w, length, 6);
      ctx.fill();
      ctx.restore();
      paintLume(ctx, p, o, () => {
        ctx.beginPath();
        ctx.roundRect(-w / 2 + 8, top + 12, w - 16, length - 24, 4);
      });
      ctx.restore();
    }
  }
}

/** Lume: flat off-white by day, glowing at night. `shape` builds the path. */
function paintLume(ctx: CanvasRenderingContext2D, p: Palette, o: { unitPx: number }, shape: () => void): void {
  ctx.save();
  if (p.lumeGlow !== null) {
    ctx.shadowColor = p.lumeGlow;
    ctx.shadowBlur = 22 * o.unitPx;
  }
  ctx.fillStyle = p.lume;
  shape();
  ctx.fill();
  ctx.restore();
}

function paintPrint(ctx: CanvasRenderingContext2D, p: Palette): void {
  uprightText(ctx, "VITREA", 0, -452, `400 76px ${SERIF}`, p.dialPrint, 22);
  uprightText(ctx, "CHRONOGRAPHE", 0, -372, `600 25px ${SANS}`, p.dialAccent, 9);
  uprightText(ctx, "À RATTRAPANTE", 0, -336, `500 21px ${SANS}`, p.dialPrint, 7);
  uprightText(ctx, "AUTOMATIQUE", 0, 128, `500 21px ${SANS}`, p.dialPrint, 8);
  // Printed too small to read without the loupe, as the finest dial printing is.
  uprightText(ctx, "LIQUID GLASS · RENDERED, NOT PHOTOGRAPHED", 0, 612, `600 11px ${SANS}`, p.dialPrint, 2);
  uprightText(ctx, "vitrea 0.24 · WebGPU", 0, 632, `500 10px ${SANS}`, p.dialPrint, 1.6);
}

/** The date, through an aperture at half past four, turned to follow the radius. */
function paintDate(ctx: CanvasRenderingContext2D, p: Palette, o: WatchPaintOptions): void {
  ctx.save();
  ctx.rotate((4.5 / 12) * TAU);
  ctx.translate(0, -(DIAL_RADIUS - 190));
  ctx.rotate(Math.PI);
  const w = 96;
  const h = 74;
  // The frame: polished steel around a recess.
  ctx.save();
  ctx.shadowColor = p.shadow;
  ctx.shadowBlur = 6 * o.unitPx;
  ctx.shadowOffsetY = 4 * o.unitPx;
  const g = ctx.createLinearGradient(0, -h / 2 - 8, 0, h / 2 + 8);
  g.addColorStop(0, p.steelLight);
  g.addColorStop(1, p.steelDark);
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.roundRect(-w / 2 - 8, -h / 2 - 8, w + 16, h + 16, 10);
  ctx.fill();
  ctx.restore();
  ctx.fillStyle = p.dateWheel;
  ctx.beginPath();
  ctx.roundRect(-w / 2, -h / 2, w, h, 4);
  ctx.fill();
  const inner = ctx.createLinearGradient(0, -h / 2, 0, h / 2);
  inner.addColorStop(0, "rgb(0 0 0 / 0.28)");
  inner.addColorStop(0.3, "rgb(0 0 0 / 0)");
  ctx.fillStyle = inner;
  ctx.fill();
  uprightText(ctx, String(o.date), 0, 3, `600 50px ${SANS}`, p.datePrint);
  ctx.restore();
}

export interface HandAngles {
  readonly hour: number;
  readonly minute: number;
  /** The running seconds at nine. */
  readonly smallSeconds: number;
  /** The chronograph's own hands. */
  readonly chrono: number;
  readonly split: number;
  readonly chronoMinutes: number;
  readonly chronoHours: number;
}

/** The hands, in stacking order: registers, hour, minute, split, chronograph. */
export function paintHands(ctx: CanvasRenderingContext2D, p: Palette, o: { unitPx: number }, h: HandAngles): void {
  registerHand(ctx, p, o, [-REGISTER_OFFSET, 0], h.smallSeconds);
  registerHand(ctx, p, o, [REGISTER_OFFSET, 0], h.chronoMinutes);
  registerHand(ctx, p, o, [0, REGISTER_OFFSET], h.chronoHours);
  batonHand(ctx, p, o, h.hour, 470, 50, 8);
  batonHand(ctx, p, o, h.minute, 720, 38, 12);
  needle(ctx, p, o, h.split, p.split, 740, 16);
  needle(ctx, p, o, h.chrono, p.chrono, 770, 20);
  // The centre: a polished cap over the stack.
  ctx.save();
  const cap = ctx.createRadialGradient(-8, -8, 2, 0, 0, 26);
  cap.addColorStop(0, p.steelLight);
  cap.addColorStop(1, p.steelDark);
  ctx.fillStyle = cap;
  ctx.beginPath();
  ctx.arc(0, 0, 22, 0, TAU);
  ctx.fill();
  ctx.restore();
}

function withShadow(ctx: CanvasRenderingContext2D, p: Palette, o: { unitPx: number }, lift: number, draw: () => void): void {
  ctx.save();
  ctx.shadowColor = p.shadow;
  ctx.shadowBlur = lift * 1.4 * o.unitPx;
  ctx.shadowOffsetX = lift * 0.5 * o.unitPx;
  ctx.shadowOffsetY = lift * o.unitPx;
  draw();
  ctx.restore();
}

/** A faceted baton: the two halves either side of the ridge take the light differently. */
function batonHand(
  ctx: CanvasRenderingContext2D,
  p: Palette,
  o: { unitPx: number },
  angle: number,
  length: number,
  width: number,
  lift: number,
): void {
  ctx.save();
  ctx.rotate(angle);
  const half = width / 2;
  const tip = half * 0.72;
  const outline = (): void => {
    ctx.beginPath();
    ctx.moveTo(-half, 60);
    ctx.lineTo(-tip, -length + tip);
    ctx.lineTo(0, -length);
    ctx.lineTo(tip, -length + tip);
    ctx.lineTo(half, 60);
    ctx.closePath();
  };
  withShadow(ctx, p, o, lift, () => {
    ctx.fillStyle = p.steelMid;
    outline();
    ctx.fill();
  });
  // Facets: light on the left of the ridge, darker on the right.
  ctx.fillStyle = p.steelLight;
  ctx.beginPath();
  ctx.moveTo(-half, 60);
  ctx.lineTo(-tip, -length + tip);
  ctx.lineTo(0, -length);
  ctx.lineTo(0, 60);
  ctx.closePath();
  ctx.fill();
  ctx.fillStyle = p.steelDark;
  ctx.beginPath();
  ctx.moveTo(half, 60);
  ctx.lineTo(tip, -length + tip);
  ctx.lineTo(0, -length);
  ctx.lineTo(0, 60);
  ctx.closePath();
  ctx.fill();
  paintLume(ctx, p, o, () => {
    ctx.beginPath();
    ctx.roundRect(-half * 0.42, -length + 70, half * 0.84, length - 200, half * 0.4);
  });
  ctx.restore();
}

function needle(
  ctx: CanvasRenderingContext2D,
  p: Palette,
  o: { unitPx: number },
  angle: number,
  color: string,
  length: number,
  lift: number,
): void {
  ctx.save();
  ctx.rotate(angle);
  withShadow(ctx, p, o, lift, () => {
    ctx.fillStyle = color;
    ctx.beginPath();
    ctx.moveTo(-5, 190);
    ctx.lineTo(-3, -length);
    ctx.lineTo(3, -length);
    ctx.lineTo(5, 190);
    ctx.closePath();
    ctx.fill();
    // The counterweight.
    ctx.beginPath();
    ctx.arc(0, 150, 24, 0, TAU);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(0, 0, 18, 0, TAU);
    ctx.fill();
  });
  paintLume(ctx, p, o, () => {
    ctx.beginPath();
    ctx.roundRect(-9, -length + 40, 18, 60, 8);
  });
  ctx.restore();
}

function registerHand(
  ctx: CanvasRenderingContext2D,
  p: Palette,
  o: { unitPx: number },
  [x, y]: [number, number],
  angle: number,
): void {
  ctx.save();
  ctx.translate(x, y);
  ctx.rotate(angle);
  withShadow(ctx, p, o, 6, () => {
    ctx.fillStyle = p.registerHand;
    ctx.beginPath();
    ctx.moveTo(-4, 40);
    ctx.lineTo(-2.5, -REGISTER_RADIUS + 26);
    ctx.lineTo(2.5, -REGISTER_RADIUS + 26);
    ctx.lineTo(4, 40);
    ctx.closePath();
    ctx.fill();
    ctx.beginPath();
    ctx.arc(0, 0, 14, 0, TAU);
    ctx.fill();
  });
  ctx.fillStyle = p.chrono;
  ctx.beginPath();
  ctx.arc(0, 0, 6, 0, TAU);
  ctx.fill();
  ctx.restore();
}
