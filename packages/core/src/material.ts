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

/** A group's material defaults. A node inherits `variant` when it declares none. */
export interface MaterialProfile {
  readonly variant: MaterialVariant;
  /** Required for any clear surface in the group. */
  readonly dimming?: DimmingPolicy;
}

export interface ResolvedMaterial {
  readonly variant: MaterialVariant;
  /** Regular adapts to the backdrop; clear's response is deliberately constrained. */
  readonly adaptation: "adaptive" | "constrained";
  /** Present exactly when `variant` is `"clear"`. */
  readonly dimming?: DimmingPolicy;
}

export interface MaterialRequest {
  readonly variant: MaterialVariant;
  readonly dimming?: DimmingPolicy;
  /** Named in diagnostics; also the dedupe subject. */
  readonly nodeId?: string;
  readonly diagnostics?: DiagnosticsChannel;
}

export function resolveMaterial(request: MaterialRequest): ResolvedMaterial {
  const { variant, dimming, nodeId, diagnostics } = request;

  if (variant === "regular") return { variant: "regular", adaptation: "adaptive" };

  if (dimming === undefined) {
    diagnostics?.report({
      code: "clear-variant-needs-dimming",
      severity: "error",
      subjects: [nodeId ?? "*"],
      message: `The clear variant requires a dimming policy (§Material variants); without one its foreground is not guaranteed legible. This surface rendered as regular instead. Supply one on the group's material profile — DEFAULT_CLEAR_DIMMING is a usable starting point.`,
    });
    return { variant: "regular", adaptation: "adaptive" };
  }

  return { variant: "clear", adaptation: "constrained", dimming };
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
