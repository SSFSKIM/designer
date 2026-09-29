"""Additive W41 clause-4 uniform transfer coverage; c9a §5.192.

The 408-cell fit and every coefficient remain frozen. Read only the previously
omitted admitted solid-background glass cells/members through the guarded Reader,
calibration then validation, and score the complete uniform union without fitting.
Public metadata gives an explicit included/excluded census, including unopened
holdout and unadmitted phase cells. Existing step-2 evidence is never rewritten.
"""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import numpy as np
import replay


def load(path):
    data = path.read_bytes()
    return json.loads(gzip.decompress(data) if path.suffix == '.gz' else data)


def candidates(attempt):
    result = []
    freeze = load(attempt / 'fit-freeze.json')
    assert len(freeze['files']) == 12
    for name, digest in freeze['files'].items():
        path = attempt / name
        assert replay.digest(path) == digest
        fit = load(path)
        methods = {'leastSquares': fit['local']['leastSquares']}
        if fit['family'] == 'O12':
            methods['localMinimax'] = fit['local']['minimax']
        else:
            methods['globalMinimax'] = fit['globalMinimax']
            if fit['survival']['status'] == 'forward-feasible':
                methods['survivalWitness'] = fit['survival']
        for method, candidate in methods.items():
            if candidate is not None and 'coefficients' in candidate:
                result.append(dict(family=fit['family'], endpoint=fit['endpoint'], method=method,
                    coefficients=candidate['coefficients'], neutral=fit['neutralOrdinatesCodes'],
                    source=name, sourceSha256=digest))
    return result


def census_row(wave, reader, cell, existing):
    sid = cell.split('/', 1)[1]
    scene = wave.scenes[sid]
    comp = wave.component(sid)
    bg = wave.spec['backgrounds'][scene['background']]
    admitted = (cell, 'crop') in reader.entries
    row = dict(cell=cell, role=wave.roles[sid], archiveAdmitted=admitted,
               backgroundKind=bg['kind'], componentKind=comp['kind'], members=[])
    if row['role'] == 'holdout':
        row['disposition'] = 'excluded: holdout sealed; metadata only'
    elif not admitted:
        row['disposition'] = 'excluded: no admitted crop in pinned inventory'
    elif comp['kind'] == 'none':
        row['disposition'] = 'excluded: no-glass reference, not a glass body'
    elif bg['kind'] != 'solid':
        row['disposition'] = 'excluded: structured background; separate spatial scope'
    else:
        for i, member in enumerate(replay.native.wave.members(comp)):
            opaque = member.get('opaque', False)
            row['members'].append(dict(member=i, kind=member['kind'], size=member['size'],
                disposition='excluded: opaque control, not glass' if opaque else
                    'covered: original step2' if cell in existing else 'covered: supplemental transfer'))
        covered = [m for m in row['members'] if m['disposition'].startswith('covered:')]
        row['disposition'] = ('covered: original step2' if cell in existing else
                              'covered: supplemental transfer') if covered else 'excluded: opaque controls only'
    return row


def score_member(candidate, row, member, metadata, coverage):
    deep = row['members'][member]
    assert min(deep['pixels']) >= 4 and len(row['stateMembership']) == 7
    pred = replay.body.forward(candidate['family'], [row['inputCodes']], candidate['neutral'],
                               candidate['coefficients'])
    return dict(cell=row['cell'], member=member, memberKind=metadata['kind'],
        memberSize=metadata['size'], coverage=coverage, role=row['role'], scale=row['scale'],
        endpoint=row['endpoint'], family=candidate['family'], method=candidate['method'],
        predictedRGB=pred[0].tolist(), nativeRGB=deep['medianRGB'], barRGB=deep['barRGB'],
        pixels=deep['pixels'], stateMembership=row['stateMembership'],
        median=replay.body.score(pred, [deep['medianRGB']], [deep['barRGB']]),
        repeats=replay.body.score(np.repeat(pred, 7, axis=0), deep['runMediansRGB'], deep['barRGB']))


def failed(score):
    return score['uncensoredFailures'] + score['railFailures'] > 0


def summary_group(rows):
    witness = []
    rail = []
    for r in rows:
        for channel, error in enumerate(r['median']['uncensoredErrorCodes'][0]):
            if error is not None:
                witness.append(dict(cell=r['cell'], member=r['member'], channel='RGB'[channel],
                                    errorCodes=error))
            rail.append(dict(cell=r['cell'], member=r['member'], channel='RGB'[channel],
                             boundDeficitCodes=r['median']['boundDeficitCodes'][0][channel]))
    statuses = Counter(s for r in rows for s in r['median']['statuses'][0])
    repeat_statuses = Counter(s for r in rows for rr in r['repeats']['statuses'] for s in rr)
    failures = [r for r in rows if failed(r['median']) or failed(r['repeats'])]
    return dict(cells=len({r['cell'] for r in rows}), members=len(rows),
        populationDeficientMembers=0, statusCounts=dict(statuses), repeatStatusCounts=dict(repeat_statuses),
        failedCells=len({r['cell'] for r in failures}), failedMembers=len(failures),
        allChannelFailedMembers=sum(r['median']['allChannelFailedCells'] for r in rows),
        measuredFailedChannels=sum(r['median']['uncensoredFailures'] for r in rows),
        railFailures=sum(r['median']['railFailures'] for r in rows),
        repeatMeasuredFailedChannels=sum(r['repeats']['uncensoredFailures'] for r in rows),
        repeatRailFailures=sum(r['repeats']['railFailures'] for r in rows),
        repeatMaximumCodes=max(r['repeats']['worstChannelCodes'] for r in rows),
        worstMeasured=max(witness, key=lambda r: r['errorCodes']) if witness else None,
        worstRail=max(rail, key=lambda r: r['boundDeficitCodes']) if rail else None,
        survives=not failures)


def main(archive, attempt, out):
    out.mkdir(parents=True, exist_ok=False)
    assert replay.digest(replay.G0 / 'bounds-declaration.txt') == replay.DECLARATION_SHA
    for name, digest in load(attempt / 'manifest.json').items():
        assert replay.digest(attempt / name) == digest
    frozen = candidates(attempt)
    old_rows = load(attempt / 'calibration.json.gz')['rows'] + load(attempt / 'validation.json.gz')['rows']
    existing = {r['cell']: r for r in old_rows}
    assert len(existing) == 496
    sources = [Path(__file__), Path(replay.__file__), replay.G2 / 'native.py',
               replay.native.G0 / 'wave.py', replay.native.G0 / 'w39_readers.py',
               replay.native.G0 / 'w39_archive.py', replay.G0 / 'body-instrument/body41.py']
    replay.save(out / 'provenance.json', dict(startedAt=replay.stamp(), sourceFitFreezeSha256=replay.digest(attempt / 'fit-freeze.json'),
        sourceAttemptManifestSha256=replay.digest(attempt / 'manifest.json'),
        declarationSha256=replay.DECLARATION_SHA, archiveInventorySha256=replay.INVENTORY_SHA,
        archive=str(archive), rawRootDenied=str(Path.home() / 'vitrea-w39'),
        roleOrder=['calibration', 'validation'], coefficientSource='unchanged attempt-1 fit-freeze',
        fitsPerformed=0, holdoutOpened=False,
        sources={str(p.relative_to(replay.RESULTS)): replay.digest(p) for p in sources}))
    replay.save(out / 'frozen-candidates.json', frozen)
    census = []
    added = []
    for role in ['calibration', 'validation']:
        wave, reader = replay.native.guarded(archive, (role,))
        assert reader.generation == replay.INVENTORY_SHA
        role_rows = []
        for cell in sorted(wave.cells):
            sid = cell.split('/', 1)[1]
            if wave.roles[sid] != role:
                continue
            item = census_row(wave, reader, cell, existing)
            census.append(item)
            if item['disposition'] != 'covered: supplemental transfer':
                continue
            row = replay.native.cell(reader, cell)
            bg = wave.spec['backgrounds'][wave.scenes[sid]['background']]
            assert len(row['members']) == len(item['members'])
            assert row['pose'] == wave.scenes[sid]['state']
            row.update(inputCodes=bg['srgb'], endpoint=row['scheme'] +
                       ('-active' if row['pose'] == 'rest' else '-inactive'))
            role_rows.append(row)
        replay.save(out / f'{role}-additional.json.gz', role_rows)
        added.extend(role_rows)
    # The guard remains validation-only. These are public identities/inventory
    # membership, not a holdout Reader or a native payload access.
    for cell in sorted(wave.cells):
        if wave.roles[cell.split('/', 1)[1]] == 'holdout':
            census.append(census_row(wave, reader, cell, existing))
    census.sort(key=lambda r: r['cell'])
    assert len(census) == len(wave.cells)
    replay.save(out / 'census.json', dict(cells=census,
        dispositions=dict(Counter(r['disposition'] for r in census)),
        requiredUniformCells=sum(r['disposition'].startswith('covered:') for r in census),
        requiredUniformMembers=sum(m['disposition'].startswith('covered:') for r in census for m in r['members']),
        definition='All admitted calibration/validation solid-background glass members; references, opaque controls, structured backgrounds and unadmitted cells explicitly excluded; holdout metadata only'))
    all_rows = {**existing, **{r['cell']: r for r in added}}
    scores = []
    for item in census:
        if not item['disposition'].startswith('covered:'):
            continue
        row = all_rows[item['cell']]
        for member in item['members']:
            if not member['disposition'].startswith('covered:'):
                continue
            for candidate in frozen:
                if candidate['endpoint'] == row['endpoint']:
                    scores.append(score_member(candidate, row, member['member'], member,
                                               member['disposition']))
    replay.save(out / 'scores.json.gz', scores)
    strata = []
    keys = sorted({(r['family'], r['endpoint'], r['scale'], r['method'], r['role'], r['coverage']) for r in scores})
    for key in keys:
        rr = [r for r in scores if (r['family'], r['endpoint'], r['scale'], r['method'], r['role'], r['coverage']) == key]
        strata.append(dict(zip(['family', 'endpoint', 'scale', 'method', 'role', 'coverage'], key),
                           **summary_group(rr)))
    endpoints = []
    for family, endpoint in sorted({(r['family'], r['endpoint']) for r in scores}):
        methods = []
        for method in sorted({r['method'] for r in scores if r['family'] == family and r['endpoint'] == endpoint}):
            rr = [r for r in scores if (r['family'], r['endpoint'], r['method']) == (family, endpoint, method)]
            methods.append(dict(method=method, **summary_group(rr)))
        endpoints.append(dict(family=family, endpoint=endpoint, methods=methods,
                              survivingMethods=[m['method'] for m in methods if m['survives']]))
    complete = {family: all(e['survivingMethods'] for e in endpoints if e['family'] == family)
                for family in sorted({e['family'] for e in endpoints})}
    replay.save(out / 'summary.json', dict(completedAt=replay.stamp(),
        originalCells=len(existing), additionalCells=len(added),
        additionalMembers=sum(len(r['members']) for r in added),
        allUniformCells=len(all_rows), scoredCellMemberCandidates=len(scores),
        repeatCellMemberCandidates=7 * len(scores), strata=strata, endpoints=endpoints,
        completeFourEndpointFamilies=complete, fitsPerformed=0, holdoutOpened=False,
        qualification='Original report-1 endpoint survival labels apply only to its explicitly tabled colour/thick subset. This supplement is the complete admitted uniform transfer verdict; it does not refit or establish any new global family negative.',
        spatialSelection='Existing diagnostic E3 selection and its coefficient/source hashes remain unchanged'))
    assert replay.digest(attempt / 'fit-freeze.json') == load(out / 'provenance.json')['sourceFitFreezeSha256']
    replay.save(out / 'manifest.json', {p.name: replay.digest(p) for p in sorted(out.iterdir()) if p.is_file()})
    print(json.dumps(dict(addedCells=len(added), addedMembers=sum(len(r['members']) for r in added),
        allUniformCells=len(all_rows), completeFamilies=complete,
        survivingEndpoints=[(e['family'], e['endpoint']) for e in endpoints if e['survivingMethods']]), indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=Path)
    parser.add_argument('attempt', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    main(args.archive, args.attempt, args.out)
