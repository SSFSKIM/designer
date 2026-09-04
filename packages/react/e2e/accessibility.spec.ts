/**
 * Parent acceptance #6 — "Accessibility modes."
 *
 * The media queries are emulated per engine and the *resolved* consequence is
 * asserted, not the query: what the spec promises is a change in the material and
 * in the motion, and the panel plus the surfaces are where that shows.
 *
 * Two emulations are not available everywhere, and each says so rather than being
 * quietly dropped from a project list: `forced-colors` is Chromium-only in
 * Playwright, and `prefers-contrast` is emulable on Chromium and Firefox.
 * `prefers-reduced-motion` works on all three, which is the one the motion half
 * of the policy hangs on.
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

test("reduced motion removes overshoot and deformation, and keeps continuity", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await gotoPlayground(page);

  expect(await readout(page, "overshoot")).toBe("none");
  expect(await readout(page, "deformation")).toBe("none");

  // Deformation gone means the press no longer compresses — while the press
  // itself still registers, because §Accessibility removes the deformation, not
  // the feedback.
  const share = page.getByRole("button", { name: "Share" });
  await share.hover();
  await page.mouse.down();
  await page.waitForTimeout(200);
  const press = await share.evaluate((element) =>
    Number.parseFloat(getComputedStyle(element).getPropertyValue("--vitrea-press")),
  );
  const glow = await share.evaluate((element) =>
    Number.parseFloat(getComputedStyle(element).getPropertyValue("--vitrea-glow")),
  );
  await page.mouse.up();

  expect(press).toBeLessThan(0.02);
  // No compression means no owned transform at all, not an identity one.
  expect(await share.evaluate((element) => element.style.transform)).toBe("");
  // Glow is illumination, not motion: it survives.
  expect(glow).toBeGreaterThan(0.5);
});

test("reduced motion keeps a morph travelling — positional continuity is an invariant", async ({
  page,
}) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await gotoPlayground(page);

  const platter = page.locator("[data-vitrea-morph]");
  const before = await platter.boundingBox();
  await page.getByRole("button", { name: "Actions" }).focus();
  await page.keyboard.press("Enter");
  await page.waitForTimeout(600);
  const after = await platter.boundingBox();

  expect(after?.height ?? 0).toBeGreaterThan((before?.height ?? 0) * 1.5);
});

test("increased contrast strengthens the border and flattens the foreground", async ({ page }) => {
  test.skip(
    test.info().project.name === "webkit",
    "Playwright cannot emulate prefers-contrast on WebKit.",
  );

  await page.emulateMedia({ contrast: "more" });
  await gotoPlayground(page);

  const plate = page.getByTestId("dom-plate");
  const border = await plate.evaluate((element) => getComputedStyle(element).borderTopWidth);
  expect(Number.parseFloat(border)).toBeGreaterThanOrEqual(2);
});

test("forced colors renders system colors with no glass", async ({ page }) => {
  test.skip(
    test.info().project.name !== "chromium",
    "Playwright emulates forced-colors on Chromium only.",
  );

  await page.emulateMedia({ forcedColors: "active" });
  await gotoPlayground(page);

  expect(await readout(page, "forcedColors")).toBe("true");
  expect(await readout(page, "glass")).toBe("none");

  const plate = page.getByTestId("dom-plate");
  const styles = await plate.evaluate((element) => {
    const computed = getComputedStyle(element);
    return {
      backdropFilter: computed.backdropFilter,
      boxShadow: computed.boxShadow,
      borderWidth: computed.borderTopWidth,
    };
  });

  expect(styles.backdropFilter).toBe("none");
  expect(styles.boxShadow).toBe("none");
  expect(Number.parseFloat(styles.borderWidth)).toBeGreaterThanOrEqual(2);
});

test("a GlassRoot prop overrules the media query", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  await gotoPlayground(page);
  expect(await readout(page, "overshoot")).toBe("none");

  // The panel's own control is the GlassRoot prop.
  await page.getByLabel("reducedMotion").selectOption("false");
  await expect
    .poll(async () => readout(page, "overshoot"))
    .toBe("elastic");
});

test("reduced transparency frosts more and refracts less", async ({ page }) => {
  await gotoPlayground(page);

  /*
   * The blur is read as a RATIO against the nominal one rather than matched
   * against a literal band.
   *
   * It used to assert `blur(1X.XXpx)` — two digits, which was the nominal σ
   * times the frost multiplier at one device scale. W12 G3 made the body's
   * widths device-pixel quantities (claims §5.56), so the same material writes
   * about 14 CSS px on a 1x context and about 8 on a 2x one, and WebKit's
   * Playwright descriptor composites at 2. What this test is about is the
   * regime, not the scale: under the preference the surface frosts harder than
   * it did, whatever the scale it is drawing at.
   *
   * Read off the published `--vitrea-blur` token since W16 G1, not out of a
   * filter string. The tier draws its body as two `backdrop-filter` layers on
   * created children rather than one filter on the host, and on an engine that
   * renders a reference filter inside `backdrop-filter` — Chromium — each layer's
   * width lives in an SVG `<filter>` definition rather than in the declaration.
   * The token is the tier's single-σ projection and it is exactly what an app
   * matching the material with its own `blur()` reads, so it is both the stable
   * number and the public one. The frost multiplies the base σ both layers are
   * built from, so this ratio is still the regime's whole effect on the body.
   */
  const blurOf = async (): Promise<number> => {
    const value = await page
      .getByTestId("dom-plate")
      .evaluate((element) => getComputedStyle(element).getPropertyValue("--vitrea-blur"));
    return Number(/([\d.]+)px/.exec(value)?.[1] ?? Number.NaN);
  };
  const nominal = await blurOf();
  expect(nominal).toBeGreaterThan(0);

  await page.getByLabel("reducedTransparency").selectOption("true");

  await expect.poll(async () => readout(page, "frost")).toBe("increased");
  expect(await readout(page, "refraction cap")).toBe("reduced");

  // The material follows the regime: a wider body. Polled, because the
  // declarations are written in the next frame's write phase.
  await expect.poll(blurOf).toBeGreaterThan(nominal);
});

test("the variant-mixing warning reaches the console", async ({ page }) => {
  const warnings: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "warning") warnings.push(message.text());
  });

  await gotoPlayground(page);
  await page.getByLabel("mix regular and clear in one group").check();

  await expect
    .poll(() => warnings.filter((text) => text.includes("variant-mixing")).length)
    .toBeGreaterThan(0);

  // And it is advice, not a coercion: both surfaces render as authored.
  await expect(page.getByTestId("texture-plate-small")).toHaveText("clear");
});
