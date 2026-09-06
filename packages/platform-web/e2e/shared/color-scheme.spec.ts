import { expect, test, type Page } from "@playwright/test";

import { gotoHarness } from "../support";

/**
 * The colour scheme in a real browser (W21 G3).
 *
 * The unit suite drives the resolution against a fake matcher; what only a
 * browser can show is that the LIVE `prefers-color-scheme` query reaches the
 * root and comes back out as a different resolved material — and that it does so
 * on both tiers, from the one option. `emulateMedia` drives the real preference,
 * so this is the path a user's system setting takes.
 *
 * The material is read off `renderInput()`, the frame's own resolution, because
 * that is what a renderer is handed on either tier. Whether the resulting pixels
 * differ is a Chromium-only question and belongs to `e2e/pixel/`; whether the
 * root resolved a different material is not, so this runs on all three engines.
 */
test.beforeEach(async ({ page }) => {
  await gotoHarness(page);
});

interface Reading {
  readonly scheme: string;
  readonly tintAlpha: number;
  readonly tint: readonly number[];
}

const readMaterial = async (
  page: Page,
  spec: { renderer: "css" | "webgpu"; colorScheme?: "light" | "dark" | "auto" },
): Promise<Reading> =>
  page.evaluate(async (rootSpec) => {
    await window.h.createRoot({
      renderer: rootSpec.renderer,
      appDevice: rootSpec.renderer === "webgpu",
      ...(rootSpec.colorScheme === undefined ? {} : { colorScheme: rootSpec.colorScheme }),
    });
    window.h.addGroup("g");
    window.h.addSurface({ groupId: "g", left: 100, top: 100, width: 140, height: 44 });
    window.h.frame(2);
    const root = window.h.requireRoot();
    const node = root.renderInput()?.planes.flatMap((plane) => plane.nodes)[0];
    if (node === undefined) throw new Error("the frame resolved no node");
    return {
      scheme: root.colorScheme,
      tintAlpha: node.optics.tintAlpha,
      tint: [...node.optics.tint],
    };
  }, spec);

test.describe("the scheme selects the material, on both tiers", () => {
  for (const renderer of ["css", "webgpu"] as const) {
    test(`${renderer} tier: dark resolves a different material from light`, async ({ page }) => {
      const light = await readMaterial(page, { renderer });
      const dark = await readMaterial(page, { renderer, colorScheme: "dark" });

      expect(light.scheme).toBe("light");
      expect(dark.scheme).toBe("dark");
      expect(dark.tintAlpha).not.toBeCloseTo(light.tintAlpha, 4);
      expect(dark.tint).not.toEqual(light.tint);
    });

    test(`${renderer} tier: auto follows prefers-color-scheme`, async ({ page }) => {
      await page.emulateMedia({ colorScheme: "dark" });
      const auto = await readMaterial(page, { renderer, colorScheme: "auto" });
      const declared = await readMaterial(page, { renderer, colorScheme: "dark" });

      expect(auto.scheme).toBe("dark");
      expect(auto.tintAlpha).toBeCloseTo(declared.tintAlpha, 6);
      expect(auto.tint).toEqual(declared.tint);
    });

    test(`${renderer} tier: the default stays light under a dark system`, async ({ page }) => {
      await page.emulateMedia({ colorScheme: "dark" });
      const defaulted = await readMaterial(page, { renderer });
      await page.emulateMedia({ colorScheme: "light" });
      const light = await readMaterial(page, { renderer });

      expect(defaulted.scheme).toBe("light");
      expect(defaulted.tintAlpha).toBeCloseTo(light.tintAlpha, 6);
    });
  }
});

test("a live flip re-derives the material without a reload", async ({ page }) => {
  await page.emulateMedia({ colorScheme: "light" });
  const before = await page.evaluate(async () => {
    await window.h.createRoot({ colorScheme: "auto" });
    window.h.addGroup("g");
    window.h.addSurface({
      groupId: "g",
      nodeId: "panel",
      left: 100,
      top: 100,
      width: 140,
      height: 44,
    });
    window.h.frame(2);
    const root = window.h.requireRoot();
    return { scheme: root.colorScheme, style: window.h.hostStyle("panel") };
  });

  await page.emulateMedia({ colorScheme: "dark" });
  const after = await page.evaluate(() => {
    window.h.frame(2);
    const root = window.h.requireRoot();
    return { scheme: root.colorScheme, style: window.h.hostStyle("panel") };
  });

  expect(before.scheme).toBe("light");
  expect(after.scheme).toBe("dark");
  // The CSS tier's own declarations moved with it: the material is re-derived on
  // the next frame, not at construction.
  expect(after.style).not.toEqual(before.style);
});
