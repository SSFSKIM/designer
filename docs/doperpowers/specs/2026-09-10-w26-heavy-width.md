# W26 — the heavy width: the thick surface's haze through a kernel whose width is a parameter (2026-09-10)

**Status: CHARTERED 2026-09-10 by W25 Decision Log 7 (e) at W25's recomposition (claims §5.118) —
the continuation of the thick-span composite on the user's word ("the larger piece"); the 0.14.0
cut unpublished pending the user's eye. G0 dispatched.**

Composite spec: design at the top; Decision Log, Surprises, Deferred and Revision Notes at the
tail. Parent: `2026-08-28-post-v1-wave.md` (the W26 row; Decision Log 23 (c)'s thick-span item,
continued). Predecessor: `2026-09-09-w25-thick-span-composite.md`, whose clauses 2 and 3 this wave
takes with their measured cause.

## Purpose

W25 measured what the thick surface's haze is and why vitrea cannot draw it. The reference's kernel
is two components; the thick surface differs from the thin in the heavy component's SHARE (0.47 at
1x, 0.69 at 2x on the uncollapsed `impulse__rrect-md`, against vitrea's 0.23); and the share cannot
be raised because vitrea's heavy component is 13.3 device px wide at the reference's own share
against 19.5 — the body's heavy sample is one level of the backdrop pyramid, "not a Gaussian", and
its effective width does not follow `sizeScatterGainMax` (8 → 10.3 leaves the reading at 13.29;
claims §5.116 §2). Raising the share therefore adds narrow structure the reference does not have,
and every check off the fitting rows ran the other way. The nested base's haze, the collapsed
dot's width and the thick body's level are the same kernel seen three ways.

The wave's purpose is a heavy tap whose width is a continuous parameter the readers can see move,
fitted on the rows W25 captured for it — the probe set's coarse checkerboards and impulse rows at
both scales — and then the share per scale, the 2x lever through the floor, and the level above
the knee re-read on the same rows.

## Parent-Level Acceptance

Binding; the numbers are W25's readers' and the declaring child re-declares them on G0's read.

1. **The width is a lever.** Reader A's heavy σ on `impulse__rrect-md` / `-ml` / `-lg` at 1x moves
   monotonically with the new constant over a ladder spanning 10–25 device px, the sharp σ and
   the thin cells (span ≤ 44) unmoved (X5: a thin cell moved by more than 0.001 ΔE stops the
   ladder), the goldens byte-identical at the inert default.
2. **The thick surface's body matches** (W25 clause 2, re-declared): on every thick untinted
   probe and canonical row that identifies it, the heavy σ within 15 % and the share within 0.05
   of the reference's at both scales, and the coarse checkerboards' single-width objective
   (readers B / C) IMPROVING with the share rather than worsening; the level within 0.002 or the
   read says which backdrops disagree.
   *Re-stated 2026-09-10 (Decision Log 4 (h)), the original kept:* the thick body's kernel matches
   the reference's as an MTF over 1/64 → 1/8 cycles per device px within 15 % at every band, both
   identified by G1b's non-parametric instrument under its control; the share is the kernel's own
   mass split where the identified kernel has two parts, not a two-Gaussian reader's number.
3. **The nested base is Apple's** (W25 clause 3): its σ-match within 15 % of the reference's at
   both scales in both schemes, neither side saturated; the overlay's sign held.
4. **The collapsed dot's width** (W24 clause 2's carried half): the FWHM through
   `impulse__capsule-button` within 1 CSS px of the reference's at both scales, the peak held.
5. **The bed no worse anywhere**: W25 clause 6's numbers; the fourteen thick floors re-read (this
   wave is the one expected to move them toward their bounds); W24's angular reads and W25's
   along-side reads within their error bounds; no bound widened.
6. **The holdout once**, at the declaring child's dry run; the landing reproduces the bytes.
7. **The CSS tier derives what it can**: its one `blur()` at the shared width where the width is
   one number, the two-component kernel recorded as an X residual where it is not.
8. **By eye, and the ledger**: the nested pane's base and the thick rrects native | before |
   landed at 2×, the impulse dot at 4×; the user's veto. The cut after the landing.

## Grounding Baseline (the 0.14.0 bed, matrix at `99a74a0`)

- The readers: `results/2026-09-09-w25-thick-span-composite/g0/w25lib.py` (A the dot PSF, B the
  edge spread bound by the pitch, C the σ-match); validated on known kernels (claims §5.113 §1).
- The heavy tap: `wgsl/optics.ts` samples `backdropChain` at the level `bodySigmaCssFor` maps the
  gain to; the doc at `material.ts` §`sizeScatterGainMax2x` records "the mip chain's tap is not a
  Gaussian" and that the renderer, not the paper model, is the fitting instrument. The reference's
  heavy component is 19.52 / 11.29 device px at 1x / 2x (W25 §5.113 §2); W15 read 8–11 device px
  per span at 2x through a bounded Gaussian fit, ±40 %.
- The share law (`sizeScatterHeavyShareThick1x` / `2x`) and the level term (`sizeToneLevelFar`)
  are in the code inert with their rows and their declines (claims §5.116 §2); the 2x lift is
  clamped by `sizeScatterFloor2x` = 1.
- The rows: the probe set (52 scenes × four standard profiles; `checkerboard` at 4 / 8 / 16 / 32 /
  64 CSS px pitch, `impulse` over `rrect-sm` / `-md` / `-ml` / `-lg`, the solids at spans 32 → 160,
  both scales, both schemes), 414 web captures per tier reproduced at the landing.

## Design (advisory unless marked)

**The mechanism (binding as to what it must satisfy, advisory as to how).** A heavy sample whose
effective Gaussian-equivalent width is a continuous function of one constant per scale, exactly 1
in the readers' units where the constant says so, and inert at a default that reproduces the
0.14.0 bytes. Three candidates for G0 to try and measure: (i) a fractional pyramid level —
`textureSampleLevel` with a non-integer level, trilinear across two mip levels, the width read by
reader A against the level; (ii) a separable Gaussian at the tap over a chosen level, the σ the
constant; (iii) a second chain level blended with the first by a share. Whichever reader A sees
move monotonically over 10–25 device px at a cost the goldens can attribute is the one.

**The share and the level after the width (advisory).** With the width a lever, the share law's
lift is re-fitted on the same rows (the off-row check should now agree); the 2x share needs
headroom, which means the floor comes down from 1 at dpr 2 or the lift is applied before the
floor — X5 at every rung; the level above the knee re-read on the probe rows with the width
right, since a too-narrow heavy component reads as a level error on a coarse checkerboard.

**The CSS tier (advisory).** One `blur()` carries one width; where the kernel is two components
the tier's residual is recorded (Decision Log 23 (a)).

## Children

### G0: The heavy tap as a parameter — spike (deliverable: findings; no merge)

- **Purpose:** the three candidate taps built behind one constant, inert at the default; reader
  A's heavy σ read against the constant on `impulse__rrect-md` / `-ml` / `-lg` at both scales;
  the thin cells and the goldens read at every rung; the cost per candidate; the one that moves
  the width monotonically named, with the mapping from the constant to the Gaussian-equivalent
  width tabled.
- **Acceptance:** clause 1's ladder on one candidate; the mapping within 10 % of reader A on every
  rung; the sharp σ unmoved; the thin cells byte-identical.
- **Edges:** blocks G1. **Track:** spike; opus; worktree.

### G1: The width, the share, the 2x lever and the level fitted — controlled

Re-stated on G0's read (Decision Log 2); the original line is kept below it.

- **(a) The tap built structurally.** Candidate (ii)'s width as a third pyramid texture: the chain
  level `heavyTapPlan` names, blurred by the residual through the existing separable body-blur
  passes into a texture of that level's extent, sampled once at the refracted uv. The 9 × 9
  in-shader grid is the spike's instrument and comes out. Acceptance: reader A's heavy σ on the
  2x impulse rows at σ 11.3 within 5 % of the grid's read (12.22 / 11.95 / 12.04); the bench row
  `mobile-390x844@3 heavy-tap` within 0.2 ms of the control; inert at 0 byte-identical (the
  goldens and the 36 bed rows). One width per source: the mid-span rows (44 → 96) are read at
  every rung, and where they cross a floor the design blends the chain's `scatterLod` sample back
  by the ramp rather than adding a second texture (advisory).
- **(b) The instrument reaches the 1x width.** Reader A extended to a lattice model — the dot
  lattice convolved with sharp + heavy Gaussians and a share, fitted on the whole tile so the
  window is the tile and not half a pitch — validated against reader A on the 2x rows where A is
  monotone (within 10 %) and on synthetic kernels including the chain's own platykurtic level 4.
  The 64 CSS px pitch's fundamental is modulated 16 % at σ 19.5 device px and 5 % at σ 25, so the
  lattice reader is expected to resolve the reference's width and not much past it; where it
  cannot, the fallback is a wider-pitch impulse probe scene declared for a sitting — the user's
  console, so that fallback is reported, not taken.
- **(c) The fits, per scale, on the impulse rows.** `sizeHeavyTapSigma2x` on `impulse__rrect-md`
  / `-ml` / `-lg` at 2x (prior 11–12); `sizeHeavyTapSigma` at 1x on the lattice reader (prior
  19.5, the reference's 1x read, quoted with G0 §6's caveat); then the share per scale by reader
  A's own share on the same rows, its off-row check the lattice reader on the second impulse span
  rather than the checkerboards (Decision Log 2 (d)); the 2x share's headroom, `sizeScatterFloor2x`
  coming off 1 or the lift applied before the floor; the level re-read on the probe solids; the
  sharp σ read and recorded at every rung, not fitted. Each fit with its condition and its
  decline; the thin cells at every rung (X5); the fourteen thick floors re-read at the candidate.
- *Original:* the width per scale on the probe set's impulse rows and coarse checkerboards; the
  share per scale on the same rows, checked off them on the checkerboards' single-width objective;
  the 2x headroom; the level re-read; each with its condition; the thin cells at every rung.
- **Edges:** blocked-by G0. **Track:** controlled; opus; worktree.

### G2: Declared and dry-run — controlled

- The constants, the documents once, `W26_HASHES`, the CSS mirror, the stops (W25 G3's set plus
  S15: reader A's heavy σ on any fitted row further from the reference's than at 0.14.0), the dry
  run with the holdout once, the sheets.

### G3: The landing — controlled; 0.15.0 after the user's eye.

## Cross-Child Contracts

X1 the readers are W25 G0's; X2 canonical writes only at G3; X3 the holdout once at G2; X4 the GPU
shared, one capture at a time, goldens in the foreground; X5 the thin capsule does not move; X6
the user's eye; X7 the dark profile a difference document.

## Deferred / Out of Scope

- **The 1x heavy width, and the probe fixture that would let it be fitted** (Decision Log 3 (b)) —
  a wider pitch AND a larger dot, so the transmitted heavy peak is codes rather than a fraction of
  one; a native sitting, which is the user's console.
- **The sharp component at 1x, 40 % narrow and unaddressed.** Vitrea reads 1.65–1.84 device px at
  every rung against the reference's 2.74–2.79, and no constant in the material moves it (claims
  §5.120 §8).
- **The 2x span grading the one-width-per-source structure gives up** — the reference's `-lg` row
  reads 16.92 against `-md`'s 11.29 at 2x, and the chain's clamped tap followed that where a single
  width cannot (Decision Log 2 (f), measured in Decision Log 3 (f) (i)).
- The rim's arc amplitude as a three-term joint fit (W23's law, W24's exponent, W25's field).
- The size-keyed light adaptation of a small surface over a bright backdrop in the dark scheme.
- The contour instrument's refusal on flat-cornered dark squares; the 2x reference's run-to-run
  instability; the demo page's coupling to `scenes.json` (tracker).
- **Whether the accessibility frost should reach the heavy width** (Decision Log 7 (d)) — measured
  at G2 as reaching the sharp component alone on both tiers, at the price of one CSS calibration
  cell leaving the shape gate; not declared and not fitted by this wave.

## Tracking Map

| child | status |
| --- | --- |
| G0 — the heavy tap as a parameter | CLOSED 2026-09-10 (claims §5.119) |
| G1 — the width, the share, the lever, the level | CLOSED 2026-09-10 (claims §5.120; Decision Logs 3–4; merged at `d306214` after the review's two fixes at `d06fe3c`) |
| G1b — Apple's kernel identified without a shape assumption (spike) | CLOSED 2026-09-10 (claims §5.121; merged at `1d541bf`) |
| G1c — the fits, second reading: both widths on the family reader (controlled) | CLOSED 2026-09-10 (claims §5.122; merged at `5a710ad`) |
| G2 — declared and dry-run | DELIVERED 2026-09-10 (claims §5.123 DRAFT; Decision Log 7 — the parent rules (a)–(d)) |
| G3 — the landing | — |

## Decision Log

### Decision Log 1 — the charter (2026-09-10; the parent, by W25 Decision Log 7 (e))

Chartered on W25's measured cause rather than on a new finding: the mechanism first, as a spike
that reads its own width with the instrument W25 built, because a constant that does not move the
reader is the failure mode W25's share fit found. The share, the 2x lever and the level are fitted
only after the width is a lever. The 0.14.0 cut stands unpublished until the user's eye; this wave
lands as 0.15.0.

### Decision Log 2 — G0's verdict: the Gaussian at the tap, with two conditions (2026-09-10; claims §5.119)

(a) **The mechanism is candidate (ii)**, a Gaussian at the tap over a chosen chain level, and the
choice is not a judgement between three working options: candidates (i) and (iii) are inert at
dpr 1 **to the bit** (18 / 18 1x captures byte-identical at every value; 16 / 18 2x captures
differing), because `scatterLod` is already at `chainMaxLod` and the chain has no level 5 on a
320 × 200 raster. The saturation §5.116 §2 measured is the clamp, and the clamp is the pyramid's
own last level.

(b) **The cost is real and the fix is structural.** The 9 × 9 in-shader grid costs +1.1 ms on the
optics pass (1.416 → 2.528 ms; the frame 134 % → 218 % of the ~2 ms hypothesis). G1 builds the
width as a **third pyramid texture through the existing separable body blur** — 0.070 ms on the
same bench row — which is the same width exactly and continuously, at the cost of being one width
per source rather than per pixel. §5.113 §4 ("the width does not grade above 96 at any pitch") is
what says the material can afford that; `sizeScatterGainFar2x`'s span grading is then re-expressed
or retired, and that is a decision for G1's declaration.

(c) **The 1x width is not fitted on the 1x impulse rows.** Reader A's window on `impulse` is half
the 64 CSS px dot pitch — 30 device px at 1x — and a 19.5 device px heavy component does not fit
in it; the reader parks on its own bound above σ ≈ 17 and the 1x ladder is non-monotone while the
2x ladder over the same constant is monotone on an identical drawn kernel. So **clause 1's ladder
is re-stated onto the 2x rows**, and the 1x constant is carried down by §5.113 §2's halving or
fitted on a wider-pitch impulse probe fixture. The 1x reading of the reference (19.52) sits at the
same edge and is quoted with that caveat from here on.

(d) **The coarse checkerboards' single-width objective is retired as the share's off-row check.**
At the reference's own width it still runs the wrong way, and so does the width alone (§5.119 §7),
because those readers are dominated by the kernel's core and §5.113 §2 already measured vitrea
32–46 % too wide there. The residual it carries belongs to the SHARP component. G1's off-row check
has to separate the two components, and the sharp width becomes a named quantity of this wave
rather than W25's declined `blurSigma2x` sibling.

(e) **The 2x width is reachable with `sizeScatterFloor2x` = 1 in place** — one constant at 11.3
device px puts reader A's heavy at 12.22 / 11.95 / 12.04 against the reference's 11.29 / 12.03 /
16.92 — so the floor question stays what W25 left it as: the SHARE's, not the width's.

(f) **The parent's rulings on (b) and (c)** (the parent, on G0's report). On (c): the 1x width is
NOT carried down from the 2x fit — the reference's own halving is 15 % off (2 × 11.29 = 22.58
against its 1x read of 19.52), so a carried-down constant would be fitted on an assumption the
same ledger already contradicts. The instrument is extended first: reader A as a lattice model
over the whole impulse tile (G1 (b)), which costs no sitting and is validated where A already
works. A wider-pitch probe scene is the fallback and is a sitting — the user's console — so G1
reports it rather than takes it. On (b): one width per source loses the 2x span grading
`sizeScatterGainFar2x` carried (the reference's `-lg` row reads 16.92 against `-md`'s 11.29 at 2x),
and that is recorded as a named gap in the tracker at G1's declaration rather than answered with a
second texture; the mid-span rows are the check that the one width does not cross a floor.

### Decision Log 3 — G1's read: the mechanism is free, the 1x width is unfittable on this bed, and two costs are the parent's to rule (2026-09-10; claims §5.120 DRAFT)

DRAFT, by G1. The parent rules (a)–(f) and amends beside; G2 declares whatever survives.

(a) **The tap is structural and it is exact.** The heavy width is a third pyramid texture built by
the existing separable body blur, and at σ2x 11.3 it reproduces G0's 9 × 9 in-shader grid on all
three 2x impulse rows **to the last digit** — 12.22 / 11.95 / 12.04, 0.0 % against a 5 % acceptance.
The bench row is 2.366 ms against a 2.186 ms control, +0.180 ms inside the 0.2 ms acceptance, with
the OPTICS pass unchanged and the whole cost on `body-blur`. Inert at 0 to the bit (33 goldens,
36 bed rows). Decision Log 2 (b) is executed and closed.

(b) **The 1x width cannot be fitted on this bed, and the cause is the FIXTURE.** Decision Log 2 (c)
named reader A's window; that is the smaller half. The 1x `impulse` interior carries about one
display code of modulation in total (native `rrect-lg`: standard deviation 0.0055 at a level of
0.4508, where one 8-bit sRGB code is 0.0059), and the heavy component's own peak is 0.08–0.33 codes.
A heavy component of 13.42 device px and one of 25.0 device px are bit-identical on 96.7 % of the
tile after quantisation. Reader D — validated exact on the model, within 5.2 % on the chain's own
kernel, and within a median 4.5 % of reader A where reader A works — reads to 1.6 % where the heavy
peak is 2.56 codes and misses by 79–90 % under half a code. **The instrument extension worked and
the fixture is the wall.** The fallback is a probe scene whose transmitted dot peak is many codes
(about a 12 CSS px dot on a 128 CSS px pitch) captured in a native sitting; G1 reports it and does
not take it, per the ruling that a sitting is the user's console.

(c) **The 1x anchor is named, not fitted, and it is free.** `sizeHeavyTapSigma` = 13.418 =
`CHAIN_LEVEL_SIGMA[4]`, the width the clamped tap already draws at dpr 1. It is **byte-identical**
on all 17 1x ladder rows and every 1x and dark probe cell, it keeps `rampAtScale` continuous between
the anchors (a 1x anchor of 0 beside a nonzero 2x anchor would make the heavy blur vanish at dpr 1
and be a fraction of a pixel wide at dpr 1.05), and it turns the 1x heavy width from a property of
the backdrop raster's size into a material constant every raster reproduces. That last is a
correctness improvement independent of any fit and closes one of G0's tracker entries.

(d) **The reference's own 2x `-ml` and `-lg` rows are unconditioned**, and reader A's fitted SHARP
component is what says so: 11.80 and 9.67 device px against `rrect-md`'s 1.40 and the 1x rows'
2.74–2.79. Reader A has split a single wide kernel there. `sizeHeavyTapSigma2x` is therefore fitted
on `impulse__rrect-md` alone — residual |log| 0.2536 → 0.0143 at **10.3** — and §5.113 §2's readings
for those two rows stand as recorded with this one beside them.

(e) **Three constants decline on measurement.** `sizeScatterFloor2x` stays 1: the objective is flat
(0.1174 → 0.1140 at 0.85, worse below) and every value off 1 moves the thin `impulse__rrect-sm` row,
which X5 forbids — the floor has no `sizeThick` factor to make it inert at the thin end the way the
lift does, and that structural difference is the decision. `sizeScatterHeavyShareThick2x` stays 0:
the 2x share is too HIGH, so a lift is the wrong sign, which answers "the lift applied before the
floor" without a code change. `sizeToneLevelFar` stays 0: the candidate moves no probe solid by more
than 0.00001 and W25's sign flip across backdrops is unchanged, so the flip was never a symptom of a
narrow heavy component.

(f) **Two rulings for the parent.** (i) `impulse__rrect-lg` at 2x goes 16.59 → 11.07 against an
unconditioned reference of 16.92; G2's stop S15 fires on it as stated. The choices are to re-state
S15 onto the conditioned rows, to accept it as the gap Decision Log 2 (f) already recorded, or to
decline the 2x width — in which case (c)'s anchor is all W26 lands, byte-identical. The advisory
remedy (blending the chain's tap back by the ramp) does not reach it: the row is at the THICK end of
that ramp, and the mid-span rows the advisory was written for move by 0 at 1x and under 0.0004 ΔE at
2x. (ii) `sizeScatterHeavyShareThick1x` = 0.25 improves the identified share by 72 % (mean |Δ|
0.2652 → 0.0745) and WORSENS the bed's OKLab ΔE at every 1x thick span (96: 6 / 9 cells, 128: 5 / 7,
160: 7 / 12). Those columns isolate the lift exactly, since the 1x width is byte-identical. The
wave's premise was that the share could be raised once the width was right; at 1x the width could not
be made right, so the premise was never tested, and declining the lift is the consistent reading of
W25.

(g) **The bed stands.** Every adopted bound and all fourteen thick regression floors pass at the
candidate; no floor became removable. Two gate assertions fail as one improvement: the conditioning
predicate ADMITS two 2x-light texture cells the frozen bed excludes, and both meet the bounds.
`PREDICATE_EXCLUDES` and the 2x-light count are G2's edit. X5 over 81 thin probe cells: worst move
0.00017 against 0.001.

### Decision Log 4 — the parent's two rulings, and G1 §7's follow-on: a readable 1x lever and an unidentified target (2026-09-10; claims §5.120 addendum)

(a) **S15 is re-stated** (the parent): "any fitted row, or any row whose reference two-component fit
is conditioned (sharp under 4 device px)". It does not fire on `impulse__rrect-lg` at 2x — not a
fitted row, and its reference fit returns a sharp component of 9.67 device px — so Decision Log
3 (f) (i)'s first choice is taken and the row's move stays the gap Decision Log 2 (f) recorded.

(b) **`sizeScatterHeavyShareThick1x` = 0.25 is DECLINED** at the current 1x width (the parent), on
the evidence shape W25 declined it on. Re-tested only if the 1x width becomes fittable; (e) says it
does not, so the decline stands and W25's four declines are joined by this one.

(c) **The dark columns of G1's probe table were the inert material.** A scratch rung writes its
constants into the LIGHT document only, and the dark difference document is resolved over
`DEFAULT_MATERIAL_PROFILE` rather than over the light patch — so the dark captures took this wave's
constants from the code default of 0. Nothing about the dark scheme makes the heavy width inert; a
LANDED constant reaches it, because landing edits the default. Re-captured with the candidate in
both documents the dark bed moves and X5 holds at 0.00013 over 41 thin cells. **The lesson
generalises past this wave: a scratch rung is not a rehearsal of a landing unless every document a
landing would move is moved in the rung**, and the two differ precisely for constants the dark patch
does not name.

(d) **The coarse checkerboards are an instrument for the 1x width after all**, and Decision Log 2 (d)
is not disturbed: what it retired was a SINGLE-Gaussian objective dominated by the kernel's core. A
two-component lattice reader on `checkerboard-64` — 63–73 display codes where the impulse tile's
heavy component has 0.08–0.33 — returns the drawn width to 0.0–1.8 % on synthetics at the fixtures'
own contrast and tracks readers A and D within 10–13 % at 2x, and vitrea's 1x ladder on it is
monotone at a slope of 0.95 from σ 13.418 up. `checkerboard-32` cannot, and its pitch says so before
any capture.

(e) **The 1x width is still not fitted, and the reason has changed.** The lever is readable and the
TARGET is not identified: the reference's 1x heavy component reads 8.4–8.7 through `checkerboard-64`
and 14.7–23.3 through the impulse tile, a joint fit across both tiles lands at 9.0–9.5 and **fails
its control** by under-reading vitrea's known 13.42 by 14–23 %, and every reader's residual on the
real surfaces is 5–7 times its residual on its own synthetics. Apple's kernel is not two Gaussians;
which two a reader recovers depends on the backdrop. Fitting on either instrument would be fitting
an instrument, which is the failure mode this wave was chartered to avoid.

(f) **What that puts in question is W25 clause 2**, whose "heavy σ within 15 % of the reference's at
both scales" presumes the reference's heavy σ is a single number. It is a projection onto a
two-Gaussian basis and the projection is backdrop-dependent by a factor of 3 at 1x after each
instrument is debiased against vitrea's known kernel. The parent's clause list is the parent's; G1
records the measurement and does not amend the clause.

(g) **The next instrument, and it needs no sitting** — a kernel model with more than two components,
or two with a shape parameter, fitted jointly across three or more backdrops of one surface and
validated first on VITREA's own known kernel. That control is the one every reader in this wave
should have had, and building it is what turned the disagreement from a puzzle into a measurement.
The wider-pitch impulse probe scene stays the fallback for the impulse-side reading and drops to
second priority.

(h) **The parent's ruling on (f) and (g)** (the parent, 2026-09-10). G1 is closed and merged with
its candidate (`sizeHeavyTapSigma` 13.418 named, `sizeHeavyTapSigma2x` 10.3 fitted, four constants
declined); the independent review found two real defects in the heavy texture's lifetime (retained
after the width returned to 0; a tolerance compare that kept a stale texture at σ near 0), both
fixed with their tests before the merge. (g) is taken as a child of this wave rather than deferred:
**G1b**, a spike, recovers the reference's point spread non-parametrically (a radial profile fitted
jointly across every thick untinted probe backdrop of one surface at one scale), with the control
binding — the pipeline must reproduce vitrea's own known kernel's MTF within 10 % between 1/64 and
1/8 cycles per device px before it reads the reference. G2 is blocked on its verdict. On (f):
clause 2's "heavy σ within 15 %" is re-stated for this wave beside the original, not rewritten —
the thick body's kernel is compared to the reference's as an MTF over 1/64 → 1/8 cycles per device
px, identified by G1b's instrument, within 15 % at every band; a two-Gaussian σ is quoted only
with the backdrop it was read through. If G1b's control fails, the 1x width stays named at 13.418
and W26 lands the mechanism and the 2x width, with the identification carried as the next wave.

### Decision Log 5 — G1b's verdict: the shape is not identified, a width is, and it is half of what vitrea draws (2026-09-10; the parent; claims §5.121)

(a) **The instrument of record for the thick body's kernel is the family reader** — the composite
`wgsl/optics.ts` computes (the body vitrea draws, plus `heavyTapPlan`'s kernel for a heavy σ, at
a share), fitted to the PIXELS jointly across every thick untinted probe backdrop of one surface
(eight rows at 1x light), with a per-backdrop gain and a depth nuisance. It reproduces vitrea's own
drawn width to 0.6 % and its share to 0.043 where the drawn tap is in the family (every 1x row),
and reads 5–10 % narrow where it is a trilinear blend (2x); every reading of the reference moves by
under 6 % when any backdrop is dropped, the band moved or the raster tiled. The free forty-node
profile the brief asked for fails its control (half maximum off by 19–38 %, the second moment
11.8 → 28.4 under a dropped backdrop) — the SHAPE is not identified by this bed, a width is.
Two-Gaussian readers fitted to ONE backdrop are single-backdrop projections and are quoted from
here on only with the backdrop they were read through: §5.113 §2's 19.52 and §5.120's 2.74–2.79
sharp stand as recorded, beside 9.1 and 1.35–1.50.

(b) **The reading.** Apple's heavy width is 8.6–9.2 device px at 1x on both surfaces and both
schemes, and 8.7–9.6 at 2x after the family bias; the share 0.44 / 0.65 (1x) and 0.83 / 0.99 (2x)
against vitrea's 0.50 / 0.68 and 0.87 / 0.92 — every difference under 0.07. So: vitrea's 1x heavy
component (13.418, the chain's level 4) is about 50 % TOO WIDE, the direction G1 §7's
`checkerboard-64` gave; the share needs no lift, and W25's and W26's declines of the lift are
confirmed by measurement; at 2x the 96-span surface is right (7.96 against 7.92) and the 160-span
one is 36 % too wide because `sizeScatterGainFar2x` grades a width the reference barely grades.
Two Gaussians describe Apple's kernel within 0.05–0.12 of a display code of forty free parameters,
so Decision Log 4 (e)'s "not two Gaussians" is withdrawn beside its record. The reference's SHARP
component is 1.29–1.40 against vitrea's 1.64–1.75 (the body is the chain's level-1 kernel, 1.542,
plus a third of a texel — not a Gaussian of `blurSigma`): 20–30 % too wide, reversing §5.120 §3g.

(c) **G1's 2x fit is withdrawn beside its record.** `sizeHeavyTapSigma2x` 10.3 was fitted on
reader A's single-backdrop read of the impulse tile; the family reader wants about 8.7–9.6. The
candidate is re-fitted by **G1c** on the family reader: rendered rungs at 1x (σ 8 / 9 / 10 / 11 /
13.418) and 2x (σ 8 / 9 / 10 / 11), read on `rrect-md` and `rrect-lg` at both scales in the light
standard and `rrect-md` in the dark, each rung with the control (the drawn σ read back), the bed
cost at every rung with BOTH documents patched (Decision Log 4 (c)), X5, the fourteen floors, the
per-span ΔE, the goldens. The 2x span grading is read at the candidate: with the heavy texture in
place `scatterLod` no longer reaches the thick body, so `sizeScatterGainFar2x` is expected to fall
silent there — G1c states what it still grades and G2 declares whether it is retired.

(d) **What no convolution explains is recorded, not chased.** Every family, the free profile
included, leaves about one display code RMS of Apple's interior unexplained (1.79–2.01 against
0.83–1.17 on vitrea's; 3.22 on `hc-text`), with a displaced raster ruled out. A non-symmetric or
non-affine component; the tracker carries it as the bound on every width fitted on this bed.
Clause 2's re-statement in Decision Log 4 (h) is narrowed to what is identified: the heavy width
and the share on the family reader, within 15 % and 0.05, per surface per scale.

(e) **The sharp component is this wave's named gap, not its fit.** It is `blurSigma`'s body, the
thin capsule's own and X5-entangled (W25); recorded for the wave after this with the family
reader's number beside W25's.

### Decision Log 6 — G1c's candidate declared to G2: 9 and 9, the gain constants inert and kept, the holdout's contamination recorded (2026-09-10; the parent; claims §5.122)

(a) **The candidate is `sizeHeavyTapSigma` 9, `sizeHeavyTapSigma2x` 9**, every other constant at
0.14.0. The control held at every rung and closed at 2x (the heavy texture is a member of the
family, so the reader returns the named width: +0.2 % on 13.418, slope 0.995–1.111, rms ≤ 0.06
device px over seven rungs). The reference, re-read holdout-free (X3), asks 9.48 / 8.63 / 9.19 at
dpr 1 (spread 9.8 %, one number serves both spans within 15 %) and 8.13 / 9.79 / 8.37 at dpr 2
(spread 20.4 %: one number does NOT serve both spans; 9 is within 11 % of each). The objective
|log(read / reference)| 0.275 → 0.069 over six cells; the share unmoved (0.064 → 0.060); X5 worst
0.00021; the gate 38 / 38 with `PREDICATE_EXCLUDES` untouched; the light bed's thick spans improve
at every span at dpr 1 and two of three at dpr 2.

(b) **The three gain constants are inert at any material naming a heavy width and are KEPT this
wave**, their docs saying so: `sizeScatterGainMax`, `sizeScatterGainMax2x` and
`sizeScatterGainFar2x` feed only `scatterLod`, which the heavy texture overwrites on every group
whose source has a pyramid — fifty rows byte-identical between 9.9 and 4.8 at the candidate.
Retiring them means deciding what a profile that names NO heavy width draws (today: the chain at
`scatterLod`); that is a code-removal wave with no fidelity content and it is deferred to the
tracker rather than folded into a declaration. The 2x span grading they carried (1.66 device px
between spans 96 and 160) is the recorded gap of Decision Log 2 (f), now measured.

(c) **The mechanism has no small values, and the declaration says so.** A heavy σ of 0.001 builds
the texture at chain level 0 with no residual — the raw backdrop — so it is the opposite of "almost
off". The inert control is exactly 0; both anchors are declared at 9 and neither anchor may be a
small non-zero; the profile documents carry the sentence. Tracker: the constant's domain is 0 or at
least the chain's level-1 width, and a floor in `heavyTapPlan` would make it continuous.

(d) **The holdout's contamination is recorded.** G1b, a spike, read eight backdrops per surface and
three were holdout scenes (`checkerboard__rrect-lg`, `hc-text__rrect-md`, `photo__rrect-lg`); it
fitted nothing, but its instrument was validated on them. G1c dropped them from every reading, so
the candidate is fitted holdout-free and G2's once-read of the holdout stands as the check of the
FIT. It is not an untouched check of the INSTRUMENT, and clause 6 is read with that sentence beside
it. `glass-over-glass` is holdout-only, so W25 clause 3 is read at G2's holdout read and nowhere
else.

(e) **The dark bed worsens on a candidate its own reference asks for** (1x dark span 128
0.01703 → 0.01892, 160 0.02173 → 0.02404; the dark reference reads 9.15 / 7.80). The 13.418 was
masking something in the dark scheme whose thick-span error is three times the light bed's before
and after; not a reason to move the width; tracker. W25 clause 4 (the collapsed dot, 6.167 CSS px
against 4.04 / 4.26) is not met at the control either, so the candidate neither meets nor regresses
it; carried.

(f) **G2 declares**: the two constants in the code default and the light patch, the fingerprints
re-recorded, the CSS tier's `blur()` derived from the heavy width where the width is one number
(clause 7; `platform-web/src/optics.ts` reads the gain constants today), `W26_HASHES` behind the
isolation proof, the stops (W25 G3's set; S15 as re-stated in Decision Log 4 (a), on the family
reader), the dry run of the frozen bed and the probe set to scratch, the holdout once, the sheets;
`PREDICATE_EXCLUDES` equal to the machine's output.

### Decision Log 7 — G2's read: the width lands on the GPU tier, clause 7 costs twelve floors, and the two are separable (2026-09-10; claims §5.123 DRAFT)

DRAFT, by G2. The parent rules (a)–(d) and amends beside; G3 lands whatever survives.

(a) **The two constants are right and the GPU tier says so quietly.** 9 and 9, declared before the
run at `6f901f0`, fingerprints b2b570e4adcea8fb and eee7294f409966d7 computed before the edit and
reproduced after it. S15 fires on exactly the two cells the declaration named in advance and the
objective falls 0.275 → 0.069; the canonical bed's GPU groups do not move by as much as 0.00001;
W24's angular bins are identical to five decimals on every GPU row; the 22 GPU captures that hold
byte for byte are exactly the flat-solid backdrops; X5 is a fifth of its bound on both tiers; the
goldens move on seven scenes by 1–3 codes and **not one pixel off a surface**. The per-span probe
table reproduces claims §5.122 §5c to the digit, which is the check that the landing draws what the
rung drew.

(b) **Clause 7 is where the cost is, and it is twelve of the fourteen thick floors.** Deriving the
CSS tier's heavy layer from the profile's own width takes it 13.800 → 9.000 CSS px at dpr 1 and
6.121 → 4.500 at dpr 2 on a 160 span, and the six large-span `dom` `ssimMean` floors and the six
dark nested-pane `dom` rows all go under; four of those cells leave the shape gate besides. **The
counterfactual is measured rather than argued** (claims §5.123 §5): the two tiers render
independently and the constants reach the CSS tier only through clause 7's code, so the bed a
landing without it would produce is this run's texture rows beside the 0.14.0 bed's dom rows — and
it breaches **one** floor instead of thirteen. The one that survives either way is the GPU tier's own
dark nested pane, on a cell whose web silhouette already carried 39 holes against a native 0.

(c) **The choice, and why it is not this child's.** Landing both gives the two tiers one heavy width
for the first time and asks the user to re-pin twelve floors that already miss their adopted bounds
and are held by decision. Declining clause 7 costs one floor and leaves the CSS tier deriving its
heavy width from three constants that grade nothing on the tier it has to agree with — an
incoherence to record and charter rather than to hide. Re-opening the width is contradicted by (a).
**The holdout was read once at the configuration WITH clause 7** and a ruling that declines it voids
that read.

(d) **Two things the run measured that nobody declared, and both are the same shape.** A heavy width
named in device px does not inherit the rules a multiple of `blurSigma` inherited for free. Under
`frost: "none"` it would have gone on frosting a surface the preference asked not to frost, and the
gate for that is in the code with its test. Under `frost: "increased"` it no longer widens at all —
on EITHER tier, and before this wave the GPU tier could not widen there either because `scatterLod`
was clamped, so the mirror was drawing 24.15 CSS px where the renderer drew 13.418. The tiers agree
now and the reduced-transparency CSS capsule leaves the shape gate for it (`silhouetteHolesWeb`
0 → 6); `PREDICATE_EXCLUDES` is edited 31 → 32 for that cell with the mechanism written into it.
**Whether the accessibility fold should reach the heavy width is a material question this wave did
not declare and did not fit**, and it is the tracker's.

(e) **The independent review found the other half of (d)'s first sentence, and it is fixed with its
test.** The gate written for `frost: "none"` was on the CSS tier only, and it fires on a base σ of 0
from ANY cause — including `optics.regular.blurSigma` 0, which is a supported material override. On
that material the two tiers drew different pictures: the mirror drew nothing and the renderer drew
an unblurred body with a 9 device px deep sample mixed into it, because the heavy texture is keyed
on the material's width and read no variant's optics. `heavySigmaCssFor` now takes the source's own
body σ and returns 0 where it is 0, `heavy-width.test.ts` pins it, and the doc comments on both
tiers say the rule once each. **No capture moves**: every profile on the bed names `blurSigma` 1.25,
and on the shipped accessibility path the case is unreachable rather than merely unused — core
couples `frost: "none"` to `glass: "none"` and the renderer disconnects backdrop sampling entirely.
The goldens are 33 / 33 unmoved after it. The review found nothing else: the device-px-over-ratio
conversion is right, no sampling-padding starvation is introduced, and the recorded-snapshot
normaliser is covered by the case that walks every field.

## Surprises & Discoveries

- **A scratch rung is not a rehearsal of a landing.** The dark difference document resolves over
  `DEFAULT_MATERIAL_PROFILE`, not over the light patch, so a rung that patches the light document
  alone renders the dark scheme at the CODE defaults — which for a wave's new constants is inert.
  Every dark reading taken that way measures the old material, and the tell is that it moves by
  exactly zero.
- **The reference's heavy component is not one number.** Read through the impulse tile it is 19.5
  device px at 1x; read through `checkerboard-64` it is 8.4; a joint fit across both says 9.4 and
  under-reads vitrea's KNOWN kernel by a fifth. Apple's kernel is not two Gaussians, and a
  two-Gaussian reader recovers whichever two the backdrop weights — which means a wave can fit a
  constant to a target that does not exist.
- **The control nobody built.** Vitrea's own drawn kernel is known exactly at the inert default
  (the chain's level 4, half-maximum σ 13.42), so every reader could have been calibrated against a
  ground truth at any point since W24. Doing it for the first time here put a ±10-40 % bias on each
  instrument and turned an argument between readers into a measurement.
- **The impulse fixture's own dynamic range is the wall at 1x, not the reader.** W26 G0 read reader
  A's half-pitch window as the cause of the unreadable 1x ladder. G1 built the window away and found
  the fixture underneath it: the 1x `impulse` interior carries about one 8-bit code of modulation in
  total, and the heavy component's share of that is a fraction of a code. Every "the reader parks on
  its bound" reading in this wave and in W25 inherits that, and so does the reference's own 19.52.
- **Reader A's fitted SHARP component is a conditioning statistic and nobody had read it as one.**
  Where it comes back at 9–12 device px the two-component fit has split one wide kernel in half and
  the "heavy" it reports is not a component. That is what the reference's 2x `-ml` and `-lg` rows do.
- **Naming the chain's own width is byte-identical.** `heavyTapPlan` at `CHAIN_LEVEL_SIGMA[4]` picks
  level 4 with a residual of exactly zero, and the separable pair then reproduces the chain tap it
  replaces to the bit — so the mechanism can take over the 1x width at literally no cost, which is
  what makes the ramp between the two scale anchors safe to close.
- **The candidate CONDITIONS two cells the frozen bed excludes.** `checkerboard__rrect-md` and
  `checkerboard__toolbar-group` on `apple-macos-26.5-2x-light-standard` enter the shape gate at the
  candidate and meet its bounds. A fidelity change moving `PREDICATE_EXCLUDES` is usually a cell
  falling out; this one is two falling in.
- **The gain was never a width.** `bodyChainLod + log2(8)` = 4.0589 against a `chainMaxLod` of 4:
  the material has been clamped since W11c fitted it, and W15 G1's 2x re-form fitted two more
  constants (`sizeScatterGainMax2x`, `sizeScatterGainFar2x`) onto the same axis. They were fitted
  on a real objective and they moved it — at dpr 2, where the chain is a level deeper and the clamp
  does not bite. What the ledger read as a material law is partly a property of the backdrop
  raster's size, and a larger backdrop would give the same profile a different heavy width.
- **`CHAIN_SIGMA_AT_LEVEL_1` is 24 % low.** The simulated chain reads 1.570 texels at level 1, not
  1.2. It is declared advisory and the body blur's residual pass absorbs it, so nothing is wrong —
  but every "the chain's blur is about σ" statement in the codebase inherits it.
- **Reader A's per-row spread at one known width is ±40 % and its median is exact.** At the 0.14.0
  material the three 1x impulse rows read 9.08 / 14.36 / 19.78 for a drawn kernel of 13.42; the
  median is right to 7 %. Any per-row acceptance on this reader at 1x is reading the instrument.

## Outcomes & Retrospective

(at recomposition)

## Revision Notes

- 2026-09-10: chartered; G0 dispatched.
- 2026-09-10: G0 CLOSED (claims §5.119). Three candidates merged inert, the goldens and the bed's
  36 rows byte-identical at the defaults; Decision Log 2 records the verdict and re-states clause 1
  onto the 2x rows. G1 ready.
- 2026-09-10: the parent's ruling appended as Decision Log 2 (f); G1's section re-stated in three
  parts (the structural tap, the lattice reader, the fits) with the original line kept beneath.
  G1 dispatched.
- 2026-09-10: G1 DELIVERED (claims §5.120 DRAFT). The structural tap accepted at 0.0 % against the
  grid and +0.180 ms against the control; the lattice reader validated and the 1x fixture measured as
  the wall; the 2x width, the 1x anchor and the 1x share fitted, three constants declined, the bed's
  fourteen floors and every bound passing. Decision Log 3 records the read and leaves two rulings —
  S15 on the 2x `-lg` row, and whether the 1x share lift's off-row cost is acceptable — to the
  parent.
- 2026-09-10: the parent's rulings recorded as Decision Log 4 (a) and (b); G1 §7 delivered on the
  follow-on. `checkerboard-64` reads the 1x width where the impulse fixture cannot, and the fit is
  still declined because the reference's 1x heavy component is not identified — a factor of 3 between
  instruments after each is debiased against vitrea's own known kernel. The dark bed re-captured with
  the candidate in both documents. The candidate is unchanged.
- 2026-09-10: G1 CLOSED and merged (`d306214`); the review's two lifetime defects fixed at
  `d06fe3c`. Decision Log 4 (h): G1b (the kernel identified without a shape assumption, a spike
  with a binding control) dispatched ahead of G2; clause 2 re-stated beside the original as an MTF
  match.
- 2026-09-10: G1b CLOSED and merged (`1d541bf`). Decision Log 5: the family reader is the
  instrument of record; Apple's heavy width 8.6–9.2 / 8.7–9.6 device px, vitrea's 1x half again too
  wide; the share right; the sharp component reversed; G1's 2x fit withdrawn beside its record;
  G1c dispatched to re-fit both widths; clause 2 narrowed to the identified quantities.
- 2026-09-10: G1c CLOSED and merged (`5a710ad`). Decision Log 6: the candidate 9 / 9 declared to
  G2; the gain constants inert and kept; the mechanism's no-small-values wart, the holdout's
  contamination by G1b's instrument, and the dark bed's preference recorded. G2 dispatched.
- 2026-09-10: G2 DELIVERED (claims §5.123 DRAFT). The declaration committed before the run
  (`6f901f0`), the two constants landed on both documents and both tiers, the goldens re-recorded
  behind their attribution under `W26_HASHES`, and the bed, the probe set and the holdout run to
  scratch. The width lands: S15 fires on exactly the two cells the declaration named, the objective
  falls 0.275 → 0.069, the GPU tier's canonical groups do not move by 0.00001 and X5 is a fifth of
  its bound on both tiers. Clause 7 is the cost: **thirteen of the fourteen thick floors are
  breached and twelve are `dom` rows**, and the counterfactual measures the split at **1 against
  13**. Decision Log 7 leaves the choice to the parent and records two undeclared findings about the
  accessibility fold and a heavy width named in device px.

### Decision Log 7 (f) — the parent's ruling on §10, and G2b (2026-09-10; the parent; claims §5.123 §9)

Appended beside (a)–(e), which stand as G2 drafted them.

**Option 2 of claims §5.123 §7 / `g2-dryrun.md` §10 is taken.** The two constants land on the GPU
tier; **clause 7's CSS derivation is DECLINED this wave**, on the measurement and on the eye: twelve
dom floors against one, two of them the user's own W24 re-pins, and at 1x dark the CSS tier at
clause 7 shows the checkerboard straight through the nested pane's inner glass where neither the
native capture nor the GPU candidate does. Clause 7 asks the CSS tier to derive what it CAN; on this
evidence it cannot carry this one yet.

**What that leaves, and it is a gap to macOS recorded rather than hidden.** The CSS tier goes on
deriving its heavy layer from `sizeScatterGainMax` / `…Max2x` / `…GainFar2x`, which the GPU tier no
longer reads (Decision Log 6 (b)) — so the two tiers' heavy widths are different numbers as of this
wave, by 53 % at dpr 1 and 36 % on a 160 span at dpr 2. It is the X residual of W26, it is pinned as
a number by `tier-coherence.test.ts` rather than left as prose, and the tracker carries the charter:
the wave that closes it has to answer why a two-layer body at the CORRECT component widths loses
structure the mip-tap projection kept.

**G2b re-ran the ruled configuration rather than inferring it** (`g2-dryrun.md` §14). The CSS tier is
byte-identical to 0.14.0 at the LANDED documents — 640 of 644 captures, the four movers each measured
as run-to-run noise — which had to be rendered because the documents now name two constants the
mirror no longer reads. The GPU tier is unmoved by the revert on a 72-capture sample. The gate reads
35 of 38 against 30, the fourteen floors 1 breached against 13, every CSS group unchanged to five
decimals and every GPU group W26 G2's own reading; S3 is clear on every group of both tiers.
`PREDICATE_EXCLUDES` reads 32 with a DIFFERENT cell entering than at the rejected configuration, and
is described rather than committed against the wrong matrix, as before.

**The one floor that remains is the extractor and the numbers are one-sided.** On
`checkerboard__glass-over-glass` at 2x dark the pane's interior level moves 0.11419 → 0.11418 and its
standard deviation 0.24677 → 0.24685; the picture moves by a mean of 0.19 of an 8-bit code. What
moves is a threshold population: 21 290 pixels sit within 0.005 of a 0.02 luminance-delta probe and
2 640 cross under it with none coming back — **toward the native**, whose own under-threshold count
(17 010) is above the candidate's (16 970) and well above 0.14.0's (14 330). The harness nevertheless
recovers a hole-free mask from that native, so its rule does more than threshold and the asymmetry —
not the material — is what a fix would go after. **The floor is the user's to re-pin or the next
wave's to fix**; this records the number and the picture and recommends neither.
- 2026-09-10: the parent's ruling recorded as Decision Log 7 (f) and executed as G2b. Option 2:
  the two constants land, clause 7 is declined, and the CSS tier is proved byte-identical to 0.14.0
  at the landed documents (640 of 644, the four movers run-to-run noise). The gate 35 of 38, the
  fourteen floors 1 breached against 13, every CSS group unchanged to five decimals, the goldens
  unmoved by hash. The tier gap is pinned as a number in `tier-coherence.test.ts` and chartered in
  the tracker. The one remaining floor is measured to be the extractor and is left to the user.
