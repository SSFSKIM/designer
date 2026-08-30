/**
 * `@vitrea/renderer-webgpu` — the optical engine (child C6 of
 * `docs/doperpowers/specs/2026-08-24-vitrea-liquid-glass-design.md`).
 *
 * The lazy half of X7: nothing here is reachable from `vitrea`'s entry
 * chunk, so a CSS-tier consumer never downloads WGSL. `vitrea` reaches this
 * package through a single dynamic import, which is also why this package imports
 * `@vitrea/geometry`, `@vitrea/motion` and `@vitrea/policy` but **never
 * `vitrea`** — an import back would close a dependency cycle. All three are pure
 * leaves that depend on nothing, which is what makes them safe to sit on from
 * under core. The handful of core-shaped types the renderer reads are declared
 * structurally in `render-model.ts`, and core's own types satisfy them without an
 * adapter.
 *
 * `@vitrea/policy` is the newest of the three and the one that is here for this
 * package's sake: the refraction ladder of Decision Log #19 has to read the same
 * to the shaders and to the CSS tier, and until Decision Log #23(d) it was written
 * out twice because there was no module on both sides of core to put it in.
 *
 * Where to start reading:
 *
 * | file | what it owns |
 * | --- | --- |
 * | `renderer.ts` | the frame: device, rebuilds, the three passes, submit |
 * | `device.ts` | ownership, loss teardown, rebuild, generations |
 * | `backdrop.ts` | X3's acquisition protocol and the five providers |
 * | `pyramid.ts` | the blur/analysis pyramid and the invariant's ledger |
 * | `passes.ts` | field, optics, highlight, as GPU work |
 * | `wgsl/` | the shaders; `wgsl/field.ts` carries X8 rider 2 |
 * | `material.ts` | the optical constants, the dual cap, the size-parameterised lens |
 * | `analysis.ts` | the stats and their temporal hysteresis |
 * | `governor.ts` | the knobs core's policy turns |
 * | `color.ts` | X5, CPU side |
 *
 * The contracts this package is bound by, and where each one is made true rather
 * than described:
 *
 *  - **X3** (BackdropFrame protocol) — `backdrop.ts`. This child owns its
 *    operational detail.
 *  - **X5** (colour pipeline) — `color.ts` and `wgsl/prelude.ts`, which carry the
 *    same piecewise sRGB curve and are held together by a test.
 *  - **X8 rider 2** (concentric renders as a level set of the parent's field) —
 *    `instances.ts` packs the parent's field parameters plus an offset, and
 *    `wgsl/field.ts` has no other path to take.
 *  - **§Core model's invariant** (≤1 pyramid rebuild per dirty source per frame) —
 *    `pyramid.ts`'s ledger, instrumented and asserted against core's own scheduler.
 *  - **Decision Log #19's dual cap** — `material.ts`, folded to one scalar before
 *    it reaches a uniform.
 *  - **Decision Log #20's f32 obligation** — `governor.ts` refuses family C until
 *    the cross-check is recorded as passing.
 */

export {
  ANALYSIS_GRID,
  ANALYSIS_STATS_FLOATS,
  ANALYSIS_WORKGROUP,
} from "./wgsl/analysis";

export {
  adaptiveTint,
  createAdaptationState,
  readbackDue,
  statsFromBuffer,
  ZERO_STATS,
  type AdaptationState,
  type AdaptationValues,
  type BackdropStats,
} from "./analysis";

export {
  BACKDROP_KINDS,
  createAppTextureProvider,
  createCopyProvider,
  createGradientProvider,
  createVideoProvider,
  linearGradientStops,
  SUPPORTED_APP_TEXTURE_FORMATS,
  validateAppTexture,
  type AppTextureProviderOptions,
  type BackdropBinding,
  type BackdropDevice,
  type BackdropFrame,
  type BackdropKind,
  type BackdropProvider,
  type CopyableSource,
  type CopyProviderOptions,
  type FrameInfoView,
  type GradientProviderOptions,
  type GradientStop,
  type VideoProviderOptions,
} from "./backdrop";

export {
  alphaNormalisationMode,
  BACKDROP_ALPHA_MODES,
  BACKDROP_COLOR_SPACES,
  displayP3ToSrgbLinear,
  encodeOutput,
  encodeOutputBytes,
  importColorMatrix,
  linearToSrgb,
  linearToSrgbChannel,
  LUMINANCE_WEIGHTS,
  OUTPUT_TEXTURE_FORMAT,
  relativeLuminance,
  srgbToLinear,
  srgbToLinearChannel,
  WORKING_TEXTURE_FORMAT,
  type BackdropAlphaMode,
  type BackdropColorSpace,
  type Rgb,
} from "./color";

export {
  createDeviceHost,
  type DeviceCapabilityInput,
  type DeviceHost,
  type DeviceHostOptions,
  type DeviceOwnership,
  type RendererDeviceStatus,
  type TeardownHook,
  type WebGPUAvailability,
} from "./device";

export {
  RENDERER_ERROR_CODES,
  RendererError,
  rendererError,
  type RendererErrorCode,
} from "./errors";

export {
  createGovernor,
  FAMILY_C_CROSS_CHECK,
  GOVERNOR_LADDER,
  NOMINAL_GOVERNOR,
  type FieldFamily,
  type Governor,
  type GovernorKnobs,
  type GovernorOptions,
} from "./governor";

export {
  createGpuContext,
  createStorageSlot,
  createUniformSlot,
  type GpuContext,
  type StorageSlot,
  type UniformSlot,
} from "./gpu-context";

export {
  clipFieldRectToCanvas,
  groupFieldRect,
  INSTANCE_BYTES,
  INSTANCE_FLOATS,
  packInstances,
  resolveSurfaces,
  snapRectToDevicePixels,
  type DevicePixelRect,
  type ResolvedSurface,
} from "./instances";

export {
  accessibilityRefractionCap,
  adaptationStrength,
  ADAPTIVE_LUMINANCE_HIGH,
  ADAPTIVE_LUMINANCE_LOW,
  ADAPTIVE_TINT_DARK,
  ADAPTIVE_TINT_LIGHT,
  adaptedTintAlpha,
  adaptedTintColour,
  BACKDROP_TONE_HIGH,
  BACKDROP_TONE_LOW,
  BACKDROP_TONE_MAX,
  BACKDROP_TONE_SIZE_BIAS,
  backdropToneAdaptation,
  backdropToneSizeBiasUnderPolicy,
  backdropToneUnderPolicy,
  bodyLod,
  DEFAULT_MATERIAL_PROFILE,
  effectiveRefraction,
  INCREASED_OCCLUSION_LIFT,
  LENS_BODY_LOD_PER_PX,
  LENS_RIM_LOD_BIAS,
  LENS_SIZE_GAIN_MAX,
  lensDepthPx,
  lensSizeGain,
  MATERIAL_OPTICS,
  MATERIAL_VARIANTS,
  occlusionAlphaUnderPolicy,
  opticsUnderPolicy,
  OUTER_SHADOW,
  outerShadowAlpha,
  outerShadowFalloff,
  outerShadowReachPx,
  outerShadowUnderPolicy,
  REFRACTION_LADDER,
  REFRACTION_SCALE,
  refractionRank,
  SIZE_OCCLUSION_GAIN,
  SIZE_SCATTER_GAIN_MAX,
  SIZE_SHADOW_GAIN_MAX,
  SIZE_SPAN_MAX,
  SIZE_SPAN_MIN,
  lensSizeGainFromThickness,
  sizeOcclusionAlpha,
  sizeOcclusionAlphaAt,
  sizeOuterShadowOcclusion,
  sizeOuterShadowOcclusionAt,
  SRGB_ENCODING_EXPONENT,
  sizeScatterSigma,
  sizeScatterSigmaAt,
  sizeShadowDepth,
  sizeShadowDepthAt,
  sizeThickness,
  sizeThicknessUnderPolicy,
  tintedTintColour,
  tintTone,
  tintToneAdaptation,
  withMaterialOverrides,
  type MaterialOptics,
  type MaterialOuterShadow,
  type MaterialPolicyView,
  type MaterialProfile,
  type MaterialProfilePatch,
  type MaterialRim,
  type MaterialVariant,
  type RefractionQuality,
} from "./material";

export {
  CANVAS_FORMAT,
  createPassRunner,
  type DeviceRect,
  type FieldPassArgs,
  type FieldTargets,
  type HighlightPassArgs,
  type OpticsPassArgs,
  type PassRunner,
} from "./passes";

export {
  createPipelineCache,
  pipelineKey,
  type PipelineCache,
  type PipelineCacheStats,
  type PipelineFactory,
} from "./pipeline-cache";

export {
  ANALYSIS_DISPATCH,
  createPyramidStore,
  type PyramidBuildOutcome,
  type PyramidBuildRequest,
  type PyramidInstrumentation,
  type PyramidResources,
  type PyramidStore,
} from "./pyramid";

export {
  createRebuildLedger,
  type RebuildLedger,
} from "./rebuild-ledger";

export {
  ANALYSIS_TARGET_EXTENT,
  bodyBlurPlan,
  CHAIN_SIGMA_AT_LEVEL_1,
  MAX_CHAIN_LEVELS,
  MIN_LEVEL_EXTENT,
  planPyramid,
  type PyramidPlan,
  type ResolutionPolicyView,
} from "./pyramid-plan";

export {
  IDLE_CHANNELS,
  type FrameContextView,
  type FrameParticipantView,
  type FrameRenderInput,
  type GroupRenderInput,
  type RebuildRequestView,
  type Rect,
  type SceneResolutionView,
  type SurfaceChannels,
  type SurfaceInput,
} from "./render-model";

export {
  ANALYSIS_PASS_ID,
  BACKDROP_PASS_ID,
  createWebGPURenderer,
  FIELD_PASS_ID,
  HIGHLIGHT_PASS_ID,
  NOMINAL_MATERIAL_POLICY,
  OPTICS_PASS_ID,
  RENDERER_PASS_IDS,
  type DrawFrameArgs,
  type DrawFrameResult,
  type GlassRenderer,
  type RendererInstrumentation,
  type ViewportState,
  type WebGPURendererOptions,
} from "./renderer";

export {
  createTexturePool,
  poolKey,
  type TextureAllocator,
  type TexturePool,
  type TexturePoolStats,
  type TextureRequest,
} from "./texture-pool";

export {
  createTimingCollector,
  PASS_LABEL,
  supportsTimestamps,
  type PassTimeline,
  type TimingCollector,
} from "./timing";

export {
  allShaderSource,
  analysisModule,
  chainModule,
  crossCheckKernelModule,
  fieldModule,
  fieldPassSource,
  highlightModule,
  importModule,
  importPassSource,
  opticsModule,
  CROSS_CHECK_SHAPE_FLOATS,
  CROSS_CHECK_WORKGROUP,
  WGSL_ANALYSIS_PASS,
  WGSL_CROSS_CHECK_PASS,
  WGSL_DOWNSAMPLE_PASS,
  WGSL_FIELD_KERNELS,
  WGSL_FIELD_PASS,
  WGSL_FIELD_SAMPLE,
  WGSL_HIGHLIGHT_PASS,
  WGSL_IMPORT_PASS,
  WGSL_INSTANCE_STRUCT,
  WGSL_OPTICS_PASS,
  WGSL_PRELUDE,
  WGSL_RSUP_GRAD,
  WGSL_RSUPN_GRAD,
  WGSL_SMOOTH_UNION,
} from "./wgsl";
