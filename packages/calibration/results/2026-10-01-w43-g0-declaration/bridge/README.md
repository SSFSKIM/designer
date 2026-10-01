# W43 G0 (b): the bridge on existing evidence

Charter `docs/doperpowers/specs/2026-10-01-w43-glass-0-25-generation.md` v1.2, clause 3, Design
"The bridges", X43. Every W43 pixel comes through the W39 side bundle; the canonical 0.5 bed came
through the original bundle on 2026-09-18/19. This reads W42's family F (four cells captured through
the side bundle at slider 0.5 on 2026-09-30, seven runs, never read before) against the canonical
0.5 fixtures, before the declaration is hashed.

**Verdict: the bridge holds.** Every one of the 20 twinned cell-passes agrees; 4 have no canonical
twin.

| verdict | cell-passes | what it means |
| --- | ---: | --- |
| AGREE (bytes) | 19 | the fixture file is byte-identical to the side bundle's frame (18 unanimous over seven runs; 2x light active checker-64 rrect-lg is the 5-of-7 plurality, its 2-run minority a different state) |
| AGREE (regions) | 1 | 2x dark active checker-64 rrect-lg: 84 px differ, every one by 1 code, all on the silhouette's edge rows; every one of its 66 region statistics is equal |
| NO TWIN | 4 | the dark impulse on rrect-md, at both scales and in both poses: the canonical dark profiles carry no impulse scene |

**Run by run** (the parent's later ruling for the sittings' bridges): every state the seven runs
produced was also judged against its fixture (`runByRun` in `bridge.json`). Every run of all 20
twinned cell-passes agrees: by bytes, or (the 2x dark active checker-64 and the two-run minority
state of the 2x light active one) by every region statistic.

**The one non-identical cell is not a bundle difference.** The original bundle's own seven W29 runs
of that cell read two states, `969118c4591d` 4 times (published as the fixture) and `24b99f3931c2`
3 times; the side bundle read `24b99f3931c2` in all seven of its runs. Across all 20 twinned
cell-passes, every state the side bundle produced is one the original bundle produced at W29, and
every fixture is one of W29's states (`w29Original` in `bridge.json`; the raw W29 tree
`~/vitrea-w29-27-run/` is on the capture machine and not committed).

**What the bridge covers (X43).** Cell types with a bridge: the two-level checker at pitch 16 on
rrect-md (2x), at pitch 64 on rrect-lg (1x and 2x), the impulse on rrect-md (light, 1x and 2x) and
photo on rrect-md (2x), in all four window states where the canonical bed has them. The canonical
0.5 bed has no dark impulse, so no 0.25-against-0.5 claim needs one; the sittings' own opening
bridges (Design) add canonical cells at both scales.

## How it was read

```bash
python3.12 -B bridge.py ~/vitrea-w42/archive-copy/1e3d6e65fa3b9a621f1d0f80fb03cc79ee76c29d9b001174983689a7aed31014/extracted/archive \
  --out . --deny ~/vitrea-w42/g1 --deny ~/vitrea-w42/archive --deny ~/vitrea-w42/release \
  --w29-runs ~/vitrea-w29-27-run
```

- The archive is the second owner-controlled copy of `w42-archive` (asset SHA-256 `1e3d6e65…`,
  re-hashed equal; inventory `5481795e…`, its tree verified entry by entry). It is opened through
  W42's guarded Reader with the `probe` role only. H was never requested, and the raw run root,
  the producer's output and the release directory were denied for the process.
- The metric is the charter's: byte identity, or region medians within max(1 code, bar). The
  region statistics are W42's instrument unchanged (`forward.Cell` at the bed's geometry; an active
  cell at masks `n` and `w`, a receded cell at its one mask; `regions.statistics`). The bar is
  recomputed from the seven runs and checked equal to G1's published `bar.json.gz` (`a85662f2…`):
  0.5 on every statistic, so the tolerance is one code.
- Every twin is a calibration, validation or probe scene of the canonical split, checked against
  `scenes.json` before its fixture is opened.

Files: `bridge.py` (the reader), `bridge.json` (every row, statistic and bar), `bridge.txt` (the
table above, per cell).
