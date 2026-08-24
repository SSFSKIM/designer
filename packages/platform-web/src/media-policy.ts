/**
 * The media-query policy feed (§Accessibility policy).
 *
 * core holds accessibility *policy* — what a preference means for the material
 * and for motion — and never touches a media query (X4). This module reads the
 * queries and hands the answers over as plain data, so the whole browser half of
 * the feature is four `matchMedia` calls and a change listener.
 *
 * `prefers-reduced-transparency` is not Baseline, which is why support detection
 * is part of the contract rather than a nicety: an engine that cannot parse the
 * query reports `media: "not all"` and `matches: false` forever, and a runtime
 * that read that as "the user does not want reduced transparency" would silently
 * lose the preference. core's resolver raises its own diagnostic when a root
 * leaves the flag on `"system"` on such a platform — this module's job is to
 * tell it the truth about what it could ask.
 */

import type { SystemAccessibilityPreferences } from "@vitrea/core";

/** The four preferences §Accessibility names, and the query that answers each. */
export const ACCESSIBILITY_MEDIA_QUERIES = {
  reducedMotion: "(prefers-reduced-motion: reduce)",
  increasedContrast: "(prefers-contrast: more)",
  forcedColors: "(forced-colors: active)",
  reducedTransparency: "(prefers-reduced-transparency: reduce)",
} as const;

export type AccessibilityQueryKey = keyof typeof ACCESSIBILITY_MEDIA_QUERIES;

/** The slice of `MediaQueryList` this module uses. Narrow so a test can supply one. */
export interface MediaQueryHandle {
  readonly matches: boolean;
  /** `"not all"` where the engine could not parse the query. */
  readonly media: string;
  addEventListener(type: "change", listener: (event: { matches: boolean }) => void): void;
  removeEventListener(type: "change", listener: (event: { matches: boolean }) => void): void;
}

export type MediaMatcher = (query: string) => MediaQueryHandle;

export interface AccessibilityFeedOptions {
  readonly matcher: MediaMatcher;
  readonly onChange: (preferences: SystemAccessibilityPreferences) => void;
}

export interface AccessibilityFeed {
  readonly preferences: SystemAccessibilityPreferences;
  stop(): void;
}

/** A query the engine did not parse can never match, whatever it later reports. */
const isSupported = (handle: MediaQueryHandle): boolean => handle.media !== "not all";

export function observeAccessibilityPreferences(
  options: AccessibilityFeedOptions,
): AccessibilityFeed {
  const { matcher, onChange } = options;

  const handles = {
    reducedMotion: matcher(ACCESSIBILITY_MEDIA_QUERIES.reducedMotion),
    increasedContrast: matcher(ACCESSIBILITY_MEDIA_QUERIES.increasedContrast),
    forcedColors: matcher(ACCESSIBILITY_MEDIA_QUERIES.forcedColors),
    reducedTransparency: matcher(ACCESSIBILITY_MEDIA_QUERIES.reducedTransparency),
  } satisfies Record<AccessibilityQueryKey, MediaQueryHandle>;

  const reducedTransparencySupported = isSupported(handles.reducedTransparency);

  const read = (): SystemAccessibilityPreferences => ({
    reducedMotion: handles.reducedMotion.matches,
    increasedContrast: handles.increasedContrast.matches,
    forcedColors: handles.forcedColors.matches,
    reducedTransparency: reducedTransparencySupported && handles.reducedTransparency.matches,
    reducedTransparencySupported,
  });

  let preferences = read();

  const listener = (): void => {
    preferences = read();
    onChange(preferences);
  };

  for (const handle of Object.values(handles)) handle.addEventListener("change", listener);

  return {
    get preferences() {
      return preferences;
    },
    stop() {
      for (const handle of Object.values(handles)) handle.removeEventListener("change", listener);
    },
  };
}

/** The live feed. `window.matchMedia`, bound so the pure form above stays testable. */
export function browserMediaMatcher(): MediaMatcher {
  return (query) => window.matchMedia(query);
}
