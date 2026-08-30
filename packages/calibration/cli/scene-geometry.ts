/**
 * The scene matrix's geometry, read once for every CLI that needs it.
 *
 * `apps/reference-apple/scenes.json` is the file both harnesses lay out from,
 * and from schema 5 it is also what the instrument bounds its search to — the
 * shape axis extracts inside the declared region and the shadow axis profiles
 * outward from its contour (wave Decision Log 15). Three CLIs need that region
 * and none of them may derive it differently, so the resolution lives here:
 * `measure` through `compare` and `diff`, and `tier-delta`, which masks its
 * interior levels with the same region for the same reason.
 *
 * Nothing here restates a geometry value. The declaration is read, placed by
 * `placeComponent`, and rasterised; a component kind this build has no geometry
 * for is refused rather than approximated.
 */

import { existsSync, readFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  componentRegion,
  type CanvasSize,
  type ComponentRegion,
  type DeclaredComponent,
} from "../src/index";

export interface SceneGeometryEntry {
  readonly id: string;
  readonly component: string;
}

export interface SceneGeometryMatrix {
  readonly canvas: CanvasSize;
  readonly components: Readonly<Record<string, DeclaredComponent>>;
  readonly scenes: readonly SceneGeometryEntry[];
}

export function readSceneGeometry(referenceRoot: string): SceneGeometryMatrix {
  const path = resolve(referenceRoot, "scenes.json");
  if (!existsSync(path)) {
    throw new Error(`scene geometry: ${path} does not exist.`);
  }
  return JSON.parse(readFileSync(path, "utf8")) as SceneGeometryMatrix;
}

/** The declared component behind a scene id, refusing an unresolvable one. */
export function declaredComponentOf(
  matrix: SceneGeometryMatrix,
  sceneId: string,
): DeclaredComponent {
  const scene = matrix.scenes.find((entry) => entry.id === sceneId);
  if (scene === undefined) {
    throw new Error(`scene geometry: scenes.json declares no scene '${sceneId}'.`);
  }
  const component = matrix.components[scene.component];
  if (component === undefined) {
    throw new Error(
      `scene geometry: scene '${sceneId}' names component '${scene.component}', which the matrix lacks.`,
    );
  }
  return component;
}

/** The declared search region for one scene, at one backing scale and capture size. */
export function componentRegionFor(
  matrix: SceneGeometryMatrix,
  sceneId: string,
  options: { readonly scale: number; readonly width: number; readonly height: number; readonly marginPx?: number },
): ComponentRegion {
  return componentRegion(declaredComponentOf(matrix, sceneId), {
    canvas: matrix.canvas,
    scale: options.scale,
    width: options.width,
    height: options.height,
    ...(options.marginPx === undefined ? {} : { marginPx: options.marginPx }),
  });
}
