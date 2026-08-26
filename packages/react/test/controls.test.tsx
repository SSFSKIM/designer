/**
 * The v1 controls, asserted on semantics rather than on looks.
 *
 * Parent acceptance #1 is a screen-reader claim, so the assertions are made
 * through roles and accessible names — the same surface a screen reader reads —
 * and never through class names or DOM shape.
 */

import { fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { act, useState } from "react";
import type { ReactNode } from "react";

import {
  GlassButton,
  GlassGroup,
  GlassIconButton,
  GlassSegmentedControl,
  GlassToolbar,
  TOOLBAR_ITEM_ATTRIBUTE,
} from "../src/index";
import { renderGlass } from "./harness";

describe("GlassButton", () => {
  it("is a real button: role, name, type and form participation", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassButton>Share</GlassButton>
      </GlassGroup>,
    );

    const button = harness.result.getByRole("button", { name: "Share" }) as HTMLButtonElement;
    expect(button.tagName).toBe("BUTTON");
    expect(button.type).toBe("button");
    // Real text, not a canvas glyph: selectable, focusable, IME-capable.
    expect(button.textContent).toBe("Share");
    button.focus();
    expect(document.activeElement).toBe(button);
  });

  it("participates in a form it was portalled out of", () => {
    // The host lives in the plane's host layer, not inside the <form> — X1 puts
    // it there. Form participation therefore has to come from the platform's own
    // form-owner association, which is exactly what rendering a real <button>
    // buys and what a role="button" div would have lost.
    const onSubmit = vi.fn((event: Event) => event.preventDefault());

    const harness = renderGlass(
      <>
        <form id="search" onSubmit={(event) => onSubmit(event.nativeEvent)}>
          <input name="q" aria-label="query" />
        </form>
        <GlassGroup id="g">
          <GlassButton type="submit" form="search">
            Send
          </GlassButton>
        </GlassGroup>
      </>,
    );

    const button = harness.result.getByRole("button", { name: "Send" }) as HTMLButtonElement;
    expect(button.form?.id).toBe("search");
    expect(button.closest("form")).toBeNull();

    act(() => {
      button.click();
    });
    expect(onSubmit).toHaveBeenCalledTimes(1);
  });
});

describe("GlassIconButton", () => {
  it("carries the accessible name its icon cannot", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassIconButton aria-label="More actions">
          <svg aria-hidden="true" />
        </GlassIconButton>
      </GlassGroup>,
    );
    expect(harness.result.getByRole("button", { name: "More actions" })).toBeTruthy();
  });

  it("is a capsule by default, so its shape follows its measured box", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassIconButton aria-label="More" nodeId="icon" />
      </GlassGroup>,
    );
    expect(harness.root().scene.glassNode("icon")?.descriptor.shapeFamily).toBe("capsule");
  });
});

describe("GlassToolbar", () => {
  it("is a toolbar with one tab stop, and arrows move within it", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions">
        <GlassButton>One</GlassButton>
        <GlassButton>Two</GlassButton>
        <GlassButton>Three</GlassButton>
      </GlassToolbar>,
    );

    const toolbar = harness.result.getByRole("toolbar", { name: "Actions" });
    const buttons = harness.result.getAllByRole("button") as HTMLButtonElement[];

    expect(buttons.map((button) => button.tabIndex)).toEqual([0, -1, -1]);
    for (const button of buttons) {
      expect(button.hasAttribute(TOOLBAR_ITEM_ATTRIBUTE)).toBe(true);
    }

    buttons[0]?.focus();
    fireEvent.keyDown(toolbar, { key: "ArrowRight" });
    expect(document.activeElement).toBe(buttons[1]);
    expect(buttons.map((button) => button.tabIndex)).toEqual([-1, 0, -1]);

    fireEvent.keyDown(toolbar, { key: "End" });
    expect(document.activeElement).toBe(buttons[2]);

    fireEvent.keyDown(toolbar, { key: "Home" });
    expect(document.activeElement).toBe(buttons[0]);
  });

  it("wraps at the ends, and skips a disabled item", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions">
        <GlassButton>One</GlassButton>
        <GlassButton disabled>Two</GlassButton>
        <GlassButton>Three</GlassButton>
      </GlassToolbar>,
    );

    const toolbar = harness.result.getByRole("toolbar");
    const one = harness.result.getByRole("button", { name: "One" });
    const three = harness.result.getByRole("button", { name: "Three" });

    one.focus();
    fireEvent.keyDown(toolbar, { key: "ArrowRight" });
    expect(document.activeElement).toBe(three);

    fireEvent.keyDown(toolbar, { key: "ArrowRight" });
    expect(document.activeElement).toBe(one);
  });

  it("moves the tab stop off an item that has just disabled itself", async () => {
    // The item set is filtered before the tab indices are assigned, so an item
    // that leaves the set keeps whatever index it was last given: the toolbar
    // hands the stop to its new first item and the page ends up with two.
    function Disabling(): ReactNode {
      const [disabled, setDisabled] = useState(false);
      return (
        <>
          <button type="button" onClick={() => setDisabled(true)}>
            disable
          </button>
          <GlassToolbar aria-label="Actions">
            <GlassButton {...(disabled ? { "aria-disabled": true } : {})}>One</GlassButton>
            <GlassButton>Two</GlassButton>
          </GlassToolbar>
        </>
      );
    }

    const harness = renderGlass(<Disabling />);
    const one = harness.result.getByRole("button", { name: "One" });
    const two = harness.result.getByRole("button", { name: "Two" });
    expect([one.tabIndex, two.tabIndex]).toEqual([0, -1]);

    // `await`, because the toolbar watches the item set with a MutationObserver
    // and its records arrive on a microtask.
    await act(async () => {
      harness.result.getByText("disable").click();
    });

    expect([one.tabIndex, two.tabIndex]).toEqual([-1, 0]);
  });

  it("creates one group, so its members share a proxy and merge as one material", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions">
        <GlassButton nodeId="a">One</GlassButton>
        <GlassButton nodeId="b">Two</GlassButton>
      </GlassToolbar>,
    );

    const groupA = harness.root().scene.glassNode("a")?.descriptor.groupId;
    const groupB = harness.root().scene.glassNode("b")?.descriptor.groupId;
    expect(groupA).toBeDefined();
    expect(groupA).toBe(groupB);
  });

  it("is not itself a glass surface — X1 forbids the overlap that would be", () => {
    const harness = renderGlass(
      <GlassToolbar aria-label="Actions">
        <GlassButton>One</GlassButton>
      </GlassToolbar>,
    );
    const toolbar = harness.result.getByRole("toolbar");
    expect(toolbar.hasAttribute("data-vitrea-node")).toBe(false);
  });
});

describe("GlassSegmentedControl", () => {
  const items = [
    { value: "day", label: "Day" },
    { value: "week", label: "Week" },
    { value: "month", label: "Month" },
  ] as const;

  function Controlled(props: { readonly onChange?: (value: string) => void }): ReactNode {
    const [value, setValue] = useState<string>("day");
    return (
      <GlassGroup id="g">
        <GlassSegmentedControl
          aria-label="Range"
          items={items}
          value={value}
          onChange={(next) => {
            setValue(next);
            props.onChange?.(next);
          }}
        />
      </GlassGroup>
    );
  }

  it("is a radiogroup of radios, with exactly one checked", () => {
    const harness = renderGlass(<Controlled />);

    expect(harness.result.getByRole("radiogroup", { name: "Range" })).toBeTruthy();
    const radios = harness.result.getAllByRole("radio");
    expect(radios).toHaveLength(3);
    expect(radios.filter((radio) => radio.getAttribute("aria-checked") === "true")).toHaveLength(1);
    expect(harness.result.getByRole("radio", { name: "Day" }).getAttribute("aria-checked")).toBe("true");
  });

  it("gives the checked radio the only tab stop", () => {
    const harness = renderGlass(<Controlled />);
    const radios = harness.result.getAllByRole("radio") as HTMLButtonElement[];
    expect(radios.map((radio) => radio.tabIndex)).toEqual([0, -1, -1]);
  });

  it("moves the selection with the arrows, as a radio group does", () => {
    const onChange = vi.fn();
    const harness = renderGlass(<Controlled onChange={onChange} />);
    const group = harness.result.getByRole("radiogroup");

    fireEvent.keyDown(group, { key: "ArrowRight" });
    expect(onChange).toHaveBeenLastCalledWith("week");
    expect(harness.result.getByRole("radio", { name: "Week" }).getAttribute("aria-checked")).toBe("true");

    fireEvent.keyDown(group, { key: "ArrowLeft" });
    expect(onChange).toHaveBeenLastCalledWith("day");
  });

  it("selects on click", () => {
    const onChange = vi.fn();
    const harness = renderGlass(<Controlled onChange={onChange} />);
    act(() => {
      harness.result.getByRole("radio", { name: "Month" }).click();
    });
    expect(onChange).toHaveBeenCalledWith("month");
  });

  it("hides the indicator from the accessibility tree — it is decoration", () => {
    const harness = renderGlass(<Controlled />);
    const indicator = harness.result.container.ownerDocument.querySelector("[data-vitrea-indicator]");
    expect(indicator?.getAttribute("aria-hidden")).toBe("true");
  });

  it("registers only the track as glass, never the indicator (X1's overlap rule)", () => {
    const harness = renderGlass(<Controlled />);
    const hosts = harness.root().plane("base").hostLayer.querySelectorAll("[data-vitrea-node]");
    expect(hosts).toHaveLength(1);
    expect(hosts[0]?.getAttribute("role")).toBe("radiogroup");
  });
});
