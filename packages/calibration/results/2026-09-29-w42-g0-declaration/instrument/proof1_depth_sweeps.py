"""W42 G0 proof 1 addendum: the active depth sweeps the parent's ruled rows added, read by the depth-graded
radius reader (DESCRIPTIVE, the parent's ruling 2), at the bed pin bed.py names and the mask W42_KERNEL names
('n': the revised ruling 3's primary, refraction after the blur, 20 + 2 sigma_n,ref; 'w': the fallback's 53.6 pt).
The first run of this addendum (proof1_depth_d34.*, pin 5d719b60, md only) is kept beside it.

Sweeps, per active pass (light 'hi' patches, dark 'lo'):
  md     centre (48 pt), d34 (the 5d719b60 row, content 30-38 pt), d24;
  md p4  the dark 16/112 twins (764217e1): centre and d34;
  lg     centre (80 pt), d60 (the 764217e1 row, content 56-64 pt), d40.
Truths: LT (depth-graded, the o-law ratio) and the free sigma_n(span) law (flat: ratio 1). A sweep whose cells the
mask empties is reported as such. The gated route to the depth grading is the family fitters' LT-against-free-sn
pair in proof2_separation.py (touch-free-sn), not this reader. Writes proof1_depth_<kernel>.json / .txt.
"""
import json

import bed
import proof1_readers_b as PB
import proof_common as PC
import read_depth as RD


def sweeps(ep):
    q = PB.pol(ep)
    out = {'md': [f'c-s8-{q}-rrect-md', f'c-s8-{q}-d34-rrect-md', f'c-s8-{q}-d24-rrect-md'],
           'lg': [f'c-s8-{q}-d80-rrect-lg', f'c-s8-{q}-d60-rrect-lg', f'c-s8-{q}-d40-rrect-lg']}
    if ep.startswith('dark'):
        out['md p4 (16/112)'] = ['c-s8-lo-p4-rrect-md', 'c-s8-lo-p4-d34-rrect-md']
    return out


if __name__ == '__main__':
    kernel = PC.KERNEL
    rows = []
    for ep in ('light-rest', 'dark-rest'):
        for name, ids in sweeps(ep).items():
            byid = {c.bed_id: c for c in bed.cells(ep, 2, ids=ids, kernel=kernel)}
            use = [byid[i] for i in ids if i in byid]            # the centre first: the reader's reference
            if len(use) < 2 or use[0].bed_id != ids[0]:
                rows.append(dict(ep=ep, sweep=name, kernel=kernel, verdict='NO SWEEP',
                                 reason=f'the mask leaves {[c.bed_id for c in use]} of {ids}'))
                print(ep, name, 'NO SWEEP', rows[-1]['reason'], flush=True)
                continue
            for tname in ('LT', 'free-sn'):
                PB.synth_all(use, tname, ep)
                r = RD.read([(c.bed_id, c) for c in use], 'native')
                for lb, rr in r['rows'].items():
                    expect = rr['olaw_ratio'] if tname == 'LT' else 1.0
                    ok = rr.get('sn') is not None and abs(rr['ratio'] - expect) <= 0.05
                    rr.update(ep=ep, sweep=name, truth=tname, label=lb, expect=expect, kernel=kernel,
                              bed=bed.BED_COMMIT[:8], verdict='PASS' if ok else ('UNREAD' if rr.get('sn') is None else 'MISS'))
                    rows.append(rr)
                    print(f"{ep:11s} {name:15s} {tname:8s} {lb:26s} depth {rr['depth']:5.1f} ratio {rr.get('ratio')} "
                          f"expect {expect:.3f} {rr['verdict']} {rr.get('band', '')}", flush=True)
    json.dump(rows, open(f'proof1_depth_{kernel}.json', 'w'), indent=1, default=float)
    L = [f'W42 G0 proof 1 addendum: the active depth sweeps (descriptive depth reader), mask {kernel}, pin {bed.BED_COMMIT[:8]}']
    for rr in rows:
        if rr.get('verdict') == 'NO SWEEP':
            L.append(f"  {rr['ep']:11s} {rr['sweep']:15s} NO SWEEP: {rr['reason']}")
            continue
        L.append(f"  {rr['ep']:11s} {rr['sweep']:15s} {rr['truth']:8s} {rr['label']:26s} depth {rr['depth']:5.1f} ratio "
                 f"{rr.get('ratio') if rr.get('ratio') is None else round(rr['ratio'], 3)} expect {rr['expect']:.3f} "
                 f"{rr['verdict']} {rr.get('band', '')}")
    open(f'proof1_depth_{kernel}.txt', 'w').write('\n'.join(L) + '\n')
