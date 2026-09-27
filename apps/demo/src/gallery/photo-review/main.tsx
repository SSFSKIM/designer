/**
 * Photo review: a culling and adjustment tool over one photograph, a Liquid Glass demo on
 * vitrea 0.24.0 built under the materialist skill. The record is `DESIGN.md` beside this file.
 *
 * The root asks for the GPU tier unless the URL says `?renderer=css` (the site's convention),
 * follows the system's colour scheme and the window's focus, and takes reduce transparency as
 * a boolean from the app's own setting: `prefers-reduced-transparency` is not answered by every
 * engine, and a boolean is the only way to honour it where it is not.
 */
import { GlassRoot } from "@vitreajs/vitrea-react";
import { StrictMode, useCallback, useEffect, useState } from "react";
import { createRoot } from "react-dom/client";

import { App } from "./App";
import "./styles.css";

const RENDERER = new URLSearchParams(window.location.search).get("renderer") === "css" ? "css" : "webgpu";

const STORAGE_KEY = "vitrea-demo:photo-review:reduce-transparency";
const SYSTEM = window.matchMedia("(prefers-reduced-transparency: reduce)");
/** An engine that does not know the feature parses the query as `not all`. */
const ANSWERED = SYSTEM.media !== "not all";

function stored(): boolean | null {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    return value === "true" ? true : value === "false" ? false : null;
  } catch {
    return null;
  }
}

/**
 * The app's reduce-transparency setting: a stored choice if the reader made one, else the
 * system's answer where the engine gives one, else off. It follows the system until the reader
 * chooses, and is always a boolean by the time it reaches the root.
 */
function useReduceTransparency(): [boolean, (on: boolean) => void] {
  const [on, setOn] = useState<boolean>(() => stored() ?? (ANSWERED ? SYSTEM.matches : false));
  useEffect(() => {
    if (!ANSWERED) return;
    const onChange = () => {
      if (stored() === null) setOn(SYSTEM.matches);
    };
    SYSTEM.addEventListener("change", onChange);
    return () => SYSTEM.removeEventListener("change", onChange);
  }, []);
  const set = useCallback((next: boolean) => {
    try {
      window.localStorage.setItem(STORAGE_KEY, String(next));
    } catch {
      // A private window without storage still gets the setting for this visit.
    }
    setOn(next);
  }, []);
  return [on, set];
}

function Page() {
  const [reduceTransparency, setReduceTransparency] = useReduceTransparency();
  return (
    <GlassRoot renderer={RENDERER} colorScheme="auto" reducedTransparency={reduceTransparency}>
      <App reduceTransparency={reduceTransparency} onReduceTransparency={setReduceTransparency} />
    </GlassRoot>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The photo-review page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <Page />
  </StrictMode>,
);
