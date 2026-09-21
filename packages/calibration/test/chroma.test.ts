import { describe, expect, it } from "vitest";

import { linearRgbToOklab, oklabChroma } from "../src/color";
import { CalibrationError } from "../src/errors";
import {
  blurLinearRgb,
  blurredChromaReference,
  chromaStructure,
  perPixelChroma,
} from "../src/metrics/chroma";
import { fromLinearRgb, maskFromPredicate, rectPredicate } from "./synthesise";

/**
 * The synthetic field every case below is read on: a level and two hues, all
 * three modulated in the SAME spatial band.
 *
 * That last property is what makes the blur case a real test rather than a
 * coincidence. A blur is a low-pass filter, so it attenuates the chroma and the
 * structure by the same factor only where the two live at the same spatial
 * frequency — which is roughly true of a photograph and exactly true here, and
 * a field whose hue varied slowly while its level varied fast would make ratio
 * (i) rise under a blur and prove nothing about either.
 *
 * The chromatic modulations are along ZERO-LUMINANCE directions of linear sRGB,
 * so the level carrier owns the luma spread outright and the hue carriers own
 * the chroma spread. `(0.7152, −0.2126, 0)` and `(0, 0.0722, −0.7152)` are two
 * such directions, built from the Rec.709 weights themselves.
 *
 * Deliberately not a photograph: every number below is checked against the
 * algebra of the operation applied to the field, and an analytic field is the
 * only kind on which that algebra is checkable.
 */
const WIDTH = 64;
const HEIGHT = 64;

function colourField(scale = 1): ReturnType<typeof fromLinearRgb> {
  return fromLinearRgb(WIDTH, HEIGHT, (x, y) => {
    const level = Math.sin((2 * Math.PI * x) / 12) * Math.cos((2 * Math.PI * y) / 10);
    const hueA = Math.cos((2 * Math.PI * x) / 10) * Math.sin((2 * Math.PI * y) / 12);
    const hueB = Math.sin((2 * Math.PI * (x + y)) / 11);
    const base = 0.3 * (1 + 0.45 * level);
    const r = base + 0.55 * base * hueA * 0.7152;
    const g = base - 0.55 * base * hueA * 0.2126 + 0.55 * base * hueB * 0.0722;
    const b = base - 0.55 * base * hueB * 0.7152;
    return [scale * r, scale * g, scale * b];
  });
}

const MASK = maskFromPredicate(WIDTH, HEIGHT, rectPredicate(8, 8, WIDTH - 9, HEIGHT - 9));

/** A flat neutral plate at one linear level, over the whole grid. */
function greyPlate(level: number): ReturnType<typeof fromLinearRgb> {
  return fromLinearRgb(WIDTH, HEIGHT, () => [level, level, level]);
}

describe("perPixelChroma reads the population and not the mean", () => {
  it("reads a colour field's chroma spread, where the mean colour is nearly neutral", () => {
    const field = colourField();
    const read = perPixelChroma(field, MASK);
    expect(read.sampleCount).toBe((WIDTH - 16) * (HEIGHT - 16));
    expect(read.meanChroma).toBeGreaterThan(0.03);
    expect(read.chromaSpread).toBeGreaterThan(0.02);
    expect(read.luminanceStdDev).toBeGreaterThan(0.01);

    // The instrument this wave exists to replace: the MEAN linear colour of the
    // same region is far less chromatic than any pixel of it. That gap is the
    // whole reason for a per-pixel read.
    let r = 0;
    let g = 0;
    let b = 0;
    let n = 0;
    for (let i = 0; i < WIDTH * HEIGHT; i += 1) {
      if ((MASK.mask[i] ?? 0) === 0) continue;
      const o = i * 4;
      const toLinear = (byte: number): number => {
        const e = byte / 255;
        return e <= 0.04045 ? e / 12.92 : Math.pow((e + 0.055) / 1.055, 2.4);
      };
      r += toLinear(field.data[o] ?? 0);
      g += toLinear(field.data[o + 1] ?? 0);
      b += toLinear(field.data[o + 2] ?? 0);
      n += 1;
    }
    const meanChroma = oklabChroma(linearRgbToOklab(r / n, g / n, b / n));
    expect(meanChroma).toBeLessThan(read.meanChroma / 4);
  });

  it("refuses ratio (i) on a flat field rather than dividing by rounding", () => {
    const read = perPixelChroma(greyPlate(0.3), MASK);
    expect(read.luminanceStdDev).toBeLessThan(1e-4);
    expect(read.chromaToStructure).toBeUndefined();
  });

  it("refuses an empty mask", () => {
    const empty = maskFromPredicate(WIDTH, HEIGHT, () => false);
    expect(() => perPixelChroma(colourField(), empty)).toThrow(CalibrationError);
  });
});

describe("the unit cases the bound is declared against (claims §5.161 §1)", () => {
  it("a grey plate over a colour field reads 0 on every ratio", () => {
    const backdrop = colourField();
    const plate = greyPlate(0.24);
    const report = chromaStructure(plate, plate, backdrop, MASK, { blurredReference: true });

    expect(report.native.meanChroma).toBeLessThan(1e-3);
    expect(report.native.chromaSpread).toBeLessThan(1e-3);
    // (i): no chroma per unit structure. The plate has no structure either, so
    // the ratio is refused rather than reported as a zero it did not measure —
    // which is the honest reading and the one the tables carry.
    expect(report.native.chromaToStructure).toBeUndefined();
    // (ii): the raw ratio IS defined, because the backdrop supplies the
    // denominator, and it reads essentially zero.
    expect(report.rawRatioNative ?? 1).toBeLessThan(0.02);
    expect(report.rawRatioWeb ?? 1).toBeLessThan(0.02);
    // (iii): no σ reproduces a flat interior from a finite blur of this field
    // at 64 px, so the reference is absent rather than invented.
    expect(report.blurredNative).toBeUndefined();
  });

  it("a luma-only darkening scales ratio (i) by exactly c^(-2/3), and leaves the OKLab-L form alone", () => {
    /*
     * The finding W31 G0 records against the charter's own Design paragraph,
     * which asserts this case leaves ratio (i) UNCHANGED. It does not, and the
     * exponent is exact rather than approximate: OKLab's `L`, `a` and `b` are
     * all linear in the cube roots of the LMS responses, so multiplying linear
     * RGB by `c` multiplies all three by exactly `c^(1/3)`, while ratio (i)'s
     * denominator is LINEAR luma and scales by `c`.
     *
     * The tolerance is 8-bit quantisation and nothing else: the darkened field
     * is re-encoded to bytes before it is read back, which is what a capture
     * does to it.
     */
    const c = 0.5;
    const bright = perPixelChroma(colourField(1), MASK);
    const dark = perPixelChroma(colourField(c), MASK);

    expect(dark.luminanceStdDev / bright.luminanceStdDev).toBeCloseTo(c, 2);
    expect(dark.chromaSpread / bright.chromaSpread).toBeCloseTo(Math.cbrt(c), 2);
    expect(dark.oklabLStdDev / bright.oklabLStdDev).toBeCloseTo(Math.cbrt(c), 2);

    const ratioI = (dark.chromaToStructure ?? 0) / (bright.chromaToStructure ?? 1);
    /*
     * Stated as a relative error, because that is what 8-bit quantisation
     * bounds: the law holds to 0.35% on a field re-encoded to bytes twice.
     *
     * 2026-09-21, the review closure (claims §5.161 §11, finding N10): this was
     * `toBeCloseTo(1, 2)`, which admits 0.5% and not the 0.35% the sentence
     * above states. The measured relative error on this field is 0.3451%, so the
     * assertion is written as the prose rather than near it — a case whose
     * tolerance is looser than its own comment is a case that would pass a law
     * the comment forbids. The field is synthetic and deterministic; there is no
     * capture noise here for a margin to absorb.
     */
    expect(Math.abs(ratioI / Math.pow(c, -2 / 3) - 1)).toBeLessThan(0.0035);
    // The exponent is not zero, which is the whole point of recording it.
    expect(ratioI).toBeGreaterThan(1.5);

    // The same numerator over sd(L_oklab) IS invariant, which is why that
    // denominator is exported beside the declared one.
    const invariant = (r: ReturnType<typeof perPixelChroma>): number =>
      r.chromaSpread / r.oklabLStdDev;
    expect(invariant(dark) / invariant(bright)).toBeCloseTo(1, 2);
  });

  it("a blur alone leaves ratio (i) unchanged and moves ratio (ii)", () => {
    /*
     * The property the bound rests on. A linear blur attenuates chromatic and
     * luminous deviations by the same factor to first order, so it divides out
     * of ratio (i) — and it does not divide out of ratio (ii), which is taken
     * against the RAW backdrop. A retention fitted on (ii) would absorb this
     * wave's untouched structure deficit as saturation; one fitted on (i)
     * cannot.
     */
    const backdrop = colourField();
    const blurred = blurLinearRgb(backdrop, 1.5);
    const blurredImage = fromLinearRgb(WIDTH, HEIGHT, (x, y) => {
      const o = (y * WIDTH + x) * 3;
      return [blurred.rgb[o] ?? 0, blurred.rgb[o + 1] ?? 0, blurred.rgb[o + 2] ?? 0];
    });

    const raw = perPixelChroma(backdrop, MASK);
    const soft = perPixelChroma(blurredImage, MASK);

    // The blur really did remove structure — otherwise the case is vacuous.
    // More than half of it, which is about what vitrea's dark body removes
    // beyond the reference's on the cells this wave reads.
    expect(soft.luminanceStdDev).toBeLessThan(raw.luminanceStdDev * 0.55);

    // (i) survives it, to 1.9%. The cancellation is first-order and not an
    // identity, and the residual is recorded rather than asserted away: it
    // grows with the radius, reaching 7% at σ = 2 on this field, where the
    // kernel has begun to eat the carriers themselves.
    const shift = (soft.chromaToStructure ?? 0) / (raw.chromaToStructure ?? 1);
    expect(shift).toBeGreaterThan(0.97);
    expect(shift).toBeLessThan(1.03);

    // (ii) moves, and by much more: more than half of it, against (i)'s 1.9%.
    const report = chromaStructure(blurredImage, blurredImage, backdrop, MASK);
    expect(report.rawRatioWeb ?? 1).toBeLessThan(0.6);
  });
});

describe("the blurred reference (ratio iii)", () => {
  it("recovers the radius a pure blur was applied at, and reads a ratio of 1", () => {
    const backdrop = colourField();
    const blurred = blurLinearRgb(backdrop, 1.5);
    const blurredImage = fromLinearRgb(WIDTH, HEIGHT, (x, y) => {
      const o = (y * WIDTH + x) * 3;
      return [blurred.rgb[o] ?? 0, blurred.rgb[o + 1] ?? 0, blurred.rgb[o + 2] ?? 0];
    });
    const side = perPixelChroma(blurredImage, MASK);
    const reference = blurredChromaReference(
      backdrop,
      MASK,
      side.luminanceStdDev,
      side.meanChroma,
    );
    expect(reference).toBeDefined();
    expect(reference?.sigmaPx ?? 0).toBeCloseTo(1.5, 2);
    // A body that ONLY blurred reads 1: every hue the blur left is still there.
    expect(reference?.ratio ?? 0).toBeCloseTo(1, 1);
  });

  it("reads below 1 for a body that blurred AND lost chroma", () => {
    const backdrop = colourField();
    const blurred = blurLinearRgb(backdrop, 1.5);
    // The plate composite, in linear light: half the blurred backdrop plus half
    // a neutral at the same mean level. Chromaticity is halved; the level is not.
    const desaturated = fromLinearRgb(WIDTH, HEIGHT, (x, y) => {
      const o = (y * WIDTH + x) * 3;
      const r = blurred.rgb[o] ?? 0;
      const g = blurred.rgb[o + 1] ?? 0;
      const b = blurred.rgb[o + 2] ?? 0;
      const y709 = 0.2126 * r + 0.7152 * g + 0.0722 * b;
      return [0.5 * r + 0.5 * y709, 0.5 * g + 0.5 * y709, 0.5 * b + 0.5 * y709];
    });
    const side = perPixelChroma(desaturated, MASK);
    const reference = blurredChromaReference(
      backdrop,
      MASK,
      side.luminanceStdDev,
      side.meanChroma,
    );
    expect(reference).toBeDefined();
    expect(reference?.ratio ?? 1).toBeLessThan(0.8);
  });

  it("is absent where the side carries more structure than its own backdrop", () => {
    const backdrop = colourField();
    const side = perPixelChroma(backdrop, MASK);
    expect(
      blurredChromaReference(backdrop, MASK, side.luminanceStdDev * 1.5, side.meanChroma),
    ).toBeUndefined();
  });
});

describe("chromaStructure refuses what it cannot index", () => {
  it("refuses a backdrop on a different grid", () => {
    const small = fromLinearRgb(8, 8, () => [0.2, 0.2, 0.2]);
    expect(() => chromaStructure(colourField(), colourField(), small, MASK)).toThrow(
      CalibrationError,
    );
  });
});
