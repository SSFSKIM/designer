W42 G0 gate: the two directional numerical stops (charter clause 10; X33)

Clause 10 asks for two stops beside the adopted referees before H is exposed: the impulse
halo/annulus statistic and the photo band-pass chroma energy, with the bar "no cell farther from
Apple than the shipped render at the statistic's declared resolution". This folder declares both,
implements them, proves the readers and records the baseline every candidate is compared with.

FILES
  stops-declaration.json  the declaration of record: populations (listed cell by cell), rings,
                          admission, regions, bands, units, resolutions (Stop P's frozen per
                          cell), the bar, the proof tolerances, the changes from the starting
                          design with their evidence, and the limits. The code reads its numbers
                          from here and refuses a run the file does not describe.
  stops_common.py         loaders (the native role guard, capture admission, the shipped-tree
                          check, the candidate stamp), geometry, the verdict rule
  halo.py                 Stop H
  chroma_band.py          Stop P; `--write-resolution` froze the resolution table (natives only)
  stops.py                the CLI: both stops on one candidate tree, one JSON (+ text) per run
  proof.py -> proof.txt   the reader proof
  baseline.json/.txt      native against shipped on every population cell (--baseline: the
                          shipped tree read against itself, stamped "baseline")

THE BAR (both stops)
  Per statistic S: dShip = |S_ship - S_nat|, dCand = |S_cand - S_nat|; pass iff
  dCand <= dShip + res. A cell passes only if all its statistics pass; a statistic with no
  support, or a population cell the candidate tree lacks, is UNMEASURED and never a pass; a stop
  passes only if every cell passes. The web renders are deterministic, so the only noise either
  side carries is the native reading's, and a candidate identical to the shipped render reads
  dCand - dShip = 0 exactly.
  Since version 2 (2026-09-30, the gate review of b151aff4, finding 10) the shipped render is no
  candidate: it passes this bar by construction. A run whose every scheme names the shipped
  documents is refused, the shipped tree as --candidate-root is refused before any read, and the
  one run that reads it is --baseline (candidate root = shipped root, stamped "baseline").

STOP H, impulse halo/annulus (16 cells)
  Population: every calibration/validation impulse scene in the four standard macOS 27 profiles,
  tinted included, WebGPU: light 6 scenes x 2 scales, dark only the capsule's two poses x 2.
  Reading: Rec.709 luma of ENCODED codes around each admitted dot's backdrop centroid, in CSS px:
  peak = mean(r < 2) - median(8 <= r < 10), annulus = mean(2 <= r < 8) - median(8 <= r < 10),
  and since version 2 floor = median(8 <= r < 10) in ABSOLUTE codes; per cell the median over
  admitted dots, and a cell passes only if all three pass. Units codes; res 1 code (canonical cells are single
  captures, the charter's one-code resolution; also the exact bound 8-bit rounding puts on a
  mean-minus-median). Why: the impulse shows the body's kernel directly; memo A reads the
  shipped halo at several times Apple's in both receded endpoints, and memo E shows the
  alternative narrow-term readings separate there by 20 codes. The peak sees a crisp core, the
  annulus a halo that spreads.
  Why the floor (version 2; the gate review of b151aff4, finding 9): the floor ring is what peak
  and annulus subtract, and it lies inside the narrow term's own reach (sigma_n about 4.1-5.4 pt
  in the receded pose puts 10-25 % of a halo's centre value at 8-10 CSS px). A halo that is too
  WIDE raises the ring with everything else and reads as a smaller, "closer" peak and a flat
  annulus; read absolutely, the floor sees the rise. It also carries the body's level beside the
  dot (on black: the black branch's level), which the stop now compares too.
  Admission: the whole r < 10 disc at depth >= 2 CSS px AND the dot's centroid past the lens
  extent L'(span) = 1.337 min(0.25 span, 20) (14.707 at span 44, 26.74 at span 96). This admits
  exactly one dot per shape, (160, 104) on the capsule and on rrect-md, at both scales; no
  population cell is left with none.

STOP P, photo band-pass chroma energy (26 cells, M1/M2's bed)
  Population: every untinted calibration/validation photo scene in the four standard profiles,
  WebGPU: light 9 scenes x 2, dark capsule and rrect-md in both poses x 2.
  Reading: OKLab (a, b) of the encoded image over memo A's deep body, depth >= D with
  D = max(6, min(16, half the inradius)): 11 capsule and toolbar, 8 rrect-sm, 16 rrect-md and
  rrect-ml. Gaussians normalised to that same region (the support IS the region); bands
  F = G(1) - G(4) and M = G(4) - G(16) in CSS px; E = sqrt(mean over the region of
  (Da^2 + Db^2)). Units OKLab (a, b) (text tables print x1e3). res_band: the band energy of the
  one-code quantisation field (the difference of two independent roundings, variance 1/6 per
  channel) at the NATIVE image's colours, propagated exactly through the masked filter by a
  secant Jacobian; 0.12-0.28 x1e-3 on F and 0.032-0.074 x1e-3 on M, frozen per cell in the
  declaration and recomputed (to 1e-9) on every run. Why: F is where memo A reads the light
  receded mottling, M is where the heavy blur sets chroma structure; M1/M2 read a ratio and a
  level, not the scale the chroma lives at.

CHANGES FROM THE STARTING DESIGN (each with its evidence in the declaration)
  1. Stop H's admission adds the lens clause. The rrect-md side dots (centroid depth 16) are
     refracted in both renders: the halo's luma centroid sits 1.4-2.5 CSS px outward on the
     shipped render and 0.6-2.75 on Apple's, against <= 0.23 on every admitted dot. Rings centred
     on the backdrop centroid would read the lens, not the body.
  2. Stop P's support is the deep region, not the interior at depth >= 2: that interior's band
     2 <= depth < D would supply 15-62 % of G(16)'s weight (5-28 % of G(4)'s) over the region,
     and it holds the lens and Apple's edge structure.
  3. Stop P's resolution is the DIFFERENCE of two roundings (sqrt 2 times one rounding's energy),
     because the stop compares two independently rounded renders; computed analytically, not
     drawn.
  4. D comes from the inradius, so the region is the same at 1x and 2x.
  5. Native channels at 255 are kept (15-30 % of deep pixels on light rrect-md and rrect-ml):
     all three images are 8-bit outputs that clip alike, which is not X21's case of an unclipped
     prediction scored against a clipped channel. The fraction is reported per cell.

RUN (python3.12 beside this file; -B keeps bytecode out of the repository)
  export OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
  python3.12 -B stops.py --candidate-root <scratch capture tree> --document <scratch doc> ... \
      --out run.json --text run.txt           # --stop halo|chroma|both, --shipped-root DIR
  python3.12 -B proof.py                      # -> proof.txt, about 3-5 minutes on a quiet machine
  python3.12 -B stops.py --candidate-root /Users/new/Developer/GitHub/designer/packages/calibration/web-captures \
      --baseline --out baseline.json --text baseline.txt
  A candidate tree has the canonical layout (<profile>/<scene>/<scene>__webgpu.png and
  cell__webgpu.json, as a scratch stage's capture tree does). Each capture must name its scene,
  scale, scheme and material document; captures of one scheme must name one document set; every
  document that is not shipped must be declared by --document FILE, matched by hash (a scheme
  left at the shipped documents needs no declaration, but a run whose every scheme is left there
  is refused). The run is stamped admission.mode "candidate" with the documents named, or
  "baseline" under --baseline. Exit 0 only when both stops pass; a refusal exits 1 with its reason.

PROOF (proof.txt, 38 checks, 0 failed; version 2, 2026-09-30, 140 s)
  Geometry equals every shipped cell's report surfaces (42 cells, 0.0 CSS px). Admission derived
  from geometry equals the declared dots. Stop H: the reader equals an independent per-pixel loop
  to 4e-14 on all three statistics; rounding moves a statistic by <= 0.79 code (tolerance 1);
  Gaussian halos of known amplitude (sigma 1-5 CSS px, A 8 and 40, both shapes, both scales) read
  within 0.98 code of their continuous values (tolerance 1 + 0.03 A); side dots at three times
  the amplitude change nothing. The floor (G9): against a narrow Apple (sigma 1.5, A 8) and a
  narrow over-strong shipped halo (sigma 1.5, A 40) on a flat 120-code body, a too-wide candidate
  (sigma 20, A 30) reads peak 3.0 (Apple 5.4-5.7, shipped 26.3-27.3) and annulus 1.73-1.77
  (Apple 0.18-0.21, shipped 1.16; margin 0.39-0.43) and passes both, while its floor reads 147
  against 120 and FAILs, so the cell FAILs, on both shapes at both scales. Stop P: the reader
  equals an FFT implementation to 3e-16 relative on every shape and scale; rounding moves an
  energy by <= 0.30 res; band-limited plane-wave noise reads within 0.40 of its tolerance
  (res + 1 %) against its continuous Gaussian responses; the analytic res matches a 64-draw Monte
  Carlo within 1.8 % (tolerance 5 %). End to end: the canonical tree as the candidate is refused
  (no output); the identity, the shipped captures re-named at four declared scratch documents,
  reads dCand - dShip = 0 on all 100 statistics of 42 cells and passes, stamped candidate;
  --baseline over the canonical tree does the same stamped baseline, and --baseline over any
  other root is refused; halos moved 3 codes away from Apple in core and annulus (2.78-3.00 after
  clipping) FAIL on every peak and annulus with the floor untouched (dCand = dShip), half a code
  passes; the whole r < 10 disc moved 3 codes away from Apple's floor (no channel clipped)
  leaves peak and annulus within 6e-14 and FAILs floor by exactly 3 codes on all 16 cells;
  chroma moved away in F (by 1.5-33 res) and in M (27-307 res) FAILs on all 26 cells, a one-code
  re-rounding field passes all 26; scene, scheme and size mismatches, a mixed document set, an
  undeclared document with or without any --document, and a stale shipped tree are refused; a
  scheme left at the shipped documents needs no declaration; a missing candidate cell reads
  UNMEASURED; holdout, probe and recorded natives raise before a path is formed.

BASELINE (baseline.txt; native vs shipped, medians with ranges there)
  Stop H peak, codes:      light active 23.2 vs 18.2 (shipped both above and below: 2.7 on 2x
                           rrect-md against 21.3); light receded 5.9 vs 25.6; dark active
                           12.4 vs 18.5; dark receded 2.7 vs 37.7.
  Stop H annulus, codes:   light active 1.8 vs 1.4; light receded 2.0 vs 2.4; dark active
                           0.4 vs 2.6; dark receded 1.1 vs 4.0.
  Stop H floor, absolute   light active 133.5 vs 132.0; light receded 134.0 vs 138.5 (the
  codes (version 2):       tinted capsule 108.8 vs 127 / 128, dShip 18-19); dark active 33 vs
                           54 (dShip 21); dark receded 23 vs 30.5. The shipped floor sits above
                           Apple's on 14 of 16 cells (below only on light capsule rest, 1x 130
                           against 134 and 2x 132 against 133).
  Stop P F, x1e-3:         light active 5.16 vs 5.20; light receded 4.26 vs 6.72 (the
                           mottling); dark active 6.83 vs 4.66; dark receded 4.64 vs 2.36.
  Stop P M, x1e-3:         light active 20.4 vs 17.2; light receded 19.7 vs 20.5; dark active
                           28.5 vs 14.7; dark receded 26.9 vs 9.0 (the shipped dark body carries
                           a half to a third of Apple's mid-band chroma).
  Tight cells, where the shipped render is already within two resolutions of Apple and any move
  away fails: Stop P F on light 2x rrect-md receded (dShip 0.041 against res 0.129 x1e-3) and
  light 2x rrect-sm active (0.208 against 0.139); Stop H annulus on ten light cells and two
  dark ones (dShip 0.15-1.98 codes), and the peak on light 2x rrect-md receded (1.92). Since
  version 2, Stop H floor on light 2x capsule rest (dShip 1.0 code); every other floor has
  dShip 3.0-21.0 codes.

LIMITS
  - Stop H reads luma only: a coloured fringe is invisible to it, and a displaced halo reads as
    a changed peak. One dot per shape carries each cell, so rrect-md's lens band is not read.
  - Stop H's annulus is 0.17-5.2 codes against a 1-code resolution: it stops a halo that spreads
    substantially, not a subtle reshaping.
  - Stop H's floor is absolute: it moves with the body's level beside the dot as well as with the
    halo's reach, so a halo widened while the level beside it falls could read unchanged, and a
    candidate that only moves the black level moves it. It reads one ring (8-10 CSS px), not the
    halo's profile.
  - Stop P reads chroma only and the deep body only; its bands overlap; an energy is blind to
    where the structure lies.
  - Stop P's resolution is the 8-bit quantisation floor, not a cross-sitting bar. Where a
    candidate crosses to the other side of Apple's value, an unmeasured re-capture spread of the
    native could move the verdict (canonical cells are single captures).
  - Neither stop reads the CSS tier, the accessibility profiles, holdout or probe cells.
  - The rehearsal (clause 3) can run these stops on memo A's body-swapped images by writing them
    into a tree of this layout with the shipped cell__webgpu.json beside each; nothing here
    rehearses.
