# W28 — the footprint response: the inactive material's abscissa under the surface, and what structure adds beyond it

**Status: CHARTERED 2026-09-14 (Decision Log 1; the user's choice after 0.17.0 published, W27 spec
§Deferred "W27c G2 and G3 — HELD by Decision Log 20"). G0 dispatched the same day (claims §5.144).
The machine stays on macOS 26.5.2 until Decision Log 2 rules on the sitting.**

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

### G0: The abscissa read — controlled, native-only, nothing spent — READ 2026-09-14: NOT IDENTIFIABLE (§5.144; Decision Log 2 required)

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

### G1: The footprint abscissa on both tiers, and the rows refitted — controlled

- **Purpose:** the mechanism, profile-gated; the receded rows refitted under it on non-D cells;
  declared and dry-run.
- **Acceptance:** acceptance 2 and 3 above, the mechanism check passed on the selection
  population before the first row is refitted (its table in the evidence directory); unit pins
  that GPU and CSS read the same abscissa kind from the same document; `tier-coherence.test.ts` and the dom
  floors unchanged at rest; the holdout declared unread; the fitted endpoint's SHA-256s and patch
  digest frozen in `fitted-endpoint.json`; a dry run of the whole G2 read (`DRY`-style: every
  refusal exercised, no page opened for a holdout cell). If G0 recommends the sitting, G1 waits on
  Decision Log 2 for the fit's holdout and proceeds with the mechanism meanwhile.
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

### G2: The read — controlled; one sealed configuration, one holdout, the bound once

- **Purpose:** acceptance 4, applied exactly as §5.143 §5–6 did: freeze, read the holdout once,
  score the unchanged bound with the same scorer lineage, six sheets by eye, CSS coherence
  recorded, no floor adopted.
- **Acceptance:** the verdict table for six profiles; holdout cells captured exactly once; machine
  0 / 0 on every browser run; `eye.md`; the ledger section. **Stop rule:** any profile failing any
  clause ends the wave at this gate with the failure named; G3 is not dispatched.
- **Edges:** blocked-by G1 (and G1s if taken); blocks G3.
- **Contracts:** X1, X7, X8.
- **Size:** 6–10 agent-hours.

### G3: The runtime — W27c G2 as chartered — controlled

- **Purpose and acceptance:** acceptance 6, verbatim from the W27 spec's W27c G2 and the tracker's
  handoff entry. Framework-agnostic first, React over it; three engines; changeset (a
  `@vitreajs/vitrea-web` minor and a `@vitreajs/vitrea-react` minor in the fixed group).
- **Edges:** blocked-by G2 holding on six; blocks G4.
- **Contracts:** X2, X7.
- **Size:** 12–20 agent-hours.

### G4: The landing — W27c G3 as chartered — controlled; the cut after the user's eye

- **Purpose and acceptance:** acceptance 5 and 7: inactive rows in the canonical matrix as scene
  `state`, `PREDICATE_EXCLUDES` equal to the machine's output, no floor adopted for any probe-bar
  regime, the demo's backgrounded pose with the harness capture beside it, README and playground,
  the matrix re-scored (§3.6 window focus state to `replicated+measured`), the eye sheets, the
  recomposition against this document's seven clauses, one minor cut prepared.
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

The active material's chroma transfer over saturated backdrops (§5.139 §5; the tracker); the
active pose's footprint abscissa (recorded by G0, acted on by a later wave); dark accessibility, 2x
accessibility, the `clear` variant and the stack regime as inactive evidence classes (W27 §Deferred,
unchanged); any inactive floor (needs the seventeen-run bar); the `strongBorderRim` one-pixel
contour under Increase Contrast and Reduce Transparency's backdrop-dependent slope (§5.143 §8,
named, not this wave's); the motion-metrics harness; the OS 27 recapture; `prominent`.

## Tracking Map

| child | status | claims | evidence |
| --- | --- | --- | --- |
| G0 | READ 2026-09-14 — not identifiable; waits on Decision Log 2 | §5.144 | `results/2026-09-14-w28-g0-abscissa/` |
| G1 | — | assigned at dispatch | — |
| G1s | — (Decision Log 2) | assigned at dispatch | — |
| G2 | — | assigned at dispatch | — |
| G3 | — | assigned at dispatch | — |
| G4 | — | assigned at dispatch | — |

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

## Surprises & Discoveries

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

## Revision Notes

- 2026-09-14 (G0): committed the 398-cell population at 8ad63af before reading pixels;
  completed five predictor families on seven-rung ladders, isotonic residuals, uniform checks
  and residual/active-input records under §5.144. Verdict: not identifiable from this bed.
  G0 recommends neither G1 mechanism yet and hands the sitting/stop choice to Decision Log 2;
  no Decision Log entry, runtime change, capture, fixture edit or D native read by this child.

- 2026-09-14 (the parent): chartered; adversarially reviewed, four findings folded into acceptance 1
  and 2, §Design, G0, G1 and X10 (Decision Log 1's amendment); G0 dispatched.
