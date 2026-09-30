/**
 * An emulator of the four SVG filter primitives W42's CSS body law is built from, at one pixel,
 * under the semantics Filter Effects 1 gives them (G2's implementation-design §5 as revised by
 * §11's R5). Not a test file: `w42-css-filter-algebra.test.ts` runs the law's pure program
 * (`cssTierBodyLawFilter`) through it and compares what comes out with the renderer's CPU
 * composite and tones.
 *
 * What it models, and why each is load-bearing for the algebra:
 *
 * - **Premultiplied storage.** Every result is held premultiplied in the colour space of the
 *   primitive that produced it. `feComposite` arithmetic acts on the premultiplied channels,
 *   ALPHA INCLUDED, and clamps each to [0, 1], then holds each colour channel at or below the
 *   alpha, as a premultiplied surface must. That is R5's first point: an arithmetic whose
 *   coefficients sum below 1 writes a translucent result, and one that sums to 0 writes nothing.
 * - **Un-premultiplied transfers.** `feComponentTransfer` and `feColorMatrix` act on
 *   un-premultiplied values and clamp their output, so a transfer that sets alpha to 1 divides a
 *   partial-alpha blur by its own weight — the normalised edge.
 * - **Colour spaces per primitive.** A result read by a primitive in the other space is converted
 *   on its un-premultiplied colour; the output is read in sRGB.
 * - **Tables** per the spec: n values, piecewise linear over n − 1 equal intervals.
 * - **Optionally, eight bits.** With `eightBit` every stored channel is rounded to 1/255, which is
 *   one plausible model of an engine's intermediates and nothing more; the engine's own is
 *   Decision Log 4's measurement.
 *
 * `feGaussianBlur` is not emulated at one pixel: its result is supplied by the caller, which is
 * where the blur's output enters the algebra.
 */

import type {
  CssTierBodyLawFilter,
  CssTierFilterSpace,
  CssTierTransferFunction,
} from "@vitreajs/vitrea-web";

export type Rgba = readonly [number, number, number, number];

/** A result supplied by the caller: straight (un-premultiplied) colour and alpha, in a space. */
export interface SuppliedResult {
  readonly rgba: Rgba;
  readonly space: CssTierFilterSpace;
}

interface Stored {
  /** Premultiplied. */
  readonly value: Rgba;
  readonly space: CssTierFilterSpace;
}

const clamp01 = (x: number): number => Math.min(1, Math.max(0, x));
const decode = (x: number): number => {
  const c = clamp01(x);
  return c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
};
const encode = (x: number): number => {
  const c = clamp01(x);
  return c <= 0.0031308 ? c * 12.92 : 1.055 * Math.pow(c, 1 / 2.4) - 0.055;
};

function transfer(fn: CssTierTransferFunction | undefined, x: number): number {
  if (fn === undefined) return x;
  if (fn.type === "linear") return clamp01(fn.slope * x + fn.intercept);
  const v = fn.tableValues;
  const n = v.length;
  if (n === 1) return clamp01(v[0]!);
  const c = clamp01(x);
  const k = Math.min(n - 2, Math.floor(c * (n - 1)));
  return clamp01(v[k]! + (c - k / (n - 1)) * (n - 1) * (v[k + 1]! - v[k]!));
}

export interface EmulatorOptions {
  readonly eightBit?: boolean;
}

/**
 * Runs the program at one pixel. `supplied` names results the caller provides (the two raw blurs
 * at least, or their normalised forms, or the argument); a primitive whose result is supplied is
 * not evaluated. Returns every stored result, and the output read as straight sRGB.
 */
export function emulateBodyLawFilter(
  filter: CssTierBodyLawFilter,
  supplied: Readonly<Record<string, SuppliedResult>>,
  options: EmulatorOptions = {},
): { readonly output: readonly [number, number, number]; readonly read: (name: string) => Rgba } {
  const store = new Map<string, Stored>();
  const quantise = (x: number): number => (options.eightBit === true ? Math.round(x * 255) / 255 : x);
  const put = (name: string, premultiplied: Rgba, space: CssTierFilterSpace): void => {
    store.set(name, {
      value: [quantise(premultiplied[0]), quantise(premultiplied[1]), quantise(premultiplied[2]),
        quantise(premultiplied[3])],
      space,
    });
  };
  for (const [name, result] of Object.entries(supplied)) {
    const [r, g, b, a] = result.rgba;
    put(name, [r * a, g * a, b * a, a], result.space);
  }
  /** A stored result as straight colour in `space`. */
  const straight = (name: string, space: CssTierFilterSpace): Rgba => {
    const stored = store.get(name);
    if (stored === undefined) throw new Error(`the emulator has no result named ${name}`);
    const [pr, pg, pb, a] = stored.value;
    const un = a > 0 ? [pr / a, pg / a, pb / a] : [0, 0, 0];
    const convert = stored.space === space
      ? (x: number): number => x
      : space === "linearRGB" ? decode : encode;
    return [convert(un[0]!), convert(un[1]!), convert(un[2]!), a];
  };
  for (const primitive of filter.primitives) {
    if (primitive.result in supplied) continue;
    // A primitive upstream of a supplied result may lack its inputs; it is skipped, and a
    // later read of what it would have written throws.
    if (primitive.primitive !== "feGaussianBlur" && (!store.has(primitive.in) ||
      (primitive.primitive === "feComposite" && !store.has(primitive.in2)))) continue;
    switch (primitive.primitive) {
      case "feGaussianBlur":
        // Supplied by the caller or not needed: a later read of it throws.
        break;
      case "feComponentTransfer": {
        const [r, g, b, a] = straight(primitive.in, primitive.space);
        const out: Rgba = [transfer(primitive.r, r), transfer(primitive.g, g),
          transfer(primitive.b, b), transfer(primitive.a, a)];
        put(primitive.result, [out[0] * out[3], out[1] * out[3], out[2] * out[3], out[3]],
          primitive.space);
        break;
      }
      case "feColorMatrix": {
        const x = [...straight(primitive.in, primitive.space), 1];
        const m = primitive.values;
        const row = (i: number): number =>
          clamp01(x.reduce((sum, value, j) => sum + m[i * 5 + j]! * value, 0));
        const out: Rgba = [row(0), row(1), row(2), row(3)];
        put(primitive.result, [out[0] * out[3], out[1] * out[3], out[2] * out[3], out[3]],
          primitive.space);
        break;
      }
      case "feComposite": {
        const premultiply = (value: Rgba): Rgba =>
          [value[0] * value[3], value[1] * value[3], value[2] * value[3], value[3]];
        const i1 = premultiply(straight(primitive.in, primitive.space));
        const i2 = premultiply(straight(primitive.in2, primitive.space));
        const { k1, k2, k3, k4 } = primitive;
        const channel = (i: number): number =>
          clamp01(k1 * i1[i]! * i2[i]! + k2 * i1[i]! + k3 * i2[i]! + k4);
        const a = channel(3);
        put(primitive.result, [Math.min(channel(0), a), Math.min(channel(1), a),
          Math.min(channel(2), a), a], primitive.space);
        break;
      }
    }
  }
  const [r, g, b] = straight(filter.results.output, "sRGB");
  return { output: [r, g, b], read: (name) => straight(name, "sRGB") };
}
