"""Dependency-free statistic and split rules shared by W33's reader and tests."""
import math


def fitting_role(role, include_holdout=False):
    return role in ('calibration', 'validation', 'probe') or (role == 'holdout' and include_holdout)


def residual(native, web):
    """Absolute before reduction: neither spatial nor channel cancellation is allowed."""
    if len(native) != len(web):
        raise ValueError('sample counts differ')
    if not len(native):
        return None
    signed = [0., 0., 0.]
    absolute = [0., 0., 0.]
    maximum = [0., 0., 0.]
    for n, w in zip(native, web):
        for c in range(3):
            delta = float(n[c])-float(w[c])
            signed[c] += delta
            absolute[c] += abs(delta)
            maximum[c] = max(maximum[c], abs(delta))
    count = len(native)
    return dict(pixels=count, mae=sum(absolute)/(3*count),
                maeRGB=[v/count for v in absolute], signed=[v/count for v in signed],
                maxRGB=maximum)


def round_up_2sf(value):
    if value <= 0: return 0.0
    step = 10. ** (math.floor(math.log10(value))-1)
    return math.ceil(value/step)*step
