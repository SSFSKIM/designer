"""Tests for the W27f G2 measurement runner, on the failures review found in it.

Stdlib `unittest`, and run directly:

    python packages/calibration/results/2026-09-11-w27f-g2/measure-tests.py

Every case here was written to FAIL against the runner as first landed, so that
the fix is what turns it green rather than the test being shaped around the code:

* a capture command that produces nothing must not be reported as a capture
  because an earlier attempt's files are still on disk under the same names;
* one phase must be one configuration, and a manifest merged from two capture
  invocations has to prove it per scheme rather than carry one provenance for
  all of them;
* a fingerprint recorded under a narrower scope may not be compared against one
  recorded under a wider scope as though the two measured the same thing;
* a phase that authors a hint without measuring it must inherit the level from a
  phase that did, over the same background raster, and stop where none did.

Nothing here starts a browser: the capture commands are replaced by a fake that
writes (or refuses to write) the artefacts, which is the whole of what the
freshness rule is about.
"""
import importlib.util
import json
import shutil
import tempfile
import time
import unittest
from pathlib import Path

RUNNER = Path(__file__).with_name("measure.py")
_spec = importlib.util.spec_from_file_location("w27f_g2", RUNNER)
g1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(g1)


class Scratch(unittest.TestCase):
    def setUp(self):
        self.out = Path(tempfile.mkdtemp(prefix="w27f-g2-test-"))
        self.addCleanup(shutil.rmtree, self.out, True)
        self.scheme = g1.SCHEMES["light"]
        self.arm = g1.ARMS_BY_NAME["unsampled-hint"]

    def write_artefacts(self, scene, when=None):
        """The three files a real capture leaves, optionally back-dated."""
        directory = g1.capture_dir(self.out, "candidate", self.scheme, self.arm, scene)
        directory.mkdir(parents=True, exist_ok=True)
        for name in g1.artefacts_of(self.arm, scene):
            path = directory / name
            path.write_text("{}")
            if when is not None:
                import os
                os.utime(path, (when, when))
        return directory


class Freshness(Scratch):
    """A capture is what THIS invocation wrote, not what is lying in its place."""

    def test_previous_attempts_output_is_not_this_runs_capture(self):
        scene = "checkerboard__rrect-md__rest"
        self.write_artefacts(scene, when=time.time() - 3600)
        faults = g1.stale_or_missing(self.out, "candidate", self.scheme, self.arm, [scene],
                                     since=time.time())
        self.assertEqual(len(faults), 3, faults)
        self.assertTrue(all("older than this run" in fault for fault in faults), faults)

    def test_a_capture_written_now_passes(self):
        scene = "checkerboard__rrect-md__rest"
        started = time.time()
        self.write_artefacts(scene)
        self.assertEqual(g1.stale_or_missing(self.out, "candidate", self.scheme, self.arm,
                                             [scene], since=started), [])

    def test_a_png_without_its_cell_and_report_is_not_a_capture(self):
        scene = "checkerboard__rrect-md__rest"
        started = time.time()
        directory = g1.capture_dir(self.out, "candidate", self.scheme, self.arm, scene)
        directory.mkdir(parents=True)
        (directory / f"{scene}__{self.arm.tier}.png").write_text("x")
        faults = g1.stale_or_missing(self.out, "candidate", self.scheme, self.arm, [scene],
                                     since=started)
        self.assertEqual([f.split("/")[-1] for f in faults],
                         [f"cell__{self.arm.tier}.json (absent)",
                          f"report__{self.arm.tier}.json (absent)"])

    def test_clearing_removes_only_the_scenes_being_recaptured(self):
        keep, retake = "photo__rrect-md__rest", "checkerboard__rrect-md__rest"
        self.write_artefacts(keep)
        self.write_artefacts(retake)
        matrix = self.out / "candidate" / "light" / f"{self.arm.name}-matrix.json"
        matrix.parent.mkdir(parents=True, exist_ok=True)
        matrix.write_text("{}")
        g1.clear_scene_outputs(self.out, "candidate", self.scheme, self.arm, [retake], matrix)
        self.assertFalse(g1.capture_dir(self.out, "candidate", self.scheme, self.arm,
                                        retake).exists())
        self.assertTrue(g1.capture_dir(self.out, "candidate", self.scheme, self.arm, keep).exists())
        self.assertFalse(matrix.exists())


def provenance(commit="abc1234", sources=None, scope=None, profiles=None):
    # Resolved at call time so this module still imports against a runner that
    # has no scope at all — which is the state these tests were written against.
    return {"commit": commit,
            "materialSourcesScope": scope or getattr(g1, "MATERIAL_SOURCES_SCOPE", None),
            "materialSourcesSha256": sources or {"packages/renderer-webgpu/src": "aaa"},
            "materialProfileSha256": profiles or {"light": "lll", "dark": "ddd"}}


class OneConfiguration(Scratch):
    """A phase is one configuration, and a merged manifest has to show it per scheme."""

    def test_two_schemes_on_the_same_configuration_are_one_phase(self):
        g1.check_one_configuration({"light": {"capturedWith": provenance()},
                                    "dark": {"capturedWith": provenance()}})

    def test_a_scheme_captured_after_a_runtime_change_is_refused(self):
        with self.assertRaises(SystemExit) as raised:
            g1.check_one_configuration({
                "light": {"capturedWith": provenance()},
                "dark": {"capturedWith": provenance(
                    sources={"packages/renderer-webgpu/src": "bbb"})},
            })
        self.assertIn("different configurations", str(raised.exception))

    def test_an_unrelated_dirty_file_does_not_split_a_phase(self):
        light = provenance()
        dark = {**provenance(), "dirtyPaths": ["docs/whatever.md"]}
        g1.check_one_configuration({"light": {"capturedWith": light},
                                    "dark": {"capturedWith": dark}})

    def test_a_capture_without_provenance_cannot_be_read_as_this_phase(self):
        with self.assertRaises(SystemExit) as raised:
            g1.check_one_configuration({"light": {}})
        self.assertIn("no capturedWith provenance", str(raised.exception))

    def test_a_narrower_fingerprint_scope_is_not_comparable(self):
        with self.assertRaises(SystemExit) as raised:
            g1.check_one_configuration({
                "light": {"capturedWith": provenance(scope="material-files-only")},
                "dark": {"capturedWith": provenance()},
            })
        self.assertIn("different fingerprint scopes", str(raised.exception))


class LegacyManifests(unittest.TestCase):
    """A baseline cannot be re-captured, so its manifest stays readable — as itself."""

    def test_phase_level_provenance_is_attached_and_labelled(self):
        captured = {"capturedWith": provenance(scope="material-files-only"),
                    "schemes": {"light": {"scenes": []}, "dark": {"scenes": []}}}
        schemes = g1.with_legacy_provenance(captured)
        for scheme in schemes.values():
            self.assertEqual(scheme["capturedWith"]["materialSourcesScope"], "material-files-only")
            self.assertIn("phase-level", scheme["provenanceAttribution"])
            self.assertEqual(scheme["armNames"], [arm.name for arm in g1.ARMS])
            self.assertIn("assumed", scheme["armNamesSource"])
        g1.check_one_configuration(schemes)

    def test_a_recorded_per_scheme_manifest_is_left_alone(self):
        captured = {"schemes": {"light": {"capturedWith": provenance(),
                                          "armNames": ["sampled"]}}}
        schemes = g1.with_legacy_provenance(captured)
        self.assertEqual(schemes["light"]["provenanceAttribution"], "per-scheme")
        self.assertEqual(schemes["light"]["armNames"], ["sampled"])
        self.assertNotIn("armNamesSource", schemes["light"])


class Fingerprint(unittest.TestCase):
    """The digested scope has to contain the files this gate changes."""

    def test_the_wired_dom_material_is_inside_the_fingerprint(self):
        wired = ["packages/renderer-webgpu/src/renderer.ts",
                 "packages/renderer-webgpu/src/passes.ts",
                 "packages/renderer-webgpu/src/material.ts",
                 "packages/platform-web/src/root.ts",
                 "packages/platform-web/src/renderer-bridge.ts",
                 "packages/platform-web/src/optics.ts",
                 "packages/platform-web/src/css-tier.ts"]
        for source in wired:
            self.assertTrue(any(source.startswith(f"{tree}/") for tree in g1.MATERIAL_SOURCES),
                            f"{source} is outside the fingerprint")

    def test_a_tree_digest_follows_a_file_inside_it(self):
        root = Path(tempfile.mkdtemp(prefix="w27f-g1-digest-"))
        self.addCleanup(shutil.rmtree, root, True)
        (root / "src").mkdir()
        (root / "src" / "a.ts").write_text("one")
        before = g1.digest(root / "src")
        (root / "src" / "a.ts").write_text("two")
        self.assertNotEqual(before, g1.digest(root / "src"))


class InheritedLevels(unittest.TestCase):
    """A phase that does not sample inherits the level, or says it cannot."""

    spec = {"scenes": [
        {"id": "checkerboard__rrect-md__rest", "background": "checkerboard"},
        {"id": "checkerboard__glass-over-glass__rest", "background": "checkerboard"},
        {"id": "hc-text__rrect-md__rest", "background": "hc-text"},
    ]}

    def source(self, levels):
        return {"name": "candidate phase (light)",
                "levels": g1.background_levels(self.spec, levels)}

    def test_a_level_measured_on_one_scene_serves_the_same_raster(self):
        source = self.source({"checkerboard__rrect-md__rest": 0.21404114048223255})
        levels, per_scene = g1.inherited_levels(
            self.spec, ["checkerboard__glass-over-glass__rest"], [source])
        self.assertEqual(levels["checkerboard__glass-over-glass__rest"], 0.21404114048223255)
        self.assertEqual(per_scene["checkerboard__glass-over-glass__rest"]["background"],
                         "checkerboard")
        self.assertEqual(per_scene["checkerboard__glass-over-glass__rest"]["measuredOn"],
                         ["checkerboard__rrect-md__rest"])

    def test_an_unmeasured_raster_stops_the_run_rather_than_inventing_a_hint(self):
        source = self.source({"checkerboard__rrect-md__rest": 0.214})
        with self.assertRaises(SystemExit) as raised:
            g1.inherited_levels(self.spec, ["hc-text__rrect-md__rest"], [source])
        message = str(raised.exception)
        self.assertIn("hc-text", message)
        self.assertIn("would be invented", message)

    def test_a_level_measured_here_must_equal_the_one_measured_before(self):
        source = self.source({"checkerboard__rrect-md__rest": 0.21404114048223255})
        agrees = g1.check_levels_against_sources(
            self.spec, {"checkerboard__glass-over-glass__rest": 0.21404114048223255}, [source])
        self.assertEqual(agrees, [{"source": "candidate phase (light)",
                                   "backgrounds": ["checkerboard"]}])

    def test_a_level_that_moved_between_two_runs_stops_the_later_one(self):
        source = self.source({"checkerboard__rrect-md__rest": 0.214})
        with self.assertRaises(SystemExit) as raised:
            g1.check_levels_against_sources(
                self.spec, {"checkerboard__glass-over-glass__rest": 0.215}, [source])
        self.assertIn("sampled analysis has moved", str(raised.exception))

    def test_a_raster_no_earlier_run_measured_is_simply_not_cross_checked(self):
        source = self.source({"checkerboard__rrect-md__rest": 0.214})
        self.assertEqual(
            g1.check_levels_against_sources(self.spec, {"hc-text__rrect-md__rest": 0.5}, [source]),
            [])

    def test_one_raster_with_two_levels_falsifies_the_inheritance_and_is_refused(self):
        with self.assertRaises(SystemExit) as raised:
            g1.background_levels(self.spec, {"checkerboard__rrect-md__rest": 0.21,
                                             "checkerboard__glass-over-glass__rest": 0.42})
        self.assertIn("different sampled levels", str(raised.exception))


class TextureIdentity(unittest.TestCase):
    """Byte equality is reported on its own terms, never softened by attribution."""

    arm = g1.ARMS_BY_NAME["sampled"]

    def row(self, scene, identical, deltas, deterministic=True, noise=0, geometry=None):
        comparison = {"phase": "baseline", "pixelIdentical": identical, "sha256": "bb" * 32,
                      **deltas}
        if geometry is not None:
            comparison["changedPixelGeometry"] = geometry
        return {"scene": scene, "readings": {self.arm.name: {
            "sha256": "aa" * 32, "deterministic": deterministic, "repeatNoise": noise,
            "comparisons": {"vsG0": None, "vsComparePhase": comparison}}}}

    def verdict(self, rows):
        return g1.texture_identity(rows, [self.arm])[self.arm.name]

    def test_a_differing_digest_is_moved_whatever_the_terms_say(self):
        verdict = self.verdict([self.row("a", False, {"interiorOklabLMeanDelta": 0.01})])
        self.assertEqual([case["scene"] for case in verdict["moved"]], ["a"])
        self.assertFalse(verdict["moved"][0]["measuredTermsUnchanged"])
        self.assertEqual(verdict["moved"][0]["movedTerms"], {"interiorOklabLMeanDelta": 0.01})

    def test_a_noisy_capture_is_still_moved_and_the_noise_is_an_annotation(self):
        verdict = self.verdict([self.row("a", False, {"interiorOklabLMeanDelta": 0.0},
                                         deterministic=False, noise=5.8e-05)])
        self.assertEqual([case["scene"] for case in verdict["moved"]], ["a"])
        self.assertFalse(verdict["moved"][0]["captureIsByteDeterministic"])
        self.assertEqual(verdict["moved"][0]["repeatNoise"], 5.8e-05)

    def test_unchanged_terms_annotate_a_moved_cell_and_never_excuse_it(self):
        verdict = self.verdict([self.row("a", False, {"interiorOklabLMeanDelta": 0.0,
                                                      "rimBandLinearMeanDelta": 0.0})])
        self.assertEqual([case["scene"] for case in verdict["moved"]], ["a"])
        self.assertTrue(verdict["moved"][0]["measuredTermsUnchanged"])
        self.assertEqual(verdict["moved"][0]["movedTerms"], {})

    def test_where_the_pixels_changed_travels_with_the_verdict_when_measured(self):
        geometry = {"comparable": True, "changedPixels": 12,
                    "changedInsideDeclaredFootprint": 0, "changedInsideDeclaredInterior": 0,
                    "changedOutsideEveryDeclaredShape": 12,
                    "changedInsideTheDecidableExterior": 12, "maxChannelDifference": 1}
        verdict = self.verdict([self.row("a", False, {}, geometry=geometry)])
        self.assertEqual(verdict["moved"][0]["changedPixelGeometry"], geometry)

    def test_nothing_to_compare_against_is_never_a_pass(self):
        row = self.row("a", True, {})
        row["readings"][self.arm.name]["comparisons"]["vsComparePhase"] = None
        verdict = self.verdict([row])
        self.assertEqual(verdict["undecided"], ["a"])
        self.assertEqual(verdict["identical"], [])

    def test_an_arm_this_phase_did_not_take_over_a_scene_is_skipped(self):
        row = {"scene": "a", "readings": {}}
        self.assertEqual(self.verdict([row]),
                         {"identical": [], "moved": [], "undecided": []})


class ChangedPixels(unittest.TestCase):
    """Where two captures differ is measured against the masks, not inferred."""

    def setUp(self):
        from PIL import Image
        self.dir = Path(tempfile.mkdtemp(prefix="w27f-g1-pixels-"))
        self.addCleanup(shutil.rmtree, self.dir, True)
        self.surface = {"nodeId": "body", "plane": "base", "radius": 4,
                        "bounds": {"x": 8, "y": 8, "width": 16, "height": 16}}
        self.distances = [g1.g0.distance(self.surface, (32, 32))]
        self.decidable = (self.distances[0] > 0)
        self.left = self.dir / "left.png"
        self.right = self.dir / "right.png"
        Image.new("RGB", (32, 32), (128, 128, 128)).save(self.left)
        self.Image = Image

    def test_a_change_outside_the_declared_shape_is_counted_outside_it(self):
        image = self.Image.new("RGB", (32, 32), (128, 128, 128))
        image.putpixel((1, 1), (129, 128, 128))
        image.save(self.right)
        result = g1.changed_pixels(self.left, self.right, [self.surface], self.distances,
                                   self.decidable)
        self.assertEqual(result["changedPixels"], 1)
        self.assertEqual(result["changedInsideDeclaredFootprint"], 0)
        self.assertEqual(result["changedOutsideEveryDeclaredShape"], 1)
        self.assertEqual(result["maxChannelDifference"], 1)

    def test_a_change_inside_the_interior_is_counted_inside_it(self):
        image = self.Image.new("RGB", (32, 32), (128, 128, 128))
        image.putpixel((16, 16), (160, 128, 128))
        image.save(self.right)
        result = g1.changed_pixels(self.left, self.right, [self.surface], self.distances,
                                   self.decidable)
        self.assertEqual(result["changedInsideDeclaredFootprint"], 1)
        self.assertEqual(result["changedOutsideEveryDeclaredShape"], 0)
        self.assertEqual(result["maxChannelDifference"], 32)

    def test_captures_of_different_sizes_are_reported_as_incomparable(self):
        self.Image.new("RGB", (16, 16), (128, 128, 128)).save(self.right)
        result = g1.changed_pixels(self.left, self.right, [self.surface], self.distances,
                                   self.decidable)
        self.assertFalse(result["comparable"])


class StackCoverage(unittest.TestCase):
    """A stack's composite is not covered by the sampled path's identity."""

    def test_a_stack_is_recognised_by_its_declared_planes(self):
        geometry = {"scenes": {
            "stacked": {"surfaces": [{"plane": "base"}, {"plane": "over"}]},
            "flat": {"surfaces": [{"plane": "base"}]},
            "siblings": {"surfaces": [{"plane": "base"}, {"plane": "base"}]},
        }}
        self.assertEqual(g1.stacked_scenes(geometry, ["stacked", "flat", "siblings"]), ["stacked"])

    def test_the_holdout_beds_declared_stacks_are_now_four_because_W27c_added_the_inactive_twins(
            self):
        """The G1 assertion this replaces pinned the list at two, and `scenes.json` moved.

        W27c G1 added `{checkerboard,photo}__glass-over-glass__inactive` to
        `split.holdout`, so the holdout bed's declared stacks are four at this
        head. The G1 test file still asserts two and fails here — a pre-existing
        breakage from a scene-set change, recorded rather than repaired in the
        frozen file. W27f G2 measures only the two `__rest` cells; the inactive
        pose has no web-side route in this runner and belongs to W27c.
        """
        spec = g1.scene_spec()
        geometry = g1.g0.declared_geometry()
        stacks = g1.stacked_scenes(geometry, g1.declared_scenes("holdout", spec))
        self.assertEqual(stacks, ["checkerboard__glass-over-glass__inactive",
                                  "checkerboard__glass-over-glass__rest",
                                  "photo__glass-over-glass__inactive",
                                  "photo__glass-over-glass__rest"])

    def test_the_two_cells_this_gate_measures_are_both_stacks(self):
        geometry = g1.g0.declared_geometry()
        measured = ["checkerboard__glass-over-glass__rest", "photo__glass-over-glass__rest"]
        self.assertEqual(g1.stacked_scenes(geometry, measured), measured)


class DeclaredSets(unittest.TestCase):
    """The scene sets come from the declared split, whole."""

    def test_the_holdout_phase_measures_the_whole_declared_holdout(self):
        spec = g1.scene_spec()
        self.assertEqual(g1.declared_scenes("holdout", spec), sorted(spec["split"]["holdout"]))

    def test_the_calibration_phases_measure_the_declared_calibration_set(self):
        spec = g1.scene_spec()
        for phase in ("baseline", "candidate"):
            self.assertEqual(g1.declared_scenes(phase, spec),
                             sorted(spec["split"]["calibration"]))


class SampledControl(unittest.TestCase):
    """G0's pixels are a control only when they can prove they are G0's pixels."""

    def setUp(self):
        self.out = Path(tempfile.mkdtemp(prefix="w27f-g1-control-"))
        self.addCleanup(shutil.rmtree, self.out, True)
        self.scheme = g1.SCHEMES["light"]
        self.scene = "checkerboard__glass-over-glass__rest"
        self.scratch = self.out / "g0"
        self.directory = self.scratch / self.scheme.profile / self.scene
        self.directory.mkdir(parents=True)
        self.png = self.directory / f"{self.scene}__webgpu.png"
        self.png.write_bytes(b"pretend-png")
        self.evidence = {self.scene: {"readings": {"sampledToday": {
            "sha256": g1.g0.digest(self.png)}}}}

    def test_a_snapshot_matching_the_recorded_digest_is_the_control(self):
        path, source = g1.sampled_control_image(self.out, "holdout", self.scheme, self.scene,
                                                self.scratch, self.evidence)
        self.assertEqual(path, self.png)
        self.assertIn("committed G0 evidence", source)

    def test_a_snapshot_that_does_not_match_is_not_used(self):
        self.png.write_bytes(b"some-other-capture")
        path, source = g1.sampled_control_image(self.out, "holdout", self.scheme, self.scene,
                                                self.scratch, self.evidence)
        self.assertIsNone(path)
        self.assertIsNone(source)

    def test_no_snapshot_and_no_sampled_arm_leaves_the_control_unknown(self):
        path, _ = g1.sampled_control_image(self.out, "holdout", g1.SCHEMES["dark"], self.scene,
                                           None, self.evidence)
        self.assertIsNone(path)


class PorcelainPaths(unittest.TestCase):
    """A dirty path is reported whole, whatever its status columns are.

    The G1 runner stripped the whole of `git status --porcelain` before taking
    each line at offset 3, so an entry whose status began with a space — every
    unstaged modification — lost its first path character when it was the first
    line. The tracker required this case before the runner was reused, and the
    first of these fails against the G1 parser.
    """

    def test_an_unstaged_first_entry_keeps_its_first_character(self):
        self.assertEqual(g1.porcelain_paths(" M packages/platform-web/src/optics.ts\n"),
                         ["packages/platform-web/src/optics.ts"])

    def test_a_staged_first_entry_is_unaffected(self):
        self.assertEqual(g1.porcelain_paths("M  packages/core/src/index.ts\n"),
                         ["packages/core/src/index.ts"])

    def test_every_entry_after_a_space_status_survives(self):
        self.assertEqual(
            g1.porcelain_paths(" M a/one.ts\n?? b/two.ts\n M c/three.ts\n"),
            ["a/one.ts", "b/two.ts", "c/three.ts"])

    def test_a_rename_reports_the_path_that_exists(self):
        self.assertEqual(g1.porcelain_paths("R  old/name.ts -> new/name.ts\n"),
                         ["new/name.ts"])

    def test_a_clean_tree_reports_nothing(self):
        self.assertEqual(g1.porcelain_paths(""), [])
        self.assertEqual(g1.porcelain_paths("\n"), [])


_ispec = importlib.util.spec_from_file_location(
    "w27f_g2_identity", Path(__file__).with_name("identity.py"))
identity = importlib.util.module_from_spec(_ispec)
_ispec.loader.exec_module(identity)


class AbsenceIsNotAgreement(unittest.TestCase):
    """The digest comparison must not read absence as a match.

    `compare` walks the *after* set, so every shape of missing data defaults to
    silence unless it is caught deliberately. Absence has two shapes and only one
    of them is benign: a scene the read never claimed is a scope decision — this
    gate reads two of the ten holdout scenes on purpose — while a scene the read
    claimed and did not deliver is a truncated capture. The second must stop.
    """

    def report(self, before, after):
        return identity.compare(before, after)["light"]

    def test_a_scene_the_read_never_claimed_is_a_scope_decision(self):
        out = self.report({"light": {"skipped": {"sampled": "a"}}}, {"light": {}})
        self.assertEqual(out["notRead"], {"skipped": ["sampled"]})
        self.assertEqual(out["truncated"], [])

    def test_a_scene_read_with_no_digest_on_any_arm_is_truncated(self):
        # The case the first version filed as `notRead`: the read claimed this
        # scene and produced nothing at all for it, which is indistinguishable
        # from a capture that died halfway if absence is read as scope.
        out = self.report({"light": {"s": {"sampled": "a", "css-today": "b"}}},
                          {"light": {"s": {"sampled": None, "css-today": None}}})
        self.assertEqual(out["notRead"], {})
        self.assertEqual([t["scene"] for t in out["truncated"]], ["s"])
        self.assertIsNone(out["truncated"][0]["arm"])

    def test_one_surviving_arm_still_names_the_arm_that_went_missing(self):
        out = self.report({"light": {"s": {"sampled": "a", "css-today": "b"}}},
                          {"light": {"s": {"sampled": "a", "css-today": None}}})
        self.assertEqual([t["arm"] for t in out["truncated"]], ["css-today"])
        self.assertEqual(out["arms"]["sampled"]["identical"], ["s"])

    def test_an_arm_the_record_has_and_the_read_lacks_is_truncated(self):
        out = self.report({"light": {"s": {"sampled": "a", "css-today": "b"}}},
                          {"light": {"s": {"sampled": "a"}}})
        self.assertEqual([t["arm"] for t in out["truncated"]], ["css-today"])

    def test_a_moved_digest_is_still_moved(self):
        out = self.report({"light": {"s": {"sampled": "a"}}},
                          {"light": {"s": {"sampled": "z"}}})
        self.assertEqual([m["scene"] for m in out["arms"]["sampled"]["moved"]], ["s"])
        self.assertEqual(out["truncated"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
