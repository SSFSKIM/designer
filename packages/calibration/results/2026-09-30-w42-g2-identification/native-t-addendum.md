# W42 G2 — pre-read addendum: native T between span strata and across a sparse stratum (2026-09-30)

**Status: written and committed before any family-A pixel is read (G1's sitting is still
capturing; its archive is unpublished). For the parent's review before G2 step 2 starts.** It adds
no family, no parameter and no bed cell. It closes a silence in the declared path that both
identification and candidate 2 would otherwise have to fill after reading family A, which is the
order X23 and clause 1 forbid. The parent's ruling on Fork 3 of `implementation-design.md` asked
for it.

## 1. The declared path is silent on both rules

- The declaration's `nativeT` defines native T **per endpoint and span stratum** as "the monotone
  piecewise-linear curve through family A's measured ordinates (`tone.TableT`)", with the strata
  t = 0 (every s ≤ 64, read on the capsule), s = 80 (dark), 96, 128 and 160, and one trust clause:
  an input above a stratum's highest measured ordinate is a clamp. `candidate2` takes that T.
- The instrument says G2 "replaces [memo C's stand-in] with family A's curve by constructing
  `TableT` from the measured ordinates; nothing else changes" (`instrument/tone.py:8–9`). A cell's
  T is otherwise `memo_c_T(endpoint, span)` (`instrument/forward.py:138`), which snaps a span to
  the nearest of memo C's tabulated spans (32, 44, 96, 128, 160; ties to the first,
  `tone.py:57`, `90`) and completes it as memo C's base table plus a residual interpolated through
  its points and held beyond them (`tone.py:91–94`). Those are memo C's spans and memo C's table,
  not family A's strata.
- The exposure runner binds predictions by hash and forms no T (`bed/exposure/runner.py:55–56`).
  The rehearsal's native T is memo C's table again, snapped the same way
  (`gate/rehearsal/body.py:578–611`).

So nothing declared says which T a span between strata reads — the light B′ validation cell on
rrect-80 (s = 80, t = 1/6; `bed/README.md:95`) and every H cell on rrect-112 (s = 112) — nor what a
stratum with three or four ordinates reads below its lowest one. Family A declares ten levels at
t = 0 and at 96, three (160, 208, 255) at 128 and at dark 80, and four (96, 160, 208, 255) at 160
(`bed/bed.json`, the 2x calibration cells).

## 2. The rule

Per endpoint. L is the encoded input level, s the surface's span in CSS px, and
t = clamp((s − 64)/96, 0, 1), the declared size variable.

1. **Full rows.** F₀ is the t = 0 stratum's curve through its ten ordinates (it serves every
   s ≤ 64, as declared); F₉₆ is the 96 stratum's. Each is piecewise linear, held at its ends
   (`TableT`).
2. **Base.** B(L, s) = F₀(L) for s ≤ 64, F₉₆(L) for s ≥ 96, and linear in t between them.
3. **A sparse stratum** σ (dark 80, 128, 160): at each of its measured levels Lᵢ the residual is
   rᵢ = yᵢ − B(Lᵢ, σ). R_σ(L) is piecewise linear through the (Lᵢ, rᵢ) and held beyond the first
   and the last, which is the stand-in's own convention (`tone.py:91–94`). The completed row is
   T_σ(L) = B(L, σ) + R_σ(L).
4. **Monotone guard.** Between two consecutive measured levels a < b of a sparse stratum, each
   completed ordinate on the grid (item 6), taken upward, is raised to its predecessor and capped at
   y_b. Below the first measured level and above the last, the row is B plus a constant and is
   monotone because B is. A measured ordinate is never moved. Measured ordinates that themselves
   decrease are a finding for the parent, not something this rule repairs: the declared `TableT` is
   monotone through them.
5. **Between strata.** T(L, s) is linear in t between the two strata that bracket s (64, dark 80,
   96, 128, 160); s ≤ 64 reads F₀ and s ≥ 160 the 160 row (the declared clamp above 160).
6. **The runtime grid.** Candidate 2's table (`bodyToneTableCodes`, `implementation-design.md`
   §2.9) is this rule sampled at the five rows 64, 80, 96, 128, 160 and the eleven levels 0, 64,
   96, 128, 160, 176, 192, 208, 224, 240, 255. Every knot of every row is one of those levels, so
   the shader's evaluation (linear in L within a row, linear in t between rows) reproduces the rule
   exactly. The light schemes have no 80 stratum; their 80 row is item 5's value, the mean of the 64
   and 96 rows, which item 5 reproduces unchanged.

The rule governs native T wherever it is read: identification's T for a cell off a full stratum
(or below a sparse stratum's lowest ordinate), and candidate 2's T, including the blind H
predictions. The declared trust clause is untouched for inversion.

## 3. s = 112, stated

t(112) = 1/2, midway between the 96 stratum (t = 1/3) and the 128 stratum (t = 2/3). So at every
level, in all four endpoints and at both scales:

    T(L, 112) = ½ T₉₆(L) + ½ T₁₂₈(L)

where T₉₆ is family A's full 96 row and T₁₂₈ the 128 row completed by item 3. Below 160 that is
F₉₆(L) + ½ r₁₂₈(160), the 96 row lowered or raised by half the 128 stratum's residual at its
lowest measured level. Memo C's snapping would have read the 96 row alone (the tie goes to the
first), and a surface resized across s = 112 would have stepped by half the 96-to-128 difference.

## 4. What it satisfies, and how that was checked

- **No free parameter**: every number is a measured ordinate, a declared stratum span or t.
- **Through every measured ordinate**, by the rule and by the grid.
- **Monotone** in L at every span, by item 4 and by convexity between strata.
- **Reduces to the full row** where no residual exists: at s ≤ 64 and at s = 96 it is F₀ and F₉₆
  exactly.
- **Continuous in s**, so no runtime surface steps between strata.

`implementation-design/native_t.py` is the rule's executable form. Its self-check
(`native_t.txt`) runs on the stand-in ordinates, memo C's table sampled at family A's declared
levels and strata. In all four endpoints the measured ordinates come back exactly by the rule and
by the grid, the grid equals the rule within 6e-14 over 169 spans and 511 levels, the full rows are
exact, s = 112 is the mean of the two rows within 3e-14, and T is monotone everywhere. A constructed
case exercises the guard: base plus residual reads 163.33 between measured ordinates 150 and 151,
the guard caps it at 151, and the row stays monotone. As a description only, the completion of
the stand-in's 128 and 160 strata below their lowest ordinates sits within 0.0–4.4 codes of memo
C's own values at inputs 0, 64 and 128.

## 5. What it does not do

- It adds no 104 row, per the parent's ruling. The dark MaxLuma knot at t = 5/12 falls between the
  96 and 128 strata and is read linearly across, a named approximation that no bed cell measures.
- It does not extrapolate T above 160 in span (the declared clamp) or add any level family A does
  not have.
- It takes no position on channels. The declaration reads each ordinate as a deep median per
  channel (`nativeT.ordinates`); the rule completes each curve native T has. If family A's greys
  read neutral within the bar, the three curves coincide and candidate 2's table carries one, as
  designed; if they do not, the table carries one row set per channel, which is a size change and
  not a new rule, and the difference is a finding for step 2.
