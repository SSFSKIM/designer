/**
 * W30 G0 (b) — the reach the shipped σ implies, against the reach a span-graded
 * σ implies, at every span the bed carries.
 *
 *   npx tsx results/2026-09-20-w30-g0-cut/reach-table.ts > reach-table.txt
 *
 * Computed through the renderer's OWN `outerShadowReachPx` and
 * `outerShadowOcclusionAt` rather than by reproducing their arithmetic, so the
 * table cannot disagree with what the scissor and the sampling pad are actually
 * sized from. The only thing varied is `sigmaPx`; the occlusion anchors, the
 * offset and the spread are the shipped macOS 27 document's, because the reach
 * is a joint function of σ and the amplitude and this table is about σ.
 *
 * `outerShadowReachPx` is a function of CSS px and takes no dpr, so a σ law
 * stated in CSS px gives one reach at both scales. That is a consequence of the
 * cut's verdict rather than an assumption, so the device-px alternative the
 * charter asked to be tested is printed beside it: what a floor held constant in
 * DEVICE px would imply at dpr 2, which is the column the rejected hypothesis
 * would have made the padding carry.
 */
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  outerShadowOcclusionAt,
  outerShadowReachPx,
  sizeThickness,
  withMaterialOverrides,
  type MaterialOuterShadow,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

const PROFILES = resolve(import.meta.dirname, "..", "..", "profiles");

function documentShadow(key: string): { shadow: MaterialOuterShadow; sigmaPx: number } {
  const patch = (JSON.parse(readFileSync(resolve(PROFILES, `${key}.json`), "utf8")) as {
    patch: MaterialProfilePatch;
  }).patch;
  const material = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
  return { shadow: material.outerShadow, sigmaPx: material.outerShadow.sigmaPx };
}

const SPANS = [32, 44, 96, 128, 130, 160];

/**
 * The bed's own median native σ per span, from `shadow-cut.py`'s pooled table
 * (§3), on the 1x light bed — the bed with the most cells at every span. The
 * thin entries are the readings the cut rules INSTRUMENT-limited and they are
 * carried here as what the law would have to produce, not as a fit.
 */
const NATIVE_SIGMA_CSS: Record<number, number> = {
  32: 2.63,
  44: 1.52,
  96: 8.8,
  128: 13.14,
  130: 13.36,
  160: 17.3,
};

/** σ_css = 0.133 · (span − 30), clamped below at a floor — the shape G0 names. */
const lawSigma = (span: number, floorCss: number): number =>
  Math.max(floorCss, 0.1329 * span - 3.937);

function reachAt(shadow: MaterialOuterShadow, sigmaPx: number, span: number): number {
  // The deepest amplitude the bed reaches at this span: the mid-plateau thin
  // anchor blended into the thick law by the surface's own size thickness,
  // which is what `renderer.ts` resolves before it asks for a reach.
  const occlusion = outerShadowOcclusionAt(shadow, 0.5, span, sizeThickness(span));
  // The span is stated rather than defaulted, because `outerShadowReachPx` now
  // requires one (claims §5.158 §8, finding 4). The table's own numbers do not
  // move: this file varies `sigmaPx` directly, and the two shipped documents
  // carry `sigmaSlopePerSpan` 0, so the law returns that `sigmaPx` at every span
  // and `reach-table.txt` is byte-identical to the run G0 recorded.
  return outerShadowReachPx({ ...shadow, sigmaPx }, occlusion, span);
}

for (const key of [
  "apple-macos-27.0-1x-light-standard-glass0.5",
  "apple-macos-27.0-1x-dark-standard-glass0.5",
]) {
  const { shadow, sigmaPx } = documentShadow(key);
  console.log(key);
  console.log(
    `  shipped sigmaPx ${sigmaPx}, offsetPx ${shadow.offsetPx}, spreadPx ${shadow.spreadPx}; ` +
      `thick anchors ${shadow.thickOcclusionAt96} / ${shadow.thickOcclusionAt128} / ` +
      `${shadow.thickOcclusionAt160}, thin mid ${shadow.thinOcclusionMid}`,
  );
  console.log();
  console.log(
    `  ${"span".padStart(5)}${"occlusion".padStart(11)}${"σ shipped".padStart(11)}` +
      `${"reach".padStart(9)}${"σ native".padStart(10)}${"reach".padStart(9)}` +
      `${"σ law/1.8".padStart(11)}${"reach".padStart(9)}${"Δ reach".padStart(10)}`,
  );
  for (const span of SPANS) {
    const occlusion = outerShadowOcclusionAt(shadow, 0.5, span, sizeThickness(span));
    const shipped = reachAt(shadow, sigmaPx, span);
    const native = NATIVE_SIGMA_CSS[span] as number;
    const law = lawSigma(span, 1.8);
    console.log(
      `  ${String(span).padStart(5)}${occlusion.toFixed(4).padStart(11)}` +
        `${sigmaPx.toFixed(2).padStart(11)}${shipped.toFixed(2).padStart(9)}` +
        `${native.toFixed(2).padStart(10)}${reachAt(shadow, native, span).toFixed(2).padStart(9)}` +
        `${law.toFixed(2).padStart(11)}${reachAt(shadow, law, span).toFixed(2).padStart(9)}` +
        `${(reachAt(shadow, law, span) - shipped).toFixed(2).padStart(10)}`,
    );
  }
  console.log();
}

console.log("The device-px alternative, at dpr 2 — the hypothesis the cut rejects");
console.log(
  "  A floor held constant in DEVICE px is a floor that HALVES in CSS px at dpr 2, so the",
);
console.log(
  "  reach below is what the padding would carry on a 2x display if the thin regime were",
);
console.log("  device-px constant at the 1x reading of 1.8 CSS px (= 1.8 device px).");
console.log();
{
  const { shadow } = documentShadow("apple-macos-27.0-1x-light-standard-glass0.5");
  console.log(
    `  ${"span".padStart(5)}${"σ css floor".padStart(13)}${"reach".padStart(9)}` +
      `${"σ dev floor @2x".padStart(17)}${"reach".padStart(9)}`,
  );
  for (const span of SPANS) {
    const css = lawSigma(span, 1.8);
    const dev = lawSigma(span, 0.9);
    console.log(
      `  ${String(span).padStart(5)}${css.toFixed(2).padStart(13)}` +
        `${reachAt(shadow, css, span).toFixed(2).padStart(9)}` +
        `${dev.toFixed(2).padStart(17)}${reachAt(shadow, dev, span).toFixed(2).padStart(9)}`,
    );
  }
}
