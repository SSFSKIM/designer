/**
 * The programme: four days, three cinemas, twenty-four films, each screened once.
 *
 * The festival, its cinemas and nineteen of the films are invented for the demo. The five films in
 * the Restored strand are real, with their real directors, years and running times, because a
 * festival's archive strand is exactly where a real programme puts real classics. Every screening
 * was laid out against the running times so that no cinema ever shows two films at once and each
 * leaves at least half an hour to turn the room round.
 */

export type DayId = "thu" | "fri" | "sat" | "sun";
export type VenueId = "regent" | "tolbooth" | "shed9";
export type StrandId = "galas" | "coasts" | "first" | "weather" | "restored";
export type PassId = "single" | "day" | "festival" | "opening";

export interface Day {
  readonly id: DayId;
  /** The segment's label in the bar. */
  readonly short: string;
  readonly long: string;
}

export interface Venue {
  readonly id: VenueId;
  readonly name: string;
  readonly address: string;
  readonly seats: number;
  readonly access: string;
}

export interface Strand {
  readonly id: StrandId;
  readonly name: string;
  readonly line: string;
}

export interface Film {
  readonly id: string;
  readonly title: string;
  readonly director: string;
  readonly country: string;
  readonly year: number;
  readonly minutes: number;
  readonly strand: StrandId;
  /** Galas carry their own billing ("Opening night"), which the schedule prints instead. */
  readonly billing?: string;
  readonly line: string;
}

export interface Screening {
  readonly film: string;
  readonly day: DayId;
  readonly venue: VenueId;
  /** "HH:MM", 24-hour. */
  readonly start: string;
}

export interface Pass {
  readonly id: PassId;
  readonly name: string;
  readonly price: number;
  readonly detail: string;
}

export const FESTIVAL = {
  name: "Northlight",
  full: "Northlight Film Festival",
  edition: "12th edition",
  dates: "18–21 February 2027",
} as const;

export const DAYS: readonly Day[] = [
  { id: "thu", short: "Thu 18", long: "Thursday 18 February" },
  { id: "fri", short: "Fri 19", long: "Friday 19 February" },
  { id: "sat", short: "Sat 20", long: "Saturday 20 February" },
  { id: "sun", short: "Sun 21", long: "Sunday 21 February" },
];

export const VENUES: readonly Venue[] = [
  {
    id: "regent",
    name: "The Regent",
    address: "Regent Picture House, 41 Quay Street",
    seats: 612,
    access: "A 1931 picture house. Step-free to the stalls, six wheelchair spaces, hearing loop.",
  },
  {
    id: "tolbooth",
    name: "Tolbooth",
    address: "Tolbooth Cinema, 3 Tolbooth Wynd",
    seats: 184,
    access: "Step-free throughout, hearing loop, audio description at every screening.",
  },
  {
    id: "shed9",
    name: "Shed 9",
    address: "Shed 9, Albert Quay",
    seats: 96,
    access: "A converted fish-market shed. Step-free, relaxed screenings all day Sunday.",
  },
];

export const STRANDS: readonly Strand[] = [
  { id: "galas", name: "Galas", line: "Opening, centrepiece and closing night at the Regent." },
  { id: "coasts", name: "Cold Coasts", line: "Films from northern seas, islands and harbour towns." },
  {
    id: "first",
    name: "First Light",
    line: "First and second features, in competition for the Northlight Prize.",
  },
  { id: "weather", name: "Real Weather", line: "Documentary: work, places and people in winter." },
  {
    id: "restored",
    name: "Restored",
    line: "Five classics of cold places, restored for the big screen.",
  },
];

export const FILMS: readonly Film[] = [
  // Galas
  {
    id: "ironai",
    title: "Ironai",
    director: "Aoi Hayama",
    country: "Japan",
    year: 2026,
    minutes: 112,
    strand: "galas",
    billing: "Opening night",
    line: "Three strangers cross one Otaru street on the morning of the first heavy snow; the film follows each of them to nightfall.",
  },
  {
    id: "salt-road",
    title: "The Salt Road",
    director: "Ingrid Solberg",
    country: "Norway, Denmark",
    year: 2026,
    minutes: 104,
    strand: "galas",
    billing: "Centrepiece",
    line: "A lorry driver and her estranged brother haul the last load of the season over the mountain before the pass closes.",
  },
  {
    id: "haar",
    title: "Haar",
    director: "Morag Lindsay",
    country: "United Kingdom",
    year: 2027,
    minutes: 96,
    strand: "galas",
    billing: "Closing night",
    line: "A ferryman's daughter walks the shore every morning the sea fog comes in, waiting for a boat the harbour has stopped expecting.",
  },
  // Cold Coasts
  {
    id: "kittiwake",
    title: "Kittiwake",
    director: "Sunna Hallgrímsdóttir",
    country: "Iceland",
    year: 2026,
    minutes: 88,
    strand: "coasts",
    line: "A seabird counter spends a winter alone on a cliff island and begins to count other things.",
  },
  {
    id: "driftwood",
    title: "Driftwood Parish",
    director: "Tomás Ó Floinn",
    country: "Ireland",
    year: 2026,
    minutes: 101,
    strand: "coasts",
    line: "The last priest of an island parish is asked to bless the causeway that will empty it.",
  },
  {
    id: "keeper",
    title: "The Lighthouse Keeper's Accounts",
    director: "Eero Salminen",
    country: "Finland",
    year: 2025,
    minutes: 79,
    strand: "coasts",
    line: "Forty years of a keeper's ledgers, read aloud over the light they paid for.",
  },
  {
    id: "wintering",
    title: "Wintering",
    director: "Maren Aas",
    country: "Norway",
    year: 2026,
    minutes: 93,
    strand: "coasts",
    line: "A fishing family sits out the polar night in Lofoten, and one of them decides not to.",
  },
  {
    id: "hokkaido-line",
    title: "Hokkaido Line",
    director: "Kenji Morita",
    country: "Japan",
    year: 2026,
    minutes: 118,
    strand: "coasts",
    line: "A retired conductor rides the coastal railway one last time before the line is closed.",
  },
  // First Light
  {
    id: "bakery",
    title: "A Room Above the Bakery",
    director: "Lena Vogt",
    country: "Germany",
    year: 2026,
    minutes: 97,
    strand: "first",
    line: "Two students share a flat that is warm only between four and seven in the morning.",
  },
  {
    id: "low-tide",
    title: "Low Tide Hours",
    director: "Priya Raman",
    country: "United Kingdom",
    year: 2026,
    minutes: 84,
    strand: "first",
    line: "A night-shift nurse and a cockle picker keep missing each other by the length of a tide.",
  },
  {
    id: "river-keeps",
    title: "Everything the River Keeps",
    director: "Ana Belén Ortiz",
    country: "Spain",
    year: 2026,
    minutes: 109,
    strand: "first",
    line: "A drought uncovers a drowned village, and the woman who left it comes back to see.",
  },
  {
    id: "signal",
    title: "Signal",
    director: "Jonas Petrauskas",
    country: "Lithuania",
    year: 2026,
    minutes: 91,
    strand: "first",
    line: "A radio ham on the Curonian Spit hears a voice he recognises from forty years ago.",
  },
  {
    id: "night-porter",
    title: "The Night Porter's Son",
    director: "Farid Haddad",
    country: "Lebanon, France",
    year: 2026,
    minutes: 103,
    strand: "first",
    line: "A boy grows up in the corridors of a Beirut hotel that never quite closes.",
  },
  {
    id: "glasshouse",
    title: "Glasshouse",
    director: "Martina Kovač",
    country: "Croatia",
    year: 2026,
    minutes: 95,
    strand: "first",
    line: "Three sisters inherit a tomato farm and a greenhouse that nobody can afford to heat.",
  },
  // Real Weather
  {
    id: "snow-clearing",
    title: "Snow Clearing, Line 4",
    director: "Hanna Berg",
    country: "Sweden",
    year: 2026,
    minutes: 74,
    strand: "weather",
    line: "One night with the plough crews who keep a city's buses running through a blizzard.",
  },
  {
    id: "ice-road",
    title: "The Last Ice Road",
    director: "Daniel Okafor",
    country: "Canada",
    year: 2026,
    minutes: 92,
    strand: "weather",
    line: "Truckers on a winter road across frozen lakes, in the year it may not freeze at all.",
  },
  {
    id: "forecast",
    title: "Forecast",
    director: "Marie Duval",
    country: "France",
    year: 2025,
    minutes: 81,
    strand: "weather",
    line: "A mountain weather station and the two observers who have not missed a reading in nine years.",
  },
  {
    id: "harbour-sounds",
    title: "Harbour Sounds",
    director: "Ciarán Walsh",
    country: "Ireland",
    year: 2026,
    minutes: 66,
    strand: "weather",
    line: "A working harbour recorded through one winter, from the fish market to the foghorn.",
  },
  {
    id: "cold-store",
    title: "A Year in the Cold Store",
    director: "Yuki Tanabe",
    country: "Japan",
    year: 2026,
    minutes: 88,
    strand: "weather",
    line: "Inside a Hokkaido seafood warehouse held at minus twenty-five, season by season.",
  },
  // Restored: real films, real credits
  {
    id: "winter-light",
    title: "Winter Light",
    director: "Ingmar Bergman",
    country: "Sweden",
    year: 1963,
    minutes: 81,
    strand: "restored",
    line: "A country pastor loses his congregation, and his faith, over one winter Sunday.",
  },
  {
    id: "the-idiot",
    title: "The Idiot",
    director: "Akira Kurosawa",
    country: "Japan",
    year: 1951,
    minutes: 166,
    strand: "restored",
    line: "Kurosawa moves Dostoevsky to a snowbound Sapporo.",
  },
  {
    id: "nanook",
    title: "Nanook of the North",
    director: "Robert J. Flaherty",
    country: "United States",
    year: 1922,
    minutes: 79,
    strand: "restored",
    line: "The founding documentary of the Arctic, screened with a live score.",
  },
  {
    id: "local-hero",
    title: "Local Hero",
    director: "Bill Forsyth",
    country: "United Kingdom",
    year: 1983,
    minutes: 111,
    strand: "restored",
    line: "An oil man is sent from Houston to buy a Scottish fishing village and cannot bring himself to.",
  },
  {
    id: "whisky-galore",
    title: "Whisky Galore!",
    director: "Alexander Mackendrick",
    country: "United Kingdom",
    year: 1949,
    minutes: 82,
    strand: "restored",
    line: "A ship runs aground off a dry Hebridean island with fifty thousand cases aboard.",
  },
];

export const SCREENINGS: readonly Screening[] = [
  // Thursday: opening night
  { film: "winter-light", day: "thu", venue: "tolbooth", start: "18:00" },
  { film: "ironai", day: "thu", venue: "regent", start: "19:30" },
  { film: "harbour-sounds", day: "thu", venue: "shed9", start: "20:00" },
  { film: "low-tide", day: "thu", venue: "tolbooth", start: "20:30" },
  // Friday
  { film: "forecast", day: "fri", venue: "tolbooth", start: "13:30" },
  { film: "the-idiot", day: "fri", venue: "regent", start: "15:00" },
  { film: "bakery", day: "fri", venue: "tolbooth", start: "16:15" },
  { film: "snow-clearing", day: "fri", venue: "shed9", start: "17:00" },
  { film: "kittiwake", day: "fri", venue: "tolbooth", start: "19:15" },
  { film: "hokkaido-line", day: "fri", venue: "regent", start: "20:00" },
  { film: "signal", day: "fri", venue: "shed9", start: "20:30" },
  // Saturday
  { film: "nanook", day: "sat", venue: "regent", start: "11:00" },
  { film: "river-keeps", day: "sat", venue: "tolbooth", start: "13:00" },
  { film: "ice-road", day: "sat", venue: "shed9", start: "14:00" },
  { film: "local-hero", day: "sat", venue: "regent", start: "15:30" },
  { film: "driftwood", day: "sat", venue: "tolbooth", start: "18:00" },
  { film: "salt-road", day: "sat", venue: "regent", start: "19:30" },
  { film: "glasshouse", day: "sat", venue: "shed9", start: "20:00" },
  // Sunday
  { film: "keeper", day: "sun", venue: "tolbooth", start: "12:00" },
  { film: "whisky-galore", day: "sun", venue: "regent", start: "13:30" },
  { film: "cold-store", day: "sun", venue: "shed9", start: "14:30" },
  { film: "night-porter", day: "sun", venue: "tolbooth", start: "16:00" },
  { film: "wintering", day: "sun", venue: "shed9", start: "17:00" },
  { film: "haar", day: "sun", venue: "regent", start: "19:00" },
];

export const PASSES: readonly Pass[] = [
  {
    id: "single",
    name: "Single ticket",
    price: 11,
    detail: "Any screening except the three galas. £8 for concessions and under-26s.",
  },
  {
    id: "day",
    name: "Day pass",
    price: 30,
    detail: "Every screening on one day, Friday, Saturday or Sunday. Galas not included.",
  },
  {
    id: "festival",
    name: "Festival pass",
    price: 96,
    detail: "All twenty-four films, galas included, with entry fifteen minutes before doors.",
  },
  {
    id: "opening",
    name: "Opening night",
    price: 20,
    detail: "Ironai at the Regent on Thursday, and the reception in the circle bar from 18:30.",
  },
];

const filmsById = new Map(FILMS.map((film) => [film.id, film]));

export function filmOf(screening: Screening): Film {
  const film = filmsById.get(screening.film);
  if (film === undefined) throw new Error(`No film "${screening.film}" in the programme.`);
  return film;
}

export function strandOf(id: StrandId): Strand {
  const strand = STRANDS.find((candidate) => candidate.id === id);
  if (strand === undefined) throw new Error(`No strand "${id}".`);
  return strand;
}

export function venueOf(id: VenueId): Venue {
  const venue = VENUES.find((candidate) => candidate.id === id);
  if (venue === undefined) throw new Error(`No venue "${id}".`);
  return venue;
}

export function dayOf(id: DayId): Day {
  const day = DAYS.find((candidate) => candidate.id === id);
  if (day === undefined) throw new Error(`No day "${id}".`);
  return day;
}

/** Minutes after midnight. */
export function minutesOf(time: string): number {
  const [hours, minutes] = time.split(":").map(Number);
  return (hours ?? 0) * 60 + (minutes ?? 0);
}

export function clock(minutes: number): string {
  const h = Math.floor(minutes / 60);
  const m = minutes % 60;
  return `${String(h).padStart(2, "0")}:${String(m).padStart(2, "0")}`;
}

export function screeningOf(filmId: string): Screening {
  const screening = SCREENINGS.find((candidate) => candidate.film === filmId);
  if (screening === undefined) throw new Error(`"${filmId}" has no screening.`);
  return screening;
}
