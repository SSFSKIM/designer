#!/usr/bin/env python3
"""W34 sitting driver, derived from W29's refusal/attestation protocol (§5.174).

No retry consumes a failed run. Every pass uses the side bundle, explicit roots,
complete per-cell membership, opening/closing facts and quarantine on failure.
Capture logs can contain holdout state diagnostics and remain producer-only.
"""
import argparse
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
import time

HERE=Path(__file__).resolve().parent
PIN=json.loads((HERE/'bundle-pin.json').read_text())
pass_module=importlib.util.spec_from_file_location('pass_spec',HERE/'pass-spec.py')
PASS=importlib.util.module_from_spec(pass_module);pass_module.loader.exec_module(PASS)


def configuration(m):
    signature=m['side'].get('signature',{}).get('stderr','')
    cd=re.search(r'^CDHash=(.+)$',signature,re.M)
    mode=re.findall(r'^  mode (\d+):.*<-- current mode$',m['display']['stdout'],re.M)
    return dict(os=m['os']['stdout'],settings={k:v['stdout'] for k,v in m['settings'].items()},
        mode=mode,displayIdentity=re.findall(r'^Persistent screen id: (.+)$',m['display']['stdout'],re.M),
        colour=m['displayColourContext']['stdout'],binary=m['side'].get('binarySha256'),
        cdhash=cd[1] if cd else None,build=m['side'].get('buildVersion',{}).get('stdout'))


def validate_machine(m,scale,require_exclusive=True):
    c=configuration(m)
    if not re.search(r'ProductVersion:\s+27\.0\s',c['os']) or '26A428' not in c['os']:
        raise ValueError('OS version/build is not the declared 27.0 / 26A428')
    expected={'reduceTransparency':'0','increaseContrast':'0','NSGlassTintAmount':'0.5','ButtonShapesEnabled':'0'}
    if c['settings']!=expected:raise ValueError('policy/slider/Show Borders mismatch')
    if c['mode']!=[str(69 if scale==1 else 68)] or c['displayIdentity']!=['7709FD0F-F423-4277-B0C8-7CA94F85723A']:
        raise ValueError('display mode/identity mismatch')
    if c['binary']!=PIN['binarySha256'] or c['cdhash']!=PIN['cdhash']:
        raise ValueError('side bundle identity changed; a rebuild needs a new grant')
    if require_exclusive and m['foreignProcessCount']!=0:raise ValueError('G1 requires foreign-capture exclusivity; G0 exception does not authorise G1')
    return c


def validate_manifest(m,expected,pose,scale):
    actual={(p['profileKey'],f['sceneId']) for p in m['profiles'] for f in p['fixtures']}
    if actual!=expected:raise ValueError('capture membership is incomplete or unexpected')
    if m['hardware']['osBuild']!='26A428':raise ValueError('captured OS build mismatch')
    for profile in m['profiles']:
        if profile['display']['actualBackingScale']!=scale:raise ValueError('captured backing scale mismatch')
        for f in profile['fixtures']:
            if not f['materialRendered'] or not f.get('deterministic'):
                raise ValueError('material/repeat attestation failed: '+f['sceneId'])
            if f.get('presentedActive')!=(pose=='active'):raise ValueError('pose attestation failed: '+f['sceneId'])
            if pose=='inactive':
                p=f.get('presentation') or {}
                if p.get('observedPose')!='inactive' or p.get('isKeyWindow') is not False or p.get('appIsActive') is not False:
                    raise ValueError('inactive presentation fields failed')


def tool(name,default):return shlex.split(os.environ.get(name,default))


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('pose',choices=['active','inactive']);ap.add_argument('scale',type=int,choices=[1,2])
    ap.add_argument('first',type=int,nargs='?',default=1);ap.add_argument('last',type=int,nargs='?')
    ap.add_argument('--sentinel',action='store_true')
    args=ap.parse_args();dry=os.environ.get('DRY')=='1'
    limit=3 if args.sentinel else 7
    last=args.last if args.last is not None else (args.first if dry else limit)
    if not 1<=args.first<=last<=limit:ap.error(f'runs must be a nonempty subset of 1..{limit}')
    root=Path(os.environ.get('VITREA_SITTING_DIR',str(Path.home()/'vitrea-w34/run'))).resolve()
    # Evidence is staged outside the repository; narrowed publication never
    # targets the frozen reference tree or a previous run's manifest.
    if str(root).startswith(str(HERE.parents[3])):raise ValueError('sitting output must be outside the repository')
    app=Path(os.environ.get('VITREA_APP',PIN['path'])).resolve()
    if str(app)!=PIN['path']:raise ValueError('this sitting is pinned to the side bundle')
    harness=tool('VITREA_HARNESS',str(app.parent/'harness'))
    recorder=tool('VITREA_RECORD_MACHINE',f'{sys.executable} {HERE}/record-machine.py')
    launcher=tool('VITREA_LAUNCHER','open -W')
    session=tool('VITREA_SESSION_READER',str(Path.home()/'vitrea-w34/scratch/read-session'))
    passdir=root/(f'{args.pose}-{args.scale}x'+('-sentinel' if args.sentinel else ''));passdir.mkdir(parents=True,exist_ok=True)
    doc=PASS.derive(args.pose,args.scale)
    if args.sentinel:
        doc['scenes']=[s for s in doc['scenes'] if s['component']=='circular-120' and s['background'] in ['grey-128','checkerboard']]
        ids={s['id'] for s in doc['scenes']}
        for p in doc['profiles']:p['scenes']=[s for s in p['scenes'] if s in ids]
        doc['split']['probe']=sorted(ids)
    spec=passdir/'scenes.json';encoded=json.dumps(doc,indent=2)+'\n'
    if spec.exists() and spec.read_text()!=encoded:raise ValueError('existing pass declaration differs')
    if not spec.exists():spec.write_text(encoded)
    rehearsal=Path(os.environ.get('VITREA_REHEARSAL_FIXTURES',
        '/Users/new/Developer/GitHub/designer/apps/reference-apple/fixtures')).resolve()
    # This non-dry branch is intentionally exercised in the G0 rehearsal. The
    # canonical manifest is read-only; W34 has no tints, so no PNG is read here.
    if not dry and args.pose=='inactive':
        env={**os.environ,'VITREA_SCENES':str(spec),'VITREA_FIXTURES':str(rehearsal),'VITREA_SCALE':str(args.scale)}
        with (passdir/'producer-rehearse-tints.out').open('w') as f:
            subprocess.run([*harness,'rehearse-tints','--pose','inactive'],env=env,
                           stdout=f,stderr=subprocess.STDOUT,check=True)
    expected={(p['key'],s) for p in doc['profiles'] for s in p['scenes']}
    for n in range(args.first,last+1):
        run=passdir/f'run-{n}'
        if run.exists():raise ValueError('run already exists; keep it, do not overwrite or silently resume')
        run.mkdir()
        def attest(phase):
            raw=subprocess.check_output([*recorder,f'w34-{args.pose}-{args.scale}x-{n}-{phase}'])
            (run/f'attest.{phase}.json').write_bytes(raw)
            return json.loads(raw)
        opened=attest('open');start=validate_machine(opened,args.scale,not dry)
        def portable_attestation(m,phase):
            c=configuration(m)
            fields=dict(phase=phase,readAt=m['recordedAt'],passName=f'{args.pose}-{args.scale}x',
                osProductVersion=re.search(r'ProductVersion:\s+(\S+)',c['os'])[1],
                osBuild=re.search(r'BuildVersion:\s+(\S+)',c['os'])[1],
                glassTintAmount=c['settings']['NSGlassTintAmount'],
                reduceTransparency=c['settings']['reduceTransparency'],
                increaseContrast=c['settings']['increaseContrast'],showBorders=c['settings']['ButtonShapesEnabled'],
                displayplacerMode=c['mode'][0],bundleCdHash=c['cdhash'],bundleBinarySha256=c['binary'],
                foreignProcessCount=m['foreignProcessCount'],
                foreignPids=','.join(row[0] for row in m['foreignProcesses']),
                passSpecSha256=hashlib.sha256(spec.read_bytes()).hexdigest())
            return ''.join(f'{key}={value}\n' for key,value in fields.items())
        (run/'attest.read').write_text(portable_attestation(opened,'open'))
        if dry and opened['foreignProcessCount']:
            print(f"dry rehearsal: real pass would refuse {opened['foreignProcessCount']} foreign processes",flush=True)
        observed=json.loads(subprocess.check_output(session,text=True))
        (run/'session-before.json').write_text(json.dumps(observed,indent=2)+'\n')
        if observed.get('idleSeconds',0)<60 or observed.get('screenLocked') is not False:
            raise ValueError('no launch: at least sixty seconds HID idle and unlocked session required')
        env={**os.environ,'VITREA_SCENES':str(spec),'VITREA_FIXTURES':str(run),'VITREA_SCALE':str(args.scale)}
        with (run/'producer-backgrounds.out').open('w') as f:
            subprocess.run([*harness,'backgrounds'],env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
        command=[*launcher]
        for key in ['VITREA_SCENES','VITREA_FIXTURES','VITREA_SCALE']:command+=['--env',key+'='+env[key]]
        command+=['--stdout',str(run/'producer-capture.out'),'--stderr',str(run/'producer-capture.err'),str(app),
                  '--args','capture','--run-label',f'w34-{args.pose}-{args.scale}x-{n}',
                  '--reset-interstitial','0' if dry else '6','--min-idle-seconds','60',
                  '--scenes',','.join(s['id'] for s in doc['scenes'])]
        if args.sentinel:command+=['--initial-settle','8','--order-seed','3401']
        if args.pose=='inactive':command+=['--inactive']
        if dry:command+=['--dry-run']
        try:
            subprocess.run(command,check=True)
            closed=attest('close')
            (run/'attest.close').write_text(portable_attestation(closed,'close'))
            if validate_machine(closed,args.scale,not dry)!=start:raise ValueError('opening/closing state drift')
            if dry:
                output=(run/'producer-capture.out').read_text()
                lines=[line for line in output.splitlines() if ' dry-run' in line]
                if len(lines)!=len(expected) or 'WOULD REFUSE' in output or 'NOT-ACTIVE' in output:
                    raise ValueError('dry rehearsal incomplete or pose refused')
                admitted=True
            else:
                m=json.loads((run/'manifest.json').read_text());validate_manifest(m,expected,args.pose,args.scale)
                admitted=True
            (run/'admission.json').write_text(json.dumps(dict(admitted=admitted,cells=len(expected),dry=dry))+'\n')
            print(f'{args.pose} {args.scale}x run {n}: admitted={admitted} cells={len(expected)} dry={dry}',flush=True)
        except BaseException:
            quarantine=run.with_name(f'QUARANTINE-run-{n}-{time.time_ns()}');run.rename(quarantine)
            print('REFUSED; retained at '+str(quarantine),file=sys.stderr);raise


if __name__=='__main__':main()
