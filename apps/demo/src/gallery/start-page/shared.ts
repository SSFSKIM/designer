/**
 * The size family and the one backdrop every group reads (`DESIGN.md`, family and groups).
 */

import {
  DEFAULT_CLEAR_DIMMING,
  type DimmingPolicy,
  type GlassTextureBackdrop,
} from "@vitreajs/vitrea-react";
import type { CSSProperties } from "react";

import type { Box } from "./environment";

/**
 * The page is written in English for a person who lives outside Siena, so it keeps the 24-hour
 * clock and day-month dates of British English wherever the browser's own locale would differ.
 */
export const LOCALE = "en-GB";

/** One thickness across every surface on the page: the home default, no reason to leave it. */
export const THICKNESS = 8;
/** Windows and the module: a generous fixed corner, the page's concentric anchor. */
export const WINDOW_RADIUS = 32;
/** The platter: a multi-row surface keeps a rounded rectangle, equal to its closed capsule's. */
export const PLATTER_RADIUS = 24;

/** The texture source id the environment canvas is supplied under. */
export const ENVIRONMENT_ID = "daybreak";
export const ENVIRONMENT_BACKDROP: GlassTextureBackdrop = { kind: "texture", id: ENVIRONMENT_ID };

/**
 * Which variant every group on the page takes. `regular` is the page this record describes;
 * `clear` is the post-panel comparison mode (`?glass=clear`, or the platter's switch), shown so
 * the two can be seen side by side. Clear is uncalibrated — no bed scene declares it — and it is
 * not the spatial register's recommendation for windows that carry text (SKILL.md §4, spatial
 * condition 8). The variants are never mixed: every group switches together.
 */
export type GlassMode = "regular" | "clear";

/**
 * The black the page paints into the environment under each host in clear mode, per scheme.
 * Started at the `Glass.clear` API example's black at 30 %, to be raised only as far as the
 * rendered text needed; every gated line and mark passed at 30 % in both schemes on both tiers,
 * so neither was raised (`DESIGN.md` part two, "Clear-variant comparison"). The page's number,
 * not a calibration: neither tier draws a scrim, and no bed scene has measured one.
 */
export const CLEAR_DIMMING: Readonly<Record<"light" | "dark", number>> = { light: 0.3, dark: 0.3 };

/** How far past a host's edge the clear mode's dimming fades to nothing, CSS px. */
export const CLEAR_DIMMING_FEATHER = 16;

/** What a group is told about its material. The regular page says nothing at all. */
export interface GroupMaterial {
  readonly variant?: "clear";
  readonly dimming?: DimmingPolicy;
}

/**
 * The material props for every group in a mode. Clear requires a dimming policy (core renders
 * a clear surface without one as regular); it names the scrim the page actually paints, in the
 * default policy's direction, since the policy itself paints nothing.
 */
export function groupMaterial(mode: GlassMode, scrim: number): GroupMaterial {
  return mode === "clear" ? { variant: "clear", dimming: { ...DEFAULT_CLEAR_DIMMING, scrim } } : {};
}

/**
 * A host's box, written as the inline offsets and size a fixed host needs. Nothing else is ever
 * written inline on a host: its background, border, shadow and transform are the runtime's.
 */
export function boxStyle(box: Box): CSSProperties {
  return {
    position: "fixed",
    left: box.x,
    top: box.y,
    width: box.width,
    height: box.height,
    boxSizing: "border-box",
  };
}
