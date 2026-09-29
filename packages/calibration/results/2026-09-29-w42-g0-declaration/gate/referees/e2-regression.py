"""W41 G2 — E2's rendered-edge regression over the generation the rows now name (c9a §5.193).

E2 is W38's frozen rendered-edge row (charter clause 1c; Decision Log 4): 212 non-holdout
active macOS 27 WebGPU `gpu-texture` rows under three declared estimators, and the pre-W38
web cut `e2-baseline.json.gz`, which `e2.py --verify` reproduces. This script applies e2.py's
population rule and estimator — imported from e2.py, not forked — to the rows the current
union names (`--stage DIR`: the scratch union that stage would publish), reads each web PNG
from the `--captures` root whose metadata names that row's capturePath, and compares every
bin with the frozen baseline under E2's bound: no measured bin's per-channel residual
worsens by more than `boundRegressionCodes` (1 code). UNMEASURED never passes. A bin the
baseline measured and this read does not is LOST and fails; a bin unmeasured on either side
is counted UNMEASURED, beside the verdict and never inside it; an absent capture fails.

E2's population is the active pose only and W41 G2 moves only the light RECEDED document,
so the web PNGs are expected to be byte-identical to the baseline's. That is shown per cell
— the capture's SHA-256 against the baseline's, and the whole computed row against the
baseline row with only its capturePath and document pair set aside — not assumed.

Every row must name documents that are the files on disk: a regression read of the shipped
generation. e2.py's own resolver admits a retired copy for its frozen reference; this read
does not.

W42 G0 (charter clause 10): "the files on disk" is `Source.admitted`, the shipped documents
under profiles/ plus any declared `--candidate`, each at its hash (W41 hashed whatever file
the row's path named). With a candidate the summary carries `admission` after `source`
(it has no `atDocuments`) and stdout opens `# CANDIDATE`.

    python3.12 -B e2-regression.py [--stage DIR ...] [--candidate PATH[=SHA12] ...]
                                   [--captures ROOT ...] [--out PATH] [--bins PATH]
"""
import argparse
import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[3]
sys.path.insert(0, str(HERE))
import referee_source  # noqa: E402

E2_DIR = CAL / 'results/2026-09-25-w38-g0-rim-axis-cut'
sys.path.insert(0, str(E2_DIR))
import e2  # noqa: E402

GENERATION_FIELDS = ('capturePath', 'documents')
BIN_IDENTITY = ('side', 'member', 'shell', 'angleBin', 'pixels')


def encoded(obj):
    return json.dumps(obj, sort_keys=True, indent=1, allow_nan=False).encode() + b'\n'


def compare_bins(cell, new, old, bound):
    """One verdict per bin: within, FAIL, LOST, NO_BASELINE or UNMEASURED."""
    if len(new['bins']) != len(old['bins']):
        raise ValueError(f'{cell}: bin geometry differs from the baseline')
    out = []
    for i, (nb, ob) in enumerate(zip(new['bins'], old['bins'])):
        identity = {k: nb[k] for k in BIN_IDENTITY if k in nb}
        if identity != {k: ob[k] for k in BIN_IDENTITY if k in ob}:
            raise ValueError(f'{cell}: bin {i} geometry differs from the baseline')
        entry = dict(cell=cell, bin=i, **identity)
        if ob['status'] == 'measured' and nb['status'] == 'measured':
            delta = [a - b for a, b in zip(nb['residualRGB'], ob['residualRGB'])]
            entry.update(verdict='FAIL' if max(delta) > bound else 'within',
                         baselineRGB=ob['residualRGB'], residualRGB=nb['residualRGB'],
                         deltaRGB=delta, worstDelta=max(delta))
        elif ob['status'] == 'measured':
            entry.update(verdict='LOST', baselineRGB=ob['residualRGB'], reason=nb.get('reason'))
        elif nb['status'] == 'measured':
            entry.update(verdict='NO_BASELINE', residualRGB=nb['residualRGB'],
                         reason=ob.get('reason'))
        else:
            entry.update(verdict='UNMEASURED', reason=nb.get('reason'))
        out.append(entry)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    referee_source.add_source_arguments(parser)
    referee_source.add_capture_arguments(parser)
    parser.add_argument('--out', type=Path, default=HERE / 'e2-regression.json')
    parser.add_argument('--bins', type=Path, default=HERE / 'e2-regression-bins.json.gz',
                        help='every bin comparison, gzip JSON (bulky)')
    args = parser.parse_args()

    decl = e2.read('e2-declaration.json')
    bound = decl['boundRegressionCodes']
    baseline_raw = (E2_DIR / 'e2-baseline.json.gz').read_bytes()
    baseline = {row['cell']: row for row in e2.read('e2-baseline.json.gz')}
    source = referee_source.load(args)
    native = e2.CanonicalNativeReader()
    mapped = e2.population(native, dict(cells=source.rows))
    declared = [ref['cell'] for ref in decl['cells']]
    if sorted(baseline) != sorted(declared):
        raise SystemExit('e2-regression: the frozen baseline and declaration disagree')
    # The frozen population is E2's; a declared cell the rows no longer carry is coverage
    # lost and fails. A cell the rule now admits that the declaration never held (a stage
    # that reads fixtures the pre-W38 generation did not) has no baseline: it is named,
    # UNMEASURED for E2's bound, and never a pass.
    dropped = sorted(set(declared) - set(mapped))
    outside = sorted(set(mapped) - set(declared))
    captures = referee_source.Captures(args.captures)

    rows, bins, cells = [], [], []
    for pinned in decl['cells']:
        cell = pinned['cell']
        if cell in dropped:
            continue
        row = mapped[cell]
        named = referee_source.store.documents(row)
        stale = [f'{path} sha256:{sha}' for _, path, sha in named
                 if source.admitted.get(path) != sha]
        if stale:
            raise SystemExit(f'e2-regression: {cell} names documents that are neither shipped nor '
                             f'a declared candidate at that hash: {stale}')
        ref = e2.reference(native, cell, row)
        if (ref['estimator'], ref['role']) != (pinned['estimator'], pinned['role']) or (
                ref['nativeSha256'] is not None and ref['nativeSha256'] != pinned['nativeSha256']):
            raise SystemExit(f'e2-regression: {cell} native reference or estimator moved')
        try:
            reader = captures.select(cell, row)
        except FileNotFoundError:
            reader = captures.readers[0]  # e2.compute reports the absence as UNMEASURED
        result = e2.compute(native, reader, cell, row, ref)
        old = baseline[cell]
        rows.append(result)
        compared = compare_bins(cell, result, old, bound)
        bins.extend(compared)
        strip = lambda r: {k: v for k, v in r.items() if k not in GENERATION_FIELDS}
        cells.append(dict(
            cell=cell, estimator=result['estimator'], status=result['status'],
            baselineStatus=old['status'],
            capturePath=result['capturePath'], baselineCapturePath=old['capturePath'],
            webSha256=result['webSha256'], baselineWebSha256=old['webSha256'],
            png=('absent' if result['webSha256'] is None else
                 'identical' if result['webSha256'] == old['webSha256'] else 'differs'),
            rowIdenticalExceptGeneration=strip(result) == strip(old),
            worstDelta=max((b['worstDelta'] for b in compared if 'worstDelta' in b), default=None),
            verdicts={v: sum(b['verdict'] == v for b in compared) for v in
                      ('within', 'FAIL', 'LOST', 'NO_BASELINE', 'UNMEASURED')}))

    count = lambda v: sum(b['verdict'] == v for b in bins)
    measured = [b for b in bins if 'worstDelta' in b]
    worst = max(measured, key=lambda b: b['worstDelta'], default=None)
    absent = [c['cell'] for c in cells if c['png'] == 'absent']
    summary = dict(
        claims='c9a §5.193; W38 clause 1c, Decision Log 4',
        what="E2's population rule and estimator (e2.py, imported) on the rows the source "
             'names, per bin against the frozen pre-W38 baseline',
        source=source.described,
        **source.stamp,
        matrixSha256=source.legacy_sha256,
        captures=[str(r) for r in captures.roots],
        baseline=dict(file=str((E2_DIR / 'e2-baseline.json.gz').relative_to(CAL)),
                      sha256=hashlib.sha256(baseline_raw).hexdigest(),
                      cells=len(baseline)),
        bound=dict(regressionCodes=bound,
                   rule='per bin and channel, residualRGB(now) - residualRGB(baseline) <= bound '
                        'on every bin measured in both; LOST and absent captures fail; '
                        'UNMEASURED is counted, never passed'),
        generations=sorted({f"{d['materialProfile']} / {d['recededProfile']}" for d in
                            (dict((k, s) for k, _, s in referee_source.store.documents(mapped[c]))
                             for c in declared)}),
        cells=len(cells),
        declaredCellsWithoutRow=dropped,
        outsideFrozenPopulation=dict(
            count=len(outside), verdict='UNMEASURED: no pre-W38 baseline; not a pass', cells=outside),
        pngs=dict(identical=sum(c['png'] == 'identical' for c in cells),
                  differs=[c['cell'] for c in cells if c['png'] == 'differs'],
                  absent=absent),
        rowsIdenticalExceptGeneration=sum(c['rowIdenticalExceptGeneration'] for c in cells),
        capturePathsMoved=sum(c['capturePath'] != c['baselineCapturePath'] for c in cells),
        bins=dict(total=len(bins), measuredBoth=len(measured), within=count('within'),
                  FAIL=count('FAIL'), LOST=count('LOST'), NO_BASELINE=count('NO_BASELINE'),
                  UNMEASURED=count('UNMEASURED')),
        worstDelta=None if worst is None else {k: worst[k] for k in
                                               ('cell', 'bin', 'worstDelta', 'deltaRGB')},
        failures=[b for b in bins if b['verdict'] in ('FAIL', 'LOST')],
        e2Summary=e2.summary(rows),
        e2SummaryEqualsPinned=e2.summary(rows) == e2.read('e2-summary.json'),
        holds=count('FAIL') == 0 and count('LOST') == 0 and not absent and not dropped,
        perCell=cells)
    with args.bins.open('xb') as out:
        out.write(gzip.compress(encoded(bins), mtime=0))
    with args.out.open('xb') as out:
        out.write(encoded(summary))
    source.banner()
    print(json.dumps({k: summary[k] for k in ('source', 'cells', 'declaredCellsWithoutRow',
                                              'outsideFrozenPopulation', 'pngs',
                                              'rowsIdenticalExceptGeneration',
                                              'capturePathsMoved', 'bins', 'worstDelta', 'holds',
                                              'e2SummaryEqualsPinned')}, indent=1))
    return 0 if summary['holds'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
