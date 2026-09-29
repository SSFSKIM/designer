# W42 grounding — the memos and rulings the charter was drafted from

The W42 charter (`docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md`) was drafted
from the grounding memos in this directory and revised under the rulings beside them. They are
copied verbatim from the working directory they were written in
(`/Users/new/.claude/jobs/17c7ce02/tmp/`), which is the path the memos, briefs and rulings
themselves cite. Every number in the memos is a READING: each memo's fits are exploratory, size
an effect and are never a proposed coefficient set. No holdout or recorded native pixel was
opened for any of them. Memo C also read the canonical probe cells, which W42 therefore treats as
calibration evidence and never as a referee (charter X34). Memo D read Apple's declared layer
tree and no pixel at all. Memo E re-fitted that tree on memo C's cells and scratch, which it
imported read-only.

## The files

| file | what it is |
| --- | --- |
| `w42-grounding-common.md` | The rules memos A–C worked under: the admitted evidence, the reading discipline (prove a reader on vitrea's own captures first; read features at their own scale; keep censored channels one-sided), and what a memo is. |
| `w42-grounding-brief-argument.md` | Memo A's brief: the argument E3's F and g are evaluated at. |
| `w42-grounding-argument.txt` | Memo A. E3's argument is ENCODED and local, not linear and not group-level; the detail transfer is one-sided in every endpoint; chroma takes the heavy argument only; the six listed argument families and the exploratory one-sided reading C7 with their referee values. |
| `w42-grounding-brief-kernel.md` | Memo B's brief: Apple's body blur, its kernel, space and pose, and the capture that identifies it. |
| `w42-grounding-kernel.txt` | Memo B. Two spatial scales composited one-sidedly; the wide component averages encoded values; the receded pose widens the narrow component; vitrea's shipped body mapped from its code; a 121-cell capture design. |
| `w42-grounding-brief-probe.md` | Memo C's brief: the probe series, the W29 dump and the smallest capture that still identifies. |
| `w42-grounding-probe.txt` | Memo C. W is a local encoded blur (box footprint when receded); σn by span and pose; the active knee's algebra; the receded algebra not closed; the averaging space on non-binary structure; the W29 dump as a pointer; the 66 + 22-cell capture (§6) the charter's bed started from; the shipped defects D1 and D2 (§7). |
| `w42-dump-brief.md` | Memo D's brief: Apple's layer tree through the harness's `dump-layers` mode across spans, poses and schemes, no pixels. |
| `w42-dumps.txt` | Memo D. The declared body chain in every surface: a radius-5 narrow blur whose opacity is graded by span (both poses) and SDF depth (active); a radius-8 fill at Lighten or Darken 0.9 then Normal at the glass slider; the face colour matrix, affine on encoded values; one size variable t = clamp((s − 64)/96, 0, 1); 1x equal to 2x apart from four one-device-pixel terms; the face against native uniform levels. |
| `w42-v1-parent-rulings.md` | The parent's rulings on charter v1's ten drafter's notes, including the user's Decision Log 5a (M2 read directionally), quoted. |
| `w42-v1-review-rulings.md` | The parent's disposition of every finding of the adversarial review of charter v1, including the user's Decision Log 5b (the landed-T bar and the native-T candidate), quoted, and, since v2.1, an addendum with the review's own text for findings 9 and 15–17 and the parent's three calls on v2. The rest of the review's text is in the parent session's transcript. |
| `w42-grounding-refit.txt` | Memo E. The literal layer tree re-fitted on memo C's cells: the declared opacity scales the narrow blur's radius (the mixture reading rejected); the radii are in points, one scale k about 2 in all four endpoints; the capture acts as memo C's 0.8-dev floor before the knee (a box decimation rejected); LT does not close where memo C's per-cell fits closed; U1's λ drift persists and lives in the heavy blur's reference 16–48 pt out; R1 kept as a rival, R2 rejected; the face matrix misses on level. |
| `w42-v2-memoE-rulings.md` | The parent's rulings on memo E, folded into charter v2.1: radius scaling with one k as the primary narrow family, λ fitted and w fixed, U1 open, R1 declared and R2 rejected, candidate 2's T the native curve from family A, and memo E's bed rows. |
| `scratch-sha256.txt` | A SHA-256 manifest of the memos' scratch, which stays on the capture machine (below). |

SHA-256 of the committed copies, byte-identical to their sources at commit:

```
f54c56f19bcb36b810e7e4b9706856b0025b5fd024b9b3a2ad6c42b9f510a1fe  w42-grounding-argument.txt
149a3281ae52e4f6aac47684e016dfcb21e0eb1c93f510119bc5e2b29f717568  w42-grounding-kernel.txt
ed4b7ef473c591a08a60d0aab885dde51cba2ef6ecd0cf23b02e7c280ddcf076  w42-grounding-probe.txt
e65c63fdd9739e3873a7be7fc68196ff63e187a3d5f7a7402a9d5e8a54498108  w42-grounding-common.md
2c014de7cedafd4bd6b0c4ceb4516503c8ad7e8df55a4df9df93686bc98c025f  w42-grounding-brief-argument.md
272a1e29374520cae0554194c3564e1c0f09232e0da13895584f069bd6bffc91  w42-grounding-brief-kernel.md
5b59368fcb4779a1b4f691869dcd61503666dfad27311ef00bf8e676fb400f86  w42-grounding-brief-probe.md
9a3d89514f5b066440072ef47014a2c281201e4d9b012611f53ef2ed61b46b43  w42-dump-brief.md
ec73d013085dd4c21c65a726361ac823f719858a3162f5df7dd421a4823dd7dc  w42-dumps.txt
e6c6325532770515777a562c7a248d90faf50d6ba4682c29c77e77c1ae4ce09c  w42-v1-parent-rulings.md
3d7946c2477bb65dbcffeddc1528cfce918fa89d4cf200b884aa925f947c1d87  w42-v1-review-rulings.md
04b4032b9a6931f08670534967b70ebf1c9d19deb3c62e74e5f0f268634d0911  w42-grounding-refit.txt
d80c9737a826e2562d50d9097337dc7b79d7f4102e0146f2786dc7594aa3cbaa  w42-v2-memoE-rulings.md
```

`w42-v1-review-rulings.md` was re-copied at v2.1 after its addendum was written; its v2 copy's
SHA-256 was `92b53ba7…` and the file's earlier lines are unchanged.

## The scratch, hashed and not committed

Each memo kept its scripts and outputs under `~/vitrea-w42/grounding/<memo>/` on the capture
machine: `argument/` (memo A), `kernel/` (memo B), `probe/` (memo C), `dumps/` (memo D: the
per-run dump JSON, attestations, logs and drivers) and `refit/` (memo E: the model, its proofs and
the fits). The raw scratch stays there and is never committed. `scratch-sha256.txt` records every
regular file under those five directories, paths
relative to `~/vitrea-w42/grounding/`, sorted. Python bytecode caches (`__pycache__/`) are
excluded, because they are rebuilt by any run and record nothing.

| directory | files | bytes | hashed |
| --- | --- | --- | --- |
| `argument/` | 42 | 3,377,901 | 2026-09-29T15:09+09:00 (v1) |
| `kernel/` | 36 | 1,362,264 | 2026-09-29T15:09+09:00 (v1) |
| `probe/` | 111 | 1,024,066 | 2026-09-29T15:09+09:00 (v1) |
| `dumps/` | 270 | 8,729,547 | 2026-09-29T16:02+09:00 (v2), after its last write at 15:38 |
| `refit/` | 36 | 459,848 | 2026-09-29T17:02+09:00 (v2.1), after its last write at 16:47 |
| total | 495 | 14,953,626 | |

Each version only adds lines: the v1 lines for `argument/`, `kernel/` and `probe/` and the v2
lines for `dumps/` are unchanged in the v2.1 manifest, which adds `refit/`. Memo E imported memo
C's scratch without writing to it.

To check the scratch against the record on the machine that holds it:

```
cd ~/vitrea-w42/grounding && shasum -a 256 -c <repo>/packages/calibration/results/2026-09-29-w42-grounding/scratch-sha256.txt
```
