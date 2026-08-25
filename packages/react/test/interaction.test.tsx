/**
 * Parent acceptance #3, at the binding level: pointer and keyboard events reach
 * the interaction machine, and the machine's channel values reach the surface.
 *
 * The continuity claim is asserted on **values**, never on pixels: a release
 * mid-press has to redirect the trajectory the press was already on. The
 * observable is the published channel — `--vitrea-press` — because that is what
 * both the CSS tier and the renderer read, and what a Playwright run can see
 * without a screenshot.
 */

import { fireEvent } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { GlassGroup, GLASS_CHANNEL_PROPERTIES, GlassButton } from "../src/index";
import { renderGlass } from "./harness";

const channel = (element: HTMLElement, name: keyof typeof GLASS_CHANNEL_PROPERTIES): number =>
  Number(element.style.getPropertyValue(GLASS_CHANNEL_PROPERTIES[name]));

function pressable() {
  const harness = renderGlass(
    <GlassGroup id="g">
      <GlassButton>Share</GlassButton>
    </GlassGroup>,
  );
  return { harness, button: harness.result.getByRole("button") };
}

describe("interaction state", () => {
  it("collapses overlapping host flags the way the kernel does", () => {
    const { harness, button } = pressable();

    fireEvent.pointerEnter(button);
    expect(harness.root().scene.glassNode(button.getAttribute("data-vitrea-node") ?? "")
      ?.descriptor.interaction).toBe("hover");

    fireEvent.focus(button);
    // hovered outranks focused: the material spends its one slot on the more
    // immediate pointer feedback, and focus has its own affordance in the DOM.
    expect(harness.root().scene.glassNode(button.getAttribute("data-vitrea-node") ?? "")
      ?.descriptor.interaction).toBe("hover");

    fireEvent.pointerDown(button, { clientX: 10, clientY: 4 });
    expect(harness.root().scene.glassNode(button.getAttribute("data-vitrea-node") ?? "")
      ?.descriptor.interaction).toBe("pressed");
  });

  it("reports `disabled` to the material and to the platform alike", () => {
    const harness = renderGlass(
      <GlassGroup id="g">
        <GlassButton disabled>Share</GlassButton>
      </GlassGroup>,
    );
    const button = harness.result.getByRole("button") as HTMLButtonElement;
    expect(button.disabled).toBe(true);
    expect(
      harness.root().scene.glassNode(button.getAttribute("data-vitrea-node") ?? "")?.descriptor
        .interaction,
    ).toBe("disabled");
  });
});

describe("press compression", () => {
  it("rises on a press and is composed as a transform, never as a shape change", () => {
    const { harness, button } = pressable();

    fireEvent.pointerDown(button, { clientX: 10, clientY: 4 });
    harness.run(8);

    expect(channel(button, "press")).toBeGreaterThan(0.5);
    // ~1–2% of geometric scale, from motion's own `pressCompressionScale`.
    expect(button.style.transform).toMatch(/^scale\(0\.9[0-9]+\)$/);
    // The shape channels are untouched: a transform cannot dirty the rect it
    // is animating, which is why the compression is composed on top.
    expect(harness.root().scene.glassNode(button.getAttribute("data-vitrea-node") ?? "")
      ?.descriptor.shape.size).toEqual([0, 0]);
  });

  it("records the press point, so the glow lands under the finger", () => {
    const { harness, button } = pressable();
    fireEvent.pointerDown(button, { clientX: 42, clientY: 7 });
    harness.run(2);

    // jsdom lays nothing out, so the host rect is at the origin and the press
    // point is the client coordinate itself. What is asserted is that the point
    // travels at all, and in the host's own frame.
    expect(button.style.getPropertyValue(GLASS_CHANNEL_PROPERTIES.pressX)).toBe("42.0000px");
    expect(button.style.getPropertyValue(GLASS_CHANNEL_PROPERTIES.pressY)).toBe("7.0000px");
  });

  it("redirects a release mid-press from where the press actually is", () => {
    const { harness, button } = pressable();

    fireEvent.pointerDown(button, { clientX: 10, clientY: 4 });
    harness.run(4);
    const atRelease = channel(button, "press");
    expect(atRelease).toBeGreaterThan(0);
    expect(atRelease).toBeLessThan(1);

    fireEvent.pointerUp(button);
    // The very next frame must continue from `atRelease`, not restart from 1 and
    // not snap to 0. A spring redirect keeps position and velocity, so a single
    // 16 ms step can only move a little — and it must keep moving downward.
    harness.run(1);
    const first = channel(button, "press");
    expect(Math.abs(first - atRelease)).toBeLessThan(0.35);

    harness.run(6);
    const later = channel(button, "press");
    expect(later).toBeLessThan(first);
  });

  it("re-presses without restarting, so the trajectory stays continuous", () => {
    const { harness, button } = pressable();

    fireEvent.pointerDown(button, { clientX: 10, clientY: 4 });
    harness.run(4);
    fireEvent.pointerUp(button);
    harness.run(2);
    const atRepress = channel(button, "press");

    fireEvent.pointerDown(button, { clientX: 10, clientY: 4 });
    harness.run(1);
    expect(Math.abs(channel(button, "press") - atRepress)).toBeLessThan(0.35);
  });

  it("ends a press even when the pointer is released off the surface", () => {
    const { harness, button } = pressable();

    fireEvent.pointerDown(button, { clientX: 10, clientY: 4 });
    harness.run(4);
    fireEvent.pointerUp(window);
    harness.run(20);

    expect(channel(button, "press")).toBeLessThan(0.05);
  });
});

describe("keyboard activation", () => {
  it("presses the material on the platform's own activation keys", () => {
    const { harness, button } = pressable();

    fireEvent.keyDown(button, { key: " " });
    harness.run(6);
    expect(channel(button, "press")).toBeGreaterThan(0.3);

    fireEvent.keyUp(button, { key: " " });
    harness.run(20);
    expect(channel(button, "press")).toBeLessThan(0.05);
  });
});

describe("glow", () => {
  it("attacks fast on a press and decays slowly on release", () => {
    const { harness, button } = pressable();

    fireEvent.pointerDown(button, { clientX: 10, clientY: 4 });
    harness.run(5, 16);
    const attacked = channel(button, "glow");

    fireEvent.pointerUp(button);
    harness.run(5, 16);
    const decayed = channel(button, "glow");

    // Same number of frames each way: the asymmetry is the driver's, not the
    // caller's, so the fall must lag the rise.
    expect(attacked).toBeGreaterThan(0.5);
    expect(decayed).toBeGreaterThan(0.2);
    expect(decayed).toBeLessThan(attacked);
  });
});
