# W32 G1 — the joint fit, the recede's stand-down, the seal and the read

Claims **§5.168**. Charter `docs/doperpowers/specs/2026-09-21-w32-shadow-wave.md`, acceptance
clauses 3, 4 and 5, under **Decision Log 1 (a), (b), (c) and Decision Log 2 as ruled**. Bounds and
band rule are G0's (`results/2026-09-21-w32-g0-exterior-cut/bounds-declaration.md`) and this gate
declares none of its own.

This gate **captures**. Every browser run is recorded in `browser-runs.txt` with the machine read
that preceded it (`x6-read.sh`: Reduce Transparency 0, Increase Contrast 0, `NSGlassTintAmount`
0.5), the foreign-browser count, and a closing read. No native capture was taken, the granted
bundle was never rebuilt, and nothing under a macOS 26.5-keyed path was opened for writing (X1, X5).

## What to read, and in what order

| file | what it is |
| --- | --- |
| `verdict.txt` | **the verdict** — every stop before and after, C1 in its ruled form and beside it, candidate (i), the per-backdrop residual, the missed rows |
| `pre-fit/` | the bed at the SHIPPED documents: the cut, the stops, the reproduction check against the committed rows, the ten never-read scenes read for the first time |
| `rounds/<label>/` | one round each: `constants.json` (the candidate), `documents.txt`, `exterior-cut.{txt,json}`, `c1-forms.txt`, `stops.txt`, `departure-stat.txt`, `anchor-solve.txt` |
| `rounds/README.md` | the trajectory: what moved each round, why, and what every stop read |
| `sealed-documents.txt` | the four documents' digests and file hashes, before and after |
| `configuration.txt` | `configuration.py record`, the cross-gate holdout artifact, run before the holdout |
| `canonical-read-*.txt` | the read at the sealed bytes: calibration + validation, the widened ladder, the holdout once |
| `append-check.txt`, `read-append-check.txt` | every macOS 26.5 row byte-identical, order unchanged, counts add up |
| `split-plan.txt`, `split-apply.txt` | the generation split, after the read |
| `sheets/`, `eye.md` | native \| WebGPU \| CSS \| ×8, looked at |
| `reach.txt` | the reach per span per pose, before and after — the tracker's padding entry |
| `ladder-fixtures.txt` | the widened ladder's fixtures, per profile directory (a declared scene with no fixture is a red) |

## The scripts, and what each is a copy of

| script | provenance and what changed |
| --- | --- |
| `x6-read.sh` | W31 G3's, byte for byte |
| `exterior-cut.py` | W32 G0's, byte for byte — the statistic, the admitted-band rule and the window departure are G0's and are not restated (X2) |
| `c1-forms.py`, `stops.py` | W32 G0's, with **one change each**: the three paths they read from disk are overridable by environment variable, so a cut per round does not need a copy of the reader per round. Unset, every path is G0's. |
| `departure-stat.py`, `shadow-law.py`, `model-fit.py`, `clearance.py` | W32 G0's, byte for byte |
| `reach.ts` | W32 G0's, byte for byte but for its title — it already reports the receded reach, which is what Decision Log 2 makes a reading |
| `build-shadow.py` | W30 G3's, changed in **three** places its docstring names: the two lengths are writable; the receded documents' amplitude stands down to 0 (Decision Log 2) rather than being inherited leaf for leaf; `--in-place` refuses a σ law outside B1 |
| `anchor-solve.py` | W30 G3's, with its **objective changed** to the window-restricted departure and two additions: the fit objective and the linearity check as a number. Its docstring states exactly how the window departure is computed per regime. |
| `constants.py` | new — a round's candidate built from the shipped documents plus overrides, with the knee re-derived whenever the slope moves |
| `render-bed.sh`, `round.sh`, `ladder.sh` | W31 G3's `round.sh` / `scratch-capture.sh` fused and widened; `ladder.sh` is the one place the read set is named |
| `repro.py` | new — the pre-fit bed against the committed rows, cell by cell |
| `check-ladder-fixtures.py` | new — the widened ladder's fixtures per profile directory |
| `digest-sites.md`, `append-check.py` | W31 G3's, **byte for byte** — verified with `cmp` at the review closure |
| `seal.ts` | W31 **G3c**'s corrected template, plus **one addition**: it writes the `$comment-sha-history-correction` into the two DARK documents, which G3c could not do because X10 forbade it their bytes (W31 Deferred item 14, closed here). Its docstring names the change and keeps G3c's header below it |
| `read-append-check.py` | W31 G3's, with **one change** its own docstring states: `snapshot` may be taken of a NAMED matrix rather than of the live one, because this gate's read had already run when the omission was noticed and the "before" it needs is the seal commit's blob. With no argument it is W31 G3's function exactly |
| `canonical-read.sh` | W31 G3's, with this gate's four sealed hashes and the widened `LADDER` sourced from `ladder.sh` |
| `sheets.ts` | W31 G4's, with **its BED changed and nothing else** — the per-cell document-bytes assertion, the panel layout, the ΔE × 8 panel and the refusal are G4's and are the reason it was the file copied. The bed is the exterior's: three spans in both poses on all four standard profiles, plus the holdout far-halo cell |

*(This table's first three rows read "W31 G3's, byte for byte" for `seal.ts`,
`read-append-check.py` and `sheets.ts` until the review closure, 2026-09-21;
claims §5.168 §10, findings N-9 and the same class. Two of the three carry this
gate's own changes and the third is G3c's file rather than G3's. Nothing the
scripts DID changes; what was wrong was the provenance beside them, which is the
"unchanged, checked" class `CLAUDE.md` names.)*

## Three files that will read oddly if taken at face value

- **`digest-sites.md` is W31 G3's file byte for byte, two seals behind.** It is a
  CHECKLIST of the places a moved digest has to reach, not a record of any
  digest: the hashes inside it are W31 G3's and were already stale at G3c. **This
  gate's four digests are the four in `verdict.txt` and in claims §5.168 §5**, and
  the list of sites they were carried to is that section's "Every digest site,
  moved" paragraph. The file is not edited, because nothing under `results/` is
  edited after commit (review closure, finding N-10).
- **`c1-forms.txt` prints 8 of 12 rows FAIL in its §2, and C1 PASSES.** That
  script is G0's and re-derives form (ii)'s bound from the generation it is
  pointed at by the charter's clause-2 rule — on the FITTED bed that rule returns
  **0.0013**, and eight rows miss it. The bound Decision Log 1 (c) RULED is
  **0.0042**, derived from the pre-fit bed before the fit existed, and `verdict.py`
  reads C1 against that: **twelve of twelve PASS**. A bound re-derived on the bed
  it is being read against is a moving target and is not the ruled clause
  (review closure, finding N-11).
- **`verdict.txt` §7's three `chromaStructureRatioR` rows print a frozen cut
  beside a re-derived reading.** `stops.py` reads M1 and M2 out of W31 G4's
  committed `chroma-cut.json`, which is one number per cell and does not move
  when a round does; §7 now prints that value and, beside it, the same statistic
  re-derived from the matrix this gate wrote (review closure, finding N-14).

## To reproduce

```bash
cd packages/calibration
# the before
VITREA_G1_SCRATCH=/tmp/w32-g1-fit results/2026-09-21-w32-g1-shadow-fit/render-bed.sh pre-fit \
  profiles/apple-macos-27.0-1x-light-standard-glass0.5.json \
  profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json \
  profiles/apple-macos-27.0-1x-dark-standard-glass0.5.json \
  profiles/apple-macos-27.0-1x-dark-standard-glass0.5-receded.json
python3 results/2026-09-21-w32-g1-shadow-fit/repro.py /tmp/w32-g1-fit/pre-fit/matrix.json

# a round
python3 results/2026-09-21-w32-g1-shadow-fit/constants.py /tmp/A.json light.spreadPx=0.5
VITREA_G1_SCRATCH=/tmp/w32-g1-fit results/2026-09-21-w32-g1-shadow-fit/round.sh A /tmp/A.json
```

The rounds render into `$VITREA_G1_SCRATCH` and `--out-matrix` there; the canonical
`results/matrix.json` and the canonical `web-captures/` are never written by a round, and
`compare` refuses either by name if one is passed.
