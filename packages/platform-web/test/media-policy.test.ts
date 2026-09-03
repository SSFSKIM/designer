import { describe, expect, it, vi } from "vitest";

import {
  ACCESSIBILITY_MEDIA_QUERIES,
  observeAccessibilityPreferences,
  observeDevicePixelRatio,
  browserMediaMatcher,
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
): {
  matcher: MediaMatcher;
  fire: (query: string, matches: boolean) => void;
  /** The queries with a live listener right now — what re-arming is visible as. */
  armed: () => string[];
} {
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
    armed: () =>
      [...listeners.entries()].filter(([, set]) => set.size > 0).map(([query]) => query),
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

/*
 * The device-pixel-ratio feed (W12 G3, claims §5.56). The CSS tier's body is a
 * device-pixel quantity, so a change of the ratio is a change of the material
 * this tier paints — and a `(resolution: <dpr>dppx)` query can fire only once,
 * because it names the ratio that has just stopped being current. Re-arming is
 * therefore the whole mechanism, and it is what these pin.
 */
describe("the device-pixel-ratio feed (W12 G3)", () => {
  it("arms a query on the current ratio", () => {
    const { matcher, armed } = fakeMatcher([]);
    const feed = observeDevicePixelRatio({ matcher, read: () => 2, onChange: () => {} });

    expect(feed.devicePixelRatio).toBe(2);
    expect(armed()).toEqual(["(resolution: 2dppx)"]);
    feed.stop();
  });

  it("re-arms on the new ratio and keeps hearing about further changes", () => {
    const onChange = vi.fn();
    let ratio = 1;
    const { matcher, armed, fire } = fakeMatcher([]);
    const feed = observeDevicePixelRatio({ matcher, read: () => ratio, onChange });

    ratio = 2;
    fire("(resolution: 1dppx)", false);
    expect(onChange).toHaveBeenNthCalledWith(1, 2);
    expect(feed.devicePixelRatio).toBe(2);
    expect(armed()).toEqual(["(resolution: 2dppx)"]);

    // The second move is the one a listener that did not re-arm would miss.
    ratio = 3;
    fire("(resolution: 2dppx)", false);
    expect(onChange).toHaveBeenNthCalledWith(2, 3);
    expect(feed.devicePixelRatio).toBe(3);
    expect(armed()).toEqual(["(resolution: 3dppx)"]);

    // And the query it left behind is dead, so a stale one cannot report again.
    fire("(resolution: 1dppx)", false);
    expect(onChange).toHaveBeenCalledTimes(2);
    feed.stop();
  });

  it("stops listening when it is stopped", () => {
    const onChange = vi.fn();
    const { matcher, armed, fire } = fakeMatcher([]);
    const feed = observeDevicePixelRatio({ matcher, read: () => 1, onChange });

    feed.stop();
    expect(armed()).toEqual([]);
    fire("(resolution: 1dppx)", false);
    expect(onChange).not.toHaveBeenCalled();
  });
});

describe("browserMediaMatcher", () => {
  it("registers its queries on the SUPPLIED window, not the ambient one", () => {
    // A root created for an iframe or a popup reads that window's ratio, so the
    // resolution query that wakes the dpr feed has to live there too; a query
    // on the ambient window never fires for a display change the supplied
    // window saw (review, W13 G1).
    const asked: string[] = [];
    const view = {
      matchMedia: (query: string): MediaQueryList => {
        asked.push(query);
        return {
          matches: false,
          media: query,
          addEventListener: () => {},
          removeEventListener: () => {},
        } as unknown as MediaQueryList;
      },
    };
    const feed = observeDevicePixelRatio({
      matcher: browserMediaMatcher(view),
      read: () => 2,
      onChange: () => {},
    });
    expect(asked).toEqual(["(resolution: 2dppx)"]);
    feed.stop();
  });
});

