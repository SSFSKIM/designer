/**
 * The live plane: one full-viewport canvas painted with the city and its buses, and
 * registered as the texture every glass group samples.
 *
 * The canvas is painted at its own CSS box times the device pixel ratio, so the
 * texture the renderer fits to that box is exactly the pixels on screen (vitrea.md
 * §2). Camera moves repaint synchronously inside the pointer or wheel event, before
 * the root's frame imports the canvas, so the glass never trails a drag by a frame;
 * the buses advance inside the root's own frame listener, never a second rAF loop.
 */
import type { BackdropHint } from "@vitreajs/vitrea-react";
import { useGlassRoot, useGlassTicker } from "@vitreajs/vitrea-react";
import { useEffect, useRef, type ReactNode, type RefObject } from "react";
import type { Point } from "./data";
import {
  coverageBounds,
  networkBounds,
  paintBase,
  paintVehicles,
  routeBounds,
  toWorld,
  vehicleScreen,
  type Camera,
  type Filters,
  type Marker,
  type Scheme,
} from "./paint";
import { advance, createVehicles, type Vehicle } from "./sim";

export const TEXTURE_ID = "city";

export interface MapApi {
  zoomBy(factor: number): void;
  fit(): void;
  showVehicle(fleet: string): void;
  showRoute(routeId: string): void;
  showPoint(point: Point): void;
  follow(fleet: string | null): void;
}

export interface MapPlaneProps {
  readonly scheme: Scheme;
  readonly filters: Filters;
  readonly selected: string | null;
  readonly highlight: Point | null;
  readonly stepped: boolean;
  readonly vehicles: readonly Vehicle[];
  readonly onSelect: (fleet: string | null) => void;
  readonly onHints: (hints: Readonly<Record<string, BackdropHint>>) => void;
  readonly apiRef: RefObject<MapApi | null>;
}

/**
 * The camera's zoom ceiling, in CSS px per metre. At 0.5 the coarsest street web (150 m
 * blocks) is 75 px on screen, finer than the long side of every control that floats
 * over the map (the zoom stack's 120 px is the shortest), and the soundings and tree
 * marks that give water and parks their own fine frequency hold their 24 to 48 px
 * pitch (paint.ts). The floor is not a constant: it is the zoom at which the window
 * just fits inside the mapped city, so the camera never shows past it.
 */
const K_MAX = 0.5;
const COVERAGE = coverageBounds();

/** A host's box, or a panel's, keyed by the name the layout gives it. */
interface Cover {
  readonly id: string;
  readonly rect: DOMRect;
}

function boxes(selector: string, key: "group" | "cover"): Cover[] {
  return [...document.querySelectorAll<HTMLElement>(selector)]
    .map((element) => ({ id: element.dataset[key] ?? "", rect: element.getBoundingClientRect() }))
    .filter((entry) => entry.rect.width > 0 && entry.rect.height > 0);
}

/** Every registered glass host, present or not: what the hints are measured under. */
function glassHosts(): Cover[] {
  return boxes("[data-group]", "group");
}

/**
 * What hides the map, measured: every glass host that is present (an absent platter has
 * a box but draws nothing) and every opaque panel that is showing (`data-cover`; the
 * vehicle's card counts while it is open even when it has stepped aside for the search,
 * because it is coming back).
 */
function coverRects(): Cover[] {
  return [
    ...boxes("[data-group]:not([data-present='false'])", "group"),
    ...boxes("[data-cover]:not([data-open='false'])", "cover"),
  ];
}

/**
 * The part of the window nothing covers at rest, from the measured boxes of the
 * sidebar, the top bar and the zoom stack (plus the vehicle's card and capsule while
 * they are open), with a breathing margin. The network is fitted into this rectangle,
 * which is the map's version of "content clears the floating bars by a measured inset".
 */
function freeRect(includeVehicle: boolean): { x0: number; y0: number; x1: number; y1: number } {
  const margin = 28;
  let x0 = margin;
  let y0 = margin;
  let x1 = window.innerWidth - margin;
  let y1 = window.innerHeight - margin;
  for (const { id, rect } of coverRects()) {
    if (id === "sidebar") x0 = Math.max(x0, rect.right + margin);
    if (id === "zoom") y1 = Math.min(y1, rect.top - margin);
    if (id === "routes" || id === "status" || id === "search") y0 = Math.max(y0, rect.bottom + margin);
    if ((id === "detail" || id === "vehicle") && includeVehicle) x1 = Math.min(x1, rect.left - margin);
  }
  return { x0, y0, x1, y1 };
}

/**
 * How often a hint is re-read. Every repaint of the displayed canvas (the buses move on
 * every frame, the city on every camera change) marks the hints dirty, and a dirty set
 * is re-read at most once every HINT_FRAMES frames: a throttle and not a debounce, so a
 * continuous pan cannot starve it. A host whose footprint moved (a gap change, the
 * suggestions opening, the capsule appearing) is read on the frame that sees it,
 * bypassing the throttle, because its old reading describes a place it no longer is.
 * HINT_DEADLINE_MS is the backstop for a frame loop that stopped repainting.
 */
const HINT_FRAMES = 6;
const HINT_DEADLINE_MS = 500;
/** A new reading replaces the declared one only when it moved by more than this. */
const HINT_STEP = { luminance: 0.004, complexity: 0.05 };

function sameHint(a: BackdropHint | undefined, b: BackdropHint): boolean {
  return (
    a !== undefined &&
    a.tone === b.tone &&
    Math.abs((a.luminance ?? 0) - (b.luminance ?? 0)) < HINT_STEP.luminance &&
    Math.abs((a.complexity ?? 0) - (b.complexity ?? 0)) < HINT_STEP.complexity
  );
}

export function MapPlane(props: MapPlaneProps): ReactNode {
  const root = useGlassRoot();
  const ticker = useGlassTicker();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const live = useRef(props);
  live.current = props;

  const state = useRef({
    camera: { x: -2000, y: -1200, k: 0.13 } as Camera,
    fitted: false,
    base: null as HTMLCanvasElement | null,
    baseKey: "",
    markers: [] as Marker[],
    hovered: null as string | null,
    follow: null as string | null,
    drag: null as null | { x: number; y: number; cx: number; cy: number; moved: boolean; id: number },
    /**
     * Frames since the last hint reading and its time; whether the canvas was repainted
     * since (read on the throttle), and whether a host's footprint moved (read at once).
     */
    hintFrames: HINT_FRAMES,
    hintAt: -Infinity,
    hintDirty: true,
    hintMoved: true,
    footprint: "",
    hints: {} as Record<string, BackdropHint>,
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null) return;
    const context = canvas.getContext("2d");
    if (context === null) return;
    const s = state.current;
    const base = document.createElement("canvas");
    s.base = base;
    const baseContext = base.getContext("2d");
    if (baseContext === null) return;
    // Hints are read off the displayed canvas in two steps: a half-resolution copy on
    // the GPU (`reduced`, drawn and never read), then one small readback of that copy
    // into `probe`, the only canvas the page reads pixels from. The displayed canvas
    // stays a GPU canvas that is drawn every frame and read never.
    const reduced = document.createElement("canvas");
    const reducedContext = reduced.getContext("2d");
    const probe = document.createElement("canvas");
    const probeContext = probe.getContext("2d", { willReadFrequently: true });
    if (reducedContext === null || probeContext === null) return;

    const size = (): { w: number; h: number; dpr: number } => {
      const w = window.innerWidth;
      const h = window.innerHeight;
      const dpr = Math.min(2, window.devicePixelRatio || 1);
      const bw = Math.round(w * dpr);
      const bh = Math.round(h * dpr);
      if (canvas.width !== bw || canvas.height !== bh) {
        canvas.width = bw;
        canvas.height = bh;
      }
      if (base.width !== bw || base.height !== bh) {
        base.width = bw;
        base.height = bh;
      }
      return { w, h, dpr };
    };

    /*
     * The camera is bounded to the mapped city. Its zoom runs from the scale at which
     * the window just fits inside the city to K_MAX, and its position keeps the whole
     * window inside the city, so every control (which is inside the window) always
     * floats over districts, water or parks and never over the bare land fill past
     * the city's edge. Every camera move goes through `place`.
     */
    const clampK = (k: number): number => {
      const floor = Math.max(
        window.innerWidth / (COVERAGE.x1 - COVERAGE.x0),
        window.innerHeight / (COVERAGE.y1 - COVERAGE.y0),
      );
      return Math.min(K_MAX, Math.max(floor, k));
    };
    const place = (camera: Camera): void => {
      const k = clampK(camera.k);
      s.camera = {
        k,
        x: Math.min(COVERAGE.x1 - window.innerWidth / k, Math.max(COVERAGE.x0, camera.x)),
        y: Math.min(COVERAGE.y1 - window.innerHeight / k, Math.max(COVERAGE.y0, camera.y)),
      };
    };

    const fitTo = (b: { x0: number; y0: number; x1: number; y1: number }, pad: number): void => {
      const free = freeRect(false);
      const bw = b.x1 - b.x0 + pad * 2;
      const bh = b.y1 - b.y0 + pad * 2;
      const k = clampK(Math.min((free.x1 - free.x0) / bw, (free.y1 - free.y0) / bh));
      place({
        k,
        x: (b.x0 + b.x1) / 2 - ((free.x0 + free.x1) / 2) / k,
        y: (b.y0 + b.y1) / 2 - ((free.y0 + free.y1) / 2) / k,
      });
    };

    const vehicleAt = (fleet: string): Vehicle | undefined =>
      live.current.vehicles.find((vehicle) => vehicle.seed.fleet === fleet);

    const centreOn = (point: Point, includeVehicle: boolean): void => {
      const free = freeRect(includeVehicle);
      const { k } = s.camera;
      place({ k, x: point[0] - ((free.x0 + free.x1) / 2) / k, y: point[1] - ((free.y0 + free.y1) / 2) / k });
    };

    /** True when a screen point sits under glass, under an opaque panel or off the window. */
    const hidden = (x: number, y: number): boolean => {
      if (x < 16 || y < 16 || x > window.innerWidth - 16 || y > window.innerHeight - 16) return true;
      return coverRects().some(
        ({ rect }) => x > rect.left - 20 && x < rect.right + 20 && y > rect.top - 20 && y < rect.bottom + 20,
      );
    };

    const paint = (): void => {
      const { w, h, dpr } = size();
      const p = live.current;
      // Fit once the chrome it is fitted around is laid out: the sidebar is in the
      // page's flow, the zoom stack arrives when the root's planes do.
      if (!s.fitted && document.querySelector('[data-group="zoom"]') !== null) {
        fitTo(networkBounds(), 180);
        s.fitted = true;
      }
      if (s.follow !== null) {
        const vehicle = vehicleAt(s.follow);
        if (vehicle !== undefined) centreOn(vehicle.at, true);
      }
      const key = [
        // Quantised to a quarter of a CSS pixel on screen: a camera that moved less
        // than that repaints nothing, which keeps "follow" from redrawing the city
        // every frame for a bus crawling a fraction of a pixel.
        w, h, dpr, p.scheme, Math.round(s.camera.x * s.camera.k * 4), Math.round(s.camera.y * s.camera.k * 4),
        s.camera.k.toFixed(5),
        [...p.filters.routes].sort().join(","), p.filters.adherence,
      ].join("|");
      if (key !== s.baseKey) {
        s.baseKey = key;
        paintBase(baseContext, w, h, dpr, s.camera, p.scheme, p.filters);
      }
      context.setTransform(1, 0, 0, 1, 0, 0);
      context.drawImage(base, 0, 0);
      s.markers = paintVehicles(
        context, dpr, s.camera, p.scheme, p.vehicles, p.filters, p.selected, s.hovered, p.highlight,
      );
      // Any repaint, the buses' included, changes what the hints describe.
      s.hintDirty = true;
    };

    /**
     * The hint each group declares, read off the FINAL displayed canvas (the city, the
     * buses, their tags, the selection) under each host's current box: mean relative
     * luminance, and a busyness from its spread. A declared hint is what drives the
     * tone on both tiers (the WebGPU tier stands its own measured tone down when one is
     * present), so it is read from the pixels the reader sees, on the cadence above,
     * and again whenever a host's footprint moves.
     */
    const hintTick = (now: number): void => {
      s.hintFrames += 1;
      // Every host, present or not: a platter's hint has to be right the moment it
      // materialises, so it is measured while it waits.
      const hosts = glassHosts();
      const footprint = hosts
        .map(({ id, rect }) =>
          `${id}:${Math.round(rect.left)},${Math.round(rect.top)},${Math.round(rect.width)},${Math.round(rect.height)}`)
        .join("|");
      if (footprint !== s.footprint) {
        s.footprint = footprint;
        s.hintMoved = true;
      }
      const due =
        s.hintMoved || (s.hintDirty && s.hintFrames >= HINT_FRAMES) || now - s.hintAt >= HINT_DEADLINE_MS;
      if (!due || hosts.length === 0) return;
      s.hintFrames = 0;
      s.hintAt = now;
      s.hintDirty = false;
      s.hintMoved = false;
      measureHints(hosts);
    };
    const measureHints = (hosts: readonly Cover[]): void => {
      const scale = 0.5;
      const pw = Math.max(1, Math.round(window.innerWidth * scale));
      const ph = Math.max(1, Math.round(window.innerHeight * scale));
      if (reduced.width !== pw || reduced.height !== ph) {
        reduced.width = pw;
        reduced.height = ph;
      }
      if (probe.width !== pw || probe.height !== ph) {
        probe.width = pw;
        probe.height = ph;
      }
      reducedContext.drawImage(canvas, 0, 0, pw, ph);
      probeContext.drawImage(reduced, 0, 0);
      const next: Record<string, BackdropHint> = { ...s.hints };
      let changed = false;
      for (const { id, rect } of hosts) {
        const x = Math.max(0, Math.floor(rect.left * scale));
        const y = Math.max(0, Math.floor(rect.top * scale));
        const w = Math.min(pw - x, Math.ceil(rect.width * scale));
        const h = Math.min(ph - y, Math.ceil(rect.height * scale));
        if (w <= 0 || h <= 0) continue;
        const data = probeContext.getImageData(x, y, w, h).data;
        let sum = 0;
        let sumSq = 0;
        let n = 0;
        const lin = (c: number): number => {
          const v = c / 255;
          return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
        };
        for (let i = 0; i < data.length; i += 4) {
          const yv = 0.2126 * lin(data[i] ?? 0) + 0.7152 * lin(data[i + 1] ?? 0) + 0.0722 * lin(data[i + 2] ?? 0);
          sum += yv;
          sumSq += yv * yv;
          n += 1;
        }
        if (n === 0) continue;
        const mean = sum / n;
        const spread = Math.sqrt(Math.max(0, sumSq / n - mean * mean));
        const hint: BackdropHint = {
          tone: mean > 0.3 ? "light" : mean < 0.08 ? "dark" : "mixed",
          luminance: Number(mean.toFixed(3)),
          complexity: Number(Math.min(1, spread / 0.12).toFixed(2)),
        };
        if (sameHint(next[id], hint)) continue;
        next[id] = hint;
        changed = true;
      }
      if (!changed) return;
      s.hints = next;
      live.current.onHints(next);
    };

    const api: MapApi = {
      zoomBy(factor) {
        const free = freeRect(false);
        const cx = (free.x0 + free.x1) / 2;
        const cy = (free.y0 + free.y1) / 2;
        zoomAt(cx, cy, factor);
      },
      fit() {
        s.follow = null;
        fitTo(networkBounds(), 180);
        paint();
      },
      showVehicle(fleet) {
        const vehicle = vehicleAt(fleet);
        if (vehicle === undefined) return;
        // Called after the selection has committed (App.tsx), so the card and the
        // capsule are already in their open boxes. Recentre only when the bus would
        // be hidden under them, under other chrome or off screen, and then in one
        // step: a dispatcher should not wait for a fly-over. Where the camera's bounds
        // stop the recentre short (a bus near the city's edge at a far zoom), step in
        // until it clears.
        const clear = (): boolean => {
          const [x, y] = vehicleScreen(s.camera, vehicle);
          return !hidden(x, y);
        };
        if (clear()) return;
        for (let i = 0; i < 8; i += 1) {
          centreOn(vehicle.at, true);
          if (clear() || s.camera.k >= K_MAX) break;
          s.camera = { ...s.camera, k: clampK(s.camera.k * 1.25) };
        }
        paint();
      },
      showRoute(routeId) {
        s.follow = null;
        fitTo(routeBounds(routeId), 400);
        paint();
      },
      showPoint(point) {
        s.follow = null;
        centreOn(point, false);
        paint();
      },
      follow(fleet) {
        s.follow = fleet;
        paint();
      },
    };
    live.current.apiRef.current = api;

    const zoomAt = (x: number, y: number, factor: number): void => {
      const { camera } = s;
      const k = clampK(camera.k * factor);
      const world = toWorld(camera, x, y);
      place({ k, x: world[0] - x / k, y: world[1] - y / k });
      paint();
    };

    const pick = (x: number, y: number): string | null => {
      let best: string | null = null;
      let bestD = 14;
      for (const marker of s.markers) {
        const d = Math.hypot(marker.x - x, marker.y - y);
        if (d <= bestD) {
          bestD = d;
          best = marker.fleet;
        }
      }
      return best;
    };

    const onPointerDown = (event: PointerEvent): void => {
      if (event.button !== 0) return;
      canvas.setPointerCapture(event.pointerId);
      s.drag = { x: event.clientX, y: event.clientY, cx: s.camera.x, cy: s.camera.y, moved: false, id: event.pointerId };
    };
    const onPointerMove = (event: PointerEvent): void => {
      const drag = s.drag;
      if (drag !== null && drag.id === event.pointerId) {
        const dx = event.clientX - drag.x;
        const dy = event.clientY - drag.y;
        if (!drag.moved && Math.hypot(dx, dy) < 4) return;
        drag.moved = true;
        s.follow = null;
        canvas.style.cursor = "grabbing";
        place({ ...s.camera, x: drag.cx - dx / s.camera.k, y: drag.cy - dy / s.camera.k });
        paint();
        return;
      }
      const hovered = pick(event.clientX, event.clientY);
      if (hovered !== s.hovered) {
        s.hovered = hovered;
        canvas.style.cursor = hovered === null ? "" : "pointer";
      }
    };
    const onPointerUp = (event: PointerEvent): void => {
      const drag = s.drag;
      if (drag === null || drag.id !== event.pointerId) return;
      s.drag = null;
      canvas.style.cursor = "";
      if (!drag.moved) live.current.onSelect(pick(event.clientX, event.clientY));
    };
    const onLeave = (): void => {
      s.hovered = null;
    };
    const onWheel = (event: WheelEvent): void => {
      event.preventDefault();
      const scale = event.deltaMode === 1 ? 16 : 1;
      zoomAt(event.clientX, event.clientY, Math.exp((-event.deltaY * scale) / 500));
    };
    const onResize = (): void => {
      s.fitted = false;
      paint();
    };

    canvas.addEventListener("pointerdown", onPointerDown);
    canvas.addEventListener("pointermove", onPointerMove);
    canvas.addEventListener("pointerup", onPointerUp);
    canvas.addEventListener("pointercancel", onPointerUp);
    canvas.addEventListener("pointerleave", onLeave);
    canvas.addEventListener("wheel", onWheel, { passive: false });
    window.addEventListener("resize", onResize);

    let last = performance.now();
    const unsubscribe = ticker.subscribe((dtMs) => {
      const now = performance.now();
      const dt = dtMs > 0 ? dtMs : now - last;
      last = now;
      advance(live.current.vehicles as Vehicle[], dt / 1000, live.current.stepped);
      paint();
      hintTick(now);
    });
    paint();

    return () => {
      unsubscribe();
      canvas.removeEventListener("pointerdown", onPointerDown);
      canvas.removeEventListener("pointermove", onPointerMove);
      canvas.removeEventListener("pointerup", onPointerUp);
      canvas.removeEventListener("pointercancel", onPointerUp);
      canvas.removeEventListener("pointerleave", onLeave);
      canvas.removeEventListener("wheel", onWheel);
      window.removeEventListener("resize", onResize);
      live.current.apiRef.current = null;
    };
  }, [ticker]);

  // Hand the pixels to the renderer. A no-op on a CSS-tier root.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (root === null || canvas === null) return;
    root.setBackdropTexture(TEXTURE_ID, { kind: "canvas", canvas });
    return () => root.setBackdropTexture(TEXTURE_ID, undefined);
  }, [root]);

  // A scheme or filter change repaints on the next frame through the base key; the
  // hints follow it, since the plane under every group just changed.
  return (
    <canvas
      ref={canvasRef}
      className="map"
      role="img"
      aria-label="Live map of Port Alder: eight bus routes and forty buses in service. Select a bus to open its details."
    />
  );
}

export { createVehicles };
