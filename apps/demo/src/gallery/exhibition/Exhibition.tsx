/**
 * The viewing room: the environment, one window and its two ornaments.
 *
 * Spatial register (DESIGN.md, part one). The painting is the environment; the label window is
 * set into it at the leading edge; the rooms ornament and the audio guide's transport hang below
 * the window's bottom edge, outside it by the derived gap, sampling the environment and not the
 * window's glass. Every host carries its role in `data-glass-role`, and every group declares the
 * level measured under its own footprint on the painted canvas, re-measured with the painting.
 */

import {
  GlassGroup,
  GlassSurface,
  useGlassAccessibility,
  useGlassRootHandle,
  type BackdropHint,
} from "@vitreajs/vitrea-react";
import type { GlassHostHandle } from "@vitreajs/vitrea-web";
import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useRef,
  useState,
  type CSSProperties,
  type ReactNode,
} from "react";
import { flushSync } from "react-dom";

import { EnvironmentCanvas, TEXTURE_ID } from "./EnvironmentCanvas";
import type { FootprintReading, Scheme } from "./painter";
import { formatSeconds, useAudioGuide } from "./guide";
import { NextIcon, PauseIcon, PlayIcon, PreviousIcon, RestartIcon } from "./icons";
import { LabelView } from "./LabelView";
import {
  GROUP,
  THICKNESS,
  WINDOW_RADIUS,
  useLayout,
  type Box,
} from "./layout";
import { RoomsView } from "./RoomsView";
import { WORK_IDS, WORKS, workById, type Work } from "./works";

const TEXTURE = { kind: "texture", id: TEXTURE_ID } as const;

function useScheme(): Scheme {
  const query = "(prefers-color-scheme: dark)";
  const [dark, setDark] = useState(() => window.matchMedia(query).matches);
  useEffect(() => {
    const list = window.matchMedia(query);
    const update = (): void => setDark(list.matches);
    list.addEventListener("change", update);
    return () => list.removeEventListener("change", update);
  }, []);
  return dark ? "dark" : "light";
}

function initialWork(): Work {
  return workById(window.location.hash.slice(1)) ?? (WORKS[0] as Work);
}

const boxStyle = (box: Box): CSSProperties => ({
  left: box.left,
  top: box.top,
  width: box.width,
  height: box.height,
});

/** Only a change that matters re-renders the groups: a level moving by a code or a tone flip. */
function sameHints(
  a: Readonly<Record<string, BackdropHint>>,
  b: Readonly<Record<string, BackdropHint>>,
): boolean {
  const keys = new Set([...Object.keys(a), ...Object.keys(b)]);
  for (const key of keys) {
    const x = a[key];
    const y = b[key];
    if (x === undefined || y === undefined) return false;
    if (x.tone !== y.tone) return false;
    if (Math.abs((x.luminance ?? 0) - (y.luminance ?? 0)) > 0.0015) return false;
  }
  return true;
}

export interface ExhibitionProps {
  readonly reducedTransparency: boolean;
  /** The visitor's choice, from the Rooms view's switch. */
  readonly onReducedTransparency: (value: boolean) => void;
  /** The audit contract's setter: one capture's statement, not remembered. */
  readonly onAuditReducedTransparency: (value: boolean) => void;
}

interface Readings {
  readonly groups: Record<string, FootprintReading>;
  readonly sourceMean: number;
}

export function Exhibition(props: ExhibitionProps): ReactNode {
  const { reducedTransparency, onReducedTransparency, onAuditReducedTransparency } = props;
  const { root } = useGlassRootHandle();
  const accessibility = useGlassAccessibility();
  const reducedMotion = accessibility?.reducedMotion ?? false;
  const scheme = useScheme();
  const layout = useLayout(scheme);

  const [work, setWork] = useState<Work>(initialWork);
  const [instant, setInstant] = useState(true);
  const [view, setView] = useState<"label" | "rooms">("label");
  const [hints, setHints] = useState<Readonly<Record<string, BackdropHint>>>({});
  const readings = useRef<Readings | undefined>(undefined);
  const [announcement, setAnnouncement] = useState("");

  const guide = useAudioGuide(work);
  const index = WORKS.indexOf(work);
  const ready = [GROUP.window, GROUP.rooms, GROUP.guide].every((id) => hints[id] !== undefined);

  const go = useCallback((next: Work, options?: { instant?: boolean; keepView?: boolean }) => {
    setInstant(options?.instant ?? false);
    setWork(next);
    // A visitor who moves to a room reads its label; an instrument's `setPhase` changes only the
    // environment's state and leaves the window's view where the capture put it.
    if (options?.keepView !== true) setView("label");
    const position = WORKS.indexOf(next) + 1;
    setAnnouncement(
      `Room ${position} of ${WORKS.length}, ${next.weather}: ${next.title}, ${next.artist}.`,
    );
    window.history.replaceState(null, "", `#${next.id}`);
  }, []);

  const step = useCallback(
    (delta: number) => {
      const next = WORKS[index + delta];
      if (next !== undefined) go(next);
    },
    [go, index],
  );

  const onReadings = useCallback((groups: Record<string, FootprintReading>, mean: number) => {
    readings.current = { groups, sourceMean: mean };
    const next: Record<string, BackdropHint> = {};
    for (const [id, reading] of Object.entries(groups)) next[id] = reading.hint;
    setHints((current) => (sameHints(current, next) ? current : next));
  }, []);

  // Arrow keys walk the rooms, except where a key already means something.
  useEffect(() => {
    const onKey = (event: KeyboardEvent): void => {
      if (event.defaultPrevented || event.altKey || event.ctrlKey || event.metaKey) return;
      const target = event.target as HTMLElement | null;
      if (target?.closest("input, textarea, select, [contenteditable='true']")) return;
      if (event.key === "ArrowRight") step(1);
      else if (event.key === "ArrowLeft") step(-1);
      else return;
      event.preventDefault();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [step]);

  useEffect(() => {
    const onHash = (): void => {
      const next = workById(window.location.hash.slice(1));
      if (next !== undefined && next.id !== work.id) go(next);
    };
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, [go, work.id]);

  // The audit contract, published once the glass is registered, so an instrument that reads the
  // root two frames after it appears reads the composed page and not an empty one.
  useEffect(() => {
    if (root === null || !ready) return;
    const w = window as unknown as Record<string, unknown>;
    w.__vitrea = root;
    w.__glassDemo = {
      setReducedTransparency: (value: boolean) =>
        flushSync(() => onAuditReducedTransparency(value)),
      phases: () => [...WORK_IDS],
      setPhase: (id: string) => {
        const next = workById(id);
        if (next === undefined) {
          throw new Error(`No room "${id}"; the phases are ${WORK_IDS.join(", ")}.`);
        }
        flushSync(() => go(next, { instant: true, keepView: true }));
      },
    };
    w.__exhibition = {
      readings: () => readings.current,
      layout: () => layout,
      scheme: () => scheme,
    };
  }, [go, layout, onAuditReducedTransparency, ready, root, scheme]);

  // A host moved without resizing keeps its cached box; say so whenever the layout moves it.
  const handles = useRef(new Map<string, GlassHostHandle>());
  const onHost = useCallback(
    (id: string) => (handle: GlassHostHandle | null) => {
      if (handle === null) handles.current.delete(id);
      else handles.current.set(id, handle);
    },
    [],
  );
  const hostCallbacks = useRef({
    window: onHost("window"),
    rooms: onHost("rooms"),
    guide: onHost("guide"),
  });
  useLayoutEffect(() => {
    for (const handle of handles.current.values()) handle.invalidateGeometry();
  }, [layout]);

  // The window's scroller: back to the top on a new work or view; scroll edges only where
  // content actually passes under the window's inner edges.
  const scroller = useRef<HTMLDivElement | null>(null);
  const updateEdges = useCallback(() => {
    const element = scroller.current;
    if (element === null) return;
    const top = element.scrollTop > 1;
    const bottom = element.scrollTop + element.clientHeight < element.scrollHeight - 1;
    element.dataset.edgeTop = String(top);
    element.dataset.edgeBottom = String(bottom);
  }, []);
  useLayoutEffect(() => {
    const element = scroller.current;
    if (element === null) return;
    element.scrollTop = 0;
    updateEdges();
  }, [ready, work, view, updateEdges]);
  useEffect(() => {
    const element = scroller.current;
    if (element === null) return;
    const observer = new ResizeObserver(updateEdges);
    observer.observe(element);
    const content = element.firstElementChild;
    if (content !== null) observer.observe(content);
    return () => observer.disconnect();
  }, [ready, updateEdges, view, work]);

  // Follow the guide through the essay, inside the window's own scroller only.
  useEffect(() => {
    const element = scroller.current;
    if (!guide.playing || element === null) return;
    const spoken = element.querySelector<HTMLElement>(".is-spoken");
    if (spoken === null) return;
    const box = spoken.getBoundingClientRect();
    const frame = element.getBoundingClientRect();
    const margin = 72;
    let delta = 0;
    if (box.bottom > frame.bottom - margin) delta = box.bottom - (frame.bottom - margin);
    else if (box.top < frame.top + margin) delta = box.top - (frame.top + margin);
    if (delta !== 0) {
      element.scrollBy({ top: delta, behavior: reducedMotion ? "auto" : "smooth" });
    }
  }, [guide.playing, guide.sentence, reducedMotion]);

  // The ground the children sit on is the drawn body, not the backdrop the hint describes: the
  // grading keeps every body in its scheme's half in every phase and pose (DESIGN.md, part two:
  // 0.66 and up in the light scheme, 0.37 and down in the dark), while a backdrop can read just
  // under the hint's 0.5 tone cut beneath a light body. Fills and `color-scheme` follow the body.
  const ground: Scheme = scheme;
  const progress = guide.progress;
  const atStart = guide.atStart;
  const RING = 2 * Math.PI * 19;

  return (
    <>
      <EnvironmentCanvas
        work={work}
        instant={instant}
        reducedMotion={reducedMotion}
        scheme={scheme}
        footprints={layout.footprints}
        onReadings={onReadings}
      />
      <p className="exh-visually-hidden" aria-live="polite">
        {announcement}
      </p>

      {ready ? (
        <>
          <GlassGroup id={GROUP.window} backdrop={TEXTURE} hint={hints[GROUP.window]}>
            <GlassSurface
              asChild
              radius={WINDOW_RADIUS}
              thickness={THICKNESS}
              foreground="vibrant"
              onHost={hostCallbacks.current.window}
            >
              <section
                id="exh-window"
                className="exh-window"
                aria-label={view === "label" ? "Gallery label" : "Exhibition rooms"}
                data-glass-role="window"
                data-ground={ground}
                style={{ ...boxStyle(layout.window), colorScheme: ground }}
              >
                <div
                  className="exh-scroll"
                  ref={scroller}
                  onScroll={updateEdges}
                  tabIndex={0}
                  role="region"
                  aria-label={view === "label" ? "Label text" : "Rooms and notes"}
                >
                  {view === "label" ? (
                    <LabelView
                      work={work}
                      stop={guide.stop}
                      spoken={guide.playing ? guide.sentence : undefined}
                      viewport={layout.viewport}
                    />
                  ) : (
                    <RoomsView
                      current={work}
                      onChoose={(next) => go(next)}
                      reducedTransparency={reducedTransparency}
                      onReducedTransparency={onReducedTransparency}
                    />
                  )}
                </div>
              </section>
            </GlassSurface>
          </GlassGroup>

          <GlassGroup id={GROUP.rooms} backdrop={TEXTURE} hint={hints[GROUP.rooms]}>
            <GlassSurface
              asChild
              plane="overlay"
              capsule
              thickness={THICKNESS}
              interactive
              foreground="vibrant"
              onHost={hostCallbacks.current.rooms}
            >
              <nav
                className="exh-ornament exh-ornament--rooms"
                aria-label="Rooms"
                data-glass-role="ornament"
                data-ground={ground}
                style={{ ...boxStyle(layout.rooms), colorScheme: ground }}
              >
                <button
                  type="button"
                  className="exh-button exh-button--icon"
                  aria-label={
                    index > 0 ? `Previous room: ${WORKS[index - 1]?.weather}` : "Previous room"
                  }
                  disabled={index === 0}
                  onClick={() => step(-1)}
                >
                  <PreviousIcon />
                </button>
                <button
                  type="button"
                  className={`exh-button exh-index${view === "rooms" ? " is-selected" : ""}`}
                  aria-label={`All rooms. Room ${index + 1} of ${WORKS.length}`}
                  aria-expanded={view === "rooms"}
                  aria-controls="exh-window"
                  onClick={() => setView((current) => (current === "rooms" ? "label" : "rooms"))}
                >
                  <span aria-hidden="true">
                    {index + 1}
                    <span className="exh-index__of"> / {WORKS.length}</span>
                  </span>
                </button>
                <button
                  type="button"
                  className="exh-button exh-button--icon"
                  aria-label={
                    index < WORKS.length - 1
                      ? `Next room: ${WORKS[index + 1]?.weather}`
                      : "Next room"
                  }
                  disabled={index === WORKS.length - 1}
                  onClick={() => step(1)}
                >
                  <NextIcon />
                </button>
              </nav>
            </GlassSurface>
          </GlassGroup>

          <GlassGroup id={GROUP.guide} backdrop={TEXTURE} hint={hints[GROUP.guide]}>
            <GlassSurface
              asChild
              plane="overlay"
              capsule
              thickness={THICKNESS}
              interactive
              foreground="vibrant"
              onHost={hostCallbacks.current.guide}
            >
              <div
                className="exh-ornament exh-ornament--guide"
                role="group"
                aria-label="Audio guide"
                data-glass-role="ornament"
                data-ground={ground}
                style={{ ...boxStyle(layout.guide), colorScheme: ground }}
              >
                <button
                  type="button"
                  className="exh-button exh-button--icon exh-play"
                  aria-label={guide.playing ? "Pause the audio guide" : "Play the audio guide"}
                  disabled={!guide.available}
                  onClick={guide.toggle}
                >
                  <svg className="exh-play__ring" viewBox="0 0 44 44" aria-hidden="true">
                    <circle className="exh-play__track" cx="22" cy="22" r="19" />
                    {progress > 0 ? (
                      <circle
                        className="exh-play__progress"
                        cx="22"
                        cy="22"
                        r="19"
                        strokeDasharray={`${RING * progress} ${RING}`}
                      />
                    ) : null}
                  </svg>
                  {guide.playing ? <PauseIcon /> : <PlayIcon />}
                </button>
                <span className="exh-guide__text">
                  <span className="exh-guide__name">Audio guide</span>
                  <span className="exh-guide__time">
                    {!guide.available
                      ? "No voice in this browser"
                      : atStart
                        ? `About ${formatSeconds(guide.stop.estimatedSeconds)}`
                        : `${guide.playing ? "Playing" : "Paused"} · ${formatSeconds(
                            guide.elapsed,
                          )}`}
                  </span>
                </span>
                <button
                  type="button"
                  className="exh-button exh-button--icon"
                  aria-label="Start the stop again"
                  disabled={atStart}
                  onClick={guide.reset}
                >
                  <RestartIcon />
                </button>
              </div>
            </GlassSurface>
          </GlassGroup>
        </>
      ) : null}
    </>
  );
}
