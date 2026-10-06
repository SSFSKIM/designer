"""W47 G0: the classifying web census and the browser pin, before every browser launch (§5.201 §21's
ruling; the W46 brief: refuse on Reduce Transparency, Increase Contrast, a real capture process, or
a Playwright and Chromium that are not the pinned ones). W46's `census-gate.py`, ported unchanged but for
this paragraph and the binding it imports (W47's `bindings.py`), so its log is W47's `census.jsonl`.

Reads W43 G3 (ii)'s `stage/census.py` by path (pinned in `bindings.SHARED`), adds the pin check, appends
the observation to `census.jsonl` beside this file with the label of the launch it gates, and exits 1
when either refuses — so a shell caller gates the launch on this command's own exit code.

**The pin.** `compare` launches the calibration package's own `@playwright/test`, whose
`playwright-core/browsers.json` names the Chromium revision it drives. The pin is what the published
dark 0.25 generation was rendered with: `@playwright/test` 1.62.1 (the workspace catalog and the
lockfile) driving Chromium revision 1234, browser version 151.0.7922.34 — the `engineVersion` every
`d0219cd684bf` row carries — installed under the Playwright cache. Every reader of a W47 render
checks the rows' `engineVersion` against the same version afterwards (`pinned_engine`).

    python3.12 -B census-gate.py <label>
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import bindings as W  # noqa: E402

PLAYWRIGHT = "1.62.1"
CHROMIUM_REVISION = "1234"
ENGINE_VERSION = "151.0.7922.34"
CACHE = Path.home() / "Library" / "Caches" / "ms-playwright"


def pin() -> dict:
    """The Playwright the calibration package resolves and the Chromium it drives, against the pin."""
    script = ("const p=require.resolve('@playwright/test/package.json');"
              "const v=require(p).version;"
              "const core=require.resolve('playwright-core/package.json',{paths:[require('path').dirname(p)]});"
              "const b=require(require('path').join(require('path').dirname(core),'browsers.json'));"
              "const c=b.browsers.find(x=>x.name==='chromium');"
              "console.log(JSON.stringify({playwright:v,revision:c.revision,browserVersion:c.browserVersion}))")
    got = subprocess.run(["node", "-e", script], cwd=W.CAL, capture_output=True, text=True)
    if got.returncode:
        return dict(ok=False, why=f"node could not resolve the package's Playwright: {got.stderr[-300:]}")
    found = json.loads(got.stdout)
    installed = (CACHE / f"chromium-{found['revision']}").is_dir()
    why = []
    if found["playwright"] != PLAYWRIGHT:
        why.append(f"Playwright {found['playwright']}, not the pinned {PLAYWRIGHT}")
    if found["revision"] != CHROMIUM_REVISION or found["browserVersion"] != ENGINE_VERSION:
        why.append(f"Chromium {found['revision']} ({found['browserVersion']}), not the pinned "
                   f"{CHROMIUM_REVISION} ({ENGINE_VERSION})")
    if not installed:
        why.append(f"chromium-{found['revision']} is not installed under {CACHE} (no install in this wave)")
    if os.environ.get("PLAYWRIGHT_BROWSERS_PATH"):
        why.append("PLAYWRIGHT_BROWSERS_PATH is set; the pinned cache is the default one")
    return dict(ok=not why, why=why, **found, installed=installed)


def pinned_engine(rows) -> list[str]:
    """Every row whose engine is not the pinned Chromium (a reader's after-the-fact check)."""
    return [f"{r['key']['profileKey']} {r['key']['sceneId']}: {r['key']['web'].get('engine')} "
            f"{r['key']['web'].get('engineVersion')}" for r in rows
            if (r["key"]["web"].get("engine"), r["key"]["web"].get("engineVersion")) != ("chromium", ENGINE_VERSION)]


def main() -> int:
    label = sys.argv[1] if len(sys.argv) > 1 else "unlabelled"
    observation = W.census().observe()
    pinned = pin()
    passes = observation["passes"] and pinned["ok"]
    refusals = observation["refusals"] + ([] if pinned["ok"] else ["browserNotPinned"])
    entry = dict(label=label, at=observation["recordedAt"], passes=passes, refusals=refusals,
                 refuse=observation["refuse"], pin=pinned,
                 annotate=[dict(pid=a["pid"], why=a["why"]) for a in observation["annotate"]])
    with (HERE / "census.jsonl").open("a") as handle:
        handle.write(json.dumps(entry, sort_keys=True) + "\n")
    print(f"census {label}: {'passes' if passes else 'REFUSES'} "
          f"({len(observation['annotate'])} annotated, refusals {refusals}"
          + ("" if pinned["ok"] else f"; pin: {'; '.join(pinned['why'])}") + ")")
    return 0 if passes else 1


if __name__ == "__main__":
    sys.exit(main())
