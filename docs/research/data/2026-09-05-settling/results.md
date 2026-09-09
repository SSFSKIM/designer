# Settling experiment — results

Builds measured: 52 of 52. Judgments: 78 (human), 78 (astra-medium), 78 (claude-opus). Topology: yes. Fit ratings: 52.

## Q — pairwise quality (human, blinded; the primary endpoint)

78 judgments.

| arm A | arm B | A wins | n | rate | 95 % Wilson |
|---|---|---|---|---|---|
| none | v1.1 | 5 | 13 | 0.38 | 0.18–0.64 |
| none | v2.0 | 10 | 13 | 0.77 | 0.50–0.92 |
| none | v2.1 | 7 | 13 | 0.54 | 0.29–0.77 |
| v1.1 | v2.0 | 8 | 13 | 0.62 | 0.36–0.82 |
| v1.1 | v2.1 | 9 | 13 | 0.69 | 0.42–0.87 |
| v2.0 | v2.1 | 6 | 13 | 0.46 | 0.23–0.71 |

Pooled Bradley–Terry log-strength per arm (mean over briefs with judgments; 0 = brief average):

| arm | mean log-strength | briefs | builds judged |
|---|---|---|---|
| none | -0.64 | 7 | 13 |
| v1.1 | -0.49 | 7 | 13 |
| v2.0 | -1.40 | 7 | 13 |
| v2.1 | -1.59 | 7 | 13 |

## Q2 — the model judge (astra-medium, blinded; secondary)

78 judgments.

| arm A | arm B | A wins | n | rate | 95 % Wilson |
|---|---|---|---|---|---|
| none | v1.1 | 6 | 13 | 0.46 | 0.23–0.71 |
| none | v2.0 | 3 | 13 | 0.23 | 0.08–0.50 |
| none | v2.1 | 4 | 13 | 0.31 | 0.13–0.58 |
| v1.1 | v2.0 | 3 | 13 | 0.23 | 0.08–0.50 |
| v1.1 | v2.1 | 5 | 13 | 0.38 | 0.18–0.64 |
| v2.0 | v2.1 | 7 | 13 | 0.54 | 0.29–0.77 |

Pooled Bradley–Terry log-strength per arm (mean over briefs with judgments; 0 = brief average):

| arm | mean log-strength | briefs | builds judged |
|---|---|---|---|
| none | -1.84 | 7 | 13 |
| v1.1 | -1.81 | 7 | 13 |
| v2.0 | -0.58 | 7 | 13 |
| v2.1 | -0.53 | 7 | 13 |

## Q3 — the third judge (claude-opus, blinded; secondary)

78 judgments.

| arm A | arm B | A wins | n | rate | 95 % Wilson |
|---|---|---|---|---|---|
| none | v1.1 | 9 | 13 | 0.69 | 0.42–0.87 |
| none | v2.0 | 8 | 13 | 0.62 | 0.36–0.82 |
| none | v2.1 | 10 | 13 | 0.77 | 0.50–0.92 |
| v1.1 | v2.0 | 4 | 13 | 0.31 | 0.13–0.58 |
| v1.1 | v2.1 | 6 | 13 | 0.46 | 0.23–0.71 |
| v2.0 | v2.1 | 9 | 13 | 0.69 | 0.42–0.87 |

Pooled Bradley–Terry log-strength per arm (mean over briefs with judgments; 0 = brief average):

| arm | mean log-strength | briefs | builds judged |
|---|---|---|---|
| none | -0.43 | 7 | 13 |
| v1.1 | -1.66 | 7 | 13 |
| v2.0 | -0.74 | 7 | 13 |
| v2.1 | -1.88 | 7 | 13 |

## Q★ — majority of the three judges (the tiebreak adopted 2026-09-09)

78 judgments.

| arm A | arm B | A wins | n | rate | 95 % Wilson |
|---|---|---|---|---|---|
| none | v1.1 | 7 | 13 | 0.54 | 0.29–0.77 |
| none | v2.0 | 8 | 13 | 0.62 | 0.36–0.82 |
| none | v2.1 | 8 | 13 | 0.62 | 0.36–0.82 |
| v1.1 | v2.0 | 4 | 13 | 0.31 | 0.13–0.58 |
| v1.1 | v2.1 | 7 | 13 | 0.54 | 0.29–0.77 |
| v2.0 | v2.1 | 9 | 13 | 0.69 | 0.42–0.87 |

Pooled Bradley–Terry log-strength per arm (mean over briefs with judgments; 0 = brief average):

| arm | mean log-strength | briefs | builds judged |
|---|---|---|---|
| none | -0.55 | 7 | 13 |
| v1.1 | -1.55 | 7 | 13 |
| v2.0 | -0.79 | 7 | 13 |
| v2.1 | -1.82 | 7 | 13 |

Unanimous on 28 of 78 pairs; the human is outvoted on 18.

### H2 and the stop rule's quality clause, per judge

| judge | v2.1 over v1.1 | v2.1 over none | H2 (≥ 45 % and ≥ 60 %) | stop clause (< 35 %) |
|---|---|---|---|---|
| human | 4/13 (0.31) | 6/13 (0.46) | not met | fires |
| astra-medium | 8/13 (0.62) | 9/13 (0.69) | met | does not fire |
| claude-opus | 7/13 (0.54) | 3/13 (0.23) | not met | does not fire |
| majority | 6/13 (0.46) | 5/13 (0.38) | not met | does not fire |

### Agreement between the judges

**human and astra-medium.** Pairs judged by both: 78. Same winner on 41 (0.53); Cohen's κ 0.03. Per brief: compare 2/6, fleet 8/12, hardware 10/12, library 4/12, pharmacy 3/12, rail 9/12, rebate 5/12.

**human and claude-opus.** Pairs judged by both: 78. Same winner on 47 (0.60); Cohen's κ 0.17. Per brief: compare 4/6, fleet 5/12, hardware 9/12, library 8/12, pharmacy 6/12, rail 8/12, rebate 7/12.

**astra-medium and claude-opus.** Pairs judged by both: 78. Same winner on 46 (0.59); Cohen's κ 0.14. Per brief: compare 2/6, fleet 7/12, hardware 11/12, library 8/12, pharmacy 5/12, rail 7/12, rebate 6/12.

### The model judge against itself

Its first run (six raters, one per brief, on a schedule that differed per process) overlaps the batch run on 70 pairs: same winner on 65 (0.93); Cohen's κ 0.85.

## R — reliability of the rubric

Model panel: 4 rater(s) — Claude claude-opus, claude-sonnet; GPT astra-high, astra-medium — over 52 of 52 pages, 26 of them v2.0 or v2.1. Anchor set (pharmacy and library): 16 of 16 pages rated by 4 rater(s); the user has not rated yet.

α is Krippendorff's — ordinal on the 7-point items, on the 0–2 brief-fit items and on the composites built from them, nominal on the 0/1 defect observations — read over three page sets: pooled over every rated page, over the v2.0 and v2.1 pages the grammar reading uses, and per brief averaged with each brief weighted by its pages (briefs at least two raters rated). Pooled α is inflated by between-brief level differences the within-brief comparison never touches. d1 and the composites carry a 1000-resample interval; a b-item is a different statement in every brief and its α pools briefs by item index; t1 exists only where the brief states a tone; the user rates a1, a2, a3, a4, d1, e1 only.

| item | metric | α pooled | raters × pages | α on v2.0+v2.1 | raters × pages | α per brief, weighted | briefs |
|---|---|---|---|---|---|---|---|
| a1 | ordinal | 0.43 | 4 × 52 | 0.38 | 4 × 26 | 0.42 | 7 |
| a2 | ordinal | 0.44 | 4 × 52 | 0.21 | 4 × 26 | 0.42 | 7 |
| a3 | ordinal | 0.49 | 4 × 52 | 0.23 | 4 × 26 | 0.45 | 7 |
| a4 | ordinal | 0.48 | 4 × 52 | 0.49 | 4 × 26 | 0.50 | 7 |
| b1 | ordinal | 0.86 | 4 × 52 | 0.84 | 4 × 26 | 0.84 | 7 |
| b2 | ordinal | 0.71 | 4 × 52 | 0.92 | 4 × 26 | 0.81 | 7 |
| b3 | ordinal | 0.33 | 4 × 52 | 1.00 | 4 × 26 | 0.89 | 7 |
| b4 | ordinal | 0.87 | 4 × 44 | 0.86 | 4 × 22 | 0.89 | 6 |
| t1 | ordinal | 0.59 | 4 × 16 | 0.68 | 4 × 8 | 0.41 | 2 |
| c1 | nominal | 0.68 | 4 × 52 | 0.60 | 4 × 26 | 0.48 | 7 |
| c2 | nominal | 0.49 | 4 × 52 | 0.43 | 4 × 26 | 0.45 | 7 |
| c3 | nominal | 0.54 | 4 × 52 | -0.02 | 4 × 26 | 0.54 | 7 |
| c4 | nominal | 0.08 | 4 × 52 | 0.12 | 4 × 26 | 0.13 | 7 |
| c5 | nominal | 0.48 | 4 × 52 | 0.65 | 4 × 26 | 0.84 | 7 |
| d1 | ordinal | 0.48 [0.32–0.61] | 4 × 52 | 0.46 [0.21–0.64] | 4 × 26 | 0.42 [0.19–0.48] | 7 |
| e1 | ordinal | 0.71 | 4 × 52 | 0.67 | 4 × 26 | 0.62 | 7 |
| e1 (first wording, superseded by the revision) | ordinal | 0.35 | 4 × 52 | 0.25 | 4 × 26 | 0.30 | 7 |
| aesthetics (VisAWI-S total, a1–a4) | ordinal | 0.57 [0.39–0.69] | 4 × 52 | 0.37 [0.14–0.53] | 4 × 26 | 0.56 [0.30–0.61] | 7 |
| brief fit (mean of the brief's b-items, 0–2) | ordinal | 0.83 [0.73–0.91] | 4 × 52 | 0.86 [0.69–0.96] | 4 × 26 | 0.72 [0.55–0.80] | 7 |
| defects (count of c1–c5) | ordinal | 0.56 [0.40–0.68] | 4 × 52 | 0.56 [0.32–0.73] | 4 × 26 | 0.34 [0.16–0.47] | 7 |

### The family split

α within each model family and between the two family means, each family counted once, so a pass carried by one family agreeing with itself shows as a low between-family α. The 7-point items and the composites; the between column is ordinal over the family means.

| item | GPT α | Claude α | between families α | pages (pooled / v2.0+v2.1) |
|---|---|---|---|---|
| a1 | 0.64 / 0.45 | 0.55 / 0.88 | 0.48 / 0.36 | 52 / 26 |
| a2 | 0.79 / 0.65 | 0.34 / 0.08 | 0.49 / 0.21 | 52 / 26 |
| a3 | 0.77 / 0.74 | 0.52 / 0.47 | 0.50 / 0.04 | 52 / 26 |
| a4 | 0.81 / 0.85 | 0.40 / 0.47 | 0.49 / 0.48 | 52 / 26 |
| t1 | 0.94 / 0.91 | 0.24 / 0.29 | 0.71 / 0.73 | 16 / 8 |
| d1 | 0.87 / 0.77 | 0.34 / 0.32 | 0.45 / 0.43 | 52 / 26 |
| e1 | 0.92 / 0.87 | 0.70 / 0.73 | 0.72 / 0.63 | 52 / 26 |
| aesthetics (VisAWI-S total, a1–a4) | 0.82 / 0.72 | 0.57 / 0.56 | 0.61 / 0.34 | 52 / 26 |
| brief fit (mean of the brief's b-items, 0–2) | 0.94 / 0.93 | 0.78 / 0.86 | 0.89 / 0.91 | 52 / 26 |
| defects (count of c1–c5) | 0.91 / 0.85 | 0.33 / 0.36 | 0.64 / 0.67 | 52 / 26 |
(each cell is pooled / v2.0+v2.1.)

### Level or order

α penalises a rater who uses the scale higher or lower than the others as much as one who orders the pages differently. Two readings that separate the two, reported and not gating: each rater's mean level over the pages the panel rated, and the mean pairwise Spearman ρ between raters within a brief (order only, level removed), for pairs from the same family and pairs across families.

| rater | d1 | e1 | aesthetics (VisAWI-S total, a1–a4) | defects (count of c1–c5) | brief fit (mean of the brief's b-items, 0–2) |
|---|---|---|---|---|---|
| astra-high | 4.35 | 4.75 | 5.39 | 0.92 | 1.82 |
| astra-medium | 4.60 | 4.79 | 5.47 | 0.87 | 1.85 |
| claude-opus | 5.13 | 4.77 | 5.36 | 0.88 | 1.89 |
| claude-sonnet | 5.58 | 4.37 | 5.62 | 0.33 | 1.84 |

| item | within-brief ρ, same family | within-brief ρ, across families | pairs × briefs (same / across) |
|---|---|---|---|
| d1 | 0.67 | 0.64 | 14 / 28 |
| e1 | 0.77 | 0.61 | 14 / 28 |
| aesthetics (VisAWI-S total, a1–a4) | 0.73 | 0.59 | 14 / 28 |
| defects (count of c1–c5) | 0.66 | 0.42 | 11 / 23 |
| brief fit (mean of the brief's b-items, 0–2) | 0.87 | 0.78 | 11 / 22 |

### The user against the panel, over the anchor pages

The user has not rated yet.

### Retest — the same rater on the same pages a second time

α between the first and the second rating, units = (page, item) over the 7-point items. Chance-corrected, because a rater drawing at random among 4, 5 and 6 passes a within-±1 share of 85 % by arithmetic; the share is printed beside α, not in place of it. The user's second pass is reported the same way and is outside the gate.

| rater | pages repeated | 7-point ratings | retest α | within ±1 | c-item ratings | equal |
|---|---|---|---|---|---|---|
| astra-high | 16 | 104 | 0.58 | 0.90 | 80 | 0.96 |
| astra-medium | 16 | 104 | 0.70 | 0.93 | 80 | 1.00 |
| claude-opus | 16 | 104 | 0.54 | 0.88 | 80 | 0.90 |
| claude-sonnet | 16 | 104 | 0.65 | 0.90 | 80 | 0.96 |

### Position in the shuffle

Each rating centred by its (rater, brief) mean and regressed on the page's 1-based position in that rater's recorded order, pooled over raters and briefs; the interval resamples the runs. A slope of 0.1 means a page seen one place later is rated a tenth of a point higher.

| item | slope per position | 95 % CI | runs |
|---|---|---|---|
| a1 | -0.011 | -0.047–0.026 | 28 |
| a2 | 0.036 | -0.009–0.082 | 28 |
| a3 | 0.006 | -0.040–0.056 | 28 |
| a4 | -0.001 | -0.040–0.037 | 28 |
| b1 | -0.005 | -0.026–0.018 | 28 |
| b2 | -0.011 | -0.041–0.020 | 28 |
| b3 | -0.005 | -0.012–0.000 | 28 |
| b4 | 0.006 | -0.019–0.037 | 24 |
| t1 | 0.083 | -0.036–0.205 | 8 |
| c1 | -0.011 | -0.032–0.009 | 28 |
| c2 | -0.023 | -0.043–-0.001 | 28 |
| c3 | 0.020 | 0.008–0.035 | 28 |
| c4 | 0.022 | 0.007–0.037 | 28 |
| c5 | 0.000 | -0.010–0.009 | 28 |
| d1 | -0.030 | -0.095–0.040 | 28 |
| e1 | -0.005 | -0.101–0.094 | 28 |
| e1_v1 | -0.014 | -0.074–0.053 | 28 |

### Against the forced choice

Each rater's implied verdict on the settling run's 78 pairs, taken from its d1 (higher wins, an equal pair undecided), against the forced choices actually recorded. κ is Cohen's over the pairs both sides decided. A rater whose d1 contradicts its own earlier forced choice says pointwise and pairwise elicit different things.

| rater | pairs decided | κ vs the user (n) | κ vs astra-medium forced (n) | κ vs claude-opus forced (n) |
|---|---|---|---|---|
| astra-high | 64 of 78 | -0.08 (64) | 0.15 (64) | 0.35 (64) |
| astra-medium | 65 of 78 | -0.12 (65) | 0.21 (65) | 0.24 (65) |
| claude-opus | 61 of 78 | 0.28 (61) | 0.29 (61) | 0.67 (61) |
| claude-sonnet | 59 of 78 | -0.02 (59) | 0.19 (59) | 0.28 (59) |

### The c-items against their mechanical ground truth

c5 (wider than the viewport) against `overflowCapture` and c3 (empty or placeholder region) against the gate's `placeholder`, over the rated pages. The panel row is the strict majority of the raters that rated the page. A dash is a rate with no case in its denominator — with two over-wide pages in 52, recall is read from very few positives — and the mechanical truth is narrower than the item it is held against: `placeholder` matches template text, not every empty region a rater can see, so a false positive here is as likely to be the gate missing something as the rater inventing it.

| rating | rater | pages | truth positives | tp | fp | fn | precision | recall |
|---|---|---|---|---|---|---|---|---|
| c5 vs overflowCapture | astra-high | 52 | 2 | 2 | 0 | 0 | 1.00 | 1.00 |
| c5 vs overflowCapture | astra-medium | 52 | 2 | 2 | 0 | 0 | 1.00 | 1.00 |
| c5 vs overflowCapture | claude-opus | 52 | 2 | 2 | 1 | 0 | 0.67 | 1.00 |
| c5 vs overflowCapture | claude-sonnet | 52 | 2 | 0 | 1 | 2 | 0.00 | 0.00 |
| c5 vs overflowCapture | panel majority | 52 | 2 | 2 | 0 | 0 | 1.00 | 1.00 |
| c3 vs placeholder | astra-high | 52 | 0 | 0 | 4 | 0 | 0.00 | — |
| c3 vs placeholder | astra-medium | 52 | 0 | 0 | 3 | 0 | 0.00 | — |
| c3 vs placeholder | claude-opus | 52 | 0 | 0 | 5 | 0 | 0.00 | — |
| c3 vs placeholder | claude-sonnet | 52 | 0 | 0 | 2 | 0 | 0.00 | — |
| c3 vs placeholder | panel majority | 52 | 0 | 0 | 3 | 0 | 0.00 | — |

### Acceptance of the instrument, declared before the run

- α ≥ 0.67 on d1 across the model panel over the 26 v2.0 and v2.1 page(s): not met — α 0.46 [0.21–0.64] over 4 rater(s) (the spec asks for 4 × 26; pooled over 52 pages it is 0.48, which does not gate).
- α ≥ 0.5 on d1 between the two family means over the same pages: not met — α 0.43 over 26 page(s).
- Spearman ρ ≥ 0.6 between the user and the panel mean on d1: not met — ρ — over 0 anchor page(s) (the spec asks for 16; the interval is printed, the point estimate gates).
- retest α ≥ 0.67 on the 7-point items for every model rater: not met — lowest of 4 rater(s) 0.54: astra-high 0.58, astra-medium 0.70, claude-opus 0.54, claude-sonnet 0.65.

**Outcome: Partial.** The items that clear α are usable readings; d1 is not, quality claims about the endpoint stay unclaimable, and the grammar reading runs as exploratory and is labelled so. Provisional: rhoD1 has no data yet, so no reading here can be Accepted until it lands. The spec's Stopped is declared *after* the one permitted wording revision; whether that revision has been spent is a judgement the reader makes, not a fact in these files.

Items that could trip the one pre-registered wording revision (only a1, a2, a3, a4, d1, e1 qualify; the b-, t- and c-items are reported only): a1 α 0.38, a2 α 0.21, a3 α 0.23.

## S — rubric scores per arm

Page scores are the panel mean over the 4 model rater(s) — the user's anchor ratings are not pooled in, since they cover two briefs and six items and would tilt those briefs' arms. 52 page(s) rated of 52. Each cell is the mean over the arm's rated pages with a 2000-resample bootstrap 95 % interval and, in parentheses, the pages it stands on — fewer than the arm's total for an item only some briefs carry.

| score | none (13 pages) | v1.1 (13 pages) | v2.0 (13 pages) | v2.1 (13 pages) |
|---|---|---|---|---|
| d1 | 4.71 [4.08–5.33] (13) | 4.96 [4.50–5.44] (13) | 5.15 [4.67–5.65] (13) | 4.83 [4.37–5.23] (13) |
| aesthetics (VisAWI-S total, a1–a4) | 5.78 [5.46–6.10] (13) | 5.55 [5.21–5.86] (13) | 5.40 [5.18–5.62] (13) | 5.11 [4.88–5.32] (13) |
| brief fit (mean of the brief's b-items, 0–2) | 1.82 [1.69–1.93] (13) | 1.85 [1.75–1.94] (13) | 1.90 [1.81–1.98] (13) | 1.83 [1.74–1.92] (13) |
| defects (count of c1–c5) | 1.08 [0.69–1.46] (13) | 0.71 [0.38–1.08] (13) | 0.50 [0.21–0.81] (13) | 0.71 [0.35–1.17] (13) |
| e1 | 6.08 [5.71–6.37] (13) | 4.29 [3.52–4.92] (13) | 4.79 [4.15–5.40] (13) | 3.52 [2.90–4.23] (13) |
| a1 | 5.90 [5.58–6.23] (13) | 5.77 [5.46–6.04] (13) | 5.92 [5.71–6.12] (13) | 5.71 [5.48–5.92] (13) |
| a2 | 5.60 [5.31–5.88] (13) | 5.29 [4.79–5.71] (13) | 4.96 [4.62–5.25] (13) | 4.60 [4.33–4.85] (13) |
| a3 | 5.85 [5.50–6.19] (13) | 5.54 [5.27–5.81] (13) | 5.02 [4.81–5.21] (13) | 4.71 [4.37–5.04] (13) |
| a4 | 5.77 [5.35–6.15] (13) | 5.62 [5.25–5.94] (13) | 5.71 [5.44–5.98] (13) | 5.40 [5.12–5.65] (13) |
| b1 | 1.71 [1.31–2.00] (13) | 1.67 [1.37–1.92] (13) | 1.77 [1.52–2.00] (13) | 1.67 [1.35–1.94] (13) |
| b2 | 1.83 [1.54–2.00] (13) | 1.92 [1.83–2.00] (13) | 1.83 [1.50–2.00] (13) | 1.85 [1.62–2.00] (13) |
| b3 | 1.96 [1.88–2.00] (13) | 2.00 [2.00–2.00] (13) | 2.00 [2.00–2.00] (13) | 2.00 [2.00–2.00] (13) |
| b4 | 1.73 [1.43–1.93] (11) | 1.75 [1.36–2.00] (11) | 2.00 [2.00–2.00] (11) | 1.77 [1.45–2.00] (11) |
| t1 | 6.38 [5.94–6.69] (4) | 5.44 [4.12–6.19] (4) | 5.56 [4.50–6.62] (4) | 5.88 [5.12–6.62] (4) |
| c1 | 0.52 [0.27–0.75] (13) | 0.25 [0.06–0.46] (13) | 0.29 [0.10–0.48] (13) | 0.35 [0.15–0.58] (13) |
| c2 | 0.35 [0.13–0.56] (13) | 0.17 [0.06–0.31] (13) | 0.10 [0.00–0.23] (13) | 0.12 [0.00–0.27] (13) |
| c3 | 0.13 [0.00–0.33] (13) | 0.08 [0.00–0.19] (13) | 0.04 [0.00–0.10] (13) | 0.02 [0.00–0.06] (13) |
| c4 | 0.08 [0.00–0.15] (13) | 0.17 [0.08–0.27] (13) | 0.08 [0.00–0.17] (13) | 0.12 [0.02–0.23] (13) |
| c5 | 0.00 [0.00–0.00] (13) | 0.04 [0.00–0.10] (13) | 0.00 [0.00–0.00] (13) | 0.12 [0.00–0.29] (13) |

### d1 per brief and arm

Panel mean deliverability, pages in parentheses.

| brief | none | v1.1 | v2.0 | v2.1 |
|---|---|---|---|---|
| compare | 5.50 (1) | 4.75 (1) | 6.25 (1) | 4.75 (1) |
| fleet | 3.88 (2) | 4.75 (2) | 5.12 (2) | 4.25 (2) |
| hardware | 5.62 (2) | 5.88 (2) | 4.38 (2) | 5.25 (2) |
| library | 6.25 (2) | 5.38 (2) | 5.12 (2) | 4.75 (2) |
| pharmacy | 3.88 (2) | 5.62 (2) | 6.12 (2) | 4.50 (2) |
| rail | 3.75 (2) | 3.62 (2) | 4.38 (2) | 5.12 (2) |
| rebate | 4.50 (2) | 4.62 (2) | 5.25 (2) | 5.12 (2) |

### v2.1 − v2.0, paired by brief and seed

The grammar reading's input (spec, The grammar reading). Paired by brief and seed label — in effect by brief, since the two arms' samplers drew different seeds and the two seeds of one arm are often near-duplicates, so the effective number of pairs is under thirteen.

13 pair(s), 4 model rater(s) a side. A positive difference favours v2.1; a dash is a pair where one side lacks the item.

| score | compare·A | fleet·A | fleet·B | hardware·A | hardware·B | library·A | library·B | pharmacy·A | pharmacy·B | rail·A | rail·B | rebate·A | rebate·B | pairs | mean | 95 % CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| d1 | -1.50 | -1.75 | 0.00 | 1.00 | 0.75 | -1.00 | 0.25 | -3.25 | 0.00 | -1.00 | 2.50 | -1.25 | 1.00 | 13 | -0.33 | -1.08–0.46 |
| aesthetics (VisAWI-S total, a1–a4) | -0.69 | -1.19 | -0.06 | 0.06 | -0.19 | -0.56 | -0.25 | -0.75 | -0.81 | -0.44 | 0.69 | -0.44 | 0.75 | 13 | -0.30 | -0.58–0.01 |
| brief fit (mean of the brief's b-items, 0–2) | -0.44 | -0.19 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | -0.25 | 0.00 | -0.06 | 0.19 | -0.50 | 0.12 | 13 | -0.07 | -0.19–0.04 |
| defects (count of c1–c5) | 0.50 | 2.00 | 0.25 | -0.75 | 0.25 | 1.00 | -0.25 | 1.00 | -0.50 | 0.50 | -1.25 | 0.00 | 0.00 | 13 | 0.21 | -0.21–0.65 |
| e1 | 1.25 | -1.50 | -4.50 | 0.25 | 0.75 | 0.75 | -2.25 | -2.25 | -1.50 | -0.75 | -4.00 | -2.00 | -0.75 | 13 | -1.27 | -2.21–-0.37 |
| a1 | -0.25 | -1.00 | 0.00 | 0.50 | 0.00 | -1.25 | 0.00 | -0.75 | -0.75 | -0.25 | 1.00 | -0.50 | 0.50 | 13 | -0.21 | -0.56–0.13 |
| a2 | -1.25 | -1.75 | -0.25 | -0.25 | 0.25 | 0.00 | -1.00 | -0.50 | -1.00 | -0.50 | 0.50 | 0.00 | 1.00 | 13 | -0.37 | -0.77–0.02 |
| a3 | -0.75 | -0.75 | 0.25 | -0.50 | -1.25 | 0.25 | 0.25 | -0.50 | -0.50 | -0.50 | 0.25 | -1.00 | 0.75 | 13 | -0.31 | -0.62–0.00 |
| a4 | -0.50 | -1.25 | -0.25 | 0.50 | 0.25 | -1.25 | -0.25 | -1.25 | -1.00 | -0.50 | 1.00 | -0.25 | 0.75 | 13 | -0.31 | -0.69–0.10 |
| b1 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | -0.25 | 0.50 | -2.00 | 0.50 | 13 | -0.10 | -0.46–0.15 |
| b2 | 0.00 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | -1.00 | 0.00 | 0.00 | 0.25 | 0.00 | 0.00 | 13 | 0.02 | -0.21–0.23 |
| b3 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 13 | 0.00 | 0.00–0.00 |
| b4 | -1.75 | -0.75 | 0.00 | 0.00 | 0.00 | — | — | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 11 | -0.23 | -0.55–0.00 |
| t1 | — | — | — | 0.00 | 0.00 | 1.00 | 0.25 | — | — | — | — | — | — | 4 | 0.31 | 0.00–0.75 |
| c1 | 0.50 | 0.00 | 0.25 | -0.50 | 0.00 | 0.00 | 0.00 | 1.00 | 0.00 | 0.00 | -0.50 | 0.00 | 0.00 | 13 | 0.06 | -0.13–0.25 |
| c2 | 0.00 | 0.75 | -0.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.50 | -0.75 | 0.00 | 0.00 | 13 | 0.02 | -0.15–0.21 |
| c3 | 0.00 | 0.00 | 0.00 | 0.00 | -0.25 | 0.00 | -0.25 | 0.25 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 13 | -0.02 | -0.08–0.04 |
| c4 | 0.00 | 0.50 | 0.25 | -0.25 | 0.50 | 0.25 | 0.00 | -0.25 | -0.50 | 0.00 | 0.00 | 0.00 | 0.00 | 13 | 0.04 | -0.12–0.19 |
| c5 | 0.00 | 0.75 | 0.00 | 0.00 | 0.00 | 0.75 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 13 | 0.12 | 0.00–0.29 |

Per rater, the sign of its own d1 difference on each pair (+ favours v2.1, · a tie, blank not rated), and how many raters carry the sign of the panel's mean difference.

| rater | compare·A | fleet·A | fleet·B | hardware·A | hardware·B | library·A | library·B | pharmacy·A | pharmacy·B | rail·A | rail·B | rebate·A | rebate·B |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| astra-high | − | − | · | + | + | − | + | − | · | · | + | − | + |
| astra-medium | − | − | · | + | + | − | · | − | · | − | + | − | + |
| claude-opus | − | − | + | − | · | − | · | − | · | − | + | − | + |
| claude-sonnet | − | − | − | + | + | · | · | − | · | − | + | + | · |
| raters on the mean's sign | 4 | 4 | 1 | 1 | 0 | 3 | 0 | 4 | 0 | 3 | 0 | 3 | 0 |

**The confirmation gate.** No difference detectable at 13 pairs: the paired d1 mean is -0.33 [-1.08–0.46] and its interval covers zero; three or more raters carry its sign on only 6 of 13 pairs. Steps 1–4 of the grammar reading run as exploratory and are labelled so. The minimum difference 13 pairs could have detected is 0.81 of a point (1.96·sd/√n).

### The no-skill hold

The settling run's hold (Decision Log 2026-09-09): `none` should not beat `v1.1`. The hold stands unless `none`'s paired d1 difference against `v1.1` is positive with its interval excluding zero; it is confirmed if the difference is negative with its interval excluding zero; between, it is not decided at this sample.

- d1: none 4.71 [4.08–5.33] over 13 page(s); v1.1 4.96 [4.50–5.44] over 13 page(s).
- defects (count of c1–c5): none 1.08 [0.69–1.46] over 13 page(s); v1.1 0.71 [0.38–1.08] over 13 page(s).

13 pair(s), 4 model rater(s) a side. A positive difference favours none; a dash is a pair where one side lacks the item.

| score | compare·A | fleet·A | fleet·B | hardware·A | hardware·B | library·A | library·B | pharmacy·A | pharmacy·B | rail·A | rail·B | rebate·A | rebate·B | pairs | mean | 95 % CI |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| d1 | 0.75 | -2.25 | 0.50 | -0.25 | -0.25 | -0.50 | 2.25 | -3.00 | -0.50 | 0.75 | -0.50 | 0.25 | -0.50 | 13 | -0.25 | -0.88–0.44 |
| defects (count of c1–c5) | 0.00 | 0.75 | 0.75 | 0.75 | 0.50 | 0.00 | -0.75 | 1.25 | 0.75 | 1.00 | -0.75 | -0.25 | 0.75 | 13 | 0.37 | 0.00–0.69 |

**The hold is not decided at this sample**: none − v1.1 on d1 is -0.25 [-0.88–0.44] over 13 pair(s) — the interval covers zero. The minimum difference detectable here is 0.72 of a point.

### UIClip

UIClip scored 52 page(s); the correlations are over the 52 of them the panel has rated. It is a reported column, never in α.

| UIClip capture | ρ with d1 | ρ with aesthetics | pages |
|---|---|---|---|
| fv | -0.08 | 0.05 | 52 |
| full | -0.12 | -0.05 | 52 |

| arm | UIClip fv | UIClip full | pages |
|---|---|---|---|
| none | 0.616 | 0.746 | 13 |
| v1.1 | 0.629 | 0.738 | 13 |
| v2.0 | 0.636 | 0.721 | 13 |
| v2.1 | 0.513 | 0.696 | 13 |

## V — validity gate per build

| id | brief | arm | seed | mechanical | judged | gate |
|---|---|---|---|---|---|---|
| c183ef | rail | none | A | fail | 0/3 | contrast 0.851, won 0 pairs |
| 8ef70a | rail | v1.1 | A | pass | 2/3 | pass |
| cb9845 | rail | v2.0 | A | pass | 3/3 | pass |
| 8d1d23 | rail | v2.1 | A | pass | 2/3 | pass |
| c78373 | rebate | none | A | fail | 2/3 | contrast 0.758 |
| cbd040 | rebate | v1.1 | A | pass | 1/3 | pass |
| 5d884a | rebate | v2.0 | A | pass | 0/3 | won 0 pairs |
| 7acb2c | rebate | v2.1 | A | pass | 1/3 | pass |
| 30f897 | library | none | A | pass | 3/3 | pass |
| dd3f5c | library | v1.1 | A | pass | 3/3 | pass |
| 99499b | library | v2.0 | A | pass | 0/3 | won 0 pairs |
| 672565 | library | v2.1 | A | pass | 2/3 | pass |
| 122077 | pharmacy | none | A | fail | 3/3 | contrast 0.57 |
| 002ea9 | pharmacy | v1.1 | A | pass | 3/3 | pass |
| 3ba9f0 | pharmacy | v2.0 | A | pass | 0/3 | won 0 pairs |
| f344b7 | pharmacy | v2.1 | A | pass | 3/3 | pass |
| ae0658 | fleet | none | A | pass | 0/3 | won 0 pairs |
| 7e71b0 | fleet | v1.1 | A | pass | 3/3 | pass |
| 4e40b0 | fleet | v2.0 | A | pass | 3/3 | pass |
| 49e6cb | fleet | v2.1 | A | fail | 1/3 | overflow |
| 4d761e | hardware | none | A | pass | 3/3 | pass |
| 5c24f6 | hardware | v1.1 | A | pass | 1/3 | pass |
| 0663a2 | hardware | v2.0 | A | pass | 2/3 | pass |
| c7de7e | hardware | v2.1 | A | pass | 0/3 | won 0 pairs |
| ede597 | compare | none | A | pass | 2/3 | pass |
| 32cc11 | compare | v1.1 | A | pass | 2/3 | pass |
| 033fcb | compare | v2.0 | A | pass | 2/3 | pass |
| d178d1 | compare | v2.1 | A | pass | 0/3 | won 0 pairs |
| e44b85 | rail | none | B | fail | 0/3 | contrast 0.55, won 0 pairs |
| a903f5 | rail | v1.1 | B | pass | 2/3 | pass |
| 92cba1 | rail | v2.0 | B | pass | 1/3 | pass |
| 661e66 | rail | v2.1 | B | pass | 2/3 | pass |
| 758523 | pharmacy | none | B | fail | 1/3 | contrast 0.499 |
| 10b239 | pharmacy | v1.1 | B | pass | 1/3 | pass |
| 42b5a3 | pharmacy | v2.0 | B | pass | 1/3 | pass |
| 5e2273 | pharmacy | v2.1 | B | pass | 0/3 | won 0 pairs |
| f77261 | rebate | none | B | pass | 3/3 | pass |
| c7de4a | rebate | v1.1 | B | pass | 2/3 | pass |
| ea1cfd | rebate | v2.0 | B | pass | 2/3 | pass |
| dcf135 | rebate | v2.1 | B | pass | 1/3 | pass |
| 865572 | fleet | none | B | pass | 1/3 | pass |
| 1a63c5 | fleet | v1.1 | B | pass | 2/3 | pass |
| 645bc6 | fleet | v2.0 | B | pass | 0/3 | won 0 pairs |
| f8973a | fleet | v2.1 | B | pass | 2/3 | pass |
| 5c042a | library | none | B | fail | 1/3 | contrast 0.801 |
| b0bad8 | library | v1.1 | B | pass | 2/3 | pass |
| f3d810 | library | v2.0 | B | pass | 0/3 | won 0 pairs |
| 8f113d | library | v2.1 | B | pass | 1/3 | pass |
| 70aa0a | hardware | none | B | pass | 3/3 | pass |
| ccf94b | hardware | v1.1 | B | pass | 1/3 | pass |
| b2095d | hardware | v2.0 | B | pass | 0/3 | won 0 pairs |
| aa615a | hardware | v2.1 | B | pass | 2/3 | pass |

## D — diversity per arm (mean pairwise; effective = Shypula pairwise form with the gate)

### across briefs within category

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff | hueEMD raw / eff | familyJaccard raw / eff |
|---|---|---|---|---|---|---|---|
| none | console | 12 | 0.247 / 0.0 | 0.688 / 0.0 | 0.712 / 0.0 | 0.135 / 0.0 | 0.667 / 0.0 |
| none | narrative | 12 | 0.24 / 0.099 | 0.427 / 0.152 | 0.654 / 0.279 | 0.198 / 0.095 | 0.917 / 0.389 |
| v1.1 | console | 12 | 0.257 / 0.257 | 0.483 / 0.483 | 0.757 / 0.757 | 0.164 / 0.164 | 0.944 / 0.944 |
| v1.1 | narrative | 12 | 0.254 / 0.254 | 0.59 / 0.59 | 0.752 / 0.752 | 0.254 / 0.254 | 0.903 / 0.903 |
| v2.0 | console | 12 | 0.308 / 0.134 | 0.616 / 0.264 | 0.813 / 0.342 | 0.089 / 0.047 | 0.75 / 0.333 |
| v2.0 | narrative | 12 | 0.27 / 0.025 | 0.601 / 0.046 | 0.712 / 0.057 | 0.242 / 0.024 | 0.75 / 0.083 |
| v2.1 | console | 12 | 0.212 / 0.074 | 0.601 / 0.239 | 0.606 / 0.246 | 0.084 / 0.037 | 0.917 / 0.417 |
| v2.1 | narrative | 12 | 0.273 / 0.181 | 0.5 / 0.316 | 0.588 / 0.4 | 0.213 / 0.134 | 0.944 / 0.639 |

### within brief across seeds

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff | hueEMD raw / eff | familyJaccard raw / eff |
|---|---|---|---|---|---|---|---|
| none | console | 3 | 0.247 / 0.0 | 0.725 / 0.0 | 0.797 / 0.0 | 0.14 / 0.0 | 1.0 / 0.0 |
| none | narrative | 3 | 0.2 / 0.05 | 0.4 / 0.133 | 0.498 / 0.098 | 0.212 / 0.031 | 0.778 / 0.222 |
| v1.1 | console | 3 | 0.257 / 0.257 | 0.442 / 0.442 | 0.623 / 0.623 | 0.173 / 0.173 | 0.667 / 0.667 |
| v1.1 | narrative | 3 | 0.262 / 0.262 | 0.598 / 0.598 | 0.602 / 0.602 | 0.306 / 0.306 | 1.0 / 1.0 |
| v2.0 | console | 3 | 0.215 / 0.073 | 0.625 / 0.269 | 0.699 / 0.246 | 0.071 / 0.017 | 0.667 / 0.333 |
| v2.0 | narrative | 3 | 0.271 / 0.0 | 0.468 / 0.0 | 0.701 / 0.0 | 0.299 / 0.0 | 0.778 / 0.0 |
| v2.1 | console | 3 | 0.193 / 0.076 | 0.684 / 0.196 | 0.44 / 0.188 | 0.045 / 0.009 | 0.667 / 0.333 |
| v2.1 | narrative | 3 | 0.264 / 0.196 | 0.393 / 0.267 | 0.596 / 0.427 | 0.171 / 0.131 | 0.778 / 0.556 |

### D2 — accent hue dispersion and ground, per arm

| arm | builds | accent hues | dispersion (1 − R̄) | eff. dispersion | grounds (L, hue) | dark grounds |
|---|---|---|---|---|---|---|
| none | 13 | 295, 39, 30, 38, 23, 30, 32, 21, 74, 221, 73, 27, 32 | 0.282 | 0.038 | 0.153/260 0.959/87 0.922/89 0.977/86 0.149/260 0.947/88 0.959/88 0.162/254 0.968/85 0.939/248 0.978/78 0.171/257 0.962/87 | 4 |
| v1.1 | 13 | 48, 46, 23, 285, 27, 265, 318, 43, 38, 25, 55, 295, 31 | 0.34 | 0.34 | 0.972/229 0.969/301 0.975/106 0.945/215 0.979/90 0.926/248 0.32/209 0.972/229 1/90 0.236/293 0.296/161 0.972/229 0.203/168 | 4 |
| v2.0 | 13 | 249, 282, 22, 28, 68, 63, 256, 28, 27, 62, 28, 30, 26 | 0.405 | 0.569 | 0.168/59 0.962/214 0.979/248 0.963/197 0.883/25 0.944/217 0.932/248 0.183/85 0.985/271 0.963/248 0.885/143 0.94/90 0.952/17 | 2 |
| v2.1 | 13 | 27, 26, 220, 24, 252, 58, 27, 58, 27, 32, 26, 248 | 0.475 | 0.482 | 0.214/71 0.978/258 0.94/271 0.968/237 0.958/90 0.954/197 0.952/242 0.973/90 0.951/209 0.957/258 0.679/192 0.931/224 0.932/236 | 1 |

### D2 supplement — accent job, and dispersion over directional accents only

Added after wave five (Decision Log): on a build whose interactive layer is achromatic the extractor's fallback reads the loudest status colour, so the D2 hue list above mixes chosen accents with critical reds. Here the job is the declared one for the 2.x arms and inferred from the extractor's locus for the others.

| arm | builds | directional | status-only | none | hues (directional) | dispersion | eff. dispersion |
|---|---|---|---|---|---|---|---|
| none | 13 | 10 | 0 | 3 | 295, 39, 30, 38, 30, 74, 221, 73, 27, 32 | 0.362 | 0.044 |
| v1.1 | 13 | 12 | 0 | 1 | 48, 46, 23, 285, 27, 265, 43, 38, 25, 55, 295, 31 | 0.33 | 0.33 |
| v2.0 | 13 | 6 | 3 | 4 | 249, 282, 28, 256, 28, 26 | 0.546 | 0.002 |
| v2.1 | 13 | 7 | 4 | 2 | 220, 252, 58, 58, 32, 26, 248 | 0.805 | 0.766 |

### D3 — families per arm

| arm | display families (distinct / builds) | body families | mono |
|---|---|---|---|
| none | 7/13: -apple-system, Inter, Iowan Old Style, Rockwell, Superclarendon, ui-rounded, ui-serif | 5/13: -apple-system, Inter, Iowan Old Style, system-ui, ui-sans-serif | 1/13: ui-monospace |
| v1.1 | 8/13: Archivo, Azeret Mono, Barlow, Barlow Condensed, Figtree, Lexend, Source Serif 4, Zilla Slab | 8/13: Archivo, Atkinson Hyperlegible Next, Barlow, Figtree, Lexend, Public Sans, Source Sans 3, Source Serif 4 | 4/13: Azeret Mono, DM Mono, Geist Mono, Roboto Mono |
| v2.0 | 7/13: Archivo Narrow, Atkinson Hyperlegible Next, Barlow, Barlow Condensed, Commissioner, Literata, Zilla Slab | 4/13: Atkinson Hyperlegible Next, Barlow, Cabin, Commissioner | 6/13: Atkinson Hyperlegible Mono, Azeret Mono, Fragment Mono, Geist Mono, JetBrains Mono, Roboto Mono |
| v2.1 | 9/13: Archivo Narrow, Arvo, Atkinson Hyperlegible Next, Barlow, Barlow Condensed, Commissioner, JetBrains Mono, Lexend, Zilla Slab | 6/13: Atkinson Hyperlegible Next, Barlow, Commissioner, JetBrains Mono, Lexend, Public Sans | 5/13: Azeret Mono, Fira Mono, Fragment Mono, JetBrains Mono, Roboto Mono |

### D4 — canonical shapes per arm and category

| arm | category | n | side region | rail band ≥1.5:1 | stat row (fv) | three-up | cards (fv) | headline band | dominant share ≥ 0.4 |
|---|---|---|---|---|---|---|---|---|---|
| none | console | 6 | 2 | 3 | 3 | 1 | 0 | 0 | 4 |
| none | narrative | 6 | 0 | 3 | 5 | 5 | 1 | 1 | 1 |
| none | pair | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |
| v1.1 | console | 6 | 0 | 5 | 1 | 0 | 0 | 0 | 1 |
| v1.1 | narrative | 6 | 0 | 5 | 0 | 5 | 0 | 0 | 2 |
| v1.1 | pair | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| v2.0 | console | 6 | 1 | 6 | 1 | 0 | 0 | 0 | 0 |
| v2.0 | narrative | 6 | 0 | 4 | 1 | 3 | 2 | 0 | 2 |
| v2.0 | pair | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 |
| v2.1 | console | 6 | 0 | 6 | 0 | 0 | 0 | 0 | 4 |
| v2.1 | narrative | 6 | 0 | 6 | 1 | 3 | 2 | 0 | 0 |
| v2.1 | pair | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |

## Per-build reads

| id | brief | arm | seed | ground | accent | hues | display / body / mono | dominant | dominance | side | stat | 3-up | height | BT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ede597 | compare | none | A | #F4F1EA L0.959 | #8C2F1F h32.1 | 2 | Iowan Old Style / -apple-system / ui-monospace | card-grid 0.11 | peers | band |  |  | 6.5vh | +0.28 |
| 32cc11 | compare | v1.1 | A | #11393F L0.32 | #7D3792 h317.7 | 2 | Figtree / Figtree / DM Mono | chart 1 | hero | band |  |  | 4.2vh | +0.28 |
| 033fcb | compare | v2.0 | A | #E4E9EE L0.932 | #205BA3 h255.6 | 1 | Barlow Condensed / Commissioner / Azeret Mono | text 0.051 | peers | band |  | y | 4.9vh | +0.28 |
| d178d1 | compare | v2.1 | A | #EBF0F4 L0.952 | #7A430E h58.1 | 1 | Lexend / Commissioner / JetBrains Mono | list 0.131 | peers |  |  | y | 3.9vh | -3.01 |
| ae0658 | fleet | none | A | #080B10 L0.149 | #FF6B6B h22.8 | 5 | None / ui-sans-serif / ui-monospace | table 0.47 | dominant | y |  |  | 1.0vh | -3.06 |
| 865572 | fleet | none | B | #0B1017 L0.171 | #FF6257 h27.2 | 6 | None / -apple-system / ui-monospace | list 0.48 | dominant | band | y |  | 3.0vh | -2.61 |
| 7e71b0 | fleet | v1.1 | A | #F8F8F8 L0.979 | #B91C1E h27.1 | 2 | Barlow / Barlow / Geist Mono | table 0.18 | dominant | band |  |  | 2.5vh | +0.77 |
| 1a63c5 | fleet | v1.1 | B | #F4F6F7 L0.972 | #5C389F h295.2 | 3 | Zilla Slab / Public Sans / Roboto Mono | list 0.382 | hero | band |  |  | 2.7vh | -0.35 |
| 4e40b0 | fleet | v2.0 | A | #DFD6D5 L0.883 | #B97515 h67.9 | 2 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | table 0.271 | hero | band |  |  | 3.2vh | +1.50 |
| 645bc6 | fleet | v2.0 | B | #EBEBEB L0.94 | #9C2318 h29.7 | 2 | Barlow / Barlow / JetBrains Mono | list 0.312 | dominant | band | y |  | 3.1vh | -3.06 |
| 49e6cb | fleet | v2.1 | A | #F1F1F1 L0.958 | #9E2C2E h24.2 | 3 | Barlow / Barlow / JetBrains Mono | list 0.456 | hero | band |  |  | 2.6vh | -1.75 |
| f8973a | fleet | v2.1 | B | #E4E9EB L0.931 | #B6312E h26.5 | 2 | Arvo / Public Sans / Fira Mono | list 0.427 | dominant | band |  |  | 2.6vh | -1.13 |
| 4d761e | hardware | none | A | #F2EDE1 L0.947 | #A02C20 h29.8 | 1 | -apple-system / Iowan Old Style / None | chart 0.16 | dominant |  |  |  | 8.4vh | +1.19 |
| 70aa0a | hardware | none | B | #F6F2E9 L0.962 | #A8301B h32.3 | 2 | Rockwell / -apple-system / None | chart 0.146 | peers |  | y | y | 6.7vh | +1.19 |
| 5c24f6 | hardware | v1.1 | A | #E3E7EB L0.926 | #1A41BA h265 | 1 | Barlow Condensed / Source Serif 4 / Roboto Mono | block 1 | hero | band |  | y | 6.3vh | -2.12 |
| ccf94b | hardware | v1.1 | B | #071B14 L0.203 | #BB3A28 h31 | 2 | Archivo / Public Sans / Azeret Mono | list 0.829 | hero | band |  | y | 5.5vh | -2.12 |
| 0663a2 | hardware | v2.0 | A | #E7EEF0 L0.944 | #693B03 h62.7 | 1 | Zilla Slab / Cabin / Fragment Mono | list 0.1 | peers |  |  |  | 5.5vh | -0.63 |
| b2095d | hardware | v2.0 | B | #F4EDED L0.952 | #7F2C29 h25.5 | 1 | Archivo Narrow / Barlow / Roboto Mono | list 0.859 | hero | band |  | y | 5.8vh | -3.06 |
| c7de7e | hardware | v2.1 | A | #E9F2F2 L0.954 | #215D99 h251.7 | 1 | Barlow Condensed / Public Sans / Azeret Mono | list 0.119 | dominant | band |  |  | 5.7vh | -3.06 |
| aa615a | hardware | v2.1 | B | #E6E9EB L0.932 | #07558E h248.3 | 1 | Barlow Condensed / Barlow / Azeret Mono | pricing 0.193 | dominant | band |  | y | 4.3vh | -0.63 |
| 30f897 | library | none | A | #FCF7EC L0.977 | #C24A22 h37.9 | 2 | Superclarendon / ui-sans-serif / None | heading 0.634 | hero | band | y | y | 6.8vh | +1.19 |
| 5c042a | library | none | B | #FDF7EE L0.978 | #F2A31C h73 | 2 | ui-rounded / system-ui / None | heading 0.183 | peers |  | y | y | 8.3vh | -2.12 |
| dd3f5c | library | v1.1 | A | #D1F4FD L0.945 | #5F4BC7 h285.1 | 1 | Source Serif 4 / Lexend / None | heading 0.078 | peers | band |  |  | 6.7vh | +1.19 |
| b0bad8 | library | v1.1 | B | #153425 L0.296 | #EA883D h54.7 | 1 | Azeret Mono / Atkinson Hyperlegible Next / Azeret Mono | chart 0.265 | hero | band |  | y | 6.9vh | -0.63 |
| 99499b | library | v2.0 | A | #E9F6F6 L0.963 | #B12D26 h28 | 1 | Literata / Atkinson Hyperlegible Next / Fragment Mono | panel 0.403 | hero |  |  |  | 6.4vh | -3.06 |
| f3d810 | library | v2.0 | B | #BEE6BB L0.885 | #C83B32 h28 | 1 | Zilla Slab / Atkinson Hyperlegible Next / Azeret Mono | heading 0.113 | peers | band |  | y | 7.7vh | -3.06 |
| 672565 | library | v2.1 | A | #EDF6FC L0.968 | #00758F h220.4 | 1 | Zilla Slab / Lexend / Fragment Mono | card-grid 0.14 | peers | band |  | y | 7.1vh | -0.63 |
| 8f113d | library | v2.1 | B | #3EABA8 L0.679 | #C13A23 h32.2 | 1 | Zilla Slab / Atkinson Hyperlegible Next / Fragment Mono | heading 0.041 | peers | band | y |  | 6.7vh | -2.12 |
| 122077 | pharmacy | none | A | #E7E5E0 L0.922 | #A52A1C h30.3 | 2 | Inter / Inter / ui-monospace | rail 0.276 | peers | y |  |  | 1.0vh | +0.89 |
| 758523 | pharmacy | none | B | #E8EBEE L0.939 | #0B5A6E h220.8 | 1 | -apple-system / -apple-system / ui-monospace | table 0.497 | hero | band | y | y | 1.9vh | -1.66 |
| 002ea9 | pharmacy | v1.1 | A | #F7F7F3 L0.975 | #A34242 h22.8 | 4 | Source Serif 4 / Source Sans 3 / Roboto Mono | list 0.33 | hero | band |  |  | 4.1vh | +0.89 |
| 10b239 | pharmacy | v1.1 | B | #201837 L0.236 | #F86E68 h24.9 | 2 | Lexend / Lexend / Geist Mono | list 0.317 | dominant | band |  |  | 3.0vh | -1.66 |
| 3ba9f0 | pharmacy | v2.0 | A | #F7F8F9 L0.979 | #98252D h22.1 | 4 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / Atkinson Hyperlegible Mono | list 0.301 | hero | band |  |  | 2.6vh | -3.05 |
| 42b5a3 | pharmacy | v2.0 | B | #F1F3F5 L0.963 | #653908 h61.7 | 1 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | table 0.185 | dominant | y |  |  | 2.9vh | -1.66 |
| f344b7 | pharmacy | v2.1 | A | #EAEBEE L0.94 | #A12626 h25.9 | 4 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | list 0.419 | dominant | band |  |  | 2.6vh | +0.89 |
| 5e2273 | pharmacy | v2.1 | B | #EFF1F4 L0.957 | #9E2D28 h27.1 | 4 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | list 0.909 | hero | band |  |  | 2.5vh | -3.05 |
| c183ef | rail | none | A | #090C11 L0.153 | #A888FA h294.8 | 1 | None / -apple-system / ui-monospace | list 0.949 | hero | band | y |  | 1.0vh | -3.08 |
| e44b85 | rail | none | B | #0A0E13 L0.162 | #F0575E h21.3 | 4 | None / Inter / ui-monospace | chart 0.274 | peers |  |  |  | 1.0vh | -3.08 |
| 8ef70a | rail | v1.1 | A | #F4F6F7 L0.972 | #D46B2C h48 | 3 | Archivo / Public Sans / Geist Mono | list 0.319 | peers |  |  |  | 1.4vh | -1.55 |
| a903f5 | rail | v1.1 | B | #F4F6F7 L0.972 | #8C3C17 h42.7 | 1 | Archivo / Public Sans / Geist Mono | block 0.543 | hero | band | y |  | 2.8vh | -0.27 |
| cb9845 | rail | v2.0 | A | #120E0B L0.168 | #4197E5 h249 | 1 | Commissioner / Commissioner / JetBrains Mono | chart 0.291 | dominant | band |  |  | 1.9vh | +1.78 |
| 92cba1 | rail | v2.0 | B | #14120E L0.183 | #F47062 h28.1 | 4 | None / Barlow / JetBrains Mono | table 0.29 | peers | band |  |  | 1.0vh | -2.96 |
| 8d1d23 | rail | v2.1 | A | #1E1811 L0.214 | #F66D62 h27 | 4 | None / Barlow / JetBrains Mono | chart 0.334 | peers | band |  |  | 1.8vh | -0.27 |
| 661e66 | rail | v2.1 | B | #F6F6F6 L0.973 | #A3322C h27.2 | 1 | JetBrains Mono / JetBrains Mono / JetBrains Mono | chart 0.392 | dominant | band |  |  | 2.2vh | -1.55 |
| c78373 | rebate | none | A | #F5F1E8 L0.959 | #A9411A h39.2 | 1 | Iowan Old Style / ui-sans-serif / ui-monospace | heading 0.142 | dominant | band | y | y | 12.1vh | +0.37 |
| f77261 | rebate | none | B | #F7F4EE L0.968 | #F0A93C h73.7 | 2 | ui-serif / ui-sans-serif / ui-monospace | heading 0.093 | peers | band | y | y | 12.8vh | +1.30 |
| cbd040 | rebate | v1.1 | A | #F5F4F7 L0.969 | #FF7729 h45.8 | 2 | Zilla Slab / Public Sans / Azeret Mono | heading 0.065 | dominant |  |  | y | 7.9vh | -1.40 |
| c7de4a | rebate | v1.1 | B | #FFFFFF L1 | #C74413 h38 | 1 | Archivo / Archivo / Roboto Mono | list 0.097 | peers | band |  | y | 7.1vh | -0.17 |
| 5d884a | rebate | v2.0 | A | #ECF4F6 L0.962 | #4A41A7 h281.8 | 1 | Zilla Slab / Atkinson Hyperlegible Next / Geist Mono | heading 0.07 | peers | band |  |  | 7.9vh | -3.03 |
| ea1cfd | rebate | v2.0 | B | #F9FAFD L0.985 | #702520 h27.2 | 3 | Barlow / Atkinson Hyperlegible Next / Azeret Mono | list 0.107 | peers | band | y | y | 9.7vh | +0.11 |
| 7acb2c | rebate | v2.1 | A | #F6F8FB L0.978 | — h | 0 | Archivo Narrow / Public Sans / Roboto Mono | block 0.09 | dominant | band |  |  | 9.4vh | -0.65 |
| dcf135 | rebate | v2.1 | B | #EAF0F1 L0.951 | #7C481B h57.8 | 1 | Commissioner / Atkinson Hyperlegible Next / Azeret Mono | list 0.2 | hero | band |  | y | 7.9vh | -2.35 |

## F — structural fit (blinded rater, secondary)

| arm | builds | mean yes of 5 |
|---|---|---|
| none | 13 | 3.38 |
| v1.1 | 13 | 4.23 |
| v2.0 | 13 | 4.23 |
| v2.1 | 13 | 4.62 |

## P — fleet against compare, per arm (all four distances)

| arm | fleet seed | partition | raster | pqgram | sig | compare dominant | fleet dominant |
|---|---|---|---|---|---|---|---|
| none | A | 0.315 | 0.964 | 0.606 | 0.75 | card-grid | table |
| none | B | 0.301 | 0.932 | 0.489 | 0.5 | card-grid | list |
| v1.1 | A | 0.305 | 0.922 | 0.442 | 0.333 | chart | table |
| v1.1 | B | 0.284 | 0.956 | 0.508 | 0.25 | chart | list |
| v2.0 | A | 0.368 | 0.734 | 0.427 | 0.417 | text | table |
| v2.0 | B | 0.302 | 0.667 | 0.697 | 0.5 | text | list |
| v2.1 | A | 0.284 | 0.732 | 0.617 | 0.5 | list | list |
| v2.1 | B | 0.258 | 0.815 | 0.541 | 0.5 | list | list |
