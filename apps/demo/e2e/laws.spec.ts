/**
 * The material-laws page, asserted rather than eyeballed.
 *
 * A smoke suite, on the CSS tier by query string so it reads the same on a runner
 * with no adapter as on a machine with one: the page loads, every law is on it,
 * the stage follows the reader, each control moves the value the runtime
 * publishes, and the page's own layout reports no dev-mode findings. The optical
 * results are not asserted here; the renderer's unit tests pin each law's shape
 * and `packages/calibration` measures its magnitude against the reference.
 */

import { expect, test, type Page } from "@playwright/test";

const SECTIONS = ["tone", "tint", "body", "shadow", "lens", "nested"] as const;

async function gotoLaws(page: Page, query = "?renderer=css"): Promise<void> {
  await page.goto(`/laws/${query}`);
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await expect(page.getByRole("heading", { level: 1, name: "The material laws" })).toBeVisible();
}

/** Bring a section into the observation band and let the stage settle on it. */
async function showSection(page: Page, id: string): Promise<void> {
  await page.evaluate((target) => {
    document.getElementById(target)?.scrollIntoView({ block: "center", behavior: "instant" });
  }, id);
  await expect(page.locator(`#${id}`)).toHaveAttribute("data-current", "");
  await expect(page.locator(`.stage[data-mode='${id}']`).first()).toBeVisible();
  await page.waitForTimeout(400);
}

const propertyOf = (page: Page, testId: string, property: string): Promise<string> =>
  page
    .getByTestId(testId)
    .evaluate((element, name) => (element as HTMLElement).style.getPropertyValue(name), property);

test("every law is on the page, and the stage follows the reader", async ({ page }) => {
  await gotoLaws(page);
  for (const id of SECTIONS) {
    await expect(page.locator(`#${id} h2`)).toBeVisible();
    await showSection(page, id);
  }
});

test("the ground control moves the tone the runtime declares", async ({ page }) => {
  await gotoLaws(page);
  await showSection(page, "tone");

  // The advertised black endpoint must be reachable, not clamped to a near-black
  // ground above the compact branch's support (W36 G2, claims §5.180).
  await page.getByTestId("tone-level").fill("0");
  await expect(page.getByTestId("tone-level-readout")).toContainText("0.000 linear");
  await expect(page.getByTestId("tone-law")).toContainText("0.231");

  await page.getByTestId("tone-level").fill("20");
  await expect(page.getByTestId("tone-level-readout")).toContainText("0.020 linear");
  await page.waitForTimeout(400);
  const dark = await propertyOf(page, "tone-small", "--vitrea-tint");

  await page.getByTestId("tone-level").fill("900");
  await expect(page.getByTestId("tone-level-readout")).toContainText("0.900 linear");
  await page.waitForTimeout(400);
  const light = await propertyOf(page, "tone-small", "--vitrea-tint");

  expect(dark).not.toBe("");
  expect(light).not.toBe(dark);

  // The law's readout moves with the control, and the two plates it evaluates
  // for are ordered by size wherever the curve is not flat.
  await expect(page.getByTestId("tone-law")).toContainText("0.9");
});

test("the tint strength moves the declared tint on both plates", async ({ page }) => {
  await gotoLaws(page);
  await showSection(page, "tint");

  const full = {
    dark: await propertyOf(page, "tint-dark", "--vitrea-tint"),
    light: await propertyOf(page, "tint-light", "--vitrea-tint"),
  };
  expect(full.dark).not.toBe("");

  await page.getByTestId("tint-strength").fill("50");
  await expect(page.getByTestId("tint-readout")).toContainText("/ 50%");
  await page.waitForTimeout(400);
  const half = {
    dark: await propertyOf(page, "tint-dark", "--vitrea-tint"),
    light: await propertyOf(page, "tint-light", "--vitrea-tint"),
  };
  expect(half.dark).not.toBe(full.dark);
  expect(half.light).not.toBe(full.light);
});

test("the span control moves the surface and the blur it is given", async ({ page }) => {
  await gotoLaws(page);
  await showSection(page, "body");

  const blurOf = async (): Promise<number> =>
    Number.parseFloat(await propertyOf(page, "body-plate", "--vitrea-blur"));

  await page.getByTestId("body-span").fill("40");
  await expect(page.getByTestId("body-span-readout")).toContainText("40px");
  await page.waitForTimeout(400);
  const small = await page.getByTestId("body-plate").boundingBox();
  const smallBlur = await blurOf();

  await page.getByTestId("body-span").fill("288");
  await expect(page.getByTestId("body-span-readout")).toContainText("288px");
  await page.waitForTimeout(400);
  const large = await page.getByTestId("body-plate").boundingBox();
  const largeBlur = await blurOf();

  if (small === null || large === null) throw new Error("the plate has no box");
  expect(Math.round(small.height)).toBe(40);
  expect(Math.round(large.height)).toBe(288);
  // The CSS tier's single width rides the mix, which rises with the span.
  expect(largeBlur).toBeGreaterThan(smallBlur);
  // And the page's own evaluation of the law agrees with what the tier wrote.
  await expect(page.getByTestId("body-single")).toContainText(`${largeBlur.toFixed(2)} px`);
});

/**
 * The σ readout, against the shadow the tier actually drew (W30 G4 review
 * closure; claims §5.160 §9).
 *
 * The readout landed at G4 with nothing pinning it: the body's two widths are
 * asserted against `--vitrea-blur` above, and the shadow — the wave's own
 * operator, and the only place on the site it is a number the reader can move —
 * had no assertion at all. It is asserted the same way, against what the tier
 * wrote rather than against a literal: `cssShadowBlurRadius` is 2σ, so the outer
 * entry of the plate's overlay layer `box-shadow` divided by two is the σ the
 * page must be printing. Both ends of the control, because a σ law that had
 * collapsed to a constant would still match at one of them.
 */
const shadowSigmaDrawn = (page: Page, testId: string): Promise<number> =>
  page.getByTestId(testId).evaluate((element) => {
    const layer = element.querySelector<HTMLElement>('[data-vitrea-css-layer="overlay"]');
    if (layer === null) throw new Error("the plate has no overlay layer to carry a shadow");
    // Read computed rather than inline, because what a browser serialises a
    // `box-shadow` back to is not what the tier wrote it as: the colour moves to
    // the front and `inset` to the end, and every entry gains its full four
    // lengths. Parsing the normalised form is parsing what the compositor has.
    const drawn = getComputedStyle(layer).boxShadow;
    // The rim is the inset entry of the same list; the outer shadow is the other.
    const outer = drawn
      .split(/,(?![^(]*\))/)
      .map((part) => part.trim())
      .find((part) => part !== "" && part !== "none" && !part.includes("inset"));
    if (outer === undefined) throw new Error(`no outer shadow in "${drawn}"`);
    const lengths = outer.match(/-?\d+(?:\.\d+)?px/g) ?? [];
    // `<colour> <x> <y> <blur> <spread>`, normalised: the third length is the blur.
    const blur = lengths.length === 4 ? lengths[2] : undefined;
    if (blur === undefined) throw new Error(`unreadable shadow "${outer}"`);
    return Number.parseFloat(blur) / 2;
  });

test("the outer shadow's σ readout is the σ the tier drew, at both ends of the span", async ({
  page,
}) => {
  await gotoLaws(page);
  await showSection(page, "body");

  const drawn: Record<string, number> = {};
  for (const span of ["32", "288"] as const) {
    await page.getByTestId("body-span").fill(span);
    await expect(page.getByTestId("body-span-readout")).toContainText(`${span}px`);
    await page.waitForTimeout(400);
    drawn[span] = await shadowSigmaDrawn(page, "body-plate");
    await expect(
      page.getByTestId("body-shadow-sigma"),
      `the σ readout at span ${span}`,
    ).toHaveText(`${(drawn[span] ?? Number.NaN).toFixed(2)} px`);
  }

  // The law is graded, not a constant: the two ends must differ, or the two
  // assertions above would both hold against one number.
  expect(drawn["288"] ?? 0).toBeGreaterThan(drawn["32"] ?? 0);

  // And the prose above the readout, which quotes both ends and their ratio, is
  // derived from the same law since the review closure. This is what says so: a
  // refit that moved σ and left the sentence behind fails here.
  const thin = drawn["32"] ?? Number.NaN;
  const wide = drawn["288"] ?? Number.NaN;
  const note = await page.locator("#body .note").last().textContent();
  expect(note).toContain(`${thin.toFixed(2)}px band`);
  expect(note).toContain(`${Math.round(wide / thin)} times as wide`);
});

/**
 * The `/laws/` shadow stage, against the exterior the tier actually drew (W32 G2;
 * Decision Log 1 (d) as ruled by the user; claims §5.169 §4).
 *
 * The case above pins the σ readout in the BODY section, which is where the σ law
 * first appeared as a number a reader could move. This section is the operator's
 * own, and it prints three more of the material's numbers and the depth at three
 * distances — so it is pinned the same way and for the same reason: against what
 * the tier wrote, never against a literal. `outerShadowDrawn` reads all four
 * lengths and the alpha out of the computed `box-shadow` rather than the inline
 * one, because what a browser serialises the property back to is not what the
 * tier wrote it as.
 *
 * The receded half is the other assertion and is not a variation of the first.
 * The receded documents carry an amplitude of zero (W32 Decision Log 2, on 121 of
 * 121 inactive rows where Apple's own transmission reads exactly 1.000000), so
 * `outerShadowDeclaration` resolves `"none"` and there is no outer entry in the
 * list at all. A test that only checked the shadow got smaller would pass on a
 * receded material that merely faded.
 */
interface DrawnShadow {
  readonly offsetYPx: number;
  readonly blurPx: number;
  readonly spreadPx: number;
  readonly alpha: number;
}

const outerShadowDrawn = (page: Page, testId: string): Promise<DrawnShadow | null> =>
  page.getByTestId(testId).evaluate((element) => {
    const layer = element.querySelector<HTMLElement>('[data-vitrea-css-layer="overlay"]');
    if (layer === null) throw new Error("the plate has no overlay layer to carry a shadow");
    const drawn = getComputedStyle(layer).boxShadow;
    // The rim is the inset entry of the same list; the outer shadow is the other,
    // and its absence is the receded material's whole statement.
    const outer = drawn
      .split(/,(?![^(]*\))/)
      .map((part) => part.trim())
      .find((part) => part !== "" && part !== "none" && !part.includes("inset"));
    if (outer === undefined) return null;
    const lengths = (outer.match(/-?\d+(?:\.\d+)?px/g) ?? []).map(Number.parseFloat);
    if (lengths.length !== 4) throw new Error(`unreadable shadow "${outer}"`);
    const alpha = /rgba?\([^)]*?([\d.]+)\s*\)/.exec(outer);
    // `<colour> <x> <y> <blur> <spread>`, normalised.
    return {
      offsetYPx: lengths[1] ?? Number.NaN,
      blurPx: lengths[2] ?? Number.NaN,
      spreadPx: lengths[3] ?? Number.NaN,
      alpha: alpha === null ? 1 : Number.parseFloat(alpha[1] ?? "1"),
    };
  });

/**
 * Pin the window pose through the page's own control and wait for the RUNTIME to
 * report it. The select's value is the pose the group reports, never the one
 * asked for, so waiting on the endpoint readout is waiting on the material.
 */
async function pinPose(page: Page, pose: "active" | "receded"): Promise<void> {
  await page.getByTestId("shadow-pose").selectOption(pose);
  const endpoint = page.getByTestId("shadow-endpoint");
  await expect(endpoint).toHaveText(/^apple-macos-/);
  if (pose === "receded") await expect(endpoint).toHaveText(/-receded$/);
  else await expect(endpoint).not.toHaveText(/-receded$/);
  await page.waitForTimeout(400);
}

test("the exterior's readout is the shadow the tier drew, at both ends of the span", async ({
  page,
}) => {
  await gotoLaws(page);
  await showSection(page, "shadow");
  await pinPose(page, "active");

  const drawn: Record<string, DrawnShadow> = {};
  const depths: Record<string, readonly number[]> = {};
  for (const span of ["32", "160"] as const) {
    await page.getByTestId("shadow-span").fill(span);
    await expect(page.getByTestId("shadow-span-readout")).toContainText(`${span}px`);
    await page.waitForTimeout(400);
    const here = await outerShadowDrawn(page, "shadow-plate");
    if (here === null) throw new Error(`no outer shadow drawn at span ${span}`);
    drawn[span] = here;

    // Every length the readout prints, against the length the tier wrote. The
    // blur radius is 2σ by CSS Backgrounds 3's convention, which is why the σ row
    // and the blur row are both here: they are one number under two conventions
    // and getting the factor wrong would halve or double the shadow silently.
    await expect(page.getByTestId("shadow-sigma"), `σ at span ${span}`).toHaveText(
      `${(here.blurPx / 2).toFixed(2)} px`,
    );
    await expect(page.getByTestId("shadow-css-blur"), `the blur radius at span ${span}`).toHaveText(
      `${here.blurPx.toFixed(2)} px`,
    );
    await expect(page.getByTestId("shadow-outset"), `the outset at span ${span}`).toHaveText(
      `${here.spreadPx.toFixed(2)} px`,
    );
    await expect(page.getByTestId("shadow-offset"), `the offset at span ${span}`).toHaveText(
      `${here.offsetYPx.toFixed(2)} px`,
    );
    // The depth is the falloff the other tier evaluates per pixel and this tier
    // hands to a blur, so it is not readable off the `box-shadow`. What is
    // asserted here is that it is a graded profile rather than one number: the
    // shadow is deepest nearest the edge and falls monotonically away from it.
    depths[span] = await Promise.all(
      [3, 12, 24].map(async (distance) =>
        Number.parseFloat(
          (await page.getByTestId(`shadow-depth-${distance}`).innerText()).replace(" %", ""),
        ),
      ),
    );
    const profile = depths[span] ?? [];
    expect(profile[0], `the depth at 3px, span ${span}`).toBeGreaterThan(0);
    expect(profile[0], `the depth profile at span ${span}`).toBeGreaterThan(profile[1] ?? 0);
    expect(profile[1], `the depth profile at span ${span}`).toBeGreaterThanOrEqual(
      profile[2] ?? 0,
    );
  }

  // The σ law is graded in the casting span and the two lengths are NOT: they are
  // lengths of the material, and a page that printed them off the caster would
  // show them moving here.
  expect(drawn["160"]?.blurPx ?? 0).toBeGreaterThan(drawn["32"]?.blurPx ?? 0);
  expect(drawn["160"]?.spreadPx).toBe(drawn["32"]?.spreadPx);
  expect(drawn["160"]?.offsetYPx).toBe(drawn["32"]?.offsetYPx);

  // And the REACH grades with it, which is the consequence of the σ law a reader
  // can see on the stage: at the thinnest caster the shadow is gone by 24 CSS px
  // below the edge and the readout prints the zero, while at the widest it is
  // still several per cent deep there. A law that had collapsed to a constant
  // would print the same two profiles.
  expect(depths["32"]?.[2], "the thin caster's shadow does not reach 24px").toBe(0);
  expect(depths["160"]?.[2] ?? 0, "the wide caster's shadow does").toBeGreaterThan(0);
});

test("the receded window casts no exterior at all, and the readout shows the zero", async ({
  page,
}) => {
  await gotoLaws(page);
  await showSection(page, "shadow");

  await pinPose(page, "active");
  const focused = await outerShadowDrawn(page, "shadow-plate");
  if (focused === null) throw new Error("the focused caster drew no outer shadow");
  expect(focused.alpha).toBeGreaterThan(0);

  await pinPose(page, "receded");
  // Not fainter — absent. `outerShadowDeclaration` resolves `"none"` at zero
  // alpha, so there is no outer entry in the list for the reader to look for.
  expect(await outerShadowDrawn(page, "shadow-plate")).toBeNull();
  for (const distance of [3, 12, 24]) {
    await expect(
      page.getByTestId(`shadow-depth-${distance}`),
      `the depth ${distance}px below the edge, receded`,
    ).toHaveText("0.00 %");
  }
  // And the group itself names the receded endpoint, which is what the readout's
  // numbers were resolved through.
  await expect(
    page.locator("#shadow").getByTestId("material-document"),
  ).toContainText("-receded");
});

test("the refraction rung is a policy result, and the readout says which", async ({ page }) => {
  await gotoLaws(page);
  await showSection(page, "lens");

  // On the CSS tier the rung reads `none`, and it is the tier that says so.
  await expect(page.getByTestId("lens-rung")).toHaveValue("none");
  await expect(page.getByTestId("lens-regime")).toHaveText("nominal");

  // Arriving with the approximate rung asked for: the override is a construction
  // prop, so the page reads it from the URL, and the policy resolves to reduced.
  await gotoLaws(page, "?renderer=webgpu&rung=approximate");
  await showSection(page, "lens");
  await expect(page.getByTestId("lens-regime")).toHaveText("reduced");
  await expect(page.getByTestId("lens-cap")).toHaveText("approximate");
});

test("the pane sits on the overlay plane, over the base surface", async ({ page }) => {
  await gotoLaws(page);
  await showSection(page, "nested");

  const base = page.getByTestId("nested-base");
  const over = page.getByTestId("nested-over");
  await expect(base).toHaveAttribute("data-vitrea-host-plane", "base");
  await expect(over).toHaveAttribute("data-vitrea-host-plane", "overlay");

  const baseBox = await base.boundingBox();
  const overBox = await over.boundingBox();
  if (baseBox === null || overBox === null) throw new Error("the nest has no box");
  expect(Math.round(baseBox.width)).toBe(220);
  expect(Math.round(overBox.width)).toBe(120);
  expect(overBox.x).toBeGreaterThan(baseBox.x);
  expect(overBox.x + overBox.width).toBeLessThan(baseBox.x + baseBox.width);
  expect(overBox.y).toBeGreaterThan(baseBox.y);
  expect(overBox.y + overBox.height).toBeLessThan(baseBox.y + baseBox.height);
});

test("the page's own layout reports no dev-mode findings", async ({ page }) => {
  const problems: string[] = [];
  page.on("console", (message) => {
    if (message.text().includes("[vitrea:")) problems.push(message.text());
  });
  page.on("pageerror", (error) => problems.push(`pageerror: ${error.message}`));

  await gotoLaws(page);
  for (const id of SECTIONS) await showSection(page, id);
  await showSection(page, "tone");

  await expect(page.getByTestId("authoring-findings")).toHaveCount(0);
  await expect(page.getByTestId("authoring-clean").first()).toBeVisible();
  expect(problems.filter((line) => line.includes("pageerror"))).toEqual([]);
});
