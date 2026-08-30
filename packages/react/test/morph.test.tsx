/**
 * `GlassMorph`'s two invariants that do not need a browser to state.
 *
 * jsdom lays nothing out, so the boxes are stubbed: the closed footprint and the
 * platter's natural size are the two measurements the component takes, and both
 * are read through `getBoundingClientRect` and `offsetWidth`/`offsetHeight`.
 * Stubbing exactly those makes the geometry deterministic and leaves everything
 * being asserted — when the platter realigns, and when it calls itself settled —
 * the component's own logic.
 *
 * The platter's *own* box is modelled rather than stubbed flat (`platterBox`),
 * because one assertion here is about what the runtime measures on the platter
 * before it has placed itself, and a flat stub would answer that question by
 * fiat. The model is two CSS rules, written out.
 */

import { describe, expect, it, vi, afterEach, beforeEach } from "vitest";
import { act, useState } from "react";
import type { ReactNode } from "react";

import { GlassGroup, GlassMorph } from "../src/index";
import { renderGlass } from "./harness";

/** The closed footprint, in viewport coordinates. Mutable: a reflow moves it. */
let anchor = { x: 10, y: 10, width: 100, height: 40 };
/** The platter's natural size, equal to the footprint so the box never changes. */
const natural = { width: 100, height: 40 };

const ZERO = { x: 0, y: 0, width: 0, height: 0 };

/** Wide enough that a viewport-wide box is unmistakable next to a 100px one. */
const VIEWPORT_WIDTH = 1024;

const offsets = new Map<"offsetWidth" | "offsetHeight", PropertyDescriptor | undefined>();

const declared = (value: string): number | null =>
  value === "" ? null : Number.parseFloat(value);

/**
 * The platter's box, modelled from its own declarations.
 *
 * jsdom lays nothing out, so the two CSS rules that decide this box are written
 * out instead — and they are the whole subject of the pre-pin assertion below,
 * so modelling them is not a convenience:
 *
 * - **Out of flow** (`position: fixed`): the box is exactly the offsets and
 *   sizes written on the element. An omitted size is shrink-to-fit, which for
 *   `width: max-content` content is that content's natural size.
 * - **In flow**: a block box inside the plane's host layer, and a host layer is
 *   `position: absolute; inset: 0` over the viewport — so it begins at that
 *   layer's origin and takes its full width, whatever the content wanted.
 */
function platterBox(element: HTMLElement): typeof ZERO {
  const style = element.style;
  if (style.position === "fixed") {
    return {
      x: declared(style.left) ?? 0,
      y: declared(style.top) ?? 0,
      width: declared(style.width) ?? natural.width,
      height: declared(style.height) ?? natural.height,
    };
  }
  return { x: 0, y: 0, width: VIEWPORT_WIDTH, height: natural.height };
}

beforeEach(() => {
  anchor = { x: 10, y: 10, width: 100, height: 40 };

  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockImplementation(function (
    this: HTMLElement,
  ) {
    const box = this.hasAttribute("data-vitrea-morph-anchor")
      ? anchor
      : this.hasAttribute("data-vitrea-morph")
        ? platterBox(this)
        : ZERO;
    return {
      ...box,
      top: box.y,
      left: box.x,
      right: box.x + box.width,
      bottom: box.y + box.height,
      toJSON: () => box,
    } as DOMRect;
  });

  for (const [name, size] of [
    ["offsetWidth", natural.width],
    ["offsetHeight", natural.height],
  ] as const) {
    offsets.set(name, Object.getOwnPropertyDescriptor(HTMLElement.prototype, name));
    Object.defineProperty(HTMLElement.prototype, name, {
      configurable: true,
      get(this: HTMLElement) {
        return this.hasAttribute("data-vitrea-morph-content") ? size : 0;
      },
    });
  }
});

afterEach(() => {
  vi.restoreAllMocks();
  for (const [name, descriptor] of offsets) {
    if (descriptor === undefined) delete (HTMLElement.prototype as unknown as Record<string, unknown>)[name];
    else Object.defineProperty(HTMLElement.prototype, name, descriptor);
  }
  offsets.clear();
});

const platterOf = (): HTMLElement => {
  const platter = document.querySelector<HTMLElement>("[data-vitrea-morph]");
  if (platter === null) throw new Error("The platter was not rendered.");
  return platter;
};

describe("GlassMorph geometry", () => {
  /*
   * Decision Log #28(d). Registration and measurement are one commit apart from
   * *placement*, and what the runtime measures in between is the assertion.
   *
   * `GlassSurface` registers in its layout effect and `registerHost` ends in
   * `geometry.track`, which marks the node dirty there and then — so the very
   * next read phase publishes whatever box the platter has at that moment, and
   * that box goes straight into `checkSamePlaneOverlap` and
   * `checkGroupProxyOverlap`. Placement cannot happen in the same commit: the
   * closed end is measured on a frame, deliberately, because a layout effect
   * inside a portalled subtree runs before the ancestor that attaches it.
   *
   * So the window is real and cannot be closed by ordering. What can be made
   * true is that nothing meaningful is published inside it — every box the
   * scene ever sees is a box the platter actually occupies.
   */
  it("publishes no box it does not occupy, from the first frame to the last", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassMorph open={false} nodeId="platter">
          {() => <span>Menu</span>}
        </GlassMorph>
      </GlassGroup>,
    );

    const positions: string[] = [];
    const published: (typeof ZERO | undefined)[] = [];
    // Past the pin (frame 2) with room to spare, so the settled box is sampled
    // alongside the transient ones and the assertion is not vacuously about an
    // unmeasured node.
    for (let i = 0; i < 6; i += 1) {
      positions.push(platterOf().style.position);
      harness.run(1);
      published.push(harness.root().scene.glassNode("platter")?.bounds);
    }

    // jsdom runs no layout, so nothing re-marks the platter dirty when it pins
    // and writes its own box — in a browser the host's ResizeObserver does, and
    // the settled box reaches the scene on the next frame. A viewport resize is
    // the one signal the geometry sync honours without a layout engine behind
    // it, so this reads the settled box the way a browser would have anyway,
    // and keeps the sweep below from passing on an unmeasured node.
    act(() => {
      window.dispatchEvent(new Event("resize"));
    });
    harness.run(1);
    published.push(harness.root().scene.glassNode("platter")?.bounds);

    const settled = published[published.length - 1];
    expect(settled, "the node was never measured").toBeDefined();
    expect(settled).toMatchObject(anchor);

    for (const [index, bounds] of published.entries()) {
      if (bounds === undefined) continue;
      // An empty box is the honest answer to "where is this surface" before the
      // surface has been placed: it overlaps nothing, so no overlap check can
      // fire on it. Anything with area is a claim, and the only claim the
      // platter is entitled to make is its own footprint.
      if (bounds.width * bounds.height === 0) continue;
      expect(bounds, `frame ${String(index + 1)} published a box the platter does not occupy`)
        .toMatchObject(anchor);
    }

    // And the mechanism, stated so a future edit cannot reintroduce it another
    // way: the platter is never laid out in the app's flow. Its box comes from
    // the springs and its footprint is the spacer's job, so flow is something it
    // has no use for at any point in its life — and inside a plane host layer,
    // which is `position: absolute; inset: 0`, flow means the viewport origin.
    expect(positions).not.toContain("static");
  });

  it("realigns when a reflow moves the closed footprint without resizing it", async () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassMorph open={false} nodeId="platter">
          {() => <span>Menu</span>}
        </GlassMorph>
      </GlassGroup>,
    );
    // One frame to measure and pin, which is when the platter leaves the flow.
    harness.run(2);

    const platter = platterOf();
    expect(platter.style.top).toBe("10px");

    // A sibling arriving above the spacer moves it and resizes nothing — the
    // ResizeObserver on the spacer alone never hears about it, and a `fixed`
    // platter keeps offsets that now point at where the footprint used to be.
    anchor = { ...anchor, y: 60 };
    await act(async () => {
      harness.result.container.prepend(document.createElement("div"));
    });

    expect(platter.style.top).toBe("60px");
  });

  it("stays morphing until the shape channels settle, not only the box", () => {
    // `gap` cancels the placement offset, so the open end occupies exactly the
    // closed box: everything that travels is radius, smoothing and thickness. A
    // settle predicate reading only the box calls this morph over on the frame it
    // begins, which cuts the platter's corner animation off at its first value.
    const onMorphEnd = vi.fn();

    function Morphing(): ReactNode {
      const [open, setOpen] = useState(false);
      return (
        <GlassGroup id="g">
          <button type="button" onClick={() => setOpen(true)}>
            open
          </button>
          <GlassMorph
            open={open}
            nodeId="platter"
            gap={-natural.height}
            radius={14}
            openRadius={64}
            thickness={8}
            openThickness={40}
            onMorphEnd={onMorphEnd}
          >
            {() => <span>Menu</span>}
          </GlassMorph>
        </GlassGroup>
      );
    }

    const harness = renderGlass(<Morphing />);
    harness.run(2);

    act(() => {
      harness.result.getByText("open").click();
    });
    harness.run(1);

    expect(onMorphEnd).not.toHaveBeenCalled();
    expect(platterOf().hasAttribute("data-vitrea-morphing")).toBe(true);

    harness.run(120);
    expect(onMorphEnd).toHaveBeenCalledWith(true);
    expect(platterOf().hasAttribute("data-vitrea-morphing")).toBe(false);
  });
});
