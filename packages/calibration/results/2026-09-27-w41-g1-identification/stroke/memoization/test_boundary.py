"""JSON-boundary numeric equivalence must not weaken live typed trace equality."""
import copy
import json
import unittest
import numpy as np
import proof
from solver_memo import fingerprint


def result_fixture():
    return json.loads((proof.HERE/'synthetic-proof-2/untouched-result.json').read_text())


def six_gap_reports(result):
    return [result['starts'][0][name] for name in (
        'minimax', 'rawStartMinimax', 'lsSeededMinimax', 'originalMinimax',
        'widthLsSeededMinimax')] + [result['minimax']]


class BoundaryTests(unittest.TestCase):
    def test_six_live_numpy_gaps_match_reloaded_json_at_exact_float64_bits(self):
        live = result_fixture()
        for i, report in enumerate(six_gap_reports(live)):
            report['epigraphGapCodes'] = np.float64(-0. if i == 0 else i*1e-9)
        reloaded = json.loads(json.dumps(live, allow_nan=False))
        self.assertNotEqual(fingerprint(live), fingerprint(reloaded))
        proof.identical_result_boundary(live, reloaded, 'live versus reloaded JSON')
        # The live comparator retains the distinction. Only the artifact
        # boundary gets schema-declared numeric normalization.
        with self.assertRaises(AssertionError):
            proof.identical(live, reloaded, 'live typed fingerprint remains strict')

    def test_numeric_bit_changes_and_nonnumeric_type_changes_still_fail(self):
        baseline = result_fixture()
        baseline['minimax']['epigraphGapCodes'] = 0.
        changes = (
            lambda r: r['minimax'].__setitem__('epigraphGapCodes', -0.),
            lambda r: r['minimax'].__setitem__('maximumCodes',
                np.nextafter(r['minimax']['maximumCodes'], np.inf)),
            lambda r: r['minimax']['coefficients'].__setitem__(0,
                np.nextafter(r['minimax']['coefficients'][0], np.inf)),
            lambda r: r['minimax'].__setitem__('evaluations', float(r['minimax']['evaluations'])),
            lambda r: r['minimax'].__setitem__('optimizerSuccess', np.bool_(r['minimax']['optimizerSuccess'])),
            lambda r: r.__setitem__('unexpected', np.float64(1.)),
        )
        baseline['unexpected'] = 1.
        for change in changes:
            changed = copy.deepcopy(baseline); change(changed)
            with self.subTest(change=change), self.assertRaises(AssertionError):
                proof.identical_result_boundary(baseline, changed, 'changed value')
        for invalid in (True, '0.0', float('nan'), float('inf')):
            changed = copy.deepcopy(baseline)
            changed['minimax']['maximumCodes'] = invalid
            with self.subTest(invalid=invalid), self.assertRaises((TypeError, ValueError)):
                proof.identical_result_boundary(baseline, changed, 'invalid numeric field')




# These tests exercise comparison/reuse only. Native readers and optimizers are
# forbidden; the real held start selector is still used to derive provenance.
import gzip
import hashlib
import tempfile
from pathlib import Path
from unittest.mock import patch

OLD_COMMIT = '853581462ed564b9f4a7a5bbe7c56460edafa43d'


def amendment_fixture(root):
    record, diff = proof.driver_amendment_data(OLD_COMMIT)
    diff_path = root/'driver.diff'; diff_path.write_bytes(diff)
    record['diff'] = dict(path=str(diff_path), sha256=proof.sha(diff_path))
    path = root/'amendment.json'; proof.write(path, record)
    return dict(path=str(path), sha256=proof.sha(path)), record


class ReuseTests(unittest.TestCase):
    def test_only_pinned_driver_change_is_compatible(self):
        with tempfile.TemporaryDirectory(dir=proof.HERE) as folder:
            root = Path(folder)
            reference, record = amendment_fixture(root)
            right = proof.sources()
            left = dict(right, **{record['sourcePath']: record['oldSourceSha256']})
            proof.compatible_sources(left, right, reference)
            with self.assertRaises(AssertionError):
                proof.compatible_sources(left, right)
            changed = dict(right)
            changed[str(proof.HERE/'solver_memo.py')] = 'f'*64
            with self.assertRaisesRegex(AssertionError, 'scientific and solver-wrapper'):
                proof.compatible_sources(left, changed, reference)
            changed = dict(right, **{record['sourcePath']: 'f'*64})
            with self.assertRaisesRegex(AssertionError, 'admitted old/new pair'):
                proof.compatible_sources(left, changed, reference)
            Path(record['diff']['path']).write_bytes(b'changed diff')
            with self.assertRaisesRegex(ValueError, 'diff bytes changed'):
                proof.compatible_sources(left, right, reference)

    def test_additive_reuse_preserves_failed_terminal_and_all_saved_bytes(self):
        with tempfile.TemporaryDirectory(dir=proof.HERE) as folder:
            root = Path(folder)
            amendment, amendment_record = amendment_fixture(root)
            saved, baseline_dir = root/'saved', root/'baseline'
            saved.mkdir(); baseline_dir.mkdir()
            _, provenance = proof.start_partition.partition(proof.f.fit_local, [0])
            result = dict(family='M1', cssWidth=False, curvature=False,
                starts=[dict(startIndex=0, initial=proof.f.domain('M1')[2].tolist())],
                leastSquares=None, minimax=None)
            completed = dict(result, partitionProvenance=provenance, seconds=1.,
                fittedEndpoints=['light-inactive'], dummyEndpoints=['synthetic'], authority='synthetic')
            baseline = baseline_dir/'completed.json'; proof.write(baseline, completed)
            proof.write(baseline_dir/'calibration-admission.json', [])
            proof.write(saved/'calibration-admission.json', [])
            proof.write(saved/'raw-result.json', result)
            trace = b'{"event":"synthetic-callback"}\n'
            (saved/'trace.jsonl.gz').write_bytes(gzip.compress(trace))
            trace_witness = dict(sha256=hashlib.sha256(trace).hexdigest(), events=1,
                                 counts={'synthetic-callback': 1})
            old_sources = dict(proof.sources(), **{
                amendment_record['sourcePath']: amendment_record['oldSourceSha256']})
            proof.write(saved/'replay.json', dict(mode='unwrapped', trace=trace_witness,
                rawResultBitsSha256=fingerprint(result), sourceSha256=old_sources,
                environment={'qualification': 'synthetic bookkeeping only'}))
            terminal = root/'terminal.json'
            proof.write(terminal, dict(kind='STROKE_VERIFICATION_TERMINAL', mode='unwrapped',
                status='failed-after-solver-start', solverStarted=True, error=dict(type='AssertionError',
                    message='completed native raw result differs at exact typed/bit witness')))
            terminal_ref = dict(path=str(terminal), sha256=proof.sha(terminal))
            before = {str(p): proof.sha(p) for p in [terminal, *saved.iterdir()]}
            with patch.object(proof, 'COMPLETED', baseline), \
                    patch.object(proof.r, 'guarded_reader', side_effect=AssertionError('native read')), \
                    patch.object(proof.r, 'Preparation', side_effect=AssertionError('native preparation')), \
                    patch.object(proof.f, 'least_squares', side_effect=AssertionError('optimizer')), \
                    patch.object(proof.f, 'minimize', side_effect=AssertionError('optimizer')):
                receipt = proof.reuse_native(saved, root/'comparison', terminal_ref, amendment)
            self.assertEqual(receipt['comparisonRerun']['action'], 'solve reused, comparison rerun')
            self.assertEqual(receipt['sourceSha256'], old_sources)
            self.assertEqual(receipt['rawResultBitsSha256'], fingerprint(result))
            self.assertEqual(receipt['artifactDirectory'], str(saved))
            self.assertEqual(before, {path: proof.sha(path) for path in before})
            self.assertTrue((root/'comparison/completed-start-proof.json').exists())
            # A recomputed trace witness is mandatory, not just a manifest copy.
            (saved/'trace.jsonl.gz').write_bytes(gzip.compress(trace+trace))
            with self.assertRaises(AssertionError):
                proof.verify_saved_trace(saved/'trace.jsonl.gz', trace_witness)


if __name__ == '__main__': unittest.main()
