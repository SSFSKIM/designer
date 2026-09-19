# The macOS 27 sitting — 2026-09-18 and 2026-09-19

W29 acceptance clause 2; claims §5.150. Eight passes, seven runs each, **56 runs and 624 cells
per round**, all banked, **none quarantined**, every run printing `attested N N`.

The raw runs stay on the capture machine under `~/vitrea-w29-27-run/`, as a sitting's snapshots do.
Committed here: the driver logs (`logs/`), every run's opening and closing attestation
(`attest/`, 112 files), a distilled head-and-tail of each run's own output
(`logs/passes/`, 56 files), and `provenance.json` — each run directory, its manifest's SHA-256, its
cell count, its first and last `capturedAt`, and the digests of both its attestation reads.

## The passes, in the order they ran

| pass | runs | cells/run | started | finished | wall clock | rehearsal |
| --- | ---: | ---: | --- | --- | ---: | --- |
| standard × active × 2x | 7 | 162 | 2026-09-18 07:21:15Z | 10:22:48Z | 3 h 01 m | 07:03:32Z–07:21:15Z |
| standard × inactive × 2x | 7 | 119 | 10:35:49Z | 12:48:52Z | 2 h 13 m | 10:22:48Z–10:35:49Z |
| standard × active × 1x | 7 | 162 | 13:06:40Z | 16:07:10Z | 3 h 00 m | 12:48:57Z–13:06:40Z |
| standard × inactive × 1x | 7 | 119 | 16:20:11Z | 18:33:54Z | 2 h 14 m | 16:07:10Z–16:20:11Z |
| increased-contrast × active × 1x | 7 | 10 | 2026-09-19 00:01:30Z | 00:12:42Z | 11 m | 00:00:24Z–00:01:30Z |
| increased-contrast × inactive × 1x | 7 | 22 | 00:15:07Z | 00:39:52Z | 25 m | 00:12:42Z–00:15:07Z |
| reduced-transparency × active × 1x | 7 | 9 | 00:43:00Z | 00:53:04Z | 10 m | 00:42:01Z–00:43:00Z |
| reduced-transparency × inactive × 1x | 7 | 21 | 00:55:23Z | 01:19:04Z | 24 m | 00:53:04Z–00:55:23Z |

**The four standard passes: 07:03:32Z to 18:33:54Z on 2026-09-18, 11 h 30 m** including their four
rehearsals and the display switch. **The four accessibility passes: 23:59:41Z on 2026-09-18 to
01:19:04Z on 2026-09-19, 1 h 19 m.** Against `plan.md`'s 12.25 h at the bar the sitting came in at
**12 h 49 m** wall including every rehearsal — inside the plan's own 15.9–30.6 h attempt-loss band,
and near its floor, because the sitting lost almost nothing to retries.

Display: mode 68 for the two 2x passes, switched to **mode 69 at 12:48:57Z** and left there for all
six 1x passes, and returned to 68 after the sitting. Every run's attestation records the mode it ran
at and the mode its scale declared, and the two agree in all 56.

## What the machine attested, per pass

All 56 runs: macOS **27.0 build 26A428**, `NSGlassTintAmount` **0.5**, Show Borders
(`ButtonShapesEnabled`) **0**, the granted bundle `bd3092e8…` / cdhash `88cbbb5b…`, `LC_BUILD_VERSION`
`minos 26.0 sdk 26.0`, one canonical scene declaration (`c3d1badc…`) and one derived pass
specification (`afcc59c5…`). Not one closing read drifted from its opening read.

| passes | Reduce Transparency | Increase Contrast | displayplacer |
| --- | ---: | ---: | ---: |
| the four standard | 0 | 0 | 68 / 69 |
| the two increased-contrast | **0** | 1 | 69 |
| the two reduced-transparency | 1 | **0** | 69 |

## macOS 27 does not couple the two accessibility toggles

On macOS 26.5 turning on Increase Contrast force-enabled Reduce Transparency, and the transparency
checkbox could not be uncleared while contrast was on (user-verified 2026-08-29). The coupled state
was therefore the only reachable increased-contrast state, the 26.5 profile was captured in it, and
the harness records the coupling as a profile caveat whenever it observes it
(`main.swift`'s `couplingNote`).

**On 27 it is gone.** All seven increased-contrast runs attested `increaseContrast=1` with
`reduceTransparency=0`; the harness wrote **no coupling note in any of the 56 run manifests**; and
the reduced-transparency passes attested the mirror image. So the 27 increased-contrast bed is a
*different state* from the 26.5 bed of the same name — contrast without transparency reduction — and
a difference between the two on that profile is confounded with the decoupling until they are
separated.

Recorded as a caveat on the two 27 accessibility profile entries, **beside the 26.5 caveat and never
over it**: the 26.5 caveat is a true statement about the bed it describes and about the operating
system that bed was captured on. `add-a11y-caveat.py` is the edit, and the evidence under it is an
attestation rather than a note — `increaseContrast` and `reduceTransparency` are fields in each of
those runs' `attest.read`, and they are carried into the profile's `attestation` block in the
published manifest.

## Every retry, and every cell captured while the machine was in use

**One refusal in the whole sitting**, and it is the gate working. The increased-contrast rehearsal at
2026-09-18 23:59:41Z was refused: *"the machine has been idle 19.9s, under the 45.0s this run
requires, and a user-activity assertion is held"* — the operator's own hand on System Settings,
seconds earlier, flipping the toggle the pass needs. It presented 0 cells, the driver stopped on the
count rather than on the exit status, and the pass was restarted 43 s later and presented its 10.
Nothing was captured by the refused attempt. No other run needed a second attempt, and no run was
quarantined.

**Ten cells of 624 were captured under the 45 s idle bar**, in two runs. The harness gates idle once
at a run's opening and per cell records it without refusing, so a touch mid-run files the cell with
its `hidIdleSeconds` beside it and the pose attestation still decides whether it is evidence — all
ten attested `presentedActive`, `deterministic` and `materialRendered`. `idle-cells.md` is the full
table; the summary is that **nine of the ten were unanimous across all seven runs**, so the
disturbance moved nothing, and the tenth stood alone and was outvoted:

| pass | run | cell | idle | outcome |
| --- | ---: | --- | ---: | --- |
| increased-contrast × active × 1x | 4 | `checkerboard__capsule-button__rest` | 40.0 s | unanimous 7/7 |
| increased-contrast × active × 1x | 4 | `checkerboard__rrect-md__rest` | 20.9 s | unanimous 7/7 |
| increased-contrast × active × 1x | 4 | `hc-text__capsule-button__rest` | 11.4 s | unanimous 7/7 |
| increased-contrast × active × 1x | 4 | `photo__rrect-lg__rest` | 1.9 s | unanimous 7/7 |
| increased-contrast × active × 1x | 4 | `photo__toolbar-group__rest` | 30.4 s | unanimous 7/7 |
| standard × active × 2x | 6 | `2x-dark/checkerboard-32__capsule-button__rest` | 12.7 s | unanimous 7/7 |
| standard × active × 2x | 6 | `2x-dark/checkerboard-64__rrect-md__rest` | **3.1 s** | **alone; outvoted 6–1** |
| standard × active × 2x | 6 | `2x-dark/dark-solid__capsule-button__rest-tint-orange` | 22.1 s | unanimous 7/7 |
| standard × active × 2x | 6 | `2x-dark/photo__rrect-md__rest` | 41.2 s | unanimous 7/7 |
| standard × active × 2x | 6 | `2x-light/photo__glass-over-glass__rest` | 31.6 s | unanimous 7/7 |

This is the plurality earning its keep: the one cell the disturbance did move is the one cell the
other six runs overruled, and the bed published bytes no disturbed run produced.

## The publication

`materialize-27.sh`, one invocation per pass, seven runs each, `--frequency-settle`. Every pass
resolved; **no cell was refused and none was state-ambiguous**, so no `--omit` ruling was needed and
the bed has no holes.

| pass | cells | unanimous | voted | frequency-settled | refused |
| --- | ---: | ---: | ---: | ---: | ---: |
| standard × active × 2x | 162 | 128 | 31 | 3 | 0 |
| standard × inactive × 2x | 119 | 117 | 2 | 0 | 0 |
| standard × active × 1x | 162 | 139 | 17 | 6 | 0 |
| standard × inactive × 1x | 119 | 75 | 44 | 0 | 0 |
| increased-contrast × active × 1x | 10 | 9 | 1 | 0 | 0 |
| increased-contrast × inactive × 1x | 22 | 15 | 7 | 0 | 0 |
| reduced-transparency × active × 1x | 9 | 8 | 1 | 0 | 0 |
| reduced-transparency × inactive × 1x | 21 | 14 | 7 | 0 | 0 |
| **total** | **624** | **505** | **110** | **9** | **0** |

All nine frequency-settled cells are in the two **active** standard passes — six settled 6–1 and
three 5–2 — and each carries `frequencySettled` and its observed `stateFrequencies` in the manifest,
so a reader can see it was decided by counting rather than by agreement:

```
2x-dark  checkerboard-8__capsule-button__rest   6-1      1x-dark   checkerboard-lc16__rrect-lg__rest  6-1
2x-light hc-text__capsule-button__rest          6-1      1x-dark   hc-text-28__rrect-lg__rest         6-1
2x-light hc-text__rrect-lg__rest                5-2      1x-dark   hc-text__rrect-lg__rest            5-2
                                                         1x-dark   light-solid__rrect-lg__rest        5-2
                                                         1x-light  hc-text-28__rrect-lg__rest         6-1
                                                         1x-light  hc-text-7__rrect-lg__rest          6-1
```

Seven of the nine are `rrect-lg`, the largest radius the declaration carries, and six sit over an
`hc-text` backdrop. That is **not** where the 26.5 bed's bistable cells sat: of its 103
frequency-settled cells, 38 are `capsule-button` and the backdrops lead with `checkerboard-4` (13),
`checkerboard` (11) and `dark-solid` (11), with `hc-text` nowhere near the top. Recorded as an
observation and nothing more — the two beds were also settled at different bars (17 runs for much of
26.5, 7 here), so the populations are not comparable as they stand, and which cells are bistable and
why is a reading. Readings are G2's. At seven runs
the bed's own provenance records **72.2 % confidence at a one-in-six minority** — the probe bar, not
the freeze bar, which is why clause 4 adopts no 27 regression floor.

## Counts, against 26.5

`bed-counts.py`; the table is `bed-counts.txt`.

| 27 profile | declared | filed | 26.5 holds | shortfall | only on 27 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 1x-dark-standard | 117 | 117 | 115 | 0 | 2 |
| 1x-light-increased-contrast | 32 | 32 | 32 | 0 | 0 |
| 1x-light-reduced-transparency | 30 | 30 | 30 | 0 | 0 |
| 1x-light-standard | 164 | 164 | 164 | 0 | 0 |
| 2x-dark-standard | 117 | 117 | 114 | 0 | 3 |
| 2x-light-standard | 164 | 164 | 164 | 0 | 0 |
| **total** | **624** | **624** | **619** | **0** | **5** |

**No shortfall.** Every profile filed exactly what the declaration asked for, and the 27 bed is five
cells larger than the 26.5 bed rather than smaller. The five are precisely the ones G0's `plan.md`
named in advance as declared-but-never-published on 26.5 — so the 27 sitting filled all five holes
the 26.5 bed has:

```
1x-dark-standard/light-solid__capsule-button__inactive
1x-dark-standard/photo__glass-over-glass__inactive
2x-dark-standard/checkerboard-8__capsule-button__rest
2x-dark-standard/light-solid__capsule-button__inactive
2x-dark-standard/photo__glass-over-glass__inactive
```

A 27 cell with no 26.5 counterpart is a cell **G2 reports rather than diffs**. The first of them,
`light-solid__capsule-button__inactive` on both dark profiles, is the scene claims §5.148 §1 found
the 26.5 publishing run passing over with no committed native fixture; on 27 it is captured.

`bed-counts.py` also checks what a count cannot: every PNG on disk has a manifest entry, every entry
has a PNG, and every entry's `file` field points at the bytes beside it. **624 of 624, both
directions, zero problems.**

## The backdrops did not move

All 32 background ids the 27 runs composited over are **byte-identical** to the rasters the 26.5
bundle indexes — 896 comparisons across the 56 runs, zero disagreements
(`check-backgrounds` in §5.150). The harness draws them with its own CoreGraphics generators and
nothing guaranteed macOS 27 would rasterise them identically, so this was a real risk to the
publication and is now a real finding: G2 reads 27 against 26.5 over the *same backdrop bytes* on
both sides, which is one confound it does not have to carry.

## What is not here

No read of any 27 fixture against vitrea — that is G2, and clause 2 forbids it in this child. No
material, no profile document, no bound, no floor, and no row in `results/matrix.json`. The sitting's
raw PNGs stay on the machine.
