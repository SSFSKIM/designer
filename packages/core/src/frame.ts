/**
 * The frame vocabulary, shared by the scene and the scheduler.
 *
 * It lives in its own module because both need it: the scheduler drives the
 * phases, and the scene uses the current phase to gate the operations that only
 * make sense in one of them.
 *
 * The five phases are the pipeline the spec describes: collect what changed,
 * read the DOM once in a batch, update the scene from those reads, write the GPU
 * resources, then render. Their point is ordering discipline — every layout read
 * in one place so the steady state performs none, and every scene mutation
 * finished before the renderer starts walking the graph.
 */

export const FRAME_PHASES = ["collect", "read", "update", "write", "render"] as const;

export type FramePhase = (typeof FRAME_PHASES)[number];

/**
 * What a host knows about the frame it is driving. `timeMs` arrives as a number
 * because core reads no clock (X4) — it is the host's monotonic timestamp.
 */
export interface FrameInfo {
  /** Monotonically increasing. Also the scope for at-most-once-per-frame work. */
  readonly id: number;
  readonly timeMs: number;
}
