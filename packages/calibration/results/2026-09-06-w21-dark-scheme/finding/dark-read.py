"""W21 finding (claims §5.87): the canonical dark bed read under the DECLARED geometry (scenes.json), body and rim separately, both
scales, native against the GPU tier. The silhouette extractor cannot do this over the dark solids
(the body sits under its 0.02 threshold and the 'interior' it returns is the rim ring), which is
why the canonical rows call dark-solid__rrect-md's interior 0.041 / 0.211: those are rim readings.
Body = declared box eroded 6 CSS px; rim band = the outer 3 CSS px of the declared box, peak per
side (top / bottom / left / right) as the max of the band's row/column means.

    python3 dark-read.py > dark-read.txt
"""
import json, os, sys
import numpy as np
from PIL import Image
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..'))
S=json.load(open(f'{R}/apps/reference-apple/scenes.json'))
comp={c['id'] if isinstance(c,dict) else c: c for c in (S['components'] if isinstance(S['components'],list) else [dict(id=k,**v) for k,v in S['components'].items()])}
def lin(a):
    a=a/255.0; return np.where(a<=0.04045,a/12.92,((a+0.055)/1.055)**2.4)
def luma(p):
    c=lin(np.asarray(Image.open(p).convert('RGB'),dtype=np.float64)); return 0.2126*c[...,0]+0.7152*c[...,1]+0.0722*c[...,2]
def box(cid, scale, shape):
    c=comp[cid]
    # every canonical component is centred on the canvas; size from the registry
    w,h=c.get('width') or c.get('size',[None,None])[0], c.get('height') or c.get('size',[None,None])[1]
    if w is None:
        w,h=c['w'],c['h']
    cx,cy=S['canvas']['width']/2,S['canvas']['height']/2
    return (cx-w/2)*scale,(cy-h/2)*scale,(cx+w/2)*scale,(cy+h/2)*scale
def masks(cid, scale, shape):
    x0,y0,x1,y1=box(cid,scale,shape)
    yy,xx=np.mgrid[0:shape[0],0:shape[1]]; xx=xx+0.5; yy=yy+0.5
    inside=lambda e:(xx>=x0+e*scale)&(xx<x1-e*scale)&(yy>=y0+e*scale)&(yy<y1-e*scale)
    body=inside(6); band=inside(0)&~inside(3)
    sides={'top':band&(yy<y0+3*scale),'bottom':band&(yy>=y1-3*scale),'left':band&(xx<x0+3*scale),'right':band&(xx>=x1-3*scale)}
    return body,sides,(x0,y0,x1,y1)
print(json.dumps({k:v for k,v in comp.items()}, default=str)[:600], file=sys.stderr)
for prof,scale in (('apple-macos-26.5-1x-dark-standard',1),('apple-macos-26.5-2x-dark-standard',2)):
    print(f'== {prof}')
    print(f"{'scene':46s} {'body nat':>9s} {'body web':>9s} {'sd nat':>7s} {'sd web':>7s} | rim peak nat T/B/L/R | rim peak web T/B/L/R")
    for p in S['profiles']:
        if p['key']!=prof: continue
        for sid in p['scenes']:
            sc=next(s for s in S['scenes'] if s['id']==sid)
            if sc['component'] not in comp or sc['state']!='rest' or 'glass-over-glass' in sid: continue
            n=f'{R}/apps/reference-apple/fixtures/{prof}/{sid}.png'; w=f'{R}/packages/calibration/web-captures/{prof}/{sid}/{sid}__webgpu.png'
            if not (os.path.exists(n) and os.path.exists(w)): continue
            ln,lw=luma(n),luma(w)
            body,sides,_=masks(sc['component'],scale,ln.shape)
            def peak(L):
                out=[]
                for k in ('top','bottom','left','right'):
                    m=sides[k]
                    if k in('top','bottom'):
                        rows=[L[r][m[r]].mean() for r in range(L.shape[0]) if m[r].any()]
                    else:
                        rows=[L[:,c][m[:,c]].mean() for c in range(L.shape[1]) if m[:,c].any()]
                    out.append(max(rows))
                return out
            pn,pw=peak(ln),peak(lw)
            print(f"{sid:46s} {ln[body].mean():9.4f} {lw[body].mean():9.4f} {ln[body].std():7.4f} {lw[body].std():7.4f} | "+' '.join(f'{v:.3f}' for v in pn)+' | '+' '.join(f'{v:.3f}' for v in pw))
