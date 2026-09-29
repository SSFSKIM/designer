W42 G0 rehearsal, ROUND 3: chroma and the band (charter clause 3; the parent's items (a)-(c))
=========================================================================================

Rounds 1 (../README.txt, ../runs/) and 2 (../round2/) are not rewritten. Round 3 uses the same
method: the body swap on the canonical shipped captures, offline, every referee in all four
endpoints. The parent ruled before this round that candidate 1 cannot land in light active, that
the shipped-solve fallback for light receded is struck, and that candidate 2's T is the route
through light active.

Variants are named r3-<candidate><knee><chroma><band>:
  candidate  1 (landed T) | 2 (native T)
  knee       l on-luma (chroma from W) | p per-channel (A = M_rgb)
  chroma     n none: the variant's own chroma, which is the shipped solve's
             s the literal face matrix's saturation, item (a)
             g W41 G1's fitted E3 gain, item (b)
             x saturation 1.2 / 1.3 applied to T's output, the narrow reading of (a); run as a
               sweep on the M1 bed only (sweeps/)
  band       h held: the 20 pt band is byte-identical to shipped, as in rounds 1-2
             b blended, item (c)
r3-1lnh, r3-2lnh, r3-1pnh and r3-2pnh are round 1/2's c1, c2, c1p and c2p, pixel for pixel. This
round re-reads their trees and does not re-render them. Twenty new trees, stages and referee runs
are kept in scratch and digested in runs/scratch-manifest.json. The small outputs are under runs/
and runs/e2abs-summary.json.

Reproduction. Seven cells were re-swapped with this round's scripts, for each of c1, c2 and c1p
and also for r3-1lnh and r3-2pnh. The cells were light 1x and dark 2x: photo rrect-md rest and
inactive, the tinted inactive twin, and photo capsule rest. Every re-swap is pixel-identical to
the committed trees, and r3-1lnh = c1 and r3-2pnh = c2p exactly. Re-reading rounds 1-2 with this
round's read.py gives identical referee readings. The only difference is round 2's owner
summaries, which finished after round 2's read. read.py now names each tree exactly: its old
glob `tree-<v>*` also matched c1d/c1f/c1m/c1p/c1s, but the tree that won had the same band rule,
so nothing it read changed. tint.py's default output still reproduces ../round2/tint.txt byte for
byte.

Scripts. swap.py gains the r3 variants (FACE_CHROMA, G_FIT, BLEND_PT). measure.py records a PROBE
cell that the instrument refuses as unmeasured, in `<profile>.unmeasured.json`, and refuses any
other missing cell. The one refused cell is 1x dark photo__rrect-ml__inactive in r3-2lgh and
r3-2lgb ("a 0.00px contour ... carries no curvature"); no adopted referee reads a probe photo.
Also changed: read.py (exact tree), sweep.py (the shared document directory), tint.py (--scheme
dark, round 3's decomposition) and r3read.py (new; writes the table, the per-cell detail and the
blend's reach).

WHERE THE FACE MATRIX SITS (item (a))
-------------------------------------
Memo D's face is ONE colour matrix, and memo E writes the body as y = T(M) or face(M). The law's
tone therefore sits where the face sits: on the argument after the knee and the Normal fill. T
replaces the face's grey-level part, which is the white/black contrast and the fill's lift, and
which T measures. The face's chroma part acts on the SAME argument, around encoded luma:

    y = T(L(arg)) + k (arg - L(arg))        encoded; arg = W (on-luma) or A = M_rgb (per-channel)
    k = saturation x (white - black) x (1 - fill alpha)

  light active    1.2 x 0.63  x 0.8 = 0.605
  light receded   1.2 x 0.56  x 0.8 = 0.538
  dark active     1.3 x 1.0         = 1.300
  dark receded    1.3 x 1.045       = 1.359
Nothing is fitted. For comparison, the chroma gain Apple's uniform response carries is W41 G1's
g: 0.93-0.96 in light and 1.07-1.21 in dark (see (b)).

THE ROUND-3 TABLE (full: rehearsal-r3.txt; every failing cell with its reading: rehearsal-r3-detail.txt)
------------------------------------------------------------------------------------------------------
Key:
  Ln       L1 cells failing (growth or new absolute miss)
  m<R>[/n] M1 failing: the median R, and the number of cells outside [0.6, 1.4] when that is not 0
  Mn       M2 directional failures
  Hn / Pn  Stop H / Stop P failing cells
  |a/b     E2 in the active pose: a = bins failing the adopted reading, b = cells failing the
           absolute reading
X1 and C1 pass everywhere, because the swap does not reach the exterior.

      light active                    light receded      dark active             dark receded
1lnh  (ruled) L10 H1 P6 |352/0        L2 M4 P6           P4 |123/0               L4 m0.46/4 P4
1lnb  (ruled) L25 M2 H1 P10 |1838/27  L2 M4 P6           H2 P4 |508/11           L4 m0.46/4 P4
1lsh  (ruled) L10 H1 P6 |373/0        L4 m0.74 M4 P8     P4 |134/0               L4 m1.29
1lsb  (ruled) L25 M2 H1 P10 |1834/27  L4 m0.74 M4 P8     m1.33 H2 P2 |538/13     L4 m1.29
1lgh  (ruled) L10 H1 P5 |372/0        L2 M4 P6           P4 |134/0               L2 m1.36/2 P2
1lgb  (ruled) L26 M2 H1 P7 |1809/30   L2 M4 P6           m1.37/2 H2 P3 |537/13   L2 m1.36/2 P2
1pnh  (ruled) L10 H1 P6 |276/0        L2 M3 P2           P4 |109/0               L6 m0.46/4 P4
1pnb  (ruled) L26 M2 H1 P10 |1872/27  L2 M3 P2           H2 P4 |501/11           L6 m0.46/4 P4
1psh  (ruled) L10 H1 P5 |269/0        L4 m0.78 M3 P8     P4 |134/0               L4 m1.25
1psb  (ruled) L26 M2 H1 P10 |1853/27  L4 m0.78 M3 P8     m1.26 H2 |539/13        L4 m1.25
1pgh  (ruled) L11 H1 P6 |373/0        L2 M3 P2           P4 |134/0               L2 m1.34/2
1pgb  (ruled) L26 m0.99/1 H1 |1801/30 L2 M3 P2           m1.35/1 H2 |537/12      L2 m1.34/2
2lnh  L3 P6 |752/0                    L2 M4 P6           m0.76 H2 P4 |599/0      L2 m0.32/4 P4
2lnb  L3 P10 |1845/14                 L2 M4 P6           m0.63/1 P4 |980/16      L2 m0.32/4 P4
2lsh  L3 P6 |679/0                    L4 m0.74 M4 P8     H2 P4 |628/0            L3 M2
2lsb  L3 P10 |1771/14                 L4 m0.74 M4 P8     P2 |1014/16             L3 M2
2lgh  L1 P5 |863/0                    L2 M4 P6           H2 P4 |628/0            L2 P2
2lgb  L1 P7 |1829/10                  L2 M4 P6           P3 |1014/16             L2 P2
2pnh  L3 P6 |663/0                    L2 M3 P2           m0.77 H2 P4 |585/0      L2 m0.33/4 P4
2pnb  L3 P10 |1729/13                 L2 M3 P2           m0.65/1 P4 |976/16      L2 m0.33/4 P4
2psh  L1 P5 |663/0                    L4 m0.78 M3 P8     H2 P4 |628/0            L4 M2
2psb  L3 P8 |1733/14                  L4 m0.78 M3 P8     pass |1014/16           L4 M2
2pgh  L1 P6 |728/0                    L2 M3 P2           H2 P4 |628/0            L2
2pgb  L1 P1 |1811/8                   L2 M3 P2           pass |1014/15           L2

M1 medians, all 24 (LA / LR / DA / DR), are in rehearsal-r3-detail.txt. The chroma rows:
  s: LA 0.81-0.93, LR 0.745 (on-luma) / 0.775 (per-channel),
     DA 0.91-0.94 held / 1.10-1.12 blended under C2 (1.10-1.33 under C1),
     DR 1.04-1.06 under C2 (1.25-1.29 under C1)
  g: LA 1.03-1.05 (C2), LR 1.10-1.11,
     DA 0.97-0.98 held / 1.09-1.10 blended under C2 (1.15-1.37 under C1),
     DR 1.05 under C2 (1.34-1.36 under C1)
Owner test (clause 10's bar; runs/<v>/owner-summary.json). Base: 108/108.
  r3-2pgb: 103/108. The five failures are:
    - L1 growth, the dark receded tinted capsule
    - M2, light receded rrect-sm 1x
    - M2's live-cut check, 3 light receded cells
    - MISSED_27_ROWS, the set of 27 rows that miss their bound. It fails when any gated row
      moves.
    - L1's named-absolute-miss list. This one is a CLOSURE: the light receded tinted impulse
      capsule goes 0.066 -> 0.0552 at 1x and below 0.055 at 2x, so the list must shrink at the
      seal.
  r3-2psb: 102/108. The same failures, plus light receded M1 (median 0.775) and M2 past Apple on
  dark receded rrect-md (+349 %).

(a) CHROMA FROM THE LITERAL FACE MATRIX: part of it, not all
  The dark M1 deficit and the M band of Stop P ARE missing chroma. The face's saturation moves
  both:
    - dark receded M1: 0.32-0.46 -> 1.04-1.06 under C2
    - dark active M1: 0.76 -> 0.91-1.12
    - dark receded Stop P: 4/4 -> 0 under both knees
    - dark active Stop P's M band closes (blended per-channel: 0/4)
  But the literal amount is wrong in every endpoint. It is too strong in dark: 1.30 / 1.36
  against Apple's 1.07-1.21. Saturation in encoded space raises linear luminance (the decode is
  convex), so dark receded fails:
    - M2 past Apple: rrect-md +286 to +349 % against Apple's +232 / +260 %
    - L1: the tinted capsule +0.025; photo rrect-md +0.005 to +0.007 (C1: +0.013)
  It is too weak in light: 0.54 / 0.60 against 0.93-0.96. So:
    - light receded M1 falls to 0.745-0.775
    - light receded Stop P fails 8/8: the M band reads 0.004-0.014 against Apple's 0.012-0.023
    - light receded L1 moves to the untinted photo capsule / toolbar inactive: the body is now
      0.010-0.016 BELOW Apple, growth +0.006 to +0.012
    - light active Stop P keeps failing on the M band: 5-8 of 10 cells, 0.013-0.022 against
      0.019-0.024
  Under candidate 1 the right chroma over the landed T's low luma structure overshoots dark M1:
  1.25-1.33. The narrow reading (x, saturation applied to T's output) is worse. It saturates the
  shipped solve's tenth-strength chroma, leaving dark receded M1 at 0.587 (C1) / 0.403 (C2) and
  dark active at 1.009 / 0.802 (sweeps/).

(b) CHROMA FROM AN E3-FORM g(L): the fit, and what it adds
  The gain is W41 G1's committed least-squares E3 fit
  (2026-09-27-w41-g1-identification/body/attempt-1/<endpoint>-E3-fit.json):
    - g(L) on encoded luma, knots 63 / 93 / 118, neutral ordinates held at the measured greys
    - fitted on 102 W39 uniform CALIBRATION cells per endpoint; no canonical cell
  Its own residual over those cells, maximum:
    light active 0.709 codes, light receded 0.925, dark active 1.088, dark receded 1.538
  (weighted squared error 0.082 / 0.110 / 0.171 / 0.194).
  Gains, g0 / g1 / g2:
    light active   0.939 / 0.955 / 0.939
    light receded  0.952 / 0.949 / 0.933
    dark active    1.203 / 1.165 / 1.070
    dark receded   1.211 / 1.163 / 1.069
  Applied as in (a) with k = g(L(arg)). It is the only chroma that passes M1 in all four
  endpoints under candidate 2: 1.03-1.05 / 1.10-1.11 / 0.97-1.10 / 1.05. It also:
    - closes light active Stop P's M band: blended per-channel, 1/10 remains, see the list
    - closes dark receded Stop P under the per-channel knee (on-luma: 2/4 on the F band)
    - removes dark receded's photo rrect-md L1 (C2's +0.013), which (a) and chroma-none keep
  Under candidate 1 dark M1 overshoots (1.34-1.37) for (a)'s reason: C1's dark receded rrect-md
  structure is 0.0235 against Apple's 0.0344, and C2's is 0.0345.

(c) THE BAND AS A BLEND (declared before the read: weight = coverage x smoothstep(0, 20 pt, depth),
    0 at the contour and 1 at the band's inner edge; the receded pose is unchanged)
  The active pose DOES change spans <= 44. The mean swap weight over the covered body is:
      component         held    blended
      capsule (44)      0.065   0.480
      rrect-sm          0     0.307
      toolbar           0.008   0.338
      rrect-md          0.447   0.707
      rrect-ml          0.576   0.779
      rrect-lg          0.654   0.821
  A body with no deep interior takes the law everywhere, at partial weight.
  Stop H at the capsule seams: the seam failures are gone under candidate 2 in every blended
  combination. Held, they were the dark active impulse-capsule annulus, -4.3 / -3.8 against
  Apple's 0.6 / 0.3. So is candidate 2's held-band Stop P F-band overshoot at the seam.
  Candidate 1 blended still fails Stop H, but on the halo PEAK, not the seam:
    - light active 62.2 against Apple's 51.3 (shipped 44.3)
    - dark active 2.3 / 2.5 against 12.0 / 12.8 (shipped 20.0 / 16.9)
  That is the landed T's own response to an impulse.
  E2 read absolutely (runs/e2abs-summary.json), r3-2pgb:
    - 70 of 7,728 bins are worse than shipped by more than one code: 23 cells, 16 light and 54
      dark. Worst 3.27 codes, median of the failing bins 1.42 codes.
    - Every failing bin is at depth 2.25-5.75 CSS px, under vitrea's lens, where the blend's
      weight is 0.035-0.20.
    - 838 bins improve by more than a code on every channel.
    - Across the blended combinations: 70-392 failing bins, worst 3.3-5.8 codes.
  Held: 0 bins change, so it passes by construction and reads nothing. E2's adopted reading fails
  in every active combination (109-1,872 bins), held or blended, because the law moves the deep
  median E2 subtracts.

THE DARK RECEDED TINTED CAPSULE (tint-dark.txt; round 2 (c)'s method)
  vitrea's dark receded tint composite is 0.0202 + 1.4398 u while u < 0.681. The tinted cell's
  mean therefore moves by 1.44 x the untinted body's. Shipped, the body is 0.017 below Apple, and
  the composite puts the tinted cell 0.0007 from Apple. Under g the untinted twin comes to 0.004
  of Apple, and the tinted cell overshoots: growth +0.0138 / +0.0133, where passing needs the
  untinted body to rise at most +0.0045 / +0.0052. The swap's fitted composite overstates the
  tinted mean by about 0.003 here; the code composite still gives about +0.011. Candidate 1
  without chroma fails the same cell from below (+0.009: the body darkens). This is round 2's
  light receded class, and W42's law does not govern it.

WHAT STILL FAILS BY CONSTRUCTION, PER COMBINATION
-------------------------------------------------
Causes:
  [T1]   candidate 1 in light active: the landed T's level, L1 10-26 up to +0.049 (ruled).
  [C0]   no chroma: the shipped solve's chroma is about a tenth of the backdrop's. Effects:
           - dark M1: receded 0.32-0.46; active 0.63-0.77 under C2
           - Stop P's M band: dark 4/4, light active 6-10/10
  [FS]   face chroma, the wrong amount: too weak in light, too strong in dark (see (a)).
  [S1]   candidate 1 with chroma: dark M1 1.25-1.37. The landed T's luma structure is too low
         for Apple's chroma.
  [I1]   candidate 1 blended: the Stop H halo peak on the impulse capsule.
  [KL]   on-luma knee: Stop P's F band too low.
           - dark active blended 2-3/4: 0.0029-0.0052 against 0.0051-0.0081
           - dark receded with g 2/4
           - light active with g 7/10
         The per-channel knee keeps it; round 2 found the same in light receded.
  [SEAM] band held, active: the step at 20 pt.
           - Stop H on the dark active impulse capsule, 2/2 under C2
           - once the chroma is right, Stop P's F band far above Apple: light active 5-6/10
             (0.008-0.010 against 0.0035-0.0074); dark active 4/4 (0.013-0.019 against
             0.005-0.008)
         Candidate 1 held also fails light active Stop H 1/6 on the annulus.
  [LT]   light receded, every combination:
           - the tinted photo rrect-md L1, +0.008 to +0.012: vitrea's grey tint layer
           - M2 on rrect-sm 2x at s = 32: -15.8 % at best; also rrect-sm 1x and toolbar 2x
             (+30.1 % against Apple's +24.8 %)
           - Stop P 2/8 at best: 1x toolbar M 0.0102 against 0.0126; 2x rrect-md F 0.00322
             against 0.00345; shipped sits 0.00004 from Apple on a 0.00013 resolution, the
             stop's tightest cell
  [DT]   dark receded with chroma s or g: the tinted capsule L1, +0.010 to +0.025, from vitrea's
         dark tint composite (above).
  [U7]   candidate 2 in light active: L1 on 1x checkerboard rrect-ml rest, +0.0085 held / +0.0105
         blended. Photo rrect-ml 1x/2x (+0.005 to +0.009) also fails unless the chroma is g. Round
         2 split this between the active ml/lg misfit (U7) and native T at span 128, which the
         bed's U7 rows identify. It is not a choice made in this round, but it fails in every
         candidate-2 combination.
  [P1]   candidate 2, per-channel, g, blended, light active: Stop P 1/10 on 2x photo rrect-sm rest.
         F reads 0.005516 against Apple's 0.005162 and shipped 0.004954; it misses the allowance
         by 0.000006 on a resolution of 0.00014.
  [E2]   the adopted reading fails every active combination. The absolute reading passes held
         combinations by construction and fails blended ones by 1-6 codes at 2-6 CSS px.

Which endpoints pass every referee but E2, per combination (LA / LR / DA / DR):
  1 l n h   none. LA T1 [SEAM]; LR LT; DA C0; DR C0, and L1 at the landed T's level
  1 l n b   none. LA T1 I1; LR LT; DA C0 I1; DR as held
  1 l s h   none. LA T1; LR FS LT; DA SEAM (P); DR S1 FS (L1)
  1 l s b   none. LA T1 I1; LR FS LT; DA S1 I1 KL; DR S1 FS
  1 l g h   none. LA T1; LR LT; DA SEAM (P); DR S1 DT KL
  1 l g b   none. LA T1 I1; LR LT; DA S1 I1 KL; DR S1 DT KL
  1 p n h   none. LA T1; LR LT; DA C0; DR C0, and landed-T L1
  1 p n b   none. LA T1 I1; LR LT; DA C0 I1; DR C0
  1 p s h   none. LA T1; LR FS LT; DA SEAM; DR S1 FS
  1 p s b   none. LA T1 I1; LR FS LT; DA S1 I1; DR S1 FS
  1 p g h   none. LA T1; LR LT; DA SEAM; DR S1 DT
  1 p g b   none. LA T1 I1 (and one M1 cell 1.59); LR LT; DA S1 I1; DR S1 DT
  2 l n h   none. LA U7 C0; LR LT; DA C0 SEAM; DR C0, and photo rrect-md L1 (round 2's item 6)
  2 l n b   none. LA U7 C0; LR LT; DA C0; DR as held
  2 l s h   none. LA U7 FS; LR FS LT; DA SEAM; DR FS DT
  2 l s b   none. LA U7 FS; LR FS LT; DA KL (2/4); DR FS DT
  2 l g h   none. LA U7 SEAM; LR LT; DA SEAM; DR DT KL
  2 l g b   none. LA U7 KL; LR LT; DA KL (3/4); DR DT KL
  2 p n h   none. LA U7 C0; LR LT; DA C0 SEAM; DR C0, and photo rrect-md L1
  2 p n b   none. LA U7 C0; LR LT; DA C0; DR as held
  2 p s h   none. LA U7 FS; LR FS LT; DA SEAM; DR FS DT
  2 p s b   DARK ACTIVE. LA U7 FS; LR FS LT; DR FS DT
  2 p g h   none. LA U7 SEAM; LR LT; DA SEAM; DR DT only
  2 p g b   DARK ACTIVE. LA U7 and P1 only; LR LT; DR DT only
As things stand, no endpoint passes everything:
  - Dark active under 2psb and 2pgb passes every referee but E2. It passes E2 too if E2 is read
    absolutely with the band held, but held fails the seam.
  - Dark receded under 2pg* fails only the tint-composite cell [DT].
  - Light active under 2pgb fails only [U7] and a marginal [P1].
  - Light receded fails [LT] in every combination.
The only failures that belong to the law's own choices are [T1] [C0] [FS] [S1] [I1] [KL] and
[SEAM]. Candidate 2, per-channel knee, chroma g and the blended band avoid all of them. What is
left is outside the law's reach from this rehearsal:
  - the tint composites [LT i] and [DT]
  - the s = 32 structure [LT ii]
  - the span-128 misfit [U7]
  - the E2 reading, which is the user's
