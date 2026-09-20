# W29 G4 — the eye, at the macOS 27 material a page now draws

Acceptance clause 7. Three sheets in `sheets/`, and the readings behind every number
below are in `harness-captures.txt` (the captures), `demo-pose.json` and
`real-focus.json` (the page), and `eye-measures.txt` (the arithmetic over the pairs).
Nothing here is gated: no bound, no floor and no threshold is read in this file. What it
is for is the rule the repository states — *metrics are not the whole verdict; when you
change the material, put the capture next to the native fixture and look.*

## What was looked at, and why these cells

`demo-and-harness-{light,dark}.png` carry three bands each.

**The demo band** is the playground at 2×, on headed hardware Chromium, pinned
`active` and pinned `inactive`, with their 8× amplified absolute difference. The pin is
the operable control an adopter can reach and it is deterministic, which is why a sheet
can be built from it (§5.147 §2).

**The two harness bands** are `photo__rrect-md` at rest and inactive, native | vitrea
WebGPU | 8× difference, at the same scale. W28 G4's sheet had one harness band because
only the receded material had moved; this gate moved both, so both poses get one. The
scene is W28's for continuity: a mid-radius pane over the photo backdrop carries the rim,
the outer shadow and a structured interior at once, and it is a calibration cell in both
schemes at 2×.

`real-focus.png` is the same page under a real window-manager focus change rather than a
pin — the browser frontmost, the Finder frontmost, the browser again — read over bare
CDP because Playwright's focus emulation holds a driven page focused and no amount of
activating other applications will change that (§5.148 §4, reproduced at this head in
`demo-pose.json`'s `realFocusLoss` block: `hasFocus` stayed **true** under the driver,
and **false** without it).

## 1. The selection is visible, and a window manager moves it

The readout row the landing added does what it was added for. Pinned `active` the
playground's group state reads `materialDocument apple-macos-27.0-1x-light-standard-glass0.5`;
pinned `inactive` it reads `…-glass0.5-receded`; in the dark sheet both carry the dark
document's key. On `real-focus.png` the same row moves from the active key to the receded
one when the Finder is made frontmost and back again when the browser returns, with the
pin on `auto` throughout and `visibilityState` `"visible"` in all three columns.

That is the first sheet in this project where a **material document** — rather than a
pose, a tier or a policy — is seen changing on screen, and it is what makes the rest of
this file checkable rather than assertive: every band names the material it is a picture
of.

It also found a defect, and the sheet above is the second run. The first run's
`inactive` column named the **active** document while the root had correctly resolved
`inactive`. The cause was one package along: `packages/react/src/store.ts` compared
snapshots on seven core fields and none of the four the platform folds on, so a change
that moved only those was never notified and the panel kept its first answer. Fixed by
comparing every field, pinned by
`packages/react/test/material-document.test.tsx`'s pose case, and recorded here because
the eye is what caught it — no unit test did, and no metric could have.

## 2. What the recede does on macOS 27, seen rather than inferred

The demo band's difference column is the clearest statement of §5.154 §6's finding. On
W28's macOS 26.5 sheets the pose *removed structure*: the broad outer shadow and the
bright rim left, and the difference column was a halo around every surface. Here the
halo is not there. The macOS 27 recede keeps the shadow, so what the difference shows is
a body-level move and an edge move inside each surface's own box, with the exterior
almost clean.

Measured on the harness pairs, the exterior beyond 12 CSS px of the component's box
differs from native by a mean of **0.12–0.16 codes** with a maximum of **3–4** — on
every one of the four cells, both poses, both schemes. The shadow at this span is, to
the eye and to that number, right.

One author tint survives the pose as an achromatic shade, as it did on macOS 26.5:
`Publish` is orange active and a pale neutral inactive at what reads as the same
lightness, in both schemes.

## 3. The residuals, named

Each is a gap to macOS, which the project's rule says must be recorded rather than
accepted silently. Interior statistics are over a 200 × 100 device-pixel box at the
pane's centre, linear luminance; ring statistics are the maximum channel difference
within 12 CSS px outside the component's box.

**(a) The body passes too little of the backdrop's structure through, and far too
little in dark.** Interior standard deviation, native against vitrea:

| cell | native | vitrea | ratio |
| --- | ---: | ---: | ---: |
| `2x-light` `photo__rrect-md__rest` | 0.0467 | 0.0307 | 0.66× |
| `2x-light` `photo__rrect-md__inactive` | 0.0385 | 0.0329 | 0.85× |
| `2x-dark` `photo__rrect-md__rest` | 0.0218 | 0.0066 | **0.30×** |
| `2x-dark` `photo__rrect-md__inactive` | 0.0205 | 0.0067 | **0.33×** |

This is the loudest thing on the dark sheet: Apple's dark pane plainly carries the photo
through it and vitrea's is a near-uniform grey. It corroborates the tracker's
scheme-conditioned entry from the other side — that entry measured `checkerboard` at
0.55× on dark and 1.77× on light, and this reads `photo` at 0.30× on dark and 0.66× on
light. Two backdrops, both schemes, and the dark bed is the more attenuated on both. Any
operator wave that fits a scale-selective scatter on the light bed alone will land on the
wrong side of the dark one, which is what that entry already says and what this sheet
makes visible.

**(b) The dark active body is 0.019 linear too dark; the other three levels are close.**
Interior mean, vitrea minus native: `2x-dark` rest **−0.0196**, `2x-light` inactive
**−0.0134**, `2x-light` rest **+0.0040**, `2x-dark` inactive **+0.0002**. The two that
match are one per scheme and one per pose, so this is not a constant offset; it is the
level law's conditioning, which §5.153 §6 records as still unidentified.

**(c) The receded pose's edge is about twice the active pose's, in both schemes.** Mean
channel difference in the 12 CSS px ring around the box: **1.58** light active against
**3.01** light inactive, **1.68** dark active against **3.76** dark inactive, with
maxima of 60 / 72 / 105 / 115 codes. The recede is fitted on the body (§5.154 §6 reports
the inactive level residual going 0.1174 → 0.01017) and its edge is a subtraction rather
than a fitted term — which is exactly the shape the tracker's "missing contour hairline"
entry names, seen here as an amplitude rather than as a stroke.

**(d) The demo band's middle third is animation, not material.** Inherited from §5.148
and named again rather than cropped: the playground's texture region is an animated
canvas, so its column of the difference is motion. The pose is read on the DOM-backdrop
column, the panel and the controls.

**(e) What these sheets cannot show.** The largest spans are not on them — the exterior
halo the tracker records at 17.42 on `checkerboard__rrect-lg__inactive` is a span-160
holdout cell and this scene is span 96, where the exterior reads 0.12–0.16. The
transit between the two poses is a settled-endpoint reading here as it was at W28, and
remains unmeasured against any native sequence. Reduced transparency and increased
contrast are not on these sheets at all.

## 4. The machine

macOS 27.0 build 26A428, Reduce Transparency 0, Increase Contrast 0, `NSGlassTintAmount`
0.5 read before and after the harness captures (`harness-captures.txt`). Chromium
151.0.7922.34, `channel: "chromium"`, `apple/metal-3`, one capture process at a time
(X7). The screen was borrowed for the few minutes the two page readings take, with the
frontmost application recorded on entry and the machine handed back with the Finder in
front; both readings are in `demo-pose.json` and `real-focus.json`.
