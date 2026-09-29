"""Complete seven-repeat scoring with inactive-first gate and separate controls."""
from collections import Counter
import numpy as np
from replay import m, ENDPOINTS, compact_predict


def summarize(rows):
    counts = Counter()
    statuses = Counter()
    worst = None
    worst_excess = None
    for row in rows:
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
            for channel in range(3):
                statuses[reading['status'][channel]] += 1
                value = reading['errorCodes'][channel]
                if value is None:
                    continue
                bound = max(1., score['barRGB'][channel])
                witness = {k: row[k] for k in ('cell', 'endpoint', 'scale', 'member',
                                                'part', 'side', 'shell', 'bin')}
                witness.update(channel='RGB'[channel], repeat='median' if ri == 0 else ri-1,
                               codes=value, bound=bound, excess=value-bound,
                               status=reading['status'][channel])
                if worst is None or value > worst['codes']:
                    worst = witness
                if worst_excess is None or value-bound > worst_excess['excess']:
                    worst_excess = witness
    names = ('requiredBins', 'admittedBins', 'populationDeficientBins',
             'shadowControlBins', 'bindingFailedBins', 'allChannelFailedBins', 'railFailedBins')
    return dict(**{k: counts[k] for k in names}, statusComparisons=dict(statuses),
                survives=counts['admittedBins'] > 0 and counts['bindingFailedBins'] == 0,
                worstMeasured=worst, worstBoundExcess=worst_excess)


def control_key(observation, member, binrow):
    sid = observation['cell'].split('/', 1)[1]
    stem = sid.removesuffix('__inactive').removesuffix('__rest')
    return (ENDPOINTS[observation['endpoint']].split('-')[0], observation['scale'],
            stem, member, binrow['part'], binrow['side'], binrow['shell'], binrow['bin'])


def inactive_zero_controls(observations):
    """Native zero classification frozen independently of candidate width.

    The inherited zero reading is equality of each repeat's bin mean to its own
    no-glass mean. Preserve the stronger pointwise equality as a separate fact.
    """
    result = {}
    for o in observations:
        if o['endpoint'] not in (1, 3):
            continue
        for part in o['parts']:
            for bi, row in enumerate(part['bins']):
                if row['pixels'] < 4:
                    continue
                at = o['binids'] == part['offset']+bi
                local = part['binids'] == part['offset']+bi
                xy = part['xy'][local]
                reference = part['reference'][xy[:, 1], xy[:, 0]]
                delta = o['runs'][:, at].astype(float)-reference
                if np.all(delta.mean(axis=1) == 0):
                    result[control_key(o, part['member'], row)] = dict(
                        zeroRepeatMeans=True, zeroEveryPixel=bool(np.all(delta == 0)))
    return result


def bin_rows(observation, prediction, controls, shadow_only=False):
    o = observation
    for part in o['parts']:
        for bi, row in enumerate(part['bins']):
            at = o['binids'] == part['offset']+bi
            count = int(at.sum())
            # Deficient bins never entered the fitting arrays; keep their true
            # population and status as explicit exclusions, not fabricated pixels.
            if row['pixels'] < 4:
                score = dict(pixels=row['pixels'], barRGB=None, median=None, runs=[],
                             survives=False, heldoutCoverage=False,
                             worstChannelFailure=False, allChannelFailure=False)
            else:
                if count != row['pixels']:
                    raise ValueError('prepared array lost an admitted bin pixel')
                score = m.score_bin(prediction[at], o['runs'][:, at])
            zero = controls.get(control_key(o, part['member'], row))
            top = o['endpoint'] == 2 and o['background'] in ('g128', 'g255') \
                and row['part'] == 'straight' and row['side'] == 'top'
            active = o['endpoint'] in (0, 2)
            yield dict(cell=o['cell'], role=o['role'], endpoint=ENDPOINTS[o['endpoint']],
                       scale=o['scale'], member=part['member'], part=row['part'],
                       side=row['side'], shell=row['shell'], bin=row['bin'],
                       score=score, shadowControl=active and (zero is not None or top),
                       zeroInactiveControl=zero, darkTopControl=top,
                       residualClass='observed-zero support/control' if zero is not None
                           else 'dark-top shadow control' if top else 'stroke material/angular',
                       prediction='held shadow only' if shadow_only else 'stroke plus held shadow')


def score_candidate(observations, q, family, css, curvature, controls, emit):
    """Inactive endpoints are the first gate; active cannot rescue a failed one."""
    strata = {}
    overall = []
    for endpoint in (1, 3, 0, 2):
        for role in ('calibration', 'validation'):
            for scale in (1, 2):
                rows = []
                for o in observations:
                    if (o['endpoint'], o['role'], o['scale']) != (endpoint, role, scale):
                        continue
                    prediction = compact_predict(q, o, family, css, curvature)
                    for row in bin_rows(o, prediction, controls):
                        emit(row); rows.append(row)
                if rows:
                    key = f'{ENDPOINTS[endpoint]}/{role}/{scale}x'
                    strata[key] = summarize(rows)
                    overall.extend(rows)
    inactive = summarize(r for r in overall if r['endpoint'].endswith('-inactive'))
    active = summarize(r for r in overall if r['endpoint'].endswith('-active'))
    return dict(strata=strata, inactiveFirst=inactive, activeSecond=active,
                survives=inactive['survives'] and active['survives'],
                authority='LOCAL fitted candidate; failure does not exclude every family coefficient')


def shadow_control_rows(observations, controls):
    for o in observations:
        if o['endpoint'] not in (0, 2):
            continue
        prediction = np.concatenate([p['compact'].mean_b-p['amplitude']*p['compact'].mean_bfall
                                     for p in o['parts']])
        for row in bin_rows(o, prediction, controls, shadow_only=True):
            if row['shadowControl']:
                yield row
