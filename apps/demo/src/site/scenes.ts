/**
 * The reference pair's geometry, read from the same contract both renderers read.
 *
 * `apps/reference-apple/scenes.json` is the geometry contract (Decision Log #26b):
 * the SwiftUI harness and the web calibration page both read it, because a diff is
 * only meaningful when both sides put the same shape in the same place. This module
 * is a third reader, and it reads rather than restates: sizes, radii and the scene
 * list come from the file. The one rule not in the file is the placement rule, and
 * it is reproduced here from `packages/calibration/web/scenes.ts` — centre the box
 * in the canvas, round to the point grid, then apply the scene's own offset. If
 * that rule ever moves, it moves in three places; the alternative was importing
 * across a package's private `web/` directory, which would couple the demo to the
 * calibration page's build.
 *
 * Only the two shape families the pair displays are handled. A scene naming a
 * group or a stack is filtered out rather than approximated.
 */

import matrix from "../../../reference-apple/scenes.json";

export interface SceneBox {
  readonly left: number;
  readonly top: number;
  readonly width: number;
  readonly height: number;
  readonly radius: number;
  readonly capsule: boolean;
}

export interface ReferenceScene {
  readonly id: string;
  readonly background: string;
  readonly backgroundFile: string;
  readonly component: string;
  readonly pressed: boolean;
  readonly fixtureSet: "calibration" | "validation" | "holdout";
  readonly box: SceneBox;
  /** Relative to the site root, so the build can rewrite it. */
  readonly nativeCapture: string;
  /**
   * The same scene captured under the DARK profile, absent where there is none.
   *
   * The dark profile carries fourteen scenes where the light one carries every
   * scene, so most of the picker's list has no dark capture at all — and a pair
   * is only evidence when both halves are the same colour scheme. Absent here is
   * what the reference section reads to withdraw the comparison rather than show
   * a dark render beside a light capture (W21 G3 review).
   */
  readonly darkCapture?: string;
  /**
   * W3's author tint as a CSS colour, absent on an untinted scene.
   *
   * The pair puts a live surface beside a native capture, so this has to be
   * carried: a tinted scene whose live half rendered untinted would show a
   * colour difference the visitor would read as vitrea's fidelity rather than
   * as the missing prop it is. Formatted from the matrix's own integers for the
   * same reason the placement rule is reproduced rather than restated.
   */
  readonly tint?: string;
}

export const CANVAS: { readonly width: number; readonly height: number } = matrix.canvas;

/**
 * The profiles whose fixtures the pair shows, one per colour scheme. The site
 * states the one it is showing on the page, beside the figures.
 *
 * Both are the 1x profiles, because that is the scale this machine captured and
 * the scale the pair's rasters are.
 */
export const NATIVE_PROFILE = "apple-macos-26.5-1x-light-standard";
export const DARK_NATIVE_PROFILE = "apple-macos-26.5-1x-dark-standard";

/** Which profile speaks for a resolved colour scheme. */
export const nativeProfileFor = (scheme: "light" | "dark"): string =>
  scheme === "dark" ? DARK_NATIVE_PROFILE : NATIVE_PROFILE;

/**
 * The scene's capture under a resolved scheme, `undefined` where there is none.
 *
 * The light profile captures every scene; the dark one captures fourteen. A
 * caller that gets `undefined` must withdraw the comparison rather than fall
 * back — a dark live surface beside a light capture, under a figure measured in
 * the light scheme, is not evidence of anything.
 */
export const nativeCaptureFor = (
  scene: ReferenceScene,
  scheme: "light" | "dark",
): string | undefined => (scheme === "dark" ? scene.darkCapture : scene.nativeCapture);

type ShapeSpec = { readonly kind: string; readonly size?: readonly [number, number]; readonly radius?: number };

const components = matrix.components as unknown as Record<string, ShapeSpec>;
const backgrounds = matrix.backgrounds as unknown as Record<string, unknown>;
const split = matrix.split as unknown as Record<string, readonly string[]>;
const tints = matrix.tints as unknown as Record<
  string,
  { readonly srgb: readonly [number, number, number]; readonly alpha?: number } | undefined
>;

/** The declared tint as a CSS colour, with its alpha carrying the strength. */
const tintOf = (id: string | undefined): string | undefined => {
  if (id === undefined) return undefined;
  const spec = tints[id];
  if (spec === undefined) return undefined;
  const [r, g, b] = spec.srgb;
  return `rgb(${r} ${g} ${b} / ${spec.alpha ?? 1})`;
};

/**
 * Which scenes the dark profile actually captured, read from the same file.
 *
 * `scenes.json` declares a profile's membership as an explicit list or as the
 * string `"all"`, and both arms are handled here rather than assumed: the light
 * profiles say `"all"` today and the dark ones name fourteen, and a wave that
 * widens the dark profile should widen this page by re-reading the file.
 */
const darkProfileScenes: ReadonlySet<string> | "all" = (() => {
  const profiles = matrix.profiles as readonly {
    readonly key: string;
    readonly scenes: readonly string[] | string;
  }[];
  const found = profiles.find((profile) => profile.key === DARK_NATIVE_PROFILE);
  if (found === undefined) return new Set<string>();
  return found.scenes === "all" ? "all" : new Set(found.scenes as readonly string[]);
})();

const capturedInDark = (id: string): boolean =>
  darkProfileScenes === "all" || darkProfileScenes.has(id);

const setOf = (id: string): ReferenceScene["fixtureSet"] =>
  split.holdout?.includes(id) === true
    ? "holdout"
    : split.validation?.includes(id) === true
      ? "validation"
      : "calibration";

/**
 * The probe set is captured, and shown by nothing here.
 *
 * W25 declared a `probe` fixture set in the same file this module reads (W25
 * Decision Log 3 (e)): 52 scenes that exist to identify constants, gated by
 * nothing and free to grow or be re-captured. The pair on this page is evidence
 * about the frozen bed — every figure beside it is a calibration, validation or
 * holdout reading — so a probe scene in the picker would offer a visitor a
 * measurement the project does not stand behind, and the instrument refuses
 * some of them outright (a 48 px dark square has no contour curvature to read),
 * which is a scene whose readout would simply be empty.
 */
const isProbe = (id: string): boolean => split.probe?.includes(id) === true;

function boxOf(spec: ShapeSpec): SceneBox | null {
  if (spec.size === undefined) return null;
  if (spec.kind !== "capsule" && spec.kind !== "rrect") return null;
  const [width, height] = spec.size;
  const capsule = spec.kind === "capsule";
  return {
    left: Math.round((CANVAS.width - width) / 2),
    top: Math.round((CANVAS.height - height) / 2),
    width,
    height,
    // A capsule's radius is half its short side, which is what makes it a stadium.
    // `scenes.json` declares none for a capsule because there is only one value it
    // could be, and a second copy of it could disagree with the native side's.
    radius: capsule ? Math.min(width, height) / 2 : (spec.radius ?? 0),
    capsule,
  };
}

/** Every scene the pair can show, in the order `scenes.json` declares them. */
export const REFERENCE_SCENES: readonly ReferenceScene[] = (
  matrix.scenes as readonly {
    id: string;
    background: string;
    component: string;
    state: string;
    tint?: string;
  }[]
)
  .flatMap((scene) => {
    if (isProbe(scene.id)) return [];
    const spec = components[scene.component];
    const box = spec === undefined ? null : boxOf(spec);
    if (box === null || backgrounds[scene.background] === undefined) return [];
    const tint = tintOf(scene.tint);
    return [
      {
        id: scene.id,
        background: scene.background,
        backgroundFile: `fixtures/backgrounds/${scene.background}@1x.png`,
        component: scene.component,
        pressed: scene.state === "pressed",
        fixtureSet: setOf(scene.id),
        box,
        nativeCapture: `fixtures/${NATIVE_PROFILE}/${scene.id}.png`,
        ...(capturedInDark(scene.id)
          ? { darkCapture: `fixtures/${DARK_NATIVE_PROFILE}/${scene.id}.png` }
          : {}),
        ...(tint === undefined ? {} : { tint }),
      } satisfies ReferenceScene,
    ];
  })
  // The pressed scenes compare two independently derived poses rather than a
  // measurement against an observed one (C7's caveat), so they stay off the pair.
  .filter((scene) => !scene.pressed);
