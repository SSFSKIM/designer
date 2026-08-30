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
import { expect, test, type Locator, type Page } from "@playwright/test";
import { PNG } from "pngjs";

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

    for (const id of ["material", "tone", "reference", "behavior", "access", "tiers", "install"]) {
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
   * reproduction in `@vitreajs/vitrea-web`'s `e2e/shared/accessible-padding`).
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
    // and their gap is the geometry the finding was about. The tone stage is the
    // one whose material this preference moves furthest, since the fold lands on
    // the backdrop adaptation directly.
    await showSection(page, "behavior");
    await showSection(page, "tone");
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

  /*
   * The tint control, and the claim the page makes beside it.
   *
   * The page says a tint colours the material without making it more opaque, and
   * that it lands on one plate rather than on the group. Both are checkable from
   * the published tokens, which is better than a screenshot here: `--vitrea-tint`
   * and `--vitrea-occlusion` are what the runtime decided, so this asserts the
   * decision rather than a rendering of it.
   */
  test("the tint control colours one plate and leaves the material's opacity alone", async ({
    page,
  }) => {
    await gotoSite(page, "?renderer=css");
    await showSection(page, "material");

    const read = async (): Promise<{ tinted: string; plain: string; occlusion: string }> =>
      page.evaluate(() => {
        const styleOf = (id: string) =>
          document.querySelector<HTMLElement>(`[data-testid="${id}"]`)?.style;
        return {
          tinted: styleOf("tinted-plate")?.getPropertyValue("--vitrea-tint") ?? "",
          plain: styleOf("untinted-plate")?.getPropertyValue("--vitrea-tint") ?? "",
          occlusion: styleOf("tinted-plate")?.getPropertyValue("--vitrea-occlusion") ?? "",
        };
      });

    const before = await read();
    expect(before.tinted).toBe(before.plain);

    await page.getByTestId("tint-select").selectOption("orange");
    await expect.poll(async () => (await read()).tinted).not.toBe(before.tinted);

    const after = await read();
    // One plate takes the colour; its neighbour in the same group does not.
    expect(after.plain).toBe(before.plain);
    // And the occlusion stays within a rounding step of where it was: the tint is
    // a colour axis, and the tier conversion re-solves its alpha for the new
    // colour rather than the tint moving how much material there is.
    expect(Math.abs(Number(after.occlusion) - Number(before.occlusion))).toBeLessThan(0.1);
  });
});

/*
 * The size sweep is a comparison too, and its whole claim rests on the one thing
 * a screenshot cannot show: that the three plates differ ONLY in size. If a
 * future edit gave the big plate more authored thickness, the stage would still
 * look right and would have stopped demonstrating anything — which is exactly the
 * conflation this sweep replaced. So the control is asserted rather than trusted.
 *
 * The optical result deliberately is not asserted here. Whether the largest plate
 * lenses harder is a per-pixel property of the GPU tier, and this page renders on
 * the CSS tier on any runner without an adapter; the renderer's own unit tests
 * pin the law's shape and `packages/calibration` measures its magnitude against
 * the reference. What this case owns is the experiment's design.
 */
test.describe("the size sweep is a controlled comparison", () => {
  test("three plates, three sizes across the law's band, one authored thickness", async ({
    page,
  }) => {
    await gotoSite(page);
    await showSection(page, "material");

    // Scoped to the stage rather than to `#material`: the narrative column and
    // the instrument are siblings, and the section id names only the column.
    const plates = page.locator(".stage--mirror[data-mode='material'] .plate--sweep");
    await expect(plates).toHaveCount(3);

    const boxes = await plates.evaluateAll((elements) =>
      elements.map((element) => {
        const rect = element.getBoundingClientRect();
        return {
          span: Math.round(Math.min(rect.width, rect.height)),
          thickness: element.getAttribute("data-sweep-thickness"),
        };
      }),
    );

    // Descending in the DOM, and genuinely separated: a sweep whose steps are
    // within a few px of each other is not a sweep.
    const spans = boxes.map((box) => box.span);
    expect(spans).toEqual([...spans].sort((a, b) => b - a));
    expect(spans[0] as number).toBeGreaterThan((spans[2] as number) * 2);

    // The control. Every plate carries the same thickness, whatever that value is
    // — this asserts they agree, not what they agree on.
    const thicknesses = new Set(boxes.map((box) => box.thickness));
    expect(thicknesses.size).toBe(1);
  });
});

/*
 * Backdrop tone adaptation (W7), pinned as the demonstration the page claims.
 *
 * Three claims, and the page makes all three in prose beside the control: that the
 * material follows the ground *continuously* rather than switching, that the
 * follow is gated by size so the small surface converges on the backdrop while the
 * large one does not, and that the runtime — not the page — re-decides each
 * surface's ink against the material that surface ended up showing.
 *
 * Read from `--vitrea-tint` on the CSS tier, and the query string says so. That is
 * the tier's published decision rather than a rendering of it, which is the same
 * reason the tint case reads tokens: the GPU tier publishes only the foreground
 * pair (the body is the canvas's), and whether this runner has an adapter at all is
 * a property of the machine. The cross-tier bound is what makes one tier's answer
 * a statement about both, and `packages/calibration` is where that is enforced.
 */
test.describe("backdrop tone adaptation is on screen", () => {
  /** The backdrop, from the backdrop: one texel of the canvas the group samples. */
  const groundOf = (page: Page): Promise<readonly [number, number, number]> =>
    page.evaluate(() => {
      const canvas = document.querySelector<HTMLCanvasElement>(".stage__canvas");
      const context = canvas?.getContext("2d") ?? null;
      if (canvas === null || context === null) throw new Error("the stage has no canvas");
      // Off the graticule: its lines are drawn on a 32px grid starting at 32.
      const dpr = window.devicePixelRatio;
      const data = context.getImageData(Math.round(16 * dpr), Math.round(16 * dpr), 1, 1).data;
      return [data[0] ?? 0, data[1] ?? 0, data[2] ?? 0] as const;
    });

  const channel = (value: number): number => {
    const v = value / 255;
    return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  };

  const levelOf = (rgb: readonly [number, number, number]): number =>
    0.2126 * channel(rgb[0]) + 0.7152 * channel(rgb[1]) + 0.0722 * channel(rgb[2]);

  const tintOf = (page: Page, step: string): Promise<string> =>
    page
      .getByTestId(`tone-plate-${step}`)
      .evaluate((element) => (element as HTMLElement).style.getPropertyValue("--vitrea-tint"));

  /**
   * What a published material is actually showing: composited over the backdrop
   * underneath it, in the encoded space the browser composites in.
   *
   * The tint alone would not answer the question. A fully adapted surface reaches
   * its backdrop as a *pair* — the colour moves and the alpha goes to 1 together,
   * because that is the only pair whose interior composite converges — so a test
   * that watched either one on its own would be watching half of the mechanism.
   */
  const bodyOf = (tint: string, ground: readonly [number, number, number]): number => {
    const parts = (tint.match(/[\d.]+/g) ?? []).map(Number);
    const [r = 0, g = 0, b = 0, alpha = 1] = parts;
    const over = (index: 0 | 1 | 2, colour: number): number =>
      alpha * colour + (1 - alpha) * (ground[index] ?? 0);
    return levelOf([over(0, r), over(1, g), over(2, b)]);
  };

  const bodyAt = async (
    page: Page,
    step: string,
    ground: readonly [number, number, number],
  ): Promise<number> => bodyOf(await tintOf(page, step), ground);

  /**
   * The plate as it is actually drawn — median pixel, so the label's glyphs (a few
   * per cent of the area) cannot move it.
   *
   * The arithmetic above reads the tier's published decision, which is the right
   * subject for the size gate and the ordering. This one reads pixels, because one
   * claim is about the composite rather than the decision: a fully adapted surface
   * is byte-identical to its own background, rim included, and no token says that.
   */
  const renderedOf = async (target: Locator): Promise<readonly [number, number, number]> => {
    const png = PNG.sync.read(await target.screenshot());
    const pixels: { readonly rgb: readonly [number, number, number]; readonly y: number }[] = [];
    for (let i = 0; i < png.data.length; i += 4) {
      if ((png.data[i + 3] ?? 0) < 200) continue;
      const rgb = [png.data[i] ?? 0, png.data[i + 1] ?? 0, png.data[i + 2] ?? 0] as const;
      pixels.push({ rgb, y: levelOf(rgb) });
    }
    pixels.sort((a, b) => a.y - b.y);
    return pixels[Math.floor(pixels.length / 2)]?.rgb ?? [0, 0, 0];
  };

  const setGround = async (page: Page, value: string): Promise<void> => {
    await page.getByTestId("ground-level").fill(value);
    // The material transitions; the readout does not, so it is the settled signal
    // that the control took rather than a timeout hoping it did.
    await expect(page.getByTestId("ground-level-readout")).toContainText(
      `${(Number(value) / 1000).toFixed(3)} linear`,
    );
    await page.waitForTimeout(400);
  };

  test("the plates track the ground control, and the small one converges where the large one does not", async ({
    page,
  }) => {
    await gotoSite(page, "?renderer=css");
    await showSection(page, "tone");

    // The top stop is `STAGE_HINT`'s own 0.16, which is past the curve's high edge.
    // Every plate is its unadapted self there, and that is the page's stated reason
    // the rest of the site looks untouched by this feature.
    await setGround(page, "160");
    const flatGround = await groundOf(page);
    const unadaptedTint = await tintOf(page, "c");
    expect(await tintOf(page, "a")).toBe(unadaptedTint);
    expect(await tintOf(page, "b")).toBe(unadaptedTint);
    const flatSmall = bodyOf(unadaptedTint, flatGround);

    // The bottom stop. The 40px plate reaches the backdrop; the 112px plate is
    // still a light glass body over the same pixels, in the same sampling group.
    await setGround(page, "2");
    const darkGround = await groundOf(page);
    const groundLevel = levelOf(darkGround);
    const dark = {
      a: await bodyAt(page, "a", darkGround),
      b: await bodyAt(page, "b", darkGround),
      c: await bodyAt(page, "c", darkGround),
    };
    /*
     * The counterfactual, and it is the only fair one: the SAME material the top
     * stop published, over the ground the bottom stop paints. A plate is darker
     * over a darker backdrop whether or not it adapts — the material is
     * translucent — so a comparison across two grounds would credit the axis with
     * the backdrop's own move.
     */
    const unadapted = bodyOf(unadaptedTint, darkGround);

    // Converged: not "darker", the backdrop's own level.
    expect(Math.abs(dark.a - groundLevel)).toBeLessThan(0.002);
    // Held: the largest plate is still nearer the material it started as than the
    // backdrop it is standing on, over the same pixels and in the same group.
    expect(unadapted - dark.c).toBeLessThan(dark.c - groundLevel);
    // And the gate is ordered by span, which is the whole claim of the sweep.
    expect(dark.a).toBeLessThan(dark.b);
    expect(dark.b).toBeLessThan(dark.c);

    /*
     * The same convergence on the pixels. A rounding step of tolerance, not zero:
     * the claim is that the surface reaches its background, and holding a demo to
     * an exact byte would make a one-step retune of the material read as a broken
     * page. The 112px plate is checked against the same ground so the tolerance is
     * doing work rather than being satisfied by everything.
     */
    const smallPixel = await renderedOf(page.getByTestId("tone-plate-a"));
    const largePixel = await renderedOf(page.getByTestId("tone-plate-c"));
    for (const index of [0, 1, 2] as const) {
      expect(Math.abs((smallPixel[index] ?? 0) - (darkGround[index] ?? 0))).toBeLessThanOrEqual(1);
      expect(Math.abs((largePixel[index] ?? 0) - (darkGround[index] ?? 0))).toBeGreaterThan(32);
    }

    /*
     * Continuity, which is the claim a two-state feature would also pass the
     * assertions above. Every intermediate stop lands strictly between the two
     * ends and never goes backwards, so what the reader drags through is a curve
     * rather than a switch with a transition painted on it.
     */
    let previous = dark.a;
    for (const value of ["20", "40", "60", "80", "100"]) {
      await setGround(page, value);
      const level = await bodyAt(page, "a", await groundOf(page));
      expect(level, `at ${value}`).toBeGreaterThan(previous);
      expect(level, `at ${value}`).toBeLessThan(flatSmall);
      previous = level;
    }

    // And the control is a control: the keyboard moves it like anything else.
    await page.getByTestId("ground-level").focus();
    await page.keyboard.press("Home");
    await expect(page.getByTestId("ground-level-readout")).toContainText("0.002 linear");
  });

  /*
   * The ink is the runtime's, per surface, and this is the assertion that says so.
   *
   * At the bottom stop the 40px plate's body has gone dark and the 112px plate's
   * has not, in one sampling group over one backdrop — so the two must be given
   * different foregrounds in the same frame. Nothing on this page chooses that;
   * the group states its backdrop level and the runtime resolves the rest.
   */
  test("the runtime gives the adapted plate a different ink from its unadapted neighbour", async ({
    page,
  }) => {
    await gotoSite(page, "?renderer=css");
    await showSection(page, "tone");

    const inkOf = (step: string): Promise<string> =>
      page
        .getByTestId(`tone-plate-${step}`)
        .evaluate((element) => (element as HTMLElement).style.getPropertyValue("--vitrea-foreground"));

    await setGround(page, "160");
    expect(await inkOf("a")).toBe(await inkOf("c"));

    await setGround(page, "2");
    expect(await inkOf("a")).not.toBe(await inkOf("c"));
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

/*
 * W8. The reference's active material casts an outer shadow across up to a third
 * of the canvas, and vitrea drew exactly none of it on either tier. The unit
 * tests hold the mechanism; what has to be true HERE is that it reaches the page
 * a reader actually looks at, and that it is the multiplicative occlusion the
 * reference measures rather than a grey layer that happens to resemble one.
 *
 * The tone stage is the controlled comparison, and it is the right one rather
 * than a convenient one: its ground is a single declared level a reader can
 * drag, and a multiplicative occlusion removes a FRACTION of the light behind
 * it — so the same shadow that is plainly there over the bright end of that
 * control has almost nothing left to remove at the dark end. Apple's own bed
 * shows exactly that: its `dark-solid` cells are byte-identical to their
 * background, shadow included.
 */
test.describe("the outer shadow is on screen", () => {
  const toLinear = (value: number): number => {
    const v = value / 255;
    return v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
  };
  const luminanceOf = (r: number, g: number, b: number): number =>
    0.2126 * toLinear(r) + 0.7152 * toLinear(g) + 0.0722 * toLinear(b);

  /** The median luminance of one rectangle of the page, in linear light. */
  const medianLuminance = async (
    page: Page,
    clip: { x: number; y: number; width: number; height: number },
  ): Promise<number> => {
    const png = PNG.sync.read(await page.screenshot({ clip }));
    const values: number[] = [];
    for (let i = 0; i < png.data.length; i += 4) {
      values.push(luminanceOf(png.data[i] ?? 0, png.data[i + 1] ?? 0, png.data[i + 2] ?? 0));
    }
    values.sort((a, b) => a - b);
    return values[Math.floor(values.length / 2)] ?? 0;
  };

  /**
   * The shadow just under a plate, and the same ground beside it — one row, one
   * paint, so the only thing that differs between the two readings is the shadow.
   *
   * The reference sits 60 CSS px past the plate's right edge, comfortably outside
   * the shadow's measured sideways reach of about 35, and the stage stacks its
   * plates in a column so nothing else is on that row.
   */
  const shadowUnder = async (
    page: Page,
    testId: string,
  ): Promise<{ readonly ground: number; readonly shadowed: number }> => {
    const box = await page.getByTestId(testId).boundingBox();
    if (box === null) throw new Error(`${testId} has no box`);
    const y = box.y + box.height + 3;
    const shadowed = await medianLuminance(page, {
      x: box.x + 20,
      y,
      width: Math.max(box.width - 40, 8),
      height: 6,
    });
    const ground = await medianLuminance(page, {
      x: box.x + box.width + 60,
      y,
      width: 40,
      height: 6,
    });
    return { ground, shadowed };
  };

  const setGroundLevel = async (page: Page, value: string): Promise<void> => {
    await page.getByTestId("ground-level").fill(value);
    await expect(page.getByTestId("ground-level-readout")).toContainText(
      `${(Number(value) / 1000).toFixed(3)} linear`,
    );
    await page.waitForTimeout(400);
  };

  test("every surface writes a real shadow: black, downward, blurred", async ({ page }) => {
    await gotoSite(page, "?renderer=css");
    await showSection(page, "material");

    for (const testId of ["untinted-plate", "tinted-plate"]) {
      const shadow = await page
        .getByTestId(testId)
        .evaluate((element) => getComputedStyle(element).boxShadow);

      // Pure black, and that is the mechanism rather than a palette choice: a
      // black layer composited source-over IS a multiply, and only a black one is.
      expect(shadow, testId).toMatch(/^rgba\(0, 0, 0, /);
      const lengths = (shadow.match(/-?[\d.]+px/g) ?? []).map((length) =>
        Number(length.slice(0, -2)),
      );
      const [offsetX = 0, offsetY = 0, blur = 0, spread = 0] = lengths;
      expect(offsetX, `${testId} offset-x`).toBe(0);
      expect(offsetY, `${testId} offset-y`).toBeGreaterThan(0);
      // The blur dominates the offset — the reference's shadow is a wide soft
      // field a little below the surface, not a hard drop.
      expect(blur, `${testId} blur`).toBeGreaterThan(2 * offsetY);
      expect(spread, `${testId} spread`).toBeGreaterThanOrEqual(0);
    }
  });

  test("it darkens a bright ground and has nothing to take from a dark one", async ({ page }) => {
    await gotoSite(page, "?renderer=css");
    await showSection(page, "tone");

    // The two ends of the stage's own control: its ground runs 0.002 to 0.160
    // linear, because the axis it was built for lives down there.
    await setGroundLevel(page, "160");
    const bright = await shadowUnder(page, "tone-plate-c");
    await setGroundLevel(page, "2");
    const dark = await shadowUnder(page, "tone-plate-c");

    // Over the bright end it is plainly there — a real fraction of the light
    // behind it, not a rounding difference.
    expect(bright.ground).toBeGreaterThan(0.05);
    expect((bright.ground - bright.shadowed) / bright.ground).toBeGreaterThan(0.03);

    /*
     * And at the dark end it is analytically absent. Stated in ABSOLUTE luminance
     * rather than as a fraction, because the fraction is what a multiplication
     * holds constant and the absolute darkening is what collapses with the light
     * available — which is the property being asserted.
     */
    expect(dark.ground - dark.shadowed).toBeLessThan((bright.ground - bright.shadowed) / 10);
  });

  test("it goes with the glass under forced colours", async ({ browser }) => {
    // Not a dimmer shadow — none. A surface that has become a flat system fill
    // has no elevation to cast one from, and a shadow that outlived the glass is
    // the composition the regime exists to prevent.
    const context = await browser.newContext({ forcedColors: "active" });
    const forced = await context.newPage();
    await gotoSite(forced, "?renderer=css");
    await showSection(forced, "material");
    await expect(forced.getByTestId("untinted-plate")).toHaveCSS("box-shadow", "none");
    await context.close();
  });
});
