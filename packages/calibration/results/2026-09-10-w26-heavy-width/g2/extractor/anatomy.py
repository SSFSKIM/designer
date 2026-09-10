"""What the extractor does on the W26 floor cell, side by side.

`texture / holdout / checkerboard__glass-over-glass__rest / apple-macos-26.5-2x-dark-standard`,
the GPU tier: native fixture, the canonical 0.14.0 capture, and G2b's candidate
capture from the ruled configuration's scratch run.
"""

from __future__ import annotations

import numpy as np
from scipy import ndimage

import w26extractor as X

PROFILE = "apple-macos-26.5-2x-dark-standard"
SCENE = "checkerboard__glass-over-glass__rest"
CAND_ROOT = "/Users/new/.claude/jobs/5c70e47f/tmp/w26/g2/g2b/web-captures"


def masks(threshold=X.DEFAULT_THRESHOLD, chroma=X.DEFAULT_CHROMA):
    native, web0, bg, region, sdist = X.cell_inputs(PROFILE, SCENE, "webgpu")
    webc = X.load(X.web_path(PROFILE, SCENE, "webgpu", root=CAND_ROOT))
    ex = lambda img: X.extract_luminance_delta(img, bg, region, threshold, chroma)
    return {
        "region": region,
        "sdist": sdist,
        "bg": bg,
        "native_img": native,
        "web0_img": web0,
        "webc_img": webc,
        "native": ex(native),
        "web0": ex(web0),
        "webc": ex(webc),
    }


def report(m, label=""):
    region = m["region"]
    out = []
    for name in ("native", "web0", "webc"):
        mask = m[name]
        excluded = (region != 0) & (mask == 0)
        lab, n = ndimage.label(excluded, structure=np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool))
        sizes = ndimage.sum(excluded, lab, range(1, n + 1)) if n else np.array([])
        out.append({
            "name": name,
            "area": int(mask.sum()),
            "excluded": int(excluded.sum()),
            "components": int(n),
            "holes": X.hole_count(mask, region),
            "largest_excluded_component": int(sizes.max()) if n else 0,
        })
    return out


def main():
    m = masks()
    region = m["region"]
    print(f"region area {int(region.sum())} px; capture {m['native'].shape[1]}x{m['native'].shape[0]}")
    print()
    hdr = f"{'mask':<8}{'area':>9}{'excluded':>10}{'exc.comps':>11}{'holes':>7}{'largest exc':>13}"
    print(hdr)
    for r in report(m):
        print(f"{r['name']:<8}{r['area']:>9}{r['excluded']:>10}{r['components']:>11}"
              f"{r['holes']:>7}{r['largest_excluded_component']:>13}")
    print()
    print(f"IoU native vs 0.14.0   {X.iou(m['native'], m['web0']):.5f}")
    print(f"IoU native vs candidate {X.iou(m['native'], m['webc']):.5f}")
    print()

    # Where the excluded sets sit relative to the declared contour.
    sd = m["sdist"]
    for name in ("native", "web0", "webc"):
        excluded = (region != 0) & (m[name] == 0)
        d = -sd[excluded]
        if d.size == 0:
            print(f"{name}: nothing excluded")
            continue
        print(f"{name}: excluded depth inside the declared contour (device px) "
              f"min {d.min():.1f} p50 {np.median(d):.1f} max {d.max():.1f}; "
              f"{int((d <= 1.5).sum())} of {d.size} within 1.5 px of the contour")
    print()

    # The luminance-delta field itself: what fraction of the region sits near the
    # threshold, and on which side.
    bgl = X.luma(m["bg"])
    for name, key in (("native", "native_img"), ("0.14.0", "web0_img"), ("candidate", "webc_img")):
        delta = np.abs(X.luma(m[key]) - bgl)
        inside = delta[region != 0]
        print(f"{name:<10} |Δluma| vs background inside region: "
              f"min {inside.min():.5f} p1 {np.percentile(inside, 1):.5f} "
              f"p5 {np.percentile(inside, 5):.5f} median {np.median(inside):.5f}; "
              f"under 0.02: {int((inside < 0.02).sum())}")
    print()

    # Is the excluded set the same pixels on both sides?
    exN = (region != 0) & (m["native"] == 0)
    ex0 = (region != 0) & (m["web0"] == 0)
    exC = (region != 0) & (m["webc"] == 0)
    print(f"excluded-set overlap native&0.14.0 {int((exN & ex0).sum())}, "
          f"native&candidate {int((exN & exC).sum())}, "
          f"0.14.0&candidate {int((ex0 & exC).sum())}")
    print(f"symmetric difference native vs candidate {int((exN ^ exC).sum())}")


if __name__ == "__main__":
    main()
