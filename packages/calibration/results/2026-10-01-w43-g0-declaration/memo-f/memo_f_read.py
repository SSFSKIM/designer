#!/usr/bin/env python3.12
"""W43 G0 (c): memo F's reading — what Apple's declared tree does as the slider moves (clause 2).

    python3.12 -B memo_f_read.py <run-root> --out <dir>           # after the window: tables.json, reading.txt
    python3.12 -B memo_f_read.py --w29-sweep <dir> --out <dir>    # W29 G0's one-scene sweep, the same reader

Reads only admitted launches (`runs/<label>/admission.json`; a quarantine is never read) and only
memo D's per-surface records (`dumpcheck.records`, unchanged). Its numbers are POINTERS (X38): the
declared inputs of a private filter, not pixels. It answers memo F's three questions:

1. **Which declared inputs move with x**, per endpoint: every field whose value at some x differs
   from its value at x = 0.5 on the same scene, with its value at every x (one value when it is
   the same on every shape, else one per span).
2. **Whether memo D's seventeen span laws and its constants hold at each x**: `dumpcheck.check`
   against memo D's reference at every x, every departure listed by field and layer (a constant
   that moves with x departs at every x but 0.5; a law that holds at x is silent).
3. **The ramps**: for every moving field, its value against x, with a piecewise-linear reading on
   [0, 0.5] and [0.5, 1] (each segment's slope and its largest residual from the chord), the knee
   W29 G0 read in the light ramps.

And two controls: at the positions that carry them, rrect-md on photo and on the checkerboard
against rrect-md on dark-solid (identical in every field but the scene's own identity, or each
difference listed); and the 1x block at 0.25 against the 2x block, which memo D read identical at
0.5 apart from four one-device-pixel terms.
"""
import argparse
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[4]
DUMPCHECK = REPO / 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/dumps'
sys.path.insert(0, str(DUMPCHECK))
import dumpcheck as DC  # noqa: E402  memo D's extract and laws, unchanged

G = DC.G
IDENTITY = set(DC.IDENTITY) | {'colorScheme', 'backingScaleFactor', 'isKeyWindow', 'appIsActive',
                               'activationPolicy'}
DEVICE_PX = {G + 'KeyFillHighlightHeight', G + 'KeyFillHighlightEffectOffset', 'bd.marginWidth', 'out.effect.maximum'}
POSES = {'active': 'active', 'inactive': 'receded'}


def records(path):
    """memo D's records, tolerant of an older dump without the pose and policy fields (W29's)."""
    raw = json.loads(Path(path).read_text())
    for k in ('appIsActive', 'isKeyWindow', 'activationPolicy', 'settleSeconds'):
        raw.setdefault(k, None)
    base = {k: raw[k] for k in ('scene', 'background', 'component', 'colorScheme', 'backingScaleFactor',
                                'isKeyWindow', 'appIsActive', 'activationPolicy', 'settleSeconds')}
    out = []
    for i, (anc, bd) in enumerate(DC.surfaces(raw['view']['layer'])):
        out.append(_record(base, i, anc, bd))
    return out


def _record(base, i, anc, bd):
    # The body of dumpcheck.records for one surface, on an already-parsed tree.
    r = dict(base)
    r['surface'] = i
    sdf = next((a for a in reversed(anc) if a.get('class') == 'SwiftUI.SDFLayer'), None)
    parent = anc[-1]
    if sdf:
        r['sdf.frame'] = tuple(sdf['frame'][k] for k in ('x', 'y', 'width', 'height'))
    r['bd.frame'] = tuple(bd['frame'][k] for k in ('x', 'y', 'width', 'height'))
    DC.props(bd.get('properties'), 'bd.', r)
    DC.filters(bd, '', r)
    for s in bd.get('sublayers') or []:
        if s.get('class') == 'CASDFLayer':
            DC.props(s.get('properties'), 'out.', r)
            elems = []

            def ew(n):
                if n.get('class') == 'CASDFElementLayer':
                    elems.append((tuple(n['frame'][k] for k in ('x', 'y', 'width', 'height')),
                                  n.get('cornerRadius'), n.get('cornerCurve'),
                                  n['properties'].get('gradientOvalization'), n['properties'].get('operation')))
                for c in n.get('sublayers') or []:
                    ew(c)
            ew(s)
            r['elements'] = tuple(elems)
    for s in parent.get('sublayers') or []:
        if s is bd:
            continue
        if s.get('class') == 'CASDFLayer':
            DC.props(s.get('properties'), 'hl.', r)
            DC.filters(s, 'hl.', r)
            r['hl.opacity'] = s.get('opacity')
    for k in ('opacity', 'compositingFilter'):
        if k in parent:
            r['parent.' + k] = parent.get(k)
    return r


def span(r):
    (_, _, w, h), *_ = r['elements'][0]
    return min(w, h)


def plain(v):
    return list(v) if isinstance(v, tuple) else v


def same(a, b):
    return DC.near(plain(a), plain(b)) if not isinstance(a, (list, tuple)) else \
        isinstance(b, (list, tuple)) and len(a) == len(b) and all(same(p, q) for p, q in zip(a, b))


def load_run(root):
    """{(x, scale, scheme, pose): {scene: record}} from the admitted launches only."""
    out = {}
    for adm in sorted(Path(root).glob('runs/*/admission.json')):
        a = json.loads(adm.read_text())
        key = (a['x'], a['scale'], a['scheme'], POSES[a['pose']])
        for p in sorted((adm.parent / 'json').glob('*.json')):
            recs = records(p)
            if len(recs) != 1:
                raise ValueError(f'{p}: memo F declares single shapes; {len(recs)} surfaces')
            out.setdefault(key, {})[recs[0]['scene']] = recs[0]
    return out


def load_w29(directory):
    """W29 G0's sweep: one scene (light, active, 2x) per arm directory named by the slider value."""
    out = {}
    for d in sorted(Path(directory).iterdir()):
        if not d.is_dir():
            continue
        try:
            x = float(d.name)
        except ValueError:
            continue    # the key-deleted arm is not a position
        for p in sorted(d.glob('*.json')):
            r = records(p)[0]
            out.setdefault((x, 2, 'light', 'active'), {})[r['scene']] = r
    return out


def piecewise(points):
    """Per segment [0, 0.5] and [0.5, 1]: the chord's slope and the largest residual from it."""
    out = {}
    for name, lo, hi in (('[0, 0.5]', 0.0, 0.5), ('[0.5, 1]', 0.5, 1.0)):
        seg = sorted((x, v) for x, v in points.items() if lo <= x <= hi and isinstance(v, (int, float)))
        if len(seg) < 2 or seg[0][0] != lo or seg[-1][0] != hi:
            out[name] = None
            continue
        (x0, v0), (x1, v1) = seg[0], seg[-1]
        slope = (v1 - v0) / (x1 - x0)
        resid = max(abs(v - (v0 + slope * (x - x0))) for x, v in seg)
        out[name] = dict(slope=round(slope, 6), maxResidual=round(resid, 6), points=len(seg))
    return out


def scalar_of(v):
    """A field's number for the ramp table: a colour's alpha, a float, else None."""
    if isinstance(v, (list, tuple)) and len(v) == 4 and all(isinstance(c, (int, float)) for c in v):
        return v[3]
    return v if isinstance(v, (int, float)) and not isinstance(v, bool) else None


def read(data, reference):
    positions = sorted({k[0] for k in data})
    endpoints = sorted({k[1:] for k in data})
    result = dict(positions=positions, endpoints={}, backdrop={}, scale={})
    for scale, scheme, pose in endpoints:
        ep = f'{scale}x-{scheme}-{pose}'
        base = data.get((0.5, scale, scheme, pose))
        e = dict(moving={}, departuresByX={}, ramps={})
        if base is None:
            e['note'] = 'no x = 0.5 block at this scale: moving fields are read against memo D only'
        for x in positions:
            block = data.get((x, scale, scheme, pose))
            if not block:
                continue
            deps = {}
            for sid, r in block.items():
                d, u, _ = DC.check(r, scheme, pose, scale, reference)
                for dep in d:
                    if dep['field'] in IDENTITY:     # the pose is the launch check's (memo_f.py check)
                        continue
                    deps.setdefault(dep['field'], []).append(dict(scene=sid, s=span(r), got=plain(dep['got']),
                                                                 want=plain(dep['want']), layer=dep['layer']))
            e['departuresByX'][repr(x)] = {f: dict(layer=v[0]['layer'], scenes=len(v), values=sorted(
                {json.dumps(x_['got']) for x_ in v})) for f, v in sorted(deps.items())}
            if base:
                for sid, r in block.items():
                    b = base.get(sid)
                    if b is None:
                        continue
                    for f in sorted(set(r) | set(b)):
                        if f in IDENTITY or f in ('scene', 'background', 'component'):
                            continue
                        if not same(r.get(f), b.get(f)):
                            e['moving'].setdefault(f, {}).setdefault(repr(x), {})[str(span(r))] = plain(r.get(f))
        for f, by_x in e['moving'].items():
            spans = {}
            for x in positions:
                block = data.get((x, scale, scheme, pose)) or {}
                for sid, r in block.items():
                    if sid.startswith('dark-solid__') or len(block) == 1:
                        spans.setdefault(str(span(r)), {})[x] = scalar_of(r.get(f))
            invariant = all(len({json.dumps(v.get(x)) for v in spans.values()}) == 1 for x in positions
                            if all(x in v for v in spans.values()))
            e['ramps'][f] = dict(spanInvariant=invariant,
                                 values={s: {repr(x): v for x, v in sorted(pts.items())} for s, pts in spans.items()},
                                 piecewise={s: piecewise(pts) for s, pts in spans.items()})
        result['endpoints'][ep] = e
    # the backdrop control: rrect-md on photo and on the checkerboard against dark-solid
    for (x, scale, scheme, pose), block in sorted(data.items()):
        ref = block.get('dark-solid__rrect-md__rest')
        for other in ('photo__rrect-md__rest', 'checkerboard__rrect-md__rest'):
            if ref is None or other not in block:
                continue
            r = block[other]
            diff = sorted(f for f in set(r) | set(ref) if f not in IDENTITY and f not in ('scene', 'background')
                          and not same(r.get(f), ref.get(f)))
            result['backdrop'][f'x{x:g} {scale}x-{scheme}-{pose} {other}'] = diff
    # the scale control: every 1x block against the 2x block at the same x
    for (x, scale, scheme, pose), block in sorted(data.items()):
        if scale != 1:
            continue
        two = data.get((x, 2, scheme, pose)) or {}
        for sid, r in sorted(block.items()):
            if sid not in two:
                continue
            diff = sorted(f for f in set(r) | set(two[sid]) if f not in IDENTITY and not same(r.get(f), two[sid].get(f)))
            result['scale'][f'x{x:g} {scheme}-{pose} {sid}'] = dict(
                differing=diff, beyondMemoD=sorted(set(diff) - DEVICE_PX))
    return result


def text(result):
    lines = [f"memo F reading: positions {result['positions']}", '']
    for ep, e in result['endpoints'].items():
        lines.append(f'== {ep}')
        if e.get('note'):
            lines.append('  ' + e['note'])
        moving = sorted(e['moving'])
        lines.append(f"  inputs that move with x ({len(moving)}): " + (', '.join(f.replace(G, '') for f in moving) or 'none'))
        for f in moving:
            ramp = e['ramps'][f]
            for s, pts in ramp['values'].items():
                if ramp['spanInvariant'] and s != sorted(ramp['values'])[0]:
                    continue
                vals = ' '.join(f"{x}:{'—' if v is None else round(v, 6)}" for x, v in pts.items())
                pw = ramp['piecewise'][s]
                pws = '; '.join(f"{k} slope {v['slope']:+g} (resid {v['maxResidual']:g})" for k, v in pw.items() if v)
                where = 'all spans' if ramp['spanInvariant'] and len(ramp['values']) > 1 else 's=' + s
                lines.append(f"    {f.replace(G, ''):40s} {where:10s} {vals}"
                             + (f'  | {pws}' if pws else ''))
        for x, deps in e['departuresByX'].items():
            if deps:
                laws = [f.replace(G, '') for f, v in deps.items() if v['layer'] == 'law']
                lines.append(f"  x={x}: memo D departs on {len(deps)} field(s); laws among them: {laws or 'none'}")
        lines.append('')
    if result['backdrop']:
        lines.append('== backdrop control (rrect-md on photo / checkerboard against dark-solid)')
        for k, diff in result['backdrop'].items():
            lines.append(f"  {k}: {'identical' if not diff else diff}")
        lines.append('')
    if result['scale']:
        bad = {k: v for k, v in result['scale'].items() if v['beyondMemoD']}
        lines.append(f"== scale control: {len(result['scale'])} scene-endpoints at 1x against 2x; "
                     f"{len(bad)} differ beyond memo D's four device-pixel terms")
        for k, v in bad.items():
            lines.append(f"  {k}: {v['beyondMemoD']}")
    return '\n'.join(lines) + '\n'


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('root', nargs='?')
    ap.add_argument('--w29-sweep', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args(argv)
    reference = json.loads((DUMPCHECK / 'dump-reference.json').read_text())
    data = load_w29(args.w29_sweep) if args.w29_sweep else load_run(args.root)
    result = read(data, reference)
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / 'tables.json').write_text(json.dumps(result, indent=1, sort_keys=True, default=plain) + '\n')
    t = text(result)
    (args.out / 'reading.txt').write_text(t)
    print(t)


if __name__ == '__main__':
    main()
