"""Guarded native/shipped/candidate triptychs, raw pixels and calibrated x8 (§5.179)."""
import hashlib,importlib.util,io,json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'2026-09-24-w35-g0-edge-cut'))
import edge
from w35_readers import WebReader,CanonicalNativeReader
spec=importlib.util.spec_from_file_location('colour',HERE.parent/'2026-09-22-w33-g1b-rim-fit/read-round.py');colour=importlib.util.module_from_spec(spec);spec.loader.exec_module(colour)
plans={p['profile']:p for p in json.loads((HERE/'candidate-plans.json').read_text())}
wave=edge.W.default_wave();native34=wave.reader(edge.G1/'probe');nativeC=CanonicalNativeReader()
old34=WebReader.w34();oldC=WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',16)
small=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',12)
lsb=float(np.linalg.norm(colour.lab(np.ones((1,1,3)))-colour.lab(np.zeros((1,1,3))))*8*255)
selected=[]
for scheme in ['light','dark']:
 for scale in [1,2]:
  profile=f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5'
  for pose in ['rest','inactive']:selected.append((profile,'grey-0__circular-120__'+pose,'w34'))
  if scale==1:
   for pose in ['rest','inactive']:
    for bg in ['impulse','photo']:selected.append((profile,bg+'__capsule-button__'+pose,'canonical'))
   selected.append((profile,'grey-32__circular-120__rest','w34'))
output=HERE/'sheets';output.mkdir(exist_ok=True);records=[]
for profile,sid,origin in selected:
 cell=profile+'/'+sid;plan=plans[profile]
 reader=(WebReader.w34 if origin=='w34' else WebReader.canonical)(Path(plan['root'])/'web-captures')
 nraw=native34.read(cell,'png') if origin=='w34' else nativeC.read(cell)
 oraw=(old34 if origin=='w34' else oldC).read(cell);craw=reader.read(cell)
 report=json.loads(reader.read(cell,'report'))
 for field in ['materialProfile','recededProfile']:
    doc=report[field];assert hashlib.sha256(Path(doc['path']).read_bytes()).hexdigest()[:12]==doc['sha256']
 ims=[Image.open(io.BytesIO(raw)).convert('RGB') for raw in [nraw,oraw,craw]]
 n,o,c=[np.asarray(im,float) for im in ims];h,w=n.shape[:2];gap=10
 page=Image.new('RGB',(3*w+2*gap,2*h+142),'white');draw=ImageDraw.Draw(page)
 draw.text((0,3),profile+' / '+sid,font=font,fill='black')
 for i,(label,im) in enumerate(zip(['Native','Shipped WebGPU','W36 candidate WebGPU'],ims)):
    draw.text((i*(w+gap),28),label,font=font,fill='black');page.paste(im,(i*(w+gap),50))
 panels=[]
 for i,(label,im) in enumerate([('Shipped - native',o),('Candidate - native',c)]):
    diff=np.minimum(255,np.linalg.norm(colour.lab(n)-colour.lab(im),axis=2)*8*255)
    delta=Image.fromarray(np.repeat(np.rint(diff).astype('uint8')[:,:,None],3,axis=2))
    y=h+72;draw.text((i*(w+gap),y),label+' | abs OKLab x8',font=font,fill='black');page.paste(delta,(i*(w+gap),y+22))
    draw.text((i*(w+gap),y+h+25),f'LSB 0 -> 1: {lsb:.2f}/255; black=0 error, white>=0.125',font=small,fill='black')
    panels.append(dict(label=label,lsbBlackOneByteAmplification=lsb,maxChannelCodes=float(np.max(abs(im-n)))))
 draw.text((2*(w+gap),h+80),'Pixels shown without resampling.\nDeep medians and native envelopes\nare separate from these full-frame\nabsolute-error panels.\n\nGrey middle, chroma and rim\nare not claimed closed.',font=font,fill='black')
 name=profile.removeprefix('apple-macos-27.0-')+'__'+sid+'.png';page.save(output/name)
 records.append(dict(cell=cell,origin=origin,file=str(output/name),nativeSha256=hashlib.sha256(nraw).hexdigest(),shippedSha256=hashlib.sha256(oraw).hexdigest(),candidateSha256=hashlib.sha256(craw).hexdigest(),panels=panels,documents={k:report[k]['sha256'] for k in ['materialProfile','recededProfile']}))
with (HERE/'sheet-readings.json').open('x') as f:json.dump(records,f,indent=2);f.write('\n')
print('sheets',len(records),'LSB',lsb)
