"""The referee witness's admission (W44 G0 (d); W46 G1, charter Decision Log 8 item 4).

    cd packages/calibration/results/holdout-configuration && python3.12 -B -m unittest test_configuration

W46 adds its adapter's schema `w46-referees-1` beside W44's `w44-referees-*`. These cases hold both
real manifests admitted with their path and SHA-256, the witness's refusals unchanged, and the
committed ledger untouched by reading it.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("configuration", HERE / "configuration.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)
RESULTS = HERE.parent
W44 = RESULTS / "2026-10-03-w44-g0-declaration/referees/referees.json"
W46 = RESULTS / "2026-10-05-w46-g0-declaration/referees/referees.json"


class RefereeWitness(unittest.TestCase):
    def assert_witness(self, path: Path) -> None:
        got = C.referee_witness(str(path))
        self.assertEqual(got, {"path": str(path.resolve().relative_to(C.ROOT)),
                               "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

    def test_w46_manifest_is_admitted(self):
        self.assertEqual(json.loads(W46.read_text())["schema"], "w46-referees-1")
        self.assert_witness(W46)

    def test_w44_manifest_is_still_admitted(self):
        self.assertEqual(json.loads(W44.read_text())["schema"], "w44-referees-1")
        self.assert_witness(W44)

    def manifest(self, **body) -> str:
        tmp = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump(body, tmp)
        tmp.close()
        self.addCleanup(Path(tmp.name).unlink)
        return tmp.name

    def test_other_schemas_are_refused(self):
        for schema in ("w45-referees-1", "w46-referees-2", "w46-referees", "referees-1", None):
            with self.subTest(schema=schema), self.assertRaises(SystemExit):
                C.referee_witness(self.manifest(schema=schema, scenes=["a"], profiles=["p"]))

    def test_a_w46_manifest_without_scenes_or_profiles_is_refused(self):
        for body in (dict(scenes=[], profiles=["p"]), dict(scenes=["a"], profiles=[]), dict(scenes=["a"])):
            with self.subTest(body=body), self.assertRaises(SystemExit):
                C.referee_witness(self.manifest(schema="w46-referees-1", **body))

    def test_reading_leaves_the_ledger_untouched(self):
        before = C.LOG.read_bytes()
        C.referee_witness(str(W46))
        C.load_log()
        self.assertEqual(C.LOG.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
