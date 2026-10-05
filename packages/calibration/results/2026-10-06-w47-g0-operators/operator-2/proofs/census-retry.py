#!/usr/bin/env python3.12
"""Retry only an explicit census refusal, every150s until the run's two-hour deadline.

The GPU lock and census stay authoritative. A test/compare failure is never retried here.
All stdout/stderr, refusals and return codes are retained in the caller's append-only log.
"""
import datetime,os,re,subprocess,sys,time
stop=float(os.environ.get('W47_CENSUS_DEADLINE',time.time()+7200))
cmd=sys.argv[1:]
while True:
 print('ATTEMPT',datetime.datetime.now(datetime.timezone.utc).isoformat(),flush=True)
 p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
 print(p.stdout,end='',flush=True)
 print('EXIT_CODE',p.returncode,flush=True)
 refused=p.returncode==1 and bool(re.search(r'^census [^\n]+: REFUSES ',p.stdout,re.M))
 if not refused:sys.exit(p.returncode)
 if time.time()+150>stop:
  print('CENSUS_DEADLINE_EXHAUSTED',flush=True);sys.exit(1)
 print('Census refusal only; retry in150s without bypassing the gate.',flush=True)
 time.sleep(150)
