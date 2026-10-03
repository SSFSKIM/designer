"""W45 G0 (a): the bench rows before and after the operator (charter Risks, "frame time"; §5.205).

Reads `before/bench-run{1,2,3}.txt` and `after/bench-run{1,2,3}.txt` (each one `test:bench` launch,
60 interleaved rounds per config, `apple/metal-3`, timestamp-query) and tables the mobile row, the
two second-tap rows and the ordering control: the frame's GPU median and the optics pass's, each
also as a ratio to the same run's control, because two launches measure the GPU's clock state at
least as much as the renderer (the bench file's own methodology note).

    python3.12 -B bench.py  →  bench.txt
"""
from __future__ import annotations

import re
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = ["mobile-390x844@3", "mobile-390x844@3 second-tap", "mobile-390x844@3 second-tap graded",
        "mobile-390x844@3 control"]


def read(path: Path) -> dict:
    out = {}
    for line in path.read_text().splitlines():
        m = re.match(r"(.+?): gpu\(median\)=([\d.]+)ms .*optics=([\d.]+)", line)
        if m:
            out[m.group(1)] = dict(gpu=float(m.group(2)), optics=float(m.group(3)))
    return out


lines = [f"{'side':6s} {'run':3s} {'row':36s} {'gpu ms':>7s} {'gpu/ctl':>7s} {'optics ms':>9s} {'opt/ctl':>7s}"]
summary = {}
for side in ("before", "after"):
    for run in (1, 2, 3):
        rows = read(HERE / side / f"bench-run{run}.txt")
        control = rows["mobile-390x844@3 control"]
        for row in ROWS:
            r = rows[row]
            g, o = r["gpu"] / control["gpu"], r["optics"] / control["optics"]
            summary.setdefault((side, row), []).append((r["gpu"], g, r["optics"], o))
            lines.append(f"{side:6s} {run:<3d} {row:36s} {r['gpu']:7.3f} {g:7.3f} {r['optics']:9.3f} {o:7.3f}")
lines.append("")
lines.append("medians over the three launches (ratio = row / the same launch's control):")
for row in ROWS:
    for side in ("before", "after"):
        v = summary[(side, row)]
        lines.append(f"  {side:6s} {row:36s} gpu {statistics.median(x[0] for x in v):.3f} "
                     f"(×{statistics.median(x[1] for x in v):.3f})  optics {statistics.median(x[2] for x in v):.3f} "
                     f"(×{statistics.median(x[3] for x in v):.3f})")
(HERE / "bench.txt").write_text("\n".join(lines) + "\n")
print("\n".join(lines))
