# W45 — the span-graded tap: the second heavy tap's share graded on the scatter's far curve, the deep share's span top, the thin trade read, and a landing rule that measures regression as growth (2026-10-03)

**Status: DRAFT v1.1 (2026-10-03): the adversarial review of v1 folded (three P1, three P2, all
accepted by the parent; Revision Notes). v1's mechanism was wrong: the thick lift saturates at
span 96 and the second tap's share is span-flat, so no existing leaf can hold span 96 apart from
128–160 at one pitch. That is W28's precommit condition, and this draft charters the smallest
operator the named structure needs, landed inert first.** Chartered from W44's close at the
finding (claims §5.203 §8; W44 charter Decision Log 4 "Otherwise", RULED by the parent
2026-10-03): the fit's joint point cut the fine stratum's error by 62 % and brought the receded
fine checkers within Apple's, and failed the landing rule on ten cells, with no point in the
declared space clearing them. Main is at `ad93ff9b` (W44 G1 merged); W44 G2 landed T1 in the owner
test with its 169 misses named (§5.204, merged as `3115bf17`). The holdout and the twelve referees are unspent for the 0.25 light
documents. **Under the user's 2026-10-03 mandate (W44 Decision Log 0) the parent rules this
charter's Decision Logs and reports them.** Ledger §5.205–§5.207 are reserved.

## Decisions

The full entries are Decision Logs 1–6 at the tail.

| DL | question | status | what holds |
| --- | --- | --- | --- |
| 1 | the operator | **RULED** by the parent, 2026-10-03 | one new leaf, `sizeHeavySecondShareFar2x`: the second tap's share graded on the scatter's far curve (`smoothstep(sizeSpanMax, sizeScatterSpanMax2x, span)`), identity 0, 2x-anchored, a plain value drop in the identity table; landed inert in G0 with every shipped digest and golden byte-identical; the CSS tier declines it as it declines the tap |
| 2 | the scope | **RULED** by the parent, 2026-10-03 | the 2x light `-glass0.25` material through W44's five leaves, `sizeScatterSpanMax2x` and the operator; `sizeScatterHeavyShareThick2x` struck (not in the document's leaf set, and saturated at 96); X48 holds; T1, the bar, the manifest and the planner reused by path; X44 narrowed for the operator's key in the active and receded light documents |
| 3 | the landing rule | **RULED** by the parent, 2026-10-03 | change as a partition by error growth alone; per stratum × pose, a declared band and aggregate with a tolerance on its own scale, gated at three cells or more; at most three cells `away` with `g > B`, none with `g > 3B`, an explicit tradeoff; rehearsed on the three complete W44 maps, c05, the pre-fit and declared synthetic cases before part 1 is hashed |
| 4 | the moves | **RULED** by the parent, 2026-10-03 | one space, two stages, two declared starting points (c05 and W44's joint point); predictions per lever from the actual law |
| 5 | the thin-span pitch trade | **RULED** by the parent, 2026-10-03 | read in G0 (a thin-span transfer ladder per lever), not pre-attributed; if no lever separates `checkerboard-4` from the pitch-16 and 32 thin cells, it is a named residual |
| 6 | the release | **RULED** by the parent, 2026-10-03 | as W44 Decision Log 6: a `@vitreajs/vitrea-web` minor (0.27.0), the light 0.25 generation superseded, the dark one unchanged, the user's `pnpm release`; the operator ships inert in every other document |

## Purpose

**What the wave is for.** The least possible gap to Apple's material at the clearer glass, at
Retina scale. W44 built the referee (T1) and found on 103 renders that the material's existing
leaves can close most of the 2x light texture gap: at the joint point the fine stratum's aggregate
fell 0.6462 → 0.2455, the receded fine checkers went from ×3.9–5.3 over Apple to within, the
coarse receded cells from ×2.5–3.4 to ×1.2–1.5, and the thin rest cells from ×0.5–0.9 under to
×0.8–1.2. What no existing leaf can do is this: Apple passes a 16-device-px checker at span 96
heavily (`checkerboard-8__rrect-md__rest` reads 0.099, a fifth of the backdrop) and barely at
128–160 (0.022 at `rrect-lg`), a ×4.5 drop across one span step, where vitrea is span-flat
(0.040 and 0.033 at the joint). Under W42's reading of Apple's declared tree (LT), the narrow
term's width scales with the declared opacity, and the opacity with the span: the material's
middle-width term is span-graded. vitrea's second tap has one width and one share per source,
and the only span grading the deep body has is `kDeep`, which grades the SHARP component against
the deep one and so passes every pitch at once. The joint point's one large regression
(`checkerboard-8` md, ×0.85 → ×0.40) and its thick overshoot (`checkerboard-32__rrect-lg__rest`,
×0.99 → ×1.25) are the two ends of that one missing grading.

**The best version of this is three things:**
1. **The smallest operator the structure needs, landed inert first.** The second tap's share
   becomes a function of span along the curve the ramp's far start already rides:
   `tapShare(span) = clamp(share + farDelta·smoothstep(sizeSpanMax, sizeScatterSpanMax2x, span), 0, 1)`,
   one leaf (`sizeHeavySecondShareFar2x`, identity 0, 2x-anchored), no new span statistic, no
   new texture and no per-fragment tap (the share is already a uniform the optics pass mixes;
   the grading is evaluated where the ramp's start is). At identity nothing moves: the shipped
   digests, the goldens and every document that does not name it are byte-identical, which G0
   proves before any ladder.
2. **A landing rule that measures regression as regression.** W44's rule vetoed a cell that
   crossed Apple with a smaller error and any single cell beyond the bound, so a candidate better
   by every aggregate landed nothing. W45's rule reads error growth only, bounds it per cell with
   a count and a ceiling stated as the tradeoff they are, bounds every stratum × pose aggregate on
   a declared band with a tolerance on its own scale, and is rehearsed on the complete W44 maps
   and on synthetic boundary cases before it is hashed.
3. **The same referees, read once.** T1 as adopted; the twelve referees and the canonical holdout
   unspent since W44, read once at the frozen bytes after the gate; publication through W40's
   publisher superseding the light 0.25 generation.

**What the wave does not do.** No native capture. No 1x or dark change (X48). No change to T1,
its bar, its manifest or its planner. No second operator: the thin span's pitch trade is read, and
if no lever separates it, named (Decision Log 5). No re-read of anything W44 read.

## Parent-Level Acceptance

1. **The operator lands inert before anything else (G0).** *Metric:* the leaf in
   `MaterialProfile` and `DEFAULT_MATERIAL_PROFILE` at 0; an append-only identity-table entry
   (a plain value drop); the grading evaluated where the ramp's far decline is; the CSS tier's
   decline recorded in `optics.ts` and pinned by `tier-coherence.test.ts`; the W31 identity and
   gate-group tests extended. *Bar:* every shipped document's `resolvedMaterialSha256` unchanged
   (the six pre-W43, the four 0.25, the two 26.5); the 34 goldens byte-identical; the 1x rows
   byte-identical under any value of the leaf (`rampAtScale` holds a 2x anchor at its 1x twin
   below dpr 1, and the 1x twin does not exist, so the leaf is read at dpr 2 only — G0 proves it
   by render, not by argument); the isolation spec's hashes unmoved. *Stop:* a digest or golden
   that moves stops the merge; the operator is not fitted on.
2. **Declared before fitted, in W44's two parts, with W45's own tools (G0).** *Metric:* W45-owned
   copies of `declare.py`, the cuts, the fit driver, the stage, X48 and the seal tools,
   parameterised by wave (charter pin, evidence root, part hashes) and refusing W44's hash,
   directory or stage before any render; the manifest, the planner's two lists, the bar and
   `t1.py`'s arithmetic shared by path and pinned byte-identical to W44's. Part 1 (T1 as
   adopted, the bar, the manifest, the landing rule with its rehearsal record, the ladders'
   protocol and permitted decisions, the two starting points by declaration hash, the regression
   references) and the part-2 draft hashed before any ladder render; part 2 after the ladders as
   a validated diff; `amend` and `amend-fit` once each under W44's rules. *Stop:* as W44 clause 1.
3. **The landing rule is rehearsed on complete maps and on declared boundary cases (G0).**
   *Metric:* the rule's outputs on W44's three complete 94-cell maps (`m1c-0.5-5`, `m2-t0.8`,
   `m3-t0.1`), on c05 and on the pre-fit render; UNMEASURED preserved on W44's 97 partial
   candidates (per-cell diagnostics only, never a landing verdict); and on synthetic cases pinned
   as tests before part 1 (a map halving F with three cells at 2B passes; four cells at 2B fails;
   one cell at 3.1B fails; a stratum aggregate worse by more than its tolerance fails; every cell
   `unchanged` is neither; a T stratum of two cells is reported, not gated). *Bar:* every verdict
   committed; the joint point's verdict recorded whatever it is; the count and ceiling not moved
   after the rehearsal. *Stop:* a synthetic case that the implementation decides against its
   declared text stops the hash.
4. **The levers separate what they are for, on the renders (G0).** *Metric:* ladders in candidate
   mode, after part 1: the operator's `farDelta` at a fixed share and width on the three vetoing
   mid/thick cells, the two `checkerboard-8` thick cells and `checkerboard-32__rrect-lg__rest`;
   `sizeScatterSpanMax2x` at a floor below 1 on the same cells; a thin-span transfer ladder per
   lever (floor, span top, thin start, share, width) on `checkerboard-4`, the pitch-16, 32 and
   text thin cells (Decision Log 5); byte identity at 1x on every rung (X48). *Bar:* the operator
   moves `checkerboard-8` md and lg in OPPOSITE directions of T1 on at least one rung (the
   separation it exists for); a leaf flat on its cells is struck. *Stop:* an operator that cannot
   separate 96 from 160 on the renders closes the wave at G0 with the finding, and the operator
   stays landed inert.
5. **Measured before moved (G1).** As W44 clause 5, with the candidate identity patch-and-digest,
   and every fit render passing `--alpha` so a fit row equals a stage row (W44 G1's tracker note).
6. **The gate, before the exposure, on the shipped bytes (G1).** As W44 clause 6: the runtime
   regenerated and its export test green before the stage; the stage filled with every declared
   set less the referees; the owner test's adapters on the stage union against a new cut; T1 as
   adopted; every other row re-baselined on the published c05 render; `tier-coherence`; X48 at
   1x; the sheets to the MacBook; a GATE REPORT to the parent.
7. **The exposure, once (G1).** As W44 clause 7: the canonical holdout and the twelve referees in
   one read per tier, recorded as read 7 with the manifest's hash.
8. **Nothing frozen moves (G0–G2).** As W44 clause 8, plus W44's committed evidence and hashes,
   and clause 1's digests and goldens at every merge.
9. **The landing (G2).** As W44 clause 9: the publication superseding `6d18c059eb42`, the tree
   copy and the superseded move, T1's owner-test block re-baselined on the new generation with
   every miss named, the generated module re-pinned, the demo refreshed, CLAUDE.md (the operator's
   paragraph beside W30's spanning set), the READMEs, the changeset, the c9d chain.
10. **By eye, and the ledger (every child).** As W44 clause 10.

## Grounding Baseline (main at `ad93ff9b`)

**W44's joint point** (`results/2026-10-03-w44-g1-refit/fit/candidates/m3-t0.1/`, declaration
`66bf5a01…`): active light `sizeScatterFloor2x` 1, `sizeHeavySecondShare` 0.5,
`sizeHeavySecondSigma2x` 5 CSS px, `sizeScatterRampStartThin2x` 0.8; receded light
`sizeScatterRampStartThin2x` 0.1 (the receded share equal to the active, by the fit); dark
unchanged. Its T1 outputs over the 94 gate cells are committed (`fit/path/joint.txt`,
`finding.txt`). Read on error growth alone, SIX cells grow by more than B and four of them by
more than 3B (the review of v1 recomputed every one):

| cell | native | c05 | joint | c05 ratio | joint ratio | growth / B |
| --- | --- | --- | --- | --- | --- | --- |
| `checkerboard-8__rrect-md__rest` | 0.0991 | 0.0841 | 0.0401 | 0.85 | 0.40 | 6.87 |
| `checkerboard-32__rrect-lg__rest` | 0.1336 | 0.1329 | 0.1675 | 0.99 | 1.25 | 4.97 |
| `checkerboard-32__rrect-sm__rest` | 0.2161 | 0.1954 | 0.2681 | 0.90 | 1.24 | 4.64 |
| `checkerboard__capsule-button__pressed` | 0.1938 | 0.1807 | 0.2310 | 0.93 | 1.19 | 3.55 |
| `checkerboard__rrect-md__rest` | 0.1501 | 0.0976 | 0.0814 | 0.65 | 0.54 | 2.44 |
| `checkerboard-64__rrect-sm__rest` | 0.0680 | 0.0319 | 0.0118 | 0.47 | 0.17 | 2.40 |

Four of W44's seven overshoots shrank their error (`checkerboard__rrect-sm__rest` 0.25 → 0.20 in
ratio, `hc-text-28` sm 0.24 → 0.20, `hc-text` sm 0.22 → 0.17, `checkerboard-32` capsule 0.14 →
0.15 at the bar) and are `toward` or `unchanged` on growth. The aggregates (W44's median
|log((k + ε) / (n + ε))| on T1): F 0.6462 → 0.2455; F inactive 1.290 → 0.047; C rest 0.172 →
0.103; C inactive 0.852 → 0.235; P rest 0.419 → 0.393; P inactive 0.139 → 0.172 with every cell
`unchanged`; T on raw T1 0.2153 → 0.2392 while both of T's bands improve; the selection metric
0.3458 → 0.1876. Two of those are why the aggregate clause below names its band and its
tolerance.

**The span structure of the vetoes, in Apple's own numbers.** Native T1 at 2x light, rest:

| backdrop | span 96 (`rrect-md`) | 128 (`rrect-ml`) | 160 (`rrect-lg`) |
| --- | --- | --- | --- |
| `checkerboard-8` (c = 16 device px) | 0.0991 | 0.0261 | 0.0224 |
| `checkerboard` (c = 32) | 0.1501 | 0.0815 | — (holdout) |
| `checkerboard-32` (c = 64) | 0.1817 | 0.1556 | 0.1336 |

Apple's pass at c = 16 drops ×4.4 between 96 and 128; at c = 32 ×1.8; at c = 64 ×1.2. The middle
pitches are what the slider's narrow term carries, and its width grows with the span. vitrea at
the joint reads `checkerboard-8` 0.0401 / 0.0362 / 0.0329 across the same spans: span-flat, under
at 96 and over at 128–160, which no span-flat share can fix.

**Why no existing leaf separates 96 from 128–160** (the review of v1; the actual law). The deep
share is `kDeep(span) = floor + (1 − floor)·smoothstep(32, spanTop, span) + thickLift·sizeThickness(span)`,
clamped at 1, with `sizeThickness` saturated at every span ≥ 96. At floor 0.7 and span top 128 it
reads 0.922 / 1 / 1 at 96 / 128 / 160, so the span top alone leaves a sharp share of 0.078 at 96
and none above — a separation, but of the SHARP component, which passes every pitch (c = 8 at
0.79 for vitrea's 1.25-device-px sharp term, c = 32 at 0.985) and so moves `checkerboard-4` md
(within at the joint) with `checkerboard-8` md. Any thick lift ≥ 0.078 erases even that. And the
shader mixes the second tap into the heavy sample before that sample is mixed with the sharp
body (`deep = heavy + share·(heavy2 − heavy)`), so the tap's weight at a thick span is `share`
whatever `kDeep` does. The quantity that must grade with span is the tap's SHARE (or its width,
which W26 made one per source for cost); the share is a uniform the optics pass already mixes,
and grading it is one multiply by a curve the ramp's start already evaluates.

**The operator, as the material will carry it** (Decision Log 1). `sizeHeavySecondShareFar2x`,
signed, identity 0, read at dpr 2 through `rampAtScale` against an implicit 1x twin of 0 so the
1x rows cannot move:

```
tapShare(span) = clamp(sizeHeavySecondShare
                       + sizeHeavySecondShareFar2x · smoothstep(sizeSpanMax, sizeScatterSpanMax2x, span), 0, 1)
deep           = heavy + tapShare(span) · (heavy2 − heavy)
```

The curve is `scatterRampStart`'s `decline` (`material.ts`), "the same curve the deep value rises
along, so the two are one span statistic read twice" — now three times. At `farDelta` 0 the term
is a multiplied zero, exact in f32: every document that does not name it resolves to 0, rule 2
drops it from the digest as a plain value drop (W31; `MATERIAL_IDENTITY_TABLE` gains an entry
with no gated leaves), and the goldens, which render explicit patches over the default, are
byte-identical. The gate on the second texture stays `sizeHeavySecondShare`: at share 0 no
texture exists and `farDelta` is unread, which the gate-group test proves. The CSS tier declines
the tap (`optics.ts`) and therefore its grading; the decline is recorded beside the tap's. Where
the grading is evaluated (per surface on the CPU into the existing uniform, or per pixel in the
optics pass beside the ramp's `decline`) is G0's to decide by the cost on the mobile bench row
and by the composite scenes (`glass-over-glass`'s 130 and 56 px members in one group), with the
reason recorded; byte identity at identity is the proof either way.

**The leaf set and the documents.** The active 0.25 light document names `sizeScatterSpanMax2x`
(256) and does not name `sizeScatterHeavyShareThick2x` or the new leaf; its 0.5 twin names the
same. X44 ("exactly the twin's leaves") is narrowed by Decision Log 2 for the operator's key in
the active light document, and in the receded light document as a difference, as W44 narrowed it
for the receded share: the candidate builder, the seal and `macos27-profile-export.test.ts`'s
leaf-set pin admit exactly that key, with red cases. The 0.5 generation does not move (X41): its
documents resolve the leaf at 0.

**The CSS tier reads the span top** and the floor and the ramp through `MATERIAL_SOURCE_SIZE`
(the review of v1 corrected the draft: both of v1's leaves reached it), and declines the tap and
the operator; the CSS rows move with the floor and the span top uncompensated and are priced as
a tier residual at the gate.

**The thin span.** vitrea's sharp term draws at 1.25 DEVICE px (0.625 CSS px at 2x), not 1.25
CSS px at both scales as v1 said; its pass at c = 8 is then 0.79 against 0.985 at c = 32, a flatter
curve than v1 assumed, so the thin cells' trade (`checkerboard-4` sm and capsule under at 0.74 /
0.64 while the pitch-16, 32 and text thin cells read 1.15–1.24 over at thin start 0.8) is not
attributed to the sharp width by this charter. G0 reads it (clause 4): the transfer per pitch on
the thin cells under each lever, including the operator's share at thin spans (where the far
curve is 0, so the base share acts) and the span top (which moves the thin spans' deep share as
well). Decision Log 5 names the residual if no lever separates them.

**What W44 left ready** (reused by path, pinned byte-identical): T1 adopted (§5.204, `3115bf17`);
the bar 0.5 code everywhere; `referees.json` and the planner's two whitelists (81 pre-gate probe,
26 exposure); the loader's refusals; `cuts/t1.py` and `readings.py` with the T stratum's two
bands; the candidate builder admitting the receded second-tap keys; 100 committed candidates, of
which three are complete 94-cell maps; the unrun `seal/seal.ts`, `stage/stage.py`, `stage/x48.py`,
`sheets/sheets.py`; the holdout ledger at read 6. **Reused by port, not by path** (the review of
v1): `declare.py` (pins W44's charter and amendment rulings), the fit driver (hard-codes part 2's
hash and W44's domains), the stage and X48 tools (W44's stage directory), the seal (W44's
provenance) — W45 owns parameterised copies that refuse the wrong wave's hash, directory or
stage (clause 2).

## Design (advisory unless marked)

### The landing rule (MARKED; Decision Log 3)

Per cell as W44: `n` native, `c` c05, `k` candidate, `e(x) = |x − n|`, `g = e(k) − e(c)`,
`B = max(1 code, 2·bar)`, `δ = |k − c|`. Fidelity as W44 (`within` by `B` or 10 %).

**Change, a partition by error growth alone:** `unchanged` if `δ ≤ bar`; else `toward` if
`g ≤ 0`; else `away` with `g`. No crossing state.

**The band per stratum, declared:** F, C and P read T1; T reads T1-fine for fidelity, change and
its aggregate, and T1-low for `away` only (W44 Decision Log 7). Raw T1 on a T cell is recorded and
read by no clause.

**The aggregate per stratum × pose:** `A = median over the group of |log((k + ε) / (n + ε))|` on
the group's band, `ε` = 1 code; its tolerance `τ = median over the group of log(1 + bar / (n + ε))`
(dimensionless, on A's own scale, W44's tie form). A group is **gated** when it has at least three
gate cells and **reported** otherwise (T has three rest cells and no inactive member in the gate;
its rest group is gated, its inactive group reported). `ε` is what keeps T's aggregate readable:
its native T1-fine values are tiny (0.0032 at 2x `rrect-lg`), so a raw ratio there is dominated by
the bar and the absolute bound decides fidelity (W44 G2, §5.204); T's `A` is read, and its gate is
the F-and-C-style bound on growth, never a ratio alone.

On the final stage, WebGPU, 2x light, both poses, over F ∪ T ∪ C ∪ P less the referees:
- **Full close:** every F cell within; every gated group's `A` at most c05's `A` + `τ`; at most
  **three** cells `away` with `g > B`, none with `g > 3B`, each named; every other adopted row
  passing or its miss named; the twelve referees within at the exposure. Lands.
- **Improvement landing:** the F aggregate (both poses pooled) at most half of c05's; every gated
  group's `A` at most c05's `A` + `τ`; at most three cells `away` with `g > B`, none with
  `g > 3B`, each named; every referee within or an unchanged miss; every other adopted row
  passing or its miss named. Lands as improved, every F cell not within named.
- **Otherwise** the wave closes at the finding.

*The count and the ceiling are a tradeoff, stated as one.* With the bar at 0.5 code, `B` is one
code and `3B` three codes of linear-light SD at the cell's native level. Three cells is the
budget the parent accepts for a landing that halves the fine stratum's error: a candidate that
regresses more cells than that has traded strata rather than closed one. Three codes is the
largest single regression accepted: above it a cell has changed texture class on T1's own scale,
not drifted. Neither number is a perceptual measurement (no eye sheet exists for the joint
point; §5.203 §9), and both are fixed here, before the rehearsal, so the rehearsal reports and
does not tune. On W44's joint point the rule as written fails on the count (six) and the
ceiling (four), which is the test it should fail: those cells are what the operator is for.

### The moves (MARKED; Decision Log 4)

One space, two stages, two declared starting points (c05 and W44's joint point by declaration
hash), W44's search procedure (coordinate sweeps, at most two passes, a full factorial
permitted), W44's selection metric and tie read on the move's cells, and the final paths
compared on the one gate population (the review of v1):

- **Stage 1, the span-graded deep composition** (rest, mid and thick cells; the within clause =
  the F and pitch-16 cells of the stage): `sizeScatterFloor2x` ∈ [0.5, 1.0];
  `sizeScatterSpanMax2x` ∈ [96, 256] (grid 96, 112, 128, 160, 192, 256); `sizeHeavySecondShare`
  ∈ [0, 1]; `sizeHeavySecondSigma2x` ∈ [1.5, 6] CSS px; `sizeHeavySecondShareFar2x` ∈ [−1, 0]
  (grid 0, −0.25, −0.5, −0.75, −1); the 1x second width 0 (W44's L3). *Prediction, from the
  law:* with the tap at 2–3 CSS px and share 0.5–0.75 at span 96 (c = 16 passes 0.38 at 4
  device px, c = 32 at 0.79), `farDelta` near −share with the span top at 160 takes the tap off
  at 160 and halves it at 128, so `checkerboard-8` md rises toward Apple while ml and lg fall,
  and `checkerboard-32` lg returns to Apple; the floor stays near 1 and the span top's role is
  the far curve's end, not the sharp taper.
- **Stage 2, the thin start and the receded overrides** (as W44's moves 2 and 3, the receded
  document's five leaves plus the operator's key as a difference; the span top inherited).
  *Prediction:* the thin start lands below 0.8 under the growth rule; the receded share lands at
  the active share as in W44, and the receded `farDelta` at the active's.
- **Interactions** as W44. The joint point is re-read at the end; a stage that undid the other is
  refitted once on the union.

### Referees: what carries over, and what is new

- **Unchanged:** T1 (adopted), the bar, the manifest, the planner, the loader's refusals, the
  regression references on c05 by hash (X52), X48, X49, X53, the freeze (1,818), X41 (911), the
  goldens, the dark 0.25 digests, W44's hashes and evidence.
- **New:** the operator's inert landing (clause 1); the error-growth partition and the budgeted,
  banded landing rule (Decision Log 3); the ladders of clause 4; the rehearsal of clause 3.

## Children

### G0: The operator inert, the rule rehearsed, the ladders, the declaration (ledger §5.205)

Branch `w45-g0-operator`, evidence `packages/calibration/results/2026-10-03-w45-g0-operator/`.
- (a) **The operator** (clause 1): the leaf, its doc comment in `material.ts` beside W30's spanning
  set, the identity-table entry, the grading's evaluation site with the cost read on the bench
  row, the CSS decline in `optics.ts` with its reason, the W31 identity and gate-group tests
  extended, the export test's leaf-set pins unchanged (no document names it yet); every shipped
  digest reproduced; 34 goldens byte-identical; the isolation spec's hashes unmoved; a ladder of
  the leaf at share 0 proving it unread.
- (b) **W45's tools**: ports of W44's `declare.py`, cuts, fit driver, stage, X48 and seal,
  parameterised and refusing W44's bindings; the shared inputs pinned byte-identical.
- (c) **The partition and the rule** in the cuts; the synthetic cases as tests.
- (d) **The rehearsal** (clause 3), committed as a table.
- (e) **Part 1 and the part-2 draft hashed**; the ladders (clause 4), including the thin-span
  transfer per lever; part 2 as a validated diff, hashed.
- Acceptance: clauses 1–4; independent review (the operator's code by `doperpowers:reviewer-high`,
  the rest medium); merge; both hashes checked on main.

### G1: The refit, the gate, the exposure and the publication (ledger §5.206)

Branch `w45-g1-refit`, evidence `results/2026-10-03-w45-g1-refit/`. W44's G1 steps 1–8 with
W45's tools: the references; the fit in two stages from both starting points; the freeze (the
active and receded light documents naming the operator's key, the export pin re-recorded with the
reason); the runtime first (X53); the stage less the referees; the gate (clause 6) with a GATE
REPORT to the parent, who rules each miss; the exposure once (clause 7); publication. The worker
stops at the gate report.

### G2: The landing (ledger §5.207)

Branch `w45-g2-landing`. W44's G2 list in full (clause 9), plus the operator's paragraph in
CLAUDE.md beside W30's spanning set and in the READMEs' material table; the changeset names the
operator (inert in every document but the 0.25 light pair) and the moved leaves. **T1's
re-baselining is a three-part task** (W44 G2, §5.204): (i) T1's regression clause (b) is read
against c05 BEFORE its reference moves, and its at-most-three named regressions are recorded in
§5.207 and in the owner test's history; only then is `T1_REFERENCE` pointed at the new generation;
(ii) the T stratum's band fixture is re-read off the new captures to a NEW path with a new pin
(`t-bands.json` refuses to overwrite; a T cell with no entry reads UNMEASURED and fails);
(iii) `MISSED_27_ROWS`' T1 entries are re-derived with `derive.py` at the new generation (the owner
case fails in both directions).

## Cross-Child Contracts

**Carried from W44:** X1, X3, X24, X33, X41, X44 as narrowed (now for the operator's key too),
X45, X48, X49, X50, X51, X52, X53; the worker and review rules; the census; no attribution;
path-scoped adds; merges with the freeze and X41 verified.

**New:**
- **X54 — regression is error growth.** No landing clause reads a crossing; every per-cell veto
  is a growth `g` against `B`, with a count and a ceiling stated before the rehearsal.
- **X55 — the rule meets a trade before the hash.** Rehearsed on the three complete W44 maps,
  c05, the pre-fit and the declared synthetic cases; UNMEASURED preserved on partial candidates;
  every verdict committed before part 1 is hashed; the count and ceiling do not move after.
- **X56 — two starting points, one space.** c05 and W44's joint point by hash; both paths
  recorded; the landed point the better by the selection metric on the gate population.
- **X57 — the operator lands inert, and is proven so by bytes.** Every shipped digest, every
  golden and every 1x row byte-identical at its landing; the leaf fitted only after clause 4's
  ladder shows the separation it exists for.
- **X58 — wave-owned tools.** Every declaration, fit, stage, seal and cut tool W45 runs is its
  own parameterised copy refusing W44's hash, directory and stage; only immutable inputs are
  shared by path.

## Ordering & Dependency Map

1. This draft's adversarial review; the parent merges the charter.
2. G0: the operator inert (review high); the tools; the rule and the rehearsal; part 1 hashed;
   the ladders; part 2 hashed; review; merge; both hashes checked on main.
3. G1: the fit; the freeze; the runtime; the stage; the gate report; the parent's ruling; the
   exposure; publication; review; merge with the tree copied.
4. G2: the landing; review; merge; the c9d chain; the user's `pnpm release`; the tag.
5. Close.

## Risks & Mitigations

- **The operator cannot separate 96 from 160 on the renders** (the far curve's start is the
  thickness knee at 96, so span 96 sits at `decline` 0 and 128 at 0.5 only if the span top is
  160; a different Apple law could need the grading to start below 96). Mitigation: clause 4's
  ladder before any fit, with the span top swept; if flat, the wave closes at G0 with the
  operator inert and the finding written.
- **The grading's evaluation site costs frame time or breaks a composite.** Mitigation: the bench
  row read at G0 (a); the per-surface uniform preferred unless `glass-over-glass` needs the
  per-pixel form; byte identity at identity either way.
- **The rule is tuned to the joint point.** It fails the joint point on both the count and the
  ceiling (Design), and both are fixed with their reasons before the rehearsal (X55).
- **The thin trade is not separable by any lever.** Decision Log 5 names it; the stratum
  aggregates bound it.
- **The CSS tier moves uncompensated** (the floor and span top reach it; the tap and its grading
  do not). Priced at the gate as a tier residual.
- **W44's prepared tooling is untested and W44-bound.** X58: W45-owned copies, each tested on c05
  (a seal of c05's bytes reproduces its digests; a stage of the shipped documents reproduces the
  published rows) before touching the frozen documents.
- **Browser automation from other sessions** during G1's reads: the classifying census.

## Deferred / Out of Scope

- **A per-span tap WIDTH** (Apple's narrow term scales its width, not only its weight): a
  per-surface or per-fragment texture cost W26 declined; if the share grading lands short of
  Apple's ×4.4 drop at c = 16, the width is the next operator.
- **The thin span's pitch trade** if G0 finds no lever (Decision Log 5).
- **The 1x texture at 0.25** (W44 Deferred; the operator's 1x twin would be that wave's); **the
  0.5 generation's texture** (X41); **the dark scheme at 0.25**; **the CSS tier's fine-pitch
  under-structure**; **accessibility at 0.25, the continuous slider, the body law**.

## Tracking Map

| child | status | ledger |
| --- | --- | --- |
| G0 | NOT STARTED; waits on this draft's review | §5.205 |
| G1 | NOT STARTED | §5.206 |
| G2 | NOT STARTED | §5.207 |

## Decision Log

### Decision Log 1 — RULED 2026-10-03 (the parent): the operator

**Ruled:** one new leaf, `sizeHeavySecondShareFar2x`, the second tap's share graded on the
scatter's far curve, identity 0, 2x-anchored with an implicit 1x twin of 0, a plain value drop in
the identity table, landed inert in G0 with every shipped digest and golden byte-identical; the
CSS tier declines it with the tap.

*Reasoning.* W28's precommit: an operator is added when the delta shows a structure the existing
profile cannot fit, and it is the smallest one the NAMED structure needs. The structure is named
twice over — Apple's ×4.4 drop in the c = 16 pass between span 96 and 128 against vitrea's flat
pass (Grounding), and the review of v1's reading of the law showing every existing grading acts on
the sharp component or saturates at 96. The smallest operator is one signed leaf on a curve the
material already evaluates, with no new texture, no new span statistic and no per-fragment tap;
its identity is exact and its 1x inertness is by construction and proven by render. LT gives the
physical reason: the narrow term's weight in the composite is what the slider sets, and its width
follows the opacity, which follows the span.

*Declined:* a per-span tap width (W26's cost reason; Deferred); `sizeScatterHeavyShareThick2x`
(not in the document's leaf set, and `sizeThickness` saturates at 96, so it cannot separate 96
from 128); a share graded on `sizeThickness` (the same saturation); fitting within the existing
leaves again (the mechanism is absent, and W44 showed what that costs).

### Decision Log 2 — RULED 2026-10-03 (the parent): the scope

**Ruled:** W44's scope and contracts; the leaf set W44's five plus `sizeScatterSpanMax2x` and the
operator; X44 narrowed for the operator's key in the active and receded light 0.25 documents;
W44's referee machinery by path; W44's declaration and execution tools by parameterised port
(X58).

*Reasoning.* The review of v1: a leaf the document does not name cannot be built, sealed or
exported under X44, and W44's tools pin W44's charter, hashes and directories. The narrowing is
the same shape as W44 Decision Log 7's for the receded share, and the 0.5 generation's documents
resolve the leaf at its identity, so X41 and the 0.5 digests are untouched.

### Decision Log 3 — RULED 2026-10-03 (the parent): the landing rule

**Ruled:** as the Design states: growth-only change; the band per stratum declared; the aggregate
and its tolerance on A's own scale, gated at three cells; count three, ceiling 3B, a stated
tradeoff; rehearsed on the three complete W44 maps, c05, the pre-fit and the synthetic cases.

*Reasoning.* W44's crossing veto rejected four cells whose error shrank; its per-cell veto had no
count. The review of v1 showed the aggregate clause was not executable (W44's aggregate is
dimensionless and the bar is linear SD; T's band was unresolved; the inactive photo's aggregate
"worsened" with every cell unchanged), so each is now defined on one scale with a tolerance of
the same form as W44's tie. The rehearsal cannot be over 100 complete maps because W44 rendered
97 candidates on move populations only; it is over what is complete, with UNMEASURED kept, and
over cases written to the rule's text.

*Declined:* a rule with no per-cell clause; a perceptual justification of the ceiling (none is
measured); a rehearsal stop that requires some old candidate to pass (a new rule need not admit
one).

### Decision Log 4 — RULED 2026-10-03 (the parent): one space, two stages, two starting points

**Ruled:** as the Design states, with the predictions from the actual law.

*Reasoning.* The operator and the span top act on the same deep composition as the floor and
the tap, so they are one stage; the thin start and the receded overrides are W44's. The joint
point is a starting point because it is the best known point and the search must show whether the
operator improves on it; c05 is the other so a search descending from the joint cannot inherit
its trades unexamined. The review of v1 found the starting point a legitimate reuse of fit
evidence and not an exposure.

### Decision Log 5 — RULED 2026-10-03 (the parent): the thin trade is read, then named

**Ruled:** G0 reads the thin-span transfer per lever; the charter attributes it to nothing in
advance; if no lever separates `checkerboard-4` from the pitch-16, 32 and text thin cells, it is
a named residual and the thin start lands where the rule says.

*Reasoning.* v1 attributed it to the sharp width on a wrong number (1.25 CSS px; the renderer
draws 1.25 device px), and the review showed the sharp term's pitch curve is flatter than that
argument needed. The memory lesson: rule on a mechanism after the separating measurement.

### Decision Log 6 — RULED 2026-10-03 (the parent): the release

**Ruled:** as W44 Decision Log 6; the operator ships inert in every document but the 0.25 light
pair, named in the changeset.

## Surprises & Discoveries

Found while drafting (2026-10-03):

1. **Four of W44's seven overshoots shrank their error**, which a regression clause must never
   reject; read on growth, the joint point has six regressions over B, four of them over 3B.
2. **Apple's pass at c = 16 drops ×4.4 between span 96 and 128** (0.099 → 0.026 → 0.022) where
   vitrea's is flat; this is the slider's narrow term widening with the span, and no existing
   leaf grades the tap by span.
3. **`sizeScatterHeavyShareThick2x` is not in the 0.25 or 0.5 light documents**, and would not
   separate 96 from 128 if it were (`sizeThickness` saturates at 96).
4. **The sharp term draws at 1.25 device px, not CSS px**, so its pitch curve at 2x is flatter
   than v1 argued (c = 8 at 0.79, c = 32 at 0.985).
5. **W44's 97 non-joint candidates have no landing population** (28–34 cells each), so a
   "100-candidate rehearsal" was never possible as a landing rehearsal.

## Revision Notes

- 2026-10-03 (v1.1; the adversarial review of v1 (`d21a6626`), needs-attention, three P1 and
  three P2, every finding accepted by the parent and folded):
  - **[P1] `sizeScatterHeavyShareThick2x` is forbidden by X44** (not in the document's leaf set):
    struck; the operator's key is admitted by a ruled narrowing (Decision Log 2).
  - **[P1] The thick lift destroys the separation it promised**: the mechanism rewritten from the
    actual law; the wave is now the operator wave (Decision Log 1), with the span top kept for the
    far curve's end.
  - **[P1] The aggregate gate was not executable**: the band per stratum, the aggregate and its
    tolerance on one scale, the gating threshold of three cells (Decision Log 3).
  - **[P2] The budget's rationale miscounted** (six over B, four over 3B; B is one code at this
    bar): the Grounding table recomputed; the count and ceiling restated as a tradeoff with no
    perceptual claim.
  - **[P2] The 100-candidate rehearsal lacked landing populations**: the rehearsal is on the
    three complete maps, c05, the pre-fit and synthetic cases; UNMEASURED preserved (X55).
  - **[P2] W44's tools are wave-bound**: X58 and clause 2, parameterised ports refusing W44's
    bindings; shared inputs by path only.
  - Corrections: the CSS tier reads the span top (and the floor and ramp); the sharp term is 1.25
    device px; the thin trade is read, not attributed (Decision Log 5).
- 2026-10-03 (v1, drafted by the parent under the user's mandate, from claims §5.203 §8, the
  joint point's committed outputs, the material's leaf documentation and the two memory lessons on
  improvement rules). An adversarial review requested before G0.
