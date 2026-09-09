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

- The width per scale on the probe set's impulse rows and coarse checkerboards; the share per
  scale on the same rows, checked off them on the checkerboards' single-width objective; the 2x
  headroom; the level re-read; each with its condition; the thin cells at every rung.
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

- The rim's arc amplitude as a three-term joint fit (W23's law, W24's exponent, W25's field).
- The size-keyed light adaptation of a small surface over a bright backdrop in the dark scheme.
- The contour instrument's refusal on flat-cornered dark squares; the 2x reference's run-to-run
  instability; the demo page's coupling to `scenes.json` (tracker).

## Tracking Map

| child | status |
| --- | --- |
| G0 — the heavy tap as a parameter | CLOSED 2026-09-10 (claims §5.119) |
| G1 — the width, the share, the lever, the level | READY (Decision Log 2) |
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

## Surprises & Discoveries

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
