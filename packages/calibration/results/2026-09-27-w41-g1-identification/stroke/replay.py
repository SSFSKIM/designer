"""W41 G1 stroke replay support. Import and synthetic checks open no native payload.

The sealed optimizer, domains, starts and budgets are unchanged. Only its forward
array evaluation is replaced by algebraically equivalent quadrature reuse. Native
fit admission belongs to fit_observations; validation is a read-only transfer.
"""
from collections import OrderedDict
import contextlib
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
from scipy.sparse import csr_matrix

HERE = Path(__file__).resolve().parent
G1 = HERE.parent
G0 = G1.parent / '2026-09-27-w41-g0-declaration'
sys.path.insert(0, str(G0 / 'instrument'))
import instrument as m
import shadow
import stroke_fit as f

DECLARATION_SHA = '850747c1f03781a6efe9b433bd4ce3bd6cf72b63c9befd8d5d98de9eadf7f759'
ENDPOINTS = f.ENDPOINTS


def verify_seal():
    closure = json.loads((G0 / 'closure.json').read_text())
    if hashlib.sha256((G0 / 'bounds-declaration.txt').read_bytes()).hexdigest() != DECLARATION_SHA:
        raise ValueError('sealed numerical declaration changed')
    for name, digest in closure['executionRecords'].items():
        if hashlib.sha256((G0 / name).read_bytes()).hexdigest() != digest:
            raise ValueError('sealed execution budget changed: ' + name)
    return closure


class CoverageKernel:
    """Share immutable geometry and held falloff across colours, never observations.

    Shadow alpha factors exactly into a held spatial falloff and the cell's
    CPU-resolved occlusion amplitude. Cached coverage still evaluates every one
    of the sealed midpoint samples; no population or quadrature is reduced.
    """
    def __init__(self, g, fall):
        self.g = g
        self.fall = np.asarray(fall, float)
        if self.fall.shape != g['d'].shape:
            raise ValueError('shadow falloff and geometry differ')
        self.cache = OrderedDict()

    def coverage(self, width, beta, gamma, css, rho):
        key = (width, beta, gamma, css, rho)
        if key not in self.cache:
            c = m.coverage(self.g, width, beta, gamma, css, rho)
            self.cache[key] = (c, c.mean(1), (c*self.fall).mean(1))
            if len(self.cache) > 2:
                self.cache.popitem(last=False)
        self.cache.move_to_end(key)
        return key, self.cache[key]


class CompactComposite:
    """Area-average Bshadow + c*(S(b)-Bshadow), before any bin reduction.

    Identical reconstructed RGB samples share only a material evaluation. The
    CSR operator sums their distinct sample weights per pixel. It does not merge
    native observations, bins, repeats or cells. Uniform backdrops use the same
    expression with one material vector and scalar coverage moments.
    """
    def __init__(self, g, b, fall, kernel=None):
        self.kernel = kernel or CoverageKernel(g, fall)
        b = np.asarray(b, float)
        if b.shape != (*g['d'].shape, 3):
            raise ValueError('RGB backdrop and quadrature differ')
        self.n, self.k = g['d'].shape
        self.mean_b = b.mean(1)
        self.mean_bfall = (b * self.kernel.fall[..., None]).mean(1)
        self.uniform = bool(np.all(b == b[0, 0]))
        if self.uniform:
            self.colours = b[0, :1].copy()
            self.ids = None
        else:
            self.colours, ids = np.unique(b.reshape(-1, 3), axis=0, return_inverse=True)
            self.ids = ids.astype(np.int32).reshape(self.n, self.k)
        self.cache = OrderedDict()
        self.operator_builds = 0

    def operator(self, key, c, mean_c, mean_cfall):
        if key not in self.cache:
            if self.uniform:
                values = (mean_c[:, None], mean_c[:, None]*self.colours,
                          mean_cfall[:, None]*self.colours)
            else:
                pixels = np.repeat(np.arange(self.n), self.k)
                weights = csr_matrix((c.ravel()/self.k, (pixels, self.ids.ravel())),
                                     shape=(self.n, len(self.colours)))
                cf = csr_matrix(((c*self.kernel.fall).ravel()/self.k,
                                 (pixels, self.ids.ravel())),
                                shape=(self.n, len(self.colours)))
                values = (weights, weights @ self.colours, cf @ self.colours)
            self.cache[key] = values
            self.operator_builds += 1
            if len(self.cache) > 2:
                self.cache.popitem(last=False)
        self.cache.move_to_end(key)
        return self.cache[key]

    def predict(self, q, endpoint, amplitude, family, css=False, curvature=False):
        width, beta, gamma, colour = f.unpack(q, family, endpoint)
        rho = float(q[-1]) if curvature else None
        key, (c, mean_c, mean_cfall) = self.kernel.coverage(width, beta, gamma, css, rho)
        weights, cb, cbfall = self.operator(key, c, mean_c, mean_cfall)
        material = m.material(self.colours, family, colour, dark=endpoint >= 2)
        painted = weights*material if self.uniform else weights @ material
        return self.mean_b - amplitude*self.mean_bfall + painted - cb + amplitude*cbfall


def required_bins(geo, member):
    bins, labels = m.readers.edge_bins(geo, member, inner_css=0, outer_css=4)
    bins = [row for row in bins if row['shell'] is not None]
    # Outer rows precede all boundary diagnostics in the inherited reader.
    admitted = np.array([row['pixels'] >= 4 for row in bins])
    selected = (labels >= 0) & (labels < len(bins))
    selected[selected] &= admitted[labels[selected]]
    return bins, labels, selected


def compact_predict(q, observation, family, css_width=False, curvature=False):
    return observation['compact'].predict(q, observation['endpoint'], observation['amplitude'],
                                          family, css_width, curvature)


@contextlib.contextmanager
def compact_forward():
    original = f.predict
    f.predict = compact_predict
    try:
        yield
    finally:
        f.predict = original


def fit_observations(observations, family, css_width=False, curvature=False):
    if not observations or any(o.get('role') != 'calibration' for o in observations):
        raise PermissionError('coefficients may use calibration observations only')
    verify_seal()
    with compact_forward():
        return f.fit_local(observations, family, css_width, curvature)


def guarded_reader(roles=('calibration', 'validation')):
    """Only called by an explicitly authorized native replay, never by preparation."""
    if not set(roles) <= {'calibration', 'validation'}:
        raise PermissionError('this replay never opens holdout')
    sys.path.insert(0, str(m.G2))
    import native
    root = Path((G1 / 'archive-root.txt').read_text().strip())
    # Fetch's verified cache is the sole root; the inherited guard denies the
    # entire raw tree, not just its run/ and archive/ children.
    expected = Path.home() / '.cache/vitrea-archives'
    if expected not in root.resolve().parents:
        raise ValueError('native replay requires the recorded fetched archive cache')
    wave, reader = native.guarded(root, tuple(roles))
    pins = json.loads((G0 / 'pins.json').read_text())
    if reader.generation != pins['archive']['inventorySha256']:
        raise ValueError('archive inventory differs from the sealed declaration')
    return native, wave, reader


def shadow_amplitude(shape, material, luminance):
    return 1-(1-shadow.occlusion(min(shape.size), material, luminance))**(1/2.4)


def held_falloff(g, shape, material):
    """The sealed shifted-path law with its scalar amplitude factored out."""
    params = material['outerShadow']
    if params['liftAmplitude'] != 0:
        raise ValueError('held macOS27 shadow expects zero lift')
    scale = g['scale']
    points = g['q'].reshape(-1, 2).copy()
    points[:, 1] -= params['offsetPx']*scale
    if shape.circular:
        distance = m.readers.I.stadium(points[:, 0], points[:, 1], shape.rect(scale),
                                       min(shape.size)/2*scale)[0]
    else:
        distance = m.readers._path_field(points, shape, scale, (0, 0))[0]
    d = distance/scale-params['spreadPx']
    x = -d/max(shadow.sigma(min(shape.size), params), 1e-4)
    fall = .5*(1+np.tanh(np.clip(.7978845608028654*(x+.044715*x*x*x), -20, 20)))
    return fall.reshape(g['d'].shape)


class CompoundComposite:
    """One cell can contain several members; their cell objective mass stays one."""
    def __init__(self, parts):
        self.parts = parts

    def predict(self, q, endpoint, amplitude, family, css=False, curvature=False):
        return np.concatenate([part.predict(q, endpoint, a, family, css, curvature)
                               for part, a in zip(self.parts, amplitude)])


class Preparation:
    def __init__(self):
        self.materials = shadow.materials()
        self.geometries = {}
        self.kernels = {}
        self.interior_counts = {}

    def geometry_samples(self, shape, scale, xy, order=16):
        key = (shape, scale, order, hashlib.sha256(xy.tobytes()).hexdigest())
        if key not in self.geometries:
            self.geometries[key] = m.samples(shape, xy, scale, order)
        return key, self.geometries[key]

    def kernel(self, key, g, shape, endpoint):
        name = ENDPOINTS[endpoint]
        # Inactive amplitude is identically zero; its falloff never contributes.
        shadow_key = name if endpoint in (0, 2) else 'inactive'
        full = (key, shadow_key)
        if full not in self.kernels:
            fall = held_falloff(g, shape, self.materials[name]) if endpoint in (0, 2) \
                else np.zeros_like(g['d'])
            self.kernels[full] = CoverageKernel(g, fall)
        return self.kernels[full]

    def prepare(self, cell, role, payloads, state_membership, background):
        """All seven admitted states supplied by the guarded reader, one cell.

        A varying reference or attested geometry would need a declared frozen
        predictor convention, so it is refused rather than silently averaged.
        Native RGB repeats themselves remain separate and need not be identical.
        """
        if role not in ('calibration', 'validation') or len(payloads) != 7:
            raise PermissionError('seven admitted calibration/validation states required')
        first = payloads[0]
        for other in payloads[1:]:
            if any(other[k] != first[k] for k in ('component', 'scale', 'scheme', 'pose')):
                raise ValueError('attested geometry/endpoint varies across repeats')
            if not np.array_equal(other['noGlass'], first['noGlass']):
                raise ValueError('reference varies across repeats; frozen convention needs ruling')
        scale = first['scale']
        pose = 'inactive' if first['pose'] == 'inactive' else 'active'
        endpoint = ENDPOINTS.index(first['scheme']+'-'+pose)
        material = self.materials[ENDPOINTS[endpoint]]
        shapes = m.readers.shapes_of(first['component'])
        geo = m.readers.geometry(first['rgb'].shape[:2], shapes, scale)
        reference = first['noGlass'].copy()
        luminance = float(m.body.decode(reference.mean(axis=(0, 1))/255) @ m.body.W)
        compacts, amplitudes, targets, repeats, ids, parts = [], [], [], [], [], []
        offset = 0
        for member, shape in enumerate(shapes):
            bins, labels, mask = required_bins(geo, member)
            yy, xx = np.nonzero(mask)
            xy = np.c_[xx, yy]
            key, g = self.geometry_samples(shape, scale, xy)
            kernel = self.kernel(key, g, shape, endpoint)
            b = m.bilinear(reference, g['q'])
            compact = CompactComposite(g, b, kernel.fall, kernel)
            amplitude = shadow_amplitude(shape, material, luminance)
            if endpoint in (1, 3) and amplitude != 0:
                raise ValueError('receded held shadow must be exactly zero')
            rgb = np.array([p['rgb'][mask] for p in payloads])
            compacts.append(compact); amplitudes.append(amplitude)
            targets.append(np.median(rgb, axis=0)); repeats.append(rgb)
            ids.append(labels[mask]+offset)
            parts.append(dict(member=member, shape=shape, xy=xy, bins=bins,
                binids=labels[mask]+offset, offset=offset, length=len(xy),
                pixelOffset=sum(len(t) for t in targets[:-1]),
                compact=compact, amplitude=amplitude, reference=reference,
                interior=interior_witness(geo, member, payloads, self, shape),
                boundary=boundary_diagnostic(geo, member, payloads)))
            offset += len(bins)
        return dict(cell=cell, role=role, endpoint=endpoint, scale=scale,
                    background=background, stateMembership=state_membership,
                    compact=CompoundComposite(compacts), amplitude=amplitudes,
                    target=np.concatenate(targets), runs=np.concatenate(repeats, axis=1),
                    binids=np.concatenate(ids), parts=parts, groupLuminance=luminance)


def interior_witness(geo, member, payloads, preparation, shape):
    rows = []
    shells = m.readers._shell(geo)
    for shell in (-1, -2, -3):
        mask = (geo.member == member) & geo.whole & (shells == shell)
        yy, xx = np.nonzero(mask)
        # All samples inside at the largest admitted reach prove zero for every
        # declared narrower width, angular factor and nominal curvature value.
        xy = np.c_[xx, yy]
        key = (shape, geo.scale, hashlib.sha256(xy.tobytes()).hexdigest())
        if key not in preparation.interior_counts:
            g = m.samples(shape, xy, geo.scale)
            preparation.interior_counts[key] = int((g['d'] > 0).sum())
        outside_samples = preparation.interior_counts[key]
        rgb = np.array([p['rgb'][mask] for p in payloads])
        rows.append(dict(shell=shell, pixels=len(xx), outsideSubpixels=outside_samples,
                         zeroStrokeWitness=outside_samples == 0,
                         nativeRunMeanRGB=rgb.mean(1).tolist() if len(xx) else None,
                         qualification='support witness only; no body accuracy assertion'))
    return rows


def boundary_diagnostic(geo, member, payloads):
    mask = (geo.member == member) & ~geo.whole & ~geo.outside & (abs(geo.d) < 2)
    rows = []
    for angle in range(16):
        at = mask & (geo.angle == angle)
        rgb = np.array([p['rgb'][at] for p in payloads])
        rows.append(dict(angle=angle, pixels=int(at.sum()),
                         nativeRunMeanRGB=rgb.mean(1).tolist() if at.any() else None,
                         status='DIAGNOSTIC', usedForFit=False, usedForSurvival=False))
    return rows


def load_role(preparation, role, emit=lambda row: None):
    """Admission precedes every read; validation never enters fit_observations."""
    native, wave, reader = guarded_reader((role,))
    observations = []
    for (cell, kind), entry in sorted(reader.entries.items()):
        sid = cell.split('/', 1)[1]
        if kind != 'crop' or sid not in reader.allowed or not entry['admitted']:
            continue
        if native.wave.native_only(wave.component(sid)):
            continue
        runs, states = native.archive.unbundle(reader.read(cell, 'crop'))
        runs = [run for run in runs if run['admitted'] and run['protocol'] == 'normal']
        if len(runs) != 7:
            raise ValueError('expected all seven normal admitted repeats: '+cell)
        decoded = {s: native.archive.unpack(states[s]) for s in {r['state'] for r in runs}}
        observation = preparation.prepare(cell, role, [decoded[r['state']] for r in runs],
            [r['state'] for r in runs], wave.scenes[sid]['background'])
        observations.append(observation)
        emit(dict(cell=cell, role=role, pixels=len(observation['target']),
                  members=len(observation['parts']), payloadSha256=entry['sha256']))
    return observations
