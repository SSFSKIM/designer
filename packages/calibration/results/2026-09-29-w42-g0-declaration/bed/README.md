# W42 G0 — the capture bed, its split, the web plan, the sitting and the one-exposure runner

The bed stream of W42 G0 (charter `docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md`
v2.1, main `0736ed64`; clauses 1, 4, 5, 8 and 11; ledger §5.194). It declares the bed and builds
the tooling that captures, archives and exposes it. **No native pixel of the new bed exists**: the
only launches of the side bundle here are `backgrounds` and `self-check` (no window) and
`dump-layers` (a window, no ScreenCaptureKit, no grant). The canonical
`apps/reference-apple/scenes.json` is untouched.

| file | what it is |
| --- | --- |
| `declare-bed.py` | reproduces the three declaration files below from its tables; never tune after capture |
| `scenes-w42-body.json` | the wave-local scenes file the W39 side bundle reads through `VITREA_SCENES`, with the split in its own `split` |
| `bed.json` | the companion: per pass every cell (family, role, geometry), the run-1 references, the sentinels, the dump list, the U-items, the validation axes, the charter deviations, the counts |
| `twin-audit.json` | every glass cell against the canonical, W34 and W39 beds (declaration files only) |
| `pins.json` | SHA-256 of the three files above |
| `verify-backgrounds.py`, `side-check/` | the side bundle's `backgrounds` / `self-check` over the bed, read back independently |
| `dumps/` | `dumpcheck.py` (memo D's configuration as a checker), its reference and self-test, the s = 112 acceptance dumps |
| `wave.py`, `web-plan.json` | the W42 boundary (reader, launcher, receipt reuse) and the W42 web plan |
| `runtime-base-sample.py`, `.json` | clause 8's declared canonical sample |
| `sitting/` | the sitting script, archive assembly and their proofs |
| `exposure/` | the one-exposure runner and its synthetic proof |

## The bed

Four passes per scale (scheme × pose): the charter's counts, plus the s = 32 receded rows the
parent ruled from the gate rehearsal (below), 4 per 2x receded pass and 1 per 1x receded pass:

| pass | glass cells | A | B | B′ | C | D | E | F | H | run-1 references |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2x light active | 88 | 30 | 8 | 10 | 13 | 11 | 4 | 4 | 8 | 54 |
| 2x light receded | 90 (86 + 4) | 30 | 8 | 9 | 14 | 13 | 4 | 4 | 8 | 56 |
| 2x dark active | 91 | 33 | 8 | 10 | 13 | 11 | 4 | 4 | 8 | 54 |
| 2x dark receded | 93 (89 + 4) | 33 | 8 | 9 | 14 | 13 | 4 | 4 | 8 | 56 |
| 1x active, each | 15 | 2 | — | 7 | 1 | 1 | — | 2 | 2 | 10 |
| 1x receded, each | 16 (15 + 1) | 2 | — | 8 | 1 | 1 | — | 2 | 2 | 10 |

424 glass cells in all (362 at 2x, 62 at 1x), 260 run-1 no-glass references (the charter's
model assumed 174 + 40 = 214; the C and D families' positions and polarities need more distinct
backdrops than it counted), 337 scene entries, 61 backgrounds, 17 glass components. Every id,
level, pitch, offset and depth is in `bed.json` `cells`; the conventions:

- **Ids.** `<family>-<what>-<shape>`, scene ids `…__rest` (active) and `…__inactive` (receded).
  A scale-specific cell carries its own id (`a-g128-rrect-md-1x`), because the split is per id.
- **Placement is `offset`, never `position`.** Both sides honour an integer `offset` identically
  (`SceneSpec.swift` `frame(in:)`; `component-region.ts` `place()`), so every glass cell is
  web-plannable. An integer offset is an integer device-pixel translation at 1x and 2x.
- **Where an impulse lands.** `Backgrounds.swift` fills impulses and checker cells in
  CoreGraphics space, whose origin is the **bottom**-left: a single impulse of spacing g ≥ 214
  sits at (g/2, 200 − g/2) in image coordinates (verified on the canonical `impulse@1x.png`,
  rows 38–41 / 102–105 / 166–169). The shape is moved onto it by an offset that keeps the
  active capture footprint (box + 0.35 s or 16 pt, memo D §3) inside the canvas on rrect-md and
  the capsule; that is why the off-centre patches sit toward the TOP edge. rrect-lg's footprint
  exceeds the canvas at any placement, as on the canonical bed; its two single patches take the
  spacing (300, 336) that maximises the box's least clearance to the canvas edge (10 and 12 px;
  the canonical rrect-lg has 20).
- **Levels.** A: neutral greys. B: P2 48/208, P3 96/160, P4 16/112, P5 144/240. B′: P1 0/255.
  C, D and H's patch and step: 48/208 (P2's pair; uncensored in every endpoint's uniform
  response). E: Rec.709 luma on codes 128 (memo A's luma), found by exhaustive integer search:
  `rg` (202,106,128)/(54,150,128) at 127.998/128.002, `by` (121,122,208)/(135,134,48) at
  127.997/128.003. H: P1 0/255 at pitch 24, P6 32/176, P3, 128/229, greys 184 and 232.
- **C's depth sweep** is S 8 in the polarity whose detail PASSES the knee: bright on dark in the
  light passes (Lighten), dark on bright in the dark passes (Darken). rrect-md: centre (depth
  48, the main S 8 cell), 24 (s/4) and 4 pt from the edge; rrect-lg: 80, 40 and 4 pt. Receded,
  the same cells are the flat-in-depth falsification control.
- **D's steps** are `split` backgrounds at x = 160 + δ under the centred shape: δ 0, 32 (and 12
  receded) on rrect-md, δ 0 (and 12 receded) on the capsule, 8 and 16 CSS px outside rrect-md's
  right edge (x 248, 256), δ 0 under rrect-lg (active). `lohi` is 48 left of the step and 208
  right; `hilo` the reverse.
- **1x** follows the charter's criteria table; the fine-pitch, rrect-lg and edge cells share ids
  with their 2x twins where both exist.
- **Dump twins.** `dump-layers` refuses any non-`rest` id in either pose, so each receded-only
  cell (D's δ 12 rows) has a `$dumpOnly` rest twin captured in no pass; memo D dumped receded
  endpoints through rest ids the same way.

### The split, in the scenes file (clause 1)

`split.calibration` (fit support), `split.validation` (read-only transfer), `split.holdout` (H),
`split.probe` (family F's four bridges, read only to tie the repeat bar across sittings, not under
clause 6, plus the references whose only dependents are bridges), `recorded` empty. A reference
takes the lowest rank among its dependents (calibration/probe < validation < holdout). Per 2x
pass: 66–70 calibration, 10 validation active and 11 receded, 8 H, 4 F; per 1x pass 9 (active)
or 10 (receded) / 2 / 2 / 2.

Validation cells are transfer axes that calibration does not contain, each a cell nothing read
before (the twin audit):

| family | validation | axis |
| --- | --- | --- |
| A | rrect-64 × {160, 208, 255}; 1x greys 128 and 255 on rrect-md | the t = 0 stratum (capsule → rrect-64); scale (T at 2x predicts 1x) |
| B | P3 at pitch 16 and 64 | the level pair (contrast 64 at mean 128) |
| B′ | P1 pitch 32 on rrect-80 | span t = 1/6, between the knot (64) and rrect-md (96) |
| C | S 8 at s/4 on rrect-md and on rrect-lg | depth, between the centre and 4 pt |
| D | the step at δ 0 under the capsule, and under rrect-sm (receded) | span (96 → 44, and below 44: 32) |
| E | `by` at pitch 64 | hue |

**H** (holdout, 8 per 2x pass, 6 structured; 2 per 1x pass): P1 pitch 24 on **rrect-112**
(s = 112, t = 0.5, the unseen span; 196 × 112, radius 23.6, holding the probe shapes' aspect
1.75 and radius fraction 0.211), P6 pitch 32 on rrect-md, the step at δ 20, the patch S 24, P3
pitch 64 on rrect-lg, 128/229 pitch 64 on the capsule, greys 184 and 232 on rrect-md; at 1x the
P3 rrect-lg cell and grey 232.

**The twin audit** (`twin-audit.json`): no bed cell twins a canonical holdout scene; no
validation or H cell twins any canonical, W34 or W39 scene (relative geometry and backdrop
declaration, placement ignored conservatively as W39 did); every F bridge twins its canonical
scene. The odd-offset 1x cell twins the canonical probe `checkerboard-4__capsule-button` under
that rule and is calibration for that reason.

### Where the charter could not be followed as written

1. **The 1x "P1 at pitch 16 on rrect-lg" is a canonical holdout twin** (`checkerboard__rrect-lg`,
   holdout in both poses). Capturing and fitting it would read the canonical holdout's geometry
   before G3 (clause 14). Declared instead: P1 pitch 32 on rrect-lg at 1x
   (`bp-p1-c32-rrect-lg`, a probe twin, admissible calibration under X34), which pairs 1x with
   the 2x B′ cell of the same id; the count stays 15. **Substituted and flagged for the
   parent's ruling.**
2. **C's "S 8 at the centre of rrect-lg" cannot be a single square.** A single impulse lies at
   (g/2, 200 − g/2) with g/2 ≥ 107; rrect-lg's centre must lie in [140, 180] × [80, 120] for its
   box to stay inside the canvas, so x = g/2 ≥ 140 forces y ≤ 60. Declared as the 64-pt grid
   (the canonical impulse's spacing) with rrect-lg offset (0, +4): one patch exactly at the
   centre, the nearest others 64 pt away, about 4 σw at memo E's 16–17 pt.
3. **The active 4-pt cells sit inside the declared inner-refraction band** (height
   min(s/4, 20) = 20 pt on rrect-md and rrect-lg, memo D §3), which LT does not model (memo E
   §5). The cells stand as the charter lists them; the instrument must model or exclude
   refraction there. Receded is unaffected (refraction opacity 0).

## Checked against the side bundle, without capturing (`side-check/`)

The side bundle `~/vitrea-w39/side/VitreaReference.app` (`dev.vitrea.reference-apple.w39`, binary
`02052b17…`, cdhash `be258cbf…`, both matching W39's pin; build inputs byte-identical to HEAD's
`apps/reference-apple/Sources`), used with no rebuild:

- `backgrounds` at 1x and 2x loads and validates the whole scenes file (every scene in a split
  role, every background kind, every component including rrect-112 and the offset shapes) and
  writes all 61 backgrounds, each byte-stable, at both scales.
- `verify-backgrounds.py` re-renders every solid, checkerboard, impulse and split independently
  (120 of 122 rasters, byte-identical), requires the 14 rasters whose declaration equals a
  canonical one (the bridges' checker-16, checker-64, impulse and photo, and the P1 pitch
  ladder) to decode byte-identically to the canonical fixture rasters, and reads every declared
  patch (count, size, centre, depth) and step column back from the pixels: no discrepancy.
- `self-check`: 82 ok, 0 FAIL.

## The s = 112 component (`dumps/`)

`dumpcheck.py` is memo D's configuration as a checker: every field memo D read constant within an
endpoint and scale (`dump-reference.json`, derived from memo D's 208 single-shape surfaces), its
span laws (the seventeen of `laws.py` plus the dark MaxLumaSDR, the fill spread, the smoothness,
the element's ovalisation and the receded SDF maximum), the backdrop scale and margin, and the
pose. Its self-test passes memo D's own dumps (both scales, the settle-16 repeats) with no
departure and catches all six seeded mutations (`selftest.json`).

**Accepted.** The side bundle loads rrect-112 from the wave-local file with no rebuild, and
`dump-layers` over one scene per glass component of the bed (15, H's rrect-112 first) in all
four endpoints at 2x departs from memo D's configuration nowhere (`s112/`). rrect-112 reads
exactly memo D's law at t = 0.5: active blur opacity 0.4 at the centre (d0 = −56) and 0.2 at
1 pt inside the edge, receded 0.6 flat; the fill 8 at Lighten 0.9 (light) with Normal 0.5;
backdrop scale 0.5; margin 39.2 active and 0.5 (one device pixel) receded; the pose attested in
every dump (key and active, or neither). Its active SDF output maximum (19.56 light, 21.16 dark,
between span 96's and 128's) has no closed form in memo D and is recorded as a reading, not a
check. **H keeps s = 112, and its span is unseen in calibration.**

The four launches (`run-s112-check.sh`, 126–131 s each at settle 8) waited on memo D's idle gate
(`gate.sh`: ≥ 60 s HID idle, unlocked, no prompt on screen) and passed memo D's opening and
closing gate (slider 0.5, Reduce Transparency, Increase Contrast and Show Borders 0, mode 68, the
binary pin). The by-name foreign census read 13–15 processes (a Google Chrome session and
another stream's tooling), recorded and not enforced for these no-pixel dumps, whose own pose
attestation is what a stolen activation would break. The sitting enforces it (clause 4). The
rrect-112 dump JSON, the check reports and the attestations are committed under `s112/`; the
other dumps stay in scratch, hashed in `s112/scratch-sha256.txt`.

## The s = 32 receded rows (the parent's ruling from the gate rehearsal)

M2 on light-receded rrect-sm 2x (s = 32) failed in the gate rehearsal across every declared
rival, support, floor and k pair, and the bed held no structured receded cell below s = 44, so
nothing could identify the law at that size. Added on the canonical rrect-sm (64 × 32, r 8) in
both receded passes at 2x: P1 at pitch 8 (`bp-p1-c8-rrect-sm`, also in both receded 1x passes)
and 16 (`bp-p1-c16-rrect-sm`), the S 8 centre patch in the scheme's passing polarity
(`c-s8-hi-rrect-sm` light, `c-s8-lo-rrect-sm` dark; rrect-sm offset (−44, −16) onto the single
impulse at (116, 84), depth 16), and one step at δ 0 (`d-d0-lohi-rrect-sm`, the split at x 160).
The two P1 cells twin canonical rrect-sm scenes grounding read (`checkerboard-8__rrect-sm`
probe, `checkerboard__rrect-sm` calibration), so they are calibration; the step is
**validation**, extending D's span-transfer axis below 44 (96 → 44 → 32); the patch is
calibration, C's support at the new span. The twin audit now also refuses a twin of a
canonical `recorded` scene in a state the bed captures (the recorded set is the pressed poses;
the bridges' pressed matches are reported): none. The backgrounds, raster read-back and
self-check were rerun on the regenerated file with no discrepancy, and `dump-layers` over the
rows' two rrect-sm shapes in the receded pose, one launch per scheme behind memo D's idle gate,
departs from memo D's configuration nowhere (`dumps/s32/`): opacity 0.4 flat (t = 0), fill 8,
backdrop scale 0.5, margin 0.5 (one device pixel), not key and not active. The census read 33
foreign processes (other streams' tooling), recorded as before.

## The W42 web plan (`wave.py plan` → `web-plan.json`)

Derived from what the calibration page can pose: `web/scene.ts` composites any background as the
fixture raster and poses `inactive` through the runtime; `web/scenes.ts` places shapes through
`component-region.ts`, a lone capsule or rrect centred with `Math.round` plus `offset`
(`position` is ignored, `none` and opaque controls are native-only). A glass cell is
web-plannable iff its native frame equals that web frame. **All 424 glass cells are
web-plannable** (A 134, B 32, B′ 68, C 58, D 52, E 16, F 24, H 40 across the eight passes), so
every H cell has a rendered prediction and none referees the numerical structure only. No smoke
render was needed: code reading decides placement. Every rrect-lg cell's box lies closer to the
canvas edge than the 24-px sampling padding (listed per pass): 20 px at the canonical placement,
16, 12 and 10 px for the depth sweep's grid, 4-pt and s/4 cells; that is the canonical
rrect-lg's own condition, tightened, and a property of vitrea's render, not of posing.

## The runtime-base sample (clause 8; `runtime-base-sample.json`)

40 WebGPU cells: one per canonical backdrop kind (solid, checkerboard, impulse, synthetic-photo,
text-rows) × the four macOS 27 standard profiles × both poses — `light-solid` / `dark-solid`,
`checkerboard`, `photo` and the probe `hc-text-7` on rrect-md, and `impulse` on the capsule;
canonical calibration, validation and probe roles only (hc-text on the capsule and rrect-md is
holdout). All 40 exist in the canonical capture tree, drawn with the shipped documents
(`85ad7f7e3e0d`/`30fbe05986ae` light, `0eac5b294cc2`/`5cec8c961201` dark); their SHA-256 at G0
is recorded as a reading. G2 runs `check-capture-tree`, renders the sample with the shipped
documents at its base and requires byte identity (X37).

## The sitting (`sitting/`; clauses 4–5)

Derived from W39's driver, machine recorder, pass spec and G1 orchestrator, with W39 G1's gate
corrections (the by-name foreign census, per-capture HID idle as an admission check). One
order: `dump-layers` over the whole declared bed first (8 launches, 414 scenes; a departure
from memo D's configuration stops the sitting before its first capture), then the four 2x
passes (seven runs, run-1 references) and their long-protocol sentinels at mode 68, then the
1x passes and sentinels at mode 69, the display restored to 68 on every exit. Before every
launch a bounded wait for ≥ 75 s of HID idle, then every X6 and W34 X4 gate named in one
refusal; any refusal quarantines the run under its own name and stops the pass. The archive
tool files operational logs and dumps inside the archive and packs it as
`w42-archive-<sha256>.tar.zst`. `sitting.py plan` walks the whole sitting and executes
nothing: 2,968 glass + 260 references + 48 sentinel captures = 3,276 in 80 launches, and 424
dump scenes in 8 launches (`sitting/dry-plan.txt`, reproduced by `dry-plan-summary.py`).

**Length from real timings** (`sitting/timing.txt`, from W39 G1's 40 admitted runs and memo
D's dump runs): 8.81 h of capture + 0.97 h of dumps ≈ **9.82 h** with the s = 32 rows (9.61 h
before them), against the charter's model of 8.71 h + about 0.96 h for its smaller bed. Idle
waits beyond the measured gaps, quarantines, the grant switch and the rehearsal are excluded.
29 tests (`sitting/test-sitting.txt`, `test-archive.txt`; rerun after the s = 32 rows as
`test-sitting-s32.txt`, `test-archive-s32.txt`).

## The one-exposure runner (`exposure/`; clause 11, X26 as carried, X40)

W41's X26 runner imported as a module, none of its globals rebound: its wave-independent
functions (the committed-file checks, `persist`, `png`, `capture_web`, the request dataclasses)
run unchanged, and W39's `Receipt` and `Reader` come through `wave.py`. What W41 hard-binds
to W39's bed and W41's declaration is derived for W42 (scope, pins, freeze, verify, the
verdict, the run), keeping W41's lifecycle: nothing before `begin`, the blind rendered H
predictions recaptured and required byte- and projection-equal inside the receipt, the full
scores fsynced before any aggregation, `result.json` before `complete`, any fault after
`begin` spending H.

The one receipt binds the identified law (numerical, the structure through native T) and
both T candidates' renders. The verdict follows clause 11 rather than W41's all-must-pass:
the law closes iff every measured H cell of every claimed endpoint passes; candidate 2 is
its render against Apple, candidate 1 its render against its own frozen
structure-with-landed-T prediction with the gap to Apple recorded as the named level miss; a
candidate is landable only where the law closes, one candidate's failure never fails the
other, and X40 selects candidate 2 only if it is landable. Unclaimed endpoints are scored and
reported "not claimed (identity)" (Decision Log 3). The real declaration's scope is 400 glass
cells (424 less the 24 bridge cell-passes; 390 of 414 before the s = 32 rows), 40 of them H,
all web-plannable (`exposure/synthetic-check.json`; the suite rerun is `green-s32.txt`).

Production refuses until `exposure/production-pin.json` names G1's archive inventory and the
integrated G0 declaration and closure (all null now). Proved on a synthetic H built through
`wave.py`'s `Wave` in temporary repositories: 26 RED against a stub, 27 GREEN
(`exposure/red.txt`, `green.txt`, `red-unadmitted-holdout.txt`).

Two readings for the parent (the runner enforces them; the charter does not say): a manifest
with only a native-T candidate is refused, reading "lands instead" as presupposing candidate
1; and a claimed endpoint must have at least one MEASURED H cell to close, so an endpoint
whose H cells are all censored does not close.

## Integration notes

- `split_sha` is the SHA-256 of the whole `bed.json`, so the archive's Reader and the receipt
  bind it byte for byte: `bed.json` (and `scenes-w42-body.json`) must be frozen at the
  declaration's hash before G1's first capture. A later edit, even a prose one, is a changed
  declaration (clause 1's stop).
- `wave.py` shares its name with the standard library's `wave`, as W39's did; every tool here
  loads it by file path.
- Freeze at hand-back: `python3.12 packages/calibration/results/2026-09-16-w29-freeze/freeze.py
  verify` reads 1,818 entries.
