"""The CSS tier's derived thick amplitude, before and after, on the X7 pair.

`before` is the wave's own confirmation matrix (the chosen constants with the
thick anchors inherited whole); `after` is this run's, with the lift folded into
the one alpha the tier can paint. The reference is the same fixture in both, so
its column is a check that the bed did not move under us.
"""
import sys, json
sys.path.insert(0, '../sweep')
from read import cells, pair, v

BEFORE = '../sweep/matrix-confirm.json'
AFTER = sys.argv[1]
TIER = 'dom'


def index(path):
    return {(c['key']['profileKey'], c['key']['sceneId']): c
            for c in cells(path) if c['tier'] == TIER}


def occ(cell, which):
    a, _ = pair(cell, which, 'below', '3-6')
    return None if a is None else 1 - a


def fmt(x, n=4):
    return '   —   ' if x is None else f'{x:.{n}f}'


before, after = index(BEFORE), index(AFTER)
print(f'{"profile":34s}{"scene":44s}{"set":12s}'
      f'{"ref 1-a":>9s}{"css was":>9s}{"css now":>9s}{"|now-ref|":>10s}{"|was-ref|":>10s}'
      f'{"ssimOut was":>13s}{"ssimOut now":>13s}{"ssimMean was":>14s}{"ssimMean now":>14s}')
for key in sorted(after):
    a = after[key]
    if a['fixtureSet'] == 'holdout':
        continue
    b = before.get(key)
    ref, now = occ(a, 'affineNative'), occ(a, 'affineWeb')
    was = occ(b, 'affineWeb') if b else None
    row = f'{key[0][:34]:34s}{key[1][:44]:44s}{a["fixtureSet"]:12s}'
    row += f'{fmt(ref):>9s}{fmt(was):>9s}{fmt(now):>9s}'
    row += f'{fmt(None if (ref is None or now is None) else abs(now - ref)):>10s}'
    row += f'{fmt(None if (ref is None or was is None) else abs(was - ref)):>10s}'
    for field in ('ssimOutside', 'ssimMean'):
        row += f'{fmt(v(b, "perceptual", field) if b else None):>13s}'
        row += f'{fmt(v(a, "perceptual", field)):>13s}'
    print(row)
