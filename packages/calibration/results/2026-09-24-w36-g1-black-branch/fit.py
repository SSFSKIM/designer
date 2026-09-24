"""Black only, through the unchanged guarded W35/W34 readers (§5.179 DL5)."""
import base64,gzip,io,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'2026-09-24-w35-g0-edge-cut'))
import edge
wave=edge.W.default_wave();native=wave.reader(edge.G1/'probe');repeat=wave.reader(edge.G1/'repeat')
rows=[];fits=[];scratch=Path.home()/'vitrea-w36/scratch/black-branch'
for scheme in ['light','dark']:
  for pose in ['rest','inactive']:
    levels=[]
    for scale in [1,2]:
      profile=f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5';cell=profile+'/grey-0__circular-120__'+pose
      crop=json.loads(gzip.decompress(repeat.read(cell,'crop')))
      first=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal')
      p=edge.I.unpack(base64.b64decode(crop['states'][first['state']]))
      image=np.asarray(Image.open(io.BytesIO(native.read(cell,'png'))).convert('RGB'),float)
      deep=edge.geometry(p)[0]<=-6*scale;median=np.median(image[deep],0)
      assert deep.sum()>=4 and len(set(median))==1
      levels.append(float(edge.decode(median[0]/255)))
      rows.append(dict(cell=cell,role=wave.roles[cell.split('/')[1]],pixels=int(deep.sum()),nativeMedian=median.tolist(),linearLevel=levels[-1]))
    assert levels[0]==levels[1]
    name=f'apple-macos-27.0-1x-{scheme}-standard-glass0.5'+('-receded' if pose=='inactive' else '')
    doc=json.loads((ROOT/'packages/calibration/profiles'/(name+'.json')).read_text())
    leaves=dict(backdropToneBlackStrength=1,backdropToneBlackThin=levels[0],backdropToneBlackThick=levels[0])
    doc['patch'].update(leaves)
    doc['$w36-candidate']='UNSEALED tune path; thin=thick is an explicit span44 extrapolation, not a thick-black measurement.'
    path=scratch/'documents'/(name+'.json');path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x') as f:json.dump(doc,f,indent=2);f.write('\n')
    fits.append(dict(scheme=scheme,pose=pose,document=str(path),nativeCodes=rows[-1]['nativeMedian'][0],patch=leaves,thickRule='equal to thin; no independent thick-black anchor'))
for name,value in [('black-native.json',rows),('candidate-ordinates.json',fits)]:
    with (HERE/name).open('x') as f:json.dump(value,f,indent=2);f.write('\n')
print(json.dumps(fits,indent=2))
