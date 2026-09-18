# The 26.5 bar per cell — what the committed manifest can attribute, and what it cannot

W29 clause 2 asks G1 to commit "a table of the 26.5 bar per cell where the manifest's
`bedProvenance` can attribute it … and names the cells it cannot attribute as such". This is that
table, derived rather than asserted: `bar-table.py` and `bar-groups.py` read
`apps/reference-apple/fixtures/manifest.json` and print what is below. Nothing under `fixtures/`
was written.

## What the bundle actually records

Three kinds of record, and only three (`probe-manifest-fields.py` prints the key sets):

| record | fixtures | what it gives |
| --- | ---: | --- |
| `stateFrequencies` (with `frequencySettled`) | 103 | the **exact** run total for that cell, as the sum of each byte-state's `runs` |
| `recoveredProvenance` | 121 | `runsPerCell: 1` — the 2026-08-30 tree re-adopted at one run, which is a bar of one and not no bar |
| neither | 395 | nothing per cell |

**224 of 619 fixtures carry a per-cell bar. 395 do not.**

`bedProvenance` has 13 publication events. An event records its profiles, its run count and
`cellsPublished` — **counts, not ids**, except `frequencySettledCells`, which are the 91 that are
already in the 103 above. So an unrecorded fixture can only inherit a bar from an event, and only
when that inheritance is unambiguous.

## Per profile

| profile | fixtures | exact bar | bars seen | recovered @1 | unrecorded | event run counts | event cells published |
| --- | ---: | ---: | --- | ---: | ---: | --- | ---: |
| apple-macos-26.5-1x-dark-standard | 115 | 6 | 7, 17 | 14 | 95 | 7 | 170 |
| apple-macos-26.5-1x-light-increased-contrast | 32 | 0 | — | 10 | 22 | 7, 17 | 22 |
| apple-macos-26.5-1x-light-reduced-transparency | 30 | 0 | — | 9 | 21 | 7, 17 | 21 |
| apple-macos-26.5-1x-light-standard | 164 | 9 | 7, 17 | 37 | 118 | 7 | 170 |
| apple-macos-26.5-2x-dark-standard | 114 | 38 | 7, 17 | 14 | 62 | 7, 17 | 223 |
| apple-macos-26.5-2x-light-standard | 164 | 50 | 7, 17 | 37 | 77 | 7, 17 | 223 |

"bars seen" is the set of distinct exact run totals among that profile's `stateFrequencies` cells,
so a profile reading "7, 17" holds cells published at both bars. The `event cells published` column
sums the events touching the profile; an event naming two profiles reports one figure across both,
which is why the arithmetic that decides attributability is at the group's level.

## Where the arithmetic closes, and where it does not

Events name profiles in groups. `bar-groups.py`:

| group | fixtures | exact | recovered | unrecorded | event run counts | event cells published | unrecorded cells the events could cover |
| --- | ---: | ---: | ---: | ---: | --- | ---: | --- |
| 1x-dark-standard + 1x-light-standard | 279 | 15 | 51 | 213 | 7 | 174 | 159 of 213 — **54 short** |
| 2x-dark-standard + 2x-light-standard | 278 | 88 | 51 | 139 | 7, 17 | 227 | 139 of 139, but at **two different bars** |
| 1x-light-increased-contrast | 32 | 0 | 10 | 22 | 7, 17 | 22 | 22 of 22, at **two different bars** |
| 1x-light-reduced-transparency | 30 | 0 | 9 | 21 | 7, 17 | 21 | 21 of 21, at **two different bars** |

So of the 395 unrecorded fixtures:

- **159** are in the one group whose events all ran at seven, and can be attributed **7 runs as a
  group statement** — "this cell was published by one of the events that ran at seven", not "this
  cell was seen seven times", because the event does not name it.
- **54** are in that same group beyond what those events say they published at all: no event
  accounts for them, and they carry no per-cell record. They have **no bar**.
- **182** are in the three groups whose events ran at both seven and seventeen. An unrecorded cell
  there could have come from either, and the manifest offers nothing to choose. They have **no
  attributable bar**.

**Committed for G1:** 224 cells with a per-cell bar (103 exact, 121 at one run); 159 attributable
to seven only as a group; **236 with no attributable bar at all**. This is why clause 2 declares
one bar per pass for the 27 bed rather than matching the 26.5 bar per cell — there is no per-cell
26.5 bar to match for 38 % of the bed.

## What this does not say

It says nothing about whether a 26.5 cell is good evidence. A cell published unanimously at one run
and a cell that needed seventeen to settle are both in the bed and both were measured against; the
bar is about how much run-to-run variation the publication could see, not about the cell's
correctness. It also does not read `results/matrix.json` — the bar is a property of how a fixture
was published, and the matrix holds readings taken against fixtures.
