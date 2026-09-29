/**
 * # The CSS tier's backdrop reading (W7)
 *
 * Backdrop tone adaptation needs to know what is behind a surface. The GPU tier
 * knows exactly — it is sampling those pixels to refract them, so the shader
 * reads the adaptation per pixel off the same value the tint tone map reads.
 * This tier has no pixels at all: a CSS declaration is one colour, written
 * before anything composites, and there is no primitive that makes an `rgba()`
 * overlay depend on what it lands on.
 *
 * So it asks the app, in the order the app's own statements deserve:
 *
 * 1. **X6's declared hint** (`hintedBackdropLuminance`). An explicit statement
 *    beats a measurement, which is core's own rule for `resolveBackdropHint`.
 *    A hint carries a luminance and not a colour, so the adaptation it drives is
 *    achromatic — the material takes the backdrop's *tone*, not its hue.
 * 2. **The backdrop source the app already handed over.** A texture-configured
 *    source is real pixels, supplied through `setBackdropTexture` because the GPU
 *    tier needs them; when the CSS tier is the one drawing, the same pixels
 *    answer the same question. This is the function below: one downsampled read,
 *    averaged in encoded space and decoded once (the W9 model — see the
 *    referee section), giving a colour as well as a level.
 * 3. **Nothing.** No hint, no readable source — then this tier does not adapt,
 *    which is exactly what it did before this axis existed. Guessing a level
 *    would be the one failure mode that matters: `CSS_TIER_MAPPING`'s
 *    `referenceBackdropLuminance` is 0.02 and is *not* a typical backdrop (it is
 *    a fitted conversion constant), so a fallback to it would dissolve every
 *    untinted surface on the page into its own background.
 *
 * ## The profile-gated silhouette reading (W28)
 *
 * The account below describes the legacy source branch, which remains unchanged
 * when the profile omits `backdropToneAbscissa` or names `source`. A silhouette
 * profile reads the raw native-resolution raster under each measured rounded
 * host instead. It averages encoded Rec709 luma and decodes that scalar once;
 * its local linear RGB mean also replaces the source reference throughout the
 * CSS solve. The input readout records the actual region mean, not a fitted
 * response or a downsampled proxy for it (W28 Decision Logs 1 amendment and 2).
 *
 * ## What the legacy source reading is coarse about, and why
 *
 * One number per **source**, not per surface: a surface sitting over a dark
 * corner of a bright backdrop reads the backdrop's mean here and its own
 * neighbourhood on the GPU tier. Making it per-surface would mean restating the
 * renderer's cover-fit mapping in this package — a second copy of a quantity the
 * two tiers must agree on exactly — to buy locality on the tier that is the
 * fallback. The cross-tier bound is the referee, and it is enforced from the
 * matrix on every gated cell.
 *
 * ### The referee ruled, and W9's probe answered it (2026-09-02)
 *
 * The 2026-09-01 reading of the failure blamed this tier's coarseness: one
 * number per source, averaged and then mapped, widest where the backdrop is
 * most bimodal (`checkerboard` + tint diverged 1.638 against a 0.8…1.25
 * cross-tier bound). That reading was half right. W9's reference probe
 * (claims §5.31, seven attested runs over a pitch and contrast sweep) found
 * the averaging is not the sin — the SPACE is. The reference's tone response
 * behaves as if the backdrop were averaged in its ENCODED form and the
 * material's response applied to that; averaging in linear light — which this
 * file did deliberately, and documented as correctness — was the
 * approximation. An equal-linear-mean pair of checkerboards, indistinguishable
 * to any linear reading, renders 0.11–0.19 apart on the reference, and the
 * encoded-space mean predicts both the direction and most of the magnitude.
 *
 * So the tone LEVEL below is taken in encoded space and decoded once at the
 * end (Decision Log 2 of the W9 spec), while the tone COLOUR stays the linear
 * mean — the two consumers read different physics, and the canonical impulse
 * cell measured the difference when the colour briefly followed the level
 * (see the loop comment). What remains of the old caveat is granularity: this
 * is still one number per source rather than per surface, the probe measured
 * the reference reading per-footprint, and the cross-tier bound is still the
 * referee, enforced from the matrix on every gated cell.
 *
 * The read is a `drawImage` downsample. The browser averages in the texture's
 * own encoded space — which under the W9 model is no longer a trap to outrun
 * but the model itself. `SAMPLE_EXTENT`'s history and what its size still
 * buys are on the constant.
 */

import type { Rect } from "@vitreajs/vitrea";
import type { GlassBackdropTexture } from "./renderer-bridge";

/**
 * A backdrop's tone reading, in the W9 model's two spaces (claims §5.31–§5.34).
 * A solid backdrop is identical under both, which is why every solid-fitted
 * constant survived the convention work unchanged.
 */
export interface BackdropToneSample {
  /** The actual encoded Rec709 input, present for the silhouette branch. */
  readonly encodedLuminance?: number;
  /** Native source dimensions and the number of covered device-pixel centres. */
  readonly footprint?: {
    readonly sampleCount: number;
    readonly sourceWidth: number;
    readonly sourceHeight: number;
  };
  /** The LINEAR-space mean colour — the physical average light, what the
   * collapse converges onto. */
  readonly rgb: readonly [number, number, number];
  /** The ENCODED-space mean's level, decoded once — the tone input the
   * reference's response tracks; feeds the collapse band and the response
   * curve. */
  readonly luminance: number;
  /**
   * The linear mean's luminance — `rgb`'s own, kept as a named scalar so a
   * per-pixel consumer (the GPU tier's tint tone map) can express how far the
   * model input sits from the linear mean its samples average to, as one ratio.
   */
  readonly linearLuminance: number;
}

/**
 * The longest edge the backdrop is drawn at before it is averaged.
 *
 * This constant's history is a lesson in conventions. It was set to 512 by a
 * measured trap: under the original linear-mean convention, `drawImage`'s
 * encoded-space downsampling made a 32 px read of the impulse backdrop report
 * 0.0008 against a true linear 0.0039, and a capsule rendered five times too
 * dark. W9 then measured the reference itself (claims §5.31) and found its
 * tone input behaves as an ENCODED-space mean — the very averaging the trap
 * story treated as the error. Under the current convention the browser's
 * downsample and this function's accumulation happen in the same space, the
 * composition of the two box filters is exact up to rounding, and the extent
 * no longer guards correctness at all.
 *
 * It stays at 512 for provenance continuity — every committed capture read at
 * this extent — and lowering it is now a pure readback-cost optimisation
 * (1 MB at the cap, once per declared content change) to be taken
 * deliberately, with the e2e pins re-verified, not as a drive-by.
 */
export const SAMPLE_EXTENT = 512;

/**
 * The shortest interval between two readings of one source.
 *
 * A canvas or video backdrop re-marks itself dirty every frame, and this axis is
 * about a quantity that moves slowly — the backdrop's *tone*. Reading it per
 * frame would spend a page-sized `getImageData` on a number that had not changed,
 * and would let a noisy backdrop jitter the material. The GPU tier's own analysis
 * readback makes the same judgement about the same quantity, with a 500 ms low
 * pass and a capped cadence; this is the CSS tier's version of it.
 *
 * A source's FIRST reading is never delayed by this. A surface that painted
 * unadapted and changed its mind a quarter of a second later would be worse than
 * either state.
 */
export const BACKDROP_TONE_CADENCE_MS = 250;

let scratch: { canvas: OffscreenCanvas | HTMLCanvasElement; ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D } | undefined;

function scratchSurface():
  | { canvas: OffscreenCanvas | HTMLCanvasElement; ctx: CanvasRenderingContext2D | OffscreenCanvasRenderingContext2D }
  | undefined {
  if (scratch !== undefined) return scratch;
  if (typeof document === "undefined" && typeof OffscreenCanvas === "undefined") return undefined;
  const canvas =
    typeof OffscreenCanvas === "undefined"
      ? Object.assign(document.createElement("canvas"), {
          width: SAMPLE_EXTENT,
          height: SAMPLE_EXTENT,
        })
      : new OffscreenCanvas(SAMPLE_EXTENT, SAMPLE_EXTENT);
  // `willReadFrequently` is the whole access pattern: one draw, one read, per
  // content change. Without it a compositor-backed canvas pays a GPU round trip
  // on every `getImageData`.
  const ctx = canvas.getContext("2d", { willReadFrequently: true }) as
    | CanvasRenderingContext2D
    | OffscreenCanvasRenderingContext2D
    | null;
  if (ctx === null) return undefined;
  scratch = { canvas, ctx };
  return scratch;
}

function srgbDecode(encoded: number): number {
  const clamped = Math.min(1, Math.max(0, encoded));
  return clamped <= 0.04045 ? clamped / 12.92 : Math.pow((clamped + 0.055) / 1.055, 2.4);
}

/**
 * `srgbDecode(byte / 255)` for every byte, computed by that same function.
 *
 * Every per-pixel decode below starts from an 8-bit channel, so a table indexed
 * by the byte returns the very number the call would have — bit for bit, not an
 * approximation of it — without a `Math.pow` per channel per tap. On a
 * page-sized read that call was most of the reduction's cost.
 */
const SRGB_DECODE_BYTE: Float64Array = (() => {
  const table = new Float64Array(256);
  for (let byte = 0; byte < 256; byte += 1) table[byte] = srgbDecode(byte / 255);
  return table;
})();

/**
 * The average colour of a supplied backdrop texture, in linear light — or
 * `undefined` where there is nothing readable yet.
 *
 * Returns `undefined` rather than a guess for every reason a read can fail: an
 * image that has not decoded, a canvas with no backing store, a video with no
 * frame, a cross-origin source that taints the scratch canvas (the throw is
 * caught, because a `SecurityError` here is an app's CORS configuration and not a
 * bug this library can fix — and a surface that does not adapt is the correct
 * behaviour for a backdrop nobody is allowed to look at).
 */
export function sampleBackdropTone(
  texture: GlassBackdropTexture | undefined,
  silhouette?: BackdropSilhouette,
): BackdropToneSample | undefined {
  if (texture === undefined) return undefined;
  const surface = scratchSurface();
  if (surface === undefined) return undefined;

  const drawable = drawableOf(texture);
  if (drawable === undefined) return undefined;

  if (silhouette !== undefined) {
    try {
      // The silhouette is a native-resolution reading, not the legacy capped
      // source statistic. Resizing also clears any previous tainted canvas.
      surface.canvas.width = drawable.width;
      surface.canvas.height = drawable.height;
      surface.ctx.drawImage(drawable.source, 0, 0);
      return silhouetteBackdropTone(
        surface.ctx.getImageData(0, 0, drawable.width, drawable.height).data,
        drawable.width, drawable.height, silhouette,
      );
    } catch {
      return undefined;
    }
  }
  if (surface.canvas.width !== SAMPLE_EXTENT || surface.canvas.height !== SAMPLE_EXTENT) {
    surface.canvas.width = SAMPLE_EXTENT;
    surface.canvas.height = SAMPLE_EXTENT;
  }

  // Aspect preserved and capped, so the source is drawn at or below 1:1 rather
  // than squashed into a square — a squashed draw averages across the wrong axis
  // and, at 1:1, is not a downsample at all.
  const scale = Math.min(1, SAMPLE_EXTENT / Math.max(drawable.width, drawable.height));
  const width = Math.max(1, Math.round(drawable.width * scale));
  const height = Math.max(1, Math.round(drawable.height * scale));

  try {
    surface.ctx.clearRect(0, 0, SAMPLE_EXTENT, SAMPLE_EXTENT);
    surface.ctx.drawImage(drawable.source, 0, 0, width, height);
    const data = surface.ctx.getImageData(0, 0, width, height).data;
    let r = 0;
    let g = 0;
    let b = 0;
    let er = 0;
    let eg = 0;
    let eb = 0;
    let weight = 0;
    for (let i = 0; i < data.length; i += 4) {
      // Alpha-weighted: a backdrop source with transparent regions has not
      // declared a colour there, and counting those texels as black would report
      // a dark backdrop for a page that has none.
      const a = (data[i + 3] as number) / 255;
      if (a <= 0) continue;
      // TWO means, one pass, because the two consumers read different physics
      // (W9, claims §5.31–§5.34). The tone LEVEL is the ENCODED-space mean,
      // decoded once — the reference's tone response tracks it (the equal-mean
      // pair is the proof: identical linear means, 0.11–0.19 apart on the
      // reference). The tone COLOUR is the LINEAR mean — the physical average
      // light the collapse converges onto; converging onto the encoded reading
      // instead was a measured ΔE p95 0.03 → 0.12 regression on the impulse
      // grid, whose two means differ 2.6×.
      const pr = (data[i] as number) / 255;
      const pg = (data[i + 1] as number) / 255;
      const pb = (data[i + 2] as number) / 255;
      er += pr * a;
      eg += pg * a;
      eb += pb * a;
      r += (SRGB_DECODE_BYTE[data[i] as number] as number) * a;
      g += (SRGB_DECODE_BYTE[data[i + 1] as number] as number) * a;
      b += (SRGB_DECODE_BYTE[data[i + 2] as number] as number) * a;
      weight += a;
    }
    if (weight <= 0) return undefined;
    const rgb: readonly [number, number, number] = [r / weight, g / weight, b / weight];
    const level: readonly [number, number, number] = [
      srgbDecode(er / weight),
      srgbDecode(eg / weight),
      srgbDecode(eb / weight),
    ];
    return {
      rgb,
      luminance: 0.2126 * level[0] + 0.7152 * level[1] + 0.0722 * level[2],
      linearLuminance: 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2],
    };
  } catch {
    return undefined;
  }
}

/**
 * How a source's pixels can change, which decides when a held reading of them
 * stops describing them.
 *
 * - `static` — a decoded image. It changes only when the app hands over another
 *   texture or marks it, so the dirty epoch is a complete account of it and a
 *   new epoch is read at once.
 * - `marked` — content the app draws and declares: a canvas supplied with
 *   `live: false`, or a video that is not playing. A new epoch is read, but no
 *   more often than `BACKDROP_TONE_CADENCE_MS`, because an app that repaints on
 *   every frame of a playing lesson marks on every frame too.
 * - `live` — content that may change on any frame without saying so: a canvas
 *   supplied live, a playing video. Re-read on the cadence whatever the epoch.
 */
export type BackdropSourceLiveness = "static" | "marked" | "live";

/**
 * Whether a reading taken at `held` must be taken again now, and — where it
 * must not yet, but the pixels may already have moved on — when it will be due.
 *
 * `retryAtMs` is what lets a host that draws on demand stop between readings: a
 * mark that lands inside the cadence would otherwise be read only if something
 * else happened to draw a frame after the cadence ran out, and on an idle page
 * nothing does.
 */
export function backdropReadingDue(
  liveness: BackdropSourceLiveness,
  held: { readonly epoch: number; readonly atMs: number },
  epoch: number,
  now: number,
): { readonly due: boolean; readonly retryAtMs?: number } {
  const changed = held.epoch !== epoch;
  if (liveness === "static") return { due: changed };
  if (liveness === "marked" && !changed) return { due: false };
  if (now - held.atMs >= BACKDROP_TONE_CADENCE_MS) return { due: true };
  return { due: false, retryAtMs: held.atMs + BACKDROP_TONE_CADENCE_MS };
}

/**
 * A rectangle of source pixels, in the source's intrinsic px: `x`/`y` inclusive,
 * `width`/`height` the extent.
 */
export interface SourceWindow {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

/**
 * A native-resolution read of the part of a source the surfaces sample.
 *
 * `width` and `height` are the source's FULL intrinsic extent — the placement
 * maps through it — and `window` says which of those pixels `data` holds. The
 * read used to be the whole source: a 2880×1800 board canvas, drawn and read
 * back in full four times a second for a toolbar a few hundred pixels wide.
 */
export interface BackdropSnapshot {
  readonly data: Uint8ClampedArray;
  readonly width: number;
  readonly height: number;
  readonly window: SourceWindow;
}

/**
 * Holds one source read across all silhouettes. Geometry changes only repeat the
 * reduction while the held pixels still cover it; source replacement, intrinsic
 * resizing and a reading falling due (`backdropReadingDue`) take new ones. A
 * surface reaching past the held window grows it — one more read, of the union.
 *
 * `region` is what to read when a read is taken, in the silhouette's own CSS
 * space: the caller passes every surface sampling this source, padded, so one
 * read serves them all and a surface that moves a little (a scroll, a morph)
 * keeps reducing the pixels already held.
 */
export function createBackdropSnapshotReader(): (
  texture: GlassBackdropTexture,
  epoch: number,
  now: number,
  liveness: BackdropSourceLiveness,
  silhouette: BackdropSilhouette,
  region: Rect,
) => { readonly snapshot: BackdropSnapshot | undefined; readonly retryAtMs?: number } {
  let held: {
    texture: GlassBackdropTexture; epoch: number; atMs: number;
    width: number; height: number; window: SourceWindow | undefined;
    snapshot: BackdropSnapshot | undefined;
  } | undefined;
  return (texture, epoch, now, liveness, silhouette, region) => {
    const drawable = drawableOf(texture);
    const width = drawable?.width ?? 0;
    const height = drawable?.height ?? 0;
    const needed = drawable === undefined ? undefined : silhouetteSourceWindow(width, height, silhouette);

    let grow: SourceWindow | undefined;
    let retryAtMs: number | undefined;
    if (held !== undefined && held.texture === texture && held.width === width &&
        held.height === height) {
      const reading = backdropReadingDue(liveness, held, epoch, now);
      if (!reading.due) {
        retryAtMs = reading.retryAtMs;
        if (needed === undefined || (held.window !== undefined && containsWindow(held.window, needed))) {
          return { snapshot: held.snapshot, ...(retryAtMs === undefined ? {} : { retryAtMs }) };
        }
        grow = held.window;
      }
    }

    const regional = drawable === undefined
      ? undefined : silhouetteSourceWindow(width, height, { ...silhouette, bounds: region });
    const window = needed === undefined ? undefined
      : unionWindow(regional === undefined ? needed : unionWindow(regional, needed), grow);
    let snapshot: BackdropSnapshot | undefined;
    const surface = drawable === undefined || window === undefined ? undefined : scratchSurface();
    if (surface !== undefined && drawable !== undefined && window !== undefined) {
      try {
        // Resizing clears any taint left by an earlier source. The window is
        // copied at 1:1 and integer offsets, so its pixels are the very bytes a
        // whole-source draw would have put at the same place.
        surface.canvas.width = window.width;
        surface.canvas.height = window.height;
        surface.ctx.drawImage(
          drawable.source,
          window.x, window.y, window.width, window.height,
          0, 0, window.width, window.height,
        );
        snapshot = {
          data: surface.ctx.getImageData(0, 0, window.width, window.height).data,
          width, height, window,
        };
      } catch {
        snapshot = undefined;
      }
    }
    held = { texture, epoch, atMs: now, width, height, window, snapshot };
    return { snapshot, ...(retryAtMs === undefined ? {} : { retryAtMs }) };
  };
}

const containsWindow = (outer: SourceWindow, inner: SourceWindow): boolean =>
  inner.x >= outer.x && inner.y >= outer.y &&
  inner.x + inner.width <= outer.x + outer.width &&
  inner.y + inner.height <= outer.y + outer.height;

const unionWindow = (a: SourceWindow, b: SourceWindow | undefined): SourceWindow => {
  if (b === undefined) return a;
  const x = Math.min(a.x, b.x);
  const y = Math.min(a.y, b.y);
  return {
    x, y,
    width: Math.max(a.x + a.width, b.x + b.width) - x,
    height: Math.max(a.y + a.height, b.y + b.height) - y,
  };
};

/** The batched host and source geometry, all in viewport-relative CSS pixels. */
export interface BackdropSilhouette {
  readonly bounds: Rect;
  readonly radius: number;
  readonly viewport: {
    readonly width: number;
    readonly height: number;
    readonly devicePixelRatio: number;
  };
  readonly placement?: Rect;
}

/**
 * The device-pixel lattice a silhouette is sampled on, and the map from it into
 * source px — shared by the reduction and by the window that says which source
 * pixels the reduction will touch, so the two cannot disagree by a rounding.
 * `undefined` where the silhouette samples nothing.
 */
function silhouetteLattice(width: number, height: number, geometry: BackdropSilhouette): {
  readonly dpr: number;
  readonly startX: number;
  readonly endX: number;
  readonly startY: number;
  readonly endY: number;
  sourceX(px: number): number;
  sourceY(py: number): number;
} | undefined {
  const { bounds, viewport } = geometry;
  const dpr = viewport.devicePixelRatio;
  if (width <= 0 || height <= 0 || bounds.width <= 0 || bounds.height <= 0 ||
      viewport.width <= 0 || viewport.height <= 0 || dpr <= 0) return undefined;
  let placement = geometry.placement;
  if (placement === undefined || !Number.isFinite(placement.x) ||
      !Number.isFinite(placement.y) || placement.width <= 0 || placement.height <= 0) {
    // This is the renderer's centred cover fit, expressed as a CSS rectangle.
    const scale = Math.max(viewport.width / width, viewport.height / height);
    placement = {
      x: (viewport.width - width * scale) / 2,
      y: (viewport.height - height * scale) / 2,
      width: width * scale, height: height * scale,
    };
  }
  const place = placement;
  return {
    dpr,
    startX: Math.max(0, Math.floor(bounds.x * dpr)),
    endX: Math.min(Math.ceil(viewport.width * dpr), Math.ceil((bounds.x + bounds.width) * dpr)),
    startY: Math.max(0, Math.floor(bounds.y * dpr)),
    endY: Math.min(Math.ceil(viewport.height * dpr), Math.ceil((bounds.y + bounds.height) * dpr)),
    sourceX: (px) => Math.max(0, Math.min(width - 1, (px - place.x) / place.width * width - 0.5)),
    sourceY: (py) => Math.max(0, Math.min(height - 1, (py - place.y) / place.height * height - 0.5)),
  };
}

/**
 * The source pixels `silhouetteBackdropTone` can read for this geometry: every
 * bilinear tap of every device-pixel centre in the silhouette's bounds. The map
 * into source px is monotonic, so the first and last centres bound the taps; the
 * rounded corners only ever read fewer. `undefined` where nothing is sampled.
 */
export function silhouetteSourceWindow(
  width: number,
  height: number,
  geometry: BackdropSilhouette,
): SourceWindow | undefined {
  const lattice = silhouetteLattice(width, height, geometry);
  if (lattice === undefined) return undefined;
  const { dpr, startX, endX, startY, endY } = lattice;
  if (startX >= endX || startY >= endY) return undefined;
  const x0 = Math.floor(lattice.sourceX((startX + 0.5) / dpr));
  const x1 = Math.min(width - 1, Math.floor(lattice.sourceX((endX - 1 + 0.5) / dpr)) + 1);
  const y0 = Math.floor(lattice.sourceY((startY + 0.5) / dpr));
  const y1 = Math.min(height - 1, Math.floor(lattice.sourceY((endY - 1 + 0.5) / dpr)) + 1);
  return { x: x0, y: y0, width: x1 - x0 + 1, height: y1 - y0 + 1 };
}

/**
 * Reads encoded Rec709 luma under a rounded rectangle at device-pixel centres
 * (W28 Decision Log 2). The source stays at native resolution; sampling is
 * bilinear with edge clamping, using the renderer's placement/cover convention.
 * The level is decoded once after averaging; colour remains a linear mean.
 *
 * `data` holds `window` of the source (the whole source when absent); the
 * window must cover `silhouetteSourceWindow` for the same geometry.
 */
export function silhouetteBackdropTone(
  data: Uint8ClampedArray,
  width: number,
  height: number,
  geometry: BackdropSilhouette,
  window?: SourceWindow,
): BackdropToneSample | undefined {
  const lattice = silhouetteLattice(width, height, geometry);
  if (lattice === undefined) return undefined;
  const { bounds } = geometry;
  const { dpr, startX, endX, startY, endY } = lattice;
  const originX = window?.x ?? 0;
  const originY = window?.y ?? 0;
  const stride = window?.width ?? width;
  const radius = Math.max(0, Math.min(geometry.radius, bounds.width / 2, bounds.height / 2));
  const cx = bounds.x + bounds.width / 2;
  const cy = bounds.y + bounds.height / 2;
  let encoded = 0;
  let r = 0;
  let g = 0;
  let b = 0;
  let weight = 0;
  let sampleCount = 0;
  for (let y = startY; y < endY; y += 1) {
    const py = (y + 0.5) / dpr;
    for (let x = startX; x < endX; x += 1) {
      const px = (x + 0.5) / dpr;
      const qx = Math.abs(px - cx) - bounds.width / 2 + radius;
      const qy = Math.abs(py - cy) - bounds.height / 2 + radius;
      const distance = Math.hypot(Math.max(qx, 0), Math.max(qy, 0)) +
        Math.min(Math.max(qx, qy), 0) - radius;
      if (distance > 0) continue;
      sampleCount += 1;
      const sx = lattice.sourceX(px);
      const sy = lattice.sourceY(py);
      const x0 = Math.floor(sx);
      const y0 = Math.floor(sy);
      const fx = sx - x0;
      const fy = sy - y0;
      // Alpha weights declared pixels rather than inventing black where a
      // transparent source has supplied no backdrop colour.
      for (let dy = 0; dy <= 1; dy += 1) {
        for (let dx = 0; dx <= 1; dx += 1) {
          const i = ((Math.min(height - 1, y0 + dy) - originY) * stride +
            Math.min(width - 1, x0 + dx) - originX) * 4;
          const a = (data[i + 3] as number) / 255 *
            (dx === 0 ? 1 - fx : fx) * (dy === 0 ? 1 - fy : fy);
          if (a <= 0) continue;
          const pr = (data[i] as number) / 255;
          const pg = (data[i + 1] as number) / 255;
          const pb = (data[i + 2] as number) / 255;
          encoded += (0.2126 * pr + 0.7152 * pg + 0.0722 * pb) * a;
          r += (SRGB_DECODE_BYTE[data[i] as number] as number) * a;
          g += (SRGB_DECODE_BYTE[data[i + 1] as number] as number) * a;
          b += (SRGB_DECODE_BYTE[data[i + 2] as number] as number) * a;
          weight += a;
        }
      }
    }
  }
  if (weight <= 0) return undefined;
  const rgb = [r / weight, g / weight, b / weight] as const;
  const encodedLuminance = encoded / weight;
  return {
    rgb, encodedLuminance, luminance: srgbDecode(encodedLuminance),
    linearLuminance: 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2],
    footprint: { sampleCount, sourceWidth: width, sourceHeight: height },
  };
}

interface Drawable {
  readonly source: CanvasImageSource;
  readonly width: number;
  readonly height: number;
}

/**
 * The drawable behind each arm with its INTRINSIC size, or `undefined` where it
 * carries no pixels yet.
 *
 * Intrinsic and not layout: an `<img>`'s `width` reflects its attribute and its
 * CSS box, so a backdrop styled to fill the viewport would report the viewport's
 * size and be resampled before it was averaged.
 */
function drawableOf(texture: GlassBackdropTexture): Drawable | undefined {
  switch (texture.kind) {
    case "canvas": {
      const { canvas } = texture;
      return canvas.width > 0 && canvas.height > 0
        ? { source: canvas as CanvasImageSource, width: canvas.width, height: canvas.height }
        : undefined;
    }
    case "image": {
      const image = texture.image;
      if (image instanceof ImageBitmap) {
        return image.width > 0 ? { source: image, width: image.width, height: image.height } : undefined;
      }
      // `complete` alone is true for a failed load; the intrinsic size is what
      // says pixels arrived.
      return image.naturalWidth > 0 && image.naturalHeight > 0
        ? { source: image, width: image.naturalWidth, height: image.naturalHeight }
        : undefined;
    }
    case "video": {
      const { video } = texture;
      return video.readyState >= 2 && video.videoWidth > 0
        ? { source: video, width: video.videoWidth, height: video.videoHeight }
        : undefined;
    }
  }
}

/** Drops the scratch surface. For tests, and for a root tearing down its last group. */
export function releaseBackdropToneScratch(): void {
  scratch = undefined;
}
