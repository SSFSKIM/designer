import { expect, test, type Page } from "@playwright/test";

import { gotoHarness } from "../support";

/**
 * The media-query feed, end to end and on every engine.
 *
 * The unit suite covers the mapping from queries to preferences with a fake
 * matcher; what only a browser can show is that the *live* queries reach core's
 * resolver and come back out as material and motion regimes. `emulateMedia`
 * drives the real preference, so this is the same path a user's system setting
 * takes.
 */
test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

const policyFor = async (page: Page) =>
  page.evaluate(async () => {
    await window.h.createRoot();
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
    window.h.frame(2);
    const policy = window.h.requireRoot().accessibility;
    return {
      flags: {
        reducedMotion: policy.reducedMotion,
        increasedContrast: policy.increasedContrast,
        forcedColors: policy.forcedColors,
        reducedTransparency: policy.reducedTransparency,
      },
      material: { ...policy.material },
      motion: { ...policy.motion },
      codes: window.h.diagnosticCodes(),
    };
  });

test("reports the nominal policy when the system asks for nothing", async ({ page }) => {
  const policy = await policyFor(page);

  expect(policy.flags).toMatchObject({
    reducedMotion: false,
    increasedContrast: false,
    forcedColors: false,
  });
  expect(policy.material).toMatchObject({ glass: "material", refraction: "nominal" });
  expect(policy.motion).toMatchObject({ overshoot: "elastic", shimmer: "travel" });
});

test("carries prefers-reduced-motion through to the motion regime", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });
  const policy = await policyFor(page);

  expect(policy.flags.reducedMotion).toBe(true);
  // Removes overshoot, deformation and shimmer travel; keeps positional
  // continuity; shortens morphs to non-elastic interpolation.
  expect(policy.motion).toMatchObject({
    overshoot: "none",
    deformation: "none",
    shimmer: "none",
    morph: "non-elastic",
    crossfade: "large-plane-shifts",
    positionalContinuity: true,
  });
});

test("carries prefers-contrast through to borders and foreground", async ({ page }) => {
  await page.emulateMedia({ contrast: "more" });
  const policy = await policyFor(page);

  expect(policy.flags.increasedContrast).toBe(true);
  expect(policy.material).toMatchObject({
    border: "strong",
    foreground: "near-monochrome",
    ambientTint: "reduced",
  });
});

test("carries forced-colors through to system colors and no glass", async ({ page }) => {
  await page.emulateMedia({ forcedColors: "active" });
  const policy = await policyFor(page);

  expect(policy.flags.forcedColors).toBe(true);
  expect(policy.material).toMatchObject({
    glass: "none",
    colorSource: "system",
    refraction: "none",
    occlusion: "opaque",
    border: "strong",
  });
});

test("says whether prefers-reduced-transparency was answerable at all", async ({ page }) => {
  // Not Baseline, which is exactly why the GlassRoot override is load-bearing
  // rather than a courtesy. Where the engine cannot parse the query, `matches`
  // is false forever and reading that as "the user does not want it" would lose
  // the preference silently — so core raises its own diagnostic instead.
  const result = await page.evaluate(async () => {
    const queryable = window.matchMedia("(prefers-reduced-transparency: reduce)").media !== "not all";
    await window.h.createRoot();
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
    window.h.frame(2);
    return { queryable, codes: window.h.diagnosticCodes() };
  });

  if (result.queryable) {
    expect(result.codes).not.toContain("reduced-transparency-undetectable");
  } else {
    expect(result.codes).toContain("reduced-transparency-undetectable");
  }
});

test("lets a GlassRoot override outrank the system, in both directions", async ({ page }) => {
  await page.emulateMedia({ reducedMotion: "reduce" });

  const result = await page.evaluate(async () => {
    await window.h.createRoot();
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
    window.h.frame(2);
    const fromSystem = window.h.requireRoot().accessibility.motion.overshoot;

    // Overriding a *detected* preference off is the direction that has to work
    // for the explicit override to be worth anything.
    window.h.requireRoot().setAccessibilityOverrides({ reducedMotion: false });
    window.h.frame(2);
    const overriddenOff = window.h.requireRoot().accessibility.motion.overshoot;

    // And "system" hands it back.
    window.h.requireRoot().setAccessibilityOverrides({ reducedMotion: "system" });
    window.h.frame(2);
    const backToSystem = window.h.requireRoot().accessibility.motion.overshoot;

    // The other direction: asking for it where the system did not.
    window.h.requireRoot().setAccessibilityOverrides({ reducedTransparency: true });
    window.h.frame(2);
    const transparency = { ...window.h.requireRoot().accessibility.material };

    return { fromSystem, overriddenOff, backToSystem, transparency };
  });

  expect(result.fromSystem).toBe("none");
  expect(result.overriddenOff).toBe("elastic");
  expect(result.backToSystem).toBe("none");
  expect(result.transparency).toMatchObject({
    frost: "increased",
    refraction: "reduced",
    occlusion: "increased",
  });
});

test("cannot be talked out of forced-colors by an app", async ({ page }) => {
  // A forced-colors mandate comes from an OS accessibility setting whose whole
  // purpose is to override author styling, so it is not an app's to switch off.
  // core makes that unexpressible in the type; this is the runtime witness.
  await page.emulateMedia({ forcedColors: "active" });

  const glass = await page.evaluate(async () => {
    await window.h.createRoot();
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
    window.h.frame(2);
    window.h.requireRoot().setAccessibilityOverrides({
      reducedTransparency: false,
      increasedContrast: false,
      reducedMotion: false,
    });
    window.h.frame(2);
    return window.h.requireRoot().accessibility.material.glass;
  });

  expect(glass).toBe("none");
});
