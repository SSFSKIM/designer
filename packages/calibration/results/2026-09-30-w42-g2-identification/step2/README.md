# W42 G2 step 2 — identification on the G1 archive (ledger §5.196, identification part)

Charter `docs/doperpowers/specs/2026-09-29-w42-body-spatial-structure.md`, G2 step 2 and clauses 6
and 15; the hashed declaration `f04ae95b…`; the native-T addendum `23e400bf…` and the black-join
addendum `8ad314c1…`; G1's archive `w42-archive` (asset `1e3d6e65…`, inventory `5481795e…`) and bar
(0.5 on every statistic). Nothing here renders vitrea, runs a gate or opens H.

## Order of work, and where each result is

| step | script | output |
| --- | --- | --- |
| pins, before the first read (`afae1c36`) | `pins.py` | `pins.json`, `reading-plan.md` |
| native T per endpoint, stratum and channel | `native_t_read.py` | `native-t/` |
| every declared family, per endpoint, calibration fit and validation transfer | `fit_family.py`, `batch.py` | `fits/main/<family>__<endpoint>__<mask>.json` |
| family E: the knee form and candidate 2's chroma scale | `knee_chroma.py` | `knee/LT__<endpoint>.json` |
| the refraction order (v3 on Apple) | `refraction_v3.py` | `refraction/<endpoint>.json` |
| the k ladder (`k@global`, `k@scheme`) | `nesting.py` | `fits/main/LT@<level>__all__n.json` |
| verdicts: survival, knee, unit, k level, Decision Log 5f, resolution | `analyze.py` | `verdicts.json`, `verdicts.txt` |
| candidate-document values | `candidates.py` | `candidates.json` |

Every script verifies the pins at import (`common.py`) and denies `~/vitrea-w42/g1` by the archive
module's audit hook. The observed images (plurality frames) and each fit's full per-statistic table
live outside the repository under `~/vitrea-w42/g2-ident-scratch/`, each named in the committed
JSON by path and SHA-256; `observed/index.json` there names every frame by the archive's own hash.

Reproduce (Python 3.12, numpy 2.3.5, scipy 1.18.0; one BLAS thread per process):

```bash
cd packages/calibration/results/2026-09-30-w42-g2-identification/step2
python3.12 -B -c 'import common; common.extract_all()'      # the archive's plurality frames
python3.12 -B native_t_read.py
W42_POOL=5 python3.12 -B batch.py main
python3.12 -B knee_chroma.py LT main
python3.12 -B refraction_v3.py light-rest LT; python3.12 -B refraction_v3.py dark-rest LT
python3.12 -B nesting.py k@global main; python3.12 -B nesting.py k@scheme main
python3.12 -B analyze.py main; python3.12 -B candidates.py main
```

## The result (ledger §5.196, identification part; `verdicts.txt` in full)

- **No declared family survives one code in any endpoint.** LT's worst region-statistic miss is
  14.1 / 10.2 / 13.7 / 16.1 codes at least squares (light active, light receded, dark active, dark
  receded) and the best of every family is 9.0–12.1. Each endpoint is the wave's negative at its
  resolution (Decision Log 3, nothing claimed).
- **Native T** is monotone in light and decreases above input 208 at s ≥ 96 in both dark
  endpoints; the addendum's completion reads dark black 26 / 14 at s = 128 where the full strata
  read 32 / 20. Channels agree within one code (12 of 114 ordinates differ by one).
- **Knee** per-channel; **unit** points; **k** one global value at the least-squares points
  (2.138); **refraction** after the blur in light active (S2 admitted, Â −6.53 pt), undecided in
  dark active, where Decision Log 5f's two fits differ (dk +0.15, dλ −0.24).
- **Candidate 2's chroma scale** (per-channel, minimax / least squares): 0.630 / 0.777,
  0.770 / 1.003, 0.992 / 0.908, 0.815 / 1.008. Family E's luma closes within 2 codes; its chroma
  does not.
- **Candidate values for scratch renders** are in `candidates.txt` / `.json` (LT's fitted values;
  none is an identified law).
