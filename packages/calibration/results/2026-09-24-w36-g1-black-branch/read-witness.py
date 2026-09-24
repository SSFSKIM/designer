"""Compare the once-read generation with the W33 rows and their surviving pixels (§5.179)."""
import hashlib,json
from pathlib import Path
HERE=Path(__file__).resolve().parent;CAL=HERE.parent.parent
assert (HERE/'read-holdout-completed.txt').is_file(), 'Holdout comparison belongs only to the completed sealed read'
sealed=json.loads((HERE/'sealed-manifest.json').read_text())['documents'];old={}
key=lambda c:(c['key']['profileKey'],c['key']['sceneId'],c['key']['web']['renderer'])
for name,doc in sealed.items():
    if '-receded' in name:continue
    path=CAL/'results/superseded'/(doc['beforeFileSha256'][:12]+'.json')
    for c in json.loads(path.read_text())['cells']:old[key(c)]=c
matrix=json.loads((CAL/'results/matrix.json').read_text());current={key(c):c for c in matrix['cells'] if c['key']['profileKey'].startswith('apple-macos-27.0-')}
assert set(current)==set(old)
main=Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures');capture=CAL/'web-captures';rows=[];changes=[]
# These paths are derived only from canonical matrix identities after the read's
# exclusive completion receipt. W34's archive and spent holdout are not reachable.
for k,c in sorted(current.items()):
    before=old[k];profile,scene,tier=k
    axes={a:c.get(a)==before.get(a) for a in ['shape','material','perceptual','shadow','coherence']}
    if not all(axes.values()):changes.append(dict(cell='/'.join(k),axes=axes))
    folder=capture/profile/scene;oldfolder=main/profile/scene
    meta=json.loads((folder/('cell__'+tier+'.json')).read_text());assert meta['capturePath']==c['key']['web']['capturePath']
    png=scene+'__'+tier+'.png';raw=(folder/png).read_bytes();prior=(oldfolder/png).read_bytes()
    alpha=scene+'__'+tier+'__alpha.png';pair=(folder/alpha).exists() and (oldfolder/alpha).exists()
    rows.append(dict(profile=profile,scene=scene,renderer=tier,role=c['fixtureSet'],axes=axes,pngSame=raw==prior,newSha256=hashlib.sha256(raw).hexdigest(),beforeSha256=hashlib.sha256(prior).hexdigest(),alphaCompared=pair,alphaSame=(folder/alpha).read_bytes()==(oldfolder/alpha).read_bytes() if pair else None))
summary=dict(workingRows=len(matrix['cells']),frozenRows=sum(c['key']['profileKey'].startswith('apple-macos-26.5-') for c in matrix['cells']),newRows=len(current),supersededRows=len(old),roles={role:sum(r['role']==role for r in rows) for role in sorted({r['role'] for r in rows})},changedAxes=changes,changedPng=[r for r in rows if not r['pngSame']],alphaCompared=sum(r['alphaCompared'] for r in rows),changedAlpha=[r for r in rows if r['alphaSame'] is False],holdoutRows=sum(r['role']=='holdout' for r in rows))
for name,value in [('read-witness.json',summary),('read-pixel-witness.json',rows)]:
    with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps(summary,indent=2))
