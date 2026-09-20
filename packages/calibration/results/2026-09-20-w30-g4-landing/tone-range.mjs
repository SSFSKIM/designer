/**
 * Where the tone stage's three plates actually separate, on the material 0.20.0
 * ships (W30 G4, claims §5.160; charter Decision Log 1 (e)).
 *
 * W29 G4 read this stage at seven stops and made the prose and the two e2e cases
 * honest (`results/2026-09-20-w29-g4-landing/tone-probe.json`), and left the
 * geometry alone because re-ranging a control is a design decision and the wave
 * that would carry it had not opened. Decision Log 1 (e) ruled it: the slider's
 * resolution moves to where the plates separate, with the near-black stop kept
 * as the last position so what macOS 27 does there stays one drag away.
 *
 * "Where they separate" has to be a reading before it can be a range, and the
 * two candidate statistics disagree about what separation is, so both are taken
 * here at every stop of the CURRENT control:
 *
 *   * the SPREAD — max minus min of the three composited bodies, in linear
 *     luminance. This is what the eye sees as "the plates are different".
 *   * the ORDER — whether the three are ordered by span (40 < 68 < 112), which
 *     is what the stage CLAIMS. The tracker's second entry records that the
 *     order fails at the darkest stop, so a spread that is large there is a
 *     spread in the wrong shape.
 *
 * The composite is the same arithmetic the e2e's `bodyOf` performs — the CSS
 * tier's published `--vitrea-tint` over the ground the page paints — so the
 * range this file chooses and the assertions that pin it read one quantity.
 *
 * Run against `pnpm --filter demo dev` on its usual port:
 *
 *     node packages/calibration/results/2026-09-20-w30-g4-landing/tone-range.mjs \
 *       > packages/calibration/results/2026-09-20-w30-g4-landing/tone-range.json
 */

import { chromium } from "@playwright/test";

const BASE = process.env.VITREA_DEMO_URL ?? "http://localhost:5173";

const browser = await chromium.launch({ channel: "chromium" });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
await page.goto(`${BASE}/?renderer=css`);
await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
await page.evaluate(() => {
  document.getElementById("tone")?.scrollIntoView({ block: "center", behavior: "instant" });
});
await page.locator("#tone").waitFor();

const read = async (step) =>
  page.getByTestId(`tone-plate-${step}`).evaluate((element) => ({
    tint: element.style.getPropertyValue("--vitrea-tint"),
    ink: element.style.getPropertyValue("--vitrea-foreground"),
    occlusion: element.style.getPropertyValue("--vitrea-occlusion"),
  }));

/** The backdrop, from the backdrop: one texel of the canvas the group samples. */
const ground = async () =>
  page.evaluate(() => {
    const canvas = document.querySelector(".stage__canvas");
    const context = canvas === null ? null : canvas.getContext("2d");
    if (context === null) throw new Error("the stage has no canvas");
    const dpr = window.devicePixelRatio;
    const data = context.getImageData(Math.round(16 * dpr), Math.round(16 * dpr), 1, 1).data;
    return [data[0], data[1], data[2]];
  });

const channel = (value) => {
  const v = value / 255;
  return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
};
const levelOf = (rgb) => 0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2]);

/** The e2e's `bodyOf`: the published tint composited over the ground it is over. */
const bodyOf = (tint, rgb) => {
  const parts = (tint.match(/[\d.]+/g) ?? []).map(Number);
  const [r = 0, g = 0, b = 0, alpha = 1] = parts;
  const over = (index, colour) => alpha * colour + (1 - alpha) * (rgb[index] ?? 0);
  return levelOf([over(0, r), over(1, g), over(2, b)]);
};

const at = async (value) => {
  await page.getByTestId("ground-level").fill(String(value));
  await page.waitForTimeout(350);
  const rgb = await ground();
  const plates = { a: await read("a"), b: await read("b"), c: await read("c") };
  const bodies = {
    a: bodyOf(plates.a.tint, rgb),
    b: bodyOf(plates.b.tint, rgb),
    c: bodyOf(plates.c.tint, rgb),
  };
  const values = [bodies.a, bodies.b, bodies.c];
  return {
    [LADDER ? "position" : "thousandths"]: value,
    ground: rgb,
    groundLevel: levelOf(rgb),
    plates,
    bodies,
    spread: Math.max(...values) - Math.min(...values),
    orderedBySpan: bodies.a < bodies.b && bodies.b < bodies.c,
    alphaSpread:
      Number(plates.c.occlusion) - Number(plates.a.occlusion),
    alphaOrderedBySpan:
      Number(plates.a.occlusion) <= Number(plates.b.occlusion) &&
      Number(plates.b.occlusion) <= Number(plates.c.occlusion),
  };
};

/**
 * Every stop of the control.
 *
 * `VITREA_TONE_STOPS=ladder` reads the re-ranged control this gate lands — 81
 * positions, 0…80 — and anything else reads the control as it stood, 2…160 by
 * twos. Both are committed: the first reading is what chose the range and the
 * second is what the assertions are written against, and they are the same
 * instrument over the same page so the two are comparable stop for stop.
 */
const LADDER = process.env.VITREA_TONE_STOPS === "ladder";
const stops = [];
if (LADDER) for (let value = 0; value <= 80; value += 1) stops.push(value);
else for (let value = 2; value <= 160; value += 2) stops.push(value);

const readings = [];
for (const value of stops) readings.push(await at(value));

const separating = readings.filter((row) => row.orderedBySpan);
const summary = {
  what: LADDER
    ? "the demo tone stage's three plates, every stop of the re-ranged 0…80 ladder, on the material 0.20.0 ships"
    : "the demo tone stage's three plates, every stop of the 2…160 control it had, on the material 0.20.0 ships",
  read: new Date().toISOString(),
  url: `${BASE}/?renderer=css`,
  tier: "css",
  statistic:
    "spread = max-min of the three composited bodies in linear luminance; orderedBySpan = 40px < 68px < 112px",
  stopsRead: readings.length,
  orderedStops: separating.map((row) => row.position ?? row.thousandths),
  firstOrderedStop: separating[0]?.position ?? separating[0]?.thousandths ?? null,
  bestSpread: readings.reduce((best, row) => (row.spread > best.spread ? row : best), readings[0]),
  bestOrderedSpread: separating.reduce(
    (best, row) => (best === undefined || row.spread > best.spread ? row : best),
    undefined,
  ),
  readings,
};

process.stdout.write(`${JSON.stringify(summary, null, 2)}\n`);

await browser.close();
