import { createHash } from "node:crypto";
import { expect, test, type Page } from "@playwright/test";

import { gotoHarness } from "../support";

const hash = (value: unknown): string => {
  const sorted = (v: unknown): unknown => Array.isArray(v) ? v.map(sorted)
    : v !== null && typeof v === "object"
      ? Object.fromEntries(Object.entries(v).sort(([a], [b]) => a.localeCompare(b))
        .map(([key, entry]) => [key, sorted(entry)])) : v;
  return createHash("sha256").update(JSON.stringify(sorted(value))).digest("hex");
};

const reading = (page: Page) => page.evaluate(() => {
  window.h.frame(2);
  return { focus: document.hasFocus(), pose: window.h.requireRoot().windowActivation };
});

test.beforeEach(async ({ page }) => { await gotoHarness(page); });

/**
 * Headed second-page bringToFront left hasFocus() true on all three engines
 * (claims §5.147, activation-discovery.txt). Drive the platform feed explicitly;
 * this proves event wiring and precedence, not native window-manager delivery.
 */
const focusFeed = (page: Page, focused: boolean) => page.evaluate((value) => {
  Object.defineProperty(document, "hasFocus", { configurable: true, value: () => value });
  window.dispatchEvent(new Event(value ? "focus" : "blur"));
}, focused);

test("auto follows the focus/blur feed; either explicit endpoint wins and auto re-follows", async ({
  page, browserName,
}) => {
  await focusFeed(page, true);
  await page.evaluate(async () => { await window.h.createRoot({ windowActivation: "auto" }); });
  await expect.poll(() => reading(page)).toEqual({ focus: true, pose: "active" });
  await focusFeed(page, false);
  await expect.poll(() => reading(page)).toEqual({ focus: false, pose: "inactive" });
  await page.evaluate(() => window.h.requireRoot().setWindowActivation("active"));
  await expect.poll(() => reading(page)).toEqual({ focus: false, pose: "active" });
  await page.evaluate(() => window.h.requireRoot().setWindowActivation("auto"));
  await expect.poll(() => reading(page)).toEqual({ focus: false, pose: "inactive" });
  await focusFeed(page, true);
  await expect.poll(() => reading(page)).toEqual({ focus: true, pose: "active" });
  await page.evaluate(() => window.h.requireRoot().setWindowActivation("inactive"));
  await expect.poll(() => reading(page)).toEqual({ focus: true, pose: "inactive" });
  await page.evaluate(() => window.h.requireRoot().setWindowActivation("auto"));
  await expect.poll(() => reading(page)).toEqual({ focus: true, pose: "active" });
  process.stdout.write(`${browserName}: synthetic hasFocus feed + window focus/blur honoured\n`);
});

test("a visibility event or synthetic blur cannot invent document inactivity", async ({ page }) => {
  await page.bringToFront();
  await page.evaluate(async () => {
    await window.h.createRoot({ windowActivation: "auto" });
    window.dispatchEvent(new Event("blur"));
    document.dispatchEvent(new Event("visibilitychange"));
  });
  await expect.poll(() => reading(page)).toEqual({ focus: true, pose: "active" });
});

/*
 * **The four hashes moved to the macOS 27 documents at W29 G4, and what they are
 * is worth stating.** Each is the sha256 of the material the renderer is handed,
 * and its first sixteen hex digits are that profile document's own recorded
 * `resolvedMaterialSha256` — `e825cb034c9070e4` and `8439eb808495f5bf` for the
 * two active documents, `8dc63b265c1de038` and `3264b6cdde64bc8b` for the two
 * receded ones. So this case is not only "the pose reaches the renderer": it is
 * "the renderer is handed exactly the material the sealed document records, and
 * exactly the one the calibration bed was read at". The four literals here and
 * the four in `packages/calibration/profiles/apple-macos-27.0-*.json` are one
 * measurement, checked from the browser.
 */
for (const scheme of ["light", "dark"] as const) {
  test(`${scheme}: the renderer receives the sealed endpoint and restores the active document`, async ({
    page,
  }) => {
    await page.evaluate(async (colorScheme) => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true,
        colorScheme, windowActivation: "active" });
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
      window.h.frame(3);
    }, scheme);
    const active = hash(await page.evaluate(() => window.h.rendererMaterial()));
    await page.evaluate(() => {
      window.h.requireRoot().setWindowActivation("inactive");
      window.h.frame(3);
    });
    expect(active).toBe(scheme === "light"
      ? "e825cb034c9070e44cc1bdc99705faa826329bf7bb1fd10a7743a82ec52e155f"
      : "8439eb808495f5bf3803d37da6becb9f56cc8294f372cc957647c04a9de83c3c");
    const inactive = hash(await page.evaluate(() => window.h.rendererMaterial()));
    process.stdout.write(`${scheme}: active ${active}; inactive ${inactive}\n`);
    expect(inactive).toBe(scheme === "light"
      ? "8dc63b265c1de0384723c80b53a46efa2fddc483a769a91116c30fae9d2867ff"
      : "3264b6cdde64bc8b8d55f74538268ae30d80eb8d0361a12061ef0d0f2aec5196");
    await page.evaluate(() => {
      window.h.requireRoot().setWindowActivation("active");
      window.h.frame(3);
    });
    expect(hash(await page.evaluate(() => window.h.rendererMaterial()))).toBe(active);
    expect((await reading(page)).pose).toBe("active");
  });
}
