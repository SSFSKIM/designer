# W43 — the clearer glass: a `-glass0.25` material generation beside `-glass0.5`, the slider's second point, and a one-knob test of the body law (2026-10-01)

**Status update (2026-10-02): G0, G1a and G2's first stage have merged (§5.198–§5.200). The
user ruled Decision Logs 5 and 7 on 2026-10-02, "Adopt all eleven recommendations", and ruled
G1b for tonight. G3's refit is open.** The status as drafted follows unchanged.

**Status: DRAFT v1.2 (2026-10-01): the adversarial review of v1.1 folded (one P1, three P2, all
accepted by the parent; Revision Notes). No child is dispatched.** Chartered
on the user's ruling at W42's close, "Close W42 here (Recommended)", whose option reads "...
Then move to your planned next phase, the clearer glass capture at slider 0.25" (W42 Decision
Log 8; §5.197 §4). **The user ruled Decision Logs 1 and 3 on 2026-10-01**: a second fixed
setting, and two sittings. The parent ruled Decision Log 4 and adopted Decision Log 2 under the
user's sitting ruling. Decision Log 5 (bounds) stays open for G2's reading, and Decision Log 6
holds the parent's mechanical rulings at charter. Ledger §5.198–§5.201 are reserved, and §5.202
if G3 splits at the seal; §5.198 was W42's conditional reservation, which W42 closed without
using. Main is at `4da14bd3`, 0.25.0 is published, and the freeze reads 1,818.

## Decisions

The full entries are Decision Logs 1–7 at the tail.

| DL | question | status | what holds |
| --- | --- | --- | --- |
| 1 | the product's shape and API | **RULED** by the user, 2026-10-01: "Second fixed setting (Recommended)" | a second set of documents at 0.25 through the existing `materialProfileDocument` option; the default stays 0.5; the runtime reports `glassTintAmount`; a continuous slider waits for more positions |
| 2 | the capture scope | **ADOPTED** by the parent under the user's Decision Log 3 ruling | the four standard keys in full at seven runs; no accessibility pass; the w-test probe and the ladder at 0, 0.75 and 1 at three runs; every pixel through the W39 side bundle |
| 3 | the sittings | **RULED** by the user, 2026-10-01: "Two sittings, 12.4 h + 4 h (Recommended)" | G1a, the generation, about 12.4 h at the Mac; G1b, the probe and ladder, about 4.0 h, later |
| 4 | W42's structure question | **RULED** by the parent, 2026-10-01 | kept separate; the probe and ladder are declared readings, never a landing; W42's H and branches untouched |
| 5 | bounds for the 0.25 documents | **RULED** by the user, 2026-10-02: "Adopt all eleven recommendations" (Decision Log 7 item 10); (e) exercised: "All named misses; proceed to G3 (ii)" | (a)–(e) as drafted: the 0.5 tables per tier; M1, C1, X1; L1 with growth against the pre-fit render; M2 directional; E2 in absolute codes; S1 as R2; no floor; every non-holdout miss ruled before the holdout |
| 6 | the charter's mechanical rulings | the parent's | ledger, branches, routing, memo F in G0 |
| 7 | what G3 refits at 0.25 | **RULED** by the user, 2026-10-02: "Adopt all eleven recommendations" | the light level and tone first, the scatter second, dark thick tone and scatter only, light chroma and receded tint only on a miss; rim, highlight, shadow held; receded documents as differences; rrect-lg its own stratum; S1 as R2 over `s1/r2-population.json` |

## Purpose

The user, 2026-09-30, verbatim: "I also want a clearer glass capture. We currently have captured
a 0.5 version ... a version with more clear sight like that 0.25. We'll make it like next phase
once we're reasonably done with what we're doing right now." W42 has closed with two negatives
(§5.196, §5.197), and the user chose this as the next phase.

**What the wave is for.** vitrea's goal is the least possible gap to Apple's material. Since
macOS 27 that material has a user-facing axis: the Glass appearance slider, `NSGlassTintAmount`
in the global domain, which runs from ultraclear to fully tinted. Every macOS 27 pixel vitrea
has measured sits at one point on it, 0.5, the system default (W29 Decision Log 3 (a)). A page
that wants the clearer glass a Mac user gets by moving the slider left has nothing measured to
draw. W29 G0's sheet read the axis as material opacity: "at 0.0 the body is nearly clear and the
backdrop's structure reads through it" (§5.149 §4). 0.25 is halfway there.

**The best version of this is three things from two sittings** (Decision Log 3, RULED): the
generation first, then the probe and the ladder.

1. **A measured clearer material that any page can choose, honestly labelled.** Four material
   documents at 0.25 (light and dark, active and receded), fitted on the WebGPU tier with the CSS
   tier derived, gated like the 0.5 ones, and shipped opt-in. The runtime then reports the
   position it drew.
2. **The second point of an axis, not a one-off.** The 0.25 bed uses the 0.5 bed's scenes,
   split and protocol, and the 0.25 documents name the same leaves as the 0.5 ones, with no
   operator added. The two generations are then two points on one line through vitrea's
   material space, so a later continuous slider starts from two fitted points rather than one.
   The sitting also takes a small ladder at 0, 0.75 and 1, which says what shape the axis has
   between and beyond them.
3. **A one-knob test of the body law.** W42's law LT declared the Normal fill's weight w equal
   to the slider and fixed it at 0.5; it was never varied (memo D §0; X38). At 0.25, Apple's
   declared tree changes w, and with it the two light-scheme constants W29 G0 read; whether
   anything else moves is memo F's question. Under LT's algebra, the side of the body the hinge
   does not act on is pulled toward the wide term by w alone, so that pull must halve at 0.25,
   whatever k, λ and T are
   (Design, "The w-test"). And at the slider's ends the composite separates the two terms W42
   had to fit jointly: at 1 the body is the wide term alone, at 0 it is the narrow term with
   its hinge. That is the identifying experiment W42's open items lacked, and it costs a
   `defaults write`.

**Who it is for.** Web developers and designers who use vitrea for Apple's Liquid Glass and want
Apple's clearer setting: glass over media, imagery and maps, where the default's milk hides the
content. Later, desktop shells (Electron, Tauri) that can read the user's real slider would want
the continuous version, which this wave's evidence is the first step toward (Decision Log 1).

**What the wave does not do.** It does not land a body law (Decision Log 4) or capture any
accessibility state at 0.25 (Decision Log 2). It does not make the slider continuous (Decision
Log 1). It does not read W42's holdout H. And it does not move the 0.5 generation, the macOS 26.5
freeze, `DEFAULT_MATERIAL_PROFILE` or the default document (X1, X41).

## Parent-Level Acceptance

Each clause names its metric, the bed it is read on, the bar and what stops the wave.

1. **Declared before captured (G0).** *Metric:* the declaration's SHA-256, committed and
   independently reviewed, against the first capture's timestamp. *Bed:* the declaration: the
   four canonical keys and their membership; the probe and ladder cells with exact ids; the
   w-test's statistic, support, resolution and verdict rule; the ladder's readings; the bridge
   cells; both sittings' order and timing. *Bar:* every item, G1b's included, present and
   hashed before G1a's first capture. *Stop:* a capture before the hash, or a declaration
   change after it (between G1a and G1b included), voids the affected sitting as the bed; its
   captures are kept and never read as the bed.
2. **The slider's declared configuration is read before the bed is declared (G0, memo F).**
   *Metric:* every declared input of Apple's glass filter as a function of x. *Bed:*
   `dump-layers` through the side bundle at nine slider positions in all four endpoints (Design,
   "Memo F"). *Bar:* the inputs that move with x and the ones that do not are written down as
   pointers (X38), and the w-test's prediction is stated in their terms before the hash.
   *Stop:* an input that moves with x and that the declaration cannot state before the hash
   keeps the declaration open; nothing is captured.
3. **The bridges hold (G0, G1a, G1b).** *Metric:* byte identity, or region medians within max(1
   code, bar), cell by cell. *Bed:* before the sittings, W42's family F frames (the side bundle
   at 0.5, 2026-09-30) against the canonical 0.5 fixtures (the original bundle,
   2026-09-18/19); in each sitting, at 0.5, W42's sentinels at its opening and its close and a
   set of canonical cells at its opening (G1a at both scales, G1b at 2x). *Bar:* every bridge
   cell agrees. *Stop:* a disagreement before the sittings goes to the user before the
   declaration is hashed; one at a sitting's opening stops that sitting before any capture away
   from 0.5; one at a close voids nothing already admitted, but G2 reads that sitting's
   claims against 0.5 as unbridged (X43) and the user rules before G3 opens.
4. **Each sitting is attested (G1a, G1b).** *Metric:* every capture's attestation. *Bed:* every
   declared pass. *Bar:* W42's X6 facts with the slider at the pass's declared position, read
   twice (the defaults domain and the tree's own `inputBlurFillNormalOpacity`, X42); W34 X4's
   native set (build 26A428, `ButtonShapesEnabled` 0, Show Borders 0, the display mode before
   and after, the colour context, the side bundle's binary, cdhash and `LC_BUILD_VERSION`,
   `deterministic`, the attested pose, the window frame); `hidIdleSeconds` ≥ 60 per fixture.
   *Stop:* a run that fails to attest is quarantined under its own name; a wrong mode, a lost
   grant, a failed idle wait or a foreign process stops the pass; a continuation is the parent's
   explicit act; there is never a hidden retry. Nothing is read against vitrea in either
   sitting.
5. **Repeats, publication and the archive (G1a, G1b).** *Metric:* the bar per cell, region and
   channel (W39's rule: 0.5 plus half the largest pairwise separation of the run medians); the
   plurality publication's refusals. *Bed:* every admitted run. *Bar:* the canonical bed at seven
   runs, plurality-published by `materialize` into `fixtures/apple-macos-27.0-*-glass0.25/` with no
   refusal and the per-profile count equal to the 0.5 count, or each missing cell named (G1a); the
   probe and ladder at three runs (Decision Log 2), never plurality-published (G1b); each sitting's
   archive of record complete, published by SHA-256 and replayed identically with the raw root
   denied. *Stop:* G2's generation reading (a, b, e) does not open until G1a's bar, publication and
   replay are committed, and its probe reading (c, d) not until G1b's are.
6. **The original bundle is restored (G1b's close).** *Metric:* the system TCC database and a
   positive capture. *Bed:* the canonical 2x light checkerboard capsule at 0.5. *Bar:* the user
   re-adds `dev.vitrea.reference-apple` by hand; its capture is `captured-active`,
   deterministic, and equal to `204f21f0…` or `6c15311b…` (the parent's W42 G1 ruling).
   *Stop:* a failed restore is an open blocker, not a closed sitting. This closes W42 Decision
   Log 8's deferral. The restore waits for G1b because both sittings need the side bundle, and
   the user's W42 ruling chose to avoid two extra swaps; if G1b is cancelled, the restore
   happens at the cancellation instead.
7. **Measured before moved (G2).** *Metric:* the native delta, 0.25 against 0.5, per cell and
   per metric, through W29 G2's driver. *Bed:* every canonical 0.25 cell with its 0.5
   counterpart. *Bar:* the per-metric bar is the 0.25 runs' own run-to-run distribution,
   declared and committed before the first pair is read; a verdict *moved / not moved* per law
   (silhouette, contour, interior level, tone by backdrop, scatter, chroma, rim band,
   highlight, exterior shadow, tint shade, the recede); sheets per profile at both scales; no
   vitrea change in the child. *Stop:* a law the bar cannot separate is the finding; it is not
   refit.
8. **The w-test (G2).** *Metric:* the declared free-side statistic (Design). *Bed:* the w-test
   probe at 0.25 against its seven-run 0.5 counterparts in `w42-archive`, and the ladder
   positions. *Bar:* the declared verdict rule per endpoint at the declared resolution. *Stop:*
   none; either verdict is recorded with its numbers, no family or support changes after the
   read, and nothing lands from it.
9. **The ladder, described (G2).** *Metric:* T(x) per endpoint and span stratum; the free side's
   pre-tone value against x; the x = 1 and x = 0 bodies. *Bed:* the ladder. *Bar:* descriptive;
   the numbers are written for the next structure wave and for the continuous slider's charter,
   with a recommendation on the latter's form and the fewest generations it needs. No fit is
   claimed and no gate reads it.
10. **The refit, gated before the holdout (G3).** *Metric:* the adopted bounds and rows Decision
    Log 5 rules, implemented with their baseline selection and rehearsed before any candidate is
    judged. *Bed:* the fit in scratch; then two final publication stages (light and dark) under
    the CLAUDE.md recipe, both tiers, filled completely, holdout last. *Bar:* four 0.25
    documents as patches over the unmoved runtime default, naming the same leaves as their 0.5
    counterparts (X44), moved only where clause 7 says Apple's law moved (X3); bounds declared
    before the read; **every non-holdout verdict passing, or each miss explicitly ruled by the
    user as a permitted named miss, before the holdout is read**; the holdout read once per
    tier; publication only after every verdict, holdout included, has passed or been ruled; no
    floor; every residual named. *Stop:* a non-holdout miss the user does not permit stops the
    holdout read and the publication; the documents return to fitting in scratch, or the wave
    closes at the miss. This is W42's lesson (its Deferred at close 7; X33): a holdout is spent
    only after every referee readable without it has passed.
11. **Nothing frozen moves (G0–G3).** *Metric:* `freeze.py verify`; the 0.5 generation's hash
    manifest (X41); the goldens; the six shipped documents' digests. *Bar:* the freeze reads
    1,818 and the X41 manifest verifies at every merge; the 34 goldens are byte-identical; the
    four 0.5 digests stay `be13dae45098fc89` / `2a4323f33df8d799` / `b0d0d8dacc6a03af` /
    `7c454858a3cbad5b` and the 26.5 pair `b2b570e4adcea8fb` / `874be66ea501621b`. *Stop:* a
    protected byte that moves stops the merge.
12. **Which material a page gets (G3).** Decision Log 1 executed. The README says what a page
    draws by default and how it chooses 0.25, and `root.material` and
    `GlassGroupState.materialDocument` report the position that drew.
13. **The landing (G3).** One publication per stage through W40's publisher; the capture tree
    copied to the canonical path and `check-capture-tree` exit 0 on it; the 0.25 profiles'
    adopted-threshold blocks; the generated profile module pinned to its documents; every
    consumer of the current union names its position (X45); the demo and playground; CLAUDE.md,
    the READMEs and the ledger's pointers; the changeset (a fixed-group minor, 0.26.0); the c9d
    chain green at the release commit. `pnpm release` is the user's hand and the tag follows.
14. **By eye, and the ledger (every child).** Native 0.25 | native 0.5 | difference sheets in
    G2; native | WebGPU | CSS | difference sheets at G3's read over the whole bed; the demo at
    0.25 beside the harness capture. Every gap to Apple at 0.25 is a named line in a claims
    section, this wave's Deferred list or the tracker.

## Grounding Baseline (main at `4da14bd3`, W42 closed, 0.25.0 published)

**What the slider does, as far as it has been read.** `NSGlassTintAmount` is a float in the global
domain. With the key absent the material renders at 0.5, byte for byte, and 0.5 is the knee of
the declared ramps (§5.149 §4). W29 G0 dumped three inputs at five positions (0, 0.25, 0.5,
0.5459057, 1): `inputBlurFillNormalOpacity` equal to the key; the face fill colour's alpha 0,
0.10, 0.20, 0.2275, 0.50; `inputBlurFillLightenOpacity` 0.675, 0.7875, 0.9, 0.9, 0.9. Memo D
identified the first as the Normal composite's weight w and the second as the light face's white
fill (W42 Grounding). The fill and the Lighten are light-scheme inputs: memo D's dark face
declares no fill and composites Darken. So **how the dark scheme's Darken, face and MaxLuma move
with x, and whether any other input moves at all, is unread.** In pixels, the slider moved 10 of
10 probe cells at 0.0 and at 1.0 by maxDelta 34–106 codes (ΔE up to 0.357), in both poses and at
both scales (§5.149 §4). No pixel has ever been captured at 0.25.

**The 0.5 generation.** Seven macOS 27 profile directories. The four standard ones hold 164
light and 117 dark cells per scale, **562 in all**: per light profile, calibration 37,
validation 12, holdout 20, recorded 8, probe 87 (68 inactive); per dark profile 19 / 2 / 7 / 2 /
87 (51 inactive). The accessibility keys are 1x light only: reduced transparency 30,
increased contrast 32, coupled 32. The documents are the four `apple-macos-27.0-1x-*-glass0.5*`
files (hashes `85ad7f7e3e0d` / `0eac5b294cc2` / `30fbe05986ae` / `5cec8c961201`; digests above).
The generation index holds `85ad7f7e3e0d.json` (509 rows over four light profiles) and
`0eac5b294cc2.json` (277 rows over two dark profiles), both current. The six gated macOS 27
profiles are the four light (standard 1x and 2x, reduced transparency, coupled contrast) and
the two dark standard.

**The machine and the two bundles.** macOS 27.0 build 26A428 at W42 G1 (2026-09-30). The W39 side
bundle, `dev.vitrea.reference-apple.w39` at `~/vitrea-w39/side/` (binary `02052b17…`, cdhash
`be258cbf…`, sources byte-identical to `apps/reference-apple/Sources` per memo D), holds the
machine's one Screen Recording grant (auth 2 since 2026-09-30 10:44:55Z). The original
`dev.vitrea.reference-apple` (binary `bd3092e8…`, cdhash `88cbbb5b…`) captured every canonical macOS
27 fixture; its Screen Recording row was removed at W42 G1, and its Accessibility row is untouched.
Its restore and positive check are deferred to this wave's capture by the user's ruling (W42
Decision Log 8); under Decision Log 3 they fall at G1b's close. Two facts already tie the bundles
together. At W42 G1 both captured the same frame, `204f21f0…`, on the canonical 2x light
checkerboard capsule. At W39 G1 the side captured a canonical 2x cell byte-identical to its
committed fixture. **X5's lift was scoped to W42's bed by its own terms** (§5.197 §3), so W43 needs
its own.

**What already carries a `-glass0.25` key, unchanged.**
- `PROFILE_KEY_PATTERN` parses the trailing `-glass<amount>` as a number
  (`packages/calibration/src/profile.ts`).
- `materialize` refuses a run whose attested `glassTintAmount` differs from the key's
  (`src/run-provenance.ts`, its rule 3, exact equality).
- W40's publisher accepts a first generation for a profile with no current one: it retires a
  previous generation only `if (previous)` (`src/generation-stage.ts`).
- The native delta driver (`cli/native-delta.ts`) reads two fixture directories by profile key.

**What hard-codes 0.5, or one macOS 27 document.**
- The sitting scripts: `run-sitting-27.sh` (`GLASS_DECLARED="0.5"`), and W42's `sitting.py` and
  `record-machine.py` gate.
- The calibration page selects a shipped document by its OS token alone (Surprises 1).
- `material-document.ts` (two documents); `scripts/generate-macos27-profile.mjs` and
  `macos27-profile-export.test.ts` (four documents); `adopted-thresholds.test.ts`'s per-profile
  blocks; `tier-coherence.test.ts`'s pins against the shipped documents.
- The demo's reduction (`apps/demo/matrix-reduction.ts`) keeps every row read at a shipped
  document. Once the 0.25 documents ship, their rows enter its picker unless it names a position.
- About thirty test and e2e files name `glass0.5`.

**The public surface.** `createGlassRoot({ materialProfileDocument })` reads the document once, at
construction (`platform-web/src/root.ts:935`); React takes the same value on `<GlassRoot>`.
`root.material` and `GlassGroupState.materialDocument` are a `ResolvedMaterialDocument`: name,
platform, profileKey, `resolvedMaterialSha256`, `tuned` (`core/src/state.ts:159`). vitrea already
has a material variant named `"clear"` (`core/src/material.ts`): Apple's `Glass.clear`, a
different material from the slider's clearer end.

**Measured capture rates.** W29's four standard passes at seven runs, 3,934 captures through the
original bundle, took 10 h 28 m of pass wall (`results/2026-09-18-w29-g1-bed/sitting.md`): 9.58
s per capture with every per-run cost included. W42 G0's model, built from W39 G1's real runs
(`results/2026-09-29-w42-g0-declaration/bed/sitting/timing.txt`), has these rates:
- a 2x run takes 5.46 + 9.530·n s, and a 1x run −2.4 + 9.541·n s;
- a sentinel capture takes about 16.5 s;
- a dump takes 8.13 s per scene plus 6.23 s per launch;
- runs are separated by 1.2 s gaps.

That model priced W42 at 10.31 h. W42 took 11 h 22 m at the Mac, of which about 64 minutes went
to its five stops (lost runs and the waits before each continuation, §5.195 §2), so its net
was within a minute of the model. W29's sitting lost almost nothing to stops (one refused
rehearsal). The model prices the canonical bed at 10.44 h against W29's measured 10.47 h.

**W42's sitting machinery** (`results/2026-09-29-w42-g0-declaration/bed/sitting/`) is
reusable: the pin-checked driver, the detached orchestrator with its display-mode trap, the
by-name census and X6 gate, per-fixture attestation, quarantines, the archive producer with its
guarded replay, and the W39 bar. Its four G1 findings are tracker entries, and W42's Deferred at
close 10 says they are fixed before this sitting:
- the census over-matches command lines that merely name a browser or the harness;
- ancestor exclusion does not reach a detached launch;
- the per-pass commit drops `driver-idle.log` (`*.log` is gitignored);
- Universal Control input is invisible to the gates.

The memory lesson on quarantines records what W39 and W42 lost runs to: the user's chat and
Universal Control input on the capture Mac, a TCC prompt for the session's own binary, foreign
browsers (another session's Playwright among them), the worker's own `pgrep` line, and a
concurrent worker's test suite spawning stub launchers.

**Two lessons on declaring bars** (memory, W42). A survival bar over cells a prior memo already
proved unclosable decides the identification before the read: exclude such cells, model their
cause, or say plainly what the decision rests on. A per-statistic "never worse than shipped"
rule fails a model that is better on average, because the baseline's errors cancel by accident;
rehearse any rule on existing renders before hashing it.

## Design (advisory unless marked)

### The product (MARKED; Decision Log 1, RULED)

- **A second document, selected the way documents are selected today.**
  `macos27Glass025MaterialProfileDocument` ships beside `macos27MaterialProfileDocument` (which
  is the 0.5 document and stays the default) and `macos26MaterialProfileDocument`. A page opts
  in with `createGlassRoot({ materialProfileDocument: macos27Glass025MaterialProfileDocument })`
  or the same prop on `<GlassRoot>`. `SHIPPED_MATERIAL_PROFILE_DOCUMENTS` lists all three.
- **The honesty core names the position.** `GlassMaterialProfileDocument` and
  `ResolvedMaterialDocument` gain `glassTintAmount?: number`: 0.5 and 0.25 on the macOS 27
  documents, absent on macOS 26.5. It is absent rather than defaulted, as `NativeProfile.glass`
  is, because a material measured before the axis existed says nothing about it. The name and
  profile key already carry the token; the field makes it readable without parsing a string.
- **Named by the measurement, never "clear".** The documents say "clearer glass" in prose, but
  no identifier uses `clear`, because `variant: "clear"` is already Apple's `Glass.clear`.
- **A construction-time choice.** The root reads the document once, so a live switch remounts
  the root, as it does today for 26.5 against 27. A live setter is Deferred.

### The generation's bed (MARKED; Decision Log 2, ADOPTED)

- **The canonical standard bed at 0.25, mirrored exactly.** `scenes.json` version 8 adds four
  profile entries, `apple-macos-27.0-{1x,2x}-{light,dark}-standard-glass0.25`, whose scene
  lists are copies of their 0.5 counterparts'. No scene, background, component, split
  membership or 0.5 entry moves: a diff against version 7 is four entries and a note. Every
  0.25 cell then has a 0.5 counterpart for clause 7, and the gate's populations exist at 0.25
  as they do at 0.5.
- **Seven runs**, plurality-published as W29's bed was, so the generation sits at the same bar
  as the one it stands beside.
- **No accessibility key.** Whether the slider reaches the reduced-transparency or
  increased-contrast material at all is unread. The passes need the user's hand on System
  Settings twice, and none of the material-axis rows (M1, M2, C1, X1, L1) covers an
  accessibility profile. The 0.25 documents carry the 0.5 documents' accessibility leaves
  unchanged, recorded as unmeasured at 0.25.

### The bridges (MARKED)

Every W43 pixel comes through the side bundle, and the canonical 0.5 bed came through the
original. Every 0.25-against-0.5 claim therefore assumes the bundles and the machine agree. Two
bridges make that a measurement:
- **On existing evidence (G0).** W42's family F cells were captured through the side bundle at
  0.5 on 2026-09-30: canonical checker-16, impulse and photo on rrect-md, and probe checker-64 on
  rrect-lg, at seven runs. They have never been read (§5.196 §1). G0 reads them against the
  canonical 0.5 fixtures.
- **In each sitting, at 0.5.** W42's two sentinel cells, three runs per endpoint, against their
  `w42-archive` frames, at the sitting's opening and again at its close; and at the opening
  only, six canonical cells per canonical pass at three runs, against their fixtures. G1a
  bridges both scales. G1b, whose cells are all 2x, bridges 2x only, and its opening bridge is
  also the check that nothing on the machine moved between the two sittings.

### Memo F: the slider in Apple's declared tree (G0)

`dump-layers` needs no grant, only an idle Mac, as memo D's did. It runs through the side
bundle at x ∈ {0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1}, in all four endpoints, on six
scenes per endpoint that span memo D's span strata, at 2x, plus x = 0.25 at 1x. That is about 240
scene dumps, roughly 0.6 h. The slider is restored after. Memo F answers three questions:
- which declared inputs move with x, in each endpoint and especially the dark ones;
- whether memo D's seventeen span laws (radii, the narrow opacity law, the margins, the backdrop
  scale, the bleed, the ring shadow and the highlight) hold unchanged at 0.25;
- the shapes of the dark scheme's ramps.

Its numbers are pointers (X38). They write the w-test's prediction, and the pixels referee it.

### The w-test: one knob, one prediction (MARKED; Decision Logs 2 and 4)

**The algebra** (W42 Design, LT; light written out, dark the mirror). C is the narrow term, W
the wide term, λ the Lighten weight, w the Normal weight, all averaged in encoded space:

    N = C + λ·max(0, W − C),    M = (1 − w)·N + w·W,    y = T(M)

**The free side** is where the hinge does not act: in light where C ≥ W, in dark where C ≤ W.
There M = C + w·(W − C), and λ does not enter. On the lifted side
M = C + (w + λ(1 − w))·(W − C).

**The prediction.** Wherever C and W do not move with x (memo F's second question), the free
side's pre-tone excursion scales with w:

    (T₀.₂₅⁻¹(y₀.₂₅) − C) / (T₀.₅⁻¹(y₀.₅) − C) = w(0.25) / w(0.5) = 0.5

This holds for any k, λ and T, with T inverted natively at each position from greys captured
at that position. Across the ladder the free side is affine in x: M(x) = C + x·(W − C), so
M(0) = C and M(1) = W, with no k, λ or W needed to test it.

**What the declared constants say the product looks like.** In light, the free side keeps
1 − w of the narrow detail: 75 % at 0.25 against 50 % at 0.5. The lifted side keeps
1 − (w + λ(1 − w)): 16 % against 5 % (λ 0.7875 against 0.9). So 0.25 is clearer mainly on the
free side, and its body is **more one-sided** than 0.5's: the gap between the sides grows from
0.45 to 0.59. vitrea's shipped body is two-sided (memo C's mirror statistic ≤ 0.024 against
Apple's 0.2–0.5). So the shipped form's structural miss is predicted to grow at 0.25. This is
written here, before any pixel, so that G3's misses are a prediction confirmed or refuted, not
a surprise.

**The support, chosen by W42's lessons** (G0 fixes ids, levels and minimums):
- *Regions:* free-side region cores where the 0.5 fit puts C at the backdrop's own level within
  the bar, and |W − C| is above a declared minimum contrast.
- *Shapes:* capsule, rrect-64, rrect-80 and rrect-md at 2x. These are where LT nearly closed at
  0.5 in light active, 0.6–1.2 codes (§5.196 §3.2).
- *Excluded, with the reason recorded:* every rrect-ml and rrect-lg cell (W42 Deferred at close
  1); every 1x cell (Deferred at close 2: the aliasing no Gaussian closes); dark levels above
  208 at s ≥ 96, where native T is not monotone and cannot be inverted (Deferred at close 3).
- *Lifted side:* read and reported, not gated. λ(0.25) is compared with the two scalings memo
  F's ramps allow (the fitted λ times the declared ratio, or minus the declared difference).

**The verdict.** Per endpoint: PASS if the free-side ratio is within its propagated resolution of
0.5 on every supported region; FAIL otherwise, with the measured ratio, which is itself the
reading of w(0.25) / w(0.5). Before the hash, the statistic is rehearsed in three ways:
- on synthetic LT renders at w 0.25 and 0.5 through native T, quantised to ±0.5, where it must
  recover 0.5;
- on a two-sided linear control, where the free and lifted readings must be equal;
- on W42's 0.5 cells, to show every supported region is well conditioned.

The test reads its cells once, against the hashed prediction. A pass is evidence for LT's
composite and its slider coupling; a FAIL refutes that coupling. Either verdict redirects the
next structure wave; neither lands anything.

**The probe's cells** are a subset of W42's declared bed, about 28 per 2x endpoint, with ids
reused so that every one has its seven-run 0.5 counterpart in `w42-archive` (calibration and
validation roles only; X46):
- family A greys on the capsule (t = 0) and on rrect-md (s = 96), to give T at both strata;
- B two-level checkers at pitch 16 and 64 on rrect-md, at levels inside each endpoint's
  monotone range;
- B′ P1 on the capsule at pitch 32 and 64;
- D steps at δ 0 and 32, both polarities, on rrect-md;
- C squares S 32, both polarities, on rrect-md.

The no-glass references do not depend on the slider, so W42's are reused; one per pass is
recaptured to prove it.

### The slider ladder (MARKED; Decision Log 2, ADOPTED)

Three positions beyond 0.25 and 0.5, all at 2x and three runs:
- **x = 1:** the probe's 28 cells per endpoint. M = W everywhere, so the body is the wide term
  through T(1) on both sides. This reads W's kernel, reach and support directly: W42's U1, U3,
  U4 and U7, which it had to fit jointly with C.
- **x = 0:** the same cells. The free side reads C directly; the lifted side reads C with the
  hinge at λ(0) (0.675 in light).
- **x = 0.75:** about 10 cells per endpoint, greys and two free-side cores. These read T on the
  [0.5, 1] segment, where the declared face fill rises from 0.20 to 0.50 while Lighten holds.

Each position opens with a dump sentinel. The ladder is described in G2 (clause 9) and fitted by
no one in W43. It is the evidence base for two later questions:
- whether a continuous slider is better carried by a law in x or by interpolating fitted
  documents;
- how many generations either route needs.

### The two sittings (MARKED; Decision Log 3, RULED)

**G1a, the generation** (about 12.4 h at the Mac, overnight):
0. **Opening, at 0.5.** The machine read: the X6 facts, build 26A428, Universal Control off, a
   clean census, and the slider's as-found value. The side bundle's pose check (expect
   `204f21f0…` or `6c15311b…`). The opening bridges at both scales.
1. **x = 0.25, mode 68.** Dump sentinels, then the canonical 2x passes (active 162, receded
   119), seven runs.
2. **x = 0.25, mode 69.** Dump sentinels, then the canonical 1x passes, seven runs.
3. **x = 0.5.** The closing bridges at both scales; mode 68 restored and verified; the slider
   set back to its as-found value. The side bundle keeps the grant for G1b.

**G1b, the probe and the ladder** (about 4.0 h at the Mac, on a later day):
0. **Opening, at 0.5, mode 68.** The machine read as in G1a, the build still 26A428 and the
   side's pins unchanged; the pose check; the opening bridges at 2x.
1. **x = 0.25.** Dump sentinels, then the w-test probe, four passes.
2. **The ladder.** x = 1, then 0, then 0.75, each opening with its dump sentinels.
3. **x = 0.5.** The closing bridges at 2x; the slider set back to its as-found value.
4. **The restore.** The user re-adds the original bundle by hand (W39's close recipe: remove
   every VitreaReference entry and add the original alone), and the parent runs its positive
   check (clause 6).

The orchestrator's exit trap restores both the display mode and the slider on every path. A
sitting that must stop drops from the bottom of its own order (in G1b, the ladder's x = 0.75,
then 0, then 1, then the probe). A dropped block is recorded and is not captured later without
a new ruling (X47).

**The estimate**, from the rates in Grounding (W42 G0's model; W29's measured canonical rate as
the check):

| sitting | block | captures | modelled |
| --- | --- | ---: | ---: |
| G1a | canonical 0.25 bed: 562 cells a round, seven runs, four passes | 3,934 | 10.44 h |
| G1a | bridges at 0.5, both scales: W42's sentinels at the opening and close (96), 72 canonical bridge captures | 168 | 0.65 h |
| G1a | dump sentinels at 0.25 (48 scenes), display switches, slider writes, the pose check | 1 | 0.17 h |
| **G1a** | **total** | **4,103** | **11.26 h** |
| G1b | w-test probe: 28 cells × 4 endpoints, 2x, three runs, plus 16 references | 352 | 0.95 h |
| G1b | ladder: x = 1 and 0 at 28 cells, x = 0.75 at 10, four endpoints, three runs | 792 | 2.16 h |
| G1b | bridges at 0.5, 2x: W42's sentinels at the opening and close (48), 36 canonical bridge captures | 84 | 0.32 h |
| G1b | dump sentinels (72 scenes), slider writes, the pose check | 1 | 0.21 h |
| **G1b** | **total** | **1,229** | **3.65 h** |

At the Mac, G1a is 11.3 h if nothing stops, as at W29, and about 12.4 h with W42's 10 % stop
loss; G1b is 3.7 h and about 4.0 h. Split this way, the two sittings cost about 0.4 h more than
one, for G1b's own bridges, dumps and checks. To these add G0's memo F window (about 0.6 h, on
another day) and the user's restore at G1b's close (about 15 minutes).

*Priced for the decision and not chosen* (modelled, at the Mac with 10 %):
- one sitting of the same scope: 14.5 h (16.0 h);
- the canonical bed at three runs, the probe and ladder at three: 8.5 h (9.4 h);
- the canonical bed at three runs, no probe or ladder: 5.3 h (5.8 h);
- everything at seven runs: 18.6 h (20.5 h).

A three-run canonical bed could confirm that 0.25 sits at the 0.5-code floor W39 and W42
measured. It could not settle the cells that flip between two states: W29's 0.5 bed had 110
voted and 9 frequency-settled cells at seven runs, and three runs see a one-in-six minority
state only 42 % of the time. W39's and W42's floor was also measured on region medians, not on
the SSIM, ΔE and contour metrics W29's native delta reads. And the 0.25 fixtures would sit at a
weaker bar than the 0.5 generation they are compared against. The user's ruling keeps seven.

### The native delta and the refit (advisory; chartered from G2's reading)

G2 re-keys W29 G2's driver to the pair (`-glass0.25`, `-glass0.5`), with its bar from the 0.25
sitting's raw runs declared before the first pair. Its verdict per law decides G3's scope (X3).

G3 refits starting from the 0.5 documents, on the WebGPU tier first, with the CSS tier derived
in the same child. It uses the existing leaves only (X44; W28's mechanism precommit). Memo F and
the w-test point at the body: the tone response, the milk and tint alpha, the scatter's
sharp-and-deep share, and the body chroma retention. The shadow, rim and highlight should move
only if clause 7 says Apple's did.

The 0.25 documents publish as two new generations, light and dark, each with its own receded
pair. Each is a first generation for its profiles, so it retires nothing. The fitted pair
(0.5 value, 0.25 value) for every leaf is tabled in the ledger, as the data a continuous
document interpolation would start from.

### Referees: what carries over, and what is new

- **Unchanged:** `freeze.py verify` (1,818); the 34 goldens; `tuned-profiles.test.ts`'s 26.5 pin;
  the six shipped digests; `check-capture-tree` on the 0.5 tree; `materialize`'s refusals,
  including the slider's exact equality; W42's sitting gates, with x per pass.
- **Re-instantiated at 0.25 (Decision Log 5):**
  - the per-profile adopted tables;
  - M1, C1 and X1 over the 0.25 standard profiles;
  - L1, with its growth measured against the pre-fit baseline (the 0.5 documents rendered on the
    0.25 cells);
  - M2, read directionally against Apple's own 0.25 texture (W42 Decision Log 5a's form);
  - E2, per cell in absolute codes (W42 Decision Log 5e's form);
  - `tier-coherence.test.ts` and the profile-export pin, extended to the 0.25 documents;
  - `check-capture-tree` on the 0.25 tree.
- **New in this wave:**
  - the slider native delta (clause 7);
  - the bridges (clause 3);
  - the tree attestation of the slider (X42);
  - the w-test (clause 8);
  - **S1, the slider's direction:** on every non-holdout standard cell where Apple's 0.25-to-0.5
    change in interior level exceeds its bar, vitrea's change has the same sign, and the median
    ratio of vitrea's change to Apple's lies in [0.8, 1.2]. It is read in G3 and adopted only by
    the user's ruling (Decision Log 5 (c)). Per-document bounds cannot see this property, and a
    developer switching positions sees exactly it. **Its sign clause is not fidelity, and is
    rehearsed before Decision Log 5 is ruled.** Where the shipped 0.5 render already errs in the
    direction of Apple's change, by more than that change, a 0.25 endpoint that matched Apple
    exactly would move against Apple's delta. G2 maps those cells on a perfect-endpoint null
    (Apple's own 0.25 in vitrea's place) before any vitrea render at 0.25, and S1 is restated
    from that map if it must be, for example over the cells where the shipped 0.5 render is
    within the bar of Apple, as the memory lesson on improvement rules advises;
  - the selection-seam test (Surprises 1; X45).

## Children

### G0: Grounding, declaration and instrument (ledger §5.198)

Branch `w43-g0-declaration`; evidence `packages/calibration/results/<date>-w43-g0-declaration/`.
- **(a) The manifests first.** Before any other act, `freeze.py verify` reads 1,818 and X41's
  0.5 manifest is written and committed. It holds two kinds of protection:
  - **bytes:** the four 0.5 standard fixture trees, the 0.5 accessibility trees, their entries in
    `fixtures/manifest.json`, the four 0.5 profile documents, `src/macos27-profile.ts` (the
    generated material), the two current generation files and the index's 0.5 entries;
  - **a projection of `macos27MaterialProfileDocument`:** its optical content (the four endpoint
    patches and their resolved digests), its endpoint identities (name, platform, profile keys)
    and its CSS mapping, hashed as a canonical JSON projection. The one permitted change is
    Decision Log 1's ruled readout metadata, `glassTintAmount: 0.5`; any other field moving
    fails the check.
- **(b) The bridge on existing evidence** (clause 3), from `w42-archive` through its guarded
  reader, H never requested. A disagreement goes to the user before (e) is hashed.
- **(c) Memo F** (clause 2). This is G0's only native act. It needs no grant and no X5 lift,
  only the user's go for a 40-minute idle window (Decision Log 3) and the slider written and
  restored by `defaults`.
- **(d) The sitting tooling,** derived from W42's, with a red and a green case for each change:
  - the four tracker fixes: the census by executable; the launching shell's chain excluded; the
    idle log kept as `.txt`; a watchdog on frontmost and idle during every launch, and a
    pre-sitting Universal Control check;
  - the slider declared per pass, with the as-found value restored by the trap. A `defaults
    write` takes effect only for a freshly launched harness (the review's confirmation; W29 G0
    relaunched per arm for it), so every slider write is followed only by fresh launches, and a
    harness or dump process alive across a write refuses the pass;
  - the dump sentinel's Normal = x check;
  - the canonical publication path for side-bundle runs: the attestation `materialize` reads,
    the bundle pin naming the side;
  - the archive storing each distinct frame once by SHA-256, with per-run membership, so a
    unanimous cell costs one frame;
  - the dry plan and timing re-derived from the declared membership.
- **(e) The declaration** (clause 1):
  - `scenes.json` version 8;
  - the wave-local probe and ladder scenes file and bed;
  - the w-test and ladder readings written from memo F, the bridge cells, both sittings' plans;
  - rehearsed as Design states, then hashed.
- **(f) The selection seam, in two declared modes** (Surprises 1):
  - **strict shipped mode**, for every read of a shipped material: the page selects a shipped
    document by (OS, glass) and refuses an unshipped or ambiguous pair;
  - **candidate mode**, for every fit and pre-seal read: the driver declares a complete
    candidate document, built over the unmoved `DEFAULT_MATERIAL_PROFILE` and independent of the
    shipped registry, with its own four endpoints (active and receded, per scheme) and its own
    CSS mapping, each matched by hash. The page constructs the root from that document, never
    from a shipped document with a patch injected over it, and stamps every output "candidate".
    It refuses a partial candidate, a candidate whose keys' glass token differs from its declared
    position, and a candidate that names a shipped document.

  Before any 0.25 shipped export exists, G0 proves the candidate path. A candidate whose content
  is the 0.5 documents', declared under a scratch `-glass0.25` name, must render byte-identical
  to strict mode's shipped 0.5 render on a declared sample covering all four endpoints and both
  tiers. Every refusal case gets a red case. No material moves.
- **Acceptance:** clauses 1–3 and 11; an independent review (`doperpowers:reviewer-medium`)
  closed; then the parent tells the user that the tooling is ready and how long G1a is
  (Decision Log 3).
- **Stops:**
  - a bridge disagreement;
  - memo F shows an input moving with x that the declaration cannot state before the hash;
  - the side bundle's pins differ from W39 G0's `bundle-pin.json`;
  - the machine is no longer on 26A428 (Risks).

### G1a: The generation sitting (ledger §5.199)

Branch `w43-g1a-generation`. It starts after G0 has merged, the user has lifted X5′ for W43's
beds, and the user's go (Decision Log 3). About 11.3 h modelled, 12.4 h at the Mac.
- G1a's order in Design ("The two sittings"). Every capture attested (clause 4) and quarantines
  named.
- The canonical bed plurality-published by `materialize --frequency-settle` into the four
  `-glass0.25` fixture directories, with the manifest's hardware block naming the side bundle.
- The bar published from the archive before plurality.
- `w43-archive-g1a` published as a release asset named by SHA-256 and bytes, with a second
  owner-controlled copy, and replayed with the raw root denied. Operational logs and dumps go
  into the archive, not into git.
- The freeze and X41 manifests verified at the close; the slider read back at its as-found
  value. The side bundle keeps the grant, and the original stays unrestored until G1b's close
  (clause 6). Nothing is read against vitrea; no browser runs while a native pass runs.

### G1b: The probe and ladder sitting (ledger §5.199b)

Branch `w43-g1b-probe`. It starts on a later day, after G1a has merged, with the user's go; X5′
covers it. About 3.7 h modelled, 4.0 h at the Mac.
- G1b's order in Design. Its opening bridge at 2x is also the check that nothing on the machine
  moved between the sittings: a different build, side pin or bridge frame stops G1b before any
  capture away from 0.5 and goes to the user.
- The probe and ladder archived as `w43-archive-g1b` by the same rules, never published as
  fixtures. The bar is published from the archive.
- The original bundle restored and positively checked (clause 6). Then the side bundle is
  retired with no row, as at W39's close.
- The freeze and X41 manifests verified at the close.

### G2: The reading (ledger §5.200)

Branch `w43-g2-reading`; no vitrea change of any kind. It reads in two stages, so the product
path does not wait for G1b.
- **After G1a:**
  - **(a)** G1a's bridges read (clause 3);
  - **(b)** the native delta with its bar declared first, and sheets (clause 7);
  - **(f)** S1's rehearsal on the perfect-endpoint null (Design, "Referees"): the shipped 0.5
    render's error per cell, from the current generation's rows, against Apple's slider change
    from (b). This maps the cells where a 0.25 endpoint that matched Apple exactly would still
    fail S1's sign clause. It needs no vitrea render at 0.25;
  - **(e)** a Decision Log 7 draft for the user: the laws G3 refits, ranked by the evidence, with
    Decision Log 5's bounds, S1 restated from (f)'s map where it must be, put for ruling on what
    the delta measured, before any vitrea render at 0.25 exists.
- **After G1b:**
  - G1b's bridges read;
  - **(c)** the w-test, read once against the prediction hashed in G0 (clause 8);
  - **(d)** the ladder described (clause 9).

  Neither may be amended for anything stage one read: the declaration was hashed before G1a's
  first capture (clause 1).
- Acceptance: clauses 7–9, with an independent review closed at each stage.

### G3: The refit, the seal and the landing (ledger §5.201; §5.202 if split at the seal)

Branches `w43-g3-refit`, then `w43-g3-landing`.
- **The refit,** opened after Decision Logs 5 and 7 are ruled; it does not wait for G1b. In
  order (clause 10):
  1. **The cuts first.** The 0.25 adopted rows Decision Log 5 rules (the per-profile tables, M1,
     C1, X1, L1, M2, E2, and S1 as ruled) are implemented with their baseline selection: the
     pre-fit render (the 0.5 documents rendered on the 0.25 cells, in candidate mode, in
     scratch) is L1's growth baseline and M2's and E2's reference. They run in W42's
     candidate-admission mode and are committed before any candidate is judged.
  2. **The rehearsal.** The cuts run on the pre-fit render and on the first candidate's renders.
     S1 is rehearsed again on real renders, beside G2's perfect-endpoint map. A cut that fails by
     construction goes to the user before fitting continues, as W42's X39 did.
  3. **The fit, in scratch.** The four documents are patched over the unmoved default, naming the
     0.5 leaf set (X44). WebGPU is fitted first; the CSS tier is derived and
     `tier-coherence.test.ts` extended. Every candidate reads in ordinary scratch
     (`--out-matrix`) or in a fresh stage of its own; no fitting read enters a stage that will
     publish, because a stage binds its document hashes.
  4. **The freeze and the final stages.** The four documents are frozen. Then the two
     publication stages, light and dark, are created at those bytes and filled completely with
     every declared non-holdout set on both tiers (`--write-partial`).
  5. **The gate.** Every non-holdout verdict is read on the final stages: the cuts, the owner
     test on the stages' scratch union, `tier-coherence.test.ts`, and the eye sheets by
     stratum. Each one passes, or the user rules each miss explicitly: ship as a named miss,
     or stop. Nothing proceeds on an unruled miss. On a stop, the two stages are left
     unpublished, the fit resumes in scratch, and a later freeze creates new final stages.
  6. **The holdout,** read once per tier into the same stages, last. A holdout miss is recorded,
     never re-read, and put to the user.
  7. **Publication,** once per stage, only after every verdict, holdout included, has passed or
     been ruled. The published bytes are the stages' bytes and never change.

  The goldens stay byte-identical and the 0.5 digests unmoved (clause 11).
- **The landing:**
  - Decision Log 1 executed: the generator and its export test for the 0.25 module, the
    document, `glassTintAmount` on both types, React re-exports, the README rows;
  - the refit's cuts committed as `adopted-thresholds.test.ts` blocks for the four 0.25
    profiles, read on the published rows, with `PREDICATE_EXCLUDES` moved to the machine's
    output and every ruled miss named in the file;
  - X45's sweep of every consumer of the current union, the demo's reduction included;
  - a playground selector and readout, the demo at 0.25 beside the harness capture;
  - the capture tree copied to the canonical path and `check-capture-tree` exit 0 on it (no
    generation is superseded, so nothing moves to `web-captures-superseded/`);
  - eye sheets over the whole canonical bed;
  - CLAUDE.md and the ledger's pointers;
  - the changeset and the c9d chain.
- Acceptance: clauses 10–14; independent review closed; `pnpm release` is the user's, and the
  tag follows.

## Cross-Child Contracts

**Carried:**
- **X1:** the 26.5 evidence frozen; the freeze at 1,818; `DEFAULT_MATERIAL_PROFILE` unmoved.
- **X2 and X6:** attestation before pixels, and the key names every axis that moved a pixel.
- **X3:** measure before moving; G2 changes nothing; G3 changes nothing G2 did not name.
- **X4′:** the side bundle is not rebuilt, and nothing is added to Screen Recording under either
  bundle identifier except the user's restore of the original at G1b's close.
- **Holdout and bounds:** the holdout is read once per frozen configuration, and bounds are
  declared before reads.
- **X7:** one capture process at a time, and no browser during a native pass.
- **X21 (W39) and X31 (W41):** one-sided censoring of channels at 250 and above or 5 and below,
  and the three closure statuses, in the w-test.
- **X24:** archives complete and cited by SHA-256 and bytes.
- **X38:** dump numbers are pointers.
- **X33 (W42):** the landing referees pass, or their misses are ruled, before the exposure
  (clause 10).
- **Workers:** every worker runs on `opus`; reviews go through the review-code agents, with
  `doperpowers:adversarial-reviewer` for this charter. The rule is passed to workers that
  dispatch workers.
- **Browser:** a pinned Playwright CLI and Chromium for G3's reads, with a fresh X6 check before
  each launch.
- **Committed evidence** is never rewritten; corrections sit beside it.
- **Merges** are `--no-ff -F <file>` with the freeze verified; commits use path-scoped `git add`
  and carry no attribution trailers or session URLs.

**X5′ — the capture authorisation.** The user's lift authorises native capture, in G1a and
G1b only, for exactly:
- the four canonical `-glass0.25` standard keys (G1a);
- the wave-local probe and ladder scenes file (G1b);
- the 0.5 bridge cells, which go into scratch and the archive and are never filed (both).

No accessibility key, no 0.5 key and no 26.5 key is filed. The lift ends at G1b's close, or at
G1b's cancellation.

**New:**
- **X41 — the 0.5 generation is frozen.** Its fixtures, profile documents, generated module and
  generation files do not change by a byte. The default document's optical content, endpoint
  identities and CSS mapping do not change; only Decision Log 1's `glassTintAmount: 0.5` readout
  is added. G0's manifest checks both, at every merge.
- **X42 — the slider is attested twice.** The run reads the defaults domain, and the dump
  sentinel reads the tree's Normal input. Either reading off the pass's declared position
  refuses the pass. The as-found value is recorded and restored on every exit path.
- **X43 — one bundle for every W43 pixel, and bridges before claims.** The side bundle captures
  everything. The 0.25 fixtures name it. No 0.25-against-0.5 claim is stated for a cell type no
  bridge covered.
- **X44 — one leaf space.** The 0.25 documents name exactly the 0.5 documents' leaves; no
  operator is added and the identity table does not move. So the two documents are points in
  one space, and the 0.5 digests and goldens cannot move.
- **X45 — every consumer of the current union names the glass position it reads:** the demo's
  reduction and figures, `adopted-thresholds.test.ts`'s populations, the calibration page's
  strict and candidate modes (G0 (f)), `check-capture-tree`, and the native delta driver. A
  consumer that would silently mix positions is a defect.
- **X46 — W42 is not reopened.** H is never requested, and `w42-g2-impl` and
  `w42-g2-identification` are not built on. The w-test reads only the probe and W42's
  calibration and validation counterparts.
- **X47 — a cut sitting drops from the bottom of its own order.** A dropped block is recorded
  with its cause and is not captured later without a new ruling. Everything G1b captures is
  declared and hashed in G0, before G1a: nothing G1a or G2's first stage shows can change G1b's
  cells or the w-test's prediction.

## Ordering & Dependency Map

1. Decision Logs 1 and 3 ruled by the user, 2 and 4 by the parent (2026-10-01); this draft's
   adversarial review.
2. G0:
   - the manifests;
   - the bridge on existing evidence;
   - memo F, after the user's go for the dump window;
   - the tooling and the selection seam;
   - the declaration, rehearsed and hashed;
   - review and merge.
3. The parent tells the user, with G1a's length.
4. G1a: the user's X5′ lift and go; opening bridges, the canonical bed at both scales, closing
   bridges; publication, the archive and the bar.
5. G2, first stage: G1a's bridges, the native delta, the Decision Log 7 draft with Decision
   Log 5's bounds; the user rules both.
6. Two tracks from here, independent:
   - **the product:** G3: bounds declared, then the refit, the holdout once, and publication;
     the landing, the c9d chain, and the user's `pnpm release`;
   - **the evidence:** G1b on a later day (opening bridges, the probe, the ladder, closing
     bridges, the restore and positive check, the archive and the bar), then G2's second stage
     (G1b's bridges, the w-test, the ladder).
7. Close, when both tracks have closed and the original bundle is restored.

## Risks & Mitigations

- **The shipped body form cannot carry the 0.25 body.** By the declared constants, the 0.25 body
  is more one-sided than the 0.5 one, and the shipped form is two-sided (Design). Mitigation:
  - the prediction is written before the read;
  - X3 and X44 keep the refit honest;
  - misses are named and go to Decision Log 5 (e);
  - the structure wave, which the ladder feeds, is the route that closes them.
- **A bridge fails:** the bundles differ on canonical cells, or the machine has drifted since
  2026-09-18. Mitigation: G0 reads W42's family F before anything is declared; G1a's opening
  bridge stops it before the first 0.25 capture. The user then rules between capturing
  the canonical bed through the original bundle (two more grant swaps) and recapturing a 0.5
  control through the side.
- **macOS updates.** A 27.0.x or 27.1 build before or during either sitting is a new reference:
  the gate refuses any build but 26A428, and the wave stops for the user. Mitigation: the user
  defers updates until G1b closes (Decision Log 3).
- **The slider does not reach a run** (a stale preference), or is left moved after a crash.
  Mitigation: the dump sentinel's tree check (X42), the orchestrator's trap, and the read-back at
  each sitting's close.
- **Stops from focus, input or the census** (W39 and W42; Grounding). Mitigation:
  - the four tracker fixes in G0;
  - the memory lesson's procedures;
  - the user's prerequisites in Decision Log 3, including Universal Control off, browser
    automation held in other sessions, the cua helper quit, and no chat from the capture Mac;
  - concurrent workers given the census pattern and barred from whole-package suites.
- **The gap between the sittings.** Three things can happen between G1a and G1b: a macOS
  update, a change to the side bundle or the machine, or G1b slipping indefinitely while the
  original bundle stays unrestored. Mitigation: G1b's opening bridges and gates refuse a changed
  build, pin or frame before any capture away from 0.5; the user defers updates until G1b
  closes; nothing before G1b needs the original bundle; and if G1b is cancelled, the restore
  happens then (clause 6).
- **The w-test fails for a reason other than w.** C or W could move with x, or T be flat where it
  is inverted. Mitigation: memo F reads the tree first; the support needs monotone T, a minimum
  slope and a minimum contrast; the statistic is rehearsed on synthetic renders and on W42's
  cells before the hash; its numbers are recorded either way.
- **The selection seam** (Surprises 1) would read the 0.25 material over 0.5's recede and CSS
  crossing. Mitigation: G0 (f) and X45, each with a red case.
- **Mixing positions in the current union.** Mitigation: X45's sweep in G3, and the demo's
  figures pinned by its own test.
- **The archive's size.** 3,934 canonical captures are far more than W42's crops. Mitigation:
  frame deduplication by SHA-256 (G0 (d)) under the 2 GiB asset limit, with the canonical frames
  committed as fixtures as at W29.
- **A cost or API regression at landing.** Mitigation: the export surface pinned, the c9d chain,
  and the renderer bench read beside the goldens.

## Deferred / Out of Scope

- **Accessibility at 0.25** (reduced transparency, increased contrast alone or coupled; Decision
  Log 2 (b), ADOPTED). The 0.25 documents carry the 0.5 accessibility leaves, recorded as
  unmeasured.
- **Other slider positions as full generations** (0 or 1 as "clearest" and "most tinted"
  documents). The ladder makes them cheap to evaluate, but not cheap to ship: each is a
  canonical bed.
- **A continuous slider** (Decision Log 1 (c)). It needs the ladder's reading and either a law in
  x or more generations. It also needs a live setter, since the root reads its document once.
- **The body law.** W42's Deferred at close 1–7 carry to the next structure wave, now with W43's
  ladder ends, w-test verdict and memo F beside `w42-archive` and its sealed H.
- **Reading the user's real setting.** No web API exposes it; only a desktop shell could.
- **Out of scope:** Show Borders; dark and 2x accessibility; Apple's `Glass.clear` variant at
  macOS 27; iOS and iPadOS.
- **The SDK-gating inactive arm** (tracker). It needs the 27-SDK side bundle, which is a different
  identity from W39's.

## Tracking Map

| child | status | ledger |
| --- | --- | --- |
| G0 | NOT STARTED; waits on this draft's review | §5.198 |
| G1a | NOT STARTED | §5.199 |
| G1b | NOT STARTED | §5.199b |
| G2 | NOT STARTED; two stages, after G1a and after G1b | §5.200 |
| G3 | NOT STARTED | §5.201 (§5.202 if split) |

## Decision Log

### Decision Log 1 — RULED 2026-10-01 (the user): a second fixed setting

**RULED 2026-10-01 by the user: "Second fixed setting (Recommended)"**, the option reading: "A
second set of material documents for the 0.25 position, chosen through the existing
materialProfileDocument option; the default stays 0.5. The runtime reports which slider position
drew (a new glassTintAmount field). A continuous slider waits until more positions are
measured." G3 executes option (a) below. The ruling names no export; the drafted name,
`macos27Glass025MaterialProfileDocument`, follows the recommendation to name by measurement and
never by "clear", and the review may propose another.

*The draft, as it was put to the user:*

**The question.** What a developer gets from a 0.25 material, how a page selects it, and how the
runtime says what drew.

**Options.**
- **(a) A second discrete document.** `macos27Glass025MaterialProfileDocument`, exported beside
  `macos27MaterialProfileDocument`, through the existing `materialProfileDocument` option and
  React prop. `glassTintAmount` is added to the document and to `ResolvedMaterialDocument`. The
  default stays 0.5, Apple's own and what an untouched Mac draws. *Costs:* two positions only;
  an app that knows its user's setting snaps to the nearer of the two.
- **(b) A `glassTintAmount` option on the root** that picks the measured document at that
  position and refuses others. The name is ready for a continuous future. *Costs:*
  - a second selection path that can contradict the first: macOS 26.5 has no slider, and an
    explicit document may name another position;
  - a numeric option that accepts two values invites the reading that the rest are supported.
- **(c) A continuous parameter**, interpolating between measured documents. With two measured
  points it would draw positions nobody measured, and the honesty core would have to say
  "interpolated". The [0.5, 1] segment has different declared slopes from [0, 0.5], so 0.25 and
  0.5 cannot even bound it.

**Recommendation: (a).** It adds no selection path, every number it ships was measured, and the
honesty core already names the document, endpoint and digest; one field makes the position
readable. It also repeats how macOS 26.5 and 27 already coexist.

(b) is the better pick only if you want the API name settled now and expect the continuous
version within a wave or two. (c) becomes right when desktop shells that can read the real
setting are an audience you care about, and after the ladder and a structure wave have said
what form it takes.

Naming is yours too. The recommendation is to name by measurement and never by "clear", which
collides with `variant: "clear"` (Apple's `Glass.clear`).

### Decision Log 2 — ADOPTED 2026-10-01 (the parent, under the user's Decision Log 3 ruling): the capture scope as recommended

**Adopted.** The user's sitting ruling fixes (a), (c), (d) and (e): "the full 0.25 bed at 7 runs
per scene", then "a small structure probe plus captures at slider 0, 0.75 and 1" in the ~4 h
sitting, which is the three-run probe and ladder as priced. (b), no accessibility pass, and (f),
the side bundle for every pixel, are the draft's recommendations, adopted by the parent as
within that ruling: its option names no accessibility pass, and two sittings through one bundle
keep the user's W42 choice to avoid extra grant swaps. The ruling moves one thing: the original
bundle's restore falls at G1b's close, not at one sitting's end (clause 6). Restoring it at
G1a's close instead would cost two more swaps (re-granting the side for G1b and restoring
again). The review or the user may reopen (b) or (f).

*The draft, as it was put:*


- **(a) Profiles.** *Recommended:* the four standard keys in full, at both scales and both poses
  (562 cells a round). This is the 0.5 bed's exact mirror and every gated population. *Smaller
  options:*
  - the gated sets only, about 214 cells a round, about 6.4 h less: this loses the probe rows X1
    and E2 read, and the pitch series the scatter refit needs;
  - 2x only, about 5.2 h less: this loses every 1x gate.
- **(b) Accessibility.** *Recommended:* none captured; the 0.5 leaves are carried, recorded as
  unmeasured. *Option:* one reduced-transparency dump pair at 0.25 and 0.5 in G0, which needs a
  GUI toggle (cua_repl, with your OK); or full 1x light reduced-transparency passes, about 0.6 h
  at seven runs plus your hand twice.
- **(c) The w-test probe.** *Recommended:* yes, about 28 W42-bed cells per 2x endpoint (Design).
  *Option:* none (about 1 h less), which forgoes the only decisive single-knob test of the body
  law and leaves it to a later sitting that costs two more grant swaps.
- **(d) The ladder.** *Recommended:* yes, at x = 1 and 0 on the probe's cells and x = 0.75 on
  about 10. *Option:* none (about 2.2 h less).
- **(e) Repeats.** *Recommended:* seven for the canonical bed and three for the probe and ladder.
  W42's seven-run bar was the 0.5 floor on all 27,777 of its statistics (§5.195 §4), on this
  bundle and these cell kinds; its two-state rows moved no region median. The probes read region
  medians, so their bar is now a measured property, not an assumption. *Option:* seven
  everywhere, for parity with `w42-archive` (about 4.1 h more).
- **(f) The bundle.** *Recommended:* the side bundle for every pixel, with the restore at the
  end, as you ruled ("Keep it for the next capture"). The bridges make the two-bundle lineage a
  measurement. *Option:* restore the original mid-sitting and capture the canonical bed through
  it. The lineage is then identical to 0.5's, but you would have to come back mid-sitting, and
  the probes still need the side (its bed kinds postdate the original binary), so it costs one
  more swap.

### Decision Log 3 — RULED 2026-10-01 (the user): two sittings

**RULED 2026-10-01 by the user: "Two sittings, 12.4 h + 4 h (Recommended)"**, the option reading:
"First the full 0.25 bed at 7 runs per scene, matching the 0.5 generation's standard (~12.4 h,
e.g. overnight). Later a ~4 h sitting for a small structure probe plus captures at slider 0,
0.75 and 1. That second set directly tests W42's law (the blend weight should track the slider)
and gives positions for a future continuous slider." Executed as G1a and G1b (Children), with
Design's timings: G1a 11.3 h modelled, 12.4 h at the Mac; G1b 3.7 h and 4.0 h. The prerequisites
in the draft below stand for both sittings, with macOS updates deferred until G1b closes and the
original bundle's restore at G1b's close. The memo F window in G0 remains the user's go.

*The draft, as it was put to the user* (the split, its alternative, was re-priced at 12.4 h and
4.0 h before the ruling; the three-run variants priced beside it are in Design):


**The estimate.** About 14.5 h modelled and 5,247 captures, as itemised in Design. At the Mac
that is 15–16 h, depending on whether stops cost what they cost W42 (about 10 %) or W29 (almost
nothing). Separately there is G0's memo F window, about 40 minutes of idle Mac and no grant.

**Recommendation: one sitting, started in the evening.** Your prerequisites:
- lift X5 for W43's beds (X5′);
- leave the Mac idle and chat from another machine;
- keep Universal Control off;
- hold browser automation in every other session;
- quit the cua helper's window;
- defer macOS updates until G1 closes.

Know also that the slider is machine-wide: your Mac draws its glass at 0.25, then 1, 0 and 0.75,
for the sitting's length, and is restored at the end. At the end, you re-add the original bundle
by hand and the parent checks it.

**The alternative:** two sittings split at the product line, the canonical bed (about 12.5 h)
and then the probes (about 3.9 h with their own bridges). Splitting is safe for the evidence,
because each half opens with its own bridges, but it spends a second idle window. It also risks
an OS update between the halves.

### Decision Log 4 — RULED 2026-10-01 (the parent): kept separate

**Ruled by the parent, as recommended: option (a).** The user's Decision Log 3 ruling adopts the
probe and the ladder, in an option that describes them as directly testing W42's law and giving
positions for a future continuous slider. The parent reads that as adopting them as declared
readings (clauses 8 and 9): never an identification, a fit or a landing of a body law in this
wave, and with W42's H and branches untouched (X46).

*The draft:*


**Options.**
- **(a) Separate.** W43 lands the 0.25 generation in the shipped material form and runs the
  w-test as a declared reading. It archives the probe and ladder, and leaves W42's H and branches
  untouched (X46). The next structure wave declares over `w42-archive` and `w43-archive`
  together, with W42's Deferred at close 1–7 stated first.
- **(b) Pursue in W43.** Declare a revised law over both positions and land it in both
  generations. This couples the product to a law that has failed twice. It needs W42's Deferred
  at close 1–3 designed into this sitting's bed (structured cells at s = 80, a span between
  rrect-ml and rrect-lg, black at every span stratum), which means several more hours of sitting
  and a declaration that would delay G0 by a wave's worth of work.
- **(c) Separate, without the probe.** About 1 h less, but the decisive test waits for a later
  sitting and two grant swaps.

**Recommendation: (a).** The 0.25 product can land by the route W29 proved; it should not wait on
an identification. But the capture is the scarce part: the slider, the grant and an idle machine
on build 26A428 come together now. The w-test and the ladder ends are what a structure wave would
most want from this position, and they are cheap. The ladder may matter more than the test: at
x = 1 the body is the wide term alone, which is what W42's U1 and U3 could not separate.

### Decision Log 5 — RULED 2026-10-02 (the user): bounds for the 0.25 documents, (a)–(e) as drafted

**RULED 2026-10-02 by the user: "Adopt all eleven recommendations"**, on G2's Decision Log 7
draft (`packages/calibration/results/2026-10-02-w43-g2-reading/decision-log-7-draft.md`), whose
item 10 put this Decision Log re-instantiated at 0.25 with the native delta's readings beside it
(§5.200). The ruling is that item's recommendation, (a)–(e) below as written, read with these
specifics from the draft:
- **(a)** the four `-glass0.25` standard profiles take the 0.5 standard tables' values per tier,
  declared before G3 reads any 0.25 render;
- **(b)** over the four 0.25 standard profiles, WebGPU tier: M1 at median [0.8, 1.2] and cells
  [0.6, 1.4]; C1 ≤ 0.0042 per bed × span, expected to reproduce its 0.5 readings, so a C1 change
  at 0.25 is a defect and not a fit; X1 at zero pixels above native black, the black branch's
  referee; L1 absolute ≤ 0.055 with growth ≤ 0.005 against the pre-fit render (the 0.5
  documents on the 0.25 cells); M2 **directional** against Apple's 0.25 texture in W42 Decision
  Log 5a's form, its reference that pre-fit render, re-baselined at the adopting gate; E2 per
  cell in absolute codes against the same render (W42 Decision Log 5e's form);
- **(c)** S1 as Decision Log 7 item 11 rules it (R2), read in G3 and adopted only by the user's
  ruling at the landing;
- **(d)** no regression floor;
- **(e)** every non-holdout miss ruled by the user, as a permitted named miss or a stop, before
  the holdout is read and before anything publishes (clause 10).

**Declined:** (e) as "0.25 ships only if every bound holds" (the draft's alternative).

**(e) exercised — RULED 2026-10-02 by the user: "All named misses; proceed to G3 (ii)".** Put to
the user with G3 (i)'s candidate c05 (§5.201 draft), on the list of every non-holdout miss c05
reads on the ruled rows: `packages/calibration/results/2026-10-02-w43-g3-refit/read/misses.md`,
SHA-256 `a7c823226fd834ce765173b2d5e20f3d7c08f16aa77ca2b9fc1ade1150294f0c` (committed at
`a878a068`). Every listed miss is a permitted named miss, recorded with its numbers, and none is a
stop:
- the 17 M2 named misses, each toward Apple's texture and none past it;
- the 62 E2 cells whose edge moved farther from Apple in absolute codes (14 of them rrect-lg);
- the one CSS table row, 1x light `checkerboard__rrect-ml__rest` ssimMean, which the pre-fit render
  already missed;
- S1's 15 WebGPU and 11 CSS wrong-sign cells (S1 is still adopted only at the landing).

The holdout may now be read once per tier after the publication stages reproduce these misses and
no new one. A new miss, or a ruled one that changes character, returns to the user first.

**(e) exercised at the holdout (clause 10 step 6) — RULED 2026-10-02 by the user: "All six named
misses; publish".** The two publication stages reproduced c05's rows and cuts exactly (no new miss,
no ruled miss changed), the holdout was then read once per tier, and six of its table rows missed.
Every one is a permitted named miss, recorded with its numbers, and the stages publish:

| tier | cell | metric | 0.25 | bound | 0.5 | note |
| --- | --- | --- | --- | --- | --- | --- |
| WebGPU 1x light | `checkerboard__rrect-lg__rest` | ssimMean | 0.86409 | ≥ 0.88 | 0.88527 | new at 0.25; the rrect-lg stratum, Decision Log 7 item 9's named gap |
| CSS 1x light | `checkerboard__rrect-lg__rest` | ssimMean | 0.86607 | ≥ 0.9 | 0.88424 | already UNMET at 0.5 (`MISSED_27_ROWS`) |
| CSS 1x light | `checkerboard__glass-over-glass__rest` | ssimMean | 0.86471 | ≥ 0.9 | 0.89539 | already UNMET at 0.5 (`MISSED_27_ROWS`) |
| CSS 1x dark | `photo__rrect-lg__rest` | oklabDeltaEP95 | 0.20600 | ≤ 0.18 | 0.20095 | already UNMET at 0.5 (`MISSED_27_ROWS`) |
| CSS 2x dark | `photo__rrect-lg__rest` | oklabDeltaEP95 | 0.20071 | ≤ 0.19 | 0.19474 | already UNMET at 0.5 (`MISSED_27_ROWS`) |
| CSS 2x light | `checkerboard__glass-over-glass__rest` | ssimMean | 0.91996 | ≥ 0.92 | 0.94071 | new at 0.25; misses by 0.00004, under the resolution the seven-run bed's repeat bar gives a whole-cell SSIM |

The reading is `packages/calibration/results/2026-10-02-w43-g3-refit/stage/holdout-reading.json`;
the holdout is spent for these document bytes and is never re-read (W31 Decision Log 1 (b); the
cross-gate ledger's read 6).

*The draft, as it stood open at charter (2026-10-01):* it was put to the user with G2's Decision
Log 7 draft, on what the native delta measured, and had to be ruled before G3 reads any 0.25
render. The recommendation below is what was ruled.

- **(a)** The four 0.25 standard profiles take the 0.5 standard tables' values per tier, declared
  before G3's read. This follows W29 Decision Log 4, which declared the 27 tables at the 26.5
  values.
- **(b)** The material rows over the 0.25 standard profiles, WebGPU tier:
  - M1, C1 and X1 as defined;
  - L1 absolute ≤ 0.055, with growth ≤ 0.005 against the pre-fit baseline (the 0.5 documents
    rendered on the 0.25 cells);
  - M2 read directionally against Apple's 0.25 texture, its reference that pre-fit render and
    re-baselined at the adopting gate;
  - E2 per cell in absolute codes against the same render.
- **(c)** S1, the slider's direction (Design), read in G3 and adopted only by your ruling at the
  landing. Before this item is ruled, G2 rehearses it on the perfect-endpoint null (G2 (f)): its
  sign clause can fail a 0.25 endpoint that matches Apple exactly, wherever the shipped 0.5
  render already errs in the direction of Apple's change. S1 is put to you as restated from
  that map.
- **(d)** No regression floor: the bed is at seven runs, not seventeen (W29 clause 4).
- **(e)** A missed bound is recorded with its numbers and comes to you as a floor decision. It
  does not by itself stop the landing; W29 landed 0.19.0 with seven UNMET rows. But every
  non-holdout miss must be ruled by you, as a permitted named miss or a stop, before the holdout
  is read and before anything publishes (clause 10). *The alternative:* 0.25 ships only if every
  bound holds.

**Recommendation: (a)–(e) as written.** It holds 0.25 to the bar 0.5 was held to. It adds the
one property per-document bounds cannot see, and reads that property once before gating on it.
And it treats this as W29's kind of landing: a measured material, honestly labelled, with its
gaps named. The prediction that the shipped form misses more at 0.25 (Design) is why (e)
matters.

### Decision Log 6 — the charter's mechanical rulings (the parent's; DRAFTED for the parent)

- Ledger §5.198–§5.201, and §5.202 if G3 splits. G1's split under Decision Log 3 gives G1a
  §5.199 and G1b §5.199b (the §5.159b precedent), so no reserved number moves. Branches and
  evidence directories as listed in Children. Contracts continue from W42's X40 at X41.
- This draft goes to `doperpowers:adversarial-reviewer` before G0. Children are reviewed by the
  review-code agents at medium, and high for G3's seal.
- Every worker runs on `opus`.
- Memo F is a G0 act, not a sitting phase: the w-test's prediction must be stated from it before
  the declaration is hashed. W42 put its dumps first in the sitting because memo D had already
  read the tree.
- The 0.25 documents are patches over `DEFAULT_MATERIAL_PROFILE`, as every shipped material is.
  They are not differences over the 0.5 documents, which would chain two digests.

### Decision Log 7 — RULED 2026-10-02 (the user): what G3 refits at 0.25, the bounds, and S1

**RULED 2026-10-02 by the user: "Adopt all eleven recommendations"**, on G2's draft
(`packages/calibration/results/2026-10-02-w43-g2-reading/decision-log-7-draft.md`, §5.200 §6),
written before any vitrea render at 0.25 existed. The ruling is each item's recommendation; each
item's alternative is recorded as declined. The draft is kept as written, with a dated note
beside it. G3's refit (clause 10; G3 steps 1–3) executes these items, in this order:

1. **The light body's level and tone are refit first, in both light documents.** Leaves:
   `backdropToneResponseThin` and `…Thick` with `backdropToneAnchorX` held,
   `optics.regular.tintAlpha`, and the black branch's `backdropToneBlackThin` and `…Thick`; the
   light receded document refits its own patch of the same families. *Declined:* tone only,
   holding `tintAlpha`.
2. **The scatter is refit second, in all four documents:** the `sizeScatter…` family (gain,
   floor, ramp starts, heavy tap and share, `sizeScatterScaleGain`) and `blurSigma`.
   *Declined:* hold the scatter and let M2 name the texture misses.
3. **In the dark documents only `backdropToneResponseThick` (active and receded) and the
   scatter move;** the thin ordinates, the black branch, `tintAlpha` and `bodyChromaRetention`
   hold their 0.5 values. *Declined:* refit all four dark tone ordinates jointly.
4. **`bodyChromaRetention` moves in the two light documents only, and only after items 1–2,**
   if the first candidate misses M1. *Declined:* hold it everywhere and name the residual.
5. **`tintShadeLight` / `…Dark` hold unless the first candidate misses** the tint cells (the
   light receded tint is the one Apple moved, −0.025 OKLab L). *Declined:* refit
   `tintShadeLight` in the light receded document from the start.
6. **Every rim and highlight leaf holds.** G3 checks that the light active rim excess follows
   Apple's −0.0037 and names the residual if it does not. *Declined:* refit `rimAlpha` /
   `rimLevelGain` in the light active document.
7. **Every `outerShadow` leaf holds in all four documents, the receded zeros included;** C1
   carries over at its 0.5 values. The draft named no sound alternative for the field.
8. **The receded 0.25 documents are each a difference over its own scheme's 0.25 active
   document:** the light one refit (items 1, 4, 5), the dark one carrying the 0.5 receded
   difference except where items 2–3 move it. *Declined:* carry both 0.5 receded differences
   unchanged over the new active documents.
9. **rrect-lg stays in the fit and the gate as its own stratum,** with its exterior edge (up to
   112 codes on structured backdrops, the capture-scale step no leaf models under X44) a named
   gap. *Declined:* keep rrect-lg out of the fit objective and in the gate.
10. **Decision Log 5 re-instantiated at 0.25, (a)–(e)** as Decision Log 5 above records.
    *Declined:* (e) as "0.25 ships only if every bound holds".
11. **S1 restated as R2.** Over the non-holdout standard cells where Apple's change exceeds both
    its bar and the shipped 0.5 render's own error there (|ΔA| > |e₀.₅|), vitrea's change has
    Apple's sign on every cell, and the median ratio of vitrea's change to Apple's, pooled over
    the four profiles per tier, lies in [0.8, 1.2]; per-profile medians are reported, not gated.
    It reads `interiorMean` off the rows. Its population is fixed in
    `results/2026-10-02-w43-g2-reading/s1/r2-population.json` (183 WebGPU and 125 CSS cells), so
    no candidate can choose it, and it is adopted only by the user's ruling at the landing
    (Decision Log 5 (c)). *Declined:* R1 (|e₀.₅| ≤ 0.2|ΔA|), and the mask-free `bodyLevel` in
    place of `interiorMean`.

Whatever was ruled, the draft put one act first: G3 renders the 0.5 documents on the 0.25 cells
in candidate mode, in scratch (a cross-position read, stamped), as the pre-fit baseline L1, M2
and E2 read against, and checks items 5–8's "hold unless" conditions on it before fitting
anything. The draft also leaves undecided what this ruling does not reach: the w-test and the
ladder (G2's second stage), any law form (X44 holds the 0.5 leaf set), and the accessibility
leaves, which carry over unmeasured (Decision Log 2 (b)).

## Surprises & Discoveries

Found while drafting (2026-10-01):

1. **The calibration page selects a shipped document by its OS token alone.**
   `packages/calibration/web/scene.ts:691–705` takes the first shipped document whose `platform`
   is `macOS 27.0`. Once a 0.25 document ships, that is still the 0.5 one. A 0.25 read posed by
   the runtime would then recede with the 0.5 document's receded endpoint, and take the 0.5 CSS
   crossing unless the driver injected another. That is the "one seam" defect W29 G4 closed
   (`material-document.ts`'s header), one axis further on. G0 (f) and X45 close it before
   anything reads at 0.25.
2. **The key grammar, `materialize` and the publisher already carry a second slider position.**
   Only the two sitting scripts hard-code 0.5 (Grounding).
3. **The slider's ends separate the two terms W42 had to fit jointly**, if Apple's declared
   composite is what draws. At x = 1, M = W on both sides; at x = 0 the free side is C. W42's
   Deferred list noted that "dumps and captures at slider 0 and 1 would isolate the
   normal-weighted wide term" (memo D §7d) as the user's call. This wave makes it a planned
   reading. A pointer until the pixels agree (X38).
4. **A page chooses its material once.** `createGlassRoot` reads the document at construction
   (`root.ts:935`), so switching between 0.5 and 0.25 is a remount.
5. **"Clear" is taken.** `variant: "clear"` is Apple's `Glass.clear` in `core/src/material.ts`.

## Revision Notes

- 2026-10-02 (G3's first commit, on branch `w43-g3-refit`): the user's ruling of Decision Logs 5
  and 7, "Adopt all eleven recommendations", folded as RULED. Decision Log 7 is added at the tail
  with the draft's eleven recommendations as the ruling and each alternative recorded as
  declined; Decision Log 5 is marked RULED with the draft's item 10 readings; the Decisions
  table and the status follow. The draft itself is unchanged, with
  `decision-log-7-RULED-2026-10-02.md` beside it. Nothing else in the charter moves.
- 2026-10-01 (v1.2; the adversarial review of `689c3f31`, needs-attention, one P1 and three P2,
  every finding accepted by the parent and folded in place):
  - **[P1] Gate before holdout and publication.** v1.1 froze, read the holdout and published,
    and added the 0.25 adopted blocks only at the landing; nothing required the non-holdout
    verdicts to pass, or their misses to be ruled, before the exposure. That dropped W42's
    protection (its Deferred at close 7; X33). Clause 10 and G3's refit now run in order: the
    cuts and their baseline selection implemented first; rehearsed on the pre-fit and candidate
    renders; the fit; the freeze; every non-holdout verdict passed or each miss ruled by the user;
    then the holdout; then publication. Decision Log 5 (e) keeps the user's option to ship named
    misses. S1 gains a rehearsal before Decision Log 5 is ruled (G2 (f); Design; Decision Log 5
    (c)), because its per-cell sign clause can fail an exact 0.25 endpoint wherever the shipped
    0.5 render already errs in the direction of Apple's change.
  - **[P2] Candidate selection path.** v1.1's strict (OS, glass) selection would refuse an
    unshipped `-glass0.25` candidate, and the page selected a shipped document before applying
    the injected patch. G0 (f) now declares two modes: strict for shipped reads, and a candidate
    mode that builds a complete four-endpoint candidate document with its own CSS mapping over
    the unmoved default, independent of the shipped registry. G0 proves it before any 0.25
    shipped export: a 0.5-content candidate renders byte-identical to shipped 0.5 on all four
    endpoints and both tiers, and every refusal case has a red case. X45 names both modes.
  - **[P2] Fitting scratch against publication stages.** A stage binds its document hashes and
    refuses later edits, so v1.1's "fit and read in one light and one dark stage" could not
    work. Fitting now reads in ordinary scratch or fresh stages per candidate. The two final
    publication stages are created only after the four documents are frozen and filled
    completely, holdout last, and only they publish.
  - **[P2] The 0.5 manifest against the ruled readout.** v1.1's byte protection of
    `material-document.ts`'s 0.5 block conflicted with adding `glassTintAmount: 0.5`. G0 (a) and
    X41 now protect a projection of the default document (optical content, endpoint identities,
    CSS mapping) and permit only that readout; the fixtures, profile documents, generated module
    and generation files keep their byte protection.
  - **The review's confirmation kept as a G0 tooling requirement:** `defaults write` takes effect
    only for a freshly launched harness, so a harness or dump process alive across a slider write
    refuses the pass (G0 (d)).
- 2026-10-01 (v1.1, for adversarial review). The user ruled Decision Logs 1 ("Second fixed
  setting (Recommended)") and 3 ("Two sittings, 12.4 h + 4 h (Recommended)"), quoted verbatim
  with their option text. The parent ruled Decision Log 4 (kept separate; the probe and ladder
  are declared readings) and adopted Decision Log 2 under the sitting ruling. Decision Log 5
  stays open for G2's reading. Changes:
  - G1 becomes G1a, the generation (§5.199), and G1b, the probe and ladder (§5.199b);
  - Design's sitting section becomes "The two sittings", with each sitting's order, bridges and
    priced timing, and the variants priced for the decision recorded beside them (one sitting,
    three-run canonical bed with and without probes, everything at seven runs), with what a
    three-run bed can and cannot establish;
  - G2 reads in two stages, so G3 does not wait for G1b;
  - the original bundle's restore moves to G1b's close (clause 6);
  - clauses 1 and 3–6, X5′, X47, the ordering map, the risks (the gap between the sittings
    replaces the long sitting) and the tracking map follow.
- 2026-10-01 (v1, drafted for the parent). Chartered from:
  - W42's close: Decision Log 8, Deferred at close 7–10, §5.196 and §5.197;
  - W29's charter and record: Decision Log 3 (a), §5.149 §4, G1's `sitting.md`;
  - W42 G0's timing model and G1's sitting record (§5.195);
  - the memory lessons on sittings, survival bars and improvement rules;
  - a read of the runtime's selection seam and the calibration and publication code.

  Five decisions open for the user, a sixth drafted for the parent, and an adversarial review
  requested before G0.
