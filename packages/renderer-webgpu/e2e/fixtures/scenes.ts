/**
 * The golden scenes, as data.
 *
 * §Testing asks for "headless golden-image tests (sRGB-locked)". Each scene is a
 * viewport, a backdrop, and a set of groups — everything the renderer needs and
 * nothing about how it is compared, so the same list drives the golden run, the
 * regeneration script, and the benchmark's smaller cousin.
 *
 * They are deliberately small (200×120 CSS px at DPR 2) and deliberately few. A
 * golden's job is to fail when the optics change, not to be a gallery: seven
 * scenes that each isolate one mechanism catch more regressions per committed byte
 * than one big scene that exercises everything at once and localises nothing.
 */

import type { GroupRenderInput, Rect, SurfaceInput } from "../../src/render-model";

export type BackdropSpec =
  | { readonly kind: "none" }
  | {
      readonly kind: "checkerboard";
      readonly cell: number;
      /** Source extent in texels, square. 256 unless a scene says otherwise. */
      readonly size?: number;
      /**
       * Dirty every frame, the way `importExternalTexture`'s expire-at-task-end
       * makes a video dirty on every frame that samples it. The benchmark scene
       * needs this: §Performance envelope pins its budget to a scene with one
       * video backdrop, and a static backdrop rebuilds nothing at all.
       */
      readonly live?: boolean;
    }
  | { readonly kind: "flat"; readonly luminance: number }
  | { readonly kind: "gradient"; readonly from: readonly [number, number, number]; readonly to: readonly [number, number, number] };

export interface Scene {
  readonly name: string;
  readonly widthCss: number;
  readonly heightCss: number;
  readonly devicePixelRatio: number;
  readonly backdrop: BackdropSpec;
  readonly groups: readonly GroupRenderInput[];
  /**
   * Frames to run before capture. More than one only where the scene depends on a
   * value that arrives through the analysis readback.
   */
  readonly warmupFrames?: number;
  /** Whether the highlight canvas is captured instead of the optics canvas. */
  readonly capture?: "optics" | "highlight";
  /**
   * Measured, never captured as a golden. A measurement scene can be sized for
   * what it needs to resolve; a golden has to stay small enough to commit.
   */
  readonly measureOnly?: boolean;
  /**
   * Where the backdrop's pixels sit on the plane, in CSS px (claims §5.47).
   * Absent, the backdrop is cover-fit to the viewport — the rule every golden
   * before `placed-checkerboard` was taken under.
   */
  readonly backdropPlacement?: Rect;
}

const VIEWPORT = { widthCss: 200, heightCss: 120, devicePixelRatio: 2 } as const;

const rect = (
  nodeId: string,
  center: readonly [number, number],
  size: readonly [number, number],
  over: Partial<SurfaceInput> = {},
): SurfaceInput => ({
  nodeId,
  family: "fixed-rounded-rect",
  shape: {
    center: [center[0], center[1]],
    size: [size[0], size[1]],
    radii: [12, 12, 12, 12],
    smoothing: 0,
    thickness: 6,
  },
  reference: "figma-smoothing",
  ...over,
});

/**
 * `noBackdrop` rather than `backdropSourceId: undefined`: under
 * `exactOptionalPropertyTypes` an explicit `undefined` is not assignable to an
 * optional property, and a sentinel says what is meant anyway.
 */
type GroupOver = Omit<Partial<GroupRenderInput>, "backdropSourceId" | "groupId" | "surfaces"> & {
  readonly noBackdrop?: boolean;
};

const group = (
  groupId: string,
  surfaces: readonly SurfaceInput[],
  over: GroupOver = {},
): GroupRenderInput => {
  const { noBackdrop, ...rest } = over;
  return {
    groupId,
    surfaces,
    refraction: "true",
    analysisExact: true,
    ...(noBackdrop === true ? {} : { backdropSourceId: "bg" }),
    ...rest,
  };
};

export const SCENES: readonly Scene[] = [
  {
    // The field pass alone, and the unsampled path (W11a): a group with no
    // backdrop leaves the optics pass as a premultiplied layer — the material's
    // tint at its own alpha, times the coverage — so this golden fails on any
    // change to the field, the corner algebra, the coverage ramp, or the layer
    // form the browser composites for a surface over a DOM proxy or the page.
    ...VIEWPORT,
    name: "field-mask",
    backdrop: { kind: "none" },
    groups: [
      group("g", [rect("s", [100, 60], [140, 68])], {
        noBackdrop: true,
        refraction: "none",
        analysisExact: false,
      }),
    ],
  },
  {
    // Refraction over a checkerboard: the displacement field is visible directly
    // as the bend in the squares, which is the same reason §Calibration puts a
    // checkerboard in the canonical scene set.
    ...VIEWPORT,
    name: "refraction-checkerboard",
    backdrop: { kind: "checkerboard", cell: 10 },
    groups: [group("g", [rect("s", [100, 60], [140, 68], { shape: { center: [100, 60], size: [140, 68], radii: [20, 20, 20, 20], smoothing: 0, thickness: 14 } })])],
  },
  {
    // The only golden at device pixel ratio 1 — the body's depth ramp, on the
    // scale it acts (W15 contract X7; W13's Deferred, claims §5.68 §8).
    //
    // The ramp adds sharpness above the deep value near the contour, and its 2x
    // anchors evaluate to nothing on this bed, so at DPR 2 — which every other
    // golden here renders at — it is a verified null and no committed pixel
    // moves when it changes. That is exactly the wrong place to pin a wave whose
    // binding rule is that the 1x material does not move. This scene is
    // `refraction-checkerboard`'s twin at DPR 1: the same 140×68 surface over a
    // checkerboard, on a cell of 8 CSS px, where the sharp component still
    // passes the plate's fundamental and the ramp's excursion is visible as a
    // crisper band inside the contour fading into a heavier interior.
    //
    // Its counterpart in `isolation.spec.ts` (`W15_HASHES`) pins the same scene
    // under the named profile, which patches the tint and the outer shadow and
    // nothing of the body — so the ramp is live in both pins, and the test
    // beside that table renders the scene with the ramp's start anchors zeroed
    // to show that the bytes actually depend on it.
    widthCss: 200,
    heightCss: 120,
    devicePixelRatio: 1,
    name: "body-ramp-1x",
    backdrop: { kind: "checkerboard", cell: 8 },
    groups: [group("g", [rect("s", [100, 60], [140, 68], { shape: { center: [100, 60], size: [140, 68], radii: [20, 20, 20, 20], smoothing: 0, thickness: 14 } })])],
  },
  {
    // A backdrop SMALLER than the viewport, placed where its pixels are (claims
    // §5.47): a 96-texel checkerboard at (28, 12), one texel per CSS px, under a
    // surface that hangs past its right edge. Sampled through the placed fit the
    // squares are 8 CSS px and land under the surface at the same coordinates a
    // page would show them at; past the placement's edge the sampler clamps.
    // The cover fit stretched this same texture over the whole 200×120 viewport,
    // and `scenes.spec.ts` keeps that render's hash as the fail-before record.
    ...VIEWPORT,
    name: "placed-checkerboard",
    backdrop: { kind: "checkerboard", cell: 8, size: 96 },
    backdropPlacement: { x: 28, y: 12, width: 96, height: 96 },
    groups: [group("g", [rect("s", [100, 60], [140, 68], { shape: { center: [100, 60], size: [140, 68], radii: [20, 20, 20, 20], smoothing: 0, thickness: 14 } })])],
  },
  {
    // Parent acceptance #2's mechanism, side by side over one backdrop: same
    // thickness, different size, visibly different bend.
    ...VIEWPORT,
    name: "lens-size-scaling",
    backdrop: { kind: "checkerboard", cell: 8 },
    groups: [
      group("small", [rect("s", [40, 60], [48, 30], { shape: { center: [40, 60], size: [48, 30], radii: [10, 10, 10, 10], smoothing: 0, thickness: 10 } })]),
      group("large", [rect("l", [138, 60], [104, 92], { shape: { center: [138, 60], size: [104, 92], radii: [24, 24, 24, 24], smoothing: 0, thickness: 10 } })]),
    ],
  },
  {
    ...VIEWPORT,
    name: "tint-adaptation-light",
    backdrop: { kind: "flat", luminance: 0.85 },
    // The analysis result reaches the shader through a readback, so the scene has
    // to run frames for it to arrive and for the low-pass to settle.
    warmupFrames: 40,
    groups: [group("g", [rect("s", [100, 60], [140, 68])])],
  },
  {
    ...VIEWPORT,
    name: "tint-adaptation-dark",
    backdrop: { kind: "flat", luminance: 0.02 },
    warmupFrames: 40,
    groups: [group("g", [rect("s", [100, 60], [140, 68])])],
  },
  {
    // The two corner references are separate fits, not two points on one axis
    // (Decision Log #22a), so the rim is where the difference is visible.
    ...VIEWPORT,
    name: "rim-two-references",
    backdrop: { kind: "gradient", from: [0.02, 0.03, 0.06], to: [0.35, 0.38, 0.45] },
    groups: [
      group("apple", [
        rect("a", [56, 60], [88, 88], {
          reference: "apple-continuous",
          shape: { center: [56, 60], size: [88, 88], radii: [26, 26, 26, 26], smoothing: 0, thickness: 8 },
        }),
      ]),
      group("figma", [
        rect("f", [148, 60], [88, 88], {
          reference: "figma-smoothing",
          shape: { center: [148, 60], size: [88, 88], radii: [26, 26, 26, 26], smoothing: 0.66, thickness: 8 },
        }),
      ]),
    ],
  },
  {
    // X8 rider 2 on screen.
    //
    // The two groups share one parent geometry. The left group draws it; the
    // right group draws only a level set of it, inset by 14 px, with the parent
    // declared as a field reference and not as a member. Side by side, the inset
    // contour and its reduced corner radius are the rider's content: the child IS
    // the parent's field, offset — not a separately resolved shape.
    //
    // Nesting the child inside its parent's own union would show nothing at all,
    // and correctly so: the child's field is the parent's plus a positive inset,
    // so `min` discards it everywhere.
    ...VIEWPORT,
    name: "concentric-nesting",
    backdrop: { kind: "gradient", from: [0.03, 0.05, 0.09], to: [0.5, 0.45, 0.3] },
    groups: [
      group("outer", [
        rect("parent", [56, 60], [86, 92], {
          shape: { center: [56, 60], size: [86, 92], radii: [26, 26, 26, 26], smoothing: 0, thickness: 9 },
        }),
      ]),
      group("inset", [
        rect("reference", [148, 60], [86, 92], {
          fieldReferenceOnly: true,
          shape: { center: [148, 60], size: [86, 92], radii: [26, 26, 26, 26], smoothing: 0, thickness: 9 },
        }),
        rect("child", [148, 60], [86, 92], {
          family: "concentric-rounded-rect",
          concentricOf: { nodeId: "reference", inset: 14 },
          shape: { center: [148, 60], size: [86, 92], radii: [26, 26, 26, 26], smoothing: 0, thickness: 9 },
        }),
      ]),
    ],
  },
  {
    // The bounded smooth-min union: close enough to grow a neck, and the bulge cap
    // is what keeps it from reading as jelly.
    ...VIEWPORT,
    name: "union-pair",
    backdrop: { kind: "gradient", from: [0.05, 0.05, 0.05], to: [0.4, 0.4, 0.42] },
    groups: [
      group("g", [
        rect("a", [72, 60], [64, 52], {
          shape: { center: [72, 60], size: [64, 52], radii: [16, 16, 16, 16], smoothing: 0, thickness: 8 },
        }),
        rect("b", [128, 60], [64, 52], {
          shape: { center: [128, 60], size: [64, 52], radii: [16, 16, 16, 16], smoothing: 0, thickness: 8 },
        }),
      ]),
    ],
  },
  {
    // The highlight canvas: X1 puts it above the semantic host DOM, so it is a
    // separate target and needs a golden of its own.
    ...VIEWPORT,
    name: "highlight-press-glow",
    backdrop: { kind: "none" },
    capture: "highlight",
    groups: [
      group(
        "g",
        [
          rect("s", [100, 60], [140, 68], {
            channels: { press: 0.6, glow: 1, sweep: 0.15, lensStrength: 1, pressPoint: [72, 48] },
          }),
        ],
        { noBackdrop: true, refraction: "none", analysisExact: false },
      ),
    ],
  },
];

/**
 * Sized so the lens's size gain is actually resolvable.
 *
 * `material.ts` saturates the gain at a 420 px span, and the golden viewport is
 * 200x120 — so inside a golden the two surfaces differ in lens depth by about
 * 11%, which no pixel metric separates from noise. Here the wide surface's span
 * is 400 px against the narrow one's 36, a 2.5x difference in depth: the
 * mechanism parent acceptance #2 asks for, at a scale where it can be measured.
 *
 * DPR 1, because this is read back and differenced rather than committed.
 */
export const LENS_DEPTH_SCENE: Scene = {
  name: "lens-size-depth",
  widthCss: 620,
  heightCss: 440,
  devicePixelRatio: 1,
  measureOnly: true,
  // A 32 px cell, not 8 (W11c G2). The lens is the body read from further
  // inside, and the body of a 400 px surface is nearly all heavy scatter (the
  // depth ramp has run out long before its centre): an 8 px checker is erased before the
  // lens can move it, and the wide group would read as not lensing at all. At
  // 32 px the heavy component still passes structure, so the moved band is the
  // lens depth on both surfaces.
  backdrop: { kind: "checkerboard", cell: 32 },
  groups: [
    group("narrow", [
      rect("n", [70, 220], [44, 36], {
        shape: {
          center: [70, 220],
          size: [44, 36],
          radii: [10, 10, 10, 10],
          smoothing: 0,
          thickness: 10,
        },
      }),
    ]),
    group("wide", [
      rect("w", [390, 220], [420, 400], {
        shape: {
          center: [390, 220],
          size: [420, 400],
          radii: [60, 60, 60, 60],
          smoothing: 0,
          thickness: 10,
        },
      }),
    ]),
  ],
};

/**
 * The outer shadow's field-extent case (W8): one surface tight against the
 * viewport's top edge, and the identical surface clear of it.
 *
 * The shadow is read from the group's own field texture at an OFFSET position —
 * the field one shadow-offset above the pixel being shaded. That rect is clipped
 * to the canvas, so for a surface within the shadow's reach of the top there are
 * no rows up there to read, and a clamp would repeat the edge texel: a distance
 * too small, and therefore a flat, too-dark band exactly where the shadow should
 * be fading out. The two scenes are identical apart from where the surface sits,
 * so the shadow above each of them must agree once one is shifted onto the other.
 *
 * DPR 1 and no backdrop: this is read back and differenced rather than committed,
 * and the shadow lands in the canvas's ALPHA, which a backdrop would only add
 * noise to.
 */
const shadowEdgeScene = (name: string, centreY: number): Scene => ({
  name,
  widthCss: 240,
  heightCss: 260,
  devicePixelRatio: 1,
  measureOnly: true,
  backdrop: { kind: "none" },
  groups: [
    group("g", [rect("s", [120, centreY], [120, 44])], {
      noBackdrop: true,
      refraction: "none",
      analysisExact: false,
    }),
  ],
});

/** Top edge of the surface at y = 8 — well inside the shadow's ~41 px reach. */
export const SHADOW_TOP_EDGE_SCENE: Scene = shadowEdgeScene("shadow-top-edge", 30);
/** The same surface 100 px lower, where the field rect is not clipped at all. */
export const SHADOW_MID_CANVAS_SCENE: Scene = shadowEdgeScene("shadow-mid-canvas", 130);

export const ALL_SCENES: readonly Scene[] = [
  ...SCENES,
  LENS_DEPTH_SCENE,
  SHADOW_TOP_EDGE_SCENE,
  SHADOW_MID_CANVAS_SCENE,
];

export const SCENE_NAMES = SCENES.map((scene) => scene.name);

export function sceneByName(name: string): Scene {
  const scene = ALL_SCENES.find((candidate) => candidate.name === name);
  if (scene === undefined) throw new Error(`No scene named "${name}".`);
  return scene;
}
