#!/usr/bin/env python3.12
"""Check a `dump-layers` output against memo D's declared configuration (charter clause 4's stop).

Memo D (packages/calibration/results/2026-09-29-w42-grounding/w42-dumps.txt) read Apple's
declared glass configuration on the W39 side bundle: 26 surfaces x 4 endpoints x 2 scales,
reproduced by seventeen closed-form span laws in t = clamp((s - 64)/96, 0, 1). This module
turns that reading into a checker the sitting runs over every dump of the declared bed
BEFORE its first capture: a surface that departs stops the sitting (clause 4).

A surface is checked in three layers:

1. CONSTANTS. Every field memo D read identical on all surfaces of an endpoint at a scale
   (the blur radius 5, the fill radius 8 with its Lighten/Darken/Normal opacities, the face
   matrix, the clamp, the highlight, the pose attestation, ...) must equal memo D's value.
   `reference` derives these from memo D's own dumps into dump-reference.json.
2. LAWS. Every field that varies with span is checked against memo D's law (laws.py, plus
   the dark MaxLumaSDR = MaxLuma, the fill spread = the key spread, smoothness 8 on a single
   shape, the element's corner and ovalisation, the receded SDF maximum 1 pt + 1 dev, and
   the backdrop scale 0.5, or 0.25 on rrect-lg), to 1e-3 as memo D verified them.
3. PER-SHAPE READINGS. The active SDF output maximum "tracks the shadow" and has no closed
   form in memo D; a shape memo D dumped must reproduce its value, and a shape it did not
   (the bed's rrect-112) is reported UNPREDICTED, never a departure. The backdrop scale of
   an unseen shape is predicted 0.5 by both readings memo D leaves open (short side <= 128
   and area <= 28,672); a disagreement is a departure.

Derived from memo D's extract.py and laws.py (scratch under ~/vitrea-w42/grounding/dumps/,
hashed in the grounding's scratch-sha256.txt); those are not edited.
"""
import argparse
import glob
import hashlib
import json
import math
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G = 'glassBackground.input'
DROP = re.compile(r'(description|sourceContextId|sourceLayerRenderId|groupName|sourceLayer)$')
IDENTITY = ('scene', 'background', 'component', 'surface', 'bd.frame', 'sdf.frame', 'elements',
            'settleSeconds')
TOL = 1e-3


# ------------------------------------------------------------- memo D's extract

def scalar(v):
    if isinstance(v, dict):
        if 'float32' in v:
            return tuple(round(x, 6) for x in v['float32'])
        if 'cgColorComponents' in v:
            return tuple(round(x, 6) for x in v['cgColorComponents'])
        if 'description' in v and v.get('class') == 'NSConcreteValue':
            return v['description']
        return None
    if isinstance(v, float):
        return round(v, 6)
    return v


def props(d, prefix, out):
    for k, v in (d or {}).items():
        if DROP.search(k):
            continue
        if isinstance(v, dict) and 'properties' in v and 'class' in v and 'float32' not in v:
            out[prefix + k + '.class'] = v['class']
            props(v['properties'], prefix + k + '.', out)
            continue
        s = scalar(v)
        if s is not None or v is None:
            out[prefix + k] = s


def filters(layer, prefix, out):
    for f in layer.get('filters') or []:
        t = f.get('type') or f.get('name')
        for k, v in (f.get('inputs') or {}).items():
            out[f'{prefix}{t}.{k}'] = scalar(v)


def surfaces(root):
    res = []

    def walk(n, anc):
        if not isinstance(n, dict):
            return
        if n.get('class') == 'CABackdropLayer':
            res.append((anc, n))
        for s in n.get('sublayers') or []:
            walk(s, anc + [n])
    walk(root, [])
    return res


def records(path):
    d = json.loads(Path(path).read_text())
    base = {k: d[k] for k in ('scene', 'background', 'component', 'colorScheme', 'backingScaleFactor',
                              'isKeyWindow', 'appIsActive', 'activationPolicy', 'settleSeconds')}
    out = []
    for i, (anc, bd) in enumerate(surfaces(d['view']['layer'])):
        r = dict(base)
        r['surface'] = i
        sdf = next((a for a in reversed(anc) if a.get('class') == 'SwiftUI.SDFLayer'), None)
        parent = anc[-1]
        if sdf:
            r['sdf.frame'] = tuple(sdf['frame'][k] for k in ('x', 'y', 'width', 'height'))
        r['bd.frame'] = tuple(bd['frame'][k] for k in ('x', 'y', 'width', 'height'))
        props(bd.get('properties'), 'bd.', r)
        filters(bd, '', r)
        for s in bd.get('sublayers') or []:
            if s.get('class') == 'CASDFLayer':
                props(s.get('properties'), 'out.', r)
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
                props(s.get('properties'), 'hl.', r)
                filters(s, 'hl.', r)
                r['hl.opacity'] = s.get('opacity')
        for k in ('opacity', 'compositingFilter'):
            if k in parent:
                r['parent.' + k] = parent.get(k)
        out.append(r)
    return out


# ------------------------------------------------------------------ the laws

def t_of(s):
    return min(1.0, max(0.0, (s - 64) / 96))


def laws(scheme, pose, scale):
    act, light, dev = pose == 'active', scheme == 'light', 1 / scale
    return {
        G + 'BlurOpacity0': lambda s: 0.8 * t_of(s) if act else 0.4 + 0.4 * t_of(s),
        G + 'BlurOpacity1': lambda s: 0.4 * t_of(s) if act else 0.4 + 0.4 * t_of(s),
        G + 'BlurDistance0': lambda s: -s / 2 if act else 0,
        G + 'InnerRefractionAmount': lambda s: -min(s / 2, 60),
        G + 'InnerRefractionHeight': lambda s: min(s / 4, 20),
        G + 'OuterRefractionAmount': lambda s: max(16, s / 4) if act else 0,
        G + 'OuterRefractionHeight': lambda s: max(16, s / 5) if act else 0,
        G + 'BleedAmount': lambda s: 0.35 * s,
        G + 'BleedHeight': lambda s: 0.35 * s,
        G + 'BleedBlurRadius': lambda s: (0.35 * s if s > 64 else 0) if act else 0,
        G + 'BleedOpacity': lambda s: ((0.5 if light else 0.8) * t_of(s)) if act else 0,
        G + 'ShadowOpacity': lambda s: (0.04 + (0.36 if light else 0.56) * t_of(s)) if act else 0,
        G + 'ShadowRadius': lambda s: (4 + 20 * t_of(s)) if act else 0,
        G + 'FaceColorMatrixMaxLuma': lambda s: 1 if light else max(0.35, 0.6 - 0.6 * t_of(s)),
        G + 'FaceColorMatrixMaxLumaSDR': lambda s: 0.94 if light else max(0.35, 0.6 - 0.6 * t_of(s)),
        # Active: 0.35 s past the knot, else 16 pt; receded: one device pixel (memo D §4).
        'bd.marginWidth': lambda s: (0.35 * s if s > 64 else 16) if act else dev,
        'hl.effect.keySpread': lambda s: math.radians(80 + max(0, s - 96) * 10 / 96),
        'hl.effect.fillSpread': lambda s: math.radians(80 + max(0, s - 96) * 10 / 96),
        'hl.smoothness': lambda s: 8,
        'out.smoothness': lambda s: 8,
    }


def backdrop_scale(w, h):
    """0.25 on rrect-lg (280 x 160) and 0.5 on every other dumped shape. Memo D cannot say
    whether span or area sets the step (§3), so an unseen shape is predicted 0.5 only where
    both readings agree with the largest 0.5 shapes dumped (short side <= 130, glass-over-
    glass's base; area <= 28,672, rrect-ml's), and is otherwise unpredicted."""
    if (w, h) == (280, 160):
        return 0.25
    if min(w, h) <= 130 and w * h <= 224 * 128:
        return 0.5
    return None


def near(a, b):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) \
            and not isinstance(b, bool):
        return abs(a - b) <= TOL
    return a == b


def endpoint_key(scheme, pose, scale):
    return f'{scale}x-{scheme}-{pose}'


def check(r, scheme, pose, scale, reference):
    """(departures, unpredicted, readings) for one surface record."""
    ref = reference['endpoints'][endpoint_key(scheme, pose, scale)]
    departures, unpredicted = [], []
    for k, want in ref['constants'].items():
        got = r.get(k)
        got = list(got) if isinstance(got, tuple) else got
        if not near(got, want):
            departures.append(dict(field=k, got=got, want=want, layer='constant'))
    missing = sorted(set(r) - set(ref['constants']) - set(ref['varying']) - set(IDENTITY))
    for k in missing:
        departures.append(dict(field=k, got=r[k], want='absent in memo D', layer='constant'))
    elements = r.get('elements') or ()
    if len(elements) != 1:
        departures.append(dict(field='elements', got=len(elements), want=1, layer='shape'))
        return departures, unpredicted, {}
    (ex, ey, w, h), corner, curve, oval, op = elements[0]
    s = min(w, h)
    for k, f in laws(scheme, pose, scale).items():
        if not near(r.get(k), f(s)):
            departures.append(dict(field=k, got=r.get(k), want=f(s), layer='law', s=s))
    want_oval = (0.5 if s > 64 else 0) if pose == 'active' else 0
    if not near(oval, want_oval) or curve != 'continuous' or op != 'union':
        departures.append(dict(field='elements', got=[oval, curve, op], want=[want_oval, 'continuous', 'union'],
                               layer='law'))
    want_scale = backdrop_scale(w, h)
    if want_scale is None:
        unpredicted.append(dict(field='bd.scale', got=r.get('bd.scale')))
    elif not near(r.get('bd.scale'), want_scale):
        departures.append(dict(field='bd.scale', got=r.get('bd.scale'), want=want_scale, layer='law', s=s))
    maximum = r.get('out.effect.maximum')
    if pose == 'receded':
        if not near(maximum, 1 + 1 / scale):
            departures.append(dict(field='out.effect.maximum', got=maximum, want=1 + 1 / scale, layer='law'))
    else:
        seen = ref['sdfMaximumByShape'].get(f'{w:g}x{h:g}')
        if seen is None:
            unpredicted.append(dict(field='out.effect.maximum', got=maximum,
                                    note='active SDF maximum tracks the shadow; memo D dumped no such shape'))
        elif not near(maximum, seen):
            departures.append(dict(field='out.effect.maximum', got=maximum, want=seen, layer='per-shape'))
    readings = {'s': s, 't': round(t_of(s), 6), 'blurOpacityCentre': r.get(G + 'BlurOpacity0'),
                'blurOpacityEdge': r.get(G + 'BlurOpacity1'), 'blurDistance0': r.get(G + 'BlurDistance0'),
                'blurRadius': r.get(G + 'BlurRadius'), 'fill': [r.get(G + 'BlurFillBlurRadius'),
                                                                   r.get(G + 'BlurFillLightenOpacity'),
                                                                   r.get(G + 'BlurFillDarkenOpacity'),
                                                                   r.get(G + 'BlurFillNormalOpacity')],
                'backdropScale': r.get('bd.scale'), 'marginWidth': r.get('bd.marginWidth'),
                'pose': [r.get('isKeyWindow'), r.get('appIsActive'), r.get('activationPolicy')]}
    return departures, unpredicted, readings


def check_dir(directory, scheme, pose, scale, reference, expected=None):
    files = sorted(glob.glob(str(Path(directory) / '*.json')))
    report = dict(directory=str(directory), endpoint=endpoint_key(scheme, pose, scale), files=len(files),
                  surfaces=[], departures=0, unpredicted=0)
    got_scenes = set()
    for path in files:
        for r in records(path):
            got_scenes.add(r['scene'])
            departures, unpredicted, readings = check(r, scheme, pose, scale, reference)
            report['surfaces'].append(dict(file=Path(path).name, scene=r['scene'], surface=r['surface'],
                                           sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                                           readings=readings, departures=departures, unpredicted=unpredicted))
            report['departures'] += len(departures)
            report['unpredicted'] += len(unpredicted)
    if expected is not None:
        missing = sorted(set(expected) - got_scenes)
        extra = sorted(got_scenes - set(expected))
        report['missingScenes'], report['extraScenes'] = missing, extra
        report['departures'] += len(missing) + len(extra)
    return report


# --------------------------------------------------------------- reference

RUNS = [('2x', 2), ('1x', 1)]
POSES = {'active': 'active', 'inactive': 'receded'}


def build_reference(memo_d):
    memo_d = Path(memo_d)
    out = dict(schema='w42-dump-reference-1', source='memo D runs under ~/vitrea-w42/grounding/dumps/runs',
               endpoints={}, inputs={})
    for tag, scale in RUNS:
        for scheme in ('light', 'dark'):
            for raw, pose in POSES.items():
                run = memo_d / 'runs' / f'{tag}-{scheme}-{raw}'
                rows = []
                for p in sorted(run.glob('json/*.json')):
                    out['inputs'][str(p.relative_to(memo_d))] = hashlib.sha256(p.read_bytes()).hexdigest()
                    rows += records(p)
                keys = set().union(*[r.keys() for r in rows]) - set(IDENTITY)
                constants, varying = {}, []
                for k in sorted(keys):
                    values = {json.dumps(r.get(k), sort_keys=True, default=list) for r in rows}
                    if len(values) == 1:
                        v = rows[0].get(k)
                        constants[k] = list(v) if isinstance(v, tuple) else v
                    else:
                        varying.append(k)
                sdf = {}
                if pose == 'active':
                    for r in rows:
                        (_, _, w, h), *_ = r['elements'][0]
                        sdf.setdefault(f'{w:g}x{h:g}', r['out.effect.maximum'])
                out['endpoints'][endpoint_key(scheme, pose, scale)] = dict(
                    surfaces=len(rows), constants=constants, varying=varying, sdfMaximumByShape=sdf)
    return out


def selftest(memo_d, reference):
    """Memo D's own dumps (both scales, the settle-16 repeats) must pass; a mutated surface must fail."""
    memo_d = Path(memo_d)
    results = []
    for run in sorted((memo_d / 'runs').iterdir()):
        m = re.fullmatch(r'(1|2)x-(light|dark)-(active|inactive)(-settle16)?', run.name)
        if not m:
            continue
        rep = check_dir(run / 'json', m[2], POSES[m[3]], int(m[1]), reference)
        # The W42 bed declares single shapes only; memo D's toolbar-group is three union
        # elements in one backdrop layer, outside this checker's scope, and is set aside.
        kept = [x for x in rep['surfaces'] if 'toolbar-group' not in x['scene']]
        results.append(dict(run=run.name, files=rep['files'], surfaces=len(kept),
                            setAsideGroupSurfaces=len(rep['surfaces']) - len(kept),
                            departures=sum(len(x['departures']) for x in kept),
                            unpredicted=sum(len(x['unpredicted']) for x in kept)))
    sample = next((memo_d / 'runs/2x-light-active/json').glob('*rrect-md__rest.json'))
    r = records(sample)[0]
    mutations = {}
    for field, value in ((G + 'BlurRadius', 6), (G + 'BlurFillNormalOpacity', 0.546), (G + 'BlurOpacity0', 0.3),
                         ('bd.scale', 0.25), ('bd.marginWidth', 16), ('isKeyWindow', False)):
        bad = dict(r)
        bad[field] = value
        departures, _, _ = check(bad, 'light', 'active', 2, reference)
        mutations[field] = [d['field'] for d in departures]
    return dict(runs=results, mutations=mutations,
                passes=all(x['departures'] == 0 for x in results)
                and all(field in fields for field, fields in mutations.items()))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='action', required=True)
    a = sub.add_parser('reference')
    a.add_argument('--memo-d', type=Path, required=True)
    a.add_argument('--out', type=Path, required=True)
    b = sub.add_parser('selftest')
    b.add_argument('--memo-d', type=Path, required=True)
    c = sub.add_parser('check')
    c.add_argument('directory', type=Path)
    c.add_argument('--scheme', choices=('light', 'dark'), required=True)
    c.add_argument('--pose', choices=('active', 'receded'), required=True)
    c.add_argument('--scale', type=int, choices=(1, 2), required=True)
    c.add_argument('--expect', help='comma-separated scene ids the directory must hold exactly')
    c.add_argument('--out', type=Path)
    args = ap.parse_args()
    reference_path = HERE / 'dump-reference.json'
    if args.action == 'reference':
        args.out.write_text(json.dumps(build_reference(args.memo_d), indent=1, sort_keys=True) + '\n')
        return
    reference = json.loads(reference_path.read_text())
    if args.action == 'selftest':
        result = selftest(args.memo_d, reference)
        print(json.dumps(result, indent=1))
        sys.exit(0 if result['passes'] else 1)
    expected = args.expect.split(',') if args.expect else None
    report = check_dir(args.directory, args.scheme, args.pose, args.scale, reference, expected)
    report['referenceSha256'] = hashlib.sha256(reference_path.read_bytes()).hexdigest()
    text = json.dumps(report, indent=1, default=list) + '\n'
    if args.out:
        args.out.write_text(text)
    print(json.dumps({k: v for k, v in report.items() if k != 'surfaces'}, indent=1))
    sys.exit(1 if report['departures'] else 0)


if __name__ == '__main__':
    main()
