"""W50 pure pixel readings. This module never locates or opens a capture tree.

The analytical contour is W50 cuts.py's W44 signed distance at pixel centres, after the
reader checks the native suppliedPaths placement/size. It is NOT a detected L1 mask or a
claim about SwiftUI's raster coverage. center8 is independent of that contour. far24 is
W49b's distance to every nonzero no-glass impulse raster pixel, in CSS px; with no dots it
is exactly deep8 (DL5a). Non-impulse span controls also report far24 = deep8.

T1 is the driver's population SD of linear Rec.709 luma on the full NATIVE detected
silhouette, including the chroma arm and declared-region bound. A web image must pass that
native mask via silhouette_mask, never detect its own. Encoded luma means the Rec.709
weighted sum of encoded RGB codes, NOT encode(mean(linear luma)). Definitions are imported
from the proven W44 port, not re-fitted here. The execution root must seal this import.
"""
from __future__ import annotations

import base64
import hashlib
import io
from pathlib import Path
import types

import numpy as np
from PIL import Image
from scipy.ndimage import distance_transform_edt

PORT_PATH = (Path(__file__).resolve().parents[2] /
             '2026-10-03-w44-g0-declaration/port/interior.py')
P = types.ModuleType('w50_w44_interior')
P.__file__ = str(PORT_PATH)
# Compile source, never a timestamp-valid stale pyc. The prospective root owns source sealing.
exec(compile(PORT_PATH.read_bytes(), str(PORT_PATH), 'exec'), P.__dict__)

SUPPORT_DEFINITIONS = {
    'deep8': 'W44 analytical supplied contour: signed distance <= -8*scale at pixel centres.',
    'center8': 'Independent central 8x8 CSS-px square, pixel centres strictly within +/-4 CSS px.',
    'deep8_far24': 'deep8 AND >=24 CSS px from every nonzero impulse raster pixel; no dots = deep8.',
    'full-silhouette': 'Full native luminance/chroma-delta silhouette, bounded to the declared region.',
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_rgb(rgb):
    array = np.asarray(rgb)
    if array.ndim != 3 or array.shape[2] != 3 or not np.issubdtype(array.dtype, np.integer) \
            or np.any(array < 0) or np.any(array > 255):
        raise ValueError('Image must be finite 8-bit RGB codes, with three channels')
    return array.astype(np.uint8, copy=False)


def decode_png(raw):
    """Decode exactly as the established PNG port: stored RGB codes, no ICC/gamma transform."""
    with Image.open(io.BytesIO(raw)) as image:
        if image.format != 'PNG':
            raise ValueError('Role frame is not a PNG')
        return checked_rgb(np.asarray(image.convert('RGB')))


def analytical_masks(component, canvas, scale, image_shape, *, background=None, impulse=False):
    if scale not in (1, 2) or isinstance(scale, bool):
        raise ValueError('W50 scale must be 1 or 2')
    distance = P.signed_distance(component, canvas, scale, image_shape)
    yy, xx = np.indices(image_shape, dtype=float)
    center = ((np.abs((xx+.5)/scale-canvas['width']/2) < 4) &
              (np.abs((yy+.5)/scale-canvas['height']/2) < 4))
    deep = distance <= -8*scale
    far = deep.copy()
    if impulse:
        if background is None:
            raise ValueError('far24 requires the recorded no-glass dependency')
        bg = checked_rgb(background)
        if bg.shape[:2] != tuple(image_shape):
            raise ValueError('No-glass dimensions differ from the declared capture')
        dots = np.any(bg != 0, axis=2)
        # scipy's EDT on an all-True array measures to an implicit outside zero, NOT infinity.
        # The explicit empty-set branch implements DL5a rather than inheriting that artefact.
        if dots.any():
            far &= distance_transform_edt(~dots)/scale >= 24
        if np.any(bg[far] != 0):
            raise ValueError('far24 selected a nonblack no-glass pixel')
    return {'deep8': deep, 'center8': center, 'deep8_far24': far}


def native_supports(native_rgb, background, component, canvas, scale):
    native, bg = checked_rgb(native_rgb), checked_rgb(background)
    if native.shape != bg.shape:
        raise ValueError('Native and no-glass image dimensions differ')
    return P.native_interior(native, bg, component, canvas, scale)


def read_support(rgb, mask, *, retain_mask=False):
    rgb = checked_rgb(rgb)
    mask = np.asarray(mask)
    if mask.dtype != np.bool_ or mask.shape != rgb.shape[:2]:
        raise ValueError('Support must be a matching boolean mask')
    packed = np.packbits(mask).tobytes()
    result = {'status': 'MEASURED' if mask.any() else 'UNMEASURED_EMPTY_SUPPORT',
              'pixels': int(mask.sum()), 'maskShape': list(mask.shape),
              'maskPackedBitsSha256': sha(packed)}
    if retain_mask:
        result['maskPackedBitsBase64'] = base64.b64encode(packed).decode('ascii')
    if not mask.any():
        return result
    values = rgb[mask].astype(np.float64)
    encoded = values @ np.asarray(P.LUMA)
    linear = P.luminance(rgb)[mask]
    # The T1 driver's one-pass population identity, not sample SD or encoded-code SD.
    mean = float(np.sum(linear)/len(linear))
    sd = float(np.sqrt(max(0., float(np.sum(linear*linear)/len(linear))-mean*mean)))
    result.update(rgbMeanCodes=values.mean(axis=0).tolist(),
                  rgbMedianCodes=np.median(values, axis=0).tolist(),
                  encodedLumaMeanCodes=float(encoded.mean()),
                  encodedLumaMedianCodes=float(np.median(encoded)),
                  linearLumaMean=mean, linearLumaStdDev=sd)
    return result


def decode_support(record):
    """Recover a saved native silhouette for web T1; verify support bytes/count before reuse."""
    shape = record['maskShape']
    if len(shape) != 2 or any(type(v) is not int or v <= 0 for v in shape):
        raise ValueError('Invalid native support shape')
    raw = base64.b64decode(record['maskPackedBitsBase64'], validate=True)
    count = int(np.prod(shape))
    if len(raw) != (count+7)//8 or sha(raw) != record['maskPackedBitsSha256']:
        raise ValueError('Native support hash/size mismatch')
    bits = np.unpackbits(np.frombuffer(raw, dtype=np.uint8))
    if bits[count:].any():
        raise ValueError('Native support has nonzero padding')
    mask = bits[:count].reshape(shape).astype(bool)
    if int(mask.sum()) != record['pixels']:
        raise ValueError('Native support population mismatch')
    return mask


def read_frame(rgb, background, component, canvas, scale, *, impulse=False,
               include_structured=False, silhouette_mask=None):
    """Pure per-frame readings, with exact reference statistic names and independent supports.

    Required empty analytical populations refuse the read. An empty detected silhouette remains
    honestly UNMEASURED; it never becomes an analytical mask to manufacture a T1 value.
    """
    rgb, bg = checked_rgb(rgb), checked_rgb(background)
    if rgb.shape != bg.shape:
        raise ValueError('Frame and no-glass dependency dimensions differ')
    masks = analytical_masks(component, canvas, scale, rgb.shape[:2],
                             background=bg, impulse=impulse)
    names = ('deep8', 'center8', 'deep8_far24') if include_structured else ('deep8', 'center8')
    supports = {name: read_support(rgb, masks[name]) for name in names}
    if any(not supports[name]['pixels'] for name in names):
        raise ValueError('Required analytical cut is empty; cannot certify readiness')
    statistics = {}
    for name, support in (('deep8-channel-median', 'deep8'),
                          ('central8-channel-median', 'center8')):
        statistics[name] = {'status': 'MEASURED', 'support': support, 'units': 'encoded-RGB-codes',
                            'value': supports[support]['rgbMedianCodes']}
    if include_structured:
        for name, field in (('mean', 'encodedLumaMeanCodes'), ('median', 'encodedLumaMedianCodes')):
            statistics['deep8-far24-luma-'+name] = {
                'status': 'MEASURED', 'support': 'deep8_far24', 'units': 'encoded-luma-codes',
                'value': supports['deep8_far24'][field]}
        mask = (native_supports(rgb, bg, component, canvas, scale)
                if silhouette_mask is None else silhouette_mask)
        supports['full-silhouette'] = read_support(rgb, mask, retain_mask=True)
        t1 = supports['full-silhouette']
        statistics['T1-full-silhouette'] = {
            'status': t1['status'], 'support': 'full-silhouette', 'units': 'linear-luma',
            'value': t1.get('linearLumaStdDev')}
    return {'supports': supports, 'statistics': statistics}


def repeat_codes(values):
    """W50 encoded level bar: half separation floored at .5, with a hard spread stop at 1."""
    array = np.asarray(values, dtype=float)
    if array.ndim not in (1, 2) or array.shape[0] != 3 or \
            (array.ndim == 2 and array.shape[1] != 3) or not np.isfinite(array).all():
        raise ValueError('Exactly three complete finite scalar/RGB repetitions are required')
    spread = np.ptp(array, axis=0)
    return {'spreadCodes': spread.tolist(), 'barCodes': np.maximum(.5, spread/2).tolist(),
            'passes': bool(np.all(spread <= 1))}


def repeat_t1(values, means):
    """NEW W50 T1 bar: max(half-code step, half-separation), in linear-luma units.

    W50 has no plurality fixture. The code-step anchor is the median of its three native
    interior means, explicitly recorded. This converts linear SD separation to encoded-code
    equivalents; it never changes T1 into an encoded-luma SD or creates a landing budget B.
    Historical W44 bars used an additive floor and remain untouched; this reads W50's rule.
    """
    values, means = np.asarray(values, dtype=float), np.asarray(means, dtype=float)
    if values.shape != (3,) or means.shape != (3,) or not np.isfinite(values).all() \
            or not np.isfinite(means).all() or np.any(values < 0) \
            or np.any(means < 0) or np.any(means > 1):
        raise ValueError('Exactly three finite T1 values and native means are required')
    anchor = float(np.median(means))
    step = P.code_step(anchor)
    spread = float(np.ptp(values))
    return {'spreadLinear': spread, 'codeStepLinear': step, 'anchorNativeMean': anchor,
            'anchorPolicy': 'median-of-three-native-interior-means',
            'spreadCodes': spread/step, 'barLinear': max(.5*step, .5*spread),
            'barCodes': max(.5, .5*spread/step), 'passes': bool(spread/step <= 1),
            'barPolicy': 'W50-max-half-code-step-half-native-separation'}
