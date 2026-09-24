"""Price the predeclared trial; do not fit its structured residuals (§5.178)."""
import base64,gzip,hashlib,io,json
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
from cut import HERE,edge,save
from w35_readers import WebReader,CanonicalNativeReader
plans=json.loads((HERE/'candidate-plans.json').read_text())
projection={r['cell']:r for r in json.loads((HERE/'projection.json').read_text())}
checks={c['cell']:c for r in map(json.loads,(HERE/'browser-runs.txt').read_text().splitlines()) for c in r.get('checks',[])}
baseline={r['cell']:r for name in ['l1-baseline.json','probe-level-diagnostics.json'] for r in json.loads((HERE/name).read_text())}
baseDeep={r['cell']:r for r in json.loads((HERE/'deep-cut.json').read_text())}
wave=edge.W.default_wave();probe=wave.reader(edge.G1/'probe');repeat=wave.reader(edge.G1/'repeat')
rows=[];greys=[]
for plan in plans:
    profile=plan['profile'];root=Path(plan['root']);matrix=json.loads((root/'matrix.json').read_text())
    indexed={c['key']['sceneId']:c for c in matrix['cells']}
    for sid in plan['scenes']:
        cell=profile+'/'+sid;p=projection[cell];reader=WebReader.w34(root/'web-captures') if p['origin']=='w34' else WebReader.canonical(root/'web-captures')
        raw=reader.read(cell);assert checks[cell]['used'];assert hashlib.sha256(raw).hexdigest()==checks[cell]['pngSha256']
        image=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),float)
        if p['origin']=='w34':
            crop=json.loads(gzip.decompress(repeat.read(cell,'crop')))
            run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal')
            body=edge.I.unpack(base64.b64decode(crop['states'][run['state']]))
            mask=edge.geometry(body)[0]<=-6*body['scale'];old=baseDeep[cell]
            median=np.median(image[mask],0);native=np.array(old['nativeMedian']);censored=[i for i in range(3) if native[i]==255 or median[i]==255]
            greys.append(dict(cell=cell,role=p['originalRole'],nativeMedian=native.tolist(),
                shippedMedian=old['webMedian'],candidateMedian=median.tolist(),missCodes=(median-native).tolist(),
                pixels=int(mask.sum()),censoredChannels=censored,
                candidateSpread=(image[mask].max(0)-image[mask].min(0)).tolist(),
                closes=all(abs(median[i]-native[i])<=1 for i in range(3) if i not in censored)))
        else:
            c=indexed.get(sid);before=baseline[cell]
            if c is None:rows.append(dict(cell=cell,status='UNMEASURED standard metrics'));continue
            m=c['material'];v=lambda name:m.get(name,{}).get('value')
            n,w=v('interiorMeanNative'),v('interiorMeanWeb');err=abs(w-n)
            cn,cw=v('chromaStructureRatioNative'),v('chromaStructureRatioWeb')
            sd=v('interiorStdDevWeb');sd0=before['interiorStdDevWeb']
            rows.append(dict(cell=cell,role=p['originalRole'],native=n,shipped=before['webMean'],candidate=w,
                nativeMatchesBaseline=abs(n-before['nativeMean'])<1e-12,
                baselineError=before['absoluteError'],candidateError=err,growth=err-before['absoluteError'],
                levelStopPass=err<=.055 and err-before['absoluteError']<=.005,
                M1=None if cn is None or not cn else cw/cn,
                baselineM1=None if before['chromaNative'] is None or not before['chromaNative'] else before['chromaWeb']/before['chromaNative'],
                structureDelta=None if sd0 is None or not sd0 else (sd-sd0)/sd0,
                perceptual={k:a['value'] for k,a in c['perceptual'].items() if isinstance(a,dict)},
                sourceMatrix=str(root/'matrix.json')))
            if sid=='photo__rrect-md__rest' and '-1x-' in profile:
                native=Image.open(io.BytesIO(CanonicalNativeReader().read(cell))).convert('RGB')
                shipped=Image.open(io.BytesIO(WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures').read(cell))).convert('RGB')
                candidate=Image.fromarray(image.astype('uint8'));sheet=Image.new('RGB',(320,3*224),'white');draw=ImageDraw.Draw(sheet)
                for i,(label,im) in enumerate(zip(['Native','Shipped WebGPU','W36 shared-shift trial'],[native,shipped,candidate])):
                    draw.text((8,i*224+6),label,fill='black');sheet.paste(im,(0,i*224+24))
                sheet.save(HERE/('eye-photo-'+profile+'.png'))
save('candidate-greys.json',greys);save('candidate-structured.json',rows)
print('Rendered',len(greys),'W34 grey cells;',len(rows),'canonical structured; deep passes',sum(r['closes'] for r in greys))
print('Structured level failures',[(r['cell'],r['growth'],r['candidateError']) for r in rows if not r.get('levelStopPass',False)])
print('Photo',[(r['cell'],r['growth'],r['M1'],r['structureDelta']) for r in rows if '/photo__' in r['cell']])
