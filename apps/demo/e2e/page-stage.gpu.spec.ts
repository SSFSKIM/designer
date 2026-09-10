/**
 * The page-content stage, on a real adapter (W27f G0).
 *
 * The chromium project renders this page on the CSS tier, because the headless
 * shell has no WebGPU adapter — so every assertion the site suite makes about this
 * stage is an assertion about the fallback. That is the wrong half of the claim.
 * The stage exists to show the WebGPU tier's unsampled path: a group whose backdrop
 * is ordinary DOM, which cannot be a texture, sampled through a masked proxy and
 * drawn over by the GPU. Only a run on a real device reaches it, and this project
 * (`channel: "chromium"`, Dawn on the hardware) is the one that does.
 *
 * Two things are checked there, and they are the two halves of "the path is
 * visible": that the runtime resolves and reports it, and that what it draws is
 * still legible under the labels the plates carry. The second is measured on the
 * rendered pixels through `glass-contrast.ts`, the same reading the CSS-tier suite
 * takes, because the GPU tier's material is a different material and a floor held
 * on one tier is not held on the other.
 *
 * It skips only where the machine genuinely has no adapter, and it says which. A
 * skip on a device that does have one would quietly retire the case, so the skip
 * reads the runtime's own demotion reason rather than a guess about the runner.
 */

import { expect, test, type Page } from "@playwright/test";

import { LARGE_FLOOR, worstNow } from "./glass-contrast";

async function gotoSite(page: Page): Promise<void> {
  await page.goto("/");
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
}

async function showPageStage(page: Page): Promise<void> {
  await page.evaluate(() => {
    document.getElementById("page")?.scrollIntoView({ block: "center", behavior: "instant" });
  });
  await expect(page.locator("#page")).toHaveAttribute("data-current", "");
  // The group registers, the proxy is built and the first optics pass lands; the
  // readout below is the runtime's, so waiting for it to say anything at all is
  // waiting for the stage rather than for a clock.
  await expect(row(page, "What the page declared")).toHaveText("dom");
}

const row = (page: Page, label: string) =>
  page.locator("#page .readout__row", { hasText: label }).locator("dd");

/**
 * Whether this machine reached the tier, in the runtime's own words, once the
 * question has actually been answered.
 *
 * The root brings WebGPU up asynchronously, and until the adapter replies a group
 * honestly reports the CSS tier with no fault named (`webgpu: "pending"` is not a
 * demotion). A single read taken in that window looks exactly like a machine with
 * no adapter, and the case it guards would skip itself on hardware that supports
 * it. So this waits for the state to settle into one of its two terminal answers:
 * the GPU is drawing, or the runtime has said `no-webgpu`.
 */
async function settledRenderer(page: Page): Promise<string> {
  let renderer = "";
  await expect
    .poll(async () => {
      renderer = (await row(page, "What is drawing").innerText()).trim();
      const reason = (await row(page, "Demotion reason").innerText()).trim();
      return renderer === "webgpu" || reason === "no-webgpu";
    })
    .toBe(true);
  return renderer;
}

test.describe("the page-content stage on the WebGPU tier", () => {
  test("the unsampled path resolves, and the runtime names every part of it", async ({ page }) => {
    await gotoSite(page);
    await showPageStage(page);

    const renderer = await settledRenderer(page);
    test.skip(
      renderer !== "webgpu",
      "no WebGPU adapter on this machine: the runtime reports no-webgpu",
    );

    // The whole state, not a sample of it. Each row is a separate decision the
    // resolver made, and the stage's claim is the conjunction: the GPU is drawing,
    // it could not take the backdrop as a texture, so it proxies the DOM and bends
    // nothing, and it has no declaration to adapt against because this stage writes
    // no hint — an adopter's first surface, exactly as the section says.
    await expect(row(page, "Where the backdrop comes from")).toHaveText("css-backdrop");
    await expect(row(page, "Refraction")).toHaveText("approximate");
    await expect(row(page, "Backdrop analysis")).toHaveText("none");

    // And it is not a fault. Choosing a DOM backdrop is a composition, so the group
    // is healthy with no reason named; a demoted row here would mean the machine
    // failed at something rather than that the page asked for this.
    await expect(row(page, "Health")).toHaveText("ok");
    await expect(row(page, "Demotion reason")).toHaveText("none");
  });

  test("the plates' labels hold the large-text floor on the material the GPU drew", async ({
    page,
  }) => {
    await gotoSite(page);
    await showPageStage(page);

    const renderer = await settledRenderer(page);
    test.skip(
      renderer !== "webgpu",
      "no WebGPU adapter on this machine: the runtime reports no-webgpu",
    );

    // Past the material's own transition, so the reading is the settled surface.
    await page.waitForTimeout(600);

    const worst = await worstNow(page, ".plate strong", "on the WebGPU tier over page content");
    test.info().annotations.push({
      type: "measurement",
      description: `worst label contrast ${worst.ratio.toFixed(2)}:1 (${worst.where})`,
    });
    expect(worst.ratio, `worst was ${worst.where}`).toBeGreaterThanOrEqual(LARGE_FLOOR);
  });
});
