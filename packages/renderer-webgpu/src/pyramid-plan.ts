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
