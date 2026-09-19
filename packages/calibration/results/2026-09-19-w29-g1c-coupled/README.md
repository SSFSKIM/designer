# W29 G1c — the coupled increased-contrast bed

**Decision Log 4 (b); claims §5.152.** Part A built the key, the declaration, the pass and the
refusals and **captured nothing**. **Part B is closed**: the bed is published, its bar was declared
and committed before a 26.5 pair was read, and the reading is §5.152 §B — *the material moved on
every one of the 32 cells and the geometry did not*, with the decoupling's share of §5.151 §9
measured for the first time. A bound is drafted for the user as the charter's Decision Log 5.

## What this child is for

macOS 26.5 force-coupled the two accessibility toggles: Increase Contrast enabled Reduce
transparency and the transparency checkbox could not be uncleared while contrast was on, so the
coupled state was the **only** increased-contrast state a machine could be in and
`apple-macos-26.5-1x-light-increased-contrast` is that state. macOS 27 made them independent, so the
first sitting's `apple-macos-27.0-1x-light-increased-contrast-glass0.5` is contrast **alone** — all
seven of its runs attested `increaseContrast=1` with `reduceTransparency=0` (§5.150 Part B §3). Two
states under one name: every difference G2 measured on that profile is confounded with the
decoupling, and §5.151 §9 refuses to read any of it as a statement about the material.

This child captures the missing half. One new profile,
`apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5`, the 26.5 increased-contrast scene
list verbatim — 32 cells, 10 active and 22 receded — at 1x in both poses at the seven-run bar, with
**Increase Contrast and Reduce transparency both on**. Read against the 26.5 bed it is the
like-for-like comparison the decoupled capture cannot give.

## The key, and why the granted bundle takes it without a rebuild

The a11y token is `increased-contrast-coupled`, and it names a **machine state** rather than a macOS
setting: both toggles on. `PROFILE_KEY_PATTERN` gains it as a fourth mode beside `standard`,
`reduced-transparency` and `increased-contrast`; every existing key parses exactly as before, which
`profile-key.test.ts` asserts in both directions (the longer alternative must not swallow the
shorter, and the shorter must not match a prefix of the longer). `-coupled` is part of one mode token
and not a modifier the grammar composes: no other mode may wear it.

The declaration is the interesting half. The harness selects a profile by comparing its declared
`a11y` field against `SystemAccessibility.current`, which answers *is contrast on* — it returns
`increased-contrast` in both states and cannot see the second toggle, and teaching it to would be a
rebuild of the bundle that holds the wave's one Screen Recording grant (X4). So the entry declares
**`a11y: "increased-contrast"`**, which the bundle already knows, and the **key** carries the state.
The two deliberately differ, and the entry's own comment says so.

That leaves the question the design turns on: with two profiles declaring the same `a11y`, what
stops one pass capturing both? Three things, in the order they act.

1. **The derived specification carries exactly one contrast profile.** `pass-spec.py` builds the
   pass's declaration by filling one contrast slot from the pass's own mode — `decoupled` by default,
   which is what the first sitting's six passes still derive. The bundle is never offered both, so
   this is structural rather than advisory.
2. **The pass refuses the other state.** `run-sitting-27.sh` reads both toggles and refuses unless
   they read the way the pass's mode declares. The plain contrast pass now refuses a **coupled**
   machine — new, and the mirror of the coupled pass refusing a decoupled one — because a run in the
   wrong state filed under either key is exactly the confound this child exists to remove.
3. **`materialize` refuses before it opens a PNG.** `src/run-provenance.ts` judges the key against
   the two attested booleans. A manifest cannot make this judgement: its `a11yMode` is
   `SystemAccessibility.current` and reads `increased-contrast` in both states, so the attestation is
   the only place the two are separable. The rule asks nothing of the 26.5 bed, which carries no
   attestation and wears the plain token for the state its OS forced.

## What was rehearsed, and what could not be

`rehearsal.txt` is the record; `rehearse-coupled.sh` produced it. **The machine is IC=0, RT=0 and
this child has no hands in System Settings**, so the pass cannot be rehearsed end to end from here.
What was proved:

- Both derivations, from the real canonical declaration: each carries exactly one contrast profile,
  each would present **10** active and **22** receded cells, and the two id lists are identical —
  the coupled profile declares the 26.5 list verbatim, so what differs between the passes is the
  profile, the key and the state.
- Every refusal fires from the machine's real state: the coupled pass in both poses (the machine is
  `standard`), the plain contrast pass (same), and the coupled pass at 2x, refused in `pass-spec.py`
  before the bundle is launched because no profile declares it — the coupled profile is 1x light, as
  its 26.5 counterpart is.
- **The granted bundle reads the version-7 declaration unrebuilt.** Handed the coupled
  specification — the one holding the new key — it resolved the backgrounds and presented its cells
  dry. A profile entry that broke the decode would have presented none.
- `run-sitting-27.test.sh`, 36 rows against a stubbed machine, covers the half a correctly
  configured machine cannot reach: each contrast pass refusing the other's state, each being offered
  exactly one contrast profile, and a run that filed under the other contrast key being quarantined.

What is **not** rehearsable without the toggles is the count under the coupled key itself. That is
the first line of each pass command below, and the RUNBOOK's standing rule applies: read the count,
not the verdict.

## The two passes

`RUNBOOK.md` §3b in `../2026-09-18-w29-g1-bed/` is the operator's document and carries the full
pre-flight. The commands:

```bash
# Increase contrast ON *and* Reduce transparency ON — macOS 27 does not set the
# second for you, which is the whole reason this pass exists.
defaults read com.apple.universalaccess increaseContrast      # must read 1
defaults read com.apple.universalaccess reduceTransparency    # must read 1
displayplacer "id:7709FD0F-F423-4277-B0C8-7CA94F85723A res:2560x1440 hz:60 color_depth:4 \
  enabled:true origin:(0,0) degree:0 mode:69"
displayplacer list | grep 'current mode'                      # must read: mode 69

R=<repo>/packages/calibration/results/2026-09-18-w29-g1-bed
export VITREA_SCENES=<repo>/apps/reference-apple/scenes.json  # version 7

DRY=1 $R/run-sitting-27.sh active   1 increased-contrast-coupled   # must print: cells presented: 10
$R/run-sitting-27.sh active   1 increased-contrast-coupled         # ~11 min at the bar
DRY=1 $R/run-sitting-27.sh inactive 1 increased-contrast-coupled   # must print: cells presented: 22
$R/run-sitting-27.sh inactive 1 increased-contrast-coupled         # ~25 min at the bar

# Toggles back off, display back to 2x.
displayplacer "id:7709FD0F-F423-4277-B0C8-7CA94F85723A res:2560x1440 hz:60 color_depth:4 \
  enabled:true origin:(0,0) degree:0 mode:68"
```

The wall clock is the first sitting's own for the same cells: 11 min and 25 min at the seven-run bar
(`../2026-09-18-w29-g1-bed/sitting.md`). The runs land in
`$HOME/vitrea-w29-27-run/increased-contrast-coupled-{active,inactive}-1x/run-N`, beside the first
sitting's and touching none of it.

## Part B, as it ran

**Published.** `materialize-coupled.sh --apply`, two passes at seven runs each: **32 cells, 28
unanimous, 4 voted, 0 frequency-settled, 0 refused**, no omission and no hole (`materialize.txt`).
`src/run-provenance.ts` did not fire — the runs and the key agree about both toggles, which is Part
A's refusal in its positive form. The profile's `attestation` block carries every field all fourteen
runs agree on, including `increaseContrast=1`, `reduceTransparency=1`, `showBorders=0` and
`glassTintAmount=0.5`.

**The caveats** (`add-coupled-caveat.py`, `caveat.txt`) are added beside and never over. The harness
wrote its own coupling note on all seven runs of both passes — the attestation the capture made —
and its wording is a statement about macOS 26.5, where the toggles were coupled. It stays verbatim;
the caveat beside it names the state, the attested values, why the profile exists, and the one thing
that note gets wrong on 27. The decoupled profile gains a pointer to where the unconfounded reading
lives, and its own caveat is untouched.

**The bar** (`bar-declaration.md`, `delta/noise-bar.json`, `bar-run.txt`) was committed in
`848713cf`, which precedes the commit that read a 26.5 pair. G2's instrument, construction and rule
are unchanged; the one thing declared here is that the zero-spread fallback is the minimum over the
27 **bed** and not over this 32-cell pass, read from G2's committed figures through
`--fallback-bar`. On 32 of 32 metrics it then equals the 624-cell bed's.

**The read** (`delta-run.txt`, `delta/`, `read-checks.txt`): 32 pair rows, 10 recede rows, **0 cells
unbarred**, 115 of 115 measurable recede readings barred. Per law — the material moved on the
interior level, the tone response, the scatter, the rim, the highlight and the tint's lightness, on
every cell that carries them; the silhouette, the corner and the tint's hue did not. The rim is the
law that moved most: the 26.5 material's crisp dark outline is gone on 27.

**What the second sitting bought.** The two 27 contrast profiles declare the same 32 cells over one
26.5 counterpart, so their rows differ in exactly one thing. The rim and the scatter moved by the
same amount in both states, to within 1 % — they are the material. The level, the tone offset and
the tint's lightness read two to five times larger on the decoupled profile — they are mostly the
toggle. `sheets/three-way__*.png` is that sentence as a picture: 26.5 opaque with an outline, 27
coupled opaque without one, 27 decoupled plainly translucent.

**A bound is drafted**, not adopted (charter Decision Log 5; §5.152 §B §11). Every material row of
the native-to-native distribution is inside the 26.5 increased-contrast allowance at its worst cell,
which is true of no profile in Decision Log 4 (c) — including the decoupled profile of nearly this
name, whose ΔE p95 the confound put over. The two things the user should weigh are in the draft.

**The review closure** (2026-09-19, `review-closure.py` / `.txt`; claims §5.152 §B §12). Six
findings, none flipping a verdict, and Decision Log 5's ruling unchanged. Under all of them: the
26.5 allowance column was transcribed by hand and four of its forty-eight texture rows were wrong,
so the allowances are now parsed from `adopted-thresholds.test.ts` through
`../2026-09-19-w29-g2-native-delta/adopted_allowances.py`, which both closures import. Two
statements above are amended by it — the SSIM-outside worst cell is **inside** its allowance
(0.237 against ≤ 0.31, not the transcribed ≤ 0.20), so there is no tail to carry as a named risk;
and "true of no profile" is **true of one other**, `1x-light-reduced-transparency`, whose own
SSIM-outside allowance was mis-transcribed the other way. The four other findings condition the tone
response on `transferR2`, separate the transfer offset from the body level (r = 0.9985), name the
two median conventions that make `law-tables.txt` and `read-checks.txt` disagree on `rrect-ml`
without either being wrong, and name the attested field as `showBorders`.

## Files

| file | what it is |
| --- | --- |
| **Part A** | |
| `rehearsal.txt` | the rehearsal record, on the machine, with the toggles off |
| `rehearse-coupled.sh` | what produced it; re-runnable, captures nothing |
| `run-sitting-27.test.txt` | the stubbed-machine test's 36 rows as they ran |
| **Part B** | |
| `materialize-coupled.sh`, `materialize.txt` | the publication, two passes at seven runs each |
| `add-coupled-caveat.py`, `caveat.txt` | the state-naming caveat and the decoupled profile's pointer, added beside what was already there |
| `bar-declaration.md` | the bar's construction and the one thing a 32-cell bed changes about the rule — **committed before any 26.5 pair was read** |
| `delta/noise-bar.json`, `bar-run.txt` | the per-cell 27-against-27 distribution the verdicts are stated against |
| `delta/native-delta.json`, `delta/recede-delta.json`, `delta-run.txt` | the rows |
| `delta/law-tables.txt` | the tables every verdict in §5.152 §B is read off |
| `read-checks.py` / `.txt` | the nine things a table cannot answer, including the coupled-against-decoupled comparison and the fallback's own alternative |
| `review-closure.py` / `.txt` | the independent review's six findings, recomputed from the committed rows; the allowances parsed from the test file, never transcribed |
| `delta/sheets/` | 26.5 \| 27 coupled \| amplified difference (×8), four per profile and three per law |
| `sheets/`, `three-way-sheet.py` | 26.5 \| 27 coupled \| 27 decoupled on one strip — the material and the toggle separated by eye |
| `verify-output.txt`, `freeze-verify.txt` | lint, the workspace's tests, and the 26.5 freeze at 1,818 entries |

The instruments themselves stay where the bed's instruments live —
`../2026-09-18-w29-g1-bed/pass-spec.py`, `run-sitting-27.sh`, `run-sitting-27.test.sh` and
`RUNBOOK.md` — because a second copy of a 450-line capture script is how two passes of one bed stop
agreeing. Their G1 records (`commands.txt`, `sitting.md`, the attestations, the counts) are that
child's evidence and are untouched.
