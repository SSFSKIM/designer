/**
 * Daybreak — a browser start page in the materialist skill's spatial register.
 *
 * The record this page was built against, and what building it changed, is `DESIGN.md` beside
 * this file. The root is mounted here with the page's own Reduce Transparency setting, which the
 * Photograph platter changes and the root always receives as a boolean.
 */

import "./start-page.css";

import { GlassRoot } from "@vitreajs/vitrea-react";
import { StrictMode, useCallback, useEffect, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./app";

const renderer = new URLSearchParams(location.search).get("tier") === "css" ? "css" : "webgpu";

/*
 * The glass root mounts inside the page's <main>, so every window, module and ornament — which
 * the runtime portals into its planes — sits inside the main landmark, after the page's heading.
 */
const main = document.createElement("main");
main.id = "daybreak";
const heading = document.createElement("h1");
heading.className = "visually-hidden";
heading.textContent = "Daybreak";
main.append(heading);
document.body.append(main);

const RT_KEY = "daybreak.reduceTransparency";
const rtQuery = window.matchMedia("(prefers-reduced-transparency: reduce)");

/**
 * The person's answer if they gave one on this page; otherwise the system's, where the engine
 * can answer the query at all (an engine that cannot parses it as `not all` and says false).
 */
function readStored(): boolean | undefined {
  try {
    const stored = localStorage.getItem(RT_KEY);
    return stored === null ? undefined : stored === "true";
  } catch {
    return undefined;
  }
}

function Shell(): ReactNode {
  const [stored, setStored] = useState<boolean | undefined>(readStored);
  const [system, setSystem] = useState(rtQuery.matches);
  useEffect(() => {
    const onChange = (): void => setSystem(rtQuery.matches);
    rtQuery.addEventListener("change", onChange);
    return () => rtQuery.removeEventListener("change", onChange);
  }, []);
  const reducedTransparency = stored ?? system;
  const change = useCallback((value: boolean) => {
    setStored(value);
    try {
      localStorage.setItem(RT_KEY, String(value));
    } catch {
      // Holds for this visit.
    }
  }, []);

  return (
    <GlassRoot
      renderer={renderer}
      colorScheme="auto"
      windowActivation="auto"
      reducedTransparency={reducedTransparency}
      container={main}
    >
      <App reducedTransparency={reducedTransparency} onReducedTransparency={change} />
    </GlassRoot>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The start-page page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <Shell />
  </StrictMode>,
);
