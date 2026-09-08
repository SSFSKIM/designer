#!/bin/bash
# W24 G0 (c) — the law, fitted twice: on the reference's own bins and on vitrea's own pixels.
#
# `fit-law.py` answers what Apple draws — the axis, the form and the ambient fraction, over the
# untinted solid rows of both canonical beds and both probe grids. `fit-vitrea.py` answers what the
# shader draws at a named constant, what exponent vitrea's own rows want against the reference, and
# whether the straight spans W23 fitted have moved. Both land in one file, in that order, because
# the second is only readable against the first.
set -eu
PY=/Users/new/.claude/jobs/5c70e47f/tmp/venv/bin/python
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
{
  "$PY" "$HERE/fit-law.py" --json "$HERE/fit-law.json"
  echo
  echo "##############################################################################"
  echo
  "$PY" "$HERE/fit-vitrea.py" --json "$HERE/fit-vitrea.json"
} > "$HERE/fit-law.txt" 2>&1
echo "-> $HERE/fit-law.txt"
