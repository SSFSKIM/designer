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
 * the digest that document's pin RESOLVES to — `3a2513742936ceb1` and
 * `f3008c3e9033ed4c` for the two macOS 27 active endpoints,
 * `d8015c2587126d08` and `8c85774d161fcbaa` for the two macOS 27 receded ones,
 * `b340a4dee871633c` and `93ab090705c43f1f` for the two macOS 26.5 active ones.
 *
 * A receded endpoint's digest is over the COMPOSITION — the receded difference
 * over the active patch of the same scheme over the renderer's default — because
 * that is the material a root hands the renderer when the window loses focus,
 * and this file is where that material is read back from a browser rather than
 * assembled by a script. (Corrected 2026-09-20, G2 review closure: the two
 * receded lines above read `91a22b7ad3473d51` and `1b40966487534d1c` on the
 * merge, digests over the recede alone, which the table below already
 * disagreed with; claims §5.158 §8, finding 1.)
 *
 * So a case here is not only "the pose reaches the renderer":
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
 *
 * **All eight moved at W30 G2, and no pixel did** (claims §5.158; W30 Decision
 * Log 1 (a) and 4 (a)). The wave added eight leaves to the renderer's
 * `DEFAULT_MATERIAL_PROFILE` for two operators — the span-graded shadow σ and
 * the scale-selective scatter — at values that are algebraic identities, and the
 * material the renderer is handed is exactly what these hashes are taken over.
 * So every one of them moves: the material gained eight keys. Nothing else did.
 * The prior eight are `e825cb03…`, `8439eb80…`, `8dc63b26…`, `3264b6cd…`,
 * `b2b570e4…`, `6dcb32c4…`, `874be66e…` and `70391dee…`, and they are recorded
 * here rather than deleted, as this file's own convention and the project's
 * require.
 *
 * The six documents' own `resolvedMaterialSha256` fields did NOT move: no
 * profile document's bytes were edited, because those bytes are an input to
 * every bound stated over that document's bed. What the pins resolve to lives in
 * `packages/calibration/profiles/digest-supersessions.json`, and the first
 * sixteen digits above are that record's `currentSha256`.
 *
 * **The four macOS 27 rows moved again at W30 G3, and this time a material did**
 * (claims §5.159; Decision Log 4 (b)). That child gives the eight leaves values —
 * a span-graded outer shadow σ with the six occlusion anchors refitted beside it,
 * and the scale gain on the dark document — re-seals the four macOS 27 documents
 * and reads the whole bed at those bytes in the same commit, which is the rule
 * Decision Log 4 (b) made after G2 measured what a re-seal without a read costs.
 * So those four documents carry their current digests in their own fields again
 * and their supersession records are retired; the two macOS 26.5 rows are
 * unchanged, and their records are permanent because their bytes can never move.
 * The four prior macOS 27 readings are `8d06a41cb70ba52f`, `73a3fb119a81312b`,
 * `035f537d9c27e3ed` and `4763b0d195fdb077`, kept here rather than deleted.
 */
const SEALED = {
  macos27: {
    light: {
      active: "3a2513742936ceb1c17a3149d75d21b79a627a7db373b03a909dbfbd18484bcc",
      inactive: "d8015c2587126d08f6db93315f8f249a2b2f0d19a84a0f525b966050eca7d00d",
    },
    dark: {
      active: "f3008c3e9033ed4cd3d55ec3a936af5ad3e91c0980f7af9a32f6b35bc843a76f",
      inactive: "8c85774d161fcbaae973003902e8e35090c92ba5bb568d500d0d59442f701917",
    },
  },
  macos26: {
    light: {
      active: "b340a4dee871633c89ee06e657a5cb55066724dc7cf1d3fcfd3b136e5c486d91",
      inactive: "07cf4a8b830cc14a8c6f27f639835df65efe9cd680186a3755d168b64d3025ce",
    },
    dark: {
      active: "93ab090705c43f1fd1b09a6899e55dbfb33d46598dc839714a73c911ce7c5b4a",
      inactive: "a52a5e2af4d5f7660a688249db8aa8bce9b6628ef3805f8da1cdddc3c5892097",
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
