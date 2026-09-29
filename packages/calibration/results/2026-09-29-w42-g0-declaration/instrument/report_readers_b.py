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
    out = '\n'.join(L) + '\n'
    rw = {k[:-2]: v for k, v in r.items() if k.endswith('_w')}
    if rw:
        out += ('\n==== KERNEL w RE-RUN (the parent\'s ruling 3): the ACTIVE endpoints of the W readers on '
                'bed.cells(kernel=\'w\'), d_in 53.6 pt ====\n\n') + p1_text(rw).split('\n', 3)[-1]
    return out


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
    if 'replica' in r:
        rep = r['replica']
        L += ['RE-PROOF AGAINST THE FLOAT64 REPLICA (the parent\'s ruling 1; tolerances.json "proof3_vitrea",',
              f"b223600a): reading(capture) against reading(replica) on one mask, at the proof-1 bars. Replica fast "
              f"path vs original: max |difference| {rep['equivalence']:.1e}.",
              'Identifiability flags (the same call on both images): patch sn and depth bins, the profile '
              'interval strictly inside its scan and 0 <= w <= 0.9 (patch sn also != sw); patch sw, the interval '
              'inside its scan and 0.1 <= w <= 1; step sw, the interval inside its '
              'scan; step lam, 0 <= w <= 0.9; per-cell lam, interval <= 0.4 wide and off the grid bound; hinge-gap '
              'bin, interval <= 0.4 wide.']
        for x in rep['rows']:
            a, b = x['cap'], x['rep']
            if x['reader'] == 'patch':
                s_ = (f"sn {q(a['sn'])}/{q(b['sn'])} {x['score_sn'][0]}; sw {q(a['sw'], 2)}/{q(b['sw'], 2)} "
                      f"{x['score_sw'][0]}")
            elif x['reader'] == 'step':
                s_ = (f"sw {q(a['sw'], 2)}/{q(b['sw'], 2)} {x['score_sw'][0]}; call {a['call']}/{b['call']} "
                      f"{x['score_call'][0]}; lam {q(a['lam'])}/{q(b['lam'])} {x['score_lam'][0]}")
            elif x['reader'] == 'depth':
                s_ = ' '.join(f"{lb} {v[0]}" for lb, v in x['scores'].items())
            else:
                s_ = (f"lam {q(a['cell']['lam'])}/{q(b['cell']['lam'])} {x['score_lam'][0]}; gap bins "
                      + ', '.join(f"{g[0]}: {g[1]}" for g in x['score_gaps']))
            L.append(f"  {x['reader']:6s} {x['cell']:46s} {s_}")
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


# ---------------------------------------------------------------- rows v2 (the parent's rulings 1-3)
BAND_N = 'outside: active d_in = 20 + 16.8 t pt (band + 2 sigma_n,ref; kernel n)'
BAND_W = 'outside: active d_in = 53.6 pt (band + 2 sigma_w,ref; kernel w), rrect-ml and rrect-lg only'


def _rep(p3, reader):
    return [r for r in p3.get('replica', {}).get('rows', []) if r['reader'] == reader]


def _tally(scores):
    """[(status, value)] -> (verdict, resolution string)."""
    st = [x[0] for x in scores]
    npass = sum(x == 'PASS' for x in st)
    nrep = sum(x.startswith('reported') for x in st)
    nmiss = len(st) - npass - nrep
    vals = [x[1] for x in scores if x[1] is not None]
    worst = max(vals) if vals else None
    verdict = 'N/A' if npass + nmiss == 0 else ('PASS' if nmiss == 0 else 'FAIL')
    return verdict, worst, f'{npass} pass / {nmiss} miss / {nrep} non-identifiable on both'


def _sup(old, reader, quantity):
    for r in old:
        if r['reader'] == reader and r['quantity'] == quantity and r.get('vitrea'):
            return dict(r['vitrea'], basis='against the code\'s sigma_RMS (bars superseded 2026-09-29)')
    return None


def rows_v2(p1, p3):
    old = rows(p1, p3)
    R = []

    def add(reader, quantity, gated, band, synthetic, vitrea, superseded, notes=''):
        R.append(dict(reader=reader, quantity=quantity, gated=gated, band=band, synthetic=synthetic,
                      vitrea=vitrea, vitrea_superseded=superseded, notes=notes))

    # ---- patch
    P = [x for x in p1.get('patch', []) if 'sn_rel' in x]
    Pw = [x for x in p1.get('patch_w', []) if 'sn_rel' in x]
    rp = _rep(p3, 'patch')
    for sel, band in ((('light-rest', 'dark-rest'), BAND_N + '; S8/S32 md outside, impulse lattices across'),
                      (('light-inactive', 'dark-inactive'), 'receded (no band)')):
        f = [x for x in P if x['truth'] == 'free-sn' and x['ep'] in sel]
        sn = _mx([x['sn_rel'] if not x['floor_dominated'] else abs(x['eff_dev'] - x['eff_dev_truth']) /
                  x['eff_dev_truth'] for x in f])
        fails = [f"{x['ep']} {x['group']}" for x in f if x['verdict_sn'] != 'PASS']
        v, worst, tally = _tally([tuple(x['score_sn']) for x in rp if x['cell'].split('__')[2] ==
                                  ('rest' if sel[0].endswith('rest') else 'inactive')])
        add('patch and annulus (family C)', 'sigma_n (lam given in the protocol)', True, band,
            dict(resolution=None if sn is None else f'{100 * sn:.1f} % (flat-in-depth truth)', tolerance='5 %',
                 verdict='PASS' if not fails else 'FAIL'),
            dict(resolution=(f'max |cap - rep| {100 * worst:.1f} %; ' if worst is not None else '') + tally,
                 tolerance='5 %', verdict=v),
            _sup(old, 'patch and annulus (family C)', 'sigma_n with lam given (linear reading)'),
            'misses: ' + '; '.join(fails) if fails else '')
    for sel, src, band in ((('light-rest', 'dark-rest'), Pw, BAND_W), (('light-inactive', 'dark-inactive'), P,
                                                                        'receded (no band)')):
        xs = [x for x in src if x['ep'] in sel]
        sw = _mx([x['sw_rel'] for x in xs])
        fails = [f"{x['ep']} {x['truth']} {x['group']} {x['sw']:.2f}/{x['sw_truth']:.2f}" for x in xs
                 if x['verdict_sw'] != 'PASS']
        v, worst, tally = _tally([tuple(x['score_sw']) for x in rp if x['cell'].split('__')[2] ==
                                  ('rest' if sel[0].endswith('rest') else 'inactive')])
        add('patch and annulus (family C)', 'sigma_w (lam given in the protocol)', True, band,
            dict(resolution=None if sw is None else f'{100 * sw:.1f} %', tolerance='5 %',
                 verdict='PASS' if not fails else 'FAIL'),
            dict(resolution=(f'max |cap - rep| {100 * worst:.1f} %; ' if worst is not None else '') + tally,
                 tolerance='5 %', verdict=v),
            None, 'misses: ' + '; '.join(fails) if fails else '')
    add('patch and annulus (family C)', 'lam, free', False, 'as above',
        dict(resolution='recovered within 0.03 on every synthetic group', tolerance='reported', verdict='N/A'),
        None, _sup(old, 'patch and annulus (family C)', 'lam, free (linear reading)'),
        'not part of the protocol: on real pixels a sparse lattice leaves lam collinear with C and W; widths are '
        'read with lam given, lam comes from the per-cell lam reader')
    # ---- depth (descriptive)
    for r in old:
        if r['reader'] == 'depth-graded radius' and r.get('synthetic'):
            d = dict(r)
            d.update(gated=False, band=('per row: outside / across / receded; ' + BAND_N),
                     vitrea=None, vitrea_superseded=None)
            R.append(d)
    rd = _rep(p3, 'depth')
    v, worst, tally = _tally([tuple(sc) for x in rd for sc in x['scores'].values()])
    add('depth-graded radius', 'ratio sigma_n(d)/sigma_n(ref), vitrea bins', False, 'vitrea lens band excluded', None,
        dict(resolution=(f'max |cap - rep| {worst:.3f}; ' if worst is not None else '') + tally, tolerance='0.05',
             verdict=v),
        _sup(old, 'depth-graded radius', 'flat narrow width in depth (vitrea, bins, lam given)'))
    # ---- step
    S = [x for x in p1.get('step', []) if x['ep'].endswith('inactive')] + p1.get('step_w', [])
    rs = _rep(p3, 'step')
    if S:
        sw = _mx([abs(x['sw_true_support'] - x['sw_truth']) / x['sw_truth'] for x in S])
        v, worst, tally = _tally([tuple(x['score_sw']) for x in rs])
        add('step (family D)', 'sigma_w on the true support', True, BAND_W + ' (d-d0 on rrect-lg); receded no band',
            dict(resolution=f'{100 * sw:.2f} %', tolerance='5 %', verdict=_verdict(sw, 0.05)),
            dict(resolution=(f'max |cap - rep| {100 * worst:.1f} %; ' if worst is not None else '') + tally,
                 tolerance='5 %', verdict=v), None)
        v, _, tally = _tally([tuple(x['score_call']) for x in rs])
        add('step (family D)', 'support / edge-mode call', True, 'as above',
            dict(resolution='; '.join(f"{x['ep']} {x['truth']} {x['mode']}: {x['call'] or 'no call'} (gap "
                                      f"{x['call_gap']:.3f}; region gap {x['region_gap']:.2f})" for x in S),
                 tolerance='the true support first wherever supports differ by > 0.05',
                 verdict='PASS' if all(x['verdict_support'] == 'PASS' for x in S) else 'FAIL'),
            dict(resolution='identical call on capture and replica: ' + tally, tolerance='identical', verdict=v),
            None, 'canvas against footprint is called when receded; box-norm, box-clamp and the rounded shape (+mu) '
                  'are never separated (<= 0.008 code pooled, < 0.5 code per region): NON-IDENTIFIABLE on family D; '
                  'active: every support ties at 0.00 at both kernels')
        v, worst, tally = _tally([tuple(x['score_lam']) for x in rs])
        add('step (family D)', 'lam (free)', False, 'as above', None,
            dict(resolution=(f'max |cap - rep| {worst:.3f}; ' if worst is not None else '') + tally,
                 tolerance='0.03', verdict=v),
            _sup(old, 'step (family D)', 'lam on the canvas support; no false footprint call'))
    # ---- per-cell lam and hinge-gap
    Lm = [x for x in p1.get('lambda', []) if x['ep'].endswith('inactive')] + p1.get('lambda_w', [])
    rl = _rep(p3, 'lambda')
    for sch in ('light', 'dark'):
        xs = [x for x in Lm if x['ep'].startswith(sch)]
        idf = [x for x in xs if x.get('identified')]
        err = _mx([abs(x['lam'] - x['lam_truth']) for x in idf])
        ge = _mx([abs(g['lam'] - x['lam_truth']) for x in xs for g in x['gaps']
                  if g['lam'] is not None and g['hi'] - g['lo'] <= 0.4])
        v, worst, tally = _tally([tuple(x['score_lam']) for x in rl if x['cell'].startswith(sch)])
        add('per-cell lam (memo E)', 'lam', True, BAND_W + '; receded no band',
            dict(resolution=None if err is None else f'max |err| {err:.3f} on {len(idf)}/{len(xs)} identified cells',
                 tolerance='0.03, truth inside the interval',
                 verdict='PASS' if all(x['verdict'] == 'PASS' for x in idf) else 'FAIL'),
            dict(resolution=(f'max |cap - rep| {worst:.3f}; ' if worst is not None else '') + tally,
                 tolerance='0.03, each interval contains the other\'s point', verdict=v),
            _sup(old, 'per-cell lam (linear reading)', 'lam'),
            'not identified: ' + ', '.join(x['cell'].split('|')[1] + f" ({x['ep']})" for x in xs
                                           if not x.get('identified')))
        v, worst, tally = _tally([(g[1], g[2]) for x in rl if x['cell'].startswith(sch) for g in x['score_gaps']])
        add('hinge-gap (memo E)', 'lam per gap bin', False, BAND_W + '; receded no band',
            dict(resolution=None if ge is None else f'max |err| {ge:.3f}', tolerance='0.05', verdict=_verdict(ge, 0.05)),
            dict(resolution=(f'max |cap - rep| {worst:.3f}; ' if worst is not None else '') + tally,
                 tolerance='0.05', verdict=v),
            _sup(old, 'hinge-gap (linear reading)', 'lam per gap bin (every cell)'))
    add('U1 diagnostic (lam readers on rival truths)', 'drift lam(p64) - lam(p16), light receded', False,
        'receded (no band)', None, None, None,
        'LT 0.00; W-shape mu4 +-0.03 (NOT told apart from LT by the lam readers); W-tails +0.15..+0.18 (opposite '
        'sign to Apple); K2 sk12 -0.17..-0.18 on capsule AND md (Apple\'s sign); edge-swap -0.21 on the capsule '
        'only; W-canvas mixed, separated by misfit. At kernel w no active capsule remains, so the dark-active U1 '
        'rows (capsule, t = 0) have no cell.')
    add('depth-graded radius', 'does the bed resolve the grading law beyond the band?', False, BAND_N, None, None,
        None, 'light active: yes on rrect-lg only (80 vs 40 pt: 0.749 against the o-law 0.750; flat would be 1.0); '
              'rrect-md d24 is cut by the mask (0.811 vs 0.749); the 0.4t-at-1-pt end is never read (nothing '
              'readable shallower than 36.8 pt on lg, 25.6 on md). Dark active: no, under memo C\'s T (the 208 '
              'side untrusted). Bed questions: an md patch at ~34 pt; a dark level pair inside dark T\'s slope.')
    return R


if __name__ == '__main__':
    p1, p3 = load('proof1_readers_b'), load('proof3_readers_b')
    json.dump(rows_v2(p1, p3), open('resolution_rows_b.json', 'w'), indent=1, default=float)
