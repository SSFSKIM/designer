/**
 * Parent acceptance #4 — "The morph."
 *
 * Three claims, and each one is asserted structurally rather than visually:
 *
 * 1. **One surface, not two.** There is exactly one registered glass node for the
 *    pair through the whole transition, and its node id never changes. A crossfade
 *    of two surfaces would be two nodes.
 * 2. **Continuous geometry.** The box travels frame by frame with no jump, and the
 *    corner radius travels with it — those are X8 channels on springs, so the
 *    sampled trajectory is the evidence.
 * 3. **The platter occludes the toolbar beneath it.** Asked of the DOM through
 *    `elementFromPoint`, which is the same question the compositor answers and one
 *    every engine can be asked.
 */

import { expect, test } from "@playwright/test";

import {
  gotoPlayground,
  morphSettled,
  press,
  recordRectsUntilSettled,
  rectOf,
  sampleRects,
  topmostAt,
} from "./support";

const PLATTER = "[data-vitrea-morph]";

test.beforeEach(async ({ page }) => {
  await gotoPlayground(page);
});

test("one surface carries the pair — the node id never changes", async ({ page }) => {
  const platter = page.locator(PLATTER);
  const before = await platter.getAttribute("data-vitrea-node");
  expect(before).not.toBeNull();

  await press(page, page.getByRole("button", { name: "Actions" }));
  await expect(page.getByRole("menu")).toBeVisible();

  await expect(platter).toHaveAttribute("data-vitrea-node", before ?? "");
  // Exactly one glass node for the morph, in either state: a crossfade would
  // need two, and X1 would refuse them in one plane anyway.
  expect(await page.locator(`${PLATTER}[data-vitrea-node]`).count()).toBe(1);
});

test("opening promotes the surface to the overlay plane as a unit", async ({ page }) => {
  const platter = page.locator(PLATTER);
  await expect(platter).toHaveAttribute("data-vitrea-host-plane", "base");

  await press(page, page.getByRole("button", { name: "Actions" }));
  await expect(platter).toHaveAttribute("data-vitrea-host-plane", "overlay");

  // The whole unit moved: the element now lives in the overlay plane's own host
  // layer, which is what puts the body and highlight on that plane's canvases.
  const layerPlane = await platter.evaluate(
    (element) =>
      element.closest('[data-vitrea-layer="semantic-host"]')?.getAttribute("data-vitrea-plane") ??
      null,
  );
  expect(layerPlane).toBe("overlay");
});

test("the geometry travels continuously, with no jump between frames", async ({ page }) => {
  const platter = page.locator(PLATTER);
  const closed = await rectOf(platter);

  const trajectory = sampleRects(platter, 14);
  await press(page, page.getByRole("button", { name: "Actions" }));
  const samples = await trajectory;

  const open = samples[samples.length - 1];
  if (open === undefined) throw new Error("no samples");

  // It actually grew into a platter.
  expect(open.height).toBeGreaterThan(closed.height * 1.5);
  expect(open.width).toBeGreaterThan(closed.width);

  // And every step of the way was a step, not a cut. A crossfade or a re-layout
  // shows up here as one frame moving most of the distance.
  const travel = Math.abs(open.y - closed.y) + Math.abs(open.height - closed.height);
  for (let i = 1; i < samples.length; i += 1) {
    const previous = samples[i - 1];
    const current = samples[i];
    if (previous === undefined || current === undefined) continue;
    const step =
      Math.abs(current.y - previous.y) +
      Math.abs(current.height - previous.height) +
      Math.abs(current.x - previous.x) +
      Math.abs(current.width - previous.width);
    expect(step).toBeLessThan(travel * 0.6);
  }
});

test("the corner radius interpolates with the box", async ({ page }) => {
  const platter = page.locator(PLATTER);
  const radiusOf = () =>
    platter.evaluate((element) =>
      Number.parseFloat(getComputedStyle(element).borderTopLeftRadius),
    );

  const closed = await radiusOf();
  await press(page, page.getByRole("button", { name: "Actions" }));
  await expect(page.getByRole("menu")).toBeVisible();
  // The runtime's own settle signal rather than a duration: the radius is on a
  // spring, so "arrived" is a state it reports and not a time it takes.
  await morphSettled(page);
  const open = await radiusOf();

  // 16 → 22 in the playground: a channel that interpolates, not a class swap.
  expect(open).toBeGreaterThan(closed + 2);
});

test("the platter's glass occludes the toolbar's DOM beneath it", async ({ page }) => {
  const toolbar = page.getByRole("toolbar", { name: "Playground actions" });
  const share = page.getByRole("button", { name: "Share" });
  const shareBox = await rectOf(share);
  const centre = { x: shareBox.x + shareBox.width / 2, y: shareBox.y + shareBox.height / 2 };

  // Before: the toolbar button is what is on top at its own centre.
  expect(await topmostAt(page, centre.x, centre.y)).toBe(
    await share.getAttribute("data-vitrea-node"),
  );

  await press(page, page.getByRole("button", { name: "Actions" }));
  await expect(page.getByRole("menu")).toBeVisible();
  await morphSettled(page);

  const platterBox = await rectOf(page.locator(PLATTER));
  // The platter opens above the toolbar and is wide enough to cover it; check a
  // point that is inside both.
  const overlapX = Math.max(platterBox.x, shareBox.x) + 4;
  const overlapY = platterBox.y + platterBox.height / 2;
  expect(overlapY).toBeLessThan(shareBox.y);

  // The point is over the platter, and the toolbar beneath is not the hit target
  // there — the overlay plane paints and hit-tests above the base plane's DOM.
  const platterNode = await page.locator(PLATTER).getAttribute("data-vitrea-node");
  expect(await topmostAt(page, overlapX, overlapY)).toBe(platterNode);
  await expect(toolbar).toBeVisible();
});

/*
 * The property is redirection: reversed mid-flight, the geometry continues from
 * where it was, at the velocity it had, rather than restarting from an endpoint.
 *
 * The whole trajectory is recorded **in the page**, one sample per frame, and the
 * reversal is triggered from Node while that recording runs. The previous shape
 * read the mid-flight box over a round trip and compared it with the first sample
 * after the reversal, which meant the two readings were separated by however long
 * the bridge took — fine with Firefox alone (thirty runs, thirty passes) and not
 * fine with three engines contending, where it failed on latency rather than on
 * motion. Adjacent frames cannot drift apart that way, and the assertion below is
 * stricter than the one it replaces: it holds at every frame of the reversal
 * instead of at one.
 */
test("a reversal mid-flight redirects instead of restarting", async ({ page }) => {
  const platter = page.locator(PLATTER);
  const closed = await rectOf(platter);

  const trajectory = recordRectsUntilSettled(page, PLATTER);
  await press(page, page.getByRole("button", { name: "Actions" }));
  // Mid-flight is a state, not a moment: wait for the geometry to be past the
  // closed end and still travelling, which is true for as long as it takes the
  // reversal to be dispatched.
  await page.waitForFunction(
    ([selector, from]) => {
      const element = document.querySelector(selector as string);
      return (
        element !== null &&
        element.hasAttribute("data-vitrea-morphing") &&
        element.getBoundingClientRect().height > (from as number) + 4
      );
    },
    [PLATTER, closed.height] as const,
  );
  await page.keyboard.press("Escape");
  const samples = await trajectory;

  expect(samples.length, "the recording caught no frames").toBeGreaterThan(4);

  // It grew before it shrank, so a reversal really happened inside the recording.
  const peak = Math.max(...samples.map((sample) => sample.height));
  expect(peak).toBeGreaterThan(closed.height + 4);
  expect(samples[samples.length - 1]?.height ?? 0).toBeLessThan(peak);

  // And no frame of it is a cut. A restart from either endpoint would put most of
  // the travel into one step; a redirect puts none of it there.
  const travel = peak - closed.height;
  for (let i = 1; i < samples.length; i += 1) {
    const previous = samples[i - 1];
    const current = samples[i];
    if (previous === undefined || current === undefined) continue;
    expect(
      Math.abs(current.height - previous.height),
      `frame ${String(i)} of ${String(samples.length)} jumped`,
    ).toBeLessThan(travel * 0.5);
  }

  await morphSettled(page);
  const settled = await rectOf(platter);
  expect(Math.abs(settled.height - closed.height)).toBeLessThan(2);
  expect(Math.abs(settled.y - closed.y)).toBeLessThan(2);
  await expect(platter).toHaveAttribute("data-vitrea-host-plane", "base");
});

test("the menu inside the platter is a real menu", async ({ page }) => {
  await press(page, page.getByRole("button", { name: "Actions" }));

  const menu = page.getByRole("menu", { name: "Playground actions" });
  await expect(menu).toBeVisible();
  await expect(page.getByRole("menuitem")).toHaveCount(4);

  // Selecting an item runs the app's action and closes the menu. What is being
  // asserted is the *composition* — vitrea's platter, the app's menu, wired
  // together — not the external primitive's own keyboard model, which belongs to
  // React Aria and is tested there. Content in flight is deliberately not an
  // activation target, so the click waits for the geometry to arrive.
  await morphSettled(page);
  await page.getByRole("menuitem", { name: "Duplicate" }).click();

  await expect(menu).toBeHidden();
  await expect(page.getByRole("status")).toHaveText("Last action: duplicate");
  await expect(page.getByRole("button", { name: "Actions" })).toBeFocused();
});

test("the keyboard opens the menu, moves inside it, and Escape returns focus", async ({ page }) => {
  const trigger = page.getByRole("button", { name: "Actions" });
  await trigger.focus();
  await page.keyboard.press("Enter");

  const menu = page.getByRole("menu", { name: "Playground actions" });
  await expect(menu).toBeVisible();
  // React Aria focuses an item outright on a keyboard open.
  await expect(page.getByRole("menuitem", { name: "Duplicate" })).toBeFocused();

  await page.keyboard.press("Escape");
  await expect(menu).toBeHidden();
  await expect(page.getByRole("button", { name: "Actions" })).toBeFocused();
});
