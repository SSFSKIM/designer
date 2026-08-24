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

import type { GroupRenderInput, SurfaceInput } from "../../src/render-model";

export type BackdropSpec =
  | { readonly kind: "none" }
  | {
      readonly kind: "checkerboard";
      readonly cell: number;
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
    // The field pass alone: an opaque tint over no backdrop is exactly the group's
    // coverage, so this golden fails on any change to the field, the corner
    // algebra, or the coverage ramp — and on nothing else.
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
  backdrop: { kind: "checkerboard", cell: 8 },
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

export const ALL_SCENES: readonly Scene[] = [...SCENES, LENS_DEPTH_SCENE];

export const SCENE_NAMES = SCENES.map((scene) => scene.name);

export function sceneByName(name: string): Scene {
  const scene = ALL_SCENES.find((candidate) => candidate.name === name);
  if (scene === undefined) throw new Error(`No scene named "${name}".`);
  return scene;
}
