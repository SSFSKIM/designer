/**
 * The author tint's fold over the contrast floor, on the `linear` form (W19 G1;
 * charter `docs/doperpowers/specs/2026-09-05-w19-author-tint-fold.md` Decision
 * Log 2, claims §5.80 §7).
 *
 * Five claims, and they are five different kinds.
 *
 *  - **The identity.** What the tier declares composites to the renderer's own
 *    expression `(1 − s)·E(M) + s·E(L)` at every strength, not only at `s = 1`.
 *    It is asserted by composing the declarations themselves — the table the
 *    transfer names, sampled and interpolated the way `css-tier-layers.ts`
 *    builds it, then L3's overlay over it — rather than by re-deriving the
 *    algebra, because the algebra is what is under test. In real arithmetic it
 *    holds to 1e−6; written as a CSS colour it holds to the eight-bit quantum,
 *    which is what the second tolerance below is.
 *  - **The table stays inside its range.** `cssTierTintTable` clamps into [0, 1]
 *    because an `feComponentTransfer` cannot carry anything else, and the clamp
 *    fires inside the filter before the heavy layer's Gaussian, so it is not
 *    recoverable from the composite. Solved on the folded colour it fired on the
 *    seed's darkest channel over most of the ladder (claims §5.80 §2 (iv)); the
 *    pin is that on the untinted colour the argument is in range on every rung.
 *  - **The floor holds.** `α″ ≥ α₃` on every tinted declaration — W17 Decision
 *    Log 4 (a)'s doctrine, which the previous form broke below `s = 0.2668`.
 *  - **Nothing else moved.** `w19-pre-fold-declarations.json` was recorded by
 *    walking `foldCases()` on the tree as it stood before this change. Every
 *    case replayed WITHOUT `untintedOptics` must return it byte for byte, every
 *    `encoded`-form and plain-`blur()` case must return it WITH the field too,
 *    and at `s = 1` the `linear` form's L3 declaration must return it as well —
 *    at full strength the fold IS the opaque layer the tier drew.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

import { cssTierDeclarations } from "../src/css-tier";
import { cssTierTintTable } from "../src/optics";
import { FLOOR_ALPHA, foldCases } from "./w19-fold-cases";

const RECORDED = JSON.parse(
  readFileSync(resolve(import.meta.dirname, "w19-pre-fold-declarations.json"), "utf8"),
) as Record<string, unknown>;

const encode = (l: number): number =>
  l <= 0.0031308 ? l * 12.92 : 1.055 * l ** (1 / 2.4) - 0.055;
const clamp01 = (v: number): number => Math.min(1, Math.max(0, v));

/** `rgba(r, g, b, a)` back into its four numbers, as the page would read it. */
function parseRgba(declaration: string): { rgb: [number, number, number]; alpha: number } {
  const parts = /^rgba\(([-\d.]+), ([-\d.]+), ([-\d.]+), ([-\d.]+)\)$/.exec(declaration);
  if (parts === null) throw new Error(`not an rgba() declaration: ${declaration}`);
  return {
    rgb: [Number(parts[1]), Number(parts[2]), Number(parts[3])],
    alpha: Number(parts[4]),
  };
}

/**
 * The table at one backdrop level, sampled and interpolated exactly as the tier's
 * own `<feComponentTransfer type="table">` is — the filter looks the value up in
 * the same array and interpolates linearly between the two nearest points.
 */
function tableAt(
  transfer: {
    tintAlpha: number;
    tint: readonly [number, number, number];
    addedLight: number;
    floorAlpha: number;
    floorEncoded: readonly [number, number, number];
  },
  channel: 0 | 1 | 2,
  backdrop: number,
): number {
  const values = cssTierTintTable({
    tintAlpha: transfer.tintAlpha,
    tint: transfer.tint[channel],
    addedLight: transfer.addedLight,
    floorAlpha: transfer.floorAlpha,
    floorEncoded: transfer.floorEncoded[channel],
  });
  const x = clamp01(backdrop) * (values.length - 1);
  const index = Math.min(Math.floor(x), values.length - 2);
  return values[index]! + (x - index) * (values[index + 1]! - values[index]!);
}

const CASES = foldCases();
const LINEAR_TINTED = CASES.filter((c) => c.form === "linear" && c.seed !== "none");

describe("the author tint folded over the contrast floor (W19 G1)", () => {
  it("composites to the renderer's expression at every strength, to 1e-6", () => {
    /*
     * `(1 − α″)·F(b) + α″·C″ = (1 − s)·E(M) + s·E(L)`, per channel, where `F` is
     * the table the declarations name and `E(M)` is the interior composite that
     * same transfer carries. The left side is composed from what the tier
     * declared; the right is the renderer's own expression, and nothing on
     * either side is a restatement of the other.
     *
     * Twice, at two tolerances. In real arithmetic — the fold's own `α″` and
     * `C″` before either is written down — the identity is exact and the bound
     * is 1e−6. As the declaration writes them, `C″` is rounded to `Rgb255` and
     * `α″` to a thousandth, and the identity holds to the eight-bit quantum
     * instead: 2.85e−3, the same quantum `rgba(L, s)` carried before the change
     * (claims §5.80 §3), which is why no clause on a tinted cell sits under it.
     */
    let worstReal = 0;
    let worstDeclared = 0;
    for (const c of LINEAR_TINTED) {
      const render = cssTierDeclarations({ ...c.args, untintedOptics: c.resolved.untinted });
      expect(render.body.tintForm, c.name).toBe("linear");
      const transfer = render.body.tintTransfer;
      const overlay = render.layers?.overlay["background-color"];
      if (transfer === undefined || overlay === undefined) {
        throw new Error(`${c.name}: the linear form declared no transfer or no overlay`);
      }
      const declared = parseRgba(overlay);
      const alphaReal = 1 - (1 - c.strength) * (1 - FLOOR_ALPHA);
      const author = c.args.authorLayer!;
      for (const channel of [0, 1, 2] as const) {
        const material = encode(
          clamp01(
            (1 - transfer.tintAlpha) * c.backdrop +
              transfer.tintAlpha * transfer.tint[channel] +
              transfer.addedLight,
          ),
        );
        const floorEncoded = transfer.floorEncoded[channel];
        const layerEncoded = author.color[channel] / 255;
        const table = encode(tableAt(transfer, channel, c.backdrop));
        const target = (1 - c.strength) * material + c.strength * layerEncoded;

        const colourReal =
          ((1 - c.strength) * FLOOR_ALPHA * floorEncoded + c.strength * layerEncoded) / alphaReal;
        worstReal = Math.max(
          worstReal,
          Math.abs((1 - alphaReal) * table + alphaReal * colourReal - target),
        );
        worstDeclared = Math.max(
          worstDeclared,
          Math.abs(
            (1 - declared.alpha) * table + declared.alpha * (declared.rgb[channel] / 255) - target,
          ),
        );
      }
    }
    expect(worstReal).toBeLessThan(1e-6);
    expect(worstDeclared).toBeLessThan(3e-3);
  });

  it("never asks the transfer table for a value outside its range", () => {
    // The table's argument is `(E(M) − α₃·E(T))/(1 − α₃)`; `cssTierTintTable`
    // clamps it, and a clamped table is not affine, so a saturating channel's
    // loss fires per pixel before L2's Gaussian and cannot be undone downstream.
    for (const c of LINEAR_TINTED) {
      const render = cssTierDeclarations({ ...c.args, untintedOptics: c.resolved.untinted });
      const transfer = render.body.tintTransfer!;
      for (const channel of [0, 1, 2] as const) {
        const material = encode(
          clamp01(
            (1 - transfer.tintAlpha) * c.backdrop +
              transfer.tintAlpha * transfer.tint[channel] +
              transfer.addedLight,
          ),
        );
        const argument =
          (material - transfer.floorAlpha * transfer.floorEncoded[channel]) /
          (1 - transfer.floorAlpha);
        expect(argument, `${c.name} channel ${String(channel)}`).toBeGreaterThanOrEqual(0);
        expect(argument, `${c.name} channel ${String(channel)}`).toBeLessThanOrEqual(1);
      }
    }
  });

  it("keeps L3 at or above the contrast floor at every strength", () => {
    // W17 Decision Log 4 (a). The previous form painted the author's own opacity
    // on L3, which is under the floor for every `s < α₃` — measured on six of the
    // eighteen captured tinted cells of G0's ladder.
    let leastMargin = Number.POSITIVE_INFINITY;
    for (const c of LINEAR_TINTED) {
      const render = cssTierDeclarations({ ...c.args, untintedOptics: c.resolved.untinted });
      const alpha = parseRgba(render.layers!.overlay["background-color"]!).alpha;
      expect(alpha, c.name).toBeGreaterThanOrEqual(FLOOR_ALPHA);
      leastMargin = Math.min(leastMargin, alpha - FLOOR_ALPHA);
    }
    // At `s = 0.1`, the ladder's lowest rung: `α″ = 0.34012`, written 0.34.
    expect(leastMargin).toBeGreaterThanOrEqual(0.073);
  });

  it("draws today's opaque layer at full strength, byte for byte", () => {
    // At `s = 1` the fold degenerates to the author's layer, so the declaration
    // the tier writes on L3 is the one it wrote before this change — which is why
    // every full-strength cell of the bed is insensitive to the whole wave.
    for (const c of LINEAR_TINTED.filter((entry) => entry.strength === 1)) {
      const render = cssTierDeclarations({ ...c.args, untintedOptics: c.resolved.untinted });
      const recorded = RECORDED[c.name] as { layers: { overlay: Record<string, string> } };
      expect(render.layers?.overlay, c.name).toEqual(recorded.layers.overlay);
    }
  });

  it("leaves the encoded form and the plain-blur engines exactly where they were", () => {
    // Contract X9. Both paths keep `tintedCssOptics`' whole-material fold on
    // `optics`, and passing `untintedOptics` beside it must change nothing they
    // declare — asserted over the whole declaration rather than over the overlay,
    // because "nothing" is the claim.
    for (const c of CASES.filter((entry) => entry.form !== "linear")) {
      const render = cssTierDeclarations({ ...c.args, untintedOptics: c.resolved.untinted });
      expect(render, c.name).toEqual(RECORDED[c.name]);
    }
  });

  it("gives a caller that passes no untinted conversion today's declarations", () => {
    // The field is optional and its absence is not an error: a direct caller has
    // said nothing about which of the two colours its `optics` holds, so it keeps
    // the behaviour it had. Every case on the bed, all three forms, tinted and
    // untinted.
    for (const c of CASES) {
      expect(cssTierDeclarations(c.args), c.name).toEqual(RECORDED[c.name]);
    }
  });

  it("leaves an untinted surface's declarations untouched by the new field", () => {
    // The change touches only surfaces with an author layer: with no tint the
    // untinted conversion IS `optics`, so the transfer's floor colour and L3's
    // overlay are the ones the tier already wrote.
    for (const c of CASES.filter((entry) => entry.seed === "none")) {
      const render = cssTierDeclarations({ ...c.args, untintedOptics: c.resolved.untinted });
      expect(render, c.name).toEqual(RECORDED[c.name]);
    }
  });
});
