#!/bin/bash
# The filename is the W43 orchestrator's entry-point contract; this invokes W49b's guarded adapter.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${W49B_PYTHON:?W49B_PYTHON must name the dedicated scientific runtime}" -I -B "$HERE/sitting.py" "$@"
