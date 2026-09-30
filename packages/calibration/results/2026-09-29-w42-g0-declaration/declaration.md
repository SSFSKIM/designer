# W42 G0 — the declaration (readable twin of `declaration.json`)

Charter `docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md` v2.1 (main `0736ed64`),
clause 1; ledger §5.194. The machine record is `declaration.json`: 31 items, each declared once and
pointing at the stream file that defines it, with 89 source files pinned by SHA-256 (the charter
at `bc1e6bc6`, which records Decision Log 5f and the review's readings beside 5a and 5c).
`declare.py check` re-derives every count and list below from those files; `declare.py hash`
refuses while any item marked **PENDING (user)** has no ruling, then writes `declaration.sha256`
and `closure.json` and pins both in `bed/exposure/production-pin.json`.

**Status: not hashed.** The three items that waited on the user were RULED on 2026-09-30:
`candidate2Chroma` (i, Decision Log 5c), `l1TintedReceded` (ii, 5d) and `activeBandAndE2`
(iii, 5e). The review of `b151aff4` and its three fix waves are folded in (the streams'
`FIXES-b151aff4.md`), and the refraction-order rule (`refractionOrderNoCall`) was RULED on
2026-09-30 (Decision Log 5f). The hash waits for the remaining commits the parent is merging (the
instrument's correction, the reader replays, a second bed fix round). No native pixel of the new
bed exists.

Streams, merged no-ff into `w42-g0-declaration`: bed `764217e1`, instrument `a489cc02`, gate
`75f244ec`. Units: codes are 8-bit encoded output levels; lengths are points (CSS px) unless
marked device px; t = clamp((s − 64)/96, 0, 1), clamped at 1 above s = 160; d is SDF depth in
points, negative inside.

## The law and its rivals

### law

LT, all averaging in ENCODED sRGB. The capture S = F∗B on R_fp (the shape's box plus the margin:
active 0.35 s above s = 64, else 16 pt; receded one device px), F memo C's 0.8-device-px Gaussian
floor (1.6 on rrect-lg) before the knee, a declared constant. The narrow term C = G(σn)∗S with
σn = k·5 pt·o(s, d, pose): active 0.8t at the centre, falling linearly to 0.4t at 1 pt inside the
edge; receded 0.4 + 0.4t, flat in depth. The wide term W = G(k·8 pt)∗S on R_fp, clamp-to-edge when
active and normalised when receded. Light N = C + λ·max(0, W − C), dark the mirror; M = 0.5N + 0.5W.
y = T(M). **Two parameters per endpoint, k and λ.** Search: outer parameters by bounded Powell
from declared starts (LOCAL), λ inner per endpoint by golden section on [−0.5, 1.6], k in
[0.8, 4.0]; least squares at equal cell weight, refined by minimax on the region statistics. Every
family maps a constant backdrop to T(level). *Sources:* `instrument/forward.py`, `families.py`,
`fitting.py`, `proof_common.py`, `ref_check.json`.

### kNesting

Global k first: `k@global` (5 parameters in all), `k@scheme` (6; the "k shared across poses"
rival), `k@endpoint` (8; memo E's LT-1k), `k2@endpoint` (12; LT-2k). A less restricted level is
taken only where it beats the more restricted one by more than max(3, sum of bars). On synthetic
renders a global-k truth recovers at every level. **The bed does NOT separate endpoint k values
0.05 apart:** memo E's per-endpoint readings read with one k per scheme (the light pair, Δ 0.052)
miss region statistics by 0.43 (UNRESOLVED), and read with one k (Δ about 0.07) by 1.23
(MARGINAL). *Sources:* `instrument/families.py`, `proof1_families.txt`.

### rivals

Per endpoint: LT-2k 3; free-sn 7 (σn ordinates at s ≤ 64, 80, 96, 128, 160, flat in depth);
R1 2 (T on C and W before the fill); W-shape 3 (W alone on the rounded shape, margin μ ∈ [−8, 40]
pt; C stays on R_fp); W-canvas 2; W-tails 4 (s2 ∈ [17, 80] pt, a ∈ [0, 0.6]); K2 3 (sk ∈ [2, 40]
pt); C-linear 2 (discrete); the knee form 2 (discrete, `kneeForms`); edge-swap 2 (discrete); k
shared across poses (`kNesting`).

**The bleed, declared dump-literal** (memo D's inputs): radius k·0.35 s; colour
Q = black + (white − black)·sat(Bl) on encoded values; darkenBlend (a darken in light, a normal
blend in dark); weight ob·r(d) with ob 0.5t light / 0.8t dark (s > 64) and r falling from 1 at
the edge to 0 one height (0.35 s) inward; before or after T a discrete choice: **LT+bleed-lit-pre
2, -post 2, -own-pre 3, -own-post 3.** The review-era form stays as a **stated variant**,
LT+bleed 2 / LT+bleed-own 3: a Normal mix in both schemes, before T, one weight over the shape,
the matrix's affine part absorbed by native T, the saturation not taken. **The literal light bleed
moves no pixel of the bed** (≤ 0.000 codes before T, 0.024 after), so it cannot be light-active
U7's cause; in dark the literal forms are distinguished from LT both ways (5.5–11.0). The 22 dark /
2.3 light separations and LT → LT+bleed-own light 1.28 (marginal) are the Normal variant's. No
family is added after the bed's first read. *Sources:* `instrument/families.py`, `resolution.txt`.

### rejectedNulls

Re-run at the narrow mask, **by their declared pooled bars the unit nulls, R2 and the
light-active mixture are NOT refused** on this bed's synthetic proof: texel 1.71–2.61 and device
px 1.17–1.41 against ≥ 4.65, R2 1.71–2.84 against ≥ 4.65, the light-active mixture 2.56 against
≥ 2.60 (its other endpoints 2.78–4.13 pass). Their worst cells (8.5–12.7, 4.2–9.4, 9.3) are
descriptive. They are non-identifiable here (`nonIdentifiable`); at 2x a point is two device px
and, off rrect-lg, one texel, so **the 1x cells decide the unit in the sitting**. The literal box
decimation is descriptive (0.99 / 1.27 active, 0.41 / 0.43 receded); the floor stays declared.
Also rejected: memo A's C7, memo B's F1 and F2; F4, the shipped form, is the baseline.
*Sources:* `instrument/families.py`, `proof2_nulls.txt`, `proof2_floor_check.txt`.

### kneeForms

Three streams' labels, **one discrete choice**, equal in count, fitted on the bed and decided by
the survival rule with family E and every RGB-read cell answering: the charter's "per-channel
knee" row, the instrument's LT (`channel`) and its `knee-luma` rival, and the gate's `*p*` and
`*l*` rehearsal variants. The forms are **per-channel** (N and M per channel, chroma argument
M_rgb), **on-luma, whole colour** (the hinge decided on luma), and **on luma, chroma from W**
(the charter's candidate-1 light-receded form). On synthetic renders the luma form is
DISTINGUISHED from per-channel (9.6–18.5 codes at the narrow support, 2.6–3.2 at the W support);
round 3's best combination uses per-channel, and on-luma leaves Stop P's F band low. **RULED by the
parent (2026-09-30): a tie is carried as per-channel, because Apple's Lighten / Darken is
per-channel.** *Sources:* `instrument/forward.py`, `families.py`, `resolution.txt`,
`gate/rehearsal/body.py`, `gate/rehearsal/round3/README.txt`.

### accessibility

Reduce Transparency returns every W42 gate to its identity; `forced-colors` draws no body;
Increase Contrast alone does not stand the law down; the bed measures neither mode. *Source:* the
charter at `bc1e6bc6`.

### supersededLeaves

Superseded: the linear pyramid's share (`sizeScatter*`), `sizeHeavyTapSigma`/`…2x`, the dark
`scatterLod` path, `collapseTransmission`'s group / local mix, and the scatter's spatial-scale
conditioning, which conditions only that share. Candidate 1's landed T is the shipped solve's
uniform response evaluated per pixel at the law's argument, so every shipped operator inside it,
body chroma retention included, reads the argument as it reads a uniform backdrop of that colour
(the rehearsal's `landed_T`). D1, D2 and the F extension are gate-groups at identity; the frozen
macOS 26.5 pair never leaves it. **No G0 stream owned this item; it was declared at integration**
from the charter and the rehearsal's construction, and the parent kept it as proposed for the
independent review to read. *Sources:* the charter, `gate/rehearsal/body.py`.

## T and the candidates

### nativeT

Per endpoint and span stratum, the monotone piecewise-linear curve through family A's measured
ordinates (`tone.TableT`), with its inverse. Ordinates are 2x family-A calibration deep medians;
the 2x rrect-64 and 1x rrect-md greys are validation. Strata: t = 0 (every s ≤ 64, read on the
capsule), s = 80 (dark), 96, 128, 160. Identification only. *Sources:* `instrument/tone.py`,
`bed/bed.json`.

### candidate1

The LANDED T. Light active, dark active and dark receded: the shipped solve's uniform response per
pixel. Light receded: y = F(L(M))·1 + g(L(W))·v(W), with E3's F (ordinates 150, 157, 164, 171, 178,
188, 197 at 40…150) extended above 150 by family A's seven light-receded ordinates at 160, 176,
192, 208, 224, 240, 255 — its own family, count 7, its own gate-group. Those ordinates are read on
the capsule (t = 0, E3's own span), and the same levels on the larger shapes referee F's span
invariance: **ACCEPTED by the parent (2026-09-30).** Scored against the law composed with this
T; the gap to Apple's level is the named level miss. Rulings: L1 reads as written, so candidate 1
cannot land in light active; Decision Log 3's shipped-solve fallback for light receded is STRUCK;
the runner requires candidate 1 in every manifest. *Sources:* W41 G1's `light-inactive-E3-fit.json`,
`bed/bed.json`, `gate/rehearsal/README.txt`, `gate/rehearsal/body.py`.

### candidate2

Native T from family A in all four endpoints, **counted by its ordinates: 27 light active,
27 light receded, 30 dark active, 30 dark receded** (10 levels at t = 0, 10 at s = 96, 3 at
s = 128, 4 at s = 160; dark adds 3 at s = 80), **plus 1 chroma parameter per endpoint**
(`candidate2Chroma`, Decision Log 5c as the parent reads it). Lands instead of candidate 1 only if it passes every check
(X40). *Sources:* `bed/bed.json`, `instrument/tone.py`.

### candidate2Chroma

**RULED 2026-09-30 by the user (Decision Log 5c): "Yes, add it."** Candidate 2 carries W41
G1's E3-form g in all four endpoints, re-fitted and checked on the new bed's colour cells.

- Form: y = T(L(arg)) + g(L(arg))·(arg − L(arg)) in encoded values, arg the knee form's chroma
  argument (per-channel: M_rgb), T candidate 2's native T (rehearsal round 3 (a)–(b)).
- g: **W41 G1's fitted E3 curve** (E3's form: nodes 63, 93, 118, bounds [0, 3]; fitted on the W39
  archive's 102 uniform colour cells per endpoint) **times ONE per-endpoint scale: 1 parameter per
  endpoint**.
- Fit: the scale is re-fitted on the new bed's calibration colour cells (family E's isoluminant hue
  pairs) with the law held at its identified parameters, and checked on its validation colour
  cells (family E's hue transfer) at clause 6's bar.
- **The parent's reading (A3)** of "re-fitted and checked on the new capture's colour cells":
  family E sits at one luma (isoluminant at Rec.709 128), so it cannot re-identify g's three
  knots; one scale on W41 G1's curve is what it can re-fit.

The question as the parent put it: whether candidate 2 carries W41 G1's E3-form g in all four
endpoints, re-fitted and checked on the new bed's colour cells (options: it carries it / it does
not). Evidence (round 3 (b)): g was the only chroma that passed M1 in all four endpoints under
candidate 2; without it the shipped solve carries about a tenth of the backdrop's chroma.
*Sources:* `gate/rehearsal/round3/README.txt`, `swap.py`, W41 G1's four E3 fits, W41 G0's
`closure.json`.

## The instrument

### regionStatistics

Medians of output codes per channel over deep-mask populations: A's deep median; a checker's
per-square core medians (at least min(4, pitch/4) pt from every edge), knee or far side, and their
pooled medians; a patch's core and annuli at 0, 2, 4, 8, 16, 32, 48 pt; a step's plateaus beyond
48 pt and bins at ±2, 4, 8, 16, 24, 32, 48 pt; photo and text their deep median. At least 12 pixels.
Receded deep mask d ≤ −8 pt; active per `refractionOrder`. Per-cell rms is reported, never gated.
*Sources:* `instrument/regions.py`, `forward.py`.

### refractionOrder

Primary: refraction acts AFTER the blur. Active mask d ≤ −(20 + 2σn,ref): 20 on the capsule,
rrect-sm and rrect-64, 22.8 on rrect-80, 25.6 on rrect-md, 28.4 on rrect-112, 31.2 on rrect-ml,
36.8 on rrect-lg. No active cell is excluded any more: b1 captures the band-only cells receded
only, and `instrument/bed.py` refuses a bed that captures one active. **The test is v3**
(declared `79152643` before its proof). The test family F (LT, or the family surviving clause 6)
is fitted as the gated fit, and only 2x cells vote. **S1** is v2's D_tail (the mean of the 3
largest Δc over structured cells less the same over uniform cells): BEFORE above 0.30, AFTER
below 0.15. **S2** is the lens projection Â = 8·β of the voting cells' residual on F's own
response to an 8-pt stand-in lens before the blur: BEFORE at 8 pt or more, AFTER below 4 pt.
**Admission:** a statistic may decide only when F's pooled rms on Apple is below its P*, the
lowest residual at which a declared rival, rendered AFTER with no lens, makes it read other than
AFTER. **P*: light S1 0.549, S2 2.285 (the leg's top); dark S1 0.568, S2 1.086.** At memo E's LT
residual (2.25 light, 3.45 dark) no statistic is admitted in dark, and in light only S2, at the
leg's edge. Neither admitted is UNDECIDED: the order goes to the user before G2 fits the active
pose; Decision Log 5f then fits under both masks and lands only if they agree
(`refractionOrderNoCall`). Sensitivity: a 16-pt lens reads BEFORE and an 8-pt lens undecided.
The **fallback mask** is d ≤ −53.6 pt (rrect-ml and rrect-lg only). History: v1's median proved
powerless; v2's tail was sensitive and not specific. **v2 disclosure:** v1's carry counts (4 light
and 3 dark cells over 0.30 at 16 pt, none at 8 pt) were known when the tail was chosen and fixed its
outcome, so v2's proof confirmed what was known. *Sources:* `instrument/tolerances.json`,
`refraction_order.py`, `refraction_order.txt` (v2), `refraction_order.v3.txt`, `.v3.json`,
`forward.py`, `bed.py`.

### refractionOrderNoCall

**RULED 2026-09-30 by the user (Decision Log 5f): "Fit both; land only if they agree"** —
"Fit the focused law under both assumptions. If both give the same law within measurement
resolution, the order doesn't matter and it can land; if they differ, that focused state doesn't
land in W42 and the difference is recorded. Unfocused states are unaffected." The options
declined were "Assume after the blur" and "Assume before the blur" (the cautious reading, with
far fewer cells).

Operationally:
- **When.** A focused endpoint where v3 makes no call: UNDECIDED (neither statistic admitted, or
  both admitted and opposite), or the admitted statistic reading between its bars.
- **The two fits.** The surviving family is fitted as the gated fit, once under the narrow mask
  (refraction after the blur) and once under the 2σw mask (before the blur, 53.6 pt, rrect-ml and
  rrect-lg only).
- **Agreement.** The two fits agree iff every parameter's difference lies within that parameter's
  survival resolution in `instrument/resolution.*`, on the side of the difference's sign. For LT:
  light active k +0.0589 / −0.0582 and λ ±0.0314; dark active k +0.0494 / −0.0477 and λ ±0.0288.
- **Other families.** A surviving family other than LT has its resolutions computed by the same
  rule (the smallest move that shifts some region statistic by 1 code), at its narrow-mask fitted
  point, before the comparison.
- **Unidentifiable parameters.** A parameter the 2σw mask cannot identify cannot show agreement.
- **If they agree,** the endpoint may land with the narrow-mask fit.
- **If they differ,** that focused endpoint stays at the identity (Decision Log 3), and both fits
  and every difference are recorded.
- **Unaffected:** the receded endpoints. Where v3 makes a call (light, S2 admitted), the call
  decides as declared.
- **Integration proposals, for the parent's review:** the rule for other families, the
  unidentifiable-parameter reading, and the narrow-mask fit being the one that lands.

*Sources:* `instrument/refraction_order.v3.txt`, `tolerances.json`, `resolution.json`.

### instrumentGating

Gated: every family fitter, and the step reader's support / edge-mode call. Descriptive, misses on
record: S, per-cell λ, step σw, patch widths, ESF, single-width impulse, depth, heavy, model,
hinge-gap. Family fitters recover every parameter well inside their bars; the step call is
identical on capture and replica on 20/20; LT's survival resolution is k ±0.037–0.068, λ
±0.029–0.044. Continuing every separation row near the 1.5 line with three times the budget moved
s by at most 0.022, and no verdict. *Sources:* `instrument/tolerances.json`, `resolution.json`, `proof1_families.txt`,
`read_step.py`.

### nonIdentifiable

Declared before any fit: U3's active half; the box / shape / edge call from D's centred steps;
the depth law's 0.4t end; R1 in light unless T is curved over 144–255; dark 48/208 at spans ≥ 96
under the stand-in T; under the fallback only, the free σn ordinates at s ≤ 96 and active
rrect-md. Added by the review: **the dark-active refraction order with LT as the test family**
(decidable only if the surviving family fits Apple's active cells below about 1.1 codes); **the
unit nulls, R2 and the light-active mixture**, by their declared bars (the 1x pass decides units);
**the dump-literal light bleed and its k_b** (inert on this bed). *Sources:*
`instrument/README.md`, `bed/bed.json`.

### survivalBars

Seven runs. The bar per cell, region statistic and channel is 0.5 + half the largest pairwise
separation of the run medians, computed before plurality and published before G2. A family
survives only at max(1 code, bar) on every required channel of every calibration and validation
cell and region, through native T; survivors within max(3, sum of bars) are insufficient
resolution and go to `tieBreak`. X31's statuses, X21's censoring (≥ 250 or ≤ 5 one-sided). F is
bridge-only. An endpoint with no survivor is the wave's negative; Decision Log 3 applies.
*Sources:* the charter, `instrument/fitting.py`, `regions.py`, `bed/sitting/w42_archive.py`.

### tieBreak

Resolution first (a win by more than max(3, sum of bars) at an admitted discriminator); then
runtime cost, passes and texture reads on the WebGPU tier, including K1b's per-surface pyramid
cost (`renderer.ts:632–637`), priced for LT and its support rivals alike; then parameter count.
k: the most restricted level not rejected. Recorded outcomes: U3's active half keeps the box; the
bleed's Normal variant with its own radius in light (marginal) keeps LT by count, and the literal
light bleed cannot be told from LT; the knee forms per `kneeForms`. *Sources:* the
charter, `instrument/resolution.txt`.

## The bed and the split

### bed

447 glass cell-passes (2x 87 / 92 / 101 / 107, 1x 14 / 16 / 14 / 16), 264 run-1 references, every
id in `bed.json` generated by `declare-bed.py`. Grown from the charter's 414 by 10 s = 32 receded
rows, 28 separation-proof rows and 13 active guard rows, then **less 18 active cell-passes no
active reader reads (b1)**: the d4 patches, the capsule S 16 patches and D's outside steps leave the
active passes and stay receded. The two substitutions are ACCEPTED by the parent; the refraction
deviation is resolved by b1. Side-bundle checks pass (73 backgrounds; 144 of 146 rasters
re-rendered; self-check 82 ok). **Pre-sitting dumps (b7):** the 2x dark receded pass and the four
1x passes dumped with no grant, no departure, 8.33–8.37 s a scene. *Sources:* `bed/bed.json`,
scenes, `declare-bed.py`, `README.md`, `dumps/b7/b7.txt`.

### split

`bed.json` SHA-256 `53870f4703681644b00ffcfb5ba60a2fb3a9d1ebe25b5c793b99a0b8b3e50762` (scenes
`4aa06af9…`, twin audit `a7f2682e…`). Roles in the scenes file's own split: per 2x pass 63–81
calibration, 12–14 validation, 8 H, 4 F; per 1x pass 8–10, 2, 2, 2. **H**: eight cells, 40
cell-passes, six structured per 2x pass; P1 pitch 24 on **rrect-112, s = 112, a span no
calibration or validation cell has**. The twin audit finds no canonical holdout twin. **Near
twins, RULED by the parent (b8):** an exact-backdrop twin of a canonical holdout is refused and
the same geometry at other levels is allowed (a holdout protects its pixels, not its geometry;
the lc16 probe at that geometry was already read), so the pitch-16 active guard rows on rrect-lg
stand; and `b-p5-c64-rrect-lg` beside `h-p3-c64-rrect-lg` makes that H cell a level-pair
transfer test in the active 2x passes, the s = 112 H cells carrying the span test. `wave.py`
enforces the split, and the sitting's pin check refuses any launch whose scenes file or
`bed.json` differ from these SHA-256s in the hashed declaration. *Sources:* `bed/bed.json`,
scenes, twin audit, `pins.json`, `wave.py`, the four `dumps/s112/*/check.json`.

### webPlan

All 447 glass cells are web-plannable; every H cell has a rendered prediction. *Sources:*
`bed/web-plan.json`, `wave.py`.

### sitting

The sitting's first phase, after the user's one grant switch: dump-layers over the whole bed
(8 launches, 447 scenes; **no grant needed**; `STOP_AFTER=dumps` runs them alone). Then 2x at mode
68 and 1x at mode 69: **3,441 captures** (3,129 glass + 264 references + 48 sentinels) in 80
launches, seven runs, every X6 / X4 gate before every launch, quarantine and stop on any refusal,
never a retry. **About 10.31 h** (9.25 capture + 1.02 dumps). The orchestrator runs detached and
restores mode 68 on every exit; the driver refuses a launch it did not make; the pin check needs
the hashed declaration; PNGs are bound at admission; H's operational manifests carry attestation
fields only. *Sources:* `bed/sitting/*` (the orchestrator and its red / green records),
`bed/dumps/dumpcheck.py`, `dump-reference.json`.

### runtimeBase

40 WebGPU cells of the canonical bed; G2 requires PNG byte identity with the canonical tree before
any candidate render. *Source:* `bed/runtime-base-sample.json`.

## The gate

### gateReferees

W41 G2's ported cuts in candidate-admission mode. **L1 as written** (≤ 0.055 absolute, growth
≤ 0.005 against W33), with Decision Log 5d's four tinted receded cell-profiles as named growth
misses through the test's L1-growth named path (`GROWTH_RULED`, `growthVerdict`,
`GROWTH_MISSES`, empty today; A1). M1 as adopted. **M2 directional** (Decision Log 5a: `structureVerdict` in
`adopted-thresholds.test.ts`, pinned by the owner case, the 2 % unmoved). The parent's reading of
the user's words: "past it by more than 2 %" is read against Apple's own value, |w − n| / n, and
two seeds pin it. On this bed Apple's interior structure exceeds vitrea's on all 26 cells, so **M2
fails only on flattening**; wrong added texture is caught by Stop P and the eye sheets. Clause
12's exception now covers two derivations, M2's and L1 growth's. C1 ≤ 0.0042 per bed ×
span. X1 zero pixels above native black. E2 per cell, absolute (Decision Log 5e). Named misses stay
named, and none is added except through M2's path, Decision Log 5d's cells and 5e's bin list.
*Sources:* `gate/referees/*`, `gate/m2-named-miss/red-green.txt`, `adopted-thresholds.test.ts`.

### l1TintedReceded

**RULED 2026-09-30 by the user (Decision Log 5d): "Named misses."** The cells are recorded as
named misses caused by vitrea's unfocused (receded) tint layer; the L1 bound is unchanged, and
fixing the tint layer goes on W42's deferred list. The named misses, 1x and 2x each:
- `apple-macos-27.0-{1x,2x}-light-standard-glass0.5` `photo__rrect-md__inactive-tint-orange`;
- `apple-macos-27.0-{1x,2x}-dark-standard-glass0.5` `photo__capsule-button__inactive-tint-orange`.

They fail L1's growth clause (+0.0100 to +0.0138 under r3-2pgb) with absolute errors under 0.055.
`declare.py check` re-derives the four from r3-2pgb's receded tinted L1 failures; every
candidate-2 combination's receded tinted failures lie within them, and round 3's light ACTIVE
tinted failures occur only under candidate 1 (the landed T's level, [T1]). The committed owner test
carries L1 growth's named path (A1), and the owner runner inserts these four as the seal would, and
nothing else. The question as the parent put it: the reading of L1 on
the two light tinted photo rrect-md inactive cells and the dark tinted capsule inactive cell (options:
named misses, the tint layer deferred / read as written). *Sources:*
`gate/rehearsal/round2/tint.txt`, `round3/tint-dark.txt`, `round3/rehearsal-r3-detail.txt`.

### activeBandAndE2

**RULED 2026-09-30 by the user (Decision Log 5e): "Per cell, list the worse ones."**
- **The band:** the law is eased in across the active band with coverage × smoothstep(0, 20 pt,
  depth): 0 at the contour, 1 at the band's inner edge. The receded pose is unchanged.
- **E2, per cell:** over E2's own bins and population, the mean over the cell's measured bins and
  channels of the bin residual mean |web − native| in codes. A cell fails only if the candidate's
  mean exceeds the shipped render's: its edge moved farther from Apple overall. A cell with no
  measured bin is UNMEASURED, never a pass. **Zero tolerance, KEPT by the parent (A2):** both
  renders are byte-deterministic and share the native, so the per-cell difference is exact.
- **E2's named misses:** every measured bin that worsens by more than 1 code on any channel is
  listed (cell, bin, channel, shipped and candidate residuals); the list is recorded, never a gate.

The question as the parent put it: blending by coverage × smoothstep(0, 20 pt, depth), and how E2
reads (options: per cell in absolute codes with worse bins listed as named misses / per bin / the
band held). Evidence (r3-2pgb): 70 of 7,728 bins worse than shipped by more than a code, all at
2.25–5.75 CSS px under vitrea's lens; 838 improve. The blend changes spans ≤ 44 too (capsule mean
weight 0.48). *Sources:* `gate/rehearsal/round3/README.txt`, `e2abs.py`, `swap.py`.

### stops

Bar: dCand ≤ dShip + res per statistic, UNMEASURED never a pass. **Stop H**, 16 impulse cells:
peak, annulus and **floor** (the floor ring in absolute codes, G9) of encoded luma round the admitted
dot, res 1 code; a cell passes only if all three do. **Stop P**, 26 untinted photo cells: OKLab band
energies F = G(1) − G(4) and M = G(4) − G(16) over the deep body, res frozen per cell (0.12–0.28
×1e-3 on F, 0.032–0.074 ×1e-3 on M). Every non-shipped document must be declared, and a run naming
only the shipped documents is refused (G10). Proof 38/38. *Sources:*
`gate/stops/stops-declaration.json` (v2), `stops.py`, `halo.py`, `proof.txt`, `baseline.txt`.

### ownerTest

`run-owner.py` runs `adopted-thresholds.test.ts` on the base's and the candidate's scratch unions
over all six gated profiles; bar: no failure the base does not show. A run that replaces a gated
profile's document without staging its WebGPU pair refuses, and so does a base with any failing
case. Kept rows are relocated (the carried holdout never counts as kept). M2's and L1 growth's
named misses are inserted as the seal would. **The seal's edits, RULED by the parent
(2026-09-30):** a closing named miss is a pass and its list shrinks at the seal; a recorded entry
whose pinned reading moved is re-recorded; nothing is added outside the two named paths. Every edit
is logged, the test runs again, and that run is the result. *Sources:* `gate/owner/run-owner.py`,
`proof.txt`, `proof-inputs.py`.

### eyeStrata

204 cells: uniform 40, binary 38, text 48, impulse 16, photo 46, gradient 16; text and gradient are
looks. The grey middle has no uniform sheet unless the mid-* probe cells are admitted (the parent's
call, not taken). *Sources:* `gate/sheets/strata.json`, `sheets.ts`.

### rehearsal

Three rounds of memo A's body swap on the canonical captures. Best combination **r3-2pgb**
(candidate 2, per-channel knee, chroma g, blended band): dark active passes every referee but E2.
Still failing by construction: light active [U7], the marginal [P1] and **[HF]**, Stop H's floor
on the 1x light active tinted impulse capsule 0.14 code past its allowance in every candidate-2
blended combination. All three are read through the active swap's unmeasured error (1.59–2.07
codes rms on 2x checkerboard-8 rrect-lg), and G2's real renders decide them. Also failing: light
receded [LT] (the tinted cells, now named; s = 32 M2; Stop P 2/8), dark receded [DT] (the tinted
capsule, named), and E2 in every active combination. M2 joins the [SEAM] list: the active-pose M2
"named" readings are seam-driven. To the user: items (i), (ii), (iii), all RULED on 2026-09-30
(Decision Logs 5c–5e). *Sources:* `gate/rehearsal/README.txt`, `round2/README.txt`,
`round3/README.txt`, `round3/rehearsal-r3.txt`, `round3/stopH-floor.txt`.

## The exposure

### exposureRunner

ONE receipt binds the law (through native T), candidate 1 (required) and at most one candidate 2,
their blind rendered H predictions frozen by hash and recaptured equal inside it. Scope **423 of
447** cell-passes (the 24 bridges excluded), 40 of them H. The law closes iff every measured H cell
of every claimed endpoint passes at max(1 code, bar), with at least one measured cell each;
censored H cells are UNMEASURED; X40 selects candidate 2 if landable. Before `begin` the runner
refuses if the receipt log has history on any ref or origin carries the marker tag, then pushes the
marker atomically, so only one checkout can expose H (b9). `declare.py hash` pins this declaration
and `closure.json` in `production-pin.json`; G1 pins the inventory. Proof: 34 / 34. *Sources:*
`bed/exposure/runner.py`, `README.md`, `green-fixes.txt`, `b9-proof.txt`.

## Errata (kept beside the bytes they correct)

- `bed/bed.json` `charterDeviations`: the first two entries still read "substituted, flagged for
  the parent's ruling" and "declared as a grid". The parent ACCEPTED both. `bed.json` is left
  byte-identical because the split's SHA-256 (`9047c8da…`) binds it; the rulings are recorded in
  item `bed` and in ledger §5.194 §8.
