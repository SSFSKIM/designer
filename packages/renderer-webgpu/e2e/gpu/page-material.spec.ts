/**
 * The DOM shader is a per-pixel mirror of materialAtBackdrop, not a second fit.
 * A scalar backdrop makes every optical term identifiable: the DOM layer,
 * composited encoded, must reproduce the same-hint texture path at that level.
 * The separate calibration table retains sampled-today as the native error budget.
 */
import { expect, test } from "@playwright/test";
import { NOMINAL_ACCESSIBILITY_POLICY } from "../../../core/src/accessibility";

import { darkMaterialProfile } from "../../../platform-web/src/dark-profile";
import { materialAtBackdrop } from "../../../platform-web/src/optics";
import type { MaterialProfilePatch } from "../../src/material";
import type { Scene } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

const encode = (v: number): number => v <= 0.0031308 ? v * 12.92 : 1.055 * v ** (1 / 2.4) - 0.055;
const decode = (v: number): number => v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4;
const SEED = [1, 0.25, 0] as const;
const MEMBERS = [{ x: 90, y: 90, width: 120, span: 32 }, { x: 290, y: 120, width: 160, span: 96 }];

function scene(level: number, dom: boolean, tintStrength: number): Scene {
  return {
    name: "scalar-page-material", widthCss: 400, heightCss: 240, devicePixelRatio: 1,
    backdrop: dom ? { kind: "none" } : { kind: "gradient", from: [level, level, level], to: [level, level, level] },
    groups: [{
      groupId: "mixed-spans", refraction: dom ? "approximate" : "true", analysisExact: false,
      ...(dom ? { unsampledMaterial: { referenceBackdropLuminance: 0.02, minimumTintContrast: 1e-3 } }
        : { backdropSourceId: "bg" }),
      backdropTone: [level, level, level], backdropToneLevel: level, backdropToneLinearLuminance: level,
      surfaces: MEMBERS.map((m, i) => ({
        nodeId: `member-${i}`, family: "fixed-rounded-rect", reference: "figma-smoothing",
        shape: { center: [m.x, m.y], size: [m.width, m.span], radii: [12, 12, 12, 12], smoothing: 0, thickness: 8 },
        tint: { color: SEED, strength: tintStrength },
      })),
    }],
  };
}

/** Readback is premultiplied encoded; the browser performs this source-over. */
function over(raster: Raster, x: number, y: number, level: number): number[] {
  const i = (y * raster.width + x) * 4;
  const a = (raster.data[i + 3] ?? 0) / 255;
  return [0, 1, 2].map((c) => Math.min(255,
    (raster.data[i + c] ?? 0) + encode(level) * 255 * (1 - a)));
}

for (const [scheme, profile] of [["light", undefined], ["dark", darkMaterialProfile]] as const) {
  for (const encodedLevel of [0.1104, 0.2706, 0.9505]) {
    test(`@gpu ${scheme} DOM material matches its scalar law at ${encodedLevel}`, async ({ page }) => {
      requireHardwareAdapter(await openHarness(page));
      const level = decode(encodedLevel);
      for (const strength of [0, 0.5, 1]) {
        const render = async (dom: boolean): Promise<Raster> => decodeCapture(await page.evaluate(
          ({ input, patch }) => window.vitrea.renderScene(input, undefined, patch),
          { input: scene(level, dom, strength), patch: profile as MaterialProfilePatch | undefined },
        ));
        const dom = await render(true);
        const texture = await render(false);
        for (const member of MEMBERS) {
          const at = materialAtBackdrop(profile, "regular", {
            rgb: [level, level, level], luminance: level, linearLuminance: level,
          }, member.span, NOMINAL_ACCESSIBILITY_POLICY.material, 1, strength);
          const expected = SEED.map((seed) => 255 * (
            encode(at.level) * (1 - strength) + encode(seed * at.shade) * strength
          ));
          const actual = over(dom, member.x, member.y, level);
          for (let c = 0; c < 3; c++) {
            expect(Math.abs((actual[c] ?? 0) - (expected[c] ?? 0)),
              `${member.span}px centre, tint ${strength}, channel ${c}`).toBeLessThanOrEqual(1.5);
          }
        }
        // Include the rim, inner shadow and exterior shadow: matching just the
        // centre could conceal a layer whose light was still composited linearly.
        let maximum = 0;
        let worst = "";
        for (let y = 0; y < dom.height; y++) {
          for (let x = 0; x < dom.width; x++) {
            const a = over(dom, x, y, level);
            const b = over(texture, x, y, level);
            for (let c = 0; c < 3; c++) {
              const delta = Math.abs((a[c] ?? 0) - (b[c] ?? 0));
              if (delta > maximum) { maximum = delta; worst = `${x},${y},${c}: ${a[c]} / ${b[c]}`; }
            }
          }
        }
        expect(maximum, `all terms at tint ${strength}: ${worst}`).toBeLessThanOrEqual(2);
      }
    });
  }
}
