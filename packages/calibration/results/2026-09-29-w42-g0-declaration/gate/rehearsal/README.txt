W42 G0 — the pre-sitting rehearsal of every landing referee (charter clause 3; X39)
====================================================================================

Clause 3: "L1, M1, M2 (as Decision Log 5a ruled), C1, X1, E2 and the two directional stops of
clause 10, each computed by memo A's body-swap: the shipped render with only the body argument
replaced by the grounding law readings (LT at memo E's readings) composed with the landed T ...
in all four endpoints ... A referee that fails whatever the structure's coefficients, because of
T, a membership or its own reading, fails 'by construction'" — and goes to the user before the
sitting. Nothing here was captured natively, fitted to Apple, published or written into a
matrix, generation, profile or capture tree. No holdout or recorded native pixel was opened.

THE METHOD
----------
body.py      Float64 forward models on the canonical canvas.
             - The SHIPPED WebGPU body: grounding memo B's replica (pyramid, body and chain taps,
               per-pixel scatter share, scale conditioning, the group-level tone solve, chroma
               retention), now SAMPLED AT THE REFRACTED POSITION the optics pass samples
               (wgsl/optics.ts, "The lens (W12 G2)"), for every shape the non-holdout bed draws.
               Constants from resolve.ts -> resolved.json (this worktree's own material code;
               equal to memo B's resolver on every overlapping field).
             - LT: memo E's lt.py over the whole canvas and all three channels. Capture on the
               box + declared margin, 0.8-dev floor (1.6 on rrect-lg) before the knee, narrow
               G(kappa 5 o(d)) by the 'var' reading, wide G(kappa 8), clamp-to-edge when active
               and normalised when receded, knee on encoded luma at lambda, Normal at w = 0.5.
               Memo E's readings: kappa 1.983 / 2.035 / 2.094 / 2.074 (light active / light
               receded / dark active / dark receded, LT-1k), lambda 0.9. Chroma: W's (memo A,
               "chroma takes the heavy argument only"), A = M_L + (W - L(W)).
             - T: candidate 1's LANDED T (the shipped solve's uniform response per pixel at A;
               in light receded E3's F on L(M) with g(L(W)) v(W)); candidate 2's NATIVE T (memo
               C's native uniform table with its span corrections, luma only, replacing candidate
               1's luma). Family A does not exist before G1, so E3's F above 150 is extended by
               memo C's light-inactive native readings (160 -> 202, 242.4 -> 235.3, 255 -> 240)
               as a STAND-IN for family A's ordinates.
swap.py      web' = round(web + cov (t(B_cand) - t(B_ship) - q)): only the difference of two
             bodies enters the shipped capture, so rim, highlight, inner and outer shadow and the
             author tint's layer are kept. t is the author tint's composite fitted per tinted
             cell (optics.ts mixes the encoded body with seed * shade(luma) at the tint's
             strength); q drops the capture's rounding where it is within one code of the replica,
             so a uniform body is rounded once. ACTIVE POSE: swapped only beyond the 20 pt
             refraction band, which stays exactly as vitrea drew it (the parent's instruction,
             2026-09-29: Apple refracts there, vitrea draws its own lens, LT does not model
             refraction). The receded pose is swapped over the whole body.
measure.py   compare --skip-capture on the swapped tree (VITREA_WEB_CAPTURES), one scratch stage
             per scheme named by the variant's documents.
ref.sh       the gate's candidate-admission referees (../referees) on both stages.
read.py      the per-endpoint reading below; sweep.py the coefficient sensitivity.

Variants (documents/<variant>/: the shipped document bytes plus one "$comment-w42-g0-rehearsal"
key, so each variant's rows name their own document hash while the resolved material is the
shipped one; they are not materials):
  identity  the shipped captures, re-measured          (the base every bar is read against)
  c1        candidate 1, the landed T
  c2        candidate 2, native T (memo C's table)
  c1s       candidate 1 with light receded left at the shipped solve (Decision Log 3's fallback)
  c1m       DIAGNOSTIC: c1 with the per-channel composite's chroma instead of W's
  e3ctl     the swap's CONTROL (light receded only), below

THE PROOFS (before any candidate was read)
-------------------------------------------
- replica-check.txt: the lensed replica against the shipped captures, codes rms, 14 cells over
  the four endpoints: 0.29-0.88 in 2-8 CSS px of depth, 0.24-0.59 beyond (rounding is 0.29),
  except light-active checker-8 rrect-lg 1.6-2.1. Unlensed, the 2-8 band misses by 1.9-31.
- control-e3.txt: the sealed W41 E3 body swapped onto the canonical capture against W41 G2's
  REAL stage capture of that body (208 light cells, cal/val/probe). Body bands 0.2-0.7 codes rms
  beyond half a CSS px of the contour; interior mean linear luminance within 0.0015 on every
  cell (impulse worst), <= 0.0005 on almost all: the swap's resolution for L1 (a quarter of
  L1's growth bound at worst). The outermost half CSS px and the exterior antialias ring carry
  up to 3.5 codes rms (the lens's maximum displacement meets the rasterised field there).
- measure.py --identity-check: 360/360 identity rows equal the canonical rows field for field
  except capturedAt and the renamed document clause.
- In all 212 active cells the band pixels (depth <= 20 pt) are byte-identical to the shipped
  capture under every variant.

THE REHEARSAL TABLE (C1 = candidate 1, C2 = candidate 2; identity passes every referee)
------------------------------------------------------------------------------------------
Verdicts: pass; FAIL-C (fails by construction: across kappa 1.5-2.5 x lambda 0.5-1.0 where swept,
or by the construction named); FAIL-R (fails at memo E's readings, passes elsewhere on the grid);
BAND (the referee's region is mainly inside the held 20 pt band: the rehearsal barely exercises
the law there); UNMOVED (exterior: the body swap cannot reach it). Numbers are growth / R / move
against the identity base, bars as clause 10 states them.

light ACTIVE (122 cells; swapped fraction 0 on s <= 44, 0.45 rrect-md, 0.58 rrect-ml)
  L1      C1 FAIL-C (T): 10 growth failures, max +0.0296 (impulse, checker, photo on rrect-md/ml).
             The landed T is 6-9 codes above native T at inputs 64-160 (96 -> 190.3 against
             181.7 at span 96): W36's named grey-middle miss, which the group argument hid and a
             per-pixel argument exposes. C2 removes 7 of the 10.
          C2 3 growth failures, all rrect-ml (span 128), +0.0065 to +0.0085, web 0.009 DARKER than
             native. checker ml: FAIL-R (passes at kappa 1.6, lambda >= 0.9). photo ml 1x/2x: FAIL-C
             across the grid by +0.0056 at best. Cause unresolved between the law's active
             ml/lg misfit (memo E: the undeclared bleed, U7) and native T's span-128 correction.
  M1      pass (median 0.888 / 0.919)
  M2      pass (4 / 5 named toward Apple, the rest within 2 %)
  C1      UNMOVED: every active T statistic identical to the base (exterior-cut §3, §9)
  X1      UNMOVED, pass (78 cells, zero above native black)
  E2      BAND, FAIL on its own reading: 352 bins / 19 cells (C1), 752 / 47 (C2).
             Every shell is inside the held band, byte-identical to shipped; the bins move only
             through E2's reference, the cell's own d <= -6 CSS px median, which includes the
             swapped core. Cause: E2's reading (an edge statistic referenced to the body level)
             plus the rehearsal's band/core composite. Not the law's edge.
  Stop H  C1 BAND FAIL 1/6 (2x capsule annulus 0.67 against native 2.01, shipped 1.86: the dot
             sits at depth 18 and its rings reach the swapped 20-22 pt strip); C2 pass
  Stop P  FAIL 6/10, both. rrect-md/ml (core swapped): the M band falls to 12-15 x1e-3 against
             native 19-23 and shipped 14.5-20. Capsules: BAND. Cause: chroma (the landed T's
             chroma compression plus W's chroma argument); c1m (M's chroma) still fails M.
light RECEDED (86 cells; whole body swapped)
  L1      FAIL-C 2, both: tinted photo rrect-md inactive, +0.0091 / +0.0098 (+0.007 to +0.012
             across the grid). The shipped already misses it by 0.033 and the untinted twin
             passes: the level moves through vitrea's tint composite. W41's +0.0131 / +0.0136 on
             these cells is the class clause 10 says is "read as written".
             W41'S LESSON CELLS PASS: every inactive checkerboard L1 error <= 0.0066 (E3 per
             pixel read 0.111-0.148); light-solid inactive (Decision Log 3's trigger) passes with
             the stand-in extension. Under C1 both named L1 misses (tinted impulse, 0.066) close.
          c1s (shipped solve kept) FAIL-C: 17 growth failures, checker inactive +0.011 to +0.026,
             plus M2 5 failures, Stop H 6/6, Stop P 8/8. Decision Log 3's fallback is not viable.
  M1      pass (1.110 / 1.115)
  M2      FAIL 4, both (4 named toward Apple: rrect-md +30 % / +19 %, toolbar 1x +37 %, capsule
             1x +6 %). rrect-sm 2x -17.9 %: FAIL-C (-4 % at kappa 1.5 to -25 %): the law on the
             thinnest receded shape (s = 32; U2/U3). rrect-sm 1x -5.9 % (within at kappa 1.5,
             lambda >= 0.9), capsule 2x -2.1 % (within at lambda <= 0.7), toolbar 2x past Apple
             by 2.9 % (named at kappa 2.5): FAIL-R.
  C1/X1   UNMOVED, pass. E2 n/a (active only).
  Stop H  pass: peaks 3.3-6.6 codes against native 2.0-11.2 (shipped 2.1-36.5)
  Stop P  FAIL 6/8, both: F 2.26 against native 4.26 (shipped 6.72: the mottling is gone and
             overshot), M 15.7 against 19.7 (shipped 20.5). Cause: the declared chroma argument
             v(W) at sigma_w ~ 16 pt (memo A read chroma at s ~ 10-12). c1m: 2/8, F 4.25.
dark ACTIVE (90 cells; swapped as light active)
  L1      pass (max growth +0.0003)
  M1      C1 pass (0.955); C2 FAIL median 0.761: C2's luma structure rises toward Apple while
             chroma stays at the landed T's
  M2      pass (4 named)
  C1/X1   UNMOVED, pass
  E2      BAND, FAIL on its own reading: 123 bins / 10 cells (C1), 599 / 36 (C2), as light active
  Stop H  C1 pass; C2 BAND FAIL 2/2 (capsule annulus -4.3 / -3.8 against native 0.6 / 0.3: the
             swapped strip reads darker than the held floor ring)
  Stop P  FAIL 4/4, both: M 12.4 x1e-3 against shipped 14.7, native 28.5. Cause: T's chroma, the
             dark body's chroma deficit (the shipped carries half of Apple's mid-band chroma, W31
             X3), which both candidates keep; c1m 13.2
dark RECEDED (62 cells; whole body swapped)
  L1      C1 FAIL-C (T) 4: photo rrect-md inactive and tinted photo capsule, +0.006 (landed T at
             input 28 gives 33 codes against native 48). C2 2: photo rrect-md inactive +0.013
             (+0.011 to +0.014 across the grid). C2's native T is not a reading above input 128
             at span 96 (memo C's trust bound) and 25 % of that body's M lies above 128: T is
             UNMEASURED there with existing evidence (family A's dark greys on rrect-80 and
             rrect-md read it).
  M1      FAIL-C, both: median 0.458 / 0.317, all four cells below 0.6, R 0.27-0.33 across the
             grid, c1m 0.470. Cause: T's chroma (the landed dark receded solve passes about a tenth
             of the backdrop's chroma) against a luma structure the law raises toward Apple (M2
             +34 % to +185 %, all named). R falls BECAUSE M2 improves.
  M2      pass (4 named)
  C1/X1   UNMOVED, pass. E2 n/a.
  Stop H  pass: peak 3.0 against native 2.7 (shipped 37.7)
  Stop P  FAIL-C 4/4: F 0.68 x1e-3 against shipped 2.36, native 4.64; M 5.4 / 9.0 / 26.9. T's
             chroma, as M1.
Owner test (run-owner.py, all six gated profiles, identity base 108/108): C1 101/108, C2 101/108.
  The seven new failures are the referee failures above (M1 median and cell, M2 case and the
  derivation's live-cut check, L1 growth, the MISSED_27_ROWS owner case) plus L1's named-miss
  list: under C1 both named tinted-impulse misses close, under C2 one does; the list cannot move
  without a commit, so the test reads a closing miss as a change. M2's toward-Apple moves were
  recorded as the seal would record them (16 / 17 entries) and pass.
Eye (a look, not a referee): the five canonical strata for C2 at
  ~/vitrea-w42/scratch/gate-rehearsal/sheets-rehearsal-c2/ (inventory sha256 9092b88d...);
  gradient NOT-DRAWN (no swapped W39 render). Body OKLab distance to native, candidate minus
  shipped: closer on every binary, impulse and text inactive cell; farther on dark inactive photo
  (median +0.003).

WHAT GOES TO THE USER BEFORE THE SITTING (clause 3's stop)
-----------------------------------------------------------
1. L1 growth against the landed T (light active, candidate 1): a per-pixel landed T carries W36's
   grey-middle miss into L1's growth bound. Decision Log 5b records that gap as "the existing
   named miss"; L1 growth is an adopted bar. Which reads?
2. Tinted photo rrect-md inactive L1 growth (+0.009 / +0.010, both candidates, across the grid):
   the class clause 10 already says is "read as written". As written it fails.
3. Dark chroma (M1 in dark receded, Stop P in both dark endpoints; M1 dark active under C2): the
   candidates' T keeps the shipped dark chroma transfer, and the structure law raises luma
   structure toward Apple, so M1's ratio falls as M2 improves. Neither candidate as declared
   changes chroma transfer (candidate 2's T is luma only). A ruling on M1's reading, or on a
   chroma term in the declaration.
4. The chroma argument in light (Stop P): v(W) as declared for candidate 1 light receded fails the
   M band; the per-channel-M diagnostic passes F. The kernel is U6 / family E's question; the
   declaration may want the chroma width free.
5. M2 on light receded rrect-sm 2x (s = 32) fails across the grid: the law on the thinnest shape.
6. E2: every rehearsal failure is its own reference moving under a held band; the charter already
   gives its reading to the user if it fails by construction.
7. Decision Log 3's light receded fallback (the shipped solve under the law) fails L1 on the
   checkerboards by construction; it is not a usable fallback as written.
8. The rehearsal cannot exercise the law on active spans <= 44 (nothing lies beyond the 20 pt
   band) nor C1 / X1 (exterior); G2's real renders must.

LIMITS
------
- The swap is a model of vitrea's render: exact to rounding in the body (control-e3.txt), not in
  the outermost half CSS px. The active band is held at shipped by instruction, so no active
  statistic whose region lies in 0-20 pt reads the law.
- LT at memo E's readings is exploratory; the sweep covers kappa 1.5-2.5 and lambda 0.5-1.0 on the
  failing cells only.
- Family A's ordinates above 150 are stand-ins; candidate 2's T is memo C's table with its trust
  bounds (dark, spans >= 96, inputs above 128/140 unread).
- The landed T per pixel is non-monotone below one code of input in dark (W36's black branch is a
  group construction: dark receded capsule 0 -> 20, 0.5 -> 48.7, 1 -> 4 codes); it reaches only
  impulse floors.

FILES
-----
resolve.ts / resolved.json, body.py, swap.py, measure.py, ref.sh, read.py, sweep.py,
control_e3.py / control-e3.txt, replica_check.py / replica-check.txt, documents/<variant>/,
rehearsal.json (read.py over c1, c2, c1s, c1m), runs/<variant>/ (the referee outputs, stops,
swap logs, owner summaries for c1 and c2), sweeps/ (kappa x lambda on the failing cells),
runs/scratch-manifest.json (SHA-256 of the stages, bulky cuts and every swapped tree, which stay
outside git at ~/vitrea-w42/scratch/gate-rehearsal/w42gate/, copied from /tmp/w42gate/ where the
recorded paths point).

  cd packages/calibration/results/2026-09-29-w42-g0-declaration/gate/rehearsal
  export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
  pnpm exec tsx resolve.ts > resolved.json          # from packages/calibration, path adjusted
  python3.12 -B replica_check.py > replica-check.txt
  python3.12 -B swap.py --variant e3ctl --out $S/tree-e3ctl --profiles <the two light>
  python3.12 -B control_e3.py $S/tree-e3ctl > control-e3.txt
  for v in identity c1 c2 c1m; do
    python3.12 -B swap.py --variant $v --out $S/tree-$v
    python3.12 -B measure.py --tree $S/tree-$v --variant $v --out $S/stage-$v
    ./ref.sh $S/stage-$v/stage-light $S/stage-$v/stage-dark $v $v $S/tree-$v $S/ref-$v
    (cd ../stops && python3.12 -B stops.py --candidate-root $S/tree-$v --document ... \
       --out $S/ref-$v/stops.json --text $S/ref-$v/stops.txt)
  done
  python3.12 -B measure.py --identity-check $S/stage-identity
  (cd ../owner && python3.12 -B run-owner.py --stage $S/stage-c1/stage-light ... )
  python3.12 -B read.py --root $S --variants c1,c2,c1s,c1m --out rehearsal
  python3.12 -B sweep.py --variant c2 --cells P/S,... --kappa 1.5,2.5 --lam 0.5,0.7,0.9,1.0 --out $S/sweep
