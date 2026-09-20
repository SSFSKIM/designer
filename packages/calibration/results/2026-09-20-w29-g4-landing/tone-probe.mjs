/**
 * What the macOS 27 material does on the demo's tone stage, read rather than
 * assumed (W29 G4, claims §5.155).
 *
 * Two of the site's e2e cases assert the macOS 26.5 adaptation behaviour — a
 * thin plate over a near-black backdrop converging onto the backdrop's own
 * level, and being given a different ink from its unadapted neighbour because of
 * it. W29 G3 measured Apple's macOS 27 adaptation band **inert** and moved it to
 * the bottom of its range (claims §5.153 §2 item 1), so those cases had to move.
 * Moving a test to whatever makes it pass is the failure mode this project
 * exists to avoid, so the replacement assertions are written against this
 * reading and the reading is committed beside them.
 *
 * Run against `pnpm --filter demo dev` on its usual port:
 *
 *     node packages/calibration/results/2026-09-20-w29-g4-landing/tone-probe.mjs
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

const at = async (value) => {
  await page.getByTestId("ground-level").fill(value);
  await page.waitForTimeout(500);
  return {
    ground: await ground(),
    a: await read("a"),
    b: await read("b"),
    c: await read("c"),
  };
};

const out = {};
for (const value of ["160", "100", "80", "60", "40", "20", "2"]) out[value] = await at(value);
process.stdout.write(`${JSON.stringify(out, null, 2)}\n`);

await browser.close();
