/**
 * The frame-phase contract, and a reference implementation of it.
 *
 * Core is **passive**. There is no timer, no `requestAnimationFrame`, and no
 * clock read anywhere here — a host calls `runFrame` and supplies the frame's
 * time as a number. platform-web owns the rAF loop and drives this; the same
 * scheduler runs in a test with hand-written frame ids and no browser at all.
 *
 * The pipeline is fixed:
 *
 * ```
 * collect  what changed since the last frame is marked dirty
 * read     every layout measurement, batched, so the steady state performs none
 * update   the scene resolves: capability state, policies, dev-mode checks
 * write    GPU resources are brought up to date — where rebuilds are handed out
 * render   drawing, with the graph frozen
 * ```
 *
 * `update` resolves the scene *before* the first update hook runs, and that
 * ordering is the contract rather than an implementation detail: every phase from
 * `update` onward reads a resolution describing the graph as it stood at the top
 * of that phase. So the graph is structurally frozen from `update` on — the scene
 * reports a register or a remove there as a `frame-phase-violation`, because a
 * hook that restructures the graph leaves the frame's resolution describing a
 * graph that no longer exists. Structural reconciliation belongs in `collect`;
 * `update` is where reads become resolved state.
 *
 * Phase discipline is enforced, not documented. Consuming the dirty set outside
 * `write`, measuring outside `read`, and restructuring the graph once it has
 * resolved each report a `frame-phase-violation`. None of them throws: a violated
 * frame still draws, and a diagnostic that costs a frame is one a host will
 * silence rather than fix.
 */

import { FRAME_PHASES, type FrameInfo, type FramePhase } from "./frame";
import type {
  BackdropRebuildRequest,
  GlassScene,
  PlaneOverlap,
  ProxyOverlap,
  SceneResolution,
} from "./scene";

/** What a hook is handed. Valid for the phase it was passed to, and no longer. */
export interface FrameContext {
  readonly frame: FrameInfo;
  readonly phase: FramePhase;
  readonly scene: GlassScene;
  /** The frame's resolution. Absent before the update phase has produced it. */
  readonly resolution?: SceneResolution;
  /**
   * The backdrop sources needing a pyramid rebuild this frame. Legal in the
   * `write` phase, and at most once per frame however many participants ask —
   * the §Core model invariant, enforced rather than asserted.
   */
  consumeDirtyBackdropSources(): readonly BackdropRebuildRequest[];
}

/**
 * A hook per phase; every one optional. platform-web registers one participant
 * for the DOM host layer and the renderer registers another, so neither has to
 * know the other exists.
 */
export interface FrameParticipant {
  readonly id: string;
  readonly collect?: (context: FrameContext) => void;
  readonly read?: (context: FrameContext) => void;
  readonly update?: (context: FrameContext) => void;
  readonly write?: (context: FrameContext) => void;
  readonly render?: (context: FrameContext) => void;
}

export interface FrameReport {
  readonly frame: FrameInfo;
  readonly resolution: SceneResolution;
  /** Same-plane surface overlaps found after the read phase, in dev mode. */
  readonly overlaps: readonly PlaneOverlap[];
  /** Groups whose padded proxies would cover the same pixels — X1's other half. */
  readonly proxyOverlaps: readonly ProxyOverlap[];
  /**
   * The rebuilds a write participant actually claimed — nothing more. The
   * scheduler never consumes on the frame's own behalf, because consuming
   * advances the source's `builtEpoch`: a rebuild taken so the report could be
   * "complete" would leave the source looking clean with no renderer having built
   * anything, and the pyramid would never be rebuilt. A frame with nobody to do
   * the work — no renderer registered yet, or one sitting out a device-loss
   * recovery — must therefore hand out nothing at all.
   */
  readonly rebuilds: readonly BackdropRebuildRequest[];
  /**
   * The source ids still dirty when the frame ended: whatever no participant
   * claimed, plus sources no group samples yet. Read with the non-consuming peek,
   * so a frame is never charged a rebuild for being reported on. A rebuild
   * survives here until a renderer takes it, which is precisely what lets
   * device-loss recovery pick the work back up instead of losing it.
   */
  readonly pendingSources: readonly string[];
}

export interface FrameScheduler {
  /** Registering an existing id replaces that participant. */
  addParticipant(participant: FrameParticipant): void;
  removeParticipant(id: string): void;
  readonly participants: readonly FrameParticipant[];
  runFrame(frame: FrameInfo): FrameReport;
}

export interface FrameSchedulerOptions {
  readonly scene: GlassScene;
}

export function createFrameScheduler(options: FrameSchedulerOptions): FrameScheduler {
  const { scene } = options;
  const participants = new Map<string, FrameParticipant>();

  return {
    addParticipant(participant) {
      participants.set(participant.id, participant);
    },

    removeParticipant(id) {
      participants.delete(id);
    },

    get participants() {
      return [...participants.values()];
    },

    runFrame(frame) {
      let resolution: SceneResolution | undefined;
      let overlaps: readonly PlaneOverlap[] = [];
      let proxyOverlaps: readonly ProxyOverlap[] = [];
      const rebuilds: BackdropRebuildRequest[] = [];

      const contextFor = (phase: FramePhase): FrameContext => ({
        frame,
        phase,
        scene,
        ...(resolution === undefined ? {} : { resolution }),
        consumeDirtyBackdropSources: () => {
          if (phase !== "write") {
            scene.diagnostics.report({
              code: "frame-phase-violation",
              severity: "error",
              subjects: [phase],
              message: `The dirty backdrop set was consumed during the "${phase}" phase. Pyramid rebuilds belong to the "write" phase, after the scene has resolved and before anything draws.`,
            });
            return [];
          }
          const handed = scene.consumeDirtyBackdropSources(frame.id);
          rebuilds.push(...handed);
          return handed;
        },
      });

      try {
        for (const phase of FRAME_PHASES) {
          scene.setFramePhase(phase);

          // Resolving before the first update hook is what freezes the graph for
          // the rest of the frame: everything after this reads a resolution of
          // the graph as it stands right here.
          if (phase === "update") resolution = scene.resolve();

          for (const participant of [...participants.values()]) {
            participant[phase]?.(contextFor(phase));
          }

          // Bounds are freshest here, and both checks must finish before the
          // renderer acts on a layout the sandwich cannot express.
          if (phase === "read") {
            overlaps = scene.checkSamePlaneOverlap();
            proxyOverlaps = scene.checkGroupProxyOverlap();
          }
        }
      } finally {
        // A hook that throws still ends the frame. Left at the failing phase, the
        // scene would report the host's own error recovery — tearing the failed
        // node down, remeasuring — as phase violations it never committed, and
        // every later frame would inherit the same lie.
        scene.setFramePhase(undefined);
      }

      return {
        frame,
        // `update` always runs, so this is always assigned by the time it is read.
        resolution: resolution ?? scene.resolve(),
        overlaps,
        proxyOverlaps,
        rebuilds,
        pendingSources: scene.dirtyBackdropSources().map((source) => source.descriptor.id),
      };
    },
  };
}
