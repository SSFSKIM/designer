"""The twelve published inactive rows of §5.148 §2, generated from the matrix they cite.

Every other figure-set in §5.148 is written by a script that a reader can re-run against
committed evidence; this table was not, and a hand-transcribed table is exactly where a
ledger whose currency is reproducibility cannot afford to stand. Its first published form
carried a sixth decimal place on the ΔE columns that had been read off a summary printed at
five, so the last digit was invented rather than measured. The matrix was always right. This
script is what makes the table a reading of it.

It selects the cells `state == "inactive"` puts in the canonical matrix, groups them by the
profile document and the tier that drew them, and reduces each group the way the ledger's
prose describes: the mean and the worst of the per-cell mean OKLab ΔE, the mean per-cell mean
SSIM, the mean silhouette IoU over the cells that carry a shape axis at all, and — on the CSS
rows only, because the coherence axis exists only where the WebGPU twin was measured first —
the mean cross-tier body ΔE. It opens no fixture, re-measures nothing and is deterministic, so
re-running it reproduces `published-rows.json` byte for byte.

    python3 published-rows.py
"""
import collections
import json
import pathlib

# Presentation order, not a measurement: the profiles in the order `inactive-rows.sh` ran them
# and the ledger prints them, and WebGPU before CSS on each, which is the order the coherence
# axis needs to exist. A group in the matrix that this order does not name is a refusal below
# rather than a row quietly dropped from the table.
PROFILE_ORDER = (
    "apple-macos-26.5-1x-dark-standard",
    "apple-macos-26.5-2x-dark-standard",
    "apple-macos-26.5-1x-light-standard",
    "apple-macos-26.5-2x-light-standard",
    "apple-macos-26.5-1x-light-increased-contrast",
    "apple-macos-26.5-1x-light-reduced-transparency",
)
TIER_ORDER = ("texture", "dom")
PROFILE_PREFIX = "apple-macos-26.5-"

here = pathlib.Path(__file__).resolve().parent
matrix = json.loads((here / "../matrix.json").resolve().read_text())
inactive = [c for c in matrix["cells"] if c.get("state") == "inactive"]

groups = collections.defaultdict(list)
for cell in inactive:
    groups[(cell["key"]["profileKey"], cell["tier"])].append(cell)

unnamed = sorted(k for k in groups if k[0] not in PROFILE_ORDER or k[1] not in TIER_ORDER)
if unnamed:
    raise SystemExit(f"matrix holds inactive groups this table does not name: {unnamed}")


def mean(values):
    return sum(values) / len(values)


rows = []
for profile in PROFILE_ORDER:
    for tier in TIER_ORDER:
        cells = groups.get((profile, tier))
        if not cells:
            continue
        deltaE = [c["perceptual"]["oklabDeltaEMean"]["value"] for c in cells]
        ssim = [c["perceptual"]["ssimMean"]["value"] for c in cells]
        iou = [c["shape"]["silhouetteIoU"]["value"] for c in cells if "shape" in c]
        coherence = [
            c["coherence"]["crossTierOklabDeltaEMean"]["value"] for c in cells if "coherence" in c
        ]
        # The two worst cells and the widest cross-tier cell are named in the paragraph that
        # follows the table, so they are reduced here too rather than read off by hand.
        worst = sorted(cells, key=lambda c: -c["perceptual"]["oklabDeltaEMean"]["value"])[:2]
        widest = max(
            (c for c in cells if "coherence" in c),
            key=lambda c: c["coherence"]["crossTierOklabDeltaEMean"]["value"],
            default=None,
        )
        rows.append({
            "profile": profile,
            "tier": tier,
            "n": len(cells),
            "oklabDeltaEMeanMean": mean(deltaE),
            "oklabDeltaEMeanWorst": max(deltaE),
            "worstCells": [
                {"sceneId": c["key"]["sceneId"],
                 "oklabDeltaEMean": c["perceptual"]["oklabDeltaEMean"]["value"]} for c in worst
            ],
            "ssimMeanMean": mean(ssim),
            "silhouetteIoUMean": mean(iou) if iou else None,
            "silhouetteIoUCells": len(iou),
            "crossTierOklabDeltaEMeanMean": mean(coherence) if coherence else None,
            "crossTierCells": len(coherence),
            "widestCrossTierCell": None if widest is None else {
                "sceneId": widest["key"]["sceneId"],
                "crossTierOklabDeltaEMean":
                    widest["coherence"]["crossTierOklabDeltaEMean"]["value"],
            },
        })


def figure(value):
    return "—" if value is None else f"{value:.6f}"


table = [
    "| profile | tier | n | mean ΔE | worst ΔE | mean SSIM | mean IoU | cross-tier ΔE |",
    "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
]
for row in rows:
    table.append(
        f"| {row['profile'].removeprefix(PROFILE_PREFIX)} | {row['tier']} | {row['n']} "
        f"| {figure(row['oklabDeltaEMeanMean'])} | {figure(row['oklabDeltaEMeanWorst'])} "
        f"| {figure(row['ssimMeanMean'])} | {figure(row['silhouetteIoUMean'])} "
        f"| {figure(row['crossTierOklabDeltaEMeanMean'])} |"
    )

report = {
    "gate": "W28 G4 — the published inactive rows",
    "claims": "§5.148 §2",
    "source": "packages/calibration/results/matrix.json",
    "schemaVersion": matrix["schemaVersion"],
    "inactiveCells": len(inactive),
    "decimals": 6,
    "rows": rows,
    "table": table,
}
(here / "published-rows.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n")
print("\n".join(table))
