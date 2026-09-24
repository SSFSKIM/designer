"""Re-derive compact tables from this gate's full artifacts; never from the memo."""
import csv,gzip,hashlib,json
from collections import defaultdict
import numpy as np
from edge import HERE,save,decode,encode,forward
p=json.loads(gzip.decompress((HERE/'profiles.json.gz').read_bytes()))
b=json.loads(gzip.decompress((HERE/'deep-bars.json.gz').read_bytes()))
parts=defaultdict(lambda:dict(cells=set(),bins=0,pixels=0,maxBar=0,deficient=0))
for r in b:
 for x in r['bins']:
  key=(r['cell'].split('/')[0],r['cell'].split('__')[-1],r['protocol'],x['part'])
  t=parts[key];t['cells'].add(r['cell']);t['bins']+=1;t['pixels']+=x['pixels'];t['maxBar']=max(t['maxBar'],max(x['barRGB']));t['deficient']+=not x['admissible']
barhead=[dict(profile=k[0],pose=k[1],protocol=k[2],part=k[3],**{j:(len(v) if j=='cells' else v) for j,v in t.items()}) for k,t in sorted(parts.items())]
save(HERE/'bar-headlines.json',barhead)
levels=[];lines=[];angular=[];structured=[]
for r in p:
 if '__circular-120__' not in r['cell']:continue
 beta=np.array(r['deep']['nativeMedian']);wb=np.array(r['deep']['webMedian']);scale=r['scale']
 top={s['shell']:s for s in r['sides'] if s['side']=='top'}
 levels.append(dict(cell=r['cell'],role=r['role'],backgroundKind=r['backgroundKind'],**r['deep']))
 if r['backgroundKind']=='solid':
  lines.append(dict(cell=r['cell'],role=r['role'],widthPartitionDevicePx=scale,
    deepRGB=beta.tolist(),lineExcessRGB=[(np.array(top[s]['nativeRGB'])-beta).tolist() for s in range(-scale,0)],
    rampLastExcessRGB=(np.array(top[-scale-1]['nativeRGB'])-beta).tolist(),
    fullRampReachCssPx=6,baselineEnvelope=r['deep']['nativeEnvelope'],
    topBottomMax=max(max(abs(np.array(s['nativeRGB'])-next(q['nativeRGB'] for q in r['sides'] if q['side']=='bottom' and q['shell']==s['shell']))) for s in top.values() if -scale<=s['shell']<0)))
 if 'grey-128__' in r['cell']:
  angular.append(dict(cell=r['cell'],rows=r['angular'],sides=r['sides']))
 if r['backgroundKind']!='solid':
  structured.append(dict(cell=r['cell'],role=r['role'],backgroundKind=r['backgroundKind'],
    reading='diagnostic only: median is not a local boundary field',deepRGB=beta.tolist(),
    shells=[dict(shell=s,nativeRGB=top[s]['nativeRGB'],excess=(np.array(top[s]['nativeRGB'])-beta).tolist()) for s in range(-6*scale,0)]))
save(HERE/'level-table.json',levels);save(HERE/'line-headlines.json',lines)
save(HERE/'angular-cut.json',angular);save(HERE/'structured-cut.json',structured)
# The original compact control operated on abstract values; this separate control
# explicitly changes the final encoded image, after the real forward composite.
body=np.repeat(np.array([.03,.12,.3,.55])[:,None],3,1);f=forward(body,np.full(4,-.5),1,a=.07,g=.23)
base=255*encode(body);final=f['encoded'];control=((final+5)-(base+5))-(final-base)
save(HERE/'encoded-control.json',dict(label='CONTROL ONLY, after composition and encoding',addedCodes=5,maxExcessChange=float(abs(control).max())))
# The eroded statistic is not an additive variance partition: pixels, mean and
# population change. Keep it as a sensitivity, not a causal attribution to shadow.
m=json.loads((HERE/'canonical-metrics.json').read_text())['rows']
cohort=json.loads((HERE.parent/'2026-09-22-w33-g2-landing/chroma-cut.json').read_text())['cells']
mr=[]
for c in cohort:
 cell=c['profile']+'/'+c['scene'];r=next(r for r in m if r['cell']==cell)
 current=r['erosion'][0]['web']['stdDev'];stored=r['storedMaterial']['interiorStdDevWeb']['value']
 assert abs(current-stored)<1e-12
 mr.append(dict(cell=cell,role=r['role'],erosion=r['erosion'],referenceGenerationForW35=current,
                stdDevFractionChange=[e['web']['stdDev']/current-1 if e['web'] else None for e in r['erosion']],
                ringVarianceSensitivity=r['varianceRingFraction'],matchesMatrix=abs(current-stored)))
save(HERE/'m2-gated-attribution.json',dict(cells=mr,rule='erosion is sensitivity, not additive ring variance or a prediction of a correct fit',tolerance=.02))
# Population and byte pins support independent replay, not a test of prose.
files=['domain.json','profiles.json.gz','deep-bars.json.gz','canonical-metrics.json','canonical-solids.json','native-law-fits.json','native-grey-law-fits.json','candidate-residuals.json.gz','identity-proof.json']
save(HERE/'pins.json',dict(sha256={f:hashlib.sha256((HERE/f).read_bytes()).hexdigest() for f in files},
    cells=len(p),barCells=len(b),barBins=sum(len(r['bins']) for r in b),profileRows=sum(len(r['rows']) for r in p),
    normalRuns=sum(r['runs'] for r in b if r['protocol']=='normal'),longRuns=sum(r['runs'] for r in b if r['protocol']=='long'),
    m2Cells=len(mr),canonicalMetricCells=len(m),maxBar=max(x['maxBar'] for x in barhead)))
with (HERE/'line-level-table.csv').open('x') as f:
 writer=csv.writer(f);writer.writerow(['cell','role','deep_R','deep_G','deep_B','web_minus_native_R','web_minus_native_G','web_minus_native_B','width_device_px','line_excess_G','last_ramp_excess_G'])
 for r in lines:
  level=next(x for x in levels if x['cell']==r['cell'])
  writer.writerow([r['cell'],r['role'],*r['deepRGB'],*level['levelMiss'],r['widthPartitionDevicePx'],str([v[1] for v in r['lineExcessRGB']]),r['rampLastExcessRGB'][1]])
print('populations',json.loads((HERE/'pins.json').read_text()))
print('M2 max erosion fraction',max(abs(v) for r in mr for v in r['stdDevFractionChange'] if v is not None))
