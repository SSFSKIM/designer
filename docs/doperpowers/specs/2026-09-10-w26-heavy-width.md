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

## Tracking Map

| child | status |
| --- | --- |
| G0 — the heavy tap as a parameter | CLOSED 2026-09-10 (claims §5.119) |
| G1 — the width, the share, the lever, the level | DELIVERED 2026-09-10 (claims §5.120 DRAFT; Decision Log 3 DRAFT — two rulings open) |
| G2 — declared and dry-run | — |
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

## Surprises & Discoveries

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
