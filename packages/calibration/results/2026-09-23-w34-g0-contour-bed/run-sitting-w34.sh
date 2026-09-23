#!/bin/bash
# W34 capture entry point, §5.174 clauses 2–3 and 7. No capture.sh auto-build path.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$HERE/sitting.py" "$@"
