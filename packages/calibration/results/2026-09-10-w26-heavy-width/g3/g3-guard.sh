#!/bin/bash
# W26 G2 — the GPU guard, run before every capture and never skipped.
#
# W26 G1c's `g1c-guard.sh`, unchanged in content and copied rather than sourced so that this
# child's runs carry their own precondition beside their own evidence. Its two exclusions and the
# measurement that justifies them are recorded there and are not restated: an idle Playwright
# daemon is not a capture RUN, and a browser automation whose command line does not name this
# repository is ambient load this child neither owns nor can wait out. A vitrea capture or bench
# process, or a held :5189, refuses the run outright — X4 is one capture at a time, and the cost of
# breaking it is not a failed run but a quietly wrong one.
set -u
PAT='compare\.ts|sweep\.ts|cost\.mjs|capture\.mjs|capture-web|VitreaReference|playwright'
HITS=$(pgrep -f "$PAT" | grep -v "^$$\$" || true)
BUSY=""
FOREIGN=""
if [ -n "$HITS" ]; then
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    pid=${line%% *}
    case "$line" in
      *run-cli-server*|*"Google Chrome"*|*Chromium.app*|*chrome_crashpad*) continue ;;
    esac
    case "$line" in
      *designer*|*vitrea*|*compare.ts*|*sweep.ts*|*cost.mjs*|*capture.mjs*|*capture-web*|*VitreaReference*)
        BUSY="$BUSY $pid" ;;
      *) FOREIGN="$FOREIGN $pid" ;;
    esac
  done <<EOF
$(ps -o pid=,command= -p $HITS 2>/dev/null)
EOF
fi
if [ -n "$BUSY" ]; then
  echo "GUARD: a vitrea capture or bench process is alive — refusing." >&2
  ps -o pid,etime,command -p $BUSY | cut -c1-160 >&2
  exit 1
fi
if [ -n "$FOREIGN" ]; then
  echo "GUARD: ambient browser automation on this machine (not vitrea, not refused):$FOREIGN"
fi
if lsof -i :5189 >/dev/null 2>&1; then
  echo "GUARD: port 5189 is held — refusing." >&2
  lsof -i :5189 >&2
  exit 1
fi
echo "GUARD: clear at $(date +%H:%M:%S)"
