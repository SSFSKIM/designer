"""W50 grounding: inventory admitted native cells; read only non-held uniform greys.

Run with /Users/new/vitrea-w49/py/bin/python -I <this file>. Archives must first pass
 their own fetch/verify commands. No capture, renderer, fit or publication is invoked.
The W42 table's completed rows are deliberately not treated as measured ordinates.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import re

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
RESULTS = HERE.parent
ARCHIVES = {
    'w39': ('2026-09-26-w39-g1-colour-edge-sitting',
            'apps/reference-apple/scenes-w39-colour-edge.json'),
    'w42': ('2026-09-30-w42-g1-sitting',
            'packages/calibration/results/2026-09-29-w42-g0-declaration/bed/scenes-w42-body.json'),
    'w43g1a': ('2026-10-01-w43-g1a-sitting', 'apps/reference-apple/scenes.json'),
    'w43g1b': ('2026-10-02-w43-g1b-sitting',
              'packages/calibration/results/2026-10-01-w43-g0-declaration/bed/scenes-w43-probe.json'),
}


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def role_of(doc, scene):
    return next((k for k, v in doc['split'].items()
                 if not k.startswith('$') and isinstance(v, list) and scene in v), 'unclassified')


def describe(source, doc, profile, scene):
    bg = doc['backgrounds'][scene['background']]
    comp = doc['components'][scene['component']]
    if 'size' not in comp or comp.get('opaque') or scene.get('tint'):
        return None
    if source == 'w39':
        if not scene['id'].startswith('neutral-') or '-colour__' not in scene['id']:
            return None
    elif source in ('w42', 'w43g1b'):
        if not scene['id'].startswith('a-'):
            return None
    elif bg['kind'] != 'solid' and scene['background'] != 'impulse':
        return None
    if bg['kind'] == 'solid' and source not in ('w39', 'w42', 'w43g1b'):
        if max(bg['srgb']) > 69:
            return None
    key = profile['key']
    return dict(source=source, profile=key, scene=scene['id'],
                levelRGB=bg.get('srgb'), background=scene['background'],
                kind='uniform' if bg['kind'] == 'solid' else 'structured-black-field',
                span=min(comp['size']), component=scene['component'], pose=scene['state'],
                glass=float(re.search(r'glass([\d.]+)', key)[1]),
                scale=int(re.search(r'-(\d)x-', key)[1]), role=role_of(doc, scene['id']))


def png_core(raw, attestation):
    """A central 8x8 CSS-px square, wholly inside every uniform surface in this read.

    This is a diagnostic, not a replacement for any adopted deep/silhouette metric.
    It is deliberately independent of detected silhouettes (which fail on dark solids).
    """
    rgb = np.asarray(Image.open(io.BytesIO(raw)).convert('RGB'))
    shape = attestation['suppliedPaths'][0]
    ox, oy = shape['frameOrigin']
    _, _, w, h = shape['rect']
    scale = attestation['windowFrame']['backingScaleFactor']
    cx, cy = (ox + w / 2) * scale, (oy + h / 2) * scale
    core = rgb[int(cy - 4 * scale):int(cy + 4 * scale),
               int(cx - 4 * scale):int(cx + 4 * scale)].reshape(-1, 3)
    assert len(core) == 64 * scale * scale
    return dict(pixels=len(core), medianRGB=np.median(core, axis=0).tolist(),
                minRGB=core.min(axis=0).tolist(), maxRGB=core.max(axis=0).tolist())


def archive_measure(label, base, inv, entry):
    assert not entry['path'].startswith('holdout/'), 'No held-out pixel/statistic read.'
    raw = (base / entry['path']).read_bytes()
    assert sha(raw) == entry['sha256']
    d = json.loads(gzip.decompress(raw))
    if label == 'w39':
        return dict(statistic='W39 archived path-deep median, every distinct state',
                    states=[v['members'][0]['deep'] for v in d['statistics'].values()],
                    runs=len(d['runs']))
    if label == 'w42':
        e = next(e for e in inv['entries']
                 if e['cell'] == entry['cell'] and e['kind'] == 'states')
        raw = (base / e['path']).read_bytes()
        assert sha(raw) == e['sha256']
        head, _, body = gzip.decompress(raw).partition(b'\n')
        header = json.loads(head)
        blobs = {key: body[v['offset']:v['offset'] + v['length']]
                 for key, v in header['blobs'].items()}
        assert all(sha(v) == k for k, v in blobs.items())
    else:
        blobs = {r['frame']: (base / 'frames' / (r['frame'] + '.png')).read_bytes()
                 for r in d['runs']}
        assert all(sha(v) == k for k, v in blobs.items())
    runs = [dict(run=r['run'], frame=r['frame'],
                 core=png_core(blobs[r['frame']], r['attestation'])) for r in d['runs']]
    return dict(statistic='central 8x8 CSS-px square, encoded RGB', runs=runs)


def main():
    rows, witnesses, readings = [], [], []
    for label, (wave, scenes) in ARCHIVES.items():
        record = load(RESULTS / wave / 'archive/fetch-verified.json')
        base = Path.home() / '.cache/vitrea-archives' / record['sha256'] / 'extracted/archive'
        inv = load(base / 'inventory.json')
        witnesses.append(dict(source=label, release=record['tag'], archiveSha256=record['sha256'],
                              inventorySha256=sha((base / 'inventory.json').read_bytes())))
        doc = load(ROOT / scenes)
        by_scene = {s['id']: s for s in doc['scenes']}
        profiles = {p['key']: p for p in doc['profiles']}
        entries = inv.get('cells')
        if entries is None:
            entries = [e for e in inv['entries'] if e['kind'] == 'statistics' and e['admitted']]
        for e in entries:
            profile, scene_id = e['cell'].split('/')
            if '-dark-standard-glass' not in profile:
                continue
            if label in ('w42', 'w43g1b') and not scene_id.startswith('a-'):
                # These inventories select family A, not structured probes/restore controls.
                continue
            if scene_id not in by_scene:
                # W43 G1a's W42 structured bridge cells add no uniform anchor.
                assert label == 'w43g1a' and scene_id.startswith('f-'), (label, scene_id)
                continue
            row = describe(label, doc, profiles[profile], by_scene[scene_id])
            if row is None:
                continue
            row.update(status='ADMITTED_ARCHIVE', archivePath=e['path'], archiveEntrySha256=e['sha256'])
            row['role'] = e['path'].split('/')[0]
            rows.append(row)
            # Dense inventory is public metadata; read only the lowest measured uniform anchors.
            if label != 'w43g1a' and row['kind'] == 'uniform' and max(row['levelRGB']) <= 64:
                assert row['role'] != 'holdout'
                readings.append(dict(cell=e['cell'], source=label, span=row['span'],
                                     levelRGB=row['levelRGB'], reading=archive_measure(label, base, inv, e)))
    for label, scenes in [('canonical', 'scenes.json'), ('w34', 'scenes-w34-contour.json')]:
        doc = load(ROOT / 'apps/reference-apple' / scenes)
        by_scene = {s['id']: s for s in doc['scenes']}
        for profile in doc['profiles']:
            if '-dark-standard-glass' not in profile['key']:
                continue
            for scene_id in profile['scenes']:
                row = describe(label, doc, profile, by_scene[scene_id])
                if row is None:
                    continue
                png = ROOT / 'apps/reference-apple/fixtures' / profile['key'] / (scene_id + '.png')
                row['status'] = 'NATIVE_FIXTURE' if png.exists() else 'DECLARED_NOT_IN_CANONICAL_TREE'
                if png.exists():
                    row['nativeSha256'] = sha(png.read_bytes())
                rows.append(row)
    rows.sort(key=lambda x: (x['source'], x['profile'], x['scene']))
    out = dict(schema='w50-native-inventory-1', archives=witnesses, cells=rows,
               note='Metadata only for held-out cells. W34 declaration is not proof of archived admission; '
                    'W36 records span-44 black readings. No W42 completed ordinate is a native cell.')
    (HERE / 'native-inventory.json').write_text(json.dumps(out, indent=2) + '\n')
    (HERE / 'native-low-anchors.json').write_text(json.dumps(readings, indent=2) + '\n')
    with (HERE / 'native-inventory.csv').open('w') as stream:
        w = csv.writer(stream, lineterminator='\n')
        w.writerow(['source', 'glass', 'scale', 'span', 'pose', 'RGB', 'scene', 'role', 'status'])
        for r in rows:
            w.writerow([r[k] for k in ['source', 'glass', 'scale', 'span', 'pose']]
                       + [r['levelRGB'], r['scene'], r['role'], r['status']])
    print(f'{len(rows)} inventory rows; {len(readings)} non-held low-anchor readings; no new pixels.')


if __name__ == '__main__':
    main()
