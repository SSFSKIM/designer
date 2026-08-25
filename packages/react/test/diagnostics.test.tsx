/**
 * The dev-mode findings, and where a developer actually sees them.
 *
 * §Material variants says mixing variants inside one group warns and changes
 * nothing, and that a clear surface without a dimming policy is refused rather
 * than given an invented scrim. Parent acceptance #6 asks for the first of those
 * to reach the devtools console — so both halves are asserted: the diagnostic is
 * recorded, and the console is where it lands by default.
 */

import { describe, expect, it, vi } from "vitest";
import type { ReactNode } from "react";

import { GlassGroup, GlassSurface, useGlassDiagnostics } from "../src/index";
import { renderGlass } from "./harness";

function Diagnostics(props: { readonly onRead: (codes: string[]) => void }): ReactNode {
  props.onRead(useGlassDiagnostics().map((entry) => entry.diagnostic.code));
  return null;
}

describe("variant mixing (§Material variants)", () => {
  it("warns in the console and changes nothing", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    let codes: string[] = [];

    const harness = renderGlass(
      <>
        <Diagnostics onRead={(next) => (codes = next)} />
        <GlassGroup id="mixed" dimming={{ scrim: 0.3, direction: "darken" }}>
          <GlassSurface nodeId="regular" variant="regular" />
          <GlassSurface nodeId="clear" variant="clear" />
        </GlassGroup>
      </>,
    );

    harness.frame();

    expect(codes).toContain("variant-mixing");
    expect(warn).toHaveBeenCalled();
    const message = warn.mock.calls.map((call) => String(call[0])).join("\n");
    expect(message).toContain("variant-mixing");
    expect(message).toContain("mixed");

    // "Both render as authored" — the warning is advice, not a coercion.
    expect(harness.root().scene.glassNode("clear")?.descriptor.variant).toBe("clear");
    expect(harness.root().scene.glassNode("regular")?.descriptor.variant).toBe("regular");

    warn.mockRestore();
  });

  it("stays quiet when a group agrees on one variant", () => {
    let codes: string[] = [];
    const harness = renderGlass(
      <>
        <Diagnostics onRead={(next) => (codes = next)} />
        <GlassGroup id="uniform">
          <GlassSurface nodeId="a" />
          <GlassSurface nodeId="b" />
        </GlassGroup>
      </>,
    );
    harness.frame();
    expect(codes).not.toContain("variant-mixing");
  });
});

describe("clear without dimming", () => {
  it("is an error, and the surface renders regular instead of getting an invented scrim", () => {
    const error = vi.spyOn(console, "error").mockImplementation(() => undefined);
    let codes: string[] = [];

    const harness = renderGlass(
      <>
        <Diagnostics onRead={(next) => (codes = next)} />
        <GlassGroup id="g">
          <GlassSurface nodeId="clear" variant="clear" />
        </GlassGroup>
      </>,
    );
    harness.frame();

    expect(codes).toContain("clear-variant-needs-dimming");
    expect(error).toHaveBeenCalled();

    const node = harness
      .root()
      .renderInput()
      ?.planes.flatMap((plane) => plane.nodes)
      .find((entry) => entry.nodeId === "clear");
    expect(node?.material.variant).toBe("regular");

    error.mockRestore();
  });

  it("is satisfied by a one-line dimming policy on the group", () => {
    let codes: string[] = [];
    const harness = renderGlass(
      <>
        <Diagnostics onRead={(next) => (codes = next)} />
        <GlassGroup id="g" variant="clear" dimming={{ scrim: 0.28, direction: "darken" }}>
          <GlassSurface nodeId="clear" variant="clear" />
        </GlassGroup>
      </>,
    );
    harness.frame();

    expect(codes).not.toContain("clear-variant-needs-dimming");
    const node = harness
      .root()
      .renderInput()
      ?.planes.flatMap((plane) => plane.nodes)
      .find((entry) => entry.nodeId === "clear");
    expect(node?.material.variant).toBe("clear");
    expect(node?.material.dimming).toEqual({ scrim: 0.28, direction: "darken" });
  });
});

describe("the diagnostic sink", () => {
  it("hands findings to an app-supplied sink instead of the console", () => {
    const warn = vi.spyOn(console, "warn").mockImplementation(() => undefined);
    const seen: string[] = [];

    const harness = renderGlass(
      <GlassGroup id="mixed" dimming={{ scrim: 0.3, direction: "darken" }}>
        <GlassSurface nodeId="regular" variant="regular" />
        <GlassSurface nodeId="clear" variant="clear" />
      </GlassGroup>,
      { onDiagnostic: (entry) => seen.push(entry.diagnostic.code) },
    );
    harness.frame();

    expect(seen).toContain("variant-mixing");
    expect(warn).not.toHaveBeenCalled();
    warn.mockRestore();
  });
});
