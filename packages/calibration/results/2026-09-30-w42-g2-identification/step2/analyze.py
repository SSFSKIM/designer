"""W42 G2 step 2, part 6: the verdicts, from the fits alone (no pixel is read here beyond the statistics tables
the fits wrote): survival per family and endpoint (clause 6), the knee (family E), the unit (the 1x cells), the k
ladder, the refraction order and Decision Log 5f's agreement, resolution between families (reading-plan.md
item 8), and the candidate-document values.

    python3.12 -B analyze.py [TAG]     -> verdicts.json, verdicts.txt
"""
import gzip
import itertools
import json
import sys

import numpy as np

import common as C

TAG = sys.argv[1] if len(sys.argv) > 1 else 'main'
FITS = C.HERE / 'fits' / TAG
BEAT = 3.0          # max(3, bar_a + bar_b) with every bar 0.5


def load(name):
    p = FITS / name
    return json.loads(p.read_text()) if p.exists() else None


def table(rep):
    t = rep['statisticsTable']
    raw = gzip.decompress(open(t['path'], 'rb').read())
    import hashlib
    if hashlib.sha256(raw).hexdigest() != t['sha256']:
        raise SystemExit('statistics table moved: ' + t['path'])
    return json.loads(raw)['statistics']


def flat(tab, point, cells=None):
    """{(cell, stat): (native, pred, err, status)} over calibration and validation."""
    out = {}
    for part in ('calibration', 'validation'):
        for cid, rows in tab[point][part].items():
            if cells is not None and not cells(cid):
                continue
            for k, nv, pv, err, bound, st in rows:
                out[(cid, k)] = (nv, pv, err, st)
    return out


def compare(a, b, cells=None):
    """a, b: flat tables. Largest |e_a| - |e_b| (b better) and |e_b| - |e_a| (a better) over admitted
    discriminators (measured statistics common to both), and the largest prediction separation."""
    keys = [k for k in a if k in b and a[k][3] == 'measured' and b[k][3] == 'measured']
    if not keys:
        return dict(n=0)
    da = [(abs(a[k][2]) - abs(b[k][2]), k) for k in keys]
    sep = max((abs(a[k][1] - b[k][1]), k) for k in keys)
    best_b = max(da)
    best_a = min(da)
    return dict(n=len(keys), bBeatsABy=best_b[0], bBeatsAAt=list(best_b[1]), aBeatsBBy=-best_a[0],
                aBeatsBAt=list(best_a[1]), maxSeparation=sep[0], maxSeparationAt=list(sep[1]),
                bBeatsA=best_b[0] > BEAT, aBeatsB=-best_a[0] > BEAT,
                withinResolution=sep[0] < BEAT)


def point_of(rep):
    """The fit's reported point: the one that survives, else the minimax point (the declared refinement)."""
    if rep['minimax']['survives'] or not rep['ls']['survives']:
        return 'minimax'
    return 'ls'


def main():
    out = dict(schema='w42-g2-step2-verdicts-1', tag=TAG, endpoints={})
    L = [f'W42 G2 step 2 verdicts (fits/{TAG}); survival at max(1, bar) = 1 code on every channel of every '
         'calibration and validation region statistic', '']
    nat = json.loads((C.HERE / 'native-t' / 'ordinates.json').read_text())
    reports = {p.stem: json.loads(p.read_text()) for p in sorted(FITS.glob('*.json'))}
    for ep in C.EPS:
        E = {}
        L.append(f'=== {ep} ({C.EP_NAME[ep]})')
        rows = []
        for key, rep in reports.items():
            if not key.endswith(f'__{ep}__n') or '@' in key:
                continue
            fam = rep['family']
            pt = point_of(rep)
            v = rep[pt]
            worst = max(v['calibration']['worstMeasured'], v['validation']['worstMeasured'])
            rows.append((fam, rep, pt, v, worst))
        rows.sort(key=lambda r: (not r[0] == 'LT', r[0].startswith('null'), r[4]))
        for fam, rep, pt, v, worst in rows:
            E[fam] = dict(count=rep['count'], point=pt, params=v['params'], lam=v['lam'][ep],
                          failures=v['failures'], worst=worst,
                          worstAt=v['calibration']['worstAt'] if v['calibration']['worstMeasured'] >= v['validation']['worstMeasured'] else v['validation']['worstAt'],
                          pooledCal=v['calibration']['pooledRms'], pooledVal=v['validation']['pooledRms'],
                          statuses={k: v['calibration']['statuses'].get(k, 0) + v['validation']['statuses'].get(k, 0)
                                    for k in set(v['calibration']['statuses']) | set(v['validation']['statuses'])},
                          survivesGrey=rep['survives'],
                          ls=dict(params=rep['ls']['params'], lam=rep['ls']['lam'][ep], failures=rep['ls']['failures'],
                                  worst=max(rep['ls']['calibration']['worstMeasured'], rep['ls']['validation']['worstMeasured'])),
                          minimax=dict(params=rep['minimax']['params'], lam=rep['minimax']['lam'][ep],
                                       failures=rep['minimax']['failures'],
                                       worst=max(rep['minimax']['calibration']['worstMeasured'],
                                                 rep['minimax']['validation']['worstMeasured'])))
            ps = ', '.join(f"{k.split('@')[0]} {x:.4g}" for k, x in v['params'].items())
            L.append(f"  {fam:22s} n={rep['count']}  {ps}, lam {v['lam'][ep]:.4f}  [{pt}]  pooled cal "
                     f"{v['calibration']['pooledRms']:.3f} val {v['validation']['pooledRms']:.3f}  worst {worst:5.2f} "
                     f"at {E[fam]['worstAt']}  failures {v['failures']}  "
                     f"{'SURVIVES (grey)' if rep['survives'] else 'fails'}")
        if f'LT__{ep}__n' in reports:
            for pt in ('ls', 'minimax'):
                bd = breakdown(reports[f'LT__{ep}__n'], pt)
                E.setdefault('_LTbreakdown', {})[pt] = bd
                L.append(f'  LT [{pt}] failing statistics by group (scale, bed family, component): ' + '; '.join(
                    f"{k} {v['failed']}/{v['stats']} worst {v['worst']}" for k, v in bd.items() if v['stats']))
                w2 = max(v['worst'] for k, v in bd.items() if k.startswith('2x'))
                L.append(f'    [{pt}] worst over the 2x cells alone: {w2}')
        # E: the knee and the chroma scale (LT's)
        kn = C.HERE / 'knee' / f'LT__{ep}.json'
        knee = json.loads(kn.read_text()) if kn.exists() else None
        if knee:
            L.append('  family E (LT held at its grey minimax point), candidate 2\'s chroma form:')
            for form, row in knee['forms'].items():
                m = row['minimax']
                L.append(f"    knee {form:8s} s ls {row['ls']['s']:.4f} mm {m['s']:.4f}  failures ls {row['ls']['failures']} "
                         f"mm {m['failures']}  worst cal {m['calibration']['worstMeasured']:.2f} val "
                         f"{m['validation']['worstMeasured']:.2f} (luma-only worst {m['lumaOnlyWorst']:.2f})  "
                         f"ls rms {row['lsObjective']:.3f}")
            surv = [f for f, r in knee['forms'].items() if r['ls']['survives'] or r['minimax']['survives']]
            E['_knee'] = dict(survivingForms=surv, carried=surv[0] if len(surv) == 1 else 'channel',
                              reason='one survivor' if len(surv) == 1 else
                              ('tie among survivors: carried as per-channel (the parent\'s ruling)' if surv else
                               'no form survives: the tie rule carries per-channel'),
                              scale={f: dict(ls=r['ls']['s'], minimax=r['minimax']['s']) for f, r in knee['forms'].items()},
                              failures={f: min(r['ls']['failures'], r['minimax']['failures']) for f, r in knee['forms'].items()},
                              worst={f: max(r['minimax']['calibration']['worstMeasured'], r['minimax']['validation']['worstMeasured'])
                                     for f, r in knee['forms'].items()})
            if 'statisticsTable' in knee:
                import hashlib
                raw = gzip.decompress(open(knee['statisticsTable']['path'], 'rb').read())
                assert hashlib.sha256(raw).hexdigest() == knee['statisticsTable']['sha256']
                kt = json.loads(raw)
                kf = {f: flat(kt[f], 'minimax') for f in kt}
                E['_knee']['resolution'] = {f'channel vs {f}': compare(kf[f], kf['channel'])
                                            for f in kf if f != 'channel'}
                for nm, c in E['_knee']['resolution'].items():
                    L.append(f"    {nm}: per-channel better by up to {c['bBeatsABy']:.2f} at {c['bBeatsAAt'][0]}:"
                             f"{c['bBeatsAAt'][1]}; the other better by up to {c['aBeatsBBy']:.2f}"
                             f"{'  PER-CHANNEL BEATS IT' if c['bBeatsA'] else ''}")
                if all(c['bBeatsA'] and not c['aBeatsB'] for c in E['_knee']['resolution'].values()):
                    E['_knee']['carried'] = 'channel'
                    E['_knee']['reason'] = ('per-channel beats both on-luma forms by more than max(3, sum of bars) at an '
                                            'admitted discriminator (resolution first), though no form survives')
            L.append(f"    knee: {E['_knee']['carried']} ({E['_knee']['reason']})")
        # resolution: LT against each rival, at the same point of both fits (minimax, the declared refinement; and
        # least squares, because a minimax point can be dragged by one cell no family closes)
        if f'LT__{ep}__n' in reports:
            comps = {}
            for pt in ('minimax', 'ls'):
                lt_tab = flat(table(reports[f'LT__{ep}__n']), pt)
                for fam, rep, _, v, worst in rows:
                    if fam == 'LT':
                        continue
                    comps.setdefault(fam, {})[pt] = compare(lt_tab, flat(table(rep), pt))
            E['_resolutionAgainstLT'] = comps
            L.append('  against LT (admitted discriminators; "beats" = |e| smaller by > 3 codes), [minimax] / [ls]:')
            for fam, cc in comps.items():
                parts = []
                for pt in ('minimax', 'ls'):
                    c = cc[pt]
                    if not c.get('n'):
                        continue
                    parts.append(f"[{pt}] rival better by {c['bBeatsABy']:5.2f} at {c['bBeatsAAt'][0]}:{c['bBeatsAAt'][1]}, "
                                 f"LT better by {c['aBeatsBBy']:5.2f}"
                                 f"{' RIVAL-BEATS' if c['bBeatsA'] else ''}{' LT-BEATS' if c['aBeatsB'] else ''}")
                L.append(f"    {fam:22s} " + ' | '.join(parts))
        # the unit: LT (points) against texels and device px on the 1x cells, at both points of each fit
        units = {}
        if f'LT__{ep}__n' in reports:
            for pt in ('minimax', 'ls'):
                u = {}
                lt_1x = flat(table(reports[f'LT__{ep}__n']), pt, lambda c: c.startswith('1x|'))
                for null in ('null-texel', 'null-dev'):
                    r = reports.get(f'{null}__{ep}__n')
                    if r:
                        u[null] = compare(lt_1x, flat(table(r), pt, lambda c: c.startswith('1x|')))
                        u[null]['pooled1x'] = _pooled_at(r, pt, '1x|')
                u['LT(pt)'] = dict(pooled1x=_pooled_at(reports[f'LT__{ep}__n'], pt, '1x|'))
                beaten = [n for n, c in u.items() if c.get('bBeatsA')]
                mutual = [n for n in beaten if u[n].get('aBeatsB')]
                if not all(n in u for n in ('null-texel', 'null-dev')):
                    u['_decision'] = 'PENDING: a unit null has not been fitted'
                elif not beaten:
                    u['_decision'] = 'no unit beats points at an admitted 1x discriminator: the declared points stand'
                elif beaten == mutual:
                    u['_decision'] = (f'{beaten} beat points at some 1x discriminator and points beat them by more '
                                      'elsewhere (resolved both ways); no unit dominates points')
                else:
                    u['_decision'] = f'{beaten} beat points at a 1x discriminator'
                units[pt] = u
                L.append(f"  unit [{pt}] (1x cells): pooled 1x rms pt {u['LT(pt)']['pooled1x']:.3f}" +
                         ''.join(f", {n.split('-')[1]} {u[n]['pooled1x']:.3f} (better than pt by up to "
                                 f"{u[n]['bBeatsABy']:.2f}, worse by up to {u[n]['aBeatsBBy']:.2f})"
                                 for n in ('null-texel', 'null-dev') if n in u and u[n].get('n')) +
                         f"; {u['_decision']}")
        E['_units'] = units
        # refraction (active)
        if ep.endswith('rest'):
            rf = C.HERE / 'refraction' / f'{ep}.json'
            if rf.exists():
                r = json.loads(rf.read_text())
                E['_refraction'] = dict(P=r['P'], Pstar=r['Pstar'], admitted=r['admitted'], S1=r['S1']['D'],
                                        S1call=r['S1']['call'], S2=r['S2']['A_hat'], S2call=r['S2']['call'],
                                        verdict=r['verdict'], P_withoutE=r['P_withoutE_descriptive'])
                L.append(f"  refraction v3: P {r['P']:.3f} (without E {r['P_withoutE_descriptive']:.3f}); S1 {r['S1']['D']:+.3f} "
                         f"{r['S1']['call']} (P* {r['Pstar']['S1']}, admitted {r['admitted']['S1']}); S2 "
                         f"{r['S2']['A_hat']:+.2f} pt {r['S2']['call']} (P* {r['Pstar']['S2']}, admitted "
                         f"{r['admitted']['S2']}) -> {r['verdict']}")
            n, w = reports.get(f'LT__{ep}__n'), reports.get(f'LT__{ep}__w')
            if n and w:
                res = _lt_resolution(ep)
                agree = {}
                for pt in ('minimax', 'ls'):
                    dk = w[pt]['params'][f'k@{ep}'] - n[pt]['params'][f'k@{ep}']
                    dl = w[pt]['lam'][ep] - n[pt]['lam'][ep]
                    ok_k = (dk <= res['k'][0]) if dk >= 0 else (-dk <= res['k'][1])
                    ok_l = (dl <= res['lam'][0]) if dl >= 0 else (-dl <= res['lam'][1])
                    agree[pt] = dict(narrow=dict(k=n[pt]['params'][f'k@{ep}'], lam=n[pt]['lam'][ep]),
                                     wide=dict(k=w[pt]['params'][f'k@{ep}'], lam=w[pt]['lam'][ep]),
                                     dk=dk, dlam=dl, resolution=res, agree=bool(ok_k and ok_l),
                                     wideCells=w['cells'])
                E['_DL5f'] = agree
                a = agree['minimax']
                L.append(f"  DL 5f (LT, minimax points): narrow k {a['narrow']['k']:.4f} lam {a['narrow']['lam']:.4f}; "
                         f"53.6-pt k {a['wide']['k']:.4f} lam {a['wide']['lam']:.4f}; dk {a['dk']:+.4f} dlam "
                         f"{a['dlam']:+.4f} against k +{res['k'][0]}/-{res['k'][1]}, lam +{res['lam'][0]}/-{res['lam'][1]}"
                         f" -> {'AGREE' if a['agree'] else 'DIFFER'} (least-squares points: "
                         f"{'agree' if agree['ls']['agree'] else 'differ'}, dk {agree['ls']['dk']:+.4f} dlam {agree['ls']['dlam']:+.4f})")
        # survival verdict for the endpoint
        grey_surv = [f for f in E if not f.startswith('_') and E[f]['survivesGrey'] and not f.startswith('null')]
        e_ok = bool(E.get('_knee', {}).get('survivingForms'))
        E['_verdict'] = dict(greySurvivors=grey_surv, familyESurvivesUnderLT=e_ok,
                             survivors=[f for f in grey_surv if f == 'LT' and e_ok],
                             negative=not ([f for f in grey_surv if f == 'LT' and e_ok]))
        L.append(f"  VERDICT: grey survivors {grey_surv or 'none'}; family E under LT "
                 f"{'passes' if e_ok else 'fails'}; endpoint "
                 f"{'NEGATIVE at its resolution (no survivor)' if E['_verdict']['negative'] else 'has a survivor'}")
        L.append('')
        out['endpoints'][ep] = E
    # the k ladder
    lad = {}
    for level in ('k@global', 'k@scheme'):
        rep = load(f'LT@{level}__all__n.json')
        if rep:
            lad[level] = rep
    if lad:
        L.append('=== the k ladder (kNesting): a less restricted level is taken only where it beats the more restricted '
                 'one by > 3 codes at an admitted discriminator')
        out['kLadder'] = {}
        for pt in ('minimax', 'ls'):
            lv_tabs = {}
            for level, rep in lad.items():
                tab = table(rep)
                lv_tabs[level] = {ep: _flat_ep(tab[pt][ep]) for ep in C.EPS}
                L.append(f"  [{pt}] {level}: {rep[pt]['params']} lam " +
                         ', '.join(f"{e} {x:.4f}" for e, x in rep[pt]['lam'].items()) + '; failures ' +
                         ', '.join(f"{ep} {rep[pt]['endpoints'][ep]['failures']}" for ep in C.EPS))
            lv_tabs['k@endpoint'] = {ep: flat(table(reports[f'LT__{ep}__n']), pt) for ep in C.EPS}
            if all(f'LT-2k__{ep}__n' in reports for ep in C.EPS):
                lv_tabs['k2@endpoint'] = {ep: flat(table(reports[f'LT-2k__{ep}__n']), pt) for ep in C.EPS}
            order = [l for l in ('k@global', 'k@scheme', 'k@endpoint', 'k2@endpoint') if l in lv_tabs]
            steps = {}
            for x, y in zip(order, order[1:]):
                steps[f'{x}->{y}'] = {ep: compare(lv_tabs[x][ep], lv_tabs[y][ep]) for ep in C.EPS}
                for ep, c in steps[f'{x}->{y}'].items():
                    L.append(f"  [{pt}] {x} -> {y} {ep:15s}: {y} better by up to {c['bBeatsABy']:5.2f} at "
                             f"{c['bBeatsAAt'][0]}:{c['bBeatsAAt'][1]}; {x} better by up to {c['aBeatsBBy']:5.2f}; "
                             f"{'TAKE ' + y if c['bBeatsA'] else 'keep ' + x}")
            taken = order[0]
            for x, y in zip(order, order[1:]):
                if x != taken:
                    break
                if any(c['bBeatsA'] for c in steps[f'{x}->{y}'].values()):
                    taken = y
            out['kLadder'][pt] = dict(steps=steps, taken=taken, levels=order,
                                      params={l: lad[l][pt]['params'] for l in lad})
            L.append(f'  [{pt}] k level taken: {taken}')
        L.append('')
    out['nativeT'] = {ep: dict(nonMonotone=[(r['channel'], r['stratum']) for r in v['nonMonotone']],
                               channelSpreadMax=v['channelSpreadMax'],
                               validation=[(x['cell'], x['error'], x['passes']) for x in v['validation']])
                      for ep, v in nat['endpoints'].items()}
    C.save(C.HERE / 'verdicts.json', out)
    (C.HERE / 'verdicts.txt').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))


def breakdown(rep, point):
    """Descriptive: failing statistics grouped by scale, bed family and component, with the worst measured miss
    in each group (which cells carry the negative)."""
    bedj = json.loads((C.DECL / 'bed' / 'bed.json').read_text())['cells']
    tab = table(rep)[point]
    groups = {}
    for part in ('calibration', 'validation'):
        for cid, rows in tab[part].items():
            sc, bid = cid.split('|')
            b = bedj[bid]
            key = f"{sc} {b['family']:2s} {b['component']}"
            g = groups.setdefault(key, dict(stats=0, failed=0, worst=0.0, cells=set()))
            g['cells'].add(bid)
            for k, nv, pv, err, bound, st in rows:
                g['stats'] += 1
                if (st == 'measured' and abs(err) > bound) or st == 'UNMEASURED':
                    g['failed'] += 1
                if st == 'measured':
                    g['worst'] = max(g['worst'], abs(err))
    return {k: dict(stats=v['stats'], failed=v['failed'], worst=round(v['worst'], 2), cells=len(v['cells']))
            for k, v in sorted(groups.items())}


def _flat_ep(tab):
    out = {}
    for part in ('calibration', 'validation'):
        for cid, rows in tab[part].items():
            for k, nv, pv, err, bound, st in rows:
                out[(cid, k)] = (nv, pv, err, st)
    return out


def _pooled_at(rep, pt, prefix):
    per = {**rep[pt]['calibration']['perCellRms'], **rep[pt]['validation']['perCellRms']}
    v = [x for k, x in per.items() if k.startswith(prefix)]
    return float(np.sqrt(np.mean(np.square(v)))) if v else float('nan')


def _pooled(rep, prefix):
    pt = point_of(rep)
    per = {**rep[pt]['calibration']['perCellRms'], **rep[pt]['validation']['perCellRms']}
    v = [x for k, x in per.items() if k.startswith(prefix)]
    return float(np.sqrt(np.mean(np.square(v)))) if v else float('nan')


def _lt_resolution(ep):
    rows = json.loads((C.INSTR / 'resolution.json').read_text())['rows']
    res = {}
    for r in rows:
        if r['reader'] == 'family fitter: LT (survival resolution)' and r['endpoints'] == [ep]:
            a, b = r['synthetic']['resolution'].split('/')
            res[r['quantity']] = (float(a.strip().lstrip('+')), float(b.strip().lstrip('-')))
    return res


if __name__ == '__main__':
    main()
