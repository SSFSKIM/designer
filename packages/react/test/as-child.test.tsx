/**
 * The `asChild` seam. platform-web never creates, wraps or replaces the app's
 * element, and this is the layer that has to keep that true in JSX.
 */

import { describe, expect, it, vi } from "vitest";
import { createRef, useRef } from "react";
import type { ReactNode } from "react";

import { composeRefs, mergeSlotProps, renderAsChild } from "../src/as-child";
import { GlassGroup, GlassSurface } from "../src/index";
import { renderGlass } from "./harness";

describe("mergeSlotProps", () => {
  it("chains event handlers, slot first", () => {
    const order: string[] = [];
    const merged = mergeSlotProps(
      { onClick: () => order.push("slot") },
      { onClick: () => order.push("child") },
    );
    (merged.onClick as () => void)();
    expect(order).toEqual(["slot", "child"]);
  });

  it("composes style and className rather than replacing them", () => {
    const merged = mergeSlotProps(
      { style: { color: "red", margin: 0 }, className: "glass" },
      { style: { color: "blue" }, className: "mine" },
    );
    expect(merged.style).toEqual({ color: "blue", margin: 0 });
    expect(merged.className).toBe("glass mine");
  });

  it("lets the child win every other prop", () => {
    const merged = mergeSlotProps({ type: "button", id: "slot" }, { id: "child" });
    expect(merged).toMatchObject({ type: "button", id: "child" });
  });
});

describe("composeRefs", () => {
  it("fills an object ref and calls a function ref with the same node", () => {
    const object = createRef<HTMLDivElement>();
    const seen: (HTMLDivElement | null)[] = [];
    const element = document.createElement("div");

    composeRefs<HTMLDivElement>(object, (value) => {
      seen.push(value);
    })(element);

    expect(object.current).toBe(element);
    expect(seen).toEqual([element]);
  });
});

describe("renderAsChild", () => {
  it("refuses anything that is not exactly one element", () => {
    expect(() => renderAsChild("text", {})).toThrow(/exactly one React element/);
  });
});

describe("GlassSurface asChild", () => {
  it("registers the app's own element — no wrapper, no replaced content", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface asChild nodeId="one">
          <button type="button" id="mine" className="app">
            Share
          </button>
        </GlassSurface>
      </GlassGroup>,
    );

    const host = harness.root().plane("base").hostLayer.querySelector("[data-vitrea-node]");
    expect(host?.tagName).toBe("BUTTON");
    expect(host?.id).toBe("mine");
    expect(host?.className).toBe("app");
    expect(host?.textContent).toBe("Share");
    expect(host?.getAttribute("data-vitrea-node")).toBe("one");
  });

  it("keeps the child's own ref working alongside vitrea's", () => {
    let captured: HTMLButtonElement | null = null;

    function Probe(): ReactNode {
      const ref = useRef<HTMLButtonElement>(null);
      captured = ref.current;
      return (
        <GlassGroup id="g">
          <GlassSurface asChild>
            <button
              type="button"
              ref={(node) => {
                ref.current = node;
                captured = node;
              }}
            >
              Share
            </button>
          </GlassSurface>
        </GlassGroup>
      );
    }

    const harness = renderGlass(<Probe />);
    expect(captured).toBe(
      harness.root().plane("base").hostLayer.querySelector("[data-vitrea-node]"),
    );
  });

  it("chains the app's handler with the surface's own interaction wiring", () => {
    const onClick = vi.fn();
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassSurface asChild interactive>
          <button type="button" onClick={onClick} onPointerDown={onClick}>
            Share
          </button>
        </GlassSurface>
      </GlassGroup>,
    );

    const button = harness.result.getByRole("button");
    button.click();
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});
