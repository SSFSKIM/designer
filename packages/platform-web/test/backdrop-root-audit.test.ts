import { describe, expect, it } from "vitest";

import {
  BACKDROP_ROOT_TRIGGERS,
  backdropRootTriggers,
  type StyleLookup,
} from "../src/probe/backdrop-root";

/**
 * S1's measured ground truth, verbatim from
 * docs/doperpowers/spikes/2026-08-24-s1-proxy-topology-findings.md §"What *is*
 * detectable". Each fixture is one candidate style placed on the GlassRoot — an
 * ancestor of the proxy but not of the backdrop content — and `reRoots` is what
 * the pixels said, not what the property looks like it should do.
 *
 * The spike's prototype audit scored 11/13 on this table with the *intuitive*
 * property list: no false negatives, and two false positives (`contain: paint`
 * and `isolation: isolate`, neither of which re-roots). Pinning the list to
 * Filter Effects 2's normative trigger set and nothing more is what closes
 * those two, so this table is the spec for the shipped list.
 */
const S1_GROUND_TRUTH: readonly { readonly name: string; readonly style: Record<string, string>; readonly reRoots: boolean }[] = [
  { name: "none", style: {}, reRoots: false },
  { name: "opacity: 0.99", style: { opacity: "0.99" }, reRoots: true },
  { name: "filter: none", style: { filter: "none" }, reRoots: false },
  { name: "filter: blur(0px)", style: { filter: "blur(0px)" }, reRoots: true },
  { name: "filter: grayscale(0)", style: { filter: "grayscale(0)" }, reRoots: true },
  {
    name: "mask-image: linear-gradient(#000,#000)",
    style: { "mask-image": "linear-gradient(rgb(0, 0, 0), rgb(0, 0, 0))" },
    reRoots: true,
  },
  { name: "clip-path: inset(0)", style: { "clip-path": "inset(0px)" }, reRoots: true },
  { name: "mix-blend-mode: multiply", style: { "mix-blend-mode": "multiply" }, reRoots: true },
  { name: "will-change: opacity", style: { "will-change": "opacity" }, reRoots: true },
  { name: "contain: paint", style: { contain: "paint" }, reRoots: false },
  { name: "isolation: isolate", style: { isolation: "isolate" }, reRoots: false },
  { name: "will-change: transform", style: { "will-change": "transform" }, reRoots: false },
  {
    name: "transform: translate3d(0,0,0)",
    style: { transform: "matrix3d(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1)" },
    reRoots: false,
  },
];

/** A computed style is a property lookup; the audit needs nothing more of it. */
const lookupFor = (style: Record<string, string>): StyleLookup => {
  const initial: Record<string, string> = {
    filter: "none",
    "backdrop-filter": "none",
    "-webkit-backdrop-filter": "none",
    opacity: "1",
    "mask-image": "none",
    "-webkit-mask-image": "none",
    "mask-border-source": "none",
    "clip-path": "none",
    "mix-blend-mode": "normal",
    "will-change": "auto",
    isolation: "auto",
    contain: "none",
    transform: "none",
  };
  return (property) => style[property] ?? initial[property] ?? "";
};

describe("the backdrop-root trigger list (S1 Q5, Filter Effects 2 §3)", () => {
  it.each(S1_GROUND_TRUTH)("scores $name as measured", ({ style, reRoots }) => {
    expect(backdropRootTriggers(lookupFor(style)).length > 0).toBe(reRoots);
  });

  it("scores every S1 fixture — no false negatives and, unlike the prototype, no false positives", () => {
    const wrong = S1_GROUND_TRUTH.filter(
      ({ style, reRoots }) => backdropRootTriggers(lookupFor(style)).length > 0 !== reRoots,
    );
    expect(wrong).toEqual([]);
  });

  it("names the property and value it flagged, because the fix is one CSS line in the host app", () => {
    const [trigger] = backdropRootTriggers(lookupFor({ opacity: "0.5" }));
    expect(trigger).toMatchObject({ property: "opacity", value: "0.5" });
  });

  it("carries only Filter Effects 2's normative triggers", () => {
    const properties = BACKDROP_ROOT_TRIGGERS.map((trigger) => trigger.property);
    expect(properties).toEqual([
      "filter",
      "backdrop-filter",
      "-webkit-backdrop-filter",
      "opacity",
      "mask-image",
      "-webkit-mask-image",
      "mask-border-source",
      "clip-path",
      "mix-blend-mode",
      "will-change",
    ]);
    // The two the prototype over-triggered on, plus the two the spike measured harmless.
    expect(properties).not.toContain("contain");
    expect(properties).not.toContain("isolation");
    expect(properties).not.toContain("content-visibility");
    expect(properties).not.toContain("transform");
  });

  it("flags will-change only when it names a trigger of its own", () => {
    for (const value of ["opacity", "filter", "mask", "clip-path", "mix-blend-mode", "backdrop-filter"]) {
      expect(backdropRootTriggers(lookupFor({ "will-change": value }))).toHaveLength(1);
    }
    for (const value of ["auto", "transform", "scroll-position", "contents", "contain"]) {
      expect(backdropRootTriggers(lookupFor({ "will-change": value }))).toEqual([]);
    }
  });

  it("treats a visually inert filter as a re-rooting one, which is the trap", () => {
    // Real application CSS emits these as animation start states all the time.
    for (const value of ["blur(0px)", "grayscale(0)", "opacity(1)"]) {
      expect(backdropRootTriggers(lookupFor({ filter: value }))).toHaveLength(1);
    }
  });

  it("reads opacity numerically, so 1 passes and 0.999 does not", () => {
    expect(backdropRootTriggers(lookupFor({ opacity: "1" }))).toEqual([]);
    expect(backdropRootTriggers(lookupFor({ opacity: "0.999" }))).toHaveLength(1);
  });
});
