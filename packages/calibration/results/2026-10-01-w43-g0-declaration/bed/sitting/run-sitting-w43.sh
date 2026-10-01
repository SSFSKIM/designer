#!/bin/bash
# W43 capture entry point (charter G1a, G1b). Derived from W42's run-sitting-w42.sh. No
# capture.sh auto-build path: the sitting runs only the pinned W39 side bundle, and a rebuild
# is a new pin and a new grant (X4').
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3.12 "$HERE/sitting.py" "$@"
