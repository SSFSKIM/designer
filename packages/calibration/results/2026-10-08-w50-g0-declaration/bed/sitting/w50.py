#!/Users/new/vitrea-w49/py/bin/python -I
"""W50's registered native entrypoint: batch first, then plan or run.

Every live action is behind the root declaration, in-process import closure and positive TCC
check. W43 owns per-capture idle/pose/path/state admission, watchdog, bridge statistics and
quarantine. W50 owns membership, classifying census, role isolation and signal-proof restore.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import time
import uuid

HERE = Path(__file__).resolve().parent
BED = HERE.parent
DECL = BED.parent
ROOT = HERE.parents[5]
MODULES = {}
TRUSTED_SOURCES = None
B = S = None


def load(name, path):
    """Source-only loading: -B stops writes but does not stop Python reading stale bytecode."""
    path = Path(path).resolve()
    raw = path.read_bytes()
    if TRUSTED_SOURCES is not None and path.is_relative_to(ROOT):
        if TRUSTED_SOURCES.get(str(path.relative_to(ROOT))) != hashlib.sha256(raw).hexdigest():
            raise ValueError('Changed or unsealed source before execution: ' + str(path))
    if name not in MODULES:
        spec = importlib.util.spec_from_file_location(name, path)
        m = importlib.util.module_from_spec(spec)
        exec(compile(raw, str(path), 'exec', dont_inherit=True), m.__dict__)
        MODULES[name] = m
    return MODULES[name]


def dry_imports():
    """Explicit trusted probe/test import path; never exposed as a CLI option or environment seam."""
    global B, S
    B = load('w50_build', BED/'build.py')
    S = load('w50_safety', HERE/'safety.py')


def bootstrap(batch):
    """Stdlib-only trust boundary, before even the guard module or its imports can execute."""
    global TRUSTED_SOURCES
    digest = lambda raw: hashlib.sha256(raw).hexdigest()

    def sealed(path):
        if not path.is_file() or not path.with_suffix('.sha256').is_file():
            raise ValueError('Native declaration/contract is not sealed: ' + str(path))
        raw = path.read_bytes()
        if path.with_suffix('.sha256').read_text() != f'{digest(raw)}  {path.name}\n':
            raise ValueError('Native seal differs: ' + str(path))
        return json.loads(raw), digest(raw)

    def checked(relative, wanted):
        path = (ROOT/relative).resolve()
        if not path.is_relative_to(ROOT) or not path.is_file() or digest(path.read_bytes()) != wanted:
            raise ValueError('Changed, missing or escaped source before execution: ' + relative)
        return path

    parts = {}
    for name in ('declaration', 'fit-declaration'):
        doc, hashed = sealed(DECL/f'{name}.json')
        if doc.get('schema') != f'w50-{name}-1':
            raise ValueError('Wrong native root schema')
        pins = doc.get('sources', [])
        if not pins or len({p['path'] for p in pins}) != len(pins):
            raise ValueError('Missing or duplicate source pins')
        for pin in pins:
            checked(pin['path'], pin['sha256'])
        parts[name] = (doc, hashed)
    if parts['fit-declaration'][0].get('partOneSha256') != parts['declaration'][1]:
        raise ValueError('Native root parts do not bind one another')
    contract = BED/'execution-contract.json'
    root_pins = {p['path'] for p in parts['declaration'][0]['sources']}
    if any(str(p.relative_to(ROOT)) not in root_pins for p in (contract, Path(str(contract)+'.sha256'))):
        raise ValueError('Native contract is not authorised by the root source seal')
    # Contracts append their sidecar suffix; the operational parts replace .json with .sha256.
    raw = contract.read_bytes()
    if Path(str(contract)+'.sha256').read_text() != f'{digest(raw)}  {contract.name}\n':
        raise ValueError('Native execution contract differs from seal')
    doc = json.loads(raw)
    if doc.get('schema') != 'batch-import-closure-1':
        raise ValueError('Wrong native execution contract schema')
    expected = dict(doc['closure']['sources'])
    for relative, wanted in expected.items():
        checked(relative, wanted)
    for name in ('next_wave.py', 'closure.py'):
        relative = str((DECL/'audit'/name).relative_to(ROOT))
        wanted = doc['guardSources'][name]
        checked(relative, wanted)
        if relative in expected and expected[relative] != wanted:
            raise ValueError('Guard source differs between closure and contract')
        expected[relative] = wanted
    entry = Path(__file__).resolve()
    if (ROOT/doc['renderer']).resolve() != entry or str(entry.relative_to(ROOT)) not in expected:
        raise ValueError('Native entrypoint is not the sealed renderer')
    registered = checked(doc['batch']['path'], doc['batch']['sha256'])
    if Path(batch).read_bytes() != registered.read_bytes():
        raise ValueError('Supplied bytes are not the sealed native batch')
    TRUSTED_SOURCES = expected
    # This helper's bytes were checked above and load() compiles those source bytes, never pyc.
    K = load('w50_bootstrap_closure', DECL/'audit/closure.py')
    K.enforce(ROOT, expected)
    return contract


def guard(batch):
    """Neither a wrapper nor its caller can substitute a different batch or source closure."""
    contract = bootstrap(batch)
    N = load('w50_native_next_wave', DECL/'audit/next_wave.py')
    doc, registered, renderer = N.verify(contract, ROOT, batch)
    if renderer != Path(__file__).resolve():
        raise ValueError('Native entrypoint is not the sealed renderer')
    declaration = load('w50_root_declaration', DECL/'declare.py')
    declaration.verify(phase='native')
    dry_imports()                              # now under the live source-only import guard
    return registered


def selected_passes(plan, stop_after=None):
    passes = plan['passes']
    if stop_after is None:
        return passes
    names = [p['name'] for p in passes]
    if stop_after not in names or passes[names.index(stop_after)].get('runAfterCut'):
        raise ValueError('Cut must name a declared non-closing pass')
    at = names.index(stop_after)
    return passes[:at+1] + [p for p in passes[at+1:] if p.get('runAfterCut')]


class Ownership:
    """A fresh unpredictable run label plus exact argv, executable and pid/start identity.

    Unlike W43's executable-wide cancellation, this cannot end another session's harness or
    a process that reused the original pid. Observations are made while our open -n -W runs.
    """
    def __init__(self, binary, args):
        self.binary, self.args = str(binary), list(args)
        self.owned = set()

    def matches(self, row):
        return row['executable'] == self.binary and row.get('argv', [])[1:] == self.args

    def observe(self, rows):
        self.owned |= {(r['pid'], r['start']) for r in rows if self.matches(r)}

    def targets(self, rows):
        return [r for r in rows if (r['pid'], r['start']) in self.owned and self.matches(r)]


def configure(batch):
    d = S.driver()
    if getattr(d, '_w50_bound', False):
        return d
    d._w50_bound = True
    d.pass_spec = B.pass_spec
    d.recorder_module = S.recorder
    d.SITTING_ENV, d.ORCHESTRATED_ENV, d.CUT_ENV = 'W50_SITTING', 'W50_ORCHESTRATED', 'W50_CUT_AFTER'
    d.DECLARATION, d.DECLARATION_DIGEST = DECL/'declaration.json', DECL/'declaration.sha256'
    d._owner = None
    d._labels = {}

    def pinned(sitting, predeclaration=False):
        if sitting != 'g1' or predeclaration:
            raise ValueError('W50 has one sealed sitting, no predeclaration launch')
        guard(batch)
        B.verify()
        grant = S.grant_check()
        if not grant['positive']:
            raise ValueError(grant['reason'])
        plan = json.loads(Path(batch).read_bytes())
        return dict(sitting='g1', planSha256=B.sha(Path(batch).read_bytes()),
                    sources={k: s['sha256'] for k, s in plan['sources'].items()},
                    declarationSha256=B.sha((DECL/'declaration.json').read_bytes()),
                    head=subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD'], text=True).strip())
    d.pinned_declaration = pinned
    original_argv, original_validate, original_watched = d.capture_argv, d.validate_manifest, d.watched

    def argv(launcher, app, spec, run, scale, label, protocol, ids, pose):
        unique = 'w50-'+uuid.uuid4().hex+'-'+label
        d._labels[label] = unique
        command = original_argv(['open', '-n', '-W'], app, spec, run, scale, unique, protocol, ids, pose)
        d._owner = Ownership((app/'Contents/MacOS/VitreaReference').resolve(),
                             command[command.index('--args')+1:])
        return command

    def validate(m, doc, pose, scale, label):
        return original_validate(m, doc, pose, scale, d._labels.get(label, label))

    def end_owned(app, grace=10.0):
        owner = d._owner
        if owner is None:
            return []
        rows = S.recorder().process_table()
        owner.observe(rows)
        targets = owner.targets(rows)
        for row in targets:
            # Re-check identity immediately before each signal, not just at observation time.
            if row in owner.targets(S.recorder().process_table()):
                try:
                    os.kill(row['pid'], signal.SIGTERM)
                except ProcessLookupError:
                    pass
        deadline = time.monotonic()+grace
        while time.monotonic() < deadline and owner.targets(S.recorder().process_table()):
            time.sleep(0.2)
        for row in owner.targets(S.recorder().process_table()):
            try:
                os.kill(row['pid'], signal.SIGKILL)
            except ProcessLookupError:
                pass
        return targets

    def watched(command, dog, **kwargs):
        original = dog.check
        def observe():
            d._owner.observe(S.recorder().process_table())
            return original()
        dog.check = observe
        try:
            return original_watched(command, dog, **kwargs)
        finally:
            d._owner.observe(S.recorder().process_table())
    base_admission = d.run_admission

    def admission(p, n, argv_, manifest, manifest_sha, cells, declaration, binding):
        record = base_admission(p, n, argv_, manifest, manifest_sha, cells, declaration, binding)
        if p['role'] == 'low-end':
            from PIL import Image
            import numpy as np
            cuts = load('w50_cuts', HERE/'cuts.py')
            run_dir = Path(argv_[argv_.index('--stdout')+1]).parent
            readings = {}
            # Operational control pixels only. Blind identifying frames are never opened here.
            for profile in manifest['profiles']:
                for fixture in profile['fixtures']:
                    sid = fixture['sceneId']
                    if sid.startswith(('00-open-', 'zz-close-')):
                        with Image.open(run_dir/fixture['file']) as image:
                            rgb = np.asarray(image.convert('RGB'))
                        readings[sid] = cuts.read(rgb, {'kind':'rrect','size':[280,160],'radius':34}, p['scale'])
            state = 'rest' if p['pose'] == 'active' else 'inactive'
            controls = {str(v): cuts.sentinel_verdict(readings[f'00-open-grey-{v:03}__{state}'],
                                                     readings[f'zz-close-grey-{v:03}__{state}']) for v in (0,64)}
            report = dict(readings=readings, controls=controls)
            if n == 3:
                earlier = [json.loads((run_dir.parent/f'run-{k}'/'sentinels.json').read_bytes()) for k in (1,2)]
                report['repeat'] = {sid: cuts.repeat_verdict([r['readings'][sid] for r in earlier]+[reading])
                                    for sid, reading in readings.items()}
            (run_dir/'sentinels.json').write_text(json.dumps(report,indent=2)+'\n')
            if not all(c['passes'] for c in controls.values()) or \
                    not all(c['passes'] for c in report.get('repeat',{}).values()):
                raise ValueError('Operational sentinel changed beyond one code: stop, do not add runs')
            record['sentinelsSha256'] = B.sha((run_dir/'sentinels.json').read_bytes())
        return record

    d.capture_argv, d.validate_manifest, d.end_native, d.watched = argv, validate, end_owned, watched
    d.run_admission = admission
    return d


def read_mode():
    text = subprocess.check_output(['/opt/homebrew/bin/displayplacer', 'list'], text=True)
    modes = re.findall(r'^  mode (\d+):.*<-- current mode$', text, re.M)
    screens = re.findall(r'^Persistent screen id: (.+)$', text, re.M)
    if len(modes) != 1 or screens != [S.driver().SCREEN]:
        raise ValueError('Display identity or current mode cannot be uniquely read')
    return modes[0]


def set_mode(mode):
    subprocess.run(['/opt/homebrew/bin/displayplacer', f'id:{S.driver().SCREEN} mode:{mode}'], check=True)
    deadline = time.monotonic()+15
    while time.monotonic() < deadline:
        if read_mode() == mode:
            return dict(restored=True, mode=mode)
        time.sleep(0.5)
    raise ValueError('Display did not reach its declared mode')


def run(batch, root, stop_after=None):
    d = configure(batch)
    d.pinned_declaration('g1')                  # grant and seals before mkdir/settings/launch
    root = d.outside_repository(root)
    if root.exists():
        raise ValueError('Sitting root exists; continuation needs explicit G1 admission review')
    preflight = S.machine('w50-preflight')
    if preflight['foreignProcessCount'] or any(preflight['settings'][k]['exitCode'] != 0 or
            preflight['settings'][k]['stdout'] != '0' for k in ('reduceTransparency','increaseContrast')):
        raise ValueError('Classifying census or accessibility preflight refused before any state change')
    root.mkdir(parents=True)
    logs = root/'logs'; logs.mkdir()
    (logs/'preflight.json').write_text(json.dumps(preflight,indent=2)+'\n')
    plan, sources = B.pass_spec().load(batch)
    chosen = selected_passes(plan, stop_after)
    # No caller-supplied launcher/session/defaults seam on the live entrypoint.
    forbidden = ('VITREA_APP', 'VITREA_HARNESS', 'VITREA_LAUNCHER', 'VITREA_SESSION_READER',
                 'VITREA_RECORD_MACHINE', 'VITREA_DEFAULTS', 'W43_PREDECLARATION')
    if any(k in os.environ for k in forbidden):
        raise ValueError('Live sitting refuses external tool overrides')
    os.environ.update(VITREA_SITTING_DIR=str(root), W50_SITTING='g1', W50_ORCHESTRATED='1',
                      VITREA_RECORD_MACHINE=f'{sys.executable} -I -B {HERE}/safety.py')
    mode = read_mode()
    (logs/'as-found-mode.json').write_text(json.dumps(dict(mode=mode))+'\n')
    d.slider_as_found(root)
    (logs/'universal-control.json').write_text(json.dumps(S.recorder().universal_control(), indent=2)+'\n')
    previous = {sig: signal.signal(sig, d._cancel) for sig in (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)}
    try:
        for p in chosen:
            guard(batch)
            if stop_after and p.get('runAfterCut'):
                os.environ['W50_CUT_AFTER'] = stop_after
            desired = B.pass_spec().MODES[p['scale']]
            if read_mode() != desired:
                with (logs/'mode-idle.txt').open('a') as log:
                    session = [str(Path.home()/'vitrea-w39/scratch/read-session')]
                    d.wait_for_idle(lambda: json.loads(subprocess.check_output(session, text=True)),
                                    lambda line: log.write(line+'\n'), need=300)
                set_mode(desired)
            if not d.slider_matches(d.slider_read()['value'], p['glass']):
                d.slider_set(root, p['glass'])
            d.main(['capture', p['name']])
    finally:
        # The child launcher is W43's watched process; only our token-owned native pid can be ended.
        for sig in previous:
            signal.signal(sig, signal.SIG_IGN)
        try:
            d.end_native(S.APP)
        finally:
            result = S.restore(lambda: d.slider_restore(root), lambda: set_mode(mode))
            (logs/'restore.json').write_text(json.dumps(result, indent=2)+'\n')
            for sig, handler in previous.items():
                signal.signal(sig, handler)
        if not result['restored']:
            raise ValueError('Restoration incomplete; inspect logs/restore.json before any continuation')


def dry_exercise():
    """No seal/launch: the prospective probe exercises the actual planner and protected instrument."""
    plan, sources = B.pass_spec().load(BED/'sitting-g1.json')
    d = S.driver()
    d.pass_spec = B.pass_spec
    value = d.dry_plan(plan, sources)
    selected_passes(plan, 'bed-x0.5-1x-active')
    d.instrument()                            # bridge's transitive numerical imports, before seal
    load('w50_archive', HERE/'archive.py')
    return value


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('batch', type=Path)
    parser.add_argument('command', choices=('plan', 'run'))
    parser.add_argument('--root', type=Path)
    parser.add_argument('--stop-after')
    args = parser.parse_args()
    registered = guard(args.batch)
    if args.command == 'plan':
        value = dry_exercise()
        print(json.dumps(dict(totals=value['totals'], passes=len(value['passes']))))
    else:
        if args.root is None:
            parser.error('run requires --root outside every checkout')
        run(registered, args.root, args.stop_after)
