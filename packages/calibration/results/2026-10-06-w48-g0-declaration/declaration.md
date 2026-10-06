# W48 G0, part 1: the declaration

Charter `docs/doperpowers/specs/2026-10-06-w48-dark-operators-fit.md@78d0211e0`. Every item below is checked by `declare.py check` against its pinned sources (`declaration.json`); this twin is its readable form.

### documents

**the starting point is four document snapshots (X62), at this charter's merge** (clause 2; X62)

The dark and light 0.25 document bodies at the charter's merge 78d0211e0, each verified against its hash and its bytes there, and equal to W47's snapshots byte for byte (no 0.25 document moved since c1f9bf84c). Every W48 tool builds from these and refuses the live profiles/ as a start.

```json
{
 "files": {
  "active.light": "ebc3d9105a4a",
  "active.dark": "d0219cd684bf",
  "receded.light": "12712d534b78",
  "receded.dark": "f0b36a71772a"
 },
 "digests": {
  "active.dark": "b074fc6913a91c66",
  "receded.dark": "280f0fddf014e0f6",
  "active.light": "3741b22934f17f4d",
  "receded.light": "c4ca0e1cd6791bde"
 },
 "commit": "78d0211e0"
}
```

### t1

**T1 as gated, its shared arithmetic, and its dark population** (clause 2; Decision Log 1)

T1 is GATED on the dark 0.25 profiles since W46 G2 against d0219cd684bf (§5.210); its statistic, bar and arithmetic unchanged (W44 G1's t1.py by path, pinned). G2 re-baselines it in the five-part order with the separate dark authorised list.

```json
{
 "populationPerDarkProfile": {
  "cells": 77,
  "F": 15,
  "T": 4,
  "C": 46,
  "P": 12,
  "gate": 66,
  "holdout": 5,
  "referee": 6
 },
 "strata": {
  "F": [
   "checkerboard-4",
   "checkerboard-8"
  ],
  "T": [
   "hc-text-7"
  ],
  "C": [
   "checkerboard",
   "checkerboard-lc16",
   "checkerboard-32",
   "checkerboard-64",
   "hc-text",
   "hc-text-28",
   "impulse"
  ],
  "P": [
   "photo"
  ]
 },
 "ratioClause": 0.1,
 "equalTolerance": 1e-12,
 "ownerTest": "packages/calibration/test/adopted-thresholds.test.ts@78d0211e0",
 "ownerNeedles": [
  "const T1_DARK_GATED_PROFILES = [\n  \"apple-macos-27.0-1x-dark-standard-glass0.25\",\n  \"apple-macos-27.0-2x-dark-standard-glass0.25\",",
  "const T1_DARK_REFERENCE = { active: \"d0219cd684bf\", receded: \"f0b36a71772a\" } as const;",
  "sha256: \"0eb8ef7712adc0f7de53290190ab1b5d903d61806cc2039de0e99fb78de4c2cf\""
 ]
}
```

### bar

**the bar: 0.5 code on every dark cell** (clause 2; Decision Log 1)

W44 G0's measurement: 77 cells per dark scale, the seven runs pixel-identical, bar = half a code.

```json
{
 "darkCells": 154,
 "maxSeparation": 0.0
}
```

### manifest

**W46's referee manifest, by hash (X69)** (clause 5; X69; Decision Log 1)

w46-referees-1 loaded by its SHA-256 through W47's X69 loader (inherited by path); W46's adapter, given only W46's frozen ladder list, still reproduces it; the six referee and seven holdout scenes per dark scale are withheld from every fit, stage, gate read and sheet.

```json
{
 "schema": "w46-referees-1",
 "scenes": [
  "checkerboard-8__rrect-sm__rest",
  "checkerboard-8__rrect-ml__rest",
  "checkerboard-4__rrect-md__inactive",
  "checkerboard-32__rrect-ml__rest",
  "checkerboard-32__rrect-lg__inactive",
  "hc-text-7__rrect-md__inactive"
 ],
 "profiles": [
  "apple-macos-27.0-1x-dark-standard-glass0.25",
  "apple-macos-27.0-2x-dark-standard-glass0.25"
 ],
 "sha256": "0eb8ef7712adc0f7de53290190ab1b5d903d61806cc2039de0e99fb78de4c2cf",
 "pregateProbe": {
  "count": 81,
  "listSha256": "91e76b666fe5d1bbec3defba7cd3c5a11f549822e4b2a3612dd2ce8d699c2f46"
 },
 "exposure": {
  "count": 13,
  "listSha256": "3172866644397e984e6ef0ecdf18b986e6b17713a8462122c2a1a87306b4b7a1"
 }
}
```

### rule

**the landing rule, its synthetic cases and its rehearsal** (clause 4; Decision Log 1)

W45's growth-only rule as W46 and W47 bound it, W47's cuts/rule.py inherited by path: d0219cd684bf, bar 0.5, per dark profile, the verdict the weaker profile's. Rehearsed under W48's bindings on d0219cd684bf against itself and on W46's point A by its committed gate cut (§5.209 §4 and §5.211 §6 reproduced); the gated groups per scale the charter's.

```json
{
 "constants": {
  "budgetCount": 3,
  "budgetCeilingB": 3.0,
  "gatingMinCells": 3
 },
 "targets": {
  "P": [
   "P rest",
   "P inactive"
  ],
  "C rest": [
   "C rest"
  ],
  "F inactive": [
   "F inactive"
  ]
 },
 "reference": "d0219cd684bf",
 "syntheticCases": 19,
 "rehearsal": {
  "published d0219cd684bf against itself (W47's cuts, canonical captures)": [
   "NEITHER: closes at the finding",
   [
    66,
    0,
    0
   ],
   [
    66,
    0,
    0
   ]
  ],
  "W46's point A (d-s2-rta0.8-rs214-rfa0.5-rh10.25-re20.04-rk10.15-rk20.04-rn10.4-rn20.4-rg0) against d0219cd684bf, W46 G1's committed gate cut read by W47's rule": [
   "NEITHER: closes at the finding",
   [
    10,
    16,
    8
   ],
   [
    9,
    17,
    10
   ]
  ]
 }
}
```

### tools

**W48's tools, W47's inherited by path, their tests on d0219cd684bf** (clause 2)

W48's own tools (bindings, inherit, the archive and replay, the census and launcher copies, the builder and seal copies, declare and assemble, the verdict reader) with their tests; W47's cuts, fit, stage, sheets, referees, level and ladder reader inherited BY PATH under W48's bindings, pinned byte-identical, their tests re-run under W48's bindings; X60 by evidence.

```json
{
 "tests": [
  [
   "test_archive",
   "archive",
   10
  ],
  [
   "test_build_candidate",
   "fit",
   24
  ],
  [
   "test_fit",
   "fit",
   46
  ],
  [
   "test_stage_sizes",
   "fit",
   6
  ],
  [
   "test_verdicts",
   "ladders",
   21
  ],
  [
   "test_level",
   "level",
   14
  ],
  [
   "test_x69_x70",
   "referees",
   6
  ],
  [
   "test_seal",
   "seal",
   18
  ],
  [
   "test_stage",
   "stage",
   14
  ],
  [
   "test_bindings",
   ".",
   20
  ],
  [
   "test_declare",
   ".",
   24
  ],
  [
   "test_run_inherited",
   "tools",
   3
  ],
  [
   "test_ts_copies",
   "tools",
   5
  ]
 ],
 "inheritedTests": [
  [
   "cuts/test_cuts_refusals.py",
   11
  ],
  [
   "cuts/test_rule.py",
   19
  ],
  [
   "referees/test_referees.py",
   11
  ],
  [
   "sheets/test_sheets.py",
   7
  ],
  [
   "stage/test_x60.py",
   11
  ]
 ],
 "inherited": [
  "packages/calibration/results/2026-10-06-w47-g0-operators/cuts/bed.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/cuts/cuts.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/cuts/rule.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/fit/finding.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/fit/fit.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/fit/joint.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/fit/labels.json",
  "packages/calibration/results/2026-10-06-w47-g0-operators/fit/recover.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/fit/search.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/ladders/ladder.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/ladders/part2.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/ladders/read.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/level/arith.ts",
  "packages/calibration/results/2026-10-06-w47-g0-operators/level/level.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/referees/referees.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/rehearsal/port-proof.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/rehearsal/rehearse.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/sheets/sheets.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/stage/stage.py",
  "packages/calibration/results/2026-10-06-w47-g0-operators/stage/x60.py"
 ]
}
```

### level

**the level check (X61), re-bound; the shipped rung's identity re-proven** (G0 (b); X61)

W47's level check, inherited by path, knowing operator 1's per-pixel alpha. The shipped rung's identity is W47's committed record (130 of 130, reads no change), re-proven against the archive's d0219cd684bf reference subset; its unexplained excesses are read beside L1, ungated.

```json
{
 "identity": [
  "IDENTICAL",
  130,
  130,
  true
 ],
 "projection": "every field but capturedAt, key.web.capturePath",
 "reproof": "REPRODUCED"
}
```

### operators

**the two operators are W47's bytes (clause 1)** (clause 1; X65, X66, X68)

Operator 1 (tintAlphaFar1x / 2x) and operator 2 (sizeFineTapShare with its two widths, the body form) as W47's part 1 states them (2d4a2c7f…, its operators item verbatim), landed inert on main at 429d0a78; every runtime file and identity-table test byte-identical to this charter's merge. Any runtime byte that moves before G1's freeze closes the child.

```json
{
 "w47PartOne": {
  "sha256": "2d4a2c7f73b5a0708c1e80ff06b64043657b0f7fafe3c05c3393da84d769c30e",
  "supersedes": "2d6d49ad7af5dc9190227ba02f57e3eb9681a85f31890f127e6c08c621103579"
 },
 "w47Operators": {
  "operator 1": {
   "leaves": [
    "tintAlphaFar1x",
    "tintAlphaFar2x"
   ],
   "slots": [
    "active.dark",
    "receded.dark"
   ],
   "domains": {
    "active.dark": {
     "tintAlphaFar1x": [
      [
       "interval",
       0,
       0.6
      ]
     ],
     "tintAlphaFar2x": [
      [
       "interval",
       0,
       0.6
      ]
     ]
    },
    "receded.dark": {
     "tintAlphaFar1x": [
      [
       "interval",
       0,
       0.6
      ]
     ],
     "tintAlphaFar2x": [
      [
       "interval",
       0,
       0.6
      ]
     ]
    }
   },
   "law": "farS = smoothstep(sizeSpanMax, sizeScatterSpanMax(dpr), span); alphaBase = clamp(tintAlpha + rampAtScale(tintAlphaFar1x, tintAlphaFar2x, dpr)·farS, 0, 1); sizedAlpha = alphaBase + sizeOcclusionGain·sizeK·(1 − alphaBase), per pixel on the WebGPU tier, per surface on the CSS tier (X65: mirrored)",
   "identity": "two plain value drops in MATERIAL_IDENTITY_TABLE, each at 0 (no gate leaf)",
   "grid": {
    "tintAlphaFar1x": [
     0,
     0.1,
     0.2,
     0.3,
     0.45,
     0.6
    ],
    "tintAlphaFar2x": [
     0,
     0.1,
     0.2,
     0.3,
     0.45,
     0.6
    ],
    "optics.regular.tintAlpha": [
     0.7,
     0.8,
     0.9
    ],
    "sizeOcclusionGain": [
     0.05,
     0.2,
     0.4,
     0.6
    ],
    "sizeScatterSpanMax": [
     128,
     160,
     192,
     256
    ],
    "sizeScatterSpanMax2x": [
     128,
     160,
     192,
     256
    ]
   },
   "units": {
    "tintAlphaFar1x": "alpha per unit of farS",
    "tintAlphaFar2x": "alpha per unit of farS",
    "optics.regular.tintAlpha": "alpha",
    "sizeOcclusionGain": "share of (1 − alpha) at sizeK 1",
    "sizeScatterSpanMax": "CSS px (span)",
    "sizeScatterSpanMax2x": "CSS px (span)"
   }
  },
  "operator 2": {
   "leaves": [
    "sizeFineTapShare",
    "sizeFineTapSigma",
    "sizeFineTapSigma2x"
   ],
   "slots": [
    "receded.dark"
   ],
   "domains": {
    "active.dark": {},
    "receded.dark": {
     "sizeFineTapShare": [
      [
       "interval",
       0,
       1
      ]
     ],
     "sizeFineTapSigma": [
      [
       "set",
       [
        0
       ]
      ],
      [
       "interval",
       1.5,
       6
      ]
     ],
     "sizeFineTapSigma2x": [
      [
       "set",
       [
        0
       ]
      ],
      [
       "interval",
       1.5,
       6
      ]
     ]
    }
   },
   "law": "receded-only by document (X66): in the form G0 (f) chose — body: bodySample' = bodySample + sizeFineTapShare·(fineSample − bodySample), fineSample the source blurred at sizeFineTapSigma(dpr) CSS px; deep: scatterColour' = scatterColour + sizeFineTapShare·(deepFine − scatterColour), deepFine at √(σdeep² + sizeFineTapSigma(dpr)²); interior = mix(·, ·, kScatter); the CSS tier declines it",
   "identity": "one gate-group in MATERIAL_IDENTITY_TABLE: gate { sizeFineTapShare: 0 }, gated [sizeFineTapSigma, sizeFineTapSigma2x]",
   "grid": {
    "sizeFineTapSigma": [
     1.5,
     2,
     3,
     4,
     6
    ],
    "sizeFineTapSigma2x": [
     1.5,
     2,
     3,
     4,
     6
    ],
    "sizeFineTapShare": [
     0.25,
     0.5,
     0.75,
     1
    ],
    "optics.regular.blurSigma": [
     1.25,
     2,
     3,
     4
    ]
   },
   "units": {
    "sizeFineTapSigma": "CSS px",
    "sizeFineTapSigma2x": "CSS px",
    "sizeFineTapShare": "share of the chosen component",
    "optics.regular.blurSigma": "device px (receded difference only)"
   }
  },
  "clause1Evidence": {
   "packages/renderer-webgpu/e2e/gpu/w47-alpha-far.spec.ts": "c6d3ed87634c11fea8728a385059628787d7191b7f30bb8ebadb4e478b8ada6c",
   "packages/renderer-webgpu/e2e/gpu/w47-fine-tap.spec.ts": "51a82527451ca87c9b2910f525ae464fcb9329f9ef574c4e93d463a315b6c05d",
   "packages/renderer-webgpu/e2e/fixtures/scenes.ts": "7c
```

### evidence

**W47's ladder evidence, archived, replayed and pinned (X71)** (G0 (a); X71; Decision Log 2)

The ladder tree, the drive's logs and the canonical d0219cd684bf reference subset as release w47-ladders-archive by SHA-256; W47's read.py and reread.py replayed read-only from the fetched archive with the raw root and the live canonical tree denied, equal to W47's committed readings byte for byte, the control 142 of 142; W47's readings, protocol, diagnostic, both part-1 hashes and amendment record pinned. The verdicts are read from these files by key.

```json
{
 "release": "w47-ladders-archive",
 "asset": "w47-ladders-archive-fd89b7618aed56a1a7a12becf07c653a444166709df24aeac636a6b5673202ac.tar.zst",
 "sha256": "fd89b7618aed56a1a7a12becf07c653a444166709df24aeac636a6b5673202ac",
 "bytes": 66241907,
 "inventorySha256": "4c6497236457bea0911893954c80ae523ec7ba55db4866762a264526d81880aa",
 "entries": {
  "ladders": 14463,
  "drive": 95,
  "reference": 426
 },
 "w47PartOne": [
  "2d6d49ad7af5dc9190227ba02f57e3eb9681a85f31890f127e6c08c621103579",
  "2d4a2c7f73b5a0708c1e80ff06b64043657b0f7fafe3c05c3393da84d769c30e"
 ]
}
```

### targets

**the three targets, their families and the predictions** (Decision Log 5)

PREDICTIONS, which the gate replaces (W48 Decision Log 5): W47's three targets, each a stratum × pose aggregate halved per profile (P pooled over both poses with P rest and P inactive reported beside it; C rest; F inactive). Predictions from W47's ladders and W46's point A, stated here and hashed in part 1 as predictions the gate replaces: - **C rest halves at both scales** at operator 1's closest rung: the thin gain is point A's (W46's C rest fell 0.390 → 0.171 at 1x and 0.538 → 0.238 at 2x at `tintAlpha` 0.7), and the thick cells sit inside the budget instead of 10–12 B away. - **F inactive's fine band falls by at least 0.73 of its excess** at tap σ 4 (R .728 / .753 at 1x, 1.005 / .967 at 2x), the whole band by 2.3–3.9 B; the joint with the receded transmission 0.8 keeps it (R .736 / .767 and 1.044 / 1.011). - **P is not halved from these operators alone** (W47 part 1's prediction: operator 1 alone 0.759 / 0.740 against 0.879 / 0.965 at the reference; the receded photo body at point A ×0.42–0.46). The gate reads it; if it is not halved, the landing rule's improvement clause reads what is. - **The budget** is predicted to hold at operator 1's closest rung (two coarse thick cells away per scale) and to be at risk from the mid-span coarse cells (`checkerboard-lc16` md / ml / lg read 2.8–4.6 B away at point A, which operator 1's gain knot and not its far knot governs). - **The level check's excesses** (`hc-text-28__rrect-md__rest` −0.005 to −0.032, `impulse__rrect-sm__rest` +0.0074 / +0.0083 on every 0.7 rung; none failing L1) are read beside L1 at every stage and in the gate report, ungated. - **S1 dark** read and not gated, direction as W47 predicted.

```json
{
 "given": {
  "statement": "PREDICTIONS, which the gate replaces (W48 Decision Log 5): W47's three targets, each a stratum × pose aggregate halved per profile (P pooled over both poses with P rest and P inactive reported beside it; C rest; F inactive). Predictions from W47's ladders and W46's point A, stated here and hashed in part 1 as predictions the gate replaces: - **C rest halves at both scales** at operator 1's closest rung: the thin gain is point A's (W46's C rest fell 0.390 → 0.171 at 1x and 0.538 → 0.238 at 2x at `tintAlpha` 0.7), and the thick cells sit inside the budget instead of 10–12 B away. - **F inactive's fine band falls by at least 0.73 of its excess** at tap σ 4 (R .728 / .753 at 1x, 1.005 / .967 at 2x), the whole band by 2.3–3.9 B; the joint with the receded transmission 0.8 keeps it (R .736 / .767 and 1.044 / 1.011). - **P is not halved from these operators alone** (W47 part 1's prediction: operator 1 alone 0.759 / 0.740 against 0.879 / 0.965 at the reference; the receded photo body at point A ×0.42–0.46). The gate reads it; if it is not halved, the landing rule's improvement clause reads what is. - **The budget** is predicted to hold at operator 1's closest rung (two coarse thick cells away per scale) and to be at risk from the mid-span coarse cells (`checkerboard-lc16` md / ml / lg read 2.8–4.6 B away at point A, which operator 1's gain knot and not its far knot governs). - **The level check's excesses** (`hc-text-28__rrect-md__rest` −0.005 to −0.032, `impulse__rrect-sm__rest` +0.0074 / +0.0083 on every 0.7 rung; none failing L1) are read beside L1 at every stage and in the gate report, ungated. - **S1 dark** read and not gated, direction as W47 predicted.",
  "targets": {
   "P": [
    "P rest",
    "P inactive"
   ],
   "C rest": [
    "C rest"
   ],
   "F inactive": [
    "F inactive"
   ]
  },
  "predictions": {
   "C rest": "halves at both scales at operator 1's closest rung (W46's C rest fell 0.390 -> 0.171 at 1x and 0.538 -> 0.238 at 2x at tintAlpha 0.7; the thick cells inside the budget instead of 10-12 B away)",
   "F inactive": "the fine band falls by at least 0.73 of its excess at tap sigma 4 (R .728 / .753 at 1x, 1.005 / .967 at 2x), the whole band by 2.3-3.9 B; the joint with the receded transmission 0.8 keeps it (R .736 / .767 and 1.044 / 1.011)",
   "P": "not halved from these operators alone (W47 part 1: operator 1 alone 0.759 / 0.740 against 0.879 / 0.965; the receded photo body at point A x0.42-0.46); if not halved, the landing rule's improvement clause reads what is",
   "budget": "holds at operator 1's closest rung (two coarse thick cells away per scale); at risk from the mid-span coarse cells (checkerboard-lc16 md / ml / lg 2.8-4.6 B away at point A)",
   "level": "the level check's excesses (hc-text-28__rrect-md__rest -0.005 to -0.032, impulse__rrect-sm__rest +0.0074 / +0.0083 on every 0.7 rung; none failing L1) read beside L1 at every stage and in the gate report, ungated"
  },
  "sources": [
   "docs/doperpowers/specs/2026-10-06-w48-dark-operators-fit.md@78d0211e0"
  ]
 },
 "families": {
  "P": [
   "active.dark optics.regular.tintAlpha",
   "active.dark sizeOcclusionGain",
   "active.dark sizeScatterSpanMax",
   "active.dark sizeScatterSpanMax2x",
   "active.dark tintAlphaFar1x",
   "active.dark tintAlphaFar2x",
   "receded.dark optics.regular.tintAlpha"
  ],
  "C rest": [
   "active.dark sizeHeavyTapSigma",
   "active.dark sizeScatterFloor",
   "active.dark sizeScatterFloor2x",
   "active.dark sizeScatterRampStartThin1x",
   "active.dark sizeScatterRampStartThin2x",
   "active.dark sizeScatterScaleGain"
  ],
  "F inactive": [
   "receded.dark optics.regular.blurSigma",
   "receded.dark sizeFineTapShare",
   "receded.dark sizeFineTapSigma",
   "receded.dark sizeFineTapSigma2x",
   "receded.dark sizeHeavySecondShare",
   "receded.dark sizeHeavySecondShareFar2x",
   "receded.dark sizeHeavySecondSigma",
   "receded.dark sizeHeavySecondSigma2x",
   "receded.dark sizeHeavyTapSigma",
```

### ladders

**the corrected protocol (Decision Log 3) and the verdict reader** (clause 3; Decision Log 3; X72, X73)

W47's rungs, read by key from its re-read and results (no ladder rendered), under Decision Log 3's bars: (a) operator 1 the landing rule's partition with `unchanged` admitted on over-Apple cells; (b) operator 2 on T1-fine, R >= 0.5, the whole band beside; (c) the joint, deciding only name-target; no precedence kind, `hold` beside `strike`; the sigma 2 and share 0.5 one-scale rungs off the grid. The verdicts are written by ladders/verdicts.py after this hash.

```json
{
 "bars": {
  "operator 1": {
   "decisionLog": "3 (a)",
   "ladder": "i",
   "cells": [
    "checkerboard-8__rrect-lg__rest",
    "hc-text__rrect-lg__rest",
    "hc-text-7__rrect-lg__rest",
    "checkerboard-32__rrect-lg__rest",
    "checkerboard-64__rrect-lg__rest"
   ],
   "perScale": [
    "no thick cell whose away band reads `away` with growth > awayCeilingB x B",
    "at most awayBeyondBMax of the five whose away band reads `away` with growth > B",
    "no thick cell over Apple at the reference on its change band (reference > native) reads `away`: `toward` and `unchanged` are both admitted, the rule's own states",
    "the thin rest cells keep at least half of point A's gain (W47 ladder (i)'s thin clause, unchanged: reread.json thinKeepsHalf)",
    "L1 passes on its population (W47's level reading, unchanged: reread.json L1passes)"
   ],
   "awayCeilingB": 3,
   "awayBeyondBMax": 2,
   "overAppleAdmits": [
    "toward",
    "unchanged"
   ],
   "reads": "reread.json rungs[label].perScale[scale]: thick[cell].changeBand and .awayBand {n, c, k, B, growth, change}, thinGain, pointAThinGain, thinKeepsHalf, L1passes"
  },
  "operator 2": {
   "decisionLog": "3 (b)",
   "ladder": "iii",
   "fine": [
    "checkerboard-8__rrect-md__inactive",
    "checkerboard-8__rrect-lg__inactive"
   ],
   "guards": [
    "checkerboard-64__rrect-md__inactive",
    "photo__rrect-md__inactive"
   ],
   "perScale": [
    "each fine cell: E = fine(reference) - fine(native) > 0 and R = (fine(reference) - fine(rung)) / E >= fineExcessRemovedMin on T1-fine",
    "each guard: whole-band T1 (k - c) / B >= -guardFloorB",
    "beside, deciding nothing: each fine cell's whole-band fall -g / B, carried to the gate"
   ],
   "fineExcessRemovedMin": 0.5,
   "guardFloorB": 1,
   "reads": "reread.json rungs[label].perScale[scale]: fine.cells[cell] {native, reference, rung, E, R, wholeFallInB}, guards.deltaInB"
  },
  "joint": {
   "decisionLog": "3 (c)",
   "ladder": "iv",
   "cells": [
    "checkerboard-8__rrect-md__inactive",
    "checkerboard-8__rrect-lg__inactive"
   ],
   "scales": [
    1,
    2
   ],
   "reading": "operator 1's partition (a) over the four readings (the two fine cells at 1x and 2x) on their change and away bands, and operator 2's halving (b) on each; the photo inactive ratio against point A's is reported and decides nothing; ladder (iv) decides only name-target",
   "awayCeilingB": 3,
   "awayBeyondBMax": 2,
   "overAppleAdmits": [
    "toward",
    "unchanged"
   ],
   "fineExcessRemovedMin": 0.5,
   "reads": "reread.json rungs['iv-joint'].perScale[scale]: partitionReads[cell].changeBand / .awayBand, fine.cells[cell], photo"
  },
  "2x width": {
   "ladder": "ii",
   "reading": "not re-stated and not re-read (W47 Decision Log 8; W48 Decision Log 4): results.json operators['2x width'] stands; the second tap is not a stage-1 member and no 1x gap is named"
  }
 },
 "separation": {
  "operator 1": "separates when a ladder (i) rung meets bar (a) at BOTH scales",
  "operator 2": "the tap separates when a ladder (iii) tap rung (sizeFineTapSigma / sizeFineTapShare) meets bar (b) at BOTH scales; the receded body width meets when a ladder (iii) optics.regular.blurSigma rung does; when both meet, both are stage-2 members and the gate reads both (Decision Log 3 (c); no precedence)",
  "oneScale": "a rung meeting at one scale only is recorded and is not a fit start (Decision Log 3 (f)); the ones the parent ruled off the grid are `offGrid`; any OTHER rung meeting at one scale only stops part 2 for the parent (W47's one-scale rule stands for the fit)"
 },
 "offGrid": {
  "oneScale": [
   {
    "rung": "iii-s2",
    "values": {
     "receded.dark": {
      "sizeFineTapSigma": 2,
      "sizeFineTapSigma2x": 2
     }
    }
   },
   {
    "rung": "iii-q0.5",
    "values": {
     "receded.dark": {
      "sizeFineTapShare": 0.5
     }
    }
   }
  ],
  "metNowhere": [
   {
    "rung": "iii-s1.5",
    "values": {
     "receded.dark": {
      "sizeFineTapSigm
```

### startingPoint

**the starting point, by hash** (Design "The moves"; X62)

One space, one starting point: d0219cd684bf, the snapshots of its two documents.

```json
{
 "generation": "d0219cd684bf",
 "generationFileSha12": "6e20f04f60c4",
 "documents": {
  "apple-macos-27.0-1x-dark-standard-glass0.25.json": "d0219cd684bf",
  "apple-macos-27.0-1x-dark-standard-glass0.25-receded.json": "f0b36a71772a"
 },
 "digests": {
  "active.dark": "b074fc6913a91c66",
  "receded.dark": "280f0fddf014e0f6"
 }
}
```

### references

**the references, by hash** (Decision Log 1; X52, X60)

d0219cd684bf is every regression row's and T1's reference; ebc3d9105a4a is what X60 holds the light rows to; the two 0.5 generations are frozen (X41).

```json
{
 "files": {
  "d0219cd684bf": "6e20f04f60c40cd8aa89e9580cdc8bca98b2c0b0cb8a3c45bbf0cab52d116d02",
  "ebc3d9105a4a": "6e13171051de77a2236d5545e1cc9ea1d35fd5fe566c6862dedf4b51a8a253f5",
  "85ad7f7e3e0d": "39ac0ba98ca200b10b194f6b45af54df8bf8b2dcbe6b98946a1c8b8aed58356e",
  "0eac5b294cc2": "f72429653e29fd760123a7273436aaaeebc332311c4a53c677b03c004468f979"
 }
}
```

### s1

**S1's predicted direction** (Decision Log 5)

S1 dark is read and not gated, direction as W47 predicted (W48 Decision Log 5); with dark 0.5 frozen (X41), S1 after a dark 0.25 refit reads the refit's change plus the slider's, not the slider's alone.

```json
{
 "given": {
  "predictedDirection": "away from the dark medians 0.31 (0.314 / 0.311), toward the refit's level change at spans 128 and 160 (W47's prediction, carried by W48 Decision Log 5)",
  "sentence": "S1 dark is read and not gated, direction as W47 predicted (W48 Decision Log 5); with dark 0.5 frozen (X41), S1 after a dark 0.25 refit reads the refit's change plus the slider's, not the slider's alone.",
  "sources": []
 }
}
```

### draft

**the part-2 draft, narrowed (Decision Log 4)** (clause 2; Design "The moves")

W47's draft narrowed by the ladders as Design "The moves" states: stage 1 the span law at 432 points (72 renders per scale; 108 / 18 with the gain held), the second tap off, then W46's rest scatter; stage 2 the receded transmission x the fine term x the body width at 114 points (42 per scale), then W46's receded scatter. Part 2 is this body changed only by the decisions the verdicts support.

```json
{
 "stages": [
  "stage1",
  "stage2"
 ],
 "searchedLeaves": 33,
 "targets": [
  "P",
  "C rest",
  "F inactive"
 ],
 "stageSizes": {
  "stage1": {
   "spanLaw": {
    "points": 432,
    "rendersPerScale": {
     "1x": 72,
     "2x": 72
    },
    "gainHeld": {
     "points": 108,
     "rendersPerScale": {
      "1x": 18,
      "2x": 18
     }
    },
    "plusStart": "the step's start (the snapshot) is offered beside the 432 grid points: 433 candidates, 73 renders per scale (fit/test_stage_sizes.py)"
   },
   "restScatter": {
    "gridPointsPerPass": 26,
    "passesAtMost": 2,
    "renders": "about 52 across both scales"
   }
  },
  "stage2": {
   "transmissionFineTerm": {
    "points": 114,
    "rendersPerScale": {
     "1x": 42,
     "2x": 42
    }
   },
   "recededScatter": {
    "gridPointsPerPass": 58,
    "passesAtMost": 2,
    "renders": "about 116 across both scales",
    "candidatesPerPass": 78,
    "candidatesNote": "58 grid values one by one; W47's search sweeps the second tap's share and widths as one factorial step (3 x 4 x 4, 33 after the share-0 collapse), so a pass from the snapshot start offers 78 candidates (fit/test_stage_sizes.py)"
   }
  },
  "note": "W48 Design \"The moves\" and Decision Log 4; recomputed from this body through W47's fit/search.py (fit/test_stage_sizes.py)"
 }
}
```
