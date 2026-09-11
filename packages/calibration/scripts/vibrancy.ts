/**
 * W27e G0 / claims §5.133: read every `vibrantColorMatrix` in the committed layer
 * dumps and say what is there. No fit, no capture, no runtime material.
 *
 * Run with `pnpm --filter @vitrea/calibration --fail-if-no-match exec tsx
 * scripts/vibrancy.ts`. Set `W27E_OUT` to a scratch directory to reproduce the
 * table without replacing the recorded one; the canonical outputs are create-only.
 *
 * Everything here is read from files already in git: the five layer-dump trees,
 * the scene specs those runs were driven from, and `results/matrix.json` for the
 * backdrop level. Nothing decodes a pixel and nothing calls the capture harness,
 * so the reading is reproducible on any machine and cannot move the bed.
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

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), "../../..");
const OUT = "packages/calibration/results/2026-09-11-w27e-g0-vibrancy";

/**
 * Every committed layer-dump tree, in the order the waves recorded them. The list
 * is explicit rather than globbed: a tree that appears later must be added here
 * deliberately, and the test pins how many dumps these five directories hold, so
 * a dump appearing or disappearing is a failing test rather than a quiet reading.
 */
const DUMP_DIRS = [
  "packages/calibration/results/2026-09-03-w12-lens/layer-dumps",
  "packages/calibration/results/2026-09-03-w12-lens/layer-dumps-ramp",
  "packages/calibration/results/2026-09-03-w12-lens/layer-dumps-adapt",
  "packages/calibration/results/2026-09-05-w18-union-contour/probe/layer-dumps",
  "packages/calibration/results/2026-09-05-w20-capsule-corner/g0/layer-dumps",
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
  "packages/calibration/results/2026-09-03-w12-lens/layer-dumps-ramp/scenes.json",
] as const;

/** Every dump in the corpus is this configuration; the matrix is read at it. */
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
interface Dump {
  readonly scene: string;
  readonly background: string;
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
  readonly components: Record<string, Component>;
  readonly scenes: readonly { id: string; component: string }[];
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

/** One `vibrantColorMatrix` as found, before the cell's own facts are attached. */
interface Occurrence {
  readonly layerPath: string;
  readonly layerClass: string;
  readonly layerName: string | null;
  readonly layerEffect: string | null;
  readonly layerFrame: Layer["frame"];
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
  readonly role: string;
  readonly input: string;
  readonly matrix: readonly number[];
  readonly operator: Decomposition;
  readonly surface: { readonly spanFromDump: number | null; readonly spanAgrees: boolean };
  readonly vitrea: { readonly backdropToneAdaptation: number | null };
}

/** The whole reading, as data; `main` only formats it. */
export function read() {
  const specs = SPEC_FILES.map((path) => ({ path, spec: readJson<SceneSpec>(path) }));
  const matrix = readJson<{ cells: MatrixCell[] }>("packages/calibration/results/matrix.json");
  const cellsAt = matrix.cells.filter((c) => c.key.profileKey === PROFILE_KEY);

  const dumps = DUMP_DIRS.flatMap((dir) => readdirSync(join(ROOT, dir)).sort()
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
    const toneSource = shadowBackdrop != null ? "cell"
      : aggregate != null ? "background-aggregate" : "absent";
    const tone = shadowBackdrop ?? aggregate?.mean ?? null;

    return found.map((occurrence) => {
      const surface = surfaceOf(layers, occurrence.layerPath);
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
        // What the layer is, in the tree's own terms. The effect class is the
        // evidence: a key/fill highlight layer generates the surface's specular,
        // a gradient layer under the tint branch generates the author tint.
        role: occurrence.layerEffect === "CASDFKeyFillHighlightEffect" ? "surface-highlight"
          : occurrence.layerEffect === "CASDFGradientEffect" ? "author-tint"
            : "unclassified",
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
          toneSource,
          tone,
          cellShadowBackdropMeanLuminance: shadowBackdrop,
          cellInteriorMeanBackdrop: interiorBackdrop,
          backgroundAggregate: aggregate,
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

  return {
    dumps: dumps.map(({ path, dump }) => ({ path, scene: dump.scene, sha256: sha(path) })),
    specs: specs.map(({ path }) => ({ path, sha256: sha(path) })),
    rows: withIds,
    operators: operators.map((o) => ({ ...o, decomposition: decompose(o.matrix) })),
  };
}

function main(): void {
  const reading = read();
  const foreground = reading.rows.filter((r) => r.role === "surface-highlight");
  const tints = reading.rows.filter((r) => r.role === "author-tint");
  const foregroundOperators = [...new Set(foreground.map((r) => r.operatorId))];
  const result = {
    declaredIn: "W27 coverage wave, W27e G0; claims §5.133; Decision Log 4 and 12; X1/X2/X4/X9",
    provenance: {
      profile: DEFAULT_MATERIAL_PROFILE.backdropToneLow === 0.02 ? "shipped" : "patched",
      matrixProfileKey: PROFILE_KEY,
      matrixSha256: sha("packages/calibration/results/matrix.json"),
      dumpDirectories: DUMP_DIRS,
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
      role: "From the carrying layer's SDF effect class, which is the tree's own statement of what the layer draws: CASDFKeyFillHighlightEffect is the surface's key/fill specular, CASDFGradientEffect is the author tint's gradient.",
      input: "From inputBackdropAware: 1 means the filter reads the backdrop beneath the layer, null means it reads the layer's own content.",
      span: "The minor dimension of the surface's CASDFElementLayer rects, read from the dump, cross-checked against every committed scene spec that declares the component.",
      tone: "shadow.backdropMeanLuminance from results/matrix.json at the 1x light standard profile — the scene's own recorded backdrop level. Where the scene has no cell, the mean over cells of the same background id, flagged as background-aggregate.",
      vitrea: "backdropToneAdaptation(tone, sizeThickness(span)) at the shipped material profile. A prediction recorded beside the reading, never a fit.",
    },
    summary: {
      dumpsRead: reading.dumps.length,
      dumpsWithoutAnyMatrix: reading.dumps.length
        - new Set(reading.rows.map((r) => r.dump)).size,
      occurrences: reading.rows.length,
      surfaceHighlight: foreground.length,
      authorTint: tints.length,
      unclassified: reading.rows.length - foreground.length - tints.length,
      distinctForegroundOperators: foregroundOperators.length,
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
          predicate: "backdropToneAdaptation(shadow.backdropMeanLuminance, sizeThickness(span))",
          minOnDarkOperator: Math.min(...values(dark)),
          maxOnDefaultOperator: Math.max(...values(rest)),
          unevaluated: foreground.length - values(dark).length - values(rest).length,
        };
      })(),
    },
    operators: reading.operators,
    dumps: reading.dumps,
    specs: reading.specs,
    rows: reading.rows,
  };

  const dir = process.env["W27E_OUT"] ?? OUT;
  mkdirSync(resolve(ROOT, dir), { recursive: true });
  writeFileSync(resolve(ROOT, dir, "table.json"), `${JSON.stringify(result, null, 2)}\n`,
    { flag: "wx" });
  process.stdout.write(
    `${reading.dumps.length} dumps, ${reading.rows.length} matrices, `
    + `${reading.operators.length} distinct, ${foregroundOperators.length} foreground operators; `
    + `wrote ${relative(ROOT, resolve(ROOT, dir, "table.json"))}\n`);
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) main();
