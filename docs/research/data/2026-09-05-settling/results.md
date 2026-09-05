# Settling experiment — results

Builds measured: 8 of 52. Judgments: 0. Topology: yes. Fit ratings: 0.

## Q — pairwise quality (human, blinded)

| arm A | arm B | A wins | n | rate | 95 % Wilson |
|---|---|---|---|---|---|

Pooled Bradley–Terry log-strength per arm (mean over briefs with judgments; 0 = brief average):

| arm | mean log-strength | briefs | builds judged |
|---|---|---|---|
| none | — | 0 | 0 |
| v1.1 | — | 0 | 0 |
| v2.0 | — | 0 | 0 |
| v2.1 | — | 0 | 0 |

## V — validity gate per build

| id | brief | arm | seed | mechanical | judged | gate |
|---|---|---|---|---|---|---|
| c183ef | rail | none | A | fail | 0/0 | contrast 0.851 |
| 8ef70a | rail | v1.1 | A | pass | 0/0 | pass |
| cb9845 | rail | v2.0 | A | pass | 0/0 | pass |
| 8d1d23 | rail | v2.1 | A | pass | 0/0 | pass |
| c78373 | rebate | none | A | fail | 0/0 | contrast 0.762 |
| cbd040 | rebate | v1.1 | A | pass | 0/0 | pass |
| 5d884a | rebate | v2.0 | A | pass | 0/0 | pass |
| 7acb2c | rebate | v2.1 | A | pass | 0/0 | pass |

## D — diversity per arm (mean pairwise; effective = Shypula pairwise form with the gate)

### across briefs within category

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff | hueEMD raw / eff | familyJaccard raw / eff |
|---|---|---|---|---|---|---|---|

### within brief across seeds

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff | hueEMD raw / eff | familyJaccard raw / eff |
|---|---|---|---|---|---|---|---|

### D2 — accent hue dispersion and ground, per arm

| arm | builds | accent hues | dispersion (1 − R̄) | eff. dispersion | grounds (L, hue) | dark grounds |
|---|---|---|---|---|---|---|
| none | 2 | 295, 39 | 0.387 | — | 0.153/260 0.959/87 | 1 |
| v1.1 | 2 | 48, 46 | 0.0 | 0.0 | 0.972/229 0.969/301 | 0 |
| v2.0 | 2 | 249, 282 | 0.041 | 0.041 | 0.168/59 0.962/214 | 1 |
| v2.1 | 2 | 27 | — | — | 0.214/71 0.978/258 | 1 |

### D3 — families per arm

| arm | display families (distinct / builds) | body families | mono |
|---|---|---|---|
| none | 1/2: Iowan Old Style | 2/2: -apple-system, ui-sans-serif | 1/2: ui-monospace |
| v1.1 | 2/2: Archivo, Zilla Slab | 1/2: Public Sans | 2/2: Azeret Mono, Geist Mono |
| v2.0 | 2/2: Commissioner, Zilla Slab | 2/2: Atkinson Hyperlegible Next, Commissioner | 2/2: Geist Mono, JetBrains Mono |
| v2.1 | 1/2: Archivo Narrow | 2/2: Barlow, Public Sans | 2/2: JetBrains Mono, Roboto Mono |

### D4 — canonical shapes per arm and category

| arm | category | n | side region | rail band ≥1.5:1 | stat row (fv) | three-up | cards (fv) | headline band | dominant share ≥ 0.4 |
|---|---|---|---|---|---|---|---|---|---|
| none | console | 1 | 0 | 1 | 1 | 0 | 0 | 0 | 1 |
| none | narrative | 1 | 0 | 1 | 1 | 1 | 0 | 0 | 0 |
| v1.1 | console | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| v1.1 | narrative | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |
| v2.0 | console | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| v2.0 | narrative | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| v2.1 | console | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| v2.1 | narrative | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |

## Per-build reads

| id | brief | arm | seed | ground | accent | hues | display / body / mono | dominant | dominance | side | stat | 3-up | height | BT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| c183ef | rail | none | A | #090C11 L0.153 | #A888FA h294.8 | 1 | None / -apple-system / ui-monospace | list 0.949 | hero | band | y |  | 1.0vh | — |
| 8ef70a | rail | v1.1 | A | #F4F6F7 L0.972 | #D46B2C h48 | 3 | Archivo / Public Sans / Geist Mono | list 0.319 | peers |  |  |  | 1.4vh | — |
| cb9845 | rail | v2.0 | A | #120E0B L0.168 | #4197E5 h249 | 1 | Commissioner / Commissioner / JetBrains Mono | chart 0.291 | dominant | band |  |  | 1.9vh | — |
| 8d1d23 | rail | v2.1 | A | #1E1811 L0.214 | #F66D62 h27 | 4 | None / Barlow / JetBrains Mono | chart 0.334 | peers | band |  |  | 1.8vh | — |
| c78373 | rebate | none | A | #F5F1E8 L0.959 | #A9411A h39.2 | 1 | Iowan Old Style / ui-sans-serif / ui-monospace | heading 0.142 | dominant | band | y | y | 12.1vh | — |
| cbd040 | rebate | v1.1 | A | #F5F4F7 L0.969 | #FF7729 h45.8 | 2 | Zilla Slab / Public Sans / Azeret Mono | heading 0.065 | dominant |  |  | y | 7.9vh | — |
| 5d884a | rebate | v2.0 | A | #ECF4F6 L0.962 | #4A41A7 h281.8 | 1 | Zilla Slab / Atkinson Hyperlegible Next / Geist Mono | heading 0.07 | peers | band |  |  | 7.9vh | — |
| 7acb2c | rebate | v2.1 | A | #F6F8FB L0.978 | — h | 0 | Archivo Narrow / Public Sans / Roboto Mono | block 0.09 | dominant | band |  |  | 9.4vh | — |
