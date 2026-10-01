#!/usr/bin/env python3.12
"""W43 G0 (e): the wave-local probe and ladder bed for G1b (charter Design "The w-test", "The slider ladder").

    python3.12 -B declare-probe.py          # writes scenes-w43-probe.json, probe-bed.json and pins.json
    python3.12 -B declare-probe.py check    # re-derives both from W42's pinned bed and compares, byte for byte

Every probe and ladder cell is a cell of W42's DECLARED bed, its id reused verbatim, so each has its
seven-run 0.5 counterpart in `w42-archive` (X46: calibration and validation roles only; H and the F
bridges are never selected). The backgrounds and components are copied from W42's pinned scenes file
verbatim, so the side bundle renders byte-identical rasters (W42 G0's `verify-backgrounds.py` read
them back). Nothing here reads a pixel.

The selection, per 2x endpoint (light and dark, active and receded), is the charter's list:

- **A, greys** on the capsule (t = 0) and on rrect-md (s = 96), at 0, 64, 128, 160, 192, 208 and 255:
  native T at each position on both strata. Seven of W42's ten levels: the light free side's M lies
  in [96, 255] and the dark free side's in [0, 192], and these seven span both with the dense part
  where the light free side sits. W42's 176, 224 and 240 are not re-captured.
- **B, two-level checkers** on rrect-md at pitch 64 (every pair) and pitch 16 (48 / 208 and 16 / 112,
  plus 96 / 160 in dark), at levels inside each endpoint's monotone range. 144 / 240 is light only,
  because dark native T falls above 208 at s >= 96 (§5.196 §2.1) and its 240 side could not be inverted.
- **B', P1** (0 / 255) on the capsule at pitch 32 and 64.
- **D, steps** at offset 0 and 32 from the shape centre, both polarities, on rrect-md.
- **C, squares** of 32 pt, both polarities, on rrect-md.

That is 28 cells per endpoint at x = 0.25 (the probe), 1 and 0 (the ladder's ends). x = 0.75 takes ten:
the greys 0, 128, 208 and 255 on both strata, and two free-side cores (the 48 / 208 pitch-64 checker
and the bright 32-pt square). Every pass also recaptures ONE no-glass reference in its run 1,
`ref-checker-64-048-208`, against W42's run-1 frame (Design: the references do not depend on the
slider and are reused; one per pass proves it). The other references are W42's.

The scenes file declares one profile per position and scheme, `apple-macos-27.0-2x-<scheme>-standard-
glass<x>`, with both poses' scene ids as W42's did; the harness selects by scale and accessibility mode
alone, so every pass derives a specification carrying ONE position's keys (scenes.json version 8's note).
"""
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
W42_BED = ROOT / 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed'
W42_PINS = {'scenes-w42-body.json': '4aa06af90eb527b249fdede3d7d102b06c027069552c07dfc7456b7bd2c43ca0',
            'bed.json': '53870f4703681644b00ffcfb5ba60a2fb3a9d1ebe25b5c793b99a0b8b3e50762'}
W42_ARCHIVE = dict(tag='w42-archive', inventorySha256='5481795e0a77ef246f6743d2b6bbe2111a79d858ff9b7a2a4571255595940ed7',
                   assetSha256='1e3d6e65fa3b9a621f1d0f80fb03cc79ee76c29d9b001174983689a7aed31014')
SCENES_FILE, BED_FILE, PINS_FILE = HERE / 'scenes-w43-probe.json', HERE / 'probe-bed.json', HERE / 'pins.json'
ENDPOINTS = (('light', 'active'), ('light', 'receded'), ('dark', 'active'), ('dark', 'receded'))
STATE = {'active': 'rest', 'receded': 'inactive'}
A_LEVELS = (0, 64, 128, 160, 192, 208, 255)
A_SHAPES = ('capsule-button', 'rrect-md')
B_PITCH64 = {'light': ('p2', 'p3', 'p4', 'p5'), 'dark': ('p2', 'p3', 'p4')}
B_PITCH16 = {'light': ('p2', 'p4'), 'dark': ('p2', 'p3', 'p4')}
PROBE_FIXED = ('bp-p1-c32-capsule-button', 'bp-p1-c64-capsule-button',
               'd-d0-hilo-rrect-md', 'd-d0-lohi-rrect-md', 'd-d32-hilo-rrect-md', 'd-d32-lohi-rrect-md',
               'c-s32-hi-rrect-md', 'c-s32-lo-rrect-md')
LADDER_075 = tuple(f'a-g{L:03d}-{s}' for s in A_SHAPES for L in (0, 128, 208, 255)) + \
    ('b-p2-c64-rrect-md', 'c-s32-hi-rrect-md')
RECAPTURED_REFERENCE = 'checker-64-048-208'
# G1b's order (Design, "The two sittings"); a sitting that must stop drops from the bottom (X47).
POSITIONS = ((0.25, 'probe'), (1.0, 'ladder'), (0.0, 'ladder'), (0.75, 'ladder'))
RUNS = 3


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def fmt(x):
    return f'{x:g}'


def profile_key(scheme, x):
    return f'apple-macos-27.0-2x-{scheme}-standard-glass{fmt(x)}'


def w42():
    for name, want in W42_PINS.items():
        if sha((W42_BED / name).read_bytes()) != want:
            raise SystemExit(f'W42 {name} is not the pinned declaration')
    return json.loads((W42_BED / 'scenes-w42-body.json').read_text()), json.loads((W42_BED / 'bed.json').read_text())


def probe_cells(scheme):
    cells = [f'a-g{L:03d}-{s}' for s in A_SHAPES for L in A_LEVELS]
    cells += [f'b-{p}-c64-rrect-md' for p in B_PITCH64[scheme]]
    cells += [f'b-{p}-c16-rrect-md' for p in B_PITCH16[scheme]]
    return cells + list(PROBE_FIXED)


def build():
    spec42, bed42 = w42()
    roles42 = {sid: role for role, ids in spec42['split'].items() for sid in ids}
    scenes42 = {s['id']: s for s in spec42['scenes']}
    passes, cells = {}, {}
    for x, kind in POSITIONS:
        for scheme, pose in ENDPOINTS:
            p42 = f'2x-{scheme}-{pose}'
            chosen = probe_cells(scheme) if x != 0.75 else list(LADDER_075)
            for cid in chosen:
                c = bed42['cells'][cid]
                if c['role'] not in ('calibration', 'validation'):
                    raise SystemExit(f'{cid} is {c["role"]} in W42: only calibration and validation are selectable (X46)')
                if p42 not in c['passes']:
                    raise SystemExit(f'{cid} was not captured in W42 pass {p42}: it has no 0.5 counterpart')
                cells.setdefault(cid, dict(family=c['family'], role=c['role'], background=c['background'],
                                           component=c['component'], geometry=c['geometry'], positions={}))
                cells[cid]['positions'].setdefault(fmt(x), []).append(p42)
            if len(chosen) != len(set(chosen)):
                raise SystemExit('a cell chosen twice')
            refs = sorted({bed42['cells'][cid]['background'] for cid in chosen})
            if RECAPTURED_REFERENCE not in refs:
                raise SystemExit('the recaptured reference has no dependent in this pass')
            passes[f'x{fmt(x)}/{p42}'] = dict(
                x=x, kind=kind, scale=2, scheme=scheme, pose=pose, state=STATE[pose], profile=profile_key(scheme, x),
                cells=sorted(chosen), references=refs, recapturedReference=RECAPTURED_REFERENCE,
                referencesReusedFrom=f'w42-archive run 1 of pass {p42}', runs=RUNS,
                w42Counterparts=f"apple-macos-27.0-2x-{scheme}-standard-glass0.5/<cell>__{STATE[pose]}")
    # the scenes file: W42's entries for every selected glass scene and its reference, verbatim
    ids = set()
    for p in passes.values():
        ids |= {f'{c}__{p["state"]}' for c in p['cells']}
        ids |= {f'ref-{b}__{p["state"]}' for b in p['references']}
    missing = sorted(i for i in ids if i not in scenes42)
    if missing:
        raise SystemExit(f'not W42 scene ids: {missing}')
    backgrounds = {scenes42[i]['background'] for i in ids}
    components = {scenes42[i]['component'] for i in ids}
    split = {r: sorted(i for i in ids if roles42[i] == r) for r in ('calibration', 'validation', 'holdout', 'recorded',
                                                                       'probe')}
    if split['holdout'] or split['probe'] or split['recorded']:
        raise SystemExit('the probe declares only calibration and validation scenes')
    profiles = []
    for x, _ in POSITIONS:
        for scheme in ('light', 'dark'):
            mine = set()
            for p in passes.values():
                if p['x'] == x and p['scheme'] == scheme:
                    mine |= {f'{c}__{p["state"]}' for c in p['cells']}
                    mine |= {f'ref-{b}__{p["state"]}' for b in p['references']}
            profiles.append(dict(key=profile_key(scheme, x), colorScheme=scheme, a11y='standard', scenes=sorted(mine)))
    spec = {
        '$comment': [
            'W43 G0 (e): the wave-local probe and ladder bed for G1b (charter',
            '2026-10-01-w43-glass-0-25-generation.md v1.2, Design "The w-test" and "The slider ladder";',
            'clause 1). Generated by packages/calibration/results/2026-10-01-w43-g0-declaration/bed/',
            'declare-probe.py; never edit by hand. Every scene, background and component is W42\'s',
            '(scenes-w42-body.json 4aa06af9...) verbatim and keeps W42\'s id and split role, so each glass',
            'cell has its seven-run 0.5 counterpart in w42-archive (X46). One profile per slider position',
            'and scheme; a pass carries one position\'s keys. Nothing here is filed as a fixture: G1b',
            'archives it as w43-archive-g1b (clause 5).'],
        'version': 1, 'canvas': spec42['canvas'],
        'backgrounds': {k: spec42['backgrounds'][k] for k in sorted(backgrounds)},
        'components': {k: spec42['components'][k] for k in sorted(components)},
        'tints': {}, 'scenes': [scenes42[i] for i in sorted(ids)], 'profiles': profiles, 'split': split,
    }
    counts = {}
    for key, p in passes.items():
        counts[key] = dict(glass=len(p['cells']), recapturedReferences=1, captures=len(p['cells']) * RUNS + 1)
    by_x = {}
    for key, p in passes.items():
        t = by_x.setdefault(fmt(p['x']), dict(kind=p['kind'], passes=0, glassPerEndpoint=set(), captures=0))
        t['passes'] += 1
        t['glassPerEndpoint'].add(len(p['cells']))
        t['captures'] += counts[key]['captures']
    for t in by_x.values():
        t['glassPerEndpoint'] = sorted(t['glassPerEndpoint'])
    companion = dict(
        schema='w43-probe-bed-1', charter='docs/doperpowers/specs/2026-10-01-w43-glass-0-25-generation.md',
        scenesFile=SCENES_FILE.name, w42=dict(scenesSha256=W42_PINS['scenes-w42-body.json'],
                                            bedSha256=W42_PINS['bed.json'], archive=W42_ARCHIVE),
        order=[dict(x=x, kind=k) for x, k in POSITIONS],
        dropOrder='a sitting that must stop drops from the bottom: x = 0.75, then 0, then 1, then the probe (X47)',
        runs=RUNS, protocol='normal (W42 bed rows)', passes=passes, counts=counts, byPosition=by_x,
        totals=dict(passes=len(passes), glassCaptures=sum(len(p['cells']) * RUNS for p in passes.values()),
                    references=len(passes), captures=sum(c['captures'] for c in counts.values())),
        cells={k: cells[k] for k in sorted(cells)},
        selection=dict(aLevels=list(A_LEVELS), aShapes=list(A_SHAPES), bPitch64=B_PITCH64, bPitch16=B_PITCH16,
                       fixed=list(PROBE_FIXED), ladder075=list(LADDER_075),
                       excluded={'b-p5-*-rrect-md in dark': 'dark native T falls above 208 at s >= 96 (§5.196 §2.1); '
                                 'its 240 side is outside the monotone range',
                                 'rrect-ml, rrect-lg and every 1x cell': "W42 Deferred at close 1-2: no Gaussian "
                                 'structure closes them; they are not w-test support and add nothing the ladder '
                                 'reads that the 2x mid shapes do not',
                                 'H and the F bridges': 'X46: calibration and validation counterparts only'}))
    return spec, companion


def render(spec, companion):
    s = json.dumps(spec, indent=2, ensure_ascii=False) + '\n'
    b = json.dumps(companion, indent=2, ensure_ascii=False) + '\n'
    pins = json.dumps({SCENES_FILE.name: sha(s.encode()), BED_FILE.name: sha(b.encode())}, indent=2) + '\n'
    return s, b, pins


def main(argv):
    spec, companion = build()
    s, b, pins = render(spec, companion)
    if len(argv) > 1 and argv[1] == 'check':
        ok = all(p.exists() and p.read_text() == t for p, t in ((SCENES_FILE, s), (BED_FILE, b), (PINS_FILE, pins)))
        print('check: ' + ('the committed files are this generator\'s output' if ok else 'MISMATCH'))
        return 0 if ok else 1
    SCENES_FILE.write_text(s)
    BED_FILE.write_text(b)
    PINS_FILE.write_text(pins)
    print(json.dumps(dict(totals=companion['totals'], byPosition=companion['byPosition'],
                          scenes=len(spec['scenes']), backgrounds=len(spec['backgrounds']),
                          components=len(spec['components']), profiles=[p['key'] for p in spec['profiles']]), indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
