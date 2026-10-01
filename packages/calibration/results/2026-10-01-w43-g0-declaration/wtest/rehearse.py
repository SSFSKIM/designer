#!/usr/bin/env python3.12
"""W43 G0 (e): the w-test's three rehearsals, run before the declaration is hashed (charter Design "The w-test").

    python3.12 -B rehearse.py r3      # W42's 0.5 frames: conditioning; writes support.json (fixed at the hash)
    python3.12 -B rehearse.py r1      # synthetic LT at w 0.25 and 0.5: recovery, size, power, lam independence
    python3.12 -B rehearse.py r2      # a two-sided linear control: the free and lifted readings agree

r3 runs first: it fixes the support r1 and r2 read. Outputs beside this file: rehearsal-r{1,2,3}.{txt,json}
and support.json. W42's frames come from w42-archive through its guarded Reader (`w42frames.py`), roles
calibration and validation only.

Both statistics are carried through every rehearsal: `median` (the region median of each channel, inverted:
the declared form) and `mean` (proposal P1: every pixel inverted, then averaged). So are two supports: the
k grid as declared, [1.4, 2.5], and the least-squares span alone, [2.0, 2.25] (proposal P3), as a sensitivity.
"""
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import wtest as W  # noqa: E402
import w42frames as O  # noqa: E402

F, R = W.F, W.R
from tone import TableT, memo_c_T  # noqa: E402

ORDINATES = W.ROOT / 'packages/calibration/results/2026-09-30-w42-g2-identification/step2/native-t/ordinates.json'
# LT's k@global least-squares point and its lam per endpoint (§5.196 §4): the synthetic truth.
K_TRUE = 2.138
LAM50 = {'light-rest': 0.868, 'light-inactive': 0.767, 'dark-rest': 0.851, 'dark-inactive': 0.759}
SEEDS = int(__import__('os').environ.get('W43_WTEST_SEEDS', 40))   # 40 for the record; fewer to scout
STATS = ('median', 'mean')
SUPPORTS = {'declared': W.K_GRID, 'ls-span': W.K_GRID_LS}
SUPPORTS_RUN = [x for x in __import__('os').environ.get('W43_WTEST_SUPPORTS', 'declared,ls-span').split(',')]


def endpoint_cells(ep):
    scheme, pose = ep.split('-')
    p = W.probe()['passes'][f'x0.25/2x-{scheme}-{W.POSE_OF[pose]}']
    return [c for c in p['cells'] if c.startswith('a-')], [c for c in p['cells'] if not c.startswith('a-')]


def level_of(cid):
    return int(cid.split('-')[1][1:])


# ------------------------------------------------------------------------------------- region evaluation

def region_reading(stat, Ts, img, idx):
    if stat == 'median':
        y = W.medians(img, idx)
        inv = W.invert(Ts, y)
        return inv, y, W.Q
    inv = W.invert_pixels(Ts, img, idx)
    y = W.medians(img, idx)
    return inv, y, W.Q / np.sqrt(max(inv['distinct'], 1))


def evaluate(ep, support, img25, img50, T25, T50, stat, side='free'):
    """[{region, status, r, dr, ...}] for the supported regions of one endpoint."""
    scheme = ep.split('-')[0]
    rows = []
    for cid, reg in support.items():
        g = reg.get(side)
        if not g:
            continue
        s = g['stratum']
        idx = np.asarray(g['idx'])
        inv50, y50, q50 = region_reading(stat, T50[s], img50(cid), idx)
        inv25, y25, q25 = region_reading(stat, T25[s], img25(cid), idx)
        if W.censored(y25):
            rows.append(dict(region=f'{cid}:{side}', status='UNMEASURED', reason='censored at 0.25 (X21)'))
            continue
        rr = W.ratio(g['level'], inv25, inv50, q25, q50)
        rows.append(dict(region=f'{cid}:{side}', status='measured', r=rr['r'], dr=rr['dr'], D=rr['D'],
                         rChannels=rr['rChannels']))
    return rows


def grey_tables(ep, greys_img):
    scheme = ep.split('-')[0]
    med = {}
    for cid, img in greys_img.items():
        c = W.cell(ep, cid)
        med.setdefault(W.stratum(c), {})[level_of(cid)] = W.deep_medians(img, c)
    return W.tables(med, scheme)


# ------------------------------------------------------------------------------------------------ r3

def r3():
    out = dict(schema='w43-wtest-rehearsal-3', archiveInventory=O.INVENTORY, constants=constants(), endpoints={})
    support = dict(schema='w43-wtest-support-1', constants=constants(), statistics={})
    lines = ["W43 G0 (e) w-test rehearsal 3: W42's 0.5 frames, every candidate region's conditioning", '',
             'T25 is stood in by T50 for the PREDICTED resolution (slope and interpolation at the predicted M25 = '
             'C + 0.5 (M50 - C)); the 0.25 region term at the median floor, or the per-pixel term at half the 0.5 '
             "region's distinct codes.", '']
    for ep in W.ENDPOINTS:
        scheme, pose = ep.split('-')
        greys, structured = endpoint_cells(ep)
        T50 = grey_tables(ep, {cid: O.observed(scheme, pose, cid)[0] for cid in greys})
        e = out['endpoints'].setdefault(ep, {})
        for sup_name, kg in SUPPORTS.items():
            for cid in structured:
                regs, why = W.side_regions(ep, cid, kg)
                c = W.cell(ep, cid)
                s = W.stratum(c)
                img, row = O.observed(scheme, pose, cid)
                for side in ('free', 'lifted'):
                    g = regs[side]
                    rec = dict(cell=cid, side=side, support=sup_name, level=g['level'], stratum=s,
                               pixels=g['pixels'], populationPixels=g['populationPixels'],
                               atLevelPixels=g['atLevelPixels'], frameStates=row['states'])
                    reasons = []
                    if g['pixels'] < W.MIN_PX:
                        reasons.append(f"{g['pixels']} px after the model conditions (C at level over the k grid: "
                                       f"{g['atLevelPixels']} px; |W - C| >= {W.MIN_W_CONTRAST:g} over it too)")
                    else:
                        y = W.medians(img, g['idx'])
                        rec['y50'] = y
                        if W.censored(y):
                            reasons.append(f'the 0.5 median is censored (X21): {y}')
                        for stat in STATS:
                            inv50, _, q50 = region_reading(stat, T50[s], img, g['idx'])
                            D = inv50['M'] - g['level']
                            if stat == 'mean':
                                q25 = W.Q / np.sqrt(max(inv50['distinct'] // 2, 1))
                            else:
                                q25 = W.Q
                            pred_c = [g['level'] + 0.5 * (m - g['level']) for m in inv50['Mc']]
                            p25 = W.invert(T50[s], [T50[s][ch](pred_c[ch]) for ch in range(3)])
                            rr = W.ratio(g['level'], p25, inv50, q25, q50)
                            rec[stat] = dict(M50=inv50['M'], D=D, slope=inv50['slope'], interp=inv50['interp'],
                                             predictedDr=rr['dr'], distinct=inv50.get('distinct'))
                        if scheme == 'dark' and s >= 96 and rec['median']['M50'] > W.DARK_T_TOP:
                            reasons.append(f"inverted M50 {rec['median']['M50']:.1f} above {W.DARK_T_TOP:g} at "
                                           's >= 96 in dark: T is not monotone there')
                        if abs(rec['median']['D']) < W.MIN_EXCURSION:
                            reasons.append(f"|M50 - C| = {abs(rec['median']['D']):.1f} < {W.MIN_EXCURSION:g}")
                    rec['excludedBeforeTheRead'] = reasons
                    for stat in STATS:
                        if stat in rec:
                            rec[stat]['supported'] = not reasons and rec[stat]['predictedDr'] <= W.DR_MAX
                            if not reasons and not rec[stat]['supported']:
                                rec[stat]['reason'] = (f"predicted dr {rec[stat]['predictedDr']:.3f} > "
                                                       f'{W.DR_MAX:g}')
                    e.setdefault(sup_name, []).append(rec)
                    if side == 'free':
                        for stat in STATS:
                            if stat in rec and rec[stat]['supported']:
                                support['statistics'].setdefault(stat, {}).setdefault(sup_name, {}).setdefault(
                                    ep, {})[cid] = dict(free=dict(level=g['level'], stratum=s, pixels=g['pixels'],
                                                                  idxSha256=idx_sha(g['idx']),
                                                                  predictedDr=round(rec[stat]['predictedDr'], 4)))
                    if side == 'lifted' and not reasons:
                        for stat in STATS:
                            sup = support['statistics'].setdefault(stat, {}).setdefault(sup_name, {}).setdefault(ep, {})
                            sup.setdefault(cid, {})['lifted'] = dict(level=g['level'], stratum=s, pixels=g['pixels'],
                                                                     idxSha256=idx_sha(g['idx']),
                                                                     reported='never gated')
        for sup_name in SUPPORTS:
            lines.append(f'== {ep} ({sup_name} support, k in {list(SUPPORTS[sup_name])})')
            for rec in e[sup_name]:
                if rec['side'] != 'free':
                    continue
                head = f"  {rec['cell']:26s} free C {rec['level']:5.1f} {rec['pixels']:6d} px"
                if rec['excludedBeforeTheRead']:
                    lines.append(head + '  EXCLUDED: ' + '; '.join(rec['excludedBeforeTheRead']))
                    continue
                parts = [f"{st}: D {rec[st]['D']:+6.1f} dr {rec[st]['predictedDr']:.3f}"
                         + (' SUPPORTED' if rec[st]['supported'] else '') for st in STATS]
                lines.append(head + '  ' + ' | '.join(parts))
            for stat in STATS:
                n = sum(1 for rec in e[sup_name] if rec['side'] == 'free' and rec.get(stat, {}).get('supported'))
                lines.append(f'  -> {stat}: {n} supported free-side region(s)')
            lines.append('')
    (HERE / 'rehearsal-r3.json').write_text(json.dumps(out, indent=1, default=float) + '\n')
    (HERE / 'support.json').write_text(json.dumps(support, indent=1, sort_keys=True) + '\n')
    (HERE / 'rehearsal-r3.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


def constants():
    return dict(kGrid=list(W.K_GRID), kGridLs=list(W.K_GRID_LS), cTol=W.C_TOL, minWContrast=W.MIN_W_CONTRAST,
                minPx=W.MIN_PX, censor=[W.CENSOR_LO, W.CENSOR_HI], darkTTop=W.DARK_T_TOP, q=W.Q, ord=W.ORD,
                minExcursion=W.MIN_EXCURSION, drMax=W.DR_MAX, greyLevels=sorted({level_of(c) for c in
                                                                                  endpoint_cells('light-rest')[0]}))


# ------------------------------------------------------------------------------------------- synthetic

class ChannelT:
    """A per-channel transfer for the forward engine: M codes (n, 3) -> y codes, channel c through tabs[c]."""

    def __init__(self, tabs):
        self.tabs, self.trust_below = tabs, None

    def __call__(self, M):
        M = np.asarray(M, float)
        if M.ndim == 2:
            return np.stack([self.tabs[c](M[:, c]) for c in range(3)], 1)
        return np.stack([self.tabs[c](M) for c in range(3)], -1)


def native_truth(ep):
    """The measured 0.5 native T per stratum and channel (W42 G2 step 2's ordinates, ten levels)."""
    d = json.loads(ORDINATES.read_text())['endpoints'][ep]['ordinates']
    out = {}
    for s_key, s in (('64', 0), ('96', 96)):
        tabs = []
        for ch in 'RGB':
            pts = sorted((int(L), float(v)) for L, v in d[ch][s_key].items())
            tabs.append(TableT([p[0] for p in pts], [p[1] for p in pts]))
        out[s] = ChannelT(tabs)
    return out


def memo_c_truth(ep):
    return {s: ChannelT([memo_c_T(ep, 44 if s == 0 else 96)] * 3) for s in (0, 96)}


def variant(T, ep, kind):
    """A 0.25 transfer derived from a 0.5 one. 'same'; 'fill' (light: the white face fill's alpha 0.2 -> 0.1,
    y = 0.9 A + 25.5 with A = (T - 51) / 0.8); 'compress' (dark: highs compressed by up to 15 %)."""
    if kind == 'same':
        return T
    out = {}
    for s, ct in T.items():
        tabs = []
        for tab in ct.tabs:
            xs = np.linspace(0, 255, 256)
            ys = tab(xs)
            if kind == 'fill':
                ys = 0.9 * (ys - 51.0) / 0.8 + 25.5
            elif kind == 'compress':
                lo, hi = ys.min(), ys.max()
                u = (ys - lo) / max(hi - lo, 1e-9)
                ys = lo + (ys - lo) * (1 - 0.15 * u)
            tabs.append(TableT(xs, ys))
        out[s] = ChannelT(tabs)
    return out


def render(ep, cid, w, lam, T):
    """LT's float output codes on the cell's deep mask (n, 3), at the truth k."""
    c = W.cell(ep, cid)
    F.WN = w
    try:
        fam = F.Family()
        return c, F.render(c, fam, F.expand(fam, {'k': K_TRUE, 'lam': lam}), T[W.stratum(c)])
    finally:
        F.WN = 0.5


def quantise(c, y, rng):
    """Rounded codes with a per-pixel dither AND one phase offset common to the whole cell, uniform in +-0.5:
    the capture is deterministic, so what is unknown is where the true value sits on the integer grid, not
    pixel noise. Without the common phase every seed would round to the same medians."""
    img = np.full(c.d.shape + (3,), np.nan)
    phase = rng.uniform(-0.5, 0.5)
    img[c.mask] = np.clip(np.round(y + phase + rng.uniform(-0.5, 0.5, y.shape)), 0, 255)
    return img


def synth_greys(ep, greys, T, rng):
    out = {}
    for cid in greys:
        c = W.cell(ep, cid)
        L = level_of(cid)
        t = T[W.stratum(c)](np.array([[L, L, L]], float))[0]
        n = int(c.mask.sum())
        img = np.full(c.d.shape + (3,), np.nan)
        phase = rng.uniform(-0.5, 0.5)      # where the uniform grey's true value sits on the integer grid
        img[c.mask] = np.clip(np.round(t[None, :] + phase + rng.uniform(-0.5, 0.5, (n, 3))), 0, 255)
        out[cid] = img
    return out


def idx_sha(idx):
    """A region's pixel set, named by the SHA-256 of its sorted flat canvas indices (int64, little-endian)."""
    import hashlib
    return hashlib.sha256(np.asarray(sorted(int(v) for v in idx), '<i8').tobytes()).hexdigest()


def load_support(stat, sup_name):
    """support.json names each region's pixels by hash; they are regenerated from the declared rule
    (`wtest.side_regions` at the support's k grid) and refused unless they hash as recorded."""
    d = json.loads((HERE / 'support.json').read_text())['statistics'].get(stat, {}).get(sup_name, {})
    out = {}
    for ep, cells in d.items():
        for cid, reg in cells.items():
            if 'idx' in next(iter(reg.values())):
                out.setdefault(ep, {})[cid] = {k: dict(v, idx=np.asarray(v['idx'])) for k, v in reg.items()}
                continue
            regs, _ = W.side_regions(ep, cid, SUPPORTS[sup_name])
            for side, v in reg.items():
                idx = regs[side]['idx']
                if idx_sha(idx) != v['idxSha256']:
                    raise SystemExit(f'{ep} {cid} {side}: the regenerated region is not the recorded one')
                out.setdefault(ep, {}).setdefault(cid, {})[side] = dict(v, idx=idx)
    return out


def scenario(ep, support, T50t, T25t, w25, lam25, seeds, stat, side='free', lam50=None):
    greys, structured = endpoint_cells(ep)
    cells = [cid for cid in structured if cid in support]
    lam50 = LAM50[ep] if lam50 is None else lam50
    y50 = {cid: render(ep, cid, 0.5, lam50, T50t) for cid in cells}
    y25 = {cid: render(ep, cid, w25, lam25, T25t) for cid in cells}
    results = []
    for seed in range(seeds):
        rng = np.random.default_rng(seed)
        T50 = grey_tables(ep, synth_greys(ep, greys, T50t, rng))
        T25 = grey_tables(ep, synth_greys(ep, greys, T25t, rng))
        i50 = {cid: quantise(*y50[cid], rng) for cid in cells}
        i25 = {cid: quantise(*y25[cid], rng) for cid in cells}
        rows = evaluate(ep, {cid: support[cid] for cid in cells}, i25.get, i50.get, T25, T50, stat, side)
        results.append(rows)
    return results


def summarise(results, r_true):
    v = [W.verdict(rows, 0.5) for rows in results]
    flat = [x for rows in results for x in rows if x['status'] == 'measured']
    if not flat:
        return dict(regions=0)
    err = np.array([x['r'] - r_true for x in flat])
    z = np.array([abs(x['r'] - r_true) / x['dr'] for x in flat])
    return dict(regions=len(results[0]), passRate=float(np.mean([x['verdict'] == 'PASS' for x in v])),
                rMedian=float(np.median([x['r'] for x in flat])), errMaxAbs=float(np.abs(err).max()),
                errRms=float(np.sqrt(np.mean(err ** 2))), drMedian=float(np.median([x['dr'] for x in flat])),
                zMax=float(z.max()), z99=float(np.quantile(z, 0.99)))


def emit(lines, text):
    lines.append(text)
    print(text, flush=True)


def r1():
    lines = ['W43 G0 (e) w-test rehearsal 1: synthetic LT at the truth k 2.138 and W42\'s lam50 per endpoint, '
             f'{SEEDS} seeds a scenario, quantised (uniform +-0.5, then rounded), the T tables rebuilt from the '
             'synthetic greys at the seven probe levels.', '',
             'passRate is the share of seeds whose verdict at r_pred = 0.5 is PASS: under the null it is 1 - size, '
             'under an alternative 1 - power. z = |r - r_true| / dr per region (dr honest if z stays below 1).', '']
    out = dict(schema='w43-wtest-rehearsal-1', seeds=SEEDS, kTrue=K_TRUE, lam50=LAM50, scenarios=[])
    for stat in STATS:
        for sup_name in SUPPORTS_RUN:
            sup = load_support(stat, sup_name)
            for ep in W.ENDPOINTS:
                scheme = ep.split('-')[0]
                s_ep = sup.get(ep, {})
                s_ep = {cid: v for cid, v in s_ep.items() if 'free' in v}
                if not s_ep:
                    lines.append(f'{stat:6s} {sup_name:8s} {ep:15s} no supported region')
                    continue
                truths = [('native', native_truth(ep)), ('memoC', memo_c_truth(ep))]
                kinds = ('same', 'fill') if scheme == 'light' else ('same', 'compress')
                lam_variants = {'ratio': LAM50[ep] * 0.875, 'difference': LAM50[ep] - 0.1125, 'wild-low': 0.2,
                                'wild-high': 1.3}
                for tname, T50t in truths:
                    for kind in kinds:
                        T25t = variant(T50t, ep, kind)
                        for w25, label in ((0.25, 'null r=0.5'), (0.35, 'alt r=0.7'), (0.5, 'alt r=1.0')):
                            lam_list = lam_variants.items() if label.startswith('null') else [('ratio', LAM50[ep] * 0.875)]
                            per_lam = {}
                            for lname, lam25 in lam_list:
                                res = scenario(ep, s_ep, T50t, T25t, w25, lam25, SEEDS, stat)
                                per_lam[lname] = res
                                sm = summarise(res, w25 / 0.5)
                                rec = dict(statistic=stat, support=sup_name, endpoint=ep, truthT=tname, t25=kind,
                                           w25=w25, label=label, lam25=lname, **sm)
                                out['scenarios'].append(rec)
                                emit(lines, f"{stat:6s} {sup_name:8s} {ep:15s} T {tname:6s}/{kind:8s} {label:10s} "
                                             f"lam25 {lname:10s} regions {sm['regions']:2d} pass {sm['passRate']:.3f} "
                                             f"r~ {sm['rMedian']:.3f} |err|max {sm['errMaxAbs']:.3f} dr~ "
                                             f"{sm['drMedian']:.3f} z99 {sm['z99']:.2f} zmax {sm['zMax']:.2f}")
                            if len(per_lam) > 1:
                                base = per_lam['ratio']
                                diff = max(abs(a['r'] - b['r']) for name, res in per_lam.items() for rs, rb in
                                           zip(res, base) for a, b in zip(rs, rb) if a['status'] == b['status'] == 'measured')
                                out['scenarios'].append(dict(statistic=stat, support=sup_name, endpoint=ep, truthT=tname,
                                                             t25=kind, lamIndependence=diff))
                                emit(lines, f"{'':6s} {'':8s} {ep:15s} free-side r moves by at most {diff:.2e} across "
                                             'lam25 in {ratio, difference, 0.2, 1.3}')
    (HERE / 'rehearsal-r1.json').write_text(json.dumps(out, indent=1) + '\n')
    (HERE / 'rehearsal-r1.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


def r2():
    """A two-sided linear control: lam = 0 at both positions (no hinge), so M - C = w (W - C) on both sides and
    the free and lifted readings must agree; then the hinge restored, where the lifted side reads
    (w25 + lam25 (1 - w25)) / (w50 + lam50 (1 - w50)) and lam25 is recovered from it."""
    lines = ['W43 G0 (e) w-test rehearsal 2: the two-sided linear control, and the lifted-side reading', '']
    out = dict(schema='w43-wtest-rehearsal-2', seeds=SEEDS, rows=[])
    for stat in STATS:
        sup = load_support(stat, 'declared')
        for ep in W.ENDPOINTS:
            s_ep = sup.get(ep, {})
            if not s_ep:
                continue
            T = native_truth(ep)
            free = [cid for cid, v in s_ep.items() if 'free' in v]
            lifted = [cid for cid, v in s_ep.items() if 'lifted' in v]
            for lam50, lam25, label in ((0.0, 0.0, 'two-sided linear (lam 0)'),
                                        (LAM50[ep], LAM50[ep] * 0.875, 'hinge, lam25 = 0.875 lam50')):
                rf = scenario(ep, {c: s_ep[c] for c in free}, T, T, 0.25, lam25, SEEDS, stat, 'free', lam50)
                rl = scenario(ep, {c: s_ep[c] for c in lifted}, T, T, 0.25, lam25, SEEDS, stat, 'lifted', lam50)
                ff = [x['r'] for rows in rf for x in rows if x['status'] == 'measured']
                ll = [x for rows in rl for x in rows if x['status'] == 'measured']
                lr = [x['r'] for x in ll]
                expect = (0.25 + lam25 * 0.75) / (0.5 + lam50 * 0.5)
                lam_hat = [(x * (0.5 + lam50 * 0.5) - 0.25) / 0.75 for x in lr]
                row = dict(statistic=stat, endpoint=ep, label=label, freeMedian=float(np.median(ff)) if ff else None,
                           liftedMedian=float(np.median(lr)) if lr else None, liftedExpected=expect,
                           liftedWithinDr=float(np.mean([abs(x['r'] - expect) <= x['dr'] for x in ll])) if ll else None,
                           lam25Recovered=float(np.median(lam_hat)) if lam_hat else None, lam25True=lam25,
                           freeRegions=len(free), liftedRegions=len(lifted))
                out['rows'].append(row)
                lines.append(f"{stat:6s} {ep:15s} {label:28s} free r~ {row['freeMedian']} | lifted r~ "
                             f"{row['liftedMedian']} (expected {expect:.4f}; within dr {row['liftedWithinDr']}) | "
                             f"lam25 recovered {row['lam25Recovered']} (true {lam25:.4f}); regions {len(free)} / {len(lifted)}")
    (HERE / 'rehearsal-r2.json').write_text(json.dumps(out, indent=1) + '\n')
    (HERE / 'rehearsal-r2.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    {'r1': r1, 'r2': r2, 'r3': r3}[sys.argv[1]]()
