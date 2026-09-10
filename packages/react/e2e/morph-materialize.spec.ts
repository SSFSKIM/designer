/**
 * `GlassMorph transition="materialize"` in a real engine (W27d).
 *
 * The matched-geometry morph's browser claims are in `morph.spec.ts`: one node,
 * a continuous trajectory, the platter occluding the toolbar. The materialize
 * transition claims the opposite structure, so it is asserted the same way and
 * point for point — two nodes, two boxes that never move toward each other, and
 * a crossfade that lives entirely in the content.
 *
 * X6 is the one that needs an engine rather than jsdom: "presence never touches
 * element opacity" is a statement about *computed* style on the host and on
 * every ancestor above it, because an `opacity < 1` anywhere in that chain forms
 * a Backdrop Root and silently kills the group's proxy sampling. Every engine is
 * asked, every frame of the transition — this is DOM and cascade, not
 * `backdrop-filter` output, so all three can answer it honestly.
 */

import { expect, test, type Page } from "@playwright/test";

import { gotoPlayground, press, rectOf, topmostAt } from "./support";

const SOURCE = '[data-vitrea-morph-end="source"]';
const DESTINATION = '[data-vitrea-morph-end="destination"]';

/** Switch the playground's Actions menu onto the materialize transition. */
async function useMaterialize(page: Page): Promise<void> {
  await page.getByLabel("Materialize the Actions menu").check();
  // The switch is a remount — the two transitions are two components — so the
  // closed end measures and places itself again before anything can be pressed.
  await page.waitForFunction((selector) => {
    const platter = document.querySelector(selector);
    const spacer = document.querySelector("[data-vitrea-morph-anchor]");
    if (platter === null || spacer === null) return false;
    const box = platter.getBoundingClientRect();
    const footprint = spacer.getBoundingClientRect();
    if (footprint.width === 0) return false;
    return Math.abs(box.x - footprint.x) < 2 && Math.abs(box.y - footprint.y) < 2;
  }, SOURCE);
}

const settled = (page: Page, selector: string): Promise<unknown> =>
  page.waitForSelector(`${selector}:not([data-vitrea-morphing])`);

interface Sample {
  readonly sourceContent: number;
  readonly destinationContent: number;
  /** The largest `1 − opacity` found on either host or any ancestor above it. */
  readonly opacityDeficit: number;
  readonly ends: number;
}

/**
 * Record the transition frame by frame, in the page.
 *
 * Started before the press and read back after it, for the reason
 * `recordRectsUntilSettled` gives: a Node round trip is frames wide, and this
 * measures what happened *during* a 220 ms transition.
 */
function recordCrossfade(page: Page): Promise<Sample[]> {
  return page.evaluate(
    (budget) =>
      new Promise<Sample[]>((resolve) => {
        const samples: Sample[] = [];
        let sawMorphing = false;
        const started = performance.now();

        const contentAlpha = (end: string): number => {
          const content = document.querySelector(`[data-vitrea-morph-end="${end}"] ` +
            "[data-vitrea-morph-content]");
          if (content === null) return end === "source" ? 1 : 0;
          return Number.parseFloat(getComputedStyle(content).opacity);
        };

        const step = (): void => {
          const platters = [...document.querySelectorAll("[data-vitrea-morph]")];
          let deficit = 0;
          for (const platter of platters) {
            for (let node = platter; node !== null; node = node.parentElement as Element) {
              const opacity = Number.parseFloat(getComputedStyle(node).opacity);
              deficit = Math.max(deficit, 1 - opacity);
              if (node.parentElement === null) break;
            }
          }
          samples.push({
            sourceContent: contentAlpha("source"),
            destinationContent: contentAlpha("destination"),
            opacityDeficit: deficit,
            ends: platters.length,
          });

          const morphing = platters.some((p) => p.hasAttribute("data-vitrea-morphing"));
          sawMorphing ||= morphing;
          if ((sawMorphing && !morphing) || performance.now() - started > budget) {
            resolve(samples);
            return;
          }
          requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }),
    4000,
  );
}

test.beforeEach(async ({ page }, testInfo) => {
  // Emulated per page rather than through `test.use`: the runtime reads the
  // query with `matchMedia` at construction, and only a page-level emulation is
  // in force before the root is built.
  if (testInfo.titlePath.join(" ").includes("Reduced Motion")) {
    await page.emulateMedia({ reducedMotion: "reduce" });
  }
  await gotoPlayground(page);
  await useMaterialize(page);
});

test("the two ends are two surfaces, and neither travels toward the other", async ({ page }) => {
  const source = page.locator(SOURCE);
  const before = await rectOf(source);

  await press(page, page.getByRole("button", { name: "Actions" }));
  await settled(page, DESTINATION);

  const destination = page.locator(DESTINATION);
  await expect(destination).toHaveCount(1);

  const ids = await page.evaluate(() =>
    [...document.querySelectorAll("[data-vitrea-morph]")].map((element) =>
      element.getAttribute("data-vitrea-node"),
    ),
  );
  expect(ids).toHaveLength(2);
  expect(new Set(ids).size, "the two ends share a node id").toBe(2);

  // The closed end stayed exactly where it was: nothing here matches geometry,
  // so the source's box is the same box it had before the transition began.
  const after = await rectOf(source);
  expect(Math.abs(after.x - before.x)).toBeLessThan(1);
  expect(Math.abs(after.y - before.y)).toBeLessThan(1);
  expect(Math.abs(after.width - before.width)).toBeLessThan(1);
  expect(Math.abs(after.height - before.height)).toBeLessThan(1);

  const platter = await rectOf(destination);
  expect(platter.height).toBeGreaterThan(after.height);
});

test("the crossfade is the content's, and no host or ancestor leaves opacity 1", async ({
  page,
}) => {
  const recording = recordCrossfade(page);
  await press(page, page.getByRole("button", { name: "Actions" }));
  const samples = await recording;

  expect(samples.length).toBeGreaterThan(2);

  // X6, machine-checked on every frame of the transition: the material's
  // presence is what arrives, so element opacity never moves at all.
  for (const sample of samples) {
    expect(sample.opacityDeficit, "presence must never be element opacity").toBeCloseTo(0, 5);
  }

  const destination = samples.map((sample) => sample.destinationContent);
  const source = samples.map((sample) => sample.sourceContent);
  expect(destination.at(-1)).toBeCloseTo(1, 2);
  expect(source.at(-1)).toBeCloseTo(0, 2);
  expect(
    destination.some((alpha) => alpha > 0.02 && alpha < 0.98),
    "the content never crossfaded — it switched",
  ).toBe(true);

  for (const [index, alpha] of destination.entries()) {
    if (index === 0) continue;
    expect(alpha, "the crossfade went backwards").toBeGreaterThanOrEqual(
      (destination[index - 1] ?? 0) - 1e-3,
    );
  }
});

test("the end that is absent is inert, and is released when it has gone", async ({ page }) => {
  const trigger = page.getByRole("button", { name: "Actions" });
  const footprint = await rectOf(trigger);
  const sourceId = await page.locator(SOURCE).getAttribute("data-vitrea-node");

  await press(page, trigger);
  await settled(page, DESTINATION);

  // The open end is on top of its own box, and the closed end — still registered,
  // still on its footprint, and with no presence — is not a target at all.
  const platter = await rectOf(page.locator(DESTINATION));
  const overPlatter = await topmostAt(page, platter.x + platter.width / 2, platter.y + 20);
  expect(overPlatter).toBe(await page.locator(DESTINATION).getAttribute("data-vitrea-node"));

  const overFootprint = await topmostAt(
    page,
    footprint.x + footprint.width / 2,
    footprint.y + footprint.height / 2,
  );
  expect(overFootprint).not.toBe(sourceId);

  const hidden = await page.locator(`${SOURCE} [data-vitrea-morph-content]`).evaluate(
    (element) => getComputedStyle(element).visibility,
  );
  expect(hidden, "the absent end is still in the tab order").toBe("hidden");

  await page.keyboard.press("Escape");
  await expect(page.locator(DESTINATION)).toHaveCount(0);
  await expect(page.locator(SOURCE)).toHaveCount(1);
});

test.describe("under Reduced Motion", () => {
  test("presence and content both land without travelling", async ({ page }) => {
    const recording = recordCrossfade(page);
    await press(page, page.getByRole("button", { name: "Actions" }));
    const samples = await recording;

    for (const sample of samples) {
      expect(sample.opacityDeficit).toBeCloseTo(0, 5);
      // Every recorded frame is at one end or the other. The reduced rule is
      // that presence steps, and the content steps with it.
      if (sample.ends < 2) continue;
      expect(
        sample.destinationContent === 0 || sample.destinationContent === 1,
        "the crossfade animated under Reduced Motion",
      ).toBe(true);
    }
    expect(samples.at(-1)?.destinationContent).toBe(1);
  });
});
