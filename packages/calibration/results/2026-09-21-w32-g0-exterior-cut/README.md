# W32 G0 — the direction-resolved exterior cut and the declarations

Claims **§5.166**. Charter `docs/doperpowers/specs/2026-09-21-w32-shadow-wave.md`, acceptance
clauses 1 and 2. **No capture was taken, no browser was run, no material constant, profile document,
golden, bound, floor or row of `results/matrix.json` moves, and nothing under a macOS 26.5-keyed
path is touched** (X1, X2, X5). `scenes.json` gains one `$comment-w32-g0` field beside `rrect-ml`
and nothing else (X11).

## What to read, and in what order

| file | what it is |
| --- | --- |
| `bounds-declaration.md` | **the declaration** — C1 in three forms with their bounds, the candidate row in `adopted-thresholds.test.ts`'s idiom, every stop with today's reading, the missed rows decomposed, the recede's reading, the rows expected unmoved |
| `directions.md` | what the directions say, in one paragraph, with the readings under it |
| `clearance.txt` | the clearance against the shipped reach per span; `rrect-ml`'s declaration upheld and narrowed; span 160's qualification with numbers |
| `exterior-cut.txt` / `.json` | the reader's own output: §0b the admitted-band rule, §3c the two band rules side by side, §9 `T_dir`, §9b the per-band profile per direction, §10 the reach, §11 the departure, §12 the inactive pose |
| `model-fit.txt` / `.json` | the renderer's falloff model on both sides: Apple's outset, the model's own error, the one-sided read, the conditioning |
| `c1-forms.txt` / `.json` | the three forms of C1, their bounds by the charter's rule, `CONTRIBUTING_CELLS`, and G0's recommendation |
| `stops.txt` / `.json` | every stop read today: candidate (i), B3 and the window-restricted departure, the thin regime per cell, M1/M2, the unmoved rows, the recede, `MISSED_27_ROWS` |
| `recede-26.5.txt` / `.json` | *(review closure, N16 and B1)* the recede's census on BOTH generations — 235 of 235 frozen macOS 26.5 rows flat, and the macOS 27 population counted at 121 non-holdout and 153 with the holdout |
| `recede-cross-section.txt` / `.json` | *(review closure, N16)* the receded exterior read off the fixture PNGs: how far out the capture differs from its background at all, and what the one differing pixel is |
| `extents-by-backdrop.txt` / `.json` | *(review closure, N17)* Apple's ACTIVE native reach per direction, per backdrop, per span, macOS 27 against 26.5 — the table that separates the backdrop from the span |

## The scripts, and what each is a copy of

| script | provenance |
| --- | --- |
| `exterior-cut.py` | W31 G1's `exterior-instrument.py`, copied and extended (its docstring names the five changes) |
| `shadow-law.py` | W30 G3's, copied byte for byte; run here as `--fit-on non-holdout --at-shipped` → `shadow-law-at-shipped.txt`, `shadow-law.v2.json` |
| `departure-stat.py` | W31 G3's, copied byte for byte; run with no argument → `departure-stat.txt` / `.json` |
| `reach.ts` | W30 G3's `reach-pad.ts` in shape; evaluates the runtime's own `outerShadowReachPx` and writes `reach.json` |
| `clearance.py` | new; joins the bed's clearance to the runtime's reach |
| `model-fit.py` | new; pure standard library, about ten minutes on the committed matrix |
| `c1-forms.py` | new; reads `exterior-cut.json` only |
| `stops.py` | new; reads `exterior-cut.json`, `departure-stat.json`, `matrix.json` and W31 G4's `chroma-cut.json` |
| `recede-26.5.py` | new at the review closure; imports `exterior-cut.py` and overrides its generation prefix, so the census is the same statistic on a different bed rather than a second implementation |
| `recede-cross-section.py` | new at the review closure; decodes the committed fixture PNGs with the standard library (`zlib`) and walks outward from the component's own rectangle |
| `extents-by-backdrop.py` | new at the review closure; imports `exterior-cut.py` the same way, reads `extent*Native` on both generations |

## To reproduce

```bash
cd packages/calibration/results/2026-09-21-w32-g0-exterior-cut
python3 exterior-cut.py > exterior-cut.txt
python3 exterior-cut.py --with-holdout > exterior-cut-with-holdout.txt
npx tsx reach.ts > reach.txt
python3 clearance.py > clearance.txt
python3 model-fit.py > model-fit.txt
python3 c1-forms.py > c1-forms.txt
python3 departure-stat.py > departure-stat.txt
python3 shadow-law.py --fit-on non-holdout --at-shipped > shadow-law-at-shipped.txt
python3 stops.py > stops.txt
python3 recede-26.5.py > recede-26.5.txt                 # review closure
python3 recede-cross-section.py > recede-cross-section.txt
python3 extents-by-backdrop.py > extents-by-backdrop.txt
```

`c1-forms.py` and `stops.py` read `exterior-cut.json`, so the reader runs first.

**`model-fit.json` is not byte-reproducible, and `model-fit.txt` is** (added 2026-09-21, review
closure; claims §5.166 §10, finding N14). Re-run on the same matrix, the printed text is
**byte-identical** and the JSON differs at **31 leaves**, all of them `threshold` or `residual`
inside the `conditioning` block: the profile likelihood sums a subsample in an order the simplex's
own path decides, and float addition is not associative. The differences are at most **6.1 × 10⁻¹⁵
relative** — up to 45 ULPs on the smallest thresholds, which are 7.6e−07. **No decision field
moves**: `bestSpread`, `interval`, `shippedSpreadInside`, `flatWithinBar`, `n` and `bar` are
identical on all forty entries, and no figure this gate records comes from the differing leaves.
So a diff on that file is expected to be non-empty and a diff on the text is not; check the text.

## The four things a reader of §5.166 should take away

1. **The admitted band set is `3-6 / 6-12` at span 160 and `3-6 / 6-12 / 12-24` at span 128**, not
   what the charter expected; at span 128 the `24-48` band is outside the frame on the left and
   right too, by half a pixel.
2. **The offset is right and the width is wrong.** +5.00 CSS px of extent excess in every direction
   at spans 96 and 128, with `offsetY` web − native at 0.00 and −0.25.
   *Corrected beside, 2026-09-21 (review closure; claims §5.166 §10, finding N2):* +5.00 in all four
   directions is **span 96** only; at 128 `below` is **+4.00** (25 of 26 rows) against +5.00 above,
   left and right. The "outset, not offset" reading stands — one pixel of anisotropy against five
   of excess.
3. **Apple's own outset reads 0.0–1.0 CSS px** at spans 32, 44 and 96, with vitrea's 3.10 outside
   the one-sigma interval on every standard bed there — §5.162 §9's finding N-10, answered.
4. **Apple's receded window removes no light at all from 3 CSS px outward**, on 100 of 100 inactive
   cells, while vitrea draws the active shadow there leaf for leaf. The recede is not the active
   shadow at a lower alpha; on this bed it is not an outer shadow at all.
   *Corrected beside, 2026-09-21 (review closure; claims §5.166 §10, finding B1):* the population
   is **121 of 121** non-holdout inactive WebGPU rows (`exterior-cut.txt` §12c's `n` column) and
   **153 of 153** with the holdout admitted (`recede-26.5.txt` §3) — and *(finding N16)* the same
   census over the FROZEN macOS 26.5 rows reads **235 of 235**, so the recede has never been an
   outer shadow on this bed (`recede-26.5.txt`, `recede-cross-section.txt`).
