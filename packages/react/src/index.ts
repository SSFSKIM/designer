/**
 * `@vitrea/react` — the declarative surface (child C8 of
 * `docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md`).
 *
 * The second published package (X7), and thin by policy: it maps React lifecycle
 * and JSX onto `@vitrea/platform-web` registration and owns no material, no
 * geometry and no motion of its own. Everything it decides, it decides about
 * React — when to register, where to portal, which element to clone. Everything
 * else is a call into a package that already owns the answer, so a later Vue,
 * Svelte or Web-Components adapter duplicates nothing but this file's worth of
 * lifecycle.
 *
 * ## The shape of an app
 *
 * ```tsx
 * <GlassRoot>
 *   <YourOrdinaryPage />
 *   <GlassToolbar aria-label="Actions" style={{ position: "absolute", bottom: 32 }}>
 *     <GlassButton onClick={…}>Share</GlassButton>
 *     <GlassIconButton aria-label="More">…</GlassIconButton>
 *   </GlassToolbar>
 * </GlassRoot>
 * ```
 *
 * The page is ordinary DOM and stays ordinary DOM. Glass surfaces portal
 * themselves into their plane's host layer, because X1's sandwich orders a plane
 * by DOM order and a host outside it cannot be sequenced at all.
 *
 * ## Zero runtime dependencies beyond React
 *
 * `@vitrea/core` is this package's one declared dependency; `platform-web`,
 * `geometry` and `motion` are internal and bundled at publish (X7). React is a
 * peer. There is no state library, no animation library and no a11y library
 * here — v1's menu is composed over an external accessible primitive **the app
 * chooses**, which is why nothing in this file mentions one (Decision Log #13).
 */

export {
  GlassRoot,
  useGlassAccessibility,
  useGlassCapabilities,
  useGlassDiagnostics,
  useGlassMotionProfile,
  useGlassTicker,
  type GlassRootProps,
} from "./root";
export { GlassGroup, type GlassBackdrop, type GlassDomBackdrop, type GlassGroupProps, type GlassTextureBackdrop } from "./group";
export { GlassSurface, type GlassSurfaceOwnProps, type GlassSurfaceProps } from "./surface";
export { GlassMorph, type GlassMorphPlacement, type GlassMorphProps, type GlassMorphState } from "./morph";

export { GlassButton, GlassIconButton, type GlassButtonProps, type GlassIconButtonProps } from "./controls/button";
export {
  GlassToolbar,
  TOOLBAR_ITEM_ATTRIBUTE,
  useToolbarItem,
  type GlassToolbarProps,
  type ToolbarItemProps,
  type ToolbarOrientation,
} from "./controls/toolbar";
export {
  GlassSegmentedControl,
  type GlassSegment,
  type GlassSegmentedControlProps,
} from "./controls/segmented-control";

export { useGlassRoot, type GlassRootHandle, type RecordedDiagnostic } from "./context";
export { GLASS_CHANNEL_PROPERTIES } from "./interaction";
export { PlanePortal, PLANE_MOUNT_ATTRIBUTE, type PlanePortalProps } from "./plane-portal";
export {
  APPLE_LIKE_SMOOTHING,
  assertSharedCornerReference,
  capsuleRadius,
  cornerReferenceFor,
  radiiFor,
  smoothingFor,
  type GlassCornerProfile,
} from "./shape";
export { composeRefs, mergeSlotProps, renderAsChild, type SlotProps } from "./as-child";
export { createGlassTicker, type GlassTicker, type GlassTickListener } from "./ticker";

/**
 * Accessibility overrides follow the media query unless the app overrules it.
 * The vocabulary is core's — `forcedColors` is deliberately absent from it,
 * because an operating-system mandate is not an app's to switch off.
 */
export type {
  AccessibilityOverride,
  AccessibilityOverrides,
  BackdropHint,
  DimmingPolicy,
  ForegroundAdaptation,
  GlassGroupState,
  GlassPlane,
  MaterialVariant,
  ResolvedAccessibilityPolicy,
} from "@vitrea/core";

/**
 * The one-liner that satisfies the clear variant's dimming requirement. Core
 * refuses a clear surface without a policy rather than inventing a scrim, and
 * names this constant when it does — so the bindings surface it too.
 */
export { DEFAULT_CLEAR_DIMMING } from "@vitrea/core";

import { GLASS_PLANES, type GlassPlane } from "@vitrea/core";
import { DEFAULT_MOTION_PROFILE, type MotionProfile } from "@vitrea/motion";

/**
 * `prefers-reduced-transparency` is not Baseline, which is why the explicit
 * override is load-bearing rather than a courtesy (§Accessibility policy).
 */
export const GLASS_ROOT_ACCESSIBILITY_DEFAULTS: {
  readonly reducedMotion: "system";
  readonly reducedTransparency: "system";
  readonly increasedContrast: "system";
} = {
  reducedMotion: "system",
  reducedTransparency: "system",
  increasedContrast: "system",
};

/** The planes a React tree can render into (X1). */
export const SUPPORTED_PLANES: readonly GlassPlane[] = GLASS_PLANES;

/** Motion constants in force when a root declares no profile. Advisory until C7. */
export const DEFAULT_GLASS_MOTION_PROFILE: MotionProfile = DEFAULT_MOTION_PROFILE;
export type { MotionProfile };
