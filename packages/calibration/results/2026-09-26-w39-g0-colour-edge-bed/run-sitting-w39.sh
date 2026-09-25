#!/bin/bash
# W39 capture entry point (c9a §5.184; charter clauses 4-5). Derived from W34's
# run-sitting-w34.sh. No capture.sh auto-build path: the sitting runs only the
# pinned side bundle, and a rebuild is a new pin and a new grant.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3.12 "$HERE/sitting.py" "$@"
