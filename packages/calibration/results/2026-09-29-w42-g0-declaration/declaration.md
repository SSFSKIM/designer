# W42 G0 — the declaration (readable twin of `declaration.json`)

Charter `docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md` v2.1 (main `0736ed64`),
clause 1; ledger §5.194. The machine record is `declaration.json`: 30 items, each declared once and
pointing at the stream file that defines it, and 74 source files pinned by SHA-256 (the charter
at `0736ed64`). `declare.py check` re-derives every count and list below from those files;
`declare.py hash` refuses while any item marked **PENDING (user)** has no ruling, then writes
`declaration.sha256` and `closure.json` and pins both in `bed/exposure/production-pin.json`.

**Status: not hashed.** Three items wait on the user: `candidate2Chroma` (i),
`l1TintedReceded` (ii) and `activeBandAndE2` (iii). No native pixel of the new bed exists.

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
renders a global-k truth recovers at every level; the bed separates endpoint k values more than
about 0.05 apart. *Sources:* `instrument/families.py`, `proof1_families.txt`.

### rivals

Per endpoint: LT-2k 3; free-sn 7 (σn ordinates at s ≤ 64, 80, 96, 128, 160, flat in depth);
R1 2 (T on C and W before the fill); W-shape 3 (margin μ ∈ [−8, 40] pt); W-canvas 2; W-tails 4
(s2 ∈ [17, 80] pt, a ∈ [0, 0.6]); K2 3 (sk ∈ [2, 40] pt); C-linear 2 (discrete); the knee form 2
(discrete, `kneeForms`); LT+bleed 2; LT+bleed-own 3; edge-swap 2 (discrete); k shared across poses
(`kNesting`). No family is added after the bed's first read. *Sources:* `instrument/families.py`,
`resolution.txt`.

### rejectedNulls

The mixture reading (passes memo E's ≥ 2.60, pooled 2.68–4.61); radii in texels and in device px,
and R2 (each fails the declared pooled ≥ 4.65 on the mostly-2x bed and is refused on its worst
cells: 9.8–12.7, 8.5–11.1, 2.7–6.2; only the 1x pass referees the unit); the literal box
decimation (descriptive: 2.1 / 3.1 pooled on the active fine pitches at the narrow support, the
floor stays declared). Also rejected: memo A's C7, memo B's F1 and F2; F4, the shipped form, is
the baseline. *Sources:* `instrument/families.py`, `proof2_nulls.txt`, `proof2_floor_check.txt`.

### kneeForms

Three forms of one discrete choice, equal in count, decided by the survival rule with family E
and every RGB-read cell answering: **per-channel** (the instrument's LT; the gate's `*p*`
variants, chroma argument M_rgb); **on-luma, whole colour** (the instrument's `knee-luma`); **on
luma, chroma from W** (the gate's `*l*` variants; the charter's candidate-1 light-receded form).
The charter calls per-channel the rival; the instrument calls it LT. On synthetic renders the luma
form is DISTINGUISHED from per-channel (9.6–18.5 codes narrow support, 2.6–3.2 W support); round 3's
best combination uses per-channel, and on-luma leaves Stop P's F band low. **Integration proposal,
for the parent's review:** a tie within resolution carries per-channel, which is what the dump's
declared Lighten / Darken composites compute. *Sources:* `instrument/forward.py`, `families.py`,
`resolution.txt`, `gate/rehearsal/body.py`, `gate/rehearsal/round3/README.txt`.

### accessibility

Reduce Transparency returns every W42 gate to its identity; `forced-colors` draws no body;
Increase Contrast alone does not stand the law down; the bed measures neither mode. *Source:* the
charter at `0736ed64`.

### supersededLeaves

Superseded: the linear pyramid's share (`sizeScatter*`), `sizeHeavyTapSigma`/`…2x`, the dark
`scatterLod` path, `collapseTransmission`'s group / local mix, and the scatter's spatial-scale
conditioning, which conditions only that share. Candidate 1's landed T is the shipped solve's
uniform response evaluated per pixel at the law's argument, so every shipped operator inside it,
body chroma retention included, reads the argument as it reads a uniform backdrop of that colour
(the rehearsal's `landed_T`). D1, D2 and the F extension are gate-groups at identity; the frozen
macOS 26.5 pair never leaves it. **No G0 stream owned this item; it is declared at integration**
from the charter and the rehearsal's construction. *Sources:* the charter, `gate/rehearsal/body.py`.

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
192, 208, 224, 240, 255 — its own family, count 7, its own gate-group. **Integration proposal, for
the parent's review:** those ordinates are read on the capsule (t = 0, E3's own span), and the same
levels on the larger shapes referee F's span invariance. Scored against the law composed with this
T; the gap to Apple's level is the named level miss. Rulings: L1 reads as written, so candidate 1
cannot land in light active; Decision Log 3's shipped-solve fallback for light receded is STRUCK;
the runner requires candidate 1 in every manifest. *Sources:* W41 G1's `light-inactive-E3-fit.json`,
`bed/bed.json`, `gate/rehearsal/README.txt`, `gate/rehearsal/body.py`.

### candidate2

Native T from family A in all four endpoints, **counted by its ordinates: 27 light active,
27 light receded, 30 dark active, 30 dark receded** (10 levels at t = 0, 10 at s = 96, 3 at
s = 128, 4 at s = 160; dark adds 3 at s = 80). Lands instead of candidate 1 only if it passes every
check (X40). *Sources:* `bed/bed.json`, `instrument/tone.py`.

### candidate2Chroma

**PENDING (user).** *(i) Chroma:* whether candidate 2 carries W41 G1's E3-form g in all four
endpoints, re-fitted and checked on the new bed's colour cells.
- Option 1: it carries W41 G1's E3-form g in all four endpoints, re-fitted and checked on the new
  bed's colour cells.
- Option 2: it does not.

Evidence (round 3 (b)): g on encoded luma, knots 63 / 93 / 118, fitted on 102 W39 uniform
calibration cells per endpoint (max residual 0.71 / 0.93 / 1.09 / 1.54 codes), is the only chroma
that passes M1 in all four endpoints under candidate 2. Without it the shipped solve carries about
a tenth of the backdrop's chroma: dark M1 0.32–0.46 receded, 0.63–0.77 active; Stop P's M band
fails 4/4 dark and 6–10/10 light active. The literal face-matrix saturation is the wrong amount
everywhere. *Sources:* `gate/rehearsal/round3/README.txt`, `swap.py`, W41 G1's four E3 fits.

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
36.8 on rrect-lg; cells whose content lies only in the 20-pt band or the 19.2-pt outer reach leave
the active fit. The rival, BEFORE, is tested on Apple's pixels: fit at the primary mask, bin the
luma residual by depth ([d_in, 30), [30, 38), [38, 46), [46, 54), [54, ∞)), Δc = rms(NEAR) −
rms(FAR) (NEAR the shallowest bin of ≥ 200 px, FAR the deepest at least 16 pt deeper), D_tail = the
mean of the 3 largest Δc over structured cells minus the same over uniform cells. **BEFORE above
0.30, AFTER below 0.15, undecided between;** a BEFORE or undecided call goes to the parent before
the **fallback mask, d ≤ −53.6 pt** (rrect-ml and rrect-lg only), is taken. Proof: AFTER reads
+0.05; the test resolves between an 8- and a 16-pt lens. The first, median statistic proved
powerless and was superseded before its successor's proof. *Sources:* `instrument/tolerances.json`,
`refraction_order.py`, `refraction_order.txt`, `forward.py`, `bed.py`.

### instrumentGating

Gated: every family fitter, and the step reader's support / edge-mode call. Descriptive, misses on
record: S, per-cell λ, step σw, patch widths, ESF, single-width impulse, depth, heavy, model,
hinge-gap. Family fitters recover every parameter well inside their bars; the step call is
identical on capture and replica on 20/20; LT's survival resolution is k ±0.037–0.068, λ
±0.029–0.044. *Sources:* `instrument/tolerances.json`, `resolution.json`, `proof1_families.txt`,
`read_step.py`.

### nonIdentifiable

Declared before any fit: U3's active half; the box / shape / edge call from D's centred steps; the
depth law's 0.4t end; R1 in light unless T is curved over 144–255; dark 48/208 at spans ≥ 96
under the stand-in T; under the fallback only, the free σn ordinates at s ≤ 96 and active rrect-md.
*Sources:* `instrument/README.md`, `bed/bed.json`.

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
k: the most restricted level not rejected. Recorded outcomes: U3's active half keeps the box;
light LT+bleed-own (marginal) keeps LT by count; the knee forms per `kneeForms`. *Sources:* the
charter, `instrument/resolution.txt`.

## The bed and the split

### bed

465 glass cell-passes (2x 95 / 92 / 109 / 107, 1x 15 / 16 / 15 / 16), 282 run-1 references, every
id in `bed.json` generated by `declare-bed.py`. Grown from the charter's 414 by 10 s = 32 receded
rows, 28 separation-proof rows and 13 active guard rows. The two substitutions (1x P1 pitch 32 on
rrect-lg for a canonical holdout twin; rrect-lg's centre S 8 as the 64-pt grid) are ACCEPTED by the
parent. Side-bundle checks: backgrounds, raster read-back, self-check and dump-layers pass.
*Sources:* `bed/bed.json`, `scenes-w42-body.json`, `declare-bed.py`, `README.md`.

### split

`bed.json` SHA-256 `9047c8da871f60b432dfe454e783a86634c9444d74e3a98f534f016e3684b176` (scenes
`e2c532d9…`, twin audit `a7f2682e…`). Roles in the scenes file's own split. **H**: eight cells,
40 cell-passes (8 per 2x pass, 2 per 1x pass), six structured per 2x pass; P1 pitch 24 on
**rrect-112, s = 112, t = 0.5, a span no calibration or validation cell has**, accepted by the side
bundle with no rebuild. The twin audit finds no canonical holdout twin and no validation or H cell
twinning any earlier bed. `wave.py` enforces the split. *Sources:* `bed/bed.json`, scenes, twin
audit, `pins.json`, `wave.py`, the four `dumps/s112/*/check.json`.

### webPlan

All 465 glass cells are web-plannable; every H cell has a rendered prediction. *Sources:*
`bed/web-plan.json`, `wave.py`.

### sitting

dump-layers over the whole bed first (8 launches, 465 scenes), then 2x at mode 68 and 1x at mode
69: 3,585 captures in 80 launches, seven runs, every X6 / X4 gate before every launch, quarantine
and stop on any refusal, never a retry. About 10.73 h (9.63 capture + 1.06 dumps). *Sources:*
`bed/sitting/*`, `bed/dumps/dumpcheck.py`, `dump-reference.json`.

### runtimeBase

40 WebGPU cells of the canonical bed; G2 requires PNG byte identity with the canonical tree before
any candidate render. *Source:* `bed/runtime-base-sample.json`.

## The gate

### gateReferees

W41 G2's ported cuts in candidate-admission mode. **L1 as written** (≤ 0.055 absolute, growth
≤ 0.005 against W33). M1 as adopted. **M2 directional** (Decision Log 5a: `structureVerdict` in
`adopted-thresholds.test.ts`, pinned by the owner case, the 2 % unmoved). C1 ≤ 0.0042 per bed ×
span. X1 zero pixels above native black. E2 per `activeBandAndE2`. Named misses stay named.
*Sources:* `gate/referees/*`, `gate/m2-named-miss/red-green.txt`, `adopted-thresholds.test.ts`.

### l1TintedReceded

**PENDING (user).** *(ii) Tinted receded cells:* the reading of L1 on the two light tinted photo
rrect-md inactive cells and the dark tinted capsule inactive cell, which are named misses caused by
vitrea's receded tint composite (light and dark `photo__…__inactive-tint-orange`, 1x and 2x).
- Option 1: read as named misses, the tint layer deferred (the parent's recommendation).
- Option 2: read as written: they fail.

Evidence: the tint composite carries the untinted body's change into the tinted cell (light
0.0288 + 0.7312u, dark 0.0202 + 1.4398u). Under r3-2pgb the untinted twins come within
0.004–0.005 of Apple while the tinted cells grow +0.0108 / +0.0100 (light) and +0.0138 / +0.0133
(dark). *Sources:* `gate/rehearsal/round2/tint.txt`, `round3/tint-dark.txt`,
`round3/rehearsal-r3-detail.txt`.

### activeBandAndE2

**PENDING (user).** *(iii) The active band:* blending by coverage × smoothstep(0, 20 pt, depth),
and how E2 reads:
- Option 1: per cell in absolute codes, with worse bins listed as named misses.
- Option 2: per bin.
- Option 3: the band held.

Evidence: E2's adopted reading fails every active combination (its deep-median reference moves).
Held, no bin changes, so E2 reads nothing, and the 20-pt seam fails Stop H and Stop P. Blended
(r3-2pgb), 70 of 7,728 bins are worse than shipped by more than a code (worst 3.27), all at
2.25–5.75 CSS px under vitrea's lens, and 838 improve. The blend changes spans ≤ 44 too (capsule
mean weight 0.48): a correction owed to the user. *Sources:* `gate/rehearsal/round3/README.txt`,
`e2abs.py`, `swap.py`.

### stops

Bar: dCand ≤ dShip + res per statistic, UNMEASURED never a pass. **Stop H**, 16 impulse cells:
peak and annulus of encoded luma round the admitted dot, res 1 code. **Stop P**, 26 untinted photo
cells: OKLab band energies F = G(1) − G(4) and M = G(4) − G(16) over the deep body, res frozen per
cell (0.12–0.28 ×1e-3 on F, 0.032–0.074 ×1e-3 on M). Proof 30/30. *Sources:*
`gate/stops/stops-declaration.json`, `stops.py`, `proof.txt`, `baseline.txt`.

### ownerTest

`run-owner.py` runs `adopted-thresholds.test.ts` unmodified on the base's and the candidate's
scratch unions over all six gated profiles; bar: no failure the base does not show. Kept rows are
relocated, the holdout carried, M2 named misses inserted as the seal would. A named miss that
closes reads as a change (`MISSED_27_ROWS`, L1's named list): a closure the seal must record.
*Sources:* `gate/owner/run-owner.py`, `proof.txt`.

### eyeStrata

204 cells: uniform 40, binary 38, text 48, impulse 16, photo 46, gradient 16; text and gradient are
looks. The grey middle has no uniform sheet unless the mid-* probe cells are admitted (the parent's
call, not taken). *Sources:* `gate/sheets/strata.json`, `sheets.ts`.

### rehearsal

Three rounds of memo A's body swap on the canonical captures. Best combination **r3-2pgb**
(candidate 2, per-channel knee, chroma g, blended band): dark active passes every referee but E2.
Still failing by construction: light active [U7] and a marginal [P1]; light receded [LT] (the
tinted cells, s = 32 M2, Stop P 2/8); dark receded [DT] (the tinted capsule); E2 in every active
combination. To the user: items (i), (ii), (iii). *Sources:* `gate/rehearsal/README.txt`,
`round2/README.txt`, `round3/README.txt`, `round3/rehearsal-r3.txt`.

## The exposure

### exposureRunner

ONE receipt binds the law (through native T), candidate 1 (required) and at most one candidate 2,
their blind rendered H predictions frozen by hash and recaptured equal inside it. Scope 441 of 465
cell-passes (the 24 bridges excluded), 40 of them H. The law closes iff every measured H cell of
every claimed endpoint passes at max(1 code, bar), with at least one measured cell each; censored
H cells are UNMEASURED; candidate 2 is scored against Apple, candidate 1 against its own frozen
prediction with its level miss recorded; X40 selects candidate 2 if landable. Any fault after
`begin` spends H. `declare.py hash` pins this declaration and `closure.json` in
`production-pin.json`; G1 pins the inventory. Proof: 26 red, 27 green. *Sources:*
`bed/exposure/runner.py`, `README.md`, `green-guard.txt`.
