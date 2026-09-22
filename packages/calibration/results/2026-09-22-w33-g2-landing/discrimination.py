#!/usr/bin/env python3.12
"""Exercise the real X1 cases against scratch mutations, never canonical pixels (§5.173)."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import numpy as np
from PIL import Image
import referee as r

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
canonical=Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
cut=json.loads((HERE/'black-cut.json').read_text())
command=['pnpm','--filter','@vitrea/calibration','--fail-if-no-match','exec','vitest','run',
         'test/adopted-thresholds.test.ts','-t','W33 X1']
with tempfile.TemporaryDirectory(prefix='w33-x1-') as scratch:
    scratch=Path(scratch)
    def run(label, env, failure):
        result=subprocess.run(command,cwd=ROOT,env=dict(os.environ,
            VITREA_WEB_CAPTURES=str(canonical),**env),text=True,capture_output=True)
        output=result.stdout+result.stderr
        (HERE/f'discrimination-{label}.txt').write_text(output)
        assert result.returncode!=0 and failure in output,(label,result.returncode,output)
        print(label,'RED as required, exit',result.returncode)
    bad=json.loads(json.dumps(cut))
    bad['cells'][0]['integer']['backdropBlack']+=1
    path=scratch/'cut.json';path.write_text(json.dumps(bad))
    run('cut',dict(VITREA_X1_CUT=str(path)),'pixels disagree with the cut')
    bad=json.loads(json.dumps(cut));bad['missed']=['bogus excuse']
    path.write_text(json.dumps(bad))
    run('excuse',dict(VITREA_X1_CUT=str(path)),'bogus excuse')
    tree=scratch/'captures';tree.mkdir()
    row=cut['cells'][0];profile,sid=row['profile'],row['scene']
    for other in cut['cells']:
        p,s=other['profile'],other['scene'];d=tree/p/s
        d.parent.mkdir(exist_ok=True)
        if (p,s)!=(profile,sid):d.symlink_to(canonical/p/s,target_is_directory=True)
    directory=tree/profile/sid;directory.mkdir()
    for src in (canonical/profile/sid).iterdir():
        if src.name==sid+'__webgpu.png':shutil.copyfile(src,directory/src.name)
        else:(directory/src.name).symlink_to(src)
    native=r.rgb(r.FIXTURES/profile/(sid+'.png'))
    png=directory/(sid+'__webgpu.png')
    pixels=np.array(Image.open(png).convert('RGBA'))
    h,w=native.shape[:2];scale=w/320
    backdrop=r.rgb(r.FIXTURES/'backgrounds'/f'{r.SCENE[sid]["background"]}@{scale:g}x.png')
    mask=r.exterior_masks(w,h,r.geometry(sid,scale)[0],scale)[0]
    eligible=mask&np.all(native==0,axis=2)&np.all(backdrop==0,axis=2)
    y,x=np.argwhere(eligible)[0]
    pixels[y,x,0]=1
    Image.fromarray(pixels).save(png)
    env=dict(os.environ,VITREA_WEB_CAPTURES=str(tree))
    result=subprocess.run(command,cwd=ROOT,env=env,text=True,capture_output=True)
    output=result.stdout+result.stderr
    (HERE/'discrimination-pixel.txt').write_text(output)
    assert result.returncode!=0 and 'pixels disagree with the cut' in output
    print('one scratch pixel',profile,sid,'xy',int(x),int(y),'RED, exit',result.returncode)
print('Canonical tree was only read; all scratch mutations removed.')
