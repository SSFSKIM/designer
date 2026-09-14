/**
 * The activation pose, driven from the `<GlassRoot>` prop the playground's panel
 * owns (W28 G3).
 *
 * Three engines, and no pixels: what is asserted is the runtime's own resolved
 * answer and the CSS-tier declaration that answer produces, both of which are
 * observable everywhere. The material's fidelity is the calibration bed's
 * business (claims §5.145–§5.147); this file is about the binding carrying three
 * values to the root and the root saying what it did with them.
 *
 * **Everything is polled, nothing is sampled once.** A pin reaches the root
 * through a React effect, the root applies it on its next frame, and the panel's
 * readout is repolled one frame after that. A single read taken straight after
 * the `selectOption` is a read of the frame before the change, which would fail
 * on a slow machine and pass on a fast one.
 */

import { expect, test, type Page } from "@playwright/test";

import { gotoPlayground } from "./support";

/** One row of the panel's readout, by its label. */
async function readout(page: Page, label: string): Promise<string> {
  return page.evaluate((name) => {
    const cell = [...document.querySelectorAll(".panel th")].find(
      (element) => element.textContent?.trim() === name,
    );
    return cell?.nextElementSibling?.textContent?.trim() ?? "";
  }, label);
}

/** The outer shadow the CSS tier declares on a host — the recede's most visible term. */
async function shadowOf(page: Page): Promise<string> {
  return page.getByTestId("dom-plate").evaluate((element) => getComputedStyle(element).boxShadow);
}

/**
 * Report the window as unfocused — and say plainly what kind of evidence that is.
 *
 * **Synthetic.** Nothing in this harness can take native focus away from a page:
 * opening a second page and bringing it to the front leaves the first one's
 * `document.hasFocus()` answering `true` on all three engines, headed included,
 * which W28 G3 measured before writing this. So the window's answer is replaced
 * and the event fired beside it, which is exactly the pair the runtime consumes
 * — `focus`/`blur` invalidate a reading, `document.hasFocus()` supplies it.
 *
 * What that buys and what it does not: this drives the root's state machine end
 * to end through the real binding, and it is NOT evidence that a real backgrounded
 * window recedes. The physical behaviour is the demo's to show by hand.
 */
async function reportWindowFocus(page: Page, focused: boolean): Promise<void> {
  await page.evaluate((next) => {
    Object.defineProperty(document, "hasFocus", { configurable: true, value: () => next });
    window.dispatchEvent(new Event(next ? "focus" : "blur"));
  }, focused);
}

test("under auto, the pose is the window's own focus", async ({ page }) => {
  await gotoPlayground(page);

  await expect
    .poll(async () => readout(page, "windowActivation"))
    .toBe((await page.evaluate(() => document.hasFocus())) ? "active" : "inactive");
});

test("a pin holds the recede while the window has focus, and the material follows", async ({
  page,
}) => {
  await gotoPlayground(page);
  await expect.poll(async () => readout(page, "windowActivation")).toBe("active");
  const active = await shadowOf(page);

  await page.getByLabel("windowActivation pin").selectOption("inactive");

  await expect.poll(async () => readout(page, "windowActivation")).toBe("inactive");
  // The window never lost focus; the pin is the whole reason the pose moved.
  expect(await page.evaluate(() => document.hasFocus())).toBe(true);
  // And it is a material change, not a label: the receded endpoint removes the
  // outer shadow, which is a declaration this tier writes on every host.
  await expect.poll(async () => shadowOf(page)).not.toBe(active);
});

test("returning the pin to auto hands the pose back to the window", async ({ page }) => {
  await gotoPlayground(page);
  const active = await shadowOf(page);

  await page.getByLabel("windowActivation pin").selectOption("inactive");
  await expect.poll(async () => readout(page, "windowActivation")).toBe("inactive");

  await page.getByLabel("windowActivation pin").selectOption("auto");

  await expect.poll(async () => readout(page, "windowActivation")).toBe("active");
  await expect.poll(async () => shadowOf(page)).toBe(active);
});

test("a blur event alone cannot recede a window that still has focus", async ({ page }) => {
  await gotoPlayground(page);
  await expect.poll(async () => readout(page, "windowActivation")).toBe("active");

  await page.evaluate(() => window.dispatchEvent(new Event("blur")));

  // The event says a reading is stale, not what the reading is. Page script
  // cannot hand the material a pose it did not ask the platform for, which is
  // what keeps this a window property rather than a dispatchable one.
  await expect.poll(async () => readout(page, "windowActivation")).toBe("active");
});

test("a pin holds the live material while the window reports no focus", async ({ page }) => {
  await gotoPlayground(page);
  await page.getByLabel("windowActivation pin").selectOption("active");
  await expect.poll(async () => readout(page, "windowActivation")).toBe("active");

  await reportWindowFocus(page, false);

  // The other direction of the same rule: an explicit pin wins over the window,
  // whichever way the window went.
  await expect.poll(async () => readout(page, "windowActivation")).toBe("active");

  // And with the pin released, the window it was overruling takes the pose.
  await page.getByLabel("windowActivation pin").selectOption("auto");
  await expect.poll(async () => readout(page, "windowActivation")).toBe("inactive");

  await reportWindowFocus(page, true);
  await expect.poll(async () => readout(page, "windowActivation")).toBe("active");
});
