W42 G0 rehearsal, ROUND 2 — the failures evidence can settle (charter clause 3; the parent's items (a)-(e))
===========================================================================================================

Round 1 (../README.txt, ../runs/) is not rewritten. Round 2 uses the same method and band rule,
offline, on the same canonical captures. The parent ruled before this round: L1 reads as written
(candidate 1 cannot land in light active; candidate 2 is the route there); Decision Log 3's
shipped-solve fallback for light receded is struck; the reach of active spans <= 44 goes to G2's
real renders.

The scripts gained options and keep round 1's defaults: a re-swap of ten round-1 cells (c1 and
c2, every endpoint, a tinted cell) is pixel-identical to round 1's trees. New: e2abs.py,
tint.py (+ tint-resolve.ts -> tint-resolved.json), monotone.py; body.py (per-channel knee,
separate kappas, W's support, floor on/off, the monotone device), swap.py (variants c1p, c2p,
c1d, c1f, c2f), sweep.py (support / floor / kappa-pair grids).

Variants in this round:
  c1p / c2p  (a) the per-channel knee rival (U6), both candidates: N and M per channel,
             A = M_rgb (luma and chroma both the per-channel composite's)
  c1d        (e) c1 with the landed T's black value held flat below its join — a REHEARSAL
             DEVICE, not a declaration
  c1f / c2f  (b) DIAGNOSTIC: the active body swapped whole, through vitrea's lens, to show what
             the held band hides from E2 — not the rehearsal of record

ROUND-2 TABLE (P = per-channel rival; C1p / C2p; identity passes every referee)
-------------------------------------------------------------------------------
light ACTIVE
  L1      C1p FAIL 10 (T, as round 1: ruled, C1 does not land here). C2p 3, all rrect-ml:
          checker +0.0085, photo 1x/2x +0.0055 / +0.0051 (round 1 +0.0070 / +0.0065)
  M1      pass (0.888 / 0.923)          M2  pass (6 / 4 named)
  C1, X1  UNMOVED, pass
  E2 abs  pass BY CONSTRUCTION: 0 of 7,728 bins changed (see (b))
  Stop H  C1p BAND 1/6 (the capsule seam, as round 1); C2p pass
  Stop P  FAIL 6/10, both: the M band of rrect-md/ml stays 12-15 x1e-3 against native 19-23
light RECEDED
  L1      FAIL 2, both: tinted photo rrect-md inactive +0.0109 / +0.0119 (round 1 +0.0091 /
          +0.0098): a COST of the rival, the untinted body moves further (see (c))
  M1      pass (1.110 / 1.113)
  M2      FAIL 3 (round 1: 4): capsule 2x now named; rrect-sm 1x -3.9 %, rrect-sm 2x -15.4 %,
          toolbar 2x +30.5 % (past Apple by 4.6 %)
  Stop H  pass
  Stop P  FAIL 2/8 (round 1: 6/8): 1x toolbar M 10.26 against native 12.59, shipped 14.06;
          2x rrect-md F 3.22 against 3.45, shipped 3.49 (dShip 0.04 on a 0.13 resolution: the
          tightest cell of the stop)
dark ACTIVE
  L1      pass
  M1      C1p pass (0.962); C2p FAIL 0.769 (round 1 0.761): NOT fixed by the rival
  M2      pass          C1, X1  UNMOVED, pass       E2 abs  pass by construction
  Stop H  C1p pass; C2p BAND 2/2 (the capsule seam)
  Stop P  FAIL 4/4, both: NOT fixed
dark RECEDED
  L1      C1p FAIL 6 (round 1: 4): adds photo capsule inactive 1x/2x +0.0063, a COST of the
          rival; C2p 2 (+0.0139, as round 1)
  M1      FAIL, both: 0.463 / 0.327, all 4 cells: NOT fixed
  M2      pass (4 named)          Stop H  pass
  Stop P  FAIL 4/4, both: NOT fixed
Owner test: C1p 101/108, C2p 101/108 against the identity base's 108/108; the seven new failures
are the rows above (M1 median and cell, M2 case and live-cut check, L1 growth, MISSED_27_ROWS,
L1's named-miss list closing). M2's toward-Apple moves recorded as the seal would: 18 / 17.

(a) THE PER-CHANNEL RIVAL, both candidates, all four endpoints
  Fixes light receded Stop P (6/8 -> 2/8) and one light receded M2 cell (capsule 2x). Does NOT fix
  dark M1 (0.463 / 0.327 receded, 0.769 active under C2), dark Stop P (4/4 both endpoints) or
  light active Stop P (6/10). Costs: light receded tinted L1 growth +0.0018 / +0.0021 more; two
  new dark receded L1 growth failures under C1p (photo capsule inactive +0.0063); Stop H unchanged
  (the active capsule seam only). The dark chroma deficit is not the knee's form.

(b) E2 READ ABSOLUTELY (e2abs.py; runs/e2abs-summary.json)
  Per bin, mean |web - native| per channel against Apple, candidate minus shipped <= 1 code, E2's
  own bins and population, the deep-median reference dropped. Under the held band: 0 of 7,728
  bins change in c1, c2, c1p and c2p, so E2 passes by construction and reads nothing of the law.
  Where the bins lie: all 7,728 (100 %) are inside the 20 pt band and all are under vitrea's
  lens (displacement at the bin 1.1-43 CSS px, median 18.9): the held band hides all of E2.
  DIAGNOSTIC, the law's body pushed through vitrea's lens (c1f / c2f): 3,580 / 2,846 bins worse
  than shipped by more than one code (median worst 6.5 codes), in 177 / 189 of 212 cells;
  2,312 / 3,476 better by more than one code. What G2 draws in the band decides E2; the law under
  vitrea's lens moves the edge both ways, and farther from Apple on 37-46 % of bins.

(c) TINTED PHOTO RRECT-MD INACTIVE (tint.py -> tint.txt)
  vitrea's composite, from the code (material.ts tintedMaterialColour, constants resolved by
  tint-resolve.ts): in light receded the tint is a GREY layer at full strength, level
  0.0288 + 0.7312 u, u the untinted body's linear luminance (chroma scale 0). It reproduces every
  shipped tinted capture from its untinted twin at 0.01-1.62 codes rms (body at depth >= 2 CSS px),
  and it equals the per-cell fit the swap used (the fit's layer 0.029 + 0.731 u, equal channels).
  So the tinted cell's mean is 0.0288 + 0.7312 x the untinted body's mean over the same pixels,
  and ALL of the growth is the body change: the untinted twin rises +0.011 to +0.016 (to within
  0.0005-0.006 of Apple, from 0.010-0.011 below), which the composite carries at 0.7312 into a
  cell it already overshoots by 0.033. Code composite against the swap's fit: +0.0081-0.0114
  against +0.0084-0.0119 (the fit's extra 0.0003-0.0005 is the edge).
  To pass, the untinted body may rise at most +0.0068 on that silhouette: about 60 % of the
  twin's gap. No candidate can pass without giving back its correction of the untinted photo;
  the other route is vitrea's receded tint composite, which W42's law does not govern.

(d) M2, LIGHT RECEDED RRECT-SM 2x (s = 32) (sweeps/sweep-r2-d.*)
  36 configurations, c2 at lambda 0.9: W's support box / canvas / rounded shape x the 0.8-dev
  floor on / off x kappa memo E, LT-2k (2.14, 1.98) and (kn, kw) = (1.5, 2.5), (2.5, 1.5),
  (1.2, 2.035), (1.0, 1.5). Every one fails; the nearest is -2.9 % (canvas, kn 1.0, kw 1.5),
  the declared box -17.9 %. None of the declared rivals or supports passes. The same grid passes
  the other three failing cells somewhere: rrect-sm 1x (canvas with kn 1.2 / kw 2.035, or kn 2.5 /
  kw 1.5 on any support), capsule 2x (box at LT-2k, or canvas), toolbar 2x (canvas).
  The bed (w42-g0-bed, bed/bed.json, read only): structured receded cells at s <= 44 exist, all at
  s = 44 on the capsule — B' P1 at pitch 32 and 64 (2x) and pitch 4, 8 and 4 at an odd offset
  (1x); C's S16 patch, both polarities; D's steps at delta 0 (validation) and 12; H's 128/229
  checker at pitch 64 (holdout). None at s = 32, and no photo cell.

(e) THE LANDED T'S BLACK END (monotone.py -> monotone.txt)
  Per pixel the landed response dips below its value at black: dark receded 20 -> 0.1 codes at
  input 1, back to 20 at input 12.5 (capsule) / 14.9 (rrect-md); light receded 133 -> 106-113,
  back at 16-17 (it bears only on the struck fallback); light active capsule 132 -> 127.7, back
  at 7.4; dark active monotone. Only dark receded impulse cells (100 % of the body) and the probe
  checker-64 cells (5-7 %) have pixels below the join; every failing dark photo cell's argument
  is at least 63 codes. The device (c1d) moves only the dark receded impulse capsule: L1 web
  0.0021 -> 0.0070 (growth -0.036 -> -0.041, both pass) and its halo peak 3.0 -> 0 (pass). No
  dark failure changes, so the non-monotonicity drives none of them.

WHAT STILL FAILS BY CONSTRUCTION (the list for the user)
----------------------------------------------------------
1. Dark chroma: M1 in dark receded (0.33-0.46, all four cells, every variant, the whole kappa x
   lambda grid), M1 in dark active under candidate 2 (0.76-0.77), and Stop P in both dark
   endpoints (4/4). Cause: T's chroma transfer. Both candidates keep the shipped dark solve's
   chroma (about a tenth of the backdrop's), and candidate 2's T is luma only. Meanwhile the law
   raises luma structure toward Apple (M2 named, +34 % to +185 %), so R falls as M2 improves.
   Neither knee form helps.
2. Light active Stop P (the M band, 6/10, both candidates, both knee forms). Cause: T's chroma in
   light active, the same class as 1. The M band reads 12-15 x1e-3 against Apple's 19-23 and the
   shipped 14.5-20.
3. Tinted photo rrect-md inactive L1 growth (+0.009 to +0.012, every candidate and rival). Cause:
   vitrea's light-receded tint composite, a grey layer 0.0288 + 0.7312 u that already overshoots
   Apple by 0.033. The body's correction of the untinted twin passes through at 0.73. Passing
   needs either the body to stay about 0.004 below Apple on the untinted photo, or a tint-composite
   change outside the law.
4. M2 on light receded rrect-sm 2x, s = 32: -2.9 % to -25 % across every declared rival, support,
   floor and kappa pair tried. The declared bed carries no s = 32 receded structured cell to
   identify it.
5. E2 cannot be read by the rehearsal (100 % of its bins are in the held band, under vitrea's
   lens). The diagnostic says the law drawn through vitrea's lens moves 37-46 % of bins farther
   from Apple by more than a code. What G2 draws in the band is a decision to take before G2.
6. Dark receded L1 on photo rrect-md inactive under candidate 2 (+0.013 to +0.014 across the
   grid). Candidate 2's native T is not a reading above input 128 at span 96, and 25 % of that
   body lies there. It is UNMEASURED with existing evidence until family A's dark greys
   (rrect-80, rrect-md) read it. Candidate 1's dark receded L1 (+0.006 to +0.009) is the landed
   T's level, the class item 1 of the ruling already settles.
Not by construction, recorded: light active candidate 2 L1 on rrect-ml (+0.005 to +0.009) is split
between the active ml/lg misfit (U7) and native T at span 128, which the bed's U7 rows identify.
The Stop H failures on the active capsule are the rehearsal's band/core seam. Everything else in
round 1's table stands.
