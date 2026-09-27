/**
 * *Weather in Painting*: the online viewing room of a museum exhibition, in the materialist
 * skill's spatial register. The record is `DESIGN.md` beside this file.
 *
 * The root is the page's only material decision made here: the tier the URL asks for (`?tier=css`
 * looks at the CSS tier on purpose; otherwise the GPU tier is requested), the colour scheme
 * following the system, the window pose following focus, and Reduce Transparency as the page's
 * own setting, always passed as a boolean. The engine may not be able to answer
 * `prefers-reduced-transparency`; where it can, the setting starts from the system's answer and
 * follows it until the visitor chooses, and a choice is remembered.
 */

import { GlassRoot } from "@vitreajs/vitrea-react";
import { StrictMode, useCallback, useEffect, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import { Exhibition } from "./Exhibition";
import "./exhibition.css";

const STORAGE_KEY = "vitrea.exhibition.reduceTransparency";
const QUERY = "(prefers-reduced-transparency: reduce)";

/** Whether this engine can answer the query at all: one of its two values must match. */
function systemAnswers(): boolean {
  return (
    window.matchMedia(QUERY).matches ||
    window.matchMedia("(prefers-reduced-transparency: no-preference)").matches
  );
}

function storedChoice(): boolean | undefined {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY);
    return value === null ? undefined : value === "true";
  } catch {
    return undefined;
  }
}

function initialReducedTransparency(): boolean {
  return storedChoice() ?? (systemAnswers() && window.matchMedia(QUERY).matches);
}

function App(): ReactNode {
  const renderer =
    new URLSearchParams(window.location.search).get("tier") === "css" ? "css" : "webgpu";
  const [reducedTransparency, setReducedTransparency] = useState(initialReducedTransparency);

  // Follow the system until the visitor has chosen.
  useEffect(() => {
    if (!systemAnswers()) return;
    const list = window.matchMedia(QUERY);
    const update = (): void => {
      if (storedChoice() === undefined) setReducedTransparency(list.matches);
    };
    list.addEventListener("change", update);
    return () => list.removeEventListener("change", update);
  }, []);

  const choose = useCallback((value: boolean) => {
    setReducedTransparency(value);
    try {
      window.localStorage.setItem(STORAGE_KEY, String(value));
    } catch {
      // A browser that refuses storage still honours the choice for this visit.
    }
  }, []);

  return (
    <GlassRoot renderer={renderer} colorScheme="auto" reducedTransparency={reducedTransparency}>
      <Exhibition
        reducedTransparency={reducedTransparency}
        onReducedTransparency={choose}
        // The audit contract's setter is a statement for one capture, not a visitor's choice,
        // so it is not remembered.
        onAuditReducedTransparency={setReducedTransparency}
      />
    </GlassRoot>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The exhibition page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
