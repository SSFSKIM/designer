/**
 * @vitrea/geometry — ShapeSpec -> Contour IR -> compiled shapes.
 *
 * Pure math (X4): no DOM, no Node built-ins, no timers. Everything here is a
 * function of its arguments.
 *
 * The five pieces, and where to start reading:
 *
 *  - `field.ts`       the v1 pseudo-SDF (`rsupn`) and its analytic gradient.
 *                     This is what renders, and what C6's WGSL mirrors.
 *  - `shape.ts`       ShapeSpec -> the X8 channel vector plus the six derived
 *                     floats the field needs.
 *  - `contour.ts`     the Contour IR — interchange and tessellation only, never
 *                     the render form.
 *  - `concentric.ts`  the level-set offset resolver.
 *  - `morph.ts`       parametric interpolation over the whole channel vector.
 *  - `union.ts`       bounded smooth-min group union.
 *  - `wgsl.ts`        the shader source of truth, kept in step by
 *                     `test/wgsl-sync.test.ts`.
 *
 * The declared error bound (S2, adopted as spec Decision Log #20) is a permanent
 * regression target in `test/error-bound.test.ts`, measured against the same
 * ground-truth harness the spike used.
 */

export {
  clamp,
  type CornerProfile,
  type CornerRadii,
  flattenShapeChannels,
  halfExtents,
  lerp,
  lerpShapeChannels,
  SHAPE_CHANNEL_COUNT,
  SHAPE_FAMILIES,
  type ShapeChannels,
  type ShapeFamily,
  smoothstep,
  uniformRadii,
  type Vec2,
} from "./channels";

export { GeometryError, type GeometryErrorCode } from "./errors";

export {
  type CornerConstruction,
  cornerBudget,
  resolveCornerConstruction,
  smoothingCeiling,
} from "./corner";

export {
  APPLE_RSUP,
  APPLE_RSUPN,
  type CoefficientRow,
  coefficientsAt,
  type CornerCoefficients,
  FIGMA_RSUP_TABLE,
  FIGMA_RSUPN_TABLE,
  RSUP_BASIS_ORDER,
  ZERO_COEFFICIENTS,
} from "./coefficients";

export {
  centralGradient,
  cornerSupport,
  type FieldParams,
  type FieldSample,
  rsupField,
  rsupLevelSetNormal,
  rsupnField,
  rsupnFieldAndGradient,
} from "./field";

export {
  APPLE_BEST_FIGMA_SMOOTHING,
  APPLE_CONTINUOUS_SMOOTHING_SEED,
  APPLE_CORNER_DUMP,
  APPLE_REACH,
  APPLE_SATURATION_RADIUS_RATIO,
  type AppleContour,
  buildAppleContour,
} from "./apple";

export {
  buildReferenceContour,
  type Contour,
  contourArea,
  contourCurvatureBreaks,
  contourGap,
  contourLength,
  type ContourSegment,
  contourTangentBreak,
  contourToCubics,
  mirrorSegment,
  type Point,
  ringFromCorner,
  segmentCurvature,
  segmentDerivative,
  segmentEnd,
  segmentLength,
  segmentNormal,
  segmentPoint,
  segmentSecondDerivative,
  segmentStart,
  translateSegment,
} from "./contour";

export {
  assertUniformRadii,
  type CapsuleSpec,
  type CornerReference,
  type FieldFamily,
  fieldParams,
  type FixedRoundedRectSpec,
  governorFieldParams,
  type ResolveOptions,
  type ResolvedCorner,
  type ResolvedShape,
  resolveCorner,
  resolveFromChannels,
  resolveShape,
  type ShapeSpec,
  toContour,
} from "./shape";

export {
  type ConcentricResult,
  type ConcentricSpec,
  concentricField,
  concentricFieldAndGradient,
  DEFAULT_CONCENTRIC_MIN_RADIUS,
  MEASURED_BAND_PX,
  resolveConcentric,
  resolveThicknessInnerShape,
} from "./concentric";

export { type MorphOptions, morphChannels, morphShapes, sampleMorph } from "./morph";

export {
  DEFAULT_GROUP_UNION,
  type GroupUnionParams,
  groupUnion,
  groupUnionField,
  memberField,
  smoothUnion2,
} from "./union";

export {
  fingerprint,
  WGSL_FIELD_MODULE,
  WGSL_RSUP,
  WGSL_RSUPN,
  WGSL_SHAPE_STRUCT,
} from "./wgsl";
