# W32 — the shadow wave: the exterior vitrea draws, fitted as a whole rather than as a blur

**Status: OPEN 2026-09-21 — chartered by the parent on the user's "W32 Shadow wave will be it"
after the 0.21.0 publish, under the standing "rest on your judgement"; adversarially reviewed the
same day and the review folded (v2, Revision Notes).** Executes W31's Deferred-at-close item 4
(the next shadow wave carrying C1 and the joint fit of the shadow's three lengths), W30's Deferred
items 8 (the recede's exterior above span 96) and 10 (a shadow section for `/laws/`), and W31's
Deferred items 12 and 14 where they touch the evidence this wave reads. Grounded on main at
`7a4ad3b4` (0.21.0 published; tag `v0.21.0`).

## Purpose

The outer shadow is the largest single facet the project has measured, and after two waves on it
the shadow vitrea draws is still not Apple's. W30 made its blur a function of the casting span and
the adopted row B1 says the law's σ is inside ±5 % of the native's fitted σ at every thick span on
every bed. W31 G1 then put a second instrument beside B1 and found that **a green B1 and a wide
exterior are consistent**: B1 compares the DOCUMENT's blur leaf in closed form to a FIT of Apple's
render, and that fit absorbs whatever else Apple's shadow is besides a blur. The same instrument
applied to both renders reads vitrea's exterior **+2.66 to +3.77 CSS px wider than Apple's at
every thick span on every standard bed, on the WebGPU tier** — additive, not proportional — and
the shadow's other two lengths, `spreadPx` 3.10 and `offsetPx` 7.95, are inherited from the macOS
26.5 default, byte-identical in every document that carries them, absent from both dark
documents, and **have never been fitted on the macOS 27 bed** (claims §5.162 §2). Nothing in the
repository pins either leaf at the shipped documents (Grounding).

The per-band transmission error says the same thing from inside the falloff, and it says it at
every span. At span 160 on the 1x light bed the median `Δa` (web − native, direction `all`) reads
**−0.0077 / −0.0078 / −0.0100 / −0.0069** across the bands 3-6 / 6-12 / 12-24 / 24-48 CSS px:
negative at every band, with no agreement radius inside the window. And at the THIN spans, where
the eye called the exterior right because the difference is confined to the body (§5.160 §6), the
inner two bands read **−0.0175 / −0.0123** at span 32 and **−0.0187 / −0.0149** at span 44 —
larger per band than the thick spans' — with the outer two bands at exactly zero on both sides
because no shadow reaches them. W31 G1's one-number `T` diluted that by weighting the empty bands
at 36 of 45, which is why it read the thin regime as "right"; the per-band reading does not. At a
thin span the instrument is mostly reading the displacement (§5.162 §2), which is to say `offsetPx`
and `spreadPx` — the two leaves this wave exists to fit. The shape statistic G1 declared for this
wave, C1, **fails today at span 128 on all four standard beds and at span 160 on all four**
(0.00487–0.00532 and 0.00733–0.00921 against ≤ 0.0045) and passes at 96.

**And the bed cannot see a span-160 exterior.** The canvas is 320 × 200 and `rrect-lg` is 280 ×
160, so every span-160 cell has **19.5 CSS px of clearance on every side**: the `24-48` band —
53 % of `T`'s weight — survives only in the capture's four corners (532 px above and below, 242
left and right, against 10,181 and 9,578 at span 128), and the web side's `extentBelowWeb` and
`offsetYWeb` are absent on all 100 span-160 rows because the shadow walks off the frame. The
axis's own doc comment (`shadow.ts`, `truncatedSides`) puts the σ bias of a σ ≈ 17 px shadow read
through a 20 px margin at roughly 8 % low — larger than B1's whole window — and `scenes.json`'s
own `rrect-ml` comment says span 128 is the largest this canvas carries with the reference's
shadow substantially intact. Found by this charter's review (Surprises); no wave had written it
down beside the span-160 readings it qualifies.

The purpose of this wave is therefore to fit the exterior vitrea draws — `spreadPx`, `offsetPx`,
and the σ law inside B1's window, together with the amplitude anchors that ride the same falloff —
against an instrument that reads the RENDERED exterior per band and per direction, on the spans
the bed can see (32, 44, 96, 128), with span 160 read inside its clearance and reported; to give
the receded documents an exterior of their own on the inactive fixtures the bed already holds and
has never read on the web side; to read C1 on the result in the span-aware form the confound
admits and adopt it if met; and to make the operator legible on the site.

What this wave does not do is as fixed as what it does. No structure, chroma, tone or tint
constant moves (X3). No native capture is taken (X5); the canvas does not change. The macOS 26.5
documents' bytes do not change and their digests stay the live pin under rule 2 (X1). No adopted
bound is re-stated (X4). Every stop is a number on a named population with a named bar.

## Parent-Level Acceptance

1. **The exterior is cut per direction and per band inside each cell's clearance before any
   length moves, and the cut says which lengths the bed can identify.** G0 copies W31 G1's reader
   into this wave's own evidence directory and extends it: per-band `Δa` and `Δc` resolved by
   DIRECTION (`all`, `above`, `below`, `left`, `right`); **bands admitted per cell only where the
   band's outer edge lies inside that cell's clearance in that direction** (the row's own
   `clearance{Above,Below,Left,Right}` divided by the scale), with bands-used reported beside every
   figure and every order statistic taken over cells carrying the same band set; the per-direction
   extents and fitted offsets both sides where the row carries them and the count where it does
   not; candidate (i), the rendered σ against the native σ (§5.162 §2's table, re-derived); the
   departure; the inactive rows as their own population. G0 tables **clearance against reach per
   span** and states, with the axis's own 8 % figure, which spans the exterior is fittable on;
   `scenes.json`'s `rrect-ml` declaration ("must not be used to fit a shadow constant") is retired
   or upheld BESIDE it from the matrix's own reading (the truncation guard's fields at span 128,
   clearance 35.5 against the reach), never walked past. From the NATIVE per-band per-direction
   slopes G0 fits the renderer's own falloff model per cell over the admitted bands and reports the
   (σ, spread, offset) triple with its conditioning, on the native and on the web side (the web
   fit should return the shipped triple; the size of its miss is the model's own error and is
   recorded before any native-side prior is trusted), and **what Apple's own outset reads** —
   §5.162 §9 N-10's open question. `above` reads exactly 0.00000 on every band on both `Δa` and
   `Δc` at span 44 (the reader's §4): the offset is identified ONE-SIDEDLY there, which G0 states
   as the condition the fit works under. Nothing is captured.
2. **Bounds before reads; every form is a number derived by a rule stated here; the stops are
   per cell where the bar is per cell.** G0 tables three forms of C1 on the current generation,
   each restricted to the admitted bands: **(i)** `T` as W31 G1 declared it, ≤ 0.0045; **(ii)**
   per-span `T`, three numbers; **(iii)** the σ-NORMALISED window §5.162 §9 N-9 named — bands at
   fixed multiples of the row's native σ, so every span is read at the same number of falloff
   lengths — with the band set that the clearance admits at each span. **The bound rule for (ii)
   and (iii) is declared now, before the tables: the bound at every span is the worst standard
   bed's span-96 order statistic of that form on the current generation, rounded up to two
   significant figures** — the promise "no worse at any span than at span 96 today", which is
   C1's own justification (§5.162 §3) applied form by form, so the tables cannot choose the number
   and the parent chooses only the form (Decision Log 1 (c)). The depth-normalised form the v1
   charter proposed is withdrawn on measurement (Surprises). The stops, each with today's reading
   in G0's declaration: **B1 at the shipped bytes** (the σ law's closed form inside every served
   bed's ±5 % window; the σ leaves move only inside it, Decision Log 1 (a)); **candidate (i)**, the
   rendered σ against the native σ on the WebGPU tier at spans 96 and 128 — **the wave's headline
   number, read at the verdict** — declared as a one-wave reading with the bound "inside B1's own
   ±5 % window of the native σ", which is the sentence W31 G1 found false; **B3's departure
   residual** ≤ 0.00035 on the WebGPU tier as W31 held it, over the whole exterior as defined;
   **the thin regime, per cell**: on every active non-holdout WebGPU cell at spans 32 and 44, the
   inner bands' |`Δa`| (3-6 and 6-12, the only bands the shadow reaches there) no worse than
   today's by more than **0.002044** — the native-pair `shadowAffineSlopeDeltaMax` MAX over 432
   cells in `results/2026-09-19-w29-g3b-shadow-recede/noise-bar.json` — with the order statistic
   over the same cells no worse than today's; **the chroma rows M1 and M2, the structure, tint and
   rim rows expected unmoved**, read before and after. The seven `MISSED_27_ROWS` rows are
   decomposed for what the shadow can reach and declared "reachable if" with the headroom from
   `T_dir` and the extents, or "not through the shadow"; nothing is CLAIMED through this wave but
   its own clauses.
3. **The joint fit, on the fidelity target, on the spans the bed can see, with the free reading
   and the shipped reading both recorded.** G1 fits `spreadPx` and `offsetPx` per scheme — and
   `sigmaPx` / `sigmaSlopePerSpan` inside B1's joint windows with `sigmaSpanRefPx` held at 96 and
   the knee held at 44 by re-deriving `sigmaThinOffsetPx` (W30 Decision Log 2 (b), 3 (c)) — on
   rendered rounds over the calibration and validation cells at spans 32, 44, 96 and 128 plus the
   ladder's rungs at 128 (granted as W30 Decision Log 3 (d) granted it), WebGPU tier, six profiles,
   against the direction-resolved per-band statistic over the admitted bands, checked on
   validation; span 160 rendered every round and READ inside its clearance, never fitted on. **The
   six occlusion anchors and `liftAmplitude` are re-solved in closed form per round from the
   departure restricted to the same 3–48 px window** (the `0-3` band excluded, because at span 160
   it reads `Δa` +0.090 to +0.157 — the contour over-fill, §5.62 — an order of magnitude above the
   shadow bands and of the opposite sign; W30 G3 solved on the whole exterior, and the difference
   between the two solves is measured and recorded at the first round), with B3 read over the
   whole exterior as the stop. **Two fits are run and both are recorded round by round: the free
   fit, in which the σ law is unconstrained, and the constrained fit, in which it stays inside
   B1's window; the constrained fit ships.** What "constrained" constrains is stated plainly: B1
   pins the σ law's closed form and nothing pins `spreadPx` or `offsetPx` today, so the lengths are
   bounded in this wave only by the declared candidate (i) and C1 readings at the verdict, and the
   free fit's distance from the constrained one is the evidence a later re-statement of B1 would
   need (Decision Log 1 (a)). Convergence: the admitted-band objective and every anchor ratio move
   by less than the bar between two successive rounds at the same candidate; budget **ten rounds**
   (W30 G3 needed three per geometry with σ alone moving, §5.159 §2); if the trajectory has not
   converged, the shipped material is the constrained round with the smallest objective among
   those meeting every stop, and the trajectory is recorded as not converged. The dark documents
   carry their own `spreadPx` and `offsetPx` if the dark bed's reading differs from the light one's
   beyond the bar, and inherit them explicitly recorded if not. The CSS tier's `box-shadow`
   follows the same leaves through the mirror `tier-coherence` pins; its rendered width is
   recorded, not bounded (§5.162 §9 N-11).
4. **The recede gets an exterior of its own, on the fixtures the bed already holds.** The matrix
   carries no inactive row at span 128 and three inactive non-holdout cells per standard bed at
   span 160 — yet the 27 fixture directories hold native captures of **nine probe inactive scenes
   the web side has never been read for**: `checkerboard`, `impulse`, `light-solid`, `photo` on
   `rrect-ml` (span 128) and `impulse`, `dark-solid`, `mid-dark-solid`, `light-solid`, `hc-text`,
   `mid-chroma-solid` on `rrect-lg` (span 160) beside the three checkerboard rungs already read
   (`mid-light-solid` on both has no fixture and is not read). **Decision Log 1 (b): the ladder
   list this wave's reads name is widened to those scenes** — a read-set decision, not a
   `scenes.json` change; the split does not move; the holdout is not touched. The receded
   documents' six anchors and lift are solved on the inactive cells: calibration and validation
   at 44 and 96, the probe rungs at 128 (three cells with a shadow to read — `impulse` has none)
   and 160 (seven, read inside the clearance), the holdout's inactive cells reported beside. The
   lengths stay the active document's unless the inactive direction-resolved reading says
   otherwise beyond the bar, in which case the receded document carries its own and the reading
   is recorded. The far-exterior halo on `checkerboard__rrect-lg__inactive` (17.42 / 15.89 against
   ≤ 5.92 active, tracker) is read before and after on the sheets.
5. **Re-seal and read in one merge, once per frozen configuration by artifact.** The four macOS 27
   documents re-sealed under rule 2 with history (the two dark documents' wrong
   `$comment-sha-history` parenthetical corrected BESIDE in the same re-seal, W31 Deferred 14);
   `configuration.py record` before the holdout with its output in the ledger, from the
   cross-gate location G0b gives it; the canonical run appended beside the 0.21.0 rows — six
   profiles, two tiers, calibration + validation, the widened ladder — then holdout **once**; the
   append-check; the split; the read's capture tree copied to the canonical `web-captures/` at
   merge and G0b's checker run against it; `freeze.py verify` 1,818 and the 27 gated-cell count
   (230 / 726, or what the machine says with the difference explained — the widened ladder adds
   probe rows, never gated cells) pinned at every merge (X10). The verdict per profile per tier
   per clause with every missed cell named; a miss recorded, not widened, not re-fitted.
6. **The landing.** C1 in its ruled form adopted into `adopted-thresholds.test.ts` on the parent's
   decision, reading a cut RE-RUN into the adopting gate's own directory with the `atDocuments`
   and `withHoldout` guards (§5.162 §9 B-1), the admitted-band rule in the case, and
   `CONTRIBUTING_CELLS` counted from the bed; candidate (i) before and after per bed and span in
   the record; sheets native | WebGPU | CSS | ×8 for `rrect-lg`, `rrect-ml` and `capsule-button`
   in both schemes at both scales, active and inactive, looked at, with the level contours named
   present or absent; a shadow stage on `/laws/` (W30 Deferred 10; the design put to the user at
   G2's dispatch, Decision Log 1 (d); a sixth stage moves the demo suite's count and needs its own
   pin beside `laws.spec.ts`'s existing `body-shadow-sigma` case); `CLAUDE.md`, both READMEs and
   the CHANGELOG saying what moved; the coverage matrix re-scored where a row moved; the fixed
   group versioned **0.22.0** and prepared, `pnpm release` the user's hand, the tag after.
7. **Every gap left is written down where it belongs**, with the evidence and the shape of the
   work: the wave's Deferred-at-close list in W31's shape, the tracker, the ledger. The span-160
   truncation is the first entry, with the canvas change that would close it named as a
   `scenes.json` decision and a native re-capture.

## Grounding Baseline (main at `7a4ad3b4`, 0.21.0 published)

- **The material.** `MaterialOuterShadow` (`packages/renderer-webgpu/src/material.ts`): the
  lengths `offsetPx` 7.95, `sigmaPx` 15.55, `spreadPx` 3.1 in the macOS 26.5 default; the σ law's
  three leaves at 0 there. The macOS 27 light document carries `offsetPx` 7.95, `spreadPx` 3.1,
  `sigmaPx` 8.96, slope 0.1314, ref 96, thin offset −6.8328; the dark document carries `sigmaPx`
  9.04, slope 0.1340, ref 96, thin offset −6.968 and **no `offsetPx` or `spreadPx`** (inherited
  from the default). Both receded documents carry their active document's anchors leaf for leaf
  (light 0.1158 / 0.1827 / 0.26, dark 0.133 / 0.2263 / 0.3409) and no length of their own.
  Shipped digests 3dc24a74f17fd87e / 8a43f54162606db4 / ab3ed65aa02869b1 / e1f42c5656ef392f.
- **What pins the lengths today: nothing.** B1 bounds `outerShadowSigmaPx`'s output only.
  `tier-coherence.test.ts` mirrors `spreadPx` and `offsetPx` against `DEFAULT_MATERIAL_PROFILE`,
  which does not move; `css-tier.test.ts` derives from the leaf rather than a literal; the 34
  goldens render the renderer defaults with no document seam, so they stay byte-identical when a
  document moves; `w30-inert-laws.test.ts` asserts the reach's monotonicity only. A fit can move
  both leaves at the shipped documents with every existing test green — which is why clause 2
  declares candidate (i) and C1 as the readings that bound them.
- **The shader** (`src/wgsl/optics.ts`, `outer_shadow`): the falloff is `Φ((d − spread)/σ)` on the
  field texture's signed distance read at the position shifted by the offset, σ per pixel from the
  casting span (`outer_shadow_sigma`), the amplitude the blend of the thin regime and the thick
  anchors on the size curve, composited multiplicatively; the lift on the same falloff. The
  displacement's clamped-off distance is added back (exact on a straight edge, errs toward less
  shadow past corners). Spread and σ are separate parameters of the render.
- **The CSS mirror** (`platform-web/src/css-tier.ts` ~line 2341): one `box-shadow` per surface —
  `0 offsetPx blur(2σ(span)) spreadPx rgba(0,0,0,α)` — from the same leaves; `outerShadowReachPx`
  bisects the falloff for the group clip and the scissor pad, so the reach moves with every length
  (X8: `samplingPaddingFor` is the backdrop blur's 3σ and does not).
- **The instrument.** `packages/calibration/src/metrics/shadow.ts`: per cell, per direction and
  `all`, six bands 0-3 / 0-6 / 3-6 / 6-12 / 12-24 / 24-48 CSS px outside the declared contour
  (`SHADOW_AFFINE_BANDS_CSS_PX`; 6 × 5 = the 30 entries of `affineNative` / `affineWeb`), the
  affine pair `(a, c)` in linear light on both sides; the blurred-edge fit `falloffSigma{Native,
  Web}` with its residual; extents and offsets per direction (absent where the shadow leaves the
  frame); `clearance{Above,Below,Left,Right}` in device px on every row; `meanDeparture{Native,
  Web}` over the whole exterior; `backdropSupport` with the axis's floor 0.1. `truncatedSides` is
  computed and NOT written to a row (X7 note). W31 G1's reader
  `results/2026-09-21-w31-g1-exterior-instrument/exterior-instrument.py` computes candidate (i)
  and `T` (`--out`, `--with-holdout`, `--at-documents`, `--against`), renormalising `T` per cell
  over the bands it finds usable (line ~400) — which is why clause 1 fixes the band set per span
  before pooling; its committed `exterior-instrument.txt` §4 prints `Δa` / `Δc` per band per
  direction for two cells. The native-pair noise bar is
  **`results/2026-09-19-w29-g3b-shadow-recede/noise-bar.json`** (not the G2 file):
  `shadowAffineSlopeDeltaMax` p95 0.000229, max 0.002044, over 432 cells of seven runs.
- **The bed** (`apps/reference-apple/scenes.json`, 168 scenes, canvas 320 × 200). Active, by span:
  32 `rrect-sm` (1 cal + 1 val + 12 probe); 44 `capsule-button` (11 cal + 2 val + 4 holdout + 11
  probe) and `toolbar-group` (1 + 1); 96 `rrect-md` (4 cal + 2 val + 1 holdout + 9 probe); 128
  `rrect-ml` (3 cal + 7 probe); 130 `glass-over-glass` (2 holdout); 160 `rrect-lg` (3 holdout + 13
  probe). Inactive: 44 `capsule-button` 11 cal + 2 val + 4 holdout + 4 probe; 96 `rrect-md` 4 + 2 +
  1 + 8; 128 `rrect-ml` 5 probe (four with fixtures, **none read on the web side**); 160 `rrect-lg`
  3 holdout + 10 probe (nine with fixtures, three read). Clearance per span (CSS px, 1x): 32 →
  84 / 68; 44 → 78 / 100; 96 → 52 / 80; 128 → 36 / 48; **160 → 19.5 all round**. The ladder the
  reads name today is 45 scenes (`canonical-read.sh`'s `LADDER`); the 27 bed at the shipped
  documents: 230 gated cells / 726 rows, 124 holdout; `freeze.py verify` 1,818.
- **The fit's bed, counted.** WebGPU tier, non-holdout, per round: the six profiles' committed row
  counts over calibration + validation + the 45-scene ladder are 94 / 94 / 66 / 66 / 12 / 14 =
  **346 cells**, active and inactive together; the widened ladder adds up to 10 scenes × 4
  standard profiles. Each round is one scratch capture of that bed.
- **The rows.** B1 adopted (reading W30 G0's `shadow-cut.json`); C1 declared and not adopted
  (`bounds-declaration.md` §3 in G1's directory, with the B-1 condition); `MISSED_27_ROWS` at 5 +
  3; M1 and M2 adopted on the chroma at W31 G4. The current generation's `T` per bed per span
  (§5.162 §1) and the per-band medians in Purpose are the before-readings.
- **The tooling this wave inherits.** W30 G3's `shadow-law.py` (`--at-shipped`), `anchor-solve.py`,
  `build-shadow.py`; W31 G3's `round.sh`, `canonical-read.sh`, `configuration.py` and its log,
  `append-check.py`, `read-append-check.py`, `departure-stat.py`, `seal.ts`, `x6-read.sh`,
  `digest-sites.md`; W30 G1's `split-generation.py`; W31 G4's `chain.sh` and `sheets.ts`. Every
  one is copied into this wave's directories rather than edited in place.
- **The demo.** `apps/demo/src/laws/Laws.tsx` has five stages; the σ readout lives inside the body
  stage (`body-shadow-sigma`), pinned by `apps/demo/e2e/laws.spec.ts` against the `box-shadow` the
  tier writes at both span ends.
- **The chain.** Units 2,662; goldens 34; gpu 48; platform-web 410; demo 59; React 172 / 3 / 2
  (driver-timing class, recorded).

## Design (advisory unless marked)

**What a joint fit is, here.** The exterior at one pixel is `bg · (1 − α(span, backdrop) · F(d))
+ lift`, with `F(d) = Φ((d − spread)/σ(span))` on the distance from the silhouette shifted down by
the offset. The three lengths shape `F`; the anchors scale it. A fit of σ alone against a fit of
Apple's σ — W30's — is right only if Apple's spread and offset equal vitrea's, which nobody
measured. The joint fit reads the rendered exterior's transmission per band per direction against
Apple's and moves the lengths until the two profiles agree; the anchors then follow in closed
form, because at a fixed geometry the departure is linear in the composited alpha (§5.159 §2) —
and since the lengths move the geometry, the linearity is re-checked at every round rather than
assumed (Risks). The direction resolution is what identifies the offset: `below` carries the
displacement and `above` carries none at span 44 — exactly 0.00000 on every band on both sides —
so a shift moves the two in opposite directions where a width moves them together, and at the
thin spans, where the shadow is mostly displacement, that is most of what the instrument reads.

**Which spans fit and which are read (binding).** Spans 32, 44, 96 and 128 fit. Span 160 is read
inside its 19.5 px clearance — the bands 3-6, 6-12 and 12-24 — and reported at every round and at
the verdict, never fitted on, because a fit that prefers the triple that fits inside a 20 px frame
is a fit of the frame. The σ leaf's value at span 160 is B1's (the closed form on the native σ),
not the exterior's; that is the one place this wave leaves the law's σ standing on W30's
instrument alone, and it says so.

**Free and constrained, both measured (binding).** B1 is adopted and a wave does not fit a bound
off. But B1's right-hand side is the instrument's σ of Apple's render, which absorbs Apple's
outset, so a joint fit that lands the shape right could want a σ outside B1's window at a spread
below 3.1 — or could not; §5.162 §9 N-10 says the bed does not know. The wave therefore runs the
free fit as a MEASUREMENT and the constrained fit as the SHIPPED material. What B1 does not
constrain — the two lengths — is bounded at the verdict by candidate (i) and by C1, both declared
with numbers by G0 before a round is rendered.

**The stops (binding).** B3 ≤ 0.00035 over the whole exterior; B1 at the shipped bytes; candidate
(i) inside B1's window at 96 and 128; the thin regime per cell on the inner bands against the max
bar 0.002044; the chroma, structure, tint and rim rows unmoved. Read at every round on scratch;
the round that breaks one is recorded and not shipped.

**The span confound, decided before the fit (binding).** `T` weights the `24-48` band at 53 % and
a larger caster fills that band with more shadow, so one number across spans is not one promise;
at span 160 that band is corner-only in any case. Three forms are tabled by G0 over the admitted
bands and the bound of each non-declared form is fixed by the rule in clause 2 — the worst
standard bed's span-96 value today, rounded up — so the parent's ruling at G0's close (Decision Log
1 (c)) chooses a form and cannot choose a number. The parent's prior is withdrawn: the v1
charter's depth-normalised form reads 3.44 / 3.37 / 0.72 / 0.31 / 0.20 across spans 32 → 160 on
1x light, inverts the thin/thick reading, and had no bound; it is not a candidate.

**The recede.** Apple's receded shadow is not the active shadow at a lower alpha; the inactive
`T` at span 160 is six to nine times the active and the far halo is three times. The receded
documents' anchors are solved on the inactive cells by the same linearity; whether the recede's
LENGTHS differ is read from the inactive direction-resolved cut and decided by the bar, so the
receded document carries a length only where the bed says the active one is wrong there.

**The fit's bed.** Calibration + validation + the widened ladder, active and inactive, WebGPU
tier, six profiles rendered per round (the accessibility documents inherit the light lengths
under the fold that overwrites their anchors, as W30 recorded, and are read as a check). The
holdout is dropped by the reader's construction. Rounds are scratch renders under
`VITREA_WEB_CAPTURES` and `--out-matrix`, never the working file.

**What lands on the CSS tier.** Nothing new: the mirror already carries all three lengths, so the
fit reaches it through the documents. Its exterior is recorded per bed and span beside the WebGPU
tier's and stays unbounded (Decision Log 23, 2026-09-05).

**The `/laws/` stage.** One caster on a structured ground, a span control the page already
drives, the exterior's own numbers beside it (σ, spread, offset, the depth at three distances)
read from the shipped document at runtime, not transcribed. A design sketch goes to the user
before G2 implements it.

## Children

### G0: The direction-resolved cut and the declarations — no material change, no capture

Ledger **§5.166**; evidence `packages/calibration/results/2026-09-21-w32-g0-exterior-cut/`.
Copies W31 G1's reader into its own directory and extends it per clause 1: direction resolution;
the admitted-band rule from each row's clearance with bands-used beside every figure; extents and
offsets with their absence counted; candidate (i); the inactive rows as their own population;
`--out`. The clearance-against-reach table and the `rrect-ml` declaration's fate beside it in
`scenes.json` (a `$comment` beside, never a rewrite). The native-side and web-side model fits with
conditioning and Apple's outset. The three forms of C1 over the admitted bands with their bounds
by the declared rule (clause 2) and a one-paragraph recommendation; the parent rules and folds the
ruling as Decision Log 1 (c). `bounds-declaration.md`: the candidate row in
`adopted-thresholds.test.ts`'s idiom with the admitted-band rule, `CONTRIBUTING_CELLS` counted
from the bed per pose, and the B-1 guards; the stops with today's readings (B1's joint windows via
`shadow-law.py --at-shipped`; candidate (i) per bed and span; B3 via `departure-stat.py` and the
window-restricted departure beside it; the thin-regime per-cell values; M1/M2 and the
expected-unmoved rows); the seven missed rows decomposed; the recede's declared reading and what
its anchor solve is judged on. A vitest case over a scratch matrix that the direction-resolved
statistic reproduces the `Δa` lines G1's committed `exterior-instrument.txt` §4 prints, plus the
holdout-drop and shipped-documents refusals. The charter's Tracking Map row and a Revision Note.
Runs in parallel with G0b; owns nothing G0b touches.

### G0b: The evidence hygiene this wave's read depends on — parallel with G0

Ledger **§5.167**; evidence `packages/calibration/results/2026-09-21-w32-g0b-evidence-tools/`.
Three of W31's Deferred items 12 and 14, each a tool and not a number: **the capture-tree
checker** — walks the canonical `web-captures/`, reads each capture's document hashes, asserts
the generation matches the matrix's rows for that profile, skips cleanly where the tree is
absent, reports a frozen profile's known-different generation distinctly from a live mismatch,
and is run in G1's read and at every later merge; **the holdout configuration artifact at a
cross-gate location** (`packages/calibration/results/holdout-configuration/` with
`configuration.py` and the log seeded from W31 G3's, the G3 copies left byte-identical, the new
location the one every later read records to — the tracker entry's fix shape; the enumerated
source list re-checked against what affects the render today); **`split-generation.py`'s
docstring made true** about the rule it enforces, with the two committed entries carrying the slip
annotated beside. Owns `results/holdout-configuration/`, the checker under `packages/calibration/
scripts/` or its evidence dir, and `results/2026-09-20-w30-g1-split/split-generation.py`'s
docstring only. No material change, no capture.

### G1: The joint fit, the recede, the seal and the read — one merge; opens after G0 and G0b are merged and reviewed

Ledger **§5.168**; evidence `packages/calibration/results/2026-09-21-w32-g1-shadow-fit/`. In
order, committing as it goes, merged whole:

1. **The pre-fit bed on scratch** at the shipped documents over the fit's bed including the
   widened ladder, reproduced against the committed rows within the repeat noise where rows exist
   (W31's rule) — the nine never-read inactive scenes have no committed row and are read for the
   first time here, as scratch, and said so — with the direction-resolved statistic and every stop
   read on it: the before. The window-restricted departure beside the whole-exterior one on this
   bed, so the anchor solve's change of objective is measured before it is used.
2. **The rounds.** `round.sh` in W31 G3's shape: candidate documents into the scratch tree, six
   profiles on the WebGPU tier over the fit's bed, active and inactive (`--receded-profile`), the
   machine read before each; the reader over the admitted bands; the anchors re-solved in closed
   form from each round's window-restricted departure; the free fit and the constrained fit both
   driven under the convergence test of clause 3 and both recorded round by round with the
   linearity check (the ratio a second round at the same candidate returns); span 160 read every
   round. The stops at every round. The dark documents' own lengths where the bed says so.
3. **The recede's anchors** solved on the inactive cells (clause 4); its lengths decided by the
   bar.
4. **The seal**: the four documents re-sealed under rule 2 with history, the dark parenthetical
   corrected beside, every digest site moved (`digest-sites.md`'s list), `macos27-profile.ts`
   regenerated, `window-activation.spec.ts`'s hashes re-recorded with the reason, `tier-coherence`
   green (the exhaustiveness case already covers the three lengths), `w30-inert-laws` and the
   identity tests green, the 34 goldens byte-identical (the default does not move), the 1,107
   gated-row pin, `freeze.py verify` 1,818.
5. **The read**: `configuration.py record` at the new location; `canonical-read.sh` at the sealed
   hashes with the widened `LADDER`; calibration + validation, the ladder, holdout once; the
   append-check; the split; G0b's checker; the 27 gated-cell count.
6. **The verdict**: C1 in its ruled form and in the other two; candidate (i) before and after per
   bed and span; B1 at the shipped bytes; B3; the thin-regime per-cell stop; the rows expected
   unmoved; the seven missed rows before and after; span 160 inside its clearance; the recede's
   halo; the accessibility beds recorded; sheets (native | WebGPU | CSS | ×8, `rrect-lg`,
   `rrect-ml` and `capsule-button`, both schemes, both scales, active and inactive) with `eye.md`
   naming the level contours present or absent; the adoption question put to the parent; Decision
   Log drafts where a ruling is needed (B1's re-statement if the free fit left its window). A
   changeset for the fixed group saying what a user of 0.22.0 gets.

### G2: The landing — 0.22.0 prepared

Ledger **§5.169**; evidence `packages/calibration/results/2026-09-21-w32-g2-landing/`. C1
adopted on the parent's decision with its cut re-run into this directory; `MISSED_27_ROWS` as G1
left it; the `/laws/` shadow stage on the design the user approved, with its own e2e pin;
`CLAUDE.md`'s Calibration and material paragraphs; both READMEs and CHANGELOGs; the coverage
matrix; the demo-beside-harness sheets; the chain (W31 G4's `chain.sh` copied), RT/IC 0 and the
slider 0.5 before every browser run; `pnpm changeset version` to 0.22.0; the dry run; the
Outcomes & Retrospective section against all seven clauses; the Deferred-at-close list; the
Tracking Map row.

## Cross-Child Contracts

- **X1 — the freeze, intact.** No macOS 26.5-keyed path, row, bound, floor or document changes;
  `freeze.py verify` 1,818 at every merge; the 34 goldens byte-identical throughout (no leaf is
  added, the default does not move); the 1,107 gated-row pin holds; the 26.5 digests stay the live
  pin under rule 2 with no exemption spent.
- **X2 — the cut precedes the fit.** G0's declarations are committed and reviewed before G1 opens;
  G1 fits against the statistic and the band rule G0 declared and no other.
- **X3 — the fit moves the shadow and nothing else.** The three lengths, the σ law's leaves inside
  B1's window, the six occlusion anchors and `liftAmplitude` on the active documents; the same on
  the receded documents; nothing on the accessibility fold's amplitude; no structure, chroma,
  tone, tint, rim or scatter constant; no leaf added. A fit that moves a row outside the shadow
  axis is a warning, not a result.
- **X4 — bounds before reads; every bound and stop is a number by a stated rule; holdout once by
  artifact; a miss is recorded.** B1 is not re-stated in this wave whatever the free fit reads;
  the form of C1 is chosen from a set whose bounds were fixed by rule before the tables.
- **X5 — no native capture; the canvas does not change; the granted bundle is never rebuilt and
  nothing is added under its identifier.** The nine inactive scenes this wave reads are read from
  fixtures already on disk.
- **X6 — RT and IC 0, the slider 0.5, one capture process, ≥ 60 s idle** before every browser run,
  rounds included; every run recorded in `browser-runs.txt`.
- **X7 — the evidence layout changes by the one rule**: the split after the read that supersedes;
  the freeze's row hashes verify at every merge; no schema bump. The band rule reads
  `clearance*`, which every row carries; `truncatedSides` is not on a row and is not needed.
- **X8 — padding untouched.** `samplingPaddingFor`'s advisory constant does not move; the reach
  moves with the lengths and its numbers at every span are recorded in the tracker's entry.
- **X9 — no GPT-rung agents**; children and reviews are opus `general-purpose` (read-only for
  reviews); ledger sections as assigned; merges `--no-ff -F <file>` with the freeze verified at
  each; no attribution trailers, no session URLs; committed evidence never rewritten, corrections
  beside.
- **X10 — the 27 bed never empties between merges.** The four documents' bytes change only in G1's
  merge, which carries rows read at the new bytes; the gated-cell count pinned at every merge;
  `MATRIX_CELLS` / `PREDICATE_EXCLUDES` move only in the commit that carries the read.
- **X11 — file ownership.** G0 owns its evidence dir, `test/w32-*.test.ts` and the one `$comment`
  beside `rrect-ml` in `scenes.json`; G0b owns `results/holdout-configuration/`, the checker and
  the split script's docstring; neither touches `adopted-thresholds.test.ts`, a profile document
  or the matrix. The parent merges G0b then G0.

## Ordering & Dependency Map

Charter → adversarial review → fold (done) → **G0 ∥ G0b** → merged G0b, G0, each reviewed → the
parent's ruling on C1's form (Decision Log 1 (c)) → **G1** (fit + recede + seal + read, one
merge, reviewed) → the parent's adoption decision and the user's ruling on the `/laws/` stage
design → **G2** → the user's eye on the sheets → `pnpm release` (the user) → tag. After this wave,
in W31's Deferred order: the surface-conditioned retention (a `scenes.json` decision first); the
accessibility documents' own values; the CSS chroma operator; the analysis pass; a canvas the
span-160 exterior fits in (a `scenes.json` decision and a native re-capture); the thin regime's
instrument (W30 Deferred 4).

## Risks & Mitigations

- **The bed cannot see the span-160 exterior.** Folded: 160 is read inside its clearance and not
  fitted on; the canvas change is a Deferred item; C1's span-160 clause is stated over the
  admitted bands.
- **σ and spread do not separate on the admitted bands.** G0 reports the conditioning before the
  fit; if the pair is degenerate the constrained fit holds σ at the law and fits spread and offset
  alone; the free fit's degeneracy is recorded as such.
- **The over-filled contour enters through the anchors.** Folded: the anchor solve's departure is
  restricted to the 3–48 px window; the `0-3` band is tabled beside every reading; the
  whole-exterior B3 is still the stop.
- **The thick fit opens the thin regime, or the thin fit opens the thick.** Both are in the bed
  and the thin stop is per cell; the knee held at 44 by construction.
- **The anchors' linearity fails under a moved geometry.** A second round at every shipped
  candidate is the check; the convergence test names the bar; ten rounds budgeted at 346 cells
  each; the ship rule under non-convergence is defined in clause 3.
- **The recede's inactive bed above 96 is thin.** Three cells at 128 and seven at 160 after the
  widening, all probe; the holdout's inactive cells report beside; if the bed cannot identify a
  length the recede inherits it with the reading recorded.
- **The per-direction statistic pools unequal band sets.** Folded: the admitted-band rule fixes
  the set per span before pooling and bands-used is printed beside every figure.
- **The re-seal empties the 27 bed.** X10.
- **The `/laws/` stage is taste.** A sketch to the user before implementation; its own pin; the
  stage is the only part of the wave the user can strike without touching the material.

## Deferred / Out of Scope

A canvas the span-160 exterior fits in (a `scenes.json` decision and a native re-capture); the
surface-conditioned retention; the accessibility documents' own retentions; the CSS chroma
operator; the analysis pass; the sweep phase's wrap; `prelude.ts`'s ceiling; the receded tinted
cells' chroma; `mid-chroma-solid`'s rotation and level; the retention under Increase Contrast
alone; the level stop as a third material row; the identifying sitting; the highlight's angular
reader; the decoupled increased-contrast read and `compare`'s flag; the motion-metrics harness;
the CSS tier over pure black; inactive calibration cells above span 96 as a `scenes.json` change
(this wave widens the read set under the standing grant instead); `samplingPaddingFor`'s advisory
constant; the Reduced Transparency opacity policy; the slider's ends; the light bed's 16 px
structure; the `saturate()` constants; the thin regime's instrument; the receded contour's
hairline (a rim term and not a shadow one); `standard-row-identity-matrix.txt`'s generator and the
`interiorStdDevWeb` 5.69 % move (W31 Deferred 14, the halves not touched here); writing
`truncatedSides` to a row.

**Added 2026-09-21 (G1 review closure; claims §5.168 §10, finding B-4): the exterior BLACK FLOOR,
which is now the dominant visible exterior residual.** Over a backdrop pixel Apple renders as
exactly (0, 0, 0), vitrea renders (1, 1, 1) — one byte, never more — on 3,334 of 9,440 native-black
exterior pixels at span 160 on the 1x light bed, 2,188 of 17,532 at span 128, and **0 of 29,330 at
span 44**. Present at 160 and 128 and absent at 44, which is below `liftSpanMin` (64), so the term
it points at is `liftAmplitude` — the lift this wave did not move (X3 leaves it alone and no stop
reads it). It is pre-existing and not a regression; what makes it Deferred rather than invisible is
that the shadow now matches, so the floor is what the eye sees. **The shape of the work**: read
`liftAmplitude` against a native black floor — the per-pixel count of exterior pixels where the
native is 0 and the web is not, per span and per bed, swept over the leaf — and decide whether the
lift is a term Apple has at all over a black backdrop or an artefact of compositing a lift into a
premultiplied output. `b4-black-floor.py` in G1's evidence is the reading; the tracker carries the
entry with the reading hazard that hid it.

## Tracking Map

| child | status |
| --- | --- |
| G0 | **MERGED-READY 2026-09-21** — the cut, the clearance table, the direction tables, the model read, the three forms and the declarations; claims §5.166; six commits on `w32-g0-exterior-cut` — **corrected beside, 2026-09-21 (review closure; claims §5.166 §10, finding N15): SEVEN landed**, `85ee970c` through `8dc93e96`, the seventh being the one that removed a suite count §5.165 §9 does not record; no capture, no material change. **Review closure ON THE BRANCH, before merge, 2026-09-21** (§5.166 §10): `main` merged in (§5.167 beside §5.166, both Tracking Map rows, both Revision Notes), then three blocking findings, one blocking for G1 and thirteen non-blocking, all closed. **No measurement is withdrawn and no statistic moves**; every correction is beside the text it corrects and dated. The recede's population is **121 / 153**, not 100 of 100, and the `0-3` range 0.01633–0.12821; the span-128 outset is **two-and-two**, with all twenty bed × span rows printed and 1x dark excluding 3.10 at span 160 as well; the encoded form's 3e−06 is scoped to spans 32/44 and 96 on two beds, with the twenty moves printed. The thin stop gains the **nine accessibility cells it always named**, which hold the population's worst `|Δa|` — **0.04012** over 103 cells on six beds. **The recede has NEVER been a shadow on this bed**: 235 of 235 frozen macOS 26.5 rows flat, and off the fixture pixels macOS 27's whole receded exterior is ONE device pixel, a dark stroke rather than a transmission, where 26.5's is none. And **Apple's active reach on macOS 27 depends on the BACKDROP outside the thin regime** — 16.0–18.5 CSS px at span 96 over twelve backdrops, 25.0–28.8 at 128 — which G1 carries as a per-backdrop residual after the fit, with the material-or-instrument question a tracker entry. Four scripts changed and re-ran into their own names; three evidence files added; `freeze.py verify` **1,818** at open and close; `pnpm -r lint` exit 0; `@vitrea/calibration` **618 over 40 files, 0 failed** |
| G0b | **CLOSED 2026-09-21.** Three tools, no material, no capture, no number. **The holdout configuration ledger** moved to `results/holdout-configuration/`, the one location every canonical read records to, with its log **seeded byte for byte** from W31 G3's (G3's copies left byte-identical where they are) and the seed asserted field by field against them. The enumerated source list was CHECKED and deliberately **not widened**: the local import graph out of its five entry points reaches **50 further files**, around twenty of which move pixels at unmoved document bytes, and `renderer-bridge.ts` — asked about by name — holds no material constant but does decide which material reaches the renderer, so it is one of the fifty rather than a special case; widening would make every logged `sourceSha256` incomparable and fire "the sources moved" at every later read forever, so `sourceListSha256` is recorded instead and the ruling is a tracker entry. **The capture-tree checker** (`scripts/check-capture-tree.ts`, `pnpm --filter @vitrea/calibration run check-capture-tree`) compares every capture's document hashes — receded included — against the row beside it: on today's canonical tree **1,840 captures, 1,833 match, 0 mismatch, 0 superseded, 0 unreadable, 7 with no row, 0 rows with no capture, exit 0**, and one line and exit 0 where the tree is absent. **The macOS 26.5 tree reads as MATCHING**, which is the shape of W31's finding rather than a contradiction of it: the frozen documents have not moved, so that divergence is a re-capture at UNMOVED bytes and no string compare can see it — the generation half closes and the `--skip-capture` re-derivation is the narrowed tracker entry. A frozen mismatch exits **2** and a live one **1**, and `--superseded-ok` demotes only a generation the split has RECORDED. **`split-generation.py`'s docstring** made true about what it enforces (both flags required; the two being different is not checked), with the two committed entries annotated by `$comment` beside — two insertions, nothing recorded rewritten, `readme` a no-op and `plan` 1,833/1,833/0. Thirteen vitest cases; `freeze.py verify` **1,818** at open and close; **2,675 unit tests over 185 files, 0 failed**. Ledger **§5.167**; evidence `packages/calibration/results/2026-09-21-w32-g0b-evidence-tools/`. **Review closure merged 2026-09-21** (§5.167 §8): no blocking finding, seven non-blocking, all seven closed — five by a tool change, two by a record. The holdout refusal now compares against **every** record at those document hashes rather than the last, so A → B → A is refused and a named reason cannot re-open a configuration already read (the defect was inherited verbatim from W31 G3's copy, which stays byte-identical). The checker gains a **`misfiled`** class over the `deviceScaleFactor` / `colorScheme` / `accessibility` clauses, because a document is shared across profiles and a 1x capture in the 2x directory read as a MATCH; **exit 2 narrows** to a generation difference under a frozen key alone, so an unreadable or misfiled capture exits 1 whatever key it sits under; the `--superseded-ok` verdict line names its demotion; and a tree path that is a file or a dangling symlink inside one is reported with its path rather than thrown. The checker is **not** wired into `pnpm -r test` and that is a decision recorded beside §3 — the parent runs it at every merge, G2's `chain.sh` is where it becomes a step of the chain, and the tracker entry stays open on the "automatic" half. `index.json`'s two `$comment` annotations say "above" of a field below them and are noted-not-fixed (committed evidence); `CLAUDE.md`'s stale sentence is **G2's**, and what the replacement must keep is that a generation check is not a capture check. Five new cases, **2,680 over 185 files, 0 failed**; the canonical tree re-run **unchanged at 1,840 / 1,833 / 0 / 0 / 0 / 7 / 0, exit 0** with misfiled **0**; `freeze.py verify` **1,818** at open and close |
| G1 | **MERGED-READY 2026-09-21** — the joint fit, the recede's stand-down, the seal and the read, in one branch; claims §5.168; **nineteen commits** on `w32-g1-shadow-fit`, `1d45eafc` through this row's own — *a count of a branch's commits cannot be written by one of them without being wrong by one, which is W32 G0's finding N15 and is why this row was wrong twice (eleven when sixteen had landed, seventeen when eighteen had). Eighteen had landed when this was written and the commit carrying it is the nineteenth, which is the only form of the sentence that is true when it lands.* **C1 form (ii) as Decision Log 1 (c) ruled it is MET on all twelve bed × span rows at ≤ 0.0042**, from four of twelve: span 96 0.00088–0.00125 (was 0.00385–0.00413), 128 0.00245–0.00391 (was 0.00738–0.00889, failing by 76–112 %), 160 0.00132–0.00168 (was 0.00627–0.00797, failing by 49–90 %). **One leaf carried it**: `spreadPx` 3.10 → **0.50** light and → **1.80** dark, never fitted on the macOS 27 bed before, takes the objective from 0.00480/0.00381 to 0.00176/0.00225 and C1 from four rows to ten by itself; the six anchors re-solved against the 3–48 px window take it to twelve. `offsetPx` unmoved at 7.95 on a rendered coordinate step that moved the objective by **4 × 10⁻⁷** — G0's "the offset needs nothing", confirmed. The dark document carries its OWN outset because the dark bed refuses the light bed's by 2.7 × the bar at span 160, and its σ slope 0.1340 → 0.1215 inside B1. **Candidate (i) halves and does not close**: `σ_web − σ_nat` +1.27 to +2.77 CSS px against +2.66 to +3.77, OUTSIDE on all twelve, still a one-wave reading. **The free fit's distance from the constrained one is 0.00009/0.00011 — a twentieth of the bar — so no Decision Log draft on B1 goes to the user**; what a free σ buys at span 128 it sells at 160 on every bed. **Decision Log 2 confirmed at exactly zero**: the inactive `T` and window departure read 0.000000 in all five directions on every inactive bed and span, the far halo is gone by eye, and the receded reach is 0 at every span. Eight rounds of a ten-round budget, converged (Δobjective 4 × 10⁻⁷ light, 0.00010 dark; window anchor ratios 0.985–1.020). **B3 BROKEN at 0.00072 against 0.00035 and recorded, not widened**: the same statistic over the admitted bands reads **0.00006 against 0.00122**, the break decomposes to 0.00029 → 0.00064 active and 0.00039 → 0.00080 inactive, and the inactive half moved at round R before a single length did — B3 pools the `0-3` band, where vitrea's body over-fill and Apple's rim hairline live, and both are outside X3. **M2 misses one cell** (2.775 % against 2 %, span 32 inactive) through the SILHOUETTE EXTRACTOR rather than the body, recorded in `MISSED_27_ROWS` with the 2 % untouched. Seal: four digests moved, `freeze.py verify` **1,818** at open and close, the 34 goldens byte-identical, W31 Deferred 14 closed beside the two dark documents. Read: 1,833 → 2,619 → **1,893** rows, both append-checks 6/6, the capture tree 786/786 match, **230 gated / 786** against 230 / 726 — the widened ladder added 60 probe rows and no gated cell. `pnpm -r build`/`lint` exit 0; **2,684 unit tests over 186 files, 0 failed**. **Review closure ON THE BRANCH, before merge, 2026-09-21** (claims §5.168 §10): four blocking findings and fourteen non-blocking, all eighteen closed; **no measurement is withdrawn and no statistic moves**, every correction beside the text it corrects and dated, and nothing re-captured, re-fitted or re-read. Two change what a later child is told. **M2's miss has no mechanism**: four records named the silhouette extractor and the material axis's mask is the NATIVE silhouette, which moved on **0** of the 726 re-read rows (native area = web area = region = 2000, IoU 1 on the miss cell before and after); the candidate that replaces it — the optics pass compositing the shadow into the body's antialiased contour ring — is a hypothesis with its test in the tracker. And **the exterior's dominant visible residual is no longer the shadow**: over a backdrop pixel Apple renders as exactly 0, vitrea renders 1 — never more — on 3,334 of 9,440 native-black exterior pixels at span 160 on 1x light, 2,188 of 17,532 at 128 and **0 of 29,330 at 44**, which is below `liftSpanMin` 64 and points at `liftAmplitude`; a ΔE × 8 OKLab panel renders that one byte as a mid-grey, which is why `eye.md` recorded the opposite. Also: the dark σ law was printed at the superseded constants in `renderer-webgpu/README.md`; the `PREDICATE_EXCLUDES` cell cleared the **BODY-COUNT** arm (2 → 1), not the area arm, which was clear on both sides and moved the wrong way; the free fit's 0.00009 / 0.00011 is a LOWER bound at un-resolved anchors; B3's break was unavoidable by arithmetic over its own 166 cells, and **Decision Log 3 is inserted and put to the user**; the two superseded-index entries this branch wrote named the moving gate as the reader and are corrected in place before merge; and "the crossfade fades the shadow out" is true of the **CSS tier only**. Five tracker entries written and one widened; two evidence scripts added (`b2-mask.py`, `b4-black-floor.py`); `verdict.txt` regenerated with every line but §7's chroma block unchanged; `src/macos27-profile.ts` regenerated from its generator. Chain green again at the close: `pnpm -r build` and `pnpm -r lint` exit 0, **2,684 over 186 files, 0 failed**, `freeze.py verify` **1,818**, and `git diff main..HEAD` shows no change under `apps/`, `packages/renderer-webgpu/src/` or any macOS 26.5-keyed path. **Twenty-five commits**, `1d45eafc` through this row's own, which is the twenty-fifth — the only form of that sentence that is true when it lands (W32 G0 finding N15) |
| G2 | not opened |

## Decision Log

### Decision Log 1 — 2026-09-21: (a), (b) and (c) RULED by the parent under the standing "rest on your judgement" ((c) at G0's close), (d) the user's

**(a) B1 and the joint fit — RULED: the constrained fit ships; the free fit is a measurement.**
The σ law's leaves may move only inside B1's joint windows at the shipped bytes, `sigmaSpanRefPx`
held at 96 and the knee at 44; the free fit is run beside it and recorded round by round; if the
two disagree beyond the bar, a Decision Log draft on re-stating B1 over the rendered exterior goes
to the user for a later wave. What this does and does not constrain is stated in clause 3: B1
pins the law's closed form, nothing pins the two lengths, and the lengths are bounded at the
verdict by candidate (i) and C1 as declared by G0. Reason: an adopted bound is not fitted off in
the wave that finds it inconvenient, and the disagreement, if any, is the evidence a re-statement
would need.

**(b) The recede's bed — RULED: the read set is widened to the nine probe inactive scenes whose
native fixtures are on disk and have never been read on the web side** (`checkerboard`,
`impulse`, `light-solid`, `photo` on `rrect-ml`; `impulse`, `dark-solid`, `mid-dark-solid`,
`light-solid`, `hc-text`, `mid-chroma-solid` on `rrect-lg`), and the receded documents' anchors are
solved on the inactive cells including them, as W30 Decision Log 3 (d) granted the active ladder
to the σ law. The split does not move; no scene changes set; the holdout's inactive cells report
beside. The v1 draft granted "the ladder's inactive rungs at 128 and 160", which the review found
did not exist at 128 in the matrix and were three cells at 160 (Surprises); the fixtures did, and
this is the read-set decision that uses them.

**(c) C1's adopted form — RULED by the parent at G0's close, 2026-09-21, on G0's tables (claims
§5.166 §5; `bounds-declaration.md` §2) as reproduced cell for cell by G0's independent review:
form (ii), per-span `T` over the admitted bands, ≤ 0.0042 at spans 96, 128 and 160.** The bound is
the charter's rule applied to the bed (the worst standard bed's span-96 order statistic, 0.00413,
rounded up to two significant figures); the statistic, the exclusions, the population and the order
statistic are exactly §5.162 §3's; the admitted band set per span is 3-6 / 6-12 / 12-24 / 24-48 at
96, 3-6 / 6-12 / 12-24 at 128 (the `24-48` band is outside the frame by half a pixel on every
side), and 3-6 / 6-12 at 160 — not the three bands the v2 Design paragraph named, corrected beside
in the Revision Notes. Form (i) is recorded beside at every read and stays §5.162's before-reading.
Form (iii), the σ-normalised window, is **withdrawn on measurement**: the clearance measured in the
bed's own native σ is 5.5–5.9 at span 96, 2.7 at 128 and 1.1 at 160, so it reads nothing at the
span whose residual is largest at any choice of multiples; it becomes available when the canvas
does (Deferred). What the ruling costs: span 96 passes today with 1.7 % of headroom on 2x light, so
a fit that buys span 128 by widening span 96 fails, which is the clause's own statement that span
96 is not free either. Today: PASS at 96 on all four beds; FAIL at 128 by 76–112 % and at 160 by
49–90 %.

*As drafted at v2:* (c) to be ruled by the parent at G0's close, among `T` as declared,
per-span `T`, and the σ-normalised window, every one over the admitted bands, with the bounds of
the two non-declared forms fixed by clause 2's rule before G0's tables exist. The v1 prior on a
depth-normalised form is withdrawn on the review's measurement.

**(d) The `/laws/` shadow stage — the user's.** G2 puts a sketch before implementing; the user
may strike it without touching the material.

### Decision Log 2 — RULED by the parent at G0's close, 2026-09-21, under the standing "rest on your judgement": the recede's outer shadow stands down to the measurement

**Ruled.** The receded documents' outer-shadow AMPLITUDE — the six occlusion anchors,
`liftAmplitude`, and the receded documents' own `reducedTransparencyOcclusion` — is set to **0**,
as a declared reading rather than a fitted value (the way W30 Decision Log 2 (b) declared
`sigmaThinOffsetPx`), and G1 confirms it with one round on the inactive bed. The receded lengths
stay the active document's and are recorded as unread, since nothing draws at zero amplitude. The
active documents' accessibility fold amplitude does not move (X3).

**Why.** G0 found what no wave had written down (claims §5.166 §7; its review reproduced it
independently and extended it): on every non-holdout inactive WebGPU row of the macOS 27 bed —
**121 of 121**, both schemes, both scales, the accessibility beds included; 153 of 153 with the
holdout — Apple's receded window removes no light from 3 CSS px outward: the native transmission
reads exactly 1.000000 with no lift in every admitted band, `falloffSigmaNative` resolves on none,
and at the pixel level the native inactive capture is byte-identical to the backdrop raster from
2 device px outward. The same holds on the frozen macOS 26.5 bed (235 of 235; byte-identical from
1 device px). What Apple's receded exterior has is a one-device-pixel dark stroke at the contour
(body 188, first exterior row 156 over a backdrop of 255 and 0–6 over a backdrop of 0, below `checkerboard__rrect-lg__inactive` at 1x) —
the hairline the tracker already names as a rim term. Vitrea draws the full ACTIVE shadow in the
inactive pose because both receded documents carry their active document's anchors leaf for leaf,
so `outerShadowReachPx` returns the active reach at every span; the inactive `T` at span 160 reads
0.098 / 0.137 (1x light / dark) against the active 0.008, and the far halo the tracker measured at
17.42 / 15.89 is that shadow.

**What it changes in the charter.** Clause 4's "anchor solve on the inactive cells" becomes a
stand-down confirmed by one round: the declared judgement "the inactive departure ratio per regime"
has a zero denominator on every bed, so the verdict is the inactive window-restricted departure on
the web side going to 0 (native 0.000000) and the residual inactive `T` being the `0-3` band's
alone; the halo cell is on the sheets before and after. The window-activation crossfade now fades
the shadow out on deactivation **on the CSS tier**, which is what the reference does; on the WebGPU
tier it disappears in one frame (corrected 2026-09-21, G1 review closure; claims §5.168 §10, finding
N-12 — `css-tier.ts` transitions `box-shadow`, `root.ts` swaps the posed profile the instant the
resolved activation changes, and `receded-profile.ts` says the two endpoints are not an interpolated
pose; the crossfade that would close it is a tracker entry). The inactive reach becomes 0 and
the group clip in the inactive pose shrinks with it — recorded in the tracker's padding entry (X8:
the advisory constant does not move). The 26.5 receded material, frozen, draws the same wrong
shadow and stays as it is (X1); a tracker entry records it. The hairline is not this wave's
(Deferred: a rim term).

### Decision Log 3 — PUT TO THE USER 2026-09-22 by the parent, at G1's close: B3 could not have been kept, and its re-statement is a bound's re-pin

**What happened.** B3 — the shadow's departure residual over the WHOLE exterior, ≤ 0.00035 on the
WebGPU tier, a stop W30 declared and W31 and this wave carried — reads **0.00072** at G1's read,
from 0.00034 before. It broke in two halves and neither is a fitted length. The INACTIVE half
moved first, from 0.00039 to 0.00080 per inactive cell (0.00054 pooled), at the round that
executed Decision Log 2 (the recede's amplitude to 0) before a single length changed, because
Apple's receded exterior is a one-pixel contour stroke vitrea does not draw and B3 now reads that
stroke uncancelled. The ACTIVE half moved from 0.00029 to 0.00064 because B3 pools the `0-3` band,
where vitrea's body over-fills its declared contour (`Δa` +0.089…+0.151, §5.62), and that positive
error had been CANCELLING the 3–48 px exterior's negative one; the fit removed the exterior's error
and left the over-fill's standing. The same statistic over the admitted bands (3–48 px) reads
**0.00122 → 0.00006**.

**It was unattainable once Decision Log 2 was ruled**, by arithmetic over B3's own 166 cells (85
active, 81 inactive): the inactive half alone after the stand-down contributes
81 × 0.00080 / 166 = 0.000390 > 0.00035, so B3 fails with a PERFECT active half; and without the
stand-down, the fitted active half alone gives (85 × 0.00064 + 81 × 0.00039) / 166 = 0.000518. No
choice of anchors, lengths or fit order kept it. Recorded, not widened, not re-fitted (X4); the cut
is prepared with it disclosed (G1's independent review, N-2).

**The parent recommends (a): re-state B3 over the admitted bands, both poses, with the bound
re-derived by clause 2's rule from the bed at the read**, so the stop reads the shadow and not the
body's edge. The `0-3` band's over-fill keeps its own entry (§5.62; tracker) and the receded
contour hairline its own (Deferred: a rim term). Alternative (b): keep B3 as stated and record it
broken at every cut until a rim wave draws the stroke and a silhouette wave closes the over-fill —
honest, and it makes B3 a standing red that reads nothing about the shadow. Alternative (c):
re-state over the active pose only with `0-3` excluded — narrower than (a), and it drops the
inactive pose from the stop just as the recede became a measured zero.

Under (a) the number is a rule's output, not this wave's choice; under any of the three the
verdict at §5.168 stands as written. Until it is ruled, 0.00072 read without `b3-window.py`
beside it says the exterior got worse, which is the opposite of what happened. Ruled: ______.

## Surprises & Discoveries

- **One leaf that had never been fitted carried the whole wave** (W32 G1, claims
  §5.168 §2). `spreadPx` 3.10 → 0.50 on the light document and → 1.80 on the dark
  one, with the σ law, the offset and all thirteen amplitudes held, moves the
  admitted-band objective 0.00480 → 0.00176 and 0.00381 → 0.00225 and takes C1
  from four of twelve bed × span rows passing to **ten**. The anchors, re-solved
  in closed form against the window, take it to twelve. The charter budgeted ten
  rounds for a four-parameter joint fit; the fit used seven of them and the first
  did most of it.
  **Said plainly, 2026-09-21 (review closure; claims §5.168 §10, finding N-6):**
  "converged in seven" is the budget, not a claim that each leaf was refined to a
  minimum. The declared convergence test is REPEATABILITY at one candidate and
  round E met it. The two LENGTHS were sampled rather than refined — the light
  `spreadPx` took two values across the whole fit (3.10, 0.50) and the dark one
  three (3.10, 1.80, 0.50), with nothing between them tried — so what ships is
  the best of the sampled points under every declared stop, with 0.50 being the
  centre of Apple's own measured outset interval [0, 1] rather than a located
  minimum. The σ law and the six anchors are solved; the lengths are chosen.
- **B3 was green by CANCELLATION, and the wave that fixes the exterior breaks it
  — before a single length moves** (W32 G1, claims §5.168 §7; a tracker entry).
  The stop reads 0.00034 at the shipped documents and 0.00072 at the fitted ones,
  while the same statistic over the same 166 cells restricted to the admitted
  bands reads **0.00122 → 0.00006**. B3 integrates the WHOLE exterior, which
  includes the `0-3` band every form of C1 excludes; in that band vitrea's body
  over-fills its contour (`Δa` +0.089 to +0.151) where in 3–48 px it removed too
  much (−0.008 to −0.019), and the two errors cancelled in B3's mean. Round R —
  Decision Log 2's stand-down at the SHIPPED active material — already reads
  0.00054, so the inactive half of the break is the parent's ruling and not the
  fit. Neither term is one X3 lets this wave touch. **Recorded, not widened, not
  re-fitted**; the re-statement is a ruling the user owns.
- **`offsetPx` is flat to 4 × 10⁻⁷ over Apple's own interval** (W32 G1, claims
  §5.168 §2). A rendered coordinate step to 7.65 at the light document's
  converged candidate moves the objective by four parts in ten million, mixed in
  sign per span. G0's model-fit reading is confirmed by a render, and the
  displacement ships unmoved at the macOS 26.5 default. The window DEPARTURE is
  not flat in the offset, which is why a closed-form anchor solve is only valid
  at the geometry it was taken on.
- **B2 moves the OPPOSITE way to the exterior it is supposed to describe** (W32
  G1, claims §5.168 §7; added 2026-09-21, review closure, finding N-3). B2 — the
  law's σ at span 44 against the bed's own measured thin σ, ≤ 1.5×, not adopted
  (§5.156 §5 (b), §5.159) — reads **1.7622 of 1.5** at the sealed dark constants
  against 1.3387 at the fit's unrounded ones. Holding the knee at 44 while the
  slope drops 0.1340 → 0.1215 re-derives the thin offset −6.968 → −6.318, so the
  thin line rises 2.072 → **2.722** CSS px against Apple's dark thin σ of 1.5446.
  On the same bed the RENDERED thin exterior improved by 8.7× at span 44 and 24×
  at span 32 (`T` 0.00201 → 0.00023, 0.00171 → 0.00007). A blur leaf read in
  closed form and a rendered exterior are different quantities, and this is the
  outset/σ confound B2 was declared a one-wave reading for.
- **The two colour schemes do not want the same outset** (W32 G1, claims §5.168
  §2). At `spreadPx` 0.50 the dark objective RISES and span 160's `T` triples
  (0.00269 → 0.00777, 0.00241 → 0.00817). The difference is 0.0055, 2.7 times the
  bar, so the dark document carries its own 1.80 — the charter's conditional
  decided by measurement rather than by default.
- **B1's window costs the fit at least a twentieth of the bar** (W32 G1, claims
  §5.168 §3). The free fit — the σ law outside B1 on both schemes, everything
  else held — improves the objective by 0.00009 and 0.00011, and what it buys at
  span 128 it sells at span 160 on every bed. Decision Log 1 (a)'s conditional
  does not fire and no draft on re-stating B1 goes to the user.
  **Qualified beside, 2026-09-21 (review closure; claims §5.168 §10, finding
  N-1):** round F is ONE render at round E's anchors, and F's own window solve
  wants anchors 3–10 % away (light 0.0244 → 0.0258, 0.0227 → 0.0250,
  0.1797 → 0.1887; ratios 1.027–1.099), while `rounds/F/anchor-solve.txt` §1's
  "converged" compares F's objective to E's rather than testing repeatability at
  F's own point. The distance is therefore a **lower bound** at un-resolved
  anchors — a free fit carried to its own convergence can only be further from
  the constrained one. It does not change the ruling: the bar is 19 to 23 times
  the measured distance, and the span-160 trade justifies the constrained σ on
  its own. Round F was not re-run; that would be a fit.
- **M2 took its first miss since adoption, and the mask it is read over did not
  move** (W32 G1, claims §5.168 §7). One cell (span 32, inactive, 1x light)
  carries a cumulative 2.775 % against 2 %. The bound is untouched and the miss
  is recorded; M2 gains the path M1 has had since adoption.
  **Corrected beside, 2026-09-21 (review closure; claims §5.168 §10, finding
  B-2):** this entry said the mechanism was the silhouette extractor —
  "`interiorStdDevWeb` is read over the EXTRACTED silhouette and the extractor
  thresholds the render against its background". The material axis's mask is the
  NATIVE silhouette by construction (`cli/measure.ts`: `const interior =
  nativeSil`, with the doc comment above it saying that a web-derived mask moves
  under tuning), and over the **726** rows this gate superseded and re-read
  `silhouetteAreaNative` moved on **0**, against 80 moves of the shape axis's
  own `silhouetteAreaWeb` (`b2-mask.py`). On the miss cell the native area, the
  web area and the declared region all read 2000 with an IoU of 1 before and
  after. What moved is the render's values under a fixed mask. The CANDIDATE
  mechanism, an unmeasured hypothesis, is the optics pass compositing
  `shadowAlpha · (1 − coverage)` into the antialiased contour ring INSIDE the
  declared region (`renderer-webgpu/src/wgsl/optics.ts`), which would put the
  effect where that ring is the largest fraction of the region — the thinnest
  span, which is where the miss landed. The deferral is repointed accordingly:
  the lever is not the extractor's asymmetry, and the measurement that would
  test the hypothesis is a tracker entry.
- **The fit FIXED a conditioning exclusion.** `PREDICATE_EXCLUDES` goes 68 → 67
  because the CSS tier's silhouette on `checkerboard__capsule-button__rest` at 1x
  light-increased-contrast-coupled stopped drawing in two pieces, so that
  profile's `dom` shape rows gate 7 cells where they gated 6. A wave removing a
  cell from the excluded list by making it well-conditioned is the first time
  that list has shrunk for that reason.
  **Corrected beside, 2026-09-21 (review closure; claims §5.168 §10, finding
  B-3):** this entry, the test comment and commit `0e03f189`'s body all said the
  cell "now clears 95 % of its declared region", and the AREA arm was never the
  one failing. Off the two generations it reads **4756 → 4755** of a 4872 px
  region against a threshold of 4628.4 — clear on both sides, and it moved the
  wrong way. The arm that cleared is `silhouetteBodiesWeb`, **2 → 1**: the
  `box-shadow` outset fell 3.10 → 0.50 CSS px and the silhouette closed into one
  body. The count, the cell and the consequence stand exactly as recorded.
- **Apple's receded window casts no outer shadow at all beyond 3 CSS px, and vitrea draws the
  ACTIVE shadow there leaf for leaf** (W32 G0, claims §5.166 §7). On 100 of 100 non-holdout
  inactive WebGPU rows — every span, both schemes, the accessibility beds included — the native
  render equals its backdrop to the axis's six written decimals in every admitted band, the
  identified pairs read `a` = 1.000000 with `c` = 0, the native window-restricted departure is
  exactly 0.000000, and `falloffSigmaNative` resolves on none of them. Apple's whole receded
  exterior lives in the `0-3` band at a departure of 0.024–0.128 — the contour hairline this
  wave's Deferred list already names as a rim term. Vitrea's receded documents carry their active
  document's anchors leaf for leaf, so `outerShadowReachPx` returns the active reach at every span.
  **Corrected beside, 2026-09-21 (review closure; claims §5.166 §10, finding B1):** the population
  is **121 of 121** — 108 standard-bed rows and 13 accessibility-bed rows, which is what
  `exterior-cut.txt` §12c's `n` column sums to — and **153 of 153** with the holdout admitted, the
  only three admitted bands on either count whose native `a` is not exactly 1.000000 being holdout
  `6-12` bands at span 160 reading 1.000001 with `c` = 0. The `0-3` departure's per-bed medians run
  **0.01633–0.12821**, not 0.024–0.128. No verdict moves.
  **And it has never been a shadow** (added 2026-09-21, review closure; claims §5.166 §10, finding
  N16): the same census over the FROZEN macOS 26.5 rows reads **235 of 235** flat, native window
  departure 0.000000 on every one, `falloffSigmaNative` on none, and no admitted band whose native
  `a` is anything but exactly 1.000000. Read off the fixture pixels, the macOS 27 inactive capture
  is byte-identical to its background from **2 device px** outward and the 26.5 one from **1**, on
  all four sides at both scales — so Apple's whole receded exterior on macOS 27 is **one device
  pixel**, and it is a semi-transparent dark STROKE rather than a transmission: 156 over a backdrop
  of 255 and 0–6 over a backdrop of 0, darker than both backdrop and body over the light square and
  lighter than the backdrop over the dark one. Clause 4's zero denominator is not a property of
  this generation's documents.
  Clause 4's "the receded documents' anchors are solved on the inactive cells" is therefore a solve
  whose target is ZERO amplitude in the 3–48 px window, not a lower alpha on the same falloff, and
  the departure ratio it is judged on has a zero denominator at every span on every bed.
- **The admitted band set at span 160 is `3-6 / 6-12`, not `3-6 / 6-12 / 12-24`** (W32 G0, claims
  §5.166 §1). The `12-24` band's outer edge is 24 CSS px against 19.50 of clearance on every side.
  The charter's Design paragraph "Which spans fit and which are read" names three bands; the rule
  the same charter states admits two. And at span 128 the `24-48` band is outside the frame on the
  LEFT AND RIGHT too — 47.50 against 48.00, by half a pixel — not only above and below. Dropping
  it makes the span-128 reading WORSE, 0.00487–0.00532 → 0.00738–0.00889, because that band carried
  53 % of the weight and was where the two exteriors agreed most.
- **Apple's own outset is not zero: it is about half a pixel** (W32 G0, claims §5.166 §4;
  §5.162 §9's finding N-10 answered). The native-side fit of the renderer's own falloff model reads
  a spread of 0.0–1.0 CSS px at spans 32, 44 and 96 with vitrea's 3.10 outside the one-sigma
  interval on every standard bed, and an offset of 7.65–8.22 against vitrea's 7.95 at every span.
  The same fit on vitrea's own render recovers the shipped triple at those spans and does NOT at
  128 and 160, which is the instrument's own error and the boundary a native-side prior may be
  trusted inside.
- **`MISSED_27_ROWS` is five + three and §5.162 §4's seven is stale** (W32 G0, claims §5.166 §6).
  Two of that section's seven cleared at W31 G3 (0.21531 → 0.14655, 0.21341 → 0.14505) and M1's
  three joined at W31 G4. Decomposed, `checkerboard__rrect-lg__rest :: ssimMean` is NOT reachable
  through the shadow at all — a perfect exterior moves it 0.01518 against a 0.01577 gap.
  **Qualified beside, 2026-09-21 (review closure; claims §5.166 §10, finding N13):** the margin is
  **0.00059**, and `reach` counts only the 14,519 `ssimOutside` windows while treating the 18,556
  `ssimBand` windows — 31.8 % of the cell, at `ssimBand` 0.7874 — as unimprovable. The `0-3` band
  every form of C1 excludes lives in that region, so the verdict reads "not reachable by the
  exterior this wave fits" rather than "not reachable by any shadow work".
- **The window-restricted departure is a different objective, not a tidier one** (W32 G0, claims
  §5.166 §6). Over the admitted bands the web-minus-native difference is 3.3 to 6.4 times the
  whole-exterior one and it reverses the sign structure: over the whole exterior vitrea's departure
  is BELOW Apple's at every thick span on 1x light and over the window it is ABOVE. Clause 3's
  "the difference between the two solves is measured at the first round" is load-bearing.
  **Corrected beside, 2026-09-21 (review closure; claims §5.166 §10, finding N11):** 3.3 to 6.4 is
  the 1x light range; over the four standard beds the ratio runs **1.69 to 50.66**, the 50.66 a
  ratio of two tiny numbers at 2x dark span 32. The restricted difference is the larger on every
  bed at every span, by at least 1.69×, and the SIGN reversal is 1x light's alone — on 2x light the
  whole-exterior ratio is above 1 at every span, so there is no sign there to reverse.
- **The bed cannot see a span-160 exterior, and three waves read one there without saying so**
  (found by this charter's adversarial review, 2026-09-21, from `matrix.json` and `scenes.json`).
  `rrect-lg` is 280 × 160 on a 320 × 200 canvas: 19.5 CSS px of clearance on every side; the
  `24-48` band survives only in the corners (532 px above/below, 242 left/right, against ~10,000
  at span 128); `extentBelowWeb` and `offsetYWeb` are absent on all 100 span-160 rows; the axis's
  own comment puts the σ bias at ~8 % low for a σ ≈ 17 px shadow through a 20 px margin, and
  `scenes.json`'s `rrect-ml` comment says span 128 is the largest this canvas carries intact.
  §5.162's span-160 `T` and B1's span-160 native σ (17.317) are both read through that frame.
  Nothing recorded is wrong; what was missing is the qualification beside it, and the fix in kind
  is a larger canvas, which is a `scenes.json` decision and a native re-capture (X5) — Deferred.
- **The v1 charter's depth-normalised C1 form was false on the bed.** Read as `T` over the
  weighted native depth it reads 3.44 / 3.37 / 0.72 / 0.31 / 0.20 across spans 32 → 160 (1x
  light), inverting the wave's thin/thick reading by 17×, and had no bound; withdrawn.
- **The thin regime is not "right" on the per-band reading.** `T` weights the `12-24` and `24-48`
  bands at 36 of 45 and the shadow reaches neither at spans 32 and 44 on either side, so the
  statistic diluted an inner-band `Δa` of −0.0175 / −0.0123 (span 32) and −0.0187 / −0.0149 (44) —
  larger per band than span 160's — to 0.00168–0.00339. The eye's "right" was "confined to the
  body", a different claim. The thin spans join the fit's bed and the thin stop is per cell on the
  inner bands.
- **The recede's span-128 bed existed as fixtures and not as rows.** Four probe inactive `rrect-ml`
  scenes have native captures under every 27 fixture directory and appear in no ladder list, so
  the matrix carries zero inactive rows at span 128; six more at `rrect-lg` are in the same state.
  A read-set decision (Decision Log 1 (b)), not a capture.
- **Nothing pins `spreadPx` or `offsetPx` at the shipped documents** — every pin mirrors the
  default or derives from the leaf — so the v1 "constrained fit" constrained the σ law alone.
  Folded into clause 2 and 3 as declared readings on the lengths.

## Outcomes & Retrospective

(at close)

## Revision Notes
- 2026-09-22 (the parent, G1's merge): G1 merged to main as `9c4b3bce` with `--no-ff`, twenty-five
  commits; `freeze.py verify` 1,818 at the merge; the read's capture tree copied to the canonical
  `web-captures/` as part of the merge and the checker run there (1,900 captures, 1,893 match,
  0 mismatch, 7 no-row — the 26.5 extras); the generation it replaced moved aside to
  `web-captures-superseded/<sha>/` on the machine (tracker, the canonical-tree entry's merge
  record). Gated count pinned on main: **230 / 786**. Decision Log 3 unruled, put to the user.

- 2026-09-21 (G1 review closure): **G1's review closure landed on its own branch, before merge.**
  The independent review reproduced every number §5.168 records and found no measurement wrong and
  nothing to re-capture, re-fit or re-read; what it found was the prose layer and one table of
  provenance. **Four blocking findings and fourteen non-blocking, all eighteen closed** (§5.168
  §10). **Nothing is withdrawn and no statistic moves**; `freeze.py verify` reads 1,818 at the
  closure's open and close, the chain is green at 2,684 over 186 files, and no byte moves under
  `apps/`, `packages/renderer-webgpu/src/` or any macOS 26.5-keyed path.
  **Four of them change what G2 is told.** First, **M2's miss has no mechanism**: the silhouette
  extractor is ruled out by measurement — the material axis's mask is the NATIVE silhouette and
  moved on 0 of the 726 re-read rows, with native area = web area = region = 2000 and IoU 1 on the
  miss cell before and after — so a wave planning around "the extractor's asymmetry" is planning
  around nothing. The replacement is a hypothesis with its test attached: the optics pass
  composites `shadowAlpha · (1 − coverage)` into the body's own antialiased contour ring inside the
  declared region, which would put the effect on the thinnest span, which is where the miss landed.
  Second, **the exterior's dominant visible residual is no longer the shadow**: over a backdrop
  pixel Apple renders as exactly 0, vitrea renders 1 — never more — on thousands of exterior pixels
  at spans 128 and 160 and on none at 44, which is below `liftSpanMin`. It points at
  `liftAmplitude`, is pre-existing, and was invisible because a ΔE × 8 OKLab panel renders one
  least significant bit at the black floor as a mid-grey. **A ΔE × 8 panel over a backdrop
  containing pure black is not a verdict on the exterior without the LSB check** — that is the
  general rule, and every future sheet over `checkerboard*`, `dark-solid` or `hc-text` inherits it.
  Third, **B3 could not have been kept**, by arithmetic over its own 166 cells: the inactive half
  alone after the ruled stand-down gives 0.000390 and the fitted active half beside the pre-fit
  inactive one gives 0.000518, both above 0.00035. **Decision Log 3 is inserted above, verbatim and
  unruled** — the re-statement of an adopted stop is the user's. Fourth, **the crossfade is the CSS
  tier's alone**: `root.ts` swaps the posed profile discretely and `receded-profile.ts` says the
  endpoints are not interpolated, so on the tier this wave fits the shadow disappears in one frame,
  which the stand-down is exactly what made visible.
  Two corrections to what this charter itself says are recorded beside their Surprises: the
  `PREDICATE_EXCLUDES` cell cleared the **body-count** arm (`silhouetteBodiesWeb` 2 → 1), not the
  area arm, which read 4756 → 4755 of a 4628.4 threshold and moved the wrong way — **commit
  `0e03f189`'s body carries the same slip and cannot be amended**; and the free fit's
  0.00009 / 0.00011 is a **lower bound** at anchors round F never resolved, which changes nothing
  because the bar is 19 to 23 times it and the span-160 trade justifies the constrained σ alone.
  Also recorded: **commit `c0f73092` carries a mid-read 2,165-row `matrix.json`** from an
  over-broad `git add`, disclosed in `0e03f189`, which lands 1,893 — the branch merges whole so
  `main` never sees it, but a checkout of that one commit is inconsistent. And **the parent's
  brief for this closure gave the wrong value** for the two superseded-index entries'
  `readUnderClaims` (`--read-claims "c9a §5.168"`, the moving gate); the right ones are §5.164 §13
  for the 479 light rows and §5.164 for the 247 dark ones, established from the capture timestamps
  and `git log` on `matrix.json`, and both entries are corrected in place because they have not
  merged. Five tracker entries written and one widened; two evidence scripts added; `verdict.txt`
  and `src/macos27-profile.ts` regenerated by their own producers.

- 2026-09-21 (G1): **the fit, the recede, the seal and the read landed in one
  branch; C1's ruled clause is met on twelve of twelve rows and two stops are
  recorded broken.** Seven Surprises added, of which three change what a later
  child is told. First, **B3 cannot be read as a verdict on this wave** — it is
  green by the cancellation of a body over-fill against a shadow excess, the
  RULED recede stand-down breaks it at the shipped active material, and the same
  statistic over the admitted bands falls by a factor of twenty; a later wave
  reading 0.00072 without `b3-window.py` beside it will conclude the exterior got
  worse. Second, **candidate (i) halves and does not close**: after the fit
  `σ_web − σ_nat` is +1.27 to +2.77 CSS px and OUTSIDE B1's window on all twelve
  rows, so the sentence W31 G1 found false is still false and the outset was not
  the whole of it. Third, **the per-backdrop residual is real**: `T` at span 128
  runs 0.00253 to 0.00556 across twelve backdrops after the fit and the extent
  excess keeps §5.166 §10's ordering, so one triple does not describe the pooled
  bed and N17's tracker entry narrows rather than closes. G1 adopted nothing:
  C1's adoption, the `/laws/` stage and 0.22.0 are G2's.
- 2026-09-21 (the parent): **G0 merged (`f71c43d5`) with its review closure on the branch; Decision Log
  1 (c) RULED (form (ii), per-span `T` over the admitted bands, ≤ 0.0042) and Decision Log 2 RULED
  (the recede's outer-shadow amplitude stands down to 0 as a declared reading).** Two corrections to
  v2 from G0's tables, recorded beside rather than rewritten: span 160 admits TWO bands (3-6 / 6-12),
  not the three the Design paragraph "Which spans fit and which are read" names — the `12-24` band's
  outer edge is 24 CSS px against 19.5 of clearance; and at span 128 the `24-48` band is outside the
  frame on the left and right too (47.5 against 48.0), not only above and below. Clause 4 is executed
  as Decision Log 2 states it. G1 carries two readings G0's closure added: the span-128 outset prior
  is an evenly split bed (two beds include 3.10, two exclude it), and Apple's active reach on macOS
  27 varies with the backdrop by 14 % of the span's median at 96 and 128 (`extents-by-backdrop.txt`),
  which G1 reports as a per-backdrop residual after the fit. G1 dispatched.
- 2026-09-21 (G0 review closure): **G0's review closure landed on its own branch, before merge.**
  The independent review reproduced every committed script byte for byte and every statistic off
  `matrix.json` and found the METHOD sound and both headline findings true; what it found was the
  prose layer, and all seventeen findings are closed (§5.166 §10). **Nothing is withdrawn and no
  statistic moves.** **Three of them change what G1 is told.** First, the span-128 outset prior:
  the beds split **two and two**, not three and one, which is a weaker prior than one dissenting
  scale and agrees with the instrument recovering the shipped spread at 128 on no bed at all.
  Second, the thin stop was declared over every active non-holdout WebGPU cell at spans 32 and 44
  and tabulated over four beds: the **nine accessibility cells** it always bound had no "today",
  and they hold the population's worst reading — 0.04012 at the `3-6` band over 103 cells on six
  beds, 19.6× the bar. Third, **Apple's active reach on macOS 27 depends on the backdrop outside
  the thin regime** (16.0–18.5 CSS px at span 96 over twelve backdrops, 25.0–28.8 at 128, the same
  two backdrops at both extremes), so a fit of one triple against a pooled bed leaves a
  per-backdrop residual at every span and G1 reports it per backdrop. Whether that is the material
  or the threshold estimator is undecidable on an extent and is a tracker entry with the
  measurement that would close it.
  **And the recede is settled further than §5.166 could settle it.** The same census over the
  frozen macOS 26.5 rows reads 235 of 235 flat, so the empty receded exterior is not something
  macOS 27 does; read off the fixture PNGs, macOS 27's whole receded exterior is ONE device pixel
  — a semi-transparent dark stroke, not a transmission — and macOS 26.5's is none at all. Clause
  4's zero denominator is a property of Apple's material and not of this generation's documents.
  Four scripts changed and were re-run into their own file names (`stops.py`, `clearance.py`);
  three evidence files were added beside the committed ones (`recede-26.5.py`,
  `recede-cross-section.py`, `extents-by-backdrop.py`). `main` was merged into the branch first, so
  §5.167 sits beside §5.166 in numeric order and both Tracking Map rows and both Revision Notes
  are kept. `freeze.py verify` 1,818 at open and close; `pnpm -r lint` exit 0; `@vitrea/calibration`
  618 over 40 files, 0 failed — §5.166 §9's 600 over 38 plus the eighteen G0b's merge brought.

- 2026-09-21 (G0b closure): **G0b's review closure merged.** No blocking finding, seven
  non-blocking, all seven closed (§5.167 §8): five tool changes and two records. **Two of them
  change what a later child can rely on.** First, the holdout refusal was comparing against the
  LAST record at a set of document hashes, so a source hash that moved and came back was admitted
  — a second read of a configuration already read, arrived at by a route nothing watched. It now
  compares against every record, and a named reason admits sources the log has never carried at
  those documents rather than re-opening a configuration: G1's clause 5 `record` is refused unless
  its sources are new at its documents, which at new document bytes it is either way. Second, the
  capture-tree checker was blind to a cross-profile miscopy, because a document is shared across
  profiles by design — a 1x capture in the 2x directory named the row's documents and passed. The
  pose clauses are compared beside the documents now, as `misfiled`, exit 1 under a frozen key as
  well as a live one; exit 2 narrows to a generation difference under a frozen key alone. **And
  the checker is not automatic**: it is not in `pnpm -r test` and that is a decision, not an
  oversight — a mid-read tree on the capture machine would redden every test run on that machine
  and `--superseded-ok` covers only recorded generations. The parent runs it at every merge, G2's
  `chain.sh` is where it becomes a step of the chain, and the tracker entry stays open on the
  "automatic" half with the shape that would close it. `CLAUDE.md`'s stale sentence remains G2's
  under X11, and what its replacement must keep is that a generation check is not a capture check.
  W31 G3's `configuration.py` carries the old defect and stays byte-identical where it is, because
  it is that gate's witness. Five new cases (2,680 over 185 files); the canonical tree re-run
  unchanged; `freeze.py verify` 1,818 at open and close.

- 2026-09-21 (G0b): **G0b closed** — `results/holdout-configuration/` (seeded, README, five
  unit cases), `scripts/check-capture-tree.ts` (eight unit cases, the npm script, the run on the
  canonical tree) and `split-generation.py`'s corrected docstring with two `$comment` annotations
  beside the entries carrying the slip. §5.167 written; FOUR tracker entries amended beside (the fourth being W27f G2's
  "Nothing checks the canonical matrix against a fresh capture", whose shape (2) this half-
  builds) and one new one written, on the source list against the render's import closure.
  **Two things a later child should know.** First, the checker reads the macOS 26.5 tree as
  MATCHING and W31's finding still stands: that divergence is a re-capture at unmoved frozen
  document bytes, so a document-hash compare is structurally blind to it and the remaining
  instrument is a `compare --skip-capture` re-derivation off the tree's own PNGs. G1's clause 5
  gets the generation check it was promised and not a metric check. Second, the configuration's
  enumerated source list was found narrower than the render by 50 files and was NOT widened, for
  a reason that binds anyone tempted later: a `sourceSha256` taken over a different enumeration
  is incomparable rather than different, so widening retires the refusal it is meant to sharpen.
  That is a ruling, it is a tracker entry, and it is not G1's to take mid-fit.

- 2026-09-21 (G0): **the cut and the declarations landed; five entries added to Surprises.** Two
  correct the charter itself — the admitted band set at span 160 is two bands and not three, and
  the `24-48` band at span 128 is outside the frame on all four sides — and neither changes a
  clause: span 160 is still read inside its clearance and never fitted on, and span 128 is still
  fitted. Three are findings the charter could not have had: Apple's outset measured at about half
  a pixel against vitrea's 3.10; the recede's native exterior being empty beyond 3 CSS px, which
  makes clause 4 a solve toward zero rather than toward a lower alpha; and the window-restricted
  departure being a different objective from the whole-exterior one rather than a restriction of
  it. G0 recommends **form (ii)** of C1, the per-span bound at **0.0042** by the charter's own
  rule, and withdraws form (iii) on measurement — the clearance in the bed's own native σ is
  5.5–5.9 at span 96, 2.7 at 128 and 1.1 at 160, so no choice of multiples buys the same number of
  falloff lengths at every span on this canvas. Decision Log 1 (c) is the parent's to rule.

- 2026-09-21 (the parent): **v2 — the adversarial review folded.** Five blocking findings and
  seven non-blocking, every number reproduced by the parent from `matrix.json` before folding:
  (1) span 160's 19.5 px clearance — the fit's bed becomes 32 / 44 / 96 / 128, span 160 read
  inside its clearance and never fitted on, the admitted-band rule per cell from `clearance*`,
  bands-used beside every figure, `rrect-ml`'s declaration retired or upheld beside, the canvas
  change Deferred; (2) the recede's granted bed did not exist at 128 — Decision Log 1 (b)
  restated as a read-set widening to the nine unread probe inactive fixtures; (3) the
  depth-normalised form withdrawn, the three candidate forms made `T`, per-span `T` and the
  σ-normalised window, with a bound rule fixed before the tables; (4) the thin stop restated per
  cell on the inner bands against the named max bar 0.002044 from the G3b noise-bar file, and the
  thin spans admitted to the fit; (5) candidate (i) declared as a stop and read at the verdict,
  with the charter saying plainly that nothing pins the two lengths today; the anchor solve's
  departure restricted to the 3–48 px window with the change measured; a convergence test, a
  ten-round budget at 346 cells and a defined ship rule under non-convergence; the noise-bar
  path, the six-band count, the reader's-§4 citation, `above` at exactly zero, `truncatedSides`
  not on a row, the `/laws/` stage's pin and chain count — all corrected. The Purpose's
  "grows outward" replaced by the bed-wide per-band medians.
- 2026-09-21 (the parent): v1 chartered on main after the 0.21.0 publish record (`7a4ad3b4`),
  from W31's Deferred item 4, W30's items 8 and 10, and W31's items 12 and 14; sent to adversarial
  review before any child opens.
