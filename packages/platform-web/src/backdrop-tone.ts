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
 *    averaged in linear light, giving a colour as well as a level.
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
 * The read is a `drawImage` downsample: the browser averages in the texture's own
 * encoded space and this converts each surviving texel to linear before the mean,
 * so the answer is a linear mean of encoded blocks rather than a true linear mean.
 * `SAMPLE_EXTENT` is what makes that difference small; it is not zero, and the
 * adaptation curve's dead zone (nothing happens above a fifth of the backdrop
 * scale) is where the remaining error lands.
 */

import type { GlassBackdropTexture } from "./renderer-bridge";

/** A backdrop's average colour in linear light, and its Rec. 709 luminance. */
export interface BackdropToneSample {
  readonly rgb: readonly [number, number, number];
  readonly luminance: number;
}

/**
 * The longest edge the backdrop is drawn at before it is averaged.
 *
 * Set by a measured trap rather than by a budget. `drawImage` downsamples in the
 * texture's own **encoded** space, and the encoded mean of a block is not the
 * encoded form of its linear mean — for a block that is a quarter white and three
 * quarters black the two differ by five times. At 32 px the calibration bed's
 * impulse backdrop (4 px squares on a 64 px grid) reported a linear mean of
 * 0.0008 against its true 0.0039, and the CSS tier rendered a fully adapted
 * capsule five times too dark. Drawing at up to 512 puts the bed's backdrops at
 * or near 1:1, where the error is a rounding one.
 *
 * It does not vanish for a backdrop larger than this — a 4K page averages 8×8
 * blocks in the wrong space — and that is a stated limit of this tier's reading,
 * not a defect the number can fix. The readback is 1 MB at the cap, once per
 * declared content change.
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
    let weight = 0;
    for (let i = 0; i < data.length; i += 4) {
      // Alpha-weighted: a backdrop source with transparent regions has not
      // declared a colour there, and counting those texels as black would report
      // a dark backdrop for a page that has none.
      const a = (data[i + 3] as number) / 255;
      if (a <= 0) continue;
      r += srgbDecode((data[i] as number) / 255) * a;
      g += srgbDecode((data[i + 1] as number) / 255) * a;
      b += srgbDecode((data[i + 2] as number) / 255) * a;
      weight += a;
    }
    if (weight <= 0) return undefined;
    const rgb: readonly [number, number, number] = [r / weight, g / weight, b / weight];
    return { rgb, luminance: 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2] };
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
