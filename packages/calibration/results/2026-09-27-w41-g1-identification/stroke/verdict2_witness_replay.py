"""Replay M1 light-inactive verdict-2 witnesses from saved m1-transfer-1 outputs only.

Standard library only: opens the four saved *-bins.jsonl.gz, *-quadrature.jsonl.gz and
*-summary.json files, never the native archive, never instrument/replay code. It
(1) re-derives each summary stratum from the saved rows with scoring.summarize's exact
rules and requires equality with the saved summary; (2) chooses, per stratum, a
measured AND failed witness: the median reading's channel is status 'measured' and
failed, preferring bins where all seven repeats of that channel are also measured and
failed, taking the largest median excess over the declared bound max(1, bar)
(bar = 0.5 + half the run-to-run range, saved per bin as barRGB; bounds-declaration.txt
line 20 and V2 addendum), first in file order on ties; (3) bounds the fixed-32 error
below by codes - stratum max |p32-p16| (triangle inequality on a channel with no
censored pixel) and its remaining excess by that minus the bound.

  python -B verdict2_witness_replay.py            print the replay as JSON
  python -B verdict2_witness_replay.py --check V  require V's witnesses to equal the replay
"""
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / 'm1-transfer-1'
CANDIDATES = [('curvature-M1', 'leastSquares'), ('curvature-M1', 'minimax'),
              ('device-M1', 'leastSquares'), ('device-M1', 'minimax')]
LOCATION = ('cell', 'endpoint', 'scale', 'member', 'part', 'side', 'shell', 'bin')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with gzip.open(path, 'rt') as handle:
        for number, line in enumerate(handle, 1):
            yield number, json.loads(line)


def stratum(row):
    return f"{row['endpoint']}/{row['role']}/{row['scale']}x"


def summarize(entries):
    """scoring.summarize, transcribed; ties keep the first reading (strict >)."""
    counts, statuses, worst, worst_excess = Counter(), Counter(), None, None
    for _, row in entries:
        score = row['score']
        counts['requiredBins'] += 1
        if score['pixels'] < 4:
            counts['populationDeficientBins'] += 1
            continue
        counts['admittedBins'] += 1
        counts['shadowControlBins'] += bool(row['shadowControl'])
        counts['bindingFailedBins'] += bool(score['worstChannelFailure'])
        counts['allChannelFailedBins'] += bool(score['allChannelFailure'])
        readings = [score['median'], *score['runs']]
        counts['railFailedBins'] += any(any(r['boundFailure']) for r in readings)
        for ri, reading in enumerate(readings):
            for c in range(3):
                statuses[reading['status'][c]] += 1
                value = reading['errorCodes'][c]
                if value is None:
                    continue
                bound = max(1., score['barRGB'][c])
                witness = {k: row[k] for k in LOCATION}
                witness.update(channel='RGB'[c], repeat='median' if ri == 0 else ri-1,
                               codes=value, bound=bound, excess=value-bound,
                               status=reading['status'][c])
                if worst is None or value > worst['codes']:
                    worst = witness
                if worst_excess is None or value-bound > worst_excess['excess']:
                    worst_excess = witness
    names = ('requiredBins', 'admittedBins', 'populationDeficientBins', 'shadowControlBins',
             'bindingFailedBins', 'allChannelFailedBins', 'railFailedBins')
    return dict(**{k: counts[k] for k in names}, statusComparisons=dict(statuses),
                survives=counts['admittedBins'] > 0 and counts['bindingFailedBins'] == 0,
                worstMeasured=worst, worstBoundExcess=worst_excess)


def measured_failed(reading, c):
    return reading['status'][c] == 'measured' and reading['failed'][c] \
        and reading['errorCodes'][c] is not None


def choose(entries):
    """Largest-excess measured+failed median channel; all-seven-repeat tier first."""
    best = {'allSeven': None, 'medianOnly': None}
    pools = Counter()
    for number, row in entries:
        score = row['score']
        if score['pixels'] < 4:
            continue
        if len(score['runs']) != 7:
            raise ValueError('admitted bin without seven repeats')
        for c in range(3):
            median = score['median']
            if not measured_failed(median, c):
                continue
            bound = max(1., score['barRGB'][c])
            codes = median['errorCodes'][c]
            if not codes > bound:
                raise ValueError('measured channel flagged failed within its bound')
            tier = 'allSeven' if all(measured_failed(r, c) for r in score['runs']) \
                else 'medianOnly'
            pools[tier] += 1
            item = dict(row=row, line=number, channel=c, codes=codes, bound=bound,
                        excess=codes-bound)
            if best[tier] is None or item['excess'] > best[tier]['excess']:
                best[tier] = item
    return best, pools


def reading_record(reading, c):
    return {k: reading[k][c] for k in ('status', 'errorCodes', 'failed', 'boundFailure',
                                       'railPixels', 'uncensoredPixels')}


def raw_row_for(entries, label):
    for number, row in entries:
        if all(row[k] == label[k] for k in LOCATION):
            return number, row
    raise ValueError('summary label not found among saved rows')


def replay():
    result = {'candidates': []}
    for model, objective in CANDIDATES:
        stem = f'{model}-{objective}'
        paths = {k: OUT / f'{stem}-{k}' for k in
                 ('bins.jsonl.gz', 'quadrature.jsonl.gz', 'summary.json')}
        summary = json.loads(paths['summary.json'].read_text())
        grouped, cells = {}, {}
        for number, row in rows(paths['bins.jsonl.gz']):
            grouped.setdefault(stratum(row), []).append((number, row))
            cells.setdefault(row['role'], set()).add(row['cell'])
        quadrature = {}
        for number, row in rows(paths['quadrature.jsonl.gz']):
            quadrature.setdefault(stratum(row), []).append((number, row))
        saved = summary['scoring']['strata']
        if set(grouped) != set(saved):
            raise ValueError(stem + ': saved strata differ from saved rows')
        recorded_delta = summary['quadratureSensitivity']['maximumPixelDifferenceCodesByStratum']
        strata = []
        for key in sorted(grouped):
            entries = grouped[key]
            derived = summarize(entries)
            if derived != saved[key]:
                raise ValueError(f'{stem} {key}: saved summary not reproduced from rows')
            q = quadrature[key]
            delta = max(max(r['maximumPixelDifferenceRGB']) for _, r in q)
            if delta != recorded_delta[key] or len(q) != derived['admittedBins']:
                raise ValueError(f'{stem} {key}: quadrature record disagrees with summary')
            best, pools = choose(entries)
            tier = 'allSeven' if best['allSeven'] is not None else 'medianOnly'
            pick = best[tier]
            if pick is None:
                raise ValueError(f'{stem} {key}: no measured failed channel')
            row, c = pick['row'], pick['channel']
            qline, qrow = next((n, r) for n, r in q if all(r[k] == row[k] for k in LOCATION))
            witness = {k: row[k] for k in LOCATION}
            witness.update(role=row['role'], channel='RGB'[c], repeat='median',
                           status='measured', failed=True, codes=pick['codes'],
                           barRGB=row['score']['barRGB'], bound=pick['bound'],
                           excess=pick['excess'], pixels=row['score']['pixels'],
                           median=reading_record(row['score']['median'], c),
                           repeats=[reading_record(r, c) for r in row['score']['runs']],
                           sevenRepeatsMeasuredAndFailed=tier == 'allSeven',
                           source={'path': str(paths['bins.jsonl.gz']), 'line': pick['line']},
                           binQuadrature={'path': str(paths['quadrature.jsonl.gz']),
                                          'line': qline,
                                          'maximumPixelDifferenceRGB':
                                              qrow['maximumPixelDifferenceRGB']})
            lower = pick['codes'] - delta
            label = derived['worstBoundExcess']
            lline, lrow = raw_row_for(entries, label)
            li = 'RGB'.index(label['channel'])
            reading = lrow['score']['median'] if label['repeat'] == 'median' \
                else lrow['score']['runs'][label['repeat']]
            same = all(label[k] == witness[k] for k in (*LOCATION, 'channel', 'repeat'))
            other = best['medianOnly']
            strata.append(dict(
                stratum=key, requiredBins=derived['requiredBins'],
                admittedBins=derived['admittedBins'],
                populationDeficientBins=derived['populationDeficientBins'],
                bindingFailedBins=derived['bindingFailedBins'],
                allChannelFailedBins=derived['allChannelFailedBins'],
                railFailedBins=derived['railFailedBins'],
                statusComparisons=derived['statusComparisons'],
                savedRows=len(entries),
                measuredFailedMedianChannels={'sevenRepeatsAlsoMeasuredAndFailed':
                                              pools['allSeven'],
                                              'medianOnly': pools['medianOnly']},
                largerMedianOnlyExcessExcluded=None if other is None or best['allSeven'] is None
                    or other['excess'] <= best['allSeven']['excess'] else other['excess'],
                measuredWitness=witness,
                maxFixed16To32PixelDifferenceCodes=delta,
                fixed32ErrorLowerBoundCodes=lower,
                remainingExcessLowerBoundCodes=lower - pick['bound'],
                positiveFixed32Margin=lower - pick['bound'] > 0,
                rawSummaryLabel=dict(label, source={'path': str(paths['bins.jsonl.gz']),
                                                    'line': lline},
                                     instrumentFailed=reading['failed'][li],
                                     boundFailure=reading['boundFailure'][li],
                                     railPixels=reading['railPixels'][li],
                                     uncensoredPixels=reading['uncensoredPixels'][li],
                                     isMeasuredWitness=same)))
        result['candidates'].append(dict(
            model=model, objective=objective,
            files={k: {'path': str(p), 'sha256': sha(p)} for k, p in paths.items()},
            optimizerConverged=summary['optimizerConverged'], rank=summary['rank'],
            railDeficitCodes=summary['railDeficitCodes'], status=summary['status'],
            survives=summary['scoring']['survives'],
            cells={role: len(v) for role, v in sorted(cells.items())},
            strata=strata))
    margins = [s['remainingExcessLowerBoundCodes']
               for c in result['candidates'] for s in c['strata']]
    result['witnesses'] = len(margins)
    result['allPositiveFixed32Margin'] = all(m > 0 for m in margins)
    result['minimumRemainingExcessLowerBoundCodes'] = min(margins)
    return result


def check(path):
    verdict = json.loads(Path(path).read_text())
    if verdict['witnessReplay'] != replay():
        raise SystemExit('MISMATCH: ' + path)
    print('MATCH', path)


if __name__ == '__main__':
    if sys.argv[1:2] == ['--check']:
        check(sys.argv[2])
    else:
        print(json.dumps(replay(), indent=1))
