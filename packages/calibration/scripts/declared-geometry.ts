/**
 * The declared placement of every scene, on stdout, as JSON.
 *
 * A gate's reader is not always TypeScript — the contour and region instruments
 * under `results/` are Python — and a reader that needs the measured region has
 * two places to get it: the declaration both harnesses lay out from, or the
 * bounds a capture's own report says the surfaces landed at. Only the first is
 * independent of the thing being measured. Taking the second and calling it
 * declared is the failure this command exists to remove: it reads plausibly, it
 * agrees with the declaration whenever nothing is wrong, and on the one run where
 * a surface lands somewhere else it moves the measurement window with the fault
 * and reports no fault.
 *
 * So the declaration is emitted from `resolveScene` — the same function the
 * calibration page places its hosts with, over the same `scenes.json` the SwiftUI
 * harness reads — and a reader compares a report's measured bounds against it
 * rather than trusting either alone. Nothing here restates a geometry value.
 *
 *   tsx scripts/declared-geometry.ts [sceneId...]     # default: every scene
 */

import { CANVAS, SCENE_IDS, resolveScene } from "../web/scenes.ts";

// `resolveScene` reads the reference matrix through a static import, so a probe
// bed pointed at a different scenes file would be silently ignored here while
// every other stage of the pipeline honoured it. Refused rather than mismatched.
if (process.env["VITREA_SCENES"] !== undefined) {
  throw new Error(
    "declared-geometry: VITREA_SCENES is set, but this command reads the reference matrix that " +
      "web/scenes.ts imports. It cannot describe a probe bed.",
  );
}

const requested = process.argv.slice(2);
const unknown = requested.filter((id) => !SCENE_IDS.includes(id));
if (unknown.length > 0) {
  throw new Error(`declared-geometry: not in the scene matrix: ${unknown.join(", ")}`);
}

const scenes = Object.fromEntries(
  (requested.length > 0 ? requested : SCENE_IDS).map((id) => {
    const placed = resolveScene(id);
    return [id, {
      backgroundId: placed.backgroundId,
      pressed: placed.pressed,
      tint: placed.tint ?? null,
      groups: placed.groups,
      // Named `bounds`, in the field names a `SurfaceReport` uses, so a reader
      // compares the two records without a translation step of its own.
      surfaces: placed.surfaces.map((surface) => ({
        nodeId: surface.nodeId,
        groupId: surface.groupId,
        plane: surface.plane,
        family: surface.family,
        radius: surface.radius,
        bounds: {
          x: surface.left,
          y: surface.top,
          width: surface.width,
          height: surface.height,
        },
      })),
    }];
  }),
);

process.stdout.write(`${JSON.stringify({
  source: "apps/reference-apple/scenes.json, placed by web/scenes.ts resolveScene",
  canvas: CANVAS,
  scenes,
}, null, 2)}\n`);
