"""W48 G0 (a): the archive tool's red cases, on synthetic trees only (no ladder file is read).

    python3.12 -B -m unittest -v test_archive      (from this directory)
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import w47_ladders_archive as A  # noqa: E402


def tree(root: Path) -> Path:
    """A minimal archive tree: one file per section and its inventory."""
    files = {"ladders/control/1x/matrix.json": b'{"cells": []}\n', "drive/logs/control__1x.txt": b"ok\n",
             "reference/p/s/s__webgpu.png": b"\x89PNG fake"}
    inv = dict(schema=A.SCHEMA, ladders=[], drive=[], reference=[])
    for rel, raw in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_bytes(raw)
        inv[rel.split("/")[0]].append(dict(path=rel, sha256=hashlib.sha256(raw).hexdigest(), bytes=len(raw)))
    (root / "inventory.json").write_text(json.dumps(inv))
    return root


class ArchiveTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="w48-archive-test-"))
        self.root = tree(self.tmp / "tree")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_a_tree_verifies(self):
        self.assertEqual(A.verify_tree(self.root)["entries"], 3)

    def test_an_altered_file_refuses(self):
        (self.root / "drive/logs/control__1x.txt").write_bytes(b"no\n")
        with self.assertRaisesRegex(ValueError, "altered"):
            A.verify_tree(self.root)

    def test_an_unlisted_file_refuses(self):
        (self.root / "ladders/extra.png").write_bytes(b"x")
        with self.assertRaisesRegex(ValueError, "unlisted"):
            A.verify_tree(self.root)

    def test_a_missing_file_refuses(self):
        (self.root / "reference/p/s/s__webgpu.png").unlink()
        with self.assertRaisesRegex(ValueError, "missing"):
            A.verify_tree(self.root)

    def test_a_path_outside_its_section_refuses(self):
        inv = json.loads((self.root / "inventory.json").read_text())
        inv["drive"][0]["path"] = "ladders/control/1x/matrix.json"
        (self.root / "inventory.json").write_text(json.dumps(inv))
        with self.assertRaisesRegex(ValueError, "escapes its section"):
            A.verify_tree(self.root)

    def test_pack_is_deterministic_and_round_trips_through_fetch(self):
        one = A.pack(self.root, self.tmp / "a")
        two = A.pack(self.root, self.tmp / "b")
        self.assertEqual(one["sha256"], two["sha256"])
        got = A.fetch(A.TAG, one["asset"], one["sha256"], cache=self.tmp / "cache", source=Path(one["path"]))
        self.assertEqual(A.verify_tree(got)["inventorySha256"], A.verify_tree(self.root)["inventorySha256"])
        for p in self.root.rglob("*"):
            if p.is_file():
                self.assertEqual((got / p.relative_to(self.root)).read_bytes(), p.read_bytes())

    def test_a_wrong_digest_extracts_nothing(self):
        one = A.pack(self.root, self.tmp / "a")
        wrong = "0" * 64
        bad = self.tmp / A.asset_name(wrong)
        shutil.copyfile(one["path"], bad)
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            A.fetch(A.TAG, A.asset_name(wrong), wrong, cache=self.tmp / "cache", source=bad)
        self.assertFalse((self.tmp / "cache" / wrong / "extracted").exists())

    def test_an_asset_not_named_by_its_digest_refuses(self):
        with self.assertRaisesRegex(ValueError, "does not carry"):
            A.fetch(A.TAG, "w47-ladders-archive-x.tar.zst", "a" * 64, cache=self.tmp / "cache")

    def test_the_asset_is_never_written_into_the_repository(self):
        with self.assertRaisesRegex(ValueError, "outside the repository"):
            A.pack(self.root, A.EVIDENCE / "asset")


if __name__ == "__main__":
    unittest.main()
