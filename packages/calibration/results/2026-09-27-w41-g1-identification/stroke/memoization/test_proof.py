"""Proof bookkeeping fails closed without reading native payloads or fitting."""
import gzip
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import proof


ARTIFACTS = ('trace.jsonl.gz', 'raw-result.json', 'replay.json')


def proof_pair(root):
    """Complete synthetic receipts and real files, with distinct gzip metadata."""
    raw = dict(starts=[dict(startIndex=0, initial=[0., -0.])], family='synthetic')
    trace = b'{"event":"synthetic-input","value":1}\n'
    base = dict(schema='w41-memoization-native-one-mode-1', verified=True,
        completedArtifact='/synthetic/artifact', completedSha256='a'*64,
        completedExceptSecondsBitsSha256='b'*64,
        partitionProvenance={'originalStartIndices': [0]}, nativeScope='synthetic test',
        classification='verification replay, not a new candidate',
        rawResultBitsSha256=proof.fingerprint(raw),
        jsonBoundaryResultBitsSha256=proof.result_boundary_fingerprint(raw),
        trace={'sha256': hashlib.sha256(trace).hexdigest(), 'events': 1},
        sourceSha256={'wrapper': 'e'*64}, environment={'python': 'synthetic'})
    directories = []
    for i, mode in enumerate(('unwrapped', 'wrapped')):
        directory = root/mode
        directory.mkdir()
        (directory/'trace.jsonl.gz').write_bytes(gzip.compress(trace, mtime=i+1))
        proof.write(directory/'raw-result.json', raw)
        proof.write(directory/'replay.json', dict(mode=mode, trace=base['trace'],
            rawResultBitsSha256=base['rawResultBitsSha256']))
        receipt = dict(base, mode=mode,
            artifacts={name: proof.sha(directory/name) for name in ARTIFACTS})
        proof.write(directory/'completed-start-proof.json', receipt)
        directories.append(directory)
    return directories


class ProofTests(unittest.TestCase):
    def test_denied_admission_cannot_enter_native_reader_or_optimizer(self):
        with tempfile.TemporaryDirectory(dir=proof.HERE) as root:
            with patch.object(proof.r, 'guarded_reader', side_effect=AssertionError('native read')), \
                    patch.object(proof.f, 'fit_local', side_effect=AssertionError('optimizer')):
                with self.assertRaises(PermissionError):
                    proof.native_once('wrapped', Path(root)/'denied',
                                      lambda stage: dict(admitted=False, stage=stage))
            self.assertFalse((Path(root)/'denied/raw-result.json').exists())
            self.assertEqual(json.loads((Path(root)/'denied/before-preparation-admission.json')
                                       .read_text())['admitted'], False)

    def test_comparison_rejects_tampering_and_deletion_of_each_required_artifact(self):
        for mode in ('unwrapped', 'wrapped'):
            for name in ARTIFACTS:
                for action in ('tamper', 'delete'):
                    with self.subTest(mode=mode, name=name, action=action), \
                            tempfile.TemporaryDirectory(dir=proof.HERE) as root:
                        root = Path(root)
                        left, right = proof_pair(root)
                        artifact = root/mode/name
                        if action == 'tamper':
                            artifact.write_bytes(artifact.read_bytes()+b'changed')
                        else:
                            artifact.unlink()
                        with self.assertRaisesRegex(ValueError, 'artifact'):
                            proof.compare_native(left, right, root/'must-not-publish.json')
                        self.assertFalse((root/'must-not-publish.json').exists())

    def test_comparison_requires_all_artifact_pins_not_an_optional_subset(self):
        for omitted in ARTIFACTS:
            with self.subTest(omitted=omitted), tempfile.TemporaryDirectory(dir=proof.HERE) as root:
                root = Path(root)
                left, right = proof_pair(root)
                path = right/'completed-start-proof.json'
                receipt = json.loads(path.read_text())
                del receipt['artifacts'][omitted]
                path.write_text(json.dumps(receipt))
                with self.assertRaisesRegex(ValueError, 'required artifact'):
                    proof.compare_native(left, right, root/'must-not-publish.json')
                self.assertFalse((root/'must-not-publish.json').exists())

    def test_distinct_compressed_bytes_with_identical_ordered_trace_are_accepted(self):
        with tempfile.TemporaryDirectory(dir=proof.HERE) as root:
            root = Path(root)
            left, right = proof_pair(root)
            self.assertNotEqual(proof.sha(left/'trace.jsonl.gz'), proof.sha(right/'trace.jsonl.gz'))
            self.assertEqual(gzip.decompress((left/'trace.jsonl.gz').read_bytes()),
                             gzip.decompress((right/'trace.jsonl.gz').read_bytes()))
            receipt = proof.compare_native(left, right, root/'matches.json')
            self.assertTrue(receipt['verified'])

    def test_comparison_requires_matching_ordered_trace_and_source_bytes(self):
        with tempfile.TemporaryDirectory(dir=proof.HERE) as root:
            root = Path(root)
            left, right = proof_pair(root)
            right_file = right/'completed-start-proof.json'
            base = json.loads(right_file.read_text())
            for field, value in (('trace', {'sha256': 'f'*64, 'events': 1}),
                                 ('sourceSha256', {'wrapper': 'f'*64}),
                                 ('rawResultBitsSha256', 'f'*64)):
                right_file.write_text(json.dumps(dict(base, **{field: value})))
                with self.assertRaises(AssertionError):
                    proof.compare_native(left, right, root/'must-not-exist.json')
                self.assertFalse((root/'must-not-exist.json').exists())


if __name__ == '__main__': unittest.main()
