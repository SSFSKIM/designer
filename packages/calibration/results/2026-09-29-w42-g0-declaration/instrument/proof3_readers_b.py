"""W42 G0 instrument, proof 3 for the step, patch, depth and lam readers (charter clause 2; tolerances.json,
declared before this ran): on vitrea's own canonical web captures, where the code says what was drawn, the
readers must read it.

What the shipped body draws (memo B's code-map and replica, canon.kernels(), SHA-256 9c684eb9...): a
TWO-SIDED blend in LINEAR light, enc(A + B ((1 - k) Ksharp * b + k Kdeep * b)), with Ksharp the chain-L1
kernel (sigma_RMS 1.58 device px, flat in depth), Kdeep a canvas-wide pyramid level (sigma_RMS 9.3-20.8
device px by endpoint and scale, platykurtic), the share k graded by depth (a ramp of reach 80 CSS px at 1x,
50 at 2x) and no knee. So every reader here runs in the LINEAR reading (read_local): it must read lam = 0,
a narrow width that is flat in depth, and a W no footprint limits. The deep mask excludes vitrea's lens band
(lensExtent + 1 pt, memo B's replica core). Only calibration, validation and probe scenes are opened, and
only vitrea's web captures: no native pixel is read.

    python3.12 proof3_readers_b.py <section> [...]     sections: patch depth step lambda report
"""
import json
import sys

import numpy as np

import canon
import read_depth as RD
import read_lambda as RL
import read_patch as RP
import read_step as RS

OUT = 'proof3_readers_b'
SCHEMES, SCALES = ('light', 'dark'), (1, 2)
LENS = {'capsule-button': 14.7, 'rrect-sm': 10.7, 'rrect-md': 26.7, 'rrect-ml': 26.7, 'rrect-lg': 26.7}
RS.MU_GRID = (0.0, 16.0)


def ep_of(scheme, scene):
    return f"{scheme}-{scene.split('__')[2]}"


def truth(scheme, scene, scale):
    """The code's narrow and deep widths (CSS px) and the centre share for a canonical cell."""
    K = canon.kernels()
    comp = scene.split('__')[1]
    cep = canon.CODE_EP[ep_of(scheme, scene)]
    key_comp = canon.CODE_COMP.get(comp)
    borrowed = key_comp is None
    if borrowed:  # rrect-lg is not in the code map: its kernels are the endpoint's (ml's where they differ)
        key_comp = 'rrect-ml'
    r = K[(cep, scale, key_comp)]
    return dict(sn=r['body']['sx'] / scale, sw=0.5 * (r['heavy']['sx'] + r['heavy']['sy']) / scale,
                share=r['kScatterSpan'], deep=r['deep'], borrowed=borrowed, heavy_kurt=r['heavy']['kurt'])


def cell(scene, scheme, scale):
    """vitrea's deep mask: beyond vitrea's OWN lens band (lensExtent + 1 pt, memo B's replica core), which is
    what confounds its captures; Apple's refraction band (forward.band_d_in) does not apply to vitrea."""
    comp = scene.split('__')[1]
    return canon.web_cell(scene, scheme, scale, d_in=LENS[comp] + 1.0)


def available(scenes):
    out = []
    for sc in scenes:
        if canon.ROLE.get(sc) not in canon.ADMIT:
            continue
        for sch in SCHEMES:
            for s in SCALES:
                if canon.exists(sc, sch, s):
                    out.append((sc, sch, s))
    return out


def rel(a, b):
    return abs(a - b) / b if b else float('inf')


# ---------------------------------------------------------------- patch reader on the impulse cells
IMPULSE = [f'impulse__{c}__{p}' for c in ('capsule-button', 'rrect-sm', 'rrect-md', 'rrect-ml', 'rrect-lg')
           for p in ('rest', 'inactive')]


def patch_section():
    out = []
    for sc, sch, s in available(IMPULSE):
        c = cell(sc, sch, s)
        if c.mask.sum() < 200:
            continue
        t = truth(sch, sc, s)
        r = RP.read([(c, c.mask)], 'linear', supports=(('canvas', 'clamp', None), ('box', 'clamp', None),
                                                      ('box', 'norm', None)))
        b = r['best']
        canvas_rms = r['fits']['canvas/clamp']['rms']
        no_false_call = canvas_rms - b['rms'] <= 0.05
        rec = dict(cell=f'{sch} {s}x {sc}', truth=t, sn=b['sn'], sn_iv=b.get('sn_iv'), sw=b['sw'],
                   sw_iv=b.get('sw_iv'), lam=b['lam'], w=b['w'], rms=b['rms'], ranking=r['ranking'],
                   rms_by_support={k: v['rms'] for k, v in r['fits'].items()},
                   sn_rel=rel(b['sn'], t['sn']), sw_rel=rel(b['sw'], t['sw']),
                   verdict_lam='PASS' if abs(b['lam']) <= 0.12 else 'MISS',
                   verdict_support='PASS' if no_false_call else 'MISS',
                   ref_sn_10pct='within' if rel(b['sn'], t['sn']) <= 0.10 else 'outside',
                   ref_sw_25pct='within' if rel(b['sw'], t['sw']) <= 0.25 else 'outside',
                   stats=RP.statistics(c, c.y, c.mask))
        out.append(rec)
        print(f"{rec['cell']:42s} sn {b['sn']:.3f} ({t['sn']:.3f}, {rec['sn_rel']:.2f}) sw {b['sw']:.2f} "
              f"({t['sw']:.2f}, {rec['sw_rel']:.2f}) w {b['w']:.3f} (k {t['share']:.3f}) lam {b['lam']:+.3f} "
              f"{rec['verdict_lam']} {r['ranking'][0]} {rec['verdict_support']} rms {b['rms']:.2f}", flush=True)
    return out


def patch_given_section():
    """The patch reader with lam GIVEN (0, vitrea's truth; on Apple, the lam readers' value): the free-lam read
    above leaves lam unidentified on a sparse impulse lattice once the kernel is not the reader's Gaussian (the
    hinge column is nearly collinear with C and W), so the widths are read with lam held, as the protocol does."""
    out = []
    for sc, sch, s in available(IMPULSE):
        c = cell(sc, sch, s)
        if c.mask.sum() < 200:
            continue
        t = truth(sch, sc, s)
        r = RP.read([(c, c.mask)], 'linear', lam=0.0, supports=(('canvas', 'clamp', None), ('box', 'clamp', None),
                                                               ('box', 'norm', None)))
        b = r['best']
        canvas_rms = r['fits']['canvas/clamp']['rms']
        rec = dict(cell=f'{sch} {s}x {sc}', truth=t, sn=b['sn'], sn_iv=b.get('sn_iv'), sw=b['sw'],
                   sw_iv=b.get('sw_iv'), w=b['w'], rms=b['rms'], ranking=r['ranking'],
                   rms_by_support={k: v['rms'] for k, v in r['fits'].items()},
                   sn_rel=rel(b['sn'], t['sn']), sw_rel=rel(b['sw'], t['sw']),
                   narrow_share=1 - b['w'],
                   verdict_support='PASS' if canvas_rms - b['rms'] <= 0.05 else 'MISS',
                   ref_sn_10pct='within' if rel(b['sn'], t['sn']) <= 0.10 else 'outside',
                   ref_sw_25pct='within' if rel(b['sw'], t['sw']) <= 0.25 else 'outside')
        out.append(rec)
        print(f"{rec['cell']:42s} sn {b['sn']:.3f} ({t['sn']:.3f}, {rec['sn_rel']:.2f}) [{rec['sn_iv']}] sw {b['sw']:.2f} "
              f"({t['sw']:.2f}, {rec['sw_rel']:.2f}) w {b['w']:.3f} (k {t['share']:.3f}) {r['ranking'][0]} "
              f"{rec['verdict_support']} rms {b['rms']:.2f}", flush=True)
    return out


# ---------------------------------------------------------------- depth bins
DEPTH_CELLS = ['impulse__rrect-ml__rest', 'checkerboard-32__rrect-lg__rest', 'checkerboard-32__rrect-lg__inactive']


def depth_section():
    out = []
    for sc, sch, s in available(DEPTH_CELLS):
        c = cell(sc, sch, s)
        comp = sc.split('__')[1]
        t = truth(sch, sc, s)
        r = RD.read_bins(c, 'linear', lam=0.0, d_min=LENS[comp] + 1.0,
                         bins=(24.0, 32.0, 40.0, 48.0, 56.0, 64.0, 80.0))
        for lb, rr in r['rows'].items():
            iv = rr.get('sn_iv') or (np.nan, np.nan)
            ident = np.isfinite(iv[0]) and np.isfinite(iv[1]) and (iv[1] - iv[0]) <= 0.6 * max(rr['sn'], 0.1)
            rr.update(cell=f'{sch} {s}x {sc}', label=lb, sn_truth=t['sn'], identified=bool(ident),
                      verdict=('PASS' if abs(rr['ratio'] - 1) <= 0.05 else 'MISS') if ident else 'not identified')
            out.append(rr)
            print(f"{sch} {s}x {sc:38s} {lb:6s} depth {rr['depth']:5.1f} sn {rr['sn']:.3f} [{iv[0]:.2f},{iv[1]:.2f}] "
                  f"(code {t['sn']:.3f}) w {rr['w']:.3f} ratio {rr['ratio']:.3f} {rr['verdict']}", flush=True)
    return out


# ---------------------------------------------------------------- step reader on checker-64 edges
STEP_CELLS = [f'checkerboard-64__{c}__rest' for c in ('capsule-button', 'rrect-md', 'rrect-lg')] + \
    ['checkerboard-64__rrect-md__inactive', 'checkerboard-64__rrect-lg__inactive']


def step_section():
    out = []
    for sc, sch, s in available(STEP_CELLS):
        c = cell(sc, sch, s)
        if c.mask.sum() < 200:
            continue
        t = truth(sch, sc, s)
        r = RS.read([(c, None)], 'linear', narrow='flat')
        b = r['best']
        canvas_ok = r['call'] in (None, 'canvas/clamp')
        rec = dict(cell=f'{sch} {s}x {sc}', truth=t, call=r['call'], call_gap=r['call_gap'], ranking=r['ranking'],
                   rms={k: v['rms'] for k, v in r['fits'].items()}, sn=b['sn'], sw=b['sw'], sw_iv=b.get('sw_iv'),
                   lam=b['lam'], w=b['w'], sw_canvas=r['fits']['canvas/clamp']['sw'],
                   lam_canvas=r['fits']['canvas/clamp']['lam'],
                   verdict_lam='PASS' if abs(r['fits']['canvas/clamp']['lam']) <= 0.12 else 'MISS',
                   verdict_support='PASS' if canvas_ok else 'MISS',
                   ref_sw_25pct='within' if rel(r['fits']['canvas/clamp']['sw'], t['sw']) <= 0.25 else 'outside',
                   stats=RS.statistics(c, c.y))
        out.append(rec)
        print(f"{rec['cell']:44s} call {r['call']} gap {r['call_gap']:.3f} sw@canvas {rec['sw_canvas']:.2f} "
              f"(code {t['sw']:.2f}) lam@canvas {rec['lam_canvas']:+.3f} {rec['verdict_lam']} "
              f"{rec['verdict_support']}", flush=True)
    return out


# ---------------------------------------------------------------- lam readers, linear reading
LAM_CELLS = [f'{bg}__{c}__{p}' for bg in ('checkerboard', 'checkerboard-8', 'checkerboard-32', 'checkerboard-64')
             for c in ('capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg') for p in ('rest', 'inactive')]


def lambda_section():
    out = []
    for sc, sch, s in available(LAM_CELLS):
        c = cell(sc, sch, s)
        if c.mask.sum() < 200:
            continue
        t = truth(sch, sc, s)
        r = RL.per_cell_linear(c, t['sn'], t['sw'])
        g = RL.hinge_gap_linear(c, t['sn'], t['sw'])
        enc = RL.encoded_control(c, t['sn'], t['sw'])
        ok = abs(r['lam']) <= 0.12
        gl = [x['lam'] for x in g if x['lam'] is not None]
        rec = dict(cell=f'{sch} {s}x {sc}', truth=t, **r, gaps=g, encoded=enc,
                   verdict='PASS' if ok else 'MISS',
                   verdict_gap='PASS' if all(abs(v) <= 0.12 for v in gl) else 'MISS')
        out.append(rec)
        print(f"{rec['cell']:44s} lam {r['lam']:+.3f} [{r['lo']:+.2f},{r['hi']:+.2f}] free {r['lam_free']:+.3f} "
              f"w {r['w_free']:.3f} {rec['verdict']} | gaps {[round(v, 3) for v in gl]} {rec['verdict_gap']} | "
              f"encoded lam {enc['lam']:+.2f}", flush=True)
    return out


# ---------------------------------------------------------------- the re-proof against the replica (ruling 1)
# Each reader reads vitrea's CAPTURE and memo B's float64 REPLICA of the same cell on one mask (fork A's
# proof3_readers_a.pair_cells: vitrea's lens core intersected with the replica's own core), with the same call,
# and is scored on the difference at its proof-1 bar (tolerances.json "proof3_vitrea", b223600a). Each reader's
# own identifiability flag is applied to both readings: non-identifiable on both is reported and not scored,
# on one only is a miss.
REP_PATCH = [f'impulse__{c}__{p}' for c in ('capsule-button', 'rrect-sm', 'rrect-md', 'rrect-ml') for p in ('rest', 'inactive')]
REP_STEP = [f'checkerboard-64__{c}__rest' for c in ('capsule-button', 'rrect-sm', 'rrect-md', 'rrect-ml')] + \
    ['checkerboard-64__rrect-md__inactive']
REP_DEPTH = ['impulse__rrect-ml__rest', 'impulse__rrect-ml__inactive', 'checkerboard-32__rrect-ml__rest',
             'checkerboard__rrect-ml__rest', 'checkerboard__rrect-ml__inactive']
REP_LAM = [sc for sc in LAM_CELLS if '__rrect-lg__' not in sc]


def _bounded(iv, x, rel):
    """A profile interval is an identification when both its ends sit strictly inside the scanned range."""
    if not iv or x is None or not np.all(np.isfinite(iv)):
        return False
    lo, hi = max(0.0, x * rel[0] - 0.05), x * rel[1] + 0.05
    return iv[0] > lo + 1e-9 and iv[1] < hi - 1e-9


def _share_ok(w):
    return w is not None and np.isfinite(w) and 0.0 <= w <= 0.9


def read_patch_given(c):
    r = RP.read([(c, c.mask)], 'linear', lam=0.0, supports=(('canvas', 'clamp', None), ('box', 'clamp', None),
                                                             ('box', 'norm', None)))
    b = r['best']
    return dict(sn=b['sn'], sn_iv=b.get('sn_iv'), sw=b['sw'], sw_iv=b.get('sw_iv'), w=b['w'], rms=b['rms'],
                support=r['ranking'][0],
                id_sn=bool(_bounded(b.get('sn_iv'), b['sn'], (0.6, 1.6)) and _share_ok(b['w'])
                           and abs(b['sn'] - b['sw']) > 0.5),
                id_sw=bool(_bounded(b.get('sw_iv'), b['sw'], (0.6, 1.6)) and b['w'] is not None and 0.1 <= b['w'] <= 1))


def read_step_rep(c):
    r = RS.read([(c, None)], 'linear', narrow='flat')
    b = r['best']
    return dict(call=r['call'], call_gap=r['call_gap'], best=r['ranking'][0], sw=b['sw'], sw_iv=b.get('sw_iv'),
                lam=b['lam'], w=b['w'],
                id_sw=bool(_bounded(b.get('sw_iv'), b['sw'], (0.8, 1.25))), id_lam=bool(_share_ok(b['w'])))


def read_depth_rep(c):
    comp = c.comp_name
    r = RD.read_bins(c, 'linear', lam=0.0, d_min=LENS[comp] + 1.0, bins=(24.0, 32.0, 40.0, 48.0, 56.0, 64.0, 80.0))
    rows = {}
    for lb, x in r['rows'].items():
        rows[lb] = dict(depth=x['depth'], sn=x['sn'], ratio=x['ratio'], w=x['w'],
                        identified=bool(_bounded(x.get('sn_iv'), x['sn'], (0.6, 1.6)) and _share_ok(x['w'])))
    ref = r.get('ref')
    return dict(ref=ref, rows=rows)


def read_lam_rep(c, t):
    r = RL.per_cell_linear(c, t['sn'], t['sw'])
    g = RL.hinge_gap_linear(c, t['sn'], t['sw'])
    r['identified'] = bool(r['hi'] - r['lo'] <= 0.4 and -0.5 < r['lam'] < 1.6)
    return dict(cell=r, gaps=[dict(bin=x['bin'], lam=x['lam'], lo=x.get('lo'), hi=x.get('hi'),
                                   identified=bool(x['lam'] is not None and x['hi'] - x['lo'] <= 0.4)) for x in g])


def _score_rel(a, b, ida, idb, bar):
    if not ida and not idb:
        return 'reported (non-identifiable on both)', None
    if ida != idb:
        return 'MISS (identifiable on one image only)', None
    d = abs(a - b) / abs(b) if b else float('inf')
    return ('PASS' if d <= bar else 'MISS'), d


def _score_abs(a, b, ida, idb, bar):
    if not ida and not idb:
        return 'reported (non-identifiable on both)', None
    if ida != idb:
        return 'MISS (identifiable on one image only)', None
    d = abs(a - b)
    return ('PASS' if d <= bar else 'MISS'), d


def replica_section():
    import proof3_readers_a as PA
    eq = PA.replica_equivalence()
    out = dict(equivalence=eq, rows=[])
    plan = [(sc, 'patch') for sc in REP_PATCH] + [(sc, 'step') for sc in REP_STEP] + \
        [(sc, 'depth') for sc in REP_DEPTH] + [(sc, 'lambda') for sc in REP_LAM]
    for sc, what in plan:
        if canon.ROLE.get(sc) not in canon.ADMIT:
            continue
        for sch in SCHEMES:
            for s in SCALES:
                pc = PA.pair_cells(sc, sch, s)
                if pc is None:
                    continue
                c, r, k = pc
                t = truth(sch, sc, s)
                row = dict(reader=what, cell=f'{sch} {s}x {sc}', k_mean=k, npx=int(c.mask.sum()), truth=t)
                if what == 'patch':
                    a, b = read_patch_given(c), read_patch_given(r)
                    row.update(cap=a, rep=b)
                    row['score_sn'] = _score_rel(a['sn'], b['sn'], a['id_sn'], b['id_sn'], 0.05)
                    row['score_sw'] = _score_rel(a['sw'], b['sw'], a['id_sw'], b['id_sw'], 0.05)
                    msg = f"sn {a['sn']:.3f}/{b['sn']:.3f} {row['score_sn'][0]} sw {a['sw']:.2f}/{b['sw']:.2f} {row['score_sw'][0]}"
                elif what == 'step':
                    a, b = read_step_rep(c), read_step_rep(r)
                    row.update(cap=a, rep=b)
                    row['score_sw'] = _score_rel(a['sw'], b['sw'], a['id_sw'], b['id_sw'], 0.05)
                    row['score_call'] = ('PASS' if a['call'] == b['call'] else 'MISS', None)
                    row['score_lam'] = _score_abs(a['lam'], b['lam'], a['id_lam'], b['id_lam'], 0.03)
                    msg = (f"sw {a['sw']:.2f}/{b['sw']:.2f} {row['score_sw'][0]} call {a['call']}/{b['call']} "
                           f"{row['score_call'][0]} lam {a['lam']:+.3f}/{b['lam']:+.3f} {row['score_lam'][0]}")
                elif what == 'depth':
                    a, b = read_depth_rep(c), read_depth_rep(r)
                    row.update(cap=a, rep=b, scores={})
                    for lb in sorted(set(a['rows']) | set(b['rows'])):
                        xa, xb = a['rows'].get(lb), b['rows'].get(lb)
                        if xa is None or xb is None:
                            row['scores'][lb] = ('MISS (bin read on one image only)', None)
                            continue
                        ida = xa['identified'] and a['rows'][a['ref']]['identified']
                        idb = xb['identified'] and b['rows'][b['ref']]['identified']
                        row['scores'][lb] = _score_abs(xa['ratio'], xb['ratio'], ida, idb, 0.05)
                    msg = ' '.join(f"{lb}:{v[0].split(' ')[0]}" for lb, v in row['scores'].items())
                else:
                    a, b = read_lam_rep(c, t), read_lam_rep(r, t)
                    row.update(cap=a, rep=b)
                    ca, cb = a['cell'], b['cell']
                    st, d = _score_abs(ca['lam'], cb['lam'], ca['identified'], cb['identified'], 0.03)
                    if st == 'PASS' and not (ca['lo'] <= cb['lam'] <= ca['hi'] and cb['lo'] <= ca['lam'] <= cb['hi']):
                        st = 'MISS (intervals do not contain each other\'s point)'
                    row['score_lam'] = (st, d)
                    row['score_gaps'] = []
                    for ga, gb in zip(a['gaps'], b['gaps']):
                        if ga['lam'] is None and gb['lam'] is None:
                            continue
                        row['score_gaps'].append((ga['bin'], *_score_abs(ga['lam'] or 0, gb['lam'] or 0,
                                                                         ga['identified'], gb['identified'], 0.05)))
                    msg = (f"lam {ca['lam']:+.3f}/{cb['lam']:+.3f} {st} | gaps "
                           + ' '.join(x[1].split(' ')[0] for x in row['score_gaps']))
                out['rows'].append(row)
                json.dump(out, open(f'{OUT}.replica.json', 'w'), indent=1, default=float)
                print(f"{what:6s} {row['cell']:46s} {msg}", flush=True)
    return out


def report():
    import glob
    res = {}
    for f in sorted(glob.glob(f'{OUT}.*.json')):
        res[f.split('.')[1]] = json.load(open(f))
    json.dump(res, open(f'{OUT}.json', 'w'), indent=1, default=float)


if __name__ == '__main__':
    for sec in sys.argv[1:]:
        if sec == 'report':
            report()
            continue
        fn = {'patch': patch_section, 'patch_given': patch_given_section, 'depth': depth_section,
              'replica': replica_section, 'step': step_section, 'lambda': lambda_section}[sec]
        json.dump(fn(), open(f'{OUT}.{sec}.json', 'w'), indent=1, default=float)
