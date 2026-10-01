// TEMPORARY perf-wave A/B (not committed): the bench's eight surfaces, law on, rendered in
// rgba32float, saved for comparison between the render-pass stage and the compute stage.
import { writeFileSync } from "node:fs";
import { test } from "@playwright/test";
import { openHarness, requireHardwareAdapter } from "../support";

const TAG = process.env["W42_AB_TAG"] ?? "new";
const LAW = { bodyLawStrength: 1, bodyLawWidthUnit: 1, bodyLawEncodedAveraging: 1 };

function scene(widthCss: number, heightCss: number, dpr: number) {
  const surfaces = (prefix: string, count: number, y: number, size: [number, number]) =>
    Array.from({ length: count }, (_, i) => ({
      nodeId: `${prefix}${i}`, family: "fixed-rounded-rect",
      shape: { center: [(widthCss / (count + 1)) * (i + 1), y], size, radii: [14, 14, 14, 14],
        smoothing: 0.5, thickness: 10 },
      reference: "figma-smoothing",
      channels: { press: 0.2, glow: 0.4, sweep: 0.3, shimmer: 1, lensStrength: 1 },
    }));
  return {
    name: "w42-ab", widthCss, heightCss, devicePixelRatio: dpr,
    backdrop: { kind: "checkerboard", cell: 12 },
    groups: [
      { groupId: "toolbar", surfaces: surfaces("t", 4, heightCss * 0.18, [Math.min(72, widthCss / 6), 44]),
        backdropSourceId: "bg", refraction: "true", analysisExact: true },
      { groupId: "segmented", surfaces: surfaces("s", 3, heightCss * 0.5, [Math.min(84, widthCss / 5), 40]),
        backdropSourceId: "bg", refraction: "true", analysisExact: true },
      { groupId: "morph", surfaces: [{ nodeId: "m", family: "fixed-rounded-rect",
        shape: { center: [widthCss / 2, heightCss * 0.8], size: [widthCss * 0.6, 96], radii: [30, 30, 30, 30],
          smoothing: 0.62, thickness: 16 }, reference: "figma-smoothing",
        channels: { press: 0.35, glow: 0.8, sweep: 0.6, shimmer: 1, lensStrength: 1 } }],
        backdropSourceId: "bg", refraction: "true", analysisExact: true },
    ],
  };
}

test("@w42-ab render the bench scene", async ({ page }) => {
  test.setTimeout(600_000);
  requireHardwareAdapter(await openHarness(page));
  const variants = [
    ["m-active", scene(390, 844, 3), LAW], ["m-receded", scene(390, 844, 3), { ...LAW, bodyLawPose: 1 }],
    ["d-active", scene(1440, 900, 2), LAW], ["d-receded", scene(1440, 900, 2), { ...LAW, bodyLawPose: 1 }],
    ["m-active-d2", scene(390, 844, 3), { ...LAW, bodyLawEncodedAveraging: 0 }],
    ["m-active-edge", scene(390, 844, 3), { ...LAW, bodyLawEdgeSwap: 1 }],
  ] as const;
  for (const [name, s, patch] of variants) {
    const capture = await page.evaluate(([sc, p]) => window.vitrea.renderSceneFloat(sc as never, p as never),
      [s, patch] as const);
    writeFileSync(`/tmp/w42-perf/ab-${TAG}-${name}.bin`, Buffer.from(capture.pixels, "base64"));
    writeFileSync(`/tmp/w42-perf/ab-${TAG}-${name}.json`, JSON.stringify({ width: capture.width, height: capture.height, format: capture.format }));
  }
});
