/**
 * W31 G2 — the three material leaves a WGSL range proof leans on, checked on
 * every document the project has fitted (claims §5.163 §1).
 *
 * `packages/renderer-webgpu/test/wgsl-range/` classifies every transcendental in
 * the shaders. Eight of its eleven call sites are bounded by the shader text
 * itself. Three are bounded by a material leaf instead — `pow`'s exponent is a
 * number a document writes, and no reading of the shader can see it — and those
 * three carry written proofs whose bound is a bound on the LEAF.
 *
 * A proof like that is only worth its words if a fit that broke it fails
 * something. This is that something, and it belongs here rather than beside the
 * shaders because here is where the fitted documents are: the renderer's own
 * case pins the runtime default, and this one pins every patch that supersedes
 * it. A document that names none of the three inherits the default and is
 * covered by the other case.
 *
 * The bounds are copied from `test/wgsl-range/proofs.ts`'s `LEAF_BOUNDS` with
 * that file named, because `@vitrea/calibration` has no import path into another
 * package's test tree. Three numbers, restated with their source, rather than a
 * build seam for them.
 *
 * ## Why each bound is what it is
 *
 * - `lensProfileExponent` must be STRICTLY positive. Its base, `lensT`, reaches
 *   exactly 0 at every pixel deeper than the lens's extent, and `pow(0, 0)` is
 *   `exp2(0 · log2(0))` = NaN while `pow(0, e < 0)` is Inf. Zero is the trap: it
 *   reads as "switch the profile off" and is the one value that is not a number.
 * - `rimLitExponent` may be 0 — its base is floored at 1e-6 — but not negative
 *   (below −6.42 the floor's own log2 overflows f32) and not enormous.
 * - `rimLitAxis` is a direction and reaches the uniform un-normalised, so its
 *   NORM is what bounds the rim's `pow` base. Every document ships it as a unit
 *   vector; 2 is a ceiling nothing approaches.
 */

import { readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

/** Mirrors `packages/renderer-webgpu/test/wgsl-range/proofs.ts`'s `LEAF_BOUNDS`. */
const LEAF_BOUNDS = {
  lensProfileExponent: { exclusiveMin: 0, max: 64 },
  rimLitExponent: { min: 0, max: 64 },
  rimLitAxisNorm: { max: 2 },
} as const;

const PROFILES = resolve(import.meta.dirname, "..", "profiles");

interface Document {
  readonly patch?: {
    readonly lensProfileExponent?: number;
    readonly rimLitAxis?: readonly [number, number];
    readonly optics?: Readonly<Record<string, { readonly rimLitExponent?: number }>>;
  };
}

const DOCUMENTS = readdirSync(PROFILES)
  .filter((name) => name.startsWith("apple-macos-") && name.endsWith(".json"))
  .sort()
  .map((name) => ({
    name,
    document: JSON.parse(readFileSync(resolve(PROFILES, name), "utf8")) as Document,
  }));

describe("the leaves a WGSL range proof leans on (claims §5.163 §1)", () => {
  it("reads every fitted document, so a green run is not an empty one", () => {
    // Six today: two frozen macOS 26.5, four macOS 27 (active and receded per
    // scheme), plus the seed. Stated as a floor rather than a count so a wave
    // that fits another document does not have to edit an arithmetic fact.
    expect(DOCUMENTS.length).toBeGreaterThanOrEqual(6);
  });

  it("no document names a lens profile exponent at or below zero", () => {
    for (const { name, document } of DOCUMENTS) {
      const value = document.patch?.lensProfileExponent;
      if (value === undefined) continue;
      expect(value, `${name}: pow(0, ${value}) is NaN or Inf at every pixel past the lens extent`)
        .toBeGreaterThan(LEAF_BOUNDS.lensProfileExponent.exclusiveMin);
      expect(value, name).toBeLessThanOrEqual(LEAF_BOUNDS.lensProfileExponent.max);
    }
  });

  it("no document names a lit-edge exponent outside its window", () => {
    for (const { name, document } of DOCUMENTS) {
      for (const [variant, optics] of Object.entries(document.patch?.optics ?? {})) {
        const value = optics.rimLitExponent;
        if (value === undefined) continue;
        expect(value, `${name} :: ${variant}`).toBeGreaterThanOrEqual(LEAF_BOUNDS.rimLitExponent.min);
        expect(value, `${name} :: ${variant}`).toBeLessThanOrEqual(LEAF_BOUNDS.rimLitExponent.max);
      }
    }
  });

  it("no document names a lit-edge axis longer than the bound the rim's pow base uses", () => {
    for (const { name, document } of DOCUMENTS) {
      const axis = document.patch?.rimLitAxis;
      if (axis === undefined) continue;
      const norm = Math.hypot(axis[0], axis[1]);
      expect(norm, `${name}: |rimLitAxis| = ${norm}`).toBeLessThanOrEqual(
        LEAF_BOUNDS.rimLitAxisNorm.max,
      );
    }
  });

  it("at least one document names each leaf, so the cases are not all vacuous", () => {
    // Three `continue`s above would make three green tests out of an empty file.
    const named = {
      lensProfileExponent: DOCUMENTS.filter((entry) => entry.document.patch?.lensProfileExponent !== undefined),
      rimLitExponent: DOCUMENTS.filter((entry) =>
        Object.values(entry.document.patch?.optics ?? {}).some(
          (optics) => optics.rimLitExponent !== undefined,
        ),
      ),
      rimLitAxis: DOCUMENTS.filter((entry) => entry.document.patch?.rimLitAxis !== undefined),
    };
    for (const [leaf, entries] of Object.entries(named)) {
      expect(entries.length, `no committed document names ${leaf}`).toBeGreaterThan(0);
    }
  });
});
