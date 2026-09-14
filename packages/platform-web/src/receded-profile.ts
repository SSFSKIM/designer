import type { RendererMaterialProfile } from "./renderer-bridge";

/**
 * The terms shared by the inactive-window endpoints (W27c G1, claims §5.130).
 * The outer shadow and bright rim disappear; tint strength survives as an
 * achromatic shade, including on a collapsed body. The corrected fitting run
 * checks the declared canvas and device scale before admitting any pixels.
 *
 * The 2x heavy width is in device pixels, selected after reading the actual
 * checker and photo spatial profiles. It is not a scale-free frost ratio.
 */
const common: RendererMaterialProfile = {
  // W28 (claims §5.145) changes only the inactive response's sampling region.
  // No active document opts in; the two endpoints stay inert until activation ships.
  backdropToneAbscissa: { kind: "silhouette" },
  tintChromaScale: 0,
  tintShadeCollapseRetention: 1,
  tintShadeStrength: 1,
  optics: {
    regular: { rimAlpha: 0, rimLevelGain: 0, shadowAlpha: 0 },
    clear: { rimAlpha: 0, rimLevelGain: 0, shadowAlpha: 0 },
  },
  rimCollapsed: 0,
  rimCollapsedTinted: 0,
  outerShadow: {
    thinOcclusionDark: 0,
    thinOcclusionMid: 0,
    thinOcclusionBright: 0,
    thickOcclusionAt96: 0,
    thickOcclusionAt128: 0,
    thickOcclusionAt160: 0,
    liftAmplitude: 0,
    reducedTransparencyOcclusion: 0,
  },
  sizeScatterRampStartThick1x: 0.3,
  sizeScatterRampStartThick2x: 0.04,
  sizeScatterRampStartFar2x: 0.04,
  sizeHeavyTapSigma2x: 14,
};

/**
 * Differences over the active material, selected AFTER resolving colour scheme.
 * Each scheme has exactly two fixed endpoints; this is not an interpolated pose.
 * A single flat difference could not move the light body down while moving the
 * dark one up through their different response curves, so the scheme seam that
 * already chooses the active document also chooses its inactive difference.
 *
 * The corrected declaration and its limits are in claims §5.130. The native bed
 * predates per-cell pose attestation, photo-body chroma remains too muted, and no
 * dark-accessibility or 2x-accessibility endpoint is measured here. G2 applies
 * the selected difference through applyMaterialProfile; G1's calibration harness
 * performs the same merge until that runtime path lands.
 *
 * W27c G1c (claims §5.141) superseded the initial fit: the 26.5 checking bed measured
 * the two terms §5.139 §6 named, one was fitted and one was refused, and the
 * G1c declaration is `2026-09-13-w27c-g1c-fit/fitted-endpoint.json`. The
 * §5.130 declaration stays on disk unchanged and the two fields G1c moved carry
 * their own paragraphs below. Nothing else in either entry moved in that gate.
 *
 * W28 G1 (claims §5.145) refits the response under a silhouette abscissa. Its
 * frozen document is `2026-09-14-w28-g1-silhouette/fitted-endpoint.json`; no active
 * profile or activation observer is changed by these opt-in endpoint documents.
 */
export const recededMaterialProfile: Readonly<Record<"light" | "dark", RendererMaterialProfile>> = {
  light: {
    ...common,
    tintShadeDark: 0.0288,
    tintShadeLight: 0.76,
    reducedTintAdaptation: 0.88,
    sizeScatterFloor: 0.7,
    sizeScatterRampStartThin1x: 0.55,
    sizeScatterRampStartThin2x: 0.7,
    // W28's non-D fit under the silhouette abscissa; the sealed rows are in claims §5.145.
    backdropToneAnchorX: [0.1104, 0.2706, 0.45, 0.9505],
    backdropToneResponseThin: [0.0126, 0.451, 0.573, 0.933],
    backdropToneResponseThick: [0.4553, 0.527, 0.63, 0.898],
    /*
     * Under a raised-occlusion policy the recede is a FLAT PANEL, not a backdrop
     * response (W27c G1c, claims §5.141 §4).
     *
     * The 26.5 checking bed reads the reference as opaque and backdrop-blind
     * there: under Reduce Transparency twelve of fourteen cells settle at
     * 0.95597 linear Y to five decimals over five backdrops and spans 32 through
     * 160. The exceptions are light-solid/rrect-ml at 0.95660 and photo/rrect-md
     * at 0.95411; eight have exactly zero native population SD and thirteen are
     * below 1e-5. Under Increase Contrast eleven of fourteen read 0.9911–0.99445;
     * hc-text/rrect-lg, hc-text-28/rrect-md and light-solid/rrect-ml are the
     * three below that band. The 0.0025-Y Reduce Transparency range still
     * identifies a backdrop-blind form at this scale, while the frozen endpoint
     * kept 45 % of the backdrop-tone adaptation alive through the refraction
     * cap. It pulled the thin end down onto the dark backdrop it was covering —
     * 0.58408 at span 48 against the reference's 0.99445, in the direction that
     * defeats the setting.
     *
     * Zeroing the cap is the whole statement, because the one factor carries all
     * three things a flat opaque panel does not have: the tone adaptation's
     * strength, the folded thickness the size occlusion grading rides, and the
     * refraction the rung is named for. The cells cannot separate them — a panel
     * with no variance shows none of the three — so the separation is recorded as
     * a gap rather than guessed at, and the standard profiles are untouched
     * because a nominal policy caps at `true`.
     */
    refractionScale: { approximate: 0 },
    /*
     * FITTED (W27c G1c) 0.92 -> 0.96, and it is a compromise between two policies
     * that want different numbers. With the adaptation gone the residual is a
     * level, and the reference has two: 0.95597 under Reduce Transparency, which
     * 0.92 reproduces exactly, and about 0.9935 under Increase Contrast, which
     * wants opacity. One shared fold cannot hold both, and 0.96 is what the
     * declared joint objective selects across the two. The 0.0375 Y the two
     * policies differ by is a model-form gap in the ledger, not a tuning residual.
     */
    increasedOcclusionLift: 0.96,
    /*
     * W27c G1d splits that shared compromise by the one policy axis the two
     * reachable states already differ on (Decision Log 19; claims §5.143).
     * The shared number remains the additive default for documents without this
     * map. Fitted on the banked supplying cells: 0.88 for Reduce Transparency,
     * 0.98 when Increase Contrast adds `ambientTint: "reduced"`.
     */
    increasedOcclusionLiftByPolicy: {
      reduceTransparency: 0.88,
      increaseContrast: 0.98,
    },
    // The existing signed rim law subtracts light; this is not a negative CSS
    // alpha. Only the 1x light increased-contrast outline identifies this band.
    strongBorderRim: { rimWidth: 1, rimAlpha: -3.5 },
  },
  dark: {
    ...common,
    optics: { ...common.optics, regular: { ...common.optics?.regular, tintAlpha: 0.89 } },
    tintShadeDark: 0.0202,
    tintShadeLight: 1.46,
    sizeScatterRampStartThin1x: 1,
    sizeScatterRampStartThin2x: 1,
    sizeScatterHeavyShareThick1x: 0.25,
    /*
     * The far ordinate stays at the extrapolation §5.130 flagged, and W27c G1c
     * REFUSED the measured value rather than adopting it (claims §5.141 §3).
     *
     * The bed measures it: the reference's dark thin recede over `light-solid`
     * reads 0.93261 where this curve returns 0.1611, which is the largest miss
     * anywhere on the bed. But this is a three-knot monotone interpolation and
     * the third knot is not a local constant — moving it reshapes the curve above
     * the second. On the GPU, raising it to the measured 0.93261 takes
     * `light-solid__rrect-sm__inactive`'s body ΔE from 0.43179 to 0.00406 and
     * `checkerboard__capsule-button__inactive`'s from 0.00653 to 0.19450, 29.8×,
     * because the reference is flat-low from encoded 0.11 to 0.74 and then steps
     * by 0.84 in the last fifth of the axis.
     *
     * The bed cannot say whether that step is in the abscissa or in the
     * structure: its four uniform backdrops sit at 0.1104, 0.2554, 0.2706 and
     * 0.9504, so 68 % of the axis has no uniform anchor, and its brightest
     * structured backdrop is 0.7652. One uniform neutral patch between them
     * decides it, on the same argument that added `mid-dark-solid` in W7 and
     * `mid-chroma-solid` in W27c G1b, and the fit waits for it.
     */
    /*
     * Superseded by W27c G1d (Decision Log 18; claims §5.143). The uniform
     * 140/255 anchor reads 0.12214 Y at both scales, against checkerboard's
     * 0.11700/0.11799 at nearly the same encoded input: the step is in the
     * abscissa, not structure. The declared sweep selects a low third knot at
     * 0.70 and the measured 0.9326072 far ordinate; its worst control is 5.68x
     * the frozen baseline, below the declared 9x refusal cap. The thick far
     * entry moves in the same pass to its measured 0.11753.
     */
    // W28's non-D fit under the silhouette abscissa; the sealed rows are in claims §5.145.
    backdropToneAnchorX: [0.1104, 0.2706, 0.8, 0.9505],
    backdropToneResponseThin: [0.011, 0.04092, 0.263, 0.9326072],
    backdropToneResponseThick: [0.0215, 0.0331, 0.092, 0.11753],
  },
};
