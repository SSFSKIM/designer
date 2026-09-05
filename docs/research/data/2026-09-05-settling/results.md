# Settling experiment — results

Builds measured: 32 of 52. Judgments: 3. Topology: yes. Fit ratings: 8.

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
| 8ef70a | rail | v1.1 | A | pass | 0/1 | pass |
| cb9845 | rail | v2.0 | A | pass | 1/1 | pass |
| 8d1d23 | rail | v2.1 | A | pass | 1/2 | pass |
| c78373 | rebate | none | A | fail | 1/1 | contrast 0.762 |
| cbd040 | rebate | v1.1 | A | pass | 0/0 | pass |
| 5d884a | rebate | v2.0 | A | pass | 0/0 | pass |
| 7acb2c | rebate | v2.1 | A | pass | 0/1 | pass |
| 30f897 | library | none | A | pass | 0/0 | pass |
| dd3f5c | library | v1.1 | A | pass | 0/0 | pass |
| 99499b | library | v2.0 | A | pass | 0/0 | pass |
| 672565 | library | v2.1 | A | pass | 0/0 | pass |
| 122077 | pharmacy | none | A | fail | 0/0 | contrast 0.57 |
| 002ea9 | pharmacy | v1.1 | A | pass | 0/0 | pass |
| 3ba9f0 | pharmacy | v2.0 | A | pass | 0/0 | pass |
| f344b7 | pharmacy | v2.1 | A | pass | 0/0 | pass |
| ae0658 | fleet | none | A | pass | 0/0 | pass |
| 7e71b0 | fleet | v1.1 | A | pass | 0/0 | pass |
| 4e40b0 | fleet | v2.0 | A | pass | 0/0 | pass |
| 49e6cb | fleet | v2.1 | A | fail | 0/0 | overflow |
| 4d761e | hardware | none | A | pass | 0/0 | pass |
| 5c24f6 | hardware | v1.1 | A | pass | 0/0 | pass |
| 0663a2 | hardware | v2.0 | A | pass | 0/0 | pass |
| c7de7e | hardware | v2.1 | A | pass | 0/0 | pass |
| ede597 | compare | none | A | pass | 0/0 | pass |
| 32cc11 | compare | v1.1 | A | pass | 0/0 | pass |
| 033fcb | compare | v2.0 | A | pass | 0/0 | pass |
| d178d1 | compare | v2.1 | A | pass | 0/0 | pass |
| e44b85 | rail | none | B | fail | 0/0 | contrast 0.55 |
| a903f5 | rail | v1.1 | B | pass | 0/0 | pass |
| 92cba1 | rail | v2.0 | B | pass | 0/0 | pass |
| 661e66 | rail | v2.1 | B | pass | 0/0 | pass |

## D — diversity per arm (mean pairwise; effective = Shypula pairwise form with the gate)

### across briefs within category

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff | hueEMD raw / eff | familyJaccard raw / eff |
|---|---|---|---|---|---|---|---|
| none | console | 5 | 0.246 / 0.0 | 0.725 / 0.0 | 0.733 / 0.0 | 0.108 / 0.0 | 0.8 / 0.0 |
| none | narrative | 3 | 0.201 / 0.077 | 0.429 / 0.108 | 0.689 / 0.29 | 0.132 / 0.045 | 0.778 / 0.333 |
| v1.1 | console | 5 | 0.256 / 0.256 | 0.493 / 0.493 | 0.806 / 0.806 | 0.157 / 0.157 | 1.0 / 1.0 |
| v1.1 | narrative | 3 | 0.268 / 0.268 | 0.53 / 0.53 | 0.729 / 0.729 | 0.134 / 0.134 | 0.889 / 0.889 |
| v2.0 | console | 5 | 0.324 / 0.324 | 0.623 / 0.623 | 0.781 / 0.781 | 0.11 / 0.11 | 0.8 / 0.8 |
| v2.0 | narrative | 3 | 0.261 / 0.261 | 0.521 / 0.521 | 0.567 / 0.567 | 0.135 / 0.135 | 0.778 / 0.778 |
| v2.1 | console | 5 | 0.249 / 0.074 | 0.44 / 0.196 | 0.684 / 0.26 | 0.077 / 0.024 | 0.8 / 0.4 |
| v2.1 | narrative | 3 | 0.255 / 0.255 | 0.514 / 0.514 | 0.542 / 0.542 | 0.189 / 0.189 | 0.889 / 0.889 |

### within brief across seeds

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff | hueEMD raw / eff | familyJaccard raw / eff |
|---|---|---|---|---|---|---|---|
| none | console | 1 | 0.221 / 0.0 | 1.0 / 0.0 | 0.786 / 0.0 | 0.106 / 0.0 | 1.0 / 0.0 |
| v1.1 | console | 1 | 0.253 / 0.253 | 0.503 / 0.503 | 0.734 / 0.734 | 0.051 / 0.051 | 0.0 / 0.0 |
| v2.0 | console | 1 | 0.22 / 0.22 | 0.806 / 0.806 | 0.737 / 0.737 | 0.051 / 0.051 | 1.0 / 1.0 |
| v2.1 | console | 1 | 0.228 / 0.228 | 0.589 / 0.589 | 0.563 / 0.563 | 0.027 / 0.027 | 1.0 / 1.0 |

### D2 — accent hue dispersion and ground, per arm

| arm | builds | accent hues | dispersion (1 − R̄) | eff. dispersion | grounds (L, hue) | dark grounds |
|---|---|---|---|---|---|---|
| none | 8 | 295, 39, 30, 38, 23, 30, 32, 21 | 0.134 | 0.004 | 0.153/260 0.959/87 0.922/89 0.977/86 0.149/260 0.947/88 0.959/88 0.162/254 | 3 |
| v1.1 | 8 | 48, 46, 23, 285, 27, 265, 318, 43 | 0.395 | 0.395 | 0.972/229 0.969/301 0.975/106 0.945/215 0.979/90 0.926/248 0.32/209 0.972/229 | 1 |
| v2.0 | 8 | 249, 282, 22, 28, 68, 63, 256, 28 | 0.608 | 0.608 | 0.168/59 0.962/214 0.979/248 0.963/197 0.883/25 0.944/217 0.932/248 0.183/85 | 2 |
| v2.1 | 8 | 27, 26, 220, 24, 252, 58, 27 | 0.542 | 0.631 | 0.214/71 0.978/258 0.94/271 0.968/237 0.958/90 0.954/197 0.952/242 0.973/90 | 1 |

### D3 — families per arm

| arm | display families (distinct / builds) | body families | mono |
|---|---|---|---|
| none | 4/8: -apple-system, Inter, Iowan Old Style, Superclarendon | 4/8: -apple-system, Inter, Iowan Old Style, ui-sans-serif | 1/8: ui-monospace |
| v1.1 | 6/8: Archivo, Barlow, Barlow Condensed, Figtree, Source Serif 4, Zilla Slab | 6/8: Barlow, Figtree, Lexend, Public Sans, Source Sans 3, Source Serif 4 | 4/8: Azeret Mono, DM Mono, Geist Mono, Roboto Mono |
| v2.0 | 5/8: Atkinson Hyperlegible Next, Barlow Condensed, Commissioner, Literata, Zilla Slab | 4/8: Atkinson Hyperlegible Next, Barlow, Cabin, Commissioner | 5/8: Atkinson Hyperlegible Mono, Azeret Mono, Fragment Mono, Geist Mono, JetBrains Mono |
| v2.1 | 7/8: Archivo Narrow, Atkinson Hyperlegible Next, Barlow, Barlow Condensed, JetBrains Mono, Lexend, Zilla Slab | 6/8: Atkinson Hyperlegible Next, Barlow, Commissioner, JetBrains Mono, Lexend, Public Sans | 4/8: Azeret Mono, Fragment Mono, JetBrains Mono, Roboto Mono |

### D4 — canonical shapes per arm and category

| arm | category | n | side region | rail band ≥1.5:1 | stat row (fv) | three-up | cards (fv) | headline band | dominant share ≥ 0.4 |
|---|---|---|---|---|---|---|---|---|---|
| none | console | 4 | 2 | 1 | 1 | 0 | 0 | 0 | 2 |
| none | narrative | 3 | 0 | 2 | 2 | 2 | 1 | 1 | 1 |
| none | pair | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |
| v1.1 | console | 4 | 0 | 3 | 1 | 0 | 0 | 0 | 1 |
| v1.1 | narrative | 3 | 0 | 2 | 0 | 2 | 0 | 0 | 1 |
| v1.1 | pair | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| v2.0 | console | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 0 |
| v2.0 | narrative | 3 | 0 | 1 | 0 | 0 | 2 | 0 | 1 |
| v2.0 | pair | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 |
| v2.1 | console | 4 | 0 | 4 | 0 | 0 | 0 | 0 | 2 |
| v2.1 | narrative | 3 | 0 | 3 | 0 | 1 | 1 | 0 | 0 |
| v2.1 | pair | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |

## Per-build reads

| id | brief | arm | seed | ground | accent | hues | display / body / mono | dominant | dominance | side | stat | 3-up | height | BT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ede597 | compare | none | A | #F4F1EA L0.959 | #8C2F1F h32.1 | 2 | Iowan Old Style / -apple-system / ui-monospace | card-grid 0.11 | peers | band |  |  | 6.5vh | — |
| 32cc11 | compare | v1.1 | A | #11393F L0.32 | #7D3792 h317.7 | 2 | Figtree / Figtree / DM Mono | chart 1 | hero | band |  |  | 4.2vh | — |
| 033fcb | compare | v2.0 | A | #E4E9EE L0.932 | #205BA3 h255.6 | 1 | Barlow Condensed / Commissioner / Azeret Mono | text 0.051 | peers | band |  | y | 4.9vh | — |
| d178d1 | compare | v2.1 | A | #EBF0F4 L0.952 | #7A430E h58.1 | 1 | Lexend / Commissioner / JetBrains Mono | list 0.131 | peers |  |  | y | 3.9vh | — |
| ae0658 | fleet | none | A | #080B10 L0.149 | #FF6B6B h22.8 | 5 | None / ui-sans-serif / ui-monospace | table 0.47 | dominant | y |  |  | 1.0vh | — |
| 7e71b0 | fleet | v1.1 | A | #F8F8F8 L0.979 | #B91C1E h27.1 | 2 | Barlow / Barlow / Geist Mono | table 0.18 | dominant | band |  |  | 2.5vh | — |
| 4e40b0 | fleet | v2.0 | A | #DFD6D5 L0.883 | #B97515 h67.9 | 2 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | table 0.271 | hero | band |  |  | 3.2vh | — |
| 49e6cb | fleet | v2.1 | A | #F1F1F1 L0.958 | #9E2C2E h24.2 | 3 | Barlow / Barlow / JetBrains Mono | list 0.456 | hero | band |  |  | 2.6vh | — |
| 4d761e | hardware | none | A | #F2EDE1 L0.947 | #A02C20 h29.8 | 1 | -apple-system / Iowan Old Style / None | chart 0.16 | dominant |  |  |  | 8.4vh | — |
| 5c24f6 | hardware | v1.1 | A | #E3E7EB L0.926 | #1A41BA h265 | 1 | Barlow Condensed / Source Serif 4 / Roboto Mono | block 1 | hero | band |  | y | 6.3vh | — |
| 0663a2 | hardware | v2.0 | A | #E7EEF0 L0.944 | #693B03 h62.7 | 1 | Zilla Slab / Cabin / Fragment Mono | list 0.1 | peers |  |  |  | 5.5vh | — |
| c7de7e | hardware | v2.1 | A | #E9F2F2 L0.954 | #215D99 h251.7 | 1 | Barlow Condensed / Public Sans / Azeret Mono | list 0.119 | dominant | band |  |  | 5.7vh | — |
| 30f897 | library | none | A | #FCF7EC L0.977 | #C24A22 h37.9 | 2 | Superclarendon / ui-sans-serif / None | heading 0.634 | hero | band | y | y | 6.8vh | — |
| dd3f5c | library | v1.1 | A | #D1F4FD L0.945 | #5F4BC7 h285.1 | 1 | Source Serif 4 / Lexend / None | heading 0.078 | peers | band |  |  | 6.7vh | — |
| 99499b | library | v2.0 | A | #E9F6F6 L0.963 | #B12D26 h28 | 1 | Literata / Atkinson Hyperlegible Next / Fragment Mono | panel 0.403 | hero |  |  |  | 6.4vh | — |
| 672565 | library | v2.1 | A | #EDF6FC L0.968 | #00758F h220.4 | 1 | Zilla Slab / Lexend / Fragment Mono | card-grid 0.14 | peers | band |  | y | 7.1vh | — |
| 122077 | pharmacy | none | A | #E7E5E0 L0.922 | #A52A1C h30.3 | 2 | Inter / Inter / ui-monospace | rail 0.276 | peers | y |  |  | 1.0vh | — |
| 002ea9 | pharmacy | v1.1 | A | #F7F7F3 L0.975 | #A34242 h22.8 | 4 | Source Serif 4 / Source Sans 3 / Roboto Mono | list 0.33 | hero | band |  |  | 4.1vh | — |
| 3ba9f0 | pharmacy | v2.0 | A | #F7F8F9 L0.979 | #98252D h22.1 | 4 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / Atkinson Hyperlegible Mono | list 0.301 | hero | band |  |  | 2.6vh | — |
| f344b7 | pharmacy | v2.1 | A | #EAEBEE L0.94 | #A12626 h25.9 | 4 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | list 0.419 | dominant | band |  |  | 2.6vh | — |
| c183ef | rail | none | A | #090C11 L0.153 | #A888FA h294.8 | 1 | None / -apple-system / ui-monospace | list 0.949 | hero | band | y |  | 1.0vh | — |
| e44b85 | rail | none | B | #0A0E13 L0.162 | #F0575E h21.3 | 4 | None / Inter / ui-monospace | chart 0.274 | peers |  |  |  | 1.0vh | — |
| 8ef70a | rail | v1.1 | A | #F4F6F7 L0.972 | #D46B2C h48 | 3 | Archivo / Public Sans / Geist Mono | list 0.319 | peers |  |  |  | 1.4vh | -3.08 |
| a903f5 | rail | v1.1 | B | #F4F6F7 L0.972 | #8C3C17 h42.7 | 1 | Archivo / Public Sans / Geist Mono | block 0.543 | hero | band | y |  | 2.8vh | — |
| cb9845 | rail | v2.0 | A | #120E0B L0.168 | #4197E5 h249 | 1 | Commissioner / Commissioner / JetBrains Mono | chart 0.291 | dominant | band |  |  | 1.9vh | +1.00 |
| 92cba1 | rail | v2.0 | B | #14120E L0.183 | #F47062 h28.1 | 4 | None / Barlow / JetBrains Mono | table 0.29 | peers | band |  |  | 1.0vh | — |
| 8d1d23 | rail | v2.1 | A | #1E1811 L0.214 | #F66D62 h27 | 4 | None / Barlow / JetBrains Mono | chart 0.334 | peers | band |  |  | 1.8vh | -1.43 |
| 661e66 | rail | v2.1 | B | #F6F6F6 L0.973 | #A3322C h27.2 | 1 | JetBrains Mono / JetBrains Mono / JetBrains Mono | chart 0.392 | dominant | band |  |  | 2.2vh | — |
| c78373 | rebate | none | A | #F5F1E8 L0.959 | #A9411A h39.2 | 1 | Iowan Old Style / ui-sans-serif / ui-monospace | heading 0.142 | dominant | band | y | y | 12.1vh | +0.67 |
| cbd040 | rebate | v1.1 | A | #F5F4F7 L0.969 | #FF7729 h45.8 | 2 | Zilla Slab / Public Sans / Azeret Mono | heading 0.065 | dominant |  |  | y | 7.9vh | — |
| 5d884a | rebate | v2.0 | A | #ECF4F6 L0.962 | #4A41A7 h281.8 | 1 | Zilla Slab / Atkinson Hyperlegible Next / Geist Mono | heading 0.07 | peers | band |  |  | 7.9vh | — |
| 7acb2c | rebate | v2.1 | A | #F6F8FB L0.978 | — h | 0 | Archivo Narrow / Public Sans / Roboto Mono | block 0.09 | dominant | band |  |  | 9.4vh | -3.02 |

## F — structural fit (blinded rater, secondary)

| arm | builds | mean yes of 5 |
|---|---|---|
| none | 2 | 2.00 |
| v1.1 | 2 | 2.50 |
| v2.0 | 2 | 3.50 |
| v2.1 | 2 | 5.00 |

## P — fleet against compare, per arm (all four distances)

| arm | fleet seed | partition | raster | pqgram | sig | compare dominant | fleet dominant |
|---|---|---|---|---|---|---|---|
| none | A | 0.316 | 0.964 | 0.606 | 0.75 | card-grid | table |
| v1.1 | A | 0.305 | 0.922 | 0.442 | 0.333 | chart | table |
| v2.0 | A | 0.368 | 0.734 | 0.427 | 0.417 | text | table |
| v2.1 | A | 0.284 | 0.732 | 0.617 | 0.5 | list | list |
