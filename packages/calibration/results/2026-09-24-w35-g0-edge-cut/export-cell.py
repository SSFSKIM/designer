"""Guarded pixel transport to the existing TypeScript metrics, not a path reader."""
import base64, gzip, io, json, sys
from pathlib import Path
from PIL import Image
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'2026-09-23-w34-g0-contour-bed'))
from w35_readers import CanonicalNativeReader, WebReader, W
import instrument as I
cell=sys.argv[2];source=sys.argv[1]
if source=='canonical':
    native=CanonicalNativeReader();profile,sid=native.roles.admit(cell)
    web=WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
    scene=native.roles.scenes[sid];spec=native.roles.spec
    value=dict(cell=cell,role=native.roles.roles[sid],component=spec['components'][scene['component']],
               canvas=spec['canvas'],scale=2 if '-2x-' in profile else 1,
               native=base64.b64encode(native.read(cell)).decode(),
               web=base64.b64encode(web.read(cell)).decode(),
               background=base64.b64encode(native.read(cell,'background')).decode())
elif source=='w34':
    wave=W.default_wave();rep=wave.reader(HERE.parent/'2026-09-23-w34-g1-contour-sitting/repeat')
    probe=wave.reader(HERE.parent/'2026-09-23-w34-g1-contour-sitting/probe')
    crop=json.loads(gzip.decompress(rep.read(cell,'crop')))
    run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal')
    p=I.unpack(base64.b64decode(crop['states'][run['state']]))
    f=io.BytesIO();Image.fromarray(p['background']).save(f,format='PNG')
    profile,sid=cell.split('/');scene=wave.scenes[sid]
    value=dict(cell=cell,role=wave.roles[sid],component=wave.spec['components'][scene['component']],
               canvas=wave.spec['canvas'],scale=p['scale'],
               native=base64.b64encode(probe.read(cell,'png')).decode(),
               web=base64.b64encode(WebReader.w34().read(cell)).decode(),
               background=base64.b64encode(f.getvalue()).decode())
else:raise ValueError('unknown declared source')
print(json.dumps(value))
