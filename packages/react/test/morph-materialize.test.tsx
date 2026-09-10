/**
 * `GlassMorph transition="materialize"` — W27d's morph subset.
 *
 * The matched-geometry morph is one surface travelling between two shapes. The
 * materialize transition is the other thing Apple's `GlassEffectTransition`
 * names: two surfaces, each keeping its own geometry, one dematerialising while
 * the other materialises, with the *content* crossfading and the material's
 * disappearance carried entirely by presence (X6 — presence never touches
 * element opacity, on the host or on any ancestor).
 *
 * jsdom lays nothing out, so the two measurements the component takes — the
 * closed footprint and each end's natural size — are stubbed, exactly as in
 * `morph.test.tsx`, and everything asserted below is the component's own logic:
 * which boxes it writes, which end it declares present, what it does to content
 * opacity per frame, and when the two ends exist at all.
 */

import { describe, expect, it, vi, afterEach, beforeEach } from "vitest";
import { act, useState } from "react";
import type { ReactNode } from "react";

import { GlassGroup, GlassMorph } from "../src/index";
import { renderGlass, type Harness } from "./harness";

/** The closed footprint, in viewport coordinates. Mutable: a reflow moves it. */
let anchor = { x: 10, y: 60, width: 120, height: 40 };

/** The two ends' natural sizes. Deliberately different: no geometry is matched. */
const NATURAL = {
  source: { width: 120, height: 40 },
  destination: { width: 240, height: 160 },
} as const;

/** Where the open end lands under the default placement, `gap` = 8. */
const OPEN_BOX = { x: 10, y: 108, width: 240, height: 160 };

const ZERO = { x: 0, y: 0, width: 0, height: 0 };

const offsets = new Map<"offsetWidth" | "offsetHeight", PropertyDescriptor | undefined>();

const declared = (value: string): number | null =>
  value === "" ? null : Number.parseFloat(value);

const endOf = (element: HTMLElement): "source" | "destination" | null => {
  const owner = element.closest<HTMLElement>("[data-vitrea-morph-end]");
  const end = owner?.dataset.vitreaMorphEnd;
  return end === "source" || end === "destination" ? end : null;
};

/**
 * A platter's box, modelled from its own declarations — the same two CSS rules
 * `morph.test.tsx` writes out. Every materialize platter is `position: fixed`
 * for its whole life, and an omitted size is its content's natural size.
 */
function platterBox(element: HTMLElement): typeof ZERO {
  const style = element.style;
  const natural = NATURAL[endOf(element) ?? "source"];
  return {
    x: declared(style.left) ?? 0,
    y: declared(style.top) ?? 0,
    width: declared(style.width) ?? natural.width,
    height: declared(style.height) ?? natural.height,
  };
}

beforeEach(() => {
  anchor = { x: 10, y: 60, width: 120, height: 40 };

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

  for (const name of ["offsetWidth", "offsetHeight"] as const) {
    offsets.set(name, Object.getOwnPropertyDescriptor(HTMLElement.prototype, name));
    Object.defineProperty(HTMLElement.prototype, name, {
      configurable: true,
      get(this: HTMLElement) {
        if (!this.hasAttribute("data-vitrea-morph-content")) return 0;
        const natural = NATURAL[endOf(this) ?? "source"];
        return name === "offsetWidth" ? natural.width : natural.height;
      },
    });
  }
});

afterEach(() => {
  vi.restoreAllMocks();
  for (const [name, descriptor] of offsets) {
    if (descriptor === undefined) {
      delete (HTMLElement.prototype as unknown as Record<string, unknown>)[name];
    } else Object.defineProperty(HTMLElement.prototype, name, descriptor);
  }
  offsets.clear();
});

const endEl = (end: "source" | "destination"): HTMLElement | null =>
  document.querySelector<HTMLElement>(`[data-vitrea-morph-end="${end}"]`);

const required = (end: "source" | "destination"): HTMLElement => {
  const element = endEl(end);
  if (element === null) throw new Error(`The ${end} platter was not rendered.`);
  return element;
};

const contentOf = (end: "source" | "destination"): HTMLElement => {
  const content = required(end).querySelector<HTMLElement>("[data-vitrea-morph-content]");
  if (content === null) throw new Error(`The ${end} content was not rendered.`);
  return content;
};

const boxOf = (element: HTMLElement): typeof ZERO => platterBox(element);

const opacityOf = (end: "source" | "destination"): number =>
  Number.parseFloat(contentOf(end).style.opacity || "1");

interface Fixture {
  readonly harness: Harness;
  setOpen(open: boolean): void;
}

interface FixtureOptions {
  readonly nodeId?: string;
  readonly reducedMotion?: boolean;
  readonly onMorphEnd?: (open: boolean) => void;
}

function mount(options: FixtureOptions = {}): Fixture {
  let setOpen: ((open: boolean) => void) | null = null;

  function Fixture(): ReactNode {
    const [open, set] = useState(false);
    setOpen = set;
    return (
      <GlassGroup id="g">
        <GlassMorph
          open={open}
          transition="materialize"
          {...(options.nodeId === undefined ? {} : { nodeId: options.nodeId })}
          {...(options.onMorphEnd === undefined ? {} : { onMorphEnd: options.onMorphEnd })}
        >
          {({ open: end }) =>
            end ? <div data-testid="menu">Menu</div> : <button type="button">Actions</button>
          }
        </GlassMorph>
      </GlassGroup>
    );
  }

  const harness = renderGlass(
    <Fixture />,
    options.reducedMotion === true ? { reducedMotion: true } : {},
  );
  // Two frames: the closed end is measured on a frame, then placed.
  harness.run(2);

  return {
    harness,
    setOpen(open) {
      act(() => setOpen?.(open));
    },
  };
}

describe("GlassMorph transition=materialize", () => {
  it("renders one platter per end, each registered under its own id and its own box", () => {
    const fixture = mount({ nodeId: "platter" });

    // Before the first open there is no destination at all: an unopened morph
    // publishes exactly the one surface the app can see.
    expect(endEl("destination")).toBeNull();
    expect(boxOf(required("source"))).toMatchObject(anchor);

    fixture.setOpen(true);
    fixture.harness.run(2);

    const source = required("source");
    const destination = required("destination");
    const ids = [
      source.getAttribute("data-vitrea-node"),
      destination.getAttribute("data-vitrea-node"),
    ];
    expect(new Set(ids).size, "the two ends share a node id").toBe(2);
    for (const id of ids) {
      expect(fixture.harness.root().scene.glassNode(id ?? "")).toBeDefined();
    }

    // No geometry is matched: each end sits on its own box for the whole
    // transition, and neither ever takes a value between the two.
    for (let frame = 0; frame < 20; frame += 1) {
      expect(boxOf(source)).toMatchObject(anchor);
      expect(boxOf(destination)).toMatchObject(OPEN_BOX);
      fixture.harness.run(1);
    }
  });

  it("crossfades the content and never the host's or an ancestor's opacity", () => {
    const fixture = mount();
    fixture.setOpen(true);
    fixture.harness.run(1);

    const source = required("source");
    const destination = required("destination");

    let lastSource = opacityOf("source");
    let lastDestination = opacityOf("destination");
    expect(lastSource).toBe(1);
    expect(lastDestination).toBe(0);

    let travelled = false;
    for (let frame = 0; frame < 20; frame += 1) {
      fixture.harness.run(1);
      const nextSource = opacityOf("source");
      const nextDestination = opacityOf("destination");
      expect(nextSource).toBeLessThanOrEqual(lastSource);
      expect(nextDestination).toBeGreaterThanOrEqual(lastDestination);
      if (nextDestination > 0 && nextDestination < 1) travelled = true;
      lastSource = nextSource;
      lastDestination = nextDestination;

      // X6, in the form a machine can check: the material's presence is what
      // moves, so the host and every ancestor the runtime writes stay opaque.
      for (const end of [source, destination]) {
        for (let node: HTMLElement | null = end; node !== null; node = node.parentElement) {
          expect(node.style.opacity, "presence must never be element opacity").toBe("");
          expect(getComputedStyle(node).opacity).toBe("1");
        }
      }
    }

    expect(travelled, "the crossfade never passed through an intermediate value").toBe(true);
    expect(lastSource).toBe(0);
    expect(lastDestination).toBe(1);
  });

  it("hands presence to the destination and takes it from the source", () => {
    const fixture = mount();

    expect(required("source").hasAttribute("data-vitrea-morph-present")).toBe(true);

    fixture.setOpen(true);
    fixture.harness.run(2);

    expect(required("source").hasAttribute("data-vitrea-morph-present")).toBe(false);
    expect(required("destination").hasAttribute("data-vitrea-morph-present")).toBe(true);

    // And the end that is leaving stops being a target the moment it does, so a
    // press cannot land on a platter that is on its way out.
    expect(required("source").style.pointerEvents).toBe("none");
    expect(required("destination").style.pointerEvents).not.toBe("none");
  });

  it("continues from where it is when the crossfade is reversed mid-flight", () => {
    const onMorphEnd = vi.fn();
    const fixture = mount({ onMorphEnd });

    fixture.setOpen(true);
    fixture.harness.run(6);

    const midFlight = opacityOf("destination");
    expect(midFlight).toBeGreaterThan(0);
    expect(midFlight).toBeLessThan(1);
    expect(onMorphEnd).not.toHaveBeenCalled();

    fixture.setOpen(false);
    fixture.harness.run(1);

    const afterReversal = opacityOf("destination");
    expect(afterReversal, "the reversal jumped rather than continued").toBeLessThan(midFlight);
    expect(afterReversal).toBeGreaterThan(0);

    fixture.harness.run(20);
    expect(onMorphEnd).toHaveBeenCalledTimes(1);
    expect(onMorphEnd).toHaveBeenCalledWith(false);
  });

  it("keeps the destination only while it is on screen", () => {
    const fixture = mount({ nodeId: "platter" });

    fixture.setOpen(true);
    fixture.harness.run(2);
    const id = required("destination").getAttribute("data-vitrea-node") ?? "";
    expect(fixture.harness.root().scene.glassNode(id)).toBeDefined();

    fixture.setOpen(false);
    // Still there while it dematerialises — unmounting it on the frame the
    // author closed would cut the transition off at its first value.
    fixture.harness.run(1);
    expect(endEl("destination")).not.toBeNull();

    fixture.harness.run(24);
    expect(endEl("destination")).toBeNull();
    expect(fixture.harness.root().scene.glassNode(id)).toBeUndefined();
  });

  it("settles without animating under Reduced Motion", () => {
    const onMorphEnd = vi.fn();
    const fixture = mount({ reducedMotion: true, onMorphEnd });

    fixture.setOpen(true);

    // Never anywhere between the two ends, on either end's content: the reduced
    // rule is that presence steps to its target and the crossfade steps with it.
    for (let frame = 0; frame < 4; frame += 1) {
      fixture.harness.run(1);
      expect([0, 1]).toContain(opacityOf("source"));
      expect([0, 1]).toContain(opacityOf("destination"));
    }

    expect(opacityOf("source")).toBe(0);
    expect(opacityOf("destination")).toBe(1);
    // `morphing` follows the *material*, which the host steps on its own frame,
    // so it clears a frame after the content rather than in the same breath.
    expect(required("destination").hasAttribute("data-vitrea-morphing")).toBe(false);
    expect(onMorphEnd).toHaveBeenCalledWith(true);
  });

  it("opens again under the same id after the open end has been released", () => {
    const fixture = mount({ nodeId: "platter" });

    for (const round of [1, 2]) {
      fixture.setOpen(true);
      fixture.harness.run(24);
      expect(opacityOf("destination"), `round ${String(round)} did not open`).toBe(1);
      expect(required("destination").getAttribute("data-vitrea-node")).toBe("platter-open");

      fixture.setOpen(false);
      fixture.harness.run(24);
      expect(endEl("destination")).toBeNull();
    }
  });

  it("moves both ends when a reflow moves the closed footprint", async () => {
    const fixture = mount();
    fixture.setOpen(true);
    fixture.harness.run(2);

    expect(boxOf(required("source"))).toMatchObject(anchor);
    expect(boxOf(required("destination"))).toMatchObject(OPEN_BOX);

    // A sibling arriving above the spacer moves it and resizes nothing. Both
    // platters are `position: fixed` on viewport numbers, so both are now
    // standing where the footprint used to be.
    anchor = { ...anchor, y: 200 };
    await act(async () => {
      fixture.harness.result.container.prepend(document.createElement("div"));
    });

    expect(boxOf(required("source"))).toMatchObject(anchor);
    expect(boxOf(required("destination"))).toMatchObject({ ...OPEN_BOX, y: 248 });
  });

  it("leaves the matched-geometry morph as the default", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassMorph open={false} nodeId="platter">
          {() => <span>Menu</span>}
        </GlassMorph>
      </GlassGroup>,
    );
    harness.run(2);

    expect(document.querySelectorAll("[data-vitrea-morph]")).toHaveLength(1);
    expect(document.querySelectorAll("[data-vitrea-morph-end]")).toHaveLength(0);
  });
});
