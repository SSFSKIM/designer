#!/bin/zsh
set -u
F=~/vitrea-w46/g1/packages/calibration/results/2026-10-05-w46-g1-refit/fit
G=~/vitrea-w46/g1/packages/calibration/results/2026-10-05-w46-g1-refit/gate
A=d-s2-rta0.8-rs214-rfa0.5-rh10.25-re20.04-rk10.15-rk20.04-rn10.4-rn20.4-rg0
B=d-s2-rta0.8-rs214-rh10.25-re20.04-rk10.3-rk20.04-rn11-rn21-rg0
cd $F
python3.12 -B drive.py fullA -- python3.12 -B search.py full $A || exit 1
python3.12 -B drive.py fullB -- python3.12 -B search.py full $B || exit 1
python3.12 -B drive.py joint -- python3.12 -B joint.py || exit 1
cd $G
for P in $A $B; do
  for try in 1 2 3 4 5 6; do
    python3.12 -B gate.py render $P --light && break
    echo "gate render $P attempt $try failed; waiting"; sleep 600
  done
done
echo CHAIN-DONE
