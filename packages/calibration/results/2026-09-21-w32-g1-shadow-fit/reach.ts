/**
 * W32 G1 — the reach per span, before and after the fit, evaluated through the runtime's own
 * functions so that `clearance.py` can hold it up against the bed's clearance
 * (claims §5.166; W32 acceptance clause 1).
 *
 *   npx tsx results/2026-09-21-w32-g0-exterior-cut/reach.ts > reach.txt
 *
 * W30 G3's `reach-pad.ts` in this directory's own shape and for its reason:
 * every number comes from `outerShadowReachPx`, `outerShadowSigmaPx`,
 * `outerShadowOcclusionAt` and `cssShadowBlurRadius` rather than from a table
 * that reproduces their arithmetic, because a reproduction can disagree with
 * what is drawn. What is new here is only the OUTPUT — a JSON beside the text,
 * so the clearance reader joins to the reach on the span rather than on a
 * transcription — and the question: W30 asked what the padding costs, this asks
 * how much of the reach the capture's frame can see.
 *
 * `reachAt` is the scissor pad the optics pass sizes itself from: the distance
 * at which the composited shadow falls below the renderer's own visibility
 * floor, at that caster's span and its own occlusion. It is the shadow's
 * OUTSIDE edge as the runtime defines it, and it is the quantity the clearance
 * has to hold for the capture to contain the whole exterior.
 *
 * Nothing is fitted and no document moves: the four macOS 27 documents are read
 * off disk and resolved through `withMaterialOverrides` exactly as the runtime
 * resolves them.
 */
import { readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  DEFAULT_MATERIAL_PROFILE,
  outerShadowOcclusionAt,
  outerShadowReachPx,
  outerShadowSigmaPx,
  sizeThickness,
  withMaterialOverrides,
  type MaterialOuterShadow,
  type MaterialProfile,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";
import { cssShadowBlurRadius } from "@vitreajs/vitrea-web";

const HERE = import.meta.dirname;
const PROFILES = resolve(HERE, "..", "..", "profiles");

/** The spans `scenes.json` declares a component at, plus the two the bed gates on. */
const SPANS = [32, 44, 96, 128, 130, 160];

const KEYS = [
  "apple-macos-27.0-1x-light-standard-glass0.5",
  "apple-macos-27.0-1x-dark-standard-glass0.5",
] as const;

function patchOf(key: string): MaterialProfilePatch {
  return (JSON.parse(readFileSync(resolve(PROFILES, `${key}.json`), "utf8")) as {
    patch: MaterialProfilePatch;
  }).patch;
}

function material(key: string): MaterialProfile {
  return withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(key));
}

/** The composition a receded document draws under: the active patch, then the recede. */
function recededMaterial(key: string): MaterialProfile {
  return withMaterialOverrides(material(key), patchOf(`${key}-receded`));
}

function reachAt(shadow: MaterialOuterShadow, span: number, profile: MaterialProfile): number {
  const occlusion = outerShadowOcclusionAt(shadow, 0.5, span, sizeThickness(span, profile), profile);
  return outerShadowReachPx(shadow, occlusion, span);
}

/** The CSS tier's group clip: the blur radius at this span, plus spread and offset. */
function cssClipAt(shadow: MaterialOuterShadow): (span: number) => number {
  return (span) =>
    cssShadowBlurRadius(outerShadowSigmaPx(shadow, span)) + shadow.spreadPx + Math.abs(shadow.offsetPx);
}

const payload: Record<string, Record<string, Record<string, number>>> = {};

console.log("W32 G1 — the reach per span, before and after the fit, from the runtime's own functions");
console.log("=".repeat(120));
console.log();
console.log(`documents  ${PROFILES}`);
console.log(
  "`reach` is `outerShadowReachPx` at that caster's own occlusion — the scissor pad the optics",
);
console.log("pass sizes itself from, and the runtime's own statement of where the shadow ends.");
console.log("`css clip` is the CSS tier's group clip: blur radius + spread + |offset|.");
console.log();

for (const key of KEYS) {
  const profile = material(key);
  const shadow = profile.outerShadow;
  const receded = recededMaterial(key);
  const clip = cssClipAt(shadow);
  payload[key] = {};
  console.log(key);
  console.log(
    `  σ law  sigmaPx ${shadow.sigmaPx}  slope ${shadow.sigmaSlopePerSpan}  ` +
      `ref ${shadow.sigmaSpanRefPx}  thin offset ${shadow.sigmaThinOffsetPx}` +
      `   offsetPx ${shadow.offsetPx}  spreadPx ${shadow.spreadPx}`,
  );
  console.log();
  console.log(
    `  ${"span".padStart(5)}${"occlusion".padStart(11)}${"σ".padStart(9)}${"reach".padStart(9)}` +
      `${"css clip".padStart(10)}${"receded occ".padStart(13)}${"receded reach".padStart(15)}`,
  );
  for (const span of SPANS) {
    const occlusion = outerShadowOcclusionAt(
      shadow,
      0.5,
      span,
      sizeThickness(span, profile),
      profile,
    );
    const recededOcclusion = outerShadowOcclusionAt(
      receded.outerShadow,
      0.5,
      span,
      sizeThickness(span, receded),
      receded,
    );
    const row = {
      occlusion,
      sigma: outerShadowSigmaPx(shadow, span),
      reach: reachAt(shadow, span, profile),
      cssClip: clip(span),
      recededOcclusion,
      recededReach: reachAt(receded.outerShadow, span, receded),
    };
    payload[key]![String(span)] = row;
    console.log(
      `  ${String(span).padStart(5)}${row.occlusion.toFixed(4).padStart(11)}` +
        `${row.sigma.toFixed(2).padStart(9)}${row.reach.toFixed(2).padStart(9)}` +
        `${row.cssClip.toFixed(2).padStart(10)}` +
        `${row.recededOcclusion.toFixed(4).padStart(13)}` +
        `${row.recededReach.toFixed(2).padStart(15)}`,
    );
  }
  console.log();
}

writeFileSync(resolve(HERE, "reach.json"), `${JSON.stringify(payload, null, 1)}\n`);
