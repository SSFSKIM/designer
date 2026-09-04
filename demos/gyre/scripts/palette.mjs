/**
 * The palette's arithmetic, kept so a later reader can re-run it rather than
 * trust it: OKLCH to sRGB, and WCAG contrast for every ink/ground pairing the
 * page relies on. `DESIGN.md` §1 cites the numbers this prints.
 *
 *   node scripts/palette.mjs
 */

function oklchToLinear(L, C, h) {
  const a = C * Math.cos((h * Math.PI) / 180);
  const b = C * Math.sin((h * Math.PI) / 180);
  const l_ = L + 0.3963377774 * a + 0.2158037573 * b;
  const m_ = L - 0.1055613458 * a - 0.0638541728 * b;
  const s_ = L - 0.0894841775 * a - 1.291485548 * b;
  const l = l_ ** 3;
  const m = m_ ** 3;
  const s = s_ ** 3;
  return [
    4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
    -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
    -0.0041960863 * l - 0.7034186147 * m + 1.707614701 * s,
  ];
}

const encode = (c) => (c <= 0.0031308 ? 12.92 * c : 1.055 * c ** (1 / 2.4) - 0.055);
const hex = (lin) =>
  "#" +
  lin
    .map((c) =>
      Math.round(Math.min(1, Math.max(0, encode(c))) * 255)
        .toString(16)
        .padStart(2, "0"),
    )
    .join("");
const luminance = (lin) => 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2];
const contrast = (a, b) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return ((hi + 0.05) / (lo + 0.05)).toFixed(2);
};
const inGamut = (lin) => lin.every((c) => c >= -0.002 && c <= 1.002);

/** The three field ramps, slow to fast, in OKLCH. Lightness never drops below 0.75. */
const ramps = {
  currents: [
    [0.93, 0.045, 200],
    [0.87, 0.085, 222],
    [0.8, 0.1, 258],
    [0.75, 0.12, 290],
  ],
  wind: [
    [0.94, 0.04, 150],
    [0.87, 0.11, 168],
    [0.8, 0.13, 205],
    [0.75, 0.135, 240],
  ],
  temperature: [
    [0.91, 0.045, 245],
    [0.87, 0.08, 305],
    [0.81, 0.13, 345],
    [0.76, 0.13, 25],
  ],
};

const ink = oklchToLinear(0.2, 0.012, 262);
const accent = oklchToLinear(0.47, 0.19, 27);
const muted = oklchToLinear(0.46, 0.02, 262);
const white = [1, 1, 1];

console.log("ink", hex(ink), " accent", hex(accent), " muted", hex(muted));
console.log(
  "on white  ink:",
  contrast(ink, white),
  " accent:",
  contrast(accent, white),
  " muted:",
  contrast(muted, white),
);
for (const [name, stops] of Object.entries(ramps)) {
  console.log("--", name);
  for (const stop of stops) {
    const lin = oklchToLinear(...stop);
    console.log(
      `  oklch(${stop.join(" ")}) ${hex(lin)} gamut=${inGamut(lin)} Y=${luminance(lin).toFixed(3)}` +
        ` ink:${contrast(ink, lin)} accent:${contrast(accent, lin)} muted:${contrast(muted, lin)}` +
        ` lin=[${lin.map((c) => c.toFixed(4)).join(", ")}]`,
    );
  }
}

// The content sheet: white at 84% over the darkest ramp stop is its worst case.
const darkest = oklchToLinear(0.75, 0.145, 290);
const sheet = darkest.map((c) => 0.84 + 0.16 * c);
console.log(
  "sheet worst composite",
  hex(sheet),
  " ink:",
  contrast(ink, sheet),
  " muted:",
  contrast(muted, sheet),
  " accent:",
  contrast(accent, sheet),
);
