/**
 * Parent acceptance #3 — "Interruptible press."
 *
 * Asserted on the published channel values, never on pixels. The claim is about
 * *continuity*: releasing mid-press must redirect the animation from its current
 * position and velocity with no snap or restart. A screenshot cannot tell a
 * redirect from a restart; a sequence of channel values can, and it is engine-
 * independent.
 */

import { expect, test } from "@playwright/test";

import { channel, gotoPlayground } from "./support";

const PRESS = "--vitrea-press";
const GLOW = "--vitrea-glow";

/** Read one channel once per animation frame, `count` times. */
async function trace(page: import("@playwright/test").Page, count: number, property: string) {
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
 * Wait until a channel is inside a window, checking every animation frame.
 *
 * Both continuity tests need to act on a surface that is *mid-flight*, and a
 * fixed sleep cannot promise that: the drivers are frame-rate invariant, so a
 * browser running long frames arrives sooner in wall-clock terms than one
 * running short ones. Waiting for the value itself is what makes the setup say
 * what it means.
 */
async function waitForChannelBetween(
  page: import("@playwright/test").Page,
  property: string,
  low: number,
  high: number,
): Promise<void> {
  await page.waitForFunction(
    ([name, lo, hi]) => {
      const button = [...document.querySelectorAll("button")].find(
        (element) => element.textContent?.trim() === "Share",
      );
      if (button === undefined) return false;
      const value = Number.parseFloat(
        getComputedStyle(button).getPropertyValue(name as string),
      );
      return value > (lo as number) && value < (hi as number);
    },
    [property, low, high] as const,
    { polling: "raf" },
  );
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
  // Mid-flight, by the channel's own value rather than by a clock.
  await waitForChannelBetween(page, PRESS, 0.2, 0.9);

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
  expect(after[after.length - 1] ?? 1).toBeLessThan(peak - 0.1);
  expectContinuous(after, "release");
});

test("re-pressing mid-release continues the same trajectory", async ({ page }) => {
  const share = page.getByRole("button", { name: "Share" });

  await share.hover();
  await page.mouse.down();
  await waitForChannelBetween(page, PRESS, 0.8, 1.1);
  await page.mouse.up();
  // Catch the release on its way down, not after it has landed.
  await waitForChannelBetween(page, PRESS, 0.25, 0.75);

  const atRepress = await channel(share, PRESS);
  const samples = trace(page, 10, PRESS);
  await page.mouse.down();
  const after = await samples;
  await page.mouse.up();

  // The mirror of the release: the fall turns into a climb, and the climb starts
  // from wherever the fall had got to rather than from zero.
  const trough = Math.min(...after);
  const turn = after.indexOf(trough);
  // Redirected mid-flight rather than restarted from rest: the climb begins
  // from a value the release was passing through, not from zero. The exact
  // value is not asserted — reading a channel and then dispatching an event are
  // separate round trips, and the spring keeps moving between them.
  expect(trough, "the re-press restarted from rest").toBeGreaterThan(0.05);
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
