"""W42 G0 instrument: gathers proof 1 and proof 3 of the step, patch, depth and lam readers into
proof1_readers_b.json/.txt and proof3_readers_b.json/.txt, with each reader's resolution row."""
import glob
import json

import numpy as np


def load(prefix):
    res = {}
    for f in sorted(glob.glob(f'{prefix}.*.json')):
        res[f.split('.')[1]] = json.load(open(f))
    return res


def q(v, n=3):
    return '-' if v is None or (isinstance(v, float) and not np.isfinite(v)) else f'{v:.{n}f}'


def p1_text(r):
    L = ['W42 G0 instrument, proof 1 (synthetic) for the step, patch, depth and lam readers',
         'Truths rendered through memo C\'s T, quantised +-0.5; bars from tolerances.json (declared first).', '']
    if 'patch' in r:
        L += ['PATCH AND ANNULUS READER (family C). sn/sw read (lam, w free, supports box/clamp and box/norm)',
              'truth free-sn: sigma_n flat in depth (gated: sn within 5 %, or the effective width sqrt((sn s)^2 +',
              'F^2) within 5 % where the floor dominates); truth LT: sigma_n depth-graded, the read is an effective',
              'width reported against the o-law at the patch depth; sw gated within 5 % for both.']
        for x in r['patch']:
            if 'group' in x and 'sn' in x:
                L.append(f"  {x['ep']:15s} {x['truth']:8s} {x['group']:12s} sn {q(x['sn'])} truth {q(x['sn_truth'])} "
                         f"(rel {q(x['sn_rel'])}; eff {q(x['eff_dev'], 2)}/{q(x['eff_dev_truth'], 2)} dev) "
                         f"{x['verdict_sn']:22s} sw {q(x['sw'], 2)}/{q(x['sw_truth'], 2)} (rel {q(x['sw_rel'])}) "
                         f"{x['verdict_sw']} lam {q(x['lam'])}/{q(x['lam_truth'], 2)} w {q(x['w'])} rms {q(x['rms'])}")
            elif 'tails' in x:
                L.append(f"  tail read ({x['ep']}, W-tails truth s2 {x['truth_tail']['s2']} a {x['truth_tail']['a']}): "
                         f"one Gaussian rms {q(x['one_gauss']['rms'])} sw {q(x['one_gauss']['sw'], 2)}; "
                         f"two-Gaussian rms {q(x['tails']['rms'])} s2 {x['tails']['s2']} a {x['tails']['a']} "
                         f"sw {q(x['tails']['sw'], 2)}")
        L.append('')
    if 'depth' in r:
        L += ['DEPTH-GRADED RADIUS READER. ratio sigma_n(d)/sigma_n(centre) against the o-law (LT active), 1 (LT',
              'receded, and the active free-sn truth: the no-grading control); bar 0.05.']
        for x in r['depth']:
            if x.get('verdict') == 'EXCLUDED':
                L.append(f"  {x['ep']:15s} {x['truth']:8s} {x['shape']:16s} {x['label']:24s} EXCLUDED: {x['reason']}")
                continue
            L.append(f"  {x['ep']:15s} {x['truth']:8s} {x['shape']:16s} {x['label']:24s} depth {q(x['depth'], 1)} "
                     f"sn {q(x.get('sn'))} ratio {q(x.get('ratio'))} expect {q(x['expect'])} {x['verdict']} "
                     f"[{x.get('band', '')}]")
        L.append('')
    if 'step' in r:
        L += ['STEP READER (family D, joint over the endpoint\'s D cells). support call by pooled rms (a call only',
              'where first and second differ by > 0.05 code, tolerances.json), sw on the true support within 5 %;',
              'the region ranking (max |median| misfit over the step populations) beside it.']
        for x in r['step']:
            L.append(f"  {x['ep']:15s} {x['truth']:9s} {x['mode']:5s} truth {x['truth_support']:12s} call "
                     f"{str(x['call']):12s} gap {q(x['call_gap'])} {x['verdict_support']} | sw@true "
                     f"{q(x['sw_true_support'], 2)}/{q(x['sw_truth'], 2)} {x['verdict_sw']} | region rank "
                     f"{x['region_ranking'][:2]} gap {q(x['region_gap'], 2)} | lam {q(x['lam'])} kn {q(x.get('kn'))}")
        L.append('')
    if 'lambda' in r:
        L += ['PER-CELL LAM AND HINGE-GAP READERS (LT truth at the truth k). identified = interval <= 0.4 wide and',
              'not at the grid bound; bar lam within 0.03 with the truth inside the interval; gap bins within 0.05.']
        by = {}
        for x in r['lambda']:
            by.setdefault(x['ep'], []).append(x)
        for ep, xs in by.items():
            idf = [x for x in xs if x.get('identified')]
            err = [abs(x['lam'] - x['lam_truth']) for x in idf]
            L.append(f"  {ep:15s} cells {len(xs)} identified {len(idf)} pass {sum(x['verdict'] == 'PASS' for x in xs)} "
                     f"max |err| {q(max(err) if err else None)} gap pass {sum(x['verdict_gap'] == 'PASS' for x in xs)}")
            for x in xs:
                if not x.get('identified'):
                    L.append(f"      not identified: {x['cell']} lam {q(x['lam'])} [{q(x['lo'], 2)}, {q(x['hi'], 2)}]"
                             + (f" ({x['note']})" if x.get('note') else ''))
        L.append('')
    if 'u1' in r:
        L += ['U1 DIAGNOSTIC. Rival truths on the receded cells (and dark active capsule), read by LT\'s pooled k',
              'and its per-cell lam and hinge-gap readers, as memo E read Apple. drift = lam(p64) - lam(p16), * =',
              'intervals disjoint; gap spread = max - min of the per-bin lam within one cell.']
        for x in r['u1']:
            d = ' '.join(f"{k}:{v['d']:+.3f}{'*' if v['disjoint'] else ''}" for k, v in x['drift'].items() if v)
            sp = [c['gap_spread'] for c in x['cells'] if c.get('gap_spread') is not None]
            L.append(f"  {x['ep']:15s} {x['truth']:9s} LT k {q(x['k_fit'])} pooled {q(x['pooled'])} max {q(x['max_cell'])}"
                     f" | {d} | gap spread max {q(max(sp) if sp else None)}")
            L.append('      ' + ' '.join(f"{c['cell'].split('|')[1]}:{q(c['lam'], 2)}" for c in x['cells']))
    return '\n'.join(L) + '\n'


def p3_text(r):
    L = ['W42 G0 instrument, proof 3 (vitrea\'s own web captures, linear reading) for the step, patch, depth',
         'and lam readers. Truth: the code map (canon.kernels()); vitrea draws a two-sided linear body, no knee.', '']
    if 'patch' in r:
        L += ['PATCH READER on impulse cells, lam FREE: lam within 0.12 of 0 (gated); no false footprint call (gated);',
              'sn and sw against the code for reference (the impulse reader\'s bars, 10 % and 25 %).']
        for x in r['patch']:
            L.append(f"  {x['cell']:42s} sn {q(x['sn'])}/{q(x['truth']['sn'])} ({x['ref_sn_10pct']}) sw {q(x['sw'], 2)}/"
                     f"{q(x['truth']['sw'], 2)} ({x['ref_sw_25pct']}) w {q(x['w'])}/k {q(x['truth']['share'])} "
                     f"lam {q(x['lam'])} {x['verdict_lam']} {x['ranking'][0]} {x['verdict_support']}")
        L.append('')
    if 'patch_given' in r:
        L += ['PATCH READER, lam GIVEN (0): sn and sw against the code (reference bars 10 % and 25 %).']
        for x in r['patch_given']:
            L.append(f"  {x['cell']:42s} sn {q(x['sn'])}/{q(x['truth']['sn'])} ({x['ref_sn_10pct']}) sw {q(x['sw'], 2)}/"
                     f"{q(x['truth']['sw'], 2)} ({x['ref_sw_25pct']}) w {q(x['w'])}/k {q(x['truth']['share'])} "
                     f"{x['ranking'][0]} {x['verdict_support']}")
        L.append('')
    if 'depth' in r:
        L += ['DEPTH READER (depth bins, lens band excluded): vitrea\'s narrow width is flat, ratio within 0.05 of 1.']
        for x in r['depth']:
            L.append(f"  {x['cell']:44s} {x['label']:6s} depth {q(x['depth'], 1)} sn {q(x['sn'])} (code "
                     f"{q(x['sn_truth'])}) ratio {q(x['ratio'])} {x['verdict']}")
        L.append('')
    if 'step' in r:
        L += ['STEP READER on checker-64 edges: no call against the canvas (vitrea\'s W is canvas-wide), lam within',
              '0.12 of 0 on the canvas support (gated); sw against the code for reference (25 %).']
        for x in r['step']:
            L.append(f"  {x['cell']:44s} call {str(x['call']):12s} gap {q(x['call_gap'])} {x['verdict_support']} "
                     f"sw@canvas {q(x['sw_canvas'], 2)}/{q(x['truth']['sw'], 2)} ({x['ref_sw_25pct']}) "
                     f"lam@canvas {q(x['lam_canvas'])} {x['verdict_lam']}")
        L.append('')
    if 'lambda' in r:
        L += ['LAM READERS, linear reading at the code\'s widths: lam within 0.12 of 0 per cell and per gap bin;',
              'the encoded reading (the known-space control) beside it.']
        for x in r['lambda']:
            gl = [g['lam'] for g in x['gaps'] if g['lam'] is not None]
            L.append(f"  {x['cell']:44s} lam {q(x['lam'])} [{q(x['lo'], 2)},{q(x['hi'], 2)}] {x['verdict']} gaps "
                     f"{[round(v, 2) for v in gl]} {x['verdict_gap']} | encoded lam {q(x['encoded']['lam'], 2)}")
    return '\n'.join(L) + '\n'


if __name__ == '__main__':
    for prefix, fn in (('proof1_readers_b', p1_text), ('proof3_readers_b', p3_text)):
        r = load(prefix)
        if not r:
            continue
        json.dump(r, open(f'{prefix}.json', 'w'), indent=1, default=float)
        open(f'{prefix}.txt', 'w').write(fn(r))


# ---------------------------------------------------------------- the resolution rows (for the parent's table)

def _mx(xs):
    xs = [x for x in xs if x is not None and np.isfinite(x)]
    return max(xs) if xs else None


def _verdict(v, tol):
    return 'N/A' if v is None else ('PASS' if v <= tol else 'FAIL')


def rows(p1, p3):
    R = []
    P = [x for x in p1.get('patch', []) if 'sn_rel' in x]
    flat = [x for x in P if x['truth'] == 'free-sn']
    for ep_set, band in ((('light-rest', 'dark-rest'), 'outside (S8/S32 md); across (impulse lattices)'),
                         (('light-inactive', 'dark-inactive'), 'receded (no band)')):
        f = [x for x in flat if x['ep'] in ep_set]
        sn = _mx([x['sn_rel'] if not x['floor_dominated'] else abs(x['eff_dev'] - x['eff_dev_truth']) /
                  x['eff_dev_truth'] for x in f])
        sw = _mx([x['sw_rel'] for x in P if x['ep'] in ep_set])
        fails = [f"{x['ep']} {x['truth']} {x['group']}" for x in f if x['verdict_sn'] != 'PASS']
        R.append(dict(reader='patch and annulus (family C)', quantity='sigma_n (flat-in-depth truth)',
                      endpoints=list(ep_set), band=band,
                      synthetic=dict(resolution=None if sn is None else f'{100 * sn:.1f} %', tolerance='5 %',
                                     verdict='PASS' if not fails else 'FAIL'),
                      vitrea=None, notes='misses: ' + '; '.join(fails) if fails else ''))
        R.append(dict(reader='patch and annulus (family C)', quantity='sigma_w', endpoints=list(ep_set), band=band,
                      synthetic=dict(resolution=None if sw is None else f'{100 * sw:.1f} %', tolerance='5 %',
                                     verdict=_verdict(sw, 0.05)),
                      vitrea=None, notes=''))
    lt = [x for x in P if x['truth'] == 'LT']
    if lt:
        R.append(dict(reader='patch and annulus (family C)', quantity='sigma_n (LT, depth-graded: effective width)',
                      endpoints=sorted({x['ep'] for x in lt}), band='as above',
                      synthetic=dict(resolution=f"{100 * _mx([x['sn_rel'] for x in lt]):.1f} % from the o-law at the "
                                     'patch depth', tolerance='reported, not gated', verdict='N/A'),
                      vitrea=None, notes='the reader assumes a flat width over its window'))
    v = p3.get('patch', [])
    if v:
        lam = _mx([abs(x['lam']) for x in v])
        R.append(dict(reader='patch and annulus (family C)', quantity='lam, free (linear reading)',
                      endpoints=['all four'], band='vitrea lens band excluded', synthetic=None,
                      vitrea=dict(resolution=f'|lam| up to {lam:.1f}', tolerance='0.12', verdict=_verdict(lam, 0.12)),
                      notes='NOT IDENTIFIED on real pixels: on a sparse impulse lattice the hinge column is nearly '
                            'collinear with C and W, so kernel misfit lands in lam. The protocol reads widths with lam '
                            'given (row below) and takes lam from the per-cell lam reader'))
    g = p3.get('patch_given', [])
    if g:
        ok = [x for x in g if x['narrow_share'] >= 0.2 and 0 <= x['w'] <= 1 and abs(x['sn'] - x['sw']) > 0.5
              and x.get('sn_iv') and x['sn_iv'][1] - x['sn_iv'][0] <= 0.6 * x['sn']]
        sn = _mx([x['sn_rel'] for x in ok])
        R.append(dict(reader='patch and annulus (family C)', quantity='sigma_n with lam given (linear reading)',
                      endpoints=['all four'], band='vitrea lens band excluded', synthetic=None,
                      vitrea=dict(resolution=f'{100 * sn:.0f} % max over {len(ok)}/{len(g)} cells with a narrow '
                                  'share >= 0.2', tolerance='10 % (the impulse reader\'s bar, reference)',
                                  verdict=_verdict(sn, 0.10)),
                      notes='the other cells carry no narrow component to read (vitrea\'s 2x deep bodies are ~all '
                            f"deep kernel) or collapse to sn = sw; no false footprint call on "
                            f"{sum(x['verdict_support'] == 'PASS' for x in g)}/{len(g)}"))
    D = [x for x in p1.get('depth', []) if x.get('verdict') not in (None, 'EXCLUDED')]
    for nm, sel, band in (
            ('ratio vs o-law, active LT (patch form)', lambda x: x['truth'] == 'LT' and x['ep'].endswith('rest')
             and 'bins' not in x['shape'], 'outside / across (per row)'),
            ('flat control (receded LT; active free-sn)', lambda x: 'bins' not in x['shape'] and
             (x['ep'].endswith('inactive') or x['truth'] == 'free-sn'), 'per row'),
            ('ratio, depth-bin form on bp-p1-c32-rrect-lg', lambda x: 'bins' in x['shape'], 'outside (declared mask)')):
        xs = [x for x in D if sel(x)]
        for sch in ('light', 'dark'):
            ys = [x for x in xs if x['ep'].startswith(sch) and x.get('ratio') is not None]
            if not ys:
                continue
            err = _mx([abs(x['ratio'] - x['expect']) for x in ys])
            fails = [f"{x['ep']} {x['label']} ({x.get('band', '')}) {x['ratio']:.3f} vs {x['expect']:.3f}"
                     for x in ys if x['verdict'] != 'PASS']
            R.append(dict(reader='depth-graded radius', quantity=nm, endpoints=sorted({x['ep'] for x in ys}),
                          band=band, synthetic=dict(resolution=f'max |ratio - expected| {err:.3f}', tolerance='0.05',
                                                    verdict='PASS' if not fails else 'FAIL'),
                          vitrea=None, notes='misses: ' + '; '.join(fails) if fails else ''))
    v = p3.get('depth', [])
    if v:
        idf = [x for x in v if x.get('identified') and 1 - x['w'] >= 0.2]
        err = _mx([abs(x['ratio'] - 1) for x in idf])
        R.append(dict(reader='depth-graded radius', quantity='flat narrow width in depth (vitrea, bins, lam given)',
                      endpoints=['all four'], band='vitrea lens band excluded', synthetic=None,
                      vitrea=dict(resolution=None if err is None else f'max |ratio - 1| {err:.3f} on {len(idf)}/{len(v)} '
                                  'bins', tolerance='0.05', verdict=_verdict(err, 0.05)),
                      notes='identified = sigma_n interval <= 0.6 sigma_n and narrow share >= 0.2: only vitrea\'s 1x '
                            'bodies qualify; the per-bin sigma_n interval is +-20-30 %, which bounds the ratio\'s own '
                            'resolution on real pixels'))
    S = p1.get('step', [])
    if S:
        sw = _mx([abs(x['sw_true_support'] - x['sw_truth']) / x['sw_truth'] for x in S])
        calls = [x for x in S if x['call'] is not None]
        R.append(dict(reader='step (family D)', quantity='sigma_w on the true support', endpoints=sorted({x['ep'] for x in S}),
                      band='outside (declared mask; active out-steps excluded)',
                      synthetic=dict(resolution=f'{100 * sw:.2f} %', tolerance='5 %', verdict=_verdict(sw, 0.05)),
                      vitrea=None, notes=''))
        R.append(dict(reader='step (family D)', quantity='support / edge-mode call (pooled rms margin 0.05)',
                      endpoints=sorted({x['ep'] for x in S}), band='as above',
                      synthetic=dict(resolution='; '.join(f"{x['ep']} {x['truth']}: {x['call'] or 'no call'} "
                                                          f"(gap {x['call_gap']:.3f}; region gap {x['region_gap']:.2f})"
                                                          for x in S if x['mode'] == 'given'),
                                     tolerance='the true support first wherever supports differ by > 0.05',
                                     verdict='PASS' if all(x['verdict_support'] == 'PASS' for x in S) else 'FAIL'),
                      vitrea=None,
                      notes='canvas against footprint is called in the receded pose; box-normalised, box-clamp and '
                            'the rounded shape (+mu) differ by < 0.05 code pooled and < 0.5 code on every region: '
                            'NON-IDENTIFIABLE on family D as declared'))
    v = p3.get('step', [])
    if v:
        lam = _mx([abs(x['lam_canvas']) for x in v])
        miss = [f"{x['cell']} {x['lam_canvas']:+.3f} (w {x['w']:.2f})" for x in v if abs(x['lam_canvas']) > 0.12]
        R.append(dict(reader='step (family D)', quantity='lam on the canvas support; no false footprint call',
                      endpoints=['all four'], band='vitrea lens band excluded', synthetic=None,
                      vitrea=dict(resolution=f'|lam| <= {lam:.3f}; false calls '
                                  f"{sum(x['verdict_support'] != 'PASS' for x in v)}/{len(v)}", tolerance='0.12; none',
                                  verdict='PASS' if not miss and all(x['verdict_support'] == 'PASS' for x in v)
                                  else 'FAIL'),
                      notes=('lam misses: ' + '; '.join(miss) + ' (2x rrect-lg: vitrea draws no narrow share there, '
                             'lam = a2/a1 with a1 ~ 0). ' if miss else '') +
                            f"sw within 25 % of the code on {sum(x['ref_sw_25pct'] == 'within' for x in v)}/{len(v)} "
                            '(1x reads 16-42 pt against 14.4: the platykurtic L4 and the share ramp)'))
    Lm = p1.get('lambda', [])
    for sch in ('light', 'dark'):
        xs = [x for x in Lm if x['ep'].startswith(sch)]
        if not xs:
            continue
        idf = [x for x in xs if x.get('identified')]
        err = _mx([abs(x['lam'] - x['lam_truth']) for x in idf])
        ge = _mx([abs(g['lam'] - x['lam_truth']) for x in xs for g in x['gaps']
                  if g['lam'] is not None and g['hi'] - g['lo'] <= 0.4])
        R.append(dict(reader='per-cell lam (memo E)', quantity='lam', endpoints=sorted({x['ep'] for x in xs}),
                      band='outside (declared mask)',
                      synthetic=dict(resolution=None if err is None else f'max |err| {err:.3f} on {len(idf)}/{len(xs)} '
                                     'identified cells', tolerance='0.03, truth inside the interval',
                                     verdict='PASS' if all(x['verdict'] == 'PASS' for x in idf) else 'FAIL'),
                      vitrea=None,
                      notes='not identified: ' + ', '.join(x['cell'].split('|')[1] + f" ({x['ep']})"
                                                             for x in xs if not x.get('identified'))))
        R.append(dict(reader='hinge-gap (memo E)', quantity='lam per gap bin', endpoints=sorted({x['ep'] for x in xs}),
                      band='outside (declared mask)',
                      synthetic=dict(resolution=None if ge is None else f'max |err| {ge:.3f}', tolerance='0.05',
                                     verdict=_verdict(ge, 0.05)), vitrea=None, notes='bins of >= 200 px whose interval '
                      'is <= 0.4 wide'))
    v = p3.get('lambda', [])
    if v:
        idf = [x for x in v if x['hi'] - x['lo'] <= 0.4 and -0.5 < x['lam'] < 1.6]
        lam = _mx([abs(x['lam']) for x in idf])
        R.append(dict(reader='per-cell lam (linear reading)', quantity='lam', endpoints=['all four'],
                      band='vitrea lens band excluded', synthetic=None,
                      vitrea=dict(resolution=f'|lam| <= {lam:.3f} on {len(idf)}/{len(v)} identified cells',
                                  tolerance='0.12', verdict=_verdict(lam, 0.12)),
                      notes='a cell identifies lam when its interval is <= 0.4 wide and off the grid bound; the '
                            'rest carry almost no narrow share (vitrea\'s 2x deep bodies are ~all deep kernel) or '
                            'too fine a pitch for W. Known-space control: the ENCODED reading returns lam ' +
                            f"{min(x['encoded']['lam'] for x in v):.2f} to {max(x['encoded']['lam'] for x in v):.2f}"))
        for thr in (0.0, 0.5):
            cs = [x for x in v if 1 - x['w_free'] >= thr]
            bins = [g for x in cs for g in x['gaps'] if g['lam'] is not None and g['hi'] - g['lo'] <= 0.4]
            gl = _mx([abs(g['lam']) for g in bins])
            R.append(dict(reader='hinge-gap (linear reading)', quantity='lam per gap bin' +
                          (f' (cells whose narrow share 1 - w >= {thr})' if thr else ' (every cell)'),
                          endpoints=['all four'], band='vitrea lens band excluded', synthetic=None,
                          vitrea=dict(resolution=f'|lam| <= {gl:.3f} over {len(bins)} bins', tolerance='0.12',
                                      verdict=_verdict(gl, 0.12)),
                          notes='vitrea draws no knee: per-bin lam is the reader manufacturing a hinge from the '
                                'misfit of Gaussian C and W to vitrea\'s chain kernels and depth-graded share'))
    return R


if __name__ == '__main__':
    p1, p3 = load('proof1_readers_b'), load('proof3_readers_b')
    json.dump(rows(p1, p3), open('resolution_rows_b.json', 'w'), indent=1, default=float)
