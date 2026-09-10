"""Where each side's excluded pixels sit, and what they sit over.

Two questions the sheet answers by eye and this answers as numbers: are the
excluded pixels over the checkerboard's BLACK cells (where |own - base| is the
surface's own absolute luminance), and are they under the stack's inner overlay
pane or out on the single-glazed base?
"""

from __future__ import annotations

import numpy as np

import w26extractor as X
from anatomy import CAND_ROOT, PROFILE, SCENE


def main():
    native, web0, bg, region, _ = X.cell_inputs(PROFILE, SCENE, "webgpu")
    webc = X.load(X.web_path(PROFILE, SCENE, "webgpu", root=CAND_ROOT))

    # The inner (overlay) pane alone, from the same declaration the region uses.
    component = X.SCENES["components"][X.scene(SCENE)["component"]]
    over_only, _ = X.component_region({"kind": "rrect", **component["over"]},
                                      X.SCENES["canvas"], 2, region.shape[1], region.shape[0])

    bgl = X.luma(bg)
    dark_cell = bgl < 0.5

    print(f"the background raster's cells: {int((bgl == 0).sum())} px at linear 0, "
          f"{int((bgl == 1).sum())} px at linear 1, "
          f"{int(((bgl > 0) & (bgl < 1)).sum())} px between (the cells' antialiased seams)")
    print(f"the declared region: {int(region.sum())} px, of which "
          f"{int((over_only & region).sum())} px are under the inner overlay pane")
    print()
    print(f"{'mask':<12}{'excluded':>10}{'over a dark cell':>18}{'under the inner pane':>22}")
    for label, img in (("native", native), ("0.14.0", web0), ("candidate", webc)):
        mask = X.extract_luminance_delta(img, bg, region)
        excluded = (region != 0) & (mask == 0)
        n = int(excluded.sum())
        print(f"{label:<12}{n:>10}{int((excluded & dark_cell).sum()):>10} "
              f"({int((excluded & dark_cell).sum()) / n:>6.1%}){int((excluded & (over_only != 0)).sum()):>14} "
              f"({int((excluded & (over_only != 0)).sum()) / n:>6.1%})")
    print()
    print("and what the three columns transmit over a dark cell, deep inside each zone")
    print("(median linear luma; the rule keeps a pixel only at >= 0.02):")
    inner = (over_only != 0)
    outer = (region != 0) & ~inner
    for label, img in (("native", native), ("0.14.0", web0), ("candidate", webc)):
        own = X.luma(img)
        a = own[inner & dark_cell]
        b = own[outer & dark_cell]
        print(f"  {label:<10} under the inner pane {np.median(a):.5f}   "
              f"on the base alone {np.median(b):.5f}")


if __name__ == "__main__":
    main()
