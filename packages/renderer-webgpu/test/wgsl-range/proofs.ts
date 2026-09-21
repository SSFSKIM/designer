/**
 * W31 G2 — the committed range proofs: the call sites in `src/wgsl/` whose
 * argument is bounded by a fact the shader text does not carry (claims §5.163).
 *
 * `scan.ts` decides finiteness from the source alone. Eight of the eleven
 * transcendental call sites the package has today are decided that way, because
 * the shader already clamps or the arithmetic already bounds them. The three
 * here are not, and each one is not for the same kind of reason: the bound is a
 * property of a MATERIAL LEAF a document writes, of a SCENE QUANTITY another
 * pass has already normalised, or of the CALLERS of the function the call sits
 * in. No textual evaluator can see any of those, so they are written down.
 *
 * (That third reason read "or of the surrounding control flow" until 2026-09-21,
 * when `prelude.ts`'s entry lost its control-flow half to a clamp in the shader
 * — review closure; claims §5.163 §8, finding N8. The entry survives on its
 * caller-bound half, so the split is still eight and three.)
 *
 * ## What an entry has to say, and what makes it stay true
 *
 * - `bound` — the interval claimed for the argument, as a number, not as a mood.
 * - `dependsOn` — every input the bound is a function of, named as the leaf or
 *   the scene quantity it is.
 * - `why` — the argument, including why it holds over any value a FIT could
 *   produce and not only over the values the bed happens to carry. A proof that
 *   is only true of today's constants is not a proof of this class, because the
 *   class exists precisely because macOS 27's fit reached a σ six waves of
 *   material had never drawn.
 * - `witness` — the substrings of the file the proof leans on. The test asserts
 *   they are still there. A proof keyed only by the call's own text would
 *   survive an edit to the `select` around it or to the `max` that normalises
 *   its input, which is exactly the edit that would end it; the witness is what
 *   makes such an edit turn this file red instead of silent.
 * - `enforcedBy` — where a leaf bound is checked, so that a fit that broke it
 *   fails a committed case rather than a capture.
 */

export interface RangeProof {
  /** File under `src/wgsl/`. */
  readonly file: string;
  /** The call's whitespace-normalised text, exactly as `scan.ts` reports it. */
  readonly call: string;
  /** Which argument this entry bounds; `pow` has two. */
  readonly argument: number;
  readonly bound: string;
  readonly dependsOn: readonly string[];
  readonly why: string;
  readonly witness: readonly string[];
  readonly enforcedBy?: readonly string[];
}

export const RANGE_PROOFS: readonly RangeProof[] = [
  {
    file: "prelude.ts",
    call: "pow(max((c + vec3f(0.055)) / 1.055, vec3f(0.0)), vec3f(2.4))",
    argument: 1,
    bound:
      "the exponent is the literal 2.4; what the entry bounds is the BASE's ceiling, " +
      "at most 1.2 and never near f32max^(1/2.4) = 1.1259e16",
    dependsOn: ["the four callers of `srgb_to_linear` in this package"],
    why:
      "This entry is the MAGNITUDE half of what used to be a two-half proof; the sign " +
      "half is now in the shader (see the history below). `pow(b, 2.4)` overflows f32 " +
      "at b > f32max^(1/2.4) = 1.1259e16, so the bound needed is b < 1.1259e16, i.e. " +
      "c < 1.2e16 — and the scanner names the EXPONENT as the unbounded argument " +
      "because the exponent is what decides that a ceiling is needed at all: at an " +
      "exponent under 1 the same base would be harmless, which is why " +
      "`linear_to_srgb`'s own `pow` needs no ceiling and this one does. `c` is an " +
      "ENCODED sRGB colour at all four call sites and the widest any of them can be is " +
      "bounded by construction: `backdrop.ts`'s is `clamp(colour, 0, 1)`; " +
      "`silhouette-tone.ts`'s is a coverage-weighted mean of `linear_to_srgb` values " +
      "over unorm samples; `optics.ts`'s tint composition is a `mix` of two encoded " +
      "colours; and the widest, `optics.ts`'s un-premultiply, is a colour over " +
      "`max(bodyAlpha, 1e-6)`, which amplifies a unorm sample by at most 1e6. Ten " +
      "orders of magnitude of headroom, and no material leaf enters any of those " +
      "expressions as a multiplier, so no fit moves the bound at all — a fit moves " +
      "what colour arrives, not by how much a division guard can scale it. " +
      "A ceiling in the source would retire this entry, and it is declined: the " +
      "literal it would take is 1.1259e16, which says nothing to a reader of a colour " +
      "transfer function, while the paragraph above is a fact about the four callers " +
      "that is worth keeping written down. " +
      "HISTORY, 2026-09-21 (review closure; claims §5.163 §8, finding N8). Until this " +
      "date the entry also carried the SIGN half, and it read: \"`pow` is undefined in " +
      "WGSL for a base below zero, and this base is below zero exactly where " +
      "`c < -0.055`. The function returns `select(hi, lo, c <= vec3f(0.04045))` " +
      "componentwise, and `-0.055 < 0.04045`, so every component whose base is " +
      "negative is a component the select discards: the undefined value is computed " +
      "and never read. `select` is a choice between two operands and not arithmetic on " +
      "them, so it propagates no NaN from the branch it does not take.\" That argument " +
      "was and is sound. It is no longer load-bearing, because the shader now floors " +
      "the base at zero — the identity at every component the select keeps — and the " +
      "gate's own failure message prefers a clamp to a proof wherever the clamp is an " +
      "identity. The goldens are byte-identical across the change, which is what an " +
      "identity predicts.",
    witness: [
      "let hi = pow(max((c + vec3f(0.055)) / 1.055, vec3f(0.0)), vec3f(2.4));",
      "return select(hi, lo, c <= vec3f(0.04045));",
      "let lo = c / 12.92;",
    ],
  },
  {
    file: "optics.ts",
    call: "pow(lensT, ou.lensShape.y)",
    argument: 1,
    bound: "lensProfileExponent, strictly greater than 0 and at most 64",
    dependsOn: [
      "material leaf `lensProfileExponent` (`ou.lensShape.y`)",
      "scene: the pixel's depth inside the surface, through `lensT`",
    ],
    why:
      "The base is mechanically bounded to [0, 1] and reaches 0 exactly — `lensT` is " +
      "`max(1 - max(-d, 0)/extent, 0)` and every pixel deeper than the lens's extent " +
      "sits at its floor. On [0, 1] the only way out of f32 is through the EXPONENT, " +
      "and there are two of them: `pow(0, e)` is `exp2(e · log2(0))`, which is 0 for " +
      "e > 0, Inf for e < 0, and NaN for e = 0. So the bound the site needs is " +
      "e > 0 strictly; 64 above is a ceiling with no consequence (base ≤ 1 makes " +
      "log2(base) ≤ 0, so a positive exponent can only shrink the result) and is here " +
      "so the enforced interval is an interval. A fit cannot reach 0 or below without " +
      "failing the cases named below, and the term would have no meaning there either: " +
      "`lensProfileExponent` is the steepness of a profile that decays to nothing at " +
      "the extent, and a decay whose exponent is zero is a constant 1 — which is why " +
      "e = 0 is worth naming rather than assuming away. It is the one value that reads " +
      "as a plausible 'switch this off' and is in fact the NaN.",
    witness: [
      "let lensT = max(1.0 - max(-d, 0.0) / extent, 0.0);",
      "let displacementCss = magnitude * pow(lensT, ou.lensShape.y) * ou.lens.x;",
    ],
    enforcedBy: [
      "renderer-webgpu test/w31-wgsl-range.test.ts — the runtime default and both variants",
      "calibration test/w31-material-leaf-ranges.test.ts — every committed profile document",
    ],
  },
  {
    file: "optics.ts",
    call: "pow(max(abs(dot(normal, ou.rimLit.xy)) * 1.4142135, 1e-6), ou.rimLit.z)",
    argument: 0,
    bound:
      "[1e-6, 2.83] — the floor is the shader's own `max`, the ceiling is " +
      "1.4142135 · |rimLitAxis| with |rimLitAxis| at most 2",
    dependsOn: [
      "material leaf `rimLitAxis` (`ou.rimLit.xy`)",
      "material leaf `rimLitExponent` (`ou.rimLit.z`), for what the ceiling has to be enough for",
      "scene: the field pass's surface normal, `field.yz`",
    ],
    why:
      "|dot(normal, axis)| ≤ |normal| · |axis| by Cauchy–Schwarz, and |normal| ≤ 1 is " +
      "written into the field pass: it emits `acc.g / max(length(acc.g), 1e-6)`, which " +
      "has norm exactly 1 above the floor and strictly under 1 below it. The filtered " +
      "read the governor's low rungs take is a convex combination of such vectors and " +
      "so has norm ≤ 1 too. That leaves |axis|, which is a document leaf and is not " +
      "normalised anywhere between the profile and the uniform — the renderer packs " +
      "`rimLitAxis` into `d[100..101]` verbatim. Bounded at 2 by the cases below, the " +
      "base is at most 2.83 and log2 of it at most 1.5, so the whole expression is " +
      "finite for every exponent up to 85 — and the exponent's own bound is 64. The " +
      "floor at 1e-6 is the shader's, and it is the half the exponent's NEGATIVE " +
      "direction would need: at base 1e-6, log2 is -19.93 and an exponent below -6.42 " +
      "would overflow. The exponent is held at or above 0 for that reason as much as " +
      "for this one. Every document ships the axis as a unit vector (the shipped " +
      "[-0.7071, -0.7071] has norm 0.99999) because it is an angle written as a pair, " +
      "which is what makes 2 a ceiling no fit approaches rather than one it is near.",
    witness: [
      "let normal = acc.g / len;",
      "let len = max(length(acc.g), 1e-6);",
      "let lit = pow(max(abs(dot(normal, ou.rimLit.xy)) * 1.4142135, 1e-6), ou.rimLit.z);",
    ],
    enforcedBy: [
      "renderer-webgpu test/w31-wgsl-range.test.ts — the runtime default and both variants",
      "calibration test/w31-material-leaf-ranges.test.ts — every committed profile document",
    ],
  },
  {
    file: "optics.ts",
    call: "pow(max(abs(dot(normal, ou.rimLit.xy)) * 1.4142135, 1e-6), ou.rimLit.z)",
    argument: 1,
    bound: "rimLitExponent, in [0, 64]",
    dependsOn: ["material leaf `rimLitExponent` (`ou.rimLit.z`)"],
    why:
      "With the base in [1e-6, 2.83] the finite window for the exponent is " +
      "[-6.42, 85]: below -6.42 the floor's own log2 of -19.93 overflows, above 85 the " +
      "ceiling's 1.5 does. [0, 64] sits well inside it on both sides. The lower end is " +
      "0 rather than a negative number because the term is a directional factor — " +
      "`(√2 · |n · L|)^p`, one at the axis and falling away from it — and a negative " +
      "exponent would invert it into a factor that is largest where the light is " +
      "absent. 0 itself is safe here, unlike the lens exponent above, because this " +
      "base has a positive floor: `pow(1e-6, 0)` is 1, which is exactly the inert " +
      "reading the `clear` variant ships and which `material.ts`'s own note names.",
    witness: [
      "let lit = pow(max(abs(dot(normal, ou.rimLit.xy)) * 1.4142135, 1e-6), ou.rimLit.z);",
    ],
    enforcedBy: [
      "renderer-webgpu test/w31-wgsl-range.test.ts — the runtime default and both variants",
      "calibration test/w31-material-leaf-ranges.test.ts — every committed profile document",
    ],
  },
];

/**
 * The bounds the proofs above lean on, as numbers one test can read and another
 * can assert. Kept here rather than in either test so the two packages' cases
 * cannot drift apart — `calibration` has no dependency on this package and
 * copies the three numbers with this file named beside them.
 */
export const LEAF_BOUNDS = {
  /** Strictly positive: `pow(0, 0)` is NaN and `pow(0, e < 0)` is Inf. */
  lensProfileExponent: { exclusiveMin: 0, max: 64 },
  rimLitExponent: { min: 0, max: 64 },
  /** The Euclidean norm of the pair, not either component. */
  rimLitAxisNorm: { max: 2 },
} as const;
