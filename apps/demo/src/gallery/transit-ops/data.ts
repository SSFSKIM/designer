/**
 * Port Alder: the city, its eight bus routes, forty vehicles and six alerts.
 *
 * Everything is in world metres, x east and y south, with the network roughly inside
 * 0..8000 by -600..5600. The city is drawn well past the network on every side,
 * because the map is full-bleed and the glass sidebar and top bar sit over the parts
 * of the city the network does not reach: those parts still need structure for the
 * lens to bend (DESIGN.md, plane).
 *
 * The data is fictional and written to read like a real control room's: fleet numbers
 * come in vehicle series rather than per route, blocks are route-run pairs, statuses
 * are schedule deviations in minutes, and each alert names what a dispatcher would
 * need to act on it.
 */

export type Point = readonly [number, number];

// ---------------------------------------------------------------------------------
// Geography

/** The Alder river, east to west: centreline points with a width in metres. */
export const RIVER: readonly (readonly [number, number, number])[] = [
  [12000, 1450, 170],
  [9000, 1560, 175],
  [8000, 1700, 180],
  [7000, 1860, 190],
  [6100, 2150, 205],
  [5200, 2160, 210],
  [4500, 2300, 220],
  [3900, 2450, 230],
  [3300, 2500, 240],
  [2700, 2560, 250],
  [2100, 2800, 270],
  [1600, 3150, 300],
  [1250, 3580, 360],
];

/** Port Alder harbour: the bay the river opens into, south-west of the old town. */
export const HARBOUR: readonly Point[] = [
  [-7000, 2640],
  [-1900, 2720],
  [-600, 2930],
  [300, 3080],
  [900, 3280],
  [1250, 3480],
  [1450, 3800],
  [1500, 4300],
  [1360, 4900],
  [1120, 5600],
  [1300, 6400],
  [1000, 11000],
  [-7000, 11000],
];

/** Piers along the harbour: rectangles given as a shore point, a direction and a size. */
export const PIERS: readonly { at: Point; dir: Point; length: number; width: number }[] = [
  { at: [-6000, 2650], dir: [0, 1], length: 520, width: 90 },
  { at: [-5500, 2655], dir: [0, 1], length: 560, width: 110 },
  { at: [-4950, 2660], dir: [0, 1], length: 500, width: 90 },
  { at: [-4400, 2665], dir: [0, 1], length: 460, width: 70 },
  { at: [-3900, 2675], dir: [0, 1], length: 420, width: 70 },
  { at: [-3400, 2690], dir: [0, 1], length: 420, width: 70 },
  { at: [-3000, 2685], dir: [0, 1], length: 360, width: 70 },
  { at: [-2600, 2680], dir: [0, 1], length: 420, width: 70 },
  { at: [-2200, 2700], dir: [0, 1], length: 300, width: 60 },
  { at: [-1600, 2765], dir: [0.12, 1], length: 380, width: 70 },
  { at: [-1250, 2830], dir: [0.14, 1], length: 380, width: 70 },
  { at: [-900, 2880], dir: [0.16, 1], length: 380, width: 70 },
  { at: [-550, 2935], dir: [0.16, 1], length: 360, width: 70 },
  { at: [1470, 4000], dir: [-1, 0.05], length: 340, width: 90 },
  { at: [1480, 4350], dir: [-1, 0.05], length: 360, width: 90 },
  { at: [1420, 4700], dir: [-1, 0.1], length: 320, width: 90 },
  { at: [1280, 5200], dir: [-1, 0.15], length: 300, width: 80 },
];

/**
 * The harbour's own structure, as a chart draws it: depth contours (isobaths), the
 * dredged channel to the container terminal, the breakwater at the mouth and the
 * marina's pontoons. Under the sidebar the harbour would otherwise be a flat field,
 * and glass over a flat field has nothing to bend (SKILL.md, the live plane).
 */
export const ISOBATHS: readonly (readonly Point[])[] = [
  [[-7000, 2960], [-5200, 3010], [-3400, 3060], [-1900, 3010], [-600, 3230], [300, 3390], [850, 3610], [1150, 3920], [1200, 4400], [1050, 4950], [820, 5600], [950, 6400], [700, 9000]],
  [[-7000, 3420], [-5200, 3520], [-3300, 3500], [-1900, 3430], [-600, 3640], [200, 3820], [600, 4080], [800, 4500], [700, 5000], [480, 5600], [600, 6400], [380, 9000]],
  [[-7000, 4050], [-5400, 4220], [-3600, 4180], [-2000, 4130], [-700, 4330], [-50, 4640], [180, 5200], [80, 6400], [-60, 9000]],
  [[-7000, 4900], [-5000, 5050], [-3000, 5000], [-1300, 5150], [-600, 5500], [-500, 6400], [-700, 9000]],
  [[-7000, 5900], [-4600, 6050], [-2400, 6100], [-1500, 6700], [-1600, 9000]],
];

export const CHANNEL: readonly Point[] = [[-7000, 3780], [-4500, 3860], [-2200, 3870], [-600, 3980], [500, 4280], [1100, 4450]];

export const BREAKWATER: readonly Point[] = [[-6450, 2655], [-6700, 3150], [-6350, 3620]];

/** Marina pontoons: short fingers off a spine, west of the shipyard. */
export const MARINA = { spine: [[-6350, 2700], [-6350, 3050]] as const, fingers: 9, length: 150 };

/** Still water that is not the river: the reservoir and the Commons' pond. */
export const LAKES: readonly { center: Point; rx: number; ry: number; rot: number }[] = [
  { center: [1500, -1250], rx: 620, ry: 330, rot: -0.3 },
  { center: [3360, 190], rx: 170, ry: 80, rot: 0.2 },
  { center: [8200, 4300], rx: 260, ry: 150, rot: 0.5 },
];

export interface District {
  readonly name: string;
  readonly polygon: readonly Point[];
  /** Street grid angle in degrees. */
  readonly angle: number;
  /** Block size in metres. */
  readonly spacing: number;
  /** Built density 0..1: how dark the blocks read. */
  readonly density: number;
  readonly label?: Point;
}

export const DISTRICTS: readonly District[] = [
  {
    name: "Northside",
    polygon: [[-7000, -4000], [1800, -4000], [2300, 1300], [2300, 2500], [-600, 2950], [-7000, 2660]],
    angle: 14,
    spacing: 125,
    density: 0.28,
    label: [-400, 700],
  },
  {
    name: "Old Town",
    polygon: [[2300, 1300], [4600, 1080], [4750, 2220], [3900, 2460], [2600, 2580], [2300, 2500]],
    angle: -8,
    spacing: 82,
    density: 0.85,
    label: [2950, 1560],
  },
  {
    name: "Northcote",
    polygon: [[1800, -4000], [5200, -4000], [4600, 1080], [2300, 1300]],
    angle: 0,
    spacing: 135,
    density: 0.38,
    label: [4200, -150],
  },
  {
    name: "University",
    polygon: [[5200, -4000], [12000, -4000], [12000, 1420], [7000, 1720], [6100, 2000], [4750, 2120], [4600, 1080]],
    angle: -24,
    spacing: 150,
    density: 0.22,
    label: [7000, 700],
  },
  {
    name: "Southbank",
    polygon: [[1600, 3200], [2100, 2850], [2700, 2660], [3300, 2620], [3900, 2570], [4500, 2420], [5200, 2300], [5050, 3120], [2400, 3200]],
    angle: -8,
    spacing: 90,
    density: 0.62,
    label: [2750, 2980],
  },
  {
    name: "Eastgate",
    polygon: [[5200, 2300], [6100, 2300], [7000, 2000], [8000, 1850], [12000, 1600], [12000, 3300], [5050, 3150]],
    angle: -17,
    spacing: 122,
    density: 0.42,
    label: [7600, 2750],
  },
  {
    name: "Mount Pleasant",
    polygon: [[2400, 3150], [12000, 3250], [12000, 11000], [2600, 11000]],
    angle: 0,
    spacing: 100,
    density: 0.32,
    label: [3500, 4700],
  },
  {
    name: "Harbourside",
    polygon: [[1250, 3600], [1600, 3200], [2400, 3150], [2600, 11000], [1000, 11000], [1300, 6400], [1120, 5600], [1360, 4900], [1500, 4300], [1450, 3800]],
    angle: 4,
    spacing: 112,
    density: 0.48,
    label: [2150, 4100],
  },
];

export interface Park {
  readonly name?: string;
  readonly polygon: readonly Point[];
  readonly label?: Point;
}

export const PARKS: readonly Park[] = [
  { name: "The Commons", polygon: [[2960, -170], [3780, -220], [3830, 520], [3010, 580]], label: [3390, -40] },
  { name: "Riverside Park", polygon: [[2320, 2400], [2780, 2330], [3240, 2300], [3250, 2370], [2780, 2410], [2330, 2480]] },
  { name: "Mill Park", polygon: [[5760, 2560], [6420, 2470], [6520, 3010], [5840, 3090]], label: [6140, 2800] },
  { name: "Hilltop Reserve", polygon: [[6300, 3880], [7400, 3660], [7980, 4480], [7050, 5020], [6200, 4700]], label: [7150, 4330] },
  { name: "University Green", polygon: [[5850, -700], [6950, -980], [7250, -40], [6230, 280]], label: [6550, -380] },
  { name: "Gull Point", polygon: [[-6200, 2400], [-4600, 2360], [-4400, 2640], [-6300, 2660]] },
  { name: "Reservoir Park", polygon: [[760, -1640], [1300, -1760], [2150, -1720], [2380, -1300], [2300, -800], [1700, -660], [900, -760], [720, -1180]] },
  { name: "Fraser Fields", polygon: [[5480, 3780], [5980, 3760], [6000, 4060], [5500, 4080]] },
];

/** Rail line through Central Station. */
export const RAIL: readonly Point[] = [
  [-7000, 180],
  [-2000, 560],
  [1000, 930],
  [2300, 1230],
  [3400, 1160],
  [4600, 1000],
  [6500, 1080],
  [12000, 1000],
];

export const CENTRAL_STATION: Point = [2620, 1250];

export interface Road {
  readonly name: string;
  readonly points: readonly Point[];
  /** 2: arterial, 1: collector. */
  readonly rank: 1 | 2;
  /** Where to set the street name, as a segment index and a position along it. */
  readonly labelAt?: readonly [number, number];
}

export const ROADS: readonly Road[] = [
  {
    name: "Market St",
    rank: 2,
    points: [[-7000, 1980], [-600, 1900], [2300, 1820], [3400, 1780], [4700, 1700], [6000, 1550], [7400, 1450], [12000, 1100]],
    labelAt: [1, 0.55],
  },
  {
    name: "Bridge St",
    rank: 2,
    points: [[3400, -4000], [3400, 1780], [3400, 2320], [3400, 2680], [3400, 3150]],
    labelAt: [0, 0.83],
  },
  { name: "Kingsway", rank: 2, points: [[3400, 3150], [9000, 6392]], labelAt: [0, 0.14] },
  {
    name: "Northside Rd",
    rank: 2,
    points: [[-4000, -2600], [-800, -500], [1200, 880], [2300, 1480], [3400, 1780]],
    labelAt: [2, 0.4],
  },
  {
    name: "University Ave",
    rank: 2,
    points: [[3400, 1200], [4600, 1000], [5600, 560], [6600, 180], [9000, -900]],
    labelAt: [2, 0.5],
  },
  {
    name: "Riverside Dr",
    rank: 2,
    points: [[2300, 2310], [3400, 2270], [4500, 2120], [5200, 1990], [6100, 1970], [7000, 1690], [8000, 1530], [12000, 1200]],
    labelAt: [3, 0.5],
  },
  {
    name: "Mill Rd",
    rank: 2,
    points: [[5600, -4000], [5600, 1980], [5600, 2040], [5600, 2280], [5600, 11000]],
    labelAt: [4, 0.2],
  },
  {
    name: "Eastgate Rd",
    rank: 2,
    points: [[1950, 3110], [2400, 3000], [3400, 2800], [4500, 2600], [5600, 2450], [7000, 2250], [8000, 2150], [12000, 2080]],
    labelAt: [4, 0.5],
  },
  {
    name: "Harbour Rd",
    rank: 2,
    points: [[-7000, 2560], [-1900, 2610], [-600, 2820], [400, 2930], [1300, 2800], [1755, 2835], [1950, 3110], [1700, 3700], [1720, 4300], [1580, 4900], [1360, 5600], [1540, 6400], [1300, 11000]],
    labelAt: [1, 0.35],
  },
  {
    name: "North Rd",
    rank: 2,
    points: [[-7000, -700], [-800, -470], [1200, -420], [3400, -420], [5600, -380], [6600, -300], [12000, -200]],
    labelAt: [3, 0.55],
  },
  { name: "Fourth Ave", rank: 1, points: [[2450, 3450], [12000, 3450]], labelAt: [0, 0.62] },
  { name: "Seventh Ave", rank: 1, points: [[2480, 3750], [12000, 3750]] },
  { name: "Ninth Ave", rank: 1, points: [[2500, 3950], [12000, 3950]], labelAt: [0, 0.14] },
  { name: "11th Ave", rank: 1, points: [[2520, 4150], [12000, 4150]] },
  { name: "Fraser St", rank: 1, points: [[5400, 3150], [5400, 11000]], labelAt: [0, 0.075] },
  { name: "Alder St", rank: 1, points: [[4200, 2560], [4200, 11000]] },
  { name: "Quay St", rank: 1, points: [[2300, 1820], [2350, 2400]] },
  { name: "Station St", rank: 1, points: [[2620, 1250], [2680, 1810], [2720, 2300]] },
  { name: "Campus Dr", rank: 1, points: [[6600, -300], [6700, 150], [6760, 700]] },
];

/** The closed section of Kingsway (8th to 10th Ave): drawn dashed, not driven. */
export const CLOSURE: readonly Point[] = [
  [4609, 3850],
  [4955, 4050],
];

/** Where each traffic camera sits, and the still it shows. */
export interface Camera {
  readonly id: string;
  readonly name: string;
  readonly at: Point;
  readonly image: "bridge" | "kingsway";
}

export const CAMERAS: readonly Camera[] = [
  { id: "CAM 14", name: "Victoria Bridge north approach", at: [3430, 2290], image: "bridge" },
  { id: "CAM 31", name: "Kingsway at Ninth Ave", at: [4800, 3930], image: "kingsway" },
];

export interface WaterLabel {
  readonly name: string;
  readonly at: Point;
  readonly angle: number;
}

export const WATER_LABELS: readonly WaterLabel[] = [
  { name: "Alder River", at: [6700, 1975], angle: -17 },
  { name: "Port Alder Harbour", at: [-1400, 3700], angle: 0 },
  { name: "Reservoir", at: [1500, -1250], angle: -17 },
];

export const BRIDGE_LABELS: readonly WaterLabel[] = [
  { name: "Victoria Bridge", at: [3470, 2560], angle: -90 },
  { name: "Mill Bridge", at: [5670, 2230], angle: -90 },
  { name: "Harbour Bridge", at: [1990, 2950], angle: 55 },
];

// ---------------------------------------------------------------------------------
// Routes

export interface Route {
  readonly id: string;
  /** Long name, terminal to terminal. */
  readonly name: string;
  readonly via: string;
  /** OKLCH hue for the route's colour; lightness and chroma are the scheme's. */
  readonly hue: number;
  /** Lateral slot so routes sharing a street draw side by side (-1, 0, 1). */
  readonly slot: number;
  /** The path vehicles drive, including any detour in effect. */
  readonly path: readonly Point[];
  readonly stops: readonly string[];
}

// Kingsway geometry: from Bridge St at (3400, 3150), slope 0.5789 (2200 m down per
// 3800 m east). Avenue n sits at y = 3050 + 100 n.
const kx = (y: number): number => 3400 + (y - 3150) / 0.5789;
const K = (y: number): Point => [Math.round(kx(y)), y];

/** Kingsway through the closure, as a detour: 7th Ave, Fraser St, 11th Ave. */
const KINGSWAY_DETOUR_SOUTHBOUND: readonly Point[] = [K(3750), [5400, 3750], [5400, 4150], K(4150)];

export const ROUTES: readonly Route[] = [
  {
    id: "1",
    name: "Northside – Riverview",
    via: "Market St",
    hue: 255,
    slot: 0,
    path: [[-1400, 1930], [-600, 1900], [2300, 1820], [3400, 1780], [4700, 1700], [6000, 1550], [7400, 1450]],
    stops: [
      "Northside Terminal", "Market St at Gale St", "Market St at Tern Ave", "Market St at Quay St",
      "Bridge St Interchange", "Market St at Alder St", "Market St at Holm St", "Market St at Mill Rd",
      "Market St at Orchard", "Riverview Loop",
    ],
  },
  {
    id: "3",
    name: "Central Station – Eastgate",
    via: "Riverside Dr, Mill Bridge",
    hue: 178,
    slot: 0,
    path: [[2620, 1250], [2680, 1810], [2720, 2300], [3400, 2270], [4500, 2120], [5200, 1990], [5600, 1985], [5600, 2280], [5600, 2450], [7000, 2250], [8000, 2150]],
    stops: [
      "Central Station", "Quay St at Market", "Riverside Dr at Quay", "Riverside Dr at Bridge St",
      "Riverside Dr at Wharf Ln", "Riverside Dr at Mill Rd", "Mill Bridge South", "Eastgate Rd at Mill Park",
      "Eastgate Rd at Pell St", "Eastgate Rd at Ash Grove", "Eastgate Exchange",
    ],
  },
  {
    id: "4",
    name: "Northcote – Hilltop",
    via: "Bridge St, Victoria Bridge, Kingsway",
    hue: 142,
    slot: -1,
    path: [[3400, -420], [3400, 1780], [3400, 2320], [3400, 2680], [3400, 3150], ...KINGSWAY_DETOUR_SOUTHBOUND, K(5050)],
    stops: [
      "Northcote Terminal", "Bridge St at the Commons", "Bridge St at Central", "Bridge St Interchange",
      "Victoria Bridge North", "Southbank at Bridge St", "Kingsway at Fourth Ave", "Kingsway at Seventh Ave",
      "Fraser St at Ninth Ave (detour)", "Kingsway at 11th Ave", "Kingsway at 14th Ave", "Hilltop Terminal",
    ],
  },
  {
    id: "7",
    name: "Piers – Harbourside",
    via: "Harbour Rd, Harbour Bridge",
    hue: 292,
    slot: -1,
    path: [[-3200, 2597], [-1900, 2610], [-600, 2820], [400, 2930], [1300, 2800], [1755, 2835], [1950, 3110], [1700, 3700], [1720, 4300], [1580, 4900]],
    stops: [
      "Pier 1", "Harbour Rd at Pier 2", "Harbour Rd at Pier 3", "Harbour Rd at Pier 4", "Harbour Rd at Net Lofts",
      "Harbour Bridge North", "Harbourside Market", "Harbour Rd at Dock Gate", "Container Terminal",
      "Harbourside South",
    ],
  },
  {
    id: "9",
    name: "Old Town – Harbourside",
    via: "Victoria Bridge, Southbank",
    hue: 342,
    slot: 0,
    path: [[3400, 1480], [3400, 1780], [3400, 2320], [3400, 2680], [3400, 2800], [2400, 3000], [1950, 3110], [1700, 3700], [1720, 4300], [1580, 4900], [1360, 5600]],
    stops: [
      "Old Town Square", "Bridge St Interchange", "Victoria Bridge North", "Southbank at Bridge St",
      "Eastgate Rd at Tanner St", "Southbank Market", "Harbourside Market", "Harbour Rd at Dock Gate",
      "Container Terminal", "Harbourside South", "Harbourside Depot",
    ],
  },
  {
    id: "12",
    name: "Southbank – University",
    via: "Kingsway, Mill Bridge",
    hue: 222,
    slot: 1,
    path: [[3400, 2860], [3400, 3150], ...KINGSWAY_DETOUR_SOUTHBOUND, K(4424), [5600, 2450], [5600, 2280], [5600, 1985], [5600, 560], [6600, 180]],
    stops: [
      "Southbank at Bridge St", "Kingsway at Fourth Ave", "Kingsway at Seventh Ave", "Fraser St at Ninth Ave (detour)",
      "Kingsway at 11th Ave", "Kingsway at Mill Rd", "Mill Rd at Fourth Ave", "Mill Park", "Mill Bridge North",
      "Mill Rd at Market St", "University Ave at Mill Rd", "University Terminal",
    ],
  },
  {
    id: "15",
    name: "Northside – Mill Park",
    via: "Northside Rd, Victoria Bridge",
    hue: 108,
    slot: 1,
    path: [[-800, -500], [1200, 880], [2300, 1480], [3400, 1780], [3400, 2320], [3400, 2680], [3400, 2800], [4500, 2600], [5600, 2450], [6100, 2380]],
    stops: [
      "Northside Heights", "Northside Rd at Fern St", "Northside Rd at Rail Bridge", "Northside Rd at Central",
      "Bridge St Interchange", "Victoria Bridge North", "Southbank at Bridge St", "Eastgate Rd at Alder St",
      "Eastgate Rd at Mill Rd", "Mill Park",
    ],
  },
  {
    id: "22",
    name: "Northside – University",
    via: "North Rd",
    hue: 316,
    slot: 0,
    path: [[-800, -470], [1200, -420], [3400, -420], [5600, -380], [6600, -300], [6700, 150]],
    stops: [
      "Northside Heights", "North Rd at Reservoir", "North Rd at Pine St", "North Rd at Bridge St",
      "North Rd at the Commons", "North Rd at Mill Rd", "North Rd at Campus Dr", "University Terminal",
    ],
  },
];

export const ROUTE_BY_ID: ReadonlyMap<string, Route> = new Map(ROUTES.map((route) => [route.id, route]));

// ---------------------------------------------------------------------------------
// Vehicles

export type Severity = "critical" | "warning" | "info";

export interface VehicleSeed {
  readonly fleet: string;
  readonly route: string;
  /** Position along the round trip, 0..1 (0..0.5 outbound, 0.5..1 inbound). */
  readonly phase: number;
  /** Schedule deviation in minutes: positive is late. */
  readonly deviation: number;
  readonly operator: string;
  readonly block: string;
  readonly load: number;
  readonly capacity: number;
  /** A vehicle that is not moving at all. */
  readonly disabled?: boolean;
}

/*
 * Forty vehicles. Fleet numbers come from three series (2100s: 2017 diesels, 3300s:
 * 2019 hybrids, 4400s: 2023 battery-electric) and are not tied to routes, because a
 * bus is assigned to a block, not to a line. Deviations are what an AVL feed would
 * report on a weekend afternoon: most of the network on time, a queue on Victoria
 * Bridge, a detour on Kingsway, one bus disabled on Harbour Rd.
 */
export const VEHICLE_SEEDS: readonly VehicleSeed[] = [
  // Route 1: Market St, six buses; two bunched eastbound near Market St at Alder.
  { fleet: "4412", route: "1", phase: 0.04, deviation: 1, operator: "R. Castell", block: "1-01", load: 22, capacity: 70 },
  { fleet: "3307", route: "1", phase: 0.285, deviation: -1, operator: "A. Nwosu", block: "1-02", load: 51, capacity: 70 },
  { fleet: "3321", route: "1", phase: 0.305, deviation: 4, operator: "T. Lindqvist", block: "1-03", load: 18, capacity: 70 },
  { fleet: "2131", route: "1", phase: 0.52, deviation: 0, operator: "M. Okafor", block: "1-04", load: 30, capacity: 70 },
  { fleet: "4418", route: "1", phase: 0.7, deviation: 2, operator: "J. Pereira", block: "1-05", load: 41, capacity: 70 },
  { fleet: "2144", route: "1", phase: 0.88, deviation: 1, operator: "S. Haddad", block: "1-06", load: 26, capacity: 70 },
  // Route 3: Riverside Dr, five buses.
  { fleet: "3302", route: "3", phase: 0.06, deviation: 0, operator: "L. Marsh", block: "3-01", load: 33, capacity: 70 },
  { fleet: "4426", route: "3", phase: 0.4, deviation: 2, operator: "P. Adeyemi", block: "3-02", load: 47, capacity: 70 },
  { fleet: "2118", route: "3", phase: 0.2, deviation: -3, operator: "K. Brennan", block: "3-03", load: 12, capacity: 70 },
  { fleet: "3315", route: "3", phase: 0.62, deviation: 1, operator: "E. Varga", block: "3-04", load: 39, capacity: 70 },
  { fleet: "4403", route: "3", phase: 0.84, deviation: 0, operator: "N. Choi", block: "3-05", load: 28, capacity: 70 },
  // Route 4: Victoria Bridge and the Kingsway detour, six buses.
  { fleet: "4431", route: "4", phase: 0.16, deviation: 9, operator: "D. Mensah", block: "4-01", load: 64, capacity: 70 },
  { fleet: "2107", route: "4", phase: 0.33, deviation: 4, operator: "H. Sato", block: "4-02", load: 38, capacity: 70 },
  { fleet: "3336", route: "4", phase: 0.46, deviation: 3, operator: "F. Duarte", block: "4-03", load: 20, capacity: 70 },
  { fleet: "4409", route: "4", phase: 0.6, deviation: 2, operator: "B. Kowalski", block: "4-04", load: 35, capacity: 70 },
  { fleet: "2152", route: "4", phase: 0.76, deviation: 6, operator: "O. Reyes", block: "4-05", load: 44, capacity: 70 },
  { fleet: "3311", route: "4", phase: 0.9, deviation: 1, operator: "C. Abara", block: "4-06", load: 25, capacity: 70 },
  // Route 7: Harbour Rd, four buses; 3318 disabled at Pier 4.
  { fleet: "3318", route: "7", phase: 0.178, deviation: 14, operator: "G. Ferreira", block: "7-01", load: 31, capacity: 70, disabled: true },
  { fleet: "2125", route: "7", phase: 0.42, deviation: 2, operator: "I. Novak", block: "7-02", load: 19, capacity: 70 },
  { fleet: "4437", route: "7", phase: 0.66, deviation: 0, operator: "W. Tan", block: "7-03", load: 23, capacity: 70 },
  { fleet: "3329", route: "7", phase: 0.88, deviation: -2, operator: "Y. Idowu", block: "7-04", load: 9, capacity: 70 },
  // Route 9: Victoria Bridge and Southbank, five buses.
  { fleet: "2163", route: "9", phase: 0.1, deviation: 7, operator: "V. Leclerc", block: "9-01", load: 58, capacity: 70 },
  { fleet: "4415", route: "9", phase: 0.3, deviation: 3, operator: "A. Kaur", block: "9-02", load: 36, capacity: 70 },
  { fleet: "3304", route: "9", phase: 0.5, deviation: 1, operator: "M. Dubois", block: "9-03", load: 21, capacity: 70 },
  { fleet: "2139", route: "9", phase: 0.7, deviation: 0, operator: "R. Olsen", block: "9-04", load: 27, capacity: 70 },
  { fleet: "4442", route: "9", phase: 0.06, deviation: 11, operator: "J. Mbeki", block: "9-05", load: 61, capacity: 70 },
  // Route 12: Kingsway detour and Mill Bridge, five buses.
  { fleet: "3325", route: "12", phase: 0.11, deviation: 5, operator: "T. Greco", block: "12-01", load: 40, capacity: 70 },
  { fleet: "4421", route: "12", phase: 0.3, deviation: 2, operator: "S. Park", block: "12-02", load: 29, capacity: 70 },
  { fleet: "2148", route: "12", phase: 0.51, deviation: 0, operator: "E. Walsh", block: "12-03", load: 17, capacity: 70 },
  { fleet: "3340", route: "12", phase: 0.7, deviation: -2, operator: "L. Ferraro", block: "12-04", load: 14, capacity: 70 },
  { fleet: "4406", route: "12", phase: 0.89, deviation: 6, operator: "K. Osei", block: "12-05", load: 48, capacity: 70 },
  // Route 15: Northside Rd and Victoria Bridge, five buses.
  { fleet: "2111", route: "15", phase: 0.08, deviation: 1, operator: "P. Novak", block: "15-01", load: 24, capacity: 70 },
  { fleet: "4428", route: "15", phase: 0.26, deviation: 3, operator: "H. Ali", block: "15-02", load: 45, capacity: 70 },
  { fleet: "3332", route: "15", phase: 0.305, deviation: 8, operator: "C. Moreau", block: "15-03", load: 55, capacity: 70 },
  { fleet: "2156", route: "15", phase: 0.64, deviation: 0, operator: "D. Ruiz", block: "15-04", load: 20, capacity: 70 },
  { fleet: "4434", route: "15", phase: 0.84, deviation: 2, operator: "F. Holm", block: "15-05", load: 32, capacity: 70 },
  // Route 22: North Rd, four buses; the gap left by 22-1142's late pull-out.
  { fleet: "3309", route: "22", phase: 0.18, deviation: 2, operator: "G. Byrne", block: "22-01", load: 26, capacity: 70 },
  { fleet: "2127", route: "22", phase: 0.4, deviation: 1, operator: "M. Svensson", block: "22-02", load: 34, capacity: 70 },
  { fleet: "4401", route: "22", phase: 0.62, deviation: 0, operator: "N. Yilmaz", block: "22-04", load: 15, capacity: 70 },
  { fleet: "3314", route: "22", phase: 0.95, deviation: 3, operator: "B. Achebe", block: "22-05", load: 38, capacity: 70 },
];

// ---------------------------------------------------------------------------------
// Alerts

export interface Alert {
  readonly id: string;
  readonly severity: Severity;
  readonly title: string;
  readonly routes: readonly string[];
  readonly place: string;
  /** Minutes since the alert was raised, at page load. */
  readonly age: number;
  readonly note: string;
  /** The vehicle a dispatcher is taken to. */
  readonly vehicle: string;
  readonly camera?: string;
}

export const ALERTS: readonly Alert[] = [
  {
    id: "a1",
    severity: "critical",
    title: "Priority request to talk",
    routes: ["3"],
    place: "Bus 2118, Riverside Dr",
    age: 2,
    note: "Passenger disturbance reported by the operator. Call now.",
    vehicle: "2118",
  },
  {
    id: "a2",
    severity: "critical",
    title: "Bus 3318 disabled",
    routes: ["7"],
    place: "Harbour Rd at Pier 4",
    age: 14,
    note: "Air-brake fault. Replacement 3326 is on its way, due in 9 min.",
    vehicle: "3318",
  },
  {
    id: "a3",
    severity: "warning",
    title: "Queue on Victoria Bridge",
    routes: ["4", "9", "15"],
    place: "Southbound from Market St",
    age: 22,
    note: "Stopped back to Market St. Four buses 7 to 11 min late.",
    vehicle: "4431",
    camera: "CAM 14",
  },
  {
    id: "a4",
    severity: "warning",
    title: "Kingsway detour",
    routes: ["4", "12"],
    place: "8th to 10th Ave",
    age: 150,
    note: "Water-main works. Via Seventh Ave, Fraser St and 11th Ave.",
    vehicle: "3325",
    camera: "CAM 31",
  },
  {
    id: "a5",
    severity: "warning",
    title: "Bunching on route 1",
    routes: ["1"],
    place: "Market St at Alder, eastbound",
    age: 6,
    note: "3307 has caught 3321. Hold 3307 at Alder St for 4 min.",
    vehicle: "3307",
  },
  {
    id: "a6",
    severity: "info",
    title: "Trip not in service",
    routes: ["22"],
    place: "Trip 22-1142, Northside",
    age: 9,
    note: "No operator for the pull-out. 24 min gap behind 2127.",
    vehicle: "2127",
  },
];
