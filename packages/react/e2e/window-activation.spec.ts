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

/** The declarations the CSS tier writes for a surface; empty ones belong to whoever writes them. */
const MATERIAL_PROPERTIES = [
  "backdrop-filter",
  "-webkit-backdrop-filter",
  "background-color",
  "background-image",
  "box-shadow",
  "border-width",
  "border-color",
  "--vitrea-tint",
  "--vitrea-occlusion",
  "--vitrea-border-color",
  "--vitrea-blur",
] as const;

/**
 * Everything this tier *wrote* for one surface, host and layers together.
 *
 * Two corrections are folded into this one read, and both were assumptions about
 * where a material lives rather than about what it is.
 *
 * **Not the host's `box-shadow` alone.** Since W18 G1 the outer shadow is written
 * by whichever carrier took it out of the body's own backdrop — L3, or the
 * group's shadow container — and the host writes `none` on every carrier but the
 * clipping-ancestor fallback. An assertion on that one property could not fail
 * for the reason it was written, and could not pass for one either. So the read
 * is the tier's whole output across the host and its three layers (`sharp`,
 * `heavy`, `overlay`), because which declaration a material change lands in is
 * the profile document's business and moves between waves.
 *
 * **And `element.style`, never `getComputedStyle`.** The tier writes its
 * declarations inline — `css-tier-layers.ts` for the layers, the host's own write
 * in `root.ts` — so the inline value is the endpoint it decided on, while a
 * computed value during an armed transition is a frame of the transit toward it.
 * WebKit caught the difference: the tier writes `backdrop-filter` and
 * `-webkit-backdrop-filter` from one string, the engine interpolates them as two
 * transitions, and a computed baseline disagreed with *itself* by a thousandth of
 * a pixel across the pair. What this file claims is that a prop reaches this
 * tier's declarations; the transit between two frozen endpoints is the tier's own
 * and is asserted where transitions are the subject.
 */
async function materialOf(page: Page): Promise<string> {
  return page.getByTestId("dom-plate").evaluate(
    (host, properties) =>
      [host, ...host.querySelectorAll<HTMLElement>("[data-vitrea-css-layer]")]
        .map((element) =>
          properties
            .map((property) => [property, element.style.getPropertyValue(property)] as const)
            .filter(([, value]) => value !== "")
            .map(([property, value]) => `${property}: ${value}`)
            .join("; "),
        )
        .join("\n"),
    MATERIAL_PROPERTIES,
  );
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
  const active = await materialOf(page);

  await page.getByLabel("windowActivation pin").selectOption("inactive");

  await expect.poll(async () => readout(page, "windowActivation")).toBe("inactive");
  // The window never lost focus; the pin is the whole reason the pose moved.
  expect(await page.evaluate(() => document.hasFocus())).toBe(true);
  // And it is a material change rather than a label: the receded endpoint is a
  // different set of declarations on this tier, not the same ones renamed.
  await expect.poll(async () => materialOf(page)).not.toBe(active);
});

test("returning the pin to auto hands the pose back to the window", async ({ page }) => {
  await gotoPlayground(page);
  // The pose is settled before the baseline is taken, so what is captured is the
  // active endpoint rather than whatever a still-materializing surface had.
  await expect.poll(async () => readout(page, "windowActivation")).toBe("active");
  const active = await materialOf(page);

  await page.getByLabel("windowActivation pin").selectOption("inactive");
  await expect.poll(async () => readout(page, "windowActivation")).toBe("inactive");
  await expect.poll(async () => materialOf(page)).not.toBe(active);

  await page.getByLabel("windowActivation pin").selectOption("auto");

  await expect.poll(async () => readout(page, "windowActivation")).toBe("active");
  // Polled, not read once: both poses are frozen endpoints and the transit
  // between them is the tier's armed transitions, so the settled value is the
  // only one worth comparing.
  await expect.poll(async () => materialOf(page)).toBe(active);
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
