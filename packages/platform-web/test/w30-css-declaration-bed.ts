/**
 * The bed W30 G2's CSS declaration-identity case is taken on, and the chain that
 * resolves one surface's declarations from a material profile document.
 *
 * Not a test file (the vitest `include` is `test/**\/*.test.ts`): it is the list
 * `w30-css-declaration-identity.test.ts` walks and the list the recorder that
 * produced `w30-css-declarations-pre-leaves.json` walked on the tree as it stood
 * **before** W30 G2's leaves existed. One list, so the pin is a pin on the same
 * surfaces and not on similar ones.
 *
 * The case exists because W30 G2 gives the outer shadow's σ a span law
 * (`MaterialOuterShadow.sigmaSlopePerSpan` and its two siblings, claims §5.156
 * §2) and the CSS tier evaluates that law **per surface**, from `surface.spanPx`,
 * to write one `box-shadow` blur radius. At the inert defaults the law returns
 * `sigmaPx` at every span, so every string this tier emits must be character-
 * identical across the commit — which is what acceptance clause 1 asks for and
 * what a fixture recorded on the pre-leaf tree is the only honest way to say.
 *
 * The sweep is the two macOS 26.5 documents (the frozen bed, X1), both colour
 * schemes, both device ratios, the declared spans of `scenes.json` and the two
 * that bracket them, and three backdrop levels — because the shadow's amplitude
 * is keyed on the backdrop and the blur radius has to be shown unmoved at every
 * amplitude the thin regime resolves, not only at one.
 *
 * ## Two sweeps, two fixtures
 *
 * `sweep()` is the nominal regime and is what
 * `w30-css-declarations-pre-leaves.json` holds. `policySweep()` is the same bed
 * under the reduced-transparency and increased-contrast regimes, added by the
 * review closure (claims §5.158 §8, finding 6) because those are the two paths
 * that fold the material before a declaration is written — `opticsUnderPolicy`
 * scales the blur radius and lifts the occlusion — and a σ law that reached them
 * and not the nominal path would be as much a violation of X1 as one that
 * reached the nominal path. It has its own fixture,
 * `w30-css-declarations-policies-pre-leaves.json`, recorded the same way and for
 * the same reason: on the pre-leaf tree, by checking out
 * `packages/platform-web/src` at `01347a2c` and running the recorder there. The
 * nominal fixture is not re-recorded and does not move.
 */

import { NOMINAL_ACCESSIBILITY_POLICY, resolveAccessibilityPolicy } from "@vitreajs/vitrea";
import type { ResolvedAccessibilityPolicy } from "@vitreajs/vitrea";

import { cssTierDeclarations, type CssTierRender, type CssTierSurface } from "../src/css-tier";
import { macos26MaterialProfileDocument } from "../src/material-document";
import { colorSchemeMaterialProfile } from "../src/color-scheme";
import {
  CSS_TIER_MAPPING,
  cssTierOptics,
  sourceOuterShadow,
  sourceSize,
  type CssTierMapping,
} from "../src/optics";

/**
 * The spans the law is read at: `scenes.json`'s own declared spans (32, 44, 96,
 * 128, 130, 160) with 24 and 320 bracketing them, so the sweep covers a span
 * below every knee the law can carry and one above the bed's largest.
 */
export const SPANS = [24, 32, 44, 64, 96, 128, 130, 160, 220, 320] as const;

/** Three backdrop levels: the thin regime's dark, mid and bright anchors. */
export const BACKDROPS = [0.02, 0.35, 0.89] as const;

export const SCHEMES = ["light", "dark"] as const;

export const RATIOS = [1, 2] as const;

/** One case's identity, so a fixture entry names the surface it came from. */
export const caseKey = (
  scheme: (typeof SCHEMES)[number],
  spanPx: number,
  backdrop: number,
  dpr: number,
): string => `${scheme}/span${String(spanPx)}/bg${String(backdrop)}/dpr${String(dpr)}`;

/**
 * `root.ts`'s chain from a material document to one surface's declarations, in
 * the shipped order and through the shipped functions.
 *
 * Deliberately short of `root.ts`'s full chain: the tone response, the author
 * tint fold and the ink decision are upstream of everything the σ law touches,
 * and a bed that reproduced them would pin them here as well as in the three
 * files that already do. What it does carry in full is every input the outer
 * shadow reads — the profile's own `outerShadow` block, the backdrop luminance
 * the thin regime keys on, the span the thick regime and the new σ law both key
 * on, and the size law's fold — plus the whole of the rest of the record, which
 * is what makes the comparison "every property this tier emits" rather than
 * "the shadow".
 */
export function renderCase(
  scheme: (typeof SCHEMES)[number],
  spanPx: number,
  backdropLuminance: number,
  devicePixelRatio: number,
  policy: ResolvedAccessibilityPolicy = NOMINAL_ACCESSIBILITY_POLICY,
): CssTierRender {
  const patch = colorSchemeMaterialProfile(scheme, macos26MaterialProfileDocument);
  const mapping: CssTierMapping = {
    ...CSS_TIER_MAPPING,
    ...macos26MaterialProfileDocument.cssTierMapping,
  };
  const surface: CssTierSurface = {
    radii: [22, 22, 22, 22],
    optics: cssTierOptics(patch, mapping).regular,
    policy,
    outerShadow: sourceOuterShadow(patch),
    size: sourceSize(patch),
    mapping,
    spanPx,
    extentsCssPx: [spanPx * 2, spanPx],
    backdropLuminance,
    devicePixelRatio,
  };
  return cssTierDeclarations(surface);
}

/** Every string one case emits, flattened so a fixture is a plain record. */
export function declarationsOf(render: CssTierRender): Record<string, string> {
  const out: Record<string, string> = {};
  for (const [property, value] of Object.entries(render.host)) {
    out[`host.${property}`] = value;
  }
  for (const [layer, declarations] of Object.entries(render.layers ?? {})) {
    for (const [property, value] of Object.entries(declarations)) {
      out[`${layer}.${property}`] = value;
    }
  }
  out["render.outerShadow"] = render.outerShadow;
  return out;
}

/** The whole sweep, keyed by `caseKey`. */
export function sweep(): Record<string, Record<string, string>> {
  const out: Record<string, Record<string, string>> = {};
  for (const scheme of SCHEMES) {
    for (const spanPx of SPANS) {
      for (const backdrop of BACKDROPS) {
        for (const dpr of RATIOS) {
          out[caseKey(scheme, spanPx, backdrop, dpr)] = declarationsOf(
            renderCase(scheme, spanPx, backdrop, dpr),
          );
        }
      }
    }
  }
  return out;
}

/**
 * The two accessibility regimes the material folds under before a declaration is
 * written, beside the nominal one the sweep above is taken at.
 *
 * Forced colours is not here: at `glass: "none"` the tier writes the platform's
 * palette and no shadow at all, so it would pin the absence of the thing this
 * bed exists to watch. These two are the regimes that keep the facet and change
 * its arithmetic — `opticsUnderPolicy` scales the blur radius under increased
 * frost and lifts the occlusion under either — which is the path a σ law could
 * reach without touching the nominal one.
 */
export const POLICIES = ["reduced-transparency", "increased-contrast"] as const;

export const policyOf = (name: (typeof POLICIES)[number]): ResolvedAccessibilityPolicy =>
  resolveAccessibilityPolicy({
    reducedTransparency: name === "reduced-transparency",
    reducedMotion: false,
    increasedContrast: name === "increased-contrast",
    forcedColors: false,
    reducedTransparencySupported: true,
  });

/** One policy case's identity — the nominal key with the regime in front of it. */
export const policyCaseKey = (
  policy: (typeof POLICIES)[number],
  scheme: (typeof SCHEMES)[number],
  spanPx: number,
  backdrop: number,
  dpr: number,
): string => `${policy}/${caseKey(scheme, spanPx, backdrop, dpr)}`;

/** The same bed under each regime, keyed by `policyCaseKey`. */
export function policySweep(): Record<string, Record<string, string>> {
  const out: Record<string, Record<string, string>> = {};
  for (const policy of POLICIES) {
    const resolved = policyOf(policy);
    for (const scheme of SCHEMES) {
      for (const spanPx of SPANS) {
        for (const backdrop of BACKDROPS) {
          for (const dpr of RATIOS) {
            out[policyCaseKey(policy, scheme, spanPx, backdrop, dpr)] = declarationsOf(
              renderCase(scheme, spanPx, backdrop, dpr, resolved),
            );
          }
        }
      }
    }
  }
  return out;
}
