#!/bin/sh
# W33 X6: all four facts, not just the accessibility half (§5.173; W32 N7).
set -e
here=$(cd "$(dirname "$0")" && pwd)
python3 "$here/record-machine.py" "$1"
