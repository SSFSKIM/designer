/**
 * `GlassRoot`'s three material props reaching the runtime (W29 G4).
 *
 * Before this wave the binding surfaced none of them, so a React app could not
 * select a reference material at all — `materialProfile` was an unstated
 * omission and `cssTierMapping` a deliberate one, and neither rationale survived
 * a release where "which macOS this page draws" became a choice.
 *
 * The bindings own no material of their own, so what is asserted here is the
 * same thing `color-scheme.test.tsx` asserts about the scheme: that each prop
 * arrives, that the default is the macOS 27 document, that withdrawing a tuning
 * takes it back off the live root, and that none of it rebuilds the root —
 * rebuilding for a material change would drop every registration in the tree.
 * What the material then looks like is platform-web's and calibration's.
 */

import { render } from "@testing-library/react";
import { act, useState, type ReactNode } from "react";
import { describe, expect, it } from "vitest";

import {
  macos26MaterialProfileDocument,
  macos27MaterialProfileDocument,
  type GlassRoot as PlatformGlassRoot,
  type RendererMaterialProfile,
} from "@vitreajs/vitrea-web";

import { GlassGroup, GlassRoot, GlassSurface, useGlassRoot } from "../src/index";

/** The material this root resolved, off the frame's own render input. */
const tintAlphaOf = (root: PlatformGlassRoot): number => {
  const node = root.renderInput()?.planes.flatMap((plane) => plane.nodes)[0];
  if (node === undefined) throw new Error("the frame resolved no node to read a material off");
  return node.optics.tintAlpha;
};

interface Mounted {
  root(): PlatformGlassRoot;
  frame(): void;
  tune(patch: RendererMaterialProfile | undefined): void;
}

/**
 * One root whose tuning is React state, so a change is an ordinary re-render
 * rather than a remount — which is the case worth testing.
 */
function mount(props: Parameters<typeof GlassRoot>[0]): Mounted {
  let held: PlatformGlassRoot | null = null;
  let change: ((patch: RendererMaterialProfile | undefined) => void) | undefined;

  function Capture(): ReactNode {
    held = useGlassRoot();
    return null;
  }

  function Switcher(): ReactNode {
    const [patch, setPatch] = useState<RendererMaterialProfile | undefined>(
      props.materialProfile,
    );
    change = setPatch;
    return (
      <GlassRoot
        autoStart={false}
        {...props}
        {...(patch === undefined ? {} : { materialProfile: patch })}
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
    frame: () => {
      act(() => {
        root().runFrame(0);
      });
    },
    tune: (patch) => {
      act(() => {
        change?.(patch);
      });
    },
  };
}

describe("GlassRoot's material props", () => {
  it("draws the macOS 27 document when no document is named", () => {
    const mounted = mount({});
    expect(mounted.root().material.name).toBe(macos27MaterialProfileDocument.name);
    expect(mounted.root().material.platform).toBe("macOS 27.0");
    expect(mounted.root().material.tuned).toBe(false);
  });

  it("selects the macOS 26.5 document when one is named", () => {
    const mounted = mount({ materialProfileDocument: macos26MaterialProfileDocument });
    expect(mounted.root().material.platform).toBe("macOS 26.5");
    expect(mounted.root().material.profileKey).toBe("apple-macos-26.5-1x-light-standard");
  });

  it("names the document per scheme, because a document holds one endpoint per scheme", () => {
    const mounted = mount({ colorScheme: "dark" });
    expect(mounted.root().material.profileKey)
      .toBe("apple-macos-27.0-1x-dark-standard-glass0.5");
  });

  it("carries a tuning at construction and says the material is tuned", () => {
    // Read as a DIFFERENCE from the untuned root rather than against the literal:
    // `optics.tintAlpha` on a render input is the profile's alpha after the size
    // law and the accessibility fold, so the number on the node is not the number
    // in the patch and never was.
    const plain = mount({});
    plain.frame();
    const mounted = mount({ materialProfile: { optics: { regular: { tintAlpha: 0.8 } } } });
    mounted.frame();
    expect(tintAlphaOf(mounted.root())).not.toBeCloseTo(tintAlphaOf(plain.root()), 6);
    expect(mounted.root().material.tuned).toBe(true);
  });

  it("applies a tuning change to the live root, and takes it back when it is withdrawn", () => {
    const mounted = mount({});
    mounted.frame();
    const untuned = tintAlphaOf(mounted.root());
    const before = mounted.root();

    mounted.tune({ optics: { regular: { tintAlpha: 0.8 } } });
    mounted.frame();
    expect(tintAlphaOf(mounted.root())).not.toBeCloseTo(untuned, 6);

    mounted.tune(undefined);
    mounted.frame();
    expect(tintAlphaOf(mounted.root())).toBeCloseTo(untuned, 6);

    // The same root throughout: a material change must not rebuild the runtime.
    expect(mounted.root()).toBe(before);
  });

  it("hands the CSS crossing over as well, for an app naming a whole material by hand", () => {
    const mounted = mount({ cssTierMapping: { blurSigmaScale: 3 } });
    // Readable only as "the root was told": the mapping has no readout of its
    // own, and the tier that renders through it is not the one jsdom can show.
    // What is asserted is the honest half — that naming it marks the material
    // tuned, so a capture cannot quote a document digest as if nothing moved.
    expect(mounted.root().material.tuned).toBe(true);
  });
});
