"""Replay step-2 certificates, role bindings and every saved forward score.

No optimizer or native payload is opened. Inputs are the recorded guarded-reader
projections and frozen coefficients. This is not a second fitting/holdout read.
"""
import argparse
import gzip
import json
from pathlib import Path
import numpy as np
import replay


def load(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def main(attempt):
    for name, expected in load(attempt / 'manifest.json').items():
        assert replay.digest(attempt / name) == expected, name
    provenance = load(attempt / 'provenance.json')
    for name, expected in provenance['sources'].items():
        assert replay.digest(replay.RESULTS / name) == expected, name
    assert replay.digest(replay.G0 / 'bounds-declaration.txt') == replay.DECLARATION_SHA
    calibration = load(attempt / 'calibration.json.gz')['rows']
    validation = load(attempt / 'validation.json.gz')['rows']
    assert {r['role'] for r in calibration} == {'calibration'}
    assert {r['role'] for r in validation} == {'validation'}
    by_cell = {r['cell']: r for r in calibration + validation}
    assert len(by_cell) == len(calibration) + len(validation)
    for r in by_cell.values():
        assert len(r['stateMembership']) == 7
        assert len(r['members']) == 1 and min(r['members'][0]['pixels']) >= 4
    frozen = load(attempt / 'fit-freeze.json')
    assert len(frozen['files']) == 12
    fits = {}
    certificate_checks = 0
    for name, expected in frozen['files'].items():
        assert replay.digest(attempt / name) == expected
        f = load(attempt / name)
        fit_rows = [by_cell[cell] for cell in f['fitCells']]
        assert len(fit_rows) == 102
        assert all(r['role'] == 'calibration' and r['population'] == 'colour' and
                   r['endpoint'] == f['endpoint'] for r in fit_rows)
        assert {r['scale'] for r in fit_rows} == {1, 2}
        x, y, bar = replay.arrays(fit_rows)
        if f['family'] != 'O12':
            checks = replay.verify_linear(f['family'], x, f['neutralOrdinatesCodes'], y, bar,
                                          f['survival'], f['globalMinimax'])
            assert checks == f['certificateReplay']
            certificate_checks += len(checks)
        starts = f['local']['starts']
        assert [r['startIndex'] for r in starts] == list(range(16))
        assert f['local']['budget']['seed'] == 4100
        fits[f['family'], f['endpoint']] = f
    scores = load(attempt / 'scores.json.gz')
    for score in scores:
        f = fits[score['family'], score['endpoint']]
        method = score['method']
        candidate = (f['local']['leastSquares'] if method == 'leastSquares' else
                     f['local']['minimax'] if method == 'localMinimax' else
                     f['survival'] if method == 'survivalWitness' else f['globalMinimax'])
        row = by_cell[score['cell']]
        assert replay.scored(f, method, candidate, [row]) == [score]
    summary = load(attempt / 'summary.json')
    assert replay.summarize(scores) == summary['strata']
    old = load(attempt / 'b0-recorded-brackets.json')
    assert replay.digest(replay.RESULTS / old['source']) == old['sha256']
    assert old['refitted'] is False and old['w41Certification'] is False
    assert not summary['holdoutOpened']
    print(json.dumps(dict(manifestFiles=len(load(attempt / 'manifest.json')),
        sourceHashes=len(provenance['sources']), fitFiles=len(fits),
        replayedCertificateAndForwardChecks=certificate_checks,
        calibrationCells=len(calibration), validationCells=len(validation),
        scoredCellCandidates=len(scores), repeatCellCandidates=7 * len(scores),
        summaryStrata=len(summary['strata']), holdoutOpened=False), indent=2))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('attempt', type=Path)
    main(p.parse_args().attempt)
