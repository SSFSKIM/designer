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
 * Phase discipline is enforced, not documented. Consuming the dirty set outside
 * `write`, measuring outside `read`, and restructuring the graph once the
 * renderer is walking it each report a `frame-phase-violation`. None of them
 * throws: a violated frame still draws, and a diagnostic that costs a frame is
 * one a host will silence rather than fix.
 */

import { FRAME_PHASES, type FrameInfo, type FramePhase } from "./frame";
import type {
  BackdropRebuildRequest,
  GlassScene,
  PlaneOverlap,
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
  /** Same-plane overlaps found after the read phase, in dev mode. */
  readonly overlaps: readonly PlaneOverlap[];
  /** Everything handed out this frame, whether a participant asked or not. */
  readonly rebuilds: readonly BackdropRebuildRequest[];
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

      for (const phase of FRAME_PHASES) {
        scene.setFramePhase(phase);

        if (phase === "update") resolution = scene.resolve();

        for (const participant of [...participants.values()]) {
          participant[phase]?.(contextFor(phase));
        }

        // Bounds are freshest here, and the check must finish before the
        // renderer acts on a layout the sandwich cannot express.
        if (phase === "read") overlaps = scene.checkSamePlaneOverlap();

        // Whatever no participant claimed is still this frame's work: the report
        // is the whole truth about what needed rebuilding, not what was asked for.
        if (phase === "write") rebuilds.push(...scene.consumeDirtyBackdropSources(frame.id));
      }

      scene.setFramePhase(undefined);

      return {
        frame,
        // `update` always runs, so this is always assigned by the time it is read.
        resolution: resolution ?? scene.resolve(),
        overlaps,
        rebuilds,
      };
    },
  };
}
