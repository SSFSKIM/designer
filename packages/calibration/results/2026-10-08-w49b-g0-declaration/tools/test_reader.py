"""Gate-reader arithmetic and constraint coverage on complete pinned registry inputs."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
s = importlib.util.spec_from_file_location("w49b_read", HERE / "read.py")
R = importlib.util.module_from_spec(s); s.loader.exec_module(R)


class ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.registry = R.C.load_registry()

    def readings(self):
        return [R.C.evaluate_cell(c, None if c["partition"] != "gate" else c["current"],
                fidelity_value=c["fidelity"]["current"]) for c in self.registry["cells"]]

    def test_gate_report_keeps_all_twenty_without_an_exception_input(self):
        summary = R.summarize(self.registry, self.readings())
        self.assertEqual(summary["standingConstraints"], 20)
        self.assertEqual(summary["binding"]["total"], 10)
        self.assertEqual(summary["protected"]["total"], 5)
        self.assertEqual(summary["prior-repair"]["total"], 5)
        self.assertEqual(summary["binding"]["unmeasured"], 1)
        self.assertEqual(summary["prior-repair"]["unmeasured"], 3)
        self.assertEqual(summary["acceptance"], "UNMEASURED")
        self.assertEqual(summary["protected"]["currentFailures"], 0)

    def test_historical_failure_in_either_reference_group_still_fails_synthetic_repaired_registry(self):
        results = []
        for c in self.registry["cells"]:
            value = c["historical"]["value"] if c["historical"] else c["current"]
            results.append(R.C.evaluate_cell(c, value, fidelity_value=c["fidelity"]["current"]))
        for generation in ("d0219cd684bf", "b2d074d2df24"):
            c = next(c for c in self.registry["cells"] if c["role"] == "binding" and
                     c["historical"]["generation"] == generation)
            mutated = [r if r["scene"] != c["scene"] or r["scale"] != c["scale"] else
                       R.C.evaluate_cell(c, c["native"] + abs(c["historical"]["value"] - c["native"]) + 2*c["B"])
                       for r in results]
            summary = R.summarize(self.registry, mutated)
            self.assertGreater(summary["binding"]["historicalFailures"], 0)
            self.assertEqual(summary["measuredGateStatus"], "FAIL")

    def test_real_recorded_gate_pixels_reproduce_all_45_corrected_readings(self):
        import gzip
        import json
        import shutil
        import tempfile
        source = Path('/Users/new/vitrea-w49/b-grounding-scratch/renders/thin-active/1x')
        grounding = R.C.CAL / 'results/2026-10-08-w49b-grounding'
        candidate = Path('/Users/new/vitrea-w49/b-grounding-scratch/candidates/thin-active/candidate.json')
        self.assertTrue(source.is_dir(), 'Existing grounding pixels are required, not a new render')
        point = {"label": "thin-active", "pose": "rest"}
        plan = R.L.plan_run(self.registry, point, 1)
        archived = grounding / 'readings/thin-active/1x/matrix.json.gz'
        matrix_bytes = gzip.decompress(archived.read_bytes())
        rows = json.loads(matrix_bytes)['cells']
        expected = next(x for x in json.loads((grounding / 'probe-readings-corrected.json').read_text())
                        if x['label'] == 'thin-active' and x['scale'] == 1)
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            (folder / 'matrix.json').write_bytes(matrix_bytes)
            shutil.copytree(source / 'web-captures', folder / 'web-captures')
            shutil.copyfile(source / 'census.json', folder / 'census.json')
            R.C.write_new_json(folder / 'request.json', {**plan, 'batchSha256': 'synthetic-batch',
                'referencesSha256': 'synthetic-references', 'candidate': str(candidate),
                'candidateSha256': R.C.sha256(candidate)})
            evidence = {str(path.relative_to(folder)): R.C.sha256(path)
                        for path in (folder / 'web-captures').rglob('*') if path.is_file() and
                        (path.name == 'cell__webgpu.json' or path.name.endswith('__webgpu.png'))}
            R.C.write_new_json(folder / 'complete.json', {'matrixSha256': R.C.sha256(folder / 'matrix.json'),
                'requested': plan['requested'], 'planned': plan['planned'],
                'measured': [[r['key']['profileKey'], r['key']['web']['renderer'], r['key']['sceneId']] for r in rows],
                'captureEvidence': evidence})
            R.C.write_new_json(folder / 'exit.json', {'returncode': 0})
            R.C.write_new_json(folder / 'lock.json', {'token': 'synthetic-reader-fixture'})
            measured = R.read_run(self.registry, plan, folder, candidate, 'synthetic-batch', 'synthetic-references')
            self.assertEqual(set(measured), {(1, c['scene']) for c in expected['cells']})
            for original in expected['cells']:
                got = measured[1, original['scene']]
                self.assertAlmostEqual(got['growthCurrentInB'], original['growthCurrentInB'], places=12)
                self.assertEqual(got['rawT1'], original['probe'])
                self.assertEqual(got['meanNative'], original['meanNative'])
                self.assertEqual(got['meanWeb'], original['meanWeb'])
                if original['stratum'] == 'T':
                    self.assertEqual(got['measured'], original['bands']['web']['low'])
                    self.assertEqual(got['fidelityValue'], original['bands']['web']['fine'])
            # A self-consistent rewritten completion hash still cannot invent a measured metric.
            original_completion = (folder / 'complete.json').read_bytes()
            rows[0]['material']['interiorStdDevWeb']['value'] += .01
            (folder / 'matrix.json').write_text(json.dumps({'schemaVersion': 5, 'cells': rows}))
            changed_completion = json.loads(original_completion)
            changed_completion['matrixSha256'] = R.C.sha256(folder / 'matrix.json')
            (folder / 'complete.json').write_text(json.dumps(changed_completion))
            with self.assertRaisesRegex(ValueError, 'capture pixels'):
                R.read_run(self.registry, plan, folder, candidate, 'synthetic-batch', 'synthetic-references')
            (folder / 'matrix.json').write_bytes(matrix_bytes)
            (folder / 'complete.json').write_bytes(original_completion)
            # Completed pixels are witnesses, not a trustworthy-looking directory name.
            capture = next((folder / 'web-captures').rglob('*__webgpu.png'))
            capture.write_bytes(b'changed')
            with self.assertRaises(ValueError):
                R.read_run(self.registry, plan, folder, candidate, 'synthetic-batch', 'synthetic-references')

    def test_protected_historical_miss_is_reported_but_does_not_require_its_repair(self):
        results = self.readings()
        protected = [r for r in results if r["role"] == "protected"]
        self.assertTrue(all(r["historicalStatus"] == "FAIL" for r in protected))
        self.assertTrue(all(not r["historical"]["enforced"] for r in protected))
        self.assertTrue(all(not r["repaired"] for r in protected))
        self.assertEqual(R.summarize(self.registry, results)["protected"]["historicalFailures"], 5)


if __name__ == "__main__": unittest.main()
