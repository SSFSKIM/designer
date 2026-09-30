"""W42 G0 instrument, finding I-4, the reader files whose committed JSON was written by an EARLIER version of the
reader code than the commit that holds it (their rows lack keys the committed code writes: 'section', 'checks',
'reads', 'pairs_kept'). A whole-file diff of their token-key replay against the record mixes that code revision
with the key, so each is compared by the rows summarize_a.py actually cites:

- proof1_readers_a.<ep>.all.json: a section re-run in a later file ('model', 'mirror,band', 'impulse,band')
  replaces that section of the 'all' run (summarize_a.load), so only the sections no later file replaces are
  cited: esf, heavy, exclusion, the linear control, and impulse in the dark endpoints;
- proof3_readers_a.<ep>.json: its 'mirror' field is replaced by the mirror-only re-run (<ep>.mirror.json,
  summarize_a lines 543-548), so every other field is cited.

For the one cited section that still differs, the linear control, the probe (`--probe`) counts the calls it makes
into the shared blur store (forward.Cell.blur, forward.maps): none, so no key can have reached it, and its
difference is the reader revision alone.

Usage: python3.12 i4_sections.py            -> i4_sections.json / i4_sections.txt beside this file
       python3.12 i4_sections.py --probe    (run through the compute lock) -> /tmp/w42fix/i4-out/linear-probe.json
"""
import collections
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REL = 'packages/calibration/results/2026-09-29-w42-g0-declaration/instrument'
ROOT = f'/tmp/w42fix/i4-7efe4ce8-07b45391/{REL}'
EPS = ('light-rest', 'light-inactive', 'dark-rest', 'dark-inactive')
PROBE = '/tmp/w42fix/i4-out/linear-probe.json'


def section_of(r):
    """summarize_a.section_of, copied so this file imports nothing that reads the cwd."""
    if r.get('mirror_only'):
        return 'proof3-mirror'
    if 'section' in r:
        return r['section']
    if 'band' in r and 'd_in' in r:
        return 'band'
    return {'linear-control': 'linear', 'esf-linear-control': 'esf', 'impulse-linear-control': 'impulse',
            'exclusion': 'exclusion'}.get(r.get('reader'), r.get('reader', 'proof3'))


def leaves(a, b, path, out, skip=('section',)):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in set(a) | set(b):
            if k not in skip:
                leaves(a.get(k), b.get(k), f'{path}.{k}', out, skip)
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((path, f'len {len(a)}', f'len {len(b)}'))
            return
        for i, (x, y) in enumerate(zip(a, b)):
            leaves(x, y, f'{path}[{i}]', out, skip)
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool):
        if a != a and b != b:
            return
        if abs(a - b) > 1e-9 * max(1, abs(a), abs(b)):
            out.append((path, a, b))
    elif a != b:
        out.append((path, str(a)[:40], str(b)[:40]))


def ident(r):
    return (section_of(r), r.get('cell'), r.get('reader'), json.dumps(r.get('truth'), sort_keys=True, default=str),
            r.get('scale'), r.get('src'))


def compare(name, sections=None, drop=()):
    rec = json.loads(subprocess.run(['git', '-C', HERE, 'show', f'7efe4ce8:{REL}/{name}'], capture_output=True,
                                    check=True).stdout)
    got = json.load(open(f'{ROOT}/{name}'))
    R, Gd = collections.defaultdict(list), collections.defaultdict(list)
    for r in rec:
        R[ident(r)].append(r)
    for r in got:
        Gd[ident(r)].append(r)
    out = collections.defaultdict(lambda: dict(rows=0, differ=0, unmatched=0, max_numeric=0.0, where=None, other=[]))
    for k in set(R) | set(Gd):
        if sections is not None and k[0] not in sections:
            continue
        s = out[k[0]]
        if len(R.get(k, [])) != len(Gd.get(k, [])):
            s['unmatched'] += 1
            continue
        for a, b in zip(R[k], Gd[k]):
            o = []
            leaves({x: y for x, y in a.items() if x not in drop}, {x: y for x, y in b.items() if x not in drop}, '', o)
            s['rows'] += 1
            if o:
                s['differ'] += 1
            for p, x, y in o:
                if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                    if abs(x - y) > s['max_numeric']:
                        s['max_numeric'], s['where'] = abs(x - y), f'{k[1]}{p}: {x} -> {y}'
                elif len(s['other']) < 4:
                    s['other'].append(f'{k[1]}{p}: {x} -> {y}')
    return dict(file=name, sections=dict(out))


def cited_sections(ep):
    later = {'model', 'mirror', 'band'} | ({'impulse'} if ep in ('light-rest', 'light-inactive') else set())
    return {'esf', 'heavy', 'exclusion', 'linear', 'impulse', 'model', 'mirror', 'band'} - later


def probe():
    sys.path.insert(0, ROOT)
    os.chdir(ROOT)
    import forward as F
    calls = {'blur': 0, 'maps': 0}
    _b, _m = F.Cell.blur, F.maps

    def blur(self, *a, **k):
        calls['blur'] += 1
        return _b(self, *a, **k)

    def maps(*a, **k):
        calls['maps'] += 1
        return _m(*a, **k)
    F.Cell.blur, F.maps = blur, maps
    import proof1_readers_a as PA
    PA.F.maps = maps
    res = {}
    for ep in EPS:
        before = dict(calls)
        rows = PA.linear_rows(ep, lambda s: None)
        res[ep] = dict(rows=len(rows), blur_calls=calls['blur'] - before['blur'], maps_calls=calls['maps'] - before['maps'])
    json.dump(res, open(PROBE, 'w'), indent=1)
    print(res)


def main():
    rows = [compare(f'proof1_readers_a.{ep}.all.json', cited_sections(ep)) for ep in EPS]
    rows += [compare(f'proof3_readers_a.{ep}.json', drop=('mirror',)) for ep in EPS]
    pr = json.load(open(PROBE)) if os.path.exists(PROBE) else None
    json.dump(dict(cited=rows, linear_probe=pr), open(os.path.join(HERE, 'i4_sections.json'), 'w'), indent=1,
              default=float)
    L = ['W42 G0 instrument, finding I-4: the reader files written by an earlier reader revision, compared on the rows',
         'summarize_a.py cites (i4_sections.py). Per cited section: rows, rows differing, largest numeric difference.']
    for r in rows:
        L.append(f"  {r['file']}")
        for sec, s in sorted(r['sections'].items()):
            L.append(f"    {sec:10s} {s['rows']:3d} rows, {s['differ']:3d} differ, {s['unmatched']} unmatched, max "
                     f"{s['max_numeric']:.3g}" + (f" at {s['where']}" if s['where'] else '')
                     + (f"; other {s['other'][:2]}" if s['other'] else ''))
    if pr:
        L.append('  linear control, calls into the shared blur store while it runs (7efe4ce8 code): '
                 + ', '.join(f"{ep} {v['rows']} rows / {v['blur_calls']} blur / {v['maps_calls']} maps" for ep, v in pr.items()))
    open(os.path.join(HERE, 'i4_sections.txt'), 'w').write('\n'.join(L) + '\n')
    print('\n'.join(L))


if __name__ == '__main__':
    probe() if '--probe' in sys.argv else main()
