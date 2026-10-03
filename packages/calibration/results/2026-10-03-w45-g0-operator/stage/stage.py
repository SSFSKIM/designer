#!/usr/bin/env python3.12
"""W45 G0 (b): the light 0.25 publication stage, W44 G1's `stage/stage.py` ported for W45 (charter
clauses 2, 6 and 7; X49, X53, X58), with the rehearsal on the shipped documents its port is tested
by. W44's committed copy is untouched.

G1 (steps 5 and 7), by the CLAUDE.md recipe, exactly as W44 declared it:

  stage.py declare                    matrix stage at ~/vitrea-w45/g1-stage-light/: the two light
                                      -glass0.25 standard profiles, both tiers, calibration,
                                      validation,holdout,recorded,probe, the FROZEN active/receded
                                      pair under profiles/. No capture.
  stage.py measure <tier>             per profile: `--set calibration,validation,recorded`, then
                                      `--set probe --scene <the planner's pre-gate list>`, each
                                      `--alpha --write-partial`. The referees and the holdout stay out.
  stage.py exposure <tier>            per profile, once, after the gate and the parent's ruling:
                                      `--set holdout,probe --scene <the planner's exposure list>`,
                                      only after the cross-gate ledger's last COMMITTED record names
                                      these documents, sources and the referee manifest.

  Before `declare` or `measure`: W45's parts 1 and 2 hashed (`bindings.require_part`), and the two
  light documents on disk SEALED by W45 (not c05's bytes, `recordedBy` "W45 G1"): a G1 stage of
  c05's own documents would publish nothing new and is refused. The captures land in this
  worktree's `packages/calibration/web-captures` (gitignored), which G2 copies to the canonical
  path. Logs and runs under G1's `stage/`.

G0's rehearsal (brief (b): "a stage rehearsal of the shipped documents reproduces the published
rows' T1"), scratch only and never published:

  stage.py rehearse-declare           matrix stage at ~/vitrea-w45/g0-stage-rehearsal/: the two light
                                      profiles, WebGPU, every set, over the documents on disk —
                                      which must BE c05 (file hashes 6d18c059eb42 / 4d5f23d9d312).
  stage.py rehearse-measure           per light profile, WebGPU: the T1 gate cells only (the
                                      planner's partition: no referee, no holdout), as two passes
                                      (`--set calibration,validation,recorded --scene <gate cvr>`,
                                      `--set probe --scene <gate probe, inside the pre-gate list>`),
                                      captures to the rehearsal's own scratch tree.
  stage.py rehearse-compare           every rehearsal row against the published c05 row of the same
                                      (profile, tier, scene): T1's three inputs equal, the whole row
                                      equal but `capturedAt`, and the PNG and alpha PNG
                                      byte-identical to the canonical tree; writes
                                      `rehearsal/rehearsal.json` and `.txt` beside this file.

Every launch runs through `with-gpu.sh` (the GPU lock and the classifying census, §5.201 §21) and
is logged in `runs.jsonl` beside its mode's logs; a started pass with no completion is a stop,
relaunched only under `--relaunch-after-stop REASON` as a new labelled pass. W44's stage, scratch
and evidence are refused as a stage directory (X58).
"""
from __future__ import annotations

import datetime
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "fit"))
import bindings as W  # noqa: E402

CAL, ROOT = W.CAL, W.ROOT
PROFILES = list(W.LIGHT_025)
ACTIVE = "profiles/apple-macos-27.0-1x-light-standard-glass0.25.json"
RECEDED = "profiles/apple-macos-27.0-1x-light-standard-glass0.25-receded.json"
CONFIG = CAL / "results/holdout-configuration/configuration.py"
LEDGER = "packages/calibration/results/holdout-configuration/configuration-log.json"
DOCUMENT_SET = "glass0.25"
REHEARSAL = HERE / "rehearsal"
MODES = {"g1": dict(stage=W.STAGE, out=W.G1_STAGE, captures=None, tiers="webgpu,css"),
         "rehearsal": dict(stage=W.REHEARSAL_STAGE, out=REHEARSAL,
                           captures=W.REHEARSAL_STAGE / "web-captures", tiers="webgpu")}


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def file_sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def log(out: Path, row):
    out.mkdir(parents=True, exist_ok=True)
    with (out / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def done(out: Path, label):
    rows = [json.loads(l) for l in (out / "runs.jsonl").read_text().splitlines()] \
        if (out / "runs.jsonl").exists() else []
    return any(r.get("label") == label and "exitCode" in r for r in rows), rows


def documents_state() -> dict:
    """The two light documents on disk: whether they are c05's bytes, and who recorded them."""
    out = {}
    for rel in (ACTIVE, RECEDED):
        path = CAL / rel
        key = path.stem
        doc = json.loads(path.read_text())
        out[rel] = dict(sha=file_sha(path), c05=file_sha(path).startswith(W.C05_DOCUMENT_FILE_SHA[key]),
                        recordedBy=doc.get("recordedBy"))
    return out


def require_sealed() -> None:
    """G1's stage reads W45's sealed documents and nothing else."""
    W.require_part(1)
    W.require_part(2)
    state = documents_state()
    for rel, s in state.items():
        if s["c05"] or s["recordedBy"] != "W45 G1":
            raise W.Refusal(f"stage REFUSES: {rel} is not sealed by W45 G1 (c05 bytes: {s['c05']}, recordedBy "
                            f"{s['recordedBy']!r}); a G1 stage stages W45's frozen documents (X53: regenerate the "
                            "runtime and run its export test first)")


def require_c05() -> None:
    """The rehearsal stages the SHIPPED documents, c05, and nothing else."""
    for rel, s in documents_state().items():
        if not s["c05"]:
            raise W.Refusal(f"rehearsal REFUSES: {rel} is not c05's published bytes ({s['sha'][:12]})")


def launch(argv, label, out: Path, mode: str, scenes=None) -> int:
    env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
    if MODES[mode]["captures"] is not None:
        env["VITREA_WEB_CAPTURES"] = str(MODES[mode]["captures"])
    started = now()
    shown = [a if scenes is None or a != ",".join(scenes) else f"<{len(scenes)} scenes>" for a in argv]
    log(out, dict(label=label, started=started, argv=shown))
    (out / "logs").mkdir(parents=True, exist_ok=True)
    log_path = out / "logs" / (label.replace("/", "__") + ".txt")
    with log_path.open("x") as handle:
        result = subprocess.run([str(W.G0 / "with-gpu.sh"), f"w45-stage {label}", *argv], cwd=CAL, env=env,
                                stdout=handle, stderr=subprocess.STDOUT)
    first = log_path.read_text().splitlines()[:1]
    code = 3 if result.returncode == 1 and first and ": REFUSES" in first[0] else result.returncode
    log(out, dict(label=label, started=started, completed=now(), exitCode=code))
    print(label, "exit", code, flush=True)
    return code


def holdout_configuration():
    spec = importlib.util.spec_from_file_location("hc", CONFIG)
    hc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hc)
    return hc


def committed_last_read():
    committed = subprocess.check_output(["git", "show", f"HEAD:{LEDGER}"], cwd=CAL, text=True)
    reads = json.loads(committed)["reads"]
    return reads[-1] if reads else None


def exposure_refusals(hc, committed_last) -> list[str]:
    """Every reason the exposure may not be read now; an empty list is the only permission (W44's,
    unchanged: the record must name these documents, sources and this referee manifest)."""
    plan = W.referee_plan()
    reads = hc.load_log()
    if not reads:
        return ["the holdout ledger has no record"]
    last = reads[-1]
    refusals = []
    if last.get("documentSet") != DOCUMENT_SET:
        refusals.append(f"the ledger's last record is documentSet {last.get('documentSet')!r}")
    if last.get("documents") != hc.document_hashes(DOCUMENT_SET):
        refusals.append("the ledger's last read is not these documents")
    if last.get("sourceSha256") != hc.source_hash()[0]:
        refusals.append("the sources moved since the ledger's record")
    manifest = plan.load_manifest()
    if (last.get("refereeManifest") or {}).get("sha256") != manifest["sha256"]:
        refusals.append("the ledger's last record does not witness this referee manifest")
    if committed_last != last:
        refusals.append("the ledger's record is not committed")
    return refusals


def gate_t1_scenes(profile: str) -> dict:
    """The T1 gate cells of one light profile, by role: (cvr, probe). Never a referee or holdout; every
    probe scene inside the planner's pre-gate whitelist."""
    B, t1 = W.load_cuts()
    plan = W.referee_plan()
    held = plan.referee_cells(plan.load_manifest())
    pregate = set(plan.lists()["pregateProbe"]["scenes"])
    cvr, probe = [], []
    for p, sid in t1.population([profile]):
        if t1.partition(p, sid, held) != "gate":
            continue
        role = B.SCENES.role[sid]
        if role == "probe":
            if sid not in pregate:
                raise W.Refusal(f"{sid}: a gate probe scene outside the planner's pre-gate whitelist")
            probe.append(sid)
        elif role in ("calibration", "validation", "recorded"):
            cvr.append(sid)
        else:
            raise W.Refusal(f"{sid}: role {role} in the gate partition")
    return dict(cvr=sorted(cvr), probe=sorted(probe))


def passes(mode: str, profile: str):
    """(label suffix, --set, scene whitelist or None) for each launch of a mode, per profile."""
    plan = W.referee_plan()
    lists = plan.lists()
    if mode == "measure":
        return [("cvr", "calibration,validation,recorded", None),
                ("probe", "probe", lists["pregateProbe"]["scenes"])]
    if mode == "exposure":
        return [("exposure", "holdout,probe", lists["exposure"]["scenes"])]
    if mode == "rehearse-measure":
        gate = gate_t1_scenes(profile)
        return [("cvr", "calibration,validation,recorded", gate["cvr"]), ("probe", "probe", gate["probe"])]
    raise W.Refusal(__doc__)


def declare(mode: str) -> int:
    stage = W.refuse_w44_path(MODES[mode]["stage"], "the stage")
    out = W.refuse_w44_path(MODES[mode]["out"], "the stage's evidence")
    argv = ["pnpm", "run", "-s", "matrix", "--", "stage", str(stage), "--profile", ",".join(PROFILES),
            "--renderer", MODES[mode]["tiers"], "--set", "calibration,validation,holdout,recorded,probe",
            "--material-profile", ACTIVE, "--receded-profile", RECEDED]
    result = subprocess.run(argv, cwd=CAL, capture_output=True, text=True)
    log(out, dict(label=f"declare/{mode}", at=now(), argv=argv, exitCode=result.returncode,
                  output=(result.stdout + result.stderr)[-2000:]))
    print(result.stdout[-1500:], result.stderr[-1500:])
    return result.returncode


def measure(mode: str, tier: str, stop_reason: str | None) -> int:
    key = "rehearsal" if mode == "rehearse-measure" else "g1"
    stage = W.refuse_w44_path(MODES[key]["stage"], "the stage")
    out = W.refuse_w44_path(MODES[key]["out"], "the stage's evidence")
    if not (stage / "membership.json").exists():
        raise W.Refusal(f"{stage}: not a declared stage (run the declare verb first)")
    for profile in PROFILES:
        for suffix, sets, scenes in passes(mode, profile):
            label = f"{mode}/{tier}/{profile}/{suffix}"
            marker = out / "logs" / (label.replace("/", "__") + ".started")
            attempt = 0
            complete, rows = done(out, label)
            while marker.exists() and not complete:
                if stop_reason is None:
                    raise W.Refusal("started pass without completion is a stop: " + label)
                if not any(r.get("label") == label and r.get("stopped") for r in rows):
                    log(out, dict(label=label, stopped=stop_reason, at=now()))
                attempt += 1
                label = f"{mode}/{tier}/{profile}/{suffix}/relaunch-{attempt}"
                marker = out / "logs" / (label.replace("/", "__") + ".started")
                complete, rows = done(out, label)
            if complete:
                continue
            argv = ["pnpm", "run", "-s", "compare", "--", "--stage", str(stage), "--profile", profile,
                    "--renderer", tier, "--material-profile", ACTIVE, "--receded-profile", RECEDED,
                    "--set", sets, "--alpha", "--write-partial"]
            if scenes is not None:
                if not scenes:
                    continue
                argv += ["--scene", ",".join(scenes)]
            marker.parent.mkdir(parents=True, exist_ok=True)
            marker.write_text(now() + "\n")
            code = launch(argv, label, out, key, scenes)
            if code not in (0, 1):
                raise W.Refusal(f"{label}: exit {code}; stop")
    return 0


def strip(row: dict) -> dict:
    out = json.loads(json.dumps(row))
    out.pop("capturedAt", None)
    return out


def rehearse_compare() -> int:
    """The rehearsal's rows against the published c05 rows, T1's inputs and the captures by bytes."""
    B, t1 = W.load_cuts()
    stage = W.REHEARSAL_STAGE
    captures = MODES["rehearsal"]["captures"]
    rows = json.loads((stage / "matrix.json").read_bytes())["cells"]
    c05 = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]): r
           for r in B.load_published(W.C05["light"]).rows}
    plan = W.referee_plan()
    held = plan.referee_cells(plan.load_manifest())
    wanted = {(p, "webgpu", s) for p in PROFILES for s in sum(gate_t1_scenes(p).values(), [])}
    t1_equal, rows_equal, png_equal = 0, 0, 0
    t1_differ, rows_differ, png_differ, no_twin, held_read = [], [], [], [], []
    for row in rows:
        k = (row["key"]["profileKey"], row["key"]["web"]["renderer"], row["key"]["sceneId"])
        if (k[0], k[2]) in held or B.SCENES.role[k[2]] == "holdout":
            held_read.append(list(k))
            continue
        twin = c05.get(k)
        if twin is None:
            no_twin.append(list(k))
            continue
        inputs = [(B.value(r, "material", m)) for r in (row, twin)
                  for m in ("interiorStdDevNative", "interiorStdDevWeb", "interiorMeanNative")]
        if inputs[:3] == inputs[3:]:
            t1_equal += 1
        else:
            t1_differ.append(dict(cell=list(k), rehearsal=inputs[:3], published=inputs[3:]))
        if strip(row) == strip(twin):
            rows_equal += 1
        else:
            a, b = strip(row), strip(twin)
            rows_differ.append(dict(cell=list(k), fields=sorted(f for f in set(a) | set(b) if a.get(f) != b.get(f))))
        for suffix in ("", "__alpha"):
            name = f"{k[2]}__{k[1]}{suffix}.png"
            mine, theirs = captures / k[0] / k[2] / name, W.CANONICAL_CAPTURES / k[0] / k[2] / name
            same = mine.exists() and theirs.exists() and file_sha(mine) == file_sha(theirs)
            png_equal += same
            if not same:
                png_differ.append(dict(cell=list(k), file=name, rehearsal=mine.exists() and file_sha(mine)[:16],
                                       canonical=theirs.exists() and file_sha(theirs)[:16]))
    have = {(r["key"]["profileKey"], r["key"]["web"]["renderer"], r["key"]["sceneId"]) for r in rows}
    missing = sorted(list(k) for k in wanted - have)
    reproduced = not (t1_differ or png_differ or no_twin or missing or held_read)
    result = dict(
        what="W45 G0 (b): the stage port's rehearsal on the shipped c05 documents, against the published rows",
        stage=str(stage), documents=documents_state(), cellsWanted=len(wanted), rows=len(rows),
        t1InputsEqual=t1_equal, t1InputsDiffer=t1_differ, rowsEqualButCapturedAt=rows_equal, rowsDiffer=rows_differ,
        capturesIdentical=png_equal, capturesDiffer=png_differ, rowsWithNoPublishedTwin=no_twin,
        wantedCellsMissing=missing, refereeOrHoldoutRowsRead=held_read,
        verdict="REPRODUCED" if reproduced else "DIFFERS")
    REHEARSAL.mkdir(parents=True, exist_ok=True)
    (REHEARSAL / "rehearsal.json").write_text(json.dumps(result, indent=1) + "\n")
    text = (f"rehearsal {result['verdict']}: {len(rows)} rows of {len(wanted)} wanted; T1 inputs equal "
            f"{t1_equal}, differ {len(t1_differ)}; rows equal but capturedAt {rows_equal}, differ {len(rows_differ)}; "
            f"captures identical {png_equal}, differ {len(png_differ)}; no published twin {len(no_twin)}; "
            f"missing {len(missing)}; referee/holdout rows {len(held_read)}")
    (REHEARSAL / "rehearsal.txt").write_text(text + "\n")
    print(text)
    return 0 if reproduced else 1


def main(argv=None) -> int:
    args = (argv or sys.argv)[1:]
    if not args:
        raise W.Refusal(__doc__)
    W.require_shared()
    mode = args[0]
    stop_reason = args[args.index("--relaunch-after-stop") + 1] if "--relaunch-after-stop" in args else None
    if mode == "declare":
        require_sealed()
        return declare("g1")
    if mode == "rehearse-declare":
        require_c05()
        return declare("rehearsal")
    if mode == "rehearse-measure":
        require_c05()
        return measure(mode, "webgpu", stop_reason)
    if mode == "rehearse-compare":
        return rehearse_compare()
    if mode in ("measure", "exposure"):
        tier = args[1]
        require_sealed()
        if mode == "exposure":
            refusals = exposure_refusals(holdout_configuration(), committed_last_read())
            if refusals:
                raise W.Refusal("exposure refused before any launch: " + "; ".join(refusals))
        return measure(mode, tier, stop_reason)
    raise W.Refusal(__doc__)


if __name__ == "__main__":
    sys.exit(main())
