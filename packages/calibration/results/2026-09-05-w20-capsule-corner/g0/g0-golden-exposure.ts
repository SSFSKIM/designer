/**
 * W20 G0: which golden scenes the capsule fix, or a change to the Apple
 * reference above its saturation ratio, could move (claims §5.83 section 5).
 *
 * Reads the golden scene list as data — `renderer-webgpu/e2e/fixtures/scenes.ts`
 * is the same module the golden run, the regeneration script and the benchmark
 * read — and for every surface prints the reference it draws under, its declared
 * radius as a fraction of its short side, and what `resolveCorner` gives it. Two
 * separate exposures, and the point of the table is that they are separate:
 *
 *   - **the capsule fix** reaches a surface only if its family is `capsule`;
 *   - **a change to the Apple reference above the ratio** reaches a surface only
 *     if it draws under `apple-continuous` AND its radius exceeds
 *     `APPLE_SATURATION_RADIUS_RATIO` (0.327083) of its short side.
 *
 *     npx tsx results/2026-09-05-w20-capsule-corner/g0/g0-golden-exposure.ts
 *
 * Imported by relative path rather than by package name: this file lives under
 * `@vitrea/calibration`, which does not depend on geometry or on the renderer,
 * and the alternative — adding two dependencies to a package so a one-off
 * exposure listing can resolve them — would put a wave's scratch in the
 * workspace graph.
 */

import {
  APPLE_SATURATION_RADIUS_RATIO,
  assertUniformRadii,
  resolveFromChannels,
} from "../../../../geometry/src/index.ts";

import { ALL_SCENES } from "../../../../renderer-webgpu/e2e/fixtures/scenes.ts";

const rows: string[] = [];
let capsules = 0;
let saturated = 0;

for (const scene of ALL_SCENES) {
  for (const group of scene.groups) {
    for (const surface of group.surfaces) {
      // Exactly what `instances.ts` does: the surface's own reference, or the
      // Apple one by default, and the family carried but never read.
      const reference = surface.reference ?? "apple-continuous";
      const radius = assertUniformRadii(surface.shape.radii);
      const [width, height] = surface.shape.size;
      const shortSide = Math.min(width, height);
      const resolved = resolveFromChannels(surface.shape, reference, surface.family);
      const ratio = radius / shortSide;
      const isCapsule = surface.family === "capsule";
      const clamped = Math.abs(resolved.corner.radius - radius) > 1e-9;
      if (isCapsule) capsules += 1;
      if (clamped) saturated += 1;
      rows.push(
        `${scene.name.padEnd(20)} ${surface.nodeId.padEnd(10)} ` +
          `${`${width}x${height}`.padStart(9)} r ${String(radius).padStart(3)}  ` +
          `r/min ${ratio.toFixed(4)}  ${reference.padEnd(17)} ${surface.family.padEnd(24)} ` +
          `drawn r ${resolved.corner.radius.toFixed(4).padStart(9)}` +
          `${clamped ? "  CLAMPED" : ""}`,
      );
    }
  }
}

process.stdout.write(
  `Apple saturation ratio: ${APPLE_SATURATION_RADIUS_RATIO.toFixed(6)} of the short side\n\n` +
    `${rows.join("\n")}\n\n` +
    `${rows.length} golden surface(s): ${capsules} of family capsule, ` +
    `${saturated} clamped by the reference they draw under.\n`,
);
