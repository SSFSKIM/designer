import type { MotionChannel } from "./channels";

/** v1 interaction states (§Motion). Neighbor glow diffusion is post-v1. */
export const INTERACTION_STATES = [
  "idle",
  "hover",
  "pressed",
  "focused",
  "disabled",
  "morphing",
] as const;

export type InteractionState = (typeof INTERACTION_STATES)[number];

/**
 * Which states each state may move to.
 *
 * Nearly everything is reachable from everything: a touch press arrives with no
 * hover before it, a pointer can leave while held, and any of them can be
 * disabled or start morphing. Two edges are missing on purpose:
 *
 * - out of `disabled`, only `idle`. A disabled control offers no press or focus
 *   affordance, so re-enabling lands at rest and the host's next event decides
 *   what it becomes. `applyFlags` routes through `idle` on its own.
 * - out of `morphing`, no `pressed`. A surface mid-morph is not yet a press
 *   target; press-during-morph is post-v1, in line with §v1 scope shipping one
 *   morph pair.
 *
 * A state is always allowed to transition to itself, as an accepted no-op.
 */
export const LEGAL_TRANSITIONS: Readonly<Record<InteractionState, readonly InteractionState[]>> = {
  idle: ["hover", "pressed", "focused", "disabled", "morphing"],
  hover: ["idle", "pressed", "focused", "disabled", "morphing"],
  pressed: ["idle", "hover", "focused", "disabled", "morphing"],
  focused: ["idle", "hover", "pressed", "disabled", "morphing"],
  disabled: ["idle"],
  morphing: ["idle", "hover", "focused", "disabled"],
};

export function canTransition(from: InteractionState, to: InteractionState): boolean {
  return from === to || LEGAL_TRANSITIONS[from].includes(to);
}

/**
 * What a host observes. These overlap in reality — a control can be focused and
 * hovered and held at once — while §Motion names one state at a time, so the
 * kernel owns the collapse rather than leaving each binding to invent it.
 */
export interface InteractionFlags {
  readonly disabled: boolean;
  readonly morphing: boolean;
  readonly pressed: boolean;
  readonly hovered: boolean;
  readonly focused: boolean;
}

/**
 * Collapse overlapping flags to the one state that describes the material.
 *
 * `disabled` outranks everything because it withdraws the affordance; `morphing`
 * next because the surface is mid-transition; `pressed` next because direct
 * manipulation reads over anything ambient. `hovered` outranks `focused`
 * deliberately: focus has its own affordance in the semantic host DOM (a ring,
 * per §rendering contract), so the *material* spends its one slot on the more
 * immediate pointer feedback.
 */
export function resolveInteractionState(flags: InteractionFlags): InteractionState {
  if (flags.disabled) return "disabled";
  if (flags.morphing) return "morphing";
  if (flags.pressed) return "pressed";
  if (flags.hovered) return "hover";
  if (flags.focused) return "focused";
  return "idle";
}

/**
 * Per-state channel targets.
 *
 * Targets are stored per state, not per transition. A state's target vector is
 * where the material rests in that state, so arriving at `hover` from `pressed`
 * and from `idle` necessarily lands on the same place — path independence is
 * structural rather than a property each transition row has to get right. What
 * a transition *does* is therefore derivable: `channelsMovedBy` reads it off the
 * two vectors, and the asymmetries a per-transition table would encode by hand
 * (glow attacking on press, decaying on release) come from the driver families
 * instead.
 *
 * A channel absent from a state's vector is not driven by interaction state and
 * keeps whatever target it already had.
 */
export type StateTargets = Readonly<Partial<Record<MotionChannel, number>>>;
export type StateTargetTable = Readonly<Record<InteractionState, StateTargets>>;

/**
 * The channels a transition actually moves — the per-transition view of the
 * state table, for tests and for callers that want to know what a state change
 * will disturb before making it.
 */
export function channelsMovedBy(
  table: StateTargetTable,
  from: InteractionState,
  to: InteractionState,
): readonly MotionChannel[] {
  const source = table[from];
  const destination = table[to];
  return (Object.keys(destination) as MotionChannel[]).filter(
    (channel) => destination[channel] !== source[channel],
  );
}
