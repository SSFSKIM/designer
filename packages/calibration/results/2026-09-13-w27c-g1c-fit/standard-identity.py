#!/usr/bin/env python3
"""W27c G1c: the four standard profiles' captures are byte-identical to the G2 read.

T2 moves fields in the recede's LIGHT entry that only act when the resolved
policy raises occlusion, and macOS reaches that only through Reduce Transparency.
So the claim is not "the standard profiles should be about the same" — it is that
every standard-profile capture is the SAME BYTES as the one §5.139 published, and
a claim of that shape is checkable rather than arguable.

It is the honest test of a policy-scoped change. A field that reached a standard
cell would show here as one differing digest, and no metric on the accessibility
rows would ever have said so.

Run it against the frozen re-read, and again over any rung of T1's ladder if that
term moves at all — T1's ordinate is in the DARK entry and reaches every dark
thin cell over a mid-to-bright backdrop, so its rows are expected to differ and
this script names which.

    python3 standard-identity.py /tmp/w27c-g1c-frozen/checking.json
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
G2 = os.path.join(HERE, "../2026-09-13-w27c-g2-read/checking-matrix.json")
STANDARD = (
    "apple-macos-26.5-1x-light-standard",
    "apple-macos-26.5-2x-light-standard",
    "apple-macos-26.5-1x-dark-standard",
    "apple-macos-26.5-2x-dark-standard",
)


def main():
    read = json.load(open(sys.argv[1] if len(sys.argv) > 1
                          else "/tmp/w27c-g1c-frozen/checking.json"))
    before = {(r["profile"], r["scene"]): r for r in json.load(open(G2))["rows"]}

    compared, identical, moved, unpaired = 0, [], [], []
    for row in read["rows"]:
        if row["profile"] not in STANDARD:
            continue
        key = (row["profile"], row["scene"])
        held = before.get(key)
        if held is None:
            unpaired.append(f"{key[0]}/{key[1]}")
            continue
        compared += 1
        cell = {
            "cell": f"{key[0]}/{key[1]}",
            "scheme": row["scheme"],
            "captureSha256": row["captureSha256"],
            "g2CaptureSha256": held["captureSha256"],
            "bodyDeltaE": row["body"]["deltaE"],
            "g2BodyDeltaE": held["body"]["deltaE"],
            "bodyYWeb": row["body"]["webY"],
            "g2BodyYWeb": held["body"]["webY"],
        }
        (identical if row["captureSha256"] == held["captureSha256"] else moved).append(cell)

    out = {
        "gate": "W27c G1c / claims §5.141",
        "question": "did anything this child moved reach a standard-profile cell?",
        "comparedAgainst": "packages/calibration/results/2026-09-13-w27c-g2-read/checking-matrix.json",
        "cellsCompared": compared,
        "byteIdentical": len(identical),
        "moved": moved,
        "unpaired": unpaired,
        "movedByScheme": sorted({c["scheme"] for c in moved}),
    }
    with open(os.path.join(HERE, "standard-identity.json"), "w") as handle:
        json.dump(out, handle, indent=1)
        handle.write("\n")

    print(f"{compared} standard-profile cells compared against the G2 read")
    print(f"  byte-identical: {len(identical)}")
    print(f"  moved:          {len(moved)}")
    for c in sorted(moved, key=lambda c: -abs(c["bodyDeltaE"] - c["g2BodyDeltaE"])):
        print(f"    {c['cell']:74} body ΔE {c['g2BodyDeltaE']:.5f} → {c['bodyDeltaE']:.5f}")
    if unpaired:
        print(f"  unpaired ({len(unpaired)}): " + ", ".join(unpaired))


sys.exit(main())
