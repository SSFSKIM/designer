"""Pure canonical reference readings; no capture discovery, files, coefficients or verdicts.

T1 is the driver's full native detected-silhouette population linear-luma SD. Text uses
W44 G1 cuts/readings.py's unmasked Gaussian sigma4 DEVICE px (reflect border), with fine
residual/low-pass SD on native EDT erosion >4 CSS px. Web always uses the published native
supports. Analytical path cuts remain distinct even where detected silhouette is empty.

NEW canonical repeat bars use seven OWN admitted repeats and W50's max(half-code, half
separation), with code_step at the PUBLISHED native full-silhouette mean. Historical spread
is reported, not a new noise stop. This is intentionally not compact W50's three-run stop,
nor W44's old additive bar. Already populated0.25 T1 fields are never replaced here.
"""
from __future__ import annotations

import copy
from pathlib import Path
import types

import numpy as np
from scipy.ndimage import distance_transform_edt, gaussian_filter

NATIVE = Path(__file__).resolve().parent.parent/'native/statistics.py'
S = types.ModuleType('w50_reference_native_statistics'); S.__file__ = str(NATIVE)
exec(compile(NATIVE.read_bytes(), str(NATIVE), 'exec', dont_inherit=True), S.__dict__)


def scalar_read(value, mask):
    if not mask.any():
        return {'status': 'UNMEASURED_EMPTY_SUPPORT', 'value': None}
    return {'status': 'MEASURED', 'value': float(np.asarray(value)[mask].std())}


def canonical_read(native_rgb, background, component, canvas, scale, *, web_rgb=None,
                   text=False, impulse=False):
    native, bg = S.checked_rgb(native_rgb), S.checked_rgb(background)
    if native.shape != bg.shape:
        raise ValueError('Canonical native/background dimensions differ')
    native_mask = S.native_supports(native, bg, component, canvas, scale)
    masks = S.analytical_masks(component, canvas, scale, native.shape[:2],
                               background=bg, impulse=impulse)
    masks['full-silhouette'] = native_mask
    if text:
        masks['eroded4'] = distance_transform_edt(native_mask) > 4*scale

    def side(rgb):
        rgb = S.checked_rgb(rgb)
        if rgb.shape != native.shape:
            raise ValueError('Canonical web/native dimensions differ')
        supports = {k: S.read_support(rgb, m, retain_mask=True) for k, m in masks.items()}
        statistics = {}
        full = supports['full-silhouette']
        statistics['T1-full-silhouette'] = {'status': full['status'],
            'value': full.get('linearLumaStdDev'), 'support': 'full-silhouette', 'units': 'linear-luma'}
        if text:
            linear = S.P.luminance(rgb)
            low = gaussian_filter(linear, 4., mode='reflect')
            for name, values in (('T1-low', low), ('T1-fine', linear-low)):
                statistics[name] = {**scalar_read(values, masks['eroded4']),
                                    'support': 'eroded4', 'units': 'linear-luma'}
        for support in ('deep8', 'deep8_far24'):
            for name, field, units in (('luma-mean', 'encodedLumaMeanCodes', 'encoded-luma-codes'),
                    ('luma-median', 'encodedLumaMedianCodes', 'encoded-luma-codes'),
                    ('channel-median', 'rgbMedianCodes', 'encoded-RGB-codes')):
                prefix = 'deep8-far24' if support == 'deep8_far24' else 'deep8'
                row = supports[support]
                statistics[prefix+'-'+name] = {'status': row['status'], 'value': row.get(field),
                                               'support': support, 'units': units}
        return {'supports': supports, 'statistics': statistics}

    result = side(native)
    result['publishedInteriorMean'] = result['supports']['full-silhouette'].get('linearLumaMean')
    result['web'] = None if web_rgb is None else side(web_rgb)
    return result


def repeat_bar(values, *, units, published_mean):
    """Own seven-run budget in statistic units; no historical-noise veto or assumed floor."""
    a = np.asarray(values, dtype=float)
    if a.shape not in ((7,), (7, 3)) or not np.isfinite(a).all():
        raise ValueError('Exactly seven finite scalar/RGB native repetitions are required')
    if units == 'linear-luma':
        if a.shape != (7,) or type(published_mean) not in (float, int) \
                or not np.isfinite(published_mean) or not 0 <= published_mean <= 1:
            raise ValueError('Linear T1 code_step needs the published native interior mean')
        code = S.P.code_step(published_mean)
    elif units == 'encoded-RGB-codes':
        if a.shape != (7, 3): raise ValueError('RGB repeat budget requires all three channels')
        code = np.ones(3)
    elif units == 'encoded-luma-codes':
        if a.shape != (7,): raise ValueError('Encoded-luma repeat budget is scalar')
        code = 1.
    else:
        raise ValueError('Unknown canonical statistic units')
    spread = np.ptp(a, axis=0)
    bar = np.maximum(.5*code, spread/2)
    budget = np.maximum(code, 2*bar)
    native = lambda x: np.asarray(x).tolist()
    return {'runs': 7, 'units': units, 'code': native(code), 'bar': native(bar), 'B': native(budget),
            'spread': native(spread), 'spreadCodes': native(spread/code),
            'publishedNativeInteriorMean': published_mean if units == 'linear-luma' else None,
            'barRule': 'W50 max(0.5 code_step, half own-seven-run spread)',
            'budgetRule': 'max(code_step, 2*bar)', 'spreadPolicy': 'REPORTED_NOT_A_HISTORICAL_NOISE_STOP'}


def evidence_reading(published, runs):
    if len(runs) != 7:
        raise ValueError('Exactly seven own source readings are required')
    result = {}
    for name, statistic in published['statistics'].items():
        rows = [r['statistics'][name] for r in runs]
        values = [r['value'] for r in rows]
        complete = statistic['status'] == 'MEASURED' and all(r['status'] == 'MEASURED' for r in rows)
        item = {'status': 'MEASURED' if complete else 'UNMEASURED_EMPTY_SUPPORT',
            'native': statistic['value'], 'current': None, 'repeatValues': values,
            'support': statistic['support'], 'units': statistic['units'], 'repeat': None, 'B': None}
        if published['web'] is not None:
            item['current'] = published['web']['statistics'][name]['value']
        if complete:
            bar = repeat_bar(values, units=statistic['units'],
                              published_mean=published['publishedInteriorMean'])
            item.update(repeat=bar, B=bar['B'])
        result[name] = item
    return result


def complete_t1_reference(original, evidence):
    """Fill only previously missing0.5 T1 evidence;0.25's complete row is a literal pass-through."""
    result = copy.deepcopy(original)
    if result['profile'].endswith('-glass0.25'):
        return result
    if not result['profile'].endswith('-glass0.5'):
        raise ValueError('Canonical completion supports only the two fixed macOS27 positions')
    for name in ('native', 'current', 'B', 'fidelity'):
        if result.get(name) is None and name in evidence:
            result[name] = copy.deepcopy(evidence[name])
    return result


def source_probe():
    rgb = np.full((64, 64, 3), 128, dtype=np.uint8)
    read = canonical_read(rgb, np.zeros_like(rgb), {'kind': 'rrect', 'size': [48, 48], 'radius': 0},
                           {'width': 64, 'height': 64}, 1, web_rgb=rgb, text=True)
    evidence_reading(read, [read]*7)
