#!/usr/bin/env python3.12
"""W49a G0: build, render and read the declared probes P1 and P2 into scratch (part 1; charter Decision Logs 1, 6, 8).

    python3.12 -B probe.py build                     the seven candidates (specs/), into SCRATCH/candidates
    python3.12 -B probe.py render LABEL              both scales, census-gated, under the GPU lock
    python3.12 -B probe.py read LABEL                W48's cut launcher on each scale's render -> readings/
    python3.12 -B probe.py report                    P1's prediction check, P2's X74 report and DL2 / DL4 reading

**The order is the declaration's.** `render` refuses unless both parts are hashed and `declare.py check` passes
on them, so no pixel exists before the rule that reads it (DL2, DL4).

**What renders.** Candidate mode (`compare --candidate-document`), WebGPU, the dark 0.25 profile of each scale,
the sets `calibration,validation,recorded,probe`, into a scratch `--out-matrix` and capture tree; never a stage,
never the canonical tree. The cells are the T1 GATE cells of the dark 0.25 profiles as W48's exposure cut
partitions them (`rule.B2D074_CUT`): P2 its inactive cells (family R moves the receded document only, so a
rest cell reads `b2d074d2df24` by construction), P1 its rest cells (the span top's own reading, F2). No
referee or holdout cell is rendered (DL6).

**The census.** Before each launch the classifying census (W43 G3 (ii)'s `stage/census.py`, by path) and the
browser pin (Playwright 1.62.1, Chromium 1234 / 151.0.7922.34, the engine every dark 0.25 row carries) must
pass; each observation is appended to `census.jsonl` beside this file. A refusal launches nothing.

**The reading.** W48's cut launcher (`2026-10-06-w48-g0-declaration/cuts/cuts.py`, W47's cuts under W48's
bindings; reference `d0219cd684bf`) on each scale's matrix and capture tree, `--kind candidate`, with the
reference's captures read from `web-captures-superseded/d0219cd684bf/` (where W48 G2 moved them; the canonical
tree now holds `b2d074d2df24`'s). The candidates are built into `candidates/` beside this file, because the cut
reads a candidate document by its repository path. Its gzipped output and text are copied into `readings/`,
the evidence a report is computed from.
"""
from __future__ import annotations

import datetime
import gzip
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parent
CAL = G0.parents[1]
ROOT = CAL.parents[1]
RESULTS = CAL / "results"
sys.path.insert(0, str(HERE))
import rule as R  # noqa: E402

SCRATCH = Path.home() / "vitrea-w49" / "w49a-g0-probes"          # renders: matrices and capture trees
CANDIDATES = HERE / "candidates"                                 # in the repository: the cut reads them by path
# The reference's captures: d0219cd684bf's tree, moved beside the canonical tree when b2d074d2df24 superseded it
# (W48 G2). The canonical tree lives in the main checkout, which a worktree shares through git's common dir.
MAIN = Path(subprocess.run(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], cwd=HERE,
                           capture_output=True, text=True, check=True).stdout.strip()).parent
REFERENCE_CAPTURES = MAIN / "packages" / "calibration" / "web-captures-superseded" / "d0219cd684bf"
SPECS = HERE / "specs"
READINGS = HERE / "readings"
BUILDER = G0 / "fit" / "build-candidate.ts"
CENSUS = RESULTS / "2026-10-02-w43-g3-refit" / "stage" / "census.py"
CUTS = RESULTS / "2026-10-06-w48-g0-declaration" / "cuts" / "cuts.py"
LOCK = Path("/tmp/w49-gpu.lock")
SETS = "calibration,validation,recorded,probe"
PLAYWRIGHT, CHROMIUM_REVISION, ENGINE_VERSION = "1.62.1", "1234", "151.0.7922.34"


class Refusal(SystemExit):
    pass


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def specs() -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text()) for p in sorted(SPECS.glob("*.json"))}


def scenes(label: str, scale: int) -> list[str]:
    pose = "rest" if label.startswith("p1-") else "inactive"
    return sorted(s for (sc, s), c in R.b2d074_cells().items()
                  if sc == scale and c["partition"] == "gate" and c["pose"] == pose)


def declared() -> None:
    got = subprocess.run([sys.executable, "-B", str(G0 / "declare.py"), "check"], cwd=G0, capture_output=True,
                         text=True)
    if got.returncode or "both parts hashed" not in got.stdout:
        raise Refusal(f"render: the declaration is not hashed and checked; nothing renders before it\n"
                      f"{got.stdout[-800:]}{got.stderr[-800:]}")


def census(label: str) -> bool:
    import importlib.util
    spec = importlib.util.spec_from_file_location("w43_census", CENSUS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    observation = module.observe()
    script = ("const p=require.resolve('@playwright/test/package.json');const v=require(p).version;"
              "const core=require.resolve('playwright-core/package.json',{paths:[require('path').dirname(p)]});"
              "const b=require(require('path').join(require('path').dirname(core),'browsers.json'));"
              "const c=b.browsers.find(x=>x.name==='chromium');"
              "console.log(JSON.stringify({playwright:v,revision:c.revision,browserVersion:c.browserVersion}))")
    found = json.loads(subprocess.run(["node", "-e", script], cwd=CAL, capture_output=True, text=True).stdout)
    pinned = (found["playwright"], found["revision"], found["browserVersion"]) == (
        PLAYWRIGHT, CHROMIUM_REVISION, ENGINE_VERSION) and not os.environ.get("PLAYWRIGHT_BROWSERS_PATH")
    passes = bool(observation["passes"]) and pinned
    entry = dict(label=label, at=observation["recordedAt"], passes=passes, refusals=observation["refusals"]
                 + ([] if pinned else ["browserNotPinned"]), pin=found,
                 refuse=[dict(pid=r["pid"], command=r["command"][:160], why=r["why"]) for r in observation["refuse"]],
                 annotate=[dict(pid=a["pid"], why=a["why"]) for a in observation["annotate"]])
    with (HERE / "census.jsonl").open("a") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    print(f"census {label}: {'passes' if passes else 'REFUSES'} {entry['refusals']}", flush=True)
    return passes


def build() -> int:
    for label, spec in specs().items():
        folder = CANDIDATES / label
        if folder.exists():
            if json.loads((folder / "spec.json").read_text()) != spec:
                raise Refusal(f"build: {folder} holds a different spec")
            continue
        got = subprocess.run(["pnpm", "exec", "tsx", str(BUILDER), str(SPECS / f"{label}.json")], cwd=CAL,
                             capture_output=True, text=True,
                             env={**os.environ, "W49A_CANDIDATE_ROOT": str(CANDIDATES)})
        if got.returncode:
            raise Refusal(f"build {label}: {got.stdout[-1500:]}{got.stderr[-1500:]}")
        (folder / "build.json").write_text(got.stdout)
        print(f"built {label}", flush=True)
    return 0


def render(label: str) -> int:
    declared()
    candidate = CANDIDATES / label / "candidate.json"
    if not candidate.exists():
        raise Refusal(f"render {label}: not built")
    worst = 0
    for scale in (1, 2):
        out = SCRATCH / "renders" / label / f"{scale}x"
        if (out / "matrix.json").exists():
            continue
        out.mkdir(parents=True, exist_ok=True)
        cells = scenes(label, scale)
        argv = ["pnpm", "run", "-s", "compare", "--", "--profile", R.PROFILES[scale], "--renderer", "webgpu",
                "--candidate-document", str(candidate), "--set", SETS, "--scene", ",".join(cells), "--alpha",
                "--write-partial", "--out-matrix", str(out / "matrix.json")]
        env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
        env.update(VITREA_WEB_CAPTURES=str(out / "web-captures"))
        while True:
            try:
                LOCK.mkdir()
                break
            except FileExistsError:
                time.sleep(3)
        try:
            if not census(f"{label} {scale}x"):
                print(f"render {label} {scale}x: the census refuses; nothing launched", flush=True)
                return 3
            started = now()
            with (out / "compare.log").open("w") as log:
                code = subprocess.run(argv, cwd=CAL, env=env, stdout=log, stderr=subprocess.STDOUT).returncode
        finally:
            LOCK.rmdir()
        record = dict(label=label, scale=scale, cells=len(cells), started=started, completed=now(), exit=code,
                      argv=[a if a != ",".join(cells) else f"<{len(cells)} scenes>" for a in argv])
        with (HERE / "runs.jsonl").open("a") as handle:
            handle.write(json.dumps(record) + "\n")
        print(f"render {label} {scale}x: exit {code}, {len(cells)} cells", flush=True)
        if code:
            (out / "matrix.json").rename(out / f"matrix.partial-{int(time.time())}.json") \
                if (out / "matrix.json").exists() else None
            worst = max(worst, code)
            continue
        rows = json.loads((out / "matrix.json").read_text())["cells"]
        measured = sorted(r["key"]["sceneId"] for r in rows)
        if measured != cells:
            raise Refusal(f"render {label} {scale}x: measured {len(measured)} rows, not the {len(cells)} cells "
                          f"planned: {sorted(set(cells) ^ set(measured))[:8]}")
    return worst


def read(label: str) -> int:
    READINGS.mkdir(exist_ok=True)
    candidate = CANDIDATES / label / "candidate.json"
    for scale in (1, 2):
        out = SCRATCH / "renders" / label / f"{scale}x"
        dest = READINGS / f"{label}-{scale}x.json.gz"
        if dest.exists():
            continue
        if not (out / "matrix.json").exists():
            raise Refusal(f"read {label} {scale}x: not rendered")
        argv = [sys.executable, "-B", str(CUTS), "--kind", "candidate", "--candidate-document", str(candidate),
                "--bed", str(out / "matrix.json"), "--captures", str(out / "web-captures"),
                "--reference-captures", str(REFERENCE_CAPTURES),
                "--out", str(out / "cut.json"), "--text", str(out / "cut.txt")]
        got = subprocess.run(argv, cwd=CUTS.parent, capture_output=True, text=True)
        if got.returncode:
            raise Refusal(f"read {label} {scale}x: cuts.py exit {got.returncode}: {got.stderr[-2000:]}")
        with gzip.open(dest, "wt") as f:
            f.write((out / "cut.json").read_text())
        shutil.copy(out / "cut.txt", READINGS / f"{label}-{scale}x.txt")
        print(f"read {label} {scale}x -> {dest.name}", flush=True)
    return 0


def t1_cells(label: str) -> list[dict]:
    cells = []
    for scale in (1, 2):
        cut = json.load(gzip.open(READINGS / f"{label}-{scale}x.json.gz"))
        cells += [c for c in cut["T1"]["cells"] if c["tier"] == "webgpu" and c["profile"] == R.PROFILES[scale]]
    return cells


def report() -> int:
    b2d = R.b2d074_cells()
    out, lines = {}, ["W49a G0 probe report (rule.py; part 1's probes read under part 2's rules)", ""]
    p1 = t1_cells("p1-d0219-top160")
    p1_predicted = {1: (0.0228, 0.0297, 0.0270), 2: (0.0283, 0.0347, 0.0287)}
    thick = ("checkerboard-32__rrect-lg__rest", "checkerboard-64__rrect-lg__rest", "hc-text-28__rrect-lg__rest")
    lines.append("P1: d0219cd684bf with only the active span tops at 160 (F2 by render; within B of the prediction)")
    out["P1"] = []
    for scale in (1, 2):
        for scene, predicted in zip(thick, p1_predicted[scale]):
            c = next(c for c in p1 if c["scale"] == scale and c["scene"] == scene)
            holds = abs(c["candidate"] - predicted) <= c["B"]
            out["P1"].append(dict(scale=scale, scene=scene, read=c["candidate"], predicted=predicted, B=c["B"],
                                  d0219=c["reference"], native=c["native"], holds=holds))
            lines.append(f"  {scale}x {scene:36} read {c['candidate']:.4f} predicted {predicted:.4f} "
                         f"(B {c['B']:.4f}; d0219 {c['reference']:.4f}, native {c['native']:.4f}) "
                         f"{'holds' if holds else 'MISSES'}")
    points = {label: (spec["overrides"]["receded.dark"]["tintAlphaFar1x"], t1_cells(label))
              for label, spec in specs().items() if label.startswith("p2-")}
    selection = R.select(points, b2d)
    out["P2"] = selection
    lines += ["", "P2: b2d074d2df24 with the receded far delta (family R); X74, then DL2 per point, then DL4"]
    for scale, s in selection["scales"].items():
        auth = s["authority"]
        lines.append(f"  {scale}: X74 reach {len(auth['reach'])} cells {auth['reach']}; outside "
                     f"{len(auth['outside'])} ({sum(1 for o in auth['outside'] if 'predicted' in o['reason'])} "
                     f"predicted); control: {auth['verdict']}")
        for o in auth["outside"]:
            if "UNEXPLAINED" in o["reason"]:
                lines.append(f"      outside, UNEXPLAINED: {o['scene']}")
        for p in s["points"]:
            obj = "n/a" if p["objective"] is None else f"{p['objective']:.4f}"
            lines.append(f"    far {p['far']:+.2f}: {'MEETS DL2' if p['meets'] else 'fails'}; objective {obj}"
                         + ("" if p["meets"] else "; " + "; ".join(p["failures"] + [f"unread {u}" for u in p["unread"]])))
        lines.append(f"    selected: {s['selected']} ({s['why']})")
    lines += ["", f"VERDICT: {selection['verdict']}" + (f" {selection['landing']}" if selection["landing"] else "")]
    (HERE / "report.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    (HERE / "report.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


def main(argv) -> int:
    verb = argv[1] if len(argv) > 1 else ""
    if verb == "build":
        return build()
    if verb == "render":
        return render(argv[2])
    if verb == "read":
        return read(argv[2])
    if verb == "report":
        return report()
    raise SystemExit(__doc__)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
