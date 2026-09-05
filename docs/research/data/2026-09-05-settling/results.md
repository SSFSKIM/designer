# Settling experiment — results

Builds measured: 16 of 52. Judgments: 3. Topology: yes. Fit ratings: 0.

## Q — pairwise quality (human, blinded)

| arm A | arm B | A wins | n | rate | 95 % Wilson |
|---|---|---|---|---|---|
| none | v2.1 | 1 | 1 | 1.00 | 0.21–1.00 |
| v1.1 | v2.1 | 0 | 1 | 0.00 | 0.00–0.79 |
| v2.0 | v2.1 | 1 | 1 | 1.00 | 0.21–1.00 |

Pooled Bradley–Terry log-strength per arm (mean over briefs with judgments; 0 = brief average):

| arm | mean log-strength | briefs | builds judged |
|---|---|---|---|
| none | +0.67 | 1 | 1 |
| v1.1 | -3.08 | 1 | 1 |
| v2.0 | +1.00 | 1 | 1 |
| v2.1 | -2.23 | 2 | 2 |

## V — validity gate per build

| id | brief | arm | seed | mechanical | judged | gate |
|---|---|---|---|---|---|---|
| c183ef | rail | none | A | fail | 0/0 | contrast 0.851 |
| 8ef70a | rail | v1.1 | A | pass | 0/1 | won 0 pairs |
| cb9845 | rail | v2.0 | A | pass | 1/1 | pass |
| 8d1d23 | rail | v2.1 | A | pass | 1/2 | pass |
| c78373 | rebate | none | A | fail | 1/1 | contrast 0.762 |
| cbd040 | rebate | v1.1 | A | pass | 0/0 | pass |
| 5d884a | rebate | v2.0 | A | pass | 0/0 | pass |
| 7acb2c | rebate | v2.1 | A | pass | 0/1 | won 0 pairs |
| 30f897 | library | none | A | pass | 0/0 | pass |
| dd3f5c | library | v1.1 | A | pass | 0/0 | pass |
| 99499b | library | v2.0 | A | pass | 0/0 | pass |
| 672565 | library | v2.1 | A | pass | 0/0 | pass |
| 122077 | pharmacy | none | A | fail | 0/0 | contrast 0.57 |
| 002ea9 | pharmacy | v1.1 | A | pass | 0/0 | pass |
| 3ba9f0 | pharmacy | v2.0 | A | pass | 0/0 | pass |
| f344b7 | pharmacy | v2.1 | A | pass | 0/0 | pass |

## D — diversity per arm (mean pairwise; effective = Shypula pairwise form with the gate)

### across briefs within category

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff | hueEMD raw / eff | familyJaccard raw / eff |
|---|---|---|---|---|---|---|---|
| none | console | 1 | 0.206 / 0.0 | 0.977 / 0.0 | 0.526 / 0.0 | 0.157 / 0.0 | 1.0 / 0.0 |
| none | narrative | 1 | 0.184 / 0.0 | 0.49 / 0.0 | 0.706 / 0.0 | 0.189 / 0.0 | 0.667 / 0.0 |
| v1.1 | console | 1 | 0.328 / 0.0 | 0.565 / 0.0 | 0.906 / 0.0 | 0.042 / 0.0 | 1.0 / 0.0 |
| v1.1 | narrative | 1 | 0.264 / 0.264 | 0.564 / 0.564 | 0.409 / 0.409 | 0.174 / 0.174 | 1.0 / 1.0 |
| v2.0 | console | 1 | 0.309 / 0.309 | 0.473 / 0.473 | 0.75 / 0.75 | 0.089 / 0.089 | 1.0 / 1.0 |
| v2.0 | narrative | 1 | 0.293 / 0.293 | 0.412 / 0.412 | 0.633 / 0.633 | 0.161 / 0.161 | 0.667 / 0.667 |
| v2.1 | console | 1 | 0.184 / 0.184 | 0.613 / 0.613 | 0.609 / 0.609 | 0.067 / 0.067 | 1.0 / 1.0 |
| v2.1 | narrative | 1 | 0.249 / 0.0 | 0.47 / 0.0 | 0.466 / 0.0 | 0.165 / 0.0 | 1.0 / 0.0 |

### within brief across seeds

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff | hueEMD raw / eff | familyJaccard raw / eff |
|---|---|---|---|---|---|---|---|

### D2 — accent hue dispersion and ground, per arm

| arm | builds | accent hues | dispersion (1 − R̄) | eff. dispersion | grounds (L, hue) | dark grounds |
|---|---|---|---|---|---|---|
| none | 4 | 295, 39, 30, 38 | 0.258 | — | 0.153/260 0.959/87 0.922/89 0.977/86 | 1 |
| v1.1 | 4 | 48, 46, 23, 285 | 0.326 | 0.372 | 0.972/229 0.969/301 0.975/106 0.945/215 | 0 |
| v2.0 | 4 | 249, 282, 22, 28 | 0.508 | 0.508 | 0.168/59 0.962/214 0.979/248 0.963/197 | 1 |
| v2.1 | 4 | 27, 26, 220 | 0.648 | 0.648 | 0.214/71 0.978/258 0.94/271 0.968/237 | 1 |

### D3 — families per arm

| arm | display families (distinct / builds) | body families | mono |
|---|---|---|---|
| none | 3/4: Inter, Iowan Old Style, Superclarendon | 3/4: -apple-system, Inter, ui-sans-serif | 1/4: ui-monospace |
| v1.1 | 3/4: Archivo, Source Serif 4, Zilla Slab | 3/4: Lexend, Public Sans, Source Sans 3 | 3/4: Azeret Mono, Geist Mono, Roboto Mono |
| v2.0 | 4/4: Atkinson Hyperlegible Next, Commissioner, Literata, Zilla Slab | 2/4: Atkinson Hyperlegible Next, Commissioner | 4/4: Atkinson Hyperlegible Mono, Fragment Mono, Geist Mono, JetBrains Mono |
| v2.1 | 3/4: Archivo Narrow, Atkinson Hyperlegible Next, Zilla Slab | 4/4: Atkinson Hyperlegible Next, Barlow, Lexend, Public Sans | 3/4: Fragment Mono, JetBrains Mono, Roboto Mono |

### D4 — canonical shapes per arm and category

| arm | category | n | side region | rail band ≥1.5:1 | stat row (fv) | three-up | cards (fv) | headline band | dominant share ≥ 0.4 |
|---|---|---|---|---|---|---|---|---|---|
| none | console | 2 | 1 | 1 | 1 | 0 | 0 | 0 | 1 |
| none | narrative | 2 | 0 | 2 | 2 | 2 | 0 | 1 | 1 |
| v1.1 | console | 2 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| v1.1 | narrative | 2 | 0 | 1 | 0 | 1 | 0 | 0 | 0 |
| v2.0 | console | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 0 |
| v2.0 | narrative | 2 | 0 | 1 | 0 | 0 | 1 | 0 | 1 |
| v2.1 | console | 2 | 0 | 2 | 0 | 0 | 0 | 0 | 1 |
| v2.1 | narrative | 2 | 0 | 2 | 0 | 1 | 1 | 0 | 0 |

## Per-build reads

| id | brief | arm | seed | ground | accent | hues | display / body / mono | dominant | dominance | side | stat | 3-up | height | BT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 30f897 | library | none | A | #FCF7EC L0.977 | #C24A22 h37.9 | 2 | Superclarendon / ui-sans-serif / None | heading 0.634 | hero | band | y | y | 6.8vh | — |
| dd3f5c | library | v1.1 | A | #D1F4FD L0.945 | #5F4BC7 h285.1 | 1 | Source Serif 4 / Lexend / None | heading 0.078 | peers | band |  |  | 6.7vh | — |
| 99499b | library | v2.0 | A | #E9F6F6 L0.963 | #B12D26 h28 | 1 | Literata / Atkinson Hyperlegible Next / Fragment Mono | panel 0.403 | hero |  |  |  | 6.4vh | — |
| 672565 | library | v2.1 | A | #EDF6FC L0.968 | #00758F h220.4 | 1 | Zilla Slab / Lexend / Fragment Mono | card-grid 0.14 | peers | band |  | y | 7.1vh | — |
| 122077 | pharmacy | none | A | #E7E5E0 L0.922 | #A52A1C h30.3 | 2 | Inter / Inter / ui-monospace | rail 0.276 | peers | y |  |  | 1.0vh | — |
| 002ea9 | pharmacy | v1.1 | A | #F7F7F3 L0.975 | #A34242 h22.8 | 4 | Source Serif 4 / Source Sans 3 / Roboto Mono | list 0.33 | hero | band |  |  | 4.1vh | — |
| 3ba9f0 | pharmacy | v2.0 | A | #F7F8F9 L0.979 | #98252D h22.1 | 4 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / Atkinson Hyperlegible Mono | list 0.301 | hero | band |  |  | 2.6vh | — |
| f344b7 | pharmacy | v2.1 | A | #EAEBEE L0.94 | #A12626 h25.9 | 4 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | list 0.419 | dominant | band |  |  | 2.6vh | — |
| c183ef | rail | none | A | #090C11 L0.153 | #A888FA h294.8 | 1 | None / -apple-system / ui-monospace | list 0.949 | hero | band | y |  | 1.0vh | — |
| 8ef70a | rail | v1.1 | A | #F4F6F7 L0.972 | #D46B2C h48 | 3 | Archivo / Public Sans / Geist Mono | list 0.319 | peers |  |  |  | 1.4vh | -3.08 |
| cb9845 | rail | v2.0 | A | #120E0B L0.168 | #4197E5 h249 | 1 | Commissioner / Commissioner / JetBrains Mono | chart 0.291 | dominant | band |  |  | 1.9vh | +1.00 |
| 8d1d23 | rail | v2.1 | A | #1E1811 L0.214 | #F66D62 h27 | 4 | None / Barlow / JetBrains Mono | chart 0.334 | peers | band |  |  | 1.8vh | -1.43 |
| c78373 | rebate | none | A | #F5F1E8 L0.959 | #A9411A h39.2 | 1 | Iowan Old Style / ui-sans-serif / ui-monospace | heading 0.142 | dominant | band | y | y | 12.1vh | +0.67 |
| cbd040 | rebate | v1.1 | A | #F5F4F7 L0.969 | #FF7729 h45.8 | 2 | Zilla Slab / Public Sans / Azeret Mono | heading 0.065 | dominant |  |  | y | 7.9vh | — |
| 5d884a | rebate | v2.0 | A | #ECF4F6 L0.962 | #4A41A7 h281.8 | 1 | Zilla Slab / Atkinson Hyperlegible Next / Geist Mono | heading 0.07 | peers | band |  |  | 7.9vh | — |
| 7acb2c | rebate | v2.1 | A | #F6F8FB L0.978 | — h | 0 | Archivo Narrow / Public Sans / Roboto Mono | block 0.09 | dominant | band |  |  | 9.4vh | -3.02 |
