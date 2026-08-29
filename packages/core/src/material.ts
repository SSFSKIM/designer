/**
 * §Material variants.
 *
 * `regular` is the adaptive default. `clear` is persistently more transparent
 * with constrained adaptation, and it *requires* a dimming policy — without one
 * there is nothing keeping foreground content legible over a busy backdrop.
 *
 * Two deliberate choices here:
 *
 * - A `clear` surface with no dimming policy resolves to `regular` and raises a
 *   dev-mode **error**. Applying an invented policy silently would be the one
 *   thing this codebase refuses: pretending to a capability the author never
 *   configured. Falling back to `regular` cannot produce an illegible surface,
 *   and `DEFAULT_CLEAR_DIMMING` makes satisfying the requirement a one-liner.
 * - Mixing variants inside one GlassGroup **warns** and changes nothing. Apple's
 *   guidance is not to mix; coercing one of the two would silently discard an
 *   author's intent, which is worse than a surface that looks wrong on purpose.
 */

import type { DiagnosticsChannel } from "./diagnostics";

export const MATERIAL_VARIANTS = ["regular", "clear"] as const;

export type MaterialVariant = (typeof MATERIAL_VARIANTS)[number];

/**
 * An author's tint seed, sRGB-encoded, 0..1 per channel.
 *
 * Encoded rather than linear because this is the number the author wrote: a CSS
 * colour, parsed. The conversion into the working space belongs to whichever
 * tier is drawing, and core carries no colour maths.
 */
export type TintColor = readonly [r: number, g: number, b: number];

/**
 * §Material tint — the author-facing half of Apple's `Glass.tint(_:)`.
 *
 * **A tint is a seed, not a fill.** Apple states the mechanism plainly:
 * "selecting a color generates a range of tones that are **mapped to content
 * brightness underneath** the tinted element… changing its hue, brightness and
 * saturation depending on what's behind without deviating too much from the
 * intended color" (WWDC25 session 219). A flat overlay of the seed is the
 * failure Apple names in the same session — "completely opaque and breaks the
 * visual character of Liquid Glass" — so this value is carried to the renderers
 * as a seed and tone-mapped there, per pixel, against the backdrop the material
 * is already sampling.
 *
 * Two axes, kept apart on purpose, because Apple's own vocabulary overloads the
 * word:
 *
 * - **This is the colour axis.** It says what colour the material's tint layer
 *   is. It never changes how much of that layer there is.
 * - The **alpha axis** — how opaque the tint layer is — is the material's
 *   calibrated `tintAlpha`, the same quantity reduced transparency lifts. That
 *   is where the *user's* system preference lives (iOS 26.1's Clear/Tinted
 *   toggle "increases the opacity of Liquid Glass and adds more contrast"; OS
 *   27's slider runs the same axis continuously, "ultra clear to fully
 *   tinted"). A future reference migration therefore lands on the occlusion
 *   axis and cannot collide with an author's tint.
 *
 * `strength` is the author's own subtlety knob and comes from the seed colour's
 * alpha — `rgba(255, 149, 0, 0.5)` is a half-strength orange, exactly as
 * `Color.orange.opacity(0.5)` is in SwiftUI. It says how far the material's tint
 * colour moves from its neutral (profile) tint toward the tone, and at 0 the
 * material is byte-identical to an untinted one.
 */
export interface GlassTint {
  readonly color: TintColor;
  /** How far the material's tint moves toward the tone, 0..1. */
  readonly strength: number;
}

const clamp01 = (value: number): number => Math.min(1, Math.max(0, value));

/** A tint with its channels clamped into range. `strength` defaults to fully tinted. */
export function glassTint(color: TintColor, strength = 1): GlassTint {
  return {
    color: [clamp01(color[0]), clamp01(color[1]), clamp01(color[2])],
    strength: clamp01(strength),
  };
}

/**
 * A tint that would change nothing is no tint.
 *
 * Zero strength has to collapse to `undefined` rather than travel as data: the
 * renderers take a tinted path only when a tint is present, and a
 * strength-0 tint reaching that path would cost a byte of rounding on a surface
 * the author asked to leave alone.
 */
function normaliseTint(tint: GlassTint | null | undefined): GlassTint | undefined {
  if (tint === null || tint === undefined) return undefined;
  const normalised = glassTint(tint.color, tint.strength);
  return normalised.strength === 0 ? undefined : normalised;
}

/** The scrim laid beneath clear glass so foreground content stays legible. */
export interface DimmingPolicy {
  /** Scrim opacity, 0..1. */
  readonly scrim: number;
  /** Which way the scrim pushes the backdrop — dark content over light, or the reverse. */
  readonly direction: "darken" | "lighten";
}

/**
 * Advisory default, named as a delegated unknown in §Calibration: the harness
 * fits the real value. Its purpose here is to make the requirement cheap to
 * satisfy, not to be correct.
 */
export const DEFAULT_CLEAR_DIMMING: DimmingPolicy = { scrim: 0.28, direction: "darken" };

/** A group's material defaults. A node inherits `variant` and `tint` when it declares none. */
export interface MaterialProfile {
  readonly variant: MaterialVariant;
  /** Required for any clear surface in the group. */
  readonly dimming?: DimmingPolicy;
  /** Group-wide tint seed. A node overrides it, or clears it with `null`. */
  readonly tint?: GlassTint;
}

export interface ResolvedMaterial {
  readonly variant: MaterialVariant;
  /** Regular adapts to the backdrop; clear's response is deliberately constrained. */
  readonly adaptation: "adaptive" | "constrained";
  /** Present exactly when `variant` is `"clear"`. */
  readonly dimming?: DimmingPolicy;
  /** Absent when the surface is untinted, or when its tint has no strength. */
  readonly tint?: GlassTint;
}

export interface MaterialRequest {
  readonly variant: MaterialVariant;
  readonly dimming?: DimmingPolicy;
  /** The tint this surface resolved to — its own, or the group's. */
  readonly tint?: GlassTint | null;
  /** Named in diagnostics; also the dedupe subject. */
  readonly nodeId?: string;
  readonly diagnostics?: DiagnosticsChannel;
}

export function resolveMaterial(request: MaterialRequest): ResolvedMaterial {
  const { variant, dimming, nodeId, diagnostics } = request;
  const tint = normaliseTint(request.tint);
  const tinted = tint === undefined ? {} : { tint };

  if (variant === "regular") return { variant: "regular", adaptation: "adaptive", ...tinted };

  if (dimming === undefined) {
    diagnostics?.report({
      code: "clear-variant-needs-dimming",
      severity: "error",
      subjects: [nodeId ?? "*"],
      message: `The clear variant requires a dimming policy (§Material variants); without one its foreground is not guaranteed legible. This surface rendered as regular instead. Supply one on the group's material profile — DEFAULT_CLEAR_DIMMING is a usable starting point.`,
    });
    return { variant: "regular", adaptation: "adaptive", ...tinted };
  }

  return { variant: "clear", adaptation: "constrained", dimming, ...tinted };
}

/** Two tints are the same seed when every channel and the strength agree. */
function sameTint(a: GlassTint | undefined, b: GlassTint | undefined): boolean {
  if (a === undefined || b === undefined) return a === b;
  return (
    a.strength === b.strength &&
    a.color[0] === b.color[0] &&
    a.color[1] === b.color[1] &&
    a.color[2] === b.color[2]
  );
}

export interface TintMixingCheck {
  readonly groupId: string;
  readonly members: readonly { readonly nodeId: string; readonly tint?: GlassTint }[];
  readonly diagnostics?: DiagnosticsChannel;
}

/**
 * Report a group whose members ask for **different** tint seeds.
 *
 * A group is one sampling region and one optics pass, so the GPU tier carries
 * one seed per group and a per-pixel strength — which is exactly enough for the
 * composition Apple's guidance describes ("apply color to the background rather
 * than to symbols… refrain from adding color to the background of multiple
 * controls"): one emphasised control inside a toolbar of plain ones. Two
 * different hues in one group is outside that, and the two tiers would then
 * disagree — the CSS tier styles each host element on its own and can honour
 * both. So it warns and changes nothing, on the same reasoning as
 * `checkVariantMixing`: coercing one of the two would silently discard an
 * author's intent.
 *
 * Untinted members are not a mix. They are the ordinary case the mechanism is
 * for, and their strength is simply zero.
 */
export function checkTintMixing(check: TintMixingCheck): boolean {
  const { groupId, members, diagnostics } = check;

  const tinted = members.filter(
    (member): member is { nodeId: string; tint: GlassTint } => member.tint !== undefined,
  );
  const distinct = tinted.filter(
    (member, index) => tinted.findIndex((other) => sameTint(other.tint, member.tint)) === index,
  );
  if (distinct.length < 2) return false;

  const name = (list: typeof tinted) => list.map((member) => member.nodeId).join(", ");
  diagnostics?.report({
    code: "tint-mixing",
    severity: "warning",
    subjects: [groupId],
    message: `Group "${groupId}" asks for ${distinct.length} different tint seeds (${name(tinted)}). A group is one optics pass and carries one seed, so the GPU tier paints them all with the first surface's colour while the CSS tier honours each — the two tiers will not agree. Apple's guidance is to tint one control rather than several; give a second tinted surface its own GlassGroup if it really needs a different colour.`,
  });

  return true;
}

export interface VariantMixingCheck {
  readonly groupId: string;
  readonly members: readonly { readonly nodeId: string; readonly variant: MaterialVariant }[];
  readonly diagnostics?: DiagnosticsChannel;
}

/**
 * Report a group whose members do not agree on a variant. Returns whether they
 * were mixed; changes nothing either way.
 */
export function checkVariantMixing(check: VariantMixingCheck): boolean {
  const { groupId, members, diagnostics } = check;

  const regular = members.filter((member) => member.variant === "regular");
  const clear = members.filter((member) => member.variant === "clear");
  if (regular.length === 0 || clear.length === 0) return false;

  const name = (list: typeof members) => list.map((member) => member.nodeId).join(", ");
  diagnostics?.report({
    code: "variant-mixing",
    severity: "warning",
    subjects: [groupId],
    message: `Group "${groupId}" mixes material variants, which Apple's guidance advises against: regular on ${name(regular)}, clear on ${name(clear)}. Both render as authored — split them into separate groups if the mix was not deliberate.`,
  });

  return true;
}
