"""G3: merge the parts into `g3-measurement.json` and print the markdown tables of the findings."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from g3lib import OUT, COMPS, SPAN, PITCHES5, LC16, SCALES  # noqa: F401

PARTS = ['interior', 'depth', 'kernel', 'level', 'lens2x', 'forms', 'photo',
         'variants', 'dryrun', 'dryrun2', 'transmission']
doc = {p: json.load(open(f'{OUT}/parts/{p}.json')) for p in PARTS}
with open(f'{OUT}/g3-measurement.json', 'w') as f:
    json.dump(doc, f, indent=1, sort_keys=True)
print(f'[wrote] {OUT}/g3-measurement.json')

SHORT = {'rrect-sm': 'sm 32', 'capsule-button': 'cap 44', 'rrect-md': 'md 96', 'rrect-ml': 'ml 128',
         'rrect-lg': 'lg 160'}
PN = {'checkerboard-4': 'p4', 'checkerboard-8': 'p8', 'checkerboard': 'p16',
      'checkerboard-32': 'p32', 'checkerboard-64': 'p64', LC16: 'lc16'}


def cell(b, comp, scale):
    return doc['interior']['cells'][f'{b}|{comp}|{scale}x']


print('\n### Table 1a — single Gaussian, σ in CSS px (device px in brackets), t, RMS\n')
print('| cell | ' + ' | '.join(f'{PN[b]} 1x | {PN[b]} 2x' for b in PITCHES5 + [LC16]) + ' |')
print('| --- ' * (1 + 2 * 6) + '|')
for comp in COMPS:
    row = [SHORT[comp]]
    for b in PITCHES5 + [LC16]:
        for s in SCALES:
            c = cell(b, comp, s)['single']
            f = cell(b, comp, s)['flags']
            mark = '*' if f else ''
            row.append(f'{c["sigma"]:.2f} ({c["sigma"] * s:.1f}) t {c["t"]:+.3f}{mark}')
    print('| ' + ' | '.join(row) + ' |')

print('\n### Table 1b — two components, σ_sharp / σ_heavy (CSS px) and the heavy share\n')
print('| cell | ' + ' | '.join(f'{PN[b]} 1x | {PN[b]} 2x' for b in PITCHES5 + [LC16]) + ' |')
print('| --- ' * (1 + 2 * 6) + '|')
for comp in COMPS:
    row = [SHORT[comp]]
    for b in PITCHES5 + [LC16]:
        for s in SCALES:
            t = cell(b, comp, s)['two']
            row.append('—' if t['share'] != t['share'] else
                       f'{t["sigma_sharp"]:.2f}/{t["sigma_heavy"]:.1f} k {t["share"]:.2f}')
    print('| ' + ' | '.join(row) + ' |')

print('\n### Table 4 — interior mean and retained contrast, 1x → 2x\n')
print('| cell | mean 1x | mean 2x | Δ | retained 1x | retained 2x | t 1x | t 2x |')
print('| --- | --- | --- | --- | --- | --- | --- | --- |')
for scene, c in doc['level']['cells'].items():
    if abs(c['mean_delta_2x_minus_1x']) < 0.002:
        continue
    print(f'| {scene} | {c["1x"]["interior_mean"]:.4f} | {c["2x"]["interior_mean"]:.4f} | '
          f'{c["mean_delta_2x_minus_1x"]:+.4f} | {c["1x"].get("retained", float("nan")):.3f} | '
          f'{c["2x"].get("retained", float("nan")):.3f} | {c["1x"].get("t", float("nan")):+.3f} | '
          f'{c["2x"].get("t", float("nan")):+.3f} |')

print('\n### Table 6 — the candidate forms\n')
print('| form | fit RMS | holdout RMS | 1x fit | 1x holdout | 2x fit | 2x holdout |')
print('| --- | --- | --- | --- | --- | --- | --- |')
for k, v in doc['forms']['forms'].items():
    ps = v['per_scale']
    print(f'| {k} | {v["rms_fit"]:.4f} | {v["rms_holdout"]:.4f} | {ps["1x"]["fit"]:.4f} | '
          f'{ps["1x"]["holdout"]:.4f} | {ps["2x"]["fit"]:.4f} | {ps["2x"]["holdout"]:.4f} |')

print('\n### Table 6b — per-pitch contrast ratio (model std ÷ reference std) at 2x, winner vs landed\n')
for name in ('F0-gpu-css-px', 'F1-gpu-sharp-css_k-scale-term', 'F2-quarter-buffer-scale-term'):
    v = doc['forms']['forms'][name]
    print(f'\n**{name}**\n')
    print('| cell | p8 | p16 | p32 | p64 |')
    print('| --- | --- | --- | --- | --- |')
    for key in list(v['fit_cells']) + list(v['holdout_cells']):
        c = (v['fit_cells'].get(key) or v['holdout_cells'][key])
        if not key.endswith('2x'):
            continue
        print(f'| {key} | ' + ' | '.join(
            f'{c["per_pitch"][b]["contrast_ratio"]:.2f}'
            for b in ['checkerboard-8', 'checkerboard', 'checkerboard-32', 'checkerboard-64']) + ' |')

print('\n### Table 2 — depth: the single-Gaussian σ and t per 8 px band, from u = 20 inward\n')
for pitch in ['checkerboard', 'checkerboard-32']:
    print(f'\n**{PN[pitch]}**\n')
    print('| cell | ' + ' | '.join(f'u {int(r["u0"])}–{int(r["u1"])}'
                                   for r in doc['depth']['cells']['rrect-lg@1x']['bands'][pitch]) + ' |')
    print('| --- ' * (1 + len(doc['depth']['cells']['rrect-lg@1x']['bands'][pitch])) + '|')
    for key, c in doc['depth']['cells'].items():
        rows = c['bands'].get(pitch, [])
        if not rows:
            continue
        print(f'| {key} | ' + ' | '.join(f'σ {r["single_sigma"]:.2f} t {r["single_t"]:+.3f}'
                                         for r in rows) + ' |')

print('\n### Table 3 — the impulse kernel from the deep interior over all five pitches\n')
print('| cell | Gaussian core | box core | quarter-buffer core | base σ (CSS/device) | base share |')
print('| --- | --- | --- | --- | --- | --- |')
for key, c in doc['kernel']['cells'].items():
    g, b, q = c['candidates']['gauss'], c['candidates']['box'], c['candidates']['quarter']
    w = c['winner']
    print(f'| {key} | σ {g["core_param"]:.2f} rms {g["rms"]:.4f} | w {b["core_param"]:.2f} '
          f'rms {b["rms"]:.4f} | rms {q["rms"]:.4f} | {w["base_sigma"]:.0f} / {w["base_sigma_dev"]:.0f} '
          f'| {w["share"]:.3f} |')

print('\n### Table 5 — the lens crossings against the landed G2 law\n')
print('| cell | pitch | edge | u (CSS px) | D measured | D from the G2 law | Δ |')
print('| --- | --- | --- | --- | --- | --- | --- |')
for key, c in doc['lens2x']['cells'].items():
    for r in sorted(c['crossings'], key=lambda r: r['u']):
        print(f'| {key} | {c["pitch"]} | {r["edge"]} | {r["u"]:.2f} | {r["D"]:.2f} | '
              f'{r["D_g2_law"]:.2f} | {r["D"] - r["D_g2_law"]:+.2f} |')


print('\n### Table 8a — F1\' variants (2x fitted alone; 1x is the landed law by construction)\n')
print('| variant | dk | 2x fit | 2x holdout | 1x fit | 1x holdout | photo 2x |')
print('| --- | --- | --- | --- | --- | --- | --- |')
for k, v in doc['variants']['variants'].items():
    print(f'| {k} | {v["params"]["dk"]:.2f} | {v["rms_2x_fit"]:.4f} | {v["rms_2x_holdout"]:.4f} | '
          f'{v["rms_1x_fit"]:.4f} | {v["rms_1x_holdout"]:.4f} | '
          f'{doc["variants"]["photo_2x"][k]["overall"]:.4f} |')

print('\n### Table 8b — the SSIM dry run, before → after (Δ against the landed law F0)\n')
print('| row | bound | floor | before | F0 | F1 | F1\' | F1−F0 | F1\'−F0 |')
print('| --- | --- | --- | --- | --- | --- | --- | --- | --- |')
for key, r in doc['dryrun']['rows'].items():
    fl = f'{r["floor"]:.4f}' if r.get('floor') else '—'
    print(f'| {key.replace(chr(124), " / ")} | {r["bound"]:.2f} | {fl} | {r["before"]:.4f} | {r["F0"]["after"]:.4f} | '
          f'{r["F1"]["after"]:.4f} | {r["F1\'"]["after"]:.4f} | '
          f'{r["F1"]["after"] - r["F0"]["after"]:+.4f} | {r["F1\'"]["after"] - r["F0"]["after"]:+.4f} |')
