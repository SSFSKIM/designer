/**
 * The instrument over the map, and the two content panels beside it.
 *
 * Six glass surfaces, each a control or a transient platter: the route rack, the
 * status filter, the search field and its suggestions, the zoom stack and the
 * selected vehicle's action capsule. What sits on glass is ink or a fill, never
 * another host and never content read in place. Each host carries `data-group`, so
 * the plane can measure the pixels under it for its hint and keep the network clear
 * of it (MapPlane.tsx).
 *
 * The alerts sidebar and the vehicle's detail card are content (SKILL.md §3, step 1:
 * a list or a panel of content stays opaque whatever the brief calls it), so they
 * are opaque tonal panels in the page's own flow, never registered. Each carries
 * `data-cover`, which is how the plane knows they hide the map too.
 */
import {
  GlassGroup,
  GlassSegmentedControl,
  GlassSurface,
  type BackdropHint,
  type GlassTextureBackdrop,
} from "@vitreajs/vitrea-react";
import {
  useEffect,
  useId,
  useMemo,
  useRef,
  useState,
  type KeyboardEvent as ReactKeyboardEvent,
  type ReactNode,
} from "react";
import { ALERTS, CAMERAS, ROUTE_BY_ID, ROUTES, type Alert, type Point } from "./data";
import bridgeStill from "./images/cam-14-victoria-bridge.jpg";
import kingswayStill from "./images/cam-31-kingsway-ninth.jpg";
import {
  CameraIcon,
  CloseIcon,
  FitIcon,
  FollowIcon,
  HoldIcon,
  MinusIcon,
  PhoneIcon,
  PlusIcon,
  SearchIcon,
  SeverityGlyph,
} from "./icons";
import { routeColour } from "./paint";
import {
  destination,
  GEOMETRY,
  headways,
  nextStop,
  onDetour,
  pointAlong,
  tagOf,
  type Adherence,
  type Vehicle,
} from "./sim";

export type Hints = (groupId: string) => BackdropHint;

/** Every group reads the painted city. */
const CITY: GlassTextureBackdrop = { kind: "texture", id: "city" };

/** One thickness across the family (DESIGN.md §1, family). */
const THICKNESS = 8;
/**
 * Rung L: the suggestions platter's fixed radius, which the two opaque panels share
 * in CSS so the page has one large corner; inner fills at inset 8 take 26 - 8 = 18.
 */
const PANEL_RADIUS = 26;

function RouteDot(props: { readonly id: string }): ReactNode {
  const route = ROUTE_BY_ID.get(props.id);
  if (route === undefined) return null;
  return (
    <span
      className="route-dot"
      aria-hidden="true"
      style={{ ["--route-light" as string]: routeColour(route.hue, "light"), ["--route-dark" as string]: routeColour(route.hue, "dark") }}
    />
  );
}

function useTicking(ms: number): number {
  const [now, setNow] = useState(() => Date.now());
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now()), ms);
    return () => window.clearInterval(id);
  }, [ms]);
  return now;
}

// ---------------------------------------------------------------------------------
// Top bar: route rack, status filter, search

export function RouteRack(props: {
  readonly hint: BackdropHint;
  readonly routes: ReadonlySet<string>;
  readonly onChange: (next: ReadonlySet<string>) => void;
}): ReactNode {
  const { hint, routes, onChange } = props;
  const rack = useRef<HTMLDivElement | null>(null);
  const [focusIndex, setFocusIndex] = useState(0);

  const toggle = (id: string): void => {
    const next = new Set(routes);
    if (next.has(id)) next.delete(id);
    else next.add(id);
    onChange(next.size === ROUTES.length ? new Set() : next);
  };

  // One tab stop; the arrows move within the rack (the WAI-ARIA toolbar pattern).
  const onKeyDown = (event: ReactKeyboardEvent<HTMLDivElement>): void => {
    const buttons = [...(rack.current?.querySelectorAll<HTMLButtonElement>("button") ?? [])];
    const index = buttons.indexOf(document.activeElement as HTMLButtonElement);
    let next = -1;
    if (event.key === "ArrowRight") next = (index + 1) % buttons.length;
    else if (event.key === "ArrowLeft") next = (index - 1 + buttons.length) % buttons.length;
    else if (event.key === "Home") next = 0;
    else if (event.key === "End") next = buttons.length - 1;
    if (next < 0) return;
    event.preventDefault();
    setFocusIndex(next);
    buttons[next]?.focus();
  };

  return (
    <GlassGroup id="routes" backdrop={CITY} hint={hint}>
      <GlassSurface asChild capsule thickness={THICKNESS} foreground="vibrant" data-group="routes">
        <div ref={rack} className="rack" role="toolbar" aria-label="Routes on the map" onKeyDown={onKeyDown}>
          <button
            type="button"
            className="chip chip--all"
            aria-pressed={routes.size === 0}
            tabIndex={focusIndex === 0 ? 0 : -1}
            onClick={() => onChange(new Set())}
          >
            All routes
          </button>
          {ROUTES.map((route, i) => (
            <button
              key={route.id}
              type="button"
              className="chip"
              aria-pressed={routes.has(route.id)}
              aria-label={`Route ${route.id}, ${route.name}`}
              title={`${route.id} · ${route.name}`}
              tabIndex={focusIndex === i + 1 ? 0 : -1}
              onClick={() => toggle(route.id)}
            >
              <RouteDot id={route.id} />
              {route.id}
            </button>
          ))}
        </div>
      </GlassSurface>
    </GlassGroup>
  );
}

export function StatusFilter(props: {
  readonly hint: BackdropHint;
  readonly value: "all" | Adherence;
  readonly counts: Record<"all" | Adherence, number>;
  readonly onChange: (value: "all" | Adherence) => void;
}): ReactNode {
  const { hint, value, counts, onChange } = props;
  const items = (
    [
      ["all", "All"],
      ["late", "Late"],
      ["early", "Early"],
      ["ontime", "On time"],
    ] as const
  ).map(([key, label]) => ({
    value: key,
    "aria-label": `${label}, ${counts[key]} buses`,
    label,
  }));
  return (
    <GlassGroup id="status" backdrop={CITY} hint={hint}>
      <GlassSegmentedControl
        items={items}
        value={value}
        onChange={onChange}
        aria-label="Schedule adherence"
        radius={22}
        thickness={THICKNESS}
        indicatorInset={4}
        className="segmented"
        segmentClassName="segment"
        indicatorClassName="segment-indicator"
        data-group="status"
      />
    </GlassGroup>
  );
}

interface Suggestion {
  readonly key: string;
  readonly kind: "vehicle" | "route" | "stop";
  readonly title: string;
  readonly detail: string;
  readonly routes: readonly string[];
  readonly run: () => void;
}

interface StopEntry {
  readonly name: string;
  readonly point: Point;
  readonly routes: string[];
}

const STOPS: readonly StopEntry[] = (() => {
  const byName = new Map<string, StopEntry>();
  for (const route of ROUTES) {
    const geometry = GEOMETRY.get(route.id);
    if (geometry === undefined) continue;
    route.stops.forEach((name, i) => {
      const existing = byName.get(name);
      if (existing !== undefined) {
        if (!existing.routes.includes(route.id)) existing.routes.push(route.id);
        return;
      }
      byName.set(name, { name, point: pointAlong(geometry, geometry.stopAt[i] ?? 0).at, routes: [route.id] });
    });
  }
  return [...byName.values()];
})();

export function Search(props: {
  readonly hint: BackdropHint;
  readonly suggestHint: BackdropHint;
  readonly vehicles: readonly Vehicle[];
  readonly onVehicle: (fleet: string) => void;
  readonly onRoute: (id: string) => void;
  readonly onStop: (point: Point) => void;
  readonly onOpenChange: (open: boolean) => void;
}): ReactNode {
  const { hint, suggestHint, vehicles, onVehicle, onRoute, onStop, onOpenChange } = props;
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const [focused, setFocused] = useState(false);
  const listId = useId();

  const suggestions: Suggestion[] = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (q === "") return [];
    const out: Suggestion[] = [];
    for (const route of ROUTES) {
      if (route.id === q || route.id.startsWith(q) || route.name.toLowerCase().includes(q)) {
        out.push({
          key: `r${route.id}`,
          kind: "route",
          title: `Route ${route.id}`,
          detail: route.name,
          routes: [route.id],
          run: () => onRoute(route.id),
        });
      }
    }
    for (const vehicle of vehicles) {
      if (vehicle.seed.fleet.startsWith(q) || vehicle.seed.operator.toLowerCase().includes(q)) {
        out.push({
          key: `v${vehicle.seed.fleet}`,
          kind: "vehicle",
          title: `Bus ${vehicle.seed.fleet}`,
          detail: `to ${destination(vehicle)}`,
          routes: [vehicle.seed.route],
          run: () => onVehicle(vehicle.seed.fleet),
        });
      }
    }
    for (const stop of STOPS) {
      if (stop.name.toLowerCase().includes(q)) {
        out.push({
          key: `s${stop.name}`,
          kind: "stop",
          title: stop.name,
          detail: "Stop",
          routes: stop.routes,
          run: () => onStop(stop.point),
        });
      }
    }
    return out.slice(0, 6);
  }, [onRoute, onStop, onVehicle, query, vehicles]);

  const open = focused && suggestions.length > 0;
  useEffect(() => onOpenChange(open), [onOpenChange, open]);

  /*
   * The platter keeps the rows it last showed through its exit, so its box does not
   * collapse while it dematerialises; before it has ever opened it holds one hidden
   * row of the real height, so the absent host is a real box (span 62) and never a
   * padding-only one that `present` would materialise from span 16.
   */
  const [retained, setRetained] = useState<readonly Suggestion[]>([]);
  if (open && retained !== suggestions) setRetained(suggestions);
  const rows = open ? suggestions : retained;

  const pick = (suggestion: Suggestion | undefined): void => {
    if (suggestion === undefined) return;
    suggestion.run();
    setQuery("");
    setActive(0);
  };

  const onKeyDown = (event: ReactKeyboardEvent<HTMLInputElement>): void => {
    if (event.key === "ArrowDown") {
      event.preventDefault();
      setActive((i) => Math.min(suggestions.length - 1, i + 1));
    } else if (event.key === "ArrowUp") {
      event.preventDefault();
      setActive((i) => Math.max(0, i - 1));
    } else if (event.key === "Enter") {
      event.preventDefault();
      pick(suggestions[active]);
    } else if (event.key === "Escape") {
      if (query !== "") setQuery("");
      else (event.target as HTMLInputElement).blur();
    }
  };

  return (
    <>
      <GlassGroup id="search" backdrop={CITY} hint={hint}>
        <GlassSurface asChild capsule thickness={THICKNESS} foreground="vibrant" data-group="search">
          <div className="search" role="search">
            <SearchIcon />
            <input
              id="search-input"
              type="text"
              role="combobox"
              autoComplete="off"
              spellCheck={false}
              aria-label="Search buses, routes, stops and operators"
              aria-expanded={open}
              aria-controls={listId}
              aria-autocomplete="list"
              aria-activedescendant={open ? `${listId}-${active}` : undefined}
              placeholder="Bus, route, stop"
              value={query}
              onChange={(event) => {
                setQuery(event.target.value);
                setActive(0);
              }}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              onKeyDown={onKeyDown}
            />
            <kbd className="search__key" aria-hidden="true">
              /
            </kbd>
          </div>
        </GlassSurface>
      </GlassGroup>
      <GlassGroup id="suggest" backdrop={CITY} hint={suggestHint}>
        <GlassSurface
          plane="overlay"
          radius={PANEL_RADIUS}
          thickness={THICKNESS}
          present={open}
          foreground="vibrant"
          className="suggest tx"
          data-group="suggest"
          data-present={open}
        >
          <ul id={listId} role="listbox" aria-label="Suggestions" className="suggest__list" inert={!open}>
            {rows.length === 0 ? (
              <li className="suggest__row suggest__row--placeholder" aria-hidden="true">
                <span className="suggest__routes">
                  <span className="badge">00</span>
                </span>
                <span className="suggest__title">&nbsp;</span>
                <span className="suggest__detail">&nbsp;</span>
              </li>
            ) : null}
            {rows.map((suggestion, i) => (
              <li
                key={suggestion.key}
                id={`${listId}-${i}`}
                role="option"
                aria-selected={i === active}
                className="suggest__row"
                onPointerDown={(event) => {
                  event.preventDefault();
                  pick(suggestion);
                }}
                onPointerEnter={() => setActive(i)}
              >
                <span className="suggest__routes">
                  {suggestion.routes.slice(0, 3).map((id) => (
                    <span key={id} className="badge">
                      <RouteDot id={id} />
                      {id}
                    </span>
                  ))}
                </span>
                <span className="suggest__title">{suggestion.title}</span>
                <span className="suggest__detail">{suggestion.detail}</span>
              </li>
            ))}
          </ul>
        </GlassSurface>
      </GlassGroup>
    </>
  );
}

// ---------------------------------------------------------------------------------
// Sidebar: the alerts, and the app's display setting

/** Minutes for a fresh alert; the time it was raised once it is older than an hour. */
function ageLabel(minutes: number, now: number): string {
  if (minutes < 60) return `${Math.max(1, Math.floor(minutes))} min`;
  const raised = new Date(now - minutes * 60000);
  return `since ${raised.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit" })}`;
}

const SEVERITY_ORDER = { critical: 0, warning: 1, info: 2 } as const;
const SEVERITY_WORD = { critical: "Critical", warning: "Warning", info: "Advisory" } as const;

export function Sidebar(props: {
  readonly counts: Record<"all" | Adherence, number>;
  readonly activeAlert: string | null;
  readonly onAlert: (alert: Alert) => void;
  readonly reducedTransparency: boolean;
  readonly onReducedTransparency: (on: boolean) => void;
}): ReactNode {
  const { counts, activeAlert, onAlert, reducedTransparency, onReducedTransparency } = props;
  const now = useTicking(1000);
  const [loaded] = useState(() => Date.now());
  const elapsed = (now - loaded) / 60000;
  const clock = new Date(now);
  const alerts = [...ALERTS].sort(
    (a, b) => SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity] || a.age - b.age,
  );
  return (
    <aside className="sidebar panel tx" data-cover="sidebar" aria-labelledby="ops-title">
      <header className="sidebar__head">
        <p className="eyebrow">Port Alder Transit</p>
        <h1 id="ops-title">Network operations</h1>
        <p className="sidebar__clock">
          <time dateTime={clock.toISOString()}>
            {clock.toLocaleDateString("en-GB", { weekday: "short", day: "numeric", month: "short" })}
            {" · "}
            {clock.toLocaleTimeString("en-GB", { hour: "2-digit", minute: "2-digit", second: "2-digit" })}
          </time>
        </p>
        <p className="sidebar__summary">
          {counts.all} in service <span aria-hidden="true">·</span> {counts.late} late{" "}
          <span aria-hidden="true">·</span> {counts.early} early
        </p>
      </header>
      <section className="sidebar__section" aria-labelledby="alerts-title">
        <h2 id="alerts-title" className="section-title">
          Active alerts <span className="count">{alerts.length}</span>
        </h2>
        <ul className="alerts">
          {alerts.map((alert) => (
            <li key={alert.id}>
              <button
                type="button"
                className="alert"
                aria-current={alert.id === activeAlert ? "true" : undefined}
                onClick={() => onAlert(alert)}
              >
                <SeverityGlyph severity={alert.severity} />
                <span className="alert__body">
                  <span className="alert__title">
                    <span className="visually-hidden">{SEVERITY_WORD[alert.severity]}: </span>
                    {alert.title}
                  </span>
                  <span className="alert__meta">
                    {alert.routes.map((id) => (
                      <span key={id} className="badge">
                        <RouteDot id={id} />
                        {id}
                      </span>
                    ))}
                    <span className="alert__place">{alert.place}</span>
                  </span>
                </span>
                <span className="alert__age">{ageLabel(alert.age + elapsed, now)}</span>
              </button>
            </li>
          ))}
        </ul>
      </section>
      <footer className="sidebar__foot">
        <button
          type="button"
          role="switch"
          aria-checked={reducedTransparency}
          className="setting"
          onClick={() => onReducedTransparency(!reducedTransparency)}
        >
          <span>Reduce transparency</span>
          <span className="switch" aria-hidden="true" />
        </button>
        <p className="attribution">
          Port Alder and its network are fictional. Camera stills:{" "}
          <a href="https://unsplash.com/@skyfly_rich">Richard Lu</a> and{" "}
          <a href="https://unsplash.com/@a4ry55">Eyforis Lurt</a> on Unsplash.{" "}
          <a href="../">vitrea gallery</a>
        </p>
      </footer>
    </aside>
  );
}

// ---------------------------------------------------------------------------------
// The selected vehicle: an opaque detail card, and a glass action capsule under it

const STILLS = { bridge: bridgeStill, kingsway: kingswayStill } as const;

/** Fleet numbers name the vehicle series, not the route (data.ts). */
const FLEET_SERIES: Readonly<Record<string, string>> = {
  "21": "2017 diesel",
  "33": "2019 hybrid",
  "44": "2023 electric",
};

function statusLine(vehicle: Vehicle): { text: string; severity: "critical" | "warning" | "info" | "ok" } {
  const { seed } = vehicle;
  const tag = tagOf(vehicle);
  const minutes = Math.abs(seed.deviation);
  const adherence =
    seed.deviation >= 1 ? `${minutes} min late` : seed.deviation <= -1 ? `${minutes} min early` : "On time";
  if (seed.disabled === true) return { text: `Disabled · ${adherence}`, severity: "critical" };
  const detour = onDetour(vehicle) ? " · on detour" : "";
  if (tag === undefined || tag.severity === "info") {
    return { text: `${adherence}${detour}`, severity: tag === undefined ? "ok" : "info" };
  }
  return { text: `${adherence}${detour}`, severity: tag.severity };
}

/**
 * The selected vehicle, split along the layer line. What a dispatcher READS about the
 * bus (its identity and status, the alert's note, the nearest camera still, six
 * facts) is a dossier, so it is an opaque card in the page's flow. What they DO to it
 * (call its operator, hold it, follow it, close it) is one row of actions, so it is
 * one compact glass capsule that materialises with `present` in its own place under
 * the card. The capsule sits at a fixed place at the window's bottom-right corner,
 * so a card whose height changes with the vehicle never moves a registered host.
 *
 * Both keep the vehicle they last showed while closed: the card keeps its box, the
 * capsule its span, so reopening is one state change and not a layout.
 */
export function SelectedVehicle(props: {
  readonly hint: BackdropHint;
  readonly open: boolean;
  /** The search suggestions are open over the card's corner: the card steps aside. */
  readonly yielding: boolean;
  readonly vehicle: Vehicle | undefined;
  readonly vehicles: readonly Vehicle[];
  readonly following: boolean;
  readonly onFollow: (on: boolean) => void;
  readonly onClose: () => void;
}): ReactNode {
  const { hint, open, yielding, vehicle, vehicles, following, onFollow, onClose } = props;
  useTicking(1000);
  const [call, setCall] = useState<{ fleet: string; since: number } | null>(null);
  const [hold, setHold] = useState<string | null>(null);
  if (vehicle === undefined) return null;

  const { seed, geometry } = vehicle;
  const route = geometry.route;
  const status = statusLine(vehicle);
  const stop = nextStop(vehicle);
  const gaps = headways(vehicle, vehicles);
  const alert = ALERTS.find((candidate) => candidate.vehicle === seed.fleet);
  const camera = CAMERAS.map((candidate) => ({
    candidate,
    d: Math.hypot(candidate.at[0] - vehicle.at[0], candidate.at[1] - vehicle.at[1]),
  }))
    .filter((entry) => entry.d < 700)
    .sort((a, b) => a.d - b.d)[0];
  const onCall = call?.fleet === seed.fleet;
  const holding = hold === seed.fleet;
  const callSeconds = onCall && call !== null ? Math.floor((Date.now() - call.since) / 1000) : 0;
  const kmh = Math.round(vehicle.speed * 3.6);
  const load = seed.load / seed.capacity;

  return (
    <>
      <section
        className="detail panel tx"
        aria-labelledby="vehicle-title"
        data-cover="detail"
        data-open={open}
        data-yield={yielding}
        inert={!open || yielding}
      >
        <header className="detail__head">
          <p className="detail__route">
            <span className="badge badge--large">
              <RouteDot id={route.id} />
              {route.id}
            </span>
            <span>to {destination(vehicle)}</span>
          </p>
          <h2 id="vehicle-title" className="detail__title">
            Bus {seed.fleet}
          </h2>
          <p className="detail__status" data-severity={status.severity}>
            {status.severity === "ok" ? (
              <span className="ok-dot" aria-hidden="true" />
            ) : (
              <SeverityGlyph severity={status.severity} />
            )}
            <span>{status.text}</span>
          </p>
        </header>
        {alert !== undefined ? (
          <p className="detail__alert">
            <strong>{alert.title}.</strong> {alert.note}
          </p>
        ) : null}
        {camera !== undefined ? (
          <figure className="detail__camera">
            <img src={STILLS[camera.candidate.image]} alt={`Traffic camera still: ${camera.candidate.name}`} />
            <figcaption>
              <CameraIcon />
              <span>
                {camera.candidate.id} · {camera.candidate.name}
              </span>
              <span className="detail__camera-distance">{Math.round(camera.d / 10) * 10} m</span>
            </figcaption>
          </figure>
        ) : null}
        <dl className="facts">
          <div>
            <dt>Next stop</dt>
            <dd>
              {stop.name}
              <span className="facts__sub">{Math.max(10, Math.round(stop.metres / 10) * 10)} m</span>
            </dd>
          </div>
          <div>
            <dt>Headway</dt>
            <dd>
              {gaps.ahead === undefined ? "—" : `${Math.round(gaps.ahead)} min ahead`}
              <span className="facts__sub">
                {gaps.behind === undefined ? "" : `${Math.round(gaps.behind)} min behind`}
              </span>
            </dd>
          </div>
          <div>
            <dt>Operator</dt>
            <dd>
              {seed.operator}
              <span className="facts__sub">Block {seed.block}</span>
            </dd>
          </div>
          <div>
            <dt>Load</dt>
            <dd>
              {seed.load} of {seed.capacity}
              <span className="facts__sub">{load > 0.85 ? "Full" : load > 0.5 ? "Busy" : "Seats free"}</span>
            </dd>
          </div>
          <div>
            <dt>Speed</dt>
            <dd>
              {kmh} km/h
              <span className="facts__sub">AVL {Math.floor(vehicle.ping)} s ago</span>
            </dd>
          </div>
          <div>
            <dt>Vehicle</dt>
            <dd>
              {FLEET_SERIES[seed.fleet.slice(0, 2)] ?? "Bus"}
              <span className="facts__sub">12 m, {seed.capacity} places</span>
            </dd>
          </div>
        </dl>
        <p className="visually-hidden" aria-live="polite">
          {onCall ? `Calling ${seed.operator}` : ""}
          {holding ? `Bus ${seed.fleet} holding at ${stop.name}` : ""}
        </p>
      </section>
      <GlassGroup id="vehicle" backdrop={CITY} hint={hint}>
        {/*
          `interactive`: the housing takes the runtime's press, light from the pointer and
          compression on a spring, as the zoom stack does. The buttons inside stay plain,
          with no pressed colour of their own.
        */}
        <GlassSurface
          asChild
          capsule
          interactive
          thickness={THICKNESS}
          present={open}
          foreground="vibrant"
          data-group="vehicle"
          data-present={open}
        >
          <div className="actions tx" role="group" aria-label={`Bus ${seed.fleet}`} inert={!open}>
            <button
              type="button"
              className="action action--primary"
              aria-pressed={onCall}
              onClick={() => setCall(onCall ? null : { fleet: seed.fleet, since: Date.now() })}
            >
              <PhoneIcon />
              {onCall
                ? `End call ${Math.floor(callSeconds / 60)}:${String(callSeconds % 60).padStart(2, "0")}`
                : "Call operator"}
            </button>
            <button
              type="button"
              className="action"
              aria-pressed={holding}
              onClick={() => setHold(holding ? null : seed.fleet)}
              title={`Hold at ${stop.name}`}
            >
              <HoldIcon />
              {holding ? "Holding" : "Hold"}
            </button>
            <button type="button" className="action" aria-pressed={following} onClick={() => onFollow(!following)}>
              <FollowIcon />
              Follow
            </button>
            <button type="button" className="icon-button" aria-label="Close" onClick={onClose}>
              <CloseIcon />
            </button>
          </div>
        </GlassSurface>
      </GlassGroup>
    </>
  );
}

// ---------------------------------------------------------------------------------
// Zoom

export function ZoomStack(props: {
  readonly hint: BackdropHint;
  readonly onZoom: (factor: number) => void;
  readonly onFit: () => void;
}): ReactNode {
  const { hint, onZoom, onFit } = props;
  return (
    <GlassGroup id="zoom" backdrop={CITY} hint={hint}>
      <GlassSurface asChild capsule interactive thickness={THICKNESS} foreground="vibrant" data-group="zoom">
        <div className="zoom tx" role="group" aria-label="Map zoom">
          <button type="button" className="icon-button" aria-label="Zoom out" onClick={() => onZoom(1 / 1.5)}>
            <MinusIcon />
          </button>
          <button type="button" className="icon-button" aria-label="Zoom in" onClick={() => onZoom(1.5)}>
            <PlusIcon />
          </button>
          <button type="button" className="icon-button" aria-label="Fit the whole network" onClick={onFit}>
            <FitIcon />
          </button>
        </div>
      </GlassSurface>
    </GlassGroup>
  );
}

