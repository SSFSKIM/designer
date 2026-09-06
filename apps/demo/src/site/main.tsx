/**
 * The public site's entry.
 *
 * `GlassRoot` is constructed here rather than inside `Site` because the renderer
 * and the accessibility overrides are its construction props: the tier is wired
 * once, and the overrides have to reach the root rather than be applied to it
 * afterwards.
 */

import { GlassRoot, type GlassColorScheme } from "@vitreajs/vitrea-react";
import { StrictMode, useEffect, useState, type ReactNode } from "react";
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

/**
 * `prefers-color-scheme`, read by the page for the page's own ground.
 *
 * vitrea reads the same query for the material — that is what
 * `colorScheme="auto"` is — and this is deliberately not the same read wired
 * twice by accident. A page's background is the page's business: the runtime
 * cannot write the reader's tokens and does not try to, so every host that
 * offers "follow the system" owns this half of it. Kept next to the `GlassRoot`
 * that owns the other half, so the pairing is visible.
 */
function usePrefersDark(): boolean {
  const [prefersDark, setPrefersDark] = useState(
    () => window.matchMedia("(prefers-color-scheme: dark)").matches,
  );

  useEffect(() => {
    const query = window.matchMedia("(prefers-color-scheme: dark)");
    const listener = (): void => setPrefersDark(query.matches);
    query.addEventListener("change", listener);
    listener();
    return () => query.removeEventListener("change", listener);
  }, []);

  return prefersDark;
}

function SiteRoot(): ReactNode {
  const [overrides, setOverrides] = useState<Overrides>({
    reducedMotion: "system",
    reducedTransparency: "system",
    increasedContrast: "system",
  });
  /*
   * Light, not auto, and that is a decision rather than an omission. This page's
   * daylight ground is a measured choice (spec `2026-09-03-demo-hero-daylight`
   * Decision Log 1: on a near-black window the material collapsed honestly to
   * flat grey plates and had nothing to show), so the dark scheme is what a
   * reader asks for here rather than what a visitor's operating system decides
   * for them. `"auto"` is one option along, and it is the position an ordinary
   * application would ship in.
   */
  const [colorScheme, setColorScheme] = useState<GlassColorScheme>("light");
  const prefersDark = usePrefersDark();
  const resolved = colorScheme === "auto" ? (prefersDark ? "dark" : "light") : colorScheme;

  // The page's own tokens, switched by one attribute — see `tokens.css`.
  useEffect(() => {
    document.documentElement.dataset["colorScheme"] = resolved;
  }, [resolved]);

  return (
    <GlassRoot
      renderer={REQUESTED_RENDERER}
      colorScheme={colorScheme}
      reducedMotion={overrides.reducedMotion}
      reducedTransparency={overrides.reducedTransparency}
      increasedContrast={overrides.increasedContrast}
    >
      <Site
        requestedRenderer={REQUESTED_RENDERER}
        overrides={overrides}
        onOverridesChange={setOverrides}
        colorScheme={colorScheme}
        resolvedColorScheme={resolved}
        onColorSchemeChange={setColorScheme}
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
