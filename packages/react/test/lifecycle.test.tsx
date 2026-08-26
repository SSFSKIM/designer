/**
 * Registration lifecycles — the half of this package that is not JSX.
 *
 * Every assertion here is about the scene, not the DOM: what the bindings are
 * for is turning a React tree into core's three registries and back out again
 * without leaking a node, a group, or a source.
 */

import { describe, expect, it } from "vitest";
import { act } from "react";
import type { ReactNode } from "react";
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

  it("registers a named dom source, so a dom backdrop is not one undocumented id", () => {
    // `backdrop={{ kind: "dom", id }}` is a second arbitrary-DOM region beside the
    // root's shared one. Forwarding the id without registering it made every value
    // but the root's own private default an `Unknown backdrop source` throw.
    const harness = renderGlass(<GlassGroup id="g" backdrop={{ kind: "dom", id: "hero" }} />);

    expect(harness.root().scene.backdropSource("hero")?.descriptor.kind).toBe("dom");
    expect(harness.root().scene.glassGroup("g")?.descriptor.backdropSourceId).toBe("hero");

    harness.result.unmount();
  });

  it("borrows a source it did not register rather than owning it", () => {
    // `id: "vitrea.dom"` names the root's own shared dom source, and an app may
    // register a texture itself before mounting the group that samples it.
    // Registering over one is a duplicate-id throw; removing one on unmount would
    // take the root's default backdrop out from under every other group.
    function Toggle(): ReactNode {
      const [shown, setShown] = useState(true);
      return (
        <>
          <button type="button" onClick={() => setShown(false)}>
            hide
          </button>
          {shown ? <GlassGroup id="a" backdrop={{ kind: "dom", id: "vitrea.dom" }} /> : null}
          <GlassGroup id="b" />
        </>
      );
    }

    const harness = renderGlass(<Toggle />);
    expect(harness.root().scene.glassGroup("a")?.descriptor.backdropSourceId).toBe("vitrea.dom");

    act(() => {
      harness.result.getByText("hide").click();
    });
    expect(harness.root().scene.backdropSource("vitrea.dom")).toBeDefined();
    expect(harness.root().capabilities("b")?.configuredSource).toBe("dom");
  });

  it("swaps its source by patching, with a surface still holding a lease", () => {
    // A source change used to re-run registration, and the child's lease makes the
    // removal half of that a no-op — so core saw `registerGroup` on an id it still
    // holds and threw `Duplicate glass group id`.
    function Swapping(): ReactNode {
      const [id, setId] = useState("a");
      return (
        <GlassGroup id="g" backdrop={{ kind: "texture", id }}>
          <button type="button" onClick={() => setId("b")}>
            flip
          </button>
          <GlassSurface nodeId="one" />
        </GlassGroup>
      );
    }

    const harness = renderGlass(<Swapping />);
    expect(harness.root().scene.glassGroup("g")?.descriptor.backdropSourceId).toBe("a");

    expect(() =>
      act(() => {
        harness.result.getByText("flip").click();
      }),
    ).not.toThrow();

    expect(harness.root().scene.glassGroup("g")?.descriptor.backdropSourceId).toBe("b");
    expect(harness.root().scene.backdropSource("b")).toBeDefined();
    // The old source goes with the last group that referenced it, and not before:
    // core refuses to remove one any group still points at.
    expect(harness.root().scene.backdropSource("a")).toBeUndefined();
    expect(harness.root().scene.glassNode("one")).toBeDefined();
  });

  it("patches its descriptor on a re-render rather than re-registering it", () => {
    // Inline object props are how anyone writes this, and a fresh literal every
    // render must not reach core's registry: registering an existing id is a
    // structural throw, and the group's surfaces hold leases that make the
    // removal half of a re-register a no-op — so the throw is what an app would
    // actually see.
    function Rerendering(): ReactNode {
      const [tone, setTone] = useState<"light" | "dark">("light");
      return (
        <GlassGroup id="g" hint={{ tone, luminance: 0.2 }} samplingPadding={24}>
          <button type="button" onClick={() => setTone("dark")}>
            flip
          </button>
          <GlassSurface nodeId="one" />
        </GlassGroup>
      );
    }

    const harness = renderGlass(<Rerendering />);
    expect(harness.root().scene.glassGroup("g")?.descriptor.backdrop?.tone).toBe("light");

    expect(() =>
      act(() => {
        harness.result.getByText("flip").click();
      }),
    ).not.toThrow();

    expect(harness.root().scene.glassGroup("g")?.descriptor.backdrop?.tone).toBe("dark");
    expect(harness.root().scene.glassNode("one")).toBeDefined();
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

  it("survives a re-render with inline object props, patching instead of re-registering", () => {
    function Rerendering(): ReactNode {
      const [mode, setMode] = useState<"fixed" | "author-hint">("fixed");
      return (
        <GlassGroup id="g">
          <button type="button" onClick={() => setMode("author-hint")}>
            flip
          </button>
          <GlassSurface nodeId="one" foreground={{ mode }} />
        </GlassGroup>
      );
    }

    const harness = renderGlass(<Rerendering />);
    expect(harness.root().scene.glassNode("one")?.descriptor.foreground?.mode).toBe("fixed");

    expect(() =>
      act(() => {
        harness.result.getByText("flip").click();
      }),
    ).not.toThrow();

    expect(harness.root().scene.glassNode("one")?.descriptor.foreground?.mode).toBe("author-hint");
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
    // Through the portal mount node, which is `display: contents` and exists so a
    // plane change can move the subtree instead of rebuilding it.
    expect(outer.closest('[data-vitrea-layer="semantic-host"]')).toBe(
      harness.root().plane("base").hostLayer,
    );
    expect(outer.contains(inner)).toBe(true);
  });
});
