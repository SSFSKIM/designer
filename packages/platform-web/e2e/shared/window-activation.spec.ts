import { createHash } from "node:crypto";
import { expect, test, type Page } from "@playwright/test";

import { materialDigestInput } from "../../../renderer-webgpu/src/material";

import { gotoHarness } from "../support";

/**
 * The material the renderer is handed, hashed **under the digest rule** (W31
 * Decision Log 1 (a); claims §5.164).
 *
 * `materialDigestInput` drops every `MATERIAL_IDENTITY_TABLE` entry whose gates
 * hold their declared inert identities — the leaves that provably cannot reach
 * a pixel — so the first sixteen hex digits below are the digest each document
 * records, which is what this file's literals are for. Before W31 the hash was
 * over the whole handed material and the correspondence held only because the
 * fingerprint was the plain one; under the rule the two agree again, and a leaf
 * landing at its identity moves neither.
 */
const hash = (value: unknown): string => {
  const sorted = (v: unknown): unknown => Array.isArray(v) ? v.map(sorted)
    : v !== null && typeof v === "object"
      ? Object.fromEntries(Object.entries(v).sort(([a], [b]) => a.localeCompare(b))
        .map(([key, entry]) => [key, sorted(entry)])) : v;
  return createHash("sha256")
    .update(JSON.stringify(sorted(materialDigestInput(value))))
    .digest("hex");
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
 * of the material the renderer is handed, taken under the digest rule, and its
 * first sixteen hex digits are the digest that document RECORDS —
 * `62e684744954580b` and `c61194f820d77280` for the two macOS 27 active
 * endpoints, `183c8949f194ff43` and `1a64247df6786fc2` for the two macOS 27
 * receded ones, `b2b570e4adcea8fb` and `874be66ea501621b` for the two macOS
 * 26.5 active ones — the numbers those two frozen documents were sealed at in
 * the first place.
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
 * every bound stated over that document's bed. What the pins resolved to in that
 * interval lives in `packages/calibration/profiles/digest-supersessions.json`,
 * and the first sixteen digits then were that record's `currentSha256`.
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
 *
 * **All eight moved once more at W31 G3, and again no pixel did** (claims
 * §5.164; W31 Decision Log 1 (a)). The wave adds one leaf — the body's chroma
 * retention, at its inert identity 0 — and rules the digest rule that drops such
 * a leaf from the fingerprint, which is why the hash above is taken over
 * `materialDigestInput`. The four macOS 27 documents are re-sealed under the
 * rule in the same merge as the read at those bytes (X10), and the two macOS
 * 26.5 rows return to the frozen documents' OWN digests without a byte of them
 * being edited. The eight prior readings are `3a251374…`, `d8015c25…`,
 * `f3008c3e…`, `8c85774d…`, `b340a4de…`, `07cf4a8b…`, `93ab0907…` and
 * `a52a5e2a…`, kept here rather than deleted.
 *
 * **And the four macOS 27 rows moved a SECOND time in the same branch, because
 * this one a material really did.** The retention is fitted into the four
 * documents — 0.282 light active, 0.349 light receded, 0.336 dark active, 0.142
 * dark receded — and a leaf that leaves its declared identity reappears in the
 * digest, which is the rule's own other half. The readings between the two
 * moves, at the rule with the leaf still inert, are `62e68474…`, `183c8949…`,
 * `c61194f8…` and `1a64247d…`, kept here beside the rest.
 *
 * **Two of the eight went back to a number this file used to carry.** The two
 * macOS 26.5 INACTIVE readings under the rule are `6dcb32c4…` and `70391dee…`,
 * which are two of the pre-W30 eight listed above, to the last digit. Nothing
 * arranged that: the frozen material's receded composition is what it was before
 * W30's leaves existed, and dropping those leaves at their identities gives the
 * same bytes back. It is the rule's own claim — "the digest is over what draws"
 * — read from the browser.
 *
 * **The four macOS 27 rows moved a fourth time at W32 G1, and this time the
 * exterior did** (claims §5.168). The wave fits the outer shadow's outset per
 * colour scheme — `spreadPx` 3.10 → 0.50 on the light document and → 1.80 on the
 * dark one, the first time either leaf has been fitted on the macOS 27 bed —
 * re-solves the six occlusion anchors against the 3–48 CSS px window, moves the
 * dark document's σ slope inside B1, and **stands the two receded documents'
 * amplitude down to 0**, because Apple's receded window removes no light at all
 * from 3 CSS px outward (W32 Decision Log 2). So the two INACTIVE readings here
 * are now a material that draws no outer shadow, and on the CSS tier the
 * shadow fades OUT on deactivation, which is what the reference does —
 * `css-tier.ts` declares a transition on `box-shadow` on the element carrying
 * it. On the WebGPU tier it does not: `root.ts` swaps the posed profile the
 * instant the resolved activation changes and `receded-profile.ts` says the two
 * endpoints are fixed rather than interpolated, so the shadow disappears in one
 * frame. *(Corrected 2026-09-21, W32 G1 review closure; claims §5.168 §10,
 * finding N-12: this comment said "the crossfade this spec exercises fades the
 * shadow OUT on deactivation" without the tier. The digests below are
 * unaffected — a discrete swap and an interpolated one seal the same bytes.)*
 * The four readings before this move are `3dc24a74…`, `ab3ed65a…`,
 * `8a43f541…` and `e1f42c56…`, kept here rather than deleted; the four macOS
 * 26.5 readings are untouched, because a frozen document's bytes cannot move.
 */
const SEALED = {
  macos27: {
    light: {
      active: "40a6dec2dc34c748fe800d41c6707978aafcc74f06de566a9dd1706b6fb4ac08",
      inactive: "f34dcc03e2774db385d233458fb9d62f38beffa52ffba4c800aad435ae676fc4",
    },
    dark: {
      active: "bd1814fac34f9b3054767ec4520fc092035122d3118e5092b9083030a477948b",
      inactive: "6b6237b7ae241638851192d165ddff03bdd40660ea805a3457f0211d11624831",
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
