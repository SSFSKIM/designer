/**
 * The tint-and-ink band, on a real adapter (W27e G2).
 *
 * The band's own suite is `packages/react`'s, and that suite pins the CSS tier by
 * construction: `gotoPlayground` asks for `?renderer=css` so that a channel read
 * off a host's computed style means the same thing on all three engines (S1). So
 * the half of the band's record that names the *GPU* tier — that the group the
 * page composed resolves to `webgpu · css-backdrop` where a device exists — has
 * no home there, and a reading taken once by hand is a claim rather than a check.
 * This project is the only one that can take it: the demo's `chromium-gpu` runs
 * the full Chromium binary with Dawn on the hardware, where the headless shell
 * hands back SwiftShader or nothing at all.
 *
 * What it asserts is the band's own readout, which is rendered from the resolved
 * `GlassGroupState` rather than from what the page asked for — so a pass says the
 * request was met and says which parts of it were met.
 *
 * It skips only where the machine genuinely has no adapter, and it says which. A
 * skip on a device that does have one would quietly retire the case, so the skip
 * reads the runtime's own demotion reason rather than a guess about the runner.
 */

import { expect, test, type Page } from "@playwright/test";

const GROUNDS = ["light", "dark"] as const;

const tier = (page: Page, ground: string) => page.getByTestId(`ink-tier-${ground}`);

/** The group a member was registered into, read the way the band's own suite reads it. */
const groupOf = (page: Page, testId: string): Promise<string | null | undefined> =>
  page
    .getByTestId(testId)
    .evaluate((host) => host.closest("[data-vitrea-group]")?.getAttribute("data-vitrea-group"));

/** One axis of one group's resolved state, as the readout panel prints it. */
const axis = (page: Page, group: string, name: string) =>
  page
    .locator(".state-table", { has: page.locator("caption", { hasText: group }) })
    .locator("tr", { hasText: name })
    .locator("td");

async function gotoPlayground(page: Page): Promise<void> {
  // No `?renderer=css`: the playground asks for the GPU tier by default, which is
  // the whole reason this case is here.
  await page.goto("/playground/");
  await page.waitForSelector("[data-vitrea-root]", { state: "attached" });
  // The band's groups have registered and answered something — "resolving" is the
  // readout before there is a state to read, so waiting for it to go is waiting
  // for the runtime rather than for a clock.
  for (const ground of GROUNDS) await expect(tier(page, ground)).not.toHaveText("resolving");
}

/**
 * Whether this machine reached the tier, in the runtime's own words, once the
 * question has actually been answered.
 *
 * The root brings WebGPU up asynchronously, and until the adapter replies a group
 * honestly reports the CSS tier with no fault named (`webgpu: "pending"` is not a
 * demotion). A single read taken in that window looks exactly like a machine with
 * no adapter, and the case it guards would skip itself on hardware that supports
 * it. So this waits for the state to settle into one of its two terminal answers:
 * the GPU is drawing, or the runtime has said `no-webgpu`. The band publishes no
 * demotion reason of its own — its readout is two axes wide — so the reason is
 * read from the panel, where the root's answer for every group in the page is.
 */
async function settledRenderer(page: Page): Promise<string> {
  let renderer = "";
  await expect
    .poll(async () => {
      renderer = (await tier(page, "light").innerText()).trim().split(" ")[0] ?? "";
      const reason = (await axis(page, "dom-region", "demotionReason").innerText()).trim();
      return renderer === "webgpu" || reason === "no-webgpu";
    })
    .toBe(true);
  return renderer;
}

test("the band's groups resolve on the WebGPU tier, and the readout names it", async ({ page }) => {
  await gotoPlayground(page);

  const renderer = await settledRenderer(page);
  test.skip(
    renderer !== "webgpu",
    "no WebGPU adapter on this machine: the runtime reports no-webgpu",
  );

  for (const ground of GROUNDS) {
    // Both axes, because the pair is the claim: the GPU is drawing this band, and
    // it is sampling the ground through a masked proxy rather than as a texture —
    // the band paints its grounds in ordinary DOM, and nothing registers one.
    await expect(tier(page, ground)).toHaveText("webgpu · css-backdrop");

    // And the composition is still the one the band declares on this tier: the
    // plate in the tinted group, `Publish` in the group a second seed has to step
    // out into.
    expect(await groupOf(page, `ink-plate-${ground}`)).toBe(`ink-${ground}`);
    expect(await groupOf(page, `ink-publish-${ground}`)).toBe(`ink-${ground}-action`);
  }
});
