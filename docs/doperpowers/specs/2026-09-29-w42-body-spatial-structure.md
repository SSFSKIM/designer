# W42 — the body's spatial structure: an encoded heavy blur, a one-sided narrow term, CSS-pixel widths, all four window states (2026-09-29)

**Status: v2 DRAFT (drafted for the parent). v2 folds the adversarial review of v1, the parent's
rulings on v1's drafter's notes and on every review finding, the user's Decision Logs 5a and 5b,
and memo D (Apple's declared layer tree). Memo E, the offline re-fit of that literal tree, is
still being written: every statement it will confirm or refute is marked **pending memo E**, and
it is folded at v2.1. Decision Logs 1, 2, 5a, 5b and 6 RULED by the user 2026-09-29; Decision Log
3 ruled by rule at charter and extended by the parent; Decision Log 4 and Decision Log 5's
remainder open. Ledger sections §5.194–§5.197 reserved (§5.198 if a child splits).**

Points still marked **Drafter's note** are v2's own; v1's ten were ruled by the parent and are
now written into the text they concerned (Revision Notes).

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
3. **Widths hold in CSS px, and both poses grade the narrow component by span.** σw reads 10–13
   on the active rrect cores and 13–19 on the receded ones (memo C §2a). Apple declares the
   narrow term as ONE radius-5 blur over the sharp half-scale backdrop, whose opacity is 0.8t at
   the centre when active and 0.4 + 0.4t when receded, with t = clamp((s − 64)/96, 0, 1)
   (memo D §0, §3). Every declared body input is the same at 1x and 2x (memo D §4).
4. **Apple's declared layer tree is this structure, literally.** The wide term is a radius-8
   fill composited Lighten 0.9 (light) or Darken 0.9 (dark), then Normal at the glass slider's
   position, 0.5 on the bed; the face colour matrix that follows it is affine on encoded values
   and gives the native black floor within 0.6 code in all four endpoints (memo D §0, §6).
   Nothing in that tree adapts to the backdrop (memo D §0).
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
starting from memo D's face matrix; it lands instead only if it passes every check, which could
close W36's grey-middle miss too. Rims, edge bands, the stroke and Apple's dark exterior contour
stay where W35–W41 left them.

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
     (rms 0.40–0.42); memo B recovered widths within 3–10 % and the share within 0.03–0.1 at 2x.
     A two-sided control reads the mirror statistic at vitrea's level (memo C: ≤ 0.024 at
     p ≥ 8). A known-space control shows the reader cannot manufacture a knee: memo C's encoded
     fit on vitrea's linear captures returned λ 1.4–1.5, so the knee is established by S and by
     every linear fit's loss, never by λ alone.
   - *Stop:* a reader that fails its control does not read Apple (memo B's two-Gaussian photo
     reader failed its control and was not used). A parameter the synthetic recovery cannot
     separate is declared non-identifiable on this bed before any fit.
3. **Every landing referee is rehearsed before the sitting (G0; X39).**
   - *Metric:* L1, M1, M2 (as Decision Log 5a ruled), C1, X1, E2 and the two directional stops
     of clause 10, each computed by memo A's body-swap: the shipped render with only the body
     argument replaced by the grounding law readings composed with the landed T.
   - *Bed:* each referee's adopted non-holdout population, in all four endpoints (memo A
     rehearsed the light receded endpoint only).
   - *Bar:* each referee's adopted bar. A referee that fails whatever the structure's
     coefficients, because of T, a membership or its own reading, fails "by construction".
   - *Stop:* a referee failing by construction goes to the user BEFORE the sitting, with its
     numbers. E2 is already a not-worse-than-baseline stop; if the rehearsal shows it failing by
     construction, the user rules its reading then.
4. **The sitting is attested (G1).**
   - *Metric:* the attestation of every capture.
   - *Bed:* the declared bed: four passes per scale (scheme × pose), 86 cells per active and 82
     per receded 2x pass and 14 per 1x pass (Design, "The bed"), **seven runs** (Decision Log 2,
     RULED), the declared no-glass references and sentinels. `dump-layers` over the whole
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
     both poses, both schemes), rendered with the SHIPPED documents at G2's base.
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
layer tree and no pixel. All of them, with their briefs, the parent's two rulings files and a
SHA-256 manifest of their scratch, are committed under
`packages/calibration/results/2026-09-29-w42-grounding/`; the raw scratch stays on the machine
under `~/vitrea-w42/grounding/`.

| memo | question | evidence read |
| --- | --- | --- |
| A, `w42-grounding-argument.txt` | the argument E3's F and g are evaluated at | canonical cal/val light-inactive checkerboard, impulse, photo (20 cells, 1x and 2x), light-active and dark cells for its question 2; W39 gradient calibration rows; G2's committed native body means for hc-text and the pitch series; both web trees |
| B, `w42-grounding-kernel.txt` | Apple's body blur: kernel, space, pose; the capture that identifies it | canonical cal/val in all four endpoints; committed uniform readings from the W39 and W34 archives; vitrea's code map and captures |
| C, `w42-grounding-probe.txt` | the probe series, the W29 dump, the smallest identifying capture | A's and B's evidence plus the canonical PROBE cells in every endpoint and scale, and the spent W34 archive's checkers |
| D, `w42-dumps.txt` | Apple's layer tree across spans, poses, schemes and scales | `dump-layers` on the W39 side bundle: 24 scenes × 4 endpoints × 2 scales, 208 surfaces, a settle-16 repeat; no pixels |
| E, `w42-grounding-refit.txt` | the literal layer tree (LT) fitted on memo C's cells through native T and through the literal face matrix; U1 re-tested | **pending memo E; folded at v2.1** |

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

**The shipped body** (memo B's float64 replica reproduces 11 web cores at rms 0.27–0.38): the
centre is enc(R + B·((1 − k)·Ksharp∗b + k·Kdeep∗b − L̄)) on the LINEAR-light backdrop b, with
Ksharp 1.58 dev at both scales and Kdeep about 14 dev (L4, platykurtic). The dark active document
names no heavy tap (`sizeHeavyTapSigma` 0 at both scales, lines 133–134), so its deep sample is
the chain level `scatterLod` (`wgsl/optics.ts:1052`; memo B: LOD 3.32, 9.7 dev at 2x). The tone
argument is group-level (the source mean when active, the silhouette encoded mean when receded).
The CSS tier blurs through `feGaussianBlur` in linearRGB. Neither tier has a knee (memo B §1, §6).

**The shipped documents.** macOS 27 light active / dark active / light receded / dark receded:
files `85ad7f7e3e0d` / `0eac5b294cc2` / `30fbe05986ae` / `5cec8c961201`, resolved digests
`be13dae45098fc89` / `2a4323f33df8d799` / `b0d0d8dacc6a03af` / `7c454858a3cbad5b`. The frozen
macOS 26.5 pair is `b2b570e4adcea8fb` / `874be66ea501621b`. E3's zero-gated identity-table group
(`bodyE3Strength` 0) is on main at the identity in every document (W41 Deferred at close 2).
`freeze.py verify` read 1,818 entries at drafting.

**The runtime base.** PR #2 (`perf/demand-driven-frames`, another session's, open, mergeable,
checks green at drafting) moves the root's frame loop to demand-driven frames and edits
`renderer-webgpu/src/renderer.ts`, `src/backdrop.ts`, `src/pyramid.ts` and
`src/silhouette-tone.ts`, files G2 also edits for D1 and D2. Its spec states that no material
constant, law or capture moved; the calibration page hand-steps `root.runFrame`
(`packages/calibration/web/scene.ts:866-877`), which the PR keeps exact. X37 governs.

## Design (advisory unless marked)

### The law: LT, Apple's literal layer tree (MARKED: the primary declared family; G0 declares every family with its count before any pixel of the new bed, and G2 fits on the new bed)

Let B be the backdrop in encoded sRGB, s the surface's short side in CSS px,
t = clamp((s − 64)/96, 0, 1), d the SDF distance from the edge (negative inside), and B½ the
backdrop sampled at the layer's backdrop scale (0.5 of the device resolution; 0.25 on rrect-lg).
All averaging is in **ENCODED** space.

- **The narrow term** is a mixture of the sharp half-scale backdrop and ONE radius-5 blur:

      C = (1 − o)·B½ + o·G(5)∗B½

  Active: o = 0.8t at the centre (d = −s/2), falling linearly in d to 0.4t at 1 pt inside the
  edge. Receded: o = 0.4 + 0.4t, flat in depth. These are memo D's exact laws; nothing in them is
  fitted. The half-scale sampling is a device-pixel operation, which is what memo C's 0.8-dev
  floor at spans 32–44 and the 1x fine-pitch aliasing read (§2e); every width in the law is in CSS
  px above that floor.
- **The wide term** W = G(8)∗B½ on the backdrop layer's support: the shape's bounding box plus
  the declared margin (active 0.35 s if s > 64, else 16; receded one device pixel). Memo C
  reads the receded W footprint-limited with the box fitting best; whether the declared support
  also beats the canvas in the active pose, where memo C's capsule preferred the canvas, is
  **pending memo E**.
- **The composite**, light: a Lighten of C with W at λ = 0.9, then Normal toward W at w = 0.5,
  the slider's position:

      M = (1 − w)·C + (1 − w)·λ·max(0, W − C) + w·W

  Dark is the mirror, a Darken with min: M = (1 − w)·C − (1 − w)·λ·max(0, C − W) + w·W.
- **The active bleed** (s > 64): a blur of radius 0.35 s at opacity 0.5t (light) or 0.8t (dark)
  through the declared bleed matrix; zero when receded. Whether LT needs it on rrect-ml and
  rrect-lg to meet memo C's σ-48 reading (19–36 % weight on the knee sides) is **pending memo E**.
- **The output** is y = T(M) (X35): candidate 1's landed T or candidate 2's native T.
- **LT's free parameters** are the radius-to-kernel mapping only: whether a declared radius is in
  points or in backdrop pixels (a discrete switch, which the rrect-ml / rrect-lg pair settles on
  the new bed), the kernel's scale per radius and its shape. Whether the dump's constants
  reproduce memo C's active cells through native T at the grounding readers' residuals, and
  so LT's final count, is **pending memo E**. Memo C's direct reading of the wide width (σw
  10–19, wider when receded) against one declared radius of 8 in both poses is the gap that
  mapping and the pose's support must close.
- **Uniform invariance by construction.** A constant backdrop maps to itself under every blur,
  every footprint normalisation, the mixture and the hinge (max(0, 0) = 0), so E3's uniform
  closure and the shipped uniform bodies are untouched by the structure (memo A). Clause 7 tests
  it.

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
- **Candidate 2, Apple's grey tone curve from the new capture, in all four endpoints.** Its
  declared starting form is memo D's face matrix: y = black + (white − black)·x on encoded x,
  Rec.709 saturation 1.2 (light) or 1.3 (dark), the light white fill at α 0.2, the cap at
  MaxLumaSDR × Clamp and, in dark, MaxLuma = max(0.35, 0.6 − 0.6t). Family A's greys referee it;
  its fitted deviations from the literal matrix (memo D §6: the light 1–3 code shoulder above 88,
  the dark compression above the floor) are counted as parameters. How many it needs is
  **pending memo E**. It lands instead of candidate 1 only if it passes every check, and may
  then close W36's grey-middle miss.
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

Counts are per endpoint, w fixed at 0.5 throughout. "σn(span)" is a declared span law whose
ordinate count G0 fixes.

| family | what differs from LT | parameters | on existing cells | answered by |
| --- | --- | --- | --- | --- |
| **LT, radius per pose** | the narrow radius free per pose (the review's r) instead of the dump's 5 | LT's + 1 | **pending memo E** | B', C |
| **K1** | a Gaussian C = G(σn)∗B with σn(span), no mixture; W on the canvas; λ free | 2 + σn(span): σw, λ | active 1.1–1.6 rms (C §4, with w free); receded fails; whether it stays within resolution of LT is **pending memo E** | B', D |
| **K1b** | K1 with W on the layer's bounding box | 2 + σn(span) | receded cores 0.35–0.8, λ drifts across pitch (C §4) | D, B, C |
| **K1b-shape** | K1b on the rounded-shape footprint, its margin a parameter | 3 + σn(span) | read beside box and canvas on every pitch-64 cell (C §2a) | D |
| **shared σw** | one σw for both poses of a scheme | one fewer than its base | memo C reads σw by pose (see Grounding) | A–D |
| **heavy tails** | W a mixture of two Gaussians, not one kernel | its base + 2: a second width and its weight | U4; not identifiable here (C §5) | C |
| **K2** | two fills: the knee against Wk, the normal mix toward Wn | 4 (memo C's 5, w fixed) | receded 0.5–1.5; no gain (C §4) | C, B |
| **receded composite order** | the receded composite in another order; its declared form is chosen after memo E | its base's | receded not closed by K1, K1b or K2 (C §2c); **pending memo E** | B, C |
| **face–knee order** | the face matrix applied before the knee composite rather than after it | its base's | not read | A, B |
| **C-linear** | the narrow term averaged in linear light, W encoded | its base's, a discrete choice | not identified: binary backdrops cannot show it, and the photo discriminator failed its CSS control (B §3) | B, D |
| **per-channel knee** | max/min per channel against on encoded luma | its base's, a discrete choice | not identifiable (C U6) | E |
| **LT without bleed** | the active bleed layer removed | LT's | **pending memo E** | D, B', C (U7) |

Nested and null families, reported and never nominated: memo A's reading C7 is K1 at λ = 1 (the
hard max memo C rejects). Memo B's F1 (one blur) and F2 (linear two-scale) are rejected by the
one-sided ESFs, and so is F4, vitrea's shipped form T(group) + b·(K∗B − group), which is the
baseline the referees read against.

**The tie-break (MARKED).** Among survivors that are "insufficient resolution" apart: resolution
first (a family that beats another at an admitted discriminator by more than max(3, sum of bars)
wins); within resolution, runtime cost (passes and texture reads on the WebGPU tier, K1b's
footprint normalisation priced as the loss of pyramid sharing across a group's surfaces); then
parameter count.

### D1 and D2 are in the law (MARKED; X36)

- **D1, device-px widths.** `renderer.ts:600-605` (`bodySigmaCssFor` = `optics.blurSigma` /
  dpr), `renderer.ts:638-644` (`heavySigmaCssFor`), `material.ts:4873-4878`
  (`heavyTapSigmaAtScale` returns device px); the light active document's lines 151–152 set
  `sizeHeavyTapSigma` 14 and `sizeHeavyTapSigma2x` 20, the light receded document's line 89
  sets 2x 14; the dark active document names no heavy tap and draws its deep sample from
  `scatterLod`, a chain level in device texels. The effect: the heavy width is 13.8 CSS at 1x but
  6.9 (receded) or 10 (light active) at 2x, where Apple reads 10–19 at both scales (memo C §7,
  §2a). The doc comment at `renderer.ts:582-586` cites §5.55–§5.58 ("one kernel in device pixels
  at both scales"); those readings were taken on macOS 26.5, so this is an OS difference, not a
  reversal of them.
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

| U (memo C §5) | what is open | family |
| --- | --- | --- |
| U1 | the receded one-sided algebra: λ drifts 0.6–1.1 and per-side kernels differ; memo E re-tests it under LT (**pending memo E**) | B (the hinge reference against mean and contrast), C (which level the one-sided term hinges on) |
| U2 | the receded narrow span law, now declared (0.4 + 0.4t) and to be confirmed in pixels | B', with C's depth sweep as its flat-in-depth control |
| U3 | the footprint support: box, rounded shape or margin; the edge normalisation; whether the active W is footprint-limited | D (inside and outside steps), both poses |
| U4 | the heavy kernel's tails | C |
| U5 | T at 150–242 in every endpoint, dark T by span, and candidate 2's face deviations | A |
| U6 | a per-channel against an on-luma knee, and the chroma kernel | E |
| U7 | the active bleed as a third component | D (active steps on rrect-md and rrect-lg), B' (active rows at spans ≥ 80), C (S 32 on rrect-md) |
| — | points or backdrop pixels for the declared radii | the rrect-ml / rrect-lg pair in C (impulse and patches) |
| — | the active narrow opacity's depth grading (0.8t → 0.4t) | C's depth sweep on rrect-md and rrect-lg |

### The bed (MARKED: the families and their questions; exact ids and levels are G0's)

Memo C §6, grown by the review's rulings and memo D's implications. Existing JSON kinds only
(solid, two-level checkerboard, impulse as a single patch, split, shape `position`); every kind is
checked against the side bundle's pinned build before it is declared. The canvas is 320×200, as
canonical (memo B §8). Every s ≤ 64 is one declared stratum (t = 0); the span budget goes to
t = 1/6, 1/3, 2/3 and 1 (s = 80, 96, 128, 160) plus a t = 0 shape (memo D §7a). Backdrop and
position switch no declared input, so no family is stratified by backdrop (memo D §7f). Four
passes per scale (scheme × pose).

**2x, per pass:**

| family | cells | answers |
| --- | --- | --- |
| A — uniform greys 0, 64, 128, 160, 176, 192, 208, 224, 240, 255 × {capsule, rrect-md}; 96, 160, 208, 255 × rrect-lg; bright 160, 208, 255 × {rrect-64, rrect-ml} | 30 | U5: native T per endpoint and span, the F extension, candidate 2's face; dark MaxLuma on both sides of its knots |
| B — two-level checkers P2 48/208, P3 96/160, P4 16/112, P5 144/240 at pitch 16 and 64 on rrect-md | 8 | U1; the space on non-binary structure; the declared λ and w refereed |
| B' — P1 0/255 at pitch 8, 32, 64 on capsule and rrect-ml; P1 at pitch 32 on rrect-64 and rrect-80 | 8 active, 6 receded (pitch 8 dropped when receded) | U2; the active span law from the new bed alone (review 8); U7 on rrect-ml |
| C — single square S 8, 32 × 2 polarities on rrect-md and S 16 × 2 on capsule, each with a surround annulus; S 8 at s/4 and 4 pt from the edge on rrect-md, and at the centre, s/4 and 4 pt from the edge on rrect-lg; the canonical impulse on rrect-ml and rrect-lg | 13 | U4; U1; the depth grading (a free falsification control when receded, where it must read one width); points against backdrop pixels; the annulus for the halo stop |
| D — step under the interior (split) at shape offsets δ 0 and 32 × 2 polarities on rrect-md, δ 0 on capsule; steps 8 and 16 CSS px OUTSIDE the rrect-md edge × 2 polarities; active only, a step at δ 0 under rrect-lg × 2 polarities | 11 active, 9 receded | U3; U7 (the rrect-lg rows are the review's bleed rows) |
| E — isoluminant chroma checkers, 2 hue pairs, pitch 16 and 64, rrect-md; G0 names the matched luma | 4 | U6 |
| F — bridges: canonical checker-16 rrect-md, impulse rrect-md, photo rrect-md; probe checker-64 rrect-lg | 4 | the bar across sittings only (not under clause 6) |
| H — the structured holdout, declared before fitting | 8 | referee |

Per active pass 86 cells, per receded pass 82. Against memo C's 66: A +6, B' +2 (active) or 0
(receded), C +7, D +3 (active) or +1 (receded), E +2; the drops are B' pitch 8 when receded and
D's inside δ 12.

- **H** (memo C): P1 at pitch 24 on rrect-80; P6 32/176 at pitch 32 on rrect-md; a step at δ 20;
  a patch S 24; P3 at pitch 64 on rrect-lg; 128/229 at pitch 64 on capsule; greys 184 and 232 on
  rrect-md. Six of the eight are structured.

  > **Drafter's note (H's span cell).** Memo C placed P1 on rrect-80 in H as "a new span". The
  > review's ruling 8 puts rrect-80 rows into calibration, so that cell now tests an unseen pitch
  > at a calibrated span, not an unseen span. If the wave-local scenes file can declare an rrect
  > of another size without a rebuild (components are data in `scenes.json`), the drafter
  > suggests G0 give H an unseen t instead, for example s = 112 (t = 0.5).

**1x, per pass: 14 cells, re-derived from memo D's criteria.** No declared input differs with
scale beyond four one-device-pixel terms (memo D §4), so a 1x cell earns its place only where
sampling density or device-pixel geometry can matter: pitches of 8 pt or less, patches of 4 pt or
less, rrect-lg (one backdrop pixel per 4 pt at 1x), and edge strips; the body-level families keep
only a small referee (memo D §7g).

| criterion | 1x cells | count |
| --- | --- | --- |
| fine pitch ≤ 8 pt | P1 at pitch 4 and 8 on capsule; P1 at pitch 4 on capsule at an odd CSS-px offset (the review's odd-offset cell: half a backdrop texel of phase) | 3 |
| rrect-lg | P1 at pitch 4, 8 and 16 on rrect-lg | 3 |
| small patch ≤ 4 pt | the canonical impulse on rrect-lg | 1 |
| edge strip | the D step 8 CSS px outside the rrect-md edge, one polarity (the receded margin is one device pixel) | 1 |
| small body referee | greys 128 and 255 on rrect-md | 2 |
| bridges (bar tie) | impulse rrect-md; probe checker-64 rrect-lg | 2 |
| H at 1x | P3 at pitch 64 on rrect-lg; grey 232 on rrect-md | 2 |

Memo C's 22 drop to 14: its six body-level greys, capsule pitch 16, the photo and checker-16
bridges and two H cells go; the odd-offset cell, the rrect-lg impulse and the edge strip come in.

**The sitting at seven runs**, on W39's model as memo C used it (9.53 s per capture, including
each no-glass reference; 16.3 s per sentinel; 13 s per run; 25 s per pass):
- glass captures: 2x (2 × 86 + 2 × 82) × 7 = 336 × 7 = 2,352; 1x 4 × 14 × 7 = 392; total 2,744;
- no-glass references, one per distinct backdrop per pass in run 1: 2x 2 × 44 + 2 × 43 = 174,
  1x 4 × 10 = 40; total 214;
- (2,744 + 214) × 9.53 s = 28,189.7 s; 48 sentinels × 16.3 s = 782.4 s; 8 passes × 7 runs ×
  13 s = 728 s; 8 passes × 25 s = 200 s;
- **total 29,900.1 s ≈ 8.3 h of capture**, against memo C's 7.6 h. If memo C's capture-to-wall
  ratio holds (7.6 → about 8 h), that is about 8.7 h at the Mac;
- plus `dump-layers` over the declared bed first, at memo D's rate (about 200 s per 24 scenes):
  (2 × 86 + 2 × 82 + 4 × 14) = 392 scene-dumps ≈ 3,270 s ≈ 0.9 h, no grant needed.

The total, about 9.6 h, is over Decision Log 2's "about 8 h"; the review ruled that the net
length is stated to the user at the "tell me first" moment (Decision Log 6), with seven runs
standing.

### Memo D's answers to v1's pending points (folded)

1. **The receded narrow width is graded by span, not flat.** Its opacity is 0.4 + 0.4t (0.400
   for s ≤ 64, 0.467 at 80, 0.533 at 96, 0.667 at 128, 0.800 at 160) and flat in depth. The
   receded narrow term therefore carries the declared span law, B' keeps its capsule and
   rrect-ml rows beside the new rrect-64 and rrect-80 rows, and C's depth sweep is its
   falsification control.
2. **Points or backdrop pixels: still open, settled by the bed.** Memo D reads the radii equal at
   both scales and the pixel widths close to scale-invariant, which points to POINTS. rrect-lg is
   the only surface at backdrop scale 0.25; with the σ ≈ 10·opacity pointer and radii in points,
   both poses predict σ ≈ 8 at its centre, and about 16 if the radii are in backdrop pixels
   (memo D §7c). C's rrect-ml / rrect-lg pair (s 128 at scale 0.5, s 160 at 0.25) decides it.
3. **1x and 2x agree on every body parameter.** The four scale-dependent quantities each equal
   one device pixel (the highlight's height and offset, the receded margin, the receded SDF
   output maximum). The reduced 1x pass stands and is re-derived above to 14 cells. Where native
   1x and 2x pixels differ (memo B: light-active rrect-md σ 1.31 against 2.36), the cause is the
   realisation, sampling density or the device-pixel terms, not a declared input.

### Pending memo E (folded at v2.1)

Memo E fits LT with the dump's constants against memo C's cells, through native T and through the
literal face matrix, and re-tests U1. It will confirm or refute:
1. whether LT at the dump's literal constants (o's span and depth laws, radii 5 and 8, λ 0.9,
   w 0.5, the declared margin) reproduces memo C's ACTIVE cells through native T within the
   grounding readers' residuals;
2. whether LT closes U1, the receded one-sided algebra that K1, K1b and K2 left open;
3. LT's radius-to-kernel mapping (scale and shape), and so LT's final parameter count, including
   whether the review's radius per pose is needed;
4. how far the literal face matrix is from native T, and so candidate 2's count of deviations;
5. which receded composite-order rival G0 declares (the review sequenced it after memo E);
6. whether LT's active form needs the bleed layer on rrect-ml and rrect-lg (U7);
7. whether the Gaussian σn(span) rival stays within resolution of LT on memo C's cells, and on
   which cells they separate;
8. whether LT's box-plus-margin support beats the canvas in the active pose.

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

- The readers, proved first (clause 2): the LT forward model and memo C's model reader (C and W
  on canvas, box and shape supports, the knee, T), the mirror statistic S, the pitch-64 heavy
  reader, the ESF and impulse readers (memo B), the step reader for D, the patch and annulus
  reader for C, and the depth-graded opacity reader.
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
`feGaussianBlur` from `SourceGraphic` at `color-interpolation-filters="sRGB"` (the narrow mixture
and the wide fill), `feBlend` lighten (dark: darken) and `feComposite` arithmetic for the λ and w
weights. `backdrop-filter` reads only the element's box, the box footprint for free (Chromium's
edge mode is unmeasured). The stacked route, encoded `blur()` layers with `mix-blend-mode`
lighten/darken at opacity, is the approximation for engines that render no reference filter.
E3's F and g, or candidate 2's face, take W41's affine route (`w41-g2-css-candidate`
`78c4b854`), re-derived against the law as W41 Deferred at close 5 lists. Decision Log 4 still
needs the Chromium proof.

### The runtime base (MARKED; X37)

G2 branches from main as it stands when G2 starts, after PR #2 if it has merged. Before any
candidate render, G2 re-renders a declared sample of the canonical bed with the SHIPPED documents
at that base and shows it byte-identical to the canonical capture tree, so every rendered
difference is attributable to the candidate and not to the base. G3 proves the seal's identity at
G2's frozen base; if the base has moved, clause 8's proof runs again first. W42 never merges or
publishes PR #2.

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
  (`backgrounds` / `self-check`, no capture).
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
- **About 8.3 h of capture at seven runs, plus about 0.9 h of dumps**, in one sitting while the
  user leaves the Mac idle.
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
  a structural parameter; candidate 2 takes native T from the face matrix's declared form with
  counted deviations (Decision Log 5b).
- **X36 — D1, D2 and the F extension land inside the law.** Each is a gate-group appended to the
  identity table; at the identity it draws exactly what ships today; the frozen macOS 26.5 pair
  never leaves it.
- **X37 — the runtime base is proved before any candidate render** (clause 8) and again whenever
  it moves before the seal; W42 never merges or publishes PR #2.
- **X38 — dump numbers are pointers.** A layer-tree number becomes evidence only where the
  pixels agree; the pixels govern. LT declares the dump's constants as a hypothesis the bed
  referees.
- **X39 — every referee is rehearsed before the sitting** (clause 3); a referee that fails by
  construction reaches the user before a native pixel is spent.
- **X40 — two candidates, one receipt.** Candidate 2 lands instead of candidate 1 only if it
  passes every check candidate 1 faces; both are bound by the same exposure receipt.

## Ordering & Dependency Map

Decision Logs 1, 2, 5a, 5b and 6 RULED (2026-09-29) → memo E lands → v2.1 (memo E folded) → G0
(declaration hashed; instrument proved; referee rehearsal, with any by-construction failure to
the user; bed, split, web plan and gate tooling; review; merge) → the parent tells the user,
with the sitting's net length (Decision Log 6) → G1 (dumps; the user's grant switch and X5 lift;
passes; archive; bar; the user restores both) → G2 (base proof → native T → calibration fit →
validation transfer → gated operators on both tiers → rendered candidates → canonical renders →
**the gate** → freeze → ONE exposure on H; Decision Log 3 if needed) → G3 (the M2 fix wave if
receded-only → seal → identity → Decision Log 4 → stage read, both tiers → canonical holdout once
→ Decision Log 5 → publish → capture tree → eye sheets → changeset → release checklist → the
user's `pnpm release`) → close.

## Risks & Mitigations

- **The receded algebra does not close (U1).** It did not on existing cells, and every declared
  variant failed the same way (memo C §2c); LT is re-tested by memo E. Mitigation: Decision Log
  3; the receded documents stay at identity and E3 stays unshipped; the negative is recorded at
  its resolution.
- **LT's literal constants do not reproduce the pixels** (**pending memo E**). Mitigation: the
  Gaussian σn(span) and K-family rivals are declared beside it, the tie-break chooses, and the
  declared constants stay pointers (X38).
- **A referee fails by construction.** Mitigation: clause 3's rehearsal before the sitting, with
  the user ruling on the numbers; Decision Log 5a already rules M2's reading.
- **A wrong mixing space manufactures a knee.** Memo C's encoded fit on vitrea's linear captures
  returned λ 1.4–1.5. Mitigation: the knee is established by S and by every linear fit's loss
  (clause 2), and the synthetic controls run in both spaces.
- **The sitting is longer than Decision Log 2's estimate** (about 8.3 h of capture plus about
  0.9 h of dumps, against about 8 h). Mitigation: stated to the user at the "tell me first"
  moment; the review's offsets (B' pitch 8 receded, D's inside δ 12) are already taken.
- **The heavy chain costs frames.** An encoded blur at radius 8 on a half-scale backdrop adds
  passes beside PR #2's demand-driven loop. Mitigation: the tie-break prices cost; G3 reads the
  renderer bench beside the goldens and records it; a regression is a finding for the parent.
- **The machine is shared.** Foreign browsers and another session's Playwright refused W41's
  reads (§5.192 §1, §5.193 §3). Mitigation: X6 before every launch; the sitting runs only when
  the user leaves the Mac idle (Decision Log 6).
- **Some H cells cannot be posed on the web.** Mitigation: the W42 web plan says which; those
  referee the numerical structure only.
- **The canonical holdout fails after H passed**, as W41's canonical referees failed after the
  W39 holdout passed. Mitigation: clause 10 puts every referee readable without a holdout first;
  the canonical holdout's miss goes to Decision Log 5.
- **The backdrop scale step's cause is unknown.** It sits between rrect-ml and rrect-lg, and the
  dumps cannot say whether span or area sets it (memo D §3). Mitigation: LT carries the scale per
  surface as declared; a runtime surface between the two is a named gap until a bed reads one.

## Deferred / Out of Scope

- **The level misses under candidate 1.** W36's grey middle and chroma stay named whenever the
  landed T is the shipped solve; candidate 2 is the route that could close them. F above 150 is
  extended only through family A's measured ordinates (X35).
- **The edge.** Rims and edge bands, the lens band, the bright inner line (W35), the top/bottom
  obstruction (W37), the stroke and Apple's dark exterior contour (W41 Deferred at close 3–4),
  and distance-to-edge grading (memo B §8). Memo D's pointers for that line: the key/fill
  highlight band is one device pixel high and one inward at both scales; the ring shadow is
  active only and cannot be W39's receded contour; the receded SDF output reaches 1 pt + 1 dev
  beyond the path, where W39 saw the contour, but the light face's lift there would lighten it
  rather than darken it, which is open (memo D §7h).
- **Other slider positions.** Normal and the light fill track `NSGlassTintAmount`; dumps and
  captures at slider 0 and 1 would isolate the normal-weighted wide term, but they are a user
  setting and a new bed key (memo D §7d). The user's call, not this wave's.
- **Tint, the clear material, glass-over-glass, accessibility, the recede transition in time,
  spans above 160** (where t's clamp at 1 is inferred), **non-sRGB content, a Light system
  appearance** (memo B §8; memo C §6; memo D §8).
- **Light active grey-128's +3 codes at s = 96**, which no declared face input explains (memo D
  §6): named, possibly bleed or refraction.
- **The private filter's semantics** beyond its effective transfer.
- **The narrow term's averaging space**, if families B and D cannot separate C-linear from
  encoded at the bed's resolution: recorded as unidentified, with the capture that would.

## Tracking Map

| child | status |
| --- | --- |
| G0 | — (after v2.1) |
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
by the review's rulings and memo D (about 8.3 h of capture plus about 0.9 h of dumps); the net
length is put to the user at Decision Log 6's "tell me first" moment.

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
- **Apple declares the structure the pixels read.** A radius-5 narrow blur at a span- and
  depth-graded opacity over a half-scale backdrop, a radius-8 fill at Lighten or Darken 0.9, then
  Normal at the slider: 17 closed-form laws in one size variable reproduce all 104 surfaces
  (memo D).
- **W29's "Normal 0.546" was the slider**, not a material constant (memo D §0), and nothing in the
  declared tree adapts to the backdrop.
- **The receded narrow opacity is span-graded** (0.4 + 0.4t), which W29's single receded dump
  had hidden (memo D §5).
- **Apple's widths hold in CSS px on macOS 27; vitrea's are device px** (memo C §7). §5.55–§5.58
  read one kernel in device pixels on macOS 26.5: an OS difference, not a reversal.
- **A half-resolution backdrop shows in the pixels**: the 0.8-dev narrow floor at both scales
  and one-sided blobs at the checker period at 1x (memo C §2e), and memo D declares the scale,
  0.5 at both display scales and 0.25 on rrect-lg.
- **hc-text fits the encoded-mean pointer** at each cell's own footprint mean (memo A). Memo A
  could reproduce W41's "hc-text does not fit" only by taking the mean from the bar geometry or
  as 128, and says so as an inference: G2's working is not in the record.
- **The pre-W41 group-level solve matched Apple's 188 on the checkerboard for a reason that is
  not Apple's mechanism.** W is a local encoded blur (memo C §0), and on a centred periodic
  pattern the local mean equals the group mean (memo B §5).

## Revision Notes

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
