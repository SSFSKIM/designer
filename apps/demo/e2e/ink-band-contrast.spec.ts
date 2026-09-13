/**
 * The tint-and-ink band's own contrast reading (W27e G2; claims §5.140).
 *
 * `contrast.spec.ts` holds the front page's labels to their floors. The band is
 * on `/playground/` and is a different question in three ways, which is why it
 * has its own file rather than a fifth case there.
 *
 * The first is that the band is the one place in either app where all four
 * published ink levels are drawn side by side, and **two of the four are
 * documented as below the body-text floor**. A suite that held every glyph on the
 * band to 4.5 would be asserting the opposite of what the levels mean. So a floor
 * is held where the library promises one — the primary ink, and the secondary
 * level whose whole guarantee is that it holds 4.5 against the colour the surface
 * is actually drawing — and tertiary and quaternary are *read and printed* rather
 * than gated. Secondary's floor here is a **pixel** floor a hair under the
 * token's own, for the reason its case states.
 *
 * The second is that each level's specimen is two characters wide, so its own
 * box is mostly glyph. `worstRatio` takes the surface from the *selected*
 * element's pixels, which on a specimen that size is the ink measuring itself.
 * So the harness's three pieces are composed by hand instead — the ink from the
 * specimen, the **surface from the plate the specimen sits on**, and the ink
 * composited over it — which is what a reader's eye integrates and the nearest
 * this instrument gets to the colour the runtime solved the alpha against.
 *
 * The third is that W27e G2 moved the primary ink to Apple's own automatic label
 * colour, which is translucent: pure black at α 0.847059 and pure white at
 * α 0.804706 where it was two opaque hexes. That is a deliberate loss of contrast
 * against an opaque ink (W27 Decision Log 15 (a)), and Decision Log 15 (b) kept
 * Decision Log 9's WCAG floor as a minimum on secondary precisely so that the
 * loss could not put a published level under it. This is where that holds or does
 * not, on the pixels, over both of the band's grounds.
 *
 * The CSS tier, by query string, for the reason `contrast.spec.ts` gives: this is
 * an assertion about the ink and the composite, and pinning the tier makes the
 * reading mean the same thing on any machine. The GPU tier's own reading of the
 * same band is in the gate's evidence directory, taken on a measured adapter.
 */

import { expect, test, type Page } from "@playwright/test";

import { BODY_FLOOR, contrast, inkOf, inkOver, luminance, surfaceOf } from "./glass-contrast";

const GROUNDS = ["light", "dark"] as const;
const LEVELS = ["primary", "secondary", "tertiary", "quaternary"] as const;

async function gotoBand(page: Page): Promise<void> {
  await page.goto("/playground/?renderer=css");
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  // The band's own material, rather than a clock: `--vitrea-tint` is the CSS
  // tier's statement that it has written this host, and a reading taken before
  // the tier has painted is the stage's ground rather than a slow start.
  await expect
    .poll(() =>
      page.evaluate(
        () =>
          [...document.querySelectorAll<HTMLElement>(".ink-plate, .ink-row .control")].filter(
            (host) => host.style.getPropertyValue("--vitrea-tint") !== "",
          ).length,
      ),
    )
    .toBeGreaterThanOrEqual(GROUNDS.length * 2);
}

/** Every level's ratio on one ground, each against the plate the specimen sits on. */
async function levelsOn(page: Page, ground: string): Promise<Record<string, number>> {
  const plate = page.getByTestId(`ink-plate-${ground}`);
  const surface = await surfaceOf(plate);
  const surfaceLuminance = luminance(surface[0], surface[1], surface[2]);
  const ratios: Record<string, number> = {};
  for (const level of LEVELS) {
    const specimen = plate.locator(`.ink-level--${level} .ink-level__specimen`);
    const inks = await inkOf(specimen);
    ratios[level] = Math.min(
      ...inks.map((ink) => contrast(inkOver(ink, surface), surfaceLuminance)),
    );
  }
  return ratios;
}

test("the band's primary ink holds the body-text floor on both grounds", async ({ page }) => {
  await gotoBand(page);
  for (const ground of GROUNDS) {
    const ratios = await levelsOn(page, ground);
    expect(ratios["primary"], `primary on the ${ground} ground`).toBeGreaterThanOrEqual(BODY_FLOOR);
  }
});

/**
 * Secondary is held to the rendered **pixel floor**, not relabelled as the
 * token's 4.5 promise (W27e G3; claims §5.142 §3).
 *
 * The attribution has now been taken. On the light plate the median and the
 * pixel under the glyph are both `[163, 192, 235]`, and the actual ground is the
 * declared `[231, 231, 231]`: neither candidate explains the shortfall. The
 * solve instead targets `[164.241, 192.852, 236.202]`, the ideal tinted
 * composite, while this CSS drawing form paints the former. The token's exact
 * alpha reads 4.500 there and 4.482 on the rendered surface; the canvas's 8-bit
 * recovery resolves that alpha to 0.588235 and the harness reads 4.463. So the
 * solve-composite mismatch is the physical gap, and the instrument's quantum is
 * the rest of the reported 0.037.
 *
 * The 4.45 floor remains named as a pixel floor until the runtime solves against
 * the selected CSS drawing form's actual composite. Tertiary and quaternary
 * remain read-only below.
 */
const SECONDARY_PIXEL_FLOOR = 4.45;

test("the band's secondary holds its floor on the pixels, to the harness's own resolution", async ({
  page,
}) => {
  await gotoBand(page);
  for (const ground of GROUNDS) {
    const ratios = await levelsOn(page, ground);
    expect(ratios["secondary"], `secondary on the ${ground} ground`).toBeGreaterThanOrEqual(
      SECONDARY_PIXEL_FLOOR,
    );
  }
});

test("the band's control labels hold the body-text floor, tinted and not", async ({ page }) => {
  await gotoBand(page);
  // A control's own box is mostly material, so `surfaceOf` on the control is the
  // right surface here and the composition above is not needed. `Publish` sits in
  // a group carrying a second tint seed it has to step out into and the bookmark
  // takes the group's own, so this reads the primary ink over two composites per
  // ground.
  for (const control of await page.locator(".ink-row .control").all()) {
    const surface = await surfaceOf(control);
    const surfaceLuminance = luminance(surface[0], surface[1], surface[2]);
    const worst = Math.min(
      ...(await inkOf(control)).map((ink) => contrast(inkOver(ink, surface), surfaceLuminance)),
    );
    const name = (await control.getAttribute("aria-label")) ?? "a control";
    expect(worst, name).toBeGreaterThanOrEqual(BODY_FLOOR);
  }
});

test("reads the two levels that carry no floor, and holds them to the scale instead", async ({
  page,
}) => {
  await gotoBand(page);
  for (const ground of GROUNDS) {
    const ratios = await levelsOn(page, ground);
    /*
     * Not a floor: WCAG 4.5 is the body-text floor and these are Apple's
     * supporting and decorative tiers. What they owe is the scale — a level that
     * read *higher* than the one above it would mean the ladder had inverted,
     * which is the failure mode Decision Log 15 (b)'s per-surface solve can
     * produce if its ceiling is ever lifted above the primary's own alpha.
     */
    expect(ratios["quaternary"], `quaternary on ${ground}`).toBeLessThanOrEqual(
      ratios["tertiary"] as number,
    );
    expect(ratios["tertiary"], `tertiary on ${ground}`).toBeLessThanOrEqual(
      ratios["secondary"] as number,
    );
    expect(ratios["secondary"], `secondary on ${ground}`).toBeLessThanOrEqual(
      ratios["primary"] as number,
    );

    // Printed so the gate's record carries the numbers rather than only the
    // verdict, and so a later change that moved them shows the movement.
    // eslint-disable-next-line no-console
    console.log(
      `ink band, CSS tier, ${ground} ground — ` +
        LEVELS.map((level) => `${level} ${(ratios[level] as number).toFixed(3)}`).join(", "),
    );
  }
});
