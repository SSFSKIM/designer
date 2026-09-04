#!/usr/bin/env python3
"""W17 G0 (c) — the closed form's table, as text beside the JSON `closed-form.ts` writes."""
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text())
print(f"{'profile':>8} {'scene':<36} {'rim pred':>9} {'rim meas':>9} {'resid':>8} "
      f"{'hl pred':>8} {'hl meas':>8} {'resid':>8} {'lens meas':>10} {'lift meas':>10} "
      f"{'whole pred':>11} {'whole meas':>11} {'resid':>8}")
for r in data["rows"]:
    p = r["profileKey"].replace("apple-macos-26.5-", "").replace("-standard", "")
    c, m = r["closedFormAsRastered"], r["measured"]
    print(f"{p:>8} {r['sceneId']:<36} {c['rim']:+9.5f} {m['rim']:+9.5f} {r['residual']['rim']:+8.5f} "
          f"{c['highlight']:+8.5f} {m['highlight']:+8.5f} {r['residual']['highlight']:+8.5f} "
          f"{m['lens']:+10.5f} {m['lift']:+10.5f} {r['predictedWhole']:+11.5f} "
          f"{m['whole']:+11.5f} {r['residualWhole']:+8.5f}")
worst = max(data["rows"], key=lambda r: abs(r["residualWhole"]))
print(f"{len(data['rows'])} cells, {len(data['skipped'])} skipped; worst whole residual "
      f"{worst['residualWhole']:+.5f} on {worst['profileKey']} {worst['sceneId']}")
