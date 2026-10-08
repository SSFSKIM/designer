#!/usr/bin/env python3
"""Package a FINISHED W50 sitting without decoding pixels or calculating statistics.

Run with python -I -B, from outside an extracted archive. `produce --sitting-finished`
is the operator's attestation that the capture command has exited; this tool neither probes
nor controls processes. Successful restoration and all 1600 admitted frames are also required.
A failed output directory is retained for inspection, never overwritten. The quarantined first
attempt remains a separate operational record and is not an input to this command.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path, PurePosixPath
import shlex
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = Path(__file__).resolve().parent
DECL = HERE.parent / '2026-10-08-w50-g0-declaration'
ROOT = HERE.parents[3]
DECLARATION_SHA = 'bb185d87d850d12fd3b0019cbe9d0db65c541b73c14690035192131e30a00b86'
FIT_SHA = 'bdd1050ed6ad9671676b0551c33a685e3093a5548652b04662fb81d4a29adb85'


def sha(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def sources():
    """Check both existing seals before executing the sealed, source-only archive helper."""
    for name, expected in (('declaration', DECLARATION_SHA), ('fit-declaration', FIT_SHA)):
        path = DECL / f'{name}.json'
        if sha(path) != expected or path.with_suffix('.sha256').read_text() != f'{expected}  {path.name}\n':
            raise ValueError('Current declaration differs from the G1a seal')
        doc = json.loads(path.read_bytes())
        for pin in doc['sources']:
            target = (ROOT / pin['path']).resolve()
            if not target.is_relative_to(ROOT) or sha(target) != pin['sha256']:
                raise ValueError('Changed declaration source: ' + pin['path'])
    path = DECL / 'bed/sitting/archive.py'
    spec = importlib.util.spec_from_file_location('w50_sealed_archive', path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), 'exec', dont_inherit=True), module.__dict__)
    return module, json.loads((DECL / 'bed/manifest.json').read_bytes()), \
        json.loads((DECL / 'bed/sitting-g1.json').read_bytes())


def destination(source, out):
    source, out = Path(source).resolve(), Path(out).resolve()
    if out == source or out.is_relative_to(source) or source.is_relative_to(out):
        raise ValueError('Source and destination overlap')
    if out.is_relative_to(ROOT):
        raise ValueError('Archive products must stay outside the source checkout')
    if out.exists():
        raise ValueError('Destination exists; never overwrite evidence')
    return source, out


def bridge_evidence(a, root, plan):
    """Bind the driver's operational verdicts; never re-read pixels or infer statistics.

    The sealed plan permits closing disagreements. They leave the sitting unbridged, not
    unadmitted; only a disagreement with stop:true prevents a finished-sitting archive.
    """
    unbridged = []
    for p in plan['passes']:
        bridge = p.get('bridge')
        if not bridge:
            continue
        for run in range(1, p['runs'] + 1):
            directory = f'{p["name"]}/run-{run}'
            path = a.safe(root, directory + '/bridge.json')
            if not path.is_file():
                raise ValueError('Missing bridge report: ' + directory)
            raw = path.read_bytes()
            admission = json.loads(a.safe(root, directory + '/admission.json').read_bytes())
            binding = admission.get('bridge')
            if not isinstance(binding, dict) or \
                    binding.get('reportSha256') != hashlib.sha256(raw).hexdigest():
                raise ValueError('Bridge report hash differs from admission: ' + directory)
            report = json.loads(raw)
            if not isinstance(report, dict) or report.get('schema') != 'w43-bridge-run-1' or \
                    report.get('pass') != p['name'] or type(report.get('run')) is not int or \
                    report['run'] != run or report.get('stop') is not bridge['stop']:
                raise ValueError('Bridge report identity differs from the sealed plan: ' + directory)
            cells = report.get('cells')
            if not isinstance(cells, list) or not all(isinstance(r, dict) for r in cells):
                raise ValueError('Invalid bridge cell report: ' + directory)
            verdicts, agreements = {}, []
            for row in cells:
                cell = row.get('cell')
                if not isinstance(cell, str) or cell not in bridge['cells'] or cell in verdicts:
                    raise ValueError('Unexpected or duplicate bridge cell: ' + directory)
                agrees = row.get('agrees')
                allowed = ('AGREE (bytes)', 'AGREE (pixels)', 'AGREE (regions)') \
                    if agrees is True else ('DISAGREE',)
                if type(agrees) is not bool or row.get('verdict') not in allowed:
                    raise ValueError('Invalid bridge cell agreement/verdict: ' + directory)
                if row.get('frameSha256') != admission['frames'][cell] or \
                        row.get('referenceSha256') != bridge['cells'][cell]['reference']['sha256']:
                    raise ValueError('Bridge cell hashes differ from admitted/declared bytes: ' + directory)
                verdicts[cell] = row['verdict']
                agreements.append(agrees)
            if set(verdicts) != set(bridge['cells']):
                raise ValueError('Bridge cell membership differs from the sealed plan: ' + directory)
            agrees = all(agreements)
            if report.get('agrees') is not agrees:
                raise ValueError('Bridge aggregate agreement differs from its cells: ' + directory)
            if binding.get('agrees') is not agrees or binding.get('stop') is not bridge['stop'] or \
                    binding.get('verdicts') != verdicts:
                raise ValueError('Admission bridge summary/verdicts differ from the report: ' + directory)
            if not agrees:
                if bridge['stop']:
                    raise ValueError('Stopping bridge disagrees: ' + directory)
                if p['name'] not in unbridged:
                    unbridged.append(p['name'])
    return unbridged


def complete_rows(a, root, manifest, plan, *, indexed=False):
    """Retain omitted root/pass logs and bind every planned bridge's operational report."""
    passes = {p['name']: {f'run-{n}' for n in range(1, p['runs'] + 1)} for p in plan['passes']}
    files = []
    for path in sorted(root.rglob('*')):
        parts = path.relative_to(root).parts
        if path.is_symlink():
            raise ValueError('Archive symlinks are refused')
        if any('QUARANTINE' in part.upper() for part in parts):
            raise ValueError('Unexpected quarantine: retain failed attempts separately')
        if parts[0] in passes:
            if len(parts) > 1 and parts[1] not in passes[parts[0]] | {'logs'}:
                if len(parts) != 2 or not path.is_file():
                    raise ValueError('Unexpected pass directory')
        elif parts[0] != 'logs' and (len(parts) != 1 or not path.is_file()):
            raise ValueError('Unexpected sitting directory')
        if path.is_file() and not (indexed and parts in (('index.json',), ('index.sha256',))):
            files.append(path)
    restored = json.loads(a.safe(root, 'logs/restore.json').read_bytes())
    if restored.get('restored') is not True or any(
            restored.get(name, {}).get('restored') is not True for name in ('slider', 'display')):
        raise ValueError('Successful slider/display restoration is required')
    for name in ('slider-as-found.json', 'as-found-mode.json', 'preflight.json'):
        if not a.safe(root, 'logs/' + name).is_file():
            raise ValueError('Missing restoration/preflight evidence')
    rows = a.collect(root, manifest, plan, DECLARATION_SHA)
    unbridged = bridge_evidence(a, root, plan)
    known = {r['path'] for r in rows}
    for path in files:
        rel = str(path.relative_to(root))
        if rel not in known:
            # Unadmitted image files must not masquerade as extra operational evidence.
            if path.suffix.lower() in ('.png', '.jpg', '.jpeg', '.tiff', '.heic'):
                raise ValueError('Unexpected unadmitted image outside a declared run')
            rows.append(dict(path=rel, sha256=sha(path), roles=['operational'], kind='attestation'))
    return a.checked_rows(root, rows), unbridged


def verify_tree(a, tree, manifest, plan, expected):
    doc = a.verify_archive(tree, expected)
    rows, unbridged = complete_rows(a, tree, manifest, plan, indexed=True)
    if sorted(rows, key=lambda r: r['path']) != doc['files']:
        raise ValueError('Archive roles or admission differ from the sealed declaration')
    return len(doc['files']), unbridged


def produce(source, out, *, finished=False):
    if not finished:
        raise ValueError('Explicit finished-sitting attestation is required')
    source, out = destination(source, out)
    a, manifest, plan = sources()
    rows, _ = complete_rows(a, source, manifest, plan)
    out.mkdir(parents=True)
    index_sha = a.write_archive(source, out / 'tree', rows)
    _, unbridged = verify_tree(a, out / 'tree', manifest, plan, index_sha)
    exports = {role: a.export_role(out / 'tree', out / role, role, index_sha)
               for role in ('calibration', 'validation')}
    # Only regular files are written; ordering and headers do not depend on local mtimes.
    with tempfile.TemporaryDirectory(prefix='.pack-', dir=out) as td:
        tar = Path(td) / 'archive.tar'
        with tarfile.open(tar, 'w', format=tarfile.PAX_FORMAT) as handle:
            for path in sorted((out / 'tree').rglob('*')):
                if path.is_file():
                    info = tarfile.TarInfo(str(path.relative_to(out / 'tree')))
                    info.size = path.stat().st_size
                    info.mode = 0o644
                    with path.open('rb') as content:
                        handle.addfile(info, content)
        compressed = Path(td) / 'archive.tar.zst'
        with compressed.open('xb') as handle:
            subprocess.run(['zstd', '-19', '-T1', '-q', '-c', str(tar)], stdout=handle, check=True)
        digest = sha(compressed)
        asset = f'w50-archive-{digest}.tar.zst'
        compressed.rename(out / asset)
    (out / 'SHA256SUMS').write_text(f'{digest}  {asset}\n')
    q = shlex.quote
    recipe = '\n'.join([
        '# Prepared only: parent chooses the source commit and publishes after verification.',
        'gh release create w50-archive --repo SSFSKIM/designer --latest=false '
        '--target "$G1_COMMIT" --title "W50 archive of record" --notes ' +
        q(f'W50 G1a: 1600 admitted frames. Asset SHA-256 {digest}; '
          f'archive index SHA-256 {index_sha}. Blind pixels remain unexposed.'),
        'gh release upload w50-archive --repo SSFSKIM/designer ' +
        q(str(out / asset)) + ' ' + q(str(out / 'SHA256SUMS')),
        'gh release view w50-archive --repo SSFSKIM/designer --json assets',
    ])
    result = dict(tag='w50-archive', bridgeStatus='unbridged' if unbridged else 'bridged',
                  unbridgedClosingPasses=unbridged, asset=asset, sha256=digest,
                  bytes=(out / asset).stat().st_size, indexSha256=index_sha,
                  declarationSha256=DECLARATION_SHA, frames=1600, files=len(rows),
                  exportIndexSha256=exports, releaseRecipe=recipe)
    (out / 'pack.json').write_text(json.dumps(result, indent=2) + '\n')
    return result


def verify_asset(asset, out, expected_sha, index_sha):
    """Verify compressed bytes before reading tar, and extract data only into a new directory."""
    asset, out = destination(asset, out)
    if sha(asset) != expected_sha:
        raise ValueError('Asset hash mismatch')
    a, manifest, plan = sources()
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.verify-', dir=out.parent) as td:
        tar = Path(td) / 'archive.tar'
        with tar.open('xb') as handle:
            subprocess.run(['zstd', '-d', '-q', '-c', str(asset)], stdout=handle, check=True)
        tree = Path(td) / 'tree'
        tree.mkdir()
        with tarfile.open(tar, 'r:') as handle:
            seen = set()
            for member in handle:
                path = PurePosixPath(member.name)
                if (not member.isfile() or path.is_absolute() or '..' in path.parts or
                        not path.parts or str(path) != member.name or member.name in seen):
                    raise ValueError('Unsafe or duplicate archive member')
                seen.add(member.name)
                target = tree / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                with handle.extractfile(member) as content, target.open('xb') as dest:
                    shutil.copyfileobj(content, dest)
        count, unbridged = verify_tree(a, tree, manifest, plan, index_sha)
        tree.rename(out)
    return dict(verified=True, bridgeStatus='unbridged' if unbridged else 'bridged',
                unbridgedClosingPasses=unbridged, frames=1600, files=count,
                sha256=expected_sha, indexSha256=index_sha)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    produce_parser = sub.add_parser('produce', help='Only after capture exits and restoration succeeds')
    produce_parser.add_argument('source', type=Path)
    produce_parser.add_argument('--out', type=Path, required=True)
    produce_parser.add_argument('--sitting-finished', action='store_true', required=True)
    verify_parser = sub.add_parser('verify', help='Verify a local/downloaded asset into a NEW directory')
    verify_parser.add_argument('asset', type=Path)
    verify_parser.add_argument('--out', type=Path, required=True)
    verify_parser.add_argument('--sha256', required=True)
    verify_parser.add_argument('--index-sha256', required=True)
    args = parser.parse_args()
    if not sys.flags.isolated:
        parser.error('Use python -I -B; never run scripts from an extracted archive')
    if args.command == 'produce':
        result = produce(args.source, args.out, finished=args.sitting_finished)
    else:
        result = verify_asset(args.asset, args.out, args.sha256, args.index_sha256)
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
