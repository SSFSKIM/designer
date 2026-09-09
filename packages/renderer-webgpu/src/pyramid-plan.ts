/**
 * How large a backdrop's pyramid is, and which level each consumer reads —
 * decided on the CPU, in one pure function, before any texture exists.
 *
 * §Performance envelope: "Effect-texture resolution is decoupled from DOM DPR."
 * That decoupling lives here: level 0 is the *source's* size scaled by the
 * resolution policy and capped by `maxDimension`, never the viewport's device
 * pixel count. A 4K video behind a 390-px-wide phone viewport does not get a 4K
 * pyramid, and a governor that halves `scale` halves the whole chain's cost
 * without touching a shader.
 *
 * ## Level count
 *
 * The chain stops when the shorter side would fall below `MIN_LEVEL_EXTENT`. Below
 * about 8 px a level carries no usable structure and the bilinear taps of the
 * 13-tap downsample start reading mostly clamped edge, so the levels past that
 * point cost bandwidth and add nothing. That also bounds the maximum LOD the
 * optics pass may ask for, which is why `maxLod` is part of the plan rather than
 * computed in the shader.
 *
 * ## The analysis level
 *
 * Not the coarsest: the coarsest level has had every edge blurred out of it, so an
 * edge-density measurement there would report the same small number for a
 * photograph and for a flat colour. The plan picks the level nearest
 * `ANALYSIS_TARGET_EXTENT`, which keeps the measurement's spatial frequency band
 * fixed as the source's resolution changes — a stat that moved when the
 * resolution policy moved would make the governor's own degradation look like a
 * change in the backdrop.
 */

export const MIN_LEVEL_EXTENT = 8;
export const MAX_CHAIN_LEVELS = 12;
/** Shorter-side extent the analysis level aims for. */
export const ANALYSIS_TARGET_EXTENT = 96;

export interface PyramidPlan {
  /** Level 0 size in texture px. */
  readonly width: number;
  readonly height: number;
  readonly levelCount: number;
  /** The highest LOD the optics pass may sample: `levelCount - 1`. */
  readonly maxLod: number;
  /** Which level the analysis reduction reads. */
  readonly analysisLevel: number;
  /** Per-level sizes, index 0 = level 0. */
  readonly levels: readonly { readonly width: number; readonly height: number }[];
}

export interface ResolutionPolicyView {
  readonly scale: number;
  readonly maxDimension: number;
}

export function planPyramid(
  sourceWidth: number,
  sourceHeight: number,
  policy: ResolutionPolicyView,
): PyramidPlan {
  const scale = Math.max(policy.scale, 1e-3);
  let width = Math.max(1, Math.round(sourceWidth * scale));
  let height = Math.max(1, Math.round(sourceHeight * scale));

  const cap = Math.max(MIN_LEVEL_EXTENT, Math.floor(policy.maxDimension));
  const longest = Math.max(width, height);
  if (longest > cap) {
    const shrink = cap / longest;
    width = Math.max(1, Math.round(width * shrink));
    height = Math.max(1, Math.round(height * shrink));
  }

  const levels: { width: number; height: number }[] = [{ width, height }];
  while (levels.length < MAX_CHAIN_LEVELS) {
    const previous = levels[levels.length - 1] as { width: number; height: number };
    const next = {
      width: Math.max(1, previous.width >> 1),
      height: Math.max(1, previous.height >> 1),
    };
    if (Math.min(next.width, next.height) < MIN_LEVEL_EXTENT) break;
    if (next.width === previous.width && next.height === previous.height) break;
    levels.push(next);
  }

  // Nearest level to the analysis target on the shorter side, in log space so
  // "nearest" means nearest by octave rather than by pixel count.
  let analysisLevel = 0;
  let bestDistance = Number.POSITIVE_INFINITY;
  for (let i = 0; i < levels.length; i += 1) {
    const level = levels[i] as { width: number; height: number };
    const shorter = Math.min(level.width, level.height);
    const distance = Math.abs(Math.log2(shorter / ANALYSIS_TARGET_EXTENT));
    if (distance < bestDistance) {
      bestDistance = distance;
      analysisLevel = i;
    }
  }

  return {
    width,
    height,
    levelCount: levels.length,
    maxLod: levels.length - 1,
    analysisLevel,
    levels,
  };
}

/**
 * The chain LOD whose blur is nearest σ, and the residual σ the separable pass
 * still has to apply on top of it.
 *
 * The 13-tap downsample's effective σ roughly doubles per level and is about 1.2
 * source texels at level 1; the constant is advisory (calibration-delegated like
 * every other optical number here) and exists so the body blur lands on the
 * material's σ rather than on the nearest power of two.
 */
export const CHAIN_SIGMA_AT_LEVEL_1 = 1.2;

/**
 * The **continuous** chain level whose blur is σ level-0 texels — the same
 * doubling `bodyBlurPlan` steps through, inverted and left continuous because its
 * one consumer samples the chain trilinearly rather than picking a level.
 *
 * The size law's scattering facet needs it (W2). The body texture is one blur for
 * a whole backdrop source — built at most once per source per frame, so it cannot
 * be per-surface — while the chain beside it carries every octave at once. So the
 * optics pass reaches a wider kernel per surface by sampling the chain, and this
 * is the origin it measures its extra octaves from. Below level 1's own σ there
 * is no coarser level to name, so the answer ramps linearly to 0 at σ = 0 rather
 * than diverging the way a bare logarithm would.
 */
export function chainLodForSigma(sigmaTexels: number): number {
  if (!(sigmaTexels > 0)) return 0;
  if (sigmaTexels <= CHAIN_SIGMA_AT_LEVEL_1) return sigmaTexels / CHAIN_SIGMA_AT_LEVEL_1;
  return 1 + Math.log2(sigmaTexels / CHAIN_SIGMA_AT_LEVEL_1);
}

export function bodyBlurPlan(
  sigmaPx: number,
  plan: PyramidPlan,
): { readonly level: number; readonly residualSigmaTexels: number } {
  if (sigmaPx <= 0) return { level: 0, residualSigmaTexels: 0 };

  // Level n's sigma in level-0 texels.
  const sigmaAt = (level: number): number =>
    level === 0 ? 0 : CHAIN_SIGMA_AT_LEVEL_1 * Math.pow(2, level - 1);

  let level = 0;
  for (let i = 1; i < plan.levelCount; i += 1) {
    if (sigmaAt(i) > sigmaPx) break;
    level = i;
  }

  // The residual is applied at the chosen level's own resolution, so convert.
  const covered = sigmaAt(level);
  const residualLevel0 = Math.sqrt(Math.max(sigmaPx * sigmaPx - covered * covered, 0));
  return { level, residualSigmaTexels: residualLevel0 / Math.pow(2, level) };
}

/**
 * Level n's own width as a Gaussian σ in level-0 texels — **measured**, not the
 * advisory `CHAIN_SIGMA_AT_LEVEL_1`.
 *
 * `CHAIN_SIGMA_AT_LEVEL_1` is 1.2 and says so about itself, and the body blur can
 * afford that because its residual pass absorbs whatever the constant misses. The
 * heavy tap cannot: its whole purpose is that the σ it is given comes back out of
 * reader A, so the width it subtracts in quadrature has to be the width the chain
 * really draws. `results/2026-09-10-w26-heavy-width/g0/chain-kernel.txt` simulates
 * `WGSL_DOWNSAMPLE_PASS` exactly on a level-0 delta and reads a second-moment σ of
 * 1.570 / 3.340 / 6.799 / 13.660 / 27.351 texels at levels 1…5 — the advisory
 * constant under-states level 1 by 24 % — with a kurtosis of −0.23 at every level
 * from 2 on. The shape is therefore fixed and platykurtic: neither a Gaussian
 * (0) nor a box (−1.2), and 12 % of peak away from the best-fitting Gaussian.
 * The table below is that reading divided by the shape's own constant ratio of
 * second-moment σ to half-maximum σ (1.018), because half maximum is the
 * statistic W25 G0's reader A reduces a two-component kernel by and the plan and
 * the reader have to speak one width.
 */
export const CHAIN_LEVEL_SIGMA = [0, 1.542, 3.281, 6.679, 13.418, 26.867] as const;

/**
 * Level n's own width as a Gaussian σ in level-0 texels, extended past the
 * measured table by the doubling the table itself settles into (the level 3 → 4
 * and 4 → 5 ratios read 2.009 and 2.002).
 */
export function chainLevelSigma(level: number): number {
  if (level <= 0) return 0;
  if (level < CHAIN_LEVEL_SIGMA.length) return CHAIN_LEVEL_SIGMA[level] as number;
  const last = CHAIN_LEVEL_SIGMA[CHAIN_LEVEL_SIGMA.length - 1] as number;
  return last * Math.pow(2, level - (CHAIN_LEVEL_SIGMA.length - 1));
}

/**
 * The plan for a **heavy** tap of σ level-0 texels (W26 G0, candidate (ii)): the
 * chain level to read, the residual σ in that level's own texels, and the uv
 * offset of one of its texels.
 *
 * The level is the deepest whose own blur is at or below the target, so the
 * residual never has to undo width the chain has already applied, and it is
 * clamped to what the chain actually has. Unlike `scatterLod`, that clamp is not
 * a ceiling on the RESULT: the residual Gaussian carries whatever octave the
 * chain is too short to supply, which is the whole reason this mechanism exists
 * (`MaterialProfile.sizeHeavyTapSigma`, and the measured cause in claims
 * §5.116 §2).
 */
export function heavyTapPlan(
  sigmaTexels: number,
  plan: PyramidPlan,
): {
  readonly level: number;
  readonly residualSigmaTexels: number;
  readonly stepUv: readonly [number, number];
} {
  let level = 0;
  if (sigmaTexels > 0) {
    for (let i = 1; i < plan.levelCount; i += 1) {
      if (chainLevelSigma(i) > sigmaTexels) break;
      level = i;
    }
  }
  const scale = Math.pow(2, level);
  const covered = chainLevelSigma(level);
  const residual = Math.sqrt(Math.max(sigmaTexels * sigmaTexels - covered * covered, 0)) / scale;
  return {
    level,
    residualSigmaTexels: residual,
    stepUv: [scale / Math.max(plan.width, 1), scale / Math.max(plan.height, 1)],
  };
}
