"""Standalone BODY-only encoded-sRGB CSS projections; no runtime material changes."""
import math
import numpy as np

E3_W=np.array([.2126,.7152,.0722])
CSS_W=np.array([.213,.715,.072])


def affine_route(g,k):
    """clip(g*x+k): contrast(c), then brightness(b). No fitted parameters.

    k>=0 implies 0<=c<=1, so contrast introduces no premature clipping for
    x in [0,1]. The final brightness clamp is exactly the E3 output clamp.
    """
    if not all(math.isfinite(v) for v in (g,k)) or g<0 or k<0 or g+2*k<=0:
        raise ValueError('requires finite g>=0, k>=0, b=g+2k>0')
    b=g+2*k
    return dict(brightness=b,contrast=g/b)


def affine_output(x,route):
    c=route['contrast'];b=route['brightness']
    return np.clip(b*np.clip(c*np.asarray(x)+(1-c)/2,0,1),0,1)


def plate_route(l,f,g):
    """Original minimum-alpha NEUTRAL plate mirror, not a fitted alternative.

    Use white for F>L and black for F<L; equality needs no plate. CSS saturate's
    weights differ from E3's; parameters use E3 L and plate_output exposes that
    residual as well as intermediate clipping.
    """
    if not all(math.isfinite(v) for v in (l,f,g)) or not 0<=l<=1 or not 0<=f<=1 or g<0:
        raise ValueError('neutral plate requires L,F in [0,1], g>=0')
    if f>l:a=(f-l)/(1-l);n=1.;side='white'
    elif f<l:a=(l-f)/l;n=0.;side='black'
    else:a=0.;n=0.;side='none'
    if a>=1:raise ValueError('full plate has no finite saturation factorization')
    return dict(alpha=a,saturation=g/(1-a),plate=n,side=side)


def plate_output(x,route):
    x=np.asarray(x);l=x @ CSS_W
    saturated=np.clip(l[...,None]+route['saturation']*(x-l[...,None]),0,1)
    return (1-route['alpha'])*saturated+route['alpha']*route['plate']


def e3_terms(rgb,params):
    x=np.asarray(rgb,dtype=float)
    if x.shape!=(3,) or not np.all(np.isfinite(x)) or np.any((x<0)|(x>255)):
        raise ValueError('requires three finite encoded RGB codes')
    l=float(x @ E3_W)
    knots=np.array([40.,56.,72.,88.,104.,128.,150.])
    neutral=np.asarray(params['neutral'],float)
    gains=np.asarray(params['coefficients'],float)
    if (neutral.shape!=(7,) or gains.shape!=(3,) or not np.all(np.isfinite(neutral))
        or not np.all(np.isfinite(gains)) or np.any((neutral<0)|(neutral>255))
        or np.any((gains<0)|(gains>3))):
        raise ValueError('invalid frozen tuple')
    i=int(np.clip(np.searchsorted(knots,l,side='right')-1,0,len(knots)-2))
    f=float(np.clip(neutral[i]+(l-knots[i])/(knots[i+1]-knots[i])*(neutral[i+1]-neutral[i]),0,255))
    return l/255,f/255,float(np.interp(l,[63.,93.,118.],gains))
