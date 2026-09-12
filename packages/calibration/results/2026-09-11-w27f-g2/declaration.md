# W27f G2 — the native stack bound, declared before the read (2026-09-11)

Executes W27's child W27f G2 (`docs/doperpowers/specs/2026-09-10-w27-coverage-wave.md`, §Children),
the §Design clause *Page content on the WebGPU tier gets the material, not a flat* (binding),
Decision Log 3 and 12, and contracts X1 and X2. It consumes claims §5.129 (G0) and §5.131 (G1)
and adopts nothing until the read below has been taken.

**This file is committed before any capture of this gate is run.** Everything in §§1–5 is written
from numbers already published in claims §5.131 §6 and from `apps/reference-apple/scenes.json`.
No capture, no server and no harness run precedes it. What §6 declares as a stop is what stops the
landing; a bound is not re-interpreted after it is declared (the wave's own rule, Decision Log 13).

Head: `8cf6a89` (`main`). The child was dispatched against `2b47bda`; `8cf6a89` is
`2b47bda` plus one documentation-only commit (W27 Decision Log 13, 26 lines of
`2026-09-10-w27-coverage-wave.md`), so the runtime, the profiles, the fixtures and `scenes.json`
at this head are `2b47bda`'s exactly.

## 0. A correction to this gate's premise, before it is used

The dispatch described the two stack cells as calibration cells. They are not. In
`apps/reference-apple/scenes.json` the `split.holdout` list carries
`checkerboard__glass-over-glass__rest` and `photo__glass-over-glass__rest` (together with their
`__inactive` twins, which this gate does not touch). Claims §5.129 already called them "the two
explicitly requested stack **holdout** cells", and §5.131 §7 spent the whole ten-scene holdout
once on candidate `1fff5e6`.

So this gate re-reads two cells of a spent holdout. It is taken deliberately, and the reasons are
recorded here rather than discovered afterwards:

1. **G2 fits nothing.** No constant, profile document, fixture, scene or material moves in this
   gate. The rule that holdout is read once per frozen configuration exists so that holdout cannot
   steer a fit. A gate whose only two outcomes are *adopt the declared bound as a floor* or *adopt
   nothing and stop* has no fit for it to steer.
2. **The bound is published before the read**, in this file, from numbers §5.131 §6 already
   printed. No reading taken by this gate can change what passing means.
3. **The read is of the same frozen material configuration** §5.131 spent, at a later head. That
   claim is not assumed: §7 below makes it a stop, checked on the `gpu-texture` digests of
   §5.131 §8 and the renderer goldens, neither of which is a stack cell, so the check is not
   circular. If it fails, the read is a different configuration and this gate stops.
4. **The other eight holdout scenes are not read.** Only the two stack cells and the 20 ordinary
   *calibration* scenes are captured.

Consequence, recorded so the next worker finds it rather than rediscovers it: after this gate the
two stack cells have been read twice on this material configuration. Any later work that would fit
anything on the stack path must treat them as spent and re-freeze the bed.

## 1. What the native evidence is, and where it stops

The two stack overlays are the only native cells on this bed that exercise the composed-glass
analogue of a `css-backdrop` group (§5.129 X8). Three of the four scheme × stack cells have a
native fixture; one does not:

| scheme / stack | native fixture |
| --- | --- |
| light checker | `apple-macos-26.5-1x-light-standard/checkerboard__glass-over-glass__rest.png` |
| light photo | `apple-macos-26.5-1x-light-standard/photo__glass-over-glass__rest.png` |
| dark checker | `apple-macos-26.5-1x-dark-standard/checkerboard__glass-over-glass__rest.png` |
| **dark photo** | **none — `apple-macos-26.5-1x-dark-standard` carries no `photo__glass-over-glass`** |

**The dark photo stack is therefore unbounded by this gate**, and nothing about it is adopted.
§5.131 §6 reports it against `S*`, each configuration's own textured-base composite — an identity,
not native fidelity — and §6 says so. No native reading for that cell is inferred, interpolated
from the light photo stack, or substituted from the dark checker stack. Closing it needs a native
`photo__glass-over-glass` capture in the dark scheme, which does not exist and which this gate does
not create.

## 2. The three configurations, kept apart

Every stack overlay resolves `css-backdrop`, `approximate`, `analysis: none` in every
configuration; only the pixels beneath it differ. §5.131 §6 keeps three composites separate and so
does this gate:

- **S0** — the old textured-base composite: a sampled texture base under the *pre-G1* overlay
  material (the flat white `tint [1,1,1]` at α 0.665 of §5.77 §4 / §5.129 §3). S0 is **history**.
  The material that produced it is gone from the runtime, so S0 cannot be re-measured at this head;
  it enters the bound only as the frozen reading §5.131 §6 published.
- **S1** — the new textured-base composite: the same sampled texture base under G1's derived
  overlay material. S1 is measurable at this head and will be measured.
- **Uh** — the page path this wave is landing: a DOM-sourced base at its measured backdrop level,
  under the same derived overlay material.

S0 and S1 are not byte-identical and neither is a native bound (§5.131 §6). They are not pooled,
averaged, or reduced to one number anywhere below.

**U0**, the unhinted DOM page base, is *not* in the bound. §5.131 §6 records its light overlay rim
excess as **−0.065296 / −0.059579** against native **+0.111642 / +0.084228** — an inverted local
contrast — and its dark overlay luminance as **0.049707 / 0.050100** against native **0.020698**.
The unknown-tone case is an information limit (§5.129 §2, §5.131 §1), not a coefficient error, and
this gate adopts no floor over it. It is captured and recorded so the limit stays visible; it is
never presented as bounded.

## 3. The tables the bound is taken from

Reproduced from claims §5.131 §6 so the arithmetic below can be checked without leaving this file.

**(a) Overlay eroded interior, linear luminance** (not OKLab L):

| scheme / stack | native | S0 | S1 | Uh |
| --- | ---: | ---: | ---: | ---: |
| light checker | 0.904655 | 0.890113 | 0.895571 | 0.896252 |
| light photo | 0.893533 | 0.873339 | 0.880533 | 0.886175 |
| dark checker | 0.020698 | 0.023909 | 0.024857 | 0.023673 |
| dark photo | — | 0.021413 | 0.021612 | 0.021984 |

**(b) Overlay-local OKLab ΔE against native, and rim local excess:**

| scheme / stack | S0 ΔE | S1 ΔE | Uh ΔE | native rim | S0 rim | S1 rim | Uh rim |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| light checker | 0.007735 | 0.005438 | 0.004662 | 0.111642 | 0.042743 | 0.111347 | 0.109977 |
| light photo | 0.019478 | 0.018619 | 0.009126 | 0.084228 | 0.047788 | 0.114151 | 0.109090 |
| dark checker | 0.013765 | 0.016702 | 0.013059 | 0.031990 | 0.035140 | 0.037864 | 0.036194 |
| dark photo | — | — | — | — | 0.032367 | 0.033665 | 0.033604 |

**(c) Whole-declared-footprint ΔE** (base *and* overlay; recorded, not bounded — see §5):

| scheme / stack | ref | S0 | S1 | Uh |
| --- | --- | ---: | ---: | ---: |
| light checker | N | 0.00989 | 0.00935 | 0.02151 |
| light photo | N | 0.04260 | 0.04240 | 0.01784 |
| dark checker | N | 0.01510 | 0.01578 | 0.02185 |
| dark photo | S* | 0.00000 | 0.00000 | 0.01346 |

## 4. The native stack envelope, per scheme × stack, S0 and S1 separately

The envelope is the interval the *composed-glass path over a real sampled base* has actually
occupied against native on this bed. Its two endpoints are S0 and S1 — the only two measured
readings of that kind — and they stay distinct. Distances to native, computed from §3:

| scheme / stack | metric | native | S0 error | S1 error | envelope [min, max] |
| --- | --- | ---: | ---: | ---: | --- |
| light checker | overlay ΔE | 0 | 0.007735 | 0.005438 | [0.005438, **0.007735**] |
| light checker | overlay luminance | 0.904655 | 0.014542 | 0.009084 | [0.009084, **0.014542**] |
| light checker | overlay rim excess | 0.111642 | 0.068899 | 0.000295 | [0.000295, **0.068899**] |
| light photo | overlay ΔE | 0 | 0.019478 | 0.018619 | [0.018619, **0.019478**] |
| light photo | overlay luminance | 0.893533 | 0.020194 | 0.013000 | [0.013000, **0.020194**] |
| light photo | overlay rim excess | 0.084228 | 0.036440 | 0.029923 | [0.029923, **0.036440**] |
| dark checker | overlay ΔE | 0 | 0.013765 | 0.016702 | [0.013765, **0.016702**] |
| dark checker | overlay luminance | 0.020698 | 0.003211 | 0.004159 | [0.003211, **0.004159**] |
| dark checker | overlay rim excess | 0.031990 | 0.003150 | 0.005874 | [0.003150, **0.005874**] |
| dark photo | — | — | — | — | **no envelope: no native fixture** |

**Clause A — the envelope clause.** On each of the nine rows above, the DOM-base hinted overlay's
distance to native must be **at or inside the envelope's upper endpoint**:

| scheme / stack | overlay ΔE ≤ | overlay luminance error ≤ | overlay rim error ≤ |
| --- | ---: | ---: | ---: |
| light checker | 0.007735 (S0) | 0.014542 (S0) | 0.068899 (S0) |
| light photo | 0.019478 (S0) | 0.020194 (S0) | 0.036440 (S0) |
| dark checker | 0.016702 (S1) | 0.004159 (S1) | 0.005874 (S1) |
| dark photo | — | — | — |

The reason is the wave's own claim, not a convenience: the overlay is `css-backdrop` in every
configuration, so the only thing the page path changes for it is the pixels underneath. If a DOM
base costs the overlay more than the two textured-base configurations differ from native
themselves, the page path is not carrying the material and W27f has not landed on a stack.

The clause is not vacuous. The pre-G1 unhinted page fails it on every scheme: light checker rim
error **0.176938** against a 0.068899 bound, dark checker luminance error **0.029009** against
0.004159. The pre-G1 *hinted* page fails it too, on light checker luminance — its overlay sat at
0.866897, an error of **0.037758** against the same 0.014542.

**Clause A is weak on exactly one row, and that is named rather than smoothed.** On dark checker
the upper endpoint is S1's, and S1 is itself a regression (§5). Taking the upper endpoint there
would let the new material be bounded by its own regression. Clause B is what carries that cell.

**Clause B — the no-widening pin.** Independently of Clause A, no overlay reading at this head may
be **worse than the value §5.131 §6 recorded** for the same configuration and metric. Twelve
readings are pinned: S1 and Uh, on overlay ΔE, overlay luminance error and overlay rim error, on
the three cells with a native fixture. The pinned values are §3's, to their printed precision. A
reading that comes back better is reported as better and the floor is adopted at the **read** value,
never at the recorded one. A reading that comes back worse is a stop (§6).

The bound this gate would adopt is **Clause A ∧ Clause B**: the envelope is the reason G1's
measured position is adoptable at all, and the pin is the requirement that the landing head is
actually at that position.

---

**Note written after the read (2026-09-12, in review of the landing).** Everything above this line
is the declaration as committed before any capture ran and is not edited. What the read and an
independent review of it showed the declared text to mean, recorded here rather than by changing
it:

1. **Clause A is subsumed by Clause B on all nine rows, not weak on one.** The paragraph above
   names dark checker as the single weak row. Compare the two clauses row by row and Clause B's pin
   is strictly tighter than Clause A's cap on *every* one of the nine: 0.004662 against 0.007735,
   0.008403 against 0.014542, 0.001665 against 0.068899, 0.009126 against 0.019478, 0.007358
   against 0.020194, 0.024862 against 0.036440, 0.013059 against 0.016702, 0.002975 against
   0.004159, 0.004204 against 0.005874. B ⟹ A, so S1 cannot fire without S2 having fired first, and
   the conjunction's operative half is Clause B alone. This is not a defect in the declaration's
   reasoning; it follows from the fact that Uh's recorded position is already better than both
   textured-base composites on every metric of every cell. Clause A's rationale stands and is why
   the pinned position is adoptable at all rather than merely reproducible — but it does no
   stopping work, and on dark checker the cell is *frozen at its regressed value* by Clause B, not
   bounded by anything.
2. **Clause B pins eighteen readings, not twelve.** Two arms (S1 and Uh) × three metrics × the
   three cells with a native fixture is eighteen. `verdict.py` evaluates eighteen pins and §2's
   table above prints eighteen; "twelve" here and in §6's S2 is an arithmetic slip in the prose,
   not in the clause.
3. **The non-vacuity example in the paragraph above cites the wrong arm.** 0.176938 is the rim
   error of the unhinted arm U0 *at the landing head*, not of the pre-G1 page: it is
   |0.111642 − (−0.065296)|. The genuine pre-G1 U0, in `2026-09-10-w27f-g0-unsampled.json`, has rim
   +0.058576 on light checker, an error of 0.053065, which **passes** the 0.068899 bound. Pre-G1 U0
   does fail Clause A on that cell's other two metrics — ΔE 0.008603 against 0.007735 and luminance
   0.020019 against 0.014542 — and the 0.029009 dark checker luminance figure is U0's at the
   landing head. The clause is not vacuous; the attribution was wrong. Claims §5.135 §1 carries the
   corrected list with each figure's arm and head named.
4. **The rounding convention this file works in.** Every error in §4 is a difference of §3's
   already-six-decimal values — a difference of rounded numbers, not a rounded difference — so that
   the arithmetic can be checked against claims §5.131 §6 without opening a capture. Seven figures
   therefore sit one ulp from the raw difference: 0.068899 (raw 0.068898), 0.176938 (0.176937),
   0.002937 (0.002936), 0.001727 (0.001726), 0.001665 (0.001664), 0.007358 (0.007357) and 0.002613
   (raw 0.002614). Re-evaluating every clause on the raw readings flips no verdict; the narrowest
   Clause A margin is dark checker luminance at 0.001184.

## 5. The regressions §5.131 §6 records, confronted

Two are named in §5.131 §6's prose, and both are in the **dark checker** cell. (The dispatch brief
attributed the first of them to the light checker; §5.131 §6 reads "The dark checker hinted overlay
**regresses 0.011332 → 0.013059**", and the light checker's hinted overlay improved. The ledger's
attribution is the one used here.)

1. **The hinted DOM overlay, dark checker: 0.011332 → 0.013059 overlay ΔE.** The pre-G1 overlay
   material, over a hinted DOM base, was **0.001727 closer to Apple's overlay** than G1's derived
   material is. The whole footprint improved over the same change (0.02477 → 0.02185) because the
   base improved; §5.131 §6 states that neither regression may disappear behind the base's larger
   footprint, and the bound above is stated only on overlay-local metrics for that reason. The
   same cell's overlay luminance error also widened, 0.002613 → 0.002975.
2. **The textured-base overlay, dark checker: 0.013765 → 0.016702 overlay ΔE (S0 → S1).** The same
   material change, measured over a real texture base, is worse by **0.002937**.

Neither is closed by this gate, and neither is averaged against the light scheme's repair (light
checker overlay ΔE 0.007735 → 0.005438, light photo 0.019478 → 0.018619, and both light hinted
overlays improving on §5.129's 0.015833 / 0.020678). What this gate does with them:

- It **pins them at their recorded magnitudes** (Clause B) so they cannot grow unobserved.
- It **records them as open gaps** in the claims section, not as accepted parity: the dark scheme's
  derived overlay material is measurably further from Apple's overlay than the flat it replaced,
  on the one dark cell that has a native fixture.
- It does **not** fit anything to repair them. A material change is a fidelity change with its own
  declared stop and belongs to a gate chartered for it. G2 is a landing gate.

A third regression is recorded but not bounded: light photo's overlay **rim overshoots** native in
both textured and DOM configurations (S1 0.114151 and Uh 0.109090 against native 0.084228, where
S0 undershot at 0.047788). It sits inside Clause A's envelope because S0's undershoot was larger,
which is precisely why it is written down here as well as passing.

## 6. What stops the landing

Any one of these is a stop. On a stop this gate **adopts nothing**, records the miss with its
evidence, and ends. It does not re-fit, re-capture to a better number, narrow a clause, exclude a
cell, or reinterpret the envelope.

- **S1 — the envelope.** Any of Clause A's nine rows fails.
- **S2 — the pin.** Any of Clause B's twelve readings is worse than §5.131 §6's record.
- **S3 — the sampled path moved.** Any ordinary `gpu-texture` cell's PNG digest differs from
  §5.131 §8's record (20/20 sampled and 20/20 same-hint sampled in each scheme), or the renderer
  golden/isolation suite is not green with nothing re-recorded.
- **S4 — the instrument.** Any capture is not byte-repeatable over its two loads, or any capture
  reports a diagnostic.
- **S5 — the route.** Any DOM arm resolves to something other than `webgpu` / `css-backdrop` /
  `approximate` / `analysis: none`, or the WebGPU adapter reports `isFallbackAdapter: true`.

**Note written after the read (2026-09-12).** S2's "twelve readings" is eighteen, for the reason
§4's note gives; the clause itself is unchanged, and nothing in it was decided by the count. S4 as
worded above was tripped by the read and is **not** resolved by this gate — see claims §5.135 §6.

## 7. What will be read, and what is recorded but not bounded

**Read at this head, WebGPU tier, 1x, both schemes** (`apple-macos-26.5-1x-light-standard` and
`apple-macos-26.5-1x-dark-standard`, profile documents unchanged: light `6a9600720477` / resolved
`b2b570e4adcea8fb`, dark `950ce1c3e917` / resolved `874be66ea501621b`):

- the two stack cells on the S1, U0 and Uh arms;
- the 20 ordinary calibration scenes on the sampled-today, U0 and Uh arms — sampled-today for S3's
  digest identity, U0 and Uh to reproduce §5.131 §5's per-scene table at the landing head;
- the CSS tier's counterpart arms on the same cells, for the coherence record only.

Captures and matrices go to scratch (`--out-matrix` and `VITREA_WEB_CAPTURES`). The canonical
`results/matrix.json` is written **only if** Clause A ∧ Clause B holds, appended by the profile-SHA
key as the repository's own rule describes, never rebuilt from empty. The capture server does not
use port 5189: another worker is on this machine's native path (W27 Revision Note, 2026-09-11) and
a collision on that port is already in the tracker.

**Recorded, never bounded:**

- **The dark photo stack** (§1): no native fixture, no envelope, no floor, no inferred native value.
- **The CSS tier** (X1): every CSS reading on DOM-sourced groups is a coherence record. It is never
  a CSS target and never a CSS floor.
- **The whole-footprint ΔE on the DOM stack** (§3c): its base is the unsampled page material, whose
  residual is §5.131 §5's ordinary-scene finding, not a stack finding. It is reported and held to
  Clause B's no-widening rule; no native whole-footprint bound is adopted on it.
- **The unhinted page arm U0** (§2): captured and reported, outside the bound.

## 8. The eye

The eye sheet prepared by this gate puts, for each stack and page cell: the native fixture where
one exists, the sampled path, the DOM path at this head, and the demo's `/#page` stage captured in
full Chromium on a real adapter. **The user's eye is taken by the parent, not by this gate**, and
no acceptance of `/#page` is claimed here. §5.131 §6 names what the sheet exists to show: the
stronger light overlay rim, the photo base's colour difference, and the dark unhinted overlay's
brightness.

## 9. What this gate may not do

No change to the material, the profile documents, the fixtures or `scenes.json`. No golden
re-recorded. The only files it may write are its own evidence under
`packages/calibration/results/2026-09-11-w27f-g2/`, the claims section, this wave's Status line and
tracking row, and — only if the bound holds — the floor in
`packages/calibration/test/adopted-thresholds.test.ts` and the appended canonical matrix rows.
