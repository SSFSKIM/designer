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
