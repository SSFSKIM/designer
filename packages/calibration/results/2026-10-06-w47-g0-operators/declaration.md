# W47 G0, part 1: the declaration

Charter `docs/doperpowers/specs/2026-10-06-w47-span-graded-dark-transmission.md@c1f9bf84c`. Every item below is checked by `declare.py check` against its pinned sources (`declaration.json`); this twin is its readable form.

### documents

**the starting point is four document snapshots (X62)** (clause 2; X62)

The dark and light 0.25 document bodies, each verified against its hash and its bytes at the charter's merge c1f9bf84c. Every W47 tool builds from these and refuses the live profiles/ as a start.

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
 "commit": "c1f9bf84c"
}
```

### t1

**T1 as gated, its shared arithmetic, and its dark population** (clause 2; Decision Log 1)

T1 is GATED on the dark 0.25 profiles since W46 G2 against d0219cd684bf (§5.210); its statistic, bar and arithmetic unchanged (W44 G1's t1.py by path, pinned). G2 re-baselines it in W45's five-part order with the separate dark authorised list.

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
 "ownerTest": "packages/calibration/test/adopted-thresholds.test.ts@c1f9bf84c",
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

**W46's referee manifest, by hash (X69)** (clause 4; X69; Decision Log 1)

w46-referees-1 loaded by its SHA-256 and never re-derived from W47's ladders; W46's adapter, given only W46's frozen ladder list, still reproduces it; W47's membership, disjointness and withholding checks hold. Six referee and seven holdout scenes per dark scale are withheld.

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

**the landing rule, its synthetic cases and its rehearsal** (clause 3; Decision Log 1)

W45's growth-only rule as W46 bound it, verbatim: d0219cd684bf, bar 0.5, per dark profile, the verdict the weaker profile's. Rehearsed on d0219cd684bf against itself and on W46's point A by its committed gate cut (§5.209 §4's verdict reproduced); the gated groups per scale the charter's. The parent's ruling: Target P is read pooled over both poses, as declared (cuts/rule.py TARGETS), with P rest and P inactive reported beside it at every gate reading (cuts.py `rule.pBeside`); they decide nothing.

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
 },
 "parentRulings": {
  "target-p-pooled": "Target P is read pooled over both poses, as declared (cuts/rule.py TARGETS), with P rest and P inactive reported beside it at every gate reading (cuts.py `rule.pBeside`); they decide nothing."
 }
}
```

### tools

**W47's tools, their red cases and their tests on d0219cd684bf** (clause 2)

Each tool a port of W46's re-bound to W47 and refusing W44's, W45's and W46's bindings, tested: the cuts port reproduces its reference cut; the stage rehearsal of the shipped dark documents reproduces the published rows; X60's evidence reads IDENTICAL.

```json
{
 "tests": [
  [
   "test_cuts_refusals",
   "cuts",
   11
  ],
  [
   "test_rule",
   "cuts",
   19
  ],
  [
   "test_build_candidate",
   "fit",
   21
  ],
  [
   "test_fit",
   "fit",
   47
  ],
  [
   "test_ladder",
   "ladders",
   22
  ],
  [
   "test_read",
   "ladders",
   5
  ],
  [
   "test_level",
   "level",
   13
  ],
  [
   "test_referees",
   "referees",
   11
  ],
  [
   "test_seal",
   "seal",
   16
  ],
  [
   "test_sheets",
   "sheets",
   7
  ],
  [
   "test_stage",
   "stage",
   8
  ],
  [
   "test_x60",
   "stage",
   11
  ],
  [
   "test_bindings",
   ".",
   12
  ],
  [
   "test_declare",
   ".",
   42
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

**the level check (X61) and its rendered test** (G0 (e); X61)

A check, not a solver, knowing operator 1's per-pixel alpha. The shipped rung reproduces d0219cd684bf on every ladder (i) cell as pixel and measurement identity and reads no change.

```json
{
 "identity": [
  "IDENTICAL",
  130,
  130,
  true
 ],
 "projection": "every field but capturedAt, key.web.capturePath"
}
```

### operators

**the two operators: laws, identities, grids, units, X68 domains** (clause 1; Design "Operator 1", "Operator 2"; X65, X66, X68; Decision Logs 2, 3)

Operator 1 grades tintAlpha per pixel on the far curve (two plain value drops, mirrored by the CSS tier); operator 2 is the receded fine term in the form the diagnostic chose (one gate-group, declined by the CSS tier). Their domains are the declaration's (X68), refused by the builder. Clause 1's evidence is pinned here by name: the two recorder specs, their scene fixture and each operator's proof records.

```json
{
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
  "packages/renderer-webgpu/e2e/fixtures/scenes.ts": "7ce2d0b427f342aab5740b30c66998a5ded60a9baede818a0720a7372ad5542a",
  "packages/calibration/results/2026-10-06-w47-g0-operators/operator-1/compare.txt": "44dee374e585f80c483717a054328ad470c7f8150b7d557ed742a034c71a7bed",
  "packages/calibration/results/2026-10-06-w47-g0-operators/operator-1/png-sha256.json": "c31fad540775aa70efff3ac7dcbe8aff17cc7468a4c40d69da2156164fb85111",
  "packages
```

### diagnostic

**the depth-split diagnostic and operator 2's form** (G0 (f); Decision Log 3 (v1.1))

G0 (f) chose the BODY form by the declared criterion: R body 0.739 / 0.769 at 1x (span 96 / 160) and 1.044 / 1.011 at 2x, pooled 0.891; R deep 0 on all four, its PNGs byte-identical to the control (the 8 px structure is already absent from the deep sample; positive control in diagnostic/positive-control/). Measured weights body / deep: 1x 96 0.766 / 0.234; 1x 160 0.624 / 0.376; 2x 96 0.459 / 0.541; 2x 160 0.456 / 0.544; beyond the reach at 2x 160 0.436 / 0.564.

```json
{
 "record": "packages/calibration/results/2026-10-06-w47-g0-operators/diagnostic/record.json",
 "chosenForm": "body",
 "population": [
  [
   "checkerboard-8__rrect-lg__inactive",
   1
  ],
  [
   "checkerboard-8__rrect-lg__inactive",
   2
  ],
  [
   "checkerboard-8__rrect-md__inactive",
   1
  ],
  [
   "checkerboard-8__rrect-md__inactive",
   2
  ]
 ]
}
```

### targets

**the three targets, their families and the predictions** (Decision Log 4)

PREDICTIONS, which the ladders replace (charter Design "The targets and their families"; Decision Log 4). From W46's point A cut (structure share 1 - alpha at held scatter): the control reproduces point A's verdict (16 / 8 and 17 / 10 away beyond B / 3B; C rest halved at both scales; P and F inactive not). Operator 1 alone (tintAlpha 0.7, gain 0.4, far 0.38 at top 256, or 0.13 at top 128): C rest halved at 1x and 2x at top 256 and NOT at top 128; P (both poses pooled) NOT halved at either scale (0.759 / 0.740 against 0.879 / 0.965), as the charter predicts; F inactive halved through the receded's inheritance of the gain and far delta at receded 0.8; the budget fails (9-13 away beyond B, 3-6 past 3B) and the 1x F rest group fails. Thick rest cells fall to x0.48-0.66 (under Apple) and mid to x0.73-0.78: the span law trades the thick overshoot for under-structure unless ladder (ii) supplies the 2x width. Operator 2 (body form): the attenuation table g = exp(-pi^2 sigma^2 / c^2), a = 1 - share + share g, on the F inactive gate cells as an upper bound (sigma 2-3 at share 0.5-1, or sigma 4 at share 0.5, brings point A's x1.72-2.38 to x0.75-1.49); the diagnostic measured the body form removing 0.74-1.04 of the excess at sigma 6, share 1, from the reference. The 64 px checker and photo lose at most 1.0-3.8 % of their mode at sigma 2-4.

```json
{
 "given": {
  "predictions": "packages/calibration/results/2026-10-06-w47-g0-operators/targets/predictions.json",
  "statement": "PREDICTIONS, which the ladders replace (charter Design \"The targets and their families\"; Decision Log 4). From W46's point A cut (structure share 1 - alpha at held scatter): the control reproduces point A's verdict (16 / 8 and 17 / 10 away beyond B / 3B; C rest halved at both scales; P and F inactive not). Operator 1 alone (tintAlpha 0.7, gain 0.4, far 0.38 at top 256, or 0.13 at top 128): C rest halved at 1x and 2x at top 256 and NOT at top 128; P (both poses pooled) NOT halved at either scale (0.759 / 0.740 against 0.879 / 0.965), as the charter predicts; F inactive halved through the receded's inheritance of the gain and far delta at receded 0.8; the budget fails (9-13 away beyond B, 3-6 past 3B) and the 1x F rest group fails. Thick rest cells fall to x0.48-0.66 (under Apple) and mid to x0.73-0.78: the span law trades the thick overshoot for under-structure unless ladder (ii) supplies the 2x width. Operator 2 (body form): the attenuation table g = exp(-pi^2 sigma^2 / c^2), a = 1 - share + share g, on the F inactive gate cells as an upper bound (sigma 2-3 at share 0.5-1, or sigma 4 at share 0.5, brings point A's x1.72-2.38 to x0.75-1.49); the diagnostic measured the body form removing 0.74-1.04 of the excess at sigma 6, share 1, from the reference. The 64 px checker and photo lose at most 1.0-3.8 % of their mode at sigma 2-4.",
  "sources": [
   "packages/calibration/results/2026-10-06-w47-g0-operators/targets/predict.py",
   "packages/calibration/results/2026-10-06-w47-g0-operators/targets/predictions.json",
   "packages/calibration/results/2026-10-06-w47-g0-operators/targets/predictions.txt",
   "packages/calibration/results/2026-10-06-w47-g0-operators/diagnostic/record.json",
   "packages/calibration/results/2026-10-05-w46-g1-refit/gate/d-s2-rta0.8-rs214-rfa0.5-rh10.25-re20.04-rk10.15-rk20.04-rn10.4-rn20.4-rg0/cut.json.gz"
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
   "active.dark sizeHeavySecondShare",
   "active.dark sizeHeavySecondShareFar2x",
   "active.dark sizeHeavySecondSigma2x",
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

**the ladders' protocol, cells and decisions** (clause 5; Design "The ladders"; X69, X70)

Four ladders in candidate mode from the snapshots, both scales, the listed cells only, X69 disjoint from the referees and X70's three-way check at every rung; the bars of clause 5 and the decisions name-unfitted, name-target, body-width-first, narrow, strike and name-1x-gap (and the outcomes fit and stop), as protocol.json names them. The parent's ruling: An operator separates only if it meets its bar at both scales. A one-scale result STOPS for the parent with the numbers, and the operator is neither struck nor admitted until ruled; part2.py refuses until then.

```json
{
 "rungs": 41,
 "levers": [
  "i-a0.7",
  "i-a0.7-f0.2",
  "i-a0.7-f0.45",
  "i-a0.7-f0.2-t128",
  "i-a0.7-f0.2-t160",
  "i-a0.7-g0.2",
  "i-a0.7-g0.4",
  "i-a0.7-g0.6",
  "i-a0.8",
  "i-a0.8-f0.2",
  "i-a0.8-f0.45",
  "i-a0.8-f0.2-t128",
  "i-a0.8-f0.2-t160",
  "i-a0.8-g0.2",
  "i-a0.8-g0.4",
  "i-a0.8-g0.6",
  "ii-w6-d0.3-t256",
  "ii-w6-d0.6-t256",
  "ii-w10-d0.3-t256",
  "ii-w10-d0.6-t256",
  "ii-w14-d0.3-t256",
  "ii-w14-d0.6-t256",
  "ii-w6-d0.3-t128",
  "ii-w6-d0.6-t128",
  "ii-w10-d0.3-t128",
  "ii-w10-d0.6-t128",
  "ii-w14-d0.3-t128",
  "ii-w14-d0.6-t128",
  "iii-b2",
  "iii-b3",
  "iii-b4",
  "iii-s1.5",
  "iii-s2",
  "iii-s3",
  "iii-s4",
  "iii-s6",
  "iii-q0.25",
  "iii-q0.5",
  "iii-q0.75",
  "iv-joint"
 ],
 "cellsPerLadder": {
  "i": [
   33,
   32
  ],
  "ii": [
   11,
   0
  ],
  "iii": [
   0,
   10
  ],
  "iv": [
   0,
   10
  ]
 },
 "parentRulings": {
  "separation-both-scales": "An operator separates only if it meets its bar at both scales. A one-scale result STOPS for the parent with the numbers, and the operator is neither struck nor admitted until ruled; part2.py refuses until then."
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

**S1's predicted direction** (Design "The other rows")

S1 is read and not gated (Design "The other rows"); with dark 0.5 frozen (X41), S1 after a dark 0.25 refit reads the refit's change plus the slider's, not the slider's alone.

```json
{
 "given": {
  "predictedDirection": "away from the dark medians 0.31 (0.314 / 0.311), toward the refit's level change at spans 128 and 160",
  "sentence": "S1 is read and not gated (Design \"The other rows\"); with dark 0.5 frozen (X41), S1 after a dark 0.25 refit reads the refit's change plus the slider's, not the slider's alone.",
  "sources": []
 }
}
```

### draft

**the part-2 draft** (clause 2; Design "The moves")

Two stages in the fit driver's shape, the tie rule, scale-separable rendering, the selection rule and the landing rule; part 2 is this body changed only by the ladders' decisions. The parent's rulings: The draft's widened second-tap domains (the active 2x width [0, 24], the active far share [0, 1]) are declaration choices; no amendment is spent. Stage 1 at 48,384 points (288 renders at 1x, 2,016 at 2x) is accepted, with no pruning beyond what is declared.

```json
{
 "stages": [
  "stage1",
  "stage2"
 ],
 "searchedLeaves": 36,
 "targets": [
  "P",
  "C rest",
  "F inactive"
 ],
 "parentRulings": {
  "widened-second-tap-domains": "The draft's widened second-tap domains (the active 2x width [0, 24], the active far share [0, 1]) are declaration choices; no amendment is spent.",
  "stage-1-crossed-factorial": "Stage 1 at 48,384 points (288 renders at 1x, 2,016 at 2x) is accepted, with no pruning beyond what is declared."
 }
}
```
