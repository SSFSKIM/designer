#!/usr/bin/env python3.12
"""W42's archive of record: produce, pack, fetch and replay (charter clause 5; X24; G1).

Derived from W39 G0's w39_archive.py, archive-producer.py, release-asset.py,
fetch-archive.py and replay-archive.py (§5.184), none of which is edited. The same
procedural boundary: every admitted run is archived BEFORE plurality, one file per cell per
kind in its role's directory, and the inventory publishes only cells, kinds, paths, hashes
and admission, so a producer may see holdout while nothing it prints discloses a held
statistic. What W42 changes:

- A frame is archived as the ORIGINAL PNG bytes the harness wrote, not re-encoded: the
  archive's frame hash is the capture's file hash. A cell's `states` file is one gzip
  stream of a JSON header (every run: pass, run, protocol, the frame it produced, its
  no-glass reference's frame and source run, the fixture attestation, the manifest hash)
  and the distinct PNG blobs it names, its reference's included, so reading one role never
  needs another. A reference captured in run 1 serves runs 2-7 of its pass and names its
  source run (W39's run-1 colour references, the same rule).
- The `statistics` file holds `analyse(png)` per distinct frame. The default analyse is
  instrument-free (decoded RGB SHA-256, shape, per-channel mean/min/max); G1 passes the
  instrument's reader instead, and replay recomputes whichever was recorded.
- The sitting's OPERATIONAL record (every run's and quarantine's machine and session reads,
  launch argv, admission or refusal, idle-wait log, capture logs, manifests, the derived
  scenes documents, the orchestrator and driver logs) goes into the archive under
  operational/, and every dump JSON with its dumpcheck report under dumps/ (charter
  "Repeats, the bar and the archive of record": the logs go into the archive, not into
  git). Both are listed in their own inventory sections, outside the role directories, so
  the wave Reader's role check (bed/wave.py, W39's Reader) never serves them to an
  estimator.
- The inventory names the W42 declaration: scenesSha256 = scenes-w42-body.json and
  splitSha256 = bed.json, the pair bed/wave.py pins.
"""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
BED_DIR = HERE.parent
REPO = HERE.parents[5]
SCHEMA = 'w42-archive-1'
TAG = 'w42-archive'
PREFIX = 'w42-archive-'
SUFFIX = '.tar.zst'
TOP = 'archive'
LIMIT = 2 * 1024 ** 3
GH_REPO = 'SSFSKIM/designer'
ZSTD = ['zstd', '-19', '-T1', '-q', '-c']
CACHE = Path.home() / '.cache' / 'vitrea-archives'
SECTIONS = ('entries', 'operational', 'dumps')
_MODULES = {}


def module(name, path):
    if name not in _MODULES:
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _MODULES[name] = m
    return _MODULES[name]


def wave_module():
    return module('w42_wave_for_archive', BED_DIR / 'wave.py')


def sitting():
    return module('w42_sitting_for_archive', HERE / 'sitting.py')


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def file_sha(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for block in iter(lambda: f.read(chunk), b''):
            h.update(block)
    return h.hexdigest()


def refuse_repository(path):
    resolved = Path(path).resolve()
    if resolved == REPO or REPO in resolved.parents:
        raise ValueError('the archive of record is a release asset; write it outside the repository')


# ------------------------------------------------------------------- analysis

def default_analyse(png):
    """Instrument-free statistics of one frame: what replay can recompute from bytes alone."""
    with Image.open(io.BytesIO(png)) as image:
        if image.format != 'PNG' or image.mode not in ('RGB', 'RGBA'):
            raise ValueError('an archived frame is an RGB(A) PNG')
        rgb = np.asarray(image.convert('RGB'), dtype=np.uint8)
    flat = rgb.reshape(-1, 3).astype(np.float64)
    return dict(shape=list(rgb.shape), rgbSha256=sha(rgb.tobytes()),
                mean=[round(float(v), 6) for v in flat.mean(0)],
                min=[int(v) for v in flat.min(0)], max=[int(v) for v in flat.max(0)])


# ------------------------------------------------------------- bundle format

def bundle(header, blobs):
    order = sorted(blobs)
    index, offset = {}, 0
    for key in order:
        index[key] = dict(offset=offset, length=len(blobs[key]))
        offset += len(blobs[key])
    return gzip.compress(encode({**header, 'blobs': index}) + b'\n' + b''.join(blobs[k] for k in order), mtime=0)


def unbundle(raw):
    head, _, body = gzip.decompress(raw).partition(b'\n')
    header = json.loads(head)
    blobs = {}
    for key, spec in header.pop('blobs').items():
        chunk = body[spec['offset']:spec['offset'] + spec['length']]
        if len(chunk) != spec['length'] or sha(chunk) != key:
            raise ValueError('archived frame is truncated or altered: ' + key)
        blobs[key] = chunk
    return header, blobs


# ---------------------------------------------------------------- the producer

def load_run(root, protocols):
    root = Path(root).resolve()
    admission = json.loads((root / 'admission.json').read_text())
    if admission.get('admitted') is not True or admission.get('dry') is True:
        raise ValueError('producer input is not an admitted capture run: ' + str(root))
    raw = (root / 'manifest.json').read_bytes()
    manifest = json.loads(raw)
    arm = admission.get('protocol')
    if arm not in ('normal', 'long'):
        raise ValueError(f'admission names no capture protocol arm: {arm!r}')
    if admission.get('captureProtocol') != protocols[arm]:
        raise ValueError(f'admission captureProtocol disagrees with the sitting\'s {arm} settings')
    captured = manifest.get('captureProtocol') or {}
    if {k: captured.get(k) for k in protocols[arm]} != protocols[arm]:
        raise ValueError(f'manifest captureProtocol is not the {arm} arm')
    if (arm == 'long') != str(admission.get('pass', '')).endswith('-sentinel'):
        raise ValueError('the long arm is exactly the sentinel passes')
    if admission.get('manifestSha256') != sha(raw):
        raise ValueError('admission names a different manifest')
    entries = {}
    for profile in manifest['profiles']:
        for fixture in profile['fixtures']:
            key = (profile['profileKey'], fixture['sceneId'])
            if key in entries:
                raise ValueError('run captured one cell twice: ' + str(key))
            entries[key] = fixture
    return dict(root=root, admission=admission, manifestSha=sha(raw), protocol=arm, entries=entries)


def sitting_runs(raw_root, bed, passes=None):
    """The admitted capture runs in sitting order, refusing any declared run that is absent.

    `passes` restricts the archive to named passes (tests); the archive of record uses all.
    """
    P = module('w42_pass_spec_for_archive', HERE / 'pass-spec.py')
    order = [p for p in P.pass_order(bed) if p['kind'] != 'dump' and (passes is None or p['name'] in passes)]
    runs = []
    for p in order:
        for n in range(1, p['runs'] + 1):
            run = Path(raw_root) / p['name'] / f'run-{n}'
            if not (run / 'admission.json').is_file():
                raise ValueError(f'{p["name"]} run {n} is not admitted; the archive of record is complete')
            runs.append(run)
    dump_passes = [p for p in P.pass_order(bed) if p['kind'] == 'dump' and (passes is None or p['name'] in passes)]
    return runs, dump_passes


def operational_files(raw_root, passes):
    """Every non-pixel file of the sitting, admitted and quarantined runs alike, and the logs."""
    raw_root = Path(raw_root)
    out = []
    for name in passes:
        base = raw_root / name
        for path in sorted(base.rglob('*')):
            rel = path.relative_to(base)
            if not path.is_file() or path.is_symlink():
                continue
            if path.suffix == '.png' or 'backgrounds' in rel.parts or (len(rel.parts) > 1 and rel.parts[1] == 'json'):
                continue
            if rel.name == 'check.json' and name.startswith('dump-'):
                continue
            out.append((f'operational/{name}/{rel.as_posix()}', path))
    logs = raw_root / 'logs'
    if logs.is_dir():
        for path in sorted(p for p in logs.rglob('*') if p.is_file() and not p.is_symlink()):
            out.append((f'operational/logs/{path.relative_to(logs).as_posix()}', path))
    return out


def dump_files(raw_root, dump_passes):
    out = []
    for p in dump_passes:
        base = Path(raw_root) / p['name']
        for run in sorted(q for q in base.iterdir() if q.is_dir()):
            if not run.name.startswith(('run-', 'QUARANTINE-')):
                continue
            for path in sorted(list((run / 'json').glob('*.json')) + [run / 'check.json']):
                if path.is_file():
                    out.append((f'dumps/{p["name"]}/{run.name}/{path.relative_to(run).as_posix()}', path))
    return out


def produce(raw_root, out, wave=None, analyse=None, passes=None):
    """Write the archive of record from a sitting root; return its inventory.

    Refuses to overwrite, refuses an incomplete sitting (every declared run of every pass
    admitted; every dump pass admitted), and refuses a reference that would outrank its
    dependent. Prints nothing but counts and hashes.
    """
    analyse = analyse or default_analyse
    wave = wave or wave_module().default_wave()
    W = wave_module()
    refuse_repository(out)
    out = Path(out)
    if out.exists():
        raise ValueError('archive output already exists; do not rewrite recorded evidence')
    bed = wave.bed
    run_dirs, dump_passes = sitting_runs(raw_root, bed, passes)
    for p in dump_passes:
        if not (Path(raw_root) / p['name'] / 'run-1' / 'admission.json').is_file():
            raise ValueError(f'{p["name"]} is not admitted; no archive without the dump step')
    protocols = sitting().PROTOCOLS
    runs = [load_run(r, protocols) for r in run_dirs]
    if len({r['root'] for r in runs}) != len(runs):
        raise ValueError('a run root is named twice')
    frames = {}

    def frame(run, key):
        if key not in run['entries']:
            raise KeyError(key)
        path = run['root'] / run['entries'][key]['file']
        if path not in frames:
            raw = path.read_bytes()
            scale = 1 if '-1x-' in key[0] else 2
            with Image.open(io.BytesIO(raw)) as image:
                size = image.size
            if size != (wave.spec['canvas']['width'] * scale, wave.spec['canvas']['height'] * scale):
                raise ValueError('frame dimensions disagree with the declared canvas and scale: ' + str(path))
            frames[path] = (raw, sha(raw))
        return frames[path]

    def dependency(run, key):
        """The run's own capture, else the first run in sitting order of the same endpoint (the
        pass and its sentinels share `key`) that has it: run 1 of the bed pass, W39's rule."""
        if key in run['entries']:
            return run
        same = [r for r in runs if r['admission'].get('key') == run['admission'].get('key') and key in r['entries']]
        if not same:
            raise ValueError('missing captured dependency ' + str(key))
        return same[0]

    out.mkdir(parents=True)
    cells = sorted({key for r in runs for key in r['entries']})
    inventory, manifests = [], set()
    for profile, sid in cells:
        cell = profile + '/' + sid
        if cell not in wave.cells:
            raise ValueError('raw run has undeclared cell ' + cell)
        role = wave.roles[sid]
        rows, blobs, stats = [], {}, {}
        deps = wave.dependencies.get(sid, {})
        for run in runs:
            if (profile, sid) not in run['entries']:
                continue
            raw, digest = frame(run, (profile, sid))
            blobs[digest] = raw
            entry = run['entries'][(profile, sid)]
            row = dict(pass_=run['admission']['pass'], run=run['admission']['run'], protocol=run['protocol'],
                       frame=digest, manifestSha256=run['manifestSha'],
                       attestation={k: v for k, v in entry.items() if k != 'file'}, dependencies={})
            manifests.add(run['manifestSha'])
            for name, dep in deps.items():
                if W.RANK[wave.roles[dep]] > W.RANK[role]:
                    raise PermissionError('dependency role ranks above its dependent: ' + dep)
                source = dependency(run, (profile, dep))
                draw, ddigest = frame(source, (profile, dep))
                blobs[ddigest] = draw
                row['dependencies'][name] = dict(sceneId=dep, frame=ddigest, sourcePass=source['admission']['pass'],
                                                 sourceRun=source['admission']['run'],
                                                 manifestSha256=source['manifestSha'])
            rows.append({('pass' if k == 'pass_' else k): v for k, v in row.items()})
        for digest, raw in blobs.items():
            stats[digest] = json.loads(encode(analyse(raw)))
        header = dict(schema=SCHEMA, cell=cell, role=role, runs=rows)
        files = {'states': bundle(header, blobs),
                 'statistics': gzip.compress(encode(dict(schema=SCHEMA, cell=cell, runs=rows, statistics=stats)),
                                             mtime=0)}
        for kind, raw in files.items():
            path = f'{role}/{sha(cell.encode())}.{kind}' + ('.bin.gz' if kind == 'states' else '.json.gz')
            dest = out / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
            inventory.append(dict(cell=cell, kind=kind, path=path, sha256=sha(raw), admitted=True))
    names = [p['name'] for p in module('w42_pass_spec_for_archive', HERE / 'pass-spec.py').pass_order(bed)
             if passes is None or p['name'] in passes]
    sections = {'operational': operational_files(raw_root, names), 'dumps': dump_files(raw_root, dump_passes)}
    listed = {}
    for section, files in sections.items():
        rows = []
        for rel, path in files:
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)
            rows.append(dict(path=rel, sha256=file_sha(dest)))
        listed[section] = rows
    if passes is None:
        declared = sorted(wave.cells)
    else:
        P = module('w42_pass_spec_for_archive', HERE / 'pass-spec.py')
        declared = sorted({f'{bed["passes"][q["key"]]["profile"]}/{sid}'
                           for q in P.pass_order(bed) if q['name'] in names and q['kind'] == 'bed'
                           for sid in P.capture_ids(bed, q['key'], 1)})
    captured = sorted({p + '/' + s for p, s in cells})
    inventory.sort(key=lambda r: (r['cell'], r['kind']))
    value = dict(schema=SCHEMA, scenesSha256=wave.scenes_sha, splitSha256=wave.split_sha,
                 sourceManifests=sorted(manifests), declaredCells=len(declared), archivedCells=len(captured),
                 uncaptured=sorted(set(declared) - set(captured)), passes=names,
                 producer={name: file_sha(HERE / name) for name in ('sitting.py', 'pass-spec.py', 'w42_archive.py')},
                 dumpcheckSha256=file_sha(BED_DIR / 'dumps/dumpcheck.py'),
                 analyse=getattr(analyse, '__qualname__', str(analyse)),
                 entries=inventory, operational=listed['operational'], dumps=listed['dumps'],
                 disclosure='Inventory, hashes and admission only; analytical payload is role-separated; '
                            'operational/ and dumps/ are audit material, never an estimator input.')
    (out / 'inventory.json').write_bytes(encode(value))
    return value


# ------------------------------------------------------------ tree and asset

def verify_tree(root):
    """Every inventory file present and intact, and nothing else: the tree IS the inventory."""
    root = Path(root)
    inventory = json.loads((root / 'inventory.json').read_bytes())
    expected = {'inventory.json'}
    for section in SECTIONS:
        for row in inventory.get(section, []):
            rel = PurePosixPath(row['path'])
            if rel.is_absolute() or '..' in rel.parts:
                raise ValueError('inventory path escapes the archive')
            path = root / rel
            if path.is_symlink() or not path.is_file():
                raise ValueError('inventory entry missing: ' + row['path'])
            if file_sha(path) != row['sha256']:
                raise ValueError('inventory entry altered: ' + row['path'])
            expected.add(str(rel))
    present = set()
    for dirpath, dirnames, filenames in os.walk(root):
        for name in dirnames + filenames:
            if (Path(dirpath) / name).is_symlink():
                raise ValueError('symlink in archive tree: ' + str(Path(dirpath) / name))
        for name in filenames:
            present.add((Path(dirpath) / name).relative_to(root).as_posix())
    if present != expected:
        raise ValueError('archive tree differs from its inventory: unlisted %s, missing %s' % (
            sorted(present - expected)[:5], sorted(expected - present)[:5]))
    return dict(entries=sum(len(inventory.get(s, [])) for s in SECTIONS),
                inventorySha256=file_sha(root / 'inventory.json'))


def asset_name(digest):
    return PREFIX + digest + SUFFIX


def check_digest(digest):
    if not (isinstance(digest, str) and len(digest) == 64 and all(c in '0123456789abcdef' for c in digest)):
        raise ValueError('an archive is named by a full lowercase SHA-256 (64 hex digits)')


def tar_bytes_to(root, stream):
    root = Path(root)
    files = sorted(p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file())
    dirs = sorted({str(d) for f in files for d in PurePosixPath(f).parents if str(d) != '.'})
    with tarfile.open(fileobj=stream, mode='w|', format=tarfile.PAX_FORMAT) as tar:
        def info(name, kind, size=0):
            t = tarfile.TarInfo(name)
            t.type, t.size, t.mtime, t.uid, t.gid, t.uname, t.gname = kind, size, 0, 0, 0, '', ''
            t.mode = 0o755 if kind == tarfile.DIRTYPE else 0o644
            return t
        tar.addfile(info(TOP, tarfile.DIRTYPE))
        for d in dirs:
            tar.addfile(info(f'{TOP}/{d}', tarfile.DIRTYPE))
        for f in files:
            with open(root / f, 'rb') as handle:
                tar.addfile(info(f'{TOP}/{f}', tarfile.REGTYPE, (root / f).stat().st_size), handle)
    return len(files)


def pack(archive, out_dir, limit=LIMIT):
    archive, out_dir = Path(archive).resolve(), Path(out_dir).resolve()
    refuse_repository(out_dir)
    tree = verify_tree(archive)
    out_dir.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.packing-', dir=out_dir)
    os.close(fd)
    tmp = Path(tmp)
    try:
        with open(tmp, 'wb') as sink:
            zstd = subprocess.Popen(ZSTD, stdin=subprocess.PIPE, stdout=sink)
            try:
                members = tar_bytes_to(archive, zstd.stdin)
            finally:
                zstd.stdin.close()
            if zstd.wait() != 0:
                raise RuntimeError('zstd failed')
        size = tmp.stat().st_size
        if size >= limit:
            raise ValueError('asset is %d bytes; a release asset must be under %d' % (size, limit))
        digest = file_sha(tmp)
        final = out_dir / asset_name(digest)
        os.replace(tmp, final)
    finally:
        if tmp.exists():
            tmp.unlink()
    version = subprocess.run(['zstd', '--version'], capture_output=True, text=True, check=True).stdout.strip()
    return dict(asset=asset_name(digest), path=str(final), sha256=digest, bytes=size, tarMembers=members,
                zstd=version, compression=' '.join(ZSTD[1:]), **tree)


def publish_commands(result, repo=GH_REPO):
    """Printed for G1, never run here: the tag is never marked latest."""
    notes = ('W42 archive of record (charter clause 5; ledger §5.195). SHA-256 %s, %d bytes. '
             'Verify with w42_archive.py fetch before reading.' % (result['sha256'], result['bytes']))
    return [['gh', 'release', 'create', TAG, '--repo', repo, '--title', 'W42 archive of record',
             '--notes', notes, '--latest=false', '--target', '<G1 merge commit>'],
            ['gh', 'release', 'upload', TAG, result['path'], '--repo', repo],
            ['gh', 'release', 'view', TAG, '--repo', repo, '--json', 'assets']]


def gh_download(tag, asset, repo, directory):
    subprocess.run(['gh', 'release', 'download', tag, '--repo', repo, '--pattern', asset,
                    '--dir', str(directory)], check=True)
    return Path(directory) / asset


def safe_members(tar):
    seen = set()
    for member in tar:
        name = PurePosixPath(member.name)
        if name.is_absolute() or '..' in name.parts or not name.parts or name.parts[0] != TOP:
            raise ValueError('unsafe archive member path: ' + member.name)
        if not (member.isreg() or member.isdir()):
            raise ValueError('archive member is not a regular file or directory: ' + member.name)
        if str(name) in seen:
            raise ValueError('duplicate archive member: ' + member.name)
        seen.add(str(name))
        yield member


def extract(tarball, destination):
    destination = Path(destination)
    with tempfile.NamedTemporaryFile(dir=destination.parent, suffix='.tar') as plain:
        subprocess.run(['zstd', '-d', '-q', '-c', str(tarball)], stdout=plain, check=True)
        plain.flush()
        with tarfile.open(plain.name, mode='r:') as tar:
            members = list(safe_members(tar))
            destination.mkdir()
            tar.extractall(destination, members=members, filter='data')
    return destination / TOP


def fetch(tag, asset, digest, repo=GH_REPO, cache=CACHE, download=gh_download, source=None):
    """Fetch by the recorded name, verify the full digest BEFORE decompression, extract through
    a member check, re-check the tree against its inventory; a cache is re-checked every call."""
    check_digest(digest)
    if asset != asset_name(digest):
        raise ValueError('asset name does not carry the expected digest: ' + asset)
    cache = Path(cache).expanduser().resolve()
    refuse_repository(cache)
    home = cache / digest
    root = home / 'extracted' / TOP
    marker = home / 'verified.json'
    if root.is_dir() and marker.is_file() and json.loads(marker.read_text()).get('sha256') == digest:
        verify_tree(root)
        return root
    home.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=home, prefix='.download-') as scratch:
        if source is not None:
            fetched = Path(scratch) / asset
            shutil.copyfile(source, fetched)
        else:
            fetched = Path(download(tag, asset, repo, scratch))
        actual = file_sha(fetched)
        if actual != digest:
            raise ValueError('digest mismatch: expected %s, fetched %s; nothing extracted' % (digest, actual))
        partial = Path(scratch) / 'extracted'
        extracted = extract(fetched, partial)
        tree = verify_tree(extracted)
        if (home / 'extracted').exists():
            shutil.rmtree(home / 'extracted')
        os.replace(partial, home / 'extracted')
        os.replace(fetched, home / asset)
    marker.write_text(json.dumps(dict(sha256=digest, asset=asset, tag=tag, repo=repo,
                                      bytes=(home / asset).stat().st_size, **tree), indent=2) + '\n')
    return root


# ---------------------------------------------------------------------- replay

_DENIED = []
_HOOKED = False


def deny(root):
    """Refuse any open under `root` for the rest of the process (W39 replay-archive's hook)."""
    global _HOOKED
    _DENIED.append(str(Path(root).resolve()))
    if not _HOOKED:
        def audit(event, values):
            if event == 'open' and isinstance(values[0], (str, bytes)) and _DENIED:
                raw = values[0].decode() if isinstance(values[0], bytes) else values[0]
                path = str(Path(raw).resolve())
                if any(path == d or path.startswith(d + '/') for d in _DENIED):
                    raise PermissionError('raw inputs forbidden in archive-only proof: ' + path)
        sys.addaudithook(audit)
        _HOOKED = True


def replay(root, wave=None, roles=('calibration', 'validation', 'probe'), analyse=None, deny_raw_root=None):
    """Recompute every recorded statistic from the archived bytes alone; refuse any difference.

    Holdout is never replayed here: the Reader refuses it without the receipt.
    """
    analyse = analyse or default_analyse
    wave = wave or wave_module().default_wave()
    if deny_raw_root is not None:
        deny(deny_raw_root)
    tree = verify_tree(root)
    reader = wave.reader(root, roles=tuple(roles))
    cells = sorted({r['cell'] for r in reader.report_inventory() if r['cell'].split('/', 1)[1] in reader.allowed})
    outputs = []
    for cell in cells:
        header, blobs = unbundle(reader.read(cell, 'states'))
        recorded = json.loads(gzip.decompress(reader.read(cell, 'statistics')))
        again = {digest: json.loads(encode(analyse(raw))) for digest, raw in blobs.items()}
        if header['runs'] != recorded['runs'] or again != recorded['statistics']:
            raise ValueError('raw/archive outputs differ: ' + cell)
        named = {r['frame'] for r in header['runs']} | {d['frame'] for r in header['runs']
                                                         for d in r['dependencies'].values()}
        if named != set(blobs):
            raise ValueError('states bundle and its runs disagree: ' + cell)
        outputs.append(dict(cell=cell, runs=len(header['runs']), states=len(blobs), identical=True))
    return dict(rawRootForbidden=None if deny_raw_root is None else str(deny_raw_root), roles=list(roles),
                generation=reader.generation, cells=len(outputs), identical=all(o['identical'] for o in outputs),
                tree=tree, outputs=outputs)


# ------------------------------------------------------------------------ CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='action', required=True)
    p = sub.add_parser('produce')
    p.add_argument('raw_root', type=Path)
    p.add_argument('--out', type=Path, required=True)
    k = sub.add_parser('pack')
    k.add_argument('archive', type=Path)
    k.add_argument('--out-dir', type=Path, required=True)
    v = sub.add_parser('verify-tree')
    v.add_argument('archive', type=Path)
    f = sub.add_parser('fetch')
    f.add_argument('--tag', default=TAG)
    f.add_argument('--asset', required=True)
    f.add_argument('--sha256', required=True)
    f.add_argument('--repo', default=GH_REPO)
    f.add_argument('--cache', type=Path, default=CACHE)
    f.add_argument('--source', type=Path, help='a local owner-controlled copy, verified the same way')
    r = sub.add_parser('replay')
    r.add_argument('root', type=Path)
    r.add_argument('--roles', default='calibration,validation,probe')
    r.add_argument('--deny-raw-root', type=Path)
    args = ap.parse_args(argv)
    if args.action == 'produce':
        value = produce(args.raw_root, args.out)
        print(json.dumps(dict(inventory=str(args.out / 'inventory.json'),
                              inventorySha256=file_sha(args.out / 'inventory.json'),
                              declaredCells=value['declaredCells'], archivedCells=value['archivedCells'],
                              uncaptured=len(value['uncaptured']), operational=len(value['operational']),
                              dumps=len(value['dumps'])), indent=2))
    elif args.action == 'pack':
        result = pack(args.archive, args.out_dir)
        print(json.dumps(dict(**result, tag=TAG, publish=publish_commands(result)), indent=2))
    elif args.action == 'verify-tree':
        print(json.dumps(verify_tree(args.archive), indent=2))
    elif args.action == 'fetch':
        print(fetch(args.tag, args.asset, args.sha256, args.repo, args.cache, source=args.source))
    else:
        result = replay(args.root, roles=args.roles.split(','), deny_raw_root=args.deny_raw_root)
        print(json.dumps({k: v for k, v in result.items() if k != 'outputs'}, indent=2))
        if not result['identical']:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
