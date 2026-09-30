"""W42 G0 instrument, finding I-4, the control for the replay's sub-1e-3 differences: a pair is FITTED afresh with the
token-keyed engine (its producing commit's run_pair, in its scratch root), and the resulting row is then replayed at
its own recorded points in a fresh process, exactly as i4_replay.py replays the committed rows. No stale blur of
another cell can exist in a token-keyed run, so any difference between the fit's own record and its replay is the
store's width rounding (a blur computed at one width serves every width within 5e-5 device px of it, so the fit's
values depend on the order of its evaluations). If the committed rows' differences are of the same size, they carry
no sign of a stale blur.

Usage: python3.12 i4_fitcontrol.py fit ROOT TRUTH FIT EP     (writes /tmp/w42fix/i4-out/fitcontrol-<...>.json)
       python3.12 i4_fitcontrol.py replay NAME               (replays that row; appends the comparison)
"""
import json
import os
import sys

import i4_replay as IR

OUT = f'{IR.SCRATCH}/i4-out'


def fit(root, truth, fitname, ep):
    IR._setup(root, 'n')
    import proof2_separation as P
    r = P.run_pair((truth, fitname, ep, False))
    name = f'fitcontrol-{root}-{truth}-{fitname}-{ep}'.replace('>', '')
    json.dump(dict(root=root, row=r), open(f'{OUT}/{name}.json', 'w'), indent=1, default=float)
    print(name, r['ls_pooled'], r['s_ls'], r['s'], flush=True)


def replay(name):
    d = json.load(open(f'{OUT}/{name}.json'))
    IR._setup(d['root'], 'n')
    o = IR.replay(dict(kind='pair', index=-1, producer='control (token-keyed fit)', root=d['root'], kernel='n',
                       row=d['row']))
    d['replay'] = o
    json.dump(d, open(f'{OUT}/{name}.json', 'w'), indent=1, default=float)
    print(name, o['status'], o['diffs'], flush=True)


if __name__ == '__main__':
    if sys.argv[1] == 'fit':
        fit(*sys.argv[2:6])
    else:
        replay(sys.argv[2])
