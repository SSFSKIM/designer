/**
 * The park's content: twelve trails, the day's conditions, a three-day forecast and the permit
 * rules, as of Saturday 27 September 2026.
 *
 * Realistic rather than live. Distances, gains, high points and trailheads are the published
 * figures for these trails as best known when the page was written; the conditions, the forecast
 * and the closure are composed for the page and dated, so the page says so in its footer rather
 * than passing them off as today's bulletin.
 */

export type CorridorId = "sr20" | "cascade-river" | "north";
export type Status = "open" | "caution" | "closed";
export type Difficulty = "Easy" | "Moderate" | "Strenuous";

export interface Corridor {
  readonly id: CorridorId;
  readonly name: string;
  readonly access: string;
}

export const CORRIDORS: readonly Corridor[] = [
  {
    id: "sr20",
    name: "Highway 20: Skagit gorge and Diablo",
    access: "Trailheads along State Route 20 between Newhalem and Washington Pass",
  },
  {
    id: "cascade-river",
    name: "Cascade River Road",
    access: "23 miles east of Marblemount; the last 14 are gravel",
  },
  {
    id: "north",
    name: "Ross Lake and the North Unit",
    access: "By water taxi up Ross Lake, or over Hannegan Pass from the Mount Baker Highway",
  },
];

export interface Overnight {
  /** Whether a permit is needed for the route at all, or only if you camp. */
  readonly required: "always" | "if-camping";
  readonly camps: readonly string[];
}

export interface Trail {
  readonly id: string;
  readonly name: string;
  readonly corridor: CorridorId;
  readonly trailhead: string;
  readonly trailheadFt: number;
  readonly distanceMi: number;
  readonly shape: "round trip" | "loop";
  readonly gainFt: number;
  readonly highFt: number;
  readonly difficulty: Difficulty;
  readonly time: string;
  readonly status: Status;
  /** One line, as the ranger wrote it. */
  readonly condition: string;
  readonly updated: string;
  readonly overnight?: Overnight;
  readonly parking: "none" | "Northwest Forest Pass";
}

export const TRAILS: readonly Trail[] = [
  {
    id: "trail-of-the-cedars",
    name: "Trail of the Cedars",
    corridor: "sr20",
    trailhead: "Newhalem, across the suspension bridge",
    trailheadFt: 500,
    distanceMi: 0.3,
    shape: "loop",
    gainFt: 20,
    highFt: 520,
    difficulty: "Easy",
    time: "20 min",
    status: "open",
    condition: "Boardwalk wet but firm. Step-free from the Newhalem day-use lot.",
    updated: "27 Sep",
    parking: "none",
  },
  {
    id: "thunder-knob",
    name: "Thunder Knob",
    corridor: "sr20",
    trailhead: "Colonial Creek Campground, north loop",
    trailheadFt: 1240,
    distanceMi: 3.6,
    shape: "round trip",
    gainFt: 635,
    highFt: 1875,
    difficulty: "Easy",
    time: "2 h",
    status: "open",
    condition: "Clear to both viewpoints over Diablo Lake. North loop closes for the season 13 Oct.",
    updated: "27 Sep",
    parking: "none",
  },
  {
    id: "pyramid-lake",
    name: "Pyramid Lake",
    corridor: "sr20",
    trailhead: "SR 20, milepost 126.8",
    trailheadFt: 1100,
    distanceMi: 4.2,
    shape: "round trip",
    gainFt: 1500,
    highFt: 2600,
    difficulty: "Moderate",
    time: "2–3 h",
    status: "open",
    condition: "Steep and rooty, slick after this morning's showers. Roadside parking for eight cars.",
    updated: "27 Sep",
    parking: "none",
  },
  {
    id: "diablo-lake",
    name: "Diablo Lake Trail",
    corridor: "sr20",
    trailhead: "Diablo Lake Resort road, near Diablo Dam",
    trailheadFt: 1220,
    distanceMi: 7.6,
    shape: "round trip",
    gainFt: 1400,
    highFt: 2100,
    difficulty: "Moderate",
    time: "4 h",
    status: "open",
    condition: "Open to Ross Dam. The Seattle City Light boat stops running after 30 Sep; walk back.",
    updated: "26 Sep",
    parking: "none",
  },
  {
    id: "sourdough",
    name: "Sourdough Mountain",
    corridor: "sr20",
    trailhead: "Diablo townsite, behind the swimming pool",
    trailheadFt: 900,
    distanceMi: 10.4,
    shape: "round trip",
    gainFt: 5085,
    highFt: 5985,
    difficulty: "Strenuous",
    time: "7–9 h",
    status: "open",
    condition: "No water above Sourdough Creek; carry three litres. The lookout's catwalk is open.",
    updated: "25 Sep",
    parking: "none",
    overnight: { required: "if-camping", camps: ["Sourdough Camp"] },
  },
  {
    id: "thornton-lakes",
    name: "Thornton Lakes",
    corridor: "sr20",
    trailhead: "Thornton Lakes Road, SR 20 milepost 117",
    trailheadFt: 2700,
    distanceMi: 10.4,
    shape: "round trip",
    gainFt: 2900,
    highFt: 5000,
    difficulty: "Strenuous",
    time: "6–7 h",
    status: "closed",
    condition: "Access road washed out at mile 2.1 on 24 Sep. No vehicles; repairs week of 6 Oct.",
    updated: "24 Sep",
    parking: "none",
    overnight: { required: "if-camping", camps: ["Lower Thornton Lake"] },
  },
  {
    id: "easy-pass",
    name: "Easy Pass",
    corridor: "sr20",
    trailhead: "SR 20, milepost 151 (national forest)",
    trailheadFt: 3700,
    distanceMi: 7.2,
    shape: "round trip",
    gainFt: 2800,
    highFt: 6500,
    difficulty: "Strenuous",
    time: "5–6 h",
    status: "caution",
    condition: "Loose talus and a firm snow patch below the pass; kick steps before 11 am.",
    updated: "26 Sep",
    parking: "Northwest Forest Pass",
  },
  {
    id: "cascade-pass",
    name: "Cascade Pass",
    corridor: "cascade-river",
    trailhead: "End of Cascade River Road",
    trailheadFt: 3600,
    distanceMi: 7.4,
    shape: "round trip",
    gainFt: 1800,
    highFt: 5400,
    difficulty: "Moderate",
    time: "4–5 h",
    status: "open",
    condition: "Snow-free to the pass. A black bear is working Pelton Basin; the lot fills by 8 am.",
    updated: "27 Sep",
    parking: "none",
    overnight: { required: "if-camping", camps: ["Pelton Basin"] },
  },
  {
    id: "sahale-arm",
    name: "Sahale Arm",
    corridor: "cascade-river",
    trailhead: "End of Cascade River Road, over Cascade Pass",
    trailheadFt: 3600,
    distanceMi: 11.8,
    shape: "round trip",
    gainFt: 4000,
    highFt: 7600,
    difficulty: "Strenuous",
    time: "8–10 h",
    status: "caution",
    condition: "8 cm of new snow above 6,800 ft since Thursday. Microspikes for the upper arm.",
    updated: "27 Sep",
    parking: "none",
    overnight: { required: "if-camping", camps: ["Sahale Glacier Camp", "Pelton Basin"] },
  },
  {
    id: "hidden-lake",
    name: "Hidden Lake Lookout",
    corridor: "cascade-river",
    trailhead: "Sibley Creek Road, FS 1540 (national forest)",
    trailheadFt: 3600,
    distanceMi: 9,
    shape: "round trip",
    gainFt: 3300,
    highFt: 6890,
    difficulty: "Strenuous",
    time: "6–7 h",
    status: "caution",
    condition: "Snow on the final traverse to the lookout. Without traction, turn back at the saddle.",
    updated: "26 Sep",
    parking: "Northwest Forest Pass",
  },
  {
    id: "desolation-peak",
    name: "Desolation Peak",
    corridor: "north",
    trailhead: "Desolation Landing, Ross Lake (water taxi)",
    trailheadFt: 1600,
    distanceMi: 13.6,
    shape: "round trip",
    gainFt: 4400,
    highFt: 6085,
    difficulty: "Strenuous",
    time: "8–9 h",
    status: "open",
    condition: "Dry above the landing; carry all your water. Water taxi daily to 31 Oct, book ahead.",
    updated: "25 Sep",
    parking: "none",
    overnight: { required: "if-camping", camps: ["Desolation Camp", "Lightning Creek"] },
  },
  {
    id: "copper-ridge",
    name: "Copper Ridge Loop",
    corridor: "north",
    trailhead: "Hannegan Pass trailhead (national forest)",
    trailheadFt: 3100,
    distanceMi: 34.5,
    shape: "loop",
    gainFt: 10300,
    highFt: 6260,
    difficulty: "Strenuous",
    time: "4–5 days",
    status: "open",
    condition: "Chilliwack cable car running; ford at low water only. Ridge camps are snow-free.",
    updated: "26 Sep",
    parking: "Northwest Forest Pass",
    overnight: {
      required: "always",
      camps: ["Boundary Camp", "Egg Lake", "Copper Lake", "Indian Creek", "U.S. Cabin"],
    },
  },
];

export const DEFAULT_TRAIL_ID = "cascade-pass";

export function trailById(id: string): Trail {
  return TRAILS.find((trail) => trail.id === id) ?? (TRAILS[7] as Trail);
}

const GROUPING = new Intl.NumberFormat("en-US");

export const formatFt = (feet: number): string => `${GROUPING.format(feet)} ft`;
export const formatMi = (miles: number): string =>
  `${miles < 1 ? miles.toFixed(1) : miles % 1 === 0 ? miles.toFixed(0) : miles.toFixed(1)} mi`;

export const STATUS_LABEL: Record<Status, string> = {
  open: "Open",
  caution: "Caution",
  closed: "Closed",
};

/* ── Weather ─────────────────────────────────────────────────────────────── */

export type Sky = "showers" | "clearing" | "sun" | "rain" | "snow" | "snow-showers";

export interface ForecastDay {
  readonly day: string;
  readonly date: string;
  /** High and low at 500 ft, the valley floor at Newhalem. */
  readonly valleyHighF: number;
  readonly valleyLowF: number;
  readonly precipitation: number;
  /** The level above which the day's precipitation falls as snow; undefined on a dry day. */
  readonly snowLevelFt?: number;
  readonly freezingLevelFt: number;
  readonly sky: "showers-clearing" | "sun" | "rain";
  readonly sunset: string;
}

export const FORECAST: readonly ForecastDay[] = [
  {
    day: "Today",
    date: "Sat 27",
    valleyHighF: 58,
    valleyLowF: 45,
    precipitation: 40,
    snowLevelFt: 6800,
    freezingLevelFt: 7300,
    sky: "showers-clearing",
    sunset: "6:57 pm",
  },
  {
    day: "Sunday",
    date: "Sun 28",
    valleyHighF: 64,
    valleyLowF: 43,
    precipitation: 5,
    freezingLevelFt: 9500,
    sky: "sun",
    sunset: "6:55 pm",
  },
  {
    day: "Monday",
    date: "Mon 29",
    valleyHighF: 54,
    valleyLowF: 47,
    precipitation: 90,
    snowLevelFt: 5800,
    freezingLevelFt: 6300,
    sky: "rain",
    sunset: "6:53 pm",
  },
];

/** A standard lapse rate: 3.5 °F per thousand feet above the valley floor at 500 ft. */
const LAPSE_F_PER_1000FT = 3.5;

export interface PointForecast {
  readonly highF: number;
  readonly lowF: number;
  readonly sky: Sky;
  readonly word: string;
}

export function forecastAt(day: ForecastDay, elevationFt: number): PointForecast {
  const drop = ((elevationFt - 500) / 1000) * LAPSE_F_PER_1000FT;
  const highF = Math.round(day.valleyHighF - drop);
  const lowF = Math.round(day.valleyLowF - drop);
  const aboveSnow = day.snowLevelFt !== undefined && elevationFt >= day.snowLevelFt;
  if (day.sky === "sun") return { highF, lowF, sky: "sun", word: "Sunny" };
  if (day.sky === "rain") {
    return aboveSnow
      ? { highF, lowF, sky: "snow", word: "Snow" }
      : { highF, lowF, sky: "rain", word: "Rain" };
  }
  return aboveSnow
    ? { highF, lowF, sky: "snow-showers", word: "Snow showers" }
    : { highF, lowF, sky: "showers", word: "Showers, clearing" };
}

/* ── Conditions bulletin ─────────────────────────────────────────────────── */

export interface Bulletin {
  readonly heading: string;
  readonly entries: readonly { readonly date: string; readonly text: string; readonly trails?: readonly string[] }[];
}

export const BULLETIN: readonly Bulletin[] = [
  {
    heading: "Roads and access",
    entries: [
      {
        date: "27 Sep",
        text: "State Route 20 is open over Rainy and Washington passes. The passes close for the winter when snow arrives, usually in November; check WSDOT before you drive east of Colonial Creek.",
        trails: ["easy-pass"],
      },
      {
        date: "27 Sep",
        text: "Cascade River Road is open to the Cascade Pass trailhead. Potholes past milepost 20; allow an hour from Marblemount.",
        trails: ["cascade-pass", "sahale-arm", "hidden-lake"],
      },
      {
        date: "24 Sep",
        text: "Thornton Lakes Road washed out at mile 2.1 after Tuesday's storm. No vehicle access to the trailhead until repairs, scheduled for the week of 6 October.",
        trails: ["thornton-lakes"],
      },
      {
        date: "22 Sep",
        text: "Ross Lake Resort's water taxi runs daily through 31 October. Book a day ahead; the last boat leaves Desolation Landing at 4 pm.",
        trails: ["desolation-peak"],
      },
    ],
  },
  {
    heading: "Snow and weather",
    entries: [
      {
        date: "27 Sep",
        text: "The season's first snow fell Thursday: 5 to 10 cm above 6,800 ft on Sahale Arm, Hidden Lake and the slopes above Easy Pass. It is firm in the morning and slushy by afternoon.",
        trails: ["sahale-arm", "hidden-lake", "easy-pass"],
      },
      {
        date: "27 Sep",
        text: "Showers end by midday and Sunday is clear, with the freezing level near 9,500 ft. A wet front arrives Monday with snow down to 5,800 ft; plan high routes for Sunday.",
      },
    ],
  },
  {
    heading: "Hazards and wildlife",
    entries: [
      {
        date: "26 Sep",
        text: "A black bear is feeding on blueberries in Pelton Basin and along the upper switchbacks to Cascade Pass. Use the camp's food lockers; never leave a pack unattended.",
        trails: ["cascade-pass", "sahale-arm"],
      },
      {
        date: "25 Sep",
        text: "Deer rifle season opens 11 October in Ross Lake National Recreation Area, where hunting is permitted. Wear orange on the Diablo Lake and Desolation trails.",
        trails: ["diablo-lake", "desolation-peak"],
      },
      {
        date: "20 Sep",
        text: "Fire danger is moderate. Campfires only in the fire rings at lakeshore camps; none above 3,500 ft.",
      },
    ],
  },
];

/* ── Permits ─────────────────────────────────────────────────────────────── */

export interface PermitStep {
  readonly title: string;
  readonly body: string;
  /** False where the step does not apply to this route and is shown struck through in words. */
  readonly applies: boolean;
}

export function permitSteps(trail: Trail): readonly PermitStep[] {
  const camps = trail.overnight?.camps ?? [];
  const campList = camps.length > 1 ? `${camps.slice(0, -1).join(", ")} and ${camps.at(-1) ?? ""}` : (camps[0] ?? "");
  const alwaysOvernight = trail.overnight?.required === "always";

  const decide: PermitStep = alwaysOvernight
    ? {
        title: "Plan your nights",
        body: `${trail.name} is a ${trail.time} trip, so every night needs a wilderness permit, issued for named camps: ${campList}.`,
        applies: true,
      }
    : camps.length > 0
      ? {
          title: "Day hike or overnight",
          body: `A day hike on ${trail.name} needs no permit. To sleep out, you need a wilderness permit for a named camp: ${campList}.`,
          applies: true,
        }
      : {
          title: "Day hike",
          body: `${trail.name} is a day hike with no backcountry camp, so there is no wilderness permit to get.`,
          applies: true,
        };

  const reserve: PermitStep =
    camps.length > 0
      ? {
          title: "Reserve the camps",
          body: "Most camps are reservable on Recreation.gov for the season. The rest are held for walk-up permits, issued the day before or the morning of your trip at the Wilderness Information Center in Marblemount, 7 am to 6 pm.",
          applies: true,
        }
      : {
          title: "Reserve the camps",
          body: "Nothing to reserve on this route.",
          applies: false,
        };

  const parking: PermitStep =
    trail.parking === "Northwest Forest Pass"
      ? {
          title: "Display a parking pass",
          body: "The trailhead is on national forest land: display a Northwest Forest Pass or an Interagency (America the Beautiful) pass on the dashboard.",
          applies: true,
        }
      : {
          title: "Display a parking pass",
          body: "The trailhead is inside the park complex, which charges no entrance or parking fee.",
          applies: false,
        };

  const carry: PermitStep =
    camps.length > 0
      ? {
          title: "Carry it, and store food",
          body: "Keep the permit with you on the trail. Use the camp's food locker where there is one and a hard-sided container where there is not.",
          applies: true,
        }
      : {
          title: "Carry the essentials",
          body:
            trail.highFt >= 6800
              ? "No permit to carry. This week, carry microspikes: the route climbs above the snow line."
              : "No permit to carry. Bring a layer and a headlamp; sunset is before 7 pm.",
          applies: true,
        };

  return [decide, reserve, parking, carry];
}

export const PHOTO_CREDIT = {
  photographer: "Pete Alexopoulos",
  profile: "https://unsplash.com/@pete_a",
  photo: "https://unsplash.com/photos/a-large-body-of-water-surrounded-by-mountains-LtvmhSsLN4k",
  caption: "Diablo Lake from the overlook on the North Cascades Highway",
};
