/**
 * The public site, asserted rather than eyeballed.
 *
 * Three claims are worth a test here, and each is a claim the page itself makes:
 *
 *  - **The layout is legal.** `devMode` is on in the shipped build, so X1's
 *    same-plane overlap check, the group-proxy-overlap check, the variant rules and
 *    the startup probe all run on this page in front of the reader. `DESIGN.md` §9
 *    exists so the findings list stays empty, and this is what checks that it is.
 *  - **The reference pair is a comparison.** Both sides read
 *    `apps/reference-apple/scenes.json`, so the live surface must land at exactly
 *    the coordinates that file declares, over exactly the raster the native capture
 *    was composited over. A pair that only looked aligned would be an illustration.
 *  - **The accessibility floor holds on the library's own front page.** axe clean,
 *    keyboard complete, honest under reduced motion, no two-dimensional scrolling
 *    at 320 CSS px, and no glass under forced colours.
 */

import AxeBuilder from "@axe-core/playwright";
import { expect, test, type Page } from "@playwright/test";

/**
 * The codes that name a mistake in *this page's* layout, as opposed to something
 * the browser could not offer. `DESIGN.md` §9 is about the first set only: a
 * machine with no WebGPU adapter reports `webgpu-unavailable`, and that finding is
 * the honesty core working rather than a defect to assert away.
 */
const AUTHORING_CODES = [
  "same-plane-overlap",
  "group-proxy-overlap",
  "merge-distance-below-padding",
  "variant-mixing",
  "clear-variant-needs-dimming",
  "host-outside-plane",
  "sampling-padding-below-3-sigma",
  "merge-distance-below-effective-padding",
  "proxy-area-over-cap",
  "proxy-overlap-after-enforcement",
  // The layer model. Apple makes glass a controls-layer material and names
  // glass-on-glass a failure; these two fire when this page's own composition
  // breaks that rule, so an empty list here is the page's claim to obey it.
  "glass-inside-glass",
  "glass-in-content-layer",
];

/** `scenes.json`: canvas 320x200, capsule-button 120x44, centred. */
const CANVAS = { width: 320, height: 200 };
const CAPSULE = { width: 120, height: 44 };

async function gotoSite(page: Page, query = ""): Promise<void> {
  await page.goto(`/${query}`);
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
}

/** Bring a section into the observation band and let the stage settle on it. */
async function showSection(page: Page, id: string): Promise<void> {
  await page.evaluate((target) => {
    document.getElementById(target)?.scrollIntoView({ block: "center", behavior: "instant" });
  }, id);
  await expect(page.locator(`#${id}`)).toHaveAttribute("data-current", "");
  await page.waitForTimeout(500);
}

const scan = (page: Page) =>
  new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "best-practice"]);

type AxeResults = Awaited<ReturnType<AxeBuilder["analyze"]>>;

const describeViolations = (violations: AxeResults["violations"]): string[] =>
  violations.map(
    (violation) =>
      `${violation.id}: ${violation.help} — ${violation.nodes.map((node) => node.target.join(" ")).join(", ")}`,
  );

test.describe("the layout is legal", () => {
  test("the shipped page reports no dev-mode findings, in any stage mode", async ({ page }) => {
    const problems: string[] = [];
    page.on("console", (message) => {
      if (message.text().includes("[vitrea:")) problems.push(message.text());
    });
    page.on("pageerror", (error) => problems.push(`pageerror: ${error.message}`));

    await gotoSite(page);
    // The readout is the page's own claim; assert the claim and the channel agree.
    await expect(page.getByTestId("authoring-clean")).toBeVisible();

    for (const id of ["material", "reference", "behavior", "access", "tiers", "install"]) {
      await showSection(page, id);
    }
    // Back to a section that shows the readout, so a late finding would be visible.
    await showSection(page, "material");

    await expect(page.getByTestId("authoring-findings")).toHaveCount(0);
    await expect(page.getByTestId("authoring-clean")).toBeVisible();

    // Environment findings are legitimate here: a machine with no WebGPU adapter
    // says so. Authoring findings are not, and the console carries both, so the
    // console assertion is scoped to the codes the layout owns.
    const authored = problems.filter((line) =>
      AUTHORING_CODES.some((code) => line.includes(code)),
    );
    expect(authored).toEqual([]);
  });

  /*
   * §9 under the preference that stresses it hardest.
   *
   * Reduced transparency multiplies frost by 1.75, so σ becomes 14 and every
   * group's derived sampling padding becomes 42. That is what the placement law
   * has to survive, and it is the state in which the cross-group overlap check
   * used to over-report: a padded-box-against-padded-box test wanted 84px of
   * clearance between neighbouring groups, where the mechanism it names — one
   * proxy's box covering a neighbour's painted pixels — needs only 42
   * (`spikes/s1-proxy-topology/overlap-experiment/`, and the demo-shaped
   * reproduction in `@vitrea/platform-web`'s `e2e/shared/accessible-padding`).
   * The behaviour stage's three groups sit inside that difference.
   *
   * What this case can see depends on the machine, and that is worth stating:
   * the proxy path belongs to the WebGPU tier's dom sampling, so on a runner
   * with no adapter this page renders on the CSS tier, filters in place on each
   * host, and builds no proxies for the check to run over. There it is the
   * core-level rules — same-plane overlap, proxy proximity, variants,
   * merge distance — that are being asserted under the preference; on a machine
   * with an adapter it is the whole set.
   */
  test("the layout stays legal under reduced transparency too", async ({ page }) => {
    const problems: string[] = [];
    page.on("console", (message) => {
      if (message.text().includes("[vitrea:")) problems.push(message.text());
    });
    page.on("pageerror", (error) => problems.push(`pageerror: ${error.message}`));

    await gotoSite(page);
    await showSection(page, "access");
    await page.getByLabel("Reduced transparency").selectOption("true");

    // The preference really is resolved on — a clean findings list under a
    // preference that never took effect would be proving nothing.
    await expect(
      page.locator("#access .readout__row", { hasText: "Frost" }).locator("dd"),
    ).toHaveText("increased");

    // The behaviour stage is where the toolbar and the menu's group both mount,
    // and their gap is the geometry the finding was about.
    await showSection(page, "behavior");
    await showSection(page, "material");

    await expect(page.getByTestId("authoring-findings")).toHaveCount(0);
    await expect(page.getByTestId("authoring-clean")).toBeVisible();

    const authored = problems.filter((line) =>
      AUTHORING_CODES.some((code) => line.includes(code)),
    );
    expect(authored).toEqual([]);
  });

  /*
   * The collapsed breakpoint is where §9 is easiest to break, and it broke twice
   * while this page was being built: once because the group gap shrank with the
   * breakpoint and fell under the 48px two sampling paddings need, and once because
   * the behaviour stage's three groups did not fit the band at all.
   */
  for (const size of [
    { width: 375, height: 812, label: "a phone" },
    { width: 320, height: 640, label: "the reflow floor" },
  ]) {
    test(`the behaviour stage still fits its three groups at ${size.label}`, async ({ page }) => {
      await page.setViewportSize({ width: size.width, height: size.height });
      await gotoSite(page);
      await showSection(page, "behavior");

      await expect(page.getByTestId("authoring-findings")).toHaveCount(0);

      // And every control is inside the band rather than clipped out of it.
      const stage = await page.locator(".stage").first().boundingBox();
      if (stage === null) throw new Error("the stage has no box");
      const hosts = await page.evaluate(() =>
        [...document.querySelectorAll("[data-vitrea-node]")].map((host) => {
          const rect = host.getBoundingClientRect();
          return { bottom: rect.bottom, right: rect.right };
        }),
      );
      expect(hosts.length).toBeGreaterThan(0);
      for (const host of hosts) {
        expect(host.bottom).toBeLessThanOrEqual(stage.y + stage.height + 1);
        expect(host.right).toBeLessThanOrEqual(stage.x + stage.width + 1);
      }
    });
  }

  test("all glass lives in the plane's host layer, and the page has one plane pair", async ({
    page,
  }) => {
    await gotoSite(page);
    await showSection(page, "behavior");

    // Two managed planes, two canvases each: X1's base and overlay, and no more.
    await expect(page.locator("[data-vitrea-root] canvas")).toHaveCount(4);

    const misplaced = await page.evaluate(() =>
      [...document.querySelectorAll("[data-vitrea-node]")]
        .filter((host) => {
          const plane = host.getAttribute("data-vitrea-host-plane");
          const layer = host.closest('[data-vitrea-layer="semantic-host"]');
          return layer === null || layer.getAttribute("data-vitrea-plane") !== plane;
        })
        .map((host) => host.getAttribute("data-vitrea-node")),
    );
    expect(misplaced).toEqual([]);
  });
});

test.describe("the reference pair is a comparison", () => {
  test("both sides load, and the native capture is a real image", async ({ page }) => {
    await gotoSite(page);
    await showSection(page, "reference");

    const rasters = page.locator(".pair img.pair__raster");
    await expect(rasters).toHaveCount(2);
    for (const raster of await rasters.all()) {
      const size = await raster.evaluate((element: HTMLImageElement) => ({
        natural: element.naturalWidth,
        complete: element.complete,
      }));
      expect(size.complete).toBe(true);
      expect(size.natural).toBe(CANVAS.width);
    }
  });

  test("the live surface lands where scenes.json puts it", async ({ page }) => {
    await gotoSite(page);
    await showSection(page, "reference");

    const frame = await page.locator(".pair img.pair__raster").first().boundingBox();
    const surface = await page.getByTestId("scene-surface").boundingBox();
    if (frame === null || surface === null) throw new Error("the pair has no box");

    // Centred in the canvas, which is the placement rule the native harness and the
    // calibration page both apply. Not "roughly aligned": the same integers.
    expect(Math.round(surface.width)).toBe(CAPSULE.width);
    expect(Math.round(surface.height)).toBe(CAPSULE.height);
    expect(Math.round(surface.x - frame.x)).toBe((CANVAS.width - CAPSULE.width) / 2);
    expect(Math.round(surface.y - frame.y)).toBe((CANVAS.height - CAPSULE.height) / 2);
  });

  /*
   * Decision Log #31(b): the pair's figures were coming from the wrong cell.
   *
   * A scene now carries up to four cells (two colour schemes x two tiers) and the
   * page shows one. It was showing whichever sorted first in the matrix, which is
   * the *dark dom* cell — "…-dark-standard" sorts before "…-light-standard" — so
   * the headline figure on the public page belonged to a profile no visitor is
   * running and a tier that measures the engine's `backdrop-filter` rather than
   * vitrea's shader math. `calibration.ts` now names the primary explicitly.
   *
   * Asserted over every scene the picker offers rather than over the opening one,
   * because the drift was invisible on nineteen of the twenty and the arbitrary
   * one is not a fixture worth trusting.
   */
  test("every scene's figures come from the primary cell", async ({ page }) => {
    await gotoSite(page);
    await showSection(page, "reference");

    const picker = page.getByLabel("Scene");
    const scenes = await picker.locator("option").evaluateAll((options) =>
      options.map((option) => (option as HTMLOptionElement).value),
    );
    expect(scenes.length).toBeGreaterThan(1);

    // The scene the pair opens on carries every axis, so it is where the figure
    // list itself is checked.
    await expect(page.locator(".readout--figures")).toContainText("Silhouette IoU");

    for (const scene of scenes) {
      await picker.selectOption(scene);
      const figures = page.locator(".readout--figures");
      // Not every scene measures every axis — over a flat backdrop of its own tone
      // the reference is within 0.02 linear luminance of it, so those scenes have no
      // silhouette and no shape row. An axis reported absent is a result; what must
      // never vary is *whose* cell the figures are.
      await expect(figures.locator(".readout__row"), scene).not.toHaveCount(1);
      await expect(figures, scene).toContainText("apple-macos-26.5-1x-light-standard");
      await expect(figures, scene).toContainText("texture tier");
    }

    // And nothing borrows: the empty-slot branch is what a scene with no cell of
    // its own renders instead of a neighbour's number. Every scene the pair can
    // show is now measured, so the slot must be absent everywhere — which is a
    // statement about coverage, and it fails the moment a scene is added to
    // `scenes.json` without being measured.
    await expect(page.locator(".note--slot")).toHaveCount(0);
  });
});

test.describe("the accessibility floor", () => {
  test("axe is clean at rest", async ({ page }) => {
    await gotoSite(page);
    const results = await scan(page).analyze();
    expect(describeViolations(results.violations)).toEqual([]);
  });

  /*
   * The one exclusion, and it is architectural rather than convenient.
   *
   * A surface promoted to the overlay plane mid-morph lands in a layer no app
   * authored: `GlassMorph` portals its platter into vitrea's own plane DOM through a
   * `display: contents` mount node it owns, and neither the platter nor the menu
   * inside it takes a landmark role, so there is no element the page can reach to
   * wrap that content in one. `region` is a best-practice rule, every WCAG A and AA
   * rule stays on, and the at-rest scan above keeps `region` enabled, so the
   * exclusion covers exactly the state that cannot be authored. Closing it properly
   * needs a role seam on `GlassMorph`, which is a library change and is reported as
   * such rather than silently worked around here.
   */
  test("axe is clean with the live controls on stage and the menu open", async ({ page }) => {
    await gotoSite(page);
    await showSection(page, "behavior");

    const trigger = page.getByRole("button", { name: "Actions" });
    await trigger.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("menu")).toBeVisible();
    await page.waitForTimeout(700);

    const results = await scan(page).disableRules(["region"]).analyze();
    expect(describeViolations(results.violations)).toEqual([]);
  });

  test("the keyboard reaches the controls, moves within the toolbar, and works the menu", async ({
    page,
  }) => {
    await gotoSite(page);
    await showSection(page, "behavior");

    const share = page.getByRole("button", { name: "Share" });
    await share.focus();
    await expect(share).toBeFocused();

    await page.keyboard.press("ArrowRight");
    await expect(page.getByRole("button", { name: "Add to favorites" })).toBeFocused();
    // The disabled control is disabled to the platform: not a tab stop, not an
    // arrow stop. The next arrow leaves the toolbar's own roving order at its end.
    await expect(page.getByRole("button", { name: "Publish", disabled: true })).toBeDisabled();

    const trigger = page.getByRole("button", { name: "Actions" });
    await trigger.focus();
    await page.keyboard.press("Enter");
    await expect(page.getByRole("menuitem", { name: "Duplicate" })).toBeFocused();

    await page.keyboard.press("Escape");
    await expect(page.getByRole("menu")).toBeHidden();
    await expect(trigger).toBeFocused();
  });

  test("every section is reachable by its own link, and the stage follows", async ({ page }) => {
    await gotoSite(page);
    await page.getByRole("link", { name: "Behaviour" }).click();
    await expect(page.locator("#behavior")).toHaveAttribute("data-current", "");
    await expect(page.locator(".stage[data-mode='behavior']").first()).toBeVisible();
    await expect(page.getByRole("link", { name: "Behaviour" })).toHaveAttribute(
      "aria-current",
      "true",
    );
  });

  test("reduced motion is honoured on both sides", async ({ page }) => {
    await page.emulateMedia({ reducedMotion: "reduce" });
    await gotoSite(page);
    await showSection(page, "access");

    // The runtime's own half.
    const overshoot = await page
      .locator("#access .readout__row", { hasText: "Overshoot" })
      .locator("dd")
      .innerText();
    expect(overshoot.trim()).toBe("none");

    // The page's own half: every transition it owns collapses to 1ms.
    const duration = await page.evaluate(() =>
      getComputedStyle(document.documentElement).getPropertyValue("--duration-standard").trim(),
    );
    expect(duration).toBe("1ms");
  });

  test("forced colours removes the glass and the page's own decoration", async ({ page }) => {
    await page.emulateMedia({ forcedColors: "active" });
    await gotoSite(page);
    await showSection(page, "access");

    const glass = await page
      .locator("#access .readout__row", { hasText: "Glass" })
      .locator("dd")
      .innerText();
    expect(glass.trim()).toBe("none");

    const canvasShown = await page.evaluate(
      () =>
        getComputedStyle(document.querySelector(".stage__canvas") as Element).display !== "none",
    );
    expect(canvasShown).toBe(false);
  });

  test("content reflows at 320 CSS px with no horizontal scrolling", async ({ page }) => {
    await page.setViewportSize({ width: 320, height: 640 });
    await gotoSite(page);
    await showSection(page, "install");

    const overflow = await page.evaluate(() => ({
      documentScroll: document.documentElement.scrollWidth - document.documentElement.clientWidth,
      // A wide code block is allowed to scroll inside itself; the page is not.
      code: [...document.querySelectorAll(".code")].every(
        (element) => getComputedStyle(element).overflowX === "auto",
      ),
    }));
    expect(overflow.documentScroll).toBeLessThanOrEqual(1);
    expect(overflow.code).toBe(true);
  });
});
