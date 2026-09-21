# W32 G0 — what the directions say

The tables are `exterior-cut.txt` §9 (`T_dir` per bed, per span, per direction, per tier, per
pose), §9b (the per-band `Δa` and `Δc` medians per direction) and §10 (the reach). This file is the
paragraph clause 1 asks for, with the numbers it rests on beside it. Nothing here is fitted or
adopted; every figure is a cut of the current generation and is reproducible by running
`exterior-cut.py`. Claims §5.166.

## The paragraph

**The offset is right and the width is wrong, and the direction resolution is what separates
them.** At spans 96 and 128 — the two spans where all four directions carry a shadow on both sides
and the frame still holds the reach — the extent excess is **+5.00 CSS px in every direction**,
above, below, left and right alike, while the fitted displacement `offsetY` (web − native) reads
**0.00 at span 96 and −0.25 at span 128**: vitrea's exterior sits where Apple's sits and is
uniformly five px too far out, which is what an outset is and is not what an offset is. Below span
96 the instrument cannot say so, because **`above` reads exactly 0.00000 on every band on both `Δa`
and `Δc`, on every standard bed and every accessibility bed, at spans 32 AND 44** — not because the
two renders agree above a thin caster but because **neither draws anything there**: the native and
the web transmission are both exactly 1.000000 from 3 CSS px outward, and both extents are 0. The
offset is therefore identified ONE-SIDEDLY at the thin spans, and `offsetY` is degenerate there
rather than merely uncertain: it is `(below − above) / 2` with `above` = 0 on both sides, so its
apparent +2.25 to +2.50 px excess is half the downward width excess and carries no displacement
information at all. `above` begins to carry shadow at **span 96** (0.00183–0.00215 on the four
standard beds), overtakes `below` at **span 128** (0.00843–0.00975 against 0.00813–0.01022) and by
**span 160** is 2.7× it on the light beds (0.01245–0.01247 against 0.00455–0.00463). The width
excess is isotropic where it can be read; the per-band error is not, and the two shapes are
different: at 96–160 `above` is **front-loaded** (−0.0123 at `3-6` falling to −0.0000 at `12-24` on
1x light span 96) where `below` is **back-loaded** (−0.0039 rising to −0.0128 over the same bands),
which is the signature a pooled ring mean cannot express and a joint fit of `spreadPx`, `offsetPx`
and σ is what resolves. And the decay the shape statistic exists to read is present at span 96 and
gone by 160: `Δa` in direction `all` runs −0.0107 / −0.0115 / −0.0066 / −0.0000 across the four
bands at span 96 — the two exteriors become the same object by 48 CSS px — and −0.0077 / −0.0078 at
span 160 with the two bands the frame ate reading (−0.0100) and (−0.0069), so inside the clearance
it is flat and outside it, where the corners still carry a reading, it **grows**. The thin spans'
inner-band `Δa` is therefore a **width** error weighted by where the amplitude is, not a
displacement error: it is −0.0389 / −0.0388 below against −0.0201 / −0.0037 left and −0.0083 /
−0.0017 right at span 44 on 1x light, an asymmetry of 2–5× in the ERROR, while the extents behind
it are +4.50 below, +4.00 left and +4.50 right — an asymmetry of 1.1× in the WIDTH. The error is
largest below because that is where the shadow is, not because the shadow is in the wrong place.

## The readings, in full

### `above` against `below`, `T_dir`, WebGPU tier, active, non-holdout, admitted bands

| bed | span 32 | 44 | 96 | 128 | 160 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1x light `above` | 0.00000 | 0.00000 | 0.00184 | 0.00843 | 0.01247 |
| 1x light `below` | 0.00776 | 0.00816 | 0.00568 | 0.00813 | 0.00463 |
| 2x light `above` | 0.00000 | 0.00000 | 0.00183 | 0.00898 | 0.01245 |
| 2x light `below` | 0.00759 | 0.00809 | 0.00552 | 0.00829 | 0.00455 |
| 1x dark `above` | 0.00000 | 0.00000 | 0.00215 | 0.00975 | 0.01318 |
| 1x dark `below` | 0.00446 | 0.00480 | 0.00553 | 0.00905 | 0.00645 |
| 2x dark `above` | 0.00000 | 0.00000 | 0.00197 | 0.00931 | 0.01386 |
| 2x dark `below` | 0.00443 | 0.00472 | 0.00528 | 0.01022 | 0.00604 |

`above` is exactly 0.00000 — min and max both — on all four standard beds and on both accessibility
beds at spans 32 and 44. The admitted set is `3-6/6-12/12-24/24-48` at 32, 44 and 96,
`3-6/6-12/12-24` at 128 and `3-6/6-12` at 160.

### Left and right against above — is the width excess isotropic?

`T_dir` on 1x light: `left` 0.00092 / 0.00242 / 0.00465 / 0.00979 / 0.00866 and `right` 0.00112 /
0.00157 / 0.00418 / 0.00911 / 0.00908 across spans 32 → 160. Left and right agree with each other
to 0.0005 at every span, which is the bed saying the two renders are symmetric about the vertical
axis — as both materials are by construction, and as `offsetX` confirms at web − native 0.00 at
every span.

The extents are the sharper reading, because they are a length rather than a transmission
(`exterior-cut.txt` §10, WebGPU, active, non-holdout, CSS px, median):

| span | above nat → web | below | left | right | offsetY web − nat |
| ---: | --- | --- | --- | --- | ---: |
| 32 | 0.00 → 0.00 (+0.00) | 8.00 → 13.00 (+4.50) | 2.00 → 5.00 (+3.50) | 2.00 → 5.00 (+3.00) | +2.25 |
| 44 | 0.00 → 0.00 (+0.00) | 8.00 → 13.00 (+4.50) | 2.00 → 6.50 (+4.00) | 2.00 → 6.00 (+4.50) | +2.50 |
| 96 | 2.00 → 7.00 (+5.00) | 17.00 → 22.00 (+5.00) | 10.00 → 15.00 (+5.00) | 10.00 → 15.00 (+5.00) | **0.00** |
| 128 | 11.00 → 15.50 (+5.00) | 27.00 → 30.50 (+4.00) | 20.00 → 25.00 (+5.00) | 19.00 → 24.00 (+5.00) | **−0.25** |
| 160 | absent on both sides, 0 of 28 | — | — | — | — |

**+5.00 CSS px in all four directions at span 96**, and +4.00 to +5.00 at span 128, with the
displacement agreeing to a quarter of a pixel. At the thin spans `above` is 0 on both sides and the
excess is +3.00 to +4.50 in the three directions that carry a shadow at all.

**Corrected beside, 2026-09-21 (review closure; claims §5.166 §10, finding N2).** The +5.00 in all
four directions is **span 96 only** (44 cells). At span 128 `below` reads **+4.00**, 27.00 → 30.50,
on the 25 of 26 rows carrying an extent on both sides; above, left and right read +5.00 there. §10's
table already prints it; the paragraph and the table above rounded it up. The "outset, not offset"
conclusion is unchanged — the anisotropy is about one pixel against five of excess, with `offsetY`
at −0.25.

### Does the per-band `Δa` decay?

1x light, direction `all`, bands `3-6` / `6-12` / `12-24` / `24-48`, with a band outside the
clearance in parentheses:

| span | 3-6 | 6-12 | 12-24 | 24-48 |
| ---: | ---: | ---: | ---: | ---: |
| 32 | −0.01754 | −0.01229 | −0.00048 | 0.00000 |
| 44 | −0.01865 | −0.01494 | −0.00058 | 0.00000 |
| 96 | −0.01073 | −0.01151 | −0.00661 | −0.00004 |
| 128 | −0.00750 | −0.00926 | −0.00897 | (−0.00204) |
| 160 | −0.00766 | −0.00782 | (−0.01001) | (−0.00694) |

Decay to inside the native-pair bar by 24 CSS px at spans 32 and 44, by 48 at span 96, not at all
at 128 and 160. The profile's PEAK also walks outward with the span — `3-6` at 32 and 44, `6-12` at
96, `6-12`/`12-24` at 128, `12-24` at 160 — which is the falloff getting wider with the caster on
both sides and the error following it.

### The thin regime: displacement or width?

1x light span 44, per-band `Δa` by direction:

| band | above | below | left | right |
| --- | ---: | ---: | ---: | ---: |
| 3-6 | 0.00000 | −0.03849 | −0.02012 | −0.00833 |
| 6-12 | 0.00000 | −0.03875 | −0.00374 | −0.00168 |
| 12-24 | 0.00000 | −0.00159 | 0.00000 | 0.00000 |

Asymmetric in the error by 2–5× and nearly symmetric in the width (+4.50 / +4.00 / +4.50 CSS px of
extent excess below, left and right), so what the asymmetry measures is where the amplitude sits,
not where the shadow sits. The one direct reading of displacement the axis offers at these spans —
`offsetY` — is degenerate, because `above` is 0 on both sides and `(below − above) / 2` is then half
a width. **The thin regime does not identify `offsetPx` on this bed**, and that is the condition
clause 1 asks G0 to state: at spans 32 and 44 the fit sees three directions of width and no
displacement at all; at 96 and 128 it sees four directions of width and a displacement that already
agrees; at 160 it sees neither extent nor offset, on either side.

### The CSS tier, recorded

`T_dir` on the CSS tier is in `exterior-cut.txt` §9's third and fourth blocks and its extents in
§10's. It is not bounded (the tier rule, Decision Log 23 of 2026-09-05) and it derives one
`box-shadow` blur radius per surface from the same leaves, so its exterior moves with the fit
through the documents and is a consequence rather than a second target.

### The inactive pose

Tabled in the same four sections and read as its own population. Its finding is not a direction
finding and is recorded in `bounds-declaration.md` §5: **Apple's receded window removes no light at
all from 3 CSS px outward**, on every inactive cell of the bed.
