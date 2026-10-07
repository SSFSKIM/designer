#!/usr/bin/env python3.12
"""W48 G2: close-checks.txt from the chain's own logs (claims §5.214 §9; W45 G2's summarise.py, copied).

    python3.12 -B summarise.py

One line per step: its exit code from chain-status.txt and the line(s) of its log that carry the
count, so the record cannot say more than the run did.
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ANSI = re.compile(r"\x1b\[[0-9;]*m")
PICK = {
    "freeze-open": r"intact|FAIL", "freeze-close": r"intact|FAIL",
    "x41-open": r"intact|FAIL", "x41-close": r"intact|FAIL",
    "capture-tree": r"totals|VERDICT", "capture-tree-close": r"totals|VERDICT",
    "build": r"^ERR|error TS", "digests": r"all ten|disagree",
    "lint": r"problems?\b|ERR_", "eslint-root": r"problems?\b|ERR_",
    "units": r"^(packages|apps)/\S+ test:\s+Tests\s|Test Files .*failed|ERR_",
    "goldens": r"\d+ (passed|failed|skipped|flaky)", "gpu": r"\d+ (passed|failed|skipped|flaky)",
    "platform-web": r"\d+ (passed|failed|skipped|flaky)", "react-e2e": r"\d+ (passed|failed|skipped|flaky)",
    "demo-e2e": r"\d+ (passed|failed|skipped|flaky)",
    "declare-check": r"^check:|does not pass|mismatch", "declare-check-fit": r"^check-fit:|does not pass|mismatch",
    "declaration-witness": r"with those bytes|committed on|removed",
}


def main() -> int:
    status = {}
    status_lines = (HERE / "chain-status.txt").read_text().splitlines()
    for line in status_lines:
        m = re.match(r"(\S+) exit=(\d+)$", line)
        if m:
            status[m[1]] = int(m[2])
    invocations = (HERE / "chain-invocations.txt").read_text().splitlines()
    head = invocations[0].split(" at ")[-1] if invocations else "?"
    out = [f"W48 G2 close checks: the c9d chain at {head} (chain.sh; one log per step), each gated on its own exit code",
           f"invocations: {len(invocations)} ({'; '.join(invocations)})", ""]
    for step, code in status.items():
        log = HERE / f"chain-{step}.txt"
        lines = [ANSI.sub("", l).strip() for l in log.read_text(errors="replace").splitlines()] if log.exists() else []
        picked = [l for l in lines if re.search(PICK.get(step, r"$^"), l)]
        out.append(f"{step}: exit {code}")
        out += [f"    {l}" for l in picked[-12:]]
        out += [f"    {l}" for l in status_lines if l.startswith(f"{step} load average")]
    out.append("")
    out.append("the chain's status record, whole (every halt, re-invocation and load reading in order):")
    out += [f"    {l}" for l in status_lines]
    out.append("")
    out.append("git status at the summary: " + (subprocess.run(["git", "status", "--short"], capture_output=True,
                                                                text=True, cwd=HERE).stdout.strip() or "clean"))
    (HERE / "close-checks.txt").write_text("\n".join(out) + "\n")
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
