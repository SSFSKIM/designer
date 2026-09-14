# W28 — the footprint response: the inactive material's abscissa under the surface, and what structure adds beyond it

**Status: CLOSED 2026-09-15 — all five gates run; six of seven acceptance clauses MET, clause 7
PARTLY, the exception named. G0 CLOSED 2026-09-14, not identifiable (§5.144); Decision Log 2 rules
the simplest survivor built and the bound as referee; G1 CLOSED 2026-09-14 (§5.145), fitted and
sealed; G2 CLOSED 2026-09-14 (§5.146), the unchanged bound holds on six of six, merged `237465fa`;
Decision Log 3 lifts W27c's hold — G3 (the runtime) CLOSED 2026-09-15 (§5.147); G4 (the landing)
CLOSED 2026-09-15 (§5.148). W27c's held runtime and landing are closed with it. Release status:
`0.18.0 PREPARED, UNPUBLISHED` — the user's eye on the six G2 sheets is still the veto before the
cut, and `pnpm release` is the user's hand. The machine stays on macOS 26.5.2 and the OS 27 decision
returns with the identifying sitting, which was priced and not taken.**

Parent: `2026-09-10-w27-coverage-wave.md` (Decision Logs 17 and 20, §Deferred, Outcomes clause 1
"window focus is measured but not shipped"); `2026-08-28-post-v1-wave.md` post-close addenda
(the handed-forward order names this work first). Ledger: `c9a-fidelity-claims.md` §§5.130,
5.134, 5.136, 5.139, 5.141, 5.143 (the inactive record) and §§5.30–5.34 (W9, the response law).
Tracker: "The window-activation runtime is held behind the inactive response" and "The inactive
endpoint's dark thin response at a bright backdrop is wrong by 0.78 Y" carry the executable
handoff and the residual this wave takes up.

## Purpose

W27c measured Apple's receded (window-inactive) material on a native checking bed of 188 cells,
fitted the endpoint documents, and then held the runtime that would apply them: the bound declared
before the bed existed (§5.134 §6) holds on four of six profiles and fails on both light standard
profiles, on one cell, `hc-text__rrect-sm__inactive`, at 2.44× and 2.15× its per-cell floor. The
recomposition (W27 Decision Log 20) refused to ship the recede on the four profiles that hold —
the failing pair is the one an adopter's first surface ships on — and named "a structure-aware
inactive response" as the work that closes the hold.

The grounding for this charter reads that name against the ledger and finds that the mechanism is
already identified, and was deferred, in W9. W9's probe established the response law — the
material's settled interior is a function of the backdrop's **encoded-space mean** (P3, RMS 0.0400
against the linear-mean model's 0.1070; claims §5.31) — and in the same read found that *the
reference takes that mean under the footprint, not over the source*: the pitch-64 `rrect-sm` cell
whose footprint sat inside one white checker cell rendered white-adapted (0.9632 native,
footprint-predicted 0.9713) where any source mean would have predicted about 0.61. W9's Decision
Log 2 shipped the source-level mean on both tiers "with no new constants", named "a dedicated
encoded-space pyramid for true per-footprint GPU means" as the escalation, and §5.34 recorded the
cost as residual class 1: "small footprints over structured backdrops (+0.05…0.09, worsening with
pitch): the per-source tone input reads the whole backdrop where the reference reads the
footprint". `hc-text__rrect-sm__inactive` — the smallest component over the brightest
high-frequency backdrop — is that class, in the pose whose response curve is steepest.

Both tiers still take one abscissa per backdrop source: the WebGPU analysis pass averages a fixed
64 × 64 grid over the chain level nearest a 96 px short side and publishes one encoded mean per
group (`wgsl/analysis.ts`, `pyramid-plan.ts`); the CSS tier averages one 512 px `drawImage`
downsample of the whole source (`backdrop-tone.ts`). Under `hc-text` the source mean is 0.7400 for
every component, but a 64 × 32 body over 14 px rows with 6 px bars covers two or three bars
depending on where it sits, and the reference answers to what it covers. The bed already shows it:
on every uniform backdrop the capsule and the small square read the same native interior to five
decimals; on `hc-text` they read 0.70985 and 0.54849 (light) and on `photo` 0.58816 and 0.54120,
at one and the same source mean.

The wave's purpose is therefore in two parts, in order. First, **the footprint abscissa**: the
response's input becomes the encoded mean of the backdrop under the surface — on the WebGPU tier
per pixel off the pyramid at a level the reading selects, on the CSS tier per surface from the
region under the host's rect — as an additive, profile-gated mechanism the receded documents opt
into and the active documents do not, so the active material stays byte-identical in this wave.
Second, **what structure adds beyond it**: with the abscissa corrected, the remaining structured
residual (W9's H4, −0.011 to −0.013 on the active pose; unmeasured on the recede) is read, and a
contrast term is given a law only if that residual is above the bed's own noise. The dark middle
knots the bed measured and no gate has yet refitted (thin 0.089 against 0.04092, thick 0.065
against 0.0331 at encoded 0.2706) are refitted in the same pass, since the same arrays carry them.
Then the unchanged §5.134 §6 bound is applied once on one sealed configuration; if it holds on all
six profiles, W27c's G2 and G3 land as this wave's last two children, and the recede ships.

## Parent-Level Acceptance

Binding. Numbers are the ledger's; a child that finds one wrong re-declares it in its own section
before it fits.

1. **The abscissa is decided by reading, not by fitting, and never on the checking set.** Before
   any constant moves, G0 shows from the committed background rasters and the committed native
   fixtures — nothing captured, nothing compared against vitrea — which abscissa orders the native
   interior across structured cells: (a) the source mean, (b) the mean under the eroded body,
   (c) the mean under the silhouette, (d) the mean under the silhouette dilated by r over a ladder
   of r, and (e) the per-pixel backdrop blurred at scale σ over a ladder of σ, averaged over the
   body. The statistic is curve-free: the RMS residual of native body Y after a monotone
   (isotonic) regression on each predictor, per scheme and thickness row, so no response curve —
   and no structured cell's outcome — enters the comparison. **The selection population excludes
   group D and `checkerboard__rrect-ml__inactive` entirely**: it is the recovered inactive bed's
   structured thin and thick cells outside D (§5.130's group E / calibration cells) plus the
   active pose's structured cells (the canonical bed and the 56-cell W9 probe, where the footprint
   effect was first seen). G0's script refuses a D id by name. A predictor is selected only if its
   residual beats the runner-up's by more than the bed's own repeat noise (the plurality's
   inter-run spread; one 8-bit code, 0.004 Y, on the recovered bed); otherwise the verdict is "not
   identifiable from this bed" and the wave stops at Decision Log 2. The uniform native points are
   a check on the selected map, not its definition. Whether the abscissa's kind and scale are the
   same on both poses is stated as an assumption of the reading and tested at G2, not assumed
   silently.
2. **The abscissa G0 selected lands on the WebGPU tier profile-gated, reproduces its predictor
   before anything is fitted, and the active material is byte-identical.** A `MaterialProfile`
   field selects the abscissa — absent or `"source"` is today's arithmetic bit for bit; the
   alternatives are the per-surface region mean (b/c/d) or the per-pixel mean at a scale (e),
   whichever G0 selected, and G1 builds that one, not both. Every active document resolves
   unchanged, `resolvedMaterialSha256` unmoved, the renderer goldens 34 / 34 without regeneration,
   the isolation spec's hashes untouched; only the receded documents opt in. The new branch is
   consistent through the whole solve: the same local reference feeds the response, the collapse
   compensation, the nominal composition and the opacity solve, because the shader composites
   against the local backdrop and a branch that swaps only the response's input renders
   `R(local) + (1 − α)(local − source)`, not `R(local)`. **The mechanism check:** on the
   selection population's structured cells the implemented branch's rendered body Y reproduces
   G0's predictor prediction within the bed's repeat noise before any row is refitted; a branch
   that does not is not the mechanism G0 selected and is not fitted around. The CSS tier derives
   what one `rgba()` layer can carry — a per-surface mean under the host's rect — and the gap to a
   per-pixel abscissa, if that is what won, is written as the X1 residual with its measured size.
   If G0 selects the source mean, the locality premise is rejected for the recede, the finding is
   the ledger section, and the wave stops at Decision Log 2.
3. **The fit never selects on the checking set.** The bound scores group D of the 2026-09-11 bed
   and nothing else (§5.134 §6 scope). Every constant this wave fits — the abscissa's scale, the
   refitted dark middle knots, the light row under the new abscissa, and any structure term — is
   selected on calibration and non-D probe cells only; the twelve group D ids plus
   `checkerboard__rrect-ml__inactive` are predictions at the read. A fit that needs a D cell to
   converge stops and says so.
4. **The bound holds on all six profiles**, applied once, unchanged, clause by clause, from the
   2026-09-11 `bound.json` on one sealed configuration (resolved SHA-256s frozen, holdout declared
   unread before the first page opens, machine settings 0 / 0 on every browser run), by the same
   `score-bound.py` lineage. Holding is clauses 1–3 jointly on every profile. If any profile fails,
   the wave stops at that read: G2 does not relax the bound, and shipping on a subset is not this
   wave's to decide (W27 Decision Logs 17 and 20).
5. **No inactive floor is adopted from probe-bar evidence** (W27 Decision Log 13). G3's inactive
   rows enter the matrix as scene `state` (X3) and are published; a floor is adopted only for a
   regime whose cells are frozen at the seventeen-run bar, which none is today.
6. **The runtime is W27c G2 as chartered**, not re-designed: the activation observer following
   `document.hasFocus()` with an explicit override that wins, the framework-agnostic
   `windowActivation` root option and `setWindowActivation`, the React `<GlassRoot>` prop, the
   pose applied through `applyMaterialProfile` as two frozen endpoints (X7), the transit through
   the existing transitions, tests on three engines, README paragraphs on both packages, the demo
   showing the recede when its window is backgrounded.
7. **By eye, and the ledger.** Native | WebGPU | difference sheets at both scales for every profile
   at the read, and the demo's backgrounded pose beside the harness capture at the landing; the
   user's veto. Every gap that remains is a named line under X8 with its size and the shape of the
   work that would close it. The cut after the landing is one `@vitreajs/vitrea-web` minor.

## Grounding Baseline (main at `7a174b54`, 0.17.0 published)

- **The bed.** `packages/calibration/results/2026-09-11-w27-26.5-run/` (38 inactive ids × four
  standard profiles, 14 × two accessibility profiles, seven runs each, macOS 26.5.2, `.accessory`
  pose attested per cell) plus G1d's eight `mid-light-solid` cells under the dark profiles. 28 of
  the 38 ids are over structured backdrops (`checkerboard` at pitches 4–64 and the low-contrast
  `lc16`, `hc-text` at row heights 7 / 14 / 28, `impulse`, `photo`), 10 over uniform ones.
  Split: 3 holdout (spent by G1), 4 calibration, 31 probe. Group D, the checking set the bound
  scores: `hc-text__rrect-sm`, `hc-text__rrect-lg`, `hc-text-7__rrect-md`, `hc-text-28__rrect-md`,
  `checkerboard-lc16__capsule-button`, `checkerboard-lc16__rrect-md`, `checkerboard-4__rrect-md`,
  `dark-solid__rrect-48`, `dark-solid__rrect-80`, `light-solid__rrect-ml`,
  `dark-solid__rrect-md-clear20`, `checkerboard__rrect-ml` (all `__inactive`).
- **The native thin rows by source mean** (`2026-09-13-w27c-g1c-fit/identifiability.json`,
  `2026-09-14-w27c-g1d/native-response.json`; linear Y over the body eroded 6 CSS px):

  | encoded source mean | backdrop | light thin | dark thin |
  | ---: | --- | ---: | ---: |
  | 0.1104 | dark-solid (uniform) | 0.01171 | 0.01171 |
  | 0.2706 | mid-dark-solid (uniform) | 0.45079 | 0.04092 |
  | 0.4254 | photo, capsule / rrect-sm | 0.58816 / 0.54120 | 0.11154 / — |
  | 0.5000 | checkerboard, capsule / rrect-sm | 0.60854 / 0.60954 | 0.11700 / — |
  | 0.5490 | mid-light-solid (uniform; dark only) | — | 0.12214 |
  | 0.7000 | checkerboard-lc16, capsule | 0.78645 | 0.13853 |
  | 0.7400 | hc-text, capsule / rrect-sm | 0.70985 / **0.54849** | — / **0.08985** |
  | 0.9504 | light-solid (uniform) | 0.93261 | 0.93261 |

  On uniform backdrops the capsule and the square agree to five decimals; on `photo` and `hc-text`
  they differ by 0.047 and 0.161 Y at one source mean. That divergence is the footprint's, and it
  is what a source-level abscissa cannot express at any knot.
- **The failing cell and its neighbours at the G1d head** (`frozen-checking-matrix.json`, body Y
  web / native, body ΔE): light 1x `hc-text__rrect-sm` 0.7228 / 0.5485, **0.0779** (2.44×);
  light 2x 0.7388 / 0.5690, **0.0731** (2.15×); dark 1x the same cell 0.1334 / 0.0899, 0.0652
  (group D, under its 0.082 cap). Beside them, unscored because they are supplying cells (group A):
  dark `mid-dark-solid__rrect-sm` 0.0887 / 0.0409, 0.1013 and `mid-dark-solid__rrect-md` / `-lg`
  0.0648 / 0.0331, 0.0806 — the measured middle knots that no gate has refitted, kept at G1's
  0.089 / 0.065 because G1c's counterfactual showed releasing them alone does not reach `hc-text`
  and because the source-mean checker control moves with them. Dark `impulse__rrect-ml` / `-lg`
  0.043 / 0.0155, 0.101. The largest readings on the bed, `mid-chroma-solid` at 0.10–0.20 on both
  poses, are the **active** material's chroma transfer (§5.139 §5; the tracker) and are out of this
  wave's scope by that finding.
- **The response as implemented.** Monotone Fritsch–Carlson Hermite in encoded x through three or
  four knots (`material.ts` `backdropToneResponse`, mirrored term for term in `wgsl/optics.ts`
  `tone_response` and `platform-web/src/optics.ts` `backdropToneResponseLevel`), thin and thick
  rows blended by `smoothstep(0, 1, sizeThickness)` with `sizeThickness = smoothstep(32, 96, span)`,
  clamped to the knot span, authority fading to 0 below the first anchor. The abscissa on the
  WebGPU tier: `stats[0]`, the encoded mean of a 64 × 64 bilinear grid over `analysisLevel` (the
  chain level nearest a 96 px short side), decoded once, low-passed at 500 ms; the optics pass
  multiplies the per-pixel tap by `backdropToneLevel / backdropToneLinearLuminance` so the field
  keeps its locality while its mean matches the model. The CSS tier: `sampleBackdropTone`, one
  alpha-weighted encoded mean over a ≤ 512 px downsample of the whole source, cadence 250 ms. The
  reduction already computes `variance` and `edgeDensity`, consumed by nothing (W9 grounding).
- **The receded documents** (`platform-web/src/receded-profile.ts`): two fixed endpoints per
  scheme. Light: three-knot rows thin `[0.0126, 0.4, 0.929]`, thick `[0.4553, 0.518, 0.9]` over the
  default anchors `[0.1104, 0.2706, 0.9505]`; `refractionScale.approximate` 0;
  `increasedOcclusionLift` 0.96 with `increasedOcclusionLiftByPolicy` 0.88 / 0.98;
  `strongBorderRim` width 1, alpha −3.5. Dark: four-knot anchors `[0.1104, 0.2706, 0.7, 0.9505]`,
  thin `[0.011, 0.089, 0.1, 0.9326072]`, thick `[0.0215, 0.065, 0.060877, 0.11753]`. Common: rim,
  shadow and tint chroma zeroed, scatter ramps moved.
- **The bound** (`2026-09-11-w27c-g1b/bound.json`; scorer lineage ending at
  `2026-09-14-w27c-g1d/score-bound.py`): clause 1 per-cell full-canvas ΔE at the active bed's
  adopted ceilings 0.07 / 0.07 / 0.09 / 0.09 / 0.06 / 0.04 (light 1x, light 2x, dark 1x, dark 2x,
  IC, RT); clause 2 the checking set's mean body ΔE at or below the frozen read's validation mean
  0.032 / 0.034 / 0.034 / 0.041 / 0.0078 / 0.011; clause 3 no checking cell above 2× its clause-2
  threshold, a cell that exceeds it named and blocking any floor for its regime. Verdict history of
  the unchanged bound: 2 / 6 (§5.139), 3 / 6 (§5.141), 4 / 6 (§5.143).
- **Cost of native evidence.** A full 188-cell round at the probe bar is 3.5 h of the machine
  before attempt loss and 4.5–8.7 h with it (§5.136 §7). G1d's four cells per scale ran 554–790 s
  (2x) and 908–1142 s (1x) per run, seven runs per scale, about 3.5 h in all. macOS 27 has shipped;
  the machine is on 26.5.2 and every 26.5 cell that will ever exist must be captured before it
  updates.
- **W9's own numbers for the mechanism** (§5.31, §5.33, §5.34): pitch does not matter (P3 residual
  +0.024 ± 0.003 from pitch 4 to 64); P3 predicts 80–90 % of the equal-mean checker/uniform
  divergence (−0.148 predicted against −0.182 on `rrect-sm`); the unmodelled contrast term H4 is
  −0.011 to −0.013, "an order of magnitude below the phenomenon P3 explains"; residual class 1,
  small footprints over structured backdrops, +0.05…0.09 worsening with pitch.

## Design (advisory unless marked)

**The abscissa is a place before it is a number (binding as to what G0 must decide).** Five
predictor families of the native interior, all computable today from the background raster and
`componentRegion`: the source mean (what ships); the mean under the eroded body; the mean under the
silhouette; the mean under the silhouette dilated by r, for r from 0 to the body's span (a blur
under the surface reaches past its edge, and on 1x `hc-text` the square's body mean is 0.6988
where its silhouette mean is 0.5110 — the two predictors order the square and the capsule in
opposite directions, so the region is the question, not a detail); and the backdrop blurred at σ
then read per pixel and averaged over the body, for σ over the same ladder. No response curve is
used to compare them: the light uniform curve has no point between encoded 0.27 and 0.95, and a
curve that admitted structured cells would let the outcomes shape their own explanation. The
statistic is the RMS residual after isotonic regression of native body Y on the predictor, per
scheme and thickness row, over the selection population (acceptance 1); the uniform points must
then lie on the selected map, which is the check. What decides: the family and scale with the
lowest residual by more than the repeat noise, provided one scale serves both schemes; a residual
after it that is flat across pitch and contrast says the region was the whole answer, a residual
that grows with contrast at fixed region mean is H4 and gets its own gate; a tie is "not
identifiable", and the sitting or a stop follows. G0 reads the active pose's cells as part of the
selection population and reports, under X8, what the selected abscissa would do to the active
material, without this wave acting on it.

**The mechanism on the WebGPU tier (advisory as to how; conditional on G0).** If a per-surface
region wins (b, c or d): one encoded-space reduction per surface over its region at the analysis
level — the analysis pass already reduces a grid over a level; it gains a rect and a dilation and
runs per surface rather than per source — published to the optics pass as that surface's local
reference. If the per-pixel family wins (e): an encoded-space statistic at the selected level
carried beside the luminance pyramid (the chain is built from linear samples, so the per-pixel
encoded mean at level L is not the encode of the linear mean at L; W9's "dedicated encoded-space
pyramid" is this candidate), or, if G0's ladder shows the difference is below noise on this bed,
the existing linear tap at L encoded per pixel. In every case the local reference replaces the
source mean wherever the solve uses it — `toneAnchor.w` in the collapse compensation, the nominal
composition and the opacity solve — not only in `tone_response`, and the source branch keeps the
old arithmetic untouched behind the profile field `backdropToneAbscissa` (absent or `"source"` =
today; `{ kind, scale }` = the new branch). The receded documents set it and nothing else does.

**The CSS tier derives the per-surface half (advisory).** `sampleBackdropTone` gains a rect: the
mean under the host's rect (the batched read protocol already knows it) rather than the source's.
That carries the footprint mean, not a per-pixel abscissa, and on a body whose backdrop is not
uniform under it the two differ by a Jensen term the reading can size — recorded under X1.

**The fit (advisory as to order, binding as to exclusion).** With the abscissa in place, the rows
are refitted on calibration and non-D probe cells: the dark middle knots to the measured
0.04092 / 0.0331 unless the checker control, now footprint-sampled, refuses them; the light row
between 0.27 and 0.95 to the structured cells' footprint means; the fourth knot's position and the
dark step re-examined under the new abscissa, since the T1 sweep was made against source-mean
controls. Controls carry the same 9× cap on their G1d body-ΔE baseline. The accessibility levels
(0.88 / 0.98) and `refractionScale.approximate` 0 are not reopened unless the accessibility rows'
own cells move under the abscissa. The holdout is declared before the fit from probe cells the fit
never sees, with at least one cell per scheme whose footprint mean differs from its source mean by
more than 0.05.

**A sitting, if the reading asks for it (the user's).** Two things no committed fixture can
answer: where the dark thin step sits between encoded 0.74 and 0.95 (real windows sit over 0.8–0.9
content more often than over anything else in the bed), and whether a footprint whose bars fall
differently — the same `hc-text__rrect-sm` offset by half a row — moves the native interior by what
the footprint predictor says it should. Two uniform neutral patches (encoded ≈ 0.80 and ≈ 0.88)
under `rrect-sm` in both schemes, and one phase-shifted `hc-text` square in both, is six cells per
scale; at G1d's rate that is roughly 3–5 h of the machine for both scales at the probe bar, and it
is the last 26.5 capture this line of work needs. Priced here; decided at Decision Log 2 after G0.

**The runtime and the landing are W27c's, unchanged (binding).** The W27 spec's G2 and G3 text is
the charter for G3 and G4 here; this document adds nothing to their scope and removes nothing.

## Children

### G0: The abscissa read — controlled, native-only, nothing spent — CLOSED 2026-09-14: NOT IDENTIFIABLE (§5.144; merged `679cee90`; ruled by Decision Log 2)

- **Purpose:** decide, from committed rasters and committed native fixtures, where the reference
  takes the response's input and how much structure adds beyond it, on the recede and on the active
  pose.
- **Acceptance:** (1) the selection population declared first and committed before any number is
  read — every structured native cell outside group D and `checkerboard__rrect-ml__inactive`, on
  both poses: the recovered inactive bed's cells, the canonical active bed's, and the W9 probe's,
  with the id list and the reason each is admissible; the script refuses a D id by name; (2) the
  five predictor families computed for every cell in that population from the fixture manifest's
  background rasters and `componentRegion`, the r and σ ladders at no fewer than six rungs from 0
  to the body's span; (3) the isotonic residual per predictor × scheme × pose × thickness row, the
  repeat-noise bar stated from the plurality records, and the verdict: a selected family and scale,
  or "not identifiable"; the uniform points shown on the selected map; (4) the residual after the
  selected predictor classified — flat, or growing with contrast at fixed region mean, with the
  numbers — and a recommendation: which mechanism G1 builds, whether the abscissa is the same on
  both poses, whether the sitting is needed and which cells would decide what; (5) the ledger
  section written, the evidence directory
  `packages/calibration/results/2026-09-14-w28-g0-abscissa/` with the population file, the script,
  its JSON and the tables; (6) no vitrea capture, no comparison against vitrea, no constant moved,
  no fixture touched, **no D cell's native fixture opened**.
- **Contracts:** X1 (record only), X8.
- **Size:** 8–12 agent-hours.
- **Ledger:** claims §5.144.

### G1: The footprint abscissa on both tiers, and the rows refitted — controlled — CLOSED 2026-09-14 (claims §5.145; endpoint sealed, G2 unread)

- **Purpose:** the mechanism, profile-gated; the receded rows refitted under it on non-D cells;
  declared and dry-run.
- **Acceptance:** acceptance 2 and 3 above, the mechanism check passed on the selection
  population before the first row is refitted (its table in the evidence directory); unit pins
  that GPU and CSS read the same abscissa kind from the same document; `tier-coherence.test.ts` and the dom
  floors unchanged at rest; the holdout declared unread; the fitted endpoint's SHA-256s and patch
  digest frozen in `fitted-endpoint.json`; a dry run of the whole G2 read (`DRY`-style: every
  refusal exercised, no page opened for a holdout cell). *Under Decision Log 2 the mechanism is
  fixed as the per-surface silhouette mean (G0's simplest surviving candidate), and the mechanism
  check is on the INPUT, not the output: the branch's per-surface abscissa, exposed as a readout,
  equals G0's `per-cell.json` silhouette encoded mean for every selection-population cell within
  one 8-bit code, on both tiers.*
- **Edges:** blocked-by G0; blocks G2.
- **Contracts:** X1, X8.
- **Size:** 20–30 agent-hours.

### G1s: The sitting — the user's hand; opened only by Decision Log 2

- **Purpose:** the six cells per scale named in §Design, captured under the existing runbook at the
  probe bar, published beside the bundle with nothing pre-existing changed, declared `probe`.
- **Acceptance:** as G1d's capture record (declaration before capture; 26.5.2; accessibility 0 / 0;
  granted bundle not rebuilt; `VITREA_SCENES` for the spec; seven runs per scale, every cell
  attested inactive; `materialize --frequency-settle`; `round-trip.json` zero old entries changed).
- **Edges:** blocked-by Decision Log 2; blocks G2's holdout if taken.

### G2: The read — controlled — CLOSED 2026-09-14 (§5.146; unchanged bound holds on all six profiles)

- **Purpose:** acceptance 4, applied exactly as §5.143 §5–6 did: freeze, read the holdout once,
  score the unchanged bound with the same scorer lineage, six sheets by eye, CSS coherence
  recorded, no floor adopted.
- **Acceptance:** the verdict table for six profiles; holdout cells captured exactly once; machine
  0 / 0 on every browser run; `eye.md`; the ledger section. **Stop rule:** any profile failing any
  clause ends the wave at this gate with the failure named; G3 is not dispatched.
- **Edges:** blocked-by G1 (and G1s if taken); blocks G3.
- **Contracts:** X1, X7, X8.
- **Size:** 6–10 agent-hours.

### G3: The runtime — W27c G2 as chartered — controlled — CLOSED 2026-09-15 (Decision Log 3; claims §5.147)

- **Purpose and acceptance:** acceptance 6, verbatim from the W27 spec's W27c G2 and the tracker's
  handoff entry. Framework-agnostic first, React over it; three engines; changeset (a
  `@vitreajs/vitrea-web` minor and a `@vitreajs/vitrea-react` minor in the fixed group).
- **Edges:** blocked-by G2 holding on six; blocks G4.
- **Contracts:** X2, X7.
- **Size:** 12–20 agent-hours.

### G4: The landing — W27c G3 as chartered — CLOSED 2026-09-15 (§5.148); the cut prepared, the user's eye still the veto

- **Purpose and acceptance:** acceptance 5 and 7: inactive rows in the canonical matrix as scene
  `state`, `PREDICATE_EXCLUDES` equal to the machine's output, no floor adopted for any probe-bar
  regime, the demo's backgrounded pose with the harness capture beside it, README and playground,
  the matrix re-scored (§3.6 window focus state to `replicated+measured`), the eye sheets, the
  recomposition against this document's seven clauses, one minor cut prepared.
- **Capture handoff from G3 (§5.147):** G3 pins calibration roots to `"active"` and retains
  `web/scene.ts`'s candidate receded merge, with 16/16 before/after captures byte-identical.
  G4 replaces that scene-pose seam: the inactive rows it publishes must be captured through
  the runtime's `"inactive"` root pose, with `applyMaterialProfile` applying the receded document.
  It also supplies the capture's colour scheme to the root: the current harness passes a dark
  active patch but leaves the root's scheme at its light default. G4 proves those captures
  byte-identical to G2's frozen matrix before writing a row, so the matrix records what ships.
  The active document's SHA remains the cell key's profile identity.
- **Edges:** blocked-by G3.
- **Contracts:** X2, X3, X8.
- **Size:** 12–16 agent-hours.

## Cross-Child Contracts

Inherited from the W27 spec by name and unchanged: **X1** (the tier boundary: every measured claim
is on the WebGPU tier; the CSS tier derives and its residual is written), **X2** (public surface is
a semver event), **X3** (scene axes extend the set, never the key grammar), **X7** (activation is a
root pose with two frozen endpoints), **X8** (what was not measured is written down). Added here:

- **X10 — the checking set is never a selection cell.** Owner: this document. Binds G0, G1 and
  G2. Group D and `checkerboard__rrect-ml__inactive` are read at G2 and at no other time: not as a
  fit cell, not as a sweep control, and not as a native target in G0's predictor selection — a
  native-only reading that minimises residuals on D still trains on D's outcomes. G0's population
  file is committed before its script runs and the script refuses a D id; the fit script refuses a
  D id; `score-bound.py`'s `scored == (scene in D)` assertion is the last lock, and it checks
  scoring membership only, which is why the first two exist.
- **X11 — the active material does not move.** Owner: G1. Every active document resolves to the
  same `resolvedMaterialSha256`; goldens 34 / 34 without regeneration; the isolation spec's
  hashes unchanged; the canonical matrix's active rows byte-identical at the landing. The
  footprint abscissa's effect on the active pose is a ledger line (G0), not a change.

## Ordering & Dependency Map

G0 → Decision Log 2 (sitting or not) → G1 (mechanism may start with G0; the fit's holdout waits
on the ruling) → [G1s] → G2 → G3 → G4 → cut. Nothing here blocks the motion-metrics harness or
the OS 27 recapture except that the machine must remain on 26.5 until G1s is either taken or
declined.

## Risks & Mitigations

- **The footprint explains less than expected and the residual is a structure term.** Then G0's
  classification says so with numbers and G1 gets a second candidate (a contrast-dependent term on
  the response's authority, fed by the reduction's dormant `variance` / `edgeDensity`) — but only
  with a law the reading supports, and the wave is allowed to stop at Decision Log 2 rather than
  invent one.
- **The per-pixel abscissa changes the active look when adopted later.** Contained by X11 now;
  G0's active reading sizes the later decision.
- **The pyramid has no encoded statistic and building one costs a pass.** Candidate (ii) is the
  fallback; G0's ladder bounds its error before G1 commits.
- **Cross-tier drift.** The CSS tier carries a per-surface mean; the Jensen gap is measured and
  recorded under X1, and the coherence pins compare like with like.
- **The sitting is declined and the light row between 0.55 and 0.95 stays unpinned by uniform
  points.** The fit uses structured cells' footprint means; X8 records that the dark step's
  position is bracketed (0.74, 0.95) and not measured.

## Deferred / Out of Scope

**The identifying sitting** (Decision Log 3 (e)): the abscissa's kind and scale — silhouette mean
versus its 1/32 and 1/16 dilations, and whether it is the same on both poses — remain unidentified;
the experiment G0 designed (two fresh phase placements of the text square, a contrast pair matched
in encoded region mean, two bright uniform patches near 0.80 and 0.88 for the dark step; about
twelve cells at 1x, four to six hours at the probe bar) needs a 26.5 machine and is priced, not
chartered. The active material's chroma transfer over saturated backdrops (§5.139 §5; the tracker); the
active pose's footprint abscissa (recorded by G0, acted on by a later wave); dark accessibility, 2x
accessibility, the `clear` variant and the stack regime as inactive evidence classes (W27 §Deferred,
unchanged); any inactive floor (needs the seventeen-run bar); the `strongBorderRim` one-pixel
contour under Increase Contrast and Reduce Transparency's backdrop-dependent slope (§5.143 §8,
named, not this wave's); the motion-metrics harness; the OS 27 recapture; `prominent`.

## Tracking Map

| child | status | claims | evidence |
| --- | --- | --- | --- |
| G0 | CLOSED 2026-09-14 — not identifiable; merged `679cee90` | §5.144 | `results/2026-09-14-w28-g0-abscissa/` |
| G1 | CLOSED 2026-09-14 — input check passed, rows fitted, endpoint sealed; G2 unread | §5.145 | `results/2026-09-14-w28-g1-silhouette/` |
| G1s | NOT TAKEN — declined at Decision Log 2, moved to §Deferred by Decision Log 3 (e) | — | — |
| G2 | CLOSED 2026-09-14 — 188 WebGPU rows, six holdouts read once, bound holds on six of six; 182 CSS coherence rows | §5.146 | `results/2026-09-14-w28-g2-read/` |
| G3 | CLOSED 2026-09-15 — root pose and bindings shipped; three-engine activation verified; review clean | §5.147 | `results/2026-09-15-w28-g3-runtime/` |
| G4 | CLOSED 2026-09-15 — runtime-pose seam proved byte-identical, 470 inactive rows published, no floor, sheets and re-score, 0.18.0 prepared and unpublished | §5.148 | `results/2026-09-15-w28-g4-landing/` |

## Decision Log

### Decision Log 1 — the charter (2026-09-14; the parent, on the user's choice)

Asked after 0.17.0 published which wave to charter next — the structure-aware inactive response,
the motion-metrics harness, or the OS 27 recapture — the user chose the inactive response, and
the machine stays on 26.5.2. The parent's grounding reads the W27 spec's name for this work
against the ledger and rules: (a) the mechanism this wave builds first is W9's deferred
per-footprint abscissa, because the bed already shows the capsule and the square diverging on
structured backdrops at one source mean and agreeing to five decimals on uniform ones, and because
the failing cell is W9's residual class 1 by definition; (b) "structure-aware beyond the scalar
mean" is read as W9's H4 and gets a law only if G0 finds it above the bed's noise once the
footprint is accounted for; (c) the reading comes before any fit and spends nothing, so the wave
can stop at Decision Log 2 with only a ledger section if the reading says the recede is a
structure term the bed cannot identify; (d) the active material is held byte-identical (X11), the
mechanism profile-gated, so W27c's hold can lift without reopening eighteen waves of active fits;
(e) the fit is forbidden the checking set (X10), so the bound's verdict at G2 remains a prediction;
(f) the sitting is priced and left to the user at Decision Log 2; (g) G0 is dispatched now under
claims §5.144, later sections assigned at dispatch. Rejected: fitting a structure term directly on
the residual without the abscissa read (would fit W9's residual class 1 as if it were H4); shipping
the runtime on the four holding profiles (W27 Decision Logs 17 and 20 stand); updating the machine
to macOS 27 before the sitting is decided.

*Amended the same day on the adversarial review of this charter, before G0 dispatched.* Four
findings, all taken: (1) G0 as first written selected the abscissa on the checking set's native
outcomes, which X10 forbids in substance if not in letter — the selection population now excludes
group D on both poses and G0's script refuses a D id; (2) the light "uniform curve" would have been
completed by the structured cells it was meant to explain — the selection statistic is now
curve-free (isotonic residual) and the uniform points are a check on the selected map; (3) the
design precommitted G1 to a per-pixel mechanism G0 might not select — G1 now builds whichever
family wins, a per-surface region mean being the simpler eligible one, and the wave stops if the
source mean wins; (4) "the change is what `tone_response` is fed" ignored that the solve uses the
source mean in the collapse compensation, the nominal composition and the opacity solve and then
composites against the local backdrop — the local reference must replace it everywhere, and a
mechanism check on the selection population precedes any refit. The review also measured, from the
committed rasters, that on 1x `hc-text` the square's silhouette mean is 0.5110 and its body mean
0.6988 against the capsule's 0.6026 and 0.5293 — the region choice reverses the predicted order —
which is why the dilated-silhouette family was added to G0.

### Decision Log 2 — G0's verdict ruled: build the simplest survivor and let the bound judge (2026-09-14; the user, on the parent's recommendation)

G0 (claims §5.144, merged `679cee90`) read the abscissa from 398 committed native cells with the
checking set excluded and a curve-free statistic, and returned **not identifiable from this bed**:
locality lowers the clean light-active thin isotonic RMS from 0.087204959 (source) to
0.011413806 (silhouette), but the runner-up gap is 0.002036644 against the declared 0.004 Y bar;
the light-inactive thin row ties body with Gaussian 1/32 and the dark-inactive thin row, six
cells, prefers the source; and the bed carries no contrast axis at matched abscissa (largest
body-contrast-SD difference 0.000024540389 over 123 pairs), so H4 is untestable rather than
absent. Three candidates remain noise-compatible on every clean row: the silhouette mean and the
silhouette dilated by 1/32 and 1/16 of span. The charter's acceptance 1 sends that verdict here.

Put to the user with three paths — build the simplest survivor and let the bound judge; take a
predeclared identifying sitting first (two fresh phase placements of the text square, a contrast
pair matched in encoded region mean, two bright uniform patches, about twelve cells at 1x, four
to six hours of the machine); or stop W28 — the user chose the first. **Ruled:** (a) G1 builds
the **per-surface silhouette mean** in encoded space as the abscissa, profile-gated
(`backdropToneAbscissa`), the active material byte-identical (X11); (b) the mechanism check is
on the input — the branch's per-surface abscissa readout equals G0's per-cell silhouette mean on
the selection population within one 8-bit code on both tiers — because G0 selected no curve and
an output check would smuggle one in; (c) the receded rows are refitted under it on non-D cells
with the same control cap and a holdout declared from probe cells the fit never sees, and the
unchanged §5.134 §6 bound at G2 is the referee: on the checking set it is a genuine prediction of
a candidate the reading could not select, which is a test and not a fit to an assumption;
(d) if G2 fails on any profile, the wave does not refit toward the checking set — the identifying
sitting above becomes the next ruling, and the machine stays on 26.5.2 until then; (e) G1 is
dispatched under claims §5.145, evidence `results/2026-09-14-w28-g1-silhouette/`; G2's number is
assigned at its dispatch. **Rejected:** the sitting first (four to six hours of the user's machine
to separate three candidates whose difference the bound may already decide for free); stopping
(the reading bounded the answer to three candidates — that is progress the hold should use); the
dilated candidates (no evidence prefers them and the silhouette is the one both tiers can carry
exactly). The acceptance-2 stop clause ("if G0 selects the source mean") did not fire: the source
won one six-cell row and lost the populous ones by an order of magnitude.

*Addendum (f), the same day, on G1's pre-fit question — the holdout's scope.* No dark inactive non-D
cell has a silhouette-minus-source offset above 0.05 (the largest are `photo__capsule-button`
at 0.03734 and `checkerboard-64__rrect-lg` at 0.03046), so the §Design requirement of one such
cell per scheme cannot be met from the bed in dark; and the light `hc-text__capsule-button__inactive`
(offset 0.137) is the manifest's `holdout`, spent by §5.130's read of G1's configuration. Ruled:
the holdout rule is one read per frozen configuration, so a cell spent against G1's endpoint and
never fitted on is admissible as W28's holdout provided the fit does not see it — the light
holdout takes `hc-text__capsule-button__inactive`; the dark holdout takes the two largest-offset
non-D inactive cells, and X8 records that its discriminating offset is bounded at 0.037, the real
dark test of the abscissa being the checking set's own `hc-text__rrect-sm__inactive` at G2. No
capture is added for this. *(Corrected by G1 the same day, the original kept: the photo capsule's
offset is 0.03734347805587751 at 1x and 0.03800814795956453 at 2x, so the bound is 0.038 across
scales; both below 0.05, holdout and threshold unchanged.)*

### Decision Log 3 — the bound holds on six; the hold lifts; the runtime is dispatched (2026-09-15; the parent, under Decision Log 2's rule)

G2 (claims §5.146, merged `237465fa`) ran the reader G1 sealed exactly once — 188 WebGPU rows, the
six holdouts admitted once, no guard refusal, no resumption; 182 CSS rows record-only with every
holdout excluded — and scored §5.134 §6's bound of 2026-09-11 unchanged, group D reconstructed
independently by the scorer. **It holds clauses 1–3 jointly on all six profiles**, 72 / 72
checking cells under their per-cell caps: dark 1x 0.01584 / 0.034, dark 2x 0.01114 / 0.041, light
1x 0.01277 / 0.032, light 2x 0.01111 / 0.034, Increase Contrast 0.00278 / 0.0078, Reduce
Transparency 0.00600 / 0.011 on clause 2, every clause-1 worst under its ceiling. The cell that
held W27c, light `hc-text__rrect-sm__inactive`, is the closest: **0.05932 / 0.064** at 1x and
**0.05455 / 0.068** at 2x, from 0.07793 and 0.07310 at G1d — under its cap by 7 % and 20 %, and
still visibly too bright on the sheet. The holdouts: light `hc-text__capsule-button` 0.01746 /
0.02665 at an offset of −0.137, the two dark cells 0.026–0.054 at offsets 0.030–0.038.

Decision Log 2 made this read the referee: a candidate the reading could not select, tested on
a checking set the fit never saw. It held. **Ruled:** (a) W27c's hold (W27 Decision Logs 17 and
20; the tracker's "The window-activation runtime is held behind the inactive response") lifts on
this evidence — G3, W27c's G2 verbatim, is dispatched under claims §5.147 and G4 follows it;
(b) the record says what the bound says and no more: holding is not pixel identity, the eye's
residuals stand as named in §5.146 (the small text control's level, structured transfer and
rim/lens bands on the large panes, the low-contrast checker's amplitude in dark, the one-pixel
contour under Increase Contrast, Reduce Transparency's backdrop-dependent slope), and the
abscissa's kind and scale remain unidentified — the silhouette mean is the candidate that passed,
not Apple's law; (c) no inactive floor is adopted (W27 Decision Log 13; `fitted-endpoint.json`'s
`adoptsNoFloor`), and G4 publishes the inactive rows as scene `state` without one; (d) the user's
eye on the six G2 sheets (`results/2026-09-14-w28-g2-read/sheets/`) is requested now and is the
veto before G4's cut, not before G3, which changes no material; (e) the identifying sitting is no
longer a gate's fallback and moves to §Deferred as the experiment that would identify the abscissa
— it still needs 26.5, so the machine stays on 26.5.2 until the wave closes and the OS decision
returns then; (f) G3's ledger number is §5.147, G4's assigned at its dispatch. **Rejected:** a
second read to widen the margin on the text cell (the holdout is spent for this configuration);
tightening the bound after seeing it hold (the bound was declared before the bed existed and is
applied as written, in both directions).

## Surprises & Discoveries

- 2026-09-15 (G4, §5.148): **the driver, not the engines, was holding the document focused.**
  Making another application frontmost through LaunchServices, with the page under Playwright,
  leaves `document.hasFocus()` true and the root `active` — because Playwright turns Chromium's
  focus emulation on for every page it owns, so a suite does not break when the developer clicks
  away. That is also G3's `bringToFront()` finding, seen from the other side. Launching the same
  binary directly and speaking CDP over a bare socket gives the true answer on the first try:
  `hasFocus` false, root `inactive`, and `visibilityState` still `"visible"` — the case the
  observer was designed around and had never been able to witness. Consequence: every automated
  activation test in the repository is synthetic by necessity, on all three engines, and the one
  real reading is a manual-class script.

- 2026-09-15 (G4, §5.148): moving the calibration seam to the runtime pose moved **no pixel** —
  354 of 354 inactive cells and 60 of 60 active captures byte-identical — but it could easily have
  moved one, in a place that has nothing to do with the material. The host's box sizing is chosen
  from the drawn abscissa, and under the runtime pose the abscissa lives in the receded difference
  the ROOT merges rather than in the document the page hands it; a decision reading only the host
  profile would have captured every inactive cell in the wrong box. The page's own geometry
  decisions have to follow the merge, not the option.

- 2026-09-15 (G4, §5.148): the playground could not draw the dark receded endpoint at all. It
  passed no `colorScheme`, so it drew the light material whatever the system said — invisible for
  two waves because the page's own chrome is dark either way, and visible the moment two sheets of
  the same page in two schemes came out identical. The recede's endpoints are fitted per scheme, so
  the acceptance harness needed the scheme under the reader's hand before it could demonstrate the
  pose it exists to demonstrate.

- 2026-09-15 (G3, §5.147): headed Playwright `bringToFront()` on a second page leaves
  the original document's `hasFocus()` true on Chromium, Firefox and WebKit. The tests state
  their synthetic focus feed explicitly rather than using visibility as a proxy. Real unfocused
  test documents (notably jsdom) now correctly recede by default, so material fixtures pin their
  active pose. The unchanged calibration candidate-merge path is byte-identical on 16 before/after
  capture pairs across both schemes and tiers; G4 owns replacing it with the runtime pose.

- 2026-09-14 (G1, §5.145): the raw silhouette input passes 335/335 unpressed canonical cells
  on each tier, with maximum GPU discrepancy 0.02723997831346303 eight-bit codes. The old
  analysis mip would shift checker/text inputs by as much as 0.13629209995269775 encoded;
  locality alone is not enough if linear blur precedes encoding. CSS also enlarged a declared
  120 × 44 content-box host to 122 × 46 with its transparent border. A silhouette-only
  border-box harness correction fixes that geometry while eight source capture pairs remain
  byte-identical. First-stage review found redundant raster work and three boundary defects;
  the separate fix wave closes them without moving sixteen checked input readouts or captures.

- 2026-09-14 (G0, §5.144): the region reversal reproduces, and locality improves clean
  light-active thin isotonic RMS from 0.087204959 (source) to 0.011413806 (silhouette), but
  its runner-up gap is only 0.002036644, below the 0.004 bar. Light-inactive thin body and
  Gaussian 1/32 tie at 0.002758498; dark-inactive thin source already reads 0.000284997.
  Isotonic ordering does not identify one family/scale across schemes or poses. The declared
  full population's tint/composite/accessibility confounds do not explain away this failure:
  clean and cohort-separated sensitivities also fail to establish a common selection.
  Of 123 same-region-mean diagnostic pairs, none changes body-contrast SD by more than 0.05;
  a contrast law cannot be inferred from the remaining pitch differences. The sitting's uniform
  patches can locate the response step, not the locality scale; its spatial discriminator needs
  non-D phase evidence rather than borrowing the original D square as a selection baseline.

## Outcomes & Retrospective

**Verified at recomposition (2026-09-15) against the Parent-Level Acceptance, on `main` at
`bf3ebe44` plus the `w28-g4-landing` branch, the prepared package entries and the live demo.**

1. **The abscissa is decided by reading, not by fitting, and never on the checking set — MET.**
   G0 (§5.144) committed its 398-cell selection population at `8ad63af` before it read a pixel, and
   the population excludes group D and `checkerboard__rrect-ml__inactive` on **both** poses, with
   the script refusing a D id by name. Five predictor families were computed from the committed
   background rasters and `componentRegion` on seven-rung ladders, and the statistic is the one the
   clause specifies: the RMS residual after isotonic regression, per scheme, pose and thickness row,
   with no response curve anywhere in the comparison. The verdict is the honest one and it is
   against the wave's own hopes: **not identifiable from this bed.** Locality lowers the clean
   light-active thin residual from 0.087204959 (source) to 0.011413806 (silhouette), but the
   runner-up gap is 0.002036644 against the declared 0.004 Y bar; the light-inactive thin row ties
   silhouette with Gaussian 1/32 at 0.002758498; the dark-inactive thin row, six cells, prefers the
   source outright. G0 also classified what it could not test: of 123 same-region-mean diagnostic
   pairs none changes body-contrast SD by more than 0.05 (the largest is 0.000024540389), so W9's
   H4 is **untestable on this bed rather than absent**, and the clause's "a residual that grows with
   contrast gets its own gate" never became answerable. Nothing was captured, no D fixture was
   opened and no constant moved at that gate.
2. **The abscissa lands profile-gated, reproduces its predictor before anything is fitted, and the
   active material is byte-identical — MET as amended by Decision Log 2 (b).** The amendment is
   material and is named here rather than buried: the clause as written asked for an **output**
   check — the branch's rendered body Y reproducing G0's prediction — and G0 selected no curve, so
   an output check would have smuggled one in. The ruling moved it to the **input**: the branch's
   per-surface abscissa, exposed as a readout, equals G0's own `per-cell.json` silhouette encoded
   mean within one 8-bit code, on both tiers. It passes **335 / 335** unpressed canonical cells per
   tier, worst GPU discrepancy 0.02723997831346303 of a code. `backdropToneAbscissa` is the gate:
   absent or `"source"` is today's arithmetic bit for bit, the two receded documents are the only
   ones that opt in, and the local reference replaces the source mean everywhere the solve uses it —
   the response, the collapse compensation, the nominal composition and the opacity solve — not only
   in `tone_response`. X11 holds at this head: every active document resolves to the same
   `resolvedMaterialSha256`, the renderer's **34 goldens pass unregenerated**, the isolation spec's
   hashes are untouched, and the canonical matrix's 637 active rows are byte-identical cell for cell
   against `bf3ebe44` (§5.148 §2). The CSS tier carries the per-surface half and its Jensen gap to
   the GPU's per-pixel field is **recorded and unmeasured in isolation**, which is the clause's own
   instruction and is now a tracker entry.
3. **The fit never selects on the checking set — MET, and locked three ways.** G1's 28-rung fit ran
   on calibration and non-D probe cells only; the twelve group D ids plus
   `checkerboard__rrect-ml__inactive` were predictions at the read. `score-bound.py` reconstructs
   group D independently and asserts `scored == (scene in D)` on every row, and the verdict records
   **zero D cells spent by the fit**. The three locks X10 names — a committed population before the
   script runs, a fit script that refuses a D id, and the scorer's membership assertion — all fired
   and none was bypassed. The holdout was declared before the fit from cells the fit never saw, and
   Decision Log 2 (f)'s addendum records honestly that the dark half of it **cannot discriminate the
   abscissa**: no dark non-D cell has a silhouette-minus-source displacement above 0.038, where the
   design asked for 0.05. That limit is in the ledger, in X8 and now in the tracker.
4. **The bound holds on all six profiles — MET.** G2 (§5.146) ran the reader G1 sealed exactly once:
   188 planned WebGPU rows, six declared holdout pairs admitted once each with two byte-identical
   deterministic repeats, no resumption and no guard refusal, then 182 CSS rows record-only with
   every holdout excluded. The 2026-09-11 `bound.json` was applied unchanged, clause by clause, by
   the same scorer lineage, and **clauses 1–3 hold jointly on every profile**, 72 / 72 checking
   cells under their per-cell caps. Clause 2: dark 1x 0.01584 / 0.034, dark 2x 0.01114 / 0.041,
   light 1x 0.01277 / 0.032, light 2x 0.01111 / 0.034, Increase Contrast 0.00278 / 0.0078, Reduce
   Transparency 0.00600 / 0.011. The cell that held W27c, light `hc-text__rrect-sm__inactive`, is
   the closest at **0.05932 / 0.064** (1x) and **0.05455 / 0.068** (2x), from 0.07793 and 0.07310 at
   G1d. The verdict history of that unchanged bound is 2 / 6 → 3 / 6 → 4 / 6 → **6 / 6**. Decision
   Log 2 (c) made this read the referee — a candidate the reading could not select, tested on a
   checking set the fit never saw — and the wave did not tighten it after seeing it hold. The
   independent medium review reproduced the verdict and every derived table by independent
   arithmetic and reconstructed all six sheets pixel-for-pixel in memory.
5. **No inactive floor is adopted, and the rows are published as scene `state` — MET.** G4 (§5.148)
   published **470 inactive rows** in the canonical matrix, on both tiers across all six profiles,
   from the 58 inactive ids the declaration puts in `calibration`, `validation` or `probe`; the
   matrix went 637 → **1,107** cells with **0 existing cells changed or missing**, read twice, once
   by the merge that refuses to write otherwise and once from outside it. `state` is an additive
   label copied off `scenes.json` beside `fixtureSet`, never a key segment (X3). **No floor was
   adopted for any regime** — `adopted-thresholds.test.ts`'s gated bed drops the inactive pose
   alongside the probe set, by the declared pose and never by naming cells, with six guards in both
   directions — and `PREDICATE_EXCLUDES` is **byte-identical to `bf3ebe44`**, 43 entries, still
   machine-checked against the predicate's own output over the gated bed. The clause's factual
   premise needed re-declaring and is, in §5.148 §2: of the 72 inactive scenes only 35 are `probe`,
   17 being `calibration`, 6 `validation`, 10 `holdout` and 4 `recorded`. Holdout and `recorded` are
   deliberately unread and neither absence changes a declared split.
6. **The runtime is W27c G2 as chartered — MET.** G3 (§5.147) built the activation observer
   following `document.hasFocus()` through the batched read with an explicit override that wins, the
   framework-agnostic `windowActivation` option and both forms of `setWindowActivation`, the resolved
   `root.windowActivation` getter, the React `<GlassRoot>` prop and `useGlassWindowActivation()`, the
   pose applied through `applyMaterialProfile` as two frozen endpoints (X7), the transit through the
   existing transitions, tests on three engines, README paragraphs on both packages, and the demo
   receding when its window is backgrounded. Nothing was re-designed and nothing was dropped. Two
   things are worth carrying out of that gate rather than leaving in it. The three-engine tests drive
   a **synthetic** `hasFocus` feed and say so, because no engine reports a real unfocused document to
   a driver — G4 found the mechanism, and it is Playwright's focus emulation rather than the engines.
   And the transit's 240 ms / 120 ms are **inherited implementation choices**, measured against no
   native sequence; both now have tracker entries of their own.
7. **By eye, and the ledger — PARTLY, with two exceptions and both are named.** The measurement half
   is met: six sheets at both scales for every profile at G2's read, indexed with full prose in
   §5.146, and the demo's backgrounded pose beside the harness capture at the landing — three sheets
   and `eye.md` in §5.148 §4, at 2× in both schemes, which needed the playground's new `colorScheme`
   pin because the recede's endpoints are fitted per scheme and the page could only draw one of
   them. Every gap that remains is a named line: §5.146 §7, §5.147 §7, §5.148 §5, and the tracker,
   which gains **nine** entries at this landing and three dated amendments beside existing ones.

   The first exception is the one the clause turns on. **The user's eye has not been given and the
   veto has not been exercised.** Decision Log 3 (d) requested it on G2's six sheets and made it the
   veto before G4's cut; the cut is therefore prepared and **unpublished**, which is the only state
   this clause can honestly be in until the user looks. The second is smaller and is a
   re-declaration: the clause says "the cut after the landing is one `@vitreajs/vitrea-web` minor",
   and it is **three minors in the fixed group**. The React minor is implied by acceptance 6, which
   required the `<GlassRoot>` prop; the core minor is the one nobody predicted, and §5.147 §2's
   sentence that "core contracts did not move" is corrected in §5.148 §6 — G1's `GlassGroupState`
   gained an optional `backdropToneAbscissae` and core exports `SurfaceBackdropToneAbscissa`, which
   X2 makes a semver event.

### The eye's residuals, carried forward unchanged

Holding a bound is not pixel identity, and this wave says so in the same breath as the verdict. The
light `hc-text__rrect-sm__inactive` control clears clause 3 by 7 % at 1x and 20 % at 2x and is
**still visibly too bright** against the native pale-grey control, at WebGPU/native body Y
0.6791 / 0.5485 and 0.6907 / 0.5690. The low-contrast checker capsule is both dark profiles'
clause-3 worst cell and reads lighter than native while transmitting a **stronger** checker
amplitude — a level error and a structure error pointing opposite ways in one cell. Large text and
checker panes agree in overall level and differ in structured transfer and in the rim/lens band,
which G4's harness sheet shows again on a cell outside the checking set. `dark-solid__rrect-80`
keeps a cool, dark body on both light profiles. Under Increase Contrast the near-complete one-pixel
contour is the dominant residual and the large light-solid pane is visibly whiter than native.
Reduce Transparency keeps a backdrop-dependent slope rather than one common level error. None of
these is closed and each now has, or already had, a tracker entry.

### What was not measured

- **Native focus delivery.** No engine reports a real unfocused document to a test driver, on any of
  the three, so every automated activation test in the repository is a synthetic `hasFocus` feed.
  The one non-synthetic reading is G4's, taken by launching Chromium directly and speaking CDP over
  a bare socket, on one machine and one engine — real, and not in any suite.
- **Native transition timing.** No frame sequence of Apple's recede exists, so the transit's
  duration, curve and per-channel ordering are authored. Every sheet in this wave is a settled
  endpoint.
- **The identifying sitting.** Not taken. The abscissa's kind and scale — silhouette mean against
  its 1/32 and 1/16 dilations, and whether it is the same on both poses — remain unidentified;
  Decision Log 3 (e) moved the experiment to §Deferred priced at about twelve cells and four to six
  hours of a 26.5 machine.
- **The CSS/GPU Jensen gap, in isolation.** Unmeasured. What exists is an equal-cell mean absolute
  body-Y gap — 0.0014–0.0095 over §5.146's 182 common cells, 0.00077–0.0048 over §5.148's 235
  published inactive dom rows — which sums the Jensen term together with every other cross-tier
  difference the two layers already had.
- **The active pose's footprint abscissa.** Read by G0 and acted on by nothing: X11 held the active
  material byte-identical, so the mechanism exists and the active pose has not been refitted under
  it. The tracker's W22 G3 entry is amended to say exactly that.
- **Element overlap**, Apple's other named system-managed adaptation input in the same sentence as
  focus state, and with it the per-element recede that would let the public site's reference pair
  offer its inactive scenes.

### Status

**0.18.0 PREPARED, UNPUBLISHED.**

### The c9d chain at the 0.18.0 head

Run serially on `w28-g4-landing`, one browser at a time, every browser invocation preceded by a
fresh reading of Reduce Transparency and Increase Contrast off the machine — **0 / 0 before every
one**, logged in `results/2026-09-15-w28-g4-landing/browser-runs.txt`, with a nonzero reading
refusing the run. Each step's whole output is kept beside it as `chain-<step>.txt`.

| step | command | result |
| --- | --- | --- |
| workspace build | `pnpm -r build` | exit 0 |
| workspace lint | `pnpm -r lint` | exit 0 |
| root ESLint | `npx eslint .` | exit 0 |
| workspace units | `pnpm -r test` | **2,382 passed / 162 files**, 0 failed — policy 23, motion 164, geometry 170, renderer 497, core 302, platform 616, React 156, calibration **420**, demo 34 |
| renderer goldens | `pnpm --filter @vitrea/renderer-webgpu test:golden` | **34 / 34**, no regeneration, isolation spec untouched |
| renderer GPU | `pnpm --filter @vitrea/renderer-webgpu test:gpu` | **28 / 28** on a real adapter |
| platform-web Playwright, all projects | `npx playwright test` | **404 / 404** — 153 Chromium, 121 Firefox, 121 WebKit, 9 hardware Chromium GPU |
| React Playwright, three engines | `pnpm --filter @vitreajs/vitrea-react test:e2e` | **174 passed / 3 intentional skips / 0 failed** — 59 Chromium, 58 Firefox, 57 WebKit |
| demo Playwright | `pnpm --filter demo test:e2e` | **57 / 57** — 49 Chromium, 8 hardware Chromium GPU |

**The React suite is green this time, and the tracker entry stays open.** W28 G3's single full
three-engine run reproduced the known Firefox `presence.spec.ts` timing case at 433.6 ms against
354.2 ms allowed, and recorded it rather than re-running to green. This chain's run of the same
suite passes it. Neither reading retires the other: the entry is a **flake** class, and one green
run is exactly what a flake looks like from the other side. Nothing was rerun to produce this
result — it is the first and only React run at this head — and the tracker entry keeps both
readings.


The publish rehearsal, short of publishing: `pnpm publish --dry-run` on each of the three published
packages at 0.18.0. All three are clean at 0.18.0, and the two things npm would get wrong on its own are read off the packed tarball rather than assumed: every `workspace:` range is rewritten — web → core `^0.18.0`, react → core and web `^0.18.0` — and each tarball carries `dist/`, `LICENSE`, `NOTICE` and `README.md`. Packed sizes 545,528 / 540,670 / 178,893 bytes for core, web and react; React's `>=19.0.0` peers survive the pack. This is the reason `pnpm release` is the only sanctioned path (Decision Log #30(a)), re-confirmed here.

**Nothing is published and nothing is tagged.** `pnpm release` is the only sanctioned path and it is
the user's hand; the tag `v0.18.0` follows the publish, not this branch.

### Tracking Map at close

| child | status | claims | evidence |
| --- | --- | --- | --- |
| G0 | CLOSED 2026-09-14 — not identifiable; merged `679cee90` | §5.144 | `results/2026-09-14-w28-g0-abscissa/` |
| G1 | CLOSED 2026-09-14 — input check passed, rows fitted, endpoint sealed | §5.145 | `results/2026-09-14-w28-g1-silhouette/` |
| G1s | NOT TAKEN — Decision Log 2 declined it, Decision Log 3 (e) moved it to §Deferred | — | — |
| G2 | CLOSED 2026-09-14 — the unchanged bound holds on six of six; merged `237465fa` | §5.146 | `results/2026-09-14-w28-g2-read/` |
| G3 | CLOSED 2026-09-15 — root pose and bindings shipped; three engines; review clean | §5.147 | `results/2026-09-15-w28-g3-runtime/` |
| G4 | CLOSED 2026-09-15 — seam, 470 matrix rows, no floor, sheets, re-score, 0.18.0 prepared | §5.148 | `results/2026-09-15-w28-g4-landing/` |

### Deferred at close

Carried unchanged from §Deferred, with the sitting as Decision Log 3 (e) left it:

- **The identifying sitting** — the experiment G0 designed: two fresh phase placements of the text
  square, a contrast pair matched in encoded region mean, and two bright uniform patches near
  encoded 0.80 and 0.88 for the dark step. About twelve cells at 1x, four to six hours at the probe
  bar, and it needs a 26.5 machine. **Priced, not chartered.** The machine stays on macOS 26.5.2
  until it is ruled on, and the OS 27 decision returns with it.
- The active material's chroma transfer over saturated backdrops (§5.139 §5), which is the worst
  inactive cell on every dark profile in G4's published rows and is not the recede's error.
- The active pose's footprint abscissa, recorded by G0, acted on by a later wave.
- Dark accessibility, 2x accessibility, the `clear` variant and the stack regime as inactive
  evidence classes — unchanged from W27 §Deferred, and G4 publishing 470 rows moved none of them,
  because publishing a row that exists is not creating a cell that does not.
- Any inactive floor: none is adoptable while seven runs is the probe bar, so the six profiles that
  hold the bound hold it as fidelity rather than as a gate.
- The `strongBorderRim` one-pixel contour under Increase Contrast and Reduce Transparency's
  backdrop-dependent slope (§5.143 §8).
- The motion-metrics harness — now with the activation transit as a second customer beside identity
  and `materialize`.
- The OS 27 recapture, under new `apple-macos-27.0-…` keys beside and never over the frozen 26.5
  ones; and `prominent`.

### Retrospective

The wave's shape was set by a reading that failed. G0 was built to identify where the reference
takes the response's input, and it could not: three candidates stayed noise-compatible on every
clean row and the bed carried no contrast axis to test the structure term with. The tempting move
was to fit the residual anyway. What happened instead is the thing worth keeping — Decision Log 2
built the **simplest survivor** and handed the verdict to a bound that had been declared before the
bed existed and had already failed four times. That made G2 a genuine prediction rather than a
confirmation, and it held on six of six. The discipline that made it a test was negative: the fit
never saw a checking cell, the mechanism check was moved to the input because an output check would
have imported a curve nobody had read, and the bound was not tightened after it held.

The second thing the wave learned is about instruments rather than material. Three times now, a
question about focus has been answered by the driver instead of by the engine: `bringToFront()` on
three engines, then a real application switch under Playwright, both reporting a focused document
that was not focused. The explanation — Playwright holds every page it owns focused on purpose —
means the repository's entire three-engine activation suite is synthetic by necessity, and the only
true reading in the project was taken by dropping the driver and speaking the protocol directly.
That reading is also the wave's nicest result: a window manager moved the pose, `hasFocus` went
false, the root resolved `inactive`, and `visibilityState` stayed `"visible"` — which is precisely
the case the observer was designed around and had never been able to witness.

What the wave did not do is as legible as what it did. The active material is byte-identical after
four gates about the response's input, because the mechanism is profile-gated and only two documents
opt in; the cost is that the tracker's oldest abscissa entry now reads "built, and off everywhere
the active material draws". No floor was adopted, so six profiles holding a bound is fidelity and
not a gate. And the cell that held W27c for five days now clears its ceiling by 7 % and is still
visibly wrong on the sheet — which is the sentence this project exists to be able to write.

## Revision Notes

- 2026-09-15 (the parent, at recomposition): the wave is CLOSED. §Outcomes & Retrospective verifies
  all seven acceptance clauses against `main` at `bf3ebe44` plus this branch — six MET, clause 7
  PARTLY on the user's eye not yet given and on the cut being three minors rather than one. Status
  line, G4's child block and the Tracking Map updated; the recomposition's Tracking Map, Deferred
  and c9d chain are in §Outcomes. W27's §Deferred entry "W27c G2 and G3 — HELD by Decision Log 20"
  is closed beside its original text, and the tracker's held-runtime entry's three remaining G4
  items are closed with it. The coverage matrix carries a 2026-09-15 re-score beside the
  2026-09-14 one: §3.6's window-focus row moves `partial` → `replicated+measured`, one row, no row
  added, none downward, 44 → 45 measured of 156 scoreable. `2026-08-28-post-v1-wave.md` gains its
  post-close addendum. Nine tracker entries are new and three are amended beside their originals.
  (The commit that landed this recomposition says "six" in its body and lists nine; the count here
  is the file's.)

- 2026-09-15 (G4, §5.148): the landing closed. The calibration seam is the runtime's — the root is
  posed and handed the capture's scheme, and the receded document is applied by
  `applyMaterialProfile` — proved byte-identical before a row was written, 354/354 inactive and
  60/60 active. 470 inactive rows entered the canonical matrix as the scene's declared `state`,
  637 → 1,107 cells with zero existing cells changed, read twice. No inactive floor was adopted and
  the gated bed excludes the pose by axis rather than by cell list; `PREDICATE_EXCLUDES` is
  byte-identical at 43 entries and still machine-checked. Three sheets and `eye.md`, including a
  real window-manager focus change read without a driver. Workspace 2,382 units in 162 files;
  goldens 34/34 unregenerated; renderer GPU 28/28; platform 404/404; React 174 passed / 3 skipped /
  0 failed; demo 57/57; three publish dry runs clean at 0.18.0 with every `workspace:` range
  rewritten. One product change: the playground gains a `colorScheme` pin, default unchanged. No
  material constant, native fixture, profile document, receded document, golden, declared split or
  fitted value moved.

- 2026-09-15 (G3, §5.147): runtime closed — auto activation, both explicit pins, live setter,
  resolved root state, React prop/hook and playground control. Workspace 2,377 units; goldens
  34/34 unchanged; platform 404/404; activation binding 15/15 after test-only carrier/transit
  corrections. The existing Firefox presence timing failure is retained, not rerun to green;
  a headed-only demo assertion is reordered and verified. One medium review is clean. The
  16/16 capture identity proof and G4's runtime-pose plus scheme handoff are recorded; no
  material, native fixture, matrix, floor, coverage score, eye verdict or release changes.

- 2026-09-15 (the parent): G2 merged (`237465fa`); Decision Log 3 recorded — the hold lifts, G3
  dispatched under §5.147, the user's eye requested on the G2 sheets before G4's cut, the sitting
  moved to Deferred as the identifying experiment. Status line, G3 status and Tracking Map updated.
- 2026-09-15 (G2 review closure, §5.146 §8): the independent medium pass over
  `5a517d68..338de679` returns correct with no material findings. Independent arithmetic reproduces
  the verdict and derived tables; in-memory reconstruction matches all six sheets pixel-for-pixel.
  No fix wave, further read, constant, matrix, sheet or verdict change is needed.

- 2026-09-14 (G2, §5.146): the sealed endpoint reads all 188 planned WebGPU rows, including
  six holdouts admitted once with two deterministic repeats each, then 182 CSS record-only rows
  excluding every holdout. All 72 checking cells hold the unchanged bound; six of six profiles
  hold clauses 1–3 jointly. The light hc-text square remains visibly too light despite body ΔE
  0.05931843667932792 / 0.05455396371236936, below 0.064 / 0.068 at 1x/2x. Six sheets and
  `eye.json`, indexed with full prose in §5.146, retain the structure, level and contour gaps.
  The fresh worktree's initial missing-built-package error preceded reader evaluation; after
  workspace build the unchanged reader completed with no guard refusal or resumption. Every
  launch records machine 0 / 0; no source, constant, native fixture, canonical matrix or floor
  moves. G3 remains the parent's dispatch decision.

- 2026-09-14 (G1, §5.145): closed the two-tier silhouette mechanism, 335/335 unpressed canonical
  inputs per tier, 39 W9 aliases and 24 interaction records. The 28-rung non-D fit selects light
  anchors [0.1104, 0.2706, 0.45, 0.9505] and dark [0.1104, 0.2706, 0.8, 0.9505], with dark
  middle ordinates 0.04092 / 0.0331 retained. GPU fit means are 0.016032500055353678 light and
  0.02253858803940114 dark; worst controls 1.6431724374048398× / 2.118232521653608×, below 9×.
  The exported endpoint is sealed at `6d7465c9`, patch digest `3fbdcb6d…`; all six holdouts remain
  unread. G2's actual dry run exercises 47 refusals with zero pages or PNGs opened. Independent
  review converged after separate fix waves. Workspace build/lint and 2,363 tests pass, with
  34 unchanged goldens, 28 GPU tests and 392 platform browser tests. Source/fixture/profile/matrix
  protections hold; the minor changeset records endpoints still inert pending activation runtime.
  The dark impulse
  low-input residual, photo chroma, pressed geometry, source CSS sizing and non-canonical locality
  limits are recorded rather than claimed closed. G2 is the next gate; no checking verdict here.

- 2026-09-14 (parent rulings recorded by G1, §5.145): the input pass condition is one code on
  every unpressed canonical cell; the 24 interaction cells retain their actual-geometry and
  abscissa deltas as records because G0 used unpressed masks. The parent also explicitly admits
  the two light `impulse__rrect-md__inactive` validation rows already present in G1's committed
  partition as non-D supplying cells. A former configuration's validation role does not bar
  later supply when it remains recorded and is not called a holdout. No partition is rewritten,
  and D plus the six W28 holdouts remain excluded from fitting. The exact dark photo-capsule
  displacement is 0.03734347805587751 at 1x and 0.03800814795956453 at 2x; the Decision Log's
  rounded 0.037 describes the 1x reading, not a literal all-scale bound.

- 2026-09-14 (the parent): G0 merged (`679cee90`); Decision Log 2 recorded on the user's choice;
  G1 dispatched under §5.145 with the mechanism fixed as the per-surface silhouette mean and the
  mechanism check moved to the input. Status line updated.
- 2026-09-14 (G0): committed the 398-cell population at 8ad63af before reading pixels;
  completed five predictor families on seven-rung ladders, isotonic residuals, uniform checks
  and residual/active-input records under §5.144. Verdict: not identifiable from this bed.
  G0 recommends neither G1 mechanism yet and hands the sitting/stop choice to Decision Log 2;
  no Decision Log entry, runtime change, capture, fixture edit or D native read by this child.
  Independent medium review returned no material findings; bounded evidence/documentation debt
  is logged in the tracker. The implementation passes 4 instrument tests and workspace build,
  lint and 2,320 tests in 156 files; review converges without another fit or mechanism choice.

- 2026-09-14 (the parent): chartered; adversarially reviewed, four findings folded into acceptance 1
  and 2, §Design, G0, G1 and X10 (Decision Log 1's amendment); G0 dispatched.
