#!/bin/bash
# Entry point only. W43's orchestrator is rebound at runtime, not copied into the repository.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "${W49B_PYTHON:?W49B_PYTHON must name the dedicated scientific runtime}" -I -B "$HERE/orchestrate.py" "$@"
