# W42 grounding — the memos the charter was drafted from

The W42 charter (`docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md`) was drafted
from the grounding memos in this directory. They are copied verbatim from the working directory
they were written in (`/Users/new/.claude/jobs/17c7ce02/tmp/`), which is the path the memos and
briefs themselves cite. Every number in them is a READING: each memo's fits are exploratory,
size an effect and are never a proposed coefficient set. No holdout or recorded native pixel was
opened for any of them. Memo C also read the canonical probe cells, which W42 therefore treats as
calibration evidence and never as a referee (charter X34).

## The files

| file | what it is |
| --- | --- |
| `w42-grounding-common.md` | The rules all three memos worked under: the admitted evidence, the reading discipline (prove a reader on vitrea's own captures first; read features at their own scale; keep censored channels one-sided), and what a memo is. |
| `w42-grounding-brief-argument.md` | Memo A's brief: the argument E3's F and g are evaluated at. |
| `w42-grounding-argument.txt` | Memo A. E3's argument is ENCODED and local, not linear and not group-level; the detail transfer is one-sided in every endpoint; chroma takes the heavy argument only; the six listed argument families and the exploratory one-sided reading C7 with their referee values. |
| `w42-grounding-brief-kernel.md` | Memo B's brief: Apple's body blur, its kernel, space and pose, and the capture that identifies it. |
| `w42-grounding-kernel.txt` | Memo B. Two spatial scales composited one-sidedly; the wide component averages encoded values; the receded pose widens the narrow component; vitrea's shipped body mapped from its code; a 121-cell capture design. |
| `w42-grounding-brief-probe.md` | Memo C's brief: the probe series, the W29 dump and the smallest capture that still identifies. |
| `w42-grounding-probe.txt` | Memo C. W is a local encoded blur (box footprint when receded); σn by span and pose; the active knee's algebra; the receded algebra not closed; the averaging space on non-binary structure; the W29 dump as a pointer; the 66 + 22-cell capture (§6) that the charter's G1 is built on; the shipped defects D1 and D2 (§7). |
| `w42-dump-brief.md` | Memo D's brief: Apple's layer tree through the harness's `dump-layers` mode across spans, poses and schemes, no pixels. Memo D itself (`w42-dumps.txt`) was still running when this directory was committed; it is added here at the charter's v2. |
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
```

## The scratch, hashed and not committed

Each memo kept its scripts and outputs under `~/vitrea-w42/grounding/<memo>/` on the capture
machine: `argument/` (memo A), `kernel/` (memo B), `probe/` (memo C). The raw scratch stays
there and is never committed. `scratch-sha256.txt` records every regular file under those three
directories, paths relative to `~/vitrea-w42/grounding/`, sorted: **189 files, 5,764,231 bytes**,
hashed at 2026-09-29T15:09+09:00 after the last memo was written. Python bytecode caches
(`__pycache__/`) are excluded, because they are rebuilt by any run and record nothing. The
`dumps/` directory is memo D's and was still being written; its manifest is added at v2.

To check the scratch against the record on the machine that holds it:

```
cd ~/vitrea-w42/grounding && shasum -a 256 -c <repo>/packages/calibration/results/2026-09-29-w42-grounding/scratch-sha256.txt
```
