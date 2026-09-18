#!/bin/bash
# Every rehearsal the four standard passes need, in one go — W29 G1 (5), claims §5.150.
#
# `DRY=1` presents and attests every cell of a pass through the real bundle, the
# real declaration and the real machine state, and captures nothing. It is the
# cheap proof that a pass will run, and its verdict is the COUNT rather than the
# exit status: `run-sitting-27.sh` treats any nonzero count as success, so a pass
# that presented 30 of 162 prints PASS and exits 0. The counts to expect are the
# id lists `pass-spec.py` derives — 96 active and 72 inactive at each scale.
#
# The 1x arms need the BetterDisplay virtual screen at displayplacer mode 69 and
# the display is returned to 68 afterwards, which is both what the W27 sitting
# records doing and what `run-sitting-27.sh` now refuses on: a 1x pass at mode 68
# does not mislabel a fixture, it quietly captures the 2x profiles into the 1x
# pass's directory.
#
# The two accessibility modes are NOT rehearsed here. Each needs the user's hand
# in System Settings > Accessibility > Display, and the script refuses a pass
# whose declared mode the machine is not in — so a rehearsal of them from this
# session would only exercise that refusal, which `run-sitting-27.test.sh`
# already does against a stubbed machine. Their rehearsal belongs beside their
# pass, in the runbook.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCREEN="id:7709FD0F-F423-4277-B0C8-7CA94F85723A"
# `.txt`, not `.log`: the repository's `.gitignore` drops `*.log` wholesale, and a
# rehearsal's output is a record the runbook asks to be committed. The W27 sitting
# committed its own pass logs as `.txt` under `logs/` for the same reason.
LOG="${1:-$HOME/vitrea-w29-27-run/rehearsal.txt}"
mkdir -p "$(dirname "$LOG")"

mode() {
  displayplacer "$SCREEN res:2560x1440 hz:60 color_depth:4 enabled:true origin:(0,0) degree:0 mode:$1" \
    >/dev/null
  sleep 3
  local now
  now="$(displayplacer list | sed -n 's/^  mode \([0-9]*\):.*<-- current mode$/\1/p' | head -1)"
  [ "$now" = "$1" ] || { echo "REFUSED: asked for display mode $1 and the screen reports $now" >&2; exit 1; }
  echo "display: mode $now"
}

{
  echo "=== W29 G1 rehearsal, $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
  for SPEC in "inactive 2" "active 2"; do
    set -- $SPEC
    echo "--- DRY $1 ${2}x standard ---"
    DRY=1 "$HERE/run-sitting-27.sh" "$1" "$2" standard
  done
  mode 69
  for SPEC in "inactive 1" "active 1"; do
    set -- $SPEC
    echo "--- DRY $1 ${2}x standard ---"
    DRY=1 "$HERE/run-sitting-27.sh" "$1" "$2" standard
  done
  mode 68
  echo "=== rehearsal done $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
} 2>&1 | tee "$LOG"
