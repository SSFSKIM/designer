# Where does the cross-group backdrop leak actually stop mattering?

Follow-up spike to S1 (backdrop proxy topology), run for the vitrea post-v1 wave's
W6 Surprise: *"the cross-group overlap check is more conservative than S1's own
measurements support."* Findings only — no production code was changed, and
nothing here is product code.

- **Harness:** `pages/bench.js` (a stripped rebuild of S1's bench with the group
  gap as the independent variable), `harness/run.mjs`, `harness/diff.mjs`.
- **Run:** `npm install && node harness/run.mjs` (≈9 min, headless Chromium
  151.0.7922.34, deviceScaleFactor 1). `node harness/table.mjs` re-renders the
  tables below from `results/results.json`.
- **Raw output:** `results/results.json`, `results/run.log`, `results/tables.md`,
  heatmaps in `results/heat/`.

---

## 1. The question, and why the current answer is 6σ

`proxy-overlap-after-enforcement` (`packages/platform-web/src/backdrop-proxy.ts`)
fires when two groups' **padded proxy boxes** intersect. Each box is the group's
shape union inflated by `samplingPadding`, whose derived default is 3σ. Two boxes
therefore stop intersecting only once the groups are `2 × 3σ = 6σ` apart, and any
pair closer than that is warned about.

S1 measured the leak this guards against at exactly two separations, both on one
blur radius, and read the wider one as noise. That left the whole span between
"noise" and "the trigger" unmeasured. This experiment measures it.

## 2. Method

For each cell — a blur radius σ, a backdrop class, and a separation — the same
page is rendered three ways and the renderings are diffed against each other:

| rendering | what it is |
| --- | --- |
| `single` | one proxy covering both groups; by construction it cannot chain |
| `split-ab` | one proxy per group, A painted first |
| `split-ba` | the same two proxies, B painted first |

Three diffs, because a split-vs-single comparison is measuring two different
things at once and they need separating:

- **`split-ab` vs `single`** — S1's own comparison. The total cost of a two-group
  topology.
- **`split-ab` vs `split-ba`** — identical geometry, opposite paint order. Only
  sibling chaining can produce a difference here, so this is the leak alone.
- **`split-ba` vs `single`** — the mirror, to confirm the signature swaps groups.

The per-pixel statistic is S1's, unchanged: the maximum absolute per-channel
difference over R, G, B in 0–255 space. Added: p99, because a leak that lives in
a thin band is described badly by a mean spread over a whole region.

**Regions of interest.** S1's rule, generalised: the *inner band* is the
padding-wide strip of each group nearest the gap — exactly where a sibling's
already-filtered pixels land — starting one padding in from the gap-facing edge
and stopping 6px short of it. At σ = 20 / padding 60 this reproduces S1's
`NA_inner` / `NB_inner` rectangles exactly. The tables below report the **core**
variant of that band, vertically inset to the corner radius so that no pixel in
it was ever clipped away by the rounded corners — see §4 for why that
distinction turned out to matter more than expected. Two control regions (the
gap strip between the groups, and a strip left of group A) sit outside every clip
and must read zero; they read zero in all 81 cells.

**Byte-determinism.** Every one of the 243 renderings was captured twice and the
two passes compared by SHA-256. **All 81 cells are byte-identical across passes.**
Every zero below is therefore a real zero and not an averaged-away flicker.

**Grid.** σ ∈ {8, 20, 40} — S1's own three radii, spanning 5×, on the principle
that one radius cannot tell a rule from a coincidence. Backdrop classes:
`checker` (24px hard-edged conic, high spatial frequency), `image` (S1's
deterministic noise raster, photo-class), `gradient` (smooth, low frequency), and
`mixed` (S1's own scene, rebuilt element for element). Separations from 0.25σ to
8σ, spanning the current trigger at 6σ. Plus the demo's real geometry (§6).

## 3. Results

Chromium 151.0.7922.34. Every number is mean / p99 / max of the per-pixel maximum
absolute per-channel difference, 0–255.


#### `s8/checker` — σ = 8, padding 24

| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.25σ | 2px | yes | yes | 0.321 / 2 / 4 | 0.321 / 2 / 4 | 0 / 0 / 0 | 0.1 / 3 / 18 |
| 0.5σ | 4px | yes | yes | 0.194 / 2 / 3 | 0.194 / 2 / 3 | 0 / 0 / 0 | 0.073 / 2 / 17 |
| 0.75σ | 6px | yes | yes | 0.109 / 1 / 2 | 0.109 / 1 / 2 | 0 / 0 / 0 | 0.052 / 2 / 17 |
| 1σ | 8px | yes | yes | 0.05 / 1 / 2 | 0.05 / 1 / 2 | 0 / 0 / 0 | 0.036 / 1 / 17 |
| 1.5σ | 12px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.021 / 1 / 18 |
| 2σ | 16px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.016 / 0 / 17 |
| 2.5σ | 20px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 17 |
| 3σ | 24px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 17 |
| 4σ | 32px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 17 |
| 6σ | 48px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 17 |
| 8σ | 64px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 17 |

#### `s8/image` — σ = 8, padding 24

| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.25σ | 2px | yes | yes | 2.563 / 13 / 15 | 2.563 / 13 / 15 | 0 / 0 / 0 | 0.462 / 16 / 34 |
| 0.5σ | 4px | yes | yes | 1.501 / 9 / 10 | 1.501 / 9 / 10 | 0 / 0 / 0 | 0.326 / 11 / 28 |
| 0.75σ | 6px | yes | yes | 0.819 / 5 / 7 | 0.819 / 5 / 7 | 0 / 0 / 0 | 0.22 / 8 / 21 |
| 1σ | 8px | yes | yes | 0.426 / 3 / 4 | 0.426 / 3 / 4 | 0 / 0 / 0 | 0.14 / 5 / 15 |
| 1.5σ | 12px | yes | yes | 0.05 / 2 / 2 | 0.05 / 2 / 2 | 0 / 0 / 0 | 0.05 / 2 / 14 |
| 2σ | 16px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.019 / 1 / 16 |
| 2.5σ | 20px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.01 / 0 / 18 |
| 3σ | 24px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.01 / 0 / 15 |
| 4σ | 32px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.009 / 0 / 14 |
| 6σ | 48px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.01 / 0 / 17 |
| 8σ | 64px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.009 / 0 / 10 |

#### `s8/gradient` — σ = 8, padding 24

| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.25σ | 2px | yes | yes | 0.719 / 4 / 4 | 0.719 / 4 / 4 | 0 / 0 / 0 | 0.167 / 6 / 10 |
| 0.5σ | 4px | yes | yes | 0.391 / 3 / 3 | 0.391 / 3 / 3 | 0 / 0 / 0 | 0.113 / 4 / 7 |
| 0.75σ | 6px | yes | yes | 0.193 / 2 / 2 | 0.193 / 2 / 2 | 0 / 0 / 0 | 0.074 / 3 / 6 |
| 1σ | 8px | yes | yes | 0.085 / 1 / 2 | 0.085 / 1 / 2 | 0 / 0 / 0 | 0.047 / 2 / 6 |
| 1.5σ | 12px | yes | yes | 0.006 / 0 / 1 | 0.006 / 0 / 1 | 0 / 0 / 0 | 0.017 / 1 / 6 |
| 2σ | 16px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.008 / 0 / 6 |
| 2.5σ | 20px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.006 / 0 / 6 |
| 3σ | 24px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.006 / 0 / 6 |
| 4σ | 32px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.006 / 0 / 6 |
| 6σ | 48px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.007 / 0 / 7 |
| 8σ | 64px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.006 / 0 / 7 |

#### `s20/mixed` — σ = 20, padding 60

| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.4σ ¹ | 8px | yes | yes | 1.387 / 6 / 7 | 1.387 / 6 / 7 | 0 / 0 / 0 | 0.371 / 6 / 18 |
| 1σ | 20px | yes | yes | 0.533 / 4 / 4 | 0.533 / 4 / 4 | 0 / 0 / 0 | 0.161 / 3 / 18 |
| 1.5σ | 30px | yes | yes | 0.174 / 2 / 3 | 0.174 / 2 / 3 | 0 / 0 / 0 | 0.076 / 2 / 18 |
| 2σ ¹ | 40px | yes | yes | 0.034 / 2 / 3 | 0.034 / 2 / 3 | 0 / 0 / 0 | 0.029 / 1 / 18 |
| 2.5σ | 50px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 18 |
| 3σ | 60px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.014 / 0 / 18 |
| 4σ | 80px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.014 / 0 / 18 |
| 6σ | 120px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.013 / 0 / 18 |

#### `s20/checker` — σ = 20, padding 60

| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.4σ | 8px | yes | yes | 0.397 / 2 / 2 | 0.397 / 2 / 2 | 0 / 0 / 0 | 0.127 / 2 / 18 |
| 1σ | 20px | yes | yes | 0.251 / 2 / 2 | 0.251 / 2 / 2 | 0 / 0 / 0 | 0.084 / 2 / 17 |
| 1.5σ | 30px | yes | yes | 0.068 / 1 / 2 | 0.068 / 1 / 2 | 0 / 0 / 0 | 0.052 / 1 / 18 |
| 2σ | 40px | yes | yes | 0.008 / 0 / 1 | 0.008 / 0 / 1 | 0 / 0 / 0 | 0.025 / 1 / 17 |
| 2.5σ | 50px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 18 |
| 3σ | 60px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 18 |
| 4σ | 80px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 18 |
| 6σ | 120px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 17 |

#### `s40/mixed` — σ = 40, padding 120

| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.4σ | 16px | yes | yes | 0.63 / 3 / 4 | 0.63 / 3 / 4 | 0 / 0 / 0 | 0.358 / 3 / 18 |
| 1σ | 40px | yes | yes | 0.307 / 2 / 2 | 0.307 / 2 / 2 | 0 / 0 / 0 | 0.171 / 2 / 18 |
| 1.5σ | 60px | yes | yes | 0.119 / 2 / 2 | 0.119 / 2 / 2 | 0 / 0 / 0 | 0.074 / 2 / 18 |
| 2σ | 80px | yes | yes | 0.027 / 2 / 2 | 0.027 / 2 / 2 | 0 / 0 / 0 | 0.031 / 2 / 18 |
| 2.5σ | 100px | yes | yes | 0.002 / 0 / 2 | 0.002 / 0 / 2 | 0 / 0 / 0 | 0.015 / 0 / 18 |
| 3σ | 120px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.013 / 0 / 18 |
| 4σ | 160px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.013 / 0 / 18 |
| 6σ | 240px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.014 / 0 / 18 |

#### `s40/checker` — σ = 40, padding 120

| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.4σ | 16px | yes | yes | 0.191 / 1 / 1 | 0.191 / 1 / 1 | 0 / 0 / 0 | 0.172 / 2 / 17 |
| 1σ | 40px | yes | yes | 0.124 / 1 / 1 | 0.124 / 1 / 1 | 0 / 0 / 0 | 0.12 / 1 / 17 |
| 1.5σ | 60px | yes | yes | 0.078 / 1 / 1 | 0.078 / 1 / 1 | 0 / 0 / 0 | 0.082 / 1 / 18 |
| 2σ | 80px | yes | yes | 0.032 / 1 / 1 | 0.032 / 1 / 1 | 0 / 0 / 0 | 0.046 / 1 / 18 |
| 2.5σ | 100px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.018 / 0 / 18 |
| 3σ | 120px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 17 |
| 4σ | 160px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.014 / 0 / 17 |
| 6σ | 240px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 17 |

#### `s8/mixed` — σ = 8, padding 24

| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 0.4σ | 3px | yes | yes | 1.667 / 10 / 12 | 1.667 / 10 / 12 | 0 / 0 / 0 | 0.319 / 10 / 27 |
| 1σ | 8px | yes | yes | 0.314 / 3 / 4 | 0.314 / 3 / 4 | 0 / 0 / 0 | 0.117 / 4 / 17 |
| 1.5σ | 12px | yes | yes | 0.036 / 2 / 2 | 0.036 / 2 / 2 | 0 / 0 / 0 | 0.045 / 2 / 18 |
| 2σ | 16px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.019 / 0 / 18 |
| 2.5σ | 20px | yes | yes | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.013 / 0 / 18 |
| 3σ | 24px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.013 / 0 / 18 |
| 4σ | 32px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.014 / 0 / 17 |
| 6σ | 48px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.013 / 0 / 18 |

#### `demo-s14/checker` — σ = 14, padding 42

| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2σ | 28px | yes | yes | 0.026 / 1 / 2 | 0.026 / 1 / 2 | 0 / 0 / 0 | 0.03 / 1 / 18 |
| 3σ | 42px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 17 |
| 4σ ² | 56px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 18 |
| 6σ | 84px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.015 / 0 / 18 |

#### `demo-s14/image` — σ = 14, padding 42

| separation | gap | boxes overlap | box reaches neighbour’s paint | leak, later group (AB vs single) | leak, order only (AB vs BA) | earlier group (AB vs single) | whole surface (AB vs single) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2σ | 28px | yes | yes | 0.015 / 0 / 2 | 0.015 / 0 / 2 | 0 / 0 / 0 | 0.025 / 1 / 18 |
| 3σ | 42px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.011 / 0 / 19 |
| 4σ ² | 56px | yes | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.011 / 0 / 15 |
| 6σ | 84px | no | no | 0 / 0 / 0 | 0 / 0 / 0 | 0 / 0 / 0 | 0.011 / 0 / 13 |

81 cells, 81 byte-identical across two capture passes.

¹ S1's two published leak-table rows (`docs/doperpowers/spikes/2026-08-24-s1-proxy-topology-findings.md`, §Q2).
² The demo's actual geometry — see §6.

---

## 4. Reading the numbers

### 4.1 The leak is one-directional, exactly as S1 found

The *earlier group* column is `0 / 0 / 0` in every single cell of the grid, at
every radius, backdrop and separation. All of the difference lives in the
later-painted group. And the order-only column (`AB` vs `BA`) matches the
vs-single column digit for digit wherever the leak is non-zero, which is the
strongest possible confirmation that what those columns measure is chaining and
nothing else.

### 4.2 The leak reaches exactly zero at, or before, 3σ — at every radius

The separation at which every leak metric becomes byte-identical zero:

| backdrop | σ = 8 | σ = 20 | σ = 40 |
| --- | --- | --- | --- |
| `checker` | 1.5σ | 2.5σ | 2.5σ |
| `image` | 2σ | — | — |
| `gradient` | 2σ | — | — |
| `mixed` (S1's scene) | 2σ | 2.5σ | 3σ |

The boundary drifts *up* slightly with radius — a bigger blur means the
neighbour's filtered output differs more from the raw backdrop it replaces, so
the leaked signal starts larger and needs more distance to fall under one 8-bit
step. It never drifts past 3σ. **Above 3σ separation there is not a single
non-zero pixel anywhere in the grid: 3 radii × 4 backdrop classes × the whole
range from 3σ to 8σ, all byte-identical.**

### 4.3 3σ is not a fit — it is where the mechanism runs out of geometry

Chaining needs one proxy's *box* to contain another proxy's *painted* output. A
group paints only inside its own clip, and its box extends one padding beyond
that clip. So group B's box reaches group A's painted pixels only while

```
gap < samplingPadding   ( = 3σ at the derived default )
```

At or beyond that separation A's filtered output is not in B's backdrop image at
all, and no amount of blur can carry it in. The measured boundary (1.5σ–3σ) sits
*under* this geometric bound and converges on it from below, which is what a real
mechanism looks like: the Gaussian tail dies before the geometry does.

The consequence for the current check is blunt. It fires whenever the boxes
intersect, i.e. up to `2 × padding = 6σ`. Between 3σ and 6σ the boxes do
intersect — but only over a region where *neither group paints anything*. The
warning's own stated mechanism ("the backdrop filter applies twice over the
overlap") is not occurring there. The `box reaches neighbour's paint` column in
the tables above is exactly this: it flips to `no` at 3σ, and every cell where it
reads `no` is byte-identical.

### 4.4 Magnitudes, where the leak is real

Worst case in the grid is `s8/image` at a 2px gap (0.25σ): mean 2.563, p99 13,
max 15, with 33% of the band's pixels over 2/255. At 1σ the same cell is mean
0.426, p99 3, max 4. At 1.5σ nothing anywhere in the grid exceeds max 3. So on a
perceptual reading the leak stops being arguably visible somewhere around
**1.5σ**, and stops existing at all at **3σ**.

### 4.5 The surprise: S1's noise floor is mostly not noise, and not a leak either

The `whole surface` column never reaches zero. It sits at mean 0.006–0.015 with
max 6–19 — and it reads *the same* at an 8σ separation, where the padded boxes do
not even touch and interaction is impossible, as it does at 0.25σ.

Locating those pixels (heatmap `results/heat/s8_checker_6sigma__*`, and a direct
pixel dump) resolves it: at 6σ, 341 pixels of the ~48,000 covered by the two
glass shapes differ at all; 335 of them by exactly 1/255; the remaining six by
10–17/255, and all six sit on the rounded-corner **arc of the clip path**. It is
an antialiasing difference between rasterising one clip path on one proxy box and
two clip paths on two smaller boxes — a constant cost of splitting, independent
of separation, and not a leak.

This matters for how S1's table should be read. S1's 40px-gap row (a 2σ
separation at σ = 20) reported mean 0.03–0.05 and was read as "Gaussian-tail
noise". Reproduced here it is mean 0.034 in that same band — but the corner-free
core band puts the *actual* order-dependent leak at that separation at mean
0.034 / p99 2 / max 3, and the rest of S1's band reading is corner antialiasing.
S1's floor was real, and its conclusion ("noise") was right; the number was
measuring two different things stacked, and the ROI's own clip corners were a
large part of it. Any future comparison of split against single topology should
exclude the clip boundary or it will report a floor it cannot go below.

### 4.6 S1 reproduces

S1's published rows, re-measured here in S1's own band definition on S1's own
scene at σ = 20, padding 60:

| row | S1 published (A_inner, B_inner) | this run |
| --- | --- | --- |
| 8px gap, order A→B | 0.01 / 18, **1.01 / 17** | 0.008 / 18, **1.009 / 17** |
| 40px gap, order A→B | 0.03 / 18, 0.05 / 18 | 0.008 / 18, 0.034 / 17 |

The stress row reproduces to three decimal places on a different Chromium build.
The 40px row's small disagreement is entirely inside the corner-antialiasing
floor described above. The methodology transfers.

## 5. What this implies for the trigger distance

**Narrow the trigger from "the padded boxes intersect" (6σ) to "one group's
padded box reaches the other group's painted region" (3σ).** In code that is a
one-predicate change in `backdrop-proxy.ts`: alongside each group's padded `box`,
record its unpadded shape-union rect, and warn on

```
rectsOverlap(a.box, b.clipUnion) || rectsOverlap(b.box, a.clipUnion)
```

instead of `rectsOverlap(a.box, b.box)`.

Why this specific predicate rather than a measured threshold:

- **It is the mechanism, not a calibration.** It states exactly the condition
  under which one proxy's filtered output is inside another proxy's backdrop
  image. It needs no perceptual constant, and it re-derives itself if the padding
  policy ever changes.
- **It cannot under-warn on anything measured.** Every non-zero pixel in all 81
  cells occurs strictly inside it. It remains conservative — it still fires from
  3σ down, where at 1.5σ–3σ the leak is real but at most 3/255.
- **It halves the false-positive range.** The entire 3σ–6σ band, which is half of
  the current trigger's reach and where every measurement is byte-identical,
  stops producing findings.

Two smaller corrections that come with it:

1. **The message quotes the wrong number.** It says "measured drifting up to
   17/255". That figure is S1's 8px-gap stress case — a 0.4σ separation. The
   warning currently fires out to 6σ, where the drift is zero, and even at the
   narrowed 3σ trigger the drift at the boundary is zero and at 1.5σ is 3/255.
   The message should quote the magnitude at the separation being warned about,
   or drop the number.
2. **An order-aware refinement is available but not recommended.** Only the
   later-painted group is ever contaminated, and the module already computes a
   deterministic paint order, so the check could fire only when the *later*
   group's box reaches the *earlier* group's clip. That is another halving, and
   it is correct for the current frame — but it makes the finding disappear and
   reappear as ordering changes, which is worse diagnostics than a symmetric
   statement about the layout. Keep it symmetric.

### The defense of the current conservatism, and why it does not hold

The strongest argument for leaving 6σ alone is the one in the wave spec: two
groups closer than their enlarged sampling regions is a fact about the page's
layout, and the check is a statement about that fact rather than about a measured
pixel delta. That argument is sound for the 0–3σ range and it is why the narrowed
check should still fire well above the perceptual boundary. It does not extend to
3σ–6σ, because there the stated fact is not true: the sampling *regions* touch,
but neither region contains anything the other one drew, and the message's
account of what goes wrong describes something that provably does not happen.
A diagnostic that names a mechanism should fire where the mechanism operates.

## 6. The demo's own warning is a false positive

`apps/demo`'s `toolbar` and `toolbar-menu` groups sit 56 CSS px apart
(`apps/demo/src/styles.css`, `.toolbar__menu { margin-left: 3.5rem }`). The
warning fires only under `reducedTransparency`, which multiplies frost by 1.75:
σ = 14, padding 42 per side, 84px of clearance wanted, 56px authored — a 4σ
separation, and the one surviving finding the wave spec records.

Measured at that exact σ and padding, on both a checkerboard and a photo-class
backdrop (`demo-s14/*` above): **0 / 0 / 0 in every region, byte-identical**, at
56px and also at 42px. The two proxies do not interact. The heatmap
`results/heat/demo-s14_checker_56px__single-vs-split-ab.png` shows only the
constant corner-antialiasing pixels of §4.5.

Under the narrowed predicate this finding disappears, correctly — and the demo's
own CSS comment ("wide enough that the toolbar group's proxy and the morph
group's do not meet") turns out to have been right about the thing that matters.

## 7. Caveats

- **Chromium only** (151.0.7922.34), `deviceScaleFactor` 1. S1 established that
  Playwright's Firefox and WebKit builds render `backdrop-filter` as a no-op in
  every capture path, so this cannot be cross-engine on this harness. The
  geometric bound in §4.3 is engine-independent; the measured 1.5σ–3σ boundary is
  not.
- **Horizontal separation, two equal-sized groups, no scroll, no transform, one
  plane.** The mechanism is symmetric and S1 already tested those axes for the
  padding rule, but this grid does not re-test them.
- **8-bit capture.** "Byte-identical" means the difference is below one step of
  8-bit sRGB after Chromium's own rounding, not that it is mathematically zero.
- The corner-antialiasing floor of §4.5 is a real, if tiny, argument that
  splitting a group is never entirely free. It is separation-independent, so it
  is not this check's business — but it is worth knowing that "put them in one
  group" is not a byte-neutral remediation either.
