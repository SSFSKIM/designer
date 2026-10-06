#!/usr/bin/env python3.12
"""Requested liveness control for W47 G0(f): exact PNG differences, never a fit objective.

python3.12 -B read.py [--check] — reads archived PNGs and refuses to overwrite a reading.
Compares RGB over the whole image; also reports differences within the original T1 eroded mask
on the fine cells. Coarse cells deliberately need no native fixture read.
"""
from pathlib import Path
import argparse,hashlib,json,sys
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
DIAG=HERE.parent
CAL=HERE.parents[3]
ROOT=CAL.parents[1]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rgb=lambda p:np.asarray(Image.open(p).convert('RGB')).astype(np.int16)
sys.path.insert(0,str(CAL/'results/2026-10-03-w44-g1-refit/cuts'))
import readings as W44

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--check',action='store_true');a=ap.parse_args()
 scenes=json.loads((ROOT/'apps/reference-apple/scenes.json').read_text())
 manifest=CAL/'results/2026-10-05-w46-g0-declaration/referees/referees.json'
 rows=[]
 for scale in (1,2):
  p=f'apple-macos-27.0-{scale}x-dark-standard-glass0.25'
  for label,scene,width in [('coarse-deep','checkerboard-64__rrect-md__inactive',6),
   ('fine-deep40','checkerboard-8__rrect-md__inactive',40),
   ('fine-deep40','checkerboard-8__rrect-lg__inactive',40)]:
   assert scene in scenes['split']['probe'] and scene not in manifest.read_text()
   assert scene in next(x['scenes'] for x in scenes['profiles'] if x['key']==p)
   target=HERE/'renders'/label/f'{scale}x/web-captures'/p/scene
   control=(HERE/'renders/coarse-control' if label=='coarse-deep' else DIAG/'renders/control')/f'{scale}x/web-captures'/p/scene
   n=f'{scene}__webgpu.png'; diff=np.abs(rgb(target/n)-rgb(control/n));pixel=diff.max(axis=2)
   trace=json.loads((target/'report__webgpu.json').read_text())['page']['w47DiagnosticScratch']
   u=trace['weights']['uniform'];assert u[133]==1 and u[134]==1 and u[135]==1
   assert trace['plan']['finePlan'] is not None
   row=dict(profile=p,scene=scene,widthCss=width,differentPixels=int((pixel>0).sum()),
    totalPixels=int(pixel.size),maxCodeDifference=int(pixel.max()),
    controlSha256=sha(control/n),deepSha256=sha(target/n),
    trace=dict(share=u[133],fineTexturePresent=u[134],deepSelector=u[135],plan=trace['plan']))
   if label=='fine-deep40':
    native=ROOT/'apps/reference-apple/fixtures'/p/f'{scene}.png'
    support=W44.cell_geometry(p,scene,rgb(native).astype(np.uint8))['eroded']
    row['erodedBody']=dict(differentPixels=int((pixel[support]>0).sum()),pixels=int(support.sum()),
     maxCodeDifference=int(pixel[support].max()))
   rows.append(row)
 assert all(r['differentPixels']>0 for r in rows if r['widthCss']==6), 'coarse control failed to demonstrate liveness'
 # Original four diagnostic deep renders carry live allocations and enabled bindings too.
 originals=json.loads((DIAG/'texture-trace.json').read_text())
 live=[r for r in originals if r['label']=='deep']
 assert len(live)==4 and all(r['textureAllocatedAndGateEnabled']==1 and r['finePlan'] for r in live)
 out=dict(what='Positive liveness controls requested by orchestrator after the declared diagnostic',
  definition='Differing pixel means any RGB channel differs; max code difference is maximum absolute RGB8 difference, whole PNG',
  rows=rows,originalDiagnosticDeepTrace=live,
  conclusion='Deep branch executes: broad checker structure moves at width6 on both scales. The original pitch8 sigma6 zero change is consistent with the deep component already suppressing fine structure, not a dead gate or unbound texture; the small sigma40 changes caution against claiming the entire deep texture is exactly flat. Width40 changes, if any, are tabled rather than presumed.',
  scope='No operator choice, refit, holdout or referee exposure. Primary BODY verdict remains the declared four-cell sigma6 reading.',
  inputs=dict(refereeManifestSha256=sha(manifest),scratchPatchSha256=sha(DIAG/'scratch-renderer.patch')))
 lines=['W47 G0(f) positive control','scale scene extraWidthCSS differingPixels maxCodeDifference']
 for r in rows:
  lines.append(f"{r['profile'].split('-')[3]} {r['scene']} {r['widthCss']} {r['differentPixels']} {r['maxCodeDifference']}")
  if 'erodedBody' in r:lines.append('  eroded body: '+json.dumps(r['erodedBody']))
 lines += [out['conclusion'],out['scope'],'Original deep sigma6 texture present and enabled on all4 diagnostic captures (trace archived).']
 for name,text in [('reading.json',json.dumps(out,indent=2)+'\n'),('reading.txt','\n'.join(lines)+'\n')]:
  path=HERE/name
  if a.check:assert path.read_text()==text
  else:
   if path.exists():raise SystemExit(f'{path} exists; use --check')
   path.write_text(text)
 print('\n'.join(lines))
if __name__=='__main__':main()
