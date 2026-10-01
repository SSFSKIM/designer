# Decision Log 7 — DRAFT for the user: what G3 refits at 0.25, the bounds it is held to, and S1 (W43 G2, 2026-10-02)

**Status: DRAFT. Nothing here is ruled.** It is written from G2's first stage (claims §5.200),
before any vitrea render at 0.25 exists, as the charter asks (G2 (e); clause 7; X3, X44;
Decision Logs 5 and 7). Decision Log 5, the bounds, is put beside it re-instantiated at 0.25
(item 10), and S1 is put restated from the perfect-endpoint map (item 11). Every number is Apple
against Apple, read against a bar declared and hashed before the first pair
(`bar/bar-declaration.md`, `a8659d7e…`); the per-law verdicts are `delta/verdicts.txt`, the
magnitudes `delta/law-tables.txt`, and the eye sheets were sent to your MacBook as
`w43-g2-sheets.zip` (53.5 MB; open `OPEN-ME.html`).

## What Apple's slider did between 0.5 and 0.25

The change is the body and its first two CSS px, and nothing outside them. Changes are 0.25 minus
0.5. "Codes" are encoded sRGB, and "held-in" means every cell but rrect-lg's (item 9).

| law | verdict (declared rule) | what moved, as the eye sees it | where |
| --- | --- | --- | --- |
| interior level | MOVED | **Light body darker:** a median 3.3 codes active and 7.3 receded, and 13–15 codes over black and dark-solid. **Dark body:** no change on uniform backdrops below span 96 (the deep body byte-identical on 42 of 44 cells, the other two by one code); brighter by 1.5–3.4 codes at spans 128 and 160, and by 2.1 at 96 when receded | light, both poses; dark at s ≥ 96 |
| tone by backdrop | MOVED | The transfer slope rises: light checkerboard 0.082 → 0.150, photo 0.53 → 0.64. The light offset falls about 0.05 linear; the dark offset barely moves | both schemes |
| scatter | MOVED | More of the backdrop's structure survives: interior spread ×1.1–1.7 on most structured backdrops in both schemes; the light receded fine checkers (pitch 4, 8) and impulse fall instead (×0.81–0.94); ×1.00 on dark solids | both schemes, both poses |
| chroma | MOVED (small) | Light body chroma +9 % on mid-chroma-solid and +13–17 % on photo; dark unchanged (×0.96–1.00) | light |
| tint shade | MOVED | The light receded tint's lightness falls 0.025 OKLab L (orange 0.105 → 0.080); light active −0.001; dark about 0 | light receded |
| the recede | MOVED | The light recede deepens: the recede's body change is a further −0.015 linear (1x) and −0.014 (2x) at 0.25; dark recede unchanged (median 0.0000) | light |
| rim band, highlight | MOVED (by the rule) | On uniform backdrops the **dark** rim and highlight are unchanged to four decimals. The **light active** rim excess falls 5 % (0.078 → 0.072) and the brightest bin 5 % (0.122 → 0.116), with the body. No receded rim at either position | light active, following the body |
| exterior shadow | MOVED (by the rule) | **The shadow field did not move.** From 2 CSS px outward, 457 of 458 held-in cells are byte-identical (the other differs by one code); the shadow's mean departure agrees to five decimals and its σ is 8.57 → 8.57 px (light) and 8.87 → 8.90 px (dark). The verdict is the rule reading the 0–2 CSS px rings, where the body's own edge changed (a median 0.05–0.12 codes, at most 9–11) | — |
| silhouette, contour | MINORITY | Median magnitude 0. Every component's implied corner radius is unchanged (capsule 17.99 → 17.95 px, the rest identical) | — |

Memo F's pointers are confirmed where they could be read: w, λ, the light fill and the dark cap
move, and the shadows, the highlight's inputs and the geometry do not. The rrect-lg stratum, whose
backdrop capture scale changes with x, moves like the rest in the body, and also differs by up to
112 codes in its first two exterior CSS px on structured backdrops.

## The questions

**1. Should G3 refit the light body's level and tone, in both light documents?**
*Recommendation: yes, first.* This is the largest change Apple made: 3–15 codes on every light cell,
in both poses. The refit uses the existing leaves (X44): `backdropToneResponseThin` and `…Thick`
with `backdropToneAnchorX` held, `optics.regular.tintAlpha`, and the black branch's
`backdropToneBlackThin` and `…Thick`, because the light body over black moves 13–15 codes and X1
reads exactly there. The light receded document refits its own patch of the same families.
*Alternative:* refit tone only and hold `tintAlpha`. That is sound if the pre-fit render (the 0.5
documents on the 0.25 cells, which G3 makes first) shows the offset closing without it. It costs
one degree of freedom against the slope.

**2. Should G3 refit the structure transmission, the scatter, in all four documents?**
*Recommendation: yes, second.* The transfer slope rises ×1.1–1.9 and the interior spread ×1.1–1.7
on most structured backdrops, in both schemes and poses (the light receded fine checkers and impulse
fall slightly instead). This is the w-driven term memo F
predicted: the narrow detail kept goes from 50 % to 75 % on the free side. The leaves are the
`sizeScatter…` family (gain, floor, ramp starts, heavy tap and share, `sizeScatterScaleGain`) and
`blurSigma`. *Alternative:* hold the scatter and let M2 name the texture misses. That is sound if
you want G3 small: the charter already predicts the shipped two-sided form cannot carry the more
one-sided 0.25 body (Design, "The w-test"), so a scatter refit buys part of a gap the structure wave
must close anyway.

**3. In the dark documents, should only the thick tone and the scatter move?**
*Recommendation: yes.* On uniform backdrops below span 96 the dark body did not change: it is
byte-identical on 42 of 44 cells. Memo F says why to expect that: the dark fill is inert below 0.5,
and a uniform backdrop makes the wide and narrow terms equal. The body brightened 1.5–3.4 codes only
at s ≥ 96, where memo F's MaxLuma cap relaxes. So move
`backdropToneResponseThick` (active and receded) and the scatter (item 2). Hold the thin ordinates,
the black branch, `tintAlpha` and `bodyChromaRetention` at their 0.5 values. *Alternative:* refit all
four dark tone ordinates jointly. That is sound if the fit shows the thin ordinates trading against
the scatter on structured cells. The bar then still requires the dark solids to come back unchanged.

**4. Should the body chroma retention move?**
*Recommendation: in the two light documents only, and only after items 1–2.* Apple's light body
carries 9–17 % more of a chromatic backdrop's chroma at 0.25. The dark body carries the same. A
clearer body may carry part of this through vitrea's luma-preserving retention once the level and
alpha move, so read the candidate first. *Alternative:* hold `bodyChromaRetention` everywhere and
name the residual. That is sound if the first candidate already sits within M1's window
(median 0.8–1.2).

**5. Should the tint shade move?**
*Recommendation: hold `tintShadeLight`/`…Dark` unless the first candidate misses.* The tinted body is
composed over the body, so items 1–2 move it. Only the light receded tint changed by a visible amount
(−0.025 L). *Alternative:* refit `tintShadeLight` in the light receded document from the start.
That is sound if you would rather spend the degree of freedom than a second candidate.

**6. Do the rim and the highlight move?** *Recommendation: no; hold every rim and highlight leaf.*
Memo F declares their inputs unchanged. Where the body did not change (dark, uniform) the rim and
highlight are unchanged to four decimals. Where it did (light active), they fell 5 % with it, which
vitrea's `rimLevelGain` (rim alpha conditioned on the body level) is meant to carry. G3 checks that
the light active rim excess follows Apple's −0.0037 and names the residual if not. *Alternative:*
refit `rimAlpha`/`rimLevelGain` in the light active document only. That is sound only if the pre-fit
render shows vitrea's rim excess not following the body.

**7. Does the outer shadow move?** *Recommendation: no; hold every `outerShadow` leaf in all four
documents, including the receded zeros.* The field from 2 CSS px outward is byte-identical on 457 of
458 cells, and the declared rule's "moved" is the body's own edge in the first rings. C1 then carries
over at its 0.5 values (item 10). There is no sound alternative for the field. A near-ring amplitude
change would be fitting the body's edge with the shadow.

**8. How should the receded 0.25 documents be built?** *Recommendation:* each is, as at 0.5, a
difference over its own scheme's 0.25 active document. The light one is refit (items 1, 4, 5): the
light recede deepened by a further −0.015 linear. The dark one carries the 0.5 receded difference
except where items 2–3 move it, since the dark recede did not change. *Alternative:* carry both 0.5
receded differences unchanged over the new active documents. That is sound for dark. For light it
would ship a named miss of about 4 codes on every receded cell.

**9. What about rrect-lg, whose capture scale moves with x?** *Recommendation:* fit and gate on every
cell, as W29 did, and report rrect-lg as its own stratum. Its body moves like the rest. Its exterior
edge differs by up to 112 codes on structured backdrops, which no vitrea leaf models (X44 forbids
adding an operator), and that is a named gap. *Alternative:* keep rrect-lg out of the fit objective
and in the gate. That is sound if its edge residual drags the body fit on the other shapes.

**10. Decision Log 5, the bounds, re-instantiated at 0.25.** *Recommendation: (a)–(e) as Decision Log
5 drafted them, with these readings from the delta:*
- **(a)** The four 0.25 profiles take the 0.5 tables' values per tier, declared before G3's read.
- **(b)** The material rows over the 0.25 standard profiles, WebGPU tier:
  - **M1:** median in [0.8, 1.2], cells in [0.6, 1.4]. Item 4 decides whether it is met by refit or
    named.
  - **C1:** ≤ 0.0042 per bed × span. Apple's exterior did not move and item 7 holds the shadow, so C1
    should reproduce its 0.5 readings; any C1 change at 0.25 is then a defect, not a fit.
  - **X1:** zero pixels above native black. The light black body moved 13–15 codes, so X1 is item 1's
    referee.
  - **L1:** absolute ≤ 0.055, growth ≤ 0.005 against the pre-fit baseline (the 0.5 documents rendered
    on the 0.25 cells).
  - **M2:** directional against Apple's 0.25 texture (W42 Decision Log 5a's form), its reference
    that pre-fit render. Apple's 0.25 texture is ×1.1–1.7 the 0.5's on structured backdrops, so
    every successful move is an M2 miss. Without the directional form M2 would forbid item 2.
  - **E2:** per cell in absolute codes against the same render.
- **(c)** S1 as item 11.
- **(d)** No regression floor: the bed is at seven runs.
- **(e)** Every non-holdout miss ruled by you, as a named miss or a stop, before the holdout is read
  and before anything publishes (clause 10).

*Alternative:* (e) as "0.25 ships only if every bound holds". That is sound only if you would rather
not ship a clearer glass than ship one with named gaps. The charter predicts the shipped form's
structural miss grows at 0.25.

**11. S1, restated from the perfect-endpoint map.** As chartered, S1 fails Apple itself. With Apple's
own 0.25 in vitrea's place, 78 of 346 WebGPU cells (interior level) change with the wrong sign and
279 leave [0.8, 1.2] (`s1/s1-null.txt`). They are the cells where Apple barely moved (median |ΔA|
0.0024 linear) and the shipped 0.5 render already errs by more: 49 of the 78 are dark, 36 are
capsules. The charter's example restatement, the shipped render within the bar of Apple, keeps 0–2
cells, because the bar is the run-to-run spread.
*Recommendation: R2.* Over the non-holdout standard cells where Apple's change exceeds both its bar
and the shipped 0.5 render's own error there (|ΔA| > |e₀.₅|), vitrea's change has Apple's sign on
every cell, and the median ratio of vitrea's change to Apple's, pooled over the four profiles per
tier, lies in [0.8, 1.2]. Per-profile medians are reported, not gated: the dark profiles carry 14–17
WebGPU cells and the 2x dark CSS tier 2.
- The population is fixed now from the X41-frozen rows (`s1/r2-population.json`: 183 WebGPU and 125
  CSS cells on interior level, 53 %), so no candidate can choose it.
- On the null a perfect endpoint passes on both tiers (median ratio 1.06 WebGPU, 1.05 CSS), and an
  unmoved endpoint fails.
- It reads `interiorMean` off the rows, as G3 will, and is adopted only by your ruling at the
  landing, as Decision Log 5 (c) says.

*Alternatives:*
- **R1** (|e₀.₅| ≤ 0.2|ΔA|; 67 WebGPU cells, 12 of them dark). Sound if you want S1 to speak only
  where the shipped 0.5 is nearly exact. It says almost nothing about the dark scheme.
- **The mask-free `bodyLevel`** in place of `interiorMean`. It behaves the same on the null (181
  WebGPU cells under R2). It is sound if you would rather S1 not depend on the extracted silhouette,
  at the cost of reading the capture tree at G3 instead of the rows.

## What G3 does first, whatever is ruled

It renders the 0.5 documents on the 0.25 cells in candidate mode, in scratch. That is the pre-fit
baseline L1, M2 and E2 read against. On it, G3 checks items 5–8's "hold unless" conditions before
fitting anything.

## What this draft does not decide

- The w-test and the ladder (G2's second stage, after G1b).
- Any law form: X44 holds the 0.5 leaf set.
- The accessibility leaves, which carry over unmeasured (Decision Log 2 (b)).
