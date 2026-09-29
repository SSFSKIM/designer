#!/usr/bin/env python3.12
"""Transfer the sealed 536-cell web baseline using guarded normal native repeats.

The web frames are already captured. Live source/runtime checks belong to the
capture, not this read-only transfer; the original evidence and native readers
remain pinned to the captured preparation and authority instead.
"""
import gzip
import hashlib
from pathlib import Path
import subprocess
import sys

import baseline as b

INSTRUMENT_ROOTS = tuple(b.runner.INSTRUMENT_ROOTS)
G2 = b.RESULTS / '2026-09-26-w39-g2-identification'


def select_normal(runs):
    """Keep the declared repeat order; state deduplication is only storage."""
    normal = [r for r in runs if r['admitted'] and r['protocol'] == 'normal']
    counts = {
        'admittedNormal': len(normal),
        'admittedLongSentinel': sum(r['admitted'] and r['protocol'] == 'long' for r in runs),
        'excludedNormal': sum(not r['admitted'] and r['protocol'] == 'normal' for r in runs),
        'excludedLongSentinel': sum(not r['admitted'] and r['protocol'] == 'long' for r in runs),
    }
    if len(normal) != 7 or len({r['run'] for r in normal}) != 7:
        raise ValueError('seven distinct normal admitted repeats required')
    return normal, counts


def verify_frozen_inputs():
    """Verify all frozen pixels and original code without requiring live runtime identity."""
    record = b.load(b.HERE / 'preparation.json')
    frozen = b.load(b.HERE / 'frozen-baseline.json')
    b.verify_authority(record)  # Checks committed preparation, baseline.py and X6 authority.
    b.verify_frozen(record, frozen)  # Checks all 536 PNGs, projections and descriptors.
    if frozen['sourceRevision'] != record['sourceRevision']:
        raise ValueError('baseline source revision changed')
    if record['inventorySha256'] != b.runner.INVENTORY_SHA:
        raise ValueError('baseline native inventory identity changed')
    if b.wave.scenes_sha != record['scenesSha256'] or b.wave.split_sha != record['splitSha256']:
        raise ValueError('native scene/split metadata changed')
    if len(frozen['captures']) != 536 or set(record['cells']) != set(frozen['captures']):
        raise ValueError('baseline capture coverage changed')
    # Preparation's source digest inventory is a claim about the OLD revision,
    # not a demand to keep the current runtime pre-W41. Check every old source
    # against that revision, then check executed instrument code in this tree.
    for name, digest in record['sources'].items():
        previous = b.runner.git(b.ROOT, 'show', record['sourceRevision'] + ':' + name)
        if hashlib.sha256(previous).hexdigest() != digest:
            raise ValueError('original source metadata changed: ' + name)
        if name.startswith(INSTRUMENT_ROOTS):
            if b.sha(b.ROOT / name) != digest or b.runner.committed(b.ROOT, name) != digest:
                raise ValueError('native instrument/source changed: ' + name)
    # Native admission and geometry use metadata outside the runtime source tree.
    if b.runner.committed(b.ROOT, b.runner.INVENTORY_PATH) != record['inventorySha256']:
        raise ValueError('native inventory changed')
    return record, frozen


def main():
    record, frozen = verify_frozen_inputs()  # No native Reader exists until this succeeds.
    script_hash = b.sha(__file__)
    root_path = b.G0 / 'archive-root.txt'
    b.runner.committed(b.ROOT, str(root_path.relative_to(b.ROOT)))
    root = Path(root_path.read_text().strip()).resolve()
    if Path.home() / '.cache/vitrea-archives' not in root.parents:
        raise ValueError('native cache must be the sealed fetched archive')
    # native.guarded installs W39's raw-tree audit deny before constructing Reader.
    native = b.load_module('baseline_v2_native', G2 / 'native.py')
    guarded_wave, reader = native.guarded(root, ('calibration', 'validation'))
    if reader.generation != record['inventorySha256']:
        raise ValueError('wrong native archive generation')
    if guarded_wave.scenes_sha != record['scenesSha256'] or guarded_wave.split_sha != record['splitSha256']:
        raise ValueError('reader metadata differs from frozen baseline')
    archive = b.load_module('baseline_v2_archive', b.W39 / 'w39_archive.py')
    summaries = {}
    for cell, capture in sorted(frozen['captures'].items()):
        role = b.wave.roles[cell.split('/', 1)[1]]
        if role not in ('calibration', 'validation'):
            raise PermissionError('baseline transfer never reads holdout')
        runs, states = archive.unbundle(reader.read(cell, 'crop'))
        admitted, counts = select_normal(runs)
        unpacked = {state: archive.unpack(states[state]) for state in {r['state'] for r in admitted}}
        data = b.transfer_projection(cell, Path(capture['png']),
                                     [unpacked[r['state']] for r in admitted])
        data.update(cell=cell, role=role,
                    nativeRuns=[{'run': r['run'], 'state': r['state'], 'protocol': r['protocol']}
                                for r in admitted], nativeAdmission=counts,
                    baselinePngSha256=capture['pngSha256'])
        profile, sid = cell.split('/', 1)
        path = b.HERE / 'transfer-v2' / profile / (sid + '.json.gz')
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as f:
            f.write(gzip.compress(b.stable(data).encode(), mtime=0))
        summaries[cell] = {'report': str(path.relative_to(b.ROOT)), 'sha256': b.sha(path),
                           'nativeAdmission': counts, 'deepMembers': len(data['deep']),
                           'exteriorBins': len(data['exterior']),
                           'interiorBins': len(data['interiorTransfer']),
                           'stripRows': len(data.get('stripTransfer', {}).get('rows', []))}
    if b.sha(__file__) != script_hash:
        raise ValueError('transfer script changed during native read')
    b.save(b.HERE / 'transfer-v2-inventory.json', {
        'recordedAt': b.stamp(), 'cells': summaries, 'sourceRevision': record['sourceRevision'],
        'originalSourceManifestSha256': hashlib.sha256(b.stable(record['sources']).encode()).hexdigest(),
        'instrumentHashes': {name: digest for name, digest in record['sources'].items()
                             if name.startswith(INSTRUMENT_ROOTS)},
        'transferScriptSha256': script_hash,
        'preparationSha256': b.sha(b.HERE / 'preparation.json'),
        'authoritySha256': b.sha(b.HERE / 'authority-v2.json'),
        'frozenBaselineSha256': b.sha(b.HERE / 'frozen-baseline.json'),
        'nativeGeneration': reader.generation, 'roles': ['calibration', 'validation'],
        'nativeReadProtocol': 'exactly seven admitted normal runs; long sentinels counted, not scored',
    })
    print('Transferred', len(summaries), 'frozen baseline cells through guarded native cal/val reads')


if __name__ == '__main__':
    main()
