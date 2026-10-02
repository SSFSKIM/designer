#!/usr/bin/env python3.12
"""W44 G0 (f): read the rendered ladders against the hashed protocol (`protocol.json`; clause 3).

    python3.12 -B read.py        writes results.json and results.txt beside it (refuses to overwrite)

For every rung it admits the scratch matrix's rows only if each names that rung's candidate
declaration at its hash, and reads each fixed cell's T1 web value off the row and its capture
off the rung's scratch tree (the capture's metadata must name the row's capturePath). Then the
protocol's checks, each recorded:
  control      c05-control against the canonical strict-mode c05 captures, pixel for pixel
  x48          every rung's 1x captures against c05-control's 1x captures
  mustNotAct   every rung's captures of the cells its ladder must not move, against its base's
  betweenRungs adjacent rungs of a ladder on its acting cells: pixel identity and |delta T1|
  flat         per base: every acting cell's T1 web values across the base and its rungs within
               the cell's bar; a leaf is flat when flat at every base it is read at
  nonFlat      per leaf, in value order at each base, end rungs dropped while within the bar of
               their neighbour on every acting cell; the range is the hull across bases
  struck       flat, or a 1x capture moved (X48); L3 additionally proves or fails C's inert 1x
               setting (every 1x capture of every L3 rung identical to c05-control's)
  transfer     per rung and acting 2x cell: T1 web / native, the readings' web / native, and the
               attenuation T1 web(rung) / T1 web(base), by the cell's pitch
Nothing here decides; part 2 cites what it records (declare.py validates the citations).
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(EVIDENCE / "cuts"))
import bed as B  # noqa: E402
import ladder as Lm  # noqa: E402
import readings as R  # noqa: E402
import t1  # noqa: E402

PROTOCOL = Lm.PROTOCOL
SCRATCH = Lm.SCRATCH
CANONICAL = Path("/Users/new/Developer/GitHub/designer/packages/calibration/web-captures")
CANDIDATE_CLAUSE = re.compile(r"materialProfile=candidate candidateDocument=(\S+) declarationSha256=([0-9a-f]{12})")
PITCH = {"checkerboard-4": 8, "checkerboard-8": 16, "checkerboard": 32, "checkerboard-32": 64,
         "checkerboard-64": 128, "hc-text-7": "text-7", "photo": "photo"}
FINE = PROTOCOL["fixedCells"]["scenes"]


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class Rung:
    def __init__(self, r: dict):
        self.__dict__.update(r)
        cand = HERE / "candidates" / self.label / "candidate.json"
        self.declaration = str(cand.relative_to(Lm.ROOT))
        self.sha12 = sha(cand.read_bytes())[:12]
        matrix = json.loads((SCRATCH / self.label / "matrix.json").read_bytes())
        self.rows = {}
        for row in matrix["cells"]:
            m = CANDIDATE_CLAUSE.search(row["key"]["web"]["capturePath"])
            if m is None or m.group(1) != self.declaration or m.group(2) != self.sha12:
                raise SystemExit(f"{self.label}: a row names {m and m.groups()}, not {self.declaration} {self.sha12}")
            self.rows[(row["key"]["profileKey"], row["key"]["sceneId"])] = row
        want = {(p, s) for p in PROTOCOL["profiles"] for s in FINE}
        if set(self.rows) != want:
            raise SystemExit(f"{self.label}: rows {len(self.rows)}, missing {sorted(want - set(self.rows))[:4]}")
        self._pixels = {}

    def t1(self, profile, sid):
        return B.value(self.rows[(profile, sid)], "material", "interiorStdDevWeb")

    def native(self, profile, sid):
        return B.value(self.rows[(profile, sid)], "material", "interiorStdDevNative")

    def pixels(self, profile, sid):
        key = (profile, sid)
        if key not in self._pixels:
            folder = SCRATCH / self.label / "web-captures" / profile / sid
            meta = json.loads((folder / "cell__webgpu.json").read_text())
            if meta.get("capturePath") != self.rows[key]["key"]["web"]["capturePath"]:
                raise SystemExit(f"{self.label} {profile}/{sid}: capture metadata names another row")
            raw = (folder / f"{sid}__webgpu.png").read_bytes()
            self._pixels[key] = (R.P.decode(raw), sha(raw))
        return self._pixels[key]


def scale_of(profile):
    return 2 if "-2x-" in profile else 1


def matches(pred: dict, profile: str, sid: str) -> bool:
    if pred.get("scale") is not None and scale_of(profile) != pred["scale"]:
        return False
    if "poses" in pred and t1.pose(sid) not in pred["poses"]:
        return False
    if "spans" in pred and t1.span_class(sid) not in pred["spans"]:
        return False
    return True


def main(out_dir: Path | None = None) -> int:
    out_dir = out_dir or HERE
    out_json, out_txt = out_dir / "results.json", out_dir / "results.txt"
    if out_json.exists() or out_txt.exists():
        raise SystemExit("results exist; a recorded reading is never overwritten")
    bars = t1.load_bars()
    by_label = {r["label"]: Rung(r) for r in Lm.unique_rungs()}
    control = by_label[PROTOCOL["bases"]["c05"]["label"]]
    base_of = {name: by_label[b["label"]] for name, b in PROTOCOL["bases"].items()}
    P2, P1 = PROTOCOL["profiles"]

    # control
    ctrl = []
    for profile in PROTOCOL["profiles"]:
        for sid in FINE:
            mine, digest = control.pixels(profile, sid)
            raw = (CANONICAL / profile / sid / f"{sid}__webgpu.png").read_bytes()
            ctrl.append(dict(cell=f"{profile}/{sid}", pixelIdentical=bool((mine == R.P.decode(raw)).all()),
                             pngIdentical=digest == sha(raw)))
    # x48 for every rung
    x48 = {}
    for label, rung in by_label.items():
        moved = [sid for sid in FINE if not (rung.pixels(P1, sid)[0] == control.pixels(P1, sid)[0]).all()]
        x48[label] = moved

    ladders, transfer = {}, []
    all_rungs = Lm.rungs()
    for lad in PROTOCOL["ladders"]:
        acting = [sid for sid in FINE if matches(lad["actsOn"], P2, sid)]
        entry = dict(leaves=lad["leaves"], actingCells=acting, bases={}, mustNotActMoved=[], moved1x=[])
        for base, values in lad["readAt"].items():
            base_rung = base_of[base]
            labels = [r["label"] for r in all_rungs if r["ladder"] == lad["id"] and r["base"] == base]
            members = [base_rung] + [by_label[l] for l in labels]
            # value of each member on the ladder's leaf (or leaves), the base's own value first
            base_value = _base_value(lad, base)
            values_all = [base_value] + list(values)
            spread = {}
            for sid in acting:
                bar = bars[(P2, sid)]["bar"]
                vals = [m.t1(P2, sid) for m in members]
                spread[sid] = dict(values=vals, spread=max(vals) - min(vals), bar=bar,
                                   flat=max(vals) - min(vals) <= bar)
            flat = all(s["flat"] for s in spread.values())
            adjacent = []
            order = sorted(range(len(members)), key=lambda i: _key(values_all[i]))
            for a, b in zip(order, order[1:]):
                ma, mb = members[a], members[b]
                adjacent.append(dict(between=[values_all[a], values_all[b]], cells={
                    sid: dict(pixelIdentical=bool((ma.pixels(P2, sid)[0] == mb.pixels(P2, sid)[0]).all()),
                              deltaT1=abs(ma.t1(P2, sid) - mb.t1(P2, sid)),
                              withinBar=abs(ma.t1(P2, sid) - mb.t1(P2, sid)) <= bars[(P2, sid)]["bar"])
                    for sid in acting}))
            entry["bases"][base] = dict(rungs=[m.label for m in members], values=values_all, flat=flat,
                                        cells=spread, adjacent=adjacent,
                                        nonFlat=_non_flat(values_all, members, acting, bars, P2, lad))
            for m in members[1:]:
                for pred in lad["mustNotAct"]:
                    for profile in PROTOCOL["profiles"]:
                        for sid in FINE:
                            if matches(pred, profile, sid) and not (
                                    m.pixels(profile, sid)[0] == base_rung.pixels(profile, sid)[0]).all():
                                entry["mustNotActMoved"].append(f"{m.label} {profile}/{sid}")
                entry["moved1x"] += [f"{m.label} {sid}" for sid in x48[m.label]]
                for sid in acting:
                    n = m.native(P2, sid)
                    got = R.read(P2, sid, _native_png(P2, sid), m.pixels(P2, sid)[0], _geometry(P2, sid))
                    transfer.append(dict(ladder=lad["id"], base=base, rung=m.label,
                                         value=values_all[members.index(m)], scene=sid,
                                         pitch=PITCH[B.SCENES.by_id[sid]["background"]],
                                         pose=t1.pose(sid), span=t1.span_class(sid),
                                         t1Ratio=m.t1(P2, sid) / n, baseT1Ratio=base_rung.t1(P2, sid) / n,
                                         attenuation=m.t1(P2, sid) / base_rung.t1(P2, sid),
                                         readings=got["ratio"]))
        entry["flat"] = all(b["flat"] for b in entry["bases"].values())
        entry["struck"] = entry["flat"] or bool(entry["moved1x"])
        entry["why"] = ("flat at every base" if entry["flat"] else
                        "moved a 1x capture (X48)" if entry["moved1x"] else "not struck")
        entry["nonFlatRange"] = _hull(lad, entry["bases"])
        if lad["id"] == "L3":
            entry["inert1x"] = not entry["moved1x"]
        ladders[lad["id"]] = entry

    body = dict(
        schema="w44-ladder-results-1",
        what="W44 G0 (f): the rendered ladders read against the hashed protocol (clause 3)",
        protocolSha256=sha((HERE / "protocol.json").read_bytes()),
        declarationSha256=(EVIDENCE / "declaration.sha256").read_text().split()[-2],
        tools={p.name: sha(p.read_bytes()) for p in (Path(__file__), HERE / "ladder.py", HERE / "build-candidate.ts",
                                                      EVIDENCE / "cuts/t1.py", EVIDENCE / "cuts/readings.py")},
        rungs={label: dict(declaration=r.declaration, sha12=r.sha12) for label, r in by_label.items()},
        control=dict(cells=len(ctrl), pixelIdentical=sum(c["pixelIdentical"] for c in ctrl),
                     pngIdentical=sum(c["pngIdentical"] for c in ctrl), table=ctrl),
        x48={k: v for k, v in x48.items()}, ladders=ladders, transfer=transfer)
    out_json.write_text(json.dumps(body, indent=1) + "\n")
    text = report(body)
    out_txt.write_text(text)
    print(text)
    return 0


_NATIVE, _GEOM = {}, {}


def _native_png(profile, sid):
    if (profile, sid) not in _NATIVE:
        _NATIVE[(profile, sid)] = R.P.read(B.ROOT / "apps/reference-apple/fixtures" / profile / f"{sid}.png")
    return _NATIVE[(profile, sid)]


def _geometry(profile, sid):
    if (profile, sid) not in _GEOM:
        _GEOM[(profile, sid)] = R.cell_geometry(profile, sid, _native_png(profile, sid))
    return _GEOM[(profile, sid)]


def _key(v):
    return tuple(v) if isinstance(v, list) else (v,)


def _base_value(lad, base):
    """The ladder's leaf value(s) at its base: the base's override, else c05's document value."""
    over = PROTOCOL["bases"][base]["overrides"].get(lad["slot"], {})
    doc = json.loads((B.ROOT / "packages/calibration/profiles" /
                      f"apple-macos-27.0-1x-light-standard-glass0.25{'-receded' if lad['slot'].startswith('receded') else ''}.json")
                     .read_text())["patch"]
    vals = [over.get(leaf, doc[leaf]) for leaf in lad["leaves"]]
    if lad["id"] == "L3":
        return vals
    return vals[0]


def _sub_ladders(lad, values):
    """(leaf key, [(value, index)]) the ladder varies. L3 is two one-leaf ladders inside it: the
    share at width 3 (the base's share 0 included) and the width at share 0.5."""
    if lad["id"] == "L3":
        share = [(v[0], i) for i, v in enumerate(values) if i == 0 or v[1] == 3]
        width = [(v[1], i) for i, v in enumerate(values) if i > 0 and v[0] == 0.5]
        return [("sizeHeavySecondShare", share), ("sizeHeavySecondSigma2x", width)]
    key = "+".join(lad["leaves"]) if lad.get("tied") else lad["leaves"][0]
    return [(key, [(v, i) for i, v in enumerate(values)])]


def _non_flat(values, members, acting, bars, profile, lad):
    out = {}
    for key, pts in _sub_ladders(lad, values):
        pts = sorted(pts)
        same = lambda a, b: all(abs(members[a].t1(profile, s) - members[b].t1(profile, s))  # noqa: E731
                                <= bars[(profile, s)]["bar"] for s in acting)
        lo, hi = 0, len(pts) - 1
        while lo < hi and same(pts[lo][1], pts[lo + 1][1]):
            lo += 1
        while hi > lo and same(pts[hi][1], pts[hi - 1][1]):
            hi -= 1
        out[key] = [pts[lo][0], pts[hi][0]] if lo < hi else None
    return out


def _hull(lad, bases):
    keys = {k for b in bases.values() for k in b["nonFlat"]}
    out = {}
    for k in keys:
        ranges = [b["nonFlat"][k] for b in bases.values() if b["nonFlat"].get(k)]
        out[k] = [min(r[0] for r in ranges), max(r[1] for r in ranges)] if ranges else None
    return out


def report(b) -> str:
    L = [f"protocol {b['protocolSha256'][:12]}, part 1 {b['declarationSha256'][:12]}",
         f"control: c05-control against the canonical strict c05 captures: {b['control']['pixelIdentical']}/"
         f"{b['control']['cells']} pixel-identical, {b['control']['pngIdentical']} PNG-identical",
         "x48 (1x captures against c05-control's): " + (
             "every rung identical" if not any(b["x48"].values()) else
             "; ".join(f"{k}: {len(v)} moved" for k, v in b["x48"].items() if v))]
    for lid, e in b["ladders"].items():
        L.append(f"\n{lid} {'+'.join(e['leaves'])}: {'STRUCK, ' + e['why'] if e['struck'] else 'not struck'}; "
                 f"non-flat range {e['nonFlatRange']}; mustNotAct moved: {len(e['mustNotActMoved'])}"
                 + (f"; C's 1x inert setting {'PROVEN' if e.get('inert1x') else 'NOT proven'}" if lid == "L3" else ""))
        for base, d in e["bases"].items():
            L.append(f"  at {base}: values {d['values']} -> {'FLAT' if d['flat'] else 'moves'}")
            for sid, c in d["cells"].items():
                L.append(f"    {sid:<40} T1 web " + " ".join(f"{v:.4f}" for v in c["values"])
                         + f"  spread {c['spread']:.4f} bar {c['bar']:.4f}")
        for m in e["mustNotActMoved"][:6]:
            L.append(f"  MUST NOT ACT, moved: {m}")
    L.append("\ntransfer (T1 web/native at the rung; attenuation = T1 web rung / base), 2x acting cells:")
    for t in b["transfer"]:
        L.append(f"  {t['ladder']} {t['base']:<6} {str(t['value']):<11} {t['scene']:<40} pitch {str(t['pitch']):<6} "
                 f"x{t['t1Ratio']:.2f} (base x{t['baseT1Ratio']:.2f}) att {t['attenuation']:.2f}  "
                 f"deep x{t['readings']['deep']:.2f} fine x{t['readings']['fine']:.2f} lattice x{t['readings']['lattice']:.2f}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    sys.exit(main())
