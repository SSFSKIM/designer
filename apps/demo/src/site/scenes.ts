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
 *
 * **They moved to macOS 27 at W29 G4**, and they had to move together with the
 * runtime rather than beside it. The pair's whole claim is "this browser, now,
 * against Apple's own pixels", and the browser draws whatever material the
 * runtime resolves by default — which is macOS 27's since 0.19.0. A macOS 26.5
 * fixture under a macOS 27 render would put a real, measured difference in the
 * pair and label it vitrea's error.
 *
 * The macOS 26.5 pair is **not** offered beside it, and that is a limitation of
 * this page rather than a preference. A material document is selected at
 * construction — a page drawing one has surfaces measured against it — so
 * offering both beds would mean two roots, and the site has one. The macOS 26.5
 * material stays shipped and selectable by an application
 * (`macos26MaterialProfileDocument`); what this page cannot do is show both at
 * once, which `packages/platform-web/README.md` says.
 */
export const NATIVE_PROFILE = "apple-macos-27.0-1x-light-standard-glass0.5";
export const DARK_NATIVE_PROFILE = "apple-macos-27.0-1x-dark-standard-glass0.5";

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

/**
 * W27c G0/G1's recovered-inactive pose (claims §5.128; X3, X7): `scenes.json`
 * declares scenes with `state: "inactive"` — the window-recede pose,
 * captured for the fidelity bed but with no counterpart on this page yet.
 * `Stage` renders every reference scene as a live, key (active) `GlassSurface`;
 * it has no inactive-root wiring, so a visitor picking one of these would see a
 * live active surface paired against a native capture of a receded window,
 * read as a fidelity gap that is actually a missing feature. W3's `pressed`
 * filter below is the same withholding for the same reason, on the pose that
 * got there first.
 *
 * **2026-09-15 (W28 G4, claims §5.148): the runtime exists and the withholding
 * stands, on a different reason.** W28 G3 shipped the pose (§5.147) and G4
 * published the inactive rows in the canonical matrix, so the earlier "until
 * W27c G3 wires an inactive `Stage` mode" no longer describes what is missing.
 * What is missing is a place to put it: activation is a pose of the **root**
 * (X7) and this page has one root, so posing the pair's surface inactive would
 * recede the whole site — its toolbar, its panels and the prose chrome around
 * the comparison — and posing only that surface would need a per-surface recede,
 * which is Apple's "element overlap" and is deferred, unbuilt and unmeasured
 * (W27 §Deferred). The operable demonstration is therefore the playground's
 * `windowActivation` pin and the whole page receding when the window is
 * backgrounded, which is what G4's sheets read. A second root scoped to the
 * pair, or the per-element recede, is what would let this picker offer the
 * inactive scenes; the tracker carries it.
 */
const isRecoveredInactive = (scene: { readonly state: string }): boolean => scene.state === "inactive";

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
    if (isRecoveredInactive(scene)) return [];
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
