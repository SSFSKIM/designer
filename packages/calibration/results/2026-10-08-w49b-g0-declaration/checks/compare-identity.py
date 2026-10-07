"""Compare raw raster hashes from the identical recorder on pre/post operator trees."""
import hashlib
import json
from pathlib import Path
import sys

before, after, output = map(Path, sys.argv[1:])
a, b = (json.loads(p.read_text()) for p in (before, after))
if set(a) != set(b):
    raise SystemExit('Identity recorder membership changed')
changed = [key for key in a if a[key] != b[key]]
if changed:
    raise SystemExit(f'Identity bytes changed: {changed}')
goldens = [key for key in a if key.startswith('golden/')]
endpoints = [key for key in a if not key.startswith('golden/')]
if len(goldens) != 13 or len(endpoints) != 30:
    raise SystemExit('Expected thirteen golden scene rasters and ten endpoints at three DPRs')
record = dict(status='byte-identical', beforeHead='fee4e8f3b',
    beforeSha256=hashlib.sha256(before.read_bytes()).hexdigest(),
    afterSha256=hashlib.sha256(after.read_bytes()).hexdigest(),
    goldenSceneRasters=len(goldens), shippedEndpointRasters=len(endpoints),
    endpointDprs=[1, 1.5, 2], rasterHashes=a,
    scope='Raw renderer rasters; the separate golden suite has34tests, not34image files. No golden regenerated.')
output.write_text(json.dumps(record, indent=2) + '\n')
print('43 raw raster hashes byte-identical:13golden scenes and10endpoints at1x/1.5x/2x')
