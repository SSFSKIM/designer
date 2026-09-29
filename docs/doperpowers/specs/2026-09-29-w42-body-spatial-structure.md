# W42 — the body's spatial structure: an encoded heavy blur, a one-sided narrow term, CSS-pixel widths, all four window states (2026-09-29)

**Status: v2.1 DRAFT (drafted for the parent). v2 folded the adversarial review of v1, the
parent's rulings on v1's drafter's notes and on every review finding, the user's Decision Logs 5a
and 5b, and memo D (Apple's declared layer tree). v2.1 folds memo E (that tree re-fitted on memo
C's cells), the parent's rulings on memo E, and the review's own text for findings 9 and 15–17
with the parent's three calls on v2. No point is pending. Decision Logs 1, 2, 5a, 5b and 6 RULED
by the user 2026-09-29; Decision Log 3 ruled by rule at charter and extended by the parent;
Decision Log 4 and Decision Log 5's remainder open. Ledger sections §5.194–§5.197 reserved
(§5.198 if a child splits).**

Points marked **Drafter's note** are v2.1's own; earlier notes were ruled by the parent and are
written into the text they concerned (Revision Notes).

## Purpose

W41 (§5.191–§5.193) identified **E3**, the light receded body's uniform response: luma through
F, a curve of seven measured neutral ordinates, plus a level-dependent radial chroma gain g, both
on encoded luma. E3 closes at one code on uniform backdrops, held-out cells included. It did not
ship. Applied per pixel to vitrea's blurred backdrop, it read 210 codes on the light-inactive
checkerboard body where Apple and the old group-level solve read 188. It failed L1 on every
inactive checkerboard cell and M2 on every light-inactive photo cell (§5.193 §3). The user ruled
"Don't land; close W41", and W41's Deferred at close 1 made the receded body's spatial argument
the next wave's first question.

The user set W42's scope on 2026-09-29: **"Widen W42 to the body's spatial structure in all four
window states (encoded heavy blur, one-sided detail, CSS-pixel widths); E3 becomes its
light-unfocused tone curve."** Their plan is an offline pass on existing cells first, then a
native capture with a structured holdout. The offline pass is grounding memos A, B and C, plus
memo D's dump of Apple's layer tree (Grounding Baseline). What they found makes E3's failure one
instance of a gap across the whole material:

1. **Apple's body is two spatial scales composited one-sidedly, in all four endpoints.** A
   narrow component carries the visible detail. A wide component sets a floor in the light
   scheme and a ceiling in the dark one, which the detail can rise above (light) or fall below
   (dark) and not cross the other way (memo B §0). On the checkerboard the native suppressed
   side stays within 2.6 codes of zero while vitrea's shipped body draws it: shipped dome ratios
   −1.04 to −1.31, where any linear filter in encoded space reads −1 (memo A, question 2). A
   mirror statistic that is zero for any two-sided linear system reads 0.2–0.5 on Apple and
   ≤ 0.024 on vitrea (memo C §1).
2. **The wide component averages ENCODED values, locally.** Encoded averaging before the tone is
   the only order within about 3 codes in all four endpoints, and linear averaging misses by
   ≥ 12 codes, except that dark rrect-md at span 96 is not decisive (memo B §0, §3). The
   checkerboard's black cells read 186.8–188.1 against F at the encoded mean, 187.8; the
   linear-light mean predicts 212.3 (memo A, reading 1).
3. **Widths hold in CSS px, and the declared opacity scales the narrow blur's reach.** Apple
   declares the narrow term as ONE radius-5 blur and the wide one as a radius-8 fill (memo D).
   The narrow blur's opacity is 0.8t at the centre when active, falling to 0.4t at 1 pt inside
   the edge, and 0.4 + 0.4t when receded, with t = clamp((s − 64)/96, 0, 1) (memo D §0, §3).
   Memo E reads that opacity as SCALING the blur's radius, σn = k·5·o, not as mixing a blur with
   the sharp backdrop, and reads k at 1.98–2.17 in all four endpoints: the radii are in points,
   σn is about 10·o pt and σw about 16–17 pt (memo E §0). Every declared body input is the same
   at 1x and 2x (memo D §4).
4. **Apple's layer tree has this shape.** One capture per surface (the shape's box plus a
   margin, at half resolution), one private filter, and no other blur anywhere: memo E checked
   224 surfaces with no departure (§0, §1). The wide term is composited Lighten (light) or Darken
   (dark) at a declared 0.9, then Normal at the glass slider's position, 0.5 on the bed. Memo E
   refutes the declared 0.9 on pitch-64 receded cells unless the heavy blur's support changes it,
   so λ is fitted and w stays fixed at 0.5. The face colour matrix after it gives the native black
   floor within 0.6 code in all four endpoints (memo D §6) but misses the level above it (memo E
   §2f), so the tone stays Apple's measured curve. Nothing in the tree adapts to the backdrop
   (memo D §0).
5. **Two shipped defects sit on the same line.** vitrea fixes both body widths in DEVICE px (D1)
   and blurs and mixes in linear light on both tiers (D2) (memo C §7). They are part of the law
   (Design), not a separate fix.

W42 declares that structure as a law with its rivals before any pixel of a new bed exists (G0);
rehearses every landing referee on the grounding readings before the sitting (G0); captures the
bed that identifies what existing cells cannot (G1); fits it on the new bed's calibration set and
transfers it to validation (G2); and passes the canonical landing referees on the candidates'
calibration/validation renders **before** spending its one exposure on the structured holdout H.
That order is the lesson W41 paid for: W41 spent the W39 holdout on E3 (§5.192 §25), and L1 and
M2 then failed on canonical calibration/validation cells that could have been read before the
exposure (§5.193 §3). **The wave lands what closes (G3), conditional on every referee passing**
(Decision Log 1, RULED: "Land in this wave, if every referee passes").

**Two candidates carry the structure (Decision Log 5b, RULED).** Candidate 1 composes the
identified structure with the LANDED tone: the shipped solve in three endpoints and, for light
receded, E3's F extended above 150 by the new bed's greys. Its blur structure is scored against
the law combined with that tone, and the gap to Apple's level is recorded as the existing named
miss. Candidate 2 takes Apple's grey tone curve from the new capture in all four window states,
measured from family A's greys and counted by its ordinates as E3's F is; it lands instead only
if it passes every check, which could close W36's grey-middle miss too.

**What stays open after the grounding.** U1, the receded pose's one-sided weight drifting with
pitch inside one shape, survives memo E: the drift persists under Apple's declared constants and
points at the heavy blur's reach 16–48 pt out or its support, which the new bed is built to read
(memo E §3). Rims, edge bands, the stroke and Apple's dark exterior contour stay where W35–W41 left
them.

## Parent-Level Acceptance

Each clause names its metric, the bed it is read on, the bar and what stops the wave.

1. **Declared before the bed exists (G0).**
   - *Metric:* the declaration's SHA-256, committed and independently reviewed, against the
     timestamp of the first native capture of the new bed.
   - *Bed:* the declaration itself. It holds every family of Design with its parameter count,
     working space, support and span or depth grading, memo E folded; both candidates' T and the
     light receded F extension (X35); the tie-break; the law's accessibility behaviour; the bed's
     families A, B, B', C, D, E, F and H with exact ids and each U-item's family; the split
     (calibration, validation, H), enforced by the wave reader and launcher; the W42 web plan;
     the region statistics and their populations; the survival and closure rules (clauses 6 and
     11); the landing-referee gate (clause 10); the stops.
   - *Bar:* every item present and hashed before G1's first capture. Nothing is fitted to native
     pixels in G0 beyond the grounding readings, which are recorded as readings.
   - *Stop:* a capture that precedes the hash, or a declaration change after the first capture,
     voids the sitting as the bed. Its captures are kept as evidence and never read as the bed.
2. **The instrument is proved before it reads Apple (G0).**
   - *Metric:* recovery of known parameters.
   - *Bed:* synthetic renders of every declared family through native T, quantised ±0.5, on the
     new bed's declared geometries; and vitrea's own existing captures, where the kernel is known
     from the code, on at least two backdrops and several pitches (the grounding's reading
     discipline).
   - *Bar:* tolerances G0 declares before the proof runs, no looser than the grounding readers
     achieved: memo C recovered λ and w to ±0.03 and widths to ±0.05 at the quantisation floor
     (rms 0.40–0.42); memo B recovered widths within 3–10 % and the share within 0.03–0.1 at 2x;
     memo E recovered k to three decimals at rms 0.40–0.42 and separated the wrong reading by
     ≥ 2.60 codes and the wrong unit by ≥ 4.65 (§2b). A two-sided control reads the mirror
     statistic at vitrea's level (memo C: ≤ 0.024 at p ≥ 8). A known-space control shows the
     reader cannot manufacture a knee: memo C's encoded fit on vitrea's linear captures returned
     λ 1.4–1.5, so the knee is established by S and by every linear fit's loss, never by λ
     alone.
   - *Stop:* a reader that fails its control does not read Apple (memo B's two-Gaussian photo
     reader failed its control and was not used). A parameter the synthetic recovery cannot
     separate is declared non-identifiable on this bed before any fit.
3. **Every landing referee is rehearsed before the sitting (G0; X39).**
   - *Metric:* L1, M1, M2 (as Decision Log 5a ruled), C1, X1, E2 and the two directional stops
     of clause 10, each computed by memo A's body-swap: the shipped render with only the body
     argument replaced by the grounding law readings (LT at memo E's readings) composed with the
     landed T.
   - *Bed:* each referee's adopted non-holdout population, in all four endpoints (memo A
     rehearsed the light receded endpoint only).
   - *Bar:* each referee's adopted bar. A referee that fails whatever the structure's
     coefficients, because of T, a membership or its own reading, fails "by construction".
   - *Stop:* a referee failing by construction goes to the user BEFORE the sitting, with its
     numbers. E2 is already a not-worse-than-baseline stop; if the rehearsal shows it failing by
     construction, the user rules its reading then.
4. **The sitting is attested (G1).**
   - *Metric:* the attestation of every capture.
   - *Bed:* the declared bed: four passes per scale (scheme × pose); per 2x pass 88 cells light
     active, 91 dark active, 86 light receded and 89 dark receded, and 15 per 1x pass (Design,
     "The bed"); **seven runs** (Decision Log 2, RULED); the declared no-glass references and
     sentinels. `dump-layers` over the whole
     declared bed is the sitting's first step: it needs no grant, only the idle Mac.
   - *Bar:* on every capture, the four X6 facts (Reduce Transparency 0, Increase Contrast 0,
     `NSGlassTintAmount` 0.5, zero foreign browser or capture processes after the measured idle
     window) and W34 X4's native set (build 26A428, `ButtonShapesEnabled` 0, Show Borders 0,
     the display mode before and after, the colour context, the side bundle's cdhash and
     `LC_BUILD_VERSION`, `deterministic`, the pose as the harness attests it, the requested and
     actual window frame and the shape's attested `frameOrigin`). Every dump of the declared bed
     reads the declared inputs memo D reads (BlurRadius 5, BlurFill 8 at 0.9 and Normal 0.5, the
     opacity laws, the backdrop scale and margin).
   - *Stop:* a run that fails to attest is quarantined and named. A wrong mode, a lost grant, a
     failed idle window or a foreign process stops the pass; there is never a hidden retry. A dump
     that departs from memo D's declared configuration stops the sitting before its first capture.
     Nothing is read against vitrea in G1.
5. **Repeats before thresholds; the archive of record (G1).**
   - *Metric:* the bar per cell, region and channel: 0.5 plus half the largest pairwise
     separation of the run medians, computed before plurality (W39's rule).
   - *Bed:* every admitted run, the losing states preserved.
   - *Bar:* the bar published before G2 opens; a zero observed spread buys no tolerance. The
     archive is complete, published as a release asset named by SHA-256 and byte size, and
     replayed identically with the raw root denied.
   - *Stop:* G2 does not open until the bar and the replay are committed.
6. **Identification on calibration, transfer on validation (G2).**
   - *Metric:* the declared region statistics per required channel: checker cell-core medians on
     the knee and far sides, patch cores and surround annuli, step plateaus and transition bins,
     uniform deep medians. Per-cell deep-body rms is reported beside them and never gated.
   - *Bed:* the new bed's calibration set, which is the fit's support; the canonical probe cells
     may corroborate (X34) but are never its only support. Its validation set, read-only
     transfer. Family F is bridge-only: it ties the bar across sittings and is not under this
     clause's survival rule.
   - *Bar:* W39 clause 8 verbatim, with the structure inverted through NATIVE T measured on
     family A per endpoint. A family SURVIVES only at max(1 code, bar) on every required channel
     of every calibration AND validation cell and region before the freeze; survivors within
     max(3, sum of bars) at every admitted discriminator are "insufficient resolution", and the
     declared tie-break chooses among them (Design). X31's three statuses and X21's one-sided
     censoring carry. Fits are least squares and minimax, equal weight per cell; a family with
     width parameters is non-linear, so its search is a bounded deterministic multistart stated
     as LOCAL.
   - *Stop:* an endpoint with no survivor is this wave's negative at its resolution; Decision
     Log 3 then applies. No family is added after the bed's first read.
7. **Uniform invariance (G2).**
   - *Metric:* the rendered deep-body median on uniform cells.
   - *Bed:* the canonical uniform calibration/validation cells and the new bed's family A, each
     rendered with the candidate and with every W42 spatial gate at its identity.
   - *Bar:* every family maps a constant backdrop to itself (memo A), so the two renders agree
     within one code in every endpoint. Candidate 1's reference is the shipped render in the
     three endpoints whose T is the shipped solve, and E3 with its extended F alone in the light
     receded endpoint. Candidate 2's reference is its own T with the spatial gates at identity.
   - *Stop:* a departure is an implementation defect, found and fixed before clause 10's gate.
8. **The runtime base (G2).**
   - *Metric:* PNG byte identity.
   - *Bed:* a sample of the canonical bed declared in G0 (every backdrop kind, both scales,
     both poses, both schemes), rendered with the SHIPPED documents at G2's base, which includes
     PR #2 (merged at `399c6bbf`).
   - *Bar:* byte-identical to the canonical capture tree, after `check-capture-tree` exits 0 on
     that tree.
   - *Stop:* no candidate render until any difference is attributed and resolved (X37). The same
     proof is repeated whenever the base moves before G3's seal.
9. **The rendered candidates on the new bed (G2; W41 clause 11; Decision Log 5b).**
   - *Metric:* clause 6's region statistics, read on vitrea's render with the same instrument.
   - *Bed:* the new bed's web-plannable calibration and validation cells (the W42 web plan).
   - *Bar:* **candidate 1** within max(1 code, bar) of the identified structure composed with
     the LANDED T; the rendered-against-Apple gap is recorded as the named level miss
     (§5.178 §2 reads the shipped solve's knot-3 miss at +0.0508 / +0.0201 / −0.0207 / −0.0029
     linear). **Candidate 2** within max(1 code, bar) of Apple directly. What these validation
     renders read is the T that would ship.
   - *Stop:* a candidate whose operator fails is removed from the code before G2's merge; its
     diff and renders are kept as evidence.
10. **The landing referees pass BEFORE the exposure (G2; X33).**
    - *Metric:* the L1, M1, M2, C1, X1 and E2 cuts, regenerated from each candidate's renders by
      W41 G2's ported referees (`results/2026-09-29-w41-g2-landing/referees/`) in their
      candidate-admission mode; two directional numerical stops, the impulse halo/annulus
      statistic and the photo band-pass chroma energy; the owner test
      (`adopted-thresholds.test.ts`) on the candidate's scratch union over all six gated macOS 27
      profiles; and eye sheets chosen BY STRATUM: uniform, binary structure, text, impulse,
      photo, gradient.
    - *Bed:* the candidate's renders of each referee's adopted non-holdout population: the
      canonical calibration/validation cells, plus the probe rows X1 and E2 already admit, on the
      WebGPU tier, 1x and 2x, in a scratch stage that is never published; for the owner test, the
      light generation's four profiles and the dark generation's two. The eye sheets show native
      | shipped | candidate with ΔE×8. The text stratum reads the canonical probe hc-text cells
      and the gradient stratum the W39 archive's web-plannable gradient cells: both are looks,
      not referees.
    - *Bar:* the adopted rows as they stand when G2 opens.
      - L1 ≤ 0.055 absolute, with growth ≤ 0.005 against its W33 baseline. The tinted photo
        inactive growth (+0.0131 / +0.0136 under E3, §5.193 §3) is read as written.
      - M1 median in [0.8, 1.2], cells in [0.6, 1.4].
      - M2 as Decision Log 5a ruled: the 2 % stays; a cell that moves toward Apple's own texture
        reading, and not past it, is a named miss with Apple's value beside it; a cell that moves
        away from Apple, or past it by more than 2 %, fails. The reference re-baselines at the
        adopting gate (W32 Decision Log 4).
      - C1 ≤ 0.0042 per bed × span. X1 zero pixels above native black. E2: no measured bin worse
        than its frozen baseline by more than one code, and UNMEASURED never a pass.
      - The two directional stops: no cell farther from Apple than the shipped render at the
        statistic's declared resolution.
      - The owner test: no failure that the base's own scratch union at the same membership does
        not show.
      - Named misses stay named and none is added, except through M2's named-miss path above.
      - The eye: the parent's verdict per stratum is recorded, and no stratum reads visibly
        further from native than the shipped render.
    - *Stop:* any failure means no exposure. H stays sealed, the result is recorded in §5.196,
      and the candidate returns to identification on calibration or the wave closes at the
      negative. If only L1's light-solid inactive growth fails with the extended F, the light
      receded tone stays the shipped solve and the spatial law lands over it, a partial adoption
      inside Decision Log 3. **This is the lesson of W41**: a holdout exposure is spent only on a
      law that has already passed every landing referee that can be read without it.
11. **The one exposure on H (G2; X26 as carried).**
    - *Metric:* clause 6's statistics on the held-out cells.
    - *Bed:* H, declared before capture (8 cells per 2x pass, 6 of them structured, and 2 per 1x
      pass), its payload behind the procedural boundary until the receipt.
    - *Bar:* the identified structure through native T against Apple's held-out pixels at
      max(1 code, bar) on every measured cell of the claimed endpoints; candidate 2's render
      against Apple's held-out pixels at the same bound; candidate 1's render against its frozen
      structure-with-landed-T prediction, with the gap to Apple recorded as the named level miss.
      A censored held-out cell is UNMEASURED and counts toward neither pass nor coverage; the
      measured coverage is reported. The rendered H predictions are produced blind from the public
      declaration and frozen by hash before the receipt, which recaptures them and requires
      equality before any native held-out pixel is scored.
    - *Stop:* a failure means the law does not close and nothing lands. H is spent either way,
      and no candidate changes after the receipt.
12. **Nothing shipped moves until clause 11 passes (G0–G2; W39 clause 9).**
    - *Metric:* the protected-path diff; `freeze.py verify`; the goldens.
    - *Bed:* `scenes.json`, `fixtures/`, the frozen matrix, `results/generations/`,
      `results/superseded/`, the six material documents, the generated profiles, the goldens and
      every adopted threshold.
    - *Bar:* no byte moves; the freeze reads 1,818 at every merge. The one ruled exception is
      G0's M2 named-miss derivation beside `chromaStructureMisses()` in
      `adopted-thresholds.test.ts`, pinned by an owner case, with the 2 % unmoved (Decision Log
      5a). Operators added in G2 sit at their identity behind zero gates, appended to the
      identity table, so no document digest moves and the goldens stay byte-identical.
    - *Stop:* a protected byte that moves stops the merge.
13. **The landing (G3), on Decision Log 1's terms.**
    - *Metric:* the seal's identity against G2's frozen renders; the canonical stage read on both
      tiers; clause 10's cuts and the owner test regenerated on the stage;
      `tier-coherence.test.ts`; the CSS carry's Chromium proof; `check-capture-tree`.
    - *Bed:* the canonical stage under the CLAUDE.md recipe, a light and a dark generation, both
      tiers, holdout membership declared and read last.
    - *Bar:* the sealed documents re-render G2's frozen predictions byte for byte at G2's frozen
      base (a moved base is re-proved through clause 8 first); clause 10's bars on the stage;
      Decision Log 4's carry, approximation or decline measured per leaf in Chromium;
      publication once through W40's publisher; the capture tree copied and
      `check-capture-tree` exit 0; the eye sheets over the whole canonical bed; the changeset
      (`@vitreajs/vitrea-web` minor); the release checklist with CI green at the release commit.
      A receded-only reseal lands only after the tracker's M2-reference fix (Decision Log 3).
    - *Stop:* a rendered prediction that moves between G2's freeze and the seal stops the landing
      and returns the law to identification with a new bed. A referee failure on the stage stops
      it for Decision Log 5. `pnpm release` is the user's hand.
14. **The canonical holdout, once by artifact (G3).**
    - *Metric:* the adopted rows that read holdout, and the eye.
    - *Bed:* the canonical holdout (`holdout-configuration/configuration.py record`). It carries
      structured backdrops in both poses: hc-text on capsule and rrect-md, checkerboard and photo
      on rrect-lg, and the glass-over-glass pairs.
    - *Bar:* the adopted bounds that apply to its rows, read once per frozen configuration.
    - *Stop:* a miss is recorded and goes to Decision Log 5; it is never re-read.
15. **Every gap is recorded.** A family that fails, an endpoint left at identity, a leaf the CSS
    tier cannot carry, a level miss seen through the landed T, a unit memo D leaves open: each
    with its numbers in §5.194–§5.197, the Deferred list or the tracker.

## Grounding Baseline (main at `9d7e171c`, W41 closed)

**The memos.** Grounding memos A, B and C were written read-only on the repository under one
set of rules (`w42-grounding-common.md`: never a holdout or recorded native pixel; prove each
reader on vitrea's own captures first; read features at their own scale; separate the surface's
own light from its transmission; keep censored channels one-sided). Their fits are exploratory
readings that size an effect, never a proposed coefficient set. Memo D read Apple's declared
layer tree and no pixel; memo E re-fitted that tree on memo C's cells under the same rules. All
of them, with their briefs, the parent's three rulings files and a SHA-256 manifest of their
scratch, are committed under
`packages/calibration/results/2026-09-29-w42-grounding/`; the raw scratch stays on the machine
under `~/vitrea-w42/grounding/`.

| memo | question | evidence read |
| --- | --- | --- |
| A, `w42-grounding-argument.txt` | the argument E3's F and g are evaluated at | canonical cal/val light-inactive checkerboard, impulse, photo (20 cells, 1x and 2x), light-active and dark cells for its question 2; W39 gradient calibration rows; G2's committed native body means for hc-text and the pitch series; both web trees |
| B, `w42-grounding-kernel.txt` | Apple's body blur: kernel, space, pose; the capture that identifies it | canonical cal/val in all four endpoints; committed uniform readings from the W39 and W34 archives; vitrea's code map and captures |
| C, `w42-grounding-probe.txt` | the probe series, the W29 dump, the smallest identifying capture | A's and B's evidence plus the canonical PROBE cells in every endpoint and scale, and the spent W34 archive's checkers |
| D, `w42-dumps.txt` | Apple's layer tree across spans, poses, schemes and scales | `dump-layers` on the W39 side bundle: 24 scenes × 4 endpoints × 2 scales, 208 surfaces, a settle-16 repeat; no pixels |
| E, `w42-grounding-refit.txt` | the literal layer tree (LT) fitted on memo C's cells through native T and through the literal face matrix; U1 re-tested | every dump file (224 surfaces); memo C's cells and scratch, imported read-only; the spent W34 archive's capsule |

**The repeat bar under the grounding.** Canonical cells are single captures (`repeatNoise` 0,
`runsPerCell` 1); one code is the resolution. The W39 and W34 seven-run bar is ≤ 0.5 code and was
not measured on the canonical cells; memo A calls the cross-sitting bar unmeasured. Family F's
bridges tie the new sitting to the canonical and probe sittings and give it a reading.

**The readings the law is built on** (all exploratory; units CSS px unless marked):

| question | reading | source |
| --- | --- | --- |
| averaging space of the level | checker black cells 186.8–188.1 against F(encoded mean 127.5) = 187.8; linear-light mean predicts 212.3. Impulse 133.0 against 132.9, linear 137.9 | A, reading 1 |
| space, all four endpoints | encoded averaging then T within about 3 codes everywhere; linear averaging misses by ≥ 12. Dark active / receded rrect-md at span 96 is not decisive ([121, 134] / [114, 127]) | B §0, §3 |
| one-sidedness | native suppressed side within 2.6 codes of 0; shipped dome ratios −1.04 to −1.31; mirror S 0.2–0.5 (Apple) against ≤ 0.024 (vitrea) | A q.2; C §1 |
| W local, not group | a group mean loses by 5–10× rms on every pitch-64 rrect cell; on the W34 active capsule it reads 3.5 / 4.5 rms against the canvas's 1.25–1.27 / 0.99–1.04 (light / dark), a 2.8× / 4.5× loss as the review read it | C §0, §2a |
| σw, full ranges | active rrect cores 10–13 (dark rrect-lg 10); W34 active capsule 24 / 17 on the canvas, 14 / 13 on its footprint. Receded rrect cores 13–19 across supports (light rrect-lg box 19); W34 receded capsule 12–15 on its footprint, 8–10 on the canvas | C §2a |
| receded W support | footprint-limited; box fits best: W34 receded capsule 0.35 rms footprint against 1.5–2.2 canvas | C §0 |
| active W support | big shapes cannot tell canvas from footprint; the capsule prefers canvas, but it is all refraction | C §0 |
| σn active | 0.8 at 1x and 0.4 at 2x on spans 32–44 at every pitch 4–64 (0.8 dev: the half-scale resampling floor); 2.0 / 4.0 / 4.5 at spans 96 / 128 / 160, both scales | C §0 |
| σn receded | 4–4.5 at spans 32–44, 5.5–9 at 96–160 (noisy); B reads 4.3 → 5.4 from span 44 to 96; σ/opacity lies between 7.5 and 11.8 on six light cells | C §0; B §0; D §5 |
| active knee | three joint fits: light capsule 1x λ 0.88, w 0.506 (per-cell 1.22–1.58); dark capsule 1x λ 0.91, w 0.497 (1.11–1.55); light rrect-md 2x λ 0.88, w 0.483 (1.31–1.58). A hard max (λ = 1) loses +0.6 to +1.2 rms; a soft knee adds nothing | C §0, §2c |
| receded knee | not closed: pitch-16 knee sides flat at W need λ ≥ 0.98; pitch-64 cores want 0.6–0.8; a shared fit leaves 0.9–1.5 codes per cell | C §0 |
| space on non-binary structure | light lc16 within 0–2 codes encoded, linear +3.6 to +4.2; hc-text 0.6–6 encoded against 16–48 linear. Dark active lc16 refits favour linear slightly (encoded 1.0–1.2 against linear 0.8–1.0); light active rrect-ml/lg and dark spans ≥ 96 are T-limited | C §0, §2d |
| chroma | takes the heavy argument only (s about 10–12), no sharp or one-sided part | A |
| gradients | native slope ratio 0.61; a canvas blur keeps the ramp (strip max 1.95–2.00 codes); a footprint-normalised blur at s = 12 reads 0.85–1.01 | A, reading 3 |
| hc-text | F at each cell's own footprint encoded mean: rrect-lg (177.6) +0.2 / −0.1, hc-text-7 rrect-md (156.5) +1.0 / +1.1, hc-text-28 rrect-md (171.6) +0.3 / +1.5 codes; the positive part is the checker's one-sided excess over a white majority | A |
| 1x fine pitches | pitches 4 and 8 at 1x pass more contrast than any Gaussian allows; a decimated backdrop | C §2e |
| size of the one-sided effect | memo A's reading C7 (encoded heavy + k·max(0, sharp − heavy)): worst-cell luma rms 1.3 (2x) / 3.9 (1x) on the checker, ≤ 0.6 impulse, ≤ 1.5 photo | A |

**Apple's declared configuration** (memo D; declared inputs to a private filter, pointers until
the pixels agree, X38). One size variable drives every span-graded input, t = clamp((s − 64)/96,
0, 1), with s the surface's short side; nothing moves for s ≤ 64, and the clamp at t = 1 is
inferred (160 is the largest span dumped). Seventeen closed-form laws reproduce all 104 surfaces
at 2x to below 1e-3.

| input | light active | light receded | dark active | dark receded |
| --- | --- | --- | --- | --- |
| BlurRadius | 5 | 5 | 5 | 5 |
| BlurOpacity, centre → 1 pt inside the edge | 0.8t → 0.4t | 0.4 + 0.4t, flat | 0.8t → 0.4t | 0.4 + 0.4t, flat |
| BlurFill radius; Lighten / Darken; Normal | 8; 0.9 / 0; 0.5 | 8; 0.9 / 0; 0.5 | 8; 0 / 0.9; 0.5 | 8; 0 / 0.9; 0.5 |
| face black / white; saturation; fill | 0.40 / 1.03; 1.2; white α 0.20 | 0.40 / 0.96; 1.2; white α 0.20 | 0.125 / 1.125; 1.3; none | 0.08 / 1.125; 1.3; none |
| MaxLuma / MaxLumaSDR; Clamp | 1 / 0.94; 1.06961 | 1 / 0.94; 1.0 | max(0.35, 0.6 − 0.6t); 1.30831 | same |
| backdrop scale; marginWidth | 0.5 (0.25 on rrect-lg); 0.35 s if s > 64, else 16 | 0.5 (0.25); 1 dev | as light active | as light receded |
| bleed blur radius; opacity | 0.35 s if s > 64; 0.5t | 0 | 0.35 s if s > 64; 0.8t | 0 |

- **Normal is the slider.** W29's "Normal 0.546" was the glass slider's position when W29
  dumped; Normal equals `NSGlassTintAmount` at five slider positions, and the light fill alpha
  tracks it too (0, 0.10, 0.20, 0.2275, 0.50). The bed attests 0.5, so w is **fixed at 0.5**.
- **Scale.** 1x and 2x are field-for-field identical apart from four quantities that equal one
  device pixel at each scale. The backdrop capture scale is 0.5 at both display scales, so the
  backdrop is sampled at 0.5 px/pt at 1x and 1 px/pt at 2x (rrect-lg 0.25 / 0.5).
- **Backdrop and position switch nothing**: dark-solid, checkerboard, light-solid and photo give
  identical inputs over 12 component-surface groups × 4 endpoints; rrect-md-clear20 is rrect-md.
- **The face against native uniform levels** (memo D §6): the declared encoded affine gives the
  black floor within 0.6 code in all four endpoints; light follows it within 1 code up to input
  88, then runs 1–3 codes high; light receded white is the 0.94 cap (239.7 against 240). Dark is
  strongly compressive above the floor, not a hard cap at MaxLuma, and its span dependence
  matches the MaxLuma law in sign (dark grey-128 134 / 127 at s ≤ 64 and 121 / 114 at s = 96).
  Light active grey-128 rises from 195 to 198 at s = 96; no declared face input explains it.

**Memo E's readings** (EXPLORATORY: each sizes an effect on memo C's deep masks and is never a
coefficient; canonical cells are single captures, so no repeat bar stands under them):

| question | reading | source |
| --- | --- | --- |
| the tree | 224 surfaces (2x, 1x, settle-16), 0 departures from memo D's laws; one CABackdropLayer per surface capturing the box plus margin, one `glassBackground` filter, a CASDFLayer mask, and no other blur (every SDF `gaussianRadius` 0) | E §0, §1 |
| the opacity's meaning | it scales the radius-5 blur's reach, σn = k·5·o: pooled rms 2.25 / 2.07 / 3.45 / 3.01 (light active / light receded / dark active / dark receded) against the mixture's 3.61 / 4.95 / 5.31 / 6.81; out of sample the light receded rrect-md impulse peaks at 3–5 codes native, 25–26 under the mixture and 3.8–3.9 under the radius scale | E §0, §2c, §2h |
| the units | points: k reads 1.98–2.17 in all four endpoints; with the radii in texels the pooled rms is 6.28 / 6.63 / 7.89 / 9.77, in device px 5.47 / 5.36 / 7.19 / 8.02; no rrect-lg ratio comes near the 2 texels would give | E §2c, §2g |
| one k or two | one k per endpoint: 2.38 / 2.11 / 3.47 / 3.03 at k 1.983 / 2.035 / 2.094 / 2.074; a second k buys 0.02–0.13 | E §2c |
| the capture | memo C's 0.8-dev Gaussian floor applied before the knee; a literal box decimation reads 7.32 against 1.46 on the 1x pitch-4 capsule | E §0, §2c |
| LT against memo C's per-cell fits | of memo C's 28 cells at ≤ 1.00 code, LT reaches ≤ 1.00 on 10 and is within +0.25 on 8; median excess +0.51 / +0.51 / +1.16 / +0.85; per-cell medians 1.64 / 1.79 / 2.33 / 2.43; 2 parameters per endpoint against memo C's 4 per cell | E §0, §2c, §2e |
| U1 | not closed: on the W34 capsule, light receded, λ 0.68 at p64 against 0.92–0.94 at p16 (non-overlapping intervals, both scales), dark 0.72 / 0.78 against 0.90 / 0.92; λ flat across hinge-gap bins, so the drift lives in W's reference at 16–48 pt; also in dark active on the small shapes at p64 | E §3a, §3c |
| composite order | R1 (T applied to C and W before the fill) 2.07 / 3.07 against LT's 2.07 / 3.01 on light / dark receded, inseparable on light even from a known truth; R2 (the fill on the sharp capture, the narrow blur last) 7.01 / 9.65, rejected | E §3b |
| the face as T | costs +0.35 to +2.26 pooled in light and +10.7 to +15.1 in dark over native T; before or after the knee ties with native T | E §0, §2f |
| rrect-lg and the bleed | light active rrect-lg k_n 1.16 against 1.73–1.74 on md and ml (unidentified: the bleed or the 0.25 realisation); dark active k_w 2.23 / 2.54 / 2.80 on md / ml / lg, pointing at the undeclared bleed | E §2e, §2g |

Memo E's limits: `gradientOvalization` 0.5 (active, s > 64) is unmodelled in its o(d); its
narrow reading interpolates five blur levels across depth (0.02–0.30 code against a 41-level
reference, max 1.25); LT there carries no bleed, refraction or highlight (§5).

**The shipped body** (memo B's float64 replica reproduces 11 web cores at rms 0.27–0.38): the
centre is enc(R + B·((1 − k)·Ksharp∗b + k·Kdeep∗b − L̄)) on the LINEAR-light backdrop b, with
Ksharp 1.58 dev at both scales and Kdeep about 14 dev (L4, platykurtic). The dark active document
names no heavy tap (`sizeHeavyTapSigma` 0 at both scales, lines 133–134) and the dark receded one
names 2x only (line 83), so the dark heavy is the chain level `scatterLod` (`material.ts:1222`,
`wgsl/optics.ts:1052`; memo B: LOD 3.32, 9.7 dev at 2x dark active). The tone
argument is group-level (the source mean when active, the silhouette encoded mean when receded).
The CSS tier blurs through `feGaussianBlur` in linearRGB. Neither tier has a knee (memo B §1, §6).

**The shipped documents.** macOS 27 light active / dark active / light receded / dark receded:
files `85ad7f7e3e0d` / `0eac5b294cc2` / `30fbe05986ae` / `5cec8c961201`, resolved digests
`be13dae45098fc89` / `2a4323f33df8d799` / `b0d0d8dacc6a03af` / `7c454858a3cbad5b`. The frozen
macOS 26.5 pair is `b2b570e4adcea8fb` / `874be66ea501621b`. E3's zero-gated identity-table group
(`bodyE3Strength` 0) is on main at the identity in every document (W41 Deferred at close 2).
`freeze.py verify` read 1,818 entries at drafting.

**The runtime base.** PR #2 (`perf/demand-driven-frames`) moves the root's frame loop to
demand-driven frames and edits `renderer-webgpu/src/renderer.ts`, `src/backdrop.ts`,
`src/pyramid.ts` and `src/silhouette-tone.ts`, files G2 also edits for D1 and D2. Its spec states
that no material constant, law or capture moved; the calibration page hand-steps `root.runFrame`
(`packages/calibration/web/scene.ts:866-877`), which the PR keeps exact. **It is merged and
released**: `399c6bbf` carries it as 0.25.0, which the user published on that commit (the c9d
row, `10c52933`). That merge's release chain read the capture tree 1,893 match / 0 mismatch,
the goldens byte-identical to v0.24.0 and the six document digests unmoved. G2's base includes
it; X37 governs. Line numbers in this charter are `9d7e171c`'s unless marked; the merge moved
`renderer.ts`'s cited lines down by 20 and left the others where they were.

## Design (advisory unless marked)

### The law: LT, Apple's layer tree with the opacity scaling the radius (MARKED: the primary declared family; G0 declares every family with its count before any pixel of the new bed, and G2 fits on the new bed)

Let B be the backdrop in encoded sRGB, s the surface's short side in CSS px,
t = clamp((s − 64)/96, 0, 1), with its continuation above 160 declared as the clamp, t = 1
(finding 9(d)), and d the SDF depth in points, negative inside. All averaging is in **ENCODED**
space. The algebra is memo E §1's; "declared" marks memo D's dump, the rest are readings memo E
tested.

- **The capture.** S = F∗B on the footprint R_fp: the shape's bounding box plus the declared
  margin (active 0.35 s if s > 64, else 16 pt; receded one device pixel). The capture is at half
  resolution, 2 device px per texel at both display scales and 4 on rrect-lg (declared), and is
  modelled as memo C's Gaussian floor F of 0.8 device px (1.6 on rrect-lg) applied BEFORE the
  knee. A literal box decimation is a rejected null (Surprises). This is the law's device-pixel
  part; every width above it is in CSS px.
- **The narrow term** C = G(σn)∗S, with the declared opacity scaling the radius:

      σn = k · 5 pt · o(s, d, pose)

  o is the dump's exact law: active 0.8t at the centre (d = −s/2), falling linearly in d to 0.4t
  at 1 pt inside the edge; receded 0.4 + 0.4t, flat in depth. The narrow term is a function of
  opacity AND pose (finding 9(c)): k is per endpoint, so the pose enters through it as well as
  through o.
- **The wide term** W = G(σw)∗S on R_fp, with σw = k · 8 pt and the same k. At R_fp's edge the
  blur is clamp-to-edge when active and normalised when receded, memo E's readings; dark active
  leaves a 0.23-code choice that G0 declares (§2c).
- **The composite**, light: a Lighten of C with W at λ, then Normal toward W at w = 0.5, the
  slider's position (declared):

      N = C + λ·max(0, W − C),    M = 0.5·N + 0.5·W

  Dark is the mirror, N = C − λ·max(0, C − W). Both fills use the one W, so lighten-then-normal
  and normal-then-lighten are the same algebra; the order question is where T sits (R1).
- **λ is fitted, per endpoint.** The dump's 0.9 is a declared hypothesis the bed referees. Memo E
  refutes it on pitch-64 receded cells unless W's support changes it: on the W34 capsule at p64,
  λ 0.9 costs 2.01 codes where λ 0.68 gives 0.90 (§3a, §4).
- **The output** is y = T(M) (X35): candidate 1's landed T or candidate 2's native T.
- **The count is 2 per endpoint: k and λ.** Everything else is declared (the radii, o, w, R_fp,
  the texel) or fixed from memo C (the 0.8-dev floor, native T in identification). Memo E's
  reading of this family is pooled rms 2.38 / 2.11 / 3.47 / 3.03 codes (light active / light
  receded / dark active / dark receded) at k 1.983 / 2.035 / 2.094 / 2.074.
- **Where LT stands on the existing cells.** It does not close where memo C's per-cell fits
  closed: 10 of memo C's 28 closed cells, a median excess of +0.51 to +1.16 codes (Grounding,
  memo E's readings). Its misses fall in three patterns: U1's drift, also in dark active on the
  small shapes at p64; the active rrect-ml and rrect-lg, worst in dark, where k_w grows with span
  and points at the bleed (U7); and memo C's 1x aliasing cells at pitches 4–8, which no Gaussian
  closes (memo E §2e).
- **Uniform invariance by construction.** A constant backdrop maps to itself under every blur,
  every footprint normalisation and the hinge (max(0, 0) = 0), so E3's uniform closure and the
  shipped uniform bodies are untouched by the structure (memo A). Clause 7 tests it.

> **Drafter's note (one k).** The parent's ruling on memo E says one k "(memo E reads 1.98-2.17 in
> all four endpoints) governs both" radii. The charter reads that as one k per endpoint shared by
> both radii, memo E's LT-1k, with the four endpoints' agreement a reading and not a constraint.
> A single k across all four endpoints would be a further nested restriction, three parameters
> fewer, that G2 could test beside it; the parent may want it declared.

### T: two candidates (MARKED; X35, X40; Decision Log 5b)

- **Identification inverts through NATIVE T**, measured on family A per endpoint, so the level
  misses never leak into a structural parameter (the parent's ruling on v1's note 5).
- **Candidate 1, the landed T.** The three non-E3 endpoints use the shipped tone solve's uniform
  response, evaluated at M per pixel rather than at the group argument. The light receded
  endpoint uses E3's F on encoded luma: its seven ordinates on 40–150 unchanged, EXTENDED above
  150 by family A's measured ordinates (one per declared level above 150: 160, 176, 192, 208,
  224, 240, 255), declared in G0 as its own family with that count and appended as its own
  gate-group; g and the chroma vector it scales are evaluated on W,
  y = F(L(M))·1 + g(L(W))·v(W) (memo A: chroma takes the heavy argument only, W41's smoother-g(L)
  hypothesis in its declared form). If L1's light-solid inactive growth still fails with the
  extended F, the light receded tone stays the shipped solve (clause 10). Its structure is scored
  against the law combined with this T, and the gap to Apple's level is the existing named miss.
- **Candidate 2, Apple's grey tone curve from the new capture, in all four endpoints.** Its T is
  the NATIVE curve measured from family A's greys per endpoint, counted by its ordinates as E3's
  F is: one per family-A level and span stratum it is read on, the count fixed in G0. It lands
  instead of candidate 1 only if it passes every check, and may then close W36's grey-middle miss.
- **The face colour matrix is a light-only partial explanation**, not the declared form (the
  parent's ruling on memo E, item 5, superseding the note under Decision Log 5b). As T in place of
  native T it costs +0.35 to +2.26 pooled in light, from its 1–3-code shoulder above input 88 and
  its lack of a span term where native light-active T rises with span, and +10.7 to +15.1 in dark
  (14–18 absolute), because the dark compression above the floor is undeclared (memo E §0, §2f).
  Moving it before or after the knee changes 0.20–0.43 (light) and 0.07–2.52 (dark), and with
  native T the two positions tie (2.07 / 2.07 light receded, 3.07 / 3.01 dark receded). The
  face–knee order is recorded as that tie, not declared as a rival.
- **Where the shipped operators take their argument.** G0 names each shipped leaf the law
  supersedes (the linear pyramid's share `sizeScatter*`, `sizeHeavyTapSigma`, the dark
  `scatterLod` path, `collapseTransmission`'s group/local mix) and each shipped operator that
  reads a blurred backdrop (body chroma retention, the scatter's spatial-scale statistic), and
  declares where it reads once C, W and M exist.
- **Accessibility.** The law stands down under an accessibility occlusion lift, as
  `bodyChromaRetentionUnderPolicy` does: Reduce Transparency returns every W42 gate to its
  identity, `forced-colors` draws no body, and Increase Contrast alone does not stand it down. The
  bed measures neither mode.
- Memo C reads the native T as span-invariant light receded, rising with span light active (+2 to
  +6.5 codes from span 44 to 160) and clamping dark at spans ≥ 96.

### The rival families (MARKED: declared with their counts in G0, before any pixel)

Counts are per endpoint, w fixed at 0.5 throughout. "σn(span)" is a free span law whose ordinate
count G0 fixes.

| family | what differs from LT | parameters | on existing cells | answered by |
| --- | --- | --- | --- | --- |
| **LT-2k** | a separate scale for each radius, k_n and k_w | 3 | a second k buys 0.02–0.13 (memo E §2c): not separated on these cells | C (S 8 against S 32 on rrect-md, both poses) |
| **free Gaussian σn(span)** | σn a free span law per pose instead of k·5·o | 2 + σn(span) | not fitted head to head with LT; memo C's per-cell free fits, which a span law restricts, sit a median +0.51 to +1.16 below LT | B', C (depth sweep) |
| **R1, receded composite order** | T applied to C and W before the fill composite | LT's | 2.07 / 3.07 against LT's 2.07 / 3.01 (light / dark receded); inseparable on light even from a known truth (0.41 against 0.44); refereed only with family A's greys 160–255 (memo E §3b) | B (P5, P3), A |
| **W on the rounded shape** | W's support the rounded-shape footprint, its margin a parameter | 3 | U1's candidate: memo E puts the drift in W's reference at 16–48 pt (§3c) | D, C |
| **W tails** | W a mixture of two Gaussians | 4: a second width and its weight | a Gaussian is best or tied on the W34 capsule in every endpoint; in dark receded a free σw of 14.67 pt closes the p64/p16 gap on that shape (memo E §3c) | C, D |
| **k shared across poses** | one k for both poses of a scheme (the review's shared-σw rival, under LT) | one fewer per scheme | k reads 1.983 / 2.035 light and 2.094 / 2.074 dark (active / receded) | A–D |
| **K2** | two fills: the knee against Wk, the normal mix toward Wn | 3: a second fill width | receded 0.5–1.5 under memo C's Gaussian family, no gain (C §4) | C, B |
| **C-linear** | the narrow term averaged in linear light, W encoded | LT's, a discrete choice | not identified (B §3) | B, D |
| **per-channel knee** | max/min per channel against on encoded luma | LT's, a discrete choice | not identifiable (C U6) | E |
| **LT + bleed** | the dump's active bleed layer added (radius 0.35 s and opacity 0.5t light / 0.8t dark for s > 64, declared) | LT's, or 3 if its radius takes its own scale | dark active k_w 2.23 / 2.54 / 2.80 on rrect-md / ml / lg; memo C's σ-48 weight of 19–36 % on active rrect-ml/lg knee sides | D, B', C (U7) |

**Rejected nulls**, recorded in Surprises and given no bed budget (memo E §4): the mixture
reading C = (1 − o)·S + o·G(5)∗S (finding 9(b)'s framing, superseded); radii in texels or in
device pixels; R2, the fill on the sharp capture with the narrow blur last; a literal box
decimation of the capture. Memo A's reading C7 (λ = 1) and memo B's F1 (one blur) and F2 (linear
two-scale) stay rejected; F4, vitrea's shipped form T(group) + b·(K∗B − group), is rejected the
same way and is the baseline the referees read against.

**The tie-break (MARKED).** Among survivors that are "insufficient resolution" apart: resolution
first (a family that beats another at an admitted discriminator by more than max(3, sum of bars)
wins); within resolution, runtime cost (passes and texture reads on the WebGPU tier); then
parameter count. A per-surface support breaks the per-source pyramid sharing the shipped heavy
blur relies on (`renderer.ts:612-617`, now 632–637; finding 17(i)). LT's box-plus-margin support
is per-surface too, so the cost is priced for LT and for its support rivals alike.

### D1 and D2 are in the law (MARKED; X36)

- **D1, device-px widths.** `renderer.ts:600-605` (`bodySigmaCssFor` = `optics.blurSigma` /
  dpr; 620–626 since PR #2), `renderer.ts:638-644` (`heavySigmaCssFor`; now 659–665),
  `material.ts:4873-4878` (`heavyTapSigmaAtScale` returns device px); the light active document's
  lines 151–152 set `sizeHeavyTapSigma` 14 and `sizeHeavyTapSigma2x` 20, the light receded
  document's line 89 sets 2x 14. The dark active document sets `sizeHeavyTapSigma` 0 at both
  scales (lines 133–134) and the dark receded one names 2x only (line 83), so the dark heavy goes
  through `scatterLod` (`material.ts:1222`, `wgsl/optics.ts:1052`), a chain level in device
  texels; it is among D1's superseded leaves (finding 15). The effect: the heavy width is 13.8 CSS
  at 1x but 6.9 (receded) or 10 (light active) at 2x, where memo C reads Apple at 10–19 at both
  scales and memo E's k puts σw at about 16–17 pt (memo C §7, §2a; memo E §0). The doc comment
  at `renderer.ts:582-586` (now 602–606) cites §5.55–§5.58 ("one kernel in device pixels at both
  scales"). Those were read on the macOS 26.5 probe beds (rrect-md 2x σ 0.5 CSS); macOS 27 differs,
  so this is an OS difference, not a reversal, and it is also the argument for keeping macOS 26.5
  at the identity (finding 16).
- **D2, linear-light blur.** WebGPU decodes before the pyramid (`wgsl/backdrop.ts:86`); the CSS
  tier picks `linearRGB` on the premise that "the reference's body … is linear in luminance"
  (`css-tier.ts:2136-2150`, whose doc comment cites §5.71 §2 for the encoded blur reading worse
  under the shipped two-sided law). Every full-linear fit on Apple loses: 5–25 codes on checkers,
  16–48 on hc-text, 3.6–4.2 on lc16 (memo C §7). This settles the heavy and level argument; the
  narrow term's space is the C-linear rival.
- Changing them moves every macOS 27 document, so they land with the law and pass the same
  referees. Each is a gate-group in the identity table: at its identity the device-px and
  linear-light paths draw exactly what ships today, and the frozen macOS 26.5 pair stays there
  with `b2b570e4adcea8fb` / `874be66ea501621b` (W29 Decision Log 1 (i); rule 2).

### What existing cells cannot identify, and the family that answers each (MARKED)

| question | what is open | family |
| --- | --- | --- |
| U1 | the receded one-sided algebra. Memo E finds the λ drift persists under the declared readings, flat across hinge-gap bins, so it lives in W's reference at 16–48 pt, its support or its tail, and not in the hinge's form or the composite order; it also appears in dark active on the small shapes at p64 (§3) | C (S 32 both polarities on rrect-md, S 16 on capsule), D (δ 0 and 12 on capsule, 0, 12 and 32 on rrect-md), B (P2 and P4 at pitch 64 beside pitch 16), receded, both schemes |
| U2 | the receded narrow span law, declared (0.4 + 0.4t), confirmed in pixels as the radius's scale | B', with C's depth sweep as its flat-in-depth control |
| U3 | the footprint support: box, rounded shape or margin; the edge mode; whether the active W is limited to it or reads the canvas | D (inside and outside steps), both poses |
| U4 | the heavy kernel's tails | C, D |
| U5 | T at 150–242 in every endpoint and dark T by span: native T for identification, the F extension, candidate 2's curve, R1's referee | A |
| U6 | a per-channel against an on-luma knee, and the chroma kernel | E |
| U7 | the active bleed (dark k_w growing with span; memo C's σ-48 weight) | D (active steps on rrect-md and rrect-lg), B' (active rows at spans ≥ 80, rrect-lg beside rrect-ml), C (S 32 on rrect-md) |
| R1 | T before the fill composite, against LT's order | B's P5 144/240 and P3 96/160 at pitch 16 and 64 in both receded endpoints, with A's greys 160–255 |
| one k or two | LT against LT-2k | C's S 8 against S 32 on rrect-md, both poses |
| depth | the active narrow opacity's grading, 0.8t → 0.4t | C's depth sweep on rrect-md and rrect-lg |
| rrect-lg | its narrow reads narrower than the o law predicts (light active k_n 1.16 against 1.73–1.74; unidentified: the bleed or the 0.25 realisation) | B' on rrect-lg beside rrect-ml; C on rrect-lg |
| units | settled by memo E: points. C's rrect-ml / rrect-lg pair re-reads it at no cost | C |

### The bed (MARKED: the families and their questions; exact ids and levels are G0's)

Memo C §6, grown by the review's rulings, memo D's implications and memo E's Q4. Existing JSON
kinds only (solid, two-level checkerboard, impulse as a single patch, split, shape `position`);
every kind is checked against the side bundle's pinned build before it is declared. The canvas
is 320×200, as canonical (memo B §8). Every s ≤ 64 is one declared stratum (t = 0); the span
budget goes to t = 1/6, 1/3, 2/3 and 1 (s = 80, 96, 128, 160) plus a t = 0 shape (memo D §7a).
Backdrop and position switch no declared input, so no family is stratified by backdrop (memo D
§7f). Four passes per scale (scheme × pose); a pass's cell list may differ by scheme and pose.

**2x, per pass:**

| family | cells | answers |
| --- | --- | --- |
| A — uniform greys 0, 64, 128, 160, 176, 192, 208, 224, 240, 255 × {capsule, rrect-md}; 96, 160, 208, 255 × rrect-lg; bright 160, 208, 255 × {rrect-64, rrect-ml}; in the dark passes also 160, 208, 255 × rrect-80 (memo D's MaxLuma transition; the parent's call) | 30 light, 33 dark | U5: native T per endpoint and span, the F extension, candidate 2's curve, R1's referee; dark MaxLuma on both sides of its knots |
| B — two-level checkers P2 48/208, P3 96/160, P4 16/112, P5 144/240 at pitch 16 and 64 on rrect-md | 8 | U1 (P2 and P4 at pitch 64 beside 16, receded); R1 (P5 and P3 in both receded endpoints); the space on non-binary structure; λ refereed |
| B' — P1 0/255 at pitch 8, 32, 64 on capsule and rrect-ml; pitch 32 on rrect-64 and rrect-80; pitch 8 and 32 on rrect-lg beside rrect-ml (finding 9(a); memo E Q4) | 10 active, 7 receded (pitch 8 dropped when receded) | U2; the span law from the new bed alone, with the knot at 64 and the saturation at 160 each carried; U7; the rrect-lg narrow |
| C — single square S 8, 32 × 2 polarities on rrect-md and S 16 × 2 on capsule, each with a surround annulus; S 8 at s/4 and 4 pt from the edge on rrect-md, and at the centre, s/4 and 4 pt from the edge on rrect-lg; the canonical impulse on rrect-ml and rrect-lg | 13 | U1 (S 32 and S 16, receded); U4; one k or two (S 8 against S 32); the depth grading (a free falsification control when receded, where it must read one width); the units re-read; the halo stop's annulus |
| D — step under the interior (split) at shape offsets δ 0 and 32 × 2 polarities on rrect-md and δ 0 on capsule; when receded, also δ 12 × 2 polarities on rrect-md and δ 12 on capsule (memo E Q4); steps 8 and 16 CSS px OUTSIDE the rrect-md edge × 2 polarities; active only, a step at δ 0 under rrect-lg × 2 polarities | 11 active, 12 receded | U1 (receded); U3; U7 (the rrect-lg rows are the review's bleed rows) |
| E — isoluminant chroma checkers, 2 hue pairs, pitch 16 and 64, rrect-md; G0 names the matched luma | 4 | U6 |
| F — bridges: canonical checker-16 rrect-md, impulse rrect-md, photo rrect-md; probe checker-64 rrect-lg | 4 | the bar across sittings only (not under clause 6) |
| H — the structured holdout, declared before fitting | 8 | referee |

Per 2x pass: **88 light active, 91 dark active, 86 light receded, 89 dark receded**. Against v2's
86 / 82: B' +2 active and +1 receded (rrect-lg); A +3 in both dark passes (rrect-80); D +3 in
both receded passes (δ 12 restored). Memo E's other Q4 rows were already in v2's bed: C's S 32 and
S 16 in both poses and schemes, S 8 beside S 32, C's depth sweep on rrect-md and rrect-lg, and
B's P2, P4, P5 and P3 at both pitches in every pass.

- **H** (memo C, with the parent's call on v2): P1 at pitch 24 on an UNSEEN span, s = 112
  (t = 0.5), if G0 shows the side bundle accepts that component from the wave-local scenes file
  with no rebuild, as memo D's scratch scenes were; otherwise P1 at pitch 24 on rrect-80, and the
  charter then records that H's span is seen in calibration. Beside it: P6 32/176 at pitch 32 on
  rrect-md; a step at δ 20; a patch S 24; P3 at pitch 64 on rrect-lg; 128/229 at pitch 64 on
  capsule; greys 184 and 232 on rrect-md. Six of the eight are structured.

**1x, per pass: 15 cells, derived from memo D's criteria and memo E's Q4.** No declared input
differs with scale beyond four one-device-pixel terms (memo D §4), so a 1x cell earns its place
only where sampling density or device-pixel geometry can matter: pitches of 8 pt or less, patches
of 4 pt or less, rrect-lg (one backdrop pixel per 4 pt at 1x), and edge strips; the body-level
families keep only a small referee (memo D §7g).

| criterion | 1x cells | count |
| --- | --- | --- |
| fine pitch ≤ 8 pt | P1 at pitch 4 and 8 on capsule; P1 at pitch 4 on capsule at an odd CSS-px offset (the review's odd-offset cell: half a backdrop texel of phase); P1 at pitch 4 on rrect-md, a depth-graded shape at the standard scale, where memo E reads LT's worst cells (5.57 light, 9.14 dark active) | 4 |
| rrect-lg | P1 at pitch 4, 8 and 16 on rrect-lg | 3 |
| small patch ≤ 4 pt | the canonical impulse on rrect-lg | 1 |
| edge strip | the D step 8 CSS px outside the rrect-md edge, one polarity (the receded margin is one device pixel) | 1 |
| small body referee | greys 128 and 255 on rrect-md | 2 |
| bridges (bar tie) | impulse rrect-md; probe checker-64 rrect-lg | 2 |
| H at 1x | P3 at pitch 64 on rrect-lg; grey 232 on rrect-md | 2 |

Memo C's 22 drop to 15: its six body-level greys, capsule pitch 16, the photo and checker-16
bridges and two H cells go; the odd-offset cell, rrect-md pitch 4, the rrect-lg impulse and the
edge strip come in.

**The sitting at seven runs**, on W39's model as memo C used it (9.53 s per capture, including
each no-glass reference; 16.3 s per sentinel; 13 s per run; 25 s per pass):
- glass captures: 2x (88 + 91 + 86 + 89) × 7 = 354 × 7 = 2,478; 1x 4 × 15 × 7 = 420; total
  2,898;
- no-glass references, one per distinct backdrop per pass in run 1: 2x 2 × 44 + 2 × 43 = 174
  (v2.1's added cells reuse declared levels, pitches and splits), 1x 4 × 10 = 40; total 214;
- (2,898 + 214) × 9.53 s = 29,657.4 s; 48 sentinels × 16.3 s = 782.4 s; 8 passes × 7 runs ×
  13 s = 728 s; 8 passes × 25 s = 200 s;
- **total 31,367.8 s ≈ 8.7 h of capture** (v2: 8.3 h; memo C: 7.6 h). If memo C's
  capture-to-wall ratio holds (7.6 → about 8 h), that is about 9.2 h at the Mac;
- plus `dump-layers` over the declared bed first, at memo D's rate (about 200 s per 24 scenes):
  354 + 60 = 414 scene-dumps ≈ 3,450 s ≈ 1.0 h, no grant needed.

The total, about 10.1 h, is over Decision Log 2's "about 8 h"; the parent tells the user the net
length at the "tell me first" moment (Decision Log 6), with seven runs standing.

### Memo D's answers to v1's pending points (folded at v2; point 2 settled by memo E at v2.1)

1. **The receded narrow width is graded by span, not flat.** Its opacity is 0.4 + 0.4t (0.400
   for s ≤ 64, 0.467 at 80, 0.533 at 96, 0.667 at 128, 0.800 at 160) and flat in depth, and memo
   E reads that opacity as the radius's scale. The receded narrow term carries the declared span
   law; B' keeps its capsule and rrect-ml rows beside the rrect-64, rrect-80 and rrect-lg rows,
   and C's depth sweep is its falsification control.
2. **Points, not backdrop pixels.** Memo D read the radii equal at both scales and the pixel
   widths close to scale-invariant, which pointed to points; memo E settles it: k reads
   1.98–2.17 in points in all four endpoints, the radii in texels or device pixels cost 5.36–9.77
   pooled against 2.11–3.47, and no rrect-lg ratio comes near the 2 texels would give (memo E §2c,
   §2g). C's rrect-ml / rrect-lg pair re-reads it at no cost.
3. **1x and 2x agree on every body parameter.** The four scale-dependent quantities each equal
   one device pixel (the highlight's height and offset, the receded margin, the receded SDF
   output maximum). The reduced 1x pass stands, now 15 cells. Where native 1x and 2x pixels differ
   (memo B: light-active rrect-md σ 1.31 against 2.36), the cause is the realisation, sampling
   density or the device-pixel terms, not a declared input.

### Memo E's answers to v2's pending points (folded at v2.1)

1. **LT at the dump's literal constants does not reproduce memo C's cells within memo C's
   residuals.** With λ 0.9 and one scale per endpoint it reaches ≤ 1.00 code on 10 of memo C's 28
   closed cells, a median excess of +0.51 (light active) and +1.16 (dark active); λ is now fitted
   and w stays fixed (the law).
2. **LT does not close U1.** The drift persists under the declared readings; memo E points it at
   W's reach 16–48 pt out or its support. U1 stays open, assigned to the bed's C, D and B rows.
3. **The mapping is radius scaling in points**, σ = k·r, one k per endpoint for both radii (a
   second k buys 0.02–0.13), so LT counts k and λ, 2 per endpoint. The review's radius per pose is
   carried by k per endpoint and by the LT-2k rival.
4. **The literal face matrix is a light-only partial explanation** (+0.35 to +2.26 light, +10.7 to
   +15.1 dark over native T); candidate 2's T is the native curve from family A, counted by its
   ordinates.
5. **The receded composite-order rival is R1** (T before the fill composite); R2 is rejected.
6. **The bleed is the active ml/lg misfit's likely cause but unidentified**: dark active k_w grows
   with span and the light-active rrect-lg narrow reads narrower than the o law predicts. LT +
   bleed stays the declared rival, read by the U7 rows.
7. **The free Gaussian σn(span) rival was not fitted against LT head to head.** Memo C's per-cell
   free fits, which a span law restricts, beat LT by the medians above, so it stays a live rival
   the bed separates (B' across spans, C's depth sweep).
8. **Canvas against the declared support in the active pose was not re-tested.** Memo E fitted LT
   on the declared box-plus-margin support only (active 2.25 / 3.45 pooled, light / dark); the
   comparison stays U3's, for D's steps in both poses.

### The split and the holdouts (MARKED)

- **H** is the new bed's structured holdout, declared and hashed in G0 before capture, enforced
  by the wave reader and launcher, its payload behind the procedural boundary until G2's one
  receipt. G0 also declares a validation set of transfer axes (a span or pitch per family that
  calibration does not contain), so that validation tests the span law, the depth grading and the
  pitch-flatness rather than repeat noise. Whether an H cell is web-plannable (an offset step may
  not be) is in the W42 web plan; a cell that is not referees the numerical structure only (W41
  clause 2).
- **The canonical holdout** stays sealed until G3 and is read there once, by artifact.
- **The canonical probe cells were READ in grounding** (memo C), as were the W34 archive's
  checkers: calibration evidence, never a referee, and admissible as corroboration (X34).

### Repeats, the bar and the archive of record

Seven runs (Decision Log 2, RULED). The bar is W39's (clause 5). The archive is W39's pattern:
complete and role-separated, lossless crops in original coordinates with every dependency an
estimator reads, the per-run statistics with populations and input hashes, the state
membership, a SHA-256-pinned inventory, replay proved identical with the raw root denied; a
`.tar.zst` under 2 GiB published as a GitHub release asset named by its SHA-256, a reader that
fetches by that name into a cache outside the repository and verifies the digest before use,
and a second owner-controlled copy. **The sitting's operational logs and its dumps go into the
archive, not into git** (the tracker's W41 G1 entry: about 84 MB packed of logs went into git). A
thin projection is a convenience, never the record.

### The instrument (G0)

- The readers, proved first (clause 2): the LT forward model (memo E's `lt.py` as its reference:
  the radius scaled by o, one k, the 0.8-dev floor before the knee, R_fp with the declared margin,
  the clamp-to-edge and normalised edge modes), its rivals' forward models, memo C's model reader,
  the mirror statistic S, the pitch-64 heavy reader, the ESF and impulse readers (memo B), the
  step reader for D, the patch and annulus reader for C, the depth-graded radius reader, and memo
  E's per-cell λ and hinge-gap readers for U1.
- The pre-sitting rehearsal of every referee (clause 3).
- The referees' **candidate-admission mode**: W41 G2's ported referees refuse a declared document
  that is not the file on disk; the mode admits a declared scratch document matched by hash and
  stamps every output "candidate", with a red/green test.
- The M2 named-miss derivation beside `chromaStructureMisses()`, pinned by an owner case
  (Decision Log 5a).
- The two directional stops' statistics, regions and resolutions (clause 10).
- The W42 web plan (which new-bed cells vitrea can pose); the wave reader and launcher enforcing
  the split; the sitting script derived from W39's with its roots pointed at the W42 bed and the
  side bundle, `dump-layers` first.
- The one-exposure runner, reusing W41's X26 machinery
  (`results/2026-09-27-w41-g0-declaration/exposure/runner.py`), binding both candidates,
  numerical and rendered, on one receipt.
- The standing eye-sheet script extended to the six strata.

### The CSS carry (advisory; Decision Log 4)

The primary route on Chromium is ONE reference filter inside `backdrop-filter`: two
`feGaussianBlur` from `SourceGraphic` at `color-interpolation-filters="sRGB"` (the narrow blur at
radius k·5·o and the wide fill at k·8), `feBlend` lighten (dark: darken) and `feComposite`
arithmetic for the λ and w weights. `backdrop-filter` reads only the element's box, the box
footprint for free (Chromium's edge mode is unmeasured). One `feGaussianBlur` has one width, so
the active narrow radius's grading in depth has no exact single-filter form; Decision Log 4
measures what the filter carries of it. The stacked route, encoded `blur()` layers with
`mix-blend-mode` lighten/darken at opacity, is the approximation for engines that render no
reference filter. E3's F and g, or candidate 2's curve, take W41's affine route
(`w41-g2-css-candidate` `78c4b854`), re-derived against the law as W41 Deferred at close 5 lists.
Decision Log 4 still needs the Chromium proof.

### The runtime base (MARKED; X37)

PR #2 is merged at `399c6bbf` and released there as 0.25.0 (`10c52933`). G2 branches from main
as it stands when G2 starts, so its base includes PR #2. Before any candidate render, G2
re-renders a declared sample of the canonical bed with the SHIPPED documents at that base and
shows it byte-identical to the canonical capture tree, so every rendered difference is
attributable to the candidate and not to the base. G3 proves the seal's
identity at G2's frozen base; if the base has moved since, clause 8's proof runs again first
(finding 17(ii)).

## Children

### G0: Declaration and instrument (ledger §5.194)

Branch `w42-g0-declaration`; evidence `packages/calibration/results/<date>-w42-g0-declaration/`.
- The families, both candidates, the F extension and the tie-break of Design, with memo E
  folded, hashed before any native pixel of the new bed exists.
- The instrument of Design, proved (clause 2).
- The rehearsal of every referee in all four endpoints (clause 3); a referee failing by
  construction goes to the user before G0 merges.
- The capture bed as a wave-local scenes file with its own fixture root, the canonical
  `scenes.json` untouched; every kind checked against the side bundle's pinned build
  (`backgrounds` / `self-check`, no capture), including whether it accepts H's s = 112 component
  with no rebuild.
- The M2 named-miss derivation and its owner case (Decision Log 5a); the candidate-admission
  mode; the W42 web plan; the runtime-base sample and the eye sheets' stratum membership.
- No native capture. Independent review before merge; the freeze reads 1,818.

### G1: The native sitting (ledger §5.195)

Branch `w42-g1-sitting`. Starts only after G0 has merged and the parent has told the user the
tooling is ready and the sitting's net length (Decision Log 6, RULED).
- **The side bundle** is the existing W39 one, `dev.vitrea.reference-apple.w39` at
  `~/vitrea-w39/side/` (binary 02052b17…, cdhash be258cbf…), used with no rebuild. Memo D ran
  `dump-layers` on it and found its build inputs byte-identical to HEAD's `apps/reference-apple/
  Sources`. It was retired at W39's close with no TCC row (W39 Decision Log 4).
- **First, `dump-layers` over the declared bed**, while the Mac is idle and before any grant
  switch; every dump must read memo D's declared configuration (clause 4).
- **The grant, by the user's hand.** One Screen Recording grant holds at a time on this machine
  (W34 Decision Log 4; W39 Decision Log 4). The user adds the side bundle under Screen & System
  Audio Recording and lifts X5 for the W42 bed; the parent reads the grant back from the system
  TCC database and runs the side's positive pose checks. The original bundle is not launched
  while it has no row. After the sitting the user re-adds the original bundle alone and restores
  X5; the original's positive check must capture a canonical cell byte-identical to its committed
  fixture, as at W39's close. Failure to restore is an open blocker, not a closed sitting.
- **The passes:** 1x and 2x × light and dark × active and inactive, seven runs each, sentinels
  after, every capture attested (clause 4), quarantines named.
- **About 8.7 h of capture at seven runs (about 9.2 h at the Mac), plus about 1.0 h of dumps**,
  in one sitting while the user leaves the Mac idle.
- **The archive** produced, pinned and published as a release asset by SHA-256 with the ledger
  citation; the bar published from the archive before plurality; replay proved with the raw root
  denied; the operational logs and dumps inside the archive, not in git. Nothing is read against
  vitrea.

### G2: Identification, the gate and the one exposure (ledger §5.196)

Branch `w42-g2-identification`, cut from main as it stands when G2 starts (X37). In order:
1. The runtime-base proof (clause 8).
2. Native T per endpoint from family A; the fit of the structure on the new bed's calibration
   set, family by family, LT first; transfer to validation; survival per clause 6; the tie-break.
3. Both candidates implemented behind zero identity gates on both tiers' code paths, D1, D2 and
   the F extension included (X36); goldens byte-identical at identity.
4. The rendered candidates on the new bed's web-plannable calibration/validation cells (clause 9)
   and uniform invariance (clause 7).
5. The canonical calibration/validation bed rendered with each candidate in a scratch stage; the
   referees in candidate-admission mode, the two directional stops, the owner test over the six
   gated profiles, and the eye sheets by stratum (clause 10).
6. **Only if all of those pass:** the freeze of the numerical and blind rendered H predictions by
   artifact, then the ONE exposure on H (clause 11). This is the lesson of W41, which spent a
   holdout on a law that later failed landing.
7. Decision Log 3 if an endpoint fails.

### G3: Seal and land (ledger §5.197)

Branch `w42-g3-landing`. Conditional on clause 11 passing (Decision Log 1).
- If the landing is receded-only, the tracker's M2-reference-by-active-hash fix lands first, as
  its own fix wave (Decision Log 3).
- Seal the documents; prove identity against G2's frozen renders at G2's frozen base.
- The canonical stage read, both tiers. The CSS carry is the one reference filter on Chromium and
  the stacked approximation elsewhere, with a Chromium proof (Decision Log 4);
  `tier-coherence.test.ts` pins whatever is carried or declined.
- The canonical holdout once, by artifact (clause 14). Decision Log 5.
- Publish once through W40's publisher; copy the capture tree and move the superseded one;
  `check-capture-tree` exit 0; eye sheets over the whole canonical bed.
- The changeset and the release checklist; `pnpm release` is the user's; tag after.

## Cross-Child Contracts

Carried from W41 where they still apply:
- **The holdout is read once, by artifact.** W41's X26 carries for H: one receipt binding every
  W42 candidate, numerical and rendered; the rendered H predictions blind and frozen before it;
  a failed exposure spends it; nothing changes after it. The canonical holdout is read once in G3.
- **X31's three closure statuses** (`measured`, `censored-bound-satisfied`, `UNMEASURED`) and
  **W39's X21** (a native channel ≥ 250 or ≤ 5 is a one-sided bound; a censored held-out cell is
  UNMEASURED); **X23** (prediction before opening); **X24** (the archive complete wherever it
  lives, cited by SHA-256 and bytes); **X25** (one canvas, attested positions).
- **Operational logs live in archives by hash**; no committed file exceeds 50 MB.
- **Every worker runs on `opus`** (X9 as updated 2026-09-28); reviews go through the review-code
  agents, with an `opus` fallback when they are rate-limited. Pass the rule to workers that
  dispatch workers.
- **A pinned browser and CLI** (§5.192 §16): the cached Playwright CLI 0.1.19 with the installed
  full Chromium 1243, tool and browser hashes recorded, no browser installation or download
  inside the wave, a fresh X6 check before each launch.
- **The four X6 facts** before every browser run and on every native capture (clause 4), with
  every browser run in `browser-runs.txt`; never a browser capture while a native pass runs.
- **W34's X1–X14** with W39's substitutions updated: X3's side bundle is `.w39`, reused and not
  rebuilt; X5 authorises native capture for the W42 bed only (its wave-local scenes file, its
  fixture root, the side bundle; no canonical key, no 26.5 key, no accessibility pass); X8's
  split is W42's; X10: the W42 bed is not a gated set; X12: raw runs stay on the machine; X14:
  the machine's GUI is touched by `amigo` first and the user second, except the grant switch,
  which is the user's hand (Decision Log 6).
- Committed evidence is never rewritten, corrections sit beside it; merges `--no-ff -F <file>`
  with the freeze verified; no attribution trailers and no session URLs.

New:
- **X33 — the landing referees before the exposure.** Clause 10: the adopted referees in
  candidate-admission mode, the two directional stops, the owner test over the six gated
  profiles and the eye sheets by stratum pass before H is predicted, frozen or opened.
- **X34 — the probe cells are calibration evidence.** The canonical probe cells memo C read (the
  checker pitch series, lc16, hc-text, hc-text-7 and hc-text-28, in every endpoint and scale)
  and the W34 archive's checkers were READ in grounding. They are never a referee of a W42 law.
  They are admissible calibration evidence that may corroborate a fit, never its only support:
  the new bed carries every parameter on its own. The adopted rows that already include probe
  rows (X1, E2) keep their populations as regression stops.
- **X35 — two roles for T.** Identification inverts through the native T measured on family A;
  candidate 1 composes the structure with the landed T (the shipped solve, or E3's F extended by
  family A for light receded), and its gap to Apple's level is a named miss, never absorbed into
  a structural parameter; candidate 2 takes the native curve measured from family A's greys,
  counted by its ordinates (Decision Log 5b; the parent's ruling on memo E, item 5).
- **X36 — D1, D2 and the F extension land inside the law.** Each is a gate-group appended to the
  identity table; at the identity it draws exactly what ships today; the frozen macOS 26.5 pair
  never leaves it.
- **X37 — the runtime base is proved before any candidate render** (clause 8) and again whenever
  it moves before the seal. The base includes PR #2, merged at `399c6bbf` and released there as
  0.25.0.
- **X38 — dump numbers are pointers.** A layer-tree number becomes evidence only where the
  pixels agree; the pixels govern. LT declares the dump's constants as hypotheses the bed
  referees; memo E has already refuted λ 0.9 on pitch-64 receded cells, so λ is fitted, and w,
  whose declared value is the slider's attested position, stays fixed.
- **X39 — every referee is rehearsed before the sitting** (clause 3); a referee that fails by
  construction reaches the user before a native pixel is spent.
- **X40 — two candidates, one receipt.** Candidate 2 lands instead of candidate 1 only if it
  passes every check candidate 1 faces; both are bound by the same exposure receipt.

## Ordering & Dependency Map

Decision Logs 1, 2, 5a, 5b and 6 RULED (2026-09-29) → v2.1 (memo E folded; no point pending) →
G0 (declaration hashed; instrument proved; referee rehearsal, with any by-construction failure to
the user; bed, split, web plan and gate tooling; H's s = 112 component checked; review; merge) →
the parent tells the user, with the sitting's net length (Decision Log 6) → G1 (dumps; the user's
grant switch and X5 lift; passes; archive; bar; the user restores both) → G2 (base proof at a
base that includes PR #2 → native T → calibration fit → validation transfer → gated operators on
both tiers → rendered candidates → canonical renders → **the gate** → freeze → ONE exposure on H;
Decision Log 3 if needed) → G3 (the M2 fix wave if receded-only → seal → identity → Decision Log 4
→ stage read, both tiers → canonical holdout once → Decision Log 5 → publish → capture tree → eye
sheets → changeset → release checklist → the user's `pnpm release`) → close.

## Risks & Mitigations

- **No family meets one code per cell.** On the existing single captures LT's per-cell medians are
  1.64 / 1.79 / 2.33 / 2.43 codes (light active / light receded / dark active / dark receded),
  and even memo C's per-cell free fits closed only 28 cells (memo E §2c, §2e). That is the main
  risk to Decision Log 1's landing. Mitigation: the bed measures the repeat bar the canonical
  cells lack, carries U1's rows and every rival, and λ is fitted; if no family survives, the
  negative is recorded at its resolution and nothing lands.
- **The receded algebra does not close (U1).** Memo E finds the drift persists under the declared
  constants. Mitigation: its candidate causes (W's reach 16–48 pt out, its support, its tails)
  are declared rivals with bed rows; Decision Log 3; the receded documents stay at identity and
  E3 stays unshipped if they fail.
- **A referee fails by construction.** Mitigation: clause 3's rehearsal before the sitting, with
  the user ruling on the numbers; Decision Log 5a already rules M2's reading.
- **A wrong mixing space manufactures a knee.** Memo C's encoded fit on vitrea's linear captures
  returned λ 1.4–1.5. Mitigation: the knee is established by S and by every linear fit's loss
  (clause 2), and the synthetic controls run in both spaces.
- **The sitting is longer than Decision Log 2's estimate**: about 8.7 h of capture (9.2 h at the
  Mac) plus about 1.0 h of dumps, against about 8 h. Mitigation: stated to the user at the "tell
  me first" moment; the review's offset of B' pitch 8 when receded is kept.
- **The heavy chain costs frames.** A per-surface encoded blur at σ about 16–17 pt beside PR #2's
  demand-driven loop, without the per-source pyramid sharing the shipped heavy blur has.
  Mitigation: the tie-break prices cost; G3 reads the renderer bench beside the goldens and
  records it; a regression is a finding for the parent.
- **The machine is shared.** Foreign browsers and another session's Playwright refused W41's
  reads (§5.192 §1, §5.193 §3). Mitigation: X6 before every launch; the sitting runs only when
  the user leaves the Mac idle (Decision Log 6).
- **Some H cells cannot be posed on the web, or s = 112 cannot be declared.** Mitigation: the W42
  web plan says which cells referee the numerical structure only; H falls back to rrect-80 and
  says its span is seen.
- **The canonical holdout fails after H passed**, as W41's canonical referees failed after the
  W39 holdout passed. Mitigation: clause 10 puts every referee readable without a holdout first;
  the canonical holdout's miss goes to Decision Log 5.
- **The backdrop scale step's cause is unknown.** It sits between rrect-ml and rrect-lg, and the
  dumps cannot say whether span or area sets it (memo D §3). Mitigation: LT carries the scale per
  surface as declared; a runtime surface between the two is a named gap until a bed reads one.

## Deferred / Out of Scope

- **The level misses under candidate 1.** W36's grey middle and chroma stay named whenever the
  landed T is the shipped solve; candidate 2 is the route that could close them. F above 150 is
  extended only through family A's measured ordinates (X35), and falls back to the shipped solve
  if L1's light-solid growth still fails (Decision Log 3).
- **The face colour matrix as T**: a light-only partial explanation (memo E §2f), not pursued.
- **The edge.** Rims and edge bands, the lens band, the bright inner line (W35), the top/bottom
  obstruction (W37), the stroke and Apple's dark exterior contour (W41 Deferred at close 3–4),
  and distance-to-edge grading (memo B §8). Memo D's pointers for that line: the key/fill
  highlight band is one device pixel high and one inward at both scales; the ring shadow is
  active only and cannot be W39's receded contour; the receded SDF output reaches 1 pt + 1 dev
  beyond the path, where W39 saw the contour, but the light face's lift there would lighten it
  rather than darken it, which is open (memo D §7h).
- **`gradientOvalization`** (0.5 when active and s > 64), which memo E's o(d) leaves unmodelled.
- **Other slider positions.** Normal and the light fill track `NSGlassTintAmount`; dumps and
  captures at slider 0 and 1 would isolate the normal-weighted wide term, but they are a user
  setting and a new bed key (memo D §7d). The user's call, not this wave's.
- **Tint, the clear material, glass-over-glass, accessibility, the recede transition in time,
  spans above 160** (declared as the clamp, t = 1, and untested), **non-sRGB content, a Light
  system appearance** (memo B §8; memo C §6; memo D §8).
- **Light active grey-128's +3 codes at s = 96**, which no declared face input explains (memo D
  §6): named, possibly bleed or refraction.
- **The private filter's semantics** beyond its effective transfer.
- **The narrow term's averaging space**, if families B and D cannot separate C-linear from
  encoded at the bed's resolution: recorded as unidentified, with the capture that would.

## Tracking Map

| child | status |
| --- | --- |
| G0 | — |
| G1 | — (after G0's merge and the parent's word to the user) |
| G2 | — |
| G3 | conditional on clause 11 (Decision Log 1) |

## Decision Log

### Decision Log 1 — land in this wave (before G0; the user's)

The parent recommended yes, on W41 Decision Log 1's terms: a survivor at one code on
calibration, validation and H, past every landing referee, is exactly the shipping criterion.

**RULED 2026-09-29 by the user: "Land in this wave, if every referee passes".** G3 is in scope,
conditional on clause 10's gate, clause 11's exposure and clauses 13–14's referees all passing.

### Decision Log 2 — the repeat count (before G0's merge; the user's)

Put to the user: seven runs as W39 ruled, about 8 h; or three, about 3.7 h (memo C §6). The parent
recommended seven: the bar must be measured, and three runs cannot show a 0.5-code floor.

**RULED 2026-09-29 by the user: "7 repeats (about 8 h)".** G1 runs seven. The bed has since grown
by the review's rulings, memo D and memo E's Q4: about 8.3 h of capture plus about 0.9 h of dumps
at v2, and about 8.7 h of capture (9.2 h at the Mac) plus about 1.0 h of dumps at v2.1. The
parent tells the user the net length at Decision Log 6's "tell me first" moment.

### Decision Log 3 — partial-endpoint adoption (at charter, by rule; the parent's)

**Ruled at charter.** If the receded endpoints do not survive calibration and validation, the
active endpoints may land alone. That is a partial-endpoint adoption with a claim scope, as W41's
Decision Log 7 allowed: the unclaimed documents hold every W42 gate at its identity, so no
unclaimed document's rendering or digest moves, and E3 stays unshipped if light receded is
unclaimed; the runner scores the complete membership; closure is tested on the claimed strata's
H cells; unclaimed strata are reported "not claimed (identity)" with their scores; at identity
the render reads byte-identical to the baseline, and that equality is a test.

**Extended by the parent (ruling on v1's note 10):** the mirror, the receded endpoints landing
alone, is allowed. A receded-only reseal requires the tracker's "M2's chroma reference is loaded
by its active hash alone" fix to land first, as its own fix wave before the seal. **And (ruling on
v1's note 2):** if L1's light-solid inactive growth still fails with the extended F, the light
receded tone stays the shipped solve and the spatial law lands over it, a partial adoption inside
this Decision Log.

### Decision Log 4 — the CSS tier's carry, approximation or decline, per leaf (in G3; the parent's, on the Chromium measurement)

Open. The primary route on Chromium is one reference filter; the stacked route is the
approximation elsewhere (Design; the review's ruling 14).

### Decision Log 5 — bounds and floors

#### 5a — M2 at the pre-exposure gate (before G0; the user's)

Put to the user before G0 hashes the declaration: M2 is a non-directional regression stop (a 2 %
structure change against the reference generation). §5.193 §3: E3's eight light-inactive photo
failures all moved TOWARD native (1x rrect-md native 0.064, base 0.044, E3 0.062), and memo A
reads every W42 candidate failing the same way; a wave whose purpose is to move structure toward
native cannot pass a stop that measures change. The parent recommended a directional reading,
the reference re-baselining at the adopting gate as W32 Decision Log 4 ruled.

**RULED 2026-09-29 by the user: "Directional: the 2% stays. A cell that moves toward Apple's own
texture reading, and not past it, is recorded as a named miss with Apple's value beside it. That
is M2's existing recorded-miss path. A cell that moves away from Apple, or past it by more than
2%, fails."** Implemented in G0 as a named-miss derivation beside `chromaStructureMisses()`,
pinned by an owner case, the 2 % tolerance unmoved.

#### 5b — the rendered bar and the native-T candidate (before G0; the user's)

Put to the user on the review's B1: the rendered candidate cannot meet one code against Apple
while it composes with a T that misses Apple's level (§5.178 §2 reads the shipped solve's knot-3
miss at +0.0508 / +0.0201 / −0.0207 / −0.0029 linear). The parent recommended both: referee the
structure against the numerical law composed with the landed T, and declare a second candidate
with native T.

**RULED 2026-09-29 by the user: "Both. Score the blur structure against the law combined with
the shipped tone curve, and record the gap to Apple's level as the existing named miss. Also
declare a second candidate that takes Apple's grey tone curve from the new capture in all four
window states. It lands instead only if it passes every check, which could close W36's
grey-middle miss too."** The parent's note: memo D's face matrix (encoded black, white,
saturation and fill, and dark MaxLuma by span) is the declared starting form of that second
candidate's T, refereed by family A's greys; its fitted deviations from the literal matrix are
counted as parameters.

*Superseded beside, 2026-09-29 (the parent's ruling on memo E, item 5):* the parent's note above
no longer holds. Candidate 2's T is the NATIVE curve measured from family A's greys per endpoint,
counted by its ordinates as E3's F is. The literal face matrix misses on level (+0.35 to +2.26
light, +10.7 to +15.1 dark over native T; the dark compression above the floor is undeclared), so
it is recorded as a light-only partial explanation. The user's ruling is unchanged, and the
native curve is its words' plainest reading: "Apple's grey tone curve from the new capture".

#### 5 (remainder) — bounds and floors if the law lands (in G3; the user's)

Open.

### Decision Log 6 — the grant switch and the sitting's timing (the user's hand)

**RULED 2026-09-29 by the user: "When the tooling is ready, tell me first; I'll switch the
permission and leave the Mac idle".** G1 starts only after G0 has merged and the parent has told
the user, with the sitting's net length. The user switches the Screen Recording grant and lifts
X5 by their own hand, and restores both after the sitting.

## Surprises & Discoveries

- **E3's failure is one instance of a gap across the whole material** (memo A, question 2): in
  every endpoint the shipped body draws the half-wave Apple removes, and its two-sided heavy part
  is too weak in the dark scheme and at light 2x.
- **Apple's declared tree has the structure the pixels read, but not every declared constant
  reads literally.** One capture per surface, one filter, no other blur (224 surfaces, memo E
  §1); 17 closed-form laws in one size variable reproduce all 104 surfaces (memo D). The declared
  opacity scales the narrow blur's radius; the declared Lighten/Darken 0.9 is refuted on
  pitch-64 receded cells (memo E §3a).
- **Rejected nulls, with memo E's numbers** (none gets bed budget, §4):
  - *The mixture* C = (1 − o)·S + o·G(5)∗S, the review's ruling 9 framing: pooled rms 3.61 /
    4.95 / 5.31 / 6.81 against the radius scale's 2.25 / 2.07 / 3.45 / 3.01 (light active / light
    receded / dark active / dark receded); out of sample it draws a crisp impulse core native
    lacks, 25–26 codes on the light receded rrect-md impulse where native reads 3–5 and the radius
    scale 3.8–3.9 (§2c, §2h).
  - *Radii in texels or device pixels:* pooled 6.28 / 6.63 / 7.89 / 9.77 (texel) and 5.47 / 5.36
    / 7.19 / 8.02 (device px) against 2.38 / 2.11 / 3.47 / 3.03 in points; no rrect-lg ratio near
    the 2 texels would give (§2c, §2g).
  - *A literal box decimation of the capture:* 7.32 against 1.46 on the 1x pitch-4 capsule; pooled
    3.49 / 2.12 / 4.99 / 3.06 (§0, §2c).
  - *R2, the fill on the sharp capture with the narrow blur last:* 7.01 / 9.65 against 2.07 / 3.01
    on light / dark receded (§3b).
- **U1 survives the declared constants** (memo E §3): on the W34 capsule, light receded, λ reads
  0.68 at pitch 64 against 0.92–0.94 at pitch 16, with non-overlapping intervals at both scales,
  and is flat across hinge-gap bins; the drift lives in W's reference 16–48 pt out.
- **W29's "Normal 0.546" was the slider**, not a material constant (memo D §0), and nothing in the
  declared tree adapts to the backdrop.
- **The receded narrow opacity is span-graded** (0.4 + 0.4t), which W29's single receded dump
  had hidden (memo D §5).
- **Apple's widths hold in points on macOS 27; vitrea's are device px** (memo C §7; memo E §2g).
  §5.55–§5.58 read one kernel in device pixels on the macOS 26.5 probe beds: an OS difference, not
  a reversal.
- **A half-resolution backdrop shows in the pixels**: the 0.8-dev narrow floor at both scales
  and one-sided blobs at the checker period at 1x (memo C §2e); memo D declares the scale, 0.5 at
  both display scales and 0.25 on rrect-lg, and memo E models it as that Gaussian floor before
  the knee.
- **hc-text fits the encoded-mean pointer** at each cell's own footprint mean (memo A). Memo A
  could reproduce W41's "hc-text does not fit" only by taking the mean from the bar geometry or
  as 128, and says so as an inference: G2's working is not in the record.
- **The pre-W41 group-level solve matched Apple's 188 on the checkerboard for a reason that is
  not Apple's mechanism.** W is a local encoded blur (memo C §0), and on a centred periodic
  pattern the local mean equals the group mean (memo B §5).

## Revision Notes

- 2026-09-29 (v2.1, drafted for the parent). Folds:
  - **memo E** (`w42-grounding-refit.txt`), the literal tree re-fitted on memo C's cells: all
    thirteen "pending memo E" marks resolved (Design, "Memo E's answers").
  - **the parent's rulings on memo E** (`w42-v2-memoE-rulings.md`): the narrow term is the
    declared opacity scaling a radius-5 blur, σn = k·5·o, with σw = k·8 and one k in points per
    endpoint (the mixture a rejected null); the capture is memo C's 0.8-dev floor before the knee
    (box decimation rejected); λ fitted per endpoint and w fixed at 0.5; U1 open and pointed at
    W's support or reach; R1 declared and R2 rejected; candidate 2's T the native curve from
    family A (the face matrix a light-only partial explanation, the note under Decision Log 5b
    superseded beside it, the face–knee order a tie); the bed's Q4 rows (B' on rrect-lg; D's
    δ 12 restored when receded), with memo E's 1x reading adding rrect-md pitch 4 at 1x.
  - **the review's own text for findings 9 and 15–17** and the parent's calls on v2 (the
    addendum in `w42-v1-review-rulings.md`): 9(a) B' rows on rrect-64 and rrect-lg; 9(b)'s
    mixture framing superseded by memo E; 9(c) the narrow term a function of opacity and pose;
    9(d) the continuation above 160 declared as the clamp; 15 the dark heavy's `scatterLod` path
    among D1's superseded leaves; 16 §5.55–§5.58 an OS difference, the argument for keeping 26.5
    at identity; 17 the per-surface support's pyramid cost, identity at G2's frozen base, the F
    extension's own gate-group and ruling 2's placement; H's span test at s = 112 if G0 can
    declare it; family A's dark greys on rrect-80.
  - **PR #2 merged** on main at `399c6bbf` and released there as 0.25.0 (`10c52933`): G2's base
    includes it.
  - The rejected nulls are recorded in Surprises with memo E's numbers. The bed is now 88 / 91 /
    86 / 89 cells per 2x pass and 15 per 1x pass, about 8.7 h of capture at seven runs plus about
    1.0 h of dumps.
- 2026-09-29 (v2, drafted for the parent). Folds:
  - **the adversarial review of v1** (`0868784c`), every finding verified and disposed by the
    parent (`w42-v1-review-rulings.md`): B1 to the user as Decision Log 5b; the pre-sitting
    rehearsal of every referee (clause 3, X39); the owner test over the six gated profiles and
    the law's accessibility behaviour; two directional stops and C's surround annulus; the
    candidate-admission mode; the new bed self-sufficient for the active span law and X34
    corrected; the narrow term reframed as the dump's mixture; D's outside steps; the rrect-lg
    bleed rows; A's bright greys; F bridge-only; the CSS carry as one reference filter; the
    items of 15–17 (the dark `scatterLod` path named, §5.55–§5.58 an OS difference, K1b's
    pyramid cost in the tie-break, identity at G2's frozen base, the F extension a new
    gate-group); the honesty corrections (memo C's full σw ranges and a shared-σw rival, the
    W34 capsule's 2.8× / 4.5×, all three hc-text cells, memo B's undecided dark rrect-md, the
    linear-favouring dark lc16, the knee's three fits, w fixed at 0.5); and the minor items (the
    tie-break, E at pitch 64 with its luma named, `dump-layers` first, the W42 web plan, the
    odd-offset 1x cell, the face–knee order rival). The review's offsets were taken: B' pitch 8
    receded and D's inside δ 12.
  - **the parent's rulings on v1's ten drafter's notes** (`w42-v1-parent-rulings.md`): M2 to the
    user as Decision Log 5a; L1 growth not re-read, fixed by extending F above 150 from family
    A, with the shipped solve as the fallback; the eye strata as looks; the device-px floor in
    the law; native T for identification and landed T for validation; the shape footprint as a
    K1b variant; a receded composite-order rival; "every document" as every macOS 27 document;
    U7 on the active rows of D, B' and C; Decision Log 3's mirror allowed after the M2 fix wave.
  - **the user's Decision Logs 5a and 5b**, quoted.
  - **memo D** (`w42-dumps.txt`): v1's three pending points answered (the receded opacity is
    span-graded; points or backdrop pixels settled by the rrect-ml / rrect-lg pair; 1x equals 2x,
    so the reduced 1x pass stands, re-derived to 14 cells); LT, the literal layer tree, declared
    the primary family; the face matrix as candidate 2's starting T; the depth grading and t in
    the law; the sitting re-sized (about 8.3 h of capture plus about 0.9 h of dumps).
  - Memo E pending; its eight points are marked and fold at v2.1.
- 2026-09-29 (Decision Logs 1, 2 and 6, the user, relayed by the coordinator): land in this wave
  if every referee passes; seven repeats (about 8 h); the grant switched and the Mac left idle by
  the user's hand once the parent reports the tooling ready.
- 2026-09-29 (v1, drafted for the parent): chartered from the parent's decision skeleton and
  grounding memos A (argument), B (kernel) and C (probe), committed with their briefs and a
  scratch manifest under `packages/calibration/results/2026-09-29-w42-grounding/`. Memo D (the
  layer dump) was running; its three points were marked and folded at v2. Ten drafter's notes:
  clause 9 (M2, L1 growth, the eye's strata), the law (the device-px floor), T (two roles), the
  rivals (U3 supports, the receded order), D1/D2 (every document), U7 and Decision Log 3.
  Adversarial review requested before G0.
