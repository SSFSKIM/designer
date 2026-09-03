/**
 * The benchmark §Performance envelope pins the ~2 ms hypothesis to.
 *
 * > The GPU budget (~2ms/frame) is a **hypothesis to validate**, pinned to
 * > declared benchmark scenes — mobile: 390×844 CSS px @ DPR 3, one video
 * > backdrop, 8 surfaces, 3 groups, 1 active morph, 60Hz; plus a desktop 2×
 * > scene — measured per pass (backdrop import, blur, analysis, body, highlight,
 * > composite) alongside browser end-to-end frame time.
 *
 * Both scenes are exactly that: 8 surfaces across 3 groups (a 4-button toolbar, a
 * 3-segment control, and one platter mid-morph), over a backdrop that is dirty
 * every frame the way an imported video is.
 *
 * ## Methodology, because it changed the answer
 *
 * The configs are **interleaved** — every round draws one frame of each — rather
 * than run to completion in turn. Sequentially, the same config measured 0.995 ms
 * in the first slot and 1.901 ms in the last: a 1.9x spread on identical work,
 * from the GPU's clock state rather than from anything rendered. Interleaved, the
 * drift reaches every config equally and the rows become comparable. The ordering
 * control below is what keeps that claim honest — it repeats the first config, and
 * the two should now agree.
 *
 * ## This measures and records. It does not tune.
 *
 * C7 owns calibration, and a renderer tuned against its own benchmark before the
 * reference exists would be fitting noise. So the spec asserts only that the
 * measurement happened and is sane; the numbers travel as annotations, and the
 * verdict against the hypothesis is written up rather than asserted.
 *
 * Run it alone: `pnpm --filter @vitrea/renderer-webgpu test:bench`. Two benchmarks
 * contending for one GPU measure the contention — S2 lost a whole run that way —
 * which is why `playwright.config.ts` pins `workers: 1`.
 */

import { expect, test } from "@playwright/test";

import { openHarness, requireHardwareAdapter } from "../support";

/** §Performance envelope's hypothesis, in ms of GPU time per frame. */
const BUDGET_MS = 2;

const CONFIGS = [
  { label: "mobile-390x844@3", widthCss: 390, heightCss: 844, devicePixelRatio: 3 },
  { label: "desktop-1440x900@2", widthCss: 1440, heightCss: 900, devicePixelRatio: 2 },
  {
    label: "mobile-390x844@3 family-C",
    widthCss: 390,
    heightCss: 844,
    devicePixelRatio: 3,
    family: "rsup" as const,
  },
  /*
   * What the outer shadow costs (W8), as a row rather than as an argument.
   *
   * The facet is not free, and the reason is structural: the field, optics and
   * highlight passes are all confined to the group's field rect, so a shadow
   * reaching about 46 CSS px has to be rasterised into a rect padded by 46 rather
   * than by the rim-and-bulge 3. On this scene's small controls that is a
   * multiple of the fragments rather than a margin on them.
   *
   * Measured against the same scene at `occlusion: 0`, which takes the pad to
   * exactly zero — a profile that declines the shadow pays what it paid before
   * the facet existed, and this row is what says so. Interleaved with the rest,
   * because two numbers from two processes measure the GPU's clock state at least
   * as much as they measure the renderer (see the methodology note above).
   *
   * **The verdict, recorded rather than asserted, as this file's rule is.** On
   * `apple / metal-3`: the shadow costs about **2.8x** the frame's GPU time on the
   * mobile scene (median ratio 2.79 over three runs), taking it from roughly 40%
   * of the ~2 ms hypothesis to roughly 115%. It came down from 3.35 in two steps,
   * each measured on this row: scoping the highlight pass back to the surface's
   * own rect (3.35 → 3.11), and thresholding the field pad on the
   * compositing-space alpha the canvas actually writes rather than on the linear
   * occlusion, which had been over-allocating five CSS px on every edge
   * (3.11 → 2.79). That is the facet's
   * footprint arriving, not an inefficiency in how it is drawn: the shadow covers
   * 8.5–29.6% of the canvas in the reference, and every pixel of it has to be
   * written by something. What is not inherent is the FIELD pass rasterising the
   * whole enlarged rect at full resolution to feed a term whose own detail is a
   * 15 px Gaussian — a dedicated low-resolution shadow pass is the structural fix,
   * and it is a design change rather than a tuning one, so it is recorded here for
   * the next cut rather than taken now.
   */
  {
    label: "mobile-390x844@3 shadow-off",
    widthCss: 390,
    heightCss: 844,
    devicePixelRatio: 3,
    materialProfile: {
      // Every amplitude anchor and the lift at zero — the facet off (W14 G1).
      outerShadow: {
        thinOcclusionDark: 0,
        thinOcclusionMid: 0,
        thinOcclusionBright: 0,
        thickOcclusionAt96: 0,
        thickOcclusionAt128: 0,
        thickOcclusionAt160: 0,
        liftAmplitude: 0,
      },
    },
  },
  // The ordering control: the first config again. Interleaved, it should land on
  // the first row's number; if it does not, nothing else in the table is
  // comparable either.
  { label: "mobile-390x844@3 control", widthCss: 390, heightCss: 844, devicePixelRatio: 3 },
];

test.describe("@bench the performance envelope", () => {
  test("measures the declared scenes pass by pass", async ({ page }) => {
    test.setTimeout(300_000);
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const measurement = await page.evaluate(
      (configs) => window.vitrea.bench({ configs, rounds: 60, warmup: 20 }),
      CONFIGS,
    );

    const lines: string[] = [
      `adapter: ${report.vendor ?? "?"}/${report.architecture ?? "?"} ` +
        `(fallback: ${String(report.isFallback === true)}, timestamp-query: ${String(report.timestamps === true)})`,
      `method: ${measurement.method}, ${measurement.rounds} interleaved rounds per config`,
    ];

    for (const result of measurement.results) {
      const passes = Object.entries(result.passMs)
        .filter(([, ms]) => ms > 0)
        .sort((a, b) => b[1] - a[1])
        .map(([label, ms]) => `${label}=${ms.toFixed(3)}`)
        .join(" ");
      const gpu = result.gpuMsPerFrame;

      lines.push(
        `${result.label}: gpu(median)=${gpu === undefined ? "n/a" : `${gpu.toFixed(3)}ms`} ` +
          `gpu(p95)=${result.gpuP95 === undefined ? "n/a" : `${result.gpuP95.toFixed(3)}ms`} ` +
          `wall(median)=${result.wallMsPerFrame.toFixed(3)}ms wall(p95)=${result.wallP95.toFixed(3)}ms ` +
          `budget=${gpu === undefined ? "n/a" : `${((gpu / BUDGET_MS) * 100).toFixed(0)}%`} ` +
          `anomalies=${result.anomalies} | ${passes}`,
      );

      // Sanity, not tuning: the measurement ran and produced a frame time that is
      // a number rather than a stall.
      expect(result.wallMsPerFrame).toBeGreaterThan(0);
      expect(result.wallMsPerFrame).toBeLessThan(200);
      if (measurement.method === "timestamp-query") {
        expect(gpu, `${result.label} produced no GPU time`).toBeDefined();
        expect(gpu ?? 0).toBeGreaterThan(0);
        // Chrome quantises timestamps to 100 microseconds unless
        // `--disable-dawn-features=timestamp_quantization` is passed; a run that
        // reads every pass as exactly 0 has hit that, and is not a measurement.
        const nonZero = Object.values(result.passMs).filter((ms) => ms > 0);
        expect(
          nonZero.length,
          "every pass read as zero — check timestamp quantization",
        ).toBeGreaterThan(2);
      }
    }

    for (const line of lines) {
      test.info().annotations.push({ type: "bench", description: line });
    }

    // The ordering control. Within 25% of the row it repeats, or the interleaving
    // is not doing its job and none of the comparisons above mean anything.
    const first = measurement.results[0]?.gpuMsPerFrame;
    const control = measurement.results.at(-1)?.gpuMsPerFrame;
    if (first !== undefined && control !== undefined) {
      expect(
        Math.abs(Math.log2(control / first)),
        `ordering control drifted: ${first.toFixed(3)}ms then ${control.toFixed(3)}ms`,
      ).toBeLessThan(Math.log2(1.25));
    }
  });
});
