"""W36 deep level cut, recomputed through W35's guarded readers (§5.178, clauses 1–3).

The native silhouette-domain abscissa uses the same circular mask for both colour
formulas. Full-RGB inversion is refused if either image's median has any channel
at 255; uncensored channel residuals remain observations, never a partial-RGB Y.
"""
import io,json,sys
from pathlib import Path
import numpy as np
from PIL import Image
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'2026-09-24-w35-g0-edge-cut'))
import edge
sys.path.insert(0,str(HERE.parent/'2026-09-23-w34-g0-contour-bed'))
from w35_readers import CanonicalNativeReader,WebReader
W=np.array([.2126,.7152,.0722])
LEVELS=[0,32,64,96,128,160,255]
COLOURS=dict(zip(['red','green','blue','yellow','magenta','cyan'],
 [[192,32,32],[32,192,32],[32,32,192],[192,192,32],[192,32,192],[32,192,192]]))
BG={**{f'grey-{v}':[v]*3 for v in LEVELS},**COLOURS}
MATERIALS=json.loads((HERE/'resolved-materials.json').read_text())
def save(name,value):
    with (HERE/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def lin(c):return edge.decode(np.asarray(c,float)/255)
def enc(c):return edge.encode(c)*255

def response(x,m,size=.09228515625):
    xs=np.array(m['backdropToneAnchorX']);f=size*size*(3-2*size)
    ys=np.array(m['backdropToneResponseThin'])*(1-f)+np.array(m['backdropToneResponseThick'])*f
    h=np.maximum(np.diff(xs),1e-4);d=np.diff(ys)/h
    slopes=[d[0]]+[2*a*b/(a+b) if a*b>0 else 0 for a,b in zip(d[:-1],d[1:])]+[d[-1]]
    x=np.clip(x,xs[0],xs[-1]);i=min(np.searchsorted(xs,x,side='left')-1,len(h)-1);i=max(i,0)
    t=(x-xs[i])/h[i]
    return float(ys[i]*(1+2*t)*(1-t)**2+slopes[i]*h[i]*t*(1-t)**2+
        ys[i+1]*t*t*(3-2*t)+slopes[i+1]*h[i]*t*t*(t-1))
def material(scheme,pose):
    return MATERIALS[f'apple-macos-27.0-1x-{scheme}-standard-glass0.5'+('-receded' if pose=='inactive' else '')]
def lab(c):
    a=np.array([[.4122214708,.5363325363,.0514459929],[.2119034982,.6806995451,.1073969566],
                [.0883024619,.2817188376,.6299787005]])
    b=np.array([[.2104542553,.7936177850,-.0040720468],[1.9779984951,-2.4285922050,.4505937099],
                [.0259040371,.7827717662,-.808675766]])
    return b@np.cbrt(a@lin(c))
def retained(c,bd):
    v=lin(c);b=lin(bd);q=v/(v@W)-1;target=b/(b@W)-1
    return float(q@target/(target@target))
def hue_delta(c,bd):
    a,b=lab(c),lab(bd)
    return float((np.degrees(np.arctan2(a[2],a[1])-np.arctan2(b[2],b[1]))+180)%360-180)

def extract():
    allrows=[]
    for row in edge.cells():
        p=row['payload'];scale=p['scale'];d=row['geo'][0];deep=d<=-6*scale
        n,w=row['native'],row['web'];nm,wm=np.median(n[deep],0),np.median(w[deep],0)
        # W28's circular silhouette mask uses nominal pixel centres, not the
        # native-mask extractor or the deep domain used for the level itself.
        component=p['component'];origin=np.array(component['suppliedPaths'][0]['frameOrigin'])*scale
        size=np.array(component['size'])*scale;y,x=np.indices(n.shape[:2])
        sd=edge.I.stadium(x+.5,y+.5,[*origin,*(origin+size)],min(size)/2)[0]
        rgb=p['background'].astype(float)[sd<=0];linear=lin(rgb)
        formulas=dict(encodeLumaMean=float(np.mean(edge.encode(linear@W))),
                      encodedChannelsMean=float(np.mean((rgb/255)@W)),pixels=len(rgb))
        allrows.append(dict(cell=row['cell'],role=row['role'],scale=scale,
            pixels=int(deep.sum()),nativeMedian=nm.tolist(),webMedian=wm.tolist(),
            nativeMinimum=n[deep].min(0).tolist(),nativeMaximum=n[deep].max(0).tolist(),
            webMinusNativeEncoded=(wm-nm).tolist(),webMinusNativeLinear=(lin(wm)-lin(nm)).tolist(),
            censoredChannels=[i for i in range(3) if nm[i]==255 or wm[i]==255],
            abscissa=formulas))
    save('deep-cut.json',allrows)
    solids=[r for r in allrows if r['cell'].split('/')[1].split('__')[0] in BG and '__circular-120__' in r['cell']]
    assert len(solids)==104
    old={r['cell']:r for r in json.loads((edge.HERE/'level-table.json').read_text())}
    for r in solids:
        assert r['nativeMedian']==old[r['cell']]['nativeMedian']
        assert r['webMedian']==old[r['cell']]['webMedian']
    save('solid-cut.json',solids)
    print('Reproduced',len(solids),'solid cells from guarded pixels; all W35 deep medians agree')


def derive():
    rows=json.loads((HERE/'solid-cut.json').read_text());indexed={}
    for r in rows:
        profile,scene=r['cell'].split('/');bg,_,pose=scene.split('__')
        scheme='dark' if '-dark-' in profile else 'light'
        indexed[(scheme,pose,bg,r['scale'])]=r
    chroma=[];checks=[];black=[];middle=[]
    secants={('light','rest'):(.5506,.45,1.2677),('light','inactive'):(.5137,.50,1.2113),
             ('dark','rest'):(.3332,.11,.5515),('dark','inactive'):(.5841,.04,.7016)}
    m1=[]
    for scheme in ['light','dark']:
      for pose in ['rest','inactive']:
        m=material(scheme,pose);size=.09228515625;f=size*size*(3-2*size)
        alpha=m['optics']['regular']['tintAlpha']+m['sizeOcclusionGain']*size*(1-m['optics']['regular']['tintAlpha'])
        neutral=m['optics']['regular']['tint'];fallback=float(enc(alpha*(np.array(neutral)@W)))
        native=indexed[(scheme,pose,'grey-0',1)]['nativeMedian'][1]
        black.append(dict(scheme=scheme,pose=pose,sizeK=size,thickWeight=f,sizedAlpha=alpha,
            neutral=neutral,fallbackCodes=fallback,nativeCodes=native,
            authorityOneCodes=float(enc(response(0,m))),authorityOneMissCodes=float(enc(response(0,m)))-native))
        gx=np.array(LEVELS)/255
        gy=np.array([lin(indexed[(scheme,pose,f'grey-{v}',1)]['nativeMedian'])@W for v in LEVELS])
        middle.append(dict(scheme=scheme,pose=pose,x=m['backdropToneAnchorX'][2],
            nativeInterpolated=float(np.interp(m['backdropToneAnchorX'][2],gx,gy)),
            thinKnot=m['backdropToneResponseThin'][2],
            excess=float(m['backdropToneResponseThin'][2]-np.interp(m['backdropToneAnchorX'][2],gx,gy))))
        R0,probe,Rprobe=secants[(scheme,pose)];k=(Rprobe/R0-1)/probe
        m1.append(dict(scheme=scheme,pose=pose,R0=R0,probe=probe,Rprobe=Rprobe,k=k,
            operatorRetention=.9 if scheme=='light' else 1,
            extrapolatedR=R0*(1+k*(.9 if scheme=='light' else 1)),
            qualification='W31 secant at old tone, not a new-tone measurement'))
        for bg,bd in BG.items():
            r=indexed[(scheme,pose,bg,1)];x=r['abscissa']['encodedChannelsMean' if pose=='inactive' else 'encodeLumaMean']
            if bg!='grey-0':
                # Diagnostic forward reproduction only. Even a clipped RGB is
                # an observed encoded image; none of its inferred Y enters a fit.
                pred=float(enc(response(x,m)));observed=float(enc(lin(r['webMedian'])@W))
                checks.append(dict(cell=r['cell'],x=x,predictedCodes=pred,observedCodes=observed,
                    errorCodes=pred-observed,censoredDiagnosticOnly=bool(r['censoredChannels'])))
            if bg not in COLOURS:continue
            for scale in [1,2]:
                r=indexed[(scheme,pose,bg,scale)];n,w=r['nativeMedian'],r['webMedian'];censored=r['censoredChannels']
                item={**r,'scheme':scheme,'pose':pose,'background':bd,'nativeRetention':None,
                    'webRetention':None,'nativeLuma':None,'webLuma':None,'qBase':None,
                    'operatorRetentionRequired':None,'oldToneM1Extrapolated':None,
                    'nativeHueDeltaDegrees':None,'webHueDeltaDegrees':None,'darkExcess':None}
                if not censored:
                    qn,qw=retained(n,bd),retained(w,bd);rn=m['bodyChromaRetention']
                    # The observed q is inverted only where neither native nor
                    # web is clipped; all three channels enter the same luma.
                    qb=(qw-rn)/(1-rn);needed=(qn-qb)/(1-qb)
                    yn,yw=float(lin(n)@W),float(lin(w)@W)
                    # Two interpolants are reported: encoded-input law and the
                    # memo's linear-Y interpolation. Their difference is not noise.
                    yb=float(lin(bd)@W);yp=float(np.interp(float(edge.encode(yb)),gx,gy))
                    yp_memo=float(np.interp(yb,lin(np.array(LEVELS)),gy))
                    p=enc(lin(bd)/yb*yp);pm=enc(lin(bd)/yb*yp_memo)
                    item.update(nativeRetention=qn,webRetention=qw,nativeLuma=yn,webLuma=yw,qBase=qb,
                        operatorRetentionRequired=needed,oldToneM1Extrapolated=R0*(1+k*needed),
                        nativeHueDeltaDegrees=hue_delta(n,bd),webHueDeltaDegrees=hue_delta(w,bd),
                        darkExcess=dict(nativeLuma=yn,greyCurveLuma=yp,excessLinear=yn-yp,
                          fullRetentionPrediction=p.tolist(),nativeMinusPrediction=(np.array(n)-p).tolist(),
                          memoLinearInterpolationLuma=yp_memo,memoNativeMinusPrediction=(np.array(n)-pm).tolist()) if scheme=='dark' else None)
                chroma.append(item)
    save('chroma-cut.json',chroma)
    save('mechanisms.json',dict(responseChecks=checks,black=black,middle=middle,m1Secants=m1))
    save('censoring.json',dict(rule='Any median channel at 255 on either side excludes that channel from fitting and the entire cell from full-RGB inversion; no deleting channels to recover Y.',
        cells=[dict(cell=r['cell'],channels=r['censoredChannels']) for r in chroma if r['censoredChannels']]))
    print('Response max error',max(abs(r['errorCodes']) for r in checks),'black',black)
    print('M1 secants',m1)


def canonical():
    proof=(HERE/'canonical-generation-check.txt').read_text()
    assert 'VERDICT  the tree and the working matrix name the same generation everywhere they meet.' in proof
    native=CanonicalNativeReader();web=WebReader.canonical('/Users/new/Developer/GitHub/designer/packages/calibration/web-captures')
    profiles=[f'apple-macos-27.0-{s}x-{c}-standard-glass0.5' for s in [1,2] for c in ['light','dark']]
    profiles += [f'apple-macos-26.5-1x-{c}-standard' for c in ['light','dark']]
    out=[]
    for profile in profiles:
      scale=2 if '-2x-' in profile else 1
      for pose in ['rest','inactive']:
       for bg in ['light-solid','dark-solid','mid-dark-solid','mid-chroma-solid']:
        cell=profile+'/'+bg+'__rrect-md__'+pose
        try:native.roles.admit(cell)
        except ValueError:continue
        def deep(raw):
            a=np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'),float);h,w=a.shape[:2]
            return np.median(a[h//2-32*scale:h//2+32*scale,w//2-64*scale:w//2+64*scale].reshape(-1,3),0)
        n=deep(native.read(cell));bd=deep(native.read(cell,'background'))
        try:w=deep(web.read(cell))
        except FileNotFoundError:w=None
        censored=[i for i in range(3) if n[i]==255 or (w is not None and w[i]==255)]
        out.append(dict(cell=cell,role=native.roles.roles[cell.split('/')[1]],domain='centre box inset 16 CSS px',
            nativeMedian=n.tolist(),webMedian=w.tolist() if w is not None else None,background=bd.tolist(),
            webMinusNativeEncoded=(w-n).tolist() if w is not None else None,
            webMinusNativeLinear=(lin(w)-lin(n)).tolist() if w is not None else None,
            censoredChannels=censored,nativeLuma=None if censored else float(lin(n)@W),
            webLuma=None if censored or w is None else float(lin(w)@W)))
    save('canonical-solids.json',out);print('Canonical admitted',len(out),'absent web',sum(r['webMedian'] is None for r in out))

if __name__=='__main__':
    {'extract':extract,'derive':derive,'canonical':canonical}[sys.argv[1]]()
