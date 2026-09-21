/**
 * W31 G0 — the CSS tier's analytic chroma ceiling, per scheme (claims §5.161 §6).
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
 * The bound is an upper one and loose in one direction, stated so: `saturate()`
 * is defined on sRGB-ENCODED values while the renderer saturates in linear
 * light, and the plate composite here is also encoded, so the arithmetic above
 * is the linear-light shape of an encoded operation. It bounds; it does not
 * predict. What it is for is the question G3 has to answer before it writes a
 * derived term — whether there is room on this tier for one at all.
 *
 * ---------------------------------------------------------------------------
 * **2026-09-21, the review closure (claims §5.161 §11, finding B1): this file
 * did not evaluate the alpha the runtime draws, and is corrected here. Its
 * first output, `css-ceiling.txt`, stands beside this one unmodified.**
 *
 * Two errors, both in the same direction on the light scheme:
 *
 * 1. **The anchor was forced.** `root.ts` (~2683) anchors the conversion on the
 *    surface's OWN measured backdrop only where the linear chain cannot hold the
 *    composite — `!linearChainReaches(cssTierCompositeLevel(interior, level))`.
 *    The first version passed that anchor unconditionally. On the LIGHT photo
 *    cells the composite is 0.58–0.60 against a reach boundary at 0.2424, so the
 *    chain does hold it and the **fitted** anchor is what draws; only the dark
 *    cells, whose composite is 0.067, take the measured one.
 * 2. **The source was unsized.** The runtime solves the conversion from
 *    `shadowedSource`, which has been through `materialAtBackdrop` and therefore
 *    through `sizeOcclusionAlphaAt` — the size law thickens the plate. The first
 *    version passed `sourceOptics(patch).regular` straight through, which is the
 *    material at zero thickness and at no span.
 *
 * So the ceiling is a function of the SPAN, and on the light scheme it is a
 * quarter lower than recorded. The consequence is in the ledger: the light
 * tier's recorded 0.784 was above every reading, and the corrected 0.5654 at
 * span ≥ 96 is BELOW the light CSS tier's own measured ratio (ii) of up to
 * 0.633 — which says plainly that the expression is an upper bound in
 * linear-light shape on an encoded operation, and not a bound the tier obeys.
 * Both numbers are printed per span, beside the first version's, so the reading
 * and its correction sit in one output.
 *
 * The inner shadow's fold (`innerShadowedSourceOptics`) is deliberately not
 * applied: its keep is 0.9964–0.9973 on the probe cells, three parts in a
 * thousand of the level, and it needs a surface's geometry that an analytic
 * ceiling does not have. Naming it is the honest treatment; folding an
 * invented geometry in would not be.
 */
import {
  CSS_TIER_MAPPING,
  cssOpticsFromSource,
  cssTierCompositeLevel,
  cssTierOptics,
  linearChainQuantumCodes,
  linearChainReaches,
  sizeOcclusionAlpha,
  sourceOptics,
  sourceSize,
} from "../../../platform-web/src/optics";
import {
  macos26MaterialProfileDocument,
  macos27MaterialProfileDocument,
} from "../../../platform-web/src/material-document";

/** The photo backdrop's measured interior level per scheme, off the committed rows. */
const PHOTO_BACKDROP = { light: 0.2212, dark: 0.23307 } as const;

/**
 * The bed's declared spans, off `scenes.json`: `capsule-button` is 44 and every
 * larger component is at or past `sizeSpanMax` (96), where the size law's
 * thickness saturates and one row covers `rrect-md`, `rrect-ml` and `rrect-lg`.
 */
const SPANS = [
  [44, "capsule-button"],
  [96, "rrect-md"],
  [128, "rrect-ml"],
  [160, "rrect-lg"],
] as const;

const documents = {
  "macos-27": macos27MaterialProfileDocument,
  "macos-26.5": macos26MaterialProfileDocument,
} as const;

/** Where `linearChainReaches` turns over, bisected rather than asserted. */
function reachBoundary(): number {
  let below = 0;
  let above = 1;
  for (let step = 0; step < 80; step += 1) {
    const mid = (below + above) / 2;
    if (linearChainQuantumCodes(mid) > 1) below = mid;
    else above = mid;
  }
  return above;
}

console.log("== the CSS tier's chroma ceiling, ratio (ii) ≤ (1 − α)·s ==\n");
console.log(`saturate() regular = ${String(CSS_TIER_MAPPING.saturation.regular)}, clear = ${String(CSS_TIER_MAPPING.saturation.clear)} (CSS-only, frozen by W31 X3)`);
console.log(`the linear chain holds a composite at or above ${reachBoundary().toFixed(6)}; below that the conversion anchors on the surface's own backdrop\n`);

for (const [label, document] of Object.entries(documents)) {
  for (const scheme of ["light", "dark"] as const) {
    const patch = document.active[scheme].patch;
    const mapping = { ...CSS_TIER_MAPPING, ...document.cssTierMapping };
    const size = sourceSize(patch);
    const source = sourceOptics(patch).regular;
    const declared = cssTierOptics(patch, mapping).regular;
    const level = PHOTO_BACKDROP[scheme];
    console.log(`${label} / ${scheme}  (photo backdrop ${level.toFixed(5)})`);
    console.log(`  renderer tintAlpha                     ${source.tintAlpha.toFixed(4)}`);
    console.log(`  cssTintAlpha at the mapping's anchor   ${declared.tintAlpha.toFixed(4)}  →  ceiling ${((1 - declared.tintAlpha) * mapping.saturation.regular).toFixed(4)}`);
    // The first version's row, kept so the correction is visible in one place:
    // the unsized source with the measured anchor forced on.
    const forced = cssOpticsFromSource(declared, source, mapping, {
      toneLevel: level,
      linearMean: level,
    });
    console.log(
      `  2026-09-21 first reading (unsized, anchor forced): α′ ${forced.tintAlpha.toFixed(4)}  →  ceiling ${((1 - forced.tintAlpha) * mapping.saturation.regular).toFixed(4)}   [SUPERSEDED — see the module note]`,
    );
    for (const [span, component] of SPANS) {
      const sized = { ...source, tintAlpha: sizeOcclusionAlpha(source.tintAlpha, span, size) };
      // `addedLight` is the rim band's contribution to the interior and is left
      // at 0: it only raises the composite, so it can move a surface from below
      // the reach to above it and never the other way. The light cells sit at
      // 0.58 and the dark ones at 0.067 against a boundary of 0.2424, so no
      // value of it reaches either decision.
      const composite = cssTierCompositeLevel(
        { tintAlpha: sized.tintAlpha, tint: sized.tint, addedLight: 0 },
        level,
      );
      const reaches = linearChainReaches(composite);
      const optics = cssOpticsFromSource(
        declared,
        sized,
        mapping,
        reaches ? undefined : { toneLevel: level, linearMean: level },
      );
      const ceiling = (1 - optics.tintAlpha) * mapping.saturation.regular;
      console.log(
        `  span ${String(span).padStart(3)} (${component.padEnd(14)}) sizedAlpha ${sized.tintAlpha.toFixed(4)}` +
          `  composite ${composite.toFixed(4)}  anchor ${reaches ? "fitted  " : "measured"}` +
          `  α′ ${optics.tintAlpha.toFixed(4)}  →  ceiling ${ceiling.toFixed(4)}`,
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

  **Corrected 2026-09-21 (claims §5.161 §11, B1): the expression is a bound on
  the DARK scheme and is not one on the light scheme.** The light tier's
  measured ratio (ii) runs 0.403–0.633 against a corrected ceiling of 0.5995
  (span 44) and 0.5654 (span ≥ 96), so the tier already draws THROUGH it — which
  is what "the linear-light shape of an encoded operation" means when the
  attenuation is weak and \`saturate()\` is strong. On the dark scheme the
  attenuation dominates: the tier reads 0.18–0.24 against a ceiling of 0.2767 /
  0.2651 and a reference of 0.90–0.92, so the ceiling binds there and the
  residual it leaves is real.

  What that changes for G3: there is no measurable room for a derived term on
  the LIGHT scheme — the authored \`saturate()\` has already spent it — and there
  is at most ~30 % of the reference's body chroma to be had on the DARK one.
`);
