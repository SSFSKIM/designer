# film-festival: the source reading (reading 3), pre-fix

Reviewer: `doperpowers:reviewer-high` (astra/high), read-only, 2026-09-27, against the page as built by
its maker and the audit at `audit/film-festival.json`.

## §8 table (summary)

| Check | Result | Evidence |
|---|---|---|
| 1 layer | holds | Navigation, the day selector, Tickets and its transient menu; the programme is ordinary DOM (`Bar.tsx:83–156`; `Sheet.tsx:70–75`). |
| 2 layer | holds | Selected-day indicator is a fill; menu items plain buttons. |
| 3 layer | holds | Three surfaces, three jobs. |
| 4 material | holds | All `regular`. |
| 5 material | holds | One tint, `#c42233` on Tickets, removed when its menu opens (`Bar.tsx:39–40,120`). |
| 6 material | holds | Capsules over facades, sign, lamp; not sky (`Still.tsx:26–44`). |
| 7 material | holds | Flat tones, rules and type below. |
| 8 geometry | holds | Viewport edge named; inner radii follow 24/28 (`DESIGN.md:153–156`). |
| 9 geometry | holds | 48/r24 closed; 300×245 r28 open. |
| 10 geometry | holds | 48 → 245, thickness 8. |
| 11 grouping | holds | Three groups; gaps ~96 and ~415 px. |
| 12 legibility | fails | The record's own dark/CSS/unfocused reading of "Sun 21" is 4.36 and QA12 calls it a pass (`DESIGN.md:203,230–234,282`). |
| 13 legibility | holds | Mask on the scrolling sheet itself; the still exposed under the bar (`main.tsx:175–180`; `styles.css:91–104`). |
| 14 legibility | holds | All emulation passes resolve; zero glass under forced colours. |
| 15 layout | holds | Fixed canvas; measured bar bottom drives edge stops and landing offsets (`main.tsx:183–205`). |
| 16 layout | holds | No authored floating ground. |
| 17 motion | holds | `GlassMorph` in place; runtime press; no idle motion. |
| 18 colour | holds | Monochrome apart from the one seed; measured child ink is the permitted escape. |
| 19 honesty | fails | Texture hints are 1440×900 constants that survive crop and layout changes (`Bar.tsx:31–37`; `Still.tsx:38–44,64–75`; ~0.20 declared against ~0.40 at 1280×900); the ticket hint calls a mixed still/mask/paper footprint pure paper (`main.tsx:246–252,309–313`). |

## r23

(a) holds (`Bar.tsx:121–156`). (b) holds (`interaction.ts:219–230`; `segmented-control.tsx:209–222`). (c) holds.

## Span exceptions

None. Closed 48; open 245.

## Findings

1. [P2][honesty] Recompute texture hints when the crop or layout changes (`Bar.tsx:31–37`).
2. [P2][honesty] Measure the composite under the ticket platter at opening, not a binary sheet test (`main.tsx:246–252`).
3. [P2][legibility] Mark QA12 as failing with the recorded exception, or fix the "Sun 21" state (`DESIGN.md:282`).

No `[layer]` or `[material]` failure.

## What the skill did not carry

1. `vitrea.md:100–103` hint precedence is wrong (fifth demo; the maker repeats it at `Bar.tsx:31–34`).
2. The film-festival scroll-edge example is sound; what it lacks is the principle that a surface
   straddling the clear band, the gradient and the paper must describe the visible composite.
3. Runtime defect: `GlassMorph` collapses to 0×0 when Reduce Motion toggles mid-session.
   `root.tsx:408–410` swaps the motion profile; `morph.tsx:315–326` creates new drivers at zero;
   the `placed`/`wasOpen` guard at `440–450` skips placement because `open` did not change; the
   frame subscription writes the zero geometry at `487–500`. The page remounts on a key.
4. `GlassSegmentedControl` positions its indicator absolutely without a positioned track
   (`segmented-control.tsx:251–274`); the page supplies `position: relative`.
5. Portalled chrome needs a deliberate DOM and focus order; the page passes `container` (`main.tsx:96–107`).
6. The quaternary-ink warning scans the whole document's stylesheets (`root.ts:1125–1133`), so a
   legitimate decorative use on a thick platter is discouraged by the zero-diagnostics rule.
