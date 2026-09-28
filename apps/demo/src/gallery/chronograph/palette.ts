/**
 * The two dials, and the bench under each.
 *
 * Day is a panda dial, silver-white with black registers, on a pale cutting mat in daylight.
 * Night is its reverse, black with silver registers, on a slate mat under one desk lamp, and the
 * lume on the hands and the indices glows. The colour scheme the glass is made of follows the
 * dial: the dark material over the night bench, the light one over the day bench.
 */

export type Scheme = "light" | "dark";

export interface Palette {
  readonly scheme: Scheme;
  // The bench.
  readonly mat: string;
  readonly matDeep: string;
  readonly gridMinor: string;
  readonly gridMajor: string;
  readonly print: string;
  readonly printSoft: string;
  readonly lamp: string | null;
  // The strap.
  readonly strap: string;
  readonly strapEdge: string;
  readonly stitch: string;
  // The steel.
  readonly steelLight: string;
  readonly steelMid: string;
  readonly steelDark: string;
  // The bezel insert and its engraving.
  readonly bezel: string;
  readonly bezelPrint: string;
  // The flange and the dial.
  readonly flange: string;
  readonly flangePrint: string;
  readonly dial: string;
  readonly dialLobe: string;
  readonly dialShade: string;
  readonly dialPrint: string;
  /** The tapisserie's four faces, lit from the upper left, and the grooves between them. */
  readonly dialTop: string;
  readonly dialLeft: string;
  readonly dialRight: string;
  readonly dialBottom: string;
  readonly dialGroove: string;
  /** The band behind the railway track, so the track reads over the pattern. */
  readonly trackBand: string;
  readonly dialAccent: string;
  readonly register: string;
  readonly registerRing: string;
  readonly registerPrint: string;
  readonly registerHand: string;
  // Hands and indices.
  readonly lume: string;
  readonly lumeGlow: string | null;
  readonly chrono: string;
  readonly split: string;
  readonly shadow: string;
  readonly dateWheel: string;
  readonly datePrint: string;
}

export const DAY: Palette = {
  scheme: "light",
  mat: "#e3e8e3",
  matDeep: "#c8d1cb",
  gridMinor: "rgb(28 52 42 / 0.10)",
  gridMajor: "rgb(28 52 42 / 0.26)",
  print: "rgb(22 40 32 / 0.78)",
  printSoft: "rgb(22 40 32 / 0.5)",
  lamp: null,
  strap: "#7b4a2e",
  strapEdge: "#4c2a17",
  stitch: "rgb(246 232 206 / 0.9)",
  steelLight: "#fbfcfd",
  steelMid: "#b9c0c7",
  steelDark: "#6c747c",
  bezel: "#121417",
  bezelPrint: "#eef1f4",
  flange: "#e4e6e8",
  flangePrint: "#1a1c1f",
  dial: "#e9e7e1",
  dialLobe: "#fbfaf7",
  dialShade: "#c9c5bc",
  dialPrint: "#16181b",
  dialTop: "#f7f6f2",
  dialLeft: "#e9e7e1",
  dialRight: "#cfccc4",
  dialBottom: "#bdb9b0",
  dialGroove: "#a19d93",
  trackBand: "#eeede8",
  dialAccent: "#c8362a",
  register: "#17191d",
  registerRing: "rgb(255 255 255 / 0.07)",
  registerPrint: "#f1f2f3",
  registerHand: "#f6f6f4",
  lume: "#f2eedf",
  lumeGlow: null,
  chrono: "#d23a2c",
  split: "#2f58b8",
  shadow: "rgb(30 40 36 / 0.3)",
  dateWheel: "#f7f6f2",
  datePrint: "#15171a",
};

export const NIGHT: Palette = {
  scheme: "dark",
  mat: "#161d21",
  matDeep: "#0b1013",
  gridMinor: "rgb(200 220 230 / 0.07)",
  gridMajor: "rgb(200 220 230 / 0.16)",
  print: "rgb(214 226 232 / 0.62)",
  printSoft: "rgb(200 214 222 / 0.34)",
  lamp: "rgb(255 214 160 / 0.16)",
  strap: "#1d1c1e",
  strapEdge: "#0c0c0d",
  stitch: "rgb(170 160 150 / 0.55)",
  steelLight: "#e8ecef",
  steelMid: "#7d858d",
  steelDark: "#2e3439",
  bezel: "#0c0d0f",
  bezelPrint: "#d9dde1",
  flange: "#1c1f23",
  flangePrint: "#d6dade",
  dial: "#0e1013",
  dialLobe: "#2a2f36",
  dialShade: "#07080a",
  dialPrint: "#e8ebee",
  dialTop: "#3a5a92",
  dialLeft: "#2c4878",
  dialRight: "#1b2f55",
  dialBottom: "#132443",
  dialGroove: "#0b152b",
  trackBand: "#14223f",
  dialAccent: "#ff5a48",
  register: "#c6cacf",
  registerRing: "rgb(0 0 0 / 0.08)",
  registerPrint: "#16181b",
  registerHand: "#15171a",
  lume: "#c9ffe2",
  lumeGlow: "rgb(120 255 190 / 0.9)",
  chrono: "#ff4b3a",
  split: "#6d93ff",
  shadow: "rgb(0 0 0 / 0.55)",
  dateWheel: "#15171a",
  datePrint: "#e9ecef",
};

export const paletteFor = (scheme: Scheme): Palette => (scheme === "dark" ? NIGHT : DAY);
