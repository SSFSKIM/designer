#!/usr/bin/env python3.12
"""External W41 dry preflight, before the one receipt (§5.192, clauses 2/11).

Only package versions are imported for the live probe. The committed runner's
read-only verify reconstructs the freeze over metadata and web evidence. Never
import the scorer or construct a native Reader, token, receipt or browser here.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
G1 = 'packages/calibration/results/2026-09-27-w41-g1-identification'
RUNTIME = G1 + '/candidate-e3/runtime.json'
RUNNER = G1 + '/exposure/runner.py'
SELF = G1 + '/preflight/preflight.py'
BOUNDARY = 'packages/calibration/results/2026-09-26-w39-g0-colour-edge-bed/wave.py'
REQUIRED = {'python': [3, 12], 'numpy': '2.3.5', 'pillow': '12.3.0'}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], stderr=subprocess.PIPE)


def committed_bytes(root, name):
    path = root / name
    if (not isinstance(name, str) or Path(name).is_absolute() or '..' in Path(name).parts
            or path.is_symlink() or root not in path.resolve().parents):
        raise ValueError('unsafe repository artifact: ' + str(name))
    live = path.read_bytes()
    if live != git(root, 'show', 'HEAD:' + name):
        raise ValueError('uncommitted frozen input: ' + name)
    return live


def probe_versions():
    import numpy
    import PIL
    return {'python': list(sys.version_info[:2]), 'numpy': numpy.__version__,
            'pillow': PIL.__version__}


def load_runner(root):
    spec = importlib.util.spec_from_file_location('w41_preflight_runner', root / RUNNER)
    module = importlib.util.module_from_spec(spec)
    # dataclasses resolves the defining module through sys.modules.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def run(root, manifest_path, evidence):
    root = Path(root).resolve()
    manifest_path = Path(manifest_path).resolve()
    report = dict(schema='w41-external-preflight-1', status='refusal',
                  startedAt=datetime.now(timezone.utc).isoformat(),
                  manifest=str(manifest_path), manifestSha256=None,
                  runtime=RUNTIME, runtimeSha256=None, checks=[])
    # Reserve exclusively before doing work; an old success/refusal is never replaced.
    with Path(evidence).open('x') as output:
        try:
            report['head'] = git(root, 'rev-parse', 'HEAD').decode().strip()
            manifest_data = committed_bytes(root, str(manifest_path.relative_to(root)))
            report['manifestSha256'] = digest(manifest_data)
            manifest = json.loads(manifest_data)
            report['checks'].append('manifest committed bytes')
            runtime_data = committed_bytes(root, RUNTIME)
            report['runtimeSha256'] = digest(runtime_data)
            declared = json.loads(runtime_data)
            report['declaredRuntime'] = declared
            if declared != REQUIRED:
                raise ValueError('declared runtime differs from required W41 runtime')
            files = manifest['files']
            for name in (RUNTIME, RUNNER, BOUNDARY, SELF):
                if name not in files:
                    raise ValueError('required preflight input missing from freeze: ' + name)
            # Check ALL pinned instruments/sources before importing any runner code.
            # This catches a changed scorer by bytes, never by executing its guard.
            for name, expected in files.items():
                if digest(committed_bytes(root, name)) != expected:
                    raise ValueError('frozen hash mismatch: ' + name)
            if files[RUNNER] != manifest['runnerSha256'] or files[BOUNDARY] != manifest['boundarySha256']:
                raise ValueError('runner/boundary hash fields disagree with frozen files')
            report['frozenFileCount'] = len(files)
            report['checks'].append('all manifest files: live == HEAD == frozen SHA256')
            live = probe_versions()
            report['liveRuntime'] = live
            if live != declared:
                raise ValueError('live runtime mismatch: ' + json.dumps(live, sort_keys=True))
            report['checks'].append('live Python major/minor, NumPy and Pillow == committed runtime')
            runner = load_runner(root)
            if runner.ROOT.resolve() != root:
                raise ValueError('runner repository differs from preflight repository')
            verified = runner.verify(root, runner.boundary.default_wave(), manifest_path, 'production')
            if verified != manifest:
                raise ValueError('manifest changed during preflight')
            report['checks'].append('runner.verify:production')
            report['verificationScope'] = ['complete freeze reconstruction', 'source inventory/revision',
                                           'domain evidence', 'compiled runtime artifact inventory/bytes',
                                           'committed web predictions/baselines/backdrops']
            report['status'] = 'success'
        except Exception as exc:
            report['error'] = type(exc).__name__ + ': ' + str(exc)
        report['finishedAt'] = datetime.now(timezone.utc).isoformat()
        json.dump(report, output, indent=2, allow_nan=False)
        output.write('\n')
        output.flush()
        os.fsync(output.fileno())
    return 0 if report['status'] == 'success' else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--evidence', required=True, type=Path,
                        help='new, exclusive JSON path beside exposure evidence')
    args = parser.parse_args()
    code = run(ROOT, args.manifest, args.evidence)
    print(('SUCCESS' if code == 0 else 'REFUSAL') + ': ' + str(args.evidence))
    return code


if __name__ == '__main__':
    raise SystemExit(main())
