# park-trails: the source reading (reading 3), pre-fix

Reviewer: `doperpowers:reviewer-high` (astra/high), read-only, 2026-09-27, against the page as built by
its maker and the audit at `audit/park-trails.json`.

## §8 table (summary)

| Check | Result | Evidence |
|---|---|---|
| 1 layer | fails | The weather platter is a three-day, two-elevation forecast TABLE plus freezing level and sunset (`Planner.tsx:452–489`; `shot-menu-light.png`). |
| 2 layer | holds | Morph children are plain buttons and menu items. |
| 3 layer | holds | Route, weather, permits: three jobs, three hosts. |
| 4 material | holds | All `regular`. |
| 5 material | holds | Untinted; native-button reset only. |
| 6 material | unclear | Closed controls over ridge and forest; platters over the scrolled sheet not captured (the audit scrolls the document, not the page's inner scroller). |
| 7 material | holds | Typography, rules, opaque paper. |
| 8 geometry | holds | Anchor named; 48/24 housings, r28 platters, r20 rows inset 8 (`DESIGN.md:41–47`). |
| 9 geometry | holds | r24 at 48 is the capsule geometry. |
| 10 geometry | holds | Spans 48 and 284; thickness 8. |
| 11 grouping | holds | Three functional groups; spacer keeps the runtime minimum (`toolbar.tsx:211–224`). |
| 12 legibility | unclear | 57/57 both schemes (min 8.77 / 4.77) at fv and weather menu; scrolled, route-menu, CSS and receded figures are the maker's. |
| 13 legibility | holds | The sheet's own fixed scroller carries the mask; no ancestor of the root. |
| 14 legibility | fails | The custom Reduce Transparency switch loses its track, thumb and state under forced colours (`styles.css:444–481`; `shot-forced.png`). |
| 15 layout | holds | Photograph fixed `inset: 0`; measured bar drives mask and scroll padding. |
| 16 layout | holds | No host decoration. |
| 17 motion | holds | Matched-geometry morphs; runtime press channels; no idle motion. |
| 18 colour | holds | Runtime foreground on glass; violet selection and status on paper. |
| 19 honesty | fails | The sheet's contribution to the hint is one paper luma, omitting visible ink and fills (`plane.ts:177–185`); the footer describes the planner from the permits group alone (`Sheet.tsx:354–363`). |

## r23

(a) holds (`Planner.tsx:205–212, 427–434`). (b) holds (`interaction.ts:219–230`). (c) holds.

## Span exceptions

None. Closed span 48; open weather 284.

## Findings

1. [P1][layer] Keep the forecast table on the opaque content layer (`Planner.tsx:452–489`).
2. [P2][honesty] Measure the sheet's visible contribution, not only its paper (`plane.ts:177–185`).
3. [P2][honesty] The footer should name the group whose state it reads (`Sheet.tsx:355–363`).
4. [P2][legibility] Give the custom switch a visible forced-colours state (`styles.css:444–481`).
5. [P2][accessibility] Do not undo destination focus when the weather action navigates (`Planner.tsx:530–534`; `App.tsx:202–209`).

Not findings: the even dark grading of the photograph (recorded, a scheme decision); fixed 48 px gaps
(the spacer still enforces the runtime minimum).

## What the skill did not carry

1. `vitrea.md:100–103` "the pixels win" is wrong; the demo repeats it (`useMeasuredHint.ts:10–12`).
2. Two scroll compositions are both taught (`examples.md:166–170` film-festival keeps a permanent
   photograph band under the bar; `examples.md:211–225` park-trails has paper become the bar's
   backdrop) without saying which "content passes underneath" means.
3. "Transient platter" needs an explicit content boundary: a menu is choices; a read-only table is
   content even inside a dialog.
4. Runtime: a toolbar layout change moves members without invalidating their geometry
   (`toolbar.tsx:509–627`, `211–224`; `root.ts:1727–1749`; `morph.tsx:477–485` writes geometry
   rather than invalidating).
5. Runtime: a matched-geometry morph captures its closed size once (`morph.tsx:421–430, 620–621`).
6. Instrument: `glass-audit.mjs:1070–1076` scrolls the document; a page whose content scrolls in a
   fixed inner element gets no second or third screen.
7. Record correction: Playwright does emulate increased contrast (`DESIGN.md:209–210` is stale).
