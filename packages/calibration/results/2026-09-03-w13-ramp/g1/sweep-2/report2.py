import json, sys, os, re, itertools
sys.path.insert(0,"/Users/new/.claude/jobs/5c70e47f/tmp/w13/sweep-2")
from tab import rows

BASE="/Users/new/Developer/GitHub/designer/packages/calibration/results/2026-09-03-w13-ramp/g0/matrix-x6-baseline.json"
T="/Users/new/.claude/jobs/5c70e47f/tmp/w13/sweep-2"
CHECKER=["checkerboard__rrect-sm__rest","checkerboard__capsule-button__rest",
         "checkerboard__rrect-md__rest","checkerboard__rrect-ml__rest",
         "checkerboard__toolbar-group__rest"]
SCORED=CHECKER+["photo__rrect-md__rest"]
SHORT={"checkerboard__rrect-sm__rest":"sm","checkerboard__capsule-button__rest":"caps",
       "checkerboard__rrect-md__rest":"md","checkerboard__rrect-ml__rest":"ml",
       "checkerboard__toolbar-group__rest":"tb","photo__rrect-md__rest":"pho-md"}

def jsnum(v):
    f=float(v)
    return str(int(f)) if f==int(f) else repr(f).rstrip('0').rstrip('.') if '.' in repr(f) else repr(f)

def objectives(name):
    out={}
    for line in open(f"{T}/{name}.out"):
        m=re.match(r"^(\S+=\S+(?:\s+\S+=\S+)*)\s{2,}([\d.]+)\s",line)
        if m: out[m.group(1).strip()]=float(m.group(2))
    return out

def build(name, profileKey, axes):
    """axes: list of (shortname, [values])"""
    objs=objectives(name)
    base=rows(BASE, profileKey)
    pts=[("main(W12 close)", None, base)]
    combos=list(itertools.product(*[v for _,v in axes]))
    for i,combo in enumerate(combos):
        p=f"{T}/points-{name}/matrix-{i}.json"
        if not os.path.exists(p): continue
        lbl=" ".join(f"{axes[j][0]}={jsnum(combo[j])}" for j in range(len(axes)))
        pts.append((lbl, objs.get(lbl), rows(p, profileKey)))
    return base, pts

def tables(name, profileKey, axes, sort_by=None):
    base, pts = build(name, profileKey, axes)
    f=lambda x: "  —   " if x is None else f"{x:.4f}"
    W=62
    hdr="point".ljust(W)+"obj".rjust(9)
    for s in SCORED: hdr+=SHORT[s].rjust(9)
    scored=[]
    for lbl,o,r in pts[1:]:
        rise=sum(r[s]["ssimBand"]-base[s]["ssimBand"] for s in CHECKER)/len(CHECKER)
        s1=min((r[s]["ssimMean"]-base[s]["ssimMean"]) for s in SCORED)
        s4=all(r[s]["ssimBand"]>base[s]["ssimBand"] for s in CHECKER)
        dsd=max(abs(r[s]["isdW"]-base[s]["isdN"]) for s in CHECKER)
        scored.append((lbl,o,r,rise,s1,s4,dsd))
    order=sorted(scored,key=lambda x:-x[3])
    print(f"\n## {name}  ({profileKey})\n")
    print("### ranked by mean ssimBand rise over the 5 checkerboard cells\n")
    print("point".ljust(W)+"obj".rjust(9)+"bandRise".rjust(10)+"minΔssimMean".rjust(14)+"S1".rjust(6)+"S4".rjust(6)+"maxΔisd".rjust(10))
    for lbl,o,r,rise,s1,s4,dsd in order:
        print(lbl.ljust(W)+(("—" if o is None else f"{o:.5f}")).rjust(9)+f"{rise:+.4f}".rjust(10)+f"{s1:+.4f}".rjust(14)
              +("PASS" if s1>=-0.002 else "FAIL").rjust(6)+("PASS" if s4 else "FAIL").rjust(6)+f"{dsd:.4f}".rjust(10))
    seq = [("main(W12 close)",None,base)] + [(l,o,r) for l,o,r,_,_,_,_ in order]
    for metric in ["isdW","ssimBand","ssimInterior","ssimMean"]:
        print(f"\n### {metric}\n"); print(hdr)
        for lbl,o,r in seq:
            line=lbl.ljust(W)+(("—" if o is None else f"{o:.5f}")).rjust(9)
            for s in SCORED: line+=f(r.get(s,{}).get(metric)).rjust(9)
            print(line)
        if metric=="isdW":
            line="NATIVE".ljust(W)+"".rjust(9)
            for s in SCORED: line+=f(base.get(s,{}).get("isdN")).rjust(9)
            print(line)
