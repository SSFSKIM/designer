/**
 * The planetarium page's sky model, pinned to astronomy-engine's own horizon coordinates.
 *
 * `sky/projection.ts` turns a J2000 position into an (east, north, up) direction through the local
 * sidereal time and the latitude; this suite asserts that reading against `Horizon()` for the Moon
 * and for a bright star, at three places and two instants, to within the quarter degree the
 * J2000-against-of-date frame costs (`astro.ts` header). It also pins the compass, the phase
 * names, and that the window's card and its list agree on where an object is — the two code paths
 * that once disagreed by a compass octant. The review's reproductions follow: wall-clock noons on
 * the day the clocks change, the twilight phase in the minutes before sunrise, and the next change
 * of phase where the Sun turns inside one.
 */

import { Body, Equator, Horizon, SearchRiseSet } from "astronomy-engine";
import { describe, expect, it, vi } from "vitest";

import {
  bodyObjects,
  directionOfObject,
  localNoon,
  moonPhaseName,
  nightSpan,
  observerFor,
  PLACES,
  siderealTime,
  sightings,
  sunState,
  type Place,
} from "../src/gallery/planetarium/astro";
import { wallClockToday, zonedInstant } from "../src/gallery/planetarium/clock";
import { computeLayout, DESIGN, meets } from "../src/gallery/planetarium/layout";
import type { StarCatalog } from "../src/gallery/planetarium/sky/catalog";
import { limbDirection } from "../src/gallery/planetarium/sky/limb";
import {
  altAzOf,
  compassOf,
  DEG,
  horizontalOf,
  horizonYAt,
  HOUR,
  project,
  unproject,
  type View,
} from "../src/gallery/planetarium/sky/projection";

// The layout's module also derives the gap from the runtime (`derivedGap`), whose package this
// suite's config does not alias; the geometry under test takes the gap as a number.
vi.mock("@vitreajs/vitrea-web", () => ({ samplingPaddingFor: () => 0 }));

const EMPTY: StarCatalog = {
  count: 0,
  ra: new Float32Array(0),
  dec: new Float32Array(0),
  mag: new Float32Array(0),
  bv: new Float32Array(0),
  hr: new Uint16Array(0),
  indexOfHr: new Map(),
  nameOfHr: new Map(),
  named: [],
};

const INSTANTS = [new Date("2026-09-28T13:30:00Z"), new Date("2026-03-02T04:00:00Z")];
const SAMPLE: Place[] = [PLACES[0] as Place, PLACES[5] as Place, PLACES[1] as Place];

describe("the sky's horizontal frame", () => {
  it("agrees with astronomy-engine for the Moon at three places", () => {
    for (const place of SAMPLE) {
      for (const date of INSTANTS) {
        const observer = observerFor(place);
        const moon = bodyObjects(date, observer).find((b) => b.id === "moon");
        expect(moon).toBeDefined();
        if (moon === undefined) continue;
        const lst = siderealTime(date, place.longitude);
        const { alt, az } = altAzOf(directionOfObject(moon, lst, place.latitude * DEG));
        const eq = Equator(Body.Moon, date, observer, true, true);
        // Of-date coordinates against the page's J2000 frame: the quarter degree of precession
        // and nutation since 2000 is the whole residual. No refraction: the page draws none.
        const hz = Horizon(date, observer, eq.ra, eq.dec);
        expect(Math.abs(alt / DEG - hz.altitude)).toBeLessThan(0.5);
        const dAz = Math.abs((((az / DEG - hz.azimuth) % 360) + 540) % 360 - 180);
        expect(dAz).toBeLessThan(0.5);
      }
    }
  });

  it("agrees with astronomy-engine for Vega", () => {
    const raHours = 18.6156;
    const decDeg = 38.7837;
    for (const place of SAMPLE) {
      for (const date of INSTANTS) {
        const lst = siderealTime(date, place.longitude);
        const { alt, az } = altAzOf(horizontalOf(raHours * HOUR, decDeg * DEG, lst, place.latitude * DEG));
        const hz = Horizon(date, observerFor(place), raHours, decDeg);
        expect(Math.abs(alt / DEG - hz.altitude)).toBeLessThan(0.05);
        const dAz = Math.abs((((az / DEG - hz.azimuth) % 360) + 540) % 360 - 180);
        expect(dAz).toBeLessThan(0.05);
      }
    }
  });

  it("puts the same object at the same place on the card and in the list", () => {
    const place = PLACES[0] as Place;
    const date = INSTANTS[0] as Date;
    const bodies = bodyObjects(date, observerFor(place));
    const row = sightings(date, place, EMPTY, bodies).find((s) => s.object.id === "moon");
    const moon = bodies.find((b) => b.id === "moon");
    expect(row).toBeDefined();
    expect(moon).toBeDefined();
    if (row === undefined || moon === undefined) return;
    const { alt, az } = altAzOf(directionOfObject(moon, siderealTime(date, place.longitude), place.latitude * DEG));
    expect(Math.abs(alt / DEG - row.altitude)).toBeLessThan(0.01);
    expect(Math.abs(az / DEG - row.azimuth)).toBeLessThan(0.01);
    expect(compassOf(az)).toBe(compassOf(row.azimuth * DEG));
  });
});

describe("the projection", () => {
  const view: View = { az: Math.PI, alt: 36 * DEG, focal: 585, width: 1440, height: 900 };
  it("round-trips a direction through the screen", () => {
    for (const [alt, az] of [[10, 150], [60, 200], [35, 180], [2, 120]] as const) {
      const v = horizontalOf(0, 0, 0, 0);
      void v;
      const dir = [Math.cos(alt * DEG) * Math.sin(az * DEG), Math.cos(alt * DEG) * Math.cos(az * DEG), Math.sin(alt * DEG)] as const;
      const px = project(dir, view);
      expect(px).toBeDefined();
      if (px === undefined) continue;
      const back = unproject(px[0], px[1], view);
      expect(Math.abs(back[0] - dir[0])).toBeLessThan(1e-6);
      expect(Math.abs(back[1] - dir[1])).toBeLessThan(1e-6);
      expect(Math.abs(back[2] - dir[2])).toBeLessThan(1e-6);
    }
  });
  it("puts the view centre at the middle of the screen and higher altitudes higher up", () => {
    const centre = project([Math.cos(36 * DEG) * Math.sin(Math.PI), Math.cos(36 * DEG) * Math.cos(Math.PI), Math.sin(36 * DEG)], view);
    expect(centre?.[0]).toBeCloseTo(720, 5);
    expect(centre?.[1]).toBeCloseTo(450, 5);
    const higher = project([0, -Math.cos(60 * DEG), Math.sin(60 * DEG)], view);
    expect(higher?.[1]).toBeLessThan(450);
    // Facing south, west (increasing azimuth) is to the right.
    const west = project([-Math.cos(30 * DEG), 0, Math.sin(30 * DEG)], view);
    expect(west?.[0]).toBeGreaterThan(720);
  });
});

describe("words", () => {
  it("names the compass points from north through east", () => {
    expect(compassOf(0)).toBe("N");
    expect(compassOf(90 * DEG)).toBe("E");
    expect(compassOf(112.5 * DEG)).toBe("ESE");
    expect(compassOf(180 * DEG)).toBe("S");
    expect(compassOf(270 * DEG)).toBe("W");
    expect(compassOf(359 * DEG)).toBe("N");
  });
  it("names the Moon's phases", () => {
    expect(moonPhaseName(0)).toBe("New Moon");
    expect(moonPhaseName(45)).toBe("Waxing crescent");
    expect(moonPhaseName(90)).toBe("First quarter");
    expect(moonPhaseName(180)).toBe("Full Moon");
    expect(moonPhaseName(300)).toBe("Waning crescent");
  });
});

const placeOf = (id: string): Place => {
  const place = PLACES.find((candidate) => candidate.id === id);
  if (place === undefined) throw new Error(`No place ${id}.`);
  return place;
};

/** The wall clock `timeZone` shows for an instant, as `HH:MM`. */
const wallClock = (instant: number | Date, timeZone: string): string =>
  new Intl.DateTimeFormat("en-GB", { timeZone, hour: "2-digit", minute: "2-digit", hourCycle: "h23" }).format(instant);

describe("wall clocks across a change of the clocks", () => {
  // Los Angeles moves from PST (UTC−8) to PDT (UTC−7) at 10:00Z on 8 March 2026.
  const zone = "America/Los_Angeles";

  it("resolves a wall-clock time with the offset in force at it", () => {
    expect(new Date(zonedInstant(zone, 2026, 3, 7, 12, 0)).toISOString()).toBe("2026-03-07T20:00:00.000Z");
    expect(new Date(zonedInstant(zone, 2026, 3, 8, 12, 0)).toISOString()).toBe("2026-03-08T19:00:00.000Z");
    expect(new Date(zonedInstant(zone, 2026, 3, 8, 1, 30)).toISOString()).toBe("2026-03-08T09:30:00.000Z");
  });

  it("takes the local noon on the calendar, not 24 hours back", () => {
    // 05:00 PDT on the 8th: that day's noon has not come, so the night began at noon on the 7th,
    // which is 12:00 PST (the reviewer's reading was the 7th's 11:00).
    const noon = localNoon(new Date("2026-03-08T12:00:00Z"), zone);
    expect(noon.toISOString()).toBe("2026-03-07T20:00:00.000Z");
    expect(wallClock(noon, zone)).toBe("12:00");
  });

  it("spans a 23-hour night from noon to the next calendar day's noon", () => {
    const night = nightSpan(new Date("2026-03-08T12:00:00Z"), zone);
    expect(night.start.toISOString()).toBe("2026-03-07T20:00:00.000Z");
    expect(night.end.toISOString()).toBe("2026-03-08T19:00:00.000Z");
    expect(wallClock(night.end, zone)).toBe("12:00");
    expect((night.end.getTime() - night.start.getTime()) / 3_600_000).toBe(23);
    // And a 25-hour one when the clocks go back (1 November 2026).
    const autumn = nightSpan(new Date("2026-11-01T12:00:00Z"), zone);
    expect((autumn.end.getTime() - autumn.start.getTime()) / 3_600_000).toBe(25);
    expect(wallClock(autumn.start, zone)).toBe("12:00");
    expect(wallClock(autumn.end, zone)).toBe("12:00");
  });

  it("reads `?at=12:00` as noon on the zone's own day, either side of the change", () => {
    // 02:00Z on the 8th is 18:00 PST on the 7th: today is the 7th.
    const evening = wallClockToday(12, 0, zone, new Date("2026-03-08T02:00:00Z"));
    expect(new Date(evening).toISOString()).toBe("2026-03-07T20:00:00.000Z");
    expect(wallClock(evening, zone)).toBe("12:00");
    // 09:00Z on the 8th is 01:00 PST, before the change: the offset at the base is not the offset
    // at noon (the reviewer's pre-transition base read 13:00).
    const early = wallClockToday(12, 0, zone, new Date("2026-03-08T09:00:00Z"));
    expect(new Date(early).toISOString()).toBe("2026-03-08T19:00:00.000Z");
    expect(wallClock(early, zone)).toBe("12:00");
  });
});

describe("the twilight state", () => {
  it("is civil twilight with sunrise next in the minutes before sunrise", () => {
    const seoul = placeOf("seoul");
    const observer = observerFor(seoul);
    const sunrise = SearchRiseSet(Body.Sun, observer, +1, new Date("2026-09-28T15:00:00Z"), 1)?.date;
    expect(sunrise).toBeDefined();
    if (sunrise === undefined) return;
    // Sunrise on 29 September in Seoul, about 06:15 KST.
    expect(wallClock(sunrise, seoul.timeZone).slice(0, 2)).toBe("06");
    const state = sunState(new Date(sunrise.getTime() - 3 * 60_000), observer);
    expect(state.phase).toBe("civil");
    expect(state.next?.label).toBe("sunrise");
    expect(Math.abs((state.next?.at.getTime() ?? 0) - sunrise.getTime())).toBeLessThan(60_000);
  });

  it("takes the earliest crossing where the Sun turns inside a phase", () => {
    // Reykjavík on the June solstice: the Sun sinks to about −2.5° after midnight and climbs
    // again without reaching −6°, so the next change is sunrise, not a civil dusk.
    const reykjavik = placeOf("reykjavik");
    const observer = observerFor(reykjavik);
    const date = new Date("2026-06-22T00:50:00Z");
    const state = sunState(date, observer);
    expect(state.phase).toBe("civil");
    const sunrise = SearchRiseSet(Body.Sun, observer, +1, date, 1)?.date;
    expect(sunrise).toBeDefined();
    if (sunrise === undefined) return;
    expect(state.next?.label).toBe("sunrise");
    expect(Math.abs((state.next?.at.getTime() ?? 0) - sunrise.getTime())).toBeLessThan(10 * 60_000);
    expect(Math.abs(sunrise.getTime() - Date.parse("2026-06-22T02:55:00Z"))).toBeLessThan(10 * 60_000);
  });
});

describe("the Moon's lit limb", () => {
  it("points along the great circle toward the Sun, not along the projected chord", () => {
    const seoul = placeOf("seoul");
    const date = new Date("2026-09-28T13:30:00Z");
    const bodies = bodyObjects(date, observerFor(seoul));
    const lst = siderealTime(date, seoul.longitude);
    const lat = seoul.latitude * DEG;
    const sun = bodies.find((b) => b.id === "sun");
    const moon = bodies.find((b) => b.id === "moon");
    if (sun === undefined || moon === undefined) throw new Error("No Sun or Moon.");
    const sunDir = directionOfObject(sun, lst, lat);
    const moonDir = directionOfObject(moon, lst, lat);
    // The page's own view at 22:30: toward the Moon, turned 12° toward the equator.
    const view: View = { az: altAzOf(moonDir).az + 12 * DEG, alt: 36 * DEG, focal: 900 / 2 / (2 * Math.tan(21 * DEG)), width: 1440, height: 900 };
    const [dx, dy] = limbDirection(sunDir, moonDir, view);
    expect(Math.hypot(dx, dy)).toBeCloseTo(1, 9);

    // The reference, built another way: a point half a degree along the great circle toward the
    // Sun (a slerp, not the tangent), projected, its screen direction from the Moon, y up.
    const omega = Math.acos(sunDir[0] * moonDir[0] + sunDir[1] * moonDir[1] + sunDir[2] * moonDir[2]);
    const t = (0.5 * DEG) / omega;
    const a = Math.sin((1 - t) * omega) / Math.sin(omega);
    const b = Math.sin(t * omega) / Math.sin(omega);
    const step = [0, 1, 2].map((i) => a * (moonDir[i] as number) + b * (sunDir[i] as number)) as unknown as readonly [number, number, number];
    const p0 = project(moonDir, view);
    const p1 = project(step, view);
    if (p0 === undefined || p1 === undefined) throw new Error("The Moon does not project.");
    const reference = Math.atan2(-(p1[1] - p0[1]), p1[0] - p0[0]);
    const angle = (x: number, y: number, to: number): number => Math.abs(((Math.atan2(y, x) - to + 3 * Math.PI) % (2 * Math.PI)) - Math.PI) / DEG;
    expect(angle(dx, dy, reference)).toBeLessThan(5);

    // What the page drew before: the chord to the projected Sun, and screen-right when the Sun
    // does not project — as here, the Sun more than 150° from the view's centre at 22:30, so the
    // lit side faced 164° away from the Sun's bearing.
    expect(project(sunDir, view)).toBeUndefined();
    expect(angle(1, 0, reference)).toBeGreaterThan(90);
  });
});

describe("the layout", () => {
  const viewOf = (width: number, height: number, az: number): View => ({
    az,
    alt: 36 * DEG,
    focal: height / 2 / (2 * Math.tan(21 * DEG)),
    width,
    height,
  });
  const inside = (box: { x: number; y: number; width: number; height: number }, width: number, height: number): boolean =>
    box.width >= 0 && box.height >= 0 && box.x >= 0 && box.y >= 0 && box.x + box.width <= width && box.y + box.height <= height;

  it("keeps every footprint, closed and open, inside the viewport and clear of the others from 1024 × 700", () => {
    for (const width of [1024, 1100, 1180, 1240, 1280, 1366, 1440, 1680, 1920]) {
      for (const height of [700, 768, 820, 900, 1080, 1200]) {
        for (const az of [0, 100 * DEG, 200 * DEG]) {
          const view = viewOf(width, height, az);
          const layout = computeLayout({ width, height }, 24, (x) => horizonYAt(x, view));
          const label = `${String(width)}×${String(height)} at ${String(Math.round(az / DEG))}° (${layout.arrangement})`;
          expect(layout.arrangement, label).not.toBe("clamped");
          const { window, module, place, time, placePlatter, timePlatter } = layout;
          for (const box of [window, module, place, time, placePlatter, timePlatter]) expect(inside(box, width, height), label).toBe(true);
          const closed = [window, module, place, time];
          closed.forEach((a, i) => closed.slice(i + 1).forEach((b) => expect(meets(a, b), label).toBe(false)));
          for (const box of [window, module, time]) expect(meets(placePlatter, box), label).toBe(false);
          for (const box of [window, module, place]) expect(meets(timePlatter, box), label).toBe(false);
          expect(place.width).toBe(DESIGN.place.width);
          expect(time.width).toBe(DESIGN.time.width);
        }
      }
    }
  });

  it("takes the standard arrangement on a wide, tall viewport and the compact one on a narrow one", () => {
    const at = (width: number, height: number) => computeLayout({ width, height }, 24, (x) => horizonYAt(x, viewOf(width, height, Math.PI)));
    expect(at(1440, 900).arrangement).toBe("standard");
    expect(at(1440, 900).window).toEqual({ x: 48, y: 48, width: 400, height: 560 });
    expect(at(1024, 768).arrangement).toBe("compact");
    const compact = at(1024, 768);
    expect(compact.module.x).toBe(compact.window.x);
    expect(compact.module.y).toBe(compact.window.y + compact.window.height + compact.gap);
  });

  it("presses every box inside a viewport too small for either arrangement", () => {
    for (const [width, height] of [[800, 600], [640, 480], [390, 844]] as const) {
      const view = viewOf(width, height, Math.PI);
      const layout = computeLayout({ width, height }, 24, (x) => horizonYAt(x, view));
      expect(layout.arrangement).toBe("clamped");
      for (const box of [layout.window, layout.module, layout.place, layout.time]) expect(inside(box, width, height)).toBe(true);
    }
  });
});
