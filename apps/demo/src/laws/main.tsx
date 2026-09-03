/**
 * The material-laws page's entry.
 *
 * `GlassRoot` is constructed here for the same reason the site's is: the renderer
 * and the accessibility overrides are construction props, so they are wired once,
 * above the page, and the page asks for changes rather than applying them.
 *
 * Two things are read from the URL, and both are read once. `?renderer=css|webgpu`
 * picks the tier the root asks for (asking is not getting; the readouts say what
 * it got). `?rung=approximate` opens the page with reduce-transparency overridden
 * on, which is how the lens section reaches the `approximate` rung on a fresh
 * root when the visitor arrives from the CSS tier: the override is a construction
 * prop, so it has to be there before the first frame.
 */

import { GlassRoot, type AccessibilityOverride } from "@vitreajs/vitrea-react";
import { StrictMode, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import "../tokens.css";
import "../site/site.css";
import "./laws.css";
import { Laws } from "./Laws";

const params = new URLSearchParams(window.location.search);

const REQUESTED_RENDERER: "css" | "webgpu" = params.get("renderer") === "css" ? "css" : "webgpu";

const INITIAL_REDUCED_TRANSPARENCY: AccessibilityOverride =
  params.get("rung") === "approximate" ? true : "system";

function LawsRoot(): ReactNode {
  const [reducedTransparency, setReducedTransparency] = useState<AccessibilityOverride>(
    INITIAL_REDUCED_TRANSPARENCY,
  );

  return (
    <GlassRoot renderer={REQUESTED_RENDERER} reducedTransparency={reducedTransparency}>
      <Laws
        requestedRenderer={REQUESTED_RENDERER}
        reducedTransparency={reducedTransparency}
        onReducedTransparencyChange={setReducedTransparency}
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
