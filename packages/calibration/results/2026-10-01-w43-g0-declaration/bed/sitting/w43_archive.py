#!/usr/bin/env python3.12
"""W43's archive of record: produce, verify-tree, pack, fetch and replay (charter clause 5; X24;
G1a, G1b).

Derived from W42 G0's w42_archive.py (§5.195), which is not edited. The same procedural boundary:
every admitted run is archived BEFORE plurality, the inventory publishes cells, kinds, paths,
hashes and admission only, `pack` writes a deterministic release asset under 2 GiB named by its
SHA-256, `fetch` verifies the full digest before it decompresses anything, and `replay`
recomputes every recorded statistic from the archived bytes alone with the raw root denied by an
audit hook. What W43 changes:

- **Each distinct frame is stored ONCE, by SHA-256** (charter G0 (d); Risks, "the archive's
  size"). `frames/<sha256>.png` holds the original PNG bytes the harness wrote, whichever run,
  cell or role produced them: a capture, or a background raster a run composited over. A cell's
  record (`<role>/<sha256(cell)>.cell.json.gz`) lists every run's membership (pass, run,
  protocol, frame, manifest hash, the fixture's attestation) and the statistics of each distinct
  frame it names, so a cell unanimous over seven runs costs one frame, and a frame two cells or
  two passes share (a bridge recaptured at the close, a capture identical to its own backdrop)
  costs one frame too. W42 bundled each cell's distinct frames inside the cell, so every no-glass
  reference was stored again in every cell that depended on it. Each run's background rasters
  are named from its run record in the inventory.
- **The membership is the declared plan** (pass-spec.py): the producer refuses a sitting with a
  declared run not admitted, a dump pass not admitted, an admission under another plan or
  sitting or a predeclaration, an admission whose bound cells are not its run's declared ones,
  a frame whose bytes are not the ones admission bound, an undeclared or uncaptured cell, a cell
  captured from two scenes files, existing output, and output inside a checkout.
- **No holdout redaction.** W42 withheld its sealed holdout's diagnostics from operational/ and
  kept the whole files behind a receipt. W43 seals no holdout: the canonical bed's held-out cells
  are published as fixtures (W29's practice) and the probe declares calibration and validation
  only (X46), as `sitting.frame_binding` records. So operational/ holds every run's and every
  quarantine's non-pixel files whole, and replay reads every role.

The operational record (every run's and quarantine's reads, attest.read, argv, admission or
refusal, driver-idle.txt and watchdog.txt, capture logs, manifests, the derived scenes documents,
and logs/: the orchestrator's status, the slider's writes and as-found record, the launcher
chain, the Universal Control report) is under operational/, and every dump JSON with its
sentinel check under dumps/, each in its own inventory section.
"""
import argparse
import gzip
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
MAIN = Path('/Users/new/Developer/GitHub/designer')
SCHEMA = 'w43-archive-1'
PREFIX = 'w43-archive-'
SUFFIX = '.tar.zst'
TOP = 'archive'
LIMIT = 2 * 1024 ** 3
GH_REPO = 'SSFSKIM/designer'
ZSTD = ['zstd', '-19', '-T1', '-q', '-c']
CACHE = Path.home() / '.cache' / 'vitrea-archives'
SECTIONS = ('frames', 'cells', 'operational', 'dumps')
SPLIT_ROLES = ('calibration', 'validation', 'holdout', 'recorded', 'probe')
FRAME_PATH = re.compile(r'^frames/([0-9a-f]{64})\.png$')
_MODULES = {}


def module(name, path):
    if name not in _MODULES:
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _MODULES[name] = m
    return _MODULES[name]


def pass_spec():
    return module('w43_pass_spec_for_archive', HERE / 'pass-spec.py')


def sitting():
    return module('w43_sitting_for_archive', HERE / 'sitting.py')


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
    for checkout in (REPO, MAIN):
        root = checkout.resolve()
        if resolved == root or root in resolved.parents:
            raise ValueError('the archive of record is a release asset; write it outside every checkout')


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


# ---------------------------------------------------------------- the producer

def role_of(doc, sid):
    for role in SPLIT_ROLES:
        if sid in (doc.get('split') or {}).get(role, []):
            return role
    return None


def unrehearsed(admission, declaration, what):
    """An admission counts only under the plan being archived, never a rehearsal's."""
    if (admission.get('sitting'), admission.get('planSha256')) != (declaration['sitting'], declaration['planSha256']):
        raise ValueError(f'{what} was admitted under another declaration (sitting {admission.get("sitting")!r}, plan '
                         f'{str(admission.get("planSha256"))[:12]}); the archive names {declaration["sitting"]} / '
                         f'{declaration["planSha256"][:12]}')
    if admission.get('predeclaration') or (admission.get('declaration') or {}).get('predeclaration'):
        raise ValueError(f'{what} is a predeclaration rehearsal, never evidence')


def load_run(run, p, n, doc, protocols, declaration):
    """One admitted capture run, checked against its plan, admission and bytes."""
    what = f'{p["name"]} run {n}'
    path = run / 'admission.json'
    if not path.is_file():
        raise ValueError(f'{what} is not admitted; the archive of record holds the whole declared sitting')
    admission = json.loads(path.read_text())
    if admission.get('admitted') is not True or admission.get('dry') is True:
        raise ValueError(f'{what} is not an admitted capture run')
    if (admission.get('pass'), admission.get('run')) != (p['name'], n):
        raise ValueError(f'{what}: its admission names {admission.get("pass")} run {admission.get("run")}')
    unrehearsed(admission, declaration, what)
    arm = admission.get('protocol')
    if arm != p['protocol'] or admission.get('captureProtocol') != protocols[arm]:
        raise ValueError(f'{what}: admission names the {arm!r} protocol; the plan declares {p["protocol"]}')
    raw = (run / 'manifest.json').read_bytes()
    if admission.get('manifestSha256') != sha(raw):
        raise ValueError(f'{what}: admission names a different manifest')
    manifest = json.loads(raw)
    captured = manifest.get('captureProtocol') or {}
    if {k: captured.get(k) for k in protocols[arm]} != protocols[arm]:
        raise ValueError(f'{what}: manifest captureProtocol is not the {arm} arm')
    entries = {}
    for profile in manifest['profiles']:
        for fixture in profile['fixtures']:
            cell = f'{profile["profileKey"]}/{fixture["sceneId"]}'
            if cell in entries:
                raise ValueError(f'{what} captured one cell twice: {cell}')
            entries[cell] = fixture
    declared = set(pass_spec().cells(doc))
    bound = admission.get('frames')
    if not isinstance(bound, dict) or set(bound) != declared or set(entries) != declared:
        raise ValueError(f'{what}: admission or manifest cells are not the cells the plan declares for this run')
    root = run.resolve()
    frames = {}
    for cell, fixture in entries.items():
        png = (run / fixture['file']).resolve()
        if root not in png.parents or not png.is_file() or png.is_symlink():
            raise ValueError(f'{what}: an admitted frame is missing: {cell}')
        frames[cell] = png
    if {c: file_sha(f) for c, f in frames.items()} != bound:
        raise ValueError(f'{what}: frame bytes differ from the ones admission bound')
    backgrounds = {}
    bg = run / 'backgrounds'
    if bg.is_dir():
        for raster in sorted(q for q in bg.rglob('*') if q.is_file()):
            if raster.is_symlink() or raster.suffix != '.png':
                raise ValueError(f'{what}: a background raster is not a regular PNG: {raster.name}')
            backgrounds[raster.relative_to(run).as_posix()] = raster
    return dict(run=run, name=p['name'], n=n, protocol=arm, admission=admission, admissionSha256=file_sha(path),
                manifestSha256=sha(raw), entries=entries, frames=frames, backgrounds=backgrounds)


def check_dump(run, p, declaration):
    path = run / 'admission.json'
    if not path.is_file():
        raise ValueError(f'{p["name"]} is not admitted; no archive without every dump sentinel')
    a = json.loads(path.read_text())
    if a.get('admitted') is not True or a.get('protocol') != 'dump' or a.get('pass') != p['name']:
        raise ValueError(f'{p["name"]} is not an admitted dump')
    unrehearsed(a, declaration, p['name'])


def operational_files(raw_root, names, dump_names):
    """Every non-pixel file of the sitting, admitted runs and quarantines alike, and the logs:
    no PNG (frames are archived by hash from admitted runs only), no dump JSON or sentinel check
    (dumps/ holds them)."""
    raw_root = Path(raw_root)
    out = []
    for name in names:
        base = raw_root / name
        if not base.is_dir():
            continue
        for path in sorted(base.rglob('*')):
            rel = path.relative_to(base)
            if not path.is_file() or path.is_symlink() or path.suffix == '.png':
                continue
            if name in dump_names and len(rel.parts) > 1 and (rel.parts[1] == 'json' or rel.name == 'check.json'):
                continue
            out.append((f'operational/{name}/{rel.as_posix()}', path.read_bytes()))
    logs = raw_root / 'logs'
    if logs.is_dir():
        for path in sorted(p for p in logs.rglob('*') if p.is_file() and not p.is_symlink()):
            out.append((f'operational/logs/{path.relative_to(logs).as_posix()}', path.read_bytes()))
    return out


def dump_files(raw_root, dump_names):
    out = []
    for name in dump_names:
        base = Path(raw_root) / name
        for run in sorted(q for q in base.iterdir() if q.is_dir() and q.name.startswith(('run-', 'QUARANTINE-'))):
            for path in sorted(list((run / 'json').glob('*.json')) + [run / 'check.json']):
                if path.is_file() and not path.is_symlink():
                    out.append((f'dumps/{name}/{run.name}/{path.relative_to(run).as_posix()}', path.read_bytes()))
    return out


def declared_snapshot(sitting_name):
    """The plan, sources and declaration record the sitting ran under, as the driver checks them."""
    declaration, plan, sources = sitting().pinned_snapshot(sitting_name)
    return plan, sources, declaration


def produce(raw_root, out, plan=None, sources=None, declaration=None, sitting_name=None, analyse=None):
    """Write the archive of record from a sitting root; return its inventory.

    Every check runs before anything is written. Prints nothing but counts and hashes.
    """
    analyse = analyse or default_analyse
    if plan is None:
        plan, sources, declaration = declared_snapshot(sitting_name)
    refuse_repository(out)
    out = Path(out)
    if out.exists():
        raise ValueError('archive output already exists; do not rewrite recorded evidence')
    P = pass_spec()
    P.validate_plan(plan, sources)
    raw_root = Path(raw_root)
    protocols = sitting().PROTOCOLS
    order = P.pass_order(plan)
    runs, declared, sources_of = [], set(), {}
    for p in order:
        if p['kind'] == 'dump':
            check_dump(raw_root / p['name'] / 'run-1', p, declaration)
            continue
        for n in range(1, p['runs'] + 1):
            doc = P.derive_from(plan, sources, p['name'], n)
            for cell in P.cells(doc):
                if sources_of.setdefault(cell, p['source']) != p['source']:
                    raise ValueError(f'{cell} is declared from two scenes files ({sources_of[cell]}, {p["source"]})')
                declared.add(cell)
            runs.append(load_run(raw_root / p['name'] / f'run-{n}', p, n, doc, protocols, declaration))
    captured = {c for r in runs for c in r['entries']}
    if captured - declared:
        raise ValueError(f'{len(captured - declared)} undeclared cell(s) captured, e.g. {sorted(captured - declared)[:3]}')
    if declared - captured:
        raise ValueError(f'{len(declared - captured)} declared cell(s) were never captured (e.g. '
                         f'{sorted(declared - captured)[:3]}); the archive holds the whole declared sitting or nothing')
    roles = {}
    for cell in sorted(captured):
        role = role_of(sources[sources_of[cell]], cell.split('/', 1)[1])
        if role is None:
            raise ValueError(f'{cell} has no role in its scenes file\'s split')
        roles[cell] = role

    # The frame store: every distinct byte string once, whichever runs, cells or kinds name it.
    store, kinds = {}, {}

    def put(path, kind):
        raw = Path(path).read_bytes()
        digest = sha(raw)
        store.setdefault(digest, raw)
        kinds.setdefault(digest, set()).add(kind)
        return digest

    cells = {c: [] for c in sorted(captured)}
    run_rows = []
    for r in runs:
        for cell, png in sorted(r['frames'].items()):
            digest = put(png, 'capture')
            if digest != r['admission']['frames'][cell]:
                raise ValueError(f'{r["name"]} run {r["n"]}: {cell} changed while being archived')
            cells[cell].append(dict(**{'pass': r['name']}, run=r['n'], protocol=r['protocol'], frame=digest,
                                    manifestSha256=r['manifestSha256'],
                                    attestation={k: v for k, v in r['entries'][cell].items() if k != 'file'}))
        run_rows.append(dict(**{'pass': r['name']}, run=r['n'], protocol=r['protocol'],
                             manifestSha256=r['manifestSha256'], admissionSha256=r['admissionSha256'],
                             cells=len(r['frames']),
                             backgrounds={rel: put(path, 'background') for rel, path in r['backgrounds'].items()}))
    for digest, raw in store.items():
        with Image.open(io.BytesIO(raw)) as image:
            if image.format != 'PNG':
                raise ValueError(f'frame {digest[:12]} is not a PNG')

    dump_names = [p['name'] for p in order if p['kind'] == 'dump']
    names = [p['name'] for p in order]
    operational = operational_files(raw_root, names, set(dump_names))
    dumps = dump_files(raw_root, dump_names)

    out.mkdir(parents=True)
    frame_rows = []
    for digest in sorted(store):
        rel = f'frames/{digest}.png'
        (out / 'frames').mkdir(exist_ok=True)
        (out / rel).write_bytes(store[digest])
        frame_rows.append(dict(path=rel, sha256=digest, bytes=len(store[digest]), kinds=sorted(kinds[digest])))
    cell_rows = []
    for cell, members in cells.items():
        distinct = sorted({m['frame'] for m in members})
        record = dict(schema=SCHEMA, cell=cell, role=roles[cell], source=sources_of[cell], runs=members,
                      statistics={d: json.loads(encode(analyse(store[d]))) for d in distinct})
        raw = gzip.compress(encode(record), mtime=0)
        rel = f'{roles[cell]}/{sha(cell.encode())}.cell.json.gz'
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        (out / rel).write_bytes(raw)
        cell_rows.append(dict(cell=cell, role=roles[cell], path=rel, sha256=sha(raw), runs=len(members),
                              frames=len(distinct)))
    listed = {}
    for section, files in (('operational', operational), ('dumps', dumps)):
        rows = []
        for rel, raw in files:
            dest = out / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(raw)
            rows.append(dict(path=rel, sha256=sha(raw)))
        listed[section] = rows
    occurrences = sum(len(m) for m in cells.values()) + sum(len(r['backgrounds']) for r in run_rows)
    value = dict(schema=SCHEMA, sitting=declaration['sitting'], planSha256=declaration['planSha256'],
                 sources=declaration.get('sources'), passes=names,
                 declaredCells=len(declared), archivedCells=len(captured),
                 frameOccurrences=occurrences, distinctFrames=len(store),
                 producer={name: file_sha(HERE / name) for name in ('sitting.py', 'pass-spec.py', 'w43_archive.py')},
                 analyse=getattr(analyse, '__qualname__', str(analyse)),
                 runs=run_rows, frames=frame_rows, cells=cell_rows,
                 operational=listed['operational'], dumps=listed['dumps'],
                 disclosure='Inventory, hashes and admission only. frames/ holds each distinct PNG once by SHA-256; '
                            'each cell record names its runs\' frames and their statistics; operational/ and dumps/ '
                            'are audit material, never an estimator input. W43 seals no holdout.')
    (out / 'inventory.json').write_bytes(encode(value))
    return value


# ------------------------------------------------------------ tree and asset

def verify_tree(root):
    """Every inventory file present and intact, every frame named by its own digest, and nothing
    else: the tree IS the inventory."""
    root = Path(root)
    inventory = json.loads((root / 'inventory.json').read_bytes())
    expected = {'inventory.json'}
    for section in SECTIONS:
        for row in inventory.get(section, []):
            rel = PurePosixPath(row['path'])
            if rel.is_absolute() or '..' in rel.parts:
                raise ValueError('inventory path escapes the archive')
            if section == 'frames':
                named = FRAME_PATH.match(row['path'])
                if not named or named[1] != row['sha256']:
                    raise ValueError('a frame is not stored under its own digest: ' + row['path'])
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


def tag_of(sitting_name):
    return PREFIX + sitting_name


def asset_name(sitting_name, digest):
    return f'{PREFIX}{sitting_name}-{digest}{SUFFIX}'


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
    sitting_name = json.loads((archive / 'inventory.json').read_bytes())['sitting']
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
        final = out_dir / asset_name(sitting_name, digest)
        os.replace(tmp, final)
    finally:
        if tmp.exists():
            tmp.unlink()
    version = subprocess.run(['zstd', '--version'], capture_output=True, text=True, check=True).stdout.strip()
    return dict(asset=asset_name(sitting_name, digest), path=str(final), sha256=digest, bytes=size,
                sitting=sitting_name, tag=tag_of(sitting_name), tarMembers=members, zstd=version,
                compression=' '.join(ZSTD[1:]), **tree)


def publish_commands(result, repo=GH_REPO):
    """Printed for G1a/G1b, never run here: the tag is never marked latest."""
    notes = ('W43 %s archive of record (charter clause 5). SHA-256 %s, %d bytes. Verify with w43_archive.py fetch '
             'before reading.' % (result['sitting'], result['sha256'], result['bytes']))
    tag = result['tag']
    return [['gh', 'release', 'create', tag, '--repo', repo, '--title', f'W43 {result["sitting"]} archive of record',
             '--notes', notes, '--latest=false', '--target', '<the sitting merge commit>'],
            ['gh', 'release', 'upload', tag, result['path'], '--repo', repo],
            ['gh', 'release', 'view', tag, '--repo', repo, '--json', 'assets']]


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


def fetch(sitting_name, asset, digest, repo=GH_REPO, cache=CACHE, download=gh_download, source=None):
    """Fetch by the recorded name, verify the full digest BEFORE decompression, extract through
    a member check, re-check the tree against its inventory; a cache is re-checked every call."""
    check_digest(digest)
    if asset != asset_name(sitting_name, digest):
        raise ValueError('asset name does not carry the sitting and the expected digest: ' + asset)
    cache = Path(cache).expanduser().resolve()
    refuse_repository(cache)
    home = cache / digest
    root = home / 'extracted' / TOP
    marker = home / 'verified.json'
    if root.is_dir() and marker.is_file() and json.loads(marker.read_text()).get('sha256') == digest:
        verify_tree(root)
        return root
    home.mkdir(parents=True, exist_ok=True)
    tag = tag_of(sitting_name)
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
    """Refuse any open under `root` for the rest of the process (W39's and W42's hook)."""
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


def replay(root, roles=None, analyse=None, deny_raw_root=None):
    """Recompute every recorded statistic from the archived bytes alone; refuse any difference.

    Each frame a cell names is read from frames/, its SHA-256 must be its name, and its statistics
    must recompute exactly; every frame the inventory stores must be named by some cell or run
    record, and every frame named must be stored (no orphan, no missing frame).
    """
    analyse = analyse or default_analyse
    if deny_raw_root is not None:
        deny(deny_raw_root)
    root = Path(root)
    tree = verify_tree(root)
    inventory = json.loads((root / 'inventory.json').read_bytes())
    stored = {row['sha256'] for row in inventory['frames']}
    named = {d for r in inventory['runs'] for d in r['backgrounds'].values()}
    outputs = []
    for row in inventory['cells']:
        record = json.loads(gzip.decompress((root / row['path']).read_bytes()))
        if record['cell'] != row['cell'] or record['role'] != row['role']:
            raise ValueError('a cell record and its inventory row disagree: ' + row['cell'])
        frames = {m['frame'] for m in record['runs']}
        named |= frames
        if frames != set(record['statistics']):
            raise ValueError('a cell record\'s runs and statistics name different frames: ' + row['cell'])
        if roles is not None and row['role'] not in roles:
            continue
        again = {}
        for digest in sorted(frames):
            if digest not in stored:
                raise ValueError(f'{row["cell"]} names a frame the archive does not store: {digest[:12]}')
            raw = (root / f'frames/{digest}.png').read_bytes()
            if sha(raw) != digest:
                raise ValueError(f'frame {digest[:12]} is not the bytes its name says')
            again[digest] = json.loads(encode(analyse(raw)))
        if again != record['statistics']:
            raise ValueError('raw/archive outputs differ: ' + row['cell'])
        outputs.append(dict(cell=row['cell'], role=row['role'], runs=len(record['runs']), frames=len(frames),
                            identical=True))
    if named - stored:
        raise ValueError(f'{len(named - stored)} named frame(s) are not stored, e.g. {sorted(named - stored)[:2]}')
    if stored - named:
        raise ValueError(f'{len(stored - named)} stored frame(s) are named by no record (orphans), e.g. '
                         f'{sorted(stored - named)[:2]}')
    return dict(rawRootForbidden=None if deny_raw_root is None else str(deny_raw_root),
                roles=None if roles is None else list(roles), inventorySha256=tree['inventorySha256'],
                cells=len(outputs), frames=len(stored), identical=all(o['identical'] for o in outputs),
                tree=tree, outputs=outputs)


# ------------------------------------------------------------------------ CLI

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='action', required=True)
    p = sub.add_parser('produce')
    p.add_argument('raw_root', type=Path)
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--sitting', required=True, choices=('g1a', 'g1b'))
    k = sub.add_parser('pack')
    k.add_argument('archive', type=Path)
    k.add_argument('--out-dir', type=Path, required=True)
    v = sub.add_parser('verify-tree')
    v.add_argument('archive', type=Path)
    f = sub.add_parser('fetch')
    f.add_argument('--sitting', required=True, choices=('g1a', 'g1b'))
    f.add_argument('--asset', required=True)
    f.add_argument('--sha256', required=True)
    f.add_argument('--repo', default=GH_REPO)
    f.add_argument('--cache', type=Path, default=CACHE)
    f.add_argument('--source', type=Path, help='a local owner-controlled copy, verified the same way')
    r = sub.add_parser('replay')
    r.add_argument('root', type=Path)
    r.add_argument('--roles', help='a comma list; default every role')
    r.add_argument('--deny-raw-root', type=Path)
    args = ap.parse_args(argv)
    if args.action == 'produce':
        value = produce(args.raw_root, args.out, sitting_name=args.sitting)
        print(json.dumps(dict(inventory=str(args.out / 'inventory.json'),
                              inventorySha256=file_sha(args.out / 'inventory.json'),
                              declaredCells=value['declaredCells'], archivedCells=value['archivedCells'],
                              frameOccurrences=value['frameOccurrences'], distinctFrames=value['distinctFrames'],
                              operational=len(value['operational']), dumps=len(value['dumps'])), indent=2))
    elif args.action == 'pack':
        result = pack(args.archive, args.out_dir)
        print(json.dumps(dict(**result, publish=publish_commands(result)), indent=2))
    elif args.action == 'verify-tree':
        print(json.dumps(verify_tree(args.archive), indent=2))
    elif args.action == 'fetch':
        print(fetch(args.sitting, args.asset, args.sha256, args.repo, args.cache, source=args.source))
    else:
        result = replay(args.root, roles=None if args.roles is None else args.roles.split(','),
                        deny_raw_root=args.deny_raw_root)
        print(json.dumps({k: v for k, v in result.items() if k != 'outputs'}, indent=2))
        if not result['identical']:
            raise SystemExit(1)


if __name__ == '__main__':
    main()
