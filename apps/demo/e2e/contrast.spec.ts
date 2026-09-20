/**
 * Text contrast over live glass, on the CSS tier, measured on the rendered pixels.
 *
 * The method and the reason axe cannot answer this are in `glass-contrast.ts`,
 * which these cases and the GPU-tier ones both read. What belongs here is which
 * labels are held to which floor, and where.
 *
 * Sampled at several points in the backdrop's drift, and the worst is the one that
 * counts. The field moves, so a single sample measures one moment rather than the
 * page.
 */

import { expect, test, type Page } from "@playwright/test";

import { BODY_FLOOR, LARGE_FLOOR, worstNow, worstRatio } from "./glass-contrast";

/*
 * Three times the default timeout for every case in this file, which is the
 * one-line fix `specs/tech-debt-tracker.md` has been holding since 2026-09-11
 * and said to take with the next demo e2e change. This is that change.
 *
 * The budget here is structural rather than incidental: the phase-sampled cases
 * sleep through `SAMPLE_DELAYS` — 13 s of fixed waiting — and screenshot every
 * `.plate strong` at each phase, and the ground sweep below walks twenty slider
 * stops with a settle at each. The tracker measured one of them at 24.1 s
 * against a 30 s default on an idle machine, and at W29 G4 the sweep crossed it
 * outright: the macOS 27 material blurs the CSS tier at 2.2 times the sigma the
 * macOS 26.5 one did, which is more work per frame at every one of those stops.
 *
 * It buys time and nothing else. No sample, no floor and no assertion moves, and
 * a case that fails on a floor still fails on it.
 */
test.slow();

async function showSection(page: Page, id: string): Promise<void> {
  await page.goto("/?renderer=css");
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await page.evaluate((target) => {
    document.getElementById(target)?.scrollIntoView({ block: "center", behavior: "instant" });
  }, id);
  await expect(page.locator(`#${id}`)).toHaveAttribute("data-current", "");

  /*
   * Wait for the material to exist before measuring it, rather than for a clock.
   *
   * Every sample below is folded into a MINIMUM, so one reading taken before the
   * tier has materialized a surface is not a slow start, it is a permanent
   * result: the glass is unpainted, the screenshot is the stage's dark ground,
   * and the ratio it reports is about 1:1 whatever the page does afterwards. The
   * first sample used to be a 400ms timeout, which held on a warm dev server and
   * did not on a cold one — the suite failed on the first run in a fresh
   * worktree and passed on every run after it, which is the signature of a test
   * measuring the server rather than the page.
   *
   * `--vitrea-tint` is the CSS tier's own statement that it has written this
   * host's material, and this file always asks for that tier by query string, so
   * it is the honest ready signal rather than a proxy for one.
   */
  await expect
    .poll(() =>
      page.evaluate(() =>
        [...document.querySelectorAll<HTMLElement>("[data-vitrea-node]")].filter(
          (host) => host.style.getPropertyValue("--vitrea-tint") !== "",
        ).length,
      ),
    )
    .toBeGreaterThan(0);
}

test("control labels on glass hold the body-text floor", async ({ page }) => {
  await showSection(page, "behavior");
  const worst = await worstRatio(page, ".control");
  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(BODY_FLOOR);
});

test("segment labels on glass hold the body-text floor, selected and not", async ({ page }) => {
  await showSection(page, "behavior");
  const worst = await worstRatio(page, ".segment");
  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(BODY_FLOOR);
});

test("the plates' labels hold the large-text floor", async ({ page }) => {
  await showSection(page, "material");
  const worst = await worstRatio(page, ".plate strong");
  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(LARGE_FLOOR);
});

/*
 * The same plates over page content rather than over the texture (W27f G0).
 *
 * A separate case because the backdrop is a different kind of thing and the
 * material is drawn from a different path: this group cannot sample, so its ink is
 * chosen against the level the page declares, over a ground that carries body copy
 * and a gradient rather than a graticule and a field. Neither the ink nor the
 * surface it lands on is the material stage's, so neither is its contrast.
 *
 * No phase sampling: nothing on this stage moves. The one reading is the page.
 */
test("the plates' labels hold the large-text floor over page content", async ({ page }) => {
  await showSection(page, "page");
  const worst = await worstNow(page, ".plate strong", "over page content");
  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(LARGE_FLOOR);
});

/*
 * The backdrop tone stage, at every position the reader can put it in (W7).
 *
 * This is the case the axis needs and the others cannot cover. Backdrop tone
 * adaptation moves a surface's body all the way from a light glass plate to the
 * backdrop's own level, and the runtime re-chooses the ink against it somewhere in
 * the middle — so the label's contrast is not a property of the page, it is a
 * function of a control, and the only honest way to hold it to a floor is to walk
 * the control. The crossing is per surface: the 40px plate flips near 0.05 and the
 * 68px one near 0.01, so the worst reading is never at either end.
 *
 * No phase sampling here, unlike the cases above. The tone stage's ground is flat
 * and still by construction — the drifting field is off, which is what makes the
 * convergence exact — so there is no drift to catch, and what varies instead is
 * the one thing this loop varies.
 */
test("the plates' labels hold the large-text floor at every ground level", async ({ page }) => {
  await showSection(page, "tone");

  /*
   * The control's value is a POSITION on a geometric ladder since W30 G4, not a
   * count of thousandths (`Stage.tsx`'s `TONE_GROUND`). The sweep walks positions
   * and reads the level back off the page rather than computing it: every one of
   * the 81 stops prints a distinct four-decimal level, so "the readout changed"
   * is the settle signal the stop's own number used to be, and this file does not
   * have to carry a copy of the ladder's arithmetic to know where it is.
   */
  const slider = page.getByTestId("ground-level");
  const readout = page.getByTestId("ground-level-readout");
  const levelNow = async (): Promise<string> =>
    (/^\s*(0\.\d+) linear/.exec((await readout.textContent()) ?? "")?.[1] ?? "");
  let worst = { ratio: Number.POSITIVE_INFINITY, where: "" };
  // Seeded with what the control already shows, so the first fill has to move it.
  let previous = await levelNow();
  for (let position = 0; position <= 80; position += 4) {
    await slider.fill(String(position));
    await expect
      .poll(levelNow, { message: `the ground readout did not move off ${previous}` })
      .not.toBe(previous);
    const level = await levelNow();
    expect(level, `position ${position}`).not.toBe("");
    previous = level;
    // Past the material transition, so the reading is the settled surface rather
    // than a frame the reader never stops on.
    await page.waitForTimeout(320);
    const found = await worstNow(page, ".plate strong", `at ground ${level}`);
    if (found.ratio < worst.ratio) worst = found;
  }

  expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(LARGE_FLOOR);
});
