/**
 * Music player: a streaming service's Mac web client, the sounding release's artwork filling the
 * window and its controls floating over it on Liquid Glass. The record of every decision is
 * `DESIGN.md` beside this file.
 *
 * This file owns the root and the app's one display setting. Reduce Transparency is offered here
 * because `prefers-reduced-transparency` is not answerable on every engine: where it is not, a
 * root left on `"system"` resolves false and says so, and the only honest way to honour the
 * preference there is to ask the listener and hand the root a boolean.
 */

import { GlassRoot } from "@vitreajs/vitrea-react";
import { StrictMode, useCallback, useState, type ReactNode } from "react";
import { createRoot } from "react-dom/client";

import { Player } from "./Player";
import "./music-player.css";

const SETTING_KEY = "vitrea-gallery.music-player.reduce-transparency";

function readSetting(): boolean {
  try {
    const stored = window.localStorage.getItem(SETTING_KEY);
    if (stored !== null) return stored === "true";
  } catch {
    // Storage can be refused (a private window, a sandbox); the system's answer stands in.
  }
  const query = window.matchMedia("(prefers-reduced-transparency: reduce)");
  // An engine that cannot parse the query reports it as "not all" and never matches.
  return query.media !== "not all" && query.matches;
}

function useReduceTransparencySetting(): readonly [boolean, (on: boolean) => void] {
  const [on, setOn] = useState(readSetting);
  const set = useCallback((next: boolean) => {
    setOn(next);
    try {
      window.localStorage.setItem(SETTING_KEY, String(next));
    } catch {
      // Not stored; the setting still holds for this session.
    }
  }, []);
  return [on, set];
}

/** The site's convention: the GPU tier unless the URL asks for the CSS tier by name. */
const renderer = new URLSearchParams(window.location.search).get("renderer") === "css" ? "css" : "webgpu";

function App(): ReactNode {
  const [reduceTransparency, setReduceTransparency] = useReduceTransparencySetting();
  return (
    <GlassRoot
      renderer={renderer}
      colorScheme="auto"
      windowActivation="auto"
      reducedTransparency={reduceTransparency}
    >
      <Player
        reduceTransparency={reduceTransparency}
        onReduceTransparency={setReduceTransparency}
      />
    </GlassRoot>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The music-player page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
