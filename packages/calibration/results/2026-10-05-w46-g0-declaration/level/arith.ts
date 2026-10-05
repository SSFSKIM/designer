/**
 * W46 G0 (d): the level check's arithmetic — the WebGPU tier's W9 tone solve evaluated per cell from
 * the runtime's OWN exported functions, so the prediction is the shader's algebra and not a second
 * statement of it (charter X61; Grounding, "The transmission, as the renderer computes it").
 *
 *   cd packages/calibration
 *   pnpm exec tsx results/2026-10-05-w46-g0-declaration/level/arith.ts <input.json>
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

import {
  DEFAULT_MATERIAL_PROFILE,
  backdropToneAdaptation,
  backdropToneResponse,
  backdropToneSolveWeight,
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
const active = withMaterialOverrides(DEFAULT_MATERIAL_PROFILE, patchOf(input.endpoints.active));
const receded = withMaterialOverrides(active, patchOf(input.endpoints.receded));
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

function solve(profile: MaterialProfile, cell: Cell) {
  const tintAlpha = profile.optics.regular.tintAlpha;
  const sizeK = sizeThickness(cell.span, profile);
  const alpha = sizeOcclusionAlphaAt(tintAlpha, sizeK, profile);
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
    tintAlpha, sizeK, sizedAlpha: alpha, toneAdapt, authority, blackWeight, levelFar, response, neutral,
    solved, clamped, collapsed, alphaLift, achieved, excess: achieved - response,
  };
}

const out = input.cells.map((cell) => ({ id: cell.id, ...solve(cell.pose === "inactive" ? receded : active, cell) }));
console.log(JSON.stringify(out));
