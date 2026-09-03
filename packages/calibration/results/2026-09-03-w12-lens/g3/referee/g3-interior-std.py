"""Did the interior actually sharpen at 2x, and stay put at 1x? — the implementation check.

`interiorStdDev{Native,Web}` is the compare's own reading of how much backdrop structure
survives inside the silhouette. If the declared law reached the pixels, the 2x web reading
must rise toward the native one and the 1x reading must not move at all.
"""
import json

T = '/Users/new/.claude/jobs/5c70e47f/tmp/w12'


def latest(path, renderer=None):
    out = {}
    for c in json.load(open(path))['cells']:
        k = (c['key']['profileKey'], c['key']['web']['renderer'], c['key']['sceneId'])
        if renderer and k[1] != renderer:
            continue
        if k not in out or c['capturedAt'] > out[k]['capturedAt']:
            out[k] = c
    return out


g2 = latest(f'{T}/matrix-g2.json')
g2b = latest(f'{T}/matrix-g2b.json')
new = latest(f'{T}/matrix-g3.json')
main = {k: v for k, v in g2.items() if k[1] == 'css'}
main.update({k: v for k, v in g2b.items() if k[1] == 'webgpu'})
for k, v in g2.items():
    main.setdefault(k, v)


def r(c, ax, k):
    v = c.get(ax, {}).get(k)
    return v['value'] if isinstance(v, dict) else None


print(f'{"scale":6s} {"tier":7s} {"component":17s} {"native":>8s} {"main":>8s} {"G3":>8s} {"Δ":>8s}')
for scale in ('1x', '2x'):
    for tier in ('webgpu', 'css'):
        for comp in ('rrect-sm', 'capsule-button', 'rrect-md', 'rrect-ml', 'rrect-lg'):
            k = (f'apple-macos-26.5-{scale}-light-standard', tier, f'checkerboard__{comp}__rest')
            if k not in new or k not in main:
                continue
            nat = r(new[k], 'material', 'interiorStdDevNative')
            a = r(main[k], 'material', 'interiorStdDevWeb')
            b = r(new[k], 'material', 'interiorStdDevWeb')
            if nat is None or a is None or b is None:
                continue
            print(f'{scale:6s} {tier:7s} {comp:17s} {nat:8.4f} {a:8.4f} {b:8.4f} {b - a:+8.4f}')
