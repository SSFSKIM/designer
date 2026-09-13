/**
 * Who owns a label's colour (W27e G2; W27 §Design's *Where each feature lives*,
 * binding; claims §5.140 §6).
 *
 * Apple transforms the app's own text colour; vitrea publishes a colour an app
 * opts into, and root Decision Log #34(c) was won at cost so that an app's own
 * rule beats the runtime. §Design keeps both true by dividing the surfaces —
 * vitrea's own controls receive the operator by default because vitrea owns
 * those labels, and arbitrary content under `GlassSurface asChild` keeps the
 * token unless the author asks. After Decision Log 15 (a) the published token
 * *is* the operator's output, so what the division controls is the specificity
 * the runtime's `color` declaration lands at, and that is what these assert:
 * the attribute, on the elements that should carry it and not on the ones that
 * should not.
 */

import { describe, expect, it } from "vitest";
import type { ReactNode } from "react";

import {
  GlassButton,
  GlassGroup,
  GlassIconButton,
  GlassSegmentedControl,
  GlassSurface,
  GlassToolbar,
} from "../src/index";
import { renderGlass } from "./harness";

const VIBRANT = "data-vitrea-vibrant";

const owned = (element: Element | null): boolean => element?.hasAttribute(VIBRANT) === true;

/** One frame, so registration and the root's first write have both happened. */
function mount(children: ReactNode) {
  const harness = renderGlass(<GlassGroup id="g">{children}</GlassGroup>);
  harness.frame(0);
  return harness;
}

describe("vitrea's own controls own their labels by default", () => {
  it("marks a button, an icon button and a segmented control's track", () => {
    const harness = mount(
      <>
        <GlassButton>Share</GlassButton>
        <GlassIconButton aria-label="Bookmark">☆</GlassIconButton>
        <GlassSegmentedControl
          aria-label="View"
          items={[{ value: "a", label: "A" }, { value: "b", label: "B" }]}
          value="a"
          onChange={() => {}}
        />
      </>,
    );
    expect(owned(harness.result.getByRole("button", { name: "Share" }))).toBe(true);
    expect(owned(harness.result.getByRole("button", { name: "Bookmark" }))).toBe(true);
    expect(owned(harness.result.getByRole("radiogroup", { name: "View" }))).toBe(true);
  });

  it("needs nothing on the toolbar itself, whose labels live on its items", () => {
    // `GlassToolbar` renders a `role="toolbar"` element and no surface of its
    // own — the glass is on the buttons inside it — so there is no host for a
    // marker to sit on and nothing for it to own.
    const harness = mount(
      <GlassToolbar aria-label="Actions">
        <GlassButton>Share</GlassButton>
      </GlassToolbar>,
    );
    expect(owned(harness.result.getByRole("toolbar", { name: "Actions" }))).toBe(false);
    expect(owned(harness.result.getByRole("button", { name: "Share" }))).toBe(true);
  });

  it("gives the label back when the author asks for the token path", () => {
    const harness = mount(<GlassButton foreground="token">Share</GlassButton>);
    expect(owned(harness.result.getByRole("button", { name: "Share" }))).toBe(false);
  });
});

describe("arbitrary content keeps the token unless the author opts in", () => {
  it("does not mark a bare `GlassSurface asChild`", () => {
    const harness = mount(
      <GlassSurface asChild>
        <section aria-label="Panel">content</section>
      </GlassSurface>,
    );
    expect(owned(harness.result.getByRole("region", { name: "Panel" }))).toBe(false);
  });

  it("marks it under a `foreground` of `vibrant`", () => {
    const harness = mount(
      <GlassSurface asChild foreground="vibrant">
        <section aria-label="Panel">content</section>
      </GlassSurface>,
    );
    expect(owned(harness.result.getByRole("region", { name: "Panel" }))).toBe(true);
  });
});

describe("the prop's two axes", () => {
  it("takes the marker off when the author switches to an adaptation cadence", () => {
    // The two axes are one prop because §Design spells the opt-in this way, so
    // an adaptation object is also a statement that vitrea does not own the
    // label. What must not happen is the marker surviving the switch, which is
    // what a patch that said nothing about ownership would leave behind.
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassButton>Share</GlassButton>
      </GlassGroup>,
    );
    harness.frame(0);
    expect(owned(harness.result.getByRole("button", { name: "Share" }))).toBe(true);

    harness.rerender(
      <GlassGroup id="g">
        <GlassButton foreground={{ mode: "fixed" }}>Share</GlassButton>
      </GlassGroup>,
    );
    harness.frame(16);
    expect(owned(harness.result.getByRole("button", { name: "Share" }))).toBe(false);
  });
});
