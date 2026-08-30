/**
 * The two gates `compare` applies to its own output, as pure predicates.
 *
 * They live here rather than in `compare.ts` because that file is a script — it
 * calls `main()` at module scope — so nothing can import a helper out of it
 * without running a whole comparison. Both decisions guard the same failure
 * mode: a matrix file that looks like evidence and is not one.
 */

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
