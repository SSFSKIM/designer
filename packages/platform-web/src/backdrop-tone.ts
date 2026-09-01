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
 * ## What this is coarse about, and why that is the honest trade
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

import type { GlassBackdropTexture } from "./renderer-bridge";

/**
 * A backdrop's tone reading, in the W9 model's two spaces (claims §5.31–§5.34).
 * A solid backdrop is identical under both, which is why every solid-fitted
 * constant survived the convention work unchanged.
 */
export interface BackdropToneSample {
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
): BackdropToneSample | undefined {
  if (texture === undefined) return undefined;
  const surface = scratchSurface();
  if (surface === undefined) return undefined;

  const drawable = drawableOf(texture);
  if (drawable === undefined) return undefined;

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
      r += srgbDecode(pr) * a;
      g += srgbDecode(pg) * a;
      b += srgbDecode(pb) * a;
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
