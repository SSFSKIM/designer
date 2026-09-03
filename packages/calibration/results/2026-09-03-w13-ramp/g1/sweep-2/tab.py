import json, sys, os

CELLS = ["checkerboard__rrect-sm__rest", "checkerboard__capsule-button__rest",
         "checkerboard__rrect-md__rest", "checkerboard__rrect-ml__rest",
         "checkerboard__toolbar-group__rest", "photo__rrect-md__rest",
         "checkerboard__rrect-lg__rest", "checkerboard__glass-over-glass__rest"]

def load(path):
    return json.load(open(path))["cells"]

def get(cell, axis, field):
    r = cell.get(axis)
    if not r: return None
    v = r.get(field)
    return v["value"] if v else None

def rows(path, profileKey=None, tier="texture", scenes=None):
    out = {}
    for c in load(path):
        k = c["key"]
        if profileKey and k["profileKey"] != profileKey: continue
        if c["tier"] != tier: continue
        sid = k["sceneId"]
        if scenes is not None and sid not in scenes: continue
        out[sid] = dict(
            ssimMean=get(c,"perceptual","ssimMean"),
            ssimBand=get(c,"perceptual","ssimBand"),
            ssimInterior=get(c,"perceptual","ssimInterior"),
            ssimOutside=get(c,"perceptual","ssimOutside"),
            isdW=get(c,"material","interiorStdDevWeb"),
            isdN=get(c,"material","interiorStdDevNative"),
            fixtureSet=c["fixtureSet"],
        )
    return out

if __name__ == "__main__":
    p = sys.argv[1]; pk = sys.argv[2] if len(sys.argv)>2 else None
    r = rows(p, pk)
    for sid in sorted(r):
        v = r[sid]
        f = lambda x: "—" if x is None else f"{x:.4f}"
        print(f"{sid:56s} {f(v['ssimMean'])} {f(v['ssimBand'])} {f(v['ssimInterior'])} {f(v['ssimOutside'])} isd {f(v['isdW'])}/{f(v['isdN'])} [{v['fixtureSet']}]")
