"""W18 G0 — the findings' tables, printed from the committed part files.

One script rather than three, because every table here is the same reading under a different cut:
the CSS tier's interior mean minus the GPU tier's, over one mask, on one arrangement. `--table`
selects which cut.

Usage: `python tables.py <partsDir> separation|annulus|spacing|stack`.
"""

import json
import sys
from pathlib import Path

BANDS = ["0.00-0.40", "0.40-0.70", "0.70-0.88", "0.88-1.00"]


def rows(parts: Path, name: str, dpr: int):
    return [r for r in json.loads((parts / f"{name}-{dpr}x.json").read_text()) if "skipped" not in r]


def separation(parts: Path) -> None:
    for dpr in (1, 2):
        print(f"=== dpr {dpr}: interior mean, CSS tier and GPU tier, and the difference ===")
        print(f"{'scene':40s} {'mask':22s} {'GPU':>8s} {'CSS':>8s} {'CSS-GPU':>9s} {'px':>7s}")
        for row in rows(parts, "separation", dpr):
            for key, label in (("native", "native silhouette"), ("declared", "declared region")):
                cell = row["whole"].get(key)
                if cell is None:
                    continue
                print(f"{row['scene']:40s} {label:22s} {cell['gpu']:8.4f} {cell['css']:8.4f} "
                      f"{cell['delta']:+9.4f} {cell['pixels']:7d}")
        print()


def annulus(parts: Path) -> None:
    for dpr in (1, 2):
        print(f"=== dpr {dpr}: CSS minus GPU per annulus, per surface (declared shape) ===")
        print(f"{'scene':40s} {'surface':10s} " + " ".join(f"{b:>10s}" for b in BANDS))
        for row in rows(parts, "separation", dpr):
            if "capsule" not in row["scene"] and "toolbar" not in row["scene"]:
                continue
            for surface in row["surfaces"]:
                a = surface["annulusDeclared"]
                cells = []
                for gpu, css in zip(a["gpu"], a["css"]):
                    cells.append("        --" if gpu is None or css is None else f"{css - gpu:+10.4f}")
                print(f"{row['scene']:40s} {surface['role']:10s} " + " ".join(cells))
        print()


def spacing(parts: Path) -> None:
    for dpr in (1, 2):
        print(f"=== dpr {dpr}: the three-up at eight gaps (declared region) ===")
        print(f"{'background':13s} {'gap':>4s} {'GPU':>8s} {'CSS':>8s} {'CSS-GPU':>9s}")
        for row in rows(parts, "spacing", dpr):
            background, component, _ = row["scene"].split("__")
            cell = row["whole"]["declared"]
            print(f"{background:13s} {component.split('s')[-1]:>4s} {cell['gpu']:8.4f} "
                  f"{cell['css']:8.4f} {cell['delta']:+9.4f}")
        print()


def stack(parts: Path) -> None:
    for dpr in (1, 2):
        print(f"=== dpr {dpr}: the stack, its base alone and its overlay alone (declared region) ===")
        print(f"{'scene':40s} {'part':24s} {'GPU':>8s} {'CSS':>8s} {'CSS-GPU':>9s} {'px':>7s}")
        for row in rows(parts, "separation", dpr):
            if "glass-over-glass" not in row["scene"] and "stack-" not in row["scene"]:
                continue
            cell = row["whole"]["declared"]
            print(f"{row['scene']:40s} {'whole component':24s} {cell['gpu']:8.4f} {cell['css']:8.4f} "
                  f"{cell['delta']:+9.4f} {cell['pixels']:7d}")
            for surface in row["surfaces"]:
                d = surface["declared"]
                print(f"{'':40s} {surface['role']:24s} {d['gpu']:8.4f} {d['css']:8.4f} "
                      f"{d['delta']:+9.4f} {d['pixels']:7d}")
        print()


if __name__ == "__main__":
    {"separation": separation, "annulus": annulus, "spacing": spacing, "stack": stack}[sys.argv[2]](
        Path(sys.argv[1])
    )
