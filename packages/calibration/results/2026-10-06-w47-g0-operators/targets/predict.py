#!/usr/bin/env python3.12
"""W47 G0 (g): the per-cell predictions part 1 hashes (charter Decision Log 4; Design "The targets and
their families"). PREDICTIONS, every one: the ladders replace them with renders (clause 5), and nothing
here is fitted or gated. W46's `targets/predict.py` form, re-based on W46's point A.

1. **Operator 1, from point A** (Design "Operator 1"; the Purpose's per-span table). The neutral
   carries no structure, so a cell's interior structure is the transmitted share `1 − α` of the
   scattered backdrop's (W46 G0 (e)'s model). Point A drew a uniform `tintAlpha` (0.7 active, 0.8
   receded) with the inherited occlusion gain 0.05 and no far delta; W46 G1's gate cut of point A
   (`results/2026-10-05-w46-g1-refit/gate/<point A>/cut.json.gz`, read, never re-rendered) carries
   every dark WebGPU gate cell's measured web SD there. At a declared operator-1 point L each cell is
   predicted as `web_A · (1 − α_L(span)) / (1 − α_A(span))`, with
       α(span) = alphaBase + gain · sizeK(span) · (1 − alphaBase),
       alphaBase = clamp(tintAlpha + far · farS(span), 0, 1),
       sizeK = smoothstep(32, 96, span), farS = smoothstep(96, top, span)
   (the MARKED law; the scatter is held at point A's, so the width lever of ladder (ii) is NOT in
   these numbers). The receded cells inherit the active's far delta, top and gain (X67) at their own
   `tintAlpha`. Each point's predicted cells are evaluated by W47's rule (`cuts/rule.py`) exactly as a
   rendered cut would be: per profile the three targets' aggregates against the reference's, the
   gated groups, the budget and the verdict.
2. **Operator 2, the attenuation table** (Design "Operator 2"). A checkerboard of cell c has its
   lowest mode on the diagonal at √2/2c cycles per CSS px, which a Gaussian of σ CSS px passes by
   g = exp(−π²σ²/c²); the body form scales the body sample's mode by a = 1 − share + share·g. On the
   two F inactive gate cells the predicted ratio at point A is ratio_A · a — an UPPER BOUND on the
   effect, because it assumes the body carries all of the web's structure; the diagnostic measured the
   body's actual share at σ 6, share 1, from the reference (R 0.74–1.04 of the excess removed; G0
   (f)), and that reading is listed beside the table. The coarse 64 px and photo cells lose at most the
   64 px mode's loss, also tabled.
3. **S1** (Design "The other rows"): the direction, stated in part 1's inputs, not computed here.

    python3.12 -B predict.py        (writes predictions.json and predictions.txt; refuses to overwrite)
"""
from __future__ import annotations

import copy
import gzip
import hashlib
import json
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
import sys  # noqa: E402
sys.path.insert(0, str(EVIDENCE))
import bindings as W  # noqa: E402

B, T1, RULE = W.load_cuts()
POINT_A = "d-s2-rta0.8-rs214-rfa0.5-rh10.25-re20.04-rk10.15-rk20.04-rn10.4-rn20.4-rg0"
POINT_A_CUT = W.W46_G1 / "gate" / POINT_A / "cut.json.gz"
POINT_A_ALPHA = {"rest": 0.7, "inactive": 0.8}
GAIN_A = 0.05
# The declared operator-1 points: the charter's worked example (Design "Operator 1", "Why this law":
# tintAlpha 0.7 and the gain 0.4 put 0.82 at span 96; the far delta 0.38 at the inherited top 256, or
# 0.13 at the top 128, puts about 0.90 at 160), and point A's own law as the control.
POINTS = {
    "A (uniform 0.7, the control)": dict(tintAlpha=0.7, gain=0.05, far=0.0, top=256),
    "L256 (0.7, gain 0.4, far 0.38, top 256)": dict(tintAlpha=0.7, gain=0.4, far=0.38, top=256),
    "L128 (0.7, gain 0.4, far 0.13, top 128)": dict(tintAlpha=0.7, gain=0.4, far=0.13, top=128),
    "K (0.8, gain 0.05, far 0.1, top 256)": dict(tintAlpha=0.8, gain=0.05, far=0.1, top=256),
}
SIGMAS = (1.5, 2, 3, 4, 6)
SHARES = (0.25, 0.5, 0.75, 1)


def smooth(lo: float, hi: float, x: float) -> float:
    t = min(max((x - lo) / max(hi - lo, 1e-6), 0.0), 1.0)
    return t * t * (3 - 2 * t)


def alpha(span: float, tint: float, gain: float, far: float, top: float) -> float:
    base = min(max(tint + far * smooth(96, top, span), 0.0), 1.0)
    return base + gain * smooth(32, 96, span) * (1 - base)


def predicted_cells(cells: list[dict], point: dict) -> list[dict]:
    out = []
    for c in cells:
        pose = "inactive" if c["pose"] == "inactive" else "rest"
        span = B.SCENES.span(c["scene"])
        a_a = alpha(span, POINT_A_ALPHA[pose], GAIN_A, 0.0, 256)
        tint = point["tintAlpha"] if pose == "rest" else POINT_A_ALPHA["inactive"]
        a_l = alpha(span, tint, point["gain"], point["far"], point["top"])
        f = (1 - a_l) / (1 - a_a)
        p = copy.deepcopy(c)
        p["candidate"] = c["candidate"] * f
        if "bands" in p:
            for band in p["bands"].values():
                band["candidate"] = band["candidate"] * f
        p["predictedFactor"], p["alphaA"], p["alphaL"], p["span"] = f, a_a, a_l, span
        out.append(p)
    return out


def main() -> int:
    out_json, out_txt = HERE / "predictions.json", HERE / "predictions.txt"
    if out_json.exists() or out_txt.exists():
        raise SystemExit("predict: committed evidence is not overwritten")
    raw = POINT_A_CUT.read_bytes()
    cut = json.loads(gzip.decompress(raw))
    held = set(W.referees().load_manifest()["scenes"])
    cells = [c for c in cut["T1"]["cells"] if RULE.in_scope(c) and c["scene"] not in held]
    lines = [f"W47 G0 (g): PREDICTIONS from W46's point A ({POINT_A_CUT.relative_to(W.ROOT)}, "
             f"sha256 {hashlib.sha256(raw).hexdigest()[:12]}); the ladders replace them.", ""]
    body = dict(what="W47 G0 (g): per-cell predictions part 1 hashes; PREDICTIONS, which the ladders replace",
                pointA=dict(label=POINT_A, cut=str(POINT_A_CUT.relative_to(W.ROOT)),
                            sha256=hashlib.sha256(raw).hexdigest(), alpha=POINT_A_ALPHA, gain=GAIN_A),
                model="web_L = web_A * (1 - alpha_L(span)) / (1 - alpha_A(span)); scatter held at point A's",
                operator1={}, operator2={})
    for name, point in POINTS.items():
        pred = predicted_cells(cells, point)
        ev = RULE.evaluate(pred)
        per_cell = [dict(profile=p["profile"], scene=p["scene"], stratum=p["stratum"], pose=p["pose"],
                         span=p["span"], alphaA=p["alphaA"], alphaL=p["alphaL"], factor=p["predictedFactor"],
                         native=p["native"], webA=c["candidate"], webL=p["candidate"],
                         ratioA=c["candidate"] / c["native"] if c["native"] else None,
                         ratioL=p["candidate"] / p["native"] if p["native"] else None)
                    for p, c in zip(pred, cells)]
        summary = {prof: {k: v for k, v in pe.items() if k != "perCell"} for prof, pe in ev["profiles"].items()}
        body["operator1"][name] = dict(point=point, verdict=ev["verdict"], profiles=summary,
                                       pooledTargets=ev["pooledTargets"], cells=per_cell)
        lines.append(f"operator 1 at {name}: {json.dumps(point)}")
        for prof in RULE.SCOPE_PROFILES:
            pe = RULE.evaluate_profile(pred, (), ("gate",), prof)
            tg = "; ".join(f"{t} {v['A']:.3f} vs {v['referenceA']:.3f}" + (" (halved)" if v.get("halved") else "")
                           for t, v in pe["targets"].items())
            gf = ", ".join(pe["gatedAggregateFailures"]) or "none"
            lines.append(f"  {prof}: {pe['verdict']}; away>B {len(pe['awayBeyondB'])}, >3B "
                         f"{len(pe['awayBeyondCeiling'])}; gated groups failing: {gf}; {tg}")
        for scale in (1, 2):
            for cls, lo, hi in (("thin", 0, 50), ("mid", 90, 100), ("thick", 120, 200)):
                rest = [p for p in per_cell if p["pose"] == "rest" and p["profile"] == W.PROFILE[scale]
                        and lo <= p["span"] <= hi and p["ratioL"] is not None]
                if rest:
                    rs = sorted(p["ratioL"] for p in rest)
                    lines.append(f"    {scale}x rest {cls}: alpha {rest[0]['alphaL']:.3f}, ratio median "
                                 f"x{rs[len(rs) // 2]:.2f} (n {len(rs)})")
    # operator 2's attenuation table and its application to F inactive at point A
    table = {str(s): {"8": math.exp(-math.pi ** 2 * s * s / 64), "64": math.exp(-math.pi ** 2 * s * s / 4096)}
             for s in SIGMAS}
    f_inactive = [c for c in cells if c["stratum"] == "F" and c["pose"] == "inactive"]
    applied = []
    for c in f_inactive:
        for s in SIGMAS:
            for q in SHARES:
                a = 1 - q + q * table[str(s)]["8"]
                applied.append(dict(profile=c["profile"], scene=c["scene"], sigma=s, share=q, a=a,
                                    ratioA=c["candidate"] / c["native"],
                                    ratioUpperBound=a * c["candidate"] / c["native"]))
    diag = json.loads((EVIDENCE / "diagnostic/record.json").read_text())
    body["operator2"] = dict(form=diag["chosenForm"], attenuation=table, fInactiveAtPointA=applied,
                             diagnosticMeasured=[dict(cell=x["cell"], scale=x["scale"], R=x["R"]["body"])
                                                 for x in diag["cells"]],
                             note="ratioUpperBound assumes the body carries all of the web's structure; the "
                                  "diagnostic measured R (from the reference, sigma 6, share 1)")
    lines += ["", "operator 2 (body form): g = exp(-pi^2 sigma^2 / c^2), a = 1 - share + share*g"]
    for s in SIGMAS:
        lines.append(f"  sigma {s}: 8 px passed {table[str(s)]['8']:.3f}; 64 px passed {table[str(s)]['64']:.3f}")
    for c in f_inactive:
        rows = [x for x in applied if x["scene"] == c["scene"] and x["profile"] == c["profile"]]
        pick = [x for x in rows if (x["sigma"], x["share"]) in ((2, 1), (3, 0.75), (3, 0.5), (4, 0.5), (6, 1))]
        lines.append(f"  {c['profile'].split('-')[3]} {c['scene']}: point A x{c['candidate'] / c['native']:.2f} -> "
                     + ", ".join(f"s{x['sigma']}/q{x['share']} x{x['ratioUpperBound']:.2f}" for x in pick))
    lines.append("  diagnostic (sigma 6, share 1, from the reference): " + ", ".join(
        f"{x['cell']} {x['scale']}x R {x['R']['body']:.2f}" for x in diag["cells"]))
    with out_json.open("x") as f:
        f.write(json.dumps(body, indent=1) + "\n")
    with out_txt.open("x") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
