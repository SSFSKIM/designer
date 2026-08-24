import { expect, test } from "@playwright/test";

import { gotoHarness } from "../support";

test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

/**
 * The probe battery. Every assertion here is engine-independent by
 * construction: none of it depends on `backdrop-filter` rendering, which is
 * exactly why S1 could measure this whole surface in all three engines while it
 * could measure no pixel at all in two of them.
 */
test.describe("probe layer 1 — the support gate", () => {
  test("passes, and answers under a spelling the engine actually accepts", async ({ page }) => {
    const probe = await page.evaluate(async () => {
      await window.h.createRoot();
      return window.h.platformProbe();
    });

    expect(probe.supported).toBe(true);
    expect((probe.properties as string[]).length).toBeGreaterThan(0);
    for (const property of probe.properties as string[]) {
      expect(["backdrop-filter", "-webkit-backdrop-filter"]).toContain(property);
    }
  });

  test("never reports itself as a conformance verdict", async ({ page }) => {
    // CSS.supports returns true in builds that render nothing, so the gate's
    // reach travels with it: the only "verified" reach comes from layer 3.
    const probe = await page.evaluate(async () => {
      await window.h.createRoot();
      return window.h.platformProbe();
    });

    expect(["verified", "structure-only"]).toContain(probe.reach);
    if (probe.rasterises !== "yes") expect(probe.reach).toBe("structure-only");
  });
});

test.describe("probe layer 3 — the engine conformance table", () => {
  test("recognises this engine and picks its row", async ({ page }) => {
    const probe = await page.evaluate(async () => {
      await window.h.createRoot();
      return window.h.platformProbe();
    });

    expect(["chromium", "gecko", "webkit"]).toContain(probe.engine);
    expect(Number(probe.version)).toBeGreaterThan(0);
    // The reserved displacement seam: only Chromium renders reference filters
    // inside backdrop-filter, and CSS.supports cannot tell the difference.
    expect(probe.referenceFilter).toBe(probe.engine === "chromium");
    expect(Number(probe.maxProxyArea)).toBeGreaterThan(0);
  });

  test("agrees with S1 about which engines were actually measured", async ({ page }) => {
    const probe = await page.evaluate(async () => {
      await window.h.createRoot();
      return window.h.platformProbe();
    });

    // Chromium was confirmed byte-exact; Gecko and WebKit are an open gate, not
    // a failure — capture blindness is not feature breakage.
    expect(probe.rasterises).toBe(probe.engine === "chromium" ? "yes" : "unverified");
  });
});

test.describe("probe layer 2 — the structural backdrop-root audit", () => {
  const RE_ROOTING = [
    ["opacity", "0.99"],
    ["filter", "blur(0px)"],
    ["filter", "grayscale(0)"],
    ["clip-path", "inset(0)"],
    ["mask-image", "linear-gradient(#000,#000)"],
    ["mix-blend-mode", "multiply"],
    ["will-change", "opacity"],
  ] as const;

  const HARMLESS = [
    ["filter", "none"],
    ["contain", "paint"],
    ["isolation", "isolate"],
    ["will-change", "transform"],
    ["transform", "translate3d(0,0,0)"],
  ] as const;

  test("passes a clean chain", async ({ page }) => {
    const verdict = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 200, top: 200, width: 140, height: 44 });
      window.h.frame(3);
      return window.h.probeVerdict("g");
    });

    expect(verdict).toBe("pass");
  });

  for (const [property, value] of RE_ROOTING) {
    test(`flags an ancestor with ${property}: ${value}`, async ({ page }) => {
      const result = await page.evaluate(
        async ([prop, val]) => {
          await window.h.createRoot({ renderer: "webgpu", appDevice: true });
          window.h.addGroup("g");
          window.h.addSurface({ groupId: "g", left: 200, top: 200, width: 140, height: 44 });
          window.h.frame(3);
          window.h.breakBackdropRoot(prop ?? "", val ?? "");
          await window.h.settle();
          window.h.frame(3);
          return {
            verdict: window.h.probeVerdict("g"),
            breaks: window.h.probeBreaks("g"),
            codes: window.h.diagnosticCodes(),
          };
        },
        [property, value] as const,
      );

      expect(result.verdict).toBe("fail");
      expect(result.breaks.length).toBeGreaterThan(0);
      expect(result.codes).toContain("backdrop-root-broken");
    });
  }

  for (const [property, value] of HARMLESS) {
    test(`does not flag ${property}: ${value}`, async ({ page }) => {
      // S1 measured all five harmless. The prototype over-triggered on `contain`
      // and `isolation`, which is what pinning the list to Filter Effects 2's
      // normative triggers fixes — and over-triggering demotes working groups.
      const verdict = await page.evaluate(
        async ([prop, val]) => {
          await window.h.createRoot({ renderer: "webgpu", appDevice: true });
          window.h.addGroup("g");
          window.h.addSurface({ groupId: "g", left: 200, top: 200, width: 140, height: 44 });
          window.h.frame(3);
          window.h.breakBackdropRoot(prop ?? "", val ?? "");
          await window.h.settle();
          window.h.frame(3);
          return window.h.probeVerdict("g");
        },
        [property, value] as const,
      );

      expect(verdict).toBe("pass");
    });
  }

  test("re-runs when application CSS changes, not only at startup", async ({ page }) => {
    // The audit's inputs are app CSS, which mutates at runtime — hover states,
    // animations, theme switches — so a startup-only probe under-detects.
    const timeline = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 200, top: 200, width: 140, height: 44 });
      window.h.frame(3);
      const atStartup = window.h.probeVerdict("g");

      window.h.breakBackdropRoot("opacity", "0.5");
      await window.h.settle();
      window.h.frame(3);
      const afterBreaking = window.h.probeVerdict("g");

      window.h.clearBackdropRoot("opacity");
      await window.h.settle();
      window.h.frame(3);
      const afterFixing = window.h.probeVerdict("g");

      return { atStartup, afterBreaking, afterFixing };
    });

    expect(timeline).toEqual({
      atStartup: "pass",
      afterBreaking: "fail",
      afterFixing: "pass",
    });
  });
});

test.describe("the probe-demotion path (X2)", () => {
  test("demotes a failing group to the CSS tier naming probe-failed, then recovers", async ({
    page,
  }) => {
    const states = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 200, top: 200, width: 140, height: 44 });
      window.h.frame(3);
      const healthy = window.h.capabilities("g");

      window.h.breakBackdropRoot("opacity", "0.5");
      await window.h.settle();
      window.h.frame(3);
      const demoted = window.h.capabilities("g");

      window.h.clearBackdropRoot("opacity");
      await window.h.settle();
      window.h.frame(3);
      const recovered = window.h.capabilities("g");

      return { healthy, demoted, recovered };
    });

    expect(states.healthy).toMatchObject({
      configuredSource: "dom",
      activeRenderer: "webgpu",
      samplingBackend: "css-backdrop",
      refraction: "approximate",
      health: "ok",
    });

    expect(states.demoted).toMatchObject({
      configuredSource: "dom",
      activeRenderer: "css",
      refraction: "none",
      health: "demoted",
      demotionReason: "probe-failed",
    });

    expect(states.recovered).toMatchObject({ health: "ok", activeRenderer: "webgpu" });
    expect(states.recovered?.demotionReason).toBeUndefined();
  });

  test("takes the failing group's proxy away and lets the CSS tier paint instead", async ({
    page,
  }) => {
    // probe-failed demotes *to the CSS tier* because the proxy path that failed
    // is not on the CSS tier's path: it filters in place on the host.
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 200,
        top: 200,
        width: 140,
        height: 44,
      });
      window.h.frame(3);
      const beforeProxy = window.h.proxyBox("g") !== undefined;
      const beforeHost = window.h.hostStyle(nodeId);

      window.h.breakBackdropRoot("opacity", "0.5");
      await window.h.settle();
      window.h.frame(3);

      return {
        beforeProxy,
        beforeHostFiltered: beforeHost?.backdropFilter,
        afterProxy: window.h.proxyBox("g") !== undefined,
        afterHost: window.h.hostStyle(nodeId),
      };
    });

    expect(result.beforeProxy).toBe(true);
    expect(result.beforeHostFiltered).toBe("none");
    expect(result.afterProxy).toBe(false);
    expect(result.afterHost?.backdropFilter).toContain("blur");
  });

  test("demotes one group without touching its neighbour", async ({ page }) => {
    // The audit is per group, not per document: different groups sit under
    // different ancestors. core's PlatformProbe is scene-wide, so this is the
    // property that would silently disappear if the per-group layer were lost.
    const states = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      const glassRoot = window.h.requireRoot();

      // "under" sits below an extra re-rooting wrapper inside the base plane;
      // "clear" sits directly in the host layer.
      const wrapper = document.createElement("div");
      wrapper.style.cssText = "position:absolute;inset:0;pointer-events:none";
      glassRoot.plane("base").hostLayer.append(wrapper);

      window.h.addGroup("clean");
      window.h.addGroup("broken");
      window.h.addSurface({ groupId: "clean", left: 100, top: 100, width: 120, height: 40 });
      window.h.addSurface({ groupId: "broken", left: 500, top: 400, width: 120, height: 40 });
      window.h.frame(3);

      // Re-root only the broken group's proxy, by styling its own proxy's parent.
      const proxy = document.querySelector<HTMLElement>('[data-vitrea-proxy="broken"]');
      const holder = document.createElement("div");
      holder.style.cssText = "position:absolute;inset:0;opacity:0.5";
      proxy?.parentElement?.append(holder);
      if (proxy !== null) holder.append(proxy);
      window.h.requireRoot().revalidateProbe();

      return { clean: window.h.capabilities("clean"), broken: window.h.capabilities("broken") };
    });

    expect(states.clean).toMatchObject({ health: "ok", activeRenderer: "webgpu" });
    expect(states.broken).toMatchObject({ health: "demoted", demotionReason: "probe-failed" });
  });
});

test.describe("the WebGPU lifecycle feeding core's capability inputs", () => {
  test("a CSS-tier root has no WebGPU in play and says so honestly, not as a fault", async ({
    page,
  }) => {
    // X2's K1 amendment (Decision Log #21c): a root that never requests
    // WebGPU is CSS by choice, not demoted — every default root would
    // otherwise read as faulted, which is the opposite of the honesty core.
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "css" });
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 120, height: 40 });
      window.h.frame(2);
      return { webgpu: window.h.webgpu(), state: window.h.capabilities("g") };
    });

    expect(result.webgpu).toBeUndefined();
    expect(result.state).toMatchObject({
      activeRenderer: "css",
      health: "ok",
      refraction: "none",
      samplingBackend: "css-backdrop",
    });
    expect(result.state?.demotionReason).toBeUndefined();
  });

  test("device loss demotes with device-lost and reports it", async ({ page }) => {
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 120, height: 40 });
      window.h.frame(2);
      const before = window.h.capabilities("g");

      window.h.loseDevice();
      await new Promise((resolve) => setTimeout(resolve, 0));
      window.h.frame(2);

      return {
        before,
        after: window.h.capabilities("g"),
        status: window.h.webgpu(),
        codes: window.h.diagnosticCodes(),
      };
    });

    expect(result.before).toMatchObject({ activeRenderer: "webgpu", health: "ok" });
    expect(result.after).toMatchObject({
      activeRenderer: "css",
      health: "demoted",
      demotionReason: "device-lost",
    });
    expect(result.status).toMatchObject({ deviceHealth: "lost", ownership: "app" });
    expect(result.codes).toContain("webgpu-device-lost");
  });

  test("plumbs both refraction caps and their resolved lower bound", async ({ page }) => {
    // Decision Log #19: renderers honour the lower of the accessibility cap and
    // the state's refraction level. Both travel to C6, not just the answer.
    const result = await page.evaluate(async () => {
      await window.h.createRoot({ renderer: "webgpu", appDevice: true });
      window.h.addGroup("g");
      const nodeId = window.h.addSurface({
        groupId: "g",
        left: 100,
        top: 100,
        width: 120,
        height: 40,
      });
      window.h.frame(2);
      const nominal = window.h.refractionFor(nodeId);

      window.h.requireRoot().setAccessibilityOverrides({ reducedTransparency: true });
      window.h.frame(2);

      return { nominal, reduced: window.h.refractionFor(nodeId) };
    });

    expect(result.nominal).toEqual({
      state: "approximate",
      accessibilityCap: "true",
      effective: "approximate",
    });
    expect(result.reduced).toEqual({
      state: "approximate",
      accessibilityCap: "approximate",
      effective: "approximate",
    });
  });
});
