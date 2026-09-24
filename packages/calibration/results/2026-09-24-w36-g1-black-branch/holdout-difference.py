"""Decompose the one changed holdout PNG from the completed read; never rerender (§5.179)."""
import hashlib,json
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;CAL=HERE.parent.parent
assert (HERE/'read-holdout-completed.txt').is_file()
p='apple-macos-27.0-1x-dark-standard-glass0.5';sid='checkerboard__glass-over-glass__rest';name=sid+'__css.png'
old=Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')/p/sid;new=CAL/'web-captures'/p/sid
before=np.asarray(Image.open(old/name).convert('RGB'),int);after=np.asarray(Image.open(new/name).convert('RGB'),int);ys,xs=np.where(np.any(before!=after,axis=2))
reports=[json.loads((folder/'report__css.json').read_text()) for folder in [old,new]]
inputs=lambda r:[dict(group=g['id'],tone=g.get('backdropTone'),local=g['state'].get('backdropToneAbscissae')) for g in r['page']['groups']]
rows=[]
for file in [CAL/'results/superseded/eab099cc6698.json',CAL/'results/matrix.json']:
    rows.append(next(c for c in json.loads(file.read_text())['cells'] if c['key']['profileKey']==p and c['key']['sceneId']==sid and c['key']['web']['renderer']=='css'))
changes=[]
for axis in ['material','perceptual','shadow','coherence']:
    for k,v in rows[0].get(axis,{}).items():
        w=rows[1].get(axis,{}).get(k)
        if isinstance(v,dict) and 'value' in v and w!=v:changes.append(dict(axis=axis,metric=k,before=v,after=w))
alpha=sid+'__css__alpha.png'
result=dict(cell=p+'/'+sid,renderer='css',role='holdout',pixels=[dict(x=int(x),y=int(y),before=before[y,x].tolist(),after=after[y,x].tolist()) for y,x in zip(ys,xs)],maxChannelDelta=int(np.max(abs(before-after))),alphaByteIdentical=(old/alpha).read_bytes()==(new/alpha).read_bytes(),inputsBefore=inputs(reports[0]),inputsAfter=inputs(reports[1]),currentMetadata=json.loads((new/'cell__css.json').read_text()),scalarMetricChanges=changes,
    qualification='Five exterior white pixels increase by one code. Both group inputs are identical and above the black support; the alpha PNG is identical. This is not attributed to the black law or labelled noise. No holdout retry or refit is made; adopted gates pass at this actual reading.')
with (HERE/'holdout-difference.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print('holdout changed pixels',len(xs),'max code delta',result['maxChannelDelta'],'inputs equal',inputs(reports[0])==inputs(reports[1]),'alpha identical',result['alphaByteIdentical'])
