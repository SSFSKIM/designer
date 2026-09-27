/**
 * The root: which tier the page asks for, the app's own Reduce Transparency setting, and the one
 * `GlassRoot` everything floats in.
 *
 * The site's convention: ask for the GPU tier unless the URL says `?renderer=css`. The colour
 * scheme follows the system (`auto`), and so do the page's own tokens, so both are designed
 * states. The window pose follows the document's focus: the receded material is a state of this
 * design, not something the page pins.
 *
 * Reduce Transparency is the one preference an engine may not be able to report, and the root
 * honours it there only through a boolean. So the root is always handed one: the reader's own
 * choice when they have made it (the toggle at the top right, or the switch in the colophon), and
 * otherwise the system's answer where `prefers-reduced-transparency` is supported, following it
 * live. On an engine that cannot answer, the page starts transparent and the setting is on the
 * page, which is what makes zero diagnostics mean "the engine answered, or the app did".
 */

import { GlassRoot } from "@vitreajs/vitrea-react";
import { useCallback, useEffect, useState, type ReactNode } from "react";

import { Page } from "./Page";

const REQUESTED: "webgpu" | "css" =
  new URLSearchParams(window.location.search).get("renderer") === "css" ? "css" : "webgpu";

const RT_QUERY = "(prefers-reduced-transparency: reduce)";
const RT_KEY = "vitrea-gallery:product-launch:reduce-transparency";

function readStored(): boolean | null {
  try {
    const value = window.localStorage.getItem(RT_KEY);
    return value === "on" ? true : value === "off" ? false : null;
  } catch {
    return null;
  }
}

function useReduceTransparency(): readonly [boolean, (on: boolean, persist: boolean) => void] {
  const [choice, setChoice] = useState<boolean | null>(readStored);
  const [system, setSystem] = useState(() => {
    const query = window.matchMedia(RT_QUERY);
    return query.media !== "not all" && query.matches;
  });

  useEffect(() => {
    const query = window.matchMedia(RT_QUERY);
    if (query.media === "not all") return;
    const onChange = (): void => setSystem(query.matches);
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, []);

  const set = useCallback((on: boolean, persist: boolean) => {
    setChoice(on);
    if (!persist) return;
    try {
      window.localStorage.setItem(RT_KEY, on ? "on" : "off");
    } catch {
      // A storage-less context keeps the choice for the session, which is all it can do.
    }
  }, []);

  return [choice ?? system, set] as const;
}

export function App(props: { readonly glassContainer: HTMLElement }): ReactNode {
  const [reduceTransparency, setReduceTransparency] = useReduceTransparency();
  return (
    <GlassRoot
      container={props.glassContainer}
      renderer={REQUESTED}
      colorScheme="auto"
      windowActivation="auto"
      reducedTransparency={reduceTransparency}
    >
      <Page
        requested={REQUESTED}
        reduceTransparency={reduceTransparency}
        onReduceTransparency={setReduceTransparency}
      />
    </GlassRoot>
  );
}
