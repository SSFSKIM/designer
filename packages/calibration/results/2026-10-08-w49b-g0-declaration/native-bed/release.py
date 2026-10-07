#!/usr/bin/env python3.12
"""Export calibration-only native evidence. Blind pass directories are never opened."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reuse

BLIND_ROLES = {'native-blind', 'no-glass-blind'}
CAL_ROLES = {'native-calibration', 'no-glass-calibration', 'dump-sentinel',
             'bridge-canonical', 'bridge-canvas-transfer'}


def calibration_passes(plan, sources):
    P = reuse.pass_spec()
    selected = []
    for p in plan['passes']:
        if p['role'] in BLIND_ROLES:
            continue
        if p['role'] not in CAL_ROLES:
            raise ValueError('undeclared export role: ' + p['role'])
        if p['source'] == 'native':
            doc = P.dump_doc_from(plan, sources, p['name']) if p['kind'] == 'dump' \
                else P.derive_from(plan, sources, p['name'])
            if doc['split']['holdout']:
                raise ValueError('a calibration export pass contains blind cells: ' + p['name'])
        selected.append(p)
    return selected


def validate_run(admission, p, n, plan, sources):
    """A same-plan blind run is not a calibration run just because it was misfiled."""
    if not admission.get('admitted') or admission.get('pass') != p['name'] or admission.get('run') != n \
            or admission.get('role') != p['role']:
        # W43 dump admissions have no role field, but still bind the pass/run.
        if not (p['kind'] == 'dump' and admission.get('admitted') and admission.get('pass') == p['name']
                and admission.get('run') == n):
            raise ValueError('wrong admitted pass/run/role: ' + p['name'])
    if admission.get('planSha256') != hashlib.sha256((HERE / 'sitting-native.json').read_bytes()).hexdigest():
        raise ValueError('admission names another plan: ' + p['name'])
    if p['kind'] == 'capture':
        doc = reuse.pass_spec().derive_from(plan, sources, p['name'], n)
        if set(admission.get('frames', {})) != set(reuse.pass_spec().cells(doc)):
            raise ValueError('admitted frame membership differs from calibration pass: ' + p['name'])


def export(root, out, plan, sources):
    """Copy declared admitted calibration passes, with hashes for the exported files.

    This is a calibration working tree, not the archive of record. The curator
    retains the raw root (including the blind tree) and later seals its archive.
    """
    if out.exists():
        raise ValueError('export destination exists; never overwrite an evidence tree')
    selected = calibration_passes(plan, sources)
    for p in selected:
        directory = root / p['name']
        for n in range(1, (p.get('runs') or 1) + 1):
            admission = json.loads((directory / f'run-{n}/admission.json').read_bytes())
            validate_run(admission, p, n, plan, sources)
        if directory.is_symlink() or any(path.is_symlink() for path in directory.rglob('*')):
            raise ValueError('native export refuses symlinks: ' + p['name'])
    out.mkdir(parents=True, mode=0o700)
    for p in selected:
        shutil.copytree(root / p['name'], out / p['name'])
    files = [{ 'path': str(p.relative_to(out)), 'sha256': hashlib.sha256(p.read_bytes()).hexdigest() }
             for p in sorted(out.rglob('*')) if p.is_file()]
    receipt = dict(schema='w49b-calibration-export-1', blindExposed=False,
                   declarationSha256=hashlib.sha256((HERE / 'bed-declaration.json').read_bytes()).hexdigest(),
                   passes=[p['name'] for p in selected], files=files)
    (out / 'receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    return receipt


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raw', type=Path)
    ap.add_argument('--out', type=Path)
    ap.add_argument('--apply', action='store_true')
    args = ap.parse_args()
    plan, sources = reuse.pass_spec().load(HERE / 'sitting-native.json')
    selected = calibration_passes(plan, sources)
    if not args.apply:
        print(json.dumps(dict(executed=False, blindExposed=False,
                              exportPasses=[p['name'] for p in selected]), indent=2))
        return
    if args.raw is None or args.out is None:
        ap.error('--apply requires --raw and --out')
    root = reuse.driver().outside_repository(args.raw)
    out = reuse.driver().outside_repository(args.out)
    if out.is_relative_to(root) or root.is_relative_to(out):
        ap.error('raw and calibration export must be disjoint trees')
    receipt = export(root, out, plan, sources)
    print(json.dumps(dict(blindExposed=False, passes=len(receipt['passes']), files=len(receipt['files']))))


if __name__ == '__main__':
    main()
