/**
 * The sky's geometry, shared by the CPU and the shaders.
 *
 * Every direction is a unit vector in the observer's horizontal frame, (east, north, up). A star's
 * J2000 right ascension and declination become one through the local sidereal time and the
 * latitude; the view is a stereographic projection centred on a chosen azimuth and altitude,
 * which keeps every small shape on the sky its own shape and every circle a circle, so the
 * horizon is an arc and a constellation is undistorted where it stands. The shaders carry the
 * same two functions in GLSL (`renderer.ts`), and `test/planetarium.test.ts` pins the CPU form to
 * astronomy-engine's own horizon coordinates.
 */

export const DEG = Math.PI / 180;
export const HOUR = Math.PI / 12;

export type Vec3 = readonly [number, number, number];

/** The direction of a J2000 position at local sidereal time `lst` (radians) and latitude `lat`. */
export function horizontalOf(ra: number, dec: number, lst: number, lat: number): Vec3 {
  const h = lst - ra;
  const cosDec = Math.cos(dec);
  const xh = cosDec * Math.cos(h); // toward the meridian
  const yh = cosDec * Math.sin(h); // toward the west
  const zh = Math.sin(dec); // toward the celestial pole
  const sinLat = Math.sin(lat);
  const cosLat = Math.cos(lat);
  return [-yh, zh * cosLat - xh * sinLat, zh * sinLat + xh * cosLat];
}

/** Altitude and azimuth (from north through east), radians, of a horizontal direction. */
export function altAzOf(v: Vec3): { readonly alt: number; readonly az: number } {
  const alt = Math.asin(Math.max(-1, Math.min(1, v[2])));
  const az = Math.atan2(v[0], v[1]);
  return { alt, az: az < 0 ? az + 2 * Math.PI : az };
}

/** The horizontal direction of an altitude and azimuth. */
export function directionOf(alt: number, az: number): Vec3 {
  const c = Math.cos(alt);
  return [c * Math.sin(az), c * Math.cos(az), Math.sin(alt)];
}

/** Where the page looks: the centre of the projection and its scale. */
export interface View {
  /** Azimuth of the view centre, radians from north through east. */
  readonly az: number;
  /** Altitude of the view centre, radians. */
  readonly alt: number;
  /** Focal length: CSS px per unit of the stereographic plane. */
  readonly focal: number;
  readonly width: number;
  readonly height: number;
}

/**
 * The tangent basis at the view centre: the centre direction, screen-right (increasing azimuth)
 * and screen-up (increasing altitude).
 */
export function viewBasis(view: View): { readonly c: Vec3; readonly right: Vec3; readonly up: Vec3 } {
  const { az, alt } = view;
  return {
    c: directionOf(alt, az),
    right: [Math.cos(az), -Math.sin(az), 0],
    up: [-Math.sin(alt) * Math.sin(az), -Math.sin(alt) * Math.cos(az), Math.cos(alt)],
  };
}

const dot = (a: Vec3, b: Vec3): number => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];

/**
 * Project a direction to CSS px from the viewport's top-left, or `undefined` for a direction more
 * than 150° from the view centre, where the stereographic plane runs away.
 */
export function project(v: Vec3, view: View): readonly [number, number] | undefined {
  const { c, right, up } = viewBasis(view);
  const cosC = dot(v, c);
  if (cosC < -0.866) return undefined;
  const k = 2 / (1 + cosC);
  return [view.width / 2 + k * dot(v, right) * view.focal, view.height / 2 - k * dot(v, up) * view.focal];
}

/** The direction seen at CSS px (x, y) from the viewport's top-left. */
export function unproject(x: number, y: number, view: View): Vec3 {
  const { c, right, up } = viewBasis(view);
  const X = (x - view.width / 2) / view.focal;
  const Y = (view.height / 2 - y) / view.focal;
  const rho = Math.hypot(X, Y);
  const angle = 2 * Math.atan(rho / 2);
  if (rho === 0) return c;
  const s = Math.sin(angle) / rho;
  const cs = Math.cos(angle);
  return [
    cs * c[0] + s * (X * right[0] + Y * up[0]),
    cs * c[1] + s * (X * right[1] + Y * up[1]),
    cs * c[2] + s * (X * right[2] + Y * up[2]),
  ];
}

/**
 * The ground's ridge line: its altitude above the true horizon at an azimuth, radians. The sky
 * shader draws the same function (`renderer.ts`), so the layout and the picture agree.
 */
export function ridgeAltitude(az: number): number {
  return 0.012 + 0.01 * Math.sin(az * 3 + 0.7) + 0.006 * Math.sin(az * 7 - 1.9) + 0.004 * Math.sin(az * 13 + 2.3);
}

/**
 * The screen row where the ground's ridge crosses column `x`, CSS px, or `undefined` where it
 * does not: the layout keeps its lowest ornament above it.
 */
export function horizonYAt(x: number, view: View): number | undefined {
  const above = (y: number): boolean => {
    const v = unproject(x, y, view);
    const { alt, az } = altAzOf(v);
    return alt > ridgeAltitude(az);
  };
  let lo = 0;
  let hi = view.height;
  if (!above(lo) || above(hi)) return undefined;
  for (let i = 0; i < 24; i += 1) {
    const mid = (lo + hi) / 2;
    if (above(mid)) lo = mid;
    else hi = mid;
  }
  return (lo + hi) / 2;
}

/** Angular distance between two directions, radians. */
export function separation(a: Vec3, b: Vec3): number {
  return Math.acos(Math.max(-1, Math.min(1, dot(a, b))));
}

const POINTS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"] as const;

/** A sixteen-point compass direction for an azimuth in radians. */
export function compassOf(az: number): string {
  const index = Math.round((((az % (2 * Math.PI)) + 2 * Math.PI) % (2 * Math.PI)) / (Math.PI / 8)) % 16;
  return POINTS[index] ?? "N";
}
