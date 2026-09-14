"""Admission-only tests: no seal, matrix, image, or scoring execution."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("score_bound", HERE / "score-bound.py")
scorer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scorer)


class Guards(unittest.TestCase):
    def test_scratch_refuses_owner_and_real_symlink(self):
        repo = HERE.parents[3]
        common = subprocess.check_output([
            "git", "-C", str(repo), "rev-parse", "--path-format=absolute", "--git-common-dir"
        ], text=True).strip()
        owner = Path(common).resolve().parent
        with tempfile.TemporaryDirectory() as temp:
            alias = Path(temp) / "alias"
            alias.symlink_to(owner, target_is_directory=True)
            for root in (repo, owner, alias):
                with self.assertRaisesRegex(SystemExit, "outside the repository"):
                    scorer.scratch_path(root / "packages/calibration/results/matrix.json", repo)
            scorer.scratch_path(Path(temp) / "scratch/result.json", repo)

    def test_renderer_check_cli_runs_only_admission(self):
        # Establish the guard-only dispatch before invoking its CLI, never the scoring main.
        self.assertTrue(scorer.check_renderer_command(["--check-renderer", "webgpu"]))
        import sys
        for renderer, succeeds in (("webgpu", True), ("css", False)):
            result = subprocess.run([sys.executable, str(HERE / "score-bound.py"),
                                     "--check-renderer", renderer], capture_output=True, text=True)
            self.assertEqual(result.returncode == 0, succeeds, result.stderr)
            if not succeeds:
                self.assertIn("only WebGPU", result.stderr)

    def test_css_record_only_read_cannot_be_scored(self):
        scorer.bound_renderer("webgpu")
        with self.assertRaisesRegex(SystemExit, "WebGPU"):
            scorer.bound_renderer("css")

    def test_placeholder_holdout_is_not_measurement_evidence(self):
        with self.assertRaisesRegex(SystemExit, "evidence"):
            scorer.measurement_evidence({"profile": "p", "scene": "s", "repeats": 2,
                                         "isHoldout": True})

    def test_complete_evidence_refuses_nonfinite_missing_geometry_and_unproved_pose(self):
        row = dict(profile="p", scene="s", repeats=2, scale=1, state="inactive",
                   isControl=False, isHoldout=False, preAttestationRecovered=False,
                   scored=True, groups=["D"], capture="/tmp/synthetic", nativePath="/synthetic",
                   captureSha256="a" * 64, nativeSha256="b" * 64, backgroundSha256="c" * 64,
                   nativeSource="sitting", nativeRun="run-1", problems=[],
                   deltaE={"mean": 0.1},
                   body=dict(n=1, deltaE=0.1, webY=0.5, nativeY=0.5, webSD=0.1,
                             nativeSD=0.1, webChroma=0.1, nativeChroma=0.1),
                   geometry=dict(capturedPixels=[2, 2], pixelSize=[2, 2], requestedScale=1,
                                 devicePixelRatio=1, canvas=dict(width=2, height=2)),
                   adapter=dict(ok=True, isFallback=False),
                   actualGroups=[dict(state=dict(activeRenderer="webgpu"))],
                   nativeAttestation=dict(presentedActive=False, presentation=dict(
                       observedPose="inactive", isKeyWindow=False, appIsActive=False)))
        scorer.measurement_evidence(row)
        scorer.measurement_evidence(dict(row, state="rest", nativeAttestation=dict(presentedActive=True)))
        for changed in (dict(deltaE={"mean": float("nan")}), dict(geometry={}),
                        dict(nativeAttestation={}), dict(nativeRun=None),
                        dict(captureSha256="missing"), dict(actualGroups=[])):
            with self.assertRaisesRegex(SystemExit, "evidence"):
                scorer.measurement_evidence(dict(row, **changed))

    def test_source_validation_reads_current_bytes_not_just_matrix_labels(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "runtime.ts"
            source.write_bytes(b"original")
            hashes = {"runtime.ts": hashlib.sha256(b"original").hexdigest()}
            scorer.verify_files(hashes, temp)
            source.write_bytes(b"changed")
            with self.assertRaisesRegex(SystemExit, "fingerprint mismatch"):
                scorer.verify_files(hashes, temp)


if __name__ == "__main__":
    unittest.main()
