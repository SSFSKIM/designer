#!/usr/bin/env python3.12
"""W48 G1: the fit's entry point, W47's `fit/fit.py` inherited by path under W48's bindings with X70's
three-way check added (charter `2026-10-06-w48-dark-operators-fit.md` clause 6, X70; Decision Log 8's
confirmation; claims §5.212 §7 item 2; the tracker's "X70 covers no fit render").

W47's `fit/fit.py`, `search.py` and `joint.py` are W48's tools BY PATH, pinned byte-identical in
`bindings.INHERITED` (part 1). W47's `fit.py` launches `compare` per scope and scale and reads the
matrices it writes without comparing them with the cells it asked for, so a fit render that plans or
measures a different cell set than its scope would not be refused. The pinned bytes cannot change, so this
file loads them under W48's bindings (`inherit.tool`, registered as the module `fit` that `search.py`
and `joint.py` import) and replaces two of the module's functions in place, so every caller (the
module's own `render`, `point`, `read`; `search.Runner`; `joint.py`) reaches the checked form:

- **`render_scale`, before the launch:** the cells requested (the scope's cells the renderer has not
  rendered at that scale, exactly as W47's function computes them) must equal the cells `compare` will
  plan for them (`compare_selects`, W46's transcription of `cli/compare.ts`, through W47's referee
  loader), else REFUSE and launch nothing.
- **`render_scale`, after the launch:** unless the census refused before launching (exit 3, no
  matrix), the rows the launch measured must be exactly the planned cells (no cell missing, none extra,
  none twice), else REFUSE: a partial render (W47's exit 1, `--write-partial`) decides nothing.
- **`read_scale`, before the cut:** per renderer and scale, the union over its scope directories of the
  scopes' cells (requested), their plan, and the rows measured (no cell in two directories) must be
  equal, else REFUSE the reading.

Each check appends one `x70` record to G1's `fit/runs.jsonl`. Nothing else in W47's driver changes.

    python3.12 -B fit.py <verb> ...                   W47's fit.py CLI (start, point, render, read)
    python3.12 -B fit.py search <verb> ...            W47's search.py CLI (stage, full, table)
    python3.12 -B fit.py joint ...                    W47's joint.py CLI

This file is never imported as `fit` (that name is W47's module); its tests load it by path.
"""
from __future__ import annotations

import datetime
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
G0 = HERE.parents[1] / "2026-10-06-w48-g0-declaration"
if str(G0) not in sys.path:
    sys.path.insert(0, str(G0))
import inherit  # noqa: E402  (W48's bindings installed as `bindings` before any W47 module)

W = inherit.W
fit = inherit.tool("fit/fit.py", "fit")
if fit.G1 != HERE:
    raise W.Refusal(f"W48 G1's fit entry is at {HERE}, but the bindings put G1's fit at {fit.G1}")


def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


class X70Refusal(W.Refusal):
    """X70's refusal: the requested, planned and measured cell sets differ."""


def planned(scenes, scale: int) -> set[tuple[str, str]]:
    """The cells `compare --profile <dark scale> --set <fit sets> --scene <scenes>` will plan."""
    ref = W.referees()
    return ref.compare_selects(ref.load_scenes(), [W.PROFILE[scale]], fit.SETS.split(","), set(scenes))


def matrix_cells(path: Path) -> list[tuple[str, str]]:
    return [(r["key"]["profileKey"], r["key"]["sceneId"]) for r in json.loads(path.read_bytes())["cells"]]


def _diff(want: set, got: set) -> str:
    missing = sorted(s for _, s in want - got)
    extra = sorted(f"{p}/{s}" for p, s in got - want)
    return f"{len(missing)} missing {missing[:6]}, {len(extra)} extra {extra[:6]}"


def _record(**row) -> None:
    fit.log(dict(x70=row, at=now()))


def check_sets(where: str, requested: set, plan: set, measured: list | None) -> None:
    """The three-way comparison itself: requested == planned, and (when measured) measured == planned
    with no cell twice. Records the comparison, then refuses on any difference."""
    row = dict(where=where, requested=len(requested), planned=len(plan))
    problems = []
    if plan != requested:
        problems.append(f"compare would plan a different set than requested: {_diff(requested, plan)}")
    if measured is not None:
        got = set(measured)
        row["measured"] = len(measured)
        twice = sorted({f"{p}/{s}" for p, s in measured if measured.count((p, s)) > 1})
        if twice:
            problems.append(f"{len(twice)} cell(s) measured twice {twice[:6]}")
        if got != plan:
            problems.append(f"the rows measured are not the cells planned: {_diff(plan, got)}")
    row["equal"] = not problems
    if problems:
        row["problems"] = problems
    _record(**row)
    if problems:
        raise X70Refusal(f"{where}: X70 REFUSES: " + "; ".join(problems))


_render_scale = fit.render_scale
_read_scale = fit.read_scale


def render_scale(renderer: str, scope: str, scale: int) -> int:
    """W47's `render_scale` with X70 before and after the launch."""
    requested = [s for s in fit.wanted(scope, scale) if s not in fit.rendered(renderer)[scale]]
    if not requested:
        return _render_scale(renderer, scope, scale)
    want = {(W.PROFILE[scale], s) for s in requested}
    where = f"{renderer}/{scope}-{scale}x"
    check_sets(f"{where} before the launch", want, planned(requested, scale), None)
    code = _render_scale(renderer, scope, scale)
    matrix = fit.SCRATCH / renderer / f"{scope}-{scale}x" / "matrix.json"
    if code == 3 and not matrix.exists():
        return code                                   # the census refused before launching; nothing measured
    if not matrix.exists():
        check_sets(f"{where} after the launch (exit {code}, no matrix)", want, want, [])
    check_sets(f"{where} after the launch (exit {code})", want, want, matrix_cells(matrix))
    return code


def read_scale(renderer: str, scale: int) -> dict:
    """W47's `read_scale` after X70 over every scope directory the renderer holds at `scale`."""
    requested, measured = set(), []
    for name in fit.rendered_scopes(renderer, scale):
        scope = name.rsplit("-", 1)[0]
        requested |= {(W.PROFILE[scale], s) for s in fit.wanted(scope, scale)}
        measured += matrix_cells(fit.SCRATCH / renderer / name / "matrix.json")
    if requested:
        check_sets(f"{renderer} {scale}x at read", requested,
                   planned({s for _, s in requested}, scale), measured)
    return _read_scale(renderer, scale)


fit.render_scale = render_scale
fit.read_scale = read_scale


def search():
    return inherit.tool("fit/search.py", "search")


def joint():
    return inherit.tool("fit/joint.py", "joint")


def main(argv) -> int:
    if len(argv) > 1 and argv[1] == "search":
        return search().main(argv[1:])
    if len(argv) > 1 and argv[1] == "joint":
        return joint().main(argv[1:])
    return fit.main(argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
