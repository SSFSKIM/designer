/**
 * `GlassMorph`'s two invariants that do not need a browser to state.
 *
 * jsdom lays nothing out, so the boxes are stubbed: the closed footprint and the
 * platter's natural size are the two measurements the component takes, and both
 * are read through `getBoundingClientRect` and `offsetWidth`/`offsetHeight`.
 * Stubbing exactly those makes the geometry deterministic and leaves everything
 * being asserted — when the platter realigns, and when it calls itself settled —
 * the component's own logic.
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

const offsets = new Map<"offsetWidth" | "offsetHeight", PropertyDescriptor | undefined>();

beforeEach(() => {
  anchor = { x: 10, y: 10, width: 100, height: 40 };

  vi.spyOn(HTMLElement.prototype, "getBoundingClientRect").mockImplementation(function (
    this: HTMLElement,
  ) {
    const box = this.hasAttribute("data-vitrea-morph-anchor") ? anchor : ZERO;
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
