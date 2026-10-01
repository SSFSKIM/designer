"""W42 G2 step 2, part 7: the candidate-document VALUES per endpoint, for scratch renders only (no shipped document
is sealed or edited). They are LT's fitted values whatever its survival, which `survives` states beside them.

Leaves (implementation-design.md §1.1): bodyLawK (k, k), bodyLawLambda, bodyLawKnee (0 per-channel, 1 on-luma
whole colour, 2 on-luma chroma from W), bodyLawWidthUnit (1 = points), bodyLawEncodedAveraging (1), bodyLawNormal
0.5, bodyLawHinge (+1 light, -1 dark), bodyLawPose; candidate 1 light receded bodyE3NeutralHigh (family A's seven
light-receded t = 0 ordinates at 160 ... 255); candidate 2 bodyToneTableCodes (five rows 64/80/96/128/160 x eleven
levels, per channel as the addendum's section 5 requires when the greys are not neutral within the bar) and its
chroma scale.

    python3.12 -B candidates.py [TAG]     -> candidates.json, candidates.txt
"""
import json
import sys

import numpy as np

import common as C

TAG = sys.argv[1] if len(sys.argv) > 1 else 'main'
KNEE_LEAF = {'channel': 0, 'luma': 1, 'lumaW': 2}
UNIT_LEAF = {'dev': 0, 'pt': 1, 'texel': 2}
F_LEVELS = (160, 176, 192, 208, 224, 240, 255)


def main():
    ver = json.loads((C.HERE / 'verdicts.json').read_text())
    nat = json.loads((C.HERE / 'native-t' / 'ordinates.json').read_text())
    out = dict(schema='w42-g2-step2-candidates-1', tag=TAG, note='candidate-document VALUES for scratch renders; '
               'no family survives clause 6 in any endpoint, so none of these is an identified law', endpoints={})
    L = ['W42 G2 step 2: candidate-document values (scratch renders only; see verdicts.txt for survival)', '']
    for ep in C.EPS:
        v = ver['endpoints'][ep]
        fit = json.loads((C.HERE / 'fits' / TAG / f'LT__{ep}__n.json').read_text())
        knee = json.loads((C.HERE / 'knee' / f'LT__{ep}.json').read_text())
        kform = v['_knee']['carried']
        unit = 'pt'
        dec = {pt: v['_units'][pt]['_decision'] for pt in ('minimax', 'ls')}
        taken = [d for d in dec.values() if d.endswith('beat points at a 1x discriminator')]
        if taken:
            raise SystemExit(f'{ep}: a unit other than points is taken ({dec}); set it by hand from verdicts.txt')
        law = {}
        for pt in ('minimax', 'ls'):
            k = fit[pt]['params'][f'k@{ep}']
            law[pt] = dict(bodyLawK=[k, k], bodyLawLambda=fit[pt]['lam'][ep], failures=fit[pt]['failures'],
                           worst=max(fit[pt]['calibration']['worstMeasured'], fit[pt]['validation']['worstMeasured']))
        common = dict(bodyLawKnee=KNEE_LEAF[kform], bodyLawWidthUnit=UNIT_LEAF[unit], bodyLawEncodedAveraging=1,
                      bodyLawNormal=0.5, bodyLawHinge=1 if ep.startswith('light') else -1,
                      bodyLawPose=0 if ep.endswith('rest') else 1, bodyLawEdgeSwap=0)
        e = nat['endpoints'][ep]
        tables = e['bodyToneTableCodes']['rows']
        luma_rows = (C.W709[0] * np.array(tables['R']) + C.W709[1] * np.array(tables['G']) +
                     C.W709[2] * np.array(tables['B'])).round(4).tolist()
        spread = max(abs(a - b) for ch1 in 'RGB' for ch2 in 'RGB'
                     for ra, rb in zip(tables[ch1], tables[ch2]) for a, b in zip(ra, rb))
        form = knee['forms'][kform]
        chroma = dict(knee=kform, scaleMinimax=form['minimax']['s'], scaleLeastSquares=form['ls']['s'],
                      gCoefficients=knee['gCoefficients'], gSource=knee['gSource'],
                      failures=dict(minimax=form['minimax']['failures'], ls=form['ls']['failures']),
                      worstMinimax=max(form['minimax']['calibration']['worstMeasured'],
                                       form['minimax']['validation']['worstMeasured']))
        row = dict(survives=False, verdict=v['_verdict'], law=law, leaves=common, unit=unit, unitDecision=dec,
                   knee=dict(form=kform, reason=v['_knee']['reason']),
                   candidate2=dict(bodyToneTableLevels=list(C.NT.GRID_LEVELS), bodyToneTableSpans=list(C.NT.GRID_SPANS),
                                   bodyToneTableCodes=tables, bodyToneTableCodesRec709=luma_rows,
                                   channelSpreadCodes=spread, chroma=chroma))
        if ep == 'light-inactive':
            t0 = e['ordinates']
            fx = {ch: [t0[ch]['64'][str(Lv)] for Lv in F_LEVELS] for ch in 'RGB'}
            fl = [round(float(sum(w * fx[ch][i] for w, ch in zip(C.W709, "RGB"))), 4) for i in range(len(F_LEVELS))]
            row['candidate1'] = dict(bodyE3NeutralHigh=fl, perChannel=fx, levels=list(F_LEVELS),
                                     readOn='2x light-receded family-A calibration greys on the capsule (t = 0)',
                                     spanInvariance={s: {Lv: [t0[ch][s].get(str(Lv)) for ch in 'RGB'] for Lv in F_LEVELS
                                                         if str(Lv) in t0['R'][s]} for s in ('96', '128', '160')})
        out['endpoints'][ep] = row
        L.append(f"== {ep} ({C.EP_NAME[ep]}): survives {row['survives']}")
        for pt in ('minimax', 'ls'):
            a = law[pt]
            L.append(f"  law [{pt}]: bodyLawK {a['bodyLawK'][0]:.4f} x2, bodyLawLambda {a['bodyLawLambda']:.4f}  "
                     f"(failures {a['failures']}, worst {a['worst']:.2f} codes)")
        L.append(f"  leaves: {common}  (unit: {dec})")
        L.append(f"  knee: {kform} — {v['_knee']['reason']}")
        L.append(f"  candidate 2 chroma scale ({kform}): minimax {chroma['scaleMinimax']:.4f}, least squares "
                 f"{chroma['scaleLeastSquares']:.4f}; g = W41 G1 {chroma['gCoefficients']}")
        L.append(f"  candidate 2 bodyToneTableCodes per channel (channels differ by at most {spread:.2f} codes); "
                 'Rec.709 rows:')
        for s, r in zip(C.NT.GRID_SPANS, luma_rows):
            L.append(f"    {s:3d}: " + ' '.join(f'{x:7.2f}' for x in r))
        if 'candidate1' in row:
            L.append(f"  candidate 1 F extension bodyE3NeutralHigh at {list(F_LEVELS)}: Rec.709 {row['candidate1']['bodyE3NeutralHigh']} "
                     f"(R {fx['R']}, G {fx['G']}, B {fx['B']})")
        L.append('')
    C.save(C.HERE / 'candidates.json', out)
    (C.HERE / 'candidates.txt').write_text('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    main()
