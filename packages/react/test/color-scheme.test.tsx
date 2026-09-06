/**
 * `GlassRoot`'s `colorScheme` prop reaching the runtime (W21 G3).
 *
 * The bindings own no material of their own: the prop is handed to
 * `createGlassRoot` and then to `setColorScheme`, and the runtime resolves it.
 * So what is asserted here is that it arrives — at construction, on a change,
 * and through the media query under `"auto"` — and that a change does NOT
 * rebuild the root, because rebuilding it for a theme toggle would drop every
 * registration in the tree.
 *
 * What the material then looks like is platform-web's
 * (`test/color-scheme.test.ts` for the resolution, `e2e/` for the pixels).
 */

import { render } from "@testing-library/react";
import { act, useState, type ReactNode } from "react";
import { describe, expect, it } from "vitest";

import { COLOR_SCHEME_MEDIA_QUERY } from "@vitreajs/vitrea-web";
import type { GlassRoot as PlatformGlassRoot } from "@vitreajs/vitrea-web";

import {
  GlassGroup,
  GlassRoot,
  GlassSurface,
  useGlassRoot,
  type GlassColorScheme,
} from "../src/index";
import { setMediaQuery } from "./setup";

/** The material this root resolved, off the frame's own render input. */
const tintAlphaOf = (root: PlatformGlassRoot): number => {
  const node = root.renderInput()?.planes.flatMap((plane) => plane.nodes)[0];
  if (node === undefined) throw new Error("the frame resolved no node to read a material off");
  return node.optics.tintAlpha;
};

interface Mounted {
  root(): PlatformGlassRoot;
  frame(): void;
  /** Re-render with a different scheme, under the SAME root. */
  setScheme(scheme: GlassColorScheme): void;
}

/**
 * One root whose scheme is React state, so a change is an ordinary re-render
 * rather than a remount — which is the case worth testing.
 */
function mount(initial: GlassColorScheme | undefined): Mounted {
  let held: PlatformGlassRoot | null = null;
  let change: ((scheme: GlassColorScheme) => void) | undefined;

  function Capture(): ReactNode {
    held = useGlassRoot();
    return null;
  }

  function Switcher(): ReactNode {
    const [scheme, setScheme] = useState<GlassColorScheme | undefined>(initial);
    change = setScheme;
    return (
      <GlassRoot autoStart={false} {...(scheme === undefined ? {} : { colorScheme: scheme })}>
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
    frame: () => {
      act(() => {
        root().runFrame(0);
      });
    },
    setScheme: (scheme) => {
      act(() => {
        change?.(scheme);
      });
    },
  };
}

describe("GlassRoot's colorScheme prop", () => {
  it("defaults to light", () => {
    const mounted = mount(undefined);
    mounted.frame();
    expect(mounted.root().colorScheme).toBe("light");
  });

  it("reaches the runtime at construction", () => {
    const mounted = mount("dark");
    mounted.frame();
    expect(mounted.root().colorScheme).toBe("dark");

    const light = mount("light");
    light.frame();
    expect(tintAlphaOf(mounted.root())).not.toBe(tintAlphaOf(light.root()));
  });

  it("reaches the live root on a change, without rebuilding it", () => {
    const mounted = mount("light");
    mounted.frame();
    const before = mounted.root();
    const asLight = tintAlphaOf(before);

    mounted.setScheme("dark");
    mounted.frame();

    expect(mounted.root()).toBe(before);
    expect(mounted.root().colorScheme).toBe("dark");
    expect(tintAlphaOf(mounted.root())).not.toBe(asLight);
  });

  it("follows prefers-color-scheme under auto", () => {
    const mounted = mount("auto");
    mounted.frame();
    expect(mounted.root().colorScheme).toBe("light");
    const asLight = tintAlphaOf(mounted.root());

    act(() => {
      setMediaQuery(COLOR_SCHEME_MEDIA_QUERY, true);
    });
    mounted.frame();

    expect(mounted.root().colorScheme).toBe("dark");
    expect(tintAlphaOf(mounted.root())).not.toBe(asLight);
  });
});
