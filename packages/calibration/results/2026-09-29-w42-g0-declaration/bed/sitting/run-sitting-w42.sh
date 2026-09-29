#!/bin/bash
# W42 capture entry point (charter clause 4; G1). Derived from W39's run-sitting-w39.sh. No
# capture.sh auto-build path: the sitting runs only the pinned W39 side bundle, and a rebuild
# is a new pin and a new grant.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3.12 "$HERE/sitting.py" "$@"
