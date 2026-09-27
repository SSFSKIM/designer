/**
 * Daybreak's content: the four photographs, the day's weather, agenda, tasks and places.
 *
 * Everything here is the product's data and nothing here is the material's. The photographs
 * carry the crop each one is painted with (`focus`, `zoom`) and the two grades the colour
 * schemes ask of it, because a crop and a grade are decisions about THAT photograph under the
 * page's fixed layout — `DESIGN.md` records why each is what it is.
 */

import dawnUrl from "./images/dawn-layers-of-light.webp";
import dayUrl from "./images/day-montichiello.webp";
import duskUrl from "./images/dusk-tramonto-a-montichiello.webp";
import nightUrl from "./images/night-site-transitoire.webp";

export type PhaseId = "dawn" | "day" | "dusk" | "night";

/**
 * A tone curve applied to encoded luma, `y = ceiling · (1 − e^(−gain·x/ceiling))`
 * normalised so that its slope at black is `gain`: shadows scale by `gain`, highlights roll off
 * toward `ceiling`. `lift` raises black toward that level first (the light grade's night floor).
 * The identity is `{ gain: 1, ceiling: Infinity, lift: 0 }`.
 */
export interface Grade {
  readonly gain: number;
  readonly ceiling: number;
  readonly lift: number;
}

export const IDENTITY_GRADE: Grade = { gain: 1, ceiling: Number.POSITIVE_INFINITY, lift: 0 };

export interface Photograph {
  readonly id: PhaseId;
  readonly label: string;
  /** Local hours this photograph covers when the page follows the time of day, [from, to). */
  readonly hours: readonly [number, number];
  readonly url: string;
  readonly title: string;
  readonly place: string;
  readonly maker: string;
  readonly licence: string;
  readonly licenceUrl: string;
  readonly source: string;
  /** Cover-fit focal point, 0..1 of the overflow on each axis, and an extra zoom over cover. */
  readonly focus: readonly [number, number];
  readonly zoom: number;
  readonly grade: { readonly light: Grade; readonly dark: Grade };
}

export const PHOTOGRAPHS: readonly Photograph[] = [
  {
    id: "dawn",
    label: "Dawn",
    hours: [5, 9],
    url: dawnUrl,
    title: "Layers of Light",
    place: "near Pienza",
    maker: "Fabrizio Lunardi",
    licence: "CC0",
    licenceUrl: "https://creativecommons.org/publicdomain/zero/1.0/",
    source: "https://commons.wikimedia.org/wiki/File:Layers_Of_Light_(182268107).jpeg",
    // Zoomed so the Radicofani ridge and its fortress run behind the search ornament (the sky
    // above it is a flat gradient) while the lit farmhouse stays below the Today window.
    focus: [0.62, 0.48],
    zoom: 1.16,
    grade: { light: IDENTITY_GRADE, dark: { gain: 0.62, ceiling: 0.3, lift: 0 } },
  },
  {
    id: "day",
    label: "Day",
    hours: [9, 17],
    url: dayUrl,
    title: "Val d’Orcia – Montichiello",
    place: "Monticchiello",
    maker: "Marco Usan",
    licence: "CC BY 3.0",
    licenceUrl: "https://creativecommons.org/licenses/by/3.0/",
    source: "https://commons.wikimedia.org/wiki/File:Val_d%27Orcia_-_Montichiello_-_panoramio.jpg",
    focus: [0.5, 0.25],
    zoom: 1,
    grade: { light: IDENTITY_GRADE, dark: { gain: 0.55, ceiling: 0.3, lift: 0 } },
  },
  {
    id: "dusk",
    label: "Dusk",
    hours: [17, 21],
    url: duskUrl,
    title: "Tramonto a Montichiello",
    place: "Monticchiello",
    maker: "Marco Usan",
    licence: "CC BY 3.0",
    licenceUrl: "https://creativecommons.org/licenses/by/3.0/",
    source:
      "https://commons.wikimedia.org/wiki/File:Tramonto_a_Montichiello_Val_d%27Orcia_-_panoramio.jpg",
    focus: [0.5, 0.5],
    zoom: 1,
    grade: { light: IDENTITY_GRADE, dark: { gain: 0.62, ceiling: 0.3, lift: 0 } },
  },
  {
    id: "night",
    label: "Night",
    hours: [21, 5],
    url: nightUrl,
    title: "Site Transitoire",
    place: "Crete Senesi",
    maker: "Emiliano Carchia",
    licence: "CC BY 3.0",
    licenceUrl: "https://creativecommons.org/licenses/by/3.0/",
    source: "https://commons.wikimedia.org/wiki/File:Site_Transitoire_(224739771).jpeg",
    focus: [0.5, 0.6],
    zoom: 1,
    grade: { light: { gain: 1, ceiling: Number.POSITIVE_INFINITY, lift: 0.04 }, dark: { gain: 0.9, ceiling: 0.34, lift: 0 } },
  },
];

export const PHASE_IDS: readonly PhaseId[] = PHOTOGRAPHS.map((photo) => photo.id);

export function photographFor(id: PhaseId): Photograph {
  const photo = PHOTOGRAPHS.find((candidate) => candidate.id === id);
  if (photo === undefined) throw new Error(`No photograph for phase ${id}.`);
  return photo;
}

/** The phase the local clock is in: dawn 05–09, day 09–17, dusk 17–21, night 21–05. */
export function phaseAt(date: Date): PhaseId {
  const hour = date.getHours();
  for (const photo of PHOTOGRAPHS) {
    const [from, to] = photo.hours;
    const inside = from < to ? hour >= from && hour < to : hour >= from || hour < to;
    if (inside) return photo.id;
  }
  return "day";
}

// --- Weather, for Siena --------------------------------------------------------------------

export type Condition = "clear" | "mostly-clear" | "partly-cloudy" | "cloudy" | "mist" | "rain";

export const CONDITION_LABEL: Record<Condition, string> = {
  clear: "Clear",
  "mostly-clear": "Mostly clear",
  "partly-cloudy": "Partly cloudy",
  cloudy: "Cloudy",
  mist: "Mist",
  rain: "Showers",
};

export const WEATHER_PLACE = "Siena";

/** Today by the hour, 00..23: the temperature and what the sky is doing. */
const TODAY_HOURS: readonly (readonly [number, Condition])[] = [
  [13, "clear"], [12, "clear"], [12, "clear"], [11, "clear"], [11, "mist"], [11, "mist"],
  [11, "mist"], [12, "mist"], [14, "mist"], [16, "mostly-clear"], [18, "mostly-clear"],
  [20, "clear"], [21, "clear"], [23, "clear"], [24, "partly-cloudy"], [24, "partly-cloudy"],
  [23, "partly-cloudy"], [22, "partly-cloudy"], [20, "clear"], [18, "clear"], [17, "clear"],
  [16, "clear"], [15, "clear"], [14, "clear"],
];

export const TODAY_HIGH = 24;
export const TODAY_LOW = 11;

export function weatherAt(date: Date): { readonly temperature: number; readonly condition: Condition } {
  const [temperature, condition] = TODAY_HOURS[date.getHours()] ?? [18, "clear"];
  return { temperature, condition };
}

/** The next five days, starting tomorrow: condition, high, low. */
export const FORECAST: readonly (readonly [Condition, number, number])[] = [
  ["partly-cloudy", 23, 12],
  ["rain", 19, 13],
  ["cloudy", 20, 12],
  ["mostly-clear", 22, 11],
  ["clear", 25, 13],
];

// --- The day's agenda ----------------------------------------------------------------------

export interface AgendaEvent {
  readonly start: string;
  readonly end?: string;
  readonly title: string;
  readonly where?: string;
}

export const AGENDA: readonly AgendaEvent[] = [
  { start: "07:15", end: "08:00", title: "Run, Fortezza loop", where: "5.4 km" },
  { start: "08:30", title: "School drop-off", where: "Scuola Duprè" },
  { start: "09:30", end: "09:45", title: "Studio stand-up", where: "Video call" },
  { start: "10:30", end: "11:30", title: "Design review: onboarding", where: "Room 2 · Ana, Luca, Pietro" },
  { start: "12:45", end: "13:45", title: "Lunch with Giulia", where: "Osteria Il Grattacielo" },
  { start: "14:00", end: "14:30", title: "1:1 with Marco", where: "Video call" },
  { start: "15:00", end: "16:30", title: "Focus: search spec", where: "Do not disturb" },
  { start: "17:15", title: "Pick up the kids", where: "Scuola Duprè" },
  { start: "19:30", end: "21:00", title: "Choir rehearsal", where: "San Domenico" },
];

export function minutesOf(time: string): number {
  const [hours, minutes] = time.split(":").map(Number);
  return (hours ?? 0) * 60 + (minutes ?? 0);
}

// --- Tasks ---------------------------------------------------------------------------------

export interface Task {
  readonly id: string;
  readonly title: string;
  readonly note?: string;
  readonly done: boolean;
}

export const TASKS: readonly Task[] = [
  { id: "notes", title: "Send review notes to Ana", note: "Before 12:00", done: false },
  { id: "insurance", title: "Renew the car insurance", note: "Due today", done: false },
  { id: "vet", title: "Book the vet for Pepe", note: "Annual jabs", done: false },
  { id: "boiler", title: "Reply to the landlord about the boiler", done: false },
  { id: "roadmap", title: "Outline the Q4 roadmap", note: "Draft for Friday", done: false },
  { id: "shop", title: "Olive oil, bread, pecorino", done: true },
  { id: "lemon", title: "Water the lemon tree", done: true },
];

// --- Places --------------------------------------------------------------------------------

export interface Place {
  readonly name: string;
  readonly href: string;
  /** One or two letters drawn in the tile: a monogram, never a trademark's artwork. */
  readonly mark: string;
}

export const PLACES: readonly Place[] = [
  { name: "Mail", href: "https://app.fastmail.com/", mark: "M" },
  { name: "Calendar", href: "https://calendar.google.com/", mark: "Ca" },
  { name: "Figma", href: "https://www.figma.com/files/", mark: "F" },
  { name: "GitHub", href: "https://github.com/", mark: "Gh" },
  { name: "Linear", href: "https://linear.app/", mark: "Li" },
  { name: "Notion", href: "https://www.notion.so/", mark: "N" },
  { name: "The Guardian", href: "https://www.theguardian.com/", mark: "G" },
  { name: "Il Post", href: "https://www.ilpost.it/", mark: "IP" },
  { name: "Wikipedia", href: "https://en.wikipedia.org/", mark: "W" },
  { name: "Trenitalia", href: "https://www.trenitalia.com/", mark: "T" },
  { name: "Maps", href: "https://www.openstreetmap.org/#map=13/43.3188/11.3308", mark: "Ma" },
  { name: "YouTube", href: "https://www.youtube.com/", mark: "Y" },
];
