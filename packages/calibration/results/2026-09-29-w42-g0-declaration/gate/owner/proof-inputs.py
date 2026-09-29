#!/usr/bin/env python3.12
"""Build the inputs of run-owner.py's GREEN and RED proofs (proof.txt), outside the repository.

  base-{light,dark}/     the four standard profiles' current WebGPU rows, byte for byte, at the
                         shipped documents: a stage whose scratch union IS the current union.
  candidate/<basename>   each shipped macOS 27 document plus one "$comment-w42-g0-owner-proof"
                         key: new bytes, new hash, the same resolved material.
  cand-{light,dark}/     the same rows re-named at those documents under a scratch path, as a
                         G2 render at identity documents would name them.
  cand-captures/         the canonical calibration/validation/probe WebGPU captures of those
                         rows, each cell__webgpu.json re-named the same way (holdout and
                         recorded captures are never opened).
  {cand,base}-light-seeded/  the light stage with one calibration row's interiorMeanWeb moved
                         0.1 away from its native mean (the RED seed).
  cand-light-m2-{toward,away}/  the candidate light stage with one photo row's interiorStdDevWeb
                         moved halfway TOWARD Apple's interiorStdDevNative (an M2 named miss),
                         or 10 % AWAY from it (an M2 failure).
  {base,cand}-{light,dark}-g2/  the same stages without their holdout rows, which is the shape
                         a G2 stage has; cand-light-g2-texture/ adds one calibration row whose
                         oklabDeltaEMean is set to 0.2 against the table's 0.07.

    python3.12 -B proof-inputs.py --out /tmp/w42-gate-owner/proof-inputs
"""
import argparse
import copy
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[3]  # owner -> gate -> declaration -> results -> calibration
sys.path.insert(0, str(CAL / "results/2026-09-26-w40-g0-generations"))
import matrix_store as store  # noqa: E402

CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
SCRATCH = "packages/calibration/results/2026-09-29-w42-g0-declaration/gate/owner/proof-candidate"
SCHEMES = {"light": ["apple-macos-27.0-1x-light-standard-glass0.5",
                     "apple-macos-27.0-2x-light-standard-glass0.5"],
           "dark": ["apple-macos-27.0-1x-dark-standard-glass0.5",
                    "apple-macos-27.0-2x-dark-standard-glass0.5"]}
LIGHT_1X = "apple-macos-27.0-1x-light-standard-glass0.5"
#: name -> (cell, axis, field, the native field it is read against or None, how it moves).
SEEDS = {
    "seeded": ((LIGHT_1X, "light-solid__rrect-md__rest"), "material", "interiorMeanWeb",
               "interiorMeanNative", lambda native, web: web + (0.1 if web >= native else -0.1)),
    "m2-toward": ((LIGHT_1X, "photo__rrect-md__inactive"), "material", "interiorStdDevWeb",
                  "interiorStdDevNative", lambda native, web: web + 0.5 * (native - web)),
    "m2-away": ((LIGHT_1X, "photo__rrect-md__inactive"), "material", "interiorStdDevWeb",
                "interiorStdDevNative",
                lambda native, web: web - (0.1 * web if native >= web else -0.1 * web)),
    "texture": ((LIGHT_1X, "light-solid__rrect-md__rest"), "perceptual", "oklabDeltaEMean", None,
                lambda native, web: 0.2),
}
COMMENT = ("W42 G0 owner-runner proof: the shipped document with this one key added, so its "
           "bytes and hash differ and its resolved material does not.")


def write_stage(target: Path, rows: list[bytes], active, receded) -> None:
    target.mkdir(parents=True)
    parsed = [json.loads(r) for r in rows]
    (target / "matrix.json").write_bytes(b'{\n  "schemaVersion": 5,\n  "cells": [\n    ' +
                                         b",\n    ".join(rows) + b"\n  ]\n}\n")
    membership = dict(schemaVersion=1, profiles=sorted({r["key"]["profileKey"] for r in parsed}),
                      tiers=["webgpu"], sets=sorted({r["fixtureSet"] for r in parsed}),
                      active=active, receded=receded,
                      cells=[dict(profileKey=r["key"]["profileKey"], renderer="webgpu",
                                  fixtureSet=r["fixtureSet"], sceneId=r["key"]["sceneId"])
                             for r in parsed])
    (target / "membership.json").write_text(json.dumps(membership, indent=2) + "\n")


def seeded(rows: list[bytes], name: str) -> tuple[list[bytes], dict]:
    cell, axis, field, native_field, move = SEEDS[name]
    out, record = [], None
    for raw in rows:
        row = json.loads(raw)
        if (row["key"]["profileKey"], row["key"]["sceneId"]) != cell:
            out.append(raw)
            continue
        native = None if native_field is None else row[axis][native_field]["value"]
        web = row[axis][field]["value"]
        moved = move(native, web)
        pattern = re.compile(rb'("' + field.encode() + rb'":\s*\{\s*"value":\s*)(-?[0-9][0-9.eE+-]*)')
        if len(pattern.findall(raw)) != 1:
            raise SystemExit(f"seed: {field} is not unique in the row")
        new = pattern.sub(lambda m: m.group(1) + repr(moved).encode(), raw)
        expected = copy.deepcopy(row)
        expected[axis][field]["value"] = moved
        assert json.loads(new) == expected
        out.append(new)
        record = dict(cell="/".join(cell), field=f"{axis}.{field}", native=native, web=web,
                      seeded=moved, changeFraction=(moved - web) / web,
                      **({} if native is None else dict(errorBefore=abs(web - native),
                                                        errorAfter=abs(moved - native))))
    assert record is not None
    return out, record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    if out.exists():
        raise SystemExit(f"{out} exists")
    rows = store.load_current_rows(matrix_path=str(CAL / "results/matrix.json"))
    scenes = json.loads((CAL.parent.parent / "apps/reference-apple/scenes.json").read_text())
    roles = {sid: role for role, ids in scenes["split"].items() if not role.startswith("$")
             for sid in ids}
    (out / "candidate").mkdir(parents=True)
    record = dict(stages={}, candidates={}, captures=0)
    for scheme, profiles in SCHEMES.items():
        mine = [r for r in rows if r["key"]["profileKey"] in profiles
                and r["key"]["web"]["renderer"] == "webgpu"]
        clauses = {tuple(c) for r in mine for c in store.documents(r)}
        pair = {kind: dict(path=path, sha256=sha) for kind, path, sha in clauses}
        assert len(clauses) == 2 and set(pair) == {"materialProfile", "recededProfile"}
        raw = [store._RAW[id(r)] for r in mine]
        write_stage(out / f"base-{scheme}", raw, pair["materialProfile"], pair["recededProfile"])
        renames, declared = {}, {}
        for kind, document in pair.items():
            source = CAL.parent.parent / document["path"]
            text = source.read_text()
            assert text.rstrip().endswith("}")
            body = text.rstrip()[:-1].rstrip() + (f',\n  "$comment-w42-g0-owner-proof": '
                                                  f"{json.dumps(COMMENT)}\n}}\n")
            assert {k: v for k, v in json.loads(body).items()
                    if k != "$comment-w42-g0-owner-proof"} == json.loads(text)
            target = out / "candidate" / source.name
            target.write_text(body)
            sha12 = hashlib.sha256(body.encode()).hexdigest()[:12]
            renames[f"{kind}={document['path']} sha256:{document['sha256']}"] = \
                f"{kind}={SCRATCH}/{source.name} sha256:{sha12}"
            declared[kind] = dict(path=f"{SCRATCH}/{source.name}", sha256=sha12)
            record["candidates"][source.name] = dict(shipped=document["sha256"], candidate=sha12)
        renamed = []
        for r in raw:
            for old, new in renames.items():
                assert r.count(old.encode()) == 1
                r = r.replace(old.encode(), new.encode())
            renamed.append(r)
        write_stage(out / f"cand-{scheme}", renamed, declared["materialProfile"],
                    declared["recededProfile"])
        if scheme == "light":
            record["seeds"] = {}
            for name in SEEDS:
                rows_seeded, record["seeds"][name] = seeded(renamed, name)
                write_stage(out / f"cand-light-{name}", rows_seeded, declared["materialProfile"],
                            declared["recededProfile"])
            base_seeded, _ = seeded(raw, "seeded")
            write_stage(out / "base-light-seeded", base_seeded, pair["materialProfile"],
                        pair["recededProfile"])
        # G2's shape: the stage holds no holdout row (clause 10 never renders one before the
        # exposure), so W41's pair replacement drops the pair's current holdout rows.
        def g2(rows_):
            return [r for r in rows_ if json.loads(r)["fixtureSet"] != "holdout"]
        write_stage(out / f"base-{scheme}-g2", g2(raw), pair["materialProfile"], pair["recededProfile"])
        write_stage(out / f"cand-{scheme}-g2", g2(renamed), declared["materialProfile"],
                    declared["recededProfile"])
        if scheme == "light":
            rows_seeded, record["seeds"]["texture"] = seeded(g2(renamed), "texture")
            write_stage(out / "cand-light-g2-texture", rows_seeded, declared["materialProfile"],
                        declared["recededProfile"])
        for r in mine:
            sid, profile = r["key"]["sceneId"], r["key"]["profileKey"]
            if roles.get(sid) not in ("calibration", "validation", "probe"):
                continue
            source = CANONICAL / profile / sid
            meta = json.loads((source / "cell__webgpu.json").read_text())
            if meta["capturePath"] != r["key"]["web"]["capturePath"]:
                raise SystemExit(f"{profile}/{sid}: the canonical tree holds another generation")
            for old, new in renames.items():
                meta["capturePath"] = meta["capturePath"].replace(old, new)
            target = out / "cand-captures" / profile / sid
            target.mkdir(parents=True)
            (target / "cell__webgpu.json").write_text(json.dumps(meta, indent=2) + "\n")
            shutil.copyfile(source / f"{sid}__webgpu.png", target / f"{sid}__webgpu.png")
            record["captures"] += 1
        record["stages"][scheme] = dict(rows=len(mine), documents=pair)
    (out / "proof-inputs.json").write_text(json.dumps(record, indent=1) + "\n")
    print(json.dumps(record, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
