"""W21 G0 — the endpoint table: what the response law can reach in the dark scheme.

Claims §5.33's diagnostic, re-run under the dark profile and under the declared geometry. Two
renders bracket the law's authority per cell — `web0` at `backdropToneResponseStrength` 0 (the
shipped dark document, the law standing down) and `web1` at strength 1 on the LIGHT reference's
anchors — and the strength the reference would require is

    s = (reference − web0) / (web1 − web0)

Read it as a diagnostic of the TARGET, not of the curve. A cell needing s inside [0, 1] is one the
law can reach by turning its authority up; a cell needing s outside [0, 1] is one whose reference
sits outside the span between the two renders altogether, which says the endpoint itself is wrong —
in W21's case, that the light anchors are the wrong rows for the dark scheme, which is the whole
premise of the wave. The charter's Design (i) asks specifically which SIDE the reference falls off:
in the light scheme the remainder ran upward against the white neutral's clamp, and the dark
neutral is 0.05 with targets from 0.007 to 0.106, so the mirror case is the black clamp below.

    endpoints.py --native <read.json> --web0 <read.json> --web1 <read.json> --out <file>
"""

import argparse
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--native", required=True)
    ap.add_argument("--web0", required=True)
    ap.add_argument("--web1", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    def rows_of(path, key):
        return {r["scene"]: r for r in json.load(open(path))["rows"] if key in r}

    native = {r["scene"]: r for r in json.load(open(args.native))["rows"]}
    w0 = rows_of(args.web0, "bodyWeb")
    w1 = rows_of(args.web1, "bodyWeb")

    out = [
        "W21 G0 table 2b — the endpoint diagnostic in the dark scheme (claims 5.33's shape)",
        "",
        "web0 = the shipped dark document (backdropToneResponseStrength 0).",
        "web1 = the same document at strength 1, on the LIGHT reference's anchors.",
        "s = (reference - web0) / (web1 - web0), the strength the reference would require of the",
        "law as it stands. |web1 - web0| below 0.002 leaves s undefined and is printed as '-':",
        "the two endpoints coincide there and the law has no authority at that input at all.",
        "",
        f"{'encIn':>7s} {'scene':46s} {'web0':>9s} {'web1':>9s} {'reference':>10s} {'s':>9s}",
    ]
    inside = outside = undefined = 0
    for sid, r in sorted(native.items(), key=lambda kv: kv[1]["backdropEncodedMean"]):
        a, b = w0.get(sid), w1.get(sid)
        if a is None or b is None:
            continue
        span = b["bodyWeb"] - a["bodyWeb"]
        if abs(span) < 0.002:
            s = None
            undefined += 1
        else:
            s = (r["bodyNative"] - a["bodyWeb"]) / span
            if 0.0 <= s <= 1.0:
                inside += 1
            else:
                outside += 1
        out.append(
            f"{r['backdropEncodedMean']:7.4f} {sid:46s} {a['bodyWeb']:9.4f} {b['bodyWeb']:9.4f} "
            f"{r['bodyNative']:10.4f} " + (f"{s:9.3f}" if s is not None else f"{'-':>9s}")
        )
    out += [
        "",
        f"cells inside [0, 1]: {inside}; outside: {outside}; span degenerate: {undefined}",
    ]
    with open(args.out, "w") as fh:
        fh.write("\n".join(out) + "\n")
    print(f"-> {args.out}")


if __name__ == "__main__":
    main()
