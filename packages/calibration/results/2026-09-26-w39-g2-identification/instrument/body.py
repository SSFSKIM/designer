"""W39's sealed uniform-body families, in normalized encoded output units.

The neutral ordinates are fixed before any chromatic fit. H2 preserves the
shader's separate tone, alpha, retention and gamut operations; it is not a
luma-preserving model of the whole material. No native reader is imported here.
"""
import numpy as np

W=np.array([.2126,.7152,.0722])
KNOTS=np.array([40,56,72,88,104,128,150])/255
LMS=np.array([[.4122214708,.5363325363,.0514459929],
              [.2119034982,.6806995451,.1073969566],
              [.0883024619,.2817188376,.6299787005]])
LAB=np.array([[.2104542553,.7936177850,-.0040720468],
              [1.9779984951,-2.4285922050,.4505937099],
              [.0259040371,.7827717662,-.808675766]])

def decode(x):
    x=np.asarray(x,float)
    return np.where(x<=.04045,x/12.92,((np.maximum(x,0)+.055)/1.055)**2.4)

def encode(x):
    x=np.clip(x,0,1)
    return np.where(x<=.0031308,12.92*x,1.055*x**(1/2.4)-.055)

def smooth(a,b,x):
    t=np.clip((np.asarray(x)-a)/max(b-a,1e-6),0,1)
    return t*t*(3-2*t)

def curve(x,xs,ys):
    """End-segment continuation followed by unit-cube clipping, not np.interp's hold."""
    x=np.asarray(x);xs=np.asarray(xs);ys=np.asarray(ys)
    i=np.clip(np.searchsorted(xs,x,side='right')-1,0,len(xs)-2)
    return np.clip(ys[i]+(x-xs[i])/(xs[i+1]-xs[i])*(ys[i+1]-ys[i]),0,1)

def h1(x,neutral):return curve(x,KNOTS,neutral)

def matrix(q):
    q=np.asarray(q).reshape(3,2)
    return np.column_stack((q,1-q.sum(1)))

def h3(x,neutral,q):return encode(decode(h1(x,neutral))@matrix(q).T)

def lab(x):return np.cbrt(np.asarray(x)@LMS.T)@LAB.T

def unlab(x):return ((np.asarray(x)@np.linalg.inv(LAB).T)**3)@np.linalg.inv(LMS).T

def h3prime(x,neutral,q):
    z=lab(decode(x));out=z.copy()
    nk=lab(decode(np.repeat(KNOTS[:,None],3,axis=1)))[:,0]
    ny=lab(decode(np.repeat(np.asarray(neutral)[:,None],3,axis=1)))[:,0]
    out[:,0]=curve(z[:,0],nk,ny)
    out[:,1:]=z[:,1:]@np.asarray(q).reshape(2,2).T
    return encode(unlab(out))

def retain(colour,backdrop,r):
    colour=np.asarray(colour,float);backdrop=np.asarray(backdrop,float)
    if r<=0:return colour.copy()
    y=colour@W;yb=backdrop@W
    valid=(y>1e-6)&(y<=1)&(yb>1e-6)
    out=colour.copy();c=colour[valid];b=backdrop[valid];yy=y[valid]
    c=c+(b*(yy/yb[valid])[:,None]-c)*np.clip(r,0,1)
    yr=c@W
    c*=np.where(yr>1e-6,yy/np.maximum(yr,1e-300),1)[:,None]
    delta=c-yy[:,None];u=np.ones(len(c))
    for j in range(3):
        d=delta[:,j];limit=np.ones(len(c))
        np.divide(1-yy,d,out=limit,where=d>1e-7)
        np.divide(-yy,d,out=limit,where=d< -1e-7)
        u=np.minimum(u,limit)
    out[valid]=yy[:,None]+np.clip(u,0,1)[:,None]*delta
    return out

def response(x,m,size,thin=None):
    xs=np.asarray(m['backdropToneAnchorX']);thin=np.asarray(m['backdropToneResponseThin'] if thin is None else thin)
    f=size*size*(3-2*size)
    ys=thin*(1-f)+np.asarray(m['backdropToneResponseThick'])*f
    h=np.maximum(np.diff(xs),1e-4);d=np.diff(ys)/h
    slopes=np.array([d[0]]+[2*a*b/(a+b) if a*b>0 else 0 for a,b in zip(d[:-1],d[1:])]+[d[-1]])
    xx=np.clip(x,xs[0],xs[-1]);i=np.clip(np.searchsorted(xs,xx,side='left')-1,0,len(h)-1)
    t=(xx-xs[i])/h[i]
    y=ys[i]*(1+2*t)*(1-t)**2+slopes[i]*h[i]*t*(1-t)**2+ys[i+1]*t*t*(3-2*t)+slopes[i+1]*h[i]*t*t*(t-1)
    black=np.clip(m['backdropToneBlackStrength'],0,1)*(1-smooth(0,.003,x))
    target=m['backdropToneBlackThin']*(1-f)+m['backdropToneBlackThick']*f
    return y+(target-y)*black

def h2(x,m,span=44,q=None,presence=1):
    """Uniform, sampled, untinted, standard-policy body before every boundary term.

    x is actual sampled sRGB. An optional fitted q is retention plus four thin
    ordinates; the thick row and all other leaves stay at the selected endpoint.
    """
    x=np.atleast_2d(x);b=decode(x);mean=b@W
    size=float(smooth(m['sizeSpanMin'],m['sizeSpanMax'],span))
    # Receded silhouette input uses the renderer's encoded channel-luma statistic.
    tone=decode(x@W) if isinstance(m.get('backdropToneAbscissa'),dict) else mean
    strength=m['backdropToneMax']
    k=np.clip(strength,0,1)*(1-smooth(m['backdropToneLow'],max(m['backdropToneHigh'],m['backdropToneLow']+1e-4),tone+m['backdropToneSizeBias']*size))
    optics=m['optics']['regular'];a=optics['tintAlpha']+m['sizeOcclusionGain']*size*(1-optics['tintAlpha'])
    n=np.broadcast_to(np.asarray(optics['tint'],float),b.shape).copy();aa=np.full(len(b),a)
    solve=(strength>0)&(m['backdropToneResponseStrength']>0)&(a>1e-3)&(k<.995)
    xx=encode(tone);anchor=max(m['backdropToneAnchorX'][0],1e-4)
    authority=smooth(anchor*.5,anchor,xx)*np.clip(m['backdropToneResponseStrength'],0,1)
    black=np.clip(m['backdropToneBlackStrength'],0,1)*(1-smooth(0,.003,xx))
    authority+= (np.clip(m['backdropToneResponseStrength'],0,1)-authority)*black
    solve&=authority>0
    if np.any(solve):
        rr=response(xx,m,size,None if q is None else q[1:])
        pre=(rr[solve]-k[solve]*mean[solve])/(1-k[solve])
        nominal=(1-a)*mean[solve]+a*(n[solve]@W)
        shift=(pre-nominal)/a*authority[solve]*strength
        nn=np.clip(n[solve]+shift[:,None],0,1);nl=nn@W
        achieved=(1-a)*mean[solve]+a*nl
        lift=(pre>achieved+1e-4)&(nl>mean[solve]+1e-3)
        target=np.full(len(pre),a)
        target[lift]=np.clip((pre[lift]-mean[solve][lift])/(nl[lift]-mean[solve][lift]),a,1)
        aa[solve]=a+(target-a)*authority[solve]*strength;n[solve]=nn
    ap=aa+k*(1-aa);adapted=n.copy();valid=(k>0)&(ap>0)
    adapted[valid]=(n[valid]*((1-k[valid])*aa[valid])[:,None]+b[valid]*k[valid,None])/ap[valid,None]
    c=b+(adapted-b)*(ap*presence)[:,None]
    return encode(retain(c,b,m['bodyChromaRetention'] if q is None else q[0]))
