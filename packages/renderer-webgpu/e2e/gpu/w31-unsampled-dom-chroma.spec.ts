/**
 * W31 G3c — what the retention restores TOWARD on the unsampled-DOM path
 * (review closure; claims §5.164 §10 and §13, finding N7).
 *
 * `body_chroma_retention` restores the colour's chromaticity toward the
 * BACKDROP's. On the unsampled-material path there is no sampled backdrop, so
 * the shader hands it `dom_material_backdrop()`, and that has two modes:
 *
 *  - **mode 1**, which a group with no declared `backdropTone` takes, returns
 *    `vec3f(ou.heavyTap.z)` — a fabricated NEUTRAL at the declared reference
 *    luminance. The mix target is then `backdrop · (Y / Y_backdrop)` =
 *    `vec3f(Y)`, the neutral at the colour's own luma.
 *  - **mode 2** returns `ou.toneColour.rgb`, the tone the page DECLARED, which
 *    can carry a chromaticity.
 *
 * The review read mode 1 and called it a desaturation. It is a desaturation in
 * FORM and the identity in effect, and this case is what says which: on that
 * path the plate is `solvedNeutral` and the fabricated backdrop is a grey, so
 * the composite the operator acts on has no chromaticity either. Both endpoints
 * of the mix coincide and the bytes do not move — at any retention, measured
 * below rather than argued.
 *
 * **What is left is a residual about the TARGET and not about a desaturation.**
 * On mode 2 the operator restores toward the tone the page stated, not toward
 * what is actually behind the surface, because on this path nothing sampled it.
 * A page whose declared tone is not its real backdrop gets a body carrying the
 * hue it was told about. That is measured here too, as the contrast that makes
 * mode 1's stillness a reading rather than a dead scene.
 *
 * §5.164 §1 declares the OTHER unsampled path — the plain layer path, where
 * `colour` is overwritten with `adapted` a few lines later and the retention is
 * silently the identity. This is not that one.
 */

import { expect, test, type Page } from "@playwright/test";

import type { Scene } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

/**
 * One deep surface over no backdrop at all, with an unsampled material and NO
 * `backdropTone` — which is what puts `dom_material_backdrop()` in mode 1.
 */
const SCENE: Scene = {
  name: "w31-unsampled-dom-chroma",
  widthCss: 240,
  heightCss: 160,
  devicePixelRatio: 1,
  backdrop: { kind: "none" },
  groups: [
    {
      groupId: "unsampled",
      refraction: "approximate",
      analysisExact: false,
      unsampledMaterial: { referenceBackdropLuminance: 0.2, minimumTintContrast: 1e-3 },
      surfaces: [
        {
          nodeId: "a",
          family: "fixed-rounded-rect",
          reference: "figma-smoothing",
          shape: {
            center: [120, 80],
            size: [160, 96],
            radii: [16, 16, 16, 16],
            smoothing: 0,
            thickness: 8,
          },
        },
      ],
    },
  ],
};

/**
 * The same group with a DECLARED tone, which is what puts
 * `dom_material_backdrop()` in mode 2 — and a chromatic one, so there is a
 * chromaticity for the operator to restore toward.
 */
const TONED: Scene = {
  ...SCENE,
  name: "w31-unsampled-dom-chroma-toned",
  groups: [
    {
      ...(SCENE.groups[0] as (typeof SCENE.groups)[0]),
      backdropTone: [0.36, 0.08, 0.2],
      backdropToneLevel: 0.2,
      backdropToneLinearLuminance: 0.14,
    },
  ],
};

const srgb = (code: number): number =>
  code <= 0.04045 * 255 ? code / 255 / 12.92 : ((code / 255 + 0.055) / 1.055) ** 2.4;

/**
 * The body's mean chroma over the interior, un-premultiplied.
 *
 * The readback on this path is a premultiplied LAYER — the browser would
 * composite it — so the alpha is divided out before the chroma is read;
 * otherwise a change in the solved alpha would read as a change in chroma.
 */
function interiorChroma(raster: Raster): { readonly chroma: number; readonly n: number } {
  let chroma = 0;
  let n = 0;
  for (let y = 62; y < 98; y += 1) {
    for (let x = 92; x < 148; x += 1) {
      const i = (y * raster.width + x) * 4;
      const a = (raster.data[i + 3] ?? 0) / 255;
      if (a < 0.2) continue;
      const r = srgb((raster.data[i] ?? 0) / a);
      const g = srgb((raster.data[i + 1] ?? 0) / a);
      const b = srgb((raster.data[i + 2] ?? 0) / a);
      const Y = 0.2126 * r + 0.7152 * g + 0.0722 * b;
      chroma += Math.hypot(r - Y, g - Y, b - Y);
      n += 1;
    }
  }
  return { chroma: n === 0 ? 0 : chroma / n, n };
}

const render = (page: Page, scene: Scene, patch: Record<string, unknown>): Promise<Raster> =>
  page
    .evaluate(
      ({ input, material }) =>
        window.vitrea.renderScene(input as never, undefined, material as never),
      { input: scene, material: patch },
    )
    .then(decodeCapture);

const bytes = (raster: Raster): number[] => [...raster.data];

const maxDelta = (a: readonly number[], b: readonly number[]): number => {
  let worst = 0;
  for (let i = 0; i < a.length; i += 1) worst = Math.max(worst, Math.abs((a[i] ?? 0) - (b[i] ?? 0)));
  return worst;
};

test.describe("@gpu W31's retention on the unsampled-DOM path (claims §5.164 §13, N7)", () => {
  test("mode 1 is the identity in EFFECT: the fabricated backdrop and the plate are both grey",
    async ({ page }) => {
      requireHardwareAdapter(await openHarness(page));

      const off = bytes(await render(page, SCENE, { bodyChromaRetention: 0 }));
      const readings: { retention: number; delta: number; chroma: number }[] = [];
      for (const retention of [0.282, 0.5, 1]) {
        const raster = await render(page, SCENE, { bodyChromaRetention: retention });
        const read = interiorChroma(raster);
        expect(read.n, "the interior window found no body to read").toBeGreaterThan(500);
        readings.push({ retention, delta: maxDelta(off, bytes(raster)), chroma: read.chroma });
      }
      process.stdout.write(
        "unsampled DOM, mode 1 (no declared tone): " +
          readings
            .map((r) => `r=${String(r.retention)} Δbytes ${String(r.delta)} ` +
              `chroma ${r.chroma.toFixed(8)}`)
            .join("; ") + "\n",
      );

      // The composite has no chromaticity to move, so `mix(colour, vec3f(Y), r)`
      // is `colour` for every `r`. Not "small": 0.
      for (const reading of readings) {
        expect(
          reading.delta,
          `retention ${String(reading.retention)} moved an unsampled-DOM group's layer — the ` +
            `mix target there is the neutral at the body's own luma and so is the body`,
        ).toBe(0);
        expect(reading.chroma).toBeLessThan(1e-4);
      }
    });

  test("mode 2 restores toward the DECLARED tone, which is the residual", async ({ page }) => {
    // The contrast that makes the stillness above a reading. With a tone
    // declared, `dom_material_backdrop()` hands back the tone's own colour, the
    // composite carries a chromaticity, and the operator restores toward it —
    // toward what the page SAID is behind the surface, since on this path
    // nothing sampled what actually is.
    requireHardwareAdapter(await openHarness(page));

    const off = await render(page, TONED, { bodyChromaRetention: 0 });
    const base = interiorChroma(off);
    expect(base.n, "the toned interior window found no body to read").toBeGreaterThan(500);

    const readings: { retention: number; delta: number; chroma: number }[] = [];
    for (const retention of [0.05, 0.282, 1]) {
      const raster = await render(page, TONED, { bodyChromaRetention: retention });
      readings.push({
        retention,
        delta: maxDelta(bytes(off), bytes(raster)),
        chroma: interiorChroma(raster).chroma,
      });
    }
    process.stdout.write(
      `unsampled DOM, mode 2 (declared tone): OFF chroma ${base.chroma.toFixed(6)}; ` +
        readings
          .map((r) => `r=${String(r.retention)} Δbytes ${String(r.delta)} ` +
            `chroma ${r.chroma.toFixed(6)}`)
          .join("; ") + "\n",
    );

    const [low, shipped, full] = readings as [
      (typeof readings)[0],
      (typeof readings)[0],
      (typeof readings)[0],
    ];
    // 1. It is not the identity here, which is what makes mode 1's zero above a
    //    reading about mode 1 and not about the scene.
    for (const reading of [low, shipped, full]) {
      expect(
        reading.delta,
        `retention ${String(reading.retention)} draws nothing at a declared chromatic tone`,
      ).toBeGreaterThan(1);
    }
    // 2. And at the shipped retention the body carries the declared tone's hue,
    //    several times over what it carried without the operator.
    expect(shipped.chroma).toBeGreaterThan(base.chroma * 2);
    expect(full.chroma).toBeGreaterThanOrEqual(shipped.chroma);
    /*
     * What is NOT asserted, and is printed instead: monotonicity in the
     * retention. The un-premultiplied layer's chroma FALLS at r = 0.05 before it
     * rises, because on this path the solved layer alpha moves with the
     * retention — `dom_material_alpha` clamps per channel inside a luma
     * computation, which claims §5.161 §11 carried forward as the reason this
     * branch is not luma-transparent. The composite the browser performs is what
     * a page sees and this raster is the premultiplied layer before it, so the
     * reading above the OFF value is the claim and the shape between is not.
     */
  });
});
