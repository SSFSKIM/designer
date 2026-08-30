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

import { DEFAULT_GROUP_SAMPLING } from "@vitreajs/vitrea";
import type { ShapeFamily } from "@vitrea/geometry";
import type { GlassPlane } from "@vitreajs/vitrea-web";

// Placement is the calibration library's, not a second copy of it: the
// instrument bounds its shape search and profiles its shadow axis from exactly
// this layout (schema 5), so the page and the measurement must lay the
// declaration out through one function or the difference between them would
// read as a fidelity finding. Imported by module rather than through the barrel,
// which pulls `pngjs` and `node:buffer` in for the PNG decoder.
import { placeComponent, type CanvasSize, type DeclaredComponent, type PlacedShape } from "../src/component-region";

// Vite resolves this through `server.fs.allow`; it is the native harness's own
// file, not a copy. See `vite.config.ts`.
import matrix from "../../../apps/reference-apple/scenes.json";

export type { CanvasSize };

type ComponentSpec = DeclaredComponent;

export interface SceneEntry {
  readonly id: string;
  readonly background: string;
  readonly component: string;
  readonly state: string;
  /** A key into the matrix's `tints` registry. Absent on every untinted scene. */
  readonly tint?: string;
}

/**
 * An author tint as the matrix declares it: sRGB components 0…255 and an
 * optional alpha, which is the tint's STRENGTH — `Color.opacity` on the native
 * side and a CSS colour's alpha here are the same axis.
 */
interface TintSpec {
  readonly srgb: readonly [number, number, number];
  readonly alpha?: number;
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
  /**
   * The scene's author tint as a CSS colour, or absent for an untinted scene.
   *
   * Scene-level rather than surface-level because that is where the native side
   * puts it: `material()` returns one configured `Glass` value and all three
   * component arms render it, so a tinted group or stack tints every body. A
   * per-surface tint here would be a shape the matrix cannot declare.
   */
  readonly tint?: string;
  readonly groups: readonly PlacedGroup[];
  readonly surfaces: readonly PlacedSurface[];
}

const components = matrix.components as unknown as Record<string, ComponentSpec>;
const scenes = matrix.scenes as readonly SceneEntry[];
const tints = matrix.tints as unknown as Record<string, TintSpec | undefined>;

/**
 * A declared tint, as the CSS colour `registerHost({ tint })` parses.
 *
 * Formatted from the matrix's own INTEGERS rather than from a hex string, which
 * is what keeps the two sides on one number: the native side divides the same
 * three integers by 255, and a hex round-trip would introduce a second
 * representation for the two implementations to disagree about. Alpha is the
 * strength on both sides, so it rides in the same colour rather than becoming a
 * separate knob.
 */
const cssColour = (spec: TintSpec): string => {
  const [r, g, b] = spec.srgb;
  return `rgb(${r} ${g} ${b} / ${spec.alpha ?? 1})`;
};

export const CANVAS: CanvasSize = matrix.canvas;

export const SCENE_IDS: readonly string[] = scenes.map((entry) => entry.id);

const familyOf = (shape: PlacedShape): ShapeFamily =>
  shape.kind === "capsule" ? "capsule" : "fixed-rounded-rect";

/** The box `registerHost` needs, straight off the shared placement. */
const boxOf = (shape: PlacedShape): { left: number; top: number; width: number; height: number } => ({
  left: shape.left,
  top: shape.top,
  width: shape.width,
  height: shape.height,
});

const isGroup = (spec: ComponentSpec): spec is Extract<ComponentSpec, { kind: "group" }> =>
  spec.kind === "group";
const isStack = (spec: ComponentSpec): spec is Extract<ComponentSpec, { kind: "stack" }> =>
  spec.kind === "stack";

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

  // Refuse rather than guess, the same posture the native harness takes at load:
  // an unresolvable tint id would otherwise render an UNTINTED surface under a
  // tinted scene id, and the resulting cell would read as a fidelity finding
  // about the tint rather than as the missing declaration it is.
  let tint: string | undefined;
  if (scene.tint !== undefined) {
    const spec = tints[scene.tint];
    if (spec === undefined) {
      throw new Error(
        `Scene "${sceneId}" names tint "${scene.tint}", which the matrix's tints registry lacks.`,
      );
    }
    tint = cssColour(spec);
  }

  const canvas = CANVAS;
  const common = {
    scene,
    canvas,
    backgroundId: scene.background,
    pressed: scene.state === "pressed",
    ...(tint === undefined ? {} : { tint }),
  } as const;

  // The shared layout: group items left to right, a stack's base before its
  // overlay, a lone shape on its own. Identity is attached here; the geometry is
  // not restated.
  const placed = placeComponent(component, canvas);
  const surfaceAt = (index: number, nodeId: string, groupId: string, plane: GlassPlane): PlacedSurface => {
    const shape = placed[index];
    if (shape === undefined) {
      throw new Error(`Scene "${sceneId}" declares no shape at position ${index}.`);
    }
    return { nodeId, groupId, plane, family: familyOf(shape), ...boxOf(shape), radius: shape.radius };
  };

  if (isGroup(component)) {
    // One group for the whole row, and `spacing` doing double duty exactly as it
    // does natively: the gap between siblings AND the container's merge
    // distance. Rendering these as independent groups would measure a scene the
    // matrix does not declare.
    const surfaces: PlacedSurface[] = placed.map((_shape, index) =>
      surfaceAt(index, `item-${index}`, "component", "base"),
    );

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
        surfaceAt(0, "base", "component", "base"),
        surfaceAt(1, "over", "component-over", "overlay"),
      ],
    };
  }

  return {
    ...common,
    groups: [{ id: "component", source: "texture" }],
    surfaces: [surfaceAt(0, "body", "component", "base")],
  };
}
