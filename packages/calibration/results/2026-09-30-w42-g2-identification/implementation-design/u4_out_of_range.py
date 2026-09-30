"""W42 G2 step 3, the U3/U4 review's fix wave, item 1: an out-of-range argument through every tone.

The law's M leaves [0, 1] under admitted parameters: the per-channel knee overshoots at lambda above
1, and the luma composite with W's chroma adds W's chroma to a luma W does not have. The declared
oracle passes M to T unclipped (`forward.py:527`, `T(255 * M)`, T `tone.py:70-71`, held at the
table's ends), and the rehearsal's tones clip where their own gamut steps do:
- the landed solve clips each channel and, separately, the luma (`body.py:513`, `515`, with `dec` at
  `69-71`);
- E3 clips F, adds the argument's chroma and clips the channels (`body.py:550`, `573`;
  `swap.py:219`, `233`);
- candidate 2's table holds its levels at the ends and clips the same way.

The implementation clipped M before storing A, and `u2_mirror.py` clipped both its oracle and its
simulation, so neither could see the difference. This fixture is the unclipped oracle for every
composite row of `composite.json`'s generator whose M leaves [0, 1], through:
- the landed solve at every endpoint (`body.solve` + `body.compose`, as `landed.json`);
- E3 with the F extension (`u2_fixtures.e3_ext`, as `tones.json`);
- candidate 2's table (`native_t.py`'s grid, as `tones.json`), plus a constant-128 table that shows
  what a clip before the chroma term would have moved.

    python3.12 -B u4_out_of_range.py      # writes fixtures/out-of-range.json beside this file
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import u2_fixtures as U  # noqa: E402  (puts the instrument, the rehearsal and native_t on the path)

BODY, G, NT = U.BODY, U.G, U.NT
OUT = os.path.join(HERE, 'fixtures', 'out-of-range.json')
KNEES = {'channel': 0, 'luma': 1, 'chromaW': 2}
HIGH = [206.0, 214.0, 222.0, 229.0, 234.0, 238.0, 240.0]


def table_out(tab, codes, span, gains, scale):
    L = float(np.dot(codes, G.W709))
    f = float(np.clip(NT.grid_eval(tab, np.array([L]), span)[0], 0, 255))
    if codes[0] == codes[1] == codes[2]:
        return [f, f, f]
    g = scale * float(np.where(L > 93, gains[1] + np.clip((L - 93) / 25, 0, 1) * (gains[2] - gains[1]),
                               gains[0] + np.clip((L - 63) / 30, 0, 1) * (gains[1] - gains[0])))
    return [float(np.clip(f + g * (v - L), 0, 255)) for v in codes]


def main():
    cases = []
    for row in U.composite_fixture()['rows']:
        for name, M in row['M'].items():
            M = np.array(M)
            if np.all((M >= 0) & (M <= 1)):
                continue
            cases.append(dict(C=row['C'], W=row['W'], lam=row['lam'], w=row['w'], hinge=row['hinge'],
                              knee=KNEES[name], M=M.tolist(), wideLuma=row['wideLuma']))
    A = np.array([c['M'] for c in cases])

    landed = {}
    for ep, e in BODY.RES.items():
        runs = []
        for sizeK in (0.0, 0.35, 1.0):
            c = BODY.dec(A)
            lin = c @ BODY.W709
            level = BODY.dec(A @ BODY.W709) if e['abscissa'] != 'source(default)' else lin
            y = BODY.compose(e, c, BODY.solve(e, sizeK, level, lin), c)
            runs.append(dict(sizeK=sizeK, linear=y.tolist()))
        landed[ep] = runs

    neutral = [150, 157, 164, 171, 178, 188, 197]
    gains = [0.929205829365914, 0.9597570955316058, 0.9383102545096953]
    e3 = [dict(strength=s, out=[U.e3_ext(255 * np.array(c['M']), 255 * c['wideLuma'], gains, neutral,
                                         HIGH, s) for c in cases]) for s in (0.0, 1.0)]

    nt = NT.NativeT(NT.stand_in('light-inactive', 'light'), 'light')
    tab = nt.table()
    tgains, tscale = [0.95, 0.949, 0.933], 1.07
    spans = [64.0, 112.0, 160.0]
    table = dict(levels=list(NT.GRID_LEVELS), spans=list(NT.GRID_SPANS), codes=tab.tolist(),
                 gains=tgains, scale=tscale,
                 out={str(s): [table_out(tab, 255 * np.array(c['M']), s, tgains, tscale) for c in cases]
                      for s in spans})
    flat = np.full_like(tab, 128.0)
    constant = dict(codes=flat.tolist(),
                    out=[table_out(flat, 255 * np.array(c['M']), 96.0, tgains, tscale) for c in cases],
                    clipped=[table_out(flat, 255 * np.clip(np.array(c['M']), 0, 1), 96.0, tgains, tscale)
                             for c in cases])

    doc = dict(source='implementation-design/u4_out_of_range.py', normalOf='each case', cases=cases,
               landed=landed, e3=dict(gains=gains, neutral=neutral, high=HIGH, runs=e3), table=table,
               constant128=constant)
    with open(OUT, 'w') as fh:
        json.dump(doc, fh, separators=(',', ':'))
        fh.write('\n')
    moved = np.abs(np.array(constant['out']) - np.array(constant['clipped'])).max(axis=1)
    print(f"{len(cases)} out-of-range composite cases ({', '.join(f'knee {k}: '
          f'{sum(c['knee'] == k for c in cases)}' for k in (0, 1, 2))}); M in "
          f"[{A.min():.4f}, {A.max():.4f}]")
    print(f"constant-128 table at span 96: a clip before the chroma term moves the output by up to "
          f"{moved.max():.2f} codes (median {np.median(moved):.2f})")


if __name__ == '__main__':
    main()
