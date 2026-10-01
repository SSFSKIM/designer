#!/usr/bin/env python3.12
"""W43 G1a: the repeat bar, read from the archive of record before plurality (charter clause 5).

report-bars.py <fetched archive root> --out <dir>

The declaration (`../../2026-10-01-w43-g0-declaration/declaration.json`, item repeatsAndBar): per
cell, region statistic and channel, the bar is 0.5 + 0.5 x the largest pairwise separation of the
run medians, computed from the archive before plurality and published before G2 reads.

Only the archive is read: every raw input and every product of one is denied for the process by
the archive tool's own audit hook, as replay-denied.py does. Each run a cell record names is
resolved to its stored frame, whose SHA-256 must be its name.

Strata are never pooled (W39 and W42): the canonical bed (normal protocol, seven runs), the
opening canonical bridges (normal, three), and W42's sentinels at the opening and at the close
(long, three each). The pose check has one run and no bar.

The identity step. A cell whose runs in a stratum all name ONE frame (equal SHA-256 of the PNG
bytes) has identical pixels in every run, so every statistic of those pixels, any region median
of any instrument included, has a spread of exactly 0 and the bar is exactly 0.5. Such a cell
needs no instrument to state its bar. For a cell with more than one state, the spread is computed
here on the archive's own instrument-free statistics (per-channel mean, min and max of the frame);
its region statistics are the bridge verdicts' business (bridge.json, region deltas), not this
report's, and no such cell is a published fixture.
"""
import argparse
import collections
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOL = HERE.parents[1] / '2026-10-01-w43-g0-declaration/bed/sitting/w43_archive.py'
W43 = Path.home() / 'vitrea-w43'
DENIED = [W43 / 'g1a-run', W43 / 'g1a-archive', W43 / 'g1a-release', W43 / 'archive-copy-g1a',
          W43 / 'g1a-stops', W43 / 'g1a-prelaunch']
SCHEMA = 'w43-repeat-bar-1'
CHANNELS = 'RGB'


def stratum(pass_name):
    if pass_name.startswith('bed-'):
        return 'bed'
    if pass_name.startswith('open-canonical-'):
        return 'open-canonical'
    if pass_name.startswith('open-w42-'):
        return 'open-w42'
    if pass_name.startswith('close-w42-'):
        return 'close-w42'
    return 'pose-check'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('root', type=Path)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    spec = importlib.util.spec_from_file_location('w43_archive', TOOL)
    A = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(A)
    for d in DENIED:
        A.deny(d)
    root = args.root
    tree = A.verify_tree(root)
    rows, heads = [], collections.defaultdict(lambda: collections.Counter())
    states = collections.defaultdict(collections.Counter)
    for path in sorted(root.glob('*/*.cell.json.gz')):
        record = json.loads(gzip.decompress(path.read_bytes()))
        by = collections.defaultdict(list)
        for run in record['runs']:
            frame = run['frame']
            raw = (root / 'frames' / f'{frame}.png').read_bytes()
            if hashlib.sha256(raw).hexdigest() != frame:
                raise ValueError(f'{record["cell"]}: frame {frame} is not its name')
            by[stratum(run['pass'])].append(run)
        for name, runs in sorted(by.items()):
            frames = [r['frame'] for r in runs]
            distinct = sorted(set(frames))
            row = dict(cell=record['cell'], role=record['role'], stratum=name, runs=len(runs),
                       distinctFrames=len(distinct),
                       stateCounts=sorted(collections.Counter(frames).values(), reverse=True))
            if len(runs) < 2:
                row['status'] = 'one run, no bar'
            elif len(distinct) == 1:
                row['status'] = 'unanimous: every statistic identical, bar exactly 0.5'
                row['bar'] = 0.5
            else:
                stats = record['statistics']
                bars = {}
                for kind in ('mean', 'min', 'max'):
                    for c, ch in enumerate(CHANNELS):
                        values = [stats[f][kind][c] for f in frames]
                        bars[f'{kind}|{ch}'] = 0.5 + 0.5 * (max(values) - min(values))
                row['status'] = 'more than one state'
                row['instrumentFreeBars'] = bars
                row['bar'] = max(bars.values())
            rows.append(row)
            heads[name][row['status']] += 1
            heads[name]['cells'] += 1
            heads[name]['captures'] += len(runs)
            if len(distinct) > 1:
                states[name][record['cell']] = row['stateCounts']
    args.out.mkdir(parents=True, exist_ok=True)
    body = json.dumps(dict(schema=SCHEMA, archiveInventory=tree['inventorySha256'], rows=rows),
                      indent=1, sort_keys=True).encode() + b'\n'
    (args.out / 'bar.json.gz').write_bytes(gzip.compress(body, mtime=0))
    headlines = dict(
        schema=SCHEMA, archiveInventory=tree['inventorySha256'], treeEntries=tree['entries'],
        barJsonSha256=hashlib.sha256(body).hexdigest(), denied=[str(d) for d in DENIED],
        strata={k: dict(v) for k, v in sorted(heads.items())},
        cellsWithMoreThanOneState={k: dict(v) for k, v in sorted(states.items())},
        largestBar={name: max((r['bar'] for r in rows if r['stratum'] == name and 'bar' in r), default=None)
                    for name in sorted(heads)})
    (args.out / 'bar-headlines.json').write_text(json.dumps(headlines, indent=2) + '\n')
    print(json.dumps(headlines, indent=2))


if __name__ == '__main__':
    main()
