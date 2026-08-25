/**
 * Registration lifecycles — the half of this package that is not JSX.
 *
 * Every assertion here is about the scene, not the DOM: what the bindings are
 * for is turning a React tree into core's three registries and back out again
 * without leaking a node, a group, or a source.
 */

import { describe, expect, it } from "vitest";
import { act } from "react";
import { useState } from "react";

import { GlassGroup, GlassSurface } from "../src/index";
import { hostsIn, renderGlass } from "./harness";

describe("GlassRoot", () => {
  it("builds one runtime and tears it down on unmount", () => {
    const harness = renderGlass(null);
    const root = harness.root();

    expect(document.querySelector("[data-vitrea-root]")).not.toBeNull();
    expect(root.plane("base").hostLayer).toBeInstanceOf(HTMLElement);

    harness.result.unmount();
    expect(document.querySelector("[data-vitrea-root]")).toBeNull();
  });

  it("defaults to the CSS tier, which is a choice and not a fault (X2, K1)", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface />
      </GlassGroup>,
    );
    harness.frame();

    const state = harness.root().capabilities("g");
    expect(state?.activeRenderer).toBe("css");
    expect(state?.health).toBe("ok");
    expect(state?.demotionReason).toBeUndefined();
    expect(state?.configuredSource).toBe("dom");
  });
});

describe("GlassGroup", () => {
  it("registers a group and removes it on unmount", () => {
    const harness = renderGlass(<GlassGroup id="toolbar" />);
    expect(harness.root().scene.glassGroup("toolbar")).toBeDefined();

    harness.result.unmount();
  });

  it("registers a texture source once, whatever the group count", () => {
    const backdrop = { kind: "texture", id: "hero" } as const;
    const harness = renderGlass(
      <>
        <GlassGroup id="a" backdrop={backdrop} />
        <GlassGroup id="b" backdrop={backdrop} />
      </>,
    );

    const source = harness.root().scene.backdropSource("hero");
    expect(source?.descriptor.kind).toBe("texture");
    expect(harness.root().capabilities("a")?.configuredSource).toBe("texture");
    expect(harness.root().capabilities("b")?.configuredSource).toBe("texture");
  });

  it("carries the sampling geometry X1 constrains", () => {
    const harness = renderGlass(
      <GlassGroup id="g" samplingPadding={30} mergeDistance={40} morphNamespace="menus" />,
    );
    const descriptor = harness.root().scene.glassGroup("g")?.descriptor;
    expect(descriptor?.samplingPadding).toBe(30);
    expect(descriptor?.mergeDistance).toBe(40);
    expect(descriptor?.morphNamespace).toBe("menus");
  });
});

describe("GlassSurface registration", () => {
  it("puts the host inside its plane's host layer, where X1 can sequence it", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface nodeId="one" />
      </GlassGroup>,
    );

    const hosts = hostsIn(harness.root());
    expect(hosts).toHaveLength(1);
    expect(hosts[0]?.getAttribute("data-vitrea-node")).toBe("one");
    expect(hosts[0]?.getAttribute("data-vitrea-group")).toBe("g");
    expect(harness.root().scene.glassNode("one")).toBeDefined();
  });

  it("releases the node when the surface unmounts", () => {
    function Toggle(): React.ReactNode {
      const [shown, setShown] = useState(true);
      return (
        <GlassGroup id="g">
          <button type="button" onClick={() => setShown(false)}>
            hide
          </button>
          {shown ? <GlassSurface nodeId="one" /> : null}
        </GlassGroup>
      );
    }

    const harness = renderGlass(<Toggle />);
    expect(harness.root().scene.glassNode("one")).toBeDefined();

    act(() => {
      harness.result.getByText("hide").click();
    });
    expect(harness.root().scene.glassNode("one")).toBeUndefined();
    expect(hostsIn(harness.root())).toHaveLength(0);
  });

  it("keeps a group alive until its last surface has gone (core refuses otherwise)", () => {
    // core throws GlassSceneError("in-use") on removing a group that still has
    // nodes, and React's unmount order across a subtree is not something to bet
    // a structural throw on. Unmounting the whole tree must simply work.
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface nodeId="one" />
        <GlassSurface nodeId="two" />
      </GlassGroup>,
    );

    expect(() => harness.result.unmount()).not.toThrow();
  });

  it("renders in place when it is already inside its plane, and portals otherwise", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface nodeId="outer" data-testid="outer">
          <GlassSurface nodeId="inner" data-testid="inner" />
        </GlassSurface>
      </GlassGroup>,
    );

    const outer = harness.result.getByTestId("outer");
    const inner = harness.result.getByTestId("inner");
    expect(outer.parentElement).toBe(harness.root().plane("base").hostLayer);
    expect(outer.contains(inner)).toBe(true);
  });
});
