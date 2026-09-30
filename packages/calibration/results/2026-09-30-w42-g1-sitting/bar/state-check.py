#!/usr/bin/env python3.12
"""W42 G1: a check on the repeat bar (state-check.py > state-check.json), read from the downloaded archive.

For every measured cell whose runs produced more than one frame state, how far apart those states
are in pixels, and the largest bar over the cell's statistics (which bar.json.gz records as 0.5
everywhere). Plus one uniform cell's deep red median per run, to show the statistics are code values.
"""
import gzip, importlib.util, json, sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('rb', HERE / 'report-bars.py'); rb = importlib.util.module_from_spec(spec); spec.loader.exec_module(rb)
A = rb.module('w42_archive_chk', rb.SITTING / 'w42_archive.py')
root = Path(sys.argv[1])
wave = A.wave_module().default_wave(); reader = wave.reader(root, roles=rb.ROLES)
bar = json.loads(gzip.decompress((HERE / 'bar.json.gz').read_bytes()))
out = []
for r in (r for r in bar['rows'] if r.get('status') == 'measured' and r['distinctStates'] > 1):
    header, blobs = A.unbundle(reader.read(r['cell'], 'states'))
    frames = [x['frame'] for x in header['runs'] if x['protocol'] == r['protocol']]
    imgs = {d: rb.decode(blobs[d]) for d in set(frames)}
    ds = sorted(imgs)
    pairs = [(a, b) for i, a in enumerate(ds) for b in ds[i + 1:]]
    out.append(dict(cell=r['cell'], kernel=r['kernel'], protocol=r['protocol'], states=len(ds),
                    runsPerState=sorted((frames.count(d) for d in ds), reverse=True),
                    maxPixelCodeDiff=max(float(np.abs(imgs[a] - imgs[b]).max()) for a, b in pairs),
                    differingPixels=max(int((np.abs(imgs[a] - imgs[b]).max(-1) > 0).sum()) for a, b in pairs),
                    statistics=len(r['statistics']), maxBar=max(v['bar'] for v in r['statistics'].values())))
sample = next(r for r in bar['rows'] if r.get('status') == 'measured' and r['kernel'] == 'n' and 'deep|R' in r['statistics'])
h, b = A.unbundle(reader.read(sample['cell'], 'states'))
scale, scheme, pose = rb.endpoint(*sample['cell'].split('/', 1))
sc = wave.scenes[sample['cell'].split('/', 1)[1]]
c = rb.F.Cell('check', sc['background'], sc['component'], scale, scheme, pose, rgb=True, kernel='n')
vals = [rb.R.statistics(c, rb.decode(b[x['frame']]))['deep|R'] for x in h['runs'] if x['protocol'] == 'normal']
print(json.dumps(dict(multiStateRows=out, sample=dict(cell=sample['cell'], deepRedMedianPerRun=vals,
                                                      deepMaskPixels=int(c.mask.sum()))), indent=1))
