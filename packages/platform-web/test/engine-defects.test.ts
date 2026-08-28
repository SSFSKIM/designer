/**
 * The engine-versioned advisory (parent Decision Log #39).
 *
 * Chromium 152 renders `backdrop-filter` as a complete no-op on an element with
 * `clip-path: path()` under an ancestor carrying `overflow` other than `visible`
 * together with a `border-radius`. All three ingredients are required and every
 * basic-shape clip-path is unaffected — the 12-cell × 2-build matrix is in
 * `spikes/s1-proxy-topology/chrome152-regression/REPORT.md`.
 *
 * vitrea's proxies are exactly that shape, so this is the product's construction
 * rather than a user's mistake. The default mount is immune — the plane root is
 * `position: fixed` under `body` — and a custom `container` mount is not. Nothing
 * in the page can see it happen: the filter is dropped with no console message,
 * and S1's Q5 already established that no readback path can observe
 * `backdrop-filter` output. So the runtime's only honest move is to say so.
 *
 * A fabricated chain in jsdom, which is what the existing audit's tests use: the
 * question is which ancestors the walk finds and what the advisory says about
 * them, and both are answerable without a renderer.
 */

import { afterEach, beforeEach, describe, expect, it } from "vitest";

import { createPlatformDiagnosticsChannel } from "../src/diagnostics";
import {
  CHROMIUM_152_PATH_CLIP_NO_OP,
  CHROMIUM_PATH_CLIP_DEFECT_MIN_VERSION,
  conformanceRowFor,
  CONFORMANCE_TABLE,
  CONSERVATIVE_ROW,
  defectsOnChain,
  describeEngineDefect,
  probeGroup,
  probePlatform,
  roundedClipOf,
  type PlatformProbeReport,
} from "../src/probe";
import { createLayoutReadMeter } from "../src/measure";
import { createGlassRoot, type GlassRoot } from "../src/root";
import type { MediaMatcher } from "../src/media-policy";

const CHROME_151 =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36";
const CHROME_152 =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/152.0.7977.64 Safari/537.36";
const SAFARI_26 =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/26.5 Safari/605.1.15";

const platformFor = (userAgent: string): PlatformProbeReport =>
  probePlatform({ meter: createLayoutReadMeter(), supports: () => true, userAgent });

/**
 * A proxy under a chain of ancestors, built from the outside in. Each entry is a
 * `style` attribute; the last one is the proxy's own parent.
 */
function chain(...styles: readonly string[]): Element {
  let parent: HTMLElement = document.body;
  for (const style of styles) {
    const element = document.createElement("div");
    element.setAttribute("style", style);
    parent.append(element);
    parent = element;
  }
  const proxy = document.createElement("div");
  proxy.setAttribute("style", "backdrop-filter: blur(8px)");
  parent.append(proxy);
  return proxy;
}

const hazardsFor = (userAgent: string, proxy: Element) =>
  probeGroup({ groupId: "g1", proxy, window }, platformFor(userAgent), createLayoutReadMeter())
    .engineDefects;

afterEach(() => {
  document.body.replaceChildren();
});

describe("the Chromium 152 clip-path defect, as a table row", () => {
  it("keeps every conformance answer the measured Chromium row already gave", () => {
    // The regression breaks one construction; it does not change what the
    // engine can do. Downgrading `rasterisesBackdropFilter` would demote every
    // Chromium 152 session, including the overwhelming majority that never
    // build the failing shape.
    const before = conformanceRowFor({ family: "chromium", version: 151 });
    const after = conformanceRowFor({ family: "chromium", version: 152 });

    expect(after.rasterisesBackdropFilter).toBe(before.rasterisesBackdropFilter);
    expect(after.edgeMode).toBe(before.edgeMode);
    expect(after.referenceFilterInBackdrop).toBe(before.referenceFilterInBackdrop);
    expect(after.maxProxyAreaDevicePx).toBe(before.maxProxyAreaDevicePx);
    expect(after.transform3dHazard).toBe(before.transform3dHazard);
    expect(after.backdropRootTriggers).toBe(before.backdropRootTriggers);
  });

  it("carries the defect from 152 forward and on no earlier version", () => {
    expect(conformanceRowFor({ family: "chromium", version: 151 }).defects).toEqual([]);
    expect(conformanceRowFor({ family: "chromium", version: 151.9 }).defects).toEqual([]);
    expect(conformanceRowFor({ family: "chromium", version: 152 }).defects).toEqual([
      CHROMIUM_152_PATH_CLIP_NO_OP,
    ]);
    expect(conformanceRowFor({ family: "chromium", version: 160 }).defects).toEqual([
      CHROMIUM_152_PATH_CLIP_NO_OP,
    ]);
    expect(CHROMIUM_PATH_CLIP_DEFECT_MIN_VERSION).toBe(152);
  });

  it("accuses no engine it did not measure", () => {
    // The opposite direction from the conformance fields, and deliberately so:
    // an unmeasured version claims no defect, because a defect is a claim that
    // something is broken.
    for (const row of [...CONFORMANCE_TABLE, CONSERVATIVE_ROW]) {
      if (row.family === "chromium" && row.minVersion >= 152) continue;
      expect(row.defects, `${row.family} ${row.minVersion}`).toEqual([]);
    }
  });

  it("makes every defect cite evidence and name a way out", () => {
    // The conformance table's own update-path rule, applied to the second axis:
    // a row cannot be added on a hunch, and an advisory that only says what is
    // wrong is half a diagnostic.
    for (const row of [...CONFORMANCE_TABLE, CONSERVATIVE_ROW]) {
      for (const defect of row.defects) {
        expect(defect.evidence.length).toBeGreaterThan(0);
        expect(defect.workarounds.length).toBeGreaterThan(0);
        expect(defect.report).not.toBe("");
      }
    }
  });
});

describe("reading a rounded, clipping ancestor off a computed style", () => {
  const lookup = (values: Record<string, string>) => (property: string) => values[property] ?? "";

  it("needs both ingredients, because the defect needs both", () => {
    expect(roundedClipOf(lookup({ overflow: "hidden", "border-radius": "6px" }))).toEqual({
      overflow: "hidden",
      borderRadius: "6px",
    });
    expect(roundedClipOf(lookup({ overflow: "hidden", "border-radius": "0px" }))).toBeUndefined();
    expect(roundedClipOf(lookup({ overflow: "visible", "border-radius": "6px" }))).toBeUndefined();
    expect(roundedClipOf(lookup({}))).toBeUndefined();
  });

  it("reads the shorthand and the longhands, because environments expand differently", () => {
    // A browser expands `overflow: hidden` into both axes and leaves the
    // shorthand readable too; jsdom reports the shorthand and leaves the
    // longhands at their initial values. One reader has to be right in both.
    expect(
      roundedClipOf(lookup({ "overflow-y": "auto", "border-top-left-radius": "4px" })),
    ).toEqual({ overflow: "auto", borderRadius: "4px" });
    expect(roundedClipOf(lookup({ overflow: "visible hidden", "border-radius": "2px" }))).toEqual({
      overflow: "visible hidden",
      borderRadius: "2px",
    });
  });

  it("counts every clipping value, not only hidden", () => {
    for (const overflow of ["hidden", "clip", "auto", "scroll"]) {
      expect(roundedClipOf(lookup({ overflow, "border-radius": "8px" }))).toBeDefined();
    }
  });

  it("counts a percentage radius, which is how a capsule is usually written", () => {
    expect(roundedClipOf(lookup({ overflow: "hidden", "border-radius": "50%" }))).toBeDefined();
    expect(
      roundedClipOf(lookup({ overflow: "hidden", "border-radius": "0px / 0px" })),
    ).toBeUndefined();
  });

  /*
   * The exact strings the three engines return, measured 2026-08-28 through the
   * e2e fixture page in Chromium, Firefox and WebKit (all three agreed). jsdom
   * cannot produce these — it expands no shorthand — so without them the reader
   * would only ever be tested against the one environment it does not ship in.
   */
  it.each([
    { authored: "overflow: hidden; border-radius: 6px", computed: { overflow: "hidden", "overflow-x": "hidden", "overflow-y": "hidden", "border-radius": "6px", "border-top-left-radius": "6px" }, clips: true },
    { authored: "overflow-y: auto; border-top-left-radius: 4px", computed: { overflow: "auto", "overflow-x": "auto", "overflow-y": "auto", "border-radius": "4px 0px 0px", "border-top-left-radius": "4px" }, clips: true },
    { authored: "overflow: clip; border-radius: 50%", computed: { overflow: "clip", "overflow-x": "clip", "overflow-y": "clip", "border-radius": "50%", "border-top-left-radius": "50%" }, clips: true },
    { authored: "overflow: visible hidden; border-radius: 2px 4px", computed: { overflow: "auto hidden", "overflow-x": "auto", "overflow-y": "hidden", "border-radius": "2px 4px", "border-top-left-radius": "2px" }, clips: true },
    { authored: "border-radius: 0", computed: { overflow: "visible", "overflow-x": "visible", "overflow-y": "visible", "border-radius": "0px", "border-top-left-radius": "0px" }, clips: false },
  ])("reads a real engine's computed values for `$authored`", ({ computed, clips }) => {
    expect(roundedClipOf(lookup(computed)) !== undefined).toBe(clips);
  });
});

describe("the advisory, on a fabricated proxy chain", () => {
  it("fires on Chromium 152 under a rounded, clipping ancestor", () => {
    const proxy = chain("overflow: hidden; border-radius: 6px", "padding: 8px");
    const [hazard] = hazardsFor(CHROME_152, proxy);

    expect(hazard?.defect.id).toBe(CHROMIUM_152_PATH_CLIP_NO_OP.id);
    expect(hazard?.ancestor.overflow).toBe("hidden");
    expect(hazard?.ancestor.borderRadius).toBe("6px");
  });

  it("says nothing on the same chain in 151 — the version is half the finding", () => {
    expect(hazardsFor(CHROME_151, chain("overflow: hidden; border-radius: 6px"))).toEqual([]);
  });

  it("says nothing in an engine with no defect on the books", () => {
    expect(hazardsFor(SAFARI_26, chain("overflow: hidden; border-radius: 6px"))).toEqual([]);
  });

  it("needs both ingredients on one ancestor, not one on each", () => {
    // Two ancestors, each carrying half the trigger. The measured defect needs
    // both on the same element, and a scan that unioned them would warn about a
    // page that renders correctly.
    expect(hazardsFor(CHROME_152, chain("overflow: hidden", "border-radius: 6px"))).toEqual([]);
    expect(hazardsFor(CHROME_152, chain("border-radius: 6px", "overflow: hidden"))).toEqual([]);
  });

  it("says nothing about a plain chain, which is what the default mount produces", () => {
    expect(hazardsFor(CHROME_152, chain("position: fixed; inset: 0"))).toEqual([]);
  });

  it("finds an ancestor further up the chain, not only the proxy's parent", () => {
    const proxy = chain("overflow: auto; border-radius: 12px", "padding: 4px", "margin: 2px");
    expect(hazardsFor(CHROME_152, proxy)).toHaveLength(1);
  });

  it("names the nearest offender when several qualify", () => {
    const proxy = chain("overflow: hidden; border-radius: 20px", "overflow: clip; border-radius: 3px");
    const [hazard] = hazardsFor(CHROME_152, proxy);
    expect(hazard?.ancestor.borderRadius).toBe("3px");
  });

  it("tells the author what broke, where, what to do, and where the proof is", () => {
    const proxy = chain("overflow: hidden; border-radius: 6px");
    const [hazard] = hazardsFor(CHROME_152, proxy);
    expect(hazard).toBeDefined();
    if (hazard === undefined) return;

    const message = describeEngineDefect("toolbar", hazard.defect, hazard.ancestor);
    expect(message).toContain('Group "toolbar"');
    expect(message).toContain("clip-path: path()");
    expect(message).toContain("overflow: hidden");
    expect(message).toContain("border-radius: 6px");
    expect(message).toContain("spikes/s1-proxy-topology/chrome152-regression/REPORT.md");
    // The workarounds, all of them, numbered — a diagnostic that only names the
    // fault leaves the author exactly where they were.
    for (const fix of hazard.defect.workarounds) expect(message).toContain(fix);
  });

  it("matches no defect against an empty chain", () => {
    expect(defectsOnChain([CHROMIUM_152_PATH_CLIP_NO_OP], [])).toEqual([]);
    expect(defectsOnChain([], [])).toEqual([]);
  });
});

/* The advisory as an app receives it: through the diagnostics channel, from a root. */
describe("the advisory reaching a root's diagnostics", () => {
  class StubResizeObserver {
    observe(): void {}
    unobserve(): void {}
    disconnect(): void {}
  }

  const matcher: MediaMatcher = () => ({
    matches: false,
    media: "(prefers-reduced-motion: reduce)",
    addEventListener: () => {},
    removeEventListener: () => {},
  });

  let roots: GlassRoot[] = [];
  const realUserAgent = navigator.userAgent;

  const pretendEngine = (userAgent: string): void => {
    Object.defineProperty(window.navigator, "userAgent", { value: userAgent, configurable: true });
  };

  beforeEach(() => {
    (globalThis as { ResizeObserver?: unknown }).ResizeObserver = StubResizeObserver;
  });

  afterEach(() => {
    for (const instance of roots) instance.destroy();
    roots = [];
    pretendEngine(realUserAgent);
  });

  /**
   * A root mounted into a rounded, clipping container — the shape the default
   * mount cannot produce and a custom `container` can. Returns the diagnostics
   * the root emitted.
   */
  function mountUnderRoundedOverflow(): {
    readonly root: GlassRoot;
    readonly reported: ReturnType<typeof createPlatformDiagnosticsChannel>["reported"];
  } {
    const channel = createPlatformDiagnosticsChannel();
    const wrapper = document.createElement("div");
    wrapper.setAttribute("style", "overflow: hidden; border-radius: 10px");
    document.body.append(wrapper);
    const container = document.createElement("div");
    wrapper.append(container);

    const instance = createGlassRoot({
      container,
      autoStart: false,
      matcher,
      diagnosticSink: ({ origin, diagnostic }) => {
        if (origin === "platform") channel.report(diagnostic);
      },
    });
    roots.push(instance);

    const host = document.createElement("button");
    instance.plane("base").hostLayer.append(host);
    instance.registerGroup({ id: "g1" });
    instance.registerHost({ host, groupId: "g1", plane: "base" });
    instance.runFrame(0);
    // Twice more, because the audit re-runs whenever the chain's styles change
    // and an advisory that repeated per audit would be worse than none.
    instance.revalidateProbe();
    instance.revalidateProbe();

    return { root: instance, reported: channel.reported };
  }

  it("reaches an app as one warning, and never demotes the group", () => {
    pretendEngine(CHROME_152);
    const { root: instance, reported } = mountUnderRoundedOverflow();

    const advisories = reported.filter((entry) => entry.code === "engine-known-defect");
    expect(advisories).toHaveLength(1);
    expect(advisories[0]?.severity).toBe("warning");
    expect(advisories[0]?.subjects).toEqual(["g1", CHROMIUM_152_PATH_CLIP_NO_OP.id]);
    expect(advisories[0]?.message).toContain(
      "spikes/s1-proxy-topology/chrome152-regression/REPORT.md",
    );

    // Advisory, not verdict. The engine drops the filter without saying so and
    // no readback path can see it, so demoting on a structural match would
    // trade a possibly-unfrosted GPU tier for a certainly-lower one, on a guess.
    expect(instance.probeReport("g1")?.verdict).toBe("pass");
    expect(instance.capabilities("g1")?.health).toBe("ok");
  });

  it("says nothing in the same page on the version before the regression", () => {
    pretendEngine(CHROME_151);
    const { reported } = mountUnderRoundedOverflow();
    expect(reported.filter((entry) => entry.code === "engine-known-defect")).toEqual([]);
  });
});
