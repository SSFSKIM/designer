#!/usr/bin/env python3
"""W17 G0 (b) — the analytic check's table, as text beside the JSON `analytic.ts` writes.

Three columns of model against one column of render: the composite as `root.ts`'s own chain
computes it, the same composite in the SHADER's order, and that plus the inner shadow the mirror
does not carry. The author-tinted cells are dropped, because this model does not carry the seed's
opaque layer (W10) and reporting a 0.4 residual against a model that was never asked to include it
would be noise in the table rather than information.
"""
import json
import sys
from pathlib import Path

rows = [r for r in json.loads(Path(sys.argv[1]).read_text()) if "-tint" not in r["sceneId"]]
print(f"{'profile':>8} {'scene':<36} {'declined':>9} {'tierOrder':>10} {'resid':>8} "
      f"{'shaderOrder':>12} {'resid':>8} {'+innerShadow':>13} {'resid':>8}")
for r in rows:
    p = r["profileKey"].replace("apple-macos-26.5-", "").replace("-standard", "")
    print(f"{p:>8} {r['sceneId']:<36} {r['allDeclinedRendered']:9.4f} "
          f"{r['analyticAtSurfaceBackdrop']:10.4f} {r['residualAtSurfaceBackdrop']:+8.4f} "
          f"{r['shaderOrderAnalytic']:12.4f} {r['shaderOrderResidual']:+8.4f} "
          f"{r['shaderOrderWithInnerShadow']:13.4f} {r['shaderOrderWithInnerShadowResidual']:+8.4f}")
worst = max(rows, key=lambda r: abs(r["shaderOrderWithInnerShadowResidual"]))
over = [r for r in rows if abs(r["shaderOrderWithInnerShadowResidual"]) > 0.005]
print(f"{len(rows)} untinted cells; worst {worst['shaderOrderWithInnerShadowResidual']:+.4f} on "
      f"{worst['profileKey']} {worst['sceneId']}; {len(over)} over 0.005")
