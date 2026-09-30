"""W42 G0 instrument: the capture floor's descriptive check (the parent's ruling: memo E's 0.8-device-px pre-blur
stays a declared constant, re-read descriptively on the fine-pitch cells, never fitted). An LT truth, at the
narrow-support mask (the revised ruling 3's primary) on the final bed, with the literal box-decimation null
fitted to it on the fine-pitch B' cells of both scales (pitch <= 8 pt, where the floor's form shows) and on
every structured family; pooled and worst-cell rms. A large misfit means the bed can tell the declared floor
from the decimation; it never moves the constant. Writes proof2_floor_check.json / .txt."""
import json

import bed
import families as FA
import fitting as Fi
import forward as F
import proof_common as PC

rows = []
for ep in ('light-rest', 'dark-rest', 'light-inactive', 'dark-inactive'):
    for scope, letters in (('fine pitch (B\' pitch <= 8)', ("B'",)), ('every structured family', ('B', "B'", 'C', 'D'))):
        cells = [c for s in (2, 1) for c in bed.cells(ep, s, letters=letters, kernel='n')
                 if scope.startswith('every') or c.geometry.get('pitch', 99) <= 8]
        PC.render_truth(cells, F.Family(), PC.truth('LT', ep))
        prob = Fi.Problem(cells, FA.FAMILIES['null-boxfloor'][0], PC.layout_for('null-boxfloor', ep),
                          PC.bounds_for('null-boxfloor'))
        r = prob.fit(PC.starts_for('null-boxfloor', ep, 1))
        worst = max(r['per_cell'].items(), key=lambda kv: kv[1])
        rows.append(dict(ep=ep, scope=scope, n_cells=len(prob.cells), pooled=r['pooled'], max_cell=r['max_cell'],
                         worst=worst[0], k=r['x'], bed=bed.BED_COMMIT[:8]))
        print(ep, scope, len(prob.cells), round(r['pooled'], 3), round(r['max_cell'], 3), worst[0], flush=True)
json.dump(rows, open('proof2_floor_check.json', 'w'), indent=1, default=float)
L = ['W42 G0 capture-floor check: the box-decimation null fitted to an LT truth at the narrow-support mask (descriptive)']
for r in rows:
    L.append(f"  {r['ep']:15s} {r['scope']:28s} {r['n_cells']:3d} cells  pooled {r['pooled']:.3f}  worst cell "
             f"{r['max_cell']:.3f} ({r['worst']})")
open('proof2_floor_check.txt', 'w').write('\n'.join(L) + '\n')
