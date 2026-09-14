/**
 * `GlassRoot`'s `windowActivation` prop reaching the runtime (W28 G3).
 *
 * Activation is a pose of the ROOT, not a state of a surface: a window is
 * active or it is not, once per document. So the binding has exactly the shape
 * the colour scheme's has — a three-valued prop handed to `createGlassRoot`, a
 * setter on the live root for every change after that, and no material of its
 * own. What is asserted here is that it arrives, that a change does not rebuild
 * the root (rebuilding it would drop every registration in the tree), that an
 * explicit pin beats the window's own focus in both directions, and that
 * returning to `"auto"` hands the pose back to the window.
 *
 * Whether the observer reads focus correctly is platform-web's
 * (`test/window-activation.test.ts`); whether the receded material is the right
 * material is the calibration bed's (claims §5.145–§5.147). This file only
 * cares that the three values travel.
 */

import { render } from "@testing-library/react";
import { act, useState, type ReactNode } from "react";
import { describe, expect, it } from "vitest";

import type { GlassRoot as PlatformGlassRoot } from "@vitreajs/vitrea-web";

import {
  GlassGroup,
  GlassRoot,
  GlassSurface,
  useGlassRoot,
  useGlassTicker,
  useGlassWindowActivation,
  type GlassWindowActivation,
} from "../src/index";
import { setWindowFocused } from "./setup";

/**
 * The whole resolved material of the first node the frame drew, as one string.
 *
 * Deliberately not one named field: which optical term the recede moves is the
 * profile document's business and it has already moved more than once
 * (§5.130 → §5.141 → §5.145). What this file claims is that the material is a
 * different material, which is a claim the whole object can carry and a single
 * field cannot without being re-chosen every wave.
 */
const opticsOf = (root: PlatformGlassRoot): string => {
  const node = root.renderInput()?.planes.flatMap((plane) => plane.nodes)[0];
  if (node === undefined) throw new Error("the frame resolved no node to read a material off");
  return JSON.stringify(node.optics);
};

interface Mounted {
  root(): PlatformGlassRoot;
  /** What the resolved-pose hook last published to a component in the tree. */
  readout(): string | undefined;
  frame(): void;
  /** Re-render with a different activation, under the SAME root. */
  setActivation(activation: GlassWindowActivation): void;
}

/** The suite's window starts focused (`test/setup.ts`); this moves it. */
function setWindowFocus(focused: boolean): void {
  act(() => {
    setWindowFocused(focused);
  });
}

function mount(initial: GlassWindowActivation | undefined): Mounted {
  let held: PlatformGlassRoot | null = null;
  let advance: ((dtMs: number) => void) | undefined;
  let change: ((activation: GlassWindowActivation) => void) | undefined;
  let published: string | undefined;

  function Capture(): ReactNode {
    held = useGlassRoot();
    const ticker = useGlassTicker();
    advance = (dtMs) => ticker.advance(dtMs);
    published = useGlassWindowActivation();
    return null;
  }

  function Switcher(): ReactNode {
    const [activation, setActivation] = useState<GlassWindowActivation | undefined>(initial);
    change = setActivation;
    return (
      <GlassRoot
        autoStart={false}
        {...(activation === undefined ? {} : { windowActivation: activation })}
      >
        <Capture />
        <GlassGroup id="g1">
          <GlassSurface>ok</GlassSurface>
        </GlassGroup>
      </GlassRoot>
    );
  }

  render(<Switcher />);

  const root = (): PlatformGlassRoot => {
    if (held === null) throw new Error("the root never mounted");
    return held;
  };

  return {
    root,
    readout: () => published,
    frame: () => {
      act(() => {
        root().runFrame(0);
        // The store polls the root's pull surface once per ticker frame; the
        // hook is a subscriber to that poll and to nothing else.
        advance?.(16);
      });
    },
    setActivation: (activation) => {
      act(() => {
        change?.(activation);
      });
    },
  };
}

describe("GlassRoot's windowActivation prop", () => {
  it("defaults to auto, and a focused window is active", () => {
    const mounted = mount(undefined);
    mounted.frame();
    expect(mounted.root().windowActivation).toBe("active");
  });

  it("reaches the runtime at construction, and the material is a different material", () => {
    const active = mount(undefined);
    active.frame();

    const receded = mount("inactive");
    receded.frame();

    expect(receded.root().windowActivation).toBe("inactive");
    expect(opticsOf(receded.root())).not.toBe(opticsOf(active.root()));
  });

  it("reaches the live root on a change, without rebuilding it", () => {
    const mounted = mount("active");
    mounted.frame();
    const before = mounted.root();
    const whileActive = opticsOf(before);

    mounted.setActivation("inactive");
    mounted.frame();

    expect(mounted.root()).toBe(before);
    expect(mounted.root().windowActivation).toBe("inactive");
    expect(opticsOf(mounted.root())).not.toBe(whileActive);
  });

  it("pins inactive over a focused window", () => {
    const mounted = mount("inactive");
    mounted.frame();
    expect(document.hasFocus()).toBe(true);
    expect(mounted.root().windowActivation).toBe("inactive");
  });

  it("pins active over a blurred window", () => {
    const mounted = mount("active");
    mounted.frame();
    setWindowFocus(false);
    mounted.frame();
    expect(mounted.root().windowActivation).toBe("active");
  });

  it("follows the window again when the prop returns to auto", () => {
    const mounted = mount("active");
    mounted.frame();
    setWindowFocus(false);
    mounted.frame();
    expect(mounted.root().windowActivation).toBe("active");

    mounted.setActivation("auto");
    mounted.frame();
    expect(mounted.root().windowActivation).toBe("inactive");

    setWindowFocus(true);
    mounted.frame();
    expect(mounted.root().windowActivation).toBe("active");
  });

  it("lets the imperative setter on the handle pin a root the prop left on auto", () => {
    const mounted = mount("auto");
    mounted.frame();
    expect(mounted.root().windowActivation).toBe("active");

    act(() => {
      mounted.root().setWindowActivation("inactive");
    });
    mounted.frame();

    // No prop changed, so the binding's effect never re-ran: what an app set by
    // hand is still what the root is on. A binding that re-asserted its prop
    // every frame would make `handle.root` a write-only surface.
    expect(mounted.root().windowActivation).toBe("inactive");
  });
});

describe("useGlassWindowActivation", () => {
  it("publishes the pose the root resolved, not the one the prop asked for", () => {
    const mounted = mount("auto");
    mounted.frame();
    expect(mounted.readout()).toBe("active");

    setWindowFocus(false);
    mounted.frame();
    expect(mounted.readout()).toBe("inactive");

    mounted.setActivation("active");
    mounted.frame();
    expect(mounted.readout()).toBe("active");
  });
});
