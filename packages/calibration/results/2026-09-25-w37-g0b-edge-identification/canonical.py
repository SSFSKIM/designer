"""E1 omission repair beside G0; the frozen cut and numbers do not change."""
import hashlib,io,json
import numpy as np
from PIL import Image
from common import HERE,G0,oldcanonical as old,edge

def geometry(shape,component,scale):
    d,existing=old.geometry(shape,component,scale)
    lookup={(info['side'],info['shell']):(info,mask) for info,mask in existing};bins=[]
    for side in ['top','bottom','left','right']:
        for shell in range(-6*scale,0):
            info,mask=lookup.get((side,shell),(dict(side=side,shell=shell,pixels=0,admissible=False),np.zeros(shape,bool)))
            info=dict(info,status='measured' if info['admissible'] else 'UNMEASURED')
            if not info['admissible']:info['reason']='absent side/shell' if info['pixels']==0 else 'population below four'
            bins.append((info,mask))
    return d,bins

def cell_status(bins):
    return 'measured' if bins and all(b['status']=='measured' for b in bins) else 'UNMEASURED'

def read_row(native,web,cell,row,decl):
    profile,sid=native.roles.admit(cell);scale=2 if '-2x-' in profile else 1
    try:
        raw=native.read(cell);assert hashlib.sha256(raw).hexdigest()==decl['nativeReferences'][cell]
        n=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),float)
        component=native.roles.spec['components'][native.roles.scenes[sid]['component']]
        d,bins=geometry(n.shape[:2],component,scale);deep=np.median(n[d<=-6*scale],0)
        old.generation(web,cell,row)
        w=np.asarray(Image.open(io.BytesIO(web.read(cell))).convert('RGB'),float)
    except FileNotFoundError:
        return dict(cell=cell,status='UNMEASURED',reason='native or matrix-named web capture absent',
            bins=[dict(side=side,shell=shell,pixels=0,admissible=False,status='UNMEASURED',
                       reason='native or matrix-named web capture absent')
                  for side in ['top','bottom','left','right'] for shell in range(-6*scale,0)])
    wd=np.median(w[d<=-6*scale],0);rr=[]
    for info,m in bins:
        if info['pixels']:
            error=abs((w[m]-wd)-(n[m]-deep)).mean(0)
            rr.append(dict(**info,nativeExcess=(n[m]-deep).mean(0).tolist(),
                webExcess=(w[m]-wd).mean(0).tolist(),residualRGB=error.tolist(),
                fails=bool(info['admissible'] and np.any(error>1))))
        else:rr.append(dict(**info,nativeExcess=None,webExcess=None,residualRGB=None,fails=None))
    measured=[r for r in rr if r['status']=='measured']
    return dict(cell=cell,nativeDeep=deep.tolist(),webDeep=wd.tolist(),bins=rr,
        maximum=max((max(r['residualRGB']) for r in measured),default=None),
        status=cell_status(rr),measuredBins=len(measured),unmeasuredBins=len(rr)-len(measured),
        sides={s:cell_status([r for r in rr if r['side']==s]) for s in ['top','bottom','left','right']},
        capturePath=row['key']['web']['capturePath'])

def main():
    decl=json.loads((G0/'e1-declaration.json').read_text());matrix=json.loads((old.CAL/'results/matrix.json').read_text())
    cells=set(decl['cells']);mapped={r['key']['profileKey']+'/'+r['key']['sceneId']:r for r in matrix['cells']
        if r['key']['web']['renderer']=='webgpu' and r['key']['profileKey']+'/'+r['key']['sceneId'] in cells}
    native=old.CanonicalNativeReader();web=old.WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
    rows=[read_row(native,web,cell,mapped[cell],decl) for cell in decl['cells']]
    prior={r['cell']:r for r in json.loads((G0/'e1-baseline.json').read_text())};comparisons=[]
    for row in rows:
        oldrow=prior[row['cell']];existing={(b['side'],b['shell']):b for b in row['bins']}
        for b in oldrow['bins']:
            new=existing[(b['side'],b['shell'])]
            assert all(new[k]==v for k,v in b.items()),(row['cell'],b)
        assert row['maximum']==oldrow['maximum']
        comparisons.append(dict(cell=row['cell'],oldBins=len(oldrow['bins']),newBins=len(row['bins']),
            oldStatus=oldrow['status'],newStatus=row['status'],maximumUnchanged=row['maximum']))
    edge.save(HERE/'e1-baseline-repaired.json',rows);edge.save(HERE/'e1-reproduction.json',comparisons)
    print(json.dumps(dict(rows=len(rows),statuses={s:sum(r['status']==s for r in rows) for s in ['measured','UNMEASURED']},
        bins=sum(len(r['bins']) for r in rows),unmeasuredBins=sum(r['unmeasuredBins'] for r in rows),
        originalNumericBinsExactlyReproduced=True,maximum=max(r['maximum'] for r in rows)),indent=2))

if __name__=='__main__':main()
