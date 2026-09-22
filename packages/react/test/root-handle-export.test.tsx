/**
 * `useGlassRootHandle` on the published surface (W32 Decision Log 5, ruled by the
 * user at G2's close; claims §5.169 §10).
 *
 * The README has told applications to `import { useGlassRootHandle } from
 * "@vitreajs/vitrea-react"` since 0.20.0, and until 0.22.0 the package exported
 * the `GlassRootHandle` TYPE and `useGlassRoot` — which returns the `GlassRoot`,
 * not the handle — so that import threw in two published READMEs. It was found
 * by building the demo's `/laws/` stage against the package rather than by
 * reading about it, which is why the assertion here is made through the
 * package's own entry point (`../src/index`) and not through `../src/context`:
 * the hook has always worked, and what was missing was the line that makes it
 * reachable.
 *
 * Three things are asserted, one per reason the export exists.
 *
 * 1. **It resolves from the entry point**, as a function. A re-export that goes
 *    missing again is a build-time symbol and not a type error anywhere in this
 *    workspace, because every internal consumer imports from `./context`.
 * 2. **It returns the handle whose `materialProfileDocument` is the document the
 *    ROOT selected**, which is the capability the paragraph promises and the one
 *    `GlassToolbar` derives its gap from. Asserted on a root built with the
 *    non-default document, so a test that read the package default would pass
 *    against the wrong thing.
 * 3. **It throws outside `<GlassRoot>`**, with the message that says why. A hook
 *    that returned `undefined` there would hand a layout a material-shaped hole
 *    on the render where it most needs a number.
 *
 * What is deliberately NOT asserted: that the document is what DREW. It is the
 * selection — the runtime reads it once at construction — and the endpoint that
 * actually drew is `GlassGroupState.materialDocument`, which needs a frame. That
 * distinction is the wave's Deferred item 20 and is documented on the export.
 */

import { render } from "@testing-library/react";
import type { ReactNode } from "react";
import { describe, expect, it } from "vitest";

import {
  macos26MaterialProfileDocument,
  macos27MaterialProfileDocument,
  type GlassMaterialProfileDocument,
} from "@vitreajs/vitrea-web";

import { GlassRoot, useGlassRootHandle, type GlassRootHandle } from "../src/index";

/** Read the handle out of a render, so each case can assert on it directly. */
function capture(document?: GlassMaterialProfileDocument): GlassRootHandle {
  let held: GlassRootHandle | undefined;

  function Capture(): ReactNode {
    held = useGlassRootHandle();
    return null;
  }

  render(
    <GlassRoot
      autoStart={false}
      {...(document === undefined ? {} : { materialProfileDocument: document })}
    >
      <Capture />
    </GlassRoot>,
  );

  if (held === undefined) throw new Error("the handle was never read");
  return held;
}

describe("useGlassRootHandle is exported (W32 Decision Log 5)", () => {
  it("resolves from the package entry point", () => {
    expect(typeof useGlassRootHandle).toBe("function");
  });

  it("returns the handle, whose materialProfileDocument is the document the root selected", () => {
    const handle = capture(macos26MaterialProfileDocument);
    expect(handle.materialProfileDocument).toBe(macos26MaterialProfileDocument);
    expect(handle.materialProfileDocument.platform).toBe("macOS 26.5");
  });

  it("names the package default when the root names no document", () => {
    expect(capture().materialProfileDocument).toBe(macos27MaterialProfileDocument);
  });

  it("carries the document on the FIRST render, before the mount effect has a runtime", () => {
    // The whole reason the document sits beside `root` rather than on it
    // (W30 Decision Log 1 (f)): a layout that must produce a number before the
    // runtime exists still gets its own material rather than the default.
    let first: { root: unknown; document: GlassMaterialProfileDocument } | undefined;

    function Capture(): ReactNode {
      const handle = useGlassRootHandle();
      first ??= { root: handle.root, document: handle.materialProfileDocument };
      return null;
    }

    render(
      <GlassRoot autoStart={false} materialProfileDocument={macos26MaterialProfileDocument}>
        <Capture />
      </GlassRoot>,
    );

    expect(first?.root).toBeNull();
    expect(first?.document).toBe(macos26MaterialProfileDocument);
  });

  it("throws outside a <GlassRoot>, rather than returning a hole", () => {
    function Orphan(): ReactNode {
      useGlassRootHandle();
      return null;
    }

    expect(() => render(<Orphan />)).toThrowError(/must be rendered inside a <GlassRoot>/);
  });
});
