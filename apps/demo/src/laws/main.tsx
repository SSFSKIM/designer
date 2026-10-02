/**
 * The material-laws page's entry.
 *
 * `GlassRoot` is constructed here for the same reason the site's is: the renderer
 * and the accessibility overrides are construction props, so they are wired once,
 * above the page, and the page asks for changes rather than applying them.
 *
 * Three things are read from the URL, and all three are read once. `?renderer=css|webgpu`
 * picks the tier the root asks for (asking is not getting; the readouts say what
 * it got). `?rung=approximate` opens the page with reduce-transparency overridden
 * on, which is how the lens section reaches the `approximate` rung on a fresh
 * root when the visitor arrives from the CSS tier: the override is a construction
 * prop, so it has to be there before the first frame. And `?glass=0.25` builds the
 * root with the macOS 27 document at that glass position rather than the default
 * 0.5 (`../glass-document.tsx`; W43 G3 (iii), claims §5.201): `law.ts` names the
 * same document, so the readouts evaluate the material the root draws.
 */

import {
  GlassRoot,
  type AccessibilityOverride,
  type GlassWindowActivation,
} from "@vitreajs/vitrea-react";
import { StrictMode, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import "../tokens.css";
import "../site/site.css";
import "./laws.css";
import { LAWS_DOCUMENT } from "./law";
import { Laws } from "./Laws";

const params = new URLSearchParams(window.location.search);

const REQUESTED_RENDERER: "css" | "webgpu" = params.get("renderer") === "css" ? "css" : "webgpu";

const INITIAL_REDUCED_TRANSPARENCY: AccessibilityOverride =
  params.get("rung") === "approximate" ? true : "system";

function LawsRoot(): ReactNode {
  const [reducedTransparency, setReducedTransparency] = useState<AccessibilityOverride>(
    INITIAL_REDUCED_TRANSPARENCY,
  );
  /*
   * The window pose, held here because it is a root property: the shadow section
   * asks for a change and this is where it is applied, the same shape the
   * reduce-transparency override already has. It starts at `"auto"` so the page
   * follows the real window until a reader pins it, which is what the shadow
   * section's own control says it does.
   */
  const [windowActivation, setWindowActivation] = useState<GlassWindowActivation>("auto");

  return (
    <GlassRoot
      renderer={REQUESTED_RENDERER}
      materialProfileDocument={LAWS_DOCUMENT}
      reducedTransparency={reducedTransparency}
      windowActivation={windowActivation}
    >
      <Laws
        requestedRenderer={REQUESTED_RENDERER}
        reducedTransparency={reducedTransparency}
        onReducedTransparencyChange={setReducedTransparency}
        windowActivation={windowActivation}
        onWindowActivationChange={setWindowActivation}
      />
    </GlassRoot>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The laws page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <LawsRoot />
  </StrictMode>,
);
