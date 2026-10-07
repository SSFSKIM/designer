/**
 * **X75 — no shipped material draws opaque glass** (W49 charter Decision Log 3; claims §5.215).
 *
 * The invariant and its arithmetic are `scripts/no-opaque-glass.ts`, which W49a's builder and seal
 * refuse on too. This file reads it over what SHIPS, not over the calibration documents: every
 * endpoint of `SHIPPED_MATERIAL_PROFILE_DOCUMENTS`, each receded patch merged over its own active
 * endpoint as the root poses it (`mergeMaterialProfiles`).
 *
 * 0.28.0 ships one endpoint in violation: the dark `-glass0.25` receded document names `tintAlpha`
 * 0.8 and carries the active's far deltas 0.2 / 0.2 at span tops 160 / 160, so an unfocused window's
 * glass resolves alphaBase above 0.95 from span 140 and 1.0 from 160 CSS px, on both tiers and both
 * scales, and transmits no backdrop at all there (W49 grounding F1; the failing output on 0.28.0 is
 * `results/2026-10-07-w49a-g0-declaration/x75/x75-on-0.28.0-unmarked.txt`). It is marked in
 * `KNOWN_DEFECT` and runs as an expected failure, so the suite stays green while the defect ships
 * and turns red the moment it is repaired: W49a G2 removes the entry with the document that
 * repairs it.
 */
import { describe, expect, it } from "vitest";

import {
  SHIPPED_MATERIAL_PROFILE_DOCUMENTS,
  mergeMaterialProfiles,
  type GlassMaterialProfileDocument,
} from "@vitreajs/vitrea-web";
import type { MaterialProfilePatch } from "@vitrea/renderer-webgpu";

import { opaqueGlassViolations, summariseOpaqueGlass } from "../scripts/no-opaque-glass";

/**
 * Endpoints 0.28.0 ships in violation, each with the wave that repairs it. An entry runs as an
 * expected failure; when its repair lands the case passes, `it.fails` turns that into a failure,
 * and the entry has to come out with the document that repaired it.
 */
const KNOWN_DEFECT: ReadonlyMap<string, string> = new Map([
  ["apple-macos-27.0-glass0.25 dark receded",
    "W49a (the receded far delta, family R): alphaBase 1.0 at span >= 160, both tiers, both scales"],
]);

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

  it("covers twelve endpoints across the three shipped documents, the known defects among them", () => {
    expect(all.map((e) => e.label)).toHaveLength(12);
    for (const label of KNOWN_DEFECT.keys()) expect(all.map((e) => e.label)).toContain(label);
  });

  for (const { label, patch } of all) {
    const defect = KNOWN_DEFECT.get(label);
    const name = defect === undefined ? label : `${label} [known defect, repaired by ${defect}]`;
    (defect === undefined ? it : it.fails)(name, () => {
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
