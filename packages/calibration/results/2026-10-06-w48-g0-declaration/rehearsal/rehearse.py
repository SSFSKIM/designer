#!/usr/bin/env python3.12
"""W48 G0 (b): the landing rule rehearsed on this bed under W48's bindings (charter clause 4; X52).
Nothing renders. W47's `rehearsal/rehearse.py` and `port-proof.py` are inherited BY PATH and run unchanged
but for where they write: each names its outputs beside ITSELF (`HERE`), which is W47's committed
directory, so their module attribute `HERE` is pointed here (and `port-proof.py`'s two cut paths named).

1. **The d0219 cut, under W48's bindings.** W47's `cuts/cuts.py` (inherited) cuts the published
   `d0219cd684bf` (with `ebc3d9105a4a`) against itself over the canonical capture tree, read-only, run as
   `__main__` in a process that imported `inherit` first, so its `bindings` is W48's
   (`d0219-cuts.json.gz`, `d0219-cuts.txt`). W47's `rehearse.cut()` finds it and does not re-cut.
2. **The rule** (`rehearse.main()`, W47's): `d0219cd684bf` against itself, every gate cell `unchanged`
   and NEITHER; W46's point A by its committed gate cut, NEITHER with 16 / 8 (1x) and 17 / 10 (2x) away
   beyond B / past 3B; the gated and reported groups the charter's (`rehearsal.json`, `.txt`, W47's shape).
   W47's record reads the synthetic cases from W47's committed transcript; W48 adds beside it W45's 19
   synthetic cases run under W48's bindings (`tools/inherited/cuts__test_rule.txt`), as `syntheticW48`
   and its check; the schema and the description name W48. Nothing else in the record is touched.
3. **The port proof** (`port-proof.py`, W47's): W48's d0219 cut against W47's committed one
   (`results/2026-10-06-w47-g0-operators/rehearsal/d0219-cuts.json.gz`), every leaf value equal but
   provenance. In its printout "W46" is W47's committed cut and "W47" is W48's (`port-proof.txt`).
   W47's proof is strict, and it names ONE key only in W48's cut: `T1.rule.pBeside`, the P rest / P
   inactive aggregates reported beside the pooled target P (the parent's ruling `target-p-pooled`),
   which `cuts.py` gained at `b8907ff07`, after W47's rehearsal cut at `7d5093078`. W48 states it rather
   than absorbing it: that key must be the only difference, and its every value must re-derive from the
   rule groups W47's committed cut already carries (`T1.rule.profiles[profile].groups`, as `cuts.py`
   derives it: A, referenceA, cells, halved = A <= referenceA / 2). Any other difference fails.

    python3.12 -B rehearse.py      (refuses to overwrite its outputs)
"""
from __future__ import annotations

import contextlib
import io
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import inherit  # noqa: E402

W = inherit.W
W48_SYNTHETIC = W.G0 / "tools" / "inherited" / "cuts__test_rule.txt"
CUT_IN_W48 = """
import runpy, sys
sys.path.insert(0, {g0!r})
import inherit
sys.argv = [{cuts!r}, *{argv!r}]
runpy.run_path({cuts!r}, run_name="__main__")
"""


def d0219_cut() -> Path:
    gz = HERE / "d0219-cuts.json.gz"
    if gz.exists():
        raise SystemExit("rehearse: d0219-cuts.json.gz exists; outputs are never overwritten")
    out = HERE / "d0219-cuts.json"
    argv = ["--published", W.REFERENCE["dark"], "--published", W.REFERENCE["light"], "--captures",
            str(W.CANONICAL_CAPTURES), "--out", str(out), "--text", str(HERE / "d0219-cuts.txt")]
    code = CUT_IN_W48.format(g0=str(W.G0), cuts=str(W.CUTS_SOURCE / "cuts.py"), argv=argv)
    got = subprocess.run([sys.executable, "-B", "-c", code], cwd=W.CUTS_SOURCE, capture_output=True, text=True)
    if got.returncode:
        raise SystemExit(f"rehearse: cuts.py exit {got.returncode}: {got.stderr[-1500:]}")
    import gzip
    with gzip.open(gz, "wt") as f:
        f.write(out.read_text())
    out.unlink()
    return gz


def main() -> int:
    for name in ("rehearsal.json", "rehearsal.txt", "port-proof.txt"):
        if (HERE / name).exists():
            raise SystemExit(f"rehearse: {name} exists; outputs are never overwritten")
    d0219_cut()
    R = inherit.tool("rehearsal/rehearse.py", name="w47_rehearse")
    R.HERE = HERE
    code = R.main()
    record = json.loads((HERE / "rehearsal.json").read_text())
    synthetic = W48_SYNTHETIC.read_text().strip().splitlines()
    ran = re.search(r"^Ran (\d+) tests?", W48_SYNTHETIC.read_text(), flags=re.M)
    record["schema"] = "w48-rehearsal-1"
    record["what"] = ("W48 G0 (b): W45's landing rule as W46 bound it (W47's port, inherited by path), on d0219cd684bf "
                      "against itself (cut by W47's cuts under W48's bindings) and on W46's point A by its committed "
                      "gate cut, beside W45's synthetic cases under W48's bindings; nothing rendered")
    record["syntheticW48"] = dict(path=str(W48_SYNTHETIC.relative_to(W.ROOT)), sha256=W.file_sha(W48_SYNTHETIC),
                                  ran=int(ran.group(1)) if ran else None, result=synthetic[-3:])
    record["checks"]["W45's synthetic cases pass under W48's bindings (19)"] = (
        synthetic[-1] == "OK" and ran is not None and int(ran.group(1)) == 19)
    (HERE / "rehearsal.json").write_text(json.dumps(record, indent=1) + "\n")
    with (HERE / "rehearsal.txt").open("a") as f:
        ok = record["checks"]["W45's synthetic cases pass under W48's bindings (19)"]
        f.write(f"CHECK {'PASS' if ok else 'FAIL'}: W45's synthetic cases pass under W48's bindings "
                "(19; tools/inherited/cuts__test_rule.txt)\n")

    port = inherit.tool("rehearsal/port-proof.py", name="w47_port_proof")
    port.W46_CUT = W.W47_G0 / "rehearsal" / "d0219-cuts.json.gz"
    port.W47_CUT = HERE / "d0219-cuts.json.gz"
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        port_code = port.main()
    differ = [ln.strip() for ln in buf.getvalue().splitlines()[1:] if ln.strip()]
    import gzip
    theirs = json.loads(gzip.open(port.W46_CUT).read())["T1"]["rule"]
    ours = json.loads(gzip.open(port.W47_CUT).read())["T1"]["rule"]
    derived = {prof: {g: dict(A=r["groups"][g]["A"], referenceA=r["groups"][g]["referenceA"], cells=r["groups"][g]["cells"],
                              halved=r["groups"][g]["A"] <= 0.5 * r["groups"][g]["referenceA"])
                      for g in ("P rest", "P inactive") if g in r["groups"]}
               for prof, r in theirs["profiles"].items()}
    only_pbeside = differ == ["T1.rule.pBeside: only in W47"] and "pBeside" not in theirs
    rederived = ours.get("pBeside") == derived
    ok = port_code == 0 or (only_pbeside and rederived)
    (HERE / "port-proof.txt").write_text(
        "W48 G0 (b): W47's port-proof.py run under W48's bindings; in its line \"W46\" is W47's committed d0219 cut "
        f"({port.W46_CUT.relative_to(W.ROOT)}) and \"W47\" is W48's ({port.W47_CUT.relative_to(W.ROOT)}).\n"
        + buf.getvalue()
        + f"W47's proof exits {port_code}. The difference it names: {differ or 'none'}.\n"
        + f"W48: the only difference is T1.rule.pBeside, a key W47's committed cut lacks (cuts.py gained it at b8907ff07, "
          f"after W47's cut at 7d5093078): {only_pbeside}; its values re-derive from W47's committed cut's own rule "
          f"groups: {rederived}.\n"
        + f"PORT PROOF {'HOLDS' if ok else 'FAILS'} (every leaf value of W47's cut equal; the one added key stated)\n")
    print((HERE / "port-proof.txt").read_text(), end="")
    record = json.loads((HERE / "rehearsal.json").read_text())
    record["portProof"] = dict(path=str((HERE / "port-proof.txt").relative_to(W.ROOT)), w47ProofExit=port_code,
                               differ=differ, onlyPBeside=only_pbeside, pBesideRederived=rederived, holds=ok)
    (HERE / "rehearsal.json").write_text(json.dumps(record, indent=1) + "\n")
    return 0 if code == 0 and ok and all(record["checks"].values()) else 1


if __name__ == "__main__":
    sys.exit(main())
