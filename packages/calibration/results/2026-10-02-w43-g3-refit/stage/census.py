"""W43 G3 (ii): the machine read before every WEB pass, under the coordinator's census ruling.

W41's X6 observer (`results/2026-09-27-w41-g1-identification/x6/observe.py`) is read whole and
logged: the slider, Reduce Transparency, Increase Contrast, HID idle and its all-names census of
foreign processes (W39's pattern, the launching chain excluded). A web pass then REFUSES on:
  - Reduce Transparency or Increase Contrast not 0 (they reach the page through the browser);
  - a real capture process: a Playwright-launched Chromium or headless shell, a Playwright-launched
    Google Chrome (automation flags on its command line), another capture-web or compare run,
    VitreaReference, or a Playwright CLI while any such browser is up.
It ANNOTATES, and does not refuse on, the user's own Google Chrome and its helpers (no automation
flag on any Chrome main process) and a Playwright CLI relay that owns no browser.

The ruling (the coordinator, 2026-10-02, during G3 (ii)): the declared zero-foreign-process fact
guards native captures, which a foreground browser can steal activation from; a headless
Chromium render has no activation to lose, and the pre-fit's 610 of 610 byte-identical rows
against the canonical 0.5 tree were themselves rendered on a machine with other processes
present. A stated deviation from the all-names census, recorded in §5.201's close notes.
"""
from __future__ import annotations

import importlib.util
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[2]
_spec = importlib.util.spec_from_file_location(
    "w41_x6", CAL / "results/2026-09-27-w41-g1-identification/x6/observe.py")
x6 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(x6)

AUTOMATION = re.compile(r"--enable-automation|--remote-debugging-pipe|playwright_chrom|ms-playwright")
CHROME_MAIN = re.compile(r"Google Chrome\.app/Contents/MacOS/Google Chrome(\s|$)")
CAPTURE = re.compile(r"Chromium|headless[-_ ]shell|chrome-headless|compare\.ts|capture-web|VitreaReference")
PLAYWRIGHT_CLI = re.compile(r"@playwright/cli|playwright/cli\.js|playwright-cli")


def classify(processes: list) -> dict:
    """Split W41's foreign list into what refuses a web pass and what is only annotated."""
    commands = [(row[0], row[2]) for row in processes]
    automated_chrome = any(CHROME_MAIN.search(c) and AUTOMATION.search(c) for _, c in commands)
    browser_up = automated_chrome or any(CAPTURE.search(c) and "compare" not in c and
                                         "capture-web" not in c for _, c in commands)
    refuse, annotate = [], []
    for pid, command in commands:
        entry = dict(pid=pid, command=command[:200])
        if CAPTURE.search(command):
            refuse.append({**entry, "why": "a capture process"})
        elif "Google Chrome" in command or "Chrome Helper" in command:
            if automated_chrome:
                refuse.append({**entry, "why": "a Playwright-launched Google Chrome (automation flags)"})
            else:
                annotate.append({**entry, "why": "the user's own Google Chrome (no automation flag)"})
        elif PLAYWRIGHT_CLI.search(command) or "playwright" in command.lower():
            if browser_up:
                refuse.append({**entry, "why": "a Playwright CLI while a Playwright browser is up"})
            else:
                annotate.append({**entry, "why": "a Playwright CLI relay that owns no browser"})
        else:
            refuse.append({**entry, "why": "matched the all-names census and no ruling admits it"})
    return dict(refuse=refuse, annotate=annotate)


def observe() -> dict:
    observation = x6.observe()
    verdict = observation["verdict"]
    split = classify(observation["foreignProcesses"])
    refusals = [fact for fact in ("reduceTransparency", "increaseContrast")
                if not verdict["facts"].get(fact)]
    if not observation["processCensus"]["usable"]:
        refusals.append("processCensusUnusable")
    if split["refuse"]:
        refusals.append("captureProcessPresent")
    return dict(recordedAt=observation["recordedAt"], x6=verdict, refuse=split["refuse"],
                annotate=split["annotate"], refusals=refusals, passes=not refusals)
