"""The rim along the contour: peak excess over the body at each position around the shape, native
against vitrea, so a rim that varies with position (lit) is told from one that does not (drawn)."""
import sys, math, numpy as np
from PIL import Image
R="/Users/new/Developer/GitHub/designer"
def lin(a):
    a=a/255.0; return np.where(a<=0.04045,a/12.92,((a+0.055)/1.055)**2.4)
def luma(p):
    c=lin(np.asarray(Image.open(p).convert("RGB"),dtype=float)); return c[...,0]*0.2126+c[...,1]*0.7152+c[...,2]*0.0722
def boundary(kind, box, r, n=720):
    x0,y0,x1,y1=box; pts=[]
    if kind=="capsule":
        cy=(y0+y1)/2; rr=(y1-y0)/2; cl=x0+rr; cr=x1-rr
        # parametrise by angle around the shape centre-ish: straight top, right arc, straight bottom, left arc
        L=2*(cr-cl)+2*math.pi*rr
        for i in range(n):
            s=i/n*L
            if s<(cr-cl): pts.append((cl+s,y0,0,-1,"top"))
            elif s<(cr-cl)+math.pi*rr:
                t=(s-(cr-cl))/rr; a=-math.pi/2+t; pts.append((cr+rr*math.cos(a),cy+rr*math.sin(a),math.cos(a),math.sin(a),"right-arc"))
            elif s<2*(cr-cl)+math.pi*rr:
                u=s-(cr-cl)-math.pi*rr; pts.append((cr-u,y1,0,1,"bottom"))
            else:
                t=(s-2*(cr-cl)-math.pi*rr)/rr; a=math.pi/2+t; pts.append((cl+rr*math.cos(a),cy+rr*math.sin(a),math.cos(a),math.sin(a),"left-arc"))
    else:
        L=2*(x1-x0-2*r)+2*(y1-y0-2*r)+2*math.pi*r
        segs=[("top",x1-x0-2*r),("tr",math.pi/2*r),("right",y1-y0-2*r),("br",math.pi/2*r),("bottom",x1-x0-2*r),("bl",math.pi/2*r),("left",y1-y0-2*r),("tl",math.pi/2*r)]
        for i in range(n):
            s=i/n*L; acc=0
            for name,ln in segs:
                if s<acc+ln:
                    u=s-acc
                    if name=="top": pts.append((x0+r+u,y0,0,-1,name))
                    elif name=="right": pts.append((x1,y0+r+u,1,0,name))
                    elif name=="bottom": pts.append((x1-r-u,y1,0,1,name))
                    elif name=="left": pts.append((x0,y1-r-u,-1,0,name))
                    else:
                        cx,cy,a0={"tr":(x1-r,y0+r,-math.pi/2),"br":(x1-r,y1-r,0),"bl":(x0+r,y1-r,math.pi/2),"tl":(x0+r,y0+r,math.pi)}[name]
                        a=a0+u/r; pts.append((cx+r*math.cos(a),cy+r*math.sin(a),math.cos(a),math.sin(a),name))
                    break
                acc+=ln
    return pts
def rim_profile(im, pts, body, depth=4):
    out=[]
    for (x,y,nx,ny,seg) in pts:
        best=-1
        for d in np.arange(-1.0,depth,0.5):   # from 1 px outside to depth px inside, along the inward normal
            sx=x-nx*d-0.5*nx; sy=y-ny*d-0.5*ny
            xi=int(round(sx)); yi=int(round(sy))
            if 0<=yi<im.shape[0] and 0<=xi<im.shape[1]: best=max(best, im[yi,xi]-body)
        out.append((seg,best))
    return out
def run(profile, scene, kind, box, r, srcs, bins=16):
    pts=boundary(kind,box,r)
    print(f"\n== {profile} {scene} — peak excess over the body along the contour, {bins} bins around the shape (clockwise from the top-left of the top edge)")
    rows=[]
    for tag,p in srcs:
        im=luma(p); x0,y0,x1,y1=box; body=im[y0+12:y1-12, x0+12:x1-12].mean()
        prof=rim_profile(im,pts,body); vals=np.array([v for _,v in prof]); per=len(vals)//bins
        binned=[vals[i*per:(i+1)*per].mean() for i in range(bins)]
        rows.append((tag,body,binned,vals))
    print(f"{'':8}"+" ".join(f"{i:>7}" for i in range(bins)))
    for tag,body,binned,vals in rows:
        print(f"{tag:8}"+" ".join(f"{v:7.4f}" for v in binned)+f"   body {body:.4f}  min/max {vals.min():.4f}/{vals.max():.4f}  ratio {vals.max()/max(vals.min(),1e-4):.2f}")
    # by segment
    segs={}
    for tag,body,binned,vals in rows:
        pass
    print("-- by segment (mean of peak excess)")
    segnames=[]
    for s,_ in rim_profile(luma(srcs[0][1]),pts,0.0):
        if s not in segnames: segnames.append(s)
    for tag,p in srcs:
        im=luma(p); x0,y0,x1,y1=box; body=im[y0+12:y1-12, x0+12:x1-12].mean(); prof=rim_profile(im,pts,body)
        print(f"{tag:8}"+"  ".join(f"{s}={np.mean([v for ss,v in prof if ss==s]):.4f}" for s in segnames))
W="/Users/new/Developer/GitHub/designer/packages/calibration/web-captures"
def srcs(prof,scene): return [("native",f"{R}/apps/reference-apple/fixtures/{prof}/{scene}.png"),("landed",f"{W}/{prof}/{scene}/{scene}__webgpu.png")]
run("apple-macos-26.5-2x-dark-standard","dark-solid__capsule-button__rest","capsule",(200,156,440,244),44,srcs("apple-macos-26.5-2x-dark-standard","dark-solid__capsule-button__rest"))
run("apple-macos-26.5-2x-dark-standard","dark-solid__rrect-md__rest","rrect",(160,104,480,296),40,srcs("apple-macos-26.5-2x-dark-standard","dark-solid__rrect-md__rest"))
run("apple-macos-26.5-2x-light-standard","dark-solid__rrect-md__rest","rrect",(160,104,480,296),40,srcs("apple-macos-26.5-2x-light-standard","dark-solid__rrect-md__rest"))
run("apple-macos-26.5-2x-dark-standard","mid-dark-solid__capsule-button__rest","capsule",(200,156,440,244),44,srcs("apple-macos-26.5-2x-dark-standard","mid-dark-solid__capsule-button__rest"))
run("apple-macos-26.5-2x-light-standard","light-solid__rrect-md__rest","rrect",(160,104,480,296),40,srcs("apple-macos-26.5-2x-light-standard","light-solid__rrect-md__rest"))
run("apple-macos-26.5-2x-dark-standard","checkerboard__rrect-md__rest","rrect",(160,104,480,296),40,srcs("apple-macos-26.5-2x-dark-standard","checkerboard__rrect-md__rest"))
run("apple-macos-26.5-2x-light-standard","photo__capsule-button__rest","capsule",(200,156,440,244),44,srcs("apple-macos-26.5-2x-light-standard","photo__capsule-button__rest"))
run("apple-macos-26.5-1x-dark-standard","dark-solid__capsule-button__rest","capsule",(100,78,220,122),22,srcs("apple-macos-26.5-1x-dark-standard","dark-solid__capsule-button__rest"))
