#!/usr/bin/env python3.12
"""W39's archive of record: role-separated lossless repeat evidence, and its replay (§5.184).

Derived from W34 G0's `archive.py` (§5.174), which stays untouched. What
carries over: every admitted run is archived BEFORE plurality, one cell per
role directory, states de-duplicated by content, and the inventory publishes
only cells, kinds, paths, hashes and admission, so a producer may see holdout
while nothing it prints discloses a held statistic.

What changes, and why:

- A state stores FULL frames: the glass capture and every dependency the
  split names for it (the no-glass reference and the opaque control), uint8
  RGB in original coordinates, crop [0, 0, w, h]. At 320x280 a full frame
  costs little, and a full frame is the only crop that is complete for an
  estimator nobody has written yet. The control's own no-glass reference
  (`opaqueNoGlass`) is a separate frame with its own hash, because a borrowed
  control's background is not its dependent's. A held-out cell's borrowed calibration
  dependencies are copied into its own role directory, so reading one role
  never needs another.
- No registration is fitted or stored: W39's reader takes positions from the
  attested `frameOrigin` (X25), so the archived attestation IS the alignment
  input.
- Native-only cells (no-glass references, opaque controls) are archived as
  cells of their own too, so the archive holds every captured cell and not
  only those some glass cell happened to borrow; an opaque control carries its
  background's no-glass reference, which its coverage calibration reads.
- The pixel container is binary (a JSON header, a newline, raw bytes), not
  base64 inside JSON, and a cell's states are one gzip stream. Statistics are
  stored once per distinct state (they are a function of it) and gzipped: the
  reader's exhaustive per-run output is ~290 KB of JSON for a 2x glass cell.
"""
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np

PIXELS = ('rgb', 'noGlass', 'opaque', 'opaqueNoGlass')
SCHEMA = 'w39-archive-1'


def encode(value): return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
def sha(raw): return hashlib.sha256(raw).hexdigest()


def default_analyse():
    import w39_readers
    return w39_readers.analyse


def statistics(payload, analyse):
    """The reader's per-run statistics; native-only cells go through the same call.

    An opaque control is read as coverage against its background reference and a
    `none` reference as a raster (`w39_readers.analyse`), so "opaque coverage
    calibrated separately" (clause 7) is recorded per run like everything else.
    """
    return analyse(payload)


def pack(payload):
    """One state, losslessly: metadata as sorted JSON, then each frame's raw bytes."""
    meta = {k: v for k, v in payload.items() if k not in PIXELS}
    blobs, offset, layout = [], 0, {}
    for name in PIXELS:
        if payload.get(name) is None: continue
        array = np.ascontiguousarray(payload[name], dtype=np.uint8)
        if array.ndim != 3 or array.shape[2] != 3: raise ValueError('frames are HxWx3 uint8 RGB')
        raw = array.tobytes()
        layout[name] = dict(shape=list(array.shape), crop=[0, 0, array.shape[1], array.shape[0]],
                            offset=offset, length=len(raw), sha256=sha(raw))
        blobs.append(raw); offset += len(raw)
    return encode({**meta, 'pixels': layout}) + b'\n' + b''.join(blobs)


def unpack(raw):
    head, _, body = raw.partition(b'\n')
    value = json.loads(head)
    for name, spec in value.pop('pixels').items():
        chunk = body[spec['offset']:spec['offset'] + spec['length']]
        if len(chunk) != spec['length'] or sha(chunk) != spec['sha256']:
            raise ValueError('archived frame is truncated or altered: ' + name)
        value[name] = np.frombuffer(chunk, dtype=np.uint8).reshape(spec['shape'])
    return value


def bundle(runs, states):
    """A cell's run mapping and its distinct states as one deterministic gzip stream."""
    order = sorted(states)
    index, offset = {}, 0
    for key in order:
        index[key] = dict(offset=offset, length=len(states[key])); offset += len(states[key])
    head = encode(dict(schema=SCHEMA, runs=runs, states=index))
    return gzip.compress(head + b'\n' + b''.join(states[k] for k in order), mtime=0)


def unbundle(raw):
    head, _, body = gzip.decompress(raw).partition(b'\n')
    value = json.loads(head)
    states = {}
    for key, spec in value['states'].items():
        chunk = body[spec['offset']:spec['offset'] + spec['length']]
        if sha(chunk) != key: raise ValueError('state digest mismatch')
        states[key] = chunk
    return value['runs'], states


def by_cell(records):
    """Group a flat record list into one list per cell (tests and small inputs)."""
    cells = {}
    for r in records: cells.setdefault(r['cell'], []).append(r)
    return [cells[c] for c in sorted(cells)]


def produce(groups, wave, root, analyse=None, captured=None):
    """Write the archive; return its inventory. Refuses to overwrite recorded evidence.

    `groups`: an iterable of per-cell record lists, each record dict(cell, run,
    protocol, admitted, payload, inputHashes, admission, sources, attestation):
    the payload is what an estimator reads, the rest is the run's provenance. A cell's
    rows arrive together and are dropped once written, so a whole sitting never
    sits in memory. `captured`: every declared cell some admitted run captured,
    for the completeness line; defaults to the archived cells.
    """
    analyse = analyse or default_analyse()
    root = Path(root)
    if root.exists(): raise ValueError('archive output already exists; do not rewrite recorded evidence')
    root.mkdir(parents=True)
    inventory, cells, manifests = [], [], set()
    for rows in groups:
        cell = rows[0]['cell']
        if any(r['cell'] != cell for r in rows): raise ValueError('a group mixes cells')
        if cell in cells: raise ValueError('a cell arrived in two groups: ' + cell)
        if cell not in wave.cells: raise ValueError('undeclared archive cell')
        cells.append(cell); manifests.update(r['inputHashes']['manifest'] for r in rows)
        role = wave.roles[cell.split('/', 1)[1]]
        states, runs, stats = {}, [], {}
        for r in rows:
            raw = pack(r['payload']); state = sha(raw)
            if state not in states:
                # The statistics are a function of the state, so a byte-stable
                # repeat is analysed once; every run still names its state.
                states[state] = raw
                stats[state] = json.loads(encode(statistics(r['payload'], analyse)))
            runs.append(dict(run=r['run'], protocol=r.get('protocol', 'normal'), state=state,
                             admitted=r['admitted'], admission=r.get('admission', {}),
                             inputHashes=r['inputHashes'], sources=r.get('sources', {}),
                             attestation=r.get('attestation', {})))
        files = {'crop': bundle(runs, states),
                 'statistics': gzip.compress(encode(dict(schema=SCHEMA, runs=runs, statistics=stats)), mtime=0)}
        admitted = any(r['admitted'] for r in rows)
        for kind, raw in files.items():
            path = f"{role}/{sha(cell.encode())}.{kind}" + ('.bin.gz' if kind == 'crop' else '.json.gz')
            dest = root / path; dest.parent.mkdir(parents=True, exist_ok=True); dest.write_bytes(raw)
            inventory.append(dict(cell=cell, kind=kind, path=path, sha256=sha(raw), admitted=admitted))
    declared = sorted(wave.cells)
    inventory.sort(key=lambda row: (row['cell'], row['kind']))
    output = dict(schema=SCHEMA, scenesSha256=wave.scenes_sha, splitSha256=wave.split_sha,
                  sourceManifests=sorted(manifests),
                  declaredCells=len(declared), archivedCells=len(cells),
                  uncaptured=sorted(set(declared) - set(captured if captured is not None else cells)),
                  entries=inventory,
                  disclosure='Inventory, hashes and admission only; analytical payload is role-separated.')
    (root / 'inventory.json').write_bytes(encode(output))
    return output


def replay(reader, cell, analyse=None):
    """Recompute every run's statistics from the archived states alone; refuse any difference."""
    analyse = analyse or default_analyse()
    runs, states = unbundle(reader.read(cell, 'crop'))
    recorded = json.loads(gzip.decompress(reader.read(cell, 'statistics')))
    output = {state: json.loads(encode(statistics(unpack(raw), analyse))) for state, raw in states.items()}
    if runs != recorded['runs'] or output != recorded['statistics']:
        raise ValueError('raw/archive instrument outputs differ: ' + cell)
    return dict(cell=cell, runs=len(runs), states=len(states), identical=True)


def recorded_statistics(reader, cell):
    """Every run of a cell with the statistics of its state, as the producer recorded them."""
    recorded = json.loads(gzip.decompress(reader.read(cell, 'statistics')))
    return [{**run, 'statistics': recorded['statistics'][run['state']]} for run in recorded['runs']]
