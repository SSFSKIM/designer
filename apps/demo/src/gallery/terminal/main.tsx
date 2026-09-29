/**
 * Terminal — a shell running on clear glass over Lake Tahoe, in the materialist skill's spatial
 * register.
 *
 * The record this page was built against is `DESIGN.md` beside this file. The root is mounted
 * here because three of the person's choices are root options: the appearance (the colour scheme
 * the glass is made of), the glass (whether the Clear tune applies), and the page's own Reduce
 * transparency setting, which the root always receives as a boolean.
 */

import "./terminal.css";

import { GlassRoot } from "@vitreajs/vitrea-react";
import { StrictMode, useCallback, useEffect, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./app";
import { CLEAR_BLUR_SIGMA, clearTune } from "./shared";
import type { GlassKind, Scheme } from "./shell/types";

const params = new URLSearchParams(location.search);
const renderer = params.get("tier") === "css" ? "css" : "webgpu";
/** A capture aid: `?sigma=<n>` draws Clear with another base σ, for the record's sweep. */
const sigmaParam = params.get("sigma");
const CLEAR = clearTune(sigmaParam === null ? CLEAR_BLUR_SIGMA : Math.max(0.05, Number(sigmaParam)));

// The page's React root and the glass root both mount inside the page's <main>, after its
// heading: the map, its credit and every host the runtime portals into its planes sit inside the
// main landmark, the React root first so the planes stack above the map.
const container = document.getElementById("root");
if (container === null) throw new Error("The terminal page has no #root to mount into.");
const main = document.createElement("main");
main.id = "terminal";
const heading = document.createElement("h1");
heading.className = "visually-hidden";
heading.textContent = "Terminal";
main.append(heading, container);
document.body.append(main);

const darkQuery = window.matchMedia("(prefers-color-scheme: dark)");
const rtQuery = window.matchMedia("(prefers-reduced-transparency: reduce)");
const RT_KEY = "terminal.reduceTransparency";

function readStored(): boolean | undefined {
  try {
    const stored = localStorage.getItem(RT_KEY);
    return stored === null ? undefined : stored === "true";
  } catch {
    return undefined;
  }
}

const initialGlass = (): GlassKind => (params.get("glass") === "regular" ? "regular" : "clear");
const initialScheme = (): Scheme => {
  const asked = params.get("appearance");
  if (asked === "dark" || asked === "light") return asked;
  return darkQuery.matches ? "dark" : "light";
};

function Shell(): ReactNode {
  const [glass, setGlass] = useState<GlassKind>(initialGlass);
  const [scheme, setScheme] = useState<Scheme>(initialScheme);
  const [stored, setStored] = useState<boolean | undefined>(readStored);
  const [system, setSystem] = useState(rtQuery.matches);

  // The appearance follows the system's until the person picks one.
  const [followSystem, setFollowSystem] = useState(!params.has("appearance"));
  useEffect(() => {
    const onChange = (): void => {
      if (followSystem) setScheme(darkQuery.matches ? "dark" : "light");
    };
    darkQuery.addEventListener("change", onChange);
    return () => darkQuery.removeEventListener("change", onChange);
  }, [followSystem]);
  useEffect(() => {
    const onChange = (): void => setSystem(rtQuery.matches);
    rtQuery.addEventListener("change", onChange);
    return () => rtQuery.removeEventListener("change", onChange);
  }, []);

  const reducedTransparency = stored ?? system;
  const changeReducedTransparency = useCallback((value: boolean) => {
    setStored(value);
    try {
      localStorage.setItem(RT_KEY, String(value));
    } catch {
      // Holds for this visit.
    }
  }, []);
  const chooseScheme = useCallback((value: Scheme) => {
    setFollowSystem(false);
    setScheme(value);
  }, []);

  useEffect(() => {
    document.documentElement.dataset.appearance = scheme;
  }, [scheme]);

  return (
    <GlassRoot
      renderer={renderer}
      colorScheme={scheme}
      windowActivation="auto"
      materialProfile={glass === "clear" ? CLEAR : undefined}
      reducedTransparency={reducedTransparency}
      container={main}
    >
      <App
        renderer={renderer}
        glass={glass}
        scheme={scheme}
        onGlass={setGlass}
        onScheme={chooseScheme}
        reducedTransparency={reducedTransparency}
        onReducedTransparency={changeReducedTransparency}
      />
    </GlassRoot>
  );
}

createRoot(container).render(
  <StrictMode>
    <Shell />
  </StrictMode>,
);
