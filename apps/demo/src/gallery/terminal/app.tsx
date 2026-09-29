/**
 * The terminal, composed: the map, one window and its ornaments (`DESIGN.md`).
 *
 * This file owns the page's state — the sessions, where the window is, what each group is over —
 * and the one statement the page makes about the glass: each group's hint and dimming strength,
 * measured from the painted map under that group's own box whenever the map or the window moves
 * (`environment.tsx`). Everything the runtime can read for itself it is left to read.
 */

import { NOMINAL_ACCESSIBILITY_POLICY, type GlassGroupState } from "@vitreajs/vitrea";
import {
  GLASS_CHANNEL_PROPERTIES,
  useGlassAccessibility,
  useGlassCapabilities,
  useGlassRootHandle,
  useGlassWindowActivation,
} from "@vitreajs/vitrea-react";
import type { GlassHostHandle, GlassRoot } from "@vitreajs/vitrea-web";
import { useCallback, useEffect, useLayoutEffect, useMemo, useRef, useState, type ReactNode } from "react";
import { flushSync } from "react-dom";

import { EnvironmentCanvas, type FootprintReading } from "./environment";
import { assemble, clampResize, clampWindow, DESIGN, derivedGap, firstWindow } from "./layout";
import { AppearanceSwitch, GlassSwitch, NewSession, SessionTabs, TransparencyToggle } from "./ornaments";
import { inkOf, themeFor, type InkPolarity } from "./palette";
import meta from "./data/relief.json";
import { reliefView } from "./relief";
import { groupMaterial, PROFILES, profileOf, WINDOW_RADIUS, WINDOW_THICKNESS, type Box, type HostShape } from "./shared";
import type { GlassKind, GlassReportRow, ProfileId, Scheme } from "./shell/types";
import { TerminalView, type SessionServices, type SessionSpec } from "./terminal-view";
import { TerminalWindow } from "./terminal-window";

type GroupId = "terminal" | "sessions" | "new-session" | "glass" | "appearance" | "transparency";

const HOME = "/Users/guest";
const params = new URLSearchParams(location.search);
/** `?intro=0` starts quietly; `?intro=instant` prints the intro at once (a capture aid). */
const introParam = params.get("intro");
const INTRO = introParam === "0" ? [] : ["glass", "git log --oneline -8"];
const instantIntro = introParam === "instant";

/**
 * The audit's phases: the window over the lake, and moved as far toward the east shore (the
 * Carson Range) or the west shore (the Sierra crest) as the viewport allows. Each shore phase asks
 * for a shift of `SHORE_REACH_M` on the ground from the window's first place, the distance to the
 * shore's range, and the window's clamp cuts it to what fits: at 1440 × 900 that is about 268 CSS
 * px either way, some 7 km at that scale, so the phase reads the window moved toward that shore,
 * not centred over it.
 */
const SHORE_REACH_M = 13_500;
const PHASES = { lake: 0, "east-shore": SHORE_REACH_M, "west-shore": -SHORE_REACH_M } as const;
type PhaseId = keyof typeof PHASES;

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
  setReducedTransparency: (value: boolean) => void;
  phases: () => PhaseId[];
  setPhase: (id: string) => void;
  /** A capture aid: choose a profile by id. */
  setProfile: (id: string) => void;
}

export function App(props: {
  /** The tier the page asked the root for: the shells wait until it is the one drawing. */
  readonly renderer: "webgpu" | "css";
  readonly glass: GlassKind;
  readonly scheme: Scheme;
  readonly onGlass: (glass: GlassKind) => void;
  readonly onScheme: (scheme: Scheme) => void;
  readonly reducedTransparency: boolean;
  readonly onReducedTransparency: (value: boolean) => void;
}): ReactNode {
  const { renderer, glass, scheme, onGlass, onScheme, reducedTransparency, onReducedTransparency } = props;
  const { root, materialProfileDocument } = useGlassRootHandle();
  const accessibility = useGlassAccessibility();
  const activation = useGlassWindowActivation();
  const reducedMotion = accessibility?.reducedMotion === true;
  const viewport = useViewport();

  const [sessions, setSessions] = useState<readonly SessionSpec[]>(() => [
    { id: "s1", name: "vitrea", cwd: `${HOME}/vitrea`, intro: INTRO },
  ]);
  const [active, setActive] = useState("s1");
  /** Bumped on an explicit choice of session, which hands focus to its terminal. */
  const [focusKey, setFocusKey] = useState(0);
  const counter = useRef(1);
  const [sizes, setSizes] = useState<Readonly<Record<string, { columns: number; rows: number }>>>({});
  const [readings, setReadings] = useState<Readonly<Record<string, FootprintReading>>>({});
  const [present, setPresent] = useState(false);
  const [ink, setInk] = useState<InkPolarity>(scheme === "dark" ? "light" : "dark");

  // --- Where everything stands -------------------------------------------------------------

  const [asked, setAsked] = useState<Box | undefined>(undefined);
  const policy = (accessibility ?? NOMINAL_ACCESSIBILITY_POLICY).material;
  const gap = derivedGap(materialProfileDocument, scheme, glass, policy, asked);
  const first = useMemo(() => firstWindow(viewport, gap), [viewport, gap]);
  // The map is framed once per viewport around the window's first place; it does not follow it.
  const focus = useMemo(() => ({ x: first.x + first.width / 2, y: first.y + first.height / 2 }), [first]);
  const windowBox = useMemo(() => clampWindow(asked ?? first, viewport, gap), [asked, first, viewport, gap]);
  const assembly = useMemo(() => assemble(windowBox, sessions.length, gap), [windowBox, sessions.length, gap]);

  const onBox = useCallback(
    (box: Box, gesture: "move" | "size") =>
      setAsked(gesture === "size" ? clampResize(box, viewport, gap) : clampWindow(box, viewport, gap)),
    [viewport, gap],
  );

  // A host moved without resizing keeps its cached box; a scroll event is the runtime's own
  // signal to measure again, and the window's handle is told directly.
  const windowHandle = useRef<GlassHostHandle | null>(null);
  const onWindowHost = useCallback((handle: GlassHostHandle | null) => {
    windowHandle.current = handle;
  }, []);
  useLayoutEffect(() => {
    windowHandle.current?.invalidateGeometry();
    document.dispatchEvent(new Event("scroll"));
  }, [assembly]);

  const shapes = useMemo(
    (): readonly HostShape[] => [
      { id: "terminal", box: assembly.window, radius: WINDOW_RADIUS },
      { id: "sessions", box: assembly.sessions, radius: DESIGN.ornament / 2 },
      { id: "new-session", box: assembly.newSession, radius: DESIGN.ornament / 2 },
      { id: "glass", box: assembly.glassSwitch, radius: DESIGN.ornament / 2 },
      { id: "appearance", box: assembly.appearanceSwitch, radius: DESIGN.ornament / 2 },
      { id: "transparency", box: assembly.transparency, radius: DESIGN.ornament / 2 },
    ],
    [assembly],
  );

  // --- The ink the runtime picked for the window, which the terminal's colours follow ----------

  useEffect(() => {
    if (root === null) return;
    let since = Infinity;
    return root.subscribe(({ deltaMs }) => {
      since += deltaMs;
      if (since < 250) return;
      since = 0;
      const host = windowHandle.current?.host;
      if (host === undefined) return;
      const read = inkOf(host);
      if (read !== undefined) setInk((was) => (was === read ? was : read));
    });
  }, [root]);
  const theme = useMemo(() => themeFor(ink), [ink]);

  // --- What the shell may ask ---------------------------------------------------------------

  const latest = useRef({ glass, scheme, readings, windowBox, reducedMotion, reducedTransparency, accessibility, activation });
  latest.current = { glass, scheme, readings, windowBox, reducedMotion, reducedTransparency, accessibility, activation };

  const chooseProfile = useCallback(
    (id: ProfileId): boolean => {
      const profile = PROFILES.find((p) => p.id === id);
      if (profile === undefined) return false;
      onGlass(profile.glass);
      onScheme(profile.scheme);
      return true;
    },
    [onGlass, onScheme],
  );

  const services = useMemo(
    (): SessionServices => ({
      reducedMotion: () => latest.current.reducedMotion || instantIntro,
      glassReport: () => (root === null ? undefined : glassReport(root, latest.current)),
      profiles: () => {
        const current = profileOf(latest.current.glass, latest.current.scheme);
        return PROFILES.map((p) => ({ id: p.id, name: p.name, note: p.note, active: p.id === current.id }));
      },
      setProfile: chooseProfile,
      environmentNotes,
    }),
    [root, chooseProfile],
  );

  const onSize = useCallback((id: string, columns: number, rows: number) => {
    setSizes((was) => (was[id]?.columns === columns && was[id]?.rows === rows ? was : { ...was, [id]: { columns, rows } }));
  }, []);

  const newSession = useCallback(() => {
    if (sessions.length >= DESIGN.maxSessions) return;
    counter.current += 1;
    const id = `s${String(counter.current)}`;
    setSessions((was) => [...was, { id, name: "~", cwd: HOME, intro: [] }]);
    setActive(id);
  }, [sessions.length]);

  const listed = useRef(sessions);
  listed.current = sessions;
  const closeSession = useCallback((id: string) => {
    const was = listed.current;
    if (was.length === 1) return;
    const index = was.findIndex((s) => s.id === id);
    const next = was.filter((s) => s.id !== id);
    setSessions(next);
    setActive((current) => (current === id ? (next[Math.max(0, index - 1)]?.id ?? current) : current));
    // The closing terminal held the focus; the session it closes onto takes it.
    setFocusKey((key) => key + 1);
  }, []);

  // A click on a tab (the selected one included) is an explicit choice, and moves focus into its
  // terminal; an arrow key in the tablist selects without it (`SessionTabs`). A new session's
  // terminal takes focus as it mounts.
  const openSession = useCallback((id: string) => {
    setActive(id);
    setFocusKey((key) => key + 1);
  }, []);

  // The tier that actually drew, on the document for the one rule that differs by tier.
  const drawn = useGlassCapabilities("terminal")?.activeRenderer;
  useEffect(() => {
    if (drawn !== undefined) document.documentElement.dataset.glassTier = drawn;
  }, [drawn]);

  // The shells start once the glass on the screen is the glass an intro's `glass` would report:
  // the tier the page asked for is drawing, or the runtime has named why it cannot; every host has
  // finished arriving, since the CSS tier decides its body from the area of the hosts present; and
  // the page has measured under the window. Read from the runtime's frame loop until it holds.
  const [settled, setSettled] = useState(false);
  useEffect(() => {
    if (root === null || !present || settled) return;
    return root.subscribe(() => {
      if (tierSettled(root.capabilities("terminal"), renderer) && arrived()) setSettled(true);
    });
  }, [root, present, settled, renderer]);
  const shellsReady = settled && readings.terminal !== undefined;

  // --- The audit contract ------------------------------------------------------------------

  useEffect(() => {
    if (root === null) return;
    const w = window as unknown as { __vitrea?: GlassRoot; __glassDemo?: Demo; __terminalReadings?: unknown };
    w.__vitrea = root;
    w.__glassDemo = {
      setReducedTransparency: onReducedTransparency,
      phases: () => Object.keys(PHASES) as PhaseId[],
      setPhase: (id) => {
        if (!(id in PHASES)) throw new Error(`Unknown phase ${id}.`);
        const view = reliefView(viewport, focus);
        const shift = (PHASES[id as PhaseId] / meta.metresPerPixel) * view.scale;
        flushSync(() => setAsked({ ...first, x: first.x + shift }));
      },
      setProfile: (id) => {
        if (!chooseProfile(id as ProfileId)) throw new Error(`Unknown profile ${id}.`);
      },
    };
  }, [root, onReducedTransparency, viewport, focus, first, chooseProfile]);

  useEffect(() => {
    (window as unknown as { __terminalReadings?: unknown }).__terminalReadings = readings;
  }, [readings]);

  const material = (id: GroupId) => groupMaterial(glass, scheme, readings[id]?.strength);
  const hint = (id: GroupId) => readings[id]?.hint;
  const current = sessions.find((s) => s.id === active) ?? sessions[0];
  const size = current === undefined ? undefined : sizes[current.id];

  return (
    <>
      <EnvironmentCanvas
        viewport={viewport}
        scheme={scheme}
        glass={glass}
        focus={focus}
        shapes={shapes}
        onReadings={setReadings}
        onReady={() => setPresent(true)}
      />
      <p className="credit">Terrain: USGS 3DEP, GMTED2010 and SRTM</p>
      <SessionTabs
        box={assembly.sessions}
        hint={hint("sessions")}
        material={material("sessions")}
        present={present}
        sessions={sessions}
        active={active}
        compact={assembly.compactTabs}
        onSelect={setActive}
        onOpen={openSession}
      />
      <NewSession
        box={assembly.newSession}
        hint={hint("new-session")}
        material={material("new-session")}
        present={present}
        disabled={sessions.length >= DESIGN.maxSessions}
        onNew={newSession}
      />
      <TerminalWindow
        box={assembly.window}
        hint={hint("terminal")}
        material={material("terminal")}
        present={present}
        title={current?.name ?? "vitrea"}
        detail={size === undefined ? "zsh" : `zsh · ${String(size.columns)} × ${String(size.rows)}`}
        onBox={onBox}
        onHost={onWindowHost}
      >
        {sessions.map((session) => (
          <TerminalView
            key={session.id}
            session={session}
            active={session.id === active}
            focusKey={focusKey}
            ready={shellsReady}
            theme={theme}
            cursorBlink={!reducedMotion}
            services={services}
            onSize={onSize}
            onClose={closeSession}
          />
        ))}
      </TerminalWindow>
      {/* The segmented control cannot materialise, so it is mounted once the glass is present. */}
      {present && (
        <>
          <GlassSwitch box={assembly.glassSwitch} hint={hint("glass")} material={material("glass")} value={glass} onChange={onGlass} />
          <AppearanceSwitch
            box={assembly.appearanceSwitch}
            hint={hint("appearance")}
            material={material("appearance")}
            value={scheme}
            onChange={onScheme}
          />
        </>
      )}
      <TransparencyToggle
        box={assembly.transparency}
        hint={hint("transparency")}
        material={material("transparency")}
        present={present}
        value={reducedTransparency}
        onChange={onReducedTransparency}
      />
    </>
  );
}

/**
 * Whether the window is drawn by the tier the page asked for, or the runtime has named a real
 * reason it is not (no WebGPU, a lost device). Neither of the two moments before that is glass a
 * report should describe: while WebGPU is still coming up the CSS tier draws with no reason given,
 * and until the map is handed over the texture path reports `no-texture-supplied`.
 */
function tierSettled(state: GlassGroupState | undefined, asked: "webgpu" | "css"): boolean {
  if (state === undefined || state.demotionReason === "no-texture-supplied") return false;
  return state.activeRenderer === asked || state.demotionReason !== undefined;
}

/** Whether every glass host has finished materialising: its presence channel reads 1. */
function arrived(): boolean {
  const hosts = [...document.querySelectorAll<HTMLElement>("[data-vitrea-node]")];
  const presence = (host: HTMLElement): string => host.style.getPropertyValue(GLASS_CHANNEL_PROPERTIES.materialization).trim();
  return hosts.length > 0 && hosts.every((host) => presence(host) === "1");
}

/** The `glass` command's report: what the runtime says drew, beside what the page painted. */
function glassReport(
  root: GlassRoot,
  page: {
    readonly glass: GlassKind;
    readonly scheme: Scheme;
    readonly readings: Readonly<Record<string, FootprintReading>>;
    readonly windowBox: Box;
    readonly reducedTransparency: boolean;
    readonly accessibility: ReturnType<typeof useGlassAccessibility>;
    readonly activation: ReturnType<typeof useGlassWindowActivation>;
  },
): readonly GlassReportRow[] | undefined {
  const state = root.capabilities("terminal");
  if (state === undefined) return undefined;
  const reading = page.readings.terminal;
  const document = state.materialDocument;
  const rows: GlassReportRow[] = [
    { label: "renderer", value: `${state.activeRenderer} · sampling ${state.samplingBackend}` },
    { label: "refraction", value: state.refraction },
    { label: "analysis", value: state.analysis },
    { label: "health", value: state.demotionReason === undefined ? state.health : `${state.health} (${state.demotionReason})` },
    { label: "profile", value: profileOf(page.glass, page.scheme).name },
    { label: "variant", value: page.glass === "clear" ? "clear, tuned toward a lens" : "regular, as calibrated" },
    { label: "material", value: document === undefined ? "—" : `${document.name}${document.profileKey === undefined ? "" : ` (${document.profileKey})`}` },
    { label: "digest", value: document?.resolvedMaterialSha256?.slice(0, 16) ?? "—" },
    { label: "tuned", value: document?.tuned === true ? "yes" : "no" },
    { label: "pose", value: page.activation ?? "—" },
    {
      label: "backdrop",
      value: reading === undefined ? "not measured yet" : `${String(reading.hint.tone)}, luminance ${String(reading.hint.luminance)} (measured under the window)`,
    },
    {
      label: "dimming",
      value:
        page.glass === "regular"
          ? "none: Regular draws no layer"
          : reading === undefined
            ? "—"
            : `${page.scheme === "dark" ? "darken" : "lighten"} ${reading.strength.toFixed(2)}, painted into the map`,
    },
    { label: "window", value: `${String(page.windowBox.width)} × ${String(page.windowBox.height)} CSS px, radius ${String(WINDOW_RADIUS)}, thickness ${String(WINDOW_THICKNESS)}` },
  ];
  if (state.cssBody !== undefined) rows.push({ label: "css body", value: state.cssBody });
  const a = page.accessibility;
  rows.push({
    label: "accessibility",
    value:
      a === undefined
        ? "—"
        : [
            a.reducedTransparency ? "reduced transparency" : undefined,
            a.increasedContrast ? "increased contrast" : undefined,
            a.reducedMotion ? "reduced motion" : undefined,
            a.forcedColors ? "forced colours" : undefined,
          ]
            .filter((x) => x !== undefined)
            .join(", ") || "none asked",
  });
  return rows;
}

function environmentNotes(): readonly string[] {
  const lake = meta.lakes[0];
  const [low, high] = meta.elevationRange as [number, number];
  const summits = meta.summits.map((s) => `${s.name} ${s.elevation.toLocaleString("en-US")} m`).join(", ");
  return [
    "The Lake Tahoe basin, Sierra Nevada, California and Nevada.",
    `Relief from ${low.toLocaleString("en-US")} to ${high.toLocaleString("en-US")} m; contours every ${String(meta.contourInterval)} m, index lines every ${String(meta.contourInterval * meta.indexEvery)} m.`,
    lake === undefined ? "" : `${lake.name}: ${lake.level.toLocaleString("en-US")} m, ${String(lake.areaKm2)} km² as the data reads it.`,
    `Summits, as the 30 m grid reads them (a grid rounds a summit down): ${summits}.`,
    `Elevation: Terrain Tiles on AWS. ${meta.attribution}.`,
    "Why Tahoe: macOS 26 Tahoe is the release that gave Terminal its Clear themes.",
  ].filter((line) => line.length > 0);
}
