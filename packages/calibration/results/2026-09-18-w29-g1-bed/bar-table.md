# The 26.5 bar per cell — committed for W29 acceptance clause 2, and verified

Clause 2 asks G1 to commit "a table of the 26.5 bar per cell where the manifest's
`bedProvenance` can attribute it … and names the cells it cannot attribute as such". G0 drafted
that table (`results/2026-09-18-w29-g0-preflight/bar-table.md`) and G1's instruction was to
**verify it rather than copy it**. This is the committed table, and the verification is
`verify-bar-table.py` beside it — an independent derivation from the same committed manifest,
written without reading G0's script, which prints its own figures next to G0's published ones and
exits non-zero on any disagreement.

**It agrees on every figure.** `python3 verify-bar-table.py ../../../../apps/reference-apple/fixtures/manifest.json`
exits 0 and prints `VERDICT: G0's bar table is confirmed on every figure.`

One derivation error was made and corrected on the way, and it is worth recording because it is the
trap this table is about. Grouping the publication events by their own `profiles` tuple — rather than
by the transitive closure of profiles that events link — splits the four single-profile events out
of the two pair groups they belong to, counts the same fixture in two groups, and reports 647 cells
with no attributable bar out of a bed of 619. The arithmetic only closes at the level of the closure,
which is exactly why the bar is not per-cell.

## What the bundle actually records

Three kinds of per-cell record, and only three:

| record | fixtures | what it gives |
| --- | ---: | --- |
| `stateFrequencies` | 103 | the **exact** run total for that cell, as the sum of each byte-state's `runs` |
| `recoveredProvenance` (`runsPerCell: 1`) | 121 | the 2026-08-30 tree re-adopted at one run — a bar of one, which is a bar |
| neither | 395 | nothing per cell |

**224 of 619 fixtures carry a per-cell bar. 395 do not.** The distinct exact bars seen across the
bed are **7 and 17**, and no other.

`bedProvenance` holds 13 publication events. An event records its profiles, its run count and
`cellsPublished` — **counts, not ids** — except `frequencySettledCells`, whose 91 named cells are
already inside the 103 above. So an unrecorded fixture can only inherit a bar from an event, and only
where that inheritance is unambiguous.

## Per profile

| profile | fixtures | exact bar | bars seen | recovered @1 | unrecorded |
| --- | ---: | ---: | --- | ---: | ---: |
| apple-macos-26.5-1x-dark-standard | 115 | 6 | 7, 17 | 14 | 95 |
| apple-macos-26.5-1x-light-increased-contrast | 32 | 0 | — | 10 | 22 |
| apple-macos-26.5-1x-light-reduced-transparency | 30 | 0 | — | 9 | 21 |
| apple-macos-26.5-1x-light-standard | 164 | 9 | 7, 17 | 37 | 118 |
| apple-macos-26.5-2x-dark-standard | 114 | 38 | 7, 17 | 14 | 62 |
| apple-macos-26.5-2x-light-standard | 164 | 50 | 7, 17 | 37 | 77 |

## The 13 publication events

| # | profiles | runs | cells published | frequency-settled cells named |
| ---: | --- | ---: | ---: | ---: |
| 0 | 2x-dark-standard + 2x-light-standard | 17 | 54 | 17 |
| 1 | 1x-light-reduced-transparency | 17 | 9 | 0 |
| 2 | 1x-light-increased-contrast | 17 | 10 | 0 |
| 3 | 2x-dark-standard + 2x-light-standard | 7 | 103 | 70 |
| 4 | 1x-dark-standard + 1x-light-standard | 7 | 104 | 3 |
| 5 | 2x-dark-standard + 2x-light-standard | 7 | 62 | 0 |
| 6 | 2x-light-standard | 7 | 4 | 1 |
| 7 | 1x-dark-standard + 1x-light-standard | 7 | 62 | 0 |
| 8 | 1x-light-standard | 7 | 4 | 0 |
| 9 | 1x-light-increased-contrast | 7 | 12 | 0 |
| 10 | 1x-light-reduced-transparency | 7 | 12 | 0 |
| 11 | 2x-dark-standard | 7 | 4 | 0 |
| 12 | 1x-dark-standard | 7 | 4 | 0 |

## Where the arithmetic closes, and where it does not

The unit is the **closure** of profiles that events link: an event records one `cellsPublished` for
every profile it names, so a pair event cannot be split between its two, and a profile named by both
a pair event and a single event ties the two together. `recoveredProvenance` cells are not subtracted
from what the events published — they were recovered from the 2026-08-30 tree, which predates every
event here — so the unrecorded cells an event accounts for are `cellsPublished − exact`.

| group | fixtures | exact | recovered | unrecorded | event runs | event cells published | verdict for the unrecorded |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| 1x-dark-standard + 1x-light-standard | 279 | 15 | 51 | 213 | 7 | 174 | 159 of 213 attributable at **7 as a group statement**; **54 short** |
| 2x-dark-standard + 2x-light-standard | 278 | 88 | 51 | 139 | 7, 17 | 227 | 139 of 139 covered, but at **two different bars** — nothing chooses |
| 1x-light-increased-contrast | 32 | 0 | 10 | 22 | 7, 17 | 22 | 22 of 22 covered, at **two different bars** |
| 1x-light-reduced-transparency | 30 | 0 | 9 | 21 | 7, 17 | 21 | 21 of 21 covered, at **two different bars** |

So of the 395 unrecorded fixtures:

- **159** are in the one group whose every event ran at seven, and can be attributed **7 runs as a
  group statement** — "this cell was published by one of the events that ran at seven", not "this
  cell was seen seven times", because the event does not name it.
- **54** are in that same group beyond what those events say they published at all: no event
  accounts for them and they carry no per-cell record. They have **no bar**.
- **182** are in the three groups whose events ran at both seven and seventeen. An unrecorded cell
  there could have come from either and the manifest offers nothing to choose. **No attributable
  bar.**

## Committed

**224 cells with a per-cell bar** (103 exact, 121 at one run); **159 attributable to seven only as a
group statement**; **236 with no attributable bar at all** — 38 % of the bed.

This is why clause 2 declares **one bar per pass** for the 27 bed rather than matching the 26.5 bar
per cell: for 38 % of the bed there is no 26.5 bar to match. It is also why clause 4 adopts **no 27
regression floor** in this wave — a floor needs the seventeen-run bar, and the 27 bed is captured at
seven.

## What this does not say

Nothing about whether a 26.5 cell is good evidence. A cell published unanimously at one run and a
cell that needed seventeen to settle are both in the bed and both were measured against; the bar is
about how much run-to-run variation the publication could see, not about the cell's correctness. It
also reads no row of `results/matrix.json` — the bar is a property of how a fixture was published,
and the matrix holds readings taken against fixtures.
