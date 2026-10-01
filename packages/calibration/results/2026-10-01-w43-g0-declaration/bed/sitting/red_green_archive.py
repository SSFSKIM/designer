#!/usr/bin/env python3.12
"""The archive's red/green case (charter G0 (d): "the archive storing each distinct frame once by
SHA-256, with per-run membership, so a unanimous cell costs one frame"), stubs only.

RED, on W42's committed producer (results/2026-09-29-w42-g0-declaration/bed/sitting/w42_archive.py)
over its own suite's synthetic sitting (that directory's test_archive.sitting_tree): every stored
frame copy is counted across the cells' `states` bundles against the distinct SHA-256s. W42
bundles each cell's frames inside the cell, so every no-glass reference is stored again in every
cell that depends on it.

GREEN, on W43's producer over test_archive.py's synthetic sitting (frames shared within a cell,
across cells, across passes and with a background raster): the frame copies stored equal the
distinct SHA-256s, a seven-run unanimous cell costs one frame, and replay recomputes every
statistic from the archive with the raw root denied.

`scenario()` returns dict(name, red, green, red_ok, green_ok) for red-green.py.
"""
import gzip
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
W42_SITTING = REPO / 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/sitting'
NAME = '8. the archive stores each distinct frame once, by SHA-256'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def red(tmp):
    TA = load('w42_test_archive_for_red_green', W42_SITTING / 'test_archive.py')
    A = TA.A
    raw = Path(tmp) / 'w42-raw'
    TA.sitting_tree(raw)
    out = Path(tmp) / 'w42-archive'
    inventory = A.produce(raw, out, wave=A.wave_module().default_wave(), passes=TA.PASSES)
    copies, distinct, stored_bytes, sizes, cells_of = 0, set(), 0, {}, {}
    for row in inventory['entries']:
        if row['kind'] != 'states':
            continue
        _, blobs = A.unbundle((out / row['path']).read_bytes())
        copies += len(blobs)
        for digest, raw_bytes in blobs.items():
            distinct.add(digest)
            stored_bytes += len(raw_bytes)
            sizes[digest] = len(raw_bytes)
            cells_of.setdefault(digest, set()).add(row['cell'])
    most = max(len(c) for c in cells_of.values())
    text = (f'{inventory["archivedCells"]} cells store {copies} frame copies of {len(distinct)} distinct SHA-256s '
            f'({stored_bytes:,} bytes for {sum(sizes.values()):,} distinct); one frame is stored in {most} cells')
    return copies > len(distinct), text


def green(tmp):
    TA = load('w43_test_archive_for_red_green', HERE / 'test_archive.py')
    A = TA.A
    raw = TA.sitting_tree(Path(tmp) / 'w43-raw')
    out = Path(tmp) / 'w43-archive'
    inventory = TA.produce(raw, out)
    copies = sum(1 for _ in (out / 'frames').iterdir())
    row = next(r for r in inventory['cells'] if r['cell'] == TA.PICKS['unanimous'])
    rec = json.loads(gzip.decompress((out / row['path']).read_bytes()))
    result = A.replay(out, deny_raw_root=raw)
    try:
        (raw / 'logs' / 'orchestrator-status.txt').read_bytes()
        denied = False
    except PermissionError:
        denied = True
    ok = (copies == inventory['distinctFrames'] < inventory['frameOccurrences'] and (row['runs'], row['frames']) == (7, 1)
          and len(rec['statistics']) == 1 and result['identical'] and result['frames'] == copies and denied)
    text = (f'{inventory["archivedCells"]} cells and {len(inventory["runs"])} runs name {inventory["frameOccurrences"]} '
            f'frame occurrences of {inventory["distinctFrames"]} distinct SHA-256s, stored as {copies} files; the '
            f'unanimous cell: {row["runs"]} runs, {row["frames"]} frame; replay with the raw root denied: '
            f'{"identical" if result["identical"] else "DIFFERS"} over {result["cells"]} cells, raw root '
            f'{"refused" if denied else "READABLE"}')
    return ok, text


def scenario():
    with tempfile.TemporaryDirectory() as tmp:
        red_ok, red_text = red(tmp)
        green_ok, green_text = green(tmp)
    return dict(name=NAME, red=red_text, green=green_text, red_ok=red_ok, green_ok=green_ok)


if __name__ == '__main__':
    r = scenario()
    print(f'{r["name"]}\n  RED   (W42): {r["red"]}  [{"defect shown" if r["red_ok"] else "NOT SHOWN"}]\n'
          f'  GREEN (W43): {r["green"]}  [{"fixed" if r["green_ok"] else "NOT FIXED"}]')
    raise SystemExit(0 if r['red_ok'] and r['green_ok'] else 1)
