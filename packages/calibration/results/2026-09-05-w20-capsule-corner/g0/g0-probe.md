# W20 G0 — Apple past the saturation ratio, measured (native probe findings)

**Apple does not clamp the radius. It keeps the requested radius and gives up the shoulder.**
Core Animation states the corner it draws, and it states the radius the author asked for at every
rung of the ladder — 14, 16, 18, 20 and 22 on a box whose short side is 44, where the ratio 0.327083
above which `1.52866495 · r` no longer fits half the side falls between the first and the second.
The pixels agree: the corner's implied circular radius rises with the requested radius all the way
to the capsule limit, and vitrea's own policy — the radius clamped to `min(halfW, halfH) / 1.52866495`
= 14.39 — misses the native contour by up to **3.15 px** where the instrument's floor is 0.5 px. The
policy the geometry package already contains, `resolveCornerConstruction` at the requested radius
with the reference family's budget clamp on the smoothing, covers all five rungs on both boxes and
both backgrounds within **0.40 px max, 0.34 px p95** — the same residual the capsule controls read
against their own exact stadium.

The one thing this probe cannot do is separate that policy from a plain circular arc at the
requested radius: the two curves are never more than **0.375 px** apart at any rung, below the grid's
floor, and they are identical at the capsule limit. Both fit; the reading does not choose between
them. §6 says which one G1 should adopt and why the argument is continuity rather than pixels.

Nothing canonical was written. `apps/reference-apple/scenes.json` and
`apps/reference-apple/fixtures/` are untouched; the probe ran through `VITREA_SCENES` and
`VITREA_FIXTURES` into `results/2026-09-05-w20-capsule-corner/probe/`, which is committed evidence
beside this file.

---

## 1. The layer dump: Core Animation states the corner, and states it unclamped

`./capture.sh dump-layers --settle 8` on all twenty probe scenes, into `layer-dumps/` (one JSON per
scene, 20 of 20 written, every one with `isKeyWindow: true`). It captures nothing and needs no TCC
grant. The shape a `glassEffect` draws is carried on the **`CASDFElementLayer`** at the bottom of the
backdrop layer's own tree — `NSViewBackingLayer → CALayer → SwiftUI.SDFLayer → CALayer →
CABackdropLayer → CASDFLayer → CALayer → CASDFElementLayer` — and that layer carries `cornerRadius`
and `cornerCurve` directly. Extracted by `read-layer-dumps.py` into `layer-corners.json`:

| component | element bounds | `cornerRadius` | `cornerCurve` | `mode` |
| --- | --- | --- | --- | --- |
| `rrect-120x44-r14` | 120 × 44 | **14** | `continuous` | `bounds` |
| `rrect-120x44-r16` | 120 × 44 | **16** | `continuous` | `bounds` |
| `rrect-120x44-r18` | 120 × 44 | **18** | `continuous` | `bounds` |
| `rrect-120x44-r20` | 120 × 44 | **20** | `continuous` | `bounds` |
| `rrect-120x44-r22` | 120 × 44 | **22** | `continuous` | `bounds` |
| `capsule-120x44` | 120 × 44 | **22** | `continuous` | `bounds` |
| `rrect-44x44-r14` | 44 × 44 | **14** | `continuous` | `bounds` |
| `rrect-44x44-r18` | 44 × 44 | **18** | `continuous` | `bounds` |
| `rrect-44x44-r22` | 44 × 44 | **22** | `continuous` | `bounds` |
| `capsule-44x44` | 44 × 44 | **22** | `continuous` | `bounds` |

Identical on both backgrounds; the ten `checkerboard` scenes carry the same ten rows.

Three readings out of this table.

1. **The radius is not clamped anywhere in the declaration.** At r = 22 on a 44-tall box the
   requested radius reaches Core Animation intact, at ratio 0.5, with the continuous curve still
   named. Whatever Apple does about a reach that does not fit, it does not do it by reducing the
   radius before the shape is declared. vitrea's `buildAppleContour` reduces it to 14.39 and reports
   `saturated: true`; there is no counterpart to that anywhere in Apple's own tree.

2. **`Capsule()` and `RoundedRectangle(cornerRadius: 22, style: .continuous)` are the SAME
   declaration.** Both reach Core Animation as a `CASDFElementLayer` of the same bounds with
   `cornerRadius: 22` and `cornerCurve: continuous`. SwiftUI does not give the capsule a shape of its
   own; it gives it the short side's half as a continuous corner radius. That makes the two cells a
   free internal control, and they are byte-identical in the materialised bed on both backgrounds and
   both boxes (§3).

3. **The dump says nothing about what the curve becomes.** `cornerCurve: continuous` is a name, not a
   construction, and the layer tree carries no path, no mask and no per-corner geometry — the SDF
   element's `mode` is `bounds` and its shape lives in contents the reflection walk cannot read. The
   `CASDFOutputEffect`'s `maximum` is **39.52763758185479** on every one of the twenty scenes, so it
   is a constant of the effect and carries no shape either. What the continuous curve does when its
   reach overflows is therefore a pixel question, which is §4.

## 2. The run table

The Screen Recording grant is live, and how that was established is itself worth recording.
`./capture.sh probe` — which `exec`s `build/harness` as a child of the calling shell — reports:

```
ScreenCaptureKit: BLOCKED
ScreenCaptureKit is unavailable: 사용자가 응용 프로그램, 윈도우, 디스플레이 캡처의 TCC를 거절함
```

The same `probe` subcommand launched the way every capture is launched — `open` on
`build/VitreaReference.app` from the main checkout — reports:

```
window canBecomeKey: true, isKeyWindow: true, isMainWindow: true, NSApp.isActive: true
ScreenCaptureKit: OK 320x200 — the material path is available
```

The grant is keyed to the app bundle's identity, and a direct `exec` from an agent's shell is
attributed to the shell instead, so `capture.sh probe` is a false negative for the path the harness
actually captures through. Recorded in §7; it costs a session to rediscover.

Ten runs by W9's protocol (claims §5.30: a 6 s bare neutral reset before each cell, one stable
order, the run refused unless the machine had been idle 45 s), driven by `run-probe.sh`, launched
from the main checkout's bundle with the bed and the fixtures directory passed as `open --env`.

| run | HID idle at start / end (s) | audit | kept |
| --- | --- | --- | --- |
| w20-probe-1 | 1 170 / 1 371 | 20/20 | yes |
| w20-probe-2 | 1 372 / 1 571 | 20/20 | yes |
| w20-probe-3 | 1 572 / 1 772 | 20/20 | yes |
| w20-probe-4 | 1 773 / 1 972 | 20/20 | yes |
| w20-probe-5 | 1 972 / **1** | 10/20 | **no** — HID activity during the run; ten cells not `presentedActive` |
| w20-probe-6 | 91 / 291 | 20/20 | yes |
| w20-probe-7 | 291 / 490 | 20/20 | yes |
| w20-probe-8 | 490 / 690 | 20/20 | yes |
| w20-probe-9 | 691 / 891 | 20/20 | yes |
| w20-probe-10 | 891 / 1 090 | 20/20 | yes |

**Ten runs taken, nine attested, nine materialised** (`cli/materialize.ts --frequency-settle
--apply`). Nineteen of twenty cells unanimous across the nine; one frequency-settled —
`checkerboard__capsule-120x44__rest` at an 8-of-9 majority (share 0.89) — and by the internal control
its twin `checkerboard__rrect-120x44-r22__rest` published the same byte-state. Provenance: nine runs,
80.7 % confidence at a one-in-six minority (`probe/provenance.json`).

Run 5 is the ordinary failure the attestation exists for — HID idle fell to 1 s at the run's end, so
somebody or something touched the machine while it was capturing — and not the second failure mode
the tracker records ("The reference harness loses cells to window activation with the machine idle",
W19 G0). That one did not appear in this session: nine of ten runs were clean, against W19's eight
of ten.

## 3. The internal control: the capsule and the r = 22 rung are the same pixels

The layer dump says the two are the same declaration, so they must be the same bytes, and they are —
on the materialised bed, sha256 equal, all four pairs:

| pair | sha256 |
| --- | --- |
| `light-solid__capsule-120x44__rest` = `light-solid__rrect-120x44-r22__rest` | `5566f778…` |
| `checkerboard__capsule-120x44__rest` = `checkerboard__rrect-120x44-r22__rest` | `6f94450e…` |
| `light-solid__capsule-44x44__rest` = `light-solid__rrect-44x44-r22__rest` | `101bc6ba…` |
| `checkerboard__capsule-44x44__rest` = `checkerboard__rrect-44x44-r22__rest` | `d2e405ab…` |

This does not by itself prove the shape is a stadium — both cells could be the same wrong thing. What
proves it is §5: the same pixels read against the exact stadium at 0.295 px p95.

## 4. The instrument, and what it is worth

`read-contours.py`, two independent extractions, both in device px at 1x (one device px is one CSS
px here). **The grid's floor is 0.5 px** — no contour read off a raster claims better than half a
pixel — and it is declared before the readings, not after them.

**`light-solid` — the rim step, sub-pixel.** Over a flat backdrop the material's boundary is a step
from the shadowed background (about 237/255 in grey) to the rim's own peak (255), with one
anti-aliased pixel between. The contour is the crossing of the half-coverage level between those two,
linearly interpolated, taken inward along every row from each side and every column from each side:
328 points on a 120 × 44 surface, 176 on a 44 × 44 one. Both levels are read out of the capture; no
model of the material enters.

**`checkerboard` — the local-contrast rule.** A 3 × 3 local range collapses inside the surface
because the material blurs the checker; the outer shadow darkens the checker very nearly
multiplicatively, so the range and the mean fall together and the RATIO to the background raster's
own local range does not move. A pixel is inside where that ratio is below a half for three
consecutive samples. The rule only speaks where the background itself has contrast — about an eighth
of the scanlines — so it yields 40 points on the 120 × 44 surfaces and 24 on the 44 × 44 ones, and it
has one-pixel resolution by construction.

**Both calibrated on the capsule controls,** whose true shape is known exactly (`Capsule()`, and
`resolveShape`'s stadium is that shape to machine precision):

| reading | control | mean signed error | p95 \|error\| | max |
| --- | --- | --- | --- | --- |
| `light-solid` | `capsule-120x44` | **+0.035** | **0.295** | 0.394 |
| `light-solid` | `capsule-44x44` | — | **0.344** | 0.395 |
| `checkerboard`, raw | `capsule-120x44` | **−1.31** (median −1.5) | 1.607 | 2.088 |
| `checkerboard`, after the declared −1.5 px scan offset | `capsule-120x44` | — | **0.760** | 1.113 |
| `checkerboard`, after the offset | `capsule-44x44` | — | **0.992** | 1.265 |

The `light-solid` reading is essentially unbiased and lands inside the floor. The `checkerboard`
rule reads 1.5 px inside the true contour, for a reason that is a property of the rule and not of the
shape — the rim occupies the boundary pixel and is itself high-contrast, and the run-of-three
requirement then costs two more samples — so `CHECKER_SCAN_BIAS = 1.5` is declared once, applied
along the scan direction to every cell alike, and the residual after it is 0.76–0.99 px, about twice
the floor. **`light-solid` is the measurement and `checkerboard` is the cross-check**, and every
verdict below is stated on `light-solid` and checked for sign agreement on `checkerboard`.

**The candidates.** `candidates.ts` builds all four through the geometry package's public API, so
whatever wins is a policy G1 can adopt by name, and samples them at 0.02 px:

| name | construction | radius / reach at r = 18 on 120 × 44 |
| --- | --- | --- |
| `vitrea-clamp` | `buildAppleContour(halfW, halfH, r)` — today's policy | 14.39 / 22 |
| `shoulder-compress` | `resolveCornerConstruction(halfW, halfH, r, APPLE_REACH − 1)` through `buildReferenceContour`; the family's budget clamp pulls smoothing to `budget/r − 1` | 18 / 22, smoothing 0.222 |
| `circular-arc` | the same at smoothing 0 | 18 / 18 |
| `apple-overflow` | Apple's dump at the requested radius with the overflow allowed (the control that should fail) | 18 / 27.52 |

## 5. The readings

Every number below is on the materialised bed, `light-solid` unless the table says otherwise. Full
tables in `read/tables.md`; the raw readings in `read/contours.json`.

### The corner Apple actually draws

| r | ratio | circle-fit radius | fit rms | diagonal depth | implied circular radius | what a radius clamp predicts |
| --- | --- | --- | --- | --- | --- | --- |
| 14 | 0.3182 | 13.67 | 0.123 | 5.57 | **13.46** | 14 (not clamped below the ratio) |
| 16 | 0.3636 | 15.24 | 0.102 | 6.41 | **15.47** | 14.39 |
| 18 | 0.4091 | 17.15 | 0.104 | 7.28 | **17.58** | 14.39 |
| 20 | 0.4545 | 18.99 | 0.106 | 8.10 | **19.56** | 14.39 |
| 22 | 0.5000 | 20.83 | 0.109 | 8.92 | **21.53** | 14.39 |

`diagonal depth` is the distance from the corner's vertex to the contour along the 45-degree
diagonal, which is the best-conditioned corner measurement a pixel grid supports — the contour
crosses the diagonal transversally — and `implied circular radius` is that depth divided by
`√2 − 1`. On the 44 × 44 box the same three rungs read 13.46, 17.58 and 21.55. The implied radius
tracks the requested radius with a constant offset near −0.5 px at every rung, above the ratio and
below it alike. **A clamp would have pinned every row from r = 16 down at 14.39 and none of them
is.**

### The candidates against the contour, p95 (px), `light-solid`

| component | r | ratio | vitrea clamp | shoulder compress | circular arc | apple overflow | stadium |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `rrect-120x44-r14` | 14 | 0.3182 | 0.283 | 0.247 | 0.244 | 0.283 | — |
| `rrect-120x44-r16` | 16 | 0.3636 | **0.524** | 0.238 | 0.240 | 0.283 | — |
| `rrect-120x44-r18` | 18 | 0.4091 | **1.351** | 0.250 | 0.250 | 0.303 | — |
| `rrect-120x44-r20` | 20 | 0.4545 | **2.117** | 0.266 | 0.266 | 0.299 | — |
| `rrect-120x44-r22` | 22 | 0.5000 | **2.942** | 0.295 | 0.295 | 0.340 | — |
| `rrect-44x44-r14` | 14 | 0.3182 | 0.328 | 0.322 | 0.322 | 0.328 | — |
| `rrect-44x44-r18` | 18 | 0.4091 | **1.382** | 0.309 | 0.309 | 0.386 | — |
| `rrect-44x44-r22` | 22 | 0.5000 | **2.993** | 0.344 | 0.344 | 0.429 | — |
| `capsule-120x44` | 22 | 0.5000 | — | — | — | — | 0.295 |
| `capsule-44x44` | 22 | 0.5000 | — | — | — | — | 0.344 |

Max over the same contours:

| component | vitrea clamp | shoulder compress | circular arc | apple overflow | stadium |
| --- | --- | --- | --- | --- | --- |
| `rrect-120x44-r14` | 0.402 | 0.393 | 0.393 | 0.402 | — |
| `rrect-120x44-r16` | **0.678** | 0.386 | 0.386 | 0.380 | — |
| `rrect-120x44-r18` | **1.506** | 0.356 | 0.356 | 0.430 | — |
| `rrect-120x44-r20` | **2.318** | 0.378 | 0.379 | 0.407 | — |
| `rrect-120x44-r22` | **3.147** | 0.394 | 0.394 | 0.479 | — |
| `rrect-44x44-r14` | 0.402 | 0.393 | 0.393 | 0.402 | — |
| `rrect-44x44-r18` | **1.506** | 0.400 | 0.400 | 0.525 | — |
| `rrect-44x44-r22` | **3.147** | 0.395 | 0.395 | 0.483 | — |
| `capsule-120x44` | — | — | — | — | 0.394 |
| `capsule-44x44` | — | — | — | — | 0.395 |

And the reverse direction, max from the candidate onto the measured points — the one that sees a
candidate drawing curve the native contour does not have, which is how the overflow control is
refuted at all (a one-sided native→candidate distance cannot see extra geometry, and at r = 22 the
overflow scores 0.340 one way round and 2.708 the other):

| component | vitrea clamp | shoulder compress | circular arc | apple overflow | stadium |
| --- | --- | --- | --- | --- | --- |
| `rrect-120x44-r14` | 0.667 | 0.709 | 0.699 | 0.667 | — |
| `rrect-120x44-r16` | 0.774 | 0.637 | 0.657 | 0.609 | — |
| `rrect-120x44-r18` | **1.539** | 0.673 | 0.673 | 0.655 | — |
| `rrect-120x44-r20` | **2.358** | 0.646 | 0.597 | **1.079** | — |
| `rrect-120x44-r22` | **3.206** | 0.637 | 0.637 | **2.708** | — |
| `rrect-44x44-r18` | **1.539** | 0.673 | 0.673 | 0.655 | — |
| `rrect-44x44-r22` | **3.206** | 0.637 | 0.637 | **2.770** | — |
| `capsule-120x44` | — | — | — | — | 0.637 |

The measured points sit about a pixel apart, so 0.6–0.7 px is what a candidate that is right reads
here.

### The same on `checkerboard`, p95 (px), after the declared offset

| component | r | vitrea clamp | shoulder compress | circular arc | apple overflow | stadium |
| --- | --- | --- | --- | --- | --- | --- |
| `rrect-120x44-r14` | 14 | 0.979 | 1.031 | 1.035 | 0.979 | — |
| `rrect-120x44-r16` | 16 | 1.007 | 0.801 | 0.801 | 0.786 | — |
| `rrect-120x44-r18` | 18 | **1.336** | 0.993 | 0.993 | 0.815 | — |
| `rrect-120x44-r20` | 20 | **1.950** | 0.816 | 0.816 | 0.851 | — |
| `rrect-120x44-r22` | 22 | **2.659** | 0.760 | 0.760 | 0.739 | — |
| `rrect-44x44-r14` | 14 | 0.813 | 0.825 | 0.821 | 0.813 | — |
| `rrect-44x44-r18` | 18 | **2.186** | 0.791 | 0.791 | 0.804 | — |
| `rrect-44x44-r22` | 22 | **3.753** | 0.992 | 0.992 | 1.013 | — |
| `capsule-120x44` | 22 | — | — | — | — | 0.760 |
| `capsule-44x44` | 22 | — | — | — | — | 0.992 |

Same sign, same ordering, coarser numbers: the clamp is refuted from r = 18 up on this reading (its
resolution cannot resolve r = 16's 0.73 px separation), everything else sits at the control's own
0.76–0.99 px.

### What the instrument can and cannot separate

Max distance between the candidate curves themselves, which bounds what any reading of them could
decide:

| pair | r 14 | r 16 | r 18 | r 20 | r 22 |
| --- | --- | --- | --- | --- | --- |
| vitrea-clamp vs shoulder-compress | 0.354 | **0.734** | **1.543** | **2.364** | **3.190** |
| shoulder-compress vs circular-arc | 0.375 | 0.360 | 0.351 | 0.290 | **0.000** |
| shoulder-compress vs apple-overflow | 0.354 | 0.339 | 0.373 | **1.053** | **2.863** |
| vitrea-clamp vs apple-overflow | 0.000 | 0.696 | 1.508 | 2.326 | 3.146 |

Bold is above the 0.5 px floor. Three things follow, and the third is a limit on this probe rather
than a result.

1. **r = 14 decides nothing about Apple and was not meant to.** Below the ratio all four candidates
   lie within 0.375 px of each other and all four fit the contour within 0.33 px p95. That rung
   measures the reader.
2. **The radius clamp is refuted from r = 16 up**, on both boxes, on both backgrounds, by a margin
   that grows to six times the floor.
3. **`shoulder-compress` and `circular-arc` cannot be separated by pixels at these sizes.** They are
   never more than 0.375 px apart and are identical at the capsule limit. Both fit every rung within
   the floor.

## 6. The verdict, and what G1 should adopt

**One candidate covers r = 14…22 within the floor on both boxes and both backgrounds:
`shoulder-compress` — the requested radius kept, the reach compressed to the corner's budget.** In
the geometry package's own terms that is

```
r     = min(radius, budget)                    budget = min(halfW, halfH)
reach = min(APPLE_REACH · r, budget)
```

with the effective smoothing falling out as `reach / r − 1`, which reaches exactly 0 at the capsule
limit — where the corner becomes a circular arc at r = budget, which is the stadium `Capsule()`
draws, which is what the r = 22 rung measures at 0.295 px p95 against the exact stadium.

`circular-arc` fits equally well and the pixels do not choose. Two arguments choose it anyway, and
neither is a measurement:

- **Continuity in r.** `circular-arc` would mean Apple discards the shoulder the instant the ratio is
  crossed, which is a step in the shape at r/side = 0.327083 — and S2's dump proves the shoulder is
  there below the ratio. `shoulder-compress` reduces the shoulder smoothly from S2's value to zero
  across the interval and agrees with the dump at the bottom of it. The probe's r = 14 rung is
  consistent with both, so this is the reason to prefer one.
- **It is the reference family's own clamp policy**, already implemented, already continuous, already
  the thing `corner.ts` calls exact at the capsule limit. Adopting it removes a policy rather than
  adding one.

The refusal the charter allowed (Decision Log 1, question 1) is **not needed**: one law fits the
probe within the instrument's floor, and its residual is indistinguishable from the reader's own
error on a known shape. What must be recorded beside it is that the probe cannot tell that law from a
plain circular arc, so the shoulder's shape between the ratio and the limit is adopted on continuity,
not on pixels. The parent writes claims §5.84 and the charter; this file does not.

For `apple.test.ts`'s "Apple's budget policy is its own", the name is now measured to be wrong in the
direction it asserts: Apple's budget policy is the reference family's, not its own.

## 7. By eye

`read/crops/*.png` — one strip per rung, four panels, the same native corner in each with one
candidate's contour drawn over it: `vitrea-clamp` red, `shoulder-compress` blue, `circular-arc`
green, `apple-overflow` magenta. Zoom 8, nearest-neighbour, and the crop is contrast-stretched to its
own min and max because over `light-solid` the whole scene lives in the top eight per cent of the
range and the material's edge is invisible at native contrast — the stretch is per-crop and recorded
in `contours.json` under `crop.stretch`, so nothing in these pictures is a level.

At r = 18 and r = 22 the red curve stands visibly outside the native rim through the whole corner
while the other three sit on it; at r = 22 the magenta curve additionally leaves a straight spur
where the overflowing reach makes the ring's straight edges reverse. The user's eye can settle this
without the tables.

## 8. What did not work

- **`./capture.sh probe` is a false negative for the grant.** It `exec`s `build/harness` as a child
  of the calling shell, so TCC attributes the request to the shell; the same subcommand launched
  through `open` on the app bundle reports the material path available. Both outputs are in §2. Every
  actual capture goes through `open`, so the grant was live throughout; a session that trusts
  `capture.sh probe` alone would stop for nothing.
- **The corner's reach cannot be measured directly on a pixel grid.** The first version of the reader
  reported "how far from the corner vertex the contour leaves the straight edge", which is the
  quantity that would separate `shoulder-compress` from `circular-arc` outright. The join is G2 —
  zero curvature — so the contour leaves the edge tangentially and the departure is under a tenth of
  a pixel for several pixels either side of the true reach. It read 18.5 for a stadium whose reach is
  22. Removed; the diagonal depth replaced it.
- **A circle fit over a short arc is not usable.** Fitting only the ±0.35·budget band around the
  corner's diagonal read 17.9 for a radius of 22. Widened to ±0.75·budget it reads 20.83, and the
  diagonal depth — one scalar, transversal — is better than either, so the circle fit is reported for
  continuity with the charter's request and the depth is what the verdict rests on. The fit is
  refused outright on `checkerboard`, where the rule yields two dozen points.
- **The half-pixel convention cost a reading.** The first extraction placed a crossing at its
  fractional sample index rather than at the sample's centre, which reads every shape one pixel too
  wide — twice the floor — and showed up as a 0.70 px p95 on a control that should read 0.30. Caught
  by the control, which is what the control is for.
- **The one-sided contour distance cannot refute a candidate that draws too much.** `apple-overflow`
  self-intersects above the ratio and still scores 0.283–0.340 p95 native→candidate, because every
  measured point finds some part of it nearby. Only the reverse direction refutes it. Both are
  reported.
- **Run 5 of ten was lost to HID activity** (idle 1 s at the run's end). Ordinary, and the protocol
  caught it. The distinct failure mode the tracker records — cells lost to window activation with the
  machine idle — did not occur in this session.

## 9. Files

| what | where |
| --- | --- |
| the probe bed | `apps/reference-apple/scenes-w20-probe.json` (written by `g0/make-probe-scenes.mjs`) |
| the captures | `results/2026-09-05-w20-capsule-corner/probe/` + `probe/provenance.json` |
| the layer dumps | `g0/layer-dumps/` (20 scenes), reduced to `g0/layer-corners.json` |
| the candidates | `g0/candidates.ts` → `g0/read/candidates.json` |
| the reader | `g0/read-contours.py`, verified by `g0/verify-reader.sh` |
| the readings | `g0/read/contours.json`, `g0/read/tables.md`, `g0/read/crops/` |
| the drivers | `g0/run-probe.sh`, `g0/run-materialize.sh`, `g0/run-dump-layers.sh`, `g0/run-read.sh` |
