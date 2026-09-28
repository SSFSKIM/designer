/**
 * Tonight — a planetarium display in the materialist skill's spatial register, the gallery's
 * flagship page.
 *
 * The record this page was built against, and what building it changed, is `DESIGN.md` beside
 * this file. The root is mounted here with the page's one tuning over the shipped material
 * (`shared.ts`, `MATERIAL_TUNE`) and the page's own Reduce Transparency setting, which the Place
 * platter changes and the root always receives as a boolean.
 */

import "./planetarium.css";

import { GlassRoot } from "@vitreajs/vitrea-react";
import { StrictMode, useCallback, useEffect, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./app";
import { CLEAR_BLUR_SIGMA, CLEAR_TINT_ALPHA, CLEAR_TONE_STRENGTH, MATERIAL_TUNE, tuneWith } from "./shared";

const params = new URLSearchParams(location.search);
const renderer = params.get("tier") === "css" ? "css" : "webgpu";
/** Capture aids: `?sigma=<n>` and `?alpha=<n>` draw the page with another clear base σ or tint alpha, for the record's sweep. */
const sigmaParam = params.get("sigma");
const alphaParam = params.get("alpha");
const toneParam = params.get("tone");
const tune =
  sigmaParam === null && alphaParam === null && toneParam === null
    ? MATERIAL_TUNE
    : tuneWith(
        sigmaParam === null ? CLEAR_BLUR_SIGMA : Math.max(0.05, Number(sigmaParam)),
        alphaParam === null ? CLEAR_TINT_ALPHA : Math.max(0, Number(alphaParam)),
        toneParam === null ? CLEAR_TONE_STRENGTH : Math.max(0, Math.min(1, Number(toneParam))),
      );

// The glass root mounts inside the page's <main>, so every window, module and ornament — which the
// runtime portals into its planes — sits inside the main landmark, after the page's heading.
const main = document.createElement("main");
main.id = "tonight";
const heading = document.createElement("h1");
heading.className = "visually-hidden";
heading.textContent = "Tonight";
main.append(heading);
document.body.append(main);

const RT_KEY = "tonight.reduceTransparency";
const rtQuery = window.matchMedia("(prefers-reduced-transparency: reduce)");

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
      materialProfile={tune}
      reducedTransparency={reducedTransparency}
      container={main}
    >
      <App reducedTransparency={reducedTransparency} onReducedTransparency={change} />
    </GlassRoot>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The planetarium page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <Shell />
  </StrictMode>,
);
