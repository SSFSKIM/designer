/**
 * @vitrea/react — skeleton (C1).
 *
 * The second published package (X7). Thin by policy: it maps React lifecycle
 * and JSX onto @vitrea/platform-web registration, so a later Vue/Svelte/WC
 * adapter duplicates nothing. C8 lands the components.
 */

import type { GlassGroupState } from "@vitrea/core";
import { GLASS_PLANES, type GlassPlane } from "@vitrea/platform-web";
import type { ReactNode } from "react";

/** Accessibility overrides follow the media query unless the app overrules it. */
export type AccessibilityOverride = "system" | boolean;

export interface GlassRootProps {
  readonly children?: ReactNode | undefined;
  readonly reducedMotion?: AccessibilityOverride | undefined;
  readonly reducedTransparency?: AccessibilityOverride | undefined;
  readonly increasedContrast?: AccessibilityOverride | undefined;
}

/**
 * `prefers-reduced-transparency` is not Baseline, which is why the explicit
 * override is load-bearing rather than a courtesy (§Accessibility policy).
 */
export const GLASS_ROOT_ACCESSIBILITY_DEFAULTS: {
  readonly reducedMotion: AccessibilityOverride;
  readonly reducedTransparency: AccessibilityOverride;
  readonly increasedContrast: AccessibilityOverride;
} = {
  reducedMotion: "system",
  reducedTransparency: "system",
  increasedContrast: "system",
};

/** The planes a React tree can render into (X1), surfaced from platform-web. */
export const SUPPORTED_PLANES: readonly GlassPlane[] = GLASS_PLANES;

export type { GlassGroupState, GlassPlane };
