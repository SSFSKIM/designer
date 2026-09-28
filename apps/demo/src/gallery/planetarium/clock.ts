/**
 * The page's clock: the real time, a time the person scrubbed to, or a time-lapse.
 *
 * `?at=` pins it for a capture — an ISO instant, or `HH:MM` on the day the page loads in the
 * place's own zone — and the audit's phases are instants derived from that pinned day, so a
 * reading is reproducible. Nothing here is a timer: the app advances a playing clock from the
 * runtime's frame loop and re-reads a live one on the minute.
 */

export type ClockMode =
  | { readonly kind: "live" }
  | { readonly kind: "pinned"; readonly at: number }
  | { readonly kind: "playing"; readonly from: number; readonly startedAt: number };

/** Sky time per real second while playing: an hour in five seconds, a night in under a minute. */
export const PLAY_RATE = 720;

export function timeOf(mode: ClockMode, nowMs: number): number {
  switch (mode.kind) {
    case "live":
      return nowMs;
    case "pinned":
      return mode.at;
    case "playing":
      return mode.from + (nowMs - mode.startedAt) * PLAY_RATE;
  }
}

/** The instant `?at=` names, if the URL carries one. */
export function readPinnedAt(timeZone: string): number | undefined {
  const at = new URLSearchParams(location.search).get("at");
  if (at === null) return undefined;
  const clock = /^(\d{1,2}):(\d{2})$/.exec(at);
  if (clock !== null) {
    return wallClockToday(Number(clock[1]), Number(clock[2]), timeZone);
  }
  const parsed = Date.parse(at);
  return Number.isFinite(parsed) ? parsed : undefined;
}

/** The calendar and wall-clock fields `timeZone` shows for an instant; `month` is 1–12. */
export interface ZonedFields {
  readonly year: number;
  readonly month: number;
  readonly day: number;
  readonly hour: number;
  readonly minute: number;
  readonly second: number;
}

const formatters = new Map<string, Intl.DateTimeFormat>();

export function zonedFields(timeZone: string, instant: number): ZonedFields {
  let format = formatters.get(timeZone);
  if (format === undefined) {
    format = new Intl.DateTimeFormat("en-US", {
      timeZone,
      hourCycle: "h23",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
    formatters.set(timeZone, format);
  }
  const parts = format.formatToParts(instant);
  const get = (type: string): number => Number(parts.find((part) => part.type === type)?.value ?? "0");
  return {
    year: get("year"),
    month: get("month"),
    day: get("day"),
    hour: get("hour") % 24,
    minute: get("minute"),
    second: get("second"),
  };
}

/** The zone's offset from UTC at an instant, ms: the wall clock it shows, read as UTC, minus it. */
function offsetAt(timeZone: string, instant: number): number {
  const f = zonedFields(timeZone, instant);
  const whole = Math.floor(instant / 1000) * 1000;
  return Date.UTC(f.year, f.month - 1, f.day, f.hour, f.minute, f.second) - whole;
}

/**
 * The instant a wall-clock time names in `timeZone` (`month` 1–12; a day or month out of range
 * rolls over as `Date.UTC` rolls it). The offset is the one in force AT the answer, not at some
 * other instant of the day: the first guess takes the offset at the wall time read as UTC, and
 * each pass re-reads it at the new guess, which settles in one pass away from a transition and in
 * two across one — so a noon on the day the clocks change is that day's noon, not an hour off it.
 */
export function zonedInstant(
  timeZone: string,
  year: number,
  month: number,
  day: number,
  hour: number,
  minute: number,
): number {
  const wall = Date.UTC(year, month - 1, day, hour, minute);
  let guess = wall - offsetAt(timeZone, wall);
  for (let pass = 0; pass < 2; pass += 1) {
    const next = wall - offsetAt(timeZone, guess);
    if (next === guess) break;
    guess = next;
  }
  return guess;
}

/** `HH:MM` on the calendar day `base` falls on in `timeZone`, as an instant. */
export function wallClockToday(hours: number, minutes: number, timeZone: string, base = new Date()): number {
  const today = zonedFields(timeZone, base.getTime());
  return zonedInstant(timeZone, today.year, today.month, today.day, hours, minutes);
}
