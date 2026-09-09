# Quality instrument: a rubric several judges agree on, and the grammar's loss read through it

Status: pre-registered 2026-09-09, before any rating is collected. Parent: `2026-09-05-settling-experiment.md`
(the stop rule's diagnosis initiative, ordered by the user 2026-09-09: instrument first, then the
grammar's quality loss).

## Purpose

The settling experiment's quality endpoint — one forced choice, "which would you be more likely to
deliver to a client?", over 78 pairs — came back at chance agreement between every pair of its three
blinded judges (the user, an astra-medium rater, a claude-opus rater: Cohen's κ 0.03, 0.17, 0.14), each
judge ordering the four skill versions differently. Nothing about quality can be claimed from it, and
no change to the skill can be accepted or rejected on quality until there is an instrument that
several judges agree on. This initiative builds that instrument and reads the same 52 builds with it.

After it, a quality claim is a number with a reliability behind it — "2.1 is below 2.0 on
deliverability by 0.8 of a point, panel α 0.71, human–panel ρ 0.66" — and the composition grammar's
quality reading (`v2.1` against `v2.0`, where two of three settling judges put 2.0 ahead) is either
confirmed and located in named rubric items, on named briefs, with the raters' evidence pointing at
named rules, or found not detectable at this sample size, which is also an answer. The next grammar
change is then held to this instrument, not to a coin flip. The loss is not presupposed: it came
from an instrument at chance agreement, and this run's first job on it is to confirm or dissolve it.

What someone can do that they could not before:

- `python3 docs/research/scripts/settling/rubric.py prompt <brief> <judge> <seed>` prints a blinded
  rubric prompt for one brief's eight pages in a seeded shuffle; a dispatched rater writes one JSON
  file per brief.
- `python3 docs/research/scripts/settling/rate.py` serves `/rubric`, the user's rating page for the
  anchor set on the same captures and items, blinded like the pairwise page.
- `python3 docs/research/scripts/settling/analyze.py` prints a Reliability section (α per item,
  human–panel ρ, retest), per-arm means with confidence intervals per item, and the `v2.1` − `v2.0`
  paired differences the diagnosis reads.

Terms used below. *Krippendorff's α*: a chance-corrected agreement coefficient for any number of raters
and for ordinal scales; 1 is perfect agreement, 0 is chance. *Spearman ρ*: rank correlation. *Anchor
set*: the pages the user rates, against which the model panel is validated. *Retest*: the same rater
rating the same pages again in a different order.

## The measured problem (what the settling run showed about its own instrument)

- Three judges, 78 pairs: 41, 47 and 46 same-winner pairs per judge pair; unanimous on 28. The
  astra rater agrees with itself across two runs (κ 0.85), so the disagreement is between judges,
  not within one: each stated a criterion the others did not weigh (the decision-ordered queue; light
  high-contrast consoles and whether the goods are pictured; the conventional console shell).
- A forced choice with no tie on pages of comparable craft is a coin flip on exactly the pairs that
  decide the hypothesis, and it yields one number per pair, nothing per dimension.
- The judges did not see the same thing: the user saw the full-page capture at half scale in a
  split pane; the model judges saw the first viewport and the full page; two first-viewport captures
  were taken after the page had scrolled itself; one full-page capture was 2760 px wide.
- Position bias was never measured (each pair was served once, in one orientation).

## What the world knows (prior art the design stands on)

- **VisAWI and VisAWI-S** (Moshagen & Thielsch, *Behaviour & Information Technology* 2010 and
  2013): a validated instrument for perceived visual aesthetics of websites, four facets —
  simplicity, diversity, colourfulness, craftsmanship — with a four-item short form (one item per
  facet, 7-point agreement) validated on 1,673 raters for internal consistency and factor
  structure, convergent with overall appeal and divergent from perceived usability and content
  quality. Its validation is within-rater, on end users of live sites, and makes no inter-rater
  agreement claim; what it gives this run is published, taste-neutral item wording that did not
  have to be invented here. The manual allows adapting the wording to other interfaces.
- **Model-judge reliability** (Zheng et al. 2023; arXiv 2606.19544, 2606.00093, 2602.02219, 2025–26):
  pairwise verdicts flip on 25–50 % of items when the order is swapped, and swapping-and-averaging
  raises within-judge consistency from about 60 % to 85 %; Krippendorff's α is the reliability
  statistic to report for three or more raters (α ≥ 0.8 strong, 0.67–0.8 tentative, under 0.4 the
  rubric is ambiguous rather than the raters wrong); raters should come from more than one model
  family; a judge is calibrated against human labels on a gold subset.
- **UICrit** (Duan et al., UIST 2024): seven designers rated 983 mobile screens on an anchored rubric
  (aesthetics, usability, overall), three raters per screen in the public release; zero-shot model
  critiques were 13 % valid, and few-shot prompting with human-rated examples raised expert-scored
  quality by 55 %. **UIClip** (Wu et al., UIST 2024, MIT): a CLIP model fine-tuned on UI quality,
  ~0.2 B parameters, CPU; zero-shot vision-language models were near chance on "which of two UIs is
  better designed", UIClip the best agreement with twelve designers' rankings. Both say what the
  settling run saw: a general model is weak on holistic preference and far better on anchored
  per-item items with a human anchor.

## Design

### The rubric

Every rater answers the same items for every page of a brief while all eight of that brief's pages
are in view (the brief's own pages are the frame, which is what kept the settling fit rater
consistent). Items, with the scale in brackets:

**A. Aesthetics — VisAWI-S, wording per the manual's interface adaptation** [1 do not agree at all …
7 fully agree]
- a1 Everything goes together on this page. *(simplicity)*
- a2 The layout is pleasantly varied. *(diversity)*
- a3 The colour composition is attractive. *(colourfulness)*
- a4 The layout appears professionally designed. *(craftsmanship)*

**B. Brief fit — presence items, one fact each, written from the brief's own nouns and frozen
here** [0 absent; 1 present but deficient; 2 present and adequate] — the settling fit rater's
yes-of-five shape with a middle step, because a presence fact on a 7-point agreement scale invites
scale-use disagreement (7 against 5 for "there but weak"). Where the brief states a tone, one tone
item **t1** follows on the 7-point agreement scale.

| brief | items |
|---|---|
| rail | b1 Every live train's position and state is visible without scrolling. b2 Delay exceptions are separated from routine traffic and placed before it. b3 Crew hours appear as values and times. b4 Maintenance windows appear as values and times. |
| fleet | b1 Open defects are listed by vehicle. b2 Overdue inspections are visibly distinguished from the rest. b3 Parts on order carry an expected date or a status each. b4 The workshop's day (bays, jobs, times) is readable as a schedule. |
| pharmacy | b1 Stock levels by drug are a table with quantities and a par or reorder level. b2 Expiring lots are shown as their own set. b3 Controlled-substance counts are shown as their own set. b4 Pending orders carry a status each. |
| compare | b1 The three suppliers are compared on the same criteria in one structure. b2 Price per axle, lead time, warranty and on-site fitting are each visible for each supplier. b3 There is a control to pick a supplier. b4 The page shows that a pick is recorded. |
| rebate | b1 Whether a resident qualifies is stated within the first screen. b2 The rebate's value is stated as amounts with its conditions. b3 The approved installers are listed. b4 The one application form is reachable from the page. |
| library | b1 The sign-up is within the first screen. b2 Weekly book lists appear as lists of titles. b3 An event calendar with dates is on the page. t1 The page reads as for children and their parents without being garish. |
| hardware | b1 Featured tools are shown with prices. b2 The goods are pictured (a photograph or a drawing). b3 Seasonal project guides are on the page. b4 In-store pickup is explained. t1 The page reads as practical and trustworthy rather than startup-slick. |

**C. Defects — five observations** [0 not seen, 1 seen], summed to a count 0–5
- c1 Content clipped or cut off by its container.
- c2 Text too small or too faint to read at this size.
- c3 An empty, placeholder or broken region (an image slot without an image, lorem, template text).
- c4 Spacing or alignment inconsistent between like elements.
- c5 The layout is wider than the viewport, or scrolls sideways.

The c-items are answered from the four captures only; a clip below the third viewport exists only in
the downscaled full capture and is not expected to be seen. c5 has a ground truth (the capture's
width, `overflowCapture` in `measurements.json`) and c3 has one (the gate's placeholder read); the
panel's precision and recall against both are reported, a free check that the raters can see the
captures at all.

**D. Deliverability — the endpoint**, anchored by the rework the page needs before it could go to
the client, not by the rater's liking [7 deliver as it is; 5 cosmetic fixes only (tokens, spacing,
copy); 3 structural rework (a region added, moved or re-formed); 1 start over; 6, 4 and 2 between]
- d1 What would this page need before you delivered it to the client who wrote the brief?

The anchor by rework category is there because the settling judges' reasons show their d1
disagreement was a weighting of criteria (a light console for all-shift use; a decision-ordered
queue; the conventional shell), and no scale format removes a weighting disagreement; a rater who
dislikes a dark ground cannot call it structural rework. The declared expectation, so the result
can be read against it: aesthetics, brief fit and defects will agree; d1 will agree where defects
or missing brief content dominate and split on taste in the middle. If the middle still splits, the
rework anchor has not been enough and the shared-client alternative (Deferred) is the next try.

**E. Conventionality — reported beside quality, never in it** [1 this page looks like nothing I have
seen for this kind of brief; 7 this is the default page for this kind of brief]
- e1 How conventional is this page for its brief?

A model rater gives one clause of evidence on the b-, c- and d-items (evidence on aesthetics and
conventionality is rationalisation and is not asked for); the user rates without evidence. Fourteen
to sixteen answers per page for a model rater.

### Raters

- **The model panel.** Four blinded raters, two model families by two rungs: `astra-medium` and
  `astra-high` (GPT), `claude-opus` and `claude-sonnet` (Claude), the only two families the gateway
  offers. One brief per prompt (eight pages by four captures, 32 images), every brief for every
  rater: 28 runs. The page order in each prompt is a shuffle seeded by (rater, brief) and recorded
  in the output.
- **Retest.** Every rater repeats the two anchor briefs in a second shuffle: eight more runs.
- **The user** rates the *anchor set* — pharmacy and library, sixteen pages — on the rating page,
  same captures, order seeded and recorded, on the taste-bearing items only: a1–a4, d1 and e1, six
  answers a page, and then four of the pages again in a second order (the user's own retest). About
  a hundred and twenty answers, under thirty minutes; the settling sitting fatigued at 78 forced
  choices, and the number that matters, the panel–human agreement on d1, is the one fatigue would
  corrupt. The b- and c-items are checked against the mechanical reads and the settling fit rater
  instead. These two briefs are where the settling judges disagreed most (3 of 12 and 4 of 12
  pairs), so the instrument is tested where the last one failed; that also makes the human–panel
  floor the likeliest to miss, and the branch for that is declared below.
- **Pilot.** One brief by all four raters before the 28 runs, to check the JSON shape and whether
  a response carrying a hundred evidence clauses survives; the pilot's ratings count if the shape
  holds.
- **UIClip** scores every page's first-viewport and full-page capture against its brief
  (`uiclip.py`, the model card's sliding-window recipe). It is a reported column: its rank
  correlation with the panel's d1 and a1–a4 is a finding about the model, and it is never in α.

Blinding as in the settling run: raters see captures and random ids only, never a build's
directory, DESIGN.md or the arm.

### Captures: one set for every rater

`measure.mjs` gains a fixed capture protocol and every one of the 52 builds is recaptured before any
rating: load; wait for `document.fonts.ready` and 1500 ms; record `scrollY`; take the first-viewport
capture at scroll 0 *before* any scroll-through (the two settling artifacts were pages that scrolled
themselves during the walk); then the walk for lazy content; return to 0; the full-page capture; then
`tile-2.png` and `tile-3.png`, the second and third 900-px viewports cut from the full capture at
native resolution (a page shorter than 1800 px sends what exists). Overflow is read as the full
capture's width against 1440, recorded beside the load-time read. Every rater, the user included,
receives the same four files per page. The same files are not the same sight — a model reads a
downscaled image, the user native pixels on the rating page — which is why the tiles exist.

### Aggregation and reliability

- Per item: Krippendorff's α across the four model raters, with a bootstrap interval, over three
  page sets — all 52 pages (pooled), the 26 `v2.0` and `v2.1` pages (the set the grammar reading
  uses; pooled α is inflated by between-brief level differences and by the plainly broken pages,
  which the within-brief comparison never touches), and per brief averaged. Ordinal for the 7-point
  and 0–2 items, nominal for c1–c5. Beside the four-rater α: α within each family (the two GPT
  raters; the two Claude raters) and α between the two family means, so a pass carried by
  within-family redundancy is visible as such. And α across all raters including the user over the
  anchor set, on the items the user rated.
- Human–panel: Spearman ρ, with its interval, between the user's rating and the panel mean, per
  item, over the sixteen anchor pages; mean absolute difference beside it.
- Retest: per rater, α between the first and second rating of the retest pages (chance-corrected;
  a rater choosing among 4, 5 and 6 at random would pass a within-±1 share of 85 % by arithmetic),
  with the within-±1 share reported beside it; the user's four retest pages the same way.
- Position: rating regressed on position in the recorded shuffle, pooled over raters and briefs,
  per item — the presentation-order effect the retest on two briefs cannot estimate.
- Against the forced choice: each rater's implied verdict on the settling run's 78 pairs, derived
  from its d1 (a tie where equal), and its κ against the user's forced choices and against the
  astra-medium and claude-opus forced choices on the same pages. A rater whose d1 contradicts its
  own earlier forced choice says pointwise and pairwise elicit different things.
- Page scores: d1 = panel mean; aesthetics = mean of a1–a4 (the VisAWI-S total); brief fit = mean of
  b1–b3; defects = mean count; e1 = panel mean.
- Per arm: mean and a bootstrap 95 % interval (resampling pages) over its thirteen pages, per item
  and per composite, pooled and per brief.
- `v2.1` − `v2.0`: paired by brief and seed label — thirteen pairs, in effect paired by brief, since
  the two arms' samplers drew different seeds and the two seeds of one arm are often near-duplicates
  (rail reproduced its forms seed by seed), so the effective number of pairs is under thirteen —
  the difference on every item with its interval, and per rater the sign of the d1 difference on
  each pair, so a panel-mean difference cannot hide rater disagreement. The minimum detectable
  difference is stated with it: with thirteen pairs and a paired standard deviation of 1 to 1.5
  points the 95 % half-width is about 0.6 to 0.8 of a point, so a difference under that is "not
  detectable here", not "none".
- The no-skill hold (settling Decision Log 2026-09-09): `none` against `v1.1` on d1 and defects.
  The hold stands unless `none`'s paired d1 difference against `v1.1` is positive with its interval
  excluding zero; it is confirmed if the difference is negative with its interval excluding zero;
  between, it is reported as not decided at this sample.

`analyze.py` prints all of this in a Reliability section and a Rubric section of `results.md`.

### Acceptance of the instrument, declared before the run

`python3 docs/research/scripts/settling/analyze.py` prints, in Reliability, each line below as met
or not met with its number. The instrument is **accepted** for the endpoint when all four hold:

- α ≥ 0.67 on d1 across the four model raters over the 26 `v2.0` and `v2.1` pages (the pooled α
  over 52 is printed beside it and does not gate);
- α ≥ 0.5 on d1 between the two family means over the same 26 pages (two raters, so a lower floor;
  this is what keeps a pass from being one family agreeing with itself);
- Spearman ρ ≥ 0.6 (point estimate; the interval is printed) between the user and the panel mean
  on d1 over the sixteen anchor pages;
- retest α ≥ 0.67 on the 7-point items for every rater.

Reported regardless: α and ρ per item and per page set, the family split, the position effect, the
implied-pairwise κ, the c5 and c3 precision and recall — so the reader sees which items carry the
agreement and which do not.

Three outcomes, declared:

1. **Accepted**: all four lines hold. The grammar reading runs as confirmatory.
2. **Partial**: d1's α over the 26 pages is in [0.4, 0.67), or the family-mean α or the retest α
   misses, or ρ misses with α holding. The items that clear α are usable readings (defects, brief
   fit, the aesthetics facets that pass); d1 is not, and quality claims about the endpoint stay
   unclaimable. The grammar reading runs as exploratory and is labelled so. The branch for "α holds,
   ρ misses" — the panel reliable but not tracking the user — is the Deferred few-shot anchoring,
   as a new pre-registered round with the example pages excluded from ρ, never a revision inside
   this one.
3. **Stopped**: d1's α over the 26 pages is under 0.4 after the one revision below. The rubric is
   not better than the forced choice on the endpoint at this level of craft; the result is recorded
   here and in the settling spec, and the acceptance instrument for the next grammar change is the
   settling fit rating plus the mechanical gate.

One rubric-wording revision is allowed, before the user rates, and only on a1–a4, d1 or e1 (the
items rated on every page; the b-items at eight pages a brief and the rare binary c-items cannot
trip a floor for reasons that are ambiguity, and are reported only): if the panel's first pass
shows one of those items under α 0.4, its wording may be revised once and the panel re-rates every
brief on that item alone — the eight pages in view again, the other items' first-pass ratings final
— with the old and new wording and both α recorded in the Decision Log. Thresholds do not move, and
no wording change is expected to rescue a weighting disagreement on d1; if that is what the first
pass shows, the revision is not spent on it.

### The grammar reading (confirmatory only when the instrument is accepted)

Input: the `v2.1` − `v2.0` paired table, the per-rater signs, and the raters' evidence clauses.

0. **The confirmation gate.** The loss is confirmed only if the paired d1 difference's interval
   excludes zero and at least three of the four raters agree on its sign on a majority of pairs.
   Otherwise the finding is "no loss detectable at thirteen pairs" (with the minimum detectable
   difference stated) and steps 1–4 run as exploratory, labelled so, on whatever the items show.
1. Which items carry the difference — d1, the aesthetics facets, brief fit, or defects — and on
   which briefs (consoles against narrative pages; the pairs where every rater put one arm ahead).
2. The defects column, read as an outcome of the arm first: a 2.1 page that lost on a clipped table
   may have clipped because the grammar's density rules put the table there. The covariate read —
   the paired difference with c1–c5 held — is secondary and labelled so; it separates "the grammar
   produced the clip" from "one build clipped".
3. Conventionality: the correlation of e1 with d1 across raters, within brief and *within arm* (the
   unconventional pages are mostly the 2.1 pages, so across arms the correlation is the arm). If the
   panel penalises leaving the default shell as such, the loss is partly the price of the doctrine's
   intent and is reported as that; if it does not, the loss is craft.
4. The evidence clauses, read pairwise: for each pair and each item where |Δ| ≥ 2 for at least three
   raters, the 2.0 and 2.1 clauses side by side, coded against a code list frozen before the
   reading — the grammar's rules from `2026-09-05-composition-grammar.md` (the console forms, the
   main-plus-rail band, no stat row, no side region, the density rules) *and* the non-grammar
   changes in the 2.0 → 2.1 diff (composition QA, imagery as content, candidates and priors) *and*
   "build defect" and "other". Two coders, both fresh agents from different families (neither the
   grammar's author nor this session), agreement between them reported; a code that only one coder
   assigns is not a finding.

Output: a Findings section in this spec, the composition-grammar spec's Outcomes amended, and — if
the loss is confirmed and coded — the named rule change to try, which becomes the next grammar wave
with this instrument as its acceptance. If it is not confirmed, the settling spec's reading is
amended to "not detectable" and the next grammar wave is chosen on fit and defects.

### Cost, declared

Recapture: minutes. Model panel: 4 pilot runs (which count), 24 more, 8 retests, at about
0.1–0.15 M tokens each (32 images), 4–5 M tokens; a wording revision, if spent, re-rates one item on
every brief, up to 28 short runs more. Two coders for the clause reading. UIClip: CPU minutes after
a one-time download. The user: under thirty minutes. Scripts and analysis: a working day.

## Files

- This spec.
- `docs/research/scripts/settling/measure.mjs` — the fixed capture protocol and the tiles;
  `rubric.py` (new) — the rater prompt per brief with the seeded shuffle, and the items;
  `rate.py` — the `/rubric` rating page for the user; `uiclip.py` (new) — the UIClip column;
  `analyze.py` — α, ρ, retest, per-arm intervals, the paired table.
- `figma-design-workspace/settling/` (gitignored): captures, `rubric/<rater>/<brief>[-retest].json`,
  `rubric-human.jsonl`, `uiclip.json`.
- Committed evidence: `docs/research/data/2026-09-05-settling/rubric/…`, `rubric-human.jsonl`,
  `uiclip.json`, `results.md` (extended).

## Findings

The grammar reading, run as **exploratory**: the instrument's outcome is Partial (below), so nothing
here is a confirmatory claim. Panel of four model raters, 52 pages, 13 `v2.1` − `v2.0` pairs.

**0. The confirmation gate does not pass.** The paired d1 difference is −0.33 [−1.08, 0.46] and
three or more raters carry its sign on 6 of 13 pairs. The smallest difference 13 pairs could have
detected is 0.81 of a point. So the settling run's reading — two of three forced-choice judges
preferring 2.0 to 2.1 — is *not detectable* here, not confirmed and not refuted. Per arm, d1 on the
panel: `none` 4.71, `v1.1` 4.96, `v2.0` 5.15, `v2.1` 4.83, every interval overlapping.

**1. Which items move.** Brief fit is flat (−0.07). Defects are slightly higher under 2.1 (+0.21
[−0.21, 0.65]). The VisAWI-S aesthetics total is lower under 2.1 by 0.30 [−0.58, 0.01], at the edge
of detectability, carried by variety (a2 −0.37) and colour (a3 −0.31); and per arm the aesthetics
total falls with every version of the doctrine — `none` 5.78, `v1.1` 5.55, `v2.0` 5.40, `v2.1`
5.11 — again on a2 (5.60 → 4.60) and a3 (5.85 → 4.71), while a1 (everything goes together) and a4
(professionally designed) hold. Conventionality moves as the grammar intends: e1 −1.27 [−2.21,
−0.37] on the pairs, and per arm 6.08, 4.29, 4.79, 3.52.

**2. Defects as the arm's outcome.** Of the four pairs where three or more raters put 2.0 ahead on
d1, two are 2.1 pages with a capture-visible defect — fleet·A (49e6cb, the over-wide sheet, +2.0
defects) and pharmacy·A (f344b7, clipped records, +1.0) — and two are brief-fit misses on the 2.1
page: rebate·A (7acb2c states eligibility after the first screen; b1 −2.0) and compare·A (d178d1
never shows a recorded pick; b4 −1.75). The one pair where three or more raters put 2.1 ahead
(rail·B, +2.50) is 2.0's clipped roster (92cba1). Where d1 moved by two or more points for three
raters, the reason on record is a defect or a missing brief region on one side, never the
composition as such. Whether the grammar's density rules *produce* the clips is what the clause
coding (step 4) reads.

**3. Conventionality does not cost deliverability.** Within arm, the panel's e1 against its d1 is
+0.41 (`none`), −0.40 (`v1.1`), −0.05 (`v2.0`), −0.28 (`v2.1`); within brief, −0.15 on average
over the seven briefs. The panel does not penalise leaving the default shell as such; if anything,
within a brief the less conventional page rates a little higher. The grammar's loss, where there is
one, is not the price of its intent.

**4. The clause coding.** Pending — two coders on the six qualifying cells.

**The no-skill hold** (settling Decision Log 2026-09-09) is not decided at this sample: `none` −
`v1.1` on d1 is −0.25 [−0.88, 0.44]; on defects `none` carries more, +0.37 [0.00, 0.69]. Per brief,
`none` is the worst arm on the three consoles (fleet 3.88, pharmacy 3.88, rail 3.75) and the best on
library (6.25) and among the best on hardware and compare: the no-skill deficit the user saw is a
console deficit.

**What the next grammar wave should be, on this reading.** Not a composition-rule change: the
composition's intended effect is confirmed and is not penalised. The losses on record are (a) a
defect class — over-wide sheets and clipped records, two of the three worst 2.1 pages — which is
composition QA, and (b) two brief-fit misses that a first-screen check would catch (the brief's
eligibility or pick region placed late or absent). And a token-level question for the stance layer:
the panel reads each version's colour restraint as a less attractive, less varied page.

## Decision Log

- Decision: A pointwise, anchored rubric answered in the brief's own context (all eight pages in
  view), not a pairwise choice.
  Rationale: pairwise with position swap would have measured the flip rate but kept the coin flip on
  near-equal pairs, doubled the cost, and still yielded one number per pair and nothing per
  dimension; a within-brief ranking gives one order per rater and no items, and carries the same
  presentation-order bias. Pointwise items in context are what the settling fit rater used, the one
  instrument that was consistent, and what UICrit found workable for models.
  Date/Author: 2026-09-09, Claude.

- Decision: VisAWI-S as the aesthetics block, wording adapted per its manual.
  Rationale: a validated scale with taste-neutral items beats any wording written here; the full
  eighteen-item VisAWI would cost the user four times the answers for a total the short form
  approximates.
  Date/Author: 2026-09-09, Claude.

- Decision: Deliverability (d1, 7-point, anchored) is the endpoint the next grammar change is held
  to; aesthetics, brief fit and defects explain it rather than define it.
  Rationale: the user's choice, for continuity with the settling question. Rejected: a composite of
  all items (a weighting nobody validated), VisAWI-S alone (does not ask whether the page does the
  brief's job).
  Date/Author: 2026-09-09, the user.

- Decision: Conventionality (e1) is rated and reported beside quality, never folded into it.
  Rationale: the user's choice. It lets the diagnosis test whether the grammar's loss is the price
  of leaving the default shell without letting the doctrine's own goal leak into the quality score.
  Date/Author: 2026-09-09, the user.

- Decision: The user rates an anchor set of sixteen pages (pharmacy and library), the panel rates
  all 52.
  Rationale: the user's choice of about thirty minutes over two hours or none. The anchor briefs are
  the two where the settling judges disagreed most, so the instrument is tested where the last one
  failed; rail and hardware, where they agreed, would have flattered it.
  Date/Author: 2026-09-09, the user (time); Claude (which briefs).

- Decision: Four model raters, two families by two rungs, each rating every brief; retest on the
  anchor briefs.
  Rationale: α over two raters is unstable and one rater per family cannot separate family bias from
  rater noise; more than four would cost more than it adds when the gateway offers two families.
  Date/Author: 2026-09-09, Claude.

- Decision: One capture set for every rater — first viewport taken at scroll 0 before the
  scroll-through, the full page, and two native-resolution tiles — regenerated for all 52 builds
  before rating.
  Rationale: the settling judges saw different things, and the full page at reduced scale hides the
  text the c-items ask about. Rejected: tiles on demand (raters would again see different things);
  every tile (up to nine images per page, 72 per prompt).
  Date/Author: 2026-09-09, Claude.

- Decision: UIClip is a reported column, not a panel member.
  Rationale: it is a different kind of instrument (a contrastive score, no items), and its agreement
  with the panel is itself a finding; it closes the settling spec's deferred "UIClip channel" at the
  cost of a CPU run.
  Date/Author: 2026-09-09, Claude.

- Decision: Acceptance floors α 0.67, ρ 0.6, retest 85 %.
  Rationale: the literature's tentative floor for α (0.8 is the strong bar and is reported), the
  practitioner floor for judge-to-human agreement, and the consistency the position-debiased
  pairwise judges reach. Rejected: 0.8 as the gate — it would fail a usable instrument on 52 pages
  and four raters.
  Date/Author: 2026-09-09, Claude.

- Decision: One pre-registered rubric-wording revision, on items under α 0.4 in the panel's first
  pass, before the user rates.
  Rationale: a single ambiguous wording would sink the run if no revision were allowed; unlimited
  revision is fitting the rubric to the answer. Wording only; thresholds never move.
  Date/Author: 2026-09-09, Claude.

- Decision: The grammar reading uses this run's data on the same 52 builds; no new builds.
  Rationale: the user's order (instrument first, then the diagnosis) and the settling spec's
  premise that the diagnosis, not a doctrine change, comes next.
  Date/Author: 2026-09-09, the user.

- Decision: The one pre-registered wording revision is spent on e1, and on nothing else. First
  wording: "How conventional is this page for its brief?" [1 this page looks like nothing I have
  seen for this kind of brief; 7 this is the default page for this kind of brief], α 0.35 pooled and
  0.25 on the 2.x pages, and the Claude pair at −0.05 on that set. Revised wording: "How closely
  does this page follow the standard layout for its kind of page — for a console, a left sidebar
  or top tabs, a row of summary tiles, then tables or panels; for a public page, a hero, a row of
  three feature cards, then stacked sections? Judge the structure, not the colours or the type."
  [1 departs from the standard layout for its kind in its main structure; 4 the standard shell with
  one departure; 7 the standard layout for its kind throughout]. The panel re-rates every brief on
  e1 alone, the same pages in the first pass's order, from the first viewport and the full page
  (a structural read; the tiles serve the c-items); the first pass's e1 is kept as e1_v1 and both
  α are printed. The user's form carries the revised wording; the user had not rated.
  Rationale: of the four items under 0.4 on the 2.x pages (a1, a2, a3, e1), the three aesthetics
  items are the published VisAWI-S wording, their pooled α is 0.43–0.49, and their fall on the 2.x
  set is range restriction on competent pages plus rater level — not ambiguity a rewrite would
  cure, and a rewrite would forfeit the validated anchor. e1 was this spec's own wording, is
  ambiguous between genre-typical structure and visual familiarity, and is the item the grammar
  reading's third step depends on. Thresholds unchanged; d1 (0.46) could not trip the revision and
  was not offered it.
  Date/Author: 2026-09-10, Claude.

- Decision: The independent critique's findings, adopted before any rating (the spec's second
  revision): the reliability gate reads d1's α over the 26 `v2.0` and `v2.1` pages and between the
  two family means, not only pooled over 52; the grammar reading has a confirmation gate and a
  stated minimum detectable difference, and no longer presupposes the loss; d1 is anchored by
  rework category; the b-items are single fact each on a 0–2 presence scale with a tone item where
  the brief states one; the c-items are scoped to the captures and checked against their mechanical
  ground truth; the user rates six items a page plus four retest pages; retest is chance-corrected;
  the acceptance has three declared outcomes and the revision rule names which items can trip it;
  the clause reading is pairwise, coded against a frozen list that includes non-grammar codes, by
  two coders; a pilot brief runs first; the position effect and the implied-pairwise κ are reported.
  Rationale: each is a way the first draft could have fooled itself — pooled α certifying agreement
  the within-brief comparison never uses, a pass carried by one family agreeing with itself, a
  "diagnosis" of a loss an instrument at chance had reported, a floor a random rater passes, an
  overloaded human form, and a mapping of free text to rules with no method. Rejected from the
  critique: the shared per-brief client statement as d1's anchor (stronger than the rework anchor
  but whoever writes it can tilt the result; held in Deferred for the case the rework anchor is not
  enough).
  Date/Author: 2026-09-09, Claude, from the doperpowers:critique review.

## Surprises & Discoveries

- Observation: The panel's first pass (28 runs, four raters, 52 pages, 2026-09-10). Brief fit is
  reliable (α 0.83 pooled, 0.86 on the 26 2.x pages); defects 0.56; aesthetics 0.57 pooled but 0.37
  on the 2.x pages; d1 0.48 pooled and 0.46 [0.21–0.64] on the 2.x pages, under the 0.67 floor;
  e1 0.35 / 0.25. The GPT pair (one model at two efforts) agrees with itself at 0.87 on d1, the
  Claude pair at 0.34, the two family means at 0.43. What the α hides: the raters order the pages
  within a brief alike — mean within-brief Spearman ρ on d1 0.65 for same-family pairs and 0.66
  across families — and differ in level: mean d1 4.35 (astra-high) to 5.58 (claude-sonnet), and
  the lenient rater counts a third as many defects. So the d1 disagreement is mostly scale use,
  not ordering, which the ordinal α charges in full and the pre-registered floor does not forgive.
  Also: c4 (spacing inconsistency) is unreadable at α 0.08; c3 is too rare to measure on the 2.x
  pages; retest α per rater 0.63 (claude-opus) to 0.89 (astra-medium), with the 0.67 floor missed
  by one rater.
  Evidence: `results.md`, R, the family split and the level-or-order tables.

- Observation: Recapturing all 52 builds under the fixed protocol changed no gate verdict and moved
  one contrast rate by 0.02 (fleet `none` A, 1.0 → 0.979, more text rendered after the font wait);
  no page scrolled itself on load or after the reset, so the two settling first-viewport artifacts
  came from the scroll-through, which the new order (first viewport before the walk) removes. Two
  captures are wider than 1440 and both are `v2.1` pages: library 672565 at 2760 px (the load-time
  overflow read false) and fleet 49e6cb at 1471 px (already a gate failure). Five short consoles
  have no tile beyond the first viewport, four have one.
  Evidence: the diff of `measurements.json` before and after; `captureWidth` per build.

## Deferred

- Few-shot anchoring of the model raters with the user's own ratings (UICrit's 55 % gain), if the
  human–panel ρ misses the floor: a new pre-registered round with two of the user's rated pages
  shown as examples and excluded from ρ.
- A shared client for d1: a frozen per-brief statement of the client's priorities, written from the
  brief's nouns by a writer who has not read the grammar and reviewed by the user, so every rater
  delivers to the same client. Stronger than the rework anchor, and it carries a leak — the writer
  can tilt the result — that would have to be owned. The next try if d1 still splits on taste.
- A third model family for the panel, if one becomes reachable.
- Pexels or Openverse imagery in the hardware builds (the imagery path, `2026-09-08-imagery-path.md`)
  so hardware b1 can be met at all; this run reads the builds as they are.

## Outcomes & Retrospective

**The instrument: Partial.** Against the four declared lines, over the 26 `v2.0` and `v2.1`
pages: d1's α across the four raters is 0.46 [0.21, 0.64] (floor 0.67; pooled over 52 it is 0.48);
between the two family means 0.43 (floor 0.5); retest α per rater 0.54–0.70, one of four over 0.67
(within ±1 on 88–93 % of repeated ratings); the user's ρ is *pending*. d1's α sits in the Partial
band [0.4, 0.67) after the one revision, which was spent elsewhere, so the outcome is Partial
whatever ρ returns: the items that clear α are usable readings, d1 is not, and the grammar reading
ran as exploratory.

What clears the floor: brief fit (α 0.83 pooled, 0.86 on the 2.x pages) and the revised
conventionality item (0.71 / 0.67, between families 0.72). What sits between: the VisAWI-S total
(0.57 pooled, 0.37 on the 2.x pages — range restriction on competent pages), defects (0.56), d1
(0.48). What does not read: c4 (spacing inconsistency, 0.08) and c3 (too rare). The panel's c5 finds
both over-wide pages with no false positive by majority; one rater (claude-sonnet) sees neither.
Position in the shuffle has no effect on any item.

Why d1 misses: not order but level. The raters order pages within a brief alike — mean pairwise
Spearman ρ on d1 0.65 for same-family pairs, 0.66 across families — and sit at different heights on
the scale, 4.35 (astra-high) to 5.58 (claude-sonnet), the lenient rater also counting a third as
many defects. α charges that gap in full. The GPT pair is one model at two efforts and agrees with
itself at 0.87; the Claude pair at 0.34, on level. A per-rater calibration (a fixed anchor set, or
the user's ratings as few-shot examples, Deferred) is the next try for the endpoint; the floors
themselves do not move.

The one wording revision, spent on conventionality, worked: α 0.35 → 0.71 pooled and 0.25 → 0.67
on the 2.x pages, with the Claude pair from −0.05 to 0.73 — the first wording had asked two
questions (structural typicality and visual familiarity) and the raters had answered different
ones.

Pointwise against pairwise: each rater's d1, read as a verdict on the settling run's 78 pairs,
agrees with the user's forced choices at κ −0.12 to 0.28, and astra-medium's implied verdicts agree
with its own earlier forced choices at only 0.21 (claude-opus's with its own at 0.67). The two
formats do not elicit the same judgment from the same model; the pre-registered comparison the
critique asked for says the settling run's forced choice and this rubric are different instruments,
not two readings of one.

UIClip does not track the panel: ρ −0.08 with d1 and 0.05 with aesthetics over 52 pages. Its per-arm
means put `v2.1` lowest on both captures; as a relevance-plus-quality score against the brief's
text it is reading something else, and it is retired from this instrument.

**The user's anchor — pending.** ρ against the panel mean on d1 over the 16 anchor pages, the
interval, the mean absolute difference, and the user's own four-page retest, written when the
ratings land.

**Retrospective.** Three things the settling run lacked made this run readable: items that name a
fact (brief fit at 0.83 where the forced choice was at chance), one capture set (both over-wide
pages found by the panel majority), and a pilot (the string-valued numbers were caught on the first
brief). Two things the design got wrong were caught by the critique before the run — pooled α would
have certified agreement the within-brief comparison never uses, and a "diagnosis" of a loss an
instrument at chance had reported — and one thing the critique predicted came true: d1 splits on
the middle pages, and a wording revision could not have moved it. The cost of the endpoint's miss
is a level effect that a calibration step handles; the cost of the settling run's miss was the
question itself. Runs: 28 first pass, 8 retests, 28 single-item re-rates, four pilot, two coders;
about 5.5 M subagent tokens; the user under thirty minutes.

## Revision Notes

- 2026-09-09: created from the settling experiment's Outcomes and the user's order for the next work;
  the rubric, raters, captures, acceptance and stop declared before any rating; the user's three
  choices (anchor set, d1 as endpoint, conventionality reported) recorded.
- 2026-09-09 (second revision, before any rating): the independent critique's findings adopted —
  see the Decision Log; the b-items, d1's anchors, the user's form, the reliability lines, the
  three outcomes, the grammar reading's gate and coding method all changed.
- 2026-09-10: the panel's first pass and retests in (Surprises); the one wording revision spent on
  e1 (Decision Log); the level-or-order diagnostic added to the report beside the family split.
- 2026-09-10 (later): the e1 re-rate in; Outcomes written for the panel side (Partial), the
  grammar reading written as exploratory (Findings); the user's anchor and the clause coding
  marked pending.
