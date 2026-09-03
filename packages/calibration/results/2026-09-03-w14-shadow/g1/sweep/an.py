import sys, json, glob, os
sys.path.insert(0,'/Users/new/.claude/jobs/5c70e47f/tmp/w14/sweep')
from read import *
rnd=sys.argv[1]; rings=sys.argv[2].split(',') if len(sys.argv)>2 else ['3-6','6-12']
D=f'/Users/new/.claude/jobs/5c70e47f/tmp/w14/sweep/points/{rnd}'
rows=[]
for m in sorted(glob.glob(f'{D}/matrix-*.json'), key=lambda p:int(p.split('-')[-1].split('.')[0])):
    i=int(m.split('-')[-1].split('.')[0])
    osh=json.load(open(f'{D}/profile-{i}.json'))['patch']['outerShadow']
    for c in cells(m):
        sid=c['key']['sceneId']; tier=c['tier']
        for ring in rings:
            an,cn=pair(c,'affineNative',ring=ring); aw,cw=pair(c,'affineWeb',ring=ring)
            rows.append(dict(i=i,osh=osh,scene=sid,tier=tier,ring=ring,
                             occN=occl(c,'affineNative',ring=ring),occW=occl(c,'affineWeb',ring=ring),
                             aN=an,aW=aw,cN=cn,cW=cw,
                             ssimMean=v(c,'perceptual','ssimMean'),ssimOut=v(c,'perceptual','ssimOutside'),
                             ssimBand=v(c,'perceptual','ssimBand'),ssimInt=v(c,'perceptual','ssimInterior'),
                             mdN=v(c,'shadow','meanDepartureNative'),mdW=v(c,'shadow','meanDepartureWeb')))
json.dump(rows, open(f'/Users/new/.claude/jobs/5c70e47f/tmp/w14/sweep/rows-{rnd}.json','w'))
keys=[k for k in sys.argv[3].split(',')] if len(sys.argv)>3 else []
print(f'{"pt":3s} {"consts":34s} {"scene":30s} {"ring":6s} {"1-a nat":>8s} {"1-a web":>8s} {"c nat":>9s} {"c web":>9s} {"occN":>7s} {"occW":>7s} {"ssimOut":>8s}')
for r in rows:
    lab=' '.join(f'{k}={r["osh"][k]}' for k in keys) if keys else str(r['i'])
    print(f'{r["i"]:<3d} {lab:34s} {r["scene"][:30]:30s} {r["ring"]:6s} '
          f'{fmt(None if r["aN"] is None else 1-r["aN"],4):>8s} {fmt(None if r["aW"] is None else 1-r["aW"],4):>8s} '
          f'{fmt(r["cN"]):>9s} {fmt(r["cW"]):>9s} {fmt(r["occN"],4):>7s} {fmt(r["occW"],4):>7s} {fmt(r["ssimOut"],4):>8s}')
