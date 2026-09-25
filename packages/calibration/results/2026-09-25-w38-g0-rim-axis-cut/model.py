"""W38 existing-leaf forward replay, beside W35/W37; never runtime code."""
import base64,gzip,hashlib,io,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;CAL=HERE.parent.parent;ROOT=CAL.parent.parent
G0=HERE.parent/'2026-09-25-w37-g0-edge-identification'
sys.path.insert(0,str(HERE.parent/'2026-09-24-w35-g0-edge-cut'))
import edge
MATERIALS=json.loads((HERE.parent/'2026-09-24-w36-g1-black-branch/resolved-materials.json').read_text())
WEIGHTS=np.array([.2126,.7152,.0722]);SCALE=.7071**.85

def material(scheme):
    # This preserved pre-black-branch material has the exact current rim/shadow
    # and tone-collapse leaves. No body solve is evaluated by this instrument.
    return MATERIALS[f'apple-macos-27.0-1x-{scheme}-standard-glass0.5']

def params(scheme,candidate='old'):
    m=material(scheme);o=m['optics']['regular']
    p=dict(axis=m['rimLitAxis'],exponent=o['rimLitExponent'],widths=[o['rimWidth'],o['rimWidth2x']],a=o['rimAlpha'],g=o['rimLevelGain'],along=o['rimAlongSideSlope'],shadowProduct=o['shadowDepth']*o['shadowAlpha'])
    if candidate=='C1':p.update(axis=[0,-1],a=p['a']*SCALE,g=p['g']*SCALE)
    return p

def inputs(structured=True,web=False):
    wave=edge.W.default_wave();repeat=wave.reader(edge.G1/'repeat');probe=wave.reader(edge.G1/'probe')
    profiles=json.loads(gzip.decompress((HERE.parent/'2026-09-24-w35-g0-edge-cut/profiles.json.gz').read_bytes()))
    black={r['cell']:r for r in json.loads((G0/'diagnostics.json').read_text())['w36BlackReplay']}
    oldweb=edge.WebReader.w34() if web else None;records=[]
    for rec in profiles:
        cell=rec['cell'];sid=cell.split('/')[1]
        # Admission precedes ANY image/crop read, strengthening W35's guard.
        if wave.roles[sid]!='calibration' or not cell.endswith('__rest'):continue
        if not structured and rec['backgroundKind']!='solid':continue
        crop=json.loads(gzip.decompress(repeat.read(cell,'crop')))
        run=next(r for r in crop['runs'] if r['admitted'] and r['protocol']=='normal')
        raw=base64.b64decode(crop['states'][run['state']]);assert hashlib.sha256(raw).hexdigest()==run['state']
        p=edge.I.unpack(raw);d,nx,ny,arc,angle,whole=edge.geometry(p);s=p['scale']
        n=np.asarray(Image.open(io.BytesIO(probe.read(cell,'png'))).convert('RGB'),float)
        b=np.median(n[d<=-6*s],0);assert np.array_equal(b,rec['deep']['nativeMedian'])
        wb=None;origin='NOT READ: native-only identification'
        if web:
            w=np.asarray(Image.open(io.BytesIO(oldweb.read(cell))).convert('RGB'),float)
            wb=np.median(w[d<=-6*s],0);assert np.array_equal(wb,rec['deep']['webMedian'])
            origin='W34 historical non-black; unchanged by compact W36 black branch'
            if cell in black:wb=np.array(black[cell]['deep']);origin='W36 retained black price; G0 provenance.json'
        circular=p['component']['kind']=='capsule-circular'
        admitted=whole if circular else (~arc)&(np.maximum(abs(nx),abs(ny))>1-1e-10)&(d<=-.5+1e-10)
        domain=(d>=-6*s)&(d<0)&admitted;bins=[]
        for part,pm in [('arc',arc),('straight',~arc)]:
            for sh in range(-6*s,0):
                for a in range(16):
                    mask=domain&pm&(d>=sh)&(d<sh+1)&(angle==a);count=int(mask.sum())
                    if count:bins.append(dict(part=part,shell=sh,bin=a,pixels=count,indices=np.flatnonzero(mask),admissible=count>=4))
        ix=np.flatnonzero(domain);remap=np.full(d.size,-1);remap[ix]=np.arange(len(ix))
        for bn in bins:bn['indices']=remap[bn['indices']]
        yy,xx=np.indices(d.shape);originpx=np.array(p['component']['suppliedPaths'][0]['frameOrigin'])*s+p['alignment']['translationDevicePx'];half=np.array(p['component']['size'])*s/2
        along=np.clip(((xx+.5-originpx[0]-half[0])/half[0])*((yy+.5-originpx[1]-half[1])/half[1]),-1,1)
        scheme='dark' if '-dark-' in cell else 'light';m=material(scheme);span=min(p['component']['size']);u=np.clip((span-m['sizeSpanMin'])/(m['sizeSpanMax']-m['sizeSpanMin']),0,1);k=u*u*(3-2*u)
        records.append(dict(cell=cell,role='calibration',scale=s,scheme=scheme,circular=circular,geometry=p['component']['kind'],span=span,backgroundKind=rec['backgroundKind'],body=b,webBody=wb,webOrigin=origin,native=n.reshape(-1,3)[ix],d=d.ravel()[ix]/s,nx=nx.ravel()[ix],ny=ny.ravel()[ix],along=along.ravel()[ix],bins=bins,k=k,reach=min(8*(1+(m['lensSizeGainMax']-1)*k),span/2)))
    return records

def predict(r,p,body=None):
    body=r['body'] if body is None else body
    lit=np.maximum(abs(r['nx']*p['axis'][0]+r['ny']*p['axis'][1])*np.sqrt(2),1e-6)**p['exponent']
    return edge.forward(edge.decode(body/255),r['d'],1,a=p['a'],g=p['g'],width=p['widths'][r['scale']-1],shadow_depth=p['shadowProduct'],shadow_alpha=1,shadow_reach=r['reach'],lit=lit,along=np.maximum(1+p['along']*r['k']*r['along'],0))['encoded']

def stratum(r,bn):
    if r['backgroundKind']!='solid':return 'structured-diagnostic'
    if not r['circular']:return 'noncircular-transfer'
    return ('greys' if '/grey-' in r['cell'] else 'solids')+'-'+bn['part']
