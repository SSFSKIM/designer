FLOOR, SMIN, SSPAN, TMAX = 0.4, 32, 256, 96
def ss(x,a,b):
    t=min(1.0,max(0.0,(x-a)/(b-a))); return t*t*(3-2*t)
def kDeep(s): return FLOOR+(1-FLOOR)*ss(s,SMIN,SSPAN)
def sizeThickness(s): return ss(s,SMIN,TMAX)

CELLS=[("rrect-sm",64,32),("capsule-button",120,44),("toolbar-group",44,44),
       ("rrect-md",160,96),("rrect-ml",224,128),("glass-over-glass",220,130),("rrect-lg",280,160)]

print("### 1. the span the law reads, and the deep sharp share on it\n")
print("| cell | box W x H | span = min(W,H) | first sweep's 'span' | kDeep(span) | sDeep = 1 - kDeep |")
print("| --- | --- | --- | --- | --- | --- |")
for n,w,s in CELLS:
    print(f"| `{n}` | {w} x {s if n!='toolbar-group' else 44} | {s} | {w} | {kDeep(s):.4f} | **{1-kDeep(s):.4f}** |")

G0={ # cell: (1x start, 2x start)  -- §1 read-off table; sm/tb from §1 finding 4's first window
 "rrect-sm":(0.637,0.483), "capsule-button":(0.642,0.437), "toolbar-group":(0.642,0.437),
 "rrect-md":(0.512,0.192), "rrect-ml":(0.501,0.179), "rrect-lg":(0.410,0.141)}
print("\n### 2. the excursion the reference implies, per cell and scale\n")
print("| cell | span | sDeep | G0 s0 1x | s0-sDeep 1x | G0 s0 2x | s0-sDeep 2x |")
print("| --- | --- | --- | --- | --- | --- | --- |")
for n,w,s in CELLS:
    if n not in G0: continue
    d=1-kDeep(s); a,b=G0[n]
    print(f"| `{n}` | {s} | {d:.4f} | {a:.3f} | **{a-d:+.4f}** | {b:.3f} | **{b-d:+.4f}** |")

print("\n### 3. the third form at the G0-pinned constants\n")
for dpr,(thin,thick,reach) in [(1,(0.64,0.47,120)),(2,(0.46,0.17,100))]:
    print(f"\n**dpr {dpr}** — s0(span) = {thin} + ({thick} - {thin}) * sizeThickness(span), reach {reach} device px\n")
    print("| cell | span | sizeThickness | s0(span) | sDeep | excursion max(0, s0-sDeep) | moves? |")
    print("| --- | --- | --- | --- | --- | --- | --- |")
    for n,w,s in CELLS:
        T=sizeThickness(s); s0=thin+(thick-thin)*T; d=1-kDeep(s); e=s0-d
        print(f"| `{n}` | {s} | {T:.4f} | {s0:.4f} | {d:.4f} | {max(e,0):.4f} ({e:+.4f}) | {'YES' if e>0 else 'no'} |")

print("\n### 4. what the 2x deep value would have to be\n")
print("| cell | span | required kDeep 2x = 1 - G0 s0 | code kDeep | shortfall |")
print("| --- | --- | --- | --- | --- |")
for n,w,s in CELLS:
    if n not in G0: continue
    req=1-G0[n][1]; print(f"| `{n}` | {s} | {req:.4f} | {kDeep(s):.4f} | **{req-kDeep(s):+.4f}** |")
print("\n1x, the same:\n")
print("| cell | span | required kDeep 1x | code kDeep | shortfall |")
print("| --- | --- | --- | --- | --- |")
for n,w,s in CELLS:
    if n not in G0: continue
    req=1-G0[n][0]; print(f"| `{n}` | {s} | {req:.4f} | {kDeep(s):.4f} | **{req-kDeep(s):+.4f}** |")
