"""W48 G0 (b): W47's stage tests, run under W48's bindings with `stage.py` loaded through `inherit.tool`
(so `SEALED_BY` is W48's, `inherit.REBIND`), and the shipped documents' stage re-proven WITHOUT a render
(charter clause 2: "the stage of the shipped documents reproduces the published rows"; X62, X69).

Two W47 cases assert W47's bindings and are W48's here: the stages are `~/vitrea-w48`'s, and a G1 stage
reads only documents sealed by W48 G1 (W47 G1's are refused like W45's and W46's). The rest of W47's module
runs unchanged.

**The stage of the shipped documents, without a render.** W47 G0 rendered it once
(`results/2026-10-06-w47-g0-operators/stage/rehearsal/`): verdict REPRODUCED, 132 of 132 rows equal to the
published `d0219cd684bf` rows but for `capturedAt`, 264 of 264 captures byte-identical to the canonical
tree, on the shipped documents' bytes. W48 renders nothing, so it re-proves that the record still
applies: (1) the record says so; (2) the documents it staged are the bytes the live profiles hold now and
W48's snapshots hold; (3) the cells W48's stage tool plans for the shipped documents (`passes
("rehearse-measure", profile)`, W47's `stage.py` under W48's bindings) are, pass by pass, exactly the
`--scene` lists W47's rehearsal launched (read from its committed launch logs), 66 per profile; and (4)
every planned cell has its published row in `d0219cd684bf`. A rehearsal render under W48's bindings is
refused outright: its evidence directory is W47's (`stage.REHEARSAL`), which W48's refusals cover.

    python3.12 -B -m unittest -v test_stage      (from this directory)
"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import inherited_suite as S  # noqa: E402

W = S.W
stage = S.inherit.tool("stage/stage.py")          # registered as `stage`, SEALED_BY re-bound (REBIND)
T = S.module("stage/test_stage.py")
REHEARSAL = W.W47_G0 / "stage" / "rehearsal"
REPLACED = {"Stage.test_the_stages_are_w47s_and_dark": "the stages are W48's",
            "Stage.test_g1_refuses_the_shipped_documents_and_unhashed_parts": "the sealed bytes are W48 G1's"}


class W48Stage(unittest.TestCase):
    def test_the_w47_module_reads_the_rebound_stage(self):
        self.assertIs(T.stage, stage)
        self.assertEqual(stage.SEALED_BY, "W48 G1")

    def test_the_stages_are_w48s_and_dark(self):
        for name, mode in stage.MODES.items():
            W.refuse_other_wave_path(mode["stage"], "stage")
            self.assertIn("vitrea-w48", str(mode["stage"]))
        W.refuse_other_wave_path(stage.MODES["g1"]["out"], "evidence")
        self.assertEqual(stage.MODES["g1"]["out"], W.G1_STAGE)
        with self.assertRaisesRegex(W.Refusal, "clause 2"):           # the rehearsal's evidence is W47's dir
            W.refuse_other_wave_path(stage.MODES["rehearsal"]["out"], "evidence")
        self.assertEqual(stage.PROFILES, list(W.DARK_025))
        self.assertIn("-dark-", stage.ACTIVE)
        self.assertIn("-dark-", stage.RECEDED)

    def test_g1_reads_only_documents_sealed_by_w48_g1(self):
        shipped = {k: dict(v, snapshot=True, recordedBy="W43 G3") for k, v in stage.documents_state().items()}

        def unhashed(part):
            raise W.Refusal("unhashed")
        with mock.patch.object(W, "require_part", unhashed), self.assertRaises(W.Refusal):
            stage.require_sealed()
        with mock.patch.object(W, "require_part", lambda part: "x"), \
                mock.patch.object(stage, "documents_state", lambda: shipped), \
                self.assertRaisesRegex(W.Refusal, "not sealed by W48 G1"):
            stage.require_sealed()
        sealed = {k: dict(v, snapshot=False, recordedBy="W48 G1") for k, v in stage.documents_state().items()}
        with mock.patch.object(W, "require_part", lambda part: "x"), \
                mock.patch.object(stage, "documents_state", lambda: sealed):
            stage.require_sealed()
        for other in ("W45 G1", "W46 G1", "W47 G1"):
            wrong = {k: dict(v, snapshot=False, recordedBy=other) for k, v in stage.documents_state().items()}
            with mock.patch.object(W, "require_part", lambda part: "x"), \
                    mock.patch.object(stage, "documents_state", lambda: wrong), \
                    self.assertRaisesRegex(W.Refusal, "not sealed by W48 G1"):
                stage.require_sealed()


def launched(profile: str) -> dict[str, list[str]]:
    """{pass: the --scene list} W47's rehearsal launched for `profile`, from its committed launch logs (a
    relaunch repeats its pass's list, and must). A log the census refused launched nothing and names no
    scene list ("REFUSES" on its first line); it is skipped, and every pass must have a launched log."""
    out = {}
    for log in sorted((REHEARSAL / "logs").glob(f"rehearse-measure__webgpu__{profile}__*.txt")):
        suffix = log.stem.split("__")[3]
        text = log.read_text()
        m = re.search(r"--scene (\S+)", text)
        if m is None:
            if ": REFUSES" not in text.splitlines()[0]:
                raise AssertionError(f"{log.name}: a launch with no scene list that the census did not refuse")
            continue
        scenes = sorted(m.group(1).split(","))
        if suffix in out and out[suffix] != scenes:
            raise AssertionError(f"{log.name}: a relaunch with another scene list")
        out[suffix] = scenes
    return out


class ShippedStage(unittest.TestCase):
    def test_w47s_rehearsal_reproduced_the_published_rows(self):
        rec = json.loads((REHEARSAL / "rehearsal.json").read_text())
        self.assertEqual((rec["verdict"], rec["cellsWanted"], rec["rows"], rec["rowsEqualButCapturedAt"],
                          rec["capturesIdentical"]), ("REPRODUCED", 132, 132, 132, 264))
        for key in ("rowsDiffer", "capturesDiffer", "t1InputsDiffer", "rowsWithNoPublishedTwin", "wantedCellsMissing",
                    "refereeOrHoldoutRowsRead", "rowsNotOnThePinnedEngine"):
            self.assertEqual(rec[key], [], key)

    def test_its_documents_are_the_shipped_and_snapshot_bytes_now(self):
        rec = json.loads((REHEARSAL / "rehearsal.json").read_text())
        now = stage.documents_state()
        for rel, slot in stage.SLOT_OF.items():
            self.assertEqual(rec["documents"][rel]["sha"], W.DOCUMENT_SHA[slot])
            self.assertEqual(now[rel]["sha"], W.DOCUMENT_SHA[slot], f"{rel} moved since the rehearsal")
            self.assertEqual(W.file_sha(W.document_path(slot)), W.DOCUMENT_SHA[slot])
        stage.require_snapshot()

    def test_w48s_stage_plans_exactly_the_cells_w47s_rehearsal_staged(self):
        total = 0
        for profile in W.DARK_025:
            plan = {suffix: sorted(scenes) for suffix, _, scenes in stage.passes("rehearse-measure", profile)}
            self.assertEqual(plan, launched(profile), profile)
            self.assertEqual(sum(len(v) for v in plan.values()), 66, profile)
            total += sum(len(v) for v in plan.values())
        self.assertEqual(total, 132)

    def test_every_planned_cell_has_its_published_row(self):
        B, _, _ = W.load_cuts()
        bed = B.load_published(W.REFERENCE["dark"])
        rows = {(r["key"]["profileKey"], r["key"]["sceneId"]) for r in bed.rows if r["key"]["web"]["renderer"] == "webgpu"}
        for profile in W.DARK_025:
            for _, _, scenes in stage.passes("rehearse-measure", profile):
                for sid in scenes:
                    self.assertIn((profile, sid), rows)

    def test_a_rehearsal_render_under_w48_refuses(self):
        with self.assertRaisesRegex(W.Refusal, "clause 2"):
            stage.declare("rehearsal")


def load_tests(loader, tests, pattern):
    return S.suite(loader, tests, T, REPLACED)


if __name__ == "__main__":
    unittest.main()
