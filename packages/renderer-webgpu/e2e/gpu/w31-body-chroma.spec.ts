/**
 * W31 G3 — the body's chroma retention, drawn on a real adapter (claims §5.161
 * §5, §5.164).
 *
 * The unit case (`test/w31-body-chroma.test.ts`) proves the law as arithmetic
 * and asserts the shader's own text; the 34 goldens prove the OFF path is the
 * path the material has always taken. Neither can say the ON path exists.
 * `bodyChroma` is a new uniform vec4 at floats 132..135 and every word of it is
 * 0 on the landed material, which is the exact shape of the defect W30 G2 found
 * after every inertness proof was green over a misaligned vec4 (claims §5.158
 * §6): a lane nobody ever reads at a non-zero value is indistinguishable from a
 * lane wired to the wrong offset.
 *
 * So this opens it, on a backdrop that HAS a chromaticity to restore toward —
 * `w31-body-chroma`, a magenta-to-green gradient under one deep surface. Three
 * claims:
 *
 *  1. **ON draws differently from OFF.** A non-zero retention moves the bytes.
 *  2. **The luma is held.** The interior's mean linear luminance moves by less
 *     than one 8-bit code at every retention, which is the by-construction
 *     proof read off a raster instead of off doubles.
 *  3. **The chroma moves toward the backdrop's, and monotonically.** The
 *     interior's mean chroma rises with the retention, so the operator restores
 *     rather than merely perturbs.
 */

import { expect, test, type Page } from "@playwright/test";

import { decodeCapture, openHarness, requireHardwareAdapter } from "../support";

const SCENE = "w31-body-chroma";

type Capture = { readonly width: number; readonly height: number; readonly pixels: string };

const render = (
  page: Page,
  materialProfile: Record<string, unknown>,
  options?: Record<string, unknown>,
): Promise<Capture> =>
  page.evaluate(
    ([name, patch, opts]) =>
      window.vitrea.renderScene(
        name as string,
        undefined,
        patch as Record<string, unknown>,
        opts as Record<string, unknown> | undefined,
      ),
    [SCENE, materialProfile, options] as const,
  );

/**
 * A resolved material policy that lifts the occlusion and does nothing else.
 *
 * core's reduced-transparency row also increases the frost and caps the
 * refraction, and both of those move the raster on their own. This is the
 * occlusion axis alone, because the claim under test is about the lift and a
 * policy that moved three things at once could not say which one the bytes
 * came from.
 */
const OCCLUSION_LIFTED = {
  glass: "material",
  frost: "nominal",
  refraction: "nominal",
  occlusion: "increased",
  border: "nominal",
  ambientTint: "nominal",
  foreground: "adaptive",
} as const;

const bytes = (capture: Capture): number[] => [...decodeCapture(capture).data];

const maxDelta = (a: readonly number[], b: readonly number[]): number => {
  let worst = 0;
  for (let index = 0; index < a.length; index += 1) {
    worst = Math.max(worst, Math.abs((a[index] ?? 0) - (b[index] ?? 0)));
  }
  return worst;
};

/** sRGB decode, the renderer's own exponent-free piecewise form. */
const linear = (code: number): number => {
  const c = code / 255;
  return c <= 0.04045 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
};

/**
 * The interior's mean linear luminance and mean chroma, over the middle of the
 * surface only.
 *
 * A central window rather than the whole capture: the rim, the contour ramp and
 * the outer shadow are outside the operator's reach by construction, and a
 * reduction over the whole raster would dilute the body's movement with pixels
 * that cannot move. 120 × 72 CSS px centred on a 240 × 160 surface sits well
 * inside the contour at every radius the scene draws.
 */
const interior = (
  capture: Capture,
  raster: readonly number[],
): { readonly luma: number; readonly chroma: number } => {
  const { width, height } = capture;
  const x0 = Math.round(width / 2 - 60);
  const x1 = Math.round(width / 2 + 60);
  const y0 = Math.round(height / 2 - 36);
  const y1 = Math.round(height / 2 + 36);
  let luma = 0;
  let chroma = 0;
  let n = 0;
  for (let y = y0; y < y1; y += 1) {
    for (let x = x0; x < x1; x += 1) {
      const index = (y * width + x) * 4;
      const r = linear(raster[index] ?? 0);
      const g = linear(raster[index + 1] ?? 0);
      const b = linear(raster[index + 2] ?? 0);
      const Y = 0.2126 * r + 0.7152 * g + 0.0722 * b;
      luma += Y;
      // Chroma as the excursion from the neutral of the same luminance, in
      // linear light — the same quantity the retention scales, read without an
      // OKLab conversion the browser does not have.
      chroma += Math.hypot(r - Y, g - Y, b - Y);
      n += 1;
    }
  }
  return { luma: luma / n, chroma: chroma / n };
};

test.describe("@gpu W31's body chroma retention (claims §5.161 §5, §5.164)", () => {
  test("ON draws differently from OFF, and holds the luma while it does", async ({ page }) => {
    requireHardwareAdapter(await openHarness(page));

    const shipped = await render(page, {});
    const off = bytes(shipped);
    const base = interior(shipped, off);

    // The scene draws a chromatic body, so none of the comparisons below can
    // pass by comparing two neutral canvases.
    expect(base.chroma, "the scene's body has no chroma to restore").toBeGreaterThan(0.005);

    const readings: { retention: number; luma: number; chroma: number; delta: number }[] = [];
    for (const retention of [0.25, 0.5, 0.8, 1]) {
      const capture = await render(page, { bodyChromaRetention: retention });
      const raster = bytes(capture);
      const read = interior(capture, raster);
      readings.push({ retention, ...read, delta: maxDelta(off, raster) });
    }

    process.stdout.write(
      `body chroma retention: OFF luma ${base.luma.toFixed(6)} chroma ${base.chroma.toFixed(6)}; ` +
        readings
          .map(
            (r) =>
              `r=${String(r.retention)} luma ${r.luma.toFixed(6)} chroma ${r.chroma.toFixed(6)} ` +
              `Δbytes ${String(r.delta)}`,
          )
          .join("; ") +
        "\n",
    );

    // 1. The ON path exists.
    for (const reading of readings) {
      expect(
        reading.delta,
        `retention ${String(reading.retention)} changed nothing — the uniform is wired to ` +
          `nothing, or packed at the wrong offset`,
      ).toBeGreaterThan(1);
    }

    // 2. The luma is held. One 8-bit code at this body's level is about 0.0016
    // in linear light; the bound is that, and the measured movement is the
    // raster's own quantisation rather than the operator's.
    for (const reading of readings) {
      expect(
        Math.abs(reading.luma - base.luma),
        `retention ${String(reading.retention)} moved the interior's mean luminance — the ` +
          `operator is luma-preserving by construction and this is the raster saying so`,
      ).toBeLessThan(0.0016);
    }

    // 3. The chroma rises with the retention, monotonically, and ends well
    // above where it started. Without this the two above would be satisfied by
    // any luma-preserving perturbation at all.
    let previous = base.chroma;
    for (const reading of readings) {
      expect(reading.chroma, `retention ${String(reading.retention)}`).toBeGreaterThan(
        previous - 1e-6,
      );
      previous = reading.chroma;
    }
    expect(previous).toBeGreaterThan(base.chroma * 1.5);
  });

  test("is bit-identical at the shipped identity, named explicitly", async ({ page }) => {
    // The OFF half, stated on this scene rather than left to the goldens: an
    // explicit retention of 0 draws the same bytes as a material that never
    // names it, which is what `MATERIAL_IDENTITY_TABLE`'s plain value drop
    // asserts about the digest and this asserts about the pixels.
    requireHardwareAdapter(await openHarness(page));
    const shipped = bytes(await render(page, {}));
    const explicitZero = bytes(await render(page, { bodyChromaRetention: 0 }));
    expect(maxDelta(shipped, explicitZero)).toBe(0);
  });
  test("under an occlusion lift it acts on the plate's un-lifted share", async ({ page }) => {
    /*
     * W31 G3c — Decision Log 3 (d), on a hardware adapter (claims §5.164 §13).
     *
     * The leaf as G3 shipped it was applied unconditionally, so under Reduce
     * Transparency or Increase Contrast — the light document plus an occlusion
     * lift — it restored the nominal fraction of a chromaticity the preference
     * had just asked to have covered up, and the two accessibility beds read
     * `R` 3.04 and 2.95 against a reference of 1. The fix scales the retention
     * by the same `1 − lift` the backdrop's own surviving share is scaled by.
     *
     * Three readings, and they are three different claims. The unit case
     * (`test/w31-body-chroma.test.ts`) holds the arithmetic; none of it says
     * the fold reaches the uniform, which is what a lane packed on the CPU
     * needs a raster to say.
     */
    requireHardwareAdapter(await openHarness(page));

    // 1. The fold is keyed to the LIFT and not to the policy tag. At a lift of
    //    0 the occlusion fold is the identity on the optics as well — `α + 0·(1
    //    − α)` is `α` — so an increased-occlusion policy there must draw the
    //    nominal policy's bytes exactly, at a retention that is doing work.
    const nominalAt = bytes(await render(page, { bodyChromaRetention: 0.5 }));
    const unliftedAt = bytes(
      await render(
        page,
        { bodyChromaRetention: 0.5, increasedOcclusionLift: 0 },
        { accessibility: OCCLUSION_LIFTED },
      ),
    );
    expect(
      maxDelta(nominalAt, unliftedAt),
      "a lift of 0 must be the identity — the fold is reading the policy tag instead of the lift",
    ).toBe(0);

    // 2. Under the shipped lift of 0.75 the packed retention is a QUARTER of
    //    the document's, so the material's own 0.2 draws what the unconditional
    //    leaf would have drawn at 0.05, and asking for 0.8 reproduces what it
    //    drew at 0.2. Those two renders are the regression and its fix on one
    //    raster.
    const lifted = (bodyChromaRetention: number): Promise<Capture> =>
      render(page, { bodyChromaRetention }, { accessibility: OCCLUSION_LIFTED });

    const liftedOff = await lifted(0);
    const offRead = interior(liftedOff, bytes(liftedOff));
    const readings: { retention: number; chroma: number; delta: number }[] = [];
    for (const retention of [0.2, 0.8]) {
      const capture = await lifted(retention);
      const raster = bytes(capture);
      readings.push({
        retention,
        chroma: interior(capture, raster).chroma,
        delta: maxDelta(bytes(liftedOff), raster),
      });
    }
    const [low, high] = readings as [(typeof readings)[0], (typeof readings)[0]];

    process.stdout.write(
      `body chroma retention under an occlusion lift of 0.75: OFF chroma ` +
        `${offRead.chroma.toFixed(6)}; ` +
        readings
          .map(
            (r) =>
              `r=${String(r.retention)} (packed ${String(r.retention * 0.25)}) chroma ` +
              `${r.chroma.toFixed(6)} Δbytes ${String(r.delta)}`,
          )
          .join("; ") +
        "\n",
    );

    expect(low.delta, "the retention draws nothing at all under the lift").toBeGreaterThan(1);
    expect(low.chroma).toBeGreaterThan(offRead.chroma);
    expect(
      low.chroma,
      "the material's 0.2 must restore LESS than its 0.8 — the lift is not reaching the uniform",
    ).toBeLessThan(high.chroma);

    // 3. And the factor is exactly `1 − lift`, proven by byte-identity rather
    //    than by a ratio. The excursion is NOT linear in the packed retention
    //    on this scene — `gamut_at_luma` clips a magenta backdrop carried to a
    //    bright body's luma, so a ratio test would read the clamp — but the
    //    identity is exact: the lift enters the draw in exactly two places,
    //    `occlusionAlphaUnderPolicy` on the plate's alpha and this fold on the
    //    retention, so a nominal policy holding the LIFTED alpha and the packed
    //    retention must produce the same bytes. `α_eff = 0.46 + 0.75·0.54 =
    //    0.865` on the regular variant and `0.1 + 0.75·0.9 = 0.775` on the
    //    clear one; `0.15 / (1 − 0.75) = 0.6`.
    const packed = 0.15;
    const byAlpha = bytes(
      await render(page, {
        optics: { regular: { tintAlpha: 0.865 }, clear: { tintAlpha: 0.775 } },
        bodyChromaRetention: packed,
      }),
    );
    const byLift = bytes(await lifted(packed / 0.25));
    process.stdout.write(
      `the lift's two entries, separated: Δbytes ${String(maxDelta(byAlpha, byLift))}\n`,
    );
    expect(
      maxDelta(byAlpha, byLift),
      "the retention the lift packs is not `r · (1 − lift)` — the fold is scaling by " +
        "something else, or reaching something else",
    ).toBe(0);
  });
});
