# transit-ops: the source reading (reading 3), pre-fix

Reviewer: `doperpowers:reviewer-high` (astra/high), read-only, 2026-09-27, against the page as built by
its maker and the audit at `audit/transit-ops.json`.

## §8 table (summary)

| Check | Result | Evidence |
|---|---|---|
| 1 layer | fails | The alerts sidebar is registered glass holding the operations summary and six incident records read in place (`Chrome.tsx:411–433`). |
| 2 layer | holds | Ordinary DOM children inside hosts. |
| 3 layer | holds | Seven surfaces, each with a job. |
| 4 material | holds | All `regular`. |
| 5 material | holds | Untinted; primary action is a child fill. |
| 6 material | fails | Unbounded panning can leave every control over the uniform land fill outside the district polygons (`MapPlane.tsx:320–330`; `paint.ts:270–284`). |
| 7 material | holds | Cartography, flat fills, one photograph. |
| 8 geometry | holds | Anchor named; 18 px inner radii derived (`DESIGN.md:57–60`). |
| 9 geometry | holds | 44/r22 housings, r26 panels. |
| 10 geometry | fails | The empty suggestion host registers at span 16 (`styles.css:310–317`). |
| 11 grouping | holds | Three top-bar groups; gaps derived from resolved padding (`App.tsx:197–224, 273–305`). |
| 12 legibility | unclear | 182/182 both schemes (min 4.96 / 4.93) at fv and menu. |
| 13 legibility | fails | The platter can open over the selected bus when it was visible before opening (`MapPlane.tsx:265–274`). |
| 14 legibility | fails | Reduce Motion read once at mount (`App.tsx:70`). |
| 15 layout | holds | Canvas fixed to the viewport; usable map rect from host bounds. |
| 16 layout | holds | No host decoration. |
| 17 motion | fails | `.icon-button:active` colour swap on zoom and close (`styles.css:656–658`). |
| 18 colour | holds | Neutral ink; route dots are a legend, severity glyphs are incidents. |
| 19 honesty | fails | Hints measured from the cached basemap after a resettable 300 ms debounce, not the displayed canvas with vehicles (`MapPlane.tsx:200–208`). |

## r23

(a) holds (`present={open}`, `Chrome.tsx:337–345, 663–670`). (b) **fails** (`styles.css:656–658`). (c) holds.

## Span exceptions

None. `.suggest.tx` at 16 px is an empty host's padding, not an exception.

## Findings

1. [P1][layer] Move the incident list onto an opaque content surface (`Chrome.tsx:411–433`).
2. [P1][layer] Separate the vehicle dossier (note, photograph, six facts) from its glass actions (`Chrome.tsx:565–568`).
3. [P1][honesty] Hints from the displayed plane and current footprints on a cadence that cannot starve (`MapPlane.tsx:200–208`).
4. [P2][material] Bound the camera to structured coverage (`MapPlane.tsx:325–330`).
5. [P2][geometry] Do not register an empty 16 px suggestion platter (`Chrome.tsx:336–347`).
6. [P2][legibility] Test selected-vehicle visibility after the platter opens (`MapPlane.tsx:265–274`; `App.tsx:113–120`).
7. [P2][motion] Remove the icon-button press colour swap (`styles.css:656–658`).
8. [P2][legibility] Follow Reduce Motion changes (`App.tsx:70`).

Not findings: app-owned child ink (permitted); seven groups; the derived gaps.

## What the skill did not carry

1. `examples.md:77–80` puts an alerts sidebar with alert rows in the floating inventory; `SKILL.md:111–112`
   says lists stay opaque. Third example contradicting the law (queue, forecast, alerts).
2. `vitrea.md:100–103` "the pixels win" is wrong (fourth demo to hit it).
3. `vitrea.md:138–140` "measured every frame" omits the dirty-host contract (`geometry-sync.ts:8–24,
   164–173, 181–185`; `root.ts:3588–3589` is the handle's invalidation).
4. Runtime API gap: `GlassSegmentedControl` exposes no `onHost` (`segmented-control.tsx:72–93, 262–273`)
   while `GlassSurface` does (`surface.tsx:167–168`).
5. Transient-host lifecycle: `vitrea.md:225–230` (keep mounted, animate presence) and `examples.md:109–112`
   (release and re-register) disagree, and neither meets the span floor with an empty box.
