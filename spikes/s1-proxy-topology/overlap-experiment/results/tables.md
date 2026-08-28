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
