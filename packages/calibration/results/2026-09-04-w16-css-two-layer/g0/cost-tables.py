"""W16 G0 §7 — the cost tables, built from `cost.mjs`'s JSON.

Three runs feed this: the first saturation sweep (`g0-cost-sweep.json`), the knee
refinement plus the demo pages (`g0-cost-knee-and-demo.json`), and the linear-light
addendum (`g0-cost-linear-light.json`). A cell that appears in more than one run is
reported from the run that measured it; nothing is averaged, because each cell is a
single run and averaging two would hide the jitter the findings name.
"""
import json
import os
import sys

OUT = os.path.dirname(os.path.abspath(__file__))
P = f'{OUT}/parts'
COUNTS = (20, 24, 28, 32, 36, 40, 48, 80, 160, 320)


def load(name):
    path = f'{P}/{name}'
    return json.load(open(path)) if os.path.exists(path) else []


def index(rows):
    out = {}
    for r in rows:
        if 'form' in r and r.get('w', 160) == 160 and r.get('n') in COUNTS:
            out[(r['form'], r['n'], r['dpr'])] = r
    return out


def main():
    syn = {}
    for name in ('g0-cost-sweep.json', 'g0-cost-knee-and-demo.json', 'g0-cost-linear-light.json'):
        syn.update(index(load(name)))
    forms = sys.argv[1:] or ['one', 'two', 'two-mask']
    head = ' | '.join(f'{f} @{d}x' for d in (1, 2) for f in forms)
    print(f'| surfaces | filtered device px per frame @1x / @2x | {head} |')
    print('| --- ' * (2 + 2 * len(forms)) + '|')
    for n in COUNTS:
        area = n * 160 * 96
        cells = []
        for dpr in (1, 2):
            for f in forms:
                r = syn.get((f, n, dpr))
                cells.append(f'{r["medianMs"]:.1f}' if r else '—')
        print(f'| {n} | {area / 1e6:.2f} M / {4 * area / 1e6:.2f} M | ' + ' | '.join(cells) + ' |')

    demo = [r for r in load('g0-cost-knee-and-demo.json') + load('g0-cost-linear-light.json')
            if 'url' in r]
    if demo:
        print()
        print('| page | filtered elements | largest | ' +
              ' | '.join(sorted({r['label'].split(' ', 2)[2] for r in demo})) + ' |')
        shapes = sorted({r['label'].split(' ', 2)[2] for r in demo})
        print('| --- ' * (3 + len(shapes)) + '|')
        for name in ('demo site', 'demo laws', 'demo playground'):
            for dpr in (1, 2):
                rows = {r['label'].split(' ', 2)[2]: r for r in demo
                        if r['label'].startswith(name) and r['dpr'] == dpr}
                if not rows:
                    continue
                any_row = next(iter(rows.values()))
                cells = [f'{rows[s]["medianMs"]:.1f} ms' if s in rows else '—' for s in shapes]
                print(f'| `{name}` @{dpr}x | {any_row["n"]} | '
                      f'{any_row["largest"][0]} × {any_row["largest"][1]} | ' + ' | '.join(cells) + ' |')


if __name__ == '__main__':
    main()
