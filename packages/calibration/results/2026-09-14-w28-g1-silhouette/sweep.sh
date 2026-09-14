#!/bin/bash
# One capture process at a time; batches resume by completed matrix, never by rereading a cell.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$HERE/../../../.." && pwd)"
: "${VITREA_WEB_CAPTURES:?Name a scratch capture directory}"
START="${1:-0}"
COUNT="${2:-3}"
PLAN="$HERE/sweep-jobs.json"
python3 - "$HERE" "$PLAN" <<'PY'
import json, pathlib, sys
here, path = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
if not path.exists():
    proposals = json.loads((here / 'fit-model-proposals.json').read_text())['proposals']
    jobs = []
    for scheme in ['light', 'dark']:
        for baseline in ['baseline-source', 'baseline-silhouette']:
            jobs.append({'scheme': scheme, 'label': f'{scheme}-{baseline}', 'patch': baseline})
        jobs.extend({'scheme': scheme, 'label': row['name'], 'patch': row['name']}
                    for row in proposals if row['scheme'] == scheme)
    path.write_text(json.dumps(jobs, indent=2) + '\n')
PY
while IFS=$'\t' read -r SCHEME LABEL PATCH; do
  if [[ -f "$HERE/sweep-matrices/$LABEL.json" ]]; then
    echo "Refusing to reuse an existing rung without checking its completeness: $LABEL" >&2
    exit 1
  fi
  pnpm --dir "$ROOT" --filter @vitrea/calibration --fail-if-no-match exec tsx \
    results/2026-09-14-w28-g1-silhouette/fit-read.ts \
    --scheme "$SCHEME" --label "$LABEL" --patch "$HERE/sweeps/$PATCH.json" \
    > "$HERE/sweep-$LABEL.out" 2>&1
  echo "Completed $LABEL"
done < <(python3 - "$PLAN" "$START" "$COUNT" <<'PY'
import json, sys
jobs = json.load(open(sys.argv[1]))
for row in jobs[int(sys.argv[2]):int(sys.argv[2]) + int(sys.argv[3])]:
    print(row['scheme'], row['label'], row['patch'], sep='\t')
PY
)
