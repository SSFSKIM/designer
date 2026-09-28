/**
 * Chronograph — vitrea's flagship: a rattrapante on a watchmaker's bench, under optical glass.
 *
 * The record this page was built against is `DESIGN.md` beside this file. The root is mounted
 * here because three of the person's choices are root options: the dial (which is the colour
 * scheme the glass is made of), the crystal (which is whether the page's optical tuning applies),
 * and the page's own Reduce Transparency setting, which the root always receives as a boolean.
 */

import "./chronograph.css";

import { GlassRoot } from "@vitreajs/vitrea-react";
import { StrictMode, useCallback, useEffect, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./app";
import type { CrystalId } from "./layout";
import type { Scheme } from "./palette";
import { crystalById, OPTICAL_PROFILE } from "./shared";

const params = new URLSearchParams(location.search);
const renderer = params.get("tier") === "css" ? "css" : "webgpu";

/*
 * The root mounts inside <main>, so every glass host the runtime portals into its planes sits
 * inside the main landmark, after the page's heading.
 */
const main = document.createElement("main");
main.id = "chronograph";
const heading = document.createElement("h1");
heading.className = "visually-hidden";
heading.textContent = "Vitrea chronograph";
main.append(heading);
document.body.append(main);

const darkQuery = window.matchMedia("(prefers-color-scheme: dark)");
const rtQuery = window.matchMedia("(prefers-reduced-transparency: reduce)");
const RT_KEY = "chronograph.reduceTransparency";

function readStored(): boolean | undefined {
  try {
    const stored = localStorage.getItem(RT_KEY);
    return stored === null ? undefined : stored === "true";
  } catch {
    return undefined;
  }
}

const initialCrystal = (): CrystalId => {
  const asked = params.get("crystal");
  return asked === "flat" || asked === "box" || asked === "apple" ? asked : "domed";
};

const initialScheme = (): Scheme => {
  const asked = params.get("dial");
  if (asked === "day") return "light";
  if (asked === "night") return "dark";
  return darkQuery.matches ? "dark" : "light";
};

function Shell(): ReactNode {
  const [scheme, setScheme] = useState<Scheme>(initialScheme);
  const [crystal, setCrystal] = useState<CrystalId>(initialCrystal);
  const [stored, setStored] = useState<boolean | undefined>(readStored);
  const [system, setSystem] = useState(rtQuery.matches);

  // The dial follows the system's appearance until the person picks one.
  const [followSystem, setFollowSystem] = useState(!params.has("dial"));
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
    document.documentElement.dataset.dial = scheme === "dark" ? "night" : "day";
  }, [scheme]);

  return (
    <GlassRoot
      renderer={renderer}
      colorScheme={scheme}
      windowActivation="auto"
      materialProfile={crystalById(crystal).tuned ? OPTICAL_PROFILE : undefined}
      reducedTransparency={reducedTransparency}
      container={main}
    >
      <App
        scheme={scheme}
        onScheme={chooseScheme}
        crystal={crystal}
        onCrystal={setCrystal}
        reducedTransparency={reducedTransparency}
        onReducedTransparency={changeReducedTransparency}
      />
    </GlassRoot>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The chronograph page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <Shell />
  </StrictMode>,
);
