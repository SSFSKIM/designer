"""Separable formula trial; all cells were admitted before the black price (§5.179 DL2)."""
import hashlib,json,os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
plans=json.loads((HERE/'candidate-plans.json').read_text())
projection={r['cell']:r for r in json.loads((HERE/'projection.json').read_text())}
sources=['packages/renderer-webgpu/src/wgsl/silhouette-tone.ts','packages/platform-web/src/backdrop-tone.ts']
hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}
output=[]
for plan in plans:
    scenes=[sid for sid in plan['scenes'] if projection[plan['profile']+'/'+sid]['origin']=='canonical' and sid.split('__')[-1].startswith('inactive') and (sid.startswith(('photo__','checkerboard','impulse__','hc-text-7__')) or '-tint-' in sid)]
    assert all(projection[plan['profile']+'/'+sid]['originalRole'] in ['calibration','validation','probe'] for sid in scenes)
    work=Path.home()/'vitrea-w36/scratch/receded-formula'/plan['profile'];work.mkdir(parents=True,exist_ok=True)
    jobs=[]
    for renderer in ['webgpu','css']:
        cmd=list(plan['command']);cmd[cmd.index('--renderer')+1]=renderer;cmd[cmd.index('--scene')+1]=','.join(scenes);cmd[cmd.index('--out-matrix')+1]=str(work/'matrix.json');cmd+=['--alpha']
        env={**os.environ,**plan['environment'],'VITREA_WEB_CAPTURES':str(work/'web-captures')}
        assert hashes=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}
        result=subprocess.run(['python3.12',str(HERE/'run-browser.py'),'formula-'+renderer+'-'+plan['profile'],*cmd],env=env)
        for sid in scenes:
            meta=json.loads((work/'web-captures'/plan['profile']/sid/('cell__'+renderer+'.json')).read_text())
            assert meta['deterministic'] and meta['repeatNoise']==0
            if renderer=='webgpu':assert meta['gpuAdapter']=='apple/metal-3'
        jobs.append(dict(renderer=renderer,command=cmd,exitCode=result.returncode))
    output.append(dict(profile=plan['profile'],scenes=scenes,root=str(work),jobs=jobs))
with (HERE/'formula-plans.json').open('x') as f:json.dump(dict(sources=hashes,plans=output),f,indent=2);f.write('\n')
print('Formula cells per tier',sum(len(p['scenes']) for p in output))
