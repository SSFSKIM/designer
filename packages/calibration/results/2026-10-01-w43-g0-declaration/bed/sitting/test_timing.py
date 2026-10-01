#!/usr/bin/env python3.12
"""W43 timing and dry-plan deriver tests (G0 (d) item 9). Nothing is launched: the plan is the
G1a-shaped stand-in (stand_in.py), the rates are W42 G1's committed attestations.

Run: python3.12 -m unittest -v test_timing    (from this directory)"""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


T = load('w43_timing_under_test', HERE / 'timing.py')
S = load('w43_stand_in_for_timing', HERE / 'stand_in.py')
D = load('w43_sitting_for_timing', HERE / 'sitting.py')
P = T.pass_spec()
CANONICAL, W42, PLAN = S.build()
SOURCES = S.sources_of(PLAN, CANONICAL, W42)
RATES = T.measure()


def priced(plan):
    P.validate_plan(plan, SOURCES)
    return T.price(plan, SOURCES, RATES)


class Membership(unittest.TestCase):
    def test_counts_are_the_plans_membership(self):
        got = priced(PLAN)
        want = sum(len(P.cells(P.derive_from(PLAN, SOURCES, p['name'], n)))
                   for p in P.pass_order(PLAN) if p['kind'] == 'capture' for n in range(1, p['runs'] + 1))
        self.assertEqual(got['totals']['captures'], want)
        self.assertEqual(want, 4103)               # the charter's G1a: 3,934 + 96 + 72 + the pose check
        self.assertEqual(got['totals']['dumpScenes'], sum(len(p['scenes']) for p in PLAN['passes']
                                                          if p['kind'] == 'dump'))
        self.assertEqual(got['totals']['dumpScenes'], 48)
        self.assertEqual(sum(q['captures'] for q in got['passes'] if q['kind'] == 'capture'), 4103)
        self.assertEqual(len(got['passes']), len(PLAN['passes']))
        self.assertEqual(len(got['boundaries']), len(PLAN['passes']) - 1)
        self.assertEqual((got['totals']['sliderWrites'], got['totals']['modeSwitches']), (2, 4))
        self.assertEqual(sum(b['sliderWrite'] for b in got['boundaries']), 2)
        self.assertEqual(sum(b['modeSwitch'] for b in got['boundaries']), 4)

    def test_one_more_run_costs_exactly_one_runs_model(self):
        plan = copy.deepcopy(PLAN)
        p = next(q for q in plan['passes'] if q['name'] == 'bed-0.25-2x-active')
        p['runs'] += 1
        cells = sum(len(v) for v in p['profiles'].values())
        delta = priced(plan)['exactTotalSeconds'] - priced(PLAN)['exactTotalSeconds']
        run = T.run_seconds(RATES, 'normal', 2, cells) + RATES['gapWithinPassSeconds']
        self.assertAlmostEqual(delta, run, places=6)
        self.assertEqual(priced(plan)['totals']['captures'] - 4103, cells)

    def test_removing_a_pass_removes_its_cost(self):
        # A pass whose neighbours share its mode and slider position: its cost and one boundary go.
        name = 'open-w42-2x-light-receded'
        plan = copy.deepcopy(PLAN)
        plan['passes'] = [q for q in plan['passes'] if q['name'] != name]
        full = priced(PLAN)
        cost = next(q['exactSeconds'] for q in full['passes'] if q['name'] == name)
        delta = full['exactTotalSeconds'] - priced(plan)['exactTotalSeconds']
        self.assertAlmostEqual(delta, cost + RATES['gapBetweenPassesSeconds'], places=6)

    def test_a_slider_change_and_a_mode_change_are_priced_at_their_boundary(self):
        got = priced(PLAN)
        b = next(b for b in got['boundaries'] if b['before'] == 'dump-0.25-2x-light-active')
        self.assertEqual((b['sliderWrite'], b['modeSwitch']), (True, True))      # 0.5 at 69 -> 0.25 at 68
        self.assertAlmostEqual(b['exactSeconds'], RATES['modeSwitchSeconds'] + RATES['sliderWriteSeconds'])

    def test_rates_are_w42_g1s_and_exclude_its_stops(self):
        self.assertEqual(RATES['admittedRuns'], 88)          # 8 dumps + 80 capture launches
        self.assertEqual(len(RATES['excludedStopGaps']), 2)   # stops 3-4 and 5, inside 2x-light-receded
        self.assertTrue(all(g['before'].startswith('2x-light-receded/') for g in RATES['excludedStopGaps']))
        for key in ('normal-1x', 'normal-2x', 'long-1x', 'long-2x'):
            self.assertIn(key, RATES['captureRates'])
        self.assertEqual(RATES['dump']['launches'], 8)
        check = T.self_check(RATES)
        self.assertLess(abs(check['differenceSeconds']), 0.01 * check['measuredSeconds'])


class DryPlan(unittest.TestCase):
    def test_the_dry_plan_launches_nothing(self):
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch('subprocess.run', side_effect=AssertionError('launched')), \
                mock.patch('subprocess.check_output', side_effect=AssertionError('read')), \
                mock.patch('subprocess.Popen', side_effect=AssertionError('spawned')):
            walk = D.dry_plan(PLAN, SOURCES, out=Path(tmp) / 'plan')
            self.assertTrue((Path(tmp) / 'plan' / 'plan.json').is_file())
        self.assertFalse(walk['executed'])
        self.assertEqual(walk['totals']['captures'], 4103)
        self.assertEqual(sum(r['cells'] for p in walk['passes'] if p['kind'] == 'capture' for r in p['runs']), 4103)
        self.assertEqual([p['name'] for p in walk['passes']], [p['name'] for p in PLAN['passes']])
        for p in walk['passes']:
            for r in p['runs']:
                self.assertNotIn('--dry-run', r['argv'])

    def test_the_summary_distils_every_argv(self):
        summary = load('w43_dry_summary_under_test', HERE / 'dry-plan-summary.py')
        with tempfile.TemporaryDirectory() as tmp:
            walk = D.dry_plan(PLAN, SOURCES, out=Path(tmp) / 'plan')
        distilled, text = summary.distil(walk, 'f' * 64, 'stand-in', True)
        self.assertTrue(all('argv' not in r and len(r['argvSha256']) == 64
                            for p in distilled['passes'] for r in p['runs']))
        self.assertIn('STAND-IN', text)
        self.assertIn('"captures": 4103', text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
