# W32 G1 — the eye, on the sheets this gate's read wrote

Claims **§5.168**. Thirty sheets under `sheets/`, written by `sheets.ts` from the tree this gate's
canonical read wrote, with each cell's capture asserted to name the shipped document bytes — the
active document AND the receded one — before a pixel is copied. Layout: **native | WebGPU | CSS |
ΔE × 8**, or **native | WebGPU | ΔE × 8** where the read took no CSS capture of that cell (the
ladder's probe scenes are captured on the CSS tier only on the two 1x standard profiles, which is
the read's shape and not a choice made here).

Two cells are named rather than photographed, and it is the PROFILE's scene declaration in
`scenes.json` that decides it, not the document: the two dark standard profiles declare neither
`photo__rrect-ml__rest` nor `checkerboard__rrect-lg__inactive`, so the span-128 ACTIVE sheet on the
dark beds is the ladder's `checkerboard-8` rung and the far-halo cell appears on the light beds
alone — where it exists on a sheet at all only because `checkerboard__rrect-lg__inactive` is a
HOLDOUT scene and this gate read the holdout once at these bytes.

**Metrics are not the whole verdict** and this file is the other half. What follows is what the
sheets show, including where they show something the numbers do not.

## The thin capsule's exterior — the difference is now inside the body, and nothing else

`photo__capsule-button__rest`, span 44, all four standard beds. At ×8 amplification the ΔE panel is
**black everywhere outside the silhouette** and carries the whole residual inside the body, as a
mottled interior structure. Before the fit the same cell's inner bands read `Δa` −0.0187 / −0.0149
— the reading the charter's Purpose opens on, where one pooled statistic had called the thin regime
"right" by dilution — and they now read 0.00096 / 0.00015 as the bed's median.

So §5.160 §6's eye and §5.162's arithmetic agree for the first time: the eye said the thin
difference was "confined to the body", the per-band reading said the exterior was wrong, and after
the fit the exterior is black at ×8 while the body is not. **The body is this bed's open work and
the exterior is not.** On the two accessibility beds the same cell still carries the population's
worst inner-band reading (0.02168 against 0.04012 before), and the sheet says why it cannot close
here: the fold overwrites all six anchors with `reducedTransparencyOcclusion`, which X3 forbids this
wave to move, so those beds got the outset and nothing else.

## Span 160 — the exterior closes, and the level contours are absent on both sides

`checkerboard-8__rrect-lg__rest`, span 160, both schemes at both scales. This is the span C1 was
declared for and the span the wave's `T` moved 0.00796 → 0.00134 on 1x light.

**On the LIT backdrop pixels the two renders agree to within one byte through the entire
falloff.** Below `rrect-lg` on the 1x light bed, reading down one column of the checkerboard's
white squares from 3 CSS px under the contour to the frame's edge, the native side runs
237, 243, 244, 244, 245, 246, 246, 247, 247 and the WebGPU side
237, 243, 244, 244, 245, 246, 245, 246, 247 — the shadow's whole falloff, the same byte at seven
of nine steps and one off at the other two. Over the whole exterior outside the `0-3` band, on all
four span-160 sheets, **96.4 to 100 % of the lit pixels are within one byte** of the native and
about half are exactly equal; the largest disagreement anywhere is 2 bytes on the dark beds and
1 on the light ones (`b4-black-floor.py`, committed beside this file with its output). That is a
stronger reading than "the panel is black", and it is the one the pixels support.

**The one caveat is the black floor, and the ΔE panel shows it as a mid-grey rather than as
black.** *(Corrected 2026-09-21, W32 G1 review closure; claims §5.168 §10, finding B-4. This
paragraph said the exterior was "black past the rim band on every one of the four" and that the
ΔE panel "shows no structure there either". It is not: a mid-grey checkerboard fills the shadow
band on all four sheets.)* On the checkerboard's BLACK squares Apple reads exactly 0 and vitrea
reads 1 — never more — on 3,334 of the 9,440 native-black exterior pixels at span 160 on 1x light,
2,188 of 17,532 at span 128, and **0 of 29,330 at span 44**. OKLab takes a cube root of linear
light, so one sRGB byte at the floor is a ΔE of **0.0672** — about two-thirds of the distance from
grey 128 to grey 160 — and the sheets' ×8 amplification turns it into byte 137, a mid-grey. Present
at 160 and 128, absent at 44, which is below `liftSpanMin` (64): it points at `liftAmplitude`, the
lift this wave did not move. **Pre-existing, not a regression** — and now the dominant visible
exterior residual, because the shadow itself matches. The charter's Deferred list and the tracker
carry it.

**The level contours below `rrect-lg` are ABSENT on both sides**, which is the reading asked for.
Neither the native nor the WebGPU panel shows a banded step in the exterior below the surface — no
ring, no terrace, no second edge. What the ΔE panel carries at span 160 is the RIM, a bright closed
ring one to two pixels wide, the black floor's mid-grey checker, and the interior's checker
structure. The rim is §5.62's and the `0-3` band's, which every form of C1 excludes; the interior is
the body's.

**A reading hazard, stated for whoever makes the next sheet.** A ΔE × 8 OKLab panel over a backdrop
containing pure black **cannot be read as "black exterior" without the LSB check**. The cube root's
derivative diverges at zero, so the smallest representable difference at the floor amplifies to a
mid-grey while the same difference at grey 128 is invisible — the panel says "large" where the
pixels differ by one byte. Read the bytes before reading the panel: a one-line count of exterior
pixels where the native is 0 and the web is not settles it, and `b4-black-floor.py` is that count.

The CSS panel at span 160 flattens the backdrop's checker almost entirely where the native and the
WebGPU panels keep it. That is the CSS tier's structure residual, recorded and unbounded by
Decision Log 23 and unchanged by this wave, which moved the same three lengths onto that tier and
nothing else.

## The inactive halo — gone, and the hairline it leaves is visible

`checkerboard__rrect-lg__inactive` at 1x and 2x light — the tracker's far-halo cell, measured at
**17.42** on the WebGPU tier and 15.89 on the CSS one when no active strip on either sheet exceeded
5.92. It is a HOLDOUT scene and exists on a sheet only because the holdout was read once at these
bytes.

**The halo is gone.** The native panel's checkerboard runs up to the body's contour with no
darkening at all; the WebGPU and CSS panels now do the same; and the ΔE panel is **black in the
entire exterior**. Before this wave vitrea drew the ACTIVE shadow out to 42.93 CSS px in that pose,
because both receded documents carried their active document's anchors leaf for leaf.

What the ΔE panel carries instead is the BODY, brightly. Apple's receded body over a 16 px checker
is nearly flat grey; vitrea's shows the checker through it. That is the receded body's diffusion —
§5.154 §9's open item and the tracker's, not this wave's — and with the halo removed it is now the
only thing on that sheet.

**And the hairline is legible in the NATIVE panel.** On `photo__rrect-ml__inactive` at 1x dark the
native panel itself shows a thin dark stroke following the body's contour that neither vitrea panel
draws — that is where it is read, and its width is §5.166 §7's measurement off the fixture pixels
rather than anything counted on a sheet. The ΔE panel carries a bright closed outline in the same
place, and after finding B-4 that panel is not evidence of width on its own: an amplified OKLab
distance over a dark backdrop is bright wherever the two sides differ at all. That is the one device pixel
§5.166 §7's closure measured off the fixture PNGs, and it is now the whole of Apple's receded
exterior that vitrea does not have. It is a RIM term and this wave's Deferred list names it.

## What the sheets show that the numbers do not

- **The dark scheme's receded BODY is further from Apple's than its exterior ever was.** On
  `photo__rrect-ml__inactive` at 1x dark the ΔE panel is saturated across the whole interior while
  the exterior is black. The exterior fit is finished on that cell and the body is not started.
- **The CSS tier's exterior now tracks the WebGPU tier's by eye at every span**, which is the
  mirror carrying all three lengths. Where the two panels differ is the interior, and at span 160
  the difference is large.
- **No sheet shows a shadow that is too SHORT.** The residual extent after the fit is −0.50 to
  +3.50 CSS px across the NINE backdrops `anchor-solve.txt` §6 tables, and exactly one of its
  thirty-nine rows is negative — `32 photo`, 8.50 native against 8.00 web. Everywhere else
  vitrea's extent is still the wider of the two, which is what a spread of 0.50 against Apple's
  measured 0.0–1.0 should produce. *(Corrected 2026-09-21, W32 G1 review closure; claims §5.168
  §10, finding N-4: this bullet said "+0.00 to +3.50 CSS px across twelve backdrops, all of it
  positive". Twelve is §5.166 §10's NATIVE reading over a different table. Half a CSS pixel at
  span 32 is below what the sheets resolve, so the bullet's heading stands.)*
