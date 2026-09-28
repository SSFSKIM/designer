/**
 * The sky's model: where everything is, and when it rises, sets and darkens.
 *
 * Positions come from astronomy-engine (Sun, Moon and planets; twilight and rise and set searches;
 * the IAU constellation a direction falls in), all in J2000 equatorial coordinates so that the
 * catalogue's stars, the sky maps and the bodies share one frame; the local sidereal time then
 * turns the frame with the Earth. The one approximation is that frame: the sidereal time is of
 * date and the positions are J2000, a difference of a quarter of a degree in 2026 that no reading
 * on this page resolves.
 */

import {
  Body,
  Constellation,
  DefineStar,
  Equator,
  Horizon,
  Illumination,
  MoonPhase,
  Observer,
  SearchAltitude,
  SearchHourAngle,
  SearchMoonQuarter,
  SearchRiseSet,
  SiderealTime,
} from "astronomy-engine";

import { zonedFields, zonedInstant } from "./clock";
import type { StarCatalog } from "./sky/catalog";
import { altAzOf, DEG, HOUR, horizontalOf, type Vec3 } from "./sky/projection";

export interface Place {
  readonly id: string;
  readonly name: string;
  readonly country: string;
  readonly latitude: number;
  readonly longitude: number;
  readonly timeZone: string;
}

/** Seven places, both hemispheres, so the same page shows a different sky at each. */
export const PLACES: readonly Place[] = [
  { id: "seoul", name: "Seoul", country: "Korea", latitude: 37.5665, longitude: 126.978, timeZone: "Asia/Seoul" },
  { id: "reykjavik", name: "Reykjavík", country: "Iceland", latitude: 64.1466, longitude: -21.9426, timeZone: "Atlantic/Reykjavik" },
  { id: "london", name: "London", country: "United Kingdom", latitude: 51.5072, longitude: -0.1276, timeZone: "Europe/London" },
  { id: "san-francisco", name: "San Francisco", country: "United States", latitude: 37.7749, longitude: -122.4194, timeZone: "America/Los_Angeles" },
  { id: "nairobi", name: "Nairobi", country: "Kenya", latitude: -1.2921, longitude: 36.8219, timeZone: "Africa/Nairobi" },
  { id: "sydney", name: "Sydney", country: "Australia", latitude: -33.8688, longitude: 151.2093, timeZone: "Australia/Sydney" },
  { id: "ushuaia", name: "Ushuaia", country: "Argentina", latitude: -54.8019, longitude: -68.303, timeZone: "America/Argentina/Ushuaia" },
];

export function observerFor(place: Pick<Place, "latitude" | "longitude">): Observer {
  return new Observer(place.latitude, place.longitude, 0);
}

/** Local sidereal time, radians. */
export function siderealTime(date: Date, longitude: number): number {
  const hours = SiderealTime(date) + longitude / 15;
  return (((hours % 24) + 24) % 24) * HOUR;
}

export type ObjectKind = "sun" | "moon" | "planet" | "star";

export interface SkyObject {
  readonly id: string;
  readonly kind: ObjectKind;
  readonly name: string;
  /** J2000, radians. */
  readonly ra: number;
  readonly dec: number;
  readonly mag: number;
  /** B−V, for a planet's colour and a star's. */
  readonly bv: number;
  /** For a star: its catalogue index. */
  readonly index?: number;
}

const BODIES: readonly { id: string; body: Body; name: string; bv: number }[] = [
  { id: "sun", body: Body.Sun, name: "Sun", bv: 0.65 },
  { id: "moon", body: Body.Moon, name: "Moon", bv: 0.9 },
  { id: "mercury", body: Body.Mercury, name: "Mercury", bv: 0.95 },
  { id: "venus", body: Body.Venus, name: "Venus", bv: 0.8 },
  { id: "mars", body: Body.Mars, name: "Mars", bv: 1.4 },
  { id: "jupiter", body: Body.Jupiter, name: "Jupiter", bv: 0.85 },
  { id: "saturn", body: Body.Saturn, name: "Saturn", bv: 1.05 },
];

const bodyOf = (id: string): Body | undefined => BODIES.find((entry) => entry.id === id)?.body;

/** The Sun, Moon and five naked-eye planets at `date`, seen from `observer`. */
export function bodyObjects(date: Date, observer: Observer): SkyObject[] {
  return BODIES.map(({ id, body, name, bv }) => {
    const eq = Equator(body, date, observer, false, true);
    const mag = id === "sun" ? -26.7 : Illumination(body, date).mag;
    return {
      id,
      kind: id === "sun" ? "sun" : id === "moon" ? "moon" : "planet",
      name,
      ra: eq.ra * HOUR,
      dec: eq.dec * DEG,
      mag,
      bv,
    };
  });
}

export function starObject(catalog: StarCatalog, index: number): SkyObject {
  const hr = catalog.hr[index] as number;
  return {
    id: `hr${String(hr)}`,
    kind: "star",
    name: catalog.nameOfHr.get(hr) ?? `HR ${String(hr)}`,
    ra: catalog.ra[index] as number,
    dec: catalog.dec[index] as number,
    mag: catalog.mag[index] as number,
    bv: catalog.bv[index] as number,
    index,
  };
}

/** The IAU constellation a J2000 direction falls in. */
export function constellationOf(ra: number, dec: number): string {
  return Constellation(ra / HOUR, dec / DEG).name;
}

/** The direction of an object at local sidereal time `lst` and latitude `latitude`, both radians. */
export function directionOfObject(object: SkyObject, lst: number, latitude: number): Vec3 {
  return horizontalOf(object.ra, object.dec, lst, latitude);
}

// --- The Sun and twilight ---------------------------------------------------------------------

export type TwilightPhase = "day" | "civil" | "nautical" | "astronomical" | "night";

export interface SunState {
  /**
   * The centre's geometric altitude, degrees, no refraction: the convention the twilight floors
   * and astronomy-engine's searches share (`sunState`).
   */
  readonly altitude: number;
  readonly azimuth: number;
  readonly phase: TwilightPhase;
  /** Whether the Sun is climbing. */
  readonly rising: boolean;
  /** The next change of phase. */
  readonly next: { readonly label: string; readonly at: Date } | undefined;
}

const PHASE_FLOORS: readonly { phase: TwilightPhase; floor: number }[] = [
  { phase: "day", floor: -0.8333 },
  { phase: "civil", floor: -6 },
  { phase: "nautical", floor: -12 },
  { phase: "astronomical", floor: -18 },
  { phase: "night", floor: -90 },
];

/**
 * The Sun's twilight state and its next change.
 *
 * Classified on the centre's GEOMETRIC altitude, because that is the altitude the floors are
 * defined on and the one astronomy-engine's searches solve: `SearchAltitude` finds the unrefracted
 * centre at a given altitude, and `SearchRiseSet`'s sunrise is the geometric centre at −0.8333°
 * (the upper limb at the horizon under standard refraction). An apparent, refracted altitude
 * crosses −0.8333° minutes before that sunrise, so the status read "Daytime" with sunset as its
 * next change in the minutes before the Sun rose.
 *
 * The next change is the EARLIEST future crossing of either boundary of the current phase — its
 * own floor downward (dusk) or the floor above upward (dawn) — searched over two days, rather than
 * one boundary chosen by whether the Sun is climbing now. The two differ where the Sun turns
 * inside a phase without leaving it: at Reykjavík in June it sinks to about −2.5° after midnight
 * and climbs again, so the next change is sunrise, and a civil dusk that never comes is not it.
 */
export function sunState(date: Date, observer: Observer): SunState {
  const eq = Equator(Body.Sun, date, observer, true, true);
  const hz = Horizon(date, observer, eq.ra, eq.dec);
  const later = new Date(date.getTime() + 60_000);
  const eqLater = Equator(Body.Sun, later, observer, true, true);
  const rising = Horizon(later, observer, eqLater.ra, eqLater.dec).altitude > hz.altitude;
  const altitude = hz.altitude;
  const found = PHASE_FLOORS.findIndex((entry) => altitude > entry.floor);
  const index = found === -1 ? PHASE_FLOORS.length - 1 : found;
  const current = PHASE_FLOORS[index] as { phase: TwilightPhase; floor: number };
  const phase = current.phase;

  const candidates: { label: string; at: Date }[] = [];
  // Down through this phase's own floor; night has none.
  if (phase !== "night") {
    const at = searchDown(observer, date, current.floor);
    if (at !== undefined) candidates.push({ label: duskLabel(phase), at });
  }
  // Up through the floor of the phase above; day has none.
  const above = PHASE_FLOORS[index - 1];
  if (above !== undefined) {
    const at = searchUp(observer, date, above.floor);
    if (at !== undefined) candidates.push({ label: dawnLabel(above.phase), at });
  }
  let next: SunState["next"];
  for (const candidate of candidates) {
    if (next === undefined || candidate.at.getTime() < next.at.getTime()) next = candidate;
  }
  return { altitude, azimuth: hz.azimuth, phase, rising, next };
}

function searchUp(observer: Observer, date: Date, altitude: number): Date | undefined {
  if (altitude === -0.8333) return SearchRiseSet(Body.Sun, observer, +1, date, 2)?.date;
  return SearchAltitude(Body.Sun, observer, +1, date, 2, altitude)?.date;
}

function searchDown(observer: Observer, date: Date, altitude: number): Date | undefined {
  if (altitude === -0.8333) return SearchRiseSet(Body.Sun, observer, -1, date, 2)?.date;
  return SearchAltitude(Body.Sun, observer, -1, date, 2, altitude)?.date;
}

function dawnLabel(phase: TwilightPhase): string {
  return phase === "day" ? "sunrise" : `${phase} dawn`;
}

function duskLabel(phase: TwilightPhase): string {
  return phase === "day" ? "sunset" : `${phase} dusk`;
}

export function twilightTitle(phase: TwilightPhase): string {
  switch (phase) {
    case "day":
      return "Daytime";
    case "civil":
      return "Civil twilight";
    case "nautical":
      return "Nautical twilight";
    case "astronomical":
      return "Astronomical twilight";
    case "night":
      return "Night";
  }
}

// --- The Moon -------------------------------------------------------------------------------------

export interface MoonState {
  /** Ecliptic phase angle, degrees: 0 new, 90 first quarter, 180 full, 270 last quarter. */
  readonly phase: number;
  /** Illuminated fraction, 0..1. */
  readonly illuminated: number;
  /** Sun–Moon–Earth angle, degrees: 0 full, 180 new; the disc's lighting. */
  readonly phaseAngle: number;
  readonly phaseName: string;
  readonly waxing: boolean;
  readonly rise: Date | undefined;
  readonly set: Date | undefined;
  readonly nextQuarter: { readonly name: string; readonly at: Date };
}

const QUARTERS = ["New Moon", "First quarter", "Full Moon", "Last quarter"] as const;

export function moonPhaseName(phase: number): string {
  if (phase < 22.5 || phase >= 337.5) return "New Moon";
  if (phase < 67.5) return "Waxing crescent";
  if (phase < 112.5) return "First quarter";
  if (phase < 157.5) return "Waxing gibbous";
  if (phase < 202.5) return "Full Moon";
  if (phase < 247.5) return "Waning gibbous";
  if (phase < 292.5) return "Last quarter";
  return "Waning crescent";
}

export function moonState(date: Date, observer: Observer): MoonState {
  const phase = MoonPhase(date);
  const illumination = Illumination(Body.Moon, date);
  const quarter = SearchMoonQuarter(date);
  return {
    phase,
    illuminated: illumination.phase_fraction,
    phaseAngle: illumination.phase_angle,
    phaseName: moonPhaseName(phase),
    waxing: phase < 180,
    rise: SearchRiseSet(Body.Moon, observer, +1, date, 2)?.date,
    set: SearchRiseSet(Body.Moon, observer, -1, date, 2)?.date,
    nextQuarter: { name: QUARTERS[quarter.quarter] ?? "New Moon", at: quarter.time.date },
  };
}

// --- Rise, transit and set of anything ----------------------------------------------------------

export interface Passage {
  readonly rise: Date | undefined;
  readonly transit: Date | undefined;
  readonly set: Date | undefined;
  /** A star that never sets from this latitude, or never rises. */
  readonly circumpolar: "always-up" | "never-up" | undefined;
}

export function passageOf(object: SkyObject, date: Date, observer: Observer): Passage {
  let body = bodyOf(object.id);
  if (body === undefined) {
    DefineStar(Body.Star1, object.ra / HOUR, object.dec / DEG, 1000);
    body = Body.Star1;
  }
  const rise = SearchRiseSet(body, observer, +1, date, 2)?.date;
  const set = SearchRiseSet(body, observer, -1, date, 2)?.date;
  const transit = SearchHourAngle(body, observer, 0, date, +1).time.date;
  let circumpolar: Passage["circumpolar"];
  if (rise === undefined && set === undefined) {
    const eq = Equator(body, date, observer, true, true);
    circumpolar = Horizon(date, observer, eq.ra, eq.dec, "normal").altitude > 0 ? "always-up" : "never-up";
  }
  return { rise, transit, set, circumpolar };
}

// --- What is up -------------------------------------------------------------------------------------

export interface Sighting {
  readonly object: SkyObject;
  readonly direction: Vec3;
  /** Degrees. */
  readonly altitude: number;
  readonly azimuth: number;
}

/**
 * Everything worth listing that is above the horizon: the Moon, the planets and the brightest named
 * stars, in that order, the stars brightest first and at least five degrees up.
 */
export function sightings(
  date: Date,
  place: Place,
  catalog: StarCatalog,
  bodies: readonly SkyObject[],
): Sighting[] {
  const lst = siderealTime(date, place.longitude);
  const lat = place.latitude * DEG;
  const sight = (object: SkyObject): Sighting => {
    const direction = horizontalOf(object.ra, object.dec, lst, lat);
    const { alt, az } = altAzOf(direction);
    return { object, direction, altitude: alt / DEG, azimuth: az / DEG };
  };
  const up: Sighting[] = [];
  for (const body of bodies) {
    if (body.kind === "sun") continue;
    const s = sight(body);
    if (s.altitude > 0) up.push(s);
  }
  const stars: Sighting[] = [];
  for (const index of catalog.named) {
    const s = sight(starObject(catalog, index));
    if (s.altitude > 5) stars.push(s);
    if (stars.length === 12) break;
  }
  return [...up, ...stars];
}

// --- Formatting in the place's own clock --------------------------------------------------------

export const LOCALE = "en-GB";

export function formatTime(date: Date, timeZone: string): string {
  return new Intl.DateTimeFormat(LOCALE, { timeZone, hour: "2-digit", minute: "2-digit", hour12: false }).format(date);
}

export function formatDate(date: Date, timeZone: string): string {
  return new Intl.DateTimeFormat(LOCALE, { timeZone, weekday: "short", day: "numeric", month: "short" }).format(date);
}

/** "11 Oct": the module's third column, which "Sun 11 Oct" reached the rim with. */
export function formatShortDate(date: Date, timeZone: string): string {
  return new Intl.DateTimeFormat(LOCALE, { timeZone, day: "numeric", month: "short" }).format(date);
}

export function formatDayMonth(date: Date, timeZone: string): string {
  return new Intl.DateTimeFormat(LOCALE, { timeZone, day: "numeric", month: "long" }).format(date);
}

/**
 * The place's local noon at or before `date`, so a night's timeline has a fixed origin: today's
 * noon on the zone's calendar if it has come, otherwise the previous calendar day's. Each noon is
 * resolved with the offset in force at that noon (`zonedInstant`), and the previous day is taken
 * on the calendar, not as 24 hours earlier, so a noon either side of a clock change is still noon.
 */
export function localNoon(date: Date, timeZone: string): Date {
  const today = zonedFields(timeZone, date.getTime());
  const noon = zonedInstant(timeZone, today.year, today.month, today.day, 12, 0);
  if (noon <= date.getTime()) return new Date(noon);
  return new Date(zonedInstant(timeZone, today.year, today.month, today.day - 1, 12, 0));
}

/**
 * The night `date` falls in, noon to noon on the place's calendar: 24 hours, or 23 and 25 across a
 * change of the clocks, which is why the end is the next calendar day's noon and not start + 24 h.
 */
export function nightSpan(date: Date, timeZone: string): { readonly start: Date; readonly end: Date } {
  const start = localNoon(date, timeZone);
  const day = zonedFields(timeZone, start.getTime());
  return { start, end: new Date(zonedInstant(timeZone, day.year, day.month, day.day + 1, 12, 0)) };
}
