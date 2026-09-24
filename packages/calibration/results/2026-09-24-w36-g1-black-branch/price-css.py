"""Tier price, admitting original roles before opening any CSS payload (§5.179)."""
import base64,gzip,hashlib,io,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;CAL=HERE.parent.parent
sys.path.insert(0,str(HERE.parent/'2026-09-24-w35-g0-edge-cut'))
import edge
from w35_readers import WebReader,confined
plans=json.loads((HERE/'candidate-plans.json').read_text())
projection={r['cell']:r for r in json.loads((HERE/'projection.json').read_text())}
old={(c['key']['profileKey']+'/'+c['key']['sceneId'],c['key']['web']['renderer']):c for c in json.loads((CAL/'results/matrix.json').read_text())['cells']}
# A read-only extension beside W35's frozen reader: same membership/role guard,
# same confined cell-key API, with the CSS suffix rather than a webgpu alias.
class TierReader(WebReader):
    def css(self,cell,kind='png'):
        profile,sid=self.admit(cell)
        names={'png':sid+'__css.png','metadata':'cell__css.json','report':'report__css.json'}
        return confined(self.root,self.root/profile/sid/names[kind]).read_bytes()
def conditioned(cell):
    shape=(cell or {}).get('shape')
    if shape is None:return True
    at=lambda k:shape.get(k,{}).get('value',float('nan'))
    return (at('silhouetteAreaNative')>=.95*at('componentRegionArea') and
        at('silhouetteAreaWeb')>=.95*at('componentRegionArea') and
        at('silhouetteBodiesNative')<=at('componentRegionBodies') and
        at('silhouetteBodiesWeb')<=at('componentRegionBodies'))
def image(raw):return np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'))
def save(name,value):
    with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
baseDeep={r['cell']:r for r in json.loads((HERE.parent/'2026-09-24-w36-g0-level-cut/deep-cut.json').read_text())}
wave=edge.W.default_wave();repeat=wave.reader(edge.G1/'repeat');rows=[];greys=[];failures=[]
for plan in plans:
    root=Path(plan['root']);cells={c['key']['sceneId']:c for c in json.loads((root/'matrix.json').read_text())['cells'] if c['key']['web']['renderer']=='css'}
    for sid in plan['scenes']:
        cell=plan['profile']+'/'+sid;origin=projection[cell]['origin']
        roles=wave if origin=='w34' else WebReader.canonical(root).roles
        reader=TierReader(root/'web-captures',roles);raw=reader.css(cell);meta=json.loads(reader.css(cell,'metadata'))
        assert meta['renderer']=='css' and meta['deterministic'] and meta['repeatNoise']==0
        current=cells.get(sid);co=(current or {}).get('coherence',{});metrics={k:v['value'] for k,v in co.items() if isinstance(v,dict) and 'value' in v}
        if origin=='w34':
            crop=json.loads(gzip.decompress(repeat.read(cell,'crop')));run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal');p=edge.I.unpack(base64.b64decode(crop['states'][run['state']]))
            mask=edge.geometry(p)[0]<=-6*p['scale'];im=image(raw);median=np.median(im[mask],0);native=np.array(baseDeep[cell]['nativeMedian'])
            ratio=metrics.get('interiorLevelRatioGpuOverCss')
            ratioStatus='UNMEASURED' if ratio is None else 'GATED' if conditioned(current) else 'PREDICATE EXCLUDED'
            row=dict(cell=cell,median=median.tolist(),native=native.tolist(),miss=(median-native).tolist(),coherence=metrics,ratioStatus=ratioStatus,
                mask={k:v for k,v in (current or {}).get('shape',{}).items() if k in ['silhouetteAreaNative','silhouetteAreaWeb','componentRegionArea','silhouetteBodiesNative','silhouetteBodiesWeb','componentRegionBodies']})
            greys.append(row)
            # Black changes on both tiers. Non-black's known level gap is not
            # silently turned into a new stop under Decision Log 5.
            if sid.startswith('grey-0__'):
                if np.max(abs(median-native))>1:failures.append(dict(stop='CSS black level',**row))
                if metrics.get('crossTierOklabDeltaEMean',float('inf'))>.05 or (ratioStatus=='GATED' and not .8<=ratio<=1.25):failures.append(dict(stop='black coherence',**row))
        else:
            before=old.get((cell,'css'))
            previous=TierReader('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures',roles)
            try:prior=previous.css(cell)
            except FileNotFoundError:prior=None
            same=None if before is None or current is None else {a:before.get(a)==current.get(a) for a in ['shape','material','perceptual','coherence','shadow']}
            row=dict(cell=cell,pngSame=None if prior is None else raw==prior,axesSame=same,coherence=metrics,baselineRowPresent=before is not None)
            rows.append(row)
            # An unchanged pre-existing diagnostic miss is not a new regression.
            # Any actual changed canonical byte or metric is decomposed, never
            # dismissed by the compact-support argument.
            if row['pngSame'] is False:failures.append(dict(stop='unexpected canonical CSS movement',**row))
summary=dict(captured=len(rows)+len(greys),canonicalByteComparisons=sum(r['pngSame'] is not None for r in rows),canonicalByteChanges=[r['cell'] for r in rows if r['pngSame'] is False],axisChanges=[r for r in rows if r['axesSame'] and not all(r['axesSame'].values())],black=[r for r in greys if '/grey-0__' in r['cell']],failures=failures)
save('price-css-pixels.json',rows);save('price-css-greys.json',greys);save('price-css-summary.json',summary)
print(json.dumps(summary,indent=2));raise SystemExit(1 if failures else 0)
