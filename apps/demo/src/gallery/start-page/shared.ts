/**
 * The size family and the one backdrop every group reads (`DESIGN.md`, family and groups).
 */

import type { GlassTextureBackdrop } from "@vitreajs/vitrea-react";
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
