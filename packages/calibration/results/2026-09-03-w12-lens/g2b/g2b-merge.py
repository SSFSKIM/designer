"""Merge the G2b webgpu rows over the G2 landing's matrix, so the adopted-bound
enforcement (`test/adopted-thresholds.test.ts`) sees a whole bed: the CSS rows are the
G2 landing's, unchanged because the CSS tier has no lens."""
import json

T = '/Users/new/.claude/jobs/5c70e47f/tmp/w12'
g2 = json.load(open(f'{T}/matrix-g2.json'))
g2b = json.load(open(f'{T}/matrix-g2b.json'))


def key(c):
    return (c['key']['profileKey'], c['key']['web']['renderer'], c['key']['sceneId'])


newkeys = {key(c) for c in g2b['cells']}
merged = dict(g2b)
merged['cells'] = [c for c in g2['cells'] if key(c) not in newkeys] + g2b['cells']
json.dump(merged, open(f'{T}/matrix-g2b-merged.json', 'w'))
print('g2', len(g2['cells']), 'g2b', len(g2b['cells']),
      'merged', len(merged['cells']), 'unique keys', len({key(c) for c in merged['cells']}))
