#!/usr/bin/env python3.12
"""W47 G0 (f), DL3 v1.1: the predeclared half-excess criterion, never a positional choice.

Reproduce: python3.12 -B read.py [--renders ~/vitrea-w47/diag]
Default input is the committed render tree alongside this script. The original canonical PNG
bytes and cell metadata are archived as reference/; compare those to live canonical when archiving.
Weights are the actual shader's kScatter, packed as round(kScatter*65535) into RG byte channels;
blue 255 is ramp band, 254 is beyond reach. Read only inside the native silhouette eroded 4 CSS px,
the SAME support as W44 T1-fine. This avoids coverage/compositor edge pixels. Quantization <= 0.5/65535.
The debug branch evaluates after the ordinary field reads and full W30 conditioned kScatter law.
It alters no uniform feeding that law. It never drives the choice; only the four whole-cell Rs do.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
HERE=Path(__file__).resolve().parent
CAL=HERE.parents[2]
ROOT=CAL.parents[1]
sys.path.insert(0,str(CAL/'results/2026-10-03-w44-g1-refit/cuts'))
import readings as W44
SCENES=['checkerboard-8__rrect-md__inactive','checkerboard-8__rrect-lg__inactive']
LABELS=['control','body','deep','weights','zero-share']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rgb=lambda p:np.asarray(Image.open(p).convert('RGB'))

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--renders',type=Path,default=HERE/'renders')
 ap.add_argument('--out',type=Path,default=HERE);ap.add_argument('--check',action='store_true');args=ap.parse_args()
 def emit(name,text):
  p=args.out/name
  if args.check:
   assert p.read_text()==text, f'{name}: committed reading does not reproduce'
  else:
   if p.exists(): raise SystemExit(f'{p} exists; use --check or --out into scratch')
   p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
 rows=[];identity=[]
 for scale in (1,2):
  profile=f'apple-macos-27.0-{scale}x-dark-standard-glass0.25'
  for scene in SCENES:
   paths={l:args.renders/l/f'{scale}x/web-captures'/profile/scene for l in LABELS}
   png=lambda l:paths[l]/f'{scene}__webgpu.png'
   reference=HERE/'reference'/profile/scene/f'{scene}__webgpu.png'
   assert png('control').read_bytes()==reference.read_bytes(), 'control differs from canonical reference'
   assert png('zero-share').read_bytes()==reference.read_bytes(), 'explicit zero-share differs'
   cell=json.loads((reference.parent/'cell__webgpu.json').read_text())
   assert 'd0219cd684bf' in cell['capturePath'] and 'f0b36a71772a' in cell['capturePath']
   identity.append(dict(profile=profile,scene=scene,canonicalCapturePath=cell['capturePath'],
    sha256=sha(reference),controlSha256=sha(png('control')),explicitZeroShareSha256=sha(png('zero-share')),
    controlEqual=True,explicitZeroShareEqual=True))
   native=ROOT/'apps/reference-apple/fixtures'/profile/f'{scene}.png'
   images={l:rgb(png(l)) for l in LABELS};images['native']=rgb(native)
   geometry=W44.cell_geometry(profile,scene,images['native'])
   support=geometry['eroded']
   values={'native':W44.read(profile,scene,images['native'],images['control'],geometry)['native']['fine']}
   for label in ['control','body','deep']:
    values[label]=W44.read(profile,scene,images['native'],images[label],geometry)['web']['fine']
   E=values['control']-values['native'];assert E>0
   ratios={l:(values['control']-values[l])/E for l in ('body','deep')}
   reports={l:json.loads((paths[l]/'report__webgpu.json').read_text()) for l in LABELS}
   debug={l:reports[l]['page']['w47DiagnosticScratch'] for l in LABELS}
   # Pin every law-driving lane between control/body/deep and the weight render.
   # Scratch lanes133..135 differ; all others must agree before the mask can explain any form.
   uniform={l:np.array(debug[l]['weights']['uniform']) for l in LABELS}
   lanes=[i for i in range(len(uniform['control'])) if i not in (133,134,135)]
   for l in LABELS:
    assert np.array_equal(uniform[l][lanes],uniform['control'][lanes]), (profile,scene,l,'uniform changed')
   assert debug['control']['plan']['deepLod']==4 if scale==1 else debug['control']['plan']['deepSigma']==7
   w=images['weights'].astype(np.uint32);deep=(w[:,:,0]*256+w[:,:,1])/65535
   assert np.all(np.isin(w[:,:,2][support],[254,255]))
   residuals={}
   for l in ['native','control','body','deep']:
    L=W44.P.luminance(images[l]);residuals[l]=L-gaussian_filter(L,W44.FINE_SIGMA_DEVICE)
   masks={}
   for name,blue in [('ramp',255),('beyond',254)]:
    mask=support & (w[:,:,2]==blue);count=int(mask.sum())
    masks[name]=dict(pixels=count,bodyWeightMean=float((1-deep[mask]).mean()) if count else None,
     deepWeightMean=float(deep[mask].mean()) if count else None,
     fine={l:float(a[mask].std()) if count else None for l,a in residuals.items()})
   assert (masks['beyond']['pixels']>0)==(scale==2 and 'rrect-lg' in scene)
   rows.append(dict(profile=profile,scale=scale,scene=scene,spanCss=96 if 'rrect-md' in scene else 160,
    fine=values,E=E,R=ratios,pixels=int(support.sum()),masks=masks,
    edgeDensity=debug['control']['weights']['statistic'],uniform=uniform['control'].tolist(),
    plans={l:debug[l]['plan'] for l in ('control','body','deep')},
    pngSha256={l:sha(png(l)) for l in LABELS},nativeSha256=sha(native)))
 means={l:float(np.mean([r['R'][l] for r in rows])) for l in ('body','deep')}
 clears={l:all(r['R'][l]>=0.5 for r in rows) for l in ('body','deep')}
 chosen=[l.upper() for l in ('body','deep') if clears[l] and means[l]>means['deep' if l=='body' else 'body']]
 verdict=chosen[0] if len(chosen)==1 else 'STOP'
 per_scale={str(s):{l:dict(meanR=float(np.mean([r['R'][l] for r in rows if r['scale']==s])),
  clearsEveryCell=all(r['R'][l]>=0.5 for r in rows if r['scale']==s)) for l in ('body','deep')} for s in (1,2)}
 out=dict(what='W47 G0(f), Decision Log3 v1.1, predeclared depth-split diagnostic',
  definition='SD(L-G(L,4 device px)), linear luminance, native silhouette eroded4 CSS px; W44 G1 read()',
  criterion='R=(reference-form)/(reference-native); >=0.5 on every cell and scale and larger pooled mean R',
  maskMethod=__doc__,maskSupport='W44 native silhouette eroded4 CSS px; ramp classification from real field depth',
  weightQuantizationMaximumError=0.5/65535,
  readerHashes={n:sha(CAL/'results/2026-10-03-w44-g1-refit/cuts'/n) for n in ('readings.py','bed.py')},
  referenceActiveDocument='d0219cd684bf',referenceRecededDocument='f0b36a71772a',
  forms=dict(body='source blurred at6 CSS px mixed into body before kScatter',
   deep='source blurred at hypot(actual deep sigma,6 CSS px), mixed after W30 second tap'),
  rows=rows,pooledMeanR=means,clearsEveryCell=clears,perScale=per_scale,verdict=verdict,
  controlIdentity=identity,
  surprises=[
   'Charter original: at2x the receded deep is sigma14 CSS px. Renderer actual: sizeHeavyTapSigma2x14 is device px; heavySigmaCssFor divides by DPR, so sigmaDeep7 CSS px; deepFine hypot(7,6)=9.2195444573 CSS px. The original sentence is preserved as provenance, corrected here. Body width6 CSS px is unchanged. The deep diagnostic broadens7 to9.2195, not14 to15.2315.',
   'At1x the shader clamps scatterLod at4. The pyramid measured chainLevelSigma(4)=13.418 level0 texels, density1, hence13.418 CSS px; deepFine hypot(13.418,6)=14.6983918848 CSS px. Fractional LOD interpolation is not used for the declared1x cells.',
   'heavyTapPlan uses no new pass shape, but the charter level0 claim is false on this source density. For width6 CSS px: body uses chain level2 plus residual1.25586223 at1x and level3 plus residual1.24618768 at2x. For width2/3/4 CSS px, plan levels are1/1/2 at1x and2/2/3 at2x. The6 CSS px grid remains CSS px and ideal-Gaussian lowest-mode attenuation0.003881 remains only a prediction; the actual existing chain+residual renderer is the referee.'
  ])
 emit('reading.json',json.dumps(out,indent=2)+'\n')
 emit('control-identity.json',json.dumps(identity,indent=2)+'\n')
 lines=[f'W47 G0(f): {verdict}', 'T1-fine, linear luminance SD, native silhouette eroded4 CSS px.',
  'scale scene native reference body deep E Rbody Rdeep']
 for r in rows:
  v=r['fine'];lines.append(f"{r['scale']}x {r['scene']} "+' '.join(f'{v[k]:.10f}' for k in ('native','control','body','deep'))+f" {r['E']:.10f} {r['R']['body']:.8f} {r['R']['deep']:.8f}")
  for name,m in r['masks'].items():lines.append(f"  {name}: {json.dumps(m)}")
  lines.append(f"  source edge density: {r['edgeDensity']:.12f}")
 lines += [f'Pooled arithmetic mean R: {means}',f'Every-cell half-excess criterion: {clears}',
  'Control AND explicit zero-share PNGs are byte-identical to canonical on all4 cells.',
  'Masks explain only; their weights come from shader output, not ramp starts.',*out['surprises']]
 emit('reading.txt','\n'.join(lines)+'\n');print('\n'.join(lines))
if __name__=='__main__': main()
