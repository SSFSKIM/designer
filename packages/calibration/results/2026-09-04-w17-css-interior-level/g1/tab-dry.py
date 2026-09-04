#!/usr/bin/env python3
"""W17 G1: one markdown table per profile of the CSS tier's checkerboard, hc-text and photo rows —
the W16 bed beside one or more dry-run matrices. W16 G1's script with one column added: since W17
reads the level and the spread against the GPU TIER rather than against native (Decision Log 3),
the GPU tier's own reading is printed on every cell, so the table carries the comparison the stops
are taken over as well as the one against Apple.

Usage: python3 tab-dry.py <label>=<matrix> [<label>=<matrix> …]"""
import json, sys
MAIN = '/Users/new/Developer/GitHub/designer/packages/calibration/results/matrix.json'
def load(p):
    best = {}
    for c in json.load(open(p))['cells']:
        k = (c['key']['profileKey'], c['key']['web']['renderer'], c['key']['sceneId'])
        if k not in best or c['capturedAt'] > best[k]['capturedAt']: best[k] = c
    return best
runs = [('bed', load(MAIN))] + [(a.split('=', 1)[0], load(a.split('=', 1)[1])) for a in sys.argv[1:]]
def v(c, ax, k):
    if c is None: return None
    x = (c.get(ax) or {}).get(k); return None if x is None else x['value']
f = lambda x: '—' if x is None else f'{x:.4f}'
SCENES = ['checkerboard__rrect-sm__rest', 'checkerboard__capsule-button__rest', 'checkerboard__rrect-md__rest',
          'checkerboard__rrect-ml__rest', 'checkerboard__toolbar-group__rest', 'checkerboard__glass-over-glass__rest',
          'checkerboard__rrect-lg__rest', 'hc-text__rrect-md__rest', 'photo__rrect-md__rest', 'photo__rrect-ml__rest']
for prof in ('apple-macos-26.5-1x-light-standard', 'apple-macos-26.5-2x-light-standard'):
    print(f'\n**{prof}**, CSS tier — `ssimMean` · `ssimBand` · spread CSS / GPU / native · level CSS / GPU / native\n')
    print('| cell | ' + ' | '.join(l for l, _ in runs) + ' |'); print('| --- |' + ' --- |' * len(runs))
    for s in SCENES:
        cells = [r.get((prof, 'css', s)) for _, r in runs]
        if all(c is None for c in cells): continue
        def col(c, run):
            if c is None:
                return '(not read)'
            gpu = run.get((prof, 'webgpu', s))
            return (f'{f(v(c,"perceptual","ssimMean"))} · {f(v(c,"perceptual","ssimBand"))} · '
                    f'{f(v(c,"material","interiorStdDevWeb"))} / {f(v(gpu,"material","interiorStdDevWeb"))} / '
                    f'{f(v(c,"material","interiorStdDevNative"))} · '
                    f'{f(v(c,"material","interiorMeanWeb"))} / {f(v(gpu,"material","interiorMeanWeb"))} / '
                    f'{f(v(c,"material","interiorMeanNative"))}')
        print(f'| `{s}` | ' + ' | '.join(col(c, r) for c, (_, r) in zip(cells, runs)) + ' |')
