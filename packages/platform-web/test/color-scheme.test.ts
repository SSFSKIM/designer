/**
 * The colour scheme, resolved (W21 G3).
 *
 * What is asserted here is precedence and re-derivation, not pixels: which patch
 * a scheme selects, that an app's own `materialProfile` still wins over it leaf
 * by leaf, that `"auto"` follows `prefers-color-scheme` and re-derives when it
 * flips, and that the default is light so an existing host's material does not
 * move because it upgraded. jsdom cannot filter, so what the material then LOOKS
 * like is the Playwright suite's (`e2e/shared/color-scheme.spec.ts`).
 *
 * The observable is the frame's own render input — the honesty core, which is
 * what the frame resolved and what a renderer is handed, rather than a
 * declaration one tier happens to write.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { afterEach, describe, expect, it } from "vitest";

import {
  colorSchemeMaterialProfile,
  mergeMaterialProfiles,
  observeColorScheme,
  resolveColorScheme,
  COLOR_SCHEME_MEDIA_QUERY,
} from "../src/color-scheme";
import { darkMaterialProfile } from "../src/dark-profile";
import { createGlassRoot, type GlassRoot, type GlassRootOptions } from "../src/root";
import type { MediaMatcher, MediaQueryHandle } from "../src/media-policy";

/** jsdom has no ResizeObserver, and `GeometrySync` builds one unconditionally. */
class StubResizeObserver {
  observe(): void {}
  unobserve(): void {}
  disconnect(): void {}
}

interface FakeQuery {
  matches: boolean;
  readonly listeners: Set<(event: { matches: boolean }) => void>;
}

/**
 * A matcher whose answers a test can change, with working change events — the
 * shape the platform's own feed sees. Every query starts unmatched, which is
 * every preference off and the light scheme.
 */
function fakeMatcher(): {
  readonly matcher: MediaMatcher;
  set(media: string, matches: boolean): void;
} {
  const queries = new Map<string, FakeQuery>();
  const query = (media: string): FakeQuery => {
    const held = queries.get(media) ?? { matches: false, listeners: new Set() };
    queries.set(media, held);
    return held;
  };

  const matcher: MediaMatcher = (media) => {
    const held = query(media);
    const handle: MediaQueryHandle = {
      get matches() {
        return held.matches;
      },
      media,
      addEventListener: (_type, listener) => held.listeners.add(listener),
      removeEventListener: (_type, listener) => held.listeners.delete(listener),
    };
    return handle;
  };

  return {
    matcher,
    set(media, matches) {
      const held = query(media);
      held.matches = matches;
      for (const listener of [...held.listeners]) listener({ matches });
    },
  };
}

/**
 * The resolved material one host is drawing, off the frame's own render input.
 *
 * The tint's alpha is the leaf the dark patch moves furthest — 0.97 against the
 * light default's 0.46 — so it is the one read.
 */
const tintAlphaOf = (root: GlassRoot): number => {
  const node = root.renderInput()?.planes.flatMap((plane) => plane.nodes)[0];
  if (node === undefined) throw new Error("the frame resolved no node to read a material off");
  return node.optics.tintAlpha;
};

let roots: GlassRoot[] = [];
let containers: HTMLElement[] = [];

interface Fixture {
  readonly root: GlassRoot;
  frame(): void;
  /** The tint alpha this root's one host resolved on the last frame. */
  tintAlpha(): number;
}

/** One root with one host in it, framed once so a material has been resolved. */
function rootWithHost(options: GlassRootOptions): Fixture {
  const container = document.createElement("div");
  document.body.append(container);
  containers.push(container);
  const created = createGlassRoot({
    container,
    autoStart: false,
    diagnosticSink: () => {},
    ...options,
  });
  roots.push(created);

  const host = document.createElement("button");
  created.plane("base").hostLayer.append(host);
  created.registerGroup({ id: "g1" });
  created.registerHost({ host, groupId: "g1", plane: "base" });

  const frame = (): void => {
    created.runFrame(0);
  };
  frame();
  return { root: created, frame, tintAlpha: () => tintAlphaOf(created) };
}

const originalResizeObserver = globalThis.ResizeObserver;
globalThis.ResizeObserver = StubResizeObserver as unknown as typeof ResizeObserver;

afterEach(() => {
  for (const created of roots) created.destroy();
  for (const container of containers) container.remove();
  roots = [];
  containers = [];
  globalThis.ResizeObserver = originalResizeObserver;
  globalThis.ResizeObserver = StubResizeObserver as unknown as typeof ResizeObserver;
});

describe("the shipped dark patch", () => {
  it("is the calibration document's own, read without a build (X7)", () => {
    /*
     * One source, checked against the SOURCE module. The calibration package
     * carries the same comparison against the published bundle
     * (`test/dark-profile-export.test.ts`), and this is the half that needs no
     * build: after a wave re-records the profile and forgets to regenerate
     * `src/dark-profile.ts`, a stale `dist/` would let that test pass while this
     * one fails. Reading the JSON here is a test-time read of a sibling package's
     * evidence, never a runtime dependency — the whole point of generating the
     * module is that the published bundle carries no such edge.
     */
    const document = JSON.parse(
      readFileSync(
        resolve(
          import.meta.dirname,
          "..",
          "..",
          "calibration",
          "profiles",
          "apple-macos-26.5-1x-dark-standard.json",
        ),
        "utf8",
      ),
    ) as { readonly patch: unknown };
    expect(
      darkMaterialProfile,
      "run `pnpm --filter @vitreajs/vitrea-web run profile:dark` and commit the result",
    ).toEqual(document.patch);
  });
});

describe("the scheme's base patch", () => {
  it("is the dark document's patch for dark, and nothing at all for light", () => {
    expect(colorSchemeMaterialProfile("dark")).toBe(darkMaterialProfile);
    // Not an empty object: light IS the renderer's defaults, and an empty patch
    // would be a second name for the absence of one.
    expect(colorSchemeMaterialProfile("light")).toBeUndefined();
  });

  it("folds the setting against the system's answer", () => {
    expect(resolveColorScheme("light", true)).toBe("light");
    expect(resolveColorScheme("dark", false)).toBe("dark");
    expect(resolveColorScheme("auto", true)).toBe("dark");
    expect(resolveColorScheme("auto", false)).toBe("light");
  });
});

describe("composing two patches", () => {
  it("lets the app's patch win leaf by leaf without dropping the scheme's siblings", () => {
    const merged = mergeMaterialProfiles(darkMaterialProfile, {
      optics: { regular: { tintAlpha: 0.5 } },
    });
    expect(merged?.optics?.regular?.tintAlpha).toBe(0.5);
    // The scheme's tint, named beside the alpha the app replaced, survives.
    expect(merged?.optics?.regular?.tint).toEqual([0.05, 0.05, 0.05]);
    expect(merged?.outerShadow?.liftAmplitude).toBe(0.0051);
    // And the scheme's own patch was not mutated.
    expect(darkMaterialProfile.optics?.regular?.tintAlpha).toBe(0.97);
  });

  it("passes either side through when the other is absent", () => {
    expect(mergeMaterialProfiles(undefined, darkMaterialProfile)).toBe(darkMaterialProfile);
    expect(mergeMaterialProfiles(darkMaterialProfile, undefined)).toBe(darkMaterialProfile);
    expect(mergeMaterialProfiles(undefined, undefined)).toBeUndefined();
  });
});

describe("the media feed", () => {
  it("reports the query's current answer and every change to it", () => {
    const { matcher, set } = fakeMatcher();
    const seen: boolean[] = [];
    const feed = observeColorScheme({ matcher, onChange: (prefersDark) => seen.push(prefersDark) });

    expect(feed.prefersDark).toBe(false);
    set(COLOR_SCHEME_MEDIA_QUERY, true);
    expect(feed.prefersDark).toBe(true);
    // A change event that does not change the answer is not a change.
    set(COLOR_SCHEME_MEDIA_QUERY, true);
    expect(seen).toEqual([true]);

    feed.stop();
    set(COLOR_SCHEME_MEDIA_QUERY, false);
    expect(seen).toEqual([true]);
  });
});

describe("a root's resolved scheme", () => {
  /*
   * The material is read as a comparison rather than as a number, on purpose.
   * What a scheme means is "this root draws the material a root handed that patch
   * draws", and the alpha the render input carries has already crossed the CSS
   * tier's mapping — so pinning its digits here would be re-recording a
   * calibration constant inside a test about precedence.
   */
  const alphaFor = (matcher: MediaMatcher, options: GlassRootOptions = {}): number =>
    rootWithHost({ matcher, ...options }).tintAlpha();

  it("is light by default, whatever the operating system says", () => {
    const { matcher, set } = fakeMatcher();
    set(COLOR_SCHEME_MEDIA_QUERY, true);
    const fixture = rootWithHost({ matcher });
    expect(fixture.root.colorScheme).toBe("light");
    expect(fixture.tintAlpha()).toBe(alphaFor(matcher));
  });

  it("draws the dark document's material under dark", () => {
    const { matcher } = fakeMatcher();
    const dark = rootWithHost({ matcher, colorScheme: "dark" });
    expect(dark.root.colorScheme).toBe("dark");
    expect(dark.tintAlpha()).toBe(alphaFor(matcher, { materialProfile: darkMaterialProfile }));
    expect(dark.tintAlpha()).not.toBe(alphaFor(matcher));
  });

  it("keeps the app's own materialProfile winning over the scheme's base", () => {
    const { matcher } = fakeMatcher();
    const patch = { optics: { regular: { tintAlpha: 0.3 } } };
    const tuned = rootWithHost({ matcher, colorScheme: "dark", materialProfile: patch });

    const composed = mergeMaterialProfiles(darkMaterialProfile, patch);
    if (composed === undefined) throw new Error("two patches composed to nothing");
    expect(tuned.tintAlpha()).toBe(alphaFor(matcher, { materialProfile: composed }));
    // The scheme is still the base under it: the leaf the app did not name is
    // the dark document's tint, not the renderer's default one.
    const tintOf = (fixture: Fixture): unknown =>
      fixture.root.renderInput()?.planes.flatMap((plane) => plane.nodes)[0]?.optics.tint;
    expect(tintOf(tuned)).toEqual(tintOf(rootWithHost({ matcher, colorScheme: "dark" })));
    expect(tintOf(tuned)).not.toEqual(tintOf(rootWithHost({ matcher })));
  });

  it("follows prefers-color-scheme under auto, and re-derives when it flips", () => {
    const { matcher, set } = fakeMatcher();
    const auto = rootWithHost({ matcher, colorScheme: "auto" });
    const asLight = alphaFor(matcher);
    const asDark = alphaFor(matcher, { materialProfile: darkMaterialProfile });

    expect(auto.root.colorScheme).toBe("light");
    expect(auto.tintAlpha()).toBe(asLight);

    set(COLOR_SCHEME_MEDIA_QUERY, true);
    expect(auto.root.colorScheme).toBe("dark");
    auto.frame();
    expect(auto.tintAlpha()).toBe(asDark);

    // And back: the light scheme is the renderer's defaults, so returning to it
    // has to restore them rather than leave the dark patch on.
    set(COLOR_SCHEME_MEDIA_QUERY, false);
    expect(auto.root.colorScheme).toBe("light");
    auto.frame();
    expect(auto.tintAlpha()).toBe(asLight);
  });

  it("ignores the system's answer while the setting is not auto", () => {
    const { matcher, set } = fakeMatcher();
    const fixed = rootWithHost({ matcher, colorScheme: "light" });
    const asLight = alphaFor(matcher);

    set(COLOR_SCHEME_MEDIA_QUERY, true);
    fixed.frame();
    expect(fixed.root.colorScheme).toBe("light");
    expect(fixed.tintAlpha()).toBe(asLight);
  });

  it("takes a scheme change after construction, on the live root", () => {
    const { matcher } = fakeMatcher();
    const switched = rootWithHost({ matcher });
    const asLight = alphaFor(matcher);
    const asDark = alphaFor(matcher, { materialProfile: darkMaterialProfile });

    switched.root.setColorScheme("dark");
    switched.frame();
    expect(switched.root.colorScheme).toBe("dark");
    expect(switched.tintAlpha()).toBe(asDark);

    switched.root.setColorScheme("light");
    switched.frame();
    expect(switched.tintAlpha()).toBe(asLight);
  });

  it("keeps the scheme when the app replaces its material profile", () => {
    const { matcher } = fakeMatcher();
    const held = rootWithHost({ matcher, colorScheme: "dark" });
    const asDark = alphaFor(matcher, { materialProfile: darkMaterialProfile });

    // A patch naming one leaf is a tuning of the scheme's material, not a
    // replacement of it: the scheme's own constants have to survive.
    held.root.setMaterialProfile({ sizeSpanMin: 24 });
    held.frame();
    expect(held.root.colorScheme).toBe("dark");
    expect(held.tintAlpha()).toBe(asDark);
  });
});
