import { describe, expect, it, vi } from "vitest";

import {
  ACCESSIBILITY_MEDIA_QUERIES,
  observeAccessibilityPreferences,
  type MediaMatcher,
} from "../src/media-policy";

/**
 * A fake `matchMedia`. `unsupported` names the queries this pretend engine does
 * not parse, which it reports the way real engines do: `media` comes back as
 * `"not all"` and `matches` is permanently false. That is the only channel
 * `prefers-reduced-transparency` support detection has.
 */
function fakeMatcher(
  active: readonly string[],
  unsupported: readonly string[] = [],
): { matcher: MediaMatcher; fire: (query: string, matches: boolean) => void } {
  const listeners = new Map<string, Set<(event: { matches: boolean }) => void>>();
  const states = new Map<string, boolean>();

  const matcher: MediaMatcher = (query) => {
    const supported = !unsupported.includes(query);
    states.set(query, supported && active.includes(query));
    return {
      get matches() {
        return states.get(query) ?? false;
      },
      media: supported ? query : "not all",
      addEventListener: (_type, listener) => {
        const set = listeners.get(query) ?? new Set();
        set.add(listener);
        listeners.set(query, set);
      },
      removeEventListener: (_type, listener) => {
        listeners.get(query)?.delete(listener);
      },
    };
  };

  return {
    matcher,
    fire: (query, matches) => {
      states.set(query, matches);
      for (const listener of listeners.get(query) ?? []) listener({ matches });
    },
  };
}

describe("the media-query policy feed (§Accessibility policy)", () => {
  it("queries exactly the four preferences the spec names", () => {
    expect(ACCESSIBILITY_MEDIA_QUERIES).toEqual({
      reducedMotion: "(prefers-reduced-motion: reduce)",
      increasedContrast: "(prefers-contrast: more)",
      forcedColors: "(forced-colors: active)",
      reducedTransparency: "(prefers-reduced-transparency: reduce)",
    });
  });

  it("reports nothing detected on a plain engine", () => {
    const { matcher } = fakeMatcher([]);
    const feed = observeAccessibilityPreferences({ matcher, onChange: () => {} });

    expect(feed.preferences).toEqual({
      reducedMotion: false,
      increasedContrast: false,
      forcedColors: false,
      reducedTransparency: false,
      reducedTransparencySupported: true,
    });
    feed.stop();
  });

  it("maps each active query onto its preference", () => {
    const { matcher } = fakeMatcher(Object.values(ACCESSIBILITY_MEDIA_QUERIES));
    const feed = observeAccessibilityPreferences({ matcher, onChange: () => {} });

    expect(feed.preferences).toMatchObject({
      reducedMotion: true,
      increasedContrast: true,
      forcedColors: true,
      reducedTransparency: true,
      reducedTransparencySupported: true,
    });
    feed.stop();
  });

  it("says so when the engine cannot answer prefers-reduced-transparency", () => {
    // It is not Baseline, which is exactly why the GlassRoot override is
    // load-bearing rather than a courtesy. Absence of evidence is reported as
    // absence of evidence, and core turns that into its own diagnostic.
    const { matcher } = fakeMatcher([], [ACCESSIBILITY_MEDIA_QUERIES.reducedTransparency]);
    const feed = observeAccessibilityPreferences({ matcher, onChange: () => {} });

    expect(feed.preferences.reducedTransparencySupported).toBe(false);
    expect(feed.preferences.reducedTransparency).toBe(false);
    feed.stop();
  });

  it("pushes a change through as data, once per change", () => {
    const onChange = vi.fn();
    const { matcher, fire } = fakeMatcher([]);
    const feed = observeAccessibilityPreferences({ matcher, onChange });

    fire(ACCESSIBILITY_MEDIA_QUERIES.reducedMotion, true);

    expect(onChange).toHaveBeenCalledTimes(1);
    expect(onChange.mock.calls[0]?.[0]).toMatchObject({ reducedMotion: true });
    expect(feed.preferences.reducedMotion).toBe(true);
    feed.stop();
  });

  it("stops listening when it is stopped", () => {
    const onChange = vi.fn();
    const { matcher, fire } = fakeMatcher([]);
    const feed = observeAccessibilityPreferences({ matcher, onChange });

    feed.stop();
    fire(ACCESSIBILITY_MEDIA_QUERIES.forcedColors, true);

    expect(onChange).not.toHaveBeenCalled();
  });
});
