"""Additive censor-aware edge readout. No optimizer or native/archive reader.

Replay: python replay.py --out attempt-1
Verify without writing: python replay.py --verify attempt-1
The sealed cache and fifteen pinned artifacts are the complete input boundary.
The original selected coefficients, tolerances and absolute residuals stay intact.
JSONL records contain median followed by each of seven normal runs, including
repeated identical states. UNMEASURED channels retain ordinary residuals only as
legacy diagnostics. Bounds use [0,5] and [250,255], not point targets at the rails.
"""
import argparse
from collections import defaultdict
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import sys
sys.dont_write_bytecode = True
import numpy as np

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
CACHE = Path('/tmp/w39-g2-edge-cache-attempt-2')
ENDPOINTS = ('light-active', 'light-inactive', 'dark-active', 'dark-inactive')
METHODS = ('leastSquares', 'minimax')
KEYS = ('member', 'part', 'side', 'bin', 'shell')
W = np.array([.2126, .7152, .0722])


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def checked_inputs(cache):
    pins = json.loads((HERE / 'input-pins.json').read_text())
    for name, digest in pins.items():
        assert sha((BASE / name).read_bytes()) == digest, name
    source = json.loads((BASE / 'edge/cache-seal.json').read_text())
    raw = (cache / 'seal.json').read_bytes()
    assert sha(raw) == source['sha256']
    seal = json.loads(raw)
    assert len(seal['files']) == source['files'] == 611
    assert len({r['file'] for r in seal['files']}) == 611
    for item in seal['files']:
        assert Path(item['file']).name == item['file']
        data = (cache / item['file']).read_bytes()
        assert len(data) == item['bytes'] and sha(data) == item['sha256'], item['file']
    manifest_bytes = (cache / 'manifest.json').read_bytes()
    manifest = json.loads(manifest_bytes)
    assert {r['role'] for r in manifest['records']} == {'calibration', 'validation'}
    for endpoint in ENDPOINTS:
        summary = json.loads((BASE / f'edge/{endpoint}-gn/summary.json').read_text())
        assert summary['cacheSealSha256'] == source['sha256']
        assert summary['cacheManifestSha256'] == sha(manifest_bytes)
        assert summary['inventorySha256'] == manifest['inventorySha256']
    return manifest, pins, source


def classify(native, prediction, labels, bins, tau):
    """Keep channel-local evidence even when another required channel is censored."""
    n = len(bins)
    counts = np.bincount(labels, minlength=n)
    def reduce(values):
        return np.stack([np.bincount(labels, weights=values[:, c], minlength=n)
                         for c in range(3)], axis=1)
    low = reduce(native <= 5).astype(int)
    high = reduce(native >= 250).astype(int)
    errors = reduce(abs(prediction - native)) / np.maximum(counts[:, None], 1)
    # Distance to the admissible scalar interval. Zero does not establish a pass.
    lower = np.where(native >= 250, 250, np.where(native <= 5, 0, native))
    upper = np.where(native <= 5, 5, np.where(native >= 250, 255, native))
    bound = reduce(np.maximum(lower - prediction, 0) + np.maximum(prediction - upper, 0))
    bound = bound / np.maximum(counts[:, None], 1)
    result = []
    for i, b in enumerate(bins):
        assert counts[i] == b['pixels']
        valid = (low[i] + high[i] == 0) & (counts[i] >= 4) & (b['status'] == 'measured')
        result.append(dict(
            channelStatus=['measured' if v else 'UNMEASURED' for v in valid],
            lowerCensoredCountsRGB=low[i].tolist(), upperCensoredCountsRGB=high[i].tolist(),
            uncensoredCountsRGB=(counts[i] - low[i] - high[i]).tolist(),
            measuredResidualRGB=[float(errors[i,c]) if valid[c] else None for c in range(3)],
            scalarBoundViolationRGB=bound[i].tolist() if counts[i] else None,
            failedChannels=np.flatnonzero(valid & (errors[i] > tau[i] + 1e-8)).tolist()))
    return result


def ordered_blocks(records, geometries, old):
    """Runner order, not legacy member labels, identifies each member's residuals."""
    offset = 0
    for r in records:
        bins = geometries[r['geometry']]['bins']
        block = old[offset:offset + len(bins)]
        assert len(block) == len(bins)
        for b, row in zip(bins, block):
            assert row['cell'] == r['cell']
            assert all(row[k] == b[k] for k in KEYS)
        yield r, bins, block
        offset += len(bins)
    assert offset == len(old)


class Summary:
    def __init__(self):
        self.groups = {}

    def add(self, row):
        for state_index, state in enumerate(row['states']):
            for background in ('all', row['sourceKind']):
                key = (row['endpoint'], row['scale'], row['role'], row['method'],
                       background, state_index)
                if key not in self.groups:
                    self.groups[key] = dict(bins=0, fullyMeasuredBins=0, partlyMeasuredBins=0,
                        unmeasuredBins=0, measuredChannels=0, unmeasuredChannels=0,
                        censoredBins=0, absentBins=0, underpopulatedBins=0, failingChannels=0,
                        failingBins=0, failingFullyMeasuredBins=0, failingCells=set(),
                        worstUncensored=None, worstAllChannelComparison=None,
                        worstOrdinaryAbsoluteDiagnostic=None)
                g = self.groups[key]
                g['bins'] += 1
                measured = [c for c, s in enumerate(state['channelStatus']) if s == 'measured']
                m = len(measured)
                g['fullyMeasuredBins' if m == 3 else 'partlyMeasuredBins' if m else 'unmeasuredBins'] += 1
                g['measuredChannels'] += m
                g['unmeasuredChannels'] += 3-m
                g['censoredBins'] += bool(sum(state['lowerCensoredCountsRGB']) + sum(state['upperCensoredCountsRGB']))
                g['absentBins'] += row['pixels'] == 0
                g['underpopulatedBins'] += 0 < row['pixels'] < 4
                failed = state['failedChannels']
                g['failingChannels'] += len(failed)
                g['failingBins'] += bool(failed)
                g['failingFullyMeasuredBins'] += bool(failed) and m == 3
                if failed:
                    g['failingCells'].add(row['cell'])
                witness = {k: row[k] for k in ('cell', 'member', 'part', 'side', 'bin', 'shell', 'sourceKind')}
                witness['measuredResidualRGB'] = state['measuredResidualRGB']
                witness['channelStatus'] = state['channelStatus']
                def take(field, channel, value):
                    if g[field] is None or value > g[field]['codes']:
                        g[field] = dict(**witness, channel=channel, codes=value,
                                        toleranceCodes=row['toleranceRGB'][channel])
                for c in measured:
                    take('worstUncensored', c, state['measuredResidualRGB'][c])
                if m == 3:
                    c = int(np.argmax(state['measuredResidualRGB']))
                    take('worstAllChannelComparison', c, state['measuredResidualRGB'][c])
                ordinary = row['legacyAbsoluteResidualRGB'][state_index]
                if ordinary is not None:
                    c = int(np.argmax(ordinary))
                    take('worstOrdinaryAbsoluteDiagnostic', c, ordinary[c])

    def rows(self):
        rows = []
        for key, values in sorted(self.groups.items()):
            out = dict(values)
            out['failingCells'] = len(values['failingCells'])
            rows.append(dict(zip(('endpoint','scale','role','method','sourceKind','stateIndex'), key), **out))
        return rows


class Output:
    def __init__(self, path, verify):
        self.path, self.verify = path, verify
        if not verify:
            path.mkdir(exist_ok=False)
        self.files = {}

    def records(self, name, rows, summary):
        digest = hashlib.sha256()
        count = 0
        if self.verify:
            stream = gzip.open(self.path / name, 'rb')
        else:
            raw = (self.path / name).open('xb')
            stream = gzip.GzipFile(filename='', mode='wb', fileobj=raw, mtime=0)
        try:
            for row in rows:
                line = (json.dumps(row, separators=(',', ':'), allow_nan=False) + '\n').encode()
                if self.verify:
                    assert stream.readline() == line, (name, count)
                else:
                    stream.write(line)
                digest.update(line)
                count += 1
                summary.add(row)
            if self.verify:
                assert stream.read() == b'', name
        finally:
            stream.close()
            if not self.verify:
                raw.close()
        self.files[name] = dict(rows=count, uncompressedSha256=digest.hexdigest())
        print(name, count, 'verified' if self.verify else 'written', flush=True)

    def document(self, name, value):
        raw = (json.dumps(value, indent=2, allow_nan=False) + '\n').encode()
        if self.verify:
            assert (self.path / name).read_bytes() == raw, name
        else:
            with (self.path / name).open('xb') as f:
                f.write(raw)


def load_npz(path):
    with np.load(path, allow_pickle=False) as z:
        return dict(z)


def corrected_rows(r, bins, old, data, geo, prediction, method):
    tau = np.maximum(1, data['bar'])
    inputs = [data['native'], *[data['states'][i] for i in data['stateix']]]
    assert len(inputs) == 8
    readings = [classify(native, prediction, geo['binids'], bins, tau) for native in inputs]
    counts = np.bincount(geo['binids'], minlength=len(bins))
    present = counts > 0
    absolute_rows = [[row['residualRGB'], *(row['repeatResidualRGB'] or [None]*7)] for row in old]
    # Check all old ordinary residuals in one vectorized reduction per state.
    for j, native in enumerate(inputs):
        error = abs(prediction - native)
        reduced = np.stack([np.bincount(geo['binids'], weights=error[:,c], minlength=len(bins))
                            for c in range(3)], axis=1) / np.maximum(counts[:,None], 1)
        expected = np.array([absolute_rows[i][j] for i in np.flatnonzero(present)])
        np.testing.assert_allclose(reduced[present], expected, rtol=0, atol=2e-10)
        assert all(absolute_rows[i][j] is None for i in np.flatnonzero(~present))
    np.testing.assert_allclose(tau, [row['toleranceRGB'] for row in old], rtol=0, atol=1e-12)
    for i, (b, legacy) in enumerate(zip(bins, old)):
        state_rows = [state[i] for state in readings]
        absolute = absolute_rows[i]
        yield dict(cell=r['cell'], member=r['member'], legacyMember=legacy['member'],
            endpoint=r['scheme'] + ('-active' if r['pose']=='rest' else '-inactive'),
            scale=r['scale'], role=r['role'], sourceKind='uniform' if r['backgroundKind']=='solid' else 'gradient',
            method=method, **{k:b[k] for k in ('part','side','bin','shell','pixels','depthCss')},
            geometryStatus=b['status'], toleranceRGB=legacy['toleranceRGB'],
            legacyAbsoluteResidualRGB=absolute, legacyFailedChannels=legacy['failedChannels'],
            stateHashes=r['stateHashes'], normalRunStateIndices=r['normalRunStateIndices'],
            states=state_rows)


def fit_rows(endpoint, method, manifest, cache, radial):
    scheme, pose = endpoint.split('-')
    pose = 'rest' if pose == 'active' else pose
    records = [r for r in manifest['records'] if r['scheme']==scheme and r['pose']==pose]
    directory = BASE / f'edge/{endpoint}-gn'
    summary = json.loads((directory / 'summary.json').read_text())
    best = summary['bestLeastSquares' if method=='leastSquares' else 'bestMinimax']
    q = np.array(best[method]['coefficients']).reshape(11, 4)
    old = json.loads(gzip.decompress((directory / (method+'-bins.json.gz')).read_bytes()))
    for r, bins, block in ordered_blocks(records, manifest['geometries'], old):
        data = load_npz(cache / (r['id']+'.npz'))
        geo = load_npz(cache / (r['geometry']+'.npz'))
        b = data['deep']/255
        y = b@W
        colour = np.column_stack((np.ones(3), np.full(3, y), b-y, y*(b-y)))
        base = np.where(geo['inside'][:,None], b, data['backdrop']/255)
        basis = radial(geo['t'], geo['ny'], best['widthCSS'], best['exponent'])
        prediction = np.clip(base + (basis @ q) @ colour.T, 0, 1)*255
        yield from corrected_rows(r, bins, block, data, geo, prediction, method)


def support_rows(manifest, cache):
    source = json.loads(gzip.decompress((BASE / 'edge/support.json.gz').read_bytes()))
    assert source['inventorySha256'] == manifest['inventorySha256']
    grouped = defaultdict(list)
    for row in source['rows']:
        grouped[(row['cell'], row['member'])].append(row)
    for r in manifest['records']:
        old = grouped.pop((r['cell'], r['member']), [])
        if not old:
            continue
        data = load_npz(cache / (r['id']+'.npz'))
        geo = load_npz(cache / (r['geometry']+'.npz'))
        bins = manifest['geometries'][r['geometry']]['bins']
        # The geometry's legacy member may be another sharing record's member.
        index = {tuple(b[k] for k in KEYS[1:]): i for i,b in enumerate(bins)}
        selected = [index[tuple(row[k] for k in KEYS[1:])] for row in old]
        remap = np.full(len(bins), -1, dtype=int)
        remap[selected] = np.arange(len(selected))
        keep = remap[geo['binids']] >= 0
        subset = dict(geo, binids=remap[geo['binids'][keep]])
        # All quadrature nodes lie outside every declared basis's support.
        assert np.all(geo['t'][keep] >= 12)
        data = dict(data, native=data['native'][keep], states=data['states'][:,keep], bar=data['bar'][selected])
        prediction = np.broadcast_to(data['deep'], data['native'].shape)
        for row in old:
            np.testing.assert_array_equal(row['bodyRGB'], data['deep'])
        yield from corrected_rows(r, [bins[i] for i in selected], old, data, subset, prediction, 'support')
    assert not grouped


def main():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--out', type=Path)
    mode.add_argument('--verify', type=Path)
    p.add_argument('--cache', type=Path, default=CACHE)
    args = p.parse_args()
    manifest, pins, source = checked_inputs(args.cache)
    spec = importlib.util.spec_from_file_location('sealed_basis', BASE/'edge/basis.py')
    basis = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(basis)
    output = Output(args.verify or args.out, args.verify is not None)
    summary = Summary()
    for endpoint in ENDPOINTS:
        for method in METHODS:
            output.records(f'{endpoint}-{method}.jsonl.gz',
                           fit_rows(endpoint, method, manifest, args.cache, basis.radial), summary)
    output.records('support.jsonl.gz', support_rows(manifest, args.cache), summary)
    rows = summary.rows()
    support = [r for r in rows if r['method']=='support' and r['role']=='calibration' and r['sourceKind']=='all']
    assert len(support) == 8*8
    assert all(r['failingChannels'] > 0 for r in support), 'uncensored support rejection must survive every repeat'
    output.document('summary.json', dict(
        schema='w39-edge-censor-correction-1',
        definitions=dict(states='index0 median; indices1..7 original normal-run order',
            admission='geometry measured AND population >=4 AND zero censored samples for that channel',
            censor='native <=5: [0,5]; native >=250: [250,255]; inclusive thresholds',
            allChannelComparison='maximum channel residual in a bin where all three channels are measured',
            scalarBoundViolation='mean distance to censor interval (point target for uncensored samples); diagnostic only',
            legacyAbsoluteResidual='original absolute residuals; diagnostic only when censored or geometry UNMEASURED',
            support='coefficient-independent: every cached quadrature node is at inward depth >=12 CSS px'),
        provenance=dict(inputs=pins, cacheSealSha256=source['sha256'], verifiedCacheFiles=611,
            inventorySha256=manifest['inventorySha256'], runnerSha256=sha(Path(__file__).read_bytes()),
            runtime=dict(python=platform.python_version(), numpy=np.__version__)),
        outputs=output.files, summary=rows))
    print('All8 calibration support strata fail on uncensored channels: median and all7 runs.', flush=True)


if __name__ == '__main__':
    main()
