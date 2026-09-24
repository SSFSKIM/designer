"""Read the boundary stand-down diagnostic on the same guarded deep domain (§5.179)."""
import base64,gzip,io,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'2026-09-24-w35-g0-edge-cut'))
import edge
from w35_readers import WebReader,confined
wave=edge.W.default_wave();repeat=wave.reader(edge.G1/'repeat')
previous={r['cell']:r for r in json.loads((HERE/'price-css-greys.json').read_text())};rows=[]
for p in json.loads((HERE/'css-boundary-isolation-plans.json').read_text()):
    cell=p['profile']+'/grey-0__circular-120__rest';reader=WebReader.w34(Path(p['root'])/'web-captures');profile,sid=reader.admit(cell)
    folder=confined(reader.root,reader.root/profile/sid)
    meta=json.loads((folder/'cell__css.json').read_text());assert meta['deterministic'] and meta['repeatNoise']==0
    crop=json.loads(gzip.decompress(repeat.read(cell,'crop')));run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal');body=edge.I.unpack(base64.b64decode(crop['states'][run['state']]))
    mask=edge.geometry(body)[0]<=-6*body['scale'];im=np.asarray(Image.open(folder/(sid+'__css.png')).convert('RGB'),float);median=np.median(im[mask],0)
    before=previous[cell];rows.append(dict(cell=cell,native=before['native'],candidate=before['median'],boundaryOff=median.tolist(),boundaryOffMinusNative=(median-np.array(before['native'])).tolist(),boundaryContribution=(np.array(before['median'])-median).tolist(),deepPixels=int(mask.sum())))
result=dict(rows=rows,qualification='Diagnostic only: rimAlpha, rimLevelGain and shadowAlpha are zeroed together. This isolates the combined existing CSS boundary projection, not which boundary leaf; none of these diagnostic values will ship.')
with (HERE/'css-boundary-isolation.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
