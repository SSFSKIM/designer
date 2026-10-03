#!/usr/bin/env python3.12
"""W44 G1 steps 5 and 7: the light 0.25 publication stage, read by the CLAUDE.md recipe.

W43 G3 (ii)'s stage driver (`results/2026-10-02-w43-g3-refit/stage/read.py`), carried to one light
stage and to the referee manifest (X49):

  stage.py declare                    matrix stage: the two light -glass0.25 standard profiles, both
                                      tiers, calibration,validation,holdout,recorded,probe, the
                                      FROZEN active/receded pair under profiles/. No capture.
  stage.py measure <tier>             per profile: `--set calibration,validation,recorded`, then
                                      `--set probe --scene <the planner's pre-gate list>` (every probe
                                      scene less the manifest), each with `--write-partial` and a
                                      fresh census before it. The referees and the holdout stay out.
  stage.py exposure <tier>            per profile, once, after the gate and the parent's ruling:
                                      `--set holdout,probe --scene <the planner's exposure list>`
                                      (the canonical holdout and the manifest), only after the
                                      cross-gate ledger's last COMMITTED record names these
                                      documents and sources (`configuration.py record --documents
                                      glass0.25 --referees <manifest>`).

Strict shipped mode at the (macOS 27.0, glass 0.25) pair: `--material-profile` and
`--receded-profile` name the frozen documents, the runtime selects
`macos27Glass025MaterialProfileDocument` by its pair (X53: the module is regenerated from the frozen
documents and its export test green before this runs), and no `--cross-position` appears. The stage
lives at ~/vitrea-w44/g1-stage-light/ with `membership.json` beside `matrix.json`; the captures
land in this worktree's `packages/calibration/web-captures` (gitignored), which the landing (G2)
copies to the canonical path. Every launch is logged in runs.jsonl beside this file with its compare
log under logs/; a started pass with no completion is a stop, relaunched only under
`--relaunch-after-stop REASON` as a new labelled pass.
"""
import datetime
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
ROOT = CAL.parent.parent
G0 = CAL / "results" / "2026-10-03-w44-g0-declaration"
STAGE = Path.home() / "vitrea-w44" / "g1-stage-light"
PROFILES = ["apple-macos-27.0-1x-light-standard-glass0.25", "apple-macos-27.0-2x-light-standard-glass0.25"]
ACTIVE = "profiles/apple-macos-27.0-1x-light-standard-glass0.25.json"
RECEDED = "profiles/apple-macos-27.0-1x-light-standard-glass0.25-receded.json"
CONFIG = CAL / "results/holdout-configuration/configuration.py"
LEDGER = "packages/calibration/results/holdout-configuration/configuration-log.json"
DOCUMENT_SET = "glass0.25"
MANIFEST = G0 / "referees" / "referees.json"

_spec = importlib.util.spec_from_file_location("w43_census", CAL / "results/2026-10-02-w43-g3-refit/stage/census.py")
census = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(census)
sys.path.insert(0, str(G0 / "referees"))
import plan  # noqa: E402


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(row):
    with (HERE / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def done(label):
    rows = [json.loads(l) for l in (HERE / "runs.jsonl").read_text().splitlines()] \
        if (HERE / "runs.jsonl").exists() else []
    return any(r.get("label") == label and "exitCode" in r for r in rows), rows


def launch(argv, label, scenes=None):
    machine = census.observe()
    log(dict(label=label, census=dict(refusals=machine["refusals"], refuse=machine["refuse"],
                                      annotate=sorted({a["why"] for a in machine["annotate"]}),
                                      x6=machine["x6"]), at=machine["recordedAt"]))
    if not machine["passes"]:
        print("CENSUS REFUSED", label, machine["refusals"], machine["refuse"][:3], flush=True)
        sys.exit(3)
    env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
    started = now()
    shown = [a if scenes is None or a != ",".join(scenes) else f"<{len(scenes)} scenes>" for a in argv]
    log(dict(label=label, started=started, argv=shown))
    with (HERE / "logs" / (label.replace("/", "__") + ".txt")).open("x") as out:
        result = subprocess.run(argv, cwd=CAL, env=env, stdout=out, stderr=subprocess.STDOUT)
    log(dict(label=label, started=started, completed=now(), exitCode=result.returncode))
    print(label, "exit", result.returncode, flush=True)
    return result.returncode


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
    """Every reason the exposure may not be read now; an empty list is the only permission (W43's
    holdout_refusals, with the referee manifest's witness: the record must name this manifest)."""
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


def passes(mode: str):
    """(label suffix, --set, scene whitelist or None) for each launch of a mode, per profile."""
    lists = plan.lists()
    if mode == "measure":
        return [("cvr", "calibration,validation,recorded", None),
                ("probe", "probe", lists["pregateProbe"]["scenes"])]
    if mode == "exposure":
        return [("exposure", "holdout,probe", lists["exposure"]["scenes"])]
    raise SystemExit(__doc__)


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    mode = args[0]
    (HERE / "logs").mkdir(exist_ok=True)
    if mode == "declare":
        argv = ["pnpm", "run", "-s", "matrix", "--", "stage", str(STAGE), "--profile", ",".join(PROFILES),
                "--renderer", "webgpu,css", "--set", "calibration,validation,holdout,recorded,probe",
                "--material-profile", ACTIVE, "--receded-profile", RECEDED]
        result = subprocess.run(argv, cwd=CAL, capture_output=True, text=True)
        log(dict(label="declare/light", at=now(), argv=argv, exitCode=result.returncode,
                 output=(result.stdout + result.stderr)[-2000:]))
        print(result.stdout, result.stderr)
        sys.exit(result.returncode)
    tier = args[1]
    stop_reason = args[args.index("--relaunch-after-stop") + 1] if "--relaunch-after-stop" in args else None
    if mode == "exposure":
        refusals = exposure_refusals(holdout_configuration(), committed_last_read())
        if refusals:
            raise SystemExit("exposure refused before any launch: " + "; ".join(refusals))
    for profile in PROFILES:
        for suffix, sets, scenes in passes(mode):
            label = f"{mode}/{tier}/{profile}/{suffix}"
            marker = HERE / "logs" / (label.replace("/", "__") + ".started")
            attempt = 0
            complete, rows = done(label)
            while marker.exists() and not complete:
                if stop_reason is None:
                    raise SystemExit("started pass without completion is a stop: " + label)
                if not any(r.get("label") == label and r.get("stopped") for r in rows):
                    log(dict(label=label, stopped=stop_reason, at=now()))
                attempt += 1
                label = f"{mode}/{tier}/{profile}/{suffix}/relaunch-{attempt}"
                marker = HERE / "logs" / (label.replace("/", "__") + ".started")
                complete, rows = done(label)
            if complete:
                continue
            argv = ["pnpm", "run", "-s", "compare", "--", "--stage", str(STAGE), "--profile", profile,
                    "--renderer", tier, "--material-profile", ACTIVE, "--receded-profile", RECEDED,
                    "--set", sets, "--alpha", "--write-partial"]
            if scenes is not None:
                argv += ["--scene", ",".join(scenes)]
            marker.write_text(now() + "\n")
            code = launch(argv, label, scenes)
            if code not in (0, 1):
                raise SystemExit(f"{label}: exit {code}; stop")


if __name__ == "__main__":
    main()
