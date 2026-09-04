import { expect, test, type Page } from "@playwright/test";

import {
  adaptedSourceOptics,
  backdropToneAdaptation,
  backdropToneResponseLevel,
  cssTintAlpha,
  cssTintColor,
  innerShadowedSourceOptics,
  interiorShadowKeep,
  sizeOcclusionAlphaAt,
  sizeThickness,
  sourceOptics,
  toneRespondedSourceOptics,
} from "../../src/optics";
import { gotoHarness, sample } from "../support";

/**
 * Backdrop tone adaptation (W7, re-lawed by W9), in a browser, on the CSS tier.
 *
 * The law is arithmetic and is unit-tested as arithmetic. Two things are not,
 * and both live here.
 *
 * The first is the **reading**. `sampleBackdropTone` draws the app's own backdrop
 * source into a scratch canvas and averages it — in the ENCODED space since W9,
 * because that is the mean the reference's own response tracks (claims §5.31) —
 * and a browser is the only place that code runs at all: jsdom has no 2-D
 * context.
 *
 * The second is the **shape of the response**, on rendered pixels rather than on
 * the curve. Since W9 the axis is two mechanisms with one seam between them
 * (W9 Decision Log 3). The *collapse mix* owns the near-black knee: a smoothstep
 * band on the linear level that converges a small surface onto its backdrop and
 * closes its transparency doing so. The *response curve* owns the interior mean
 * everywhere the collapse does not: a monotone curve through three measured
 * solid anchors, its levels functions of surface size, landed by shifting the
 * neutral's luma — and where a white neutral cannot reach the target, by
 * opacity, the "light attractor". So the declared occlusion is not monotone in
 * the backdrop's level and never claimed to be after W9: it falls through the
 * collapse, bottoms out where the neutral is darkest, and rises again as the
 * backdrop lightens and the attractor carries the remainder. The rendered LEVEL
 * is monotone, which is the claim an adopter can see.
 *
 * **Expectations are the law's own values.** `lawDeclares` below runs the same
 * per-surface chain `root.ts` runs for a flat backdrop, on the exported
 * functions, so a constant that moves in the profile moves these expectations
 * with it and a literal copied off one run cannot go stale silently. What the
 * browser adds to that mirror is the reading, the declarations and the pixels.
 *
 * **A fresh page per backdrop, deliberately.** The harness's `createRoot` leaves
 * the previous root's hosts in the document, so a loop that rebuilt the scene in
 * one page would read the *first* iteration's declarations off
 * `querySelector` while screenshotting the last iteration's pixels — which is a
 * fine way to prove a feature works when it does not.
 */

const SMALL = { x: 300, y: 200, width: 120, height: 44 };
const LARGE = { x: 300, y: 300, width: 260, height: 140 };

/**
 * One flat backdrop, one small surface over it and one large one.
 *
 * The pair is the point: the same backdrop moves them by very different amounts,
 * because both mechanisms are size-gated — over the settled bed's `dark-solid`
 * the reference's 44 px capsule vanishes into its background while its 96 px
 * rrect keeps three quarters of its own appearance.
 *
 * The backdrop is a *registered texture source* and is never painted on the page,
 * which is what the harness's texture groups have always done. That is not a
 * limitation here: what the CSS tier does with the tone it reads is entirely in
 * its declarations, and a surface that has adapted all the way is opaque, so its
 * rendered pixels are its declared colour whatever lies behind it.
 */
const buildScene = async (page: Page, fill: string): Promise<void> => {
  await gotoHarness(page);
  await page.evaluate(async (colour) => {
    await window.h.createRoot({ renderer: "css" });
    window.h.addTextureGroup({ groupId: "g", sourceId: "g.raster", fill: colour });
    window.h.addSurface({
      groupId: "g",
      nodeId: "small",
      left: 300,
      top: 200,
      width: 120,
      height: 44,
      radius: 22,
      label: "",
    });
    window.h.addSurface({
      groupId: "g",
      nodeId: "large",
      left: 300,
      top: 300,
      width: 260,
      height: 140,
      radius: 30,
      label: "",
    });
    window.h.frame(3);
  }, fill);
};

interface Declared {
  readonly occlusion: number;
  readonly tint: string;
}

const declared = (page: Page, nodeId: string): Promise<Declared> =>
  page.evaluate((id) => {
    const el = document.querySelector<HTMLElement>(`[data-vitrea-node="${id}"]`);
    return {
      occlusion: Number.parseFloat(el?.style.getPropertyValue("--vitrea-occlusion") ?? "0"),
      tint: el?.style.getPropertyValue("--vitrea-tint") ?? "",
    };
  }, nodeId);

const level = (pixel: { r: number; g: number; b: number }): number =>
  0.2126 * pixel.r + 0.7152 * pixel.g + 0.0722 * pixel.b;

/** `rgba(r, g, b, a)` → `"r, g, b"`, the colour without its alpha. */
const colourOf = (tint: string): string =>
  (/rgba?\(([^)]*)\)/.exec(tint)?.[1] ?? "")
    .split(",")
    .slice(0, 3)
    .map((part) => part.trim())
    .join(", ");

/**
 * The sRGB transfer, decoding — the same function `optics.ts` applies privately.
 * A flat backdrop is the one case where the encoded-space mean and the linear
 * mean are one value decoded, so the reading needs no sampling to mirror.
 */
const decode = (encoded: number): number =>
  encoded <= 0.04045 ? encoded / 12.92 : ((encoded + 0.055) / 1.055) ** 2.4;

interface LawDeclared {
  readonly colour: string;
  readonly occlusion: number;
  /** `R(encodedInput, thickness)` — the interior level the curve is aiming at. */
  readonly target: number;
}

const SOURCE = sourceOptics().regular;

/**
 * The CSS tier's tone chain for a flat grey backdrop, at nominal policy, on the
 * law's own functions — the per-surface sequence `root.ts` runs (collapse amount
 * → response solve → adaptation fold → tier conversion → size occlusion), with
 * the accessibility folds omitted because they are the identity at nominal.
 */
/** The two surfaces `buildScene` registers, whose boxes the inner shadow reads. */
const BOXES: Readonly<Record<number, { width: number; height: number; radius: number }>> = {
  44: { width: 120, height: 44, radius: 22 },
  140: { width: 260, height: 140, radius: 30 },
};

const lawDeclares = (grey: number, spanPx: number): LawDeclared => {
  const linear = decode(grey / 255);
  const tone = { rgb: [linear, linear, linear] as const, luminance: linear, linearLuminance: linear };
  const thickness = sizeThickness(spanPx);
  const collapse = backdropToneAdaptation(linear, thickness);
  /*
   * Re-pointed at W17 G1 (charter Decision Log 2 (b)): the size law's occlusion
   * enters the alpha BEFORE the W9 response solve, which is where the shader's
   * `sizedAlpha` puts it, and the inner shadow enters the pair after it. Solving
   * at the unsized alpha and raising it afterwards — which is what this helper
   * did, mirroring the tier — lands the interior's mean above the response the
   * solve exists to hit, by up to +0.027 of the level (claims §5.74 §3). The law
   * is unchanged and its order is not, so the helper follows the tier there.
   */
  const sized = { ...SOURCE, tintAlpha: sizeOcclusionAlphaAt(SOURCE.tintAlpha, thickness) };
  const responded = toneRespondedSourceOptics(sized, tone, thickness, collapse, 1);
  const adapted = adaptedSourceOptics(responded, tone.rgb, collapse);
  // The surface's own box, because the inner shadow's area mean is a co-area
  // integral over it — the same numbers `buildScene` registers above.
  const box = BOXES[spanPx]!;
  const geometry = {
    widthCssPx: box.width,
    heightCssPx: box.height,
    radiusCssPx: box.radius,
    thicknessCssPx: 8,
  };
  const shadowed = innerShadowedSourceOptics(
    adapted,
    interiorShadowKeep(SOURCE, geometry, thickness, 1 - collapse),
  );
  const alpha = cssTintAlpha(shadowed);
  return {
    colour: cssTintColor(shadowed, alpha).join(", "),
    occlusion: Math.round(alpha * 1000) / 1000,
    target: backdropToneResponseLevel(grey / 255, thickness),
  };
};

/** One rounding step of the declared occlusion, which is written to 3 decimals. */
const ROUNDING = 0.0015;

test("a small surface over a near-black backdrop becomes that backdrop", async ({ page }) => {
  // `dark-solid` (28, 28, 30) — the calibration backdrop where the reference's own
  // capsule is byte-identical to its background. Fully adapted, the CSS tier
  // declares the backdrop's own colour at an opacity of 1, so the surface renders
  // as its backdrop rather than as a body in front of it.
  await buildScene(page, "rgb(28, 28, 30)");

  const small = await declared(page, "small");
  expect(small.occlusion).toBeCloseTo(1, 3);
  // Not "close to" the backdrop — the backdrop's own bytes, at an opacity of 1.
  // The reading, the curve and the linear-lerp-to-sRGB-overlay conversion all
  // have to be right for this string to come out.
  expect(small.tint).toBe("rgba(28, 28, 30, 1)");

  const pixel = (await sample(page, SMALL)).at(60, 22);
  expect(Math.abs(level(pixel) - level({ r: 28, g: 28, b: 30 }))).toBeLessThan(4);
});

test("a large surface over the same backdrop keeps most of its own appearance", async ({
  page,
}) => {
  await buildScene(page, "rgb(28, 28, 30)");

  const large = await declared(page, "large");
  const small = await declared(page, "small");

  // The size gate. Same backdrop, same material, and the large surface is still
  // mostly its own colour where the small one is entirely its backdrop's.
  expect(large.occlusion).toBeLessThan(small.occlusion);
  expect(large.tint).not.toBe(small.tint);
  expect(level((await sample(page, LARGE)).at(130, 70))).toBeGreaterThan(
    level((await sample(page, SMALL)).at(60, 22)) + 60,
  );
});

test("a mid grey backdrop lands on the response curve, and the surface's size moves it", async ({
  page,
}) => {
  /*
   * Until W9 this backdrop was "above the curve's high edge" and the axis was
   * exactly inert on it. The response curve has no inert region: a mid grey is
   * between the mid and light anchors, and the reference's interior sits on the
   * curve there, at a level that depends on the surface's thickness.
   */
  await buildScene(page, "rgb(140, 140, 140)");

  const small = await declared(page, "small");
  const large = await declared(page, "large");
  const law = { small: lawDeclares(140, 44), large: lawDeclares(140, 140) };

  expect(colourOf(small.tint)).toBe(law.small.colour);
  expect(small.occlusion).toBe(law.small.occlusion);
  expect(colourOf(large.tint)).toBe(law.large.colour);
  expect(large.occlusion).toBe(law.large.occlusion);

  /*
   * At this grey the curve's target sits above what the white neutral reaches at
   * its calibrated alpha, so the achromatic shift saturates at white and the
   * remainder is carried as opacity. Pinned as a property of the shipped
   * constants, not derived.
   *
   * Re-pointed at W17 G1 (Decision Log 2 (b)): the inner shadow now enters the
   * mirror as the shader's own layer identity — `(k·a·c, 1 − k·(1 − a))`
   * composites to `k` times what `(a·c, a)` would — so a saturated white tint
   * comes back below white with the alpha raised to match. The keep is a co-area
   * integral over the surface's own box, so the two sizes no longer round to the
   * same code: the small surface reads 254 and the large 255, each its own law's.
   * The claim the test carries is unchanged — the shift saturates and the
   * remainder is opacity — and it is now read per surface rather than by
   * asserting the two are identical.
   */
  expect(colourOf(small.tint)).toBe("254, 254, 254");
  expect(colourOf(large.tint)).toBe("255, 255, 255");

  // The anchors' settled levels are functions of thickness, and at this grey the
  // thick row sits above the thin one — so the large surface is the MORE opaque,
  // the opposite of the near-black case above, and on the same law.
  expect(law.large.target).toBeGreaterThan(law.small.target);
  expect(large.occlusion).toBeGreaterThan(small.occlusion);
});

test("across the transition the level is monotone, the collapse is a slope, and the opacity hands over", async ({
  page,
}) => {
  /*
   * The evidence the reference bed cannot give. Twelve flat backdrops from black
   * to a mid grey, read as the small surface's declared occlusion and as its
   * rendered level, every declaration held to the law's own value.
   *
   * Three claims. The rendered level never moves the wrong way as the backdrop
   * darkens. The declared occlusion is V-shaped — it falls through the collapse,
   * bottoms out where the response solve has darkened the neutral furthest, and
   * rises with the light attractor — and each arm is monotone; a fourth mechanism
   * would show as a second dip. And the collapse is a slope rather than a
   * switch, which the coarse grid cannot resolve (the band is a few grey levels
   * wide), so a finer sweep across it carries that claim on its own.
   */
  const steps = 12;
  const occlusions: number[] = [];
  const levels: number[] = [];
  for (let i = 0; i < steps; i += 1) {
    const value = Math.round((i / (steps - 1)) * 140);
    await buildScene(page, `rgb(${value}, ${value}, ${value})`);
    const small = await declared(page, "small");
    expect(
      Math.abs(small.occlusion - lawDeclares(value, 44).occlusion),
      `occlusion at ${value}`,
    ).toBeLessThanOrEqual(ROUNDING);
    occlusions.push(small.occlusion);
    levels.push(level((await sample(page, SMALL)).at(60, 22)));
  }

  for (let i = 1; i < steps; i += 1) {
    expect(levels[i] as number, `level ${i}`).toBeGreaterThanOrEqual((levels[i - 1] as number) - 1);
  }

  // The ends: fully collapsed over black, and the curve's own value at the grey.
  expect(occlusions[0] as number).toBeCloseTo(1, 3);
  const dip = occlusions.indexOf(Math.min(...occlusions));
  expect(dip).toBeGreaterThan(0);
  expect(dip).toBeLessThan(steps - 1);
  for (let i = 1; i <= dip; i += 1) {
    expect(occlusions[i] as number, `collapse arm ${i}`).toBeLessThanOrEqual(
      (occlusions[i - 1] as number) + ROUNDING,
    );
  }
  for (let i = dip + 1; i < steps; i += 1) {
    expect(occlusions[i] as number, `attractor arm ${i}`).toBeGreaterThanOrEqual(
      (occlusions[i - 1] as number) - ROUNDING,
    );
  }
  const excursion = 1 - (occlusions[dip] as number);
  expect(excursion).toBeGreaterThan(0.15);

  /*
   * The slope. Twenty-two backdrops two grey levels apart across the collapse
   * band (28…70 straddles it for a 44 px surface, size bias included): no single
   * move in either quantity is more than a third of the whole excursion. One
   * seam is known and bounded by `ROUNDING`: the response solve stands down at a
   * collapse amount above 0.995, so the first backdrop it acts on can move the
   * declared alpha by a rounding step against the arm's direction.
   */
  const fine = 22;
  const fineOcclusions: number[] = [];
  const fineLevels: number[] = [];
  for (let i = 0; i < fine; i += 1) {
    const value = Math.round(28 + (i / (fine - 1)) * 42);
    await buildScene(page, `rgb(${value}, ${value}, ${value})`);
    const small = await declared(page, "small");
    expect(
      Math.abs(small.occlusion - lawDeclares(value, 44).occlusion),
      `occlusion at ${value}`,
    ).toBeLessThanOrEqual(ROUNDING);
    fineOcclusions.push(small.occlusion);
    fineLevels.push(level((await sample(page, SMALL)).at(60, 22)));
  }
  const widest = (series: readonly number[]): number => {
    let most = 0;
    for (let i = 1; i < series.length; i += 1) {
      most = Math.max(most, Math.abs((series[i] as number) - (series[i - 1] as number)));
    }
    return most;
  };
  for (let i = 1; i < fine; i += 1) {
    expect(fineLevels[i] as number, `fine level ${i}`).toBeGreaterThanOrEqual(
      (fineLevels[i - 1] as number) - 1,
    );
  }
  const fineExcursion = (fineOcclusions[0] as number) - Math.min(...fineOcclusions);
  expect(fineExcursion).toBeGreaterThan(0.15);
  expect(widest(fineOcclusions)).toBeLessThan(fineExcursion / 3);
  const levelExcursion = Math.max(...fineLevels) - Math.min(...fineLevels);
  expect(widest(fineLevels)).toBeLessThan(levelExcursion / 3);
});
