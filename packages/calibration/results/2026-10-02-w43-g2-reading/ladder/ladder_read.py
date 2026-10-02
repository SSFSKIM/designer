#!/usr/bin/env python3.12
"""W43 G2 stage two (d): the ladder, described (charter clause 9; item ladderReadings of declaration 4f90f910...).

    python3.12 -B ladder_read.py     # writes ladder.json and ladder.txt beside itself

Descriptive: no fit is claimed and no gate reads it. Read after the w-test's read was committed
(`../wtest/read-plan.md` §2 states what is computed here; `../wtest/reading.json` is the w-test and is
not amended). The functions are the declaration's (`wtest.py`, `rehearse.py`), imported unchanged; the
frames are the w-test's: G1b's ladder and probe passes from the verified `w43-archive-g1b` copy, the
plurality of each cell's three normal runs, and W42's seven-run 0.5 counterparts through its guarded Reader
(re-extracted by `../wtest/wtest_read.py` into scratch outside the repository, each the frame G0 read).
"""

from __future__ import annotations

import gzip
import importlib.util
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EVID = HERE.parent
RESULTS = EVID.parent
G1B = RESULTS / '2026-10-02-w43-g1b-sitting'
spec = importlib.util.spec_from_file_location('wtest_read_g2', EVID / 'wtest' / 'wtest_read.py')
WR = importlib.util.module_from_spec(spec)
spec.loader.exec_module(WR)
W, RH, O = WR.W, WR.RH, WR.O

POSITIONS = ('0', '0.25', '0.5', '0.75', '1')
PASS_PREFIX = {'0': 'ladder-0-', '0.25': 'probe-0.25-', '0.75': 'ladder-0.75-', '1': 'ladder-1-'}
FIVE = [('0', 'dark', 'inactive', 'b-p3-c64-rrect-md'), ('0', 'light', 'inactive', 'a-g128-rrect-md'),
        ('0', 'light', 'inactive', 'c-s32-hi-rrect-md'), ('0.75', 'dark', 'rest', 'a-g000-capsule-button'),
        ('0.75', 'light', 'inactive', 'a-g128-rrect-md')]


def fmt(v, spec='+.1f'):
    return '—' if v is None or (isinstance(v, float) and math.isnan(v)) else format(v, spec)


CONTROL_SIGMAS = (10.0, 20.0, 40.0)   # device px: the linear control's blur widths
MIRROR_CONTROL_TOL = 0.05             # a cell's control |m| must stay within this at every sigma


def linear_control(ep, cid, regs):
    """The mirror a plain linear blur gives on this cell's own declared regions (review closure, §5.200b §7).

    e = W - C on each side, with W the Gaussian blur of the background raster's encoded luma and C the side's
    level, medians over the region. A cell whose two regions are a complementary pair reads 0 here at every
    sigma; one that is not (a patch core against its ring) reads geometry as one-sidedness, so it is kept out
    of the mirror's aggregate.
    """
    from scipy.ndimage import gaussian_filter
    cl = W.cell(ep, cid, rgb=False)
    level = W.G.luma(W.G.render_background(cl.bg_spec, 2).astype(np.float64))
    out = {}
    for sigma in CONTROL_SIGMAS:
        wide = gaussian_filter(level, sigma, mode='nearest').reshape(-1)
        e = {side: float(np.median(wide[regs[side]['idx']] - regs[side]['level'])) for side in ('free', 'lifted')}
        den = abs(e['free']) + abs(e['lifted'])
        out[f'{sigma:g}'] = (e['free'] + e['lifted']) / den if den > 1e-9 else None
    return out


class Frames:
    """Cell images at every position, by plurality; 0.5 from W42's re-extracted counterparts."""

    def __init__(self):
        self.archive = WR.G1bArchive()
        O.SCRATCH = WR.SCRATCH / 'observed-0.5'
        if not (O.SCRATCH / 'index.json').exists():
            WR.w42_counterparts()
        self.cache = {}

    def cells(self, ep, x):
        scheme, pose = ep.split('-')
        key = f'x{0.25 if x == "0.5" else x}/2x-{scheme}-{W.POSE_OF[pose]}'
        return W.probe()['passes'][key]['cells']

    def meta(self, ep, x, cid):
        scheme, pose = ep.split('-')
        if x == '0.5':
            row = json.loads((O.SCRATCH / 'index.json').read_text())['cells'][f'{O.profile(scheme)}/{cid}__{pose}']
            return dict(frame=row['frame'], runs=row['runs'], states=row['states'], plurality=row['plurality'])
        return self.archive.plurality(x, scheme, cid, pose, PASS_PREFIX[x])

    def image(self, ep, x, cid):
        key = (ep, x, cid)
        if key not in self.cache:
            scheme, pose = ep.split('-')
            if x == '0.5':
                self.cache[key] = O.observed(scheme, pose, cid)[0]
            else:
                self.cache[key] = self.archive.image(self.meta(ep, x, cid)['frame'])
        return self.cache[key]


def deep(img, c):
    return W.deep_medians(img, c)


def step_profile(img, c):
    """Columns across a vertical step: per column, the median over the deep mask's rows of the mean channel
    (codes); the plateaus far from the step; the 10-90 % transition width in device px."""
    mask = c.mask.reshape(img.shape[:2])
    luma = img.mean(axis=2)
    cols = np.flatnonzero(mask.any(axis=0))
    prof = np.array([np.median(luma[mask[:, j], j]) for j in cols])
    step = c.bg_spec['position'] * c.scale
    left = prof[cols < step - 24]
    right = prof[cols > step + 24]
    if left.size == 0 or right.size == 0:
        return None
    a, b = float(np.median(left)), float(np.median(right))
    if abs(b - a) < 1:
        return dict(left=a, right=b, width=None)
    frac = (prof - a) / (b - a)
    near = (cols > step - 80) & (cols < step + 80)
    c10 = cols[near][np.argmax(frac[near] >= 0.1)]
    c90 = cols[near][np.argmax(frac[near] >= 0.9)]
    return dict(left=a, right=b, width=float(c90 - c10), stepPx=float(step))


def main() -> None:
    frames = Frames()
    reading = json.loads((EVID / 'wtest' / 'reading.json').read_text())
    support = RH.load_support('median', 'declared')
    bar = {row['cell']: row for row in json.loads(gzip.decompress((G1B / 'bar' / 'bar.json.gz').read_bytes()))['rows']}
    out: list[str] = []
    say = out.append
    record: dict = {'schema': 'w43-g2-ladder-1', 'T': {}, 'sides': {}, 'mirror': {}, 'steps': {}, 'five': [],
                    'consistency': []}
    say('# W43 G2 stage two (d): the ladder, described (clause 9). No fit, no gate.')
    say('')
    say('Positions x = 0, 0.25, 0.5 (W42), 0.75, 1, all 2x. Codes are encoded sRGB. Memo F: at x = 1 the backdrop')
    say('capture scale is 0.125 on every shape (0.5 below 1), so W itself moves between 0.75 and 1.')
    say('')

    # 1. T(x): the greys' deep medians per stratum, level and position
    tables = {}
    say('## 1. T(x): the greys\' deep medians (mean of R, G, B; channel spread in brackets where > 1 code)')
    for ep in W.ENDPOINTS:
        scheme = ep.split('-')[0]
        say(f'### {ep}')
        tables[ep] = {}
        rows = {}
        for x in POSITIONS:
            greys = {}
            for cid in frames.cells(ep, x):
                if not cid.startswith('a-'):
                    continue
                c = W.cell(ep, cid)
                med = deep(frames.image(ep, x, cid), c)
                greys.setdefault(W.stratum(c), {})[int(cid.split('-')[1][1:])] = med
                rows.setdefault((W.stratum(c), int(cid.split('-')[1][1:])), {})[x] = med
            tables[ep][x] = W.tables(greys, scheme)
        say(f'  {"stratum level":<14}' + ''.join(f'{"x=" + x:>16}' for x in POSITIONS))
        for (s, level), by_x in sorted(rows.items()):
            cells = []
            for x in POSITIONS:
                m = by_x.get(x)
                if m is None:
                    cells.append(f'{"·":>16}')
                    continue
                spread = max(m) - min(m)
                cells.append(f'{np.mean(m):>11.1f}' + (f' [{spread:3.0f}]' if spread > 1 else '     '))
            say(f'  s{s:<3} {level:>4}     ' + ''.join(cells))
            record['T'].setdefault(ep, {})[f's{s}/{level}'] = {x: by_x[x] for x in by_x}
        say('')

    # 2. the free and lifted sides against x, and the mirror
    say('## 2. The two sides against x: e(x) = M_x - C (codes, pre-tone), r(x) = e(x) / e(0.5), and the affine line')
    say('   through x = 0 and 1. "*" marks a region of the w-test\'s support (free side). The composite predicts')
    say('   r(x) = 2x on the free side; the lifted side carries the hinge (lam) as well.')
    for ep in W.ENDPOINTS:
        scheme = ep.split('-')[0]
        say(f'### {ep}')
        sup = support.get(ep, {})
        _, structured = RH.endpoint_cells(ep)
        for cid in structured:
            regs, why = W.side_regions(ep, cid)
            if regs is None:
                continue
            c = W.cell(ep, cid)
            s = W.stratum(c)
            line = {}
            for side in ('free', 'lifted'):
                g = regs[side]
                if g['pixels'] < W.MIN_PX:
                    continue
                es = {}
                for x in POSITIONS:
                    if cid not in frames.cells(ep, x):
                        continue
                    y = W.medians(frames.image(ep, x, cid), g['idx'])
                    T = tables[ep][x].get(s)
                    if T is None:
                        continue
                    inv = W.invert(T, y)
                    flag = 'censored' if W.censored(y) else ''
                    if scheme == 'dark' and s >= 96 and inv['M'] > W.DARK_T_TOP:
                        flag = 'above 208'
                    es[x] = dict(e=inv['M'] - g['level'], y=y, flag=flag)
                line[side] = es
                # A flagged reading (censored, X21; or dark T above 208 at s >= 96) is no reading of M, so it
                # leaves every derived statistic and not only the display (review closure, §5.200b §7).
                ok = {x: v for x, v in es.items() if not v['flag']}
                e05 = ok.get('0.5', {}).get('e')
                r = {x: (v['e'] / e05 if (e05 and abs(e05) >= 1 and x in ok) else None) for x, v in es.items()}
                aff = None
                if '0' in ok and '1' in ok:
                    e0, e1 = ok['0']['e'], ok['1']['e']
                    res = {x: ok[x]['e'] - (e0 + float(x) * (e1 - e0)) for x in ok if x not in ('0', '1')}
                    aff = dict(intercept=e0, slope=e1 - e0, residuals=res,
                               worst=max(res.items(), key=lambda kv: abs(kv[1])) if res else None)
                star = '*' if side == 'free' and 'free' in sup.get(cid, {}) else ' '
                say(f'  {star}{cid:<26} {side:<6} {g["pixels"]:>5} px  e: '
                    + ' '.join(f'{x}:{fmt(v["e"])}{"!" if v["flag"] else ""}' for x, v in es.items())
                    + '   r: ' + ' '.join(f'{x}:{fmt(v, ".3f")}' for x, v in r.items())
                    + (f'   line e(0) {aff["intercept"]:+.1f} slope {aff["slope"]:+.1f}, worst residual '
                       f'{aff["worst"][1]:+.1f} at x={aff["worst"][0]}' if aff and aff['worst'] else ''))
                record['sides'].setdefault(ep, {}).setdefault(cid, {})[side] = dict(
                    pixels=g['pixels'], level=g['level'], e=es, r=r, affine=aff, supported=star == '*')
                if star == '*' and '0.25' in es:
                    # consistency with the w-test's own reading at 0.25 (not a second read)
                    w = next((row for row in reading['endpoints'][ep]['free'] if row['region'] == f'{cid}:free'), None)
                    if w is not None and w.get('status') == 'measured':
                        record['consistency'].append(dict(endpoint=ep, region=cid, ladderR=r.get('0.25'),
                                                          wtestR=w['r'], same=abs((r.get('0.25') or 0) - w['r']) < 1e-12))
            if 'free' in line and 'lifted' in line:
                m = {}
                for x in POSITIONS:
                    if x in line['free'] and x in line['lifted']:
                        if line['free'][x]['flag'] or line['lifted'][x]['flag']:
                            m[x] = None
                            continue
                        ef, el = line['free'][x]['e'], line['lifted'][x]['e']
                        den = abs(ef) + abs(el)
                        m[x] = (ef + el) / den if den >= 2 else None
                control = linear_control(ep, cid, regs)
                admitted = all(v is not None and abs(v) <= MIRROR_CONTROL_TOL for v in control.values())
                record['mirror'].setdefault(ep, {})[cid] = dict(m=m, control=control, admitted=admitted)
        say('')

    say('## 3. The mirror m = (e_free + e_lifted) / (|e_free| + |e_lifted|) per two-level cell, +-1 fully one-sided.')
    say('   It reads 0 for a two-sided linear system only where the two regions are a complementary pair, so each')
    say('   cell is first read under a LINEAR CONTROL: its own declared regions, e = W - C with W a plain Gaussian')
    say('   blur of its background raster (encoded luma) at sigma ' + ', '.join(f'{v:g}' for v in CONTROL_SIGMAS)
        + f' device px. A cell enters the aggregate only if')
    say(f'   its control |m| <= {MIRROR_CONTROL_TOL:g} at every sigma, and a flagged reading (censored, or dark T above')
    say('   208) leaves the mirror at its x (review closure, §5.200b §7).')
    for ep in W.ENDPOINTS:
        say(f'### {ep}')
        cells = record['mirror'].get(ep, {})
        for cid, v in sorted(cells.items()):
            say(f'  {"IN " if v["admitted"] else "out"} {cid:<26} control '
                + ' '.join(f's{sg}:{fmt(c, "+.3f")}' for sg, c in v['control'].items())
                + '   reading ' + ' '.join(f'x={x}:{fmt(mv, "+.3f")}' for x, mv in v['m'].items()))
        per_x = {x: [v['m'][x] for v in cells.values() if v['admitted'] and v['m'].get(x) is not None]
                 for x in POSITIONS}
        say('  median over the admitted cells: ' + '  '.join(
            f'x={x}: {fmt(float(np.median(v)) if v else None, "+.3f")} (n {len(v)})' for x, v in per_x.items()))
    say('')

    say('## 3b. The lifted side at x = 0: the hinge alone. Under LT e_lifted(x) = (x + lam(x)(1 - x))(W - C), so')
    say('   lam(0) = e(0) / e(1) if W is the same at 0 and 1 (it is not exactly: memo F\'s 0.125 capture scale at')
    say('   x = 1), and lam(0) = r(0) (0.5 + 0.5 lam50) through W42\'s fitted lam50. Declared lam(0) = 0.675.')
    lam50 = W.LAM50_FITTED
    for ep in W.ENDPOINTS:
        via1, via05 = [], []
        for cid, sides in record['sides'].get(ep, {}).items():
            lift = sides.get('lifted')
            if not lift or '0' not in lift['e'] or lift['e']['0']['flag']:
                continue
            e0 = lift['e']['0']['e']
            if '1' in lift['e'] and not lift['e']['1']['flag'] and abs(lift['e']['1']['e']) >= 12:
                via1.append(e0 / lift['e']['1']['e'])
            if (lift['r'].get('0') is not None and '0.5' in lift['e'] and not lift['e']['0.5']['flag']
                    and abs(lift['e']['0.5']['e']) >= 12):
                via05.append(lift['r']['0'] * (0.5 + 0.5 * lam50[ep]))
        record.setdefault('lam0', {})[ep] = dict(via1=via1, via05=via05)
        say(f'  {ep:<15} via x = 1: median {fmt(float(np.median(via1)) if via1 else None, ".3f")} '
            f'[{fmt(min(via1) if via1 else None, ".3f")}, {fmt(max(via1) if via1 else None, ".3f")}] (n {len(via1)});  '
            f'via x = 0.5: median {fmt(float(np.median(via05)) if via05 else None, ".3f")} '
            f'[{fmt(min(via05) if via05 else None, ".3f")}, {fmt(max(via05) if via05 else None, ".3f")}] (n {len(via05)})')
    say('')
    say('## 3c. The free side against x, per endpoint: median r(x) over the cells whose |e(0.5)| >= 12 codes')
    say('   (predicted 2x: 0, 0.5, 1, 1.5, 2), and the worst |residual| from the line through x = 0 and 1. A flagged')
    say('   reading ("!" above) leaves all of it: no r at its x, no line where x = 0 or 1 is flagged, no residual.')
    for ep in W.ENDPOINTS:
        rs = {x: [] for x in POSITIONS}
        worst = []
        for cid, sides in record['sides'].get(ep, {}).items():
            free = sides.get('free')
            if not free or abs(free['e'].get('0.5', {}).get('e', 0)) < 12:
                continue
            for x, v in free['r'].items():
                # a censored or out-of-table reading (X21; dark T above 208) is no reading of M
                if v is not None and not free['e'][x]['flag']:
                    rs[x].append(v)
            if free['affine'] and free['affine']['worst']:
                worst.append(abs(free['affine']['worst'][1]))
        record.setdefault('freeSummary', {})[ep] = dict(r={x: v for x, v in rs.items()}, worstResidual=worst)
        say(f'  {ep:<15} ' + '  '.join(f'x={x}: {fmt(float(np.median(v)) if v else None, ".3f")} (n {len(v)})'
                                       for x, v in rs.items())
            + f'   worst residual {fmt(max(worst) if worst else None, ".1f")} codes')
    say('')

    say('## 4. The step cells across the step: plateaus (codes) and the 10-90 % transition width (device px)')
    for ep in W.ENDPOINTS:
        _, structured = RH.endpoint_cells(ep)
        for cid in [c for c in structured if c.startswith('d-')]:
            c = W.cell(ep, cid)
            parts = []
            for x in POSITIONS:
                if cid not in frames.cells(ep, x):
                    continue
                p = step_profile(frames.image(ep, x, cid), c)
                record['steps'].setdefault(ep, {}).setdefault(cid, {})[x] = p
                if p:
                    parts.append(f'x={x}: {p["left"]:.0f}->{p["right"]:.0f} w {fmt(p["width"], ".0f")}')
            say(f'  {ep:<15} {cid:<22} ' + '; '.join(parts))
    say('')

    say('## 5. The five two-state cells of G1b\'s bar (§5.199b §5), read under the bar')
    for x, scheme, pose, cid in FIVE:
        ep = f'{scheme}-{pose}'
        name = f'apple-macos-27.0-2x-{scheme}-standard-glass{x}/{cid}__{pose}'
        rec = frames.archive.records[name]
        runs = [r for r in rec['runs'] if r['protocol'] == 'normal' and r['pass'].startswith(PASS_PREFIX[x])]
        states = sorted({r['frame'] for r in runs}, key=lambda f: -sum(r['frame'] == f for r in runs))
        c = W.cell(ep, cid)
        imgs = [frames.archive.image(f) for f in states]
        dm = [deep(i, c) for i in imgs]
        diff_deep = max(abs(a - b) for a, b in zip(dm[0], dm[1]))
        regs, _ = W.side_regions(ep, cid)
        reg_diffs = {}
        if regs:
            for side in ('free', 'lifted'):
                g = regs[side]
                if g['pixels'] >= W.MIN_PX:
                    ma, mb = W.medians(imgs[0], g['idx']), W.medians(imgs[1], g['idx'])
                    reg_diffs[side] = max(abs(a - b) for a, b in zip(ma, mb))
        pix = int((np.abs(imgs[0] - imgs[1]).max(axis=2) > 0).sum())
        b = bar.get(name, {})
        sees_wtest = 'free' in support.get(ep, {}).get(cid, {}) and x == '0.25'
        role = 'a T ordinate at x = ' + x if cid.startswith('a-') else 'a structured ladder cell'
        say(f'- x = {x} {name}: states {[s[:12] for s in states]} '
            f'({[sum(r["frame"] == f for r in runs) for f in states]} runs); {pix} px differ, at most '
            f'{float(np.abs(imgs[0] - imgs[1]).max()):.0f} code; deep-median difference {diff_deep:.1f}; region-median '
            f'differences {reg_diffs or "none (no region)"}; bar {b.get("bar")} ({b.get("status", "?")}); it is {role}; '
            f'a w-test region sees it: {sees_wtest}')
        record['five'].append(dict(cell=name, states=states, pixels=pix, deepMedianDifference=diff_deep,
                                   regionMedianDifferences=reg_diffs, bar=b.get('bar'), wtestSees=sees_wtest))
    say('')
    same = sum(1 for c in record['consistency'] if c['same'])
    say(f'Consistency with the w-test\'s reading at 0.25 on its supported regions: {same} of {len(record["consistency"])} '
        'identical (the same functions on the same frames; not a second read).')
    (HERE / 'ladder.json').write_text(json.dumps(record, indent=1, default=float) + '\n')
    (HERE / 'ladder.txt').write_text('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
