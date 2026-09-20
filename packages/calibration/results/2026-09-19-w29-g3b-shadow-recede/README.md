# W29 G3b — the outer shadow read and refit, and the macOS 27 receded endpoints

W29 Decision Log 6 (a), (d) and (e), ruled by the user 2026-09-19; contracts X1, X3, X5, X7;
claims **§5.154**. Nothing under `apps/reference-apple/fixtures/` was written by this gate, no
native capture was taken, `DEFAULT_MATERIAL_PROFILE` did not move and the 26.5 bed — its documents,
its rows, its bounds and its floors — is byte-identical throughout.

## What is here

| file | what it is |
| --- | --- |
| `bar-declaration.md` | the shadow axis's seventeen metrics and the bar they are read against, **committed before any 26.5 pair was opened** |
| `noise-bar.json` | the 624-cell 27-against-27 bar, all forty-nine metrics |
| `bar-reproduction.py` / `.txt` | the check that the instrument's extension changed none of G2's thirty-two metrics: 190,683 readings, zero disagreements (its last line says "thirty-one" — see the correction below) |
| `native-delta.json`, `recede-delta.json`, `law-tables.txt`, `delta-run.txt` | the read, in the instrument's own shapes |
| `shadow-delta.py` | the per-cell cut of it a refit needs: the 26.5 and 27 readings of one cell side by side |
| `bound.json` | W27c G1b's three clauses carried to the 27 receded bed at their 26.5 values, **committed before the endpoints were fitted** |
| `fitted-shadow.json` | the only numbers this child chose for the outer shadow, and the structure it could not fit |
| `fitted-receded.json` | the only numbers it chose for the two receded endpoints, and the two weaknesses in them |
| `build-shadow.py`, `build-receded.ts` | the two documents' builders — one patches the committed 27 actives, one merges over the shipped 26.5 endpoint |
| `seal.ts`, `sealed-documents.txt` | the four documents' hashes, and X1 re-proved on every run |
| `document-diff.py` / `.txt` | the leaf-by-leaf proof that only the shadow block moved in the active documents |
| `canonical-read.sh`, `canonical-read-calval.txt`, `canonical-read-holdout.txt` | the read, refused at any bytes but the sealed four |
| `shadow-table.py` | the shadow axis of a fit label's matrices, with the holdout dropped in the reader |
| `score-bound.ts`, `verdict-recede.json`, `verdict-recede.txt` | `bound.json` scored over the receded rows |
| `referee.txt` | the declared active tables over the canonical matrix, per profile per tier per clause |
| `sheets/` | native \| vitrea \| difference ×8, six profiles, two tiers, both poses |
| `freeze-verify-open.txt`, `freeze-verify-close.txt` | the 26.5 freeze at this gate's opening and close |
| `verify-*.txt` | build, lint, test, goldens and the GPU suite on the finished tree |

## How it was run

```bash
cd packages/calibration
R=results/2026-09-19-w29-g3b-shadow-recede

# 1. The bar, and the delta that reads the shadow for the first time.
npx tsx cli/native-delta.ts bar   --runs "$HOME/vitrea-w29-27-run" --out $R/noise-bar.json
python3 $R/bar-reproduction.py > $R/bar-reproduction.txt
#    ... committed, with bar-declaration.md and bound.json, BEFORE the line below
npx tsx cli/native-delta.ts delta --bar $R/noise-bar.json --out $R
npx tsx cli/native-delta.ts tables --dir $R > $R/law-tables.txt

# 2. The fit. Every round is G3's fit.py, unchanged, into scratch.
export VITREA_G3_SCRATCH=/tmp/g3b-scratch
python3 results/2026-09-19-w29-g3-refit/fit.py render <label> <profile> webgpu <document> \
    [--receded-profile <candidate>] --set calibration --scene <ids>
python3 $R/shadow-table.py <label>          # the shadow axis
python3 results/2026-09-19-w29-g3-refit/fit.py table <label> interiorMean   # the recede's level

# 3. The documents, and the seal.
python3 $R/build-shadow.py
npx tsx  $R/build-receded.ts
npx tsx  $R/seal.ts | tee $R/sealed-documents.txt
python3 $R/document-diff.py > $R/document-diff.txt

# 4. The read, once, at the sealed four.
$R/canonical-read.sh calibration,validation > $R/canonical-read-calval.txt
$R/canonical-read.sh holdout                > $R/canonical-read-holdout.txt
npx tsx  $R/score-bound.ts | tee $R/verdict-recede.txt
python3  $R/sheets.py
```

## Five things to read before any number here

1. **The bar is G2's, and it is 27-against-27.** The construction, the rule and the zero-spread
   fallback are `results/2026-09-19-w29-g2-native-delta/bar-declaration.md`'s, unchanged. So
   "moved" means beyond what this bed does against itself, the 26.5 bed's own spread is not in it
   and is not derivable, and a cell that fails to move is the weaker of the two statements.

2. **The coupled increased-contrast profile's thirty-two cells are read UNBARRED and are reported
   rather than judged.** They were published by G1c Part B after G2's bar was built, so they have no
   shadow bar anywhere: G2's eight passes do not cover their sitting and G1c's own bar predates the
   shadow metrics. A bar built for them now would be a bar declared after their first reading, which
   is what X5 forbids, so this gate does not build one — their readings are printed with the rest
   and carry no verdict. Every other 27 profile, including the DECOUPLED increased-contrast one, is
   barred normally.

3. **The fit never read a holdout row**, and on the SHADOW half the drop is in `shadow-table.py`
   rather than in each invocation's scene list. One round's scene list did name two holdout ids; the
   reader dropped them, printed that it had, and no number off those captures reached a table or a
   constant. **Scoped 2026-09-19 (review closure):** the RECEDE half was read through
   `results/2026-09-19-w29-g3-refit/fit.py table`, which has no holdout filter — it prints every row
   in the label's scratch matrices — so that half's guarantee is **procedural**: each invocation
   passed `--set calibration` with an explicit `--scene` list naming no holdout id — the invocation
   form `fitted-receded.json`'s `reproduce` line records. The statement above
   stands for both halves; the *enforcement* is a refusing reader on one and the operator's scene
   list on the other, and a reader-side drop shared by both is in `specs/tech-debt-tracker.md`.

4. **`bar-reproduction.txt`'s verdict line says "thirty-one metrics" and the number is thirty-two**
   (correction 2026-09-19, review closure). Its own header says `shared 32`, it compares 32
   `bedMinimumNonZeroBar` entries, and claims §5.154 §1 says thirty-two. The generated line is left
   exactly as the run wrote it — nothing under `results/` is edited after it is committed — and this
   is the correction beside it. Nothing about the check changes: 32 shared metrics, 190,683 readings,
   zero disagreements, zero rows present in one bar and absent in the other.

5. **Two weaknesses in the receded fit are recorded rather than removed**, both about the
   response's dark anchor and both in `fitted-receded.json`: the light document's first ordinate is
   identified by no untinted calibration cell and was moved on two `impulse` VALIDATION cells, and
   the dark document's sits at the bottom of its range with a residual no value of it reaches. The
   bound is scored over those cells anyway and the verdict names them.
