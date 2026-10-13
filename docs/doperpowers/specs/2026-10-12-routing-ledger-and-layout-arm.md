# SKILL.md back to routing, the build ledger, and the layout arm

**Status:** in progress, 2026-10-12. Parts A and B are the plugin's 2.4.0; part C is a pre-registered
run that reuses the settling experiment's 52 builds as its baseline arms. Child of
`2026-09-05-stance-derivation.md` (Deferred: "a ledger of recent builds' families and hues") and
`2026-09-05-composition-grammar.md` (Deferred: "the settling experiment gains a layout arm"; "a
layout ledger"). Reads `2026-09-05-settling-experiment.md` and `2026-09-09-quality-instrument.md`
for its instruments and for what has already been measured.

## Purpose

Three things the review of the skill's history (2026-10-12) named, in the order the user chose
them.

**A. SKILL.md is a routing document again.** Version 1's `SKILL.md` routed to the references;
2.0 to 2.3 restated a growing share of them inside it — the nine-line stance paragraph, the
composition derivation, the adoption and persona routes, the clone question, the ratio ban — each
added by a review round that propagated an exemption to every place it applied. The always-loaded
file grew from about 2,350 to 3,400 words, and three independent agents produced `DESIGN.md`
records of 271 to 302 lines against a 160-line budget. After this change a reader of `SKILL.md`
learns what the steps are and where each is specified, and the specification lives once, in the
reference that owns it.

**B. The build ledger.** Both v2 specs found that convergence relocates: remove the hex block and
it reappears as the "best answer" family (Atkinson Hyperlegible Next in three of four acceptance
builds), the leftover hue (two consoles at violet by elimination), the signature motif (the
library brief's stamp card under both derivation arms and across seeds; the hardware brief's
will-call ticket under three skills), and the same form for a different unit (pharmacy and
wind-farm both "exception-first"). Criteria funnel to one answer as a catalogue does, one level
down. A calibration file that names bands is the right tool and needs feeding; the structural
answer both specs deferred is a ledger of what recent builds chose, consulted at derivation so
that dispersion happens in output space (Marks 1997, via the stance memo) rather than by axis
distance. After this change, before the accent hue, the ground, the families, the signature and
the composition form are fixed, the agent sees the nearest prior builds and either names what in
this product's world puts it beside them or moves.

**C. The layout arm, measured with the right instrument.** The settling run measured 2.1 with
partition distance as the headline and found the clause fired because the grammar converged
consoles onto the brief's form, which is exactly what partition penalises. Its retrospective and
the quality instrument's findings together say: brief fit is the one reliable rubric item
(α 0.83), partition is reported but cannot gate, and 13 pairs cannot detect a deliverability
difference under 0.8 of a point. What is still unmeasured is the composition spec's ablation —
the grammar with one candidate and no candidate comparison — and, now, whether the compressed
skill with the ledger holds what 2.1 to 2.3 bought (fit, no stat row, the contrast gate) while
moving the token and signature convergence the ledger exists for. After this run, 2.1's claim
has a reading on the instrument its own retrospective asked for, and the compression and the
ledger have a measurement rather than a review.

## Part A — compression

**Rule.** `SKILL.md` carries: the classification and precedence chain; persona routing; the
required first steps as one or two sentences each with the command or file they point at; the
eight-step spine with one sentence of purpose and the reference that specifies it; the taste floor;
runtime adaptation; the routing table. Every procedural sentence that a reference already states is
cut; every one a reference does not state is moved to the reference that owns it, not deleted.

**Moves.** Before cutting, each clause was checked against the references:

- The nine-line derivation, the rejected values, the signature, "a name is a starting position,
  never a source of values", the clone question: `stances.md` §"The derivation procedure" and
  §"Closing rule". Cut from `SKILL.md`.
- The two routes that reach the nine lines without a derivation (adopted system; persona):
  `guidelines-authoring.md` §0 states both; `stances.md`'s procedure did not. Added to
  `stances.md` after step 7 as one paragraph; cut from `SKILL.md`.
- "Material is decided in the parse step; a glass system changes the component canon":
  `material.md` intro. "Read liquid-glass.md when the axis resolves to glass, before composition":
  `liquid-glass.md` intro. Cut.
- The six composition lines read at parse time; the candidates at step 3 before `DESIGN.md`; one
  candidate when only one fits; the compiled consequences; the ratio band; the imagery ladder;
  the adopted-geometry exception: `composition.md` intro, §"Compiled consequences", §"The
  procedure", §"Imagery as content" and the ladder. Cut.
- "A worked derivation's values are that product's instantiation": `stances.md` §"Five worked
  derivations". Cut.
- Composition QA and the clone check at step 8: `qa-protocol.md` check 3 and §"Verify the build
  against its own law". Cut to the pointer.
- The capsule preference on the glass taste-floor line: `liquid-glass.md` §"Shape". Cut to the
  rule.

**What stays verbatim.** The taste floor (it is the floor, and nothing else states it whole), the
precedence chain, and persona routing (`personas/essentialist.md` does not carry the activation
rules).

**Result.** 3,393 → 2,674 words (v1.0.0 was 2,351 with eleven references; the file now routes to
fourteen and two scripts). What remains above the v1 count is persona routing and the taste floor,
both kept whole because no reference states them. The test of the compression is part C's `v2.4`
arm: a builder under the compressed skill still writes the §0 and §4 records, runs the sampler, and
passes the gate at the 2.1 to 2.3 rate.

## Part B — the build ledger

**What it is.** `skills/designer/scripts/build-ledger.mjs`, an append-only JSON-lines file of what
each finished build chose, and a nearest-neighbour report over it. The ledger is per machine, not
per project, because convergence is across products built by the same agent: `DESIGNER_LEDGER`
names the file, else `~/.config/designer/build-ledger.jsonl` (the convention `find-image.mjs` set
with `~/.config/designer/unsplash-key`). The plugin ships the script; the ledger starts empty and
fills as builds are recorded.

**An entry.** Written at the end of QA from the build's own record, by flags (a record's prose is
not parsed; the agent already holds the values):

```
node scripts/build-ledger.mjs record --project perpetual --brief "inpatient pharmacy inventory console" \
  --category console --accent-hue none --accent-job none --ground-l 0.94 --ground-hue 265 \
  --ground-temperature neutral --display "Atkinson Hyperlegible Next" --body "Atkinson Hyperlegible Next" \
  --mono "JetBrains Mono" --signature "numbered witness gutter in the controlled-substance region" \
  --posture workspace --activity monitor --relation sequence --dominance one-dominant --prior exception-first
```

`category` is the agent's one-word class for the product (console, landing, docs, commerce,
editorial, settings, …), free text, matched exactly. Every field is optional; a missing field is
recorded as missing and never guessed.

**The report.** `nearest`, with any subset of the same flags, run at derivation before the values
are fixed and again at QA. For the twenty most recent entries, nearest first within the same
category and then across, it prints one line per entry with the distances, and flags:

- *accent*: a directional or atmospheric accent within 30° of a recent entry's (the stance
  spec's A1 band); `none` and status-only never flag.
- *ground*: same lightness side and hue within 20° at chroma that reads as the same temperature.
- *family*: the display or body family already used by an entry in the same category among the
  last ten.
- *signature*: a content word of five letters or more shared with a recent entry's signature
  line (the stamp, the ticket, the gutter).
- *form*: the same activity, relation and prior as an entry whose brief differs.

The preamble says what a flag means, the way the sampler's does: a neighbour inside a band is not
forbidden; the record names what in this product's world put the value there, or the value moves.
A flag is evidence for the clone check, never a verdict.

**Where the skill consults it.** `stances.md` derivation step 4 (before the values are fixed);
`composition.md` procedure step 5 (before the candidate is chosen); `qa-protocol.md` composition
check 5, which already assumed a ledger it did not have, and the clone check; `SKILL.md` names the
script once at step 3 and once at step 8. `taste-calibration.md` §"The leftover accent" and
§"The landing scaffold" gain one line each pointing at the report as the way the band is seen.

**Seeding for the experiment.** `docs/research/scripts/settling/ledger-seed.mjs` writes a ledger
from the settling run's measured tokens (`measurements.json`), topology signatures
(`topology.json`) and each record's signature line, filtered to the skill arms and to briefs other
than the one being built, so a `v2.4` cell's ledger holds realistic prior work and never a sibling
of its own brief. Entries carry `source: measured`.

**Tests.** `build-ledger.test.mjs` under `node --test`: circular hue distance, the five flags, the
ordering, a missing field never flags, and record-then-nearest round-trips through a temp ledger.

## Part C — the run, pre-registered

**Arms.** The four settling arms (`none`, `v1.1`, `v2.0`, `v2.1`) are reused as built: 52 pages,
their measurements, topology, fit ratings and rubric ratings as recorded. New arms, chosen by the
user (Decision Log), on the same seven briefs, same two seeds, same builder prompt, same frozen-copy
rule:

| Arm | Skill | What it isolates |
|---|---|---|
| `v2.4` | `skills/designer` at the commit that ships parts A and B, ledger seeded per cell from the other briefs' skill-arm builds | the compressed skill plus the ledger, against `v2.1` and `v2.3`'s doctrine |
| `v2.1-one` | the frozen `v2.1` copy with `composition.md` §"The procedure" steps 4–5 rewritten to one candidate, chosen by fit, no comparison; composition QA check 3 removed | the candidate step's own contribution |

The `v2.4` arm's builder prompt adds one line: `DESIGNER_LEDGER` set to the cell's seeded file.
Nothing else in the prompt changes. The sampler seeds are the settling seeds, so where the
ingredient lists coincide the draws coincide with `v2.1`'s.

**Measures.** Declared here, run by the settling instruments unchanged except where named.

- **Fit, the headline.** The blinded structural rater's five yes/no questions per category
  (`cells.mjs fitprompt`), one rater per brief seeing the brief's pages old and new, ids only; and
  the rubric panel's brief-fit composite (the b-items, α 0.83 in the quality run), four raters per
  brief. Reported as mean yes-of-five and mean b-score per arm with bootstrap intervals, and
  `v2.4 − v2.1`, `v2.4 − v2.0`, `v2.1-one − v2.1` paired by brief and seed.
- **Conventionality** (e1, revised wording, α 0.71) and **deliverability** (d1) from the same
  panel, reported beside fit; d1 is exploratory by the quality spec's finding and is labelled so.
- **D4**, the canonical-shape counts per arm and category, from `measure.mjs`.
- **D1**, partition and pq-gram within category across briefs and within brief across seeds,
  reported and not gating.
- **D2 and D3** as pre-registered in the settling spec, plus the by-job supplement.
- **The ledger's own reading**, new: for every `v2.4` build, the distances the agent saw at
  derivation (the ledger report is saved in the build directory as `ledger-report.txt` by the
  builder prompt) against the values it shipped; the share of builds whose record names a ledger
  neighbour; accent dispersion and distinct display families for `v2.4` against `v2.1`; the
  signature-word overlap across `v2.4` builds against `v2.1`'s (the stamp-card test).
- **V**, the validity gate, with the overflow clause read from the capture width (the settling
  spec's deferred fix) for every arm, old and new, re-measured once.
- **Record discipline**, new: lines in `DESIGN.md`, the presence of §0's nine lines and §4's six
  lines and candidates, the sampler draw recorded, the ledger record run (an entry appended to the
  cell's ledger).

**Hypotheses.**

- **C1 (the compression holds).** `v2.4`'s fit is not below `v2.1`'s by more than 0.3 of a point
  (mean yes-of-five), its gate pass rate is at least 12 of 13, and every build carries the §0 and
  §4 records. A fit drop over 0.3 or a missing record is the compression cutting something the
  references did not carry.
- **C2 (the ledger moves what it watches).** Over the 13 `v2.4` builds against the 13 `v2.1`:
  directional-accent dispersion by job does not fall; no display family appears in more than three
  builds of one category; the library brief's two seeds do not share the stamp motif and the
  hardware brief's do not share the ticket. Each is read on its own; the ledger's report in the
  build directory says whether the agent saw the neighbour.
- **C3 (the candidate step).** `v2.1-one`'s fit against `v2.1`'s: a drop over 0.3 says the
  candidate step earns its cost; a difference inside ±0.3 with no change in D4 says it does not,
  and the step is cut to one candidate in the next revision.
- **C4 (quality, exploratory).** Paired d1 for `v2.4 − v2.1` and `v2.4 − v2.0` with intervals; at
  13 pairs the minimum detectable difference is about 0.8, so this reading can only catch a large
  loss, and it is labelled so.

**What would stop the change.** C1 failing: `v2.4` is not shipped as 2.4.0 until the missing
specification is found and restored to its reference; the compression is not reverted wholesale.
C2 failing on every clause with the reports showing the agent saw the neighbours: the ledger is
reporting without moving anything, and the next step is the structural one (the band becomes a
hard rule in the record, or the step is dropped), recorded here.

**Cost.** Per arm, 13 builds at about 0.35 M tokens; one fit rater per brief; the rubric panel at
four raters per brief over the new pages (the old pages' ratings are reused). Two waves of eight
builders per arm as before.

**Files.** This spec; `skills/designer/SKILL.md`, `references/stances.md`, `composition.md`,
`qa-protocol.md`, `taste-calibration.md`, `guidelines-authoring.md`, `scripts/build-ledger.mjs`,
`scripts/build-ledger.test.mjs`; `docs/research/scripts/settling/ledger-seed.mjs` and the
`cells.mjs` arm table; `docs/research/data/2026-10-12-layout-arm/` for the committed evidence.

## Plan of Work

1. Part A: rewrite `SKILL.md`; move the two-route paragraph into `stances.md`; verify each cut
   against its reference; word count; `claude plugin validate . --strict`.
2. Part B: `build-ledger.mjs` and its test; hooks in the four references; `ledger-seed.mjs`.
3. Version 2.4.0, plugin tests, commit.
4. Part C: freeze the skill copies, extend the manifest, run the waves, measure, rate, record.

## Decision Log

- Decision: Three pieces in one wave, in the order compression, ledger, run.
  Rationale: the user's choice on 2026-10-12, from the review of the skill's history. The run is
  what tests the first two; doing it last means the arms are the shipped artifacts.
  Date/Author: 2026-10-12, the user.

- Decision: The ledger is a report at derivation, not a constraint; its entry is written by flags
  at QA, not parsed from the record; it lives per machine.
  Rationale: the band rules already exist in `taste-calibration.md` and `stances.md`; what was
  missing is the evidence at the moment of choice. Parsing a prose record is the fragility the
  stance spec hit with semantic token names; flags are what the agent has in hand. Per machine
  because the clone is across products, not within one. Rejected: a required structured block in
  `DESIGN.md` for the script to read (a doctrine change to the record's shape, deferred until the
  budget problem is addressed on its own); a per-project ledger (would never see the sibling).
  Date/Author: 2026-10-12, Claude.

- Decision: The gap flag (2.4.1). The `nearest` report prints the recent directional accents by
  30° band and flags a candidate whose band and both neighbouring bands are empty while the recent
  accents occupy at most half the wheel and number at least three, repeating the calibration rule;
  the preamble says a value does not move into the unused band. `stances.md` step 4 says the same
  with the run's number.
  Rationale: the user's choice on 2026-10-13 from the run's C2 reading — four of six directional
  accents in the one empty band. Rejected: dropping the accent flag (it did its half of the job:
  the red and blue clusters were left), and leaving the report as is (the rule lived in a file the
  agent was not reading at the moment of choice). Whether the flag moves the next run's dispersion
  is the next measurement.
  Date/Author: 2026-10-13, the user.

- Decision: The `v2.1-one` ablation runs, 13 builds, and the fit and rubric frames are re-rated
  with all twelve pages of a brief (eight baseline, two `v2.4`, two `v2.1-one`) in one frame; the
  first frame's readings are kept as `fit-run1/` and `rubric-run1/` and stay the record for C1,
  C2 and C4 above.
  Rationale: the user's choice; one frame keeps `v2.1-one` comparable to `v2.1` and `v2.4` alike.
  Date/Author: 2026-10-13, the user.

- Decision: Part C reuses the settling builds and adds arms, with fit as the headline and partition
  reported only.
  Rationale: the settling retrospective and the quality instrument's reliability table. A
  partition clause pre-registered again would fire again for the reason already recorded.
  Rejected: rebuilding the four settling arms (the frozen copies and builds exist; a rebuild
  measures model drift, not the doctrine).
  Date/Author: 2026-10-12, Claude.

## Surprises & Discoveries

- Observation: No Playwright module on the machine could launch Chromium: the browser cache under
  `~/Library/Caches/ms-playwright` holds no `chromium*` directory any more (the settling run's
  captures on 2026-09-09 used one), and a fresh download of the headless shell timed out through the
  sandbox twice at both CDNs. The run's captures use the system Google Chrome
  (`PLAYWRIGHT_CHANNEL=chrome`, Chrome 155), recorded per measurement; the baseline's token reads
  stay as recorded, and the combined topology re-renders old and new pages in the same browser so
  the layout distances are on one footing.
  Evidence: the measurer's candidate test-launches; the two install attempts; `measurements.json`'s
  `browser` field.

- Observation: The measurer captured two builds while their builders were still writing, because
  the `.incomplete` marker the settling run adopted is set by hand and this run's first wave was
  launched without it. The two are re-measured on the builder's report (the measurer re-measures
  on a changed mtime); the marker is now set at launch for every running cell.
  Evidence: the first measurement pass listed 7 builds with 5 reports in.

- Observation: Five of five first-wave reports say the builder ran `nearest` several times and
  changed a value on a flag — the library build dropped ballpoint blue for teal after seven blue
  neighbours, the compare build dropped a shared-scale signature flagged as a recent fleet motif,
  the pharmacy build rejected a layout the ledger matched — and recorded the rest ("the library
  signup page used the same layout pattern; expected, same job"). Whether the moved values are
  better is the fit and rubric reading's question; that the report reached the moment of choice is
  the mechanism working as designed.
  Evidence: the builders' reports; `ledger-report.txt` in each build directory.

- Observation: **The ledger relocated the accent convergence into the gap it showed.** The seeded
  ledgers' directional accents sat in two bands, red-orange (24–58°) and blue-violet (220–282°),
  and the report flagged a candidate inside either. Of the six `v2.4` builds that chose a
  directional accent, four landed at 90–96° (tape-measure yellow, safety yellow, signal yellow,
  larch gold), one at 70° (damson) and one at 205° (teal): by-job dispersion 0.237 against
  `v2.1`'s 0.805, the lowest of any arm. Each hue has a product reason in its record, and the two
  seeds of the hardware brief and the two of the rebate brief are 2–6° apart. This is the
  taste-calibration file's leftover-accent mechanism — "the one hue no one has taken" is a valid
  constraint and an invalid source — now computed for the agent by the ledger. The family flag
  did the opposite: Atkinson Hyperlegible Next, in three of four 2.0 acceptance builds and five
  of thirteen 2.1 builds, is in none of the thirteen; eleven distinct display families where 2.1
  had nine. The signature flag held too: no content word shared across the two seeds of any
  brief, where 2.1 shared the stamp on the library brief and 2.0 the string-line on the rail
  brief.
  Evidence: D2 and D3 in `results.md`; the stamp-card table under L; the four records' accent
  derivations.

- Observation: The pharmacy brief's two `v2.4` builds compile to one table that carries stock,
  the nearest expiring lot, the controlled count and the open order on each drug's row. The
  structural rater gives both 5 of 5 (q5: a table for lots and stock); the rubric's b-items, which
  ask for expiring lots and controlled counts "as their own set", score them 1, and three raters
  put their d1 at 3. The two instruments disagree about the same design decision: fit reads the
  brief's unit and relation, the b-items read the brief's nouns as sections.
  Evidence: `fit/pharmacy.json`; `rubric/*/pharmacy.json`; the two records' §4.

- Observation: The structural rater's frame moved the baseline. Rated beside the new pages by a
  different rater, the four settling arms score 2.77 / 3.23 / 3.69 / 4.38 where the settling run's
  own raters gave 3.38 / 4.23 / 4.23 / 4.62; the order is the same and the gaps are wider. The
  paired differences in this spec are read within this frame only.
  Evidence: F in `results.md`, both columns.

- Observation: Two canonical shapes survived in `v2.4`: the rebate seed-A page opens with a
  four-cell step strip the instrument reads as a stat row, and the fleet seed-B page carries a
  three-up and a right-hand board the instrument reads as a rail (the structural rater passed it,
  as task content). One `v2.4` console has a sidebar: none.
  Evidence: D4 and the per-build topology lines.

## Outcomes & Retrospective

Thirteen `v2.4` builds exist, pass the mechanical gate (13 of 13; `v2.1` passed 11 of 13 on the
capture-width read), were rated for fit by one blinded rater per brief in the same frame as the
baseline's pages, and were rated by the four-model rubric panel (28 runs, 65 pages). The
`v2.1-one` arm was not built: the arm choice was asked and not yet answered, and its frozen copy
stands ready under `figma-design-workspace/layout-arm/skills/v2.1.0-one/`.

**C1 (the compression holds) — met.** Fit `v2.4` 4.77 [4.38–5.00] against `v2.1` 4.38
[4.15–4.62]; paired by brief and seed +0.38 [−0.08, +0.77], a rise where the bar allowed a 0.3
drop. Every record carries the nine axis lines (13 of 13), the six composition lines (11 of 13;
two carry five), candidates (12 of 13) and the sampler draw (13 of 13), at a mean of 223 lines
against the settling run's 271–302. Nothing the compression cut was missed by the builders.

**C2 (the ledger moves what it watches) — two of three clauses met, one failed in the direction
the calibration file predicted.** No display family appears in more than two builds (clause: three).
The library and hardware seeds share no signature word (the stamp and the ticket are gone). The
directional-accent dispersion fell, 0.805 → 0.237, because four of six directional accents landed
in the one band the seeded ledgers left empty. The report said where the neighbours were and the
agents went where they were not; the calibration rule that the empty band is not a source was in
`taste-calibration.md`, not in the report the agent was reading at the moment of choice.

**C3 (the candidate step) — not run.**

**C4 (quality, exploratory) — no detectable loss, two detectable gains on secondary items.**
Panel d1: `v2.4` 5.12 [4.54–5.63], the highest arm mean; paired +0.35 [−0.19, +0.87] against
`v2.1` and +0.17 [−0.62, +0.88] against `v2.0`, both intervals over zero. Defects −0.35
[−0.60, −0.08] against `v2.1`, interval excluding zero. Conventionality (e1) 3.40, the lowest arm;
−0.60 [−1.23, −0.04] against `v2.1`. The rubric's brief-fit composite is flat (−0.07 [−0.22,
+0.05]), with the pharmacy disagreement above inside it. Panel α in this frame: brief fit 0.79, e1
0.70, defects 0.63, d1 0.56 — d1 still under the quality spec's 0.67 floor, so the d1 reading is
exploratory as pre-registered.

**The shapes.** `v2.4` consoles: no stat row, no sidebar, the dominant region at or over 0.4 of
the first viewport on 6 of 6 (`v2.1`: 4 of 6); narrative pages: no three-up (`v2.1`: 3 of 6).
Console partition distance within category is the lowest of any arm (0.179) and console pq-gram
the highest of the 2.x arms (0.632): the pages share the brief's form and differ in their trees,
which is the reading the settling retrospective predicted for a grammar that works.

**What the run settles.** (1) The compressed SKILL.md loses nothing the references carry; the
record got shorter and more complete. (2) A nearest-neighbour report moves families and motifs
and relocates hue convergence to the complement of what it shows; the report needs to say so, or
show the coverage rather than the neighbours. (3) Fit rose with every version for the fifth time
and is the instrument to hold the next change to; partition is reported and did what it does.
(4) On the panel, `v2.4` is the first arm whose deliverability mean is above every other arm's,
with fewer defects than `v2.1` and the least conventional pages, at thirteen pages a side.

**Retrospective.** Reusing the 52 settling builds as the baseline cost nothing and made the
comparison frame honest; the fit rater re-rating old and new in one frame is the right form.
Setting the `.incomplete` marker at launch should be in `cells.mjs`, not by hand. The ledger's
first run found the mechanism's failure mode in thirteen builds, which is what a pre-registered
diversity clause is for. Cost: 13 builders at 0.35–0.46 M tokens (about 5.2 M), 7 fit raters at
about 0.08 M, 28 rubric raters at about 0.09 M (about 2.5 M), roughly 8.5 M subagent tokens over
about three hours of wall clock.

## Deferred

- **The gap flag.** The `nearest` report should name the leftover: when the candidate's accent
  sits in a band no recent build occupies while the recent builds cluster in one or two bands, the
  report says so and repeats the calibration rule (the empty band is a constraint, not a source).
  A coverage line — the recent hues as a 12-bin wheel — beside the neighbour list is the simplest
  form. A user decision, because it changes what the report tells the agent to do.
- **The `v2.1-one` ablation**, 13 builds, frozen copy ready; pending the arm choice.
- A compact table form for the nine stance lines and the six composition lines in `DESIGN.md`,
  the stance spec's suggested fix for the record budget; this wave does not change the record's
  shape.
- The structured ledger block in `DESIGN.md`, if the flag form proves to be skipped (it was not:
  13 of 13 appended an entry).
- `cells.mjs` setting the `.incomplete` marker at `init` for every unbuilt cell.
- The fit rater and the rubric's b-items disagree on a page that folds the brief's nouns into one
  table; which reading the doctrine wants is a judgment to record in the composition spec.

## Revision Notes

- 2026-10-12: written before any edit; part C's measures declared before any build.
- 2026-10-13: parts A and B shipped as 2.4.0 (commit a9e714c0); the `v2.4` arm built, measured,
  fit-rated and panel-rated; Outcomes, Surprises and Deferred written. Evidence under
  `docs/research/data/2026-10-12-layout-arm/`. The ablation arm and the gap flag await the user.
