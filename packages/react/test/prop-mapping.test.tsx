/**
 * Props → core's scene model. The bindings own the vocabulary; core owns the
 * meaning, and these assertions are the boundary between the two.
 */

import { APPLE_CONTINUOUS_SMOOTHING_SEED, APPLE_BEST_FIGMA_SMOOTHING } from "@vitrea/geometry";
import { describe, expect, it } from "vitest";
import { act, useEffect, useLayoutEffect, useState, type ReactNode } from "react";

import {
  APPLE_LIKE_SMOOTHING,
  assertSharedCornerReference,
  cornerReferenceFor,
  GlassGroup,
  GlassSurface,
  radiiFor,
  smoothingFor,
} from "../src/index";
import type { GlassHostHandle } from "@vitreajs/vitrea-web";

import { renderGlass } from "./harness";

describe("X8's public sugar", () => {
  it("resolves `profile` exactly as geometry's own table does", () => {
    expect(smoothingFor("circular")).toBe(0);
    expect(smoothingFor("continuous")).toBe(APPLE_CONTINUOUS_SMOOTHING_SEED);
    expect(smoothingFor(undefined)).toBe(APPLE_CONTINUOUS_SMOOTHING_SEED);
    expect(smoothingFor(0.66)).toBe(0.66);

    expect(cornerReferenceFor("continuous")).toBe("apple-continuous");
    expect(cornerReferenceFor(undefined)).toBe("apple-continuous");
    expect(cornerReferenceFor("circular")).toBe("figma-smoothing");
    expect(cornerReferenceFor(0.66)).toBe("figma-smoothing");
  });

  it("keeps radii uniform, with the Vec4 shape preserved (X8 rider 3)", () => {
    expect(radiiFor(14)).toEqual([14, 14, 14, 14]);
    expect(radiiFor(-4)).toEqual([0, 0, 0, 0]);
  });

  it("names the interpolable stand-in for Apple's curve", () => {
    expect(APPLE_LIKE_SMOOTHING).toBe(APPLE_BEST_FIGMA_SMOOTHING.radiusFixed.smoothing);
    expect(cornerReferenceFor(APPLE_LIKE_SMOOTHING)).toBe("figma-smoothing");
  });

  it("refuses a morph pair whose ends are fit against different curves", () => {
    expect(() =>
      assertSharedCornerReference(
        { label: "closed", profile: "continuous" },
        { label: "open", profile: "circular" },
      ),
    ).toThrow(/must share a corner reference/);

    expect(
      assertSharedCornerReference(
        { label: "closed", profile: 0.6 },
        { label: "open", profile: "circular" },
      ),
    ).toBe("figma-smoothing");
  });
});

describe("GlassSurface → GlassNodeDescriptor", () => {
  it("maps shape, variant and z-slot onto the node core registered", () => {
    const harness = renderGlass(
      <GlassGroup id="g" dimming={{ scrim: 0.3, direction: "darken" }}>
        <GlassSurface
          nodeId="one"
          plane="overlay"
          order={3}
          variant="clear"
          profile="circular"
          radius={20}
          thickness={11}
        />
      </GlassGroup>,
    );

    const descriptor = harness.root().scene.glassNode("one")?.descriptor;
    expect(descriptor?.groupId).toBe("g");
    expect(descriptor?.shapeFamily).toBe("fixed-rounded-rect");
    expect(descriptor?.shape.radii).toEqual([20, 20, 20, 20]);
    expect(descriptor?.shape.smoothing).toBe(0);
    expect(descriptor?.shape.thickness).toBe(11);
    expect(descriptor?.variant).toBe("clear");
    expect(descriptor?.zSlot).toEqual({ plane: "overlay", order: 3 });
  });

  /*
   * The corner reference reaches the scene (Decision Log #23(c)).
   *
   * It did not in v1: this binding computed it, used it only to refuse a
   * cross-reference morph, and threw it away — so `profile="circular"` and
   * `profile={0.6}`, which both sit on the Figma smoothing axis, were drawn
   * against the Apple-direct fit like everything else. `smoothing` alone cannot
   * say which curve it is a point on, because the two are separate fits rather
   * than two points on one axis (#22(a)).
   */
  it("sends the corner reference the profile resolves to, not only its smoothing", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface nodeId="figma" profile={0.6} />
        <GlassSurface nodeId="circular" profile="circular" />
        <GlassSurface nodeId="continuous" profile="continuous" />
        <GlassSurface nodeId="unsaid" />
      </GlassGroup>,
    );

    const referenceOf = (nodeId: string) =>
      harness.root().scene.glassNode(nodeId)?.descriptor.reference;

    expect(referenceOf("figma")).toBe("figma-smoothing");
    expect(referenceOf("circular")).toBe("figma-smoothing");
    expect(referenceOf("continuous")).toBe("apple-continuous");
    // The default is the renderer's to apply, and the binding's `profile`
    // default is `"continuous"` — so this one is stated rather than omitted.
    expect(referenceOf("unsaid")).toBe("apple-continuous");
  });

  it("re-sends it when the profile changes rather than only at registration", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface nodeId="one" profile="continuous" />
      </GlassGroup>,
    );
    expect(harness.root().scene.glassNode("one")?.descriptor.reference).toBe("apple-continuous");

    harness.rerender(
      <GlassGroup id="g">
        <GlassSurface nodeId="one" profile="circular" />
      </GlassGroup>,
    );

    expect(harness.root().scene.glassNode("one")?.descriptor.reference).toBe("figma-smoothing");
  });

  it("declares a capsule as one, and never declares position or size", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface nodeId="pill" capsule />
      </GlassGroup>,
    );

    const descriptor = harness.root().scene.glassNode("pill")?.descriptor;
    expect(descriptor?.shapeFamily).toBe("capsule");
    // Position and size are measured, never authored — the read phase owns them.
    expect(descriptor?.shape.center).toEqual([0, 0]);
    expect(descriptor?.shape.size).toEqual([0, 0]);
  });

  it("patches the node when a shape prop changes, keeping the same registration", () => {
    function Resizable(): ReactNode {
      const [radius, setRadius] = useState(10);
      return (
        <GlassGroup id="g">
          <button type="button" onClick={() => setRadius(24)}>
            grow
          </button>
          <GlassSurface nodeId="one" radius={radius} />
        </GlassGroup>
      );
    }

    const harness = renderGlass(<Resizable />);
    const before = harness.root().scene.glassNode("one");
    expect(before?.descriptor.shape.radii).toEqual([10, 10, 10, 10]);

    act(() => {
      harness.result.getByText("grow").click();
    });

    const after = harness.root().scene.glassNode("one");
    expect(after?.descriptor.shape.radii).toEqual([24, 24, 24, 24]);
    // Same node id, so nothing was released and re-registered under the covers.
    expect(after?.descriptor.groupId).toBe("g");
  });
});

describe("the tint prop", () => {
  it("parses the author's colour into the seed core carries, alpha as strength", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface nodeId="one" tint="rgba(255, 149, 0, 0.5)" />
      </GlassGroup>,
    );

    const tint = harness.root().scene.glassNode("one")?.descriptor.tint;
    expect(tint?.color[0]).toBeCloseTo(1, 6);
    expect(tint?.color[1]).toBeCloseTo(149 / 255, 6);
    expect(tint?.strength).toBeCloseTo(0.5, 6);
  });

  it("leaves an untinted surface with no tint declared at all", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface nodeId="one" />
      </GlassGroup>,
    );
    expect(harness.root().scene.glassNode("one")?.descriptor.tint).toBeUndefined();
  });

  it("patches the seed in place when the prop changes, without re-registering", () => {
    function Recolourable(): ReactNode {
      const [tint, setTint] = useState<string | null>("rgb(255, 0, 0)");
      return (
        <GlassGroup id="g">
          <button type="button" onClick={() => setTint(null)}>
            clear
          </button>
          <GlassSurface nodeId="one" tint={tint} />
        </GlassGroup>
      );
    }

    const harness = renderGlass(<Recolourable />);
    expect(harness.root().scene.glassNode("one")?.descriptor.tint?.color).toEqual([1, 0, 0]);

    act(() => {
      harness.result.getByText("clear").click();
    });

    // `null` is the author clearing the tint, which is a value rather than an
    // absence — the same distinction `Glass.tint(nil)` makes.
    expect(harness.root().scene.glassNode("one")?.descriptor.tint).toBeNull();
    expect(harness.root().scene.glassNode("one")?.descriptor.groupId).toBe("g");
  });
});

/**
 * The group seed, which core has carried since W3 (`MaterialProfile.tint`,
 * resolved per member in `scene.ts`) and the CHANGELOG's 0.2.0 entry has
 * documented since — "Set it on a `GlassGroup` to tint its members" — while
 * `GlassGroupProps` had no such prop and the policy object the binding built
 * was variant and dimming only.
 *
 * Asserted on the *resolved* material off the frame's render input rather than
 * on the descriptor, because inheritance is core's resolution step: a member's
 * own descriptor stays empty and is meant to.
 */
describe("a group's tint", () => {
  const resolvedTintOf = (harness: ReturnType<typeof renderGlass>, nodeId: string) =>
    harness
      .root()
      .renderInput()
      ?.planes.flatMap((plane) => plane.nodes)
      .find((node) => node.nodeId === nodeId)?.material.tint;

  it("reaches members that declare none, and not one that clears it", () => {
    const harness = renderGlass(
      <GlassGroup id="g" tint="rgba(255, 149, 0, 0.5)">
        <GlassSurface nodeId="inherits" />
        <GlassSurface nodeId="clears" tint={null} />
      </GlassGroup>,
    );
    harness.frame();

    expect(harness.root().scene.glassGroup("g")?.descriptor.material?.tint?.color[1]).toBeCloseTo(
      149 / 255,
      6,
    );

    const inherited = resolvedTintOf(harness, "inherits");
    expect(inherited?.color[0]).toBeCloseTo(1, 6);
    expect(inherited?.color[1]).toBeCloseTo(149 / 255, 6);
    expect(inherited?.strength).toBeCloseTo(0.5, 6);

    // `tint={null}` is `Glass.tint(nil)`: the member opts out of what the group
    // gave it, rather than inheriting it anyway.
    expect(resolvedTintOf(harness, "clears")).toBeUndefined();
  });

  it("is patched in place when the prop changes", () => {
    function Recolourable(): ReactNode {
      const [tint, setTint] = useState<string | null>("rgb(255, 0, 0)");
      return (
        <GlassGroup id="g" tint={tint}>
          <button type="button" onClick={() => setTint("rgb(0, 0, 255)")}>
            recolour
          </button>
          <GlassSurface nodeId="one" />
        </GlassGroup>
      );
    }

    const harness = renderGlass(<Recolourable />);
    harness.frame();
    expect(resolvedTintOf(harness, "one")?.color).toEqual([1, 0, 0]);

    act(() => {
      harness.result.getByText("recolour").click();
    });
    harness.frame();
    expect(resolvedTintOf(harness, "one")?.color).toEqual([0, 0, 1]);
  });
});

/**
 * `present` — the authored presence W27d gives every surface (claims §5.132 §1).
 *
 * The phase it is forwarded in is a property of the runtime and not of React
 * trivia, because the material and the content it belongs to have to reach the
 * runtime on one commit. `GlassMorph`'s materialize crossfade writes its content
 * in the layout phase, and under Reduced Motion that write IS the transition, so
 * a presence that arrives from the passive phase lands after the browser painted
 * that commit — one frame of content over material that is not there.
 *
 * Layout effects run child-first and in tree order, so a probe rendered after the
 * surface can say which phase the forward happened in without knowing anything
 * about how it is implemented: before the probe's own layout effect, or after it.
 */
describe("a surface's presence", () => {
  it("reaches the runtime in the layout phase, ahead of any passive effect", () => {
    const order: string[] = [];

    function Probe(): ReactNode {
      useLayoutEffect(() => {
        order.push("layout-phase-ended");
      });
      useEffect(() => {
        order.push("passive-phase-ended");
      });
      return null;
    }

    function Fixture(): ReactNode {
      const [present, setPresent] = useState(true);
      const [handle, setHandle] = useState<GlassHostHandle | null>(null);

      // Wrapped once, on the commit the handle arrives, so the recorded calls are
      // the surface's own patches and nothing the test provoked.
      useLayoutEffect(() => {
        if (handle === null) return;
        const update = handle.update.bind(handle);
        handle.update = (patch) => {
          if (patch.present !== undefined) order.push(`present:${String(patch.present)}`);
          update(patch);
        };
      }, [handle]);

      return (
        <GlassGroup id="g">
          <button type="button" onClick={() => setPresent(false)}>
            park
          </button>
          <GlassSurface nodeId="one" present={present} onHost={setHandle} />
          <Probe />
        </GlassGroup>
      );
    }

    const harness = renderGlass(<Fixture />);
    harness.frame();

    order.length = 0;
    act(() => {
      harness.result.getByText("park").click();
    });

    const forwarded = order.indexOf("present:false");
    expect(forwarded, "the surface never forwarded the prop").toBeGreaterThanOrEqual(0);
    expect(
      forwarded,
      "presence reached the runtime after the layout phase had ended",
    ).toBeLessThan(order.indexOf("layout-phase-ended"));
  });
});
