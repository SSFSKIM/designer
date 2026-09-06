# Settling experiment — results

Builds measured: 52 of 52. Judgments: 3. Topology: yes. Fit ratings: 52.

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
| c78373 | rebate | none | A | fail | 1/1 | contrast 0.758 |
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
| 758523 | pharmacy | none | B | fail | 0/0 | contrast 0.499 |
| 10b239 | pharmacy | v1.1 | B | pass | 0/0 | pass |
| 42b5a3 | pharmacy | v2.0 | B | pass | 0/0 | pass |
| 5e2273 | pharmacy | v2.1 | B | pass | 0/0 | pass |
| f77261 | rebate | none | B | pass | 0/0 | pass |
| c7de4a | rebate | v1.1 | B | pass | 0/0 | pass |
| ea1cfd | rebate | v2.0 | B | pass | 0/0 | pass |
| dcf135 | rebate | v2.1 | B | pass | 0/0 | pass |
| 865572 | fleet | none | B | pass | 0/0 | pass |
| 1a63c5 | fleet | v1.1 | B | pass | 0/0 | pass |
| 645bc6 | fleet | v2.0 | B | pass | 0/0 | pass |
| f8973a | fleet | v2.1 | B | pass | 0/0 | pass |
| 5c042a | library | none | B | fail | 0/0 | contrast 0.801 |
| b0bad8 | library | v1.1 | B | pass | 0/0 | pass |
| f3d810 | library | v2.0 | B | pass | 0/0 | pass |
| 8f113d | library | v2.1 | B | pass | 0/0 | pass |
| 70aa0a | hardware | none | B | pass | 0/0 | pass |
| ccf94b | hardware | v1.1 | B | pass | 0/0 | pass |
| b2095d | hardware | v2.0 | B | pass | 0/0 | pass |
| aa615a | hardware | v2.1 | B | pass | 0/0 | pass |

## D — diversity per arm (mean pairwise; effective = Shypula pairwise form with the gate)

### across briefs within category

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff | hueEMD raw / eff | familyJaccard raw / eff |
|---|---|---|---|---|---|---|---|
| none | console | 12 | 0.247 / 0.0 | 0.688 / 0.0 | 0.712 / 0.0 | 0.142 / 0.0 | 0.667 / 0.0 |
| none | narrative | 12 | 0.24 / 0.099 | 0.427 / 0.152 | 0.654 / 0.279 | 0.199 / 0.095 | 0.917 / 0.389 |
| v1.1 | console | 12 | 0.257 / 0.257 | 0.483 / 0.483 | 0.757 / 0.757 | 0.165 / 0.165 | 0.944 / 0.944 |
| v1.1 | narrative | 12 | 0.254 / 0.254 | 0.59 / 0.59 | 0.752 / 0.752 | 0.254 / 0.254 | 0.903 / 0.903 |
| v2.0 | console | 12 | 0.308 / 0.308 | 0.616 / 0.616 | 0.813 / 0.813 | 0.089 / 0.089 | 0.75 / 0.75 |
| v2.0 | narrative | 12 | 0.27 / 0.27 | 0.601 / 0.601 | 0.712 / 0.712 | 0.242 / 0.242 | 0.75 / 0.75 |
| v2.1 | console | 12 | 0.212 / 0.115 | 0.601 / 0.432 | 0.606 / 0.382 | 0.084 / 0.054 | 0.917 / 0.667 |
| v2.1 | narrative | 12 | 0.273 / 0.273 | 0.5 / 0.5 | 0.588 / 0.588 | 0.213 / 0.213 | 0.944 / 0.944 |

### within brief across seeds

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff | hueEMD raw / eff | familyJaccard raw / eff |
|---|---|---|---|---|---|---|---|
| none | console | 3 | 0.247 / 0.075 | 0.725 / 0.193 | 0.797 / 0.266 | 0.127 / 0.052 | 1.0 / 0.333 |
| none | narrative | 3 | 0.2 / 0.05 | 0.4 / 0.133 | 0.498 / 0.098 | 0.213 / 0.031 | 0.778 / 0.222 |
| v1.1 | console | 3 | 0.257 / 0.257 | 0.442 / 0.442 | 0.623 / 0.623 | 0.172 / 0.172 | 0.667 / 0.667 |
| v1.1 | narrative | 3 | 0.262 / 0.262 | 0.598 / 0.598 | 0.602 / 0.602 | 0.306 / 0.306 | 1.0 / 1.0 |
| v2.0 | console | 3 | 0.215 / 0.215 | 0.625 / 0.625 | 0.699 / 0.699 | 0.071 / 0.071 | 0.667 / 0.667 |
| v2.0 | narrative | 3 | 0.271 / 0.271 | 0.468 / 0.468 | 0.701 / 0.701 | 0.299 / 0.299 | 0.778 / 0.778 |
| v2.1 | console | 3 | 0.193 / 0.119 | 0.684 / 0.469 | 0.44 / 0.276 | 0.045 / 0.036 | 0.667 / 0.333 |
| v2.1 | narrative | 3 | 0.264 / 0.264 | 0.393 / 0.393 | 0.596 / 0.596 | 0.171 / 0.171 | 0.778 / 0.778 |

### D2 — accent hue dispersion and ground, per arm

| arm | builds | accent hues | dispersion (1 − R̄) | eff. dispersion | grounds (L, hue) | dark grounds |
|---|---|---|---|---|---|---|
| none | 13 | 295, 39, 30, 38, 23, 30, 32, 21, 74, 221, 73, 27, 32 | 0.282 | 0.037 | 0.153/260 0.959/87 0.922/89 0.977/86 0.149/260 0.947/88 0.959/88 0.162/254 0.968/85 0.939/248 0.978/78 0.171/257 0.962/87 | 4 |
| v1.1 | 13 | 48, 46, 23, 285, 27, 265, 318, 43, 38, 25, 55, 295, 31 | 0.34 | 0.34 | 0.972/229 0.969/301 0.975/106 0.945/215 0.979/90 0.926/248 0.32/209 0.972/229 1/90 0.236/293 0.296/161 0.972/229 0.203/168 | 4 |
| v2.0 | 13 | 249, 282, 22, 28, 68, 63, 256, 28, 27, 62, 28, 30, 26 | 0.405 | 0.405 | 0.168/59 0.962/214 0.979/248 0.963/197 0.883/25 0.944/217 0.932/248 0.183/85 0.985/271 0.963/248 0.885/143 0.94/90 0.952/17 | 2 |
| v2.1 | 13 | 27, 26, 220, 24, 252, 58, 27, 58, 27, 32, 26, 248 | 0.475 | 0.518 | 0.214/71 0.978/258 0.94/271 0.968/237 0.958/90 0.954/197 0.952/242 0.973/90 0.951/209 0.957/258 0.679/192 0.931/224 0.932/236 | 1 |

### D2 supplement — accent job, and dispersion over directional accents only

Added after wave five (Decision Log): on a build whose interactive layer is achromatic the extractor's fallback reads the loudest status colour, so the D2 hue list above mixes chosen accents with critical reds. Here the job is the declared one for the 2.x arms and inferred from the extractor's locus for the others.

| arm | builds | directional | status-only | none | hues (directional) | dispersion | eff. dispersion |
|---|---|---|---|---|---|---|---|
| none | 13 | 10 | 0 | 3 | 295, 39, 30, 38, 30, 74, 221, 73, 27, 32 | 0.362 | 0.044 |
| v1.1 | 13 | 12 | 0 | 1 | 48, 46, 23, 285, 27, 265, 43, 38, 25, 55, 295, 31 | 0.33 | 0.33 |
| v2.0 | 13 | 6 | 3 | 4 | 249, 282, 28, 256, 28, 26 | 0.546 | 0.546 |
| v2.1 | 13 | 7 | 4 | 2 | 220, 252, 58, 58, 32, 26, 248 | 0.805 | 0.805 |

### D3 — families per arm

| arm | display families (distinct / builds) | body families | mono |
|---|---|---|---|
| none | 7/13: -apple-system, Inter, Iowan Old Style, Rockwell, Superclarendon, ui-rounded, ui-serif | 5/13: -apple-system, Inter, Iowan Old Style, system-ui, ui-sans-serif | 1/13: ui-monospace |
| v1.1 | 8/13: Archivo, Azeret Mono, Barlow, Barlow Condensed, Figtree, Lexend, Source Serif 4, Zilla Slab | 8/13: Archivo, Atkinson Hyperlegible Next, Barlow, Figtree, Lexend, Public Sans, Source Sans 3, Source Serif 4 | 4/13: Azeret Mono, DM Mono, Geist Mono, Roboto Mono |
| v2.0 | 7/13: Archivo Narrow, Atkinson Hyperlegible Next, Barlow, Barlow Condensed, Commissioner, Literata, Zilla Slab | 4/13: Atkinson Hyperlegible Next, Barlow, Cabin, Commissioner | 6/13: Atkinson Hyperlegible Mono, Azeret Mono, Fragment Mono, Geist Mono, JetBrains Mono, Roboto Mono |
| v2.1 | 9/13: Archivo Narrow, Arvo, Atkinson Hyperlegible Next, Barlow, Barlow Condensed, Commissioner, JetBrains Mono, Lexend, Zilla Slab | 6/13: Atkinson Hyperlegible Next, Barlow, Commissioner, JetBrains Mono, Lexend, Public Sans | 5/13: Azeret Mono, Fira Mono, Fragment Mono, JetBrains Mono, Roboto Mono |

### D4 — canonical shapes per arm and category

| arm | category | n | side region | rail band ≥1.5:1 | stat row (fv) | three-up | cards (fv) | headline band | dominant share ≥ 0.4 |
|---|---|---|---|---|---|---|---|---|---|
| none | console | 6 | 2 | 3 | 3 | 1 | 0 | 0 | 4 |
| none | narrative | 6 | 0 | 3 | 5 | 5 | 1 | 1 | 1 |
| none | pair | 1 | 0 | 1 | 0 | 0 | 1 | 0 | 0 |
| v1.1 | console | 6 | 0 | 5 | 1 | 0 | 0 | 0 | 1 |
| v1.1 | narrative | 6 | 0 | 5 | 0 | 5 | 0 | 0 | 2 |
| v1.1 | pair | 1 | 0 | 1 | 0 | 0 | 0 | 0 | 1 |
| v2.0 | console | 6 | 1 | 6 | 1 | 0 | 0 | 0 | 0 |
| v2.0 | narrative | 6 | 0 | 4 | 1 | 3 | 2 | 0 | 2 |
| v2.0 | pair | 1 | 0 | 1 | 0 | 1 | 0 | 0 | 0 |
| v2.1 | console | 6 | 0 | 6 | 0 | 0 | 0 | 0 | 4 |
| v2.1 | narrative | 6 | 0 | 6 | 1 | 3 | 2 | 0 | 0 |
| v2.1 | pair | 1 | 0 | 0 | 0 | 1 | 0 | 0 | 0 |

## Per-build reads

| id | brief | arm | seed | ground | accent | hues | display / body / mono | dominant | dominance | side | stat | 3-up | height | BT |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ede597 | compare | none | A | #F4F1EA L0.959 | #8C2F1F h32.1 | 2 | Iowan Old Style / -apple-system / ui-monospace | card-grid 0.11 | peers | band |  |  | 6.5vh | — |
| 32cc11 | compare | v1.1 | A | #11393F L0.32 | #7D3792 h317.7 | 2 | Figtree / Figtree / DM Mono | chart 1 | hero | band |  |  | 4.2vh | — |
| 033fcb | compare | v2.0 | A | #E4E9EE L0.932 | #205BA3 h255.6 | 1 | Barlow Condensed / Commissioner / Azeret Mono | text 0.051 | peers | band |  | y | 4.9vh | — |
| d178d1 | compare | v2.1 | A | #EBF0F4 L0.952 | #7A430E h58.1 | 1 | Lexend / Commissioner / JetBrains Mono | list 0.131 | peers |  |  | y | 3.9vh | — |
| ae0658 | fleet | none | A | #080B10 L0.149 | #FF6B6B h22.8 | 5 | None / ui-sans-serif / ui-monospace | table 0.47 | dominant | y |  |  | 1.0vh | — |
| 865572 | fleet | none | B | #0B1017 L0.171 | #FF6257 h27.2 | 6 | None / -apple-system / ui-monospace | list 0.48 | dominant | band | y |  | 3.0vh | — |
| 7e71b0 | fleet | v1.1 | A | #F8F8F8 L0.979 | #B91C1E h27.1 | 2 | Barlow / Barlow / Geist Mono | table 0.18 | dominant | band |  |  | 2.5vh | — |
| 1a63c5 | fleet | v1.1 | B | #F4F6F7 L0.972 | #5C389F h295.2 | 3 | Zilla Slab / Public Sans / Roboto Mono | list 0.382 | hero | band |  |  | 2.7vh | — |
| 4e40b0 | fleet | v2.0 | A | #DFD6D5 L0.883 | #B97515 h67.9 | 2 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | table 0.271 | hero | band |  |  | 3.2vh | — |
| 645bc6 | fleet | v2.0 | B | #EBEBEB L0.94 | #9C2318 h29.7 | 2 | Barlow / Barlow / JetBrains Mono | list 0.312 | dominant | band | y |  | 3.1vh | — |
| 49e6cb | fleet | v2.1 | A | #F1F1F1 L0.958 | #9E2C2E h24.2 | 3 | Barlow / Barlow / JetBrains Mono | list 0.456 | hero | band |  |  | 2.6vh | — |
| f8973a | fleet | v2.1 | B | #E4E9EB L0.931 | #B6312E h26.5 | 2 | Arvo / Public Sans / Fira Mono | list 0.427 | dominant | band |  |  | 2.6vh | — |
| 4d761e | hardware | none | A | #F2EDE1 L0.947 | #A02C20 h29.8 | 1 | -apple-system / Iowan Old Style / None | chart 0.16 | dominant |  |  |  | 8.4vh | — |
| 70aa0a | hardware | none | B | #F6F2E9 L0.962 | #A8301B h32.3 | 2 | Rockwell / -apple-system / None | chart 0.146 | peers |  | y | y | 6.7vh | — |
| 5c24f6 | hardware | v1.1 | A | #E3E7EB L0.926 | #1A41BA h265 | 1 | Barlow Condensed / Source Serif 4 / Roboto Mono | block 1 | hero | band |  | y | 6.3vh | — |
| ccf94b | hardware | v1.1 | B | #071B14 L0.203 | #BB3A28 h31 | 2 | Archivo / Public Sans / Azeret Mono | list 0.829 | hero | band |  | y | 5.5vh | — |
| 0663a2 | hardware | v2.0 | A | #E7EEF0 L0.944 | #693B03 h62.7 | 1 | Zilla Slab / Cabin / Fragment Mono | list 0.1 | peers |  |  |  | 5.5vh | — |
| b2095d | hardware | v2.0 | B | #F4EDED L0.952 | #7F2C29 h25.5 | 1 | Archivo Narrow / Barlow / Roboto Mono | list 0.859 | hero | band |  | y | 5.8vh | — |
| c7de7e | hardware | v2.1 | A | #E9F2F2 L0.954 | #215D99 h251.7 | 1 | Barlow Condensed / Public Sans / Azeret Mono | list 0.119 | dominant | band |  |  | 5.7vh | — |
| aa615a | hardware | v2.1 | B | #E6E9EB L0.932 | #07558E h248.3 | 1 | Barlow Condensed / Barlow / Azeret Mono | pricing 0.193 | dominant | band |  | y | 4.3vh | — |
| 30f897 | library | none | A | #FCF7EC L0.977 | #C24A22 h37.9 | 2 | Superclarendon / ui-sans-serif / None | heading 0.634 | hero | band | y | y | 6.8vh | — |
| 5c042a | library | none | B | #FDF7EE L0.978 | #F2A31C h73 | 2 | ui-rounded / system-ui / None | heading 0.183 | peers |  | y | y | 8.3vh | — |
| dd3f5c | library | v1.1 | A | #D1F4FD L0.945 | #5F4BC7 h285.1 | 1 | Source Serif 4 / Lexend / None | heading 0.078 | peers | band |  |  | 6.7vh | — |
| b0bad8 | library | v1.1 | B | #153425 L0.296 | #EA883D h54.7 | 1 | Azeret Mono / Atkinson Hyperlegible Next / Azeret Mono | chart 0.265 | hero | band |  | y | 6.9vh | — |
| 99499b | library | v2.0 | A | #E9F6F6 L0.963 | #B12D26 h28 | 1 | Literata / Atkinson Hyperlegible Next / Fragment Mono | panel 0.403 | hero |  |  |  | 6.4vh | — |
| f3d810 | library | v2.0 | B | #BEE6BB L0.885 | #C83B32 h28 | 1 | Zilla Slab / Atkinson Hyperlegible Next / Azeret Mono | heading 0.113 | peers | band |  | y | 7.7vh | — |
| 672565 | library | v2.1 | A | #EDF6FC L0.968 | #00758F h220.4 | 1 | Zilla Slab / Lexend / Fragment Mono | card-grid 0.14 | peers | band |  | y | 7.1vh | — |
| 8f113d | library | v2.1 | B | #3EABA8 L0.679 | #C13A23 h32.2 | 1 | Zilla Slab / Atkinson Hyperlegible Next / Fragment Mono | heading 0.041 | peers | band | y |  | 6.7vh | — |
| 122077 | pharmacy | none | A | #E7E5E0 L0.922 | #A52A1C h30.3 | 2 | Inter / Inter / ui-monospace | rail 0.276 | peers | y |  |  | 1.0vh | — |
| 758523 | pharmacy | none | B | #E8EBEE L0.939 | #0B5A6E h220.8 | 1 | -apple-system / -apple-system / ui-monospace | table 0.497 | hero | band | y | y | 1.9vh | — |
| 002ea9 | pharmacy | v1.1 | A | #F7F7F3 L0.975 | #A34242 h22.8 | 4 | Source Serif 4 / Source Sans 3 / Roboto Mono | list 0.33 | hero | band |  |  | 4.1vh | — |
| 10b239 | pharmacy | v1.1 | B | #201837 L0.236 | #F86E68 h24.9 | 2 | Lexend / Lexend / Geist Mono | list 0.317 | dominant | band |  |  | 3.0vh | — |
| 3ba9f0 | pharmacy | v2.0 | A | #F7F8F9 L0.979 | #98252D h22.1 | 4 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / Atkinson Hyperlegible Mono | list 0.301 | hero | band |  |  | 2.6vh | — |
| 42b5a3 | pharmacy | v2.0 | B | #F1F3F5 L0.963 | #653908 h61.7 | 1 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | table 0.185 | dominant | y |  |  | 2.9vh | — |
| f344b7 | pharmacy | v2.1 | A | #EAEBEE L0.94 | #A12626 h25.9 | 4 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | list 0.419 | dominant | band |  |  | 2.6vh | — |
| 5e2273 | pharmacy | v2.1 | B | #EFF1F4 L0.957 | #9E2D28 h27.1 | 4 | Atkinson Hyperlegible Next / Atkinson Hyperlegible Next / JetBrains Mono | list 0.909 | hero | band |  |  | 2.5vh | — |
| c183ef | rail | none | A | #090C11 L0.153 | #A888FA h294.8 | 1 | None / -apple-system / ui-monospace | list 0.949 | hero | band | y |  | 1.0vh | — |
| e44b85 | rail | none | B | #0A0E13 L0.162 | #F0575E h21.3 | 4 | None / Inter / ui-monospace | chart 0.274 | peers |  |  |  | 1.0vh | — |
| 8ef70a | rail | v1.1 | A | #F4F6F7 L0.972 | #D46B2C h48 | 3 | Archivo / Public Sans / Geist Mono | list 0.319 | peers |  |  |  | 1.4vh | -3.08 |
| a903f5 | rail | v1.1 | B | #F4F6F7 L0.972 | #8C3C17 h42.7 | 1 | Archivo / Public Sans / Geist Mono | block 0.543 | hero | band | y |  | 2.8vh | — |
| cb9845 | rail | v2.0 | A | #120E0B L0.168 | #4197E5 h249 | 1 | Commissioner / Commissioner / JetBrains Mono | chart 0.291 | dominant | band |  |  | 1.9vh | +1.00 |
| 92cba1 | rail | v2.0 | B | #14120E L0.183 | #F47062 h28.1 | 4 | None / Barlow / JetBrains Mono | table 0.29 | peers | band |  |  | 1.0vh | — |
| 8d1d23 | rail | v2.1 | A | #1E1811 L0.214 | #F66D62 h27 | 4 | None / Barlow / JetBrains Mono | chart 0.334 | peers | band |  |  | 1.8vh | -1.43 |
| 661e66 | rail | v2.1 | B | #F6F6F6 L0.973 | #A3322C h27.2 | 1 | JetBrains Mono / JetBrains Mono / JetBrains Mono | chart 0.392 | dominant | band |  |  | 2.2vh | — |
| c78373 | rebate | none | A | #F5F1E8 L0.959 | #A9411A h39.2 | 1 | Iowan Old Style / ui-sans-serif / ui-monospace | heading 0.142 | dominant | band | y | y | 12.1vh | +0.67 |
| f77261 | rebate | none | B | #F7F4EE L0.968 | #F0A93C h73.7 | 2 | ui-serif / ui-sans-serif / ui-monospace | heading 0.093 | peers | band | y | y | 12.8vh | — |
| cbd040 | rebate | v1.1 | A | #F5F4F7 L0.969 | #FF7729 h45.8 | 2 | Zilla Slab / Public Sans / Azeret Mono | heading 0.065 | dominant |  |  | y | 7.9vh | — |
| c7de4a | rebate | v1.1 | B | #FFFFFF L1 | #C74413 h38 | 1 | Archivo / Archivo / Roboto Mono | list 0.097 | peers | band |  | y | 7.1vh | — |
| 5d884a | rebate | v2.0 | A | #ECF4F6 L0.962 | #4A41A7 h281.8 | 1 | Zilla Slab / Atkinson Hyperlegible Next / Geist Mono | heading 0.07 | peers | band |  |  | 7.9vh | — |
| ea1cfd | rebate | v2.0 | B | #F9FAFD L0.985 | #702520 h27.2 | 3 | Barlow / Atkinson Hyperlegible Next / Azeret Mono | list 0.107 | peers | band | y | y | 9.7vh | — |
| 7acb2c | rebate | v2.1 | A | #F6F8FB L0.978 | — h | 0 | Archivo Narrow / Public Sans / Roboto Mono | block 0.09 | dominant | band |  |  | 9.4vh | -3.02 |
| dcf135 | rebate | v2.1 | B | #EAF0F1 L0.951 | #7C481B h57.8 | 1 | Commissioner / Atkinson Hyperlegible Next / Azeret Mono | list 0.2 | hero | band |  | y | 7.9vh | — |

## F — structural fit (blinded rater, secondary)

| arm | builds | mean yes of 5 |
|---|---|---|
| none | 13 | 3.38 |
| v1.1 | 13 | 4.23 |
| v2.0 | 13 | 4.23 |
| v2.1 | 13 | 4.62 |

## P — fleet against compare, per arm (all four distances)

| arm | fleet seed | partition | raster | pqgram | sig | compare dominant | fleet dominant |
|---|---|---|---|---|---|---|---|
| none | A | 0.315 | 0.964 | 0.606 | 0.75 | card-grid | table |
| none | B | 0.301 | 0.932 | 0.489 | 0.5 | card-grid | list |
| v1.1 | A | 0.305 | 0.922 | 0.442 | 0.333 | chart | table |
| v1.1 | B | 0.284 | 0.956 | 0.508 | 0.25 | chart | list |
| v2.0 | A | 0.368 | 0.734 | 0.427 | 0.417 | text | table |
| v2.0 | B | 0.302 | 0.667 | 0.697 | 0.5 | text | list |
| v2.1 | A | 0.284 | 0.732 | 0.617 | 0.5 | list | list |
| v2.1 | B | 0.258 | 0.815 | 0.541 | 0.5 | list | list |
