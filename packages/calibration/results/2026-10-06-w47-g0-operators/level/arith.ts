/**
 * W47 G0 (e): W46 G0's level arithmetic (`results/2026-10-05-w46-g0-declaration/level/arith.ts`), ported
 * by copy for W47 and taught operator 1 (charter Design "Operator 1", X61, X65): the alpha the W9
 * solve runs at is now
 *
 *   farS        smoothstep(sizeSpanMax, scatterSpanMaxAtScale(dpr), span)    (the far curve, in hand)
 *   alphaBase   clamp(tintAlpha + tintAlphaFarAtScale(dpr) · farS, 0, 1)      (operator 1)
 *   sizedAlpha  sizeOcclusionAlphaAt(alphaBase, sizeK)                       (the existing form)
 *
 * with `tintAlphaFarAtScale` the runtime's own export once operator 1 merges. On a runtime without it
 * a document at identity evaluates exactly as W46's (alphaBase = tintAlpha) and a non-zero delta
 * refuses as WAITING. Each cell reports `farS`, `farDelta`, `alphaBase` and which path evaluated it.
 *
 * W46 G0's text follows, unchanged; the `sizedAlpha` line below is now taken at `alphaBase`.
 *
 * W46 G0 (d): the level check's arithmetic — the WebGPU tier's W9 tone solve evaluated per cell from
 * the runtime's OWN exported functions, so the prediction is the shader's algebra and not a second
 * statement of it (charter X61; Grounding, "The transmission, as the renderer computes it").
 *
 *   cd packages/calibration
 *   pnpm exec tsx results/2026-10-06-w47-g0-operators/level/arith.ts <input.json>
 *
 * Input: `{ "endpoints": { "active": <document path>, "receded": <document path> },
 *           "cells": [ { "id", "pose": "rest"|"inactive", "span", "encoded", "linear" } ] }`
 * where `encoded` is the backdrop's encoded-space mean (the solve's `encodedInput`) and `linear` its
 * linear mean (`toneLinearMean`), both supplied by the caller from the background fixture.
 *
 * Per cell, under the endpoint the pose draws (the receded resolved over its active):
 *   sizeK       `sizeThickness(span)`                         (the size law's one input)
 *   sizedAlpha  `sizeOcclusionAlphaAt(tintAlpha, sizeK)`       (tintAlpha + gain·sizeK·(1 − tintAlpha))
 *   toneAdapt   `backdropToneAdaptation(linear, sizeK)`        (the collapse; owns the pixel at ≥ 0.995)
 *   authority   `backdropToneSolveWeight(encoded)`             (the fade below the dark anchor, W36's
 *                                                               black branch restoring it near black)
 *   response    `backdropToneResponse(encoded, sizeK, …, levelFar)` — the composite TARGET
 *   neutral     the resolved `optics.regular.tint` luma (the dark scheme's adaptive tint equals it)
 * and the solve as the shader writes it (`wgsl/optics.ts`, the W9 block):
 *   preCollapse = (response − toneAdapt·linear)/(1 − toneAdapt)
 *   shift       = (preCollapse − ((1 − α)·linear + α·neutral))/α · authority
 *   solved      = clamp(neutral + shift, 0, 1)            — `clamped` when the lower clamp bites
 *   achieved    = (1 − α′)·linear + α′·solved             — the composite mean the solve reaches, α′ the
 *                                                          sizedAlpha after the one-sided opacity lift
 *   excess      = achieved − response                     (> 0 where the clamp or the authority
 *                                                          leaves the composite above its target)
 * The one-sided lightward opacity solve is applied as the shader applies it (`alphaLift`, α′ = α + alphaLift);
 * it never acts below the target. This is a PREDICTION from group means: the rendered interior also carries the scatter,
 * the rim, the tint shade and the chroma retention, which the check reads off the rows instead.
 */

import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import * as runtime from "@vitrea/renderer-webgpu";
import {
  DEFAULT_MATERIAL_PROFILE,
  backdropToneAdaptation,
  backdropToneResponse,
  backdropToneSolveWeight,
  scatterSpanMaxAtScale,
  sizeOcclusionAlphaAt,
  sizeThickness,
  sizeToneLevelFar,
  withMaterialOverrides,
  type MaterialProfile,
  type MaterialProfilePatch,
} from "@vitrea/renderer-webgpu";

type Cell = { id: string; pose: "rest" | "inactive"; span: number; encoded: number; linear: number; dpr?: number };
const input = JSON.parse(readFileSync(resolve(process.argv[2]!), "utf8")) as {
  endpoints: { active: string; receded: string };
  cells: Cell[];
};
const patchOf = (path: string): MaterialProfilePatch =>
  (JSON.parse(readFileSync(resolve(path), "utf8")) as { patch: MaterialProfilePatch }).patch;
const activePatch = patchOf(input.endpoints.active);
const recededPatch = patchOf(input.endpoints.receded);
const active = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, activePatch);
const receded = withMaterialOverrides(active, recededPatch);
// W36's black-branch weight, for the record only (the runtime does not export it; `authority` and
// `response` above already fold it, through the runtime's own functions): the same expression as
// `backdropToneBlackWeight` in material.ts, its join 0.003.
const smooth = (a: number, b: number, x: number): number => {
  const t = Math.min(1, Math.max(0, (x - a) / (b - a)));
  return t * t * (3 - 2 * t);
};
const backdropToneBlackWeight = (encoded: number, profile: MaterialProfile): number =>
  profile.backdropToneBlackStrength <= 0 || encoded >= 0.003 ? 0
    : Math.min(1, Math.max(0, profile.backdropToneBlackStrength)) * (1 - smooth(0, 0.003, encoded));
const luma = (rgb: readonly number[]): number => 0.2126 * rgb[0]! + 0.7152 * rgb[1]! + 0.0722 * rgb[2]!;

// W47 operator 1 (charter Design "Operator 1", X65): the far delta at the cell's scale, through the
// runtime's own export once operator 1 lands (`tintAlphaFarAtScale`, the `rampAtScale` of the two
// leaves). Before then the runtime has no such leaf: a document naming a NON-ZERO delta cannot be
// evaluated, and refuses as WAITING rather than reading the delta as 0; at identity (the leaves
// absent or 0) the delta is 0 and `alphaBase` is `tintAlpha` exactly, which is what the inert leaf
// promises.
type FarAtScale = (profile: MaterialProfile, devicePixelRatio: number) => number;
const tintAlphaFarAtScale = (runtime as unknown as { tintAlphaFarAtScale?: FarAtScale }).tintAlphaFarAtScale;
const OPERATOR_1 = tintAlphaFarAtScale === undefined ? "absent (identity only)" : "runtime";
function farDelta(profile: MaterialProfile, dpr: number): number {
  return tintAlphaFarAtScale === undefined ? 0 : tintAlphaFarAtScale(profile, dpr);
}
/** Before operator 1 merges, `withMaterialOverrides` does not carry a leaf the runtime does not know,
 *  so the resolved profile cannot show a delta a document names: the PATCHES are read for it. */
function requireOperator1(patches: Record<string, MaterialProfilePatch>): void {
  if (tintAlphaFarAtScale !== undefined) return;
  for (const [endpoint, patch] of Object.entries(patches)) {
    for (const key of ["tintAlphaFar1x", "tintAlphaFar2x"]) {
      const value = (patch as Record<string, unknown>)[key];
      if (value !== undefined && value !== 0) {
        throw new Error(`WAITING: the ${endpoint} document names ${key} ${String(value)}, and this runtime exports no ` +
          "tintAlphaFarAtScale (operator 1 not merged); only the identity is evaluated");
      }
    }
  }
}
/** farS: the far curve the optics pass reads per pixel, `smoothstep(sizeSpanMax, sizeScatterSpanMax(dpr), span)`. */
const farCurve = (span: number, profile: MaterialProfile, dpr: number): number =>
  smooth(profile.sizeSpanMax, scatterSpanMaxAtScale(profile, dpr), span);
/** alphaBase = clamp(tintAlpha + tintAlphaFarAtScale · farS, 0, 1), before the occlusion term. Where the
 *  runtime exports its CPU statement of the law (`spanGradedTintAlpha`, the expression the CSS tier's
 *  `materialAtBackdrop` applies before `sizeOcclusionAlphaAt`), alphaBase is taken from it, so the check
 *  composes the operator exactly as the runtime does; the local expression is the identity-only path. */
type SpanGraded = (alpha: number, spanPx: number, profile: MaterialProfile, devicePixelRatio: number) => number;
const spanGradedTintAlpha = (runtime as unknown as { spanGradedTintAlpha?: SpanGraded }).spanGradedTintAlpha;
const alphaBaseAt = (profile: MaterialProfile, span: number, dpr: number) => {
  const farS = farCurve(span, profile, dpr);
  const delta = farDelta(profile, dpr);
  const alpha = profile.optics.regular.tintAlpha;
  const alphaBase = spanGradedTintAlpha !== undefined ? spanGradedTintAlpha(alpha, span, profile, dpr)
    : Math.min(1, Math.max(0, alpha + delta * farS));
  return { farS, farDelta: delta, alphaBase };
};

function solve(profile: MaterialProfile, cell: Cell) {
  const tintAlpha = profile.optics.regular.tintAlpha;
  const sizeK = sizeThickness(cell.span, profile);
  const { farS, farDelta: delta, alphaBase } = alphaBaseAt(profile, cell.span, cell.dpr ?? 1);
  const alpha = sizeOcclusionAlphaAt(alphaBase, sizeK, profile);
  const toneAdapt = backdropToneAdaptation(cell.linear, sizeK, profile);
  const authority = backdropToneSolveWeight(cell.encoded, profile);
  const blackWeight = backdropToneBlackWeight(cell.encoded, profile);
  const levelFar = sizeToneLevelFar(cell.span, profile, cell.dpr ?? 1);
  const response = backdropToneResponse(cell.encoded, sizeK, profile, levelFar);
  const neutral = luma(profile.optics.regular.tint);
  const collapsed = toneAdapt >= 0.995;
  let solved = neutral;
  let clamped = false;
  let alphaLift = 0;
  let achieved = (1 - alpha) * cell.linear + alpha * neutral;
  if (!collapsed && alpha > 1e-3 && authority > 0) {
    const pre = (response - toneAdapt * cell.linear) / (1 - toneAdapt);
    const nominal = (1 - alpha) * cell.linear + alpha * neutral;
    const raw = neutral + ((pre - nominal) / alpha) * authority;
    solved = Math.min(1, Math.max(0, raw));
    clamped = raw < 0;
    achieved = (1 - alpha) * cell.linear + alpha * solved;
    if (pre > achieved + 1e-4 && solved > cell.linear + 1e-3) {
      // The shader's one-sided lightward opacity solve: solvedAlpha = mix(sizedAlpha, target,
      // authority · strength), and the composite is drawn at solvedAlpha (the review of G0's level
      // check, P2: the lift was computed and not applied).
      const target = Math.min(1, Math.max(alpha, (pre - cell.linear) / (solved - cell.linear)));
      alphaLift = (target - alpha) * authority;
      achieved = (1 - (alpha + alphaLift)) * cell.linear + (alpha + alphaLift) * solved;
    }
  }
  return {
    tintAlpha, farS, farDelta: delta, alphaBase, operator1: OPERATOR_1, sizeK, sizedAlpha: alpha, toneAdapt, authority, blackWeight, levelFar, response, neutral,
    solved, clamped, collapsed, alphaLift, achieved, excess: achieved - response,
  };
}

requireOperator1({ active: activePatch, receded: recededPatch });
const out = input.cells.map((cell) => ({ id: cell.id, ...solve(cell.pose === "inactive" ? receded : active, cell) }));
console.log(JSON.stringify(out));
