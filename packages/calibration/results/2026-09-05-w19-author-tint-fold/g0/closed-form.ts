/**
 * W19 G0 (a) and (d) — the author-tint composite on Chromium's linear path, from the code.
 *
 * The review's scratch test (W18's post-landing review, claims §5.79 §7 addendum) found the defect
 * by hand-composing two declarations at one interior it chose. This is that test made an instrument:
 * the interior is no longer a literal but is resolved through `root.ts`'s own chain from the shipped
 * profile at each backdrop level, the sweep runs the charter's six strengths, five levels and two
 * seeds, and every quantity the findings quote is written to JSON rather than printed.
 *
 * ## The four quantities, in code terms
 *
 * All four are per channel. `E` is `srgbEncode` and `D` is `srgbDecode`; `b` is the filtered
 * backdrop in linear light that the sharp layer's reference filter sees.
 *
 *  - **`M`** — the renderer's interior composite in linear light, `(1 − α)·b + α·tint + X`, with
 *    `(α, tint)` the pair `root.ts` builds as `CssTierInterior` (the size law's occlusion before the
 *    W9 response solve, the backdrop adaptation, the inner shadow folded into the pair by
 *    `innerShadowedSourceOptics`) and `X` = `interiorBandLight`. `cssTierTintTransfer` carries
 *    exactly this triple, so `M` is `(1 − transfer.tintAlpha)·b + transfer.tintAlpha·transfer.tint
 *    + transfer.addedLight`, clamped into [0, 1] as `cssTierTintTable` clamps it.
 *  - **`T`** — the UNTINTED conversion's overlay colour: `cssOpticsFromSource(baseOptics,
 *    shadowedSource, mapping).tint / 255`, already encoded (`cssTintColor` writes an encoded
 *    Rgb255). This is what `optics.tint` would be on a surface with no author tint.
 *  - **`T_folded`** — `tintedCssOptics(cssOpticsFromSource(...), …).tint / 255`, the author layer
 *    already folded over `T` at the untinted conversion's alpha. **This is what the tier uses
 *    today**, because `root.ts` (~1918) passes those folded optics to `cssTierDeclarations` as
 *    `optics`, and the declarations take the transfer's `floorEncoded` from `optics.tint`.
 *  - **`L`** — `authorTintLayer(policySource, seed, tintBackdrop, tintGrip).color / 255`: the
 *    author's seed at the shade the material's luminance puts it at, encoded, and `s` its strength.
 *
 * With `α₃` = `cssTierFloorAlpha(optics)` = `CSS_TIER_TINT_FLOOR_ALPHA`, today's chain is
 *
 *     F(b)      = D( max(0, (E(M) − α₃·E(T_folded)) / (1 − α₃)) )     the table, in the filter
 *     composite = D( (1 − s)·E(F(b)) + s·E(L) )                        L3's rgba(L, s) over it
 *
 * against the renderer's own expression `D((1 − s)·E(M) + s·E(L))` (`tintedMaterialColour`).
 * Subtracting in encoded space the residue is exact and closed:
 *
 *     E(composite) − E(intended) = (1 − s)·α₃/(1 − α₃)·(E(M) − E(T_folded))
 *
 * which is the charter's form. It is quoted in encoded space because that is the space it is exact
 * in; the linear-luminance figure the review reported is this residue carried through `D` at the
 * intended level, and both are written per cell.
 *
 * ## (d), the exact fold
 *
 * The candidate keeps the table solved on the untinted pair `(T, α₃)` and paints on L3 the
 * encoded-space fold of `(L, s)` over that same floor overlay — `α″ = 1 − (1 − s)(1 − α₃)`,
 * `C″ = ((1 − s)·α₃·E(T) + s·E(L))/α″` — which is what `tintedCssOptics` computes when its `css`
 * argument is `{tint: T, tintAlpha: α₃}`. Both are evaluated here: the real-valued fold, which is
 * where the 1e-6 identity lives, and `tintedCssOptics`'s own output, whose channels are rounded to
 * eight bits because an `rgba()` declaration is written in eight bits. The difference between the
 * two is the declaration's quantum and is reported as such rather than folded into the identity.
 *
 * The boundary (`cssTintFormAt`) is read on both, from the declarations themselves, because the
 * charter's Design asserts the form cannot move and an assertion of that kind should be a reading.
 *
 * ## The backdrop, and why it is uniform
 *
 * Two different backdrop quantities exist (W17 G0's analytic.ts says so at length): the group's
 * SAMPLED tone, which drives the response solve and the adaptation, and the filtered backdrop under
 * the surface, which is the table's input. This study sweeps a UNIFORM grey backdrop at each level,
 * where the two coincide exactly — the encoded mean decoded and the linear mean are both `b` — so
 * one swept number is unambiguous. The captured ladder (G0 (b)) is where the two part company, and
 * it is read on the real backdrops.
 *
 * Usage, from `packages/calibration`:
 *   npx tsx results/2026-09-05-w19-author-tint-fold/g0/closed-form.ts <scenesJson> <component> <out>
 *
 * `<scenesJson>` is the bed whose component geometry the surface is taken from (W18 G0's lesson:
 * a verify script takes its bed as an argument), `<component>` a key of its `components` map.
 */

import { writeFileSync } from "node:fs";

import { NOMINAL_ACCESSIBILITY_POLICY, glassTint } from "@vitreajs/vitrea";
import { DEFAULT_MATERIAL_PROFILE, tintedMaterialColour } from "@vitrea/renderer-webgpu";
import {
  MATERIAL_OPTICS,
  cssTierDeclarations,
  cssTierFloorAlpha,
  cssTierTintTable,
  linearTint,
  resolvedTintShade,
  tintedCssOptics,
  type CssTierEngineCapabilities,
} from "@vitreajs/vitrea-web";

import { readSceneGeometry } from "../../../cli/scene-geometry";
import { resolveSurface } from "./surface";

const [, , scenesJson, componentName, outJson] = process.argv;
if (scenesJson === undefined || componentName === undefined || outJson === undefined) {
  throw new Error("usage: closed-form.ts <scenesJson> <componentName> <outJson>");
}

const STRENGTHS = [0.1, 0.2, 0.35, 0.5, 0.75, 1.0] as const;
const BACKDROPS = [0.15, 0.3, 0.45, 0.6, 0.8] as const;
const SEEDS: readonly { readonly id: string; readonly srgb: readonly [number, number, number] }[] = [
  { id: "orange", srgb: [255, 149, 0] },
  { id: "blue", srgb: [10, 132, 255] },
];

const encode = (l: number): number =>
  l <= 0.0031308 ? 12.92 * l : 1.055 * Math.pow(l, 1 / 2.4) - 0.055;
const decode = (e: number): number =>
  e <= 0.04045 ? e / 12.92 : Math.pow((e + 0.055) / 1.055, 2.4);
const clamp01 = (v: number): number => Math.min(1, Math.max(0, v));
const luma = (rgb: readonly number[]): number =>
  0.2126 * (rgb[0] as number) + 0.7152 * (rgb[1] as number) + 0.0722 * (rgb[2] as number);

/** The surface, from the bed's own declaration — the size law reads its short span. */
const geometryMatrix = readSceneGeometry(scenesJson);
const declared = geometryMatrix.components[componentName] as
  | { readonly kind: string; readonly size: readonly [number, number]; readonly radius?: number }
  | undefined;
if (declared === undefined) {
  throw new Error(`closed-form: ${scenesJson} declares no component '${componentName}'.`);
}
const widthCssPx = declared.size[0];
const heightCssPx = declared.size[1];
const radiusCssPx =
  declared.kind === "capsule" ? Math.min(widthCssPx, heightCssPx) / 2 : (declared.radius ?? 0);
// `DEFAULT_HOST_SHAPE.thickness`; the calibration pages never override it.
const thicknessCssPx = 8;
const spanPx = Math.min(widthCssPx, heightCssPx);

const CHROMIUM: CssTierEngineCapabilities = {
  referenceFilterInBackdrop: true,
  maskOnBackdropFilter: "yes",
};

const shade = resolvedTintShade();
const floorAlpha = cssTierFloorAlpha(MATERIAL_OPTICS.regular);
const box = { widthCssPx, heightCssPx, radiusCssPx, thicknessCssPx };
/** A uniform grey backdrop: the sampled tone and the filtered backdrop are one number on it. */
const toneAt = (b: number) => ({ rgb: [b, b, b] as const, luminance: b, linearLuminance: b });

/** The table `css-tier-layers.ts` samples, and its own linear interpolation, for one channel. */
function tableOf(interior: CssTierInterior, channel: 0 | 1 | 2, floorEncoded: number): (b: number) => number {
  const values = cssTierTintTable({
    tintAlpha: interior.tintAlpha,
    tint: interior.tint[channel],
    addedLight: interior.addedLight,
    floorAlpha,
    floorEncoded,
  });
  return (b: number): number => {
    const x = clamp01(b) * (values.length - 1);
    const i = Math.min(Math.floor(x), values.length - 2);
    return (values[i] as number) + (x - i) * ((values[i + 1] as number) - (values[i] as number));
  };
}

const rows: unknown[] = [];
const foldChecks: { encodedIdentity: number; linearIdentity: number; quantisedLinear: number; alphaMargin: number } = {
  encodedIdentity: 0,
  linearIdentity: 0,
  quantisedLinear: 0,
  alphaMargin: Number.POSITIVE_INFINITY,
};
const formFlips: unknown[] = [];
const fullStrengthDeclarations: unknown[] = [];

for (const seed of SEEDS) {
  for (const s of STRENGTHS) {
    const tint = glassTint(seed.srgb.map((v) => v / 255) as never, s);
    const seedLinear = linearTint(tint);
    for (const b of BACKDROPS) {
      const r = resolveSurface(box, toneAt(b), seedLinear as never);
      const author = r.authorLayer;
      if (author === undefined) throw new Error("closed-form: the author layer resolved to nothing.");

      // TODAY: root.ts hands the declarations the FOLDED optics, so the transfer's floorEncoded is
      // T_folded and L3 paints rgba(L, s).
      const today = cssTierDeclarations({
        radii: [radiusCssPx, radiusCssPx, radiusCssPx, radiusCssPx],
        optics: r.folded,
        tint,
        policy: NOMINAL_ACCESSIBILITY_POLICY,
        spanPx,
        extentsCssPx: [widthCssPx, heightCssPx],
        filterIdPrefix: "w19",
        engine: CHROMIUM,
        interior: r.interior,
        authorLayer: author as never,
        backdropLuminance: b,
      });
      // THE FOLD: the same declarations over the UNTINTED optics — which is the whole of the change
      // to the table — with L3 taking the fold of (L, s) over (T, α₃).
      const candidate = cssTierDeclarations({
        radii: [radiusCssPx, radiusCssPx, radiusCssPx, radiusCssPx],
        optics: r.untinted,
        tint,
        policy: NOMINAL_ACCESSIBILITY_POLICY,
        spanPx,
        extentsCssPx: [widthCssPx, heightCssPx],
        filterIdPrefix: "w19",
        engine: CHROMIUM,
        interior: r.interior,
        authorLayer: author as never,
        backdropLuminance: b,
      });
      const todayTransfer = today.body.tintTransfer;
      const candidateTransfer = candidate.body.tintTransfer;
      if (todayTransfer === undefined || candidateTransfer === undefined) {
        throw new Error(`closed-form: no transfer at s=${String(s)} b=${String(b)} — the form is not linear.`);
      }
      if (today.body.tintForm !== candidate.body.tintForm) {
        formFlips.push({ seed: seed.id, s, b, today: today.body.tintForm, candidate: candidate.body.tintForm });
      }

      // `tintedCssOptics` with the floor overlay as its base is the fold, verbatim.
      const foldedOverlay = tintedCssOptics(
        { ...r.untinted, tintAlpha: floorAlpha },
        r.policySource,
        seedLinear as never,
        b,
        r.grip,
        shade,
      );
      const alphaDoublePrime = 1 - (1 - s) * (1 - floorAlpha);
      foldChecks.alphaMargin = Math.min(foldChecks.alphaMargin, foldedOverlay.tintAlpha - floorAlpha);

      const actual: number[] = [];
      const intended: number[] = [];
      const foldReal: number[] = [];
      const foldQuantised: number[] = [];
      const closed: number[] = [];
      const perChannel: unknown[] = [];
      for (const c of [0, 1, 2] as const) {
        const eM = encode(
          clamp01((1 - todayTransfer.tintAlpha) * b + todayTransfer.tintAlpha * todayTransfer.tint[c] + todayTransfer.addedLight),
        );
        const eT = candidateTransfer.floorEncoded[c];
        const eTFolded = todayTransfer.floorEncoded[c];
        const eL = (author.color[c] as number) / 255;

        const F = tableOf(r.interior, c, eTFolded);
        const eActual = (1 - s) * encode(F(b)) + s * eL;
        const eIntended = (1 - s) * eM + s * eL;
        // The fold, real-valued: the identity's own arithmetic.
        const cReal = ((1 - s) * floorAlpha * eT + s * eL) / alphaDoublePrime;
        const Fc = tableOf(r.interior, c, eT);
        const eFoldReal = (1 - alphaDoublePrime) * encode(Fc(b)) + alphaDoublePrime * cReal;
        // The fold as `tintedCssOptics` writes it, in eight bits.
        const cQuantised = (foldedOverlay.tint[c] as number) / 255;
        const eFoldQuantised = (1 - foldedOverlay.tintAlpha) * encode(Fc(b)) + foldedOverlay.tintAlpha * cQuantised;

        actual.push(decode(clamp01(eActual)));
        intended.push(decode(clamp01(eIntended)));
        foldReal.push(decode(clamp01(eFoldReal)));
        foldQuantised.push(decode(clamp01(eFoldQuantised)));
        closed.push(((1 - s) * floorAlpha * (eM - eTFolded)) / (1 - floorAlpha));
        perChannel.push({
          channel: c,
          eM,
          eT,
          eTFolded,
          eL,
          tableToday: F(b),
          tableCandidate: Fc(b),
          encodedError: eActual - eIntended,
          encodedClosedForm: ((1 - s) * floorAlpha * (eM - eTFolded)) / (1 - floorAlpha),
          encodedResidual: eActual - eIntended - ((1 - s) * floorAlpha * (eM - eTFolded)) / (1 - floorAlpha),
          linearError: decode(clamp01(eActual)) - decode(clamp01(eIntended)),
          foldEncodedErrorReal: eFoldReal - eIntended,
          foldEncodedErrorQuantised: eFoldQuantised - eIntended,
        });
        foldChecks.encodedIdentity = Math.max(foldChecks.encodedIdentity, Math.abs(eFoldReal - eIntended));
        foldChecks.linearIdentity = Math.max(
          foldChecks.linearIdentity,
          Math.abs(decode(clamp01(eFoldReal)) - decode(clamp01(eIntended))),
        );
        foldChecks.quantisedLinear = Math.max(
          foldChecks.quantisedLinear,
          Math.abs(decode(clamp01(eFoldQuantised)) - decode(clamp01(eIntended))),
        );
      }

      // The renderer's own law, at the same material and the same grip — its shade is read off the
      // material's per-pixel luminance where this tier reads one level per source, so this is the
      // renderer's number and not a restatement of `intended`.
      const materialLinear: [number, number, number] = [0, 1, 2].map((c) =>
        clamp01(
          (1 - todayTransfer.tintAlpha) * b +
            todayTransfer.tintAlpha * (todayTransfer.tint[c as 0] as number) +
            todayTransfer.addedLight,
        ),
      ) as [number, number, number];
      const renderer = tintedMaterialColour(
        materialLinear,
        { color: seedLinear.color as never, strength: s },
        r.grip,
        DEFAULT_MATERIAL_PROFILE,
      );

      if (s === 1) {
        fullStrengthDeclarations.push({
          seed: seed.id,
          b,
          todayOverlay: today.layers?.overlay["background-color"],
          candidateOverlay: `rgba(${String(foldedOverlay.tint[0])}, ${String(foldedOverlay.tint[1])}, ${String(foldedOverlay.tint[2])}, ${String(foldedOverlay.tintAlpha)})`,
          alphaDoublePrime: foldedOverlay.tintAlpha,
          transferIdentical:
            JSON.stringify(todayTransfer.floorEncoded) === JSON.stringify(candidateTransfer.floorEncoded),
        });
      }

      rows.push({
        seed: seed.id,
        strength: s,
        backdrop: b,
        paintedAlphaToday: s,
        underFloorToday: s < floorAlpha,
        alphaDoublePrime: foldedOverlay.tintAlpha,
        form: today.body.tintForm,
        formCandidate: candidate.body.tintForm,
        compositeLevelForForm:
          (1 - r.interior.tintAlpha) * b + r.interior.tintAlpha * luma(r.interior.tint) + r.interior.addedLight,
        interior: { tintAlpha: r.interior.tintAlpha, tint: r.interior.tint, addedLight: r.interior.addedLight },
        luminance: {
          actualToday: luma(actual),
          intended: luma(intended),
          renderer: luma(renderer),
          foldReal: luma(foldReal),
          foldQuantised: luma(foldQuantised),
          errorToday: luma(actual) - luma(intended),
          errorTodayAgainstRenderer: luma(actual) - luma(renderer),
          rendererAgainstIntended: luma(renderer) - luma(intended),
          errorFoldReal: luma(foldReal) - luma(intended),
          errorFoldQuantised: luma(foldQuantised) - luma(intended),
          closedFormEncodedLuma: luma(closed),
        },
        perChannel,
      });
    }
  }
}

const summary = {
  scenesJson,
  componentName,
  surface: { widthCssPx, heightCssPx, radiusCssPx, thicknessCssPx, spanPx },
  floorAlpha,
  strengths: STRENGTHS,
  backdrops: BACKDROPS,
  seeds: SEEDS.map((s) => s.id),
  foldIdentity: {
    worstEncodedRealValued: foldChecks.encodedIdentity,
    worstLinearRealValued: foldChecks.linearIdentity,
    worstLinearEightBitDeclaration: foldChecks.quantisedLinear,
    leastAlphaMarginOverFloor: foldChecks.alphaMargin,
  },
  formFlips,
  fullStrengthDeclarations,
  worstTodayLinearError: rows.reduce(
    (worst, row) => Math.max(worst, Math.abs((row as { luminance: { errorToday: number } }).luminance.errorToday)),
    0,
  ),
  worstClosedFormResidualEncoded: rows.reduce((worst, row) => {
    for (const c of (row as { perChannel: { encodedResidual: number }[] }).perChannel) {
      worst = Math.max(worst, Math.abs(c.encodedResidual));
    }
    return worst;
  }, 0),
  rows,
};

writeFileSync(outJson, `${JSON.stringify(summary, null, 2)}\n`);
process.stdout.write(
  `${String(rows.length)} cells -> ${outJson}\n` +
    `fold identity: encoded ${summary.foldIdentity.worstEncodedRealValued.toExponential(2)}, ` +
    `linear ${summary.foldIdentity.worstLinearRealValued.toExponential(2)}, ` +
    `eight-bit declaration ${summary.foldIdentity.worstLinearEightBitDeclaration.toExponential(2)}\n` +
    `least α″ − α₃: ${summary.foldIdentity.leastAlphaMarginOverFloor.toExponential(2)}; ` +
    `form flips: ${String(formFlips.length)}\n` +
    `worst |today − intended| in linear luminance: ${summary.worstTodayLinearError.toFixed(6)}; ` +
    `worst closed-form residual (encoded): ${summary.worstClosedFormResidualEncoded.toExponential(2)}\n`,
);
