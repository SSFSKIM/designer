/**
 * `@vitrea/policy` — the vocabulary both rendering tiers have to agree on.
 *
 * ## Why this is a package (Decision Log #23(d))
 *
 * The refraction ladder was not in one place for most of v1. C5's CSS tier had a
 * copy in `platform-web/src/refraction.ts`, C6's shaders had a second in
 * `renderer-webgpu/src/material.ts`, and `platform-web/src/optics.ts` re-inlined
 * the regime's three-arm map twice more inside the tier that already had it —
 * five statements of one four-function rule, plus three copies of the rung-scale
 * table. Each carried a comment explaining that it was restated rather than
 * imported, and every one of those comments was right: core is the ladder's
 * natural home, since `RefractionQuality` is core's type and the accessibility
 * regime is core's resolver, but `renderer-webgpu` sits *below* core and reaches
 * it only through a dynamic import, so an import back would close a dependency
 * cycle — while `platform-web` sits above core and can only see what core
 * re-exports. There was no module both tiers could see.
 *
 * A pure leaf below everything is the module both tiers can see. This package
 * imports nothing, from anywhere, which is not tidiness but the whole mechanism:
 * core imports it and re-exports `RefractionQuality`, so core's published surface
 * is what it always was; the renderer takes it as a direct dependency alongside
 * `@vitrea/geometry`, with no cycle to close; and platform-web reads the same
 * symbols the shaders do.
 *
 * Two alternatives were rejected. Putting the ladder in `@vitrea/geometry` would
 * have reached one module both tiers already import, at the cost of a shape
 * package owning an accessibility vocabulary it has no other business with.
 * Inverting the renderer seam — core owning the ladder and passing it down as
 * arguments — would have threaded it through every call site in `renderer.ts` to
 * remove a twelve-line duplication.
 *
 * ## What it deliberately does not absorb
 *
 * The renderer's `MaterialPolicyView` and `NOMINAL_MATERIAL_POLICY` stay in the
 * renderer. They look like a third restatement of core's `ResolvedMaterialPolicy`
 * and are not: the view is a *narrower structural slice*, because core carries an
 * eighth axis (`colorSource`) that no renderer reads. Moving it here would
 * relocate a type rather than deduplicate one, and the only way to make it a real
 * deduplication — having core's published, heavily documented policy type extend
 * a leaf's — would rewrite §Accessibility's own vocabulary for no gain. The
 * assignability pin in `renderer-webgpu/test/core-contract.test.ts` already
 * carries the invariant, cheaply.
 *
 * ## The laws it is held to
 *
 * Pure, like the other leaves (X4): no DOM, no Node built-ins, no runtime
 * dependencies. `eslint.config.mjs`'s shared `pure` config enforces it and
 * `test/purity.test.ts` asserts it — and here the "no downstream imports" half of
 * that rule is load-bearing rather than hygienic, since one import of core would
 * restore the cycle this package exists to avoid.
 *
 * Private and bundled (X7). Core, platform-web and the React bindings all carry
 * `noExternal: [/^@vitrea\//]`, so nothing here reaches npm as a package of its
 * own — only inlined into the three published artifacts.
 */

export {
  accessibilityRefractionCap,
  DEFAULT_REFRACTION_SCALE,
  effectiveRefraction,
  REFRACTION_LADDER,
  refractionRank,
  type RefractionPolicyView,
  type RefractionQuality,
  type RefractionRegime,
  type RefractionScale,
} from "./refraction";
