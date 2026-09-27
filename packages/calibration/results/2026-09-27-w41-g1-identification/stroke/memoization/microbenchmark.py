"""Small synthetic callback benchmark: no optimizer, archive read or fit candidate."""
import json
from pathlib import Path
import platform
import time
import numpy as np
import scipy
from fixtures import HERE, f, r, observations
from solver_memo import CallbackCache, EffectiveKey, fingerprint


def run():
    family = 'M1'
    rows = observations(family, endpoints=(1,))
    # Sixty-four pixels, retaining the real 16x16 quadrature. Benchmark both the
    # sealed sample evaluator and the already-admitted compact evaluator.
    o = rows[0]
    g = {k: np.tile(v, (16, 1, 1) if v.ndim == 3 else (16, 1))
         if isinstance(v, np.ndarray) else v for k, v in o['g'].items()}
    b = np.tile(o['backdrop'], (16, 1, 1))
    o = dict(o, g=g, backdrop=b, shadow=b.copy(), binids=np.arange(64),
             target=np.tile(o['target'], (16, 1)), amplitude=0.)
    o['compact'] = r.CompactComposite(g, b, np.zeros_like(g['d']))
    low, high, q = f.domain(family)
    vectors = [q.copy()]
    for i in range(len(q)):
        moved = q.copy()
        moved[i] += 1e-8*(-1 if q[i] == high[i] else 1)
        vectors.append(moved)
    results = []
    for label, predict in (('sealed', f.predict), ('held-compact', r.compact_predict)):
        def callback(v):
            # Same residual arithmetic as the sealed fitter, not a replacement
            # reduction. The tiny synthetic observation has one pixel per bin.
            target, mass, _ = layout
            exact = (target > 5) & (target < 250)
            return (predict(v, o, family).ravel()-target)[exact]*np.sqrt(mass[exact])
        layout = f.objective_layout([o])
        timings = {False: [], True: []}
        hashes = set()
        cached_stats = []
        # Alternate order to avoid always giving the warm interpreter to cache.
        for trial in range(6):
            for enabled in ((False, True) if trial % 2 == 0 else (True, False)):
                # Clear only this synthetic fixture's existing compact caches.
                o['compact'].cache.clear(); o['compact'].kernel.cache.clear()
                cache = CallbackCache(callback, EffectiveKey(f, [o], family))
                selected = cache if enabled else callback
                t = time.perf_counter()
                outputs = [selected(v) for v in vectors]
                timings[enabled].append(time.perf_counter()-t)
                hashes.add(fingerprint(outputs))
                if enabled: cached_stats.append(cache.stats.copy())
        if len(hashes) != 1:
            raise AssertionError('synthetic callback results changed bits')
        plain, memo = [float(np.median(timings[mode])) for mode in (False, True)]
        results.append(dict(evaluator=label, callsPerTrial=len(vectors), trials=6,
            unwrappedMedianSeconds=plain, wrappedMedianSeconds=memo, speedup=plain/memo,
            bitIdentical=True, resultSha256=hashes.pop(), cache=cached_stats[0],
            allTrialCacheStatsEqual=all(c == cached_stats[0] for c in cached_stats)))
    return dict(schema='w41-callback-memo-microbenchmark-1', nativePayloadReads=0,
        optimizerRuns=0, pixels=64, quadraturePerPixel=256, family=family, endpoint=1,
        python=platform.python_version(), numpy=np.__version__, scipy=scipy.__version__,
        rows=results, qualification='Synthetic callback cost only; no end-to-end native '
            'speedup is established. Both evaluators are compared to themselves, not each other.')


if __name__ == '__main__':
    print(json.dumps(run(), indent=2, allow_nan=False))
