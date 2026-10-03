#!/usr/bin/env python3.12
"""W45 G0 (e): the ladders, built, rendered and read under the hashed protocol (charter clause 4).
W44 G0's ladder driver (`results/2026-10-03-w44-g0-declaration/ladders/ladder.py`), ported for
W45's protocol (X58); W44's committed copy is untouched.

    python3.12 -B ladder.py plan             # every rung: label, ladder, overrides; contents rendered once
    python3.12 -B ladder.py build [bases]    # build every rung's candidate (fit/build-candidate.ts)
    python3.12 -B ladder.py render [LABEL..] # render the contents, 2x then 1x, one compare per profile
    python3.12 -B ladder.py read             # results.json and results.txt (read.py)

Everything follows `protocol.json`, which part 1 pins. `build bases` builds only the protocol's
bases (control and the joint point), which part 1's check reads before the hash; `render` refuses
unless part 1 is hashed and `declare.py check` passes, and refuses a fixed cell that is not a
declared `__rest` cell, is a referee, is a holdout scene, or is a probe scene outside the
planner's pre-gate whitelist. Rungs of ONE content (their four endpoint digests equal) render once,
under the first label in protocol order (W44 G1's tracker note). Each launch runs through
`../with-gpu.sh` (the GPU lock and the classifying web census, §5.201 §21) and the calibration
package's own `compare` script, so the Playwright and Chromium it launches are the package's
pinned ones; `--alpha` is passed, so a ladder row carries every field a stage row does. Every launch
is logged in `runs.jsonl` with its compare log under `logs/`; the matrices and PNGs stay in scratch at
`~/vitrea-w45/g0-ladders/<label>/`.
"""
from __future__ import annotations

import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
CAL = EVIDENCE.parents[1]
ROOT = CAL.parent.parent
SCRATCH = Path.home() / "vitrea-w45" / "g0-ladders"
PROTOCOL = json.loads((HERE / "protocol.json").read_text())
CANDIDATES = HERE / "candidates"
BUILDER = EVIDENCE / "fit" / "build-candidate.ts"
TSX = CAL / "node_modules" / ".bin" / "tsx"
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402
sys.path.append(str(B.G0 / "referees"))
import plan  # noqa: E402


def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def log(row):
    with (HERE / "runs.jsonl").open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def fmt(v) -> str:
    return f"{v:g}"


def merged(*layers: dict) -> dict:
    out: dict = {}
    for layer in layers:
        for slot, leaves in layer.items():
            out.setdefault(slot, {}).update(leaves)
    return out


def rungs() -> list[dict]:
    """Every rung the protocol declares, bases first: label, ladder, overrides, value, reference label."""
    bases = PROTOCOL["bases"]
    out = [dict(label=b["label"], ladder="base", base=name, overrides=b["overrides"], value=None, against=None)
           for name, b in bases.items()]
    for lad in PROTOCOL["ladders"]:
        base = bases[lad["base"]]
        slot = lad["slot"]
        fixed = {slot: lad.get("fixed", {})}
        if lad["id"] == "v":
            for lever in lad["levers"]:
                label = "v-" + "-".join(f"{k.removeprefix('size')}-{fmt(v)}" for k, v in lever["set"].items())
                against = None
                if "against" in lever:
                    against = "v-" + "-".join(f"{k.removeprefix('size')}-{fmt(v)}"
                                              for k, v in lever["against"].items())
                out.append(dict(label=label.lower(), ladder="v", base=lad["base"], lever=lever["lever"],
                                overrides=merged(base["overrides"], {slot: lever["set"]}), value=lever["set"],
                                against=against.lower() if against else base["label"]))
            continue
        if "grid" in lad:
            leaves = list(lad["grid"])
            points = [[]]
            for leaf in leaves:
                points = [p + [x] for p in points for x in lad["grid"][leaf]]
            for p in points:
                label = f"{lad['id']}-" + "-".join(f"{fmt(x)}" for x in p)
                out.append(dict(label=label, ladder=lad["id"], base=lad["base"], value=dict(zip(leaves, p)),
                                overrides=merged(base["overrides"], fixed, {slot: dict(zip(leaves, p))}),
                                against=base["label"]))
            continue
        ats = [dict(zip(lad.get("at", {}), combo)) for combo in
               ([[]] if not lad.get("at") else [[x] for x in next(iter(lad["at"].values()))])]
        for at in ats:
            for v in lad["values"]:
                setv = {leaf: v for leaf in lad["leaves"]}
                label = f"{lad['id']}-" + "-".join(f"{fmt(x)}" for x in [*at.values(), v])
                out.append(dict(label=label, ladder=lad["id"], base=lad["base"], value=v, at=at,
                                overrides=merged(base["overrides"], fixed, {slot: at}, {slot: setv}),
                                against=base["label"]))
    seen = {}
    for r in out:
        if r["label"] in seen:
            raise SystemExit(f"two rungs share the label {r['label']}")
        seen[r["label"]] = r
    return out


def build(only_bases: bool = False) -> int:
    for r in rungs():
        if only_bases and r["ladder"] != "base":
            continue
        folder = CANDIDATES / r["label"]
        if folder.exists():
            print("built already", r["label"])
            continue
        spec = dict(label=r["label"], note=f"W45 ladder {r['ladder']} rung {r['value']}",
                    overrides=r["overrides"])
        path = SCRATCH / "specs" / f"{r['label']}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(spec, indent=2) + "\n")
        got = subprocess.run([str(TSX), str(BUILDER), str(path)], cwd=CAL, capture_output=True, text=True,
                             env=dict(os.environ, W45_CANDIDATE_ROOT=str(CANDIDATES)))
        print(r["label"], "exit", got.returncode, got.stderr[-400:] if got.returncode else "", flush=True)
        if got.returncode:
            return got.returncode
    return 0


def content(label: str) -> tuple:
    """A built candidate's content: its four endpoint digests."""
    body = json.loads((CANDIDATES / label / "candidate.json").read_text())
    return tuple(json.loads((CANDIDATES / label / e["path"]).read_text())["resolvedMaterialSha256"]
                 for _, e in sorted(body["endpoints"].items()))


def rendered_as() -> dict:
    """label -> the label whose render it reads (the first label of its content, in protocol order)."""
    first, out = {}, {}
    for r in rungs():
        key = content(r["label"])
        first.setdefault(key, r["label"])
        out[r["label"]] = first[key]
    return out


def admitted_cells() -> list[str]:
    """The fixed cells, each checked: a declared `__rest` cell, not a referee, not holdout, a probe
    cell inside the planner's pre-gate whitelist (the loader's intersection)."""
    manifest = plan.load_manifest()
    held = plan.referee_cells(manifest)
    scenes = plan.load_scenes()
    pregate = set(plan.lists(manifest)["pregateProbe"]["scenes"])
    cells = PROTOCOL["fixedCells"]["scenes"]
    for sid in cells:
        role = scenes["role"].get(sid)
        why = ("not a __rest cell" if not sid.endswith("__rest") else
               "a holdout scene" if role == "holdout" else
               "a referee" if any((p, sid) in held for p in PROTOCOL["profiles"]) else
               f"in no set the ladders render ({role})" if role not in PROTOCOL["fixedCells"]["sets"].split(",") else
               "a probe scene outside the pre-gate whitelist" if role == "probe" and sid not in pregate else
               "undeclared" if any(sid not in scenes["declared"][p] for p in PROTOCOL["profiles"]) else None)
        if why:
            raise SystemExit(f"ladder REFUSES: {sid} is {why}")
    return cells


def preflight():
    if not (EVIDENCE / "declaration.sha256").exists():
        raise SystemExit("render REFUSES: part 1 is not hashed")
    got = subprocess.run([sys.executable, "-B", str(EVIDENCE / "declare.py"), "check"], capture_output=True,
                         text=True)
    if got.returncode:
        raise SystemExit("render REFUSES: declare.py check fails:\n" + got.stdout[-2000:])
    admitted_cells()


def render(labels: list[str]) -> int:
    preflight()
    cells = admitted_cells()
    renders = sorted(set(rendered_as().values()), key=[r["label"] for r in rungs()].index)
    todo = [label for label in renders if not labels or label in labels]
    done = [json.loads(ln) for ln in (HERE / "runs.jsonl").read_text().splitlines()] \
        if (HERE / "runs.jsonl").exists() else []
    (HERE / "logs").mkdir(exist_ok=True)
    for label in todo:
        candidate = CANDIDATES / label / "candidate.json"
        for profile in PROTOCOL["profiles"]:
            run_label = f"{label}/{profile}"
            if any(x.get("label") == run_label and x.get("exitCode") == 0 for x in done):
                continue
            attempt = 0
            logfile = HERE / "logs" / (run_label.replace("/", "__") + ".txt")
            while logfile.exists():
                attempt += 1
                logfile = HERE / "logs" / (run_label.replace("/", "__") + f".relaunch-{attempt}.txt")
            out = SCRATCH / label
            out.mkdir(parents=True, exist_ok=True)
            argv = ["pnpm", "run", "-s", "compare", "--", "--profile", profile, "--renderer", PROTOCOL["tier"],
                    "--candidate-document", str(candidate.relative_to(CAL)),
                    "--set", PROTOCOL["fixedCells"]["sets"], "--scene", ",".join(cells),
                    "--alpha", "--write-partial", "--out-matrix", str(out / "matrix.json")]
            env = {k: v for k, v in os.environ.items() if not k.startswith("VITREA_")}
            env.update(VITREA_WEB_CAPTURES=str(out / "web-captures"))
            started = now()
            log(dict(label=run_label, started=started, argv=argv, attempt=attempt))
            with logfile.open("x") as f:
                result = subprocess.run([str(EVIDENCE / "with-gpu.sh"), f"ladder {run_label}", *argv],
                                        cwd=CAL, env=env, stdout=f, stderr=subprocess.STDOUT)
            log(dict(label=run_label, started=started, completed=now(), exitCode=result.returncode))
            print(run_label, "exit", result.returncode, flush=True)
            if result.returncode != 0:
                return result.returncode
    return 0


def main() -> int:
    verb = sys.argv[1] if len(sys.argv) > 1 else ""
    if verb == "plan":
        rs = rungs()
        renders = rendered_as() if all((CANDIDATES / r["label"] / "candidate.json").exists() for r in rs) else {}
        for r in rs:
            shared = renders.get(r["label"])
            note = "" if not renders else ("" if shared == r["label"] else f"  (renders as {shared})")
            print(f"{r['label']:<34} {r['ladder']:<5} {json.dumps(r['overrides'])}{note}")
        print(len(rs), "rungs", f"{len(set(renders.values()))} contents" if renders else "(not all built)")
        return 0
    if verb == "build":
        return build(only_bases=sys.argv[2:] == ["bases"])
    if verb == "render":
        return render(sys.argv[2:])
    if verb == "read":
        import read  # noqa: E402  (beside this file)
        return read.main()
    raise SystemExit(__doc__)


if __name__ == "__main__":
    raise SystemExit(main())
