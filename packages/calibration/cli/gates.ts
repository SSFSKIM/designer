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

import type { FixtureSet } from "../src/index";

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
 * mismatched target costs a whole browser capture run before failing — and the
 * default target is `results/matrix.json`, which wave Decision Log 15 ruling 3
 * deliberately freezes at the schema the inactive-bed gate was adopted against.
 * During that interregnum the documented default invocation is precisely the one
 * that cannot succeed, so it should say so before doing any work rather than
 * after.
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
  return (
    `${path} is a schema-${existingVersion} matrix and this build writes schema ${buildVersion}, so it ` +
    `can be neither read nor merged into. If that is the frozen inactive-bed matrix, it is meant to ` +
    `stay frozen (wave Decision Log 15 ruling 3) — send this run somewhere else with ` +
    `--out-matrix results/<name>.json.`
  );
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
