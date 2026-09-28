/**
 * The environment: the sky over the place at the page's time, drawn into one viewport-fixed WebGL
 * canvas that the runtime samples as its texture, and measured under each glass footprint.
 *
 * Three quantities stay apart (SKILL.md §4, the spatial register, condition 1): the SOURCE is these
 * painted pixels; the TONE INPUT each group declares is the level measured under that group's own
 * box, from a quarter-scale render of the same frame; and the DRAWN level behind a text line is
 * neither — the audit reads it from rendered pixels. The dimming layer the clear variant requires
 * is painted here, into the plane, and its strength under each host is derived from the undimmed
 * level under that host (`shared.ts`, `DIMMING`), so the declaration describes the composite the
 * glass actually samples, re-measured on a cadence, on every layout change and through a
 * time-lapse.
 *
 * The frame loop is the runtime's own (`root.subscribe`); there is no second animation frame.
 */

import { useGlassRoot, type BackdropHint } from "@vitreajs/vitrea-react";
import { useEffect, useLayoutEffect, useRef, type KeyboardEvent, type ReactNode } from "react";

import { bodyObjects, directionOfObject, observerFor, siderealTime, starObject, type Place, type SkyObject } from "./astro";
import { timeOf, type ClockMode } from "./clock";
import { DIMMING, dimmingFor, ENVIRONMENT_ID, featherFor, type HostShape } from "./shared";
import type { StarCatalog } from "./sky/catalog";
import { limbDirection } from "./sky/limb";
import { altAzOf, DEG, horizontalOf, project, separation, unproject, type Vec3, type View } from "./sky/projection";
import { SkyRenderer, type DiscDraw, type LabelDraw, type PointDraw, type Reading, type SkyFrame } from "./sky/renderer";

import figuresUrl from "./images/constellation-figures-2020-celestial-8k.webp";
import milkyWayUrl from "./images/milky-way-2020-celestial-4k.webp";

/** The view centre's altitude, and the vertical field the focal length is set from. */
const VIEW_ALT = 36 * DEG;
const VERTICAL_FIELD = 84 * DEG;
/** How far a click may fall from an object and still pick it, CSS px. */
const PICK_RADIUS = 18;
/** How far one arrow key turns the sky, and one with Shift. */
const TURN_STEP = 5 * DEG;
const TURN_STEP_LARGE = 20 * DEG;
/** How often the footprints are re-measured while the sky is changing, ms. */
const MEASURE_EVERY_MS = 240;
/** The Moon and the Sun are drawn at five times their angular size, as a planetarium does. */
const DISC_ENLARGEMENT = 5;
const DISC_ANGULAR_RADIUS = 0.26 * DEG;

export interface FootprintReading {
  readonly hint: BackdropHint;
  /** The dimming strength painted under this footprint. */
  readonly strength: number;
  readonly raw: Reading;
  readonly composite: Reading;
}

export interface EnvironmentProps {
  readonly place: Place;
  readonly clock: ClockMode;
  readonly catalog: StarCatalog | null;
  /** The view centre's azimuth, radians; the person pans it. */
  readonly azimuth: number;
  readonly onAzimuth: (azimuth: number) => void;
  readonly selected: SkyObject | undefined;
  readonly onSelect: (object: SkyObject | undefined) => void;
  readonly shapes: readonly HostShape[];
  readonly onReadings: (readings: Readonly<Record<string, FootprintReading>>) => void;
  /** The first frame has been painted and supplied, so the glass may materialise over it. */
  readonly onReady: () => void;
  readonly viewport: { readonly width: number; readonly height: number };
}

export function viewFor(azimuth: number, viewport: { readonly width: number; readonly height: number }): View {
  const focal = viewport.height / 2 / (2 * Math.tan(VERTICAL_FIELD / 4));
  return { az: azimuth, alt: VIEW_ALT, focal, width: viewport.width, height: viewport.height };
}

export function EnvironmentCanvas(props: EnvironmentProps): ReactNode {
  const root = useGlassRoot();
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const renderer = useRef<SkyRenderer | null>(null);
  const latest = useRef(props);
  latest.current = props;
  const loaded = useRef({ maps: false, stars: false, ready: false });
  const dirty = useRef(true);
  const sinceMeasure = useRef(Infinity);
  const measuredKey = useRef("");
  const strengths = useRef(new Map<string, number>());
  const lastReadings = useRef<Record<string, FootprintReading>>({});
  const drag = useRef<{ startX: number; startAz: number; moved: boolean } | null>(null);

  // The renderer and its assets.
  useLayoutEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null) return;
    let sky: SkyRenderer;
    try {
      sky = new SkyRenderer(canvas);
    } catch (error) {
      console.error(error);
      return;
    }
    renderer.current = sky;
    void sky.load(milkyWayUrl, figuresUrl).then(() => {
      loaded.current.maps = true;
      dirty.current = true;
    });
    return () => {
      sky.dispose();
      renderer.current = null;
    };
  }, []);

  useEffect(() => {
    const sky = renderer.current;
    const catalog = props.catalog;
    if (sky === null || catalog === null) return;
    sky.setStars(catalog);
    sky.setLabels(["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", ...catalog.nameOfHr.values()]);
    loaded.current.stars = true;
    dirty.current = true;
  }, [props.catalog]);

  useLayoutEffect(() => {
    const sky = renderer.current;
    if (sky === null) return;
    sky.resize(props.viewport.width, props.viewport.height, Math.min(2, window.devicePixelRatio || 1));
    dirty.current = true;
    sinceMeasure.current = Infinity;
  }, [props.viewport]);

  // The canvas is the texture: supplied once, re-imported by the runtime every frame it samples.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (root === null || canvas === null) return;
    root.setBackdropTexture(ENVIRONMENT_ID, { kind: "canvas", canvas });
    return () => root.setBackdropTexture(ENVIRONMENT_ID, undefined);
  }, [root]);

  // Anything the frame is built from changing marks it dirty.
  useEffect(() => {
    dirty.current = true;
    sinceMeasure.current = Infinity;
  }, [props.place, props.clock, props.azimuth, props.selected, props.shapes]);

  // The frame loop.
  useEffect(() => {
    if (root === null) return;
    return root.subscribe(({ deltaMs }) => {
      const sky = renderer.current;
      const { place, clock, catalog, azimuth, selected, shapes, viewport } = latest.current;
      if (sky === null || catalog === null || !loaded.current.maps || !loaded.current.stars) return;
      const live = clock.kind !== "pinned";
      if (!dirty.current && !live) return;
      const time = timeOf(clock, Date.now());
      const view = viewFor(azimuth, viewport);
      const built = buildFrame(place, time, view, selected);
      sinceMeasure.current += deltaMs;
      const layoutKey = shapes.map((s) => `${s.id}:${String(Math.round(s.box.x))},${String(Math.round(s.box.y))},${String(Math.round(s.box.width))},${String(Math.round(s.box.height))}`).join("|");
      const measureKey = `${layoutKey}|${place.id}|${String(Math.round(time / 30_000))}|${azimuth.toFixed(3)}`;
      let dims = dimsFor(shapes, strengths.current);
      if (sinceMeasure.current >= MEASURE_EVERY_MS && measureKey !== measuredKey.current) {
        sinceMeasure.current = 0;
        measuredKey.current = measureKey;
        const boxes = shapes.map((s) => s.box);
        const raw = sky.measure({ ...built.frame, dims: [] }, boxes, false);
        shapes.forEach((shape, index) => {
          const reading = raw[index];
          if (reading !== undefined) strengths.current.set(shape.id, dimmingFor(reading.luminance));
        });
        dims = dimsFor(shapes, strengths.current);
        const composite = sky.measure({ ...built.frame, dims }, boxes, true);
        const readings: Record<string, FootprintReading> = {};
        let changed = false;
        shapes.forEach((shape, index) => {
          const r = raw[index];
          const c = composite[index];
          if (r === undefined || c === undefined) return;
          const strength = strengths.current.get(shape.id) ?? DIMMING.floor;
          const reading: FootprintReading = { hint: hintFrom(c), strength, raw: r, composite: c };
          readings[shape.id] = reading;
          const was = lastReadings.current[shape.id];
          if (
            was === undefined ||
            Math.abs((was.hint.luminance ?? 0) - (reading.hint.luminance ?? 0)) > 0.002 ||
            was.hint.tone !== reading.hint.tone ||
            Math.abs(was.strength - strength) > 0.01
          ) {
            changed = true;
          }
        });
        if (changed || Object.keys(readings).length !== Object.keys(lastReadings.current).length) {
          lastReadings.current = readings;
          latest.current.onReadings(readings);
        }
      }
      sky.render({ ...built.frame, dims });
      dirty.current = false;
      if (!loaded.current.ready) {
        loaded.current.ready = true;
        latest.current.onReady();
      }
    });
  }, [root]);

  // Panning and picking on the sky itself: a drag turns the view, a click selects.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (canvas === null) return;
    const onDown = (event: PointerEvent): void => {
      if (event.button !== 0) return;
      drag.current = { startX: event.clientX, startAz: latest.current.azimuth, moved: false };
      canvas.setPointerCapture(event.pointerId);
    };
    const onMove = (event: PointerEvent): void => {
      const d = drag.current;
      if (d === null) return;
      const dx = event.clientX - d.startX;
      if (Math.abs(dx) > 3) d.moved = true;
      if (!d.moved) return;
      const view = viewFor(latest.current.azimuth, latest.current.viewport);
      // A pixel of drag is the angle it subtends at the view centre.
      latest.current.onAzimuth(d.startAz - dx / view.focal);
    };
    const onUp = (event: PointerEvent): void => {
      const d = drag.current;
      drag.current = null;
      if (d === null || d.moved) return;
      const { place, clock, catalog, azimuth, viewport, selected } = latest.current;
      if (catalog === null) return;
      const rect = canvas.getBoundingClientRect();
      const picked = pick(event.clientX - rect.left, event.clientY - rect.top, place, timeOf(clock, Date.now()), viewFor(azimuth, viewport), catalog);
      latest.current.onSelect(picked?.id === selected?.id ? undefined : picked);
    };
    canvas.addEventListener("pointerdown", onDown);
    canvas.addEventListener("pointermove", onMove);
    canvas.addEventListener("pointerup", onUp);
    canvas.addEventListener("pointercancel", () => {
      drag.current = null;
    });
    return () => {
      canvas.removeEventListener("pointerdown", onDown);
      canvas.removeEventListener("pointermove", onMove);
      canvas.removeEventListener("pointerup", onUp);
    };
  }, []);

  /*
   * The keyboard's way to turn the sky, beside the pointer's drag: the canvas takes focus and the
   * Left and Right arrows turn the view as a drag would, right toward increasing azimuth. It is an
   * `application` so a screen reader passes the arrows through rather than reading by them.
   */
  const onKeyDown = (event: KeyboardEvent<HTMLCanvasElement>): void => {
    if (event.key !== "ArrowLeft" && event.key !== "ArrowRight") return;
    event.preventDefault();
    const step = event.shiftKey ? TURN_STEP_LARGE : TURN_STEP;
    latest.current.onAzimuth(latest.current.azimuth + (event.key === "ArrowRight" ? step : -step));
  };

  return (
    <canvas
      ref={canvasRef}
      className="sky"
      role="application"
      tabIndex={0}
      onKeyDown={onKeyDown}
      aria-label={`The sky over ${props.place.name}: stars, the Milky Way, the Moon and the planets as they stand now. Drag, or press the Left and Right arrow keys, to turn it by 5° (with Shift, 20°); click a star or planet to read about it.`}
    />
  );
}

function dimsFor(shapes: readonly HostShape[], strengths: ReadonlyMap<string, number>): SkyFrame["dims"] {
  return shapes.map((shape) => ({
    x: shape.box.x,
    y: shape.box.y,
    width: shape.box.width,
    height: shape.box.height,
    radius: shape.radius,
    strength: strengths.get(shape.id) ?? DIMMING.floor,
    feather: featherFor(Math.min(shape.box.width, shape.box.height)),
  }));
}

/**
 * The declaration a group makes from its footprint. The tone names the pole the measured level is
 * on; the level itself is the measurement (the runtime's own statistic: the encoded mean, decoded).
 */
export function hintFrom(reading: Reading): BackdropHint {
  return { tone: reading.luminance >= 0.18 ? "light" : "dark", luminance: Math.round(reading.luminance * 1000) / 1000 };
}

export interface BuiltFrame {
  readonly frame: SkyFrame;
  readonly bodies: readonly SkyObject[];
  readonly lst: number;
}

/** Everything the renderer needs for one instant, from the model. */
export function buildFrame(place: Place, time: number, view: View, selected: SkyObject | undefined): BuiltFrame {
  const date = new Date(time);
  const observer = { latitude: place.latitude, longitude: place.longitude };
  const lst = siderealTime(date, place.longitude);
  const latitude = place.latitude * DEG;
  const bodies = bodyObjects(date, observerFor(observer));
  const sun = bodies.find((b) => b.kind === "sun") as SkyObject;
  const moon = bodies.find((b) => b.kind === "moon") as SkyObject;
  const sunDir = directionOfObject(sun, lst, latitude);
  const moonDir = directionOfObject(moon, lst, latitude);
  const sunAltAz = altAzOf(sunDir);
  const moonAltAz = altAzOf(moonDir);

  const planets: PointDraw[] = bodies
    .filter((b) => b.kind === "planet")
    .map((b) => ({ ra: b.ra, dec: b.dec, mag: b.mag, bv: b.bv }));

  const discRadius = DISC_ANGULAR_RADIUS * DISC_ENLARGEMENT * view.focal;
  const discs: DiscDraw[] = [];
  const labels: LabelDraw[] = [];
  if (moonAltAz.alt > -2 * DEG) {
    // The lit limb points at the Sun along the great circle between them (`sky/limb.ts`), and
    // the Sun–Moon–Earth angle gives the light in the disc's own frame.
    const moonPx = project(moonDir, view);
    const [dx, dy] = limbDirection(sunDir, moonDir, view);
    const phase = separation(sunDir, moonDir);
    // The phase angle at the Moon is the supplement of the Sun–Moon elongation, near enough for a
    // disc; the Sun is far compared with the Moon.
    const psi = Math.PI - phase;
    const illuminated = (1 + Math.cos(psi)) / 2;
    discs.push({
      direction: moonDir,
      radius: discRadius,
      light: [Math.sin(psi) * dx, Math.sin(psi) * dy, Math.cos(psi)],
      colour: [0.93, 0.91, 0.87],
      glow: 0.06 + 0.32 * illuminated,
      sun: false,
    });
    if (moonPx !== undefined) labels.push({ text: "Moon", x: moonPx[0] + discRadius + 8, y: moonPx[1], alpha: 0.85 });
  }
  if (sunAltAz.alt > -2 * DEG) {
    discs.push({ direction: sunDir, radius: discRadius, light: [0, 0, 1], colour: [1, 0.96, 0.88], glow: 1.4, sun: true });
    const sunPx = project(sunDir, view);
    if (sunPx !== undefined) labels.push({ text: "Sun", x: sunPx[0] + discRadius + 8, y: sunPx[1], alpha: 0.85 });
  }
  const starVisibility = 1 - smoothstep(-12 * DEG, -1 * DEG, sunAltAz.alt);
  for (const body of bodies) {
    if (body.kind !== "planet") continue;
    const dir = directionOfObject(body, lst, latitude);
    if (dir[2] < 0.01) continue;
    const px = project(dir, view);
    if (px === undefined) continue;
    labels.push({ text: body.name, x: px[0] + 9, y: px[1], alpha: 0.8 * starVisibility });
  }
  let ring: SkyFrame["ring"];
  if (selected !== undefined) {
    // A body moves against the stars: the selection holds the position it had when it was chosen,
    // so the ring stands on this frame's position of the same body, by id.
    const target = selected.kind === "star" ? selected : (bodies.find((b) => b.id === selected.id) ?? selected);
    const dir = directionOfObject(target, lst, latitude);
    const px = project(dir, view);
    if (px !== undefined && dir[2] > -0.02) {
      const r = target.kind === "moon" || target.kind === "sun" ? discRadius + 8 : 13;
      ring = { x: px[0], y: px[1], r, alpha: 0.75 };
      if (target.kind === "star") labels.push({ text: target.name, x: px[0] + r + 6, y: px[1], alpha: 0.9 });
    }
  }
  const frame: SkyFrame = {
    view,
    latitude,
    lst,
    sunAlt: sunAltAz.alt,
    sunAz: sunAltAz.az,
    exposure: 0.42,
    figures: 0.03,
    planets,
    discs,
    labels,
    ring,
    dims: [],
  };
  return { frame, bodies, lst };
}

function smoothstep(a: number, b: number, x: number): number {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
}

/** The catalogue star, planet, Moon or Sun nearest a click, within the pick radius. */
function pick(x: number, y: number, place: Place, time: number, view: View, catalog: StarCatalog): SkyObject | undefined {
  const date = new Date(time);
  const lst = siderealTime(date, place.longitude);
  const latitude = place.latitude * DEG;
  const target = unproject(x, y, view);
  if (target[2] < 0) return undefined;
  let best: SkyObject | undefined;
  let bestDistance = PICK_RADIUS;
  const consider = (object: SkyObject, dir: Vec3): void => {
    if (dir[2] < 0) return;
    const px = project(dir, view);
    if (px === undefined) return;
    const distance = Math.hypot(px[0] - x, px[1] - y);
    if (distance < bestDistance) {
      bestDistance = distance;
      best = object;
    }
  };
  for (const body of bodyObjects(date, observerFor(place))) consider(body, directionOfObject(body, lst, latitude));
  for (let i = 0; i < catalog.count; i += 1) {
    if ((catalog.mag[i] as number) > 4.2 && !catalog.nameOfHr.has(catalog.hr[i] as number)) break;
    consider(starObject(catalog, i), horizontalOf(catalog.ra[i] as number, catalog.dec[i] as number, lst, latitude));
  }
  return best;
}
