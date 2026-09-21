# W31 G0 — the reproduction check (claims §5.161 §2)

Every cell of the scratch re-capture against the committed row of the SAME KEY —
same profile, same scene, same engine build, same `capturePath` and therefore the
same material profile document hash. A key that matches is a row read at the same
bytes of the same documents, so the two numbers are comparable by construction.

**The bar is 5e-4 absolute on both statistics, declared before the check ran.**
`repeatNoise` is 0 on 1,830 of the committed matrix's 1,833 rows, so the row's own
field gives no usable tolerance for a re-capture taken on a different day; the three
rows that do carry one read 3.5e-05, 1.05e-04 and 1.96e-04, and the bar is that
largest value rounded up.

The two halves of the re-capture are reported apart, because they are two
different operations. The macOS 27 half is a FRESH CAPTURE at the shipped
documents — a browser run on this machine today against a row read weeks ago, and
the half the wave's statistic is actually taken from. The macOS 26.5 half is a
`--skip-capture` RE-MEASURE of a copy of the canonical `web-captures/` trees, with
no browser in it at all, so a difference there is a difference between the tree on
disk and the raster the committed row was read from.

| statistic | cells | worst |Δ| overall | macOS 27 | macOS 26.5 | bar | verdict |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `interiorMeanWeb` | 552 | 2.840e-03 | 0.000e+00 | 2.840e-03 | 5.0e-04 | MISSES on macOS 26.5 only |
| `ssimMean` | 552 | 5.825e-04 | 0.000e+00 | 5.825e-04 | 5.0e-04 | MISSES on macOS 26.5 only |

> **2026-09-21, the review closure (claims §5.161 §11, findings N11 (i), N8, N9
> and N12). Three corrections beside the table above, none of them in a number.**
>
> **(i) The header row does not render.** Its third cell is written `worst |Δ|
> overall`, and the unescaped pipes split it into three — the header parses as
> eight cells against the separator's and the data rows' seven, so the columns
> are offset by one wherever this file is rendered as Markdown rather than read
> as text. The header the two rows below it belong to reads:
>
>     | statistic | cells | worst \|Δ\| overall | macOS 27 | macOS 26.5 | bar | verdict |
>
> The numbers are as recorded and the file is otherwise left as the run wrote it.
>
> **(ii) The foreign-process count was never recorded.** `scratch-capture.sh`
> read it with `pgrep -fc`, which BSD `pgrep` does not have: on macOS that exits
> 2 with a usage message, `|| true` swallows the failure and `$FOREIGN` is
> empty. All three "foreign browser automation processes at start:" lines in
> `browser-runs.txt` are therefore blank, and `browser-runs.txt` is left exactly
> as the run wrote it. The script is fixed for a re-run (`pgrep -f 'playwright'
> | wc -l`). What this does NOT change: the disclosed condition was refereed by
> this check rather than by the count — every one of the 552 macOS 27 cells
> reproduces its committed row at |Δ| exactly 0 on both statistics, which is a
> cell-by-cell answer to contention and the count never was one. The RT, IC and
> slider readings on the same lines came from `x6-read.sh` and are intact.
>
> **(iii) The narrowing lives in this gate's own script and propagates to
> nothing.** `cli/compare.ts` carries no exclusivity guard at all — X6's "one
> capture process" has always been enforced by each wave's capture script, and
> every one of them holds its own copy of the `pgrep` pattern. So the decision
> to refuse only another CALIBRATION capture and merely RECORD other browser
> automation is `scratch-capture.sh`'s, for this bed, and a later wave inherits
> W29's and W30's wider pattern unless it copies this one deliberately.
>
> **(iv) The tree these numbers were read against is gitignored scratch.**
> `/tmp/w31-g0-captures` and the scratch matrix beside this file are outside the
> repository, which is the same class of artefact the wave's own Surprise
> records disappearing. `cut.json` preserves the distilled rows; G3 re-derives
> the pre-fit baseline by running `scratch-capture.sh 27` into a fresh tree at
> the shipped documents rather than by reading this one.

## 64 scratch cells have no committed row at the same key

Named before anything is read off them. A scratch cell with no committed twin is
a cell the 0.20.0 generation never carried — a probe row the canonical read did
not include, or a pose no committed run posed — not a reproduction failure.

- `dom / probe / checkerboard-32__capsule-button__rest-tint-orange / apple-macos-27.0-2x-dark-standard-glass0.5`
- `dom / probe / checkerboard-32__capsule-button__rest-tint-orange / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / checkerboard-4__capsule-button__rest-tint-orange / apple-macos-27.0-2x-dark-standard-glass0.5`
- `dom / probe / checkerboard-4__capsule-button__rest-tint-orange / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / checkerboard-64__capsule-button__rest-tint-orange / apple-macos-27.0-2x-dark-standard-glass0.5`
- `dom / probe / checkerboard-64__capsule-button__rest-tint-orange / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / checkerboard-8__capsule-button__rest-tint-orange / apple-macos-27.0-2x-dark-standard-glass0.5`
- `dom / probe / checkerboard-8__capsule-button__rest-tint-orange / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__inactive / apple-macos-27.0-1x-dark-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__inactive / apple-macos-27.0-1x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__inactive / apple-macos-27.0-2x-dark-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__inactive / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__inactive-tint-orange / apple-macos-27.0-1x-dark-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__inactive-tint-orange / apple-macos-27.0-1x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__inactive-tint-orange / apple-macos-27.0-2x-dark-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__inactive-tint-orange / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__rest / apple-macos-27.0-1x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__rest / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__rest-tint-orange / apple-macos-27.0-1x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__capsule-button__rest-tint-orange / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-lg__inactive / apple-macos-27.0-1x-dark-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-lg__inactive / apple-macos-27.0-1x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-lg__inactive / apple-macos-27.0-2x-dark-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-lg__inactive / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-lg__rest / apple-macos-27.0-1x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-lg__rest / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-md__inactive / apple-macos-27.0-1x-dark-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-md__inactive / apple-macos-27.0-1x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-md__inactive / apple-macos-27.0-2x-dark-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-md__inactive / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-md__rest / apple-macos-27.0-1x-light-standard-glass0.5`
- `dom / probe / mid-chroma-solid__rrect-md__rest / apple-macos-27.0-2x-light-standard-glass0.5`
- `dom / probe / photo__rrect-ml__inactive / apple-macos-27.0-1x-dark-standard-glass0.5`
- `dom / probe / photo__rrect-ml__inactive / apple-macos-27.0-1x-light-standard-glass0.5`
- `dom / probe / photo__rrect-ml__inactive / apple-macos-27.0-2x-dark-standard-glass0.5`
- `dom / probe / photo__rrect-ml__inactive / apple-macos-27.0-2x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__inactive / apple-macos-27.0-1x-dark-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__inactive / apple-macos-27.0-1x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__inactive / apple-macos-27.0-2x-dark-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__inactive / apple-macos-27.0-2x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__inactive-tint-orange / apple-macos-27.0-1x-dark-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__inactive-tint-orange / apple-macos-27.0-1x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__inactive-tint-orange / apple-macos-27.0-2x-dark-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__inactive-tint-orange / apple-macos-27.0-2x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__rest / apple-macos-27.0-1x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__rest / apple-macos-27.0-2x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__rest-tint-orange / apple-macos-27.0-1x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__capsule-button__rest-tint-orange / apple-macos-27.0-2x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-lg__inactive / apple-macos-27.0-1x-dark-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-lg__inactive / apple-macos-27.0-1x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-lg__inactive / apple-macos-27.0-2x-dark-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-lg__inactive / apple-macos-27.0-2x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-lg__rest / apple-macos-27.0-1x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-lg__rest / apple-macos-27.0-2x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-md__inactive / apple-macos-27.0-1x-dark-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-md__inactive / apple-macos-27.0-1x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-md__inactive / apple-macos-27.0-2x-dark-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-md__inactive / apple-macos-27.0-2x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-md__rest / apple-macos-27.0-1x-light-standard-glass0.5`
- `texture / probe / mid-chroma-solid__rrect-md__rest / apple-macos-27.0-2x-light-standard-glass0.5`
- `texture / probe / photo__rrect-ml__inactive / apple-macos-27.0-1x-dark-standard-glass0.5`
- `texture / probe / photo__rrect-ml__inactive / apple-macos-27.0-1x-light-standard-glass0.5`
- `texture / probe / photo__rrect-ml__inactive / apple-macos-27.0-2x-dark-standard-glass0.5`
- `texture / probe / photo__rrect-ml__inactive / apple-macos-27.0-2x-light-standard-glass0.5`

## 2 cells DO NOT reproduce, named before their new statistic is read

| cell | interiorMeanWeb scratch / committed | ssimMean scratch / committed |
| --- | --- | --- |
| `texture / holdout / photo__glass-over-glass__rest / apple-macos-26.5-1x-light-standard` | 0.68650 / 0.68934 | 0.99439 / 0.99381 |
| `texture / holdout / photo__glass-over-glass__rest / apple-macos-26.5-2x-light-standard` | 0.68651 / 0.68904 | 0.99581 / 0.99551 |

**The cause, diagnosed rather than guessed.** Both are the `texture` tier of the
stacked cell, and both were RE-MEASURED from the canonical tree with no browser
involved — so the metric and the mask are today's on both sides of the
comparison. The `dom` tier of the same two cells reproduces to the last bit
(|Δ| exactly 0), which is only possible if `interiorLevel`, the native
silhouette it is masked by and the background it is differenced against are all
unchanged. That leaves one thing that can differ: the `__webgpu.png` on disk is
not the raster the committed row was read from. The canonical tree's files are
dated 2026-09-10 and the committed rows were measured 2026-09-11.

This is the charter's Surprise with a number attached. `CLAUDE.md` says the
canonical `web-captures/` 'is what the sheets and the demo fixture are copied
from'; on these two cells it is already a DIFFERENT generation from the rows
beside it, and nothing would have said so. Consequence for this child, and it
is narrow: the macOS 26.5 columns of `cut.md` for `photo__glass-over-glass__rest`
on the two light profiles' texture tier are read off pixels the committed row
was not read off. They are tabled and they carry this sentence. No macOS 27
cell is affected, no bound is declared on a macOS 26.5 row, and the freeze is
untouched — a capture tree is gitignored scratch, not committed evidence.

