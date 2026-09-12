/**
 * W27e G0 / claims §5.133: read every `vibrantColorMatrix` in the committed layer
 * dumps and say what is there. No fit, no capture, no runtime material.
 *
 * Run with `pnpm --filter @vitrea/calibration --fail-if-no-match exec tsx
 * scripts/vibrancy.ts`, and `--corpus probe` for the labelled probe run of §5.133
 * §7. Set `W27E_OUT` to a scratch directory to reproduce a table without replacing
 * the recorded one; the canonical outputs are create-only.
 *
 * Everything here is read from files already in git: the layer-dump trees, the
 * scene specs those runs were driven from, and `results/matrix.json` for the
 * backdrop level. Nothing decodes a pixel and nothing calls the capture harness,
 * so the reading is reproducible on any machine and cannot move the bed.
 *
 * The two corpora are kept apart on purpose. §5.133 pins a reading of a specific
 * 57 files, so the G0 corpus is frozen as the five trees it was declared over and
 * the labelled probe arrives beside it as a second one; a corpus is a parameter of
 * the reader rather than a wider glob, and the test pins both.
 *
 * Two conventions are worth stating once, because both are easy to get backwards.
 * A `CAColorMatrix` is **four rows of five columns** — `out_i = m_i1·R + m_i2·G +
 * m_i3·B + m_i4·A + m_i5` — not five rows of four, and the dump stores it as the
 * twenty floats of that struct in row order. And a filter's inputs are the
 * filter's own declared keys (`inputKeysSource: "inputKeys"`), so a key reading
 * `null` means the filter declares it and holds no value for it, which is a
 * different fact from the key being absent.
 */
import { createHash } from "node:crypto";
import { mkdirSync, readFileSync, readdirSync, writeFileSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import {
  DEFAULT_MATERIAL_PROFILE,
  backdropToneAdaptation,
  sizeThickness,
} from "@vitrea/renderer-webgpu";
import { componentRegion, type DeclaredComponent } from "../src/component-region";
import { decodePng } from "../src/image";
import { interiorLevel } from "../src/metrics/material";

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const OUT = "packages/calibration/results/2026-09-11-w27e-g0-vibrancy";
const PROBE_OUT = "packages/calibration/results/2026-09-11-w27e-probe";

/**
 * Every committed layer-dump tree, in the order the waves recorded them. The list
 * is explicit rather than globbed: a tree that appears later must be added here
 * deliberately, and the test pins how many dumps these five directories hold, so
 * a dump appearing or disappearing is a failing test rather than a quiet reading.
 */
export const DUMP_DIRS = [
  "packages/calibration/results/2026-09-03-w12-lens/layer-dumps",
  "packages/calibration/results/2026-09-03-w12-lens/layer-dumps-ramp",
  "packages/calibration/results/2026-09-03-w12-lens/layer-dumps-adapt",
  "packages/calibration/results/2026-09-05-w18-union-contour/probe/layer-dumps",
  "packages/calibration/results/2026-09-05-w20-capsule-corner/g0/layer-dumps",
] as const;

/**
 * The labelled probe run of §5.133 §7, one tree per colour scheme. It is a second
 * corpus and not a sixth G0 tree: G0's reading is published evidence about the five
 * trees above, and this run answers the question that reading could not reach —
 * whether Apple installs a vibrancy operator on a label at all — under a different
 * configuration. Merging the two would confound the readings and silently move a
 * recorded count.
 *
 * THREE axes differ between the corpora and every cross-corpus statement has to
 * carry all of them: colour scheme (G0 is light-only), backing scale (G0 is 1x,
 * this is 2x) and the WINDOW POSE — all 57 G0 dumps record `isKeyWindow: true`
 * and all 50 of these record `isKeyWindow: false`. The pose is the variable this
 * wave exists to measure, so it is never the one to leave out of a comparison.
 */
export const PROBE_DUMP_DIRS = [
  "packages/calibration/results/2026-09-11-w27e-probe/light",
  "packages/calibration/results/2026-09-11-w27e-probe/dark",
] as const;

/**
 * The scene specs a dump could have been driven from. A probe run writes its own
 * spec beside `scenes.json` rather than editing it, so a component is declared in
 * exactly one of these — except the canonical components, which several probe beds
 * re-declare. The reader takes every spec that declares the scene and refuses a
 * disagreement rather than preferring one file, so the declared span is a
 * cross-checked reading and not a lookup in whichever file was listed first.
 */
const SPEC_FILES = [
  "apps/reference-apple/scenes.json",
  "apps/reference-apple/scenes-w9-probe.json",
  "apps/reference-apple/scenes-w12-probe-2x.json",
  "apps/reference-apple/scenes-w18-probe.json",
  "apps/reference-apple/scenes-w19-probe.json",
  "apps/reference-apple/scenes-w20-probe.json",
  "apps/reference-apple/scenes-w21-probe.json",
  "apps/reference-apple/scenes-w27e-probe.json",
  "packages/calibration/results/2026-09-03-w12-lens/layer-dumps-ramp/scenes.json",
] as const;

/**
 * Every dump in the G0 corpus is this configuration; the matrix is read at it. A
 * corpus that is not one configuration — the labelled probe covers both schemes at
 * 2x — reads no matrix cell at all rather than a cell from a configuration it is
 * not, so the two backdrop statistics stay unavailable there instead of wrong.
 */
const PROFILE_KEY = "apple-macos-26.5-1x-light-standard";

/** Rec.709 luma, the weights every matrix in the corpus factors through. */
export const LUMA_REC709 = [0.2126, 0.7152, 0.0722] as const;

/**
 * Two matrices are one operator when every one of their twenty floats agrees to
 * this tolerance. It is loose against float32's own resolution (about 6e-8 near 1)
 * and tight against the smallest difference the corpus actually shows, which is a
 * whole unit in the first coefficient, so the grouping is not a judgement call.
 */
export const OPERATOR_TOLERANCE = 1e-6;

interface FilterInputs { readonly [key: string]: unknown }
interface CaFilter {
  readonly class?: string;
  readonly description?: string;
  readonly inputs?: FilterInputs;
}
interface Layer {
  readonly class: string;
  readonly name: string | null;
  readonly frame: { x: number; y: number; width: number; height: number };
  readonly bounds: { x: number; y: number; width: number; height: number };
  readonly cornerRadius?: number;
  readonly opacity?: number;
  readonly isHidden?: boolean;
  readonly filters?: readonly CaFilter[];
  readonly backgroundFilters?: readonly CaFilter[];
  readonly compositingFilter?: unknown;
  readonly properties?: Record<string, unknown>;
  readonly sublayers?: readonly Layer[];
}
/**
 * The label a scene declared, as the harness writes it back into the dump. `srgb`
 * is null when the scene took the automatic colour, which is the case the whole
 * probe is about: an explicit colour is the author overriding what the system
 * would have chosen, so the two are different questions and the dump says which.
 */
interface DeclaredLabel {
  readonly text: string;
  readonly fontSize: number;
  readonly srgb: readonly number[] | null;
}
interface Dump {
  readonly scene: string;
  readonly background: string;
  readonly label?: DeclaredLabel | null;
  readonly component: string;
  readonly state: string;
  readonly tint: string | null;
  readonly colorScheme: string;
  readonly a11y: string;
  readonly backingScaleFactor: number;
  readonly isKeyWindow: boolean;
  readonly settleSeconds: number;
  readonly os: string;
  readonly canvas: { width: number; height: number };
  readonly view: { layer: Layer };
}
interface Component {
  readonly kind: string;
  readonly size?: readonly [number, number];
  readonly radius?: number;
  readonly base?: Component;
  readonly over?: Component;
  readonly items?: readonly Component[];
}
interface SceneSpec {
  readonly canvas: { width: number; height: number };
  readonly components: Record<string, Component>;
  readonly scenes: readonly { id: string; component: string }[];
}

/**
 * The backdrop level under a cell, read from the committed background fixture over
 * the *declared* region — not from the extracted silhouette.
 *
 * The matrix already carries two backdrop statistics and neither is quite this.
 * `shadow.backdropMeanLuminance` is the scene's exterior level, and
 * `material.interiorMeanBackdrop` is the backdrop over the silhouette the
 * luminance-delta extractor recovered, which `src/report.ts` documents as losing
 * "any part of the material whose level coincides with the backdrop's" — over the
 * impulse train that leaves 71 pixels weighted to the bright ones and reads
 * 0.11268 where the region is 0.00303. Both are recorded here beside this one so a
 * reader can see the disagreement, and the predicate below is evaluated on the
 * declared-region reading, which is the closest the committed evidence comes to
 * what Apple's `tracksLuma` samples.
 */
const backgrounds = new Map<string, { region: number; canvas: number }>();
function fixtureTone(background: string, scale: number, component: DeclaredComponent,
  canvas: { width: number; height: number }) {
  const path = `apps/reference-apple/fixtures/backgrounds/${background}@${scale}x.png`;
  const key = `${path}|${JSON.stringify(component)}`;
  const cached = backgrounds.get(key);
  if (cached) return { ...cached, source: path };
  const image = decodePng(readFileSync(join(ROOT, path)));
  const region = componentRegion(component,
    { canvas, scale, width: image.width, height: image.height });
  const value = {
    region: interiorLevel(image, { interior: region.silhouette }).mean,
    canvas: interiorLevel(image).mean,
  };
  backgrounds.set(key, value);
  return { ...value, source: path };
}

/**
 * The affine form every matrix in this corpus takes: `out = m·c + g⊙Y(c) + b`,
 * with `Y` the Rec.709 luma of the input colour. `m` is a scalar chroma gain — the
 * identity part — and `g` and `b` are per-channel, so one form covers both uses
 * the dumps contain. A foreground operator has `g` and `b` achromatic and `m` > 0;
 * an author tint has `m` = 0 and its whole output on one line through the seed.
 *
 * The fit is the exact least-squares solution for `(m, g)` with `L` fixed at
 * Rec.709 and `b` taken straight from the matrix's fifth column, so `maxResidual`
 * is a falsifiable claim about the form rather than a fitted slack: it is the
 * largest single coefficient the form fails to reproduce.
 */
export interface Decomposition {
  readonly chromaGain: number;
  readonly lumaGain: readonly [number, number, number];
  readonly offset: readonly [number, number, number];
  /** `m + g_i`, the gain the operator applies to an achromatic input's level. */
  readonly levelGain: readonly [number, number, number];
  readonly achromatic: boolean;
  readonly alphaRowIsIdentity: boolean;
  readonly alphaColumnIsZero: boolean;
  readonly maxResidual: number;
  readonly maps: Record<string, readonly [number, number, number]>;
}

/** The normal equations for `A = m·I + g·Lᵀ`, solved in closed form. */
export function decompose(flat: readonly number[]): Decomposition {
  if (flat.length !== 20) throw new Error(`A CAColorMatrix is twenty floats, not ${flat.length}`);
  const a = (i: number, j: number) => flat[i * 5 + j] as number;
  const l = LUMA_REC709;
  const lDotL = l[0] * l[0] + l[1] * l[1] + l[2] * l[2];
  // Row i reads `A_ij = m·δ_ij + g_i·L_j`. For a given m the row's own g_i is
  // `((A_i· − m·e_i)·L) / (L·L)`, so the whole system reduces to one scalar.
  let num = 0;
  let den = 0;
  for (let i = 0; i < 3; i += 1) {
    for (let j = 0; j < 3; j += 1) {
      const basis = (i === j ? 1 : 0) - (l[i] as number) * (l[j] as number) / lDotL;
      num += basis * a(i, j);
      den += basis * ((i === j ? 1 : 0));
    }
  }
  const chromaGain = den === 0 ? 0 : num / den;
  const lumaGain = [0, 1, 2].map((i) => {
    let dot = 0;
    for (let j = 0; j < 3; j += 1) dot += (a(i, j) - (i === j ? chromaGain : 0)) * (l[j] as number);
    return dot / lDotL;
  }) as unknown as [number, number, number];
  const offset = [a(0, 4), a(1, 4), a(2, 4)] as [number, number, number];
  let maxResidual = 0;
  for (let i = 0; i < 3; i += 1) {
    for (let j = 0; j < 3; j += 1) {
      const modelled = (i === j ? chromaGain : 0) + (lumaGain[i] as number) * (l[j] as number);
      maxResidual = Math.max(maxResidual, Math.abs(a(i, j) - modelled));
    }
  }
  const spread = (xs: readonly number[]) => Math.max(...xs) - Math.min(...xs);
  const apply = (c: readonly [number, number, number]) => {
    const y = l[0] * c[0] + l[1] * c[1] + l[2] * c[2];
    return [0, 1, 2].map((i) => chromaGain * (c[i] as number) + (lumaGain[i] as number) * y
      + (offset[i] as number)) as unknown as [number, number, number];
  };
  return {
    chromaGain,
    lumaGain,
    offset,
    levelGain: [0, 1, 2].map((i) => chromaGain + (lumaGain[i] as number)) as
      unknown as [number, number, number],
    achromatic: spread(lumaGain) < 1e-3 && spread(offset) < 1e-3,
    alphaRowIsIdentity: a(3, 0) === 0 && a(3, 1) === 0 && a(3, 2) === 0
      && a(3, 3) === 1 && a(3, 4) === 0,
    alphaColumnIsZero: a(0, 3) === 0 && a(1, 3) === 0 && a(2, 3) === 0,
    maxResidual,
    maps: {
      black: apply([0, 0, 0]), white: apply([1, 1, 1]), grey50: apply([0.5, 0.5, 0.5]),
      red: apply([1, 0, 0]), green: apply([0, 1, 0]), blue: apply([0, 0, 1]),
    },
  };
}

/*
 * ---------------------------------------------------------------------------
 * W27e G1 / claims §5.137: the label operator, as a function.
 *
 * Everything above reads matrices out of dumps. This block evaluates the one the
 * labelled probe found, so that G2 implements an operator that has already been
 * written down and checked rather than one derived a second time from prose. It
 * is pure arithmetic on encoded sRGB and knows nothing about the DOM, the
 * renderer or a profile; `test/vibrancy.test.ts` pins its coefficients to the
 * committed dumps, so the constants cannot drift away from Apple's.
 * ---------------------------------------------------------------------------
 */

/**
 * Which of the two label matrices applies. Apple selects by the colour scheme
 * and by nothing else the probe moved (§5.136 §4). vitrea cannot use the
 * document's scheme for this, because a vitrea surface's own level does not have
 * to follow it; the selector is the material's own composite level against the
 * CSS tier's `foregroundCrossover`, which is the same quantity the published ink
 * already switches on. `darkening` is Apple's light-scheme matrix and
 * `lightening` its dark-scheme one, named for what they do rather than for the
 * scheme they were read under, because the scheme is not what vitrea decides on.
 */
export type LabelOperator = "darkening" | "lightening";

/** Apple's scheme names, as the dumps record them, kept for the corpus tests. */
export type LabelScheme = "light" | "dark";

/**
 * The two matrices, copied to the float32 values
 * `results/2026-09-11-w27e-probe/table.json` holds. The dark alpha coefficient is
 * 0.95 in float32 and is written here as the float32 value rather than as 0.95,
 * because the test compares it to the dump byte for byte.
 */
export const LABEL_MATRICES: Readonly<Record<LabelOperator, readonly number[]>> = {
  darkening: [1, 0, 0, 0, -1, 0, 1, 0, 0, -1, 0, 0, 1, 0, -1, 0, 0, 0, 1, 0],
  lightening: [1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 0.949999988079071, 0],
};

/** Apple's scheme → the operator it carries, which is the whole of its selector. */
export const LABEL_OPERATOR_BY_SCHEME: Readonly<Record<LabelScheme, LabelOperator>> = {
  light: "darkening",
  dark: "lightening",
};

/** An ink in encoded sRGB, channels and alpha in [0, 1], non-premultiplied. */
export interface LabelInk {
  readonly rgb: readonly [number, number, number];
  readonly alpha: number;
}

const clamp01 = (value: number) => (value < 0 ? 0 : value > 1 ? 1 : value);

/**
 * A `CAColorMatrix` applied the way `inputClamp` = 1 applies it: four rows of
 * five columns over non-premultiplied encoded channels, then a plain [0, 1]
 * clamp. `feColorMatrix` at `color-interpolation-filters: sRGB` is the same
 * arithmetic, which §5.133 §5 confirmed to the code value on both surface
 * operators and §5.137 confirmed again on these two.
 */
export function applyColorMatrix(ink: LabelInk, matrix: readonly number[]): LabelInk {
  if (matrix.length !== 20) throw new Error(`A CAColorMatrix is twenty floats, not ${matrix.length}`);
  const input = [ink.rgb[0], ink.rgb[1], ink.rgb[2], ink.alpha];
  const out: number[] = [];
  for (let row = 0; row < 4; row += 1) {
    let sum = matrix[row * 5 + 4] as number;
    for (let column = 0; column < 4; column += 1) {
      sum += (matrix[row * 5 + column] as number) * (input[column] as number);
    }
    out.push(clamp01(sum));
  }
  return { rgb: [out[0] as number, out[1] as number, out[2] as number], alpha: out[3] as number };
}

/**
 * The operator the material's own composite level selects.
 *
 * `crossover` has no default on purpose. The number that belongs here is the
 * runtime's `CSS_TIER_MAPPING.foregroundCrossover`, and a calibration script that
 * kept its own copy would go on agreeing with a constant that had moved.
 */
export function labelOperatorFor(compositeLevel: number, crossover: number): LabelOperator {
  return compositeLevel >= crossover ? "darkening" : "lightening";
}

/**
 * The rendered ink: Apple's operator evaluated on the automatic ink.
 *
 * Both matrices offset every channel by a whole unit against a [0, 1] clamp, so
 * the operator **saturates** — the output colour is black under `darkening` and
 * white under `lightening` for every input in gamut, and the only thing the input
 * contributes is its alpha, which `lightening` scales by 0.95. That is why this
 * takes no backdrop argument: the operator vitrea evaluates has no backdrop term,
 * which is what lets the CSS tier fold it on the CPU without losing anything
 * (§5.137 §3). The alternative reading of `inputBackdropAware` — the classic
 * plus-darker / plus-lighter vibrancy composite — does have one, and §5.137 §2
 * records why this is the reading vitrea takes and what the two are worth apart.
 */
export function labelInk(operator: LabelOperator, ink: LabelInk): LabelInk {
  return applyColorMatrix(ink, LABEL_MATRICES[operator]);
}

/** One `vibrantColorMatrix` as found, before the cell's own facts are attached. */
interface Occurrence {
  readonly layerPath: string;
  readonly layerClass: string;
  readonly layerName: string | null;
  readonly layerEffect: string | null;
  readonly layerFrame: Layer["frame"];
  /**
   * The layer's own `opacity`. Recorded because a matrix on a layer at opacity 0
   * has no pixel consequence, and W27e G1 found that is exactly where the probe
   * corpus's surface operator sits: the `CASDFKeyFillHighlightEffect` layer reads
   * 0 on all 50 of these non-key dumps and 1 on all 58 of G0's key ones, which is
   * §5.128's receded rim showing up in the configuration.
   */
  readonly layerOpacity: number | null;
  readonly matrix: readonly number[];
  readonly inputBackdropAware: unknown;
  readonly inputClamp: unknown;
  readonly inputClampPreserveHue: unknown;
  readonly declaredInputKeys: readonly string[];
}

function effectClass(layer: Layer): string | null {
  const effect = layer.properties?.["effect"] as { class?: string } | undefined;
  return effect?.class ?? null;
}

/**
 * The layer SwiftUI commits a text run into. Its class is a mangled Swift name of
 * the form `_TtC7SwiftUIP33_<hash>14CGDrawingLayer`, and the hash identifies the
 * private context in the framework binary rather than the layer, so it changes
 * between builds and must never be matched on: the stable part is the suffix. The
 * layer carries no `effect` property at all — it draws glyphs, not a field — so its
 * class is the only statement the tree makes about what it is.
 */
export const LABEL_LAYER_CLASS = "CGDrawingLayer";
function isLabelLayer(layerClass: string): boolean {
  return layerClass.includes(LABEL_LAYER_CLASS);
}

/** Depth-first, recording the dotted sublayer index path the dump's own order gives. */
export function occurrences(layer: Layer, path = "0", found: Occurrence[] = []): Occurrence[] {
  for (const filter of layer.filters ?? []) {
    if (filter.description !== "vibrantColorMatrix") continue;
    const inputs = filter.inputs ?? {};
    const boxed = inputs["inputColorMatrix"] as { float32?: number[] } | undefined;
    if (!boxed?.float32) throw new Error(`${path}: vibrantColorMatrix with no decoded matrix`);
    found.push({
      layerPath: path,
      layerClass: layer.class,
      layerName: layer.name,
      layerEffect: effectClass(layer),
      layerFrame: layer.frame,
      layerOpacity: layer.opacity ?? null,
      matrix: boxed.float32,
      inputBackdropAware: inputs["inputBackdropAware"] ?? null,
      inputClamp: inputs["inputClamp"] ?? null,
      inputClampPreserveHue: inputs["inputClampPreserveHue"] ?? null,
      declaredInputKeys: ((filter as { properties?: { inputKeys?: string[] } })
        .properties?.inputKeys ?? []),
    });
  }
  (layer.sublayers ?? []).forEach((child, index) => occurrences(child, `${path}.${index}`, found));
  return found;
}

/** Every layer of a tree, by its dotted path, so an ancestor walk is a string cut. */
function index(layer: Layer, path = "0", into = new Map<string, Layer>()): Map<string, Layer> {
  into.set(path, layer);
  (layer.sublayers ?? []).forEach((child, i) => index(child, `${path}.${i}`, into));
  return into;
}

/**
 * The glass surface an occurrence belongs to: the nearest ancestor container one of
 * whose children is a `CABackdropLayer` carrying the `glassBackground` filter. That
 * container is what SwiftUI commits per `.glassEffect`, so a stacked scene resolves
 * two of them and a merged toolbar resolves one — which is the distinction the
 * table needs, and it is read from the tree rather than from the scene's name.
 */
function surfaceOf(layers: Map<string, Layer>, layerPath: string) {
  const parts = layerPath.split(".");
  for (let cut = parts.length - 1; cut >= 1; cut -= 1) {
    const containerPath = parts.slice(0, cut).join(".");
    const container = layers.get(containerPath);
    if (!container) continue;
    for (const child of container.sublayers ?? []) {
      if (child.class !== "CABackdropLayer") continue;
      const glass = (child.filters ?? []).find((f) => f.description === "glassBackground");
      if (glass) return { containerPath, backdrop: child, glass };
    }
  }
  throw new Error(`No glass surface above ${layerPath}`);
}

/**
 * The one glass surface a tree holds, for an occurrence that has none above it.
 *
 * A label is **not** inside the surface it labels: SwiftUI commits the text run to
 * a sibling branch of the `CABackdropLayer`, so the ancestor walk above runs off
 * the top of the tree. The association has to come from the scene's declaration
 * instead, and the reading of that declaration is mechanical — a probe scene
 * declares one control with one label, and a tree holding exactly one glass surface
 * is that. Two surfaces would make the association a guess, so this refuses rather
 * than picking one, which keeps a later stacked labelled scene from reading wrong.
 */
function soleSurfaceOf(layers: Map<string, Layer>, layerPath: string) {
  const found = [...layers].flatMap(([containerPath, container]) =>
    (container.sublayers ?? []).flatMap((child) => {
      if (child.class !== "CABackdropLayer") return [];
      const glass = (child.filters ?? []).find((f) => f.description === "glassBackground");
      return glass ? [{ containerPath, backdrop: child, glass }] : [];
    }));
  if (found.length !== 1) {
    throw new Error(`${layerPath}: ${found.length} glass surfaces in the tree, not one`);
  }
  return found[0] as { containerPath: string; backdrop: Layer; glass: CaFilter };
}

/** Element rects in the container's own coordinates, which is where span lives. */
function elementsOf(layer: Layer, offset: { x: number; y: number },
  into: { x: number; y: number; width: number; height: number; radius: number }[] = []) {
  const here = { x: offset.x + layer.frame.x - layer.bounds.x,
    y: offset.y + layer.frame.y - layer.bounds.y };
  if (layer.class === "CASDFElementLayer" && layer.frame.width > 0 && layer.frame.height > 0) {
    into.push({ x: here.x, y: here.y, width: layer.frame.width, height: layer.frame.height,
      radius: layer.cornerRadius ?? 0 });
  }
  for (const child of layer.sublayers ?? []) elementsOf(child, here, into);
  return into;
}

/** The minor dimension of a declared component, which is what Apple's size law reads. */
function declaredSpan(component: Component): number[] {
  if (component.size) return [Math.min(component.size[0], component.size[1])];
  const parts = [component.base, component.over, ...(component.items ?? [])]
    .filter((c): c is Component => c !== undefined);
  return parts.flatMap(declaredSpan);
}

interface MatrixCell {
  readonly key: { sceneId: string; profileKey: string };
  readonly material?: { interiorMeanBackdrop?: { value: number } };
  readonly shadow?: { backdropMeanLuminance?: { value: number } };
}

function readJson<T>(path: string): T {
  return JSON.parse(readFileSync(join(ROOT, path), "utf8")) as T;
}
function sha(path: string): string {
  return createHash("sha256").update(readFileSync(join(ROOT, path))).digest("hex");
}
function unique(values: number[]): number | null {
  const kept = [...new Set(values.map((v) => Number(v.toFixed(9))))];
  return kept.length === 1 ? (kept[0] as number) : null;
}

/**
 * One row of the table. The named fields are the ones the reading and the test
 * reason about; everything else the reader emits travels in the index signature
 * so the JSON stays the whole record rather than a projection of it.
 */
export interface Row extends Record<string, unknown> {
  readonly operatorId: number;
  readonly dump: string;
  readonly scene: string;
  readonly background: string;
  readonly component: string;
  readonly tint: string | null;
  readonly colorScheme: string;
  readonly a11y: string;
  readonly scale: number;
  readonly isKeyWindow: boolean;
  readonly settleSeconds: number;
  readonly layerPath: string;
  readonly layerClass: string;
  readonly layerEffect: string | null;
  readonly layerOpacity: number | null;
  readonly role: string;
  readonly input: string;
  readonly matrix: readonly number[];
  readonly operator: Decomposition;
  readonly surface: {
    readonly spanFromDump: number | null;
    readonly spanAgrees: boolean;
    readonly tracksLuma: unknown;
  };
  readonly body: {
    readonly faceColorMatrixBlack: unknown;
    readonly faceColorMatrixWhite: unknown;
    readonly faceFill: readonly number[] | null;
  };
  readonly backdrop: {
    readonly tone: number;
    readonly cellShadowBackdropMeanLuminance: number | null;
    readonly cellInteriorMeanBackdrop: number | null;
  };
  readonly vitrea: { readonly backdropToneAdaptation: number | null };
}

/**
 * The whole reading, as data; `main` only formats it.
 *
 * The corpus is a parameter with the G0 trees as its default, so calling this with
 * no argument is the reading §5.133 published and adding a corpus cannot move it.
 */
export function read(dirs: readonly string[] = DUMP_DIRS,
  matrixProfileKey: string | null = PROFILE_KEY) {
  const specs = SPEC_FILES.map((path) => ({ path, spec: readJson<SceneSpec>(path) }));
  const matrix = readJson<{ cells: MatrixCell[] }>("packages/calibration/results/matrix.json");
  const cellsAt = matrixProfileKey == null ? []
    : matrix.cells.filter((c) => c.key.profileKey === matrixProfileKey);

  const dumps = dirs.flatMap((dir) => readdirSync(join(ROOT, dir)).sort()
    .filter((f) => f.endsWith(".json") && f !== "scenes.json")
    .map((f) => ({ path: `${dir}/${f}`, dump: readJson<Dump>(`${dir}/${f}`) })));

  const rows = dumps.flatMap(({ path, dump }) => {
    const layers = index(dump.view.layer);
    const found = occurrences(dump.view.layer);

    // The declared span, cross-checked across every spec that declares this scene.
    const declaring = specs.filter(({ spec }) => spec.scenes.some((s) => s.id === dump.scene)
      && spec.components[dump.component] !== undefined);
    const declared = [...new Set(declaring.map(({ spec }) =>
      JSON.stringify(declaredSpan(spec.components[dump.component] as Component).sort((a, b) => a - b))))];
    if (declaring.length === 0) throw new Error(`${dump.scene}: declared in no committed spec`);
    if (declared.length !== 1) throw new Error(`${dump.scene}: specs disagree on span`);
    const declaredSpans = JSON.parse(declared[0] as string) as number[];
    const component = (declaring[0] as { spec: SceneSpec }).spec.components[dump.component];
    const fixture = fixtureTone(dump.background, dump.backingScaleFactor,
      component as unknown as DeclaredComponent, dump.canvas);

    const scene = cellsAt.filter((c) => c.key.sceneId === dump.scene);
    const interiorBackdrop = unique(scene
      .map((c) => c.material?.interiorMeanBackdrop?.value).filter((v): v is number => v != null));
    const shadowBackdrop = unique(scene
      .map((c) => c.shadow?.backdropMeanLuminance?.value).filter((v): v is number => v != null));
    const sameBackground = cellsAt.filter((c) => c.key.sceneId.startsWith(`${dump.background}__`))
      .map((c) => c.shadow?.backdropMeanLuminance?.value).filter((v): v is number => v != null);
    const aggregate = sameBackground.length === 0 ? null : {
      cells: sameBackground.length,
      min: Math.min(...sameBackground),
      max: Math.max(...sameBackground),
      mean: sameBackground.reduce((a, b) => a + b, 0) / sameBackground.length,
    };
    const tone = fixture.region;

    return found.map((occurrence) => {
      // What the layer is, in the tree's own terms. The effect class is the
      // evidence: a key/fill highlight layer generates the surface's specular,
      // a gradient layer under the tint branch generates the author tint. A label
      // has no effect to read, so it is named by its class — and because it is not
      // inside the surface's subtree, it is also the one role whose surface is
      // resolved by the tree holding exactly one rather than by an ancestor walk.
      const role = occurrence.layerEffect === "CASDFKeyFillHighlightEffect" ? "surface-highlight"
        : occurrence.layerEffect === "CASDFGradientEffect" ? "author-tint"
          : isLabelLayer(occurrence.layerClass) ? "content-label"
            : "unclassified";
      const surface = role === "content-label" ? soleSurfaceOf(layers, occurrence.layerPath)
        : surfaceOf(layers, occurrence.layerPath);
      const elements = elementsOf(surface.backdrop, { x: 0, y: 0 });
      const spanFromDump = elements.length === 0 ? null
        : Math.min(...elements.map((e) => Math.min(e.width, e.height)));
      const glass = (surface.glass.inputs ?? {}) as Record<string, unknown>;
      const colour = (key: string) => (glass[key] as
        { cgColorComponents?: number[] } | null)?.cgColorComponents ?? null;
      const backdropProps = surface.backdrop.properties ?? {};
      const thickness = spanFromDump == null ? null : sizeThickness(spanFromDump);
      return {
        dump: path,
        scene: dump.scene,
        background: dump.background,
        component: dump.component,
        state: dump.state,
        tint: dump.tint,
        colorScheme: dump.colorScheme,
        a11y: dump.a11y,
        scale: dump.backingScaleFactor,
        isKeyWindow: dump.isKeyWindow,
        settleSeconds: dump.settleSeconds,
        os: dump.os,
        layerPath: occurrence.layerPath,
        layerClass: occurrence.layerClass,
        layerName: occurrence.layerName,
        layerEffect: occurrence.layerEffect,
        layerFrame: occurrence.layerFrame,
        layerOpacity: occurrence.layerOpacity,
        role,
        // `inputBackdropAware` is the filter's own statement of what it reads.
        input: occurrence.inputBackdropAware === 1 ? "backdrop-beneath" : "own-content",
        matrix: occurrence.matrix,
        flags: {
          inputBackdropAware: occurrence.inputBackdropAware,
          inputClamp: occurrence.inputClamp,
          inputClampPreserveHue: occurrence.inputClampPreserveHue,
          declaredInputKeys: occurrence.declaredInputKeys,
        },
        operator: decompose(occurrence.matrix),
        surface: {
          containerPath: surface.containerPath,
          spanFromDump,
          spanDeclared: declaredSpans,
          // The dump's rect is the declaration put through CA's own layout, so it
          // arrives with the parent's bounds origin subtracted and can miss the
          // declared integer by an ulp. A tolerance here is arithmetic, not slack:
          // the smallest real span step in the corpus is 8 px.
          spanAgrees: spanFromDump != null
            && declaredSpans.some((d) => Math.abs(d - spanFromDump) < 1e-6),
          elementCount: elements.length,
          elements,
          marginWidth: backdropProps["marginWidth"] ?? null,
          tracksLuma: backdropProps["tracksLuma"] ?? null,
          scale: backdropProps["scale"] ?? null,
        },
        // The body's own adapted state on the same surface, because that is what
        // the operator co-varies with and the co-variation is the finding.
        body: {
          faceColorMatrixBlack: glass["inputFaceColorMatrixBlack"] ?? null,
          faceColorMatrixWhite: glass["inputFaceColorMatrixWhite"] ?? null,
          faceFill: colour("inputFaceColorMatrixFillColor"),
          shadowFill: colour("inputShadowColorMatrixFillColor"),
          clamp: glass["inputClamp"] ?? null,
          clampPreserveHue: glass["inputClampPreserveHue"] ?? null,
          faceFillIsDark: (colour("inputFaceColorMatrixFillColor") ?? [1])[0] === 0,
        },
        backdrop: {
          toneSource: "declared-region-of-fixture",
          tone,
          fixture,
          cellShadowBackdropMeanLuminance: shadowBackdrop,
          cellInteriorMeanBackdrop: interiorBackdrop,
          backgroundShadowAggregate: aggregate,
        },
        // vitrea's own fitted collapse predicate, evaluated at the shipped profile
        // on the harness's recorded backdrop level. Not a fit: a prediction the
        // table records so G1 can see whether the switch already has a law.
        vitrea: {
          sizeThickness: thickness,
          backdropToneAdaptation: tone == null || thickness == null ? null
            : backdropToneAdaptation(tone, thickness),
        },
      };
    });
  });

  // Operator identity: equal within float32 noise is one operator.
  const operators: { id: number; matrix: readonly number[]; count: number }[] = [];
  const withIds: Row[] = rows.map((row) => {
    let match = operators.find((o) => o.matrix.every((v, i) =>
      Math.abs(v - (row.matrix[i] as number)) <= OPERATOR_TOLERANCE));
    if (!match) {
      match = { id: operators.length, matrix: row.matrix, count: 0 };
      operators.push(match);
    }
    match.count += 1;
    return { ...row, operatorId: match.id } as Row;
  });

  // One line per dump, whether or not it contributed a row. A filter that is not
  // there produces no occurrence and would otherwise leave no trace at all, and
  // "the scene declared a label, the tree committed its layer, and the layer
  // carries no operator" is a reading in its own right — the case where Apple
  // installs nothing. It is recorded per dump so that absence is legible in the
  // table beside presence, and so that a labelled dump can never be silently lost.
  const perDump = dumps.map(({ path, dump }) => {
    const labelled = [...index(dump.view.layer).values()].filter((l) => isLabelLayer(l.class));
    return {
      path,
      scene: dump.scene,
      sha256: sha(path),
      colorScheme: dump.colorScheme,
      scale: dump.backingScaleFactor,
      declaredLabel: dump.label ?? null,
      labelLayers: labelled.length,
      labelLayersWithOperator: labelled.filter((l) => (l.filters ?? [])
        .some((f) => f.description === "vibrantColorMatrix")).length,
      occurrences: occurrences(dump.view.layer).length,
    };
  });

  return {
    dumps: perDump,
    specs: specs.map(({ path }) => ({ path, sha256: sha(path) })),
    rows: withIds,
    operators: operators.map((o) => ({ ...o, decomposition: decompose(o.matrix) })),
  };
}

/**
 * A corpus and everything that is true of it as a whole, so that emitting a second
 * table is choosing a corpus rather than copying the reader. `matrixProfileKey` is
 * null where no single configuration describes the corpus, and `lead` is the
 * table's own statement of what it is — the G0 table points at the prose reading
 * committed beside it, and the probe table points at the question it answers.
 */
interface Corpus {
  readonly dirs: readonly string[];
  readonly matrixProfileKey: string | null;
  readonly out: string;
  readonly declaredIn: string;
  readonly title: string;
  readonly lead: readonly string[];
}

const CORPORA: Record<string, Corpus> = {
  g0: {
    dirs: DUMP_DIRS,
    matrixProfileKey: PROFILE_KEY,
    out: OUT,
    declaredIn:
      "W27 coverage wave, W27e G0; claims §5.133; Decision Log 4 and 12; X1/X2/X4/X9",
    title: "# W27e G0: every `vibrantColorMatrix` in the committed layer dumps (2026-09-11)",
    lead: [
      "Generated by `packages/calibration/scripts/vibrancy.ts`; the prose reading of this table is",
      "`reading.md` beside it and the whole record with per-element geometry is `table.json`.",
    ],
  },
  probe: {
    dirs: PROBE_DUMP_DIRS,
    matrixProfileKey: null,
    out: PROBE_OUT,
    declaredIn:
      "W27 coverage wave, W27e; claims §5.133 §2 and §7 — the labelled probe run; X1/X2/X4/X9",
    title: "# W27e: every `vibrantColorMatrix` in the labelled probe dumps (2026-09-11)",
    lead: [
      "Generated by `packages/calibration/scripts/vibrancy.ts --corpus probe`; the whole record",
      "with per-element geometry is `table.json` beside this file. §5.133 §2 found that the",
      "committed corpus carries no label's operator at all, because the reference harness renders",
      "`Color.clear` inside every `glassEffect`; these dumps come from a labelled probe scene spec",
      "through `dump-layers`, which captures no pixels. The two backdrop statistics from",
      "`results/matrix.json` are unavailable here on purpose: this corpus spans both schemes at 2x,",
      "so no single matrix profile key describes it and a cell from another configuration would be",
      "a wrong number rather than a missing one.",
    ],
  },
};

function main(argv: readonly string[]): void {
  const requested = argv.includes("--corpus") ? argv[argv.indexOf("--corpus") + 1] ?? "" : "g0";
  const corpus = CORPORA[requested];
  if (!corpus) throw new Error(`--corpus takes ${Object.keys(CORPORA).join(" or ")}, not ${requested}`);
  const reading = read(corpus.dirs, corpus.matrixProfileKey);
  const foreground = reading.rows.filter((r) => r.role === "surface-highlight");
  const tints = reading.rows.filter((r) => r.role === "author-tint");
  const labels = reading.rows.filter((r) => r.role === "content-label");
  const foregroundOperators = [...new Set(foreground.map((r) => r.operatorId))];
  const labelOperators = [...new Set(labels.map((r) => r.operatorId))];
  // The label half of the reading, hoisted so the table and the markdown state it
  // from one object rather than two that could drift.
  const labelSummary = {
        dumpsDeclaringALabel: reading.dumps.filter((d) => d.declaredLabel != null).length,
        dumpsDeclaringAnAutomaticColour:
          reading.dumps.filter((d) => d.declaredLabel != null && d.declaredLabel.srgb == null).length,
        dumpsDeclaringAnExplicitColour:
          reading.dumps.filter((d) => d.declaredLabel?.srgb != null).length,
        labelLayersCommitted: reading.dumps.reduce((a, d) => a + d.labelLayers, 0),
        labelLayersCarryingAnOperator:
          reading.dumps.reduce((a, d) => a + d.labelLayersWithOperator, 0),
        labelLayersCarryingNothing: reading.dumps
          .filter((d) => d.labelLayers > d.labelLayersWithOperator)
          .map((d) => ({ scene: d.scene, colorScheme: d.colorScheme,
            declaredSrgb: d.declaredLabel?.srgb ?? null })),
        distinctLabelOperators: labelOperators.length,
        labelOperatorCounts: labelOperators.map((id) => ({
          operatorId: id,
          count: labels.filter((r) => r.operatorId === id).length,
          schemes: [...new Set(labels.filter((r) => r.operatorId === id).map((r) => r.colorScheme))],
          spans: [...new Set(labels.filter((r) => r.operatorId === id)
            .map((r) => r.surface.spanFromDump))].sort((a, b) => (a ?? 0) - (b ?? 0)),
          backgrounds: [...new Set(labels.filter((r) => r.operatorId === id)
            .map((r) => r.background))].sort(),
        })),
        // Whether anything but the scheme selects the label's operator. The probe
        // holds a span ladder and a tone ladder for this one line: if either
        // selected, a scheme would carry more than one operator.
        operatorsPerScheme: [...new Set(labels.map((r) => r.colorScheme))].sort().map((scheme) => ({
          colorScheme: scheme,
          operators: [...new Set(labels.filter((r) => r.colorScheme === scheme)
            .map((r) => r.operatorId))],
          spans: [...new Set(labels.filter((r) => r.colorScheme === scheme)
            .map((r) => r.surface.spanFromDump))].sort((a, b) => (a ?? 0) - (b ?? 0)),
          backgrounds: [...new Set(labels.filter((r) => r.colorScheme === scheme)
            .map((r) => r.background))].sort(),
        })),
  };

  const result = {
    declaredIn: corpus.declaredIn,
    provenance: {
      profile: DEFAULT_MATERIAL_PROFILE.backdropToneLow === 0.02 ? "shipped" : "patched",
      matrixProfileKey: corpus.matrixProfileKey,
      matrixSha256: sha("packages/calibration/results/matrix.json"),
      dumpDirectories: corpus.dirs,
      dumpsRead: reading.dumps.length,
      occurrences: reading.rows.length,
      distinctMatrices: reading.operators.length,
      distinctForegroundOperators: foregroundOperators.length,
      schemes: [...new Set(reading.rows.map((r) => r.colorScheme))],
      scales: [...new Set(reading.rows.map((r) => r.scale))],
      a11y: [...new Set(reading.rows.map((r) => r.a11y))],
      states: [...new Set(reading.rows.map((r) => r.state))],
    },
    definitions: {
      matrix: "CAColorMatrix, four rows of five columns, row order; out_i = m_i1·R + m_i2·G + m_i3·B + m_i4·A + m_i5 on the layer's own non-premultiplied channels.",
      operator: `Matrices equal within ${OPERATOR_TOLERANCE} on every one of the twenty floats are one operator. The corpus's smallest real difference is order 1, so the grouping is not sensitive to the tolerance.`,
      decomposition: "Exact least squares for out = m·c + g⊙Y(c) + b with Y fixed at Rec.709 (0.2126, 0.7152, 0.0722) and b read from the fifth column. maxResidual is the largest coefficient the form fails to reproduce, not a fitted slack.",
      role: "From the carrying layer's SDF effect class, which is the tree's own statement of what the layer draws: CASDFKeyFillHighlightEffect is the surface's key/fill specular, CASDFGradientEffect is the author tint's gradient. A label's layer has no effect and is named by its class instead, on the stable CGDrawingLayer suffix of a mangled Swift name whose hash belongs to the framework binary; it also sits outside the surface's subtree, so its surface is the one the tree holds rather than an ancestor.",
      label: "Per dump, from the dump's own top-level `label` field and from the layers whose class carries CGDrawingLayer: whether the scene declared a label, how many label layers the tree committed, and how many of those carry a vibrantColorMatrix. A label layer present with no operator is a reading, not a silence.",
      input: "From inputBackdropAware: 1 means the filter reads the backdrop beneath the layer, null means it reads the layer's own content.",
      span: "The minor dimension of the surface's CASDFElementLayer rects, read from the dump, cross-checked against every committed scene spec that declares the component.",
      tone: "Mean linear luminance of the committed background fixture over the DECLARED component region, read with the harness's own decodePng/componentRegion/interiorLevel. The matrix's two backdrop statistics are recorded beside it and are not the same quantity: shadow.backdropMeanLuminance is the exterior level, and material.interiorMeanBackdrop is taken over the extracted silhouette, which over a high-contrast backdrop is punched out.",
      vitrea: "backdropToneAdaptation(tone, sizeThickness(span)) at the shipped material profile. A prediction recorded beside the reading, never a fit.",
    },
    summary: {
      dumpsRead: reading.dumps.length,
      dumpsWithoutAnyMatrix: reading.dumps.length
        - new Set(reading.rows.map((r) => r.dump)).size,
      occurrences: reading.rows.length,
      surfaceHighlight: foreground.length,
      authorTint: tints.length,
      unclassified: reading.rows.length - foreground.length - tints.length - labels.length,
      distinctForegroundOperators: foregroundOperators.length,
      // The label half of the reading, present only on a corpus that has labels,
      // for the reason `dumps` is projected below. Its shape is the finding: a
      // labelled dump whose label layer carries NOTHING is counted beside one that
      // carries an operator, because "Apple installs nothing here" is the answer on
      // exactly the scenes that name their own colour.
      ...(labels.length === 0 ? {} : { contentLabel: labels.length, label: labelSummary }),
      foregroundOperatorCounts: foregroundOperators.map((id) => ({
        operatorId: id,
        count: foreground.filter((r) => r.operatorId === id).length,
        scenes: foreground.filter((r) => r.operatorId === id).map((r) => r.scene),
      })),
      layerPaths: [...new Set(reading.rows.map((r) => r.layerPath))].sort(),
      spanDisagreements: reading.rows.filter((r) => !r.surface.spanAgrees).map((r) => r.dump),
      // Whether vitrea's own collapse predicate separates the two foreground
      // operators, stated as the gap it leaves rather than as a verdict.
      separation: (() => {
        const value = (r: Row) => r.vitrea.backdropToneAdaptation;
        const dark = foreground.filter((r) => r.operatorId !== foreground[0]?.operatorId);
        const rest = foreground.filter((r) => r.operatorId === foreground[0]?.operatorId);
        const values = (rows: Row[]) => rows.map(value).filter((v): v is number => v != null);
        return {
          predicate: "backdropToneAdaptation(fixture tone over the declared region, sizeThickness(span))",
          minOnDarkOperator: Math.min(...values(dark)),
          maxOnDefaultOperator: Math.max(...values(rest)),
          unevaluated: foreground.length - values(dark).length - values(rest).length,
        };
      })(),
    },
    operators: reading.operators,
    // The per-dump record carries its label columns only where a label exists to
    // report. §5.133's evidence note claims the G0 table is "byte-identical on
    // re-run", and that corpus has no labels in it — so a corpus with none is
    // published in the three-field form it was recorded in, and adding a reading
    // about labels does not silently restate a published one.
    dumps: labels.length === 0 && reading.dumps.every((d) => d.declaredLabel == null)
      ? reading.dumps.map((d) => ({ path: d.path, scene: d.scene, sha256: d.sha256 }))
      : reading.dumps,
    specs: reading.specs,
    rows: reading.rows,
  };

  const n = (x: number | null | undefined, digits = 5) => x == null ? "—" : x.toFixed(digits);
  const vec = (xs: readonly number[], digits = 5) => xs.map((x) => n(x, digits)).join(" / ");
  const tree = (path: string) => path.split("/").slice(3, -1).join("/");
  const markdown = [
    corpus.title,
    "",
    ...corpus.lead,
    "A `CAColorMatrix` is four rows of five columns, row order, and every matrix here factors as",
    "`out = m·c + g⊙Y(c) + b` with `Y` the Rec.709 luma. `—` means unavailable, never zero.",
    "",
    "## The operators",
    "",
    "| id | n | role | R row | G row | B row | A row | m | g | b | level gain | max residual |",
    "| ---: | ---: | --- | --- | --- | --- | --- | ---: | --- | --- | --- | ---: |",
    ...reading.operators.map((o) => {
      const roles = [...new Set(reading.rows.filter((r) => r.operatorId === o.id)
        .map((r) => r.role))].join(", ");
      const row = (i: number) => vec(o.matrix.slice(i * 5, i * 5 + 5), 4);
      const d = o.decomposition;
      return `| ${o.id} | ${o.count} | ${roles} | ${row(0)} | ${row(1)} | ${row(2)} | ${row(3)} `
        + `| ${n(d.chromaGain, 4)} | ${vec(d.lumaGain, 4)} | ${vec(d.offset, 4)} `
        + `| ${vec(d.levelGain, 4)} | ${d.maxResidual.toExponential(2)} |`;
    }),
    "",
    "What each operator does to a colour, before `inputClamp`:",
    "",
    "| id | black | mid grey | white | red | green | blue |",
    "| ---: | --- | --- | --- | --- | --- | --- |",
    ...reading.operators.map((o) => `| ${o.id} | `
      + ["black", "grey50", "white", "red", "green", "blue"]
        .map((k) => vec(o.decomposition.maps[k] ?? [], 3)).join(" | ") + " |"),
    "",
    // Emitted only where there are labels to report, so the G0 table — published
    // evidence about a corpus that has none — keeps the shape it was recorded in.
    ...(labels.length === 0 ? [] : [
      "## The label",
      "",
      "A label layer that carries no operator is a reading, not a silence: it is Apple declining to",
      "rewrite a colour the author named. Counted per dump for that reason.",
      "",
      `- dumps declaring a label: **${labelSummary.dumpsDeclaringALabel}** `
      + `(${labelSummary.dumpsDeclaringAnAutomaticColour} taking the automatic colour, `
      + `${labelSummary.dumpsDeclaringAnExplicitColour} naming their own)`,
      `- label layers committed: **${labelSummary.labelLayersCommitted}**, of which `
      + `**${labelSummary.labelLayersCarryingAnOperator}** carry a \`vibrantColorMatrix\``,
      `- distinct label operators: **${labelSummary.distinctLabelOperators}**`,
      "",
      "| scene | scheme | declared label colour | operator |",
      "| --- | --- | --- | ---: |",
      ...reading.dumps.filter((d) => d.declaredLabel != null).map((d) => {
        const row = labels.find((r) => r.dump === d.path);
        const declared = d.declaredLabel?.srgb == null ? "automatic (`Color.primary`)"
          : `explicit ${JSON.stringify(d.declaredLabel.srgb)}`;
        return `| ${d.scene} | ${d.colorScheme} | ${declared} | `
          + `${row ? row.operatorId : "**none — no filter on the label layer**"} |`;
      }),
      "",
      "Operators per scheme, with everything the probe varied inside each — if span or backdrop tone",
      "selected the label's operator, a scheme would carry more than one.",
      "",
      "| scheme | operators | spans | backgrounds |",
      "| --- | --- | --- | --- |",
      ...labelSummary.operatorsPerScheme.map((s) =>
        `| ${s.colorScheme} | ${s.operators.join(", ")} | ${s.spans.join(", ")} | `
        + `${s.backgrounds.join(", ")} |`),
      "",
    ]),
    "## The cells",
    "",
    "`tone` is the mean linear luminance of the committed background fixture over the declared",
    "component region; `matrix tone` is `shadow.backdropMeanLuminance` / `material.interiorMeanBackdrop`",
    `from \`results/matrix.json\` at \`${PROFILE_KEY}\`, recorded beside it because neither is the same`,
    "quantity and they disagree on the impulse background. `adapt` is",
    "`backdropToneAdaptation(tone, sizeThickness(span))` at the shipped profile — a prediction",
    "recorded beside the reading, not a fit.",
    "",
    "| tree | scene | role | layer | effect | input | op | span | tracksLuma "
      + "| tone | matrix tone | adapt | face black / white | face fill |",
    "| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: | --- | --- |",
    ...reading.rows.map((r) => {
      const num = (x: unknown) => typeof x === "number" ? n(x, 4) : "—";
      return `| ${tree(r.dump)} | ${r.scene} | ${r.role} | ${r.layerPath} `
        + `| ${(r.layerEffect ?? "—").replace("CASDF", "")} | ${r.input} | ${r.operatorId} `
        + `| ${n(r.surface.spanFromDump, 0)} | ${String(r.surface.tracksLuma)} `
        + `| ${n(r.backdrop.tone)} `
        + `| ${n(r.backdrop.cellShadowBackdropMeanLuminance)} `
        + `/ ${n(r.backdrop.cellInteriorMeanBackdrop)} `
        + `| ${n(r.vitrea.backdropToneAdaptation)} `
        + `| ${num(r.body.faceColorMatrixBlack)} / ${num(r.body.faceColorMatrixWhite)} `
        + `| ${r.body.faceFill ? vec(r.body.faceFill, 3) : "—"} |`;
    }),
    "",
  ].join("\n");

  const dir = process.env["W27E_OUT"] ?? corpus.out;
  mkdirSync(resolve(ROOT, dir), { recursive: true });
  writeFileSync(resolve(ROOT, dir, "table.json"), `${JSON.stringify(result, null, 2)}\n`,
    { flag: "wx" });
  writeFileSync(resolve(ROOT, dir, "table.md"), `${markdown}\n`, { flag: "wx" });
  const label = labels.length === 0 ? ""
    : `, ${labels.length} on a label in ${labelOperators.length} operator(s)`;
  process.stdout.write(
    `${reading.dumps.length} dumps, ${reading.rows.length} matrices, `
    + `${reading.operators.length} distinct, ${foregroundOperators.length} foreground operators`
    + `${label}; wrote ${relative(ROOT, resolve(ROOT, dir))}\n`);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  main(process.argv.slice(2));
}
