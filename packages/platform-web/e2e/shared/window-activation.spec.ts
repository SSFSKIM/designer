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
      ? "b2b570e4adcea8fb9281aed4d2556598a1fc95b34ce4b12dd5a50157ac138306"
      : "874be66ea501621be265265424c16d2d98a01c40835d89c02de9473362c0d4dc");
    const inactive = hash(await page.evaluate(() => window.h.rendererMaterial()));
    process.stdout.write(`${scheme}: active ${active}; inactive ${inactive}\n`);
    expect(inactive).toBe(scheme === "light"
      ? "6dcb32c422639d0d49a4ad2927766f97817fb48c90c8987fbc09ec6a55a2b689"
      : "70391dee6d9990c22efc4b268caf9139886af9684a4255ded1128d3b7a2b7326");
    await page.evaluate(() => {
      window.h.requireRoot().setWindowActivation("active");
      window.h.frame(3);
    });
    expect(hash(await page.evaluate(() => window.h.rendererMaterial()))).toBe(active);
    expect((await reading(page)).pose).toBe("active");
  });
}
