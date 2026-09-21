# W31 G4 — by eye, at the landing

Twenty sheets, `sheets.ts`, written from the **canonical** `web-captures/` tree on the capture
machine: the pixels the committed rows beside them were measured off, at the shipped document bytes
(`49490eb9ff7a` / `14c6bacf2eda` light, `b5714a866288` / `cc4ed1038996` dark), which the script
asserts per cell before it opens a file rather than after.

Written **before** the records, the demo, the version and §5.165, on the charter's own rule that the
metrics are not the whole verdict, and read against W31 G3's `eye.md` and W31 G0's cell for cell
where the cells are the same.

Four panels on the standard and overshoot bands — **native | WebGPU | CSS | OKLab ΔE × 8** — and
three on the accessibility band, where the question is not a tier comparison.

---

## 1. The accessibility band, which is the gate this sheet exists for

Four sheets: `photo__rrect-md` in both poses on `…-1x-light-reduced-transparency-glass0.5` and
`…-1x-light-increased-contrast-coupled-glass0.5`. The brief's instruction was to stop before the
version bump if the eye found a visible regression against 0.20.0 despite the numbers.

**No regression. The eye agrees with the bytes, and the gate does not stop.**

On all four sheets vitrea's body is a flat near-white plate with essentially no chroma in it, which
is what a plate at `α + lift·(1 − α)` should be and is what 0.20.0 drew. The defect W31 G3's review
found would be unmistakable here — a body carrying three times the reference's chroma-to-structure
is a body with visible colour in it, over a backdrop this saturated — and there is none on any of
the four. The difference panels are flat mid-greys with a faint rim and no coloured structure
anywhere in the interior.

Two readings beside the verdict, neither of them this wave's doing:

- **The residual on these beds is a LEVEL residual and it is inherited.** On increased contrast's
  inactive pose vitrea's plate is a clean white where the reference keeps a faint warm-to-green
  cast, and that sheet's ΔE panel is the brightest and most uniform of the four. That is the
  `R` 0.1552 §5.164 §13 records at 0.20.0 — a seventh of the reference — and it was there before
  this wave and is there unchanged after it. It is what Decision Log 3 (c) defers.
- **Reduced transparency's active pose is the closest of the four**, and its difference panel is
  the one with visible interior structure rather than a flat wash, so the residual there is the
  structure deficit rather than the level.

The objective half, taken beside the eye and not instead of it: the two accessibility profiles'
**68 rows carry 6,855 numeric readings across every axis and not one of them differs from the
0.20.0 generation** in `results/superseded/d0c389d70456.json`. The only fields that differ at all
are the 24 optional chroma fields this wave's instrument added, which are additions and not
movements. That is `standard-row-identity.txt`'s claim re-derived from the committed matrix by a
different route.

## 2. The dark scheme: the body carries the hue, and the third panel is the one that does not

`photo__rrect-lg__rest` at 1x and 2x dark — the wave's own cell, the two rows that CLEARED.

G0's first finding was *the reference's dark body over the photograph is a photograph seen through
glass, with its hues in place; vitrea's is a flat warm grey, and the difference panel is saturated
white across the whole interior*. On the WebGPU panel that is **gone**. The magenta-to-green
diagonal the reference carries runs through vitrea's body in the same places and the same
direction, softer than the reference's but a coloured body rather than a grey one, at both scales.

**And the CSS panel is exactly what G0 described.** Third panel, both scales: a flat grey-lilac
plate with no hues in it at all, beside a second panel that has them. That is the decline of
§5.164 §5 as a picture, and it is the plainest statement of what 0.21.0 does and does not ship —
the two `dom` rows in `MISSED_27_ROWS` are this panel.

The ΔE panel on those two cells is still bright over much of the interior. The residual that
remains there is the structure this wave declined to touch (X3): vitrea's body is smoother than the
reference's, which is the analysis pass's work and not this operator's.

## 3. `photo__capsule-button__rest`, dark — where the eye finds a level and the statistic finds a ratio

The bed's lowest cell (`R` 0.8213 at 1x). Vitrea's capsule is not only greyer than the reference's,
it is visibly **darker**, and the two are not separable by eye. That is the cell §5.161 §7 (c)'s
closure names as the level stop's worst — `|Δlevel|` 0.0457 at 1x and 0.0493 at 2x, the largest in
the bed — and §5.164 §12 names as the dark bed's worst reproducibility pair, biased through the
exact `(level)^(−2/3)`.

Worth stating plainly because the metrics frame it as two numbers and the eye sees one thing: on
this cell the chroma miss and the level miss are the same defect to a viewer, and the level is the
half M1 does not bound. M2 does not reach it either — M2 bounds the structure. **The level stop
that would is a declared number in §5.161 §7 (c) and is not an adopted row.** That is a gap and it
is recorded as one.

## 4. The light scheme, and a correction to §5.164 §9 read beside it

§5.164 §9 found that on the light sheets the ΔE panel has **inverted** — the interior mostly dark,
the brightest band the rim, a bright outline all the way round where before the fit the interior
was the bright part — and concluded that "on the light scheme the body's chroma is no longer the
largest thing on the cell".

That reproduces, and the span qualifies it.

| light cell | span | what the ΔE panel is |
| --- | ---: | --- |
| `photo__capsule-button__rest` 1x | 44 | rim-dominated; interior near black |
| `photo__rrect-md__rest` 1x and 2x | 96 | rim-dominated, with faint interior structure |
| `photo__rrect-lg__rest` 2x | 160 | **interior-dominated**; broad bright regions, the rim not the brightest thing |

So the inversion is a reading of the light scheme **up to about span 96**, not of the light scheme
flat. At the largest span the interior is still the largest thing on the cell, and that is the span
the two claimed light-adjacent cells and the overshoot live on. A wave that takes §5.164 §9's
sentence as licence to read only the rim would read the wrong half of its own bed.

On the two light cells at spans 44 and 96 the first two panels are genuinely hard to tell apart at
a glance, which is G0's second finding (*the reference reads as a transparent slab and vitrea's as
a painted panel on top of the image*) resolved on the fidelity target. At span 160 they are close
but not interchangeable: the reference's greens are stronger and its magenta band is tighter.

## 5. The overshoot band, and the one thing these sheets found that the numbers did not

Four sheets of `photo__rrect-sm` — span 32, the thinnest surface the bed carries. Three of them are
the cells M1's per-cell ceiling declares MISSED at adoption (`R` 1.5155, 1.4469, 1.4417) and the
fourth is the sibling that passes at 1.3567.

**The four are indistinguishable by eye, and so is each of them from its own reference.** On every
one the native plate is a small pink-lilac rectangle and vitrea's is a small pink-lilac rectangle
with a marginally stronger, slightly bluer cast; the ΔE × 8 panel is nearly black on all four,
where on `rrect-lg` at the same gain it is nearly white.

That is worth saying exactly, because it cuts both ways and the record should carry both halves.

- **The overshoot is real and it is not visible.** `R` 1.52 is a 52 % excess on a ratio whose
  absolute magnitude at span 32 is small — the plate at that span transmits little, so a large
  relative gain on little is still little. The ceiling at 1.40 separates cells the eye cannot
  separate, and it is a statistic rather than a picture.
- **That is an argument for the clause and not against it.** A defect invisible at span 32 is the
  same defect that is visible at span 160 on the holdout cell, where it reads 1.24 and 1.36 — the
  span axis is what carries it from one to the other, and it is exactly the axis one constant per
  document does not condition on (§5.164 §8 (a)). A clause that fired only where the eye already
  complains would be a clause that adds nothing; this one names the cells the next form has to fix
  while they are still cheap to fix.

The honest summary of the ceiling: **it is worth having and it is not a claim about what a user
sees at span 32.** Recorded that way in §5.165 rather than as "three cells look wrong".

## 6. What is NOT on these sheets, and what that costs

`mid-chroma-solid` is a **probe** scene. The canonical read is calibration + validation + the pitch
ladder (§5.164 §7), so the canonical tree carries no macOS 27 `mid-chroma-solid` capture at all, and
X1 allows this gate no calibration capture of its own. So:

- **G0's hue ROTATION finding stands open exactly where §5.164 §9 left it** — the reference's body
  a clean lighter pink and vitrea's a lavender, desaturated *and* rotated toward blue, with
  `tintHueShift*` never read on those cells. G0's pre-fit sheets are committed at
  `results/2026-09-21-w31-g0-chroma-cut/sheet__*__mid-chroma-solid__*.png` and are the last look
  anyone has taken at it.
- On the `photo` cells the restored hues sit where the reference's do, at every span and both
  schemes, which is consistent with a rotation that was the plate's rather than a hue-mapping
  error. **This gate does not claim that**, for the same reason G3 did not: the cell that would
  decide it was not re-read.
- Closing it needs a read that carries the probe set, or a scratch capture under a gate chartered
  for one. Deferred, with the tracker entry.

## 7. The verdict of the eye, in one line each

| band | reading |
| --- | --- |
| accessibility, four sheets | no regression against 0.20.0; the body is the occluded plate it was, and the inherited level residual on increased contrast is unchanged. **No stop.** |
| dark standard, six sheets | the WebGPU body carries the backdrop's hue at both scales; the CSS body does not, and is the panel G0 described |
| light standard, six sheets | the first two panels are hard to tell apart up to span 96; at span 160 they are close but the reference's greens are stronger |
| overshoot, four sheets | the three missed cells and the one that passes are indistinguishable from each other and from their references; the ceiling is a statistic |
| `mid-chroma-solid` | not captured; G0's hue-rotation finding stands open |
