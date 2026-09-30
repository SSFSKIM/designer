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
  cand-light-closure/    two named misses CLOSED (the parent's ruling of 2026-09-30, run-owner.py
                         step 8): L1's named 1x light impulse__capsule-button__inactive-tint-orange
                         at its native mean, and MISSED_27_ROWS's 1x light photo__rrect-sm__inactive
                         chromaStructureRatioR at R = 1 (its web ratio set to the native one).
  cand-light-closure-plus-new/  the same two closures and the RED seed together: a closure
                         never excuses a new miss.

Added by the fix wave on the gate review of b151aff4:
  The light stages hold the WebGPU rows of all four light gated profiles, reduced transparency and
  increased contrast included (finding 1: a candidate that moves the light documents must render
  all six gated profiles' WebGPU pairs), and {base,cand}-light-no-rt/ omit reduced transparency's,
  the synthetic stage the new refusal must refuse.
  cand-light-closure-move/  the two closures and a MOVE of the other two M1 misses (the 2x light
                         photo__rrect-sm inactive and rest R set to 1.43 and 1.42, still past
                         1.40): finding 2's re-record. cand-light-closure-move-plus-new/ adds the
                         RED seed.
  cand-{light,dark}-a1/  Decision Log 5d's four cell-profiles at round 3's r3-2pgb growths (light
                         photo__rrect-md__inactive-tint-orange +0.0108 / +0.0100, dark
                         photo__capsule-button__inactive-tint-orange +0.0138 / +0.0133, 1x / 2x):
                         item A1. cand-light-a1-fifth/ adds a fifth growth failure, round 3's [U7]
                         reading, 1x light checkerboard__rrect-ml__rest at +0.0105.

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
                     "apple-macos-27.0-2x-light-standard-glass0.5",
                     "apple-macos-27.0-1x-light-reduced-transparency-glass0.5",
                     "apple-macos-27.0-1x-light-increased-contrast-coupled-glass0.5"],
           "dark": ["apple-macos-27.0-1x-dark-standard-glass0.5",
                    "apple-macos-27.0-2x-dark-standard-glass0.5"]}
LIGHT_1X = "apple-macos-27.0-1x-light-standard-glass0.5"
LIGHT_2X = "apple-macos-27.0-2x-light-standard-glass0.5"
RT = "apple-macos-27.0-1x-light-reduced-transparency-glass0.5"
#: L1's W33 baseline generations (adopted-thresholds.test.ts BASELINE), for the growth seeds.
L1_BASELINE = {"light": ("6e509c7f76cc", "45acb6d916b9"), "dark": ("eab099cc6698", "4e68f81869f6")}
#: Growth seeds: name -> (cell, growth). Decision Log 5d's four at r3-2pgb, and [U7] as a fifth.
GROWTH = {
    "g5d-l1": ((LIGHT_1X, "photo__rrect-md__inactive-tint-orange"), 0.0108),
    "g5d-l2": ((LIGHT_2X, "photo__rrect-md__inactive-tint-orange"), 0.0100),
    "g5d-d1": (("apple-macos-27.0-1x-dark-standard-glass0.5",
                "photo__capsule-button__inactive-tint-orange"), 0.0138),
    "g5d-d2": (("apple-macos-27.0-2x-dark-standard-glass0.5",
                "photo__capsule-button__inactive-tint-orange"), 0.0133),
    "g-fifth": ((LIGHT_1X, "checkerboard__rrect-ml__rest"), 0.0105),
}
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
    "l1-close": ((LIGHT_1X, "impulse__capsule-button__inactive-tint-orange"), "material",
                 "interiorMeanWeb", "interiorMeanNative", lambda native, web: native),
    "m27-close": ((LIGHT_1X, "photo__rrect-sm__inactive"), "material", "chromaStructureRatioWeb",
                  "chromaStructureRatioNative", lambda native, web: native),
    "m27-move-a": ((LIGHT_2X, "photo__rrect-sm__inactive"), "material", "chromaStructureRatioWeb",
                   "chromaStructureRatioNative", lambda native, web: 1.43 * native),
    "m27-move-b": ((LIGHT_2X, "photo__rrect-sm__rest"), "material", "chromaStructureRatioWeb",
                   "chromaStructureRatioNative", lambda native, web: 1.42 * native),
}
#: stage name -> the seeds applied in order (only the stages that combine seeds). A stage is
#: written for each scheme that holds at least one of its seeds' cells.
COMBINED = {"closure": ("l1-close", "m27-close"),
            "closure-plus-new": ("l1-close", "m27-close", "seeded"),
            "closure-move": ("l1-close", "m27-close", "m27-move-a", "m27-move-b"),
            "closure-move-plus-new": ("l1-close", "m27-close", "m27-move-a", "m27-move-b", "seeded"),
            "a1": ("g5d-l1", "g5d-l2", "g5d-d1", "g5d-d2"),
            "a1-fifth": ("g5d-l1", "g5d-l2", "g5d-d1", "g5d-d2", "g-fifth")}
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
    return out, record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, required=True)
    out = parser.parse_args().out.resolve()
    if out.exists():
        raise SystemExit(f"{out} exists")
    rows = store.load_current_rows(matrix_path=str(CAL / "results/matrix.json"))
    # The growth seeds move a cell's web mean to n + sign(w - n) (before + g): its L1 error is
    # its W33 baseline error plus g, which is the growth L1 reads.
    for name, (cell, growth) in GROWTH.items():
        scheme = "dark" if "-dark-" in cell[0] else "light"
        old = [r for r in store.load_generation(*L1_BASELINE[scheme])
               if (r["key"]["profileKey"], r["key"]["sceneId"]) == cell
               and r["key"]["web"]["renderer"] == "webgpu"]
        assert len(old) == 1, (name, len(old))
        before = abs(old[0]["material"]["interiorMeanWeb"]["value"]
                     - old[0]["material"]["interiorMeanNative"]["value"])
        SEEDS[name] = (cell, "material", "interiorMeanWeb", "interiorMeanNative",
                       lambda native, web, before=before, growth=growth:
                       native + (1.0 if web >= native else -1.0) * (before + growth))
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
        record.setdefault("seeds", {})
        for name in SEEDS:
            rows_seeded, seed_record = seeded(renamed, name)
            if seed_record is None:
                continue  # the seed's cell is in the other scheme's stage
            record["seeds"][name] = seed_record
            write_stage(out / f"cand-{scheme}-{name}", rows_seeded, declared["materialProfile"],
                        declared["recededProfile"])
        for stage, names in COMBINED.items():
            rows_seeded, hit = renamed, False
            for name in names:
                rows_seeded, seed_record = seeded(rows_seeded, name)
                hit |= seed_record is not None
            if hit:
                write_stage(out / f"cand-{scheme}-{stage}", rows_seeded,
                            declared["materialProfile"], declared["recededProfile"])
        record["combined"] = {stage: list(names) for stage, names in COMBINED.items()}
        if scheme == "light":
            base_seeded, _ = seeded(raw, "seeded")
            write_stage(out / "base-light-seeded", base_seeded, pair["materialProfile"],
                        pair["recededProfile"])
            # Finding 1's synthetic stage: the light stages without reduced transparency's WebGPU
            # rows, which the candidate's light documents drew.
            def no_rt(rows_):
                return [r for r in rows_ if json.loads(r)["key"]["profileKey"] != RT]
            write_stage(out / "base-light-no-rt", no_rt(raw), pair["materialProfile"],
                        pair["recededProfile"])
            write_stage(out / "cand-light-no-rt", no_rt(renamed), declared["materialProfile"],
                        declared["recededProfile"])
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
