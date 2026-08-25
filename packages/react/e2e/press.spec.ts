/**
 * Parent acceptance #3 — "Interruptible press."
 *
 * Asserted on the published channel values, never on pixels. The claim is about
 * *continuity*: releasing mid-press must redirect the animation from its current
 * position and velocity with no snap or restart. A screenshot cannot tell a
 * redirect from a restart; a sequence of channel values can, and it is engine-
 * independent.
 */

import { expect, test, type Page } from "@playwright/test";

import { channel, gotoPlayground } from "./support";

const PRESS = "--vitrea-press";
const GLOW = "--vitrea-glow";

/** Read one channel once per animation frame, `count` times. */
async function trace(page: Page, count: number, property: string) {
  return page.evaluate(
    ([frames, name]) =>
      new Promise<number[]>((resolve) => {
        const button = [...document.querySelectorAll("button")].find(
          (element) => element.textContent?.trim() === "Share",
        );
        const samples: number[] = [];
        const step = (): void => {
          samples.push(
            Number.parseFloat(getComputedStyle(button as Element).getPropertyValue(name as string)),
          );
          if (samples.length >= (frames as number)) resolve(samples);
          else requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }),
    [count, property] as const,
  );
}

/**
 * Wait until a channel has **crossed** a threshold, and report where it was when
 * that was first observed.
 *
 * Both continuity tests need to act on a surface that is *mid-flight*, and a fixed
 * sleep cannot promise that: the drivers are frame-rate invariant, so a browser
 * running long frames arrives sooner in wall-clock terms than one running short
 * ones. Waiting for the value itself is what makes the setup say what it means.
 *
 * **A crossing rather than a window, and that is the whole fix.** This used to wait
 * for the channel to be *inside* a range, polled per frame — and a window can be
 * stepped straight over. A spring is closed-form in time, so one long frame moves
 * it as far as the frame was long, and under three-engine contention a Firefox
 * frame is long enough to take the release from above the window to below it
 * between two polls. The wait then never resolved and the test died on its
 * thirty-second timeout, having measured nothing. A crossing predicate cannot be
 * stepped over: once true it stays true, so the only thing a long frame costs is
 * precision about *where* the crossing was caught — which is why the value is
 * returned rather than re-read over a second round trip.
 */
async function waitForChannelPast(
  page: Page,
  property: string,
  threshold: number,
  direction: "above" | "below",
): Promise<number> {
  const handle = await page.waitForFunction(
    ([name, limit, side]) => {
      const button = [...document.querySelectorAll("button")].find(
        (element) => element.textContent?.trim() === "Share",
      );
      if (button === undefined) return null;
      const value = Number.parseFloat(
        getComputedStyle(button).getPropertyValue(name as string),
      );
      if (Number.isNaN(value)) return null;
      const past = side === "above" ? value > (limit as number) : value < (limit as number);
      return past ? { value } : null;
    },
    [property, threshold, direction] as const,
    { polling: "raf" },
  );
  // `waitForFunction` resolves only on a truthy return, so the handle is the
  // object the predicate built; the type does not know that.
  const observed = await handle.jsonValue();
  if (observed === null) throw new Error(`waitForChannelPast(${property}) resolved with nothing`);
  return observed.value;
}

test.beforeEach(async ({ page }) => {
  await gotoPlayground(page);
});

test("a press compresses the surface, and the release lets it back out", async ({ page }) => {
  const share = page.getByRole("button", { name: "Share" });

  await share.hover();
  await page.mouse.down();
  await page.waitForTimeout(160);
  const pressed = await channel(share, PRESS);
  expect(pressed).toBeGreaterThan(0.7);

  // ~1–2% of geometric scale, composed on top of the measured rect rather than
  // written into the shape.
  const transform = await share.evaluate((element) => element.style.transform);
  expect(transform).toMatch(/^scale\(0\.9[0-9]+\)$/);

  await page.mouse.up();
  await page.waitForTimeout(500);
  expect(await channel(share, PRESS)).toBeLessThan(0.02);
  expect(await share.evaluate((element) => element.style.transform)).toBe("");
});

/**
 * No step in a trace covers most of the ground it covers in total.
 *
 * This is what "no snap or restart" means as something a machine can check, and
 * it is deliberately expressed as a *fraction of the travel* rather than as an
 * absolute bound: the drivers are frame-rate invariant, so a browser that drops a
 * frame legitimately moves further in one step than one that does not. A restart
 * or a snap is not a large step — it is a step that covers the whole distance,
 * whatever the frame rate. `@vitrea/motion` caps a frame at 50 ms, so no honest
 * step can be more than about three frames' worth.
 */
function expectContinuous(samples: readonly number[], label: string): void {
  const first = samples[0] ?? 0;
  const last = samples[samples.length - 1] ?? 0;
  const travel = Math.abs(last - first);
  expect(travel, `${label} should actually travel`).toBeGreaterThan(0.05);

  for (let i = 1; i < samples.length; i += 1) {
    const step = Math.abs((samples[i] ?? 0) - (samples[i - 1] ?? 0));
    expect(step, `${label}: frame ${i} jumped ${step.toFixed(3)} of ${travel.toFixed(3)}`).toBeLessThan(
      travel * 0.75,
    );
  }
}

test("releasing mid-press redirects rather than snapping or restarting", async ({ page }) => {
  const share = page.getByRole("button", { name: "Share" });

  await share.hover();
  await page.mouse.down();
  // Mid-flight, by the channel's own value rather than by a clock. The press is
  // rising, so "past 0.2 going up" is the crossing.
  await waitForChannelPast(page, PRESS, 0.2, "above");

  const samples = trace(page, 10, PRESS);
  await page.mouse.up();
  const after = await samples;

  /*
   * The trace starts a frame or two before the release is processed, so the
   * press is still rising at its head — which is exactly right, and why the
   * turn is found rather than assumed. What "no restart" forbids is going back
   * up *after* it has turned; what "no snap" forbids is arriving in one step.
   */
  const peak = Math.max(...after);
  const turn = after.indexOf(peak);
  for (let i = turn + 1; i < after.length; i += 1) {
    expect(after[i] ?? 1, `frame ${i} rose again after the release`).toBeLessThanOrEqual(
      (after[i - 1] ?? 1) + 0.02,
    );
  }
  expect(
    after[after.length - 1] ?? 1,
    `the release did not descend — samples were ${after.map((v) => v.toFixed(3)).join(" ")}`,
  ).toBeLessThan(peak - 0.1);
  expectContinuous(after, "release");
});

/*
 * The mirror of the release test, and the one place this suite dispatches its own
 * pointer event rather than driving Playwright's mouse.
 *
 * The property is redirection: re-pressed while the release is still travelling,
 * the channel turns and climbs from where the release had got to rather than from
 * rest. Producing that state needs the driver observed mid-flight and *then*
 * interrupted — and the press channel's response is 260 ms, which is the same
 * order as a Playwright round trip on a loaded machine. Observing from Node and
 * interrupting from Node therefore raced: measured over five three-engine runs,
 * one of them re-pressed after the release had already landed and the assertion
 * that catches exactly that ("the re-press restarted from rest") fired. Nothing
 * about the product was wrong; the scenario had not been produced.
 *
 * So the observation and the interruption happen in the same frame, in the page.
 * That costs the real-pointer path here — and the real-pointer path is covered by
 * the two tests above, which drive `page.mouse` end to end. What is under test in
 * this one is the interaction machine's redirect, and it reaches that through the
 * same `onPointerDown` React attaches for a trusted event.
 */
test("re-pressing mid-release continues the same trajectory", async ({ page }) => {
  const share = page.getByRole("button", { name: "Share" });

  await share.hover();
  await page.mouse.down();
  await waitForChannelPast(page, PRESS, 0.8, "above");

  /*
   * Armed BEFORE the release, on an already-resolved element handle.
   *
   * Both halves of that matter, and the second one is what took three attempts to
   * see. An `evaluate` issued after `mouse.up()` has to cross the bridge before its
   * loop starts, and on a loaded Firefox that crossing was long enough for the whole
   * release to land — which reads exactly like "the re-press restarted from rest",
   * the thing this test exists to catch. But issuing it *before* `mouse.up()` is not
   * enough either when it goes through a Locator: a Locator resolves its selector
   * first and only sends the evaluate once that round trip answers, so the
   * already-sent `mouse.up()` still won at random. Playwright preserves message
   * order on one connection, so the fix is to make the arming a *single* message —
   * one handle, resolved up front, then one evaluate.
   *
   * The diagnostic that settled it is in the failure message: the loop's very first
   * observation was -0.038, past the release's undershoot, with the ten frames after
   * it climbing cleanly to 1.03. The product was redirecting correctly every time;
   * the harness was arriving after the event.
   */
  const handle = await share.elementHandle();
  if (handle === null) throw new Error("the Share button has no handle");
  const armed = handle.evaluate(
    (element, [property, threshold, frames]) =>
      new Promise<{ atRepress: number; after: number[] }>((resolve) => {
        const read = (): number =>
          Number.parseFloat(getComputedStyle(element).getPropertyValue(property as string));
        const box = element.getBoundingClientRect();
        const after: number[] = [];
        let atRepress: number | undefined;

        const step = (): void => {
          const value = read();
          if (atRepress === undefined) {
            // Still waiting for the release to be observably in flight. A crossing,
            // not a window: once true it stays true, so a long frame cannot step
            // over it.
            if (value < (threshold as number)) {
              atRepress = value;
              element.dispatchEvent(
                new PointerEvent("pointerdown", {
                  bubbles: true,
                  isPrimary: true,
                  pointerId: 1,
                  button: 0,
                  buttons: 1,
                  clientX: box.x + box.width / 2,
                  clientY: box.y + box.height / 2,
                }),
              );
              after.push(value);
            }
            requestAnimationFrame(step);
            return;
          }
          after.push(value);
          if (after.length >= (frames as number)) {
            element.dispatchEvent(
              new PointerEvent("pointerup", { bubbles: true, isPrimary: true, pointerId: 1 }),
            );
            resolve({ atRepress, after });
            return;
          }
          requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }),
    [PRESS, 0.75, 10] as const,
  );
  await page.mouse.up();
  const { atRepress, after } = await armed;

  // The mirror of the release: the fall turns into a climb, and the climb starts
  // from wherever the fall had got to rather than from zero.
  const trough = Math.min(...after);
  const turn = after.indexOf(trough);
  const trail = after.map((value) => value.toFixed(3)).join(" ");
  expect(
    trough,
    `the re-press restarted from rest — caught at ${atRepress.toFixed(3)}, then ${trail}`,
  ).toBeGreaterThan(0.05);
  expect(trough).toBeLessThan(atRepress + 0.35);
  for (let i = turn + 1; i < after.length; i += 1) {
    expect(after[i] ?? 0, `frame ${i} fell again after the re-press`).toBeGreaterThanOrEqual(
      (after[i - 1] ?? 0) - 0.02,
    );
  }
  expect(after[after.length - 1] ?? 0).toBeGreaterThan(trough + 0.1);
  expectContinuous(after, "re-press");
});

test("the glow attacks fast and decays slowly, at the press point", async ({ page }) => {
  const share = page.getByRole("button", { name: "Share" });
  const box = await share.boundingBox();
  if (box === null) throw new Error("no box");

  // Press near the left edge, not the centre, so the recorded point is testable.
  await page.mouse.move(box.x + 12, box.y + box.height / 2);
  await page.mouse.down();
  await page.waitForTimeout(150);

  const attacked = await channel(share, GLOW);
  expect(attacked).toBeGreaterThan(0.6);

  const pressX = await share.evaluate((element) =>
    Number.parseFloat(getComputedStyle(element).getPropertyValue("--vitrea-press-x")),
  );
  expect(pressX).toBeGreaterThan(4);
  expect(pressX).toBeLessThan(24);

  await page.mouse.up();
  await page.waitForTimeout(150);
  const decayed = await channel(share, GLOW);
  // Same dwell each way; the slow decay is the driver's asymmetry, not ours.
  expect(decayed).toBeGreaterThan(0.15);
  expect(decayed).toBeLessThan(attacked);
});

test("keyboard activation presses the material too", async ({ page }) => {
  const share = page.getByRole("button", { name: "Share" });
  await share.focus();

  await page.keyboard.down("Space");
  await page.waitForTimeout(150);
  expect(await channel(share, "--vitrea-press")).toBeGreaterThan(0.5);

  await page.keyboard.up("Space");
  await page.waitForTimeout(500);
  expect(await channel(share, "--vitrea-press")).toBeLessThan(0.02);
});

test("a disabled control does not press", async ({ page }) => {
  const disabled = page.getByRole("button", { name: "Disabled" });
  await disabled.hover({ force: true });
  await page.mouse.down();
  await page.waitForTimeout(150);
  expect(await channel(disabled, "--vitrea-press")).toBeLessThan(0.02);
  await page.mouse.up();
});
