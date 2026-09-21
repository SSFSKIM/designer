/**
 * The gates `compare` applies to its own output and its own inputs, as pure
 * (or near-pure — `colourlessTintEvidence` reads fixture bytes, nothing else)
 * functions.
 *
 * They live here rather than in `compare.ts` because that file is a script — it
 * calls `main()` at module scope — so nothing can import a helper out of it
 * without running a whole comparison. Every decision here guards the same
 * failure mode: an artifact that looks like evidence and is not one.
 */

import { createHash } from "node:crypto";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import type { FixtureSet, SceneState } from "../src/index";

/**
 * mtime comparisons have to tolerate a coarse clock. Some filesystems store
 * mtime at whole-second resolution, so a file genuinely written 300ms into the
 * run can report a timestamp before the run started. A second of slack cannot
 * admit a stale capture: the artifacts this predicate guards are minutes or
 * hours old, being leftovers from a previous run.
 */
const MTIME_GRANULARITY_MS = 1_000;

/**
 * Was this capture artifact written by the run that started at `runStartedAtMs`?
 *
 * The question exists because `capture-web` resolves the renderer off the page
 * rather than off the request: asked for the WebGPU tier on a machine that
 * refuses the adapter, it captures the CSS tier, writes `__css` artifacts and
 * exits 0. `compare` then selects `__webgpu` filenames — and without this check
 * measures whatever `__webgpu` pixels an earlier run happened to leave on disk,
 * under a matrix key that is byte-identical to a real GPU-tier result.
 */
export function isCaptureFresh(mtimeMs: number, runStartedAtMs: number): boolean {
  return mtimeMs + MTIME_GRANULARITY_MS >= runStartedAtMs;
}

/**
 * May this run overwrite the official matrix?
 *
 * Not when any cell failed to measure, unless asked to. The matrix is keyed per
 * cell and upserted, so a run with holes in it writes a file that mixes this
 * run's cells with a previous run's — valid-looking, internally inconsistent,
 * and indistinguishable afterwards from a clean full run.
 */
export function shouldWriteMatrix(failureCount: number, writePartial: boolean): boolean {
  return failureCount === 0 || writePartial;
}

/**
 * Why this run may not write to the matrix already on disk at `path` — or
 * `undefined` when it may.
 *
 * A run upserts into whatever matrix it finds at its output path, so a file
 * written under a different schema can be neither read nor merged into. The
 * reader refuses it, correctly; what this predicate fixes is *when*.
 * Deserialisation happens after the capture step, so without an up-front check a
 * mismatched target costs a whole browser capture run before failing.
 *
 * The committed `results/matrix.json` is at the schema this build writes, so the
 * default invocation is not the case this guards: what it guards is a run sent at
 * a matrix written under an older instrument — a scratch file, a matrix restored
 * from a branch, or a committed matrix a future bump leaves behind, as wave
 * Decision Log 15 ruling 3 deliberately did until the post-W8 pass re-read the
 * bed. (Corrected 2026-09-20, W30 G1 review closure, c9a §5.157 §10: this
 * paragraph still described that interregnum as the present. The MESSAGE below
 * still did too, and is rewritten 2026-09-21 by W31 G2, c9a §5.163 §5.)
 *
 * A predicate rather than an assertion, so the CLIs that need it phrase the
 * refusal in their own terms and this file stays free of I/O.
 */
export function matrixSchemaRefusal(
  existingVersion: number,
  buildVersion: number,
  path: string,
): string | undefined {
  if (existingVersion === buildVersion) return undefined;
  /*
   * What the operator is actually holding, as of W31 (c9a §5.163 §5).
   *
   * The message this replaced offered "If that is the frozen inactive-bed
   * matrix, it is meant to stay frozen (wave Decision Log 15 ruling 3)". That
   * was true during the schema-4/5 interregnum, when the committed default
   * target was itself a refused file and a reader landing here had most likely
   * just run `compare` with no flags. The post-W8 pass re-read the bed and ended
   * it: `results/matrix.json` is at schema 5 and has been for eleven waves, so
   * nobody arrives here from the default invocation any more, and a sentence
   * telling them their file is meant to stay frozen sends them to look for a
   * ruling that no longer applies to anything.
   *
   * A run that trips this today got here by naming a target, and there are only
   * three such files: a scratch matrix an earlier `--out-matrix` wrote, one
   * restored from a branch or from `git show`, and a superseded generation under
   * `results/superseded/`. All three are readings taken under an older
   * instrument, and the answer for all three is the same — this build cannot
   * merge into them, and it must not rewrite them either, because a recorded
   * number is never rewritten.
   */
  const direction = existingVersion < buildVersion ? "an older" : "a newer";
  return (
    `${path} is a schema-${existingVersion} matrix and this build writes schema ${buildVersion}, so it ` +
    `can be neither read nor merged into. A file at ${direction} schema is a reading taken under ` +
    `${direction === "an older" ? "an earlier" : "a later"} instrument: the usual ones are a scratch matrix an earlier ` +
    `--out-matrix wrote, one restored from a branch, and a superseded generation under ` +
    `results/superseded/. None of them is a target to write into — a recorded number is never ` +
    `rewritten — so send this run somewhere else with --out-matrix results/<name>.json.`
  );
}

// ---------------------------------------------------------------------------
// The pose and the scheme a capture actually resolved
// ---------------------------------------------------------------------------

/**
 * The two resolved readouts `capture-web` writes onto `report__<renderer>.json`,
 * under `page` — where the page's own readbacks live, beside what was requested.
 */
export interface CaptureReadout {
  readonly windowActivation?: string;
  readonly colorScheme?: string;
  /**
   * The candidate receded document the harness merged, where one was injected
   * (W29 G3b). `null` or absent on every other path.
   */
  readonly candidateRecededMaterialProfile?: unknown;
}

export interface CaptureReport {
  readonly page?: CaptureReadout;
}

/**
 * Why this capture may not be measured as this cell — or `undefined` when it may.
 *
 * Neither the window-activation pose nor the colour scheme is visible in the PNG,
 * and neither is in the matrix key: an inactive cell's `key.web.capturePath` is
 * byte-identical to its active twin's on the same profile, because the pose and the
 * receded document's identity appear nowhere in the grammar. So a capture filed
 * under an `__inactive` scene id that had in fact resolved `"active"` would be the
 * active material published under the recede's name, with nothing in the committed
 * artifacts to expose it afterwards. `scene.ts` reports what resolved; this is what
 * stands between that report and a published row, and it is the only thing that does.
 *
 * The scheme is here for the same reason one level down. A capture is filed under a
 * profile key that names a scheme, the driver declares that scheme on the browser
 * context, and the page reads that declaration once — so a context that did not take
 * the declaration produces a light capture under a dark profile's key, and every
 * figure measured over it is a fidelity reading of the wrong material.
 *
 * **An absent `windowActivation` is a pre-W28-G4 capture, not a pose.** Before that
 * gate the page could only pin the root active, so an unlabelled capture can only be
 * an active-pose one: it is accepted for a scene declared `rest` or `pressed`, and
 * refused for one declared `inactive`, where its silence is exactly the claim that
 * cannot be taken on trust. The scheme readback arrived in the same change, so an
 * unlabelled capture carries no scheme to compare and is judged on the pose alone.
 *
 * **One named exception, and it is the whole reason this function has a third
 * branch** (W29 G3b, Decision Log 6 (d)). A capture posed with a CANDIDATE
 * receded document resolves `windowActivation: "active"` by construction: the
 * page merges the candidate over the active document and pins the root active,
 * because a root that receded itself would apply the shipped difference and the
 * candidate would never draw. Refusing it would make a fitted endpoint
 * unmeasurable; waving every active resolution through would give back exactly
 * the mistake above. So the recede is admitted on the evidence that it happened —
 * `candidateRecededMaterialProfile` non-null in the same report — and on nothing
 * else. The cell's `capturePath` carries that document's hash, so the row says
 * which endpoint drew it and cannot be confused with a runtime-posed one.
 */
export function capturePoseRefusal(
  report: CaptureReport,
  state: SceneState,
  colorScheme: "light" | "dark",
): string | undefined {
  const expected = state === "inactive" ? "inactive" : "active";
  const resolved = report.page?.windowActivation;
  const candidate = report.page?.candidateRecededMaterialProfile;
  const posedByCandidate =
    typeof candidate === "object" && candidate !== null && !Array.isArray(candidate);
  if (expected === "inactive" && resolved === "active" && posedByCandidate) {
    return schemeRefusal(report, colorScheme);
  }
  if (resolved === undefined) {
    if (expected === "active") return undefined;
    return (
      `the capture carries no resolved windowActivation, so it predates W28 G4 and can only be an ` +
      `active-pose capture — but this scene is declared ${state}`
    );
  }
  if (resolved !== expected) {
    return (
      `the scene is declared ${state}, so the capture had to resolve windowActivation ` +
      `'${expected}' and resolved '${resolved}'`
    );
  }
  return schemeRefusal(report, colorScheme);
}

/** The scheme half of the check above, shared with the candidate-receded branch. */
function schemeRefusal(
  report: CaptureReport,
  colorScheme: "light" | "dark",
): string | undefined {
  const resolvedScheme = report.page?.colorScheme;
  if (resolvedScheme !== colorScheme) {
    return (
      `the cell is planned under a ${colorScheme} profile and the capture resolved colorScheme ` +
      `'${resolvedScheme ?? "(absent)"}'`
    );
  }
  return undefined;
}

// ---------------------------------------------------------------------------
// The tint axis: admitted only by a bed that demonstrably carried colour
// ---------------------------------------------------------------------------

/** The scene-matrix and native-manifest shapes `colourlessTintEvidence` reads. */
export interface SceneEntry {
  readonly id: string;
  readonly background: string;
  readonly component: string;
  readonly state: string;
  /** A key into the matrix's `tints` registry (W3). Absent on an untinted scene. */
  readonly tint?: string;
}

export interface SceneSpec {
  readonly scenes: readonly SceneEntry[];
  readonly split: Readonly<Record<FixtureSet, readonly string[]>>;
}

export interface FixtureEntry {
  readonly sceneId: string;
  readonly file: string;
  readonly fixtureSet: FixtureSet;
  readonly captureMethod: string;
  readonly materialRendered: boolean;
  readonly identicalToBackground?: boolean;
}

export interface ManifestProfile {
  readonly profileKey: string;
  readonly colorScheme: "light" | "dark";
  /** The System Settings state the fixtures were captured under. */
  readonly a11yMode: string;
  readonly display?: { readonly actualBackingScale?: number };
  readonly fixtures: readonly FixtureEntry[];
}

export interface Manifest {
  readonly backgrounds: Readonly<Record<string, string>>;
  readonly profiles: readonly ManifestProfile[];
  readonly caveats: readonly string[];
}

/**
 * Evidence that this bed's capture session did not carry the author tint's
 * COLOUR into the material — or `undefined` when it did.
 *
 * The test is byte-identity and nothing else, which is what makes it
 * unarguable: two scenes that share a background, a component and a state and
 * differ only in *which* tint they declare cannot render to the same bytes if
 * the seed reached the material. `systemOrange` and `systemBlue` are not the
 * same colour. When they produce the same file, the seed was dropped somewhere
 * between the registry and the composite, and every number measured over a
 * tinted fixture is a measurement of the UNTINTED material wearing a tinted
 * scene id — the exact failure the tint plan's "refuse rather than guess" rule
 * at the harness's own load step was written to prevent, one level deeper.
 *
 * **Why one duplicate condemns the whole tint axis rather than the pair.** A
 * manifest is written by one binary in one capture session. A tint path that
 * dropped the seed for `photo__capsule-button__rest-tint-blue` dropped it for
 * every other tinted scene in that same session too; the pairs are merely where
 * the drop is *visible*, because they are the only places the bed declares two
 * seeds over one scene. Admitting `light-solid__capsule-button__rest-tint-orange`
 * on the grounds that nothing contradicts it would be filing the untinted
 * material under a tinted key with no duplicate left to expose it.
 *
 * **The inactive pose is excluded from the scan, not swept into it.** W27c G1
 * (claims §5.128) recovered 121 inactive fixtures whose own evidence is that the
 * window-recede pose drops the author tint's HUE by design — "orange and blue
 * give the same inactive level on the checkerboard" is the wave's own finding,
 * not a capture defect. A byte-identical `…__inactive-tint-orange` /
 * `…__inactive-tint-blue` pair is therefore the expected reading, and scanning
 * it here would condemn the whole tint axis, active scenes included, on a
 * signal that active scenes never produced. Only a group whose scenes are in a
 * pose that is supposed to CARRY hue — `rest`, `pressed` — is evidence that the
 * capture session dropped it; `inactive` groups are skipped before the digest
 * comparison ever runs, so this guard stays exactly as strict as it was for the
 * pose it was written for.
 *
 * No threshold and no colour model on purpose. A chroma-response floor would be
 * a number that a bed could meet by accident, and this question does not need
 * one to be answered.
 */
export interface ColourlessTintEvidence {
  readonly profileKey: string;
  readonly scenes: readonly [string, string];
}

export function colourlessTintEvidence(
  spec: SceneSpec,
  manifest: Manifest,
  fixturesDir: string,
): ColourlessTintEvidence | undefined {
  const sceneById = new Map(spec.scenes.map((scene) => [scene.id, scene]));
  const digest = (file: string): string =>
    createHash("sha256").update(readFileSync(resolve(fixturesDir, file))).digest("hex");

  for (const profile of manifest.profiles) {
    // Grouped by everything a tint is orthogonal to, so the only difference
    // left inside a group is the declared seed.
    const groups = new Map<string, FixtureEntry[]>();
    for (const fixture of profile.fixtures) {
      const scene = sceneById.get(fixture.sceneId);
      if (scene?.tint === undefined) continue;
      // The recovered inactive pose is exempt: its own evidence (claims
      // §5.128) is that the window-recede drops hue by design, so a
      // byte-identical orange/blue pair there is the expected reading, not a
      // capture defect. Scanning it would condemn the active poses' real tint
      // on a signal only the inactive pose was ever going to produce.
      if (scene.state === "inactive") continue;
      const base = `${scene.background}|${scene.component}|${scene.state}`;
      groups.set(base, [...(groups.get(base) ?? []), fixture]);
    }
    for (const group of groups.values()) {
      if (group.length < 2) continue;
      const byDigest = new Map<string, string>();
      for (const fixture of group) {
        const hash = digest(fixture.file);
        const twin = byDigest.get(hash);
        if (twin !== undefined) {
          return { profileKey: profile.profileKey, scenes: [twin, fixture.sceneId] };
        }
        byDigest.set(hash, fixture.sceneId);
      }
    }
  }
  return undefined;
}
