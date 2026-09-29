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
        fn = {'patch': patch_section, 'patch_given': patch_given_section, 'depth': depth_section, 'step': step_section, 'lambda': lambda_section}[sec]
        json.dump(fn(), open(f'{OUT}.{sec}.json', 'w'), indent=1, default=float)
