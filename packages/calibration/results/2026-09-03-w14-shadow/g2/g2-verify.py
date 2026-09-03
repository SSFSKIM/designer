#!/usr/bin/env python3
"""W14 G2: the rebuilt canonical matrix read against claims §5.66 §4 and §3's S6.

Three readings, all off `packages/calibration/results/matrix.json`:

  1. the twelve GPU-tier `ssimMean` rows on the six checkerboard cells at both
     scales, against §5.66 §4's declared numbers;
  2. the four `ssimOutside` rows §5.66 §4 also declares on the large cells;
  3. the CSS tier's band `3-6` below occlusion (`1 - a`) on `rrect-md` and
     `rrect-ml`, against the G1 css-fold run's readings.

A deviation is a finding, never something to adjust: every row prints its delta.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MATRIX = os.path.join(HERE, '..', '..', 'matrix.json')

DECLARED = {  # cell -> (1x, 2x), GPU tier ssimMean, claims §5.66 §4
    'rrect-sm': (0.9988, 0.9978),
    'capsule-button': (0.9852, 0.9836),
    'rrect-md': (0.9859, 0.9840),
    'rrect-ml': (0.9788, 0.9746),
    'glass-over-glass': (0.9807, 0.9762),
    'rrect-lg': (0.9687, 0.9680),
}
DECLARED_OUTSIDE = {  # the four large cells' ssimOutside, §5.66 §4
    'rrect-md': (0.9959, 0.9934),
    'rrect-ml': (0.9962, 0.9932),
    'glass-over-glass': (0.9950, 0.9900),
    'rrect-lg': (0.9935, 0.9885),
}
DECLARED_CSS = {  # dom tier, band 3-6 below `1 - a`, G1 css-fold
    ('rrect-md', 1): 0.1991,
    ('rrect-ml', 1): 0.2350,
    ('rrect-md', 2): 0.1986,
    ('rrect-ml', 2): 0.2344,
}
TOLERANCE = 0.0002


def load():
    cells = json.load(open(MATRIX))['cells']
    return {(c['tier'], c['key']['profileKey'], c['key']['sceneId']): c for c in cells}


def v(cell, axis, field):
    e = (cell.get(axis) or {}).get(field)
    return None if e is None else e['value']


def band(cell, which, direction='below', ring='3-6'):
    for s in (cell.get('shadow') or {}).get(which, []) or []:
        if s['direction'] == direction and s['ringLabel'] == ring:
            return s
    return None


def main():
    idx = load()
    worst = 0.0
    over = []

    def row(label, measured, declared):
        nonlocal worst
        if measured is None:
            print(f'{label:60s}  MISSING (declared {declared})')
            over.append(label)
            return
        d = measured - declared
        worst = max(worst, abs(d))
        flag = '  <-- OVER TOLERANCE' if abs(d) > TOLERANCE else ''
        if flag:
            over.append(label)
        print(f'{label:60s}  {measured:.5f}  declared {declared:.4f}  delta {d:+.5f}{flag}')

    print('=== §5.66 §4: GPU tier ssimMean, the six checkerboard cells, both scales ===')
    for comp, (a, b) in DECLARED.items():
        for scale, declared in ((1, a), (2, b)):
            profile = f'apple-macos-26.5-{scale}x-light-standard'
            cell = idx.get(('texture', profile, f'checkerboard__{comp}__rest'))
            row(f'{scale}x  checkerboard__{comp}  ssimMean',
                None if cell is None else v(cell, 'perceptual', 'ssimMean'), declared)

    print('\n=== §5.66 §4: toolbar-group (declared unchanged, 0.9642 / 0.9662) ===')
    for scale, declared in ((1, 0.9642), (2, 0.9662)):
        profile = f'apple-macos-26.5-{scale}x-light-standard'
        cell = idx.get(('texture', profile, 'checkerboard__toolbar-group__rest'))
        row(f'{scale}x  checkerboard__toolbar-group  ssimMean',
            None if cell is None else v(cell, 'perceptual', 'ssimMean'), declared)

    print('\n=== §5.66 §4: GPU tier ssimOutside, the four large cells ===')
    for comp, (a, b) in DECLARED_OUTSIDE.items():
        for scale, declared in ((1, a), (2, b)):
            profile = f'apple-macos-26.5-{scale}x-light-standard'
            cell = idx.get(('texture', profile, f'checkerboard__{comp}__rest'))
            row(f'{scale}x  checkerboard__{comp}  ssimOutside',
                None if cell is None else v(cell, 'perceptual', 'ssimOutside'), declared)

    print('\n=== §5.66 §3 S6: CSS tier band 3-6 below, 1 - a (G1 css-fold) ===')
    for (comp, scale), declared in DECLARED_CSS.items():
        profile = f'apple-macos-26.5-{scale}x-light-standard'
        cell = idx.get(('dom', profile, f'checkerboard__{comp}__rest'))
        s = None if cell is None else band(cell, 'affineWeb')
        measured = None if s is None or 'slopeALinear' not in s else 1 - s['slopeALinear']
        row(f'{scale}x  checkerboard__{comp}  css 1-a', measured, declared)

    print(f'\nworst |delta| = {worst:.5f}   tolerance {TOLERANCE}')
    print('rows over tolerance:', over if over else 'none')
    return 1 if over else 0


if __name__ == '__main__':
    sys.exit(main())
