/**
 * The stopwatch, as a rattrapante: a chronograph with a second, split hand.
 *
 * Start, Stop and Reset are the ordinary chronograph. Lap is the split: the split hand stops
 * where the chronograph hand is and the lap is recorded, while the chronograph runs on; a moment
 * later the split hand flies back to rejoin it, as a rattrapante's does when its pusher is
 * pressed again. Time is read from `performance.now()`, never accumulated per frame, so a
 * backgrounded tab resumes on the right second.
 */

export interface Lap {
  readonly index: number;
  /** The lap's own length, and the total at the split, in ms. */
  readonly split: number;
  readonly total: number;
}

export interface ChronoState {
  readonly running: boolean;
  /** Elapsed ms banked before the current run. */
  readonly banked: number;
  /** When the current run started (performance.now()), or null when stopped. */
  readonly startedAt: number | null;
  readonly laps: readonly Lap[];
  /** The split hand's hold: the total it shows, and when it was stopped. */
  readonly splitHold: { readonly total: number; readonly at: number } | null;
}

export const INITIAL: ChronoState = { running: false, banked: 0, startedAt: null, laps: [], splitHold: null };

/** How long the split hand holds before it flies back, in ms. */
export const SPLIT_HOLD_MS = 1600;

export function elapsed(s: ChronoState, now: number): number {
  return s.banked + (s.running && s.startedAt !== null ? now - s.startedAt : 0);
}

export function startStop(s: ChronoState, now: number): ChronoState {
  if (s.running) return { ...s, running: false, banked: elapsed(s, now), startedAt: null };
  return { ...s, running: true, startedAt: now };
}

export function lapOrReset(s: ChronoState, now: number): ChronoState {
  if (!s.running) return INITIAL;
  const total = elapsed(s, now);
  const previous = s.laps[0]?.total ?? 0;
  const lap = { index: s.laps.length + 1, split: total - previous, total };
  return { ...s, laps: [lap, ...s.laps], splitHold: { total, at: now } };
}

/**
 * What the chronograph's own hands read: the centre seconds in 1/8 s steps (a 28,800 vph
 * movement's beat), the thirty-minute and twelve-hour counters, and the split hand.
 */
export function chronoAngles(s: ChronoState, now: number): { chrono: number; split: number; minutes: number; hours: number } {
  const t = elapsed(s, now);
  const beat = Math.floor(t / 125) * 125;
  const chrono = ((beat / 1000) % 60) / 60 * Math.PI * 2;
  let split = chrono;
  if (s.splitHold !== null && now - s.splitHold.at < SPLIT_HOLD_MS) {
    const held = Math.floor(s.splitHold.total / 125) * 125;
    split = ((held / 1000) % 60) / 60 * Math.PI * 2;
  }
  return {
    chrono,
    split,
    minutes: ((t / 60000) % 30) / 30 * Math.PI * 2,
    hours: ((t / 3600000) % 12) / 12 * Math.PI * 2,
  };
}

/** `mm:ss.cc`, or `h:mm:ss.cc` past the hour, in tabular figures. */
export function format(ms: number): string {
  const cs = Math.floor(ms / 10) % 100;
  const s = Math.floor(ms / 1000) % 60;
  const m = Math.floor(ms / 60000) % 60;
  const h = Math.floor(ms / 3600000);
  const two = (n: number): string => String(n).padStart(2, "0");
  return h > 0 ? `${h}:${two(m)}:${two(s)}.${two(cs)}` : `${two(m)}:${two(s)}.${two(cs)}`;
}

/** Spoken: "1 minute 4.2 seconds". */
export function spoken(ms: number): string {
  const s = (ms / 1000) % 60;
  const m = Math.floor(ms / 60000) % 60;
  const h = Math.floor(ms / 3600000);
  const parts: string[] = [];
  if (h > 0) parts.push(`${h} hour${h === 1 ? "" : "s"}`);
  if (m > 0) parts.push(`${m} minute${m === 1 ? "" : "s"}`);
  parts.push(`${s.toFixed(2)} seconds`);
  return parts.join(" ");
}
