import { expect, test, type Page } from "@playwright/test";

import {
  adaptedSourceOptics,
  backdropToneAdaptation,
  backdropToneResponseLevel,
  cssOpticsFromSource,
  cssTierCompositeLevel,
  cssTierOptics,
  resolvedBackdropTone,
  resolvedBackdropToneResponse,
  rimAmplitude,
  sourceInteriorLight,
  sourceSize,
  COLLAPSE_TRANSMISSION,
  CSS_TIER_MAPPING,
  type CssTierMapping,
  innerShadowedSourceOptics,
  interiorBandLight,
  interiorShadowKeep,
  linearChainReaches,
  sizeOcclusionAlphaAt,
  sizeThickness,
  sourceOptics,
  toneRespondedSourceOptics,
} from "../../src/optics";
import { colorSchemeMaterialProfile } from "../../src/color-scheme";
import { DEFAULT_MATERIAL_PROFILE_DOCUMENT } from "../../src/material-document";
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
 * **The collapse is inert on the material this package now ships** (W29 G4). The
 * two mechanisms below are both still in the runtime and both still fitted per
 * document, but macOS 27's adaptation band measures inert (claims §5.153 §2 item
 * 1) — `k` is 0.00 at every step of every sweep in this file — so what these
 * cases read is the response curve alone. The collapse's own assertions are kept
 * and inverted rather than deleted, so that a material which brings it back is
 * loud rather than silent; each says so where it stands.
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

/*
 * The material the harness's root actually draws, resolved rather than taken off
 * the module constants (W29 G4).
 *
 * The header above says the point of this mirror is that "a constant that moves
 * in the profile moves these expectations with it". Until 0.19.0 the renderer's
 * own defaults WERE what a root drew, so calling the exported functions with no
 * patch satisfied that by accident. They are not any more: W29 Decision Log 1 (i)
 * holds `DEFAULT_MATERIAL_PROFILE` still at the macOS 26.5 light material and a
 * root resolves a selected document over it, so an unpatched mirror would be
 * comparing one material's arithmetic against another material's declarations.
 *
 * The light endpoint of the default document, because `createRoot` here passes
 * no `colorScheme` and the default is light.
 */
const PROFILE = colorSchemeMaterialProfile("light", DEFAULT_MATERIAL_PROFILE_DOCUMENT);
const MAPPING: CssTierMapping = {
  ...CSS_TIER_MAPPING,
  ...DEFAULT_MATERIAL_PROFILE_DOCUMENT.cssTierMapping,
};
const SIZE = sourceSize(PROFILE);
const TONE = resolvedBackdropTone(PROFILE);
const RESPONSE = resolvedBackdropToneResponse(PROFILE);
const INTERIOR_LIGHT = sourceInteriorLight(PROFILE);
const SOURCE = sourceOptics(PROFILE).regular;

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
  const thickness = sizeThickness(spanPx, SIZE);
  const collapse = backdropToneAdaptation(linear, thickness, TONE);
  /*
   * Re-pointed at W17 G1 (charter Decision Log 2 (b)): the size law's occlusion
   * enters the alpha BEFORE the W9 response solve, which is where the shader's
   * `sizedAlpha` puts it, and the inner shadow enters the pair after it. Solving
   * at the unsized alpha and raising it afterwards — which is what this helper
   * did, mirroring the tier — lands the interior's mean above the response the
   * solve exists to hit, by up to +0.027 of the level (claims §5.74 §3). The law
   * is unchanged and its order is not, so the helper follows the tier there.
   */
  const sized = { ...SOURCE, tintAlpha: sizeOcclusionAlphaAt(SOURCE.tintAlpha, thickness, SIZE) };
  const responded = toneRespondedSourceOptics(sized, tone, thickness, collapse, 1, RESPONSE);
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
    interiorShadowKeep(SOURCE, geometry, thickness, 1 - collapse, INTERIOR_LIGHT),
  );
  /*
   * The conversion the tier actually runs, ANCHOR AND ALL (W21 Decision Log 4
   * (a)), and it has to be the anchored one since W24 (claims §5.108 §2).
   *
   * The unanchored `cssTintAlpha` stood in for it while a collapsed surface's
   * alpha saturated at 1, where the two agree by construction. The collapse now
   * keeps a transmission, so the alpha it hands the conversion is `1 − k·c`
   * rather than 1, and on a backdrop this dark the tier anchors its solve on the
   * group's own tone — where the two conversions differ by 0.012, which is eight
   * times the declaration's own rounding step. So the helper follows the tier
   * here as it already follows it on the order of the size occlusion above.
   */
  const interior = {
    tintAlpha: shadowed.tintAlpha,
    tint: shadowed.tint,
    // The band carries its evaluated amplitude, not the intercept (W23).
    // W36's lower black body reaches the conversion seam, exposing the stale
    // intercept here: it selected the reference anchor instead of measured black.
    addedLight: interiorBandLight(
      { ...SOURCE, rimAlpha: rimAmplitude(SOURCE, linear) },
      geometry, 1 - collapse, INTERIOR_LIGHT,
    ),
  };
  const anchor = linearChainReaches(cssTierCompositeLevel(interior, tone.luminance))
    ? undefined
    : { linearMean: tone.linearLuminance, toneLevel: tone.luminance };
  const converted = cssOpticsFromSource(
    cssTierOptics(PROFILE, MAPPING).regular,
    shadowed,
    MAPPING,
    anchor,
    "regular",
  );
  return {
    colour: converted.tint.join(", "),
    occlusion: Math.round(converted.tintAlpha * 1000) / 1000,
    target: backdropToneResponseLevel(grey / 255, thickness, RESPONSE),
  };
};

/** One rounding step of the declared occlusion, which is written to 3 decimals. */
const ROUNDING = 0.0015;

test("a small surface over a near-black backdrop stays a body, and no longer becomes it", async ({
  page,
}) => {
  /*
   * **Inverted at W29 G4, and the inversion is the finding.**
   *
   * `dark-solid` (28, 28, 30) is the calibration backdrop where the macOS 26.5
   * reference's own 44 px capsule was byte-identical to its background, so this
   * case asserted the collapse: an opacity of 1 − `collapseTransmission`, the
   * backdrop's own bytes as the declared colour, and a rendered pixel within four
   * codes of the backdrop.
   *
   * macOS 27's material does not do that anywhere. W29 G2 measured Apple's body
   * over `dark-solid` at **0.2899 linear against a backdrop of 0.06**, five times
   * its own backdrop (§5.151 §4), and W29 G3 measured the adaptation band inert
   * and moved it to the bottom of its range (§5.153 §2 item 1). W29 G4 made that
   * document what a root resolves, so what this case can assert is the opposite
   * of what it used to — and it is asserted against the law's own mirror rather
   * than against a literal.
   */
  await buildScene(page, "rgb(28, 28, 30)");

  const small = await declared(page, "small");
  const law = lawDeclares(28, 44);

  // The tier runs the law: the declaration is the mirror's, to its rounding step.
  expect(Math.abs(small.occlusion - law.occlusion)).toBeLessThanOrEqual(ROUNDING);
  // And the law is not a collapse. Well clear of it rather than merely unequal:
  // a collapsed declaration sits at 0.983 and this sits near 0.65.
  expect(small.occlusion).toBeLessThan(1 - COLLAPSE_TRANSMISSION - 0.1);
  // The declared colour is a light body, not the backdrop's own bytes.
  expect(small.tint).not.toBe("rgba(28, 28, 30, 0.983)");

  // And the pixels say the same thing: the surface is plainly in front of its
  // backdrop where it used to be indistinguishable from it.
  const pixel = (await sample(page, SMALL)).at(60, 22);
  expect(Math.abs(level(pixel) - level({ r: 28, g: 28, b: 30 }))).toBeGreaterThan(40);
});

test("a large surface over the same backdrop is the more opaque of the two", async ({
  page,
}) => {
  await buildScene(page, "rgb(28, 28, 30)");

  const large = await declared(page, "large");
  const small = await declared(page, "small");

  /*
   * **The size gate survives and its sign turns over** (W29 G4). While the small
   * surface collapsed onto this backdrop it was the more opaque of the two by a
   * wide margin, and this case read the gate that way. With nothing collapsing,
   * what separates the two is the response curve's own thin and thick rows, and
   * at macOS 27's first anchor the thick row sits above the thin one (0.242
   * against 0.214) exactly as it does at the mid greys the case below reads. So
   * the large surface is the more opaque here too — one rule at both ends of the
   * curve, where there used to be two.
   */
  expect(large.occlusion).toBeGreaterThan(small.occlusion);
  expect(large.tint).not.toBe(small.tint);
  /*
   * The rendered separation is real and small. It was more than 60 codes while
   * the small surface was its backdrop; it is now a few, because both surfaces
   * are bodies over the same backdrop and only their thickness differs. Asserted
   * as a direction with a floor of one code rather than as a magnitude: the claim
   * is that the size law reaches the pixels, and pinning the magnitude here would
   * be pinning the conversion's rounding.
   */
  expect(level((await sample(page, LARGE)).at(130, 70))).toBeGreaterThan(
    level((await sample(page, SMALL)).at(60, 22)) + 1,
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
  // Moved at W29 G4: the large surface read 255 under the macOS 26.5 material and
  // reads 254 under macOS 27's. The claim is unchanged — the shift saturates at
  // white and the remainder is carried as opacity — and the two sizes rounding to
  // the same code again is a property of this material rather than of the law,
  // which is why each is still read per surface rather than by asserting equality.
  expect(colourOf(large.tint)).toBe("254, 254, 254");

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
   *
   * **The collapse arm carries a second named seam since W24** (claims §5.108
   * §2). The declared opacity is now `A − k·c`, and `k` falls across this sweep,
   * so the term the tier hands back to `backdrop-filter` shrinks with it — a RISE
   * where the arm falls, measured at +0.0025 over the whole arm, which is less
   * than the constant itself and is bounded by it. The arm's tolerance therefore
   * admits `COLLAPSE_TRANSMISSION` beside the rounding step, and the claim it
   * still carries is unchanged in kind: the excursion the V has to show is 0.15,
   * an order of magnitude larger than either seam.
   */
  const steps = 12;
  const occlusions: number[] = [];
  const levels: number[] = [];
  for (let i = 0; i < steps; i += 1) {
    const value = Math.round((i / (steps - 1)) * 140);
    await buildScene(page, `rgb(${value}, ${value}, ${value})`);
    const small = await declared(page, "small");
    expect(colourOf(small.tint), `tint at ${value}`).toBe(lawDeclares(value, 44).colour);
    expect(
      Math.abs(small.occlusion - lawDeclares(value, 44).occlusion),
      `occlusion at ${value}`,
    ).toBeLessThanOrEqual(ROUNDING);
    occlusions.push(small.occlusion);
    levels.push(level((await sample(page, SMALL)).at(60, 22)));
  }

  /*
   * **Monotone including black since W36** (claims §5.179).
   *
   * W29's recorded ramp was 187.5, 144.2, 150.1, 156.6, 164.2, 169.5, 174.7,
   * 179.7, 183.7, 187.5, 189.8, 192.7. Its old assertion REQUIRED the first
   * step's >20-code overshoot. G0 identified that black as the response's zero
   * authority fallback, not the conversion quantum the old comment blamed.
   * W36's compact black branch removes it: this harness reads 141.3822 then
   * 144.1696, with all subsequent steps unchanged. The registered texture is
   * not painted behind these hosts, so this is a monotonicity check, not the
   * native-black deep-domain measurement in the calibration bed.
   *
   * The old exclusion of step zero now comes off by fix. The one-code rounding
   * allowance stays the same; no ramp value is pinned to a new literal.
   */
  for (let i = 1; i < steps; i += 1) {
    expect(levels[i] as number, `level ${i}`).toBeGreaterThanOrEqual((levels[i - 1] as number) - 1);
  }

  /*
   * The dark end. It was `1 − collapseTransmission` while the collapse owned
   * this backdrop; on macOS 27 nothing collapses anywhere (`k` is 0.00 at every
   * step of this ramp, both spans) and the end is simply the curve's own value
   * there, which the per-step check above has already held to the law. Asserted
   * again as a value rather than dropped, so that a collapse returning to this
   * region would be loud.
   */
  expect(occlusions[0] as number).toBeCloseTo(lawDeclares(0, 44).occlusion, 3);
  expect(occlusions[0] as number).toBeLessThan(1 - COLLAPSE_TRANSMISSION - 0.1);
  const dip = occlusions.indexOf(Math.min(...occlusions));
  expect(dip).toBeGreaterThan(0);
  expect(dip).toBeLessThan(steps - 1);
  for (let i = 1; i <= dip; i += 1) {
    expect(occlusions[i] as number, `collapse arm ${i}`).toBeLessThanOrEqual(
      (occlusions[i - 1] as number) + ROUNDING + COLLAPSE_TRANSMISSION,
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
  /*
   * Two codes rather than one, from W29 G4. The sweep is 22 backdrops two grey
   * levels apart and it rises 151.3 → 172.5 across them; the one backward step
   * in it is **1.60 codes** at grey 50, and every other step is forward or flat.
   * The tolerance was one code under the macOS 26.5 material and that material's
   * declared alpha moved faster here, so a single code covered the conversion's
   * quantum. On macOS 27 the alpha crosses this whole band between 0.654 and
   * 0.663 — a ninth of the excursion — so the rendered level is carried almost
   * entirely by the backdrop showing through, and the overlay's encoded rounding
   * is a larger share of each step than it was.
   */
  for (let i = 1; i < fine; i += 1) {
    expect(fineLevels[i] as number, `fine level ${i}`).toBeGreaterThanOrEqual(
      (fineLevels[i - 1] as number) - 2,
    );
  }
  /*
   * **What this band carries on macOS 27, and what it does not** (W29 G4).
   *
   * The band 28…70 was chosen because it straddles the macOS 26.5 collapse for a
   * 44 px surface, size bias included, and the claim was that the collapse is a
   * slope rather than a switch: the declared alpha fell by more than 0.15 across
   * it and no single step took more than a third of that fall. On macOS 27 there
   * is no collapse here or anywhere — `k` reads 0.00 at every step of this sweep
   * and of the coarse one (`results/2026-09-20-w29-g4-landing/ramp-probe.txt`) —
   * so the alpha does not fall at all: it rises monotonically from 0.654 to
   * 0.663, which is the light attractor's arm and nothing else.
   *
   * So the excursion assertion is replaced by the statement that makes its
   * absence checkable rather than dropped. A collapse returning to this band
   * would put a fall of at least 0.15 in a series that is now flat to 0.009, and
   * the first line below would fail on it; the two that follow keep the
   * no-switch claim on both quantities, which is the half of the original that
   * still has something to be true about.
   */
  const fineFall = (fineOcclusions[0] as number) - Math.min(...fineOcclusions);
  expect(fineFall, "the collapse arm, which macOS 27 does not have").toBeLessThan(0.01);
  const fineExcursion = Math.max(...fineOcclusions) - Math.min(...fineOcclusions);
  expect(widest(fineOcclusions)).toBeLessThan(fineExcursion / 3);
  const levelExcursion = Math.max(...fineLevels) - Math.min(...fineLevels);
  expect(widest(fineLevels)).toBeLessThan(levelExcursion / 3);
});
