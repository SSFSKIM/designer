/**
 * The canonical scene matrix, as the web side reads it.
 *
 * Every number here comes out of `apps/reference-apple/scenes.json` — the file
 * the native SwiftUI harness reads too. Nothing in this module restates a
 * geometry value, and that is the whole point: the diff between the two captures
 * is only a statement about *material* if the two sides provably placed the same
 * shape at the same place. Two hand-kept copies of a rect would drift, and the
 * drift would be indistinguishable from a fidelity finding.
 *
 * What this module *does* own is the translation from the scene matrix's
 * declarative shape specs to DOM placement, which is the one thing SwiftUI does
 * implicitly (a `ZStack` centres its children) and the DOM does not.
 */

import { DEFAULT_GROUP_SAMPLING } from "@vitrea/core";
import type { ShapeFamily } from "@vitrea/geometry";
import type { GlassPlane } from "@vitrea/platform-web";

// Vite resolves this through `server.fs.allow`; it is the native harness's own
// file, not a copy. See `vite.config.ts`.
import matrix from "../../../apps/reference-apple/scenes.json";

export interface CanvasSize {
  readonly width: number;
  readonly height: number;
}

interface ShapeSpec {
  readonly kind: string;
  readonly size: readonly [number, number];
  readonly radius?: number;
  readonly offset?: readonly [number, number];
}

interface GroupSpec {
  readonly kind: "group";
  readonly items: readonly ShapeSpec[];
  readonly spacing: number;
}

interface StackSpec {
  readonly kind: "stack";
  readonly base: ShapeSpec;
  readonly over: ShapeSpec;
}

type ComponentSpec = ShapeSpec | GroupSpec | StackSpec;

export interface SceneEntry {
  readonly id: string;
  readonly background: string;
  readonly component: string;
  readonly state: string;
}

/** One glass surface, placed in viewport CSS px, ready for `registerHost`. */
export interface PlacedSurface {
  readonly nodeId: string;
  readonly groupId: string;
  readonly plane: GlassPlane;
  readonly family: ShapeFamily;
  readonly left: number;
  readonly top: number;
  readonly width: number;
  readonly height: number;
  /** Uniform, per X8's v1 restriction. A capsule's is half its short side. */
  readonly radius: number;
}

/**
 * How a group samples its backdrop.
 *
 * `texture` hands the renderer the background raster itself, which is what makes
 * the GPU tier's `samplingBackend: "gpu-texture"` and `refraction: "true"` an
 * honest description of these scenes: the raster *is* the entire content behind
 * the glass, and the app owns it.
 *
 * `dom` is reserved for the one surface that must sample something the app does
 * not own a texture of — see `glass-over-glass` below.
 */
export type GroupSource = "texture" | "dom";

export interface PlacedGroup {
  readonly id: string;
  readonly source: GroupSource;
  /** `GlassEffectContainer(spacing:)`'s counterpart. Absent means the default. */
  readonly mergeDistance?: number;
  /**
   * What the matrix declared, when it differs from `mergeDistance`.
   *
   * Present only where X1's floor moved the number, so the cell descriptor can
   * say that the web side unioned at a distance the scene did not ask for
   * instead of implying the two containers agreed.
   */
  readonly declaredSpacing?: number;
}

export interface PlacedScene {
  readonly scene: SceneEntry;
  readonly canvas: CanvasSize;
  readonly backgroundId: string;
  readonly pressed: boolean;
  readonly groups: readonly PlacedGroup[];
  readonly surfaces: readonly PlacedSurface[];
}

const components = matrix.components as unknown as Record<string, ComponentSpec>;
const scenes = matrix.scenes as readonly SceneEntry[];

export const CANVAS: CanvasSize = matrix.canvas;

export const SCENE_IDS: readonly string[] = scenes.map((entry) => entry.id);

/**
 * A capsule's corner radius is half its short side — the value that makes the
 * shape a stadium, which is what `Capsule()` draws. Derived rather than declared
 * because `scenes.json` gives capsules no radius: for a capsule there is only
 * one, and a second copy of it here could disagree with the native side's.
 */
const radiusOf = (spec: ShapeSpec): number =>
  spec.kind === "capsule" ? Math.min(spec.size[0], spec.size[1]) / 2 : (spec.radius ?? 0);

const familyOf = (spec: ShapeSpec): ShapeFamily =>
  spec.kind === "capsule" ? "capsule" : "fixed-rounded-rect";

/**
 * Centre a box in the canvas, then apply the scene's own offset.
 *
 * This is `ZStack`'s default alignment, spelled out. `Math.round` matches
 * SwiftUI laying out on the point grid at 1x; every size in the current matrix
 * centres to an integer anyway, so the rounding is a guard against a future
 * odd-sized component rather than a live correction.
 */
const place = (
  spec: ShapeSpec,
  canvas: CanvasSize,
): { left: number; top: number; width: number; height: number } => {
  const [width, height] = spec.size;
  const [offsetX, offsetY] = spec.offset ?? [0, 0];
  return {
    left: Math.round((canvas.width - width) / 2) + offsetX,
    top: Math.round((canvas.height - height) / 2) + offsetY,
    width,
    height,
  };
};

const isGroup = (spec: ComponentSpec): spec is GroupSpec => spec.kind === "group";
const isStack = (spec: ComponentSpec): spec is StackSpec => spec.kind === "stack";

export function resolveScene(sceneId: string): PlacedScene {
  const scene = scenes.find((entry) => entry.id === sceneId);
  if (scene === undefined) {
    throw new Error(
      `Unknown scene "${sceneId}". The matrix declares: ${SCENE_IDS.join(", ")}.`,
    );
  }
  const component = components[scene.component];
  if (component === undefined) {
    throw new Error(`Scene "${sceneId}" names component "${scene.component}", which is absent.`);
  }

  const canvas = CANVAS;
  const common = {
    scene,
    canvas,
    backgroundId: scene.background,
    pressed: scene.state === "pressed",
  } as const;

  if (isGroup(component)) {
    // One group for the whole row, and `spacing` doing double duty exactly as it
    // does natively: the gap between siblings AND the container's merge
    // distance. Rendering these as independent groups would measure a scene the
    // matrix does not declare.
    const total =
      component.items.reduce((sum, item) => sum + item.size[0], 0) +
      component.spacing * (component.items.length - 1);
    const height = Math.max(...component.items.map((item) => item.size[1]));
    let left = Math.round((canvas.width - total) / 2);

    const surfaces: PlacedSurface[] = [];
    for (const [index, item] of component.items.entries()) {
      surfaces.push({
        nodeId: `item-${index}`,
        groupId: "component",
        plane: "base",
        family: familyOf(item),
        left,
        top: Math.round((canvas.height - height) / 2) + Math.round((height - item.size[1]) / 2),
        width: item.size[0],
        height: item.size[1],
        radius: radiusOf(item),
      });
      left += item.size[0] + component.spacing;
    }

    /*
     * X1 floors the merge distance at the sampling padding, and the floor bites
     * here: the matrix's `spacing: 12` is under the default 24px padding, so the
     * three padded proxies overlap — and X1's rule exists because overlapping
     * proxies chain, double-applying the material's own filter (S1 measured
     * 1.5625× for `brightness(1.25)`). Honouring the declared 12 would either
     * produce that artefact or force the padding down to 12, starving the blur
     * at exactly the edges the group scene exists to measure.
     *
     * So the web side unions at the padding instead, which lands on the same
     * *outcome* the native container is expected to reach at this spacing — one
     * merged body — by a different route. Both numbers travel into the cell
     * descriptor so the difference in route is on the record.
     */
    const mergeDistance = Math.max(component.spacing, DEFAULT_GROUP_SAMPLING.samplingPadding);

    return {
      ...common,
      groups: [
        {
          id: "component",
          source: "texture",
          mergeDistance,
          ...(mergeDistance === component.spacing ? {} : { declaredSpacing: component.spacing }),
        },
      ],
      surfaces,
    };
  }

  if (isStack(component)) {
    /*
     * S1's mandated scene, and the one place the two sides' mechanisms differ in
     * kind rather than in tuning.
     *
     * Natively the overlay `glassEffect` sits above the base one in a `ZStack`
     * with no shared container, so it samples the base's *rendered output*. On
     * the web that relationship is the plane sandwich: the overlay plane's
     * proxy is composited after the base plane's optics canvas, so a
     * DOM-sampling overlay sees glassed content, while a texture-sampling one
     * would see the raw raster and miss the entire point of the scene.
     *
     * So the base group samples the raster it actually sits over, and the
     * overlay group is declared `dom`. On the GPU tier that resolves to
     * `samplingBackend: "css-backdrop"`, `refraction: "approximate"` — a
     * demotion in fidelity that is *not* a fault, and the cell descriptor
     * records it by name rather than letting the scene quietly claim `true`
     * refraction over the wrong pixels.
     */
    return {
      ...common,
      groups: [
        { id: "component", source: "texture" },
        { id: "component-over", source: "dom" },
      ],
      surfaces: [
        {
          nodeId: "base",
          groupId: "component",
          plane: "base",
          family: familyOf(component.base),
          ...place(component.base, canvas),
          radius: radiusOf(component.base),
        },
        {
          nodeId: "over",
          groupId: "component-over",
          plane: "overlay",
          family: familyOf(component.over),
          ...place(component.over, canvas),
          radius: radiusOf(component.over),
        },
      ],
    };
  }

  return {
    ...common,
    groups: [{ id: "component", source: "texture" }],
    surfaces: [
      {
        nodeId: "body",
        groupId: "component",
        plane: "base",
        family: familyOf(component),
        ...place(component, canvas),
        radius: radiusOf(component),
      },
    ],
  };
}
