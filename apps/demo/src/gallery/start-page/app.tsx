/**
 * Daybreak, composed: the environment, three windows and two ornaments (`DESIGN.md`).
 *
 * This file owns the page's state and the one statement the page makes about what the glass is
 * over: each group's hint, measured from the painted environment under that group's own box
 * whenever the environment or the layout moves. Everything the runtime can read for itself it
 * is left to read.
 *
 * It also owns the post-panel comparison mode, `?glass=clear`: every group in the clear variant
 * over the same environment with the page's own dimming painted under each host. The default
 * (no parameter) is the page the panel read, and takes none of that mode's code.
 */

import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import {
  useGlassAccessibility,
  useGlassCapabilities,
  useGlassRootHandle,
  type BackdropHint,
} from "@vitreajs/vitrea-react";
import type { GlassHostHandle, GlassRoot } from "@vitreajs/vitrea-web";
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { flushSync } from "react-dom";

import {
  PHASE_IDS,
  PHOTOGRAPHS,
  PLACES,
  phaseAt,
  photographFor,
  type PhaseId,
  type Photograph,
} from "./data";
import {
  createDimmer,
  hintFrom,
  loadPhotograph,
  measureFootprint,
  paintPhotograph,
  type Box,
  type Dimmer,
  type HostShape,
  type Painted,
} from "./environment";
import { computeLayout, derivedGap } from "./layout";
import { NowModule } from "./now-module";
import { PHOTOGRAPH_HOST_CLASS, PhotographOrnament } from "./photograph-ornament";
import { PlacesWindow } from "./places-window";
import { SearchOrnament } from "./search-ornament";
import {
  CLEAR_DIMMING,
  CLEAR_DIMMING_FEATHER,
  ENVIRONMENT_ID,
  PLATTER_RADIUS,
  WINDOW_RADIUS,
  groupMaterial,
  type GlassMode,
} from "./shared";
import { TodayWindow } from "./today-window";

type GroupId = "now" | "places" | "today" | "search" | "photograph";
type PhaseMode = PhaseId | "follow";

const PHASE_KEY = "daybreak.photograph";

function readPhaseMode(): PhaseMode {
  try {
    const stored = localStorage.getItem(PHASE_KEY);
    if (stored !== null && (PHASE_IDS as readonly string[]).includes(stored)) return stored as PhaseId;
  } catch {
    // No storage: follow the day.
  }
  return "follow";
}

function storePhaseMode(mode: PhaseMode): void {
  try {
    localStorage.setItem(PHASE_KEY, mode);
  } catch {
    // The choice holds for this visit.
  }
}

/** The comparison mode is the URL's, so a link names it and composes with `?tier` and `?at`. */
function readGlassMode(): GlassMode {
  return new URLSearchParams(location.search).get("glass") === "clear" ? "clear" : "regular";
}

function writeGlassMode(mode: GlassMode): void {
  const url = new URL(location.href);
  if (mode === "clear") url.searchParams.set("glass", "clear");
  else url.searchParams.delete("glass");
  history.replaceState(history.state, "", url);
}

/**
 * The clock. `?at=HH:MM` pins it — a capture aid, so a measurement of the agenda's states is
 * reproducible; without it the page reads the real time, ticking on the minute.
 */
function useNow(): Date {
  const pinned = useMemo(() => {
    const at = new URLSearchParams(location.search).get("at");
    const match = at === null ? null : /^(\d{1,2}):(\d{2})$/.exec(at);
    if (match === null) return undefined;
    const date = new Date();
    date.setHours(Number(match[1]), Number(match[2]), 0, 0);
    return date;
  }, []);
  const [now, setNow] = useState(() => pinned ?? new Date());
  useEffect(() => {
    if (pinned !== undefined) return;
    let timer = 0;
    const schedule = (): void => {
      timer = window.setTimeout(() => {
        setNow(new Date());
        schedule();
      }, 60_000 - (Date.now() % 60_000) + 20);
    };
    schedule();
    return () => window.clearTimeout(timer);
  }, [pinned]);
  return now;
}

function useSystemScheme(): "light" | "dark" {
  const query = useMemo(() => window.matchMedia("(prefers-color-scheme: dark)"), []);
  const [dark, setDark] = useState(query.matches);
  useEffect(() => {
    const onChange = (): void => setDark(query.matches);
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, [query]);
  return dark ? "dark" : "light";
}

function useViewport(): { width: number; height: number } {
  const [viewport, setViewport] = useState(() => ({ width: window.innerWidth, height: window.innerHeight }));
  useEffect(() => {
    const onResize = (): void =>
      setViewport((was) =>
        was.width === window.innerWidth && was.height === window.innerHeight
          ? was
          : { width: window.innerWidth, height: window.innerHeight },
      );
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  return viewport;
}

/**
 * Supply the painted canvas to the runtime. The canvas itself goes first, so the glass shows the
 * new photograph on the very next frame; an ImageBitmap of the same pixels replaces it as soon as
 * it decodes, because a canvas source is re-imported on every frame that samples it and this one
 * only changes when the phase, the scheme or the window's size does.
 *
 * `defer` is the clear mode's: its dimming follows the Photograph host through a morph, a change
 * every frame, so the canvas is re-supplied each time (supplying is what marks the source dirty)
 * and the bitmap is taken once the changes stop, rather than a full-canvas copy per frame.
 */
function createSupplier(root: GlassRoot, canvas: HTMLCanvasElement): (defer?: boolean) => void {
  let token = 0;
  let current: ImageBitmap | undefined;
  let timer = 0;
  const takeBitmap = (mine: number): void => {
    void createImageBitmap(canvas).then((bitmap) => {
      if (mine !== token) {
        bitmap.close();
        return;
      }
      root.setBackdropTexture(ENVIRONMENT_ID, {
        kind: "image",
        image: bitmap,
        placement: { kind: "element", element: canvas },
      });
      const previous = current;
      current = bitmap;
      // Released after the runtime has had frames to drop its reference to it.
      if (previous !== undefined) window.setTimeout(() => previous.close(), 1000);
    });
  };
  return (defer = false) => {
    root.setBackdropTexture(ENVIRONMENT_ID, { kind: "canvas", canvas });
    const mine = ++token;
    window.clearTimeout(timer);
    if (defer) timer = window.setTimeout(() => takeBitmap(mine), 250);
    else takeBitmap(mine);
  };
}

interface Demo {
  openMenu: () => void;
  setReducedTransparency: (value: boolean) => void;
  phases: () => PhaseId[];
  setPhase: (id: string) => void;
  /** The comparison mode, as the platter's switch sets it (URL included). */
  setGlass: (mode: GlassMode) => void;
  /** A capture aid for re-measuring the clear mode's dimming; `undefined` restores the page's. */
  setDimming: (strength: number | undefined) => void;
}

export function App(props: {
  readonly reducedTransparency: boolean;
  readonly onReducedTransparency: (value: boolean) => void;
}): ReactNode {
  const { reducedTransparency, onReducedTransparency } = props;
  const { root, materialProfileDocument } = useGlassRootHandle();
  const accessibility = useGlassAccessibility();
  const scheme = useSystemScheme();
  const now = useNow();
  const viewport = useViewport();

  const [mode, setMode] = useState<PhaseMode>(readPhaseMode);
  const [glass, setGlass] = useState<GlassMode>(readGlassMode);
  const changeGlass = useCallback((next: GlassMode) => {
    writeGlassMode(next);
    setGlass(next);
  }, []);
  const [dimmingOverride, setDimmingOverride] = useState<number | undefined>(undefined);
  const strength = dimmingOverride ?? CLEAR_DIMMING[scheme];
  // Every group is told the same thing: the whole page switches, never one group.
  const material = useMemo(() => groupMaterial(glass, strength), [glass, strength]);
  const phase: PhaseId = mode === "follow" ? phaseAt(now) : mode;
  const photo = photographFor(phase);

  const gap = derivedGap(
    materialProfileDocument,
    scheme,
    (accessibility ?? NOMINAL_ACCESSIBILITY_POLICY).material,
  );
  const layout = useMemo(() => computeLayout(viewport, gap), [viewport, gap]);

  const [query, setQuery] = useState("");
  const match = useMemo(() => {
    const text = query.trim().toLowerCase();
    return text === "" ? undefined : PLACES.find((place) => place.name.toLowerCase().startsWith(text));
  }, [query]);
  /*
   * The platter is open only on the morph it was opened on. The ornament remounts its morph when
   * the Now column crosses into or out of its compact width (the other face) and when Reduce
   * Motion changes. The second is a workaround for a tracked runtime seam: a mounted morph whose
   * motion profile changes rebuilds its geometry springs at zero and collapses to 0 × 0. A morph
   * must never mount open (it would take the open platter as its closed size), so a change of key
   * closes the platter before the new morph mounts, and it stays closed if the change reverses.
   */
  const reducedMotion = accessibility?.reducedMotion === true;
  const morphKey = `${layout.compact ? "compact" : "full"}/${reducedMotion ? "reduced-motion" : "motion"}`;
  const [menu, setMenu] = useState({ open: false, key: morphKey });
  if (menu.key !== morphKey) setMenu({ open: false, key: morphKey });
  const open = menu.open && menu.key === morphKey;
  const setOpen = useCallback((value: boolean) => setMenu({ open: value, key: morphKey }), [morphKey]);

  // --- The environment -------------------------------------------------------------------

  const canvas = useRef<HTMLCanvasElement>(null);
  const supply = useRef<((defer?: boolean) => void) | null>(null);
  const paintedKey = useRef("");
  const [painted, setPainted] = useState<Painted | null>(null);
  /*
   * Clear mode only. The dimmer holds the graded paint and writes the dimmed composite over it;
   * the refs let a paint that resolves later dim for the hosts and the strength as they are then.
   */
  const dimmer = useRef<Dimmer | null>(null);
  const shapes = useRef<readonly HostShape[]>([]);
  const strengthNow = useRef(strength);
  strengthNow.current = strength;
  const viewportNow = useRef(viewport);
  viewportNow.current = viewport;
  const glassNow = useRef(glass);
  glassNow.current = glass;
  const [decoded, setDecoded] = useState(0);

  useEffect(() => {
    // Every photograph is decoded up front, so a phase change is a repaint, never a wait.
    for (const candidate of PHOTOGRAPHS) {
      void loadPhotograph(candidate.url).then(() => setDecoded((count) => count + 1));
    }
  }, []);

  useEffect(() => {
    if (root === null || canvas.current === null) return;
    supply.current = createSupplier(root, canvas.current);
    paintedKey.current = "";
  }, [root]);

  const paint = useCallback(
    (
      target: Photograph,
      targetScheme: "light" | "dark",
      size: { width: number; height: number },
      targetGlass: GlassMode,
    ): void => {
      const element = canvas.current;
      if (element === null || supply.current === null) return;
      void loadPhotograph(target.url).then((image) => {
        const scale = Math.min(2, window.devicePixelRatio || 1);
        const key = `${target.id}|${targetScheme}|${String(size.width)}x${String(size.height)}@${String(scale)}|${targetGlass}`;
        if (key === paintedKey.current || supply.current === null) return;
        paintedKey.current = key;
        const result = paintPhotograph(element, image, target, targetScheme, size, scale);
        if (targetGlass === "clear") {
          dimmer.current = createDimmer(element, result);
          const composite = dimmer.current.apply(
            shapes.current,
            { strength: strengthNow.current, feather: CLEAR_DIMMING_FEATHER },
            viewportNow.current,
          );
          supply.current();
          setPainted(composite);
          return;
        }
        dimmer.current = null;
        supply.current();
        setPainted(result);
      });
    },
    [],
  );

  // Repaint when the photograph, the scheme or the mode changes at once; after a resize, once
  // it settles.
  const settledViewport = useSettled(viewport, 120);
  useEffect(() => {
    if (root !== null) paint(photo, scheme, settledViewport, glass);
  }, [root, paint, photo, scheme, settledViewport, decoded, glass]);

  // --- The declarations ------------------------------------------------------------------

  const [photographBox, setPhotographBox] = useState<Box | null>(null);
  const [morphing, setMorphing] = useState(false);

  /*
   * The Photograph group's box is the morph's own host, which the runtime springs between the
   * closed capsule and the open platter; it is read after every frame while it can be moving,
   * so the declaration follows the box the group is actually drawing, transitions included.
   */
  useEffect(() => {
    if (root === null) return;
    let last = "";
    const read = (): void => {
      const host = document.querySelector(`.${PHOTOGRAPH_HOST_CLASS}`);
      if (host === null) return;
      const rect = host.getBoundingClientRect();
      if (rect.width < 4 || rect.height < 4) return;
      const key = [rect.x, rect.y, rect.width, rect.height].map((value) => Math.round(value)).join(",");
      if (key === last) return;
      last = key;
      setPhotographBox({ x: rect.x, y: rect.y, width: rect.width, height: rect.height });
      /*
       * A closed morph realigns its host onto a moved footprint by writing `left`/`top`, which
       * resizes nothing, so the runtime keeps drawing the glass at the cached box (a recorded
       * gap: the morph exposes no handle to invalidate). A scroll event targeted at the host is
       * the geometry sync's own "this host moved" signal, and marks that one host dirty.
       */
      host.dispatchEvent(new Event("scroll"));
    };
    read();
    return root.subscribe(read);
  }, [root, open, morphing, layout]);

  const photographFootprint = useMemo(
    (): Box => photographBox ?? { ...layout.photograph, width: 240 },
    [photographBox, layout],
  );

  /*
   * Clear mode: the dimming follows every host's footprint — the three windows, the search, and
   * the Photograph host through its morph — and each hint below is then measured from the
   * dimmed composite, which is what the glass samples.
   */
  const hostShapes = useMemo(
    (): readonly HostShape[] => [
      { box: layout.now, radius: WINDOW_RADIUS },
      { box: layout.places, radius: WINDOW_RADIUS },
      { box: layout.today, radius: WINDOW_RADIUS },
      { box: layout.search, radius: layout.search.height / 2 },
      { box: photographFootprint, radius: PLATTER_RADIUS },
    ],
    [layout, photographFootprint],
  );
  shapes.current = hostShapes;
  useLayoutEffect(() => {
    if (glass !== "clear" || dimmer.current === null || supply.current === null) return;
    const composite = dimmer.current.apply(hostShapes, { strength, feather: CLEAR_DIMMING_FEATHER }, viewport);
    supply.current(true);
    setPainted(composite);
  }, [glass, hostShapes, strength, viewport]);

  const hints = useMemo((): Partial<Record<GroupId, BackdropHint | undefined>> => {
    if (painted === null) return {};
    const measure = (box: Box | null): BackdropHint | undefined => {
      if (box === null) return undefined;
      const footprint = measureFootprint(painted, box, viewport);
      return footprint === undefined ? undefined : hintFrom(footprint);
    };
    return {
      now: measure(layout.now),
      places: measure(layout.places),
      today: measure(layout.today),
      search: measure(layout.search),
      photograph: measure(photographFootprint),
    };
  }, [painted, layout, photographFootprint, viewport]);

  // --- Hosts that move without resizing are re-measured -------------------------------------

  const handles = useRef(new Map<GroupId, GlassHostHandle>());
  const onHost = useMemo(() => {
    const make = (id: GroupId) => (handle: GlassHostHandle | null) => {
      if (handle === null) handles.current.delete(id);
      else handles.current.set(id, handle);
    };
    return { now: make("now"), places: make("places"), today: make("today"), search: make("search") };
  }, []);
  useLayoutEffect(() => {
    for (const handle of handles.current.values()) handle.invalidateGeometry();
  }, [layout]);

  // The tier that actually drew, published for the one rule that differs by tier (forced
  // colours' frame): read from the runtime's resolved state, never from what was requested.
  const drawn = useGlassCapabilities("now")?.activeRenderer;
  useEffect(() => {
    if (drawn === undefined) return;
    document.documentElement.dataset.glassTier = drawn;
  }, [drawn]);

  // The page's own tokens that the scheme decides under regular glass follow the ink under
  // clear glass (`start-page.css`); written only in that mode.
  useLayoutEffect(() => {
    if (glass !== "clear") return;
    document.documentElement.dataset.glass = "clear";
    return () => {
      delete document.documentElement.dataset.glass;
    };
  }, [glass]);

  // --- The audit contract ------------------------------------------------------------------

  const choose = useCallback((id: PhaseId) => {
    setMode(id);
    storePhaseMode(id);
  }, []);
  const follow = useCallback((value: boolean) => {
    const next: PhaseMode = value ? "follow" : phaseAt(new Date());
    setMode(next);
    storePhaseMode(next);
  }, []);

  useEffect(() => {
    if (root === null) return;
    const w = window as unknown as { __vitrea?: GlassRoot; __glassDemo?: Demo };
    w.__vitrea = root;
    w.__glassDemo = {
      openMenu: () => setOpen(true),
      setReducedTransparency: (value) => onReducedTransparency(value),
      phases: () => [...PHASE_IDS],
      setPhase: (id) => {
        if (!(PHASE_IDS as readonly string[]).includes(id)) throw new Error(`Unknown phase ${id}.`);
        flushSync(() => setMode(id as PhaseId));
        paint(
          photographFor(id as PhaseId),
          window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light",
          { width: window.innerWidth, height: window.innerHeight },
          glassNow.current,
        );
      },
      setGlass: (next) => changeGlass(next),
      setDimming: (value) => setDimmingOverride(value),
    };
  }, [root, onReducedTransparency, paint, setOpen, changeGlass]);

  return (
    <>
      <canvas ref={canvas} className="environment" aria-hidden="true" />
      <NowModule now={now} box={layout.now} hint={hints.now} material={material} onHost={onHost.now} />
      <PlacesWindow
        box={layout.places}
        hint={hints.places}
        material={material}
        match={match}
        onHost={onHost.places}
      />
      <TodayWindow now={now} box={layout.today} hint={hints.today} material={material} onHost={onHost.today} />
      <SearchOrnament
        box={layout.search}
        hint={hints.search}
        material={material}
        query={query}
        match={match}
        onQuery={setQuery}
        onHost={onHost.search}
      />
      <PhotographOrnament
        box={layout.photograph}
        compact={layout.compact}
        morphKey={morphKey}
        room={Math.max(120, viewport.height - (layout.photograph.y + layout.photograph.height + 8) - 12)}
        hint={hints.photograph}
        material={material}
        photo={photo}
        follow={mode === "follow"}
        reducedTransparency={reducedTransparency}
        clearGlass={glass === "clear"}
        open={open}
        onOpenChange={(value) => {
          setMorphing(true);
          setOpen(value);
        }}
        onChoose={choose}
        onFollow={follow}
        onReducedTransparency={onReducedTransparency}
        onClearGlass={(value) => changeGlass(value ? "clear" : "regular")}
        onMorphEnd={() => setMorphing(false)}
      />
    </>
  );
}

/** A value that follows `value` once it has stopped changing for `ms`. */
function useSettled<T>(value: T, ms: number): T {
  const [settled, setSettled] = useState(value);
  useEffect(() => {
    const timer = window.setTimeout(() => setSettled(value), ms);
    return () => window.clearTimeout(timer);
  }, [value, ms]);
  return settled;
}
