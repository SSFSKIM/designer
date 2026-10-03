# W45 — the span-selective texture refit at 0.25: the deep share graded by span, the thin trade named, and a landing rule rehearsed on W44's joint point before it is hashed (2026-10-03)

**Status: DRAFT v1 (2026-10-03), for adversarial review before G0.** Chartered from W44's close at
the finding (claims §5.203 §8; W44 charter Decision Log 4 "Otherwise", RULED by the parent
2026-10-03): the fit's joint point cut the fine stratum's error by 62 % and brought the receded
fine checkers within Apple's, and failed the landing rule on three cells moved further under and
seven thin cells pushed past Apple, with no point in the declared space clearing them. Main is at
`ad93ff9b` (W44 G1 merged); W44 G2 lands T1 in the owner test (§5.204). The holdout and the twelve
referees are unspent for the 0.25 light documents. **Under the user's 2026-10-03 mandate (W44
Decision Log 0) the parent rules this charter's Decision Logs and reports them.** Ledger
§5.205–§5.207 are reserved.

## Decisions

The full entries are Decision Logs 1–5 at the tail.

| DL | question | status | what holds |
| --- | --- | --- | --- |
| 1 | the scope | **RULED** by the parent, 2026-10-03 | the 2x light `-glass0.25` material, through W44's leaves plus the two it never searched (`sizeScatterSpanMax2x`, `sizeScatterHeavyShareThick2x`); X48 holds; W44's T1, bar, referees, manifest and planner are reused unchanged |
| 2 | the landing rule | **RULED** by the parent, 2026-10-03 | regression is error growth alone (no crossing veto); a stratum × pose aggregate may not worsen; a per-cell growth budget with a count and a ceiling; rehearsed on W44's 100 committed candidates and on c05 before part 1 is hashed, and the rehearsal's verdict on W44's joint point recorded whatever it is |
| 3 | the moves | **RULED** by the parent, 2026-10-03 | one joint space in two stages: the span-graded deep composition (floor, span top, thick lift, the tap) on the mid and thick rest cells first, then the thin start and the receded overrides; W44's joint point and c05 are declared starting points; predictions per lever hashed |
| 4 | the thin-span pitch trade | **RULED** by the parent, 2026-10-03 | named, not closed: it needs a per-scale sharp width, which is an operator (X44); the thin start lands where the aggregate says and the trade is a named residual |
| 5 | the release | **RULED** by the parent, 2026-10-03 | as W44 Decision Log 6: a `@vitreajs/vitrea-web` minor (0.27.0), the light 0.25 generation superseded, the dark one unchanged, the user's `pnpm release`; no changeset if the wave closes at a finding |

## Purpose

**What the wave is for.** The least possible gap to Apple's material at the clearer glass, at
Retina scale. W44 built the referee (T1, now adopted) and found, on 103 renders, that the 2x light
texture gap has three parts and that the material's existing leaves can close most of it: at the
joint point the fine stratum's aggregate fell 0.6462 → 0.2455, the receded fine checkers went from
×3.9–5.3 over Apple to within, the coarse receded cells from ×2.5–3.4 to ×1.2–1.5, and the thin
rest cells from ×0.5–0.9 under to ×0.8–1.2. What it could not do with the levers it declared was
hold span 96 and span 128–160 apart: `checkerboard-8` at `rrect-md` needs MORE structure while
`rrect-ml` and `rrect-lg` need less, and `checkerboard-32` at `rrect-lg`, on Apple at c05, must
not take the mid band the fine thick cells want (§5.203 §8). The deep share is one number per
span curve, and that curve's top and thick lift — `sizeScatterSpanMax2x` 256 and
`sizeScatterHeavyShareThick2x` 0 — were listed as candidate leaves and never searched.

**The best version of this is three things:**
1. **A deep share graded by span.** With the floor below 1 and the span top lowered toward 128,
   the sharp share tapers from the thin spans through 96 to 0 at 128 (`kDeep = floor + (1 −
   floor)·smoothstep(32, spanTop, span) + thickLift·sizeThickness(span)`), which is the shape the
   vetoing cells ask for; the second tap carries pitch 16 and 32 at the mid and thick spans as it
   did in W44. One joint space, searched in two stages, from two declared starting points.
2. **A landing rule that measures regression as regression.** W44's rule vetoed a cell that
   crossed Apple into a miss even when its error shrank, and vetoed any single cell moving away
   beyond the bound; both are never-worse rules in disguise (the memory lesson, twice). W45's
   rule reads error growth only, bounds it per cell with a count and a ceiling, and bounds every
   stratum × pose aggregate; it is rehearsed on the 100 W44 candidates before it is hashed, and
   the rehearsal's verdict on the joint point is recorded either way.
3. **The same referees, read once.** T1 as adopted; the twelve referees and the canonical holdout
   unspent since W44, read once at the frozen bytes after the gate; the publication through
   W40's publisher superseding the light 0.25 generation.

**What the wave does not do.** No native capture. No 1x or dark change (X48). No operator (X44):
the thin span's pitch trade (Decision Log 4) is named. No change to T1, its bar, its manifest or
its planner. No re-read of anything W44 read: the joint point's numbers are evidence, not a verdict.

## Parent-Level Acceptance

1. **Declared before fitted, in W44's two parts (G0).** *Metric:* part 1 (T1 as adopted, the bar,
   the manifest, the landing rule with its rehearsal record, the ladders' protocol and permitted
   decisions, the two starting points by declaration hash, the regression references) and the
   part-2 draft hashed before any ladder render; part 2 after the ladders as a validated diff;
   W44's `declare.py` reused with its `amend` and `amend-fit` rules. *Stop:* as W44 clause 1.
2. **The landing rule is rehearsed on renders that trade (G0).** *Metric:* the rule's three
   outputs on every one of W44's 100 committed candidates (`results/2026-10-03-w44-g1-refit/
   fit/candidates/`), on c05 and on the pre-fit render, before part 1 is hashed. *Bar:* the
   verdict per candidate is committed; the joint point's verdict is recorded whatever it is; the
   rule's count and ceiling are stated with their reasons (Decision Log 2) and not moved after
   the rehearsal. *Stop:* a rule that no candidate better than c05 by every aggregate can pass is
   not a rule and goes back to the drawing before the hash.
3. **The two new leaves move the drawn quantity (G0).** *Metric:* ladders for `sizeScatterSpanMax2x`
   and `sizeScatterHeavyShareThick2x` at a floor below 1, on W44's fixed cells plus the three
   vetoing mid/thick cells, both poses; byte identity at 1x (X48). *Stop:* a flat leaf is struck.
4. **Measured before moved (G1).** As W44 clause 5, with the candidate identity patch-and-digest.
5. **The gate, before the exposure, on the shipped bytes (G1).** As W44 clause 6: the runtime
   regenerated and its export test green before the stage; the stage filled with every declared
   set less the referees; the owner test's adapters on the stage union against a new cut; T1 as
   adopted; every other row re-baselined on the published c05 render; `tier-coherence`; X48 at
   1x; the sheets to the MacBook.
6. **The exposure, once (G1).** As W44 clause 7: the canonical holdout and the twelve referees in
   one read per tier, recorded as read 7 with the manifest's hash.
7. **Nothing frozen moves (G0–G2).** As W44 clause 8, plus W44's committed evidence and hashes.
8. **The landing (G2).** As W44 clause 9: the publication superseding `6d18c059eb42`, the tree
   copy and the superseded move, T1's owner-test block re-baselined on the new generation with
   every miss named, the generated module re-pinned, the demo refreshed, CLAUDE.md, the READMEs,
   the changeset, the c9d chain.
9. **By eye, and the ledger (every child).** As W44 clause 10.

## Grounding Baseline (main at `ad93ff9b`)

**W44's joint point** (`results/2026-10-03-w44-g1-refit/fit/candidates/m3-t0.1/`, declaration
`66bf5a01…`): active light `sizeScatterFloor2x` 1, `sizeHeavySecondShare` 0.5,
`sizeHeavySecondSigma2x` 5 CSS px, `sizeScatterRampStartThin2x` 0.8; receded light
`sizeScatterRampStartThin2x` 0.1 (the receded share equal to the active, by the fit); dark
unchanged. Its T1 outputs over the 94 gate cells are committed (`fit/path/joint.txt`,
`finding.txt`). The ten vetoing cells, with native / c05 / joint in linear SD:

| cell | native | c05 | joint | c05 ratio | joint ratio | W44 state |
| --- | --- | --- | --- | --- | --- | --- |
| `checkerboard__rrect-md__rest` | 0.1501 | 0.0976 | 0.0814 | 0.65 | 0.54 | away, g 2.4 B |
| `checkerboard-8__rrect-md__rest` | 0.0991 | 0.0841 | 0.0401 | 0.85 | 0.40 | away, g 6.9 B |
| `checkerboard-64__rrect-sm__rest` | 0.0680 | 0.0319 | 0.0118 | 0.47 | 0.17 | away, g 2.4 B |
| `checkerboard-32__rrect-lg__rest` | 0.1336 | 0.1329 | 0.1675 | 0.99 | 1.25 | overshoot (g > 0) |
| `checkerboard__rrect-sm__rest` | 0.1940 | 0.1451 | 0.2322 | 0.75 | 1.20 | overshoot (g < 0) |
| `checkerboard__capsule-button__pressed` | 0.1938 | 0.1807 | 0.2310 | 0.93 | 1.19 | overshoot (g > 0) |
| `checkerboard-32__rrect-sm__rest` | 0.2161 | 0.1954 | 0.2681 | 0.90 | 1.24 | overshoot (g > 0) |
| `checkerboard-32__capsule-button__rest` | 0.2195 | 0.1897 | 0.2519 | 0.86 | 1.15 | overshoot (g ≈ 0) |
| `hc-text-28__rrect-sm__rest` | 0.1891 | 0.1444 | 0.2275 | 0.76 | 1.20 | overshoot (g < 0) |
| `hc-text__rrect-sm__rest` | 0.1595 | 0.1237 | 0.1868 | 0.78 | 1.17 | overshoot (g < 0) |

Read on error growth alone, four of the seven overshoots have g ≤ 0 or near it (their error
shrank or held) and three have g > 0; the three `away` cells are real regressions, one of them
large (`checkerboard-8` md, ×0.85 → ×0.40). The aggregates: F 0.6462 → 0.2455; F inactive 1.290 →
0.047; C rest 0.172 → 0.103; C inactive 0.852 → 0.235; P rest 0.419 → 0.393; P inactive 0.139 →
0.172 (all unchanged cells); the selection metric 0.3458 → 0.1876.

**Where the vetoes sit on the span axis** (§5.203 §8). `checkerboard-8` md (span 96) needs more
structure while `checkerboard-8` ml and lg (128, 160) need less: at the joint they read 1.38 and
1.47 over. `checkerboard-32` lg is on Apple at c05 and takes the mid band. The thin cells trade
by pitch: `checkerboard-4` sm and capsule still under (0.74, 0.64) at thin start 0.8 while the
pitch-16, 32 and text thin cells are 15–24 % over.

**The two unsearched leaves** (`packages/renderer-webgpu/src/material.ts`):
- `sizeScatterSpanMax2x` 256: the span at which the deep share's smoothstep from `sizeSpanMin` 32
  reaches 1 at dpr 2; "a floor of 1 leaves the deep value nothing to rise to", which is why W15
  never moved it. With the floor below 1 it is the taper's end.
- `sizeScatterHeavyShareThick2x` 0: a lift on the deep heavy share riding `sizeThickness(span)`
  (0 at span ≤ 32, 1 at ≥ 96), clamped at 1; inert while the floor is 1 "because the clamp
  absorbs any lift" (W25). With the floor below 1 it is the thick end's own share.
Both are 2x-anchored and 1x-inert by construction (`rampAtScale`), named in the active 0.25
document already (X44), and in the receded document's twin only if its twin names them: the
receded twin names neither, so both are inherited in the receded pose.

**The thin span's pitch trade.** Apple's thin 0.25 surface passes `checkerboard-4` (c = 8), the
pitch-16 (c = 32) and `checkerboard-32` (c = 64) backdrops at nearly one ratio to their own SD
(0.17–0.22 of a 0.5 backdrop), which only a sharp component narrower than vitrea's can do; vitrea's
sharp term is `blurSigma` 1.25 CSS px through the mip chain at both scales, and raising its share
(the thin start) raises c = 32 more than c = 8. A per-scale sharp width would be a new leaf, an
operator (X44), and is Decision Log 4's named residual.

**What W44 left ready.** T1 adopted (§5.204); the bar 0.5 code everywhere; `referees.json` and the
planner's two whitelists; W44's `declare.py` with `check`, `check-fit`, `amend`, `amend-fit`;
`cuts/t1.py` and `readings.py` with the T stratum's two bands; the candidate builder admitting the
receded second-tap keys; the prepared and unrun `seal/seal.ts`, `stage/stage.py`, `stage/x48.py`
and `sheets/sheets.py`; 100 committed candidates with their T1 outputs; the holdout ledger at
read 6.

## Design (advisory unless marked)

### The landing rule (MARKED; Decision Log 2)

Per cell as in W44: `n` native, `c` c05, `k` candidate, `e(x) = |x − n|`, `g = e(k) − e(c)`,
`B = max(1 code, 2·bar)`, `δ = |k − c|`. Fidelity as W44 (`within` by `B` or 10 %). **Change,
a partition by error growth alone:** `unchanged` if `δ ≤ bar`; else `toward` if `g ≤ 0`; else
`away` with `g`. There is no crossing state: a cell that crosses Apple with a smaller error is
`toward`, and one that crosses with a larger error is `away` by its growth. Aggregates per
stratum × pose as W44, with the F aggregate the headline.

On the final stage, WebGPU, 2x light, both poses, over F ∪ T ∪ C ∪ P less the referees (a T
cell on T1-fine for fidelity and change, T1-low for `away`):
- **Full close:** every F cell within; every stratum × pose aggregate at most c05's; at most
  **three** cells `away` with `g > B`, none with `g > 3B`, each named; every other adopted row
  passing or its miss named; the twelve referees within at the exposure. Lands.
- **Improvement landing:** the F aggregate at most half of c05's; every stratum × pose aggregate
  at most c05's plus the bar; at most **three** cells `away` with `g > B`, none with `g > 3B`,
  each named; every referee within or an unchanged miss; every other adopted row passing or its
  miss named. Lands as improved, every F cell not within named.
- **Otherwise** the wave closes at the finding.

*The count and the ceiling, with their reasons, fixed before the rehearsal:* three is the number
of cells W44's joint point moved away beyond the bound, which is what a span-graded deep share
exists to repair, so a candidate that still has more has not used the new leaves; `3B` is the
largest growth a fine-pitch cell can take while staying inside the band the eye reads as the same
texture class (a code and a half on a mid-grey body), and `checkerboard-8` md's growth at the
joint, 6.9 B, is what the rule must reject. The rehearsal (clause 2) reports the joint point's
verdict under this rule without moving either number.

### The moves (MARKED; Decision Log 3)

One joint space, two stages, two declared starting points (c05 and W44's joint point by
declaration hash), the selection metric and tie as W44's, the search procedure as W44's
(coordinate sweeps, at most two passes, a full factorial permitted):

- **Stage 1, the span-graded deep composition** (rest, mid and thick cells; the within clause =
  the F and pitch-16 cells of the stage, as amended in W44): `sizeScatterFloor2x` ∈ [0.5, 1.0],
  `sizeScatterSpanMax2x` ∈ [96, 256] (grid 96, 112, 128, 160, 192, 256), `sizeScatterHeavyShareThick2x`
  ∈ [0, 1], `sizeHeavySecondShare` ∈ [0, 1] with `sizeHeavySecondSigma2x` ∈ [1.5, 6] CSS px, the
  1x second width 0 (W44's L3). *Prediction:* a floor near 0.7 with the span top near 128 and the
  thick lift near 1 holds `checkerboard-8` md within while ml and lg fall to within, and
  `checkerboard-32` lg stays on Apple because the thick lift takes the mid band off the thick
  spans; the tap at 0.5 × 5 CSS px carries pitch 16 and 32 at mid as in W44.
- **Stage 2, the thin start and the receded overrides** (as W44's moves 2 and 3, with the receded
  document's five leaves; `sizeScatterSpanMax2x` and the thick lift inherited in the receded
  pose). *Prediction:* the thin start lands below 0.8 under the error-growth rule, between
  `checkerboard-4`'s need and the pitch-16/32 cells' (Decision Log 4); the receded share lands
  at the active share, as in W44.
- **Interactions** as W44. The joint point is re-read at the end; a stage that undid the other is
  refitted once on the union.

### Referees: what carries over, and what is new

- **Unchanged:** everything W44 declared and built: T1 (adopted), the bar, the manifest, the
  planner, the loader's refusals, the regression references on c05 by hash (X52), X48, X49, X53,
  the freeze (1,818), X41 (911), the goldens, the dark 0.25 digests, W44's hashes and evidence.
- **New:** the error-growth change partition and the budgeted landing rule (Decision Log 2); the
  two new leaves' ladders; the rehearsal over 100 candidates (clause 2).

## Children

### G0: The rule rehearsed, the ladders, the declaration (ledger §5.205)

Branch `w45-g0-declaration`, evidence `packages/calibration/results/2026-10-03-w45-g0-declaration/`.
- (a) W44's `cuts/t1.py` extended with the error-growth partition beside W44's (both reported;
  W45's is the gate's), the budget clauses, and the pinned examples re-run under both.
- (b) The rehearsal (clause 2) over c05, the pre-fit and W44's 100 candidates, committed as a
  table; the joint point's verdict recorded.
- (c) The referee manifest, planner and loader reused by path; a red case that they are byte-
  identical to W44's.
- (d) Part 1 and the part-2 draft hashed (the rule, the starting points, the protocol for the
  two new leaves' ladders, the references); the ladders (clause 3); part 2 as a validated diff.
- Acceptance: clauses 1–3; independent review; merge; both hashes checked on main.

### G1: The refit, the gate, the exposure and the publication (ledger §5.206)

Branch `w45-g1-refit`, evidence `results/2026-10-03-w45-g1-refit/`. W44's G1 steps 1–8 with W44's
prepared tooling (`seal`, `stage`, `x48`, `sheets`), run and tested this time: the references;
the fit in two stages from both starting points; the freeze; the runtime first (X53); the stage
less the referees; the gate (clause 5) with a GATE REPORT to the parent, who rules each miss;
the exposure once (clause 6); publication. The worker stops at the gate report.

### G2: The landing (ledger §5.207)

Branch `w45-g2-landing`. W44's G2 list in full (clause 8): the superseded tree move, T1's block
re-baselined on the new generation with every miss named, the generated module, the demo, CLAUDE.md,
the READMEs, the changeset for 0.27.0, the c9d chain; the user's `pnpm release`.

## Cross-Child Contracts

**Carried from W44:** X1, X3, X24, X33, X41, X44 as narrowed, X45, X48, X49, X50, X51, X52, X53;
the worker and review rules; the census; no attribution; path-scoped adds; merges with the freeze
and X41 verified.

**New:**
- **X54 — regression is error growth.** No landing clause reads a crossing; every per-cell veto
  is a growth `g` against `B`, with a count and a ceiling stated before the rehearsal.
- **X55 — the rule meets a trade before the hash.** The landing rule is rehearsed on W44's 100
  committed candidates, and the verdict of every one is committed, before part 1 is hashed;
  the count and ceiling do not move after the rehearsal.
- **X56 — two starting points, one space.** c05 and W44's joint point are declared starting
  points by hash; the fit's path from each is recorded; the landed point is the better by the
  selection metric, a tie going to the fewer moved leaves.

## Ordering & Dependency Map

1. This draft's adversarial review; the parent merges the charter.
2. G0: the partition and the rule; the rehearsal; part 1 hashed; the ladders; part 2 hashed;
   review; merge.
3. G1: the fit; the freeze; the runtime; the stage; the gate report; the parent's ruling; the
   exposure; publication; review; merge with the tree copied.
4. G2: the landing; review; merge; the c9d chain; the user's `pnpm release`; the tag.
5. Close.

## Risks & Mitigations

- **The span-graded share cannot hold 96 and 128 apart either** (the smoothstep's shape is fixed
  and `sizeThickness` saturates at 96). Mitigation: the ladders on the three vetoing cells
  before the hash; if both leaves are flat on them, the wave closes at G0 with the finding and
  the next step is an operator wave.
- **The rule passes W44's joint point by construction.** It does not: `checkerboard-8` md's
  growth is 6.9 B against a ceiling of 3 B, so the joint point fails the rule as drafted, and the
  count and ceiling are fixed before the rehearsal with their reasons (X55).
- **The thin trade worsens under the error-growth rule** (the thin start may land lower and the
  cb4 thin cells further under). Mitigation: Decision Log 4 names it; the aggregate per stratum ×
  pose bounds it.
- **The CSS tier moves uncompensated** (the floor, span top and ramp reach it; the widths and the
  thick lift do not — G0 checks which of the two new leaves the CSS mirror reads). Priced as a
  tier residual at the gate.
- **W44's prepared tooling is untested.** G1 tests each piece on c05 (a seal of c05's own bytes
  must reproduce its digests; a stage of the shipped documents must reproduce the published rows)
  before using it on the frozen documents.
- **Browser automation from other sessions** during G1's reads: the classifying census.

## Deferred / Out of Scope

- **A per-scale sharp width** (the thin span's pitch trade; Decision Log 4): an operator wave,
  with the identity table extended and the goldens re-attributed.
- **The 1x texture at 0.25** (W44 Deferred); **the 0.5 generation's texture** (X41); **the dark
  scheme at 0.25**; **the CSS tier's fine-pitch under-structure**; **accessibility at 0.25, the
  continuous slider, the body law** (W43's Deferred).

## Tracking Map

| child | status | ledger |
| --- | --- | --- |
| G0 | NOT STARTED; waits on this draft's review | §5.205 |
| G1 | NOT STARTED | §5.206 |
| G2 | NOT STARTED | §5.207 |

## Decision Log

### Decision Log 1 — RULED 2026-10-03 (the parent): the scope

**Ruled:** W44's scope and contracts, plus the two unsearched leaves; nothing else moves.

*Reasoning.* The finding names the two leaves and the span boundary they exist to separate;
everything else W44 built is reused by path so the wave is a fit and a landing, not a rebuild.

### Decision Log 2 — RULED 2026-10-03 (the parent): the landing rule

**Ruled:** change as a partition by error growth alone; a stratum × pose aggregate may not
worsen; at most three cells `away` with `g > B`, none with `g > 3B`, each named; rehearsed on
W44's 100 candidates before part 1 is hashed; the count and ceiling fixed before the rehearsal.

*Reasoning.* W44's rule vetoed a crossing even when the error shrank, and vetoed any single cell
moving away beyond the bound, so a candidate better than c05 by every aggregate landed nothing
(§5.203). A crossing is not a regression; growth is. A per-cell veto with no count is a
never-worse rule, which the W42 lesson already named, so the budget has a count (what the new
leaves are for) and a ceiling (what the eye reads as a different texture class), both stated with
reasons before the rehearsal so the rehearsal cannot move them. The rehearsal is on renders that
trade, which W44's was not.

*Declined:* a rule with no per-cell clause (a large single regression could hide under an
aggregate); keeping W44's crossing veto (it rejected four cells whose error shrank).

### Decision Log 3 — RULED 2026-10-03 (the parent): one space, two stages, two starting points

**Ruled:** as the Design states.

*Reasoning.* The two new leaves act on the same deep share the floor and the tap act on, so they
are one stage, not a new move; the thin start and the receded overrides are W44's as fitted. The
joint point is a starting point because it is the best known point and the search must show
whether the new leaves improve on it; c05 is the other because a search that only descends from
the joint could inherit its trades.

### Decision Log 4 — RULED 2026-10-03 (the parent): the thin trade is named

**Ruled:** the thin span's pitch trade is a named residual; the thin start lands where the
aggregate and the rule say; a per-scale sharp width is the next operator wave's.

*Reasoning.* The trade is fixed by the sharp component's width (Grounding) and no existing 2x
leaf changes it; X44 holds, and an operator is a different kind of wave with its own identity
and golden work.

### Decision Log 5 — RULED 2026-10-03 (the parent): the release

**Ruled:** as W44 Decision Log 6.

## Surprises & Discoveries

Found while drafting (2026-10-03):

1. **Four of W44's seven overshoots shrank their error.** The crossing veto rejected cells whose
   distance to Apple fell (`checkerboard__rrect-sm__rest` 0.25 → 0.20 in ratio; `hc-text-28` sm
   0.24 → 0.20; `hc-text` sm 0.22 → 0.17), which is what a regression clause must never do.
2. **The joint point's one large regression is on the span boundary the new leaves address**
   (`checkerboard-8` md, growth 6.9 B), and the rule as drafted fails it, which is the test the
   rule should fail.

## Revision Notes

- 2026-10-03 (v1, drafted by the parent under the user's mandate, from claims §5.203 §8, the
  joint point's committed outputs, the material's leaf documentation for `sizeScatterSpanMax2x`
  and `sizeScatterHeavyShareThick2x`, and the two memory lessons on improvement rules). Five
  decisions ruled by the parent; an adversarial review requested before G0.
