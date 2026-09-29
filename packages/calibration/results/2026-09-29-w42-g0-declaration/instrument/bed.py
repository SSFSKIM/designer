"""W42 G0 instrument: the bed the clause-2 proofs render on — the DECLARED bed of the bed stream
(`../bed/scenes-w42-body.json` and `../bed/bed.json`, pinned by SHA-256 as `../bed/pins.json` records them at
w42-g0-bed 07b45391), so every synthetic render sits on the exact ids, levels, pitches, offsets and depths G1 captures.

`cells(ep, scale)` returns the calibration and validation cells of one pass (the split's H and the F bridges
are left out: the instrument is never tuned on the holdout's geometry, and the bridges are not under clause
6). Each cell carries its family letter, role and bed.json geometry.

Refraction (the parent's ruling on the bed stream's finding, 2026-09-29): in the ACTIVE pose Apple refracts
inside an inner band reaching 20 pt inward from the edge and an outer reach of 19.2 pt beyond it, and LT
models neither. `forward.Cell`'s active deep mask already sits beyond the band plus the narrow kernel's
support (forward.band_d_in). `refraction_exclusions(ep, scale)` lists the active cells whose informative
content lies only inside the zones, each with its reason; `cells()` leaves them out of the fit set unless
`with_excluded=True`. Receded cells are unaffected.
"""
import hashlib
import json
import os
import subprocess

import geometry as G
import forward as F

HERE = os.path.dirname(os.path.abspath(__file__))
# The declaration this instrument's proofs rendered on: w42-g0-bed 07b45391 (the s = 32 receded rrect-sm rows
# added to 5ba68aeb's bed, no cell changed). After G0's integration the files sit beside this folder; before
# it, they are read from the bed branch's commit itself, so an uncommitted edit in the bed stream's worktree
# can never be read as the declaration.
BED_COMMIT = '07b453915fa653a2a7110d67d3a09531abffecf1'
PINS = {'scenes-w42-body.json': 'd8adbaac4b35d2fcded103861828b35dcb86d4f11cddd202846f00a757773e51',
        'bed.json': 'a4e9640ef89f8f2ec7625c28d15901ba96f50e9fced2108a6458c462ae63d4b1'}
REL = 'packages/calibration/results/2026-09-29-w42-g0-declaration/bed'
SIBLING = os.path.join(HERE, '..', 'bed')


def _pinned(d):
    return all(os.path.exists(os.path.join(d, f)) and
               hashlib.sha256(open(os.path.join(d, f), 'rb').read()).hexdigest() == sha for f, sha in PINS.items())


def _bed_dir():
    if _pinned(SIBLING):
        return SIBLING
    out = f'/tmp/w42-bed-{BED_COMMIT[:8]}'
    os.makedirs(out, exist_ok=True)
    for f in PINS:
        data = subprocess.run(['git', '-C', HERE, 'show', f'{BED_COMMIT}:{REL}/{f}'], check=True,
                              capture_output=True).stdout
        open(os.path.join(out, f), 'wb').write(data)
    assert _pinned(out), f'the bed files at {BED_COMMIT[:8]} are not the pinned declaration'
    return out


BED_DIR = _bed_dir()
SCENES = G.load_scenes(os.path.join(BED_DIR, 'scenes-w42-body.json'))
DECL = json.load(open(os.path.join(BED_DIR, 'bed.json')))
CELLS = DECL['cells']
ROLES_FIT = ('calibration', 'validation')


def pass_key(ep, scale):
    scheme, pose = ep.split('-')
    return f'{scale}x-{scheme}-{"active" if pose == "rest" else "receded"}'


def refraction_exclusions(ep, scale):
    """{id: reason} for the active cells whose informative content lies only inside the refraction zones."""
    if not ep.endswith('rest'):
        return {}
    out = {}
    key = pass_key(ep, scale)
    for cid, c in CELLS.items():
        if key not in c['passes']:
            continue
        g = c['geometry']
        if c['family'] == 'D' and 'stepFromShapeCentre' in g:
            comp = G.COMPONENTS[g['shape']]
            half = comp['size'][0] / 2
            outside = abs(g['stepFromShapeCentre']) - half
            if outside > 0:
                out[cid] = (f'step {outside:g} pt outside the edge, inside the {F.BAND_OUT} pt outer refraction '
                            'reach: refraction-confounded')
        if c['family'] == 'C' and 'depth' in g and g['depth'] - g['patchSize'] / 2 < F.BAND_IN:
            out[cid] = (f"patch at depth {g['depth']:g} pt (near edge {g['depth'] - g['patchSize'] / 2:g} pt): "
                        f'inside the {F.BAND_IN} pt inner refraction band')
    return out


def cells(ep, scale=2, letters=None, ids=None, rgb=False, roles=ROLES_FIT, with_excluded=False):
    scheme, pose = ep.split('-')
    key = pass_key(ep, scale)
    excl = {} if with_excluded else refraction_exclusions(ep, scale)
    out = []
    for cid, c in CELLS.items():
        if key not in c['passes'] or c['role'] not in roles or cid in excl:
            continue
        letter = c['family']
        if letters and letter not in letters:
            continue
        if ids and cid not in ids:
            continue
        sc = f'{cid}__{"rest" if pose == "rest" else "inactive"}'
        spec = next(s for s in SCENES if s['id'] == sc)
        cell = F.Cell(f'{scale}x|{cid}', spec['background'], spec['component'], scale, scheme, pose,
                      rgb=rgb or letter == 'E')
        cell.letter, cell.role, cell.geometry, cell.bed_id = letter, c['role'], c['geometry'], cid
        if cell.mask.sum() == 0:
            continue
        out.append(cell)
    return out


def empty_mask_cells(ep, scale):
    """Cells a pass declares whose deep mask is empty under the band rule (reported beside the exclusions)."""
    key = pass_key(ep, scale)
    scheme, pose = ep.split('-')
    out = []
    for cid, c in CELLS.items():
        if key in c['passes'] and c['role'] in ROLES_FIT:
            comp = G.COMPONENTS[c['component']]
            cell = F.Cell(cid, c['background'], c['component'], scale, scheme, pose)
            if cell.mask.sum() == 0:
                out.append(cid)
    return out
