/**
 * Entry. `GlassRoot` is built here because the renderer and the accessibility
 * overrides are its construction props: the tier is wired once per page load
 * (`?renderer=css` forces the CSS tier; the default asks for WebGPU and reports
 * honestly if it does not get it), and the overrides have to reach the root.
 */

import { GlassRoot } from "@vitreajs/vitrea-react";
import { StrictMode, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import type { Overrides } from "./sheets/RenderingSheet";
import "./styles/tokens.css";
import "./styles/app.css";

const REQUESTED_RENDERER: "css" | "webgpu" =
  new URLSearchParams(window.location.search).get("renderer") === "css" ? "css" : "webgpu";

function Root(): ReactNode {
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
      <App
        requestedRenderer={REQUESTED_RENDERER}
        overrides={overrides}
        onOverridesChange={setOverrides}
      />
    </GlassRoot>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("No #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <Root />
  </StrictMode>,
);
