# W38 — the rim-axis wave: the shipped rim's light turned vertical, as a bounded improvement (2026-09-25)

**Status: CHARTERED v3 2026-09-25 after two adversarial rounds (two P1 + two P2, then two P1, folded; Revision Notes); nothing dispatched.** Chartered by the parent on the user's
"W38 rim-axis refit (Recommended)" after W37 closed at its finding (main `b4715d78`), under the
standing "rest on your judgement" and the routing of 2026-09-22 (X9). Grounded on a read-only memo
(`/Users/new/.claude/jobs/17c7ce02/tmp/w38-grounding.md`, an `astra-high` product saved by the
parent; diagnostics under `~/vitrea-w38/grounding/`; every number reproduced by G0 before anything
is scored). **The parent's recommendation to the user was stronger than the grounding supports**,
and this charter says so: the wave is a bounded improvement under a dominance rule, not the
"cheapest eye-visible gain" without qualification.

## Purpose

vitrea's rim lights the sides of every active surface where Apple's edge is slightly dark: the
shipped diagonal law contributes +6.5 / +17.5 codes (light / dark) at the horizontal-normal arcs
where Apple reads −2.5 / −2 (§5.181), and at the top it contributes +7.1 / +23.3 where Apple's
line reads +31 / +39. `rimLitAxis` is already a per-document leaf, so turning the light vertical
on the four macOS 27 documents needs no new operator, no identity-table entry and no shader
change. That is the whole of what this wave may do. What it cannot do, established by the memo
before any fit: (1) draw Apple's line's colour — a neutral-light rim over physical occlusion
(0 ≤ k ≤ 1) has a proven floor of 16.81 codes on dark yellow's top row (the body's own strong
channels lifted while the weak one falls needs a chromatic term); (2) be assumed to land Apple's
two 2x rows — the shader samples `rw` at pixel centres and squares it, the memo's selected grid
point predicts 5.85 / 18.30 against 18 / 31 on light grey-128, and an area-integrating change is a
runtime change outside this wave; but this is an observed grid miss, not a form obstruction: the
adversarial review evaluated the existing-leaf law in the forward model at a vertical axis,
exponent 0.85, `rimWidth2x` 2.3245, `rimAlpha` 0.2157, gain and along-slope 0 and the shipped
shadow, and it predicts exactly 18.000 / 31.000 on that cell, so joint two-scale feasibility is a
question for the declared constrained search, not a settled limit; (3) improve everywhere by
aggregate least squares — the memo's 864-point grid per scheme,
selected on total encoded error, cut the light greys' maxima (25.6 → 16.6 straights, 19.8 → 12.8
arcs) but made the light solids worse (23.6 → 37.0) and the dark grey straights worse (24.2 →
28.8), with worst single-bin worsenings of +22 (dark yellow arc) and +17 (light green top), because
a vertical lobe puts 2^(exponent/2) times the amplitude on the top where neutral light desaturates
a coloured body.

So the purpose is narrow and testable: remove the side light Apple does not have, hold every
stratum at or better than today, and ship only a candidate that dominates the shipped treatment
under a rule declared before the first score — or close at the finding.

## Parent-Level Acceptance

1. **The cut precedes the fit; the dominance rule and the candidates are declared first.** G0
   reproduces the memo (the 9,637-bin / 84-cell old-treatment replay, the grid's stratum table,
   the chroma floor, the sampling numbers) into committed scripts through the guarded readers
   (calibration admitted; validation and W34's holdout refused), then DECLARES, committed and
   hashed before any score: (a) **two candidates** — **C1, the pure rotation at held top
   amplitude**: axis (0, −1), the REGULAR variant's `rimAlpha` and `rimLevelGain` scaled by
   2^(−exponent/2) so the ordinary rim's straight top and bottom draw exactly today's light, the
   sides draw none, and the diagonals change from the old law's 1.34× / 0× pair to the new lobe's
   value; the collapsed amplitudes (`rimCollapsed`, `rimCollapsedTinted`) are NOT scaled — they are
   profile-wide constants every variant consumes (`renderer.ts` ~1177–1202; `optics.ts` ~1572,
   ~1604, ~1636 multiply them by the variant's own angular factor), and the clear variant at
   exponent 0 has no rotation gain to compensate, so scaling them would dim clear's collapsed rim
   to 0.7448 of today — instead the regular variant's collapsed and tinted rims BRIGHTEN at the top
   by 2^(exponent/2) = 1.34 under the rotation, which G0 prices on the canonical tinted cells
   against the per-bin veto (Decision Log 2); nothing else moves; and **C2, the
   rotation with a refit** of `rimLitExponent`, `rimWidth` / `rimWidth2x`, `rimAlpha`,
   `rimLevelGain`, `rimAlongSideSlope`, `shadowDepth` / `shadowAlpha` on the regular variant,
   selected by a declared constrained objective (minimax over the strata subject to the dominance
   rule), not by aggregate least squares; (b) **the dominance rule, per bin first**: (i) a
   PER-CHANNEL-BIN VETO — no admitted channel-bin's MAE against the native excess is worse than
   the shipped treatment's by more than the closure tolerance (1 code) on any cell of the archive's
   calibration set, tinted and structured diagnostics included; a single veto disqualifies the
   candidate, because a stratum's maximum and mean both improve while one coloured arc worsens by
   22 codes (the memo's dark-yellow bin: 25.87 → 48.22 inside a stratum whose maximum fell 99.28 →
   80.79 and mean 4.31 → 2.28) — an aggregate rule accepts exactly the defect this wave exists to
   avoid; (ii) per stratum — the greys' straights, the greys' arcs, the solids' straights, the
   solids' arcs, the noncircular transfer cells, each per scheme — the maximum AND the mean
   channel-bin MAE not worse than the shipped treatment's by more than the bar (0.5 code); (iii)
   the horizontal-normal bins' excess within 2 codes of Apple's; (iv) every trade within the veto
   tabled with the worst named. No tolerance, bound, stratum or allowance is redefined to admit a
   candidate; a candidate that fails (i) anywhere or (ii)–(iii) on any stratum is not nominated;
   (c) **E2 frozen, as a rendered-edge regression row over every canonical active row an
   estimator can MEASURE, with the rest named**: three declared estimators, each with a minimum
   measured-coverage requirement below which a row is UNMEASURED and never a pass — (1) W37's E1
   estimator (one centred component, straight-side intervals, capsules top/bottom only, absent
   sides UNMEASURED) on every non-holdout active macOS 27 WebGPU `gpu-texture` row with a single
   component: uniform, tinted and structured; (2) a geometry-aware CURVED-boundary cut for the
   grouped rows, whose members are three 44×44 circular capsules with no straight interval
   (`scenes.json` ~323–331): per-member placement from the scene declaration, W35's whole-pixel
   arc bins by normal angle, a per-member deep reference, the bins' ownership by member declared;
   (3) for the two stacked `glass-over-glass` rows — both HOLDOUT, backend
   `gpu-texture+css-backdrop` — the visible layer's boundary under estimator (1) or (2) as the
   scene declares, applied ONLY at G1b's one holdout read as accept-or-stop, never in G1a. Bound
   for all three: the per-side-or-arc / per-shell / per-channel MAE of the excess over the d ≤ −6
   deep against native is not worse than the pre-W38 generation's capture by more than 1 code on
   any measured bin; on the 14 untinted uniform rows the side straights' excess additionally lands
   within a declared bound. Re-derivable from matrix fields, the matrix-named captures at the
   adopting bytes and the named superseded generation, as L1 is. Paths with NO native fixture —
   the unsampled `css-backdrop` / `none` WebGPU e2e fixtures and Reduce Transparency — get a
   separate regression contract **R1**, declared in G0: outside the rim band the render is
   byte-identical to the pre-W38 render; inside it the side band's luminance does not rise and the
   top band stays within 1 code of before under C1 (within the law's own prediction under C2);
   exercised at G1a. Together E2 and R1 are the veto the omitted paths get, not the eye at G2; (d) every stop's expected value
   (clause 4); (e) the pre-W38 baselines named — the matrix generation, the goldens' hashes, the
   window-activation hashes, the E1 artifact.
2. **Native-only identification, transfer tabled, rendered check.** C2's coefficients are
   identified on native pixels with the native deep as the conditioning input (W37 clause 3 in
   full — the rim's `g·L_shadowed` is body-conditioned); the transfer to the web body is tabled per
   cell; G1a renders C1 and C2 through the tune path on scratch documents and compares against the
   forward prediction; a refinement is admitted only under W37 clause 3's attribution rule.
3. **The fit's reach.** The four macOS 27 documents' EXISTING leaves named in clause 1 — the
   regular variant's `rimAlpha`, `rimLevelGain`, `rimWidth` / `rimWidth2x`, `rimLitExponent`,
   `rimAlongSideSlope`, `shadowDepth` / `shadowAlpha`, and the top-level `rimLitAxis`; the shared
   collapsed constants and the clear variant's leaves untouched, which is what keeps clear
   identical (its exponent 0 makes the axis inert there; a test renders it and says so); √2, the
   squared form and the shader
   untouched; no signed shadow amplification (k ≤ 1 — the floor argument stands); the frozen 26.5
   documents' values unmoved; the receded documents' amplitudes stay 0 and their PIXELS
   byte-identical (a test says so) while their DIGESTS move because the axis and widths are in the
   composed material — all four documents are resealed and `window-activation.spec.ts`'s macOS 27
   expectations updated with the reason.
4. **Bounds before reads; a miss is recorded, not widened; holdout once by artifact.** The
   canonical holdout read once at the sealed configuration (its sixth read, G1b); W34's holdout
   spent. Every stop read with its expected value declared in G0: the per-cell tables and
   `MISSED_27_ROWS`, the predicate (churn counted), M1 (a neutral ring moves numerator and
   denominator — priced), M2 ±2 % against the generation this wave supersedes with the ring's
   sensitivity put to the user as Decision Log 3 WITH the measured delta before any mask or bound
   moves, L1 ≤ 0.055 / growth ≤ 0.005 against W33 (a narrower ring moves the silhouette mean —
   priced per row), C1 ≤ 0.0042 / X1 = 0 / B1 ±5 % shown on pixels (the rim is coverage-limited
   half a device px outside the contour; grouped and stacked cells verified, never assumed), tier
   coherence (repriced on a render), the goldens (the renderer harness draws the default material,
   so a document-only change should leave the 13 PNGs byte-identical — the isolation proof run and
   any delta attributed before a hash moves), W29 G3's FWHM reading recorded beside, not promised.
5. **Every path an existing-leaf patch reaches is rendered.** Unlike W37's gated operator, a
   document patch reaches the collapsed and tinted rims, Reduce Transparency (which keeps the
   ordinary rim), the WebGPU `css-backdrop` and `none` backends and the grouped/stacked cells; G1a
   renders each over differing backdrops and reads E2's rendered-edge veto on every non-holdout
   canonical row its estimators measure (the stacks wait for G1b's holdout read), R1 on the paths
   with no native fixture, and the per-bin veto on the bed's tinted and structured diagnostics — a
   rendered regression is a rejection, not a residual to table, and no refit is admitted to
   absorb the body's miss (W37 clause 3); Increase Contrast's strong border and forced-colors are
   unchanged by construction and shown so.
6. **The CSS tier derives from the same leaves and is priced before the seal.** The CSS inset's
   alpha is converted from the BLENDED amplitude `A·(1−T) + C·T` (ordinary mixed with collapsed by
   the tint, `platform-web/src/optics.ts` ~4432–4435, converted at ~4026–4033) with NO angular
   factor, so C1's scaling of `A` alone would dim the CSS straight top on untinted surfaces and
   dividing the conversion by the scale would not restore it on tinted ones. The derivation
   therefore FOLLOWS THE ROTATED LOBE as the WebGPU tier does: the blended amplitude is
   multiplied by the lobe's straight-normal value `lit_top = (√2·|axis·ŷ|)^exponent` evaluated
   from the resolved variant's ACTUAL axis and exponent — 1 for the frozen 26.5 diagonal, for the
   clear variant (exponent 0) and for the strong border (exponent zeroed), 2^(exponent/2) under the
   rotation. Under C1 that leaves the untinted CSS inset byte-identical to today's and brightens
   the collapsed contribution by the same 1.3426 the WebGPU tier applies (at full collapse the
   shipped regular bare alpha 0.02432 → 0.03265, painted 0.3328 → 0.44681 — recorded as the
   priced change, mirrored across tiers, not an identity); ordinary, partial-collapse,
   full-collapse, clear and strong-border cases are pinned SEPARATELY in `tier-coherence.test.ts`
   with the reason. The interior-light integral (which already suppresses the vertical runs
   under a vertical axis) is re-derived from the patched leaves; G1a renders the projection
   on the bed and the canonical non-holdout CSS cells and records the residual against the 6.5 /
   8.5 two-row bound; the parent rules carry or decline as Decision Log 5 BEFORE G1b seals.
7. **Seal, read, tree** as W37 clause 7 (rule-2 seal, configuration 6, the read once, the split,
   the tree to canonical with the replaced generation aside, `check-capture-tree`); G1b changes
   nothing beyond what the rulings on G1a fixed; after the holdout read, accept or stop.
8. **Landing.** E2 adopted; M2 re-baselined per W32 Decision Log 4 with the drift tabled; docs
   swept (`CLAUDE.md`'s rim and contour paragraphs, READMEs, CHANGELOG, coverage matrix, `/laws/`);
   the chain with X6's four facts; 0.25.0 prepared; the eye on the captures beside the fixtures —
   the sides dark where Apple's are, the top no dimmer than today, no whitening of the tinted
   buttons' line.

## Grounding Baseline (main at `b4715d78`, W37 closed)

The memo's law, leaf table, resolved endpoints, grid, stratum table, floor, sampling numbers,
footprint and CSS reading are the baseline (memo §§1–6); the guarded reader is
`results/2026-09-23-w34-g0-contour-bed/w35_readers.py`; the holdout configuration log holds five
records; the E1 artifact is `results/2026-09-25-w37-g0b-edge-identification/e1-baseline-repaired.json`.

## Design (advisory unless marked)

C1 is the wave's floor: a change that by construction leaves the straight tops and bottoms as they
are and removes the side light, so its only priced risk is the diagonals and the collapsed/tinted
rims. C2 is the ceiling within the family: a narrower, brighter top within the dominance rule. G0
scores both on the archive; if C2 cannot dominate, C1 alone goes to G1a; if C1 cannot dominate, the
wave closes. The objective for C2 is minimax over strata under the rule, never aggregate least
squares (the memo shows what that selects). Rendering is where the diagonals and the transfer
are actually read; nothing about a rendered candidate is inferred from the forward model.

## Children

### G0: The cut, the rule, the candidates on the archive, E2 frozen — no material change, no capture

Ledger **§5.183**; evidence `packages/calibration/results/2026-09-25-w38-g0-rim-axis-cut/`. Owns its
dir and `test/w38-*.test.ts`. Does clause 1 in full, clause 2's identification for C2, the
collapsed/tinted amplitude scaling for C1 with its reading on the canonical tinted cells (native
fixtures), the stops' expected values, the pre-W38 baselines, the Decision Log 1 draft (C2, C1
alone, or close). Stop: neither candidate dominates on the archive → the wave closes at the finding.

### G1a: Both candidates rendered, every path read, the CSS projection, M2's delta — pre-seal

Ledger **§5.184**; evidence `…/2026-09-25-w38-g1a-rim-axis-render/`. Owns the scratch documents and
the CSS derivation's code. Renders C1 and C2 through the tune path on the bed's scenes and the
canonical non-holdout cells (never holdout), reads every stop of clause 4 and every path of clause
5 — E2's estimators (1) and (2) on the rows they measure, R1 on the paths without a fixture —
records the transfer and the rendered-versus-forward check, the CSS projection's residual with the
five pinned cases, M2's delta with the eroded-mask attribution; the Decision Log 1 / 3 / 5
material. Nothing sealed.

### G1b: The seal, the read, the tree — one merge

Ledger **§5.185**; evidence `…/2026-09-25-w38-g1b-rim-axis-seal/`. With the rulings fixed: the
four documents patched and resealed, the generated profile, `PREDICATE_EXCLUDES` / `MISSED_27_ROWS`,
`window-activation.spec.ts`'s hashes with the reason, `configuration.py record`, the read once
including the holdout — E2's estimator (3) on the two stacked rows read there, once, as
accept-or-stop — the split, the tree. Accept or stop.

### G2: The landing — E2 adopted, 0.25.0 prepared

Ledger **§5.186**; evidence `…/2026-09-25-w38-g2-landing/`. Clause 8.

## Cross-Child Contracts

W37's X1–X17 carry verbatim with these substitutions: X3's reach is clause 3 here; X13 has no new
leaf (the identity table is untouched); X15 applies to C2's `g` and `a`; X16 reads "the receded
pixels are identity, the receded digests move and are resealed"; X17 reads "every backend is
rendered, none is inferred". **X18 — the dominance rule is the acceptance, per bin first**: a
single channel-bin worse than the shipped treatment by more than 1 code disqualifies a candidate,
then the stratum rule; no tolerance, bound, stratum or allowance is redefined to make one pass.
**X19 — C1's amplitude scaling is exact and touches only the regular variant**: 2^(−exponent/2)
at the shipped exponent on `rimAlpha` and `rimLevelGain`, so the ordinary rim's straight top and
bottom are byte-identical to today on an untinted uniform backdrop on BOTH tiers, the clear
variant is byte-identical everywhere, and the collapsed/tinted contribution brightens by the same
factor on both tiers (priced, Decision Log 2); tests say so case by case. **X20 —
the collapsed constants are shared and do not move.**

## Ordering & Dependency Map

G0 → review → merge → Decision Log 1 (the parent) → G1a → review → merge (scratch evidence only) →
Decision Logs 1 (final), 3 (the user, on the measured delta) and 5 (the parent) → G1b → review →
merge with the tree → G2 → review → merge → `pnpm release` (the user's hand) → tag. No ruling that
changes a source or a document after G1b's holdout read.

## Risks & Mitigations

- **C1 moves the diagonals the wrong way.** The old law lights the top-left/bottom-right diagonals
  at 1.34× and the others at 0; the new lobe gives both about 0.75× at held top amplitude. G0's
  per-bin table on the arcs says which way each moves; the dominance rule decides.
- **The collapsed/tinted rims brighten at the top by 1.34× under C1** because their shared
  constants cannot be scaled without dimming clear; priced on the canonical tinted cells against
  the per-bin veto before anything renders (Decision Log 2). If the tinted line whitens beyond the
  veto, C1 fails on that evidence.
- **M2 on the ring.** Decision Log 3 with the measured delta.
- **The CSS inset cannot follow the lobe.** Priced before the seal; carry or decline.
- **A stop breaks only at the render.** Revert to C1 if it holds; else close.
- **The stacks are holdout.** Their E2 reading exists once, at G1b; a failure there is a stop, not
  a refit, and G1a cannot pre-price it beyond the grouped rows' curved-boundary reading.

## Deferred / Out of Scope

The chromatic line term (W37 Deferred 1); the area-integrating `rw` (a runtime change with its own
charter); signed shadow amplification; any change to the clear variant, the 26.5 documents, the
strong border; the native experiment.

## Tracking Map

| child | state |
| --- | --- |
| G0 | not dispatched |
| G1a | not dispatched |
| G1b | not dispatched |
| G2 | not dispatched |

## Decision Log

### Decision Log 1 — which candidate, or none (after G0 on the archive; final after G1a's render; the parent's)

Open. G0 drafts on the stratum tables; G1a finalises on the rendered stops.

### Decision Log 2 — the collapsed and tinted rims under C1 (after G0; the parent's)

Open. Default: the shared collapsed constants stay (clear identity), so the regular variant's
collapsed and tinted rims brighten at the top by 2^(exponent/2) under the rotation; G0 prices that
on the canonical tinted cells (native fixtures present) against the per-bin veto. A
variant-specific collapsed amplitude would be a NEW leaf pair through the identity table and is
not authorised by this charter.

### Decision Log 3 — M2's mask or bound on the ring (after G1a's measured delta, before the seal; the user's)

Open, carried from W35 Decision Log 3 and W37 Decision Log 3.

### Decision Log 4 — E2's frozen form (after G0; the parent's)

Open.

### Decision Log 5 — the CSS projection: carry or decline (after G1a's measurement, before the seal; the parent's)

Open.

## Surprises & Discoveries

- **The rim's axis was a leaf all along.** `rimLitAxis` is a top-level profile leaf, patchable per
  document; no wave since W24 read it as one. (memo §1)
- **The wave's own recommendation was oversold.** The parent put the refit to the user as "the
  cheapest eye-visible gain left"; the grounding shows a neutral-light floor of 16.81 codes on
  saturated colours and an aggregate refit that trades bins heavily. The charter narrows the wave
  to a dominance-ruled improvement and says so to the user.

## Outcomes & Retrospective

(at close)

## Deferred at close

(at close)

## Revision Notes

- 2026-09-25 (v3, the parent, after the second adversarial round's two P1s): **P1 folded** — the
  CSS conversion fix promised identity but the inset converts the BLENDED amplitude (ordinary
  mixed with collapsed by tint), so dividing by the scale would have restored the untinted top and
  brightened the collapsed one by 1/s; clause 6 now follows the rotated lobe on the CSS tier
  exactly as the WebGPU tier does (`lit_top` from the resolved variant's actual axis and
  exponent, 1 for the 26.5 diagonal, clear and strong border), identity on untinted surfaces, the
  collapsed brightening mirrored and priced (0.02432 → 0.03265 bare, 0.3328 → 0.44681 painted at
  full collapse), five cases pinned separately (clause 6, X19). **P1 folded** — E2 promised every
  canonical row but its estimator measures one centred component with straight intervals: the
  grouped toolbar's members are all-arc circles (every bin UNMEASURED) and both stacked rows are
  holdout with a backend E1's check rejects; E2 now has three declared estimators with minimum
  coverage (straight-interval rows; a curved-boundary per-member cut for the grouped rows; the
  stacks' visible layer at G1b's one holdout read only, accept-or-stop), and the paths with no
  native fixture get R1, a separate regression contract (clauses 1c, 5, G1a, G1b, Risks).
- 2026-09-25 (v2, the parent, after the adversarial review's four findings): **P1 folded** — C1
  scaled the collapsed amplitudes, which are profile-wide constants every variant consumes, so it
  would have dimmed the clear variant's collapsed rim to 0.7448 while declaring clear untouched;
  C1 now scales only the regular `rimAlpha` / `rimLevelGain`, the collapsed constants stay (X20),
  and the regular collapsed/tinted top's 1.34× brightening is priced against the veto (clause 1a,
  3, Risks, Decision Log 2). **P1 folded** — the dominance rule was aggregate and would have
  accepted the memo's +22-code dark-yellow worsening inside a stratum whose maximum and mean both
  improved; a per-channel-bin veto at 1 code now comes first (clause 1b, X18). **P2 folded** — the
  omitted paths had no edge gate; E2 is now a rendered-edge regression row over every canonical
  active row with a native fixture, tinted and structured included, exercised at G1a as a veto
  (clauses 1c, 5); and the CSS inset's alpha conversion, which has no angular factor, would have
  dimmed the CSS top under C1 — clause 6 now takes the lobe's top value into the conversion so
  C1's CSS is byte-identical. **P2 folded** — Purpose claimed the two 2x rows cannot be landed;
  the reviewer's forward-model point (vertical axis, exponent 0.85, width2x 2.3245, alpha 0.2157)
  predicts 18.000 / 31.000 exactly, so the claim is restated as an observed grid miss and left to
  the constrained search.
- 2026-09-25 (v1, the parent): chartered on the grounding memo; nothing dispatched; to
  `doperpowers:adversarial-reviewer` before G0 opens.
