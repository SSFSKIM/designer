import { expect, type Locator, type Page } from "@playwright/test";

/**
 * Load the playground and wait for the runtime to have settled.
 *
 * "Settled" is more than "rendered": the morph measures its closed end on a
 * frame and only then pins itself out of flow, so a press dispatched at
 * coordinates read before that lands a pixel or two off the trigger. Waiting for
 * the pin is waiting for the layout to stop moving.
 */
export async function gotoPlayground(page: Page): Promise<void> {
  await page.goto("/");
  await page.waitForSelector("[data-vitrea-root]");
  await expect(page.getByRole("toolbar", { name: "Playground actions" })).toBeVisible();
  await page.waitForFunction(() => {
    const platter = document.querySelector("[data-vitrea-morph]");
    return platter !== null && getComputedStyle(platter).position === "fixed";
  });
}

/**
 * A channel value the runtime publishes on a surface.
 *
 * Read from the computed style rather than from any test-only hook: these are
 * the same custom properties an app styles against and the same numbers the
 * renderer's `SurfaceChannels` consume, so the assertion is about the product
 * rather than about a probe built for it.
 */
export async function channel(locator: Locator, property: string): Promise<number> {
  const raw = await locator.evaluate(
    (element, name) => getComputedStyle(element).getPropertyValue(name),
    property,
  );
  return Number.parseFloat(raw);
}

export interface Rect {
  readonly x: number;
  readonly y: number;
  readonly width: number;
  readonly height: number;
}

export async function rectOf(locator: Locator): Promise<Rect> {
  const box = await locator.boundingBox();
  if (box === null) throw new Error("The element has no box.");
  return box;
}

/** Sample a locator's box once per animation frame, `count` times. */
export async function sampleRects(locator: Locator, count: number): Promise<Rect[]> {
  return locator.evaluate(
    (element, frames) =>
      new Promise<Rect[]>((resolve) => {
        const samples: Rect[] = [];
        const step = (): void => {
          const box = element.getBoundingClientRect();
          samples.push({ x: box.x, y: box.y, width: box.width, height: box.height });
          if (samples.length >= frames) resolve(samples);
          else requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }),
    count,
  );
}

/**
 * Press an element with a real pointer, down then up.
 *
 * `locator.click()` is not usable on a control that opens on *press start*: the
 * element is gone by the time Playwright's own actionability retry looks for it
 * again, and the retried click toggles the menu shut. A menu trigger opening on
 * pointer-down is the platform behaviour React Aria implements, so the test
 * drives the pointer rather than asking the trigger to behave differently.
 */
export async function press(page: Page, locator: Locator): Promise<void> {
  const box = await locator.boundingBox();
  if (box === null) throw new Error("The element has no box to press.");
  await page.mouse.move(box.x + box.width / 2, box.y + box.height / 2);
  await page.mouse.down();
  // A real press is not instantaneous, and a zero-length one is a shape the
  // press library is entitled not to recognise. This is also what makes the
  // press channel observable in the frame between the two.
  await page.waitForTimeout(60);
  await page.mouse.up();
}

/** Wait until a morph's geometry has arrived, which is when its content is live. */
export async function morphSettled(page: Page): Promise<void> {
  await page.waitForSelector("[data-vitrea-morph]:not([data-vitrea-morphing])");
}

/** What is actually on top at a viewport point — the occlusion question, asked of the DOM. */
export async function topmostAt(page: Page, x: number, y: number): Promise<string> {
  return page.evaluate(
    ([px, py]) => {
      const element = document.elementFromPoint(px as number, py as number);
      if (element === null) return "none";
      const host = element.closest("[data-vitrea-node]");
      return host?.getAttribute("data-vitrea-node") ?? element.tagName.toLowerCase();
    },
    [x, y],
  );
}
