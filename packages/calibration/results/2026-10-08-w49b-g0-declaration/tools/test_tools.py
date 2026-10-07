"""CPU-only contracts for W49b tools; no browser, census observation or GPU launch."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("w49b_tools", HERE / "common.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def batch():
    return {"schemaVersion": 1, "id": "test", "domain": {
        "active.dark": {"tintAlphaSpanMax": [0, 160]}}, "points": [{
        "label": "identity", "scales": [1, 2], "pose": "rest", "overrides": {}}]}


def cell(scene="checker__rrect-lg__rest", role=None, partition="gate", statistic="T1-full-silhouette"):
    return {"profile": "p", "renderer": "webgpu", "scene": scene, "scale": 1,
            "pose": "rest", "stratum": "C", "partition": partition, "role": role,
            "statistic": statistic, "native": 0.1, "current": 0.07, "B": 0.01,
            "fidelity": {"statistic": "T1-fine" if statistic == "T1-low" else statistic,
                         "native": 0.08 if statistic == "T1-low" else 0.1,
                         "current": 0.06 if statistic == "T1-low" else 0.07},
            "historical": {"generation": "old", "value": 0.08, "maxGrowthInB": 1,
                           "enforced": role in ("binding", "prior-repair")} if role else None}


class BatchTests(unittest.TestCase):
    def test_prospective_point_enumeration_is_a_finite_domain_without_generated_points(self):
        source = {"schema": "w49b-g0-batch-1", "base": "b2d074d2df24-940384c06f73",
                  "points": batch()["points"]}
        normalized = C.validate_batch(source)
        self.assertEqual(len(normalized["points"]), 1)
        self.assertEqual(normalized["domain"], {})

    def test_finite_batch_refuses_unlisted_value_unknown_slot_and_duplicate_labels(self):
        C.validate_batch(batch())
        for change in (lambda b: b["points"][0].update(overrides={"active.dark": {"tintAlphaSpanMax": 192}}),
                       lambda b: b["domain"].update({"active.light": {"tintAlphaSpanMax": [160]}}),
                       lambda b: b["points"].append(b["points"][0]),
                       lambda b: b["points"][0].update(scales=[True]),
                       lambda b: b["domain"]["active.dark"].update({"backdropCaptureScale": [0]})):
            b = batch(); change(b)
            with self.assertRaises(ValueError): C.validate_batch(b)

    def test_current_protection_uses_error_growth_and_protected_limit_is_zero(self):
        protected = cell(role="protected")
        self.assertEqual(C.evaluate_cell(protected, 0.069)["currentStatus"], "FAIL")
        self.assertEqual(C.evaluate_cell(protected, 0.071)["currentStatus"], "PASS")
        # A crossing can displace by >B while reducing the error; displacement is not the guard.
        self.assertEqual(C.evaluate_cell(cell(), 0.12)["currentStatus"], "PASS")

    def test_binding_and_prior_repairs_intersect_current_and_historical_even_with_no_exceptions(self):
        for role in ("binding", "prior-repair"):
            c = cell(role=role)
            self.assertEqual(C.evaluate_cell(c, 0.065)["currentStatus"], "PASS")
            self.assertEqual(C.evaluate_cell(c, 0.065)["historicalStatus"], "FAIL")
            self.assertFalse(C.evaluate_cell(c, 0.065)["repaired"])
            self.assertTrue(C.evaluate_cell(c, 0.081)["repaired"])

    def test_withheld_is_never_repaired_and_t_low_is_distinct_from_fine(self):
        result = C.evaluate_cell(cell(role="binding", partition="referee"), None)
        self.assertEqual(result["historicalStatus"], "UNMEASURED")
        self.assertFalse(result["repaired"])
        c = cell(statistic="T1-low")
        r = C.evaluate_cell(c, 0.08, fidelity_value=0.02)
        self.assertEqual(r["growthCurrentInB"], -1.0)
        self.assertAlmostEqual(r["fidelityError"], 0.06)
        self.assertEqual(r["fidelityStatus"], "miss")

    def test_duplicate_extra_wrong_profile_and_wrong_pose_rows_cannot_meet_request(self):
        expected = [("p", "webgpu", "s")]
        row = {"key": {"profileKey": "p", "sceneId": "s", "web": {
            "renderer": "webgpu", "sceneId": "s", "engineVersion": C.ENGINE_VERSION}},
            "state": "rest", "fixtureSet": "calibration", "tier": "texture"}
        C.assert_membership(expected, [row])
        for rows in ([row, row], [], [{**row, "key": {**row["key"], "profileKey": "q"}}]):
            with self.assertRaises(ValueError): C.assert_membership(expected, rows)

    def test_lock_competitor_and_changed_owner_are_not_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "lock"
            p.mkdir()
            with self.assertRaises(FileExistsError):
                with C.owned_lock(p): pass
            self.assertTrue(p.exists()); p.rmdir()
            with self.assertRaises(ValueError):
                with C.owned_lock(p):
                    (p / "owner.json").write_text('{"token":"foreign"}')
            self.assertTrue(p.exists())

    def test_snapshots_and_exclusive_output_detect_mutation_and_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "data.json"
            C.write_new_json(p, {"answer": 1})
            pin = {"path": str(p), "sha256": C.sha256(p)}
            self.assertEqual(C.read_pinned(pin), {"answer": 1})
            with self.assertRaises(FileExistsError): C.write_new_json(p, {})
            p.write_text('{}')
            with self.assertRaises(ValueError): C.read_pinned(pin)


if __name__ == "__main__":
    unittest.main()
