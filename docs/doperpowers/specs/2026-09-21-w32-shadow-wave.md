# W32 — the shadow wave: the exterior vitrea draws, fitted as a whole rather than as a blur

**Status: OPEN 2026-09-21 — chartered by the parent on the user's "W32 Shadow wave will be it"
after the 0.21.0 publish, under the standing "rest on your judgement".** Executes W31's
Deferred-at-close item 4 (the next shadow wave carrying C1 and the joint fit of the shadow's three
lengths), W30's Deferred items 8 (the recede's exterior above span 96) and 10 (a shadow section for
`/laws/`), and W31's Deferred items 12 and 14 where they touch the evidence this wave reads.
Grounded on main at `7a4ad3b4` (0.21.0 published; tag `v0.21.0`).

## Purpose

The outer shadow is the largest single facet the project has measured, and after two waves on it
the shadow vitrea draws at a thick span is still not Apple's. W30 made its blur a function of the
casting span and the adopted row B1 says the law's σ is inside ±5 % of the native's fitted σ at
every thick span on every bed. W31 G1 then put a second instrument beside B1 and found that **a
green B1 and a wide exterior are consistent**: B1 compares the DOCUMENT's blur leaf in closed form
to a FIT of Apple's render, and that fit absorbs whatever else Apple's shadow is besides a blur.
The same instrument applied to both renders reads vitrea's exterior **+2.66 to +3.77 CSS px wider
than Apple's at every thick span on every standard bed, on the WebGPU tier** — additive, not
proportional — and the shadow's other two lengths, `spreadPx` 3.10 and `offsetPx` 7.95, are
inherited from the macOS 26.5 default, byte-identical in every document that carries them, absent
from both dark documents, and **have never been fitted on the macOS 27 bed** (claims §5.162 §2).
The eye's reading is the same finding from the other side: below a span-160 panel the ×8
difference carries visible level contours rather than a featureless haze (§5.160 §6), and the
per-band transmission error `Δa` at span 160 is negative at every band in every direction and
GROWS outward, where at span 44 it collapses to zero by 24 CSS px (§5.162 §1). The shape statistic
G1 declared for exactly this wave, C1, **fails today at span 128 on all four standard beds and at
span 160 on all four** (0.00487–0.00532 and 0.00733–0.00921 against ≤ 0.0045) and passes at 96.

The purpose of this wave is to fit the exterior vitrea draws — the three lengths `sigmaPx`,
`spreadPx` and `offsetPx` together with the amplitude anchors that ride the same falloff — against
an instrument that reads the RENDERED exterior rather than the law's closed form, per band and per
direction, on the macOS 27 bed; to give the receded documents an exterior of their own, since the
inactive pose reads six to nine times the active pose's shape error at span 160 and its far
exterior is three times the active halo on the sheets (§5.162 §3; tracker "The macOS 27 recede's
exterior is unfitted above span 96"); to read C1 on the result and adopt it if met, in the form
the span confound admits; and to make the operator legible on the site.

What this wave does not do is as fixed as what it does. No structure, chroma, tone or tint
constant moves (X3). No native capture is taken (X5). The macOS 26.5 documents' bytes do not
change and their digests stay the live pin under rule 2 (X1). The thin regime — spans 32 and 44,
where the eye calls the exterior right and the shape statistic reads 0.00168–0.00339 — is a STOP,
not a target: a fit that closes the thick spans by opening the thin ones has fitted the bound.

## Parent-Level Acceptance

1. **The exterior is cut per direction before any length moves, and the cut says which lengths
   the bed can identify.** G0 extends W31 G1's reader into this wave's own evidence directory: the
   shape statistic `T` and its per-band `Δa` resolved by DIRECTION (`above`, `below`, `left`,
   `right`, the axis's own groups), the per-direction extents and the fitted offset the axis
   already carries (`extent{Above,Below,Left,Right}{Native,Web}`, `offsetY{Native,Web}`), and the
   departure — all read off `results/matrix.json`'s current generation with no capture. From the
   NATIVE per-band per-direction slopes G0 fits the renderer's own falloff model
   (`Φ((d − spread)/σ)` on the scene's signed distance, translated by the offset, at one amplitude)
   per cell and reports the (σ, spread, offset) triple with its conditioning: whether σ and spread
   separate on four bands per direction with the `0-3` band excluded, whether the `below`
   direction identifies the offset, and **what Apple's own outset reads** — the question §5.162 §9
   finding N-10 left open and the one that decides whether the +2.66…+3.77 gap is vitrea's
   `spreadPx` or the difference of two outsets. Where the pair does not separate, G0 says so and
   the fit in clause 3 is run on rendered rounds against the direction-resolved statistic rather
   than on a native-side model. The recede's exterior is cut the same way on the inactive rows.
2. **Bounds before reads; the adopted form of C1 is chosen from the tables and declared before the
   fit; the stops are numbers.** G0 tables C1 as declared (one `T` ≤ 0.0045 per standard bed per
   thick span, the upper middle order statistic over active non-holdout WebGPU cells) AND the two
   span-aware forms §5.162 §3 named — per-span bounds, and a form normalised by the native
   shadow's own depth in the window — on the current generation, and the parent rules at G0's
   close which form is the candidate adopted row (Decision Log 1 (c)). The stops: **B1 at the
   shipped bytes** (adopted; the σ law's closed form stays inside every served bed's ±5 % window —
   the fit may move `sigmaPx` and `sigmaSlopePerSpan` only inside that window, Decision Log 1
   (a)); **B3's departure residual** ≤ 0.00035 on the WebGPU tier as W31 held it; **the thin
   regime's shape** — `T` at spans 32 and 44 on every standard bed no worse than today's reading
   plus the native-pair bar; **the chroma rows M1 and M2, the structure, tint and rim rows expected
   unmoved**, each read before and after. The seven `MISSED_27_ROWS` rows are decomposed for what
   the shadow can reach: the three W30 claimed and had refuted (`checkerboard__rrect-lg__rest` and
   `checkerboard__glass-over-glass__rest :: ssimMean` on 1x light dom, `photo__rrect-lg__rest ::
   ssimOutside` on reduced-transparency dom) are "reachable if" with the headroom stated from
   G1's `T` on them (§5.162 §4); nothing is CLAIMED through this wave but its own clause.
3. **The joint fit, on the fidelity target, with the free reading and the shipped reading both
   recorded.** G1 fits `spreadPx` and `offsetPx` per scheme — and `sigmaPx` / `sigmaSlopePerSpan`
   inside B1's window with `sigmaSpanRefPx` held at 96 and the knee held at 44 by re-deriving
   `sigmaThinOffsetPx` (W30 Decision Log 2 (b), 3 (c)) — on rendered rounds over the calibration
   and validation cells plus the pitch ladder at the thick spans (granted as W30 Decision Log 2 (a)
   granted it), WebGPU tier, against the direction-resolved shape statistic G0 declared, checked
   on validation, with the six occlusion anchors and `liftAmplitude` re-solved in closed form per
   round from the departure as W30 G3 solved them (`anchor-solve.py`'s linearity). **Two fits are
   run and both are recorded: the free fit, in which the σ law is unconstrained, and the
   constrained fit, in which it stays inside B1's window; the constrained fit ships.** If the two
   differ by more than the bed's own noise, the free fit's reading is put to the user as a
   Decision Log draft on whether B1 is re-stated in a later wave — never in this one (X4). The
   dark documents carry their own `spreadPx` and `offsetPx` if the dark bed's reading differs from
   the light one's beyond the bar, and inherit them explicitly recorded if not. The CSS tier's
   `box-shadow` follows the same leaves through the mirror `tier-coherence` pins; its rendered
   width is recorded, not bounded (§5.162 §9 N-11).
4. **The recede gets an exterior of its own.** The receded documents' six anchors and lift are
   solved on the INACTIVE cells — calibration and validation at spans 44 and 96, the ladder's
   inactive rungs at 128 and 160 (Decision Log 1 (b)) — with the lengths shared with the active
   document unless the inactive bed's direction-resolved reading says otherwise, in which case the
   receded document carries its own and the reading is recorded. The far-exterior halo on
   `checkerboard__rrect-lg__inactive` (17.42 / 15.89 against ≤ 5.92 active, tracker) is read
   before and after on the sheets.
5. **Re-seal and read in one merge, once per frozen configuration by artifact.** The four macOS 27
   documents re-sealed under rule 2 with history (the two dark documents' wrong
   `$comment-sha-history` parenthetical corrected BESIDE in the same re-seal, W31 Deferred 14);
   `configuration.py record` before the holdout with its output in the ledger, from the
   cross-gate location G0b gives it; the canonical run appended beside the 0.21.0 rows — six
   profiles, two tiers, calibration + validation, the ladder — then holdout **once**; the
   append-check; the split; the read's capture tree copied to the canonical `web-captures/` at
   merge and the checker G0b lands run against it; `freeze.py verify` 1,818 and the 27 gated-cell
   count (230 / 726, or what the machine says with the difference explained) pinned at every merge
   (X10). The verdict per profile per tier per clause with every missed cell named; a miss
   recorded, not widened, not re-fitted.
6. **The landing.** C1 in its ruled form adopted into `adopted-thresholds.test.ts` on the parent's
   decision, reading a cut RE-RUN into the adopting gate's own directory with the `atDocuments` and
   `withHoldout` guards (§5.162 §9 B-1) and `CONTRIBUTING_CELLS` counted from the bed; sheets
   native | WebGPU | CSS | ×8 for `rrect-lg` and `capsule-button` in both schemes at both scales,
   active and inactive, looked at, with the level contours named present or absent; a shadow stage
   on `/laws/` that shows one caster's exterior as the span moves (W30 Deferred 10; the design put
   to the user at G2's dispatch, Decision Log 1 (d)); `CLAUDE.md`, both READMEs and the CHANGELOG
   saying what moved; the coverage matrix re-scored where a row moved; the fixed group versioned
   **0.22.0** and prepared, `pnpm release` the user's hand, the tag after.
7. **Every gap left is written down where it belongs**, with the evidence and the shape of the
   work: the wave's Deferred-at-close list in W31's shape, the tracker, the ledger.

## Grounding Baseline (main at `7a4ad3b4`, 0.21.0 published)

- **The material.** `MaterialOuterShadow` (`packages/renderer-webgpu/src/material.ts`): the
  lengths `offsetPx` 7.95, `sigmaPx` 15.55, `spreadPx` 3.1 in the macOS 26.5 default; the σ law's
  three leaves at 0 there. The macOS 27 light document carries `offsetPx` 7.95, `spreadPx` 3.1,
  `sigmaPx` 8.96, slope 0.1314, ref 96, thin offset −6.8328; the dark document carries `sigmaPx`
  9.04, slope 0.1340, ref 96, thin offset −6.968 and **no `offsetPx` or `spreadPx`** (inherited
  from the default). Both receded documents carry their active document's anchors leaf for leaf
  (light 0.1158 / 0.1827 / 0.26, dark 0.133 / 0.2263 / 0.3409) and no length of their own.
  Shipped digests 3dc24a74f17fd87e / 8a43f54162606db4 / ab3ed65aa02869b1 / e1f42c5656ef392f.
- **The shader** (`src/wgsl/optics.ts`, `outer_shadow`): the falloff is `Φ((d − spread)/σ)` on the
  field texture's signed distance read at the position shifted by the offset, σ per pixel from the
  casting span (`outer_shadow_sigma`), the amplitude the blend of the thin regime and the thick
  anchors on the size curve, composited multiplicatively; the lift on the same falloff. The
  displacement's clamped-off distance is added back (exact on a straight edge, errs toward less
  shadow past corners). Spread and σ are therefore separate parameters of the render, which is
  what makes them separately fittable on it.
- **The CSS mirror** (`platform-web/src/css-tier.ts` line ~2341): one `box-shadow` per surface —
  `0 offsetPx blur(2σ(span)) spreadPx rgba(0,0,0,α)` — from the same leaves; `outerShadowSigmaPx`
  is the law's CSS-side copy; `outerShadowReachPx` bisects the falloff for the group clip and the
  scissor pad, so the reach moves with every length (X8: the padding constant does not).
- **The instrument.** `packages/calibration/src/metrics/shadow.ts`: per cell, per direction and
  `all`, five bands 0-3 / 3-6 / 6-12 / 12-24 / 24-48 CSS px outside the declared contour, the
  affine pair `(a, c)` in linear light on both sides (`affineNative`, `affineWeb`, 30 entries
  each); the blurred-edge fit `falloffSigma{Native,Web}` with its residual; the extents and
  offsets per direction; `meanDeparture{Native,Web}`; `backdropSupport` with the axis's own floor
  0.1. W31 G1's reader `results/2026-09-21-w31-g1-exterior-instrument/exterior-instrument.py`
  computes candidate (i) and `T` with `--out`, `--with-holdout`, `--at-documents`, `--against`;
  its §4 already prints `Δa` per band per direction for named cells. The native-pair noise bar
  (`results/2026-09-19-w29-g2-native-delta/noise-bar.json`): p95 0.000229 and max 0.002044 on
  the worst affine band over 432 cells.
- **The bed** (`apps/reference-apple/scenes.json`, 168 scenes). Active, by span: 32 `rrect-sm` (1
  cal + 1 val + 12 probe); 44 `capsule-button` (11 cal + 2 val + 4 holdout + 11 probe) and
  `toolbar-group` (1 + 1); 96 `rrect-md` (4 cal + 2 val + 1 holdout + 9 probe); 128 `rrect-ml` (3
  cal + 7 probe); 130 `glass-over-glass` (2 holdout); 160 `rrect-lg` (3 holdout + 13 probe).
  Inactive: 44 `capsule-button` 11 cal + 2 val + 4 holdout + 4 probe; 96 `rrect-md` 4 + 2 + 1 + 8;
  128 `rrect-ml` 5 probe; 160 `rrect-lg` 3 holdout + 10 probe. **Every non-ladder span-160 cell is
  holdout, active and inactive alike**; the ladder is what makes spans 128 and 160 fittable, and
  W30 Decision Log 2 (a) granted it for the σ law. The 27 bed at the shipped documents: 230 gated
  cells / 726 rows, 124 of them holdout; `freeze.py verify` 1,818.
- **The rows.** B1 adopted (`adopted-thresholds.test.ts`, reading W30 G0's `shadow-cut.json`);
  C1 declared and not adopted (`bounds-declaration.md` §3 in G1's directory, with the B-1
  condition); `MISSED_27_ROWS` at 5 + 3; M1 and M2 adopted on the chroma at W31 G4 with three
  cells missed. The current generation's `T` per bed per span (§5.162 §1's table) is the
  before-reading this wave is judged against.
- **The tooling this wave inherits.** W30 G3's `shadow-law.py` (the closed-form σ solve, four
  objectives, `--at-shipped`), `anchor-solve.py` (the closed-form anchor solve from one round's
  departure), `build-shadow.py`; W31 G3's `round.sh` (candidate documents into a scratch tree,
  four profiles rendered on the WebGPU tier, `--receded-profile`), `canonical-read.sh`,
  `configuration.py` and `configuration-log.json`, `append-check.py`, `read-append-check.py`,
  `departure-stat.py`, `seal.ts`, `x6-read.sh`, `digest-sites.md`; W30 G1's
  `split-generation.py`; W31 G4's `chain.sh` and `sheets.ts` (the per-cell document-bytes
  assertion). Every one is copied into this wave's directories rather than edited in place,
  on the rule that nothing under `results/` changes after commit.
- **The chain.** Units 2,662; goldens 34; gpu 48; platform-web 410; demo 59; React 172 / 3 / 2
  (driver-timing class, recorded).

## Design (advisory unless marked)

**What a joint fit is, here.** The exterior at one pixel is `bg · (1 − α(span, backdrop) · F(d))
+ lift`, with `F(d) = Φ((d − spread)/σ(span))` on the distance from the silhouette shifted down by
the offset. The three lengths shape `F`; the anchors scale it. A fit of σ alone against a fit of
Apple's σ — W30's — is right only if Apple's spread and offset equal vitrea's, which nobody
measured. The joint fit reads the rendered exterior's transmission per band per direction against
Apple's and moves the lengths until the two profiles agree in shape; the anchors then follow in
closed form, because at a fixed geometry the departure is linear in the composited alpha
(§5.159 §2). The direction resolution is what identifies the offset: `below` carries the
displacement and `above` carries almost none (§5.162 §4's table reads `above` at 0.00000 from
the `3-6` band outward at span 44), so a shift moves the two in opposite directions where a width
moves them together.

**Free and constrained, both measured (binding).** B1 is adopted and a wave does not fit a bound
off. But B1's right-hand side is the instrument's σ of Apple's render, which absorbs Apple's
outset, so a joint fit that lands the shape right could want a σ outside B1's window at a spread
below 3.1 — or could not; §5.162 §9 N-10 says the bed does not know. The wave therefore runs the
free fit as a MEASUREMENT and the constrained fit as the SHIPPED material: if they agree within
the bar, B1 was never in the way; if they disagree, the disagreement is the reading that decides
whether B1 should be re-stated over the rendered exterior, and that is a user's ruling for a
later wave, put with numbers.

**The stops (binding).** B3 ≤ 0.00035 as W31 held it; B1 at the shipped bytes; thin-span `T`
no worse than today plus the bar; the chroma, structure, tint and rim rows unmoved. Every stop is
read at every round on scratch, and the round that breaks one is recorded and not shipped.

**The span confound, decided before the fit (binding).** `T` weights the `24-48` band at 53 % and
a larger caster fills that band with more shadow, so one number across 96 / 128 / 160 is not one
promise. G0 computes three readings on the current generation — `T` as declared; `T` per span
with its own bound; and a depth-normalised form `T / Σ_b w_b (1 − a_native,b)` (the transmission
error as a fraction of the native shadow's own depth in the window) — and the parent rules at
G0's close which is the candidate row, with the other two recorded beside at the read. The
parent's prior: the depth-normalised form is the promise a reader can state in one sentence
("the falloff's error is under a tenth of the shadow's own depth") and is comparable across
spans; the declared `T` stays as G1 declared it so the before/after is on one statistic.

**The recede.** Apple's receded shadow is not the active shadow at a lower alpha; the inactive
`T` at span 160 is six to nine times the active and the far halo is three times. The receded
documents' anchors are solved on the inactive cells by the same linearity; whether the recede's
LENGTHS differ is read from the inactive direction-resolved cut and decided by the bar, so the
receded document carries a length only where the bed says the active one is wrong there.

**The fit's bed.** Calibration + validation + the ladder's rungs at 128 and 160, active and
inactive, WebGPU tier, six profiles rendered per round (the accessibility documents inherit the
light lengths under the fold that overwrites their anchors, as W30 recorded, and are read as a
check). The holdout is dropped by the reader's construction. Rounds are scratch renders under
`VITREA_WEB_CAPTURES` and `--out-matrix`, never the working file.

**What lands on the CSS tier.** Nothing new: the mirror already carries all three lengths, so the
fit reaches it through the documents. Its exterior is recorded per bed and span beside the
WebGPU tier's and stays unbounded (Decision Log 23, 2026-09-05).

**The `/laws/` stage.** One caster on a structured ground, a span control the page already
drives, the exterior's own numbers beside it (σ, spread, offset, the depth at three distances)
read from the shipped document at runtime, not transcribed. A design sketch goes to the user
before G2 implements it.

## Children

### G0: The direction-resolved cut and the declarations — no material change, no capture

Ledger **§5.166**; evidence `packages/calibration/results/2026-09-21-w32-g0-exterior-cut/`.
Copies W31 G1's reader into its own directory and extends it: `T` and `Δa` per direction; the
per-direction extents and offsets; the departure; the inactive rows read as their own population;
`--out`. The native-side model fit per cell with its conditioning and Apple's outset reading
(clause 1). The three forms of C1 tabled on the current generation (clause 2) and the parent's
ruling folded in as Decision Log 1 (c). `bounds-declaration.md`: the candidate row in
`adopted-thresholds.test.ts`'s idiom with `CONTRIBUTING_CELLS` counted from the bed and the B-1
guards; the stops with today's readings; the rows expected unmoved; the "reachable if" rows with
headroom. A test over a scratch matrix that the direction-resolved statistic reproduces §5.162
§4's printed `Δa` on the two cells it printed. The charter's Tracking Map row and a Revision Note.
Runs in parallel with G0b; owns nothing G0b touches.

### G0b: The evidence hygiene this wave's read depends on — parallel with G0

Ledger **§5.167**; evidence `packages/calibration/results/2026-09-21-w32-g0b-evidence-tools/`.
Three of W31's Deferred items 12 and 14, each a tool and not a number: **the capture-tree
checker** — walks the canonical `web-captures/`, reads each capture's document hashes, asserts
the generation matches the matrix's rows for that profile, skips cleanly where the tree is
absent, and is run in G1's read and at every later merge; **the holdout configuration log moved
to a cross-gate location** (`packages/calibration/results/holdout-configuration/` with
`configuration.py` and the log, the W31 G3 copies left byte-identical where they are and the new
location the one every later read records to — the tracker entry's fix shape); **`split-generation.py`'s
docstring made true** about the rule it enforces, with the two committed entries carrying the slip
annotated beside. Owns `results/holdout-configuration/`, the checker under `packages/calibration/
scripts/` or its evidence dir, and `results/2026-09-20-w30-g1-split/split-generation.py`'s
docstring only. No material change, no capture.

### G1: The joint fit, the recede, the seal and the read — one merge; opens after G0 and G0b are merged and reviewed

Ledger **§5.168**; evidence `packages/calibration/results/2026-09-21-w32-g1-shadow-fit/`. In
order, committing as it goes, merged whole:

1. **The pre-fit bed on scratch** at the shipped documents, reproduced against the committed rows
   within the repeat noise before any new reading (W31's rule), with the direction-resolved
   statistic and every stop read on it — the before.
2. **The rounds.** `round.sh` in W31 G3's shape: candidate documents into the scratch tree, six
   profiles on the WebGPU tier over calibration + validation + the ladder, active and inactive
   (`--receded-profile`), the machine read before each; the reader; the anchors re-solved in
   closed form from each round's departure; the free fit and the constrained fit both driven to
   convergence on the direction-resolved statistic and both recorded round by round. The stops at
   every round. The dark documents' own lengths where the bed says so.
3. **The recede's anchors** solved on the inactive cells (clause 4); its lengths decided by the
   bar.
4. **The seal**: the four documents re-sealed under rule 2 with history, the dark parenthetical
   corrected beside, every digest site moved (`digest-sites.md`'s list), `macos27-profile.ts`
   regenerated, `window-activation.spec.ts`'s hashes re-recorded with the reason, `tier-coherence`
   green (the mirror list already carries the three lengths — the exhaustiveness case says so),
   `w30-inert-laws` and the identity tests green, the 34 goldens byte-identical (the default does
   not move), the 1,107 gated-row pin, `freeze.py verify` 1,818.
5. **The read**: `configuration.py record` at the new location; `canonical-read.sh` at the sealed
   hashes; calibration + validation, the ladder, holdout once; the append-check; the split; the
   capture-tree checker; the 27 gated-cell count.
6. **The verdict**: C1 in its ruled form and in the other two forms; B1 at the shipped bytes; B3;
   the thin-span stop; the rows expected unmoved; the seven missed rows before and after; the
   recede's halo; the accessibility beds recorded; sheets (native | WebGPU | CSS | ×8, `rrect-lg`
   and `capsule-button`, both schemes, both scales, active and inactive) with `eye.md` naming the
   level contours present or absent; the adoption question put to the parent; Decision Log drafts
   where a ruling is needed (B1's re-statement if the free fit left its window). A changeset for
   the fixed group saying what a user of 0.22.0 gets.

### G2: The landing — 0.22.0 prepared

Ledger **§5.169**; evidence `packages/calibration/results/2026-09-21-w32-g2-landing/`. C1
adopted on the parent's decision with its cut re-run into this directory; `MISSED_27_ROWS` as G1
left it; the `/laws/` shadow stage on the design the user approved; `CLAUDE.md`'s Calibration and
material paragraphs; both READMEs and CHANGELOGs; the coverage matrix; the demo-beside-harness
sheets; the chain (W31 G4's `chain.sh` copied), RT/IC 0 and the slider 0.5 before every browser
run; `pnpm changeset version` to 0.22.0; the dry run; the Outcomes & Retrospective section against
all seven clauses; the Deferred-at-close list; the Tracking Map row.

## Cross-Child Contracts

- **X1 — the freeze, intact.** No macOS 26.5-keyed path, row, bound, floor or document changes;
  `freeze.py verify` 1,818 at every merge; the 34 goldens byte-identical throughout (no leaf is
  added, the default does not move); the 1,107 gated-row pin holds; the 26.5 digests stay the live
  pin under rule 2 with no exemption spent.
- **X2 — the cut precedes the fit.** G0's declarations are committed and reviewed before G1 opens;
  G1 fits against the statistic G0 declared and no other.
- **X3 — the fit moves the shadow and nothing else.** The three lengths, the σ law's leaves inside
  B1's window, the six occlusion anchors and `liftAmplitude` on the active documents; the same on
  the receded documents; nothing on the accessibility fold's amplitude; no structure, chroma,
  tone, tint, rim or scatter constant; no leaf added. A fit that moves a row outside the shadow
  axis is a warning, not a result.
- **X4 — bounds before reads; the stops are numbers; holdout once by artifact; a miss is
  recorded.** B1 is not re-stated in this wave whatever the free fit reads.
- **X5 — no native capture; the granted bundle is never rebuilt and nothing is added under its
  identifier.**
- **X6 — RT and IC 0, the slider 0.5, one capture process, ≥ 60 s idle** before every browser run,
  rounds included; every run recorded in `browser-runs.txt`.
- **X7 — the evidence layout changes by the one rule**: the split after the read that supersedes;
  the freeze's row hashes verify at every merge; no schema bump (the direction-resolved statistic
  needs no field a row does not carry; say so if that turns out false).
- **X8 — padding untouched.** The advisory constant does not move; the reach moves with the
  lengths and its numbers at every span are recorded in the tracker's entry.
- **X9 — no GPT-rung agents**; children and reviews are opus `general-purpose` (read-only for
  reviews); ledger sections as assigned; merges `--no-ff -F <file>` with the freeze verified at
  each; no attribution trailers, no session URLs; committed evidence never rewritten, corrections
  beside.
- **X10 — the 27 bed never empties between merges.** The four documents' bytes change only in G1's
  merge, which carries rows read at the new bytes; the gated-cell count pinned at every merge;
  `MATRIX_CELLS` / `PREDICATE_EXCLUDES` move only in the commit that carries the read.
- **X11 — file ownership.** G0 owns its evidence dir and `test/w32-*.test.ts`; G0b owns
  `results/holdout-configuration/`, the checker and the split script's docstring; neither touches
  `adopted-thresholds.test.ts`, a profile document or the matrix. The parent merges G0b then G0.

## Ordering & Dependency Map

Charter → adversarial review → fold → **G0 ∥ G0b** → merged G0b, G0, each reviewed → the parent's
ruling on C1's form (Decision Log 1 (c)) → **G1** (fit + recede + seal + read, one merge,
reviewed) → the parent's adoption decision and the user's ruling on the `/laws/` stage design →
**G2** → the user's eye on the sheets → `pnpm release` (the user) → tag. After this wave, in W31's
Deferred order: the surface-conditioned retention (a `scenes.json` decision first); the
accessibility documents' own values; the CSS chroma operator; the analysis pass; the thin regime's
instrument (W30 Deferred 4), which this wave's direction-resolved cut may or may not have made
readable.

## Risks & Mitigations

- **σ and spread do not separate on four bands.** G0 reports the conditioning before the fit; if
  the pair is degenerate the constrained fit holds σ at the law and fits spread and offset alone,
  which is still the reading B1 cannot see; the free fit's degeneracy is recorded as such.
- **The over-filled contour absorbs the spread.** Vitrea over-fills its declared silhouette by
  3.5–4 CSS px against Apple's ≤ 1 (§5.62); the `0-3` band is excluded from the statistic for that
  reason, so the fit cannot read the over-fill as spread; the band is tabled beside every reading
  and a fit that moves it is recorded.
- **The thick fit opens the thin regime.** The thin-span stop; and the knee held at 44 by
  construction.
- **The anchors' linearity fails under a moved geometry.** Two rounds per candidate as W30 G3 ran
  them; the second is the check and the secant where it disagrees.
- **The recede's inactive bed is thin above span 96.** Ladder rungs only at 128 and 160; the
  recede's anchors above 96 are fitted on the ladder and the holdout cells report beside; if the
  ladder cannot identify a length, the recede inherits it with the reading recorded.
- **The rounds cost more than the wave can afford.** Each round is one scratch capture of six
  profiles on one tier over ~120 cells; W31 G3 ran two; budget six, and a fit that has not
  converged by then ships the best constrained round with the trajectory recorded.
- **The re-seal empties the 27 bed.** X10.
- **The `/laws/` stage is taste.** A sketch to the user before implementation; the stage is the
  only part of the wave the user can strike without touching the material.

## Deferred / Out of Scope

The surface-conditioned retention; the accessibility documents' own retentions; the CSS chroma
operator; the analysis pass; the sweep phase's wrap; `prelude.ts`'s ceiling; the receded tinted
cells' chroma; `mid-chroma-solid`'s rotation and level; the retention under Increase Contrast
alone; the level stop as a third material row; the identifying sitting; the highlight's angular
reader; the decoupled increased-contrast read and `compare`'s flag; the motion-metrics harness;
the CSS tier over pure black; inactive calibration cells above span 96 as a `scenes.json` change
(this wave uses the ladder under the standing grant instead); `samplingPaddingFor`'s advisory
constant; the Reduced Transparency opacity policy; the slider's ends; the light bed's 16 px
structure; the `saturate()` constants; the thin regime's instrument; the receded contour's
hairline (tracker, a rim term and not a shadow one); `standard-row-identity-matrix.txt`'s
generator and the `interiorStdDevWeb` 5.69 % move (W31 Deferred 14, the halves not touched here).

## Tracking Map

| child | status |
| --- | --- |
| G0 | OPEN — dispatched at charter v2 |
| G0b | OPEN — dispatched at charter v2 |
| G1 | not opened |
| G2 | not opened |

## Decision Log

### Decision Log 1 — DRAFT 2026-09-21 by the parent; (a) and (b) ruled by the parent under the standing "rest on your judgement", (c) ruled at G0's close, (d) the user's

**(a) B1 and the joint fit — RULED by the parent: the constrained fit ships; the free fit is a
measurement.** The σ law's leaves may move only inside B1's joint windows at the shipped bytes,
`sigmaSpanRefPx` held at 96 and the knee at 44; the free fit is run to convergence beside it and
recorded round by round; if the two disagree beyond the bar, a Decision Log draft on re-stating B1
over the rendered exterior goes to the user for a later wave. Reason: an adopted bound is not
fitted off in the wave that finds it inconvenient, and the disagreement, if any, is the evidence
a re-statement would need.

**(b) The ladder's inactive rungs — RULED by the parent: granted to the recede's anchor solve, as
W30 Decision Log 2 (a) granted the active rungs to the σ law.** The inactive bed above span 96 is
otherwise holdout or nothing; the grant is the same grant for the same reason, the split is not
changed, and the holdout's inactive span-160 cells report beside as a check.

**(c) C1's adopted form — to be RULED by the parent at G0's close on G0's tables**, among `T` as
declared, per-span bounds, and the depth-normalised form. Prior stated in Design.

**(d) The `/laws/` shadow stage — the user's.** G2 puts a sketch before implementing; the user
may strike it without touching the material.

## Surprises & Discoveries

(none yet)

## Outcomes & Retrospective

(at close)

## Revision Notes

- 2026-09-21 (the parent): v1 chartered on main after the 0.21.0 publish record (`7a4ad3b4`),
  from W31's Deferred item 4, W30's items 8 and 10, and W31's items 12 and 14; sent to adversarial
  review before any child opens.
