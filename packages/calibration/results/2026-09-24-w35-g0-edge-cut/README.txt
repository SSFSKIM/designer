W35 G0a operational evidence index — c9a §5.177

This file is plain text because the worker's instructions forbid Markdown reports.
The declaration is domain.json; its digest will be pinned by the calibration test.
All native W34 reads use the unchanged wave.Reader calibration/validation roles.
The new sibling w35_readers.py is the only web pixel entry point. Canonical native
reads use its separate role guard (parent-directed): calibration/validation/probe
are admitted; holdout and recorded and bare paths refuse before payload opening.
Probe is a diagnostic role, not a new gated set (W25 DL3(e)).

Replay without capture:
  python3.12 test-readers.py
  python3.12 test-instrument.py
  python3.12 edge.py           Produces profiles and deep bars; refuses overwrite.
  pnpm --filter @vitrea/calibration exec tsx results/2026-09-24-w35-g0-edge-cut/canonical.ts
  pnpm --filter @vitrea/calibration exec tsx results/2026-09-24-w35-g0-edge-cut/identity-proof.ts

Run in a fresh evidence copy for replay; never remove a recorded result to rerun it.
Canonical web tree is the MAIN checkout, read-only, after its recorded generation
check. W34 web captures are G2/web-captures, checked against non-holdout provenance.
No W34 holdout payload or spent receipt path is read or edited. No native capture.
The first browser preflight refused nine foreign processes before launch. The
parent directed coexistence with that unrelated College session; the following
opening isolation passed once. Foreign PIDs remain recorded, not terminated.

Completed artifacts
  profiles.json.gz / profile-index.json   336 cells; full diagnostic and whole-body profiles.
  deep-bars.json.gz / bar-headlines.json  All admitted normal/long deep shells and populations.
  line-ramp-level.json / line-level-table.csv / angular-cut.json / structured-cut.json
                                         Per-level decomposition and qualifications.
  level-table.json                       Level/chroma misses, including inactive controls.
  canonical-metrics.json                 Actual rim estimator and 1/2/3-pixel erosion.
  canonical-solids.json                  Native physical sides versus integer-ring widths.
  canonical-centre{,-left}.json          Memo centre-pixel check, not full-side averages.
  native-law-fits.json                   All-colour calibration-only nominated forward fits.
  native-grey-law-fits.json              Grey-only diagnostic; colours stay in closure.
  forward-web-check.json / synthetic.json / encoded-control.json
                                         Mapping check and discriminating interventions.
  candidate-plans.json / candidate-*.txt  Eight actual launches; scratch paths and documents.
  candidate-residuals.json.gz            Frozen-domain per-bin RGB residuals and actual bars.
  candidate-verdicts.json                Every tested candidate fails; no global optimum claim.
  receded-composition.json               Eight controls, zero changed pixels versus shipped.
  eye-*.png                             Native/shipped/candidate at1:1 pixels; inspected.
  m2-gated-attribution.json              26 current-generation M2 cells; sensitivity, not waiver.
  bounds-declaration.txt                 Unchanged stops and unresolved expected values.
  pins.json / runtime-source-provenance.json
                                         Data and unchanged runtime byte identities.
  close-*.txt                           Calibration suite, static checks and freeze.

Replay the extra analyses with canonical-solids.py, canonical-centre.py [--left],
model.py [--greys], read-candidates.py, and summarize.py. test-replay.py reproduces
normal/long deep-bar witnesses while banning raw sitting access. Production readers
use python3.12 (PIL/numpy), not the repository's lean python3 environment.

For full regeneration, copy source scripts plus domain.json and their named INPUT
artifacts into a fresh sibling directory under results, leaving its OUTPUT files
absent. Scripts refuse output overwrites. Keep the canonical tree generation check
beside a canonical replay. Browser.py is NOT an offline replay command and refuses
an already attempted plan; do not rerun it to improve residuals or repeatability.
The scratch candidate captures persist under ~/vitrea-w35/scratch/existing-leaves,
not under this disposable worktree; candidate-plans.json and browser-runs.txt name
all inputs, hashes and admitted cells. No canonical capture generation is replaced.

Qualification: no viable post-fit material exists here, so post-fit canonical M1/M2,
per-cell and predicate expectations are explicitly unidentified, not invented passes.
The G0a declaration is delivered as a negative/qualified result for independent
parent review. No G0b source or operator is written, and no coefficient transfer,
canonical read at changed bytes, CSS decline or E1 adoption is authorised.

The required complete unit suite inherits W34's command-line side/harness self-check.
It ran without capture or GUI/app-bundle activation; do not report that as "no native
executable invocation". No native capture, build, open, TCC or grant operation ran.

staged-diff-check.txt reports trailing whitespace in retained raw comparer/test
logs. Those logs are not edited to make a whitespace check green. The authored
Python/TypeScript/specification files have no whitespace warning.

Independent-review correction (§5.177 §10)
  edge.forward now refuses alpha or coverage other than1: its supported contract
  is the opaque, fully covered sampled-texture branch used by every recorded check.
  bounds-declaration-addendum.txt narrows the earlier wording beside the original
  declaration and domain, whose bytes and SHA pins remain unchanged.
  review-composition-before.txt records the old fractional-coverage counterexample.
  review-composition-red.txt / review-composition-green.txt retain failing/passing
  refusal regressions and the opaque-white and existing forward cases.
