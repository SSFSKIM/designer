/**
 * A toolbar's sequence, when one of its items has been hoisted out of it.
 *
 * The consumer's observation, from 0.1.1: a toolbar whose last control is a
 * `GlassMorph` handed its single tab stop to that control. Tab reached the
 * toolbar at its visually *last* item, `Home` went there, and `ArrowRight` from
 * it walked to the first. Correct ARIA — one tab stop, arrows within — and the
 * wrong sequence.
 *
 * Nothing was wrong on its own terms. `GlassMorph` hoists its closed platter
 * into a plane mount, and `GlassToolbar` collects its items with
 * `querySelectorAll` — document order, because a member need not be a
 * descendant. Where the mount lands among the plane layer's children is then an
 * accident: the fixture below, a toolbar that portals itself, lands the platter
 * *first*, while the demo's playground, whose app portals the whole `<nav>`,
 * lands it *last* and so was correct by luck. Opening and closing the menu
 * re-appends the mount at the end, so the order does not even hold still.
 *
 * An item that has been hoisted therefore names the placeholder it left behind,
 * and the toolbar sorts by those. This file is the reproduction of record; the
 * playground's e2e is a guard over an app that happened not to show it.
 */

import { fireEvent } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { act, useState } from "react";
import type { ReactNode } from "react";

import {
  GlassButton,
  GlassMorph,
  GlassToolbar,
  PLANE_ANCHOR_ATTRIBUTE,
  useToolbarItem,
} from "../src/index";
import { renderGlass } from "./harness";

/** The closed footprint, in viewport coordinates. */
const anchor = { x: 10, y: 10, width: 100, height: 40 };
const ZERO = { x: 0, y: 0, width: 0, height: 0 };
const natural = { width: 100, height: 40 };

const offsets = new Map<"offsetWidth" | "offsetHeight", PropertyDescriptor | undefined>();

beforeEach(() => {
  // The same layout stubs `morph.test.tsx` uses: jsdom lays nothing out, and the
  // morph takes exactly two measurements.
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
    if (descriptor !== undefined) Object.defineProperty(HTMLElement.prototype, name, descriptor);
  }
  offsets.clear();
});

/** The morph's trigger, marked as a toolbar item the way a consumer marks it. */
function MorphTrigger(props: { readonly label: string }): ReactNode {
  const toolbarItem = useToolbarItem();
  return (
    <GlassMorph open={false} radius={12}>
      {() => (
        <button {...toolbarItem} type="button">
          {props.label}
        </button>
      )}
    </GlassMorph>
  );
}

/** The same trigger, with an open state the test can cycle. */
function CyclingTrigger(props: {
  readonly open: boolean;
  readonly onToggle: () => void;
}): ReactNode {
  const toolbarItem = useToolbarItem();
  return (
    <GlassMorph open={props.open} radius={12}>
      {() => (
        <button {...toolbarItem} type="button" onClick={props.onToggle}>
          Actions
        </button>
      )}
    </GlassMorph>
  );
}

/** The playground's own shape: three plain controls, then a morph. */
function Playground(props: { readonly last?: boolean } = {}): ReactNode {
  const morph = <MorphTrigger label="Actions" />;
  return (
    <nav aria-label="Playground toolbar">
      <GlassToolbar aria-label="Playground actions">
        {props.last === false ? morph : null}
        <GlassButton>Share</GlassButton>
        <GlassButton>Favourite</GlassButton>
        <GlassButton>Duplicate</GlassButton>
        {props.last === false ? null : morph}
      </GlassToolbar>
    </nav>
  );
}

const names = (elements: readonly HTMLElement[]): readonly string[] =>
  elements.map((element) => (element.textContent ?? "").trim());

describe("a toolbar whose last item hoists itself out of it", () => {
  it("keeps the single tab stop on the first control the author wrote", () => {
    const harness = renderGlass(<Playground />);
    const buttons = harness.result.getAllByRole("button") as HTMLButtonElement[];
    const stops = buttons.filter((button) => button.tabIndex === 0);

    // Still exactly one tab stop — the half that was already right.
    expect(stops).toHaveLength(1);
    // And it is the first control in the toolbar, not the morph trigger that
    // happens to precede it in the document.
    expect(names(stops)).toEqual(["Share"]);
  });

  it("walks the arrows in the author's order, ending on the hoisted item", () => {
    const harness = renderGlass(<Playground />);
    const toolbar = harness.result.getByRole("toolbar");
    const at = (): string => (document.activeElement?.textContent ?? "").trim();

    harness.result.getByRole("button", { name: "Share" }).focus();
    for (const expected of ["Favourite", "Duplicate", "Actions", "Share"]) {
      fireEvent.keyDown(toolbar, { key: "ArrowRight" });
      expect(at()).toBe(expected);
    }
  });

  it("puts Home on the first control and End on the hoisted one", () => {
    const harness = renderGlass(<Playground />);
    const toolbar = harness.result.getByRole("toolbar");

    fireEvent.keyDown(toolbar, { key: "End" });
    expect((document.activeElement?.textContent ?? "").trim()).toBe("Actions");

    fireEvent.keyDown(toolbar, { key: "Home" });
    expect((document.activeElement?.textContent ?? "").trim()).toBe("Share");
  });

  it("reads the same order to a screen reader as it gives the arrows", () => {
    // `aria-owns` appends owned elements after an element's DOM children, so the
    // accessibility tree already put the hoisted trigger last while the arrows
    // put it first. The two orders disagreeing is worse than either being wrong
    // on its own; this is the assertion that they no longer do.
    const harness = renderGlass(<Playground />);
    const toolbar = harness.result.getByRole("toolbar");
    const trigger = harness.result.getByRole("button", { name: "Actions" });

    expect(toolbar.getAttribute("aria-owns")).toBe(trigger.id);
    expect(trigger.id).not.toBe("");
  });

  it("takes the author's order even when the hoisted item comes first", () => {
    // The other direction, and the one a "descendants first, hoisted last" rule
    // would get wrong: the sequence follows the placeholder's position, not a
    // fixed tier.
    const harness = renderGlass(<Playground last={false} />);
    const stops = (harness.result.getAllByRole("button") as HTMLButtonElement[]).filter(
      (button) => button.tabIndex === 0,
    );
    expect(names(stops)).toEqual(["Actions"]);

    const toolbar = harness.result.getByRole("toolbar");
    fireEvent.keyDown(toolbar, { key: "End" });
    expect((document.activeElement?.textContent ?? "").trim()).toBe("Duplicate");
  });

  it("marks the hoisted platter with the placeholder it left in the flow", () => {
    const harness = renderGlass(<Playground />);
    const trigger = harness.result.getByRole("button", { name: "Actions" });
    // Read upwards from the item, the way the toolbar reads it — the app marks
    // the trigger, and the marker belongs to the platter that was hoisted.
    const anchorId = trigger
      .closest(`[${PLANE_ANCHOR_ATTRIBUTE}]`)
      ?.getAttribute(PLANE_ANCHOR_ATTRIBUTE);

    expect(anchorId).toBeTruthy();
    const placeholder = document.getElementById(anchorId ?? "");
    expect(placeholder?.hasAttribute("data-vitrea-morph-anchor")).toBe(true);
    // The placeholder is inside the toolbar — which is what makes it a position
    // in *this* sequence rather than somewhere else in the document.
    expect(harness.result.getByRole("toolbar").contains(placeholder)).toBe(true);
  });

  it("survives the platter changing planes, which used to flip the order", () => {
    // Opening promotes the platter to the overlay plane and closing demotes it,
    // and each move re-appends its mount — so the document order the toolbar
    // used to follow was different before and after a single menu cycle, and the
    // tab stop moved with it.
    function Cycling(): ReactNode {
      const [open, setOpen] = useState(false);
      return (
        <GlassToolbar aria-label="Playground actions">
          <GlassButton>Share</GlassButton>
          <CyclingTrigger open={open} onToggle={() => setOpen(!open)} />
        </GlassToolbar>
      );
    }

    const harness = renderGlass(<Cycling />);
    const stops = (): readonly string[] =>
      names(
        (harness.result.getAllByRole("button") as HTMLButtonElement[]).filter(
          (button) => button.tabIndex === 0,
        ),
      );

    expect(stops()).toEqual(["Share"]);

    act(() => {
      harness.result.getByRole("button", { name: "Actions" }).click();
    });
    harness.frame();
    act(() => {
      harness.result.getByRole("button", { name: "Actions" }).click();
    });
    harness.frame();

    expect(stops()).toEqual(["Share"]);
  });
});
