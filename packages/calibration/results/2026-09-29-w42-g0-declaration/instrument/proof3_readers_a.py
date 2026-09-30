"""W42 G0 instrument, proof 3 for five statistic readers (charter clause 2, third bar): on vitrea's own
canonical web captures, whose body the code fixes, each reader reads what the code draws, and that measures
the reader's resolution on REAL pixels.

What the code draws (memo B §1; `canon.kernels()`, SHA-256 9c684eb9…): a two-sided LINEAR-light blend
enc(R + B ((1 - k) Ksharp * b + k Kdeep * b - Lbar)) with Ksharp the chain's L1 kernel (sigma_RMS 1.58 device
px at both scales), Kdeep the L4 heavy texture (13.8-14.6 dev, 2x light active 20.8) or, dark active 2x, a
chain LOD (10.2 dev), a share k graded by span, scale, depth and pose, and no knee. So in the linear reading
(space 'lin', T 'srgb', canvas kernels, no capture floor) the truth is lam = 0, s1/gain = 0, sn = 1.58 dev /
scale, sw = the deep kernel's sigma_RMS / scale, w = k. The deep kernels are not Gaussian (L4 is platykurtic,
kurtosis -0.41; the dark 2x LOD leptokurtic, +0.93), so a Gaussian reader's deep width differs from sigma_RMS
by construction: memo B's float64 replica of the shader (`~/vitrea-w42/grounding/kernel/code-map/verify.py`,
SHA-256 45f54862…, imported read-only; it reproduces 11 web cores at rms 0.27-0.38 code) is read by the same
readers on a subset, which splits that model mismatch from the real-pixel error (capture minus replica).

Cells: canonical calibration, validation and PROBE scenes only (canon.web_cell refuses the rest), web captures
only, all four endpoints, both scales: checkerboards at pitch 4-64 and the impulse lattice. The body core is
where the code's blend is the whole story: depth beyond the lens band (lensExtent + 1 device px, the replica's
`core`), intersected with the reader's deep mask.

Usage: python3.12 proof3_readers_a.py [endpoint ...] [--replica]
"""
import hashlib
import json
import os
import sys
import time

import numpy as np

import canon
import geometry as G
import read_esf as RE
import read_heavy as RH
import read_impulse as RI
import read_mirror as RMi
import read_model as RM

REPLICA_SHA = '45f548629e25c975552f7a2850846c2d8b7885aaf2250f77a3db9da70de137eb'
RESOLVED = json.load(open(f'{canon.CODE_MAP}/resolved.json'))['endpoints']
_replica = None


def replica():
    global _replica
    if _replica is None:
        p = f'{canon.CODE_MAP}/verify.py'
        assert hashlib.sha256(open(p, 'rb').read()).hexdigest() == REPLICA_SHA, 'verify.py moved'
        src = open(p).read()
        src = src[:src.index('CASES = [')]      # the module's own comparison loop is not run
        sys.path.insert(0, canon.CODE_MAP)
        ns = {'__file__': p, '__name__': 'w42_replica'}
        exec(compile(src, p, 'exec'), ns)
        _speed_up(ns)
        _replica = ns['render']
    return _replica


def _speed_up(ns):
    """Two arithmetic-preserving substitutions in the replica's namespace (its source file is not touched):
    `upsample` computes the same separable bilinear upsampling as two matrix products per channel instead
    of one three-operand einsum (O(H W h w) per channel, minutes at 2x), and `Chain` is built once per
    canvas size instead of once per render. `replica_equivalence()` checks the result against the original
    functions to float64 rounding."""
    orig_up, orig_chain = ns['upsample'], ns['Chain']
    bilinear_row = ns['bilinear_row']

    def upsample(level, W, H):
        hl, wl = level.shape[:2]
        Sx = np.stack([bilinear_row((x + 0.5) / W, wl) for x in range(W)])
        Sy = np.stack([bilinear_row((y + 0.5) / H, hl) for y in range(H)])
        return np.stack([Sy @ level[..., c] @ Sx.T for c in range(level.shape[2])], -1)
    chains = {}

    def Chain(W, H):
        if (W, H) not in chains:
            chains[(W, H)] = orig_chain(W, H)
        return chains[(W, H)]
    ns['_orig'] = (orig_up, orig_chain)
    ns['upsample'], ns['Chain'] = upsample, Chain
    ns['_ns'] = ns


def replica_equivalence(ep='light-active', scale=1, bg='checkerboard', comp='rrect-md'):
    """Max |fast - original| over the replica's render of one cell (the original einsum path at 1x)."""
    render = replica()
    ns = render.__globals__
    fast = render(ep, scale, bg, comp)[0]
    up, ch = ns['upsample'], ns['Chain']
    ns['upsample'], ns['Chain'] = ns['_orig']
    try:
        slow = render(ep, scale, bg, comp)[0]
    finally:
        ns['upsample'], ns['Chain'] = up, ch
    return float(np.abs(fast - slow).max())


def lens_core(c):
    """Depth beyond the code's lens band: lensExtent + 1 device px (resolved.json, per component)."""
    code_ep = canon.CODE_EP[c.ep]
    comp = canon.CODE_COMP.get(c.comp_name)
    if comp is None:
        return None
    le = RESOLVED[code_ep]['perScale'][f'{c.scale}x']['components'][comp]['lensExtent']
    return -c.d > le + 1.0 / c.scale


def cell(scene, scheme, scale):
    if not canon.exists(scene, scheme, scale):
        return None
    c = canon.web_cell(scene, scheme, scale)
    core = lens_core(c)
    if core is None:
        return None
    c.mask = c.mask & core
    c.y = np.where(c.mask, c.y, np.nan)
    c.T = type('NoT', (), {'trust_below': None})()
    c._rm = {}
    return c if c.mask.sum() > 200 else None


def truth(c):
    code_ep, comp = canon.CODE_EP[c.ep], canon.CODE_COMP[c.comp_name]
    kr = canon.kernels()[(code_ep, c.scale, comp)]
    return dict(sn=kr['body']['sx'] / c.scale, sw=0.5 * (kr['heavy']['sx'] + kr['heavy']['sy']) / c.scale,
                sw_kurt=kr['heavy']['kurt'], k_centre=kr['kScatterSpan'], deep=kr['deep'])


def replica_cell(c):
    """The same cell with the replica's float render as its observation (the code's exact body)."""
    import copy
    code_ep, comp = canon.CODE_EP[c.ep], canon.CODE_COMP[c.comp_name]
    bg = c.id.split('__')[0]
    out, core, kmap, _ = replica()(code_ep, c.scale, bg, comp)
    r = copy.copy(c)
    r._rm = {}
    r.y = np.where(c.mask & core, G.luma(out), np.nan)
    r.mask = c.mask & core
    r.kmap = kmap
    return r


ENDS = [('light', 'rest'), ('light', 'inactive'), ('dark', 'rest'), ('dark', 'inactive')]
CHECKERS = {'rest': [('checkerboard', 'rrect-md'), ('checkerboard', 'capsule-button'), ('checkerboard', 'rrect-ml'),
                     ('checkerboard-8', 'rrect-md'), ('checkerboard-32', 'rrect-md'), ('checkerboard-64', 'rrect-md'),
                     ('checkerboard-64', 'rrect-ml'), ('checkerboard-64', 'capsule-button'), ('checkerboard-4', 'rrect-md')],
            'inactive': [('checkerboard', 'rrect-md'), ('checkerboard', 'capsule-button'), ('checkerboard', 'rrect-ml'),
                         ('checkerboard-8', 'rrect-md'), ('checkerboard-64', 'rrect-md'), ('checkerboard-4', 'rrect-md')]}
IMPULSES = {'rest': [('impulse', 'rrect-md'), ('impulse', 'capsule-button'), ('impulse', 'rrect-ml')],
            'inactive': [('impulse', 'rrect-md'), ('impulse', 'capsule-button'), ('impulse', 'rrect-ml')]}


MIRROR_ONLY = '--which=mirror' in sys.argv


def read_all(c, log, tag, tr, rows, ep):
    p = c.bg_spec.get('cell')
    kmean = float(np.mean(c.kmap[c.mask])) if hasattr(c, 'kmap') else None
    if MIRROR_ONLY:
        # S alone, re-read after the mirror reader's identifiability rule changed (vitrea's narrow is flat in
        # depth, so the single-width path is its reading)
        if c.bg_spec['kind'] != 'checkerboard':
            return
        mi = RMi.read(c, kind='canvas', space='lin', floor=False, Tkind='srgb')
        rows.append(dict(ep=ep, cell=c.id, scale=c.scale, pitch=p, src=tag, truth=tr, mirror_only=True,
                         mirror=None if mi is None else {q: mi[q] for q in ('s1_gain', 's1_gain_range', 'identified', 'checks', 'sn', 'sw', 'rmsD', 'rmsS', 'n')}))
        log(f"{tag:7s} {ep:14s} {c.scale}x {c.id:36s} | S " + ('none' if mi is None else
            f"{mi['s1_gain']:+.4f} identified {mi['identified']} {[k for k, v in mi['checks'].items() if not v]}"))
        return
    if c.bg_spec['kind'] == 'checkerboard':
        m = RM.read(c, kind='canvas', space='lin', floor=False, Tkind='srgb')
        me = RM.read(c, kind='canvas', space='enc', floor=False, Tkind='enc-affine')
        mi = RMi.read(c, kind='canvas', space='lin', floor=False, Tkind='srgb')
        hv = RH.read(c, d_core=min(14.0, p / 4.5), space='lin', floor=False, Tkind='srgb') if p >= 32 else None
        es = RE.read(c, Tkind='srgb', space='lin', side=1, margin_pt=4.0)
        es_d = RE.read(c, Tkind='srgb', space='lin', side=-1, margin_pt=4.0)
        row = dict(ep=ep, cell=c.id, scale=c.scale, pitch=p, src=tag, truth=tr, k_mean_replica=kmean,
                   model_lin={q: m[q] for q in ('sn', 'sw', 'lam', 'w', 'rms')},
                   model_enc_known_space={q: me[q] for q in ('sn', 'sw', 'lam', 'w', 'rms')},
                   mirror=None if mi is None else {q: mi[q] for q in ('s1_gain', 's1_gain_range', 'identified', 'sn', 'sw', 'rmsD', 'rmsS', 'n')},
                   heavy=None if not hv else {f: {q: hv[f][q] for q in ('sw', 'iv', 'rms', 'lam', 'w')} for f in RH.FAMILIES if f in hv} | {'best': hv['best']},
                   esf_bright=None if es is None else {q: es[q] for q in ('sigma', 'iv', 'identified', 'rms', 'n_edges')},
                   esf_dark=None if es_d is None else {q: es_d[q] for q in ('sigma', 'iv', 'identified', 'rms', 'n_edges')})
        rows.append(row)
        s1 = row['mirror']['s1_gain'] if row['mirror'] else float('nan')
        log(f"{tag:7s} {ep:14s} {c.scale}x {c.id:36s} | model lin sn {m['sn']:.3f}/{tr['sn']:.3f} sw {m['sw']:.2f}/{tr['sw']:.2f} "
            f"lam {m['lam']:+.3f} w {m['w']:.3f}{'' if kmean is None else f'/{kmean:.3f}'} rms {m['rms']:.2f} | enc lam {me['lam']:+.3f} "
            f"| S {s1:+.4f} | ESF {es and round(es['sigma'], 3)}/{es_d and round(es_d['sigma'], 3)}"
            + ('' if not hv else f" | heavy best {hv['best']} " + ' '.join(f"{f}:{hv[f]['sw']:.1f} {hv[f]['rms']:.3f}" for f in RH.FAMILIES if f in hv)))
    else:
        im = RI.read(c, margin_pt=2.0, R_pt=28.0, Tkind='srgb')
        imo = RI.read(c, margin_pt=2.0, R_pt=28.0, Tkind='output', mix=False)
        if im is None:
            return
        row = dict(ep=ep, cell=c.id, scale=c.scale, src=tag, truth=tr, k_mean_replica=kmean,
                   impulse_single=im['single'], impulse_mix=im['mix'], impulse_output_single=imo['single'])
        rows.append(row)
        g, mx = im['single'], im['mix']
        log(f"{tag:7s} {ep:14s} {c.scale}x {c.id:36s} | impulse single {g['sigma']:.3f}/{tr['sn']:.3f} (output-affine "
            f"{imo['single']['sigma']:.3f}) | mix s1 {mx['s1']:.3f} s2 {mx['s2']:.2f}/{tr['sw']:.2f} k {mx['k']:.3f}"
            f"{'' if kmean is None else f'/{kmean:.3f}'} rms {mx['rms']:.2f}")


def main(eps, use_replica):
    for scheme, pose in eps:
        ep = f'{scheme}-{pose}'
        rows = []
        suffix = '.mirror' if MIRROR_ONLY else ''
        fh = open(f'proof3_readers_a.{ep}{suffix}.txt', 'w')

        def log(s):
            print(s, flush=True)
            fh.write(s + '\n')
            fh.flush()
        t0 = time.time()
        for scale in (1, 2):
            for bg, comp in CHECKERS[pose] + IMPULSES[pose]:
                scene = f'{bg}__{comp}__{pose}'
                if canon.ROLE.get(scene) not in canon.ADMIT:
                    continue
                c = cell(scene, scheme, scale)
                if c is None:
                    continue
                tr = truth(c)
                read_all(c, log, 'capture', tr, rows, ep)
                if use_replica and not MIRROR_ONLY and scale == 1 and bg in ('checkerboard', 'checkerboard-64', 'impulse'):
                    rc = replica_cell(c)
                    read_all(rc, log, 'replica', tr, rows, ep)
        log(f'# {ep} done in {time.time() - t0:.0f} s')
        json.dump(rows, open(f'proof3_readers_a.{ep}{suffix}.json', 'w'), indent=1, default=float)


# ---------------------------------------------------------------- the re-proof against the replica (ruling 1)

def pair_cells(scene, scheme, scale):
    """The capture cell and the replica cell of one scene on ONE mask: vitrea's lens core (depth beyond
    lensExtent + 1 device px) intersected with the replica's own core. Apple's refraction band does not
    apply to vitrea's pixels, so the mask is the code's own lens core, not the band rule."""
    if not canon.exists(scene, scheme, scale):
        return None
    c = canon.web_cell(scene, scheme, scale, d_in=0.0)
    core = lens_core(c)
    if core is None:
        return None
    code_ep, comp = canon.CODE_EP[c.ep], canon.CODE_COMP[c.comp_name]
    out, rcore, kmap, _ = replica()(code_ep, scale, scene.split('__')[0], comp)
    m = c.mask & core & rcore
    if m.sum() < 200:
        return None
    y_cap = c.y
    c.mask = m
    c.y = np.where(m, y_cap, np.nan)
    c.T = type('NoT', (), {'trust_below': None})()
    c._rm = {}
    import copy
    r = copy.copy(c)
    r._rm = {}
    r.y = np.where(m, G.luma(out), np.nan)
    k = float(np.mean(kmap[m]))
    return c, r, k


def read_set(c):
    """Every reader of this fork on one image, in vitrea's linear reading (canvas kernels, no capture floor,
    the sRGB-affine T); the same call on the capture and on the replica."""
    out = {}
    if c.bg_spec['kind'] == 'checkerboard':
        p = c.bg_spec['cell']
        m = RM.read(c, kind='canvas', space='lin', floor=False, Tkind='srgb')
        out['model'] = None if m is None else {q: m[q] for q in ('sn', 'sw', 'lam', 'w', 'rms')}
        me = RM.read(c, kind='canvas', space='enc', floor=False, Tkind='enc-affine')
        out['model_enc'] = None if me is None else {q: me[q] for q in ('lam', 'w', 'rms')}
        mi = RMi.read(c, kind='canvas', space='lin', floor=False, Tkind='srgb') if p >= 8 else None
        out['mirror'] = None if mi is None else {q: mi[q] for q in ('s1_gain', 's1_gain_range', 'identified', 'checks', 'rmsD', 'rmsS', 'n')}
        if p >= 32:
            hv = RH.read(c, d_core=min(14.0, p / 4.5), space='lin', floor=False, Tkind='srgb')
            out['heavy'] = None if not hv else {'best': hv['best'], **{f: {q: hv[f][q] for q in ('sw', 'iv', 'rms')}
                                                                       for f in RH.FAMILIES if f in hv}}
        for side, sg in (('esf_bright', 1), ('esf_dark', -1)):
            e = RE.read(c, Tkind='srgb', space='lin', side=sg, margin_pt=0.0)
            out[side] = None if e is None else {q: e[q] for q in ('sigma', 'iv', 'identified', 'n_edges')}
    else:
        im = RI.read(c, margin_pt=0.0, R_pt=28.0, Tkind='srgb')
        out['impulse'] = None if im is None else {'single': {q: im['single'][q] for q in ('sigma', 'rms')},
                                                  'mix': {q: im['mix'][q] for q in ('s1', 's2', 'k', 'rms')}}
    return out


def replica_main(eps):
    """ruling 1: every proof-3 cell the replica covers, both scales, all four endpoints, read on the capture
    and on the replica with the same call; scored in summarize_a.py at the proof-1 bars."""
    eq = replica_equivalence()
    for scheme, pose in eps:
        ep = f'{scheme}-{pose}'
        rows = []
        fh = open(f'proof3_readers_a.{ep}.replica.txt', 'w')

        def log(s):
            print(s, flush=True)
            fh.write(s + '\n')
            fh.flush()
        log(f'# replica fast path against the original functions: max |difference| {eq:.2e} (1x md checker)')
        t0 = time.time()
        for scale in (1, 2):
            for bg, comp in CHECKERS[pose] + IMPULSES[pose]:
                scene = f'{bg}__{comp}__{pose}'
                if canon.ROLE.get(scene) not in canon.ADMIT or canon.CODE_COMP.get(comp) is None:
                    continue
                pc = pair_cells(scene, scheme, scale)
                if pc is None:
                    log(f'{ep:14s} {scale}x {scene:40s} no capture or fewer than 200 px on the joint core')
                    continue
                c, r, k = pc
                row = dict(ep=ep, cell=scene, scale=scale, pitch=c.bg_spec.get('cell'), kind=c.bg_spec['kind'],
                           k_mean=k, npx=int(c.mask.sum()), truth=truth(c), cap=read_set(c), rep=read_set(r))
                rows.append(row)
                a, b = row['cap'], row['rep']
                if 'model' in a:
                    f = lambda x, q: float('nan') if x is None else x[q]
                    log(f"{ep:14s} {scale}x {scene:40s} k {k:.2f} | model sn {f(a['model'],'sn'):.3f}/{f(b['model'],'sn'):.3f} "
                        f"sw {f(a['model'],'sw'):.2f}/{f(b['model'],'sw'):.2f} lam {f(a['model'],'lam'):+.3f}/{f(b['model'],'lam'):+.3f} "
                        f"w {f(a['model'],'w'):.3f}/{f(b['model'],'w'):.3f} | S "
                        + ('-' if a['mirror'] is None or b['mirror'] is None else
                           f"{a['mirror']['s1_gain']:+.4f}{'*' if a['mirror']['identified'] else ''}/{b['mirror']['s1_gain']:+.4f}{'*' if b['mirror']['identified'] else ''}")
                        + f" | ESF {a['esf_bright'] and round(a['esf_bright']['sigma'], 3)}/{b['esf_bright'] and round(b['esf_bright']['sigma'], 3)}"
                        + ('' if 'heavy' not in a or not a['heavy'] or not b.get('heavy') else
                           f" | heavy {a['heavy']['best']} {a['heavy']['canvas']['sw']:.2f} / {b['heavy']['best']} {b['heavy']['canvas']['sw']:.2f}"))
                else:
                    ia, ib = a['impulse'], b['impulse']
                    log(f"{ep:14s} {scale}x {scene:40s} k {k:.2f} | impulse "
                        + ('-' if not ia or not ib else
                           f"single {ia['single']['sigma']:.3f}/{ib['single']['sigma']:.3f} s1 {ia['mix']['s1']:.3f}/{ib['mix']['s1']:.3f} "
                           f"k {ia['mix']['k']:.3f}/{ib['mix']['k']:.3f}"))
        log(f'# {ep} done in {time.time() - t0:.0f} s')
        json.dump(dict(equivalence=eq, rows=rows), open(f'proof3_readers_a.{ep}.replica.json', 'w'), indent=1, default=float)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    eps = [tuple(a.split('-')) for a in args] or ENDS
    if '--replica-all' in sys.argv:
        replica_main(eps)
    else:
        main(eps, '--replica' in sys.argv)
