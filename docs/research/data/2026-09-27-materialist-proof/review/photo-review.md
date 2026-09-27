# photo-review: the source reading (reading 3), pre-fix

Reviewer: `doperpowers:reviewer-high` (astra/high), read-only, 2026-09-27, against the page as built by
its maker and the audit at `audit/photo-review.json`.

## §8 table (summary)

| Check | Result | Evidence |
|---|---|---|
| 1 layer | holds | Three registered surfaces hold controls; metadata, histogram, filmstrip off glass (`Controls.tsx:69–108,309–365`). |
| 2 layer | holds | Platter children are plain buttons and fills. |
| 3 layer | holds | Adjust, compare, decide. |
| 4 material | holds | All `regular`. |
| 5 material | holds | No tint; no host fill or blur. |
| 6 material | fails | Seven of ninety surface/frame pairs over near-flat image (`DESIGN.md:174–179`; frame 25 under the palette). |
| 7 material | holds | Crop matte and grid are functional overlays. |
| 8 geometry | holds | Anchor named (the square photograph). |
| 9 geometry | fails | Palette registers at span 54 with fixed r26, not the recorded 52/r26 capsule. |
| 10 geometry | holds | Spans 40, 52, 54, platter 244; thickness 8. |
| 11 grouping | holds | One group per function. |
| 12 legibility | unclear | 14/14 pairs both schemes (min 11.17 / 8.08); the thirty-frame sweep is the maker's. |
| 13 legibility | fails (recorded exception) | The photograph sits under the controls at rest; the brief asks for it. |
| 14 legibility | unclear | Emulation passes hold; unfocused pose not independently captured. |
| 15 layout | fails on open-platter resize | Open morph does not follow the moved photo rectangle (`morph.tsx:470–485`). |
| 16 layout | holds | No host decoration. |
| 17 motion | fails | Open platter's plain controls have no press channel; morph disables host interaction when open (`morph.tsx:636–641`). |
| 18 colour | holds | Neutral chrome; saturation from the photograph and the white-balance ramps. |
| 19 honesty | fails on open-platter resize | Hint measured from the intended platter rectangle, not the drawn box (`App.tsx:218–223`). |

## r23

(a) holds (one `GlassMorph`, `Controls.tsx:69–108`). (b) **fails for the open platter** (no press
channel on its controls). (c) holds.

## Span exceptions

None.

## Findings

1. [P1][material] Flat-backdrop phases (`App.tsx:67–80`; `DESIGN.md:174–179`).
   **Session ruling:** bounded by design intent, not fixed in the demo. The plane is the
   photographer's frame and cannot be altered; per-frame control placement is worse for the task
   than the faint edge Apple's own glass shows over a flat region. The demo records the phases
   as a reproducible measurement; the skill is corrected to distinguish a plane designed flat
   (the ban) from user content that is locally flat in some phases (the material's own edge and
   shadow carry it, and the record says so).
2. [P2][honesty] Open platter and its hint on the same footprint after resize (`App.tsx:218–223`).
3. [P2][motion] Press feedback on the opened platter's plain controls (`Controls.tsx:178–185`).
4. [P3][geometry] Closed palette's box (54) against its declared capsule (52/r26) (`Controls.tsx:30,73–74`).

Not findings: the app-authored child ink at alpha 1 (permitted by SKILL.md 220–224); the
selected-state wells (selection, not press).

## What the skill did not carry

1. Real media needs a prescribed response to locally unstructured phases ("inside an image" vs
   "over usable structure").
2. The React recipe does not say the open morph host is non-interactive, and gives no recipe for
   press on non-glass children inside a platter.
3. The morph's open host does not follow a layout change; geometry-dependent hints must measure the
   drawn box.
4. `vitrea.md:100–103` texture/hint precedence is wrong (also found on music-player).
5. Teach capsule geometry as radius = half the MEASURED span; `examples.md:135–137,160–162` keeps a
   fixed-radius tool column while §8 check 9 asks for capsule housings.
6. Media behind controls vs readable content under a bar: the photo-review example puts every
   control inside the photograph while check 13 says content does not sit under a control at rest.
7. The evidence contract for a contrast claim: keep the per-phase, per-label measurements.
