#!/usr/bin/env python3.12
"""W47 G0 (c): the referee loader under X69 (charter clause 4; G0 (c); Decision Log 1 as amended v1.1).

  frozen       `w46-referees-1` loads by its SHA-256 and holds W46's six scenes; a byte off refuses;
               W46's adapter, given W46's frozen ladder list, still reproduces it (the pin)
  not re-derived  W46's adapter given W47's ladders refuses the frozen file (the charter's v1.1 P1),
               which is why the loader never gives it W47's list
  membership   red: a manifest scene one dark profile does not declare
  disjoint     red: a W47 ladder naming a referee (the refusal names the ladder and the cell);
               W47's committed ladders/cells.json names none
  withholding  red: a referee row in a stage; red: a dark holdout row in a stage; a clean stage passes
  lists        the pre-gate whitelist excludes the referees; the exposure is the seven dark holdout
               scenes plus the six referees per scale (13)

    python3.12 -B -m unittest test_referees -v      (from this directory)
"""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import referees as R  # noqa: E402

SIX = ["checkerboard-8__rrect-sm__rest", "checkerboard-8__rrect-ml__rest",
       "checkerboard-4__rrect-md__inactive", "checkerboard-32__rrect-ml__rest",
       "checkerboard-32__rrect-lg__inactive", "hc-text-7__rrect-md__inactive"]
HOLDOUT = ["checkerboard__glass-over-glass__inactive", "checkerboard__glass-over-glass__rest",
           "mid-dark-solid__capsule-button__inactive", "mid-dark-solid__capsule-button__rest",
           "photo__glass-over-glass__inactive", "photo__rrect-lg__inactive", "photo__rrect-lg__rest"]


def row(profile, sid):
    return {"key": {"profileKey": profile, "sceneId": sid, "web": {"renderer": "webgpu"}}}


class Frozen(unittest.TestCase):
    def setUp(self):
        self.before = hashlib.sha256(R.MANIFEST.read_bytes()).hexdigest()

    def tearDown(self):
        self.assertEqual(hashlib.sha256(R.MANIFEST.read_bytes()).hexdigest(), self.before)

    def test_loaded_by_hash_with_w46s_six(self):
        m = R.load_manifest()
        self.assertEqual(m["sha256"], "0eb8ef7712adc0f7de53290190ab1b5d903d61806cc2039de0e99fb78de4c2cf")
        self.assertEqual(m["scenes"], SIX)
        self.assertEqual(m["profiles"], list(R.DARK_025))

    def test_a_byte_off_refuses(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "referees.json"
            path.write_bytes(R.MANIFEST.read_bytes() + b" ")
            with self.assertRaisesRegex(R.Refused, "loaded by hash"):
                R.load_manifest(path)

    def test_w46s_adapter_reproduces_it_from_w46s_frozen_ladders(self):
        self.assertEqual(R.pin_derivation()["scenes"], SIX)

    def test_w46s_adapter_given_w47s_ladders_refuses_the_frozen_file(self):
        w47 = {s for cells in R.load_ladder_cells().values() for s in cells}
        derived = R._plan.derive(R.load_scenes(), w47)
        coarse = next(d for d in derived if d["slot"] == "coarse rest")
        self.assertEqual(coarse["referee"], "checkerboard-32__rrect-sm__rest")
        with self.assertRaisesRegex(SystemExit, "is not what the rule produces"):
            R._plan.load_manifest(R.MANIFEST, None, w47)


class Membership(unittest.TestCase):
    def test_red_a_scene_one_dark_profile_does_not_declare(self):
        scenes = R.load_scenes()
        bad = copy.deepcopy(scenes)
        bad["declared"][R.DARK_025[1]] = [s for s in bad["declared"][R.DARK_025[1]]
                                          if s != "hc-text-7__rrect-md__inactive"]
        manifest = dict(path="w46-referees-1", sha256=R.MANIFEST_SHA, profiles=list(R.DARK_025), scenes=SIX)
        with self.assertRaisesRegex(R.Refused, r"hc-text-7__rrect-md__inactive.*not declared by "
                                    r"apple-macos-27.0-2x-dark.*membership"):
            R.check_membership(manifest, bad)
        R.check_membership(manifest, scenes)


class Disjoint(unittest.TestCase):
    def test_w47s_committed_ladders_name_no_referee(self):
        ladders = R.load_ladder_cells()
        R.check_disjoint(R.load_manifest(), ladders)
        self.assertFalse({s for c in ladders.values() for s in c} & set(SIX))

    def test_red_a_w47_ladder_naming_a_referee(self):
        body = json.loads(R.LADDER_CELLS.read_text())
        body["ladders"]["ii"]["rest"].append("checkerboard-32__rrect-ml__rest")
        body["union"] = sorted(set(body["union"]) | {"checkerboard-32__rrect-ml__rest"})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "cells.json"
            path.write_text(json.dumps(body))
            ladders = R.load_ladder_cells(path)
            with self.assertRaisesRegex(R.Refused, r"ladder \(ii\) checkerboard-32__rrect-ml__rest.*never "
                                        r"the manifest"):
                R.load_manifest(ladders=ladders)
        self.assertEqual(R.load_manifest()["scenes"], SIX)       # the manifest did not move


class Withholding(unittest.TestCase):
    def setUp(self):
        self.m = R.load_manifest()

    def test_red_a_referee_row_in_a_stage(self):
        rows = [row(R.DARK_025[0], "photo__rrect-md__rest"), row(R.DARK_025[1], "checkerboard-8__rrect-ml__rest")]
        with self.assertRaisesRegex(R.Refused, "2x-dark-standard-glass0.25/checkerboard-8__rrect-ml__rest"):
            R.assert_absent(rows, self.m, "stage")

    def test_red_a_dark_holdout_row_in_a_stage(self):
        rows = [row(R.DARK_025[0], "photo__rrect-lg__rest")]
        with self.assertRaisesRegex(R.Refused, "photo__rrect-lg__rest"):
            R.assert_absent(rows, self.m, "stage")

    def test_a_clean_stage_passes_and_check_stage_reads_it(self):
        rows = [row(p, "photo__rrect-md__rest") for p in R.DARK_025]
        R.assert_absent(rows, self.m, "stage")
        with tempfile.TemporaryDirectory() as tmp:
            good, bad = Path(tmp) / "good.json", Path(tmp) / "bad.json"
            good.write_text(json.dumps({"cells": rows}))
            bad.write_text(json.dumps({"cells": rows + [row(R.DARK_025[0], SIX[0])]}))
            self.assertEqual(R.check_stage(str(good)), 0)
            self.assertEqual(R.check_stage(str(bad)), 1)


class Lists(unittest.TestCase):
    def test_the_whitelists(self):
        scenes = R.load_scenes()
        out = R.lists()
        self.assertEqual(out["exposure"]["scenes"], sorted(HOLDOUT + SIX))
        self.assertFalse(set(out["pregateProbe"]["scenes"]) & set(SIX))
        self.assertEqual(R.withheld(R.load_manifest(), scenes), sorted(HOLDOUT + SIX))


if __name__ == "__main__":
    unittest.main()
