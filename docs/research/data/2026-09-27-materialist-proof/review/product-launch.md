# product-launch: the source reading (reading 3), pre-fix

Reviewer: `doperpowers:reviewer-high` (astra/high), read-only with bounded browser checks, 2026-09-27,
against the page as built by its maker and the audit at `audit/product-launch.json`.

## §8 table (summary)

| Check | Result | Evidence |
|---|---|---|
| 1 layer | holds | Navigation, the display action, three configuration actions; story and specs in ordinary DOM (`Chrome.tsx:139–234`; `Sheets.tsx:99–347`). |
| 2 layer | holds | Plain button inside the morph; runtime's single glass track for the segmented control. |
| 3 layer | holds | Five surfaces, five functions. |
| 4 material | holds | All `regular`. |
| 5 material | holds | Untinted; selection and swatches on children. |
| 6 material | fails | At the Body landing the nav and lower controls sit over the nickel macro's defocused grey, not its knurling (`content.ts:107–112`; `DESIGN.md:214–217`). |
| 7 material | holds | Flat tonal content; the wood, metal and leatherette are the product's photography. |
| 8 geometry | holds | Anchor named; 22−6 and 28−8 inner radii (`DESIGN.md:73–78`). |
| 9 geometry | holds | Capsule housings, r28 platter; audit boxes 58 against the record's 56. |
| 10 geometry | holds | 44/44/58/56/58, thickness 8; menu ~160. |
| 11 grouping | holds | Gap derived from the selected document and policies (`Page.tsx:126–150`). |
| 12 legibility | unclear | 25/25 both schemes (min 11.21 / 6.67) at fv and menu only. |
| 13 legibility | holds | Mask on the scrolling column; edges derived from host bounds (`styles.css:93–126`; `Page.tsx:297–325`). |
| 14 legibility | fails | The selected finish disappears under forced colours (`styles.css:753–755, 863–875`; `shot-forced.png`); menu focus and dismissal incomplete. |
| 15 layout | holds | Viewport-fixed full-bleed canvas; measured final inset. |
| 16 layout | holds | The 0.4 dark-scheme dim is applied to the whole painted photograph, a scheme decision, not a bar scrim (`plane.ts:205–223`). |
| 17 motion | fails | The navigation `GlassSurface` is not `interactive`, so its links get no press (`Chrome.tsx:142`; `surface.tsx:199`). |
| 18 colour | holds | Runtime pole at full strength on child labels; colour in the photographs. |
| 19 honesty | fails | CSS hints measured from the TARGET photograph while the canvas dissolves for 480 ms (`Page.tsx:362–375`; `plane.ts:209–218`): nav declared 0.001 with the painted mean at 0.237. Hints correctly withheld on WebGPU (`Page.tsx:204, 477`). |

## r23

(a) holds (`LensMenu.tsx:175–188`). (b) **fails** (no colour swap, but the nav housing has no press). (c) holds.

## Span exceptions

None. Smallest registered surface 44.

## Findings

1. [P2][material] Reframe or replace the nickel macro so both control bands sit over structure (`content.ts:107–112`).
2. [P2][honesty] Derive CSS hints from the currently painted dissolve (`Page.tsx:362–375`).
3. [P2][legibility] Complete the lens menu's dismissal and focus lifecycle (`LensMenu.tsx:154–164`).
4. [P2][legibility] Preserve the selected finish under forced colours (`styles.css:753–755`).
5. [P2][legibility] Forward scrolling keys from focused floating chrome (`Page.tsx:411–412`).
6. [P2][motion] Opt the navigation surface into channel-based press (`Chrome.tsx:142`).

No `[layer]` failure.

## What the skill did not carry

1. `vitrea.md:100–103` hint precedence is wrong; this maker rejected it correctly (`Page.tsx:204, 477`)
   and the general principle is to describe the PAINTED state, transitions included.
2. `vitrea.md:138–140` "measured once per frame" overpromises; `invalidateGeometry()` on the host
   handle (`root.ts:3588–3589`) is the explicit route the skill should name.
3. Portal focus order and a menu's complete lifecycle (focus restoration, Tab exit, outside
   dismissal) are the app's; the morph example does not show them (`vitrea.md:175–177, 262–267`).
4. A custom `GlassSurface` is not interactive by default (`surface.tsx:199`); the React opt-in is
   not carried.
5. The segmented indicator's visible selection treatment is the app's
   (`segmented-control.tsx:275–289`), so a policy pass is not a forced-colours pass.
