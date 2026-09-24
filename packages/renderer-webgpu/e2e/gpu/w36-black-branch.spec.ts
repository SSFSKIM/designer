/** W36's new uniform must reach the pixels, while its old stand-downs remain (§5.179). */
import { expect, test } from "@playwright/test";
import { decodeCapture, openHarness, requireHardwareAdapter } from "../support";

test("@gpu W36 black branch identity, on-state and stand-downs", async ({ page }) => {
  requireHardwareAdapter(await openHarness(page));
  const draw = async (patch: Record<string, unknown>, scene = "w36-black",
    options?: Record<string, unknown>) => {
    const capture = await page.evaluate(([name, material, opts]) =>
      window.vitrea.renderScene(name, undefined, material, opts), [scene, patch, options] as const);
    return [...decodeCapture(capture).data];
  };
  const base = { backdropToneLow: 0, backdropToneHigh: 0.0001,
    backdropToneBlackThin: 0.2, backdropToneBlackThick: 0.2 };
  const off = await draw({ ...base, backdropToneBlackStrength: 0 });
  for (const value of [0, 0.7, 1]) {
    expect(await draw({ ...base, backdropToneBlackThin: value,
      backdropToneBlackThick: 1 - value, backdropToneBlackStrength: 0 })).toEqual(off);
  }
  const on = await draw({ ...base, backdropToneBlackStrength: 1 });
  expect(on).not.toEqual(off);
  // The central body has neither rim nor shadow. At Y=.2 its encoded code is124.
  expect(on[(50 * 160 + 80) * 4]).toBe(124);
  for (const disabled of [
    { backdropToneResponseStrength: 0 },
    { optics: { regular: { tintAlpha: 0 } }, sizeOcclusionGain: 0 },
    { backdropToneLow: 0.5, backdropToneHigh: 0.6, backdropToneSizeBias: 0 },
  ]) {
    expect(await draw({ ...base, ...disabled, backdropToneBlackStrength: 1 }))
      .toEqual(await draw({ ...base, ...disabled, backdropToneBlackStrength: 0 }));
  }
  expect(await draw({ ...base, backdropToneBlackStrength: 1 }, "w36-no-tone"))
    .toEqual(await draw({ ...base, backdropToneBlackStrength: 0 }, "w36-no-tone"));
  const policy = { accessibility: { glass: "material", frost: "nominal",
    refraction: "nominal", occlusion: "nominal", border: "nominal",
    ambientTint: "reduced", foreground: "adaptive" } };
  expect(await draw({ ...base, backdropToneBlackStrength: 1 }, "w36-black", policy))
    .toEqual(await draw({ ...base, backdropToneBlackStrength: 0 }, "w36-black", policy));
});
