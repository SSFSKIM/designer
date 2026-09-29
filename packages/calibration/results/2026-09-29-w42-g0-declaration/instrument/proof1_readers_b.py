"""W42 G0 instrument, proof 1 for the step, patch, depth and lam readers (charter clause 2; tolerances.json,
declared before this ran): synthetic renders of the declared families through the known T (memo C's table),
quantised +-0.5, on the bed's geometry (bed.py), read back and scored against the declared bars.

    python3.12 proof1_readers_b.py <section> [...]     sections: patch depth step lambda u1 report

Each section writes proof1_readers_b.<section>.json; `report` gathers them into proof1_readers_b.json/.txt.
Also the U1 diagnostic (section u1): rival truths that move W's far reference (W-shape, W-tails, K2, the
canvas support, the swapped edge mode) rendered on the receded cells and read by LT's per-cell lam and
hinge-gap readers at LT's own pooled scale, which is how memo E read Apple.
"""
import json
import sys
import zlib

import numpy as np

import bed
import families as FA
import fitting as FI
import forward as F
import geometry as G
import read_depth as RD
import read_lambda as RL
import read_patch as RP
import read_step as RS

EPS = F.ENDPOINTS
OUT = 'proof1_readers_b'


def save(sec, out):
    json.dump(out, open(f'{OUT}.{sec}.json', 'w'), indent=1, default=float)


def seed(c):
    return zlib.crc32(c.id.encode()) & 0xffff


def truth_params(name, ep):
    k, lam = FA.TRUTH_K[ep], FA.TRUTH_LAM[ep]
    p = {'k': k, 'lam': lam}
    pose = ep.split('-')[1]
    if name == 'free-sn':
        p.update({f'sn_{pose}_{s}': v for s, v in FA.TRUTH_EXTRA['free-sn'][pose].items()})
    elif name in FA.TRUTH_EXTRA:
        p.update(FA.TRUTH_EXTRA[name])
    return p


def fam(name):
    return FA.FAMILIES[name][0]


def synth_all(cells, name, ep):
    p = truth_params(name, ep)
    for c in cells:
        F.synth(c, fam(name), p, seed=seed(c))
    return p


def rel(a, b):
    return abs(a - b) / abs(b) if b else float('inf')


def checker(a, b, pitch):
    return {'kind': 'checkerboard', 'cell': pitch, 'a': [a] * 3, 'b': [b] * 3}


def extra_cells(rows, ep, scale=2):
    """Diagnostic cells beyond the declared bed (the U1 capsule/md pitch-16 twins); never a bed claim."""
    sch, pose = ep.split('-')
    out = []
    for cid, letter, bg, comp in rows:
        c = F.Cell(f'{scale}x|{cid}', bg, comp, scale, sch, pose)
        c.letter, c.bed_id = letter, cid
        out.append(c)
    return out


def pol(ep):
    """The depth sweep's polarity per pass (bed.json: 'hi' in the light passes, 'lo' in the dark ones)."""
    return 'hi' if ep.startswith('light') else 'lo'


# ---------------------------------------------------------------- patch
PATCH_GROUPS = [('S8 md', ['c-s8-hi-rrect-md', 'c-s8-lo-rrect-md']), ('S32 md', ['c-s32-hi-rrect-md', 'c-s32-lo-rrect-md']),
                ('S16 capsule', ['c-s16-hi-capsule-button', 'c-s16-lo-capsule-button']),
                ('impulse ml', ['c-impulse-rrect-ml']), ('impulse lg', ['c-impulse-rrect-lg'])]


def olaw_sn(c, k, depth):
    return float(k * F.RN * F.opacity_law(np.array([-depth]), c.span, c.active)[0])


def patch_section():
    out = []
    for ep in EPS:
        for tname in ('free-sn', 'LT'):
            for gname, ids in PATCH_GROUPS:
                cs = bed.cells(ep, 2, ids=ids)
                if not cs:
                    continue
                p = synth_all(cs, tname, ep)
                c0 = cs[0]
                sw_t = 8 * p['k']
                if tname == 'free-sn':
                    sn_t = F.free_sigma(p, c0.pose, c0.span)
                    sn_rng = (sn_t, sn_t)
                else:
                    cen = RP.patch_centres(c0)
                    deps = [float(-c0.d[int(cy * c0.scale), int(cx * c0.scale)]) for _, cy, cx in cen
                            if c0.mask[int(cy * c0.scale), int(cx * c0.scale)]]
                    sn_t = float(np.mean([olaw_sn(c0, p['k'], d) for d in deps])) if deps else float('nan')
                    sn_rng = (min(olaw_sn(c0, p['k'], max(d - 8, 0.5)) for d in deps),
                              max(olaw_sn(c0, p['k'], d) for d in deps)) if deps else (np.nan, np.nan)
                cp = [(c, RP.reader_mask(c)) for c in cs]
                r_free = RP.read(cp, 'native', supports=(('box', 'clamp', None), ('box', 'norm', None)))
                r_given = RP.read(cp, 'native', lam=p['lam'], w=0.5, supports=((r_free['best']['support'],
                                  r_free['best']['edge'], None),), intervals=False) if tname == 'LT' else None
                b = r_free['best']
                eff_t = RP.effective_dev(c0, sn_t)
                eff_r = RP.effective_dev(c0, b['sn'])
                floor_dominated = sn_t * c0.scale < 0.4 * c0.f
                sn_ok = (rel(eff_r, eff_t) <= 0.05) if floor_dominated else (rel(b['sn'], sn_t) <= 0.05)
                rec = dict(ep=ep, truth=tname, group=gname, sn_truth=sn_t, sn_truth_range=sn_rng, sw_truth=sw_t,
                           lam_truth=p['lam'], sn=b['sn'], sn_iv=b.get('sn_iv'), sw=b['sw'], sw_iv=b.get('sw_iv'),
                           lam=b['lam'], w=b['w'], rms=b['rms'], support=f"{b['support']}/{b['edge']}",
                           ranking=r_free['ranking'], call_gap=r_free['call_gap'],
                           eff_dev_truth=eff_t, eff_dev=eff_r, floor_dominated=bool(floor_dominated),
                           sn_given=r_given['best']['sn'] if r_given else None,
                           sw_given=r_given['best']['sw'] if r_given else None,
                           sn_rel=rel(b['sn'], sn_t), sw_rel=rel(b['sw'], sw_t),
                           verdict_sn=('PASS' if sn_ok else 'MISS') if tname == 'free-sn' else 'report (depth-graded)',
                           verdict_sw='PASS' if rel(b['sw'], sw_t) <= 0.05 else 'MISS',
                           stats=RP.statistics(c0, c0.y, RP.reader_mask(c0)))
                out.append(rec)
                save('patch', out)
                print(f"{ep:15s} {tname:8s} {gname:12s} sn {b['sn']:.3f} (truth {sn_t:.3f} rel {rec['sn_rel']:.3f} "
                      f"{rec['verdict_sn']}) sw {b['sw']:.2f} ({sw_t:.2f} {rec['verdict_sw']}) lam {b['lam']:.3f} "
                      f"w {b['w']:.3f} rms {b['rms']:.3f} [{rec['support']}]", flush=True)
    # the optional tail read on a W-tails truth (light receded, S32 pair)
    ep = 'light-inactive'
    cs = bed.cells(ep, 2, ids=['c-s32-hi-rrect-md', 'c-s32-lo-rrect-md'])
    p = synth_all(cs, 'W-tails', ep)
    cp = [(c, RP.reader_mask(c)) for c in cs]
    one = RP.read(cp, 'native', supports=(('box', 'norm', None),), intervals=False)['best']
    tail = RP.read_tails(cp, 'native', one['sn'], one['sw'], 'box', 'norm')
    out.append(dict(ep=ep, truth='W-tails', group='S32 md (tail read)', one_gauss=one, tails=tail,
                    truth_tail=dict(s2=p['s2'], a=p['a'], sw=8 * p['k'])))
    print('tails', one['rms'], one['sw'], tail, flush=True)
    return out


# ---------------------------------------------------------------- depth
def depth_sets(ep):
    q = pol(ep)
    return {'md': [f'c-s8-{q}-rrect-md', f'c-s8-{q}-d24-rrect-md', f'c-s8-{q}-d4-rrect-md'],
            'lg': [f'c-s8-{q}-d80-rrect-lg', f'c-s8-{q}-d40-rrect-lg', f'c-s8-{q}-d4-rrect-lg']}


def depth_section():
    out = []
    for ep in EPS:
        excl = bed.refraction_exclusions(ep, 2)
        truths = ['LT'] + (['free-sn'] if ep.endswith('rest') else [])
        for tname in truths:
            for shape, ids in depth_sets(ep).items():
                allc = {c.bed_id: c for c in bed.cells(ep, 2, ids=ids, with_excluded=True)}
                use = [(i, allc[i]) for i in ids if i in allc and i not in excl]
                for i in ids:
                    if i in excl:
                        out.append(dict(ep=ep, truth=tname, shape=shape, label=i, verdict='EXCLUDED', reason=excl[i]))
                synth_all([c for _, c in use], tname, ep)
                r = RD.read(use, 'native')
                for lb, rr in r['rows'].items():
                    expect = rr['olaw_ratio'] if (tname == 'LT' and ep.endswith('rest')) else 1.0
                    ok = rr.get('sn') is not None and abs(rr['ratio'] - expect) <= 0.05
                    rr.update(ep=ep, truth=tname, shape=shape, label=lb, expect=expect,
                              verdict='PASS' if ok else ('UNREAD' if rr.get('sn') is None else 'MISS'))
                    out.append(rr)
                    save('depth', out)
                    print(f"{ep:15s} {tname:8s} {shape} {lb:24s} depth {rr['depth']:5.1f} "
                          f"sn {rr['sn'] if rr['sn'] is None else round(rr['sn'], 3)} ratio {rr.get('ratio')} "
                          f"expect {expect:.3f} {rr['verdict']} {rr.get('band', '')}", flush=True)
        # the checker form of the reader: depth bins on B' P1 pitch 32 on rrect-lg (the declared deep mask)
        cs = bed.cells(ep, 2, ids=['bp-p1-c32-rrect-lg'])
        synth_all(cs, 'LT', ep)
        rb = RD.read_bins(cs[0], 'native')
        for lb, rr in rb['rows'].items():
            expect = rr['olaw_ratio'] if ep.endswith('rest') else 1.0
            rr.update(ep=ep, truth='LT', shape='lg P1 p32 (bins)', label=lb, expect=expect,
                      verdict='PASS' if abs(rr['ratio'] - expect) <= 0.05 else 'MISS')
            out.append(rr)
            save('depth', out)
            print(f"{ep:15s} LT bins lg-p32 {lb:8s} depth {rr['depth']:5.1f} sn {rr['sn']:.3f} ratio {rr['ratio']:.3f} "
                  f"expect {expect:.3f} {rr['verdict']}", flush=True)
    return out


# ---------------------------------------------------------------- step
STEP_TRUTHS = {'LT': None, 'W-canvas': 'canvas/clamp', 'edge-swap': None, 'W-shape': 'shape/norm'}


def step_truth_support(name, ep):
    act = ep.endswith('rest')
    if name == 'LT':
        return 'box/clamp' if act else 'box/norm'
    if name == 'edge-swap':
        return 'box/norm' if act else 'box/clamp'
    return STEP_TRUTHS[name]


def inner_band(c):
    """The declared active inner-refraction band (memo D §3: InnerRefraction height min(s/4, 20) pt)."""
    return min(c.span / 4.0, 20.0) if c.active else 0.0


def outer_reach(c):
    """The declared active outer-refraction reach (OuterRefraction height max(16, s/5) pt)."""
    return max(16.0, c.span / 5.0) if c.active else 0.0


def refraction_outside(c):
    """For a split whose step lies outside the shape: its distance (pt) from the shape's edge; else None."""
    if c.bg_spec['kind'] != 'split':
        return None
    cx, cy, w, h, r = G.shape_frame(c.comp_spec)
    pos = c.bg_spec['position']
    gap = max(cx - w / 2 - pos, pos - (cx + w / 2))
    return gap if gap > 0 else None


STEP_PLAN = [('light-inactive', ('LT', 'W-canvas', 'edge-swap', 'W-shape'), True),
             ('light-rest', ('LT', 'W-canvas', 'edge-swap'), False),
             ('dark-inactive', ('LT', 'edge-swap'), False),
             ('dark-rest', ('LT',), False)]


def step_section():
    import os
    out = json.load(open(f'{OUT}.step.json')) if os.path.exists(f'{OUT}.step.json') else []
    done = {(x['ep'], x['truth'], x['mode']) for x in out}
    for ep, truths, free_mode in STEP_PLAN:
        for tname in truths:
            cs = bed.cells(ep, 2, letters=['D'])
            excluded = [dict(cell=k, reason=v) for k, v in bed.refraction_exclusions(ep, 2).items()
                        if k.startswith('d-')]
            p = synth_all(cs, tname, ep)
            modes = [('given', dict(narrow='olaw', kn=p['k'], lam=p['lam'], w=0.5))]
            if tname == 'LT' and free_mode:
                modes.append(('free', dict(narrow='olaw')))
            for mode, kw in modes:
                if (ep, tname, mode) in done:
                    continue
                r = RS.read([(c, None) for c in cs], 'native', shape=(tname == 'W-shape' or mode == 'given'),
                            **kw)
                b = r['best']
                ts = step_truth_support(tname, ep)
                call_ok = r['call'] is None or r['call'] == ts
                sw_t = 8 * p['k']
                sw_true_support = r['fits'][ts]['sw'] if ts in r['fits'] else float('nan')
                rec = dict(ep=ep, truth=tname, mode=mode, truth_support=ts, call=r['call'], call_gap=r['call_gap'],
                           excluded=excluded, cells=[c.id for c in cs],
                           ranking=r['ranking'], rms={k: v['rms'] for k, v in r['fits'].items()},
                           region_ranking=r['region_ranking'], region_gap=r['region_gap'],
                           region={k: (v['region_max'], v['region_where']) for k, v in r['fits'].items()},
                           sw_best=b['sw'], sw_iv=b.get('sw_iv'), sw_true_support=sw_true_support, sw_truth=sw_t,
                           kn=b.get('kn'), lam=b['lam'], w=b['w'], mu=b.get('mu'),
                           mu_scan=r['fits'].get('shape/norm', {}).get('mu_scan'),
                           verdict_support='PASS' if call_ok else 'MISS',
                           verdict_sw='PASS' if rel(sw_true_support, sw_t) <= 0.05 else 'MISS',
                           stats={c.id: RS.statistics(c, c.y) for c in cs[:3]})
                out.append(rec)
                save('step', out)
                print(f"{ep:15s} {tname:9s} {mode:5s} call {r['call']} (truth {ts}) gap {r['call_gap']:.3f} "
                      f"sw@true {sw_true_support:.2f} vs {sw_t:.2f} {rec['verdict_sw']} {rec['verdict_support']} "
                      f"lam {b['lam']:.3f} kn {b.get('kn')} | region rank {r['region_ranking'][:2]} gap {r['region_gap']:.2f}",
                      flush=True)
    return out


# ---------------------------------------------------------------- lam readers
def lam_cells(ep):
    return bed.cells(ep, 2, letters=['B', "B'"])


def identified(r):
    return r['lam'] is not None and (r['hi'] - r['lo'] <= 0.4) and not r['at_bound']


def lambda_section():
    out = []
    for ep in EPS:
        cs = lam_cells(ep)
        p = synth_all(cs, 'LT', ep)
        for c in cs:
            r = RL.per_cell(c, fam('LT'), {'k': p['k']})
            idf = identified(r)
            ok = idf and abs(r['lam'] - p['lam']) <= 0.03 and r['lo'] <= p['lam'] <= r['hi']
            gaps = RL.hinge_gap(c, fam('LT'), {'k': p['k']})
            gap_ok = all(abs(g['lam'] - p['lam']) <= 0.05 for g in gaps
                         if g['lam'] is not None and g['hi'] - g['lo'] <= 0.4)
            out.append(dict(ep=ep, cell=c.id, lam_truth=p['lam'], **r, identified=idf,
                            verdict=('PASS' if ok else 'MISS') if idf else 'not identified',
                            gaps=gaps, verdict_gap='PASS' if gap_ok else 'MISS'))
            if r['lam'] is None:
                print(f"{ep:15s} {c.id:32s} {r['note']}", flush=True)
                continue
            print(f"{ep:15s} {c.id:32s} lam {r['lam']:.3f} [{r['lo']:.2f},{r['hi']:.2f}] "
                  f"{out[-1]['verdict']} gaps {[None if g['lam'] is None else round(g['lam'], 3) for g in gaps]} "
                  f"{out[-1]['verdict_gap']}", flush=True)
    return out


# ---------------------------------------------------------------- U1 diagnostic
U1_TRUTHS = ('LT', 'W-shape', 'W-tails', 'K2', 'W-canvas', 'edge-swap')
U1_IDS = ['b-p2-c16-rrect-md', 'b-p2-c64-rrect-md', 'b-p4-c16-rrect-md', 'b-p4-c64-rrect-md',
          'bp-p1-c32-capsule-button', 'bp-p1-c64-capsule-button']
U1_EXTRA = [('x-p1-c16-capsule-button', "B'", checker(0, 255, 16), 'capsule-button'),
            ('x-p1-c16-rrect-md', "B'", checker(0, 255, 16), 'rrect-md'),
            ('x-p1-c64-rrect-md', "B'", checker(0, 255, 64), 'rrect-md')]


def u1_cells(ep):
    return bed.cells(ep, 2, ids=U1_IDS) + extra_cells(U1_EXTRA, ep)


def lt_pooled_k(cells, lo=1.2, hi=3.2):
    """LT's one k per endpoint pooled over the cells (equal weight per cell), lam inner, with the lam
    readers' model-based trust set (fitting.Problem selects on the observed code, which censors the dark
    knee side at spans >= 96)."""
    lt = fam('LT')

    def inner(k):
        mps = [F.maps(c, lt, F.expand(lt, {'k': k})) for c in cells]
        obs = [RL._obs(c, mp) for c, mp in zip(cells, mps)]

        def mse(lam):
            return [float(np.mean((F.compose(c, lt, mp, lam) - y)[ok] ** 2)) for c, mp, (y, ok)
                    in zip(cells, mps, obs) if ok.sum() >= RL.MIN_BIN_PX]
        lam = FI.golden(lambda v: float(np.mean(mse(v))), *FI.LAM_BOUNDS, tol=2e-4)
        return lam, mse(lam)

    k = FI.golden(lambda v: float(np.mean(inner(v)[1])), lo, hi, tol=2e-4)
    lam, m = inner(k)
    return dict(k=k, lam=lam, pooled=float(np.sqrt(np.mean(m))), max_cell=float(np.sqrt(max(m))))


def u1_section(eps=('light-inactive', 'dark-inactive', 'dark-rest')):
    out = []
    for ep in eps:
        for tname in U1_TRUTHS:
            cs = u1_cells(ep)
            if ep.endswith('rest'):
                cs = [c for c in cs if 'capsule' in c.id]
            synth_all(cs, tname, ep)
            fit = lt_pooled_k(cs)
            k = fit['k']
            rows = []
            for c in cs:
                r = RL.per_cell(c, fam('LT'), {'k': k})
                g = RL.hinge_gap(c, fam('LT'), {'k': k}) if ('c16' in c.id or 'c64' in c.id) else []
                gl = [x['lam'] for x in g if x['lam'] is not None]
                rows.append(dict(cell=c.id, **r, identified=identified(r), gaps=g,
                                 gap_spread=float(max(gl) - min(gl)) if len(gl) > 1 else None))
            by = {r['cell']: r for r in rows}

            def drift(a, b):
                ra, rb = by.get(a), by.get(b)
                if not ra or not rb:
                    return None
                return dict(d=ra['lam'] - rb['lam'], disjoint=bool(ra['hi'] < rb['lo'] or rb['hi'] < ra['lo']))

            pairs = {'capsule P1 p64-p16': drift('2x|bp-p1-c64-capsule-button', '2x|x-p1-c16-capsule-button'),
                     'md P1 p64-p16': drift('2x|x-p1-c64-rrect-md', '2x|x-p1-c16-rrect-md'),
                     'md P2 p64-p16': drift('2x|b-p2-c64-rrect-md', '2x|b-p2-c16-rrect-md'),
                     'md P4 p64-p16': drift('2x|b-p4-c64-rrect-md', '2x|b-p4-c16-rrect-md')}
            rec = dict(ep=ep, truth=tname, k_fit=k, lam_fit=fit['lam'], pooled=fit['pooled'],
                       max_cell=fit['max_cell'], cells=rows, drift=pairs)
            out.append(rec)
            print(f"{ep:15s} truth {tname:9s} LT k {k:.3f} pooled {fit['pooled']:.3f} max {fit['max_cell']:.3f} | " +
                  ' '.join(f"{r['cell'].split('|')[1]}:{r['lam']:.2f}[{r['lo']:.2f},{r['hi']:.2f}]" for r in rows),
                  flush=True)
            print('      drift ' + ' '.join(f"{k_}: {v['d']:+.3f}{'*' if v['disjoint'] else ''}"
                                         for k_, v in pairs.items() if v) +
                  ' | gap spread ' + ' '.join(f"{r['cell'].split('|')[1]}:{r['gap_spread']:.3f}"
                                              for r in rows if r['gap_spread'] is not None), flush=True)
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
        fn = {'patch': patch_section, 'depth': depth_section, 'step': step_section, 'lambda': lambda_section,
              'u1': u1_section}[sec]
        res = fn()
        json.dump(res, open(f'{OUT}.{sec}.json', 'w'), indent=1, default=float)
