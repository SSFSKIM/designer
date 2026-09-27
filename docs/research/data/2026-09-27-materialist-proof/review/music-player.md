# music-player: the source reading (reading 3), pre-fix

Reviewer: `doperpowers:reviewer-high` (astra/high), read-only, 2026-09-27, against the page as built by
its maker and the audit at `audit/music-player.json`. Verified by the session before the fix wave:
the queue host (`Queue.tsx:41–58`), the press colour swaps (`music-player.css:397–401, 599–601,
683–685`), the forced-colours gradient (`music-player.css:712–718`), and the two skill-level claims
(examples.md 27–30 teaches a glass queue; vitrea.md 100–103 says pixels win over a hint, while
`root.ts:2211–2222` gives a declared luminance precedence and `renderer.ts:1038–1059` suppresses the
measured local tone when a hint is present).

## §8 table

| Check | Result | Evidence |
|---|---|---|
| 1 layer | fails | Permanent `GlassSurface` holds the queue heading, summary, track list, metadata, empty-state prose (`Queue.tsx:41–75`). |
| 2 layer | fails | Nine-row queue after playing the album's first track moves the below-end menu across the volume housing (`Queue.tsx:46,103–111`). |
| 3 layer | holds | Four bodies at rest, each with a job. |
| 4 material | holds | All `regular`. |
| 5 material | holds | No tint, no authored fill or blur on a host; ember accent is a content-plane glyph. |
| 6 material | holds | Both artworks carry broad and fine structure where the controls sit. |
| 7 material | holds | No other depicted material. |
| 8 geometry | holds | Anchor named; radii derived (`DESIGN.md:101–107`). |
| 9 geometry | holds | Single-row housings capsules; queue and menu r24 with padding. |
| 10 geometry | holds | Spans 46, 66, 346; open menu 199; thickness 8. |
| 11 grouping | fails | No reserved space between the growing menu and the volume group. |
| 12 legibility | unclear | 82/82 pairs in both schemes at fv and menu; single/CSS/reduced figures are maker assertions. |
| 13 legibility | holds | No album text scrolls under a bar. |
| 14 legibility | fails | Forced colours loses both slider tracks (`css:712–718`); empty-queue menu without focus. |
| 15 layout | fails | Vertical clearance safe only for the initial sizes. |
| 16 layout | holds | No host decoration. |
| 17 motion | fails | Press is a background swap plus 6% shrink (`css:397–400, 599–601, 683–685`). |
| 18 colour | holds | Monochrome controls; one content-plane accent. |
| 19 honesty | fails | Hint can describe the previous or destination artwork during the dissolve (`Player.tsx:181–201,215–217,243–253`). |

## r23

(a) morph/present: holds (`Queue.tsx:103–124`). (b) press through channels: **fails** (the `:active`
colour swaps). (c) no host transition of opacity/background/filter: holds.

## Span exceptions

None. Smallest registered surface is span 46.

## Findings (severity order)

1. [P1][layer] Keep the permanent queue in the content layer (`Queue.tsx:41–58`).
2. [P1][layer] Bound queue and menu growth before it overlaps glass (`Queue.tsx:46`; `playback.ts:109–123`).
3. [P2][honesty] Keep the declared hint synchronised with the displayed plane (`Player.tsx:215–217`).
4. [P2][motion] Replace colour-swap press states with the runtime's press (`music-player.css:397–400`).
5. [P2][legibility] Forced-colours sliders need a solid track (`music-player.css:712–718`).
6. [P2][legibility] Empty-queue menu traps keyboard focus (`Queue.tsx:175–181`).

## What the skill did not carry

1. `examples.md:27–30` teaches a glass queue sidebar; `SKILL.md:111–112, 359` forbids a list on glass.
   The maker saw the tension and followed the example.
2. `vitrea.md:100–103` and `examples.md:33–37` say the pixels win over a hint on the WebGPU tier and a
   hint costs the texture tier nothing. The runtime gives a declared luminance precedence on both
   tiers and suppresses its measured local tone under a hint. A hint is an override.
3. `vitrea.md:231–245` gives no recipe for several plain actions inside one glass housing or an open
   morph, whose host interaction the runtime disables when open (`morph.tsx:635–641`).
4. `vitrea.md:231–240` does not say that `below-end` is a placement, not a collision-avoiding popover;
   the app owns bounded growth and clearance.
5. A resolved accessibility policy is not the visibility test for authored controls under forced
   colours; the page's own fills and tracks must be inspected after substitution.

The maker's product derivations (imagery, the sounding-release plane change, Save Queue below the
queue) were judged appropriate and need no prescription.
