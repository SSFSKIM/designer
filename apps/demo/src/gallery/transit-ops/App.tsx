/**
 * The page: one glass root over one live plane, with two opaque content panels.
 *
 * The content layer is the map (a canvas), the alerts sidebar and the selected
 * vehicle's detail card, all opaque. The six glass surfaces are the instrument over
 * the map — the top bar's three groups, the search suggestions, the zoom stack and the
 * vehicle's action capsule (DESIGN.md §1, inventory). State lives here; the simulation
 * and the painting live outside React and are driven by the root's own frame.
 */
import {
  GlassRoot,
  PlanePortal,
  useGlassAccessibility,
  useGlassRootHandle,
  useGlassTicker,
  type BackdropHint,
} from "@vitreajs/vitrea-react";
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { ALERTS, type Point } from "./data";
import { MapPlane, createVehicles, type MapApi } from "./MapPlane";
import type { Filters, Scheme } from "./paint";
import {
  Search,
  SelectedVehicle,
  Sidebar,
  StatusFilter,
  RouteRack,
  ZoomStack,
  type Hints,
} from "./Chrome";
import { adherenceOf, type Adherence, type Vehicle } from "./sim";

const RT_KEY = "vitrea.transit-ops.reduce-transparency";

/** `?renderer=css` asks for the CSS tier, the site's convention; otherwise the GPU tier. */
const RENDERER: "css" | "webgpu" =
  new URLSearchParams(window.location.search).get("renderer") === "css" ? "css" : "webgpu";

/**
 * Reduce Transparency, as the app's own setting. `prefers-reduced-transparency` is not
 * Baseline, so the page seeds the switch from it where the engine answers and from
 * the stored choice otherwise, and always hands the root a boolean (SKILL.md,
 * Accessibility and the fallback).
 */
function initialReducedTransparency(): boolean {
  const stored = window.localStorage.getItem(RT_KEY);
  if (stored === "1" || stored === "0") return stored === "1";
  const query = window.matchMedia("(prefers-reduced-transparency: reduce)");
  return query.media !== "not all" && query.matches;
}

function useScheme(): Scheme {
  const query = useMemo(() => window.matchMedia("(prefers-color-scheme: dark)"), []);
  const [dark, setDark] = useState(query.matches);
  useEffect(() => {
    const onChange = (): void => setDark(query.matches);
    query.addEventListener("change", onChange);
    return () => query.removeEventListener("change", onChange);
  }, [query]);
  return dark ? "dark" : "light";
}

/**
 * The audit's two handles. Written through a local view of `window` rather than a
 * global `Window` augmentation, because every gallery page compiles in one program
 * and two pages declaring the same global property with different types collide.
 */
const handles = window as unknown as {
  __vitrea?: unknown;
  __glassDemo?: { openMenu?: () => void; setReducedTransparency: (on: boolean) => void };
};

export function App(): ReactNode {
  const [reducedTransparency, setReducedTransparencyState] = useState(initialReducedTransparency);
  const setReducedTransparency = useCallback((on: boolean) => {
    window.localStorage.setItem(RT_KEY, on ? "1" : "0");
    setReducedTransparencyState(on);
  }, []);

  return (
    <GlassRoot
      renderer={RENDERER}
      colorScheme="auto"
      windowActivation="auto"
      reducedTransparency={reducedTransparency}
    >
      <Operations
        reducedTransparency={reducedTransparency}
        onReducedTransparency={setReducedTransparency}
      />
    </GlassRoot>
  );
}

interface OperationsProps {
  readonly reducedTransparency: boolean;
  readonly onReducedTransparency: (on: boolean) => void;
}

/** Before the root's first frame resolves its policy, the query answers directly. */
const REDUCED_MOTION_QUERY = "(prefers-reduced-motion: reduce)";

function Operations(props: OperationsProps): ReactNode {
  const { reducedTransparency, onReducedTransparency } = props;
  const scheme = useScheme();
  /*
   * Reduced motion steps the buses. It is read from the policy the runtime resolved,
   * which follows the system preference live (and an app override, were one set), so
   * turning the setting on or off mid-session changes the simulation on the next
   * frame; the media query answers only for the frames before the root has resolved.
   */
  const accessibility = useGlassAccessibility();
  const stepped = accessibility?.reducedMotion ?? window.matchMedia(REDUCED_MOTION_QUERY).matches;
  const { root } = useGlassRootHandle();
  const [vehicles] = useState<Vehicle[]>(createVehicles);
  const mapApi = useRef<MapApi | null>(null);

  const [routes, setRoutes] = useState<ReadonlySet<string>>(() => new Set());
  const [adherence, setAdherence] = useState<"all" | Adherence>("all");
  const filters: Filters = useMemo(() => ({ routes, adherence }), [routes, adherence]);

  const [selected, setSelected] = useState<string | null>(null);
  // The vehicle keeps content from the first frame, closed: the action capsule's box,
  // and so the padding the runtime derives from its span, is already its open size
  // when it first materialises, and the card has a box to lay out.
  const [shown, setShown] = useState<string | null>("4431");
  const [highlight, setHighlight] = useState<Point | null>(null);
  const [following, setFollowing] = useState(false);
  const [hints, setHints] = useState<Readonly<Record<string, BackdropHint>>>({});
  const [searching, setSearching] = useState(false);

  const select = useCallback((fleet: string | null) => {
    setSelected(fleet);
    setFollowing(false);
    mapApi.current?.follow(null);
    if (fleet !== null) {
      setShown(fleet);
      setHighlight(null);
    }
  }, []);

  /*
   * The selected bus must not open under its own card. The visibility test runs after
   * the open state has committed, so the card and the capsule it tests against are in
   * their open boxes with this vehicle's content in them; before commit it would read
   * the closed panel, which is where the old test let a visible bus end up underneath.
   */
  useLayoutEffect(() => {
    if (selected !== null) mapApi.current?.showVehicle(selected);
  }, [selected]);

  // App content inside a plane declares its own scheme (vitrea.md §4): the plane's
  // ground follows the system, and so does every portalled cluster's `.tx` root.
  useEffect(() => {
    document.documentElement.dataset.scheme = scheme;
  }, [scheme]);

  // The audit's handles (DESIGN.md §3).
  useEffect(() => {
    handles.__vitrea = root ?? undefined;
  }, [root]);
  useEffect(() => {
    handles.__glassDemo = {
      openMenu: () => select("4431"),
      setReducedTransparency: onReducedTransparency,
    };
  }, [onReducedTransparency, select]);

  // Escape closes the platter; "/" goes to search.
  useEffect(() => {
    const onKey = (event: KeyboardEvent): void => {
      const target = event.target as HTMLElement | null;
      const typing = target?.tagName === "INPUT";
      if (event.key === "Escape" && !typing) select(null);
      if (event.key === "/" && !typing) {
        event.preventDefault();
        document.getElementById("search-input")?.focus();
      }
      if (!typing && (event.key === "=" || event.key === "+")) mapApi.current?.zoomBy(1.4);
      if (!typing && event.key === "-") mapApi.current?.zoomBy(1 / 1.4);
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [select]);

  const counts = useMemo(() => {
    const result = { all: vehicles.length, late: 0, early: 0, ontime: 0 };
    for (const vehicle of vehicles) result[adherenceOf(vehicle.seed)] += 1;
    return result;
  }, [vehicles]);

  const fallback: BackdropHint =
    scheme === "light"
      ? { tone: "light", luminance: 0.78, complexity: 0.6 }
      : { tone: "dark", luminance: 0.012, complexity: 0.5 };
  const allHints: Hints = (id) => hints[id] ?? fallback;

  const activeAlert = ALERTS.find((alert) => alert.vehicle === selected)?.id ?? null;
  const shownVehicle = vehicles.find((vehicle) => vehicle.seed.fleet === shown);

  return (
    <>
      <main className="plane tx">
        <MapPlane
          scheme={scheme}
          filters={filters}
          selected={selected}
          highlight={highlight}
          stepped={stepped}
          vehicles={vehicles}
          onSelect={select}
          onHints={setHints}
          apiRef={mapApi}
        />
        <Sidebar
          counts={counts}
          activeAlert={activeAlert}
          onAlert={(alert) => select(alert.vehicle)}
          reducedTransparency={reducedTransparency}
          onReducedTransparency={onReducedTransparency}
        />
        <SelectedVehicle
          hint={allHints("vehicle")}
          open={selected !== null}
          yielding={searching}
          vehicle={shownVehicle}
          vehicles={vehicles}
          following={following}
          onFollow={(on) => {
            setFollowing(on);
            mapApi.current?.follow(on ? (selected ?? null) : null);
          }}
          onClose={() => select(null)}
        />
      </main>
      <Gaps />
      <>
        <PlanePortal plane="base">
        <div className="topbar tx">
          <RouteRack
            hint={allHints("routes")}
            routes={routes}
            onChange={setRoutes}
          />
          <StatusFilter
            hint={allHints("status")}
            value={adherence}
            counts={counts}
            onChange={setAdherence}
          />
          <div className="topbar__spacer" aria-hidden="true" />
          <Search
            hint={allHints("search")}
            suggestHint={allHints("suggest")}
            vehicles={vehicles}
            onVehicle={select}
            onRoute={(id) => {
              setRoutes(new Set([id]));
              mapApi.current?.showRoute(id);
            }}
            onStop={(point) => {
              setHighlight(point);
              mapApi.current?.showPoint(point);
            }}
            onOpenChange={setSearching}
          />
        </div>
        </PlanePortal>
        <ZoomStack
          hint={allHints("zoom")}
          onZoom={(factor) => mapApi.current?.zoomBy(factor)}
          onFit={() => {
            setFollowing(false);
            mapApi.current?.fit();
          }}
        />
      </>
    </>
  );
}

/**
 * The room the layout gives around each group, derived every frame from the sampling
 * padding the runtime actually resolved (it follows the blur, and rises under Reduce
 * Transparency), never pinned. Core's own overlap check reads its advisory padding of
 * 24 where the descriptor names none, so that is the floor.
 *
 * Two kinds of gap. Between two glass groups it is the larger one's padding, so their
 * proxies never cover each other's shapes. Between glass and an opaque panel it is the
 * glass group's own padding, because every group samples the painted plane and the
 * plane under a panel is not what the reader sees: a sampled box that reached under
 * the sidebar or the card would carry map the panel hides into the glass at its edge.
 */
function Gaps(): null {
  const { root } = useGlassRootHandle();
  const ticker = useGlassTicker();
  const current = useRef<Record<string, number>>({});
  useEffect(() => {
    if (root === null) return;
    return ticker.subscribe(() => {
      const groups = root.renderInput()?.groups ?? [];
      const pad = (id: string): number =>
        Math.max(24, groups.find((group) => group.groupId === id)?.samplingPadding ?? 24);
      const gap = (...ids: string[]): number => Math.ceil(Math.max(...ids.map(pad))) + 2;
      const values: Record<string, number> = {
        // Glass beside an opaque panel: the bar and the zoom stack from the sidebar,
        // the top bar from the card below it, the action capsule from the card above.
        "--gap-side": gap("routes", "zoom"),
        "--gap-top": gap("routes", "status", "search"),
        "--gap-actions": gap("vehicle"),
        // Glass beside glass: the bar's three groups.
        "--gap-bar": gap("routes", "status"),
        "--gap-search": gap("status", "search"),
      };
      // Grow at once, shrink only past a few pixels, so a padding that breathes with
      // a surface's span does not nudge the layout on every change.
      let changed = false;
      for (const [name, value] of Object.entries(values)) {
        const previous = current.current[name];
        if (previous === undefined || value > previous || previous - value > 6) {
          current.current[name] = value;
          document.documentElement.style.setProperty(name, `${value}px`);
          changed = true;
        }
      }
      if (!changed) return;
      /*
       * A host that MOVES without resizing is invisible to the runtime's geometry
       * sync: it re-measures on a host's own resize, a scroll, a viewport resize or
       * a host handle's invalidateGeometry(). GlassSegmentedControl keeps its
       * handle to itself, so the page signals the one documented dirty source that
       * covers every host, a scroll of the document. Without this the glass stays
       * where the host was (measured on the page's first build: a platter drawn
       * 36 px above its box, and a top bar past the window's inset under Reduce
       * Transparency with no diagnostic, because the overlap check read the stale
       * rects).
       */
      document.dispatchEvent(new Event("scroll"));
    });
  }, [root, ticker]);
  return null;
}

