/**
 * Film festival: the programme page of the Northlight Film Festival, a Liquid Glass demo on
 * vitrea 0.24.0. The design record, derivation and measurements are in `DESIGN.md` beside this
 * file; the plane is `Still.tsx`, the floating layer `Bar.tsx`, the printed programme `Sheet.tsx`.
 */
import {
  GlassRoot,
  useGlassAccessibility,
  useGlassRootHandle,
  useGlassWindowActivation,
  type BackdropHint,
} from "@vitreajs/vitrea-react";
import {
  StrictMode,
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";
import { createRoot } from "react-dom/client";

import { Bar, PLATTER_GAP, PLATTER_RADIUS, SECTIONS, TICKETS_RADIUS, type SectionId } from "./Bar";
import {
  bodyOf,
  displayedUnder,
  hintFrom,
  inkOver,
  paperOf,
  sameHint,
  type Footprint,
  type Ink,
  type Paper,
  type Reading,
} from "./beneath";
import type { DayId, PassId } from "./data";
import { Sheet } from "./Sheet";
import { Still } from "./Still";
import "./styles.css";

/** The site's convention: the GPU tier unless the URL asks for the CSS tier. */
const RENDERER = new URLSearchParams(window.location.search).get("renderer") === "css" ? "css" : "webgpu";

/**
 * The scroll edge's geometry, in CSS px below the bar's measured bottom: a clear band as wide as
 * the bar group's sampling reach, then the ramp over which the sheet comes back to full opacity.
 */
const EDGE_CLEARANCE = 12;
const EDGE_RAMP = 56;

interface Hints {
  readonly nav: BackdropHint | undefined;
  readonly days: BackdropHint | undefined;
  readonly tickets: BackdropHint | undefined;
}

const NO_HINTS: Hints = { nav: undefined, days: undefined, tickets: undefined };

/** Each label's own pole where the page has measured it, keyed by its link or pass. */
interface LabelInks {
  readonly nav: Readonly<Record<string, Ink>>;
  readonly platter: Readonly<Record<string, Ink>>;
}

interface LabelReadings {
  readonly nav: ReadonlyMap<string, Reading>;
  readonly platter: ReadonlyMap<string, Reading>;
}

const NO_INKS: LabelInks = { nav: {}, platter: {} };

const sameInks = (a: Readonly<Record<string, Ink>>, b: Readonly<Record<string, Ink>>): boolean =>
  Object.keys(a).length === Object.keys(b).length &&
  Object.keys(a).every((key) => a[key] === b[key]);

/** A host's own box as a capsule footprint. */
function capsuleOf(element: Element | null | undefined): Footprint | undefined {
  if (element === null || element === undefined) return undefined;
  const { x, y, width, height } = element.getBoundingClientRect();
  return width === 0 || height === 0 ? undefined : { x, y, width, height, radius: height / 2 };
}

/**
 * Where the Tickets morph's surface stands: the closed capsule's footprint (the morph's spacer in
 * the bar), or, while open, the platter's, placed from that spacer the way the morph places its
 * open end (below-end: the right edges shared, the top at the spacer's bottom plus the gap) at the
 * open content's own laid-out size.
 */
function ticketsFootprint(bar: HTMLElement, open: boolean): Footprint | undefined {
  const anchor = bar.querySelector(".ff-tickets-slot [data-vitrea-morph-anchor]");
  if (anchor === null) return undefined;
  const a = anchor.getBoundingClientRect();
  if (!open) {
    if (a.width === 0) return undefined;
    return { x: a.x, y: a.y, width: a.width, height: a.height, radius: TICKETS_RADIUS };
  }
  const platter = document.querySelector<HTMLElement>(".ff-platter");
  if (platter === null || platter.offsetWidth === 0) return undefined;
  const width = platter.offsetWidth;
  const height = platter.offsetHeight;
  return { x: a.right - width, y: a.bottom + PLATTER_GAP, width, height, radius: PLATTER_RADIUS };
}

/**
 * The platter's labels (its head and each row) at the places they will stand once it has grown:
 * their layout offsets inside the platter, from its placed footprint, so a reading taken while the
 * morph is still travelling is of the ground the label settles on.
 */
function platterLabels(platter: Footprint): readonly (readonly [string, Footprint])[] {
  const content = document.querySelector<HTMLElement>(".ff-platter");
  if (content === null) return [];
  return [...content.querySelectorAll<HTMLElement>(".ff-platter-head, .ff-platter-row")].map(
    (label) =>
      [
        label.dataset.pass ?? "head",
        {
          x: platter.x + label.offsetLeft - content.offsetLeft,
          y: platter.y + label.offsetTop - content.offsetTop,
          width: label.offsetWidth,
          height: label.offsetHeight,
          radius: 0,
        },
      ] as const,
  );
}

/** The navigation's links, each at its own box. */
function navLabels(bar: HTMLElement): readonly (readonly [string, Footprint])[] {
  return [...bar.querySelectorAll<HTMLElement>(".ff-nav > a")].map((label) => {
    const { x, y, width, height } = label.getBoundingClientRect();
    return [label.getAttribute("href") ?? "", { x, y, width, height, radius: 0 }] as const;
  });
}

const RT_QUERY = "(prefers-reduced-transparency: reduce)";
const RT_KEY = "northlight.reduce-transparency";

function useMediaQuery(query: string): boolean {
  const [matches, setMatches] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const list = window.matchMedia(query);
    const update = (): void => setMatches(list.matches);
    list.addEventListener("change", update);
    return () => list.removeEventListener("change", update);
  }, [query]);
  return matches;
}

/**
 * The page's own Reduce Transparency setting. It starts from the system's answer where the
 * engine gives one, follows it until the reader chooses, and then keeps the reader's choice. The
 * root always receives a boolean, so an engine that cannot answer the query is honoured by the
 * app rather than warned about.
 */
function useReducedTransparencySetting(): readonly [boolean, (on: boolean) => void] {
  const system = useMediaQuery(RT_QUERY);
  const [stored, setStored] = useState<boolean | null>(() => {
    try {
      const value = window.localStorage.getItem(RT_KEY);
      return value === null ? null : value === "1";
    } catch {
      return null;
    }
  });
  const set = useCallback((on: boolean) => {
    setStored(on);
    try {
      window.localStorage.setItem(RT_KEY, on ? "1" : "0");
    } catch {
      // A storage-less context keeps the choice for this visit only.
    }
  }, []);
  return [stored ?? system, set] as const;
}

function App(): ReactNode {
  // The glass root mounts into the first element of the page, so the floating controls come
  // first in reading and tab order rather than after the whole programme.
  const [mount, setMount] = useState<HTMLDivElement | null>(null);
  const [reducedTransparency, setReducedTransparency] = useReducedTransparencySetting();

  return (
    <div className="ff">
      <div ref={setMount} className="ff-glass-mount" />
      {mount !== null && (
        <GlassRoot
          container={mount}
          renderer={RENDERER}
          colorScheme="auto"
          windowActivation="auto"
          reducedTransparency={reducedTransparency}
        >
          <Page
            reducedTransparency={reducedTransparency}
            onReducedTransparency={setReducedTransparency}
          />
        </GlassRoot>
      )}
    </div>
  );
}

interface PageProps {
  readonly reducedTransparency: boolean;
  readonly onReducedTransparency: (on: boolean) => void;
}

function Page(props: PageProps): ReactNode {
  const { reducedTransparency, onReducedTransparency } = props;
  const { root, ticker } = useGlassRootHandle();
  const dark = useMediaQuery("(prefers-color-scheme: dark)");
  const reducedMotion = useMediaQuery("(prefers-reduced-motion: reduce)");

  const [day, setDay] = useState<DayId>("thu");
  const [ticketsOpen, setTicketsOpen] = useState(false);
  const [current, setCurrent] = useState<SectionId | null>(null);
  const [hints, setHints] = useState<Hints>(NO_HINTS);
  const [inks, setInks] = useState<LabelInks>(NO_INKS);
  /** Bumped on every repaint of the still, so the hints are read again off the new pixels. */
  const [planeEpoch, setPlaneEpoch] = useState(0);

  const barRef = useRef<HTMLElement>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const barBottom = useRef(68);
  const openedAt = useRef(0);
  const plane = useRef<HTMLCanvasElement | null>(null);
  const ticketsOpenNow = useRef(false);
  const labelReadings = useRef<LabelReadings>({ nav: new Map(), platter: new Map() });
  const inksNow = useRef<LabelInks>(NO_INKS);
  /**
   * Where focus goes once the tickets morph has moved: into the menu (on a given pass, or its first
   * item) or back to the capsule. The platter changes plane as it opens and closes, and a moved
   * node drops focus, so the target is applied on the next frame and again when the morph settles.
   */
  const pendingFocus = useRef<{ readonly to: "menu"; readonly pass?: PassId } | { readonly to: "trigger" } | null>(null);

  const behavior: ScrollBehavior = reducedMotion ? "auto" : "smooth";

  /*
   * The two labels whose ground the page can predict, given its own plane and the runtime's
   * resolved policy and pose, take a pole the page chose from measurement (DESIGN.md, contrast).
   * The runtime's pick is a two-pole guess, and over this still two surfaces sit on its crossover:
   * the day control, where the dark material's plain body is mid-grey and its frosted and
   * high-contrast bodies are dark; and the tinted Tickets capsule, red whenever the window is active
   * and a grey when it is not, light or dark with the frost.
   */
  const policy = useGlassAccessibility();
  const activation = useGlassWindowActivation();
  const frosted = policy?.reducedTransparency ?? reducedTransparency;
  const contrasted = policy?.increasedContrast ?? false;
  const daysInk = dark && (frosted || contrasted) ? "light" : "dark";
  // Active, the tint is a red shade in every state (a preference resolves before the tint, which
  // keeps its colour): white. Receded it loses its chroma: a light grey, black on it, except under
  // the dark scheme's frost, where the receded body is dark.
  const ticketsInk = activation !== "inactive" ? "light" : dark && frosted ? "light" : "dark";

  /*
   * The scroll edge. Its stops are the bar's measured bottom plus the clearance, recomputed on
   * every scroll and whenever the bar's box changes, and written to the scrolling column, a
   * sibling of the glass root, never to one of its ancestors.
   */
  const placeEdge = useCallback(() => {
    const column = scrollRef.current;
    if (column === null) return;
    const edge = window.scrollY - column.offsetTop + barBottom.current + EDGE_CLEARANCE;
    column.style.setProperty("--ff-edge", `${edge.toFixed(1)}px`);
    column.style.setProperty("--ff-edge-end", `${(edge + EDGE_RAMP).toFixed(1)}px`);
  }, []);

  /*
   * The navigation's and the platter's labels take their pole from their own ground rather than
   * the surface's (`beneath.ts`, `inkOver`): each label's reading, under the body the runtime
   * publishes for the frame it is drawing. Re-chosen whenever the readings are taken and on every
   * frame the runtime draws, because a new hint reaches the published body a frame later and the
   * body eases between levels.
   */
  const chooseInks = useCallback(() => {
    const input = root?.renderInput();
    const pick = (groupId: string, readings: ReadonlyMap<string, Reading>): Record<string, Ink> => {
      const body = bodyOf(input, groupId);
      const out: Record<string, Ink> = {};
      if (body === undefined) return out;
      for (const [key, reading] of readings) out[key] = inkOver(reading, body);
      return out;
    };
    const next: LabelInks = {
      nav: pick("nav", labelReadings.current.nav),
      platter: pick("tickets", labelReadings.current.platter),
    };
    // Compared here rather than in the updater, so a frame that changes nothing schedules nothing.
    const prev = inksNow.current;
    if (sameInks(prev.nav, next.nav) && sameInks(prev.platter, next.platter)) return;
    inksNow.current = next;
    setInks(next);
  }, [root]);

  // Re-chosen on every frame the runtime draws, and never the reason one is drawn.
  useEffect(() => ticker.subscribe(() => {
    chooseInks();
    return false;
  }), [chooseInks, ticker]);

  /*
   * Every group's hint, measured off what the page displays under the group's footprint
   * (`beneath.ts`): the still's painted pixels, and, where the scroll column paints paper, that
   * paper through the scroll edge's mask. Read after every repaint of the still, whenever the bar
   * or one of its hosts changes box, when the scheme changes the paper, when the platter opens or
   * closes, and on every scroll while it is open, because then the sheet moves beneath it.
   */
  const measureHints = useCallback(() => {
    const canvas = plane.current;
    const bar = barRef.current;
    const column = scrollRef.current;
    if (canvas === null || bar === null || column === null) return;
    const papers = [...column.querySelectorAll(".ff-tab, .ff-sheet, .ff-footer")]
      .map(paperOf)
      .filter((paper): paper is Paper => paper !== undefined);
    const start = barBottom.current + EDGE_CLEARANCE;
    const edge = { start, end: start + EDGE_RAMP };
    const read = (footprint: Footprint | undefined): BackdropHint | undefined => {
      if (footprint === undefined) return undefined;
      const reading = displayedUnder(canvas, footprint, papers, edge);
      return reading === undefined ? undefined : hintFrom(reading);
    };
    const tickets = ticketsFootprint(bar, ticketsOpenNow.current);
    const next: Hints = {
      nav: read(capsuleOf(bar.querySelector(".ff-nav"))),
      days: read(capsuleOf(bar.querySelector(".ff-days"))),
      tickets: read(tickets),
    };
    const readAll = (labels: readonly (readonly [string, Footprint])[]): Map<string, Reading> => {
      const readings = new Map<string, Reading>();
      for (const [key, footprint] of labels) {
        const reading = displayedUnder(canvas, footprint, papers, edge);
        if (reading !== undefined) readings.set(key, reading);
      }
      return readings;
    };
    labelReadings.current = {
      nav: readAll(navLabels(bar)),
      platter:
        ticketsOpenNow.current && tickets !== undefined
          ? readAll(platterLabels(tickets))
          : new Map<string, Reading>(),
    };
    chooseInks();
    setHints((prev) =>
      sameHint(prev.nav, next.nav) &&
      sameHint(prev.days, next.days) &&
      sameHint(prev.tickets, next.tickets)
        ? prev
        : next,
    );
  }, [chooseInks]);

  const onPaint = useCallback((canvas: HTMLCanvasElement) => {
    plane.current = canvas;
    setPlaneEpoch((epoch) => epoch + 1);
  }, []);

  useLayoutEffect(() => {
    ticketsOpenNow.current = ticketsOpen;
    measureHints();
  }, [dark, measureHints, planeEpoch, ticketsOpen]);

  // While the platter is open the sheet can move beneath it: read again once per frame of scroll.
  useEffect(() => {
    if (!ticketsOpen) return;
    let frame: number | undefined;
    const onScroll = (): void => {
      if (frame !== undefined) return;
      frame = window.requestAnimationFrame(() => {
        frame = undefined;
        measureHints();
      });
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => {
      window.removeEventListener("scroll", onScroll);
      if (frame !== undefined) window.cancelAnimationFrame(frame);
    };
  }, [measureHints, ticketsOpen]);

  useLayoutEffect(() => {
    const bar = barRef.current;
    const measure = (): void => {
      if (bar === null) return;
      const rect = bar.getBoundingClientRect();
      if (rect.height === 0) return;
      barBottom.current = rect.bottom;
      // Section anchors land below the scroll edge, from the same measurement.
      document.documentElement.style.setProperty(
        "--ff-anchor",
        `${Math.ceil(rect.bottom + EDGE_CLEARANCE + EDGE_RAMP + 16)}px`,
      );
      placeEdge();
      measureHints();
    };
    measure();
    // The bar, and each host and the Tickets spacer in it: a host can move without the bar
    // resizing (the navigation's width decides where the spread row puts the days below 1360).
    const observer = new ResizeObserver(measure);
    if (bar !== null) {
      observer.observe(bar);
      for (const host of bar.querySelectorAll(".ff-nav, .ff-days, [data-vitrea-morph-anchor]")) {
        observer.observe(host);
      }
    }
    window.addEventListener("scroll", placeEdge, { passive: true });
    window.addEventListener("resize", measure);
    return () => {
      observer.disconnect();
      window.removeEventListener("scroll", placeEdge);
      window.removeEventListener("resize", measure);
    };
    // The bar mounts through a portal one commit after the root exists.
  }, [measureHints, placeEdge, root]);

  // Which section the reader is in, for the navigation's current mark.
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) setCurrent(entry.target.id as SectionId);
        }
      },
      { rootMargin: "-30% 0px -60% 0px" },
    );
    for (const section of SECTIONS) {
      const element = document.getElementById(section.id);
      if (element !== null) observer.observe(element);
    }
    const top = (): void => {
      if (window.scrollY < window.innerHeight * 0.4) setCurrent(null);
    };
    window.addEventListener("scroll", top, { passive: true });
    return () => {
      observer.disconnect();
      window.removeEventListener("scroll", top);
    };
  }, []);

  const applyFocus = useCallback(() => {
    const pending = pendingFocus.current;
    if (pending === null) return;
    const selector =
      pending.to === "trigger"
        ? ".ff-tickets-trigger"
        : pending.pass === undefined
          ? ".ff-platter [role=menuitem]"
          : `.ff-platter [data-pass=${pending.pass}]`;
    document.querySelector<HTMLElement>(selector)?.focus({ preventScroll: true });
  }, []);

  const openTickets = useCallback((pass?: PassId) => {
    pendingFocus.current = pass === undefined ? { to: "menu" } : { to: "menu", pass };
    openedAt.current = window.scrollY;
    setTicketsOpen(true);
  }, []);

  const closeTickets = useCallback((restore = true) => {
    pendingFocus.current = restore ? { to: "trigger" } : null;
    setTicketsOpen(false);
  }, []);

  const ticketsSettled = useCallback(() => {
    applyFocus();
    pendingFocus.current = null;
  }, [applyFocus]);

  // A menu does not outlive a scroll or a click elsewhere.
  useEffect(() => {
    if (!ticketsOpen) return;
    const onScroll = (): void => {
      if (Math.abs(window.scrollY - openedAt.current) > 24) closeTickets(false);
    };
    const onPointer = (event: PointerEvent): void => {
      const target = event.target as Element | null;
      if (target?.closest("[data-vitrea-morph]") == null) closeTickets(false);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    document.addEventListener("pointerdown", onPointer);
    return () => {
      window.removeEventListener("scroll", onScroll);
      document.removeEventListener("pointerdown", onPointer);
    };
  }, [closeTickets, ticketsOpen]);

  // A one-off frame, not a loop: the plane move has happened by then.
  useEffect(() => {
    const frame = window.requestAnimationFrame(applyFocus);
    return () => window.cancelAnimationFrame(frame);
  }, [applyFocus, ticketsOpen]);

  const chooseDay = useCallback(
    (next: DayId) => {
      setDay(next);
      document.getElementById("programme")?.scrollIntoView({ behavior, block: "start" });
    },
    [behavior],
  );

  const choosePass = useCallback(
    (pass: PassId) => {
      closeTickets(false);
      const card = document.getElementById(`pass-${pass}`);
      card?.scrollIntoView({ behavior, block: "start" });
      card?.querySelector<HTMLElement>("button")?.focus({ preventScroll: true });
    },
    [behavior, closeTickets],
  );

  // The audit's two handles: the runtime root, and the page's menu and setting.
  useEffect(() => {
    const handles = window as unknown as Record<string, unknown>;
    if (root !== null) handles.__vitrea = root;
    handles.__glassDemo = {
      openMenu: () => openTickets(),
      setReducedTransparency: (on: boolean) => onReducedTransparency(on),
    };
  }, [onReducedTransparency, openTickets, root]);

  return (
    <>
      <Still onPaint={onPaint} />
      <Sheet
        scrollRef={scrollRef}
        day={day}
        onDay={chooseDay}
        onPass={(pass) => openTickets(pass)}
        reducedTransparency={reducedTransparency}
        onReducedTransparency={onReducedTransparency}
      />
      <Bar
        barRef={barRef}
        current={current}
        day={day}
        onDay={chooseDay}
        ticketsOpen={ticketsOpen}
        onTickets={(open) => (open ? openTickets() : closeTickets())}
        onPass={choosePass}
        daysInk={daysInk}
        ticketsInk={ticketsInk}
        onTicketsSettled={ticketsSettled}
        navInks={inks.nav}
        platterInks={inks.platter}
        navHint={hints.nav}
        daysHint={hints.days}
        ticketsHint={hints.tickets}
      />
    </>
  );
}

const container = document.getElementById("root");
if (container === null) throw new Error("The film-festival page has no #root to mount into.");

createRoot(container).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
