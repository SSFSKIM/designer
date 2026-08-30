import { expect, type Locator, type Page } from "@playwright/test";

/**
 * Load the playground and wait for the runtime to have settled.
 *
 * "Settled" is more than "rendered": the morph measures its closed end on a
 * frame and only then pins itself out of flow, so a press dispatched at
 * coordinates read before that lands a pixel or two off the trigger. Waiting for
 * the pin is waiting for the layout to stop moving.
 *
 * **The tier is pinned to CSS**, and that is a statement about what this suite
 * is for rather than a convenience. These are tests of the *bindings* — that a
 * channel is published, that a morph interpolates, that a preference reaches the
 * material — and several of them read the answer off the host's own computed
 * style, which only the CSS tier writes. The playground now asks for the GPU
 * tier by default, and whether it gets one is a property of the machine: C5
 * measured Playwright's WebKit returning a device on localhost where Chromium
 * returns none. Left unpinned, the same assertion would read a real value on one
 * engine and `none` on another, for a reason that has nothing to do with the
 * binding under test. The GPU tier's own drawing is asserted where it can be
 * asserted honestly: `@vitreajs/vitrea-web`'s `e2e/gpu` suite, against a real
 * adapter.
 */
export async function gotoPlayground(page: Page): Promise<void> {
  // `/` is now vitrea's public demo site (C9b); the acceptance playground this
  // suite drives moved to its own route. Same page, same structure, same control
  // names: the only change is where it is served from.
  await page.goto("/playground/?renderer=css");
  await page.waitForSelector("[data-vitrea-root]");
  await expect(page.getByRole("toolbar", { name: "Playground actions" })).toBeVisible();
  // The pin asked for as "is the platter standing on its footprint yet", which
  // is the property every caller below actually depends on — they read
  // coordinates off the trigger, and a platter that has not pinned is still
  // collapsed at wherever it was last placed.
  //
  // Since Decision Log #28(d) the platter is `position: fixed` from its first
  // commit, so the older "is it fixed yet" question is answered yes before the
  // answer means anything. "Does it have a box" is not the replacement either: a
  // collapsed platter still reports the 1px border it paints on each side, so it
  // measures 2×2 rather than 0×0, and a caller that waited on `width > 0` read
  // its coordinates one frame early — measured at 21px of vertical drift, which
  // is half a control and lands a press off the trigger.
  await page.waitForFunction(() => {
    const platter = document.querySelector("[data-vitrea-morph]");
    const spacer = document.querySelector("[data-vitrea-morph-anchor]");
    if (platter === null || spacer === null) return false;
    const box = platter.getBoundingClientRect();
    const footprint = spacer.getBoundingClientRect();
    if (footprint.width === 0 || footprint.height === 0) return false;
    return (
      Math.abs(box.x - footprint.x) < 2 &&
      Math.abs(box.y - footprint.y) < 2 &&
      Math.abs(box.width - footprint.width) < 2 &&
      Math.abs(box.height - footprint.height) < 2
    );
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
 * Record a locator's box every frame until the morph settles, and hand back the
 * whole trajectory.
 *
 * **Why this exists rather than another `sampleRects`.** A reversal test has to
 * compare where the geometry *was* when the reversal was triggered against where it
 * went next. Reading the "was" from Node costs a round trip, and a spring keeps
 * moving during it — so under load the two readings are frames apart and the test
 * fails on the harness rather than on the product. Measured: this suite's reversal
 * assertion passed thirty out of thirty runs with Firefox alone and failed with
 * three engines contending, which is a statement about round-trip latency and not
 * about motion.
 *
 * Recording in the page removes the round trip from the measurement entirely: every
 * sample is a frame, adjacent samples are adjacent frames, and the trigger lands
 * somewhere inside the recording rather than between two of them. The caller starts
 * the recording, does whatever it likes from Node, and reads the trajectory back.
 *
 * Settling is the runtime's own answer (`data-vitrea-morphing`), not a duration, so
 * the recording ends when the springs do.
 */
export function recordRectsUntilSettled(page: Page, selector: string): Promise<Rect[]> {
  return page.evaluate(
    ([target, budget]) =>
      new Promise<Rect[]>((resolve) => {
        const samples: Rect[] = [];
        const started = performance.now();
        const step = (): void => {
          const element = document.querySelector(target as string);
          if (element === null) {
            resolve(samples);
            return;
          }
          const box = element.getBoundingClientRect();
          samples.push({ x: box.x, y: box.y, width: box.width, height: box.height });
          // Two conditions, and both are needed. The morph has to have started
          // before "not morphing" can mean "arrived", and the budget is a bound on
          // a hang rather than a wait for anything.
          const morphing = element.hasAttribute("data-vitrea-morphing");
          if (morphing) element.setAttribute("data-recorded-morphing", "");
          const sawMorphing = element.hasAttribute("data-recorded-morphing");
          if ((sawMorphing && !morphing) || performance.now() - started > (budget as number)) {
            element.removeAttribute("data-recorded-morphing");
            resolve(samples);
            return;
          }
          requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }),
    [selector, 4000] as const,
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
