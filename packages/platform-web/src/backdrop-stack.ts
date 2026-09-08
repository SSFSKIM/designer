/**
 * # A group's backdrop when the backdrop is another group's glass (W22 G3)
 *
 * A `css-backdrop` group samples the page rather than a texture the app handed
 * over, and `backdrop-tone.ts` can only read textures — it draws its pixels into
 * a scratch canvas and averages them. So until this module existed, a group
 * sampling the DOM was handed **no backdrop tone at all**, and the whole tone
 * axis stood down for it: the collapse's amount is zero without a measurement by
 * design (`backdrop-tone.ts`'s rule 3, "guessing a level would be the one failure
 * mode that matters"), and W9's response law rides the same gate. The group drew
 * the material's unadapted body over whatever it happened to be over.
 *
 * That rule is right for a group over a page vitrea knows nothing about. It is
 * wrong for the one case where vitrea knows the answer exactly: a group stacked
 * over **another vitrea surface**. There the backdrop is not an unknown page, it
 * is glass this runtime resolved itself in the same frame, and its rendered
 * output is a closed form of quantities already in hand.
 *
 * Measured, on the calibration bed's `checkerboard__glass-over-glass__rest` at
 * the dark profile (claims §5.94 §5; W22 G3): the overlay pane drew 0.0493 of
 * linear luminance where Apple's draws 0.0207 and the shipped dark response law
 * at the true backdrop gives 0.0245 — the overlay's body was the unadapted
 * material's own tint, `(1 − 0.9198)·0.0470 + 0.9198·0.05 = 0.0498`, a flat mid
 * grey that inverted the reference's sign (Apple's overlay is *darker* than its
 * base; vitrea's was lighter). No constant of the material was wrong. The input
 * was missing.
 *
 * ## What the surface beneath renders at
 *
 * `cssTierCompositeLevel` already names what a surface draws: the tint's lerp
 * over its own backdrop, `(1 − α)·b + α·T + X` per channel in linear light. That
 * is an affine in the backdrop, so the surface's output tone follows from its
 * backdrop's tone by applying the same affine — which is what `compositeToneOver`
 * does, and the reason this is a mechanism rather than a level: nothing here
 * carries a number of its own.
 *
 * **The author's tint is part of what the surface draws, so it is part of what a
 * group above it samples.** W10's composition contract puts the author's layer
 * last — the seed at its shade, opaque, at the author's opacity, composited over
 * the converted material in the ENCODED space, which is what a `CALayer` with
 * `opacity` does and what both tiers draw. So the layer is applied here in that
 * space, after the material's affine and not folded into it. Without it a
 * full-strength red base published the same achromatic tone as an untinted one and
 * the pane above it adapted to a colour and a level that were on nobody's screen.
 *
 * The one place the affine is not the whole answer is W9's split between the
 * tone's two spaces. The tone COLOUR and `linearLuminance` are linear means and
 * the affine carries them exactly. The tone LEVEL is the backdrop's ENCODED-space
 * mean, decoded, and an encoded-space mean does not commute with a linear affine:
 * the gap between the two statistics is the encoding's curvature over the
 * backdrop's own spread, and the surface has narrowed that spread — by its
 * occlusion, and by the blur it drew the backdrop through, which is the larger of
 * the two.
 *
 * **So the output's level is its linear mean**, and the gap the input carried
 * does not travel. That is a measurement and not an assumption: read off the
 * stacked cell's own captures, the base pane's rendered body has an encoded-space
 * mean 0.0020 – 0.0027 below its linear mean in the dark scheme and 0.0037 –
 * 0.0048 below it in the light one, on both tiers and at both scales, against an
 * input whose two statistics stand 0.286 apart. A surface's own material is what
 * flattens the structure the split exists to carry.
 *
 * The form this replaced transported the input's gap scaled by the square of the
 * transmission — exact at both ends of the transmission range, and wrong in the
 * middle by more than the whole quantity: it read −0.0749 on the light base pane
 * where the capture reads −0.0042, because the variance is not the only thing the
 * composite changes and the encoding's curvature at a body near 0.66 is nothing
 * like its curvature at a checkerboard's 0.5. Carrying nothing is off by at most
 * 0.005 there; carrying the transported gap was off by 0.07.
 *
 * The residual is recorded rather than corrected. Correcting it needs the
 * backdrop's distribution and the surface's blur, and the tone sample carries two
 * moments and no kernel. The limit it gives up is a surface transparent enough to
 * pass its backdrop's structure through — this says the pane above it is over a
 * flat backdrop when it is over a faint checkerboard — and the bound on that is
 * the 0.005 above.
 *
 * ## Which surface is beneath
 *
 * §Geometry's X1 says nodes in one plane must not overlap, so a stack is two
 * planes by law and never two orders of one plane. The surface a group is over is
 * therefore the last-painted surface in a **strictly lower** plane whose box
 * contains the group's whole footprint — `compareZSlot`'s own back-to-front
 * order, read backwards.
 *
 * Containment and not overlap, and that is deliberate. A footprint straddling one
 * surface's edge sits over glass on one side and over a page vitrea has not
 * measured on the other, and there is no single backdrop to hand it; the rule
 * above then finds nothing and the group keeps the unadapted body it has always
 * drawn. Guessing an area-weighted blend of a measurement and an unknown would be
 * the failure mode `backdrop-tone.ts` refuses by name.
 *
 * Two approximations are stated rather than implied. The containment test is on
 * border boxes, so a footprint tucked into a rounded surface's own corner is
 * treated as contained when a sliver of it is not; the error is bounded by that
 * surface's radius. And the derivation is one hop — a group over a group over a
 * group takes the tone of the surface immediately beneath it, which is the right
 * answer, because that surface's own tone already carries everything below it.
 */

import { GLASS_PLANES, compareZSlot, type GlassPlane, type Rect } from "@vitreajs/vitrea";

import type { CssTierInterior } from "./css-tier";
import type { BackdropToneSample } from "./backdrop-tone";

/**
 * A surface this frame has already resolved, with the tone it renders at.
 *
 * Filled by the frame's group loop as each surface's interior resolves, and read
 * by a later group that turns out to be sitting on it. `tone` is the surface's
 * OUTPUT — what a group above it would be sampling — not the backdrop it drew
 * over.
 */
export interface PaintedSurface {
  readonly plane: GlassPlane;
  readonly order: number;
  /**
   * The surface's VISIBLE extent, viewport CSS px — its measured border box
   * reduced to the windows its clipping ancestors let through.
   *
   * Visible and not measured, for the same reason `ProxyGeometry.clipUnion` is
   * (Decision Log #41(k)): a host's border box is reported unclipped, so a
   * surface scrolled out of an `overflow: scroll` ancestor still has a full-size
   * box while painting nothing at all. A backdrop is what a group above actually
   * looks through to, and a surface that is not on the screen is not one.
   */
  readonly bounds: Rect;
  readonly tone: BackdropToneSample;
}

/**
 * The author's tint as the tier draws it: the seed at its shade, in encoded
 * channels 0..255, at the author's opacity.
 *
 * `authorTintLayer`'s return shape, restated structurally rather than imported,
 * so this module keeps its one dependency on `css-tier`'s vocabulary.
 */
export interface AuthorTintLayer {
  readonly color: readonly [number, number, number];
  readonly strength: number;
}

const srgbEncode = (linear: number): number => {
  const clamped = Math.min(1, Math.max(0, linear));
  return clamped <= 0.0031308 ? 12.92 * clamped : 1.055 * Math.pow(clamped, 1 / 2.4) - 0.055;
};

const srgbDecode = (encoded: number): number => {
  const clamped = Math.min(1, Math.max(0, encoded));
  return clamped <= 0.04045 ? clamped / 12.92 : Math.pow((clamped + 0.055) / 1.055, 2.4);
};

/**
 * Containment, on rects that both have extent.
 *
 * The extent test is not a guard against nonsense, it is the rule: a host that
 * has not been measured yet, or one its ancestors have cropped away, reports an
 * empty box, and an empty box is contained by everything and contains nothing.
 * Neither a backdrop nor a footprint can be a surface that is not there.
 */
const contains = (outer: Rect, inner: Rect): boolean =>
  outer.width > 0 &&
  outer.height > 0 &&
  inner.width > 0 &&
  inner.height > 0 &&
  inner.x >= outer.x &&
  inner.y >= outer.y &&
  inner.x + inner.width <= outer.x + outer.width &&
  inner.y + inner.height <= outer.y + outer.height;

/**
 * The tone a surface with this interior and this author tint renders at, over a
 * backdrop with this tone — the renderer's own composite, applied to the tone
 * sample's colour.
 *
 * Two steps, in the two spaces the composition contract puts them in: the
 * material's affine in linear light, then the author's layer as an encoded lerp
 * over it. The colour and the linear mean follow exactly; the level is the linear
 * mean, for the reason the module comment gives and with the residual it names.
 */
export function compositeToneOver(
  interior: CssTierInterior,
  tone: BackdropToneSample,
  author?: AuthorTintLayer,
): BackdropToneSample {
  const alpha = Math.min(1, Math.max(0, interior.tintAlpha));
  const transmission = 1 - alpha;
  const composite = (backdrop: number, tint: number): number =>
    transmission * backdrop + alpha * tint + interior.addedLight;

  const material: readonly [number, number, number] = [
    composite(tone.rgb[0], interior.tint[0]),
    composite(tone.rgb[1], interior.tint[1]),
    composite(tone.rgb[2], interior.tint[2]),
  ];

  // `(1 − s)·material + s·layer`, encoded — the space the author's layer
  // composites in on both tiers. At strength 0 the round trip through the
  // transfer is the identity to the last bit the transfer is invertible in, and
  // the branch keeps it exactly so rather than nearly so.
  const strength = author === undefined ? 0 : Math.min(1, Math.max(0, author.strength));
  const rgb: readonly [number, number, number] =
    author === undefined || strength <= 0
      ? material
      : [
          srgbDecode((1 - strength) * srgbEncode(material[0]) + strength * (author.color[0] / 255)),
          srgbDecode((1 - strength) * srgbEncode(material[1]) + strength * (author.color[1] / 255)),
          srgbDecode((1 - strength) * srgbEncode(material[2]) + strength * (author.color[2] / 255)),
        ];

  const linearLuminance = 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2];
  return { rgb, linearLuminance, luminance: linearLuminance };
}

/**
 * The tone of the glass beneath this footprint, or `undefined` where no single
 * already-painted surface carries the whole of it.
 *
 * `painted` is in resolution order; the search runs from the back so that the
 * NEAREST surface underneath wins, which is the one whose output is actually
 * composited under this group.
 */
export function toneBeneath(
  footprint: Rect,
  plane: GlassPlane,
  painted: readonly PaintedSurface[],
): BackdropToneSample | undefined {
  const above = GLASS_PLANES.indexOf(plane);
  let found: PaintedSurface | undefined;
  for (const surface of painted) {
    // Strictly lower plane: X1 forbids two overlapping nodes in one plane, so a
    // surface sharing this group's plane cannot be underneath it however its
    // order reads.
    if (GLASS_PLANES.indexOf(surface.plane) >= above) continue;
    if (!contains(surface.bounds, footprint)) continue;
    if (found === undefined || compareZSlot(found, surface) < 0) found = surface;
  }
  return found?.tone;
}
