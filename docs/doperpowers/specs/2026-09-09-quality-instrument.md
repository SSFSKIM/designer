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

After it, a quality claim is a number with a reliability behind it — "2.1 is preferred to 2.0 on
deliverability by 0.4 of a point, panel α 0.71, human–panel ρ 0.66" — and the composition grammar's
quality loss (`v2.1` against `v2.0`, the reading two of three settling judges shared) is located in
named rubric items, on named briefs, with the raters' evidence pointing at named grammar rules. The
next grammar change is then held to this instrument, not to a coin flip.

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
  facet, 7-point agreement) validated on 1,673 raters, convergent with overall appeal and divergent
  from perceived usability and content quality. The manual allows adapting the wording to other
  interfaces. It gives taste-neutral aesthetics items that did not have to be invented here.
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

**B. Brief fit — three statements per brief, written from the brief's own nouns and frozen here**
[1 … 7 agreement]

| brief | b1 | b2 | b3 |
|---|---|---|---|
| rail | A dispatcher can see every live train's position and state without scrolling. | Delay exceptions are separated from the routine and read before it. | Crew hours and maintenance windows are on the page as values and times, not only as headings. |
| fleet | Open defects are listed by vehicle, and the overdue inspections are visibly distinguished. | Parts on order are on the page with an expected date or status each. | The workshop's day (bays, jobs, times) is readable as a schedule. |
| pharmacy | Stock levels by drug are a table with quantities and a par or reorder level. | Expiring lots and controlled-substance counts are each visible as their own set. | Pending orders are on the page with a status each. |
| compare | The three suppliers are compared on the same criteria in one structure. | Price per axle, lead time, warranty and on-site fitting are each visible for each supplier. | There is a control to pick a supplier, and the page shows that a pick is recorded. |
| rebate | A resident can tell within the first screen whether they qualify. | The rebate's value is stated as amounts with its conditions. | The approved installers are listed, and the one application form is reachable from the page. |
| library | A parent can find the sign-up within the first screen. | Weekly book lists are on the page as lists of titles. | An event calendar with dates is on the page, and the page reads as for children and their parents without being garish. |
| hardware | Featured tools are shown with prices, and the goods are pictured (a photograph or a drawing). | Seasonal project guides are on the page. | In-store pickup is explained, and the page reads as practical and trustworthy rather than startup-slick. |

**C. Defects — five observations** [0 not seen, 1 seen], summed to a count 0–5
- c1 Content clipped or cut off by its container.
- c2 Text too small or too faint to read at this size.
- c3 An empty, placeholder or broken region (an image slot without an image, lorem, template text).
- c4 Spacing or alignment inconsistent between like elements.
- c5 The layout is wider than the viewport, or scrolls sideways.

**D. Deliverability — the endpoint** [1 I would not deliver this and would start over; 4 deliverable
after real rework; 7 I would deliver this as it is]
- d1 Would you deliver this page to the client who wrote the brief?

**E. Conventionality — reported beside quality, never in it** [1 this page looks like nothing I have
seen for this kind of brief; 7 this is the default page for this kind of brief]
- e1 How conventional is this page for its brief?

A model rater gives one clause of evidence per item; the user rates without evidence. Fifteen
answers per page.

### Raters

- **The model panel.** Four blinded raters, two model families by two rungs: `astra-medium` and
  `astra-high` (GPT), `claude-opus` and `claude-sonnet` (Claude), the only two families the gateway
  offers. One brief per prompt (eight pages by four captures, 32 images), every brief for every
  rater: 28 runs. The page order in each prompt is a shuffle seeded by (rater, brief) and recorded
  in the output.
- **Retest.** Every rater repeats the two anchor briefs in a second shuffle: eight more runs.
- **The user** rates the *anchor set* — pharmacy and library, sixteen pages — on the rating page,
  same captures, same items, order seeded and recorded. About thirty minutes. These two briefs are
  where the settling judges disagreed most (3 of 12 and 4 of 12 pairs), so the instrument is tested
  where the last one failed.
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
receives the same four files per page.

### Aggregation and reliability

- Per item: Krippendorff's α across the four model raters over all 52 pages (ordinal for the 7-point
  items, nominal for c1–c5); and α across all five raters over the anchor set.
- Human–panel: Spearman ρ between the user's rating and the panel mean, per item, over the sixteen
  anchor pages; mean absolute difference on the 7-point items beside it.
- Retest: per rater, the share of repeated 7-point ratings within ±1 and of repeated c-items equal.
- Page scores: d1 = panel mean; aesthetics = mean of a1–a4 (the VisAWI-S total); brief fit = mean of
  b1–b3; defects = mean count; e1 = panel mean.
- Per arm: mean and a bootstrap 95 % interval (resampling pages) over its thirteen pages, per item
  and per composite, pooled and per brief.
- `v2.1` − `v2.0`: paired by (brief, seed), thirteen pairs, the difference on every item with its
  interval. This table is the diagnosis's input.
- The no-skill hold (settling Decision Log 2026-09-09): `none` against `v1.1` on d1 and defects,
  reported as the number that confirms or overturns the hold.

`analyze.py` prints all of this in a Reliability section and a Rubric section of `results.md`.

### Acceptance of the instrument, declared before the run

The instrument is accepted when `python3 docs/research/scripts/settling/analyze.py` prints, in
Reliability:

- α ≥ 0.67 on d1 across the four model raters over 52 pages;
- α ≥ 0.67 on the VisAWI-S total (a1–a4 averaged per rater) across the panel;
- Spearman ρ ≥ 0.6 between the user and the panel mean on d1 over the sixteen anchor pages;
- retest within ±1 on at least 85 % of repeated 7-point ratings, per rater.

Reported regardless: α and ρ per item, so the reader sees which items carry the agreement.

One rubric revision is allowed, before the user rates: if the panel's first pass shows an item with
α < 0.4, that item's wording may be revised once and the panel re-run on it, with the old and new
wording and both α recorded in the Decision Log. Thresholds do not move.

**Stop.** If d1's α is under 0.4 after that one revision, the instrument is not better than the
forced choice at this level of craft; the result is recorded here and in the settling spec, quality
claims stay unclaimable, and the acceptance instrument for the next grammar change is the settling
fit rating plus the mechanical gate, not this rubric.

### The diagnosis (executed only after acceptance)

Input: the `v2.1` − `v2.0` paired table and the raters' evidence clauses. Reading, in order:

1. Which items carry the loss — d1 alone, the aesthetics facets, brief fit, or defects — and on
   which briefs (consoles against narrative pages; the pairs where every rater put 2.0 ahead).
2. Whether the loss survives the defects column: a 2.1 page that lost on a clipped table or an
   over-wide sheet (672565) is a build defect, not a grammar effect; the paired difference is
   re-read with c1–c5 as a covariate.
3. Whether e1 explains it: within brief, the correlation of e1 with d1 across raters says whether
   the panel penalises leaving the default shell as such. If it does, the loss is partly the price
   of the doctrine's intent and is reported as that; if it does not, the loss is craft.
4. The evidence clauses on the losing items for every 2.1 page, mapped to the grammar's rules in
   `2026-09-05-composition-grammar.md` (the console forms, the main-plus-rail band, no stat row, no
   side region) and to the composition lines of each page's DESIGN.md: which rule the raters' words
   point at.

Output: a Findings section in this spec, the composition-grammar spec's Outcomes amended, and the
named rule change to try, which becomes the next grammar wave with this instrument as its
acceptance.

### Cost, declared

Recapture: minutes. Model panel: 28 runs plus 8 retests at about 0.1–0.15 M tokens each (32
images), 4–5 M tokens. UIClip: CPU minutes after a one-time download. The user: about thirty
minutes. Scripts and analysis: a working day.

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

Pending — written after the diagnosis, once the instrument is accepted.

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

- Decision: The diagnosis reads this run's data on the same 52 builds; no new builds.
  Rationale: the user's order (instrument first, then the diagnosis) and the settling spec's
  premise that the diagnosis, not a doctrine change, comes next.
  Date/Author: 2026-09-09, the user.

## Surprises & Discoveries

(none yet)

## Deferred

- Few-shot anchoring of the model raters with the user's own ratings (UICrit's 55 % gain), if the
  human–panel ρ misses the floor: a second pass with two of the user's rated pages shown as examples.
- A third model family for the panel, if one becomes reachable.
- Pexels or Openverse imagery in the hardware builds (the imagery path, `2026-09-08-imagery-path.md`)
  so hardware b1 can be met at all; this run reads the builds as they are.

## Outcomes & Retrospective

Pending — written at finish.

## Revision Notes

- 2026-09-09: created from the settling experiment's Outcomes and the user's order for the next work;
  the rubric, raters, captures, acceptance and stop declared before any rating; the user's three
  choices (anchor set, d1 as endpoint, conventionality reported) recorded.
