"""Diagnose the CSS-only +2 codes, without fitting or shipping a boundary change (§5.179)."""
import json,os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
plans=json.loads((HERE/'candidate-plans.json').read_text());out=[]
for plan in plans:
    path=Path.home()/'vitrea-w36/scratch/black-css-boundary-isolation'/plan['profile'];path.mkdir(parents=True,exist_ok=True)
    doc=json.loads(json.dumps(plan['active']));doc['patch']['optics']={'regular':{'rimAlpha':0,'rimLevelGain':0,'shadowAlpha':0}}
    doc['claims']='c9a §5.179; diagnostic boundary stand-down only, never a candidate fit or seal'
    with (path/'diagnostic.json').open('x') as f:json.dump(doc,f,indent=2);f.write('\n')
    cmd=list(plan['command']);cmd[cmd.index('--renderer')+1]='css';cmd[cmd.index('--scene')+1]='grey-0__circular-120__rest';cmd[cmd.index('--material-profile')+1]=str(path/'diagnostic.json');cmd[cmd.index('--out-matrix')+1]=str(path/'matrix.json')
    env={**os.environ,**plan['environment'],'VITREA_WEB_CAPTURES':str(path/'web-captures')}
    result=subprocess.run(['python3.12',str(HERE/'run-browser.py'),'css-boundary-isolation-'+plan['profile'],*cmd],env=env)
    out.append(dict(profile=plan['profile'],root=str(path),command=cmd,exitCode=result.returncode,patch=doc['patch']))
with (HERE/'css-boundary-isolation-plans.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
