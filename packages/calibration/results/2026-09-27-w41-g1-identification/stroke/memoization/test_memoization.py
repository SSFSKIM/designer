"""Cache misses, coordinate omissions and callback mutation must not change a solve."""
import unittest
import numpy as np
from fixtures import f, observations, start_partition
from solver_memo import EffectiveKey, CallbackCache, SolverMemo, Trace, fingerprint


class KeyTests(unittest.TestCase):
    def test_effective_coordinates_match_real_forward_for_every_family_and_rival(self):
        for family in ('M0', 'M1', 'M2'):
            for css, curvature in ((False, False), (True, False), (False, True)):
                low, high, q = f.domain(family, curvature)
                for endpoint in range(4):
                    obs = observations(family, curvature, (endpoint,), scale=2, css=css)
                    key = EffectiveKey(f, obs, family, curvature)
                    cached = CallbackCache(
                        lambda v: f.predict(v, obs[0], family, css, curvature), key)
                    # Every dummy perturbation must reuse; every effective input
                    # perturbation must miss, even if clipping happens to hide it.
                    for i in range(len(q)):
                        moved = q.copy()
                        moved[i] += (high[i]-low[i])*1e-4*(-1 if q[i] == high[i] else 1)
                        effective = i == 0 or (curvature and i == len(q)-1)
                        old = f.unpack(q, family, endpoint)
                        new = f.unpack(moved, family, endpoint)
                        effective |= any(fingerprint(a) != fingerprint(b)
                                         for a, b in zip(old, new))
                        self.assertEqual(key(q) == key(moved), not effective,
                                         (family, css, curvature, endpoint, i))
                        self.assertEqual(fingerprint(cached(q)),
                                         fingerprint(f.predict(q, obs[0], family, css, curvature)))
                        self.assertEqual(fingerprint(cached(moved)),
                            fingerprint(f.predict(moved, obs[0], family, css, curvature)))
                        if not effective:
                            self.assertEqual(fingerprint(f.predict(q, obs[0], family, css, curvature)),
                                fingerprint(f.predict(moved, obs[0], family, css, curvature)))
                    for bound in (low, high):
                        self.assertEqual(key(bound), key(bound.copy()))
                        f.predict(bound, obs[0], family, css, curvature)

    def test_sorted_knots_gamma_and_clipping_are_not_raw_coordinate_keys(self):
        for family in ('M1', 'M2'):
            obs = observations(family, endpoints=(2,))
            key = EffectiveKey(f, obs, family, False)
            _, _, q = f.domain(family)
            q[3] = 1
            moved = q.copy(); moved[6] = .75
            moved[23:31] = moved[23:31][::-1]
            self.assertEqual(key(q), key(moved))
            self.assertEqual(fingerprint(f.predict(q, obs[0], family)),
                             fingerprint(f.predict(moved, obs[0], family)))
        obs = observations(endpoints=(1,))
        key = EffectiveKey(f, obs, 'M0', False)
        _, _, q = f.domain('M0')
        q[9:11] = [3, 255]  # All channels clip; still do not drop these inputs.
        moved = q.copy(); moved[9] = 2.9
        self.assertNotEqual(key(q), key(moved))
        self.assertEqual(fingerprint(f.predict(q, obs[0], 'M0')),
                         fingerprint(f.predict(moved, obs[0], 'M0')))

    def test_original_fixed_width_closure_and_epigraph_t_are_in_key(self):
        obs = observations('M2', True, (1, 3))
        _, _, q = f.domain('M2', True)
        held = q.copy(); held[0] = .375
        def full(v): return np.r_[held[0], v]
        normal = EffectiveKey(f, obs, 'M2', True)
        fixed = EffectiveKey(f, obs, 'M2', True, full=full)
        epi = EffectiveKey(f, obs, 'M2', True, full=full, epigraph=True)
        self.assertEqual(normal(held), fixed(held[1:]))
        self.assertNotEqual(epi(np.r_[held[1:], 1.]), epi(np.r_[held[1:], 2.]))
        held[0] = .625
        self.assertEqual(normal(held), fixed(held[1:]))


class CacheTests(unittest.TestCase):
    def test_two_entry_lru_copies_both_misses_and_hits(self):
        calls = []
        def callback(q, scale=1):
            calls.append(q.copy())
            return np.array([q[0]*scale, -0.])
        cache = CallbackCache(callback, lambda q: q.tobytes())
        a, b, c = [np.array([v]) for v in (1., 2., 3.)]
        first = cache(a, scale=2); first[:] = 999
        self.assertEqual(fingerprint(cache(a, scale=2)), fingerprint(np.array([2., -0.])))
        cache(b); cache(a, scale=2); cache(c); cache(b)
        self.assertEqual(len(calls), 4)
        self.assertEqual(cache.stats['hits'], 2)
        self.assertEqual(cache.stats['misses'], 4)
        self.assertEqual(cache.stats['maxEntries'], 2)
        self.assertGreater(cache.stats['peakPayloadBytes'], 0)
        # Callback arguments form part of the identity, not merely q.
        self.assertEqual(cache(a, scale=3)[0], 3.)

    def test_context_restores_after_exception_and_rejects_nested_use(self):
        original = f.least_squares, f.minimize
        with self.assertRaisesRegex(RuntimeError, 'test'):
            with SolverMemo(f, observations(), 'M0'):
                with self.assertRaises(RuntimeError):
                    with SolverMemo(f, observations(), 'M0'): pass
                raise RuntimeError('test')
        self.assertEqual((f.least_squares, f.minimize), original)


class TraceTests(unittest.TestCase):
    def test_fixed_width_ls_and_hard_rail_objective_keep_original_full_closure(self):
        obs = observations(endpoints=(1,), rails=True)
        target, mass, _ = f.objective_layout(obs)
        exact = (target > 5) & (target < 250)
        low, high, q = f.domain('M0')
        q[0] = .4375
        # Identity material leaves the planted synthetic target unchanged at
        # this non-default held width. Real SciPy can finish without a long fit.
        def full(v): return np.r_[q[0], v]
        def forward(v): return np.concatenate([f.predict(full(v), o, 'M0') for o in obs]).ravel()
        def residual(v): return (forward(v)-target)[exact]*np.sqrt(mass[exact])
        def objective(v):
            full(v)  # Same closure dependency as the sealed fixed-width callback.
            return np.sum(residual(v)**2)
        def rails(v):
            pred = np.concatenate([f.predict(full(v), o, 'M0') for o in obs]).ravel()
            return np.r_[5-pred[target <= 5], pred[target >= 250]-250]
        # The sealed LS lambda captures full directly, rather than through a
        # nested helper. This matters to fixed-width boundary identification.
        def ls_callback(v):
            pred = np.concatenate([f.predict(full(v), o, 'M0') for o in obs]).ravel()
            return (pred-target)[exact]*np.sqrt(mass[exact])
        summaries, results = [], []
        for enabled in (False, True):
            trace = Trace()
            with SolverMemo(f, obs, 'M0', enabled=enabled, trace=trace) as memo:
                ls = f.least_squares(ls_callback, q[1:], bounds=(low[1:], high[1:]),
                    max_nfev=3000, ftol=1e-10, xtol=1e-10, gtol=1e-10)
                rail = f.minimize(objective, ls.x, method='SLSQP',
                    bounds=list(zip(low[1:], high[1:])),
                    constraints=[dict(type='ineq', fun=rails)],
                    options=dict(maxiter=3000, ftol=1e-10))
            summaries.append(trace.summary()); results.append(fingerprint((ls, rail)))
            self.assertTrue(all(s['fixedWidth'] and not s['epigraph']
                                for s in memo.summary()['solvers']))
        self.assertEqual(summaries[0], summaries[1])
        self.assertEqual(results[0], results[1])

    def test_trace_detects_bits_order_budget_and_optimizer_status(self):
        def digest(events):
            trace = Trace()
            for event, value in events: trace.emit(event, value=value)
            return trace.summary()['sha256']
        source = [('input', np.array([0.])), ('budget', {'maxiter': 3000}),
                  ('output', {'success': False})]
        for changed in ([('input', np.array([-0.])), *source[1:]],
                        [source[0], ('budget', {'maxiter': 2999}), source[2]],
                        [*source[:2], ('output', {'success': True})],
                        list(reversed(source))):
            self.assertNotEqual(digest(source), digest(changed))

    def test_real_scipy_start_retains_all_solver_calls_budgets_and_raw_outcomes(self):
        obs = observations(endpoints=(1,), rails=True)
        fit, provenance = start_partition.partition(f.fit_local, [0])
        original = fingerprint(provenance)
        untouched = fit(obs, 'M0')
        results, traces, stats = [], [], []
        for enabled in (False, True):
            trace = Trace()
            with SolverMemo(f, obs, 'M0', enabled=enabled, trace=trace) as memo:
                results.append(fit(obs, 'M0'))
            traces.append(trace.summary())
            stats.append(memo.summary())
        self.assertEqual(fingerprint(untouched), fingerprint(results[0]))
        self.assertEqual(fingerprint(results[0]), fingerprint(results[1]))
        self.assertEqual(traces[0], traces[1])
        self.assertEqual(original, fingerprint(provenance))
        self.assertGreater(stats[1]['hits'], 0)
        self.assertGreater(stats[1]['misses'], 0)
        self.assertLessEqual(stats[1]['maxActiveCaches'], 2)
        self.assertTrue(any(c['fixedWidth'] for c in stats[1]['solvers']))
        self.assertTrue(any(c['epigraph'] for c in stats[1]['solvers']))
        self.assertTrue(any(c['kind'] == 'least_squares' for c in stats[1]['solvers']))
        self.assertTrue(any(c['kind'] == 'minimize' and not c['epigraph']
                            for c in stats[1]['solvers']))


if __name__ == '__main__': unittest.main()
