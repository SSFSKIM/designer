/**
 * Parent acceptance #6, at the binding level.
 *
 * The bindings read no media query. What is asserted here is the passthrough:
 * the platform's answers reach core's policy without any wiring, a `GlassRoot`
 * prop overrules one, and `forced-colors` is not overridable at all — which is a
 * property of core's type, so the test that matters is the runtime one: an app
 * cannot switch it off even by asking.
 */

import { describe, expect, it } from "vitest";
import { act } from "react";
import type { ReactNode } from "react";

import { GlassGroup, GlassSurface, useGlassAccessibility, useGlassMotionProfile } from "../src/index";
import type { ResolvedAccessibilityPolicy } from "vitrea";
import { renderGlass } from "./harness";
import { setMediaQuery } from "./setup";

const QUERIES = {
  reducedMotion: "(prefers-reduced-motion: reduce)",
  increasedContrast: "(prefers-contrast: more)",
  forcedColors: "(forced-colors: active)",
  reducedTransparency: "(prefers-reduced-transparency: reduce)",
} as const;

interface ProbeProps {
  readonly onRead: (policy: ResolvedAccessibilityPolicy | undefined, reducedMotionApplied: boolean) => void;
}

function Probe(props: ProbeProps): ReactNode {
  props.onRead(useGlassAccessibility(), useGlassMotionProfile().reducedMotionApplied);
  return null;
}

describe("media-query passthrough", () => {
  it("carries every preference into the resolved policy with no wiring", () => {
    setMediaQuery(QUERIES.reducedMotion, true);
    setMediaQuery(QUERIES.increasedContrast, true);

    let policy: ResolvedAccessibilityPolicy | undefined;
    renderGlass(<Probe onRead={(next) => (policy = next)} />);

    expect(policy?.reducedMotion).toBe(true);
    expect(policy?.increasedContrast).toBe(true);
    expect(policy?.motion.overshoot).toBe("none");
    expect(policy?.motion.deformation).toBe("none");
    // "keeps direct-manipulation positional continuity" — an invariant, not a knob.
    expect(policy?.motion.positionalContinuity).toBe(true);
    expect(policy?.material.border).toBe("strong");
    expect(policy?.material.foreground).toBe("near-monochrome");
  });

  it("follows a preference that changes after mount", () => {
    let policy: ResolvedAccessibilityPolicy | undefined;
    const harness = renderGlass(<Probe onRead={(next) => (policy = next)} />);
    expect(policy?.reducedMotion).toBe(false);

    act(() => setMediaQuery(QUERIES.reducedMotion, true));
    harness.tick(16);
    expect(policy?.reducedMotion).toBe(true);
  });

  it("applies motion's Reduced Motion transform to the profile in force", () => {
    setMediaQuery(QUERIES.reducedMotion, true);
    let applied = false;
    renderGlass(<Probe onRead={(_policy, next) => (applied = next)} />);
    expect(applied).toBe(true);
  });
});

describe("GlassRoot overrides", () => {
  it("overrules the media query in both directions", () => {
    setMediaQuery(QUERIES.reducedMotion, true);
    let policy: ResolvedAccessibilityPolicy | undefined;

    renderGlass(<Probe onRead={(next) => (policy = next)} />, { reducedMotion: false });
    expect(policy?.reducedMotion).toBe(false);
    expect(policy?.motion.overshoot).toBe("elastic");
  });

  it("carries `reducedTransparency`, which the query cannot always answer", () => {
    let policy: ResolvedAccessibilityPolicy | undefined;
    renderGlass(<Probe onRead={(next) => (policy = next)} />, { reducedTransparency: true });

    expect(policy?.reducedTransparency).toBe(true);
    expect(policy?.material.frost).toBe("increased");
    expect(policy?.material.refraction).toBe("reduced");
    expect(policy?.material.occlusion).toBe("increased");
  });
});

describe("forced-colors", () => {
  it("renders system colors and no glass", () => {
    setMediaQuery(QUERIES.forcedColors, true);

    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface nodeId="one" data-testid="surface" />
      </GlassGroup>,
    );
    harness.frame();

    const host = harness.result.getByTestId("surface");
    // jsdom lower-cases system colour keywords; the identity is what matters.
    expect(host.style.getPropertyValue("background").toLowerCase()).toBe("canvas");
    expect(host.style.getPropertyValue("color").toLowerCase()).toBe("canvastext");
    expect(host.style.getPropertyValue("border-color").toLowerCase()).toBe("canvastext");
    expect(host.style.getPropertyValue("backdrop-filter")).toBe("none");
    expect(host.style.getPropertyValue("box-shadow")).toBe("none");
  });

  it("cannot be switched off by an app, whatever it asks for", () => {
    setMediaQuery(QUERIES.forcedColors, true);
    let policy: ResolvedAccessibilityPolicy | undefined;

    // The prop does not exist in the type; passing it anyway must change nothing.
    renderGlass(<Probe onRead={(next) => (policy = next)} />, {
      ...({ forcedColors: false } as Record<string, unknown>),
    });

    expect(policy?.forcedColors).toBe(true);
    expect(policy?.material.glass).toBe("none");
  });
});
