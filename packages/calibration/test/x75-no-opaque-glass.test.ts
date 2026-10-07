/**
 * **X75 — no shipped material draws opaque glass** (W49 charter Decision Log 3; claims §5.215).
 *
 * The invariant and its arithmetic are `scripts/no-opaque-glass.ts`, which W49a's builder and seal
 * refuse on too. This file reads it over what SHIPS, not over the calibration documents: every
 * endpoint of `SHIPPED_MATERIAL_PROFILE_DOCUMENTS`, each receded patch merged over its own active
 * endpoint as the root poses it (`mergeMaterialProfiles`).
 *
 * 0.28.0's dark `-glass0.25` receded endpoint violated this bound: tintAlpha 0.8 plus the inherited
 * far deltas 0.2 / 0.2 made it opaque at span 160 (W49 grounding F1; the failing output is
 * `results/2026-10-07-w49a-g0-declaration/x75/x75-on-0.28.0-unmarked.txt`). W49a Decision Log 9
 * seals its own far deltas at 0.10 / 0.10, so its thick alphaBase is 0.9. The expected-failure
 * exception is removed with that seal: every shipped endpoint must now pass, without exemptions.
 */
import { describe, expect, it } from "vitest";

import {
  SHIPPED_MATERIAL_PROFILE_DOCUMENTS,
  mergeMaterialProfiles,
  type GlassMaterialProfileDocument,
} from "@vitreajs/vitrea-web";
import type { MaterialProfilePatch } from "@vitrea/renderer-webgpu";

import { opaqueGlassViolations, summariseOpaqueGlass } from "../scripts/no-opaque-glass";

function endpoints(document: GlassMaterialProfileDocument) {
  return (["light", "dark"] as const).flatMap((scheme) => [
    { label: `${document.name} ${scheme} active`, patch: document.active[scheme].patch },
    {
      label: `${document.name} ${scheme} receded`,
      patch: mergeMaterialProfiles(document.active[scheme].patch, document.receded[scheme].patch),
    },
  ]);
}

describe("X75: no shipped endpoint resolves alphaBase above 0.95 (W49 Decision Log 3)", () => {
  const all = SHIPPED_MATERIAL_PROFILE_DOCUMENTS.flatMap(endpoints);

  it("covers twelve endpoints across the three shipped documents", () => {
    expect(all.map((e) => e.label)).toHaveLength(12);
  });

  for (const { label, patch } of all) {
    it(label, () => {
      expect(summariseOpaqueGlass(opaqueGlassViolations(patch as MaterialProfilePatch)), label)
        .toEqual([]);
    });
  }

  it("is not vacuous: a synthetic endpoint past the bound fails on both tiers, and only where it is", () => {
    const found = opaqueGlassViolations({ optics: { regular: { tintAlpha: 0.8 } }, tintAlphaFar1x: 0.2 });
    expect(new Set(found.map((v) => v.tier))).toEqual(new Set(["webgpu", "css"]));
    expect(found.every((v) => v.dpr === 1 && v.variant === "regular")).toBe(true);
    // At the bound itself: 0.8 + 0.15 is 0.95 at full far weight and is admitted.
    expect(opaqueGlassViolations({ optics: { regular: { tintAlpha: 0.8 } }, tintAlphaFar1x: 0.15,
      tintAlphaFar2x: 0.15 })).toEqual([]);
  });
});
