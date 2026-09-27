/**
 * Daybreak, composed: the environment, three windows and two ornaments (`DESIGN.md`).
 *
 * This file owns the page's state and the one statement the page makes about what the glass is
 * over: each group's hint, measured from the painted environment under that group's own box
 * whenever the environment or the layout moves. Everything the runtime can read for itself it
 * is left to read.
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
  hintFrom,
  loadPhotograph,
  measureFootprint,
  paintPhotograph,
  type Box,
  type Painted,
} from "./environment";
import { computeLayout, derivedGap } from "./layout";
import { NowModule } from "./now-module";
import { PHOTOGRAPH_HOST_CLASS, PhotographOrnament } from "./photograph-ornament";
import { PlacesWindow } from "./places-window";
import { SearchOrnament } from "./search-ornament";
import { ENVIRONMENT_ID } from "./shared";
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
 */
function createSupplier(root: GlassRoot, canvas: HTMLCanvasElement): () => void {
  let token = 0;
  let current: ImageBitmap | undefined;
  return () => {
    root.setBackdropTexture(ENVIRONMENT_ID, { kind: "canvas", canvas });
    const mine = ++token;
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
}

interface Demo {
  openMenu: () => void;
  setReducedTransparency: (value: boolean) => void;
  phases: () => PhaseId[];
  setPhase: (id: string) => void;
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
  const supply = useRef<(() => void) | null>(null);
  const paintedKey = useRef("");
  const [painted, setPainted] = useState<Painted | null>(null);
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
    (target: Photograph, targetScheme: "light" | "dark", size: { width: number; height: number }): void => {
      const element = canvas.current;
      if (element === null || supply.current === null) return;
      void loadPhotograph(target.url).then((image) => {
        const scale = Math.min(2, window.devicePixelRatio || 1);
        const key = `${target.id}|${targetScheme}|${String(size.width)}x${String(size.height)}@${String(scale)}`;
        if (key === paintedKey.current || supply.current === null) return;
        paintedKey.current = key;
        const result = paintPhotograph(element, image, target, targetScheme, size, scale);
        supply.current();
        setPainted(result);
      });
    },
    [],
  );

  // Repaint when the photograph or the scheme changes at once; after a resize, once it settles.
  const settledViewport = useSettled(viewport, 120);
  useEffect(() => {
    if (root !== null) paint(photo, scheme, settledViewport);
  }, [root, paint, photo, scheme, settledViewport, decoded]);

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
      photograph: measure(photographBox ?? { ...layout.photograph, width: 240 }),
    };
  }, [painted, layout, photographBox, viewport]);

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
        paint(photographFor(id as PhaseId), window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light", {
          width: window.innerWidth,
          height: window.innerHeight,
        });
      },
    };
  }, [root, onReducedTransparency, paint, setOpen]);

  return (
    <>
      <canvas ref={canvas} className="environment" aria-hidden="true" />
      <NowModule now={now} box={layout.now} hint={hints.now} onHost={onHost.now} />
      <PlacesWindow box={layout.places} hint={hints.places} match={match} onHost={onHost.places} />
      <TodayWindow now={now} box={layout.today} hint={hints.today} onHost={onHost.today} />
      <SearchOrnament
        box={layout.search}
        hint={hints.search}
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
        photo={photo}
        follow={mode === "follow"}
        reducedTransparency={reducedTransparency}
        open={open}
        onOpenChange={(value) => {
          setMorphing(true);
          setOpen(value);
        }}
        onChoose={choose}
        onFollow={follow}
        onReducedTransparency={onReducedTransparency}
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
