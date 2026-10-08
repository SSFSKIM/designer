"""DL5h pure repeat comparison, with no file I/O or source authority.

A failed comparison is an instrument fault, never candidate NEITHER. The admitted I/O layer
supplies only registered native evidence. A caller of this pure core gains no admission.
"""
import copy
import math
import numpy as np


class InstrumentFault(ValueError):
    def __init__(self, message, *, differences=None):
        super().__init__(message)
        self.differences = {} if differences is None else differences

class IdentityRequired(InstrumentFault): pass


def bar_from_fixed_budget(budget, provenance):
    """Recover a bar only from THIS statistic's source-bound positive scalar B.

    W50 defines B=max(code,2bar), bar>=code/2, hence B=2bar. This is not a
    neighbouring-cell estimate and supplies no value where a reference has B null.
    """
    if type(budget) not in (int, float) or not math.isfinite(budget) or budget <= 0:
        raise IdentityRequired('No finite own source-bound scalar repeat budget')
    if not provenance:
        raise IdentityRequired('A fixed budget needs its exact reference provenance')
    return dict(bar=budget/2, B=budget, formula='B=max(code,2*bar), bar>=code/2 => bar=B/2',
                provenance=copy.deepcopy(provenance))


def compare_statistics(first, second):
    """Compare every scalar/channel separately; preserve the first reading, never average."""
    if set(first) != set(second):
        raise InstrumentFault('Repeat statistic membership differs')
    if not first:
        raise IdentityRequired('No declared numerical repeat statistics; byte identity required')
    result = {}; missing = []; outside = []
    for name in sorted(first):
        a, b = first[name], second[name]
        if any(a.get(key) != b.get(key) for key in ('units','support','repeat','provenance')):
            raise InstrumentFault('Repeat statistic source/support/budget differs: '+name)
        bar = a.get('repeat', {}).get('bar')
        if bar is None or a.get('value') is None or b.get('value') is None:
            missing.append(name)
            result[name] = dict(status='STRICT_IDENTITY_REQUIRED', first=copy.deepcopy(a.get('value')),
                second=copy.deepcopy(b.get('value')), units=a['units'], support=a['support'],
                nativeRepeat=copy.deepcopy(a.get('repeat')), provenance=copy.deepcopy(a['provenance']))
            continue
        x, y, limit = (np.asarray(v, dtype=float) for v in (a['value'], b['value'], bar))
        shape = (3,) if a['units'] == 'encoded-RGB-codes' else ()
        if a['units'] not in ('encoded-RGB-codes','encoded-luma-codes','linear-luma') \
                or x.shape != shape or y.shape != shape or limit.shape not in ((),shape) \
                or not all(np.isfinite(v).all() for v in (x,y,limit)) or np.any(limit <= 0):
            raise InstrumentFault('Invalid finite statistic/own repeat bar: '+name)
        limit = .1*limit
        difference = np.abs(x-y)
        if np.any(difference > limit): outside.append(name)
        result[name] = dict(first=copy.deepcopy(a['value']), second=copy.deepcopy(b['value']),
            difference=difference.tolist(), limit=limit.tolist(), units=a['units'], support=a['support'],
            nativeRepeat=copy.deepcopy(a['repeat']), provenance=copy.deepcopy(a['provenance']))
    if missing:
        raise IdentityRequired('Empty or unbudgeted declared statistic: '+', '.join(missing), differences=result)
    if outside:
        raise InstrumentFault('Repeat outside 0.1 native bar: '+', '.join(outside), differences=result)
    return result
