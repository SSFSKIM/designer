/**
 * X7 at runtime: a CSS-tier session never reaches the renderer package.
 *
 * Three claims make up X7's lazy half, and they are checked in three different
 * places because no one place can see all of them:
 *
 *  - **The chunk boundary** — WGSL sits behind a dynamic import and lands in its
 *    own chunk. `@vitrea/core`'s `bundle-shape.test.ts` reads `dist/` and proves
 *    it on the built artifact, which is the only place a chunk exists.
 *  - **Nothing static reaches it** — the bridge imports core's seam and not the
 *    renderer, so treeshaking can drop the renderer from an entry chunk. Also a
 *    property of a build.
 *  - **The session never asks** — this file. The dev server hands out one module
 *    per URL, so the request log is a direct readout of what the page actually
 *    pulled down, and a `renderer-webgpu` URL in it means the runtime reached
 *    for the renderer whether or not a bundler would later have hidden that.
 *
 * The claim here is deliberately about the *renderer package*, not about the
 * string "wgsl": `@vitrea/geometry` exports the field shaders' source as string
 * constants, and its module is in the entry graph, so an unbundled dev server
 * serves it. That is a treeshaking question rather than a laziness one, and it
 * is answered in the built artifact — where those constants do not appear in the
 * entry chunk — not here, where no bundler has run.
 *
 * Two paths reach the CSS tier and both are checked, because they fail
 * differently. `renderer: "css"` never asks; the bridge is never constructed.
 * `renderer: "webgpu"` on a machine with no adapter asks and is told no, and the
 * temptation there is to have loaded the module anyway so `ready()` has
 * something to await — which would download the renderer on precisely the
 * machine that can never use it.
 *
 * All three engines, because this is a statement about a dependency graph rather
 * than about rendering: nothing here needs a pixel, so S1's capture blindness
 * does not reach it.
 */

import { expect, test, type Page } from "@playwright/test";

import { gotoHarness } from "../support";

/** Module URLs the dev server serves only if the runtime reached the renderer. */
const rendererRequests = (urls: readonly string[]): readonly string[] =>
  urls.filter((url) => url.includes("renderer-webgpu"));

const watchRequests = (page: Page): string[] => {
  const urls: string[] = [];
  page.on("request", (request) => urls.push(request.url()));
  return urls;
};

test("a css-tier root never fetches the renderer", async ({ page }) => {
  const urls = watchRequests(page);
  await gotoHarness(page);

  await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", left: 40, top: 40, width: 160, height: 60 });
    window.h.frame(3);
  });

  expect(rendererRequests(urls), "a CSS-tier session pulled renderer modules").toEqual([]);
});

test("a webgpu root fetches the renderer only if it got a device", async ({ page }) => {
  const urls = watchRequests(page);
  await gotoHarness(page);

  const hadDevice = await page.evaluate(async () => {
    await window.h.createRoot({ renderer: "webgpu" });
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", left: 40, top: 40, width: 160, height: 60 });
    window.h.frame(3);
    return window.h.webgpu()?.available === true;
  });

  // Engines differ on whether a device is had here at all — C5 measured this
  // machine's Playwright WebKit returning one where Chromium does not — so the
  // claim is checked against the engine's own answer rather than an assumed
  // environment. Both directions matter: downloading it without a device is the
  // waste X7 forbids, and not downloading it with one would mean no GPU tier.
  if (hadDevice) {
    expect(
      rendererRequests(urls).length,
      "a live device should have loaded the renderer",
    ).toBeGreaterThan(0);
  } else {
    expect(rendererRequests(urls), "no device, yet the renderer was fetched").toEqual([]);
  }
});
