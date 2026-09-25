"""W38 grounding only. Native conditioned grid, no validation or holdout payload opens."""
import sys,os,json,gzip,inspect,itertools,hashlib
from pathlib import Path
os.environ['PYTHONDONTWRITEBYTECODE']='1';sys.dont_write_bytecode=True
import numpy as np
R=Path(__file__).resolve().parents[4]; C=R/'packages/calibration';G=C/'results/2026-09-25-w37-g0-edge-identification';S=Path(__file__).resolve().parent/'memo-reproduction';S.mkdir(exist_ok=True)
sys.path.insert(0,str(G));import identify
edge=identify.edge
# Declare BEFORE loading image payloads. No adaptive enlargement.
declaration={'scope':'Native-only calibration active solids; fit circular-120 and circular-200, other calibration shapes transfer only. No validation payload reads. Opaque full coverage only.', 'axis':[0,-1], 'exponent':[.85,2,4], 'widthPairs':{'light':[[1,1],[1.5,1.5],[2.2,1.35],[6.5,5.85]],'dark':[[1,1],[1.5,1.5],[2.2,1.35],[3,2]]}, 'a':{'light':[.04,.08,.115],'dark':[.03,.055,.08]}, 'g':{'light':[-.122,0,.2],'dark':[.2,.44,.6]},'along':[0,.1], 'shadowDepth':[0,.35], 'shadowAlpha':[.05,.1], 'objective':'mean squared encoded RGB error, equal bin/channel mass, >=4 whole pixels; includes clipped channels as forward outputs, not inversions','comparison':'per-bin max channel MAE; better/worse only beyond 0.5 code; old native-conditioned treatment, NOT actual shipped render'}
assert not (S/'scores.json').exists(), 'refuse to overwrite recorded replay'
(S/'declaration.json').write_text(json.dumps(declaration,indent=2))
# Reuse G0 input geometry/binning verbatim, but filter BEFORE payload opens and remove web opens.
src=inspect.getsource(identify.inputs)
src=src.replace("if rec['backgroundKind']!='solid':continue", "if rec['backgroundKind']!='solid' or rec['role']!='calibration' or not rec['cell'].endswith('__rest'):continue")
a=src.index('        web=np.asarray');b=src.index('        circular=',a)
src=src[:a]+"        wb=b.copy();web_origin='NOT READ: native-only diagnostic'\n"+src[b:]
ns=identify.__dict__.copy();exec(src,ns); records=ns['inputs']()
materials=json.loads((C/'results/2026-09-24-w36-g1-black-branch/resolved-materials.json').read_text())
old=json.loads(gzip.decompress((G/'old-rim.json.gz').read_bytes()))['rows'];oldmap={(r['cell'],r['part'],r['shell'],r['bin']):r for r in old}
repro=[];oldpred={}; maxdiff=0
for r in records:
 m=materials[f"apple-macos-27.0-1x-{r['scheme']}-standard-glass0.5"];o=m['optics']['regular'];u=np.clip((r['span']-m['sizeSpanMin'])/(m['sizeSpanMax']-m['sizeSpanMin']),0,1);r['k']=u*u*(3-2*u)
 r['reach']=min(8*(1+(m['lensSizeGainMax']-1)*r['k']),r['span']/2)
 opts=dict(width=o['rimWidth'] if r['scale']==1 else o['rimWidth2x'],shadow_alpha=o['shadowAlpha'],shadow_depth=o['shadowDepth']*(1+(m['sizeShadowGainMax']-1)*r['k']),shadow_reach=r['reach'],lit=np.maximum(abs(r['nx']*m['rimLitAxis'][0]+r['ny']*m['rimLitAxis'][1])*np.sqrt(2),1e-6)**o['rimLitExponent'],along=np.maximum(1+o['rimAlongSideSlope']*r['k']*r['along'],0))
 pred=edge.forward(edge.decode(r['body']/255),r['d'],1,a=o['rimAlpha'],g=o['rimLevelGain'],**opts)['encoded'];shadow=edge.forward(edge.decode(r['body']/255),r['d'],1,**opts)['encoded'];oldpred[r['cell']]=pred
 for bn in r['bins']:
  ix=bn['indices']; key=(r['cell'],bn['part'],bn['shell'],bn['bin']);ref=oldmap[key]
  vals={'rimContributionRGB':(pred[ix]-shadow[ix]).mean(0),'shadowContributionRGB':(shadow[ix]-r['body']).mean(0),'oldExcessRGB':(pred[ix]-r['body']).mean(0),'nativeExcessRGB':(r['native'][ix]-r['body']).mean(0)}
  maxdiff=max(maxdiff,max(float(np.max(abs(v-ref[k]))) for k,v in vals.items()));repro.append({**ref,**{k:v.tolist() for k,v in vals.items()}})
print('reproduced',len(records),len(repro),maxdiff,flush=True)
(S/'reproduction.json').write_text(json.dumps({'cells':len(records),'bins':len(repro),'maximumDifference':maxdiff,'rows':repro}))
results=[];binsout=[]
for scheme in ['light','dark']:
 fit=[r for r in records if r['scheme']==scheme and r['circular']]
 # vectorized forward, bin weight means each bin contributes equally.
 body=np.concatenate([np.broadcast_to(edge.decode(r['body']/255),r['native'].shape) for r in fit]);target=np.concatenate([r['native'] for r in fit]);d=np.concatenate([r['d'] for r in fit]);ny=np.concatenate([r['ny'] for r in fit]);along=np.concatenate([r['k']*r['along'] for r in fit]);scale=np.concatenate([np.full(len(r['d']),r['scale']) for r in fit]);reach=np.concatenate([np.full(len(r['d']),r['reach']) for r in fit]);weight=np.concatenate([r['weight'] for r in fit]);norm=3*weight.sum();best=None;trials=[]
 for exp,widths,a,g,slope,depth,alpha in itertools.product(declaration['exponent'],declaration['widthPairs'][scheme],declaration['a'][scheme],declaration['g'][scheme],declaration['along'],declaration['shadowDepth'],declaration['shadowAlpha']):
  opts=dict(width=np.where(scale==1,widths[0],widths[1]),a=a,g=g,shadow_depth=depth,shadow_alpha=alpha,shadow_reach=reach,lit=np.maximum(abs(ny)*np.sqrt(2),1e-6)**exp,along=np.maximum(1+slope*along,0))
  pred=edge.forward(body,d,1,**opts)['encoded'];score=float(np.sum((pred-target)**2*weight[:,None])/norm)
  row=dict(exponent=exp,widths=widths,a=a,g=g,along=slope,shadowDepth=depth,shadowAlpha=alpha,mse=score)
  trials.append(row)
  if best is None or score<best['mse']:best=row
 print(scheme,'best',best,'trials',len(trials),flush=True)
 results.append(dict(scheme=scheme,fitCells=[r['cell'] for r in fit],best=best,trials=len(trials)))
 for r in records:
  if r['scheme']!=scheme:continue
  p=edge.forward(edge.decode(r['body']/255),r['d'],1,width=best['widths'][r['scale']-1],a=best['a'],g=best['g'],shadow_depth=best['shadowDepth'],shadow_alpha=best['shadowAlpha'],shadow_reach=r['reach'],lit=np.maximum(abs(r['ny'])*np.sqrt(2),1e-6)**best['exponent'],along=np.maximum(1+best['along']*r['k']*r['along'],0))['encoded']
  for bn in r['bins']:
   if not bn['admissible']:continue
   ix=bn['indices'];err=np.abs(p[ix]-r['native'][ix]).mean(0);old_err=np.abs(oldpred[r['cell']][ix]-r['native'][ix]).mean(0);delta=float(max(err)-max(old_err))
   binsout.append(dict(cell=r['cell'],scheme=scheme,circular=r['circular'],geometry=r['geometry'],part=bn['part'],shell=bn['shell'],bin=bn['bin'],pixels=bn['pixels'],residualRGB=err.tolist(),oldResidualRGB=old_err.tolist(),delta=delta,verdict='better' if delta<-.5 else 'worse' if delta>.5 else 'same'))
 (S/f'trials-{scheme}.json').write_text(json.dumps(trials))
summary=[]
for scheme in ['light','dark']:
 for label,sel in [('grey-straights',lambda b:'/grey-' in b['cell'] and b['part']=='straight'),('grey-arcs',lambda b:'/grey-' in b['cell'] and b['part']=='arc'),('solids',lambda b:'/grey-' not in b['cell']),('all',lambda b:True),('transfer',lambda b:True)]:
  rows=[b for b in binsout if b['scheme']==scheme and b['circular']==(label!='transfer') and sel(b)]
  summary.append(dict(scheme=scheme,stratum=label,bins=len(rows),maxResidual=max(max(b['residualRGB']) for b in rows),oldMaxResidual=max(max(b['oldResidualRGB']) for b in rows),meanMaxResidual=float(np.mean([max(b['residualRGB']) for b in rows])),counts={v:sum(b['verdict']==v for b in rows) for v in ['better','same','worse']}))
(S/'scores.json').write_text(json.dumps({'declaration':declaration,'fits':results,'summary':summary,'worstWorsenings':sorted(binsout,key=lambda b:b['delta'],reverse=True)[:20],'bins':binsout},indent=2));print(json.dumps(summary,indent=2))
