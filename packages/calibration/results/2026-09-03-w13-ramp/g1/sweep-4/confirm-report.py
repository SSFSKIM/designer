"""The confirmation run's rows, every profile, against the W14 bed."""
import json, sys
T = "/Users/new/.claude/jobs/5c70e47f/tmp/w13/sweep-4"
BASE = "/Users/new/.claude/jobs/5c70e47f/tmp/w13/sweep-4/matrix-w14-bed.json"
CONF = f"{T}/matrix-confirm.json"
FIELDS = ["perceptual.ssimMean", "perceptual.ssimBand", "perceptual.ssimInterior",
          "perceptual.ssimOutside", "material.interiorStdDevWeb",
          "material.interiorStdDevNative", "shape.silhouetteIoU",
          "shape.contourDistanceMean", "shape.contourDistanceP95",
          "perceptual.oklabDeltaEMean", "perceptual.oklabDeltaEP95"]


def cells(path, tier="texture"):
    out = {}
    for c in json.load(open(path))["cells"]:
        if c["tier"] != tier:
            continue
        m = {"fixtureSet": c["fixtureSet"]}
        for ax, rec in c.items():
            if isinstance(rec, dict):
                for f, v in rec.items():
                    if isinstance(v, dict) and "value" in v:
                        m[f"{ax}.{f}"] = v["value"]
        out[(c["key"]["profileKey"], c["key"]["sceneId"])] = m
    return out


def show(profileKey, tier="texture", only=None):
    a, b = cells(BASE, tier), cells(CONF, tier)
    keys = sorted(k for k in b if k[0] == profileKey)
    print(f"\n### {profileKey} ({tier})\n")
    print(f"{'cell':44s}{'set':12s}{'band':>9s}{'Dband':>9s}{'mean':>9s}{'Dmean':>9s}"
          f"{'out':>9s}{'Dout':>9s}{'isdW':>8s}{'isdN':>8s}")
    for k in keys:
        sid = k[1]
        if only and not any(o in sid for o in only):
            continue
        n, o = b[k], a.get(k)
        f = lambda x: "   —   " if x is None else f"{x:.4f}"
        d = lambda fl: "   —   " if (o is None or fl not in o or fl not in n) else f"{n[fl]-o[fl]:+.4f}"
        print(f"{sid:44s}{n['fixtureSet']:12s}"
              f"{f(n.get('perceptual.ssimBand')):>9s}{d('perceptual.ssimBand'):>9s}"
              f"{f(n.get('perceptual.ssimMean')):>9s}{d('perceptual.ssimMean'):>9s}"
              f"{f(n.get('perceptual.ssimOutside')):>9s}{d('perceptual.ssimOutside'):>9s}"
              f"{f(n.get('material.interiorStdDevWeb')):>8s}"
              f"{f(n.get('material.interiorStdDevNative')):>8s}")


if __name__ == "__main__":
    for pk in ["apple-macos-26.5-1x-light-standard", "apple-macos-26.5-2x-light-standard",
               "apple-macos-26.5-1x-dark-standard", "apple-macos-26.5-2x-dark-standard"]:
        for tier in ["texture", "dom"]:
            show(pk, tier)
