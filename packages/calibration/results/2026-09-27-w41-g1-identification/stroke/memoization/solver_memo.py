"""Two-entry solver-callback reuse; no change to the sealed fitter or its math.

The context owns no scientific data and outlives no fit. Each solver call owns
at most two caches (objective/residual and constraint); each cache holds at most
two results. Reports, width scans, Jacobians and final vectors are not cached.
This is process-local module replacement, not a thread-safe runtime service.
"""
from collections import OrderedDict
from contextlib import AbstractContextManager
import hashlib
import inspect
import json
import struct
import numpy as np


def encoded(value):
    """Lossless-bit witnesses, with arrays represented by dtype/shape/byte digest."""
    if isinstance(value, np.ndarray):
        if value.dtype.hasobject:
            raise TypeError('object arrays have no stable byte witness')
        return {'array': value.dtype.str, 'shape': list(value.shape),
                'sha256': hashlib.sha256(value.tobytes(order='C')).hexdigest()}
    if isinstance(value, np.generic):
        return {'scalar': encoded(np.asarray(value))}
    if isinstance(value, float):
        return {'float64': struct.pack('!d', value).hex()}
    if value is None or isinstance(value, (str, int, bool)):
        return value
    if isinstance(value, dict):
        return {k: encoded(v) for k, v in sorted(value.items())}
    if isinstance(value, (list, tuple)):
        return {type(value).__name__: [encoded(v) for v in value]}
    if callable(value):
        return {'callback': getattr(value, '__memo_label__', value.__qualname__)}
    raise TypeError(f'no exact witness for {type(value).__name__}')


def fingerprint(value):
    return hashlib.sha256(json.dumps(encoded(value), sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


class Trace:
    """Rolling ordered transcript of every solver/callback input and output.

    Optional JSONL records contain byte witnesses, not huge residual arrays.
    Timing and cache hit/miss status are intentionally not in this scientific
    transcript; they belong in the separate performance receipt.
    """
    def __init__(self, stream=None):
        self.stream = stream
        self.digest = hashlib.sha256()
        self.events = 0
        self.counts = {}

    def emit(self, event, **data):
        row = dict(event=event, **encoded(data))
        raw = (json.dumps(row, sort_keys=True, separators=(',', ':'))+'\n').encode()
        self.digest.update(raw)
        self.events += 1
        self.counts[event] = self.counts.get(event, 0)+1
        if self.stream is not None:
            self.stream.write(raw.decode())

    def summary(self):
        return dict(sha256=self.digest.hexdigest(), events=self.events, counts=self.counts.copy())


class EffectiveKey:
    """Key only what predict reads, using the sealed unpack operation itself.

    Endpoints not present in this fit have no forward effect. Inactive eta is
    ignored by unpack; active gamma and sorted ordinates are keyed after unpack.
    We deliberately do NOT identify further clipping/coverage equivalences.
    Fixed-width callbacks supply their actual captured full(v), not a guessed
    width. Epigraph constraints additionally read t, which is kept bit-for-bit.
    """
    def __init__(self, fitter, observations, family, curvature=False, *, full=None,
                 epigraph=False):
        self.fitter = fitter
        self.family = family
        self.curvature = curvature
        self.endpoints = tuple(sorted({o['endpoint'] for o in observations}))
        self.full = full
        self.epigraph = epigraph
        self.dimension = len(fitter.domain(family, curvature)[2])
        if not self.endpoints or any(e not in range(4) for e in self.endpoints):
            raise ValueError('nonempty admitted endpoint membership required')

    def __call__(self, vector):
        v = np.asarray(vector)
        q = v[:-1] if self.epigraph else v
        if self.full is not None:
            q = self.full(q)
        if q.shape != (self.dimension,) or q.dtype != np.dtype('float64'):
            raise ValueError('sealed float64 full-coordinate vector required')
        pieces = [q[:1].tobytes()]
        if self.curvature:
            pieces.append(q[-1:].tobytes())
        for endpoint in self.endpoints:
            _, beta, gamma, material = self.fitter.unpack(q, self.family, endpoint)
            pieces.extend((struct.pack('!dd', beta, gamma), material.tobytes()))
        if self.epigraph:
            pieces.append(v[-1:].tobytes())
        return b''.join(pieces)


class CallbackCache:
    """Cache pure callback results, returning owned arrays even on the cold call."""
    def __init__(self, callback, key):
        self.callback, self.key = callback, key
        self.entries = OrderedDict()
        self.stats = dict(hits=0, misses=0, maxEntries=0, peakPayloadBytes=0)

    def __call__(self, vector, *args, **kwargs):
        key = self.key(vector)
        if args or kwargs:
            key += fingerprint((args, kwargs)).encode()
        if key in self.entries:
            self.stats['hits'] += 1
            self.entries.move_to_end(key)
            value = self.entries[key]
        else:
            self.stats['misses'] += 1
            value = self.callback(vector, *args, **kwargs)
            value = value.copy() if isinstance(value, np.ndarray) else value
            # Evict BEFORE insertion, so three output buffers are never retained.
            if len(self.entries) == 2:
                self.entries.popitem(last=False)
            self.entries[key] = value
            self.stats['maxEntries'] = max(self.stats['maxEntries'], len(self.entries))
            size = sum(len(k)+(v.nbytes if isinstance(v, np.ndarray) else np.asarray(v).nbytes)
                       for k, v in self.entries.items())
            self.stats['peakPayloadBytes'] = max(self.stats['peakPayloadBytes'], size)
        return value.copy() if isinstance(value, np.ndarray) else value


class SolverMemo(AbstractContextManager):
    """Wrap only least_squares/minimize calls; pass all solver arguments by value.

    enabled=False installs identical trace plumbing but executes every callback.
    Wrappers and caches are discarded at solver return. The caller must keep the
    observations/family/curvature identical to the fit this context encloses.
    """
    def __init__(self, fitter, observations, family, curvature=False, *, enabled=True,
                 trace=None):
        self.fitter, self.observations = fitter, observations
        self.family, self.curvature = family, curvature
        self.enabled, self.trace = enabled, trace
        self.solvers = []
        self.original = None
        self.dimension = len(fitter.domain(family, curvature)[2])

    def __enter__(self):
        if self.original is not None or any(getattr(getattr(self.fitter, n), '__memo_solver__', False)
                                           for n in ('least_squares', 'minimize')):
            raise RuntimeError('nested solver memoization is not supported')
        self.original = {n: getattr(self.fitter, n) for n in ('least_squares', 'minimize')}
        for kind, solver in self.original.items():
            setattr(self.fitter, kind, self._boundary(kind, solver))
        return self

    def __exit__(self, *exception):
        for kind, solver in self.original.items():
            setattr(self.fitter, kind, solver)
        self.original = None
        return False

    def _emit(self, event, **data):
        if self.trace is not None:
            self.trace.emit(event, **data)

    def _boundary(self, kind, solver):
        signature = inspect.signature(solver)

        def boundary(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            values = bound.arguments
            constraints = values.get('constraints', ())
            # These are precisely the callback forms in the held fitter. Refuse
            # an unfamiliar solver boundary rather than guess its dependencies.
            if not isinstance(constraints, (list, tuple)) or any(
                    not isinstance(c, dict) or set(c) != {'type', 'fun'} for c in constraints):
                raise ValueError('unrecognized sealed constraint interface')
            callbacks = [values['fun'], *(c['fun'] for c in constraints)]
            fulls = [inspect.getclosurevars(cb).nonlocals.get('full') for cb in callbacks]
            fulls = [full for full in fulls if full is not None]
            full = fulls[0] if fulls else None
            if any(candidate is not full for candidate in fulls):
                raise ValueError('callbacks disagree on fixed-width reconstruction')
            size = len(values['x0'])
            base = self.dimension-int(full is not None)
            epigraph = kind == 'minimize' and size == base+1
            if size != base+int(epigraph):
                raise ValueError('unrecognized sealed solver dimension')
            number = len(self.solvers)
            record = dict(kind=kind, fixedWidth=full is not None, epigraph=epigraph, caches=[])
            self.solvers.append(record)
            caches = []

            def wrap(callback, label, cacheable):
                cache = None
                if self.enabled and cacheable:
                    key = EffectiveKey(self.fitter, self.observations, self.family,
                                       self.curvature, full=full, epigraph=epigraph)
                    cache = CallbackCache(callback, key)
                    caches.append(cache)
                    record['caches'].append(cache.stats)

                def call(vector, *cb_args, **cb_kwargs):
                    self._emit('callback-input', solver=number, callback=label,
                               vector=vector, args=cb_args, kwargs=cb_kwargs)
                    output = (cache or callback)(vector, *cb_args, **cb_kwargs)
                    self._emit('callback-output', solver=number, callback=label, value=output)
                    return output
                call.__memo_label__ = label
                return call

            values['fun'] = wrap(values['fun'], 'fun', not epigraph)
            if 'constraints' in values:
                replaced = [dict(c, fun=wrap(c['fun'], f'constraint-{i}', True))
                            for i, c in enumerate(constraints)]
                values['constraints'] = tuple(replaced) if isinstance(constraints, tuple) else replaced
            self._emit('solver-input', solver=number, kind=kind, arguments=dict(values))
            try:
                result = solver(*bound.args, **bound.kwargs)
                self._emit('solver-output', solver=number, kind=kind, result=result)
                return result
            finally:
                for cache in caches:
                    cache.entries.clear()

        boundary.__memo_solver__ = True
        return boundary

    def summary(self):
        stats = [cache for solver in self.solvers for cache in solver['caches']]
        return dict(enabled=self.enabled, hits=sum(c['hits'] for c in stats),
                    misses=sum(c['misses'] for c in stats),
                    maxEntriesPerCallback=max((c['maxEntries'] for c in stats), default=0),
                    maxActiveCaches=max((len(s['caches']) for s in self.solvers), default=0),
                    cachePayloadUpperBoundBytes=max((sum(c['peakPayloadBytes'] for c in s['caches'])
                        for s in self.solvers), default=0),
                    memoryQualification='key and result payloads; excludes Python object overhead, '
                        'uncached evaluation temporaries and the returned array copy',
                    solvers=self.solvers)
