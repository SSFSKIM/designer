"""W42 G0 instrument: the reader proofs whose synthetic truth is W-shape, re-run after the review of b151aff4 (I-2:
W-shape's narrow term had followed W onto the shape window). Two sections of proof1_readers_b carry a W-shape truth:
the step reader's support call (gated; light-inactive, W-shape given) and the U1 diagnostic's lam readers
(descriptive; three endpoints). Their W-shape rows are replaced in place, each marked with the pin and engine;
every other row is left as it stands. Run from this folder: python3.12 rerun_wshape_readers.py
"""
import json

import bed
import forward as F
import proof1_readers_b as PB

# the step reader's gated call: drop the W-shape row so step_section recomputes it alone
fn = f'{PB.OUT}.step.json'
old = json.load(open(fn))
json.dump([x for x in old if x['truth'] != 'W-shape'], open(fn, 'w'), indent=1, default=float)
PB.STEP_PLAN = [('light-inactive', ('W-shape',), False)]
out = PB.step_section()
for x in out:
    if x['truth'] == 'W-shape':
        x.update(bed=bed.BED_COMMIT[:8], engine=F.ENGINE)
PB.save('step', out)

# the U1 diagnostic: the W-shape truth's rows only
PB.U1_TRUTHS = ('W-shape',)
new = PB.u1_section()
for x in new:
    x.update(bed=bed.BED_COMMIT[:8], engine=F.ENGINE)
fn = f'{PB.OUT}.u1.json'
old = json.load(open(fn))
keep = [x for x in old if x['truth'] != 'W-shape']
PB.save('u1', keep + new)
PB.report()
print('W-shape reader rows re-run:', [(x['ep'], x['truth'], x.get('call', x.get('k_fit'))) for x in
                                      [y for y in out if y['truth'] == 'W-shape'] + new])
