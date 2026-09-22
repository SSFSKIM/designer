# W32 G2 — the eye, on thirty-one sheets and three demo rows

*The landing's own look, claims §5.169 §5. Every panel comes from the CANONICAL
`packages/calibration/web-captures/` — the tree the parent copied at W32 G1's
merge — and `sheets.ts` asserts per cell that the capture names the SHIPPED
document bytes, the receded document included, and refuses rather than
photographing a stale one. `sheets.txt` beside this file carries that assertion's
output for all thirty-one.*

**The verdict first: nothing here stops the landing.** Every difference this eye
found is a residual that is already measured and already recorded — three of them
with numbers this gate adds to. The one thing that is NEW is not a defect: it is a
second, independent confirmation of the black floor W32 G1's review closure found,
read off a different bed by a different route, with the control that makes it a
statement about `liftAmplitude` rather than about the renderer's black.

## 1. The exterior, which is what this wave moved

**On the `photo` bed the exterior is gone from the difference panel.** At span 44
(`photo__capsule-button__rest`, 1x light), at 128 and at 160 on all four standard
profiles, the ΔE × 8 column is BLACK from the contour outward — no band, no halo,
no falloff visible at eight times gain. What is left on those panels is entirely
inside the body: a bright ring on the contour and the interior's own structure and
chroma. On the dark beds the interior is brighter still, which is the cell
`MISSED_27_ROWS` carries at `oklabDeltaEP95` 0.20095 and is not this wave's.

That is the wave's own claim, seen rather than scored: C1 reads 0.00088–0.00391
over twelve bed × span rows against ≤ 0.0042, and the picture agrees — at eight
times gain there is nothing outside the contour to look at on the bed the eye
reads a body over.

**The `photo` bed has no native-black exterior pixel anywhere**, which
`sheets.txt` prints under every one of its panels. That is why the exterior looks
clean there and needs the paragraph below beside it.

## 2. The black floor, confirmed from a second direction, with its control

W32 G1's review closure (§5.168 §10, finding B-4) found that over a backdrop pixel
Apple renders as exactly (0, 0, 0), vitrea renders (1, 1, 1) — never more — and
that a ΔE × 8 OKLab panel draws that one byte as a MID-GREY, because OKLab takes a
cube root of linear light and its derivative diverges at zero. This gate
photographs B-4's own three spans on the profile it was read on and counts the
pixels under each panel (`sheets.txt`, the "black floor's own bed" band):

| cell, 1x light | native-black exterior px | web at exactly 1 | above 1 | worst byte |
| --- | ---: | ---: | ---: | ---: |
| `checkerboard-8__capsule-button__rest` (span 44) | 29,330 | **0** | 0 | **0** |
| `checkerboard-8__rrect-ml__rest` (span 128) | 17,532 | **2,188** | 0 | 1 |
| `checkerboard-8__rrect-lg__rest` (span 160) | 9,440 | **3,334** | 0 | 1 |

Those are B-4's three numbers, reproduced to the pixel by a TypeScript reader that
shares no code with `b4-black-floor.py`, and the panels say the same thing by eye:
at spans 128 and 160 the difference panel carries a faint grey checkerboard in the
exterior, and **at span 44 the exterior is pure black with no pattern at all**.
Span 44 is below `liftSpanMin` 64, which is what makes the reading a statement
about `liftAmplitude` rather than about how the renderer writes black.

`halo.txt` reads the same thing from the other end, over the far exterior — every
pixel more than 12 CSS px outside the component's box, W29 G3b's own band and
amplification — on the 16 px `checkerboard` bed, before and after:

| cell | tier | 0.21.0 | shipped |
| --- | --- | ---: | ---: |
| `checkerboard__rrect-lg__inactive`, 1x / 2x light | WebGPU | 34.82 / 34.78 | **0.00 / 0.00** |
| the same | CSS | 16.74 / 17.11 | **0.00 / 0.00** |
| `checkerboard__rrect-lg__rest`, 1x / 2x light | WebGPU | 20.67 / 20.54 | 11.98 / 12.76 |
| the same | CSS | 4.39 / 5.04 | 2.34 / 1.94 |

The active pose halves and does not clear, and the maximum on **every** WebGPU row
before and after is exactly **137.10** — which is ΔE(OKLab) between sRGB (0,0,0)
and (1,1,1), 0.0672, times eight times 255. The CSS tier, which cannot paint a
lift at all, is five times cleaner in the same band on the same cells. A tier that
does not draw the term does not have the residual: that is the strongest evidence
this gate has that what is left in the active far exterior is the lift's and not
the shadow's, and it is a reading rather than a verdict. Nothing here moves
`liftAmplitude`; the measurement that would decide it is the wave's Deferred item.

## 3. The recede, which is the picture Decision Log 2 is made of

**On every inactive sheet the exterior difference is nothing.** On
`photo__rrect-lg__inactive` and `photo__rrect-ml__inactive`, on all four standard
profiles, the ΔE × 8 column is black outside the contour edge to edge. And the far
exterior on the holdout `checkerboard__rrect-lg__inactive` reads **0.00 mean and
0.00 max on both tiers and both scales** — vitrea's capture is byte-identical to
Apple's out there. The tracker's far-halo entry measured 17.42 on the WebGPU sheet
and 15.89 on the CSS one; both are zero now, and the entry closes on a number
rather than on an impression.

Put beside the harness, the same thing reads as a shape rather than a statistic.
`demo-beside-harness-160-receded.png` is Apple's inactive capture, vitrea's, the
`/laws/` stage with the pose toggled to receded, and the site's material stage:
the checkerboard runs up to the plate's edge on all of them, with no band under
it anywhere. `demo-beside-harness-160.png` is the same row focused, and there the
band is under every plate on all four panels.

## 4. What the inactive sheets DO show, and where it is already written down

**Apple's receded body is nearly opaque and vitrea's is not.** On
`checkerboard__rrect-lg__inactive` at 2x light the reference's plate is a
near-flat grey that passes almost none of the checker, and vitrea's passes it
plainly; the difference is the whole interior. The metric says the same thing and
says it in the opposite direction from the active pose: `interiorStdDevNative`
0.01526 against `interiorStdDevWeb` **0.03705**, a factor of 2.43 the wrong way,
where on the same cell's active pose it is 0.04622 against 0.03019, a factor of
0.65. **The structure deficit reverses its sign with the pose.**

This is not new and it is not this wave's: claims §5.154's eye recorded it in as
many words at W29 G3b — *"the receded body passes too much of the backdrop's
structure… the level is right and the diffusion under the recede is not"* — and
recorded why it was not fitted, which is that no inactive calibration cell above
span 96 existed to fit it on and the cells that show it are holdout. **That reason
is weaker after this wave than before it**, and the Deferred-at-close list says so:
Decision Log 1 (b) widened the read set to nine inactive probe scenes at spans 128
and 160, so a bed that can carry the fit now exists as probe rows where it did not
at W29.

Two more, both recorded before and both unmoved here: the CSS panel on every
`photo` sheet is visibly flatter and greyer in the body than the WebGPU one, which
is W31's chroma decline on that tier (§5.164 §5, the two `dom` rows in
`MISSED_27_ROWS`); and every panel carries a bright ring at the contour, which is
**Apple's one-device-pixel contour stroke, which vitrea does not draw** — the term
that stopped cancelling B3, and it is one term on both poses rather than two.

*Re-stated 2026-09-22 at this gate's review closure (finding B2;
`contour-stroke.py`, `contour-stroke.txt` beside this file). The sentence above
first read "the body over-filling its declared contour by 3.5–4 CSS px against
Apple's ≤ 1 (§5.62)", which has the sign and the width backwards on this bed.
Read outward from the declared rect one DEVICE pixel at a time on the `photo`
bed, the native is 14 to 30 bytes DARKER than the web at exactly one device
pixel and the two agree to a fraction of a byte from two pixels out — on 22 of
24 cells across six macOS 27 profiles, both poses, both scales. On none of the
24 is the web darker than the native anywhere in the band, which is what an
over-fill would look like. §5.62's 3.5–4 CSS px was measured at W14 on the macOS
26.5 material through the shape axis and is not withdrawn; it is simply not what
these bytes show.*

## 4b. The level contours, named because the clause asks for them present or absent

**ABSENT, on all thirty-one.** The artefact the clause means is what a level law
evaluated in too few steps leaves behind: stepped iso-level bands across the
interior, hard-edged, following the level rather than the content. There are none
on any panel of any bed at eight times gain. What the interiors DO carry is three
things, and none of them is a contour: broad smooth regions that follow the
backdrop's own large-scale structure (the scatter and structure residual, largest
on the dark beds); on the `checkerboard-8` and `checkerboard` beds, the ground's
own pattern read through the body (the same residual at the pitch the ground
supplies it); and on the tinted and `photo` cells a smooth chromatic field with
no steps in it. **The only hard edge anywhere on any panel is the ring at the
contour**, which is Apple's one-device-pixel contour stroke standing un-drawn and
is a RIM term rather than a level one — it appears at the same radius on every
span and every scheme, including the two accessibility beds where the body is an
occluded plate with no structure at all behind the ring. *(Re-stated 2026-09-22,
finding B2: this sentence read "the body's over-fill of its declared silhouette
(§5.62)" and "is a silhouette term". `contour-stroke.txt` reads the band's sign
directly and it is the other way round; the ring's width — one device pixel at
1x and at 2x alike — is the other half of the reading.)*

Recorded as an absence rather than left unmentioned, because an absent artefact
and an unlooked-for one are the same thing in a record.

## 5. The demo beside the harness

`demo-beside-harness-96.png` and `-160.png` put four panels in one row: the
harness's native capture, the harness's WebGPU capture, the `/laws/` shadow stage
at the same span, and the site's material stage. The grounds are not the same —
the harness's `photo` and 16 px `checkerboard` beds against the stage's own 16 px
checker and the site's dark bloom — so the row is a juxtaposition and never a
metric, which `demo-sheet.py`'s header says before it composes one. The span-160
row is deliberately composed against the harness's 16 px `checkerboard` cell so
the two checkerboards in it are at the same pitch.

What it shows: the band under the page's caster is the band under the harness's,
at the same span, on the same pitch of ground, with the same displacement
downward. The site's three plates carry the same band graded by their three spans.
Nothing in the demo draws an exterior the bed does not.

**One thing about the `/laws/` stage itself, as a stage rather than as a
material.** A 16 px checkerboard of #202830 and #d6dde3 is a structured ground and
the shadow multiplies it, which is what makes the transmission legible AS a
transmission — but it also means the falloff is read across hard square edges, so
the GRADE is harder to see than the presence. The readout is what carries the
grade (7.00 / 3.33 / 0.40 % at span 96 against 16.93 / 11.39 / 5.04 % at 160), and
a reader who wants to see it rather than read it has to drag the slider. That is a
property of the bed the stage inherited from the lens law and not of the material;
it is on the Deferred-at-close list as a page decision, with the alternative named.
