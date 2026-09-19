/**
 * W29 G3b — score `bound.json` over the 27 receded rows.
 *
 *   npx tsx results/2026-09-19-w29-g3b-shadow-recede/score-bound.ts \
 *     [--matrix <matrix.json>] [--captures <web-captures dir>] [--out <verdict.json>]
 *
 * The three clauses of `results/2026-09-11-w27c-g1b/bound.json`, carried to the
 * 27 bed by `bound.json` beside this file and evaluated exactly as that file
 * declares them — which is why this reads the bound rather than restating it.
 * **It holds no copy of a threshold**, no copy of the checking-set rule and no
 * list of cells: the thresholds, the scope rule and the composite exclusion are
 * parsed out of `bound.json`, and the checking set is reconstructed from
 * `scenes.json`'s split and the fixture manifest, independently of whatever the
 * read happened to capture. A scorer that could disagree with the declaration
 * about what was declared is not expressible.
 *
 * Two metrics, and they come from two places for a stated reason.
 * `oklabDeltaEMean` is read off the matrix row, because it is the canonical
 * quantity `adopted-thresholds.test.ts` gates and re-deriving it here would be a
 * second opinion about a committed number. `bodyDeltaE` — the OKLab distance
 * over the declared box eroded `ERODE_CSS_PX` — is not a row the matrix carries,
 * so it is computed here from the committed native fixture and the canonical web
 * capture the same row was measured from, through the package's own
 * `declaredBox` and `oklabDistance`. Adding it to the schema instead would move
 * every cell of both beds for one gate's benefit.
 */
import { existsSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";

import {
  decodePng,
  oklabDistance,
  srgbByteToOklab,
  type CalibrationImage,
} from "../../src/index";
import { declaredBox, ERODE_CSS_PX, type DeclaredBox } from "../../cli/native-delta-readers";
import { declaredComponentOf, readSceneGeometry } from "../../cli/scene-geometry";

const HERE = import.meta.dirname;
const PACKAGE_ROOT = resolve(HERE, "..", "..");
const REPO_ROOT = resolve(PACKAGE_ROOT, "..", "..");
const REFERENCE = resolve(REPO_ROOT, "apps", "reference-apple");
const FIXTURES = resolve(REFERENCE, "fixtures");

const say = (line: string): void => void process.stdout.write(`${line}\n`);

const flag = (name: string): string | undefined => {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : undefined;
};

const MATRIX_PATH = resolve(PACKAGE_ROOT, flag("matrix") ?? "results/matrix.json");
const CAPTURES = resolve(PACKAGE_ROOT, flag("captures") ?? "web-captures");
const OUT = resolve(flag("out") ?? resolve(HERE, "verdict-recede.json"));

const readJson = <T,>(path: string): T => JSON.parse(readFileSync(path, "utf8")) as T;

// ---------------------------------------------------------------------------
// The declaration, read rather than restated
// ---------------------------------------------------------------------------

interface Bound {
  readonly scope: {
    readonly expectedCheckingCells: Readonly<Record<string, number>>;
    readonly notScoredOnClauses2And3: {
      readonly components: readonly string[];
      readonly expectedCells: number;
    };
  };
  readonly clauses: readonly {
    readonly id: string;
    readonly name: string;
    readonly thresholds?: Readonly<Record<string, number>>;
  }[];
}

const bound = readJson<Bound>(resolve(HERE, "bound.json"));
const thresholdsOf = (id: string): Readonly<Record<string, number>> => {
  const clause = bound.clauses.find((c) => c.id === id);
  if (clause?.thresholds === undefined) throw new Error(`score-bound: clause ${id} has no thresholds`);
  return clause.thresholds;
};
const CEILING = thresholdsOf("1");
const MEAN_BOUND = thresholdsOf("2");
const COMPOSITES = new Set(bound.scope.notScoredOnClauses2And3.components);

// ---------------------------------------------------------------------------
// The checking set, reconstructed from the declaration and the manifest
// ---------------------------------------------------------------------------

interface SceneSpec {
  readonly scenes: readonly { readonly id: string; readonly component: string; readonly state: string }[];
  readonly split: Readonly<Record<string, readonly string[]>>;
}
interface Manifest {
  readonly profiles: readonly {
    readonly profileKey: string;
    readonly fixtures: readonly { readonly sceneId: string; readonly file: string; readonly fixtureSet: string }[];
  }[];
}

const spec = readJson<SceneSpec>(resolve(REFERENCE, "scenes.json"));
const manifest = readJson<Manifest>(resolve(FIXTURES, "manifest.json"));
const geometryMatrix = readSceneGeometry(REFERENCE);

const setOf = new Map<string, string>();
for (const [set, ids] of Object.entries(spec.split)) {
  if (!Array.isArray(ids)) continue;
  for (const id of ids) setOf.set(id, set);
}
const componentOf = new Map(spec.scenes.map((scene) => [scene.id, scene.component]));
const stateOf = new Map(spec.scenes.map((scene) => [scene.id, scene.state]));

/** The scope rule of `bound.json`, applied rather than a list of cells. */
const inCheckingSet = (profileKey: string, sceneId: string): boolean =>
  profileKey in CEILING &&
  stateOf.get(sceneId) === "inactive" &&
  (setOf.get(sceneId) === "validation" || setOf.get(sceneId) === "holdout");

// ---------------------------------------------------------------------------
// The body metric
// ---------------------------------------------------------------------------

/** OKLab distance over the declared box eroded 6 CSS px, and the two levels in it. */
function bodyReading(
  native: CalibrationImage,
  web: CalibrationImage,
  box: DeclaredBox,
  scale: number,
): { readonly deltaE: number; readonly n: number } {
  const e = ERODE_CSS_PX * scale;
  let sum = 0;
  let count = 0;
  for (let y = 0; y < native.height; y += 1) {
    const yc = y + 0.5;
    if (yc < box.y0 + e || yc >= box.y1 - e) continue;
    for (let x = 0; x < native.width; x += 1) {
      const xc = x + 0.5;
      if (xc < box.x0 + e || xc >= box.x1 - e) continue;
      const src = (y * native.width + x) * 4;
      sum += oklabDistance(
        srgbByteToOklab(native.data[src] ?? 0, native.data[src + 1] ?? 0, native.data[src + 2] ?? 0),
        srgbByteToOklab(web.data[src] ?? 0, web.data[src + 1] ?? 0, web.data[src + 2] ?? 0),
      );
      count += 1;
    }
  }
  if (count === 0) throw new Error("score-bound: the eroded declared box is empty");
  return { deltaE: sum / count, n: count };
}

// ---------------------------------------------------------------------------
// The rows
// ---------------------------------------------------------------------------

interface Cell {
  readonly key: {
    readonly profileKey: string;
    readonly sceneId: string;
    readonly web: { readonly renderer: string; readonly capturePath: string };
  };
  readonly fixtureSet: string;
  readonly state?: string;
  readonly tier: "texture" | "dom";
  readonly perceptual?: Record<string, { readonly value: number } | undefined>;
}

const matrix = readJson<{ readonly cells: readonly Cell[] }>(MATRIX_PATH);

/** The receded generation: rows posed with a candidate receded document. */
const RECEDED = /recededProfile=(\S+) sha256:([0-9a-f]{12})/;

interface Row {
  readonly profileKey: string;
  readonly sceneId: string;
  readonly tier: "texture" | "dom";
  readonly fixtureSet: string;
  readonly component: string;
  readonly scored: boolean;
  readonly recededDocument: string;
  readonly recededSha256: string;
  readonly fullCanvasDeltaE: number;
  readonly bodyDeltaE: number | null;
  readonly bodyPixels: number | null;
  readonly clause1: { readonly threshold: number; readonly holds: boolean };
  readonly clause3: { readonly ceiling: number; readonly holds: boolean } | null;
}

const fixtureOf = new Map<string, { file: string; fixtureSet: string }>();
for (const profile of manifest.profiles) {
  for (const fixture of profile.fixtures) {
    fixtureOf.set(`${profile.profileKey} ${fixture.sceneId}`, fixture);
  }
}

const scaleOf = (profileKey: string): number => (profileKey.includes("-2x-") ? 2 : 1);

const rows: Row[] = [];
const unreadable: string[] = [];
for (const cell of matrix.cells) {
  const match = RECEDED.exec(cell.key.web.capturePath);
  if (match === null) continue;
  const { profileKey, sceneId } = cell.key;
  if (!inCheckingSet(profileKey, sceneId)) continue;
  const full = cell.perceptual?.["oklabDeltaEMean"]?.value;
  if (full === undefined) {
    unreadable.push(`${profileKey} / ${sceneId} / ${cell.tier}: no oklabDeltaEMean`);
    continue;
  }
  const component = componentOf.get(sceneId) ?? "?";
  const scale = scaleOf(profileKey);

  let body: number | null = null;
  let pixels: number | null = null;
  if (!COMPOSITES.has(component)) {
    const declared = declaredComponentOf(geometryMatrix, sceneId);
    const box = declaredBox(declared, geometryMatrix.canvas, scale);
    const fixture = fixtureOf.get(`${profileKey} ${sceneId}`);
    const renderer = cell.key.web.renderer;
    const capture = resolve(CAPTURES, profileKey, sceneId, `${sceneId}__${renderer}.png`);
    if (box === null) {
      unreadable.push(`${profileKey} / ${sceneId}: ${component} has no declared box`);
    } else if (fixture === undefined || !existsSync(capture)) {
      unreadable.push(`${profileKey} / ${sceneId} / ${cell.tier}: no fixture or no capture on disk`);
    } else {
      const reading = bodyReading(
        decodePng(readFileSync(resolve(FIXTURES, fixture.file))),
        decodePng(readFileSync(capture)),
        box,
        scale,
      );
      body = reading.deltaE;
      pixels = reading.n;
    }
  }

  const ceiling = CEILING[profileKey] as number;
  const twice = 2 * (MEAN_BOUND[profileKey] as number);
  rows.push({
    profileKey,
    sceneId,
    tier: cell.tier,
    fixtureSet: cell.fixtureSet,
    component,
    scored: true,
    recededDocument: match[1] ?? "",
    recededSha256: match[2] ?? "",
    fullCanvasDeltaE: full,
    bodyDeltaE: body,
    bodyPixels: pixels,
    clause1: { threshold: ceiling, holds: full <= ceiling },
    clause3: body === null ? null : { ceiling: twice, holds: body <= twice },
  });
}

// ---------------------------------------------------------------------------
// The verdict
// ---------------------------------------------------------------------------

const TIERS = ["texture", "dom"] as const;
const profiles = Object.keys(CEILING).sort();
const perProfile: Record<string, unknown> = {};
let jointHolds = 0;

for (const profileKey of profiles) {
  const forProfile: Record<string, unknown> = {};
  for (const tier of TIERS) {
    const mine = rows.filter((r) => r.profileKey === profileKey && r.tier === tier);
    if (mine.length === 0) {
      forProfile[tier] = { cells: 0, verdict: "no row" };
      continue;
    }
    const withBody = mine.filter((r) => r.bodyDeltaE !== null);
    const mean =
      withBody.length === 0
        ? null
        : withBody.reduce((a, r) => a + (r.bodyDeltaE as number), 0) / withBody.length;
    const c1 = mine.filter((r) => !r.clause1.holds);
    const c3 = mine.filter((r) => r.clause3 !== null && !r.clause3.holds);
    const bound2 = MEAN_BOUND[profileKey] as number;
    const c2holds = mean !== null && mean <= bound2;
    const holds = c1.length === 0 && c2holds && c3.length === 0;
    if (tier === "texture" && holds) jointHolds += 1;
    forProfile[tier] = {
      cells: mine.length,
      cellsWithBody: withBody.length,
      expectedCells: bound.scope.expectedCheckingCells[profileKey],
      clause1: {
        threshold: CEILING[profileKey],
        worst: Math.max(...mine.map((r) => r.fullCanvasDeltaE)),
        worstCell: mine.reduce((a, b) => (b.fullCanvasDeltaE > a.fullCanvasDeltaE ? b : a)).sceneId,
        misses: c1.map((r) => ({ sceneId: r.sceneId, set: r.fixtureSet, value: r.fullCanvasDeltaE })),
        holds: c1.length === 0,
      },
      clause2: { threshold: bound2, mean, holds: c2holds },
      clause3: {
        ceiling: 2 * bound2,
        worst: withBody.length === 0 ? null : Math.max(...withBody.map((r) => r.bodyDeltaE as number)),
        worstCell:
          withBody.length === 0
            ? null
            : withBody.reduce((a, b) => ((b.bodyDeltaE as number) > (a.bodyDeltaE as number) ? b : a))
                .sceneId,
        misses: c3.map((r) => ({
          sceneId: r.sceneId,
          set: r.fixtureSet,
          value: r.bodyDeltaE,
          multiple: (r.bodyDeltaE as number) / bound2,
        })),
        holds: c3.length === 0,
      },
      joint: holds,
    };
  }
  perProfile[profileKey] = forProfile;
}

const verdict = {
  gate: "W29 G3b / claims §5.154",
  bound: "results/2026-09-19-w29-g3b-shadow-recede/bound.json",
  matrix: MATRIX_PATH.replace(`${REPO_ROOT}/`, ""),
  captures: CAPTURES.replace(`${REPO_ROOT}/`, ""),
  scoredAt: new Date().toISOString(),
  checkingCells: rows.length,
  cellsWithoutABody: rows.filter((r) => r.bodyDeltaE === null).length,
  compositesDeclared: bound.scope.notScoredOnClauses2And3.expectedCells,
  unreadable,
  recededDocuments: [...new Set(rows.map((r) => `${r.recededDocument} sha256:${r.recededSha256}`))].sort(),
  perProfile,
  rows: rows.sort((a, b) =>
    `${a.profileKey}${a.tier}${a.sceneId}`.localeCompare(`${b.profileKey}${b.tier}${b.sceneId}`),
  ),
};

mkdirSync(resolve(OUT, ".."), { recursive: true });
writeFileSync(OUT, `${JSON.stringify(verdict, null, 1)}\n`);

say(`checking cells read: ${String(rows.length)} (${String(verdict.cellsWithoutABody)} with no declared box)`);
for (const line of unreadable) say(`  UNREADABLE ${line}`);
for (const profileKey of profiles) {
  const forProfile = perProfile[profileKey] as Record<string, Record<string, unknown>>;
  for (const tier of TIERS) {
    const t = forProfile[tier];
    if (t === undefined || t["cells"] === 0) {
      say(`${profileKey} / ${tier}: no row`);
      continue;
    }
    const c1 = t["clause1"] as { worst: number; holds: boolean; threshold: number };
    const c2 = t["clause2"] as { mean: number | null; holds: boolean; threshold: number };
    const c3 = t["clause3"] as { worst: number | null; holds: boolean; ceiling: number; worstCell: string | null };
    say(
      `${profileKey} / ${tier} (${String(t["cells"])} cells)\n` +
        `  clause 1  worst ${c1.worst.toFixed(6)} / ${String(c1.threshold)}   ${c1.holds ? "holds" : "MISS"}\n` +
        `  clause 2  mean  ${c2.mean === null ? "—" : c2.mean.toFixed(6)} / ${String(c2.threshold)}   ${c2.holds ? "holds" : "MISS"}\n` +
        `  clause 3  worst ${c3.worst === null ? "—" : c3.worst.toFixed(6)} / ${String(c3.ceiling)} (${c3.worstCell ?? "—"})   ${c3.holds ? "holds" : "MISS"}\n` +
        `  joint     ${t["joint"] === true ? "HOLDS" : "DOES NOT HOLD"}`,
    );
  }
}
say(`\ntexture-tier profiles holding jointly: ${String(jointHolds)} of ${String(profiles.length)}`);
say(`written ${OUT.replace(`${REPO_ROOT}/`, "")}`);
