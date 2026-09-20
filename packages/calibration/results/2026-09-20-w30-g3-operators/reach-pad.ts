/**
 * W30 G3 (c), contract X8 and Decision Log 2 (c) — the padding, recomputed from
 * the fitted σ law and recorded on both sides.
 *
 *   npx tsx results/2026-09-20-w30-g3-operators/reach-pad.ts > reach-pad.txt
 *
 * W30 G0's `reach-table.ts` asked what a span-graded σ WOULD imply and varied
 * `sigmaPx` by hand to ask it. This file asks what the sealed documents DO imply
 * and varies nothing: it reads the four macOS 27 documents off disk, resolves
 * each through the renderer's own `withMaterialOverrides`, and computes every
 * number through the renderer's and the web tier's own functions — the scissor
 * pad through `outerShadowReachPx`, the CSS tier's group clip through
 * `outerShadowSigmaPx` and `cssShadowBlurRadius`, and the backdrop sampling pad
 * through `samplingPaddingFor`. A table that reproduced their arithmetic could
 * disagree with what is actually drawn, which is the failure this shape exists
 * to prevent.
 *
 * **The recomputation is two-sided** (Decision Log 2 (c)). The shipped σ is
 * 4.2–7.2 times too wide below span 96 and about a third too NARROW at 128 and
 * above, so the σ law shrinks the pad at the thin spans and grows it at the
 * thick ones. Both directions are recorded, the smallest pad each law produces
 * and the largest, because the shrink is what can expose a sampling floor and
 * the growth is a cost on a facet already at 3.2× the frame's GPU time.
 *
 * **The group readers are bounds, and the table says so by computing them as
 * bounds**: the optics pass takes the max over the group's members of the
 * occlusion and, separately, of the span; the CSS group clip takes the law at
 * the widest carried cast. Neither is any member's value and both contain every
 * member's, exactly while `sigmaSlopePerSpan ≥ 0` — which this file asserts on
 * the sealed documents rather than assuming, because a negative slope would
 * invert the bound (claims §5.158 §8, finding 4).
 */
import { readFileSync } from "node:fs";
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
import { cssShadowBlurRadius, samplingPaddingFor } from "@vitreajs/vitrea-web";
import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";

/*
 * Two document sets: the one whose padding is being recorded, and the one it is
 * recorded against. The first defaults to the committed `profiles/` — the sealed
 * documents — and the second must be named, because the "before" state is the
 * 0.19.0 documents and after the seal they exist only in git. `reach-pad.txt`
 * names both in its own first line, so the table cannot be read as a comparison
 * against something it was not taken against.
 */
const PROFILES =
  process.argv[2] === undefined
    ? resolve(import.meta.dirname, "..", "..", "profiles")
    : resolve(process.cwd(), process.argv[2]);
const BEFORE = process.argv[3] === undefined ? undefined : resolve(process.cwd(), process.argv[3]);

const SPANS = [32, 44, 64, 96, 128, 130, 160, 220];

function material(key: string, directory: string = PROFILES): MaterialProfile {
  const patch = (JSON.parse(readFileSync(resolve(directory, `${key}.json`), "utf8")) as {
    patch: MaterialProfilePatch;
  }).patch;
  return withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patch);
}

/** The composition a receded document draws under: the active patch, then the recede. */
function recededMaterial(activeKey: string): MaterialProfile {
  const active = (JSON.parse(readFileSync(resolve(PROFILES, `${activeKey}.json`), "utf8")) as {
    patch: MaterialProfilePatch;
  }).patch;
  const receded = (JSON.parse(
    readFileSync(resolve(PROFILES, `${activeKey}-receded.json`), "utf8"),
  ) as { patch: MaterialProfilePatch }).patch;
  return withMaterialOverrides(withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, active), receded);
}

/** The reach the optics pass sizes its scissor from, at one caster's own span. */
function reachAt(shadow: MaterialOuterShadow, span: number, profile: MaterialProfile): number {
  const occlusion = outerShadowOcclusionAt(shadow, 0.5, span, sizeThickness(span, profile), profile);
  return outerShadowReachPx(shadow, occlusion, span);
}

/** The CSS tier's group clip: the blur radius at this span, plus spread and offset. */
function cssClipAt(shadow: MaterialOuterShadow, span: number): number {
  return (
    cssShadowBlurRadius(outerShadowSigmaPx(shadow, span)) +
    shadow.spreadPx +
    Math.abs(shadow.offsetPx)
  );
}

console.log(
  `documents  ${PROFILES}\nagainst    ${BEFORE ?? "the same documents with the σ law neutralised"}`,
);
console.log();

for (const key of [
  "apple-macos-27.0-1x-light-standard-glass0.5",
  "apple-macos-27.0-1x-dark-standard-glass0.5",
]) {
  const profile = material(key);
  const shadow = profile.outerShadow;
  if (!(shadow.sigmaSlopePerSpan >= 0)) {
    throw new Error(
      `${key}: sigmaSlopePerSpan is ${String(shadow.sigmaSlopePerSpan)}, and a group's ` +
        `reach(max occlusion, max span) is a bound on every member's only while it is >= 0`,
    );
  }
  const beforeProfile = BEFORE === undefined ? profile : material(key, BEFORE);
  const before: MaterialOuterShadow =
    BEFORE === undefined
      ? { ...shadow, sigmaSlopePerSpan: 0, sigmaThinOffsetPx: 0, sigmaSpanRefPx: 0 }
      : beforeProfile.outerShadow;
  console.log(key);
  console.log(
    `  σ law  sigmaPx ${shadow.sigmaPx}  slope ${shadow.sigmaSlopePerSpan}  ` +
      `ref ${shadow.sigmaSpanRefPx}  thin offset ${shadow.sigmaThinOffsetPx}  ` +
      `(knee ${
        shadow.sigmaSlopePerSpan === 0
          ? "none — a flat law has no knee"
          : `${(shadow.sigmaSpanRefPx + shadow.sigmaThinOffsetPx / shadow.sigmaSlopePerSpan).toFixed(2)} CSS px`
      })`,
  );
  console.log(`  offsetPx ${shadow.offsetPx}  spreadPx ${shadow.spreadPx}`);
  console.log();
  console.log(
    `  ${"span".padStart(5)}${"occlusion".padStart(11)}` +
      `${"σ before".padStart(10)}${"reach".padStart(9)}` +
      `${"σ after".padStart(10)}${"reach".padStart(9)}${"Δ".padStart(9)}${"Δ %".padStart(9)}` +
      `${"css clip before".padStart(17)}${"after".padStart(9)}`,
  );
  const reaches: number[] = [];
  for (const span of SPANS) {
    const wasReach = reachAt(before, span, beforeProfile);
    const isReach = reachAt(shadow, span, profile);
    reaches.push(isReach);
    console.log(
      `  ${String(span).padStart(5)}` +
        `${outerShadowOcclusionAt(shadow, 0.5, span, sizeThickness(span, profile), profile).toFixed(4).padStart(11)}` +
        `${outerShadowSigmaPx(before, span).toFixed(2).padStart(10)}${wasReach.toFixed(2).padStart(9)}` +
        `${outerShadowSigmaPx(shadow, span).toFixed(2).padStart(10)}${isReach.toFixed(2).padStart(9)}` +
        `${(isReach - wasReach).toFixed(2).padStart(9)}` +
        `${(((isReach - wasReach) / wasReach) * 100).toFixed(1).padStart(9)}` +
        `${cssClipAt(before, span).toFixed(2).padStart(17)}${cssClipAt(shadow, span).toFixed(2).padStart(9)}`,
    );
  }
  console.log();
  console.log(
    `  smallest pad the law produces over the bed's spans ${Math.min(...reaches).toFixed(2)} ` +
      `CSS px (span ${String(SPANS[reaches.indexOf(Math.min(...reaches))])}), ` +
      `largest ${Math.max(...reaches).toFixed(2)} (span ${String(SPANS[reaches.indexOf(Math.max(...reaches))])})`,
  );
  console.log();

  // The receded pose draws the same σ law — the recede names no σ leaf, so it
  // inherits the active document's — with its own amplitudes.
  const receded = recededMaterial(key);
  console.log(`  ${key}-receded, which inherits the σ law and carries its own anchors`);
  console.log(
    `  ${"span".padStart(5)}${"occlusion".padStart(11)}${"σ".padStart(9)}${"reach".padStart(9)}`,
  );
  for (const span of SPANS) {
    console.log(
      `  ${String(span).padStart(5)}` +
        `${outerShadowOcclusionAt(receded.outerShadow, 0.5, span, sizeThickness(span, receded), receded).toFixed(4).padStart(11)}` +
        `${outerShadowSigmaPx(receded.outerShadow, span).toFixed(2).padStart(9)}` +
        `${reachAt(receded.outerShadow, span, receded).toFixed(2).padStart(9)}`,
    );
  }
  console.log();

  /*
   * A group's bound, shown to be one. Three members at 44, 96 and 160 CSS px:
   * the reach at the maxima has to contain each member's own.
   */
  const members = [44, 96, 160];
  const perMember = members.map((span) => reachAt(shadow, span, profile));
  const maxOcclusion = Math.max(
    ...members.map((span) =>
      outerShadowOcclusionAt(shadow, 0.5, span, sizeThickness(span, profile), profile),
    ),
  );
  const bound = outerShadowReachPx(shadow, maxOcclusion, Math.max(...members));
  console.log(
    `  the group bound: members ${members.join(", ")} reach ` +
      `${perMember.map((r) => r.toFixed(2)).join(", ")}; ` +
      `reach(max occlusion ${maxOcclusion.toFixed(4)}, max span ${Math.max(...members)}) = ` +
      `${bound.toFixed(2)}  ${bound >= Math.max(...perMember) ? "BOUNDS" : "DOES NOT BOUND"} ` +
      `every member`,
  );
  console.log();
}

console.log("The backdrop sampling pad, which the σ law does not reach");
console.log(
  "  `samplingPaddingFor` is 3σ of the BACKDROP blur, not of the shadow, so a span-graded",
);
console.log(
  "  shadow moves no part of it. Printed because X8 asks for the pads and a pad that did",
);
console.log("  not move is a reading too.");
console.log();
{
  const policy = NOMINAL_ACCESSIBILITY_POLICY.material;
  for (const key of [
    "apple-macos-27.0-1x-light-standard-glass0.5",
    "apple-macos-27.0-1x-dark-standard-glass0.5",
  ]) {
    const document = JSON.parse(readFileSync(resolve(PROFILES, `${key}.json`), "utf8")) as {
      patch: MaterialProfilePatch;
      cssTierMapping?: Record<string, unknown>;
    };
    for (const members of [[[120, 44]], [[160, 96]], [[220, 160]]] as const) {
      console.log(
        `  ${key.replace("apple-macos-27.0-1x-", "").padEnd(24)} members ` +
          `${JSON.stringify(members).padEnd(14)} pad ` +
          `${samplingPaddingFor({
            members: members as unknown as readonly (readonly [number, number])[],
            material: policy,
            profile: document.patch as never,
            cssTierMapping: document.cssTierMapping as never,
          }).toFixed(2)} CSS px`,
      );
    }
  }
}
