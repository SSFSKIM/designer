/**
 * The dual-cap rule (Decision Log #19, ratified with C4's landing), read from the
 * one module that owns it.
 *
 * Two independent things cap refraction: the accessibility policy's ceiling
 * (core's `ResolvedMaterialPolicy.refraction`, a regime — `nominal | reduced |
 * none`) and the group's resolved capability state (X2's `RefractionQuality` —
 * `true | approximate | none`, what the sampling backend can actually deliver).
 * **Renderers honour the lower of the two.** That sentence is only meaningful
 * against an ordering, and C5's CSS tier and C6's shaders have to read the same
 * one.
 *
 * The ladder was authored here until Decision Log #23(d), with a second copy in
 * `@vitrea/renderer-webgpu`'s `material.ts`, because the renderer sits *below*
 * core and this package sits above it, so there was no module both could import.
 * `@vitrea/policy` is that module: a pure leaf under everything, which the
 * renderer takes as a direct dependency and this package reads the same symbols
 * from. This file stays because `index.ts` star-exports it and these four names
 * are part of the published surface — it is now a re-export and nothing else.
 *
 * One signature widened in the move. `accessibilityRefractionCap` took a whole
 * `ResolvedMaterialPolicy` here and reads exactly one axis of it, so the shared
 * one takes the axis (`RefractionPolicyView`); core's policy still satisfies it
 * structurally, and so does the renderer's narrower `MaterialPolicyView`, which is
 * what let the two implementations become one.
 */

export {
  accessibilityRefractionCap,
  effectiveRefraction,
  REFRACTION_LADDER,
  refractionRank,
} from "@vitrea/policy";
