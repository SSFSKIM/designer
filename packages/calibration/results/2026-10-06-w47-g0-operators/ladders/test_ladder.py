#!/usr/bin/env python3.12
"""W47 G0 (c), (g): the ladder runner and reader without a render (charter clause 5; Design "The
ladders"; X60, X66, X67, X68, X69, X70).

  X70        red: a requested cell no dark profile declares (`hc-text__rrect-md__rest`, v1's cell) refuses
             before rendering; red: a cell `compare` would not plan (a probe cell under a set list without
             `probe`) refuses before rendering; red: a rung matrix missing one declared row refuses the rung
             at read; green: every protocol rung's planned set equals its requested set at both scales, and
             a complete synthetic rung reads
  X69        no rung renders a referee or a holdout cell (`admitted`); W46's checks kept
  protocol   pins the committed cells.json; 41 rungs as Design "The ladders" lists them; every override
             a snapshot leaf or ADMITTED on a dark slot, inside DOMAINS (X67, X68), operator 2 receded only
             (X66), no light slot (X60); ladder (ii) never names `sizeHeavySecondSigma` or the 1x top;
             ladder (iv) carries point A's receded scatter exactly as W46 G1's committed candidate moves it
  phases     a dependent rung refuses until its selection is recorded, then resolves; a rung needing an
             operator this runtime lacks is WAITING with its reason
  bars       clause 5's four bars on synthetic readings, and the two selections
  part2      the decisions on synthetic results: a separating operator fitted, a non-separating one named
             and its leaves struck, body width first, the 1x gap named, tintAlpha narrowed, stop

    python3.12 -B -m unittest test_ladder -v      (from this directory)
"""
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ladder as L  # noqa: E402
import part2 as P2  # noqa: E402
import read as R  # noqa: E402

W = L.W
REF = W.referees()
SCENES = REF.load_scenes()
PROTO = L.protocol()
SETS = PROTO["sets"]


def row(profile, sid):
    return {"key": {"profileKey": profile, "sceneId": sid, "web": {"renderer": "webgpu"}}}


def rd(n, c, k, scale=1, bar=0.5 / 255, code=1 / 255):
    """A synthetic per-cell reading in read.reading's shape."""
    return dict(scale=scale, native=n, control=c, web=k, ratio=k / n, controlRatio=c / n, delta=k - c, bar=bar,
                B=max(code, 2 * bar), moved=abs(k - c) > bar, g=abs(k - n) - abs(c - n))


class X70(unittest.TestCase):
    def test_every_protocol_rung_plans_exactly_what_it_requests(self):
        for r in L.rungs(PROTO):
            got = L.x70_plan(r["label"], r["cells"], SETS, SCENES)
            for scale in (1, 2):
                self.assertEqual(got[scale], {(W.PROFILE[scale], s) for s in r["cells"]})
            L.admitted(r["cells"], SETS)

    def test_red_a_requested_cell_no_dark_profile_declares(self):
        cells = ["photo__rrect-md__rest", "hc-text__rrect-md__rest"]
        with self.assertRaisesRegex(W.Refusal, r"X70 REFUSES before rendering.*not planned \['hc-text__rrect-md__rest'\]"):
            L.x70_plan("red", cells, SETS, SCENES)
        with self.assertRaisesRegex(W.Refusal, "hc-text__rrect-md__rest is a holdout scene"):
            L.admitted(cells, SETS)

    def test_red_a_cell_compare_would_not_plan(self):
        cells = ["photo__rrect-md__rest", "checkerboard-8__rrect-lg__rest"]       # the second is a probe scene
        self.assertEqual(SCENES["role"]["checkerboard-8__rrect-lg__rest"], "probe")
        with self.assertRaisesRegex(W.Refusal, r"X70 REFUSES before rendering.*checkerboard-8__rrect-lg__rest"):
            L.x70_plan("red", cells, "calibration,validation", SCENES)
        L.x70_plan("green", cells, SETS, SCENES)

    def test_red_a_rung_matrix_missing_one_declared_row(self):
        cells = sorted(json.loads(W.LADDER_CELLS.read_text())["ladders"]["iii"]["inactive"])
        rows = {(W.PROFILE[s], sid): row(W.PROFILE[s], sid) for s in (1, 2) for sid in cells}
        R.x70_read("green", rows, cells, SETS, SCENES)
        short = dict(rows)
        del short[(W.PROFILE[2], "photo__rrect-ml__inactive")]
        with self.assertRaisesRegex(W.Refusal, r"2x: X70 REFUSES the rung.*1 missing \['photo__rrect-ml__inactive'\]"):
            R.x70_read("red", short, cells, SETS, SCENES)
        extra = dict(rows)
        extra[(W.PROFILE[1], "photo__rrect-md__rest")] = row(W.PROFILE[1], "photo__rrect-md__rest")
        with self.assertRaisesRegex(W.Refusal, r"1x: X70 REFUSES the rung.*1 extra"):
            R.x70_read("red", extra, cells, SETS, SCENES)

    def test_x69_no_rung_names_a_withheld_cell(self):
        manifest = REF.load_manifest()
        for sid in manifest["scenes"] + ["photo__rrect-lg__rest"]:
            with self.assertRaisesRegex(W.Refusal, "a referee|a holdout scene"):
                L.admitted(["photo__rrect-md__rest", sid], SETS)


class Protocol(unittest.TestCase):
    def test_pins_the_committed_cells_and_lists_the_designs_rungs(self):
        self.assertEqual(PROTO["cells"]["sha256"], W.file_sha(W.LADDER_CELLS))
        rs = L.rungs(PROTO)
        by = {lad: [r["label"] for r in rs if r["ladder"] == lad] for lad in ("i", "ii", "iii", "iv")}
        self.assertEqual(len(rs), 41)
        self.assertEqual([len(by[k]) for k in ("i", "ii", "iii", "iv")], [16, 12, 11, 1])
        self.assertEqual(by["iii"][:3], ["iii-b2", "iii-b3", "iii-b4"])            # the body width first

    def test_every_override_is_admitted_and_inside_its_domain(self):
        for r in L.rungs(PROTO):
            for slot, leaves in r["overrides"].items():
                self.assertIn(slot, W.MOVING_SLOTS, r["label"])
                for key, value in leaves.items():
                    self.assertTrue(L.snapshot_leaf(slot, key) is not None or key in W.ADMITTED[slot], (r["label"], key))
                    if not isinstance(value, dict):
                        self.assertTrue(W.in_domain(slot, key, value), (r["label"], key, value))
                if slot == "active.dark":
                    self.assertFalse(set(leaves) & set(W.OPERATOR_2), r["label"])
        bad = copy.deepcopy(PROTO)
        bad["ladders"][0]["rungs"][1]["overrides"]["active.dark"]["tintAlphaFar2x"] = 0.7
        with self.assertRaisesRegex(W.Refusal, "outside its declared domain"):
            L.rungs(bad)
        bad = copy.deepcopy(PROTO)
        bad["ladders"][0]["rungs"][0]["overrides"]["active.dark"]["sizeFineTapShare"] = 0.5
        with self.assertRaisesRegex(W.Refusal, "neither a snapshot leaf nor admitted"):
            L.rungs(bad)
        bad = copy.deepcopy(PROTO)
        bad["ladders"][0]["rungs"][0]["overrides"]["active.light"] = {"optics.regular.tintAlpha": 0.8}
        with self.assertRaisesRegex(W.Refusal, "X60"):
            L.rungs(bad)

    def test_ladder_ii_holds_the_1x_width_and_the_1x_top(self):
        for r in L.rungs(PROTO):
            if r["ladder"] == "ii":
                a = r["overrides"]["active.dark"]
                self.assertNotIn("sizeHeavySecondSigma", a)
                self.assertNotIn("sizeScatterSpanMax", a)
                self.assertEqual(a["sizeHeavySecondShare"], 0.05)
                self.assertEqual(r["actsAt"], "2x")
        self.assertEqual(L.snapshot_leaf("active.dark", "sizeHeavySecondSigma"), 0)

    def test_ladder_iv_is_point_as_receded_scatter(self):
        a = PROTO["pointA"]
        spec = json.loads((W.ROOT / a["candidate"]["path"]).with_name("spec.json").read_text())
        self.assertEqual(W.file_sha(W.ROOT / a["candidate"]["path"]), a["candidate"]["sha256"])
        receded_doc = json.loads((W.ROOT / a["recededDocument"]["path"]).read_text())
        self.assertEqual(receded_doc["resolvedMaterialSha256"], "1a2c804a11e632ba")
        moved = {}
        for key, value in spec["overrides"]["receded.dark"].items():
            snap = L.snapshot_leaf("receded.dark", key)
            start = snap if snap is not None else W.ADMITTED["receded.dark"].get(key)
            if value != start:
                moved[key] = value
        self.assertEqual(moved, a["recededScatter"])
        self.assertEqual(moved, {"optics.regular.tintAlpha": 0.8, "sizeScatterRampStartThin1x": 0.4,
                                 "sizeScatterRampStartThin2x": 0.4, "sizeScatterFloor": 0.5,
                                 "sizeScatterRampStartThick1x": 0.15, "sizeScatterScaleGain": 0})
        iv = next(r for r in L.rungs(PROTO) if r["label"] == "iv-joint")
        self.assertEqual(iv["overrides"]["receded.dark"], a["recededScatter"])


class Phases(unittest.TestCase):
    def test_a_dependent_rung_waits_for_its_selection(self):
        rs = {r["label"]: r for r in L.rungs(PROTO, chosen={}, resolve=True)}
        self.assertIn("iii-width-1x", rs["iii-q0.5"]["unresolved"])
        self.assertIn("iii-best", rs["iv-joint"]["unresolved"])
        chosen = {"iii-width-1x": {"value": 3}, "iii-width-2x": {"value": 2},
                  "iii-best": {"overrides": {"receded.dark": {"sizeFineTapShare": 0.5, "sizeFineTapSigma": 3,
                                                               "sizeFineTapSigma2x": 2}}}}
        rs = {r["label"]: r for r in L.rungs(PROTO, chosen=chosen, resolve=True)}
        self.assertEqual(rs["iii-q0.5"]["overrides"]["receded.dark"],
                         {"sizeFineTapShare": 0.5, "sizeFineTapSigma": 3, "sizeFineTapSigma2x": 2})
        self.assertEqual(rs["iv-joint"]["overrides"]["receded.dark"]["sizeFineTapSigma"], 3)
        self.assertEqual(rs["iv-joint"]["overrides"]["receded.dark"]["optics.regular.tintAlpha"], 0.8)
        none = {"iii-width-1x": {"value": None, "why": "no width rung holds the guards at 1x"}, "iii-width-2x": {"value": 2}}
        rs = {r["label"]: r for r in L.rungs(PROTO, chosen=none, resolve=True)}
        self.assertIn("found no admissible value", rs["iii-q0.5"]["inapplicable"])     # read, and nothing admissible
        self.assertNotIn("unresolved", rs["iii-q0.5"])

    def test_operator_rungs_wait_for_the_runtime(self):
        rs = {r["label"]: r for r in L.rungs(PROTO)}
        without = "export const DEFAULT_MATERIAL_PROFILE = {\n  tintAlpha: 0.9,\n};\n"
        self.assertIn("WAITING", L.waiting(rs["i-a0.7-f0.2"], without))
        self.assertIn("tintAlphaFar1x", L.waiting(rs["i-a0.7-f0.2"], without))
        self.assertIn("sizeFineTapShare", L.waiting(rs["iii-s2"], without))
        self.assertIsNone(L.waiting(rs["i-a0.7-g0.4"], without))
        self.assertIsNone(L.waiting(rs["ii-w6-d0.3-t128"], without))
        withop = without + "  tintAlphaFar1x: 0,\n  tintAlphaFar2x: 0,\n"
        self.assertIsNone(L.waiting(rs["i-a0.7-f0.2"], withop))
        state = {lab: L.waiting(r) for lab, r in rs.items()}
        waiting = sorted(lab for lab, why in state.items() if why)
        print(f"\n  WAITING on this runtime: {len(waiting)} rungs: {', '.join(waiting)}", file=sys.stderr)


class Bars(unittest.TestCase):
    def test_i(self):
        pa = {(s, "thin-a"): dict(native=0.10, reference=0.04, candidate=0.09) for s in (1, 2)}
        thick = ["thick-a"]
        good = {(s, "thick-a"): rd(0.05, 0.10, 0.1035, s) for s in (1, 2)}
        good.update({(s, "thin-a"): rd(0.10, 0.04, 0.07, s) for s in (1, 2)})       # gain 0.03 >= half of 0.05
        b = R.bar_i(good, thick, ["thin-a"], pa, True)
        self.assertTrue(b["meets"])
        self.assertFalse(R.bar_i(good, thick, ["thin-a"], pa, False)["meets"])     # L1 fails
        far = {**good, (2, "thick-a"): rd(0.05, 0.10, 0.11, 2)}               # 2.55 B off the reference
        self.assertEqual(R.bar_i(far, thick, ["thin-a"], pa, True)["meetsAt"], [1])
        weak = {**good, (1, "thin-a"): rd(0.10, 0.04, 0.05, 1)}               # gain 0.01 < 0.025
        self.assertFalse(R.bar_i(weak, thick, ["thin-a"], pa, True)["perScale"][1]["thinKeepsHalf"])

    def test_ii(self):
        cells = {(2, "checkerboard-8__rrect-lg__rest"): rd(0.05, 0.09, 0.07, 2),
                 (2, "hc-text__rrect-lg__rest"): rd(0.05, 0.08, 0.06, 2),
                 (2, "checkerboard-64__rrect-lg__rest"): rd(0.10, 0.05, 0.0495, 2)}
        self.assertTrue(R.bar_ii(cells, [])["meets"])
        self.assertFalse(R.bar_ii(cells, ["1x capture moved"])["meets"])
        drop = {**cells, (2, "checkerboard-64__rrect-lg__rest"): rd(0.10, 0.05, 0.04, 2)}
        self.assertFalse(R.bar_ii(drop, [])["meets"])
        flat = {**cells, (2, "hc-text__rrect-lg__rest"): rd(0.05, 0.08, 0.0799, 2)}
        self.assertFalse(R.bar_ii(flat, [])["meets"])

    def test_iii_and_the_selections(self):
        def cells(fall_codes, guard_web=0.05):
            out = {}
            for s in (1, 2):
                for sid in R.FINE:
                    out[(s, sid)] = rd(0.01, 0.03, 0.03 - fall_codes / 255, s)
                out[(s, R.GUARD[0])] = rd(0.10, 0.05, guard_web, s)
                out[(s, R.GUARD[1])] = rd(0.10, 0.04, 0.04, s)
            return out
        self.assertTrue(R.bar_iii(cells(3.5))["meets"])
        self.assertFalse(R.bar_iii(cells(2.5))["meets"])
        self.assertFalse(R.bar_iii(cells(3.5, guard_web=0.05 - 1.5 / 255))["meets"])
        widths = {1.5: R.bar_iii(cells(1)), 2: R.bar_iii(cells(4)), 3: R.bar_iii(cells(4.05)),
                  6: R.bar_iii(cells(5, guard_web=0.05 - 2 / 255))}
        self.assertEqual(R.select_width(widths, 1)["value"], 2)           # 3 ties within 0.1 B; 6 breaks a guard
        self.assertIsNone(R.select_width({6: widths[6]}, 2)["value"])
        tap = {"iii-s2": ({"sizeFineTapShare": 1, "sizeFineTapSigma": 2, "sizeFineTapSigma2x": 2}, widths[2]),
               "iii-q0.5": ({"sizeFineTapShare": 0.5, "sizeFineTapSigma": 2, "sizeFineTapSigma2x": 2}, R.bar_iii(cells(4)))}
        body = {"iii-b3": ({"optics.regular.blurSigma": 3}, R.bar_iii(cells(6)))}
        best = R.select_best(tap, body)
        self.assertEqual((best["label"], best["form"]), ("iii-q0.5", "operator 2"))
        best = R.select_best({"iii-s6": ({"sizeFineTapShare": 1, "sizeFineTapSigma": 6}, widths[6])}, body)
        self.assertEqual(best["label"], "iii-b3")
        self.assertIn("body width", best["form"])

    def test_iv(self):
        pa = {(s, "photo__rrect-md__inactive"): dict(ratio=r) for s, r in ((1, 0.417), (2, 0.460))}
        cells = {}
        for s in (1, 2):
            for sid in R.FINE:
                cells[(s, sid)] = rd(0.01, 0.03, 0.01 + 1.5 / 255, s)
            cells[(s, "photo__rrect-md__inactive")] = rd(0.10, 0.03, 0.044, s)
        b = R.bar_iv(cells, pa)
        self.assertEqual(b["meetsAt"], [1])                               # 0.44 >= 0.417 at 1x, < 0.460 at 2x
        self.assertTrue(R.point_a(PROTO)[(1, "photo__rrect-md__inactive")]["ratio"] > 0.41)


class NoAdmissibleWidth(unittest.TestCase):
    """The reviewer's scenario (reviewer-medium, W47 G0): every tap-width rung of ladder (iii) fails a guard
    at 2x, so `iii-width-2x` is read with no admissible value and the share rungs cannot be built. They are
    INAPPLICABLE, not pending: ladder (iii) completes without them, `iii-best` falls to the body width (or to
    none), ladder (iv) resolves from it, and part 2's declared decision proceeds — body-width-first where a
    body-width rung met its bar, the tap named unfitted where none did."""

    @staticmethod
    def cells(fall_codes, guard_drop_2x=0.0, guard_drop_1x=0.0):
        out = {}
        for s, drop in ((1, guard_drop_1x), (2, guard_drop_2x)):
            for sid in R.FINE:
                out[(s, sid)] = rd(0.01, 0.03, 0.03 - fall_codes / 255, s)
            out[(s, R.GUARD[0])] = rd(0.10, 0.05, 0.05 - drop / 255, s)
            out[(s, R.GUARD[1])] = rd(0.10, 0.04, 0.04, s)
        return out

    def read(self, body_meets, op1):
        flat = dict(meets=False, meetsAt=[])
        per = {}

        def entry(r, bar, **extra):
            per[r["label"]] = dict(ladder=r["ladder"], overrides=r["overrides"], cells={}, bar=bar, **extra)

        rungs = L.rungs(PROTO, chosen={}, resolve=True)
        for r in rungs[1:]:
            if r["ladder"] == "i":
                entry(r, dict(meets=op1, meetsAt=[1, 2] if op1 else []), level=dict(L1passes=True))
            elif r["ladder"] == "ii":
                entry(r, flat)
            elif r["label"].startswith("iii-s"):                     # every width breaks a 2x guard (and,
                entry(r, R.bar_iii(self.cells(1, guard_drop_2x=2)))  # under 3 B at 1x, meets at no scale)
            elif r["label"].startswith("iii-b"):
                entry(r, R.bar_iii(self.cells(3.5 if body_meets and r["label"] == "iii-b3" else 1)))
        ladders, chosen, ops = R.summarise(PROTO, rungs, per, {})
        self.assertIsNone(chosen["iii-width-2x"]["value"])
        self.assertIsNotNone(chosen["iii-width-1x"]["value"])
        self.assertFalse(ladders["iii"]["complete"])                 # the share rungs are not yet resolved

        rungs = L.rungs(PROTO, chosen=chosen, resolve=True)
        inapplicable = {r["label"]: r["inapplicable"] for r in rungs if r.get("inapplicable")}
        self.assertEqual(sorted(inapplicable), ["iii-q0.25", "iii-q0.5", "iii-q0.75"])
        ladders, chosen2, ops = R.summarise(PROTO, rungs, per, inapplicable)
        self.assertTrue(ladders["iii"]["complete"])
        self.assertEqual(ladders["iii"]["inapplicable"], ["iii-q0.25", "iii-q0.5", "iii-q0.75"])
        best = chosen2["iii-best"]
        self.assertTrue(best["label"].startswith("iii-b"), best)       # no tap rung holds both scales' guards
        self.assertIn("body width", best["form"])

        rungs = L.rungs(PROTO, chosen={**chosen, **chosen2}, resolve=True)
        joint = next(r for r in rungs if r["label"] == "iv-joint")
        self.assertNotIn("unresolved", joint)
        self.assertEqual(joint["overrides"]["receded.dark"]["optics.regular.blurSigma"],
                         best["overrides"]["receded.dark"]["optics.regular.blurSigma"])
        entry(joint, flat)
        ladders, _, ops = R.summarise(PROTO, rungs, per, inapplicable)
        self.assertTrue(all(v["complete"] for v in ladders.values()), ladders)
        return dict(rungs=per, ladders={k: dict(v, passingL1=v.get("passingL1")) for k, v in ladders.items()},
                    operators=ops)

    def test_body_width_first_proceeds(self):
        results = self.read(body_meets=True, op1=False)
        self.assertEqual(results["operators"]["operator 2"]["bodyRungs"], ["iii-b3"])
        got = P2.changes_from(Part2.DRAFT, results, {})
        self.assertIn(("body-width-first", "operator 2"), Part2.kinds(None, got))

    def test_the_tap_is_named_unfitted(self):
        results = self.read(body_meets=False, op1=True)
        self.assertFalse(results["operators"]["operator 2"]["separates"])
        self.assertFalse(results["operators"]["operator 2"]["bodyWidthMeets"])
        got = P2.changes_from(Part2.DRAFT, results, {})
        self.assertIn(("name-unfitted", "operator 2"), Part2.kinds(None, got))


class Part2(unittest.TestCase):
    DRAFT = {"moves": [{"id": "stage1", "families": {
        "span": {"leaves": {"optics.regular.tintAlpha": {"grid": [0.9, 0.8, 0.7], "ladder": "i", "operator": None},
                            "tintAlphaFar1x": {"grid": [0, 0.2], "operator": "operator 1"}}}}},
        {"id": "stage2", "families": {"fine": {"leaves": {
            "sizeFineTapSigma": {"grid": [1.5, 2], "operator": "operator 2"},
            "optics.regular.blurSigma": {"grid": [1.25, 2], "operator": None}}}}}]}

    def results(self, op1=True, op2=True, body=False, ii=False, passing=("i-a0.7",)):
        lad = dict(complete=True, read=["x"], notRead=[], meetsAtOneScaleOnly=[])
        return dict(rungs={}, ladders={"i": dict(lad, passingL1=list(passing)), "iii": dict(lad, passingL1=None),
                                       "ii": dict(lad, passingL1=None), "iv": dict(lad, passingL1=None)},
                    operators={"operator 1": dict(separates=op1, oneScaleOnly=[]), "2x width": dict(meets=ii, rungs=["ii-x"]),
                               "operator 2": dict(separates=op2, bodyWidthMeets=body, bodyRungs=["iii-b3"] if body else [],
                                                  oneScaleOnly=[]), "joint": dict(meets=False)})

    def kinds(self, changes):
        return sorted((c["kind"], c.get("operator") or c.get("leaf") or "") for c in changes)

    def test_both_separate_narrows_tintalpha_only(self):
        got = P2.changes_from(self.DRAFT, self.results(), {})
        self.assertEqual(self.kinds(got), [("narrow", "optics.regular.tintAlpha")])
        self.assertEqual(got[0]["grid"], [0.9, 0.7])

    def test_operator_1_unfitted_and_the_1x_gap(self):
        """The name-unfitted change itself removes operator 1's leaves (declare.py `apply_changes`), so no
        separate strike is listed for them."""
        got = P2.changes_from(self.DRAFT, self.results(op1=False, ii=True), {})
        self.assertIn(("name-unfitted", "operator 1"), self.kinds(got))
        self.assertNotIn(("strike", "tintAlphaFar1x"), self.kinds(got))
        self.assertIn(("name-1x-gap", ""), self.kinds(got))
        self.assertEqual(next(c for c in got if c["kind"] == "name-1x-gap")["ladder"], "ii")

    def test_body_width_first(self):
        got = P2.changes_from(self.DRAFT, self.results(op2=True, body=True), {})
        self.assertIn(("body-width-first", "operator 2"), self.kinds(got))
        self.assertNotIn(("strike", "sizeFineTapSigma"), self.kinds(got))
        self.assertNotIn(("strike", "optics.regular.blurSigma"), self.kinds(got))

    def test_a_ladder_ii_conditional_leaf_is_struck_when_ladder_ii_did_not_meet_its_bar(self):
        draft = {"moves": [{"id": "stage1", "families": {"tap": {"leaves": {
            "sizeHeavySecondShareFar2x": {"grid": [0.3, 0.6], "ladder": "ii", "conditional": "ii"}}}}}]}
        got = P2.changes_from(draft, self.results(ii=False), {})
        self.assertEqual([(c["kind"], c["leaf"], c["ladder"]) for c in got],
                         [("strike", "sizeHeavySecondShareFar2x", "ii")])
        self.assertEqual(P2.changes_from(draft, self.results(ii=True), {})[0]["kind"], "name-1x-gap")

    def test_stop_incomplete_and_one_scale(self):
        with self.assertRaisesRegex(SystemExit, "neither operator separates"):
            P2.changes_from(self.DRAFT, self.results(op1=False, op2=False), {})
        r = self.results()
        r["ladders"]["iii"]["complete"] = False
        with self.assertRaisesRegex(SystemExit, "incomplete"):
            P2.changes_from(self.DRAFT, r, {})
        r = self.results()
        r["operators"]["operator 1"]["oneScaleOnly"] = ["i-a0.7-f0.2"]
        with self.assertRaisesRegex(SystemExit, "one scale only"):
            P2.changes_from(self.DRAFT, r, {})


if __name__ == "__main__":
    unittest.main()
