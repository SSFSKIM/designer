"""Synthetic tests only: no measured inventory, statistic or capture is opened."""
import importlib.util
import math
from pathlib import Path
import sys
import unittest
from dataclasses import replace

spec = importlib.util.spec_from_file_location('w50_judge_numerical', Path(__file__).with_name('numerical.py'))
j = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = j
spec.loader.exec_module(j)


def pair(a='a', r='b'):
    return j.DocumentPair(a * 64, r * 64)


def reading(value, units='linear-luma', native=False, documents=None):
    return j.Reading('MEASURED', units, value,
                     j.Evidence('c' * 64, 'd' * 64, None if native else documents or pair()))


def row(n=.25, c=.375, k=.25, *, statistic='T1-full-silhouette', units='linear-luma',
        code=.0625, bar=.03125, scene='checkerboard__rrect-md__rest', renderer='webgpu'):
    key = j.RowIdentity('apple-macos-27.0-1x-dark-standard-glass0.25', renderer,
                        scene, statistic, 'synthetic-declared-support')
    ref = j.Reference(key, 'e' * 64, reading(n, units, native=True), reading(c, units),
                      code, bar, max(code, 2 * bar))
    return ref, j.Candidate(key, reading(k, units, documents=pair('f', '0')))


def rgb(k=(20., 20., 20.), statistic='deep8-channel-median'):
    support = 'center8' if statistic == 'central8-channel-median' else 'deep8'
    key = j.RowIdentity('apple-macos-27.0-1x-dark-standard-glass0.25', 'webgpu',
                        'uniform__rrect-md__rest', statistic, support)
    ref = j.Reference(key, 'e'*64, reading((20.,)*3, 'encoded-RGB-codes', native=True),
                      reading((20.,)*3, 'encoded-RGB-codes'), 1, .5, 1)
    return ref, j.Candidate(key, reading(k, 'encoded-RGB-codes', documents=pair('f', '0')))


class NumericalTests(unittest.TestCase):
    def test_channel_errors_cannot_cancel_and_each_channel_has_own_bar(self):
        ref, candidate = rgb((22., 18., 20.))
        out = j.channel_level(ref, candidate)
        self.assertEqual(out.status, 'EXCEEDS')
        self.assertEqual([c.error for c in out.components], [2, 2, 0])
        ref = replace(ref, bar=(1., .5, .5), budget=(2., 1., 1.))
        self.assertEqual([c.status for c in j.channel_level(ref, candidate).components],
                         ['WITHIN', 'EXCEEDS', 'WITHIN'])

    def test_deep_and_center_independent_and_64_has_no_native_bound(self):
        deep, kd = rgb()
        center, kc = rgb((20., 22., 20.), 'central8-channel-median')
        self.assertEqual([r.status for r in j.uniform_levels(40, deep, kd, center, kc)],
                         ['WITHIN', 'EXCEEDS'])
        out = j.uniform_levels(64, deep, kd, center, kc)
        self.assertEqual([r.status for r in out], ['DIAGNOSTIC', 'DIAGNOSTIC'])
        self.assertTrue(all(c.bound is None for r in out for c in r.components))
        with self.assertRaises(ValueError): j.uniform_levels(69, deep, kd, center, kc)

    def test_paired_levels_refuse_different_candidate_document_pairs_or_capture(self):
        deep, kd = rgb()
        center, kc = rgb(statistic='central8-channel-median')
        for evidence in (replace(kc.reading.evidence, document_pair=pair('1', '2')),
                         replace(kc.reading.evidence, source_sha256='9'*64)):
            mixed = replace(kc, reading=replace(kc.reading, evidence=evidence))
            with self.assertRaises(ValueError): j.uniform_levels(40, deep, kd, center, mixed)

    def test_typed_source_kinds_preserve_cohort_and_reference_identity_without_inventing_pngs(self):
        for kind in ('png','native-three-run-cohort','frozen-reference-record'):
            evidence=j.Evidence(source_sha256='a'*64,statistic_sha256='b'*64,
                                document_pair=None,source_kind=kind)
            self.assertEqual(evidence.source_kind,kind)
            self.assertEqual(evidence.source_sha256,'a'*64)
            self.assertFalse(hasattr(evidence,'capture_sha256'))
        with self.assertRaises(ValueError):
            j.Evidence('a'*64,'b'*64,None,source_kind='pretend-png')
        deep,kd=rgb();center,kc=rgb(statistic='central8-channel-median')
        cohort=replace(center.native.evidence,source_kind='native-three-run-cohort')
        center=replace(center,native=replace(center.native,evidence=cohort))
        # The same digest bytes in different source namespaces are not the same evidence.
        with self.assertRaises(ValueError):j.uniform_levels(40,deep,kd,center,kc)
        deep=replace(deep,native=replace(deep.native,evidence=cohort))
        self.assertEqual([r.status for r in j.uniform_levels(40,deep,kd,center,kc)],['WITHIN','WITHIN'])

    def test_missing_budget_does_not_pass_and_T_regression_reads_low_not_fine(self):
        ref, candidate = row(statistic='T1-low')
        self.assertEqual(j.t1_growth(ref, candidate).status, 'WITHIN')
        ref = replace(ref, code=None, bar=None, budget=None)
        self.assertEqual(j.t1_growth(ref, candidate).status, 'UNMEASURED')

    def test_single_luma_original_key_uses_its_own_encoded_bound_without_a_sibling(self):
        for statistic in ('deep8-far24-luma-mean','deep8-far24-luma-median'):
            ref,candidate=row(20,23,22,statistic=statistic,units='encoded-luma-codes',code=1,bar=1)
            out=j.luma_level(ref,candidate)
            self.assertEqual(out.identity,ref.identity)
            self.assertEqual(out.status,'WITHIN')
            self.assertEqual(out.components[0].error,2)
            self.assertEqual(out.components[0].bound,2)
            worse=replace(candidate,reading=reading(22.01,'encoded-luma-codes'))
            self.assertEqual(j.luma_level(ref,worse).status,'EXCEEDS')
            missing=replace(candidate,reading=j.Reading('UNMEASURED_EMPTY_SUPPORT',
                'encoded-luma-codes',None,None,'empty original support'))
            self.assertEqual(j.luma_level(ref,missing).status,'UNMEASURED')
            with self.assertRaises(ValueError):
                j.luma_level(ref,replace(candidate,identity=replace(candidate.identity,scene='other')))
        for ref,candidate in (row(statistic='deep8-far24-luma-mean'),
                              row(20,20,20,statistic='deep8-luma-mean',
                                  units='encoded-luma-codes',code=1,bar=.5)):
            with self.assertRaises(ValueError):j.luma_level(ref,candidate)

    def test_luma_mean_and_median_do_not_cancel(self):
        mean = row(20, 22, 20, statistic='deep8-far24-luma-mean',
                   units='encoded-luma-codes', code=1, bar=.5)
        median = row(20, 22, 22, statistic='deep8-far24-luma-median',
                     units='encoded-luma-codes', code=1, bar=.5)
        self.assertEqual([r.status for r in j.luma_levels(*mean, *median)], ['WITHIN', 'EXCEEDS'])
        with self.assertRaises(ValueError):
            j.luma_levels(*row(statistic='deep8-far24-luma-mean'), *median)

    def test_css_is_error_growth_not_displacement_or_absolute_error(self):
        ref, candidate = row(20, 25, 14, statistic='deep8-far24-luma-mean',
                             units='encoded-luma-codes', code=1, bar=.5, renderer='css')
        out = j.css_level_growth(ref, candidate)
        self.assertEqual(out.status, 'WITHIN')  # displacement 11, error 6, growth 1
        self.assertEqual(out.components[0].growth, 1)
        self.assertEqual(j.css_level_growth(ref, replace(candidate, reading=reading(13.99,
                         'encoded-luma-codes'))).status, 'EXCEEDS')

    def test_t1_crossing_is_error_growth_and_adds_no_absolute_gate(self):
        ref, candidate = row(n=.25, c=.375, k=.0625)
        out = j.t1_growth(ref, candidate)
        self.assertEqual(out.status, 'WITHIN')
        self.assertEqual(out.components[0].growth, .0625)
        self.assertEqual(j.t1_growth(ref, replace(candidate, reading=reading(.06))).status, 'EXCEEDS')
        self.assertEqual(j.t1_growth(*row(n=.1, c=.45, k=.45)).status, 'WITHIN')
        with self.assertRaises(ValueError): j.t1_growth(*row(statistic='T1-fine'))

    def test_newbed_structured_t1_prices_both_tiers_without_widening_canonical_scope(self):
        for tier in ('webgpu','css'):
            ref, candidate = row(n=.25,c=.375,k=.0625,renderer=tier,
                                 scene='cell-checker-low-s096__rest')
            out=j.newbed_structured_t1_growth(ref,candidate)
            self.assertEqual(out.status,'WITHIN')
            self.assertEqual(out.components[0].growth,.0625)
            self.assertEqual(j.newbed_structured_t1_growth(ref,replace(candidate,reading=reading(.06))).status,
                             'EXCEEDS')
            if tier=='css':
                with self.assertRaises(ValueError):j.t1_growth(ref,candidate)
                with self.assertRaises(ValueError):
                    j.historical_growth(ref,candidate,j.Historical(reading(.25),.125,False))
        for scene in ('checkerboard__rrect-md__rest','cell-grey-000-s128__rest'):
            with self.assertRaises(ValueError):
                j.newbed_structured_t1_growth(*row(scene=scene,renderer='css'))
        with self.assertRaises(ValueError):
            j.newbed_structured_t1_growth(*row(scene='cell-impulse-sparse-s096__rest',statistic='T1-low'))

    def test_own_historical_reference_cap_is_unrounded_and_frozen(self):
        ref, candidate = row(n=.25, c=.4375, k=.4375)
        historical = j.Historical(reading(.3125, documents=pair('1', '2')), .125, False)
        result = j.historical_growth(ref, candidate, historical)
        self.assertEqual(result.status, 'WITHIN')
        self.assertEqual(result.components[0].bound, .125)
        self.assertEqual(j.historical_growth(ref, replace(candidate, reading=reading(.438)),
                                            historical).status, 'EXCEEDS')
        for changes in ({'frozen_current_growth': .126}, {'repaired': True}):
            with self.assertRaises(ValueError):
                j.historical_growth(ref, candidate, replace(historical, **changes))

    def test_frozen_in_B_normalization_proves_original_division_without_roundtrip_loss(self):
        ref,candidate=row(n=.1,c=.203,k=.203,code=.0003,bar=.00015)
        old=reading(.2,documents=pair('1','2'))
        raw=abs(.203-.1)-abs(.2-.1)
        normalized=10.000000000000009
        self.assertNotEqual(normalized*ref.budget,raw)
        history=j.historical_from_frozen_in_b(ref,old,frozen_current_growth_in_b=normalized,repaired=False)
        self.assertEqual(history.frozen_current_growth,raw)
        self.assertEqual(j.historical_growth(ref,candidate,history).status,'WITHIN')
        with self.assertRaises(ValueError):
            j.historical_from_frozen_in_b(ref,old,frozen_current_growth_in_b=10.0,repaired=False)

    def test_repaired_entry_cannot_revive_old_allowance(self):
        ref, candidate = row(n=.25, c=.3125, k=.375)
        repaired = j.Historical(reading(.25, documents=pair('1', '2')), .0625, True)
        out = j.historical_growth(ref, candidate, repaired)
        self.assertEqual(out.components[0].bound, .0625)
        self.assertEqual(out.status, 'EXCEEDS')

    def test_single_row_diagnostic_has_no_bound_and_keeps_missing_status(self):
        ref,candidate=rgb((20.,30.,10.),'central8-channel-median')
        ref=replace(ref,code=None,bar=None,budget=None)
        out=j.diagnostic_reading(ref,candidate)
        self.assertEqual(out.identity,ref.identity)
        self.assertEqual(out.status,'DIAGNOSTIC')
        self.assertEqual([c.error for c in out.components],[0,10,10])
        self.assertTrue(all(c.bound is None for c in out.components))
        scalar=j.diagnostic_reading(*row(statistic='T1-fine',renderer='css'))
        self.assertEqual(scalar.units,'linear-luma')
        self.assertEqual(scalar.status,'DIAGNOSTIC')
        missing=j.Reading('UNMEASURED_EMPTY_SUPPORT','encoded-RGB-codes',None,None,'empty')
        self.assertEqual(j.diagnostic_reading(replace(ref,native=missing),candidate).status,'UNMEASURED')

    def test_empty_support_is_explicitly_unmeasured(self):
        ref, candidate = rgb()
        absent = j.Reading('UNMEASURED_EMPTY_SUPPORT', 'encoded-RGB-codes', None, None,
                           'declared support empty')
        out = j.channel_level(replace(ref, native=absent), candidate)
        self.assertEqual(out.status, 'UNMEASURED')
        self.assertIn('UNMEASURED_EMPTY_SUPPORT', out.reason)
        self.assertEqual(out.components, ())

    def test_boundaries_reject_nonfinite_range_units_and_identity_errors(self):
        for value in (math.nan, math.inf, -.01, 256, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                reading(value, 'encoded-luma-codes')
        with self.assertRaises(ValueError): reading(.1, 'not-a-unit')
        with self.assertRaises(ValueError): j.Evidence('short', 'd'*64, pair())
        with self.assertRaises(ValueError): j.Reading('MEASURED', 'linear-luma', .2, None)
        ref, candidate = row()
        for changes in ({'code': 0}, {'bar': -1}, {'budget': .2}):
            with self.assertRaises(ValueError): replace(ref, **changes)
        with self.assertRaises(ValueError):
            j.t1_growth(ref, replace(candidate, identity=replace(candidate.identity, scene='other')))
        with self.assertRaises(TypeError): j.t1_growth({'native': .1}, candidate)

    def test_only_explicit_own_row_frozen_T1_budget_can_differ_from_fresh_repeat_budget(self):
        ref,candidate=row(n=.25,c=.375,k=.03125,code=.0625,bar=.0625)
        self.assertEqual(j.t1_growth(ref,candidate).status,'WITHIN')
        frozen=j.FrozenT1Budget(ref.identity,ref.inventory_sha256,.0625)
        old=replace(ref,budget=.0625,frozen_t1_budget=frozen)
        self.assertEqual(old.code,.0625)
        self.assertEqual(old.bar,.0625)
        self.assertEqual(j.t1_growth(old,candidate).status,'EXCEEDS')
        with self.assertRaises(ValueError):replace(ref,budget=.0625)
        with self.assertRaises(ValueError):
            replace(ref,budget=.0625,frozen_t1_budget=replace(frozen,inventory_sha256='9'*64))
        for identity in (replace(ref.identity,renderer='css'),
                         replace(ref.identity,profile=ref.identity.profile.replace('glass0.25','glass0.5')),
                         replace(ref.identity,scene='cell-checker-low-s096__rest')):
            with self.assertRaises(ValueError):j.FrozenT1Budget(identity,ref.inventory_sha256,.0625)

    def test_aggregate_epsilon_is_own_code_not_B_and_aggregate_is_median(self):
        cells = []
        for i, (code, k) in enumerate(((.03125, .03125), (.0625, .1875), (.03125, .21875))):
            ref, candidate = row(0, 0, k, code=code, bar=code,
                                 scene=f'checkerboard-{i}__rrect-md__rest')
            cells.append(j.AggregateCell(ref, candidate, reading(0, documents=pair('1', '2'))))
        out = j.target_aggregate('C rest', 1, cells, expected_keys=tuple(c.reference.identity for c in cells))
        self.assertAlmostEqual(out.candidate, math.log(4))
        self.assertEqual(out.current, 0)
        self.assertEqual(out.status, 'EXCEEDS')

    def test_halving_uses_w48_reference_and_P_pools_poses_against_current(self):
        cells = []
        for pose in ('rest', 'inactive'):
            ref, candidate = row(0, .0625, .125, scene=f'photo__rrect-md__{pose}')
            cells.append(j.AggregateCell(ref, candidate, reading(.25, documents=pair('1', '2'))))
        out = j.target_aggregate('P', 1, cells, expected_keys=tuple(c.reference.identity for c in cells))
        self.assertEqual(out.rule, 'current-nonworsening')
        self.assertEqual(out.status, 'EXCEEDS')
        ref, candidate = row(0, .0625, .125)
        cell = j.AggregateCell(ref, candidate, reading(.5, documents=pair('1', '2')))
        out = j.target_aggregate('C rest', 1, [cell], expected_keys=(ref.identity,))
        self.assertEqual(out.rule, 'w48-reference-halving')
        self.assertAlmostEqual(out.bound, .5 * math.log(9))
        self.assertEqual(out.status, 'WITHIN')

    def test_aggregate_cannot_drop_members_or_mix_scales_or_generations(self):
        ref, candidate = row()
        cell = j.AggregateCell(ref, candidate, reading(.375, documents=pair('1', '2')))
        keys = (ref.identity, replace(ref.identity, scene='checkerboard__rrect-lg__rest'))
        out = j.target_aggregate('C rest', 1, [cell], expected_keys=keys)
        self.assertEqual(out.status, 'UNMEASURED')
        self.assertIsNone(out.candidate)
        self.assertEqual(j.target_aggregate('C rest', 1, [], expected_keys=()).status, 'UNMEASURED')
        with self.assertRaises(ValueError):
            j.target_aggregate('C rest', 1, [cell, cell], expected_keys=(ref.identity,))
        with self.assertRaises(ValueError):
            j.target_aggregate('C rest', 2, [cell], expected_keys=(ref.identity,))
        ref2, k2 = row(scene='checkerboard__rrect-lg__rest')
        cell2 = j.AggregateCell(ref2, k2, reading(.375, documents=pair('3', '4')))
        with self.assertRaises(ValueError):
            j.target_aggregate('C rest', 1, [cell, cell2], expected_keys=(ref.identity, ref2.identity))

    def test_f_inactive_2x_uses_current_nonworsening_without_tau(self):
        ref, candidate = row(.25, .375, .375, scene='checkerboard-8__rrect-lg__inactive')
        identity = replace(ref.identity, profile=ref.identity.profile.replace('-1x-', '-2x-'))
        ref, candidate = replace(ref, identity=identity), replace(candidate, identity=identity)
        out = j.target_aggregate('F inactive', 2, [j.AggregateCell(ref, candidate)], expected_keys=(identity,))
        self.assertEqual(out.rule, 'current-nonworsening')
        self.assertEqual(out.status, 'WITHIN')
        candidate = replace(candidate, reading=reading(.375001))
        out = j.target_aggregate('F inactive', 2, [j.AggregateCell(ref, candidate)], expected_keys=(identity,))
        self.assertEqual(out.status, 'EXCEEDS')


if __name__ == '__main__':
    unittest.main()
