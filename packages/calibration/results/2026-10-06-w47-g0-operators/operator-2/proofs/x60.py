#!/usr/bin/env python3.12
"""X60: the frozen evidence paths are byte-unchanged from af8cf7e5f; scratch archives are not canonical trees."""
from pathlib import Path
import json,subprocess
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[5]
changed=subprocess.check_output(['git','diff','af8cf7e5f','--name-only'],cwd=ROOT,text=True).splitlines()
frozenPrefixes=(
 'packages/calibration/profiles/', 'packages/calibration/results/generations/',
 'packages/calibration/web-captures/', 'packages/calibration/web-captures-superseded/',
 'packages/renderer-webgpu/e2e/golden/', 'packages/renderer-webgpu/e2e/goldens/',
 'apps/reference-apple/fixtures/',
)
historicalPrefixes=('packages/calibration/results/2026-10-03-w44',
 'packages/calibration/results/2026-10-03-w45','packages/calibration/results/2026-10-04-w45',
 'packages/calibration/results/2026-10-05-w46')
violations=[p for p in changed if p=='packages/calibration/results/matrix.json'
 or p.startswith(frozenPrefixes) or p.startswith(historicalPrefixes)]
report=dict(base='af8cf7e5f',checkedFrozenPrefixes=frozenPrefixes,
 checkedHistoricalPrefixes=historicalPrefixes,changedFrozenPaths=violations,
 note='New diagnostic/renders/.../web-captures paths are archived scratch inputs, not the canonical capture tree.')
if violations:raise SystemExit(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
