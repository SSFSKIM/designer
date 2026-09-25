# W39 — the colour-and-edge capture: one native sitting that identifies Apple's colour response and the edge line's directional law (2026-09-26)

**Status: G0 MERGED `ba38ebbf` (2026-09-26, §5.184); G1 (the sitting) is next and needs the user's grant switch; the TCC-refusal rehearsal is G1's first step because the machine was not exclusive during G0.**
Chartered by the parent on the user's "W39 colour-and-edge capture (Recommended)" after W38's
close (main `e3ec337e`, 0.24.0 published), under the standing "rest on your judgement" and the
routing the user set on 2026-09-22 (X9). This is the wave W37's Deferred at close 1 and W38's
Deferred at close 1 both named: the native experiment that supplies what the W34 archive cannot —
uncensored colour at matched luminance, matched top/bottom controls at several depths, a
subpixel-phase mechanism proved reachable first, a second calibration span under a fresh split
and a larger circular radius — under the user's X5 / TCC authority. Grounded by two read-only
memos (2026-09-26; the colour bed from the W34 archive through the guarded reader, 88
calibration and 16 validation cells, no holdout; the edge controls, the phase mechanism, the
harness, the sitting budget, the grant sequence and the archive's weight).

## Purpose

vitrea's macOS 27 material misses Apple's on colour and at the edge, and both misses are now
known to be COUPLED-COLOUR questions that the archive cannot answer:

- **The body.** W36 closed black and named the grey middle and chroma as misses (§5.179–§5.180).
  The archive's six chromatic solids are 192/32 mixes whose native outputs clip on their strong
  channel (light red 255/133/133, magenta 255/127/255, blue 143/143/255; dark blue 58/58/255),
  so no full-RGB inversion exists. What the archive DOES say, on unclipped channels alone, is that
  Apple's body is not a per-channel tone curve: the same input value 32 reads **148** on grey-32,
  **133** on red, **143** on blue, **96** on green, **81** on yellow and **127** on magenta in the
  light active pose, at both scales; red and blue share G = 32 and read **10 codes** apart (8 on
  dark active). And the shipped model misses on unclipped channels too: dark active red reads
  native **242/50/50** against vitrea's **160/90/90** (W35's calibration reading; W36–W38 shipped
  no colour change). So the question is not "is there a per-channel curve" — there is not — but
  WHICH coupled law predicts unseen mixtures at matched luminance, and whether the interior law
  extends to the edge without a separate chromatic boundary term.
- **The edge.** W35 read Apple's active one-CSS-px inner line as bright at vertical normals and
  faint at horizontal, lifting the body's own saturated channels; W37 identified five families on
  the archive, none closer than 8.13 codes, and found a coefficient-independent obstruction —
  Apple's TOP edge reads **250** where its BOTTOM reads **253** at matched inward depth on light
  grey-255 (1x 5.5 CSS px; 2x 5.75/5.25), 156 / 312 pixels a side, seven byte-stable repeats,
  persisting 7–14 CSS px inward — so no even-normal law, vitrea's rim included, can close. W38
  showed the cheap re-aim fails a per-bin veto by up to 47 codes on saturated colours because the
  rim is colour-blind. The next step needs a SIGNED-normal term declared first, and a bed that
  can attribute it (shape-local, window-relative or backdrop-driven) and condition it on colour.

This wave captures one native bed that serves both questions from the same pixels, and then
identifies. Its purpose, in order:

1. **A bed declared before it is captured** that (a) varies channel mixtures at matched
   luminance inside a region where Apple's output is predicted to stay unclipped, with held-out
   colours predicted once after the freeze; (b) places the same shape at three window heights
   on two uniform greys, flips a vertical gradient, and puts two independent shapes in one
   window, each with an opaque control and a no-glass reference; (c) adds a second calibration
   span at held corner radius and a circular radius ladder; (d) proves a subpixel-phase mechanism
   reachable in a preflight before any phase cell is admitted; (e) repeats seven times and
   publishes the bar before any threshold.
2. **Identification on that bed**, split declared first: a body colour law that closes at
   max(1 code, bar) on every channel of every held-out colour in all eight strata, and a
   signed-normal, colour-conditioned edge law that closes on the wave's own holdout — or the
   negative at its resolution, including "insufficient resolution" between surviving laws.
3. **Only if a law closes, the leaf(s)**: through the identity table, WebGPU tier first, CSS
   derived or declined by measurement, W38's per-bin veto FIRST and its E2/R1 rows as the edge
   acceptance, sealed, the canonical holdout read once (four records remain), landed as a
   `@vitreajs/vitrea-web` minor. Otherwise the wave closes at the finding.

The purpose is the colour law and the directional edge law identified or their
unidentifiability sharpened to a stated resolution, the frozen bed and the shipped macOS 27 bed
untouched until a law closes, the archive of record complete and fetchable by the name the
ledger records, and every gap written down.

## Parent-Level Acceptance

1. **The bed is declared before it is captured.** The wave-local scenes file
   (`apps/reference-apple/scenes-w39-colour-edge.json`), the split (`split.json`, whole
   glass/control pairs kept together), the repeat count, the statistics, the forward families
   with their parameter counts and working spaces, the closure rules, the preflight's pass rule
   and BOTH of its branches, and the stop conditions are committed, hashed and independently
   reviewed in G0 before any pixel is captured into evidence. The split is never re-cut; the six
   held-out colours and the wave's holdout are read once, by artifact; W34's holdout is spent and
   never read.
2. **The colour bed lives inside the admissible box, and a clipped channel is censored, never
   inverted.** Every colour cell's sRGB is inside [40, 150] on every channel (the memo's
   first-order prediction that native output stays inside [8, 247] on both schemes and poses;
   NOT a guarantee). A native output ≥ 250 or ≤ 5 on any channel censors that channel; a censored
   channel excludes the cell from full-RGB inversion and remains a scalar bound; no colour is
   replaced or re-chosen after a rail hit, and a censored held-out cell is UNMEASURED, not a pass.
3. **The archive already excludes two hypotheses, and the bed does not spend captures to
   rediscover that.** G0 commits the archive reading (H1, the per-channel curve, rejected on
   unclipped calibration channels at ≥ 52 codes; the shipped H2 rejected as a body predictor at
   82 codes on unclipped dark red) as evidence beside the declaration. The bed carries the W34
   red, green and grey-128 circular cells as BRIDGE cells that lay the new bar beside the old
   readings and serve as saturated anchors with their clipped channels censored.
4. **The preflight precedes the bed, tests ONE actuator, and both branches are declared for
   that actuator.** The sitting opens with a paired opaque/glass preflight of the phase mechanism
   — fractional SIZE on a 120×44 rounded rectangle of radius 22 with the near edge pinned by the
   new `position` field (position = pinned edge + size/2), four requested DEVICE-pixel phases 0,
   ¼, ½, ¾ divided by the scale, in x (width) and separately in y (height), at 1x and 2x — plus an
   INTEGER-size control per axis (width 121 / height 45 CSS px at device phase 0) that bounds
   what a whole-pixel size change does to the material: 9 geometries × opaque/glass × 2 scales =
   **36 captures**, light active. An axis is reachable when, at both scales: (i) the opaque
   control's FAR edge row shows ≥ 3 distinct coverage states across the four phases while its
   pinned NEAR edge row is byte-identical across them; (ii) the glass cell's near-edge profile
   (W37's shells, both sides of the edge) is within the bar across the four phases, so the
   material's response did not change with the size; (iii) the glass cell's far-edge profile
   shows ≥ 3 distinct states whose differences exceed the integer-size control's far-edge
   difference and are consistent with a subpixel shift of one ramp (W37's area-integrated model)
   rather than an amplitude change. Three distinct glass RGB responses alone do not pass — they
   can come from the size law. Only a reachable axis's phase cells, defined on exactly this
   actuator, enter the bed; an unreachable axis's cells are omitted verbatim; no phase is
   inferred from backdrop motion (Decision Log 3, by rule). No second actuator is built or run in
   this sitting: the window-origin, odd-canvas and transform candidates are Deferred, because an
   actuator that passed a preflight but has no declared seven-run bed would admit nothing, and
   one that has a bed the preflight did not test would admit the wrong thing.
5. **Every run is attested as W34's were, and a run that fails to attest is quarantined.** macOS
   27.0 build 26A428; `NSGlassTintAmount` 0.5; Reduce Transparency and Increase Contrast 0; Show
   Borders 0; display mode read before and after; the side bundle's cdhash and `LC_BUILD_VERSION`;
   the display's colour context beside the capture's sRGB setting; opening and closing reads that
   agree; per cell `deterministic`, the pose as the harness attests it, and NOW the requested and
   actual window frame in screen coordinates and the shape's attested `frameOrigin`. The sitting
   script derives from `run-sitting-w34.sh` / `sitting.py` with roots pointed at the W39 side
   bundle and the version gate kept.
6. **Repeats before thresholds, reproducible from the archive of record.** Seven runs per pass
   (state discovery: 72.1 % of seeing a one-in-six minority state); the per-bin, per-channel
   run-to-run spread published in G1 before G2 opens, computed from all admitted runs before
   plurality with the losing states preserved, from a complete role-separated repeat archive
   (lossless crops in original coordinates with every sampled dependency) that replays the
   instrument without the raw PNGs. Where the archive lives is Decision Log 1; wherever it lives,
   the ledger cites it by SHA-256 and byte size and a reader fetches and verifies it by that name.
   No closure threshold before the bar; "one code" is the encoding's resolution.
7. **The instrument reads what the bed was built to separate, and says what each control
   proves.** Matched top/bottom at equal inward depth are READINGS from one glass PNG (W37's
   reader extended to 14 CSS px inward, to attested positions and to the new paths), never extra
   cells; arcs and straights stay separate strata; the opaque control measures rasteriser
   alignment and coverage on the ordinary fill path and is NOT assumed to transfer to the glass
   path; the no-glass reference is captured through ScreenCaptureKit like the glass cells. A
   symmetric axis-aligned shape cannot distinguish a path-local top-lit coefficient from a
   screen-up vector by translation, gradient flip or a vertical pair: any surviving law is
   recorded as an EFFECTIVE signed-normal response, not as Apple's lighting source identified.
8. **Identification precedes fitting and the split precedes identification; a bin mean is not
   a closure.** G2 fits on calibration, checks validation as read-only transfer, freezes every
   parameter, endpoint and forward output by artifact, THEN opens the six held-out colours and
   the wave's holdout once on a receipt. The closure test is the absolute per-channel residual
   per cell (deep body) and per shell/bin (edge) against max(1 code, bar) with a declared
   minimum population; least-squares and minimax both reported; worst-channel and all-channel
   failures both reported; every repeat state scored against the frozen prediction beside the
   median. **A law SURVIVES only if it meets max(1 code, bar) on every required channel of every
   calibration AND validation cell (body) and bin (edge) BEFORE the freeze**; a law that fails
   there is recorded as failed and is not carried to the held-out read, and no candidate is
   changed after any exposure. A survivor then CLOSES only if it also meets the same bound on
   the six held-out colours in all eight strata and on the wave's holdout. Survivors that differ
   by less than max(3 codes, the sum of their bars) at every admitted discriminator are
   "insufficient resolution", a finding, not a reason to fit more — two laws that both pass a
   one-code test differ by at most two codes on those observations, so this outcome is expected
   whenever the bed cannot tell them apart, and it never widens a tolerance.
9. **Nothing shipped moves until a law closes.** In G0–G2 no byte changes under `scenes.json`,
   `fixtures/`, `results/matrix.json`, the six material documents, the goldens or any adopted
   threshold; every W39 cell carries the single role `probe`; the wave's rows go to its own
   matrix under `fixtureSet: "probe"`; the freeze reads 1,818 at every merge.
10. **If a leaf lands, the edge acceptance is W38's shape and the colour acceptance is clause
    8's whole chain.** Per-channel-bin veto at one code FIRST against the shipped treatment on
    the calibration archive, then stratum max/mean ≤ +0.5 and sides within 2 codes; E2's 212-row
    rendered-edge regression row with its three estimators frozen against the pre-W39 capture
    before any W39 scoring; R1 for the fixture-less paths; the body law closing on calibration,
    validation AND the held-out colours in all eight strata (clause 8), and the RENDERED body
    re-read against the same cells on the WebGPU tier; M1/M2/C1/X1/L1 re-read; the canonical
    holdout once; the eye beside the metrics.

## Grounding Baseline (main at `e3ec337e`, W38 closed)

- **The archive's colour map, on unclipped channels.** Deep-body medians (W35's d ≤ −6 CSS px
  statistic, seven-run median, 0.5-code bar on all 104 admitted cells, 1x and 2x identical):
  light active black→white 132→253, inactive 133→240; dark active 32→184, inactive 20→180.
  Input 32 in the light active pose reads 148 grey / 133 red / 143 blue / 96 green / 81 yellow /
  127 magenta (all calibration, all unclipped). Dark active green carries a linear luma EXCESS of
  +0.0648 over the neutral interpolant at its input luminance (light green +0.0292), so a
  luminance-only law also misses on what exists. Full tables in the colour memo; grey-208 is
  W34 identification-holdout and was not read.
- **The admissible region (predicted).** Per-stratum grey interpolant plus the six solids' signed
  departure envelope (light active [−67, +30.5]; dark active [−51, +92.9]) gives a per-channel
  input box of [0, 170] light and [36, 167] dark; the bed narrows to [40, 150] (linear Y
  0.0212–0.3050). OKLab chroma ceilings inside the rounded box are about 0.034 at Y 0.05,
  0.064 at 0.11 and 0.054 at 0.18; the factorial uses 0.012 and 0.024, the matched-channel
  pairs reach 0.029–0.055.
- **The harness today.** One global `canvas`; a single shape centred with an optional Double
  `offset` (W34 measured that `.offset` snaps to two states); `capsule`, `capsule-circular`,
  `rrect` with radius, `opaque` + `fillSRGB` on single shapes, `none`, `group` (one container),
  `stack` (two surfaces, upper offsettable, base fixed); backgrounds `solid`, `linear-gradient`
  (90° and 270° flip vertical order), `split`, `checkerboard`, `impulse`, `synthetic-photo`,
  `text-rows`, generated at canvas × scale and refused if stale. One GUI process captures both
  schemes per scale/pose pass. `build.sh` refuses the protected output and requires
  `VITREA_BUILD_OUT` + `VITREA_BUNDLE_ID` for a side bundle.
- **W34's sitting rate.** 4,192 captures in 40,339 s of capture wall (9.62 s per capture;
  normal passes 9.54 s including launch and attestation; sentinels 16.5 s). 28 normal launches
  at ≈ 6.4 s overhead each.
- **The grant.** One Screen Recording grant at a time on this machine (W34 DL4, executed):
  side granted → original refused; original re-added → side refused; distinct identifiers and
  cdhashes; mechanism not inferred. The original bundle holds the grant now. `~/vitrea-w34/side/`
  is ungranted.
- **The weight.** Pack 462.44 MiB; the eight largest blobs are `results/matrix.json` revisions
  63.0–76.6 MB; W34's archive 146 MB in the tree (`repeat/` 115, `probe/` 17, `bar.json` 7.2). A
  W39 archive at this bed's size and the taller canvas is estimated at 200–350 MB.
- **The acceptance tools that exist.** `results/2026-09-25-w38-g0-rim-axis-cut/model.py`
  (old/candidate predictions and strata), `test-veto.py` and
  `packages/calibration/test/w38-veto.test.ts` (the per-bin veto), `e2.py` and
  `w38-e2.test.ts` (212 rows, three estimators; proposed, not adopted); W37's `canonical.py`
  (G0b, repaired: per-side rows, population ≥ 4, explicit UNMEASURED; centred shapes, shells
  −6..−1 device px only).

## Design (advisory unless marked)

### The bed (MARKED: the cell classes and pairings; exact ids and colours are G0's declaration)

One canvas for the wave, **320 × 280 CSS px**, so a 120×44 shape at centre y 70 / 140 / 210 keeps
48 CSS px of exterior above and below at the extremes; colour cells sit at the centre. Backgrounds
are regenerated at that canvas and both scales. Every id below exists in both schemes, both poses
and both scales.

- **Colour cells, 61 + 2 bridge, all on `capsule-circular` 120×44 at centre.** 36 factorial
  (Y ∈ {0.05, 0.11, 0.18} × hue ∈ {0°, 60°, …, 300°} × OKLab C ∈ {0.012, 0.024}, solved to exact
  8-bit sRGB and reported at their actual Y and C); 7 neutral knots (40, 56, 72, 88, 104, 128,
  150); 6 matched-channel pairs ([90,70,100] / [90,100,70]; G-fixed and B-fixed likewise);
  6 validation colours at interstitial hues (read-only transfer, never fitted); 6 held-out
  colours at unseen Y 0.08 and 0.145 (predicted once after the freeze). Roles: 49 calibration,
  6 validation, 6 held-out. Plus W34's `red` (192/32/32) and `green` (32/192/32) circular-120
  as bridge and saturated anchors (their clipped channels censored). The colour reading needs no
  second geometry; the same PNGs supply the edge shells on 63 colours, which is the
  colour-conditioning of the edge law.
- **Edge cells, 40 per scheme.** No-glass references for grey-128, grey-255 and the two vertical
  gradients (64→192 at 90° and 270°, equal centre level, opposite order). Circular 120×44 glass +
  opaque at y 70 / 140 / 210 on grey-128 and grey-255 (12). The two gradients at centre, glass +
  opaque (4). Span ladder: `rrect` 120×44, 120×64, 120×96 at held radius 22, glass + opaque (6);
  circular 120×64, 120×96, 96×96, 160×96, glass + opaque (8). W37's witness repeated: grey-255
  circular 200×44 at centre, glass + opaque (2). A new `column` kind — two INDEPENDENT circular
  120×44 surfaces at y 70 and 210 in one window, never `stack` — on grey-128 and on the 90°
  gradient, glass + opaque (4). The grey-128 centre cell is W34's grey-128 circular-120 bridge.
- **No-glass references for the colour cells** are captured in the FIRST run of each pass only
  (W34 proved every solid reference equals its raster at every byte at both scales): 63 per
  scheme per pass, raster-identity checks that confirm the input label, not bar inputs.
- **Conditional phase cells, 14 per scheme** (7 glass + 7 opaque over grey-128: the shared zero,
  x ¼ ½ ¾, y ¼ ½ ¾ as fractional width/height with the near edge pinned — exactly the actuator
  and geometry the preflight tests, nothing else), admitted per axis by the preflight; 8 if one
  axis passes; none if neither. The bed carries no cell for any other actuator.
- **Sentinels.** The long-protocol three-run sentinel kept on two ids per scheme (a grey circular
  and one colour cell) to detect order/settle drift.
- **Sizing.** Full bed: (40 + 63) × 2 schemes × 2 scales × 2 poses × 7 runs = 5,768 captures;
  references 63 × 2 × 4 = 504; sentinels 48; preflight 36 → 6,356 captures ≈ **17.0 h** of
  capture wall at W34's overall rate (9.62 s), ≈ **19.1 h** if both phase axes pass (+784). Before machine changes
  and the two grant switches. The trimmed alternative (colour at 2x only, a 13-colour subset at 1x
  because the archive's body medians are identical at both scales on 104/104 cells) is ≈ 12.7 /
  14.8 h; Decision Log 5 records the user's choice.

### The hypotheses (MARKED: declared with parameter counts in G0 before any pixel)

Let b be the sampled backdrop, F the stratum's neutral curve (its knots fitted on the neutral
cells), E/D the sRGB encode/decode.

- **H1** (negative control, already rejected): out_j = F(in_j).
- **H2** (the shipped shader, exact): the tone solve on the group's tone luminance, `toneAdapt`,
  the black branch, then `bodyChromaRetention` toward the blurred backdrop's chromaticity at held
  luma with the f32 guard and `gamut_at_luma`; the output chromaticity coefficient is
  q_base + (1 − q_base)·r, not r. Its fitted variant H2′ frees r and the tone knots.
- **H3** (coupled transform, concrete): z = D(F(in)); out = E(clamp(M z, 0, 1)) with a fixed 3×3 M
  per scheme × pose, M·1 = 1 (six free coefficients; neutral curve preserved). An OKLab-domain
  variant H3′ (tone on L, a fixed 2×2 on (a, b)) is a separate declared candidate with its own
  count, not a fallback space chosen after seeing held colours.
- **H4**: any surviving body law plus a separate chromatic boundary term B(body, b, signed n, d,
  span) with B = 0 on the deep domain; identified only with out-of-sample edge improvement AND
  independent non-zero boundary evidence, never by parameter count.

Discriminators: the matched-channel pairs kill channel independence locally (H2* predicts a
9.85-code R difference where H1 predicts 0); the factorial's six hue directions at three Y give M
its rank and the two C levels test linearity; matched-Y pairs test whether tone is Y-indexed or
mixture-indexed. An H3 with M close to identity is within 3 codes of H1 on the whole bed; that is
reported as insufficient resolution, not inflated by picking a colour outside the box.

### The edge law (MARKED: declared in G0)

Beside W37's even lobe, a signed-normal term s·max(0, −n_y)^p (top-lit) with its amplitude
conditioned on the identified body law's per-channel response (the line lifts the body's own
saturated channels), fitted on calibration strata at both spans; the three positions and the
column test its constancy against window height; the gradient flip tests backdrop dependence;
the rrect ladder identifies thickness against span at held curvature; the circular ladder
against radius. The reader: W37's G0b `canonical.py` extended to −14 CSS px inward, to attested
`frameOrigin` positions, to the new paths' SDFs and to paired top/bottom equal-depth bins with
separately calibrated opaque coverage. Per-run registration is never fitted to erase the
variance being measured.

### The split (MARKED)

Roles are SCENE-level, as W34's guarded reader enforces them (`wave.py` assigns one role per
scene and returns that scene's whole admitted payload): a scene is wholly in one role at both
scales, and whole glass/control pairs stay together. Calibration: 44 and 64 rrects, 44 circular
at the three positions on grey-128 and at top and centre on grey-255, the gradients, the column,
49 colours. Validation: 96 span (rrect and circular 120×96), 96×96, 6 colours. W39 holdout,
whole pairs at both scales: the grey-255 BOTTOM position pair, the circular 160×96 pair, **the
W37 witness pair (grey-255 circular 200×44 glass + opaque)** — so the directional law is
identified on the 120-wide cells and refereed on the very cell W37 read — and the 6 held-out
colours as whole cells (body and edge shells alike). No bin, region or scale of an admitted
scene is ever "held out": opening a calibration PNG exposes all of it. If G0's twin audit finds a
holdout member is needed to identify rather than referee, it moves to calibration BEFORE
capture. The hashed `split.json` is enforced by the wave reader and launcher (W34's pattern),
and the holdout's payload is producer-created and behind the procedural boundary from G1.

### Repeats and the bar

Seven; the bar per cell/bin/channel is 0.5 + half the largest pairwise separation of the run
medians, computed before plurality; the spatial deep profile (min/max) is recorded separately
and never used as repeat noise; a zero observed spread buys no tolerance.

### The archive of record

Complete: role-separated, lossless crops in original coordinates with the dependency closure
(no-glass and opaque pixels, alignment inputs, every neighbourhood an estimator reads), the
per-run statistics with populations and input hashes, the state membership; a SHA-256-pinned
inventory; replay proved identical with the raw root denied (W34's `replay-archive.py` pattern).
Its home is Decision Log 1. If the home is a release asset: `.tar.zst` under 2 GiB named by its
SHA-256, a reader that fetches by that name into a cache outside the repository, verifies the
full digest and then uses the guarded role reader; the ledger records tag, name, digest, bytes and
the replay command; a second owner-controlled copy for durability. A thin projection is a
convenience only, never the record.

### The harness additions (G0; X11)

`position` (absolute centre in canvas CSS px, Double) on a single shape and on each `column`
member, replacing `offset` for W39 scenes (fractional size with a pinned near edge is position =
edge + size/2, so no `anchor` field); the `column` kind (two independent glass surfaces, or two
opaque fills, each with its own attested path); the manifest's requested/actual window frame in
screen coordinates (an attestation, not an actuator).
Existing `capsule` and `rrect` resolutions untouched; the canonical `scenes.json` untouched.

### The grant plan (Decision Log 4; the user's hand, `amigo` first)

1. Before any build or Settings change: positive scratch capture with the ORIGINAL granted bundle
   (27-only 2x light checkerboard capsule; `materialRendered`, `presentedActive`,
   `deterministic` true, `repeatNoise` 0); stop if it fails.
2. After inputs are final: one build outside the repository, `VITREA_BUILD_OUT=~/vitrea-w39/side`,
   `VITREA_BUNDLE_ID=dev.vitrea.reference-apple.w39`; SHA-256 and cdhash pinned; no rebuild after
   granting.
3. The user grants the side app in Screen & System Audio Recording (remove a stale off row first).
4. Positive check of the side (up to three pose checks as W34 DL4 allowed), and of the original
   (expected: refused); stop on an unexplained state; no restore mid-sitting.
5. The preflight, then the passes; one wrong mode, lost grant, failed idle or foreign process
   stops the pass, never a hidden retry.
6. At wave close the user re-adds the original; positive check of the original, then the side
   (expected: refused); the side stays at `~/vitrea-w39/side/` ungranted. Failure to restore is
   an open blocker, not a closed sitting.

## Children

### G0: The bed, the harness, the bundle, the preflight and the archive tooling — declared and rehearsed, nothing captured into evidence

Branch `w39-g0-colour-edge-bed`; evidence `packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/`;
ledger **§5.184**. Delivers: (a) the harness additions with tests (`position`, `column`, the frame
attestation; `SceneSpec.swift` refuses `offset` beside `position`);
(b) `scenes-w39-colour-edge.json` with every cell above, the 320×280 canvas, single role `probe`,
its backgrounds; the twin audit against `scenes.json` and W34's file; `split.json` hashed; (c) the
declaration: forward families with parameter counts and spaces, the colour box and censor rule,
the edge law and its bins, the statistics, the bar formula, the closure and resolution rules, the
preflight's pass rule and both branches, the stop conditions — one `bounds-declaration.txt` with
its SHA-256 recorded before any pixel; (d) the archive reading (H1 and shipped-H2 rejections on
unclipped channels) as committed scripts through the guarded reader; (e) the reader extensions
(−14 CSS px, positions, new paths, paired equal-depth bins) tested on the W34 archive's
calibration cells; (f) the sitting script, the preflight script with its verdict artifact, the
archive producer and the fetch-and-verify reader for the home Decision Log 1 chooses; (g) the side
bundle built and pinned, NOT granted; four dry rehearsals of the launcher with capture refused
(no grant), attestations committed; (h) the wave reader and launcher enforcing the split. Merged
after independent review (`doperpowers:reviewer-high`) before any pixel.

### G1: The sitting — the grant switch, the preflight, the bed at the bar; archived and published; no read against vitrea

Branch `w39-g1-colour-edge-sitting`; evidence `…/2026-09-26-w39-g1-colour-edge-sitting/`; ledger
**§5.185**. The user's two hand actions (grant; nothing else during the sitting). The preflight
first and its verdict frozen (Decision Log 3); the passes 1x/2x × active/inactive, seven runs,
sentinels after; every run attested; quarantines named; the archive produced, pinned and stored
by Decision Log 1 with the ledger citation; the bar published from the archive before plurality;
replay proved with the raw root denied; the materialised probe bed committed by role with the
holdout's payload behind the procedural boundary. Nothing is read against vitrea.

### G2: Identification — the colour law and the directional edge law against the bar, or the negative at its resolution

Branch `w39-g2-identification`; evidence `…/2026-09-26-w39-g2-identification/`; ledger
**§5.186**. Fits on calibration through the wave reader (validation transfer read-only); freezes
by artifact; opens the six held-out colours and the wave's holdout once on a receipt binding the
inventories; reports least-squares and minimax, worst-channel and all-channel, every repeat
state; the discrimination rule between survivors; the transfer table to vitrea's rendered body
(W37's pattern) for each surviving law; CSS reach per surviving law stated from
`optics.ts`/`css-tier.ts` (a per-channel or matrix law is WebGPU-first with a CSS residual
recorded). Ends in Decision Log 2.

### G3 (conditional on Decision Log 2 finding a law): The leaf(s), the seal, the read, the landing

Ledger **§5.187** (and §5.188 if split G3a/G3b as W37 chartered: pre-seal render and every path
read; then seal + canonical holdout + tree in one merge). The leaf(s) through the identity table
(identity gate-group), WebGPU tier; the CSS derivation measured, carried or declined; W38's
per-bin veto FIRST against the shipped treatment, E2 frozen against the pre-W39 capture and R1;
M1/M2/C1/X1/L1 re-read; goldens attributed; the four documents resealed; the canonical holdout
read once by artifact; the capture tree copied and the superseded one moved; the demo and README;
the changeset (`@vitreajs/vitrea-web` minor); the release checklist; `pnpm release` is the
user's hand.
G3 stages its whole membership (calibration, validation, both tiers, and the holdout read after the seal) and publishes once at the seal merge.

## Cross-Child Contracts

W34's **X1–X14** carry verbatim with these substitutions: X3's identifier is
`dev.vitrea.reference-apple.w39` and its out-of-tree root `~/vitrea-w39/side/`; X5 authorises
native capture for the W39 probe bed only (the wave-local scenes file, the wave's fixture root,
the side bundle; no canonical key, no 26.5 key, no accessibility pass); X8's split is W39's; X11's
ownership is G0 the Swift additions, `build.sh` only if a seam is missing, the scenes file, its
tests and dir; G1 its dir and the probe fixtures; G2 its dir; G3 as W37 X11. W37's **X15–X17**
carry (the excess is the estimand and the coefficients are native-identified; the inactive pose
is read here, not assumed identity, because both poses are captured; the sampling-backend
contract at G3). W38's **X18** carries (per-bin veto first). New:

- **X21 — the colour box and the censor rule.** Every colour cell inside [40, 150] per channel
  by construction; a native channel ≥ 250 or ≤ 5 is censored, excludes its cell from full-RGB
  inversion and stays a scalar bound; no colour is replaced after a rail hit; a censored held-out
  cell is UNMEASURED, never a pass.
- **X22 — the preflight precedes the bed and the bed is the actuator's.** One actuator; its
  pass rule (near edge invariant, far edge ≥ 3 states beyond the integer-size control, a shift
  not an amplitude) and both branches are in the declaration; a phase cell enters the bed only
  for a reachable axis and only on that actuator; an unreachable axis's cells are omitted
  verbatim; no phase is inferred from backdrop motion; every preflight capture and reading is
  kept.
- **X23 — prediction before opening.** The six held-out colours and the wave's holdout are
  predicted, frozen by artifact and opened once on a receipt; validation is transfer only; the
  W34 holdout is never opened.
- **X24 — the archive of record is complete wherever it lives**, cited by SHA-256 and byte size
  in the ledger, fetched and verified by that name; a thin projection is convenience only.
- **X25 — one canvas, attested positions.** 320×280 for every W39 cell; the reader takes each
  shape's position from the attested `frameOrigin`, never from the declaration alone; the
  supplied path attests what SwiftUI supplied, not what the window server rasterised.

## Ordering & Dependency Map

G0 (declaration, harness, bundle, tooling; DL1 and DL5 ruled before its merge) → the user's
grant switch → G1 (preflight → DL3 → passes → archive → bar) → G2 (identification → DL2) → G3 if
a law closes (→ DL6 → landing → release) → wave close (the original grant restored, DL4
executed). W40 (matrix per-generation files), if the user charters it, runs after G0's merge and
lands before G3's landing.

## Risks & Mitigations

- **The admissible box is a prediction.** A coupled transform can excurse between the sampled
  inputs; the censor rule keeps a rail hit honest and the bed is not re-chosen mid-sitting.
- **The phase mechanism fails again.** The preflight costs 36 captures; the bed loses only the
  phase cells; no second actuator runs in this sitting; the negative is recorded with every
  reading, and the other candidates stay Deferred with the reason.
- **The grant evicts the original again.** Planned; both positive checks each way; the sitting
  never restores mid-way.
- **The sitting is long.** 17–19 h contiguous, the machine untouched; the largest honest lever is
  the 1x colour pass (Decision Log 5), never the repeat count, a scheme, a pose, a validation
  span or a control pairing.
- **The archive's home fails to fetch.** A second owner-controlled copy; the digest detects
  replacement but not loss; recorded as an operational dependency.
- **A law closes on the body but not the edge, or the reverse.** Claims stay separate; a body
  leaf can land alone under clause 10; the edge stays a named miss.
- **Translation cannot attribute the lighting frame.** Declared up front (clause 7); the law is
  effective, not mechanistic; an oriented/asymmetric path is Deferred.

## Deferred / Out of Scope

- An oriented or asymmetric attested path (or a rotated shape frame) that could separate
  path-local from screen-up lighting.
- A saturation ladder above OKLab C 0.055 (risk cells that may clip on one channel).
- Author tint over coloured backdrops; the accessibility beds; span 160.
- The window-origin, odd-canvas and transform phase candidates (each would need its own
  declared bed and a preflight of its own; the window-origin one also needs per-cell window
  repositioning, which the one-window-per-process harness does not do).
- W37 Deferred 3–8, W36 Deferred 1–6 as they stand until G2 reads them.

## Tracking Map

| child | status |
| --- | --- |
| G0 | MERGED 2026-09-26 as `ba38ebbf` (§5.184): 388 ids, split 316/36/36, declaration final 94cebb42… with five superseded hashes retained, side pinned and ungranted, tooling tested (718 + 89), review 3 P1 / 1 P2 fixed, re-review clean. Outstanding: the TCC-refusal rehearsal (machine not exclusive: a foreign Chrome; a since-dismissed unattributed prompt). |
| G1 | — |
| G2 | — |
| G3 | conditional |

## Decision Log

### Decision Log 1 — the archives' home and the matrix's history (before G0's merge; the user's)

Put to the user 2026-09-26 with the numbers above. Options for the W39 archive: a GitHub release
asset named by SHA-256 (recommended; keeps 200–350 MB out of ordinary Git, CI and Pages; an
operational dependency on the asset's availability, mitigated by a second copy), Git LFS for new
archives only (path readers after hydration; CI/Pages hydration and quota), ordinary Git as W34.
For the matrix: a separate housekeeping wave (W40) moving future generations to indexed
per-generation files with no history rewrite (recommended), or keep the monolithic file.
**RULED by the user, 2026-09-26: the W39 archive is a GitHub release asset named by SHA-256,
fetched and verified by the readers, kept out of ordinary Git; and W40 is chartered as the
matrix housekeeping wave after W39 G0's merge, to land before W39's G3 landing.** G0 therefore
delivers the archive producer, the release-asset naming and the fetch-and-verify reader; G1
publishes the asset and the ledger citation (tag, name, digest, bytes, replay command) and keeps
a second owner-controlled copy on the capture machine outside the repository.

### Decision Log 2 — a law or the negative (after G2; the user's)

### Decision Log 3 — the phase mechanism: reachable or declared unreachable (in G1, by G0's rule; the parent's)

G0's rule as executed (superseding clause 4's first wording where they differ; the declaration
is the contract): 40 preflight captures (36 geometries plus the phase-0 pair repeated at the end
of each scale as a repeat sentinel); near-edge tolerance max(0.5, D_int_near); far edge ≥ 3
states beyond max(0.5, D_int_far); the shift test as one shared integrated profile with knots
every 1.0 DEVICE px translated per phase against the same profile at one edge with per-phase
gain, RSS_shift ≤ 0.5·RSS_amp with the amplitude fit converged (tolerance 1e-10, cap 200),
monotone edges within 1/32 device px, full rank with the condition number, leave-one-phase-out
at max(0.5, D_int_far) + 0.5·‖w_i‖₁. Proved on seven synthetic beds (true shift admits both
axes; amplitude-only and a half-pixel-snapped raster admit none; one-axis admission; drift
refused). The amplitude alternative's shared edge is underidentified and its edge/gains are
never reported as physical; its RSS is the comparison.

### Decision Log 4 — the grant switch and its restoration (the user's hand; the parent plans and checks)

G0 record: the side bundle `dev.vitrea.reference-apple.w39` is built at `~/vitrea-w39/side/`
(binary 02052b17…, cdhash be258cbf…), NOT granted; the system TCC database reads the original
allowed, `.w34` denied, `.w39` no row. An unattributed pending Screen Recording prompt naming
"VitreaReference" was found on screen during G0 (not raised by G0's launches: `backgrounds` and
`self-check` touch no ScreenCaptureKit path); the codex companion could not act (its screenshot
of the prompt was denied); the user dismissed it with Deny at 2026-09-25T17:16Z; no system TCC
row was written. The TCC-refusal rehearsal could not run because a foreign Chrome session (14
capture processes) held the machine; it is G1's first step, before the grant switch.

### Decision Log 5 — the sitting's size (before G0's merge; the user's)

Put to the user 2026-09-26: the full bed (colour at both scales; ≈ 17.0 / 19.1 h) or the trimmed
bed (colour at 2x, a 13-colour 1x subset; ≈ 12.7 / 14.8 h). Recommended: full. **RULED by the
user, 2026-09-26: the full bed, in one untouched sitting.** Seven runs; no scheme, pose, scale,
validation span or control pairing is dropped for time.

### Decision Log 6 — bounds and floors if a leaf lands (in G3; the user's)

## Surprises & Discoveries

- **The archive already answers the per-channel question**, and in the negative, on unclipped
  channels: the brief asked for an experiment to separate H1 from the rest and the memo showed
  the separation exists in the calibration cells (input 32 → 148 / 96 / 81 on grey / green /
  yellow). The bed spends nothing on it.
- **The shipped model is not luma-preserving as a whole.** The tone solve changes Y; only the
  retention that follows preserves its incoming Y. CLAUDE.md's "luma-preserving by construction"
  is a statement about the retention step, and the charter says so.
- **Two schemes cost one process** (writable `colorScheme`), which is why the bed's count is per
  scheme and the passes are four, not eight.

- **The review's model arithmetic on the colour bed** (v1 round): H2* differs from H1 by up to
  8.80 codes on the light-active factorial and 3.28 on dark-active; the declared OKLab candidate
  fitted on calibration to an H2* world stays within 2.70 / 2.67 / 1.17 / 1.01 codes on all 61
  colours (light active / light inactive / dark active / dark inactive) — so a one-code test
  discriminates those instances and a three-code separation cannot be assumed, which is what
  the "insufficient resolution" outcome is for. And a wrong fitted law can pass the six
  held-out colours (0.755 max) while failing calibration (1.458): survival is now defined on
  calibration and validation first (clause 8).

- **The preflight's terms needed three corrections before any pixel** (G0): the half-device-pixel
  knot grid had an exact Nyquist null vector under unit-pixel area integration, so "full rank"
  could never hold (knots moved to 1.0 device px); a held-out prediction from rounded samples
  carries a computable worst-case rounding term 0.5·‖w_i‖₁ (1.07–3.52 codes on the synthetic
  beds) that the plain max(0.5, D_int) tolerance ignored; and the amplitude alternative's fit
  broke after one iteration (inf ≤ inf), inflating its residual — caught by the review, with
  every verdict unchanged after convergence. All three are the parent's terms corrected by the
  workers' synthetic tests, recorded with their numbers.
- **H2′ as first declared was underidentified by construction**: freeing the four thick tone
  ordinates on an all-span-44 colour bed would have been rejected for rank, not for colour; the
  fitted variant frees retention plus the four thin ordinates and tests the thick row's transfer
  on the span-64/96 cells instead.
- **Operational**: an unattributed Screen Recording prompt on screen blocked every launch; the
  companion's GUI hand cannot see a TCC prompt; a background Chrome counts as a foreign capture
  process. None of it touched the evidence; all of it cost the rehearsal.

## Revision Notes

- 2026-09-26 (the user, routing): "prefer opus over sol" — from here, children, fix waves and
  grounding run on the default `opus` worker or on `astra` at medium/high; `sol` is no longer
  the default rung named in X9's carry-over. Reviews still route through the review-code
  agents (`reviewer-high` for gate merges).

- 2026-09-26 (G0's merge, the parent): merged `ba38ebbf` after an independent review (3 P1 / 1
  P2, fixed on the branch: amplitude convergence, sentinel protocol, borrowed-control
  calibration, pass ordering) and a clean re-review; freeze 1,818; no capture tree moved (no
  read). Counts corrected at G0 and recorded here beside the charter's: preflight 36 → 40,
  baseline 6,356 → 6,360, with both axes 7,140 → 7,144. Mid-gate parent rulings recorded in
  Decision Logs 3 and 4 and Surprises. Worktree removed; the side bundle stays outside the
  repository, ungranted.
- 2026-09-26 (the user, Decision Logs 1 and 5): full bed; release asset by SHA-256; W40
  housekeeping chartered after G0, before G3's landing. G0 dispatched.
- 2026-09-26 (v2, the parent): one adversarial round folded — P1 the conditional phase bed was
  defined on the size actuator while a window-origin fallback could have been the one that
  passed (fixed: one actuator, no fallback in this sitting, the others Deferred); P1 a bin-level
  holdout (the witness's 2x arcs) cannot be guarded by a scene-level reader (fixed: the whole
  witness pair is holdout at both scales; roles are scene-level); P2 three distinct glass
  responses can come from the size law, not the phase (fixed: integer-size control, near-edge
  invariance, a shift-not-amplitude rule; 36 captures); P2 survival was not defined on
  calibration and validation (fixed: clause 8 and 10). Verdict's checks recorded in Surprises.
- 2026-09-26 (v1, the parent): chartered from the two grounding memos; Decision Logs 1 and 5 put
  to the user; adversarial review requested.
