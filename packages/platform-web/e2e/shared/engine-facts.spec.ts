import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

/**
 * What this machine's engines actually report, recorded as assertions.
 *
 * S1's layer-3 design says the conformance table "must be *generated* by this
 * spike's own harness in CI, not hand-maintained, or it will rot". The table is
 * committed data for now (C9 owns the release-time gate), so this spec is the
 * guard against rot in the meantime: if an engine's answers ever stop matching
 * the row the table hands it, this fails and names the field.
 *
 * It also pins the two things S1 measured about `CSS.supports` that are easy to
 * forget and dangerous to assume — that it is true where nothing renders, and
 * that it cannot see the reference-filter seam at all.
 */
test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

test("CSS.supports claims backdrop-filter in every engine, including the two S1 could not measure", async ({
  page,
}) => {
  const supports = await page.evaluate(() => ({
    unprefixed: CSS.supports("backdrop-filter", "blur(1px)"),
    prefixed: CSS.supports("-webkit-backdrop-filter", "blur(1px)"),
    referenceFilter: CSS.supports("backdrop-filter", "url(#x)"),
    referenceInList: CSS.supports("backdrop-filter", "blur(1px) url(#x)"),
  }));

  // At least one spelling is claimed everywhere — which is exactly why the gate
  // is necessary and not sufficient.
  expect(supports.unprefixed || supports.prefixed).toBe(true);

  // And `url()` is claimed in all three engines while only Chromium renders it
  // (WebKit bug 245510, Gecko bug 1887451). No probe can see that difference, so
  // the conformance table is the only place the fact can live.
  expect(supports.referenceFilter).toBe(true);
  expect(supports.referenceInList).toBe(true);
});

test("computed-style readback carries no capability information", async ({ page }) => {
  // "Engines drop what they cannot render" is simply false: Filter Effects 2
  // specifies `Computed value: as specified`. Only syntactically invalid
  // functions are dropped, identically everywhere. This probe avenue is closed.
  const readback = await page.evaluate(() => {
    const probe = document.createElement("div");
    document.body.append(probe);
    const read = (declaration: string) => {
      probe.style.removeProperty("backdrop-filter");
      probe.style.setProperty("backdrop-filter", declaration);
      return probe.style.getPropertyValue("backdrop-filter");
    };
    const result = {
      valid: read("blur(8px)"),
      unrenderableUrl: read("url(#nope)"),
      mixed: read("blur(8px) url(#nope)"),
      invalidFunction: read("blur(8px) bogusfn(3)"),
    };
    probe.remove();
    return result;
  });

  expect(readback.valid).toContain("blur");
  // Round-tripped unchanged, in every engine, although only one renders it.
  expect(readback.unrenderableUrl).toContain("url(");
  expect(readback.mixed).toContain("url(");
  // The one thing that *is* dropped is a parse error, which says nothing about
  // rendering capability.
  expect(readback.invalidFunction).toBe("");
});

test("the table's row for this engine matches what the engine reports", async ({ page }) => {
  const observed = await page.evaluate(async () => {
    await window.h.createRoot();
    const probe = window.h.platformProbe();
    return { probe, userAgent: navigator.userAgent };
  });

  const { probe, userAgent } = observed;

  // Detection agrees with the UA string, and a Chromium derivative is never read
  // as WebKit — every Chromium UA also carries `Safari/537.36`.
  if (/Firefox\//.test(userAgent)) expect(probe.engine).toBe("gecko");
  else if (/(?:Chrome|Chromium|HeadlessChrome)\//.test(userAgent)) expect(probe.engine).toBe("chromium");
  else expect(probe.engine).toBe("webkit");

  // Never the conservative row: an engine falling through to it here would mean
  // detection or the table's version ranges had drifted.
  expect(probe.reach).not.toBe("unsupported");
  expect(["yes", "unverified"]).toContain(probe.rasterises);
});

test("the WebGPU probe agrees with whatever this engine actually offers", async ({ page }) => {
  // Asserted as an agreement rather than as a hardcoded expectation, because the
  // three engines disagree here and the disagreement is environmental, not
  // architectural. On this machine, through Playwright and over the fixture's
  // http://localhost origin — a secure context, which matters: `navigator.gpu`
  // is absent on `about:blank`, so probing there reports a false negative —
  // WebKit returns a real adapter and device, while Chromium and Firefox expose
  // `navigator.gpu` and return no adapter at all.
  //
  // So this pins the invariant instead of the environment: whatever the engine
  // offers, the root's probe reports the same thing and the group's resolved
  // state follows from it honestly.
  const engineOffers = await page.evaluate(async () => {
    if (!("gpu" in navigator)) return { device: false };
    try {
      const adapter = await navigator.gpu.requestAdapter();
      if (adapter === null) return { device: false };
      await adapter.requestDevice();
      return { device: true };
    } catch {
      return { device: false };
    }
  });

  const root = await page.evaluate(async () => {
    // A vitrea-owned device: no stand-in, the real §GPU device ownership default.
    await window.h.createRoot({ renderer: "webgpu" });
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
    window.h.frame(3);
    return { status: window.h.webgpu(), state: window.h.capabilities("g") };
  });

  expect(root.status?.available).toBe(engineOffers.device);
  expect(root.status?.ownership).toBe("vitrea");

  if (engineOffers.device) {
    // A real device: the group samples the DOM through its proxy, and the GPU
    // tier is what the renderer will draw on.
    expect(root.state).toMatchObject({
      activeRenderer: "webgpu",
      samplingBackend: "css-backdrop",
      refraction: "approximate",
      health: "ok",
    });
  } else {
    // No adapter: the CSS tier, named honestly, with a recovery of "none" —
    // enabling support means a new session, not a retry.
    expect(root.state).toMatchObject({
      activeRenderer: "css",
      refraction: "none",
      health: "demoted",
      demotionReason: "no-webgpu",
    });
  }
});
