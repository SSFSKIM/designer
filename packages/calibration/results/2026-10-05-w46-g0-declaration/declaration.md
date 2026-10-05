# W46 G0, part 1: the declaration

Charter `docs/doperpowers/specs/2026-10-05-w46-dark-texture-at-0-25.md@b711762a`. Every item below is checked by `declare.py check` against its pinned sources (`declaration.json`); this twin is its readable form.

### documents

**the starting point is four document snapshots (X62)** (clause 1; X62)

The dark and light 0.25 document bodies, each verified against its twelve-hex hash and its bytes at b36c9990. Every W46 tool builds from these and refuses the live profiles/ as a start.

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
 "commit": "b36c9990"
}
```

### t1

**T1 as adopted, its shared arithmetic, and its dark population** (Decision Log 3)

T1's statistic, bar and arithmetic unchanged (W44 G1's t1.py by path, pinned). The owner test reads the dark 0.25 profiles and gates none of them today; G2 adopts them in W45's five-part order.

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
 "ownerTest": "packages/calibration/test/adopted-thresholds.test.ts@b711762a",
 "ownerNeedles": [
  "const T1_READ_PROFILES = [\n  \"apple-macos-27.0-1x-dark-standard-glass0.25\",\n  \"apple-macos-27.0-2x-dark-standard-glass0.25\",",
  "const T1_REFERENCE = { active: \"ebc3d9105a4a\", receded: \"12712d534b78\" } as const;"
 ]
}
```

### bar

**the bar: 0.5 code on every dark cell** (Decision Log 3)

W44 G0's measurement: 77 cells per dark scale, the seven runs pixel-identical, bar = half a code.

```json
{
 "darkCells": 154,
 "maxSeparation": 0.0
}
```

### manifest

**the referee manifest and the planner adapter** (clause 3; Decision Log 2)

Six probe scenes per dark scale chosen by the charter's deterministic rule, re-derived by the adapter, which refuses any other manifest, a ladder cell, a light profile or W44's schema. 66 of 72 non-holdout T1 cells per scale remain to fit.

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
 },
 "tests": 14,
 "fitMembers": {
  "P rest": 4,
  "P inactive": 5,
  "C rest": 28,
  "F inactive": 2,
  "F rest": 10,
  "T rest": 3,
  "C inactive": 14,
  "T inactive": 0
 }
}
```

### rule

**the landing rule, its synthetic cases and its rehearsal** (clause 2; Decision Log 3)

W45's growth-only rule bound to d0219cd684bf, evaluated per dark profile, the verdict the weaker profile's. Rehearsed on d0219cd684bf against itself (every gate cell unchanged), W43 G3's pre-fit render (504c5348…, every cell unchanged too: the dark 0.5 documents differ in two tone ordinates only) and W43's c02 (partial: UNMEASURED). The gated groups per scale are the charter's.

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
  "published d0219cd684bf against itself": [
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
  "W43 G3's pre-fit render (504c5348…) against d0219cd684bf": [
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
  "W43's dark probe c02 against d0219cd684bf": [
   "UNMEASURED: 1x UNMEASURED: 52 member(s) of the scope have no reading; 2x UNMEASURED: 52 member(s) of the scope have no reading",
   [
    12,
    1,
    0
   ],
   [
    10,
    0,
    0
   ]
  ]
 }
}
```

### tools

**W46's tools, their red cases and their tests on d0219cd684bf** (clause 1)

Each tool a parameterised port refusing W44's and W45's bindings, tested: the cuts port equals W45's landing cut on every dark non-referee entry; the stage rehearsal of the shipped dark documents reproduces the published rows (132 rows, 264 captures byte-identical); X60's evidence reads IDENTICAL.

```json
{
 "tests": [
  [
   "test_bindings",
   ".",
   9
  ],
  [
   "test_cuts_refusals",
   "cuts",
   11
  ],
  [
   "test_build_candidate",
   "fit",
   11
  ],
  [
   "test_fit",
   "fit",
   35
  ],
  [
   "test_seal",
   "seal",
   10
  ],
  [
   "test_stage",
   "stage",
   7
  ],
  [
   "test_x60",
   "stage",
   11
  ],
  [
   "test_sheets",
   "sheets",
   7
  ],
  [
   "test_declare",
   ".",
   19
  ]
 ],
 "stageRehearsal": [
  "REPRODUCED",
  132,
  264
 ]
}
```

### level

**the level check (X61) and its rendered test** (X61; G0 (d))

A check, not a solver: L1 through the cuts' own cut_l1, the level rows, every excess attributed to the stand-down the runtime's own arithmetic predicts. The shipped rung reproduces d0219cd684bf on every ladder (i) cell as pixel and measurement identity and reads no change.

```json
{
 "tests": 11,
 "identity": [
  "IDENTICAL",
  116,
  116,
  true
 ],
 "projection": "every field but capturedAt, key.web.capturePath"
}
```

### targets

**the three targets, their families and the predictions** (Decision Log 4)

P (both poses) by the transmission, C rest by the rest scatter, F inactive by the receded scatter. Predicted from the rows: the transmission alone halves P's aggregate near a = 0.7 at rest and 0.7 receded, and moves C rest toward Apple at 0.8 and past it below; it moves F inactive away (it only adds structure); the receded photo reaches ×1 near a′ 0.51–0.60, below the receded checker's clamp (≈ 0.64), so P inactive is predicted not closable by the transmission at held ordinates.

```json
{
 "predictedAggregates": {
  "apple-macos-27.0-1x-dark-standard-glass0.25 P": {
   "A": [
    0.879,
    0.703,
    0.364,
    0.367,
    0.58
   ],
   "halvedAt": [
    "rung 2",
    "rung 3"
   ]
  },
  "apple-macos-27.0-1x-dark-standard-glass0.25 C rest": {
   "A": [
    0.39,
    0.318,
    0.632,
    0.909,
    1.126
   ],
   "halvedAt": []
  },
  "apple-macos-27.0-1x-dark-standard-glass0.25 F inactive": {
   "A": [
    0.917,
    1.462,
    1.846,
    2.122,
    2.338
   ],
   "halvedAt": []
  },
  "apple-macos-27.0-2x-dark-standard-glass0.25 P": {
   "A": [
    0.965,
    0.658,
    0.302,
    0.27,
    0.483
   ],
   "halvedAt": [
    "rung 2",
    "rung 3",
    "rung 4"
   ]
  },
  "apple-macos-27.0-2x-dark-standard-glass0.25 C rest": {
   "A": [
    0.538,
    0.282,
    0.434,
    0.697,
    0.904
   ],
   "halvedAt": []
  },
  "apple-macos-27.0-2x-dark-standard-glass0.25 F inactive": {
   "A": [
    0.982,
    1.526,
    1.908,
    2.184,
    2.4
   ],
   "halvedAt": []
  }
 },
 "families": {
  "P": [
   "active.dark optics.regular.tintAlpha",
   "receded.dark optics.regular.tintAlpha"
  ],
  "C rest": [
   "active.dark sizeHeavySecondShare",
   "active.dark sizeHeavySecondShareFar2x",
   "active.dark sizeHeavySecondSigma",
   "active.dark sizeHeavySecondSigma2x",
   "active.dark sizeHeavyTapSigma",
   "active.dark sizeHeavyTapSigma2x",
   "active.dark sizeScatterFloor",
   "active.dark sizeScatterFloor2x",
   "active.dark sizeScatterRampStartThin1x",
   "active.dark sizeScatterRampStartThin2x",
   "active.dark sizeScatterScaleGain"
  ],
  "F inactive": [
   "receded.dark sizeHeavySecondShare",
   "receded.dark sizeHeavySecondShareFar2x",
   "receded.dark sizeHeavySecondSigma",
   "receded.dark sizeHeavySecondSigma2x",
   "receded.dark sizeHeavyTapSigma",
   "receded.dark sizeHeavyTapSigma2x",
   "receded.dark sizeScatterFloor",
   "receded.dark sizeScatterFloor2x",
   "receded.dark sizeScatterHeavyShareThick1x",
   "receded.dark sizeScatterRampStartFar1x",
   "receded.dark sizeScatterRampStartFar2x",
   "receded.dark sizeScatterRampStartThick1x",
   "receded.dark sizeScatterRampStartThick2x",
   "receded.dark sizeScatterRampStartThin1x",
   "receded.dark sizeScatterRampStartThin2x",
   "receded.dark sizeScatterScaleGain"
  ]
 }
}
```

### ladders

**the ladders' protocol, cells and decisions** (clause 4; Design "The ladders")

Three ladders, one leaf per rung from the snapshots, both scales, the listed cells only; the control identical to d0219cd684bf or the ladders stop; the bars of clause 4 and the decisions strike, narrow and name-target (X63).

```json
{
 "rungs": 44,
 "levers": [
  "i-a",
  "i-r",
  "ii-fa",
  "ii-fb",
  "ii-n1",
  "ii-n2",
  "ii-s1",
  "ii-s2",
  "iii-rn1",
  "iii-rn2",
  "iii-rk1",
  "iii-rk2",
  "iii-re1",
  "iii-re2",
  "iii-rs2"
 ],
 "cellsPerLadder": {
  "i": [
   25,
   33
  ],
  "ii": [
   13,
   2
  ],
  "iii": [
   0,
   4
  ]
 }
}
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

**the references, by hash** (Decision Logs 3, 5; X60)

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

At held ordinates the level moves only where the clamp bites, so S1's dark medians (0.31 today) are predicted unmoved down to a = 0.8, to rise slightly at 0.7 and far above 1 below it, through the clamped thick cells. S1 is read and not gated; after a dark 0.25 refit with dark 0.5 frozen it reads the refit's change plus the slider's.

```json
{
 "predictedMedians": {
  "apple-macos-27.0-1x-dark-standard-glass0.25": {
   "0.9/0.89": 0.314,
   "0.8/0.8": 0.314,
   "0.7/0.7": 0.382,
   "0.6/0.6": 2.547,
   "0.5/0.5": 6.586
  },
  "apple-macos-27.0-2x-dark-standard-glass0.25": {
   "0.9/0.89": 0.311,
   "0.8/0.8": 0.311,
   "0.7/0.7": 0.338,
   "0.6/0.6": 1.786,
   "0.5/0.5": 5.911
  }
 },
 "sentence": "after a dark 0.25 refit with dark 0.5 frozen, S1's dark reading is the refit's change plus the slider's, and says nothing about Apple's slider until dark 0.5 is refit under the same families (Decision Log 1)"
}
```

### draft

**the part-2 draft** (clause 1; Design "The moves")

Two stages in the fit driver's shape, the tie rule, scale-separable rendering, the selection rule and the landing rule; part 2 is this body changed only by the ladders' decisions.

```json
{
 "stages": [
  "stage1",
  "stage2"
 ],
 "searchedLeaves": 29,
 "targets": [
  "P",
  "C rest",
  "F inactive"
 ]
}
```
