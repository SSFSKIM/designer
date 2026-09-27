/**
 * Painting Port Alder.
 *
 * Two layers. The basemap (land, districts and their street grids, parks, water,
 * piers, rail, roads, the closure, route lines, stops and labels) is painted into an
 * offscreen canvas whenever the camera, the scheme, the size or a filter changes. The
 * live layer (forty vehicles, their exception tags, hover and selection) is painted
 * over it every frame. Both land in the one canvas the glass samples, so every
 * frequency the lens bends is painted, never laid over in CSS (DESIGN.md, plane).
 *
 * The cartography follows the control-room rule the page is built on: the normal
 * state is quiet and colour is reserved for the abnormal. Routes carry their hue;
 * only an exception carries a tag, and its tag says in words what is wrong.
 */
import {
  BREAKWATER,
  BRIDGE_LABELS,
  CAMERAS,
  CHANNEL,
  CLOSURE,
  DISTRICTS,
  HARBOUR,
  ISOBATHS,
  LAKES,
  MARINA,
  PARKS,
  PIERS,
  RAIL,
  RIVER,
  ROADS,
  ROUTES,
  WATER_LABELS,
  CENTRAL_STATION,
  type Point,
  type Severity,
} from "./data";
import { adherenceOf, GEOMETRY, tagOf, type Adherence, type Vehicle } from "./sim";

export type Scheme = "light" | "dark";

/** World top-left in metres and pixels per metre. */
export interface Camera {
  x: number;
  y: number;
  k: number;
}

export interface Filters {
  /** Empty: every route. */
  readonly routes: ReadonlySet<string>;
  readonly adherence: "all" | Adherence;
}

// ---------------------------------------------------------------------------------
// Colour

/** OKLCH to an sRGB hex string, clamped to the gamut. */
export function oklch(l: number, c: number, h: number): string {
  const hr = (h * Math.PI) / 180;
  const a = c * Math.cos(hr);
  const b = c * Math.sin(hr);
  const l_ = (l + 0.3963377774 * a + 0.2158037573 * b) ** 3;
  const m_ = (l - 0.1055613458 * a - 0.0638541728 * b) ** 3;
  const s_ = (l - 0.0894841775 * a - 1.291485548 * b) ** 3;
  const lin = [
    4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
    -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
    -0.0041960863 * l_ - 0.7034186147 * m_ + 1.707614701 * s_,
  ];
  const hex = lin
    .map((v) => {
      const x = Math.max(0, Math.min(1, v));
      const e = x <= 0.0031308 ? 12.92 * x : 1.055 * x ** (1 / 2.4) - 0.055;
      return Math.round(e * 255)
        .toString(16)
        .padStart(2, "0");
    })
    .join("");
  return `#${hex}`;
}

export function routeColour(hue: number, scheme: Scheme): string {
  return scheme === "light" ? oklch(0.555, 0.145, hue) : oklch(0.76, 0.125, hue);
}

interface Palette {
  land: string;
  wash: (density: number) => string;
  street: string;
  collector: string;
  collectorCasing: string;
  arterial: string;
  arterialCasing: string;
  water: string;
  waterEdge: string;
  park: string;
  parkEdge: string;
  pier: string;
  pierEdge: string;
  rail: string;
  closure: string;
  district: string;
  street_label: string;
  water_label: string;
  isobath: string;
  channel: string;
  sounding: string;
  tree: string;
  halo: string;
  routeCasing: string;
  stop: string;
  outline: string;
  ink: string;
  inkOn: string;
  camera: string;
}

const LIGHT: Palette = {
  land: "#e9ebee",
  wash: (d) => `rgba(52, 62, 78, ${(0.035 + d * 0.075).toFixed(3)})`,
  street: "#fbfcfd",
  collector: "#ffffff",
  collectorCasing: "#cfd4da",
  arterial: "#ffffff",
  arterialCasing: "#c3c9d1",
  water: "#b4cde0",
  waterEdge: "#9ab7ce",
  park: "#cfe2c8",
  parkEdge: "#b7d0ae",
  pier: "#dde0e4",
  pierEdge: "#a9b7c3",
  rail: "#98a1ab",
  closure: "#8d949c",
  district: "#6f7985",
  street_label: "#7b848f",
  water_label: "#55809f",
  isobath: "#9bb9d0",
  channel: "#7d9db8",
  sounding: "#93b2ca",
  tree: "#a6c59b",
  halo: "rgba(236, 238, 241, 0.92)",
  routeCasing: "#ffffff",
  stop: "#ffffff",
  outline: "#ffffff",
  ink: "#1b2129",
  inkOn: "#ffffff",
  camera: "#39424d",
};

const DARK: Palette = {
  land: "#15181c",
  wash: (d) => `rgba(150, 165, 185, ${(0.02 + d * 0.06).toFixed(3)})`,
  street: "#282d34",
  collector: "#333941",
  collectorCasing: "#0f1114",
  arterial: "#3d454f",
  arterialCasing: "#0c0e11",
  water: "#0c1824",
  waterEdge: "#1b2c3c",
  park: "#15241a",
  parkEdge: "#1d3124",
  pier: "#1d2126",
  pierEdge: "#2d3945",
  rail: "#4d5661",
  closure: "#6d757e",
  district: "#8a94a0",
  street_label: "#76808b",
  water_label: "#5f86a6",
  isobath: "#172838",
  channel: "#2a4057",
  sounding: "#2b445c",
  tree: "#2b4735",
  halo: "rgba(21, 24, 28, 0.9)",
  routeCasing: "#0e1013",
  stop: "#15181c",
  outline: "#0e1013",
  ink: "#eef1f4",
  inkOn: "#101317",
  camera: "#c9d1da",
};

export const PALETTES: Record<Scheme, Palette> = { light: LIGHT, dark: DARK };

/** Alarm colours: the only saturated colours outside the route palette. */
export const SEVERITY: Record<Severity, { fill: Record<Scheme, string>; text: Record<Scheme, string> }> = {
  critical: { fill: { light: "#c42b33", dark: "#e5484d" }, text: { light: "#ffffff", dark: "#ffffff" } },
  warning: { fill: { light: "#f2b134", dark: "#f5b83d" }, text: { light: "#2a1c00", dark: "#2a1c00" } },
  info: { fill: { light: "#2a313a", dark: "#dfe4ea" }, text: { light: "#ffffff", dark: "#111418" } },
};

const FONT = `-apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", system-ui, sans-serif`;

// ---------------------------------------------------------------------------------
// Geometry helpers

const sx = (cam: Camera, p: Point): number => (p[0] - cam.x) * cam.k;
const sy = (cam: Camera, p: Point): number => (p[1] - cam.y) * cam.k;

export function toScreen(cam: Camera, p: Point): Point {
  return [sx(cam, p), sy(cam, p)];
}

export function toWorld(cam: Camera, x: number, y: number): Point {
  return [cam.x + x / cam.k, cam.y + y / cam.k];
}

function tracePolygon(ctx: CanvasRenderingContext2D, cam: Camera, polygon: readonly Point[]): void {
  ctx.beginPath();
  polygon.forEach((p, i) => (i === 0 ? ctx.moveTo(sx(cam, p), sy(cam, p)) : ctx.lineTo(sx(cam, p), sy(cam, p))));
  ctx.closePath();
}

function tracePolyline(ctx: CanvasRenderingContext2D, points: readonly Point[]): void {
  ctx.beginPath();
  points.forEach((p, i) => (i === 0 ? ctx.moveTo(p[0], p[1]) : ctx.lineTo(p[0], p[1])));
}

/** Offset a screen-space polyline sideways by `d` px, mitred at each vertex. */
export function offsetPolyline(points: readonly Point[], d: number): Point[] {
  if (d === 0) return [...points];
  return points.map((p, i) => {
    const prev = points[i - 1];
    const next = points[i + 1];
    const n1 = prev === undefined ? undefined : normal(prev, p);
    const n2 = next === undefined ? undefined : normal(p, next);
    let nx = (n1?.[0] ?? 0) + (n2?.[0] ?? 0);
    let ny = (n1?.[1] ?? 0) + (n2?.[1] ?? 0);
    const len = Math.hypot(nx, ny) || 1;
    nx /= len;
    ny /= len;
    // Mitre length, capped so a sharp turn does not spike.
    const cos = n1 !== undefined && n2 !== undefined ? nx * n1[0] + ny * n1[1] : 1;
    const scale = d / Math.max(0.5, cos);
    return [p[0] + nx * scale, p[1] + ny * scale];
  });
}

function normal(a: Point, b: Point): Point {
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const len = Math.hypot(dx, dy) || 1;
  return [-dy / len, dx / len];
}

/** A deterministic hash in 0..1. */
function hash2(a: number, b: number): number {
  const x = Math.sin(a * 12.9898 + b * 78.233) * 43758.5453;
  return x - Math.floor(x);
}

export const SLOT_PX = 3.4;

export function routeScreenPath(cam: Camera, routeId: string): Point[] {
  const geometry = GEOMETRY.get(routeId);
  if (geometry === undefined) return [];
  return offsetPolyline(
    geometry.points.map((p) => toScreen(cam, p)),
    geometry.route.slot * SLOT_PX,
  );
}

// ---------------------------------------------------------------------------------
// The flat fills' own fine frequency

/**
 * Everywhere else the city carries a street web, but water and parks are flat fills,
 * and at a close zoom a whole control fits inside one: glass over a flat field, which
 * has nothing to bend (SKILL.md, the live plane). A chart and a park plan both answer
 * that with marks of their own, so the water carries depth soundings and the parks
 * carry tree marks, on a lattice fixed to the world whose pitch doubles as the camera
 * zooms out. On screen the pitch therefore stays between 24 and 48 px at every zoom
 * the camera allows (MapPlane.tsx, the camera's bounds), which is finer than the long
 * side of every control that floats over the map.
 */
const LATTICE_MIN_PX = 24;

function boxOf(points: readonly Point[]): Box {
  let x0 = Infinity;
  let y0 = Infinity;
  let x1 = -Infinity;
  let y1 = -Infinity;
  for (const [x, y] of points) {
    x0 = Math.min(x0, x);
    y0 = Math.min(y0, y);
    x1 = Math.max(x1, x);
    y1 = Math.max(y1, y);
  }
  return { x0, y0, x1, y1 };
}

function inBox(box: Box, x: number, y: number): boolean {
  return x >= box.x0 && x <= box.x1 && y >= box.y0 && y <= box.y1;
}

function inPolygon(polygon: readonly Point[], x: number, y: number): boolean {
  let inside = false;
  for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i, i += 1) {
    const a = polygon[i];
    const b = polygon[j];
    if (a === undefined || b === undefined) continue;
    if (a[1] > y !== b[1] > y && x < ((b[0] - a[0]) * (y - a[1])) / (b[1] - a[1]) + a[0]) inside = !inside;
  }
  return inside;
}

const HARBOUR_BOX = boxOf(HARBOUR);
const PARK_BOXES = PARKS.map((park) => ({ polygon: park.polygon, box: boxOf(park.polygon) }));

/** Inside the river's band, a little in from either bank so a mark never sits on the shore. */
function inRiver(x: number, y: number): boolean {
  for (let i = 1; i < RIVER.length; i += 1) {
    const a = RIVER[i - 1];
    const b = RIVER[i];
    if (a === undefined || b === undefined) continue;
    const dx = b[0] - a[0];
    const dy = b[1] - a[1];
    const t = Math.max(0, Math.min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy)));
    const half = (a[2] + (b[2] - a[2]) * t) / 2;
    if (Math.hypot(x - (a[0] + dx * t), y - (a[1] + dy * t)) < half * 0.7) return true;
  }
  return false;
}

function inLake(x: number, y: number): boolean {
  return LAKES.some((lake) => {
    const cx = x - lake.center[0];
    const cy = y - lake.center[1];
    const c = Math.cos(-lake.rot);
    const s = Math.sin(-lake.rot);
    const u = (cx * c - cy * s) / (lake.rx * 0.8);
    const v = (cx * s + cy * c) / (lake.ry * 0.8);
    return u * u + v * v < 1;
  });
}

function paintFlatMarks(ctx: CanvasRenderingContext2D, cam: Camera, pal: Palette, width: number, height: number): void {
  let pitch = 40;
  while (pitch * cam.k < LATTICE_MIN_PX) pitch *= 2;
  const [wx0, wy0] = toWorld(cam, 0, 0);
  const [wx1, wy1] = toWorld(cam, width, height);
  ctx.font = "600 8.5px -apple-system, BlinkMacSystemFont, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  const trees = new Path2D();
  for (let i = Math.floor(wx0 / pitch) - 1; i <= Math.ceil(wx1 / pitch); i += 1) {
    for (let j = Math.floor(wy0 / pitch) - 1; j <= Math.ceil(wy1 / pitch); j += 1) {
      // Jittered inside its cell, and seeded by the pitch, so each level is its own
      // stable pattern rather than a grid.
      const h = hash2(i * 7.1 + pitch, j * 3.7);
      const x = (i + 0.2 + 0.6 * h) * pitch;
      const y = (j + 0.2 + 0.6 * hash2(j * 5.3 - pitch, i * 1.9)) * pitch;
      const sxp = (x - cam.x) * cam.k;
      const syp = (y - cam.y) * cam.k;
      let depth = 0;
      if (inBox(HARBOUR_BOX, x, y) && inPolygon(HARBOUR, x, y)) {
        // Deeper away from the northern shore, as the isobaths run.
        depth = Math.round(Math.min(48, 3 + Math.max(0, y - 2640) / 320 + h * 4));
      } else if (inRiver(x, y)) {
        depth = Math.round(2 + h * 5);
      } else if (inLake(x, y)) {
        depth = Math.round(1 + h * 4);
      }
      if (depth > 0) {
        ctx.fillStyle = pal.sounding;
        ctx.fillText(String(depth), sxp, syp);
        continue;
      }
      if (PARK_BOXES.some(({ polygon, box }) => inBox(box, x, y) && inPolygon(polygon, x, y))) {
        trees.moveTo(sxp + 1.6, syp);
        trees.arc(sxp, syp, 1.6, 0, Math.PI * 2);
      }
    }
  }
  ctx.fillStyle = pal.tree;
  ctx.fill(trees);
  ctx.textAlign = "start";
  ctx.textBaseline = "alphabetic";
}

/**
 * The extent of the mapped city: the districts and the harbour together tile it,
 * and outside it the plane is the bare land fill. The camera never shows past it
 * (MapPlane.tsx), so no control can float over that fill.
 */
export function coverageBounds(): Box {
  return boxOf([...DISTRICTS.flatMap((district) => district.polygon), ...HARBOUR]);
}

// ---------------------------------------------------------------------------------
// The basemap

export function paintBase(
  ctx: CanvasRenderingContext2D,
  width: number,
  height: number,
  dpr: number,
  cam: Camera,
  scheme: Scheme,
  filters: Filters,
): void {
  const pal = PALETTES[scheme];
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  ctx.fillStyle = pal.land;
  ctx.fillRect(0, 0, width, height);
  ctx.lineCap = "round";
  ctx.lineJoin = "round";

  // Districts: a density wash, then the street web on each district's own grid.
  for (const [index, district] of DISTRICTS.entries()) {
    tracePolygon(ctx, cam, district.polygon);
    ctx.fillStyle = pal.wash(district.density);
    ctx.fill();
    ctx.save();
    tracePolygon(ctx, cam, district.polygon);
    ctx.clip();
    paintGrid(ctx, cam, district.angle, district.spacing, index, width, height, pal);
    ctx.restore();
  }

  // Parks cover the grid.
  for (const park of PARKS) {
    tracePolygon(ctx, cam, park.polygon);
    ctx.fillStyle = pal.park;
    ctx.fill();
    ctx.strokeStyle = pal.parkEdge;
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  // Water: the harbour, the river and the lakes, each with a shore line.
  tracePolygon(ctx, cam, HARBOUR);
  ctx.fillStyle = pal.water;
  ctx.fill();
  ctx.strokeStyle = pal.waterEdge;
  ctx.lineWidth = 1.2;
  ctx.stroke();
  for (const pass of [0, 1]) {
    for (let i = 1; i < RIVER.length; i += 1) {
      const a = RIVER[i - 1];
      const b = RIVER[i];
      if (a === undefined || b === undefined) continue;
      ctx.beginPath();
      ctx.moveTo(sx(cam, [a[0], a[1]]), sy(cam, [a[0], a[1]]));
      ctx.lineTo(sx(cam, [b[0], b[1]]), sy(cam, [b[0], b[1]]));
      ctx.lineWidth = ((a[2] + b[2]) / 2) * cam.k + (pass === 0 ? 2.4 : 0);
      ctx.strokeStyle = pass === 0 ? pal.waterEdge : pal.water;
      ctx.stroke();
    }
  }
  for (const lake of LAKES) {
    ctx.beginPath();
    ctx.ellipse(sx(cam, lake.center), sy(cam, lake.center), lake.rx * cam.k, lake.ry * cam.k, lake.rot, 0, Math.PI * 2);
    ctx.fillStyle = pal.water;
    ctx.fill();
    ctx.strokeStyle = pal.waterEdge;
    ctx.lineWidth = 1.2;
    ctx.stroke();
  }

  // The harbour's chart: depth contours, the dredged channel and its buoys.
  ctx.save();
  tracePolygon(ctx, cam, HARBOUR);
  ctx.clip();
  ctx.strokeStyle = pal.isobath;
  ctx.lineWidth = 1;
  for (const line of ISOBATHS) {
    tracePolyline(ctx, line.map((p) => toScreen(cam, p)));
    ctx.stroke();
  }
  const channel = CHANNEL.map((p) => toScreen(cam, p));
  ctx.setLineDash([6, 4]);
  ctx.strokeStyle = pal.channel;
  for (const side of [-1, 1]) {
    tracePolyline(ctx, offsetPolyline(channel, side * 90 * cam.k));
    ctx.stroke();
  }
  ctx.setLineDash([]);
  for (const side of [-1, 1]) {
    const edge = offsetPolyline(channel, side * 90 * cam.k);
    for (let i = 1; i < edge.length; i += 1) {
      const a = edge[i - 1];
      const b = edge[i];
      if (a === undefined || b === undefined) continue;
      const steps = Math.max(1, Math.floor(Math.hypot(b[0] - a[0], b[1] - a[1]) / 46));
      for (let j = 0; j < steps; j += 1) {
        const t = j / steps;
        ctx.beginPath();
        ctx.arc(a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, 1.8, 0, Math.PI * 2);
        ctx.fillStyle = pal.channel;
        ctx.fill();
      }
    }
  }
  ctx.restore();

  // Soundings on the water and tree marks in the parks: the fine frequency of the
  // city's only flat fills.
  paintFlatMarks(ctx, cam, pal, width, height);

  // The breakwater and the marina.
  tracePolyline(ctx, BREAKWATER.map((p) => toScreen(cam, p)));
  ctx.strokeStyle = pal.pierEdge;
  ctx.lineWidth = Math.max(3, 55 * cam.k) + 2;
  ctx.stroke();
  ctx.strokeStyle = pal.pier;
  ctx.lineWidth = Math.max(3, 55 * cam.k);
  ctx.stroke();
  {
    const [top, bottom] = MARINA.spine;
    const a = toScreen(cam, top);
    const b = toScreen(cam, bottom);
    ctx.beginPath();
    ctx.moveTo(a[0], a[1]);
    ctx.lineTo(b[0], b[1]);
    for (let i = 1; i <= MARINA.fingers; i += 1) {
      const t = i / (MARINA.fingers + 1);
      const x = a[0] + (b[0] - a[0]) * t;
      const y = a[1] + (b[1] - a[1]) * t;
      ctx.moveTo(x - MARINA.length * cam.k, y);
      ctx.lineTo(x + MARINA.length * cam.k, y);
    }
    ctx.strokeStyle = pal.pierEdge;
    ctx.lineWidth = 1.2;
    ctx.lineCap = "butt";
    ctx.stroke();
    ctx.lineCap = "round";
  }

  // Piers.
  for (const pier of PIERS) {
    const [dx, dy] = pier.dir;
    const len = Math.hypot(dx, dy) || 1;
    const ux = dx / len;
    const uy = dy / len;
    const hw = pier.width / 2;
    const polygon: Point[] = [
      [pier.at[0] - uy * hw, pier.at[1] + ux * hw],
      [pier.at[0] + ux * pier.length - uy * hw, pier.at[1] + uy * pier.length + ux * hw],
      [pier.at[0] + ux * pier.length + uy * hw, pier.at[1] + uy * pier.length - ux * hw],
      [pier.at[0] + uy * hw, pier.at[1] - ux * hw],
    ];
    tracePolygon(ctx, cam, polygon);
    ctx.fillStyle = pal.pier;
    ctx.fill();
    ctx.strokeStyle = pal.pierEdge;
    ctx.lineWidth = 1;
    ctx.stroke();
  }

  // Rail: a line with sleepers.
  const rail = RAIL.map((p) => toScreen(cam, p));
  tracePolyline(ctx, rail);
  ctx.strokeStyle = pal.rail;
  ctx.lineWidth = 1.3;
  ctx.stroke();
  ctx.setLineDash([1.3, 5]);
  ctx.lineWidth = 5;
  ctx.lineCap = "butt";
  tracePolyline(ctx, rail);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.lineCap = "round";

  // Roads: collectors, then arterials, each casing first.
  for (const rank of [1, 2] as const) {
    const roads = ROADS.filter((road) => road.rank === rank);
    const casing = rank === 2 ? pal.arterialCasing : pal.collectorCasing;
    const fill = rank === 2 ? pal.arterial : pal.collector;
    const w = rank === 2 ? 3.4 : 2;
    for (const [colour, lw] of [
      [casing, w + 1.8],
      [fill, w],
    ] as const) {
      ctx.strokeStyle = colour;
      ctx.lineWidth = lw;
      for (const road of roads) {
        tracePolyline(ctx, road.points.map((p) => toScreen(cam, p)));
        ctx.stroke();
      }
    }
  }

  // The closed section of Kingsway: the road stays, crossed out as closed.
  const closure = CLOSURE.map((p) => toScreen(cam, p));
  tracePolyline(ctx, closure);
  ctx.strokeStyle = pal.closure;
  ctx.lineWidth = 3.4;
  ctx.setLineDash([4, 3]);
  ctx.lineCap = "butt";
  ctx.stroke();
  ctx.setLineDash([]);
  for (const end of closure) {
    const [ax, ay] = closure[0] ?? end;
    const [bx, by] = closure[1] ?? end;
    const len = Math.hypot(bx - ax, by - ay) || 1;
    const nx = -(by - ay) / len;
    const ny = (bx - ax) / len;
    ctx.beginPath();
    ctx.moveTo(end[0] - nx * 6, end[1] - ny * 6);
    ctx.lineTo(end[0] + nx * 6, end[1] + ny * 6);
    ctx.strokeStyle = SEVERITY.critical.fill[scheme];
    ctx.lineWidth = 2.4;
    ctx.stroke();
  }
  ctx.lineCap = "round";

  // Route lines, dimmed where a filter leaves them out.
  const routeFiltered = filters.routes.size > 0;
  const ordered = [...ROUTES].sort(
    (a, b) => Number(filters.routes.has(a.id)) - Number(filters.routes.has(b.id)),
  );
  for (const route of ordered) {
    const shown = !routeFiltered || filters.routes.has(route.id);
    const path = routeScreenPath(cam, route.id);
    ctx.globalAlpha = shown ? 1 : 0.28;
    tracePolyline(ctx, path);
    ctx.strokeStyle = pal.routeCasing;
    ctx.lineWidth = 6.2;
    ctx.stroke();
    tracePolyline(ctx, path);
    ctx.strokeStyle = routeColour(route.hue, scheme);
    ctx.lineWidth = 3.2;
    ctx.stroke();
    ctx.globalAlpha = 1;
  }

  // Stops, once the scale can carry them.
  if (cam.k >= 0.09) {
    for (const route of ROUTES) {
      const geometry = GEOMETRY.get(route.id);
      if (geometry === undefined) continue;
      const shown = !routeFiltered || filters.routes.has(route.id);
      ctx.globalAlpha = shown ? 1 : 0.28;
      const path = routeScreenPath(cam, route.id);
      for (const at of geometry.stopAt) {
        const p = alongScreen(path, geometry.cumulative, at);
        ctx.beginPath();
        ctx.arc(p[0], p[1], 2.3, 0, Math.PI * 2);
        ctx.fillStyle = pal.stop;
        ctx.fill();
        ctx.strokeStyle = routeColour(route.hue, scheme);
        ctx.lineWidth = 1.3;
        ctx.stroke();
      }
      ctx.globalAlpha = 1;
    }
  }

  paintLabels(ctx, cam, pal, scheme, filters);
}

/** A point along a screen path at a WORLD along-path distance. */
function alongScreen(path: readonly Point[], cumulative: readonly number[], s: number): Point {
  let i = 1;
  while (i < cumulative.length - 1 && (cumulative[i] ?? 0) < s) i += 1;
  const a = path[i - 1] ?? path[0] ?? [0, 0];
  const b = path[i] ?? a;
  const start = cumulative[i - 1] ?? 0;
  const span = (cumulative[i] ?? start) - start;
  const t = span > 0 ? Math.max(0, Math.min(1, (s - start) / span)) : 0;
  return [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
}

function paintGrid(
  ctx: CanvasRenderingContext2D,
  cam: Camera,
  angle: number,
  spacing: number,
  seed: number,
  width: number,
  height: number,
  pal: Palette,
): void {
  const step = spacing * cam.k;
  if (step < 4) return;
  const rad = (angle * Math.PI) / 180;
  const ux = Math.cos(rad);
  const uy = Math.sin(rad);
  const vx = -uy;
  const vy = ux;
  // Work in the grid's own frame, anchored at the world origin so the grid is fixed
  // to the city rather than to the screen.
  const origin = toScreen(cam, [0, 0]);
  const corners: Point[] = [
    [0, 0],
    [width, 0],
    [0, height],
    [width, height],
  ];
  const us = corners.map(([x, y]) => (x - origin[0]) * ux + (y - origin[1]) * uy);
  const vs = corners.map(([x, y]) => (x - origin[0]) * vx + (y - origin[1]) * vy);
  const uMin = Math.floor(Math.min(...us) / step);
  const uMax = Math.ceil(Math.max(...us) / step);
  const vMin = Math.floor(Math.min(...vs) / step);
  const vMax = Math.ceil(Math.max(...vs) / step);
  ctx.beginPath();
  // Lines of constant u, broken into blocks, some blocks missing: superblocks, cul-de-
  // sacs and rail yards, so the web reads as a city rather than as graph paper.
  for (let i = uMin; i <= uMax; i += 1) {
    for (let j = vMin; j < vMax; j += 1) {
      if (hash2(i + seed * 101, j) < 0.06) continue;
      const u = i * step;
      const x0 = origin[0] + ux * u + vx * j * step;
      const y0 = origin[1] + uy * u + vy * j * step;
      ctx.moveTo(x0, y0);
      ctx.lineTo(x0 + vx * step, y0 + vy * step);
    }
  }
  for (let j = vMin; j <= vMax; j += 1) {
    for (let i = uMin; i < uMax; i += 1) {
      if (hash2(i, j + seed * 211) < 0.06) continue;
      const v = j * step;
      const x0 = origin[0] + vx * v + ux * i * step;
      const y0 = origin[1] + vy * v + uy * i * step;
      ctx.moveTo(x0, y0);
      ctx.lineTo(x0 + ux * step, y0 + uy * step);
    }
  }
  ctx.strokeStyle = pal.street;
  ctx.lineWidth = step > 16 ? 1.5 : 1;
  ctx.lineCap = "butt";
  ctx.stroke();
  ctx.lineCap = "round";
}

function haloText(
  ctx: CanvasRenderingContext2D,
  text: string,
  x: number,
  y: number,
  pal: Palette,
  colour: string,
): void {
  ctx.strokeStyle = pal.halo;
  ctx.lineWidth = 3;
  ctx.strokeText(text, x, y);
  ctx.fillStyle = colour;
  ctx.fillText(text, x, y);
}

function paintLabels(ctx: CanvasRenderingContext2D, cam: Camera, pal: Palette, scheme: Scheme, filters: Filters): void {
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.lineJoin = "round";

  // Districts: small, tracked capitals.
  ctx.font = `600 10.5px ${FONT}`;
  ctx.letterSpacing = "1.6px";
  for (const district of DISTRICTS) {
    if (district.label === undefined) continue;
    const [x, y] = toScreen(cam, district.label);
    haloText(ctx, district.name.toUpperCase(), x, y, pal, pal.district);
  }
  ctx.letterSpacing = "0.6px";
  ctx.font = `italic 500 11px ${FONT}`;
  for (const label of WATER_LABELS) {
    const [x, y] = toScreen(cam, label.at);
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate((label.angle * Math.PI) / 180);
    ctx.fillStyle = pal.water_label;
    ctx.fillText(label.name, 0, 0);
    ctx.restore();
  }
  ctx.letterSpacing = "0px";

  // Parks.
  ctx.font = `500 10px ${FONT}`;
  for (const park of PARKS) {
    if (park.name === undefined || park.label === undefined) continue;
    const [x, y] = toScreen(cam, park.label);
    haloText(ctx, park.name, x, y, pal, scheme === "light" ? "#5d7a52" : "#7e9b73");
  }

  // Street names along their roads, kept upright.
  ctx.font = `500 9.5px ${FONT}`;
  for (const road of ROADS) {
    if (road.labelAt === undefined) continue;
    const [segment, t] = road.labelAt;
    const a = road.points[segment];
    const b = road.points[segment + 1];
    if (a === undefined || b === undefined) continue;
    const p: Point = [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
    const [x, y] = toScreen(cam, p);
    let angle = Math.atan2(b[1] - a[1], b[0] - a[0]);
    if (angle > Math.PI / 2) angle -= Math.PI;
    if (angle < -Math.PI / 2) angle += Math.PI;
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate(angle);
    haloText(ctx, road.name, 0, road.rank === 2 ? -7 : -5.5, pal, pal.street_label);
    ctx.restore();
  }
  ctx.font = `600 9.5px ${FONT}`;
  for (const label of BRIDGE_LABELS) {
    const [x, y] = toScreen(cam, label.at);
    ctx.save();
    ctx.translate(x, y);
    ctx.rotate((label.angle * Math.PI) / 180);
    haloText(ctx, label.name, 0, 0, pal, pal.street_label);
    ctx.restore();
  }

  // Central Station: the rail interchange, as a small pictogram.
  {
    const [x, y] = toScreen(cam, CENTRAL_STATION);
    ctx.beginPath();
    ctx.roundRect(x - 7, y - 7, 14, 14, 3.5);
    ctx.fillStyle = pal.ink;
    ctx.fill();
    ctx.fillStyle = pal.inkOn;
    ctx.font = `700 9px ${FONT}`;
    ctx.fillText("R", x, y + 0.5);
    ctx.font = `600 10px ${FONT}`;
    haloText(ctx, "Central Station", x, y + 15, pal, pal.district);
  }

  // Traffic cameras.
  for (const camera of CAMERAS) {
    const [x, y] = toScreen(cam, camera.at);
    paintCameraGlyph(ctx, x + 14, y - 12, pal);
  }

  // Route shields, one per route a third of the way along.
  ctx.font = `700 10px ${FONT}`;
  const routeFiltered = filters.routes.size > 0;
  for (const route of ROUTES) {
    const geometry = GEOMETRY.get(route.id);
    if (geometry === undefined) continue;
    const path = routeScreenPath(cam, route.id);
    for (const fraction of [0.34, 0.78]) {
      const p = alongScreen(path, geometry.cumulative, geometry.length * fraction);
      const w = route.id.length > 1 ? 20 : 15;
      ctx.globalAlpha = !routeFiltered || filters.routes.has(route.id) ? 1 : 0.35;
      ctx.beginPath();
      ctx.roundRect(p[0] - w / 2, p[1] - 7.5, w, 15, 4);
      ctx.fillStyle = routeColour(route.hue, scheme);
      ctx.fill();
      ctx.strokeStyle = pal.routeCasing;
      ctx.lineWidth = 1.5;
      ctx.stroke();
      ctx.fillStyle = scheme === "light" ? "#ffffff" : "#0e1013";
      ctx.fillText(route.id, p[0], p[1] + 0.5);
      ctx.globalAlpha = 1;
    }
  }
}

function paintCameraGlyph(ctx: CanvasRenderingContext2D, x: number, y: number, pal: Palette): void {
  ctx.beginPath();
  ctx.roundRect(x - 8, y - 6, 12, 12, 2.5);
  ctx.moveTo(x + 4, y - 2);
  ctx.lineTo(x + 8.5, y - 5);
  ctx.lineTo(x + 8.5, y + 5);
  ctx.lineTo(x + 4, y + 2);
  ctx.closePath();
  ctx.fillStyle = pal.camera;
  ctx.fill();
  ctx.beginPath();
  ctx.arc(x - 2, y, 2.6, 0, Math.PI * 2);
  ctx.fillStyle = pal.land;
  ctx.fill();
}

// ---------------------------------------------------------------------------------
// The live layer

export interface Marker {
  readonly fleet: string;
  readonly x: number;
  readonly y: number;
}

export function vehicleScreen(cam: Camera, vehicle: Vehicle): Point {
  const p = toScreen(cam, vehicle.at);
  // Sit the bus on its own line where routes share a street.
  const d = vehicle.geometry.route.slot * SLOT_PX;
  const [dx, dy] = vehicle.dir;
  const sign = vehicle.s < vehicle.geometry.length ? 1 : -1;
  return [p[0] - dy * d * sign, p[1] + dx * d * sign];
}

export function paintVehicles(
  ctx: CanvasRenderingContext2D,
  dpr: number,
  cam: Camera,
  scheme: Scheme,
  vehicles: readonly Vehicle[],
  filters: Filters,
  selected: string | null,
  hovered: string | null,
  highlight: Point | null,
): Marker[] {
  const pal = PALETTES[scheme];
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  const markers: Marker[] = [];
  const pending: PendingTag[] = [];
  const visible = (vehicle: Vehicle): boolean =>
    (filters.routes.size === 0 || filters.routes.has(vehicle.seed.route)) &&
    (filters.adherence === "all" || adherenceOf(vehicle.seed) === filters.adherence);

  // Draw order: filtered-out first, then quiet, then exceptions, then selection.
  const rank = (vehicle: Vehicle): number => {
    if (vehicle.seed.fleet === selected) return 4;
    if (vehicle.seed.fleet === hovered) return 3;
    if (!visible(vehicle)) return 0;
    return tagOf(vehicle) === undefined ? 1 : 2;
  };
  const order = [...vehicles].sort((a, b) => rank(a) - rank(b));

  if (highlight !== null) {
    const [x, y] = toScreen(cam, highlight);
    ctx.beginPath();
    ctx.arc(x, y, 9, 0, Math.PI * 2);
    ctx.strokeStyle = pal.ink;
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  for (const vehicle of order) {
    const [x, y] = vehicleScreen(cam, vehicle);
    markers.push({ fleet: vehicle.seed.fleet, x, y });
    const shown = visible(vehicle);
    const isSelected = vehicle.seed.fleet === selected;
    const isHovered = vehicle.seed.fleet === hovered;
    ctx.globalAlpha = shown || isSelected ? 1 : 0.3;
    const colour = routeColour(vehicle.geometry.route.hue, scheme);
    const [dx, dy] = vehicle.dir;
    const r = isSelected ? 8 : 6.2;

    if (isSelected || isHovered) {
      ctx.beginPath();
      ctx.arc(x, y, r + 6, 0, Math.PI * 2);
      ctx.fillStyle = scheme === "light" ? "rgba(27, 33, 41, 0.12)" : "rgba(238, 241, 244, 0.16)";
      ctx.fill();
      ctx.strokeStyle = pal.ink;
      ctx.lineWidth = isSelected ? 2.2 : 1.4;
      ctx.stroke();
    }

    // A teardrop pointing the way the bus is running.
    const tip: Point = [x + dx * (r + 5), y + dy * (r + 5)];
    const a0 = Math.atan2(dy, dx);
    ctx.beginPath();
    ctx.moveTo(tip[0], tip[1]);
    ctx.arc(x, y, r, a0 + 0.95, a0 - 0.95 + Math.PI * 2);
    ctx.closePath();
    ctx.fillStyle = colour;
    ctx.fill();
    ctx.strokeStyle = pal.outline;
    ctx.lineWidth = 1.8;
    ctx.stroke();
    if (vehicle.seed.disabled === true) {
      ctx.beginPath();
      ctx.moveTo(x - 3, y - 3);
      ctx.lineTo(x + 3, y + 3);
      ctx.moveTo(x + 3, y - 3);
      ctx.lineTo(x - 3, y + 3);
      ctx.strokeStyle = pal.outline;
      ctx.lineWidth = 1.8;
      ctx.stroke();
    }

    const tag = shown || isSelected ? tagOf(vehicle) : undefined;
    const label = isSelected || isHovered ? vehicle.seed.fleet : undefined;
    if (tag !== undefined || label !== undefined) {
      pending.push({ x, y, r, label, tag, forced: isSelected || isHovered, rank: tagRank(tag, isSelected, isHovered) });
    }
    ctx.globalAlpha = 1;
  }

  // Tags last, most important first, each placed where it collides with nothing
  // already placed: right of the bus, then left, then stacked above or below with a
  // leader. The queue on Victoria Bridge puts four late buses inside ten pixels, and
  // every one of them must still say what is wrong.
  const placed: Box[] = markers.map((m) => ({ x0: m.x - 7, y0: m.y - 7, x1: m.x + 7, y1: m.y + 7 }));
  pending.sort((a, b) => a.rank - b.rank);
  ctx.font = TAG_FONT;
  for (const item of pending) {
    const w = tagWidth(ctx, item.label, item.tag);
    const own: Box = { x0: item.x - 7, y0: item.y - 7, x1: item.x + 7, y1: item.y + 7 };
    const candidates: [number, number][] = [
      [item.x + item.r + 5, item.y],
      [item.x - item.r - 5 - w, item.y],
      [item.x + item.r + 3, item.y - 20],
      [item.x + item.r + 3, item.y + 20],
      [item.x - item.r - 3 - w, item.y - 20],
      [item.x - item.r - 3 - w, item.y + 20],
      [item.x + item.r + 3, item.y - 40],
      [item.x + item.r + 3, item.y + 40],
      [item.x - item.r - 3 - w, item.y - 40],
      [item.x - item.r - 3 - w, item.y + 40],
    ];
    const fits = (cx: number, cy: number): boolean => {
      const box: Box = { x0: cx - 1, y0: cy - 9.5, x1: cx + w + 1, y1: cy + 9.5 };
      return !placed.some((other) => overlaps(box, other) && !sameBox(other, own));
    };
    const spot = candidates.find(([cx, cy]) => fits(cx, cy)) ?? (item.forced ? candidates[0] : undefined);
    if (spot === undefined) continue;
    const [cx, cy] = spot;
    if (cy !== item.y) {
      ctx.beginPath();
      ctx.moveTo(item.x, item.y);
      ctx.lineTo(cx < item.x ? cx + w : cx, cy);
      ctx.strokeStyle = pal.ink;
      ctx.lineWidth = 1;
      ctx.stroke();
    }
    paintTag(ctx, cx, cy, item.label, item.tag, scheme, pal);
    placed.push({ x0: cx - 1, y0: cy - 9.5, x1: cx + w + 1, y1: cy + 9.5 });
  }
  return markers;
}

interface Box {
  x0: number;
  y0: number;
  x1: number;
  y1: number;
}

interface PendingTag {
  x: number;
  y: number;
  r: number;
  label: string | undefined;
  tag: { text: string; severity: Severity } | undefined;
  forced: boolean;
  rank: number;
}

const TAG_FONT = `650 10.5px ${FONT}`;

function overlaps(a: Box, b: Box): boolean {
  return a.x0 < b.x1 && a.x1 > b.x0 && a.y0 < b.y1 && a.y1 > b.y0;
}

/** A tag may sit over its own bus's marker box. */
function sameBox(a: Box, b: Box): boolean {
  return a.x0 === b.x0 && a.y0 === b.y0 && a.x1 === b.x1 && a.y1 === b.y1;
}

function tagRank(tag: { severity: Severity } | undefined, selected: boolean, hovered: boolean): number {
  if (selected) return 0;
  if (hovered) return 1;
  if (tag?.severity === "critical") return 2;
  if (tag?.severity === "warning") return 3;
  return 4;
}

function tagWidth(
  ctx: CanvasRenderingContext2D,
  label: string | undefined,
  tag: { text: string } | undefined,
): number {
  let w = 0;
  if (label !== undefined) w += ctx.measureText(label).width + 10 + (tag === undefined ? 0 : 3);
  if (tag !== undefined) w += ctx.measureText(tag.text).width + 10;
  return w;
}

function paintTag(
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  label: string | undefined,
  tag: { text: string; severity: Severity } | undefined,
  scheme: Scheme,
  pal: Palette,
): void {
  ctx.textBaseline = "middle";
  ctx.textAlign = "left";
  ctx.font = TAG_FONT;
  let cursor = x;
  const h = 17;
  if (label !== undefined) {
    const w = ctx.measureText(label).width + 10;
    ctx.beginPath();
    ctx.roundRect(cursor, y - h / 2, w, h, h / 2);
    ctx.fillStyle = pal.ink;
    ctx.fill();
    ctx.fillStyle = pal.inkOn;
    ctx.fillText(label, cursor + 5, y + 0.5);
    cursor += w + 3;
  }
  if (tag !== undefined) {
    const w = ctx.measureText(tag.text).width + 10;
    ctx.beginPath();
    ctx.roundRect(cursor, y - h / 2, w, h, h / 2);
    ctx.fillStyle = SEVERITY[tag.severity].fill[scheme];
    ctx.fill();
    ctx.strokeStyle = pal.outline;
    ctx.lineWidth = 1.2;
    ctx.stroke();
    ctx.fillStyle = SEVERITY[tag.severity].text[scheme];
    ctx.fillText(tag.text, cursor + 5, y + 0.5);
  }
}

/** Bounds of the whole network, for "fit". */
export function networkBounds(): { x0: number; y0: number; x1: number; y1: number } {
  let x0 = Infinity;
  let y0 = Infinity;
  let x1 = -Infinity;
  let y1 = -Infinity;
  for (const route of ROUTES) {
    for (const [x, y] of route.path) {
      x0 = Math.min(x0, x);
      y0 = Math.min(y0, y);
      x1 = Math.max(x1, x);
      y1 = Math.max(y1, y);
    }
  }
  return { x0, y0, x1, y1 };
}

/** Bounds of one route, for fitting a search result. */
export function routeBounds(routeId: string): { x0: number; y0: number; x1: number; y1: number } {
  const path = GEOMETRY.get(routeId)?.points ?? [];
  let x0 = Infinity;
  let y0 = Infinity;
  let x1 = -Infinity;
  let y1 = -Infinity;
  for (const [x, y] of path) {
    x0 = Math.min(x0, x);
    y0 = Math.min(y0, y);
    x1 = Math.max(x1, x);
    y1 = Math.max(y1, y);
  }
  return { x0, y0, x1, y1 };
}
