#!/usr/bin/env python3
"""W23 G2: every `REGRESSION_FLOORS` entry re-read against the landed matrix.

A floor says "no worse than this" about a row whose adopted bound the bed does not meet. Two things
have to be true of each at a landing and neither is true by construction: the landed reading must
still hold the floor, and the row must still MISS its adopted bound — a floor whose cell recovered
its bound is inert and comes off with its reason — and this landing moves the rim on every
cell of the bed, so a floor going inert is what the wave is FOR and is expected here rather than
not.

    python3 g2-floors.py <before matrix>
"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..'))
CAL = os.path.join(ROOT, 'packages', 'calibration')
SOURCE = open(os.path.join(CAL, 'test', 'adopted-thresholds.test.ts')).read()


def floors():
    block = SOURCE.split('const REGRESSION_FLOORS', 1)[1].split('};', 1)[0]
    return [(m.group(1), float(m.group(2)), float(m.group(3)))
            for m in re.finditer(r'"([^"]+)":\s*\{\s*measured:\s*([\d.]+),\s*floor:\s*([\d.]+)\s*\}',
                                 block)]


def load(path):
    best = {}
    for cell in json.load(open(path))['cells']:
        key = (cell['tier'], cell['fixtureSet'], cell['key']['sceneId'], cell['key']['profileKey'])
        if key not in best or cell['capturedAt'] > best[key]['capturedAt']:
            best[key] = cell
    return best


def reading(cell, metric):
    for axis in ('shape', 'perceptual', 'material', 'coherence'):
        entry = (cell.get(axis) or {}).get(metric)
        if entry is not None:
            return entry['value'] if isinstance(entry, dict) else entry
    return None


def main():
    before = load(sys.argv[1])
    landed = load(os.path.join(CAL, 'results', 'matrix.json'))
    rows = floors()
    print(f"{len(rows)} floors (UNMET_ROWS is "
          f"{re.search(r'const UNMET_ROWS = (\d+)', SOURCE).group(1)})\n")
    bad = 0
    for key, recorded, floor in rows:
        head, metric = key.split(' :: ')
        tier, fixture_set, scene, profile = [part.strip() for part in head.split(' / ')]
        cell = landed.get((tier, fixture_set, scene, profile))
        was = before.get((tier, fixture_set, scene, profile))
        now = reading(cell, metric) if cell else None
        then = reading(was, metric) if was else None
        direction = 'ge' if floor < recorded or metric.startswith('silhouetteIoU') or metric == 'ssimMean' else 'le'
        if metric in ('contourDistanceMean', 'contourDistanceP95'):
            direction = 'le'
        held = now is not None and (now >= floor if direction == 'ge' else now <= floor)
        if not held:
            bad += 1
        print(f"{key}\n    floor {direction} {floor}   recorded {recorded}   "
              f"W21 bed {then}   landed {now}   {'held' if held else 'BROKEN'}")
    print(f"\n{len(rows) - bad} held, {bad} broken")


main()
