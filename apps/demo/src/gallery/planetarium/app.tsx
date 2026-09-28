/**
 * Tonight, composed: the sky, one window, one module and two ornaments (`DESIGN.md`).
 *
 * This file owns the page's state and the one statement the page makes about what the glass is
 * over: each group's hint and dimming strength, measured from the painted sky under that group's
 * own box whenever the sky or the layout moves (`environment.tsx`). Everything the runtime can
 * read for itself it is left to read.
 */

import { NOMINAL_ACCESSIBILITY_POLICY } from "@vitreajs/vitrea";
import { useGlassAccessibility, useGlassCapabilities, useGlassRootHandle } from "@vitreajs/vitrea-react";
import type { GlassHostHandle, GlassRoot } from "@vitreajs/vitrea-web";
import { Body, SearchRiseSet } from "astronomy-engine";
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { flushSync } from "react-dom";

import {
  bodyObjects,
  directionOfObject,
  localNoon,
  moonState,
  observerFor,
  passageOf,
  PLACES,
  siderealTime,
  sightings,
  sunState,
  type Place,
  type SkyObject,
} from "./astro";
import { readPinnedAt, timeOf, type ClockMode } from "./clock";
import names from "./data/names.json";
import starsUrl from "./data/stars.bin?url";
import { EnvironmentCanvas, viewFor, type FootprintReading } from "./environment";
import { computeLayout, derivedGap, DESIGN } from "./layout";
import { MoonModule } from "./moon-module";
import { PLACE_HOST_CLASS, PlaceOrnament } from "./place-ornament";
import { groupMaterial, PLATTER_RADIUS, WINDOW_RADIUS, type HostShape } from "./shared";
import { loadCatalog, type StarCatalog } from "./sky/catalog";
import { altAzOf, DEG, horizonYAt, project } from "./sky/projection";
import type { Box } from "./sky/renderer";
import { runMaterialiseSweep } from "./sweep";
import { TIME_HOST_CLASS, TimeOrnament } from "./time-ornament";
import { TonightWindow, type SelectedDetail } from "./tonight-window";

type GroupId = "tonight" | "moon" | "place" | "time";

const PLACE_KEY = "tonight.place";
const PHASE_IDS = ["night", "dusk", "dawn", "day"] as const;
type PhaseId = (typeof PHASE_IDS)[number];

function readPlace(): Place {
  try {
    const stored = localStorage.getItem(PLACE_KEY);
    if (stored !== null) {
      const parsed = JSON.parse(stored) as Partial<Place>;
      const listed = PLACES.find((place) => place.id === parsed.id);
      if (listed !== undefined) return listed;
      if (typeof parsed.latitude === "number" && typeof parsed.longitude === "number" && typeof parsed.timeZone === "string") {
        return { id: "here", name: parsed.name ?? "Your location", country: parsed.country ?? "", latitude: parsed.latitude, longitude: parsed.longitude, timeZone: parsed.timeZone };
      }
    }
  } catch {
    // No storage: Seoul.
  }
  return PLACES[0] as Place;
}

function storePlace(place: Place): void {
  try {
    localStorage.setItem(PLACE_KEY, JSON.stringify(place));
  } catch {
    // The choice holds for this visit.
  }
}

/**
 * Where to look on arrival: at the Moon when it is well up, otherwise toward the equator, where
 * the ecliptic and the planets are.
 */
function defaultAzimuth(place: Place, time: number): number {
  const date = new Date(time);
  const moonObject = bodyObjects(date, observerFor(place)).find((b) => b.kind === "moon");
  const equator = place.latitude >= 0 ? Math.PI : 0;
  if (moonObject !== undefined) {
    const { alt, az } = altAzOf(directionOfObject(moonObject, siderealTime(date, place.longitude), place.latitude * DEG));
    if (alt > 12 * DEG) {
      // A little toward the equator from the Moon, so it stands in the open sky beside the window
      // and the ecliptic's planets with it.
      const toward = Math.atan2(Math.sin(equator - az), Math.cos(equator - az));
      return az + Math.max(-12 * DEG, Math.min(12 * DEG, toward));
    }
  }
  return equator;
}

/** The audit's phases: instants of the pinned day, from its sunset and sunrise. */
function phaseInstant(id: PhaseId, time: number, place: Place): number {
  const noon = localNoon(new Date(time), place.timeZone);
  const observer = observerFor(place);
  const sunset = SearchRiseSet(Body.Sun, observer, -1, noon, 1)?.date;
  const sunrise = SearchRiseSet(Body.Sun, observer, +1, sunset ?? noon, 1)?.date;
  const hours = (n: number): number => noon.getTime() + n * 3_600_000;
  switch (id) {
    case "night":
      return hours(13);
    case "dusk":
      return sunset === undefined ? hours(7) : sunset.getTime() + 30 * 60_000;
    case "dawn":
      return sunrise === undefined ? hours(18) : sunrise.getTime() - 45 * 60_000;
    case "day":
      return hours(1);
  }
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
        was.width === window.innerWidth && was.height === window.innerHeight ? was : { width: window.innerWidth, height: window.innerHeight },
      );
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);
  return viewport;
}

interface Demo {
  openMenu: () => void;
  setReducedTransparency: (value: boolean) => void;
  phases: () => PhaseId[];
  setPhase: (id: string) => void;
  /** Capture aids: pin the clock, choose a place, turn the view. */
  setTime: (iso: string) => void;
  setPlace: (id: string) => void;
  setAzimuth: (degrees: number) => void;
}

export function App(props: {
  readonly reducedTransparency: boolean;
  readonly onReducedTransparency: (value: boolean) => void;
}): ReactNode {
  const { reducedTransparency, onReducedTransparency } = props;
  const { root, materialProfileDocument } = useGlassRootHandle();
  const accessibility = useGlassAccessibility();
  const reducedMotion = accessibility?.reducedMotion === true;
  const scheme = useSystemScheme();
  const viewport = useViewport();

  const [place, setPlaceState] = useState<Place>(readPlace);
  const [locating, setLocating] = useState(false);
  const [clock, setClock] = useState<ClockMode>(() => {
    const at = readPinnedAt(place.timeZone);
    return at === undefined ? { kind: "live" } : { kind: "pinned", at };
  });
  const [domTime, setDomTime] = useState(() => timeOf(clock, Date.now()));
  const [azimuth, setAzimuth] = useState(() => defaultAzimuth(place, timeOf(clock, Date.now())));
  const [selected, setSelected] = useState<SkyObject | undefined>(undefined);
  const chosen = useRef(false);
  const [catalog, setCatalog] = useState<StarCatalog | null>(null);
  const [readings, setReadings] = useState<Readonly<Record<string, FootprintReading>>>({});
  const [ready, setReady] = useState(false);
  const [present, setPresent] = useState(false);
  const [hostBoxes, setHostBoxes] = useState<{ place?: Box | undefined; time?: Box | undefined }>({});

  useEffect(() => {
    void loadCatalog(starsUrl, names as { hr: number; name: string }[]).then(setCatalog, (error: unknown) => console.error(error));
  }, []);

  // The DOM's clock: at once when pinned, on a cadence while playing, on the quarter minute live.
  useEffect(() => {
    if (root === null) return;
    if (clock.kind === "pinned") {
      setDomTime(clock.at);
      return;
    }
    setDomTime(timeOf(clock, Date.now()));
    let accumulated = 0;
    const every = clock.kind === "playing" ? 150 : 15_000;
    return root.subscribe(({ deltaMs }) => {
      accumulated += deltaMs;
      if (accumulated < every) return;
      accumulated = 0;
      setDomTime(timeOf(clock, Date.now()));
    });
  }, [root, clock]);

  // --- Layout, from the runtime's gap ------------------------------------------------------

  const gap = derivedGap(materialProfileDocument, scheme, (accessibility ?? NOMINAL_ACCESSIBILITY_POLICY).material);
  const layout = useMemo(() => {
    // The layout asks where the drawn ridge crosses under each low surface's own centre.
    const view = viewFor(azimuth, viewport);
    // The ridge under an ornament is read across its whole width, not at its centre alone: the
    // ridge rises and falls with azimuth and a capsule's end crossed it where its middle did not.
    const half = DESIGN.time.width / 2;
    const ridgeAt = (x: number): number | undefined => {
      const reads = [x - half, x, x + half].map((at) => horizonYAt(at, view));
      if (reads.some((y) => y === undefined)) return undefined;
      return Math.min(...(reads as number[]));
    };
    return computeLayout(viewport, gap, ridgeAt);
  }, [viewport, gap, azimuth]);

  /*
   * The platters are open only on the morph they were opened on: a change of Reduce Motion
   * remounts each morph closed (the tracked runtime seam; see `morph-ornament.tsx`).
   */
  const morphKey = reducedMotion ? "reduced-motion" : "motion";
  const [menus, setMenus] = useState({ time: false, place: false, key: morphKey });
  if (menus.key !== morphKey) setMenus({ time: false, place: false, key: morphKey });
  const timeOpen = menus.time && menus.key === morphKey;
  const placeOpen = menus.place && menus.key === morphKey;
  const setTimeOpen = useCallback((open: boolean) => setMenus((m) => ({ ...m, time: open, place: open ? false : m.place, key: morphKey })), [morphKey]);
  const setPlaceOpen = useCallback((open: boolean) => setMenus((m) => ({ ...m, place: open, time: open ? false : m.time, key: morphKey })), [morphKey]);

  const shapes = useMemo(
    (): readonly HostShape[] => [
      { id: "tonight", box: layout.window, radius: WINDOW_RADIUS },
      { id: "moon", box: layout.module, radius: WINDOW_RADIUS },
      { id: "place", box: hostBoxes.place ?? layout.place, radius: placeOpen ? PLATTER_RADIUS : layout.place.height / 2 },
      { id: "time", box: hostBoxes.time ?? layout.time, radius: timeOpen ? PLATTER_RADIUS : layout.time.height / 2 },
    ],
    [layout, hostBoxes, placeOpen, timeOpen],
  );

  const onPlaceBox = useCallback((box: Box | undefined) => setHostBoxes((was) => (sameBox(was.place, box) ? was : { ...was, place: box })), []);
  const onTimeBox = useCallback((box: Box | undefined) => setHostBoxes((was) => (sameBox(was.time, box) ? was : { ...was, time: box })), []);

  // Hosts that move without resizing are re-measured after a layout change.
  const handles = useRef(new Map<GroupId, GlassHostHandle>());
  const onHost = useMemo(() => {
    const make = (id: GroupId) => (handle: GlassHostHandle | null) => {
      if (handle === null) handles.current.delete(id);
      else handles.current.set(id, handle);
    };
    return { tonight: make("tonight"), moon: make("moon") };
  }, []);
  useLayoutEffect(() => {
    for (const handle of handles.current.values()) handle.invalidateGeometry();
  }, [layout]);

  // --- The sky's model at the DOM's time ------------------------------------------------------

  const date = useMemo(() => new Date(domTime), [domTime]);
  const observer = useMemo(() => observerFor(place), [place]);
  const bodies = useMemo(() => bodyObjects(date, observer), [date, observer]);
  const sun = useMemo(() => sunState(date, observer), [date, observer]);
  const moon = useMemo(() => moonState(date, observer), [date, observer]);
  const sights = useMemo(
    () => (catalog === null ? [] : sightings(date, place, catalog, bodies)),
    [catalog, date, place, bodies],
  );
  const night = useMemo(() => {
    const noon = localNoon(date, place.timeZone);
    const sunset = SearchRiseSet(Body.Sun, observer, -1, noon, 1)?.date;
    const sunrise = SearchRiseSet(Body.Sun, observer, +1, sunset ?? noon, 1)?.date;
    return { sunset, sunrise };
  }, [date, observer, place.timeZone]);

  // The first thing up is chosen for the person, once; after that the choice is theirs.
  useEffect(() => {
    if (chosen.current || sights.length === 0) return;
    chosen.current = true;
    setSelected(sights[0]?.object);
  }, [sights]);

  const selectedDetail = useMemo((): SelectedDetail | undefined => {
    if (selected === undefined) return undefined;
    const object = selected.kind === "star" ? selected : (bodies.find((b) => b.id === selected.id) ?? selected);
    const direction = directionOfObject(object, siderealTime(date, place.longitude), place.latitude * DEG);
    const { alt, az } = altAzOf(direction);
    return { object, altitude: alt / DEG, azimuth: az / DEG, passage: passageOf(object, date, observer) };
  }, [selected, bodies, date, place, observer]);

  // --- Materialise ---------------------------------------------------------------------------

  useEffect(() => {
    if (ready) setPresent(true);
  }, [ready]);
  useEffect(() => {
    if (!present || root === null) return;
    const hosts = [
      handles.current.get("tonight")?.host,
      handles.current.get("moon")?.host,
      document.querySelector<HTMLElement>(`.${PLACE_HOST_CLASS}`),
      document.querySelector<HTMLElement>(`.${TIME_HOST_CLASS}`),
    ].filter((host): host is HTMLElement => host instanceof HTMLElement);
    return runMaterialiseSweep(root, hosts, reducedMotion);
    // Once, when the material arrives; a later preference change does not replay it.
  }, [present, root]);

  // --- Handlers --------------------------------------------------------------------------------

  /*
   * A row chosen in the window names something the person may not be facing: unless it stands in
   * the open sky — inside the viewport and clear of the window and the module by the layout's gap
   * — the view turns to its azimuth, set directly (content, not page motion). A choice made on the
   * sky is already in view and turns nothing.
   */
  const chooseFromList = useCallback(
    (object: SkyObject | undefined) => {
      setSelected(object);
      if (object === undefined) return;
      const at = new Date(timeOf(clock, Date.now()));
      const current =
        object.kind === "star" ? object : (bodyObjects(at, observerFor(place)).find((b) => b.id === object.id) ?? object);
      const direction = directionOfObject(current, siderealTime(at, place.longitude), place.latitude * DEG);
      const px = project(direction, viewFor(azimuth, viewport));
      const under = (box: Box): boolean =>
        px !== undefined &&
        px[0] > box.x - layout.gap &&
        px[0] < box.x + box.width + layout.gap &&
        px[1] > box.y - layout.gap &&
        px[1] < box.y + box.height + layout.gap;
      const inView =
        px !== undefined &&
        px[0] >= 0 &&
        px[0] <= viewport.width &&
        px[1] >= 0 &&
        px[1] <= viewport.height &&
        !under(layout.window) &&
        !under(layout.module);
      if (!inView) setAzimuth(altAzOf(direction).az);
    },
    [clock, place, azimuth, viewport, layout],
  );

  const choosePlace = useCallback((next: Place) => {
    setPlaceState(next);
    storePlace(next);
    setSelected(undefined);
    chosen.current = false;
    setAzimuth(defaultAzimuth(next, Date.now()));
  }, []);

  const locate = useCallback(() => {
    if (!("geolocation" in navigator)) return;
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocating(false);
        choosePlace({
          id: "here",
          name: "Your location",
          country: "",
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        });
      },
      () => setLocating(false),
      { timeout: 10_000 },
    );
  }, [choosePlace]);

  const step = useCallback((hours: number) => setClock((mode) => ({ kind: "pinned", at: timeOf(mode, Date.now()) + hours * 3_600_000 })), []);
  const scrub = useCallback((at: number) => setClock({ kind: "pinned", at }), []);
  const play = useCallback((playing: boolean) => {
    setClock((mode) => {
      const now = Date.now();
      return playing ? { kind: "playing", from: timeOf(mode, now), startedAt: now } : { kind: "pinned", at: timeOf(mode, now) };
    });
  }, []);
  const live = useCallback(() => setClock({ kind: "live" }), []);

  // The tier that actually drew, on the document for the one rule that differs by tier.
  const drawn = useGlassCapabilities("tonight")?.activeRenderer;
  useEffect(() => {
    if (drawn === undefined) return;
    document.documentElement.dataset.glassTier = drawn;
  }, [drawn]);

  // --- The audit contract --------------------------------------------------------------------

  useEffect(() => {
    if (root === null) return;
    const w = window as unknown as { __vitrea?: GlassRoot; __glassDemo?: Demo };
    w.__vitrea = root;
    w.__glassDemo = {
      openMenu: () => setTimeOpen(true),
      setReducedTransparency: onReducedTransparency,
      phases: () => [...PHASE_IDS],
      setPhase: (id) => {
        if (!(PHASE_IDS as readonly string[]).includes(id)) throw new Error(`Unknown phase ${id}.`);
        const at = phaseInstant(id as PhaseId, timeOf(clock, Date.now()), place);
        flushSync(() => setClock({ kind: "pinned", at }));
      },
      setTime: (iso) => flushSync(() => setClock({ kind: "pinned", at: Date.parse(iso) })),
      setPlace: (id) => {
        const next = PLACES.find((candidate) => candidate.id === id);
        if (next === undefined) throw new Error(`Unknown place ${id}.`);
        flushSync(() => choosePlace(next));
      },
      setAzimuth: (degrees) => flushSync(() => setAzimuth(degrees * DEG)),
    };
  }, [root, onReducedTransparency, setTimeOpen, clock, place, choosePlace]);

  // The audit contract's readout: what the page measured and painted under each host.
  useEffect(() => {
    (window as unknown as { __tonightReadings?: unknown }).__tonightReadings = readings;
  }, [readings]);

  const material = (id: GroupId) => groupMaterial(readings[id]?.strength);
  const hint = (id: GroupId) => readings[id]?.hint;

  return (
    <>
      <EnvironmentCanvas
        place={place}
        clock={clock}
        catalog={catalog}
        azimuth={azimuth}
        onAzimuth={setAzimuth}
        selected={selected}
        onSelect={setSelected}
        shapes={shapes}
        onReadings={setReadings}
        onReady={() => setReady(true)}
        viewport={viewport}
      />
      <TonightWindow
        box={layout.window}
        hint={hint("tonight")}
        material={material("tonight")}
        present={present}
        place={place}
        date={date}
        sun={sun}
        sightings={sights}
        selected={selectedDetail}
        onSelect={chooseFromList}
        moonPhase={moon.phaseName}
        onHost={onHost.tonight}
      />
      <MoonModule box={layout.module} hint={hint("moon")} material={material("moon")} present={present} place={place} moon={moon} onHost={onHost.moon} />
      <PlaceOrnament
        box={layout.place}
        hint={hint("place")}
        material={material("place")}
        morphKey={morphKey}
        place={place}
        locating={locating}
        reducedTransparency={reducedTransparency}
        reducedMotion={reducedMotion}
        open={placeOpen}
        onOpenChange={setPlaceOpen}
        onHostBox={onPlaceBox}
        onPlace={choosePlace}
        onLocate={locate}
        onReducedTransparency={onReducedTransparency}
      />
      <TimeOrnament
        box={layout.time}
        hint={hint("time")}
        material={material("time")}
        morphKey={morphKey}
        place={place}
        time={domTime}
        clock={clock}
        sunset={night.sunset}
        sunrise={night.sunrise}
        reducedMotion={reducedMotion}
        open={timeOpen}
        onOpenChange={setTimeOpen}
        onHostBox={onTimeBox}
        onStep={step}
        onScrub={scrub}
        onPlay={play}
        onNow={live}
      />
    </>
  );
}

function sameBox(a: Box | undefined, b: Box | undefined): boolean {
  if (a === undefined || b === undefined) return a === b;
  return Math.round(a.x) === Math.round(b.x) && Math.round(a.y) === Math.round(b.y) && Math.round(a.width) === Math.round(b.width) && Math.round(a.height) === Math.round(b.height);
}
