/**
 * The one canvas every glass group on the page reads as its texture: the bench, the watch, its
 * hands, and whatever the loupe is magnifying.
 *
 * The bench and the watch's body are cached; the hands are drawn every time the scene repaints,
 * which is on each beat of the movement (eight a second), on each frame the loupe moves, and on
 * any change of layout or dial. The watch is cached at twice the canvas's resolution so the loupe
 * can draw it magnified and still sharp.
 *
 * The loupe's magnification is painted here, into the plane, not asked of the glass. The glass
 * over it is the material's own lens: it bends the edge of what it sits on, the way every surface
 * on the page does, and on the CSS tier it bends nothing at all. A loupe that magnified only on
 * one tier would be a broken loupe on the other, so the page draws the enlarged image and the
 * glass draws the optics of the edge around it (DESIGN.md, "The loupe").
 */

import { paintBench, radius } from "./bench";
import type { Circle, Layout } from "./layout";
import type { Palette } from "./palette";
import { paintHands, paintWatchBody, type HandAngles } from "./watch";

/** The loupe's power: the page enlarges what is under it by this much. */
export const LOUPE_POWER = 2;

/** The watch's painted extent in its own units (case radius 1000), shadows included. */
const WATCH_BOUNDS = { x0: -1120, x1: 1280, y0: -1260, y1: 1320 };

export interface SceneFrame {
  readonly hands: HandAngles;
  /** The local day of the month, read off the same clock as the hands, for the date wheel. */
  readonly date: number;
  /** The loupe's current circle, or null where it is not drawn (it is always drawn today). */
  readonly loupe: Circle | null;
  /**
   * Draw the loupe's edge as a fine ring, because its glass is not being drawn: the lenses step
   * aside under Reduce Transparency, forced colours and an unfocused window (DESIGN.md).
   */
  readonly loupeRing: boolean;
}

export class Scene {
  readonly canvas: HTMLCanvasElement;
  private readonly ctx: CanvasRenderingContext2D;
  private bench: HTMLCanvasElement | null = null;
  private watch: HTMLCanvasElement | null = null;
  private layout: Layout | null = null;
  private palette: Palette | null = null;
  private dpr = 1;
  /** The day of the month the cached watch body shows in its date window. */
  private watchDate = 0;

  constructor(canvas: HTMLCanvasElement) {
    this.canvas = canvas;
    const ctx = canvas.getContext("2d");
    if (ctx === null) throw new Error("The chronograph's bench needs a 2D canvas.");
    this.ctx = ctx;
  }

  /** Re-paint the caches for a new layout, dial or device scale. */
  prepare(layout: Layout, palette: Palette, dpr: number): void {
    this.layout = layout;
    this.palette = palette;
    this.dpr = dpr;
    const W = Math.round(layout.width * dpr);
    const H = Math.round(layout.height * dpr);
    if (this.canvas.width !== W || this.canvas.height !== H) {
      this.canvas.width = W;
      this.canvas.height = H;
    }

    const bench = this.bench ?? document.createElement("canvas");
    bench.width = W;
    bench.height = H;
    const b = bench.getContext("2d");
    if (b !== null) {
      b.setTransform(dpr, 0, 0, dpr, 0, 0);
      paintBench(b, layout, palette);
    }
    this.bench = bench;
    this.paintWatch(layout, palette, dpr, new Date().getDate());
  }

  /**
   * The watch body's cache, date wheel included. The date is painted into the cache, so a page
   * left open past midnight would keep yesterday's; `paint` re-paints this cache, and only this
   * one, when the day it shows is no longer the day it is.
   */
  private paintWatch(layout: Layout, palette: Palette, dpr: number, date: number): void {
    const { r } = layout.watch;
    const scale = (r / 1000) * dpr * LOUPE_POWER;
    const watch = this.watch ?? document.createElement("canvas");
    watch.width = Math.ceil((WATCH_BOUNDS.x1 - WATCH_BOUNDS.x0) * scale);
    watch.height = Math.ceil((WATCH_BOUNDS.y1 - WATCH_BOUNDS.y0) * scale);
    const w = watch.getContext("2d");
    if (w !== null) {
      w.setTransform(scale, 0, 0, scale, -WATCH_BOUNDS.x0 * scale, -WATCH_BOUNDS.y0 * scale);
      paintWatchBody(w, palette, { unitPx: scale, date });
    }
    this.watch = watch;
    this.watchDate = date;
  }

  /** Draw one frame of the scene into the visible canvas. */
  paint(frame: SceneFrame): void {
    const { layout, palette, bench, watch } = this;
    if (layout === null || palette === null || bench === null || watch === null) return;
    if (frame.date !== this.watchDate) this.paintWatch(layout, palette, this.dpr, frame.date);
    const ctx = this.ctx;
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = "high";
    ctx.drawImage(bench, 0, 0);
    ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    this.drawWatch(ctx, layout, palette, frame.hands, 1);

    const loupe = frame.loupe;
    if (loupe !== null) {
      // The loupe is held above the bench, so it throws a soft shadow down and to the right of
      // itself, the way the watch does; only the part outside the lens can be seen.
      ctx.save();
      ctx.beginPath();
      ctx.rect(0, 0, layout.width, layout.height);
      ctx.arc(loupe.cx, loupe.cy, loupe.r, 0, Math.PI * 2, true);
      ctx.clip("evenodd");
      const shadow = ctx.createRadialGradient(
        loupe.cx + loupe.r * 0.12,
        loupe.cy + loupe.r * 0.22,
        radius(loupe.r * 0.8),
        loupe.cx + loupe.r * 0.12,
        loupe.cy + loupe.r * 0.22,
        radius(loupe.r * 1.25),
      );
      shadow.addColorStop(0, palette.scheme === "dark" ? "rgb(0 0 0 / 0.55)" : "rgb(10 20 16 / 0.38)");
      shadow.addColorStop(1, "rgb(0 0 0 / 0)");
      ctx.fillStyle = shadow;
      ctx.fillRect(0, 0, layout.width, layout.height);
      ctx.restore();

      ctx.save();
      ctx.beginPath();
      ctx.arc(loupe.cx, loupe.cy, loupe.r, 0, Math.PI * 2);
      ctx.clip();
      // Everything under the loupe, again, twice the size about its centre.
      ctx.translate(loupe.cx, loupe.cy);
      ctx.scale(LOUPE_POWER, LOUPE_POWER);
      ctx.translate(-loupe.cx, -loupe.cy);
      paintBench(ctx, layout, palette);
      this.drawWatch(ctx, layout, palette, frame.hands, LOUPE_POWER);
      ctx.restore();
      if (frame.loupeRing) {
        ctx.save();
        ctx.lineWidth = 2;
        ctx.strokeStyle = palette.scheme === "dark" ? "rgb(232 238 242 / 0.8)" : "rgb(20 26 24 / 0.7)";
        ctx.beginPath();
        ctx.arc(loupe.cx, loupe.cy, loupe.r - 1, 0, Math.PI * 2);
        ctx.stroke();
        ctx.restore();
      }
    }
  }

  private drawWatch(
    ctx: CanvasRenderingContext2D,
    layout: Layout,
    palette: Palette,
    hands: HandAngles,
    magnification: number,
  ): void {
    const { cx, cy, r } = layout.watch;
    const u = r / 1000;
    if (this.watch !== null) {
      ctx.drawImage(
        this.watch,
        cx + WATCH_BOUNDS.x0 * u,
        cy + WATCH_BOUNDS.y0 * u,
        (WATCH_BOUNDS.x1 - WATCH_BOUNDS.x0) * u,
        (WATCH_BOUNDS.y1 - WATCH_BOUNDS.y0) * u,
      );
    }
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(u, u);
    paintHands(ctx, palette, { unitPx: u * this.dpr * magnification }, hands);
    ctx.restore();
  }

  /**
   * The relative luminance of what is painted under a box: the channels' encoded mean, decoded
   * once, which is how the runtime reads a texture's level and what a group's hint states.
   */
  measure(box: { x: number; y: number; width: number; height: number }): number {
    const probe = document.createElement("canvas");
    probe.width = 24;
    probe.height = 24;
    const p = probe.getContext("2d", { willReadFrequently: true });
    if (p === null) return 0.05;
    const d = this.dpr;
    p.drawImage(this.canvas, box.x * d, box.y * d, box.width * d, box.height * d, 0, 0, 24, 24);
    const data = p.getImageData(0, 0, 24, 24).data;
    const mean = [0, 0, 0];
    for (let i = 0; i < data.length; i += 4) {
      for (let c = 0; c < 3; c += 1) mean[c] = (mean[c] ?? 0) + (data[i + c] ?? 0);
    }
    const n = data.length / 4;
    const decode = (v: number): number => {
      const e = v / n / 255;
      return e <= 0.04045 ? e / 12.92 : Math.pow((e + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * decode(mean[0] ?? 0) + 0.7152 * decode(mean[1] ?? 0) + 0.0722 * decode(mean[2] ?? 0);
  }
}
