#!/usr/bin/env python3
"""Attest the sixty-second capture-idle interval before one browser run (§5.173)."""
import datetime
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent

def processes():
    output=subprocess.check_output(['ps','-axo','pid=,ppid=,command='],text=True)
    rows=[line.strip().split(None,2) for line in output.splitlines()]
    parents={int(p):int(pp) for p,pp,_ in rows}
    ancestors=set();pid=os.getpid()
    while pid and pid not in ancestors:
        ancestors.add(pid);pid=parents.get(pid,0)
    return [line for line in rows if int(line[0]) not in ancestors and
            re.search(r'Chromium|playwright|compare\.ts|capture-web|VitreaReference',line[2])]

def settings():
    values=[]
    for domain,key in [('com.apple.universalaccess','reduceTransparency'),
                       ('com.apple.universalaccess','increaseContrast'),('-g','NSGlassTintAmount')]:
        p=subprocess.run(['defaults','read',domain,key],capture_output=True,text=True)
        values.append(p.stdout.strip() if p.returncode==0 else 'absent')
    return values

start=datetime.datetime.now(datetime.timezone.utc).isoformat()
clock=time.monotonic()
foreign=[]
# These are idle observations, not polling a background task for completion.
while True:
    foreign.extend(processes())
    if foreign or time.monotonic()-clock>=60:break
    time.sleep(min(1,60-(time.monotonic()-clock)))
rt,ic,glass=settings()
record=dict(time=datetime.datetime.now(datetime.timezone.utc).isoformat(),run=sys.argv[1],
    reduceTransparency=rt,increaseContrast=ic,NSGlassTintAmount=glass,
    foreignProcessCount=len(foreign),foreignProcesses=foreign,idleStart=start,
    idleSeconds=round(time.monotonic()-clock,3))
line=json.dumps(record)
with (HERE/'browser-runs.txt').open('a') as f:f.write(line+'\n')
print(line,flush=True)
if foreign or [rt,ic,glass]!=['0','0','0.5'] or record['idleSeconds']<60:
    raise SystemExit('X6 refused; browser not launched')
