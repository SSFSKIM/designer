# Layout-arm run — results

New arms: v2.4. New builds measured: 13 of 13. Baseline builds: 52 of 52. Combined topology: yes, 65 pages. Fit (this run's frame): 65 pages. Rubric raters in this run: 4.

## V — the gate per new build

| id | brief | arm | seed | gate | DESIGN.md |
|---|---|---|---|---|---|
| ffb439 | compare | v2.4 | A | pass | yes |
| 126c4c | fleet | v2.4 | A | pass | yes |
| 0cb4c1 | fleet | v2.4 | B | pass | yes |
| 392ab5 | hardware | v2.4 | A | pass | yes |
| 8d4ab7 | hardware | v2.4 | B | pass | yes |
| 2cc1d7 | library | v2.4 | A | pass | yes |
| 1850b3 | library | v2.4 | B | pass | yes |
| 5971c1 | pharmacy | v2.4 | A | pass | yes |
| 37e667 | pharmacy | v2.4 | B | pass | yes |
| 485d8c | rail | v2.4 | A | pass | yes |
| b8dca3 | rail | v2.4 | B | pass | yes |
| 077ea7 | rebate | v2.4 | A | pass | yes |
| bf9530 | rebate | v2.4 | B | pass | yes |

| arm | built | mechanical pass | contrast fails | overflow (load / capture) |
|---|---|---|---|---|
| none | 13 | 7 | 6 | 0 / 0 |
| v1.1 | 13 | 13 | 0 | 0 / 0 |
| v2.0 | 13 | 13 | 0 | 0 / 0 |
| v2.1 | 13 | 11 | 0 | 1 / 2 |
| v2.4 | 13 | 13 | 0 | 0 / 0 |

## R — the record, per new build

Nine axis lines and six composition lines are counted by label; the rest are presence reads of the record's own words. A record that names the ledger is one whose derivation cites a neighbour.

| id | brief | arm | lines | §0 axes /9 | §4 lines /6 | rejected vector | candidates | sampler | signature | accent job | names the ledger |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ffb439 | compare | v2.4 | 215 | 9 | 6 | y | y | y | y | directional | - |
| 126c4c | fleet | v2.4 | 228 | 9 | 6 | y | y | y | - | none | y |
| 0cb4c1 | fleet | v2.4 | 225 | 9 | 6 | y | y | y | y | status-only | y |
| 392ab5 | hardware | v2.4 | 227 | 9 | 6 | y | y | y | y | directional | y |
| 8d4ab7 | hardware | v2.4 | 254 | 9 | 6 | y | y | y | y | directional | - |
| 2cc1d7 | library | v2.4 | 222 | 9 | 6 | y | y | y | y | directional | y |
| 1850b3 | library | v2.4 | 192 | 9 | 5 | y | y | y | y | atmospheric | y |
| 5971c1 | pharmacy | v2.4 | 221 | 9 | 5 | y | y | y | y | none | y |
| 37e667 | pharmacy | v2.4 | 247 | 9 | 6 | y | y | y | y | none | y |
| 485d8c | rail | v2.4 | 235 | 9 | 6 | y | y | y | y | none | - |
| b8dca3 | rail | v2.4 | 204 | 9 | 6 | y | y | y | - | none | - |
| 077ea7 | rebate | v2.4 | 224 | 9 | 6 | y | - | y | y | directional | y |
| bf9530 | rebate | v2.4 | 202 | 9 | 6 | y | y | y | y | directional | y |

- v2.4: records 13 of 13; mean lines 223; all nine axes on 13; all six lines on 11; candidates recorded on 12; sampler recorded on 13.

## L — the ledger reading

Per build: the seeded entries the agent could see, whether it ran `nearest` (reports saved) and `record` (an entry appended), the flags it was shown, and whether what it shipped sits inside a band it was shown — the display family it was told was already used, or an accent within 30° of a flagged hue. A build that saw a flag and shipped inside the band is not a fault by itself; the record column R says whether it named the neighbour.

| id | brief | arm | seeded | nearest runs | flags shown (kinds) | recorded | shipped display | shipped accent | inside a shown band |
|---|---|---|---|---|---|---|---|---|---|
| ffb439 | compare | v2.4 | 36 | 5 | 13 (signature) | 1 | Cabin | 70° directional | — |
| 126c4c | fleet | v2.4 | 33 | 5 | 10 (family, ground, signature) | 1 | Fira Sans | none | — |
| 0cb4c1 | fleet | v2.4 | 33 | 4 | 5 (form, signature) | 1 | Bitter | none | — |
| 392ab5 | hardware | v2.4 | 33 | 4 | 2 (signature) | 1 | Chivo | 93° directional | — |
| 8d4ab7 | hardware | v2.4 | 33 | 3 | 8 (signature) | 1 | League Gothic | 95° directional | — |
| 2cc1d7 | library | v2.4 | 33 | 5 | 10 (accent, signature) | 1 | Young Serif | 205° directional | — |
| 1850b3 | library | v2.4 | 33 | 4 | 12 (accent, family, signature) | 1 | Alegreya Sans | — | — |
| 5971c1 | pharmacy | v2.4 | 33 | 5 | 3 (family, form) | 1 | Fira Sans | none | — |
| 37e667 | pharmacy | v2.4 | 33 | 5 | 8 (family, form, signature) | 1 | Radio Canada | none | — |
| 485d8c | rail | v2.4 | 33 | 4 | 6 (ground, signature) | 1 | — | none | — |
| b8dca3 | rail | v2.4 | 33 | 5 | 7 (family, signature) | 1 | B612 | none | — |
| 077ea7 | rebate | v2.4 | 33 | 5 | 17 (accent, form, ground, signature) | 1 | Rokkitt | 96° directional | — |
| bf9530 | rebate | v2.4 | 33 | 5 | 8 (accent, ground, signature) | 1 | Instrument Sans | 90° directional | — |

- v2.4: ran `nearest` on 13 of 13, appended a record on 13, shipped inside a shown band on 0, of which 0 name the neighbour in the record.

**Signature motifs across seeds** (the stamp-card test): content words of five letters or more shared by the two seeds' signature lines, per brief and arm; the settling run's derivation arms shared the stamp on the library brief and the ticket on the hardware brief.

| brief | arm | seed A signature | seed B signature | shared words |
|---|---|---|---|---|
| fleet | v2.0 | The availability ladder: one ordered severity scale, printed once | The shift ruler and the eight bays hung from it: one 05:00 to 19:00 | — |
| fleet | v2.1 | the deadline ruler. Every row in the exception queue shares one horizontal | — | — |
| fleet | v2.4 | — | The fleet number is the name. Staff say "4471", never the registration, | — |
| hardware | v2.0 | The shelf tag. Every purchasable thing on the page carries a | The shelf-edge price rail: bin code, condensed name, spec line, | — |
| hardware | v2.1 | The drawn counter plate. Every featured item is a monoline catalog drawing in | The shelf-edge tag: a paper strip with a clip flange, a stenciled bin | — |
| hardware | v2.4 | The shelf tag: every tool is sold from a tag laid out like the one on the | the store plan. A drawn floor plan of 218 Front Street in the | — |
| library | v2.0 | The stamped reader's card. A 4×2 grid of stamp boxes in | the reading-log grid. One square at three sizes: the town progress board in | — |
| library | v2.1 | The stamp. A slab-lettered rounded-rect mark, drawn in ink with a 2px poppy | the stamp sheet. Ten perforated week-stamps in the hero: postmarked for the weeks | stamp |
| library | v2.4 | Two readers, two pages. Each split band divides at one vertical line into | The climb map: contour lines are reading minutes, the trail is fifty dots of | — |
| pharmacy | v2.0 | The fill rule: a flat 6px band under every on-hand quantity, filled to | The ink-ruled control block — the FDA boxed-warning form borrowed | — |
| pharmacy | v2.1 | The numbered witness gutter: in the controlled-substance | The tall-man name column. Every drug name is set the way the | — |
| pharmacy | v2.4 | Tall Man drug names: every look-alike name on the ISMP list carries its | The auxiliary-label sticker: a solid die-cut rectangle with one word, | — |
| rail | v2.0 | the stringline. A time-distance train graph: mileposts up, six hours across, | the stringline board — milepost down, clock across, each train a | across, stringline, train |
| rail | v2.1 | The territory graph: an eight-hour train graph, milepost against time, | The corridor chart — a live string-line (time against distance) diagram in the | against |
| rail | v2.4 | The train graph (string-line): every train a sloped path on one | — | — |
| rebate | v2.0 | The rate-schedule leader line: a label, a dotted leader, a right-aligned | The rebate worksheet: a printed fee-schedule ledger that computes in | — |
| rebate | v2.1 | — | the determination sheet. The page's dominant region is a form-shaped instrument | — |
| rebate | v2.4 | The reservation line: a 6px ink rule, the only heavy line in a hairline | The worked sum: 13.5 kWh × $300 = $4,050, set at display size in the | — |

## F — fit, the headline

The blinded structural rater's five yes/no questions per category, this run's reading: one rater per brief saw the baseline's eight pages and the new arms' pages in one frame. Mean yes-of-five per arm with a bootstrap interval; then the new arms paired with `v2.1` and `v2.0` by brief and seed.

| arm | mean yes-of-five (this frame) | pages | settling run's own reading |
|---|---|---|---|
| none | 2.77 [2.31–3.23] (13) | 13 | 3.38 [2.77–4.08] (13) |
| v1.1 | 3.23 [2.54–3.85] (13) | 13 | 4.23 [3.69–4.69] (13) |
| v2.0 | 3.69 [3.15–4.23] (13) | 13 | 4.23 [3.62–4.77] (13) |
| v2.1 | 4.38 [4.15–4.62] (13) | 13 | 4.62 [4.23–4.92] (13) |
| v2.4 | 4.77 [4.38–5.00] (13) | 13 | — |

Per brief (this frame):

| brief | none | v1.1 | v2.0 | v2.1 | v2.4 |
|---|---|---|---|---|---|
| compare | 2 | 4 | 4 | 4 | 5 |
| fleet | 2, 2 | 1, 2 | 2, 2 | 5, 5 | 5, 4 |
| hardware | 3, 3 | 4, 4 | 4, 4 | 4, 4 | 5, 3 |
| library | 3, 3 | 5, 4 | 4, 4 | 4, 5 | 5, 5 |
| pharmacy | 4, 2 | 4, 2 | 4, 4 | 4, 4 | 5, 5 |
| rail | 2, 2 | 2, 2 | 5, 2 | 5, 5 | 5, 5 |
| rebate | 4, 4 | 4, 4 | 5, 4 | 4, 4 | 5, 5 |

- **v2.4 − v2.1**, paired by brief and seed: +0.38 [-0.08, +0.77] over 13 pairs — a rise over the bar. Pairs: +0, +1, +1, +1, +0, +1, +1, +0, +1, +1, +0, -1, -1.
- **v2.4 − v2.0**, paired by brief and seed: +1.08 [+0.54, +1.62] over 13 pairs — a rise over the bar. Pairs: +0, +0, +1, +1, +3, +1, +1, +3, +1, +1, +1, +2, -1.

## D4 — canonical shapes per arm and category (combined topology)

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
| v2.4 | console | 6 | 1 | 5 | 0 | 1 | 1 | 0 | 6 |
| v2.4 | narrative | 6 | 0 | 5 | 1 | 0 | 2 | 0 | 1 |
| v2.4 | pair | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 1 |

## D1 — layout distance per arm (reported, not gating)

Raw / effective (both builds pass the mechanical gate). Across briefs within category, then within brief across seeds.

### across briefs within category

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff |
|---|---|---|---|---|---|
| none | console | 15 | 0.250 / 0.016 | 0.692 / 0.039 | 0.734 / 0.054 |
| none | narrative | 15 | 0.224 / 0.088 | 0.420 / 0.147 | 0.633 / 0.257 |
| v1.1 | console | 15 | 0.257 / 0.257 | 0.475 / 0.475 | 0.730 / 0.730 |
| v1.1 | narrative | 15 | 0.256 / 0.256 | 0.591 / 0.591 | 0.722 / 0.722 |
| v2.0 | console | 15 | 0.290 / 0.290 | 0.618 / 0.618 | 0.790 / 0.790 |
| v2.0 | narrative | 15 | 0.270 / 0.270 | 0.574 / 0.574 | 0.710 / 0.710 |
| v2.1 | console | 15 | 0.208 / 0.115 | 0.617 / 0.439 | 0.573 / 0.361 |
| v2.1 | narrative | 15 | 0.271 / 0.181 | 0.478 / 0.337 | 0.590 / 0.390 |
| v2.4 | console | 15 | 0.179 / 0.179 | 0.632 / 0.632 | 0.762 / 0.762 |
| v2.4 | narrative | 15 | 0.262 / 0.262 | 0.497 / 0.497 | 0.689 / 0.689 |

### within brief across seeds

| arm | category | pairs | partition raw / eff | pqgram raw / eff | raster raw / eff |
|---|---|---|---|---|---|
| none | console | 3 | 0.250 / 0.078 | 0.725 / 0.193 | 0.802 / 0.272 |
| none | narrative | 3 | 0.199 / 0.049 | 0.394 / 0.128 | 0.544 / 0.143 |
| v1.1 | console | 3 | 0.257 / 0.257 | 0.442 / 0.442 | 0.623 / 0.623 |
| v1.1 | narrative | 3 | 0.262 / 0.262 | 0.598 / 0.598 | 0.602 / 0.602 |
| v2.0 | console | 3 | 0.215 / 0.215 | 0.625 / 0.625 | 0.699 / 0.699 |
| v2.0 | narrative | 3 | 0.271 / 0.271 | 0.468 / 0.468 | 0.701 / 0.701 |
| v2.1 | console | 3 | 0.193 / 0.119 | 0.684 / 0.469 | 0.440 / 0.276 |
| v2.1 | narrative | 3 | 0.264 / 0.150 | 0.393 / 0.283 | 0.596 / 0.385 |
| v2.4 | console | 3 | 0.165 / 0.165 | 0.575 / 0.575 | 0.534 / 0.534 |
| v2.4 | narrative | 3 | 0.281 / 0.281 | 0.367 / 0.367 | 0.656 / 0.656 |

## D2 — accent hue dispersion per arm

Max-chroma accent as measured, and by declared job (2.x arms, from the record; `none` and status-only excluded) where a record exists.

| arm | builds | measured hues | dispersion | directional (by job) | hues | dispersion | status-only / none | dark grounds |
|---|---|---|---|---|---|---|---|---|
| none | 13 | 295, 39, 30, 38, 23, 30, 32, 21, 74, 221, 73, 27, 32 | 0.282 | 0 | — | — | 0 | 4 |
| v1.1 | 13 | 48, 46, 23, 285, 27, 265, 318, 43, 38, 25, 55, 295, 31 | 0.341 | 0 | — | — | 0 | 4 |
| v2.0 | 13 | 249, 282, 22, 28, 68, 63, 256, 28, 27, 62, 28, 30, 26 | 0.405 | 6 | 249, 282, 28, 256, 28, 26 | 0.546 | 7 | 2 |
| v2.1 | 13 | 27, 26, 220, 24, 252, 58, 27, 58, 27, 32, 26, 248 | 0.475 | 7 | 220, 252, 58, 58, 32, 26, 248 | 0.805 | 6 | 1 |
| v2.4 | 13 | 27, 96, 27, 205, 28, 93, 70, 27, 90, 27, 28, 95 | 0.287 | 6 | 96, 205, 93, 70, 90, 95 | 0.237 | 6 | 2 |

## D3 — families per arm

| arm | display families (distinct / builds) | body families | mono |
|---|---|---|---|
| none | 7/13: -apple-system, Inter, Iowan Old Style, Rockwell, Superclarendon, ui-rounded, ui-serif | 5/13: -apple-system, Inter, Iowan Old Style, system-ui, ui-sans-serif | 1/13: ui-monospace |
| v1.1 | 8/13: Archivo, Azeret Mono, Barlow, Barlow Condensed, Figtree, Lexend, Source Serif 4, Zilla Slab | 8/13: Archivo, Atkinson Hyperlegible Next, Barlow, Figtree, Lexend, Public Sans, Source Sans 3, Source Serif 4 | 4/13: Azeret Mono, DM Mono, Geist Mono, Roboto Mono |
| v2.0 | 7/13: Archivo Narrow, Atkinson Hyperlegible Next, Barlow, Barlow Condensed, Commissioner, Literata, Zilla Slab | 4/13: Atkinson Hyperlegible Next, Barlow, Cabin, Commissioner | 6/13: Atkinson Hyperlegible Mono, Azeret Mono, Fragment Mono, Geist Mono, JetBrains Mono, Roboto Mono |
| v2.1 | 9/13: Archivo Narrow, Arvo, Atkinson Hyperlegible Next, Barlow, Barlow Condensed, Commissioner, JetBrains Mono, Lexend, Zilla Slab | 6/13: Atkinson Hyperlegible Next, Barlow, Commissioner, JetBrains Mono, Lexend, Public Sans | 5/13: Azeret Mono, Fira Mono, Fragment Mono, JetBrains Mono, Roboto Mono |
| v2.4 | 11/13: Alegreya Sans, B612, Bitter, Cabin, Chivo, Fira Sans, Instrument Sans, League Gothic, Radio Canada, Rokkitt, Young Serif | 11/13: Andika, B612, Bitter, Chivo, Fira Sans, Golos Text, Instrument Sans, Libre Franklin, Radio Canada, Source Sans 3, Work Sans | 5/13: Courier Prime, DM Mono, Fira Code, Red Hat Mono, Ubuntu Sans Mono |

## S — the rubric in this run's frame (exploratory for d1)

4 rater(s): astra-high, astra-medium, claude-opus, claude-sonnet. Each rated a brief's baseline pages and new pages together; the baseline's earlier ratings are not pooled in. Panel mean per arm with a bootstrap interval over pages; then the new arms paired with `v2.1` and `v2.0` by brief and seed.

| score | none | v1.1 | v2.0 | v2.1 | v2.4 |
|---|---|---|---|---|---|
| d1 | 4.67 [4.23–5.13] (13) | 4.65 [4.23–5.02] (13) | 4.94 [4.52–5.37] (13) | 4.77 [4.40–5.12] (13) | 5.12 [4.54–5.63] (13) |
| brief fit | 1.81 [1.68–1.92] (13) | 1.86 [1.77–1.94] (13) | 1.90 [1.80–1.98] (13) | 1.86 [1.78–1.93] (13) | 1.79 [1.66–1.90] (13) |
| e1 | 6.12 [5.65–6.46] (13) | 4.63 [4.08–5.17] (13) | 4.94 [4.40–5.46] (13) | 4.00 [3.56–4.48] (13) | 3.40 [2.87–4.02] (13) |
| aesthetics | 22.67 [21.65–23.60] (13) | 21.15 [19.75–22.44] (13) | 21.69 [20.87–22.50] (13) | 20.63 [19.73–21.46] (13) | 21.42 [20.10–22.58] (13) |
| defects | 1.38 [0.98–1.71] (13) | 1.06 [0.62–1.52] (13) | 0.81 [0.48–1.15] (13) | 1.02 [0.65–1.40] (13) | 0.67 [0.33–1.08] (13) |

- v2.4 − v2.1 on d1: +0.35 [-0.19, +0.87] over 13 pairs.
- v2.4 − v2.1 on brief fit: -0.07 [-0.22, +0.05] over 13 pairs.
- v2.4 − v2.1 on e1: -0.60 [-1.23, -0.04] over 13 pairs — the interval excludes zero.
- v2.4 − v2.1 on aesthetics: +0.79 [-0.75, +2.33] over 13 pairs.
- v2.4 − v2.1 on defects: -0.35 [-0.60, -0.08] over 13 pairs — the interval excludes zero.
- v2.4 − v2.0 on d1: +0.17 [-0.62, +0.88] over 13 pairs.
- v2.4 − v2.0 on brief fit: -0.11 [-0.30, +0.06] over 13 pairs.
- v2.4 − v2.0 on e1: -1.54 [-2.44, -0.62] over 13 pairs — the interval excludes zero.
- v2.4 − v2.0 on aesthetics: -0.27 [-1.98, +1.23] over 13 pairs.
- v2.4 − v2.0 on defects: -0.13 [-0.44, +0.13] over 13 pairs.

α (Krippendorff, ordinal) across this run's raters over every page they rated:

| score | α | raters × pages |
|---|---|---|
| d1 | 0.56 | 4 × 65 |
| brief fit | 0.79 | 4 × 65 |
| e1 | 0.70 | 4 × 65 |
| aesthetics | 0.56 | 4 × 65 |
| defects | 0.63 | 4 × 65 |
