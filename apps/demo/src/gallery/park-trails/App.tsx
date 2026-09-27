/**
 * Park trails: the page as three layers, in paint order.
 *
 *   1. the plane    a viewport-fixed canvas painting the photograph (ParkPlane)
 *   2. the sheet    a viewport-fixed scroller whose content, paper included, is masked away across
 *                   the planner's band: the scroll edge (below)
 *   3. the glass    the runtime's own fixed planes, a sibling of both, carrying the planner
 *
 * The scroller is its own element rather than the document so that the scroll edge can be a mask
 * on the scrolling content's own box, fixed to the viewport while the content moves under it,
 * without touching any ancestor of the glass root (SKILL.md, layout under floating chrome). Its
 * stops are derived from the planner's measured box and follow it when it changes.
 */

import { GlassRoot, useGlassRootHandle } from "@vitreajs/vitrea-react";
import { useCallback, useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";

import { DEFAULT_TRAIL_ID, trailById } from "./data";
import { buildSheetField } from "./paper";
import { ParkPlane } from "./ParkPlane";
import { planeState } from "./plane";
import { Planner } from "./Planner";
import { Sheet } from "./Sheet";

const RT_STORAGE_KEY = "park-trails.reduce-transparency";

/**
 * The app's own reduce-transparency setting (SKILL.md, accessibility): the stored choice if the
 * reader made one, else the system's answer where the engine can give it, else off. Always a
 * boolean, so the root never has to fall back to `"system"` on an engine that cannot say.
 */
function initialReduceTransparency(): boolean {
  const stored = window.localStorage.getItem(RT_STORAGE_KEY);
  if (stored === "on") return true;
  if (stored === "off") return false;
  const query = window.matchMedia("(prefers-reduced-transparency: reduce)");
  return query.media !== "not all" && query.matches;
}

function requestedRenderer(): "webgpu" | "css" {
  return new URLSearchParams(window.location.search).get("renderer") === "css" ? "css" : "webgpu";
}

export function App(props: { readonly glassContainer: HTMLElement }): ReactNode {
  const [reduceTransparency, setReduceTransparency] = useState(initialReduceTransparency);
  const [renderer] = useState(requestedRenderer);

  const chooseReduceTransparency = useCallback((on: boolean) => {
    window.localStorage.setItem(RT_STORAGE_KEY, on ? "on" : "off");
    setReduceTransparency(on);
  }, []);

  return (
    <GlassRoot
      renderer={renderer}
      colorScheme="auto"
      reducedTransparency={reduceTransparency}
      container={props.glassContainer}
    >
      <Page reduceTransparency={reduceTransparency} onReduceTransparency={chooseReduceTransparency} />
    </GlassRoot>
  );
}

/** How far below the planner's box the sheet starts to show, and over how long it fades in. */
function scrollEdgeFor(bar: DOMRect): { start: number; end: number } {
  // The band clears the capsule's own shadow, which falls about a third of the capsule's height
  // below it at this span, and then fades over one capsule height.
  const start = bar.bottom + Math.round(bar.height / 3);
  return { start, end: start + Math.round(bar.height) };
}

function Page(props: {
  readonly reduceTransparency: boolean;
  readonly onReduceTransparency: (on: boolean) => void;
}): ReactNode {
  const { root } = useGlassRootHandle();
  const [trailId, setTrailId] = useState(DEFAULT_TRAIL_ID);
  const [routeOpen, setRouteOpen] = useState(false);
  const trail = trailById(trailId);

  const scrollerRef = useRef<HTMLDivElement>(null);
  const sheetRef = useRef<HTMLElement>(null);
  const trailsRef = useRef<HTMLElement>(null);
  const conditionsRef = useRef<HTMLElement>(null);
  const forecastRef = useRef<HTMLTableElement>(null);
  const permitsRef = useRef<HTMLElement>(null);

  // The window handles the audit reads (vitrea.md §7).
  const setReducedTransparency = useRef(props.onReduceTransparency);
  setReducedTransparency.current = props.onReduceTransparency;
  useEffect(() => {
    if (root === null) return;
    Object.assign(window, {
      __vitrea: root,
      __glassDemo: {
        openMenu: () => setRouteOpen(true),
        setReducedTransparency: (on: boolean) => setReducedTransparency.current(on),
      },
    });
  }, [root]);

  /*
   * What the measurement needs to know about the sheet: where its top edge is in the viewport,
   * what it displays (paper.ts, rebuilt when it changes), and where the scroll edge's stops are.
   */
  const syncSheet = useCallback(() => {
    const scroller = scrollerRef.current;
    const sheet = sheetRef.current;
    if (scroller === null || sheet === null) return;
    planeState.sheetTop = sheet.offsetTop - scroller.scrollTop;
  }, []);

  useLayoutEffect(() => {
    const scroller = scrollerRef.current;
    const sheet = sheetRef.current;
    if (scroller === null || sheet === null) return;

    /*
     * The sheet's displayed field is rebuilt, a frame later and once however many changes land in
     * that frame, whenever what it shows can have changed: its DOM (a route chosen re-marks rows,
     * the bulletin and the steps), its size, the scheme, and the fonts arriving.
     */
    let rebuild = 0;
    const readSheet = (): void => {
      cancelAnimationFrame(rebuild);
      rebuild = requestAnimationFrame(() => {
        planeState.sheet = buildSheetField(sheet);
      });
    };

    let bar: Element | null = null;
    const placeEdge = (): void => {
      bar ??= document.getElementById("pt-planner");
      if (bar === null) return;
      const { start, end } = scrollEdgeFor(bar.getBoundingClientRect());
      planeState.fadeStart = start;
      planeState.fadeEnd = end;
      scroller.style.setProperty("--pt-fade-start", `${String(start)}px`);
      scroller.style.setProperty("--pt-fade-end", `${String(end)}px`);
    };

    readSheet();
    syncSheet();
    placeEdge();

    const scheme = window.matchMedia("(prefers-color-scheme: dark)");
    scheme.addEventListener("change", readSheet);
    void document.fonts.ready.then(readSheet);
    const mutations = new MutationObserver(readSheet);
    mutations.observe(sheet, {
      subtree: true,
      childList: true,
      characterData: true,
      attributes: true,
    });
    scroller.addEventListener("scroll", syncSheet, { passive: true });
    const resize = new ResizeObserver(() => {
      syncSheet();
      placeEdge();
      readSheet();
    });
    resize.observe(sheet);
    resize.observe(scroller);
    // The planner mounts through a portal a commit after the root exists; watch for it.
    const watch = window.setInterval(() => {
      const found = document.getElementById("pt-planner");
      if (found === null) return;
      window.clearInterval(watch);
      bar = found;
      resize.observe(found);
      placeEdge();
    }, 50);

    return () => {
      cancelAnimationFrame(rebuild);
      scheme.removeEventListener("change", readSheet);
      mutations.disconnect();
      scroller.removeEventListener("scroll", syncSheet);
      resize.disconnect();
      window.clearInterval(watch);
    };
  }, [syncSheet]);

  /*
   * The scroller is the page's scroll, so keyboard scrolling that would have gone to the document
   * goes to it while nothing else holds focus.
   */
  useEffect(() => {
    const scroller = scrollerRef.current;
    if (scroller === null) return;
    const onKeyDown = (event: KeyboardEvent): void => {
      const target = event.target;
      if (target !== document.body && target !== document.documentElement) return;
      const page = scroller.clientHeight - (planeState.fadeEnd + 24);
      const by: Record<string, number> = {
        ArrowDown: 48,
        ArrowUp: -48,
        PageDown: page,
        PageUp: -page,
        " ": event.shiftKey ? -page : page,
      };
      if (event.key === "Home") scroller.scrollTo({ top: 0 });
      else if (event.key === "End") scroller.scrollTo({ top: scroller.scrollHeight });
      else {
        const step = by[event.key];
        if (step === undefined) return;
        scroller.scrollBy({ top: step });
      }
      event.preventDefault();
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  /*
   * The planner's two navigations. The heading that names the destination lands one gutter below
   * the scroll edge (the scroller's own scroll-padding, derived from the planner's box), and the
   * destination takes focus, which is where it stays: a navigation is not a dismissal.
   */
  const reveal = useCallback((target: HTMLElement | null) => {
    if (target === null) return;
    const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const named = target.getAttribute("aria-labelledby");
    const heading = (named === null ? null : document.getElementById(named)) ?? target;
    heading.scrollIntoView({ behavior: reduced ? "auto" : "smooth", block: "start" });
    target.focus({ preventScroll: true });
  }, []);

  const chooseRoute = useCallback((id: string) => setTrailId(id), []);

  return (
    <>
      <ParkPlane onPainted={syncSheet} />
      <div ref={scrollerRef} className="pt-scroller">
        <div className="pt-view" aria-hidden="true" />
        <main>
          <Sheet
            trail={trail}
            onChooseRoute={chooseRoute}
            reduceTransparency={props.reduceTransparency}
            onReduceTransparency={props.onReduceTransparency}
            sheetRef={sheetRef}
            trailsRef={trailsRef}
            conditionsRef={conditionsRef}
            forecastRef={forecastRef}
            permitsRef={permitsRef}
          />
        </main>
      </div>
      <Planner
        trail={trail}
        routeOpen={routeOpen}
        onRouteOpenChange={setRouteOpen}
        onChooseRoute={chooseRoute}
        onForecast={() => reveal(forecastRef.current)}
        onPermits={() => reveal(permitsRef.current)}
      />
    </>
  );
}
