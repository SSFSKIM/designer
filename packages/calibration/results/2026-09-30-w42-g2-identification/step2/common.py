"""W42 G2 step 2: what every identification script shares (reading-plan.md is the governing note).

- `verify()` of the pins at import; the raw sitting root denied by the archive module's audit hook;
- the archive of record, fetched from the verified copy by digest and re-checked against its inventory, read
  through the wave's guarded Reader for the roles calibration and validation only;
- the observed image of a cell (the plurality frame of its seven normal runs), cached outside the repository;
- native T per endpoint and channel (the addendum's executable form);
- the instrument's cells with Apple's image and a per-channel T attached; a per-channel Problem; the region
  statistics; W41 G1's score (X31 statuses, X21 rails); the bar per statistic from G1's bar.json.
"""
import gzip
import hashlib
import importlib.util
import io
import json
import os
import sys
from collections import Counter
from pathlib import Path

os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('VECLIB_MAXIMUM_THREADS', '1')

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import pins as P  # noqa: E402

PINS = P.verify()
DECL = P.DECL
INSTR = DECL / 'instrument'
sys.path.insert(0, str(INSTR))
sys.path.insert(0, str(P.EVID / 'implementation-design'))
import bed as IB  # noqa: E402
import fitting as Fi  # noqa: E402
import forward as F  # noqa: E402
import geometry as G  # noqa: E402
import proof_common as PC  # noqa: E402
import regions as R  # noqa: E402
import native_t as NT  # noqa: E402

SCRATCH = Path(os.environ.get('W42_STEP2_SCRATCH', Path.home() / 'vitrea-w42' / 'g2-ident-scratch'))
OBS = SCRATCH / 'observed'
EPS = ('light-rest', 'light-inactive', 'dark-rest', 'dark-inactive')
EP_NAME = {'light-rest': 'light active', 'light-inactive': 'light receded', 'dark-rest': 'dark active',
           'dark-inactive': 'dark receded'}
W709 = G.W709


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


_ARCHIVE = None


def archive():
    global _ARCHIVE
    if _ARCHIVE is None:
        _ARCHIVE = _module('w42_archive_step2', DECL / 'bed' / 'sitting' / 'w42_archive.py')
        _ARCHIVE.deny(P.RAW_ROOT)
    return _ARCHIVE


def profile(ep, scale):
    scheme = ep.split('-')[0]
    return f'apple-macos-27.0-{scale}x-{scheme}-standard-glass0.5'


def sid(cid, ep):
    return f'{cid}__{"rest" if ep.endswith("rest") else "inactive"}'


def open_reader():
    """The archive root (digest-verified, tree-checked) and the guarded Reader for calibration + validation."""
    a = archive()
    A = PINS['archive']
    root = a.fetch(A['tag'], A['asset'], A['sha256'], repo=A['repo'], cache=Path(A['verifiedCopy']),
                   download=lambda *x: (_ for _ in ()).throw(RuntimeError('no download: the verified copy only')))
    wave = a.wave_module().default_wave()
    reader = wave.reader(root, roles=('calibration', 'validation'))
    if reader.generation != A['inventorySha256']:
        raise SystemExit('archive inventory is not the pinned generation')
    return a, wave, reader


def _decode(raw):
    from PIL import Image
    with Image.open(io.BytesIO(raw)) as im:
        return np.asarray(im.convert('RGB'), dtype=np.uint8)


def extract_all():
    """Write the plurality frame of every calibration / validation cell to SCRATCH/observed (outside git), and
    an index with every frame's SHA-256, the run membership of each state and the plurality's count."""
    a, wave, reader = open_reader()
    OBS.mkdir(parents=True, exist_ok=True)
    cells = sorted({r['cell'] for r in reader.report_inventory() if r['kind'] == 'states'
                    and r['cell'].split('/', 1)[1] in reader.allowed})
    index = {}
    for cell in cells:
        prof, s = cell.split('/', 1)
        comp = wave.spec['components'][wave.scenes[s]['component']]
        if comp.get('kind') == 'none':
            continue
        header, blobs = a.unbundle(reader.read(cell, 'states'))
        runs = [r for r in header['runs'] if r['protocol'] == 'normal']
        count = Counter(r['frame'] for r in runs)
        top = max(count.values())
        frame = next(r['frame'] for r in sorted(runs, key=lambda r: r['run']) if count[r['frame']] == top)
        img = _decode(blobs[frame])
        out = OBS / prof / f'{s}.npy'
        out.parent.mkdir(parents=True, exist_ok=True)
        np.save(out, img)
        index[cell] = dict(role=wave.roles[s], frame=frame, plurality=top, runs=len(runs),
                           states={k: sorted(r['run'] for r in runs if r['frame'] == k) for k in count},
                           shape=list(img.shape), npySha256=hashlib.sha256(out.read_bytes()).hexdigest())
    (OBS / 'index.json').write_text(json.dumps(dict(generation=reader.generation, archive=PINS['archive']['sha256'],
                                                    cells=index), indent=1, sort_keys=True) + '\n')
    return index


_INDEX = None


def index():
    global _INDEX
    if _INDEX is None:
        _INDEX = json.loads((OBS / 'index.json').read_text())
        if _INDEX['generation'] != PINS['archive']['inventorySha256']:
            raise SystemExit('observed cache is not the pinned generation')
    return _INDEX


def observed(ep, scale, cid):
    cell = f'{profile(ep, scale)}/{sid(cid, ep)}'
    row = index()['cells'][cell]
    if row['role'] not in ('calibration', 'validation'):
        raise PermissionError(cell)
    path = OBS / profile(ep, scale) / f'{sid(cid, ep)}.npy'
    if hashlib.sha256(path.read_bytes()).hexdigest() != row['npySha256']:
        raise SystemExit('observed cache altered: ' + cell)
    return np.load(path).astype(np.float64)


# ------------------------------------------------------------------------------------------------ the bar

_BAR = None


def bars():
    """{(profile/sid, kernel, statistic|channel): bar} from G1's bar.json (normal protocol)."""
    global _BAR
    if _BAR is None:
        raw = gzip.decompress((P.G1 / 'bar' / 'bar.json.gz').read_bytes())
        if hashlib.sha256(raw).hexdigest() != P.BAR_JSON_SHA:
            raise SystemExit('bar.json moved')
        _BAR = {}
        for r in json.loads(raw)['rows']:
            if r.get('status') == 'measured' and r['protocol'] == 'normal':
                for name, v in r['statistics'].items():
                    _BAR[(r['cell'], r['kernel'], name)] = v['bar']
    return _BAR


def bar_of(cell, name):
    return bars().get((f'{profile(cell.ep, cell.scale)}/{sid(cell.bed_id, cell.ep)}', cell.kernel, name), 0.5)


# ------------------------------------------------------------------------------------------------ native T

STRATUM_OF = {'capsule-button': 64, 'rrect-80': 80, 'rrect-md': 96, 'rrect-ml': 128, 'rrect-lg': 160}


class ChannelT:
    """One channel of native T at a fixed span: the instrument's scalar T interface (M codes -> y codes)."""

    def __init__(self, nt, span, name):
        self.nt, self.span, self.name = nt, span, name
        self.trust_below = None
        self._row = nt._between(span)

    def __call__(self, M):
        return np.interp(M, NT.GRID_LEVELS, self._row)


class NativeTC:
    """Native T for one endpoint, per channel: three NT.NativeT (or the measured ordinates as given)."""

    def __init__(self, ordinates, scheme):
        # ordinates: {channel: {stratum: {level: code}}}
        self.scheme = scheme
        self.ordinates = ordinates
        self.nonmonotone = []
        self.nt = {}
        for c in 'RGB':
            for s, pts in ordinates[c].items():
                ys = [pts[x] for x in sorted(pts)]
                if any(b < a for a, b in zip(ys, ys[1:])):
                    self.nonmonotone.append(dict(channel=c, stratum=s, ordinates=[(x, pts[x]) for x in sorted(pts)]))
            self.nt[c] = _NativeTUnchecked(ordinates[c], scheme)

    def channels(self, span):
        return [ChannelT(self.nt[c], span, f'native:{self.scheme}:{c}@{span}') for c in 'RGB']

    def table(self, c):
        return self.nt[c].table()


class _NativeTUnchecked(NT.NativeT):
    """The addendum's rule exactly, except that decreasing MEASURED ordinates are recorded by NativeTC rather
    than raised: the finding goes to the parent and nothing is repaired (reading-plan.md item 4)."""

    def __init__(self, ordinates, scheme):
        orig = NT._check_monotone
        NT._check_monotone = lambda *a: None
        try:
            super().__init__(ordinates, scheme)
        finally:
            NT._check_monotone = orig


def load_native_t():
    return json.loads((HERE / 'native-t' / 'ordinates.json').read_text())


def native_tc(ep, ords=None):
    ords = ords or load_native_t()
    o = ords['endpoints'][ep]['ordinates']
    conv = {c: {int(s): {int(L): v for L, v in row.items()} for s, row in o[c].items()} for c in 'RGB'}
    return NativeTC(conv, ep.split('-')[0])


# ------------------------------------------------------------------------------------------------ cells

def cells(ep, scale, roles, letters=None, kernel='n', ntc=None, rgb=None):
    """The instrument's cells (bed.cells) with Apple's plurality frame and the per-channel native T attached."""
    ntc = ntc or native_tc(ep)
    out = IB.cells(ep, scale, letters=letters, roles=roles, kernel=kernel, rgb=bool(rgb))
    for c in out:
        img = observed(ep, scale, c.bed_id)
        if img.shape[:2] != c.d.shape:
            raise SystemExit(f'{c.id}: capture {img.shape} is not the cell canvas {c.d.shape}')
        y = np.full(img.shape, np.nan, np.float32)
        y[c.mask] = img[c.mask]
        c.y = y
        c.Tc = ntc.channels(c.span)
        c.T = c.Tc[1]
        c.kernel = kernel
    return out


# ------------------------------------------------------------------------------------------------ rendering

def compose_rgb(c, fam, mp, lam):
    """Per-channel output (n, 3): compose once per channel with that channel's scalar T."""
    out = []
    for i, Tc in enumerate(c.Tc):
        y = F.compose(c, fam, mp, lam, T=Tc)
        out.append(y if y.ndim == 1 else y[:, i])
    return np.stack(out, -1)


def render_rgb(c, fam, p):
    return compose_rgb(c, fam, F.maps(c, fam, F.expand(fam, p)), p['lam'])


class ProblemRGB(Fi.Problem):
    """fitting.Problem with the per-channel native T (reading-plan.md item 3); everything else is the
    instrument's: equal cell weight, lam inner by golden section, outer Powell / bounded Brent (LOCAL)."""

    def _cell_mse(self, c, mp, obs, lam, x):
        y, ok = obs
        if self.fam.order == 'blurlast':
            p = self.params_for(x, c)
            p['lam'] = lam
            pred = np.stack([F.render(c, self.fam, p, T=Tc) for Tc in c.Tc], -1)
            if pred.ndim == 3:
                pred = np.stack([pred[:, i, i] for i in range(3)], -1)
        else:
            pred = compose_rgb(c, self.fam, mp, lam)
        e = (pred - y)[ok]
        return float(np.mean(e ** 2))

    def predictions(self, x, lams):
        out = []
        for c in self.cells:
            p = self.params_for(x, c)
            p['lam'] = lams[c.ep]
            if self.fam.order == 'blurlast':
                pr = np.stack([F.render(c, self.fam, p, T=Tc) for Tc in c.Tc], -1)
                out.append(np.stack([pr[:, i, i] for i in range(3)], -1) if pr.ndim == 3 else pr)
            else:
                out.append(render_rgb(c, self.fam, p))
        return out


# ------------------------------------------------------------------------------------------------ statistics

def stats(c, values):
    """Region statistics {name|channel: median} of per-pixel values on c.mask (n, 3)."""
    return R.stats_from_masked(c, values, R.populations(c))


def native_stats(c):
    if getattr(c, '_native_stats', None) is None:
        c._native_stats = R.statistics(c, c.y, R.populations(c))
    return c._native_stats


def score_cell(c, pred):
    """W41 G1's score (body41.score) per region statistic and channel: measured within max(1, bar); a rail
    (native <= 5 or >= 250) satisfied one-sidedly, or UNMEASURED and failed."""
    sp, sn = stats(c, pred), native_stats(c)
    rows = []
    for k, nv in sn.items():
        pv = sp[k]
        bound = max(1.0, bar_of(c, k))
        if 5 < nv < 250:
            err = pv - nv
            rows.append((k, nv, pv, err, bound, 'measured', abs(err) > bound))
        else:
            deficit = max(pv - 5, 0) if nv <= 5 else max(250 - pv, 0)
            st = 'censored-bound-satisfied' if deficit == 0 else 'UNMEASURED'
            rows.append((k, nv, pv, float(deficit), bound, st, deficit > 0))
    return rows


def minimax_objective_terms(c, pred):
    """|err| for measured statistics, the rail deficit for censored ones (reading-plan.md item 5)."""
    return [abs(r[3]) if r[5] == 'measured' else r[3] for r in score_cell(c, pred)]


def summarize(cells_, preds):
    """Survival summary over cells: failures, worst measured miss, statuses; per-cell rms."""
    fails, worst, where, statuses, per_cell = 0, 0.0, None, Counter(), {}
    fail_list = []
    unmeasured_cells = []
    for c, pr in zip(cells_, preds):
        rows = score_cell(c, pr)
        if not rows:
            unmeasured_cells.append(c.id)
        for k, nv, pv, err, bound, st, failed in rows:
            statuses[st] += 1
            if failed:
                fails += 1
                fail_list.append((c.id, k, nv, round(pv, 3), round(err, 3), st))
            if st == 'measured' and abs(err) > worst:
                worst, where = abs(err), f'{c.id}:{k}'
        y = c.y[c.mask]
        per_cell[c.id] = float(np.sqrt(np.nanmean((pr - y) ** 2)))
    return dict(failures=fails, worstMeasured=worst, worstAt=where, statuses=dict(statuses),
                cellsWithNoStatistic=unmeasured_cells, perCellRms=per_cell,
                pooledRms=float(np.sqrt(np.mean([v ** 2 for v in per_cell.values()]))) if per_cell else None,
                failed=fail_list)


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=1, sort_keys=True, default=float) + '\n')
