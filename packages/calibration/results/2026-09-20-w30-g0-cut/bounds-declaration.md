# W30 — the bounds and the acceptances, declared before either operator exists

**Gate: W30 G0 (e), acceptance clause 3; contracts X2 and X4 ("bounds before reads"); charter
Decision Log 1. Claims §5.156 §5.**

This file is committed **before G2 opens**, which is before the first leaf of either operator is
written and therefore before any value of either is fitted. Nothing about vitrea's material has been
changed or measured at the moment it is written: the cuts it rests on (§5.156 §2, §3) are cuts of
evidence W29 committed. **These declarations are what G4 judges the wave against.**

---

## (a) The 27 adopted tables: unchanged, and no floor

The six macOS 27 profiles' adopted tables stay at the values W29 Decision Log 4 (a) and Decision
Log 5 ruled. **They are not transcribed here and must not be transcribed anywhere**:
`packages/calibration/test/adopted-thresholds.test.ts` is the only copy the rule allows, and the
tables there are **aliases** of the macOS 26.5 constants rather than literals, so "at exactly the
26.5 tables' values" cannot drift by a digit. Three cases in that file hold it and this wave does not
touch them:

- *"declares exactly the six profiles the user ruled, and not the confounded one"* — the roster,
  `DECLARED_27_PROFILES`, and the exclusion of the unbounded key.
- *"holds every 27 table at its 26.5 twin's values, row for row"* — `RULED_EQUAL_TO_26_5`, twelve
  entries, two per profile. Breaking one out into its own literal is what re-pinning a 27 bound
  would mean, and this case fails the day it happens silently.
- *"adopts no regression floor on any 27 profile"* — `REGRESSION_FLOORS` carries no
  `apple-macos-27.0-` key.

**No floor is adopted in this wave, on any profile, on either tier.** The reason is W29's and is
unchanged: the macOS 27 bed is published at the seven-run probe bar and a floor needs the
seventeen-run freeze bar, so a floor here would pin a precision the bed does not carry. A miss at
G4's read is **recorded, not widened and not floored** (X4); re-pinning a floor is a user decision
and this wave asks for none.

---

## (b) The wave's own acceptance, per operator

These are the wave's, not the bed's: they are read on the fit's scratch matrices and on G4's
canonical read, and each one says here whether it becomes an adopted row in
`adopted-thresholds.test.ts` at G4 or stays a one-wave reading.

### B1 — the shadow, thick regime (spans 96–160): **adopted at G4 if it passes**

**The tolerance.** The fitted σ_css at each of spans 96, 128 and 160, against that bed's own median
native σ at the same span, **within ±5 %**, on all four standard beds (1x/2x × light/dark) and on the
three accessibility beds at the spans they carry.

**The statistic it is read by.** The bed's median is the **upper middle order statistic**,
`sorted[n // 2]`, over that bed's ACTIVE cells at that span that resolve a σ and survive the
`σ_css > span` exclusion (§5.156 §2), computed by
`results/2026-09-20-w30-g0-cut/shadow-cut.py` and tabled in `shadow-cut.txt` §3. The fitted σ is the
law's own output at that span, not a re-read of a capture, because the law is a closed form.

**Why ±5 %.** The thick regime's own scale disagreement is 1.3–6.8 % between the two beds (§5.154
§4 as corrected) and the line's max residual on the medians is 0.023–0.090 CSS px, which is 0.3–0.7 %
at span 96 and 0.1–0.5 % at 160 (§5.156 §2). ±5 % is therefore wider than the fit's own residual and
narrower than the instrument's cross-scale spread: it can fail, and it cannot fail for a reason the
bed already contains.

**Fitted on non-holdout cells; the holdout reported.** Span 160 carries **ten fittable cells per
standard bed** from the probe ladder and three holdout cells on 1x light. Span 130 carries **no
fittable cell on any bed** — every `glass-over-glass` σ is holdout — so the law's value there is an
extrapolation of the line, and the six holdout readings (13.25–13.74) are the only check on it.
The three accessibility beds carry **no fittable cell above span 96**; their span-160 σ is the
holdout `photo__rrect-lg__rest` at 16.97 and is a reported check, never a fit input.

#### B1 read as a joint clause, 2026-09-20 (review closure), per charter Decision Log 3 (c)

*B1 above reads as seven independent clauses; it is two, because a document is selected per SCHEME
and not per bed.* Nothing above is rewritten. `shadow-cut.py` §9 and §10 compute everything below.

**The law's held parameter.** The σ law has one flat direction: shifting `sigmaPx`,
`sigmaThinOffsetPx` and `sigmaSpanRefPx` together leaves σ unchanged at every span, so a fit that
frees all four leaves is unidentified and two fits with different constants can draw the same
shadow. **G3 holds `sigmaSpanRefPx` at 96** in the macOS 27 documents and refits `sigmaPx` as the σ
at span 96, fitting the slope and the offset around it. 96 is the span every bed carries sixteen
cells at and the span the amplitude's own anchor (`thickOcclusionAt96`) is keyed to, so the two
laws pivot on the same abscissa. **The inert default of `sigmaSpanRefPx` stays 0** — the identity
`σ = sigmaPx + max(0, 0)` does not depend on its value, and 96 is the fit's number, not the
default's.

**The clause is joint across the beds one document serves.** The light document is what the 1x,
2x, reduced-transparency and coupled-contrast beds all draw; the dark document is what the two dark
beds draw. One σ at span 96 therefore has to meet every one of its own document's beds at ±5 % at
once, and the admissible window is the intersection:

| document | beds served (median native σ at span 96) | joint window at span 96 | effective |
| --- | --- | --- | ---: |
| light | 1x light **8.7954**, 2x light **9.3648**, reduced transparency **8.5898**, coupled contrast **8.5898** | **[8.8966, 9.0193]** | **±0.685 %** |
| dark | 1x dark **8.8743**, 2x dark **9.3773** | **[8.9084, 9.3180]** | ±2.247 % |

Both are non-empty, so B1 remains meetable — but the light document's effective tolerance is
**±0.685 %, not ±5 %**, which is seven times tighter than the clause reads and tighter than the
line's own max residual at the worst bed. That is the clause G3 fits against and G4 judges.
(The confounded `1x-light-increased-contrast` key reads 8.7968 over 2 cells and is excluded, because
it is not one of the six declared profiles.)

**The warning the window carries.** A law fitted to the 1x-light median alone lands **−6.08 %**
against the 2x-light bed and fails B1 there; on the dark document the same mistake is −5.4 %. The
fit is therefore a joint one from the start, not a 1x fit checked at 2x afterwards.

**B1's median and the fit's own population are the same number to 0.4 %.** B1 is read against the
bed's median native σ, which is taken over every active cell that resolves a σ, while the σ law is
fitted on non-holdout cells only — two populations, and a bound stated against a number no fit may
see would be unreachable by construction. It is not: at every thick span on every bed that carries
a non-holdout cell, the pooled median and the non-holdout median agree to **≤ 0.354 %** (the worst
is 1x light at span 160; twelve of the fifteen comparisons are exact). The three accessibility beds
carry no non-holdout cell at span 160 at all, which is the extrapolation B1 already declares.

### B2 — the shadow, thin regime (spans 32–44): **a one-wave reading, not adopted**

**The clause.** "No longer 2.8–7.2× too wide", with a numeric bound: the fitted σ_css at span 44 is
**within a factor of 1.5 of the bed's own thin-span median, in both directions** —
`1/1.5 ≤ σ_fitted / σ_bed ≤ 1.5`.

**The statistic it is read by, in full.** The upper middle order statistic of the σ_css of the
**UNTINTED, non-holdout, non-excluded span-44 ACTIVE cells at dpr 1** of that bed. Which is: on
1x light **1.84 over 8 cells** (range 1.42–2.05), on 1x dark **1.54 over 6** (1.42–1.70), on 1x
reduced transparency 1.50 over 3, on 1x increased contrast 1.52 over 3, on the coupled profile 1.50
over 3. Every `-tint-*` scene is excluded, every cell the `σ_css > span` rule removes is excluded
(the 74.3 and 157.7 readings among them), and **dpr 2 is excluded entirely**.

**Why those exclusions, and why 1x only.** §5.156 §2 establishes that in the thin regime the reader's
(amplitude, σ) pair is not identified — the two trade at a nearly constant product between the
scales on the same cell, where at spans 96–160 both are separately scale-invariant — and that the
fitted thin σ bifurcates on the author's **tint**, a parameter the material's blur cannot depend on.
The tinted cells at dpr 2 read σ of 0.57–0.73 CSS px, one to one and a half device pixels, below the
raster's resolution. Excluding them is not convenience: including them is what made the bed-wide
median disagree with its own quoted cell by 21 % at span 44 where the thick spans agree to 0.04.

**Why a factor of 1.5.** It is the bed's own per-cell spread at the statistic's own cells: 1.42–2.05
on 1x light is a full-range factor of **1.44**, and 1.42–1.70 on 1x dark is 1.20. A bound tighter
than the spread would fail on the instrument; 1.5 is the spread rounded up, so the clause asserts
"no wider than the widest cell and no narrower than the narrowest" and nothing more. Against today's
**5.97× (1x light) and 7.14× (1x dark)** it has two and a half orders of room to fail in.

**Not adopted, and the reason is the instrument.** A bound adopted into
`adopted-thresholds.test.ts` is a standing promise about the material; this clause is a statement
about a reading whose identifiability §5.156 §2 has just shown to be poor. It stays a one-wave
reading and the ledger records it. Closing it properly wants a thin-span cell whose amplitude is
large enough for the pair to separate — a `scenes.json` decision, filed with the tracker's existing
thin-span entries.

**The floor's value is declared unfitted.** The law's floor exists for a structural reason — the
line crosses zero at span 23.6–30.4, inside the bed's own range — and no order statistic over the
thin cells is a measurement of Apple's blur. G3 sets it by declaration and records it as a decision.

### B3 — the shadow's departure residual: **the stop condition**

**0.0007 bed-wide, mean absolute** (§5.154 §3), and the joint refit must hold **at or better than**
it. If the σ law lands and the departure residual worsens, the wave has traded a shape for an
energy and the fit is not taken; the anchors are refitted with σ, which is what "jointly" means, and
the residual is the referee. It is a stop, not a bound: it gates whether G3's fit may be sealed at
all, and it is read on the non-holdout cells of every profile.

The six occlusion anchors and `liftAmplitude` carry the compensation for the wrong σ today, and
§5.156 §2 measures the compensation directly: at span 44 vitrea draws a shadow 3.7× too dim over six
times too wide an area, and the two cancel in a mean taken over the whole exterior. The expected
directions are recorded there — `thinOcclusionMid` and `thinOcclusionBright` rise, the three thick
anchors fall with `thickOcclusionAt160` falling most, `thinOcclusionDark` stays exactly 0, and
`liftAmplitude` moves only as the thick anchors' trade partner — and a refit that moves them the
other way is a warning, not a result.

#### B3 restated beside, 2026-09-20 (review closure), per charter Decision Log 3 (a)

*The clause above declares a stop the wave is already past, because it names one tier's number over
both tiers' cells.* Nothing above is rewritten; this is the stop G3 and G4 are judged by.

The quantity is unchanged — `|meanDepartureWeb − meanDepartureNative|`, the shadow axis's own mean
exterior departure, arithmetic mean over rows — and it is now computed rather than quoted:
`departure-stat.py` in this directory reads it off the committed matrix through
`atAShippedDocument`'s partition and `departure-stat.txt` is its output, so G3 and G4 re-run it
instead of transcribing it.

| reading, over the non-holdout cells of all six declared profiles | n | today |
| --- | ---: | ---: |
| **the WebGPU tier — THE STOP** | 166 | **0.00035** |
| the CSS tier, recorded beside | 166 | 0.00124 |
| both tiers pooled, which is what the clause above literally declares | 332 | **0.00079** |
| the two light standard beds pooled, both tiers | 196 | 0.00066 |

**The stop is: the WebGPU tier's mean absolute exterior departure over the non-holdout cells of all
six macOS 27 profiles, 0.00035 today, held at or better by G3's sealed fit.** The both-tier figure
is recorded beside it as the CSS tier's reading and is not a stop: the shadow is fitted on the
WebGPU tier and the CSS tier derives one `box-shadow` blur radius per surface from the same
profile, so a CSS-tier worsening is a recorded residual and not a refusal (the tier rule, Decision
Log 23 of 2026-09-05). A CSS figure that improves is reported; one that worsens is recorded with
what moved it.

**Where 0.0007 came from, and why it is not this bed's number.** It is §5.154 §3's
"0.00681 → 0.00074 mean absolute on the light standard bed", restated here unqualified. That figure
was read during G3b's fit on its own scratch matrices at the moment the anchors were chosen; the
committed matrix does not reproduce it under any partition of the 1x-light-standard bed —
`departure-stat.txt`'s last block prints all eight (0.00022 to 0.00349 on the WebGPU tier, 0.00051
to 0.00432 pooled). The correction is recorded beside §5.154 §3 and §4 as well, and neither figure
there is rewritten.

**What this changes about the wave's difficulty, said plainly.** 0.00035 is tighter than 0.0007 by a
factor of two on the tier that is fitted, so the restatement makes the stop harder, not easier. That
is the point of it: a stop a fit passes by standing still is not a stop.

### B4 — the scatter's structure ratio: **a one-wave reading, not adopted**

**The tolerance.** On the **WebGPU tier**, the interior structure ratio
`interiorStdDevWeb / interiorStdDevNative` on the gated 16 px checkerboard cell
(`checkerboard__rrect-md__rest`, active) moves **toward 1.0 on every one of the six macOS 27
profiles, and past 1.0 on none** — and on the two standard light beds and the two standard dark beds
it lands **within 0.8–1.25**. On the pitch ladder, the same ratio is **reported per pitch** and the
clause is that no pitch that is inside 0.8–1.25 today leaves it.

**The statistic it is read by.** The per-cell ratio itself, from the matrix's own
`material.interiorStdDev{Native,Web}` — linear light over the shared mask — on the row at the sealed
document, exactly as `tier-coherence.test.ts`'s recorded residual reads it (W30 G0 (d)). Today's
values are pinned there and in §5.156 §3 §6: WebGPU **1.5670** (1x light), **0.7489** (1x dark),
**0.4252** (2x light), **0.6374** (2x dark).

**The CSS tier is recorded, not bounded.** Its single `backdrop-filter` cannot express a
two-component kernel at all, so it gets the best scalar projection and its residual goes in the
ledger, per the tier rule (Decision Log 23 of 2026-09-05). Today: CSS **0.9681** (1x light),
**0.3552** (1x dark), **0.3838** (2x light), **0.2537** (2x dark). A CSS ratio that worsens is
recorded; it does not stop the wave.

**Not adopted, and the reason is the bed.** §5.156 §3 establishes that the macOS 27 generation of
`results/matrix.json` carries **no probe row at all**, so the pitch ladder — the row set the operator
is fitted on — has no committed macOS 27 web reading. A ratio adopted into
`adopted-thresholds.test.ts` on one pitch would be a standing promise about a curve read at one
point. It becomes adoptable when the ladder is read at a macOS 27 document, which is the decision
§5.156 §3 puts to the parent for G4's canonical read.

#### B4 scoped beside, 2026-09-20 (review closure), per charter Decision Log 3 (b)

*"Toward 1.0 on every one of the six profiles, and past it on none" cannot be met as written, for a
reason this gate's own tables already carry.* Nothing above is rewritten.

**The binding clause is the four standard beds.** The reduced-transparency and coupled-contrast beds
are **captured at the light standard document** — every one of their rows' `capturePath` names
`profiles/apple-macos-27.0-1x-light-standard-glass0.5.json`, 32 rows and 35 rows respectively, and
no other document appears on either — so they inherit its scatter values by construction and carry
no leaf of their own to move. And they need the operator moved the other way from the bed that is
fitted: the light standard bed reads **1.567** and needs structure removed, while reduced
transparency reads **0.818** and coupled contrast **0.969** and both need it added. One value of one
leaf cannot do both, so a clause binding all six is a clause the wave fails by arithmetic before it
starts.

So: **B4's "toward 1.0 and past it on none" binds the four standard beds whose documents are
fitted** (1x/2x × light/dark). The two accessibility beds are **reported** — their ratio before and
after, with the direction it moved and by how much — which is what B4's own last sentence already
said of the CSS tier and what §5.156 §3 established for these two profiles when it showed five
ladder rungs identify a scalar and not a curve.

**The ladder clause is read on the macOS 27 ladder probe rows, and on nothing else.** "No pitch
inside 0.8–1.25 today leaves it" is read on the rows charter Decision Log 2 (a) grants — the 45
ladder scenes on the WebGPU tier for the four standard profiles and on the CSS tier for the two 1x
standard ones, written `fixtureSet: "probe"` into the macOS 27 generation at G4. Reading it on the
macOS 26.5 ladder instead would be vacuous: that generation is frozen evidence at a material this
wave does not touch, so every one of its 662 metric-carrying probe rows is unmoved by construction
and the clause could not fail. The macOS 26.5 reading is what §5.156 §3 uses to establish the
residual's SHAPE; it is not a bed this wave's operator can be judged on, and that reading is
dropped here.

### B5 — `sizeToneLevelFar`: **declined, and the decline is the declaration**

Its sign is stable per scheme on the macOS 27 gated bed (positive on 4 of 4 light readings, negative
on 2 of 2 dark) and its magnitude is not: within the light scheme the two backdrops disagree by 5.5×.
The row set that would condition it is the ladder, which has no macOS 27 web row. **It stays at 0
and is not fitted in this wave**, and — per the charter's own instruction — it is **not** added to
`tuned-profiles.test.ts`'s `FITTED_CONSTANTS`, which is asserted over the frozen macOS 26.5 light
patch.

---

## (c) The rows this wave claims, with the lever and the tier each is claimed through

Three of the seven `MISSED_27_ROWS`. Each is named with the operator that is supposed to move it and
the tier the operator reaches it on.

| row | measured | bound | lever | why that lever |
| --- | ---: | --- | --- | --- |
| `dom / holdout / checkerboard__rrect-lg__rest / …1x-light-standard… :: ssimMean` | 0.88402 | ≥ 0.9 | **the shadow's σ**, on the CSS tier | span **160**, where the shipped σ is 0.64× the native and the reach is 12 CSS px short; the shadow mirrors FULLY onto the CSS tier (one `box-shadow` blur radius per surface) while the scatter reaches `dom` only as a scalar |
| `dom / holdout / checkerboard__glass-over-glass__rest / …1x-light-standard… :: ssimMean` | 0.89538 | ≥ 0.9 | **the shadow's σ**, on the CSS tier | span **130**, the same lever; and span 130 has no fittable cell anywhere, so this row moves on the line's extrapolation |
| `dom / holdout / photo__rrect-lg__rest / …1x-light-reduced-transparency… :: ssimOutside` | 0.82707 | ≥ 0.83 | the shadow's σ, on the CSS tier — **"reachable if the law extrapolates"** | scored OUTSIDE the silhouette at span 160, which is the shadow's own territory; but that profile's only span-160 native σ (16.97) is read **on this holdout cell itself**, so the law arrives there by extrapolation from the standard beds and nothing fits it |

**Neither `ssimMean` row is claimed through the scatter**, and that is a decision with a measurement
behind it: on 1x light the CSS tier already passes 0.968 of the native structure where the WebGPU
tier passes 1.567 (W30 G0 (d)), so a scalar refitted to carry a WebGPU scatter operator moves these
`dom` rows the wrong way. `tier-coherence.test.ts` pins both readings before the fit so that if it
happens it is seen.

---

## (d) Expected unmoved, and reported but not claimed

**Expected unmoved — the four dark `oklabDeltaEP95` rows.** They are chromatic and the tone solve is
achromatic by construction (W29 Decision Log 6 (c)); the chromatic-transmission child is chartered
separately and this wave does not touch it (X3).

| row | measured | bound |
| --- | ---: | --- |
| `dom / holdout / photo__rrect-lg__rest / …1x-dark-standard… :: oklabDeltaEP95` | 0.20095 | ≤ 0.18 |
| `dom / holdout / photo__rrect-lg__rest / …2x-dark-standard… :: oklabDeltaEP95` | 0.19474 | ≤ 0.19 |
| `texture / holdout / photo__rrect-lg__rest / …1x-dark-standard… :: oklabDeltaEP95` | 0.21521 | ≤ 0.17 |
| `texture / holdout / photo__rrect-lg__rest / …2x-dark-standard… :: oklabDeltaEP95` | 0.21344 | ≤ 0.17 |

**A fit that appears to move them is a warning sign, not a result** (X3, and the charter's Purpose
says so in those words). If G4's read shows one of them moved, the wave records it as evidence that
the scatter reached the chromatic axis, and does not claim it.

**Reported, not claimed — the reduced-transparency body-structure residual.** The preference's whole
purpose is that a backdrop stops showing through, and it shows through. **The declaration names the
instrument with the number, because the two instruments disagree in the residual's direction**
(§5.156 §3):

| instrument | native | vitrea (WebGPU) | ratio |
| --- | ---: | ---: | ---: |
| the sheets (§5.154 §9 (d); 0–255 luminance over the box inset 12 CSS px) | sd **0.43** | sd **3.49** | **8.1×** |
| `results/matrix.json` (`interiorStdDev`, linear light, shared mask) | **0.0562** | **0.0459** | **0.818×** |

G4 reports **both**, on `checkerboard__rrect-md__rest` at
`apple-macos-27.0-1x-light-reduced-transparency-glass0.5`, and reconciling the two instruments is
tracker work, not this wave's. The profile carries three backdrop classes and five ladder fixtures,
so it can identify a scalar and not a curve; it inherits the 1x-light standard document's scatter
values (charter Design) and the residual that leaves is a reading.

---

## What is deliberately not declared

- **No bound on the inactive pose**, on either operator. No inactive calibration cell above span 96
  exists; the receded exterior at span 160 (far-exterior difference 17.42 WebGPU / 15.89 CSS against
  ≤ 5.92 on any active strip) is expected to narrow because the receded documents inherit the active
  block leaf for leaf, and it is **reported on the inactive holdout rows**, not fitted.
- **No bound on the 130 span**, because no bed carries a fittable cell there.
- **No bound on the accessibility profiles' scatter**, because five ladder rungs cannot identify a
  curve; they inherit and report.
- **No floor**, anywhere (§(a)).
- **No claim on the chromatic axis**, the highlight's directionality, the level law's abscissa, or
  the decoupled-contrast read — all out of scope by the charter's own Deferred list.
