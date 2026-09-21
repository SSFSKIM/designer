/**
 * W31 G0 — the CSS tier's analytic chroma ceiling, per scheme (claims §5.161 §5).
 *
 *   npx tsx results/2026-09-21-w31-g0-chroma-cut/css-ceiling.ts
 *
 * The tier composes exactly two layers: one `backdrop-filter:
 * blur(...) saturate(s)` and one `rgba()` plate at alpha α over it. The
 * saturation acts on the backdrop BEFORE the plate covers it, so whatever the
 * WebGPU tier's chroma retention turns out to be, the interior chroma this tier
 * can reach is bounded above by
 *
 *     ratio (ii) ≤ (1 − α) · s
 *
 * — the backdrop's per-pixel chroma, saturated by `s`, attenuated by the plate.
 * `s` is 1.8 on the regular variant and does not move (W31 X3); α is the
 * CONVERTED alpha `cssTintAlpha` solves, not the renderer's `tintAlpha`, so it
 * has to be evaluated rather than read off the document.
 *
 * Two α's are printed per scheme because the tier uses two. The declared one is
 * `cssTierOptics`'s, solved at the mapping's fitted `referenceBackdropLuminance`
 * and used wherever nothing was sampled. The one that actually draws on the
 * photo cells is `cssOpticsFromSource`'s, solved at the surface's OWN measured
 * backdrop level — which is the number the ceiling should be declared at, and
 * the reason the two schemes' ceilings are not simply the two `tintAlpha`s.
 *
 * The bound is an upper one and loose in one direction, stated so: `saturate()`
 * is defined on sRGB-ENCODED values while the renderer saturates in linear
 * light, and the plate composite here is also encoded, so the arithmetic above
 * is the linear-light shape of an encoded operation. It bounds; it does not
 * predict. What it is for is the question G3 has to answer before it writes a
 * derived term — whether there is room on this tier for one at all.
 */
import {
  CSS_TIER_MAPPING,
  cssOpticsFromSource,
  cssTierOptics,
  cssTintAlpha,
  sourceOptics,
} from "../../../platform-web/src/optics";
import {
  macos26MaterialProfileDocument,
  macos27MaterialProfileDocument,
} from "../../../platform-web/src/material-document";

/** The photo backdrop's measured interior level per profile, off the committed rows. */
const PHOTO_BACKDROP = [
  ["macOS 27 light 1x", "light", 0.2212],
  ["macOS 27 dark 1x", "dark", 0.23307],
  ["macOS 27 dark 1x (rrect-lg)", "dark", 0.23307],
] as const;

const documents = {
  "macos-27": macos27MaterialProfileDocument,
  "macos-26.5": macos26MaterialProfileDocument,
} as const;

console.log("== the CSS tier's chroma ceiling, ratio (ii) ≤ (1 − α)·s ==\n");
console.log(`saturate() regular = ${String(CSS_TIER_MAPPING.saturation.regular)}, clear = ${String(CSS_TIER_MAPPING.saturation.clear)} (CSS-only, frozen by W31 X3)\n`);

for (const [label, document] of Object.entries(documents)) {
  for (const scheme of ["light", "dark"] as const) {
    const patch = document.active[scheme].patch;
    const mapping = { ...CSS_TIER_MAPPING, ...document.cssTierMapping };
    const source = sourceOptics(patch).regular;
    const declared = cssTierOptics(patch, mapping).regular;
    console.log(`${label} / ${scheme}`);
    console.log(`  renderer tintAlpha            ${source.tintAlpha.toFixed(4)}`);
    console.log(`  cssTintAlpha at the mapping's anchor  ${declared.tintAlpha.toFixed(4)}`);
    console.log(
      `  ceiling at that alpha         ${((1 - declared.tintAlpha) * mapping.saturation.regular).toFixed(4)}`,
    );
    for (const [name, wanted, level] of PHOTO_BACKDROP) {
      if (wanted !== scheme) continue;
      const atLevel = cssOpticsFromSource(declared, source, mapping, {
        toneLevel: level,
        linearMean: level,
      });
      const alpha = atLevel.tintAlpha;
      console.log(
        `  at ${name} (backdrop ${level.toFixed(5)}): α′ ${alpha.toFixed(4)}  →  ceiling ${((1 - alpha) * mapping.saturation.regular).toFixed(4)}`,
      );
    }
    console.log("");
  }
}

// The same number stated the other way: what a retention on the WebGPU tier is
// asking the CSS tier to reach, against what its two layers can carry.
console.log(`
== how to read it ==

  Ratio (ii) is the interior's mean per-pixel chroma over the RAW backdrop's, so
  a ceiling of C says: whatever the material does, this tier's body cannot show
  more than C of the backdrop's chroma. A WebGPU tier fitted to a native ratio
  above C is a fit the CSS tier cannot follow, and the difference is a DECLARED
  RESIDUAL rather than a bug — which is the question G3 decides: derive a term
  from the leaf, or record that this tier carries nothing of the operator.

  The ceiling is not the current reading. The tier draws well BELOW it today,
  because the retention does not exist and the only chroma the body carries is
  what \`saturate()\` left under the plate. The gap between the reading and the
  ceiling is the room a derived term has.
`);
