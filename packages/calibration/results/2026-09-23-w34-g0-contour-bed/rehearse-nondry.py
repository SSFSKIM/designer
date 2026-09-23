#!/usr/bin/env python3
"""Exercise the non-dry inactive branch with real rehearse-tints, no capture."""
import json
import os
from pathlib import Path
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent


def main():
    with tempfile.TemporaryDirectory(prefix='w34-nondry-rehearsal-') as tmp:
        root=Path(tmp)
        machine=json.loads((HERE/'machine-side-built.json').read_text())
        machine['foreignProcessCount']=0;machine['foreignProcesses']=[]
        (root/'machine.json').write_text(json.dumps(machine))
        recorder=root/'recorder.py'
        recorder.write_text('import pathlib\nprint(pathlib.Path('+repr(str(root/'machine.json'))+').read_text())\n')
        session=root/'session.py';session.write_text('print(\'{"idleSeconds": 100, "screenLocked": false}\')\n')
        harness=root/'harness.py'
        harness.write_text('''import json,os,subprocess,sys
from pathlib import Path
scenes=os.environ['VITREA_SCENES'];fixtures=os.environ['VITREA_FIXTURES']
assert Path(scenes).is_file() and Path(fixtures).is_dir()
with Path(os.environ['CALLS']).open('a') as f:f.write(json.dumps(dict(command=sys.argv[1:],scenes=scenes,fixtures=fixtures))+'\\n')
if sys.argv[1]=='rehearse-tints':
 subprocess.run(['/Users/new/vitrea-w34/side/harness',*sys.argv[1:]],check=True)
elif sys.argv[1]=='backgrounds':
 print('STUB backgrounds; no capture will consume these')
else:raise ValueError('unexpected harness call')
''')
        launcher=root/'launcher.py'
        launcher.write_text('''import json,sys
from pathlib import Path
args=sys.argv[1:];env={}
for i,a in enumerate(args):
 if a=='--env':k,v=args[i+1].split('=',1);env[k]=v
assert 'VITREA_SCENES' in env and 'VITREA_FIXTURES' in env
assert '--inactive' in args and '--dry-run' not in args
spec=json.loads(Path(env['VITREA_SCENES']).read_text())
base=json.loads(Path('''+repr(str(HERE/'scratch-manifests/inactive/run-1/manifest.json'))+''').read_text())
fixture=base['profiles'][0]['fixtures'][0]
profiles=[]
for p in spec['profiles']:
 template=next(x for x in base['profiles'] if x['profileKey']==p['key'])
 profiles.append({**template,'fixtures':[{**fixture,'sceneId':s,'file':p['key']+'/'+s+'.png'} for s in p['scenes']]})
base['profiles']=profiles
Path(env['VITREA_FIXTURES'],'manifest.json').write_text(json.dumps(base))
Path(args[args.index('--stdout')+1]).write_text('STUB capture: no native pixels produced\\n')
Path(args[args.index('--stderr')+1]).write_text('')
''')
        calls=root/'calls.jsonl'
        env={**os.environ,'DRY':'0','VITREA_SITTING_DIR':str(root/'runs'),
             'VITREA_RECORD_MACHINE':f'python3 {recorder}','VITREA_SESSION_READER':f'python3 {session}',
             'VITREA_HARNESS':f'python3 {harness}','VITREA_LAUNCHER':f'python3 {launcher}','CALLS':str(calls),
             'VITREA_REHEARSAL_FIXTURES':'/Users/new/Developer/GitHub/designer/apps/reference-apple/fixtures'}
        print('NO CAPTURE: launcher and machine are stubs; the side rehearse-tints is real.',flush=True)
        subprocess.run(['bash',str(HERE/'run-sitting-w34.sh'),'inactive','2','1','1'],env=env,check=True)
        observed=[json.loads(line) for line in calls.read_text().splitlines()]
        assert [r['command'][0] for r in observed]==['rehearse-tints','backgrounds']
        assert all(r['scenes'] and r['fixtures'] for r in observed)
        print(json.dumps(observed,indent=2))
        print((root/'runs/inactive-2x/producer-rehearse-tints.out').read_text())
        print('Non-dry inactive branch exercised with both explicit roots; zero native pixels.')


if __name__=='__main__':main()
