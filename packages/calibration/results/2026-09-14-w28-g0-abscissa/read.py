"""W28 G0: native-only encoded abscissae and curve-free isotonic residuals.

Run from the repository using Python 3.12 with numpy/scipy; see index.md.
No renderer imports, capture commands, reference builds, or raw sitting reads.
"""
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
import subprocess
import tempfile

import numpy as np
from scipy.ndimage import gaussian_filter

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
NOISE = 0.004


def load(path):
    return json.loads(path.read_text())


def save(name, value):
    (HERE/name).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def isotonic(x, y):
    """Equal-weight PAVA; collapse tied x BEFORE pooling descending blocks.

    Twelve decimal places removes numerical order manufactured by summation
    roundoff (e.g. a mathematically identical checker mean across pitches).
    Return fitted values in original cell order, not sorted target order.
    """
    x, y = np.round(np.asarray(x, dtype=float), 12), np.asarray(y, dtype=float)
    order = np.argsort(x, kind='stable')
    blocks = []
    for i in order:
        if blocks and blocks[-1]['x'] == x[i]:
            blocks[-1]['sum'] += y[i]
            blocks[-1]['indices'].append(int(i))
        else:
            blocks.append(dict(x=x[i], sum=y[i], indices=[int(i)]))
    pooled = []
    for block in blocks:
        pooled.append(block)
        while len(pooled) > 1:
            a, b = pooled[-2:]
            if a['sum']/len(a['indices']) <= b['sum']/len(b['indices']):
                break
            pooled[-2:] = [dict(x=b['x'], sum=a['sum']+b['sum'], indices=a['indices']+b['indices'])]
    result = np.empty(len(y))
    for block in pooled:
        result[block['indices']] = block['sum']/len(block['indices'])
    return result


def decode(x):
    return x/12.92 if x <= 0.04045 else ((x+0.055)/1.055)**2.4


def predictors(row, scratch, ladder, cache):
    key = (row['backgroundArray'], row['regionArray'], row['scale'])
    if key in cache:
        return cache[key]
    shape = (row['height'], row['width'])
    field = np.fromfile(scratch/row['backgroundArray'], dtype='<f8').reshape(shape)
    distance = np.fromfile(scratch/row['regionArray'], dtype='<f8').reshape(shape)
    body = distance <= -6*row['scale']
    silhouette = distance <= 0
    xs = {'source': float(field.mean()), 'body': float(field[body].mean()),
          'silhouette': float(field[silhouette].mean())}
    scales = {}
    for fraction in ladder:
        radius = fraction*row['span']
        suffix = f'{fraction:g}'
        xs['dilated/'+suffix] = float(field[distance <= radius*row['scale']].mean())
        blurred = field if radius == 0 else gaussian_filter(
            field, radius*row['scale'], mode='nearest', truncate=4.0)
        xs['gaussian/'+suffix] = float(blurred[body].mean())
        scales[suffix] = radius
    spec = row['backgroundSpec']
    value = dict(encoded=xs, decodedOnce={k:decode(v) for k,v in xs.items()},
        scaleCssPx=scales, sourceContrastSd=float(field.std()),
        bodyContrastSd=float(field[body].std()), silhouetteContrastSd=float(field[silhouette].std()),
        pitchCssPx=spec.get('cell', spec.get('rowHeight')),
        bodyMinusSource=xs['body']-xs['source'], silhouetteMinusSource=xs['silhouette']-xs['source'])
    cache[key] = value
    return value


def fits(rows):
    """Required full-population rows plus predeclared confound sensitivities."""
    groups = defaultdict(list)
    for r in rows:
        base = (r['scheme'], r['pose'], r['thickness'])
        groups[('all',)+base].append(r)
        groups[('policy:'+r['policy'],)+base].append(r)
        clean = not set(r['flags']).intersection({'tinted','interaction','composite'})
        if clean and r['policy'] == 'standard':
            groups[('clean-standard',)+base].append(r)
            groups[('clean-standard-'+r['bed'],)+base].append(r)
    tables, models = [], {}
    for group, cells in sorted(groups.items()):
        y = np.array([r['nativeBodyY'] for r in cells])
        group_key = '/'.join(group)
        group_models = {}
        for name in cells[0]['predictors']['encoded']:
            x = np.array([r['predictors']['encoded'][name] for r in cells])
            fitted = isotonic(x, y)
            residual = y-fitted
            model = dict(predictor=name, rms=float(np.sqrt(np.mean(residual**2))),
                uniqueX=len(set(np.round(x,12))), n=len(cells),
                cells=[dict(id=r['id'], x=float(xx), nativeBodyY=float(yy),
                    fittedY=float(ff), residualY=float(rr))
                    for r,xx,yy,ff,rr in zip(cells,x,y,fitted,residual)])
            group_models[name] = model
            tables.append(dict(subset=group[0], scheme=group[1], pose=group[2], thickness=group[3],
                predictor=name, n=len(cells), uniqueX=model['uniqueX'], rms=model['rms']))
        # Zero-scale variants are literally the same predictor and not runner-ups.
        eligible = [m for name,m in group_models.items() if name not in ('dilated/0','gaussian/0')]
        ranking = sorted(eligible, key=lambda m:(m['rms'], m['predictor']))
        models[group_key] = dict(ranking=[dict(predictor=m['predictor'], rms=m['rms']) for m in ranking],
            best=ranking[0]['predictor'], runnerUp=ranking[1]['predictor'],
            margin=ranking[1]['rms']-ranking[0]['rms'], models=group_models)
    return tables, models


def uniform_checks(models, denied):
    """Use recorded ordinates only. Uniform points are never in a selection fit.

    With no selected map these are labelled diagnostics on the row winner, not
    checks that silently promote that winner. A monotone envelope avoids assuming
    an interpolating response curve across the sparse structured support.
    """
    result = []
    source = ROOT/'packages/calibration/results/2026-09-14-w27c-g1d/native-response.json'
    for row in load(source)['rows']:
        if row['background'] not in ['dark-solid','mid-dark-solid','mid-light-solid','light-solid']:
            continue
        if row['scene'].rsplit('__',1)[0] in denied:
            continue
        thickness = 'thin' if row['sizeThickness'] < 1 else 'thick'
        key = f"policy:{row['a11y']}/{row['scheme']}/inactive/{thickness}"
        if key not in models:
            continue
        winner = models[key]['best']
        fit = models[key]['models'][winner]['cells']
        x = row['encodedBackdropMean']
        lower = max([c['fittedY'] for c in fit if c['x'] <= x]+[0.0])
        upper = min([c['fittedY'] for c in fit if c['x'] >= x]+[1.0])
        y = row['nativeBodyY']
        result.append(dict(profile=row['profile'], scene=row['scene'], x=x, nativeBodyY=y,
            group=key, diagnosticPredictor=winner, monotoneLower=lower, monotoneUpper=upper,
            outsideEnvelopeY=max(lower-y,y-upper,0),
            outsideStructuredXRange=x<min(c['x'] for c in fit) or x>max(c['x'] for c in fit)))
    return result


def residual_read(rows, models):
    by_id = {r['id']:r for r in rows}
    cells, pairs = [], []
    for key,g in models.items():
        if not key.startswith('clean-standard/'):
            continue
        for c in g['models'][g['best']]['cells']:
            r = by_id[c['id']]
            cells.append(dict(group=key, diagnosticPredictor=g['best'], **c,
                background=r['backgroundName'], component=r['component'], pitchCssPx=r['predictors']['pitchCssPx'],
                contrastSd=r['predictors']['bodyContrastSd'], profile=r['profile'], bed=r['bed']))
        members = [c for c in cells if c['group']==key]
        for i,a in enumerate(members):
            for b in members[i+1:]:
                if (a['profile'],a['component'],a['bed']) != (b['profile'],b['component'],b['bed']):
                    continue
                if a['background']==b['background']:
                    continue
                if abs(a['x']-b['x']) <= 0.001:
                    pairs.append(dict(group=key, a=a['id'], b=b['id'], deltaX=b['x']-a['x'],
                        deltaContrast=b['contrastSd']-a['contrastSd'], deltaPitch=(b['pitchCssPx']-a['pitchCssPx'])
                            if a['pitchCssPx'] is not None and b['pitchCssPx'] is not None else None,
                        deltaNativeY=b['nativeBodyY']-a['nativeBodyY'],
                        deltaResidualY=b['residualY']-a['residualY']))
    return dict(status='Diagnostic only: no predictor selected; no H4 term identified by residual fitting',
                cells=cells, matchedRegionMeanTolerance=0.001, matchedPairs=pairs)


def main():
    # Refuse changed enumeration even if someone committed a manually edited list.
    from declare import declaration
    population = load(HERE/'population.json')
    if population != declaration():
        raise ValueError('Current manifests do not reproduce the committed population')
    with tempfile.TemporaryDirectory(prefix='vitrea-w28-g0-') as directory:
        scratch = Path(directory)
        subprocess.run(['pnpm','--filter','@vitrea/calibration','--fail-if-no-match','exec','tsx',
            str(HERE/'extract.ts'),'--scratch',str(scratch)], cwd=ROOT, check=True)
        raw = load(scratch/'extracted.json')
        rows, cache = [], {}
        for row in raw['rows']:
            p = predictors(row,scratch,population['statistics']['ladderFractions'],cache)
            if row['pose'] == 'inactive' and row['provenance'] == 'manifest-attested active':
                row['provenance'] = 'manifest-attested inactive (non-recovered probe)'
            rows.append({k:v for k,v in row.items() if k not in ['backgroundArray','regionArray','backgroundSpec']} | {'predictors':p})
    tables, models = fits(rows)
    required = {k:v for k,v in models.items() if k.startswith('all/')}
    winners = {v['best'] for v in required.values()}
    selected = next(iter(winners)) if len(winners)==1 and all(v['margin']>NOISE for v in required.values()) else None
    verdict = 'selected' if selected is not None else 'not identifiable from this bed'
    denied = {s.rsplit('__',1)[0] for s in population['deniedInactiveIds']}
    uniforms = uniform_checks(models,denied)
    residuals = residual_read(rows,models)
    plurality = load(ROOT/'packages/calibration/results/2026-09-14-w27c-g1d/plurality.json')
    noise = dict(thresholdLinearY=NOISE,
        status='Charter decision bar, approximately one 8-bit code on the recovered single-run bed; not a re-estimated per-cell Y variance. Plurality JSON records state shares, not raw pixel spread.',
        source='2026-09-11-w27-26.5-run/provenance.json and 2026-09-14-w27c-g1d/plurality.json; §5.143 §1 records minority differences <= one code for the new neutral anchors',
        passes=[{k:p[k] for k in ['pass','runs','cells','unanimousCells','agreementHistogram'] if k in p} for p in plurality['passes']])
    summary = dict(gate='W28 G0 / claims §5.144', verdict=verdict, selected=selected,
        count=len(rows), populationMetadataCorrection='The immutable declaration labels 32 non-recovered inactive rows as manifest-attested active. Their pose field was always inactive and selection membership is unchanged. Per-cell provenance corrects that label to manifest-attested inactive (non-recovered probe).', countsByPolicyPose=dict(Counter(r['policy']+'/'+r['pose'] for r in rows)),
        noise=noise, regionChecks=raw['regionChecks'],
        rowVerdicts={k:{kk:v[kk] for kk in ['best','runnerUp','margin','ranking']} for k,v in models.items()},
        activeInputDisplacement={name:dict(meanAbsolute=float(np.mean([abs(r['predictors']['encoded'][name]-r['predictors']['encoded']['source']) for r in rows if r['pose']=='active'])),
            maxAbsolute=float(max(abs(r['predictors']['encoded'][name]-r['predictors']['encoded']['source']) for r in rows if r['pose']=='active')))
            for name in ['body','silhouette']},
        x8='No selected abscissa means no uniquely defined active-material counterfactual. Active native order and candidate input displacements are measured; no rendered active or inactive effect, CSS Jensen gap, new uniform/phase fixture, D target, or response constant was measured or changed.')
    save('per-cell.json',dict(rows=rows))
    save('isotonic.json',models)
    save('summary.json',summary)
    save('uniform-check.json',dict(status='No selected map; these are labelled winner diagnostics, not selection points',rows=uniforms))
    save('residuals.json',residuals)
    save('inputs.json',dict(populationCommit='8ad63af',populationSha256=hashlib.sha256((HERE/'population.json').read_bytes()).hexdigest(),sha256=raw['hashes']))
    with (HERE/'predictor-table.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(tables[0]));writer.writeheader();writer.writerows(tables)
    print(verdict)
    for key,g in models.items():
        if key.startswith(('all/','clean-standard/')):
            print(key, g['ranking'][:2], 'margin',g['margin'])

if __name__ == '__main__':
    main()
