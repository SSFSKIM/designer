/**
 * The three field layers: what each one measures, how its ramp is coloured, and
 * how the field's unitless speed maps onto a physical reading.
 *
 * The ramps are data colours, not UI tokens (DESIGN.md §1): a colormap with a
 * legend. Every stop keeps OKLCH lightness at or above 0.75, which is the floor
 * that guarantees the page's ink at least 7.8:1 and its accent at least 3.2:1
 * anywhere on the field. `scripts/palette.mjs` prints the arithmetic; the hex and
 * linear values below are its output, copied rather than recomputed at runtime so
 * the shader and the legend read one set of numbers.
 */

export type LayerId = "currents" | "wind" | "temperature";

export interface RampStop {
  readonly oklch: string;
  readonly hex: string;
  /** Linear sRGB, for the shader, which mixes in linear light. */
  readonly linear: readonly [number, number, number];
}

export interface FieldLayer {
  readonly id: LayerId;
  readonly label: string;
  readonly quantity: string;
  readonly unit: string;
  /** Legend ends. */
  readonly min: number;
  readonly max: number;
  readonly decimals: number;
  readonly stops: readonly [RampStop, RampStop, RampStop, RampStop];
  /** Shader and sampler parameters. Shared verbatim by GLSL and JS. */
  readonly scale: number;
  readonly warp: number;
  readonly rate: number;
  readonly detail: number;
  /** Weight of the meandering zonal jet across the middle of the box. */
  readonly jet: number;
  /** Weight of the front on the jet's axis: warm to the south, cold to the north. */
  readonly front: number;
  /** Whether the reading carries a bearing. Temperature is a scalar. */
  readonly vector: boolean;
  /** Unitless 0..1 speed to a physical reading. */
  readonly reading: (speed: number) => number;
}

export const LAYERS: readonly FieldLayer[] = [
  {
    id: "currents",
    label: "Currents",
    quantity: "Surface current",
    unit: "m/s",
    min: 0.05,
    max: 2.4,
    decimals: 2,
    stops: [
      { oklch: "oklch(0.93 0.045 200)", hex: "#c6f2f4", linear: [0.564, 0.8846, 0.9021] },
      { oklch: "oklch(0.87 0.085 222)", hex: "#94e1fc", linear: [0.2948, 0.7561, 0.9777] },
      { oklch: "oklch(0.8 0.1 258)", hex: "#96c0fe", linear: [0.3029, 0.5254, 0.9919] },
      { oklch: "oklch(0.75 0.12 290)", hex: "#ada0f5", linear: [0.4174, 0.3534, 0.9099] },
    ],
    scale: 1.3,
    warp: 1.6,
    rate: 1.0,
    detail: 0.03,
    jet: 0.6,
    front: 0,
    vector: true,
    reading: (speed) => 0.05 + 2.35 * speed ** 1.3,
  },
  {
    id: "wind",
    label: "Wind",
    quantity: "10 m wind",
    unit: "m/s",
    min: 1.2,
    max: 27.5,
    decimals: 1,
    stops: [
      { oklch: "oklch(0.94 0.04 150)", hex: "#d9f3dd", linear: [0.6954, 0.8985, 0.7258] },
      { oklch: "oklch(0.87 0.11 168)", hex: "#86ecc6", linear: [0.2389, 0.8369, 0.5674] },
      { oklch: "oklch(0.8 0.13 205)", hex: "#2ad5e5", linear: [0.0231, 0.6669, 0.7858] },
      { oklch: "oklch(0.75 0.135 240)", hex: "#50b8fa", linear: [0.0803, 0.4804, 0.9584] },
    ],
    scale: 1.0,
    warp: 2.2,
    rate: 1.7,
    detail: 0.05,
    jet: 0.3,
    front: 0,
    vector: true,
    reading: (speed) => 1.2 + 26.3 * speed ** 1.1,
  },
  {
    id: "temperature",
    label: "Temperature",
    quantity: "Sea surface temperature",
    unit: "°C",
    min: 3.4,
    max: 28.9,
    decimals: 1,
    stops: [
      { oklch: "oklch(0.91 0.045 245)", hex: "#c9e5fe", linear: [0.5861, 0.7853, 0.9904] },
      { oklch: "oklch(0.87 0.08 305)", hex: "#e0c8ff", linear: [0.7473, 0.5745, 1.0016] },
      { oklch: "oklch(0.81 0.13 345)", hex: "#fc9ed4", linear: [0.9773, 0.3409, 0.6589] },
      { oklch: "oklch(0.76 0.13 25)", hex: "#f98f87", linear: [0.9455, 0.2727, 0.2413] },
    ],
    scale: 0.9,
    warp: 1.2,
    rate: 0.6,
    detail: 0.015,
    jet: 0,
    front: 0.38,
    vector: false,
    reading: (speed) => 3.4 + 25.5 * speed,
  },
];

export function layerById(id: LayerId): FieldLayer {
  const layer = LAYERS.find((candidate) => candidate.id === id);
  if (layer === undefined) throw new Error(`Unknown field layer: ${id}`);
  return layer;
}

/**
 * The region the viewport maps onto: the Kuroshio Extension, east of Japan, where
 * the strongest surface currents in the North Pacific are. Longitude runs across
 * the viewport, latitude up it; the box is 14° by 10°, so on a wide viewport the
 * grid is stretched, which a real instrument would also do.
 */
export const REGION = {
  name: "Kuroshio Extension",
  west: 138,
  east: 152,
  south: 30,
  north: 40,
} as const;

/** The nominal observation time the field is centred on. */
export const OBSERVATION_TIME = new Date("2026-09-04T11:20:00Z");
