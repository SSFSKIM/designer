/**
 * The shoot: ten photographs shown as thirty exposures, and the cull as the photographer left it.
 *
 * Each photograph is one setup of a burst of three. The second and third frames are the same
 * file re-framed by a few per cent and bracketed by a third of a stop, which the page paints
 * (`develop.ts`), because a real cull is mostly choosing between near-duplicates. Filenames,
 * times and exposure data are invented for the demo; the page says so beside the credits, and
 * nothing here describes the photographers' own cameras (`DESIGN.md`, "Thirty frames").
 */
import s01 from "./images/s01-shop-interior.jpg";
import s01t from "./images/s01-shop-interior-t.jpg";
import s02 from "./images/s02-brick-hearth.jpg";
import s02t from "./images/s02-brick-hearth-t.jpg";
import s03 from "./images/s03-at-the-forge.jpg";
import s03t from "./images/s03-at-the-forge-t.jpg";
import s04 from "./images/s04-mallet.jpg";
import s04t from "./images/s04-mallet-t.jpg";
import s05 from "./images/s05-anvil-hook.jpg";
import s05t from "./images/s05-anvil-hook-t.jpg";
import s06 from "./images/s06-hammer-strike.jpg";
import s06t from "./images/s06-hammer-strike-t.jpg";
import s07 from "./images/s07-working-metal.jpg";
import s07t from "./images/s07-working-metal-t.jpg";
import s08 from "./images/s08-hot-rod.jpg";
import s08t from "./images/s08-hot-rod-t.jpg";
import s09 from "./images/s09-mask-and-iron.jpg";
import s09t from "./images/s09-mask-and-iron-t.jpg";
import s11 from "./images/s11-horseshoe.jpg";
import s11t from "./images/s11-horseshoe-t.jpg";

export interface Photograph {
  readonly id: string;
  readonly full: string;
  readonly thumb: string;
  /** What it shows, from `images/CREDITS.md`; the stage's accessible name. */
  readonly depicts: string;
  readonly photographer: string;
  readonly profile: string;
  /** The white balance the frame was shot at, in kelvin: the temperature slider's origin. */
  readonly asShotTemp: number;
  readonly focal: number;
  readonly aperture: string;
  readonly iso: number;
}

export const PHOTOGRAPHS: readonly Photograph[] = [
  { id: "s01", full: s01, thumb: s01t, depicts: "Forge bay with anvil, hearth and hanging tongs",
    photographer: "Jay Kettle-Williams", profile: "https://unsplash.com/@jay_kettle_williams",
    asShotTemp: 4700, focal: 24, aperture: "f/4", iso: 800 },
  { id: "s02", full: s02, thumb: s02t, depicts: "Two smiths working either side of a brick hearth",
    photographer: "Rusty Watson", profile: "https://unsplash.com/@rustyct1",
    asShotTemp: 4400, focal: 35, aperture: "f/2.8", iso: 1600 },
  { id: "s03", full: s03, thumb: s03t, depicts: "A smith drawing stock out of the fire",
    photographer: "Chris Bischoff", profile: "https://unsplash.com/@cbischoff",
    asShotTemp: 5100, focal: 35, aperture: "f/2.8", iso: 1250 },
  { id: "s04", full: s04, thumb: s04t, depicts: "A smith at the anvil in the dark end of the shop",
    photographer: "Nicolas Hoizey", profile: "https://unsplash.com/@nhoizey",
    asShotTemp: 3900, focal: 50, aperture: "f/1.8", iso: 3200 },
  { id: "s05", full: s05, thumb: s05t, depicts: "A hot hook held on the anvil face with tongs",
    photographer: "Albert Stoynov", profile: "https://unsplash.com/@albertstoynov",
    asShotTemp: 4500, focal: 85, aperture: "f/2", iso: 1600 },
  { id: "s06", full: s06, thumb: s06t, depicts: "Hammer and chisel over bar stock on the anvil",
    photographer: "Maranda Vandergriff", profile: "https://unsplash.com/@mkvandergriff",
    asShotTemp: 4200, focal: 50, aperture: "f/2.2", iso: 2000 },
  { id: "s07", full: s07, thumb: s07t, depicts: "Stock worked at the far bench, low light",
    photographer: "James Lo", profile: "https://unsplash.com/@olsemaj",
    asShotTemp: 3500, focal: 50, aperture: "f/1.8", iso: 6400 },
  { id: "s08", full: s08, thumb: s08t, depicts: "Hammer landing on a glowing rod at the anvil edge",
    photographer: "Raul Barrios", profile: "https://unsplash.com/@lookscanshoot",
    asShotTemp: 4800, focal: 85, aperture: "f/2.8", iso: 1000 },
  { id: "s09", full: s09, thumb: s09t, depicts: "Molten iron poured under a raised extraction hood",
    photographer: "Francisco Fernandes", profile: "https://unsplash.com/@franciscofernandes",
    asShotTemp: 3300, focal: 70, aperture: "f/4", iso: 800 },
  { id: "s11", full: s11, thumb: s11t, depicts: "A horseshoe set on the anvil horn",
    photographer: "Jonathan Bean", profile: "https://unsplash.com/@jonathanbean",
    asShotTemp: 4300, focal: 50, aperture: "f/2.8", iso: 1600 },
];

/** How a burst member differs from the file: a re-framing and a bracket. */
export interface Framing {
  /** Zoom into the file, 1 = the whole file. */
  readonly zoom: number;
  /** Offset of the framing's centre, as a fraction of the file's width and height. */
  readonly ox: number;
  readonly oy: number;
  /** The bracket, in stops, relative to the metered exposure. */
  readonly bracket: number;
}

export type Aspect = "original" | "1:1" | "4:5" | "16:9";
export type Flag = "pick" | "reject" | null;

/** Everything the develop step applies. Crop centre and scale are in the frame's own units. */
export interface Develop {
  readonly ev: number;
  readonly temp: number;
  readonly tint: number;
  readonly aspect: Aspect;
  readonly angle: number;
  readonly scale: number;
  readonly cx: number;
  readonly cy: number;
}

export interface Frame {
  readonly index: number;
  readonly photo: Photograph;
  readonly framing: Framing;
  readonly file: string;
  readonly time: string;
  readonly shutter: string;
  readonly flag: Flag;
  readonly rating: number;
  readonly develop: Develop;
}

export function asShot(photo: Photograph): Develop {
  return { ev: 0, temp: photo.asShotTemp, tint: 0, aspect: "original", angle: 0, scale: 1, cx: 0.5, cy: 0.5 };
}

/** Third-stop shutter speeds, fastest first, so a bracket is one step either way. */
const SHUTTERS = [
  "1/2000", "1/1600", "1/1250", "1/1000", "1/800", "1/640", "1/500", "1/400", "1/320", "1/250",
  "1/200", "1/160", "1/125", "1/100", "1/80", "1/60", "1/50", "1/40", "1/30",
] as const;

/** Metered shutter per setup, as an index into SHUTTERS. */
const METERED = [13, 11, 9, 15, 9, 10, 16, 6, 7, 11];
/** Minutes after 09:12 at which each setup's burst was taken. */
const MINUTE = [0, 7, 11, 19, 26, 31, 38, 44, 52, 63];

/** Three members per burst: the metered frame, one under and one over, each re-framed. */
const FRAMINGS: readonly (readonly [Framing, Framing, Framing])[] = PHOTOGRAPHS.map((_, setup) => {
  const s = setup % 3;
  return [
    { zoom: 1, ox: 0, oy: 0, bracket: 0 },
    { zoom: 1.045 + 0.01 * s, ox: -0.012 - 0.004 * s, oy: 0.008, bracket: -1 / 3 },
    { zoom: 1.07 + 0.008 * s, ox: 0.016, oy: -0.01 + 0.004 * s, bracket: 1 / 3 },
  ];
});

function timeOf(setup: number, member: number): string {
  const total = 9 * 3600 + 12 * 60 + (MINUTE[setup] ?? 0) * 60 + 4 + setup * 13;
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const tenths = member * 2;
  const pad = (n: number): string => String(n).padStart(2, "0");
  return `${pad(h)}:${pad(m)}:${pad(s)}.${tenths}`;
}

/** Where the photographer had got to: five bursts culled, the sixth frame of burst five up. */
const CULL: readonly { flag: Flag; rating: number }[] = [
  { flag: null, rating: 2 }, { flag: "reject", rating: 0 }, { flag: "pick", rating: 3 },
  { flag: "pick", rating: 4 }, { flag: "reject", rating: 0 }, { flag: null, rating: 1 },
  { flag: "reject", rating: 0 }, { flag: "pick", rating: 5 }, { flag: null, rating: 2 },
  { flag: null, rating: 0 }, { flag: "pick", rating: 3 }, { flag: "reject", rating: 0 },
  { flag: "pick", rating: 4 },
];

/** Adjustments already made on the picks, keyed by frame index. */
const DEVELOPED: Readonly<Record<number, Partial<Develop>>> = {
  2: { ev: 0.3 },
  3: { temp: 4100, aspect: "16:9", cy: 0.56 },
  7: { ev: -0.2, temp: 4700, tint: 4, aspect: "4:5", cx: 0.44, angle: -1.2 },
  10: { ev: 0.5, tint: -3 },
  12: { ev: 0.35, temp: 4200 },
};

export const INITIAL_FRAME = 13;

export const SHOOT = {
  title: "Harrow Lane Forge",
  brief: "For Hands of the Trade",
  date: "12 Sep 2026",
} as const;

export const FRAMES: readonly Frame[] = PHOTOGRAPHS.flatMap((photo, setup) =>
  [0, 1, 2].map((member): Frame => {
    const index = setup * 3 + member;
    const framing = FRAMINGS[setup]?.[member] ?? { zoom: 1, ox: 0, oy: 0, bracket: 0 };
    const metered = METERED[setup] ?? 10;
    const shutter = SHUTTERS[metered + (member === 1 ? -1 : member === 2 ? 1 : 0)] ?? "1/125";
    const cull = CULL[index] ?? { flag: null, rating: 0 };
    return {
      index,
      photo,
      framing,
      file: `HLF_${String(4412 + index * 2 + (index % 3)).padStart(4, "0")}.CR3`,
      time: timeOf(setup, member),
      shutter,
      flag: cull.flag,
      rating: cull.rating,
      develop: { ...asShot(photo), ...DEVELOPED[index] },
    };
  }),
);
