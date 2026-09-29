/**
 * W42 G0 rehearsal round 2 (item (c)): the author-tint composite's constants, resolved from THIS
 * worktree's material code for the four macOS 27 endpoints, so `tint.py` can evaluate
 * `tintedMaterialColour` (material.ts) exactly instead of a per-cell fit.
 *
 *   pnpm exec tsx results/2026-09-29-w42-g0-declaration/gate/rehearsal/tint-resolve.ts > tint-resolved.json
 */
import { DEFAULT_MATERIAL_PROFILE, withMaterialOverrides } from "../../../../../renderer-webgpu/src/material.ts";
import {
  macos27LightMaterialProfile,
  macos27DarkMaterialProfile,
  macos27RecededMaterialProfile,
} from "../../../../../platform-web/src/macos27-profile.ts";

const lightActive = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, macos27LightMaterialProfile as never);
const darkActive = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, macos27DarkMaterialProfile as never);
const endpoints = {
  "light-active": lightActive,
  "light-receded": withMaterialOverrides(lightActive, macos27RecededMaterialProfile.light as never),
  "dark-active": darkActive,
  "dark-receded": withMaterialOverrides(darkActive, macos27RecededMaterialProfile.dark as never),
};
const out: Record<string, unknown> = {};
for (const [name, m] of Object.entries(endpoints)) {
  out[name] = {
    tintShadeDark: m.tintShadeDark, tintShadeLight: m.tintShadeLight,
    tintShadeStrength: m.tintShadeStrength, tintChromaScale: m.tintChromaScale ?? 1,
    tintShadeCollapseRetention: m.tintShadeCollapseRetention ?? 0,
  };
}
process.stdout.write(`${JSON.stringify(out, null, 1)}\n`);
