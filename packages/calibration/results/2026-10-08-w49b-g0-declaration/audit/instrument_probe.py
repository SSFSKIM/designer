"""Exercise W49b's planner and transitive Python band instrument without opening any PNG."""
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
TOOLS = HERE.parent / 'tools'


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


reader = load('w49b_audit_reader', TOOLS / 'read.py')
C, L = reader.C, reader.L
registry = C.load_registry()
import json
batch = C.validate_batch(json.loads((HERE.parent / 'batches/identification.json').read_text()))
for point in batch['points']:
    for scale in point['scales']:
        L.plan_run(registry, point, scale)
sys.path.insert(0, str(C.CAL / 'results/2026-10-03-w44-g1-refit/cuts'))
import readings as R
import numpy as np

# read_run's delayed imports and all its geometry/luminance/band calls are exercised on
# synthetic RGB. No fixture, background, web capture, referee or holdout pixel is decoded.
canvas = {'width': 32, 'height': 24}
component = {'kind': 'rrect', 'size': [24, 16], 'radius': 4}
for scale in (1, 2):
    shape = (24 * scale, 32 * scale)
    image = np.indices(shape).sum(axis=0).astype(np.uint8)
    image = np.repeat(image[..., None], 3, axis=2) + np.uint8(80)
    background = np.zeros_like(image)
    silhouette = R.P.native_interior(image, background, component, canvas, scale)
    distance = R.P.signed_distance(component, canvas, scale, shape)
    geometry = {'scale': scale, 'silhouette': silhouette, 'deep': distance <= -8 * scale,
                'eroded': R.distance_transform_edt(silhouette) > 4 * scale}
    R.P.luminance(image)[silhouette].std()
    R.read(f'apple-macos-27.0-{scale}x-dark-standard-glass0.25', 'synthetic',
           image, image, geometry)
