"""W42 G0 proof 1 addendum (the parent's question at pin 5d719b60): does the new rrect-md depth patch
(c-s8-{hi,lo}-d34-rrect-md, content 30-38 pt) let the depth-graded radius reader resolve md's depth grading
in the active pose? The reader is narrow (ruling 3: it adds 2 sigma_n, so md's mask starts at 25.6 pt and the
d34 patch lies wholly outside the band plus its support). It is DESCRIPTIVE (ruling 2); the gated family
fitters read W and cannot reach any active rrect-md pixel (53.6 pt against md's 48-pt half-height).
Truths: LT (depth-graded; o-law ratio at 34 pt 0.851) and the free sigma_n(span) law (flat: ratio 1).
Writes proof1_depth_d34.json / .txt."""
import json

import bed
import proof1_readers_b as PB
import read_depth as RD

rows = []
for ep in ('light-rest', 'dark-rest'):
    q = PB.pol(ep)
    ids = [f'c-s8-{q}-rrect-md', f'c-s8-{q}-d34-rrect-md', f'c-s8-{q}-d24-rrect-md']
    for tname in ('LT', 'free-sn'):
        byid = {c.bed_id: c for c in bed.cells(ep, 2, ids=ids)}
        cells = [byid[i] for i in ids]                  # the centre first: the reader's reference
        PB.synth_all(cells, tname, ep)
        r = RD.read([(c.bed_id, c) for c in cells], 'native')
        for lb, rr in r['rows'].items():
            expect = rr['olaw_ratio'] if tname == 'LT' else 1.0
            ok = rr.get('sn') is not None and abs(rr['ratio'] - expect) <= 0.05
            rr.update(ep=ep, truth=tname, label=lb, expect=expect, bed=bed.BED_COMMIT[:8],
                      verdict='PASS' if ok else ('UNREAD' if rr.get('sn') is None else 'MISS'))
            rows.append(rr)
            print(f"{ep:11s} {tname:8s} {lb:24s} depth {rr['depth']:5.1f} sn {rr.get('sn')} ratio {rr.get('ratio')} "
                  f"expect {expect:.3f} {rr['verdict']} {rr.get('band', '')}", flush=True)
json.dump(rows, open('proof1_depth_d34.json', 'w'), indent=1, default=float)
L = ['W42 G0 proof 1 addendum: the md depth sweep with the d34 patch (pin 5d719b60; narrow reader, descriptive)']
for rr in rows:
    L.append(f"  {rr['ep']:11s} {rr['truth']:8s} {rr['label']:24s} depth {rr['depth']:5.1f} ratio "
             f"{rr.get('ratio') if rr.get('ratio') is None else round(rr['ratio'], 3)} expect {rr['expect']:.3f} "
             f"{rr['verdict']} {rr.get('band', '')}")
open('proof1_depth_d34.txt', 'w').write('\n'.join(L) + '\n')
