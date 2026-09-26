#!/bin/bash
# when-idle.sh <seconds> <command...>: wait (bounded, 2 h) until read-session reports at least
# <seconds> of HID idle and no prompt window, then run the command. It never launches while
# the user is at the machine; the command's own gates still decide.
need=$1; shift
for i in $(seq 1 720); do
  s=$(/Users/new/vitrea-w39/scratch/read-session)
  ok=$(python3.12 -c "import json,sys;d=json.loads(sys.argv[1]);print(int(d['idleSeconds']>=$need and not any(o.startswith('universalAccessAuthWarn') for o in d['windowOwners'])))" "$s")
  [ "$ok" = 1 ] && exec "$@"
  sleep 10
done
echo "when-idle: gave up after 2 h: $s"; exit 9
