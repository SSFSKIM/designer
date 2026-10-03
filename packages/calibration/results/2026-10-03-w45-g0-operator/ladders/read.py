#!/usr/bin/env python3.12
"""W45 G0 (e): read the rendered ladders against the hashed protocol (`protocol.json`; clause 4).

    python3.12 -B read.py        writes results.json and results.txt beside it (refuses to overwrite)

Every render is admitted through W45's loader (`cuts/bed.py`, candidate kind): each row must name
its rung's candidate declaration at its hash, and a referee, holdout or undeclared row refuses. Each
fixed cell's T1 is read off the row (`interiorStdDev{Native,Web}`, its bar and code from the
shared bar file), a T cell's two bands off its capture beside the native fixture (W44 G1's
`readings.read`), and every capture is decoded and compared where a check asks. Then, each recorded:
  control   c05-control against the canonical strict-mode c05 captures, pixel for pixel, and its T1
            against the published c05 rows
  joint     base-joint's 2x T1 against W44's committed joint-point cut (m3-t0.1), cell for cell
  x48       every rung's 1x captures pixel-identical to c05-control's 1x captures; `inert1x` when all
  (i)       the `unchanged` cells within the bar of the rung at 0, and byte-identical, on every rung;
            the `monotone` cells' T1 monotone in the delta; struck when no monotone cell moves by
            more than its bar between 0 and -1
  (ii)      per rung, md and lg against c05 and against the joint point: growth g and direction;
            the bar met when one rung moves md up and lg down, both toward Apple, against both
  (iii)     per floor, the transfer per cell across the span tops; flat when no cell moves by more
            than its bar; the non-flat range
  (iv)      the fine thick cells across the tied thick/far starts; flat; the non-flat range
  (v)       per lever rung against its reference, the transfer per thin cell and pitch, and whether
            the lever SEPARATES checkerboard-4 from the pitch-16, 32 and text thin cells; farDelta at
            thin spans byte-identical
Nothing here decides; part 2 cites what it records (`declare.py check-fit` validates the citations).
"""
from __future__ import annotations

import gzip
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402
sys.path.insert(1, str(B.W44_G1 / "cuts"))
import ladder as Lm  # noqa: E402
import readings as R  # noqa: E402
import t1  # noqa: E402
import numpy as np  # noqa: E402

PROTOCOL = Lm.PROTOCOL
CELLS = PROTOCOL["fixedCells"]["scenes"]
P2, P1 = PROTOCOL["profiles"]
CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
FIXTURES = B.ROOT / "apps" / "reference-apple" / "fixtures"
PITCH = {"checkerboard-4": "c8", "checkerboard-8": "c16", "checkerboard": "c32", "checkerboard-32": "c64",
         "checkerboard-64": "c128", "hc-text": "text", "hc-text-28": "text-28", "hc-text-7": "text-7"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Render:
    """One rendered content: its rows (admitted by W45's loader) and its captures."""

    def __init__(self, label: str):
        self.label = label
        cand = Lm.CANDIDATES / label / "candidate.json"
        self.bed = B.load([str(Lm.SCRATCH / label / "matrix.json")], "candidate", str(cand))
        self.rows = {(r["key"]["profileKey"], r["key"]["sceneId"]): r for r in self.bed.rows}
        want = {(p, s) for p in PROTOCOL["profiles"] for s in CELLS}
        if set(self.rows) != want:
            raise SystemExit(f"{label}: rows {len(self.rows)}; missing {sorted(want - set(self.rows))[:4]}, "
                             f"extra {sorted(set(self.rows) - want)[:4]}")
        self._pixels: dict = {}

    def value(self, profile, sid, metric):
        return B.value(self.rows[(profile, sid)], "material", metric)

    def capture(self, profile, sid):
        key = (profile, sid)
        if key not in self._pixels:
            folder = Lm.SCRATCH / self.label / "web-captures" / profile / sid
            meta = json.loads((folder / "cell__webgpu.json").read_text())
            if meta.get("capturePath") != self.rows[key]["key"]["web"]["capturePath"]:
                raise SystemExit(f"{self.label} {profile}/{sid}: the capture's metadata names another row")
            raw = (folder / f"{sid}__webgpu.png").read_bytes()
            self._pixels[key] = (R.P.decode(raw), sha(raw))
        return self._pixels[key]


def cell_reading(render: Render, profile: str, sid: str, bars: dict) -> dict:
    n = render.value(profile, sid, "interiorStdDevNative")
    k = render.value(profile, sid, "interiorStdDevWeb")
    mean = render.value(profile, sid, "interiorMeanNative")
    entry = bars.get((profile, sid))
    code = entry["code"] if entry else t1.code_step(mean)
    bar = entry["bar"] if entry else 0.5 * code
    out = dict(native=n, web=k, ratio=k / n if n else None, bar=bar, code=code, B=max(code, 2 * bar))
    if t1.stratum(sid) == "T" and profile == P2:
        fixture = R.P.decode((FIXTURES / profile / f"{sid}.png").read_bytes())
        got = R.read(profile, sid, fixture, render.capture(profile, sid)[0])
        out["bands"] = {b: dict(native=got["native"][b], web=got["web"][b]) for b in t1.BANDS}
    return out


def growth(n, ref, k):
    return abs(k - n) - abs(ref - n)


def main(out_dir: Path | None = None) -> int:
    out_dir = out_dir or HERE
    out_json, out_txt = out_dir / "results.json", out_dir / "results.txt"
    if out_json.exists() or out_txt.exists():
        raise SystemExit("results exist; a recorded reading is never overwritten")
    bars = t1.load_bars()
    rungs = Lm.rungs()
    by_label = {r["label"]: r for r in rungs}
    renders_of = Lm.rendered_as()
    renders = {label: Render(label) for label in sorted(set(renders_of.values()))}
    read = {r["label"]: {(p, s): cell_reading(renders[renders_of[r["label"]]], p, s, bars)
                         for p in PROTOCOL["profiles"] for s in CELLS} for r in rungs}
    render_of = lambda label: renders[renders_of[label]]  # noqa: E731
    control = PROTOCOL["bases"]["control"]["label"]
    lines, results = [], dict(schema="w45-ladder-results-1", protocolSha256=sha((HERE / "protocol.json").read_bytes()),
                              renders={label: dict(rungs=[x for x, y in renders_of.items() if y == label],
                                                   matrixSha256=sha((Lm.SCRATCH / label / "matrix.json").read_bytes()))
                                       for label in renders},
                              ladders={})

    # control: c05-control against the canonical strict-mode c05 captures and the published rows.
    published = {(r["key"]["profileKey"], r["key"]["sceneId"]): r
                 for r in B.load_published("6d18c059eb42").rows if r["key"]["web"]["renderer"] == "webgpu"}
    ctrl = []
    for p in PROTOCOL["profiles"]:
        for s in CELLS:
            mine, mine_sha = render_of(control).capture(p, s)
            raw = (CANONICAL / p / s / f"{s}__webgpu.png").read_bytes()
            theirs = R.P.decode(raw)
            k_pub = B.value(published[(p, s)], "material", "interiorStdDevWeb")
            ctrl.append(dict(cell=f"{p} {s}", pixelsEqual=bool(np.array_equal(mine, theirs)),
                             pngSha256=dict(control=mine_sha, canonical=sha(raw)),
                             t1=read[control][(p, s)]["web"], t1Published=k_pub,
                             t1Equal=read[control][(p, s)]["web"] == k_pub))
    results["control"] = dict(cells=ctrl, allPixelsEqual=all(c["pixelsEqual"] for c in ctrl),
                              allT1Equal=all(c["t1Equal"] for c in ctrl))
    lines.append(f"control (c05-control against the canonical c05 captures and published rows): pixels equal "
                 f"{sum(c['pixelsEqual'] for c in ctrl)}/{len(ctrl)}, T1 equal {sum(c['t1Equal'] for c in ctrl)}/{len(ctrl)}")

    # joint: base-joint's 2x T1 against W44's committed m3-t0.1 cut.
    joint_label = PROTOCOL["bases"]["J"]["label"]
    w44 = json.loads(gzip.open(B.W44_G1 / "fit/candidates/m3-t0.1/cuts.json.gz").read())["T1"]["cells"]
    w44_t1 = {c["scene"]: c for c in w44 if c["tier"] == "webgpu" and c["profile"] == P2}
    jt = [dict(cell=s, mine=read[joint_label][(P2, s)]["web"], w44=w44_t1[s]["candidate"],
               equal=read[joint_label][(P2, s)]["web"] == w44_t1[s]["candidate"]) for s in CELLS if s in w44_t1]
    results["joint"] = dict(cells=jt, allEqual=all(x["equal"] for x in jt))
    lines.append(f"joint (base-joint's 2x T1 against W44's m3-t0.1 cut): equal {sum(x['equal'] for x in jt)}/{len(jt)}")

    # x48: every rung's 1x captures against c05-control's.
    x48 = []
    for label in sorted(renders):
        moved = [s for s in CELLS
                 if not np.array_equal(renders[label].capture(P1, s)[0], render_of(control).capture(P1, s)[0])]
        x48.append(dict(render=label, moved=moved))
    inert1x = all(not x["moved"] for x in x48)
    results["ladders"]["x48"] = dict(renders=x48, inert1x=inert1x)
    lines.append(f"X48: every render's 1x captures pixel-identical to c05-control's: {inert1x} "
                 f"({sum(not x['moved'] for x in x48)}/{len(x48)} renders)")

    t1_of = lambda label, s, p=P2: read[label][(p, s)]["web"]  # noqa: E731
    lad = {x["id"]: x for x in PROTOCOL["ladders"]}

    # (i) the operator in isolation.
    li = lad["i"]
    order = [r["label"] for r in rungs if r["ladder"] == "i"]          # values 0, -0.25, ..., -1
    zero = order[0]
    unchanged = {}
    for s in li["reads"]["unchanged"]:
        unchanged[s] = dict(
            withinBar=all(abs(t1_of(lbl, s) - t1_of(zero, s)) <= read[zero][(P2, s)]["bar"] for lbl in order),
            byteIdentical=all(np.array_equal(render_of(lbl).capture(P2, s)[0], render_of(zero).capture(P2, s)[0])
                              for lbl in order),
            t1=[t1_of(lbl, s) for lbl in order])
    monotone = {}
    for s in li["reads"]["monotone"]:
        seq = [t1_of(lbl, s) for lbl in order]
        diffs = [b - a for a, b in zip(seq, seq[1:])]
        monotone[s] = dict(t1=seq, monotone=all(d <= 0 for d in diffs) or all(d >= 0 for d in diffs),
                           moves=abs(seq[-1] - seq[0]) > read[zero][(P2, s)]["bar"],
                           movedInBars=abs(seq[-1] - seq[0]) / read[zero][(P2, s)]["bar"],
                           native=read[zero][(P2, s)]["native"])
    struck_i = [] if any(m["moves"] for m in monotone.values()) else ["sizeHeavySecondShareFar2x"]
    moved_vals = [v for v, lbl in zip(li["values"], order)
                  if any(abs(t1_of(lbl, s) - t1_of(zero, s)) > read[zero][(P2, s)]["bar"] for s in monotone)]
    results["ladders"]["i"] = dict(
        unchanged=unchanged, monotone=monotone, struck=struck_i,
        barMet=all(u["withinBar"] for u in unchanged.values()) and all(m["monotone"] for m in monotone.values()),
        nonFlatRange={"sizeHeavySecondShareFar2x": [min(li["values"]), max(li["values"])] if moved_vals else None})
    lines.append(f"\n(i) the operator in isolation (rungs {', '.join(order)}):")
    for s, u in unchanged.items():
        lines.append(f"  unchanged {s:<36} within bar {u['withinBar']}, byte-identical {u['byteIdentical']}: "
                     + " ".join(f"{x:.4f}" for x in u["t1"]))
    for s, m in monotone.items():
        lines.append(f"  monotone  {s:<36} {m['monotone']}, moves {m['moves']} ({m['movedInBars']:.1f} bars), "
                     f"native {m['native']:.4f}: " + " ".join(f"{x:.4f}" for x in m["t1"]))
    lines.append(f"  bar met: {results['ladders']['i']['barMet']}; struck: {struck_i or 'none'}")

    # (ii) the joint composition, against c05 and the joint point.
    lii = lad["ii"]
    md, lg = lii["reads"]["md"], lii["reads"]["lg"]
    ref = {"c05": {s: B.value(published[(P2, s)], "material", "interiorStdDevWeb") for s in (md, lg)},
           "joint": {s: w44_t1[s]["candidate"] for s in (md, lg)}}
    native = {s: read[control][(P2, s)]["native"] for s in (md, lg)}
    rows_ii, met = [], []
    for r in (x for x in rungs if x["ladder"] == "ii"):
        entry = dict(rung=r["label"], value=r["value"], md=t1_of(r["label"], md), lg=t1_of(r["label"], lg))
        ok = True
        for name, refs in ref.items():
            g_md, g_lg = growth(native[md], refs[md], entry["md"]), growth(native[lg], refs[lg], entry["lg"])
            up, down = entry["md"] > refs[md], entry["lg"] < refs[lg]
            entry[name] = dict(mdGrowth=g_md, lgGrowth=g_lg, mdRises=up, lgFalls=down,
                               meets=g_md < 0 and up and g_lg < 0 and down)
            ok = ok and entry[name]["meets"]
        entry["meetsBoth"] = ok
        if ok:
            met.append(r["label"])
        rows_ii.append(entry)
    results["ladders"]["ii"] = dict(native=native, references=ref, rungs=rows_ii, met=met, barMet=bool(met),
                                    stop=not met)
    lines.append(f"\n(ii) the joint composition: md {md} (native {native[md]:.4f}; c05 {ref['c05'][md]:.4f}, "
                 f"joint {ref['joint'][md]:.4f}), lg {lg} (native {native[lg]:.4f}; c05 {ref['c05'][lg]:.4f}, "
                 f"joint {ref['joint'][lg]:.4f})")
    for e in rows_ii:
        lines.append(f"  {e['rung']:<22} md {e['md']:.4f} lg {e['lg']:.4f}  vs c05 md g {e['c05']['mdGrowth']:+.4f} "
                     f"lg g {e['c05']['lgGrowth']:+.4f}  vs joint md g {e['joint']['mdGrowth']:+.4f} lg g "
                     f"{e['joint']['lgGrowth']:+.4f}  {'MEETS' if e['meetsBoth'] else ''}")
    lines.append(f"  bar met on: {met or 'NO RUNG (the stop)'}")

    # (iii) and (iv): transfer, flatness and the non-flat range.
    def sweep(lid: str, cells: list[str], values: list, groups: dict) -> dict:
        out = {}
        hull = []
        for gname, labels in groups.items():
            table = {s: [t1_of(lbl, s) for lbl in labels] for s in cells}
            moved = {s: max(table[s]) - min(table[s]) > read[labels[0]][(P2, s)]["bar"] for s in cells}
            keep = list(range(len(values)))
            def flat_pair(i, j):
                return all(abs(table[s][i] - table[s][j]) <= read[labels[0]][(P2, s)]["bar"] for s in cells)
            while len(keep) > 1 and flat_pair(keep[0], keep[1]):
                keep.pop(0)
            while len(keep) > 1 and flat_pair(keep[-1], keep[-2]):
                keep.pop()
            rng = [values[keep[0]], values[keep[-1]]] if any(moved.values()) else None
            if rng:
                hull += rng
            out[gname] = dict(rungs=labels, t1=table, moved=moved, flat=not any(moved.values()), nonFlatRange=rng,
                              ratio={s: [x / read[labels[0]][(P2, s)]["native"] for x in table[s]] for s in cells})
        return dict(groups=out, flat=all(g["flat"] for g in out.values()),
                    hull=[min(hull), max(hull)] if hull else None)

    liii = lad["iii"]
    groups = {}
    for floor in liii["at"]["sizeScatterFloor2x"]:
        groups[f"floor {floor:g}"] = [r["label"] for r in rungs if r["ladder"] == "iii" and r["at"]["sizeScatterFloor2x"] == floor]
    s3 = sweep("iii", liii["reads"]["cells"], liii["values"], groups)
    results["ladders"]["iii"] = dict(s3, struck=["sizeScatterSpanMax2x"] if s3["flat"] else [],
                                     nonFlatRange={"sizeScatterSpanMax2x": s3["hull"]})
    liv = lad["iv"]
    s4 = sweep("iv", liv["reads"]["cells"], liv["values"], {"base I, farDelta -0.5": [r["label"] for r in rungs if r["ladder"] == "iv"]})
    key4 = "sizeScatterRampStartThick2x+sizeScatterRampStartFar2x"
    results["ladders"]["iv"] = dict(s4, struck=[key4] if s4["flat"] else [], nonFlatRange={key4: s4["hull"]})
    for lid, s, vals, leaf in (("iii", s3, liii["values"], "span top"), ("iv", s4, liv["values"], "thick/far")):
        lines.append(f"\n({lid}) {leaf} at {vals}: flat {s['flat']}; non-flat hull {s['hull']}")
        for gname, g in s["groups"].items():
            lines.append(f"  {gname}:")
            for c in g["t1"]:
                lines.append(f"    {c:<40} {'moves' if g['moved'][c] else 'flat '} web/native "
                             + " ".join(f"{x:.2f}" for x in g["ratio"][c]))

    # (v) the thin-span transfer per lever.
    lv = lad["v"]
    cb4, others = lv["reads"]["cb4"], lv["reads"]["others"]
    thin = cb4 + others
    rows_v, separating = [], []
    for r in (x for x in rungs if x["ladder"] == "v"):
        reference = r["against"]
        cells = {}
        for s in thin:
            here, there = read[r["label"]][(P2, s)], read[reference][(P2, s)]
            if "bands" in here:
                n, c, k = here["bands"]["fine"]["native"], there["bands"]["fine"]["web"], here["bands"]["fine"]["web"]
            else:
                n, c, k = here["native"], there["web"], here["web"]
            cells[s] = dict(pitch=PITCH[B.SCENES.by_id[s]["background"]], reference=c, web=k, native=n,
                            transfer=k / c - 1 if c else None, growth=growth(n, c, k), toward=growth(n, c, k) < 0,
                            band="T1-fine" if "bands" in here else "T1",
                            byteIdentical=bool(np.array_equal(render_of(r["label"]).capture(P2, s)[0],
                                                              render_of(reference).capture(P2, s)[0])))
        sep = all(cells[s]["toward"] for s in cb4) and all(cells[s]["toward"] for s in others)
        if sep:
            separating.append(r["label"])
        rows_v.append(dict(rung=r["label"], lever=r["lever"], set=r["value"], reference=reference, cells=cells,
                           separates=sep))
    far = next(x for x in rows_v if x["lever"] == "farDelta")
    results["ladders"]["v"] = dict(rungs=rows_v, separating=separating,
                                   farDeltaThinByteIdentical=all(c["byteIdentical"] for c in far["cells"].values()),
                                   reading=("a lever separates checkerboard-4 from the pitch-16, 32 and text thin cells"
                                            if separating else "no lever separates: Decision Log 5's named residual"))
    base_v = PROTOCOL["bases"]["J"]["label"]
    lines.append(f"\n(v) the thin-span transfer per lever (base {base_v}; T1 web/native at the base: "
                 + ", ".join(f"{s.split('__')[0]}/{s.split('__')[1]} {read[base_v][(P2, s)]['ratio']:.2f}" for s in thin) + ")")
    for x in rows_v:
        lines.append(f"  {x['rung']:<36} {x['lever']:<22} vs {x['reference']:<18} "
                     + " ".join(f"{c['pitch']}:{c['transfer']:+.2f}{'*' if c['toward'] else ''}" for c in x["cells"].values())
                     + ("  SEPARATES" if x["separates"] else ""))
    lines.append(f"  (* toward Apple) separating: {separating or 'none'}; farDelta at thin spans byte-identical: "
                 f"{results['ladders']['v']['farDeltaThinByteIdentical']}")

    results["cells"] = {label: {f"{p} {s}": v for (p, s), v in cells.items()} for label, cells in read.items()}
    with out_json.open("x") as f:
        json.dump(results, f, indent=1)
        f.write("\n")
    with out_txt.open("x") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
