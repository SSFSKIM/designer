"""W42 G2 step 2, part 1: native T per endpoint, stratum and channel from family A (declaration `nativeT`, the
native-T addendum 23e400bf..., reading-plan.md item 4).

Ordinates: each 2x family-A CALIBRATION cell's deep median per channel (regions.statistics, population `deep`, on
the cell's own deep mask). Strata by component: capsule 64 (t = 0), rrect-80 80 (dark), rrect-md 96, rrect-ml 128,
rrect-lg 160. Checks: the measured ordinates are monotone per stratum and channel (a decrease is a finding, never
repaired); the channels agree within the bar (neutral greys); the addendum's grid (bodyToneTableCodes, five rows
64/80/96/128/160 x eleven levels) reproduces every measured ordinate; the validation greys (2x rrect-64 at t = 0,
1x rrect-md 128 / 255) are predicted by T at their span, scored at max(1, bar).

    python3.12 -B native_t_read.py    -> native-t/ordinates.json, native-t/native-t.txt
"""
import json

import numpy as np

import common as C

OUT = C.HERE / 'native-t'


def level_of(c):
    return int(C.G.BACKGROUNDS[c.bg_spec['name']]['srgb'][0]) if 'name' in c.bg_spec else int(c.bg_spec['srgb'][0])


def main():
    OUT.mkdir(exist_ok=True)
    res = dict(schema='w42-g2-step2-native-t-1', rule='native-t-addendum.md (23e400bf...), implementation-design/'
               'native_t.py; ordinates = 2x family-A calibration deep medians per channel', endpoints={})
    lines = ['W42 G2 step 2: native T from family A (2x calibration deep medians, per channel)', '']
    for ep in C.EPS:
        scheme = ep.split('-')[0]
        cal = C.IB.cells(ep, 2, letters=('A',), roles=('calibration',), kernel='n', rgb=True)
        ords = {c: {} for c in 'RGB'}
        raw = []
        for cell in cal:
            img = C.observed(ep, 2, cell.bed_id)
            st = C.R.statistics(cell, img, C.R.populations(cell))
            L = int(cell.bg_spec['srgb'][0])
            s = C.STRATUM_OF[cell.comp_name]
            for i, ch in enumerate('RGB'):
                ords[ch].setdefault(s, {})[L] = st[f'deep|{ch}']
            raw.append(dict(cell=cell.bed_id, stratum=s, level=L, deep=[st[f'deep|{ch}'] for ch in 'RGB'],
                            pixels=int(cell.mask.sum())))
        ntc = C.NativeTC(ords, scheme)
        tables = {ch: ntc.table(ch).round(4).tolist() for ch in 'RGB'}
        # neutrality: largest channel spread over every ordinate
        spread = max(max(r['deep']) - min(r['deep']) for r in raw)
        # the grid reproduces every measured ordinate (per channel)
        worst_grid = 0.0
        for ch in 'RGB':
            tab = np.array(tables[ch])
            for s, row in ords[ch].items():
                for L, y in row.items():
                    g = NT_grid(tab, L, s)
                    worst_grid = max(worst_grid, abs(g - y))
        # validation greys: T at their span against Apple (every channel), 2x rrect-64 and 1x rrect-md
        val = []
        for scale in (2, 1):
            for cell in C.IB.cells(ep, scale, letters=('A',), roles=('validation',), kernel='n', rgb=True):
                img = C.observed(ep, scale, cell.bed_id)
                cell.kernel = 'n'
                st = C.R.statistics(cell, img, C.R.populations(cell))
                L = float(cell.bg_spec['srgb'][0])
                pred = [float(t(np.array([L]))[0]) for t in ntc.channels(cell.span)]
                errs = [pred[i] - st[f'deep|{ch}'] for i, ch in enumerate('RGB')]
                bound = [max(1.0, C.bar_of(cell, f'deep|{ch}')) for ch in 'RGB']
                cens = [not (5 < st[f'deep|{ch}'] < 250) for ch in 'RGB']
                ok = all((abs(e) <= b) if not cz else (pred[i] >= 250 if st[f'deep|{"RGB"[i]}'] >= 250 else pred[i] <= 5)
                         for i, (e, b, cz) in enumerate(zip(errs, bound, cens)))
                val.append(dict(cell=f'{scale}x|{cell.bed_id}', span=cell.span, level=L,
                                native=[st[f'deep|{ch}'] for ch in 'RGB'], predicted=pred,
                                error=[round(e, 3) for e in errs], censored=cens, passes=bool(ok)))
        res['endpoints'][ep] = dict(ordinates={ch: {str(s): {str(L): v for L, v in sorted(row.items())}
                                                     for s, row in sorted(ords[ch].items())} for ch in 'RGB'},
                                    raw=raw, nonMonotone=ntc.nonmonotone, channelSpreadMax=spread,
                                    gridReproducesMeasuredWithin=worst_grid,
                                    bodyToneTableCodes=dict(levels=list(C.NT.GRID_LEVELS),
                                                            spans=list(C.NT.GRID_SPANS), rows=tables),
                                    validation=val)
        lines.append(f'== {ep} ({C.EP_NAME[ep]})')
        for s in sorted(ords['R']):
            row = ords['R'][s]
            lines.append(f'  stratum {s:3d}: ' + '  '.join(
                f'{L}->{row[L]:.1f}' + ('' if abs(ords["G"][s][L] - row[L]) < 0.01 and abs(ords["B"][s][L] - row[L]) < 0.01
                                        else f'({ords["G"][s][L]:.1f},{ords["B"][s][L]:.1f})')
                for L in sorted(row)))
        lines.append(f'  monotone: {"YES" if not ntc.nonmonotone else "NO -- " + json.dumps(ntc.nonmonotone)}')
        lines.append(f'  largest channel spread over the ordinates: {spread:.2f} codes; grid reproduces measured '
                     f'within {worst_grid:.1e}')
        lines.append('  bodyToneTableCodes (R; rows 64/80/96/128/160 x levels ' + ','.join(map(str, C.NT.GRID_LEVELS)) + '):')
        for s, row in zip(C.NT.GRID_SPANS, tables['R']):
            lines.append(f'    {s:3d}: ' + ' '.join(f'{v:7.2f}' for v in row))
        for v in val:
            lines.append(f"  validation {v['cell']:28s} s {v['span']:.0f} L {v['level']:.0f}: native "
                         f"{v['native']} predicted {[round(x, 2) for x in v['predicted']]} error {v['error']} "
                         f"{'PASS' if v['passes'] else 'FAIL'}")
        lines.append('')
    C.save(OUT / 'ordinates.json', res)
    (OUT / 'native-t.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


def NT_grid(tab, L, s):
    return float(C.NT.grid_eval(tab, np.array([float(L)]), s)[0])


if __name__ == '__main__':
    main()
