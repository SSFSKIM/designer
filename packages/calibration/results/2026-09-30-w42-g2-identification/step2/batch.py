"""W42 G2 step 2: the family fits as one batch (clause 6's order: LT first, then every declared rival with its
declared count, in every endpoint where it is defined; the unit nulls for the 1x decision; the other rejected nulls
descriptively; LT under the 53.6-pt mask for Decision Log 5f). At most W42_POOL processes (default 5), one BLAS
thread each, a fresh process per job.

    python3.12 -B batch.py [TAG]     -> fits/<TAG>/*.json, logs/batch-<TAG>.log
"""
import os
import sys
import time
import traceback
from multiprocessing import get_context

ACTIVE = ('light-rest', 'dark-rest')
EPS = ('light-rest', 'light-inactive', 'dark-rest', 'dark-inactive')
RIVALS = ('LT-2k', 'free-sn', 'R1', 'W-shape', 'W-canvas', 'W-tails', 'K2', 'C-linear', 'edge-swap')
BLEEDS = ('LT+bleed-lit-pre', 'LT+bleed-lit-post', 'LT+bleed-lit-own-pre', 'LT+bleed-lit-own-post', 'LT+bleed',
          'LT+bleed-own')
UNITS = ('null-texel', 'null-dev')
NULLS = ('null-mix', 'null-R2', 'null-boxfloor')
COST = {'free-sn': 9, 'W-tails': 8, 'K2': 7, 'W-shape': 7, 'LT-2k': 6, 'LT+bleed-lit-own-pre': 6,
        'LT+bleed-lit-own-post': 6, 'LT+bleed-own': 6}


def jobs():
    out = [('LT', ep, 'n') for ep in EPS]
    out += [(f, ep, 'n') for f in RIVALS for ep in EPS]
    out += [(f, ep, 'n') for f in BLEEDS for ep in ACTIVE]
    out += [('LT', ep, 'w') for ep in ACTIVE]
    out += [(f, ep, 'n') for f in UNITS for ep in EPS]
    out += [(f, ep, 'n') for f in NULLS for ep in EPS]
    head = out[:4]
    rest = sorted(out[4:], key=lambda j: -COST.get(j[0], 3))
    return head + rest


def one(args):
    fam, ep, kernel, tag = args
    t0 = time.time()
    if os.path.exists(f'fits/{tag}/{fam}__{ep}__{kernel}.json'):
        return f'{fam:24s} {ep:15s} {kernel} skipped: already fitted by another worker'
    try:
        import fit_family
        r = fit_family.run(fam, ep, kernel, (2, 1), tag)
        return (f"{fam:24s} {ep:15s} {kernel} {time.time() - t0:6.0f}s survives {r['survives']} "
                f"ls {r['ls']['params']} lam {r['ls']['lam']} fail {r['ls']['failures']} worst "
                f"{max(r['ls']['calibration']['worstMeasured'], r['ls']['validation']['worstMeasured']):.2f} | mm "
                f"{r['minimax']['params']} lam {r['minimax']['lam']} fail {r['minimax']['failures']} worst "
                f"{max(r['minimax']['calibration']['worstMeasured'], r['minimax']['validation']['worstMeasured']):.2f}")
    except Exception:
        return f'{fam} {ep} {kernel} FAILED\n' + traceback.format_exc()


if __name__ == '__main__':
    tag = sys.argv[1] if len(sys.argv) > 1 else 'main'
    only = [x for x in os.environ.get('W42_ONLY', '').split(',') if x]
    todo = [j for j in jobs() if not only or j[0] in only]
    done = {f for f in os.listdir(f'fits/{tag}')} if os.path.isdir(f'fits/{tag}') else set()
    todo = [(f, e, k, tag) for f, e, k in todo if f'{f}__{e}__{k}.json' not in done]
    print(f'{len(todo)} jobs', flush=True)
    with get_context('spawn').Pool(int(os.environ.get('W42_POOL', '5')), maxtasksperchild=1) as pool:
        for line in pool.imap_unordered(one, todo):
            print(time.strftime('%H:%M:%S'), line, flush=True)
    print('BATCH DONE', flush=True)
