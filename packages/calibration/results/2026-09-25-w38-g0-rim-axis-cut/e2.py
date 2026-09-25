"""W38 E2's read-only, fixed-generation rendered-edge regression cut (clause 1c).

--declare records the population and native references before a candidate exists;
--build records the shipped pre-W38 web cut. --verify rederives from the actual
matrix-named canonical captures and refuses generation drift, not merely scores.
Neither operation admits a holdout payload or modifies a canonical input.
"""
import argparse
import gzip
import hashlib
import io
import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
CAL = HERE.parents[1]
ROOT = CAL.parent.parent
G0B = HERE.parent / '2026-09-25-w37-g0b-edge-identification'
sys.path.insert(0, str(G0B))
import canonical as repaired
from w35_readers import CanonicalNativeReader, WebReader

WEB_ROOT = Path('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
DOC_PATTERN = re.compile(r'(?:materialProfile|recededProfile)=(\S+) sha256:([0-9a-f]{12})')
MIN_PIXELS = 4
SIDES = ('top', 'bottom', 'left', 'right')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def save_once(name, obj):
    data = encoded(obj)
    if name.endswith('.gz'):
        data = gzip.compress(data, mtime=0)
    with (HERE / name).open('xb') as out:
        out.write(data)


def read(name):
    data = (HERE / name).read_bytes()
    return json.loads(gzip.decompress(data) if name.endswith('.gz') else data)


def population(native, matrix):
    roles = native.roles
    cells = {}
    for row in matrix['cells']:
        key = row['key']; profile = key['profileKey']; sid = key['sceneId']; web = key['web']
        if (not profile.startswith('apple-macos-27.0-') or '-standard-glass0.5' not in profile
                or roles.roles.get(sid) not in ('calibration', 'validation', 'probe')
                or roles.scenes[sid]['state'] != 'rest'
                or web['renderer'] != 'webgpu' or web['samplingBackend'] != 'gpu-texture'):
            continue
        cell = profile + '/' + sid
        roles.admit(cell)
        component = roles.spec['components'][roles.scenes[sid]['component']]
        if component['kind'] not in ('capsule', 'rrect', 'group'):
            continue
        if component['kind'] == 'group':
            if len(component['items']) != 3 or any(i['kind'] != 'capsule' or i['size'] != [44, 44]
                                                   for i in component['items']):
                raise ValueError('grouped scene geometry changed; declare an estimator first')
        if cell in cells:
            raise ValueError('ambiguous matrix generation for ' + cell)
        cells[cell] = row
    return dict(sorted(cells.items()))


def documents(capture_path):
    pairs = DOC_PATTERN.findall(capture_path)
    if len(pairs) != 2 or len({name for name, _ in pairs}) != 2:
        raise ValueError('expected an active and a receded document')
    return {name: sha for name, sha in pairs}


def reference(native, cell, row):
    profile, sid = native.roles.admit(cell)
    try:
        raw = native.read(cell)
    except FileNotFoundError:
        raw = None
    path = row['key']['web']['capturePath']
    docs = documents(path)
    for name, sha in docs.items():
        if digest((ROOT / name).read_bytes())[:12] != sha:
            raise ValueError('document generation mismatch: ' + cell)
    return dict(cell=cell, role=native.roles.roles[sid],
                estimator=('grouped-arcs' if native.roles.spec['components'][
                    native.roles.scenes[sid]['component']]['kind'] == 'group' else 'single-straights'),
                nativeSha256=digest(raw) if raw is not None else None, capturePath=path, documents=docs)


def group_geometry(shape, component, scale):
    """Centred HStack placement, circular SDF, W35 whole-pixel/16-normal-bin rule.

    Every pixel belongs only to its nearest declared member centre; no pooled
    three-member deep, and no bin can absorb a neighbouring member's pixels.
    """
    h, w = shape
    items = component['items']; gap = component['spacing']
    width = sum(i['size'][0] for i in items) + (len(items)-1)*gap
    left = (w / scale - width) / 2
    y, x = np.indices(shape)
    bins = []; deeps = []; centres = []
    for item in items:
        iw, ih = item['size']; cx = (left + iw/2)*scale; cy = h/2
        centres.append((cx,cy))
        left += iw + gap
    for member, ((cx,cy), item) in enumerate(zip(centres,items)):
        radius = min(item['size'])*scale/2
        dx=x+.5-cx; dy=y+.5-cy
        d=np.hypot(dx,dy)-radius
        owned=np.ones(shape,bool)
        for other,(ox,oy) in enumerate(centres):
            if other != member:
                owned &= dx*dx+dy*dy <= (x+.5-ox)**2+(y+.5-oy)**2
        whole=owned.copy()
        for ox,oy in ((0,0),(0,1),(1,0),(1,1)):
            whole &= np.hypot(x+ox-cx,y+oy-cy) <= radius
        angle=np.floor(np.mod(np.arctan2(dy,dx),2*np.pi)/(2*np.pi/16)+.5).astype(int)%16
        deeps.append(owned & (d <= -6*scale))
        for shell in range(-6*scale,0):
            ring=whole & (d>=shell) & (d<shell+1)
            for sector in range(16):
                mask=ring & (angle==sector)
                bins.append((dict(member=member, shell=shell, angleBin=sector,
                                  pixels=int(mask.sum())),mask))
    return deeps,bins



def single_geometry(shape, component, scale):
    """Reuse repaired E1 exactly at centre; honour a declared off-centre shape."""
    offset=component.get('offset',[0,0])
    if offset==[0,0]:
        return repaired.geometry(shape,component,scale)
    h,w=shape;cw,ch=component['size'];radius=component.get('radius',min(cw,ch)/2)
    cx=w/2+offset[0]*scale;cy=h/2+offset[1]*scale
    y,x=np.indices(shape);px=x+.5;py=y+.5
    def sdf(x,y):
        qx=abs(x-cx)-(cw/2-radius)*scale;qy=abs(y-cy)-(ch/2-radius)*scale
        return np.hypot(np.maximum(qx,0),np.maximum(qy,0))+np.minimum(np.maximum(qx,qy),0)-radius*scale
    d=sdf(px,py);whole=np.ones(shape,bool)
    for dx,dy in ((0,0),(0,1),(1,0),(1,1)):
        whole&=sdf(x+dx,y+dy)<=0
    xs=(px>=cx+(1.6*radius-cw/2)*scale)&(px<=cx+(cw/2-1.6*radius)*scale)
    ys=(py>=cy+(1.6*radius-ch/2)*scale)&(py<=cy+(ch/2-1.6*radius)*scale)
    sides={'top':xs&(py<cy),'bottom':xs&(py>=cy),
           'left':ys&(px<cx),'right':ys&(px>=cx)}
    bins=[]
    for side,region in sides.items():
        for sh in range(-6*scale,0):
            mask=region&whole&(d>=sh)&(d<sh+1)
            bins.append((dict(side=side,shell=sh,pixels=int(mask.sum())),mask))
    return d,bins

def empty_bins(estimator, scale):
    if estimator == 'single-straights':
        return [dict(side=side,shell=s,pixels=0) for side in SIDES for s in range(-6*scale,0)]
    return [dict(member=m,shell=s,angleBin=b,pixels=0) for m in range(3)
            for s in range(-6*scale,0) for b in range(16)]


def status(estimator, bins, scale, deeps):
    if not all(deeps):
        return 'UNMEASURED'
    if estimator == 'single-straights':
        # Preserve G0b's capsule rule: missing sides invalidate the ROW, even
        # when the top/bottom numeric bins are still useful diagnostics.
        return ('measured' if len(bins) == 24*scale and all(b['status']=='measured' for b in bins)
                else 'UNMEASURED')
    # Grouped arcs have no straight intervals. Each member needs at least 8
    # independently populated angular sectors and at least four of six
    # CSS-px shells; whole-pixel geometry can leave the outermost shell empty.
    for member in range(3):
        selected = [b for b in bins if b.get('member') == member and b['status']=='measured']
        if (len({b['angleBin'] for b in selected}) < 8 or
                len({b['shell'] for b in selected}) < 4*scale):
            return 'UNMEASURED'
    return 'measured'


def missing_row(ref,scale,reason):
    bins=[dict(**b,status='UNMEASURED',reason=reason,nativeExcess=None,
               webExcess=None,residualRGB=None) for b in empty_bins(ref['estimator'],scale)]
    return dict(cell=ref['cell'],role=ref['role'],estimator=ref['estimator'],
                capturePath=ref['capturePath'],documents=ref['documents'],
                nativeSha256=ref['nativeSha256'],webSha256=None,
                nativeDeep=None,webDeep=None,deepPixels=None,bins=bins,
                status='UNMEASURED',measuredBins=0,unmeasuredBins=len(bins),maximum=None)


def compute(native, web, cell, row, ref):
    profile,sid = native.roles.admit(cell)
    # Matrix and both document hashes are checked BEFORE either PNG opens.
    path=row['key']['web']['capturePath']
    if path != ref['capturePath'] or documents(path) != ref['documents']:
        raise ValueError('pre-W38 matrix generation changed: ' + cell)
    for name, sha in ref['documents'].items():
        if digest((ROOT/name).read_bytes())[:12]!=sha:
            raise ValueError('pre-W38 document generation changed: '+cell)
    try:
        repaired.old.generation(web,cell,row)
    except FileNotFoundError:
        return missing_row(ref,2 if '-2x-' in cell else 1,'capture metadata absent')
    scale=2 if '-2x-' in profile else 1
    shape=tuple(reversed(row['key']['web']['pixelSize']))
    component=native.roles.spec['components'][native.roles.scenes[sid]['component']]
    try:
        raw=native.read(cell); wr=web.read(cell)
    except FileNotFoundError:
        return missing_row(ref,scale,'capture or fixture absent')
    if ref['nativeSha256'] is not None and digest(raw) != ref['nativeSha256']:
        raise ValueError('native PNG hash mismatch: '+cell)
    n=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),float)
    w=np.asarray(Image.open(io.BytesIO(wr)).convert('RGB'),float)
    if n.shape != w.shape or n.shape[:2] != shape:
        raise ValueError('matrix pixel size/capture mismatch: '+cell)
    if ref['estimator']=='single-straights':
        d,parts=single_geometry(shape,component,scale)
        deep_masks=[d<=-6*scale]
    else:
        deep_masks,parts=group_geometry(shape,component,scale)
    deeps=[int(mask.sum()) for mask in deep_masks]
    native_deep=[np.median(n[m],axis=0) if m.any() else None for m in deep_masks]
    web_deep=[np.median(w[m],axis=0) if m.any() else None for m in deep_masks]
    bins=[]
    for info,mask in parts:
        member=info.get('member',0)
        count=info['pixels']
        measured=count>=MIN_PIXELS and deeps[member]>=MIN_PIXELS
        bin=dict(**{k:v for k,v in info.items() if k not in ('admissible','status','reason')},
                 status='measured' if measured else 'UNMEASURED')
        if ref['estimator']=='single-straights':
            bin['admissible']=measured
        if not measured:
            bin.update(reason=('population below four' if count else 'absent side/shell or angle bin')
                       if deeps[member]>=MIN_PIXELS else 'deep population below four',
                       nativeExcess=None,webExcess=None,residualRGB=None)
        else:
            nd=native_deep[member]; wd=web_deep[member]
            err=abs((w[mask]-wd)-(n[mask]-nd)).mean(axis=0)
            bin.update(nativeExcess=(n[mask]-nd).mean(axis=0).tolist(),
                       webExcess=(w[mask]-wd).mean(axis=0).tolist(),residualRGB=err.tolist())
        bins.append(bin)
    measured_bins=[b for b in bins if b['status']=='measured']
    result=dict(cell=cell,role=ref['role'],estimator=ref['estimator'],capturePath=path,
                documents=ref['documents'],nativeSha256=digest(raw),webSha256=digest(wr),
                nativeDeep=[v.tolist() if v is not None else None for v in native_deep],
                webDeep=[v.tolist() if v is not None else None for v in web_deep],deepPixels=deeps,
                bins=bins,status=status(ref['estimator'],bins,scale,[v>=MIN_PIXELS for v in deeps]),
                measuredBins=len(measured_bins),unmeasuredBins=len(bins)-len(measured_bins),
                maximum=max((max(b['residualRGB']) for b in measured_bins),default=None))
    if ref['estimator']=='single-straights':
        result['sides']={side:('measured' if all(b['status']=='measured' for b in bins
                    if b['side']==side) else 'UNMEASURED') for side in SIDES}
    return result


def summary(rows):
    return dict(cells=len(rows),singleRows=sum(r['estimator']=='single-straights' for r in rows),
                groupedRows=sum(r['estimator']=='grouped-arcs' for r in rows),
                measuredRows=sum(r['status']=='measured' for r in rows),
                unmeasuredRows=sum(r['status']=='UNMEASURED' for r in rows),
                measuredBins=sum(r['measuredBins'] for r in rows),
                unmeasuredBins=sum(r['unmeasuredBins'] for r in rows),
                maximum=max((r['maximum'] for r in rows if r['maximum'] is not None),default=None),
                unmeasured=[dict(cell=r['cell'],measuredBins=r['measuredBins'],
                    unmeasuredBins=r['unmeasuredBins']) for r in rows if r['status']=='UNMEASURED'])


def declare(native,matrix):
    cells=population(native,matrix)
    refs=[reference(native,cell,row) for cell,row in cells.items()]
    source=G0B/'e1-baseline-repaired.json'
    roles=native.roles
    excluded=[]
    for row in matrix['cells']:
        key=row['key'];sid=key['sceneId'];profile=key['profileKey']
        if (profile.startswith('apple-macos-27.0-') and '-standard-glass0.5' in profile
                and key['web']['renderer']=='webgpu' and sid in roles.scenes
                and roles.scenes[sid]['state']=='rest' and profile+'/'+sid not in cells):
            excluded.append(dict(cell=profile+'/'+sid,role=roles.roles[sid],
                                 reason='holdout: no G0 pixels opened; G1b only'))
    excluded.sort(key=lambda r:r['cell'])
    stacked=[r for r in excluded if roles.scenes[r['cell'].split('/')[1]]['component']=='glass-over-glass']
    decl=dict(schema=1,claims='W38 clause 1c; G0, before candidate score',
              population='all nonholdout active standard macOS27 WebGPU gpu-texture single-component'
                         ' and three-member grouped canonical calibration/validation/probe rows',
              cells=refs,minimumPixels=MIN_PIXELS,minimumDeepPixels=MIN_PIXELS,
              singleCoverage='all four sides and all six CSS-px shells; absent capsule sides make row UNMEASURED',
              groupedCoverage='each member: at least 8 angular sectors and 4 CSS px of measured shells'
                              ' (4*scale device-px shells); absent bins stay UNMEASURED',
              groupedOwnership='nearest declared member centre; HStack total width centered, spacing 12 CSS px',
              outOfEstimator=excluded,
              estimator='whole-pixel RGB channel mean absolute excess difference against own d<=-6 CSS-px median',
              shellsCss=[-6,0],angleBins=16,boundRegressionCodes=1,
              uniformUntintedSideBoundCodes=2,
              preW38=dict(e1RepairedSha256=digest(source.read_bytes()),
                matrixSha256=digest((CAL/'results/matrix.json').read_bytes()),
                documents={name:digest((ROOT/name).read_bytes()) for name in
                           sorted({name for r in refs for name in r['documents']})}),
              stackedHoldout=dict(estimator='visible upper layer boundary under single-component'
                                    ' straight-side cut (over rrect, 120x56, radius 16, offset [0,-8]);'
                                    ' per-layer deep within overlay; no stack pixel read before G1b',
                                  backend='gpu-texture+css-backdrop',scenes=2,profileCells=len(stacked),
                                  cells=[r['cell'] for r in stacked],status='DECLARED_ONLY'),
              missing='absent captures, deep, side/shell or angular bins are UNMEASURED, never pass')
    return decl


def self_test(native,matrix,web):
    decl=read('e2-declaration.json');refs=decl['cells'];mapped=population(native,matrix)
    cell=refs[0]['cell'];row=json.loads(json.dumps(mapped[cell]))
    row['key']['web']['capturePath']+=' altered'
    try:
        compute(native,web,cell,row,refs[0])
    except (AssertionError,ValueError):
        # An assertion from the pre-image metadata guard also rejects drift.
        pass
    else:
        raise AssertionError('generation mismatch not rejected')
    grouped=next(r for r in refs if r['estimator']=='grouped-arcs')
    scale=2 if '-2x-' in grouped['cell'] else 1
    synthetic=[dict(member=m,shell=sh,angleBin=b,status='measured')
               for m in range(3) for sh in range(-6*scale,0) for b in range(8)]
    assert status('grouped-arcs',synthetic,scale,[True]*3)=='measured'
    assert status('grouped-arcs',[b for b in synthetic if b['member']!=1],scale,[True]*3)=='UNMEASURED'
    profile=cell.split('/')[0]
    holdout=next(sid for sid in native.roles.roles if native.roles.roles[sid]=='holdout'
                 and profile+'/'+sid in native.roles.cells)
    try:
        native.roles.admit(profile+'/'+holdout)
    except PermissionError:
        pass
    else:
        raise AssertionError('holdout was admitted')
    base={'kind':'rrect','size':[120,44],'radius':12}
    original,_=single_geometry((200,320),base,1)
    shifted,_=single_geometry((200,320),dict(**base,offset=[0,32]),1)
    assert original[100,160]<0 and shifted[100,160]>0 and shifted[132,160]<0
    # A missing metadata file is not a different generation; a changed metadata
    # file is. The guarded reader is still called before either PNG is opened.
    from tempfile import TemporaryDirectory
    with TemporaryDirectory() as empty:
        absent=compute(native,WebReader.canonical(empty),cell,mapped[cell],refs[0])
        assert absent['status']=='UNMEASURED' and absent['measuredBins']==0
        assert all(b['status']=='UNMEASURED' for b in absent['bins'])
    return dict(rejectsGenerationMismatch=True,rejectsMissingGroupMember=True,
                rejectsHoldout=True,shiftedGeometry=True,missingCaptureUnmeasured=True)


def main():
    parser=argparse.ArgumentParser()
    modes=parser.add_mutually_exclusive_group(required=True)
    for mode in ('declare','build','verify','self-test'):
        modes.add_argument('--'+mode,action='store_true')
    args=parser.parse_args()
    mode=next(m for m in ('declare','build','verify','self-test') if getattr(args,m.replace('-','_')))
    native=CanonicalNativeReader()
    matrix=json.loads((CAL/'results/matrix.json').read_text())
    if mode=='declare':
        decl=declare(native,matrix);save_once('e2-declaration.json',decl)
        print(json.dumps(dict(cells=len(decl['cells']),holdoutPixelsOpened=0)))
        return
    decl=read('e2-declaration.json')
    actual=declare(native,matrix)
    # Absence is UNMEASURED, not permission to substitute a different PNG.
    # Retain the pinned native SHA while a formerly present fixture is absent.
    for ref, pinned in zip(actual['cells'],decl['cells']):
        if ref['cell']==pinned['cell'] and ref['nativeSha256'] is None:
            ref['nativeSha256']=pinned['nativeSha256']
    if decl != actual:
        raise ValueError('pre-W38 declaration, native reference, documents or matrix population changed')
    web=WebReader.canonical(WEB_ROOT)
    if mode=='self-test':
        print(json.dumps(self_test(native,matrix,web)));return
    mapped=population(native,matrix)
    rows=[compute(native,web,ref['cell'],mapped[ref['cell']],ref) for ref in decl['cells']]
    stats=summary(rows)
    if mode=='build':
        save_once('e2-baseline.json.gz',rows)
        save_once('e2-summary.json',stats)
        print(json.dumps(stats));return
    baseline=read('e2-baseline.json.gz')
    absent=[row['cell'] for row in rows if row['webSha256'] is None]
    if any(row!=old for row,old in zip(rows,baseline) if row['cell'] not in absent):
        raise ValueError('E2 baseline differs from pinned matrix-named pixels')
    if not absent and stats!=read('e2-summary.json'):
        raise ValueError('E2 summary differs from the pinned generation')
    print(json.dumps(dict(sameBaseline=not bool(absent),absentCells=absent,**stats)))


if __name__=='__main__':main()
