W41 G2 STOP — the canonical referees fail on structured light-inactive backdrops
================================================================================

Brief step 3: "If a referee fails, stop and report it with the evidence." They fail.

What was read. The stage /Users/new/vitrea-w41/g2-stage-light (declared 780 cells, the
CLAUDE.md recipe; ../canonical/read.py) holds 288 WebGPU rows: the two light standard
profiles (1x 144, 2x 144), calibration/validation/recorded/probe, at the sealed pair
85ad7f7e3e0d / 003940b4c7da, captured 2026-09-29T01:20-01:58Z, each launch after a fresh
X6 pass (../canonical/runs.jsonl). Stage matrix SHA-256
3558cee9f7549beb3d502ea1ff5d581cf2ce2498e04ac5cbc7ee4248a162f69a (not committed; scratch
until publication). The RT and IC WebGPU profiles and the whole CSS tier were refused by
X6 (a foreign Playwright session, `terminal-review`, launched 10:24 local from the main
checkout); nothing was launched for them.

These are the OWNER'S PREVIEW numbers (l1-m1-m2-preview.py over the stage rows against
W36's adopted L1 population and chroma cut), not the regenerated cuts. The regenerated
cuts are being ported to W40's store and will say the same thing formally.

L1 (|interiorMeanWeb - native| <= 0.055, growth <= 0.005 against W33), 98 light rows:
- 12 new absolute failures, every inactive checkerboard cell at both scales: 0.111-0.148
  (pre-W41 0.001-0.033), growth +0.089 to +0.140. The body centre on
  checkerboard__rrect-md__inactive 1x reads native 188, pre-W41 188, E3 210 codes.
- growth failures without an absolute miss: light-solid inactive (+0.005 to +0.007, three
  cells) and photo tint-orange inactive (+0.013/+0.014, two cells).
- the named impulse tint-orange miss improves (0.066 -> 0.060/0.064).
M2 (interior structure within 2 % of the re-baselined reference = the retired pre-W41
generation): all 8 light-inactive photo cells move +14.6 % to +44.6 %. Every one moves
TOWARD native (e.g. photo__rrect-md__inactive 1x: native 0.064, pre-W41 0.044, E3 0.062).
M2 is a regression stop, not a fidelity bound; the failure is real under its own clause.
M1: medians 1.047 (light inactive) / 1.049 (light active) inside [0.8, 1.2]; the one
per-cell movement is the existing named miss photo__rrect-sm__inactive (1x 1.539 -> 1.681,
2x 1.461 -> 1.416). No new M1 failure.
Active cells: every rest-pose row reads 0.0 % structure change (unchanged, as expected).

Mechanism, by eye and by number (the triptychs here: native | pre-W41 | E3, 1x, 2x zoom):
- checkerboard / hc-text: Apple's receded body over a black-and-white texture is a nearly
  uniform grey (188 on the checker); vitrea's receded body shows the texture both before
  and after, and E3, applied per pixel to the blurred backdrop in encoded space, lifts it
  by about 22 codes. The texture's pixels sit at both ends of the input range, outside the
  identified 40-150 domain, where F is its declared end-segment continuation. The pre-W41
  group-level tone solve matched the native LEVEL (188).
- impulse: E3 amplifies the impulse points and adds faint mottling that native does not
  show; the level improves.
- photo: E3's hue and saturation are visibly closer to native and its structure moves
  toward native; the texture-period mottling of G1's sheet06 is faintly present.
This is the spatial question of Decision Log 6 and §5.192 §20 showing up at the canonical
referees: Apple's receded body behaves as if its argument were much smoother (group-level
or heavily blurred), and E3's uniform-backdrop closure says nothing about that.
