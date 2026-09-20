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
 * **What these hashes are, and why there are eight of them.** Each is the sha256
 * of the material the renderer is handed, and its first sixteen hex digits are
 * the profile document's own recorded `resolvedMaterialSha256` where there is a
 * document — `e825cb034c9070e4` and `8439eb808495f5bf` for the two macOS 27
 * active endpoints, `8dc63b265c1de038` and `3264b6cdde64bc8b` for the two macOS
 * 27 receded ones, `b2b570e4adcea8fb` and `874be66ea501621b` for the two macOS
 * 26.5 active ones. So a case here is not only "the pose reaches the renderer":
 * it is "the renderer is handed exactly the material the sealed document
 * records, and exactly the one the calibration bed was read at". Those literals
 * and the ones in `packages/calibration/profiles/` are one measurement, checked
 * from the browser.
 *
 * **The macOS 26.5 row is the selection's own pin** (W29 G4 review closure). The
 * four values in it are the four this file carried before W29 G4 moved the
 * default, restored from the commit before the landing rather than re-derived.
 * The README, the CHANGELOG and the upgrade note all promise that selecting
 * `macos26MaterialProfileDocument` keeps exactly what 0.18.0 drew, and the
 * complete statement of "what 0.18.0 drew" is the material the renderer was
 * handed then: these are those bytes. The two macOS 26.5 RECEDED endpoints have
 * no digest anywhere else in the repository — they were fitted straight into
 * `receded-profile.ts` in W27c and W28 G1 and have no profile document on disk —
 * so this is their only pin, which is why the loop is over both poses of both
 * documents rather than over the default alone.
 */
const SEALED = {
  macos27: {
    light: {
      active: "e825cb034c9070e44cc1bdc99705faa826329bf7bb1fd10a7743a82ec52e155f",
      inactive: "8dc63b265c1de0384723c80b53a46efa2fddc483a769a91116c30fae9d2867ff",
    },
    dark: {
      active: "8439eb808495f5bf3803d37da6becb9f56cc8294f372cc957647c04a9de83c3c",
      inactive: "3264b6cdde64bc8b8d55f74538268ae30d80eb8d0361a12061ef0d0f2aec5196",
    },
  },
  macos26: {
    light: {
      active: "b2b570e4adcea8fb9281aed4d2556598a1fc95b34ce4b12dd5a50157ac138306",
      inactive: "6dcb32c422639d0d49a4ad2927766f97817fb48c90c8987fbc09ec6a55a2b689",
    },
    dark: {
      active: "874be66ea501621be265265424c16d2d98a01c40835d89c02de9473362c0d4dc",
      inactive: "70391dee6d9990c22efc4b268caf9139886af9684a4255ded1128d3b7a2b7326",
    },
  },
} as const;

for (const materialDocument of ["macos27", "macos26"] as const) {
  for (const scheme of ["light", "dark"] as const) {
    const sealed = SEALED[materialDocument][scheme];

    test(`${materialDocument} ${scheme}: the renderer receives the sealed endpoint and restores the active document`, async ({
      page,
    }) => {
      await page.evaluate(async ([colorScheme, document]) => {
        await window.h.createRoot({
          renderer: "webgpu", appDevice: true, windowActivation: "active",
          colorScheme: colorScheme as "light" | "dark",
          materialDocument: document as "macos26" | "macos27",
        });
        window.h.addGroup("g");
        window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
        window.h.frame(3);
      }, [scheme, materialDocument]);
      const active = hash(await page.evaluate(() => window.h.rendererMaterial()));
      await page.evaluate(() => {
        window.h.requireRoot().setWindowActivation("inactive");
        window.h.frame(3);
      });
      expect(active).toBe(sealed.active);
      const inactive = hash(await page.evaluate(() => window.h.rendererMaterial()));
      process.stdout.write(
        `${materialDocument} ${scheme}: active ${active}; inactive ${inactive}\n`,
      );
      expect(inactive).toBe(sealed.inactive);
      await page.evaluate(() => {
        window.h.requireRoot().setWindowActivation("active");
        window.h.frame(3);
      });
      expect(hash(await page.evaluate(() => window.h.rendererMaterial()))).toBe(active);
      expect((await reading(page)).pose).toBe("active");
      // And the two documents are four different materials, so this loop is
      // discriminating rather than four readings of one selection.
      expect(SEALED.macos26[scheme].active).not.toBe(SEALED.macos27[scheme].active);
      expect(SEALED.macos26[scheme].inactive).not.toBe(SEALED.macos27[scheme].inactive);
    });
  }
}
