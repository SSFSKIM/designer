# W42 — the body's spatial structure: an encoded heavy blur, a one-sided narrow term, CSS-pixel widths, all four window states (2026-09-29)

**Status: v1 DRAFT (drafted for the parent from its decision skeleton and grounding memos A–C);
memo D, the native layer dump, is still running and is folded at v2; adversarial review
requested before G0. Decision Logs 1, 2 and 6 RULED by the user 2026-09-29; Decision Log 3 ruled
by rule at charter; Decision Logs 4 and 5 open. Ledger sections §5.194–§5.197 reserved (§5.198
if a child splits).**

Drafter's notes (marked **Drafter's note**) sit beside decisions the drafter would question; the
decisions stand as the parent wrote them. Points memo D is meant to settle are marked **Pending
memo D; folded at v2**, each with what its outcomes would change.

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
native capture with a structured holdout. The offline pass is done: grounding memos A, B and C
(Grounding Baseline). What they found makes E3's failure one instance of a gap across the whole
material:

1. **Apple's body is two spatial scales composited one-sidedly, in all four endpoints.** A
   narrow component carries the visible detail. A wide component sets a floor in the light
   scheme and a ceiling in the dark one, which the detail can rise above (light) or fall below
   (dark) and not cross the other way (memo B §0). On the checkerboard the native suppressed
   side stays within 2.6 codes of zero while vitrea's shipped body draws it: shipped dome ratios
   −1.04 to −1.31, where any linear filter in encoded space reads −1 (memo A, question 2). A
   mirror statistic that is zero for any two-sided linear system reads 0.2–0.5 on Apple and
   ≤ 0.024 on vitrea (memo C §1).
2. **The wide component averages ENCODED values, locally.** Encoded averaging before the tone is
   the only order within about 3 codes in all four endpoints; linear averaging misses by ≥ 12
   codes (memo B §0, §3). A group mean loses by 5–10× rms on every pitch-64 cell, so W is a local
   blur (memo C §0). The checkerboard's black cells read 186.8–188.1 against F at the encoded mean,
   187.8; the linear-light mean predicts 212.3 (memo A, reading 1).
3. **Widths hold in CSS px, and the receded pose widens the narrow component.** σw reads 12–13
   (active) and 14–19 (receded), identical at 1x and 2x (memo C §0). The narrow component is
   span-graded when active (2.0 / 4.0 / 4.5 at spans 96 / 128 / 160, the same at both scales) and
   wider when receded (4–4.5 at spans 32–44, 5.5–9 at spans 96–160, noisy) (memo C §0). Memo B
   reads rrect-md's narrow width as 2.0–2.4 active against 5.0–5.8 receded (§0).
4. **Two shipped defects sit on the same line.** vitrea fixes both body widths in DEVICE px (D1)
   and blurs and mixes in linear light on both tiers (D2) (memo C §7). They are part of the law
   (Design), not a separate fix.

W42 declares that structure as a law with its rivals before any pixel of a new bed exists (G0),
captures the bed that identifies what existing cells cannot (G1), fits it on the new bed's
calibration set and transfers it to validation (G2), and passes the canonical landing referees
on the candidate's calibration/validation renders **before** spending its one exposure on the
structured holdout H. That order is the lesson W41 paid for: W41 spent the W39 holdout on E3
(§5.192 §25), and L1 and M2 then failed on canonical calibration/validation cells that could have
been read before the exposure (§5.193 §3). **The wave lands what closes (G3), conditional on
every referee passing** (Decision Log 1, RULED: "Land in this wave, if every referee passes").

W42 identifies spatial structure. It does not refit T, the endpoint's uniform response: the
level misses already recorded (W36's grey middle, chroma) stay named and are not W42's to close.
Rims, edge bands, the stroke and Apple's dark exterior contour stay where W35–W41 left them.

## Parent-Level Acceptance

Each clause names its metric, the bed it is read on, the bar and what stops the wave.

1. **Declared before the bed exists (G0).**
   - *Metric:* the declaration's SHA-256, committed and independently reviewed, against the
     timestamp of the first native capture of the new bed.
   - *Bed:* the declaration itself. It holds every family of Design with its parameter count,
     working space, support, span-law form and knots; T's two roles and its interpolation and
     continuation (X35); the bed's families A, B, B', C, D, E, F and H with exact ids, and each
     U-item's family; the split (calibration, validation, H), enforced by the wave reader and
     launcher; the region statistics and their populations; the survival and closure rules
     (clauses 5 and 10); the landing-referee gate (clause 9); the stops. Memo D is folded.
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
3. **The sitting is attested (G1).**
   - *Metric:* the attestation of every capture.
   - *Bed:* the declared bed: four passes per scale (scheme × pose), 66 cells per 2x pass and 22
     per 1x pass as memo C sized it (pending memo D), **seven runs** (Decision Log 2, RULED), the
     declared no-glass references and sentinels, and `dump-layers` on every scene.
   - *Bar:* on every capture, the four X6 facts (Reduce Transparency 0, Increase Contrast 0,
     `NSGlassTintAmount` 0.5, zero foreign browser or capture processes after the measured idle
     window) and W34 X4's native set (build 26A428, `ButtonShapesEnabled` 0, Show Borders 0,
     the display mode before and after, the colour context, the side bundle's cdhash and
     `LC_BUILD_VERSION`, `deterministic`, the pose as the harness attests it, the requested and
     actual window frame and the shape's attested `frameOrigin`).
   - *Stop:* a run that fails to attest is quarantined and named. A wrong mode, a lost grant, a
     failed idle window or a foreign process stops the pass; there is never a hidden retry.
     Nothing is read against vitrea in G1.
4. **Repeats before thresholds; the archive of record (G1).**
   - *Metric:* the bar per cell, region and channel: 0.5 plus half the largest pairwise
     separation of the run medians, computed before plurality (W39's rule).
   - *Bed:* every admitted run, the losing states preserved.
   - *Bar:* the bar published before G2 opens; a zero observed spread buys no tolerance. The
     archive is complete, published as a release asset named by SHA-256 and byte size, and
     replayed identically with the raw root denied.
   - *Stop:* G2 does not open until the bar and the replay are committed.
5. **Identification on calibration, transfer on validation (G2).**
   - *Metric:* the declared region statistics per required channel: checker cell-core medians on
     the knee and far sides, patch cores, step plateaus and transition bins, uniform deep medians.
     Per-cell deep-body rms is reported beside them and never gated.
   - *Bed:* the new bed's calibration set, which is the only fit input; its validation set,
     read-only transfer.
   - *Bar:* W39 clause 8 verbatim. A family SURVIVES only at max(1 code, bar) on every required
     channel of every calibration AND validation cell and region before the freeze; survivors
     within max(3, sum of bars) at every admitted discriminator are "insufficient resolution".
     X31's three statuses and X21's one-sided censoring carry. Fits are least squares and
     minimax, equal weight per cell; the width parameters make every family non-linear, so each
     search is a bounded deterministic multistart stated as LOCAL.
   - *Stop:* an endpoint with no survivor is this wave's negative at its resolution. If the
     receded endpoints fail, Decision Log 3 applies. No family is added after the bed's first
     read.
6. **Uniform invariance (G2).**
   - *Metric:* the rendered deep-body median on uniform cells.
   - *Bed:* the canonical uniform calibration/validation cells and the new bed's family A,
     each rendered with the candidate and with every W42 spatial gate at its identity.
   - *Bar:* every family maps a constant backdrop to itself (memo A), so the two renders agree
     within one code on every endpoint: against the shipped render on the three endpoints whose
     T is the shipped solve, and against E3 alone (its W41 closure, §5.192 §25) on the light
     receded endpoint.
   - *Stop:* a departure is an implementation defect, found and fixed before clause 9's gate.
7. **The runtime base (G2).**
   - *Metric:* PNG byte identity.
   - *Bed:* a sample of the canonical bed declared in G0 (every backdrop kind, both scales,
     both poses, both schemes), rendered with the SHIPPED documents at G2's base.
   - *Bar:* byte-identical to the canonical capture tree, after `check-capture-tree` exits 0 on
     that tree.
   - *Stop:* no candidate render until any difference is attributed and resolved (X37).
8. **The rendered candidate on the new bed (G2; W41 clause 11).**
   - *Metric:* clause 5's region statistics, read on vitrea's render with the same instrument.
   - *Bed:* the new bed's web-plannable calibration and validation cells; G0 declares which are
     plannable.
   - *Bar:* clause 5's survival bound.
   - *Stop:* a candidate whose operator fails is removed from the code before G2's merge; its
     diff and renders are kept as evidence.
9. **The landing referees pass BEFORE the exposure (G2; X33).**
   - *Metric:* the L1, M1, M2, C1, X1 and E2 cuts, regenerated from the candidate's renders by
     W41 G2's ported referees (`results/2026-09-29-w41-g2-landing/referees/`) in `--stage` mode;
     and eye sheets chosen BY STRATUM: uniform, binary structure, text, impulse, photo, gradient.
   - *Bed:* the candidate's renders of each referee's adopted non-holdout population: the
     canonical calibration/validation cells, plus the probe rows X1 and E2 already admit, on the
     WebGPU tier, macOS 27 standard profiles, 1x and 2x, in a scratch stage that is never
     published. The eye sheets show native | shipped | candidate with ΔE×8.
   - *Bar:* the adopted rows as they stand when G2 opens. L1 ≤ 0.055 absolute, with growth
     ≤ 0.005 against its W33 baseline. M1 median in [0.8, 1.2], cells in [0.6, 1.4]. M2 within
     2 % of its reference generation, the shipped one when G2 opens. C1 ≤ 0.0042 per bed × span.
     X1 zero pixels above native black. E2: no measured bin worse than its frozen baseline by
     more than one code, and UNMEASURED never a pass. Named misses stay named and none is added.
     The eye: the parent's verdict per stratum is recorded, and no stratum reads visibly further
     from native than the shipped render.
   - *Stop:* any failure means no exposure. H stays sealed, the result is recorded in §5.196, and
     the candidate returns to identification on calibration or the wave closes at the negative.
     **This is the lesson of W41**: a holdout exposure is spent only on a law that has already
     passed every landing referee that can be read without it.

   > **Drafter's note (M2).** As written, M2 cannot pass for any law that moves photo structure,
   > whatever the direction. Memo A's table C reads every candidate failing M2 on all eight
   > light-inactive photo cells; its best reading, C7, fails all eight while moving each toward
   > native, and E3 did the same at W41 G2 (§5.193 §3). The grounding also reads shipped photo
   > luma sd at 0.25–0.37 of native in the dark scheme (memo A, question 2), so a law that closes
   > that gap moves those cells' structure by far more than 2 %. The drafter recommends that
   > Decision Log 5's M2 reading be ruled before G2's gate rather than in G3: either M2 is read by
   > direction (a move toward native passes, an overshoot fails) or its reference is re-based for
   > this gate. Otherwise the gate is unpassable by construction.

   > **Drafter's note (L1 growth under a T that is not refit).** §5.193 §3 records, under E3's
   > level, three light-solid inactive growth failures (+0.0051 to +0.0066) and two tinted photo
   > inactive ones (+0.0131 / +0.0136). Memo A's table C attributes its two tinted photo
   > rrect-md tint-orange growth failures (+0.007 to +0.011) on every candidate to tint and level
   > composition, not to the argument. No spatial family moves a uniform cell (clause 6), so with
   > T = E3's F held, the light-solid failures recur by construction. Either Decision Log 5 rules
   > on L1 growth before the gate, or the light receded claim waits for a wave that refits T.

   > **Drafter's note (the eye's strata).** The canonical calibration/validation bed has no text
   > and no gradient cell: hc-text is holdout or probe, and gradients exist only in the W39
   > archive. The text stratum therefore reads the canonical probe hc-text cells (calibration
   > evidence under X34) and the gradient stratum the W39 archive's web-plannable gradient cells
   > (`v90`/`v270`, calibration rows). The canonical holdout's hc-text cells stay sealed until G3.
10. **The one exposure on H (G2; X26 as carried).**
    - *Metric:* clause 5's statistics on the held-out cells: the numerical candidate on all of
      them, the rendered candidate on the web-plannable ones.
    - *Bed:* H, declared before capture (memo C: 8 cells per 2x pass, 6 of them structured, and a
      1x subset of 4), its payload behind the procedural boundary until the receipt.
    - *Bar:* max(1 code, bar) on every measured held-out cell of the claimed endpoints. A censored
      held-out cell is UNMEASURED and counts toward neither pass nor coverage; the measured
      coverage is reported. The rendered H predictions are produced blind from the public
      declaration and frozen by hash before the receipt, which recaptures them and requires
      equality before any native held-out pixel is scored.
    - *Stop:* a failure means the law does not close and nothing lands. H is spent either way,
      and no candidate changes after the receipt.
11. **Nothing shipped moves until clause 10 passes (G0–G2; W39 clause 9).**
    - *Metric:* the protected-path diff; `freeze.py verify`; the goldens.
    - *Bed:* `scenes.json`, `fixtures/`, the frozen matrix, `results/generations/`,
      `results/superseded/`, the six material documents, the generated profiles, the goldens and
      every adopted threshold.
    - *Bar:* no byte moves; the freeze reads 1,818 at every merge. Operators added in G2 sit at
      their identity behind zero gates, appended to the identity table, so no document digest
      moves and the goldens stay byte-identical.
    - *Stop:* a protected byte that moves stops the merge.
12. **The landing (G3), on Decision Log 1's terms.**
    - *Metric:* the seal's identity against G2's frozen renders; the canonical stage read on both
      tiers; clause 9's cuts regenerated on the stage; `tier-coherence.test.ts` and
      `adopted-thresholds.test.ts`; the CSS carry's Chromium proof; `check-capture-tree`.
    - *Bed:* the canonical stage under the CLAUDE.md recipe, a light and a dark generation, both
      tiers, holdout membership declared and read last.
    - *Bar:* the sealed documents re-render G2's frozen predictions byte for byte; clause 9's bars
      on the stage; Decision Log 4's carry, approximation or decline measured per leaf in
      Chromium; publication once through W40's publisher; the capture tree copied and
      `check-capture-tree` exit 0; the eye sheets over the whole canonical bed; the changeset
      (`@vitreajs/vitrea-web` minor); the release checklist with CI green at the release commit.
    - *Stop:* a rendered prediction that moves between G2's freeze and the seal stops the landing
      and returns the law to identification with a new bed. A referee failure on the stage stops
      it for Decision Log 5. `pnpm release` is the user's hand.
13. **The canonical holdout, once by artifact (G3).**
    - *Metric:* the adopted rows that read holdout, and the eye.
    - *Bed:* the canonical holdout (`holdout-configuration/configuration.py record`). It carries
      structured backdrops in both poses: hc-text on capsule and rrect-md, checkerboard and photo
      on rrect-lg, and the glass-over-glass pairs.
    - *Bar:* the adopted bounds that apply to its rows, read once per frozen configuration.
    - *Stop:* a miss is recorded and goes to Decision Log 5; it is never re-read.
14. **Every gap is recorded.** A family that fails, an endpoint left at identity, a leaf the CSS
    tier cannot carry, a level miss seen through T, a unit the dump leaves open: each with its
    numbers in §5.194–§5.197, the Deferred list or the tracker.

## Grounding Baseline (main at `9d7e171c`, W41 closed)

**The memos.** Three grounding memos, written read-only on the repository under one set of
rules (`w42-grounding-common.md`: never a holdout or recorded native pixel; prove each reader on
vitrea's own captures first; read features at their own scale; separate the surface's own light
from its transmission; keep censored channels one-sided). Each memo's fits are exploratory
readings that size an effect, never a proposed coefficient set. They are committed verbatim, with
their briefs and a SHA-256 manifest of their scratch, under
`packages/calibration/results/2026-09-29-w42-grounding/`; the raw scratch stays on the machine
under `~/vitrea-w42/grounding/`.

| memo | question | evidence read |
| --- | --- | --- |
| A, `w42-grounding-argument.txt` | the argument E3's F and g are evaluated at | canonical cal/val light-inactive checkerboard, impulse, photo (20 cells, 1x and 2x), light-active and dark cells for its question 2; W39 gradient calibration rows; G2's committed native body means for hc-text and the pitch series; both web trees |
| B, `w42-grounding-kernel.txt` | Apple's body blur: kernel, space, pose; the capture that identifies it | canonical cal/val in all four endpoints; committed uniform readings from the W39 and W34 archives; vitrea's code map and captures |
| C, `w42-grounding-probe.txt` | the probe series, the W29 dump, the smallest identifying capture | A's and B's evidence plus the canonical PROBE cells in every endpoint and scale, and the spent W34 archive's checkers |
| D, `w42-dumps.txt` | Apple's layer tree across spans, poses and schemes, no pixels | **pending memo D; folded at v2** |

**The repeat bar under the grounding.** Canonical cells are single captures (`repeatNoise` 0,
`runsPerCell` 1); one code is the resolution. The W39 and W34 seven-run bar is ≤ 0.5 code and was
not measured on the canonical cells; memo A calls the cross-sitting bar unmeasured. Family F's
bridges tie the new sitting to the canonical and probe sittings and give it a reading.

**The readings the law is built on** (all exploratory; units CSS px unless marked):

| question | reading | source |
| --- | --- | --- |
| averaging space of the level | checker black cells 186.8–188.1 against F(encoded mean 127.5) = 187.8; linear-light mean predicts 212.3. Impulse 133.0 against 132.9, linear 137.9 | A, reading 1 |
| space, all four endpoints | encoded averaging then T within about 3 codes everywhere; linear averaging misses by ≥ 12 | B §0, §3 |
| one-sidedness | native suppressed side within 2.6 codes of 0; shipped dome ratios −1.04 to −1.31; mirror S 0.2–0.5 (Apple) against ≤ 0.024 (vitrea) | A q.2; C §1 |
| W local, not group | a group mean loses by 5–10× rms on every pitch-64 cell | C §0 |
| σw | 12–13 active, 14–19 receded, identical at 1x and 2x | C §0 |
| receded W support | footprint-limited; box fits best: W34 receded capsule 0.35 rms footprint against 1.5–2.2 canvas | C §0 |
| active W support | big shapes cannot tell canvas from footprint; the capsule prefers canvas, but it is all refraction | C §0 |
| σn active | 0.8 at 1x and 0.4 at 2x on spans 32–44 at every pitch 4–64 (0.8 dev: the half-scale resampling floor); 2.0 / 4.0 / 4.5 at spans 96 / 128 / 160, both scales | C §0 |
| σn receded | 4–4.5 at spans 32–44, 5.5–9 at 96–160 (noisy); B reads 4.3 → 5.4 from span 44 to 96 | C §0; B §0 |
| active knee | lighten/darken at λ 0.88–0.91, then normal at w 0.48–0.51, both schemes and scales; a hard max (λ = 1) rejected by +0.6 to +1.2 rms; the dump's 0.9 / 0.546 costs +0.3 to +0.7 | C §0 |
| receded knee | not closed: pitch-16 knee sides flat at W need λ ≥ 0.98; pitch-64 cores want 0.6–0.8; a shared fit leaves 0.9–1.5 codes per cell | C §0 |
| space on non-binary structure | lc16 within 0–2 codes encoded, linear +3.6 to +4.2; hc-text 0.6–6 encoded against 16–48 linear | C §0 |
| chroma | takes the heavy argument only (s about 10–12), no sharp or one-sided part | A |
| gradients | native slope ratio 0.61; a canvas blur keeps the ramp (strip max 1.95–2.00 codes); a footprint-normalised blur at s = 12 reads 0.85–1.01 | A, reading 3 |
| hc-text | fits F at its own footprint encoded mean (177.6, not 128) to +0.2 / −0.1 codes | A |
| 1x fine pitches | pitches 4 and 8 at 1x pass more contrast than any Gaussian allows; points to a decimated backdrop | C §2e |
| size of the one-sided effect | memo A's reading C7 (encoded heavy + k·max(0, sharp − heavy)): worst-cell luma rms 1.3 (2x) / 3.9 (1x) on the checker, ≤ 0.6 impulse, ≤ 1.5 photo | A |

**The shipped body** (memo B's float64 replica reproduces 11 web cores at rms 0.27–0.38): the
centre is enc(R + B·((1 − k)·Ksharp∗b + k·Kdeep∗b − L̄)) on the LINEAR-light backdrop b, with
Ksharp 1.58 dev at both scales and Kdeep about 14 dev (L4, platykurtic); the tone argument is
group-level (the source mean when active, the silhouette encoded mean when receded). The CSS
tier blurs through `feGaussianBlur` in linearRGB. Neither tier has a knee (memo B §1, §6).

**The shipped documents.** macOS 27 light active / dark active / light receded / dark receded:
files `85ad7f7e3e0d` / `0eac5b294cc2` / `30fbe05986ae` / `5cec8c961201`, resolved digests
`be13dae45098fc89` / `2a4323f33df8d799` / `b0d0d8dacc6a03af` / `7c454858a3cbad5b`. The frozen
macOS 26.5 pair is `b2b570e4adcea8fb` / `874be66ea501621b`. E3's zero-gated identity-table group
(`bodyE3Strength` 0) is on main at the identity in every document (W41 Deferred at close 2).
`freeze.py verify` read 1,818 entries at drafting.

**A pointer, not evidence of record.** The uncommitted W29 G0 dump
(`/Users/new/vitrea-w29-g0-scratch/c/dump-sdk27/`, macOS 27 26A428, 2x only, nine scenes, one
receded cell) shows a `glassBackground` filter on a `CABackdropLayer` whose bounds are the
shape's box, at scale 0.5; `inputBlurRadius` 5; blur opacity graded by span when active (0, 0,
0.133, 0.267 at spans 32, 44, 80, 96) and 0.533 when receded; a radius-8 blur fill at Lighten
0.9 (light) or Darken 0.9 (dark) plus Normal 0.546; refraction, bleed and shadow zeroed when
receded (memo C §3). Memo D reads the same tree across spans, poses and schemes.

**The runtime base.** PR #2 (`perf/demand-driven-frames`, another session's, open, mergeable,
checks green at drafting) moves the root's frame loop to demand-driven frames and edits
`renderer-webgpu/src/renderer.ts`, `src/backdrop.ts`, `src/pyramid.ts` and
`src/silhouette-tone.ts`, files G2 also edits for D1 and D2. Its spec states that no material
constant, law or capture moved; the calibration page hand-steps `root.runFrame`
(`packages/calibration/web/scene.ts:866-877`), which the PR keeps exact. X37 governs.

## Design (advisory unless marked)

### The law (MARKED: its structure; G0 declares the families with their counts before any pixel of the new bed, and G2 fits on the new bed only)

Let B be the backdrop in encoded sRGB and G(σ) a Gaussian of width σ in CSS px.

- **The narrow component** C = G(σn)∗B↓, sampled from a half-scale backdrop.
- **The heavy component** W = G(σw)∗B, on the support its family declares.
- Both are averaged in **ENCODED** space.
- **They combine one-sidedly.** Light: a lighten of C with W at opacity λ, then a normal mix
  toward W at w:

      M = (1 − w)·C + (1 − w)·λ·max(0, W − C) + w·W

  Dark is the mirror, a darken with min: M = (1 − w)·C − (1 − w)·λ·max(0, C − W) + w·W.
- **The output** is y = T(M), where T is the endpoint's uniform response (X35).
- **Widths are in CSS px.** σn follows a span law per pose; σw is set per pose. G0 declares the
  span law's form and knots, and so its count, before any fit. Two forms are advisory: ordinates
  at declared knots among the calibration spans (rrect-80 is H's, so it tests the law and never
  anchors it), or the dump's opacity-graded form (memo B calls σ ≈ 10·opacity "arithmetic on 3
  points"). Whether the receded σn has a span law at all is pending memo D (below).

  > **Drafter's note (the floor is a device-pixel quantity).** Memo C reads the active narrow
  > width at spans 32–44 as 0.8 dev at both scales, the resampling floor of a half-resolution
  > backdrop, and the 1x fine-pitch aliasing as a decimated backdrop (§2e). "Widths are in CSS
  > px" holds for σn above that floor; the half-scale sampling itself is modelled in device px,
  > or 1x and 2x cannot share one law.

- **Uniform invariance by construction.** A constant backdrop maps to itself under every blur,
  every footprint normalisation and the hinge (max(0, 0) = 0), so E3's uniform closure and the
  shipped uniform bodies are untouched (memo A). Clause 6 tests it.

### T: read from uniforms, not refit (MARKED; X35)

- **Light receded:** T = E3's F on encoded luma, with its chroma gain g evaluated on W:
  y = F(L(M))·1 + g(L(W))·v(W), where L is Rec.709 encoded luma and v the encoded chroma
  vector. Memo A reads chroma as taking the heavy argument only, which is W41's smoother-g(L)
  hypothesis (§5.192 §20) in its declared form.
- **The other three endpoints:** the shipped tone solve's uniform response, evaluated at M per
  pixel rather than at the group argument. G0 names each shipped leaf the law supersedes (the
  linear pyramid's share `sizeScatter*`, `sizeHeavyTapSigma`, `collapseTransmission`'s
  group/local mix) and each shipped operator that reads a blurred backdrop (body chroma
  retention, the scatter's spatial-scale statistic), and declares where it takes its argument
  once W and M exist.
- W42 identifies spatial structure. The level misses already recorded (W36's grey middle,
  chroma) stay named. Memo C reads T as span-invariant light receded, rising with span light
  active (+2 to +6.5 codes from span 44 to 160) and clamping dark at spans ≥ 96 (dark receded
  242.4 reads 177.4 at span 44 and 117.2 at span 160).

> **Drafter's note (two T's).** "T is read from uniforms" and "T is the shipped tone solve" are
> two different functions for the three non-E3 endpoints, because the shipped solve misses the
> native uniform response (W36's grey middle and chroma). Identification should read the NATIVE
> uniform response (family A plus the committed W34/W39 deep medians, as memo C did); otherwise
> the level misses leak into σ, λ and w. The landed law then applies the shipped T, and the
> difference is the named level miss. G0 declares both roles.

### The rival families (MARKED: declared with their counts in G0, before any pixel)

Counts are per endpoint. "4 + σn(span)" is memo C's count: σn, σw, λ and w, with σn extended by
its span law.

| family | what differs | parameters | on existing cells | answered by |
| --- | --- | --- | --- | --- |
| **K1** | W on the canvas | 4 + σn(span) | active 1.1–1.6 rms, both schemes and scales; receded fails (C §4) | D, B |
| **K1b** | W limited to the layer's bounding box | 4 + σn(span) | receded cores 0.35–0.8, but λ drifts across pitch (C §4) | D, B, C |
| **K2** | two fills: the knee against Wk, the normal mix toward Wn | 5 (C §4) | receded 0.5–1.5; no gain (C §4) | C, B |
| **C-linear** | C averaged in linear light, W encoded | K1/K1b's, a discrete choice | narrow space not identified: binary backdrops cannot show it, and the photo discriminator failed its CSS control (B §3) | B (non-binary), D (intermediate steps) |
| **per-channel knee** | max/min per channel against on encoded luma | the base family's, a discrete choice | not identifiable (C U6) | E |
| **active bleed** | a third, wide component on the active endpoints | a width and a span-graded weight per active endpoint; the grading's form, and so its count, fixed in G0 | active rrect-ml/lg knee sides carry 19–36 % weight at σ 48; dump bleed radius 28–33.6, opacity 0.08–0.27 at spans ≥ 80 (C §2a, §3) | D, B', C (U7) |

Nested and null families, reported and never nominated: memo A's reading C7 is K1 at λ = 1 (the
hard max memo C rejects on the active probes). Memo B's F1 (one blur) and F2 (linear two-scale)
are rejected by the one-sided ESFs, and so is F4, vitrea's shipped form T(group) + b·(K∗B −
group), which is the baseline the referees read against.

> **Drafter's note (support rivals, U3).** Memo C's U3 names three supports: the box, the
> rounded shape and a margin. The skeleton declares canvas (K1) and box (K1b). Memo C §2a reads
> the shape footprint beside the box and the canvas on every pitch-64 cell. The drafter suggests
> declaring the shape footprint as a K1b variant so family D discriminates it rather than
> leaving it implicit.

> **Drafter's note (the receded algebra has no declared rival).** Memo C lists two open
> alternatives with no declared family: non-Gaussian W tails, and a different receded composite
> order. U1, the receded one-sided algebra, is the main thing still unidentified, and K1, K1b
> and K2 all fail it the same way on existing cells (C §2c). If none of them closes on the new
> bed, the receded identification has nothing declared to select, and Decision Log 3 applies. The
> drafter recommends G0 declare one receded-order rival before capture.

### D1 and D2 are in the law (MARKED; X36)

- **D1, device-px widths.** `renderer.ts:600-605` (`bodySigmaCssFor` = `optics.blurSigma` /
  dpr), `renderer.ts:638-644` (`heavySigmaCssFor`), `material.ts:4873-4878`
  (`heavyTapSigmaAtScale` returns device px); the light active document's lines 151–152 set
  `sizeHeavyTapSigma` 14 and `sizeHeavyTapSigma2x` 20, the light receded document's line 89
  sets 2x 14. The effect: the heavy width is 13.8 CSS at 1x but 6.9 (receded) or 10 (light
  active) at 2x, where Apple reads 12–13 and 14–19 at both scales (memo C §7). The doc comment
  at `renderer.ts:582-586` justifies device px by §5.55–§5.58 ("one kernel in device pixels at
  both scales"); the pitch series contradicts it.
- **D2, linear-light blur.** WebGPU decodes before the pyramid (`wgsl/backdrop.ts:86`); the CSS
  tier picks `linearRGB` on the premise that "the reference's body … is linear in luminance"
  (`css-tier.ts:2136-2150`, whose doc comment cites §5.71 §2 for the encoded blur reading worse
  under the shipped two-sided law). Every full-linear fit on Apple loses: 5–25 codes on checkers,
  16–48 on hc-text, 3.6–4.2 on lc16 (memo C §7). This settles the heavy and level argument; the
  narrow term's space is the C-linear rival.
- Changing them moves every document, so they land with the law and pass the same referees.
  Each is a gate-group in the identity table: at its identity the device-px and linear-light
  paths draw exactly what ships today.

> **Drafter's note ("every document").** Read as every macOS 27 document. The frozen macOS 26.5
> pair must stay at the identity and keep `b2b570e4adcea8fb` / `874be66ea501621b` (W29 Decision
> Log 1 (i); rule 2). The recorded §5.55–§5.58 and §5.71 §2 readings are not rewritten; G2
> records the reversal beside them.

### What existing cells cannot identify, and the family that answers each (MARKED)

| U (memo C §5) | what is open | family |
| --- | --- | --- |
| U1 | the receded one-sided algebra: λ drifts 0.6–1.1 and per-side kernels differ | B (the hinge reference against mean and contrast), C (which level the one-sided term hinges on) |
| U2 | the receded narrow span law: only capsule, sm and ml at p16, plus the md and lg series | B' |
| U3 | the footprint support: box, rounded shape or margin; the edge normalisation; whether the active W is footprint-limited | D, both poses |
| U4 | the heavy kernel's tails | C |
| U5 | T at 150–242 in every endpoint, and dark T at spans ≥ 96 | A |
| U6 | a per-channel against an on-luma knee, and the chroma kernel | E |
| U7 | the active bleed as a third component | D (active steps on rrect-md, span 96), B' (active P1 at pitch 64 on rrect-ml, span 128), C (S 32 on rrect-md) |

> **Drafter's note (U7).** Memo C lists U7 but its §6 table assigns it no family. The drafter
> assigned it to the active rows that sit at spans where memo C and the dump place the bleed
> (spans ≥ 80). If G0's synthetic recovery cannot separate a σ-48 component on those rows, a
> dedicated long-range family (active steps on rrect-ml and rrect-lg) is a size change for the
> user, since Decision Log 2 was ruled at about 8 h.

### The bed (MARKED: the families and their questions; exact ids and levels are G0's)

Memo C §6, pending memo D. Existing JSON kinds only (solid, two-level checkerboard, impulse as a
single patch, split, shape `position`), so the W39 side bundle captures it without a rebuild. The
canvas is 320×200, as canonical (memo B §8). The full set runs at 2x; the 1x pass is reduced,
because the widths read CSS-invariant and 1x adds the resampling floor and the aliasing. Four
passes per scale (scheme × pose); `dump-layers` on every scene.

| family | cells per 2x pass | answers |
| --- | --- | --- |
| A — uniform greys 0, 64, 128, 160, 176, 192, 208, 224, 240, 255 × {capsule, rrect-md}; 96, 160, 208, 255 × rrect-lg | 24 | U5 |
| B — two-level checkers P2 48/208, P3 96/160, P4 16/112, P5 144/240 at pitch 16 and 64 on rrect-md | 8 | U1 (hinge reference against mean and contrast); the space on non-binary structure |
| B' — P1 0/255 at pitch 8, 32, 64 on capsule and rrect-ml | 6 | U2 (the active pose is already covered by the probes); U7 on rrect-ml |
| C — single square S 8, 32 × 2 polarities on rrect-md; S 16 × 2 on capsule | 6 | U4; U1 (which level the one-sided term hinges on); U7 at S 32 |
| D — step under the interior (split) at shape offsets δ 0, 12, 32 × 2 polarities on rrect-md; δ 0, 12 on capsule | 8 | U3 in both poses; U7 when active |
| E — isoluminant chroma checkers, 2 hue pairs, pitch 16, rrect-md | 2 | U6 |
| F — bridges: canonical checker-16 rrect-md, impulse rrect-md, photo rrect-md; probe checker-64 rrect-lg | 4 | ties to the canonical and probe sittings; the cross-sitting bar |
| H — the structured holdout, declared before fitting | 8 | referee |

- **H** (memo C): P1 at pitch 24 on rrect-80 (a new span); P6 32/176 at pitch 32 on rrect-md; a
  step at δ 20; a patch S 24; P3 at pitch 64 on rrect-lg; 128/229 at pitch 64 on capsule; greys
  184 and 232 on rrect-md. Six of the eight are structured.
- **The 1x pass, 22 cells:** greys 0 / 128 / 192 / 255 × {capsule, rrect-md}; P1 at pitch 4, 8,
  16 × {capsule, rrect-lg}; F; a 4-cell subset of H that G0 declares.
- **Size** on W39's model (9.53 s per capture, 16.3 s per sentinel, 13 s per run, 25 s per pass):
  2x 4 × 66 × 7 = 1,848 and 1x 4 × 22 × 7 = 616 glass captures; about 230 no-glass references;
  48 sentinels; about 7.6 h of capture and 8 h of wall clock, in one sitting (memo C §6). The
  levers memo C names: a full 1x pass adds about 3.5 h (about 11 h); three runs would bring it to
  about 3.7 h, which Decision Log 2 declined.
- **What memo C dropped against memo B's 121-cell, 21–22 h design, and why:** B and B' 31 → 14,
  because the probes read all five shapes × five pitches in the active pose and σn is
  pitch-flat at 2x; C 34 → 6, because the pitch-64 cores and the W34 capsule already give σw
  and local against group; D 21 → 8, because local against group is settled and the support is
  what remains; A 26 → 24, with rrect-lg added because dark T clamps with span; E 6 → 2; the full
  1x pass, because the widths are CSS-invariant; H 16 → 8.

### Pending memo D; folded at v2

Memo D reads Apple's layer tree through the harness's `dump-layers` mode across every canonical
component and span, both schemes and both poses, at 2x and at 1x if the harness supports it
without a rebuild (`w42-dump-brief.md`). Its numbers are pointers; they become evidence only where
the pixels agree (X38). Three points in this charter wait on it.

1. **Is the receded narrow width flat across span?** *Pending memo D; folded at v2.* The one
   receded dump reads blur opacity 0.533 with its distances zeroed; the pixels read the receded
   σn growing with span (memo C: 4–4.5 at spans 32–44, 5.5–9 at 96–160, noisy; memo B: 4.3 → 5.4
   from span 44 to 96).
   - *If the receded opacity is flat at every span:* the receded σn is one parameter per endpoint
     rather than a span law, and the growth the pixels show is attributed elsewhere (the box
     footprint's normalisation, or U1's algebra). B' then tests the flatness rather than
     identifying a law, and memo C expects the receded span axis could shrink.
   - *If it is graded by span:* the receded σn carries a span law as the active one does. B'
     keeps its capsule and rrect-ml rows beside the probes' rrect-md and rrect-lg series, and H's
     rrect-80 becomes the span law's held-out test in both poses.
2. **What are the units of `BlurRadius` and the BlurFill radius: points or pixels?** *Pending memo
   D; folded at v2.* The dump reads `inputBlurRadius` 5 and a BlurFill radius 8 against a
   measured σw of 12–19; memo C calls the radius-to-sigma mapping unknown.
   - *If points (CSS px):* the dump corroborates D1's fix and the pixels' scale invariance; the
     reduced 1x pass stands.
   - *If pixels (device px):* the declared radii halve in CSS at 2x, against pixels that read σw
     and the rrect-md σn identical at both scales. The pixels govern, but the radius-to-width
     mapping is then scale-dependent, so the 1x pass should be FULL (memo C: about 11 h) to
     identify the widths at 1x rather than infer them from 2x. That is a size change for the user
     (Decision Log 2 was ruled at about 8 h); the law still carries CSS-px widths as the
     effective description, with the mechanism recorded beside it.
3. **Do the 1x and 2x trees agree?** *Pending memo D; folded at v2.* The W29 dump is 2x only.
   - *If they agree* (the same radii, opacities, blend modes and a backdrop scale of 0.5): 1x
     differs from 2x only by the half-scale resampling floor and its aliasing (memo C §2e), the
     law carries no per-scale parameter beyond the device-px sampling, and the 1x pass stays at
     22 cells.
   - *If they disagree* (another backdrop scale, or radii that scale): the law declares
     per-scale widths or sampling, the 1x pass becomes full, and the hours go back to the user.

Memo D may also read the active opacity at more spans, the bleed and `MaxLuma` per span, and the
decoded `backdropRect` (memo C §3). Those are folded as pointers where they land.

### The split and the holdouts (MARKED)

- **H** is the new bed's structured holdout, declared and hashed in G0 before capture, enforced
  by the wave reader and launcher, its payload behind the procedural boundary until G2's one
  receipt. G0 also declares a validation set of transfer axes (a span or pitch per family that
  calibration does not contain), so that validation tests the span law and the pitch-flatness
  rather than repeat noise. Whether an H cell is web-plannable (an offset step may not be) is
  declared in G0; a cell that is not referees the numerical candidate only (W41 clause 2).
- **The canonical holdout** stays sealed until G3 and is read there once, by artifact.
- **The canonical probe cells were READ in grounding** (memo C), as were the W34 archive's
  checkers. They are calibration evidence and not a referee from now on (X34).

### Repeats, the bar and the archive of record

Seven runs (Decision Log 2, RULED). The bar is W39's (clause 4). The archive is W39's pattern:
complete and role-separated, lossless crops in original coordinates with every dependency an
estimator reads, the per-run statistics with populations and input hashes, the state
membership, a SHA-256-pinned inventory, replay proved identical with the raw root denied; a
`.tar.zst` under 2 GiB published as a GitHub release asset named by its SHA-256, a reader that
fetches by that name into a cache outside the repository and verifies the digest before use,
and a second owner-controlled copy. **The sitting's operational logs go into the archive, not
into git** (the tracker's W41 G1 entry: about 84 MB packed of logs went into git). A thin
projection is a convenience, never the record.

### The instrument (G0)

- The readers, proved first (clause 2): memo C's model reader (C and W on canvas, box and shape
  supports, the knee, T), the mirror statistic S, the pitch-64 heavy reader, the ESF and impulse
  readers (memo B), the step reader for D and the patch reader for C.
- The wave reader and launcher enforcing the split; the sitting script derived from W39's with
  its roots pointed at the W42 bed and the side bundle.
- The one-exposure runner, reusing W41's X26 machinery
  (`results/2026-09-27-w41-g0-declaration/exposure/runner.py`), binding numerical and rendered
  candidates on one receipt.
- The landing-referee gate's tooling: W41 G2's referee ports in `--stage` mode and the standing
  eye-sheet script extended to the six strata.

### The landing-referee gate (MARKED; X33)

Clause 9 in full. Its bed is the canonical calibration/validation renders the adopted rows
already read; its bars are the adopted rows as they stand; its order is before the freeze and
the receipt. Nothing about H is read, predicted or opened until the gate has passed.

### The CSS carry (advisory; Decision Log 4)

`backdrop-filter: blur()` already blurs ENCODED values, and `backdrop-filter` reads only the
element's box, which is the box footprint for free (Chromium's edge mode is unmeasured). The
one-sided term maps to a sharp sibling layer with `mix-blend-mode: lighten` (dark: `darken`) at
opacity over the heavy layer, which computes heavy + k·max(0, sharp − heavy) per channel and
commutes with a monotone affine F (memo A). Blend modes on `backdrop-filter` layers are unmeasured
per engine, which is why G3 needs a Chromium proof. E3's F and g take W41's affine route
(`w41-g2-css-candidate` `78c4b854`), re-derived against the law as W41 Deferred at close 5 lists.

### The runtime base (MARKED; X37)

G2 branches from main as it stands when G2 starts, after PR #2 if it has merged. Before any
candidate render, G2 re-renders a declared sample of the canonical bed with the SHIPPED documents
at that base and shows it byte-identical to the canonical capture tree, so every rendered
difference is attributable to the candidate and not to the base. W42 never merges or publishes
PR #2.

## Children

### G0: Declaration and instrument (ledger §5.194)

Branch `w42-g0-declaration`; evidence `packages/calibration/results/<date>-w42-g0-declaration/`.
- The families and bounds of Design, hashed before any native pixel of the new bed exists.
- The reader, proved on synthetic renders of the declared algebra and on vitrea's own existing
  captures (clause 2).
- The capture bed: memo C §6 refined by memo D, with families A, B, B', C, D, E, F and the
  structured holdout H declared before capture, as a wave-local scenes file with its own fixture
  root; the canonical `scenes.json` untouched. Every kind the bed uses is checked against the
  side bundle's pinned build (`backgrounds` / `self-check`, no capture) before it is declared.
- The one-exposure runner, reusing W41's X26 machinery.
- The pre-exposure landing-referee gate's tooling (clause 9).
- The runtime-base sample (clause 7) and the eye sheets' stratum membership declared.
- No native capture. Independent review before merge; the freeze reads 1,818.

### G1: The native sitting (ledger §5.195)

Branch `w42-g1-sitting`. Starts only after G0 has merged and the parent has told the user the
tooling is ready (Decision Log 6, RULED).
- **The side bundle** is the existing W39 one, `dev.vitrea.reference-apple.w39` at
  `~/vitrea-w39/side/` (binary 02052b17…, cdhash be258cbf…), which can capture the inactive pose,
  used with no rebuild. It was retired at W39's close with no TCC row (W39 Decision Log 4).
- **The grant, by the user's hand.** One Screen Recording grant holds at a time on this machine
  (W34 Decision Log 4; W39 Decision Log 4). The user adds the side bundle under Screen & System
  Audio Recording and lifts X5 for the W42 bed; the parent reads the grant back from the system
  TCC database and runs the side's positive pose checks. The original bundle is not launched
  while it has no row. After the sitting the user re-adds the original bundle alone and restores
  X5; the original's positive check must capture a canonical cell byte-identical to its committed
  fixture, as at W39's close. Failure to restore is an open blocker, not a closed sitting.
- **The passes:** 1x and 2x × light and dark × active and inactive, seven runs each, sentinels
  after, `dump-layers` on every scene, every capture attested (clause 3), quarantines named.
- **About 8 h at seven runs**, in one sitting while the user leaves the Mac idle.
- **The archive** produced, pinned and published as a release asset by SHA-256 with the ledger
  citation; the bar published from the archive before plurality; replay proved with the raw root
  denied; the operational logs inside the archive, not in git. Nothing is read against vitrea.

### G2: Identification, the gate and the one exposure (ledger §5.196)

Branch `w42-g2-identification`, cut from main as it stands when G2 starts (X37). In order:
1. The runtime-base proof (clause 7).
2. The fit on the new bed's calibration set only, family by family; transfer to validation;
   survival per clause 5.
3. The survivors implemented behind zero identity gates on both tiers' code paths, D1 and D2
   included (X36); goldens byte-identical at identity.
4. The rendered candidate on the new bed's web-plannable calibration/validation cells (clause 8)
   and uniform invariance (clause 6).
5. The canonical calibration/validation bed rendered with the candidate in a scratch stage; L1,
   M1, M2, C1, X1 and E2 run on those renders; eye sheets by stratum: uniform, binary structure,
   text, impulse, photo, gradient (clause 9).
6. **Only if all of those pass:** the freeze of the numerical and blind rendered H predictions by
   artifact, then the ONE exposure on H (clause 10). This is the lesson of W41, which spent a
   holdout on a law that later failed landing.
7. Decision Log 3 if the receded endpoints fail.

### G3: Seal and land (ledger §5.197)

Branch `w42-g3-landing`. Conditional on clause 10 passing (Decision Log 1).
- Seal the documents; prove identity against G2's frozen renders.
- The canonical stage read, both tiers. The CSS carry uses encoded `blur()` layers and
  `mix-blend-mode` lighten/darken at opacity, and needs a Chromium proof (Decision Log 4);
  `tier-coherence.test.ts` pins whatever is carried or declined.
- The canonical holdout once, by artifact (clause 13). Decision Log 5.
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
- **The four X6 facts** before every browser run and on every native capture (clause 3), with
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
- **X33 — the landing referees before the exposure.** Clause 9: L1, M1, M2, C1, X1 and E2 on the
  candidate's canonical non-holdout renders, and the eye sheets by stratum, pass before H is
  predicted, frozen or opened.
- **X34 — the probe cells are calibration evidence.** The canonical probe cells memo C read (the
  checker pitch series, lc16, hc-text, hc-text-7 and hc-text-28, in every endpoint and scale)
  and the W34 archive's checkers were read in grounding. From now on they cannot serve as
  held-out evidence for any W42 law, and they are no G2 fit input, which is the new bed's
  calibration set alone. The adopted rows that already include probe rows (X1, E2) keep their
  populations as regression stops.
- **X35 — T is read, never refit.** Identification reads the native uniform response; the landed
  law applies E3's F (light receded) or the shipped tone solve (the other three); a departure
  between them is a named level miss, never absorbed into a spatial parameter.
- **X36 — D1 and D2 land inside the law.** Each is a gate-group in the identity table; at the
  identity it draws exactly what ships today; the frozen macOS 26.5 pair never leaves it.
- **X37 — the runtime base is proved before any candidate render** (clause 7); W42 never merges
  or publishes PR #2.
- **X38 — dump numbers are pointers.** A layer-tree number becomes evidence only where the
  pixels agree; the pixels govern.

## Ordering & Dependency Map

Decision Logs 1, 2 and 6 RULED (2026-09-29) → memo D lands → v2 (memo D folded; adversarial
review) → G0 (declaration hashed; instrument proved; bed, split and gate tooling; review; merge)
→ the parent tells the user (Decision Log 6) → G1 (the user's grant switch and X5 lift; passes;
archive; bar; the user restores both) → G2 (base proof → calibration fit → validation transfer →
gated operators on both tiers → rendered candidate → canonical renders → **the gate** → freeze →
ONE exposure on H; Decision Log 3 if needed) → G3 (seal → identity → Decision Log 4 → stage read,
both tiers → canonical holdout once → Decision Log 5 → publish → capture tree → eye sheets →
changeset → release checklist → the user's `pnpm release`) → close.

## Risks & Mitigations

- **The receded algebra does not close (U1).** It did not on existing cells, and every declared
  variant failed the same way (memo C §2c). Mitigation: Decision Log 3, declared now; the
  receded documents stay at identity and E3 stays unshipped; the negative is recorded at its
  resolution.
- **The gate cannot pass on M2 or L1 growth by construction** (the drafter's notes at clause 9).
  Mitigation: the parent decides whether Decision Log 5's M2 and L1 readings are ruled before
  G2's gate.
- **A wrong mixing space manufactures a knee.** Memo C's encoded fit on vitrea's linear captures
  returned λ 1.4–1.5. Mitigation: the knee is established by S and by every linear fit's loss
  (clause 2), and the synthetic controls run in both spaces.
- **Dump numbers mislead.** The dump's w of 0.546 reads 0.48–0.51 in the pixels, and its fill
  radius of 8 has no known mapping to σw of 12–19 (memo C §3). Mitigation: X38.
- **D1 and D2 reverse recorded readings** (§5.55–§5.58; §5.71 §2). Mitigation: recorded beside,
  never rewritten; the identity gate keeps the old path exact for the frozen 26.5 material.
- **The heavy chain costs frames.** An encoded separable blur at σ 12–19 CSS px adds passes
  beside PR #2's demand-driven loop. Mitigation: G3 reads the renderer bench beside the goldens
  and records the cost; a regression is a finding for the parent, not a silent trade.
- **The machine is shared.** Foreign browsers and another session's Playwright refused W41's
  reads (§5.192 §1, §5.193 §3). Mitigation: X6 before every launch; the sitting runs only when
  the user leaves the Mac idle (Decision Log 6).
- **Some H cells cannot be posed on the web.** Mitigation: G0 declares which; those referee the
  numerical candidate only.
- **The canonical holdout fails after H passed**, as W41's canonical referees failed after the
  W39 holdout passed. Mitigation: clause 9 puts every referee readable without a holdout first;
  the canonical holdout's miss goes to Decision Log 5.
- **The 1x pass is too thin** if memo D shows device-px radii or disagreeing trees. Mitigation:
  the full 1x pass (about 11 h, memo C) goes back to the user before G0's merge.

## Deferred / Out of Scope

- **Refitting T.** The level misses (W36's grey middle, chroma) and F above 150 stay named; family
  A reads T on 150–242 for the reader, not to refit it (X35).
- **The edge.** Rims and edge bands, the lens band, the bright inner line (W35), the top/bottom
  obstruction (W37), the stroke and Apple's dark exterior contour (W41 Deferred at close 3–4),
  and distance-to-edge grading (memo B §8).
- **Tint, the clear material, glass-over-glass, accessibility, the recede transition in time,
  spans above 160, non-sRGB content** (memo B §8; memo C §6).
- **The private filter's semantics** beyond its effective transfer.
- **The narrow term's averaging space**, if families B and D cannot separate C-linear from
  encoded at the bed's resolution: recorded as unidentified, with the capture that would.
- **A full 1x pass**, unless memo D requires it.

## Tracking Map

| child | status |
| --- | --- |
| G0 | — |
| G1 | — (after G0's merge and the parent's word to the user) |
| G2 | — |
| G3 | conditional on clause 10 (Decision Log 1) |

## Decision Log

### Decision Log 1 — land in this wave (before G0; the user's)

The parent recommended yes, on W41 Decision Log 1's terms: a survivor at one code on
calibration, validation and H, past every landing referee, is exactly the shipping criterion.

**RULED 2026-09-29 by the user: "Land in this wave, if every referee passes".** G3 is in scope,
conditional on clause 9's gate, clause 10's exposure and clauses 12–13's referees all passing.

### Decision Log 2 — the repeat count (before G0's merge; the user's)

Put to the user: seven runs as W39 ruled, about 8 h; or three, about 3.7 h (memo C §6). The parent
recommended seven: the bar must be measured, and three runs cannot show a 0.5-code floor.

**RULED 2026-09-29 by the user: "7 repeats (about 8 h)".** G1 runs seven. A size change from
memo D (a full 1x pass) comes back to the user.

### Decision Log 3 — partial-endpoint adoption if the receded endpoints fail (at charter, by rule; the parent's)

**Ruled at charter.** If the receded endpoints do not survive calibration and validation, the
active endpoints may land alone. That is a partial-endpoint adoption with a claim scope, as W41's
Decision Log 7 allowed: the receded documents hold every W42 gate at its identity, so no receded
document's rendering or digest moves, and E3 stays unshipped; the runner scores the complete
membership; closure is tested on the claimed strata's H cells; unclaimed strata are reported
"not claimed (identity)" with their scores; at identity the render reads byte-identical to the
baseline, and that equality is a test.

> **Drafter's note.** The ruling names the receded failure only. W41 Decision Log 7's general
> rule would also admit the receded endpoints alone if the active ones fail. G3 would then be a
> receded-only reseal, which makes M2's active-hash reference lookup ambiguous (the tracker's
> "M2's chroma reference is loaded by its active hash alone" entry; the fix is the
> chroma-reference half of W41 G2's drafted patch). The parent may want to rule that case now.

### Decision Log 4 — the CSS tier's carry, approximation or decline, per leaf (in G3; the parent's, on the Chromium measurement)

Open. Advisory route in Design.

### Decision Log 5 — bounds and floors if the law lands (in G3; the user's)

Open. See the drafter's notes at clause 9 on whether its M2 and L1 readings are needed before
G2's gate.

### Decision Log 6 — the grant switch and the sitting's timing (the user's hand)

**RULED 2026-09-29 by the user: "When the tooling is ready, tell me first; I'll switch the
permission and leave the Mac idle".** G1 starts only after G0 has merged and the parent has told
the user. The user switches the Screen Recording grant and lifts X5 by their own hand, and
restores both after the sitting.

## Surprises & Discoveries

- **E3's failure is one instance of a gap across the whole material** (memo A, question 2): in
  every endpoint the shipped body draws the half-wave Apple removes, and its two-sided heavy part
  is too weak in the dark scheme and at light 2x.
- **Apple's widths hold in CSS px; vitrea's are device px** (memo C §7), against the reading that
  justified device px (§5.55–§5.58).
- **The receded pose widens the narrow component** (memo B §0); memo C reads the heavy one wider
  too (12–13 active, 14–19 receded) and limited to the box footprint.
- **A half-resolution backdrop shows in the pixels**: the 0.8-dev narrow floor at both scales
  and one-sided blobs at the checker period at 1x (memo C §2e), matching the dump's backdrop scale
  of 0.5.
- **hc-text fits the encoded-mean pointer** at its own footprint mean, 177.6 rather than 128
  (memo A). Memo A could reproduce W41's "hc-text does not fit" only by taking the mean from the
  bar geometry or as 128, and says so as an inference: G2's working is not in the record.
- **The pre-W41 group-level solve matched Apple's 188 on the checkerboard for a reason that is
  not Apple's mechanism.** W is a local encoded blur (memo C §0), and on a centred periodic
  pattern the local mean equals the group mean (memo B §5).

## Revision Notes

- 2026-09-29 (Decision Logs 1, 2 and 6, the user, relayed by the coordinator): land in this wave
  if every referee passes; seven repeats (about 8 h); the grant switched and the Mac left idle by
  the user's hand once the parent reports the tooling ready.
- 2026-09-29 (v1, drafted for the parent): chartered from the parent's decision skeleton and
  grounding memos A (argument), B (kernel) and C (probe), committed with their briefs and a
  scratch manifest under `packages/calibration/results/2026-09-29-w42-grounding/`. Memo D (the
  layer dump) is running; its three points are marked and folded at v2. Drafter's notes beside
  clause 9 (M2, L1 growth, the eye's strata), the law (the device-px floor), T (two roles), the
  rivals (U3 supports, the receded order), D1/D2 (every document), U7 and Decision Log 3.
  Adversarial review requested before G0.
