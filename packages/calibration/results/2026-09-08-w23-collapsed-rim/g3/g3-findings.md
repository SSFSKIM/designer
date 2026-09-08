# W23 G3 — the rim beneath the paint

The declaration is above the horizontal rule and was written before this gate captured a canonical
pixel; everything below it is what the run then read.

---

## 1. The finding, and what the rows chose

Decision Log 3 (h) put it by eye: **Apple's rim on a painted surface is the paint lifted, and
vitrea's is white added over it.** Read on the contour row's straight-span mean colour at 2x in
light (`chroma-before.txt`; the reader is this gate's `read-contour.py`, extended with the hue
columns):

| cell (light 2x) | base native | row0 native | landed 0.11.0 | G1 |
| --- | --- | --- | --- | --- |
| `dark-solid__capsule-button__rest-tint-orange` | (255, 148, 0) | **(255, 189, 0)** | (255, 149, 0) | (255, 192, 130) |
| `light-solid__…-tint-orange` | (254, 148, 0) | **(255, 195, 3)** | (255, 173, 99) | (255, 180, 112) |
| `photo__…-tint-orange` | (231, 133, 0) | **(245, 188, 14)** | (247, 163, 99) | (255, 197, 153) |
| `checkerboard__…-tint-blue` | (8, 120, 236) | **(58, 199, 248)** | (100, 153, 250) | (145, 183, 255) |

The bases agree to a code — the paint is right — and the ROWS do not: the reference lifts an
orange's green channel and leaves its blue at 0, and vitrea lifts all three, which turns an orange
edge peach and a blue edge lilac. No luminance clause sees it. In OKLab the reference's orange row
moves from the base's (a +0.082, b +0.155) to (+0.021, +0.171) and vitrea's to (+0.045, +0.097).

**Two candidate compositions, and the rows chose between them.** The first — the rim's light beneath
the author layer at the author's opacity — is refuted before a capture: the reference's tinted base
over `dark-solid` is the seed exactly, so the paint is opaque there, and a rim strictly beneath an
opaque paint is no rim at all where the reference draws +0.118. The second is a luminance lift the
paint's colour scales, and it has two forms that differ in what they normalise by:

| normalised by | mean \|da\| | mean \|db\| | the collapsed painted rim |
| --- | --- | --- | --- |
| nothing (white; G1) | 0.0399 | 0.0554 | 0.115 against +0.118 |
| the paint's brightest channel | 0.0441 | 0.0221 | **0.030** against +0.118 |
| the paint's **LUMINANCE** | **0.0222** | **0.0093** | 0.072 against +0.118 |

Normalising by the brightest channel reproduces the hue and loses the AMOUNT — it divides the rim's
luminance by the paint's. Normalising by luminance is what the rows chose, and it is what the
reference's own channels say: on the collapsed orange capsule at 2x the reference lifts green by
0.213 of linear light where a white rim of the same amount lifts it by 0.304, and 0.213 / 0.304 =
0.70 is exactly that orange's green coefficient divided by its luminance.

So the rim's light is spent in `mix(white, paint / luminance(paint), rimTintChroma × tintStrength)`,
with a floor of 0.05 on the divisor — below that a paint has no readable hue and the normalisation
would be a colour cast of arbitrary size rather than a rim.

## 2. What lands

| constant | before → after | fitted on |
| --- | --- | --- |
| `rimTintChroma` | — → **1** | 52 tinted sides of both beds at both scales, per-side answers 0.921…1.732 (mean 1.154), the objective monotone to the bound |
| `rimCollapsedTinted` | 0.337 → **0.520** | 12 collapsed painted sides, per-side answers 0.510 (1x) and 0.544 (2x), minimiser worst residual 0.0055 |

`rimCollapsedTinted` moved because the LIGHT is spent differently and not because the reading did:
an orange paint's red channel is already at 255, so the share of the rim that goes there is lost to
the raster, and at 0.337 the collapsed painted rim fell to +0.072 against a reference of +0.118.

Fingerprints `ee0010558553ee12` → **`c426a37744c38cce`** (light) and `afd0e999e2f5813e` →
**`bf5752ac1b152238`** (dark). Both documents move because both constants are the material's; the
dark PATCH itself does not move and its resolved material does.

Nothing else moves. `rimTintChroma` is 0 under a strong border on both tiers: an accessibility
border that took the paint's hue would be the paint again, which is what it exists not to be.

## 3. The stops, declared

G1's S1–S8, and two of this gate's own:

- **S9** — a tinted cell whose luminance rim leaves Decision Log 2 (c)'s binding (no tinted row worse
  than landed by more than 0.03; the tinted collapsed cells within 0.05).
- **S10** — any untinted capture moved.

**S10 is already proven on the ladder, before the bed was captured.** The rim's colour is gated by
the pixel's own tint strength, so an unpainted surface keeps a white rim at every value of the
constant, and `untinted-identity.py` over the four ladder pairs reads **0 untinted captures moved
and 0 tinted captures unmoved** at all four points. The golden suite says the same thing from the
other side: ten of the eleven scenes moved 0 pixels and the eleventh is the only one that carries a
paint.

## 4. The goldens

`goldens-attribution.txt`. Every scene rendered twice through the isolation proof's own profile
seam, once with the two constants at G1's values and once as shipped: **not one pixel outside a
contour band moved on any scene, and ten of the eleven scenes moved no pixel at all.** The eleventh
is `collapsed-tone` — the only scene in the suite with an author tint, added by G1 for exactly this
kind of attribution — which moved 1 448 pixels by at most 130 code values, all inside its contour
band. One hash re-recorded, under `W23_G3_HASHES`; the suite is 31 / 31.

## 5. How the bed is run

`g3-dryrun-run.sh`, all six profiles on both tiers, calibration and validation first and the holdout
last. **G1's holdout read is spent on a configuration that will not land** (W23 Decision Log 3 (f))
and is not a target here; this is the read of the holdout on the configuration G2 will build.

---

## 6. What the run read

`g3-evidence.sh`; 229 cells; the outputs are `g3-clauses.txt`, `stops.txt`, `tinted-rows.txt`,
`untinted-identity.txt`, `chroma-after.txt`, `chroma-after-css.txt`, `delta-e.txt`,
`byte-identity.txt`, `g3-digests.txt` and `g3-gate.txt` beside this file. One run of the
twenty-four exited 1 for the same reason G1's did — `hc-text__capsule-button__rest` cannot be
measured on `contourCurvature` at increased contrast, and the canonical bed carries the same hole.

### The hue clause — the wave's new one, and the mechanism's own verdict

The contour row's OKLab (a, b) against the reference's, over 52 tinted sides of both beds at both
scales, GPU tier:

| column | mean \|da\| | mean \|db\| | worst \|da\| | worst \|db\| | sides over 0.02 |
| --- | --- | --- | --- | --- | --- |
| landed 0.11.0 | 0.0520 | 0.0371 | 0.0708 | 0.0600 | 50 of 52 |
| G1 | 0.0399 | 0.0554 | 0.0797 | 0.0919 | 52 of 52 |
| **G3** | **0.0203** | **0.0088** | 0.0507 | 0.0370 | **36 of 52** |

Better than both columns on both axes; `db` — the yellow-blue axis the white rim was wrecking — is
down sixfold on G1 and fourfold on the landed bed. **The clause's 0.02 is not met on 36 sides**, and
every one of the 36 is `a` on the DARK bed's tinted rows, where vitrea draws 0.031 of contour rim
against a reference of +0.127: a rim that dim cannot move its row's hue whatever colour it is spent
in. That is the dark amplitude law's amount, recorded in the tracker, and not this composition's.

By channel, on the row the finding was stated on (`dark-solid__capsule-button__rest-tint-orange`,
light 2x): native (255, 148, 0) → **(255, 189, 0)**; vitrea (255, 192, 130) at G1 → **(255, 195, 0)**
now, with the blue channel back at 0 where the reference's is and the green within six codes.

The CSS tier moves less and in one direction only: |db| 0.0257 → 0.0205 and |da| 0.0417 → 0.0461,
with the worst values unmoved. Its border is one inset shadow of one colour where the renderer adds
a coloured light per pixel, and the residual is recorded rather than chartered.

### S9 — the tinted rows' AMOUNT, which the hue must not cost

`tinted-rows.txt`: **no tinted row is worse than the landed bed by more than 0.03** (worst excess
0.0000 — every tinted side is better than landed), and **every collapsed painted side is inside
0.05** at a worst of **0.0052**. `rimCollapsedTinted` 0.520 is what buys the second: at 0.337 under
the new composition those sides read 0.0455 out.

### S10 — no untinted capture moves

Two readings, and the isolated one is the proof. **On the ladder** — the same build, the same
document, `rimTintChroma` the only difference — `untinted-identity.py` reads **0 untinted captures
moved and 0 tinted captures unmoved** on all four beds. That is the mechanism's own claim, measured
with nothing else in the difference.

Against G1's dry run the count is 16, and every one is attributable to something that is not this
constant: **14 are the increased-contrast profile's GPU captures**, moved by the review fix wave's
strong-border fold (`rimLevelGain` 0 under the policy), and the other two moved by ONE code value —
`checkerboard__glass-over-glass__rest` on the dark CSS tier by one pixel and
`photo__toolbar-group__rest` at increased contrast by seventeen — which is the one-code capture
flake already in the tracker. The four tinted captures that did NOT move are the increased-contrast
profile's, where the strong border keeps `rimTintChroma` at 0 by design.

### The clauses, re-read

Unchanged from G1 by construction, since no untinted capture moved: clause 1's rim half MET on every
collapsed side of both beds at both scales (worst **0.0040** against 0.005) with the body's
`impulse` miss pre-existing and unmoved (S7 worst 0.00004); clause 2 **MET** (worst **0.0200**
against 0.03); clause 3 missed as a per-side bound (worst 0.1917) and met on its second half
(validation 0.0155 against calibration 0.0479); clause 4 missed on the band instrument. Decision Log
3 (c) and (d) already stand on those numbers.

Clause 5, and the tinted rows now carry it: every GPU calibration mean improves, and by more than
G1's did — light **0.00330 → 0.00324** (1x) and **0.00333 → 0.00329** (2x), dark **0.00404 →
0.00395** and **0.00403 → 0.00397**. S1 fires on no row (worst ΔE rise +0.00078, worst `ssimMean`
fall −0.00475). **S3 no longer fires**: the CSS 2x light calibration mean that rose +0.00011 at G1
is inside the stop here.

### Clause 6 — the holdout, read once on the configuration that lands

| profile | tier | holdout before → after |
| --- | --- | --- |
| 1x light standard | webgpu | 0.00914 → **0.00901** |
| 2x light standard | webgpu | 0.00906 → **0.00898** |
| 1x dark standard | webgpu | 0.01326 → **0.01331** |
| 2x dark standard | webgpu | 0.01301 → **0.01317** |
| 1x light increased contrast | webgpu | 0.02042 → 0.02042 |
| 1x light reduced transparency | webgpu | 0.00341 → 0.00345 |

The two light holdouts improve on G1's own numbers (0.00909 and 0.00904) and the two dark ones read
the same +0.00005 / +0.00016 G1 recorded. 229 digests in `g3-digests.txt` for G2.

### Clause 7 and 8

The goldens: one hash moved, ten scenes moved no pixel, nothing outside any contour band (§4).
The CSS tier: 106 of 115 renders move against the canonical bed and the 9 that do not are the
increased-contrast profile, where `border: "strong"` substitutes its own width and alpha; the movers
are the amplitude law, the re-based conversion, the collapsed rims, `interiorBandLight`'s derived
level and now the painted rim's colour.

### The gate, and what G2 re-derives

24 of 33 pass; the nine failures are the same bookkeeping G1 read and they have not moved:
`PREDICATE_EXCLUDES` re-derives **29 → 27**, four dom cells becoming well-conditioned
(`dark-solid__rrect-md` in dark at both scales and two holdout cells) and two texture cells newly
refused (`dark-solid__capsule-button` at 2x in both schemes) — one mechanism in both directions, a
rim on a surface that drew nothing changing the web silhouette.

## 7. The stops, dispositioned

| stop | verdict | number |
| --- | --- | --- |
| S1 | does not fire | worst +0.00078 / −0.00475, 0 rows |
| S2 | **FIRES, on two CSS rows** | +0.00347 / +0.00351 against 0.002 |
| S3 | **no longer fires** | every calibration mean inside 0.0001; the GPU tier improves |
| S4 | does not fire | 0 pixels outside any band; ten scenes moved 0 pixels |
| S5 | does not fire | both constants separate on every row; see §1 |
| S6 | does not fire | 9 identical are the strong border; the movers are named |
| S7 | does not fire | worst 0.00004 |
| S8 | **the user's** | `sheets/g3-1x.png`, `g3-2x.png` |
| S9 | does not fire | 0 rows worse than landed; worst collapsed painted side 0.0052 |
| S10 | does not fire on the mechanism | 0 untinted movers in isolation; the 16 against G1 are the fix wave and a one-code flake |

**S2 is G1's own, unchanged and for the same reason**: `photo__capsule-button__rest-tint-orange-half`
on the CSS tier at both scales, body +0.0035 against 0.002 — the one tinted cell whose material
shows through the paint, carrying `interiorBandLight`'s brighter band into the derived interior
level. Decision Log 3 (e) took it at the number; nothing in this gate moved it (+0.00350 → +0.00347
at 1x).

## 8. What the parent must decide

1. **The hue clause's 0.02 is met on `db` and not on `da`** — 36 of 52 sides, every one of them the
   dark bed's tinted rows, where the rim is 0.031 against +0.127 and no colour can move a row that
   dim. The composition is right and the dark bed's AMOUNT is the residual; it is in the tracker and
   it needs a bed with more than one fittable dark solid cell.
2. **The CSS tier's tinted rows move little and its |da| moves the wrong way** (0.0417 → 0.0461).
   One inset shadow of one colour cannot be a coloured light added per pixel; recorded as a CSS-only
   residual under wave Decision Log 23 (a).
3. **S2 still fires** at +0.0035 on one CSS cell, unchanged from G1 and already taken at the number.
4. **Clauses 3 and 4 stand as Decision Log 3 left them** — this gate moved no untinted capture, so
   their numbers are G1's exactly.
5. **The eye, S8** — the sheets, with the tinted capsules at 4× beside the black-on-black cells.
