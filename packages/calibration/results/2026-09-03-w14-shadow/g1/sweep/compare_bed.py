"""Confirmation matrix against the W12 close bed (X7 baseline)."""
import sys, json
sys.path.insert(0,'/Users/new/.claude/jobs/5c70e47f/tmp/w14/sweep')
from read import *
BED='/Users/new/.claude/jobs/5c70e47f/tmp/w14/x7/matrix-x7-baseline.json'
NEW=sys.argv[1]
def index(p):
    return {(c['key']['profileKey'], c['key']['sceneId'], c['tier']): c for c in cells(p)}
bed=index(BED); new=index(NEW)
prof=sys.argv[2] if len(sys.argv)>2 else None
tier=sys.argv[3] if len(sys.argv)>3 else 'texture'
print(f'{"scene":46s}{"set":12s}{"ssimMean":>19s}{"ssimBand":>19s}{"ssimInt":>19s}{"ssimOut":>19s}')
for k in sorted(new):
    if prof and k[0]!=prof: continue
    if k[2]!=tier: continue
    n=new[k]; b=bed.get(k)
    row=f'{k[1][:46]:46s}{n["fixtureSet"]:12s}'
    for f in ('ssimMean','ssimBand','ssimInterior','ssimOutside'):
        nv=v(n,'perceptual',f); bv=v(b,'perceptual',f) if b else None
        if nv is None: row+=f'{"—":>19s}'
        elif bv is None: row+=f'{nv:>12.4f}{"  (new)":>7s}'
        else: row+=f'{nv:>12.4f} ({nv-bv:+.4f})'
    print(row)
