/**
 * The vehicles, moving on real time.
 *
 * Each bus runs its route's round trip: outbound along the path, a layover at the far
 * terminal, inbound back. It cruises at an urban bus's speed, dwells at stops, and
 * crawls in the southbound queue on Victoria Bridge that alert a3 describes. Nothing
 * is accelerated: a bus crosses about a pixel a second at the fitted zoom, which is
 * what a control room's map does. Under Reduce Motion the sim still runs and the
 * displayed position steps at the AVL ping cadence instead of gliding (DESIGN.md,
 * motion).
 */
import {
  ROUTES,
  VEHICLE_SEEDS,
  type Point,
  type Route,
  type Severity,
  type VehicleSeed,
} from "./data";

export interface RouteGeometry {
  readonly route: Route;
  readonly points: readonly Point[];
  /** Cumulative length at each point, metres. */
  readonly cumulative: readonly number[];
  readonly length: number;
  /** Along-path position of each named stop. */
  readonly stopAt: readonly number[];
  /** Along-path interval driven on the Kingsway detour, if any. */
  readonly detour?: readonly [number, number];
}

function measure(points: readonly Point[]): number[] {
  const cumulative = [0];
  for (let i = 1; i < points.length; i += 1) {
    const a = points[i - 1];
    const b = points[i];
    if (a === undefined || b === undefined) continue;
    cumulative.push((cumulative[i - 1] ?? 0) + Math.hypot(b[0] - a[0], b[1] - a[1]));
  }
  return cumulative;
}

export function pointAlong(geometry: RouteGeometry, s: number): { at: Point; dir: Point } {
  const { points, cumulative } = geometry;
  const clamped = Math.max(0, Math.min(geometry.length, s));
  let index = 1;
  while (index < cumulative.length - 1 && (cumulative[index] ?? 0) < clamped) index += 1;
  const a = points[index - 1] ?? points[0] ?? [0, 0];
  const b = points[index] ?? a;
  const start = cumulative[index - 1] ?? 0;
  const span = (cumulative[index] ?? start) - start;
  const t = span > 0 ? (clamped - start) / span : 0;
  const dx = b[0] - a[0];
  const dy = b[1] - a[1];
  const norm = Math.hypot(dx, dy) || 1;
  return { at: [a[0] + dx * t, a[1] + dy * t], dir: [dx / norm, dy / norm] };
}

function detourInterval(points: readonly Point[], cumulative: readonly number[]): readonly [number, number] | undefined {
  // The detour leaves Kingsway at Seventh Ave (y 3750) and rejoins it at 11th (y 4150):
  // the path's first vertex on Seventh Ave through the vertex at 11th Ave on Kingsway.
  const start = points.findIndex((p) => p[1] === 3750);
  if (start < 0) return undefined;
  let end = -1;
  for (let i = start + 1; i < points.length; i += 1) {
    if (points[i]?.[1] === 4150) end = i;
  }
  if (end < 0) return undefined;
  return [cumulative[start] ?? 0, cumulative[end] ?? 0];
}

export const GEOMETRY: ReadonlyMap<string, RouteGeometry> = new Map(
  ROUTES.map((route) => {
    const cumulative = measure(route.path);
    const length = cumulative[cumulative.length - 1] ?? 0;
    const stopAt = route.stops.map((_, i) => (length * i) / Math.max(1, route.stops.length - 1));
    const detour = detourInterval(route.path, cumulative);
    const geometry: RouteGeometry = {
      route,
      points: route.path,
      cumulative,
      length,
      stopAt,
      ...(detour === undefined ? {} : { detour }),
    };
    return [route.id, geometry];
  }),
);

export type Adherence = "late" | "early" | "ontime";

export interface Vehicle {
  readonly seed: VehicleSeed;
  readonly geometry: RouteGeometry;
  /** Position along the round trip, 0..2L. */
  s: number;
  dwell: number;
  /** World position and heading as last displayed. */
  at: Point;
  dir: Point;
  speed: number;
  /** Seconds since the last AVL ping; a ping lands every 15 s. */
  ping: number;
  stepClock: number;
}

export function adherenceOf(seed: VehicleSeed): Adherence {
  if (seed.disabled === true || seed.deviation >= 5) return "late";
  if (seed.deviation <= -2) return "early";
  return "ontime";
}

export interface VehicleTag {
  readonly text: string;
  readonly severity: Severity;
}

/** The words an exception carries on the map. On-time vehicles carry none. */
export function tagOf(vehicle: Vehicle): VehicleTag | undefined {
  const { seed } = vehicle;
  if (seed.disabled === true) return { text: "Disabled", severity: "critical" };
  if (seed.deviation >= 10) return { text: `+${seed.deviation} min`, severity: "critical" };
  if (seed.deviation >= 5) return { text: `+${seed.deviation} min`, severity: "warning" };
  if (seed.deviation <= -2) return { text: `${seed.deviation} min`, severity: "warning" };
  if (onDetour(vehicle)) return { text: "Detour", severity: "info" };
  return undefined;
}

export function outbound(vehicle: Vehicle): boolean {
  return vehicle.s < vehicle.geometry.length;
}

/** Along-path position, whichever way the bus is running. */
export function alongPath(vehicle: Vehicle): number {
  const { length } = vehicle.geometry;
  return vehicle.s < length ? vehicle.s : 2 * length - vehicle.s;
}

export function onDetour(vehicle: Vehicle): boolean {
  const interval = vehicle.geometry.detour;
  if (interval === undefined) return false;
  const p = alongPath(vehicle);
  return p >= interval[0] && p <= interval[1];
}

/** A deterministic hash in 0..1, so dwell times differ per bus and per stop. */
function hash(a: number, b: number): number {
  const x = Math.sin(a * 127.1 + b * 311.7) * 43758.5453;
  return x - Math.floor(x);
}

const CRUISE = 8.2; // m/s, about 30 km/h between stops
const QUEUE = 1.1; // m/s, the southbound queue on Victoria Bridge
const LAYOVER = 45; // s at each terminal

function inBridgeQueue(at: Point, dir: Point): boolean {
  return Math.abs(at[0] - 3400) < 60 && at[1] > 1950 && at[1] < 2700 && dir[1] > 0.5;
}

export function createVehicles(): Vehicle[] {
  return VEHICLE_SEEDS.map((seed, index) => {
    const geometry = GEOMETRY.get(seed.route);
    if (geometry === undefined) throw new Error(`Vehicle ${seed.fleet} names an unknown route.`);
    const s = seed.phase * 2 * geometry.length;
    const vehicle: Vehicle = {
      seed,
      geometry,
      s,
      dwell: 0,
      at: [0, 0],
      dir: [1, 0],
      speed: 0,
      ping: hash(index, 7) * 15,
      stepClock: hash(index, 3) * 5,
    };
    place(vehicle);
    return vehicle;
  });
}

function place(vehicle: Vehicle): void {
  const { at, dir } = pointAlong(vehicle.geometry, alongPath(vehicle));
  vehicle.at = at;
  vehicle.dir = outbound(vehicle) ? dir : [-dir[0], -dir[1]];
}

/**
 * Advance every vehicle by `dt` seconds. With `stepped`, the displayed position only
 * moves when a bus's own 5-second step clock rolls over, which is the AVL cadence.
 */
export function advance(vehicles: Vehicle[], dt: number, stepped: boolean): void {
  const delta = Math.min(dt, 1); // a backgrounded tab does not teleport the fleet
  vehicles.forEach((vehicle, index) => {
    vehicle.ping = (vehicle.ping + delta) % 15;
    if (vehicle.seed.disabled === true) {
      vehicle.speed = 0;
      place(vehicle);
      return;
    }
    const { length, stopAt } = vehicle.geometry;
    if (vehicle.dwell > 0) {
      vehicle.dwell = Math.max(0, vehicle.dwell - delta);
      vehicle.speed = 0;
    } else {
      const queued = inBridgeQueue(vehicle.at, vehicle.dir);
      const speed = queued ? QUEUE : CRUISE;
      const before = alongPath(vehicle);
      const sBefore = vehicle.s;
      vehicle.s = (vehicle.s + speed * delta) % (2 * length);
      vehicle.speed = speed;
      const after = alongPath(vehicle);
      // Terminal layover when the round trip turns or wraps.
      if ((sBefore < length && vehicle.s >= length) || vehicle.s < sBefore) {
        vehicle.dwell = LAYOVER;
      } else {
        const lo = Math.min(before, after);
        const hi = Math.max(before, after);
        for (let i = 1; i < stopAt.length - 1; i += 1) {
          const stop = stopAt[i] ?? -1;
          if (stop > lo && stop <= hi) {
            vehicle.dwell = 8 + hash(index, i) * 18;
            break;
          }
        }
      }
    }
    if (!stepped) {
      place(vehicle);
      return;
    }
    vehicle.stepClock += delta;
    if (vehicle.stepClock >= 5) {
      vehicle.stepClock %= 5;
      place(vehicle);
    }
  });
}

/** The next named stop ahead of the bus, and its distance in metres. */
export function nextStop(vehicle: Vehicle): { name: string; metres: number } {
  const { stopAt, route } = vehicle.geometry;
  const p = alongPath(vehicle);
  if (outbound(vehicle)) {
    for (let i = 0; i < stopAt.length; i += 1) {
      const at = stopAt[i] ?? 0;
      if (at > p + 1) return { name: route.stops[i] ?? "", metres: at - p };
    }
    return { name: route.stops[route.stops.length - 1] ?? "", metres: 0 };
  }
  for (let i = stopAt.length - 1; i >= 0; i -= 1) {
    const at = stopAt[i] ?? 0;
    if (at < p - 1) return { name: route.stops[i] ?? "", metres: p - at };
  }
  return { name: route.stops[0] ?? "", metres: 0 };
}

/** Terminal the bus is heading for. */
export function destination(vehicle: Vehicle): string {
  const { stops } = vehicle.geometry.route;
  return outbound(vehicle) ? (stops[stops.length - 1] ?? "") : (stops[0] ?? "");
}

/**
 * Headways to the buses ahead and behind on the same route and direction, in minutes
 * at the scheduled average speed (stops included), as a dispatcher reads them.
 */
export function headways(vehicle: Vehicle, fleet: readonly Vehicle[]): { ahead?: number; behind?: number } {
  const round = 2 * vehicle.geometry.length;
  let ahead = Infinity;
  let behind = Infinity;
  for (const other of fleet) {
    if (other === vehicle || other.seed.route !== vehicle.seed.route) continue;
    const forward = (other.s - vehicle.s + round) % round;
    const backward = (vehicle.s - other.s + round) % round;
    ahead = Math.min(ahead, forward);
    behind = Math.min(behind, backward);
  }
  const perMinute = 5.2 * 60; // metres per minute with dwell, about 19 km/h
  return {
    ...(Number.isFinite(ahead) ? { ahead: ahead / perMinute } : {}),
    ...(Number.isFinite(behind) ? { behind: behind / perMinute } : {}),
  };
}

