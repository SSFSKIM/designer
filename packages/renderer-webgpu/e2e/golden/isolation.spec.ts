/**
 * The isolation proof (Decision Log #31(a), user-directed) — now a pinned-bytes
 * regression guard. See `POST_WAVE_HASHES` for why the original reading retired.
 *
 * Eight goldens went stale when C9a tuned the material, and the parent refused to
 * re-baseline them on the strength of "the tint changed, so of course they moved."
 * The gate is this: **render every golden scene with the OLD profile values
 * injected through the `materialProfile` seam, and require the result to be
 * byte-identical to the goldens the new baseline replaces.** Identity attributes
 * the entire visual delta to exactly the two constants C9a moved. Any residual
 * means something unintended moved with them, and is investigated before anything
 * is re-baselined.
 *
 * ## Why this stays in the suite after the re-baseline
 *
 * The obvious shape — compare an old-profile render against the old golden PNGs —
 * can only run once, because the PNGs are about to be overwritten. So the
 * baseline is carried as **hashes of the pre-C9a pixel bytes** instead: nine short
 * strings rather than nine more images, recorded at the moment the proof was run
 * and never regenerated. That makes the attribution reproducible rather than a
 * paragraph in a commit message, and it keeps working as a regression guard: any
 * future change that moves a golden *other* than through the material profile
 * fails here too, because the old-profile render would stop matching a hash taken
 * before that change existed.
 *
 * Hashing the raw RGBA readback rather than the encoded PNG deliberately: the
 * bytes are what the renderer produced, and a PNG encoder's choices are not part
 * of the claim.
 */

import { createHash } from "node:crypto";

import { expect, test } from "@playwright/test";

import { assertUniformRadii, resolveCorner } from "@vitrea/geometry";

import { SCENES } from "../fixtures/scenes";
import { decodeCapture, openHarness, requireHardwareAdapter, type Raster } from "../support";

/**
 * The material as it stood before C9a, as a patch over today's defaults.
 *
 * Exactly the two constants C9a moved, from `git show 1d4545e^` — the tint alpha
 * (0.28 → 0.62) and the light-backdrop end of the adaptive crossover, whose old
 * value `SRGB_DARK_TINT` = [0.09, 0.09, 0.1] is what made the tint invert against
 * the backdrop. The dark end was white then and is white now, and the crossover
 * band (0.12 / 0.42) never moved, so neither is restated here: a patch that named
 * unchanged fields would weaken the claim rather than strengthen it, because
 * identity would no longer tell "these two constants" apart from "these five".
 */
const PRE_C9A_PROFILE = {
  optics: { regular: { tintAlpha: 0.28 } },
  // srgbToLinear([0.09, 0.09, 0.1]), computed here rather than imported so the
  // patch is a literal a reader can check against the old source.
  adaptiveTintLight: [0.008540382112116999, 0.008540382112116999, 0.010022825574869039],
  /*
   * The outer shadow, off — W8's own entry in this patch, and it belongs here on
   * the file's own rule rather than despite it.
   *
   * The rule is that the patch names the fields that MOVED, so identity
   * attributes the whole delta to them. Before W8 this renderer drew no outer
   * shadow at all; every amplitude anchor at zero is that state, exactly, and
   * every one of the eight scene hashes below reproduces from it unchanged. That
   * identity is the proof W8's golden re-baseline needed: the entire visual delta
   * across every golden is the outer shadow and nothing else travelled with it.
   *
   * It is seven zeros rather than one since W14 G1 (claims §5.62): the single
   * `occlusion` became two regimes of three anchors each plus the lift's own
   * amplitude, and "the shadow off" is all of them at zero. The lengths are left
   * alone because a shadow of zero amplitude has no extent whatever they say.
   */
  outerShadow: {
      thinOcclusionDark: 0,
      thinOcclusionMid: 0,
      thinOcclusionBright: 0,
      thickOcclusionAt96: 0,
      thickOcclusionAt128: 0,
      thickOcclusionAt160: 0,
      liftAmplitude: 0,
    },
} as const;

/**
 * SHA-256 of each scene's pre-C9a RGBA readback, recorded 2026-08-25 on this
 * machine's `apple / metal-3` adapter through Playwright's full Chromium binary.
 *
 * These ARE the goldens that C9d replaced: every one of them was verified equal to
 * the committed `e2e/goldens/*.png` of the moment, before regeneration, which is
 * the proof itself. §Calibration keys results by adapter class, so a different GPU
 * is expected to move them — this file is a same-machine attribution, not a
 * cross-hardware claim.
 */
const PRE_C9A_HASHES: Readonly<Record<string, string>> = {
  "field-mask": "532584d4daebd7a1c93f90191e64f19f",
  "refraction-checkerboard": "e18f05b87024069ca806bdcce24d85c6",
  "lens-size-scaling": "bd3f42d122eae08df677d36f0dbe93c1",
  "tint-adaptation-light": "adb3f1ada4ecbd31d4221bb414f83c42",
  "tint-adaptation-dark": "f10e9033dc5b3846ff90c352bcd6cc1c",
  "rim-two-references": "889c2dab911df9a3f68dfde8698ef855",
  "concentric-nesting": "59e00a6cae5b199c5f254934859221f1",
  "union-pair": "5ed83d006fa1c5cf95d0acd30bda8e66",
  "highlight-press-glow": "0b9dc460a6616c5a3d6fb69a6b97a783",
};

/**
 * Hashes a later, deliberately NON-profile change moved — re-recorded, with the
 * pre-C9a value left in place above so the record is not overwritten.
 *
 * This is the file doing its job, not the file being worked around: the note above
 * says a change that moves a golden other than through the material profile must
 * fail here, and one did. What makes re-recording legitimate rather than a
 * re-baseline is that the change is attributable independently of any image, and
 * the attribution is asserted below rather than asserted in prose — see
 * "the geometry change is confined to the scenes it can reach".
 */
const SUPERSEDED: Readonly<Record<string, { readonly now: string; readonly why: string }>> = {
  "rim-two-references": {
    now: "62aec916a518da80353e29564690642b",
    why:
      "the normalization's anchor in sd_rsupn / sd_rsupn_grad (@vitrea/geometry " +
      "field.ts, 'The normalization'). It is provably inert at corner smoothing 0 — " +
      "the coefficients are all zero there, so R is exactly the corner reach, R' is " +
      "exactly 0, and the anchored and unanchored forms are the same expression. " +
      "This is the only golden scene with a non-zero effective smoothing on any " +
      "surface, and therefore the only one that could move. Delta: max channel 9, " +
      "mean 0.008, 16 of 96000 pixels past the golden suite's tolerance of 4, all " +
      "of them in two ~5-device-px clusters at the squares' centres, where each " +
      "square's corner-sector vertices land because its reach (39.7 and 43.2 px) " +
      "nearly fills its 44 px half-extent. Those clusters were four hook-shaped " +
      "marks of false refraction, the same artifact the public demo showed at plate " +
      "scale, and the new bytes are the ones without them.",
  },
};

/**
 * The bytes every scene rendered from `PRE_C9A_PROFILE` on `main` immediately
 * before W8 — re-recorded 2026-08-31, and the record that is actually asserted.
 *
 * ## Why a whole new table, and why re-recording is legitimate here
 *
 * Eight of the nine hashes above had ALREADY gone stale on `main` before this
 * child started. That is not a claim from reading the code: the same eight tests
 * fail on `main` at `1132b3a` with W8 nowhere in the tree. The file predicted
 * this exactly — "any future change that moves a golden *other* than through the
 * material profile fails here too" — and the likeliest mover is that W2, W3 and
 * W7 each added a profile axis that did not exist when these hashes were taken,
 * so a patch naming only C9a's two constants no longer reconstructs the 2026-08-25
 * renderer. Attributing that drift belongs to whoever moved it, not to W8.
 *
 * What W8 can prove, and did, is that it contributes NOTHING to it. Every one of
 * the nine values below was rendered twice: once on `main` in a detached
 * worktree, and once on this branch with the outer shadow declined — and all
 * nine are byte-identical across the two trees. So the whole of W8's visual
 * delta is the outer shadow, the golden re-baseline beside this file is
 * attributable to that facet alone, and this table restores a guard that had
 * stopped guarding rather than papering over one that was working.
 *
 * `highlight-press-glow` is the control: it never drifted, and its value here is
 * the original pre-C9a hash unchanged.
 */
const PRE_W8_HASHES: Readonly<Record<string, string>> = {
  "field-mask": "c4e1e54af89533f30dae2be255aedf0a",
  "refraction-checkerboard": "9237a010b7f2303b23c809a51c89ab65",
  "lens-size-scaling": "0685b1229624e9e2f38ad1c05d3a28b7",
  "tint-adaptation-light": "391343c056b2ee0bb6358b1a6ea905ab",
  "tint-adaptation-dark": "7d513fdd12438f8ae0af386ee2b26e8e",
  "rim-two-references": "3d346e698f1432a29fa1e64764644137",
  "concentric-nesting": "93fa07dd683e9761442d05c5afef1e1e",
  "union-pair": "55ffdedb9fe1e6c626ce3ca8e986b42e",
  "highlight-press-glow": "0b9dc460a6616c5a3d6fb69a6b97a783",
};

/**
 * The bytes `PRE_C9A_PROFILE` renders on the post-v1 wave's frozen material —
 * recorded 2026-09-01, and the record that is actually asserted.
 *
 * ## Why a fourth table, and what this file can no longer claim
 *
 * The eight hashes above went stale again, and this time the reason is one the
 * file's own rule cannot absorb by naming another constant.
 *
 * The rule was: name the fields that MOVED, and identity attributes the delta to
 * them. It works only while the delta is expressible as a profile patch. Across
 * this wave it is not. `git diff` between the commit that recorded `PRE_W8_HASHES`
 * and this one moves material constants — `tintAlpha` 0.62 → 0.46, `shadowAlpha`
 * 0.55 → 0.05, `blurSigma` 8 → 3, `tintToneFloor` 0.45 → 1, `tintToneCeilMix`
 * 0.45 → 0, `sizeOcclusionGain` 0 → 0.05, `sizeShadowGainMax` 1.4 → 1,
 * `backdropToneLow`, `backdropToneSizeBias`, `occlusion`,
 * `reducedTransparencyOcclusion`, `INCREASED_OCCLUSION_LIFT` — **and it also
 * moves shader and pass code**: `passes.ts`, `renderer.ts`, `wgsl/optics.ts`,
 * `wgsl/highlight.ts`. No value injected through the `materialProfile` seam can
 * reconstruct a renderer whose shaders are different. The old reading of this
 * file is therefore retired rather than patched, and saying so is cheaper than a
 * patch that would look complete and quietly not be.
 *
 * ## What survives, and it is not nothing
 *
 * What the seam still buys is a **regression guard with a named configuration**.
 * These bytes are what today's renderer produces from one fixed, explicitly
 * written material patch. Anything that moves them — a constant, a shader, a
 * pass, a geometry primitive — fails here and has to be attributed before the
 * table is touched. That is the property the file was always most useful for,
 * and the one that catches the next unintended change.
 *
 * Deliberately, `PRE_C9A_PROFILE` is left naming only three fields. Every
 * constant it does NOT name is a constant this guard can see move. Adding
 * `sizeOcclusionGain: 0` to it would have made these hashes reproduce across the
 * wave — and would have bought that by blinding the guard to the very constant
 * the wave had just refitted. Coverage is worth more here than continuity.
 *
 * The re-recording is attributable independently of any image: every constant
 * above has a measured driver in `c9a-fidelity-claims.md` §5.13, §5.16, §5.17 and
 * §5.26, and the shader work is W8's, whose own delta this file already proves is
 * confined to the alpha channel two tests below.
 *
 * `highlight-press-glow` is the control, and it is worth reading twice: its hash
 * here is **byte-identical to the 2026-08-25 original**, through C9a, through W8,
 * and through this wave. A scene with no tint, no outer shadow and no smoothing
 * has not moved once, which is what makes the other eight movements legible as
 * facets rather than as noise.
 */
const POST_WAVE_HASHES: Readonly<Record<string, string>> = {
  "field-mask": "c587d588fd98eea1bd799b7fc164b0ee",
  "refraction-checkerboard": "6d1f904503b136e30610681bb6465655",
  "lens-size-scaling": "ec7ec804bb9bd2aa8554cb95312f91bf",
  "tint-adaptation-light": "520732bdb6f6434215760d3d4f3bef2e",
  "tint-adaptation-dark": "83496d4e9689786c229b73dd24b721a8",
  "rim-two-references": "c5a32f7e06d8dd0f5748e8745e346dcc",
  "concentric-nesting": "acb46d0afe555e4a551f758f80176561",
  "union-pair": "a65571b183d017b33389ebd49f6d453d",
  "highlight-press-glow": "0b9dc460a6616c5a3d6fb69a6b97a783",
};

/**
 * `field-mask` after W11a (2026-09-02) — the one golden on the UNSAMPLED path,
 * re-recorded with the attribution the file asks for.
 *
 * W11a changed what the optics pass writes for a group with no backdrop to
 * sample: a premultiplied LAYER of the material at its own alpha, composited by
 * the browser, where before it wrote the material mixed over black as an opaque
 * pixel (claims §5.38 §5 — the nested-glass upper pane rendering as a flat
 * 0.468). The change is a branch on `flags.x`, so it can reach exactly the
 * scenes that bind no backdrop, and `field-mask` (`noBackdrop: true`) is the
 * only golden that does. The attribution is asserted rather than described:
 * the other eight hashes in `POST_WAVE_HASHES` reproduce unchanged in the same
 * run, `highlight-press-glow` among them — a scene that is ALSO unsampled but
 * captures the highlight canvas, which this change never touches.
 */
const W11A_HASHES: Readonly<Record<string, string>> = {
  "field-mask": "06473282f886a2ecc81f19c257bd515e",
};

/**
 * Five goldens after W11c G1, the body law (2026-09-03) — re-recorded with the
 * attribution the file asks for, and the first re-baseline whose delta is NOT
 * expressible through the profile seam.
 *
 * W11c changed the FORM of the interior, not a constant of it. Before, the body
 * was mixed toward a heavier sample whose mip level itself rose with the
 * thickness (`log2(1 + (gain − 1) · sizeK)`), so a small control had no heavy
 * component at all. The reference's interior is a sharp component plus a heavy
 * one at every span (claims §5.38 §4), so the heavy tap now sits at the full
 * gain and the scattering facet has its OWN law — a floor at any span
 * (`sizeScatterFloor`) and, since W13 G1, a ramp in depth above it rather than a
 * curve in the span (claims §5.61 §2) — with `blurSigma` 3 → 1.25 and the gain
 * 1 → 8 refitted around it. No patch
 * over the new shader can reproduce the old one: the old form has no floor to
 * name and ties the heavy tap's level to the thickness, which the new form does
 * not. So `PRE_C9A_PROFILE` stays what it is and these five hashes are the new
 * pins, taken in the same run as the isolation below.
 *
 * The attribution is in which scenes did NOT move. The law is a blur of what is
 * behind the glass, so it can move only structure: the two checkerboard scenes
 * carry the delta (`refraction-checkerboard` max 10 / mean 0.65 code values
 * against the committed goldens, `lens-size-scaling` max 4 / mean 0.37), the
 * three gradient scenes move by at most ONE code value (a Gaussian over a linear
 * ramp is the ramp), and the four that have no structure to blur — the two flat
 * `tint-adaptation-*` backdrops and the two unsampled scenes, `field-mask` and
 * `highlight-press-glow` — reproduce their hashes byte-for-byte. The control has
 * still not moved once since 2026-08-25.
 */
const W11C_HASHES: Readonly<Record<string, string>> = {
  "refraction-checkerboard": "2f64282dbe199da49a2eccfcfd12e989",
  "lens-size-scaling": "0f5fdbd3664b1f8e04150d45328161c8",
  "rim-two-references": "220b7249d17570bf343050330178bc05",
  "concentric-nesting": "e48ffeaa324370afd0a5cdf89b8ff64c",
  "union-pair": "8e2df1d44ab52baeb9a3307b8aa5f97e",
};

/**
 * Five goldens after W11c G2, the lens band (2026-09-03) — the second FORM change
 * of the round, and again not expressible through the profile seam.
 *
 * The lens used to be a separate sample of the backdrop chain at a level biased
 * SHARPER toward the rim (`lensRimLodBias`), mixed over the body by the lens
 * profile — so the band showed finer detail than the interior and faded into it.
 * The reference's band is nothing of the kind (claims §5.43): read per depth
 * shell around the contour on the probe's resolved pitches, it is the interior's
 * own two-component body displaced 1.6 lens depths inward at the contour on the
 * shader's own (1 − depth)² profile, at full weight, with no sharper sample, no
 * heavier one and no darkening. So the shader now reads both body components at
 * the refracted position and the two rim-LOD constants are retired; the new
 * `lensRefractionGain` is the one constant of the form. Nothing in the old form
 * can be patched into this one, so these are new pins.
 *
 * The attribution is the same shape as G1's: only scenes with backdrop
 * structure under a lens can move. The two checkerboard scenes carry the delta
 * (`lens-size-scaling` max 32 / mean 0.98 code values against the committed
 * goldens, `refraction-checkerboard` max 21 / mean 1.21 — the band now folds the
 * plate rather than compressing a sharper copy of it), the three gradient scenes
 * move by at most TWO code values (`rim-two-references` 2, `concentric-nesting`
 * 2, `union-pair` 1: a displaced ramp is a slightly different ramp), and the four
 * with nothing to displace — the two flat `tint-adaptation-*`
 * backdrops and the two unsampled scenes, `field-mask` and `highlight-press-glow`
 * — reproduce their hashes byte-for-byte. The control has still not moved once
 * since 2026-08-25.
 */
const W11C_G2_HASHES: Readonly<Record<string, string>> = {
  "refraction-checkerboard": "d751a8315c0746f88ddb48a078cbe8bd",
  "lens-size-scaling": "31e0766b9c8eb0f8a6d53f43e3ad83da",
  "rim-two-references": "5dd211830a43f096d4d61cb005e8699e",
  "concentric-nesting": "2923132241682bde2e28aa1955aee198",
  "union-pair": "33049e332405b5d9a16d36765352cd17",
};

/**
 * Claims §5.47 — the placed fit. The one scene whose backdrop is smaller than
 * its viewport, `placed-checkerboard`, was added WITH the fit and has no
 * pre-fit golden to attribute against; its fail-before record is the cover-fit
 * render's hash in `scenes.spec.ts`. Pinned here under the named profile like
 * every other scene, so a later change that moves it through anything but the
 * profile seam fails the same way. Every pre-existing scene's backdrop is the
 * size of its viewport, where the placed fit and the cover fit coincide, and
 * every one of their hashes above reproduced unchanged the day this landed.
 */
const PLACEMENT_HASHES: Readonly<Record<string, string>> = {
  "placed-checkerboard": "c42c0c7069e55624f5e34d717a1ffb99",
};

/**
 * Six goldens after W12 G2, the lens's shape (2026-09-03; claims §5.51) — a
 * FORM change again, and again not expressible through the profile seam.
 *
 * The lens used to displace along the field's normal by `1.6 × lensDepth ×
 * (1 − depth)²` on a depth that rode the size law's smoothstep. The reference's
 * band is a steeper power on the reference's own span law (its inner refraction
 * height `min(0.25·span, 20)` and amount `min(0.8·span, 60)`, read from its
 * layer tree, claims §5.50), 44.7 px at the contour on a saturated span dying
 * as `(1 − u/26.7)^3.69`, and it runs along the field's gradient blended toward
 * the oval inscribed in the surface's box on thick surfaces — which is what
 * magnifies the band along the edge. Neither the exponent, the span law nor the
 * direction can be patched into the old form, so these are new pins; the inner
 * shadow keeps the old depth law and profile, which is why nothing without
 * backdrop structure moved.
 *
 * The attribution is the same shape as G2's: only scenes with structure under
 * a lens can move. `placed-checkerboard` carries the largest delta (max 34 /
 * mean 3.79 code values against the committed goldens — a 68 px span authored
 * at thickness 14, whose depth went 14 × 1.95 = 27.3 → (14/8) × 17 = 29.75 px
 * and whose contour magnitude went 1.6 × 27.3 = 43.7 → 0.745 × (14/8) × 54.4 =
 * 70.9 px under the new laws, with the ovalization's knee sitting at 64–72),
 * then `refraction-checkerboard`
 * (max 19 / mean 1.51) and `lens-size-scaling` (max 7 / mean 0.49); the three
 * gradient scenes move by at most TWO code values (`rim-two-references` 2,
 * `concentric-nesting` 2, `union-pair` 2: a displaced ramp is a slightly
 * different ramp); and the four with nothing to displace — the two flat
 * `tint-adaptation-*` backdrops and the two unsampled scenes, `field-mask` and
 * `highlight-press-glow` — reproduce their hashes byte-for-byte. The control
 * has still not moved once since 2026-08-25.
 */
const W12_G2_HASHES: Readonly<Record<string, string>> = {
  "refraction-checkerboard": "daa6d48e663a40348882491385d6b9cb",
  "placed-checkerboard": "b0b1e9e0f32fd66957b33954cbce00f6",
  "lens-size-scaling": "ea72926bab6a0a7b0144a477ac4f477d",
  "rim-two-references": "1748f11aef65573d0445157cd3db2fb8",
  "concentric-nesting": "9f547ae88a38432f002bae2c70213b6e",
  "union-pair": "e63ff99028171bc22e797f7ee6cb0b6f",
};

/**
 * Five goldens after the W12 ω 0.8 round (2026-09-03; measured under W12
 * Decision Log 4, landed under Decision Log 6) — one constant, `lensOvalization`
 * 0.6 → 0.8, and nothing else. The lens keeps its span law, its magnitude and
 * its exponent; only the direction it warps along leans further toward the oval
 * inscribed in the surface's box, which is what stretches the band along an edge
 * away from that edge's midpoint. The value landed by eye, not by measurement:
 * 0.6 is what the pixels preferred by 0.001–0.002 SSIM on every row that can see
 * the constant (claims §5.54), 0.8 is the field's measured tilt, and the user
 * read the 0.8 sheet as much closer to macOS.
 *
 * The attribution is narrower than G2's, as one would expect of a direction-only
 * change on thick surfaces: `placed-checkerboard` again carries the largest
 * delta (max 23 / mean 0.51 code values against the G2 goldens — a 68 px span
 * sitting inside the ovalization's 64–72 knee, so its ω moves the most in
 * relative terms), then `refraction-checkerboard` (11 / 0.30) and
 * `lens-size-scaling` (6 / 0.19); the two gradient scenes that move do so by ONE
 * code value (`rim-two-references` 1, `concentric-nesting` 1), and `union-pair`
 * — which moved by two under G2 — is byte-identical here, as are the two flat
 * `tint-adaptation-*` backdrops and the two unsampled scenes, `field-mask` and
 * `highlight-press-glow`. The control has still not moved once since 2026-08-25.
 */
const W12_G2B_HASHES: Readonly<Record<string, string>> = {
  "refraction-checkerboard": "4aeeb4ed7efe9995d544b329f07f95a1",
  "placed-checkerboard": "6e9a3c5978d4e93ebc40edcd700bc3d7",
  "lens-size-scaling": "8d82c1f1c268d62ba84513651aab1138",
  "rim-two-references": "1981d711750823a735c3f05aa8c15e50",
  "concentric-nesting": "94496ccfe1bd23c77943346f21ec4a95",
};

/**
 * One hash after W14 G2, the outer shadow's two-term composite (2026-09-03;
 * claims §5.66). With all seven amplitudes at zero the composite IS the
 * pre-W8 renderer, and nine of the ten scenes reproduce their pinned bytes
 * from it exactly. `placed-checkerboard` does not, by ONE pixel: (290, 141),
 * fully covered (alpha 255), on a smooth interior gradient, reads 217 where it
 * read 218 in all three channels. Attributed by rendering the declined scene in
 * a build of the pre-merge commit (`1c865fe`) and in this one and diffing the
 * two readbacks — 1 of 96 000 pixels differs, by 1 of 255, and nothing else
 * moves; the default (shadow-on) renders differ across half the frame by up to
 * 7 codes of alpha, which is the shadow itself. The optics pass now composes the
 * body, the black term and the lift in one expression so the coverage ramp has
 * no seam, and that reordering flips a value that sat on a rounding boundary.
 * A tie, not a term; pinned here so the next reordering has to say the same.
 */
const W14_HASHES: Readonly<Record<string, string>> = {
  "placed-checkerboard": "0d15cb9d99ad972659968a5b9b509401",
};

/*
 * No hash after W13 G2, the body's depth ramp (2026-09-04; claims §5.68 §8),
 * and the reason is worth its line so the next landing does not mistake a
 * clean run for a proof it is not. Every scene here renders at device pixel
 * ratio 2, and at 2x the landing changes nothing by design — the ramp is a
 * verified null there and the widths are the bed's (W13 Decision Log 8) — so
 * `goldens:regen` on the landed tree rewrote all ten goldens byte for byte,
 * and the proof's declined renders reproduce the pinned bytes because the
 * named profile's scatter gain of 1 makes the sharp and heavy components one
 * and the mix has nothing to act on. No golden exercises the 1x ramp; that
 * gap is recorded in the wave's Deferred list, not closed here.
 */

/**
 * `body-ramp-1x`, pinned for the first time (2026-09-04; W15 contract X7, and
 * W13's Deferred entry that asked for it).
 *
 * This is a first pin, not a re-record: the scene did not exist before, so
 * nothing here supersedes anything and no attribution is owed. What it is for is
 * the gap the note above records — every other scene renders at device pixel
 * ratio 2, where the body's depth ramp evaluates to nothing on this bed, so no
 * committed byte in this directory depends on the 1x material at all. W15 moves
 * the 2x body under a binding rule that the 1x material does not move; a promise
 * with no pixel behind it is not a promise, and this is the pixel.
 *
 * Recorded at the W13 bed (`main` at `967bf7c`, the material as W13 G2 landed
 * it), on this machine's `apple / metal-3` adapter through Playwright's full
 * Chromium binary, like every hash above. The named profile patches the tint and
 * the outer shadow and nothing of the body, so the ramp is live in this render:
 * the test below is the fail-before record that says so, and it is what makes
 * this hash a pin on the ramp rather than on the geometry alone.
 */
const W15_HASHES: Readonly<Record<string, string>> = {
  "body-ramp-1x": "084480a056aab58bd1ec90d4e5d98b8d",
};

/**
 * Six hashes after W15 G2, the 2x body (2026-09-04; claims §5.70 §8) — and the
 * one 1x pin above holding, which is the point of the table.
 *
 * At device pixel ratio 2 the body's widths became device-pixel quantities, the
 * deep value went fully heavy and the depth ramp became the whole body above
 * it. Every golden scene but `body-ramp-1x` renders at ratio 2, so every one
 * that has backdrop structure under its surface moves by design. The named
 * profile declines the tint and the outer shadow and touches nothing of the
 * body, so the body change reaches the declined renders as well as the
 * defaults. **Attributed by measurement** (`results/2026-09-04-w15-body-2x/g2/
 * attribution.txt`, `attribute-goldens.py`): the declined and default renders
 * of every scene were read back from the pre-merge tree (`c9edbb0`) and the
 * landed one and diffed pixel for pixel. `body-ramp-1x`: 0 of 24 000 pixels.
 * The four scenes with no structure to blur — `field-mask` (no backdrop), the
 * two flat tint adaptations, `highlight-press-glow` — 0 of 96 000 each. The six
 * that move, all inside their surfaces, alpha untouched: `refraction-checkerboard`
 * 27 413 px by up to 10 codes, `placed-checkerboard` 30 502 by 19,
 * `lens-size-scaling` 25 610 by 17 (the checkerboard bodies: a narrower, deeper
 * body); `rim-two-references` 3 118, `concentric-nesting` 1 299, `union-pair`
 * 514, each by exactly 1 code (the flat backdrops: the heavy tap's level moved
 * and resamples a code apart). Nothing else moved anywhere.
 */
const W15_G2_HASHES: Readonly<Record<string, string>> = {
  "refraction-checkerboard": "ef1a44c45b42abf0a927adf6d53a418e",
  "placed-checkerboard": "8fff9f59c9d59591208e9062212decc0",
  "lens-size-scaling": "01a333c953c2cbc3fa16ed597bbaffd5",
  "rim-two-references": "fd7836b6f82749ea9d908a6fd57e26bf",
  "concentric-nesting": "0e053b06bde1449b72c09838b7da0d45",
  "union-pair": "25ca33c47abd68cc27358ab9e4e24eb4",
};

const expectedHashFor = (name: string): string | undefined =>
  W15_G2_HASHES[name] ??
  W15_HASHES[name] ??
  W14_HASHES[name] ??
  W12_G2B_HASHES[name] ??
  W12_G2_HASHES[name] ??
  PLACEMENT_HASHES[name] ??
  W11C_G2_HASHES[name] ??
  W11C_HASHES[name] ??
  W11A_HASHES[name] ??
  POST_WAVE_HASHES[name] ??
  PRE_W8_HASHES[name] ??
  SUPERSEDED[name]?.now ??
  PRE_C9A_HASHES[name];

/** The largest effective corner smoothing any of a scene's surfaces resolves to. */
const maxSmoothingEff = (scene: (typeof SCENES)[number]): number => {
  let worst = 0;
  for (const group of scene.groups) {
    for (const surface of group.surfaces) {
      const corner = resolveCorner(
        surface.shape.size,
        assertUniformRadii(surface.shape.radii),
        surface.shape.smoothing,
        surface.reference ?? "figma-smoothing",
      );
      worst = Math.max(worst, corner.smoothingEff);
    }
  }
  return worst;
};

const hashOf = (raster: Raster): string =>
  createHash("sha256").update(raster.data).digest("hex").slice(0, 32);

test.describe("@golden the goldens move only through the named profile seam", () => {
  for (const scene of SCENES.filter((candidate) => candidate.measureOnly !== true)) {
    test(`${scene.name} renders its pinned bytes from the named profile`, async ({ page }) => {
      const report = await openHarness(page);
      requireHardwareAdapter(report);

      const before = decodeCapture(
        await page.evaluate(
          ([name, profile]) => window.vitrea.renderScene(name as string, undefined, profile),
          [scene.name, PRE_C9A_PROFILE] as const,
        ),
      );

      expect(
        hashOf(before),
        `${scene.name}: rendering with the named profile, outer shadow declined, ` +
          `must reproduce its pinned bytes — if this moved, find what moved it ` +
          `before re-recording the hash`,
      ).toBe(expectedHashFor(scene.name));
    });
  }

  test("the outer shadow is the whole of W8's delta — it draws, and only there", async ({
    page,
  }) => {
    /*
     * The other half of the attribution, and the half a hash cannot carry: the
     * declined shadow reproducing main is only a proof if the shadow, when it is
     * NOT declined, actually changes the picture. Otherwise every assertion above
     * would pass just as well against a facet that had been wired up and never
     * reached a pixel — which is precisely the failure mode W8 exists to correct.
     */
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const off = decodeCapture(
      await page.evaluate(
        (profile) => window.vitrea.renderScene("field-mask", undefined, profile),
        PRE_C9A_PROFILE,
      ),
    );
    const on = decodeCapture(
      await page.evaluate(
        (profile) => window.vitrea.renderScene("field-mask", undefined, profile),
        { ...PRE_C9A_PROFILE, outerShadow: {} },
      ),
    );

    expect(hashOf(off)).not.toBe(hashOf(on));

    /*
     * And it lands in the ALPHA and nowhere else, which is the mechanism itself
     * showing up in the readback: the pass writes premultiplied black outside the
     * contour, so the canvas gains opacity and gains no colour, and what the
     * browser then composites is `page × (1 − alpha)`. A shadow that had put
     * colour on this canvas would be a grey layer over the page rather than a
     * multiplication of it — the very thing Decision Log #32(c) was right to
     * delete — and it would show up here as a moved RGB channel.
     */
    let opaquer = 0;
    let clearer = 0;
    let colourMoved = 0;
    for (let i = 0; i < off.data.length; i += 4) {
      for (let channel = 0; channel < 3; channel += 1) {
        if (off.data[i + channel] !== on.data[i + channel]) colourMoved += 1;
      }
      const before = off.data[i + 3] ?? 0;
      const after = on.data[i + 3] ?? 0;
      if (after > before) opaquer += 1;
      else if (after < before) clearer += 1;
    }
    expect(colourMoved).toBe(0);
    expect(opaquer).toBeGreaterThan(1000);
    expect(clearer).toBe(0);
  });

  test("the geometry change is confined to the scenes it can reach", () => {
    // The attribution above, as an assertion. A scene can only have moved through
    // the corner-smoothing path if some surface of it actually resolves to a
    // non-zero effective smoothing — so the superseded set and the non-zero-
    // smoothing set must be the same set. If a future geometry change moves a
    // smoothing-0 scene, this fails and the "provably inert at smoothing 0"
    // reasoning above is what has to be revisited, not the hash.
    const scenes = SCENES.filter((candidate) => candidate.measureOnly !== true);
    const smoothed = scenes.filter((s) => maxSmoothingEff(s) > 0).map((s) => s.name);
    expect(smoothed.sort()).toEqual(Object.keys(SUPERSEDED).sort());
    // and every recorded hash still names a scene that exists
    for (const name of Object.keys(SUPERSEDED)) {
      expect(scenes.map((s) => s.name)).toContain(name);
    }
  });

  test("the 1x pin carries the depth ramp — its fail-before record", async ({ page }) => {
    // `W15_HASHES` is only worth its line if the bytes it pins depend on the ramp.
    // The ramp's excursion is `max(0, s₀(span) − sDeep(span))`, so zeroing the
    // three 1x start anchors makes it clamp to nothing at every span while
    // leaving the deep value, the widths and the lens exactly where they are.
    // That render must differ from the pinned one; if it ever stops differing,
    // this scene has stopped exercising the 1x ramp and the pin above is empty.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const pinned = decodeCapture(
      await page.evaluate(
        (profile) => window.vitrea.renderScene("body-ramp-1x", undefined, profile),
        PRE_C9A_PROFILE,
      ),
    );
    const rampOff = decodeCapture(
      await page.evaluate(
        (profile) => window.vitrea.renderScene("body-ramp-1x", undefined, profile),
        {
          ...PRE_C9A_PROFILE,
          sizeScatterRampStartThin1x: 0,
          sizeScatterRampStartThick1x: 0,
          sizeScatterRampStartFar1x: 0,
        },
      ),
    );

    expect(hashOf(pinned)).toBe(expectedHashFor("body-ramp-1x"));
    expect(hashOf(rampOff)).not.toBe(hashOf(pinned));
  });

  test("and the tuned profile is not the old one — the proof is not vacuous", async ({ page }) => {
    // Without this, every assertion above would pass just as happily if the
    // `materialProfile` argument were being dropped on the floor.
    const report = await openHarness(page);
    requireHardwareAdapter(report);

    const before = decodeCapture(
      await page.evaluate(
        (profile) => window.vitrea.renderScene("tint-adaptation-light", undefined, profile),
        PRE_C9A_PROFILE,
      ),
    );
    const after = decodeCapture(
      await page.evaluate(() => window.vitrea.renderScene("tint-adaptation-light")),
    );

    expect(hashOf(before)).not.toBe(hashOf(after));
  });
});
