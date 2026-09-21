# W31 G1 — the exterior-width instrument

**Gate: W31 G1, acceptance clause 4; contracts X1, X7, X11. Claims §5.162.** Executes W30's
Deferred-at-close items 1 and 9 and its Decision Log 5 (d).

**No material constant, profile document, native fixture, golden, bound, floor or row of
`results/matrix.json` moves at this gate, and no capture of any kind was taken.** Every number here
is a cut of evidence already committed: the working file's current generation, two superseded
generations under `results/superseded/`, W29 G3b's native-pair noise bar and the two shipped macOS 27
documents read for their σ leaves. `freeze.py verify` reads **1,818 entries intact** at this gate's
open and at its close. No schema addition was needed — every field both statistics read
(`falloffSigma{Native,Web}`, `affine{Native,Web}`, `backdropSupport`) is already on a schema-5 row,
so `src/report.ts` and `cli/measure.ts` are untouched (X11).

## The files

| file | what it is |
| --- | --- |
| `exterior-instrument.py` | the reader. Two candidate statistics over the current generation, holdout dropped in `cells()` by construction, `--with-holdout` the typed exception, `--against LABEL=path[,path]` for a superseded generation read by name, `--at-documents shipped\|any` for which documents a row may name |
| `exterior-instrument.txt` / `.json` | its default run: the holdout dropped, 602 macOS 27 rows at the shipped documents |
| `exterior-instrument-with-holdout.txt` / `.json` | the reported check: the same run with the seven `MISSED_27_ROWS` readings, the two span-160 sheet cells, and the lever against two superseded generations |
| `bounds-declaration.md` | the clause the next shadow wave adopts a row on — statistic, bed, exclusions, bound and the row shape in `adopted-thresholds.test.ts`'s idiom — plus candidate (i) beside B1 and what their divergence means |
| `freeze-verify-open.txt` / `-close.txt` | `freeze.py verify` at this gate's open and close |
| `chain.txt` | the build, lint and unit chain at this gate's head — 2,570 passed, 0 failed, four more than W30 G4's close |

## The test this gate adds

- `test/w31-exterior-instrument.test.ts` — runs the reader on a scratch matrix in a temporary
  directory with a known answer: `T` = 0.03267 for band differences of 0.01/0.02/0.03/0.04 under the
  weights 3/6/12/24, asserting also that an unweighted mean of the same four (0.02500) is *not* what
  the reader prints; candidate (i) = 0.500 for σ 10 against 15; a holdout row yields no number
  without the flag and the drop notice names what it refused; the flag admits it; and the default
  `shipped` mode refuses a fabricated document hash. No capture, no browser, nothing written outside
  the temporary directory.

## Reproducing

```bash
cd packages/calibration/results/2026-09-21-w31-g1-exterior-instrument
python3 exterior-instrument.py > exterior-instrument.txt
python3 exterior-instrument.py --with-holdout \
  --against "0.19.0 (c9a §5.154)=results/superseded/f42ddec1cf5a.json,results/superseded/272d1b0c3e10.json" \
  --against "W30 G3 (c9a §5.159)=results/superseded/d731b3838994.json,results/superseded/ce1af58886ff.json" \
  > exterior-instrument-with-holdout.txt
```

The two `--against` labels are the generations `results/superseded/index.json` maps those hashes to:
the first is 0.19.0's read at a span-invariant σ of 11.0 CSS px, which makes the comparison the σ
law's own lever; the second is W30 G3's read at the sealed material before G3b's `tanh` fix, which
isolates that fix and shows it moved neither statistic on any row.

## The one-line verdict

Candidate (ii) — the departure profile's SHAPE, read off the affine bands — is the clause; candidate
(i), the fitted σ's relative error, reads the bed the opposite way from the eye and is kept as the
diagnostic that points at `spreadPx` and `offsetPx`, two leaves the macOS 27 material inherited and
no wave has fitted. Nothing is adopted here: both are one-wave readings.
