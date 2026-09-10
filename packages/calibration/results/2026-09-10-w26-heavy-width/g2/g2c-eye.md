# W26 G2c — the eye's gradient, measured (2026-09-10)

The user's eye on G2b's sheets found something no metric in this wave reports: on the dark
`checkerboard-64` rrects and the dark nested pane the candidate's pane looks **milkiest at its edges
and blackest at its centre**, where Apple's pane and the 0.14.0 material both look uniformly milky.
This is a measurement of that and of nothing else. **It changes no code, no constant, no spec and no
ledger entry** — the parent rules.

Evidence beside this file: `g2c-rings.py` / `g2c-rings.txt` / `g2c-rings.json` (the ring reader),
`g2c-docs.py` and `g2c-rung.sh` (the diagnostic rungs), `g2c-toggle.py` / `g2c-toggle.txt`
(the toggles), `g2c-levels.txt` (§4's two level gaps), and the plots
`sheets/g2c-rings.png` and `sheets/g2c-toggle.png`.

---

## 0. The answer in three lines

1. **The gradient is real and it is ~0.6 codes of added depth-variation on a pane whose own light
   also drops 1.4 codes** — so what the eye sees is mostly the SECOND thing: the uniform milk that
   was masking a depth structure both materials share falls by a third, and the structure surfaces.
   Vitrea's own light varies by **1.9× its mean** across the pane at the candidate, **1.3×** at
   0.14.0, and Apple's by **0.3×**.
2. **The mechanism is the WIDTH and nothing else.** The same new heavy texture at the old width
   (13.418) reproduces 0.14.0 **to the digit** on every statistic. The ramp is not it, the lens is
   not it, the tone response is not it — each was toggled and each is ruled out below.
3. **No constant flattens it** except the width itself. The ramp — the parent's plausible reading —
   is measured and rejected: switching it off makes the variation slightly WORSE (7.19 against
   6.87 codes). What would reduce the eye's complaint is the dark scheme's own LEVEL, which is
   already the tracker's open item and is not this wave's fit.

## 1. What the eye found, quantified

**The reader.** The interior read in 4 CSS px rings from the pane's own signed distance, the first
6 CSS px skipped as rim and shoulder. Per ring, the pane's own light and its transmission of the
backdrop are separated by fitting `interior ≈ milk + trans · backdrop` over the ring's pixels:

- **milk** — the intercept, in 8-bit display codes: what the pane adds whatever is under it.
- **trans** — the slope: the fraction of the checkerboard's contrast that still reaches the eye.

**The raw ring mean is not usable on its own here and the first draft of this reader learned it the
hard way.** A 64 CSS px checker under a 160 CSS px pane puts a dark square at the centre and bright
ones at the edges, so *every* column — the native's included — shows a large apparent "gradient" that
is the backdrop's phase. Every verdict below is on the intercept and the slope; the raw mean is
printed beside them in `g2c-rings.txt` because it is what the eye actually receives.

### 1.1 The dark `checkerboard-64` rrects — where the eye looked

Means and peak-to-peak over the rings, all columns on **identical rings**, so the ranges are
comparable even where one ring is weakly conditioned:

| profile / cell | column | milk mean | milk range | milk range ÷ mean | trans mean |
| --- | --- | --- | --- | --- | --- |
| 1x dark `rrect-lg` | native | **7.38** | **2.34** | **0.32** | **0.0477** |
| | 0.14.0 | 4.95 | 6.29 | 1.27 | 0.0566 |
| | candidate | **3.58** | **6.87** | **1.92** | **0.0673** |
| 1x dark `rrect-md` | native | 6.45 | 5.59 | 0.87 | 0.0527 |
| | 0.14.0 | 5.10 | 5.88 | 1.15 | 0.0534 |
| | candidate | 4.31 | 7.00 | 1.62 | 0.0596 |
| 2x dark `rrect-lg` | native | 7.37 | 2.59 | 0.35 | 0.0487 |
| | 0.14.0 | 3.25 | 7.55 | 2.32 | 0.0699 |
| | candidate | 2.51 | 7.20 | 2.87 | 0.0759 |
| 2x dark `rrect-md` | native | 6.41 | 6.23 | 0.97 | 0.0549 |
| | 0.14.0 | 4.06 | 8.43 | 2.08 | 0.0620 |
| | candidate | 4.11 | 8.62 | 2.10 | 0.0616 |

**So: yes, the candidate has a depth structure the native lacks — but so does 0.14.0.** On the cell
the eye named hardest (1x dark `rrect-lg`) Apple's pane varies by 2.3 codes about a mean of 7.4, and
vitrea varies by 6.3 codes about 5.0 at 0.14.0 and by 6.9 about 3.6 at the candidate. **The
candidate's contribution to the absolute variation is +0.58 codes; its contribution to the RELATIVE
variation is +51 %**, because the mean it varies about fell by 1.37 codes.

### 1.2 The thing that actually moved: a trade, at a conserved total

The raw ring mean — the light the eye receives — barely moves at all:

| profile / cell | raw mean 0.14.0 → candidate | milk | trans |
| --- | --- | --- | --- |
| 1x dark `rrect-lg` | 11.99 → **11.94** (−0.05) | 4.95 → 3.58 | 0.0566 → 0.0673 |
| 2x dark `rrect-lg` | 11.93 → **11.93** (0.00) | 3.25 → 2.51 | 0.0699 → 0.0759 |
| 1x dark `rrect-md` | 12.50 → 12.55 (+0.05) | 5.10 → 4.31 | 0.0534 → 0.0596 |

**The candidate does not darken the pane on average by any amount the eye could see.** It moves light
out of the uniform term and into the term that follows the checkerboard: `milk + trans · mean(bg)` is
conserved to a twentieth of a code. That is the eye's report restated exactly — the pane stops being
uniformly milky and starts showing what is under it — and it is what a narrower blur does by
definition.

### 1.3 It is not a radial ramp, in either material

Edge ring to deepest ring, transmission: native **0.0540 → 0.0537**, 0.14.0 0.0654 → 0.0661,
candidate 0.0735 → 0.0771 (1x dark `rrect-lg`). None of the three ramps meaningfully with depth; the
structure in all of them is the checker's own, and it is common to all three columns. **What
separates the columns is a LEVEL of transmission and a LEVEL of milk, not a gradient in either.** The
eye's "edge→centre" is the checker's phase — bright squares near this pane's edges, a dark one at its
centre — amplified by a transmission that is now 19 % higher over a milk that is now 28 % lower.

## 2. The mechanism, one toggle at a time

Five rungs, each one change against the candidate, all rendered on the same two probe rows
(`g2c-docs.py`, `g2c-rung.sh`). **The rows are PROBE rows only**, deliberately: they carry the effect
and are not in the holdout, so the mechanism is identified without opening
`checkerboard__glass-over-glass` again — X3's one read stays the dry run's, and the nested pane is
read here only from captures that already exist.

| rung | what it changes | 1x dark `rrect-lg`: milk mean / range / trans mean | verdict |
| --- | --- | --- | --- |
| `d9` | nothing — the candidate | 3.58 / 6.87 / 0.0673 | the column complained of |
| **`t13`** | **the same new heavy texture at the OLD width, 13.418** | **4.95 / 6.29 / 0.0566** | **identical to 0.14.0 on every digit** |
| `flat` | the body's depth ramp switched off (reach 0) | 3.87 / **7.19** / 0.0650 | **not the ramp** — slightly worse |
| `nolens` | `lensRefractionGain` 0 | 3.43 / 6.87 / 0.0677 | **not the lens** — an edge-ring effect only |
| `flat13` | the ramp off AND the old width | 5.39 / 6.63 / 0.0532 | the pair, for control |

**(a) It is the width, not the texture path.** `t13` reads 4.95 / 6.29 / 0.0566 / edge 0.0654 → deep
0.0661 — every one of them the 0.14.0 material's number to four decimal places. The mechanism W26
built reproduces the old picture exactly when it is given the old width, so nothing about *how* the
heavy component is now computed contributes to what the eye saw. This also re-confirms claims §5.120
§3a from the other end.

**(b) It is not the ramp.** The parent's plausible reading was that a 13.4 px tap washes the checker
at any share, so the share's spatial ramp is invisible, and a 9 px tap makes it visible. Switching
the ramp off entirely leaves the variation at **7.19 codes against the candidate's 6.87** — the same
size, marginally larger — and moves the transmission by 0.002. The ramp is live (the numbers do
move) and it is not the cause.

**(c) It is not the tone response.** A tone-response effect adds or removes light; §1.2 measures the
raw ring mean conserved to 0.05 codes while milk and transmission trade. There is no light to
attribute to a response curve.

**(d) It is not the lens.** `nolens` changes the FIRST ring's transmission (0.0735 → 0.0795) and
leaves the deepest ring identical (0.0771 both), and the milk range is unchanged to the digit at
6.87. The lens suppresses transmission within a ring or two of the contour — visible as the purple
line's departure at the left edge of every panel of `sheets/g2c-toggle.png` — and cannot produce a
whole-pane effect.

**The light scheme, same rows.** The effect is there and smaller relative to the level, and it
reverses sign against the reference on transmission: 1x light `rrect-lg` reads native 0.3275,
0.14.0 **0.3054** (under), candidate **0.3630** (over). So in the light scheme 0.14.0 sits below
Apple's transmission and the candidate above it, where in the dark scheme both sit above and the
candidate further. On the pane's own light the candidate is the closer of the two at 1x light
(130.80 against a native 134.03, where 0.14.0 reads 138.17).

## 3. What would flatten it

**Not a ramp constant** — §2 (b) rules that out on measurement, so the question as posed has no
answer of that shape. What the rungs actually say:

- **The width is the only lever on this effect.** `t13` restores the 0.14.0 picture exactly, and it
  restores it by giving up the wave. Any intermediate width buys back milk and gives up transmitted
  contrast in the same proportion, along the conserved total of §1.2.
- **The reference's own transmission on this cell is 0.0477 at 1x dark**, against 0.0566 at 0.14.0
  and 0.0673 at the candidate. On this cell and in this scheme **Apple washes the checker MORE than
  vitrea does at either width**, and the candidate moves away from it. Under the assumption that the
  pane's opacity is vitrea's, that transmission implies an effective kernel near **18 device px** at
  1x — twice what the family reader fitted on the same scheme (claims §5.122 §2, 9.15 at dpr 1).
  **That is a contradiction between two instruments on the same material and it is the open
  question this measurement hands up**, not a proposal to re-fit the width on one cell: the
  assumption is load-bearing and §4 shows Apple's pane is also brighter, which a single kernel width
  cannot explain on its own.
- **The eye's complaint is reducible without touching the width**, because it is a ratio: the same
  6.9 codes of variation on Apple's own 7.4-code milk would read 0.93 instead of 1.92. The dark
  scheme's thick-body level is already on the tracker as W26's largest open dark-scheme item
  (claims §5.122 §5c) and §4 measures it here again.

## 4. The two other things the eye named, for the record

`g2c-levels.txt`. Means over the rings, 8-bit display codes; the tracker's, not this wave's fit.

**(a) Apple's TOPMOST nested pane transmits the checkerboard and ours does not — in the dark scheme
only, and it reverses in the light.**

| profile | native trans | 0.14.0 | candidate | |
| --- | --- | --- | --- | --- |
| 1x dark | **0.0016** | 0.0005 | 0.0005 | Apple passes **3.2×** what we do |
| 2x dark | **0.0022** | 0.0006 | 0.0007 | Apple passes **3.1×** |
| 1x light | 0.0113 | **0.0206** | **0.0218** | we pass **1.9×** what Apple does |
| 2x light | 0.0164 | **0.0271** | **0.0304** | we pass **1.9×** |

The dark-scheme absolute amplitude is small — ±0.2 of a code on a full-swing checker against our
±0.08 — so the eye is reading a ratio near the noise floor; the light-scheme reversal is the larger
and better-conditioned reading and it says our top pane is not opaque enough there. The candidate
moves the light rows further from Apple (0.0206 → 0.0218, 0.0271 → 0.0304) and the dark rows not at
all.

**(b) Apple's dark panes are brighter than ours.**

| cell | native raw | candidate raw | Apple − us | native milk | candidate milk | Apple − us |
| --- | --- | --- | --- | --- | --- | --- |
| 1x dark `rrect-lg` | 13.34 | 11.94 | **+1.40** | 7.38 | 3.58 | **+3.80** |
| 1x dark `rrect-md` | 13.86 | 12.55 | +1.31 | 6.45 | 4.31 | +2.14 |
| 2x dark `rrect-lg` | 13.49 | 11.93 | +1.56 | 7.37 | 2.51 | **+4.86** |
| 2x dark `rrect-md` | 14.12 | 12.58 | +1.54 | 6.41 | 4.11 | +2.30 |
| 1x dark nested base | 11.76 | 11.90 | −0.14 | 9.69 | 8.91 | +0.78 |
| 1x dark nested over | 5.27 | 6.09 | **−0.82** | 5.07 | 6.03 | −0.96 |

The dark 64-checker rrects are **1.3–1.6 codes darker than Apple's** in what the eye receives and
**2.1–4.9 codes darker** in the pane's own light; 0.14.0 is darker too, by 1.35 and 2.43 on the first
row, so the candidate deepens a gap it did not create. The nested BASE is level to a seventh of a
code in raw terms and 0.78 short in its own light. **The nested OVERLAY is the exception and it runs
the other way: ours is 0.82 codes brighter than Apple's**, in both schemes.

## 5. What this does not say

- It does not re-fit anything. No constant is proposed and no document is touched.
- It does not read the holdout again: the nested pane is read from the native fixture, the canonical
  0.14.0 bed and W26 G2's own dry run, and every rung rendered here is a probe row.
- The 18 device px of §3 is an INFERENCE under a stated assumption (that Apple's pane has vitrea's
  opacity), offered because it contradicts the family reader and the contradiction is worth the
  parent's attention — not as a reading of Apple's kernel. §4 (b) is the reason to distrust the
  assumption: a pane that is also 1.4 codes brighter is not the same pane with a wider blur.
