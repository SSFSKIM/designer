"""Reproduce the per-engine counts from the retained Playwright list logs."""
import collections
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ANSI = re.compile(r"\x1b\[[0-9;]*m")
CASE = re.compile(r"^\s*([✓✘-])\s+\d+\s+\[([^\]]+)\]", re.M)
NAMES = [
    "activation-discovery", "platform-web", "renderer-goldens", "platform-web-final",
    "react", "demo", "react-activation-final", "demo-stage-final", "react-activation-endpoints",
]
results = {}
for name in NAMES:
    path = HERE / f"{name}.txt"
    text = ANSI.sub("", path.read_text())
    counts = collections.defaultdict(lambda: {"passed": 0, "failed": 0, "skipped": 0})
    for mark, engine in CASE.findall(text):
        status = "passed" if mark == "✓" else "failed" if mark == "✘" else "skipped"
        counts[engine][status] += 1
    results[name] = {"engines": dict(counts), "logSha256": hashlib.sha256(path.read_bytes()).hexdigest()}

identity = json.loads((HERE / "capture-identity.json").read_text())
summary = {
    "browserRuns": results,
    "captureIdentity": {"pairs": len(identity["rows"]),
                        "byteIdentical": sum(row["byteIdentical"] for row in identity["rows"])},
    "note": "First-run failures remain separate from targeted corrections; no summed result is presented as a fresh full-suite run.",
}
(HERE / "verification.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
