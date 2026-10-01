#!/usr/bin/env python3.12
"""W43 G0 (c): memo F's reader proved before the window (writes proof-read.txt beside this file).

    python3.12 -B proof_read.py

Three inputs whose answers are known:
1. **memo D's own dumps** (~/vitrea-w42/grounding/dumps/runs/, checked against the grounding's
   committed scratch-sha256.txt), arranged as an x = 0.5 run at both scales: no field may move,
   memo D may not depart from itself, and the 1x-against-2x control must find exactly memo D's
   four one-device-pixel terms and nothing beyond them.
2. **a stub run** of the driver (proof.py's tools; its ramps are W29's light readings, its dark
   moves the Normal weight only): the reader must find exactly those fields moving, with W29's
   slopes, the backdrop controls identical and the 1x block at 0.25 within memo D's terms.
3. **W29 G0's one-scene sweep** (light active photo rrect-md at 0, 0.25, 0.5 and 1; scratch
   ~/vitrea-w29-g0-scratch/d/dump-sweep/): the reader must recover W29's committed table (Normal
   = x; the face fill alpha 0, 0.1, 0.2, 0.5; Lighten 0.675, 0.7875, 0.9, 0.9). What else it
   reads there is a pointer and is written to `w29-sweep-reading/`.
"""
import hashlib
import json
from pathlib import Path
import shutil
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import memo_f_read as MR  # noqa: E402
import proof as P  # noqa: E402

MEMO_D = Path.home() / 'vitrea-w42/grounding'
W29 = Path.home() / 'vitrea-w29-g0-scratch/d/dump-sweep'
G = MR.G
RESULTS = []


def expect(what, ok, detail=''):
    RESULTS.append((what, bool(ok), detail))


def memo_d_as_run(tmp):
    want = {ln.split()[1]: ln.split()[0] for ln in P.GROUNDING.read_text().splitlines() if ln.strip()}
    root = tmp / 'memo-d-run'
    for scale in (1, 2):
        for scheme in ('light', 'dark'):
            for pose in ('active', 'inactive'):
                d = root / 'runs' / f'x0.5-{scale}x-{scheme}-{pose}'
                (d / 'json').mkdir(parents=True)
                for p in sorted((MEMO_D / f'dumps/runs/{scale}x-{scheme}-{pose}/json').glob('*.json')):
                    rel = str(p.relative_to(MEMO_D))
                    raw = p.read_bytes()
                    assert want[rel] == hashlib.sha256(raw).hexdigest(), rel
                    if 'toolbar-group' in p.name or 'glass-over-glass' in p.name:
                        continue        # memo F declares single shapes
                    (d / 'json' / p.name).write_bytes(raw)
                (d / 'admission.json').write_text(json.dumps(dict(x=0.5, scale=scale, scheme=scheme, pose=pose)))
    return root


def main():
    reference = json.loads((MR.DUMPCHECK / 'dump-reference.json').read_text())
    tmp = Path(tempfile.mkdtemp(prefix='memo-f-proof-read-'))
    try:
        r = MR.read(MR.load_run(memo_d_as_run(tmp)), reference)
        expect('memo D as a run: no field moves (one position)', all(not e['moving'] for e in r['endpoints'].values()))
        deps = {ep: e['departuresByX'].get('0.5') for ep, e in r['endpoints'].items()}
        expect('memo D as a run: zero departures from its own reference in all eight endpoint-scales',
               all(v == {} for v in deps.values()), json.dumps(deps)[:300])
        beyond = {k: v['beyondMemoD'] for k, v in r['scale'].items() if v['beyondMemoD']}
        found = set().union(*[set(v['differing']) for v in r['scale'].values()])
        expect('memo D as a run: 1x against 2x differs only in its four device-pixel terms, and they are found',
               not beyond and found == MR.DEVICE_PX, f'beyond {beyond}; found {sorted(found)}')

        c = P.Case('read')
        try:
            c.as_found('<real>0.5</real>')
            rc, out = c.run()
            expect('the stub run completes', rc == 0, out[-200:])
            s = MR.read(MR.load_run(c.root), reference)
        finally:
            c.close()
        light = {f for ep, e in s['endpoints'].items() if 'light' in ep for f in e['moving']}
        dark = {f for ep, e in s['endpoints'].items() if 'dark' in ep for f in e['moving']}
        expect('stub: light moves exactly Normal, Lighten and the face fill',
               light == {G + 'BlurFillNormalOpacity', G + 'BlurFillLightenOpacity', G + 'FaceColorMatrixFillColor'},
               sorted(light))
        expect('stub: dark moves exactly Normal', dark == {G + 'BlurFillNormalOpacity'}, sorted(dark))
        la = s['endpoints']['2x-light-active']['ramps']
        pw = lambda f: la[f]['piecewise'][next(iter(la[f]['piecewise']))]  # noqa: E731
        expect('stub: the ramps read W29\'s slopes, span-invariant, exactly piecewise linear',
               all(la[f]['spanInvariant'] for f in la)
               and (pw(G + 'BlurFillLightenOpacity')['[0, 0.5]']['slope'], pw(G + 'BlurFillLightenOpacity')['[0.5, 1]']['slope'])
               == (0.45, 0.0)
               and (pw(G + 'FaceColorMatrixFillColor')['[0, 0.5]']['slope'], pw(G + 'FaceColorMatrixFillColor')['[0.5, 1]']['slope'])
               == (0.4, 0.6)
               and all(v['maxResidual'] < 1e-6 for f in la for p in la[f]['piecewise'].values() for v in p.values() if v))
        expect('stub: every backdrop control identical', s['backdrop'] and all(not v for v in s['backdrop'].values()),
               json.dumps(s['backdrop'])[:200])
        expect('stub: 1x at 0.25 within memo D\'s device-pixel terms',
               s['scale'] and all(not v['beyondMemoD'] for v in s['scale'].values()))
        expect('stub: no memo D law departs at any x',
               all(v['layer'] != 'law' for e in s['endpoints'].values() for d in e['departuresByX'].values()
                   for v in d.values()))

        inputs = {str(p.relative_to(W29)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in sorted(W29.glob('*/*.json'))}
        w = MR.read(MR.load_w29(W29), reference)
        e = w['endpoints']['2x-light-active']
        vals = lambda f: [v for _, v in sorted(next(iter(e['ramps'][f]['values'].values())).items(),  # noqa: E731
                                               key=lambda kv: float(kv[0]))]
        expect("W29 sweep: W29's committed table recovered (Normal, fill alpha, Lighten at 0, 0.25, 0.5, 1)",
               vals(G + 'BlurFillNormalOpacity') == [0, 0.25, 0.5, 1]
               and [round(v, 4) for v in vals(G + 'FaceColorMatrixFillColor')] == [0, 0.1, 0.2, 0.5]
               and [round(v, 4) for v in vals(G + 'BlurFillLightenOpacity')] == [0.675, 0.7875, 0.9, 0.9])
        out = HERE / 'w29-sweep-reading'
        out.mkdir(exist_ok=True)
        (out / 'tables.json').write_text(json.dumps(dict(inputs=inputs, source=str(W29), reading=w), indent=1,
                                                    sort_keys=True, default=MR.plain) + '\n')
        (out / 'reading.txt').write_text(MR.text(w))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    lines = [f'memo F reader proof: {sum(ok for _, ok, _ in RESULTS)} of {len(RESULTS)} expectations hold', '']
    lines += [f"{'PASS' if ok else 'FAIL'}  {what}" + (f'  [{d}]' if d and not ok else '') for what, ok, d in RESULTS]
    (HERE / 'proof-read.txt').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))
    return 0 if all(ok for _, ok, _ in RESULTS) else 1


if __name__ == '__main__':
    sys.exit(main())
