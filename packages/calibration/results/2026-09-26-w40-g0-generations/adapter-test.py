#!/usr/bin/env python3.12
"""Live W40 Python adapter check: four named groups and the original envelope."""
from matrix_store import (load_current_rows, load_current_profile, load_generation,
                          owners_for_document, legacy_envelope_digest)
from snapshot import digest
import copy
import json
import os
import pathlib
import re
import tempfile
from snapshot import key

EXPECTED = "7df96c9246bc9b964fd6e173e742f49dcf493ccb360f7df505a0157240eaf0de"
GROUPS = {"950ce1c3e917": 437, "6a9600720477": 670,
          "0eac5b294cc2": 277, "85ad7f7e3e0d": 509}


def synthetic():
    """Test a receded-only reseal, scratch override and closed metadata boundary."""
    with tempfile.TemporaryDirectory(prefix="w40-python-store-") as temporary:
        root = pathlib.Path(temporary)
        generations = root / "generations"
        generations.mkdir()
        frozen = copy.deepcopy(load_generation("950ce1c3e917")[0])
        original = copy.deepcopy(load_generation("85ad7f7e3e0d")[0])
        resealed = copy.deepcopy(original)
        old_receded, new_receded = "30fbe05986ae", "111111111111"
        resealed["key"]["web"]["capturePath"] = resealed["key"]["web"]["capturePath"].replace(
            f"recededProfile=packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json sha256:{old_receded}",
            f"recededProfile=packages/calibration/profiles/apple-macos-27.0-1x-light-standard-glass0.5-receded.json sha256:{new_receded}")
        assert resealed["key"]["web"]["capturePath"] != original["key"]["web"]["capturePath"]

        def save(path, cells):
            path.write_text(json.dumps({"schemaVersion": 5, "cells": cells}, indent=2) + "\n")
            return path.read_bytes()

        save(root / "matrix.json", [frozen])
        retired_name = "85ad7f7e3e0d.json"
        current_name = "85ad7f7e3e0d-111111111111.json"
        entries = {}
        for filename, row, receded, status in ((retired_name, original, old_receded, "retired"),
                                                (current_name, resealed, new_receded, "current")):
            raw = save(generations / filename, [row])
            paths = row["key"]["web"]["capturePath"]
            docs = [{"path": path, "sha256": sha} for path, sha in
                    re.findall(r"(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})", paths)]
            entries[filename] = {"activeDocumentSha256": "85ad7f7e3e0d",
                                 "documents": sorted(docs, key=lambda d: d["path"]),
                                 "rowCount": 1, "rowsByProfileKey": {row["key"]["profileKey"]: 1},
                                 "bytes": len(raw), "sha256": digest(raw), "status": status}
        index = {"schemaVersion": 1, "files": entries,
                 "byDocumentSha256": {"85ad7f7e3e0d": sorted(entries),
                                        old_receded: [retired_name], new_receded: [current_name]},
                 "currentByProfile": {original["key"]["profileKey"]: current_name}}
        (generations / "index.json").write_text(json.dumps(index))
        rows = load_current_rows(results_dir=root)
        assert len(rows) == 2
        matrix_alias = root / "MATRIX.JSON"
        if matrix_alias.exists() and os.path.samefile(matrix_alias, root / "matrix.json"):
            assert len(load_current_rows(matrix_path=matrix_alias, results_dir=root)) == 2
        hardlink = root / "frozen-hardlink.json"
        os.link(root / "matrix.json", hardlink)
        assert len(load_current_rows(matrix_path=hardlink, results_dir=root)) == 2
        assert any(key(row) == key(resealed) for row in rows)
        assert len(load_generation("85ad7f7e3e0d", old_receded, results_dir=root)) == 1
        assert len(load_generation("85ad7f7e3e0d", new_receded, results_dir=root)) == 1
        try:
            load_generation("85ad7f7e3e0d", results_dir=root)
        except ValueError as error:
            assert "owners" in str(error)
        else:
            raise AssertionError("unqualified active-only lookup accepted two generations")
        scratch = root / "scratch.json"
        raw = save(scratch, sorted([frozen, original, resealed], key=key))
        assert legacy_envelope_digest(load_current_rows(matrix_path=scratch, results_dir=root)) == digest(raw)
        index["files"][current_name]["sha256"] = "0" * 64
        (generations / "index.json").write_text(json.dumps(index))
        try:
            load_current_rows(results_dir=root)
        except ValueError as error:
            assert "SHA-256" in str(error)
        else:
            raise AssertionError("altered index hash accepted")
        index["files"][current_name]["sha256"] = digest((generations / current_name).read_bytes())
        (generations / "index.json").write_text(json.dumps(index))
        duplicate = root / "duplicate.json"
        save(duplicate, [frozen, frozen])
        try:
            load_current_rows(matrix_path=duplicate, results_dir=root)
        except ValueError as error:
            assert "duplicate" in str(error)
        else:
            raise AssertionError("duplicate scratch row accepted")
        (generations / current_name).unlink()
        try:
            load_current_rows(results_dir=root)
        except FileNotFoundError:
            pass
        else:
            raise AssertionError("missing indexed generation accepted")

        # The no-receded generation and its posed sibling are different pair identities.
        save(generations / current_name, [resealed])
        renamed = f"85ad7f7e3e0d-{old_receded}.json"
        (generations / retired_name).rename(generations / renamed)
        index["files"][renamed] = index["files"].pop(retired_name)
        index["byDocumentSha256"][old_receded] = [renamed]
        unposed = copy.deepcopy(original)
        unposed["key"]["web"]["capturePath"] = re.sub(
            r",? recededProfile=\S+ sha256:[0-9a-f]{12}", "",
            unposed["key"]["web"]["capturePath"])
        assert "recededProfile=" not in unposed["key"]["web"]["capturePath"]
        raw = save(generations / retired_name, [unposed])
        active_doc = next(d for d in index["files"][renamed]["documents"]
                          if d["sha256"] == "85ad7f7e3e0d")
        index["files"][retired_name] = {
            "activeDocumentSha256": "85ad7f7e3e0d", "documents": [active_doc],
            "rowCount": 1, "rowsByProfileKey": {unposed["key"]["profileKey"]: 1},
            "bytes": len(raw), "sha256": digest(raw), "status": "retired",
        }
        index["byDocumentSha256"]["85ad7f7e3e0d"] = sorted(index["files"])
        (generations / "index.json").write_text(json.dumps(index))
        assert len(load_generation("85ad7f7e3e0d", None, results_dir=root)) == 1
        assert len(load_generation("85ad7f7e3e0d", old_receded, results_dir=root)) == 1
        assert len(load_generation("85ad7f7e3e0d", new_receded, results_dir=root)) == 1
        try:
            load_generation("85ad7f7e3e0d", results_dir=root)
        except ValueError as error:
            assert "owners" in str(error)
        else:
            raise AssertionError("unqualified lookup accepted (A,none) beside (A,R)")
        print("synthetic reseal, none/receded pair, scratch, altered hash, duplicate, missing file: passed")


def main():
    grouped = []
    for active, count in GROUPS.items():
        rows = load_generation(active)
        assert len(rows) == count, (active, len(rows), count)
        grouped.extend(rows)
        print(f"{active}: {len(rows)} rows")
    assert legacy_envelope_digest(grouped) == EXPECTED
    current = load_current_rows()
    assert len(current) == 1893
    case_alias = pathlib.Path(__file__).resolve().parents[1] / "MATRIX.JSON"
    if case_alias.exists() and os.path.samefile(case_alias, case_alias.parent / "matrix.json"):
        assert len(load_current_rows(matrix_path=case_alias)) == 1893
    assert [key(row) for row in sorted(grouped, key=key)] == [key(row) for row in current]
    assert legacy_envelope_digest(current) == EXPECTED
    assert legacy_envelope_digest([]) == digest(b'{\n  "schemaVersion": 5,\n  "cells": []\n}\n')
    assert len(load_generation("30fbe05986ae")) == 509  # receded-only unique alias
    assert len(load_current_profile("apple-macos-26.5-1x-light-standard")) == 281
    assert len(owners_for_document("45acb6d916b9")) == 2
    try:
        load_generation("45acb6d916b9")
    except ValueError as error:
        assert "owners" in str(error)
    else:
        raise AssertionError("shared receded hash must refuse ambiguous lookup")
    print(f"current union: {len(current)} rows; raw legacy envelope SHA-256: {EXPECTED}")
    print("historical shared-receded alias: both owners found; ambiguous lookup refused")
    synthetic()


if __name__ == "__main__":
    main()
