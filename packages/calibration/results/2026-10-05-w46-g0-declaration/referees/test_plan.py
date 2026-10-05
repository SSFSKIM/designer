#!/usr/bin/env python3.12
"""W46 G0 (b): the referee planner adapter, its rule and its refusals (charter clause 3; Design "The
referees"; Decision Log 2 as amended v1.1).

  rule       the adapter re-derives exactly the charter's six scenes from scenes.json and
             ladders/cells.json, and its slots' candidate lists are the rule's (span ascending,
             pitch descending, scene id; no tint; no ladder cell; both dark profiles declare it)
  refusals   a manifest the rule does not produce, a manifest naming a ladder cell, a light profile,
             W44's schema
  lists      the pre-gate whitelist excludes every referee and `compare`'s selection under it is the
             dark probe cells less the referees exactly; the exposure list is the dark canonical
             holdout (seven scenes) plus the referees exactly; scenes.json untouched
  counts     the fit-member counts per target and pose after the withholding, per scale, as the
             charter states them (P rest 4, P inactive 5, C rest 28, F inactive 2; beside them F rest
             10, T rest 3, C inactive 14, T inactive 0; 66 of 72 non-holdout T1 cells)

    python3.12 -B -m unittest test_plan -v      (from this directory)
"""
import hashlib
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import plan  # noqa: E402

CHARTER_SIX = ["checkerboard-8__rrect-sm__rest", "checkerboard-8__rrect-ml__rest",
               "checkerboard-4__rrect-md__inactive", "checkerboard-32__rrect-ml__rest",
               "checkerboard-32__rrect-lg__inactive", "hc-text-7__rrect-md__inactive"]
T1_BACKDROPS = {"F": ("checkerboard-4", "checkerboard-8"), "T": ("hc-text-7",),
                "C": ("checkerboard", "checkerboard-lc16", "checkerboard-32", "checkerboard-64", "hc-text",
                      "hc-text-28", "impulse"), "P": ("photo",)}


def manifest_file(tmp: Path, **change) -> Path:
    body = json.loads(plan.MANIFEST.read_text())
    body.update(change)
    path = tmp / "referees.json"
    path.write_text(json.dumps(body))
    return path


class Rule(unittest.TestCase):
    def setUp(self):
        self.scenes_before = hashlib.sha256(plan.SCENES_PATH.read_bytes()).hexdigest()
        self.scenes = plan.load_scenes()

    def tearDown(self):
        self.assertEqual(hashlib.sha256(plan.SCENES_PATH.read_bytes()).hexdigest(), self.scenes_before)

    def test_the_rule_produces_the_charters_six(self):
        self.assertEqual([d["referee"] for d in plan.derive(self.scenes)], CHARTER_SIX)
        self.assertEqual(plan.load_manifest()["scenes"], CHARTER_SIX)

    def test_the_slots_candidates(self):
        got = {d["slot"]: d["candidates"] for d in plan.derive(self.scenes)}
        self.assertEqual(got["thick fine rest"], ["checkerboard-8__rrect-ml__rest", "checkerboard-4__rrect-ml__rest",
                                                  "checkerboard-8__rrect-lg__rest", "checkerboard-4__rrect-lg__rest"])
        self.assertEqual(got["coarse rest"], ["checkerboard-32__rrect-ml__rest", "checkerboard-32__rrect-lg__rest"])
        # the exceptions the charter states: one thin fine rest candidate left once the ladders take
        # theirs, and the fine inactive slot lands on the mid-span pitch-4 cell
        self.assertEqual(got["thin fine rest"], ["checkerboard-8__rrect-sm__rest"])
        self.assertEqual(got["fine inactive"], ["checkerboard-4__rrect-md__inactive"])

    def test_no_referee_is_a_ladder_cell_and_without_the_ladders_the_rule_differs(self):
        ladder = plan.load_ladder_cells()
        self.assertFalse(set(CHARTER_SIX) & ladder)
        free = [d["referee"] for d in plan.derive(self.scenes, ladder=set())]
        self.assertNotEqual(free, CHARTER_SIX)     # the ladders' cells are what moves two slots

    def test_tinted_scenes_are_never_candidates(self):
        for d in plan.derive(self.scenes):
            for sid in d["candidates"]:
                self.assertNotIn("tint", self.scenes["by_id"][sid])


class Refusals(unittest.TestCase):
    def refused(self, needle, **change):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(plan.Refused) as caught:
                plan.load_manifest(manifest_file(Path(tmp), **change))
            self.assertIn(needle, str(caught.exception))

    def test_a_manifest_the_rule_does_not_produce(self):
        self.refused("is not what the rule produces",
                     scenes=CHARTER_SIX[:1] + ["checkerboard-4__rrect-ml__rest"] + CHARTER_SIX[2:])
        self.refused("is not what the rule produces", scenes=list(reversed(CHARTER_SIX)))
        self.refused("is not what the rule produces", scenes=CHARTER_SIX[:5])

    def test_a_ladder_cell(self):
        self.refused("ladder cells", scenes=CHARTER_SIX[:2] + ["checkerboard-8__rrect-md__inactive"] + CHARTER_SIX[3:])

    def test_a_light_profile(self):
        self.refused("not the two dark", profiles=["apple-macos-27.0-1x-light-standard-glass0.25",
                                                   "apple-macos-27.0-2x-light-standard-glass0.25"])
        self.refused("not the two dark", profiles=["apple-macos-27.0-2x-dark-standard-glass0.25"])

    def test_w44s_schema(self):
        self.refused("w44-referees-1", schema="w44-referees-1")

    def test_a_non_probe_scene(self):
        self.refused("a referee is a probe scene", scenes=CHARTER_SIX[:5] + ["photo__rrect-lg__rest"])


class Lists(unittest.TestCase):
    def setUp(self):
        self.scenes = plan.load_scenes()
        self.m = plan.load_manifest(scenes=self.scenes)
        self.lists = plan.lists(self.m, self.scenes)

    def test_pregate_excludes_every_referee(self):
        pre = set(self.lists["pregateProbe"]["scenes"])
        selected = plan.compare_selects(self.scenes, self.m["profiles"], ("probe",), pre)
        probe_cells = {(p, s) for p in self.m["profiles"] for s in self.scenes["declared"][p]
                       if self.scenes["role"][s] == "probe"}
        self.assertEqual(selected, probe_cells - plan.referee_cells(self.m))

    def test_exposure_is_the_dark_holdout_and_the_referees_exactly(self):
        exp = set(self.lists["exposure"]["scenes"])
        selected = plan.compare_selects(self.scenes, self.m["profiles"], ("holdout", "probe"), exp)
        holdout_cells = {(p, s) for p in self.m["profiles"] for s in self.scenes["declared"][p]
                         if self.scenes["role"][s] == "holdout"}
        self.assertEqual(selected, holdout_cells | plan.referee_cells(self.m))
        self.assertEqual(len({s for s in exp if self.scenes["role"][s] == "holdout"}), 7)

    def test_counts(self):
        self.assertEqual(self.lists["exposure"]["count"], 13)
        self.assertEqual(self.lists["pregateProbe"]["count"], 81)

    def test_check_stage(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.json"
            path.write_text(json.dumps({"cells": [{"key": {"profileKey": plan.DARK_025[0],
                                                           "sceneId": CHARTER_SIX[0]}}]}))
            self.assertEqual(plan.check_stage(str(path)), 1)
            path.write_text(json.dumps({"cells": []}))
            self.assertEqual(plan.check_stage(str(path)), 0)


class FitMembers(unittest.TestCase):
    """The members that remain to fit, per scale (Design "The referees", "What remains to fit")."""

    def test_the_charters_counts(self):
        scenes = plan.load_scenes()
        held = set(plan.load_manifest(scenes=scenes)["scenes"])
        for profile in plan.DARK_025:
            got = Counter()
            for sid in scenes["declared"][profile]:
                bg = scenes["by_id"][sid]["background"]
                stratum = next((k for k, v in T1_BACKDROPS.items() if bg in v), None)
                if stratum is None or scenes["role"][sid] == "holdout" or sid in held:
                    continue
                got[f"{stratum} {plan.pose(scenes, sid)}"] += 1
            self.assertEqual(dict(got), {"P rest": 4, "P inactive": 5, "C rest": 28, "F inactive": 2,
                                         "F rest": 10, "T rest": 3, "C inactive": 14}, profile)
            self.assertEqual(sum(got.values()), 66)


if __name__ == "__main__":
    unittest.main()
