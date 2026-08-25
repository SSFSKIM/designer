/**
 * The public site's entry.
 *
 * `GlassRoot` is constructed here rather than inside `Site` because the renderer
 * and the accessibility overrides are its construction props: the tier is wired
 * once, and the overrides have to reach the root rather than be applied to it
 * afterwards.
 */

import { GlassRoot } from "@vitreajs/vitrea-react";
import { StrictMode, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import "../tokens.css";
import "./site.css";
import { Site, type Overrides } from "./Site";

/**
 * Which tier to ask for, from `?renderer=css|webgpu`. Defaults to the GPU tier.
 *
 * Asking is not getting: where there is no adapter, no device or no renderer chunk,
 * every group resolves to the CSS tier and the readouts name the reason. That is
 * what makes asking for the GPU tier by default safe to ship, and it is the thing
 * the page is trying to show. Read once at module scope, because a root wires its
 * renderer at construction, so changing it means a reload.
 */
const REQUESTED_RENDERER: "css" | "webgpu" =
  new URLSearchParams(window.location.search).get("renderer") === "css" ? "css" : "webgpu";

function SiteRoot(): ReactNode {
  const [overrides, setOverrides] = useState<Overrides>({
    reducedMotion: "system",
    reducedTransparency: "system",
    increasedContrast: "system",
  });

  return (
    <GlassRoot
      renderer={REQUESTED_RENDERER}
      reducedMotion={overrides.reducedMotion}
      reducedTransparency={overrides.reducedTransparency}
      increasedContrast={overrides.increasedContrast}
    >
      <Site
        requestedRenderer={REQUESTED_RENDERER}
        overrides={overrides}
        onOverridesChange={setOverrides}
      />
    </GlassRoot>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The site has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <SiteRoot />
  </StrictMode>,
);
