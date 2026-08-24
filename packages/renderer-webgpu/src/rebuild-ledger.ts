/**
 * The §Core model invariant, as a testable object.
 *
 * > blur/analysis pyramids belong to `BackdropSource`, rebuilt **at most once per
 * > dirty source per frame** — never per group.
 *
 * core enforces one half of that: `consumeDirtyBackdropSources(frameId)` hands out
 * one pass over the dirty set per frame id, so a second caller in the same frame
 * gets nothing. What core cannot see is the renderer's side — a renderer that also
 * rebuilt lazily on first draw, or that rebuilt once per group from a single
 * request, would satisfy core's guard and still violate the invariant.
 *
 * So the ledger lives here, apart from the GPU work it guards, for one reason: it
 * makes the invariant assertable against core's real scheduler with no adapter and
 * no device. `pyramid.ts` claims through it before it encodes a single pass, and
 * `test/dirty-epoch.test.ts` drives core's own scene and scheduler over this same
 * object. An invariant tested only through a GPU is an invariant tested only where
 * a GPU exists.
 */

export interface RebuildLedger {
  /** Begin a frame. Clears the per-frame tally. */
  beginFrame(frameId: number): void;
  readonly frameId: number | undefined;
  /**
   * Claim the one rebuild this source is allowed this frame. `false` means it has
   * already had it — the caller must not encode a second one.
   */
  claim(sourceId: string): boolean;
  /** Record that a claim did no work because the source was clean. */
  recordClean(): void;
  /** Rebuilds recorded for `sourceId` in the frame being recorded. */
  countInFrame(sourceId: string): number;
  readonly rebuilds: number;
  readonly refusedDuplicates: number;
  readonly skippedClean: number;
  /**
   * Highest per-source rebuild count seen in any single frame. The invariant is
   * exactly the statement that this never exceeds 1.
   */
  readonly peakPerSourcePerFrame: number;
}

export function createRebuildLedger(): RebuildLedger {
  const perFrame = new Map<string, number>();
  let frameId: number | undefined;
  let rebuilds = 0;
  let refused = 0;
  let clean = 0;
  let peak = 0;

  return {
    beginFrame(next) {
      frameId = next;
      perFrame.clear();
    },

    get frameId() {
      return frameId;
    },

    claim(sourceId) {
      const already = perFrame.get(sourceId) ?? 0;
      if (already > 0) {
        refused += 1;
        return false;
      }
      const count = already + 1;
      perFrame.set(sourceId, count);
      peak = Math.max(peak, count);
      rebuilds += 1;
      return true;
    },

    recordClean() {
      clean += 1;
    },

    countInFrame(sourceId) {
      return perFrame.get(sourceId) ?? 0;
    },

    get rebuilds() {
      return rebuilds;
    },

    get refusedDuplicates() {
      return refused;
    },

    get skippedClean() {
      return clean;
    },

    get peakPerSourcePerFrame() {
      return peak;
    },
  };
}
